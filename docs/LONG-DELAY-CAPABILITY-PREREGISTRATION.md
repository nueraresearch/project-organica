# Long-delay capability preregistration (Q051)

**Status:** frozen before any confirmatory cell. The pilot in
`benchmarks/long_delay_capability.py` is a design probe, not a result: its
seed block (20302801-20302802) is excluded from this design, and no cell of
this protocol has been run.

## 1. Question

Does the smallest surviving temporal-decay factor, **0.9925**, rank the next
cycle's tags better than the shipped **0.95** at a horizon where the shipped
theory layer is already dead, and is the advantage absent early?

This is a claim about **next-cycle tag ranking**, not about intelligence,
theory quality, or adoption. The theory layer's survival is a manipulation
check, not the outcome.

## 2. Why this instrument

The committed held-out benchmark freezes the model after cycle 200, so decay
cannot act inside its scored window and a persistence difference cannot
appear there. This protocol keeps the organism in the loop: after each
cycle's consolidation it reads the engine's own `report.predictions`, scores
them against the next cycle, and only then ingests that cycle. The pilot
showed the two endpoints diverge: 0.9925 ranked slightly better while its raw
log loss was much worse, the signature of uncalibrated strengths. Ranking is
therefore primary and calibration secondary.

## 3. World

`lattice_L1` (`L1_hub1_t3_disjoint`) with **one seed-determined stable rare
cross-triangle edge**: a pair of tags chosen by the seed, emitted as a single
event on the last slot of every 40th cycle. The edge recurs, so it is
learnable; its period is long enough that a fast-decaying arm loses it
between occurrences. The triangle scaffold and the block order are held
fixed. This is a schedule-and-content variation of the same world family, not
a new world.

The pilot used random distractors and was rejected: random pairs recur only
by chance, so retention accumulated noise and the persistence arm looked
worse for a reason unrelated to the claim. The stable rare edge replaces
that confound.

## 4. Arms and cells

| Arm | `TEMPORAL_DECAY_FACTOR` | Role |
| --- | --- | --- |
| shipped | 0.95 | primary comparator |
| mid | 0.99 | dose-response, secondary |
| survivor | 0.9925 | primary arm |
| ceiling | 1.0 | ceiling, secondary |

Every arm runs the same stream for a given seed. Arms are in-process
subclasses of `SleepService`; the engine files are untouched.

Cells: 300 cycles, eight events per cycle, one database per cell.

## 5. Seeds

| Block | Seeds | Use |
| --- | --- | --- |
| design | 20302901-20302905 | calibrate the bar and check the gates; **not judged** |
| confirmatory | 20302911-20302920 | judged once against the frozen bar |

Both blocks must be disjoint from every integer under a seed key in
`docs/*.json`; `benchmarks/long_delay_capability_prereg.py` checks this and
the campaign does not run if it fails. The pilot's seeds (20302801-20302802)
are excluded.

## 6. Windows and endpoint

- **Early:** cycles 40-90. Both theory layers are expected alive.
- **Late:** cycles 240-300. The shipped arm is expected dead well before 240.

Primary endpoint: **mean recall@5** over consecutive event pairs, where for
each source tag in the previous event the engine's top five target tags by
`strength` are checked against the next event's tags. `k = 5` is frozen; the
pilot used the same value.

Secondary endpoint: binary log loss over the same pairs, using `strength` as
a probability. It is reported, never a criterion, because calibration is not
established.

Per cell, the gap is `recall(0.9925) - recall(0.95)` within a seed and
window. The confirmatory statistic is the **median gap over the ten
confirmatory seeds**.

## 7. Bar

The design block estimates the standard deviation of the per-seed late-window
gap. The bar is

```
delta = max(0.010, 1.5 * sd_design)
```

fixed before the confirmatory block is seen. The confirmatory result passes
the late criterion when **both** the median gap is at least `delta` **and**
at least 8 of 10 seeds have a positive gap. The early criterion is an
equivalence check: the median early gap must be smaller than `0.010` in
absolute value.

## 8. Predictions

- **P1 — early equivalence.** The early-window median gap is within
  `[-0.010, +0.010]`. The pilot's early gap was positive, so this prediction
  is a real test, not a formality.
- **P2 — late advantage.** The late-window median gap is at least `delta`,
  with at least 8 of 10 seeds positive.
- **P3 — growth.** The late gap exceeds the early gap in at least 8 of 10
  seeds.
- **P4 — calibration, secondary.** The late log-loss gap is reported with
  its sign and interval; no decision depends on it.

## 9. Gates

Every gate must be able to fail; a failing gate voids the block.

| Gate | Check | Failure |
| --- | --- | --- |
| G1 seed liveness | per-arm early recall differs across at least two seeds | `VOID_SEED_DEGENERATE` |
| G2 arm liveness | 0.95 theory count is 0 by cycle 240; 0.9925 count is > 0 at 300 | `VOID_ARM_NOT_MANIPULATED` |
| G3 predictor liveness | late-window predictions are non-empty in every confirmatory cell | `VOID_PREDICTOR_DEAD` |
| G4 denominator | every window has consecutive event pairs and labels | `VOID_NO_DENOMINATOR` |
| G5 control | a synthetic ranking with a known top-5 is recovered by the scorer, and a deliberately wrong ranking fails it | `VOID_CONTROL` |
| G6 seed disjointness | both blocks are unused in `docs/*.json` | `VOID_SEED_REUSED` |
| G7 digest | the protocol digest matches the committed constant | `VOID_PROTOCOL_CHANGED` |

The control in G5 is the harness's own falsifier: the scorer must recover a
planted ranking and must reject a shuffled one.

## 10. Decision table

| Outcome | Condition | Decision |
| --- | --- | --- |
| `CAPABILITY_EARNED` | P1, P2 and P3 hold; all gates pass | 0.9925 becomes the default candidate for a Phase-J precision block; no adoption until that block runs |
| `LATE_GAIN_EARLY_COST` | P2 holds but P1 fails | the early difference is a confound; do not adopt; diagnose the non-persistence source before another capability cell |
| `PERSISTENCE_WITHOUT_CAPABILITY` | P2 fails and the late gap is not positive | 0.9925 is an operating point, not a capability improvement; close the persistence-to-capability bridge and move to the bottleneck map |
| `INCONCLUSIVE` | intervals too wide or P3 fails while P2 holds | report the interval; the remedy is a larger confirmatory block, not a re-read |
| `VOID` | any gate fails | no claim; the block is rerun only after the named gate is repaired, with a fresh seed block |

`PERSISTENCE_WITHOUT_CAPABILITY` is the most informative outcome: it answers
the question the persistence program was built to ask, and a clean null is a
result, not a failure of the program.

## 11. Stop condition

One design block, one confirmatory block. No extension, no endpoint added
after the freeze, no re-scoring of a failed criterion. A correction is a
dated amendment that says what was wrong and which cells it affects.

## 12. What this cannot claim

- It is one synthetic world family and one engine; it is not a general
  capability result.
- It ranks next-cycle tags; it does not measure belief revision, transfer,
  adaptation, or intelligence.
- It cannot license adoption of 0.9925; that requires the Phase-J precision
  block and is the owner's decision.
- A positive result means "the longer-lived engine ranks better late on this
  world"; a negative result means "on this world, persistence did not buy
  ranking quality." Neither is a statement about all worlds.

## 13. Pilot disclosure

The design was motivated by a two-seed probe on 20302801-20302802 (200
cycles, 0.95 vs 0.9925). Its late gaps were +0.0191 and +0.0357 recall@5,
and its early gaps were +0.0100 and +0.0250, so the early difference is
real and P1 must be able to fail. The probe's raw log loss was much worse
for 0.9925, which is why log loss is secondary. The probe is not a
confirmatory result and its seeds are not reused.
