"""The six-seed A1 feasibility and adversarial audit.

This runs no arm cell.  It asks whether the selector produces exactly four
disjoint targets for every provisional seed from the pre-cycle-37 state, and
whether the same targets survive future-blindness, determinism, report-
blindness and sleep-blindness checks.
"""
import argparse
import inspect
import json
import random
import statistics
import tempfile
from pathlib import Path

from benchmarks import a1_arms
from benchmarks import a1_target_selection as selection
from benchmarks.a1_arms import sample_u
from organica.memory import MemoryService

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "docs" / "a1_adversarial_audit.json"
PAGE_PATH = ROOT / "docs" / "A1-ADVERSARIAL-AUDIT.md"
KIND = "A1-ADVERSARIAL-AUDIT-1"
ID = "A1-ADVERSARIAL-AUDIT-1"
DATE = "2026-11-14"
N = selection.N_PER_SEED


def _same(short: dict, long: dict) -> dict:
    same_events = short.get("event_cycles") == long.get("event_cycles")
    same_selected = short.get("selected") == long.get("selected")
    same_u = short.get("u") == long.get("u")
    same_members = short.get("cycle_member") == long.get("cycle_member")
    same_digest = short.get("selection_digest") == long.get("selection_digest")
    return {
        "pass": all((same_selected, same_u, same_members, same_digest)),
        "same_event_count": same_events,
        "same_selected": same_selected,
        "same_u": same_u,
        "same_cycle_member": same_members,
        "same_digest": same_digest,
        "short_selected": short.get("selected") or [],
        "long_selected": long.get("selected") or [],
    }


def _feasibility(row: dict) -> dict:
    selected = row.get("selected") or []
    endpoints = [tag for edge in selected for tag in edge.split(">", 1)]
    disjoint = len(endpoints) == len(set(endpoints))
    positive = all(
        ((row.get("u") or {}).get(edge) or {}).get("strength", 0) > 0
        for edge in selected
    )
    cycle_member = all((row.get("cycle_member") or {}).get(edge) for edge in selected)
    passed = (
        row.get("status") == "TARGET SET FORMED"
        and len(selected) == N
        and disjoint
        and positive
        and cycle_member
    )
    return {
        "pass": passed,
        "status": row.get("status"),
        "selected": selected,
        "candidate_count": row.get("candidate_count"),
        "eligible_count": row.get("eligible_count"),
        "disjoint": disjoint,
        "positive_u": positive,
        "cycle_member": cycle_member,
    }


def _permutation(selected: list[bool], values: list[float]) -> float:
    observed = (statistics.mean(v for s, v in zip(selected, values) if s)
                - statistics.mean(v for s, v in zip(selected, values) if not s))
    rng = random.Random(0)
    hits = 0
    draws = 20000
    for _ in range(draws):
        rng.shuffle(selected)
        diff = (statistics.mean(v for s, v in zip(selected, values) if s)
                - statistics.mean(v for s, v in zip(selected, values) if not s))
        hits += abs(diff) >= abs(observed)
    return hits / draws


def _representativeness() -> dict:
    """Measure the selected target sample against all eligible candidates."""
    doc = json.loads(selection.OUT_PATH.read_text(encoding="utf-8"))
    flags: list[bool] = []
    strengths: list[float] = []
    selected_edges: list[str] = []
    eligible_counts: dict[str, int] = {}
    candidate_counts: dict[str, int] = {}
    for seed, row in doc["per_seed"].items():
        chosen = set(row["selected"])
        selected_edges.extend(row["selected"])
        eligible_counts[seed] = int(row["eligible_count"])
        candidate_counts[seed] = int(row["candidate_count"])
        for edge, u in row["u"].items():
            flags.append(edge in chosen)
            strengths.append(float(u["strength"]))

    selected_strength = [v for s, v in zip(flags, strengths) if s]
    unselected_strength = [v for s, v in zip(flags, strengths) if not s]
    p_value = _permutation(flags[:], strengths)
    selected_observations = len(selected_edges)
    unique_edges = len(set(selected_edges))
    all_eligible = all(eligible_counts[s] == candidate_counts[s] for s in eligible_counts)
    passed = (
        selected_observations == 24
        and unique_edges == 23
        and len(flags) == 382
        and all_eligible
        and len(unselected_strength) == 358
    )
    return {
        "pass": passed,
        "source": "docs/a1_target_selection.json",
        "estimand": "representative eligible pre-37 cycle-membership directed-edge population",
        "measurement": {
            "selected_observations": selected_observations,
            "unique_target_edges": unique_edges,
            "unselected_candidates": len(unselected_strength),
            "candidates": len(flags),
            "all_candidates_eligible": all_eligible,
            "eligible_counts": eligible_counts,
            "selected_median_strength": statistics.median(selected_strength),
            "unselected_median_strength": statistics.median(unselected_strength),
            "selected_mean_strength": round(statistics.mean(selected_strength), 3),
            "unselected_mean_strength": round(statistics.mean(unselected_strength), 3),
            "permutation_p": round(p_value, 5),
        },
        "not_a_sample_of": [
            "high-U edges",
            "hard edges",
            "carrier-enriched anomalies",
        ],
        "conclusion": (
            "The selected targets are a representative eligible pre-37 sample; "
            "A1 does not estimate a high-U, hard-edge or carrier-enriched effect."
        ),
        "statistical_note": (
            "The permutation p-value is descriptive. Failure to reject a difference "
            "is not an equivalence test and does not by itself establish "
            "representativeness; the design fact is that every candidate is eligible "
            "and the hash order ignores U."
        ),
    }


def _u_sampler_pre_sleep() -> dict:
    source = inspect.getsource(a1_arms.run_cell)
    sample_at = source.index("pending_u = sample_u(")
    sleep_at = source.index("report = service.run_sleep_cycle()")
    return {
        "pass": sample_at < sleep_at,
        "sample_before_sleep_call": sample_at < sleep_at,
    }


def _report_blindness() -> dict:
    source = inspect.getsource(selection.run_seed)
    forbidden = ("predictions", "loops", "dreams", "assertions", "carriers", "served", "rank")
    hits = [token for token in forbidden if token in source]
    return {
        "pass": not hits,
        "forbidden_tokens_found": hits,
        "allowed_report_fields": [],
    }


def _sleep_blindness() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        memory = MemoryService(str(Path(tmp) / "sleep-blindness.db"))
        try:
            memory.store("alpha beta gamma", event_type="observe", source="env")
            edges = list(memory.temporal_edges(min_count=1))
            if not edges:
                return {"pass": False, "reason": "observation produced no temporal edge"}
            target = (edges[0][0], edges[0][1])
            before = sample_u(memory, {target}, selection.U_CYCLE)[target]
            memory.store("alpha beta gamma", event_type="sleep", source="sleep")
            after = sample_u(memory, {target}, selection.U_CYCLE)[target]
            return {
                "pass": before == after,
                "target": "%s>%s" % target,
                "before": before,
                "after": after,
            }
        finally:
            memory.close()


def run_seed(seed: int) -> dict:
    short_world = selection.generate_compositional_world(
        seed=seed, cycles=selection.U_CYCLE
    )
    long_world = selection.generate_compositional_world(
        seed=seed, cycles=selection.CYCLES
    )
    same_prefix = (
        short_world["events"] == long_world["events"][:len(short_world["events"])]
        and short_world["trainable"] == long_world["trainable"][:len(short_world["trainable"])]
    )
    short = selection.run_seed(seed, world=short_world)
    long = selection.run_seed(seed, world=long_world)
    again = selection.run_seed(seed, world=long_world)
    future = _same(short, long)
    future["same_world_prefix"] = same_prefix
    future["pass"] = future["pass"] and same_prefix
    determinism = _same(long, again)
    return {
        "seed": seed,
        "future_blindness": future,
        "determinism": determinism,
        "feasibility": _feasibility(long),
        "long": {
            "candidate_count": long.get("candidate_count"),
            "eligible_count": long.get("eligible_count"),
            "selected": long.get("selected") or [],
            "event_cycles": long.get("event_cycles"),
        },
    }


def build() -> dict:
    per_seed = {str(seed): run_seed(seed) for seed in selection.SEEDS}
    report = _report_blindness()
    sleep = _sleep_blindness()
    self_test = selection.self_test()
    p0 = {
        "u_sampled_before_cycle_36_sleep": _u_sampler_pre_sleep(),
        "pre37_candidate_universe": {
            "pass": all(row["long"]["event_cycles"] == selection.U_CYCLE
                        for row in per_seed.values()),
        },
        "future_blindness": {
            "pass": all(row["future_blindness"]["pass"] for row in per_seed.values()),
        },
        "report_blindness": report,
        "sleep_blindness": sleep,
        "determinism": {
            "pass": all(row["determinism"]["pass"] for row in per_seed.values()),
        },
    }
    p0_pass = (
        p0["u_sampled_before_cycle_36_sleep"]["pass"]
        and p0["pre37_candidate_universe"]["pass"]
        and p0["future_blindness"]["pass"]
        and p0["report_blindness"]["pass"]
        and p0["sleep_blindness"]["pass"]
        and p0["determinism"]["pass"]
    )
    representativeness = _representativeness()
    all_pass = (
        p0_pass
        and all(row["feasibility"]["pass"] for row in per_seed.values())
        and not self_test
        and representativeness["pass"]
    )
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": (
            "P0 PASS — SIX-SEED FEASIBILITY AND BLINDNESS"
            if all_pass
            else "AUDIT FAIL — DO NOT FREEZE"
        ),
        "engine": "0.15.0",
        "u_cycle": selection.U_CYCLE,
        "n_per_seed": N,
        "p0_pass": p0_pass,
        "p0": p0,
        "representativeness": representativeness,
        "all_pass": all_pass,
        "per_seed": per_seed,
        "checks": {
            "report_blindness": report,
            "sleep_blindness": sleep,
            "selector_self_test": self_test,
        },
        "not_evidence": (
            "A no-arm feasibility and adversarial audit. It selects draft "
            "targets, records a descriptive selection-representativeness "
            "measurement, but freezes no manifest, authorises no cell and "
            "records no A1 result."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("audit kind")
    if doc.get("n_per_seed") != N or doc.get("u_cycle") != selection.U_CYCLE:
        found.append("audit cycle or target size")
    per_seed = doc.get("per_seed") or {}
    if set(per_seed) != {str(seed) for seed in selection.SEEDS}:
        found.append("audit seed block")
    for seed, row in per_seed.items():
        for check in ("future_blindness", "determinism", "feasibility"):
            if not (row.get(check) or {}).get("pass"):
                found.append("seed %s %s failed" % (seed, check))
    checks = doc.get("checks") or {}
    for check in ("report_blindness", "sleep_blindness"):
        if not (checks.get(check) or {}).get("pass"):
            found.append("%s failed" % check)
    if checks.get("selector_self_test"):
        found.append("selector self-test failed")
    p0 = doc.get("p0") or {}
    for check in (
        "u_sampled_before_cycle_36_sleep",
        "pre37_candidate_universe",
        "future_blindness",
        "report_blindness",
        "sleep_blindness",
        "determinism",
    ):
        if not (p0.get(check) or {}).get("pass"):
            found.append("P0 %s failed" % check)
    if doc.get("p0_pass") is not True:
        found.append("P0 overall is not a pass")
    if doc.get("all_pass") is not True:
        found.append("audit overall is not a pass")
    rep = doc.get("representativeness") or {}
    if not rep.get("pass"):
        found.append("selection representativeness failed")
    if rep.get("estimand") != "representative eligible pre-37 cycle-membership directed-edge population":
        found.append("selection estimand changed")
    measurement = rep.get("measurement") or {}
    expected = {
        "selected_observations": 24,
        "unique_target_edges": 23,
        "unselected_candidates": 358,
        "candidates": 382,
    }
    for key, value in expected.items():
        if measurement.get(key) != value:
            found.append("selection measurement %s changed" % key)
    if not measurement.get("all_candidates_eligible"):
        found.append("not every candidate is eligible")
    if abs(float(measurement.get("permutation_p", 0)) - 0.91765) > 0.001:
        found.append("selection permutation p changed")
    return found


def render(doc: dict) -> str:
    rows = [
        "# A1 six-seed feasibility and adversarial audit",
        "",
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an experimental result.** No arm cell was run; no manifest was frozen.",
        "",
        "| Seed | Feasibility | Future-blind | Determinism | Selected |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for seed in selection.SEEDS:
        row = doc["per_seed"][str(seed)]
        rows.append("| %d | %s | %s | %s | %s |" % (
            seed,
            "PASS" if row["feasibility"]["pass"] else "FAIL",
            "PASS" if row["future_blindness"]["pass"] else "FAIL",
            "PASS" if row["determinism"]["pass"] else "FAIL",
            ", ".join("`%s`" % edge for edge in row["feasibility"]["selected"]) or "none",
        ))
    checks = doc["checks"]
    p0 = doc["p0"]
    rows += [
        "",
        "| Check | Result |",
        "| --- | --- |",
        "| P0 protocol compliance | %s |" % ("PASS" if doc["p0_pass"] else "FAIL"),
        "| U sampled before cycle-36 sleep | %s |" % ("PASS" if p0["u_sampled_before_cycle_36_sleep"]["pass"] else "FAIL"),
        "| Pre-37 candidate universe | %s |" % ("PASS" if p0["pre37_candidate_universe"]["pass"] else "FAIL"),
        "| Future-blindness | %s |" % ("PASS" if p0["future_blindness"]["pass"] else "FAIL"),
        "| Determinism | %s |" % ("PASS" if p0["determinism"]["pass"] else "FAIL"),
        "| Report-blindness | %s |" % ("PASS" if checks["report_blindness"]["pass"] else "FAIL"),
        "| Sleep-blindness | %s |" % ("PASS" if checks["sleep_blindness"]["pass"] else "FAIL"),
        "| Selector self-test | %s |" % ("PASS" if not checks["selector_self_test"] else "FAIL"),
        "",
        "## Selection representativeness",
        "",
        "**Source:** `%s`." % doc["representativeness"]["source"],
        "",
        "**Estimand:** %s." % doc["representativeness"]["estimand"],
        "",
        "| Measurement | Result |",
        "| --- | ---: |",
        "| Selected target observations | %d |" % doc["representativeness"]["measurement"]["selected_observations"],
        "| Unique target edges | %d |" % doc["representativeness"]["measurement"]["unique_target_edges"],
        "| Unselected candidates | %d |" % doc["representativeness"]["measurement"]["unselected_candidates"],
        "| Candidates | %d |" % doc["representativeness"]["measurement"]["candidates"],
        "| All candidates eligible | %s |" % ("yes" if doc["representativeness"]["measurement"]["all_candidates_eligible"] else "no"),
        "| Selected mean / median strength | %s / %s |" % (
            doc["representativeness"]["measurement"]["selected_mean_strength"],
            doc["representativeness"]["measurement"]["selected_median_strength"],
        ),
        "| Unselected mean / median strength | %s / %s |" % (
            doc["representativeness"]["measurement"]["unselected_mean_strength"],
            doc["representativeness"]["measurement"]["unselected_median_strength"],
        ),
        "| Descriptive permutation p | %s |" % doc["representativeness"]["measurement"]["permutation_p"],
        "",
        "**Conclusion:** %s" % doc["representativeness"]["conclusion"],
        "",
        "It is **not** a sample of %s." % ", ".join(doc["representativeness"]["not_a_sample_of"]),
        "",
        "%s" % doc["representativeness"]["statistical_note"],
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
    ]
    return "\n".join(rows)


def write() -> int:
    doc = build()
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(doc["status"])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    found = problems(doc)
    if not PAGE_PATH.exists():
        found.append("audit page is missing")
    elif PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("audit page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 adversarial audit: clean; %d seeds" % len(doc["per_seed"]))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
