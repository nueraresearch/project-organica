# World-edge density: a design record, not an explanation (2026-11-07, revised)

**Status: an untested hypothesis. No cell, no seed, no threshold, no bar, no claim.**
Every number is in `docs/world_density_design.json`.

## 1. The non-inference to state first

The 448-cell decay calibration is **not evidence for or against this hypothesis.** It held
world geometry fixed and varied a threshold; density was never a manipulation. Its null
belongs to the one-threshold question, bounded in `docs/DECAY-NULL-SCOPE.md`. Density is a
serious, untested possibility here, not the explanation for anything already observed.

## 2. Two candidate universes, and why the distinction is the design

There are two different populations, and only one of them is a world knob.

* **`P_world`, the oracle-filtered universe.** Directed non-self pairs of the world's own
  vocabulary, so |P_world| = n(n-1). The ratio **rho_world = |W| / |P_world|** is a property of
  the world and is what this record manipulates.
* **`P_rank`, the population the ranker actually sees.** The rows the frozen engine holds at
  the end of a run — intra-cell co-occurrence, sleep-sourced pairs (the D2 mechanism), and any
  pair over the world vocabulary. The ratio **rho_rank = |W and P_rank| / |P_rank|** is produced
  by the engine, so it is **measured per cell, never set**.

They can move in different directions. `P_rank` grows with contamination and with intra-cell
mass, and it shrinks when a selector or a threshold prunes rows. A design that reports only
rho_world is reporting a world property as if it were the ranker's difficulty.

| tags | |P_world| |
|---|---|
| 16 | 240 |
| 24 | 552 |
| 32 | 992 |

At 16 tags, |P_world| = **240** — the same 240 world-tag pairs the Gate 13 separation
isolates. And 500 true edges is impossible there: it needs at least **23** tags,
where |P_world| = **506** and 500 edges is rho_world **0.988**, a nearly complete
graph. That is a scale change, not a density change, and it may not be pooled with the
fixed-vocabulary ladder.

Declared levels at a fixed 16 tags:

| rho_world | true edges |
|---|---|
| 0.1 | 24 |
| 0.2 | 48 |
| 0.4 | 96 |
| 0.6 | 144 |
| 0.8 | 192 |

One consequence is an arithmetic bound, and this record's first statement of it was
**wrong**. **A k-row selection cannot contain more world rows than the pool holds**, so
precision cannot exceed **min(1, |W and P_rank| / k)**. The earlier version of this
paragraph said precision cannot exceed rho_rank; that is false whenever the ranker prefers
world rows, and the density review measured it false: at rho_world 0.8 the control's
precision was **1.000 against** a rho_rank of **0.800**
(`docs/DENSITY-INTERACTION-REVIEW.md`). Every precision figure this study reports still
travels with its rho_rank and with the budget it was measured at.

## 3. Exposure is a separate choice, named in advance

* **Primary — fixed total exposure.** Same events and cycles at every level, so each edge is
  observed fewer times as density rises.
* **Sensitivity — fixed exposure per edge.** Cycles scale with |W|, so the curriculum lengthens
  with density.

The rule: **a density effect that reverses under the other scheme is an exposure artifact, not
geometry.** Neither scheme is the truth; the pair separates the two accounts.

Held fixed: the tag count (so |P_world| and every source-frequency denominator stay put), one
world family, one horizon per scheme, and the frozen engine.

## 4. Treatment and control, each named for what it changes

* **Control — global count-ranked top-k.** The engine's own selection: rank every candidate by
  count, take the top k at the frozen cap.
* **Treatment — intra-cell-excluded ranking.** Identical cap, identical scoring, identical
  admission window; intra-cell co-occurrence rows are simply not eligible for the top-k.

The two arms are identical by construction in candidate generation, cap, scoring, admission
window, world, seed, exposure and horizon. The treatment changes **only what may occupy the
budget**, so a gain is budget competition, not a better score. That matters because Gate 13
measured the top-20 as 75–100% intra-cell: a row class that cannot be a world edge was holding
budget that world edges needed.

## 5. Predicted direction, registered before any cell

Three predictions, stated so they can fail:

1. The **control's** precision rises with rho_world, mechanically, because the population it
   samples is denser. This is predicted and it is *not* the claim.
2. **Delta(rho) = treated − control declines as rho_world rises.** The advantage is largest at
   the lowest level, where control coverage is near zero.
3. As rho_world approaches **1**, every candidate is a true edge, the two arms must select the
   same rows, and Delta must go to **0**. A non-zero Delta there is a harness defect, not a
   result.

Falsifiers, named in advance: **flat** Delta means geometry is not the lever for this ranking
bottleneck; **rising** Delta means the mechanism claim is wrong and something other than budget
competition is being measured; a non-zero Delta at rho_world = 1 means the arms are not
identical where they must be.

**Amended before any cell — amendment A1 in §10.** The direction registered in prediction 2
is superseded; the prediction itself is retained above, because a design record that rewrites
its own prediction cannot be tested.

## 6. The contrast that answers the question

At each density, the same treatment and control; the estimand is Delta(rho) and the hypothesis
is about its **shape across levels**. Two things it is not:

* A **main effect of density** is not an interaction. A world where everything gets harder says
  nothing about whether geometry is the lever.
* An **interaction** does not show density caused an earlier failure. It shows the
  intervention's value is density-dependent, and nothing wider.

## 7. Endpoints

* **Presence ceiling**: |W available in memory| / |W|, which must be 1.0 or the cell tests memory.
* **Coverage**: |asserted and W| / |W|, reported with its denominator.
* **Precision**: |asserted and W| / |asserted|, reported beside rho_rank and bounded by it.
* **Recovery distribution** across budgets — a distribution, never the rank of the first edge.
* **Interaction**: Delta(rho) with a paired interval on the difference of differences.

## 8. Why density is plausible, and why it is not yet the explanation

Gate 13 established the constraint was **not presence**: all 112 true world edges were in
memory, and the engine's own count-ranked top 20 still recovered 0–1 of them (0–3 in the
five-seed capacity sweep), reaching 1–8 at cap 40 and 106–109 at top 320 — about sixteen times
the engine's budget. The competition is intra-cell. That makes density a plausible moderator,
and it points at **ranking** as the proximate bottleneck; a single world cannot separate them,
which is what §5–§6 exist for.

One caution that must travel with the number: **0.3438** is the maximum precision observed for
the tested frequency-based allocation rules and budgets in that world family. It is not an
information-theoretic bound, and quoting it as "the ceiling" would turn a property of two rules
into a property of the problem.

## 9. What this record does not do

It allocates nothing: **0 seeds, 0 cells, 0 thresholds, 0 bars**. Bars and seeds are fixed in a
pre-registration with fresh seeds, per `docs/DECAY-TUNING-CYCLE.md`.

## 10. Pre-run amendment A1 (2026-11-07): the direction, corrected before any cell

§5's second prediction is **superseded** and retained above unedited. The correction came
from this record's own world, measured with no engine and no judged cell: on the designed
pools over the block's registered seeds, the treatment's advantage at the primary cap is
**0.075** at rho_world 0.1 and **0.350** at 0.8. It **rises** with density; §5 predicted it
would fall. Over the same ladder the control's own precision rises and the intra-cell share
falls, as §5's first prediction says. The per-density table and every figure live in
`docs/density_interaction_prereg.json` (`leverage_audit`), not here.

Why the prediction was wrong: the benefit of freeing budget is bounded by how many world
rows exist to fill it. A sparse world has too few world edges for the freed budget to spend
on, so the advantage is **small there by construction**, and it is the dense end that can
use the freed slots. §5 reasoned from coverage's denominator — small |W|, large relative
gain — to a claim about a fixed budget, which is the denominator slip §2 warns about.

What changes is registered as A1 in `docs/density_interaction_prereg.json`: the
manipulation, world family, arms, caps, endpoint, seed block and bars are unchanged, and the
criterion tests the corrected direction. "Rising" therefore stops being a falsifier of the
claim and becomes the claim, with its own falsifiers — flat, or falling — registered before
the first cell. The block itself is `docs/DENSITY-INTERACTION-PREREGISTRATION.md`.
