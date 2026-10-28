"""Probe Gate 13 (Sufficiency Gate) across seeds.

Uses the identical engine stepping and event processing as acquisition_runner.py:
  - mem = MemoryService(scratch_db_path)
  - svc = SleepService(mem)
  - mem.store(events[i], event_type="observe", source=source)
  - svc.run_sleep_cycle() every epc events
  - structure_edges(svc._load_prior_candidates()) deduplicated
  - evaluated against world_edges (_world_compositional_edges)

Standard library only. Scratch DB only. Engine files untouched.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.acquisition_compositional import (
    generate_compositional_world,
    PHASE_WARMUP,
    PHASE_ACQUISITION,
)
from benchmarks.acquisition_harness import (
    SUFFICIENCY_THRESHOLD,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import (
    _world_compositional_edges,
    structure_edges,
    EVENTS_PER_CYCLE,
)
from organica.memory import MemoryService
from organica.sleep import SleepService


def check_seed_gate_13(
    seed: int,
    cycles_to_run: int = 110,
    epc: int = EVENTS_PER_CYCLE,
) -> dict:
    world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=epc)
    events = world["events"]
    trainable = world["trainable"]
    warm_lo, warm_hi = PHASE_WARMUP
    acq_lo, acq_hi = PHASE_ACQUISITION

    world_edges = _world_compositional_edges(world)

    scratch_db_path = _make_scratch_db(f"probe_gate13_{seed}")
    try:
        mem = MemoryService(str(scratch_db_path))
        svc = SleepService(mem)

        # Replicate acquisition loop from acquisition_runner.py (lines 543-555)
        for i in range(acq_hi * epc):
            in_acq = (acq_lo * epc <= i < acq_hi * epc)
            if in_acq and not trainable[i]:
                continue
            source = "env_acq" if in_acq else "env"
            mem.store(events[i], event_type="observe", source=source)
            if (i + 1) % epc == 0:
                svc.run_sleep_cycle()

        # Gate 13 computation exactly matching runner (lines 564-588)
        frozen_cands = svc._load_prior_candidates()
        asserted_rows = structure_edges(frozen_cands)
        asserted_edges = set((u, v) for u, targets in asserted_rows.items() for v in targets)
        org_temporal_edges = set((ft, tt) for ft, tt, _cnt in mem.temporal_edges(min_count=1))

        covered_asserted = world_edges & asserted_edges
        covered_temporal = world_edges & org_temporal_edges

        asserted_coverage = len(covered_asserted) / len(world_edges) if world_edges else 0.0
        temporal_coverage = len(covered_temporal) / len(world_edges) if world_edges else 0.0

        cands_by_type = {}
        for c in frozen_cands:
            t = c.get("type", "unknown")
            cands_by_type[t] = cands_by_type.get(t, 0) + 1

        return {
            "seed": seed,
            "passed": (asserted_coverage >= SUFFICIENCY_THRESHOLD),
            "asserted_coverage": asserted_coverage,
            "temporal_coverage": temporal_coverage,
            "covered_asserted": len(covered_asserted),
            "covered_temporal": len(covered_temporal),
            "world_edges": len(world_edges),
            "unique_cands": len(asserted_rows),
            "raw_cands": len(frozen_cands),
            "cands_by_type": cands_by_type,
        }
    finally:
        try:
            scratch_db_path.unlink(missing_ok=True)
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Probe Gate 13 across seeds")
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=[20261101, 20261102, 20261103, 20261104, 20261105],
    )
    args = parser.parse_args()

    print(f"Probing Gate 13 across {len(args.seeds)} seeds: {args.seeds}")
    print(f"Threshold: {SUFFICIENCY_THRESHOLD:.2f}\n")
    print(
        f"{'Seed':<10} {'Asserted':<12} {'Temporal':<12} {'Pass?':<8} "
        f"{'Asserted Edges':<16} {'Temp Edges':<14} {'Time (s)'}"
    )
    print("-" * 80)

    for seed in args.seeds:
        t0 = time.time()
        res = check_seed_gate_13(seed)
        elapsed = time.time() - t0
        cov_str = f"{res['asserted_coverage']:.4f}"
        raw_str = f"{res['temporal_coverage']:.4f}"
        pass_str = "PASS" if res["passed"] else "FAIL"
        edge_ratio = f"{res['covered_asserted']}/{res['world_edges']}"
        temp_ratio = f"{res['covered_temporal']}/{res['world_edges']}"
        print(
            f"{seed:<10} {cov_str:<12} {raw_str:<12} {pass_str:<8} "
            f"{edge_ratio:<16} {temp_ratio:<14} {elapsed:.1f}s"
        )


if __name__ == "__main__":
    main()
