# A1 C7/C8 denominator unit — adopted decision

**ID:** `A1-C7-C8-DENOMINATOR-1`

**Date:** 2026-11-14

**Status:** `ADOPTED — BINDING FOR A1; C7 PER-EDGE RATE; C8 N=20 DESIGN REGISTERED, NOT FROZEN`

**Decision owner:** owner direction, 2026-11-14.

**This is a design-unit decision, not a result, freeze, grant or run.** No A1 cell has run, no seed is reserved and no target is frozen. It changes no threshold: C7 remains a **0.05** absolute A-formation and K-formation margin, and C8 remains a **0.05** assertion ceiling.

## 1. The mismatch this decision resolves

The implemented readiness contracts pooled C7 and C8 rows across all seeds before applying the same thresholds. That is the wrong evaluation unit for both gates, but the two gates do not have the same denominator:

- **C7** is an A/K **formation-rate difference** on each Y− edge against that edge's paired `A+K+` control. Each edge is read over **120 cycles**, so the smallest nonzero rate change is `1/120 = 0.008333`. The `2N` Y− rows per seed (two Y− cells × N targets) establish cell completeness and the assertion-order check; they are **not** the denominator for the 0.05 rate margin.
- **C8** is an assertion **proportion** over the `N` `A−K−` target rows in a seed, so the smallest nonzero change is `1/N`.

The original denominator audit treated C7's 0.05 margin as a proportion over the `2N` Y− rows. That was a category error: it made C7 look under-resolved at eight rows when the gate's margin is a per-edge rate over 120 cycles. This record corrects that reading before any freeze. The C8 row denominator is correct and unchanged.

Pooling is rejected for both gates. A pooled C8 rate can pass while one seed fails; a pooled C7 rate can average a failing seed's per-edge A/K difference into a passing one. The fact that C7's 0.05 margin uses cycles rather than rows does not license pooling across seeds.

## 2. Decision

**C7 and C8 are evaluated per seed. Rows are not pooled across seeds; there is no averaging, no best-seed reading and no post-hoc denominator expansion.**

1. **C7 — per seed and per edge.** Every seed must have a paired `A+K+` control and both Y− cells. On that seed, Y− must lower assertion, and every Y− edge's absolute A and K formation-rate difference from its paired `A+K+` edge must be at most **0.05**. The rate denominator is the **120 cycles** on that edge, so the step is `1/120 = 0.008333`. A missing Y− cell, paired edge, or rate is **NOT MEASURABLE**, not a pass. The `2N` Y− rows remain required for cell completeness and the assertion-order check, but they do not set the 0.05 rate resolution.
2. **C8 — per seed, per target row.** Every seed must have an `A−K−` cell. That seed's assertion rate over its `N` target rows must be at most **0.05**. The step is `1/N`. If any one seed's rate is above 0.05, the result is **`THIRD ROUTE PRESENT`** for that seed, regardless of the pooled rate.
3. **Denominator units.** C7: **per seed, per edge rate over 120 cycles**; C8: **per seed, per target row**. C7 does not need 20 rows; C8 does.
4. **No pooled rescue.** A pooled calculation is not an alternative reading of either gate. It is rejected because it changes the unit of the claim. The pooled C8 count at N=4 is 24 rows; one seed at `1/4 = 0.25` would appear as `1/24 = 0.041667` and pass, hiding the per-seed third route the control exists to detect.

**Implementation note.** The target rows now carry `A_cycles`, `K_cycles`, `Y_cycles` and the corresponding `A_rate`, `K_rate`, `Y_rate`, matching the non-target stream. `gate_c7` uses `delta_from_baseline` when it is supplied and otherwise computes each Y− edge's absolute A/K rate difference against that seed's paired `A+K+` edge. Without the target rates, the per-seed C7 contract could not read a real cell.

## 3. Consequence for the current design

At the registered **N = 4** target block:

| Gate | Rows per seed | Rate/row step | 0.05 margin | Resolution |
| --- | ---: | ---: | ---: | --- |
| `C7_assertion_block` | 8 Y− rows for completeness/order; 120 cycles per edge | 0.008333 | 0.05 | **RESOLVED** |
| `C8_third_route` | 4 A−K− target rows | 0.250000 | 0.05 | **FLAGGED** |

At the maximum feasible disjoint block, **N = 8** (all 16 tag vertices):

| Gate | Rows per seed | Rate/row step | 0.05 margin | Resolution |
| --- | ---: | ---: | ---: | --- |
| `C7_assertion_block` | 16 Y− rows for completeness/order; 120 cycles per edge | 0.008333 | 0.05 | **RESOLVED** |
| `C8_third_route` | 8 A−K− target rows | 0.125000 | 0.05 | **FLAGGED** |

C7's rate margin is already resolved at one target edge per seed; the 120-cycle denominator, not `N`, sets its step. C8 needs at least **20 rows per seed** (N ≥ 20) for a one-step resolution at 0.05, above the 16-vertex, eight-disjoint-target maximum. The current design therefore **cannot adjudicate C8 at the precommitted margin on a per-seed basis**. C7 is resolvable by design but remains unrun.

A separate **N=20 C8 expansion design** is now registered in [`A1-C8-EXPANSION.md`](A1-C8-EXPANSION.md). It permits limited endpoint overlap, caps each tag at three selected targets, and supplies 20 A−K− rows per seed. Its step is `1/20 = 0.05`, so it resolves C8 **if adopted and frozen**. It is not the live manifest and is not frozen.

| Gate | Registered N=20 | Step | Resolution |
| --- | ---: | ---: | --- |
| `C8_third_route` | 20 A−K− rows per seed | 0.050000 | **RESOLVED BY REGISTERED DESIGN IF ADOPTED** |
| `C7_assertion_block` | 40 Y− rows per seed; per-edge rate unchanged | 0.008333 | **RESOLVED PER EDGE** |

This is a design blocker for the current N=4/N=8 block only, not a reason to change the threshold after seeing an outcome. The registered N=20 design is the resolution path if C8 adjudication is required; adopting it requires a separate target-freeze act. If the owner does not adopt it, the current run may proceed only with C8 explicitly recorded as **not adjudicated by design**, and that limitation must appear before any result.

The pooled counts at N=4 would be 48 C7 rows and 24 C8 rows. The 48-row C7 count is not a rate denominator at all; the 24-row C8 count is recorded only to identify the rejected reading. Neither is an A1 denominator, and neither can be used to pass a gate.

## 4. What this decision does not do

- It does not change the C7 or C8 thresholds.
- It does not freeze targets, reserve seeds, issue a grant or run a cell.
- It does not change C1 or C4, the 60-row C1 floor or the C1/C4 VOID gate.
- It does not measure C7 or C8.
- It does not license a post-outcome change to the target block, the unit or the margin.

## 5. Effect on freeze readiness

The target freeze remains **NOT AUTHORISED**. The current N=4 design cannot resolve C8 per seed, so it is not a complete A1 design for a two-path adjudication. The N=20 design is registered and would resolve C8 if adopted, but registration is not adoption: the existing target sets are still draft, the manifest is still unfrozen, the grant is still absent and the run has not started. C7 is resolvable by design but is still an unrun gate.

The separate C1 denominator-feasibility question is unchanged: the planned 63–64 C1 rows are unobserved, and the existing C6/Q4 availability proxies are a pre-freeze warning, not an A1 denominator.

## 6. Related records

| Record | Relationship |
| --- | --- |
| [`A1-DENOMINATOR-RESOLUTION.md`](A1-DENOMINATOR-RESOLUTION.md) | Uses this per-seed unit; C7 is rate-resolved, C8 is flagged |
| [`A1-GATE-READINESS.md`](A1-GATE-READINESS.md) | C7/C8 contracts require every seed to pass on its own rows |
| [`A1-PRECOMMITTED-THRESHOLDS.md`](A1-PRECOMMITTED-THRESHOLDS.md) | Thresholds unchanged; C7/C8 definitions marked per seed |
| [`A1-PRE-FREEZE-CHECKLIST.md`](A1-PRE-FREEZE-CHECKLIST.md) | Freeze readiness remains open; C8 under-resolved |
| [`A1-PROTOCOL-COMPLIANCE-REPORT.md`](A1-PROTOCOL-COMPLIANCE-REPORT.md) | Reports the same blocker without changing P0 |
| [`A1-C8-EXPANSION.md`](A1-C8-EXPANSION.md) | Registered N=20 design that resolves C8 if adopted; not frozen |
| [`A1-C1-C4-VOID-GATE.md`](A1-C1-C4-VOID-GATE.md) | Separate C1/C4 validity gate; C7/C8 are not adjudicated when that gate voids |

**Not evidence:** A denominator-unit decision and a design-feasibility statement. No cell has run, no target is frozen, no seed is reserved and no C7/C8 measurement exists.
