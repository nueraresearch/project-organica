# A1 C5 target timing — fixed earlier U

**ID:** `A1-C5-TARGET-TIMING-1`
**Status:** `PASS — FIXED EARLIER-U AT CYCLE 4; ALL CURRENT TARGETS PRESERVED`

**This is not an A1 result.** It is a no-arm timing audit; no cell was run and no target was changed.

## Decision

C5's U is fixed at **cycle 4**, sampled after the cycle-4 observations are stored and before
the cycle-4 sleep call. The cycle-36 sample remains the target-selection diagnostic; it is not
the C5 baseline. The four current targets are retained in every seed.

| Check | Value |
| --- | --- |
| Current target observations | 24 |
| N=20 target observations | 120 |
| Current targets with an observed carrier | 14 |
| Current targets without an observed carrier by cycle 120 | 10 |
| Current carriers before cycle 4 | 0 |
| Earliest observed carrier | cycle 5 |
| Earliest current carrier | cycle 5 |

An absent carrier is not a C5 timing violation; carrier absence is left to the
structural gates that require it. A carrier before cycle 4 is a failure.

## Per-seed audit

| Seed | Current targets | Preserved | Observed carriers | Missing carriers |
| ---: | ---: | ---: | ---: | ---: |
| `20630101` | 4 | 4 | 15 | 5 |
| `20630102` | 4 | 4 | 8 | 12 |
| `20630103` | 4 | 4 | 12 | 8 |
| `20630104` | 4 | 4 | 9 | 11 |
| `20630105` | 4 | 4 | 13 | 7 |
| `20630106` | 4 | 4 | 11 | 9 |

The full per-observation rows are in [`a1_c5_target_timing.json`](a1_c5_target_timing.json).
Each row records the first carrier cycle, the cycle-4 U counts and whether U precedes the carrier.

**Not evidence:** A no-arm target-timing audit. It runs no A1 cell, freezes no target and makes no causal, capability or transfer claim. C5 remains unrun until a granted cell produces its own U and carrier rows.

## Reproduce

```bash
python -m benchmarks.a1_c5_target_timing --check
python -m benchmarks.a1_c5_target_timing --self-test
```
