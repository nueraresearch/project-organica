# T1b -- persistence-off at cap 112: result

**PERSISTENCE CONTRIBUTES.** Removing the carried temporal count removes served world edges at the same cap, world and seed: 6 of 6 seeds lose at least 10 edges.

## Gates

| Gate | Result |
| --- | --- |
| `G1_build` | PASS |
| `G2_world` | PASS |
| `G3_manipulation_live` | PASS |
| `G4_denominator` | PASS |
| `G5_seed_axis` | PASS |
| `G6_determinism` | PASS |
| `G7_cells` | PASS |

## Per-seed endpoint

`S_ever` is the union of served windows intersected with the world; `A_W` is the asserted world edges at the end of the run. A zero `S_ever` is shown as zero: P is the denominator and it is non-zero in every cell.

| Seed | Shipped S_ever | Off S_ever | Difference | Shipped A_W | Off A_W |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20612208 | 101 | 0 | 101 | 57 | 0 |
| 20612209 | 95 | 1 | 94 | 53 | 0 |
| 20612210 | 100 | 0 | 100 | 65 | 0 |
| 20612211 | 103 | 3 | 100 | 62 | 2 |
| 20612212 | 98 | 0 | 98 | 54 | 0 |
| 20612213 | 99 | 3 | 96 | 57 | 0 |

**Paired mean 98.167**, 95% interval [96.000, 100.000], 6 of 6 seeds at or above the margin of 10, 10000 resamples at seed 20612214. Zero S_ever cells: 20612208/persistence_off, 20612210/persistence_off, 20612212/persistence_off.

## Decision

Pursue the persistence mechanism (decay, floor, denominator); the cap arm does not answer this question.

One ablation, six seeds, one build; the direction is the claim, not an effect size. This result does not re-read T1's cells or Q4's stage table or Q2's cap verdict.
