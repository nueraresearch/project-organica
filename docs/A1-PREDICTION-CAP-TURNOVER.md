# A1 prediction-cap turnover

Generated from `docs/a1_prediction_cap_turnover.json` by `python -m benchmarks.a1_prediction_cap_turnover --write`. Do not edit by hand.

**Descriptive edge trace, not an A1 result.** 18 no-arm seeds at prediction caps **80** and **112**, loop cap **120**. No target, freeze, grant or A1 cell.

## Result

Raising the prediction cap from 80 to 112 adds 140 A edges (1129 to 1269) and drops 0, so A is nested and the turnover is pure addition. K membership is not one number here. On the 12 16-tag seeds K is complete at both caps, so new and retained edges both sit at 1.000 and those seeds cannot answer the question. On larger-28 the new edges carry K at 0.812 (65 of 80) against 0.791 (394 of 498) for retained, a difference of +0.021, with 2 seeds above, 3 below and 1 tied (two-sided sign test p = 1.0000). The pooled rates move the other way (0.893 against 0.908, -0.015) only because the new edges are weighted toward larger-28 — 80 of 140 against 498 of 1129 retained — whose base rate is lower; no block reverses that direction at block level. Against a block-adjusted expectation of 123.3, the new edges add 125 K-covered edges (+1.7), and joint C1 rises 1025 → 1150.

## Pooled

| Part | Edges | In K | K rate |
| --- | ---: | ---: | ---: |
| Retained (A80 ∩ A112) | 1129 | 1025 | 0.908 |
| New (A112 − A80) | 140 | 125 | 0.893 |
| Dropped (A80 − A112) | 0 | 0 | n/a |

A at cap 80: **1129**; at cap 112: **1269**. Joint C1 rises **1025 → 1150**. At the pooled retained rate the new edges would add **127.1** K-covered edges; block-adjusted they would add **123.3**; they add **125** (+1.7 against the adjusted expectation).

## Per seed

| Block | Seed | A80 | A112 | Retained | New | Dropped | New in K | New rate | Retained rate | Joint 80 | Joint 112 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 20630101 | 51 | 57 | 51 | 6 | 0 | 6 | 1.000 | 1.000 | 51 | 57 |
| current-16 | 20630102 | 53 | 57 | 53 | 4 | 0 | 4 | 1.000 | 1.000 | 53 | 57 |
| current-16 | 20630103 | 59 | 60 | 59 | 1 | 0 | 1 | 1.000 | 1.000 | 59 | 60 |
| current-16 | 20630104 | 48 | 55 | 48 | 7 | 0 | 7 | 1.000 | 1.000 | 48 | 55 |
| current-16 | 20630105 | 53 | 59 | 53 | 6 | 0 | 6 | 1.000 | 1.000 | 53 | 59 |
| current-16 | 20630106 | 53 | 57 | 53 | 4 | 0 | 4 | 1.000 | 1.000 | 53 | 57 |
| fresh-16 | 20650101 | 56 | 59 | 56 | 3 | 0 | 3 | 1.000 | 1.000 | 56 | 59 |
| fresh-16 | 20650102 | 49 | 56 | 49 | 7 | 0 | 7 | 1.000 | 1.000 | 49 | 56 |
| fresh-16 | 20650103 | 58 | 59 | 58 | 1 | 0 | 1 | 1.000 | 1.000 | 58 | 59 |
| fresh-16 | 20650104 | 55 | 63 | 55 | 8 | 0 | 8 | 1.000 | 1.000 | 55 | 63 |
| fresh-16 | 20650105 | 47 | 52 | 47 | 5 | 0 | 5 | 1.000 | 1.000 | 47 | 52 |
| fresh-16 | 20650106 | 49 | 57 | 49 | 8 | 0 | 8 | 1.000 | 1.000 | 49 | 57 |
| larger-28 | 20660101 | 86 | 101 | 86 | 15 | 0 | 11 | 0.733 | 0.791 | 68 | 79 |
| larger-28 | 20660102 | 75 | 90 | 75 | 15 | 0 | 12 | 0.800 | 0.747 | 56 | 68 |
| larger-28 | 20660103 | 83 | 93 | 83 | 10 | 0 | 9 | 0.900 | 0.614 | 51 | 60 |
| larger-28 | 20660104 | 88 | 104 | 88 | 16 | 0 | 14 | 0.875 | 0.875 | 77 | 91 |
| larger-28 | 20660105 | 91 | 100 | 91 | 9 | 0 | 7 | 0.778 | 0.791 | 72 | 79 |
| larger-28 | 20660106 | 75 | 90 | 75 | 15 | 0 | 12 | 0.800 | 0.933 | 70 | 82 |

## Per block

| Block | Retained | New | Dropped | Retained K rate | New K rate | Joint C1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 317 | 28 | 0 | 1.000 | 1.000 | 317 → 345 |
| fresh-16 | 314 | 32 | 0 | 1.000 | 1.000 | 314 → 346 |
| larger-28 | 498 | 80 | 0 | 0.791 | 0.812 | 394 → 459 |

## Sign test

All 18 seeds, new-minus-retained K rate: **3** below zero, **2** above, **13** tied; two-sided p = **1.0000**.

Larger-28 only: **3** below zero, **2** above, **1** tied; two-sided p = **1.0000**. The 12 16-tag seeds are ties by construction (K is complete, so both rates are 1.000) and carry no information about the question.

K sets are identical at both caps on **18/18** seeds, so the membership comparison uses the same carried set within a seed.

## What this does not claim

A descriptive edge-level trace on 18 no-arm seeds at two prediction caps. K membership is an availability property, not a treatment effect; seeds are the unit and edges within a seed are not independent. It does not show that serving a new edge would make K carry it, and it is not a target viability or successor.
