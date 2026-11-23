"""Frozen analysis for the two-arm admission comparison.

Reads only the cells the runner wrote. Gates first: a failed gate voids the
block and no criterion is read. Then the paired gain at the pre-registered bar,
a precision guard, and a verdict from the decision table committed before the
run. It imports nothing from the engine and runs no cell.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "admission_two_arm_prereg.json"


def prereg(path: Path = PREREG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(cells: list[dict], record: dict) -> None:
    design = record["design"]
    wanted = {(arm, int(seed)) for arm in design["arms"] for seed in design["seeds"]}
    seen = {(c["arm"], int(c["seed"])) for c in cells}
    if len(seen) != len(cells):
        raise ValueError("duplicate cell")
    if seen != wanted:
        raise ValueError("cell set is not the pre-registered grid: %d missing, %d extra"
                         % (len(wanted - seen), len(seen - wanted)))


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values)


def _interval(samples: list[float], seed: int, record: dict) -> list[float]:
    reps = int(record["criteria"]["bootstrap_reps"])
    level = float(record["criteria"]["interval"])
    rng = random.Random(seed)
    n = len(samples)
    means = sorted(_mean(samples[rng.randrange(n)] for _ in range(n)) for _ in range(reps))
    tail = (1.0 - level) / 2.0
    return [round(means[min(int(tail * reps), reps - 1)], 6),
            round(means[min(int((1 - tail) * reps), reps - 1)], 6)]


def _paired(cells: list[dict], key: str) -> dict[int, float]:
    index = {(c["arm"], int(c["seed"])): c for c in cells}
    return {seed: float(index[("adopted", seed)][key]) - float(index[("reference", seed)][key])
            for seed in sorted({int(c["seed"]) for c in cells})}


def gates(cells: list[dict], payload: dict) -> dict:
    record = prereg()
    seeds = [int(s) for s in record["design"]["seeds"]]
    index = {(c["arm"], int(c["seed"])): c for c in cells}
    out: dict = {}

    differ = sum(1 for s in seeds
                 if index[("reference", s)]["asserted_fingerprint"]
                 != index[("adopted", s)]["asserted_fingerprint"])
    out["G0_liveness"] = {"seeds_where_the_arms_differ": differ, "of": len(seeds),
                          "required": len(seeds) - 1, "passed": differ >= len(seeds) - 1}

    raw = [float(c["raw_temporal_coverage"]) for c in cells]
    out["G1_world_present"] = {"min_raw_temporal_coverage": round(min(raw), 6),
                               "passed": min(raw) >= 1.0 - 1e-9}

    problems = []
    for cell in cells:
        world, covered, asserted = int(cell["world_edges"]), int(cell["covered"]), int(cell["asserted"])
        if covered > asserted:
            problems.append("covered above asserted")
        if world <= 0:
            problems.append("zero denominator")
        elif abs(float(cell["coverage"]) - round(covered / world, 6)) > 1e-6:
            problems.append("coverage is not covered over the world")
        if asserted and abs(float(cell["precision"]) - round(covered / asserted, 6)) > 1e-6:
            problems.append("precision is not covered over asserted")
    out["G2_arithmetic"] = {"problems": problems[:4], "passed": not problems}

    det = payload.get("determinism") or {}
    out["G3_determinism"] = {"matched": bool(det.get("matched")),
                             "passed": bool(det.get("matched"))}

    out["G4_denominator"] = {"min_world_edges": min(int(c["world_edges"]) for c in cells),
                             "passed": min(int(c["world_edges"]) for c in cells) > 0}

    boundary = payload.get("boundary") or {}
    out["G5_boundary"] = {"frozen_files_clean": bool(boundary.get("frozen_files_clean")),
                          "passed": bool(boundary.get("frozen_files_clean"))}

    out["all_passed"] = all(v.get("passed") for v in out.values() if isinstance(v, dict))
    return out


def criteria(cells: list[dict]) -> dict:
    record = prereg()
    crit = record["criteria"]
    gain = _paired(cells, "coverage")
    mean = _mean(gain.values())
    interval = _interval(list(gain.values()), int(record["seeds"]["bootstrap"]), record)
    width = round(interval[1] - interval[0], 6)
    positive = sum(1 for v in gain.values() if v > 0)
    conditions = {"mean_at_or_above_bar": mean >= crit["bar"],
                  "interval_lower_above_zero": interval[0] > 0,
                  "sign_test_met": positive >= int(crit["sign_test"]["required"])}
    adoption = {"mean_paired_gain": round(mean, 6), "interval": interval,
                "interval_width": width, "bar": crit["bar"],
                "seeds_positive": positive, "conditions": conditions,
                "passed": all(conditions.values())}

    precision = _paired(cells, "precision")
    guard = {"mean_paired_precision_difference": round(_mean(precision.values()), 6),
             "bar": crit["guard_bar"],
             "passed": _mean(precision.values()) >= crit["guard_bar"]}

    per_seed = {str(s): {"coverage_gain": round(gain[s], 6),
                         "precision_difference": round(precision[s], 6)}
                for s in sorted(gain)}
    return {"adoption": adoption, "guard": guard, "per_seed": per_seed}


def verdict(gate_report: dict, criterion_report: dict) -> dict:
    if not gate_report["all_passed"]:
        failed = sorted(k for k, v in gate_report.items()
                        if isinstance(v, dict) and v.get("passed") is False)
        return {"verdict": "VOID", "failed_gates": failed, "decision": "neither",
                "reading": "a gate failed; no criterion is read"}
    adoption, guard = criterion_report["adoption"], criterion_report["guard"]
    if adoption["passed"] and guard["passed"]:
        return {"verdict": "ADOPTED ARM GAINS", "decision": "gains",
                "reading": "the adopted admission covers more of the world's edges at the same budget without losing precision"}
    if adoption["passed"]:
        return {"verdict": "PRICED TRADE", "decision": "trade",
                "reading": "coverage rises and precision falls; nothing is claimed as a gain"}
    if adoption["interval_width"] > prereg()["criteria"]["underpowered_width"]:
        return {"verdict": "UNDERPOWERED", "decision": "neither",
                "reading": "the interval cannot place the difference"}
    return {"verdict": "NO GAIN ON THIS LAYER", "decision": "close",
            "reading": "the adopted rule does not cover more of the world here; this layer is closed to this rule"}


def score(payload: dict) -> dict:
    record = prereg()
    validate(payload["cells"], record)
    gate_report = gates(payload["cells"], payload)
    criterion_report = criteria(payload["cells"]) if gate_report["all_passed"] else {}
    return {"prereg": record["prereg"], "cells": len(payload["cells"]),
            "gates": gate_report, "criteria": criterion_report,
            "decision": verdict(gate_report, criterion_report),
            "not_evidence": record["not_evidence"]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="docs/admission_two_arm_run.json")
    parser.add_argument("--out", default="docs/admission_two_arm_result.json")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.results).read_text(encoding="utf-8"))
    result = score(payload)
    Path(args.out).write_text(json.dumps(engine_stamp.stamp(result), indent=1) + "\n", encoding="utf-8")
    print(result["decision"]["verdict"], "->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
