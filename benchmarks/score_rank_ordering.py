"""The ranking experiment's analysis path: gates, criterion, verdict, decision.

Frozen before the run. It reads the cells a runner writes and nothing else, so the
criterion cannot be re-chosen after a result is seen. Every gate can fail, and each
failure is reported as the gate rather than as a verdict.

M1 is the only criterion. M2 was withdrawn by Amendment 4 of the pre-registration: no
endpoint could both vary with density and fail in this world family, so the density
ladder is reported as a characterization (`criteria.density_profile`) and is not scored.

    ./.venv/bin/python -m benchmarks.score_rank_ordering \
        --results docs/rank_ordering_run.json --out docs/rank_ordering_result.json

No engine runs here, and the module imports nothing from `organica`.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "rank_ordering_prereg.json"

ARMS = ("control", "diversity")
CAPS = (20, 40)
DENSITIES = (0.1, 0.2, 0.4, 0.6, 0.8)
MIN_RHO = 0.1
MAX_RHO = 0.8
PRIMARY_CAP = 20
SIGN_TEST_MIN = 7          # of 8 seeds
BOOTSTRAP_REPS = 4000
INTERVAL = 0.95
TOL = 1e-9


def prereg(path: Path = PREREG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_cells(record: dict | None = None) -> int:
    record = record or prereg()
    design = record["design"]
    return (len(design["arms"]) * len(design["caps"])
            * len(design["densities"]) * len(design["seeds"]))


def _index(cells: list[dict]) -> dict[tuple, dict]:
    index: dict[tuple, dict] = {}
    for cell in cells:
        key = (cell["arm"], int(cell["cap"]), round(float(cell["rho_world"]), 6),
               int(cell["seed"]))
        if key in index:
            raise ValueError("duplicate cell %r" % (key,))
        index[key] = cell
    return index


def validate(cells: list[dict], record: dict) -> None:
    """The cell set must be exactly the pre-registered grid; a missing cell is not a null."""
    design = record["design"]
    wanted = {(arm, int(cap), round(float(rho), 6), int(seed))
              for arm in design["arms"] for cap in design["caps"]
              for rho in design["densities"] for seed in design["seeds"]}
    seen = _index(cells)
    missing = sorted(wanted - set(seen))
    extra = sorted(set(seen) - wanted)
    if missing or extra:
        raise ValueError("cell set is not the pre-registered grid: %d missing, %d extra; "
                         "missing=%r extra=%r" % (len(missing), len(extra),
                                                  missing[:4], extra[:4]))


def _delta(cells: list[dict], cap: int, rho: float) -> dict[int, float]:
    index = _index(cells)
    seeds = sorted({k[3] for k in index})
    out = {}
    for seed in seeds:
        control = index[("control", cap, round(rho, 6), seed)]["coverage"]
        treated = index[("diversity", cap, round(rho, 6), seed)]["coverage"]
        out[seed] = treated - control
    return out


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values)


def _interval(samples: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    n = len(samples)
    means = sorted(_mean(samples[rng.randrange(n)] for _ in range(n))
                   for _ in range(BOOTSTRAP_REPS))
    tail = (1.0 - INTERVAL) / 2.0
    lo = means[min(int(tail * BOOTSTRAP_REPS), BOOTSTRAP_REPS - 1)]
    hi = means[min(int((1 - tail) * BOOTSTRAP_REPS), BOOTSTRAP_REPS - 1)]
    return [round(lo, 6), round(hi, 6)]


def _groups(cells: list[dict], rho: float, cap: int) -> dict[int, dict]:
    index = _index(cells)
    seeds = sorted({k[3] for k in index})
    return {seed: {arm: index[(arm, cap, round(rho, 6), seed)]
                   for arm in ARMS} for seed in seeds}


def gates(cells: list[dict], identity: dict) -> dict:
    """Comparability gates. Any failure voids the block and no criterion is read."""
    out: dict = {}
    design = prereg()["design"]
    seeds = design["seeds"]

    # G0 liveness: at the sparsest level the two arms must not select the same rows.
    for cap in CAPS:
        groups = _groups(cells, MIN_RHO, cap)
        differ = sum(1 for seed in seeds
                     if sorted(groups[seed]["control"]["selected"]) !=
                     sorted(groups[seed]["diversity"]["selected"]))
        out["G0_liveness_cap_%d" % cap] = {
            "seeds_where_arms_differ": differ, "of": len(seeds),
            "required": SIGN_TEST_MIN,
            "passed": differ >= SIGN_TEST_MIN,
        }

    smallest_presence = min(float(c["presence"]) for c in cells)
    out["G1_presence_ceiling"] = {
        "minimum": smallest_presence, "required": 1.0,
        "passed": abs(smallest_presence - 1.0) <= TOL,
    }

    bad = []
    for c in cells:
        asserted, covered = c.get("asserted"), c.get("covered")
        if asserted is None or covered is None or asserted <= 0:
            bad.append((c["arm"], c["cap"], c["rho_world"], c["seed"], "no counts"))
            continue
        coverage, precision = float(c["coverage"]), float(c["precision"])
        if covered < 0 or covered > asserted:
            bad.append((c["arm"], c["cap"], c["rho_world"], c["seed"], "covered/asserted"))
        elif abs(precision - covered / asserted) > 1e-6:
            bad.append((c["arm"], c["cap"], c["rho_world"], c["seed"], "precision"))
        elif not (0.0 <= coverage <= 1.0 and 0.0 <= precision <= 1.0):
            bad.append((c["arm"], c["cap"], c["rho_world"], c["seed"], "range"))
    out["G2_arithmetic_consistency"] = {
        "cells_failing": len(bad), "example": bad[:2], "passed": not bad,
    }

    live = []
    for cap in CAPS:
        low = _mean(c["rho_rank"] for c in cells
                    if c["cap"] == cap and abs(c["rho_world"] - MIN_RHO) < TOL)
        high = _mean(c["rho_rank"] for c in cells
                     if c["cap"] == cap and abs(c["rho_world"] - MAX_RHO) < TOL)
        live.append(high > low)
        out["G3_rho_rank_moves_by_cap_%d" % cap] = {"at_min": round(low, 4),
                                                    "at_max": round(high, 4),
                                                    "passed": high > low}
    out["G3_axis_live"] = {"passed": all(live)}

    control_floor = _mean(c["coverage"] for c in cells
                          if c["arm"] == "control" and c["cap"] == PRIMARY_CAP
                          and abs(c["rho_world"] - MIN_RHO) < TOL)
    ceiling = prereg()["gates"]["control_coverage_ceiling"]
    out["G4_control_reproduces_gate13"] = {
        "control_coverage_at_min_density": round(control_floor, 6),
        "must_not_exceed": ceiling, "passed": control_floor <= ceiling,
    }

    identical = bool(identity.get("arms_identical"))
    zero = abs(float(identity.get("delta", 1.0))) <= TOL
    out["G5_identity_at_density_1"] = {
        "rho_world": identity.get("rho_world"), "arms_identical": identical,
        "delta": identity.get("delta"), "passed": identical and zero,
    }

    out["all_passed"] = all(v.get("passed") for v in out.values() if isinstance(v, dict))
    return out


def criteria(cells: list[dict]) -> dict:
    """M1, the level at the sparsest point. M2 is withdrawn (Amendment 4).

    The density ladder is a profile, not a criterion: the precision gap at cap 20 is set
    by how many crowded sources the spread must spend on, which does not vary with density,
    and the coverage gap can only vary through |W|, the denominator. Reporting the ladder
    keeps the shape visible without letting arithmetic decide a verdict.
    """
    record = prereg()
    bar = record["criteria"]["M1_bar"]
    index = _index(cells)
    seeds = sorted({k[3] for k in index})
    low = round(MIN_RHO, 6)

    delta_cov = {}
    for seed in seeds:
        control = index[("control", PRIMARY_CAP, low, seed)]
        treated = index[("diversity", PRIMARY_CAP, low, seed)]
        delta_cov[seed] = treated["coverage"] - control["coverage"]

    seed = int(record["seeds"]["bootstrap"])
    m1_mean = _mean(delta_cov.values())
    m1_interval = _interval(list(delta_cov.values()), seed)
    m1 = m1_mean >= bar and m1_interval[0] > 0

    profile = {}
    for rho in record["design"]["densities"]:
        rho = round(float(rho), 6)
        cov, prec = [], []
        for seed in seeds:
            control = index[("control", PRIMARY_CAP, rho, seed)]
            treated = index[("diversity", PRIMARY_CAP, rho, seed)]
            cov.append(treated["coverage"] - control["coverage"])
            prec.append(treated["precision"] - control["precision"])
        profile["%.1f" % rho] = {
            "coverage_gap_mean": round(_mean(cov), 6),
            "precision_gap_mean": round(_mean(prec), 6),
            "seeds_with_a_positive_coverage_gap": sum(1 for v in cov if v > 0),
        }

    return {
        "M1": {"mean_delta_at_min_density": round(m1_mean, 6),
               "interval": m1_interval, "interval_upper": m1_interval[1],
               "interval_width": round(m1_interval[1] - m1_interval[0], 6),
               "bar": bar, "passed": bool(m1)},
        "M2": {"withdrawn": True, "amendment": 4,
               "reason": record["criteria"]["M2_withdrawn"]},
        "density_profile": profile,
    }


def verdict(gate_report: dict, criterion_report: dict) -> dict:
    """Level-based, because M2 is withdrawn: M1 alone decides."""
    if not gate_report["all_passed"]:
        failed = sorted(k for k, v in gate_report.items()
                        if isinstance(v, dict) and v.get("passed") is False)
        return {"verdict": "VOID", "failed_gates": failed,
                "decision": "neither", "reading": "a gate failed; no criterion is read"}
    if criterion_report["M1"]["passed"]:
        return {"verdict": "ORDERING SUPPORTED", "decision": "positive",
                "reading": "the ordering basis is the lever at the sparsest density; the "
                           "density ladder is reported as a characterization, not scored"}
    width = criterion_report["M1"]["interval_width"]
    if width > prereg()["criteria"]["underpowered_width"]:
        return {"verdict": "UNDERPOWERED", "decision": "neither",
                "reading": "the interval cannot place the level; closing the line "
                           "would read a draw as an absence"}
    return {"verdict": "ORDERING NOT THE LEVER", "decision": "negative",
            "reading": "ordering is closed at this cap and world family; the line moves "
                       "to the candidate space"}


def score(payload: dict, record: dict | None = None) -> dict:
    record = record or prereg()
    cells = payload["cells"]
    validate(cells, record)
    gate_report = gates(cells, payload["identity"])
    criterion_report = (criteria(cells) if gate_report["all_passed"]
                        else {"M1": {"passed": None}, "M2": {"passed": None}})
    return {
        "prereg": record["prereg"],
        "cells": len(cells),
        "gates": gate_report,
        "criteria": criterion_report,
        "decision": verdict(gate_report, criterion_report),
        "not_evidence": record["not_evidence"],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="docs/rank_ordering_run.json")
    parser.add_argument("--out", default="docs/rank_ordering_result.json")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.results).read_text(encoding="utf-8"))
    result = score(payload)
    Path(args.out).write_text(json.dumps(engine_stamp.stamp(result), indent=1) + "\n", encoding="utf-8")
    print(result["decision"]["verdict"], "->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
