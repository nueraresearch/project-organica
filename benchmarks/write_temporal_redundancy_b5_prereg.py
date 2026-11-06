"""Generate docs/GATE13-TEMPORAL-REDUNDANCY-B5-PREREGISTRATION.md from the block-5 calibration artifact."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
c = json.loads((REPO / "docs/gate13_temporal_redundancy_b5_calibration.json").read_text())
a, b, p = c["allocation"], c["bars"], c["power"]
thr, fit, asc, fr = c["cut_o"], c["linear_fit"], c["association"], c["freshness"]
sp, den, rng, sens = c["calibration_split"], c["denominator"], c["o_range"], c["sensitivity_floor3"]
pairs = c["pairs"]
lo, hi = a["lo"], a["hi"]
rej = fr["rejected_hits"]
n_meas = c["calibration_sources"]["measurable"]
le2 = den["le2"]


def row(k, lab):
    d = p[k]
    return (f"| {lab} | {d['slope']} | {d['power_m1_half_split']} | {d['power_m2_spearman']} | "
            f"{d['power_both']} | {d['power_m3_replication']} |")


DOC = f"""# Gate 13 — control-side temporal redundancy, block 5 (repaired covariate)

**Status: FROZEN, NOT RUN.** No cell of this block has been executed. The criteria below were fixed before the first
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
only {json.loads((REPO / "docs/gate13_temporal_redundancy_b5_calibration.json").read_text())["fixes_from_block4"]["why_not_a_count"].split("Spearman ")[1].split(" ")[0]} on the same 110 cells and its expected half-split gap is
0.015 against a 0.03 bar. A block frozen on it would be a null ritual. The count is recorded in the artifact and in §4
of the capacity record so the choice is auditable.

## 2. What is registered, and what is not

Registered: the covariate definition and its floor, its cut, three gates, three criteria, the decision table, and the
power of every bar under three effect sizes. Not registered and not changed: the arms (count control C, ratio arm R as
defined in `benchmarks/run_ratio_admission_arm.py`), cap 20, the world generator, the readout, and the frozen engine.

## 3. Allocation and cells

- Seeds **{lo}-{hi}**, **{a['seeds']} seeds**. Freshness scan: **{fr['files_scanned']} files** (`.py`, `.md`, `.json`),
  **0 occurrences** in the allocated range.
- Excluded by the same rule as block 4, applied to the letter: **{", ".join(str(x) for x in rej)}**. {rej[0]} occurs in
  the tree only as this harness's own scan-start constant; {", ".join(str(x) for x in rej[1:])} occur only in the
  superseded block-5 calibration artifact, which was written and then replaced before any cell ran. An allocation may not
  contain a seed already written into the tree, however innocently, and the run starts at the first free {a['seeds']}-seed
  window.
- Cells: **C and R at cap 20, {2 * a['seeds']} cells**. No other cap and no E arm — no criterion here reads them.
- Runner: `benchmarks/run_temporal_redundancy_block.py`, unchanged from block 4 and already self-tested against block 2 on
  the excluded seed 20270901 (C 90/34/`1a51184e43b546a7`, R 87/34/`129da0ffd2052b85`). Command:
  `PYTHONPATH="$PWD" PYTHONHASHSEED=0 .venv/bin/python benchmarks/run_temporal_redundancy_block.py --block {lo}:{hi} --budget {2 * a['seeds']} --jsonl .scratch/temporal_redundancy_b5.jsonl`
- The runner writes its `o` field at the old floor of 3; the scorer **ignores** that field and recomputes `o_s` from the
  recorded `overlap` and `pred_world` counts. That is stated here so the mismatch is not mistaken for a defect later.

## 4. Covariate (read from the control cell, before the ratio cell is scored)

`o_s = |L_s ∩ P_s ∩ W| / |P_s ∩ W|`, where `P_s` is the set of world edges the control cell's `prediction_candidate`
structures assert, `L_s` its `loop_candidate` edges, and `W` the world's edges. Both sets come from the same store-time
observer §8.13 validated.

- **Measurability floor: `|P_s ∩ W| >= {c['floor']}`.** A zero denominator is not measurable and is excluded, never
  recorded as `0.0`. Denominator 1 is kept as a measured value of 0.0 or 1.0 and is **coarse**, not missing: on the 110
  calibration cells {le2} cells have a denominator of 2 or less (range {den['min']}–{den['max']}).
- Cut `o*` = **{thr}**, chosen by the balance rule in `benchmarks/calibrate_temporal_redundancy_b5.py`: among the observed
  values, maximise the smaller half; ties by smaller imbalance, then lower cut. The outcome does not enter the choice.
  On the calibration cells it splits **{sp['low_n']} low / {sp['high_n']} high**.
- **Sensitivity, disclosed:** restricted to block 4's floor of 3 (denominator ≥ 3, n={sens['n']}) the association is
  Spearman {sens['spearman']}. The floor does not create the association.
- The covariate uses the control cell. The outcome is the paired difference R − C, so the control appears on both sides;
  that is inherent to this design and is why the covariate is defined on structures the control produces, not on the
  ratio arm's output.

**Selection disclosure, stated before the run.** The covariate is the one block 4 tested, chosen after reading §8.13's
ten-seed table, and its calibration set here is the 10 block-2 seeds plus the **100 block-4 seeds**. Block 4 was voided
by its own gate, so those cells are not being judged by this block, and rule 19 permits calibration on data that is not
being judged — but the block-4 cells were run under these same arms, on this same world, and their gains are the gains
this block re-measures. On those {asc['n']} cells the association is Pearson {asc['pearson']}, Spearman {asc['spearman']}
(slope {fit['slope']}, residual sd {fit['resid_sd']}). That is **in-sample and selection-contaminated**: it is the reason
the block exists, not evidence for it. The {a['seeds']} fresh seeds are the first out-of-sample test.

## 5. Gates (a failed gate voids the block; it is not a negative result)

- **G0 liveness**: the C and R asserted sets differ on at least 96 of {a['seeds']} seeds. If they do not, the arm is not
  what is being compared.
- **G1 comparability (C1′)**: the block-mean cap-20 control precision lies in [0.4347, 0.4987] (δ = 0.032 from
  `docs/gate13_control_precision_sweep.json`, as in blocks 2–4). Otherwise the block is `NOT COMPARABLE`.
- **G2 measurability**: `o_s` is defined on at least 96 of {a['seeds']} seeds at a floor of {c['floor']}. With the floor at
  1 this failed on 1 of 110 calibration cells, so the gate is now reachable — and it is retained rather than dropped
  precisely because the block-4 failure was a gate doing its job. Unmeasurable seeds are excluded from every criterion
  and counted, never imputed.
- **G3 split liveness**, added because block 4's failure was invisible to G2 alone: after the cut, both halves must
  contain at least 40 seeds. This is the half-balance that block 4 could not achieve; if it fails, the reason is recorded
  and the block is void, not analysed on a skewed subset. On the calibration cells the halves are
  {sp['low_n']}/{sp['high_n']}.

## 6. Criteria (evaluated once, in this order, by committed code)

- **M1 — half-split contrast.** `gain_s = coverage_R - coverage_C`. Split at `o*`. Pass iff both halves have at least 40
  seeds and `median(gain, high) - median(gain, low) >= {b['m1_median_gain_difference']}`.
- **M2 — directional association.** Pass iff `Spearman(o_s, gain_s) >= {b['m2_spearman_min']}` across the measurable seeds
  (one-sided; higher control-side duplication, larger gain). Calibration: {asc['spearman']}.
- **M3 — replication (secondary, never confirmatory).** Pass iff at least {round(b['m3_positive_share'] * a['seeds'])} of
  {a['seeds']} seeds have `gain_s > 0`. Blocks 2, 3 and 4 gave 20/25, 88/100 and 81/87.

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

Simulated by resampling the {asc['n']} calibration pairs with the mean preserved
(`gain = mean(gain) + slope·(o − mean(o)) + N(0, {fit['resid_sd']})`), 4,000 replicates per row. "Mechanism-sized" is the
slope that makes the expected half-split gap equal the bar, 0.03 / {round(fit['expected_half_split_gap'] / fit['slope'], 3)}
= {p['n100_mechanism_sized']['slope']}.

| scenario | slope | M1 | M2 | M1 and M2 | M3 |
|---|---|---|---|---|---|
{row('n100_mechanism_sized', 'mechanism-sized')}
{row('n100_calibration_implied', 'calibration-implied')}
{row('n100_null', 'null (no association)')}

**The asymmetry, stated before the data arrive.** M2 is well powered: **{p['n100_calibration_implied']['power_m2_spearman']}** at the
calibrated association and **{p['n100_null']['power_m2_spearman']}** at none, so a pass on M2 is strong evidence and a miss is
evidence against. M1 is not: the calibrated half-split gap is {fit['expected_half_split_gap']}, **below** the 0.03 bar, so even a
perfect replication of the calibration effect passes M1 only **{p['n100_calibration_implied']['power_m1_half_split']}** of the time. Joint
power is therefore **{p['n100_calibration_implied']['power_both']}** at the calibrated effect against
**{p['n100_null']['power_both']}** at none. Read it as: **a miss on M1 is the calibrated expectation and is not evidence against the
hypothesis; only a pass on M1 is informative.** A miss on M2, by contrast, would be informative. This is the one place
block 5's design is weaker than block 4's claimed power, and it is published rather than left to be discovered after a
miss.

## 9. Pre-registered predictions

- **P1** G0 and G1 pass, as they did in blocks 2, 3 and 4.
- **P2** G2 passes at or above 96/100: with a floor of 1 the covariate is undefined only when the control asserts no
  world-covered temporal edge, which happened on 1 of 110 calibration cells.
- **P3** G3 passes: the cut is balance-optimal over 110 cells with a {sp['low_n']}/{sp['high_n']} split, and block 4's
  imbalance came from a cut estimated on ten seeds.
- **P4** M2 passes at +{b['m2_spearman_min']}: the calibration association is {asc['spearman']} on {asc['n']} cells and
  {sens['spearman']} at the old floor, and M2 has {p['n100_calibration_implied']['power_m2_spearman']} power at that effect.
- **P5** M1 fails, at the bar, on a draw whose gap is near the calibrated {fit['expected_half_split_gap']}. If that
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

Criteria, gates, cut, bars, allocation and decision table are frozen as written. No cell of {lo}-{hi} has been run.
Scoring code reads the cut and bars from `docs/gate13_temporal_redundancy_b5_calibration.json`. Artifacts:
`docs/gate13_temporal_redundancy_b5_calibration.json`, `docs/gate13_temporal_redundancy_block4.json` (calibration cells
only), `docs/gate13_redundancy_moderator_calibration.json` (block-2 gains), `docs/gate13_c1_respecification.json`.
"""
(REPO / "docs/GATE13-TEMPORAL-REDUNDANCY-B5-PREREGISTRATION.md").write_text(DOC)
print("prereg written:", len(DOC.splitlines()), "lines")
