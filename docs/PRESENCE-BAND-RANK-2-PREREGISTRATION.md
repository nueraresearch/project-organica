# PRESENCE-BAND-2 — corrected B5 and a live rank reading

**Status.** FROZEN, NOT RUN. This page is rendered from `docs/presence_band_rank_2_prereg.json`; it is not edited by hand.

| Field | Value |
| --- | --- |
| Preregistration | `PRESENCE-BAND-2` |
| Frozen on | 2026-11-11 |
| Engine | 0.15.0, cap 112, none |
| Cells planned | 12 (2 caps x 6 seeds = 12 cells) |
| Seeds | 20611601, 20611602, 20611603, 20611604, 20611605, 20611606 |
| Caps | 40, 112 |
| Cycles | 120 |
| Named band edges | 62 |
| Runner | not built |
| Cells run | 0 |
| Authorisation | not granted |

## Why a second block

BAND-1 was VOID on B5, not because the band failed but because B5 required an exact 56 transition rows and the rank reader returned character tuples. BAND-2 is a new block, not a re-score: it corrects both defects from the engine source, keeps the same 62 edges and the same Q4 worlds, and makes a pass a confirmation of same-world service rather than a fresh-seed generalisation. BAND-1 remains VOID and its cells are not re-read as this block's evidence.

BAND-1's B5 required the cap-112 transition allocation to be exactly **56**. That was the wrong reading of the engine's allocation: 56 is a guaranteed floor, and unused cooccurrence slots are backfilled with further transitions. Its first rank comparison also read served edges as character tuples, so it resolved no rank. BAND-2 corrects both before any cell and keeps the 62 named edges and the same Q4 worlds.

## The corrected B5

**Previous condition.** BAND-1 required the 112 arm's transition allocation to be exactly 56 and its rank comparison to read a served edge. It was VOID on every seed: the allocation was 64-69 and the rank read was 0.

**Why it was wrong.** The transition allocation is a floor, not an exact count. `organica/sleep_extraction.py` sets `transition_budget = returned_budget // 2`, serves that many transitions, fills the remaining budget with cooccurrences, and then backfills any unused slots with further transitions (`more_trans`). At cap 112 the floor is 56; 64-69 is 56 plus backfill, so the old exact-count condition could not pass on a correctly functioning engine.

**Source.** `organica/sleep_extraction.py:511-525`.

**New condition.** transitions >= 56; max served transition rank > 40; every served edge parsed strictly; every served transition ranked; no window above 112.

BAND-1 remains VOID and is not re-scored. BAND-2 does not use BAND-1's cells as its own result; it repeats the same-world measurement under a corrected gate.

## Fixed rank reading

**Previous defect.** BAND-1's first B5 built character tuples from the served strings, so the rank lookup found no served transition and reported 0.

**Rule.** Each served edge is a string `source>target` in `windows_world`. Split at exactly one `>` and require two non-empty tags. The edge's rank is the minimum recorded rank for that exact tuple in the universe. A served transition with no recorded rank fails B5; it is never defaulted to 0. An unparseable served edge also fails.

**Fixture.** `amber>olive` maps to `('amber', 'olive')` and a recorded rank 41 must yield a maximum served transition rank of 41 with no missing rank; the pre-fix character tuple does not resolve and fails the fixture.

## The 62 named edges

These are Q4's never-served present transitions whose minimum block rank in the ceiling universe was 21–40. The identity block is copied from BAND-1's frozen band; BAND-2 does not re-derive a fresh band.

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

## Design

| Field | Value |
| --- | --- |
| Arms | cap 40 and cap 112 |
| Variable | `SleepService.MAX_PREDICTIONS`, set per cell |
| Observer | the repaired observer of PRESENCE-CONVERSION-2, whose served window is the engine's own and whose ceiling call records the pre-cap universe |
| World | the compositional world family of PHASE_ACQUISITION at 120 cycles, on Q4's six seeds, because the named edges live in those worlds |
| Pairing | each seed contributes one world and one stimulus to both caps; only the cap differs, and each cell's per-edge ledger is paired with the other cap's |
| Reuse | Q4's six seeds are reused deliberately, not redrawn: the named edges exist only in Q4's worlds and BAND-2 is a confirmatory block on the same worlds. This is not a fresh-seed generalisation, and the record says so before any cell. |
| Freshness | No new seed is drawn. The six worlds are Q4's, gated by the frozen world digest; a different world cannot pass as the same band. |
| Cycles | 120 |
| Cells | 12 |

## Gates

| Gate | Rule |
| --- | --- |
| `B1_build` | all twelve cells run the shipped 0.15.0 build at the named cap, with one sha256 across the run and only `MAX_PREDICTIONS` overridden; a mixed or edited build is VOID |
| `B2_world` | each seed's world digest and present fingerprint are identical at 40 and 112 and equal the frozen Q4 digest for that seed; a difference is VOID |
| `B3_band_identity` | at cap 40 every one of the 62 named edges is a present transition whose minimum block rank is 21-40 and which is served in 0 cycles; an edge missing, miss-ranked or served is BAND NOT REPRODUCED and no acceptance is read |
| `B4_control_40` | the 40 arm is the pre-treatment control and must show 0 of 62 band edges served on every seed, with the served transition prefix at 20; a served band edge at 40 means the band is not the band |
| `B5_cap_live` | the 112 arm's transition count is **at least 56** — the engine guarantees `MAX_PREDICTIONS // 2 = 56` and backfills unused cooccurrence slots with further transitions, so **56 is a floor, not an exact count** — its served transition prefix extends past **block rank 40** on every seed, and no window exceeds **112** rows. The rank of a served edge is read by splitting `source>target` at **exactly one** `>` into **two non-empty** tags, then taking the **minimum** recorded rank for that exact edge; a served transition with **no recorded rank** fails the gate rather than contributing 0. A transition count below 56, a maximum served transition rank at or below 40, a window above 112, an unparseable served edge, or a served transition with no recorded rank is VOID. |
| `B6_denominator` | each seed's ledger holds all 62 edges and every stage has a denominator; a missing edge is not imputed and a zero denominator is not measurable, never 0.0 |
| `B7_determinism` | a fresh-process rerun of seed 20611601 at 112 reproduces its per-edge ledger exactly |
| `B8_seed_axis` | the six 112 ledgers are not one repeated row; at least three distinct served counts across the band, so the arm is not measuring a single world |

## Acceptance condition

> The 21–40 transitions must be served at 112 and the block's own gates must pass, per seed, with the seed axis live.

Source: `docs/DECISION-ADMISSION-STEP.md`. The condition is the decision's, unchanged; this block adjudicates whether it holds and does not decide what follows. The decision remains the owner's and stays PENDING until the result is recorded.

## Prediction, stated before any cell

**Prediction.** All 62 named edges are served at 112 on every seed and none at 40; the corrected B5 passes with a transition count of at least 56 and a maximum served transition rank above 40.

**Because.** The 112 transition floor is 56 and the band occupies block ranks 21-40; the engine's backfill can only add transitions. BAND-1's ledger already recorded 62/62 at 112, so this is a confirmatory prediction, not a discovery.

**Prior observation.** BAND-1's run recorded all 62 served at 112 and 0 at 40, but BAND-1 is VOID on B5. BAND-2 treats that only as the prior that motivates a corrected block; it is not BAND-2's result and is not counted as BAND-2 evidence.

**Falsifier.** Any named edge served in 0 cap-112 cycles, any named edge served at cap 40, any transition count below 56, any maximum served transition rank at or below 40, any window above 112, any unparseable served edge, any served transition with no recorded rank, or any gate failure.

A pass is confirmation on the same worlds; it is not a fresh-seed replication and does not license a capability, retention or transfer claim.

## Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| any gate other than B3 fails | **VOID** | the block is unrun or non-reproducible and the failed gate names what did not happen | record VOID; fix the failed gate and register a new block; read no acceptance |
| B3 fails: a named edge is missing, not ranked 21-40, or served at cap 40 | **BAND NOT REPRODUCED** | the named edges are not the 21-40 band on the shipped build, so the band is build-dependent | report the build dependence; the acceptance stays unadjudicated and the decision PENDING; do not substitute a fresh band |
| gates pass; all 62 named edges served at 112 on every seed | **BAND IN SERVICE** | the condition is met on the named edges with the corrected floor and a live rank comparison | record the condition met; the allocation explanation is not refuted at this world family; BAND-1 remains VOID and is not re-scored; no capability claim |
| gates pass; between 1 and 61 named edges served at 112 | **BAND PARTLY IN SERVICE** | the condition is not met; the unserved edges are the finding and are named in the ledger | report the per-edge misses; the allocation explanation is refuted for them; the next step is the admission rule, not another level |
| gates pass; none of the 62 named edges served at 112 | **BAND NOT IN SERVICE** | the condition is not met on any named edge | record the refutation; the next step is the admission rule, not another level |

## No cell has run

**Authorisation.** No dated grant exists. A grant naming the twelve cells, the determinism rerun and the result artifact must be recorded against this record before an arm is built or a cell is opened. This preregistration authorises nothing to run.

**Cost.** 12 cells (one fresh-process determinism rerun) x 120 cycles.

**Stop condition.** No cell runs until a dated grant is recorded. After the grant, the block closes when the twelve cells and the rerun have produced their parts, B1-B8 have been scored once in the frozen order, and the verdict is recorded. Any gate failure is VOID; no cell is rerun to escape a gate and no gate is amended after a result.

## What this record does not license

A preregistration, not a result. No cell has run. BAND-1 remains VOID and its cells are not re-read; Q2's CAP LIMITING and Q4's CONVERSION STAGE MEASURED are not re-scored. This record licenses no capability, retention or transfer claim.
