# Never-served assertion model — replication

Generated from `docs/never_served_assertion_model_replication.json` by `python -m benchmarks.never_served_assertion_model_replication --write`. Do not edit by hand.

**Verdict: `REPLICATED`.** The model and gates were frozen in `docs/never_served_assertion_model_replication_prereg.json` before the replay.

## Design

- Seeds: **20613101, 20613102, 20613103, 20613104, 20613105, 20613106** — the existing provenance block, fresh relative to Q4 but not a new draw.
- **120** cycles, cap **40**, PHASE_ACQUISITION schedule, one replay per seed.
- Population: every world edge with zero direct served windows.
- `min_rank`: minimum 1-based position in the repaired observer's full pre-cap universe.
- `ever_loop`: any reported loop path containing the edge in either orientation.
- Direct count: final temporal transition count.

## Result

| Term | Original Q4 | Fresh block |
| --- | ---: | ---: |
| Population | 179 complete / 180 | 212 complete / 212 |
| Events | 26 | 26 |
| Loop OR | 75.10 | 134.78 |
| Loop 95% CI | 6.66–847.08 | 8.09–2246.62 |
| Rank OR | 1.09 | 0.91 |
| Rank 95% CI | 0.61–1.95 | 0.48–1.73 |
| Count OR | 1.96 | 1.26 |
| Count 95% CI | 0.87–4.40 | 0.70–2.24 |
| AUC | 0.925 | 0.928 |
| Brier | 0.074 | 0.0664 |

## Separation

| | Asserted | Not asserted |
| --- | ---: | ---: |
| Loop formed | 26 | 62 |
| No loop | 0 | 124 |

## Post-hoc identity adjustment

The preregistered model did not include source or target identity. This check adds categorical fixed effects for both tags to the same Firth specification, holding seed fixed as before. It is post hoc and does not change the verdict.

| Term | Unadjusted | + source/target identity |
| --- | ---: | ---: |
| Loop OR | 134.78 | 24.58 |
| Loop 95% CI | 8.09–2246.62 | 3.72–162.63 |
| Rank OR | 0.91 | 1.22 |
| Rank 95% CI | 0.48–1.73 | 0.57–2.60 |
| Count OR | 1.26 | 1.39 |
| Count 95% CI | 0.70–2.24 | 0.61–3.19 |
| In-sample AUC | 0.928 | 1.000 |
| Brier | 0.0664 | 0.0171 |

The count point estimate moves from **1.26** to **1.39**, but its interval still includes 1. The count association was already unsupported, and identity adjustment does not create one. Loop attenuates from **134.78** to **24.58** but remains positive; rank remains null.

The identity model has **39** parameters (30 source/target indicators and 9 other terms) for **212** rows and **26** events. Its in-sample AUC of **1.000** is overfit and is not a predictive comparison.

## Gates

| Gate | Passes |
| --- | --- |
| `M1_population` | yes |
| `M2_rank_coverage` | yes |
| `M3_provenance_replay` | yes |
| `M4_loop_variation` | yes |
| `M5_convergence` | yes |
| `M6_complete_predictors` | yes |
| `M7_seed_levels` | yes |

## Average marginal effects

| Contrast | Probability difference |
| --- | ---: |
| Loop 1 vs 0 | +0.295 |
| Rank +1 SD | -0.007 |
| Count +1 SD | +0.018 |

## Leave-one-seed-out

| Held out | Loop beta | Rank beta | Count beta |
| ---: | ---: | ---: | ---: |
| 20613101 | 4.986 | -0.321 | 0.159 |
| 20613102 | 5.011 | -0.059 | 0.079 |
| 20613103 | 4.869 | -0.129 | 0.233 |
| 20613104 | 3.863 | -0.079 | 0.193 |
| 20613105 | 4.645 | 0.154 | 0.323 |
| 20613106 | 4.703 | -0.131 | 0.314 |

## Per seed

| Seed | Asserted world | Served world | Never served | Never-served asserted |
| ---: | ---: | ---: | ---: | ---: |
| 20613101 | 30 | 81 | 31 | 1 |
| 20613102 | 49 | 75 | 37 | 5 |
| 20613103 | 37 | 79 | 33 | 1 |
| 20613104 | 50 | 80 | 32 | 8 |
| 20613105 | 23 | 72 | 40 | 6 |
| 20613106 | 29 | 73 | 39 | 5 |

## What this does and does not establish

The replay uses seeds that already carried the provenance replication, so it tests whether the model reproduces on that existing fresh block; it is not a new independent draw. The model is descriptive: the loop coefficient is quasi-separated if the no-loop asserted cell remains empty, and its interval is not a precise effect. No causal, capability, retention or engine-effect claim follows.

A six-seed replication on one synthetic world family. The seeds were already used for the provenance split, so this is not a new independent draw. It does not establish causation, capability, retention or a general engine property.
