# A1 C1 at prediction cap 112

Generated from `docs/a1_prediction_cap_112.json` by `python -m benchmarks.a1_prediction_cap_112 --write`. Do not edit by hand.

**Availability-only counterfactual, not an A1 result.** Same 18 candidate streams at loop cap **120**, prediction caps **40/80/112**. No target, freeze, grant or A1 cell.

## Result

At prediction cap 112, the 16-tag near-misses clear on 2/12 seeds (current 1/6, fresh 1/6); joint C1 reaches 8/18 overall against 4/18 at cap 80.

| Prediction cap | A | K | A∩K | Σ min(A,K) | Pass min | Pass joint | Binding A/K/tie |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 40 | 913 | 1498 | 842 | 913 | 2/18 | 0/18 | 18/0/0 |
| 80 | 1129 | 1497 | 1025 | 1129 | 6/18 | 4/18 | 18/0/0 |
| 112 | 1269 | 1497 | 1150 | 1269 | 8/18 | 8/18 | 18/0/0 |

Cap 40 reproduces the committed cap-120 C1 control, and cap 80 reproduces the committed prediction-cap rows exactly. Cap 112 is the engine's shipped prediction cap.

## Per block

| Block | Candidates | A at 80 | A∩K at 80 | Joint at 80 | A at 112 | A∩K at 112 | Joint at 112 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 382 | 317 | 317 | 0/6 | 345 | 345 | 1/6 |
| fresh-16 | 383 | 314 | 314 | 0/6 | 346 | 346 | 1/6 |
| larger-28 | 1000 | 498 | 394 | 4/6 | 578 | 459 | 6/6 |

## Per-seed rows at cap 112

| Block | Seed | Candidates | A | K | A∩K | min(A,K) | Gap to 60 (joint) | Binding | Pass min | Pass joint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| current-16 | 20630101 | 64 | 57 | 64 | 57 | 57 | 3 | A | no | no |
| current-16 | 20630102 | 63 | 57 | 63 | 57 | 57 | 3 | A | no | no |
| current-16 | 20630103 | 64 | 60 | 64 | 60 | 60 | 0 | A | yes | yes |
| current-16 | 20630104 | 64 | 55 | 64 | 55 | 55 | 5 | A | no | no |
| current-16 | 20630105 | 64 | 59 | 64 | 59 | 59 | 1 | A | no | no |
| current-16 | 20630106 | 63 | 57 | 63 | 57 | 57 | 3 | A | no | no |
| fresh-16 | 20650101 | 64 | 59 | 64 | 59 | 59 | 1 | A | no | no |
| fresh-16 | 20650102 | 64 | 56 | 64 | 56 | 56 | 4 | A | no | no |
| fresh-16 | 20650103 | 64 | 59 | 64 | 59 | 59 | 1 | A | no | no |
| fresh-16 | 20650104 | 64 | 63 | 64 | 63 | 63 | -3 | A | yes | yes |
| fresh-16 | 20650105 | 63 | 52 | 63 | 52 | 52 | 8 | A | no | no |
| fresh-16 | 20650106 | 64 | 57 | 64 | 57 | 57 | 3 | A | no | no |
| larger-28 | 20660101 | 169 | 101 | 111 | 79 | 101 | -19 | A | yes | yes |
| larger-28 | 20660102 | 167 | 90 | 124 | 68 | 90 | -8 | A | yes | yes |
| larger-28 | 20660103 | 172 | 93 | 105 | 60 | 93 | 0 | A | yes | yes |
| larger-28 | 20660104 | 165 | 104 | 138 | 91 | 104 | -31 | A | yes | yes |
| larger-28 | 20660105 | 169 | 100 | 121 | 79 | 100 | -19 | A | yes | yes |
| larger-28 | 20660106 | 158 | 90 | 133 | 82 | 90 | -22 | A | yes | yes |

## Reading

The 16-tag blocks have full K coverage, so their joint ceiling is A. The larger block is reported separately because its joint ceiling is limited by K coverage as well as A.

## What this does not claim

An availability-only counterfactual on 18 no-arm seeds at one shipped cap. It measures the C1 ceiling; it is not a treatment effect, target viability or a successor. Cap 112 is the engine's shipped prediction cap, not a new protocol.
