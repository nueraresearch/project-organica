# A1 denominator-resolution audit

**Date:** 2026-11-14
**Status:** `FLAGGED — 6 GATE SCENARIO(S) FINER THAN PLANNED DENOMINATOR`

**This is not an A1 result.** No cell was run; the observed denominators are still unknown.

For a proportion over n rows, the smallest nonzero change is 1/n. For a floor threshold t, the margin is 1-t; for a ceiling threshold t, the margin is t. A gate is FLAGGED when 1/n is greater than its margin; equality is not finer.

## Gates

| Gate | Scenario | Threshold | Denominator | Step | Status |
| --- | --- | ---: | ---: | ---: | --- |
| `C1_path_separation` | target-only fallback | 0.95 | 4 | 0.250000 | **FLAGGED** |
| `C1_path_separation` | N=8 maximum-feasibility target-only | 0.95 | 8 | 0.125000 | **FLAGGED** |
| `C1_path_separation` | expanded C4 denominator | 0.95 | 63–64 | 0.015873 | **PASS** |
| `C1_path_separation` | N=8 maximum-feasibility expanded denominator | 0.95 | 63–64 | 0.015873 | **PASS** |
| `C4_no_interference` | all cells | 0.05 | 59–60 | 0.016949 | **PASS** |
| `C4_no_interference` | N=8 maximum-feasibility all cells | 0.05 | 55–56 | 0.018182 | **PASS** |
| `C7_assertion_block` | Y- blocked rows | 0.05 | 8 | 0.125000 | **FLAGGED** |
| `C7_assertion_block` | N=8 maximum-feasibility Y- blocked rows | 0.05 | 16 | 0.062500 | **FLAGGED** |
| `C8_third_route` | A-K- blocked rows | 0.05 | 4 | 0.250000 | **FLAGGED** |
| `C8_third_route` | N=8 maximum-feasibility A-K- blocked rows | 0.05 | 8 | 0.125000 | **FLAGGED** |
| `C2_treatment_consistency` | per manipulated arm | — | 4 | — | **NOT_APPLICABLE** |
| `C3_positivity` | per target edge | — | 4 | — | **NOT_APPLICABLE** |
| `C5_common_cause` | target rows | — | 4 | — | **NOT_APPLICABLE** |
| `C6_temporal_resolution` | six-seed block | — | 653–672 | — | **NOT_APPLICABLE** |
| `C9_same_object` | paired cells | — | 6 | — | **NOT_APPLICABLE** |

## N=8 maximum-feasibility reading

Eight disjoint targets use all 16 tag vertices, so N=8 is the maximum disjoint target block; eight disjoint edges are available in every seed. At that maximum, C7 has 16 rows and C8 has 8. The smallest nonzero steps are 1/16 = 0.0625 and 1/8 = 0.125, both above the 0.05 margin, so C7 and C8 remain under-resolved. C7 would need at least 20 rows (N>=10) and C8 at least 20 rows (N>=20) for a one-step resolution. C1 target-only at 8 rows is also still flagged (7/8 = 0.875); expanded C1 at 63–64 rows and C4 at 55–56 rows remain resolved. This is a planned-denominator statement, not a C7/C8 measurement.

## Flags

- `C1_path_separation — target-only fallback`
- `C1_path_separation — N=8 maximum-feasibility target-only`
- `C7_assertion_block — Y- blocked rows`
- `C7_assertion_block — N=8 maximum-feasibility Y- blocked rows`
- `C8_third_route — A-K- blocked rows`
- `C8_third_route — N=8 maximum-feasibility A-K- blocked rows`

`C1` is listed for both target-only and expanded-denominator cases. The 4-row and 8-row target-only cases are flagged; the expanded 63–64 row cases pass the resolution test, but the observed baseline-available count is still unknown.

**Not evidence:** A resolution audit over planned denominators and precommitted thresholds. It runs no cell, assigns no seed, and does not measure C1, C4, C7 or C8.
