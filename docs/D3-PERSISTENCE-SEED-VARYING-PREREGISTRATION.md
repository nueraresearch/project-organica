# D3 persistence seed-varying confirmation — preregistration

Generated from `docs/d3_persistence_seed_varying_prereg.json` by `python -m benchmarks.d3_persistence_seed_varying --render-prereg`. Do not edit by hand.

**Status: FROZEN, NOT RUN.** No cell has run. The mechanism is the already-built `MatchedFrequencySleepService`; this record changes no engine file.

**Post-freeze result.** The status and text above are the frozen pre-run record. The block has since run; its result is `docs/D3-PERSISTENCE-SEED-VARYING-RESULT.md`. The repair was promoted into the engine at 0.14.0 by the dated owner decision. This pointer is outside the frozen protocol and changes no criterion, bar, seed, arm or gate.

## The question

Does matched source-frequency decay keep the reference arm alive to the campaign horizon on independent, seed-determined worlds, without breaking the L3 witness or costing early next-cycle recall?

**Prior result.** `D3-PERSISTENCE-1` on `docs/d3_persistence_run.json` returned **PERSISTENCE REPAIRED**, but its seed axis was degenerate: all six seeds produced the same per-cycle trajectory, early recall and prediction counts; effective n = 1. The seed was applied to the service RNG, but the lattice stimulus was fixed, so it never varied a world.

The first block is a single-trajectory mechanism result. This confirmation asks whether the repair survives a seed axis that actually varies the world schedule.

## The mechanism

**matched source-frequency decay** (`MatchedFrequencySleepService`).

Each cycle, before Layer 1 predictions are built, maintain a per-tag decayed frequency D(tag) = 0.95 * D_previous(tag) + delta(tag), where delta is the increase in memory.tag_frequencies() since the previous cycle and the first cycle starts from the raw counter. Prediction strength uses temporal_count / max(D(source), 1) instead of temporal_count / raw_tag_count. The stored tag counts, the temporal graph, the candidate decay and every threshold are unchanged.

It preserves: the temporal decay constant 0.95; the death threshold 0.15; the stable threshold 0.30; the candidate decay factor 0.8; the admission count and every cap; the retention policy and which structures compete. It does not: change the decay constant, which Q046 already tested at 0.99 and which delayed death to cycle 228 rather than the horizon; change the stored tag_counts table; change the admission floor or the candidate set; add a budget, a reserved pool or a second mechanism; regenerate or resurrect a belief that formation no longer proposes.

## The seed-varying world

For each seed, the design's triangle list is shuffled by `random.Random(seed)`, passed through the frozen `lattice_stream`, and rotated by `seed % len(events)`. The triangle multiset and local triangle structure are fixed; the schedule is seed-determined. Both arms of a seed receive the same stream.

**Why this is the only change.** The first block seeded the service RNG, but the lattice stimulus was the same for every seed, so the seed never varied a world. This block makes the seed vary the schedule, which is the quantity the earlier protocol claimed was seed-determined.

## The block

| Stage | Design | Cycles | What it reads |
| --- | --- | --- | --- |
| witness | `L3_hub1_t3_mixed` | 40 | the whole per-cycle theory trace, plus the NO_DREAMS and NO_QUESTIONS negative controls |
| preflight | `L1_hub1_t3_disjoint` | 3000 | the first cycle with zero theories after a positive one; the treatment runs the full horizon |

| Field | Value |
| --- | --- |
| world seeds | 20611101, 20611102, 20611103, 20611104, 20611105, 20611106 |
| bootstrap seed | 20611107 |
| cells | 24 (2 stages x 2 arms x 6 seeds = 24 cells) |
| early window | 5-36 |
| k | 5 |
| pairing | both arms of a seed run on the same seed-determined shuffled and rotated world and stimulus; only the service class differs |

**Gate G8 is pre-committed.** the preflight treatment must produce at least two distinct trajectory signatures across the six seeds; if all six are identical, the block is VOID because the seed axis did not vary the measured trajectory

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
| G1_baseline_death | the control must record a first zero after a positive cycle at or before cycle 60 on every seed; if the control survives, there is no death to repair and the block is void |
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

a pass on W1, P1 and C1 is necessary but not sufficient. Adoption requires a recorded owner decision, a fresh engine pin if the repair is promoted into the engine, and a campaign run under the gate D2 already requires. Nothing in this block changes the engine by itself.

**Withdrawal.** A W1 failure withdraws the repair from consideration: a persistence gain bought by breaking the witness is not a repair. A P1 failure records NO REPAIR and this form is not retried; a C1 failure records the trade and the repair is not adopted. Withdrawal is not deletion: the block stays in the record, and a different mechanism needs its own preregistration.

**Stop condition.** one mechanism, one protocol, one confirmatory block of 24 cells. The record may be fixed if it is found wrong; it may not grow into a second mechanism, a second endpoint or an additional block without a new preregistration.

## What this does not claim

This is a seed-axis confirmation of one mechanism on two designs. A pass does not adopt the repair, and a failure does not show that every persistence intervention fails. The original D3-PERSISTENCE-1 result remains the single-trajectory record; it is not re-scored here.
