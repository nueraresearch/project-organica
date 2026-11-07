"""The A2 density block's analysis path: gates, one criterion, a descriptive slope, a verdict.

Frozen before the run. It reads the cells a runner writes and nothing else, so no criterion
can be re-chosen after a result is seen. Every gate can fail, and each failure is reported
as the gate rather than as a verdict.

The judged criterion is the **sparse-end level** on precision at the frozen cap: the pilot
measured the dense end to be pinned by the pool's composition (control 17 of 20, treated
20 of 20, on every seed), so an interaction criterion there would be arithmetic. The
interaction is still computed, with its interval and its per-seed values, and the decision
table places it — but it is a description, not a criterion.

    ./.venv/bin/python -m benchmarks.score_density_interaction_a2 \
        --results docs/density_interaction_a2_run.json \
        --out docs/density_interaction_a2_result.json

No engine runs here, and the module imports nothing from `organica`.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "density_interaction_a2_prereg.json"

ARMS = ("control", "intra_cell_excluded")
SCHEMES = ("primary", "sensitivity")
DENSITIES = (0.1, 0.2, 0.4, 0.6, 0.8)
PRIMARY_SCHEME = "primary"
PRIMARY_CAP = 20
SPARSE = 0.1
DENSE = 0.8
TOL = 1e-9

#: G0's floor as a share of the seed block: 14 of 16.
G0_SHARE = 0.875


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
    required_g0 = max(7, int(round(G0_SHARE * len(seeds))))
    out: dict = {}

    # Compare the selected SETS. A reordering of the same rows is not liveness.
    differ = sum(1 for seed in seeds
                 if set(index[(PRIMARY_SCHEME, "control", PRIMARY_CAP, SPARSE,
                               seed)]["selected"])
                 != set(index[(PRIMARY_SCHEME, "intra_cell_excluded", PRIMARY_CAP,
                               SPARSE, seed)]["selected"]))
    out["G0_liveness"] = {"seeds_where_arms_differ": differ, "of": len(seeds),
                          "required": required_g0, "passed": differ >= required_g0,
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
    seed = int(record["seeds"]["bootstrap"])
    reps = int(crit["bootstrap_reps"])
    level = float(crit["interval"])

    sparse = _delta(cells, PRIMARY_SCHEME, PRIMARY_CAP, SPARSE)
    dense = _delta(cells, PRIMARY_SCHEME, PRIMARY_CAP, DENSE)
    interaction = {s: dense[s] - sparse[s] for s in sparse}

    mean = _mean(sparse.values())
    interval = _interval(list(sparse.values()), seed, reps, level)
    positive = sum(1 for value in sparse.values() if value > 0)
    required = int(crit["sign_test"]["required"])
    c1 = (mean >= float(crit["sparse_bar"]) and interval[0] > 0
          and positive >= required)

    interaction_mean = _mean(interaction.values())
    interaction_interval = _interval(list(interaction.values()), seed + 1, reps, level)

    sensitivity = _delta(cells, "sensitivity", PRIMARY_CAP, SPARSE)
    sensitivity_mean = _mean(sensitivity.values())
    sensitivity_positive = sum(1 for value in sensitivity.values() if value > 0)

    profile = {}
    for rho in DENSITIES:
        row = {}
        for scheme in SCHEMES:
            delta = _delta(cells, scheme, PRIMARY_CAP, rho)
            index = _index(cells)
            seeds = sorted(delta)
            row[scheme] = {
                "delta_precision_mean": round(_mean(delta.values()), 6),
                "seeds_positive": sum(1 for v in delta.values() if v > 0),
                "control_precision_mean": round(_mean(
                    index[(scheme, "control", PRIMARY_CAP, round(rho, 6), s)]["precision"]
                    for s in seeds), 6),
                "treated_precision_mean": round(_mean(
                    index[(scheme, "intra_cell_excluded", PRIMARY_CAP, round(rho, 6),
                           s)]["precision"] for s in seeds), 6),
            }
        profile["%.1f" % rho] = row

    return {
        "C1_sparse_level": {
            "mean": round(mean, 6), "interval": interval,
            "interval_width": round(interval[1] - interval[0], 6),
            "bar": crit["sparse_bar"], "seeds_positive": positive,
            "of": len(sparse), "required": required, "passed": bool(c1)},
        "descriptive_interaction": {
            "judged": False,
            "mean": round(interaction_mean, 6), "interval": interaction_interval,
            "interval_width": round(interaction_interval[1] - interaction_interval[0], 6),
            "dense_minus_sparse_per_seed": {str(s): round(v, 6)
                                            for s, v in sorted(interaction.items())},
            "why_not_judged": crit["C2"]},
        "exposure": {
            "sensitivity_sparse_mean": round(sensitivity_mean, 6),
            "seeds_positive": sensitivity_positive, "of": len(sensitivity),
            "holds": bool(sensitivity_mean > 0
                          and abs(sensitivity_mean - mean) < 1.0)},
        "profile": profile,
    }


def verdict(gate_report: dict, criterion_report: dict, record: dict | None = None) -> dict:
    """Every pole of the decision table, read from the frozen numbers."""
    record = record or prereg()
    if not gate_report["all_passed"]:
        failed = sorted(k for k, v in gate_report.items()
                        if isinstance(v, dict) and v.get("passed") is False)
        return {"verdict": "VOID", "failed_gates": failed,
                "reading": "a gate failed; no criterion is read",
                "decision": "none; fix the harness"}
    c1 = criterion_report["C1_sparse_level"]
    slope = criterion_report["descriptive_interaction"]
    exposure = criterion_report["exposure"]

    if c1["passed"] and not exposure["holds"]:
        return {"verdict": "EXPOSURE ARTIFACT",
                "reading": "the sparse-end level does not survive the other exposure scheme",
                "decision": "adopt nothing; report both schemes"}

    if c1["passed"]:
        if slope["interval"][0] > 0:
            return {"verdict": "EXCLUSION PAYS AT SPARSE DENSITY AND GROWS WITH DENSITY",
                    "reading": "the exclusion buys precision at the sparse end, and the "
                               "dense-minus-sparse difference lies above zero",
                    "decision": "adopt intra-cell exclusion as an allocation change behind "
                                "a recorded owner decision; no behavioural claim"}
        if slope["interval"][1] < 0:
            return {"verdict": "EXCLUSION PAYS MORE AT SPARSE THAN DENSE",
                    "reading": "the exclusion buys precision where the world is sparse, and "
                               "less where it is dense",
                    "decision": "adopt at the sparse end; retire the density interaction as "
                                "a moderator of this bottleneck"}
        return {"verdict": "EXCLUSION PAYS AT SPARSE DENSITY; DENSITY SLOPE NOT IDENTIFIED",
                "reading": "the exclusion buys precision where the world is sparse, and the "
                           "block cannot place how that changes with density",
                "decision": "adopt at the sparse end; move the density question to the "
                            "candidate space, since the dense end is pinned by composition"}

    if c1["interval_width"] > float(record["criteria"]["underpowered_width"]):
        return {"verdict": "UNDERPOWERED",
                "reading": "the interval cannot place the sparse-end level; absence is not "
                           "established",
                "decision": "neither pole; a new block on fresh seeds may be registered, "
                            "never a re-read"}
    return {"verdict": "EXCLUSION DOES NOT PAY AT SPARSE DENSITY",
            "reading": "removing the ineligible class does not buy precision at the budget "
                       "where Gate 13's observation lives",
            "decision": "retire budget competition as the lever at this cap and world "
                        "family; move the line to the candidate space"}


def score(payload: dict, record: dict | None = None) -> dict:
    record = record or prereg()
    cells = payload["cells"]
    validate(cells, record)
    gate_report = gates(cells, payload["identity"], record)
    criterion_report = criteria(cells, record) if gate_report["all_passed"] else {}
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
    parser.add_argument("--results", default="docs/density_interaction_a2_run.json")
    parser.add_argument("--out", default="docs/density_interaction_a2_result.json")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.results).read_text(encoding="utf-8"))
    result = score(payload)
    Path(args.out).write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(result["decision"]["verdict"], "->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
