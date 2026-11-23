# D3 persistence engine replication (G1 recalibrated) — preregistration

Generated from `docs/d3_persistence_g1_recalibrated_prereg.json` by `python -m benchmarks.d3_persistence_g1_recalibrated --render-prereg`. Do not edit by hand.

**Status at freeze: FROZEN, NOT RUN.** No cell had run at freeze. The treatment is the shipped `organica.sleep.SleepService` at 0.14.0; the control is a benchmark-only pre-repair denominator ablation. This block changes no engine file.

**Post-freeze result.** This block ran on 2026-11-10. The result is `docs/D3-PERSISTENCE-G1-RECALIBRATED-RESULT.md`; the verdict is `PERSISTENCE REPAIRED`. This pointer was added after the run and changes no criterion, bar, seed, arm or gate.

## The question

Does the shipped 0.14.0 persistence repair survive six fresh seed-determined worlds against a pre-repair denominator control when G1 is calibrated to the control distribution observed in the prior three D3 blocks?

## Why this replication

Prior block: `D3-PERSISTENCE-3` returned **VOID** (`docs/d3_persistence_engine_replication_run.json`). D3-3's frozen G1 bound (1-60) was below the observed 0.14.0 control maximum of 61; two controls first reached zero at 61 and the block voided before W1/P1/C1 were read.

D3-4 changes only the control-death bound and the seed window. The treatment, control, criteria, stages and 3,000-cycle horizon are carried unchanged. The bound is calibrated on the three prior D3 control blocks, not on D3-4 cells.

## The two arms

| Arm | Service | Decay | Death threshold | Frequency decay | Rule |
| --- | --- | --- | --- | --- | --- |
| control | `benchmarks.d3_persistence_g1_recalibrated.LegacyFrequencySleepService` | 0.95 | 0.15 | none | the pre-repair raw source-frequency denominator, otherwise the shipped 0.14.0 engine |
| treatment | `organica.sleep.SleepService` | 0.95 | 0.15 | 0.95 | the shipped 0.14.0 engine, including the matched source-frequency denominator |

## The block

| Stage | Design | Cycles | What it reads |
| --- | --- | --- | --- |
| witness | `L3_hub1_t3_mixed` | 40 | the whole per-cycle theory trace, plus the NO_DREAMS and NO_QUESTIONS negative controls |
| preflight | `L1_hub1_t3_disjoint` | 3000 | the first cycle with zero theories after a positive one; the treatment runs the full horizon |

| Field | Value |
| --- | --- |
| world seeds | 20611301, 20611302, 20611303, 20611304, 20611305, 20611306 |
| bootstrap seed | 20611307 |
| cells | 24 (2 stages x 2 arms x 6 seeds = 24 cells) |
| early window | 5-36 |
| k | 5 |
| pairing | both arms of a seed run on the same seed-determined world and stimulus; only the service class differs |

**Freshness.** the first contiguous seven-integer window at or above 20611301 that appears in no artifact, harness, test, document or journal; checked before this record was written

**Seed-varying world.** the design's triangle order is shuffled by the seed before lattice_stream, and the resulting stream is rotated by seed modulo its length; the multiset and local triangle structure are fixed, the schedule is seed-determined

**G1 bound.** 1-65 cycles. The control preflight first zero was observed in 18 prior cells: 60 in all six D3-1 cells (one repeated trajectory), 59,59,60,60,60,58 in D3-2, and 60,58,61,61,58,59 in D3-3. The maximum is 61 and the observed spread is 3 cycles (58 to 61). D3-4 sets the bound at 61 + 3 + 1 = 65: the prior maximum plus one full observed spread plus one cycle, fixed before any D3-4 cell runs and not computed from D3-4. The bound is a baseline check, not a treatment criterion; W1, P1 and C1 are unchanged.

## Criteria, in the order they are read

| Criterion | Quantity | Rule | Bar | Provenance |
| --- | --- | --- | --- | --- |
| W1_witness | the treatment's theory cycles and peak on the L3 witness over 40 cycles | at least 39 of 40 theory cycles and a peak of at least 6, on at least 5 of 6 seeds, with both negative controls at zero across the trace | 39/40 cycles and peak 6 on 5/6 seeds | the adopted witness's measured baseline in docs/tier1_preflight.json, not calibrated on the treatment |
| P1_persistence | the treatment's theory count in the last 100 cycles of the L1 horizon | no first zero through cycle 3000 and a theory count above zero in every one of the last 100 cycles, on at least 5 of 6 seeds | 5 of 6 seeds alive at the horizon | 3000 is the campaign's own horizon from D2. The 5/6 bar is declared, not calibrated: the campaign requires one live colony, and a majority guards against a single-seed fluke without demanding every seed. |
| C1_early_cost | next-cycle recall@5 over cycles 5-36, median per-seed gap (treatment minus control) | median gap at or above the early-cost bound | -0.01 | Q051's early equivalence margin, carried unchanged; a larger early loss prices the trade and blocks adoption |

The criteria are judged whole. A failed W1 leaves P1 and C1 unread.

## Gates, which void the block before any criterion is read

| Gate | Requirement |
| --- | --- |
| G1_baseline_death | the control must record a first zero after a positive cycle at or before cycle 65 on every seed; if the control survives, there is no death to repair and the block is void |
| G2_manipulation_live | both arms must record decay 0.95 and death threshold 0.15; the treatment must record frequency_decay 0.95 and a non-zero denominator update in every cycle; a treatment that differs on the decay constant or never updates the denominator is void |
| G3_noop_control | the control's structure fingerprint must equal the shipped engine's fingerprint recorded in the run artifact |
| G4_determinism | the control re-run on the first seed must reproduce its recorded fingerprint |
| G5_seed_block | the cells must be exactly the frozen 24, with both stages and both arms of every seed and no cell outside the block |
| G6_denominator | every witness cell must report at least one early prediction, and every preflight cell must report at least one early prediction; a cell with none is not measurable and the block is void |
| G7_negative_controls | NO_DREAMS must record zero dreams and NO_QUESTIONS zero questions in every witness cycle |
| G8_seed_axis_live | the preflight treatment must produce at least two distinct trajectory signatures across the six seeds; if all six are identical, the block is VOID because the seed axis did not vary the measured trajectory |

Void rule: a failed gate voids the block and no criterion is read.

## The decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
| any gate fails | VOID | the block is unrun; the failed gate names what did not happen, and no criterion is read |
| gates pass; W1 fails | WITNESS BROKEN | the repair damages the L3 witness, so it cannot be adopted for the campaign even if L1 stays alive; the failure is a property of the repair, not of the witness |
| gates pass; W1 passes; P1 fails | NO REPAIR | the arm still dies before the campaign horizon; persistence is not restored, and the campaign remains not measurable as designed |
| gates pass; W1 passes; P1 passes; C1 fails | PERSISTENCE REPAIRED WITH EARLY COST | the arm survives to the horizon but loses early ranking beyond the equivalence margin; the trade is priced and nothing is adopted |
| gates pass; W1 passes; P1 passes; C1 passes | PERSISTENCE REPAIRED | the arm survives to the campaign horizon with the witness intact and no early cost beyond the margin; adoption is still an owner decision and is not implied by the label |

## Adoption and stop condition

The repair is already promoted at 0.14.0. A pass is a replication of the shipped engine and creates no new adoption; a failure opens a correction and does not re-open the historical D3 results.

**Withdrawal.** A W1 failure withdraws the replication claim: the promoted engine does not preserve the witness. A P1 failure records NO REPAIR for this replication. Withdrawal is not deletion: the block stays in the record, and a different mechanism needs its own preregistration.

**Stop condition.** one mechanism, one protocol, one replication block of 24 cells. The record may be fixed if it is found wrong; it may not grow into a second mechanism, endpoint or block.

## What this does not claim

This is a fresh-seed replication of the promoted engine against a pre-repair control. A pass does not establish a new adoption or a transfer claim; it records whether the promoted behavior survives this seed-varying block.
