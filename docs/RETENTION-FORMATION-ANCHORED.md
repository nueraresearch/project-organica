# Retention formation-anchored — result

Generated from `docs/retention_formation_anchored.json` by `python -m benchmarks.retention_formation_anchored --finish`. Do not edit by hand.

**Verdict: `CONFIRMED, TEMPORALLY AMBIGUOUS`.** The design was frozen in `docs/retention_formation_anchored_prereg.json` before this block ran.

## Design

- Seeds: **20619101, 20619102, 20619103, 20619104, 20619105, 20619106, 20619107, 20619108, 20619109, 20619110, 20619111, 20619112**.
- **120** cycles, cap **40**, per-edge **20**-cycle window.
- Population: never-served loop-forming edges with `formation_cycle <= 90` that were not asserted in their window.
- Primary: early retention over the first twenty cycles, with rank20, count20, strength20 and the follow-up horizon control; formation is descriptive.

**Model identification note.** `formation` and `followup` are exact affine transforms: `followup = (101 - formation) / 120`.  The fitted model uses `followup` as the single horizon control; `formation_cycle` is descriptive and has no separate coefficient.  This amendment was recorded before any grant or seed replay.
- Late cohort: edges with formation after cycle 60.

## Result

| Quantity | Primary | Reverse |
| --- | ---: | ---: |
| Eligible edges | **172** | **172** |
| Fitted complete cases | **166** | **166** |
| Asserted events | **70** | **70** |
| Retention OR | **2.09** | **32.83** |
| Retention 95% CI | 1.36–3.23 | 8.66–124.44 |
| Late-retention boundary | — | **1/55** at 0.0; **58/100** in between; **11/11** at 1.0 |
| AUC | 0.804 | 0.961 |
| Brier | 0.1739 | 0.0696 |

The primary coefficient is early retention per 1 SD. Post-landmark retention also has a positive association, so the block cannot separate early timing from concurrent or reverse timing. The reverse OR is a boundary contrast, not a dose-response: **1/55** edges at late retention 0.0 were asserted, **58/100** in between, against **11/11** at 1.0. Both coefficients remain observational.

## Late cohort

The late cohort is reported descriptively; it does not replace the all-cohort primary or M9.

| Quantity | Late cohort |
| --- | ---: |
| Edges | **36** |
| Asserted events | **18** |
| Early-retention OR | **2.14** |
| Early-retention 95% CI | 0.60–7.59 |

## Criteria

| Criterion | Passes |
| --- | --- |
| `P1` | yes |
| `P2` | yes |
| `P3` | yes |
| `R1` | no |

## Gates

| Gate | Passes |
| --- | --- |
| `M1_population` | yes |
| `M2_window_complete` | yes |
| `M3_rank_coverage` | yes |
| `M4_seed_levels` | yes |
| `M5_convergence` | yes |
| `M6_complete` | yes |
| `M7_reverse_onset` | yes |
| `M8_no_collision` | yes |
| `M9_late_representation` | yes |

## Per seed

| Seed | Never served | Asserted |
| ---: | ---: | ---: |
| 20619101 | 43 | 4 |
| 20619102 | 39 | 2 |
| 20619103 | 37 | 9 |
| 20619104 | 49 | 15 |
| 20619105 | 37 | 5 |
| 20619106 | 33 | 3 |
| 20619107 | 38 | 11 |
| 20619108 | 37 | 7 |
| 20619109 | 27 | 3 |
| 20619110 | 51 | 8 |
| 20619111 | 31 | 6 |
| 20619112 | 12 | 3 |

## Leave-one-seed-out sensitivity

| Held out | Early beta | Late beta |
| ---: | ---: | ---: |
| 20619101 | 0.725 | 3.331 |
| 20619102 | 0.753 | 3.498 |
| 20619103 | 0.679 | 3.243 |
| 20619104 | 0.690 | 3.080 |
| 20619105 | 0.785 | 3.352 |
| 20619106 | 0.793 | 3.702 |
| 20619107 | 0.921 | 3.069 |
| 20619108 | 0.732 | 4.383 |
| 20619109 | 0.686 | 4.019 |
| 20619110 | 0.749 | 3.284 |
| 20619111 | 0.646 | 3.692 |
| 20619112 | 0.731 | 3.453 |

## What this does and does not establish

A formation-anchored landmark model on one synthetic world family. It tests whether early retention predicts assertion beyond the measured controls, including among edges that form late. It does not establish a mechanism, a capability, transfer, or a general engine property. The reverse-time model is a diagnostic, not a second primary test.

An observational formation-anchored landmark model on one synthetic world family.  Early and post-landmark retention both carry positive associations, so this block does not establish that early retention precedes assertion.  It does not establish a mechanism, capability, transfer, causal effect, or general engine property.
