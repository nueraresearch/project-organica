"""What coverage can the theory budget reach on a degree-12 hub?

The degree-12 coverage floor of 0.50 was fixed before the engine had ever been
measured at that degree, and the engine reached 0.40. A failed bar is not
evidence that the bar was wrong, so the next protocol's bar has to be set from a
measured ceiling rather than from a guess. This harness measures the quantity the
bar is about: the share of a degree-12 lattice's world edges that the engine's
stable predictions cover, at its own theory budget and at two larger ones, so the
ceiling is separated into the part the budget causes and the part the world does.

    ./.venv/bin/python -m benchmarks.theory_budget_ceiling --measure
    ./.venv/bin/python -m benchmarks.theory_budget_ceiling --reuse
    ./.venv/bin/python -m benchmarks.theory_budget_ceiling --check
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import date
from pathlib import Path

from benchmarks.decay_confirmation import (
    Counted,
    _feed,
    _stable,
    harvest_seeds,
    temp_db,
    world_edges,
)
from benchmarks.decay_fix_confirm import lattice_world
from organica.memory import MemoryService

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "theory_budget_ceiling" / "parts"
ARTIFACT = ROOT / "docs" / "theory_budget_ceiling.json"
DOC = ROOT / "docs" / "THEORY-BUDGET-CEILING.md"

DEGREE = 12
CYCLES = 300
SEED_BASE = 20300501
SEED_COUNT = 3
#: Theory cap, hypothesis cap. `shipped` is the engine's own budget; `lifted` is
#: above the world's subject count (13 tags), so it cannot bind by construction.
BUDGETS = {
    "shipped": (8, 15),
    "doubled": (16, 30),
    "lifted": (64, 128),
}
#: A difference this small is not a ceiling difference.
TOLERANCE = 0.02


def ceiling_seeds() -> list[int]:
    """The block, verified free — except for this harness's own record of it.

    The artifact records the seeds it ran, so a second invocation would otherwise
    find its own claim and refuse. This artifact is the allocation record for the
    block, and it is the one document allowed to claim it.
    """
    seeds = list(range(SEED_BASE, SEED_BASE + SEED_COUNT))
    if ARTIFACT.exists():
        try:
            recorded = json.loads(ARTIFACT.read_text(encoding="utf-8")).get("seeds") or []
        except (ValueError, OSError):
            recorded = []
        if recorded == seeds:
            return seeds
    claimed = harvest_seeds(ROOT / "docs")
    overlap = sorted(set(seeds) & claimed)
    if overlap:
        raise SystemExit("the ceiling block overlaps seeds already used under docs/: %s" % overlap)
    return seeds


def arm_for(budget: str):
    cap_theories, cap_hypotheses = BUDGETS[budget]
    return type(
        "BudgetArm_" + budget,
        (Counted,),
        {"MAX_THEORIES": cap_theories, "MAX_HYPOTHESES": cap_hypotheses},
    )


def cell(budget: str, seed: int, cycles: int = CYCLES) -> dict:
    events = lattice_world(DEGREE)
    world = world_edges(events)
    db = temp_db("budget_%s_%s.db" % (budget, seed))
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = arm_for(budget)(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    for text in events[:12]:
        memory.store(text, event_type="event", source="seed:bootstrap")
    theories, hypotheses = [], []
    stable_final = coverage = precision = None
    stable_peak = 0
    coverage_peak = 0.0
    false_assertions = 0
    try:
        for cycle in range(cycles):
            _feed(memory, events, cycle)
            service.run_sleep_cycle()
            stable = _stable(service)
            hit = [edge for edge in stable if edge in world]
            theories.append(int(getattr(service, "theories", 0)))
            hypotheses.append(int(getattr(service, "beliefs", 0)))
            stable_final = len(stable)
            stable_peak = max(stable_peak, len(stable))
            coverage = (len(hit) / len(world)) if world else None
            if coverage is not None:
                coverage_peak = max(coverage_peak, coverage)
            precision = (len(hit) / len(stable)) if stable else None
            false_assertions = len(stable) - len(hit)
    finally:
        memory.close()
        db.unlink(missing_ok=True)
    cap_theories, cap_hypotheses = BUDGETS[budget]
    return {
        "budget": budget,
        "seed": seed,
        "cycles": cycles,
        "degree": DEGREE,
        "realised_degree": len({tgt for src, tgt in world if src == "alpha"}),
        "world_edges": len(world),
        "theories_final": theories[-1] if theories else None,
        "theories_max": max(theories) if theories else 0,
        "hypotheses_final": hypotheses[-1] if hypotheses else None,
        "hypotheses_max": max(hypotheses) if hypotheses else 0,
        "cap_theories": cap_theories,
        "cap_hypotheses": cap_hypotheses,
        "cap_bound_theories": bool(theories) and max(theories) >= cap_theories,
        "cap_bound_hypotheses": bool(hypotheses) and max(hypotheses) >= cap_hypotheses,
        "stable_final": stable_final,
        "stable_peak": stable_peak,
        "coverage_peak": round(coverage_peak, 4),
        "precision": precision,
        "coverage": coverage,
        "false_assertions": false_assertions,
    }


def _path(budget: str, seed: int) -> Path:
    return PARTS / ("cell_%s_s%d.json" % (budget, seed))


def run(seeds: list[int]) -> int:
    PARTS.mkdir(parents=True, exist_ok=True)
    for budget in BUDGETS:
        for seed in seeds:
            path = _path(budget, seed)
            if path.exists():
                print("cached", path.name)
                continue
            row = cell(budget, seed)
            path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            print(
                "%-8s s%d  theories=%3d hypotheses=%3d stable=%3d coverage=%s"
                % (
                    budget,
                    seed,
                    row["theories_max"],
                    row["hypotheses_max"],
                    row["stable_final"],
                    row["coverage"],
                )
            )
    return 0


def load_cells() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(PARTS.glob("cell_*.json"))]


def analyse(rows: list[dict]) -> dict:
    findings, failures = [], []
    by: dict[str, list[dict]] = {}
    for row in rows:
        by.setdefault(row["budget"], []).append(row)

    summary = {}
    for name, (cap_t, cap_h) in BUDGETS.items():
        cells = by.get(name, [])
        finals = [c["coverage"] for c in cells if c["coverage"] is not None]
        peaks = [c["coverage_peak"] for c in cells if c.get("coverage_peak") is not None]
        summary[name] = {
            "caps": [cap_t, cap_h],
            "cells": len(cells),
            "median_final_coverage": round(statistics.median(finals), 4) if finals else None,
            "final_coverage_range": [round(min(finals), 4), round(max(finals), 4)] if finals else None,
            "median_peak_coverage": round(statistics.median(peaks), 4) if peaks else None,
            "peak_coverage_range": [round(min(peaks), 4), round(max(peaks), 4)] if peaks else None,
            "median_stable": round(statistics.median([c["stable_final"] for c in cells]), 1) if cells else None,
            "max_stable": max((c["stable_peak"] for c in cells), default=None),
            "theories_max": max((c["theories_max"] for c in cells), default=None),
            "hypotheses_max": max((c["hypotheses_max"] for c in cells), default=None),
            "cap_bound_theories": any(c["cap_bound_theories"] for c in cells),
            "cap_bound_hypotheses": any(c["cap_bound_hypotheses"] for c in cells),
        }

    for name in BUDGETS:
        if len(by.get(name, [])) < SEED_COUNT:
            failures.append("%s has %d of %d cells" % (name, len(by.get(name, [])), SEED_COUNT))
    for row in rows:
        if row.get("realised_degree") != DEGREE:
            failures.append(
                "seed %s (%s) realised degree %r, not %d"
                % (row.get("seed"), row.get("budget"), row.get("realised_degree"), DEGREE)
            )
        if row.get("coverage") is None:
            failures.append(
                "seed %s (%s) formed no stable edge in its final cycle, so coverage is not measurable"
                % (row.get("seed"), row.get("budget"))
            )
    # Rule 22 corollary: a lifted cap that never let a larger structure form is not
    # a lifted cap, and the contrast would be an unrun experiment.
    shipped_t = summary["shipped"]["theories_max"] or 0
    lifted_t = summary["lifted"]["theories_max"] or 0
    if lifted_t < shipped_t:
        failures.append(
            "the lifted budget produced fewer theories than the shipped one (%d vs %d)"
            % (lifted_t, shipped_t)
        )

    shipped_peak = summary["shipped"]["median_peak_coverage"]
    lifted_peak = summary["lifted"]["median_peak_coverage"]
    finals = [summary[name]["median_final_coverage"] for name in BUDGETS]
    stable_anywhere = max((summary[name]["max_stable"] or 0) for name in BUDGETS)
    if shipped_peak is None or lifted_peak is None:
        verdict = "NOT MEASURABLE"
        next_bar = None
    elif stable_anywhere == 0:
        verdict = "NO_STABLE_EDGES"
        next_bar = shipped_peak
    elif lifted_peak - shipped_peak > TOLERANCE:
        verdict = "BUDGET_BOUND"
        next_bar = shipped_peak
    elif shipped_peak > 0 and all(final is not None and final == 0 for final in finals):
        # Structure forms and then dies: the reachable ceiling is a peak, and the
        # final-cycle endpoint is a decay measurement, not a coverage measurement.
        verdict = "DECAY_DOMINATED"
        next_bar = shipped_peak
    elif all(
        abs(summary[name]["median_peak_coverage"] - shipped_peak) <= 0.001 for name in BUDGETS
    ) and not any(summary[name]["cap_bound_theories"] for name in BUDGETS):
        verdict = "AXIS_DEAD"
        next_bar = shipped_peak
    else:
        verdict = "WORLD_BOUND"
        next_bar = shipped_peak

    for name in BUDGETS:
        entry = summary[name]
        findings.append(
            "%s (caps %d/%d): median peak coverage %s, median final coverage %s over %d cells, "
            "stable edge peak %s, theories max %s, hypotheses max %s, theory cap bound %s"
            % (
                name, entry["caps"][0], entry["caps"][1], entry["median_peak_coverage"],
                entry["median_final_coverage"], entry["cells"], entry["max_stable"],
                entry["theories_max"], entry["hypotheses_max"], entry["cap_bound_theories"],
            )
        )

    shipped_final = summary["shipped"]["median_final_coverage"]
    return {
        "date": date.today().isoformat(),
        "degree": DEGREE,
        "cycles": CYCLES,
        "seeds": sorted({r["seed"] for r in rows}),
        "cells": len(rows),
        "tolerance": TOLERANCE,
        "by_budget": summary,
        "max_stable_edge_any_cell": stable_anywhere,
        "peak_ceiling_at_shipped_budget": shipped_peak,
        "peak_ceiling_if_budget_lifted": lifted_peak,
        "final_cycle_coverage_at_shipped_budget": shipped_final,
        "budget_gap": (
            round(lifted_peak - shipped_peak, 4)
            if shipped_peak is not None and lifted_peak is not None
            else None
        ),
        "next_bar": next_bar,
        "next_bar_endpoint": (
            "a peak within the %d-cycle run; the final-cycle ceiling is %s"
            % (CYCLES, shipped_final)
        ),
        "verdict": verdict,
        "findings": findings,
        "failures": failures,
    }


def render(record: dict) -> str:
    by = record["by_budget"]
    lines = [
        "# The theory budget's coverage ceiling on a degree-12 hub",
        "",
        "**Generated from `docs/theory_budget_ceiling.json`. Do not edit this file.** Rebuild with",
        "`python -m benchmarks.theory_budget_ceiling --measure`; `--check` validates without writing.",
        "",
        "## What was asked",
        "",
        "The degree-12 coverage floor of 0.50 was fixed before the engine had been measured at that",
        "degree, and the shipped engine reported 0.40 on a build that was later reverted. A failed bar",
        "is not evidence that the bar was wrong, so this run measures the ceiling the next bar may be",
        "set from: how much of a degree-12 hub's world a fixed theory budget can actually cover, at",
        "the shipped budget and at two larger ones so the ceiling can be attributed.",
        "",
        "## What was run",
        "",
        "| Item | Value |",
        "| --- | --- |",
        "| World | `lattice_stream` on six triangles sharing hub `alpha`, the matrix's generator |",
        "| Degree | %d, measured from each cell's own edge set |" % record["degree"],
        "| Edges per world | 60 |",
        "| Cycles | %d per cell |" % record["cycles"],
        "| Seeds | %s |" % ", ".join(str(s) for s in record["seeds"]),
        "| Cells | %d |" % record["cells"],
        "| Engine | pinned 0.13.0, unchanged |",
        "",
        "## What each budget reached",
        "",
        "| Budget | caps (theories/hypotheses) | median peak coverage | peak range | median final coverage | final stable edges | theories max | hypotheses max | theory cap bound |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name in ("shipped", "doubled", "lifted"):
        entry = by[name]
        lines.append(
            "| %s | %d / %d | %s | %s | %s | %s | %s | %s | %s |"
            % (
                name,
                entry["caps"][0],
                entry["caps"][1],
                entry["median_peak_coverage"],
                entry["peak_coverage_range"],
                entry["median_final_coverage"],
                entry["median_stable"],
                entry["theories_max"],
                entry["hypotheses_max"],
                entry["cap_bound_theories"],
            )
        )
    lines += [
        "",
        "## The ceiling",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        "| Peak coverage at the shipped budget (8 theories / 15 hypotheses) | %s |" % record["peak_ceiling_at_shipped_budget"],
        "| Peak coverage with the budget lifted (64 / 128) | %s |" % record["peak_ceiling_if_budget_lifted"],
        "| Difference in peak coverage | %s |" % record["budget_gap"],
        "| Final-cycle coverage at the shipped budget | %s |" % record["final_cycle_coverage_at_shipped_budget"],
        "| Largest stable-edge count in any cell, any budget | %s |" % record["max_stable_edge_any_cell"],
        "| Verdict | **%s** |" % record["verdict"],
        "| Bar the next protocol may set | %s |" % record["next_bar"],
        "| Endpoint that bar names | %s |" % record["next_bar_endpoint"],
        "",
        "## What this establishes",
        "",
        CROWN.get(record["verdict"], ""),
        "",
        "## What it does not establish",
        "",
        "- **Three seeds, one stimulus family, 300 cycles.** It places a ceiling, not an interval;",
        "  the range above is the spread of three draws, not a confidence interval.",
        "- **Coverage is structural.** It counts world edges the stable predictions assert; it does",
        "  not measure whether any belief predicts the next tag.",
        "- **The lifted arm is a counterfactual about the budget, not a proposal to raise it.** It is",
        "  run in-process and never shipped.",
        "- **Both endpoints are reported because they differ.** A peak inside the run and the value at",
        "  its end are different quantities, and quoting one as the other is how a decay becomes a",
        "  coverage claim.",
        "",
    ]
    if record["failures"]:
        lines += ["## Gate failures", ""]
        lines += ["- " + failure for failure in record["failures"]]
        lines.append("")
    return "\n".join(lines)


CROWN = {
    "DECAY_DOMINATED": (
        "The budget is not the constraint. Peak coverage is identical at every budget tested, so a "
        "larger theory budget buys no reach on this world; what ends the coverage is decay, and the "
        "final-cycle endpoint is zero at every budget. The reachable ceiling is the peak column, and "
        "the next bar must name its endpoint: a bar on the final cycle cannot exceed zero on this "
        "build, while a bar on a peak inside the run can be set from the measured peak without "
        "implying a budget change."
    ),
    "NO_STABLE_EDGES": (
        "Nothing was reachable to cover. No prediction reached the strength filter at degree 12 in "
        "any cell, at any budget, in any cycle, so the numerator is empty while the world's edges "
        "are present: this is a measured zero with a named cause, not a missing denominator and not "
        "a budget ceiling. The theory budget never bound, so raising it cannot raise coverage here, "
        "and no coverage bar above zero is attainable on this build until the strength rule admits "
        "a degree-12 edge."
    ),
    "BUDGET_BOUND": (
        "The budget is the binding constraint: raising it moves peak coverage beyond the tolerance, "
        "so the shipped ceiling is the budget's ceiling. The next bar may not exceed the shipped "
        "column, and the decision this licenses is about the budget, not about the world."
    ),
    "WORLD_BOUND": (
        "The budget is not the binding constraint: raising it does not move peak coverage beyond the "
        "tolerance, so the shipped ceiling is a property of this world and this engine. The next bar "
        "may be set from the shipped column without implying a budget change."
    ),
    "AXIS_DEAD": (
        "Every budget reached the same coverage and no cap bound, so this run cannot separate the "
        "budget from the world. That is a measurement defect and is reported as one (rule 13c), not "
        "read as a ceiling."
    ),
    "NOT MEASURABLE": (
        "At least one budget produced no measurable coverage, so no ceiling is stated. The zero "
        "denominators are named above rather than scored."
    ),
}


def problems(record: dict) -> list[str]:
    found = []
    if record.get("degree") != DEGREE:
        found.append("the record is not a degree-%d measurement" % DEGREE)
    if record.get("cells") != SEED_COUNT * len(BUDGETS):
        found.append(
            "the record covers %s cells, not %d" % (record.get("cells"), SEED_COUNT * len(BUDGETS))
        )
    if not record.get("seeds") or len(record["seeds"]) < SEED_COUNT:
        found.append("fewer than %d seeds are recorded" % SEED_COUNT)
    if record.get("failures"):
        found.append("the record carries gate failures: %s" % "; ".join(record["failures"]))
    peak = record.get("peak_ceiling_at_shipped_budget")
    lifted = record.get("peak_ceiling_if_budget_lifted")
    if peak is not None and lifted is not None:
        if record["verdict"] == "BUDGET_BOUND" and lifted - peak <= record["tolerance"]:
            found.append("the verdict says BUDGET_BOUND but the measured gap is within the tolerance")
        if record["verdict"] == "DECAY_DOMINATED" and (
            record.get("final_cycle_coverage_at_shipped_budget") not in (0.0, 0)
        ):
            found.append("the verdict says DECAY_DOMINATED but the final cycle is not zero")
        if record["next_bar"] is not None and record["next_bar"] > peak + 1e-9:
            found.append("the recommended bar exceeds the measured peak ceiling")
    if not record.get("next_bar_endpoint"):
        found.append("the recommended bar names no endpoint")
    if not DOC.exists():
        found.append("the result document does not exist")
    elif DOC.read_text(encoding="utf-8") != render(record):
        found.append("%s is stale; rebuild with python -m benchmarks.theory_budget_ceiling" % DOC.name)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measure", action="store_true", help="run any missing cells, then write the record")
    parser.add_argument("--reuse", action="store_true", help="summarise the existing cells without running")
    parser.add_argument("--check", action="store_true", help="validate the record and the page without writing")
    parser.add_argument("--seeds", type=int, nargs="*", default=None)
    args = parser.parse_args(argv)

    if args.check:
        found = problems(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("theory budget ceiling: %s" % json.loads(ARTIFACT.read_text(encoding="utf-8"))["verdict"])
        return 0

    if args.measure or args.reuse:
        seeds = args.seeds or ceiling_seeds()
        if args.measure:
            run(seeds)
        record = analyse(load_cells())
        ARTIFACT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        DOC.write_text(render(record), encoding="utf-8")
        for line in record["findings"]:
            print("finding:", line)
        for line in record["failures"]:
            print("FAIL:", line)
        print("peak ceiling at shipped budget:", record["peak_ceiling_at_shipped_budget"])
        print("verdict:", record["verdict"], "| next bar:", record["next_bar"])
        return 0 if not record["failures"] else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
