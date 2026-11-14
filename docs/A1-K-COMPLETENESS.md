# A1 K completeness across prediction caps

Generated from `docs/a1_k_completeness.json` by `python -m benchmarks.a1_k_completeness --write`. Do not edit by hand.

**Descriptive census, not an A1 result.** 18 no-arm seeds at prediction caps **20/40/80/112**. No target, freeze, grant or A1 cell.

## Result

K completeness separates the blocks at every cap: all 16-tag rows are 1.000, while larger-28 rows are 0.6105-0.8485 (margin 0.1515). But it is nearly invariant across caps: larger-28 moves only 0.0011 in absolute aggregate, and its per-seed range is at most 0.0121, while joint C1 passes move 0->0->4->8 overall and 0->0->4->6 in larger-28. K completeness is therefore a regime marker, not the cap lever. It also does not order joint success within larger-28: at cap 80, the lowest-completeness pass is 0.6568 while the highest-completeness failure is 0.7425.

| Cap | Candidates | A | K | A∩K | K completeness | K coverage of A | Joint pass |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 1765 | 744 | 1499 | 691 | 0.849 | 0.929 | 0/18 |
| 40 | 1765 | 913 | 1498 | 842 | 0.849 | 0.922 | 0/18 |
| 80 | 1765 | 1129 | 1497 | 1025 | 0.848 | 0.908 | 4/18 |
| 112 | 1765 | 1269 | 1497 | 1150 | 0.848 | 0.906 | 8/18 |

## By block

| Block | Cap | Candidates | K | K completeness | K coverage of A | Joint pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 20 | 382 | 382 | 1.000 | 1.000 | 0/6 |
| current-16 | 40 | 382 | 382 | 1.000 | 1.000 | 0/6 |
| current-16 | 80 | 382 | 382 | 1.000 | 1.000 | 0/6 |
| current-16 | 112 | 382 | 382 | 1.000 | 1.000 | 1/6 |
| fresh-16 | 20 | 383 | 383 | 1.000 | 1.000 | 0/6 |
| fresh-16 | 40 | 383 | 383 | 1.000 | 1.000 | 0/6 |
| fresh-16 | 80 | 383 | 383 | 1.000 | 1.000 | 0/6 |
| fresh-16 | 112 | 383 | 383 | 1.000 | 1.000 | 1/6 |
| larger-28 | 20 | 1000 | 734 | 0.734 | 0.804 | 0/6 |
| larger-28 | 40 | 1000 | 733 | 0.733 | 0.799 | 0/6 |
| larger-28 | 80 | 1000 | 732 | 0.732 | 0.791 | 4/6 |
| larger-28 | 112 | 1000 | 732 | 0.732 | 0.794 | 6/6 |

## Separation

| Statistic | Value |
| --- | ---: |
| Minimum 16-tag completeness | 1.000 |
| Maximum larger-28 completeness | 0.848 |
| Margin | 0.152 |
| Classification accuracy | 100% |

The block split is perfect at every cap. It is also almost constant within larger-28: the aggregate moves by only 0.0011, and the largest per-seed across-cap range is 0.0121.

## What it does not explain

K completeness is static while joint C1 is not. Joint passes move **0 → 0 → 4 → 8** overall and **0 → 0 → 4 → 6** in larger-28 across caps 20/40/80/112. At cap 80, the lowest-completeness larger-28 pass is **0.657**, while the highest-completeness failure is **0.743**; a higher completeness does not guarantee a joint pass.

The 16-tag block is K-complete but still fails joint C1 at caps 20/40/80 (and 10/12 seeds fail at 112). Completeness removes the A\K loss; it does not supply A.

## Reading

K completeness is a **regime marker**: 1.000 in the 16-tag streams, 0.61–0.85 in larger-28, at every cap. It is not the variable that moves C1 across caps. The cap response is A, while K coverage of A determines how much of that A survives into the joint count.

## What this does not claim

A descriptive census of 18 fixed no-arm seeds across four prediction caps.  K completeness is measured from the committed rows, not intervened; the artifact does not show that changing K completeness would change C1, and it is not a treatment, target viability or a successor.
