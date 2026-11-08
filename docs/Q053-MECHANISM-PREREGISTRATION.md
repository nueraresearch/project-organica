# Q053 mechanism preregistration: one floor, one block, one reading

Generated from `docs/q053_mechanism_prereg.json` by `python -m benchmarks.q053_mechanism_prereg --render`. Do not edit by hand.

**Status: FROZEN, NOT RUN.** No cell has run. The mechanism is specified and **not implemented**; implementing it is an owner decision and is not authorised by this record.

## The question

Can a second-competing retention floor preserve competing hypotheses through consolidation without touching the decay constant, and does preserving them produce a late recall@5 gain over shipped 0.95?

Scope: **lattice_L1**, stimulus `L1_hub1_t3_disjoint`, through the online next-cycle recall@5 instrument at `k = 5`. burst_L1 is excluded: Q052 amendment A2 classified its late collapse DIFFERENT_SUPPORT_COLLAPSE, so it is not a second instance of this mechanism and may not be pooled. A burst block would need its own matched arms.

## The mechanism

**second-competing retention floor** (`RetainSecondCompetingSleepService`).

at the consolidation prune, for each subject that still holds hypotheses, keep the highest-support hypothesis of each of the subject's top two expectations, exempt from the death threshold. Every other candidate is pruned exactly as shipped.

| Field | Value |
| --- | --- |
| competition floor | 2 |
| order | expectations ordered by their best hypothesis's support_count descending; ties broken on the expectation tag |
| scope | applies per subject, inside the existing prune pass; no other layer changes |

**Why it should work.** the control's death leaves subjects holding two retention pairs but no subject holding two competing expectations, so exempting the top two expectations keeps exactly the structure theory formation needs, and can raise the late competition share without moving any decay constant

**Risk, stated before the run.** a stale minority survives on old evidence and competes with the current best, which is why the capability criterion and the early-cost bound are judged separately rather than merged into one score

**Edge case.** if a subject holds one expectation only, the floor keeps it and adds nothing; the mechanism cannot manufacture competition

It preserves: the decay constant 0.95; the death threshold 0.15; the confidence formula; the hypothesis cap; the candidate set and which structures compete. It does not: create or regenerate hypotheses; lower the global decay factor; reserve a separate budget pool; displace high-support structure outside the subject; change admission, ranking or selection.

## The two arms

| Arm | Service | Decay | Death threshold | Rule |
| --- | --- | --- | --- | --- |
| control | `organica.sleep.SleepService` | 0.95 | 0.15 | the shipped engine, no subclass, no-op |
| treatment | `the in-process RetainSecondCompetingSleepService` | 0.95 | 0.15 | the shipped engine plus the second-competing retention floor at the prune |

The decay factor is held at 0.95 in **both** arms: the treatment may not buy its effect with persistence, and the run artifact is refused if either arm records a different value.

## The block

| Field | Value |
| --- | --- |
| world seeds | 20410101, 20410102, 20410103, 20410104, 20410105, 20410106, 20410107, 20410108, 20410109, 20410110 |
| bootstrap seed | 20410111 |
| cells | 20 (2 arms x 10 seeds = 20 cells) |
| cycles per cell | 300 |
| early window | 40-90 |
| late window | 240-300 |
| pairing | both arms of a seed run on the same seed-determined world; only the service class differs |

Freshness: the first contiguous window of eleven integers at or above 20410101 that appears in no artifact, harness, test, document or journal in the repository; the eleventh is the bootstrap seed and is not a world seed.

## Criteria, in the order they are read

| Criterion | Quantity | Rule | Bar | Provenance |
| --- | --- | --- | --- | --- |
| M1_mechanism | late-window competition share -- the fraction of late cycles in which at least one subject retains two competing hypotheses | median per-seed gap (treatment minus control) at or above the manipulation bar | 0.25 | declared, not calibrated: no committed block measures this quantity, so there is no honest calibration set, and the bar is placed where the manipulation is visible rather than marginal. It is a manipulation check, not a capability criterion. |
| C1_capability | late-window recall@5 over cycles 240-300, median per-seed gap (treatment minus control) | median gap at or above the bar, bootstrap interval lower bound above zero, and at least seven of ten seeds with a positive gap | 0.0133 | carried as policy from Q051's confirmatory block: one half of its measured late median gap, 0.0265 / 2 = 0.01325, rounded up to 0.0133. It is NOT calibrated on this layer, this contrast or this mechanism; a pass means the treatment cleared a bar fixed before this block ran. |
| C2_early_cost | early-window recall@5 over cycles 40-90, median per-seed gap | median gap at or above the early-cost bound | -0.01 | Q051's early equivalence margin, carried unchanged; a larger early loss prices the trade and blocks adoption |

A failed `M1_mechanism` leaves the capability endpoint **unread**: an unrun experiment, not a null. `C1_capability` additionally requires an interval lower bound above zero and 7 of 10 positive seeds; an interval wider than 0.3 is reported as underpowered.

## Gates, which void the block before any criterion is read

| Gate | Requirement |
| --- | --- |
| G1_liveness | the control's late theory count must be zero in at least 90 percent of its late cycles on every seed; if the control survives, the block compares two live arms and is void |
| G2_noop_control | the control's structure fingerprint must equal the shipped engine's fingerprint recorded in the run artifact |
| G3_determinism | the control re-run on the first seed must reproduce its recorded fingerprint |
| G4_persistence_confound | both arms must record decay 0.95 and death threshold 0.15 in the run artifact; a treatment that differs on either is void, because the mechanism may not buy its effect with persistence |
| G5_seed_block | the cells must be exactly the frozen block, with both arms of every seed and no cell outside it |
| G6_denominator | every cell must report at least one prediction in each window; a cell with none is not measurable and the block is void |

Void rule: a failed gate voids the block and no criterion is read.

## The decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
| any gate fails | VOID | the block is unrun; the gate that failed names what did not happen, and no criterion is read |
| gates pass; M1 fails | MECHANISM DID NOT OPERATE | the floor did not raise the late competition share, so the capability endpoint was never run; this is not evidence that preservation cannot help |
| gates pass; M1 passes; C1 passes; C2 passes | COMPETITION PRESERVED WITH CAPABILITY GAIN | the mechanism keeps competing hypotheses alive and the late ranking gain clears the bar without an early cost; adoption is still an owner decision and is not implied by the label |
| gates pass; M1 passes; C1 fails | COMPETITION PRESERVED, NO CAPABILITY GAIN | preservation is real and insufficient: the preserve-to-capability link is not established, and the mechanism is recorded without adoption |
| gates pass; M1 passes; C1 passes; C2 fails | GAIN AT AN EARLY COST | the late gain is bought with early ranking, so the trade is priced and nothing is adopted |
| gates pass; M1 passes; C1 interval wider than 0.30 | UNDERPOWERED | the block cannot separate a gain from zero; this is reported as underpowered rather than as a negative |

## Adoption

a capability gain is necessary but not sufficient: the mechanism must also pass M1, clear C1, keep C2, and pass every gate; adoption then requires a recorded owner decision, and nothing in this block changes the engine by itself

Not authorised by this block: a decay-factor sweep; a second mechanism or a parameter sweep of this one; pooling burst_L1 cells into this block; re-scoring a criterion after the block runs.

## Stop condition

one mechanism, one protocol, one confirmatory block of twenty cells. The record may be fixed if it is found wrong; it may not grow into a second mechanism, a second endpoint or an additional block without a new preregistration.

Cost: 20 cells at 300 cycles each. no cell has run; the cost is stated so the block is not opened casually

## What this does not claim

Nothing here shows that competition preservation improves capability, that the floor can be implemented as described, or that a result would generalise beyond this world family. The mechanism has not been built, no cell has run, and the engine is unchanged.
