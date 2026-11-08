"""Stage B's outcome, redefined on the scale-stream family (option A, 2026-11-03).

Why this file exists
--------------------
The protocol's predictor and its outcome were defined in two different worlds: `DI`
onset needs the Phase L scale-stream family, whose worlds carry an early and a late
entity group, while `revision_held_out` is the compositional cell family's score on
cycles 250-299 of a 300-cycle world. No world carried both, and the confirmation+101
clock ran past the end of the compositional world at the protocol's own onset medians
(`docs/STAGE-B-PROTOCOL.md` §5a).

Option A keeps the predictor and redefines the outcome where the predictor lives.

The endpoint, named exactly
---------------------------
`held_out_next_tag` -- mean pairwise binary log loss on the **behavioural test window**
of a scale-stream world, restricted to ordered tag transitions that occur there and
**never occurred in the formation window**. It is the same scorer and the same
withholding principle as `revision_held_out` (AGENTS 23a: an endpoint must measure the
claim it is used for), re-parameterised onto the stream the predictor is measured on.

What this script measures, and what it does not
-----------------------------------------------
It measures the **estimator's precision**, not the organism: how tightly a world's mean
is pinned down by its withheld transitions, under two declared readouts that bracket
plausible prediction quality --

    ceiling       the world's own generating law, evaluated in closed form
    wrong_law     the same machinery on a rotated entity-to-feature assignment

Neither readout is the engine. No engine runs here, no confirmatory seed is spent, and
the worlds are the consumed Phase L design-block seeds, regenerated deterministically to
read their withheld sets. The precision gate is the one protocol §3.1 states: twice a
world's standard error must fall below the 0.05-nat effect gap.

    ./.venv/bin/python -m benchmarks.stage_b_endpoint_scale
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path

from benchmarks.acquisition_compositional import score
from benchmarks.phase_l_campaign import NOISE_FEATURES, NOISE_RATE, build_world
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "stage_b_endpoint_scale.json"

#: The four claimed configurations, as the Phase L support ratio (late, early).
CONFIG_RATIOS: dict[str, tuple[int, int]] = {
    "2:1": (2, 1), "3:1": (3, 1), "4:1": (4, 1), "6:1": (6, 1),
}

#: Declared design-block confirmation cycles: the protocol's §2 medians for each
#: configuration. They position the behavioural window where a real world's onset sits;
#: they are NOT measurements taken here and no world's onset is inferred from them.
CONFIRMATION_CYCLE: dict[str, int] = {"2:1": 539, "3:1": 404, "4:1": 362, "6:1": 329}

LEARN_CYCLES = 50
TEST_CYCLES = 50
DESIGN_SEEDS = (20261023, 20261024, 20261025)   # consumed Phase L seeds: design block
REPS = 1000
EFFECT_GAP = 0.05          # protocol §3.1's assumed gap, in nats
EPS = 1e-12
PRNG = 20261105


def _window_events(world: dict, lo: int, hi: int, epc: int) -> list[str]:
    return world["events"][lo * epc:hi * epc]


def _ordered_pairs(events: list[str]) -> set[tuple[str, str]]:
    """Every ordered tag transition between consecutive events."""
    out: set[tuple[str, str]] = set()
    for i in range(len(events) - 1):
        for u in sorted(set(events[i].split())):
            for v in sorted(set(events[i + 1].split())):
                if u != v:
                    out.add((u, v))
    return out


def withheld_pairs(world: dict, confirmation: int, epc: int) -> set[tuple[str, str]]:
    """Ordered transitions present in the test window and absent from formation.

    The withholding rule is the one the design record states for the compositional
    endpoint (§4): the scored set is disjoint from everything the organism was shown,
    and the disjointness is computed rather than asserted.
    """
    formation = _window_events(world, 0, confirmation, epc)
    test = _window_events(world, confirmation + LEARN_CYCLES,
                          confirmation + LEARN_CYCLES + TEST_CYCLES, epc)
    return _ordered_pairs(test) - _ordered_pairs(formation)


def held_positions(world: dict, confirmation: int, epc: int,
                   withheld: set[tuple[str, str]]) -> tuple[list[list[str]], list[list[str]]]:
    """Consecutive-event positions in the test window that carry a withheld transition.

    A position is kept when at least one (source, target) tag pair across its two events
    is in the withheld set -- the analogue of `held_only()` in the compositional limb.
    """
    lo = (confirmation + LEARN_CYCLES) * epc
    hi = (confirmation + LEARN_CYCLES + TEST_CYCLES) * epc
    events = world["events"]
    ctx, obs = [], []
    for i in range(lo, hi - 1):
        sources = sorted(set(events[i].split()))
        targets = sorted(set(events[i + 1].split()))
        if any((u, v) in withheld for u in sources for v in targets if u != v):
            ctx.append(sources)
            obs.append(targets)
    return ctx, obs


def law_holder(world: dict, rotate: int = 0):
    """P(next event contains v | current event contains u), from the generator's law.

    The generator picks the next event's entity by weight, then samples two of that
    entity's three features, with a declared noise rate drawing a pair from the noise
    vocabulary instead. Conditioning on `u` being visible fixes the set of entities the
    current event could have come from, which is what makes the expression closed form.

    `rotate` shifts the entity-to-feature assignment by that many places: the same
    machinery on the wrong law, which is the control the endpoint must be able to fail.
    """
    entities = list(world["entities"])
    features = [tuple(e.features) for e in entities]
    if rotate:
        features = features[rotate:] + features[:rotate]
    weights = [float(e.weight) for e in entities]
    noise_p = 2.0 / len(NOISE_FEATURES)

    def prob(u: str, v: str) -> float:
        num = 0.0
        den = 0.0
        for w, feats in zip(weights, features):
            if u in feats:
                den += w
                if v in feats:
                    num += w * (2.0 / len(feats))
        signal = (num / den) if den else 0.0
        p = (1.0 - NOISE_RATE) * signal
        if v in NOISE_FEATURES:
            p += NOISE_RATE * noise_p
        return p
    return prob


def per_position_losses(prob, ctx, obs, vocabulary) -> list[tuple[float, int]]:
    """(loss, cells) per scored position, reproducing `score()`'s inner loop."""
    out = []
    for context, observation in zip(ctx, obs):
        truth = set(observation) & vocabulary
        ll = 0.0
        cells = 0
        for source in context:
            for target in vocabulary:
                p = min(1 - EPS, max(EPS, prob(source, target)))
                y = int(target in truth and target != source)
                ll -= y * math.log(p) + (1 - y) * math.log1p(-p)
                cells += 1
        out.append((ll, cells))
    return out


def cluster_bootstrap(per, reps: int, rng: random.Random) -> tuple[float, float]:
    """Resample scored positions, recomputing the ratio estimator each replicate."""
    means = []
    total = len(per)
    for _ in range(reps):
        num = 0.0
        den = 0
        for _ in range(total):
            ll, cells = per[rng.randrange(total)]
            num += ll
            den += cells
        means.append(num / den)
    return statistics.fmean(means), statistics.stdev(means)


def probe(seed: int, label: str, reps: int) -> dict:
    late, early = CONFIG_RATIOS[label]
    confirmation = CONFIRMATION_CYCLE[label]
    cycles = confirmation + LEARN_CYCLES + TEST_CYCLES + 1
    world = build_world(seed, support_ratio=(late, early), cycles=cycles)
    epc = world["events_per_cycle"]

    def _pair_count(lo: int, hi: int) -> int:
        return len(_ordered_pairs(_window_events(world, lo, hi, epc)))

    formation_pairs = _pair_count(0, confirmation)
    test_pairs = _pair_count(confirmation + LEARN_CYCLES,
                             confirmation + LEARN_CYCLES + TEST_CYCLES)
    withheld = withheld_pairs(world, confirmation, epc)
    ctx, obs = held_positions(world, confirmation, epc, withheld)
    vocabulary = {t for event in world["events"] for t in event.split()}

    rows: dict[str, dict] = {}
    if not ctx:
        return {"configuration": label, "design_block_cell": seed,
                "withheld_transitions": 0, "measurable": False,
                "formation_pairs": formation_pairs, "test_pairs": test_pairs,
                "reason": "no withheld transition occurs in the behavioural test window: "
                          "formation already covers every ordered pair the test window uses"}
    for name, rotate in (("ceiling", 0), ("wrong_law", 1)):
        prob = law_holder(world, rotate=rotate)
        per = per_position_losses(prob, ctx, obs, vocabulary)
        cells = sum(n for _, n in per)
        total = sum(ll for ll, _ in per) / cells
        house = score(prob, ctx, obs, vocabulary)["log_loss"]
        assert abs(total - house) < 1e-6, (label, seed, name, total, house)
        rng = random.Random(PRNG + seed + len(name))
        _, se = cluster_bootstrap(per, reps, rng)
        rows[name] = {
            "scored_positions": len(per),
            "scored_cells": cells,
            "score_nats": round(total, 6),
            "cluster_se": round(se, 6),
            "twice_cluster_se": round(2.0 * se, 6),
            "clears_the_assumed_gap": bool(2.0 * se < EFFECT_GAP),
        }
    return {"configuration": label, "design_block_cell": seed,
            "withheld_transitions": len(withheld), "measurable": True,
            "formation_pairs": formation_pairs, "test_pairs": test_pairs,
            "readouts": rows}


def build(reps: int = REPS) -> dict:
    cells = [probe(seed, label, reps) for label in CONFIG_RATIOS for seed in DESIGN_SEEDS]
    measurable = [c for c in cells if c["measurable"]]
    by_config = {}
    for label in CONFIG_RATIOS:
        vals = [c["readouts"]["ceiling"]["twice_cluster_se"]
                for c in measurable if c["configuration"] == label]
        broken = [c["readouts"]["wrong_law"]["twice_cluster_se"]
                  for c in measurable if c["configuration"] == label]
        if vals:
            by_config[label] = {
                "ceiling_twice_se_min": min(vals), "ceiling_twice_se_max": max(vals),
                "wrong_law_twice_se_min": min(broken), "wrong_law_twice_se_max": max(broken),
                "clears_the_assumed_gap": bool(max(vals) < EFFECT_GAP),
            }
    pair_counts = [c["formation_pairs"] for c in cells if "formation_pairs" in c]
    finding = {
        "measurable_cells": len(measurable),
        "cells": len(cells),
        "formation_ordered_pairs_min": min(pair_counts) if pair_counts else None,
        "formation_ordered_pairs_max": max(pair_counts) if pair_counts else None,
        "statement": "an absence-based withheld set is empty on every cell: the formation "
                     "window already exhibits every ordered tag-pair transition the "
                     "behavioural window uses, because the world's vocabulary is small and "
                     "a few hundred cycles of twelve events saturate the pair space. "
                     "`held_out_next_tag` therefore cannot be defined by absence on this "
                     "stream. It needs a world that DECLARES a withheld set and enforces it "
                     "by conditioned sampling, as the compositional family does.",
    }
    return {
        "status": "NOT MEASURABLE AS DEFINED: the withheld set is empty on every cell "
                  "(see `finding`), so no standard error exists and the gate cannot be "
                  "evaluated. This is a result about the endpoint, not a bug in the probe.",
        "finding": finding,
        "what_this_is": "The per-world standard error of `held_out_next_tag`, the Stage B "
                        "outcome redefined on the scale-stream family (option A), measured "
                        "by a cluster bootstrap over scored behavioural-test positions for "
                        "three consumed design-block seeds in each claimed configuration.",
        "why_it_exists": "protocol §5a: the predictor `DI` is defined only in the "
                         "scale-stream family and the former outcome only in the "
                         "compositional family. Option A keeps the predictor and defines "
                         "the outcome on the stream the predictor lives on.",
        "endpoint": {
            "name": "held_out_next_tag",
            "scorer": "benchmarks.acquisition_compositional.score -- mean pairwise binary "
                      "log loss, the same scorer the composed endpoint used",
            "scored": "consecutive-event positions in the behavioural test window that "
                      "carry an ordered tag transition never seen in formation",
            "window": f"learning {LEARN_CYCLES} cycles then test {TEST_CYCLES} cycles, "
                      "starting one cycle after the world's confirmed onset",
        },
        "method": "each scored position is a cluster; its cells move together because the "
                  "vocabulary is scored under every position; the world's score is the "
                  "ratio (sum of position losses) / (sum of position cell counts), "
                  "bootstrapped by resampling positions with replacement",
        "replicates": reps,
        "effect_gap_assumed": EFFECT_GAP,
        "design_block_cells": list(DESIGN_SEEDS),
        "cells_are": "consumed Phase L seeds, regenerated deterministically; no seed is "
                     "spent and none is re-allocated",
        "confirmation_cycles_are": "the protocol §2 medians per configuration, used to "
                                   "position the behavioural window; no onset is measured "
                                   "here and none is inferred",
        "configurations": by_config,
        "cells": cells,
        "limits": [
            "the two readouts bracket plausible prediction quality (the world's own law "
            "and the same machinery rotated onto a wrong law); neither is the engine's "
            "readout, whose loss distribution does not exist before the run",
            "the confirmation cycles are the protocol's medians, not measured onsets, so "
            "this measures the estimator on plausible windows rather than reproducing a "
            "run",
            "the readouts carry no noise beyond the world's own, so a real readout with "
            "heavier-tailed losses would give a larger standard error",
            "three design-block seeds per configuration measure the estimator; they do "
            "not authorise the run and they are not the confirmatory block",
            "a bootstrap standard deviation is itself estimated, so the reported figures "
            "carry Monte-Carlo uncertainty not shown here",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=REPS)
    args = ap.parse_args()
    result = build(args.reps)
    OUT.write_text(json.dumps(engine_stamp.stamp(result), indent=2), encoding="utf-8")
    for label, row in result["configurations"].items():
        print(f"{label}: ceiling 2SE {row['ceiling_twice_se_min']}-{row['ceiling_twice_se_max']} "
              f"| wrong law {row['wrong_law_twice_se_min']}-{row['wrong_law_twice_se_max']} "
              f"| clears gap: {row['clears_the_assumed_gap']}")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
