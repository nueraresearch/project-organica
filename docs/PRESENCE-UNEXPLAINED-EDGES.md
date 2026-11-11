# The asserted-but-never-served edges

Generated from `docs/presence_unexplained_edges.json` by `python -m benchmarks.presence_unexplained_edges --write`. Do not edit by hand.

**Not a result artifact.** It describes the remainder the Q4 stage table counts, recomputed from the run artifact, the committed N3 campaign tables, a deterministic world and the asserted edge lists stored here. The campaign ran on 0.14.0; this record was re-derived from the same inputs on 0.15.0. It re-scores nothing.

## What is counted

A world edge is **unexplained** when it is present, asserted at the end of the run, and appears in none of the 120 served windows. `rank` is the edge's best recorded position in the ceiling call's list -- a block position, not an admission position -- and `gap` is that rank minus the transitions actually served in the cycle that ranked it, so a gap of zero or less would mean it was inside the served transitions.

## Per seed

| Seed | Present | Served | Asserted | Unexplained | In cap | Within served transitions | Rank range |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 20611601 | 112 | 76 | 39 | 4 | 2 | 0 | 31-127 |
| 20611602 | 112 | 84 | 48 | 4 | 1 | 0 | 26-61 |
| 20611603 | 112 | 71 | 39 | 9 | 3 | 0 | 26-111 |
| 20611604 | 112 | 89 | 34 | 2 | 1 | 0 | 35-41 |
| 20611605 | 112 | 76 | 36 | 3 | 2 | 0 | 22-81 |
| 20611606 | 112 | 96 | 51 | 4 | 1 | 0 | 27-82 |
| **total** | 672 | 492 | 247 | 26 | 10 | 0 | 22-127 |

## Rank bands

| 1-20 | 21-40 | 41-80 | 81-112 | 113+ |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 10 | 10 | 4 | 2 |

Relations: transition 26. The served world edges are cooccurrence 0, transition 492.

## The edges

| Seed | Edge | Rank | Gap | Band | Relation |
| ---: | --- | ---: | ---: | --- | --- |
| 20611601 | `olive>umber` | 31 | 11 | 21-40 | transition |
| 20611601 | `olive>willow` | 39 | 19 | 21-40 | transition |
| 20611601 | `willow>olive` | 127 | 107 | 113+ | transition |
| 20611601 | `willow>teal` | 124 | 104 | 113+ | transition |
| 20611602 | `amber>umber` | 61 | 41 | 41-80 | transition |
| 20611602 | `indigo>umber` | 52 | 32 | 41-80 | transition |
| 20611602 | `sable>slate` | 26 | 6 | 21-40 | transition |
| 20611602 | `willow>umber` | 54 | 34 | 41-80 | transition |
| 20611603 | `sable>yarrow` | 111 | 91 | 81-112 | transition |
| 20611603 | `slate>umber` | 27 | 7 | 21-40 | transition |
| 20611603 | `slate>yarrow` | 26 | 6 | 21-40 | transition |
| 20611603 | `umber>teal` | 28 | 8 | 21-40 | transition |
| 20611603 | `willow>verdant` | 41 | 21 | 41-80 | transition |
| 20611603 | `yarrow>indigo` | 80 | 60 | 41-80 | transition |
| 20611603 | `yarrow>sable` | 79 | 59 | 41-80 | transition |
| 20611603 | `yarrow>slate` | 81 | 61 | 81-112 | transition |
| 20611603 | `yarrow>verdant` | 77 | 57 | 41-80 | transition |
| 20611604 | `amber>maple` | 35 | 15 | 21-40 | transition |
| 20611604 | `maple>amber` | 41 | 21 | 41-80 | transition |
| 20611605 | `amber>birch` | 22 | 2 | 21-40 | transition |
| 20611605 | `sable>birch` | 31 | 11 | 21-40 | transition |
| 20611605 | `sable>teal` | 81 | 61 | 81-112 | transition |
| 20611606 | `crimson>teal` | 27 | 7 | 21-40 | transition |
| 20611606 | `ochre>amber` | 82 | 62 | 81-112 | transition |
| 20611606 | `teal>amber` | 51 | 31 | 41-80 | transition |
| 20611606 | `teal>willow` | 50 | 30 | 41-80 | transition |

## What this licenses

- **The assertion stage is not lossless, and it is not the served union.** 26 of 247 asserted world edges were never served, so `A_W` contains edges the served window never carried; the S_ever-to-A_W step cannot be read as a pure conversion loss.
- **The remainder is small and second-order.** 26 of 247 asserted edges (10.5%) are unexplained; the other 221 were served.
- **It is not a late-window artefact.** The asserted edges that were served have a per-seed median last-served cycle of 116, 117, 119, 116, 119, 117 (cycle 120 is the last), so the served asserted edges are mostly late arrivals; the unexplained set is not simply an early cohort.
- **Only 10 of the 26 sit inside the cap and 0 inside the served transitions.** The closest in-cap miss is 2 rank(s) short.

## What it does not license

- Not a mechanism: it does not show *why* an asserted edge was never served.
- Not a defect: it does not show that serving them would have changed `A_W`, and it does not make the admission rule wrong.
- Not a prediction: nothing here says cap 112 would serve them; that is the registered cap-112 arm's question.
- Not a capability, retention or transfer claim: one world family, six seeds, one cap, one build.
- The asserted edge lists are stored as an input; their count and digest are checked against the run, but storing them is not a second measurement.
