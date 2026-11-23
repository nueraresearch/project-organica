# Never-served assertion model — result

**Status.** FIT. Generated from `docs/never_served_assertion_model.json`; never edited by hand.

| Field | Value |
| --- | --- |
| Population | 180 never-served edges |
| Complete cases | 179 |
| Events | 26 asserted |
| Model | Firth logistic, seed fixed effects |
| AUC | 0.925 |
| Brier | 0.0743 |
| Gates | all pass |

## Separation

| | Asserted | Not asserted |
| --- | ---: | ---: |
| Loop formed | 26 | 35 |
| No loop | 0 | 118 |

The no-loop, asserted cell is zero. This is quasi-complete separation; the Firth penalty is what makes the loop coefficient finite.

## Coefficients

| Term | OR | 95% CI | p |
| --- | ---: | --- | ---: |
| `loop` | 75.104 | 6.659–847.078 | 0.0005 |
| `rank_log2_z` | 1.094 | 0.613–1.954 | 0.7614 |
| `count_z` | 1.961 | 0.873–4.402 | 0.1027 |

Rank and count odds ratios are per 1 SD. The loop odds ratio is a 0/1 contrast. A rank OR below 1 means a worse rank is associated with lower assertion.

## Average marginal effects

| Contrast | Probability difference |
| --- | ---: |
| Loop 1 vs 0 | +0.327 |
| Rank +1 SD | +0.007 |
| Count +1 SD | +0.055 |

## Calibration

| Bin | n | Mean predicted | Observed |
| ---: | ---: | ---: | ---: |
| 1 | 35 | 0.002 | 0.000 |
| 2 | 36 | 0.004 | 0.000 |
| 3 | 36 | 0.008 | 0.000 |
| 4 | 36 | 0.200 | 0.167 |
| 5 | 36 | 0.542 | 0.556 |

## Leave-one-seed-out

| Held out | Loop beta | Rank beta | Count beta |
| ---: | ---: | ---: | ---: |
| 20611601 | 4.122 | -0.163 | 0.915 |
| 20611602 | 4.175 | 0.113 | 0.513 |
| 20611603 | 4.016 | 0.202 | 0.756 |
| 20611604 | 4.228 | 0.120 | 0.684 |
| 20611605 | 4.177 | 0.138 | 0.622 |
| 20611606 | 4.270 | 0.092 | 0.531 |

## What this does not license

An observational model on one synthetic world family and six seeds, with 26 events. Firth stabilizes a separated coefficient; it does not establish causation, capability, retention, transfer, or a general engine property.
