# Gate 13 — control-side temporal redundancy pre-registration (block 4)

**Status: RUN (2026-11-06). Verdict: VOID / NOT COMPARABLE.** All 200 cells have since been executed and scored exactly once; §12 records the readings and §11 remains the freeze text. The criteria below were fixed before the first cell,
from an artifact the block does not contain (§4). Amendments, if any, are appended with a date; this text is not edited to
match a result.

## 1. Question

Block 3 closed the loop-coverage proxy: pre-run loop redundancy does **not** predict where the ratio arm pays
(`MODERATOR NOT SUPPORTED`; Spearman -0.02, high-redundancy half gaining more, not less). §8.13's store-time
attribution points somewhere else: the arm's effect is carried entirely by temporal (`prediction_candidate`) edges, and the
seeds that improved were the ones where the **control's** temporal edges were already **largely implied by its loops** —
median overlap 5.2 in improving seeds against 1.4 in failing ones, with the two arms moving in opposite directions
(5.2→3.6 improving, 1.4→8.8 failing).

That is a different covariate from block 3's: not how much of the *world* the loops cover, but how much of the control's
*own temporal structure* the loops already duplicate. Block 4 tests whether that predicts the gain on a fresh allocation.

## 2. What is registered, and what is not

Registered: the covariate, its threshold, three gates, three criteria, the decision table, and the power of every bar under
three effect sizes. Not registered and not changed: the arms (count control C, ratio arm R as defined in
`benchmarks/run_ratio_admission_arm.py`), cap 20, the world generator, the readout, and the frozen engine.

## 3. Allocation and cells

- Seeds **20271202-20271301**, **100 seeds**. Freshness scan: **524 files** (`.py`, `.md`, `.json`),
  **0 occurrences** in the allocated range.
- **20271201 is excluded**: it occurs in the tree only as this harness's own scan-start constant, and an
  allocation may not contain a seed already written into the tree — the rule is applied to the letter, not to intent.
- Cells: **C and R at cap 20, 200 cells**. No other cap and no E arm — no criterion here reads them.
- Runner: `benchmarks/run_temporal_redundancy_block.py`. Command:
  `PYTHONPATH="$PWD" PYTHONHASHSEED=0 .venv/bin/python benchmarks/run_temporal_redundancy_block.py --block 20271202:20271301 --budget 200 --jsonl .scratch/temporal_redundancy_block.jsonl`
- The runner was self-tested **before** this freeze on the excluded seed 20270901: both arms reproduce block 2's `asserted`,
  `covered` and digest (C 90/34/`1a51184e43b546a7`, R 87/34/`129da0ffd2052b85`), and it records the covariate on both arms
  (C `o` = 0.0, R `o` = 0.4615 on that seed).

## 4. Covariate (read from the control cell, before the ratio cell is scored)

`o_s = |L_s ∩ P_s ∩ W| / |P_s ∩ W|`, where `P_s` is the set of world edges the control cell's
`prediction_candidate` structures assert, `L_s` its `loop_candidate` edges, and `W` the world's edges. Both sets come from
the same store-time observer §8.13 validated (all 20 cells passed replay-digest, edge-set and per-edge-weight checks).

- Threshold `o*` = **0.3095**, the median of the 10 calibration seeds (block 2), which this block does not contain.
  `o_s >= o*` is the *high-overlap* half.
- **Measurability rule.** `o_s` is a share, so it is defined only when `|P_s ∩ W| >= 3`. A seed whose control cell
  asserts fewer temporal world edges than that is **not measurable and is excluded** — never recorded as `o_s = 0.0`. If
  fewer than 96 seeds are measurable the block is void (gate G2).
- The covariate uses the control cell. The outcome is the paired difference R − C, so the control appears on both sides;
  that is inherent to this design and is why the covariate is defined on structures the control produces, not on the ratio
  arm's output.

**Selection disclosure, stated before the run.** This covariate was chosen *after* reading §8.13's ten-seed table, and on
those same ten seeds it associates with the gain at Pearson 0.642, Spearman 0.659 (slope
0.0795, residual sd 0.0422). That association is **in-sample and selection-contaminated**: it is not
independent evidence for anything, it is the reason the block exists. The block's 100 fresh seeds are the first
out-of-sample test of it. It also differs from block 3 in one way that matters for how a pass should be read: block 3's
calibration pointed the wrong way and still failed; this one points the predicted way, so a pass here would be consistent
with the hypothesis and a fail would contradict it sharply.

## 5. Gates (a failed gate voids the block; it is not a negative result)

- **G0 liveness**: the C and R asserted sets differ on at least 96 of 100 seeds. If they do not, the arm is not what
  is being compared.
- **G1 comparability (C1′)**: the block-mean cap-20 control precision lies in [0.4347, 0.4987] (δ = 0.032 from
  `docs/gate13_control_precision_sweep.json`, as in blocks 2 and 3). Otherwise the block is `NOT COMPARABLE`.
- **G2 measurability**: `o_s` is defined on at least 96 of 100 seeds (i.e. `|P_s ∩ W| >= 3` on the control
  cell). Unmeasurable seeds are excluded from every criterion and counted, not imputed.

## 6. Criteria (evaluated once, in this order, by committed code)

- **M1 — half-split contrast.** `gain_s = coverage_R - coverage_C`. Split at `o*`. Pass iff both halves have at least 40
  seeds and `median(gain, high) - median(gain, low) >= 0.03`.
- **M2 — directional association.** Pass iff `Spearman(o_s, gain_s) >= 0.25` across the measurable seeds
  (one-sided; the hypothesis is that more control-side duplication means more room to trade, so higher overlap, larger gain).
- **M3 — replication (secondary, never confirmatory).** Pass iff at least 66 of 100 seeds have
  `gain_s > 0`. Blocks 2 and 3 gave 20/25 and 88/100.

## 7. Decision table (fixed)

| M1 | M2 | G0-G2 | verdict |
|---|---|---|---|
| pass | pass | pass | **MODERATOR SUPPORTED** — control-side temporal redundancy predicts where the ratio arm helps |
| fail | pass | pass | **DIRECTIONAL ONLY** — the association is there, the half-split contrast is not |
| pass | fail | pass | **HALF-SPLIT ONLY** — a threshold contrast without a monotone association; read as fragile |
| fail | fail | pass | **MODERATOR NOT SUPPORTED** — the proxy is not a predictor at this n |
| — | — | fail | **VOID / NOT COMPARABLE** — report the gate, not a verdict |

M3 is reported beside the verdict and never substitutes for M1 or M2.

## 8. Power, computed in advance

Simulated by resampling the 10 calibration pairs with the mean preserved
(`gain = mean(gain) + slope·(o − mean(o)) + N(0, 0.0422)`), 4,000 replicates per row. "Mechanism-sized" is a
slope of 0.10 across the observed `o` range, about 0.08 of coverage.

| scenario | slope | M1 | M2 | M1 and M2 | M3 |
|---|---|---|---|---|---|
| mechanism-sized | 0.1 | 1.0 | 1.0 | 1.0 | 0.389 |
| calibration-implied | 0.0795 | 0.988 | 1.0 | 0.988 | 0.596 |
| null (no association) | 0.0 | 0.003 | 0.006 | 0.001 | 0.91 |

**What this means, before the data arrive.** The joint bar has **1.0** power against a mechanism-sized
effect and **0.001** at no association, so the test is asymmetric: a pass is strong evidence, a miss is evidence
against the hypothesis — stronger evidence than block 3's miss, because here the calibration association is in the tested
direction and the design is not fighting its own prior.

## 9. Pre-registered predictions

- **P1** G0 and G1 pass, as they did in blocks 2 and 3.
- **P2** G2 passes: the control asserts at least 3 temporal world edges on nearly every seed (the calibration
  range was 3–12).
- **P3** M3 passes: the gain replicates (~88/100 in block 3), since nothing about the arm changed.
- **P4** M2 passes at +0.25: the calibration association was +0.659, and even heavily shrunk toward zero an
  out-of-sample rank correlation of this size clears the bar.
- **P5** The `o_s` distribution is more concentrated at the extremes than the calibration's (three calibration seeds sat at
  1.0), which would leave M1's halves uneven; if a half falls below 40 seeds, M1 is recorded as not satisfied and the
  reason is stated rather than smoothed.

## 10. What each outcome would and would not license

- `MODERATOR SUPPORTED`: control-side temporal redundancy is a usable pre-run covariate for this arm on this world family,
  and the §8.13 mechanism gains out-of-sample support. It does **not** establish causality — the covariate is measured on the
  control cell, not manipulated.
- `MODERATOR NOT SUPPORTED`: the §8.13 pattern does not generalize across seeds at n=100. It does **not** retract §8.13's
  composition finding (which is about *where* the effect lives, not *which seeds*), and it does not license any claim about
  an intervention.
- The decisive test remains an intervention, not a moderator: an arm identical to R that prefers temporal candidates whose
  edge no loop asserts at admission time. Not registered here.

## 11. Freeze

Criteria, gates, threshold, bars, allocation and decision table are frozen as written. No cell of 20271202-20271301 has been run.
Scoring code must read the threshold and bars from `docs/gate13_temporal_redundancy_calibration.json`. Artifacts:
`docs/gate13_temporal_redundancy_calibration.json`, `docs/gate13_structure_provenance.json`,
`docs/gate13_redundancy_block3.json`, `docs/gate13_ratio_block2.json`.

## 12. Readings (2026-11-06, one scoring pass)

200 cells, seeds 20271202-20271301, C and R at cap 20, no cell substituted and no cell failed. Threshold 0.3095
and bars were read from `docs/gate13_temporal_redundancy_calibration.json`, the C1′ band from
`docs/gate13_c1_respecification.json`; nothing was adjusted after the run. Scored once by
`benchmarks/score_temporal_redundancy_block.py` into `docs/gate13_temporal_redundancy_block4.json`.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness | 100/100 seeds with arm-dependent asserted sets | yes |
| G1 C1′ | mean control precision 0.4465 in [0.4347, 0.4987] | yes |
| G2 measurability | 87/100 seeds with `o_s` defined (required 96) | NO |

**Verdict: VOID / NOT COMPARABLE.** G0 and G1 pass, so the arms and the control behave as in blocks 2 and 3. G2 fails: the covariate's denominator, |P_s ∩ W|, fell below 3 on 13 control cells, so `o_s` was not measurable there; those seeds are excluded and counted, never imputed. Per §7 the
gate is reported and no criterion is read.

**Why the gate failed, in its own terms.** This is a defect of the covariate as specified, not a property of the treatment.
`o_s` is a share of the control's temporal world edges, and on this allocation that denominator is small and often empty —
the block-2 calibration ranged 3-12, the fresh allocation 0-11. The distribution is also saturated rather than centred: the
mean `o_s` is 0.7191 against 0.468 in calibration, and 78 of the 87 measurable seeds sit at or
above the threshold 0.3095, leaving 9 below it. Even had every seed been measurable, M1's 40-seed
per-half requirement could not have been met, which §9's P5 anticipated and this reading confirms. Pre-registered
prediction **P2 is falsified**: the calibration range did not transfer.

**Recorded but not scored.** The code computes M1, M2 and M3 on the measurable seeds and they are in the artifact —
M1 difference 0.0358 (9 low / 78 high),
M2 Spearman 0.389 (95% CI [0.192, 0.551]), M3 81/87. They are **descriptive only**: the gate voided the
block, so reading them as a verdict would be exactly the post-hoc re-scoring §7 forbids. Recorded for a future
pre-registration, not as a result.

**What this does and does not settle.** Nothing about whether control-side temporal redundancy moderates the ratio arm —
the test was not admissible. It does establish something about the covariate: as specified, `o_s` is not usable at n=100 on
this world family, because the quantity whose share it measures is frequently absent. A further block would need a coarser
covariate — the count of the control's temporal world edges, or the overlap taken over asserted edges rather than world
edges — with the denominator problem solved *before* the freeze rather than excluded afterwards.
