# A1 split-block power

Generated from `docs/a1_split_power.json` by `python -m benchmarks.a1_split_power --write`. Do not edit by hand.

**Design estimate, not an A1 result.** No split block has been run.

## Result

The differential needs **9 seeds per split block** — **18** seeds in total — to decide either branch at a **20%** wrong-decision rate under the primary per-seed SD **0.0667** (candidate-size cell seed-level LOO RMSE). The branches are not equally cheap: the size branch needs **6** seeds and the density branch **9**, because the density evidence is the distance from the estimate to the **0.09** ceiling — only **0.0264** against a **0.1164** separation — while the size branch only has to land the estimate inside a **0.05** band around zero. Across the per-seed SDs the measured blocks supply (**0.0357**–**0.0728**) the same rate asks for **2**–**11** seeds per block, so **11** is the defensible design number and **9** the one implied by the frozen fit. The committed **6** seeds per block do not reach the convention: at **σ 0.0667** the standard error of the difference is **0.0385**, which gives **0.818** power on the size branch but only **0.767** on the density branch, with a **0.013** chance of declaring density when the size summary is true, **0.043** of the reverse, **0.078** of landing in the undecided band when the size summary is true and **0.190** when the density summary is. A paired design on the same seeds in both blocks scales the requirement by **(1 − ρ)**; at **ρ 0.5** the number falls to **4** seeds per block. The cheaper alternative — measuring one block's level against the two predictions, which differ by **0.349** and **0.465** at equal candidate count — needs only **2** seeds per block at the primary SD, but that level estimate inherits the failure measured in `84ce329`, where a fresh block landed below its fitted value; the differential is robust to that shift, which is why it is the more expensive estimand.

## Seeds per block by per-seed SD and wrong-decision rate

| Per-seed SD | Source | Rate | Size branch | Density branch | Both | Total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0.035742 | seed-2067 within-block offset SD | 0.20 | 2 | 2 | 2 | 4 |
| 0.035742 | seed-2067 within-block offset SD | 0.10 | 3 | 6 | 6 | 12 |
| 0.035742 | seed-2067 within-block offset SD | 0.05 | 5 | 10 | 10 | 20 |
| 0.043410 | current-16 within-block offset SD | 0.20 | 2 | 3 | 3 | 6 |
| 0.043410 | current-16 within-block offset SD | 0.10 | 5 | 9 | 9 | 18 |
| 0.043410 | current-16 within-block offset SD | 0.05 | 7 | 15 | 15 | 30 |
| 0.066656 | candidate-size cell seed-level LOO RMSE | 0.20 | 6 | 9 | 9 | 18 |
| 0.066656 | candidate-size cell seed-level LOO RMSE | 0.10 | 10 | 21 | 21 | 42 |
| 0.066656 | candidate-size cell seed-level LOO RMSE | 0.05 | 14 | 35 | 35 | 70 |
| 0.072798 | fresh-16 within-block offset SD | 0.20 | 7 | 11 | 11 | 22 |
| 0.072798 | fresh-16 within-block offset SD | 0.10 | 12 | 25 | 25 | 50 |
| 0.072798 | fresh-16 within-block offset SD | 0.05 | 17 | 42 | 42 | 84 |

## What six seeds per block buys

| Quantity | Value |
| --- | ---: |
| SE of the difference | 0.038484 |
| Power, size branch | 0.8179 |
| Power, density branch | 0.7672 |
| Declares density when size is true | 0.0127 |
| Declares size when density is true | 0.0426 |
| Lands in the undecided band, size true | 0.0783 |
| Lands in the undecided band, density true | 0.1902 |

## Paired design

| Seed correlation | SE at six | Density power at six | Seeds for both branches |
| ---: | ---: | ---: | ---: |
| 0.00 | 0.038484 | 0.7672 | 9 |
| 0.30 | 0.032198 | 0.8068 | 6 |
| 0.50 | 0.027212 | 0.8453 | 4 |

## The cheaper level alternative

| Block | Model gap | Seeds at half the gap |
| --- | ---: | ---: |
| split-32 | 0.348712 | 2 |
| split-48 | 0.465092 | 2 |

## Limits

- The per-seed SD is not measured in a split block; it is borrowed from 16-tag blocks and from the fitted seed-level LOO RMSE, and the answer moves by a factor of three across that grid.
- The predictions are frozen-summary counterfactuals: no split block has been run, so a measured differential may not fall at either predicted value.
- Power assumes independent seeds across the two blocks; a paired design on the same seeds is reported as a sensitivity, not as a recommendation.
- The band rule is a design convention, not a hypothesis test; the reported rate is the probability of the wrong band, and it is not comparable to a p-value.

## What this does not claim

A design estimate computed from committed artifacts. It runs no arm, measures no split block, and is not a treatment, target, freeze, grant or A1 cell.
