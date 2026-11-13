# Matched carrier base-rate replication

Generated from `docs/matched_carrier_replication_2.json` by `python -m benchmarks.matched_carrier_replication --write`. Do not edit by hand.

**Verdict: `REPLICATED`.** The design was frozen in `docs/matched_carrier_replication_2_prereg.json` before the fresh block ran.

## Design

- Seeds: **20615201, 20615202, 20615203, 20615204, 20615205, 20615206** (collision scan empty).
- **120** cycles, cap **40**, PHASE_ACQUISITION schedule, one replay per seed.
- Case: asserted world edge with zero direct served windows.
- Control: same-seed world edge that is neither asserted nor served.
- Matching: cases sorted by (final temporal count, edge); each case takes the nearest unused same-seed control by |final temporal count difference|; ties by lexicographically smaller edge; 1:1, no replacement.
- Endpoint: `ever_loop`, a reported `loop_candidate` path containing the edge in either orientation in any cycle.

## Voided prior attempt

`MATCHED-CARRIER-REPLICATION-1` on seeds 20615101, 20615102, 20615103, 20615104, 20615105, 20615106 is not read: The first pipeline matched on served-window counts, which are zero for every never-served edge, instead of the final temporal count. The control sample is therefore not the matched sample the census defines, and no contrast from that run is read. The seeds are not reused here.
The voided record is `.scratch/matched_carrier_replication_1_void.json`.

## Result

| Quantity | Original Q4 | Fresh block |
| --- | ---: | ---: |
| Matched pairs | 26 | 29 |
| Cases ever looping | 26/26 | 29/29 |
| Controls ever looping | 13/26 | 11/29 |
| Risk difference | +50.0 pp | +62.1 pp |
| Risk ratio | 2.00 | 2.64 |
| Seed-cluster 95% CI | [34.5, 69.6] pp | [38.5, 85.2] pp |
| Exact McNemar p | 2.40e-04 | 7.63e-06 |

### Paired table

| | Control loops | Control does not loop |
| --- | ---: | ---: |
| **Case loops** | 11 | 18 |
| **Case does not loop** | 0 | 0 |

Discordant pairs: **18** case-only, **0** control-only. Unmatched cases: **0**.

| Criterion | Passes |
| --- | --- |
| R1 case rate > control rate | yes |
| R2 exact McNemar p < 0.05 | yes |
| R3 cluster 95% interval above 0 | yes |
| Original +50 pp inside fresh interval (descriptive) | yes |

## Per seed

| Seed | World edges | Asserted | Served | Cases | Controls | Pairs | Case loops | Control loops |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20615201 | 112 | 52 | 91 | 4 | 17 | 4 | 4 | 3 |
| 20615202 | 112 | 31 | 63 | 5 | 44 | 5 | 5 | 4 |
| 20615203 | 112 | 26 | 70 | 4 | 38 | 4 | 4 | 1 |
| 20615204 | 112 | 33 | 83 | 4 | 25 | 4 | 4 | 0 |
| 20615205 | 112 | 42 | 80 | 3 | 29 | 3 | 3 | 0 |
| 20615206 | 112 | 43 | 72 | 9 | 31 | 9 | 9 | 3 |

## Every matched pair

| Seed | Case | Count | Loop | Control | Count | Loop | |diff| |
| ---: | --- | ---: | --- | --- | ---: | --- | ---: |
| 20615201 | `cedar>birch` | 27 | yes | `cedar>sable` | 27 | yes | 0 |
| 20615201 | `teal>birch` | 27 | yes | `cedar>amber` | 30 | no | 3 |
| 20615201 | `crimson>birch` | 29 | yes | `verdant>sable` | 31 | yes | 2 |
| 20615201 | `amber>crimson` | 35 | yes | `amber>teal` | 41 | yes | 6 |
| 20615202 | `crimson>cedar` | 24 | yes | `olive>ochre` | 24 | yes | 0 |
| 20615202 | `willow>umber` | 27 | yes | `indigo>olive` | 26 | no | 1 |
| 20615202 | `fern>cedar` | 31 | yes | `fern>umber` | 31 | yes | 0 |
| 20615202 | `birch>fern` | 34 | yes | `fern>ochre` | 32 | yes | 2 |
| 20615202 | `crimson>umber` | 34 | yes | `indigo>slate` | 40 | yes | 6 |
| 20615203 | `umber>olive` | 18 | yes | `cedar>olive` | 19 | no | 1 |
| 20615203 | `umber>amber` | 27 | yes | `indigo>fern` | 27 | yes | 0 |
| 20615203 | `umber>fern` | 29 | yes | `slate>ochre` | 29 | no | 0 |
| 20615203 | `birch>umber` | 39 | yes | `birch>indigo` | 37 | no | 2 |
| 20615204 | `maple>fern` | 22 | yes | `birch>fern` | 22 | no | 0 |
| 20615204 | `olive>fern` | 38 | yes | `sable>willow` | 35 | no | 3 |
| 20615204 | `olive>willow` | 39 | yes | `verdant>slate` | 33 | no | 6 |
| 20615204 | `olive>teal` | 40 | yes | `willow>sable` | 31 | no | 9 |
| 20615205 | `crimson>ochre` | 13 | yes | `teal>sable` | 13 | no | 0 |
| 20615205 | `fern>amber` | 31 | yes | `cedar>slate` | 29 | no | 2 |
| 20615205 | `indigo>birch` | 41 | yes | `yarrow>maple` | 42 | no | 1 |
| 20615206 | `umber>sable` | 28 | yes | `willow>amber` | 27 | yes | 1 |
| 20615206 | `birch>yarrow` | 29 | yes | `ochre>sable` | 30 | yes | 1 |
| 20615206 | `verdant>yarrow` | 29 | yes | `yarrow>umber` | 31 | no | 2 |
| 20615206 | `verdant>sable` | 30 | yes | `willow>maple` | 33 | no | 3 |
| 20615206 | `birch>sable` | 32 | yes | `willow>verdant` | 33 | no | 1 |
| 20615206 | `yarrow>birch` | 32 | yes | `indigo>maple` | 35 | no | 3 |
| 20615206 | `yarrow>maple` | 41 | yes | `fern>verdant` | 42 | no | 1 |
| 20615206 | `cedar>birch` | 43 | yes | `indigo>verdant` | 43 | yes | 0 |
| 20615206 | `umber>willow` | 53 | yes | `cedar>umber` | 46 | no | 7 |

## What this does and does not establish

The fresh block tests whether the matched loop contrast repeats. It does not test loop retention, whether loops cause assertion, whether serving a direct edge would change the final structure, or any capability claim. The original +50 pp is shown for comparison only; the verdict is fixed by R1-R3.

A six-seed diagnostic of one matched contrast in one synthetic world family. It is not a capability, retention, transfer, causal or engine-effect claim, and it does not show that loops cause assertion.
