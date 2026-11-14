# A1 denominator-resolution audit

**Date:** 2026-11-14
**Status:** `FLAGGED — 3 GATE SCENARIO(S) FINER THAN PLANNED DENOMINATOR`

**This is not an A1 result.** No cell was run; the observed denominators are still unknown.

For a proportion over n rows, the smallest nonzero change is 1/n. For a floor threshold t, the margin is 1-t; for a ceiling threshold t, the margin is t. A gate is FLAGGED when 1/n is greater than its margin; equality is not finer.

## Gates

| Gate | Scenario | Threshold | Denominator | Step | Status |
| --- | --- | ---: | ---: | ---: | --- |
| `C1_path_separation` | target-only fallback | 0.95 | 4 | 0.250000 | **FLAGGED** |
| `C1_path_separation` | expanded C4 denominator | 0.95 | 63–64 | 0.015873 | **PASS** |
| `C4_no_interference` | all cells | 0.05 | 59–60 | 0.016949 | **PASS** |
| `C7_assertion_block` | Y- blocked rows | 0.05 | 8 | 0.125000 | **FLAGGED** |
| `C8_third_route` | A-K- blocked rows | 0.05 | 4 | 0.250000 | **FLAGGED** |
| `C2_treatment_consistency` | per manipulated arm | — | 4 | — | **NOT_APPLICABLE** |
| `C3_positivity` | per target edge | — | 4 | — | **NOT_APPLICABLE** |
| `C5_common_cause` | target rows | — | 4 | — | **NOT_APPLICABLE** |
| `C6_temporal_resolution` | six-seed block | — | 653–672 | — | **NOT_APPLICABLE** |
| `C9_same_object` | paired cells | — | 6 | — | **NOT_APPLICABLE** |

## Flags

- `C1_path_separation — target-only fallback`
- `C7_assertion_block — Y- blocked rows`
- `C8_third_route — A-K- blocked rows`

`C1` is listed twice: the target-only fallback has four rows and is flagged; the expanded C4 denominator is planned at 63–64 rows and passes the resolution test, but its observed baseline-available count is still unknown.

**Not evidence:** A resolution audit over planned denominators and precommitted thresholds. It runs no cell, assigns no seed, and does not measure C1, C4, C7 or C8.
