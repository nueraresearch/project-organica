"""
benchmarks/study_health.py
------------------------------------------------------------------
Standing health check for the 90-day longitudinal study.

Answers four questions about the running daemon:

  1. Is it alive?
  2. Is the sleep-cycle counter still strictly monotonic? (A reset means
     the counter bug is back, and every time series derived from it is
     suspect.)
  3. Is cycle latency still in the expected band? (A drift upward means
     the substrate is degrading again.)
  4. What is the rolling G5 duty cycle -- the fraction of recent cycles
     carrying at least one Theory?

Usage:
    python benchmarks/study_health.py
    python benchmarks/study_health.py --window 200 --json
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from pathlib import Path

LOG = Path(__file__).parent.parent / "organica.log"
CYCLE_RE = re.compile(r"Cycle\s+(\d+):\s+(\{.*\})")


def load_records(log_path: Path = LOG) -> list[dict]:
    records: list[dict] = []
    if not log_path.exists():
        return records
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = CYCLE_RE.search(line)
        if not m:
            continue
        try:
            records.append(json.loads(m.group(2)))
        except json.JSONDecodeError:
            continue
    return records


def main() -> int:
    ap = argparse.ArgumentParser(description="Health check for the Organica study.")
    ap.add_argument("--window", type=int, default=200,
                    help="cycles to include in the rolling duty cycle (default 200)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args()

    records = load_records()
    if not records:
        print("NO CYCLES PARSED - the daemon has not written a cycle summary yet")
        return 2

    sleep_cycles = [r.get("sleep_cycle", 0) for r in records]
    non_monotonic = sum(1 for i in range(1, len(sleep_cycles))
                        if sleep_cycles[i] <= sleep_cycles[i - 1])

    durations = [r.get("duration_ms", 0) for r in records]
    window = records[-args.window:]
    win_durations = [r.get("duration_ms", 0) for r in window]

    theories = [r.get("theories", 0) for r in window]
    questions = [r.get("questions", 0) for r in window]
    hypotheses = [r.get("hypotheses", 0) for r in window]
    dreams = [r.get("dreams", 0) for r in window]
    pruned = [r.get("substrate_rows_pruned", 0) for r in window]
    failures = [r for r in records if r.get("status") != "success"]

    n = max(len(window), 1)
    result = {
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_cycles_logged": len(records),
        "sleep_cycle_first": sleep_cycles[0],
        "sleep_cycle_last": sleep_cycles[-1],
        "counter_non_monotonic_steps": non_monotonic,
        "duration_median_ms": statistics.median(durations[-50:]) if durations else 0,
        "duration_max_ms": max(durations[-50:]) if durations else 0,
        "window": len(window),
        "g5_duty_cycle_pct": round(100 * sum(1 for t in theories if t > 0) / n, 1),
        "question_duty_cycle_pct": round(100 * sum(1 for q in questions if q > 0) / n, 1),
        "mean_theories_per_cycle": round(sum(theories) / n, 2),
        "mean_questions_per_cycle": round(sum(questions) / n, 2),
        "mean_hypotheses": round(sum(hypotheses) / n, 2),
        "mean_dreams": round(sum(dreams) / n, 2),
        "mean_rows_pruned": round(sum(pruned) / n, 1),
        "failed_cycles_total": len(failures),
        "window_duration_median_ms": statistics.median(win_durations) if win_durations else 0,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print("=" * 66)
    print("ORGANICA STUDY -- HEALTH CHECK")
    print("=" * 66)
    print(f"  checked at                 : {result['checked_at']}")
    print(f"  cycles logged              : {result['total_cycles_logged']}")
    print(f"  sleep_cycle {result['sleep_cycle_first']} .. {result['sleep_cycle_last']}"
          f"   non-monotonic steps: {non_monotonic}"
          f"   {'OK' if non_monotonic == 0 else 'COUNTER BROKEN'}")
    print(f"  duration median (last 50)  : {result['duration_median_ms']:.0f} ms"
          f"   max {result['duration_max_ms']:.0f} ms")
    print(f"  window                     : last {result['window']} cycles")
    print(f"  G5 duty cycle (theories)   : {result['g5_duty_cycle_pct']}%")
    print(f"  G5 duty cycle (questions)  : {result['question_duty_cycle_pct']}%")
    print(f"  mean theories / questions  : {result['mean_theories_per_cycle']} / {result['mean_questions_per_cycle']}")
    print(f"  mean hypotheses / dreams   : {result['mean_hypotheses']} / {result['mean_dreams']}")
    print(f"  mean substrate rows pruned : {result['mean_rows_pruned']}")
    print(f"  failed cycles (all time)   : {result['failed_cycles_total']}")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
