# Retention formation-anchored — preregistration

Generated from `docs/retention_formation_anchored_prereg.json` by `python -m benchmarks.retention_formation_anchored_prereg --freeze`. Do not edit by hand.

**Status: `FROZEN, RUN`.** This is the frozen preregistration.

## Question

Among never-served loop-forming world edges that formed by cycle 90 and were not asserted during their first 20 loop cycles, does early retention measured over that full 20-cycle window predict assertion by cycle 120, including for edges that formed after cycle 60?

## Why this block exists

`CONFIRMATORY-RETENTION-INCREMENTAL-1` fixed a calendar landmark at cycle 60.  It found **103** eligible edges and **0** asserted events: all **16** late assertions in its never-served set formed after cycle 60.  That block is **`VOID`** and is not reused here.

The prior fixed cycle-60 landmark left no eligible asserted events.  This block keeps a full 20-cycle predictor window but anchors it at each edge's formation, so late-forming loop edges can enter the population.  No seed, part or row from the prior block is reused; its result is cited only as the reason for the new population.

## Design

- Seeds: **20619101, 20619102, 20619103, 20619104, 20619105, 20619106, 20619107, 20619108, 20619109, 20619110, 20619111, 20619112** (twelve fresh seeds).
- **120** cycles, cap **40**, PHASE_ACQUISITION, one replay per seed.
- **Formation-anchored window:** **20** cycles, from formation through formation + 19.
- Population: never-served world edges with ever_loop=true, formation_cycle <= 90, and no assertion at or before formation_cycle + 19.
- Excluded: never-served edges that never loop; edges that form after cycle 90; edges asserted during their first 20 loop cycles.
- Outcome: asserted in the final structure at cycle 120, with at least one outcome cycle after the landmark.
- Horizon control: `followup`; `formation` is descriptive.

The window is the point of the design.  Every eligible edge has the same **20-cycle** predictor window measured from its own formation, so an edge that forms at cycle 61 or 90 is not excluded for being late.  The outcome horizon varies with formation; `followup/120` is a control, and the cycle-90 ceiling leaves at least 10 outcome cycles.

## Primary model

```text
logit P(asserted by 120) = b0 + b_rank*z(log2(rank20)) + b_count*z(count20) + b_strength*z(strength20) + b_followup*z(followup) + b_early*z(early_retention) + seed fixed effects
```

Early retention is the distinct loop cycles in the first 20 cycles divided by 20.  It is bounded to [0, 1].  Rank, count and strength are measured in the same window.  Follow-up is the single fitted horizon control; formation is descriptive.  The estimator is Firth penalized likelihood with twelve seed fixed effects.

**Model identification.** `formation` and `followup` are exact affine transforms: `followup = (101 - formation) / 120`.  The fitted model uses `followup` as the single horizon control; `formation_cycle` is descriptive and has no separate coefficient.  This amendment was recorded before any grant or seed replay.

## Late cohort

Edges with `formation_cycle > 60` are the late cohort.  The same model is reported for that cohort descriptively.  Gate **M9** requires at least **10** eligible late edges and **3** asserted late events; if it fails, the block is `VOID` and no late-forming claim is read.

## Reverse-time control

The reverse model replaces early retention with **late retention**, measured from `formation + 20` through cycle 120 and divided by the available outcome cycles.  The first assertion cycle must be after the landmark.  A positive late-retention result labels the block `CONFIRMED, TEMPORALLY AMBIGUOUS`; it does not rescue the primary.

## Criteria and verdicts

| Criterion | Test |
| --- | --- |
| `P1` early-retention direction | all-cohort early-retention OR > 1 |
| `P2` early-retention interval | all-cohort early-retention 95% CI lower bound > 1 |
| `P3` gates | all confirmatory gates pass, including late representation |
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
| `M1_population` | at least 60 eligible edges and 20 asserted events; one row per seed-edge |
| `M2_window_complete` | every eligible row formed by 90, has no assertion at or before its landmark, and has finite early_retention in a full 20-cycle window |
| `M3_rank_coverage` | at least 95% of eligible edges have a finite rank20 |
| `M4_seed_levels` | all twelve seeds contribute rows |
| `M5_convergence` | both the primary and reverse Firth fits converge with finite coefficients |
| `M6_complete` | every fitted row has finite count20, strength20 and followup |
| `M7_reverse_onset` | every asserted eligible row has a finite assertion_cycle after its landmark; every non-asserted eligible row has no assertion_cycle |
| `M8_no_collision` | the seed block is collision-free at freeze and check |
| `M9_late_representation` | at least 10 eligible edges and 3 asserted events have formation_cycle > 60; otherwise the late-forming claim is VOID |

## Sample size

- Planned seeds: **12**.
- Minimum eligible edges: **60**.
- Minimum asserted events: **20**.
- Minimum late-cohort edges: **10**.
- Minimum late-cohort events: **3**.
- Power calculation: none.  Twelve fresh seeds test whether the formation-anchored population has both enough events and enough late-cohort representation; the block does not reuse the prior point estimate.

## Amendments

| Date | Kind | Change |
| --- | --- | --- |
| 2026-11-12 | `model-identification` | Removed `formation` from the fitted predictors and kept `followup` as the single horizon control. |

## Authorisation

Granted on **2026-11-12** in `docs/AUTHORISATION-RETENTION-FORMATION-ANCHORED-1.md`.

Run authorisation:

> Fix the post-landmark assertion cycle and rerun the twelve cells.
The runner is built behind the grant check.
The twelve cells have run; the result is `docs/retention_formation_anchored.json`.

## What this does not establish

A preregistration, not a result.  It spends no seed and makes no capability, causal, retention or general engine claim.  The prior block's VOID is not evidence for this design; the 20-cycle window and the cycle-90 formation ceiling are design choices, and a different window or ceiling is a different block.
