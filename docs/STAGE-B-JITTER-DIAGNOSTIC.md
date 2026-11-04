# Stage B: how large is the hash-order jitter's effect?

**Status: defined and committed unrun, 2026-11-04.** Every number in §2 is computed from the committed
assembly and costs no engine run; §3 defines the run that would answer the question; §4 says what an answer
would and would not cover. No cell has been re-executed for this document, and nothing here re-scores the
block's verdict.

## 1. The question the four-cell check left open

The reproduction check (`docs/stage_b_rerun_check.json`, journal §187) established that the engine's
cycle-level output depends on the process's string-hash order, and that the dependence changed no cell's
score or eligibility in a sample of four. It could not say how much the effect matters for the block as a
whole, and four cells cannot: the per-configuration statistic rests on 587 eligible
worlds out of the 671 that produced an onset, and a
shift of a few cycles matters only to the cells that sit close to their own clock.

Three quantities can move, in descending order of how much they would matter:

1. **Displacement.** A cell's onset moves by some number of cycles when the hash order changes.
2. **Eligibility.** A cell's eligibility changes only if its onset sits within that displacement of its
   clock, `horizon - 101`. A cell that flips enters or leaves the scored set, which changes a denominator
   and not only a point.
3. **Score.** A cell's outcome changes, or does not. In the four-cell sample it did not, to six decimals.

Only the second can change a verdict without changing any measurement, so the diagnostic is built around it.

## 2. Exposure, measured from the assembly (no engine run)

The band is the largest displacement actually observed in the reproduction check: **10** cycles. A cell
outside it cannot flip under a shift no larger than anything seen so far -- and §3.6 tests that ceiling
instead of assuming it.

| configuration | clock | cells | censored | within 10 cycles of the clock | ineligible but reachable | eligible but reachable |
| --- | --- | --- | --- | --- | --- | --- |
| `2:1` | 539 | 180 | 49 | 38 | 26 | 12 |
| `3:1` | 404 | 180 | 0 | 0 | 0 | 0 |
| `4:1` | 362 | 180 | 0 | 0 | 0 | 0 |
| `6:1` | 329 | 180 | 0 | 0 | 0 | 0 |

Read as exposure, not as effect: 38 of the 671 cells that produced an onset sit close
enough to their clock that a shift of the observed size could move their eligibility, and every one of them is
enumerated below rather than sampled. The other 633 cells with an onset cannot flip
unless a displacement larger than 10 cycles appears, which is what the control in §3.6 would catch. The
49 censored cells are a separate case: with no onset there is no distance to the clock, so the
band argument does not bound them at all. They sit inside the strided sample, and a censored cell that
produced an onset in a redraw is reported as a flip rather than absorbed.

## 3. The design

### 3.1 Population and sample

Two parts, both fixed before any run:

- **Enumerate the band.** All 38 cells with `abs(onset - clock) <= 10` are re-run, so the
  flip count inside the band is exact for the band and is not an estimate.
- **Sample the rest by position.** Every 20th seed of each configuration's block, in seed order
  (`2:1`, `3:1`, `4:1`, `6:1` blocks, 36 strided cells in total), of
  which 33 lie outside the band. The rule is positional and outcome-independent: it cannot select
  cells that look jitter-prone, because it never looks at an onset to choose.

The strided sample estimates the displacement distribution across the block, including the tail the band
assumption ignores. The enumeration answers the eligibility question where it can be answered exactly.

### 3.2 Redraws

`PYTHONHASHSEED` takes each value in 0, 1, 2, one run per cell per value, on this machine. Three
redraws are enough to test the band and to see whether a flip happens at all; they are not enough to
estimate a flip *rate*, and the document does not.

### 3.3 What is recorded

Per run: the cell's onset, eligibility, outcome, `cycles_run`, the trajectory hash and the cycles at which
the trajectory differs from the committed one -- the same fields the four-cell check recorded, so the two
artifacts are comparable cell by cell. Each run writes to its own cache path, because two runs of one
configuration and seed share a SQLite path and corrupt each other.

### 3.4 The estimator

- **Displacement.** Per cell, the largest absolute onset difference across the redraws, reported as a
  distribution over the strided sample: median, maximum, and how many cells moved at all.
- **Eligibility.** Exact inside the band: the number of cells whose eligibility differs in any redraw.
- **Aggregate.** If the band shows no flip, the effect on eligibility is exactly zero inside the band and
  zero outside it under the displacement ceiling -- stated at that width, not as "no effect".
- **Sensitivity of the statistic.** If a cell flips, the per-configuration analysis in
  `docs/stage_b_results.md` §2 is recomputed under the flipped eligibility and both results are reported side
  by side: the recorded one and the sensitive one.

### 3.5 Cost

213 cell-runs, about 111,363 cycles -- 3 redraws of 71 distinct
cells. That is a bounded, declared cost, and it is not a re-run of the block, which would be 720
cells and 330,120 cycles to reproduce.

### 3.6 Pre-committed readings, and the control that can void them

- **R1, stable.** No band cell changes eligibility in any redraw, and no sampled cell's displacement exceeds
  10. Then the block's eligibility is invariant to hash order within the measured band and the jitter
  changes no denominator. That is a statement about `v0.9.0` on this block, not about the engine in general.
- **R2, unstable.** Some band cell flips. Then the flip set is reported by configuration, the analysis is
  recomputed under it, and the verdict is *not* re-scored: the block is reported as sensitive to hash order
  to that degree, and §D15's boundary is what keeps the recorded result intact.
- **R3, void.** Any sampled cell moves more than 10 cycles. Then the band was too narrow, the
  enumeration was incomplete, and **no conclusion is drawn** -- the diagnostic is redesigned around the new
  ceiling before it is read. A diagnostic whose coverage condition cannot fail would be decoration.

R3 is what makes R1 mean something. It fires only if the tail is wider than the four-cell sample suggested,
and the strided sample spans all four configurations, so it is cheap to test.

## 4. What it would and would not establish

- It would bound how much of this block's recorded result depends on the process's hash order, and it would
  name the cells where that dependence is live.
- It would not re-run the block, would not change the assembly, and would not touch the `NOT SUPPORTED`
  verdict.
- It would not license regenerating the block under a tie-broken engine: that is a different instrument and a
  different study (§D15).
- It would say nothing about other engines, other world families or other arms, and it measures the
  *instrument's* sensitivity rather than a property of the organism.
- Three redraws bound the presence of an effect, not its rate. A rate would cost more redraws than the
  question is worth.

## 5. Provenance

- Eligibility rule and the clock: §D14; `horizon - 101` is the planned confirmation cycle, and that identity
  is re-checked against every non-censored cell in the assembly when this document is generated.
- Displacement ceiling: the largest absolute onset difference in `docs/stage_b_rerun_check.json`.
- Cells, cycles and horizons: `docs/stage_b_runner.json`.
- The finding this measures: journal §187; `docs/stage_b_results.md` §4; §D15 for the boundary it keeps.
