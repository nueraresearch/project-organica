# T1b — persistence-off at cap 112, with a zero-admitting denominator

**Status.** FROZEN, RUN. This page is rendered from `docs/t1b_persistence_off_prereg.json`; it is not edited by hand.

| Field | Value |
| --- | --- |
| Preregistration | `T1B-PERSISTENCE-OFF` |
| Frozen on | 2026-11-11 |
| Engine | 0.15.0, cap 112, none |
| Question | At the shipped cap of 112, does conversion from constructed edges to served and asserted edges depend on temporal edge counts carried across sleep cycles, when a zero S_ever is read as a measured count rather than as an unmeasurable stage? |
| Cells planned | 12 (2 arms x 6 seeds = 12 cells) |
| Seeds | 20612208, 20612209, 20612210, 20612211, 20612212, 20612213; bootstrap 20612214 |
| Cycles | 120 |
| Runner | built |
| Cells run | 13 |
| Authorisation | granted |

## Why T1b exists

T1 ran and returned VOID because its frozen G4 treated a zero S_ever as unmeasurable. T1b changes only that reading, before any cell: P is the denominator and S_ever is a measured count, so zero is a value. T1's twelve cells are not re-read, and this block runs six fresh seeds on the same two arms.

## Arms

| Arm | Service | Carried temporal counts |
| --- | --- | --- |
| shipped | `organica.sleep.SleepService` | the decayed count is carried across cycles |
| persistence_off | `benchmarks.t1b_persistence_off_arm.PersistenceOffMemory with the shipped SleepService` | reset to zero at the end of every cycle |

**Manipulation.** A MemoryService subclass overrides decay_temporal_edges to set every precedes row to count = 0 at the end of each cycle instead of carrying the decayed count forward. The temporal read requires count >= 1, so a reset edge is not returned; an edge observed once in the next cycle increments from 0 to 1 and is returned. Rows are not deleted, the schema is unchanged, and no engine file is edited.

## Endpoints

| Stage | Definition | Role |
| --- | --- | --- |
| P | present world edges: the world's edges, the denominator of every share | denominator |
| C | constructed candidates: the pre-cap universe intersect the world | secondary |
| S_ever | served world edges: the union of every served window intersect the world, counted once; zero is a measured count | primary |
| A_W | asserted world edges at the end of the run | secondary |
| U | asserted world edges that never enter a served window | reported, not a verdict |

The stage table is recomputed from each cell's committed per-cycle tables. S_ever is a union, not a sum, so an edge served twice counts once; it may be zero, and zero is reported as zero rather than excluded. Every stage is reported as a count and as a share of P, and no ratio is a verdict.

## Gates

| Gate | Rule |
| --- | --- |
| `G1_build` | both arms run the shipped 0.15.0 build at cap 112 and the pin is unchanged; an engine edit voids the block |
| `G2_world` | each seed contributes one world and stimulus to both arms; a differing world digest voids the pair |
| `G3_manipulation_live` | after the first cycle of every treatment cell the maximum carried temporal count is zero at the end of each cycle, and the control's maximum exceeds zero in at least one cycle on every seed; a reset that never fires, or a control that also resets, is void |
| `G4_denominator` | P is non-zero in every cell; S_ever is a measured count, so a zero S_ever is admissible and read as zero served edges; a zero P is not measurable and voids the block |
| `G5_seed_axis` | the six shipped cells hold at least three distinct (S_ever, A_W) pairs; one outcome repeated six times is not a seed axis |
| `G6_determinism` | the first seed re-run reproduces its stage row exactly |
| `G7_cells` | exactly twelve cells, both arms x six seeds, with no extra seed, cap or cycle |

**G4 is the correction.** T1's G4 required P *and* S_ever to be non-zero. Here P is the denominator and S_ever is a count: a zero S_ever is read as zero served edges, not as a missing stage. A zero P still voids the block.

## Decision rule

The primary endpoint is the paired per-seed difference in S_ever, shipped minus persistence-off. The table is read once, in the frozen order, and both directions are decisions: a shortfall names persistence as the lever, no shortfall names the in-cycle stage. A zero S_ever in either arm is a value on this endpoint, not a missing measurement.

Margin: 10 edges, 5 of 6 seeds in the same direction, paired bootstrap 95% lower bound above zero, 10000 resamples at seed 20612214. 10 is the smallest difference the cap decision treated as decision-relevant (Q2's ten-edge bar), imported as a declared margin and unchanged from T1. Five of six seeds guards against one seed; the paired interval guards the magnitude. T1's observed differences are not used to set the bar; only the denominator reading changes.

## Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| any gate fails | **VOID** | the block is unrun or non-measurable and the failed gate names what did not happen | record VOID; fix the harness and register a new block; read no endpoint |
| gates pass; shipped S_ever exceeds persistence-off by at least the margin on at least five of six seeds, with the paired lower bound above zero | **PERSISTENCE CONTRIBUTES** | carried counts are a necessary input to conversion at cap 112: removing the carry removes served edges at the same cap, world and seed | pursue the persistence mechanism (decay, floor, denominator); do not read the cap arm as an answer to this question |
| gates pass; the difference is at or below zero, or at most two seeds are positive, or the paired interval's upper bound is below the margin | **PERSISTENCE NOT LIMITING** | conversion at 112 is created inside the cycle; carried counts do not explain the served or asserted stage | pursue the in-cycle stage (construction or admission), and stop treating retention as the conversion lever |
| gates pass; the direction or magnitude falls between the two rows | **MIXED** | the direction is not resolved and the per-seed rows disagree | make no mechanism claim; the only follow-up is a larger fresh seed axis, not a re-read of this block |

## Prediction, stated before any cell

**Prediction.** The Q4 artifact records 26 asserted edges that never enter a served window and T1 observed two persistence-off cells with zero served world edges. If carried support keeps an edge available between cycles, the persistence-off arm should serve and assert fewer world edges. The record does not commit to a magnitude, and a zero S_ever is inside the endpoint rather than outside it.

## Cost and stop

**Cost.** twelve cells plus the determinism rerun at 120 cycles each

**Stop condition.** any gate failure stops the block as VOID; no endpoint is read, no direction is chosen and no cell is rerun to escape the gate


## Result

**PERSISTENCE CONTRIBUTES** -- `docs/t1b_persistence_off_run.json`, 2026-11-11.

All seven gates pass. G4 passes with P = 112 in every cell and three persistence-off cells at S_ever = 0 (seeds 20612208, 20612210, 20612212); those zeros are measured counts, not unmeasurable stages. The paired differences are 101, 94, 100, 100, 98 and 96 (mean 98.167, 95% interval [96, 100]), positive on 6 of 6 seeds against the margin of 10. No gate was changed after the cells ran.


## What this record does not license

The block reads one ablation on six fresh seeds at cap 112. It is not a capability, retention or transfer claim, and it does not re-read T1's cells or Q2's and Q4's verdicts.
