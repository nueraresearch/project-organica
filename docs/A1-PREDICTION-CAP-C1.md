# A1 C1 ceiling under the prediction cap

Generated from `docs/a1_prediction_cap_c1.json` by `python -m benchmarks.a1_prediction_cap_c1 --write`. Do not edit by hand.

**Availability-only counterfactual, not an A1 result.** Same 18 candidate streams at loop cap **120**, prediction caps **20/40/80**. No target, freeze, grant or A1 cell.

## Result

A responds to the prediction cap while K stays flat, and the joint C1 ceiling rises with it; 4/18 seeds reach 60 jointly at cap 80.

| Prediction cap | A | K | A∩K | Σ min(A,K) | C1 pass (marginal) | C1 pass (joint) | Binding A/K/tie |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 20 | 744 | 1499 | 691 | 744 | 0/18 | 0/18 | 18/0/0 |
| 40 | 913 | 1498 | 842 | 913 | 2/18 | 0/18 | 18/0/0 |
| 80 | 1129 | 1497 | 1025 | 1129 | 6/18 | 4/18 | 18/0/0 |

The cap-40 control reproduces the committed cap-120 C1 rows exactly for A, K and A∩K. The marginal ceiling is `min(A,K)`; the joint ceiling is `A∩K`, which is the stricter targetable count.

## Per block

| Block | Candidates | A at 20 | A at 40 | A at 80 | K at 80 | A∩K at 80 | Joint pass at 80 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 382 | 243 | 281 | 317 | 382 | 317 | 0/6 |
| fresh-16 | 383 | 230 | 279 | 314 | 383 | 314 | 0/6 |
| larger-28 | 1000 | 271 | 353 | 498 | 732 | 394 | 4/6 |

## Per-seed rows at cap 80

| Block | Seed | Candidates | A | K | A∩K | min(A,K) | Gap to 60 (joint) | Binding | Marginal pass | Joint pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| current-16 | 20630101 | 64 | 51 | 64 | 51 | 51 | 9 | A | no | no |
| current-16 | 20630102 | 63 | 53 | 63 | 53 | 53 | 7 | A | no | no |
| current-16 | 20630103 | 64 | 59 | 64 | 59 | 59 | 1 | A | no | no |
| current-16 | 20630104 | 64 | 48 | 64 | 48 | 48 | 12 | A | no | no |
| current-16 | 20630105 | 64 | 53 | 64 | 53 | 53 | 7 | A | no | no |
| current-16 | 20630106 | 63 | 53 | 63 | 53 | 53 | 7 | A | no | no |
| fresh-16 | 20650101 | 64 | 56 | 64 | 56 | 56 | 4 | A | no | no |
| fresh-16 | 20650102 | 64 | 49 | 64 | 49 | 49 | 11 | A | no | no |
| fresh-16 | 20650103 | 64 | 58 | 64 | 58 | 58 | 2 | A | no | no |
| fresh-16 | 20650104 | 64 | 55 | 64 | 55 | 55 | 5 | A | no | no |
| fresh-16 | 20650105 | 63 | 47 | 63 | 47 | 47 | 13 | A | no | no |
| fresh-16 | 20650106 | 64 | 49 | 64 | 49 | 49 | 11 | A | no | no |
| larger-28 | 20660101 | 169 | 86 | 111 | 68 | 86 | -8 | A | yes | yes |
| larger-28 | 20660102 | 167 | 75 | 124 | 56 | 75 | 4 | A | yes | no |
| larger-28 | 20660103 | 172 | 83 | 105 | 51 | 83 | 9 | A | yes | no |
| larger-28 | 20660104 | 165 | 88 | 138 | 77 | 88 | -17 | A | yes | yes |
| larger-28 | 20660105 | 169 | 91 | 121 | 72 | 91 | -12 | A | yes | yes |
| larger-28 | 20660106 | 158 | 75 | 133 | 70 | 75 | -10 | A | yes | yes |

## Reading

This moves only the prediction window at a fixed 120-loop cap. A response identifies the prediction path as a lever; it does not show that C1 is reachable, because the joint A∩K ceiling is reported beside the marginal `min(A,K)` ceiling.

## What this does not claim

An availability-only counterfactual on 18 no-arm seeds. It varies the prediction cap on the service instance and measures the C1 ceiling; it is not a treatment effect, target viability or a successor. Cap 80 is a diagnostic condition, not a proposed protocol.
