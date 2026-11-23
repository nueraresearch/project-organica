# NEVER-SERVED-ASSERTION-MODEL-1 — preregistration

**Status.** FROZEN, FIT. Generated from `docs/never_served_assertion_model_prereg.json`; never edited by hand.

| Field | Value |
| --- | --- |
| Preregistration | `NEVER-SERVED-ASSERTION-MODEL-1` |
| Freeze date | 2026-11-12 |
| Population | Every world edge with served=false in .scratch/carrier_census.json: 180 edges over seeds 20611601-20611606, of which 26 are asserted. |
| Outcome | asserted=true in the final structure, from the carrier census |
| Complete cases | An edge must have a finite minimum full-universe rank; one count-4, never-asserted, no-loop edge has no rank and is excluded. The fit therefore uses 179 edges and 26 events. |
| Model | logit P(asserted) = b0 + b_loop*loop + b_rank*z(log2(min_rank)) + b_count*z(direct_count) + seed fixed effects |
| Estimator | Firth penalized likelihood (Jeffreys prior), because loop is quasi-separated: all 26 events have loop=1 and all 118 complete-case loop=0 edges are non-events. |
| Result | `docs/never_served_assertion_model.json` |

## Predictors

| Name | Definition |
| --- | --- |
| `loop` | Binary ever_loop from the census: at least one reported loop candidate contains the edge in either orientation in any of the 120 cycles. |
| `rank` | Minimum full-universe prediction rank across all 120 cycles, measured at cap 40 with the repaired observer. Lower is better. Analyzed as log2(min_rank), then standardized over the 179 complete cases. |
| `count` | Direct temporal count at the end of the run, from the census; standardized over the 179 complete cases. |
| `seed` | Six-level fixed effect; treatment coded with 20611601 as reference. |

No interactions. No variable selection. Rank and count are standardized over the complete cases; the standardization does not use the outcome.

## Why Firth

The ordinary MLE for the loop coefficient diverges under this zero cell. Firth returns a finite estimate; it does not turn the zero cell into evidence of an infinite effect.

The penalty is 0.5 * log|X' W X|, with W = diag(p*(1-p)).

## Inference

Firth Wald 95% confidence intervals for the three reported coefficients, from the inverse information at the penalized estimate.

exp(beta): loop is a 0/1 contrast; rank and count are per 1 SD. A rank odds ratio below 1 means a worse (larger) rank is associated with lower assertion.

Average marginal effects on the probability scale, computed at the observed covariates: loop 1 vs 0; rank +1 SD; count +1 SD.

Leave-one-seed-out refits with the same full-sample standardization; the range of each coefficient is reported. No cluster-robust SE claim is made.

The model is descriptive. No coefficient-significance rule selects a verdict, and no causal claim is licensed.

## Expected directions

| Predictor | Direction |
| --- | --- |
| `loop` | positive association; the sample has no asserted edge without a loop |
| `rank` | negative coefficient for log2 rank; a worse rank should reduce assertion |
| `count` | positive association; more direct transitions should increase assertion |

## Gates

| Gate | Rule |
| --- | --- |
| `M1_population` | 180 never-served edges, 26 asserted; no duplicate seed-edge rows |
| `M2_rank_coverage` | at least 95% of never-served edges have a finite minimum rank |
| `M3_label_replay` | the rank replay reproduces every census asserted and ever_loop label |
| `M4_loop_variation` | both loop levels are present; the zero cell is disclosed, not hidden |
| `M5_convergence` | the Firth fit converges with finite coefficients and information matrix |
| `M6_complete_predictors` | every fitted row has loop, rank and count; no silent row loss |
| `M7_seed_levels` | all six seeds contribute rows and the seed fixed effect is full rank |

## Reading

Report the three adjusted odds ratios, their intervals, the average marginal effects, the separation table, and the leave-one-seed-out ranges. A coefficient whose interval includes 1 is not read as an association.

## What this does not license

An observational model on one synthetic world family and six seeds, with 26 events. Firth stabilizes a separated coefficient; it does not establish causation, capability, retention, transfer, or a general engine property.
