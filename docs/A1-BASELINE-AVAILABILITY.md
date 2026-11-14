# A1 baseline availability — observed C1/C4 denominators

**ID:** `A1-BASELINE-AVAILABILITY-1`
**Status:** `FLAGGED — C1 FLOOR NOT REACHED IN EITHER STREAM; C4 CELL STREAM IS WIDER THAN THE CANDIDATE PLAN`

**This is not an A1 result.** It is a no-arm A+K+ replay; no A-, K- or Y- treatment was applied and no target was changed.

## Definition

C1's A− denominator is the count of edges that have a carrier in the baseline; C1's K− denominator is the count of edges that are served in the baseline. C4's non-target rows are the stream minus the target block. Treatment deltas and gate verdicts still require cells.

## Cell stream

This is the full 120-cycle directed-edge stream that `a1_arms.run_cell` currently uses for `rows + neighbor_rows`.

| Seed | Rows | Baseline A | Baseline K | C1 A− denom | C1 K− denom | Min | Floor | C4 non-target N4 | C4 non-target N20 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| `20630101` | 112 | 70 | 82 | 82 | 70 | 70 | PASS | 108 | 92 |
| `20630102` | 112 | 72 | 59 | 59 | 72 | 59 | FAIL | 108 | 92 |
| `20630103` | 112 | 89 | 69 | 69 | 89 | 69 | PASS | 108 | 92 |
| `20630104` | 112 | 67 | 58 | 58 | 67 | 58 | FAIL | 108 | 92 |
| `20630105` | 112 | 85 | 72 | 72 | 85 | 72 | PASS | 108 | 92 |
| `20630106` | 112 | 85 | 72 | 72 | 85 | 72 | PASS | 108 | 92 |

| Total rows | Total C1 A− rows | Total C1 K− rows | Overall minimum | Floor reached? | C4 N4 | C4 N20 |
| ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 672 | 412 | 468 | 58 | **NO** | 648 | 552 |

## Candidate-protocol stream

This is the narrower one-orientation, first-36-cycle candidate universe used by target selection and the 63–64 plan.

| Seed | Rows | Baseline A | Baseline K | C1 A− denom | C1 K− denom | Min | Floor | C4 non-target N4 | C4 non-target N20 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| `20630101` | 64 | 44 | 44 | 44 | 44 | 44 | FAIL | 60 | 44 |
| `20630102` | 63 | 44 | 31 | 31 | 44 | 31 | FAIL | 59 | 43 |
| `20630103` | 64 | 52 | 39 | 39 | 52 | 39 | FAIL | 60 | 44 |
| `20630104` | 64 | 43 | 35 | 35 | 43 | 35 | FAIL | 60 | 44 |
| `20630105` | 64 | 49 | 43 | 43 | 49 | 43 | FAIL | 60 | 44 |
| `20630106` | 63 | 49 | 36 | 36 | 49 | 36 | FAIL | 59 | 43 |

| Total rows | Total C1 A− rows | Total C1 K− rows | Overall minimum | Floor reached? | C4 N4 | C4 N20 |
| ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 382 | 228 | 281 | 31 | **NO** | 358 | 262 |

## Stream divergence

| Extra cell-stream rows | Extra C4 N4 rows | Extra C4 N20 rows | Disposition |
| ---: | ---: | ---: | --- |
| 290 | 290 | 290 | **DESIGN INCONSISTENCY — the cell stream and the 63-64 candidate plan are not the same edge set; do not treat one denominator as the other.** |

The cell stream is wider than the candidate universe. Its C4 non-target counts are therefore not the 59–60 and 43–44 candidate-plan counts, and its C1 denominator can exceed the 63–64 candidate upper bound. That is a design inconsistency, not a larger sample: the extra edges were not candidate targets and are not licensed by the 63–64 plan.

## Target-only context

| Seed | N4 target rows | N4 baseline A/K available | N20 target rows | N20 baseline A/K available |
| ---: | ---: | --- | ---: | --- |
| `20630101` | 4 | 3 / 3 | 20 | 14 / 15 |
| `20630102` | 4 | 4 / 3 | 20 | 11 / 8 |
| `20630103` | 4 | 3 / 3 | 20 | 17 / 12 |
| `20630104` | 4 | 2 / 2 | 20 | 14 / 9 |
| `20630105` | 4 | 3 / 2 | 20 | 16 / 13 |
| `20630106` | 4 | 3 / 1 | 20 | 16 / 11 |

The target-only rows are below the 60-row C1 floor by construction; they are shown to keep the target and expanded denominators separate.

## Limits

C4 treatment deltas are **not** measured: `c4_measured_deltas` is 0 and C4 remains waiting for A+K+, A+K−, A−K+ and A−K− parts. C7 and C8 also remain unrun. A baseline count does not turn any gate into a verdict. This audit does not change the runner or the target set; it records the denominator that the current implementation and the candidate protocol would supply.

**Not evidence:** A no-arm baseline-availability audit. It runs no A1 cell, freezes no target, makes no causal, capability or transfer claim, and does not measure C1, C4, C7 or C8.

## Reproduce

```bash
python -m benchmarks.a1_baseline_availability --check
python -m benchmarks.a1_baseline_availability --self-test
```
