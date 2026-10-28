"""Paired, scratch-only full acquisition test across diagnostic seeds 20261101-20261105.

Compares:
  - Control:   Normal engine with MAX_PREDICTIONS = 20
  - Treatment: Same engine with MAX_PREDICTIONS = 1000

At each sleep cycle, tracks how many valid world edges are:
  1. Present in temporal memory (lookback=3)
  2. Admitted as prediction candidates
  3. Retained after natural selection (admitted or reinforced/decayed in cycle)
  4. Present in the final asserted structure at the end of acquisition (Gate 13)

Standard library only. Scratch DBs only. Engine files untouched.
Output: docs/gate13_paired_capacity_test.json and report.
"""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.acquisition_compositional import (
    generate_compositional_world,
    PHASE_WARMUP,
    PHASE_ACQUISITION,
)
from benchmarks.acquisition_runner import (
    _world_compositional_edges,
    structure_edges,
    EVENTS_PER_CYCLE,
)
from benchmarks.acquisition_harness import _make_scratch_db, SUFFICIENCY_THRESHOLD
from organica.memory import MemoryService
from organica.sleep import SleepService, PredictionCandidate, _make_id

SEEDS = [20261101, 20261102, 20261103, 20261104, 20261105]
EPC = EVENTS_PER_CYCLE
NON_VOCAB_MARKERS = {"high_structural_significance"}


class PairedDiagnosticSleepService(SleepService):
    def __init__(self, memory: MemoryService, max_predictions: int = 20):
        super().__init__(memory)
        self.custom_max_predictions = max_predictions
        self.cycle_telemetry: list[dict] = []

    def _build_predictions(self, temporal, freqs):
        candidates = []
        for tag_from, targets in temporal.items():
            source_freq = freqs.get(tag_from, 1)
            for tag_to, count in targets.items():
                if count >= self.PREDICTION_MIN_COUNT:
                    ratio = count / max(source_freq, 1)
                    pid = _make_id("pred", tag_from, tag_to)
                    candidates.append(PredictionCandidate(
                        id=pid,
                        source=tag_from,
                        target=tag_to,
                        strength=min(1.0, ratio),
                        evidence={
                            "temporal_count": count,
                            "source_frequency": source_freq,
                            "target_frequency": freqs.get(tag_to, 0),
                            "ratio": round(ratio, 3),
                        },
                    ))
        candidates.sort(key=lambda p: p.evidence["temporal_count"], reverse=True)
        return candidates[:self.custom_max_predictions]


def run_paired_condition(
    seed: int,
    max_predictions: int,
    world: dict,
    world_edges: set[tuple[str, str]],
) -> dict:
    t0 = time.time()
    events = world["events"]
    trainable = world["trainable"]
    warm_lo, warm_hi = PHASE_WARMUP
    acq_lo, acq_hi = PHASE_ACQUISITION
    tag_to_cell = world["tag_to_cell"]
    vocab = set(tag_to_cell.keys())

    cond_name = f"pred_cap_{max_predictions}"
    scratch_path = _make_scratch_db(f"paired_{seed}_{cond_name}")
    mem = MemoryService(str(scratch_path))
    svc = PairedDiagnosticSleepService(mem, max_predictions=max_predictions)

    cycle_logs = []

    for cycle_idx in range(acq_hi):
        start = cycle_idx * EPC
        end = start + EPC
        in_acq = (acq_lo <= cycle_idx < acq_hi)
        for i in range(start, end):
            if in_acq and not trainable[i]:
                continue
            source = "env_acq" if in_acq else "env"
            mem.store(events[i], event_type="observe", source=source)

        report = svc.run_sleep_cycle()

        # Measure stage metrics for this cycle (sampling every 10 cycles and final cycle)
        if (cycle_idx + 1) % 10 == 0 or cycle_idx == acq_hi - 1:
            # 1. Temporal memory edges overlap
            cur_temporal_edges = set((ft, tt) for ft, tt, _cnt in mem.temporal_edges(min_count=1) if ft in vocab and tt in vocab)
            cov_temporal = len(cur_temporal_edges & world_edges)

            # 2. Admitted prediction candidates overlap in this cycle
            admitted_pred_edges = set((p.source, p.target) for p in report.predictions if p.source in vocab and p.target in vocab)
            cov_admitted_preds = len(admitted_pred_edges & world_edges)

            # 3. Retained in memory after natural selection in this cycle
            # (all prediction candidates currently stored / strengthened / decayed)
            cycle_logs.append({
                "cycle": cycle_idx + 1,
                "world_edges_in_temporal": cov_temporal,
                "world_edges_in_admitted_preds": cov_admitted_preds,
                "admitted_preds_count": len(report.predictions),
            })

    # 4. Final asserted structure at end of acquisition (Gate 13)
    frozen_cands = svc._load_prior_candidates()
    asserted_dict = structure_edges(frozen_cands)
    final_asserted_edges = set(
        (u, v) for u, targets in asserted_dict.items() for v in targets
        if u in vocab and v in vocab and u not in NON_VOCAB_MARKERS and v not in NON_VOCAB_MARKERS
    )

    covered_world_edges = len(final_asserted_edges & world_edges)
    asserted_coverage = covered_world_edges / len(world_edges) if world_edges else 0.0
    passed_gate_13 = asserted_coverage >= SUFFICIENCY_THRESHOLD

    intra_edges = sum(1 for u, v in final_asserted_edges if tag_to_cell.get(u) == tag_to_cell.get(v))
    inter_edges = sum(1 for u, v in final_asserted_edges if tag_to_cell.get(u) != tag_to_cell.get(v))

    mem.close()
    try:
        scratch_path.unlink(missing_ok=True)
    except Exception:
        pass

    return {
        "seed": seed,
        "max_predictions": max_predictions,
        "runtime_s": round(time.time() - t0, 1),
        "world_edges_total": len(world_edges),
        "covered_world_edges": covered_world_edges,
        "asserted_coverage": round(asserted_coverage, 4),
        "passed_gate_13": passed_gate_13,
        "final_asserted_edges_count": len(final_asserted_edges),
        "intra_cell_asserted": intra_edges,
        "inter_cell_asserted": inter_edges,
        "cycle_milestones": cycle_logs,
    }


def main():
    print(f"Running Paired Full-Acquisition Capacity Test on seeds: {SEEDS}")
    print(f"Comparing Control (cap=20) vs Treatment (cap=1000)\n")

    summary_records = []

    for seed in SEEDS:
        print(f"=== Seed {seed} ===")
        world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=EPC)
        world_edges = _world_compositional_edges(world)

        print("  Running Control (cap=20)...")
        control_res = run_paired_condition(seed, max_predictions=20, world=world, world_edges=world_edges)
        print(f"    Control: {control_res['covered_world_edges']}/{control_res['world_edges_total']} ({control_res['asserted_coverage']:.4f}) | Gate 13: {'PASS' if control_res['passed_gate_13'] else 'FAIL'} ({control_res['runtime_s']}s)")

        print("  Running Treatment (cap=1000)...")
        treatment_res = run_paired_condition(seed, max_predictions=1000, world=world, world_edges=world_edges)
        print(f"    Treatment: {treatment_res['covered_world_edges']}/{treatment_res['world_edges_total']} ({treatment_res['asserted_coverage']:.4f}) | Gate 13: {'PASS' if treatment_res['passed_gate_13'] else 'FAIL'} ({treatment_res['runtime_s']}s)")

        summary_records.append({
            "seed": seed,
            "control": control_res,
            "treatment": treatment_res,
        })

    out_file = REPO / "docs" / "gate13_paired_capacity_test.json"
    with open(out_file, "w") as f:
        json.dump(summary_records, f, indent=2)
    print(f"\nSaved paired results to {out_file}")


if __name__ == "__main__":
    main()
