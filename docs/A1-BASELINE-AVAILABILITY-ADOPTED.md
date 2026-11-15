# A1 baseline availability — observed C1/C4 denominators

**ID:** `A1-BASELINE-AVAILABILITY-ADOPTED-1`
**Status:** `FLAGGED — C1 FLOOR NOT REACHED IN THE CANDIDATE STREAM; C4 CELL STREAM IS WIDER THAN THE CANDIDATE PLAN`

**This is not an A1 result.** It is a no-arm A+K+ replay; no A-, K- or Y- treatment was applied and no target was changed.

## Definition

C1's A− denominator is the count of edges that have a carrier in the baseline; C1's K− denominator is the count of edges that are served in the baseline. C4's non-target rows are the stream minus the target block. Treatment deltas and gate verdicts still require cells.

## Cell stream

This is the full 120-cycle directed-edge stream that `a1_arms.run_cell` currently uses for `rows + neighbor_rows`.

| Seed | Rows | Baseline A | Baseline K | C1 A− denom | C1 K− denom | Min | Floor | C4 non-target N4 | C4 non-target N20 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| `20740101` | 112 | 79 | 81 | 81 | 79 | 79 | PASS | 108 | 92 |
| `20740102` | 112 | 81 | 64 | 64 | 81 | 64 | PASS | 108 | 92 |
| `20740103` | 112 | 79 | 84 | 84 | 79 | 79 | PASS | 108 | 92 |
| `20740104` | 112 | 74 | 82 | 82 | 74 | 74 | PASS | 108 | 92 |
| `20740105` | 112 | 83 | 72 | 72 | 83 | 72 | PASS | 108 | 92 |
| `20740106` | 112 | 82 | 74 | 74 | 82 | 74 | PASS | 108 | 92 |

| Total rows | Total C1 A− rows | Total C1 K− rows | Overall minimum | Floor reached? | C4 N4 | C4 N20 |
| ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 672 | 457 | 478 | 64 | **YES** | 648 | 552 |

## Candidate-protocol stream

This is the narrower one-orientation, first-36-cycle candidate universe used by target selection and the 63–64 plan.

| Seed | Rows | Baseline A | Baseline K | C1 A− denom | C1 K− denom | Min | Floor | C4 non-target N4 | C4 non-target N20 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| `20740101` | 64 | 45 | 46 | 46 | 45 | 45 | FAIL | 60 | 44 |
| `20740102` | 64 | 51 | 34 | 34 | 51 | 34 | FAIL | 60 | 44 |
| `20740103` | 64 | 47 | 48 | 48 | 47 | 47 | FAIL | 60 | 44 |
| `20740104` | 64 | 50 | 48 | 48 | 50 | 48 | FAIL | 60 | 44 |
| `20740105` | 64 | 49 | 38 | 38 | 49 | 38 | FAIL | 60 | 44 |
| `20740106` | 62 | 48 | 41 | 41 | 48 | 41 | FAIL | 58 | 42 |

| Total rows | Total C1 A− rows | Total C1 K− rows | Overall minimum | Floor reached? | C4 N4 | C4 N20 |
| ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 382 | 255 | 290 | 34 | **NO** | 358 | 262 |

## Stream divergence

| Extra cell-stream rows | Extra C4 N4 rows | Extra C4 N20 rows | Disposition |
| ---: | ---: | ---: | --- |
| 290 | 290 | 290 | **DESIGN INCONSISTENCY — the cell stream and the 63-64 candidate plan are not the same edge set; do not treat one denominator as the other.** |

The cell stream is wider than the candidate universe. Its C4 non-target counts are therefore not the 59–60 and 43–44 candidate-plan counts, and its C1 denominator can exceed the 63–64 candidate upper bound. That is a design inconsistency, not a larger sample: the extra edges were not candidate targets and are not licensed by the 63–64 plan.

## Target-only context

| Seed | N4 target rows | N4 baseline A/K available | N20 target rows | N20 baseline A/K available |
| ---: | ---: | --- | ---: | --- |
| `20740101` | 4 | 4 / 3 | 20 | 13 / 14 |
| `20740102` | 4 | 3 / 0 | 20 | 16 / 9 |
| `20740103` | 4 | 3 / 4 | 20 | 13 / 15 |
| `20740104` | 4 | 3 / 2 | 20 | 17 / 14 |
| `20740105` | 4 | 3 / 2 | 20 | 13 / 13 |
| `20740106` | 4 | 4 / 2 | 20 | 14 / 12 |

The target-only rows are below the 60-row C1 floor by construction; they are shown to keep the target and expanded denominators separate.

## Limits

C4 treatment deltas are **not** measured: `c4_measured_deltas` is 0 and C4 remains waiting for A+K+, A+K−, A−K+ and A−K− parts. C7 and C8 also remain unrun. A baseline count does not turn any gate into a verdict. This audit does not change the runner or the target set; it records the denominator that the current implementation and the candidate protocol would supply.

**Not evidence:** A no-arm baseline-availability audit. It runs no A1 cell, freezes no target, makes no causal, capability or transfer claim, and does not measure C1, C4, C7 or C8.

## Reproduce

```bash
python -m benchmarks.a1_baseline_availability --check
python -m benchmarks.a1_baseline_availability --self-test
```
