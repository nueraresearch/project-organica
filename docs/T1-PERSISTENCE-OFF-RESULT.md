# T1 -- persistence-off at cap 112: result

**VOID.** A gate failed, so the block measured nothing and no endpoint is read.

## Gates

| Gate | Result |
| --- | --- |
| `G1_build` | PASS |
| `G2_world` | PASS |
| `G3_manipulation_live` | PASS |
| `G4_denominator` | FAIL |
| `G5_seed_axis` | PASS |
| `G6_determinism` | PASS |
| `G7_cells` | PASS |

## Per-seed endpoint (computed, not adjudicated)

`S_ever` is the union of served windows intersected with the world; `A_W` is the asserted world edges at the end of the run. The primary endpoint is the paired difference in `S_ever`, shipped minus persistence-off.

| Seed | Shipped S_ever | Off S_ever | Difference | Shipped A_W | Off A_W |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20612201 | 97 | 9 | 88 | 78 | 5 |
| 20612202 | 106 | 3 | 103 | 72 | 0 |
| 20612203 | 103 | 6 | 97 | 50 | 0 |
| 20612204 | 102 | 0 | 102 | 53 | 0 |
| 20612205 | 95 | 0 | 95 | 58 | 0 |
| 20612206 | 94 | 5 | 89 | 42 | 0 |

**Paired mean 95.667**, 95% interval [91.167, 100.167], 6 of 6 seeds at or above the margin of 10, 10000 resamples at seed 20612207.

## Decision

Record VOID; fix the gate named here and register a new block.

One ablation, six seeds, one build; the direction is the claim, not an effect size. This result does not re-read Q4's stage table or Q2's cap verdict.

**No endpoint is adjudicated.** The frozen decision table reads no endpoint when a gate fails, so the per-seed differences above are reported as computed values, not as a verdict. G4 failed because two persistence-off cells served zero world edges; that is the finding the gate records, and the gate is not relaxed after the run.
