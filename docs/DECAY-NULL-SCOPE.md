# What the 448-cell null rules out (2026-11-07)

**Status: a scope characterization, not a verdict and not a re-scoring.** The
verdict stays `docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md` §18: the
calibration returned no usable threshold and the campaign stopped. This document
asks a narrower question — *how wide is that statement?* — and answers it from
the protocol text, the harness constants and §18's reported rejections. Every
number below is in `docs/decay_null_scope.json`; nothing here re-reads a cell.

## 1. What actually ran

| quantity | value |
|---|---|
| cells | 448 = 7 thresholds x 4 degrees x 8 seeds x 2 arms |
| cells per arm per threshold | 32 |
| thresholds | 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3 |
| degrees (measured hub out-degree) | 2, 4, 6, 12 |
| calibration seeds | 20300101-20300108 (8) |
| cycles per cell | 300 |
| precision floor | 0.95 |

The shipped arm is not calibrated: it runs at a fixed 0.30. The two calibrated
arms are the ratio control and the transition arm, which is why the cell count is
**448** and not 672.

## 2. The null, stated exactly

For each of the two calibrated arms, there is **no threshold in the tested grid**
that is simultaneously live on all 32 cells *and* holds
precision at or above 0.95 on all 32
cells. Liveness is the harness's own gate: at least one theory in every one of
the final 10% of cycles, and a tail mean of at least two beliefs.

So what the null establishes is a **conjunction over cells at a fixed horizon on
one world family**: one global threshold cannot satisfy both gates across the
ladder. It establishes nothing about either formula's merit, because the
comparison that would have tested the formulas was never reached.

## 3. Sensitivity to the selection rule

The rule is a conjunction with no slack: a cell that fails liveness rejects the
threshold, and a cell whose precision is `None` — **no stable edges at all** —
rejects it too. Coverage only breaks ties among survivors.

For the transition arm, §18's reported pattern rejects every tested threshold:

* `0.05`, `0.075`, `0.1`, `0.15` — precision at degree 4;
* `0.2` — liveness at degree 12;
* the two above it — liveness at degrees 6 and 12.

The largest threshold with no reported liveness failure is **0.15**; the
smallest with no reported precision failure is **0.2**. Their intersection
is **empty**. Therefore **no selection rule that keeps both per-cell gates could
have selected anything** for that arm: the failure is not an artifact of the
conjunction, the coverage tie-break, or the choice of "highest mean coverage".
A rule that does select something must weaken or drop a gate — pooled precision,
a fraction of cells, a lower floor — and that is a different question with a
different bar, not a re-reading of this one.

For the **ratio control** the same argument cannot be made: §18 records only that
it selected nothing, not which cells rejected which threshold. The per-cell
pattern for that arm is unresolved here.

## 4. Sensitivity to grid resolution

The map from threshold to behaviour is **piecewise constant**, because a
threshold is compared against a strength that is a ratio of integer counts —
`count / out_counts[source]` for the transition arm, `count / source_frequency`
for the ratio arm. Two thresholds that fall between the same pair of realised
strengths produce identical cells. Grid resolution therefore matters only where
a realised strength lies in an untested interval.

On the reported pattern there is exactly **one** such interval: **(0.15,
0.2)**, width **0.05**,
midpoint **0.175**. Elsewhere the grid is already
decisive: below 0.15 precision fails at degree 4, and at and above 0.2
liveness fails at degree 12. A finer grid inside that interval could only help if
precision is **non-monotone** in the threshold there — that is, if some value
admits a strength plateau that 0.15 excludes while keeping precision at
degree 4 and liveness at degree 12. The grid's own smallest step is
**0.025**, so a refinement at that step would test
the midpoint.

Whether such a plateau exists is **not decidable from this worktree**. It is
decided by the sealed artifact: the distinct strengths recorded per cell, and
`choices[arm].rejected` per threshold. If no realised strength falls inside the
interval, refinement is guaranteed to change nothing; if one does, refinement is
a new calibration — with fresh seeds, per `docs/DECAY-TUNING-CYCLE.md` — not a
re-reading of this one.

## 5. The gate is stricter than the adoption gate, in one respect

§7.3 requires 40 stable edges before quoting a precision, precisely because a
ratio over a handful of edges is not an estimate. The **calibration** rule has no
such floor: a cell with one stable edge scores 1.0 or 0.0, and a cell with none
scores `None` and is rejected. So §18's phrase "failed the precision floor" can
mean either *asserted the wrong edges* or *asserted nothing*, and the summary does
not separate them. The artifact does: `rejected` renders the two as a number
versus `None`. This distinction matters, because a threshold rejected for
asserting nothing is closer to a liveness failure than to a dishonesty failure,
and the difference decides whether the conflict is "two gates bind at opposite
ends" or "the low end never got off the ground".

## 6. What this null does not rule out

* **A per-degree threshold.** §3 put it out of scope; out of scope is not
  refuted. Selecting one now would be a threshold chosen from the data that
  rejected it.
* **A degree-aware or otherwise non-constant rule**, or a different strength
  normalisation — untested.
* **Weaker gates.** A 0.90 floor, or precision pooled across cells rather than
  required in every cell, is a different claim.
* **Other worlds, seeds, degrees and horizons.** The design is one ladder of
  synthetic worlds at 2, 4, 6, 12 for 300 cycles,
  with 8 seeds.
* **The held-out stage and the task endpoint.** No held-out cell exists; nothing
  was scored on held-out seeds; the task comparison was never made.
* **The mechanism.** Both formulas failed the same calibration gate, so "Option
  2r does not help" is not a supported reading either. What is supported is that
  the *one-threshold* design does not clear this ladder.

## 7. The sentence that is not licensed

> "No threshold works, so threshold tuning is hopeless."

Neither half follows. The tested set is 7 values, the gate is a
per-cell conjunction at one horizon, and the artefact that would show whether an
untested value sits on a distinct strength plateau is not in this worktree. The
licensed sentence is: *on the committed grid, no global threshold cleared both
per-cell gates for either calibrated arm, so no held-out cell was run; the
interval (0.15, 0.2) is untested and its resolution is undetermined.*
