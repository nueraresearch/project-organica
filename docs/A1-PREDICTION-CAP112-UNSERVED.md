# A1 cap-112 unserved edges

Generated from `docs/a1_prediction_cap112_unserved.json` by `python -m benchmarks.a1_prediction_cap112_unserved --write`. Do not edit by hand.

**Descriptive edge trace, not an A1 result.** Twelve 16-tag no-arm seeds at loop cap **120** / prediction cap **112**. No target, freeze, grant or A1 cell.

## Result

Across the twelve 16-tag seeds, A leaves 74 of 765 candidate edges unserved at cap 112 (691 served). The unserved edges are all support-eligible on the stream (0 below the 5 floor), so the window, not supply, is the binding constraint: 73 are transition candidates, 0 are cooccurrence candidates, and 1 never became a candidate at all. Their candidate-order ranks run 65 to 189 (median 100): 47 fall in the tail of the nominal window at ranks 57-112 and 26 beyond it. That is the transition share talking, not the raw cap: transitions get the first half of the budget plus whatever the cooccurrence quota leaves unused, so an edge at rank 90 is still outside the window whenever cooccurrences claim their share. By family the unserved split is flip_p 8, flip_q 66: flip_q supplies 66 and flip_p 8, and the serve rates are flip_p 0.979, flip_q 0.827, so the window loses flip_q edges 8.3 times as fast as flip_p. 74 of the unserved edges are already carried by K, so the shortfall is prediction-side, not carrier-side.

## Totals

| Candidate edges | Served | Unserved | Support ≥ 5 | Transitions | Cooccurrences | No candidate | Already in K |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 765 | 691 | 74 | 74 | 73 | 0 | 1 | 74 |

## By family

| Family | Candidates | Served | Serve rate | Unserved |
| --- | ---: | ---: | ---: | ---: |
| flip_p | 383 | 375 | 0.979 | 8 |
| flip_q | 382 | 316 | 0.827 | 66 |

## Unserved by kind

| Kind | Unserved | Families |
| --- | ---: | --- |
| transition | 73 | flip_p 8, flip_q 65 |
| cooccurrence | 0 | - |
| none | 1 | flip_q 1 |

## Unserved by candidate-order band

| Band | Unserved | Families |
| --- | ---: | --- |
| 1-56 | 0 | - |
| 57-112 | 47 | flip_p 3, flip_q 44 |
| 113-224 | 26 | flip_p 5, flip_q 21 |
| 225+ | 0 | - |

## Per seed

| Block | Seed | Candidates | A | Unserved | Support ≥ 5 | Families |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| current-16 | 20630101 | 64 | 57 | 7 | 7 | flip_q 7 |
| current-16 | 20630102 | 63 | 57 | 6 | 6 | flip_p 1, flip_q 5 |
| current-16 | 20630103 | 64 | 60 | 4 | 4 | flip_p 1, flip_q 3 |
| current-16 | 20630104 | 64 | 55 | 9 | 9 | flip_p 1, flip_q 8 |
| current-16 | 20630105 | 64 | 59 | 5 | 5 | flip_p 1, flip_q 4 |
| current-16 | 20630106 | 63 | 57 | 6 | 6 | flip_q 6 |
| fresh-16 | 20650101 | 64 | 59 | 5 | 5 | flip_p 1, flip_q 4 |
| fresh-16 | 20650102 | 64 | 56 | 8 | 8 | flip_p 1, flip_q 7 |
| fresh-16 | 20650103 | 64 | 59 | 5 | 5 | flip_q 5 |
| fresh-16 | 20650104 | 64 | 63 | 1 | 1 | flip_q 1 |
| fresh-16 | 20650105 | 63 | 52 | 11 | 11 | flip_p 2, flip_q 9 |
| fresh-16 | 20650106 | 64 | 57 | 7 | 7 | flip_q 7 |

## Unserved edges

| Block | Seed | Edge | Support | Family | Kind | Rank | Band | In K |
| --- | ---: | --- | ---: | --- | --- | ---: | --- | --- |
| current-16 | 20630101 | `amber>ochre` | 13 | flip_q | transition | 117 | 113-224 | yes |
| current-16 | 20630101 | `amber>olive` | 25 | flip_q | transition | 70 | 57-112 | yes |
| current-16 | 20630101 | `amber>teal` | 18 | flip_q | transition | 120 | 113-224 | yes |
| current-16 | 20630101 | `cedar>teal` | 20 | flip_q | transition | 94 | 57-112 | yes |
| current-16 | 20630101 | `fern>willow` | 17 | flip_q | transition | 96 | 57-112 | yes |
| current-16 | 20630101 | `ochre>cedar` | 12 | flip_q | transition | 166 | 113-224 | yes |
| current-16 | 20630101 | `slate>umber` | 12 | flip_q | transition | 70 | 57-112 | yes |
| current-16 | 20630102 | `birch>willow` | 21 | flip_q | transition | 113 | 113-224 | yes |
| current-16 | 20630102 | `cedar>birch` | 20 | flip_q | transition | 166 | 113-224 | yes |
| current-16 | 20630102 | `cedar>olive` | 26 | flip_q | transition | 100 | 57-112 | yes |
| current-16 | 20630102 | `cedar>umber` | 20 | flip_q | transition | 139 | 113-224 | yes |
| current-16 | 20630102 | `slate>indigo` | 22 | flip_q | transition | 113 | 113-224 | yes |
| current-16 | 20630102 | `yarrow>umber` | 25 | flip_p | transition | 65 | 57-112 | yes |
| current-16 | 20630103 | `ochre>slate` | 10 | flip_q | transition | 75 | 57-112 | yes |
| current-16 | 20630103 | `sable>slate` | 9 | flip_q | transition | 87 | 57-112 | yes |
| current-16 | 20630103 | `slate>willow` | 16 | flip_q | none | - | never | yes |
| current-16 | 20630103 | `yarrow>maple` | 35 | flip_p | transition | 134 | 113-224 | yes |
| current-16 | 20630104 | `amber>birch` | 18 | flip_q | transition | 106 | 57-112 | yes |
| current-16 | 20630104 | `birch>cedar` | 10 | flip_q | transition | 166 | 113-224 | yes |
| current-16 | 20630104 | `crimson>birch` | 19 | flip_q | transition | 70 | 57-112 | yes |
| current-16 | 20630104 | `fern>indigo` | 21 | flip_q | transition | 110 | 57-112 | yes |
| current-16 | 20630104 | `maple>crimson` | 29 | flip_p | transition | 76 | 57-112 | yes |
| current-16 | 20630104 | `teal>cedar` | 11 | flip_q | transition | 66 | 57-112 | yes |
| current-16 | 20630104 | `teal>fern` | 7 | flip_q | transition | 67 | 57-112 | yes |
| current-16 | 20630104 | `umber>crimson` | 25 | flip_q | transition | 86 | 57-112 | yes |
| current-16 | 20630104 | `willow>olive` | 17 | flip_q | transition | 125 | 113-224 | yes |
| current-16 | 20630105 | `sable>willow` | 15 | flip_q | transition | 76 | 57-112 | yes |
| current-16 | 20630105 | `slate>birch` | 13 | flip_q | transition | 110 | 57-112 | yes |
| current-16 | 20630105 | `slate>crimson` | 23 | flip_p | transition | 131 | 113-224 | yes |
| current-16 | 20630105 | `slate>maple` | 12 | flip_q | transition | 114 | 113-224 | yes |
| current-16 | 20630105 | `slate>olive` | 21 | flip_q | transition | 134 | 113-224 | yes |
| current-16 | 20630106 | `crimson>teal` | 10 | flip_q | transition | 112 | 57-112 | yes |
| current-16 | 20630106 | `fern>ochre` | 12 | flip_q | transition | 180 | 113-224 | yes |
| current-16 | 20630106 | `sable>crimson` | 14 | flip_q | transition | 93 | 57-112 | yes |
| current-16 | 20630106 | `sable>willow` | 13 | flip_q | transition | 95 | 57-112 | yes |
| current-16 | 20630106 | `slate>fern` | 13 | flip_q | transition | 105 | 57-112 | yes |
| current-16 | 20630106 | `teal>willow` | 18 | flip_q | transition | 74 | 57-112 | yes |
| fresh-16 | 20650101 | `cedar>sable` | 19 | flip_q | transition | 100 | 57-112 | yes |
| fresh-16 | 20650101 | `maple>umber` | 16 | flip_q | transition | 105 | 57-112 | yes |
| fresh-16 | 20650101 | `umber>sable` | 37 | flip_p | transition | 86 | 57-112 | yes |
| fresh-16 | 20650101 | `umber>verdant` | 23 | flip_q | transition | 92 | 57-112 | yes |
| fresh-16 | 20650101 | `verdant>amber` | 14 | flip_q | transition | 120 | 113-224 | yes |
| fresh-16 | 20650102 | `cedar>ochre` | 10 | flip_q | transition | 128 | 113-224 | yes |
| fresh-16 | 20650102 | `cedar>slate` | 16 | flip_q | transition | 72 | 57-112 | yes |
| fresh-16 | 20650102 | `maple>indigo` | 10 | flip_q | transition | 104 | 57-112 | yes |
| fresh-16 | 20650102 | `ochre>indigo` | 13 | flip_q | transition | 141 | 113-224 | yes |
| fresh-16 | 20650102 | `olive>birch` | 34 | flip_p | transition | 158 | 113-224 | yes |
| fresh-16 | 20650102 | `slate>indigo` | 9 | flip_q | transition | 98 | 57-112 | yes |
| fresh-16 | 20650102 | `umber>slate` | 12 | flip_q | transition | 83 | 57-112 | yes |
| fresh-16 | 20650102 | `yarrow>birch` | 19 | flip_q | transition | 100 | 57-112 | yes |
| fresh-16 | 20650103 | `cedar>indigo` | 22 | flip_q | transition | 115 | 113-224 | yes |
| fresh-16 | 20650103 | `olive>ochre` | 14 | flip_q | transition | 108 | 57-112 | yes |
| fresh-16 | 20650103 | `sable>cedar` | 17 | flip_q | transition | 111 | 57-112 | yes |
| fresh-16 | 20650103 | `sable>ochre` | 15 | flip_q | transition | 68 | 57-112 | yes |
| fresh-16 | 20650103 | `teal>fern` | 23 | flip_q | transition | 88 | 57-112 | yes |
| fresh-16 | 20650104 | `olive>slate` | 17 | flip_q | transition | 95 | 57-112 | yes |
| fresh-16 | 20650105 | `cedar>indigo` | 22 | flip_p | transition | 147 | 113-224 | yes |
| fresh-16 | 20650105 | `fern>indigo` | 17 | flip_q | transition | 67 | 57-112 | yes |
| fresh-16 | 20650105 | `olive>birch` | 11 | flip_q | transition | 166 | 113-224 | yes |
| fresh-16 | 20650105 | `sable>willow` | 18 | flip_q | transition | 189 | 113-224 | yes |
| fresh-16 | 20650105 | `umber>fern` | 25 | flip_p | transition | 123 | 113-224 | yes |
| fresh-16 | 20650105 | `umber>teal` | 21 | flip_q | transition | 126 | 113-224 | yes |
| fresh-16 | 20650105 | `verdant>cedar` | 17 | flip_q | transition | 75 | 57-112 | yes |
| fresh-16 | 20650105 | `verdant>olive` | 12 | flip_q | transition | 73 | 57-112 | yes |
| fresh-16 | 20650105 | `verdant>sable` | 13 | flip_q | transition | 76 | 57-112 | yes |
| fresh-16 | 20650105 | `verdant>teal` | 16 | flip_q | transition | 128 | 113-224 | yes |
| fresh-16 | 20650105 | `yarrow>maple` | 18 | flip_q | transition | 65 | 57-112 | yes |
| fresh-16 | 20650106 | `cedar>slate` | 15 | flip_q | transition | 80 | 57-112 | yes |
| fresh-16 | 20650106 | `crimson>ochre` | 22 | flip_q | transition | 130 | 113-224 | yes |
| fresh-16 | 20650106 | `ochre>birch` | 12 | flip_q | transition | 96 | 57-112 | yes |
| fresh-16 | 20650106 | `sable>amber` | 10 | flip_q | transition | 67 | 57-112 | yes |
| fresh-16 | 20650106 | `teal>crimson` | 10 | flip_q | transition | 83 | 57-112 | yes |
| fresh-16 | 20650106 | `umber>willow` | 18 | flip_q | transition | 92 | 57-112 | yes |
| fresh-16 | 20650106 | `willow>ochre` | 17 | flip_q | transition | 71 | 57-112 | yes |

## What this does not claim

A descriptive trace of the cap-112 prediction window on twelve no-arm 16-tag seeds. Rank is the engine's candidate order under observed, signalled stop rules; it is not a counterfactual about what a different cap would serve. It is not a treatment, target viability or successor.
