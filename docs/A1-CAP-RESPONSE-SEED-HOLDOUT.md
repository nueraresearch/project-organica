# A1 cap-response seed holdout

Generated from `docs/a1_cap_response_seed_holdout.json` by `python -m benchmarks.a1_cap_response_seed_holdout --write`. Do not edit by hand.

**Descriptive held-out prediction, not an A1 result.** A fresh 16-tag block, **20670101–20670106**, at the fitted caps **20/40/80/112**. Candidate stream from the committed fixed rule, not target selection. No target, freeze, grant or A1 cell.

## Result

On the unseen block the offset model misses the block's level. The frozen candidate-size offset predicts the four fitted caps with RMSE 0.0321 (max 0.0432) and mean residual -0.0313, against a 16-tag leave-one-cell-out error of 0.0216 for the curve with free block offsets and 0.0184 for the size model itself. The 24 seed-by-cap values give RMSE 0.0592 (max 0.1153), inside the 16-tag seed LOO of 0.0747, so the per-seed scatter is no worse than at fitting time while the level is. The block sits below both fitted 16-tag blocks at all four caps — coverage 0.5797/0.6789/0.8096/0.8826 at caps 20/40/80/112 against 0.6362/0.7356/0.8299/0.9032 for current-16 — although its candidate space is the same size (63 edges per seed). Its mean log candidate size, 4.156258, is identical to fresh-16's, so the size model gives it fresh-16's offset (0.4128) and cannot tell the two blocks apart, yet the block still sits 0.0171 to 0.0369 below the fresh-16 bracket at every cap. Applying a known 16-tag offset instead is no better in kind: cell RMSE 0.0392 (current-16) and 0.0260 (fresh-16), both outside the fitted 16-tag LOO. Candidate size therefore replaces the block label inside the fitted blocks, but it does not predict a new block's offset; the cell error is outside the fitted 16-tag scale.

## Cells

| Cap | Observed | Size prediction | Residual | Current-16 bracket | Residual | Fresh-16 bracket | Residual |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 0.5797 | 0.6229 | -0.0432 | 0.6302 | -0.0505 | 0.6166 | -0.0369 |
| 40 | 0.6789 | 0.7100 | -0.0310 | 0.7172 | -0.0383 | 0.7036 | -0.0247 |
| 80 | 0.8096 | 0.8330 | -0.0234 | 0.8403 | -0.0306 | 0.8267 | -0.0171 |
| 112 | 0.8826 | 0.9100 | -0.0274 | 0.9173 | -0.0346 | 0.9037 | -0.0211 |

Reference scales. All 12 cells: shared curve LOO **0.0193**, candidate-size model **0.0184** (cell) and **0.0667** (seed). 16-tag cells and rows only: shared curve **0.0216** (cell) and candidate-size model **0.0747** (seed).

## Per seed

| Seed | Candidates | Mean coverage | RMSE vs size prediction | Max |
| ---: | ---: | ---: | ---: | ---: |
| 20670101 | 63 | 0.7857 | 0.0382 | 0.0670 |
| 20670102 | 64 | 0.7109 | 0.0785 | 0.1153 |
| 20670103 | 64 | 0.7656 | 0.0350 | 0.0566 |
| 20670104 | 64 | 0.7070 | 0.0656 | 0.0996 |
| 20670105 | 64 | 0.7656 | 0.0405 | 0.0497 |
| 20670106 | 64 | 0.6914 | 0.0788 | 0.0977 |

## Fitted 16-tag blocks

| Cap | Current-16 | Fresh-16 | Unseen-16 |
| ---: | ---: | ---: | ---: |
| 20 | 0.6362 | 0.6000 | 0.5797 |
| 40 | 0.7356 | 0.7278 | 0.6789 |
| 80 | 0.8299 | 0.8197 | 0.8096 |
| 112 | 0.9032 | 0.9032 | 0.8826 |

## Control

Cap 80 on two committed seeds reproduces their committed A, K and A∩K counts.

| Block | Seed | A | K | A∩K | Matches committed |
| --- | ---: | ---: | ---: | ---: | --- |
| current-16 | 20630101 | 51 | 64 | 51 | yes |
| fresh-16 | 20650101 | 56 | 64 | 56 | yes |

## What this does not claim

A descriptive held-out prediction from no-arm replays. The seed block is new, the caps are the fitted ones, and the model is frozen; this bounds seed-axis transfer of the offset model over one 16-tag block, not a population of blocks. The candidate stream comes from a fixed rule, not from target selection, so these are not A1 protocol cells. It is not a treatment, target viability or successor.
