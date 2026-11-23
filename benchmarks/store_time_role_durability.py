"""Decide whether the engine must record the licensing role at store time.

The pair resolver answers a different question: whether a reader can follow the record. This asks
whether the record is *there* when the trace reads it. The engine already writes three legs on
separate rows -- the prediction carries `schema_prior`, the schema row carries `source_role_id`
and `target_role_id`, and the role rows carry the exemplars behind those ids. If every leg is
present for every primed prediction, a new field would be a second copy of what already exists
(rule 17c) and the engine should record nothing new. If any leg is missing, the field buys
durability the record cannot otherwise have.

**The decision rule is fixed before the run** (rule 19): all recoverable -> no engine change; any
missing leg -> the change is needed, and the leg observed is named. An empty denominator is not
measurable, never "no missing rows" (rule 13a).

The classifier is proved on fixtures with known answers before it is pointed at a run: removing the
schema row must report R1, removing a role row R2, stripping the ids R3, and a classifier that
cannot report a missing leg fails the self-test (rule 11).

    ./.venv/bin/python -m benchmarks.store_time_role_durability --self-test
    ./.venv/bin/python -m benchmarks.store_time_role_durability --measure
    ./.venv/bin/python -m benchmarks.store_time_role_durability --check
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ARTIFACT = ROOT / "docs" / "store_time_role_durability.json"
DOC = ROOT / "docs" / "STORE-TIME-ROLE-DURABILITY.md"

SEED = 20261101
PHASE_A = 40
PHASE_B = 40
STATUSES = ("recoverable", "R1_schema_absent", "R2_role_rows_absent", "R3_schema_without_role_ids")
DECISION_RULE = (
    "all primed predictions recoverable from stored rows -> NO_ENGINE_CHANGE; any missing leg -> "
    "ENGINE_CHANGE_NEEDED, with the leg named; no primed prediction -> NOT_MEASURABLE"
)


def classify(primed: list[dict], by_id: dict[str, dict]) -> list[dict]:
    """Join each primed prediction to the row it names and both role rows behind it."""
    out = []
    for row in primed:
        prior = row.get("schema_prior")
        base = {"prediction": row.get("id"), "schema_prior": prior, "role_ids": None}
        schema = by_id.get(prior) if prior else None
        if schema is None:
            out.append({**base, "status": "R1_schema_absent"})
            continue
        ids = [schema.get("source_role_id"), schema.get("target_role_id")]
        if not all(ids):
            out.append({**base, "status": "R3_schema_without_role_ids"})
            continue
        base["role_ids"] = ids
        missing = [role_id for role_id in ids if role_id not in by_id]
        if missing:
            out.append({**base, "status": "R2_role_rows_absent", "missing": missing})
            continue
        out.append({**base, "status": "recoverable"})
    return out


def decision_for(rows: list[dict]) -> str:
    if not rows:
        return "NOT_MEASURABLE"
    if all(row["status"] == "recoverable" for row in rows):
        return "NO_ENGINE_CHANGE"
    return "ENGINE_CHANGE_NEEDED"


def summarise(rows: list[dict]) -> dict:
    counts = {status: 0 for status in STATUSES}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    total = len(rows)
    return {
        "primed_predictions": total,
        "denominator": total,
        "statuses": counts,
        "recoverable": counts["recoverable"],
        "share": (counts["recoverable"] / total) if total else None,
        "measurable": total > 0,
        "decision": decision_for(rows),
        "residuals_observed": sorted({row["status"] for row in rows
                                      if row["status"] != "recoverable"}),
    }


def _fixtures() -> dict[str, dict]:
    by_id = {
        "schema_1": {"id": "schema_1", "source_role_id": "role_a", "target_role_id": "role_b"},
        "role_a": {"id": "role_a", "exemplars": ["willow", "teal"]},
        "role_b": {"id": "role_b", "exemplars": ["cedar", "maple"]},
    }
    primed = [{"id": "pred_1", "schema_prior": "schema_1"}]
    return {
        "recoverable": {"primed": primed, "by_id": by_id, "expected": "recoverable"},
        "schema_absent": {"primed": primed,
                          "by_id": {k: v for k, v in by_id.items() if k != "schema_1"},
                          "expected": "R1_schema_absent"},
        "role_absent": {"primed": primed,
                        "by_id": {k: v for k, v in by_id.items() if k != "role_b"},
                        "expected": "R2_role_rows_absent"},
        "ids_stripped": {"primed": primed,
                         "by_id": {**{k: v for k, v in by_id.items() if k != "schema_1"},
                                   "schema_1": {"id": "schema_1", "exemplars": ["willow"]}},
                         "expected": "R3_schema_without_role_ids"},
    }


def run_controls(classifier=classify) -> dict:
    results = {}
    for name, fixture in _fixtures().items():
        got = classifier(fixture["primed"], fixture["by_id"])
        status = got[0]["status"] if got else None
        results[name] = {"expected": fixture["expected"], "observed": status,
                         "passed": status == fixture["expected"]}
    empty = summarise([])
    results["empty_denominator_is_not_measurable"] = {
        "expected": "measurable=False",
        "observed": "measurable=%s" % empty["measurable"],
        "passed": empty["measurable"] is False and empty["decision"] == "NOT_MEASURABLE",
    }
    return {"controls": results, "all_passed": all(r["passed"] for r in results.values())}


def always_recoverable(primed, by_id):
    return [{"prediction": row.get("id"), "schema_prior": row.get("schema_prior"),
             "role_ids": None, "status": "recoverable"} for row in primed]


def self_test() -> dict:
    controls = run_controls()
    blind = run_controls(always_recoverable)
    ok = controls["all_passed"] and not blind["all_passed"]
    return {"controls": controls, "a_blind_classifier_is_rejected": not blind["all_passed"],
            "all_passed": ok}


def _stored_rows(mem) -> tuple[list[dict], dict]:
    """Every stored sleep candidate, read past the engine's own recency window."""
    wanted = 200000
    events = mem.recent(n=wanted, event_type="sleep")
    rows = []
    for event in events:
        source = getattr(event, "source", "") or ""
        if not source.startswith("sleep:") or source == "sleep:meta":
            continue
        try:
            rows.append(json.loads(event.content))
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
    return rows, {"events_scanned": len(events), "window": wanted,
                  "window_truncated": len(events) >= wanted}


def measure(seed: int = SEED, phase_a: int = PHASE_A, phase_b: int = PHASE_B) -> dict:
    from organica.memory import MemoryService
    from organica.paths import scratch_db
    from organica.sleep import SleepService
    from benchmarks.cross_context_reuse_benchmark import (
        VOCAB_A, VOCAB_B, generate_world_events)

    db = Path(scratch_db("store_time_role_durability.db"))
    if db.exists():
        db.unlink()
    mem = MemoryService(str(db))
    service = SleepService(mem)
    minimum = int(getattr(service, "PREDICTION_MIN_COUNT", 5))
    primed = []
    roles_seen = 0
    try:
        for texts in generate_world_events(VOCAB_A, phase_a, seed=seed):
            with mem.batch():
                for text in texts:
                    mem.store(text, event_type="observe", source="env:A")
            service.run_sleep_cycle()
        for texts in generate_world_events(VOCAB_B, phase_b, seed=seed + 1000):
            with mem.batch():
                for text in texts:
                    mem.store(text, event_type="observe", source="env:B")
            report = service.run_sleep_cycle()
            for prediction in (getattr(report, "predictions", None) or []):
                evidence = getattr(prediction, "evidence", {}) or {}
                count = int(evidence.get("temporal_count", evidence.get("count", 0)) or 0)
                if evidence.get("schema_prior") and count >= minimum:
                    primed.append({"id": getattr(prediction, "id", None),
                                   "schema_prior": evidence.get("schema_prior")})
        stored, scan = _stored_rows(mem)
    finally:
        mem.close()
        db.unlink(missing_ok=True)

    by_id = {row["id"]: row for row in stored if row.get("id")}
    roles_seen = sum(1 for row in stored if row.get("exemplars") is not None)
    traces = classify(primed, by_id)
    summary = summarise(traces)
    return {
        "kind": "store_time_role_durability",
        "seed": seed,
        "cycles": phase_a + phase_b,
        "phase_a_cycles": phase_a,
        "phase_b_cycles": phase_b,
        "stored_rows": len(stored),
        "role_rows": roles_seen,
        "scan": scan,
        "decision_rule": DECISION_RULE,
        "measurement": summary,
        "traces": traces,
        "note": ("This decides whether the store-time field is needed; it makes no claim about "
                 "the organism and resolves no transfer. Q028 stays open either way."),
    }


def render(artifact: dict) -> str:
    m = artifact["measurement"]
    share = "not measurable" if m["share"] is None else "%.4f" % m["share"]
    decision_text = {
        "NO_ENGINE_CHANGE": (
            "**No engine change.** Every primed prediction's role pair is recoverable from the rows "
            "the engine already writes, on the cell the trace will read. A `schema_prior_roles` "
            "field would be a second copy of `schema_prior` plus the schema row, and Q028's trace "
            "does not need it; the pair resolver is the whole fix."),
        "ENGINE_CHANGE_NEEDED": (
            "**The engine change is needed.** At least one leg the trace reads is already gone for "
            "a live prediction, so no reader could recover the pair from the record. The residual "
            "named below selects the field: R3 needs the ids copied at rebuild, R1 and R2 need the "
            "pair carried on the prediction itself."),
        "NOT_MEASURABLE": (
            "**Not measurable.** No schema-primed prediction with the trace's minimum count was "
            "recorded, so there is no denominator to judge and no decision is taken (rule 13a)."),
    }[m["decision"]]
    lines = [
        "# Does the record already survive to trace time?",
        "",
        "**Generated from `docs/store_time_role_durability.json`. Do not edit this file.** Rebuild",
        "with `python -m benchmarks.store_time_role_durability --measure`; `--check` validates.",
        "",
        "## What was asked",
        "",
        "Whether the engine must record the licensing role pair on each schema-primed prediction so",
        "Q028's trace can name it. The engine already writes the pair on two rows -- the schema",
        "carries `source_role_id` and `target_role_id`, the prediction carries `schema_prior` -- so",
        "the question is whether those rows are still there when the trace reads them.",
        "",
        "## What was run",
        "",
        "| Item | Value |",
        "| --- | --- |",
        "| World | the campaign's two context worlds, `VOCAB_A` then `VOCAB_B` |",
        "| Seed | `%d` (the trace's calibration seed, outside CCRE-2's confirmatory block) |" % artifact["seed"],
        "| Cycles | %d + %d |" % (artifact["phase_a_cycles"], artifact["phase_b_cycles"]),
        "| Stored sleep rows read | %d |" % artifact["stored_rows"],
        "| Role rows among them | %d |" % artifact["role_rows"],
        "| Scan window | %d events, truncated: %s |"
        % (artifact["scan"]["window"], artifact["scan"]["window_truncated"]),
        "| Decision rule, fixed before the run | %s |" % artifact["decision_rule"],
        "",
        "## Controls, run before the measurement",
        "",
        "| control | expected | observed | passed |",
        "| --- | --- | --- | --- |",
    ]
    for name, row in sorted(artifact["controls"]["controls"].items()):
        lines.append("| `%s` | `%s` | `%s` | %s |"
                     % (name, row["expected"], row["observed"], "yes" if row["passed"] else "no"))
    lines += [
        "",
        "A classifier that answers `recoverable` for everything was rejected: %s."
        % ("yes" if artifact["a_blind_classifier_is_rejected"] else "no"),
        "",
        "## What survived",
        "",
        "| status | count |",
        "| --- | --- |",
    ]
    for status in STATUSES:
        lines.append("| `%s` | %d |" % (status, m["statuses"].get(status, 0)))
    lines += [
        "",
        "| quantity | value |",
        "| --- | --- |",
        "| primed predictions (denominator) | %d |" % m["denominator"],
        "| recoverable from stored rows | %d |" % m["recoverable"],
        "| share | %s |" % share,
        "| decision | **%s** |" % m["decision"],
        "",
        "## The decision",
        "",
        decision_text,
        "",
    ]
    if m["residuals_observed"]:
        lines += ["Residuals observed: %s." % ", ".join("`%s`" % r for r in m["residuals_observed"]),
                  ""]
    lines += [
        "## What this does not establish",
        "",
        "- **One cell, one seed.** It is the cell the trace will read, not a distribution; pruning",
        "  that needs more than 80 cycles is not exercised.",
        "- **Survival is not resolution.** A recoverable pair still needs the pair resolver to read",
        "  it; this measures whether the record is present, not whether Q028 is answered.",
        "- **The window was widened deliberately.** The engine's own loader reads a bounded recency",
        "  window, so this reads every stored sleep row; a missing row here is missing from the",
        "  record, not from the reader.",
        "",
    ]
    return "\n".join(lines)


def problems(artifact: dict) -> list[str]:
    found = []
    m = artifact["measurement"]
    if artifact["scan"]["window_truncated"]:
        found.append("the scan window was truncated, so a missing row may be a scan limit")
    if m["denominator"] != len(artifact["traces"]):
        found.append("the denominator does not match the traced predictions")
    if (m["denominator"] and m["share"] is not None
            and abs(m["share"] - m["recoverable"] / m["denominator"]) > 1e-9):
        found.append("the recorded share does not follow from its counts")
    if m["measurable"] and m["decision"] != decision_for(artifact["traces"]):
        found.append("the recorded decision does not follow from the traced rows")
    if not m["measurable"] and m["decision"] != "NOT_MEASURABLE":
        found.append("a zero denominator was scored as a decision")
    if not DOC.exists():
        found.append("the result document does not exist")
    elif DOC.read_text(encoding="utf-8") != render(artifact):
        found.append("%s is stale; rebuild with python -m benchmarks.store_time_role_durability"
                     % DOC.name)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the classifier controls")
    parser.add_argument("--measure", action="store_true", help="run the cell and write the result")
    parser.add_argument("--check", action="store_true", help="validate and write nothing")
    args = parser.parse_args(argv)

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=1, sort_keys=True))
        return 0 if result["all_passed"] else 1
    if args.check:
        found = problems(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("store-time role durability: %s"
              % json.loads(ARTIFACT.read_text(encoding="utf-8"))["measurement"]["decision"])
        return 0
    if not args.measure:
        parser.print_help()
        return 2

    result = self_test()
    if not result["all_passed"]:
        print("FAIL: the classifier's controls must pass before it measures")
        return 1
    artifact = measure()
    artifact["controls"] = result["controls"]
    artifact["a_blind_classifier_is_rejected"] = result["a_blind_classifier_is_rejected"]
    artifact["generated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    DOC.write_text(render(artifact), encoding="utf-8")
    m = artifact["measurement"]
    print(json.dumps({"decision": m["decision"], "primed": m["denominator"],
                      "recoverable": m["recoverable"], "statuses": m["statuses"],
                      "stored_rows": artifact["stored_rows"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
