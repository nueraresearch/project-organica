# Loop-only assertion model — confirmatory

Generated from `docs/loop_only_assertion_model.json` by `python -m benchmarks.loop_only_assertion_model --write`. Do not edit by hand.

**Verdict: `CONFIRMED`.** The design was frozen in `docs/loop_only_assertion_model_prereg.json` before the fresh block ran.

## Design

- Seeds: **20616101, 20616102, 20616103, 20616104, 20616105, 20616106, 20616107, 20616108, 20616109, 20616110, 20616111, 20616112**.
- **120** cycles, cap **40**, PHASE_ACQUISITION, repaired full-universe rank capture.
- Population: never-served world edges that ever formed a reported loop.
- Model: Firth logistic; rank and count per 1 SD; twelve seed fixed effects.
- Primary criterion: count OR > 1 and its 95% CI lower bound > 1.

## Result

| Quantity | Exploratory Q4 | Fresh block |
| --- | ---: | ---: |
| Loop-forming edges | 61 | 177 |
| Asserted events | 26 | 77 |
| Count OR | 1.69 | 2.69 |
| Count 95% CI | 0.85–3.36 | 1.77–4.07 |
| Rank OR | 1.09 | 1.19 |
| Rank 95% CI | 0.62–1.90 | 0.82–1.72 |
| AUC | — | 0.801 |
| Brier | — | 0.1798 |

## Count association

The primary estimate is the Firth count OR per 1 SD: **2.69** (95% CI **1.77–4.07**, p **3.09e-06**). The point estimate is above 1; the interval excludes 1.

Average marginal effect of count +1 SD: **+0.188** probability.

## Rank (secondary)

Rank OR per 1 SD: **1.19** (95% CI **0.82–1.72**). No rank-based verdict was pre-specified; this is reported descriptively.

## Gates

| Gate | Passes |
| --- | --- |
| `M1_population` | yes |
| `M2_rank_coverage` | yes |
| `M3_no_duplicate` | yes |
| `M4_seed_levels` | yes |
| `M5_convergence` | yes |
| `M6_complete` | yes |
| `M7_loop_only` | yes |

## Leave-one-seed-out

| Held out | Rank beta | Count beta |
| ---: | ---: | ---: |
| 20616101 | 0.253 | 0.970 |
| 20616102 | 0.158 | 1.013 |
| 20616103 | 0.189 | 1.135 |
| 20616104 | 0.293 | 1.007 |
| 20616105 | 0.152 | 0.932 |
| 20616106 | 0.198 | 0.940 |
| 20616107 | 0.070 | 0.947 |
| 20616108 | 0.077 | 0.882 |
| 20616109 | 0.145 | 1.200 |
| 20616110 | 0.142 | 0.939 |
| 20616111 | 0.207 | 0.946 |
| 20616112 | 0.193 | 0.974 |

## Per seed

| Seed | Never served | Loop-forming | Asserted | Loop-forming asserted |
| ---: | ---: | ---: | ---: | ---: |
| 20616101 | 46 | 17 | 12 | 12 |
| 20616102 | 44 | 10 | 6 | 6 |
| 20616103 | 43 | 21 | 7 | 6 |
| 20616104 | 34 | 12 | 7 | 7 |
| 20616105 | 40 | 16 | 4 | 4 |
| 20616106 | 29 | 5 | 2 | 2 |
| 20616107 | 33 | 18 | 8 | 8 |
| 20616108 | 35 | 14 | 8 | 8 |
| 20616109 | 35 | 23 | 6 | 6 |
| 20616110 | 35 | 16 | 9 | 9 |
| 20616111 | 49 | 13 | 4 | 4 |
| 20616112 | 37 | 12 | 5 | 5 |

## What this does and does not establish

This is a confirmatory subgroup test on a fresh twelve-seed block, not a capability or causal result. It conditions on loop formation, so it does not test whether loops cause assertion or whether retention matters. The sample is still modest, the world family is synthetic, and the model is observational.

A twelve-seed observational subgroup model in one synthetic world family. It does not establish causation, capability, retention, transfer or a general engine property.
