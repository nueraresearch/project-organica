# Gate 13 — the loop-free preference arm, block 7 (gate repaired)

**Status: RUN (2026-11-06). Verdict: INTERVENTION SUPPORTED.** The criteria, gates, bar and allocation below were fixed before the first cell, from
artifacts the block does not contain (§4, §5). Readings are appended in §13 with a date; this text is not edited to
match a result.

## 1. What this block changes, and what it does not

Block 6 registered the arm §10 of block 5 named — Y, R with loop-asserted edges sorted last at admission — ran its 300
cells and was **void by its own G0**: Y's asserted set differed from R's on 62 of 100
seeds against a required 96, while the same pre-registration printed the calibration's 6-of-10 liveness beside that
bar. A 96/100 threshold on a 62% event cannot fire; that is block 4's defect in a new gate, and it is recorded in block
6's readings as a specification error rather than a result about the arm.

**Block 7 changes exactly one thing: G0's bar.** The arm, the world, cap 20, the readout, the C1′ band, G2's bar, the
M1 bar and its M2 partner, and the C/R baselines are block 6's, unchanged. The new G0 bar is 50/100,
calibrated to the pooled liveness rate 0.6182 (68 of 110 cells across 110
calibration pairs): the arm must change the final asserted structure on at least half the seeds. That bar is reachable
by construction — under the measured rate G0 itself passes with probability 0.9939 — while the block-6 bar
would have passed with probability 0.0.

## 2. Question

Does removing temporal redundancy from the ratio arm's admission budget raise its coverage? Same question as block 6,
asked with a gate that can be met. The claim under test is causal in the narrow sense only: the arm changes which
candidates the cap is spent on and leaves loops, construction, thresholds and readout untouched.

## 3. What is registered, and what is not

Registered: G0's calibrated bar and the three unchanged gates, M1 and M2 with their bars, the decision table, the
allocation, and the power of M1 at the unchanged bar. Not changed: any frozen engine file, the arm's implementation,
the world generator, the readout, and blocks 2–6's records.

## 4. Allocation and cells

- Seeds **20271715-20271814**, **100 seeds**: the first free 100-seed window after block 6's allocation, by a scan
  of 553 files. Rejected hits inside the candidate range: [20271714].
- Cells: **C, R and Y at cap 20 — 300 cells**, no other cap, no E arm.
- Runner: `benchmarks/run_loop_free_admission_block.py`, unchanged from block 6 and validated against block 2 before
  either block ran (C 90/34/`1a51184e43b546a7`, R 87/34/`129da0ffd2052b85`). Command:
  `PYTHONPATH="$PWD" PYTHONHASHSEED=0 .venv/bin/python benchmarks/run_loop_free_admission_block.py --block 20271715:20271814 --budget 300 --jsonl .scratch/loop_free_block7.jsonl`
- A missing cell is a defect, not a seed to substitute.

## 5. Calibration evidence (110 pairs, none judged here)

Sources: block 6's 100 cells — void by their own gate, so rule 19 permits using them, as block 5 used block 4's void
cells — and the ten dose-calibration seeds. The arm is identical in both, so the pairs are comparable.

- **Liveness** 68/110 = 0.6182: on roughly two seeds in five the intervention changes admission
  and leaves the final asserted set identical to R's, because the asserted structure is a ninety-cycle accumulation.
  G0 therefore tests that the arm *does* reach the structure on at least half the seeds, not that it does so on almost
  all of them.
- **Effect** mean 0.0100, median 0.0000, sd 0.0150, positive on 48 of 110.
  Block 6's own mean was 0.0095, i.e. **below** the unchanged 0.01 bar; that is the honest state of the
  evidence and it is why §8 reports M1's power as low rather than lowering the bar.
- **Mechanism** novel covered edges 1.1 on average (interval [0.8, 1.41818]), loop-covered change
  0.0182 — the same composition block 6 measured.

## 6. Gates (a failed gate voids the block; it is not a negative result)

- **G0 liveness**: Y and R differ on at least **50** of 100 seeds, calibrated to the observed
  rate; power of the gate under that rate 0.9939.
- **G0b liveness of the pair being measured**: C and R differ on at least 96 seeds. Block 6 measured
  100/100.
- **G1 comparability (C1′)**: mean cap-20 control precision in [0.4347, 0.4987]. Block 6 measured 0.4441.
- **G2 perturbation**: the preference displaced at least one admitted edge on at least 96 seeds. Block 6
  measured 100/100. An intervention that displaces nothing has not run.

## 7. Criteria (evaluated once, in this order, by committed code)

- **M1**: `mean(coverage_Y - coverage_R) >= 0.01` **and** the 95% bootstrap interval's lower bound > 0. Unchanged from
  block 6, so the two blocks test the same claim at the same bar.
- **M2**: `mean(covered_novel_Y - covered_novel_R) >= 0.005` with interval above zero, **and** loop-covered
  coverage not lower on average. Unchanged.

## 8. Power, computed in advance — and it is low

Resampling the 110 calibration pairs to 100 seeds, 4,000 replicates per row.

| bar | point criterion | point and interval |
|---|---|---|
| 0.005 | 1.000 | 1.000 |
| 0.0075 | 0.959 | 0.959 |
| 0.01 | 0.487 | 0.487 |
| 0.0125 | 0.051 | 0.051 |
| 0.015 | 0.001 | 0.001 |

**at the unchanged bar 0.01 the pooled mean 0.01 sits -0.01 standard errors from it, so this block is underpowered at M1 and a miss does not distinguish 'no effect' from 'smaller than 0.01'; a pass would be informative.** This is the opposite disclosure from block 6, where the bar sat 2.46 standard errors below the
calibrated mean: here the pooled mean is 0.0100, so at the unchanged bar the block is a coin flip at best. The
bar is **not** lowered, because moving it after block 6's miss would make this block a second attempt at a result
rather than a repair of a gate. The consequence is stated plainly: **a pass is informative, a miss is not evidence
against the intervention**, and the block will say which one it produced.

## 9. Pre-registered predictions

- **P1** G0, G0b, G1 and G2 all pass: the arm reaches the structure on at least half the seeds, the block is
  comparable, and the preference displaces something.
- **P2** M1 lands near the pooled mean 0.0100; whether that clears 0.01 is not predicted, because the two
  estimates straddle it.
- **P3** M2 passes: the gain, if any, is in novel covered edges with loop-covered coverage unchanged.

## 10. What each outcome licenses

- `INTERVENTION SUPPORTED`: the admission budget's redundancy is a cost at this cap and readout, on a fresh allocation,
  with a gate that could fire. It licenses an admission-rule change, not a claim about what loops are for.
- `COVERAGE ONLY`: the arm helps, not through the channel it claims.
- `INTERVENTION NOT SUPPORTED`: at this bar and n the arm does not beat R. Given the disclosed power this is **not**
  evidence of no effect; it is the end of this readout as a test, and a sharper endpoint would need its own block.
- Any gate failure: `VOID / NOT COMPARABLE`, reported as the gate. G0's bar is calibrated, so a G0 failure here would
  mean the liveness rate itself moved between blocks, which is a finding about the arm's reach.

## 11. Freeze

Criteria, gates, bar and allocation are frozen as written. All 300 cells have since been executed and scored exactly once; §13 records the readings and §11 remains the freeze text.
`benchmarks/score_loop_free_block7.py` reads every bar, the band and the allocation from
`docs/gate13_loop_free_block7_calibration.json`. Artifacts: that file, block 6's artifact (void cells and composition),
the two dose artifacts, `docs/gate13_c1_respecification.json`.

## 13. Readings (2026-11-06, one scoring pass)

300 cells, seeds 20271715-20271814, C, R and Y at cap 20, no cell missing and none substituted.
Every bar, the band and the allocation were read from `docs/gate13_loop_free_block7_calibration.json`; nothing was
adjusted after the run. Scored once by `benchmarks/score_loop_free_block7.py` into `docs/gate13_loop_free_block7.json`.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, Y vs R | 72/100 seeds with different asserted sets (bar 50) | yes |
| G0b liveness, C vs R | 100/100 seeds with different asserted sets (bar 96) | yes |
| G1 comparability (C1′) | mean control precision 0.4427 in [0.4347, 0.4987] | yes |
| G2 perturbation | 100/100 seeds with an edge displaced (bar 96) | yes |

**Verdict: INTERVENTION SUPPORTED.** All four gates pass. **M1** passes: mean Y − R coverage 0.0127, 95% interval [0.0092, 0.01652], against the 0.01 bar (median 0.0089, 53/100 seeds positive). **M2** passes: novel covered edges +1.4 on average (interval [0.98, 1.8], bar 0.005), loop-covered change +0.05.

The admission budget's redundancy is a **cost** at this cap and readout, now measured on a fresh allocation with a gate that could fire. The gain sits where the arm claims -- novel edges with loop-covered coverage unchanged. It licenses an admission-rule change; it does not say what loops are for, because the arm removes prediction candidates whose edges loops assert and leaves the loops themselves untouched.

**What this block settled about block 6.** Block 6's void was a gate that could not fire: it required 96 of 100 seeds
where the calibration measured 62 of 110. With G0 at 50 the arm is testable, and the liveness it delivered here
was 72/100 — consistent with the 0.6182 pooled rate, so the gate is now
measuring the arm's reach rather than failing on arithmetic.

**Where this leaves the programme.** Six blocks have now tested the control-side claim: block 3 rejected the loop-count
proxy, block 4 was void by measurability, block 5 found an out-of-sample association without a threshold contrast, block
6 registered the intervention and voided on an unreachable gate, and block 7 ran it with a calibrated gate. Coverage
over C moved from 0.0466 for R to 0.0593 for Y, a mean Y − R of
0.0127 (sd 0.0187), and the preference displaced a mean of 685.34 admitted edges
per seed.
