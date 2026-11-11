# PRESENCE-BAND-4 — confirmatory allocation block

**Status.** FROZEN, NOT RUN. This page is rendered from `docs/presence_band_rank_4_prereg.json`; it is not edited by hand.

| Field | Value |
| --- | --- |
| Preregistration | `PRESENCE-BAND-4` |
| Frozen on | 2026-11-11 |
| Engine | 0.15.0, cap 112, none |
| Cells planned | 12 (2 caps x 6 seeds = 12 cells) |
| Seeds | 20612501, 20612502, 20612503, 20612504, 20612505, 20612506 |
| Caps | 40, 112 |
| Cycles | 120 |
| Band | measured per seed; no fixed total |
| Runner | not built |
| Cells run | 0 |
| Authorisation | not granted |

## The reconciliation

**Frozen point.** BAND-1's B5 required exactly 56 transitions at cap 112.

**Engine law.** `organica/sleep_extraction.py` sets `transition_budget = returned_budget // 2` (56 at 112), seats up to 56 cooccurrences in the remainder, then backfills unused cooccurrence slots with further transitions (`more_trans`). A full window therefore has `transitions + cooccurrences = 112` with `transitions >= 56` and `cooccurrences <= 56`.

**Observed 64-69.** The six BAND-1 cells served 64-69 transitions, so their full-window cooccurrence counts were 48-43. That is the floor plus backfill; it is not a new allocation rule and it is not an acceptance threshold.

**Why not exact 56.** A correct engine can serve more than 56 transitions whenever fewer than 56 cooccurrence candidates fill the remainder. Requiring exactly 56 rejects a healthy backfill.

**Why not a floor alone.** A floor-only gate accepts 56 transitions with no cooccurrences in a 56-row window. That is not the full allocation law and would pass without showing the backfill that produced 64-69. BAND-4 therefore requires a full 112-row window and the sum identity.

**Not fitted to the observation.** The law and its fixtures are written from `sleep_extraction.py` before any BAND-4 cell. The observed 64-69 is a consistency check, not a calibrated range, and no threshold is set to 64 or 69.

## Design

| Field | Value |
| --- | --- |
| Arms | cap 40 and cap 112 |
| Variable | `SleepService.MAX_PREDICTIONS, set per cell` |
| Observer | the repaired observer of PRESENCE-CONVERSION-2, returning the engine's own served list and recording the pre-cap universe and allocation |
| World | the compositional world family of PHASE_ACQUISITION at 120 cycles on six fresh seeds; no Q4, BAND-1, BAND-2 or BAND-3 world is reused |
| Pairing | each seed contributes one world and one stimulus to both caps; only the cap changes, and each band edge is paired across the two cells |
| Freshness | All six seeds are fresh at freeze time: seed_collisions over every docs JSON returns no hit. The record and page are the only allowed artifacts that name them. |
| Reuse | No prior block's cells, named band or result is reused. The 64-69 observation is cited only as the prior that motivates the allocation law; it is not BAND-4 evidence. |
| Cycles | 120 |
| Cells | 12 |

## Band

**Definition.** For each seed, the band is every present transition whose minimum block rank in the cap-112 ceiling universe is 21-40. It is measured from the 112 arm and is not filtered by cap-40 service.

**Derivation.** Read the cap-112 cell's present_edges and universe; keep each edge whose relation is transition and whose minimum recorded rank is 21-40. A missing rank is a failure, not a zero.

**Zero band.** A seed with zero rank-21-40 present transitions is a zero denominator: B6 fails and the block is VOID, never split as 0 served.

**Service separation.** Band membership is independent of cap-40 service and is not filtered by it. B4 measures whether the 40 arm served a band edge.

## Endpoints

| Stage | Definition | Role |
| --- | --- | --- |
| W | world edges generated for the seed | denominator |
| P | world edges present in the temporal graph | band universe |
| band | present transitions at minimum block rank 21-40 in the 112 ceiling | measured treatment group |
| S40 | band edges served in at least one cap-40 cycle | pre-treatment control |
| S112 | band edges served in at least one cap-112 cycle | band endpoint |
| A112 | band edges asserted at the end of the cap-112 run | secondary, reported not adjudicated |
| alloc | per cycle transitions and cooccurrences in the 112 window | allocation endpoint |
| ledger | per edge: rank, cycles served at each cap, asserted, relation | per-edge record |

## Gates

| Gate | Rule |
| --- | --- |
| `B1_build` | all twelve cells run the shipped 0.15.0 build at the named cap, with one sha256 across the run and only MAX_PREDICTIONS overridden; a mixed or edited build is VOID |
| `B2_world_fresh` | each seed's world digest and present fingerprint are identical at 40 and 112, and every seed is absent from every prior docs artifact; a different world or a reused seed is VOID |
| `B3_band_identity` | at cap 112 every band edge is a present transition whose minimum recorded rank is 21-40 and whose rank is present; each seed's band is non-empty; a missing edge, duplicate, missing rank or out-of-band rank fails B3. The band is read before cap-40 service is considered. |
| `B4_control_40` | at cap 40 no band edge is served on any seed, and the 40-row allocator satisfies the same sum identity with its 20-transition floor; a band edge served at 40, an incomplete full window, or a 40-row allocation that does not sum fails B4 |
| `B5_allocation_law` | at cap 112 every cell has at least one full 112-row window; every full window satisfies transitions >= 56, cooccurrences <= 56 and transitions + cooccurrences = 112, and every allocation row sums to its own served window. The maximum served transition rank is above block rank 40, every served edge parses as exactly one source>target, and every served transition is ranked. A 56-transition, 56-row window; a 64-transition, 104-row sum; a cooccurrence count above 56; a rank ceiling at 40; an unparseable edge; or an unranked served transition fails B5. B5 is not conditional on band service. |
| `B6_denominator` | each seed's band is non-empty and every band edge reaches the ledger; a zero band or a zero P is not measurable and is VOID, never 0.0 |
| `B7_determinism` | a fresh-process rerun of seed 20612501 at 112 reproduces its per-edge ledger and allocation exactly |
| `B8_seed_axis` | the six 112 ledgers hold at least three distinct served-band edge sets; a repeated set is one world, not six |

## B5 fixtures

| Fixture | Expected |
| --- | --- |
| 64 transitions + 48 cooccurrences in a 112-row window, maximum rank 64 | PASS |
| 56 transitions + 56 cooccurrences in a 112-row window, maximum rank 56 | PASS |
| 56 transitions + 0 cooccurrences in a 56-row window | FAIL |
| 20 transitions + 20 cooccurrences in a 40-row window | FAIL |
| 64 transitions + 40 cooccurrences in a 112-row window | FAIL |
| 64 transitions + 60 cooccurrences in a 124-row window | FAIL |
| a full window whose maximum served transition rank is 40 | FAIL |
| a served transition with no recorded rank | FAIL |
| an edge with more than one source>target separator | FAIL |

the same allocation_law helper is used by the record check and the future arm; the pass fixtures cover both the observed backfill shape and the exact floor, and every failure fixture must fail

## Acceptance can fail independently

**Criterion A — allocation.** B5 passes: the cap-112 allocation law holds on every full window and the rank ceiling is live.

**Criterion B — band.** B3, B4 and B6 pass: every measured rank-21-40 band edge is served at 112, none is served at 40, and the seed axis is live.

**Confirmed.** CONFIRMED only when both criterion A and criterion B pass.

**Independent failure.** The criteria fail independently: a block with perfect band service but a failed B5 is ALLOCATION LAW NOT CONFIRMED. A block with a perfect allocation but any unserved band edge is BAND NOT CONFIRMED. Neither result can be averaged into or rescued by the other.

**Not fitted.** The 64-69 observation is not used as a threshold. The allocation identity is fixed from the engine source, and the band criterion is the same rank rule fixed before the cells.

Source: `organica/sleep_extraction.py and docs/DECISION-ADMISSION-STEP.md`.

## Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| B1, B2, B3 identity, B6, B7 or B8 fails | **VOID** | the block is unrun or non-reproducible and the failed gate names what did not happen | record VOID; fix the failed gate and register a new block; read no acceptance |
| allocation law fails, band service passes | **ALLOCATION LAW NOT CONFIRMED** | the band can be served while the full-window floor-plus-backfill identity is false | report the allocation failure; do not call the band a confirmation; fix the allocation rule before another band block |
| allocation law passes, any band edge is unserved at 112 or served at 40 | **BAND NOT CONFIRMED** | the allocation is correct but the measured rank-21-40 band does not enter service as claimed | report the per-edge misses; the next step is the admission rule, not another cap level |
| allocation law and band service both pass on every seed | **CONFIRMED** | the floor-plus-backfill law and fresh-world rank-21-40 service both hold | record the confirmation; the owner decides any engine or promotion step; no capability claim |

## Grant and stop

**Authorisation.** No dated grant exists. A grant naming the twelve cells, the determinism rerun and the result artifact must be recorded against this record before an arm is built or a cell is opened. This record authorises nothing to run.

**Cost.** 12 cells (one fresh-process determinism rerun) x 120 cycles.

**Stop condition.** No cell runs until a dated grant is recorded and the arm's preflight passes. After that, the block closes when the twelve cells and rerun have produced their parts, B1-B8 have been scored once in the frozen order, and the verdict is recorded. Any gate failure is VOID; no cell is rerun to escape a gate and no gate is amended after a result.

## What this record does not license

A preregistration and page, not a result. No grant, arm, runner or cell exists. BAND-1 stays VOID; BAND-2 and BAND-3 stay unrun and are not re-read. This record licenses no capability, retention or transfer claim.
