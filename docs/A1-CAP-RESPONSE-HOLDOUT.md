# A1 cap-response holdout

Generated from `docs/a1_cap_response_holdout.json` by `python -m benchmarks.a1_cap_response_holdout --write`. Do not edit by hand.

**Descriptive held-out prediction, not an A1 result.** The same 18 no-arm seeds at prediction caps **28/64/96/128**, outside the **20/40/80/112** fit. No target, freeze, grant or A1 cell.

## Result

The held-out caps do not separate interpolation from extrapolation over this range. At caps 28, 64, 96, between fitted caps, the frozen shared curve has RMSE 0.0139 (max 0.0237) over 9 cells, inside its own leave-one-cell-out scale of 0.0193. At cap 128, one step above the fitted range, the RMSE is 0.0142 (max 0.0223) over 3 cells, against 0.0139 interpolated, so one step beyond the fit does not degrade measurably. The candidate-size offset is comparable (0.0151 interpolated, 0.0131 at cap 128). Two bounds apply. Cap 128 sits at 84% of current-16's saturation cap (152) and 80% of fresh-16's (160), and the 16-tag cells at 96 and 128 already fall below the curve (fresh -0.024 at 96, current -0.022 at 128), which is flattening near the ceiling rather than a curve that keeps rising; the fit is not admissible past those caps.

The block holdout shows where the offset model can and cannot stand in for the block label. Holding out current-16 or fresh-16 leaves two blocks whose candidate sizes bracket the held-out one, and the curve plus size offset interpolates them at RMSE 0.0216 and 0.0197 against its own held-out scale of 0.0193. Holding out larger-28 leaves only the two 16-tag blocks, whose log candidate sizes differ by 0.0026; the fitted size coefficient is -5.17 against an intercept of 21.89 and predicts a coverage of -4.33, so that direction is not identified, and its RMSE is a rank-deficiency artifact rather than an extrapolation error.

## Held-out caps

| Cap | Kind | RMSE | Max | Mean residual | Candidate-size RMSE |
| ---: | --- | ---: | ---: | ---: | ---: |
| 28 | interpolation | 0.0142 | 0.0172 | +0.0043 | 0.0161 |
| 64 | interpolation | 0.0067 | 0.0111 | +0.0039 | 0.0059 |
| 96 | interpolation | 0.0183 | 0.0237 | -0.0091 | 0.0198 |
| 128 | extrapolation | 0.0142 | 0.0223 | -0.0084 | 0.0131 |

Reference scale from the committed fit: in-sample RMSE **0.0131**, leave-one-cell-out RMSE **0.0193**.

| | Cells | RMSE | Max |
| --- | ---: | ---: | ---: |
| Interpolation (28/64/96) | 9 | 0.0139 | 0.0237 |
| Extrapolation (128) | 3 | 0.0142 | 0.0223 |

## Held-out cells

| Block | Cap | Kind | Observed | Predicted | Residual | Size prediction | Size residual |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| current-16 | 28 | interpolation | 0.6859 | 0.6687 | +0.0172 | 0.6624 | +0.0235 |
| current-16 | 64 | interpolation | 0.7985 | 0.7959 | +0.0026 | 0.7896 | +0.0089 |
| current-16 | 96 | interpolation | 0.8639 | 0.8804 | -0.0165 | 0.8741 | -0.0102 |
| current-16 | 128 | extrapolation | 0.9293 | 0.9516 | -0.0223 | 0.9453 | -0.0160 |
| fresh-16 | 28 | interpolation | 0.6653 | 0.6551 | +0.0102 | 0.6614 | +0.0039 |
| fresh-16 | 64 | interpolation | 0.7934 | 0.7824 | +0.0111 | 0.7887 | +0.0048 |
| fresh-16 | 96 | interpolation | 0.8432 | 0.8668 | -0.0237 | 0.8732 | -0.0300 |
| fresh-16 | 128 | extrapolation | 0.9294 | 0.9381 | -0.0086 | 0.9444 | -0.0149 |
| larger-28 | 28 | interpolation | 0.3031 | 0.3175 | -0.0144 | 0.3175 | -0.0143 |
| larger-28 | 64 | interpolation | 0.4427 | 0.4447 | -0.0020 | 0.4447 | -0.0020 |
| larger-28 | 96 | interpolation | 0.5422 | 0.5292 | +0.0130 | 0.5292 | +0.0130 |
| larger-28 | 128 | extrapolation | 0.6062 | 0.6004 | +0.0058 | 0.6004 | +0.0058 |

## Block holdout

Fit on the other two blocks' eight committed cells, predict the held-out block's four cells from its candidate size.

| Held-out block | Status | Training log spread | RMSE | Max | Cap 20 | Cap 40 | Cap 80 | Cap 112 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | estimated | 0.9594 | 0.0216 | 0.0339 | +0.0257 | +0.0339 | -0.0008 | -0.0082 |
| fresh-16 | estimated | 0.9620 | 0.0197 | 0.0299 | -0.0299 | +0.0113 | -0.0194 | -0.0125 |
| larger-28 | not identified | 0.0026 | 4.6181 | 4.6362 | +4.6040 | +4.6026 | +4.6296 | +4.6362 |

A direction is marked *not identified* when the training blocks' log candidate sizes span less than **0.10**, which leaves the size coefficient unconstrained. Its RMSE is reported for completeness and must not be read as an extrapolation error.

## Saturation

The fitted curve crosses coverage 1.0 at cap **152** (current-16), **160** (fresh-16) and **393** (larger-28), so caps above those are outside the model's admissible range by construction.

## Control

Cap 80 on six seeds (two per block) reproduces the committed cap-80 A, K and A∩K counts exactly.

| Block | Seed | A | K | A∩K | Matches committed |
| --- | ---: | ---: | ---: | ---: | --- |
| current-16 | 20630101 | 51 | 64 | 51 | yes |
| current-16 | 20630102 | 53 | 63 | 53 | yes |
| fresh-16 | 20650101 | 56 | 64 | 56 | yes |
| fresh-16 | 20650102 | 49 | 64 | 49 | yes |
| larger-28 | 20660101 | 86 | 111 | 68 | yes |
| larger-28 | 20660102 | 75 | 124 | 56 | yes |

## What this does not claim

A descriptive held-out prediction from no-arm replays. The cap axis is held out, the seeds are not: these are the same 18 seeds the fit was built from, so this bounds interpolation over caps and blocks, not generalization to a new seed block or world. Cap 128 sits near the 16-tag coverage ceiling, so its residual mixes curve error with saturation. It is not a treatment, target viability or successor.
