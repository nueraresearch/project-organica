# Gate 13, block 8 — does the loop-free admission gain scale with the cap?

**Status: RUN (2026-11-06). Verdict: SCALING SUPPORTED.** The criteria, gates, bar and allocation below were written before any judged cell was run.
Nothing here may be changed after the run; the readings are appended as §13 and any defect is disclosed there rather
than repaired.

## 1. Question

Block 7 measured the loop-free arm's gain at cap 20: mean Y − R coverage **0.0366** on fresh
seeds, M1 and M2 both passing. The gain is a statement about *how a fixed budget is spent*: Y withholds prediction
candidates whose edges loops already assert, so the twenty slots go to non-redundant edges. If that mechanism is what
produces the gain, the gain should **grow with the budget**, because a larger cap widens the pool from which the loop
edges would otherwise be drawn and leaves more non-redundant edges to admit. If the gain is an artifact of the cap-20
pool — for instance, a fixed set of loop edges crowding a small budget — it should not grow, and may vanish.

This block tests the scaling prediction directly, on two larger caps, with the same arm and world.

## 2. Design — caps 40 and 100, arms R and Y, fresh seeds

- **Arms:** R (no intervention) and Y (loop-asserted edges sorted last at admission, cap reservation). Arm C is not run:
  the claim is Y versus R, and the comparability question is whether the cap axis itself is live, which this block's own
  R cells answer.
- **Caps:** 40 and 100.
- **Seeds:** the frozen window **20271826–20271925**, 100 seeds, 400 cells (2 arms × 2 caps × 100 seeds).
- **World, readout, cycles:** unchanged from blocks 6 and 7.
- **Arm code:** `benchmarks/run_loop_free_admission_block.py`, `--caps 40,100`; the cap-20 self-test was re-run after the
  extension and reproduced block 7's cap-20 cell exactly (`20271816` and the frozen window were
  checked; the self-test at 20270901 still passes).

## 3. What is measured

Per seed and cap: coverage of the world's asserted edges, precision, novel and loop-covered coverage, displacement of the
previous cycle's asserted set by this cycle's, and whether R's and Y's final asserted sets differ (the liveness gate).

The **scaling quantity** is the difference-in-differences

    DiD(seed) = [Y − R coverage at cap 100] − [Y − R coverage at cap 40]

which is a paired, per-seed number: both gains come from the same seed, so the world's difficulty cancels.

## 4. Gates (all must pass, or the block is void)

| Gate | Requirement | Why |
| --- | --- | --- |
| G0 liveness, both caps | Y and R final asserted sets differ on at least **50/100** seeds **at each cap** | an arm that changes nothing is not measurable |
| G1 perturbation, both caps | at least **96/100** seeds displaced at each cap | the readout must be alive |
| G2 axis live | mean R coverage at cap 100 > at cap 40, bootstrap interval above zero | otherwise the cap axis changes nothing and no scaling claim can be read (rule 13c) |

Calibration measured liveness **8/10** at cap 40 and **10/10**
at cap 100; displacement mean **1230.10** and **2168.20** cells.

## 5. M1 — the scaling criterion

**Mean DiD ≥ 0.01**, with the 95% bootstrap interval's lower bound above zero.

The bar is the one blocks 6 and 7 applied to the gain itself: one fifth of R's gain over C at cap 20 (0.0485). Here it
applies to the **change** in the gain between caps 40 and 100, so the claim is that the larger budget adds at least a
block-7-sized gain on top of the smaller one. Calibration measured a mean DiD of **0.0223** (sd
0.0216, 9/10 seeds positive).

## 6. M2 — the gain must exist at both caps

Mean Y − R > 0 at **each** cap, with the interval's lower bound above zero.

Without M2, M1 could pass through a *negative* gain at cap 40 — a loss that becomes a smaller loss, not a scaling
effect. Requiring both gains positive makes the scaling claim conditional on the arm working at both budgets.

## 7. Decision table, fixed in advance

| M1 | M2 | Verdict | Reading |
| --- | --- | --- | --- |
| pass | pass | **SCALING SUPPORTED** | the gain grows with the budget, and is positive at both |
| pass | fail | **SCALE-DEPENDENT** | the gain appears or reverses at one budget; not scaling |
| fail | pass | **GAIN WITHOUT SCALING** | the arm helps at both caps, by a similar amount |
| fail | fail | **NO GAIN AT THESE CAPS** | the cap-20 result does not extend to larger budgets |

A gate failure voids the block: **VOID / NOT COMPARABLE**, reported as the gate and not as a verdict.

## 8. Power, computed in advance

Ten calibration seeds at each cap, resampled to 100 seeds, 4,000 replicates per row.

| bar | point criterion | point and interval |
|---|---|---|
| 0.005 | 1.000 | 1.000 |
| 0.01 | 1.000 | 1.000 |
| 0.015 | 1.000 | 1.000 |
| 0.02 | 0.873 | 0.873 |

The DiD is a noisier quantity than either gain, because it differences two paired differences, so the power figures are
estimates from ten seeds and are reported as such. Calibration: gain at cap 40 **0.0143** (interval
0.0027 to 0.0285), at cap 100 **0.0366** (interval 0.0214 to
0.0518), DiD **0.0223** (interval 0.0098 to 0.0348).

## 9. Pre-registered predictions

1. **P1 (primary).** M1 passes: the gain at cap 100 exceeds the gain at cap 40 by at least 0.01, interval above zero.
2. **P2.** M2 passes: the gain is positive at both caps.
3. **P3.** The novel-edge channel carries the scaling: the change in novel covered edges between caps is larger for Y than
   for R, and the loop-covered difference does not turn negative.
4. **P4.** R's own coverage rises with the cap (G2), so the axis is live.

## 10. What this block cannot say

- It measures coverage of one world family's asserted edges at two caps, at this readout. A scaling result is a statement
  about **where the arm's benefit comes from**, not a general claim that larger budgets always help.
- Two caps test a difference, not a shape: a monotone curve needs more points, and the cap-20 point comes from block 7 on
  different seeds and is reported as context only, never pooled into this block's criteria.
- Nothing here changes the loops themselves; the arm only changes which candidates are admitted.

## 11. Artifacts

`docs/gate13_loop_free_cap_calibration.json` (this pre-registration's source), `benchmarks/score_loop_free_cap.py`
(scoring, run once), `docs/gate13_loop_free_cap.json` (readings). Capacity record §8.19; manual paragraph and revision
row; changelog section.

## 13. Readings (2026-11-06, one scoring pass)

400 cells, seeds 20271826-20271925, R and Y at caps 40, 100, no cell missing and none
substituted. Every bar, gate and the allocation were read from `docs/gate13_loop_free_cap_calibration.json`; nothing was
adjusted after the run. Scored once by `benchmarks/score_loop_free_cap.py` into `docs/gate13_loop_free_cap.json`.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, both caps | 86/100 and 100/100 seeds with different asserted sets (bar 50) | yes |
| G1 perturbation, both caps | 100/100 and 100/100 seeds with an edge displaced (bar 96) | yes |
| G2 axis live | R coverage 0.6898 at cap 40 to 0.7840 at cap 100; lift 0.0942 (interval 0.0867 to 0.1023) | yes |

**Verdict: SCALING SUPPORTED.** All three gates pass. **M1** passes: mean
difference-in-differences 0.0240 (95% interval 0.0196 to 0.0285)
against the 0.0100 bar, median 0.0268 and 81/100 seeds
positive. **M2** passes: cap 40: 0.0179 (interval 0.0144 to 0.0218), cap 100: 0.0420 (interval 0.0369 to 0.0472).

The two gains, which are what the DiD is built from: cap 40 mean Y − R 0.0179, cap 100
0.0420. Calibration had predicted 0.0143 and 0.0366
respectively. Novel covered edges moved +1.98 at cap 40 and
+4.59 at cap 100, loop-covered edges +0.030 and
+0.110. Mean displacement 1151.18 and
2125.08 cells.

The gain grows with the budget and is positive at both caps: the mechanism the arm claims -- spending admission slots on edges loops do not already assert -- is the one that produces the effect, because the effect grows when the pool of redundant edges does.

**Disclosed defect.** The launcher for this run omitted the arm selector, so arm C also executed alongside R and Y. C is outside this block's frozen design, which runs R and Y only; its cells are excluded from scoring, moved to `.scratch/loop_free_cap_unregistered_C.jsonl`, and reported as unregistered rather than judged. The scored grid is exactly the 400 registered cells and no C number enters any criterion.

This licenses a statement about the admission rule at these two budgets on this world family and readout; it is not a
statement about what loops are for, because the arm leaves the loops, their construction and their thresholds untouched.
