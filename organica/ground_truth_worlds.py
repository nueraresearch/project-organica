"""Synthetic worlds with explicit latent-cause and regime ground truth.

The emitted event text contains only feature tags. Hidden cause and regime
labels are returned separately for benchmark scoring and must never be fed to
Organica or a baseline.
"""
from __future__ import annotations

import random

CAUSE_FEATURES = {
    "cause_a": ("amber", "birch", "cedar", "maple"),
    "cause_b": ("indigo", "fern", "willow", "yarrow"),
}
NOISE_FEATURES = ("quartz", "static", "velvet", "random")


def generate_cause_world(
    cycles: int = 300,
    events_per_cycle: int = 8,
    regime_cycles: int = 100,
    noise_rate: float = 0.10,
    seed: int = 20261023,
) -> dict:
    """Generate feature-pair events from hidden causes with regime switches.

    The dominant cause alternates every ``regime_cycles``. Its probability is
    0.85 in the active regime and 0.15 otherwise. A separate ``noise_rate``
    produces independent pairs from a noise-only vocabulary. The event text
    omits both cause and regime labels.
    """
    if cycles < 1 or events_per_cycle < 1 or regime_cycles < 1:
        raise ValueError("cycles, events_per_cycle and regime_cycles must be positive")
    if not 0.0 <= noise_rate <= 1.0:
        raise ValueError("noise_rate must be between 0 and 1")

    rng = random.Random(seed)
    events: list[str] = []
    causes: list[str] = []
    regimes: list[int] = []
    for cycle in range(cycles):
        regime = (cycle // regime_cycles) % len(CAUSE_FEATURES)
        dominant = tuple(CAUSE_FEATURES)[regime]
        alternative = tuple(c for c in CAUSE_FEATURES if c != dominant)[0]
        for _ in range(events_per_cycle):
            regimes.append(regime)
            if rng.random() < noise_rate:
                cause = "noise"
                pair = rng.sample(NOISE_FEATURES, 2)
            else:
                cause = dominant if rng.random() < 0.85 else alternative
                pair = rng.sample(CAUSE_FEATURES[cause], 2)
            events.append(" ".join(pair))
            causes.append(cause)

    gold_pairs = sorted(
        tuple(sorted((a, b)))
        for features in CAUSE_FEATURES.values()
        for i, a in enumerate(features)
        for b in features[i + 1:]
    )
    return {
        "events": events,
        "hidden_causes": causes,
        "hidden_regimes": regimes,
        "gold_same_cause_pairs": gold_pairs,
        "cause_features": {k: list(v) for k, v in CAUSE_FEATURES.items()},
        "noise_features": list(NOISE_FEATURES),
        "config": {
            "cycles": cycles, "events_per_cycle": events_per_cycle,
            "regime_cycles": regime_cycles, "noise_rate": noise_rate,
            "seed": seed, "dominant_cause_probability": 0.85,
        },
    }
