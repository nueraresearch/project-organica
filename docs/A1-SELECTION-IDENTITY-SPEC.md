# A1 selection-versus-count specification

Generated from `docs/a1_selection_identity_spec.json` by `python -m benchmarks.a1_selection_identity_spec --write`. Do not edit by hand.

**Specification, not a result. No arm was run.**

## Result

The test is a **fixed-count exchange**: run the committed configuration twice on the same seeds — once unchanged (**arm I**) and once with the transition ordering replaced by the probability-only order (**arm S**) — at the same cap and on the same candidate set, so the served count is fixed by construction and only the identity of the served edges moves. A third arm (**arm C**) moves the cap by a few slots to price one served edge in the same conditions, so the contrast is reported in **edge-equivalents** rather than in offset units only this analysis can read. The committed traces already say how big the exchange is: the two orders disagree on **6.1** of **58** served edges per seed (**10.5%**). If identity matters with the same exchange rate the count has, that is **0.1128** coverage units, or **2.60** seed standard deviations of the level — **6 seeds per arm and block** to see it at a 5% two-sided test with 80% power. The decision rule is pre-committed in edge-equivalents: selection identity is **supported** only if the swap moves the level by at least **2.0** edges' worth with an interval excluding zero, **refuted** if it moves by less than **0.5**, and otherwise undecided. The calibration is the point: arm C makes a one-edge effect measurable, so a null in arm S says that swapping **6.1** edges changed nothing a single edge would have changed, not merely that the level was noisy. The design is asymmetric and that is its weakness: **0** seeds per arm and block would be needed to refute a **0.5**-edge effect, against **6** to see the full swap, so the test can support the selection account cheaply but can only fail to find a small identity effect — a null leaves the question open rather than closing it.

## Exchange rate: level per served edge

| Block | Caps | Served per sqrt(cap) | Level per served edge |
| --- | --- | ---: | ---: |
| current-16 | 40/80/112 | 2.4849 | 0.018909 |
| fresh-16 | 40/80/112 | 2.5855 | 0.018173 |
| larger-28 | 40/80/112 | 8.8449 | 0.005312 |

## Exchange size in the committed trace

| Seeds | Mean served | Mean swapped | Swap fraction | Effect if identity matters |
| ---: | ---: | ---: | ---: | ---: |
| 12 | 57.6 | 6.1 | 0.105 | 0.1128 |

## Seeds per arm and block

| Per-seed SD | Source | Effect (edges) | Effect (level) | Seeds |
| ---: | --- | ---: | ---: | ---: |
| 0.066656 | seed-level LOO RMSE | 0.5 | 0.0093 | 812 |
| 0.066656 | seed-level LOO RMSE | 1.0 | 0.0185 | 203 |
| 0.066656 | seed-level LOO RMSE | 2.0 | 0.0371 | 51 |
| 0.066656 | seed-level LOO RMSE | 3.0 | 0.0556 | 23 |
| 0.066656 | seed-level LOO RMSE | 6.0 | 0.1112 | 6 |
| 0.043410 | current-16 within-block SD | 0.5 | 0.0093 | 345 |
| 0.043410 | current-16 within-block SD | 1.0 | 0.0185 | 87 |
| 0.043410 | current-16 within-block SD | 2.0 | 0.0371 | 22 |
| 0.043410 | current-16 within-block SD | 3.0 | 0.0556 | 10 |
| 0.043410 | current-16 within-block SD | 6.0 | 0.1112 | 3 |
| 0.072798 | fresh-16 within-block SD | 0.5 | 0.0093 | 968 |
| 0.072798 | fresh-16 within-block SD | 1.0 | 0.0185 | 242 |
| 0.072798 | fresh-16 within-block SD | 2.0 | 0.0371 | 61 |
| 0.072798 | fresh-16 within-block SD | 3.0 | 0.0556 | 27 |
| 0.072798 | fresh-16 within-block SD | 6.0 | 0.1112 | 7 |

## Arms

| Arm | Role | Change | Requirement |
| --- | --- | --- | --- |
| I | identity control | none — the committed configuration, re-run | reproduce the committed level for the seed, or the seed is void |
| S | swap | transition ordering replaced by the probability-only order | serve the same number of candidate edges as arm I |
| C | count calibration | prediction cap moved by a few transition slots | move the served count without touching the candidate set |

## Decision rule

- **statistic**: level(arm S) minus level(arm I), divided by the level per served edge measured by arm C, reported in edge-equivalents
- **supported**: at least 2.0 edge-equivalents with an interval excluding zero
- **refuted**: at most 0.5 edge-equivalents
- **otherwise**: undecided — the exchange neither separates nor excludes
- **seed_rule**: a seed contributes only if its arms serve the same count; the block is void if arm I misses the committed level

## Limits

- The exchange rate is read from the frozen cap curve, which attributes the whole cap slope to the count; the cap also buys window depth, so the per-edge value is an upper proxy until arm C measures it in-run.
- Arm S changes the ordering basis, which is an engine-behaviour change: the spec is a proposal that needs a grant, not a thing this analysis may run.
- The swap fraction is measured on the committed ordering trace at cap 112 and will not transfer exactly to a block whose candidate pool differs.
- Three arms multiply the run cost: the design is only worth mounting if a positive arm-S result would change the selection architecture rather than add another diagnostic.

## What this does not claim

A specification and a design estimate. It runs no arm, opens no database, measures no level, and is not a treatment, target, freeze, grant or A1 cell.
