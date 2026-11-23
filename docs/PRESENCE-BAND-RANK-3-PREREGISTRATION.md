# PRESENCE-BAND-3 — fresh worlds, the fixed band, and a B5 that can fail

**Status.** FROZEN, NOT RUN. This page is rendered from `docs/presence_band_rank_3_prereg.json`; it is not edited by hand.

| Field | Value |
| --- | --- |
| Preregistration | `PRESENCE-BAND-3` |
| Frozen on | 2026-11-11 |
| Engine | 0.15.0, cap 112, none |
| Question | On the shipped 0.15.0 build, with six fresh worlds, does raising the Layer-1 cap from 40 to 112 put every measured rank-21-40 present transition into service, with B1-B8 passing and B5 still able to fail? |
| Cells planned | 12 (2 caps x 6 seeds = 12 cells) |
| Seeds | 20612401, 20612402, 20612403, 20612404, 20612405, 20612406 |
| Caps | 40, 112 |
| Cycles | 120 |
| Band | measured per seed; no fixed total |
| Runner | not built |
| Cells run | 0 |
| Authorisation | granted |

## Why a third block

BAND-1 named Q4's 62 rank-21-40 edges and was VOID on B5. BAND-2 fixed B5 and the rank reader but reused Q4's worlds, so it could not test a fresh-world band. BAND-3 keeps the fixed parser and the corrected floor, re-derives the band in six unused worlds, and leaves the cap-live gate able to fail. BAND-1 remains VOID and BAND-2 remains unrun and is not re-read as this block's evidence.

## The band is measured, not named before the run

For each seed, the band is every present transition whose minimum block rank in the cap-112 ceiling universe is 21-40. The band is measured from the 112 arm; it is not fixed to 62 edges and it is not filtered by cap-40 service.

**Derivation.** Read the cap-112 cell's present_edges and universe; keep each edge whose relation is transition and whose minimum recorded rank is 21-40. A missing rank is a failure, not a zero.

**Zero band.** A seed with zero rank-21-40 present transitions is a zero denominator: B6 fails and the block is VOID, never split as 0 served.

**Service separation.** Band membership is independent of cap-40 service and is not filtered by cap-40 service. B4 measures whether the 40 arm served a band edge; it is not removed from the band to make B4 pass.

## Design

| Field | Value |
| --- | --- |
| Arms | cap 40 and cap 112 |
| Variable | `SleepService.MAX_PREDICTIONS, set per cell` |
| Observer | the repaired observer of PRESENCE-CONVERSION-2, returning the engine's own served list and recording the pre-cap universe with a second call |
| World | the compositional world family of PHASE_ACQUISITION at 120 cycles on six fresh seeds; no Q4 world is reused |
| Pairing | each seed contributes one world and one stimulus to both caps; only the cap changes, and each band edge is paired across the two cells |
| Freshness | All six seeds are fresh and unused at freeze time: seed_collisions over every docs JSON returns no hit. The record and page are the only allowed artifacts that name them. |
| Reuse | No Q4 seed, no named Q4 band and no BAND-1 or BAND-2 cell is reused. This is a fresh-world generalisation of the rank rule, not a replication of the 62 named edges. |
| Cycles | 120 |
| Cells | 12 |

## Endpoints

| Stage | Definition | Role |
| --- | --- | --- |
| W | world edges generated for the seed | denominator |
| P | world edges present in the temporal graph | band universe |
| band | present transitions at minimum block rank 21-40 in the 112 ceiling | measured treatment group |
| S40 | band edges served in at least one cap-40 cycle | pre-treatment control |
| S112 | band edges served in at least one cap-112 cycle | primary endpoint |
| A112 | band edges asserted at the end of the cap-112 run | secondary, reported not adjudicated |
| ledger | per edge: rank at each cap, cycles served, first served cycle, asserted, relation | per-edge record |

## Gates

| Gate | Rule |
| --- | --- |
| `B1_build` | all twelve cells run the shipped 0.15.0 build at the named cap, with one sha256 across the run and only MAX_PREDICTIONS overridden; a mixed or edited build is VOID |
| `B2_world_fresh` | each seed's world digest and present fingerprint are identical at 40 and 112, and every seed is absent from every prior docs artifact; a different world or a reused seed is VOID |
| `B3_band_identity` | at cap 112 every band edge is a present transition whose minimum recorded rank is 21-40 and whose rank is present; each seed's band is non-empty; a missing edge, duplicate, missing rank or out-of-band rank fails B3. The band is read before cap-40 service is considered. |
| `B4_control_40` | the 40 arm serves exactly 20 transitions and 0 band edges on every seed; a band edge served at 40, or a transition count other than 20, fails B4 |
| `B5_cap_live` | the 112 arm has at least 56 transitions, a maximum served transition rank above block rank 40, no window above 112 rows, every served edge parsed as exactly one source>target, and every served transition ranked. A fixture with 20 transitions, or with 56 transitions but a maximum served rank of 40, must fail B5; B5 is not conditional on band service. A short count, a rank ceiling at or below 40, an overfull window, an unparseable edge or an unranked served transition is VOID. |
| `B6_denominator` | each seed's band is non-empty and every band edge reaches the ledger; a zero band or a zero P is not measurable and is VOID, never 0.0 |
| `B7_determinism` | a fresh-process rerun of seed 20612401 at 112 reproduces its per-edge ledger exactly |
| `B8_seed_axis` | the six 112 ledgers hold at least three distinct served-band edge sets; a repeated set is one world, not six. Distinct served counts are not required because fresh band sizes may differ. |

## Fixed harness and a B5 that can fail

The strict `source>target` parser and the minimum-rank lookup are imported from `benchmarks.presence_band_rank_2_prereg`. B5 is scored by `b5_cap_live`, the same helper the future arm must use.

| Fixture | Expected |
| --- | --- |
| 56 transitions, maximum served transition rank 56 | PASS |
| 20 transitions | FAIL |
| 56 transitions with maximum served transition rank 40 | FAIL |
| a served transition with no recorded rank, or an unparseable edge | FAIL |

the same b5_cap_live helper is used by the arm and by the check; the fixture must show both pass and fail

## Acceptance condition

> The 21–40 transitions must be served at 112 and the block's own gates must pass, per seed, with the seed axis live.

Source: `docs/DECISION-ADMISSION-STEP.md`. The condition is the decision's, unchanged; this block adjudicates whether it holds and does not decide what follows.

## Prediction, stated before any cell

**Prediction.** Every measured band edge is served at 112 on every seed and none at 40; B5 passes with at least 56 transitions and a maximum served transition rank above 40.

**Because.** The 112 floor is 56 and the band is ranks 21-40 by construction. BAND-1 observed 62/62 served at 112 on its Q4 worlds; this is a fresh-world generalisation, not a discovery.

**Prior observation.** BAND-1's band was served 62/62 at 112 and 0/62 at 40, but BAND-1 is VOID on its B5. BAND-2 corrected B5 but reused the same worlds and is unrun. Neither is BAND-3's evidence.

**Falsifier.** Any band edge unserved at 112, any band edge served at 40, any B5 failure, an empty band, a rank mismatch, an unparseable edge, or a missing rank.

A pass is fresh-world service for one world family and build; it is not a capability, retention or transfer claim.

## Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| any gate other than B3 fails | **VOID** | the block is unrun or non-reproducible and the failed gate names what did not happen | record VOID; fix the failed gate and register a new block; read no acceptance |
| B3 fails: a band edge is missing, duplicate, unranked, or not ranked 21-40 | **BAND NOT REPRODUCED** | the rank-21-40 band is not reproduced on the fresh build, so the band is build-dependent | report the build dependence; the acceptance stays unadjudicated; do not substitute a fresh band |
| gates pass; every measured band edge served at 112 on every seed | **BAND IN SERVICE** | the condition is met on every measured fresh-world band edge | record the condition met; the allocation explanation is not refuted at this world family; the owner decides any engine or promotion step; no capability claim |
| gates pass; between 1 and all-but-one measured band edges served at 112 | **BAND PARTLY IN SERVICE** | the condition is not met; the unserved edges are the finding and are named in the ledger | report the per-edge misses; the allocation explanation is refuted for them; the next step is the admission rule, not another level |
| gates pass; none of the measured band edges served at 112 | **BAND NOT IN SERVICE** | the condition is not met on any measured band edge | record the refutation; the next step is the admission rule, not another level |

## Grant and stop

**Authorisation.** Granted 2026-11-11 against this record before any cell. The twelve design cells, the determinism rerun and the result artifact/page are authorised. The arm is not built and no cell has run; building the arm does not open a cell without a passing preflight.

**Grant document.** `docs/AUTHORISATION-PRESENCE-BAND-3.md`

> Preregister a repaired band block with fresh seeds and the fixed harness, with B5 still able to fail, and record its grant before running.

**Cost.** 12 cells (one fresh-process determinism rerun) x 120 cycles.

**Stop condition.** No cell runs until the arm exists and its preflight passes. After that, the block closes when the twelve cells and rerun have produced their parts, B1-B8 have been scored once in the frozen order, and the verdict is recorded. A gate failure is VOID; no cell is rerun to escape a gate and no gate is amended after a result.

## What this record does not license

A preregistration and a grant, not a result. No cell has run. BAND-1 stays VOID and BAND-2 stays unrun; neither is re-read. This record licenses no capability, retention or transfer claim.
