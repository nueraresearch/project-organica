"""Counterfactual audit of acquisition structure coverage across seeds 20261101-20261105.

Investigates where the transition information is lost:
  1. Valid world-edge coverage in:
     - Raw temporal memory (lookback=3)
     - Direct 1-step predecessor transitions (lookback=1)
     - Individual candidate types: prediction_candidate, loop_candidate, process_candidate, etc.
     - Final projected graph (excluding non-vocabulary marker links like 'high_structural_significance')
  2. Capacity hypothesis test:
     - Recompute prediction candidates with and without the MAX_PREDICTIONS = 20 cap.
  3. Controlled breakdown of intra-cell vs inter-cell relations across representations.

Standard library only. Scratch databases only.
Output: docs/GATE13-PREFLIGHT-AUDIT.md and docs/gate13_counterfactual_audit.json
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
from benchmarks.ablation_metrics import edges_implied_by_structures
from benchmarks.acquisition_harness import _make_scratch_db
from organica.memory import MemoryService
from organica.sleep import SleepService

SEEDS = [20261101, 20261102, 20261103, 20261104, 20261105]
EPC = EVENTS_PER_CYCLE
NON_VOCAB_MARKERS = {"high_structural_significance"}


def audit_seed(seed: int) -> dict:
    t0 = time.time()
    world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=EPC)
    events = world["events"]
    trainable = world["trainable"]
    warm_lo, warm_hi = PHASE_WARMUP
    acq_lo, acq_hi = PHASE_ACQUISITION

    world_edges = _world_compositional_edges(world)
    tag_to_cell = world["tag_to_cell"]
    vocab = set(tag_to_cell.keys())

    scratch_path = _make_scratch_db(f"cf_audit_{seed}")
    mem = MemoryService(str(scratch_path))
    svc = SleepService(mem)

    # 1. Run acquisition
    for i in range(acq_hi * EPC):
        in_acq = (acq_lo * EPC <= i < acq_hi * EPC)
        if in_acq and not trainable[i]:
            continue
        source = "env_acq" if in_acq else "env"
        mem.store(events[i], event_type="observe", source=source)
        if (i + 1) % EPC == 0:
            svc.run_sleep_cycle()

    # 2. Raw temporal memory inspection
    raw_temporal_edges = set((ft, tt) for ft, tt, _cnt in mem.temporal_edges(min_count=1) if ft in vocab and tt in vocab)
    raw_temporal_cov = len(raw_temporal_edges & world_edges) / len(world_edges)

    # 3. Direct 1-step predecessor transitions (lookback = 1) from the actual observed event sequence
    step1_precedes = defaultdict(int)
    for i in range(1, acq_hi * EPC):
        prev_tags = events[i - 1].split()
        curr_tags = events[i].split()
        for a in prev_tags:
            for b in curr_tags:
                if a != b and a in vocab and b in vocab:
                    step1_precedes[(a, b)] += 1
    step1_edges = set(step1_precedes.keys())
    step1_cov = len(step1_edges & world_edges) / len(world_edges)

    # 4. Candidates from sleep
    raw_cands = svc._load_prior_candidates()
    # Deduplicate newest-first
    seen_ids = set()
    dedup_cands = []
    for c in raw_cands:
        cid = c.get("id")
        if cid and cid in seen_ids:
            continue
        if cid:
            seen_ids.add(cid)
        dedup_cands.append(c)

    # Breakdown by candidate type
    by_type = defaultdict(list)
    for c in dedup_cands:
        by_type[c.get("type", "unknown")].append(c)

    type_coverage = {}
    for ctype, c_list in by_type.items():
        type_edges_dict = edges_implied_by_structures(c_list)
        type_edges = set(
            (u, v) for u, targets in type_edges_dict.items() for v in targets
            if u in vocab and v in vocab and u not in NON_VOCAB_MARKERS and v not in NON_VOCAB_MARKERS
        )
        cov = len(type_edges & world_edges) / len(world_edges)
        intra = sum(1 for u, v in type_edges if tag_to_cell.get(u) == tag_to_cell.get(v))
        inter = sum(1 for u, v in type_edges if tag_to_cell.get(u) != tag_to_cell.get(v))
        type_coverage[ctype] = {
            "count": len(c_list),
            "edges_count": len(type_edges),
            "world_edge_overlap": len(type_edges & world_edges),
            "coverage": round(cov, 4),
            "intra_cell": intra,
            "inter_cell": inter,
        }

    # Final projected graph (filtered of markers)
    final_dict = structure_edges(dedup_cands)
    final_edges = set(
        (u, v) for u, targets in final_dict.items() for v in targets
        if u in vocab and v in vocab and u not in NON_VOCAB_MARKERS and v not in NON_VOCAB_MARKERS
    )
    final_cov = len(final_edges & world_edges) / len(world_edges)
    final_intra = sum(1 for u, v in final_edges if tag_to_cell.get(u) == tag_to_cell.get(v))
    final_inter = sum(1 for u, v in final_edges if tag_to_cell.get(u) != tag_to_cell.get(v))

    # 5. Capacity hypothesis test on prediction_candidate
    temp_table = svc._load_temporal()
    freqs = dict(mem.tag_frequencies())

    uncapped_cands = []
    for tag_from, targets in temp_table.items():
        if tag_from not in vocab:
            continue
        source_freq = freqs.get(tag_from, 1)
        for tag_to, count in targets.items():
            if tag_to not in vocab or tag_to == tag_from:
                continue
            if count >= svc.PREDICTION_MIN_COUNT:
                ratio = count / max(source_freq, 1)
                uncapped_cands.append({
                    "from": tag_from,
                    "to": tag_to,
                    "count": count,
                    "ratio": ratio,
                })

    uncapped_edges = set((c["from"], c["to"]) for c in uncapped_cands)
    uncapped_cov = len(uncapped_edges & world_edges) / len(world_edges)
    uncapped_intra = sum(1 for u, v in uncapped_edges if tag_to_cell.get(u) == tag_to_cell.get(v))
    uncapped_inter = sum(1 for u, v in uncapped_edges if tag_to_cell.get(u) != tag_to_cell.get(v))

    # Capped top 20
    sorted_uncapped = sorted(uncapped_cands, key=lambda c: c["count"], reverse=True)
    capped20_edges = set((c["from"], c["to"]) for c in sorted_uncapped[:20])
    capped20_cov = len(capped20_edges & world_edges) / len(world_edges)
    capped20_intra = sum(1 for u, v in capped20_edges if tag_to_cell.get(u) == tag_to_cell.get(v))
    capped20_inter = sum(1 for u, v in capped20_edges if tag_to_cell.get(u) != tag_to_cell.get(v))

    # Close DB and clean up
    mem.close()
    try:
        scratch_path.unlink(missing_ok=True)
    except Exception:
        pass

    return {
        "seed": seed,
        "runtime_s": round(time.time() - t0, 1),
        "raw_temporal_coverage": round(raw_temporal_cov, 4),
        "step1_temporal_coverage": round(step1_cov, 4),
        "final_projected_coverage": round(final_cov, 4),
        "final_projected_edges": {
            "total": len(final_edges),
            "intra_cell": final_intra,
            "inter_cell": final_inter,
            "world_edge_overlap": len(final_edges & world_edges),
        },
        "capacity_test_predictions": {
            "min_count_threshold": svc.PREDICTION_MIN_COUNT,
            "uncapped_candidates_count": len(uncapped_cands),
            "uncapped_coverage": round(uncapped_cov, 4),
            "uncapped_intra": uncapped_intra,
            "uncapped_inter": uncapped_inter,
            "capped20_coverage": round(capped20_cov, 4),
            "capped20_intra": capped20_intra,
            "capped20_inter": capped20_inter,
        },
        "per_candidate_type": type_coverage,
    }


def main():
    print(f"Running Counterfactual Acquisition Audit on seeds: {SEEDS}...")
    results = []
    for s in SEEDS:
        res = audit_seed(s)
        results.append(res)
        print(f"Seed {s}: RawCov={res['raw_temporal_coverage']:.2f} | FinalCov={res['final_projected_coverage']:.4f} | UncappedPredCov={res['capacity_test_predictions']['uncapped_coverage']:.4f} | Capped20PredCov={res['capacity_test_predictions']['capped20_coverage']:.4f} ({res['runtime_s']}s)")

    out_json = REPO / "docs" / "gate13_counterfactual_audit.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved raw JSON to {out_json}")


if __name__ == "__main__":
    main()
