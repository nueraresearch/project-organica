# World-edge density: a design record, not an explanation (2026-11-07)

**Status: an untested hypothesis. No cell, no seed, no threshold, no bar, no claim.**
Everything numeric is in `docs/world_density_design.json`.

## 1. The one non-inference to state first

The 448-cell decay calibration is **not evidence for or against this hypothesis.** It
held world geometry fixed and varied a threshold; density was never a manipulation.
Its null belongs to the one-threshold question, and `docs/DECAY-NULL-SCOPE.md`
already bounds it. Density is promoted here as a *serious, untested* possibility,
not as the explanation for anything already observed.

## 2. The measure: density of W in C, not a count of edges

Let **C** be the directed, non-self tag pairs of the world's own vocabulary, so
|C| = n(n-1), and let **W** be the world's true directed edges. The independent
variable is **|W| / |C|**.

| tags | |C| |
|---|---|
| 16 | 240 |
| 24 | 552 |
| 32 | 992 |

For 16 tags, |C| = 240, which is exactly the 240 world-tag pairs the Gate 13
separation isolates. That is also why edge *counts* are the wrong axis: **500 true
edges is impossible at 16 tags.** It needs at least **23** tags, where
|C| = 506 and 500 edges is a density of **0.988** — a nearly complete graph,
not a denser 16-tag world. Any protocol that says "500 edges" has silently changed
the vocabulary, and with it the candidate universe.

At a fixed 16 tags the declared levels and their counts are:

| density | true edges |
|---|---|
| 0.1 | 24 |
| 0.2 | 48 |
| 0.4 | 96 |
| 0.6 | 144 |
| 0.8 | 192 |

## 3. "Hold everything else fixed" is a choice, so name it

Two schemes, both defensible, and they are not the same experiment:

* **Primary — fixed total exposure.** Same events and cycles at every density. The
  world gets denser while the curriculum stays constant, so each edge is observed
  **fewer times** as density rises. A density effect here may be an
  observation-starvation effect.
* **Sensitivity — fixed exposure per edge.** Cycles scale with |W|, so every edge is
  observed about the same number of times and the curriculum **lengthens** with
  density.

The rule: **a density effect that reverses under the other scheme is an exposure
artifact, not geometry.** Neither scheme is the truth; the pair is what separates
the two accounts.

Two confounds to hold explicitly: fix the **tag count**, so |C| and every
source-frequency denominator stay fixed — adding tags for higher edge counts is a
separate arm and is never pooled with the fixed-vocabulary ladder — and keep one
world family and one horizon per arm.

## 4. The comparison that can actually answer it

At each density, run the **same ranking intervention and its control**, differing
only in the selection rule. The estimand is

> **Delta(d) = treated(d) − control(d)**

and the hypothesis is about the **shape of Delta across densities**, not about
density itself. Two things follow:

* A main effect of density is **not** an interaction. A world where everything gets
  harder tells you nothing about whether geometry is the lever.
* An interaction does **not** show that density caused an earlier failure. It shows
  the intervention's value is density-dependent, which is a claim about the
  interaction and nothing more.

A flat Delta falsifies "geometry is the lever for this ranking bottleneck". It does
not falsify density as a factor somewhere else, and it does not license the reverse
reading either.

## 5. Why density is plausible, and why it is not yet the explanation

Gate 13 established that the constraint was **not presence**: all 112 true world
edges were in memory, and the engine's own global count-ranked top 20 still
recovered 0–1 of them (0–3 in the five-seed capacity sweep), rising only to 1–8 at
cap 40 and 106–109 at top 320 — roughly sixteen times the engine's budget. The
competition is intra-cell: a cell's two tags co-occur in every event of that cell,
so co-occurrence rows outrank world relations that occur less often per cycle.

That makes density a plausible moderator — a world with more of its |C| realised
gives a frequency-ranked selector more true edges to find near the top — but the
same evidence points at **ranking** as the proximate bottleneck, and the two are
not separable by looking at a single world. Separating them is what §4 is for.

One caution that must travel with the number: **0.3438** is the maximum precision
observed for the tested frequency-based allocation rules and budgets in that world
family. It is not an information-theoretic bound, and quoting it as "the ceiling"
would turn a property of two rules into a property of the problem.

## 6. Endpoints, and what would count as an answer

* **Presence ceiling**: |W available in memory| / |W|, which must be 1.0 or the cell
  is testing memory rather than selection.
* **Coverage**: |asserted ∩ W| / |W|, the density-normalised main readout.
* **Precision**: |asserted ∩ W| / |asserted|, reported beside coverage, never merged
  with it.
* **Recovery distribution** at each budget — a distribution, never the rank of the
  first edge.
* **Interaction**: Delta(d) across levels, with the paired interval on the
  difference of differences.

## 7. What this record does not do

It allocates nothing: **0 seeds, 0 cells, 0 thresholds, 0 bars**. Bars and seeds are
fixed in a pre-registration with fresh seeds, per `docs/DECAY-TUNING-CYCLE.md`, and
the calibration null may not be offered as support for the hypothesis in that
document.
