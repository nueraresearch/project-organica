# What the 448-cell null rules out (2026-11-07, revised 2026-11-07)

**Status: a scope characterization, not a verdict and not a re-scoring.** The verdict
stays `docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md` §18: the calibration
returned no usable threshold and the campaign stopped. This document asks how wide
that statement is. Counts are recomputed from the harness constants; the per-cell
rejections are the owner's verified readings of the sealed artifact, which is not
in this worktree. Everything is in `docs/decay_null_scope.json`.

## 1. What actually ran

| quantity | value |
|---|---|
| cells | **448** = 7 thresholds x 4 degrees x 8 seeds x 2 arms |
| cells per arm per threshold | **32** |
| thresholds | 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3 |
| degrees (measured hub out-degree) | 2, 4, 6, 12 |
| calibration block | 20300101-20300108 (8 seeds) |
| cycles per cell | 300 |
| precision floor | 0.95 |

The shipped arm is fixed at 0.30 and contributes no cells, which is why the total
is **448** and not 672.

## 2. The null, stated exactly

For each calibrated arm there is **no threshold in the tested grid** that is
simultaneously live on all **32** cells *and* holds precision at or above
**0.95** on all 32. Liveness is the harness's own gate: at least
one theory in every one of the final 10% of cycles, and a tail mean of at least
two beliefs. That is a conjunction over cells at one horizon on one world family.

## 3. Sensitivity to the selection rule: none for the transition arm

The rule has no slack: a cell that fails liveness rejects the threshold, a cell
whose precision is `None` rejects it, coverage only breaks ties. The verified
pattern rejects **every** tested threshold for the transition arm:

* **0.05, 0.075, 0.10** — precision at degrees 4 and 6;
* **0.15, 0.20** — liveness at degree 12;
* **0.25, 0.30** — liveness at degrees 6 and 12.

So for that arm **no selection rule that keeps both per-cell gates could have
selected anything**, whatever it did with coverage or tie-breaks. A rule that
selects must weaken or drop a gate — pooled precision, a fraction of cells, a
lower floor — and that is a different question with a different bar.

The ratio arm is a different story, and a sharper one: at **0.20 and above its
precision is `None` in every cell because it forms no stable predictions at all**.
That is rejection for asserting nothing, not for asserting wrongly — see §5.

## 4. Sensitivity to grid resolution: decisive, and previously understated

The largest threshold with no reported liveness failure is **0.1**; the
smallest with no reported precision failure is **0.15**. The sets are disjoint
and *adjacent*, but they fail for **opposite reasons** — 0.1 is live and
imprecise, 0.15 is precise and dead. That is the one arrangement in which grid
resolution matters: a single global threshold that satisfies both must lie in
**(0.1, 0.15)**, an untested interval **one grid step wide**
(**0.05**, midpoint
**0.125**).

Whether one exists there is not a formality. Under monotone gates — precision
non-decreasing in the threshold, liveness non-increasing — a both-satisfying value
exists exactly when the precision crossing precedes the liveness crossing inside
that interval. The grid cannot distinguish those two cases, and they have opposite
implications: the first makes the null a **resolution artifact**, the second makes
it structural.

Because a threshold is compared against a strength that is a ratio of integer
counts (`count / out_counts[source]`, `count / source_frequency`), the map from
threshold to behaviour is **piecewise constant**. So the question has an exact
form: *does a realised strength lie inside (0.1, 0.15) at which degrees 4
and 6 clear 0.95 and degree 12 stays live?* A refinement at the grid's own step
would test 0.125, 0.15, 0.175.
The per-cell strengths are in the sealed artifact; they are not in this worktree,
so this stays open here.

## 5. The precision gate rejects two different things

§7.3 requires 40 stable edges before quoting a precision, because a ratio over a
handful of edges is not an estimate. The **calibration** rule has no such floor:
one stable edge scores 1.0 or 0.0, and no stable edges scores `None` and is
rejected. So "failed the precision floor" covers both *wrong edges* and *no
edges*, and the ratio arm's high end is entirely the second case.

This is not a technicality. A threshold rejected for asserting nothing is closer
to a liveness failure than to a dishonesty failure, and the difference decides
whether the conflict is two gates binding on different degrees or one gate that
never gets off the ground at the top of the range.

## 6. What this null does not rule out

* **A single global threshold in (0.1, 0.15)** — the one value the grid
  cannot speak about.
* **A per-degree threshold.** §3 put it out of scope; out of scope is not refuted.
* **A degree-aware rule, or another strength normalisation** — untested.
* **Weaker gates**: a 0.90 floor, or precision pooled rather than per-cell.
* **Other worlds, seeds, degrees, horizons.** One ladder at
  2, 4, 6, 12 for 300 cycles.
* **The held-out stage and the task endpoint.** Neither exists.
* **The mechanism.** Both formulas failed the same gate; neither is individually
  refuted.

## 7. What is not licensed

> "No threshold works, so threshold tuning is hopeless."

The tested set is 7 values, and the only place a single global threshold
could still work is an interval the grid skipped. The licensed sentence is: *on
the committed grid, no global threshold cleared both per-cell gates for either
calibrated arm, so no held-out cell was run; the interval (0.1, 0.15) is
untested and decides whether that null is structural or a resolution artifact.*

## 8. Correction (2026-11-07)

An earlier version of this record placed the untested interval at (0.15, 0.20).
That was wrong: it rested on §18's summary, which located the transition precision
boundary at 0.20 and did not report the degree-12 liveness rejection already at
0.15. With the verified readings the interval is (0.1, 0.15), one grid
step wide instead of two, and the resolution risk is larger rather than smaller.
The verdict is unchanged: no qualifying threshold on the grid, no held-out cell,
nothing adopted.
