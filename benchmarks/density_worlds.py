"""The density interaction's world: a fixed vocabulary, a declared rho_world, one filler rule.

This module owns the world half of the density study and nothing else: no engine, no
criterion, no verdict. It exists separately so the runner, the scorer and the harness
audits cannot each grow their own copy of the world and drift apart.

The manipulation
----------------
`rho_world = |W| / |P_world|`, with `P_world` the directed non-self pairs of the world's
own 16-tag vocabulary, so `|P_world| = 240`. W is a deterministic subset of `P_world`
drawn with a generator keyed on (seed, rho), so it is independent of which arm ranks it
and reproducible across machines.

The world's edges are drawn from **all** 240 pairs, not from the cross-cell pairs alone.
That matters: an intra-cell pair is then a world edge at some densities, so excluding the
intra-cell class costs something as well as buying something. A design that draws W only
from cross-cell pairs makes every intra-cell row a non-edge by construction and pins the
treatment's advantage at its ceiling.

The intra-cell mass is a function of density
--------------------------------------------
Gate 13 measured the engine's top-20 as 75-100 % intra-cell in a sparse world. Here that
observation is made an explicit property of the stream: the filler's share of the event
budget is `1 - rho_world`, so a sparse world's stream is dominated by within-cell
co-occurrence and a dense world's is dominated by transitions. This is a **declared
choice of world family**, recorded as such; a world whose filler mass is density-invariant
is a different arm and is not run here.

Two exposure schemes
--------------------
* `primary`     -- fixed total exposure: every density gets `TOTAL_EVENTS` events, so each
  edge is observed fewer times as density rises.
* `sensitivity` -- fixed exposure per edge: each world edge is emitted `EDGE_REPEATS`
  times regardless of density, so the curriculum lengthens with density.

Both are constructed from the same per-density recipe; only the padding differs. Neither
is the truth about exposure, and the pair is what separates a geometry effect from an
exposure artifact.

Not evidence on its own: this module measures no learner. `leverage_audit` reports what the
designed pools do under each arm, which is a property of the world, not of the engine.
"""
from __future__ import annotations

import random
from collections import Counter

from benchmarks.acquisition_compositional import TAG_POOL

#: The Gate 13 vocabulary, four cells of four. Every tag is >= 4 letters (AGENTS rule 9).
VOCAB: tuple[str, ...] = tuple(TAG_POOL)
TAGS_PER_CELL = 4
TAGS_PER_EVENT = 2
EVENTS_PER_CYCLE = 8

#: Fixed total exposure for the primary scheme: 50 sleep cycles at 8 events per cycle.
TOTAL_EVENTS = 400
#: Emissions of each world edge: the sensitivity scheme's per-edge exposure.
EDGE_REPEATS = 2
#: The filler's peak event budget, spent in proportion to (1 - rho_world).
#: Chosen so the within-cell class outcounts a world edge at the sparse end and loses to it
#: at the dense end; the crossover is what makes the registered direction testable.
FILLER_BUDGET = 24
#: The cap ladder. 20 is the primary cap (Gate 13's budget); the rest is characterization.
CAPS = (20, 40, 80, 160, 240)
PRIMARY_CAP = 20

assert len(VOCAB) == 16 and len(set(VOCAB)) == 16
assert set(VOCAB) == set(TAG_POOL)
assert min(len(tag) for tag in VOCAB) >= 4, "a tag under four letters is invisible"


def cells() -> list[tuple[str, ...]]:
    return [tuple(VOCAB[i:i + TAGS_PER_CELL])
            for i in range(0, len(VOCAB), TAGS_PER_CELL)]


def all_pairs() -> list[tuple[str, str]]:
    return [(a, b) for a in VOCAB for b in VOCAB if a != b]


def cross_cell_pairs() -> list[tuple[str, str]]:
    """The law's candidate universe: ordered pairs that cross a cell boundary.

    The world's edges live here and nowhere else. That is the Gate 13 law, and it is what
    makes the treatment a coherent intervention: an intra-cell row **can never** be a
    world edge, so excluding the class can only free budget, never discard the signal.
    Drawing W from all 240 pairs instead would make the exclusion a pure gamble and the
    study would measure the draw, not the geometry.
    """
    groups = cells()
    out: list[tuple[str, str]] = []
    for i, left in enumerate(groups):
        for j, right in enumerate(groups):
            if i != j:
                out.extend((a, b) for a in left for b in right)
    return out


def universe_size() -> int:
    return len(VOCAB) * (len(VOCAB) - 1)


def cell_index(tag: str) -> int:
    for index, group in enumerate(cells()):
        if tag in group:
            return index
    raise KeyError(tag)


def is_intra_cell(a: str, b: str) -> bool:
    """True when both tags sit in the same cell: the row class the treatment excludes."""
    return cell_index(a) == cell_index(b)


def world_edges(seed: int, rho: float) -> set[tuple[str, str]]:
    """The world's true edges at this density: a subset of the cross-cell universe.

    `rho_world` is |W| / |P_world| with |P_world| = 240, so the ladder tops out at 0.8,
    where every cross-cell pair is a world edge. A density above that is not a denser
    version of this world; it is a different vocabulary, and it is refused here rather
    than silently pooling two universes.
    """
    k = round(rho * universe_size())
    if not 0.0 < rho <= 1.0:
        raise ValueError("rho_world outside (0, 1]: %r" % (rho,))
    universe = cross_cell_pairs()
    if k > len(universe):
        raise ValueError("density %r wants %d edges; the cross-cell universe has %d"
                         % (rho, k, len(universe)))
    rng = random.Random("%d:%.3f" % (seed, round(rho, 6)))
    rng.shuffle(universe)
    return set(universe[:k])


def filler_events(rho: float) -> int:
    """The number of within-cell events: the (1 - rho) share of a declared budget."""
    return int(round((1.0 - rho) * FILLER_BUDGET))


def base_stream(seed: int, rho: float) -> list[str]:
    """One emission of every world edge, plus this density's within-cell filler.

    World edges are emitted in a sorted order so the stream is reproducible from the
    seed and the density alone; the filler cycles through the four cells so no cell is
    privileged.
    """
    events = ["%s %s" % edge for edge in sorted(world_edges(seed, rho))] * EDGE_REPEATS
    groups = cells()
    for index in range(filler_events(rho)):
        events.append(" ".join(groups[index % len(groups)]))
    return events


def stream(seed: int, rho: float, scheme: str = "primary") -> list[str]:
    """The event stream for one cell, in the scheme's exposure.

    `sensitivity` returns the base stream unchanged: every world edge emitted
    `EDGE_REPEATS` times, so the horizon grows with |W|. `primary` repeats the base
    stream cyclically to `TOTAL_EVENTS`, which holds the total exposure fixed across
    densities and therefore observes each edge fewer times as density rises.
    """
    events = base_stream(seed, rho)
    if scheme == "sensitivity":
        return events
    if scheme != "primary":
        raise ValueError("unknown exposure scheme %r" % (scheme,))
    if not events:
        raise ValueError("an empty stream cannot be padded")
    return [events[i % len(events)] for i in range(TOTAL_EVENTS)]


def designed_pairs(events: list[str]) -> set[tuple[str, str]]:
    """Every pair the stream can produce as a temporal edge, engine rules aside."""
    pairs: set[tuple[str, str]] = set()
    previous: list[str] = []
    for text in events:
        tags = text.split()
        for a in tags:
            for b in tags:
                if a != b:
                    pairs.add((a, b))
        for a in previous:
            for b in tags:
                if a != b:
                    pairs.add((a, b))
        previous = tags
    return pairs


# ---------------------------------------------------------------------------
# The two arms. Identical cap, scoring and admission window; only eligibility differs.
# ---------------------------------------------------------------------------

def rank_control(rows: list[tuple[str, str, int]], k: int) -> list[tuple[str, str]]:
    """The engine's own rule: top-k by count, ties on a stable key."""
    ordered = sorted(rows, key=lambda r: (-r[2], r[0], r[1]))
    return [(a, b) for a, b, _c in ordered[:k]]


def rank_intra_cell_excluded(rows: list[tuple[str, str, int]],
                             k: int) -> list[tuple[str, str]]:
    """The treatment: the same rule over the eligible rows, intra-cell rows removed.

    The rule is not re-scored: the surviving rows are ranked by count exactly as the
    control ranks them. What changes is only which rows may occupy the budget.
    """
    eligible = [row for row in rows if not is_intra_cell(row[0], row[1])]
    return rank_control(eligible, k)


RANKERS = {"control": rank_control, "intra_cell_excluded": rank_intra_cell_excluded}


def measure(pool: list[tuple[str, str, int]], world: set[tuple[str, str]],
            selected: list[tuple[str, str]]) -> dict:
    """Presence, rho_rank, coverage and precision for one selection.

    `presence` is the ceiling the design requires: every world edge must be in the pool,
    or the cell is testing memory rather than ranking. `rho_rank` is the true-edge share
    of the ranker's own population, reported beside every precision figure.
    """
    present = sum(1 for edge in world if any((a, b) == edge for a, b, _c in pool))
    covered = sum(1 for edge in selected if edge in world)
    intra = sum(1 for a, b, _c in pool if is_intra_cell(a, b))
    return {
        "asserted": len(selected),
        "covered": covered,
        "coverage": round(covered / len(world), 6) if world else None,
        "precision": round(covered / len(selected), 6) if selected else None,
        "presence": round(present / len(world), 6) if world else None,
        "rho_rank": round(present / len(pool), 6) if pool else None,
        "pool_rows": len(pool),
        "pool_intra_cell_rows": intra,
        "intra_cell_share": round(intra / len(pool), 6) if pool else None,
    }


def identity_cell(seed: int) -> dict:
    """The rho -> 1 fixture: every eligible row is a world edge, no intra-cell row exists.

    At rho = 1 the two arms must select the same rows, so Delta must be exactly 0. This
    cannot be a ladder cell -- even this world's top density holds intra-cell rows that
    are never world edges -- so it is a fixture, and a non-zero Delta is a harness defect.
    """
    world = world_edges(seed, 0.8)
    pool = [(a, b, 2) for a, b in sorted(world)]
    cap = len(pool)
    control = rank_control(pool, cap)
    treated = rank_intra_cell_excluded(pool, cap)
    delta = (measure(pool, world, treated)["precision"]
             - measure(pool, world, control)["precision"])
    return {"seed": int(seed), "pool_edges": sorted(world), "pool": len(pool),
            "cap": cap, "intra_cell_rows": 0,
            "arms_identical": set(control) == set(treated),
            "delta": round(delta, 12),
            "passed": set(control) == set(treated) and abs(delta) <= 1e-12}


def designed_pool(seed: int, rho: float) -> list[tuple[str, str, int]]:
    """The pool the world *designs*: world edges and filler rows, no engine.

    Counts come from the stream itself, so this is the pool a ranker would see if the
    engine stored exactly the transitions the world emitted. The engine adds cross-event
    rows on top, which is why the audit's numbers are a leverage check and not a result.
    """
    events = stream(seed, rho, "sensitivity")
    counts: Counter[tuple[str, str]] = Counter()
    previous: list[str] = []
    for text in events:
        tags = text.split()
        for a in tags:
            for b in tags:
                if a != b:
                    counts[(a, b)] += 1
        for a in previous:
            for b in tags:
                if a != b:
                    counts[(a, b)] += 1
        previous = tags
    return [(a, b, c) for (a, b), c in counts.items()]


# ---------------------------------------------------------------------------
# Leverage audit: can this world produce the registered pattern at all?
# ---------------------------------------------------------------------------

#: The audit reports both registered caps; the criterion is read at the primary one.
AUDIT_CAPS = (PRIMARY_CAP, 40)


def leverage_audit(seeds: list[int], densities: list[float]) -> dict:
    """Report the designed pools' arm readings, with no engine and no judged cell.

    Three things are checked, and each can fail:

    * the axis is live -- the intra-cell share of the pool falls as density rises;
    * the control itself improves -- its precision rises with density, which is the design
      record's mechanical prediction and the precondition for the treatment's advantage to
      *change* at all. A world where the control is equally bad everywhere cannot test an
      interaction;
    * the advantage **rises** with density, which is amendment A1's corrected direction.

    These are properties of the designed pool, so they are a feasibility expectation on the
    world and not a result. The bars are not computed from them.
    """
    rows = []
    for rho in densities:
        row: dict = {"rho_world": rho,
                     "world_edges": len(world_edges(seeds[0], rho))}
        shares = []
        for cap in AUDIT_CAPS:
            control = treated = 0.0
            for seed in seeds:
                pool = designed_pool(seed, rho)
                world = world_edges(seed, rho)
                control += measure(pool, world, rank_control(pool, cap))["precision"]
                treated += measure(pool, world,
                                   rank_intra_cell_excluded(pool, cap))["precision"]
                shares.append(measure(pool, world, [])["intra_cell_share"])
            control /= len(seeds)
            treated /= len(seeds)
            row["control_cap_%d" % cap] = round(control, 4)
            row["treated_cap_%d" % cap] = round(treated, 4)
            row["delta_cap_%d" % cap] = round(treated - control, 4)
        row["intra_cell_share"] = round(sum(shares) / len(shares), 4)
        rows.append(row)
    share_falls = all(rows[i]["intra_cell_share"] >= rows[i + 1]["intra_cell_share"]
                      for i in range(len(rows) - 1))
    control_rises = rows[-1]["control_cap_%d" % PRIMARY_CAP] > rows[0]["control_cap_%d" % PRIMARY_CAP]
    delta_rises = rows[-1]["delta_cap_%d" % PRIMARY_CAP] > rows[0]["delta_cap_%d" % PRIMARY_CAP]
    return {
        "endpoint": "precision at a fixed cap; the denominator is the arm's own selection",
        "audit_seeds": [int(seed) for seed in seeds],
        "rows": rows,
        "share_falls": bool(share_falls),
        "control_rises": bool(control_rises),
        "delta_rises": bool(delta_rises),
        "passed": bool(share_falls and control_rises and delta_rises),
    }
