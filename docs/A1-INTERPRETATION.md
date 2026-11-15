# What the A1 preparation record adds up to

**Date:** 2026-11-15

**Status:** `INTERPRETATION — NO NEW MEASUREMENT, NO CELL, NOTHING IN FORCE`

**This document runs nothing and adds no artifact.** Every number in it is already committed elsewhere and is cited. Its only contribution is putting the measurements beside each other, because each was recorded to answer its own question and nobody has read them as one record. Nothing here decides an owner question.

## The finding the separate records do not state

**C8's twenty-row failure is combinatorial before it is empirical, and the two ways to relieve it destroy each other.** That is arithmetic on numbers already measured, not a hypothesis.

The published N=20 rule caps selected edges at **3 per tag** with one orientation per relation. Sixteen tags therefore admit at most `16 × 3 / 2 = 24` relations, of which twenty are needed: **four edges of slack, 20% headroom**, and any tag imbalance spends it. That is what "impossible on `20740102`" is — that seed's competent rows are distributed such that no twenty-row selection fits the cap, which is exactly what enumerating all 888,030 subsets confirmed (`A1-COMPETENCE-FILTER-DRAFT-1`). The N=4 design selects four *disjoint* targets, which on sixteen tags admits `16 / 2 = 8` and needs four — also four edges of slack, but **100% headroom**. Same absolute slack, five times the relative room. Nothing about the world changed between those two designs; only N did.

So the obvious repair is more tags, which raises the ceiling to `28 × 3 / 2 = 42` with 22 edges of slack. And that repair is measured, and it fails: at 28 tags the competent pool falls from **20–46** rows per seed in the 16-tag world to **15–26** in the 28-tag world — below the twenty required on four of six seeds — because A&K density falls from **63.2% to 24.4%** while candidate edges rise 161% and K-available rows rise **0.8%** (`A1-K-DILUTION-1`, `A1-LARGER-UNIVERSE-CANDIDATE-1`, preflight `FAIL 0/6`).

**Sixteen tags fit twenty rows under the cap with four edges of slack, and the measured 16-tag pool bottoms out at exactly twenty on one seed — no room for imbalance. Twenty-eight tags fit them with 22 edges of slack and cannot fill them.** No tag count between the two has been measured; the pincer is arithmetic at both ends, so it will not be escaped by picking seventeen or twenty-two. The question is which constraint to move.

## Why the world does not supply the missing K

Three levers have been tried and all three return sublinear or descriptive answers, which is the substance of the record:

| Lever | Measured response | Consequence |
| --- | --- | --- |
| More edges (28-tag world) | +161% candidates, **+0.8%** K rows, density 63.2% → 24.4% | dilution, not supply (`A1-K-DILUTION-1`) |
| Higher loop cap (15 → 120) | K 714 → 1498 (**+109.8%**) for an 8× cap, two edges lost | window-limited and strongly sublinear, with reshuffling (`A1-LOOP-CAP-COUNTERFACTUAL-1`) |
| Higher prediction cap (20 → 112) | one shared √ curve + block offset, LOO RMSE 0.0193; block-specific slopes no better | no per-block lever, a single saturating curve (`A1-CAP-RESPONSE-CURVE-1`) |

Read together these say something the individual documents do not: **K is not a resource that more universe buys.** It is a resource that a *window* buys — the loop-cap counterfactual raises it 110% by lengthening the view, and the 16-tag blocks reach 382/383 candidates K-available at cap 120. The registered design's K shortfall is therefore substantially an artifact of how much history the engine's loop window holds, not of how many relations exist. That is why the 28-tag world fails: it multiplies relations while the window stays fixed.

## What this says about C1, and about which block was adopted

C1's directed reading clears the 0.95 floor on **6 of 6** adopted seeds (64–79 rows against 61) and on **4 of 6** of the earlier block (58–72 against 60, `A1-DESIGN-VIABILITY-1`). The margin on the tightest adopted seed is **three rows**. That is a real clearing, and it is thin enough that it should be described as such rather than as capacity.

The three measured blocks separate sharply: `2063` clears 4/6, `2074` clears 6/6, `2065` clears 0/6 (K-available 37–46, `A1-K-DILUTION-1`). So "is C1 reachable?" has no block-free answer in this record — it has a *block-dependent* answer, and the block in use is the best of the three measured. Which block A1 runs on is therefore itself a selection parameter, and it belongs in the declaration beside the denominator and the unit.

## What the record supports A1 claiming, today

Put together, the preparation supports one configuration without any engine or world change: **run C1, C7 and C4 on a declared block, with C8 recorded as not adjudicable on this design and the reason stated as combinatorial capacity plus K density rather than as treatment failure.** Under that reading A1 tests carrier separation and inter-path blocking with a declared hole where the third route would be.

It does not support claiming C8 at N=20 on sixteen tags, on any block, under the current cap — that is arithmetic, not a result that a different seed might overturn. It also does not support the 28-tag repair, which is measured and fails 0/6.

## The one lever the record has not tested

Every attempt so far changed the **number of relations** (tags, edges, seeds) or the **prediction cap**. None changed the **event density per cycle at fixed tag count** — the measured worlds run 8 events per cycle. K is window-limited, so density and window are the two quantities that should matter, and only the window has been moved. That is a statement about what the record covers, not a proposal to run it; it is recorded here so the gap is visible when the owner weighs a redesign.

## What would change this reading

A C8 block forming on every adopted seed would refute the capacity arithmetic — it cannot, because the cap and tag count are fixed, which is why the impossibility is exhaustive rather than empirical. A density change at sixteen tags clearing the A&K pool above twenty on six seeds would reopen the design without touching the tag count. An owner decision to accept a lower N for C8 — at the cost of a coarser `1/N` step — sidesteps the arithmetic entirely and is a legitimate choice this record cannot make.

## What this document is not

It is not a redesign, not a freeze, not a grant, not a disposition, not a measurement, and not a decision. It repeats no numbers that are not already committed, and it recomputes nothing. If it is wrong, it is wrong in the reading, and the artifacts it cites will say so.
