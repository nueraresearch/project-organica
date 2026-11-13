"""MATCHED-CARRIER-REPLICATION-2.

Fresh-seed replication of the matched carrier base-rate contrast.  The original
Q4 census found 26 asserted-but-never-served world edges, and all 26 had ever
formed a reported loop.  Their matched never-served / never-asserted controls
formed a loop 13 times out of 26.  That is a +50 percentage-point difference and
a twofold enrichment, but it is one seed block.

This module asks whether the same contrast appears on a genuinely fresh six-seed
block (20615101-20615106), using the same world family, 120 cycles, cap 40 and
acquisition schedule.  The design is frozen in
``docs/matched_carrier_replication_prereg.json`` before any fresh seed runs.

Case: a world edge that is asserted in the final structure and has zero direct
served windows.  Control: a world edge in the same seed that is neither
asserted nor served.  Cases are sorted by ``(direct_count, edge)`` and each is
matched 1:1 to the nearest unused control by absolute direct-count difference,
with edge as the tie-break.  The endpoint is ``ever_loop``: at least one
reported ``loop_candidate`` path in any cycle contains the edge in either
orientation.

Inference is the exact two-sided McNemar test over discordant pairs and a
percentile bootstrap that resamples the six seeds as clusters (10,000
replicates, fixed RNG seed).  The verdict is ``REPLICATED`` only when the case
rate exceeds the control rate, exact McNemar p < 0.05, and the seed-cluster 95%
interval for the risk difference lies entirely above zero.  Magnitude
compatibility with the original +50 pp is reported descriptively, not required
for the verdict.

    ./.venv/bin/python -m benchmarks.matched_carrier_replication --freeze
    ./.venv/bin/python -m benchmarks.matched_carrier_replication --write
    ./.venv/bin/python -m benchmarks.matched_carrier_replication --check
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                      # noqa: E402
from benchmarks.acquisition_compositional import generate_compositional_world  # noqa: E402
from benchmarks.acquisition_harness import (                              # noqa: E402
    _CountingMemoryService,
    _make_scratch_db,
    _world_compositional_edges,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges  # noqa: E402
from benchmarks.presence_construct_audit import (                         # noqa: E402
    ACQ_SOURCE,
    PHASE_ACQUISITION,
)
from organica.sleep import SleepService                                   # noqa: E402

ID = "MATCHED-CARRIER-REPLICATION-2"
FROZEN_ON = "2026-11-12"
SEEDS = [20615201, 20615202, 20615203, 20615204, 20615205, 20615206]
CYCLES = 120
CAP = 40
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20261112
ORIGINAL_CASES = 26
ORIGINAL_CASE_LOOPS = 26
ORIGINAL_CONTROLS = 26
ORIGINAL_CONTROL_LOOPS = 13
ORIGINAL_DIFFERENCE = 0.5
ORIGINAL_CI = [0.345, 0.696]
ORIGINAL_P = 0.00024
Z_95 = 1.959963984540054
VERDICTS = ("REPLICATED", "NOT REPLICATED", "VOID")

PREREG = ROOT / "docs" / "matched_carrier_replication_2_prereg.json"
ARTIFACT = ROOT / "docs" / "matched_carrier_replication_2.json"
PAGE = ROOT / "docs" / "MATCHED-CARRIER-REPLICATION-2.md"


def build_prereg() -> dict:
    return {
        "prereg": ID,
        "kind": "matched_carrier_replication_prereg",
        "status": "FROZEN, NOT RUN",
        "frozen_on": FROZEN_ON,
        "question": (
            "Does the matched carrier base-rate contrast replicate on a fresh "
            "six-seed block: do asserted-but-never-served world edges form reported "
            "loops more often than matched never-served and never-asserted controls?"
        ),
        "reference": {
            "source": ".scratch/loop_retention.json",
            "case_loops": ORIGINAL_CASE_LOOPS,
            "case_n": ORIGINAL_CASES,
            "control_loops": ORIGINAL_CONTROL_LOOPS,
            "control_n": ORIGINAL_CONTROLS,
            "risk_difference_pp": 50.0,
            "seed_cluster_ci95_pp": [34.5, 69.6],
            "mcnemar_exact_p": ORIGINAL_P,
            "seeds": [20611601, 20611602, 20611603, 20611604, 20611605, 20611606],
        },
        "design": {
            "seeds": SEEDS,
            "cells": len(SEEDS),
            "cycles": CYCLES,
            "cap": CAP,
            "world": (
                "generate_compositional_world(seed=, cycles=120) with the "
                "PHASE_ACQUISITION schedule and one replay per seed"
            ),
            "case": "asserted world edge with zero direct served windows",
            "control": (
                "same-seed world edge with asserted=false and zero direct served "
                "windows"
            ),
            "matching": (
                "cases sorted by (final temporal count, edge); each case takes the "
                "nearest unused same-seed control by |final temporal count difference|; "
                "ties by lexicographically smaller edge; 1:1, no replacement"
            ),
            "direct_count": (
                "final direct temporal transition count from service._load_temporal(); "
                "validated against the Q4 census on seed 20611601, where all 112 world "
                "edges match the recorded count exactly"
            ),
            "endpoint": (
                "ever_loop: at least one reported loop_candidate path in any of the "
                "120 cycles contains the edge in either orientation"
            ),
            "replay": (
                "A single replay supplies the final asserted set, the direct served "
                "windows and every reported loop path. No committed fingerprint is "
                "available for this fresh block; the replay is the observation."
            ),
        },
        "endpoint": {
            "name": "ever_loop",
            "case_rate": "case_loops / matched_pairs",
            "control_rate": "control_loops / matched_pairs",
            "contrast": "case rate minus control rate, in percentage points",
        },
        "inference": {
            "paired_test": (
                "exact two-sided McNemar test on the discordant pairs; "
                "p = min(1, 2 * sum_{k=0}^{min(b,c)} C(b+c,k) / 2^(b+c))"
            ),
            "cluster_interval": (
                "percentile bootstrap over the six seeds as clusters: resample six "
                "seeds with replacement, pool their matched pairs, recompute the "
                "risk difference; 10,000 replicates; fixed RNG seed 20261112"
            ),
            "alpha": 0.05,
            "multiplicity": "one prespecified contrast; no adjustment",
            "magnitude_note": (
                "Whether the original +50 pp lies inside the fresh interval is "
                "reported, but it does not decide the replication verdict"
            ),
        },
        "criteria": [
            {
                "id": "R1",
                "name": "direction",
                "test": "case ever_loop rate > control ever_loop rate",
            },
            {
                "id": "R2",
                "name": "paired association",
                "test": "exact two-sided McNemar p < 0.05",
            },
            {
                "id": "R3",
                "name": "cluster precision",
                "test": "seed-cluster 95% interval lower bound > 0 pp",
            },
        ],
        "verdicts": {
            "REPLICATED": "R1, R2 and R3 all pass.",
            "NOT REPLICATED": "Any of R1, R2 or R3 fails.",
            "VOID": (
                "No case exists, the seed block collides with a recorded block, or "
                "1:1 matching cannot be completed in every seed."
            ),
        },
        "engine": {
            "version": "0.15.0",
            "cap": CAP,
            "cycles": CYCLES,
            "edit": "none",
        },
        "voided_prior_attempt": {
            "prereg": "MATCHED-CARRIER-REPLICATION-1",
            "seeds": [20615101, 20615102, 20615103, 20615104, 20615105, 20615106],
            "reason": (
                "The first pipeline matched on served-window counts, which are zero "
                "for every never-served edge, instead of the final temporal count. "
                "The control sample is therefore not the matched sample the census "
                "defines, and no contrast from that run is read. The seeds are not "
                "reused here."
            ),
            "record": ".scratch/matched_carrier_replication_1_void.json",
        },
        "result": ARTIFACT.relative_to(ROOT).as_posix(),
        "not_evidence": (
            "A six-seed diagnostic of one matched contrast in one synthetic world "
            "family. It is not a capability, retention, transfer, causal or "
            "engine-effect claim, and it does not show that loops cause assertion."
        ),
    }


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_prereg(body: dict) -> list[str]:
    found: list[str] = []
    if body.get("prereg") != ID:
        found.append("prereg id")
    if body.get("status") not in ("FROZEN, NOT RUN", "FROZEN, RUN"):
        found.append("prereg status")
    design = body.get("design") or {}
    if design.get("seeds") != SEEDS:
        found.append("seed block")
    if design.get("cells") != len(SEEDS):
        found.append("cell count")
    if design.get("cycles") != CYCLES or design.get("cap") != CAP:
        found.append("cycles or cap")
    reference = body.get("reference") or {}
    if (reference.get("case_loops"), reference.get("case_n"),
            reference.get("control_loops"), reference.get("control_n")) != (
            ORIGINAL_CASE_LOOPS, ORIGINAL_CASES, ORIGINAL_CONTROL_LOOPS,
            ORIGINAL_CONTROLS):
        found.append("reference counts")
    if [row.get("id") for row in body.get("criteria") or []] != ["R1", "R2", "R3"]:
        found.append("criteria")
    if set(body.get("verdicts") or {}) != set(VERDICTS):
        found.append("verdict vocabulary")
    if body.get("result") != ARTIFACT.relative_to(ROOT).as_posix():
        found.append("result path")
    return found


def _run_seed(seed: int) -> dict:
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("matched_carrier_replication")
    memory = _CountingMemoryService(str(db_path))
    service = SleepService(memory)
    service.MAX_PREDICTIONS = CAP
    windows: list[list[tuple[str, str]]] = []
    loop_edges: set[tuple[str, str]] = set()
    loop_cycles: dict[tuple[str, str], list[int]] = defaultdict(list)
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                report = service.run_sleep_cycle()
                windows.append([(p.source, p.target) for p in report.predictions])
                cycle = len(windows)
                for loop in report.loops:
                    path = list(loop.path)
                    for a, b in zip(path, path[1:]):
                        for edge in ((a, b), (b, a)):
                            if edge in world_edges and edge not in loop_edges:
                                loop_edges.add(edge)
                                loop_cycles[edge].append(cycle)
        temporal = service._load_temporal()
        candidates = service._load_prior_candidates()
        asserted = {(a, b) for a, targets in structure_edges(candidates).items()
                    for b in targets}
    finally:
        memory.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    asserted_world = asserted & world_edges
    served = Counter(edge for window in windows for edge in window
                     if edge in world_edges)
    edge_rows = []
    for edge in sorted(world_edges):
        edge_rows.append({
            "seed": seed,
            "edge": "%s>%s" % edge,
            "direct_count": int(temporal.get(edge[0], {}).get(edge[1], 0)),
            "served": served.get(edge, 0) > 0,
            "asserted": edge in asserted_world,
            "ever_loop": edge in loop_edges,
            "loop_cycles": loop_cycles.get(edge, []),
        })
    return {
        "seed": seed,
        "world_edges": len(world_edges),
        "asserted_world_edges": len(asserted_world),
        "served_world_edges": len(served),
        "rows": edge_rows,
    }


def _match(rows: list[dict]) -> tuple[list[tuple[dict, dict]], list[dict]]:
    cases = [row for row in rows if row["asserted"] and not row["served"]]
    controls = [row for row in rows if not row["asserted"] and not row["served"]]
    available = list(controls)
    pairs: list[tuple[dict, dict]] = []
    unmatched: list[dict] = []
    for case in sorted(cases, key=lambda row: (row["direct_count"], row["edge"])):
        if not available:
            unmatched.append(case)
            continue
        control = min(
            available,
            key=lambda row: (abs(row["direct_count"] - case["direct_count"]),
                             row["edge"]),
        )
        available.remove(control)
        pairs.append((case, control))
    return pairs, unmatched


def _mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2.0 ** n)
    return min(1.0, 2.0 * tail)


def _bootstrap(pairs_by_seed: dict[int, list[tuple[dict, dict]]]) -> dict:
    rng = random.Random(BOOTSTRAP_SEED)
    values = []
    seeds = [seed for seed in SEEDS if pairs_by_seed.get(seed)]
    if len(seeds) != len(SEEDS):
        return {"replicates": 0, "ci95_pp": None, "reason": "not every seed has pairs"}
    for _ in range(BOOTSTRAP_REPLICATES):
        sample = [seeds[rng.randrange(len(seeds))] for _ in seeds]
        diffs = [float(case["ever_loop"]) - float(control["ever_loop"])
                 for seed in sample for case, control in pairs_by_seed[seed]]
        values.append(100.0 * statistics.fmean(diffs))
    values.sort()
    low = values[int(0.025 * len(values))]
    high = values[int(0.975 * len(values)) - 1]
    return {
        "replicates": BOOTSTRAP_REPLICATES,
        "rng_seed": BOOTSTRAP_SEED,
        "ci95_pp": [round(low, 4), round(high, 4)],
        "mean_pp": round(statistics.fmean(values), 4),
    }


def _summarise(pairs: list[tuple[dict, dict]], unmatched: list[dict]) -> dict:
    both = sum(1 for case, control in pairs if case["ever_loop"] and control["ever_loop"])
    case_only = sum(1 for case, control in pairs
                    if case["ever_loop"] and not control["ever_loop"])
    control_only = sum(1 for case, control in pairs
                       if not case["ever_loop"] and control["ever_loop"])
    neither = sum(1 for case, control in pairs
                  if not case["ever_loop"] and not control["ever_loop"])
    case_loops = both + case_only
    control_loops = both + control_only
    n = len(pairs)
    difference = 100.0 * (case_loops - control_loops) / n if n else None
    case_rate = case_loops / n if n else None
    control_rate = control_loops / n if n else None
    ratio = (case_rate / control_rate
             if case_rate is not None and control_rate not in (None, 0.0) else None)
    p = _mcnemar_exact(case_only, control_only)
    pairs_by_seed: dict[int, list[tuple[dict, dict]]] = defaultdict(list)
    for case, control in pairs:
        pairs_by_seed[case["seed"]].append((case, control))
    bootstrap = _bootstrap(pairs_by_seed)
    ci = bootstrap.get("ci95_pp")
    criteria = {
        "R1_direction": bool(n and case_loops > control_loops),
        "R2_mcnemar": bool(n and p < 0.05 and case_loops != control_loops),
        "R3_cluster_ci_above_zero": bool(ci and ci[0] > 0.0),
        "original_difference_pp_inside_ci": bool(
            ci and ci[0] <= 100.0 * ORIGINAL_DIFFERENCE <= ci[1]),
    }
    if not n or unmatched:
        verdict = "VOID"
    elif all(criteria[key] for key in ("R1_direction", "R2_mcnemar",
                                       "R3_cluster_ci_above_zero")):
        verdict = "REPLICATED"
    else:
        verdict = "NOT REPLICATED"
    return {
        "pairs": n,
        "unmatched_cases": len(unmatched),
        "case_loops": case_loops,
        "control_loops": control_loops,
        "both_loop": both,
        "case_only_loop": case_only,
        "control_only_loop": control_only,
        "neither_loop": neither,
        "case_rate": round(case_rate, 6) if case_rate is not None else None,
        "control_rate": round(control_rate, 6) if control_rate is not None else None,
        "risk_difference_pp": round(difference, 4) if difference is not None else None,
        "risk_ratio": round(ratio, 4) if ratio is not None else None,
        "mcnemar_exact_p": round(p, 8),
        "cluster_bootstrap": bootstrap,
        "criteria": criteria,
        "verdict": verdict,
        "original": {
            "case_loops": ORIGINAL_CASE_LOOPS,
            "case_n": ORIGINAL_CASES,
            "control_loops": ORIGINAL_CONTROL_LOOPS,
            "control_n": ORIGINAL_CONTROLS,
            "risk_difference_pp": 100.0 * ORIGINAL_DIFFERENCE,
            "seed_cluster_ci95_pp": ORIGINAL_CI,
            "mcnemar_exact_p": ORIGINAL_P,
        },
    }


def build() -> dict:
    prereg = _load(PREREG)
    problems = _validate_prereg(prereg)
    from benchmarks.presence_cap_experiment import seed_collisions
    collisions = seed_collisions(SEEDS, allow=(PREREG, ARTIFACT))
    if collisions:
        problems.append("seed collision: %r" % (collisions,))
    if problems:
        raise SystemExit("REFUSED: " + "; ".join(problems))

    traces = [_run_seed(seed) for seed in SEEDS]
    rows = [row for trace in traces for row in trace["rows"]]
    pairs: list[tuple[dict, dict]] = []
    unmatched: list[dict] = []
    per_seed = []
    for trace in traces:
        seed_pairs, seed_unmatched = _match(trace["rows"])
        pairs.extend(seed_pairs)
        unmatched.extend(seed_unmatched)
        per_seed.append({
            "seed": trace["seed"],
            "world_edges": trace["world_edges"],
            "asserted_world_edges": trace["asserted_world_edges"],
            "served_world_edges": trace["served_world_edges"],
            "cases": sum(1 for row in trace["rows"]
                         if row["asserted"] and not row["served"]),
            "controls": sum(1 for row in trace["rows"]
                            if not row["asserted"] and not row["served"]),
            "matched_pairs": len(seed_pairs),
            "unmatched_cases": len(seed_unmatched),
            "case_loops": sum(1 for case, _ in seed_pairs if case["ever_loop"]),
            "control_loops": sum(1 for _, control in seed_pairs if control["ever_loop"]),
        })
    pair_rows = [{
        "seed": case["seed"],
        "case_edge": case["edge"],
        "case_direct_count": case["direct_count"],
        "case_ever_loop": case["ever_loop"],
        "control_edge": control["edge"],
        "control_direct_count": control["direct_count"],
        "control_ever_loop": control["ever_loop"],
        "absolute_count_difference": abs(case["direct_count"]
                                         - control["direct_count"]),
    } for case, control in pairs]
    summary = _summarise(pairs, unmatched)
    summary["asserted_world_edges"] = sum(t["asserted_world_edges"] for t in traces)
    summary["served_world_edges"] = sum(t["served_world_edges"] for t in traces)
    summary["world_edges"] = sum(t["world_edges"] for t in traces)
    summary["unmatched"] = [
        {"seed": row["seed"], "edge": row["edge"],
         "direct_count": row["direct_count"]}
        for row in unmatched
    ]
    return engine_stamp.stamp({
        "kind": "matched_carrier_replication",
        "status": "RUN",
        "prereg": PREREG.relative_to(ROOT).as_posix(),
        "question": prereg["question"],
        "scope": (
            "Six fresh seeds, one compositional world family, 120 cycles, cap 40 "
            "and one replay per seed. This block tests the matched ever_loop "
            "contrast; it does not test retention, causation or whether service "
            "changes assertion."
        ),
        "design": prereg["design"],
        "voided_prior_attempt": prereg.get("voided_prior_attempt"),
        "reference": prereg["reference"],
        "endpoint": prereg["endpoint"],
        "inference": prereg["inference"],
        "criteria": prereg["criteria"],
        "seeds": per_seed,
        "pairs": pair_rows,
        "summary": summary,
        "not_evidence": prereg["not_evidence"],
    })


def render(art: dict) -> str:
    summary = art["summary"]
    original = summary["original"]
    ci = summary["cluster_bootstrap"].get("ci95_pp")
    lines = [
        "# Matched carrier base-rate replication",
        "",
        "Generated from `%s` by "
        "`python -m benchmarks.matched_carrier_replication --write`. Do not edit by hand."
        % ARTIFACT.relative_to(ROOT),
        "",
        "**Verdict: `%s`.** The design was frozen in "
        "`%s` before the fresh block ran."
        % (summary["verdict"], PREREG.relative_to(ROOT)),
        "",
        "## Design",
        "",
        "- Seeds: **%s** (collision scan empty)."
        % ", ".join(str(seed) for seed in art["design"]["seeds"]),
        "- **%d** cycles, cap **%d**, PHASE_ACQUISITION schedule, one replay per seed."
        % (art["design"]["cycles"], art["design"]["cap"]),
        "- Case: asserted world edge with zero direct served windows.",
        "- Control: same-seed world edge that is neither asserted nor served.",
        "- Matching: %s." % art["design"]["matching"],
        "- Endpoint: `ever_loop`, a reported `loop_candidate` path containing the "
        "edge in either orientation in any cycle.",
        "",
    ]
    prior = art.get("voided_prior_attempt")
    if prior:
        lines += [
            "## Voided prior attempt",
            "",
            "`%s` on seeds %s is not read: %s" % (
                prior["prereg"], ", ".join(str(seed) for seed in prior["seeds"]),
                prior["reason"]),
            "The voided record is `%s`." % prior["record"],
            "",
        ]
    lines += [
        "## Result",
        "",
        "| Quantity | Original Q4 | Fresh block |",
        "| --- | ---: | ---: |",
        "| Matched pairs | %d | %d |"
        % (original["case_n"], summary["pairs"]),
        "| Cases ever looping | %d/%d | %d/%d |"
        % (original["case_loops"], original["case_n"],
           summary["case_loops"], summary["pairs"]),
        "| Controls ever looping | %d/%d | %d/%d |"
        % (original["control_loops"], original["control_n"],
           summary["control_loops"], summary["pairs"]),
        "| Risk difference | +%.1f pp | %s |"
        % (original["risk_difference_pp"],
           "not measurable" if summary["risk_difference_pp"] is None
           else "%+.1f pp" % summary["risk_difference_pp"]),
        "| Risk ratio | 2.00 | %s |"
        % ("not measurable" if summary["risk_ratio"] is None
           else "%.2f" % summary["risk_ratio"]),
        "| Seed-cluster 95%% CI | [%.1f, %.1f] pp | %s |"
        % (100.0 * original["seed_cluster_ci95_pp"][0],
           100.0 * original["seed_cluster_ci95_pp"][1],
           "not measurable" if not ci else "[%.1f, %.1f] pp" % tuple(ci)),
        "| Exact McNemar p | %.2e | %.2e |"
        % (original["mcnemar_exact_p"], summary["mcnemar_exact_p"]),
        "",
        "### Paired table",
        "",
        "| | Control loops | Control does not loop |",
        "| --- | ---: | ---: |",
        "| **Case loops** | %d | %d |"
        % (summary["both_loop"], summary["case_only_loop"]),
        "| **Case does not loop** | %d | %d |"
        % (summary["control_only_loop"], summary["neither_loop"]),
        "",
        "Discordant pairs: **%d** case-only, **%d** control-only. Unmatched cases: "
        "**%d**." % (summary["case_only_loop"], summary["control_only_loop"],
                     summary["unmatched_cases"]),
        "",
        "| Criterion | Passes |",
        "| --- | --- |",
        "| R1 case rate > control rate | %s |"
        % ("yes" if summary["criteria"]["R1_direction"] else "no"),
        "| R2 exact McNemar p < 0.05 | %s |"
        % ("yes" if summary["criteria"]["R2_mcnemar"] else "no"),
        "| R3 cluster 95%% interval above 0 | %s |"
        % ("yes" if summary["criteria"]["R3_cluster_ci_above_zero"] else "no"),
        "| Original +50 pp inside fresh interval (descriptive) | %s |"
        % ("yes" if summary["criteria"]["original_difference_pp_inside_ci"] else "no"),
        "",
        "## Per seed",
        "",
        "| Seed | World edges | Asserted | Served | Cases | Controls | Pairs | Case loops | Control loops |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in art["seeds"]:
        lines.append("| %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            row["seed"], row["world_edges"], row["asserted_world_edges"],
            row["served_world_edges"], row["cases"], row["controls"],
            row["matched_pairs"], row["case_loops"], row["control_loops"]))
    lines += [
        "",
        "## Every matched pair",
        "",
        "| Seed | Case | Count | Loop | Control | Count | Loop | |diff| |",
        "| ---: | --- | ---: | --- | --- | ---: | --- | ---: |",
    ]
    for row in art["pairs"]:
        lines.append("| %d | `%s` | %d | %s | `%s` | %d | %s | %d |" % (
            row["seed"], row["case_edge"], row["case_direct_count"],
            "yes" if row["case_ever_loop"] else "no",
            row["control_edge"], row["control_direct_count"],
            "yes" if row["control_ever_loop"] else "no",
            row["absolute_count_difference"]))
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "The fresh block tests whether the matched loop contrast repeats. It does "
        "not test loop retention, whether loops cause assertion, whether serving a "
        "direct edge would change the final structure, or any capability claim. "
        "The original +50 pp is shown for comparison only; the verdict is fixed by "
        "R1-R3.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != "matched_carrier_replication":
        found.append("artifact kind")
    if art.get("status") != "RUN":
        found.append("artifact status")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    prereg = _load(PREREG)
    found.extend(_validate_prereg(prereg))
    if art.get("prereg") != PREREG.relative_to(ROOT).as_posix():
        found.append("prereg path")
    if art.get("design", {}).get("seeds") != SEEDS:
        found.append("artifact seed block")
    rows = art.get("pairs") or []
    if len(rows) != art.get("summary", {}).get("pairs"):
        found.append("pair count")
    by_seed: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        by_seed[row["seed"]].append(row)
    if set(by_seed) != set(SEEDS):
        found.append("seed coverage")
    if any(len({row["case_edge"] for row in group}) != len(group)
           or len({row["control_edge"] for row in group}) != len(group)
           for group in by_seed.values()):
        found.append("matching is not 1:1")
    summary = art.get("summary") or {}
    unmatched = summary.get("unmatched") or []
    recomputed = _summarise([
        ({"seed": row["seed"], "edge": row["case_edge"],
          "direct_count": row["case_direct_count"],
          "ever_loop": row["case_ever_loop"], "asserted": True, "served": False},
         {"seed": row["seed"], "edge": row["control_edge"],
          "direct_count": row["control_direct_count"],
          "ever_loop": row["control_ever_loop"], "asserted": False, "served": False})
        for row in rows
    ], unmatched)
    for key in ("case_loops", "control_loops", "case_only_loop",
                "control_only_loop", "both_loop", "neither_loop",
                "mcnemar_exact_p", "risk_difference_pp", "criteria", "verdict"):
        if summary.get(key) != recomputed.get(key):
            found.append("summary %s" % key)
    if summary.get("pairs") != len(rows):
        found.append("summary pairs")
    from benchmarks.presence_cap_experiment import seed_collisions
    if seed_collisions(SEEDS, allow=(PREREG, ARTIFACT)):
        found.append("seed collision")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    return found


def freeze() -> int:
    if PREREG.exists():
        print("REFUSED: prereg exists")
        return 2
    doc = engine_stamp.stamp(build_prereg())
    PREREG.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print("froze %s" % PREREG.relative_to(ROOT))
    return 0


def write() -> int:
    body = build()
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    prereg = _load(PREREG)
    prereg["status"] = "FROZEN, RUN"
    prereg["completed_on"] = FROZEN_ON
    prereg["verdict"] = body["summary"]["verdict"]
    PREREG.write_text(json.dumps(prereg, indent=1) + "\n", encoding="utf-8")
    print("matched carrier replication: %s %s" % (
        body["summary"]["verdict"], json.dumps({
            "pairs": body["summary"]["pairs"],
            "case_loops": body["summary"]["case_loops"],
            "control_loops": body["summary"]["control_loops"],
            "risk_difference_pp": body["summary"]["risk_difference_pp"],
            "mcnemar_p": body["summary"]["mcnemar_exact_p"],
            "cluster_ci_pp": body["summary"]["cluster_bootstrap"].get("ci95_pp"),
        })))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no replication artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("matched carrier replication: %s %s" % (
        art["summary"]["verdict"], json.dumps({
            "pairs": art["summary"]["pairs"],
            "case_loops": art["summary"]["case_loops"],
            "control_loops": art["summary"]["control_loops"],
            "risk_difference_pp": art["summary"]["risk_difference_pp"],
        })))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.freeze:
        return freeze()
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
