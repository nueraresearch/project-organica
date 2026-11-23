# Loop retention, strength and formation timing in the loop-only model — post hoc

Generated from `docs/loop_persistence_assertion_model.json` by `python -m benchmarks.loop_persistence_assertion_model --write`. Do not edit by hand.

**Post hoc, not confirmatory.** This extends the confirmed model on the same twelve consumed seeds. It has no preregistration and no verdict. The formation control was added before the controlled model was read.

## Design

- Population: the confirmed block's **177** never-served loop-forming edges (**77** asserted).
- Seeds: **20616101, 20616102, 20616103, 20616104, 20616105, 20616106, 20616107, 20616108, 20616109, 20616110, 20616111, 20616112**; no fresh seed.
- **Retention:** observed loop span divided by the cycles available after first detection, in **(0, 1]**. A loop seen in one cycle is not assigned zero.
- **Strength:** maximum `loop_candidate.strength` over loops containing the edge; strength is the within-loop minimum temporal edge count.
- **Formation:** first loop cycle divided by 120. It controls for when the loop first appeared, because retention's denominator is the cycles available after that point.
- All models are Firth logistic with twelve seed fixed effects. The baseline is the confirmed rank + count model; the persistence model adds retention and strength; the controlled model adds formation. Predictors are per 1 SD.

## Count association

| Model | Count OR | 95% CI | Count beta | In-sample AUC | Brier |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline (confirmed form) | 2.688 | 1.774–4.072 | 0.989 | 0.801 | 0.1798 |
| + retention + strength | 0.609 | 0.292–1.274 | -0.495 | 0.992 | 0.0355 |
| + formation control | 0.714 | 0.333–1.533 | -0.337 | 0.995 | 0.0275 |

The count log-odds coefficient changes by **+150.1%** from baseline to adjusted (positive means attenuation). The adjusted count OR is **0.609** (95% CI **0.292–1.274**, p **1.88e-01**).

**Post-hoc readout: `COUNT ATTENUATES AND REVERSES`.** This is a descriptive label, not a verdict.

The adjusted count OR is below 1, so the association does not merely lose significance: after persistence enters, the point estimate changes sign and its interval includes 1. The in-sample AUC rises to **0.992** and the Brier score falls to **0.0355**, but these are fit statistics on the same rows, not held-out predictions.

## Retention and strength

| Predictor | Model | OR per 1 SD | 95% CI | p | AME |
| --- | --- | ---: | ---: | ---: | ---: |
| Retention | persistence | 8.022 | 2.572–25.019 | 3.33e-04 | +0.105 |
| Strength | persistence | 2031.575 | 38.710–106621.843 | 1.64e-04 | +0.330 |
| Retention | + formation | 14.683 | 3.677–58.643 | 1.43e-04 | +0.131 |
| Strength | + formation | 274.769 | 6.581–11471.400 | 3.18e-03 | +0.275 |
| Formation | + formation | 6.252 | 1.165–33.542 | 3.25e-02 | +0.089 |

Strength's 1-SD step is **10.37** raw units, so its **2031.57** OR per SD is about **2.08** per raw strength unit; retention's 1-SD step is **0.329**, so its OR per +0.1 retention is about **1.88**.

The formation control moves the retention OR from **8.022** to **14.683** (controlled 95% CI **3.677–58.643**, p **1.43e-04**); the controlled formation OR is **6.252** (95% CI **1.165–33.542**). **Formation-control readout: `RETENTION SURVIVES FORMATION CONTROL`.** This is descriptive, not a verdict.

Rank is shown for completeness: baseline OR **1.189** (0.824–1.716), adjusted OR **1.874** (0.816–4.303), controlled OR **1.332** (0.554–3.205).

Strength is not a subtle gradient in this sample. Its upper quartile is almost entirely asserted while its lower quartile is almost entirely not:

| Strength quartile | Range | Edges | Asserted | Mean count | Mean retention |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 5–10 | 44 | 0 | 24.6 | 0.076 |
| 2 | 11–20 | 44 | 7 | 28.7 | 0.340 |
| 3 | 20–26 | 44 | 26 | 32.4 | 0.489 |
| 4 | 26–51 | 45 | 44 | 36.3 | 0.696 |

## Descriptives

| Variable | Min | P25 | Median | P75 | Max | Mean | SD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `direct_count` | 7.000 | 23.000 | 31.000 | 38.000 | 55.000 | 30.537 | 9.969 |
| `retention` | 0.010 | 0.099 | 0.330 | 0.646 | 1.000 | 0.402 | 0.329 |
| `retention_cycles` | 1.000 | 7.000 | 24.000 | 51.000 | 116.000 | 32.226 | 30.068 |
| `strength` | 5.000 | 11.000 | 20.000 | 26.000 | 51.000 | 19.915 | 10.368 |
| `formation_cycle` | 5.000 | 21.000 | 41.000 | 58.000 | 114.000 | 41.362 | 24.358 |
| `formation_fraction` | 0.042 | 0.175 | 0.342 | 0.483 | 0.950 | 0.345 | 0.203 |

## Predictor correlations

| Pair | Pearson r |
| --- | ---: |
| `rank~retention` | -0.106 |
| `rank~strength` | -0.065 |
| `count~rank` | -0.200 |
| `count~retention` | 0.450 |
| `count~strength` | 0.484 |
| `count~formation` | -0.044 |
| `retention~strength` | 0.718 |
| `formation~rank` | 0.178 |
| `formation~retention` | -0.025 |
| `formation~strength` | 0.310 |

## Leave-one-seed-out

| Held out | Baseline count | Adjusted count | Retention | Strength | Controlled count | Controlled retention | Controlled formation |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20616101 | 0.970 | -0.473 | 2.052 | 7.280 | -0.345 | 2.397 | 1.348 |
| 20616102 | 1.013 | -0.398 | 1.966 | 7.290 | -0.069 | 3.116 | 3.687 |
| 20616103 | 1.135 | -0.546 | 2.321 | 8.631 | -0.347 | 2.954 | 1.887 |
| 20616104 | 1.007 | -0.508 | 1.992 | 7.700 | -0.342 | 2.562 | 1.843 |
| 20616105 | 0.932 | -0.540 | 1.995 | 7.412 | -0.389 | 2.585 | 1.762 |
| 20616106 | 0.940 | -0.474 | 2.071 | 7.344 | -0.325 | 2.651 | 1.768 |
| 20616107 | 0.947 | -0.644 | 2.009 | 8.145 | -0.455 | 2.416 | 1.670 |
| 20616108 | 0.882 | -0.469 | 2.148 | 7.714 | -0.318 | 2.759 | 1.872 |
| 20616109 | 1.200 | -0.348 | 1.770 | 7.138 | -0.257 | 2.119 | 1.106 |
| 20616110 | 0.939 | -0.518 | 1.942 | 7.134 | -0.346 | 2.623 | 1.852 |
| 20616111 | 0.946 | -0.499 | 1.888 | 7.817 | -0.357 | 2.388 | 1.736 |
| 20616112 | 0.974 | -0.424 | 2.616 | 6.432 | -0.426 | 4.621 | 3.110 |

## Integrity

| Check | Passes |
| --- | --- |
| `population_unchanged` | yes |
| `events_unchanged` | yes |
| `replay_edges_match` | yes |
| `replay_assertions_match` | yes |
| `retention_finite` | yes |
| `formation_finite` | yes |
| `strength_finite` | yes |
| `baseline_converged` | yes |
| `extended_converged` | yes |
| `controlled_converged` | yes |
| `baseline_reproduces_confirmed` | yes |

## What this does and does not establish

Retention and strength are measured at the edge, not assigned by treatment. The count coefficient falls below zero when they enter, which is consistent with count being a marker for how long and how strongly the loop was present. It does not follow that persistence causes assertion: strength is close to a separating variable here, retention and strength correlate at **0.72**, and the model is observational. The formation control does not attenuate the retention association in this sample; the controlled retention OR is larger than the uncontrolled one, and later formation has its own positive association. That is consistent with timing and retention carrying separate information, but the control is linear, the timing is measured rather than assigned, and onset may proxy for unmeasured loop quality. The sample is small, the seeds are reused and the world family is synthetic.

A post-hoc observational extension in one synthetic world family on already-consumed seeds. Retention and strength are measured, not manipulated. The formation control is a linear covariate for first-detection timing, not a randomisation or an identification strategy. Attenuation is consistent with a proxy reading but does not establish mediation, causation, capability, transfer or a general engine property.
