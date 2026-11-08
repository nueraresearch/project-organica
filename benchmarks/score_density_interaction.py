"""The density interaction's analysis path: gates, criteria, verdict, decision.

Frozen before the run. It reads the cells a runner writes and nothing else, so no
criterion can be re-chosen after a result is seen. Every gate can fail, and each failure
is reported as the gate rather than as a verdict.

The criterion is the **interaction** on precision at the frozen cap: coverage divides by
|W|, which grows eightfold across the ladder, so a coverage difference is forced by
arithmetic and cannot test anything. Precision at a fixed cap is budget-normalised, and
its shape is a fact about the ranking.

    ./.venv/bin/python -m benchmarks.score_density_interaction \\
        --results docs/density_interaction_run.json \\
        --out docs/density_interaction_result.json

No engine runs here, and the module imports nothing from `organica`.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "density_interaction_prereg.json"

ARMS = ("control", "intra_cell_excluded")
SCHEMES = ("primary", "sensitivity")
DENSITIES = (0.1, 0.2, 0.4, 0.6, 0.8)
CAPS = (20, 40)
PRIMARY_SCHEME = "primary"
PRIMARY_CAP = 20
SPARSE = 0.1
DENSE = 0.8
TOL = 1e-9


def prereg(path: Path = PREREG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_cells(record: dict | None = None) -> int:
    record = record or prereg()
    design = record["design"]
    return (len(design["arms"]) * len(design["caps"]) * len(design["densities"])
            * len(design["seeds"]) * len(design["schemes"]))


def _index(cells: list[dict]) -> dict[tuple, dict]:
    index: dict[tuple, dict] = {}
    for cell in cells:
        key = (cell["scheme"], cell["arm"], int(cell["cap"]),
               round(float(cell["rho_world"]), 6), int(cell["seed"]))
        if key in index:
            raise ValueError("duplicate cell %r" % (key,))
        index[key] = cell
    return index


def validate(cells: list[dict], record: dict) -> None:
    """The cell set must be exactly the registered grid; a missing cell is not a null."""
    design = record["design"]
    wanted = {(scheme, arm, int(cap), round(float(rho), 6), int(seed))
              for scheme in design["schemes"] for arm in design["arms"]
              for cap in design["caps"] for rho in design["densities"]
              for seed in design["seeds"]}
    seen = _index(cells)
    missing = sorted(wanted - set(seen))
    extra = sorted(set(seen) - wanted)
    if missing or extra:
        raise ValueError("cell set is not the pre-registered grid: %d missing, %d extra; "
                         "missing=%r extra=%r" % (len(missing), len(extra),
                                                  missing[:4], extra[:4]))


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values)


def _interval(samples: list[float], seed: int, reps: int, level: float) -> list[float]:
    rng = random.Random(seed)
    n = len(samples)
    means = sorted(_mean(samples[rng.randrange(n)] for _ in range(n)) for _ in range(reps))
    tail = (1.0 - level) / 2.0
    lo = means[min(int(tail * reps), reps - 1)]
    hi = means[min(int((1 - tail) * reps), reps - 1)]
    return [round(lo, 6), round(hi, 6)]


def _delta(cells: list[dict], scheme: str, cap: int, rho: float) -> dict[int, float]:
    """Per-seed Delta(rho) = treated precision - control precision at a fixed cap."""
    index = _index(cells)
    seeds = sorted({k[4] for k in index})
    out = {}
    for seed in seeds:
        control = index[(scheme, "control", cap, round(rho, 6), seed)]
        treated = index[(scheme, "intra_cell_excluded", cap, round(rho, 6), seed)]
        if treated["precision"] is None or control["precision"] is None:
            raise ValueError("a cell has no precision; the block is not measurable")
        out[seed] = treated["precision"] - control["precision"]
    return out


def gates(cells: list[dict], identity: dict, record: dict | None = None) -> dict:
    """Comparability gates. Any failure voids the block and no criterion is read."""
    record = record or prereg()
    seeds = [int(s) for s in record["design"]["seeds"]]
    index = _index(cells)
    out: dict = {}

    # Compare the selected SETS. Comparing the stored lists would count a reordering of
    # the same rows as liveness, so a treatment that changed nothing but the tie order
    # could pass the gate.
    differ = sum(1 for seed in seeds
                 if set(index[(PRIMARY_SCHEME, "control", PRIMARY_CAP, SPARSE,
                               seed)]["selected"])
                 != set(index[(PRIMARY_SCHEME, "intra_cell_excluded", PRIMARY_CAP,
                               SPARSE, seed)]["selected"]))
    out["G0_liveness"] = {"seeds_where_arms_differ": differ, "of": len(seeds),
                          "required": 7, "passed": differ >= 7,
                          "comparison": "selected sets, not their order"}

    smallest = min(float(c["presence"]) for c in cells)
    out["G1_presence_ceiling"] = {"minimum": smallest, "required": 1.0,
                                  "passed": abs(smallest - 1.0) <= TOL}

    bad = []
    for cell in cells:
        asserted, covered = cell.get("asserted"), cell.get("covered")
        if not asserted or covered is None:
            bad.append([cell["arm"], cell["cap"], cell["rho_world"], cell["seed"],
                        "no counts"])
            continue
        precision = float(cell["precision"])
        if covered < 0 or covered > asserted:
            bad.append([cell["arm"], cell["cap"], cell["rho_world"], cell["seed"],
                        "covered/asserted"])
        elif abs(precision - covered / asserted) > 1e-6:
            bad.append([cell["arm"], cell["cap"], cell["rho_world"], cell["seed"],
                        "precision"])
        elif not 0.0 <= precision <= 1.0:
            bad.append([cell["arm"], cell["cap"], cell["rho_world"], cell["seed"], "range"])
        elif cell.get("rho_rank") is None:
            bad.append([cell["arm"], cell["cap"], cell["rho_world"], cell["seed"],
                        "no rho_rank"])
    out["G2_arithmetic"] = {"cells_failing": len(bad), "example": bad[:2],
                            "passed": not bad}

    axis = {}
    for scheme in SCHEMES:
        low = _mean(index[(scheme, arm, PRIMARY_CAP, SPARSE, seed)]["rho_rank"]
                    for arm in ARMS for seed in seeds)
        high = _mean(index[(scheme, arm, PRIMARY_CAP, DENSE, seed)]["rho_rank"]
                     for arm in ARMS for seed in seeds)
        axis[scheme] = {"at_sparse": round(low, 4), "at_dense": round(high, 4),
                        "passed": high > low}
    out["G3_axis_live"] = dict(axis)
    out["G3_axis_live"]["passed"] = all(axis[s]["passed"] for s in SCHEMES)

    ceiling = float(record["gates"].get("control_ceiling", 0.50))
    control_sparse = _mean(index[(PRIMARY_SCHEME, "control", PRIMARY_CAP, SPARSE,
                                  seed)]["precision"] for seed in seeds)
    out["G4_control_reproduces_gate13"] = {
        "control_precision_at_sparse": round(control_sparse, 6),
        "must_not_exceed": ceiling, "passed": control_sparse <= ceiling}

    out["G5_identity_where_it_must_hold"] = {
        "arms_identical": bool(identity.get("arms_identical")),
        "delta": identity.get("delta"),
        "passed": bool(identity.get("arms_identical"))
        and abs(float(identity.get("delta", 1.0))) <= TOL}

    violations = []
    for cell in cells:
        if cell["arm"] != "control":
            continue
        treated = index[(cell["scheme"], "intra_cell_excluded", int(cell["cap"]),
                         round(float(cell["rho_world"]), 6), int(cell["seed"]))]
        if treated["coverage"] < cell["coverage"] - TOL:
            violations.append([cell["seed"], cell["rho_world"], cell["scheme"],
                               cell["cap"], cell["coverage"], treated["coverage"]])
    out["G6_treatment_does_not_lose_coverage"] = {
        "violations": violations[:3], "count": len(violations),
        "passed": not violations}

    out["all_passed"] = all(v.get("passed") for v in out.values() if isinstance(v, dict))
    return out


def criteria(cells: list[dict], record: dict | None = None) -> dict:
    record = record or prereg()
    crit = record["criteria"]
    seeds = int(record["seeds"]["bootstrap"])
    reps = int(crit["bootstrap_reps"])
    level = float(crit["interval"])

    sparse = _delta(cells, PRIMARY_SCHEME, PRIMARY_CAP, SPARSE)
    dense = _delta(cells, PRIMARY_SCHEME, PRIMARY_CAP, DENSE)
    interaction = {seed: dense[seed] - sparse[seed] for seed in sparse}
    mean = _mean(interaction.values())
    interval = _interval(list(interaction.values()), seeds, reps, level)
    c1 = mean >= float(crit["interaction_bar"]) and interval[0] > 0

    level_mean = _mean(dense.values())
    level_interval = _interval(list(dense.values()), seeds, reps, level)
    positive = sum(1 for value in dense.values() if value > 0)
    c2 = (level_mean >= float(crit["level_bar"]) and level_interval[0] > 0
          and positive >= int(crit["sign_test"]["required"]))

    sensitivity = _delta(cells, "sensitivity", PRIMARY_CAP, DENSE)
    sensitivity_sparse = _delta(cells, "sensitivity", PRIMARY_CAP, SPARSE)
    sensitivity_interaction = _mean(sensitivity[seed] - sensitivity_sparse[seed]
                                    for seed in sensitivity)

    profile = {}
    for rho in DENSITIES:
        row = {}
        for scheme in SCHEMES:
            delta = _delta(cells, scheme, PRIMARY_CAP, rho)
            row[scheme] = {"delta_precision_mean": round(_mean(delta.values()), 6),
                           "seeds_positive": sum(1 for v in delta.values() if v > 0)}
        profile["%.1f" % rho] = row

    return {
        "C1_interaction": {
            "mean": round(mean, 6), "interval": interval,
            "interval_width": round(interval[1] - interval[0], 6),
            "bar": crit["interaction_bar"], "passed": bool(c1)},
        "C2_level_at_dense": {
            "mean": round(level_mean, 6), "interval": level_interval,
            "bar": crit["level_bar"], "seeds_positive": positive,
            "of": len(dense), "passed": bool(c2)},
        "exposure": {"sensitivity_interaction_mean": round(sensitivity_interaction, 6),
                     "agrees_in_sign": sensitivity_interaction > 0},
        "profile": profile,
    }


def verdict(gate_report: dict, criterion_report: dict, record: dict | None = None) -> dict:
    record = record or prereg()
    if not gate_report["all_passed"]:
        failed = sorted(k for k, v in gate_report.items()
                        if isinstance(v, dict) and v.get("passed") is False)
        return {"verdict": "VOID", "failed_gates": failed,
                "reading": "a gate failed; no criterion is read"}
    c1 = criterion_report["C1_interaction"]
    c2 = criterion_report["C2_level_at_dense"]
    if c1["passed"] and c2["passed"]:
        if criterion_report["exposure"]["agrees_in_sign"]:
            return {"verdict": "DENSITY INTERACTION SUPPORTED",
                    "reading": "the exclusion spends a larger share of the budget on "
                               "world edges as the world densifies, and the exposure "
                               "check agrees in direction"}
        return {"verdict": "EXPOSURE ARTIFACT",
                "reading": "the direction reverses under the other exposure scheme, "
                           "which is the design record's own confound rule"}
    if c1["interval"][1] <= 0:
        return {"verdict": "ADVANTAGE FALLS WITH DENSITY",
                "reading": "the benefit is smaller at the dense end than at the sparse "
                           "end, so budget competition is not what is being measured"}
    if not c1["passed"] and not c2["passed"]:
        if c1["interval_width"] > float(record["criteria"]["underpowered_width"]):
            return {"verdict": "UNDERPOWERED",
                    "reading": "the interval cannot place the interaction; absence of an "
                               "effect is not established"}
        return {"verdict": "FLAT - GEOMETRY NOT THE LEVER",
                "reading": "the exclusion's value does not vary with density in this "
                           "world family"}
    return {"verdict": "UNDERPOWERED",
            "reading": "one criterion passed and the other failed; the conjunction is "
                       "not met and the set is not scored piecewise"}


def score(payload: dict, record: dict | None = None) -> dict:
    record = record or prereg()
    cells = payload["cells"]
    validate(cells, record)
    gate_report = gates(cells, payload["identity"], record)
    criterion_report = (criteria(cells, record) if gate_report["all_passed"] else {})
    return {
        "prereg": record["prereg"],
        "cells": len(cells),
        "gates": gate_report,
        "criteria": criterion_report,
        "decision": verdict(gate_report, criterion_report, record),
        "not_evidence": record["not_evidence"],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="docs/density_interaction_run.json")
    parser.add_argument("--out", default="docs/density_interaction_result.json")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.results).read_text(encoding="utf-8"))
    result = score(payload)
    Path(args.out).write_text(json.dumps(engine_stamp.stamp(result), indent=1) + "\n", encoding="utf-8")
    print(result["decision"]["verdict"], "->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
