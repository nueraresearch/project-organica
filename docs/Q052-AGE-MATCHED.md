# Q052 addendum A2a: the same mass, at the same age

Generated from `docs/q052_age_matched.json` by `python -m benchmarks.q052_age_matched --render`. Do not edit by hand.

A2 classified `burst_L1` as `DIFFERENT_SUPPORT_COLLAPSE` and recorded one confound: the burst cells die at 131-134 and the control at 300, so the mass gap might belong to the death's age. This page measures the two comparisons that can separate them.

**Reading rule, fixed before the cells were read.** Tolerance 10 cycles; band 0.10 of cohort mass ratio. AGE_MATCH_UNAVAILABLE when no lattice death falls within the tolerance of a burst death; AGE_EXPLAINS_THE_GAP when a matched lattice death's ratio is within the band; AGE_DOES_NOT_EXPLAIN_THE_GAP when it is not.

**Label: `AGE_MATCH_UNAVAILABLE`**

## What a live cycle does at those ages

The lattice control is alive at cycles 131, 134, so these transitions carry no death. They measure how much cohort mass one live cycle costs at those ages, which is what an age effect would have to move.

| Cycle | Theories before -> at | Cohort | Survived | Mass before -> after | Ratio |
| --- | --- | --- | --- | --- | --- |
| 131 | 5 -> 5 | 22 | 22 | 5003 -> 5002 | 0.9998 |
| 134 | 5 -> 5 | 22 | 21 | 5041 -> 4710 | 0.934338 |

## The burst deaths under test

| Seed | Death | Cohort | Survived | Mass before -> after | Ratio |
| --- | --- | --- | --- | --- | --- |
| 20303001 | 134 | 14 | 11 | 1394 -> 429 | 0.307747 |
| 20303002 | 131 | 16 | 12 | 1386 -> 437 | 0.315296 |
| 20303003 | 131 | 15 | 7 | 1981 -> 67 | 0.033821 |

## The lattice deaths, and the age match

| Factor | Death | Cohort | Survived | Mass before -> after | Ratio |
| --- | --- | --- | --- | --- | --- |
| 0.9924 | 300 | 17 | 13 | 4106 -> 2374 | 0.578178 |
| 0.95 | 39 | 17 | 13 | 834 -> 509 | 0.610312 |
| 0.97 | 69 | 17 | 13 | 1189 -> 703 | 0.591253 |
| 0.98 | 112 | 17 | 13 | 1733 -> 1006 | 0.580496 |
| 0.985 | 150 | 17 | 13 | 2203 -> 1286 | 0.583749 |
| 0.99 | 228 | 17 | 13 | 3192 -> 1848 | 0.578947 |

| Burst seed | Burst death | Burst ratio | Nearest lattice death | Distance | Nearest ratio | Matched ratio | Difference | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20303001 | 134 | 0.307747 | 150 (0.985) | 16 | 0.583749 | None | None | AGE_MATCH_UNAVAILABLE |
| 20303002 | 131 | 0.315296 | 112 (0.98) | 19 | 0.580496 | None | None | AGE_MATCH_UNAVAILABLE |
| 20303003 | 131 | 0.033821 | 112 (0.98) | 19 | 0.580496 | None | None | AGE_MATCH_UNAVAILABLE |

## Does the ratio depend on the age of the death?

| Death cycle | Factor | Cohort mass ratio |
| --- | --- | --- |
| 39 | 0.95 | 0.610312 |
| 69 | 0.97 | 0.591253 |
| 112 | 0.98 | 0.580496 |
| 150 | 0.985 | 0.583749 |
| 228 | 0.99 | 0.578947 |
| 300 | 0.9924 | 0.578178 |

Spread across the lattice deaths: **0.032134**, so the age trend is flat against the band of 0.1.

Recorded after the exact match was found unavailable. It interpolates the lattice death ratio at the burst death age from the deaths either side, uses the same band of 0.10, and changes no label.

| Burst seed | Burst death | Burst ratio | Bracketed lattice ratio | Difference | Beyond the band |
| --- | --- | --- | --- | --- | --- |
| 20303001 | 134 | 0.307747 | 0.582379 (from 112 and 150) | -0.274632 | True |
| 20303002 | 131 | 0.315296 | 0.582122 (from 112 and 150) | -0.266826 | True |
| 20303003 | 131 | 0.033821 | 0.582122 (from 112 and 150) | -0.548301 | True |

## What this decides, and what it cannot

One world family, one instrument, four cells. The live comparison is not a death: it shows what a live cycle does to the cohort at those ages, while the death comparison needs a lattice factor that dies there.

A lattice death inside the tolerance is a family-matched, age-matched comparator; its absence means the death comparison is not constructible with the factors run, and the live comparison is the weaker statement that the measure itself does not drift with age.

Factors run: 0.95, 0.97, 0.98, 0.985, 0.99, 0.9924.

The first three factors (0.9924, 0.95, 0.97) put the lattice deaths at 300, 39 and 69, so no death fell inside the tolerance of 131-134. Three more factors were run to search for a death near those ages. The tolerance of 10 cycles and the band of 0.10 were fixed before any cell and were not changed.

This addendum changes no label. A2's `DIFFERENT_SUPPORT_COLLAPSE` stands as the classification the amended conditions imply; this record only decides whether the recorded *confound* explains the gap it was charged with.
