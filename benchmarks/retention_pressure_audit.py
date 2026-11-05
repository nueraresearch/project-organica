"""
benchmarks/retention_pressure_audit.py
--------------------------------------
Evaluates hypothesis belief pool retention pressure (Gate G-P1).

Measures whether doubling MAX_PREDICTIONS to 40 generates sufficient belief supply
upstream to exceed MAX_HYPOTHESES = 15, activating retention policy competition.

Retention Policies:
  - "confidence": Rank hypotheses by confidence score descending.
  - "contradiction": Rank hypotheses by contradiction count descending (raw competing flow).
  - "shannon_entropy": Rank hypotheses by competing flow Shannon entropy H(E).

Usage:
  python benchmarks/retention_pressure_audit.py --cycles 300
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService
from organica.paths import temp_db
from organica.sleep import SleepService
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM


def audit_policy(policy: str, cycles: int = 300) -> dict[str, Any]:
    db = temp_db(f"audit_retention_{policy}.db")
    if db.exists():
        db.unlink()

    mem = MemoryService(str(db))
    svc = SleepService(mem)
    svc.HYPOTHESIS_RETENTION = policy

    # Seed memory
    for text in STUDY_STREAM:
        mem.store(text, event_type="event", source="seed:bootstrap")

    pool_sizes: list[int] = []
    pressure_ratios: list[float] = []
    retained_counts: list[int] = []
    competing_subjects_counts: list[int] = []
    theory_counts: list[int] = []

    # Hook hypothesis retention to observe pre-cap pool
    original_retain = svc._retain_hypotheses

    def tracking_retain(candidates):
        pool_size = len(candidates)
        pool_sizes.append(pool_size)
        pressure = round(pool_size / max(svc.MAX_HYPOTHESES, 1), 3)
        pressure_ratios.append(pressure)

        # Count subjects with >= 2 hypotheses
        subjects = {}
        for c in candidates:
            subj = getattr(c, "subject", "")
            subjects[subj] = subjects.get(subj, 0) + 1
        competing = sum(1 for cnt in subjects.values() if cnt >= 2)
        competing_subjects_counts.append(competing)

        retained = original_retain(candidates)
        retained_counts.append(len(retained))
        return retained

    svc._retain_hypotheses = tracking_retain

    for c in range(cycles):
        start = (c * EVENTS_PER_CYCLE) % len(STUDY_STREAM)
        for text in STUDY_STREAM[start:start + EVENTS_PER_CYCLE]:
            mem.store(text, event_type="event", source=f"cycle:{c}")
        rep = svc.run_sleep_cycle()
        theory_counts.append(len(rep.theories))

    mem.close()
    db.unlink(missing_ok=True)

    mean_pool = round(sum(pool_sizes) / len(pool_sizes), 2) if pool_sizes else 0.0
    max_pool = max(pool_sizes) if pool_sizes else 0
    mean_pressure = round(sum(pressure_ratios) / len(pressure_ratios), 2) if pressure_ratios else 0.0
    max_pressure = max(pressure_ratios) if pressure_ratios else 0.0
    pressure_ge1_ratio = round(sum(1 for p in pressure_ratios if p >= 1.0) / len(pressure_ratios), 3) if pressure_ratios else 0.0

    return {
        "policy": policy,
        "cycles": cycles,
        "max_hypotheses_cap": svc.MAX_HYPOTHESES,
        "max_predictions_cap": svc.MAX_PREDICTIONS,
        "mean_pre_cap_pool": mean_pool,
        "max_pre_cap_pool": max_pool,
        "mean_retention_pressure": mean_pressure,
        "max_retention_pressure": max_pressure,
        "pressure_ge1_fraction": pressure_ge1_ratio,
        "gate_gp1_passed": mean_pressure > 1.0,
        "mean_competing_subjects": round(sum(competing_subjects_counts) / len(competing_subjects_counts), 2) if competing_subjects_counts else 0.0,
        "mean_theories": round(sum(theory_counts) / len(theory_counts), 2) if theory_counts else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description="Hypothesis Retention Pressure Audit (Gate G-P1)")
    parser.add_argument("--cycles", type=int, default=300, help="Cycles per policy run")
    args = parser.parse_args()

    policies = ["confidence", "contradiction", "shannon_entropy"]
    results = {}

    for pol in policies:
        print(f"Auditing policy '{pol}' ({args.cycles} cycles) ...")
        res = audit_policy(pol, cycles=args.cycles)
        results[pol] = res
        print(f"  mean pool: {res['mean_pre_cap_pool']}, mean pressure: {res['mean_retention_pressure']}, G-P1: {res['gate_gp1_passed']}")

    out_path = REPO / "docs" / "retention_pressure_audit.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote retention audit to {out_path}")


if __name__ == "__main__":
    main()
