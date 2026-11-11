# PRESENCE-CONVERSION-2 -- result

**CONVERSION STAGE MEASURED.** The stage table locates the loss at admission: 671 of 672 present edges became candidates (C) and 16-41 per seed were never served, so construction is not the step that loses them. This is a measurement of the path, not a capability result.

## Gates

| Gate | Result |
| --- | --- |
| `N1_served_is_engine` | PASS |
| `N2_observation_cannot_leak` | PASS |
| `N3_allocation_recorded` | PASS |
| `N4_stage_complete` | PASS |
| `N5_witness_reproduces_audit` | PASS |
| `N6_seed_axis` | PASS |
| `N7_determinism` | PASS |

## Stage table

`C` is the present edges that appear as candidates in the recorded pre-cap universe; `S_ever` is the union of served windows. `A_W` is the asserted world edges at the end of the run -- an end-state stock, not a union -- so the S_ever-to-A_W difference is not read as a loss step. `Unexplained` counts asserted world edges that were never served.

| Seed | P | C | Below minimum | S_ever | Never admitted | Within 20 | 21-40 | Above 40 | A_W | Unexplained |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20611601 | 112 | 111 | 1 | 76 | 35 | 0 | 12 | 23 | 39 | 4 |
| 20611602 | 112 | 112 | 0 | 84 | 28 | 0 | 9 | 19 | 48 | 4 |
| 20611603 | 112 | 112 | 0 | 71 | 41 | 0 | 16 | 25 | 39 | 9 |
| 20611604 | 112 | 112 | 0 | 89 | 23 | 0 | 9 | 14 | 34 | 2 |
| 20611605 | 112 | 112 | 0 | 76 | 36 | 0 | 14 | 22 | 36 | 3 |
| 20611606 | 112 | 112 | 0 | 96 | 16 | 0 | 2 | 14 | 51 | 4 |
| **total** | 672 | 671 | 1 | 492 | 179 | 0 | 62 | 117 | 247 | 26 |

**What a rank is, and is not.** The universe is the ceiling call's list: every transition precedes every cooccurrence, so a rank is a block position, not an admission position. Served windows are an order-preserving subsequence of that list in 720/720 cycles; served transitions are the transition prefix in 720/720 and never rank above 20 (the 20-slot half-budget); served cooccurrences are the cooccurrence prefix in 720/720, so their ranks are offset by up to 192 transition rows (maximum served rank 212) and cannot be compared with the cap. 179 never-admitted present edges, relation(s) transition, and 0 of them ranked inside the transition budget; of the 26 asserted-without-admission edges, 10 rank inside the cap and 0 ranked inside the transitions served in its best cycle (the closest miss is 1 rank(s) short). Every recorded row is labelled and the labels form two contiguous blocks in 720/720 cycles. The label is not inferred: the engine computes it from its own cooccurrence table and uses the same variable to choose the append list, a guard test checks that in the source, and the fixture recomputes every row's label independently with no mismatch.

Never-admitted edges: the best rank one ever carried is 21-27 across seeds and the worst is 189; the per-seed median is 56, 59, 44, 41, 61, 54. Below-minimum edges: 20611601: sable>ochre.

## Decision

Report the stage table; the next step is an owner decision on the named step, with no engine change implied.

Fourteen planned runs (12 design cells, one witness, one determinism rerun) plus 6 plain N1 references. This is a measurement of the path, not a capability result.
