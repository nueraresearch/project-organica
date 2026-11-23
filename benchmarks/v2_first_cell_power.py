"""What benefit must the first cell show before its ten seeds can see it?

The null calibration (`V2-FIRST-CELL-NULL`) measured `d = L_C − L_A` on 20
structureless worlds: mean **+0.000847** nats, sd **0.000645**. A world with no
temporal law cannot contain a benefit by construction, so this diagnostic
injects one as a **known shift**: if arm C were better than the baseline by `b`
nats on a seed, that seed's `d` would be its measured null value minus `b`.

Injecting a constant shift is exact for the interval. The percentile bootstrap
of the mean shifts every resampled mean by the same `−b`, so an interval's
upper bound at benefit `b` is simply its upper bound at zero minus `b`. A cell
passes when `hi − b < 0`, i.e. when `b > hi`. Power is therefore the fraction
of ten-seed cells whose measured null upper bound lies below `b`, and the
smallest detectable benefit at a target power is that fraction's quantile.

It also means the null handicap has to be overcome first: the observed mean
`d` under a true benefit `b` is `+0.000847 − b`, so a cell only publishes a
negative difference once `b` exceeds the handicap.

    python -m benchmarks.v2_first_cell_power --check
    python -m benchmarks.v2_first_cell_power --write

This is a protocol diagnostic. It is not a cell, not a verdict, and it changes
no part of the pre-registration.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from benchmarks import engine_stamp, v2_first_cell_readout as readout  # noqa: E402

ARTIFACT = Path("docs/v2_first_cell_power.json")
PAGE = Path("docs/V2-FIRST-CELL-POWER.md")
NULL_ARTIFACT = Path("docs/v2_first_cell_null.json")
CELLS = 1000
RESAMPLES = 2000
CELL_SIZE = 10
GRID = [round(index * 0.0001, 6) for index in range(0, 36)]
TARGETS = (0.8, 0.9, 0.95)
CELL_RNG_SEED = 20261118


def null_diffs() -> dict[int, float]:
    record = json.loads(NULL_ARTIFACT.read_text(encoding="utf-8"))
    return {row["seed"]: row["d"] for row in record["per_seed"]}


def upper_bounds(diffs: dict[int, float], *, cells: int, resamples: int) -> list[float]:
    """The protocol interval's upper bound for each ten-seed null cell."""
    seeds = sorted(diffs)
    size = min(CELL_SIZE, len(seeds))
    rng = random.Random(CELL_RNG_SEED)
    bounds = []
    for _ in range(cells):
        chosen = rng.sample(seeds, size)
        interval = readout.paired_interval([diffs[seed] for seed in chosen],
                                           level=0.99, resamples=resamples)
        bounds.append(interval["hi"])
    return bounds


def build(cells: int = CELLS, resamples: int = RESAMPLES) -> dict:
    diffs = null_diffs()
    bias = statistics.fmean(diffs.values())
    sd = statistics.stdev(diffs.values())
    bounds = upper_bounds(diffs, cells=cells, resamples=resamples)
    ordered = sorted(bounds)

    def quantile(p: float) -> float:
        return ordered[int(round(p * (len(ordered) - 1)))]

    mde = {str(target): round(quantile(target), 6) for target in TARGETS}
    power = [{"benefit": benefit,
              "power": round(sum(1 for bound in bounds if bound < benefit) / len(bounds), 4)}
             for benefit in GRID]

    # The protocol uses 10,000 resamples. Check that 2,000 does not move the
    # bounds or the decision at the 90% point on the first 100 cells.
    fine = upper_bounds(diffs, cells=min(100, cells), resamples=10_000)
    coarse = upper_bounds(diffs, cells=min(100, cells), resamples=resamples)
    deltas = [abs(a - b) for a, b in zip(fine, coarse)]

    return engine_stamp.stamp({
        "kind": "v2_first_cell_power",
        "id": "V2-FIRST-CELL-POWER-1",
        "date": "2026-11-16",
        "status": "PROTOCOL DIAGNOSTIC — POWER AT THE MEASURED NULL NOISE, NOT A CELL AND NOT A VERDICT",
        "source": {
            "null_artifact": str(NULL_ARTIFACT),
            "null_seeds": sorted(diffs),
            "null_mean_d": round(bias, 6),
            "null_sd_d": round(sd, 6),
        },
        "method": {
            "injection": ("a known benefit `b` shifts every seed's measured null d by -b (constant-shift "
                          "model); the bootstrap interval shifts with it, so power is the fraction of cells "
                          "whose null upper bound lies below b"),
            "cells": cells, "cell_size": min(CELL_SIZE, len(diffs)), "resamples": resamples, "level": 0.99,
            "cell_rng_seed": CELL_RNG_SEED, "grid_step": 0.0001,
            "assumption": ("the treatment shifts the mean of d without changing its seed-to-seed variance; if a "
                           "real benefit varies across seeds, the benefit needed for the same power is larger"),
        },
        "upper_bounds": {
            "min": round(min(bounds), 6), "p50": round(quantile(0.5), 6),
            "p80": round(quantile(0.8), 6), "p90": round(quantile(0.9), 6),
            "p95": round(quantile(0.95), 6), "max": round(max(bounds), 6),
        },
        "power_curve": power,
        "mde": mde,
        "required_mean_d": {str(target): round(bias - mde[str(target)], 6) for target in TARGETS},
        "power_at_null_bias": round(sum(1 for bound in bounds if bound < bias) / len(bounds), 4),
        "convergence": {
            "cells": len(deltas), "resamples_fine": 10_000, "resamples_coarse": resamples,
            "max_abs_upper_bound_delta": round(max(deltas), 8) if deltas else None,
        },
        "note": ("the null was measured on structureless worlds, so this is the rule's sensitivity at that noise, "
                 "not a prediction about any real effect. A benefit smaller than the measured null handicap "
                 "cannot produce a negative observed difference at all."),
    })


def render_doc(record: dict) -> str:
    source = record["source"]
    curve = "\n".join("| %.4f | %.3f |" % (row["benefit"], row["power"])
                      for row in record["power_curve"] if round(row["benefit"] * 10000) % 5 == 0)
    mde_rows = "\n".join(
        "| %.0f%% | **%.6f** | %.6f |" % (float(target) * 100, record["mde"][target],
                                          record["required_mean_d"][target])
        for target in ("0.8", "0.9", "0.95"))
    return f"""# The interval's power at the measured null noise — a protocol diagnostic

**Status:** `{record['status']}`

**Question:** the directional criterion passes only when the ten-seed interval lies entirely below zero. How large must
the primitive's held-out benefit be for that to happen reliably? A rule that cannot see a benefit it is meant to detect is
as uninformative as one that manufactures a benefit that is not there — and the null calibration already showed the rule is
sensitive enough to resolve a handicap of {abs(source['null_mean_d']):.6f} nats.

## 1. The injection

A structureless world cannot contain a benefit, so the benefit is injected as a **known shift**: if arm C were better than
the baseline by `b` nats on a seed, that seed's `d = L_C − L_A` would be its measured null value minus `b`. The shift is
exact for the interval — the percentile bootstrap of the mean moves every resampled mean by `−b`, so the upper bound at
benefit `b` is the null upper bound minus `b`. A cell passes when `hi − b < 0`, i.e. when `b > hi`; power is therefore the
fraction of cells whose measured null upper bound lies below `b`.

Source: [`v2_first_cell_null.json`](v2_first_cell_null.json), {len(source['null_seeds'])} structureless worlds, mean `d` =
**{source['null_mean_d']:.6f}**, sd **{source['null_sd_d']:.6f}**. `{record['method']['cells']}` ten-seed cells,
{record['method']['resamples']:,} resamples each, level 99%.

**Assumption, stated:** the treatment shifts the mean of `d` without changing its seed-to-seed variance. A benefit that
varies across seeds would need to be larger for the same power.

## 2. The answer

| Target power | Smallest detectable benefit (nats) | Required mean `d = L_C − L_A` |
|---|---|---|
{mde_rows}

The second column is the benefit relative to the seed's null value; the third is the difference a cell would actually
observe. Because the null mean is **+{source['null_mean_d']:.6f}**, a benefit of {record['mde']['0.9']:.6f} nats is what it
takes for the *observed* mean to sit at {record['required_mean_d']['0.9']:.6f} — the handicap has to be overcome before any
benefit shows.

The upper-bound distribution across cells: min `{record['upper_bounds']['min']:.6f}`, median
`{record['upper_bounds']['p50']:.6f}`, p80 `{record['upper_bounds']['p80']:.6f}`, p90
`{record['upper_bounds']['p90']:.6f}`, p95 `{record['upper_bounds']['p95']:.6f}`, max
`{record['upper_bounds']['max']:.6f}`. Power at the null's own mean benefit ({source['null_mean_d']:.6f}) is
{record['power_at_null_bias']:.3f}: that is the case where a true benefit exactly cancels the handicap, so the true mean
difference is zero and the pass rate should match the null's directional false-pass rate — and it does.

| Injected benefit (nats) | Power |
|---|---|
{curve}

## 3. What this establishes, and what it does not

**Establishes:** at the noise measured on {len(source['null_seeds'])} structureless worlds, a ten-seed cell detects a true
benefit of **{record['mde']['0.8']:.6f}** nats 80% of the time, **{record['mde']['0.9']:.6f}** 90%, and
**{record['mde']['0.95']:.6f}** 95%. Those are properties of the rule at this noise, computed from the same interval code the
cell will run.

**Does not establish:** the size of any real effect. The null worlds are structureless; a real world's seed-to-seed
variance may be larger, which would raise every number in the table. Nor does it establish the probability of the charter's
other error — a null verdict when the primitive works — beyond the power curve above, which is exactly that error under the
constant-shift model.

**Convergence check:** the protocol uses 10,000 resamples; the calibration used {record['method']['resamples']:,}. On the
first {record['convergence']['cells']} cells the two agree to a maximum upper-bound difference of
{record['convergence']['max_abs_upper_bound_delta']:.8f} nats.

## 4. Reproduction

```bash
python -m benchmarks.v2_first_cell_power --write    # artifact and this page
python -m benchmarks.v2_first_cell_power --check    # page freshness, a small recomputation, and interval sanity
```

Artifact: [`v2_first_cell_power.json`](v2_first_cell_power.json).
"""


def check() -> None:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if render_doc(record) != PAGE.read_text(encoding="utf-8"):
        raise SystemExit("power page is stale; rebuild with --write")
    if record["kind"] != "v2_first_cell_power":
        raise SystemExit("artifact is not a power diagnostic")
    small = build(cells=100, resamples=500)
    powers = [row["power"] for row in small["power_curve"]]
    if powers != sorted(powers):
        raise SystemExit("power curve is not monotone")
    if small["power_curve"][0]["power"] != 0.0:
        raise SystemExit("power at zero benefit is not zero")
    if not (small["mde"]["0.8"] <= small["mde"]["0.9"] <= small["mde"]["0.95"]):
        raise SystemExit("detectable benefits are not ordered by target power")
    print("check: power diagnostic reproduces, its curve is monotone, and its MDEs are ordered")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify page freshness and interval sanity")
    parser.add_argument("--write", action="store_true", help="measure power and write artifact and page")
    args = parser.parse_args()
    if args.check:
        check()
        return 0
    if args.write:
        record = build()
        ARTIFACT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        PAGE.write_text(render_doc(record), encoding="utf-8")
        print(json.dumps({"mde": record["mde"], "required_mean_d": record["required_mean_d"],
                          "power_at_null_bias": record["power_at_null_bias"],
                          "convergence": record["convergence"]}, indent=1))
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
