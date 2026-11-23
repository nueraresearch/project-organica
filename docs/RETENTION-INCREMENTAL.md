# Retention incremental — result

Generated from `docs/retention_incremental.json` by `python -m benchmarks.retention_incremental --finish`. Do not edit by hand.

**Verdict: `VOID`.** The design was frozen in `docs/retention_incremental_prereg.json` before this block ran.

## Design

- Seeds: **20618101, 20618102, 20618103, 20618104, 20618105, 20618106, 20618107, 20618108, 20618109, 20618110, 20618111, 20618112**.
- **120** cycles, cap **40**, cycle-60 landmark.
- Population: never-served loop-forming edges formed by 60 and not asserted by 60.
- Primary: early retention, with rank, count, strength and formation measured through 60.
- Reverse-time diagnostic: late retention over cycles 61-120.

## Result

**VOID: no coefficient is read.** The pre-registered gates failed: `M1_population`.

| Quantity | Value |
| --- | ---: |
| Never-served edges | **399** |
| Loop-forming edges | **181** |
| Eligible edges | **103** |
| Asserted events | **0** |
| Fitted complete cases | **101** |
| Failed gates | `M1_population` |

## Criteria

| Criterion | Passes |
| --- | --- |
| `P1` | not read |
| `P2` | not read |
| `P3` | not read |
| `R1` | not read |

## Gates

| Gate | Passes |
| --- | --- |
| `M1_population` | no |
| `M2_landmark_complete` | yes |
| `M3_rank_coverage` | yes |
| `M4_seed_levels` | yes |
| `M5_convergence` | yes |
| `M6_complete` | yes |
| `M7_reverse_onset` | yes |
| `M8_no_collision` | yes |

## Per seed

| Seed | Never served | Asserted |
| ---: | ---: | ---: |
| 20618101 | 37 | 9 |
| 20618102 | 37 | 7 |
| 20618103 | 23 | 3 |
| 20618104 | 38 | 6 |
| 20618105 | 35 | 7 |
| 20618106 | 29 | 10 |
| 20618107 | 35 | 7 |
| 20618108 | 47 | 1 |
| 20618109 | 27 | 5 |
| 20618110 | 34 | 3 |
| 20618111 | 26 | 6 |
| 20618112 | 31 | 3 |

## Run note

A preliminary collection stopped at 88-92 cycles for seven seeds because a withheld acquisition event at a block boundary skipped that sleep. The boundary was fixed, all twelve parts were regenerated at 120 cycles, and no preliminary part entered this result.

## What this does and does not establish

A landmark model on one synthetic world family. It tests whether pre-assertion retention predicts final assertion beyond the measured controls. It does not establish a mechanism, a capability, transfer, or a general engine property. The reverse-time model is a diagnostic, not a second primary test.

An observational landmark model on one synthetic world family. The result does not establish a mechanism, a capability, transfer, or a general engine property. The cycle-60 cutoff is one choice; a different cutoff is a different design.
