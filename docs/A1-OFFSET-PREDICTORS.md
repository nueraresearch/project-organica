# A1 block-offset predictors

Generated from `docs/a1_offset_predictors.json` by `python -m benchmarks.a1_offset_predictors --write`. Do not edit by hand.

**Descriptive predictor comparison, not an A1 result.** 12 block-by-cap cells and 72 seed rows at caps **20/40/80/112**. No target, freeze, grant or A1 cell.

## Result

Candidate size can replace the free block offset: its cell LOO RMSE is 0.0184 against 0.0193 for the free offset, and its seed LOO is 0.0667 against 0.0668. K completeness alone is similar at cell level (0.0189) but much worse across seeds (0.0865), and adding it to candidate size does not improve seed LOO (0.0669 vs 0.0667). Within larger-28, K completeness and A coverage correlate only 0.079, while candidate size and A coverage correlate -0.012. Candidate size is the usable offset predictor; K completeness is a correlated regime marker, not an independent predictor.

## Model comparison

| Model | Parameters | Cell LOO RMSE | Cell LOO max | Seed LOO RMSE | Seed LOO max |
| --- | ---: | ---: | ---: | ---: | ---: |
| free_block_offset | 4 | 0.0193 | 0.0333 | 0.0668 | 0.2353 |
| candidate_size | 3 | 0.0184 | 0.0314 | 0.0667 | 0.2415 |
| k_completeness | 3 | 0.0189 | 0.0314 | 0.0865 | 0.2218 |
| candidate_plus_k | 4 | 0.0162 | 0.0312 | 0.0669 | 0.2412 |

Candidate size replaces two block dummies with one continuous predictor and uses one fewer parameter. K completeness alone does not improve seed prediction; the joint model is collinear.

## Offsets

| Block | Free offset | Candidate-size prediction at cap 0 |
| --- | ---: | ---: |
| current-16 | 0.4200 | 0.4137 |
| fresh-16 | 0.4065 | 0.4128 |
| larger-28 | 0.0688 | 0.0688 |

The candidate-size prediction reproduces the large larger-28 offset; it does not distinguish current-16 from fresh-16, whose sizes are nearly identical.

## Within larger-28

| Relation | Correlation |
| --- | ---: |
| A coverage vs K completeness | 0.079 |
| A coverage vs log candidates | -0.012 |
| K completeness vs log candidates | -0.866 |

| Cap | A vs K completeness | A vs log candidates |
| ---: | ---: | ---: |
| 20 | 0.405 | -0.124 |
| 40 | 0.312 | -0.044 |
| 80 | 0.062 | 0.197 |
| 112 | 0.420 | -0.166 |

Within the larger block neither quantity carries a stable seed-level signal. The between-block offset is a candidate-space effect that the block label summarizes; K completeness is too collinear with that label to be an independent predictor.

## Reading

Candidate-space size is the simpler replacement for the free block offset. K completeness is a regime marker: it separates 16-tag from larger-28, but it does not predict A coverage within larger-28 and does not improve seed-level prediction once size is included.

The joint model's slightly lower cell LOO is not evidence of two independent predictors: its coefficients are large and unstable because candidate size and K completeness are strongly collinear.

## What this does not claim

A descriptive predictor comparison on 12 fixed block-by-cap cells and 72 seed rows from no-arm runs. Candidate size and K completeness are not intervened; the artifact does not show that changing either would move the offset, and it is not a treatment, target viability or successor.
