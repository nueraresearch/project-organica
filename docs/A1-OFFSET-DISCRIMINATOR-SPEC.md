# A1 offset-discriminator construction

Generated from `docs/a1_offset_discriminator_spec.json` by `python -m benchmarks.a1_offset_discriminator_spec --write`. Do not edit by hand.

**Candidate-space spec, not an A1 result.** No engine replay, no target, freeze, grant or A1 cell. The predicted offsets are projections from the frozen fits, not measurements.

## Result

Within the committed compositional law the offset predictors cannot be separated: tags-per-cell **k** fixes the alphabet **4k** and the candidate count together, so measured blocks sit at **16/2.0**, **36/3.0**, **63.7/3.98** and **167/5.95** (candidates, density) — density is a function of candidate count, and no setting of **k** moves one without the other. The pair-split construction breaks that identity by fixing the per-regime pair width at **active=4** while letting the alphabet grow: **split-32** (32 tags) yields **63.8** candidates at density **1.995**, and **split-48** (48 tags) yields **63.8** at density **1.330**, both within **5.0%** of the 16-tag candidate count of **63.8**. The frozen size model therefore assigns them nearly the same offset (**0.413** against **0.413**, a gap of **0.000**), while the frozen density model assigns **0.761** and **0.878** — a predicted difference of **0.116** against the size model's **0.000**. The differential between the two split blocks is the test: it is **6×** the candidate-size cell LOO, and because both blocks come from the same split family, family-level shifts cancel in the difference.

## The construction

| Block | Tags per cell | Active per regime | Alphabet | Seeds | Candidates (mean) | Density |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| split-32 | 8 | 4 | 32 | 6 | 63.8 | 1.995 |
| split-48 | 12 | 4 | 48 | 6 | 63.8 | 1.330 |
| current-16 | 4 | - | 16 | 6 | 63.7 | 3.979 |
| fresh-16 | 4 | - | 16 | 6 | 63.8 | 3.990 |
| larger-28 | 7 | - | 28 | 6 | 166.7 | 5.952 |

The split rule cuts each cell's tags into consecutive `active` groups and lets the regime index pick the group, so every declared tag is exercised while the per-regime pair space stays `active` wide.

## Why the committed family cannot separate the predictors

Within the compositional law, tags-per-cell `k` sets both the alphabet (`4k`) and the candidate count, so density moves with candidate count: 16 tags gives 63.7 candidates at 3.98 per tag, 28 tags gives 167 at 5.95. Every `k` lands on the same one-dimensional locus.

## Measured candidates

| Block | Seed | Tags | Candidates | log candidates | Density |
| --- | ---: | ---: | ---: | ---: | ---: |
| split-32 | 20690101 | 32 | 63 | 4.143 | 1.969 |
| split-32 | 20690102 | 32 | 64 | 4.159 | 2.000 |
| split-32 | 20690103 | 32 | 64 | 4.159 | 2.000 |
| split-32 | 20690104 | 32 | 64 | 4.159 | 2.000 |
| split-32 | 20690105 | 32 | 64 | 4.159 | 2.000 |
| split-32 | 20690106 | 32 | 64 | 4.159 | 2.000 |
| split-48 | 20690101 | 48 | 63 | 4.143 | 1.312 |
| split-48 | 20690102 | 48 | 64 | 4.159 | 1.333 |
| split-48 | 20690103 | 48 | 64 | 4.159 | 1.333 |
| split-48 | 20690104 | 48 | 64 | 4.159 | 1.333 |
| split-48 | 20690105 | 48 | 64 | 4.159 | 1.333 |
| split-48 | 20690106 | 48 | 64 | 4.159 | 1.333 |

## Predicted offsets under the frozen models

| Block | log candidates | Density | Size-model offset | Density-model offset | Gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| split-32 | 4.156 | 1.995 | 0.413 | 0.761 | +0.349 |
| split-48 | 4.156 | 1.330 | 0.413 | 0.878 | +0.465 |
| current-16 | 4.154 | 3.979 | 0.414 | 0.414 | +0.000 |
| fresh-16 | 4.156 | 3.990 | 0.413 | 0.412 | -0.000 |
| larger-28 | 5.116 | 5.952 | 0.069 | 0.069 | +0.000 |

## The differential

| Quantity | Value |
| --- | ---: |
| Blocks | split-32 vs split-48 |
| log candidates | 4.156 / 4.156 |
| density | 1.995 / 1.330 |
| size model predicts | +0.000 |
| density model predicts | -0.116 |
| measured | not measured |

## Identification

| Quantity | Value |
| --- | ---: |
| Blocks in the design | 5 |
| Coefficient SE (constant, log candidates, density) | 0.1248, 0.0330, 0.0077 |
| Residual sigma used | 0.01837 |
| log candidates in design | 4.154 to 5.116 |
| density in design | 1.330 to 5.952 |
| fitted log candidates | 4.154 to 5.116 |
| fitted density | 3.979 to 5.952 |

## Decision rule

| Rule | Value |
| --- | --- |
| statistic | measured offset difference, split-32 minus split-48 |
| size model | near zero (predicted 0.000000) |
| density model | negative, about -0.116 |
| if abs below | 0.05 -> candidate count tracks the level |
| if abs above | 0.09 with the density sign -> density tracks the level |
| otherwise | neither summary is identified by this pair |
| power | about 3 standard errors at six seeds per block under the fitted seed-level RMSE 0.067 |

## Controls

| Control | Expected | Observed | Pass |
| --- | --- | --- | --- |
| the committed 16-tag law reproduces 20630101 | 64 | 64 | yes |
| the committed 16-tag law reproduces 20630102 | 63 | 63 | yes |
| the committed 16-tag law reproduces 20650101 | 64 | 64 | yes |
| the committed 28-tag law reproduces 20660101 | 169 | 169 | yes |
| split-32 uses every declared tag | 32 | 32 | yes |
| split-48 uses every declared tag | 48 | 48 | yes |
| split-32 matches the 16-tag candidate count | |log gap| <= 0.05 | 0.0 | yes |
| split-48 matches the 16-tag candidate count | |log gap| <= 0.05 | 0.0 | yes |

## Limits

- The split blocks are a different world family from the three fitted blocks: their absolute level is not comparable to the fitted blocks except through the predictors.
- The differential test cancels family-level shifts only because both split blocks share the split rule, the active width and the regime law.
- Density 1.31-1.96 lies below the fitted density range 3.98-5.95, so the density model extrapolates downward while the size model interpolates.
- Candidate count is fixed by the fixed candidate rule; a different rule would move both features together again.
- No coverage, offset or A/K value is measured here; every predicted number is a projection from the frozen fits.

## What this does not claim

A candidate-space specification with measured candidate counts. It is not a treatment, a target, a freeze, a grant, an A1 cell or evidence that either predictor is the mechanism. The predicted offsets are projections from frozen fits, not measurements.
