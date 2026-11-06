# Gate 13 — loop-redundancy moderator pre-registration (block 3)

**Status: RUN (2026-11-06). Verdict: MODERATOR NOT SUPPORTED.** All 200 cells have since been executed and scored exactly once; §13 records the readings and §11 remains the freeze text. The criteria below were fixed before the first cell,
from artifacts that the block does not contain (§4). Amendments, if any, are appended with a date; this text is not edited
to match a result.

## 1. Question

Block 2 returned `TREATMENT NOT REPRODUCED` with C1′ passing for the first time, and §8.11-§8.13 narrowed the variation to
one place: the ratio arm always adds temporal (`prediction_candidate`) edges, loop (`loop_candidate`) coverage is identical
across arms, and the 20/5 split tracked whether those temporal edges were **already present in the loop structure**.

That mechanism makes a prediction about *which seeds* the treatment should help: where the loops already cover most of the
world, there is less for admission to add. This block tests that prediction on a fresh allocation, with a covariate that is
readable from the control cell before the ratio cell is scored.

## 2. What is registered, and what is not

Registered: the covariate, its threshold, three gates, three criteria, the decision table, and the power of every bar under
two effect sizes. Not registered and not changed: the arms (count control C, ratio arm R as defined in
`benchmarks/run_ratio_admission_arm.py`), cap 20, the world generator, the readout, and the frozen engine.

## 3. Allocation and cells

- Seeds **20271101-20271200**, **100 seeds**, chosen as the first run of 100 consecutive seeds at or after 20271001 that
  appears nowhere in the tree. Freshness scan: **517 files** (`.py`, `.md`, `.json`), **0
  occurrences in the allocated range**. The candidate window 20271001-20271100 was rejected for 2 pre-existing
  occurrences (20271001, 20271100), which is why the allocation starts at 20271101 and not at 20271001.
- Cells: **C and R at cap 20, 200 cells**. No other cap and no E arm — no criterion here reads them.
- Runner: `benchmarks/run_redundancy_block.py`, which records the asserted-set digest, coverage, precision and the store-time
  loop attribution. Command for the block:
  `PYTHONPATH="$PWD" PYTHONHASHSEED=0 .venv/bin/python benchmarks/run_redundancy_block.py --block 20271101:20271200 --budget 200 --jsonl .scratch/redundancy_block.jsonl`
- The runner was self-tested **before** the block on the excluded seed 20270901: both arms reproduce block 2's `asserted`,
  `covered` and digest (C 90/34/`1a51184e43b546a7`, R 87/34/`129da0ffd2052b85`). A runner that cannot reproduce a scored
  cell is not a runner for this block.

## 4. Covariate (pre-treatment, arm-independent)

`r_s = |W and L_s| / |W|`: the share of the world's 112 edges that the control cell's **loop** candidates
assert, where `L_s` is measured by a store-time observer over the same sleep payloads `structure_edges` aggregates. Loops are
built from the stream and are not what the admission cap ranks; §8.13 measured loop attribution identical across arms on
10/10 seeds, and gate **G2** re-checks that on every block cell.

- Threshold `r*` = 0.509, fixed from the 10 calibration seeds (block 2) as their median, which the block does
  not contain. `r_s < r*` is the *low-redundancy* half.
- The covariate uses the control cell. The outcome is the paired difference R − C. Disclosed: the control therefore appears
  on both sides, which is why the covariate is defined on **loop** edges only (arm-invariant, G2) and not on the arm's
  prediction edges (which would be the treatment's own output).

**Calibration, stated honestly.** On the 10 calibration seeds the association between `r_s` and the gain is
**Pearson 0.171, Spearman 0.22** — the *wrong* sign for the mechanism's prediction, with a linear
slope of 0.0528 and residual sd 0.0542. Ten seeds cannot separate +0.171 from −0.4. The block
therefore tests the proxy's directional prediction *against* the calibration's hint, not with it.

## 5. Gates (a failed gate voids the block; it is not a negative result)

- **G0 liveness**: the C and R asserted sets differ on at least 96 of 100 seeds. If they do not, the arm is not manipulating
  admission and nothing downstream is interpretable.
- **G1 comparability (C1′)**: the block-mean cap-20 control precision lies in [0.4347, 0.4987] (δ = 0.032 from
  `docs/gate13_control_precision_sweep.json`, as in block 2). If it does not, the block is `NOT COMPARABLE` and no criterion
  is read.
- **G2 loop invariance**: loop attribution is identical between arms on at least 98 of 100 seeds. If it is not, the covariate
  is treatment-dependent and the moderator framing is void.

## 6. Criteria (evaluated once, in this order, by committed code)

- **M1 — half-split contrast.** Let `gain_s = coverage_R - coverage_C`. Split at `r*`. Pass iff both halves have at least 40
  seeds and `median(gain, low) - median(gain, high) >= 0.03`.
- **M2 — directional association.** Pass iff `Spearman(r_s, gain_s) <= -0.25` across all 100 seeds
  (one-sided; the mechanism predicts lower redundancy, larger gain).
- **M3 — replication (secondary, never confirmatory).** Pass iff at least 66 of 100 seeds have
  `gain_s > 0`. Block 2 gave 20/25; this bar only asks whether that rate survives a fresh allocation.

## 7. Decision table (fixed)

| M1 | M2 | G0-G2 | verdict |
|---|---|---|---|
| pass | pass | pass | **MODERATOR SUPPORTED** — pre-treatment loop redundancy predicts where the ratio arm helps |
| fail | pass | pass | **DIRECTIONAL ONLY** — the association is there, the half-split contrast is not |
| pass | fail | pass | **HALF-SPLIT ONLY** — a threshold contrast without a monotone association; read as fragile |
| fail | fail | pass | **MODERATOR NOT SUPPORTED** — the proxy is not a predictor at this n |
| — | — | fail | **VOID / NOT COMPARABLE** — report the gate, not a verdict |

M3 is reported beside the verdict and never substitutes for M1 or M2.

## 8. Power, computed in advance

Simulated by resampling the 10 calibration pairs and adding Gaussian noise at the fitted residual sd
(0.0542), 4,000 replicates per row. "Mechanism-sized" is a slope of -0.1 — the effect the mechanism
implies, i.e. about 0.055 of coverage across the observed r range.

| scenario | n | M1 | M2 | M1 and M2 | M3 |
|---|---|---|---|---|---|
| mechanism-sized | 100 | 0.361 | 0.587 | 0.327 | 0.0 |
| calibration-implied | 100 | 0.001 | 0.0 | 0.0 | 0.002 |
| null (no association) | 100 | 0.012 | 0.005 | 0.002 | 0.001 |

**What this means, before the data arrive.** The joint bar has **0.327** power against a real,
mechanism-sized moderator, and the false-positive rate at no association is **0.002**. The test is therefore
**asymmetric by design**: a `MODERATOR SUPPORTED` verdict would be strong evidence; a `MODERATOR NOT SUPPORTED` verdict is
**weak evidence against the mechanism** and only meaningful evidence against the proxy. If the calibration's
+0.22 is the truth, the expected verdict is `MODERATOR NOT SUPPORTED` with power 0.0 to have
said otherwise — so that outcome must not be reported as a refutation of §8.13.

For scale: 25 seeds would have given 0.348; 100 is the smallest allocation in this design
that keeps the joint power above 0.327 without exceeding a 15-minute block.

## 9. Pre-registered predictions

- **P1** G2 holds: loops are arm-invariant on at least 98 of 100 seeds (they were on 10/10).
- **P2** M3 passes: the overall gain replicates at 20/25-like rates, since nothing about the arm changed.
- **P3** M2 fails at the -0.25 bar, because the calibration association is positive
  (+0.22); if it passes, the signal is negative and the proxy is live.
- **P4** If M2 passes, M1 also passes (the half-split contrast is the easier of the two at a mechanism-sized effect:
  0.361 vs 0.587).
- **P5** The block's loop-coverage distribution is close to the calibration's (0.24-0.79); if `r_s` is compressed near 0 or 1,
  the split has too few seeds per half and M1 is `INCONCLUSIVE BY SIZE`, which is recorded as such.

## 10. What each outcome would and would not license

- `MODERATOR SUPPORTED`: loop redundancy is a usable pre-run covariate for this arm on this world family. It does **not**
  establish the mechanism's causal claim (loops pre-empting temporal edges) — that needs the time-ordered observer §8.13
  could not provide, or the loop-novelty arm below.
- `MODERATOR NOT SUPPORTED`: the proxy is not a predictor at n=100. It does **not** refute §8.13's composition finding, and it
  does **not** refute the mechanism; it says the between-seed implication is too weak to detect at this size.
- The decisive test of the mechanism is an **intervention**, not a moderator: an arm identical to R that prefers temporal
  candidates whose edge is not already asserted by a loop at admission time. That arm changes the outcome directly and is
  not registered here.

## 11. Freeze

Criteria, gates, threshold, bars, allocation and decision table are frozen as written. No cell of 20271101-20271200 has been
run. Scoring code must read the threshold and bars from `docs/gate13_redundancy_moderator_calibration.json` rather than
recompute them. Artifacts: `docs/gate13_redundancy_moderator_calibration.json`,
`docs/gate13_structure_provenance.json`, `docs/gate13_ratio_block2.json`.

## 12. Amendment 1 (2026-11-06, before the first cell) — `loop_hash` recorded

G2 compares loop attribution *across arms*. The runner as frozen recorded only `loop_world_edges`, a count, and a count
cannot establish that the two arms attribute the same loop edges. Before any cell of this block was run, the runner was
amended to record `loop_hash` — a SHA-1 over the sorted loop-covered world-edge set — and G2 now compares that digest across
arms. Nothing else changed: the allocation, gates, criteria, bars, threshold and decision table are exactly as frozen in
§3-§11. No cell of 20271101-20271200 had been executed when this amendment was made.

## 13. Readings (2026-11-06, one scoring pass)

200 cells, seeds 20271101-20271200, C and R at cap 20,
no cell substituted and no cell failed. Threshold 0.509 and bars were read from
`docs/gate13_redundancy_moderator_calibration.json`, the C1′ band from `docs/gate13_c1_respecification.json`; nothing was
adjusted after the run. Scored once, by `benchmarks/score_redundancy_block.py`, into
`docs/gate13_redundancy_block3.json`.

**Gates** — all three pass, so the block is admissible and the criteria below are read as a test, not as a void.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness | 100/100 seeds with arm-dependent asserted sets | yes |
| G1 C1′ | mean control precision 0.4444 in [0.4347, 0.4987] | yes |
| G2 loop invariance | 100/100 seeds with identical loop edge sets across arms | yes |

**Criteria** — evaluated in the registered order, once.

| Criterion | Reading | Bar | Pass |
| --- | --- | --- | --- |
| M1 half-split | low `r` (n=31) median 0.0357 vs high (n=69) 0.0536; difference -0.0179 | ≥ +0.03 | no |
| M2 monotone | Spearman -0.02, 95% bootstrap CI [-0.243, 0.185] | ≤ -0.25 | no |
| M3 replication (secondary) | 88/100 seeds with a positive gain | ≥ 66 | yes |

**Verdict: MODERATOR NOT SUPPORTED.**

M3 passes: the ratio arm's gain replicates again in a fresh allocation of 100 seeds, 88 of them positive,
mean gain 0.0442 coverage and median 0.0535, against control coverage
0.3273 and ratio coverage 0.3520. M1 and M2 both fail. Pre-run loop redundancy does
not predict where the arm pays: the low-redundancy half gains *more* than the high-redundancy half
(0.0357 vs 0.0536, difference -0.0179, opposite to the registered
sign), and the rank association is -0.02 with an interval that spans zero and excludes the registered direction
(the bar, -0.25, lies outside the interval). The covariate spans `r` 0.2054 to 0.8214 across the
100 seeds, so the test was not starved of variation.

Two limits are recorded rather than smoothed over. First, M1 as specified requires at least 40 seeds per half and the
allocation produced 31/69 against the fixed threshold 0.509, so M1 is not satisfied on
size as well as on sign; its point estimate points the wrong way regardless, so the failure does not rest on the split.
Second, §8 fixed joint power at 0.327 under a mechanism-sized effect and 0.002 under no association, so this miss is
evidence against the redundancy mechanism — moderate against a mechanism that shifts the gain by ~0.10 across the covariate,
weak against a small one. It does not weaken the replication finding, which is M3's separate claim.

What this does and does not license, per §10: the redundancy story is retired as the explanation for the 20/5 split. The
§8.13 fact stands unchanged — the arm's effect is carried by `prediction_candidate` edges, not loops — and this block adds
that the *quantity* of pre-existing loop coverage does not predict the payoff. The question the 20/5 split posed is
therefore open again, and a further block would need a different pre-treatment covariate, not a re-run of this one.
