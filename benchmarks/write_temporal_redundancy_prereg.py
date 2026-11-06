"""Generate docs/GATE13-TEMPORAL-REDUNDANCY-PREREGISTRATION.md from the calibration artifact."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
c = json.loads((REPO / "docs/gate13_temporal_redundancy_calibration.json").read_text())
a, b, p = c["allocation"], c["bars"], c["power"]
thr, fit, asc, fr = c["threshold_o"], c["linear_fit"], c["association"], c["freshness"]
pairs = c["pairs"]
lo, hi = a["lo"], a["hi"]


def row(k, lab):
    d = p[k]
    return (f"| {lab} | {d['slope']} | {d['power_m1_half_split']} | {d['power_m2_spearman']} | "
            f"{d['power_both']} | {d['power_m3_replication']} |")


DOC = f"""# Gate 13 — control-side temporal redundancy pre-registration (block 4)

**Status: FROZEN, NOT RUN.** No cell of this block has been executed. The criteria below were fixed before the first cell,
from an artifact the block does not contain (§4). Amendments, if any, are appended with a date; this text is not edited to
match a result.

## 1. Question

Block 3 closed the loop-coverage proxy: pre-run loop redundancy does **not** predict where the ratio arm pays
(`MODERATOR NOT SUPPORTED`; Spearman {asc and '-0.02'}, high-redundancy half gaining more, not less). §8.13's store-time
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

- Seeds **{lo}-{hi}**, **{a['seeds']} seeds**. Freshness scan: **{fr['files_scanned']} files** (`.py`, `.md`, `.json`),
  **0 occurrences** in the allocated range.
- **{fr['rejected_hits'][0]} is excluded**: it occurs in the tree only as this harness's own scan-start constant, and an
  allocation may not contain a seed already written into the tree — the rule is applied to the letter, not to intent.
- Cells: **C and R at cap 20, {2 * a['seeds']} cells**. No other cap and no E arm — no criterion here reads them.
- Runner: `benchmarks/run_temporal_redundancy_block.py`. Command:
  `PYTHONPATH="$PWD" PYTHONHASHSEED=0 .venv/bin/python benchmarks/run_temporal_redundancy_block.py --block {lo}:{hi} --budget {2 * a['seeds']} --jsonl .scratch/temporal_redundancy_block.jsonl`
- The runner was self-tested **before** this freeze on the excluded seed 20270901: both arms reproduce block 2's `asserted`,
  `covered` and digest (C 90/34/`1a51184e43b546a7`, R 87/34/`129da0ffd2052b85`), and it records the covariate on both arms
  (C `o` = 0.0, R `o` = 0.4615 on that seed).

## 4. Covariate (read from the control cell, before the ratio cell is scored)

`o_s = |L_s ∩ P_s ∩ W| / |P_s ∩ W|`, where `P_s` is the set of world edges the control cell's
`prediction_candidate` structures assert, `L_s` its `loop_candidate` edges, and `W` the world's edges. Both sets come from
the same store-time observer §8.13 validated (all 20 cells passed replay-digest, edge-set and per-edge-weight checks).

- Threshold `o*` = **{thr}**, the median of the 10 calibration seeds (block 2), which this block does not contain.
  `o_s >= o*` is the *high-overlap* half.
- **Measurability rule.** `o_s` is a share, so it is defined only when `|P_s ∩ W| >= {c['min_denominator']}`. A seed whose control cell
  asserts fewer temporal world edges than that is **not measurable and is excluded** — never recorded as `o_s = 0.0`. If
  fewer than 96 seeds are measurable the block is void (gate G2).
- The covariate uses the control cell. The outcome is the paired difference R − C, so the control appears on both sides;
  that is inherent to this design and is why the covariate is defined on structures the control produces, not on the ratio
  arm's output.

**Selection disclosure, stated before the run.** This covariate was chosen *after* reading §8.13's ten-seed table, and on
those same ten seeds it associates with the gain at Pearson {asc['pearson']}, Spearman {asc['spearman']} (slope
{fit['slope']}, residual sd {fit['resid_sd']}). That association is **in-sample and selection-contaminated**: it is not
independent evidence for anything, it is the reason the block exists. The block's {a['seeds']} fresh seeds are the first
out-of-sample test of it. It also differs from block 3 in one way that matters for how a pass should be read: block 3's
calibration pointed the wrong way and still failed; this one points the predicted way, so a pass here would be consistent
with the hypothesis and a fail would contradict it sharply.

## 5. Gates (a failed gate voids the block; it is not a negative result)

- **G0 liveness**: the C and R asserted sets differ on at least 96 of {a['seeds']} seeds. If they do not, the arm is not what
  is being compared.
- **G1 comparability (C1′)**: the block-mean cap-20 control precision lies in [0.4347, 0.4987] (δ = 0.032 from
  `docs/gate13_control_precision_sweep.json`, as in blocks 2 and 3). Otherwise the block is `NOT COMPARABLE`.
- **G2 measurability**: `o_s` is defined on at least 96 of {a['seeds']} seeds (i.e. `|P_s ∩ W| >= {c['min_denominator']}` on the control
  cell). Unmeasurable seeds are excluded from every criterion and counted, not imputed.

## 6. Criteria (evaluated once, in this order, by committed code)

- **M1 — half-split contrast.** `gain_s = coverage_R - coverage_C`. Split at `o*`. Pass iff both halves have at least 40
  seeds and `median(gain, high) - median(gain, low) >= {b['m1_median_gain_difference']}`.
- **M2 — directional association.** Pass iff `Spearman(o_s, gain_s) >= {b['m2_spearman_min']}` across the measurable seeds
  (one-sided; the hypothesis is that more control-side duplication means more room to trade, so higher overlap, larger gain).
- **M3 — replication (secondary, never confirmatory).** Pass iff at least {round(b['m3_positive_share'] * a['seeds'])} of {a['seeds']} seeds have
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

Simulated by resampling the {asc['n']} calibration pairs with the mean preserved
(`gain = mean(gain) + slope·(o − mean(o)) + N(0, {fit['resid_sd']})`), 4,000 replicates per row. "Mechanism-sized" is a
slope of 0.10 across the observed `o` range, about 0.08 of coverage.

| scenario | slope | M1 | M2 | M1 and M2 | M3 |
|---|---|---|---|---|---|
{row('n100_mechanism_sized', 'mechanism-sized')}
{row('n100_calibration_implied', 'calibration-implied')}
{row('n100_null', 'null (no association)')}

**What this means, before the data arrive.** The joint bar has **{p['n100_mechanism_sized']['power_both']}** power against a mechanism-sized
effect and **{p['n100_null']['power_both']}** at no association, so the test is asymmetric: a pass is strong evidence, a miss is evidence
against the hypothesis — stronger evidence than block 3's miss, because here the calibration association is in the tested
direction and the design is not fighting its own prior.

## 9. Pre-registered predictions

- **P1** G0 and G1 pass, as they did in blocks 2 and 3.
- **P2** G2 passes: the control asserts at least {c['min_denominator']} temporal world edges on nearly every seed (the calibration
  range was {min(q['pred_world'] for q in pairs)}–{max(q['pred_world'] for q in pairs)}).
- **P3** M3 passes: the gain replicates (~88/100 in block 3), since nothing about the arm changed.
- **P4** M2 passes at +{b['m2_spearman_min']}: the calibration association was +{asc['spearman']}, and even heavily shrunk toward zero an
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

Criteria, gates, threshold, bars, allocation and decision table are frozen as written. No cell of {lo}-{hi} has been run.
Scoring code must read the threshold and bars from `docs/gate13_temporal_redundancy_calibration.json`. Artifacts:
`docs/gate13_temporal_redundancy_calibration.json`, `docs/gate13_structure_provenance.json`,
`docs/gate13_redundancy_block3.json`, `docs/gate13_ratio_block2.json`.
"""
(REPO / "docs/GATE13-TEMPORAL-REDUNDANCY-PREREGISTRATION.md").write_text(DOC)
print("prereg written:", len(DOC.splitlines()), "lines")
