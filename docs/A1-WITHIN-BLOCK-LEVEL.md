# A1 within-block level

Generated from `docs/a1_within_block_level.json` by `python -m benchmarks.a1_within_block_level --write`. Do not edit by hand.

**Descriptive join, not an A1 result.** No engine replay, no target, freeze, grant or A1 cell.

## Result

Neither acquisition-time pair support nor temporal-edge density explains the 16-tag level. The three equal-size blocks differ in fitted offset by at most **0.0385** (**0.4200** / **0.4065** / **0.3815**), which is **0.39** to **1.68** standard errors of the pairwise difference at six seeds each and no wider than the within-block seed spread (**0.043** / **0.073** / **0.036**). Pair support barely moves — mean **22.90** / **22.61** / **22.62**, median **22.33** / **22.00** / **21.50**, mass **1458** / **1443** / **1444**, dispersion **7.88** / **7.77** / **8.14**, share at support <= 10 **0.045** / **0.034** / **0.029** — and temporal-edge density does not move at all: **176.0** / **176.0** / **175.8** distinct temporal edges, **11.00** / **11.00** / **10.99** per tag, so a quantity the two-tags-per-event law pins at **11** edges per tag cannot carry a level that varies. Of **11** quantities, **4** order the three block means the way the level does — median support, tag entropy, the support <= 10 share and the temporal-edge share (**2.765** / **2.757** / **2.755**) — each a one-in-six chance ordering, and none keeps a consistent sign at seed resolution: median support runs **-0.62** / **+0.38** / **-0.09**, tag entropy **-0.77** / **+0.14** / **-0.46**, the floor share **+0.14** / **-0.60** / **-0.82** and the edge share **+0.21** / **-0.65** / **+0.69**. The sharpest single case against a support account is fresh-16's lowest seed, `20650105` at offset **+0.2589**, which has that block's **highest** mean support (**23.0**). The lowest block matches fresh-16 on candidate count (**63.8** against **63.8**), K completeness (**1.000**) and temporal-edge density (**11.00** against **10.99**), so the level is not carried by candidate support, support mass, support dispersion, entropy, cell-pair coverage, pair saturation or the size of the temporal graph: it varies more inside a block than between equal-size blocks, and the fitted block offset is a mean of draws rather than a property of the candidate space.

## Blocks

| Block | Seeds | Offset mean | Offset SD | Offset SE | Candidates | K completeness |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| current-16 | 6 | +0.4200 | 0.0434 | 0.0177 | 63.7 | 1.000 |
| fresh-16 | 6 | +0.4065 | 0.0728 | 0.0297 | 63.8 | 1.000 |
| seed-2067 | 6 | +0.3815 | 0.0357 | 0.0146 | 63.8 | 1.000 |

## Pairwise level gaps

| Blocks | Difference | SE | z |
| --- | ---: | ---: | ---: |
| current-16 vs fresh-16 | 0.0136 | 0.0346 | 0.39 |
| current-16 vs seed-2067 | 0.0385 | 0.0230 | 1.68 |
| fresh-16 vs seed-2067 | 0.0249 | 0.0331 | 0.75 |

## Statistics

| Quantity | Block means | Relative spread | Orders like the level | Within-block rho | Sign consistent |
| --- | --- | ---: | --- | --- | --- |
| mean_support | 22.897 / 22.609 / 22.618 | 1.267% | no | -0.77 / +0.12 / -0.29 | no |
| median_support | 22.333 / 22.000 / 21.500 | 3.798% | yes | -0.62 / +0.38 / -0.09 | no |
| support_mass | 1457.833 / 1443.167 / 1443.833 | 1.013% | no | -0.77 / +0.41 / -0.55 | no |
| support_sd | 7.882 / 7.771 / 8.145 | 4.710% | no | +0.09 / -0.26 / -0.06 | no |
| frac_le_10 | 0.045 / 0.034 / 0.029 | 44.576% | yes | +0.14 / -0.60 / -0.82 | no |
| tag_entropy | 3.906 / 3.902 / 3.896 | 0.268% | yes | -0.77 / +0.14 / -0.46 | no |
| cell_pairs | 9.000 / 9.000 / 9.000 | 0.000% | no | +0.00 / +0.00 / +0.00 | no |
| pair_saturation | 0.442 / 0.443 / 0.443 | 0.262% | no | -0.21 / +0.65 / -0.66 | no |
| temporal_edges | 176.000 / 176.000 / 175.833 | 0.095% | no | +0.00 / +0.00 / +0.40 | no |
| temporal_edge_density | 11.000 / 11.000 / 10.990 | 0.095% | no | +0.00 / +0.00 / +0.40 | no |
| temporal_edge_share | 2.765 / 2.757 / 2.755 | 0.358% | yes | +0.21 / -0.65 / +0.69 | no |

## Per seed

| Block | Seed | Offset | Candidates | Mean support | Support mass | Entropy | Cell pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 20630101 | +0.3782 | 64 | 22.83 | 1461 | 3.917 | 9 |
| current-16 | 20630102 | +0.4057 | 63 | 23.06 | 1453 | 3.933 | 9 |
| current-16 | 20630103 | +0.4836 | 64 | 22.59 | 1446 | 3.880 | 9 |
| current-16 | 20630104 | +0.3586 | 64 | 23.53 | 1506 | 3.915 | 9 |
| current-16 | 20630105 | +0.4407 | 64 | 22.92 | 1467 | 3.911 | 9 |
| current-16 | 20630106 | +0.4533 | 63 | 22.44 | 1414 | 3.880 | 9 |
| fresh-16 | 20650101 | +0.4407 | 64 | 22.52 | 1441 | 3.909 | 9 |
| fresh-16 | 20650102 | +0.3938 | 64 | 22.39 | 1433 | 3.890 | 9 |
| fresh-16 | 20650103 | +0.4915 | 64 | 22.77 | 1457 | 3.912 | 9 |
| fresh-16 | 20650104 | +0.4446 | 64 | 22.52 | 1441 | 3.889 | 9 |
| fresh-16 | 20650105 | +0.2589 | 63 | 23.05 | 1452 | 3.897 | 9 |
| fresh-16 | 20650106 | +0.4094 | 64 | 22.42 | 1435 | 3.916 | 9 |
| seed-2067 | 20670101 | +0.4295 | 63 | 22.49 | 1417 | 3.885 | 9 |
| seed-2067 | 20670102 | +0.3547 | 64 | 22.23 | 1423 | 3.886 | 9 |
| seed-2067 | 20670103 | +0.4094 | 64 | 22.22 | 1422 | 3.886 | 9 |
| seed-2067 | 20670104 | +0.3508 | 64 | 22.53 | 1442 | 3.890 | 9 |
| seed-2067 | 20670105 | +0.4094 | 64 | 23.28 | 1490 | 3.924 | 9 |
| seed-2067 | 20670106 | +0.3352 | 64 | 22.95 | 1469 | 3.903 | 9 |

## Limits

- Three blocks and six seeds each: the block-level ordering has three points, so agreement of a block mean with the level ordering is necessary but far from sufficient.
- Within-block Spearman has n=6 per block and no multiplicity control; it is reported as a sign pattern, not a p-value.
- Support is measured on the acquisition stream; the engine's own temporal graph also includes within-event pairs, so these are stream-side quantities, not engine state.
- The level is a fitted intercept on committed coverage cells; it inherits the shared-slope assumption of the cap-response fit.
- No arm was run: every coverage number is read from a committed artifact.

## What this does not claim

A descriptive join of committed coverage cells to stream-side candidate quantities. It does not show that no quantity anywhere tracks the level, only that these eight do not, and it does not change any verdict, target, freeze or grant.
