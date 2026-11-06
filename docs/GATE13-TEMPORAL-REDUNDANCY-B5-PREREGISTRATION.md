# Gate 13 — control-side temporal redundancy, block 5 (repaired covariate)

**Status: RUN (2026-11-06). Verdict: DIRECTIONAL ONLY.** All 200 cells have since been executed and scored exactly once; §12 records the readings and §11 remains the freeze text. The criteria below were fixed before the first
cell, from artifacts the block does not contain (§4). Amendments, if any, are appended with a date; this text is not
edited to match a result.

## 1. Question, and what changed from block 4

Block 4 asked whether the gain from the ratio arm is larger on seeds whose **control** cell already has much of its
temporal structure implied by its loops, and was **voided by its own measurability gate**: G0 and G1 passed, G2 failed at
87/100 against a required 96. Block 5 asks the same question with the same covariate, repaired.

Two defects, both in the specification and both visible in block 4's readings:

- **The floor was 3.** `o_s` was declared measurable only when the control asserted at least 3 world-covered temporal
  edges. On this world family that is a property of the draw, not of the treatment: block 4's fresh cells produced
  0–11 such edges, and 13 of 100 fell below 3. A 96/100 measurability gate was therefore **unreachable by design**,
  which is a design error and not a result.
- **The cut came from 10 seeds.** 0.3095 was the median of the ten block-2 calibration seeds, while the covariate's mass
  sits near 1.0: 78 of block 4's 87 measurable seeds landed on the high side, so M1's 40-per-half rule could not have
  been met even with every seed measurable.

The repair is exactly these two things. A share with denominator 1 or 2 is **coarse, not undefined** — rule 13 forbids
recording a zero-denominator ratio as `0.0`, and says nothing against a ratio with a small but nonzero denominator, which
is why the floor becomes 1 and not 0. The cut is chosen by a stated balance rule over 110 cells rather than by a median
of ten. Nothing about the arms, the cap, the world, the readout or the engine changes; the criteria's numbers are
unchanged from blocks 2–4 so that blocks remain comparable.

**Why not the count.** The obvious denominator-free covariate — the raw overlap count `|L ∩ P ∩ W|` — was calibrated
first and rejected before freezing: it is defined everywhere and splits 52/58, but its rank association with the gain is
only 0.241 on the same 110 cells and its expected half-split gap is
0.015 against a 0.03 bar. A block frozen on it would be a null ritual. The count is recorded in the artifact and in §4
of the capacity record so the choice is auditable.

## 2. What is registered, and what is not

Registered: the covariate definition and its floor, its cut, three gates, three criteria, the decision table, and the
power of every bar under three effect sizes. Not registered and not changed: the arms (count control C, ratio arm R as
defined in `benchmarks/run_ratio_admission_arm.py`), cap 20, the world generator, the readout, and the frozen engine.

## 3. Allocation and cells

- Seeds **20271403-20271502**, **100 seeds**. Freshness scan: **532 files** (`.py`, `.md`, `.json`),
  **0 occurrences** in the allocated range.
- Excluded by the same rule as block 4, applied to the letter: **20271302, 20271303, 20271402**. 20271302 occurs in
  the tree only as this harness's own scan-start constant; 20271303, 20271402 occur only in the
  superseded block-5 calibration artifact, which was written and then replaced before any cell ran. An allocation may not
  contain a seed already written into the tree, however innocently, and the run starts at the first free 100-seed
  window.
- Cells: **C and R at cap 20, 200 cells**. No other cap and no E arm — no criterion here reads them.
- Runner: `benchmarks/run_temporal_redundancy_block.py`, unchanged from block 4 and already self-tested against block 2 on
  the excluded seed 20270901 (C 90/34/`1a51184e43b546a7`, R 87/34/`129da0ffd2052b85`). Command:
  `PYTHONPATH="$PWD" PYTHONHASHSEED=0 .venv/bin/python benchmarks/run_temporal_redundancy_block.py --block 20271403:20271502 --budget 200 --jsonl .scratch/temporal_redundancy_b5.jsonl`
- The runner writes its `o` field at the old floor of 3; the scorer **ignores** that field and recomputes `o_s` from the
  recorded `overlap` and `pred_world` counts. That is stated here so the mismatch is not mistaken for a defect later.

## 4. Covariate (read from the control cell, before the ratio cell is scored)

`o_s = |L_s ∩ P_s ∩ W| / |P_s ∩ W|`, where `P_s` is the set of world edges the control cell's `prediction_candidate`
structures assert, `L_s` its `loop_candidate` edges, and `W` the world's edges. Both sets come from the same store-time
observer §8.13 validated.

- **Measurability floor: `|P_s ∩ W| >= 1`.** A zero denominator is not measurable and is excluded, never
  recorded as `0.0`. Denominator 1 is kept as a measured value of 0.0 or 1.0 and is **coarse**, not missing: on the 110
  calibration cells 12 cells have a denominator of 2 or less (range 1–12).
- Cut `o*` = **0.75**, chosen by the balance rule in `benchmarks/calibrate_temporal_redundancy_b5.py`: among the observed
  values, maximise the smaller half; ties by smaller imbalance, then lower cut. The outcome does not enter the choice.
  On the calibration cells it splits **53 low / 56 high**.
- **Sensitivity, disclosed:** restricted to block 4's floor of 3 (denominator ≥ 3, n=97) the association is
  Spearman 0.447. The floor does not create the association.
- The covariate uses the control cell. The outcome is the paired difference R − C, so the control appears on both sides;
  that is inherent to this design and is why the covariate is defined on structures the control produces, not on the
  ratio arm's output.

**Selection disclosure, stated before the run.** The covariate is the one block 4 tested, chosen after reading §8.13's
ten-seed table, and its calibration set here is the 10 block-2 seeds plus the **100 block-4 seeds**. Block 4 was voided
by its own gate, so those cells are not being judged by this block, and rule 19 permits calibration on data that is not
being judged — but the block-4 cells were run under these same arms, on this same world, and their gains are the gains
this block re-measures. On those 109 cells the association is Pearson 0.449, Spearman 0.425
(slope 0.0469, residual sd 0.031). That is **in-sample and selection-contaminated**: it is the reason
the block exists, not evidence for it. The 100 fresh seeds are the first out-of-sample test.

## 5. Gates (a failed gate voids the block; it is not a negative result)

- **G0 liveness**: the C and R asserted sets differ on at least 96 of 100 seeds. If they do not, the arm is not
  what is being compared.
- **G1 comparability (C1′)**: the block-mean cap-20 control precision lies in [0.4347, 0.4987] (δ = 0.032 from
  `docs/gate13_control_precision_sweep.json`, as in blocks 2–4). Otherwise the block is `NOT COMPARABLE`.
- **G2 measurability**: `o_s` is defined on at least 96 of 100 seeds at a floor of 1. With the floor at
  1 this failed on 1 of 110 calibration cells, so the gate is now reachable — and it is retained rather than dropped
  precisely because the block-4 failure was a gate doing its job. Unmeasurable seeds are excluded from every criterion
  and counted, never imputed.
- **G3 split liveness**, added because block 4's failure was invisible to G2 alone: after the cut, both halves must
  contain at least 40 seeds. This is the half-balance that block 4 could not achieve; if it fails, the reason is recorded
  and the block is void, not analysed on a skewed subset. On the calibration cells the halves are
  53/56.

## 6. Criteria (evaluated once, in this order, by committed code)

- **M1 — half-split contrast.** `gain_s = coverage_R - coverage_C`. Split at `o*`. Pass iff both halves have at least 40
  seeds and `median(gain, high) - median(gain, low) >= 0.03`.
- **M2 — directional association.** Pass iff `Spearman(o_s, gain_s) >= 0.25` across the measurable seeds
  (one-sided; higher control-side duplication, larger gain). Calibration: 0.425.
- **M3 — replication (secondary, never confirmatory).** Pass iff at least 66 of
  100 seeds have `gain_s > 0`. Blocks 2, 3 and 4 gave 20/25, 88/100 and 81/87.

## 7. Decision table (fixed)

| M1 | M2 | G0-G3 | verdict |
|---|---|---|---|
| pass | pass | pass | **MODERATOR SUPPORTED** — control-side temporal redundancy predicts where the ratio arm helps |
| fail | pass | pass | **DIRECTIONAL ONLY** — the association is there, the half-split contrast is not |
| pass | fail | pass | **HALF-SPLIT ONLY** — a threshold contrast without a monotone association; read as fragile |
| fail | fail | pass | **MODERATOR NOT SUPPORTED** — the proxy is not a predictor at this n |
| — | — | fail | **VOID / NOT COMPARABLE** — report the gate, not a verdict |

M3 is reported beside the verdict and never substitutes for M1 or M2.

## 8. Power, computed in advance — and its asymmetry

Simulated by resampling the 109 calibration pairs with the mean preserved
(`gain = mean(gain) + slope·(o − mean(o)) + N(0, 0.031)`), 4,000 replicates per row. "Mechanism-sized" is the
slope that makes the expected half-split gap equal the bar, 0.03 / 0.55
= 0.0546.

| scenario | slope | M1 | M2 | M1 and M2 | M3 |
|---|---|---|---|---|---|
| mechanism-sized | 0.0546 | 0.478 | 0.994 | 0.478 | 1.0 |
| calibration-implied | 0.0469 | 0.283 | 0.978 | 0.283 | 1.0 |
| null (no association) | 0.0 | 0.0 | 0.009 | 0.0 | 1.0 |

**The asymmetry, stated before the data arrive.** M2 is well powered: **0.978** at the
calibrated association and **0.009** at none, so a pass on M2 is strong evidence and a miss is
evidence against. M1 is not: the calibrated half-split gap is 0.0258, **below** the 0.03 bar, so even a
perfect replication of the calibration effect passes M1 only **0.283** of the time. Joint
power is therefore **0.283** at the calibrated effect against
**0.0** at none. Read it as: **a miss on M1 is the calibrated expectation and is not evidence against the
hypothesis; only a pass on M1 is informative.** A miss on M2, by contrast, would be informative. This is the one place
block 5's design is weaker than block 4's claimed power, and it is published rather than left to be discovered after a
miss.

## 9. Pre-registered predictions

- **P1** G0 and G1 pass, as they did in blocks 2, 3 and 4.
- **P2** G2 passes at or above 96/100: with a floor of 1 the covariate is undefined only when the control asserts no
  world-covered temporal edge, which happened on 1 of 110 calibration cells.
- **P3** G3 passes: the cut is balance-optimal over 110 cells with a 53/56 split, and block 4's
  imbalance came from a cut estimated on ten seeds.
- **P4** M2 passes at +0.25: the calibration association is 0.425 on 109 cells and
  0.447 at the old floor, and M2 has 0.978 power at that effect.
- **P5** M1 fails, at the bar, on a draw whose gap is near the calibrated 0.0258. If that
  happens the verdict is **DIRECTIONAL ONLY**, and it is the registered expectation under the calibrated effect rather
  than a finding about the mechanism. A second moderator block would not fix this: the bar is fixed for comparability and
  the effect is below it, so raising n only approaches the 50% ceiling.

## 10. What each outcome would and would not license

- `MODERATOR SUPPORTED`: control-side temporal redundancy is a usable pre-run covariate for this arm on this world family,
  and §8.13's mechanism gains out-of-sample support. It does **not** establish causality — the covariate is measured on
  the control cell, not manipulated.
- `DIRECTIONAL ONLY`: the association replicates but does not clear the half-split bar; the covariate is a candidate
  stratifier, not yet a moderator. It does **not** license a threshold rule.
- `MODERATOR NOT SUPPORTED`: the §8.13 pattern does not generalize across seeds at n=100. It does **not** retract §8.13's
  composition finding, which is about *where* the effect lives, not *which seeds*.
- The decisive test remains an intervention, not a moderator: an arm identical to R that prefers temporal candidates whose
  edge no loop asserts at admission time. Not registered here, and §8.15's data suggest it is where the next block should
  go rather than a third between-seed proxy.

## 11. Freeze

Criteria, gates, cut, bars, allocation and decision table are frozen as written. No cell of 20271403-20271502 has been run.
Scoring code reads the cut and bars from `docs/gate13_temporal_redundancy_b5_calibration.json`. Artifacts:
`docs/gate13_temporal_redundancy_b5_calibration.json`, `docs/gate13_temporal_redundancy_block4.json` (calibration cells
only), `docs/gate13_redundancy_moderator_calibration.json` (block-2 gains), `docs/gate13_c1_respecification.json`.

## 12. Readings (2026-11-06, one scoring pass)

200 cells, seeds 20271403-20271502, C and R at cap 20, no cell substituted and no cell failed. Cut 0.75 and bars were read
from `docs/gate13_temporal_redundancy_b5_calibration.json`, the C1′ band from `docs/gate13_c1_respecification.json`;
nothing was adjusted after the run. The covariate was recomputed at the registered floor of 1 from the recorded
`overlap` and `pred_world` counts, as §3 says. Scored once by `benchmarks/score_temporal_redundancy_b5.py` into
`docs/gate13_temporal_redundancy_block5.json`.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness | 100/100 seeds with arm-dependent asserted sets | yes |
| G1 C1′ | mean control precision 0.4467 in [0.4347, 0.4987] | yes |
| G2 measurability | 99/100 seeds with `o_s` defined at floor 1 (required 96) | yes |
| G3 split liveness | 42 low / 57 high at `o*` = 0.75 (each ≥ 40) | yes |

**Verdict: DIRECTIONAL ONLY.** All four gates pass. **M1 half-split** fails: median gain 0.0357 low against 0.0625 high, a difference of +0.0268 against the 0.03 bar, on 42 low and 57 high seeds. **M2 association** passes: Spearman 0.407, 95% CI [0.219, 0.576], against the 0.25 bar. **M3 replication** passes as the secondary criterion: 88/99 seeds positive, 66 required.

The association replicates at the bar, so the direction of §8.13's pattern survives out of sample. The half-split contrast does not clear its bar, which is what the pre-registered power table said to expect: M1 has 0.283 power at the calibrated effect because the calibrated gap sits below 0.03. **A failed M1 here is therefore not evidence against the hypothesis** — it is the registered expectation — while the passing M2 is evidence for the association.

**Where this leaves the moderator question.** Blocks 3, 4 and 5 tested three different control-side proxies for the same
ratio-arm gain: loop *quantity* (block 3, `MODERATOR NOT SUPPORTED`), the world-covered overlap *share* with a floor of 3
and a ten-seed cut (block 4, void), and the same share with the floor and cut repaired (block 5, DIRECTIONAL ONLY). The measured
gain itself has now replicated on 100 fresh seeds (M3: 88/99, mean 0.0485),
so the effect is stable and the question is only what predicts it between seeds. §8.15's data and this block's both
point away from a between-seed proxy at the registered bars; the decisive test remains the intervention named in §10 —
an arm identical to R that prefers temporal candidates whose edge no loop asserts at admission time — which manipulates
the quantity instead of hoping it varies across seeds.
