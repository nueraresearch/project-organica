"""Characterise the count control's cap-20 precision across a wide seed sweep (diagnostic only).

Reads `.scratch/control_precision_sweep.jsonl` (one row per seed, written by
`benchmarks/gate13_control_precision_sweep.py`) and answers three questions:

  1. Is the frozen comparator 0.4667 a structural constant?  The pool is reported per cell, so this is
     checked rather than assumed: 112 world edges in 240 rows on every seed.
  2. What is the distribution of arm C's cap-20 asserted precision across seeds -- mean, spread,
     quantiles -- and how often does it fall inside the +-0.05 band that C1 required on 21 of 25?
  3. Where do the development (5 seeds) and confirmatory (25 seeds) blocks sit in that distribution?

Nothing here is pre-registered and no threshold is tested; the output is a characterisation written to
`docs/gate13_control_precision_sweep.json`. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
from pathlib import Path

BASE = 0.4667
BAND = 0.05


def _cells(path: Path) -> list[dict]:
    art = json.loads(path.read_text())
    for k in ("raw", "cells", "rows"):
        if isinstance(art.get(k), list) and art[k] and isinstance(art[k][0], dict):
            return art[k]
    raise SystemExit(f"no cell list in {path}")


def _precisions(path: Path) -> list[float]:
    out = []
    for r in _cells(path):
        if r.get("arm") == "C" and r.get("cap") == 20 and r.get("precision") is not None:
            out.append(r["precision"])
    return out


def pct(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    idx = q * (len(sorted_vals) - 1)
    lo, hi = math.floor(idx), math.ceil(idx)
    return sorted_vals[lo] if lo == hi else sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)


def bootstrap_ci(vals: list[float], stat, reps: int = 20000, seed: int = 0) -> tuple[float, float]:
    rng, n = random.Random(seed), len(vals)
    draws = sorted(stat([vals[rng.randrange(n)] for _ in range(n)]) for _ in range(reps))
    return round(draws[int(0.025 * reps)], 4), round(draws[int(0.975 * reps) - 1], 4)


def summarise(vals: list[float]) -> dict:
    s = sorted(vals)
    m, sd = st.fmean(vals), st.stdev(vals)
    lo, hi = bootstrap_ci(vals, st.fmean)
    return {
        "n": len(vals),
        "mean": round(m, 4),
        "median": round(st.median(vals), 4),
        "sd": round(sd, 4),
        "min": round(s[0], 4),
        "q10": round(pct(s, 0.10), 4),
        "q25": round(pct(s, 0.25), 4),
        "q75": round(pct(s, 0.75), 4),
        "q90": round(pct(s, 0.90), 4),
        "max": round(s[-1], 4),
        "mean_ci95": [lo, hi],
        "t_vs_base": round((m - BASE) / (sd / math.sqrt(len(vals))), 2),
        "within_band": round(sum(1 for v in vals if abs(v - BASE) <= BAND) / len(vals), 4),
        "below_base": round(sum(1 for v in vals if v < BASE) / len(vals), 4),
    }


def rank_of(vals: list[float], x: float) -> dict:
    s = sorted(vals)
    return {"value": round(x, 4),
            "percentile": round(100.0 * sum(1 for v in s if v < x) / len(s), 1),
            "z": round((x - st.fmean(vals)) / st.stdev(vals), 2)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default=".scratch/control_precision_sweep.jsonl")
    ap.add_argument("--out", default="docs/gate13_control_precision_sweep.json")
    args = ap.parse_args()

    rows = [json.loads(l) for l in Path(args.jsonl).read_text().splitlines() if l.strip()]
    seeds = sorted(r["seed"] for r in rows)
    prec = [r["precision"] for r in rows if r["precision"] is not None]
    asserted = [r["asserted"] for r in rows]
    base_rates = {r.get("base_rate") for r in rows}
    pool_rows = {r.get("pool_rows") for r in rows}
    pool_edges = {r.get("pool_world_edges") for r in rows}
    top20 = [r["top_k"]["20"] for r in rows if r.get("top_k", {}).get("20") is not None]

    dev = _precisions(Path("docs/gate13_ratio_arm.json"))
    conf = _precisions(Path("docs/gate13_ratio_confirm.json"))

    art = {
        "what": "diagnostic characterisation of the count-sorted control's cap-20 asserted precision",
        "status": "NOT CONFIRMATORY. No threshold is pre-registered; this characterises why C1 failed.",
        "harness": "benchmarks/gate13_control_precision_sweep.py",
        "computation": "benchmarks.run_ratio_admission_arm.run_cell(arm='C', cap=20, seed)",
        "hash_seed": 0,
        "block": {"lo": seeds[0], "hi": seeds[-1], "seeds": len(seeds)},
        "commit": sorted({r.get("commit", "unknown") for r in rows}),
        "comparator_check": {
            "frozen_base_rate": BASE,
            "base_rates_seen": sorted(base_rates),
            "pool_rows_seen": sorted(pool_rows),
            "pool_world_edges_seen": sorted(pool_edges),
            "constant": base_rates == {BASE} and pool_rows == {240} and pool_edges == {112},
        },
        "precision": summarise(prec),
        "asserted_size": {"min": min(asserted), "median": st.median(asserted), "max": max(asserted)},
        "pool_top20_density": summarise(top20),
        "dev_block_5": {"values": dev, "mean": round(st.fmean(dev), 4), "median": round(st.median(dev), 4),
                        "within_band": sum(1 for v in dev if abs(v - BASE) <= BAND)},
        "confirm_block_25": {"mean": round(st.fmean(conf), 4), "median": round(st.median(conf), 4),
                             "within_band": sum(1 for v in conf if abs(v - BASE) <= BAND),
                             "placement_of_mean": rank_of(prec, st.fmean(conf)),
                             "placement_of_median": rank_of(prec, st.median(conf))},
        "dev_placement_of_mean": rank_of(prec, st.fmean(dev)),
        "raw": rows,
    }
    out = Path(args.out)
    out.write_text(json.dumps(art, indent=2) + "\n")

    p = art["precision"]
    print(f"seeds {seeds[0]}-{seeds[-1]}  n={p['n']}  comparator constant={art['comparator_check']['constant']}")
    print(f"precision mean {p['mean']} ci{p['mean_ci95']} median {p['median']} sd {p['sd']} "
          f"range {p['min']}-{p['max']} q25-q75 {p['q25']}-{p['q75']}")
    print(f"within +-{BAND} of {BASE}: {p['within_band']:.1%}   below base: {p['below_base']:.1%}   t={p['t_vs_base']}")
    print(f"dev mean {art['dev_block_5']['mean']} -> {art['dev_placement_of_mean']['percentile']}th pct "
          f"(z {art['dev_placement_of_mean']['z']}); confirm mean "
          f"{art['confirm_block_25']['mean']} -> {art['confirm_block_25']['placement_of_mean']['percentile']}th pct "
          f"(z {art['confirm_block_25']['placement_of_mean']['z']})")
    print(f"pool top-20 density median {art['pool_top20_density']['median']} "
          f"range {art['pool_top20_density']['min']}-{art['pool_top20_density']['max']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
