# Retention entry-transition — preregistration

Generated from `docs/retention_entry_transition_prereg.json` by `python -m benchmarks.retention_entry_transition_prereg --freeze`. Do not edit by hand.

**Status: `FROZEN, NOT RUN`.** The design was frozen before any cell. The runner is built behind the grant check; there is no grant, part or result.

## Question

Among never-served world edges that first loop by cycle 60 and remain absent from the readout structure through cycle f + 39, does loop retention in the first 20 cycles predict a sustained first structure entry in cycles f + 40 through 120, after controlling for retention in the adjacent 20-cycle window and for early rank, count, strength and follow-up horizon?

## Why this block exists

`CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` returned **`CONFIRMED, TEMPORALLY AMBIGUOUS`**: early-retention OR **2.09** (1.36–3.23), reverse post-landmark OR **32.83** (8.66–124.44). The reverse audit found the late OR stable to the follow-up control but concentrated at the boundaries: **11/11** edges at late retention **1.0** were asserted, **58/100** in between, against **1/55** at **0.0**. That block still defined assertion as a first post-landmark appearance, which can be a re-entry by an edge already present before the landmark.

The prior block's assertion_cycle was the first structure appearance after the landmark. That admits a re-entry by an edge already present before the landmark and labels it a new assertion. The reverse model also used a post-landmark rate whose denominator was the follow-up control. This block requires a structure-free interval through f + 39, makes the event a two-cycle entry at f + 40 or later, and measures both early and proximal retention before the outcome window. No seed, row or part from the prior block is reused.

## Timeline

```text
f .............. f+19 | f+20 ........ f+39 | f+40 ................ 120
     early retention      proximal retention     first sustained entry
     <----------- structure-free through f+39 ----------->
```

## Design

- Seeds: **20620101, 20620102, 20620103, 20620104, 20620105, 20620106, 20620107, 20620108, 20620109, 20620110, 20620111, 20620112, 20620113, 20620114, 20620115, 20620116, 20620117, 20620118, 20620119, 20620120, 20620121, 20620122, 20620123, 20620124** (24 fresh seeds).
- **120** cycles, cap **40**, PHASE_ACQUISITION, one replay per seed.
- Formation ceiling: **f <= 60**.
- Structure-free interval: **no structure appearance through f + 39**.
- Outcome window: **f + 40 through 120**.
- Population: never-served world edges with ever_loop=true, formation_cycle <= 60, no structure appearance at any cycle <= formation_cycle + 39, and full early and proximal windows.
- Excluded: never-served edges that never loop; edges forming after cycle 60; edges with any structure appearance through f + 39; edges served at least once; edges with incomplete predictor windows.
- Outcome: sustained first structure entry: the first cycle t >= formation_cycle + 40 with appearances at both t and t + 1; entry_cycle = t. Final presence at cycle 120 is descriptive only..
- Horizon control: `followup`; `f` is descriptive.

The event is not final presence. It is the first **two-cycle** structure entry at or after `f + 40`, so a one-cycle flicker does not count and a later exit does not erase the entry. Final presence at cycle 120 is reported separately.

## Primary model

```text
logit P(sustained entry) = b0 + b_early*z(early_retention) + b_proximal*z(proximal_retention) + b_rank*z(log2(rank20)) + b_count*z(count20) + b_strength*z(strength20) + b_followup*z(followup) + seed fixed effects
```

The primary coefficient is `b_early`. `proximal_retention` is a pre-outcome control measured in `f+20..f+39`; it is not a reverse-time variable. The estimator is Firth penalized likelihood with 24 seed fixed effects.

The base model without proximal retention, the full model adding `rank40`, `count40` and `strength40`, and the final-presence model are sensitivity diagnostics. They are reported but do not decide the verdict.

## Criteria

| ID | Criterion |
| --- | --- |
| `P1` early-retention direction | joint-model early-retention OR > 1 |
| `P2` early-retention interval | joint-model early-retention 95% CI lower bound > 1 |
| `P3` gates | all gates D1-D10 pass |
| `P4` proximal separation | proximal-retention OR <= 1 or its 95% CI includes 1 |

## Verdicts

| Verdict | Reading |
| --- | --- |
| `CONFIRMED` | P1-P4 pass: early retention adds a positive association with the later entry transition beyond proximal retention and the controls. |
| `CONFIRMED, PROXIMALLY AMBIGUOUS` | P1-P3 pass but P4 fails: both windows carry positive associations; the block does not identify the early window as the relevant one. |
| `DIRECTIONAL ONLY` | P1 and P3 pass but P2 fails: the point estimate is positive, the interval is not. |
| `NOT CONFIRMED` | P1 fails. |
| `VOID` | A gate fails; no coefficient is read. |

## Gates

| Gate | Requirement |
| --- | --- |
| `D1_population` | at least 60 eligible edges and 20 sustained entries; one row per seed-edge |
| `D2_structure_free` | every eligible edge has no structure appearance at any cycle <= f + 39, has finite early and proximal retention in full 20-cycle windows, and has f <= 60 |
| `D3_rank_coverage` | at least 95% of eligible edges have a finite rank20 |
| `D4_seed_levels` | all 24 planned seeds contribute eligible rows |
| `D5_convergence` | the primary joint fit and the base fit converge with finite coefficients |
| `D6_complete` | every fitted row has finite count20, strength20 and followup |
| `D7_entry_validity` | every entry has a finite entry_cycle > f + 39 with appearances at entry_cycle and entry_cycle + 1; every non-entry has entry_cycle = None; no edge has a structure appearance before f + 40 |
| `D8_no_collision` | the seed block is collision-free at freeze and check |
| `D9_separation` | abs(Pearson r(early_retention, proximal_retention)) <= 0.80; otherwise the two windows are not separable and the block is VOID |
| `D10_exposure` | every eligible edge has at least 20 cycles in f + 40..120; f <= 60 already implies at least 21 |

## Sample size

- Planned seeds: **24**.
- Minimum eligible edges: **60**.
- Minimum sustained entries: **20**.
- Power calculation: none. The structure-free 40-cycle requirement may leave too few entries; D1 is the only feasibility check and is applied once. The thresholds are not lowered after the count is seen.

`D1_population` is a feasibility gate, not a target. If the strict structure-free interval leaves fewer than 60 eligible edges or 20 sustained entries, the block is `VOID`; no threshold is lowered after the count is seen.

## Authorisation

No grant is recorded. The block is `FROZEN, NOT RUN`; the runner is built behind the grant check, but no part, result, gate or verdict exists. It must not be cited as evidence until it has a dated grant, a run artifact and a verdict from its own gates.

## What this does not establish

A preregistration, not a result. It spends no seed and makes no capability, causal, retention or general engine claim. The prior block's ambiguous result is not evidence for this design; the structure-free interval, the two-cycle entry and the 24-seed block are design choices, and a different interval or entry rule is a different block.
