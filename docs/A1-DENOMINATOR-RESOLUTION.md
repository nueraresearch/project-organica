# A1 denominator-resolution audit

**Date:** 2026-11-14
**Status:** `FLAGGED — 4 GATE SCENARIO(S) FINER THAN PLANNED DENOMINATOR`

**This is not an A1 result.** No cell was run; the observed denominators are still unknown.

For a proportion over n rows, the smallest nonzero change is 1/n. For a floor threshold t, the margin is 1-t; for a ceiling threshold t, the margin is t. A gate is FLAGGED when 1/n is greater than its margin; equality is not finer. C8 uses each seed's own A-K- rows. C7's 0.05 margin is an A/K rate difference over the 120 cycles on each paired target edge, not over the 2N Y- rows.

## Denominator unit

**ADOPTED — BINDING FOR A1 (2026-11-14): C7 and C8 are per seed.** See [`A1-C7-C8-DENOMINATOR.md`](A1-C7-C8-DENOMINATOR.md). Rows are not pooled across seeds; every seed must pass on its own rows. The pooled reading is rejected, not an alternative interpretation.

| Gate | Unit | N=4 rows/seed | N=4 step | N=8 rows/seed | N=8 step | N=20 registered rows/seed | N=20 step |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `C7_assertion_block` | per seed, per edge rate | 8 (completeness/order) | 0.008333 (120 cycles) | 16 (completeness/order) | 0.008333 (120 cycles) | 40 (completeness/order) | 0.008333 (120 cycles) |
| `C8_third_route` | per seed, per target row | 4 | 0.250000 | 8 | 0.125000 | 20 | 0.050000 |

C7's 0.05 margin is an A/K rate over 120 cycles on each paired target edge, so one cycle is 1/120 = 0.008333 and **C7 is resolved at N=4 and N=8**. The 2N Y- rows are for cell completeness and the assertion-order check, not the rate denominator. C8 is a per-target assertion rate: N=4 gives 0.25 and N=8 gives 0.125, both above 0.05, and the registered N=20 design gives 0.05; C8 needs at least 20 rows per seed (N>=20) for one-step resolution. The maximum disjoint target block is N=8, so the current design is **UNDER-RESOLVED for C8 only**. A separate registered N=20 C8 expansion design gives 20 A-K- rows per seed and a 0.05 step, so it resolves the C8 denominator **if adopted**; it is registered, not frozen, and is not the live manifest. The pooled counts at N=4 would be 48 C7 rows and 24 C8 rows; they are recorded only to show what was rejected, and the 24-row C8 pooled count would turn 1/4 = 0.25 into 1/24 = 0.041667.

**C1 denominator caveat.** The expanded C1 denominator of 63-64 rows is an upper bound from candidate counts. It assumes every candidate edge is baseline-available in the paired A+K+ control; it is not an observed or estimated baseline-availability denominator. See the [power-review risk note](A1-POWER-REVIEW.md#c1-denominator-feasibility-risk-note).

## Gates

| Gate | Scenario | Threshold | Denominator | Step | Status |
| --- | --- | ---: | ---: | ---: | --- |
| `C1_path_separation` | target-only fallback | 0.95 | 4 | 0.250000 | **FLAGGED** |
| `C1_path_separation` | N=8 maximum-feasibility target-only | 0.95 | 8 | 0.125000 | **FLAGGED** |
| `C1_path_separation` | expanded C4 denominator | 0.95 | 63–64 | 0.015873 | **PASS** |
| `C1_path_separation` | N=8 maximum-feasibility expanded denominator | 0.95 | 63–64 | 0.015873 | **PASS** |
| `C4_no_interference` | all cells | 0.05 | 59–60 | 0.016949 | **PASS** |
| `C4_no_interference` | N=8 maximum-feasibility all cells | 0.05 | 55–56 | 0.018182 | **PASS** |
| `C7_assertion_block` | Y- blocked rows | 0.05 | 120 | 0.008333 | **PASS** |
| `C7_assertion_block` | N=8 maximum-feasibility Y- blocked rows | 0.05 | 120 | 0.008333 | **PASS** |
| `C8_third_route` | A-K- blocked rows | 0.05 | 4 | 0.250000 | **FLAGGED** |
| `C8_third_route` | N=8 maximum-feasibility A-K- blocked rows | 0.05 | 8 | 0.125000 | **FLAGGED** |
| `C8_third_route` | registered N=20 C8 expansion | 0.05 | 20 | 0.050000 | **PASS** |
| `C2_treatment_consistency` | per manipulated arm | — | 4 | — | **NOT_APPLICABLE** |
| `C3_positivity` | per target edge | — | 4 | — | **NOT_APPLICABLE** |
| `C5_common_cause` | target rows | — | 4 | — | **NOT_APPLICABLE** |
| `C6_temporal_resolution` | six-seed block | — | 653–672 | — | **NOT_APPLICABLE** |
| `C9_same_object` | paired cells | — | 6 | — | **NOT_APPLICABLE** |

## N=8 maximum-feasibility reading

Eight disjoint targets use all 16 tag vertices, so N=8 is the maximum disjoint target block; eight disjoint edges are available in every seed. At that maximum, C7 has 16 Y- rows and C8 has 8 A-K- target rows. C7's rate step remains 1/120 = 0.008333, below the 0.05 margin, so C7 stays resolved. C8's step is 1/8 = 0.125, above 0.05, so C8 remains under-resolved and needs at least 20 rows (N>=20) for one-step resolution. C1 target-only at 8 rows is also still flagged (7/8 = 0.875); expanded C1 at 63–64 rows and C4 at 55–56 rows remain resolved. This is a planned-denominator statement, not a C7/C8 measurement.

## Flags

- `C1_path_separation — target-only fallback`
- `C1_path_separation — N=8 maximum-feasibility target-only`
- `C8_third_route — A-K- blocked rows`
- `C8_third_route — N=8 maximum-feasibility A-K- blocked rows`

`C1` is listed for both target-only and expanded-denominator cases. The 4-row and 8-row target-only cases are flagged; the expanded 63–64 row cases pass the resolution test, but the observed baseline-available count is still unknown.

## Post-run update

When A1 cell parts exist, `python -m benchmarks.a1_denominator_audit --parts [DIR]` recomputes the numeric denominators from those parts and writes a separate `A1-DENOMINATOR-RESOLUTION-OBSERVED.md` and JSON record. It uses the minimum observed denominator per gate, marks missing values **UNMEASURED** rather than zero, and does not overwrite this planned audit. An empty directory is **NOT RUN**. The observed record is a denominator statement, not a C7/C8 verdict or an A1 PASS/FAIL.

**Not evidence:** A resolution audit over planned denominators and precommitted thresholds. It runs no cell, assigns no seed, and does not measure C1, C4, C7 or C8.
