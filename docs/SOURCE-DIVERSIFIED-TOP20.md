# Source-diversified top 20 — post hoc diagnostic

Generated from `docs/source_diversified_top20.json` by `python -m benchmarks.source_diversified_top20 --write`. Do not edit by hand.

**Verdict: `NO RELIABLE RECOVERY GAIN`.** A cap of three seats per source recovers **one** additional positive, on one seed. It is not a reliable recovery gain.

## Population

The source is the six-seed never-served replication: **212** never-served edges across six seeds, of which **26** are asserted. Each seed is ranked separately by the observed minimum pre-cap rank, then top 20 is taken. That gives **120** seats, not one global list, because an edge string can occur in more than one seed.

| Measure | Uncapped | Cap 3 |
| --- | ---: | ---: |
| Selected seats | **120** | **120** |
| Full 20-seat windows | **6 / 6** | **6 / 6** |
| Asserted edges recovered | **18 / 26** | **19 / 26** |
| Recovery rate | **69.2%** | **73.1%** |
| Baseline seats displaced | — | **8** |
| Displaced that were asserted | — | **0** |
| New seats added | — | **8** |
| Added that were asserted | — | **1** |

The one added positive is the whole gain. Every displaced seat was a non-asserted edge, so the cap did not trade a positive away on this ordering — but it also recovered only one of the eight positives the uncapped top 20 leaves out.

## Cap sweep

| Cap per source | Seats | Full windows | Recovered / 26 | Displaced | Displaced asserted | Added | Added asserted |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 73 | 0 | **10** | 61 | 9 | 14 | 1 |
| 2 | 115 | 4 | **18** | 26 | 3 | 21 | 3 |
| 3 | 120 | 6 | **19** | 8 | 0 | 8 | 1 |
| 4 | 120 | 6 | **18** | 2 | 0 | 2 | 0 |
| 5 | 120 | 6 | **18** | 0 | 0 | 0 | 0 |

Cap 1 cannot fill a 20-seat window on any seed and is not comparable. Cap 2 loses three asserted baseline seats and recovers no more than the uncapped list. Cap 3 is the only cap with a positive net gain; cap 4 and above are the baseline or worse.

## Per-seed detail at cap 3

| Seed | Rows | Asserted rows | Recovered | Baseline recovered | Displaced | Added |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20613101 | 31 | 1 | **1** | 0 | 4 | 4 |
| 20613102 | 37 | 5 | **3** | 3 | 1 | 1 |
| 20613103 | 33 | 1 | **1** | 1 | 0 | 0 |
| 20613104 | 32 | 8 | **5** | 5 | 1 | 1 |
| 20613105 | 40 | 6 | **6** | 6 | 0 | 0 |
| 20613106 | 39 | 5 | **3** | 3 | 2 | 2 |

The gain is confined to seed **20613101**: its uncapped list recovers **0 / 1**, while the cap-3 list recovers **1 / 1**.

## Rank sensitivity

The result depends on which stored rank defines the list. The same cap does not gain under median-rank or final-rank ordering:

| Ranking field | Uncapped recovered | Cap-3 recovered | Cap-3 positives displaced |
| --- | ---: | ---: | ---: |
| `min_rank` | **18** | **19** | **0** |
| `median_rank` | **25** | **23** | **3** |
| `final_rank` | **24** | **23** | **3** |

## What this does and does not establish

This is a post-hoc re-ranking of already-observed never-served edges, not an engine arm. It does not show that a source cap would change the served window, assertion, acquisition, transfer or capability. The uncapped list already recovers 18 of 26, and the capped list recovers 19; the difference is one edge on one seed and reverses its sign under other stored rank fields.

A post-hoc re-ranking of the 212 never-served edges already observed in the six-seed replication. The top 20 is per seed, not the engine's served window. The one additional recovery is on one seed and does not survive median-rank or final-rank ordering. No engine cell ran, no fresh seed was spent, and no served prediction, assertion, acquisition, transfer or capability claim follows.
