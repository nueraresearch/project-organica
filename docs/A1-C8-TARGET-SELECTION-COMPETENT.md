# A1 C8 target selection under the competence screen

**ID:** `A1-C8-EXPANSION-COMPETENT-1`  
**Date:** 2026-11-15  
**Status:** `TARGET SETS FORMED UNDER THE COMPETENCE SCREEN — NOT FROZEN, NOT A RESULT, NO GRANT, NO RUN`

**This is not an experimental result.** No arm cell ran; no manifest was frozen.

The published 20-row rule, with one predicate added: the no-arm A+K+ replay must record **both** an A carrier and a K path. Universe, strength test, hash order, salt and the endpoint cap of **3** are unchanged. The block falls back from 20 to the largest size that exists, never below **17**, and never to a non-competent row.

| Seed | Eligible | Competent pool | Rows | Max degree | Largest searched | Verdict |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 20740101 | 64 | 38 | **20** | 3 | 20 | FORMED — EXACT WITNESS |
| 20740102 | 64 | 27 | **17** | 3 | 20, 19, 18, 17 | FORMED — EXACT WITNESS |
| 20740103 | 64 | 37 | **20** | 3 | 20 | FORMED — EXACT WITNESS |
| 20740104 | 64 | 40 | **20** | 3 | 20 | FORMED — EXACT WITNESS |
| 20740105 | 64 | 32 | **18** | 3 | 20, 19, 18 | FORMED — EXACT WITNESS |
| 20740106 | 62 | 31 | **20** | 3 | 20 | FORMED — EXACT WITNESS |

Sizes: **20/17/20/20/18/20** — 115 target rows across the block. Sizes are decided by an exact search: a feasible size yields a witness, an infeasible one is proved by exhaustion, and a search that runs out of budget is reported `UNDECIDED` rather than as a ceiling.

## C1's denominator does not move

| Seed | A− denominator | K− denominator | Minimum |
| ---: | ---: | ---: | ---: |
| 20740101 | 81 | 79 | **79** |
| 20740102 | 64 | 81 | **64** |
| 20740103 | 84 | 79 | **79** |
| 20740104 | 82 | 74 | **74** |
| 20740105 | 72 | 83 | **72** |
| 20740106 | 74 | 82 | **74** |

C1 counts every recorded row of the cell stream, targets included, so its denominator is a property of the universe rather than of the target set — these are the same numbers the representative selection produces. Changing which edges are targets changes which rows are *not* targets, and C4's stream, but not this.

**Not evidence:** A no-arm target selection for a registered design. It freezes no manifest, reserves no seed, authorises no cell and records no C8 measurement.

Reproduce with `python -m benchmarks.a1_c8_target_selection_competent --write`; `--check` re-derives every block from the artifacts.
