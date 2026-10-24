"""Pilot: recover known latent-cause feature pairs from a synthetic world.

Hidden labels are held by the generator and used only by the scorer. Organica
and two graph baselines receive the same first 200 cycles; recovered undirected
feature pairs are scored against the generator's same-cause pair set.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.ablation_metrics import edges_implied_by_structures  # noqa: E402
from organica.ground_truth_worlds import generate_cause_world  # noqa: E402
from organica.memory import MemoryService, _extract_tags  # noqa: E402
from organica.paths import temp_db  # noqa: E402
from organica.sleep import SleepService  # noqa: E402
from organica.streams import EVENTS_PER_CYCLE  # noqa: E402

TRAIN_CYCLES = 200
MIN_EDGE_COUNT = 5


def _undirected(edges: dict[str, set[str]]) -> set[tuple[str, str]]:
    return {tuple(sorted((a, b))) for a, targets in edges.items()
            for b in targets if a != b}


def _score(predicted: set[tuple[str, str]], gold: set[tuple[str, str]]) -> dict:
    tp = len(predicted & gold)
    fp = len(predicted - gold)
    fn = len(gold - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positive": tp, "false_positive": fp, "false_negative": fn,
        "precision": round(precision, 6), "recall": round(recall, 6),
        "f1": round(f1, 6), "predicted_pairs": len(predicted),
        "gold_pairs": len(gold),
    }


def run(seed: int = 20261023) -> dict:
    world = generate_cause_world(seed=seed)
    cut = TRAIN_CYCLES * EVENTS_PER_CYCLE
    train = world["events"][:cut]
    db = temp_db("ground_truth_recovery.db")
    db.unlink(missing_ok=True)
    mem = MemoryService(db_path=str(db))
    svc = SleepService(mem)
    report = None
    try:
        for cycle in range(TRAIN_CYCLES):
            for event in train[cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]:
                mem.store(event, event_type="event", source=f"cycle:{cycle}")
            report = svc.run_sleep_cycle()

        structures = []
        if report:
            for name in ("concepts", "phrases", "loops", "predictions", "anomalies",
                         "meta_concepts", "processes", "workflow_concepts", "hypotheses",
                         "theories", "questions", "dreams", "investigations", "experiments"):
                structures.extend(asdict(item) for item in getattr(report, name, []))
        organica_pairs = _undirected(edges_implied_by_structures(structures))

        cooc_pairs = {tuple(sorted((a, b))) for a, b, count in mem.cooccurrences(MIN_EDGE_COUNT)
                      if a != b}
        temporal = {}
        for a, b, count in mem.temporal_edges(MIN_EDGE_COUNT):
            if a != b:
                temporal.setdefault(a, set()).add(b)
        markov_pairs = _undirected(temporal)
    finally:
        mem.close()
        db.unlink(missing_ok=True)

    gold = {tuple(pair) for pair in world["gold_same_cause_pairs"]}
    predicted_tags = {tag for event in train for tag in _extract_tags(event)}
    return {
        "protocol": {
            "train_cycles": TRAIN_CYCLES,
            "test_cycles_not_ingested": world["config"]["cycles"] - TRAIN_CYCLES,
            "events_per_cycle": EVENTS_PER_CYCLE,
            "seed": seed,
            "hidden_cause_and_regime_labels_ingested": False,
            "pair_threshold": MIN_EDGE_COUNT,
            "recovery_target": "undirected same-latent-cause pairs among the observable cause features",
        },
        "world": {k: world[k] for k in ("config", "cause_features", "noise_features")},
        "training": {
            "events": len(train), "observed_tags": sorted(predicted_tags),
            "hidden_causes_seen": sorted(set(world["hidden_causes"][:cut])),
            "regime_switches_seen": sorted(set(world["hidden_regimes"][:cut])),
        },
        "gold_pairs": sorted(gold),
        "results": [
            {"model": "organica_surviving_structures", **_score(organica_pairs, gold)},
            {"model": "same_event_cooccurrence", **_score(cooc_pairs, gold)},
            {"model": "temporal_transition_graph", **_score(markov_pairs, gold)},
        ],
        "limitations": [
            "Single seed; no run-to-run uncertainty estimate.",
            "The generator's feature families are cleanly separable; recovery is easier than an ambiguous natural world.",
            "Pairwise co-cause recovery is not proof of causal intervention knowledge.",
            "The final 100 cycles are not ingested; this pilot scores structural recovery from training data, not held-out prediction.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--out", default=str(REPO / "docs" / "ground_truth_recovery.json"))
    args = parser.parse_args()
    result = run(args.seed)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
