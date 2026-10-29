"""The acquisition study's world: temporally coupled, group-structured, regime-switching.

Why a new world (docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md, Revision 3):

The frozen cause-world draws each event's cause INDEPENDENTLY.  Measured on
that world, within a regime P(cause_{t+1}=c | cause_t=c) differs from
P(cause_{t+1}=c) by at most 0.03 -- the events are independent given the
regime.  So a same-cause pair, which describes features that co-occur
WITHIN one event, does not predict the NEXT event, and a next-event endpoint
measures something the world never asserted.  A study may not ask a question
its world cannot answer.

This generator makes the sequence itself law-governed, so next-event
prediction is INTRINSIC to the world, and it makes the governing law change
at a switch, so revision has something to revise.

Structure
---------
* `GROUPS` disjoint sets of tags.  Every event draws two tags from ONE group.
* A Markov chain over groups governs which group follows.  The chain is
  regime-dependent, so the law CHANGES at the switch.
* A noise vocabulary, reachable as its own chain state, so a noise context is
  a legitimate context with a legitimate next-state distribution.
* `hidden_groups` and `hidden_transitions` are returned separately, for
  scoring only, and must never be fed to Organica or to a baseline.

The exact next-event conditional is computable in closed form, so the study
has a TRUE prediction ceiling rather than a relation oracle:

    P(v in e_{t+1} | context is group g)
        = sum over g' of  T[g][g'] * (2 / |g'|) * [v in g']

This module is a benchmark, not the engine.  `organica/` is not modified.
"""
from __future__ import annotations

import random

# Four groups of four tags.  Groups are disjoint, so a context's group is
# recoverable from its tags.
GROUPS: dict[str, tuple[str, ...]] = {
    "g0": ("amber", "birch", "cedar", "maple"),
    "g1": ("indigo", "fern", "willow", "yarrow"),
    "g2": ("olive", "sable", "umber", "verdant"),
    "g3": ("ochre", "crimson", "teal", "slate"),
}
NOISE_TAGS: tuple[str, ...] = ("quartz", "static", "velvet", "random")
NOISE_STATE = "noise"

# The study's phase boundaries, in CYCLES.  They live here, in the world
# module, so the generator and the scoring code cannot drift apart: the
# regime switch lands exactly on the boundary between the retention window
# and the revision window, by construction.
#
#   0    - 19    warm-up           regime 0
#   20   - 109   acquisition       regime 0   <- the episodes under study
#   110  - 149   retention window  regime 0   <- frozen state, OLD law
#   150  - 189   revision window   regime 1   <- the law has rotated
#   190  - 249   revision window   regime 1   <- scored after continued learning
#
# The switch is at cycle 150, which is the boundary between the retention
# window and the revision window.  So the retention window is scored under
# the OLD law and the revision window under the NEW one, and the two are
# genuinely different questions.
PHASE_WARMUP = (0, 20)
PHASE_ACQUISITION = (20, 110)
PHASE_RETENTION = (110, 150)
PHASE_REVISION = (150, 250)
REGIME_SWITCH_CYCLE = 150

# The transition law.  Each group's preferred successor is the key design
# choice, and it was FIXED BEFORE ANY CELL RUN (docs/ACQUISITION-EXPERIMENT-
# PREREGISTRATION.md §4.1).  The headroom between "knows the law" and "knows
# only the tag base rate" was swept over chain sharpness, and this value was
# chosen from that sweep:
#
#   self/succ/other  ceiling log-loss  base-rate log-loss  headroom
#        0.60/0.30/0.10      0.3114            0.3663        0.0550
#        0.80/0.15/0.05      0.2726            0.3441        0.0716
#   *   0.88/0.09/0.03      0.2409            0.3320        0.0911
#        0.94/0.05/0.01      0.2097            0.3271        0.1173
#
# The sharpest chain has a larger headroom but makes the world nearly
# deterministic, which would turn the study into a test of a lookup table.
# 0.88/0.09/0.03 leaves a real gap (0.0911 nats) in a world that is not
# deterministic.  The choice is not revisited.
SELF_P, SUCC_P, OTHER_P = 0.88, 0.09, 0.03


def _normalise(row: dict[str, float]) -> dict[str, float]:
    total = sum(row.values())
    return {k: v / total for k, v in row.items()}


def _row(preferred: str, second: str, third: str) -> dict[str, float]:
    return {preferred: SELF_P, second: SUCC_P, third: OTHER_P}


def _build_chains() -> list[dict[str, dict[str, float]]]:
    """Regime 0: each group prefers ITSELF.  Regime 1: the preference ROTATES
    to the successor, but stays partly valid.

    The rotation is deliberately partial rather than total.  A total
    inversion would make the old law simply wrong, and a frozen state's
    transfer score would then be a foregone near-zero -- a cliff, not a
    measurement.  With a partial rotation the acquired structure remains
    *partly* right in the new regime, so:

      * TRANSFER (frozen state, new regime) is a real, graded quantity, and
      * REVISION (the same window, after continued learning) can improve on
        it, which is what makes the limb worth measuring.

    The exact values were swept for headroom before any cell was run.
    """
    names = list(GROUPS)
    r0: dict[str, dict[str, float]] = {}
    r1: dict[str, dict[str, float]] = {}
    for i, g in enumerate(names):
        nxt = names[(i + 1) % len(names)]
        prv = names[(i - 1) % len(names)]
        r0[g] = _row(g, nxt, prv)
        r1[g] = _row(nxt, g, prv)
    # the noise state reaches the groups with a spread, plus itself
    noise_row = {"g0": 0.40, "g1": 0.25, "g2": 0.20, "g3": 0.10, NOISE_STATE: 0.05}
    r0[NOISE_STATE] = dict(noise_row)
    r1[NOISE_STATE] = dict(noise_row)
    out = []
    for chain in (r0, r1):
        out.append({k: _normalise(v) for k, v in chain.items()})
    return out


# Regime 0: the group prefers itself.  Regime 1: the group prefers its
# successor.  These are the two laws; the switch between them is the thing
# the study's revision limb is about.
CHAIN_R0: dict[str, dict[str, float]] = _build_chains()[0]
CHAIN_R1: dict[str, dict[str, float]] = _build_chains()[1]


def _chains() -> list[dict[str, dict[str, float]]]:
    return [CHAIN_R0, CHAIN_R1]


def group_of(tags) -> str | None:
    """The group a tag set belongs to, or None if it is a noise context."""
    ts = set(tags)
    for g, members in GROUPS.items():
        if ts and ts.issubset(set(members)):
            return g
    return NOISE_STATE


def next_event_distribution(regime: int) -> dict[str, dict[str, float]]:
    """P(v in e_{t+1} | context group), for every tag v, in the given regime.

    This is the TRUE conditional the endpoint scores against, and it is what
    the study's ceiling uses.  It is a property of the generator alone; it
    does not involve the organism.
    """
    chain = _chains()[regime]
    out: dict[str, dict[str, float]] = {}
    for g, row in chain.items():
        dist: dict[str, float] = {}
        for g2, p_g2 in row.items():
            members = NOISE_TAGS if g2 == NOISE_STATE else GROUPS[g2]
            share = 2.0 / len(members)
            for t in members:
                dist[t] = dist.get(t, 0.0) + p_g2 * share
        out[g] = dist
    return out


def generate_rule_world(
    cycles: int = 250,
    events_per_cycle: int = 8,
    regime_cycles: int = 150,
    seed: int = 20261100,
    start_state: str = "g0",
) -> dict:
    """Generate the temporally coupled, group-structured world.

    Returns the event text plus the hidden labels used only for scoring.
    """
    if cycles < 1 or events_per_cycle < 1 or regime_cycles < 1:
        raise ValueError("cycles, events_per_cycle and regime_cycles must be positive")

    chains = _chains()
    rng = random.Random(seed)
    events: list[str] = []
    hidden_groups: list[str] = []
    hidden_regimes: list[int] = []
    state = start_state

    for cycle in range(cycles):
        regime = (cycle // regime_cycles) % 2
        chain = chains[regime]
        for _ in range(events_per_cycle):
            row = chain[state]
            targets = list(row)
            weights = [row[t] for t in targets]
            nxt = rng.choices(targets, weights=weights, k=1)[0]
            members = NOISE_TAGS if nxt == NOISE_STATE else GROUPS[nxt]
            pair = rng.sample(list(members), 2)
            events.append(" ".join(pair))
            hidden_groups.append(nxt)
            hidden_regimes.append(regime)
            state = nxt

    return {
        "events": events,
        "hidden_groups": hidden_groups,
        "hidden_regimes": hidden_regimes,
        "groups": {k: list(v) for k, v in GROUPS.items()},
        "noise_tags": list(NOISE_TAGS),
        "config": {
            "cycles": cycles, "events_per_cycle": events_per_cycle,
            "regime_cycles": regime_cycles, "seed": seed,
            "chains": chains, "start_state": start_state,
        },
    }
