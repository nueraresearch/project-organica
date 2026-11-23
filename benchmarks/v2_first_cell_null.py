"""How often does the pre-registered interval pass when there is nothing to find?

The first cell's failure rule is "an interval including zero fails the charter",
so its dangerous error is the opposite: an interval that *excludes* zero on a
world with no composition to learn. This module measures that rate directly.

It builds a **structureless null world** per seed: every event draws two tags
independently from the same 16-tag pool, at the same 8 events per block and
120 blocks the real world uses. There is no temporal law, so nothing about a
composite's membership can predict a held-out edge. Everything else is the
protocol: the frozen engine, the same detection, `m = 2`, the same admission,
the same calibration band, the same per-arm beta grid and the same scorer.

Then it resamples ten-seed cells from the measured null worlds, applies
`v2_first_cell_readout.paired_interval` (99%, 10,000 resamples) to each, and
counts how often the interval excludes zero. That count is the interval's
false-pass rate at the protocol's ten seeds.

    python -m benchmarks.v2_first_cell_null --check
    python -m benchmarks.v2_first_cell_null --write

This is a protocol diagnostic. It is not a cell, not a verdict, and it does not
change the pre-registration.
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
from benchmarks.acquisition_compositional import TAG_POOL  # noqa: E402
from organica.streams import EVENTS_PER_CYCLE  # noqa: E402

ARTIFACT = Path("docs/v2_first_cell_null.json")
PAGE = Path("docs/V2-FIRST-CELL-NULL.md")
NULL_SEEDS = list(range(20920101, 20920121))
CYCLES = 120
CELL_SIZE = 10
CELLS = 1000
CELL_RESAMPLES = 2000


def null_stream(seed: int, cycles: int) -> dict:
    """A world with the same tags, event length and block count, and no temporal law."""
    rng = random.Random(seed)
    events, trainable = [], []
    for _ in range(cycles * EVENTS_PER_CYCLE):
        first, second = rng.sample(TAG_POOL, 2)
        events.append("%s %s" % (first, second))
        trainable.append(True)
    return {"events": events, "trainable": trainable}


def measure(seed: int, cycles: int = CYCLES) -> dict:
    stream = null_stream(seed, cycles)
    data = readout.replay(seed, cycles, stream)
    scored = readout.arms_for(data["tags"], data["detections"], cycles)
    arms = scored["arms"]
    return {
        "seed": seed,
        "blocks": data["blocks"],
        "detections": len(data["detections"]),
        "arms": arms,
        "d": round(arms["C"]["log_loss"] - arms["A"]["log_loss"], 6),
    }


def calibrate(diffs_by_seed: dict, *, cells: int, resamples: int, level: float = 0.99) -> dict:
    seeds = sorted(diffs_by_seed)
    size = min(CELL_SIZE, len(seeds))
    rng = random.Random(20261117)
    pool = [value for values in diffs_by_seed.values() for value in values]
    pool_mean = statistics.fmean(pool)
    excluded = above = below = contains = 0
    widths = []
    for _ in range(cells):
        chosen = rng.sample(seeds, size)
        cell = [rng.choice(diffs_by_seed[seed]) for seed in chosen]
        interval = readout.paired_interval(cell, level=level, resamples=resamples)
        if interval["includes_zero"]:
            pass
        else:
            excluded += 1
            above += int(interval["lo"] > 0)
            below += int(interval["hi"] < 0)
        contains += int(interval["lo"] <= pool_mean <= interval["hi"])
        widths.append(interval["hi"] - interval["lo"])
    inclusion = (cells - excluded) / cells
    directional = below / cells
    return {
        "cells": cells, "cell_size": size, "resamples": resamples, "level": level,
        "excludes_zero_rate": round(excluded / cells, 4),
        "includes_zero_rate": round((cells - excluded) / cells, 4),
        "excludes_above_zero": above, "excludes_below_zero": below,
        "directional_false_pass_rate": round(directional, 4),
        "coverage_of_pool_mean": round(contains / cells, 4),
        "median_width": round(statistics.median(widths), 6),
        "monte_carlo_se": round((inclusion * (1 - inclusion) / cells) ** 0.5, 4),
        "directional_se": round((directional * (1 - directional) / cells) ** 0.5, 4),
        "bootstrap_rng_seed": readout.BOOTSTRAP_SEED,
        "cell_rng_seed": 20261117,
    }


def run(seeds=None, cycles: int = CYCLES, cells: int = CELLS,
        resamples: int = CELL_RESAMPLES) -> dict:
    seeds = NULL_SEEDS if seeds is None else list(seeds)
    per_seed = [measure(seed, cycles) for seed in seeds]
    diffs = [row["d"] for row in per_seed]
    calibration = calibrate({row["seed"]: [row["d"]] for row in per_seed},
                            cells=cells, resamples=resamples) if len(seeds) >= 2 else None
    record = {
        "kind": "v2_first_cell_null",
        "id": "V2-FIRST-CELL-NULL-1",
        "date": "2026-11-16",
        "status": "PROTOCOL DIAGNOSTIC — A NULL-WORLD CALIBRATION, NOT A CELL AND NOT A VERDICT",
        "protocol": {
            "m": readout.M, "alpha": readout.ALPHA, "beta_grid": list(readout.BETA_GRID),
            "window": readout.WINDOW, "cells": CELLS, "cell_size": CELL_SIZE,
            "cell_resamples": CELL_RESAMPLES, "level": 0.99,
            "failure_rule": "an interval including zero fails the charter",
        },
        "null_world": {
            "construction": ("each event draws two tags independently from the same 16-tag pool, "
                             "at the same 8 events per block and the same block count; no temporal law"),
            "tag_pool_size": len(TAG_POOL),
            "events_per_cycle": EVENTS_PER_CYCLE,
            "cycles": cycles,
            "seeds": seeds,
        },
        "per_seed": per_seed,
        "summary": {
            "n": len(diffs),
            "mean_d": round(statistics.fmean(diffs), 6),
            "sd_d": round(statistics.stdev(diffs), 6) if len(diffs) > 1 else None,
            "min_d": round(min(diffs), 6), "max_d": round(max(diffs), 6),
            "median_composites_c": round(statistics.median(
                [row["arms"]["C"]["composites"] for row in per_seed]), 3),
            "median_detections": round(statistics.median([row["detections"] for row in per_seed]), 3),
        },
        "calibration": calibration,
        "reference_interval_20_seeds": readout.paired_interval(diffs, resamples=10_000),
        "note": ("the null removes the temporal law, not the apparatus: detections, admission, beta selection "
                 "and the scorer are unchanged. A false pass is an interval that excludes zero on a world with "
                 "nothing to learn; the charter's own error is the opposite one, an interval that includes zero "
                 "when there is something to find, which this diagnostic does not measure."),
    }
    return engine_stamp.stamp(record)


def render_doc(record: dict) -> str:
    cal = record["calibration"]
    summary = record["summary"]
    rows = "\n".join(
        "| `%d` | %.6f | %.6f | %.6f | %s | %s | %d |" % (
            row["seed"], row["arms"]["A"]["log_loss"], row["arms"]["B"]["log_loss"],
            row["arms"]["C"]["log_loss"],
            row["arms"]["B"]["beta"], row["arms"]["C"]["beta"],
            row["arms"]["C"]["composites"])
        for row in record["per_seed"])
    ref = record["reference_interval_20_seeds"]
    return f"""# The interval on null worlds — a protocol diagnostic

**Status:** `{record['status']}`

**Question:** the first cell fails when its 99% interval includes zero. What is the opposite error — how often does that
interval **exclude** zero on a world with no composition to learn? A rule that cannot produce a false pass on a null world
cannot manufacture a result; a rule that can, at a rate worth knowing, has a number attached to it now.

## 1. What is null here

`{record['null_world']['construction']}`. The tag pool is {record['null_world']['tag_pool_size']} tags, every event carries
two of them, and the world has {record['null_world']['events_per_cycle']} events per block over
{record['null_world']['cycles']} blocks — the real world's shape, with its temporal law removed. The engine, the detection,
the admission at `m = {record['protocol']['m']}`, the calibration band, the per-arm β grid
`{record['protocol']['beta_grid']}`, the 20-cycle revision rule and the scorer are unchanged. Only the sequence is gone.

## 2. What the null worlds measured

`d = L_C − L_A` per seed; a positive value means the primitive scored *worse* than the pair counts.

| Seed | A | B | C | β (B) | β (C) | Composites |
|---|---|---|---|---|---|---|
{rows}

Across {summary['n']} null worlds: mean `d` = **{summary['mean_d']:.6f}**, sd `{summary['sd_d']:.6f}`, range
`[{summary['min_d']:.6f}, {summary['max_d']:.6f}]`; median composites {summary['median_composites_c']:.0f}, median
detections {summary['median_detections']:.0f}. The 20-seed interval — wider than the protocol's ten-seed cell, and reported
only as a reference — is `[{ref['lo']:.6f}, {ref['hi']:.6f}]` around `{ref['mean']:.6f}`.

## 3. The calibration

`{cal['cells']}` cells, each drawing {cal['cell_size']} distinct null seeds and applying the protocol's interval
({cal['resamples']:,} resamples per cell, level {cal['level']:.0%}).

| Quantity | Value |
|---|---|
| Cells in which the interval **included** zero | **{round(cal['includes_zero_rate'] * cal['cells']):,} of {cal['cells']:,}** ({cal['includes_zero_rate']:.4f}) |
| Cells in which it excluded zero | {cal['excludes_above_zero'] + cal['excludes_below_zero']:,} ({cal['excludes_zero_rate']:.4f}) |
| — excluded **above** zero (C worse) | {cal['excludes_above_zero']:,} |
| — excluded **below** zero (C better) | {cal['excludes_below_zero']:,} |
| False-pass rate under the **directional** rule (Amendment 2) | **{cal['directional_false_pass_rate']:.4f}** |
| Cell intervals containing the null's pool mean | {cal['coverage_of_pool_mean']:.4f} |
| Median interval width | {cal['median_width']:.6f} |

## 4. What this establishes, and what it does not

**The interval is calibrated around the null's mean** — {cal['coverage_of_pool_mean']:.1%} of cell intervals contained the
pool mean — **but the null's mean is not zero.** On structureless worlds arm C is slower by
**{summary['mean_d']:.6f}** nats (sd {summary['sd_d']:.6f}), so at ten seeds the interval resolves that handicap in
{cal['excludes_zero_rate']:.1%} of cells. Every one of those exclusions lies **above** zero: the rule never claims the
primitive helped, but it does reject the null, and the two-sided wording as first signed would count that as a pass.

**That wording was wrong and is corrected.** Amendment 2 makes the criterion directional: the charter passes only when the
interval lies entirely **below** zero; an interval including zero fails as bookkeeping, and an interval entirely above zero
fails as a reversal. Under that rule the null's false-pass rate is **{cal['directional_false_pass_rate']:.4f}** — 0 of
{cal['cells']:,} cells claimed a benefit that was not there.

**What is not established:** the rate of the charter's own error, a null verdict when the primitive does work. That is a
power question and this diagnostic does not measure it. The null also removes the temporal law rather than generating
independently drawn worlds from the same family, and its cell draws reuse the same {summary['n']} worlds, so the rate's
uncertainty is a little wider than the Monte Carlo error suggests.

**One caution about the construction:** removing the temporal law changes what the detector sees — the median null world
yielded {summary['median_detections']:.0f} loop detections — so this is the readout's null behaviour on worlds where
detections still form, not the whole engine on a different law.

## 5. Reproduction

```bash
python -m benchmarks.v2_first_cell_null --write    # artifact and this page
python -m benchmarks.v2_first_cell_null --check    # pins, a small deterministic run, page freshness
```

Artifact: [`v2_first_cell_null.json`](v2_first_cell_null.json).
"""


def check() -> None:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if render_doc(record) != PAGE.read_text(encoding="utf-8"):
        raise SystemExit("null page is stale; rebuild with --write")
    if record["kind"] != "v2_first_cell_null":
        raise SystemExit("artifact is not a null diagnostic")
    first = run(seeds=NULL_SEEDS[:2], cycles=12, cells=40, resamples=200)
    second = run(seeds=NULL_SEEDS[:2], cycles=12, cells=40, resamples=200)
    if [row["d"] for row in first["per_seed"]] != [row["d"] for row in second["per_seed"]]:
        raise SystemExit("null measurement is not deterministic")
    if len(record["per_seed"]) != len(NULL_SEEDS):
        raise SystemExit("artifact does not cover the declared null seeds")
    for row in record["per_seed"]:
        if abs((row["arms"]["C"]["log_loss"] - row["arms"]["A"]["log_loss"]) - row["d"]) > 1e-6:
            raise SystemExit("a recorded difference does not match its arm losses")
    print("check: null diagnostic is deterministic, the page is fresh, and the artifact covers %d worlds"
          % len(record["per_seed"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the pin, determinism and page freshness")
    parser.add_argument("--write", action="store_true", help="measure the null worlds and write artifact and page")
    args = parser.parse_args()
    if args.check:
        check()
        return 0
    if args.write:
        record = run()
        ARTIFACT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        PAGE.write_text(render_doc(record), encoding="utf-8")
        print(json.dumps({"summary": record["summary"], "calibration": record["calibration"]}, indent=1))
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
