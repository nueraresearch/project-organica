# A1 larger-28 overlap at prediction cap 80

Generated from `docs/a1_prediction_cap80_overlap.json` by `python -m benchmarks.a1_prediction_cap80_overlap --write`. Do not edit by hand.

**Availability-only overlap decomposition, not an A1 result.** Six larger-28 seeds at loop cap **120** / prediction cap **80**. No target, freeze, grant or A1 cell.

## Result

All six larger-28 seeds clear A marginally (A 75-91), so the two joint failures are not A shortages.  At cap 80, K covers 56/75 and 51/83 of the A edges on seeds 20660102 and 20660103, leaving 19 and 32 A edges uncarried; only 4 and 9 of those need to be covered to reach 60.  K volume is not scarce (K 124 and 105 against A 75 and 83), so the failure is selective K coverage: the joint ceiling loses 19 and 32 rows to A\K.

| Seeds | A | K | A∩K | A\K | K\A | Marginal pass | Joint pass |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 498 | 732 | 394 | 104 | 338 | 6/6 | 4/6 |

The joint count is `A∩K = A - |A\K| = K - |K\A|`. The two joint failures are **20660102, 20660103**, with A\K **19, 32** and minimum K repair **4, 9**.

## Per seed

| Seed | A | K | A∩K | A\K | K\A | K coverage of A | Gap to 60 (joint) | Marginal | Joint |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 20660101 | 86 | 111 | 68 | 18 | 43 | 79.1% | -8 | yes | yes |
| 20660102 | 75 | 124 | 56 | 19 | 68 | 74.7% | 4 | yes | no |
| 20660103 | 83 | 105 | 51 | 32 | 54 | 61.4% | 9 | yes | no |
| 20660104 | 88 | 138 | 77 | 11 | 61 | 87.5% | -17 | yes | yes |
| 20660105 | 91 | 121 | 72 | 19 | 49 | 79.1% | -12 | yes | yes |
| 20660106 | 75 | 133 | 70 | 5 | 63 | 93.3% | -10 | yes | yes |

## Failure test

Both joint failures clear A marginally, so their deficit is entirely the overlap loss:

| Seed | A | A∩K | A\K | Need to reach 60 | K | K\A | K coverage |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20660102 | 75 | 56 | 19 | 4 | 124 | 68 | 74.7% |
| 20660103 | 83 | 51 | 32 | 9 | 105 | 54 | 61.4% |

Both seeds have A≥60 and K≥60. K nevertheless misses 19, 32 A edges; recovering only 4, 9 of those would lift each joint ceiling to 60. The failures also have the two lowest K-coverage rates, while the four passing seeds have coverage at least 79.1%.

K volume is therefore not the constraint: the failing seeds have K **124, 105** against A **75, 83**. The constraint is which A edges K covers.

## A\K exact edges on the two failures

| Seed | Edge | Support | A rank |
| ---: | --- | ---: | ---: |
| 20660102 | amber>taggg | 12 | 33 |
| 20660102 | birch>maple | 11 | 19 |
| 20660102 | birch>taggg | 7 | 21 |
| 20660102 | birch>teal | 17 | 8 |
| 20660102 | cedar>tagii | 3 | 1 |
| 20660102 | cedar>teal | 9 | 1 |
| 20660102 | tagbb>tagkk | 13 | 39 |
| 20660102 | taghh>fern | 14 | 1 |
| 20660102 | taghh>teal | 8 | 1 |
| 20660102 | taghh>yarrow | 6 | 1 |
| 20660102 | tagll>maple | 10 | 19 |
| 20660102 | tagll>taggg | 10 | 20 |
| 20660102 | teal>willow | 4 | 6 |
| 20660102 | umber>taggg | 12 | 14 |
| 20660102 | umber>tagjj | 11 | 19 |
| 20660102 | verdant>teal | 5 | 26 |
| 20660102 | willow>tagaa | 7 | 36 |
| 20660102 | yarrow>amber | 7 | 3 |
| 20660102 | yarrow>tagll | 6 | 30 |
| 20660103 | fern>birch | 8 | 8 |
| 20660103 | fern>crimson | 5 | 15 |
| 20660103 | indigo>olive | 7 | 21 |
| 20660103 | olive>birch | 6 | 38 |
| 20660103 | olive>crimson | 9 | 39 |
| 20660103 | olive>teal | 8 | 34 |
| 20660103 | sable>taggg | 8 | 7 |
| 20660103 | slate>crimson | 5 | 4 |
| 20660103 | slate>maple | 7 | 5 |
| 20660103 | slate>taghh | 8 | 6 |
| 20660103 | tagaa>taggg | 3 | 2 |
| 20660103 | tagcc>indigo | 8 | 4 |
| 20660103 | tagcc>maple | 8 | 9 |
| 20660103 | tagcc>ochre | 13 | 12 |
| 20660103 | tagcc>sable | 9 | 4 |
| 20660103 | tagcc>tagdd | 13 | 34 |
| 20660103 | tagcc>taghh | 14 | 26 |
| 20660103 | tagcc>tagll | 17 | 20 |
| 20660103 | tagkk>birch | 8 | 19 |
| 20660103 | tagkk>sable | 7 | 2 |
| 20660103 | tagkk>tagaa | 8 | 28 |
| 20660103 | teal>fern | 3 | 16 |
| 20660103 | verdant>ochre | 3 | 21 |
| 20660103 | verdant>tagaa | 8 | 25 |
| 20660103 | verdant>tagdd | 6 | 22 |
| 20660103 | verdant>taghh | 10 | 18 |
| 20660103 | yarrow>crimson | 12 | 1 |
| 20660103 | yarrow>maple | 11 | 21 |
| 20660103 | yarrow>ochre | 7 | 22 |
| 20660103 | yarrow>tagdd | 11 | 24 |
| 20660103 | yarrow>taghh | 9 | 29 |
| 20660103 | yarrow>umber | 12 | 26 |

## A\K by support

| Support | A\K |
| --- | ---: |
| 0 | 0 |
| 1 | 0 |
| 2-3 | 7 |
| 4-7 | 35 |
| 8-15 | 59 |
| 16+ | 3 |

## K\A by support

| Support | K\A |
| --- | ---: |
| 0 | 0 |
| 1 | 2 |
| 2-3 | 30 |
| 4-7 | 168 |
| 8-15 | 136 |
| 16+ | 2 |

## Reading

Four seeds pass jointly because K covers enough of A, not because their A or K totals are larger. The two failures are not K-volume failures: both carry more K than A. They are selective-coverage failures, and full K coverage of A would make both pass because A alone is already 75 and 83.

The K\A pool is the alternative repair side: those edges are already carried, so serving them into A would also raise A∩K. This decomposition does not choose between repairing K coverage and serving the K\A pool.

## What this does not claim

A descriptive overlap decomposition on six no-arm larger-28 seeds at one cap pair.  It measures A\K and K\A availability; it is not a treatment, a K-repair result, target viability or a successor.  Full K coverage is a counterfactual, not an engine change.
