# Retention incremental — preregistration

Generated from `docs/retention_incremental_prereg.json` by `python -m benchmarks.retention_incremental_prereg --freeze`. Do not edit by hand.

**Status: `FROZEN, RUN`.** This is the frozen preregistration.

The owner's grant is recorded in `docs/AUTHORISATION-RETENTION-INCREMENTAL-1.md`, dated 2026-11-12.
The twelve cells have run; the result is `docs/retention_incremental.json`.

## Question

Among never-served loop-forming world edges that formed by cycle 60 and were not yet asserted at cycle 60, does retention measured only through cycle 60 predict final assertion at cycle 120 beyond rank, count, strength and formation timing?

## Design

- Seeds: **20618101, 20618102, 20618103, 20618104, 20618105, 20618106, 20618107, 20618108, 20618109, 20618110, 20618111, 20618112** (twelve fresh seeds).
- **120** cycles, cap **40**, PHASE_ACQUISITION, one replay per seed.
- **Landmark:** cycle **60**.
- Population: world edges with zero direct served windows, ever_loop=true, formation_cycle <= 60, and no assertion at or before cycle 60.
- Excluded: edges never served but not loop-forming; edges whose first loop forms after cycle 60; edges asserted at or before cycle 60.
- Outcome: asserted in the final structure at cycle 120.

The landmark is the point of the design. All primary predictors are measured through cycle 60; the outcome is read at cycle 120. Edges that were already asserted at the landmark are excluded, so the primary comparison is prospective rather than a full-run association.

## Primary model

```text
logit P(asserted at 120) = b0 + b_rank*z(log2(rank60)) + b_count*z(count60) + b_formation*z(formation) + b_strength*z(strength60) + b_early*z(early_retention) + seed fixed effects
```

Early retention is loop cycles from formation through cycle 60 divided by the available cycles in that window. It is bounded to [0, 1]. Rank, count, strength and formation are also landmark-capped. The estimator is Firth penalized likelihood with twelve seed fixed effects.

## Reverse-time control

The reverse model replaces early retention with **late retention**, the loop cycles in cycles 61-120 divided by 60. The first assertion cycle is recorded for every asserted edge and must be greater than 60.

The diagnostic is deliberately asymmetric: a positive early-retention result with a null late-retention result narrows reverse timing; a positive late-retention result means the association may be concurrent or post-assertion. It does not rescue a failed primary criterion.

## Reference, not replication

| Quantity | Post-hoc full-run model | This landmark block |
| --- | ---: | ---: |
| Loop-forming edges | **177** | see result artifact |
| Asserted events | **77** | see result artifact |
| Retention OR | **8.02** | see result artifact |
| Controlled retention OR | **14.68** | see result artifact |

The post-hoc result is `POST-HOC, not confirmatory`. This block tests a stricter landmark predictor, so its coefficient is not expected to equal the full-run coefficient.

## Criteria and verdicts

| Criterion | Test |
| --- | --- |
| `P1` early-retention direction | early-retention OR > 1 |
| `P2` early-retention interval | early-retention 95% CI lower bound > 1 |
| `P3` gates | all confirmatory gates pass |
| `R1` reverse-time diagnostic | late-retention OR <= 1 or its 95% CI includes 1 |

| Verdict | Reading |
| --- | --- |
| `CONFIRMED` | P1-P3 pass and R1 passes. |
| `CONFIRMED, TEMPORALLY AMBIGUOUS` | P1-P3 pass but late retention also has an OR > 1 with a lower 95% bound > 1; no temporal-direction claim. |
| `DIRECTIONAL ONLY` | P1 and P3 pass, but the early interval includes 1. |
| `NOT CONFIRMED` | The early-retention OR is at or below 1. |
| `VOID` | A gate fails; no coefficient is read. |

## Gates

| Gate | Requirement |
| --- | --- |
| `M1_population` | at least 60 eligible loop-forming never-served edges and 20 asserted events; one row per seed-edge |
| `M2_landmark_complete` | every eligible row has formation_cycle <= 60, is not asserted at or before 60, and has finite early_retention |
| `M3_rank_coverage` | at least 95% of eligible edges have a finite rank60 |
| `M4_seed_levels` | all twelve seeds contribute rows |
| `M5_convergence` | both the primary and reverse Firth fits converge with finite coefficients |
| `M6_complete` | every fitted row has finite count60 and strength60 |
| `M7_reverse_onset` | every asserted row has a finite assertion_cycle > 60; every non-asserted row has no assertion_cycle |
| `M8_no_collision` | the seed block is collision-free at freeze and check |

## Sample size

- Planned seeds: **12**.
- Minimum eligible edges: **60**.
- Minimum asserted events: **20**.
- Power calculation: none. Twelve fresh seeds are used to test a narrower landmark claim, not to power the post-hoc point estimate.

## Authorisation

Granted on **2026-11-12** in `docs/AUTHORISATION-RETENTION-INCREMENTAL-1.md`.
The twelve cells have run; the result is `docs/retention_incremental.json`.


## What this does not establish

An observational landmark model on one synthetic world family. The result does not establish a mechanism, a capability, transfer, or a general engine property. The cycle-60 cutoff is one choice; a different cutoff is a different design.
