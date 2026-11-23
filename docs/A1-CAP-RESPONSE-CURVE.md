# A1 predicted-cap response curve

Generated from `docs/a1_cap_response_curve.json` by `python -m benchmarks.a1_cap_response_curve --write`. Do not edit by hand.

**Descriptive fit, not an A1 result.** 12 block-by-cap cells from 18 no-arm seeds at prediction caps **20/40/80/112**. No target, freeze, grant or A1 cell.

## Result

A single square-root cap curve plus a block offset predicts the 12 block-by-cap cells with in-sample RMSE 0.0131 (max 0.0242) and leave-one-cell-out RMSE 0.0193 (max 0.0333). Block-specific square-root slopes reach LOO RMSE 0.0209, arbitrary per-cap effects 0.0232, and block-specific linear slopes 0.0398. The shared curve is therefore sufficient over this cap range: the blocks differ mainly by a baseline offset, not by response shape.

## Model comparison

| Model | Parameters | In-sample RMSE | In-sample max | LOO RMSE | LOO max |
| --- | ---: | ---: | ---: | ---: | ---: |
| block_only | 3 | 0.1112 | 0.1627 | 0.1483 | 0.2169 |
| cap_only | 4 | 0.1629 | 0.2525 | 0.2443 | 0.3787 |
| common_linear_offset | 4 | 0.0199 | 0.0359 | 0.0299 | 0.0502 |
| common_log_offset | 4 | 0.0148 | 0.0292 | 0.0220 | 0.0395 |
| common_sqrt_offset | 4 | 0.0131 | 0.0242 | 0.0193 | 0.0333 |
| common_quadratic_offset | 5 | 0.0142 | 0.0261 | 0.0234 | 0.0387 |
| common_exponential_offset | 5 | 0.0134 | 0.0228 | 0.0230 | 0.0368 |
| additive_cap_effects | 6 | 0.0116 | 0.0229 | 0.0232 | 0.0457 |
| block_linear | 6 | 0.0181 | 0.0362 | 0.0398 | 0.0776 |
| block_sqrt | 6 | 0.0102 | 0.0248 | 0.0209 | 0.0486 |
| full_interaction | 12 | 0.0000 | 0.0000 | n/a | n/a |

The saturated interaction has zero in-sample error by construction and no held-out prediction, because each cell is its own parameter. It is shown for scale, not selected.

## Shared curve

Selected form:

```text
A_coverage = block_offset + 0.04699 * sqrt(cap)
```

| Block | Offset | Relative to current-16 |
| --- | ---: | ---: |
| current-16 | 0.4200 | +0.0000 |
| fresh-16 | 0.4065 | -0.0136 |
| larger-28 | 0.0688 | -0.3512 |

## Cell fit

| Block | Cap | Observed | Predicted | Residual |
| --- | ---: | ---: | ---: | ---: |
| current-16 | 20 | 0.6362 | 0.6302 | +0.0061 |
| current-16 | 40 | 0.7356 | 0.7172 | +0.0184 |
| current-16 | 80 | 0.8299 | 0.8403 | -0.0104 |
| current-16 | 112 | 0.9032 | 0.9173 | -0.0141 |
| fresh-16 | 20 | 0.6000 | 0.6166 | -0.0166 |
| fresh-16 | 40 | 0.7278 | 0.7036 | +0.0242 |
| fresh-16 | 80 | 0.8197 | 0.8267 | -0.0071 |
| fresh-16 | 112 | 0.9032 | 0.9037 | -0.0005 |
| larger-28 | 20 | 0.2711 | 0.2790 | -0.0078 |
| larger-28 | 40 | 0.3530 | 0.3660 | -0.0130 |
| larger-28 | 80 | 0.4978 | 0.4891 | +0.0087 |
| larger-28 | 112 | 0.5781 | 0.5661 | +0.0121 |

## Reading

The shared curve is not just a description of the marginal cap effect: it predicts a held-out block-cap cell better than giving each block its own slope or giving each cap its own free effect. The block offsets are the baseline-occupancy difference. The fitted curve is concave, so each additional prediction slot buys less coverage, but the same shape applies to all three blocks over this range.

This does not establish a mechanism. It establishes that the 12-cell surface is low-rank in the tested family: one curve plus three offsets.

## What this does not claim

A descriptive fit to 12 fixed block-by-cap cell means from 18 no-arm seeds. It compares interpolation models, not causal effects; it does not show that changing the prediction cap would move A by the fitted curve, and it is not a treatment, target viability or successor.
