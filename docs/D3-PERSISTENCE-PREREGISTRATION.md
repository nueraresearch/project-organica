# D3 persistence preregistration: matched source-frequency decay

Generated from `docs/d3_persistence_prereg.json` by `python -m benchmarks.d3_persistence_prereg --render`. Do not edit by hand.

**Status: FROZEN, NOT RUN.** No cell has run. The repair is available only as the in-process `MatchedFrequencySleepService`; it is **not promoted into the engine**, and promotion is an owner decision.

**Post-freeze result.** The status and text above are the frozen pre-run record. The block has since run; its result is `docs/D3-PERSISTENCE-RESULT.md`, and the seed-varying confirmation is `docs/D3-PERSISTENCE-SEED-VARYING-RESULT.md`. The repair was promoted into the engine at 0.14.0 by the dated owner decision. This pointer is outside the frozen protocol and changes no criterion, bar, seed, arm or gate.

D3 in `docs/DECISION-G1-WITNESS.md` is **PENDING** and requires its own preregistration. This is that record. It does not change an engine file and does not authorise a run.

## The question

Does matching the source-frequency denominator's decay horizon to the temporal numerator's keep the reference arm alive to the campaign horizon on L1 without breaking the L3 witness or costing early next-cycle recall?

Scope: **lattice_L1**. Witness `L3_hub1_t3_mixed`; campaign stimulus `L1_hub1_t3_disjoint`. burst_L1 is excluded. Q052 amendment A2 classified its late collapse DIFFERENT_SUPPORT_COLLAPSE, so it is not a second instance of this mechanism and may not be pooled.

Pre-flight hook: `benchmarks.tier1_preflight.build(reference_class=benchmarks.d3_persistence_arm.MatchedFrequencySleepService)`.

## Why this repair, and not a slower decay

Q046 already moved the temporal decay factor from 0.95 to 0.99 and delayed the death from cycle 39 to cycle 228 on all six arms. It did not reach the campaign horizon. The measured cause is not only the numerator: the source frequency that divides it grows without decay, so an edge renewed every cycle is still diluted by its own history. This record changes the denominator's horizon, not the decay constant.

## The mechanism

**matched source-frequency decay** (`MatchedFrequencySleepService`).

Each cycle, before Layer 1 predictions are built, maintain a per-tag decayed frequency D(tag) = 0.95 * D_previous(tag) + delta(tag), where delta is the increase in memory.tag_frequencies() since the previous cycle and the first cycle starts from the raw counter. Prediction strength uses temporal_count / max(D(source), 1) instead of temporal_count / raw_tag_count. The stored tag counts, the temporal graph, the candidate decay and every threshold are unchanged.

| Field | Value |
| --- | --- |
| frequency decay | 0.95 |
| order | the decayed counter is updated once per cycle, before _build_predictions, keyed on the monotonic sleep-cycle number so a second call in the same cycle cannot apply the delta twice |
| scope | the Layer 1 prediction denominator only; no other layer reads the decayed counter |

**Why it should work.** On a repeated stimulus the raw source frequency grows without bound while the temporal count decays, so the shipped ratio falls even though the edge is renewed every cycle. Matching the denominator's horizon to the numerator's keeps the ratio near its per-cycle renewal rate, so a re-presented edge reaches the strength rule instead of being diluted by its own history.

**Risk, stated before the run.** A stale edge whose temporal count decays no faster than its source frequency can keep a ratio near the renewal rate and remain asserted. The witness and early-recall criteria are the guards, and precision is reported beside the verdict rather than treated as a pass.

**What success would look like.** The decayed denominator keeps the ratio near its renewal rate: L1 stays above zero through cycle 3000 on at least 5 of 6 seeds, the L3 witness holds 39 of 40 theory cycles and peak 6, and early recall stays within 0.01 of control.

**What failure would look like.** The ratio still falls because the temporal count decays faster than the matched denominator, or the denominator's early value keeps stale edges asserted and early recall falls. Either shows the ratio was not the binding constraint.

**Edge case.** On the first cycle D equals the raw counter. A tag absent for a cycle decays by 0.95 with no increment. The denominator is floored at 1, exactly as the shipped ratio is.

It preserves: the temporal decay constant 0.95; the death threshold 0.15; the stable threshold 0.30; the candidate decay factor 0.8; the admission count and every cap; the retention policy and which structures compete. It does not: change the decay constant, which Q046 already tested at 0.99 and which delayed death to cycle 228 rather than the horizon; change the stored tag_counts table; change the admission floor or the candidate set; add a budget, a reserved pool or a second mechanism; regenerate or resurrect a belief that formation no longer proposes.

## The two arms

| Arm | Service | Decay | Death threshold | Frequency decay | Rule |
| --- | --- | --- | --- | --- | --- |
| control | `organica.sleep.SleepService` | 0.95 | 0.15 | none | the shipped engine, no subclass, no-op |
| treatment | `the in-process MatchedFrequencySleepService` | 0.95 | 0.15 | 0.95 | the shipped engine plus the matched source-frequency denominator; no other change |

The temporal decay factor is held at 0.95 in **both** arms. The treatment may not buy its effect by slowing the graph's decay: the run artifact is refused if either arm records a different value, or if the treatment records a denominator decay other than 0.95.

## The block

| Stage | Design | Cycles | What it reads |
| --- | --- | --- | --- |
| witness | `L3_hub1_t3_mixed` | 40 | the whole per-cycle theory trace, plus the NO_DREAMS and NO_QUESTIONS negative controls |
| preflight | `L1_hub1_t3_disjoint` | 3000 | the first cycle with zero theories after a positive one; the treatment runs the full horizon |

| Field | Value |
| --- | --- |
| world seeds | 20410301, 20410302, 20410303, 20410304, 20410305, 20410306 |
| bootstrap seed | 20410307 |
| cells | 24 (2 stages x 2 arms x 6 seeds = 24 cells) |
| early window | 5-36 |
| k | 5 |
| pairing | both arms of a seed run on the same seed-determined world and stimulus; only the service class differs |

Freshness: the first contiguous window of seven integers at or above 20410301 that appears in no artifact, harness, test, document or journal in the repository; the seventh is the bootstrap seed and is not a world seed.

## Criteria, in the order they are read

| Criterion | Quantity | Rule | Bar | Provenance |
| --- | --- | --- | --- | --- |
| W1_witness | the treatment's theory cycles and peak on the L3 witness over 40 cycles | at least 39 of 40 theory cycles and a peak of at least 6, on at least 5 of 6 seeds, with both negative controls at zero across the trace | 39/40 cycles and peak 6 on 5/6 seeds | the adopted witness's measured baseline in docs/tier1_preflight.json, not calibrated on the treatment |
| P1_persistence | the treatment's theory count in the last 100 cycles of the L1 horizon | no first zero through cycle 3000 and a theory count above zero in every one of the last 100 cycles, on at least 5 of 6 seeds | 5 of 6 seeds alive at the horizon | 3000 is the campaign's own horizon from D2. The 5/6 bar is declared, not calibrated: the campaign requires one live colony, and a majority guards against a single-seed fluke without demanding every seed. |
| C1_early_cost | next-cycle recall@5 over cycles 5-36, median per-seed gap (treatment minus control) | median gap at or above the early-cost bound | -0.01 | Q051's early equivalence margin, carried unchanged; a larger early loss prices the trade and blocks adoption |

The criteria are judged whole. A failed W1 leaves P1 and C1 unread: a repair that breaks the witness cannot be adopted for the campaign even if it keeps L1 alive.

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

Void rule: a failed gate voids the block and no criterion is read.

## The decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
| any gate fails | VOID | the block is unrun; the failed gate names what did not happen, and no criterion is read |
| gates pass; W1 fails | WITNESS BROKEN | the repair damages the L3 witness, so it cannot be adopted for the campaign even if L1 stays alive; the failure is a property of the repair, not of the witness |
| gates pass; W1 passes; P1 fails | NO REPAIR | the arm still dies before the campaign horizon; persistence is not restored, and the campaign remains not measurable as designed |
| gates pass; W1 passes; P1 passes; C1 fails | PERSISTENCE REPAIRED WITH EARLY COST | the arm survives to the horizon but loses early ranking beyond the equivalence margin; the trade is priced and nothing is adopted |
| gates pass; W1 passes; P1 passes; C1 passes | PERSISTENCE REPAIRED | the arm survives to the campaign horizon with the witness intact and no early cost beyond the margin; adoption is still an owner decision and is not implied by the label |

## Adoption

a pass on W1, P1 and C1 is necessary but not sufficient. Adoption requires a recorded owner decision, a fresh engine pin if the repair is promoted into the engine, and a campaign run under the gate D2 already requires. Nothing in this block changes the engine by itself.

**Withdrawal.** A W1 failure withdraws the repair from consideration: a persistence gain bought by breaking the witness is not a repair. A P1 failure records NO REPAIR and this form is not retried; a C1 failure records the trade and the repair is not adopted. Withdrawal is not deletion: the block stays in the record, and a different mechanism needs its own preregistration.

Not authorised by this block: implementing the repair before the block runs; a decay-factor sweep, including retrying 0.99; a second mechanism or a parameter sweep of this one; pooling burst_L1 cells into this block; re-scoring a criterion after the block runs; launching the Tier-1 campaign on the strength of this block alone.

## Stop condition

one mechanism, one protocol, one confirmatory block of 24 cells. The record may be fixed if it is found wrong; it may not grow into a second mechanism, a second endpoint or an additional block without a new preregistration.

Cost: 24 cells. 12 witness cells at 40 cycles (480), 6 control preflight cells stopped at death (at most 360), 6 treatment preflight cells at 3000 (18,000).

## What this does not claim

Nothing here shows that matched denominator decay restores persistence, that it can be implemented as described, or that a result would generalise beyond these two designs. The repair has not been built, no cell has run, and the engine is unchanged.
