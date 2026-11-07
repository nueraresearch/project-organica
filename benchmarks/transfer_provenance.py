"""The Q028 instrument: transfer -> role match -> the events behind it.

`docs/ccre_question_licensing.json` licenses Q028 to be *answered* by the next
cross-context run, and requires its diagnostic to be trace-derived.  This module
is that diagnostic, built and proved before the run rather than after it.

**What it measures.**  A *transfer event* is a prediction asserted in context B
whose pair was already asserted in context A: the relation reappears under a new
context after being learned in the first.  A transfer is *resolved* only when all
three legs are present in the recorded state:

  role    a role whose exemplars contain both tags of the pair,
  events  at least one recorded event that asserted that role,
  priming the schema prior the engine recorded on the prediction.

Anything less is reported with its reason, and the share is reported with its
denominator.  A zero denominator is **not measurable**, never zero (AGENTS rule
13b).

**Resolution.**  This is event-level for the role leg (the events are the stored
ones) and structure-level for the priming leg (the engine records a schema id,
not the events that created it).  The artifact says so; it does not claim
observation-level provenance for the whole chain (rule 17d).

**The controls are the deliverable.**  Fixtures with known answers run first, and
three flip controls remove one leg at a time and require the status to change.
`compare_to_expected` is then pointed at a tracer that always answers
`resolved_role_match`, and the self-test fails unless every control rejects it:
a check that cannot fail would authorise a transfer claim on nothing (rule 25).

No threshold, no verdict, no transfer claim.  `python -m benchmarks.transfer_provenance
--self-test` exits non-zero if any control fails.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ARTIFACT = ROOT / "docs" / "transfer_provenance.json"
DOC = ROOT / "docs" / "TRANSFER-PROVENANCE.md"

STATUSES = (
    "resolved_role_match",
    "unresolved_no_role",
    "unresolved_missing_events",
    "unresolved_no_priming",
    "unresolved_missing_structure",
)
RESOLVED = "resolved_role_match"


def role_match(pair: tuple[str, str], roles: list[dict]) -> dict | None:
    """The first role whose exemplars contain both tags of the pair."""
    source, target = pair
    for role in roles:
        exemplars = set(role.get("exemplars") or ())
        if source in exemplars and target in exemplars:
            return role
    return None


def asserting_events(role: dict, events: list[dict]) -> list[dict]:
    """The recorded events that carry at least two of the role's exemplars."""
    exemplars = set(role.get("exemplars") or ())
    out = []
    for event in events:
        if len(exemplars & set(event.get("tags") or ())) >= 2:
            out.append(event)
    return out


def trace_transfer(transfer: dict, roles: list[dict], events: list[dict],
                   snapshot: set[str]) -> dict[str, Any]:
    """One transfer event's provenance, at the resolution the record allows."""
    row = {"source": transfer.get("source"), "target": transfer.get("target"),
           "id": transfer.get("id"), "role_id": None, "events": [], "priming": None}
    node_id = transfer.get("id")
    if node_id is not None and node_id not in snapshot:
        return {**row, "status": "unresolved_missing_structure",
                "reason": "the transfer's own prediction row is not in the snapshot"}
    pair = (transfer.get("source"), transfer.get("target"))
    if not all(isinstance(v, str) and v for v in pair):
        return {**row, "status": "unresolved_missing_structure",
                "reason": "the transfer names no pair, so there is nothing to trace"}
    role = role_match(pair, roles)
    if role is None:
        return {**row, "status": "unresolved_no_role",
                "reason": "no recorded role's exemplars contain both tags"}
    row["role_id"] = role.get("id")
    behind = asserting_events(role, events)
    if not behind:
        return {**row, "status": "unresolved_missing_events",
                "reason": "the role matched but no recorded event asserts it"}
    row["events"] = [e.get("id") for e in behind]
    priming = transfer.get("schema_prior")
    if not priming:
        return {**row, "status": "unresolved_no_priming",
                "reason": "the prediction records no schema prior, so no priming licensed it"}
    row["priming"] = priming
    return {**row, "status": RESOLVED,
            "reason": "role matched, its events are recorded, and a prior licensed the prediction"}


def summarise(traces: list[dict]) -> dict[str, Any]:
    """The share, its denominator, and every unresolved reason, counted apart."""
    total = len(traces)
    counts = {status: 0 for status in STATUSES}
    for row in traces:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    resolved = counts[RESOLVED]
    return {
        "transfer_events": total,
        "denominator": total,
        "resolved": resolved,
        "unresolved": total - resolved,
        "statuses": counts,
        "share": (resolved / total) if total else None,
        "measurable": total > 0,
        "not_measurable_reason": (None if total else
                                  "no transfer event was recorded, so no share exists"),
    }


# ---------------------------------------------------------------------------
# Controls: fixtures whose provenance is known by construction.
# ---------------------------------------------------------------------------

def _fixtures() -> dict[str, dict[str, Any]]:
    roles = [{"id": "role_1", "exemplars": ["willow", "teal"]}]
    events = [{"id": "B:0:1", "tags": ["willow", "teal"]},
              {"id": "B:0:2", "tags": ["willow", "teal"]},
              {"id": "B:1:1", "tags": ["cedar", "maple"]}]
    resolved = {"id": "pred_1", "source": "willow", "target": "teal",
                "schema_prior": "schema_7"}
    return {
        "resolved": {"transfer": resolved, "roles": roles, "events": events,
                     "snapshot": {"pred_1"}, "expected": RESOLVED},
        "no_role": {"transfer": resolved, "roles": [], "events": events,
                    "snapshot": {"pred_1"}, "expected": "unresolved_no_role"},
        "no_events": {"transfer": resolved, "roles": roles, "events": [],
                      "snapshot": {"pred_1"}, "expected": "unresolved_missing_events"},
        "no_priming": {"transfer": {**resolved, "schema_prior": None}, "roles": roles,
                       "events": events, "snapshot": {"pred_1"},
                       "expected": "unresolved_no_priming"},
        "missing_row": {"transfer": resolved, "roles": roles, "events": events,
                        "snapshot": set(), "expected": "unresolved_missing_structure"},
    }


def run_controls(tracer: Callable[..., dict] | None = None) -> dict[str, Any]:
    """Prove the tracer on provenance it knows before pointing it at a run.

    `tracer` defaults to the module's own, resolved at call time, so a broken
    replacement can be substituted and the controls must reject it.
    """
    tracer = tracer or trace_transfer
    results: dict[str, Any] = {}
    for name, fixture in _fixtures().items():
        got = tracer(fixture["transfer"], fixture["roles"], fixture["events"],
                     fixture["snapshot"])
        results[name] = {"expected": fixture["expected"], "status": got["status"],
                         "passed": got["status"] == fixture["expected"],
                         "reason": got["reason"]}
    # The flips: each leg removed from the resolved fixture must change the answer.
    base = _fixtures()["resolved"]
    flips = {
        "role_removed_flips": ({"roles": []}, "unresolved_no_role"),
        "events_removed_flips": ({"events": []}, "unresolved_missing_events"),
        "priming_removed_flips": ({"transfer": {**base["transfer"], "schema_prior": None}},
                                  "unresolved_no_priming"),
    }
    for name, (override, expected) in flips.items():
        got = tracer(override.get("transfer", base["transfer"]),
                     override.get("roles", base["roles"]),
                     override.get("events", base["events"]), base["snapshot"])
        results[name] = {"expected": expected, "status": got["status"],
                         "passed": got["status"] == expected,
                         "reason": "a leg that cannot change the answer is not being read"}
    empty = summarise([])
    results["empty_denominator_is_not_measurable"] = {
        "expected": "measurable=True, share=None",
        "status": "measurable=%s, share=%s" % (empty["measurable"], empty["share"]),
        "passed": empty["measurable"] is False and empty["share"] is None,
        "reason": "an unmeasurable quantity is never reported as zero (rule 13b)",
    }
    return {"controls": results, "all_passed": all(r["passed"] for r in results.values())}


def compare_to_expected(tracer: Callable[..., dict]) -> dict[str, Any]:
    """Point the controls at a tracer and report what it failed to satisfy.

    Pointed at a tracer that always answers `resolved_role_match`, this must
    report failures; otherwise the controls are decoration.
    """
    report = run_controls(tracer)
    failures = sorted(name for name, row in report["controls"].items() if not row["passed"])
    return {"passed": report["all_passed"], "failures": failures,
            "checked": len(report["controls"])}


def always_resolved(transfer, roles, events, snapshot):
    return {"source": transfer.get("source"), "target": transfer.get("target"),
            "id": transfer.get("id"), "role_id": "role_1", "events": ["stub"],
            "priming": "stub", "status": RESOLVED, "reason": "stub"}


def self_test() -> dict[str, Any]:
    controls = run_controls()
    broken = compare_to_expected(always_resolved)
    ok = controls["all_passed"] and (not broken["passed"] and bool(broken["failures"]))
    return {
        "kind": "transfer_provenance_self_test",
        "controls": controls,
        "comparator_rejects_a_broken_tracer": not broken["passed"],
        "comparator_failures": broken["failures"],
        "all_passed": ok,
    }


# ---------------------------------------------------------------------------
# The pre-run measurement: two contexts through the frozen engine.
# ---------------------------------------------------------------------------

def _db_path() -> Path:
    try:
        from organica.paths import scratch_db
        return Path(scratch_db("transfer_provenance.db"))
    except Exception:
        path = ROOT / ".scratch" / "transfer_provenance.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


def _pred_row(prediction) -> dict[str, Any]:
    evidence = getattr(prediction, "evidence", {}) or {}
    count = evidence.get("temporal_count", evidence.get("count", 0))
    return {"id": getattr(prediction, "id", None),
            "source": getattr(prediction, "source", None),
            "target": getattr(prediction, "target", None),
            "count": int(count or 0),
            "schema_prior": evidence.get("schema_prior")}


def _roles_of(report, service) -> tuple[str | None, list[dict]]:
    """The engine's roles, if it exposes them, with the name of the source used."""
    candidates = (("report.roles", getattr(report, "roles", None)),
                  ("service._last_roles", getattr(service, "_last_roles", None)),
                  ("service.roles", getattr(service, "roles", None)))
    for source, values in candidates:
        if values:
            return source, [{"id": getattr(r, "id", None),
                             "exemplars": list(getattr(r, "exemplars", []) or [])}
                            for r in values]
    return None, []


def measure(seed: int, cycles: int, phase_a_cycles: int, phase_b_cycles: int) -> dict[str, Any]:
    """Run both contexts and trace every transfer in the recorded state."""
    from organica.memory import MemoryService, _extract_tags
    from organica.sleep import SleepService
    from benchmarks.cross_context_reuse_benchmark import (
        VOCAB_A, VOCAB_B, generate_world_events)

    db = _db_path()
    if db.exists():
        db.unlink()
    mem = MemoryService(str(db))
    service = SleepService(mem)
    minimum = int(getattr(service, "PREDICTION_MIN_COUNT", 5))
    learned: dict[tuple[str, str], dict] = {}
    a_priors: set[str] = set()
    roles: list[dict] = []
    roles_source = None
    events_b: list[dict] = []
    b_preds: list[dict] = []
    try:
        for cycle, texts in enumerate(generate_world_events(VOCAB_A, phase_a_cycles, seed=seed)):
            with mem.batch():
                for text in texts:
                    mem.store(text, event_type="observe", source="env:A")
            report = service.run_sleep_cycle()
            for row in (_pred_row(p) for p in (getattr(report, "predictions", None) or [])):
                if row["schema_prior"]:
                    a_priors.add(row["schema_prior"])
                if row["count"] >= minimum and row["source"] and row["target"]:
                    learned[(row["source"], row["target"])] = row
        for cycle, texts in enumerate(generate_world_events(VOCAB_B, phase_b_cycles,
                                                            seed=seed + 1000)):
            with mem.batch():
                for index, text in enumerate(texts):
                    mem.store(text, event_type="observe", source="env:B")
                    events_b.append({"id": "B:%d:%d" % (cycle, index),
                                     "cycle": cycle, "text": text,
                                     "tags": _extract_tags(text)})
            report = service.run_sleep_cycle()
            source_name, cycle_roles = _roles_of(report, service)
            roles_source = roles_source or source_name
            roles.extend(r for r in cycle_roles if r["id"] not in {x["id"] for x in roles})
            b_preds = [_pred_row(p) for p in (getattr(report, "predictions", None) or [])]
    finally:
        mem.close()
        db.unlink(missing_ok=True)

    snapshot = {row["id"] for row in b_preds if row["id"]}
    # A transfer event is a prediction in B that a schema prior licensed.  The two
    # contexts use disjoint vocabularies, so an identical tag pair cannot reappear
    # in B: a definition based on pair identity could not fire in this design, and
    # a denominator of zero from it would report a dead definition as a null
    # result.  Pair identity is still counted, separately, so the claim is visible.
    identical_pairs = [row for row in b_preds
                       if (row["source"], row["target"]) in learned]
    transfers = [row for row in b_preds if row["schema_prior"] and row["count"] >= minimum]
    traces = [{"transfer": {"id": row["id"], "source": row["source"],
                            "target": row["target"],
                            "schema_prior": row["schema_prior"]},
               **trace_transfer({"id": row["id"], "source": row["source"],
                                 "target": row["target"],
                                 "schema_prior": row["schema_prior"]},
                                roles, events_b, snapshot)}
              for row in transfers]
    summary = summarise(traces)
    return {
        "kind": "transfer_provenance_measurement",
        "instrument": "benchmarks/transfer_provenance.py",
        "question": "Q028",
        "seed": seed,
        "cycles": cycles,
        "phase_a_cycles": phase_a_cycles,
        "phase_b_cycles": phase_b_cycles,
        "resolution": ("event-level for the role leg (stored events), structure-level "
                       "for the priming leg (a schema id, not its events)"),
        "roles_source": roles_source,
        "roles_recorded": len(roles),
        "events_recorded": len(events_b),
        "transfer_definition": ("a prediction in B that carries a schema prior and at least "
                                "PREDICTION_MIN_COUNT transitions; the prior is the transferred "
                                "structure, because the two contexts share no tags"),
        "identical_pair_reappearances": len(identical_pairs),
        "identical_pair_note": ("counted and reported, but it cannot fire across disjoint "
                                "vocabularies, so it is never the denominator"),
        "priors_seen_in_a": len(a_priors),
        "priors_shared_with_a": sum(1 for row in transfers
                                    if row["schema_prior"] in a_priors),
        "no_threshold": True,
        "no_verdict": True,
        "measurement": summary,
        "traces": traces,
        "note": ("This is the instrument's pre-run measurement, not a transfer result. "
                 "It sets no threshold and makes no claim about the organism; the "
                 "campaign that Q028 licenses has no preregistration on disk."),
    }


def render_report(artifact: dict) -> str:
    m = artifact["measurement"]
    share = "not measurable" if m["share"] is None else "%.4f" % m["share"]
    lines = [
        "# Transfer provenance (Q028) — the instrument, before the run",
        "",
        "**Generated from [`docs/transfer_provenance.json`](transfer_provenance.json); do not",
        "edit by hand.** Rebuild with `python -m benchmarks.transfer_provenance --measure`,",
        "and re-check the page with `--check`.",
        "",
        "## What this is",
        "",
        "Q028 asks whether a transfer event can be traced to the role satisfaction that",
        "licensed it. This instrument answers that from **recorded state only**: a transfer",
        "is resolved when a role's exemplars contain the transferred pair, at least one",
        "recorded event asserts that role, and the prediction carries the schema prior that",
        "licensed it. Anything less is counted with its reason. **There is no threshold, no",
        "verdict and no transfer claim in this document.**",
        "",
        "## Controls, run before the measurement",
        "",
        "| control | expected | observed | passed |",
        "|---|---|---|---|",
    ]
    for name, row in artifact["controls"]["controls"].items():
        lines.append("| `%s` | `%s` | `%s` | %s |"
                     % (name, row["expected"], row["status"], "yes" if row["passed"] else "no"))
    lines += [
        "",
        "The comparator was pointed at a tracer that always answers `resolved_role_match`,",
        "and rejected it: %s. A control set that cannot fail would license a transfer claim"
        % ("yes" if artifact["comparator_rejects_a_broken_tracer"] else "no"),
        "on nothing.",
        "",
        "## The pre-run measurement",
        "",
        "| quantity | value |",
        "|---|---|",
        "| transfer events (denominator) | %d |" % m["denominator"],
        "| resolved to a role match | %d |" % m["resolved"],
        "| unresolved | %d |" % m["unresolved"],
        "| share resolved | %s |" % share,
        "| roles recorded | %d (source `%s`) |" % (artifact["roles_recorded"],
                                                   artifact["roles_source"]),
        "| events recorded | %d |" % artifact["events_recorded"],
        "| identically-paired reuses (cannot fire across contexts) | %d |"
        % artifact["identical_pair_reappearances"],
        "| schema priors recorded in A | %d |" % artifact["priors_seen_in_a"],
        "| B priors whose id was also recorded in A | %d |" % artifact["priors_shared_with_a"],
        "",
        "| status | count |",
        "|---|---|",
    ]
    for status in STATUSES:
        lines.append("| `%s` | %d |" % (status, m["statuses"].get(status, 0)))
    lines += [
        "",
        "## What the number is, and is not",
        "",
        "- **Resolution is mixed by design.** The role leg is event-level: the events are the",
        "  stored ones. The priming leg is structure-level: the engine records a schema id,",
        "  not the events that created it. This does not claim observation-level provenance",
        "  for the whole chain.",
        "- **A zero denominator is not a zero share.** If the run records no transfer event,",
        "  the share is reported as `null` and marked not measurable (AGENTS rule 13b).",
        "- **A shared prior id is the stronger claim, and it is counted separately.** The two",
        "  contexts use disjoint vocabularies, so a schema id recorded in A need not reappear",
        "  in B. The table reports how many B priors were also seen in A; where that count is",
        "  zero, \"transfer\" here means *licensed by a prior*, not *carried from A*.",
        "- **A zero share with a real denominator is a measurement, not a null.** With",
        "  transfers recorded and none resolved, the unresolved column names the leg that",
        "  failed, which is the diagnostic Q028 asks for.",
        "- **This is not the campaign's result.** It exists so the measure is in place, and",
        "  proved able to fail, before the campaign runs; the campaign still needs its own",
        "  preregistration.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Transfer provenance (Q028).")
    parser.add_argument("--self-test", action="store_true",
                        help="run the controls and the broken-tracer comparator")
    parser.add_argument("--measure", action="store_true",
                        help="run the two contexts and write the pre-run measurement")
    parser.add_argument("--check", action="store_true",
                        help="re-run the self-test and compare the page with a fresh render")
    parser.add_argument("--report", action="store_true",
                        help="regenerate the page from the committed artifact")
    parser.add_argument("--seed", type=int, default=20261101)
    parser.add_argument("--phase-a-cycles", type=int, default=40)
    parser.add_argument("--phase-b-cycles", type=int, default=40)
    args = parser.parse_args(argv)

    if args.report:
        art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        DOC.write_text(render_report(art), encoding="utf-8")
        print("wrote %s" % DOC.name)
        return 0
    if args.check:
        result = self_test()
        if not result["all_passed"]:
            print("FAIL: the instrument's controls do not pass")
            return 1
        if not ARTIFACT.exists() or not DOC.exists():
            print("FAIL: the artifact or page is missing")
            return 1
        art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        if DOC.read_text(encoding="utf-8") != render_report(art):
            print("FAIL: %s is stale; rebuild with --report" % DOC.name)
            return 1
        print("transfer provenance: controls pass, page current")
        return 0
    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=1, sort_keys=True))
        return 0 if result["all_passed"] else 1
    if not args.measure:
        parser.print_help()
        return 2

    result = self_test()
    if not result["all_passed"]:
        print("FAIL: the instrument's controls must pass before it measures")
        return 1
    art = measure(args.seed, args.phase_a_cycles + args.phase_b_cycles,
                  args.phase_a_cycles, args.phase_b_cycles)
    art["controls"] = result["controls"]
    art["comparator_rejects_a_broken_tracer"] = result["comparator_rejects_a_broken_tracer"]
    art["generated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ARTIFACT.write_text(json.dumps(art, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    DOC.write_text(render_report(art), encoding="utf-8")
    m = art["measurement"]
    print(json.dumps({"wrote": [ARTIFACT.name, DOC.name],
                      "transfers": m["denominator"], "resolved": m["resolved"],
                      "share": m["share"], "roles_source": art["roles_source"]},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
