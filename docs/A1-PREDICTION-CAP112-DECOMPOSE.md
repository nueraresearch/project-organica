# A1 cap-112 16-tag decomposition

Generated from `docs/a1_prediction_cap112_decompose.json` by `python -m benchmarks.a1_prediction_cap112_decompose --write`. Do not edit by hand.

**Descriptive, not an A1 result.** Ten failing 16-tag seeds at loop cap **120** and prediction cap **112**, with a diagnostic cap **1000** to locate missing edges. No target, freeze, grant or A1 cell.

## Result

All 69 A-missing candidate edges across the ten failing seeds appear at diagnostic cap 1000, at ranks 65-189. They are support-eligible and all 69 are transition candidates; none is a cooccurrence. 62/69 are flip_q. The cap-112 run excludes them, but cap 1000 also changes which predictions are reinforced across cycles, so the rank range is diagnostic, not a fixed cutoff. The stable discriminator is the edge family: flip_q transitions are ranked out of the 112-row prediction window.

| Missing edges | Support >=5 | Cap-1000 bound | Never A | Cooccurrence | Cap-1000 rank range |
| ---: | ---: | ---: | ---: | ---: | --- |
| 69 | 69 | 69 | 0 | 0 | 65-189 |

## Per seed

| Block | Seed | Candidates | A112 | A1000 | Gap | Missing | Cap-bound | Never | Max A112 rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 20630101 | 64 | 57 | 64 | 3 | 7 | 7 | 0 | 112 |
| current-16 | 20630102 | 63 | 57 | 63 | 3 | 6 | 6 | 0 | 111 |
| current-16 | 20630104 | 64 | 55 | 64 | 5 | 9 | 9 | 0 | 111 |
| current-16 | 20630105 | 64 | 59 | 64 | 1 | 5 | 5 | 0 | 112 |
| current-16 | 20630106 | 63 | 57 | 63 | 3 | 6 | 6 | 0 | 106 |
| fresh-16 | 20650101 | 64 | 59 | 64 | 1 | 5 | 5 | 0 | 112 |
| fresh-16 | 20650102 | 64 | 56 | 64 | 4 | 8 | 8 | 0 | 56 |
| fresh-16 | 20650103 | 64 | 59 | 64 | 1 | 5 | 5 | 0 | 110 |
| fresh-16 | 20650105 | 63 | 52 | 63 | 8 | 11 | 11 | 0 | 56 |
| fresh-16 | 20650106 | 64 | 57 | 64 | 3 | 7 | 7 | 0 | 111 |

## Support

| Support | Candidates | A112 | A112 rate | A1000 | Missing | Cap-bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 4-7 | 3 | 2 | 66.7% | 3 | 1 | 1 |
| 8-15 | 134 | 106 | 79.1% | 134 | 28 | 28 |
| 16+ | 500 | 460 | 92.0% | 500 | 40 | 40 |

## Edge family

| Cell relation | Candidates | A112 | A112 rate | Missing | Cap-bound | Never |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| flip_p | 319 | 312 | 97.8% | 7 | 7 | 0 |
| flip_q | 318 | 256 | 80.5% | 62 | 62 | 0 |

## Prediction kind

| Kind | Candidates | A112 | A1000 | Missing | Cap-bound |
| --- | ---: | ---: | ---: | ---: | ---: |
| transition | 637 | 568 | 637 | 69 | 69 |

## A112 rank bands

| Best A112 rank | A edges |
| --- | ---: |
| 1-20 | 455 |
| 21-40 | 62 |
| 41-56 | 37 |
| 57-112 | 14 |

## Missing-edge cap-1000 ranks

| Best cap-1000 rank | Missing edges |
| --- | ---: |
| 57-112 | 44 |
| 113-1000 | 25 |

## Reading

A112 rank is the best 1-based position in the shipped 112-row list. The diagnostic cap 1000 only locates edges that the shipped window excludes; it is not a proposed protocol.

## What this does not claim

A descriptive decomposition of ten no-arm 16-tag seeds at one cap pair plus a diagnostic ceiling. Cap 1000 changes reinforcement across cycles, so it locates missing edges but is not a pure window expansion. It does not establish why flip_q transitions rank lower, and it is not a treatment, target-viability or successor result.
