# PRESENCE-BAND-1 — the 21–40 transitions at 40 versus 112

**Status.** FROZEN, RUN. This page is rendered from `docs/presence_band_rank_prereg.json`; it is not edited by hand.

| Field | Value |
| --- | --- |
| Preregistration | `PRESENCE-BAND-1` |
| Frozen on | 2026-11-11 |
| Engine | 0.15.0, cap 112, none |
| Question | On the shipped 0.15.0 build, does raising the Layer-1 cap from 40 to 112 put each of the 62 named Q4 rank-21-40 transition edges into service, per seed, with the block's own gates passing? |
| Cells planned | 12 (2 caps x 6 seeds = 12 cells) |
| Seeds | 20611601, 20611602, 20611603, 20611604, 20611605, 20611606 |
| Caps | 40, 112 |
| Cycles | 120 |
| Named band edges | 62 |
| Runner | built |
| Cells run | 13 |
| Authorisation | granted |

## The 62 named edges

These are Q4's never-served present transitions whose minimum block rank in the ceiling universe was 21–40. They are frozen here by identity, so the arm reads service on the named edges rather than on a rank band recomputed at run time.

| Seed | Edge | Q4 best rank |
| ---: | --- | ---: |
| 20611601 | `amber>olive` | 35 |
| 20611601 | `birch>cedar` | 23 |
| 20611601 | `fern>willow` | 34 |
| 20611601 | `indigo>cedar` | 24 |
| 20611601 | `maple>indigo` | 32 |
| 20611601 | `ochre>willow` | 22 |
| 20611601 | `olive>cedar` | 28 |
| 20611601 | `olive>umber` | 31 |
| 20611601 | `olive>willow` | 39 |
| 20611601 | `slate>birch` | 28 |
| 20611601 | `slate>indigo` | 32 |
| 20611601 | `umber>verdant` | 40 |
| 20611602 | `amber>yarrow` | 22 |
| 20611602 | `cedar>crimson` | 23 |
| 20611602 | `indigo>verdant` | 27 |
| 20611602 | `indigo>yarrow` | 25 |
| 20611602 | `olive>yarrow` | 38 |
| 20611602 | `sable>amber` | 32 |
| 20611602 | `sable>indigo` | 25 |
| 20611602 | `sable>slate` | 26 |
| 20611602 | `yarrow>olive` | 35 |
| 20611603 | `amber>olive` | 21 |
| 20611603 | `cedar>amber` | 28 |
| 20611603 | `cedar>ochre` | 25 |
| 20611603 | `cedar>teal` | 21 |
| 20611603 | `ochre>willow` | 39 |
| 20611603 | `olive>amber` | 26 |
| 20611603 | `olive>fern` | 32 |
| 20611603 | `sable>olive` | 22 |
| 20611603 | `slate>birch` | 32 |
| 20611603 | `slate>umber` | 27 |
| 20611603 | `slate>willow` | 30 |
| 20611603 | `slate>yarrow` | 26 |
| 20611603 | `umber>teal` | 28 |
| 20611603 | `willow>fern` | 36 |
| 20611603 | `willow>indigo` | 39 |
| 20611603 | `willow>sable` | 37 |
| 20611604 | `amber>maple` | 35 |
| 20611604 | `birch>verdant` | 25 |
| 20611604 | `birch>yarrow` | 26 |
| 20611604 | `indigo>verdant` | 39 |
| 20611604 | `teal>umber` | 23 |
| 20611604 | `teal>willow` | 22 |
| 20611604 | `willow>crimson` | 33 |
| 20611604 | `willow>ochre` | 32 |
| 20611604 | `willow>teal` | 29 |
| 20611605 | `amber>birch` | 22 |
| 20611605 | `amber>slate` | 33 |
| 20611605 | `amber>verdant` | 35 |
| 20611605 | `amber>willow` | 40 |
| 20611605 | `cedar>fern` | 27 |
| 20611605 | `ochre>birch` | 35 |
| 20611605 | `ochre>cedar` | 36 |
| 20611605 | `ochre>teal` | 37 |
| 20611605 | `olive>yarrow` | 23 |
| 20611605 | `sable>birch` | 31 |
| 20611605 | `slate>amber` | 38 |
| 20611605 | `slate>crimson` | 24 |
| 20611605 | `slate>ochre` | 22 |
| 20611605 | `yarrow>indigo` | 26 |
| 20611606 | `crimson>teal` | 27 |
| 20611606 | `umber>maple` | 31 |

| Seed | World digest | Present | Named edges |
| ---: | --- | ---: | ---: |
| 20611601 | `a7532369b92daeb9` | 112 | 12 |
| 20611602 | `a904c0382ebf3db9` | 112 | 9 |
| 20611603 | `41b98d54cb1dc579` | 112 | 16 |
| 20611604 | `f9ed4793f27a7fd2` | 112 | 9 |
| 20611605 | `6faa0ac07fb2d0c3` | 112 | 14 |
| 20611606 | `d0b6d246e273cb63` | 112 | 2 |

**Derivation.** For each of Q4's six seeds, the union of present world edges that are transition candidates, were never served in any of Q4's 120 cycles, and whose minimum block rank in the ceiling universe is 21-40. The per-seed counts are 12, 9, 16, 9, 14 and 2, summing to 62, and they reproduce Q4's 21-40 column exactly. A block rank is a position in the ceiling list with every transition before every cooccurrence, so a transition's rank is its position in the transition prefix.

**Source.** `docs/presence_conversion_repair_run.json`, with the per-cycle candidate ledger from `.scratch/presence_repair/parts/`; both are Q4's, frozen before this record.

## What this block is, and is not

Q2 returned `CAP LIMITING` but could not identify the 21-40 band: its seeds were fresh and its cells recorded counts, not per-edge ranks. This block is the instrument that can. It supplies the designation the admission decision asked for at the level of the named edges, and it re-scores no verdict: Q2's CAP LIMITING stands, Q4's CONVERSION STAGE MEASURED stands, and neither is re-read.

## Design

| Field | Value |
| --- | --- |
| Arms | cap 40 and cap 112 |
| Variable | `SleepService.MAX_PREDICTIONS`, set per cell |
| Observer | the repaired observer of PRESENCE-CONVERSION-2, whose served window is the engine's own and whose ceiling call records the pre-cap universe |
| World | the compositional world family of PHASE_ACQUISITION at 120 cycles, on Q4's six seeds, because the named edges live in those worlds |
| Pairing | each seed contributes one world and one stimulus to both caps; only the cap differs, and each cell's per-edge ledger is paired with the other cap's |
| Reuse | Q4's six seeds are reused deliberately, not redrawn: the named edges exist only in Q4's worlds. The reuse is declared against the Q4 artifact and gated by the frozen world digest, so a different world cannot pass as the same band. |
| Cycles | 120 |
| Cells | 12 |

**Treatment.** `SleepService.MAX_PREDICTIONS` is set to 40 or 112 on the instance; the treatment defines `__init__` and nothing else, and the repaired observer's served window is the engine's own list returned untouched, with a second call at the diagnostic ceiling used only to record the pre-cap universe.

## Endpoints

| Stage | Definition | Role |
| --- | --- | --- |
| W | world edges generated for the seed | denominator |
| P | world edges present in the temporal graph | the band's universe |
| band | the 62 frozen edges, with their Q4 best rank | the named treatment group |
| S40 | band edges served in at least one cap-40 cycle | pre-treatment control |
| S112 | band edges served in at least one cap-112 cycle | primary endpoint |
| A112 | band edges asserted at the end of the cap-112 run | secondary, reported not adjudicated |
| ledger | per edge: best block rank at each cap, cycles served at each cap, first served cycle at 112, asserted at 112, relation | the per-edge record the decision needed |

## Gates

| Gate | Rule |
| --- | --- |
| `B1_build` | all twelve cells run the shipped 0.15.0 build at the named cap, with one sha256 across the run and only `MAX_PREDICTIONS` overridden; a mixed or edited build is VOID |
| `B2_world` | each seed's world digest and present fingerprint are identical at 40 and 112 and equal the frozen Q4 digest for that seed; a difference is VOID |
| `B3_band_identity` | at cap 40 every one of the 62 named edges is a present transition whose minimum block rank is 21-40 and which is served in 0 cycles; an edge missing, miss-ranked or served is BAND NOT REPRODUCED and no acceptance is read |
| `B4_control_40` | the 40 arm is the pre-treatment control and must show 0 of 62 band edges served on every seed, with the served transition prefix at 20; a served band edge at 40 means the band is not the band |
| `B5_cap_live` | the 112 arm's transition allocation is 56 and its served transition prefix extends past block rank 40 on every seed; 40 never returns more than 40 rows and 112 never more than 112; a cap that does not move the window is VOID |
| `B6_denominator` | each seed's ledger holds all 62 edges and every stage has a denominator; a missing edge is not imputed and a zero denominator is not measurable, never 0.0 |
| `B7_determinism` | a fresh-process rerun of seed 20611601 at 112 reproduces its per-edge ledger exactly |
| `B8_seed_axis` | the six 112 ledgers are not one repeated row; at least three distinct served counts across the band, so the arm is not measuring a single world |

## Acceptance condition

> The 21–40 transitions must be served at 112 and the block's own gates must pass, per seed, with the seed axis live.

Source: `docs/DECISION-ADMISSION-STEP.md`. The condition is the decision's, unchanged; this block adjudicates whether it holds and does not decide what follows. The decision remains the owner's and stays PENDING until the result is recorded.

## Prediction, stated before any cell

**Prediction.** All 62 named edges are served at 112 on every seed, and 0 of 62 are served at 40.

**Because.** At cap 112 the transition allocation is 56 slots and the band occupies block ranks 21-40, so the arithmetic puts every named edge inside the served transition prefix unless the ordering, the split or the world differs.

**Falsifier.** Any named edge served in 0 cap-112 cycles, any named edge served at cap 40, or any seed whose world digest or band rank differs from the frozen record.

The mechanism predicts the pass, so a pass is confirmation, not discovery. What the arm adds is that the prediction is per edge, that the 40 arm is measured rather than assumed, and that a failure names exactly which edge and which gate.

## Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| any gate other than B3 fails | **VOID** | the block is unrun or non-reproducible and the failed gate names what did not happen | record VOID; fix the harness and register a new block; read no acceptance |
| B3 fails: a named edge is missing, not ranked 21-40, or served at cap 40 | **BAND NOT REPRODUCED** | the named edges are not the 21-40 band on the shipped build, so the band is build-dependent and this block cannot read the condition | report the build dependence; the acceptance stays unadjudicated and the decision PENDING; do not re-read Q2 and do not substitute a fresh band |
| gates pass; all 62 named edges served at 112 on every seed | **BAND IN SERVICE** | the condition is met on the named edges: the transitions ranked 21-40 at cap 40 enter service when the cap is 112, per seed | record the condition met; the allocation explanation is not refuted at this world family; the owner decides any engine or promotion step; no capability claim |
| gates pass; between 1 and 61 named edges served at 112 | **BAND PARTLY IN SERVICE** | the condition is not met; the unserved edges are the finding and are named in the ledger | report the per-edge misses; the allocation explanation is refuted for them; the next step is the admission rule, not another level |
| gates pass; none of the 62 named edges served at 112 | **BAND NOT IN SERVICE** | the condition is not met on any named edge | record the refutation; the next step is the admission rule, not another level |

## Result

**VOID** -- `docs/presence_band_rank_run.json`, 2026-11-11.

B5_cap_live failed on every seed: the cap-112 transition allocation is 69, 67, 68, 68, 68 and 64, not the frozen 56, and the rank comparison read no served edge's block rank. The band itself was served in full at 112 (62 of 62) and in 0 cycles at 40; B1-B4 and B6-B8 passed. Because a gate failed, no acceptance is adjudicated. The harness defect behind the rank reading (`_served` built character tuples from the served strings) and a `dict & set` crash in the B4 control were found after the cells ran and fixed before this record was closed; no cell was rerun and no gate was rescored.


## Authorisation and stop

**Authorisation.** Granted 2026-11-11 against this record. The quoted instruction authorises the twelve cells, the determinism rerun and the result artifact; it does not authorise an engine edit, a cap change, a gate change or a re-score.

**Cost.** 12 cells (one fresh-process determinism rerun) x 120 cycles. twelve cells plus one rerun at 120 cycles each

**Stop condition.** The block closes when the twelve cells and the rerun have produced their parts, B1-B8 have been scored once in the frozen order, and the verdict is recorded. A defect is fixed and disclosed; no feature is added afterwards.

## What this record does not license

The block ran under its dated grant on 2026-11-11. It reads whether the 62 named edges enter service; it is not a capability, retention or transfer claim, and it does not re-score Q2 or Q4.


## Amendments

- **2026-11-11 — `grant-recorded`.** A dated grant names the twelve cells and the rerun; at the moment of the grant the record was FROZEN, NOT RUN with zero cells run.
- **2026-11-11 — `harness-fixed`.** The first --finish crashed in the B4 control (`dict & set`) before any gate was scored. The comparison was fixed, and a second defect in `_served` was fixed: it built character tuples from the served strings, so B5 could not resolve a served edge's rank. No cell was rerun and no gate was rescored; the verdict is VOID.
- **2026-11-11 — `run-completed`.** Twelve cells plus the determinism rerun executed on 0.15.0 at cap 112 under the grant. B5 failed on the frozen 56-transition and rank conditions; seven of eight gates pass and the verdict is VOID. No gate, band, seed, cap or endpoint changed.
- **2026-11-11 — `budget-reconciled`.** The 112 cap's 56-transition allocation is the engine's guaranteed floor, not an exact count. `_build_predictions` sets `transition_budget = returned_budget // 2`, then backfills unused cooccurrence slots with `more_trans`; the 64-69 observed in this block is that backfill, so B5's exact-56 condition was a gate defect rather than a failure of the allocation. BAND-2 freezes the corrected `>= 56` condition. This amendment does not alter BAND-1's gates, result or VOID verdict; no cell re-ran and no gate was rescored.