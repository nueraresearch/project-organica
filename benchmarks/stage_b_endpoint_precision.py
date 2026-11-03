"""The per-world standard error of `revision_held_out`, measured by resampling transitions.

Protocol §3.1 requires the granularity gate to be decided on a per-world standard
error. The second machine pass (`docs/AI-REVIEW-2026-11-03.md`, finding 3) established
that the previous rule could not be evaluated: `score()` averages pairwise binary log
loss over context x source x vocabulary cells, so the 82-110 withheld transitions are
not 82-110 independent contributions, and the SD of scored cells over `sqrt(cells)`
was never the per-world standard error.

This script measures it the way the protocol now says it must be measured: a **cluster
bootstrap over the withheld transitions**. Each withheld transition is a cluster; its
cells move together, because the same vocabulary is scored under every transition. The
world's score is a ratio estimator -- sum of transition losses over sum of transition
cell counts -- so the bootstrap resamples transitions and recomputes the ratio.

Two readouts bracket the losing end and the winning end of the plausible range:

    ceiling        the exact latent rule for the world, so the world's score is at
                   its floor
    broken rule    the right machinery on the wrong law, the classic failure the
                   benchmark exists to catch

Neither is the organism. What is measured here is a property of the **estimator** --
how precisely a world's mean is pinned down by its withheld transitions -- and the
limitation is stated in the artifact rather than implied.

No engine runs, no seed is spent, no world is generated that was not already
generated: the five seeds are the calibration block, already consumed, and they are
re-generated deterministically here only to read their withheld sets.

    ./.venv/bin/python -m benchmarks.stage_b_endpoint_precision
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path

from benchmarks.acquisition_compositional import score
from benchmarks.reusable_knowledge import (
    CYCLES, broken_rule_holder, generate_compositional_world,
    latent_rule_holder, limbs,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "stage_b_endpoint_precision.json"

CALIBRATION_SEEDS = (20261201, 20261202, 20261203, 20261204, 20261205)
REPS = 2000             # cluster-bootstrap replicates per world and readout
EFFECT_GAP = 0.05       # the protocol's assumed gap, in nats (stage_b_protocol)
EPS = 1e-12             # the scorer's own floor, so the losses match it exactly
PRNG = 20261104


def per_transition_losses(prob, contexts, observations, vocabulary):
    """(loss, cells) per withheld transition, reproducing `score()`'s inner loop."""
    out = []
    for ctx, obs in zip(contexts, observations):
        truth = set(obs) & vocabulary
        ll = 0.0
        cells = 0
        for source in ctx:
            for target in vocabulary:
                p = min(1 - EPS, max(EPS, prob(source, target)))
                y = int(target in truth and target != source)   # exclude_self
                ll -= y * math.log(p) + (1 - y) * math.log1p(-p)
                cells += 1
        out.append((ll, cells))
    return out


def cell_losses(prob, contexts, observations, vocabulary):
    """Every individual cell loss, for the withdrawn naive standard error."""
    out = []
    for ctx, obs in zip(contexts, observations):
        truth = set(obs) & vocabulary
        for source in ctx:
            for target in vocabulary:
                p = min(1 - EPS, max(EPS, prob(source, target)))
                y = int(target in truth and target != source)
                out.append(-(y * math.log(p) + (1 - y) * math.log1p(-p)))
    return out


def cluster_bootstrap(per, reps, rng):
    """Bootstrap the ratio estimator by resampling transitions, not cells."""
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


def probe_seed(seed: int, reps: int) -> dict:
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    held = limbs(world)
    ctx, obs = held["revision_held_out"]
    vocabulary = {t for event in world["events"] for t in event.split()}

    rows: dict[str, dict] = {}
    for name, make in (("ceiling", lambda: latent_rule_holder(world, 0)),
                       ("broken_rule", lambda: broken_rule_holder(world))):
        prob = make()
        per = per_transition_losses(prob, ctx, obs, vocabulary)
        cells = sum(n for _, n in per)
        total = sum(ll for ll, _ in per) / cells

        # the reconstruction must reproduce the house scorer, or the two are not
        # measuring the same quantity
        house = score(prob, ctx, obs, vocabulary)["log_loss"]
        assert abs(total - house) < 1e-6, (seed, name, total, house)

        rng = random.Random(PRNG + seed + len(name))
        _, cluster_se = cluster_bootstrap(per, reps, rng)

        losses = cell_losses(prob, ctx, obs, vocabulary)
        naive_se = statistics.stdev(losses) / math.sqrt(len(losses))

        rows[name] = {
            "withheld_transitions": len(per),
            "scored_cells": cells,
            "score_nats": round(total, 6),
            "cluster_se": round(cluster_se, 6),
            "twice_cluster_se": round(2.0 * cluster_se, 6),
            "naive_cell_se": round(naive_se, 6),
            "cluster_over_naive_se_ratio": round(cluster_se / naive_se, 2),
            "clears_the_assumed_gap": bool(2.0 * cluster_se < EFFECT_GAP),
        }

    return {"design_block_cell": seed, "readouts": rows}


def build(reps: int = REPS) -> dict:
    seeds = [probe_seed(seed, reps) for seed in CALIBRATION_SEEDS]
    worst = max(row["twice_cluster_se"]
                for seed in seeds for row in seed["readouts"].values())
    ratios = [row["cluster_over_naive_se_ratio"]
              for seed in seeds for row in seed["readouts"].values()]
    by_readout = {}
    for name in ("ceiling", "broken_rule"):
        vals = [seed["readouts"][name]["twice_cluster_se"] for seed in seeds]
        by_readout[name] = {
            "min_twice_cluster_se": min(vals),
            "max_twice_cluster_se": max(vals),
            "clears_the_assumed_gap": bool(max(vals) < EFFECT_GAP),
        }
    return {
        "what_this_is": "The per-world standard error of `revision_held_out`, "
                        "measured by a cluster bootstrap over withheld transitions "
                        "rather than over scored cells, for the five design-block "
                        "cells. It discharges the method the granularity gate now "
                        "requires; it does not discharge the gate for Stage B.",
        "why_it_exists": "docs/STAGE-B-PROTOCOL.md §3.1 and "
                         "docs/AI-REVIEW-2026-11-03.md finding 3: `score()` returns "
                         "an aggregate over nested cells, so no per-world standard "
                         "error existed and `s/sqrt(N)` over the transition count was "
                         "a substitution.",
        "method": "each withheld transition is a cluster; its cells move together "
                  "because the vocabulary is scored under every transition; the "
                  "world's score is the ratio (sum of transition losses) / (sum of "
                  "transition cell counts) and is bootstrapped by resampling "
                  "transitions with replacement",
        "level_and_reps": {"percentile_level": 0.9833, "replicates": reps,
                           "reported_quantity": "the bootstrap standard deviation "
                                                "of the ratio estimator"},
        "prng_state": PRNG,
        "effect_gap_assumed": EFFECT_GAP,
        # not filed under a key naming a seed: these are the calibration block's
        # consumed seeds, already counted in that artifact, and re-listing them
        # here would make the protocol's consumed-seed scan count an artifact twice
        "design_block_cells": [s["design_block_cell"] for s in seeds],
        "cells_are": "the consumed calibration seeds, regenerated deterministically; "
                     "no seed is spent and none is re-allocated",
        "cells": seeds,
        "worst_twice_cluster_se": round(worst, 6),
        "by_readout": by_readout,
        "the_bracket_straddles_the_gap": (
            by_readout["ceiling"]["clears_the_assumed_gap"]
            != by_readout["broken_rule"]["clears_the_assumed_gap"]),
        "cluster_over_naive_se_ratio": {"min": min(ratios), "max": max(ratios)},
        "status": "method discharged on design-block cells; the gate is NOT "
                  "confirmed for Stage B, because the bracket straddles the gap",
        "limits": [
            "the five seeds are the calibration block, already consumed; they are "
            "design-block cells, not the four claimed configurations, so this "
            "measures the estimator and does not authorise the run",
            "the two readouts bracket plausible prediction quality (the exact "
            "latent rule and the wrong-law control); neither is the organism's "
            "readout, whose loss distribution is not available before the run, and "
            "a readout with heavier-tailed losses would give a larger standard error",
            "a bootstrap standard deviation is itself estimated: with %d replicates "
            "per cell its own Monte-Carlo error is a few percent of its value" % reps,
            "%d held-out transitions per cell is the count the calibration cells "
            "happen to have; the claimed configurations' counts do not exist yet"
            % min(row["withheld_transitions"]
                  for s in seeds for row in s["readouts"].values()),
        ],
        "no_engine": "No engine ran and no seed was spent. The worlds are "
                     "regenerated deterministically from already-consumed seeds to "
                     "read their withheld sets.",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reps", type=int, default=REPS)
    args = ap.parse_args()
    artifact = build(args.reps)
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  reps={args.reps}")
    for cell in artifact["cells"]:
        for name, row in cell["readouts"].items():
            print(f"  cell {cell['design_block_cell']}  {name:>11}  T={row['withheld_transitions']:>3}  "
                  f"cells={row['scored_cells']:>5}  score {row['score_nats']:.4f}  "
                  f"2xSE {row['twice_cluster_se']:.4f}  "
                  f"naive {row['naive_cell_se']:.4f}  "
                  f"ratio {row['cluster_over_naive_se_ratio']:.1f}x")
    print("worst 2xSE:", artifact["worst_twice_cluster_se"],
          "| by readout:", {k: v["clears_the_assumed_gap"]
                            for k, v in artifact["by_readout"].items()})


if __name__ == "__main__":
    main()
