"""
benchmarks/substrate_scaling_analysis.py
------------------------------------------------------------------
Phase G diagnostic: does the memory substrate survive a 90-day run?

Phase G ("30-day continuous life cycle in an active server/development
environment") and the 90-day longitudinal study both depend on the
substrate staying affordable. This script measures the REAL growth curve
from the daemon's own log rather than from a synthetic probe.

Two quantities matter:

  1. Cycle latency vs. cumulative event count. If latency grows
     linearly with the event table, total work is O(n^2) and the study
     cannot run for 90 days.

  2. The growth of the event table itself. Sleep candidates are persisted
     as `event_type="sleep"` rows, so the substrate grows even when the
     cognitive population is stable.

Usage:
    python benchmarks/substrate_scaling_analysis.py
    python benchmarks/substrate_scaling_analysis.py --cycles 90

Writes docs/substrate_scaling_analysis.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import metrics  # noqa: E402


def fit_linear(xs, ys):
    """Least-squares slope/intercept for y = a*x + b. Returns (a, b, r2)."""
    n = len(xs)
    if n < 2:
        return None, None, None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    if sxx == 0:
        return None, None, None
    a = sxy / sxx
    b = mean_y - a * mean_x
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - (ss_res / ss_tot) if ss_tot else 1.0
    return a, b, r2


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyse Organica substrate scaling.")
    ap.add_argument("--cycles", type=int, default=0,
                    help="limit analysis to the last N cycles (0 = all)")
    ap.add_argument("--out", type=str, default="docs/substrate_scaling_analysis.json")
    args = ap.parse_args()

    cycles = metrics.parse_cycles()
    if not cycles:
        print("ERROR: no cycles parsed from organica.log")
        return 1
    if args.cycles:
        cycles = cycles[-args.cycles:]

    rows = []
    for c in cycles:
        dur = c.get("duration_ms", 0)
        cyc = c.get("cycle", 0)
        rows.append({
            "cycle": cyc,
            "duration_ms": dur,
            # Each cycle injects 4 experience events plus the persisted
            # sleep candidates; the log gives us the composite count and
            # the candidate counts, which bound the growth.
            "composites_created": c.get("composites_created", 0),
            "candidates_strengthened": c.get("candidates_strengthened", 0),
            "candidates_pruned": c.get("candidates_pruned", 0),
            "total_composites": c.get("total_composites", 0),
        })

    xs = [r["cycle"] for r in rows]
    ys = [r["duration_ms"] for r in rows]
    slope, intercept, r2 = fit_linear(xs, ys)

    # Extrapolate: a 90-day run at the configured 30s interval.
    CYCLES_90D = 90 * 24 * 60 * 2  # 30s interval
    if slope is not None:
        predicted_90d_ms = slope * CYCLES_90D + intercept
    else:
        predicted_90d_ms = None

    # Event-table size estimate. Sleep candidates persist one row each.
    # We can bound the per-cycle write rate from the log's own counts.
    avg_composites = sum(r["composites_created"] for r in rows) / len(rows)
    avg_strengthened = sum(r["candidates_strengthened"] for r in rows) / len(rows)

    print("=" * 74)
    print("PROJECT ORGANICA -- SUBSTRATE SCALING ANALYSIS (real daemon log)")
    print("=" * 74)
    print(f"  cycles analysed                : {len(rows)}")
    print(f"  cycle range                    : {xs[0]} .. {xs[-1]}")
    print(f"  latency first -> last          : {ys[0]}ms -> {ys[-1]}ms")
    if ys:
        print(f"  latency min / max              : {min(ys)}ms / {max(ys)}ms")
    if slope is not None:
        print(f"  linear fit  latency_ms         : {slope:.3f} * cycle + {intercept:.1f}   (R^2 = {r2:.4f})")
        print(f"  marginal cost per cycle        : {slope:.3f} ms")
        print(f"  extrapolated 90-day latency    : {predicted_90d_ms/1000:.1f} s per cycle "
              f"({predicted_90d_ms/60000:.1f} min)")
        print(f"    (90d @ 30s interval = {CYCLES_90D:,} cycles)")
        print(f"  total projected CPU over 90d   : {predicted_90d_ms * CYCLES_90D / 3.6e9:.1f} CPU-hours")
    print(f"  avg composites created / cycle : {avg_composites:.1f}")
    print(f"  avg candidates strengthened    : {avg_strengthened:.1f}")
    print(f"  final total_composites         : {rows[-1]['total_composites']}")

    if slope is not None and r2 is not None and r2 > 0.9 and slope > 1.0:
        print("\n  VERDICT: latency grows LINEARLY with cycle count (R^2 > 0.9).")
        print("  The substrate is O(n) per cycle -> O(n^2) total. A 90-day run")
        print("  is not reachable without substrate work, regardless of the")
        print("  cognitive findings.")
    else:
        print("\n  VERDICT: no strong linear growth detected in this window.")

    # Persist candidates as sleep events: every stored candidate is a row.
    # Estimate the event table growth from the log's own write counters.
    per_cycle_rows = 4 + avg_composites + avg_strengthened
    est_90d_rows = per_cycle_rows * CYCLES_90D
    print(f"\n  estimated persisted rows/cycle : {per_cycle_rows:.0f}")
    print(f"  estimated 90-day event rows    : {est_90d_rows/1e6:.1f} million")

    out = Path(__file__).parent.parent / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "G",
        "title": "Substrate Scaling Analysis (real daemon log)",
        "method": "Least-squares fit of sleep-cycle latency against cycle index "
                  "from the daemon's own organica.log, plus event-table projection.",
        "cycles_analysed": len(rows),
        "cycle_range": [xs[0], xs[-1]],
        "latency_first_ms": ys[0],
        "latency_last_ms": ys[-1],
        "latency_min_ms": min(ys),
        "latency_max_ms": max(ys),
        "linear_fit": {
            "slope_ms_per_cycle": slope,
            "intercept_ms": intercept,
            "r_squared": r2,
            "model": "latency_ms = slope * cycle + intercept",
        },
        "projection_90d": {
            "assumed_interval_s": 30,
            "cycles": CYCLES_90D,
            "predicted_latency_ms_per_cycle": predicted_90d_ms,
            "predicted_cpu_hours_total": (predicted_90d_ms * CYCLES_90D / 3.6e9) if predicted_90d_ms else None,
            "estimated_event_rows": est_90d_rows,
        },
        "per_cycle": rows,
    }, indent=2))
    print(f"\n  Full report written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
