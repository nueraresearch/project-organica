"""Diagnostic sweep testing the effect of prediction capacity (MAX_PREDICTIONS)
on full-cycle sleep, selection, and persistence across diagnostic seeds 20261101-20261105.

Evaluates caps: [20 (default), 40, 80, None (uncapped)]
Runs full acquisition (cycles 0-109) in scratch DBs under each cap.
Measures final deduplicated asserted-structure coverage against Gate 13 (0.50 threshold).

Standard library only. Scratch DBs only. Engine files untouched.
Output: docs/gate13_capacity_sweep.json
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
from benchmarks.acquisition_harness import _make_scratch_db
from organica.memory import MemoryService
from organica.sleep import SleepService

SEEDS = [20261101, 20261102, 20261103, 20261104, 20261105]
CAPS = [20, 40, 80, None]
EPC = EVENTS_PER_CYCLE
NON_VOCAB_MARKERS = {"high_structural_significance"}


class DiagnosticSleepService(SleepService):
    """Subclass varying MAX_PREDICTIONS for diagnostic evaluation only.
    Leaves organica/sleep.py frozen.
    """
    def __init__(self, memory: MemoryService, max_predictions: int | None = 20):
        super().__init__(memory)
        self.diagnostic_max_predictions = max_predictions

    def _build_predictions(self, temporal, freqs):
        cands = super()._build_predictions(temporal, freqs)
        if self.diagnostic_max_predictions is None:
            # Recompute without truncation
            from organica.sleep import _make_id, PredictionCandidate
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
            return candidates
        elif self.diagnostic_max_predictions != 20:
            from organica.sleep import _make_id, PredictionCandidate
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
            return candidates[:self.diagnostic_max_predictions]
        return cands


def run_pipeline(seed: int, cap: int | None) -> dict:
    t0 = time.time()
    world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=EPC)
    events = world["events"]
    trainable = world["trainable"]
    warm_lo, warm_hi = PHASE_WARMUP
    acq_lo, acq_hi = PHASE_ACQUISITION

    world_edges = _world_compositional_edges(world)
    tag_to_cell = world["tag_to_cell"]
    vocab = set(tag_to_cell.keys())

    cap_label = f"cap_{cap}" if cap is not None else "uncapped"
    scratch_path = _make_scratch_db(f"sweep_{seed}_{cap_label}")
    mem = MemoryService(str(scratch_path))
    svc = DiagnosticSleepService(mem, max_predictions=cap)

    for i in range(acq_hi * EPC):
        in_acq = (acq_lo * EPC <= i < acq_hi * EPC)
        if in_acq and not trainable[i]:
            continue
        source = "env_acq" if in_acq else "env"
        mem.store(events[i], event_type="observe", source=source)
        if (i + 1) % EPC == 0:
            svc.run_sleep_cycle()

    frozen_cands = svc._load_prior_candidates()
    asserted_dict = structure_edges(frozen_cands)
    asserted_edges = set(
        (u, v) for u, targets in asserted_dict.items() for v in targets
        if u in vocab and v in vocab and u not in NON_VOCAB_MARKERS and v not in NON_VOCAB_MARKERS
    )

    covered = asserted_edges & world_edges
    cov = len(covered) / len(world_edges) if world_edges else 0.0

    intra = sum(1 for u, v in asserted_edges if tag_to_cell.get(u) == tag_to_cell.get(v))
    inter = sum(1 for u, v in asserted_edges if tag_to_cell.get(u) != tag_to_cell.get(v))

    mem.close()
    try:
        scratch_path.unlink(missing_ok=True)
    except Exception:
        pass

    return {
        "seed": seed,
        "cap": cap,
        "runtime_s": round(time.time() - t0, 1),
        "total_asserted_edges": len(asserted_edges),
        "covered_world_edges": len(covered),
        "world_edges": len(world_edges),
        "asserted_coverage": round(cov, 4),
        "passed_gate_13": cov >= 0.50,
        "intra_cell_edges": intra,
        "inter_cell_edges": inter,
    }


def main():
    print(f"Running Capacity Sweep across seeds: {SEEDS} and caps: {CAPS}...")
    results = defaultdict(dict)
    for s in SEEDS:
        print(f"\n--- Seed {s} ---")
        for cap in CAPS:
            cap_str = str(cap) if cap is not None else "None"
            res = run_pipeline(s, cap)
            results[s][cap_str] = res
            print(f"  Cap={cap_str:<4}: Coverage={res['covered_world_edges']:>3}/{res['world_edges']} ({res['asserted_coverage']:.4f}) | Gate 13: {'PASS' if res['passed_gate_13'] else 'FAIL'} | Intra={res['intra_cell_edges']:<3} Inter={res['inter_cell_edges']:<3} ({res['runtime_s']}s)")

    out_file = REPO / "docs" / "gate13_capacity_sweep.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved capacity sweep results to {out_file}")


if __name__ == "__main__":
    main()
