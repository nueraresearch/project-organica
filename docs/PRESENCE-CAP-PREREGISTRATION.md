# Presence to assertion: the cap-only experiment (PRESENCE-CAP-1)

Generated from `docs/presence_cap_prereg.json` by `python -m benchmarks.presence_cap_experiment --render-prereg`. Do not edit by hand.

**Status: FROZEN, RUN. Authorised 2026-11-10 and run.** The verdict is `CAP LIMITING`; the artifact is `docs/presence_cap_run.json` and the result page is `docs/PRESENCE-CAP-RESULT.md`.

Question 2 of the conversion program (`docs/PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md`), frozen on its own. This is the Q2 half of the draft program, frozen on its own so the cap question can be answered without waiting for Q1 or Q3. It uses Q2's quantities (`S_ever`, `A_W`), its four levels, its K1-K6 gates and its four readings without renaming them. It adds one thing Q2 did not have: a magnitude bar and an admission ceiling derived from committed artifacts, because a direction on six seeds is not a decision-grade bar. It runs ahead of Q1 and Q3 deliberately and states the consequences: it may not claim construct separation, it does not use either block's cells, and if Q1 or Q3 later changes a definition this block is not re-scored.

## The question

With the world, presence and every non-cap parameter held fixed, does raising only the Layer-1 prediction cap add world edges to the final asserted structure?

## The hypothesis, stated before any cell

The 40-slot window truncates a ranked candidate list that holds roughly 225-238 candidates per cycle, so most world edges never receive a slot; if admission is what limits assertion, raising the cap should add asserted world edges, and if it is not, coverage should stay flat.

**Prediction.** If the budget is limiting, asserted world edges rise from the cap-40 arm to the cap-112 arm on at least five of six seeds, in the same direction across levels, by a mean of at least the declared bar.

**Falsifier.** Coverage stays flat at cap 112 and at the uncapped ceiling while admitted coverage rises: the budget reaches more edges and assertion does not follow, which closes the budget route.

**Alternative.** The admitted-but-unasserted edges are already the majority of the loss, so a budget increase may simply admit more edges of the kind that do not consolidate; that outcome is reported as a below-bar or flat result, not as a mechanism claim.

## The engine is frozen; the treatment is one constant

| Field | Value |
| --- | --- |
| Engine | 0.14.0 |
| Engine edit | **none** |
| Engine pin | `docs/engine_pin.json` |
| Treatment | `benchmarks.presence_cap_experiment.CapOnlySleepService` |
| Base class | `organica.sleep.SleepService` |
| Overrides | `__init__` |
| Constants changed | `MAX_PREDICTIONS` |

`benchmarks.acquisition_harness._CapOverrideSleepService` overrides `_build_predictions` and rebuilds the candidate list with a different evidence dict and a different sort key. It is a capacity diagnostic, not a one-variable treatment, so it cannot answer this question. The treatment here overrides no pipeline method at all: it sets the instance constant in `__init__` and returns the engine's own list unchanged.

`S_cycle` is read from the `SleepReport` the engine's public `run_sleep_cycle()` already returns, so no observer sits inside the engine: engine version, engine sha256 and the effective cap, so a mixed-build or mixed-cap row is caught rather than averaged.

## What the prior blocks already establish, and what they leave open

| Block | Artifact | Reading | Why it does not answer this question |
| --- | --- | --- | --- |
| same-build presence/assertion audit | `docs/presence_assertion_audit_0.14.0.json` | 112 of 112 world edges present, 34-47 asserted, at the shipped cap of 40 on six seeds | it measures one cap level only, so it cannot separate a capacity limit from a conversion limit |
| presence-to-assertion ladder trace (exploratory) | `docs/presence_assertion_ladder_0.14.0.json` | every world edge is offered by the ranking; 171 of 423 misses are never admitted and 252 are admitted and not asserted; the verdict is MIXED | it traces one cap level and its offered arm changes the cap in a recording subclass, so it quantifies the split but cannot show what a different budget would do |
| Gate 13 paired capacity diagnostic | `docs/gate13_paired_capacity_test.json` | the cap is manipulable in-process and a raised cap changes acquisition coverage | its treatment replaces candidate construction as well as the cap, so its gain cannot be attributed to the budget alone; this block does not re-score it |

## The ceiling the ladder already implies

**28.5 world edges per seed per seed** (docs/presence_assertion_ladder_0.14.0.json): mean of `buckets.offered_not_admitted` over the six ladder seeds (25, 33, 23, 26, 36, 28).

This is the reach-limited part of the loss: edges no 40-row window ever admitted. It is a bound on what a larger budget can buy by reach alone, not a hard bound on the gain, because a larger budget can also admit an already-admitted edge more often, and repetition may feed consolidation. A gain above this number is possible and is reported as repeat-driven rather than smoothed into the estimate.

## The bar, and why it is not computed on this block

A mean paired gain of **10 asserted world edges**, derived as round(2 * stdev(asserted_world_edges over the six audit seeds)) = round(2 * 5.0498) = 10: twice the seed-to-seed spread already measured at cap 40. Provenance: `docs/presence_assertion_audit_0.14.0.json`.

**Fragility.** One block, one world family, six seeds. The bar is not calibrated on the seeds this block runs, but it is not independent of the engine or the world family either, so it is a starting bar rather than a constant.

## Freeze notes: corrections made before any cell

- K4's third clause first required the higher caps to change `S_ever` on at least five of six seeds. That made `CAP NOT LIMITING` unreachable: flat assertion with a changed `S_ever` on five seeds is already `ADMISSION SCALES, ASSERTION FLAT`, and the remaining flat case would have failed K4 and returned `CAP NOT BINDING`. The gate now requires the cap to change `S_ever` on at least one seed, and the number of seeds that change reach is the reading that separates the two verdicts.
- The correction was made at freeze time, before any cell, and is recorded here rather than folded in silently. No level, seed, cycle count, bar or ceiling moved.

## The design

| Field | Value |
| --- | --- |
| Variable | `layer1_prediction_cap` |
| Levels | `40`, `80`, `112`, `1000000000` (diagnostic ceiling) |
| Seeds | 20611401, 20611402, 20611403, 20611404, 20611405, 20611406 |
| Bootstrap | 20611407 |
| Cycles | 120 |
| Cells | 24 (4 levels x 6 seeds) |
| Witness cell | seed 20261100 at cap 40 |
| Pairing | same seed and world across all four caps; only the cap differs, so each seed contributes its own paired difference |
| World | the Gate-13 compositional world (generate_compositional_world, 16 tags, 112 derivable edges), 120 cycles covering warmup and acquisition |

**Freshness.** The six seeds and the bootstrap are fresh: they appear in no other docs artifact except this record and the registry echo that records every artifact's seeds. The audit seeds are not reused, so the bar is not computed from the seeds it judges.

**Witness.** the audit's first seed, run through this block's treatment at the shipped cap; it must reproduce the published audit row exactly, which is what proves the treatment at 40 IS the shipped engine.

## Endpoints, named once

| Reading | Definition |
| --- | --- |
| `W` | the world's derivable edges from the training stream |
| `P` | world edges present in raw temporal memory at the end of the run (`temporal_edges(min_count=1)`), before any cap |
| `S_cycle` | the prediction edges the engine returned from one sleep cycle, read from the `SleepReport` the public API already returns |
| `S_ever` | the union of `S_cycle` over the run; this can exceed the cap |
| `S_final` | the admitted prediction edges still present in the surviving candidate snapshots |
| `A` | the final asserted structure over all six structure types (`structure_edges`) |
| `A_W` | `A` intersected with `W`, the assertion endpoint |
| `A_pred` | `A_W` intersected with `S_ever`: world edges asserted and ever admitted |
| `A_other` | `A_W` minus `S_ever`: world edges asserted without ever being admitted, the non-prediction assertion route |

## Gates, which decide admissibility before any reading

| Gate | Requirement |
| --- | --- |
| `K1_build` | all cells and the witness name one engine version, one sha256 and the effective cap; no mixed-build row is averaged |
| `K2_same_world` | `W` is identical across the four caps of every seed (same world digest) |
| `K3_presence_invariant` | `P` is identical across the four caps of every seed (same presence fingerprint) |
| `K4_cap_live` | each cell records its cap; the 40 arm never returns more than 40 rows; at least five of six seeds produce a full 40-row cycle; the higher caps produce a different `S_ever` on at least one seed, so the cap is live somewhere. How many seeds change reach is a reading, not a gate. Failure is `CAP NOT BINDING`, not a void |
| `K5_cap_only` | the treatment overrides no pipeline method (only `__init__`, which sets the constant), and the witness cell at cap 40 reproduces the published audit row: presence, asserted count and asserted fingerprint. A failure is `VOID` |
| `K6_denominator` | `W`, `P` and `S_ever` are non-empty in every cell; a zero denominator is not measurable |

## Readings, in the order they are read

| Reading | Rule |
| --- | --- |
| `SCALES` | moving from 40 to 112 or uncapped adds world edges to `A_W` on at least five of six seeds, with the three level steps (40->80, 80->112, 112->uncapped) non-decreasing within each counted seed |
| `FLAT` | at least five of six seeds gain no `A_W` edge at 112 or uncapped relative to 40, while `S_ever` changes on fewer than five seeds; when `S_ever` does change on at least five the reading is `ADMISSION SCALES, ASSERTION FLAT` |
| `ADMISSION SCALES, ASSERTION FLAT` | `S_ever` changes at 112 or uncapped while `A_W` does not, on at least five of six seeds |
| `MIXED` | none of the above; report the per-seed membership changes and force no label |
| **Threshold** | A `SCALES` reading is split by magnitude: `CAP LIMITING` requires the mean paired gain at 112 to be at least the bar, the 95% paired t lower bound above zero, and a positive gain on at least five of six seeds; otherwise the reading is `CAP LIMITING BELOW BAR`. The threshold is read after the membership reading, never instead of it |

The readings are membership readings, not aggregate counts: adding a world edge to `A_W` means the organism asserts that edge, not that a count moved.

## The retention profile, declared before any cell

Before any mechanism is proposed, every cell records its stage counts, the retention ratios P/W, S_ever/P and A_W/S_ever (with the admitted-only variant A_W|admitted/S_ever beside the last), and the absolute loss at each observed step: W to P, P to S_ever and S_ever to A_pred. The retained chain ends at A_pred, not at A_W: an edge asserted without ever being admitted is a bypass, reported separately and counted neither as retention nor as loss. The P to S_ever loss excludes the bypass, because those edges leave the admitted chain but survive into assertion; the bypass is removed from that drop rather than added to it. The primary suspect stage is the earliest step with the largest absolute loss, ties going to the earlier step, which is the conversion draft's own loss rule; the relative shares are reported beside it and never name a suspect on their own, because a large relative loss on a small denominator is not the same finding as a large absolute one. A stage whose denominator is zero is not measured and is excluded from the comparison; it is never reported as 0.0. The rule names the stage to inspect next and licenses no mechanism, no engine change and no verdict.

| Stage | Prior retained | Prior drop |
| --- | --- | --- |
| W | 672 | - |
| P | 672 | 171 |
| S_ever | 460 | 252 |
| A_pred | 208 | - |

| Step | Prior ratio | Prior relative loss |
| --- | --- | --- |
| P/W | 1.0 | - |
| S_ever/P | 0.684524 | - |
| A_W/S_ever | 0.541304 | - |
| A_W|admitted/S_ever | 0.452174 | - |
| P->S_ever | - | 0.254464 |
| S_ever->A_W | - | 0.547826 |

The prior columns are recomputed from the **exploratory** `presence_assertion_ladder_0.14.0.json` on every render, pooled over its six rows. The primary suspect stage is **S_ever->A_W**, and the ladder's own bucket shares over its 423 misses are 0.404255 at admission, 0.0 before it and 0.595745 after it. The P->S_ever loss is the **171** offered-not-admitted edges, not the raw stage difference of **212**: the **41** asserted edges that never passed admission are a bypass, excluded from the retained chain and removed from the P->S_ever drop rather than added to it. The two drops sum to **171 + 252 = 423**, the full miss count, so the bypass is counted once and no edge is counted twice.

**The steps the engine makes identities.** `S_cycle` to `S_ever` is a union, not a retention step: `S_ever` is the union of the per-cycle predictions and can exceed the cap, so it is recorded as window sizes rather than as a ratio.

**Why the last step is not `A/S_final`.** The surviving candidate snapshot is the asserted structure, so `A = S_final` and `A/S_final` is 1 by definition in this engine; `A_W` is that structure intersected with the world, which is why the last measured step is `A_W/S_ever`.

**Why `A_W/S_ever` is not pure retention.** `A_W/S_ever` is not a pure retention ratio, because `structure_edges` aggregates six structure types and some asserted edges were never admitted. The ladder separates them as `asserted_without_admission`; the profile prints the admitted-only ratio beside the raw one and never treats the bypass as a loss or as retention.

## The decision table

| Condition | Verdict | Decision | What it licenses |
| --- | --- | --- | --- |
| a K gate other than K4 fails | **VOID** | none; fix the harness and register a new block, never this one re-read | the block is inadmissible; no reading is made and nothing is recorded as a cap result |
| K4 fails: the window never fills or the higher caps do not change admission | **CAP NOT BINDING** | do not run a larger-cap block at these levels; report the window and move the question to another constraint | the budget is not the constraint at these levels and no scaling reading is made |
| `S_ever` changes and `A_W` does not on at least five of six seeds | **ADMISSION-ONLY BOTTLENECK** | close the budget route and move the line to the assertion step; no cap change | the budget reaches more world edges and assertion does not follow; the budget route is closed and the next question is conversion, not capacity |
| `SCALES` and the magnitude conditions hold | **CAP LIMITING** | take the budget to the owner as a limiting factor and license a cap-change decision with its own date and rationale | the admission budget limits assertion at the declared bar; this licenses an owner decision on the cap, not an adoption and not a capability claim |
| `SCALES` but the magnitude conditions fail | **CAP LIMITING BELOW BAR** | do not spend an owner decision on the cap; the gain sits inside the seed spread, so record it and diagnose why admission converts at a low rate | the budget moves assertion in the predicted direction but by less than twice the seed spread; the cap is a weak lever and the next question is why admission converts at a low rate |
| `FLAT` on at least five of six seeds while `S_ever` changes on fewer than five | **CAP NOT LIMITING** | close the budget route; the constraint is ranking or consolidation, not capacity | more slots do not buy more assertion; the ranking or the consolidation path is the constraint, and the budget route is closed |
| none of the above | **MIXED** | neither pole; re-register on a fresh seed block rather than re-reading this one | the per-seed changes are reported and no label is forced; a mixed result does not license a cap change |

## Adoption, withdrawal and stop

Only `CAP LIMITING` licenses anything, and what it licenses is an owner decision to change `MAX_PREDICTIONS`, recorded with its own date and rationale, because the cap governs which structures the Layer-1 layer selects and is therefore a cognition constant rather than a measurement detail. No arm of this block edits `organica/`.

**Withdrawal.** The reading is withdrawn if the cap-40 witness stops reproducing the audit row, if the treatment class gains a second override, if the engine pin moves without a version bump, or if a later block finds the cap-40 control was not the shipped build. A withdrawn reading is recorded, not deleted.

**Not authorised by this record.** raising the cap in the engine; adding a level, a seed or a criterion after the first cell; a capability, transfer or generalization claim; re-scoring the audit, the ladder or the Gate 13 capacity diagnostic

**Stop condition.** One block, four levels, six seeds, one endpoint. When it is analysed the cap question is closed in one of the six verdicts above. A follow-up may read these cells at a different resolution; it may not add a cap level, swap an arm or re-run a failing seed. Any intervention on admission or allocation needs its own preregistration.

## Cost and authorisation

24 cells (1 witness) x 3000 cycles. about four minutes sequentially on this machine at roughly eight seconds per cell

**Authorisation.** The draft program's freeze checklist requires the owner's authorisation before a run, and the owner gave it on 2026-11-10: `Authorize all runs`, covering all three frozen conversion blocks. This record had no request document before the grant, so `docs/AUTHORISATION-PRESENCE-CAP-1.md` records the request scope and the decision together. The record stays FROZEN, NOT RUN and no cell has run; `--measure` refuses unless `authorisation.granted` is true and the document check passes. A grant is not a run: executing the first cell is a separate, dated act.

## What this does not claim

This record measures admitted and asserted world-edge membership on one world family, one engine build and 120 cycles. It does not show that the cap causes the presence/assertion gap, that the gap is a defect, that any structure type is responsible, or that raising the cap would improve capability. `U`, the readout/use stage, is not measured. The uncapped level is a diagnostic ceiling, not a proposal, and a gain above the reach-limited ceiling is attributable to repetition rather than to reach and is reported as such.
