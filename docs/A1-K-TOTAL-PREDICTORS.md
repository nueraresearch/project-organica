# A1 absolute K predictors — what tracks total K?

**ID:** `A1-K-TOTAL-PREDICTORS-1`
**Status:** `DESCRIPTIVE — WHAT TRACKS ABSOLUTE K; NO TARGET, NO THRESHOLD, NO RUN`

**This is not an A1 result.** It is a read-only join of eighteen no-arm seeds across three blocks. It selects no target, changes no threshold and runs no A1 cell.

## The question

K density is a ratio. The constrained quantity is the **absolute K count** per seed. This artifact asks which measured feature tracks that count across worlds, not which rows happen to have K.

## Per-seed rows

| Block | Seed | Edges | A | K | Mean U | Median support | Support >=4 | Flip-P share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | `20630101` | 64 | 44 | 44 | 14.14 | 4.00 | 34 | 50.0% |
| current-16 | `20630102` | 63 | 44 | 31 | 15.19 | 4.00 | 40 | 50.8% |
| current-16 | `20630103` | 64 | 52 | 39 | 15.03 | 4.00 | 33 | 50.0% |
| current-16 | `20630104` | 64 | 43 | 35 | 15.38 | 4.00 | 35 | 50.0% |
| current-16 | `20630105` | 64 | 49 | 43 | 16.00 | 4.00 | 35 | 50.0% |
| current-16 | `20630106` | 63 | 49 | 36 | 15.60 | 4.00 | 32 | 50.8% |
| fresh-16 | `20650101` | 64 | 49 | 40 | 15.78 | 3.00 | 30 | 50.0% |
| fresh-16 | `20650102` | 64 | 46 | 37 | 14.84 | 4.00 | 33 | 50.0% |
| fresh-16 | `20650103` | 64 | 54 | 46 | 15.67 | 3.00 | 31 | 50.0% |
| fresh-16 | `20650104` | 64 | 53 | 42 | 16.09 | 4.00 | 36 | 50.0% |
| fresh-16 | `20650105` | 63 | 31 | 39 | 15.52 | 4.00 | 35 | 49.2% |
| fresh-16 | `20650106` | 64 | 46 | 38 | 15.50 | 4.00 | 33 | 50.0% |
| larger-28 | `20660101` | 169 | 59 | 23 | 5.77 | 2.00 | 6 | 53.8% |
| larger-28 | `20660102` | 167 | 50 | 40 | 5.90 | 2.00 | 13 | 52.7% |
| larger-28 | `20660103` | 172 | 57 | 42 | 5.70 | 1.00 | 11 | 51.7% |
| larger-28 | `20660104` | 165 | 67 | 55 | 5.81 | 2.00 | 17 | 52.1% |
| larger-28 | `20660105` | 169 | 66 | 47 | 5.98 | 1.00 | 12 | 48.5% |
| larger-28 | `20660106` | 158 | 54 | 37 | 5.87 | 2.00 | 11 | 51.3% |

## Correlations with absolute K

Spearman rank correlation, pooled across 18 seeds and within each 6-seed block. A bootstrap 95% interval is shown for the pooled value; it resamples seeds, not worlds.

| Feature | Pooled rho | 95% interval | Current-16 | Fresh-16 | Larger-28 | Pre-run? |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| candidate_edges | 0.32 | -0.22 to 0.74 | 0.62 | 0.13 | 0.03 | yes |
| mean_U | 0.04 | -0.48 to 0.55 | -0.20 | 0.83 | 0.20 | yes |
| median_U | -0.06 | -0.57 to 0.46 | -0.03 | 0.29 | 0.00 | yes |
| mean_support_36 | -0.20 | -0.70 to 0.38 | -0.14 | -0.37 | 0.09 | yes |
| median_support_36 | -0.33 | -0.73 to 0.19 | — | -0.62 | -0.41 | yes |
| support_ge4_edges | -0.12 | -0.65 to 0.43 | -0.41 | -0.12 | 0.78 | yes |
| flip_p_share | -0.27 | -0.74 to 0.27 | -0.62 | 0.13 | -0.43 | yes |
| A_available | 0.42 | -0.15 to 0.83 | 0.35 | 0.81 | 0.60 | no |

## Leave-one-world-out prediction

Each model is fit on two blocks and predicts the third. MAE is in K rows per seed. The mean baseline predicts the training-block K mean for every held-out seed.

| Model | LOFO MAE | Current-16 | Fresh-16 | Larger-28 |
| --- | ---: | ---: | ---: | ---: |
| mean baseline | 4.81 | 4.50 | 2.33 | 7.61 |
| candidate_edges | 177.21 | 4.45 | 2.67 | 524.52 |
| mean_U | 6.48 | 4.48 | 2.83 | 12.15 |
| median_U | 5.45 | 4.46 | 2.81 | 9.09 |
| mean_support_36 | 12.65 | 4.45 | 2.63 | 30.89 |
| median_support_36 | 5.81 | 4.05 | 2.44 | 10.93 |
| support_ge4_edges | 7.96 | 4.95 | 2.32 | 16.60 |
| flip_p_share | 5.64 | 4.49 | 3.04 | 9.38 |
| A_available | 4.65 | 4.05 | 3.66 | 6.26 |

**Lowest observed MAE:** `A_available` at **4.65** K rows, against a mean baseline of **4.81**; the gain is only **0.16** rows. The best pre-run feature is `median_U` at **5.45**, **0.64 rows worse** than the baseline. These are the lowest observed errors, not a validated model.

## Reading

All entries are associations. A is an output of the same baseline, not a design lever. A low leave-one-world-out error is predictive only for these three blocks.

The result is mostly negative:

- `A_available` is the best model, but it is an output of the same baseline and improves on the mean baseline by only **0.16** K rows.
- No pre-run feature beats the mean baseline out of world; the best is **0.64 rows worse**.
- `candidate_edges` fails catastrophically out of world (LOFO MAE **177.21**) and has rho **0.03** inside the 28-tag block: edge count is not a predictor of total K.
- Support and U summaries are inconsistent across blocks: their pooled intervals cross zero and their within-block signs do not agree.

So the current answer is: **absolute K is seed-specific under these structural summaries.** This rejects `candidate_edges`, mean U and the pre-U support summaries as simple cross-world predictors; it does not prove no predictor exists.

The next diagnostic should measure the carrier process directly rather than another summary of the same rows.

## Limits

- Eighteen seeds and three world blocks; this is not a fitted causal model.
- The current and fresh 16-tag blocks share a world family but not seeds; the 28-tag block differs in tag count and mapping.
- Support is measured before U (cycles 20-35) and is not a latent probability.
- K is a no-arm availability flag, not a treatment or a rate.
- A leave-one-world-out error is a small-sample descriptive check, not a validated predictor.
- No target, threshold, freeze, grant or run changed.

**Not evidence:** A read-only join of existing no-arm rows. It selects no target, changes no protocol and runs no A1 cell.

## Reproduce

```bash
python -m benchmarks.a1_k_total_predictors --check
python -m benchmarks.a1_k_total_predictors --self-test
```
