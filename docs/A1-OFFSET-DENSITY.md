# A1 block-offset density predictors

Generated from `docs/a1_offset_density.json` by `python -m benchmarks.a1_offset_density --write`. Do not edit by hand.

**Descriptive predictor comparison, not an A1 result.** 12 block-by-cap cells and 72 seed rows at caps **20/40/80/112**. No target, freeze, grant or A1 cell.

Density is **candidate edges per tag**: 64/16 = **4.00** for both 16-tag blocks and 167/28 ≈ **5.96** for larger-28.

## Result

Density predicts the offset about as well as candidate size at cell level and slightly worse across seeds; with 12 cells and 72 rows none of the three continuous summaries separates from the others, and only K completeness is clearly worse. Candidate density reaches cell LOO 0.0182 and seed LOO 0.0689, against 0.0184 and 0.0667 for candidate size, 0.0193 and 0.0668 for the free block offset, and 0.0189 and 0.0865 for K completeness. The cell-level edge over size (0.0002) and the seed-level gap (0.0023) are both small against the fits' own error. Adding density to size does not help: cell LOO moves from 0.0184 to 0.0193 and seed LOO from 0.0667 to 0.0663, with coefficients [-9.42916961, 4.76918983, -2.5031062, 0.04698668], because density is candidate count divided by a block constant. Across the three blocks the pairs run current-16 (4.1536, 3.9792); fresh-16 (4.1563, 3.9896); larger-28 (5.1156, 5.9524), so every monotone block summary separates the 16-tag blocks from larger-28 equally well. Within larger-28, A coverage correlates -0.013 with density, -0.012 with log candidate size and 0.079 with K completeness, while density and size correlate 1.000. Density is an equally admissible label, not a better one: the data cannot choose between counting candidates and measuring how full the alphabet is, and that choice needs a design that varies one while holding the other.

## Model comparison

| Model | Parameters | Cell LOO RMSE | Cell LOO max | Seed LOO RMSE | Seed LOO max |
| --- | ---: | ---: | ---: | ---: | ---: |
| free_block_offset | 4 | 0.0193 | 0.0333 | 0.0668 | 0.2353 |
| candidate_size | 3 | 0.0184 | 0.0314 | 0.0667 | 0.2415 |
| candidate_density | 3 | 0.0182 | 0.0308 | 0.0689 | 0.2445 |
| k_completeness | 3 | 0.0189 | 0.0314 | 0.0865 | 0.2218 |
| size_plus_density | 4 | 0.0193 | 0.0333 | 0.0663 | 0.2389 |
| size_plus_k | 4 | 0.0162 | 0.0312 | 0.0669 | 0.2412 |
| density_plus_k | 4 | 0.0160 | 0.0303 | 0.0693 | 0.2454 |

## Block-level collinearity

| Block | Mean log candidates | Mean density (edges per tag) |
| --- | ---: | ---: |
| current-16 | 4.1536 | 3.9792 |
| fresh-16 | 4.1563 | 3.9896 |
| larger-28 | 5.1156 | 5.9524 |

All three blocks are ordered the same way by either quantity, so three points cannot distinguish them.

## Within larger-28

| Relation | Correlation |
| --- | ---: |
| A coverage vs density | -0.013 |
| A coverage vs log candidates | -0.012 |
| A coverage vs K completeness | 0.079 |
| Density vs log candidates | 1.000 |
| Density vs K completeness | -0.871 |

## Reading

Density is a legitimate replacement for the block label and ties with candidate size; the choice between them is not identifiable here, and neither carries seed-level signal inside larger-28. K completeness remains the only one of the three that fails the seed-level comparison.

## What this does not claim

A descriptive predictor comparison on 12 fixed block-by-cap cells and 72 seed rows from no-arm runs. Density and size are not intervened, are collinear across three blocks, and cannot be separated by this design; the artifact does not show that changing either would move the offset, and it is not a treatment, target viability or successor.
