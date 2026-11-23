# Gate 13 — the loop-free preference arm, block 6 (intervention)

**Status: RUN (2026-11-06). Verdict: VOID / NOT COMPARABLE.** The criteria, gates, bar, allocation and decision table below were fixed before the first
cell, from artifacts the block does not contain (§4, §5). This text is not edited to match a result; readings are
appended in §12 with a date.

## 1. Question

Blocks 3, 4 and 5 asked whether a between-seed proxy predicts where the ratio arm helps. Block 3 said no
(`MODERATOR NOT SUPPORTED`), block 4 was void, block 5 said the association replicates but the threshold contrast does
not (`DIRECTIONAL ONLY`). All three measured something the control cell happened to do. Block 6 manipulates instead.

**Does removing temporal redundancy from the ratio arm's admission budget raise its coverage?** §10 of the block-5
pre-registration names this as the decisive test: an arm identical to R that prefers temporal candidates whose edge no
loop asserts at admission time. That arm is registered here, with its criteria fixed by calibration rather than by
hoping the covariate varies.

## 2. What is registered, and what is not

Registered: the arm's definition and its one changed sort key, the world, cap 20, the readout, three gates, two
criteria, the decision table, the bar and its provenance, and the power of the bar under the calibrated effect.

Not changed: `organica/sleep.py`, `organica/sleep_extraction.py`, `organica/sleep_selection.py` and every other frozen
file. The arm is an in-process subclass, as `benchmarks/ablation_study.py` is. The readout is blocks 2–5's: asserted
temporal edges at the end of acquisition, coverage of the world's edges, precision. Arm C (count admission) and arm R
(ratio admission) are the registered arms of blocks 2–5, unchanged, and R is the baseline this block modifies.

## 3. Allocation and cells

- Seeds **20271614-20271713**, **100 seeds**, chosen as the first free 100-seed window after the ten calibration
  seeds 20271604-20271613, by scanning the tree plus those seeds.
  first free 100-seed window after the calibration block, scanned over the tree plus the calibration seeds; an allocation may not contain a seed already written into the tree.
- Cells: **C, R and Y at cap 20 — 300 cells.** No other cap; no E arm.
- Runner: `benchmarks/run_loop_free_admission_block.py`, validated against block 2 before calibration (C 90 asserted /
  34 covered / `1a51184e43b546a7`; R 87 / 34 / `129da0ffd2052b85`, both equal to the block-2 artifact).
  Command:
  `PYTHONPATH="$PWD" PYTHONHASHSEED=0 .venv/bin/python benchmarks/run_loop_free_admission_block.py --block 20271614:20271713 --budget 300 --jsonl .scratch/loop_free_block6.jsonl`
- The runner is resumable and writes one JSON line per (arm, cap, seed). A missing cell is a defect, not a seed to
  substitute.

## 4. The intervention, stated exactly

Arm **Y** is R in every respect -- the same candidate construction (`PairedDiagnosticSleepService`, i.e. every temporal
edge meeting `PREDICTION_MIN_COUNT`), the same cap of 20, the same ratio key `-count / source_frequency` with the same
deterministic tiebreak -- with one additional step before the cap is applied:

> a candidate whose edge a loop candidate asserts **this cycle** sorts after one that no loop asserts; the cap is
> spent on non-loop edges first, and loop-asserted edges are admitted only as backfill when fewer than 20 non-loop
> candidates exist.

The loop set is the one the engine itself forms for that cycle. `SleepService.run` calls `_build_loops(temporal)` at
line 166 and `_build_predictions(temporal, freqs)` at line 175, so the arm recomputes that same deterministic function
on the same `temporal` mapping before sorting; it does not change what a loop is, and it does not change which
candidates are admissible. Edges are compared undirected because the readout (`structure_edges`) counts a loop path in
both directions.

**The preference is already at maximum dose, and this is a finding, not an assumption.** The arm was first calibrated
as a reorder (X) and then as a reservation (Y). On all ten calibration seeds the two produced identical effects,
composition and displacement statistics, field for field, because the candidate pool always holds at least 20 non-loop
edges -- with that many, sorting loop-asserted edges last and reserving the cap select the same set. Reserving is
therefore not a stronger version of reordering on this world family, and block 6 registers one intervention arm. The
two arms would diverge only on a seed whose pool holds fewer than 20 non-loop edges; the block records how often that
happens (never, if G2 passes as calibrated).

## 5. Calibration evidence (ten seeds, not judged here)

Reference: `docs/gate13_loop_free_admission_calibration.json`, `docs/gate13_loop_free_dose_calibration.json`, and
`docs/gate13_loop_free_block6_calibration.json`.

- **The perturbation is real.** The preference displaced at least one admitted edge from R's ratio-ordered cap on
  10 of 10 seeds, with a mean of 626.4 displaced edges across the
  acquisition cycles (median 550.5, max 977) and movement in
  88.5 cycles per seed. It is not an arm that looks different and does nothing.
- **The final-structure effect is small and sparse.** Mean coverage difference Y - R 0.0152, median
  0.0044, sd 0.0211, range [0.0, 0.0625], positive on 5 of 10 seeds.
  Half the seeds are exactly unchanged: the intervention changes which edges are admitted each cycle, and the final
  asserted structure is the accumulation of ninety cycles, so a reallocated admission budget moves a few edges.
- **Where the effect sits.** Loop-covered coverage is unchanged on average (20.6 vs
  20.6): the edges loops assert are still asserted by the loops themselves. The movement is in
  novel, non-loop covered edges (47.2 vs 48.9). That is the mechanism
  the arm claims, and M2 tests it.
- **The criterion follows from this distribution, and is stated before the run.** With the effect zero on half the
  seeds, a median criterion would report the zeros as the result (calibrated median 0.0044) and a sign
  criterion has roughly 3% power at 100 seeds. The quantity the mechanism predicts is a mean: a fixed budget
  reallocated away from redundant edges pays whenever a displaced edge was a world edge. The primary criterion is
  therefore the paired mean difference. This choice is made in calibration, is disclosed here, and is not a response to
  anything the block has produced -- no cell of 20271614-20271713 has run.

## 6. Gates (a failed gate voids the block; it is not a negative result)

- **G0 liveness**: the Y and R asserted sets differ on at least 96 of 100 seeds. Calibration: 6 of 10.
- **G0b liveness of the pair being measured**: C and R asserted sets differ on at least 96 seeds, as in blocks 2–5.
- **G1 comparability (C1′)**: the block-mean cap-20 control precision lies in [0.4347, 0.4987] (δ = 0.032,
  `docs/gate13_control_precision_sweep.json`). Calibration arm-C precision is not part of this block's data; the gate is
  the same one blocks 2–5 used, on the same arm.
- **G2 perturbation**: the preference displaced at least one edge on at least 96 of 100 seeds. Calibration:
  10 of 10. An intervention that displaces nothing has not run, and a null from it would
  be an unrun experiment, not a result.

## 7. Criteria (evaluated once, in this order, by committed code)

- **M1 — the intervention's effect.** `d_s = coverage_Y(s) - coverage_R(s)`. Pass iff
  `mean(d) >= 0.01` **and** the 95% bootstrap interval of the mean excludes zero (lower bound > 0).
  Calibration: mean 0.0152, interval [0.00447, 0.02858].
- **M2 — the mechanism check.** Pass iff the gain sits where the arm claims: `mean(covered_novel_Y - covered_novel_R)
  >= 0.005` with its bootstrap interval excluding zero, **and** loop-covered coverage does not fall on average
  (`mean(covered_loop_Y - covered_loop_R) >= 0`). Calibration: novel mean 1.7 (interval [0.5, 3.2]),
  loop-covered mean difference 0.0. M2 is a second criterion on the same cells: it does not rescue
  M1 and is reported beside it.

## 8. Decision table (fixed)

| M1 | M2 | G0–G2 | verdict |
|---|---|---|---|
| pass | pass | pass | **INTERVENTION SUPPORTED** — removing admission redundancy raises coverage, in the place the mechanism names |
| pass | fail | pass | **COVERAGE ONLY** — coverage rises but not via the novel-edge channel; read as unexplained |
| fail | — | pass | **INTERVENTION NOT SUPPORTED** — the loop-free preference does not beat R at the registered bar |
| — | — | fail | **VOID / NOT COMPARABLE** — report the gate, not a verdict |

## 9. Power, computed in advance

Resampling the ten calibration pairs to 100 seeds, 4,000 replicates per row, counting `mean >= bar` and the same
condition with the interval's lower bound above zero.

| bar | point criterion | point and interval |
|---|---|---|
| 0.005 | 1.000 | 1.000 |
| 0.010 | 0.997 | 0.997 |
| 0.015 | 0.534 | 0.534 |
| 0.020 | 0.011 | 0.011 |
| 0.030 | 0.000 | 0.000 |

At the frozen bar of 0.01 the calibrated mean is 2.46 standard errors above it, so the criterion
is powered under the calibrated effect -- unlike block 5's M1, which was published as underpowered. The cost is that
the mean is tail-sensitive: 5 of 10 calibration seeds carry the whole effect, and if the block's
draw has fewer large gains than the calibration did, M1 fails. The ten-seed sd is itself uncertain, so the table is an
estimate, and the artifact reports the observed mean, interval, median, positive share and every seed row beside the
verdict.

## 10. Pre-registered predictions

- **P1** G0, G0b, G1 and G2 pass: the arms differ, the block is comparable, and the preference displaces something.
- **P2** M1 passes: mean effect at or above 0.01 with an interval above zero, near the calibrated 0.0152.
- **P3** M2 passes: the gain is in novel covered edges and loop-covered coverage is unchanged.
- **P4** The gain over C is larger for Y than for R by the M1 margin: `mean(Y - C) - mean(R - C) >= 0.01`. Both
  gains over C are reported descriptively, and this prediction is context, not a criterion.

## 11. What each outcome would and would not license

- `INTERVENTION SUPPORTED`: on this world family, at this cap and readout, the admission budget's redundancy is a cost
  -- spending it on edges loops already assert buys less coverage than spending it elsewhere. It licenses a change of
  admission *rule*, not a claim about what loops are for: the arm removes prediction candidates whose edges loops
  assert, and the loops themselves are untouched.
- `COVERAGE ONLY`: the arm helps, but not through the channel it claims; the mechanism sentence in §1 is not supported
  even though the arm is useful.
- `INTERVENTION NOT SUPPORTED`: at this bar the preference does not beat R. It does **not** retract block 5's
  association, which is about which seeds benefit, nor §8.13's composition finding. The honest next step would be a
  readout that scores the admitted set rather than the ninety-cycle accumulation, and that would need its own
  calibration -- not a new bar on this one.
- Any gate failure: `VOID / NOT COMPARABLE`, reported as the gate.

## 12. Freeze

Criteria, gates, bar, allocation and decision table are frozen as written. All 300 cells have since been executed and scored exactly once; §13 records the readings and §12 remains the freeze text.
`benchmarks/score_loop_free_block6.py` reads the bar, the band and the allocation from
`docs/gate13_loop_free_block6_calibration.json`. Artifacts: that file, the two dose artifacts, block 5's artifact (bar
provenance), `docs/gate13_c1_respecification.json` (band).

## 13. Readings (2026-11-06, one scoring pass)

300 cells, seeds 20271614-20271713, C, R and Y at cap 20, no cell missing and none substituted.
The bar (0.01), the band and the allocation were read from `docs/gate13_loop_free_block6_calibration.json`; nothing was
adjusted after the run. Scored once by `benchmarks/score_loop_free_block6.py` into
`docs/gate13_loop_free_block6.json`.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, Y vs R | 62/100 seeds with different asserted sets | NO |
| G0b liveness, C vs R | 100/100 seeds with different asserted sets | yes |
| G1 comparability (C1′) | mean control precision 0.4441 in [0.4347, 0.4987] | yes |
| G2 perturbation | 100/100 seeds with at least one edge displaced (required 96) | yes |

**Verdict: VOID / NOT COMPARABLE.** Gate G0 failed: Y and R asserted the same set on 38 seeds, so the intervention did not reach the final structure often enough to compare. Per §6 the gate is reported and **no criterion is read**; the scorer's numbers are in the artifact and are descriptive only. **The gate's bar was not achievable on this distribution, and that is a defect of this block's specification rather than evidence about the arm.** Calibration measured Y-vs-R liveness at 6 of 10 seeds and G0 required 96 of 100, so the same class of error block 4 made -- a threshold the calibrated distribution cannot reach -- was written into a new gate with the calibration number printed beside it. The numbers below are descriptive only and read no criterion: M1's mean 0.0095 sits below its 0.01 bar, so the block would not have passed M1 either, and M2's pass is a mechanism check on data the gate voided.

**The dose finding, stated as part of the result.** The arm was calibrated twice — reordering (X) and reserving the cap
(Y) — and produced identical effects on all ten seeds, because a pool with at least 20 non-loop edges makes the two the
same function. So this block tested the preference at its maximum strength, not at one of several doses; a null here is
a null for the strongest form of the intervention at this readout, not for a weak one.

**Where this leaves the programme.** The moderators are settled: block 3 rejected the loop-count proxy, block 4 was
void, block 5 found an out-of-sample association without a threshold contrast (`DIRECTIONAL ONLY`). This block tested
the intervention those results pointed to. The coverage gain over C moved from 0.0481 for R to
0.0576 for Y, and the mean Y − R difference was 0.0095 with sd
0.0143 — so the intervention adds to R's gain, by
about 19.7505% of it.
The arm's own tally: the preference displaced a mean of 686.86 admitted edges per seed across the
acquisition cycles, on 100 of 100 seeds, and changed the final asserted set on
62.
