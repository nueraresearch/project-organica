"""
benchmarks/active_inquiry_benchmark.py
--------------------------------------
Head-to-head comparison of Passive Observation vs Active Inquiry (Law IV).

Compares:
  Arm 1: Passive Observation (Organism only observes natural stream).
  Arm 2: Active Inquiry (Organism emits Layer-8 experiment probes into ReactiveWorld,
         observes immediate causal feedback, updates memory, and closes questions).

Usage:
  python benchmarks/active_inquiry_benchmark.py --cycles 150
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

from organica.environment import ActiveInquiryLoop, ReactiveWorld
from organica.memory import MemoryService
from organica.paths import temp_db
from organica.sleep import SleepService
from benchmarks import engine_stamp


def run_passive_arm(cycles: int) -> dict[str, Any]:
    db = temp_db("active_benchmark_passive.db")
    if db.exists():
        db.unlink()

    mem = MemoryService(str(db))
    svc = SleepService(mem)
    world = ReactiveWorld()

    unique_structures: set[str] = set()
    theories_series: list[int] = []
    questions_series: list[int] = []
    experiments_series: list[int] = []
    hypotheses_series: list[int] = []

    t0 = time.perf_counter()
    for c in range(cycles):
        # 1. Ingest natural events
        with mem.batch():
            for _ in range(5):
                for text in world.step():
                    mem.store(text, event_type="observe", source=f"env:{c}")

        # 2. Consolidate sleep (passive - no active intervention)
        rep = svc.run_sleep_cycle()

        for cat in [rep.concepts, rep.phrases, rep.loops, rep.predictions,
                    rep.hypotheses, rep.theories, rep.questions, rep.dreams,
                    rep.investigations, rep.experiments]:
            for item in cat:
                if getattr(item, "id", None):
                    unique_structures.add(item.id)

        hypotheses_series.append(len(rep.hypotheses))
        theories_series.append(len(rep.theories))
        questions_series.append(len(rep.questions))
        experiments_series.append(len(rep.experiments))

    duration = round(time.perf_counter() - t0, 2)
    mem.close()
    db.unlink(missing_ok=True)

    return {
        "arm": "passive_observation",
        "cycles": cycles,
        "seconds": duration,
        "inventory_total": len(unique_structures),
        "mean_hypotheses": round(sum(hypotheses_series) / max(len(hypotheses_series), 1), 2),
        "mean_theories": round(sum(theories_series) / max(len(theories_series), 1), 2),
        "mean_questions": round(sum(questions_series) / max(len(questions_series), 1), 2),
        "mean_experiments": round(sum(experiments_series) / max(len(experiments_series), 1), 2),
        "questions_closed": 0,
        "interventions_executed": 0,
    }


def run_active_arm(cycles: int) -> dict[str, Any]:
    db = temp_db("active_benchmark_active.db")
    if db.exists():
        db.unlink()

    mem = MemoryService(str(db))
    svc = SleepService(mem)
    world = ReactiveWorld()
    loop = ActiveInquiryLoop(mem, svc, world, events_per_step=5)

    unique_structures: set[str] = set()
    theories_series: list[int] = []
    questions_series: list[int] = []
    experiments_series: list[int] = []
    hypotheses_series: list[int] = []
    total_interventions = 0
    total_validated = 0
    total_refuted = 0
    total_closed_questions = 0

    t0 = time.perf_counter()
    for _ in range(cycles):
        rep, inquiry = loop.step_and_sleep()

        for cat in [rep.concepts, rep.phrases, rep.loops, rep.predictions,
                    rep.hypotheses, rep.theories, rep.questions, rep.dreams,
                    rep.investigations, rep.experiments]:
            for item in cat:
                if getattr(item, "id", None):
                    unique_structures.add(item.id)

        hypotheses_series.append(len(rep.hypotheses))
        theories_series.append(len(rep.theories))
        questions_series.append(len(rep.questions))
        experiments_series.append(len(rep.experiments))
        total_interventions += inquiry.experiments_executed
        total_validated += inquiry.experiments_validated
        total_refuted += inquiry.experiments_refuted
        total_closed_questions += inquiry.questions_closed

    duration = round(time.perf_counter() - t0, 2)
    mem.close()
    db.unlink(missing_ok=True)

    return {
        "arm": "active_inquiry",
        "cycles": cycles,
        "seconds": duration,
        "inventory_total": len(unique_structures),
        "mean_hypotheses": round(sum(hypotheses_series) / max(len(hypotheses_series), 1), 2),
        "mean_theories": round(sum(theories_series) / max(len(theories_series), 1), 2),
        "mean_questions": round(sum(questions_series) / max(len(questions_series), 1), 2),
        "mean_experiments": round(sum(experiments_series) / max(len(experiments_series), 1), 2),
        "interventions_executed": total_interventions,
        "experiments_validated": total_validated,
        "experiments_refuted": total_refuted,
        "questions_closed": total_closed_questions,
    }


def main():
    parser = argparse.ArgumentParser(description="Active Inquiry Benchmark (Law IV)")
    parser.add_argument("--cycles", type=int, default=150, help="Cycles per arm")
    args = parser.parse_args()

    print(f"Running Passive Observation arm ({args.cycles} cycles) ...")
    passive_res = run_passive_arm(args.cycles)
    print(f"  Passive Inventory: {passive_res['inventory_total']}, duration: {passive_res['seconds']}s")

    print(f"Running Active Inquiry arm ({args.cycles} cycles) ...")
    active_res = run_active_arm(args.cycles)
    print(f"  Active Inventory: {active_res['inventory_total']}, Interventions: {active_res['interventions_executed']}, duration: {active_res['seconds']}s")

    payload = {
        "kind": "active_inquiry_benchmark",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cycles": args.cycles,
        "passive": passive_res,
        "active": active_res,
        "delta_inventory": active_res["inventory_total"] - passive_res["inventory_total"],
        "delta_inventory_pct": round(
            (active_res["inventory_total"] - passive_res["inventory_total"])
            / max(passive_res["inventory_total"], 1) * 100, 2
        ),
    }

    out_path = REPO / "docs" / "active_inquiry_benchmark.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(engine_stamp.stamp(payload), f, indent=2)
    print(f"Wrote active inquiry benchmark to {out_path}")


if __name__ == "__main__":
    main()
