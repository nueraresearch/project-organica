"""
benchmarks/cross_context_reuse_benchmark.py
-------------------------------------------
Cross-Context Structural Reuse Experiment (CCRE).

Evaluates whether persistent developmental structures formed in Context A
accelerate the acquisition of an isomorphic relational structure in Context B
without relearning, under strict R1-R5 operational criteria:
  - R1: Observed formation in Context A
  - R2: No direct reteaching (Context B has disjoint surface vocabulary)
  - R3: Accelerated acquisition (Transfer Ratio TR = baseline_cycles / transfer_cycles > 1.0)
  - R4: Traceable provenance linking transfer to Context A structure
  - R5: Transfer persistence (TP >= 20 cycles surviving ongoing sleep selection)

Arms:
  - Treatment: Context A -> Context B (retains consolidated memory)
  - Control 1: Naïve Baseline (enters Context B directly, fresh memory)
  - Control 2: Ablation / Pruned (Context A -> excise target schema -> Context B)
  - Control 3: Orthogonal Volume Control (Context A with randomized/flat schema -> Context B)

Acquisition is scored under the earned-evidence contract: a B_source -> B_target
prediction counts only when its own temporal_count clears PREDICTION_MIN_COUNT.
A schema prior may reorder candidates; it may never supply evidence
(docs/DECISION-EARNED-SCHEMA-PRIMING.md D1-D4).

Usage:
  python benchmarks/cross_context_reuse_benchmark.py --seeds 1 --seed_offset 0 \
      --phase_a_cycles 40 --phase_b_cycles 40 --out_path .scratch/ccre_0.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService
from organica.paths import temp_db
from organica.sleep import SleepService

# Disjoint vocabularies for Context A, Context B, and Control C
VOCAB_A = {
    "source": ("amber", "birch", "cedar", "maple"),
    "target": ("indigo", "fern", "willow", "yarrow"),
}

VOCAB_B = {
    "source": ("quartz", "crystal", "topaz", "granite"),
    "target": ("plasma", "nebula", "pulsar", "cosmos"),
}

VOCAB_C = {
    "source": ("copper", "bronze", "iron", "nickel"),
    "target": ("silver", "gold", "platinum", "cobalt"),
}


def generate_world_events(vocab: dict[str, tuple[str, ...]], n_cycles: int,
                          events_per_cycle: int = 5, transition_prob: float = 0.85,
                          seed: int = 42) -> list[list[str]]:
    """Generate sequential events with structured Markov transitions between source and target groups."""
    rng = random.Random(seed)
    cycles_events: list[list[str]] = []
    
    current_group = "source"
    for _ in range(n_cycles):
        cycle: list[str] = []
        for _ in range(events_per_cycle):
            # Select 2 distinct tags from the current group
            tags = rng.sample(vocab[current_group], 2)
            content = f"reading {tags[0]} with {tags[1]}"
            cycle.append(content)
            
            # Transition rule: source -> target with high prob, target -> source
            if current_group == "source":
                if rng.random() < transition_prob:
                    current_group = "target"
            else:
                if rng.random() < transition_prob:
                    current_group = "source"
        cycles_events.append(cycle)
    return cycles_events


def run_experiment_cell(arm: str, seed: int, phase_a_cycles: int = 60,
                        phase_b_cycles: int = 60) -> dict[str, Any]:
    db = temp_db(f"ccre_{arm}_{seed}_{time.time_ns()}.db")
    if db.exists():
        db.unlink()
        
    mem = MemoryService(str(db))
    svc = SleepService(mem)
    
    # Target pair to monitor in Context B
    b_source_tags = set(VOCAB_B["source"])
    b_target_tags = set(VOCAB_B["target"])
    
    cycles_to_acquire: int | None = None
    persistence_counter = 0
    acquired = False
    primed_predictions = 0
    target_rank_at_acquire: int | None = None
    
    try:
        # Phase A
        if arm in ("treatment", "control_pruned"):
            events_a = generate_world_events(VOCAB_A, phase_a_cycles, seed=seed)
            for c, cycle_events in enumerate(events_a):
                with mem.batch():
                    for ev in cycle_events:
                        mem.store(ev, event_type="observe", source="env:A")
                svc.run_sleep_cycle()
                
            if arm == "control_pruned":
                # Excise all Phase A predictions/hypotheses to isolate latent state
                mem._conn.execute("DELETE FROM precedes")
                mem._conn.execute("DELETE FROM events WHERE event_type = 'sleep'")
                mem._conn.commit()
                if getattr(svc, "_prior_cache", None):
                    svc._prior_cache.clear()
                svc._prior_cache = None
                    
        elif arm == "control_orthogonal":
            # Context C: random transition probability (0.50)
            events_c = generate_world_events(VOCAB_C, phase_a_cycles, transition_prob=0.50, seed=seed)
            for c, cycle_events in enumerate(events_c):
                with mem.batch():
                    for ev in cycle_events:
                        mem.store(ev, event_type="observe", source="env:C")
                svc.run_sleep_cycle()
                
        # Phase B: All arms enter Context B
        events_b = generate_world_events(VOCAB_B, phase_b_cycles, transition_prob=0.85, seed=seed + 1000)
        
        for c, cycle_events in enumerate(events_b):
            with mem.batch():
                for ev in cycle_events:
                    mem.store(ev, event_type="observe", source="env:B")
            rep = svc.run_sleep_cycle()
            
            # Earned-evidence integrity check (D1/D4): a prediction's count must be
            # its observed count. An inflated count is a hard failure, not a measurement.
            for p in rep.predictions:
                observed = p.evidence.get("temporal_count")
                reported = p.evidence.get("effective_count", observed)
                if observed is None or reported != observed:
                    raise AssertionError(
                        f"{arm}/{seed}: prediction {p.source}->{p.target} reports an "
                        f"unaudited count (observed={observed!r}, reported={reported!r}); "
                        "acquisition must be earned by unboosted evidence"
                    )

            primed_predictions += sum(
                1 for p in rep.predictions if p.evidence.get("schema_prior")
            )

            # Acquisition (D4): raw evidence, not a prior's substitution.
            target_index = None
            for idx, p in enumerate(rep.predictions):
                if (
                    p.source in b_source_tags
                    and p.target in b_target_tags
                    and p.strength >= 0.5
                    and int(p.evidence.get("temporal_count", 0)) >= svc.PREDICTION_MIN_COUNT
                ):
                    target_index = idx
                    break
            has_target = target_index is not None
            
            if has_target:
                if not acquired:
                    acquired = True
                    cycles_to_acquire = c + 1
                    target_rank_at_acquire = (target_index or 0) + 1
                persistence_counter += 1
            else:
                if acquired:
                    # Dropped out of active retention
                    pass
                    
        if cycles_to_acquire is None:
            cycles_to_acquire = phase_b_cycles + 1
            
        return {
            "arm": arm,
            "seed": seed,
            "acquired": acquired,
            "cycles_to_acquire": cycles_to_acquire,
            "persistence_cycles": persistence_counter,
            "primed_predictions": primed_predictions,
            "target_rank_at_acquire": target_rank_at_acquire,
        }
    finally:
        mem.close()
        db.unlink(missing_ok=True)


def build_summary(results, seeds, phase_a_cycles, phase_b_cycles, total_seconds):
    """Assemble the artifact from per-arm cell results.

    A function rather than inline code so a chunked run (several processes, one seed
    range each) is assembled by exactly the code that assembles a single-process run.
    """
    n = len(seeds)
    mean_naive = sum(r["cycles_to_acquire"] for r in results["control_naive"]) / n
    mean_treatment = sum(r["cycles_to_acquire"] for r in results["treatment"]) / n
    mean_pruned = sum(r["cycles_to_acquire"] for r in results["control_pruned"]) / n
    mean_ortho = sum(r["cycles_to_acquire"] for r in results["control_orthogonal"]) / n

    tr_treatment = round(mean_naive / max(mean_treatment, 1e-6), 3)
    tr_pruned = round(mean_naive / max(mean_pruned, 1e-6), 3)
    tr_ortho = round(mean_naive / max(mean_ortho, 1e-6), 3)

    primed = {arm: sum(r.get("primed_predictions", 0) for r in rows)
              for arm, rows in results.items()}
    ranks = [r["target_rank_at_acquire"] for r in results["treatment"]
             if r.get("target_rank_at_acquire")]

    if tr_treatment > 1.25 and tr_treatment > tr_pruned and tr_treatment > tr_ortho:
        verdict = "TRANSFER_DEMONSTRATED_UNDER_EARNED_EVIDENCE"
    elif tr_treatment <= 1.05 and primed.get("treatment", 0) > 0:
        verdict = "STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE"
    else:
        verdict = "NULL_UNDER_EARNED_EVIDENCE"

    return {
        "kind": "cross_context_reuse_benchmark",
        "protocol": "earned-evidence (docs/DECISION-EARNED-SCHEMA-PRIMING.md)",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seeds": list(seeds),
        "phase_a_cycles": phase_a_cycles,
        "phase_b_cycles": phase_b_cycles,
        "total_seconds": total_seconds,
        "metrics": {
            "mean_cycles_naive": mean_naive,
            "mean_cycles_treatment": mean_treatment,
            "mean_cycles_pruned": mean_pruned,
            "mean_cycles_orthogonal": mean_ortho,
            "transfer_ratio_treatment": tr_treatment,
            "transfer_ratio_pruned": tr_pruned,
            "transfer_ratio_orthogonal": tr_ortho,
            "mean_tp_treatment": round(
                sum(r["persistence_cycles"] for r in results["treatment"]) / n, 2),
            "primed_predictions": primed,
            "treatment_target_rank_at_acquire": ranks,
            "reusable_knowledge_verdict": verdict,
        },
        "per_arm_results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Cross-Context Reuse Benchmark (CCRE)")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds")
    parser.add_argument("--phase_a_cycles", type=int, default=40, help="Cycles in Phase A")
    parser.add_argument("--phase_b_cycles", type=int, default=40, help="Cycles in Phase B")
    parser.add_argument("--seed_offset", type=int, default=0,
                        help="Offset into the pre-assigned seed block")
    parser.add_argument("--out_path", type=str, default=None,
                        help="Artifact path (default docs/cross_context_reuse_benchmark.json)")
    args = parser.parse_args()

    seeds = [20261101 + args.seed_offset + i for i in range(args.seeds)]
    arms = ["treatment", "control_naive", "control_pruned", "control_orthogonal"]
    
    results: dict[str, list[dict[str, Any]]] = {arm: [] for arm in arms}
    
    print(f"Executing Cross-Context Reuse Experiment across {len(seeds)} seeds...")
    print(f"Phase A: {args.phase_a_cycles} cycles | Phase B: {args.phase_b_cycles} cycles")
    print("-" * 65)
    
    t0 = time.perf_counter()
    for arm in arms:
        print(f"Running arm: {arm:20s} ...", end="", flush=True)
        t_arm = time.perf_counter()
        for seed in seeds:
            res = run_experiment_cell(arm, seed, args.phase_a_cycles, args.phase_b_cycles)
            results[arm].append(res)
        dur = round(time.perf_counter() - t_arm, 2)
        mean_acq = round(sum(r["cycles_to_acquire"] for r in results[arm]) / len(seeds), 2)
        mean_tp = round(sum(r["persistence_cycles"] for r in results[arm]) / len(seeds), 2)
        print(f" Done ({dur}s) -> Mean Acq: {mean_acq:5.2f} cyc, Mean TP: {mean_tp:5.2f} cyc")
        
    total_time = round(time.perf_counter() - t0, 2)

    summary = build_summary(
        results, seeds, args.phase_a_cycles, args.phase_b_cycles, total_time,
    )
    tr_treatment = summary["metrics"]["transfer_ratio_treatment"]
    tr_pruned = summary["metrics"]["transfer_ratio_pruned"]
    tr_ortho = summary["metrics"]["transfer_ratio_orthogonal"]

    out_file = Path(args.out_path) if args.out_path else REPO / "docs" / "cross_context_reuse_benchmark.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("=" * 65)
    print(f"Results written to {out_file}")
    print(f"Transfer Ratio (Treatment vs Naïve): {tr_treatment}")
    print(f"Transfer Ratio (Pruned vs Naïve):    {tr_pruned}")
    print(f"Transfer Ratio (Orthogonal vs Naïve):{tr_ortho}")
    print(f"Verdict: {summary['metrics']['reusable_knowledge_verdict']}")


if __name__ == "__main__":
    main()
