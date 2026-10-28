"""The compositional generalisation task: a world where counting cannot win.

Why a SECOND world exists (2026-10-27).

The redesigned transition world (`acquisition_world.py`) is **first-order
Markov**, and that has a consequence that was measured, not assumed:

    ceiling (knows the law)        0.2242
    copy-context (grouping only)   0.2521
    first-order Markov on raw rows 0.2517     <-- 0.0275 nats from the ceiling

A bigram table is the *natural* learner for a first-order chain, so with
enough data "understood the law" and "estimated the transition table" are
not separable by a next-event score.  That world is therefore a
**calibration / control task** — it tests ordinary transition learning and
law-change adaptation — and it is **not** evidence of abstraction beyond
counts.

This module is the task that CAN separate them.  Its design principle is
the standard one from the systematic-generalisation literature: **withhold
a COMBINATION of familiar elements, so that a learner must generalise a
rule rather than recount a transition.**

The world
---------

Four CELLS arranged in a 2x2 grid of two latent factors:

    (P0,Q0)   (P0,Q1)
    (P1,Q0)   (P1,Q1)

Each cell holds 4 tags.  The law is **compositional**:

    the successor cell is the one that differs in EXACTLY ONE factor
    (flip P with probability 0.5, flip Q with probability 0.5)

So "flip exactly one factor" is a single rule that applies to all four
cells, and it says nothing about any particular tag.

The tag-to-cell mapping is **randomised per world** from a fixed pool of
16 words, so no fixed tag association can solve it and no result can be
carried between seeds.

The withheld combination
------------------------

One cell per world, chosen at random, is the HELD cell.  Its
flip-P transitions are withheld from the **training stream** only: the
events in which the held cell is the context and the successor is its
flip-P neighbour are removed from the acquisition phase.  Everything else
in the world is untouched, and the *test* stream is the unmodified world.

Why that is fair, not a rigged hole:

* the held cell's tags are still present in the training stream, so the
  learner still sees them co-occur and can still learn which cell they
  belong to;
* the held cell's flip-Q transitions are still present, so the learner
  still has *some* evidence about that cell;
* the other three cells show BOTH transition types, so the rule "flip
  exactly one factor, 50/50" is fully supported by the training data;
* the learner must therefore *apply* the rule to the one cell where the
  evidence is missing, instead of recounting the transition.

A tag-level bigram, and even a cell-level counter, has **zero support**
for the withheld transition and must fall back to a backoff.  A learner
holding the rule does not.

The controls
------------

* **Positive control** — the rule holder: it knows the factor grid and the
  law, so it can answer the withheld combination.  It must reach the
  closed-form ceiling.
* **Broken-rule control** — the same learner with a WRONG law ("always
  flip P").  It must be clearly worse than the ceiling, or the benchmark
  is not measuring the law.
* **Baselines** — a tuned bigram, a tuned decayed bigram, a cell-level
  (latent-state) counter, and the base rate.  The benchmark's headroom
  is measured against the **BEST** of them, never against the base rate
  alone.

Read-only.  No engine run.  Standard library only.
"""
from __future__ import annotations

import itertools
import math
import random
from collections import defaultdict

# 16 tags, 4 per cell.  The same pool the transition world uses, so the two
# tasks differ in their LAW and not in their vocabulary size.
TAG_POOL: tuple[str, ...] = (
    "amber", "birch", "cedar", "maple",
    "indigo", "fern", "willow", "yarrow",
    "olive", "sable", "umber", "verdant",
    "ochre", "crimson", "teal", "slate",
)

TAGS_PER_CELL = 4
TAGS_PER_EVENT = 2

# The four cells as (P, Q) coordinates.
CELLS: tuple[tuple[int, int], ...] = ((0, 0), (0, 1), (1, 0), (1, 1))


def cell_name(c: tuple[int, int]) -> str:
    return f"p{c[0]}q{c[1]}"


def flip_p(c: tuple[int, int]) -> tuple[int, int]:
    return (1 - c[0], c[1])


def flip_q(c: tuple[int, int]) -> tuple[int, int]:
    return (c[0], 1 - c[1])


def neighbours(c: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    return (flip_p(c), flip_q(c))


# ---------------------------------------------------------------------------
# The world
# ---------------------------------------------------------------------------

# Phase boundaries, in CYCLES.  They live here so the generator and the
# scoring code cannot drift apart.
#
#   0    - 19    warm-up            regime 0
#   20   - 109   acquisition        regime 0   <- the training stream
#   110  - 149   retention          regime 0   <- same law, frozen state
#   150  - 199   transfer           regime 0   <- NEW combination, frozen state
#   200  - 249   revision learning  regime 1   <- the law has changed
#   250  - 299   revision test      regime 1   <- held combination, after learning
#
# The regime switch rotates the law: flip-P and flip-Q swap probability.
PHASE_WARMUP = (0, 20)
PHASE_ACQUISITION = (20, 110)
PHASE_RETENTION = (110, 150)
PHASE_TRANSFER = (150, 200)
PHASE_REVISION_LEARN = (200, 250)
PHASE_REVISION_TEST = (250, 300)
REGIME_SWITCH_CYCLE = 200

EVENTS_PER_CYCLE = 8
CYCLES = 300

# The law's two transition types and their probability in each regime.
# Regime 0: flip-P is the more likely.  Regime 1: it rotates.
LAW_R0 = {"flip_p": 0.65, "flip_q": 0.35}
LAW_R1 = {"flip_p": 0.35, "flip_q": 0.65}


def generate_compositional_world(seed: int = 20261100,
                                 cycles: int = CYCLES,
                                 events_per_cycle: int = EVENTS_PER_CYCLE,
                                 regime_cycles: int = REGIME_SWITCH_CYCLE,
                                 held_cell_index: int | None = None,
                                 ) -> dict:
    """Generate the compositional world.

    Returns the event text plus the hidden labels used only for scoring, and
    the TRAINING MASK: which acquisition events are withheld from the
    learner because they carry the held combination.
    """
    if cycles < 1 or events_per_cycle < 1 or regime_cycles < 1:
        raise ValueError("cycles, events_per_cycle and regime_cycles must be positive")

    rng = random.Random(seed)

    # Randomise the tag-to-cell mapping per world.
    pool = list(TAG_POOL)
    rng.shuffle(pool)
    cell_tags: dict[tuple[int, int], list[str]] = {}
    for i, c in enumerate(CELLS):
        cell_tags[c] = sorted(pool[i * TAGS_PER_CELL:(i + 1) * TAGS_PER_CELL])

    if held_cell_index is None:
        held_cell_index = rng.randrange(len(CELLS))
    held = CELLS[held_cell_index]
    held_flip_p = flip_p(held)

    events: list[str] = []
    cells: list[str] = []
    regimes: list[int] = []
    trainable: list[bool] = []   # False => withheld from the training stream
    withheld: list[bool] = []     # True => this event carries the held combination

    state = CELLS[rng.randrange(len(CELLS))]
    acq_lo, acq_hi = PHASE_ACQUISITION

    for cycle in range(cycles):
        regime = (cycle // regime_cycles) % 2
        law = LAW_R0 if regime == 0 else LAW_R1
        for _ in range(events_per_cycle):
            kinds = ("flip_p", "flip_q")
            kind = rng.choices(kinds, weights=[law[k] for k in kinds], k=1)[0]
            nxt = flip_p(state) if kind == "flip_p" else flip_q(state)
            tags = cell_tags[nxt]
            pair = rng.sample(tags, TAGS_PER_EVENT)
            events.append(" ".join(sorted(pair)))
            cells.append(cell_name(nxt))
            regimes.append(regime)
            # The withheld combination: the held cell as CONTEXT, with its
            # flip-P successor.  Withheld from the TRAINING STREAM only.
            in_acq = (acq_lo * events_per_cycle <= len(events) - 1
                      < acq_hi * events_per_cycle)
            is_withheld = (state == held and nxt == held_flip_p and in_acq)
            trainable.append(not is_withheld)
            withheld.append(is_withheld)
            state = nxt

    return {
        "events": events,
        "cells": cells,
        "regimes": regimes,
        "trainable": trainable,
        "withheld": withheld,
        "cell_tags": {cell_name(c): sorted(v) for c, v in cell_tags.items()},
        "tag_to_cell": {t: cell_name(c) for c, v in cell_tags.items() for t in v},
        "held_cell": cell_name(held),
        "held_cell_tags": sorted(cell_tags[held]),
        "held_cell_flip_p": cell_name(held_flip_p),
        "config": {
            "seed": seed, "cycles": cycles,
            "events_per_cycle": events_per_cycle,
            "regime_cycles": regime_cycles,
            "held_cell_index": held_cell_index,
            "law_r0": LAW_R0, "law_r1": LAW_R1,
        },
    }


# ---------------------------------------------------------------------------
# The closed-form conditional: the Bayes ceiling
# ---------------------------------------------------------------------------

def cell_conditional(regime: int, cell_tags: dict[str, list[str]]
                     ) -> dict[str, dict[str, float]]:
    """P(v in the next event | the context cell), for every tag v.

    The next cell is flip-P with prob p and flip-Q with prob 1-p; within a
    cell, each of its 4 tags appears in the 2-of-4 event with prob 2/4.

    `cell_tags` maps a cell NAME to its tag list.  The mapping is
    randomised per world, so it must be passed in; it is **scoring-side
    information only** and is never given to a learner.
    """
    law = LAW_R0 if regime == 0 else LAW_R1
    coord = {c: (int(c[1]), int(c[3])) for c in cell_tags}
    out: dict[str, dict[str, float]] = {}
    for cname, members in cell_tags.items():
        p, q = coord[cname]
        dist: dict[str, float] = {}
        for kind, (np_, nq) in (("flip_p", (1 - p, q)), ("flip_q", (p, 1 - q))):
            share = law[kind] * (TAGS_PER_EVENT / TAGS_PER_CELL)
            nxt = f"p{np_}q{nq}"
            for t in cell_tags.get(nxt, []):
                dist[t] = dist.get(t, 0.0) + share
        out[cname] = dist
    return out


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

EPS = 1e-12


def score(prob, contexts, observations, vocabulary, exclude_self=True) -> dict:
    """The house pairwise log-loss, plus Brier.

    `exclude_self` reproduces the house `_score` shape, which skips the
    cell where target == source.  The alternative is measured and reported,
    because the house shape was found to shield the baseline on the
    transition world.
    """
    ll = brier = n = 0.0
    for ctx, obs in zip(contexts, observations):
        truth = set(obs) & vocabulary
        for source in ctx:
            for target in vocabulary:
                p = min(1 - EPS, max(EPS, prob(source, target)))
                y = int(target in truth)
                if exclude_self:
                    y = int(target in truth and target != source)
                ll -= y * math.log(p) + (1 - y) * math.log1p(-p)
                brier += (p - y) ** 2
                n += 1
    return {"log_loss": round(ll / n, 6), "brier": round(brier / n, 6)}


# ---------------------------------------------------------------------------
# The rules
# ---------------------------------------------------------------------------

def make_ceiling(world: dict, regime: int):
    """The Bayes ceiling: the world's true conditional."""
    cond = cell_conditional(regime, world["cell_tags"])
    tag_to_cell = world["tag_to_cell"]

    def p(source: str, target: str) -> float:
        return cond.get(tag_to_cell.get(source, ""), {}).get(target, 0.0)
    return p


def make_rule_holder(world: dict, regime: int, law: dict | None = None):
    """The POSITIVE CONTROL: a learner that holds the generating rule.

    It knows the factor grid and the law, so it answers the withheld
    combination correctly.  With the world's own law it must reach the
    closed-form ceiling; with a different law it must not (that is the
    broken-rule control).

    The law is the full mixture over the two transition types -- a learner
    that knows only ONE transition type does NOT hold the rule.
    """
    if law is None:
        law = LAW_R0 if regime == 0 else LAW_R1
    tag_to_cell = world["tag_to_cell"]
    coord = {c: (int(c[1]), int(c[3])) for c in world["cell_tags"]}

    def p(source: str, target: str) -> float:
        sc = tag_to_cell.get(source)
        tc = tag_to_cell.get(target)
        if sc is None or tc is None:
            return 0.0
        sp, sq = coord[sc]
        tp, tq = coord[tc]
        if sp == tp and sq == tq:
            return 0.0                      # same cell: never a successor
        if sp != tp and sq != tq:
            return 0.0                      # differs in two factors: impossible
        kind = "flip_q" if sp == tp else "flip_p"
        return law.get(kind, 0.0) * (TAGS_PER_EVENT / TAGS_PER_CELL)
    return p


def make_broken_rule(world: dict, regime: int, wrong_law: dict | None = None):
    """The BROKEN-RULE CONTROL: the right machinery, the wrong law.

    The default is the classic failure this benchmark is built to catch: a
    learner that **latched onto one transition type** and believes the
    successor is always the flip-P neighbour, ignoring the flip-Q
    transition entirely.  That is precisely the mistake a learner would
    make on the withheld cell — the one whose flip-P transitions are
    missing from the training stream — so it is the right thing for the
    control to embody.

    It must be clearly worse than the ceiling, or the endpoint is not
    measuring the law.
    """
    if wrong_law is None:
        wrong_law = {"flip_p": 0.99, "flip_q": 0.01}
    return make_rule_holder(world, regime, law=wrong_law)


def make_swapped_law(world: dict, regime: int):
    """A NEAR-MISS control: the right structure, the two weights swapped.

    This is reported as a **sensitivity measurement**, not as a gate.  It
    is a subtle error, and if the endpoint barely notices it, that is a
    fact about the endpoint's resolution rather than a defect — so it is
    reported with its number instead of being used as a pass/fail check.
    """
    base = LAW_R0 if regime == 0 else LAW_R1
    return make_rule_holder(world, regime,
                            law={"flip_p": base["flip_q"],
                                 "flip_q": base["flip_p"]})
