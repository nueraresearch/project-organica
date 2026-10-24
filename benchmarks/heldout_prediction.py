"""Frozen-model, held-out next-tag prediction benchmark.

Train Organica and two lightweight graph baselines on the same first 200
cycles of the burst curriculum, then score cycles 201-300 without updating
any model during evaluation. Scores are micro precision, recall, F1, Brier
score, and binary log loss over known training tags. Unseen test tags are
reported separately as a novelty diagnostic.

This benchmark is an evaluation instrument, not a preregistered result. The
model definitions and scoring protocol should be frozen before interpreting
its first output.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService, _extract_tags
from organica.paths import temp_db
from organica.scale_streams import burst_stream, scale_designs, triangle_events
from organica.sleep import SleepService
from organica.streams import EVENTS_PER_CYCLE

TRAIN_CYCLES = 200
TEST_CYCLES = 100
DECAY_HALF_LIFE_CYCLES = 50
ALPHA = 0.5
EPSILON = 1e-9


def _transition_counts(events: list[str], *, window: int = 1,
                       half_life_events: float | None = None):
    """Return weighted positive and exposure counts for tag transitions."""
    positives: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    exposures: dict[str, float] = defaultdict(float)
    for i in range(len(events) - 1):
        nxt = set(_extract_tags(events[i + 1]))
        if not nxt:
            continue
        age = len(events) - 2 - i
        weight = (0.5 ** (age / half_life_events)
                  if half_life_events is not None else 1.0)
        for j in range(max(0, i - window + 1), i + 1):
            for source in set(_extract_tags(events[j])):
                exposures[source] += weight
                for target in nxt:
                    if source != target:
                        positives[source][target] += weight
    return positives, exposures


def _probability(positives, exposures, source: str, target: str) -> float:
    # Beta(0.5, 0.5) smoothing keeps both observed and absent edges finite.
    if source not in exposures:
        return 0.0
    return (positives.get(source, {}).get(target, 0.0) + ALPHA) / (
        exposures.get(source, 0.0) + 2 * ALPHA
    )


def _score(name: str, probability, contexts: list[list[str]],
           observations: list[list[str]], vocabulary: set[str]) -> dict:
    tp = fp = fn = 0
    brier = logloss = n = 0.0
    for ctx, obs in zip(contexts, observations):
        truth = set(obs) & vocabulary
        for source in ctx:
            for target in vocabulary:
                p = min(1 - EPSILON, max(EPSILON, probability(source, target)))
                y = int(target in truth and target != source)
                pred = p >= 0.5
                tp += int(pred and y)
                fp += int(pred and not y)
                fn += int(not pred and y)
                brier += (p - y) ** 2
                logloss -= y * math.log(p) + (1 - y) * math.log1p(-p)
                n += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "model": name, "threshold": 0.5, "tp": tp, "fp": fp, "fn": fn,
        "precision": round(precision, 6), "recall": round(recall, 6),
        "f1": round(f1, 6), "brier": round(brier / n, 6) if n else None,
        "log_loss": round(logloss / n, 6) if n else None,
        "scored_binary_labels": int(n),
    }


def run(seed: int = 20261023) -> dict:
    designs = scale_designs()
    core = designs["rung0"]["triangles"]
    stream = burst_stream(core, TRAIN_CYCLES + TEST_CYCLES,
                          burst_every=30, burst_len=8,
                          events_per_cycle=EVENTS_PER_CYCLE)
    cut = TRAIN_CYCLES * EVENTS_PER_CYCLE
    train_stream, test_stream = stream[:cut], stream[cut:]
    bootstrap = triangle_events(core)
    train_history = bootstrap + train_stream
    vocabulary = {tag for event in train_history for tag in _extract_tags(event)}

    # First-order Markov: current event tags -> next event tags.
    markov_pos, markov_exp = _transition_counts(train_history)
    markov = lambda a, b: _probability(markov_pos, markov_exp, a, b)

    # Recency-decayed temporal association: the same one-event context as the
    # Markov baseline, with old transition evidence exponentially downweighted.
    decay_pos, decay_exp = _transition_counts(
        train_history, window=1,
        half_life_events=DECAY_HALF_LIFE_CYCLES * EVENTS_PER_CYCLE)
    decayed = lambda a, b: _probability(decay_pos, decay_exp, a, b)

    db = temp_db("heldout_prediction.db")
    db.unlink(missing_ok=True)
    mem = MemoryService(db_path=str(db))
    svc = SleepService(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    try:
        for event in bootstrap:
            mem.store(event, event_type="event", source="seed:bootstrap")
        report = None
        for cycle in range(TRAIN_CYCLES):
            chunk = train_stream[cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]
            for event in chunk:
                mem.store(event, event_type="event", source=f"cycle:{cycle}")
            report = svc.run_sleep_cycle()
        organica_scores = {
            (p.source, p.target): float(p.strength)
            for p in (report.predictions if report else [])
        }
    finally:
        mem.close()
        db.unlink(missing_ok=True)

    organica = lambda a, b: organica_scores.get((a, b), 0.0)
    # Include the final training event as the context for the first test event.
    evaluation = train_stream[-1:] + test_stream
    contexts = [_extract_tags(e) for e in evaluation[:-1]]
    observations = [_extract_tags(e) for e in evaluation[1:]]
    test_tags = {tag for event in test_stream for tag in _extract_tags(event)}
    novel_tags = test_tags - vocabulary
    novel_occurrences = sum(
        len(set(_extract_tags(event)) & novel_tags) for event in test_stream
    )
    models = [
        ("organica_g1_predictions", organica),
        ("first_order_markov", markov),
        ("decayed_temporal_association", decayed),
    ]
    results_known = [_score(name, model, contexts, observations, vocabulary)
                     for name, model in models]
    results_open_vocab = [_score(name, model, contexts, observations,
                                 vocabulary | novel_tags)
                          for name, model in models]
    return {
        "protocol": {
            "train_cycles": TRAIN_CYCLES, "test_cycles": TEST_CYCLES,
            "events_per_cycle": EVENTS_PER_CYCLE, "seed": seed,
            "curriculum": "lattice_L1 core + burst_30, burst_len=8",
            "freeze_point": f"after cycle {TRAIN_CYCLES}; no test-time updates",
            "prediction_unit": "tag in current event predicts tag in next event",
            "primary_vocabulary": "tags seen in bootstrap or training stream",
            "f1_threshold": 0.5, "smoothing_alpha": ALPHA,
            "decay_half_life_cycles": DECAY_HALF_LIFE_CYCLES,
        },
        "novelty": {
            "test_only_tags": sorted(novel_tags),
            "test_only_tag_occurrences": novel_occurrences,
            "note": "Primary scores exclude unseen target tags; this count exposes that limitation.",
        },
        "results_known_training_tags": results_known,
        "results_including_test_only_tags": results_open_vocab,
        "limitations": [
            "Single deterministic seed; this is a pilot, not an uncertainty estimate.",
            "F1 uses a fixed 0.5 probability threshold; no threshold is tuned on test data.",
            "Organica's G1 strengths are treated as probabilities for Brier and log loss; calibration is not established.",
            "This is a synthetic curriculum and does not score latent causal structure.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--out", default=str(REPO / "docs" / "heldout_prediction.json"))
    args = parser.parse_args()
    result = run(args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
