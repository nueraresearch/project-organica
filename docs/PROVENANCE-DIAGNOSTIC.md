# Provenance diagnostic — five already-used calibration seeds

**Generated from [`docs/provenance_diagnostic.json`](provenance_diagnostic.json);
do not edit by hand.** Regenerate with
`PYTHONHASHSEED=0 python -m benchmarks.provenance_trace --report`.

Plan: [`docs/PROVENANCE-ANALYSIS-PLAN.md`](PROVENANCE-ANALYSIS-PLAN.md), frozen at commit
`7d8f34d4b5280009a55609b9af7d631bf25ffaa8` before this run. Seeds:
20261201, 20261202, 20261203, 20261204, 20261205 (calibration only), cap
`1000`, variant `V1.1-cap(1000)`.

## What this is, and what it is not

A descriptive diagnostic of the instrument and of the lineage the engine
records. **There is no threshold, no pass mark and no verdict in this
document.** `world_rooted` means vocabulary overlap across a complete
ancestor chain; it is not observation-level provenance, and nothing here
validates transfer or reopens the closed study.

The tracer's 11 controls passed before the run
(`all_passed: true`).

## Statuses, by limb

| status | formation | revision |
|---|---|---|
| `world_rooted` | 14 | 13 |
| `mixed` | 0 | 0 |
| `self_only` | 0 | 0 |
| `world_rooted_incomplete` | 49 | 44 |
| `mixed_incomplete` | 0 | 0 |
| `self_only_incomplete` | 0 | 0 |
| `unresolved_missing_records` | 0 | 0 |
| `unresolved_cycle` | 0 | 0 |
| `unresolved_depth_truncated` | 0 | 0 |
| `unresolved_nothing_resolved` | 0 | 0 |
| `unresolved_no_ancestry` | 1581 | 1596 |

The three families are counted separately and are never summed: a lineage
with a resolvable branch and a missing, cyclic or truncated one is not a
rooted lineage with a note attached.

| family | limb | claims | with asserted edge | complete `world_rooted` | incomplete | unresolved |
|---|---|---|---|---|---|---|
| formation | 1644 | 1644 | 14 | 49 | 1581 |
| revision | 1653 | 1653 | 13 | 44 | 1596 |

### Why a lineage is incomplete

| defect | formation | revision |
|---|---|---|
| `missing_records` | 23 | 9 |
| `cycle` | 39 | 41 |
| `depth_truncated` | 0 | 0 |

## Counting units

The same lineage question at three resolutions. A survivor is re-stored every
sleep cycle, so the study's per-claim rule counts **raw snapshot rows**, while
the tracer walks **unique structure ids**; a pair of tags may also be asserted
by more than one structure, which is a third unit. None of the three may stand
in for another.

| unit | formation | revision |
|---|---|---|
| raw stored claim rows with an asserted edge (the study's `_claim_edges` count) | 3942 | 3640 |
| raw stored claim rows (all claim-typed rows) | 3942 | 3640 |
| unique structure ids | 1644 | 1653 |
| unique structure ids with an asserted edge | 1644 | 1653 |
| unique asserted edges | 1623 | 1638 |
| unique asserted edges with a complete `world_rooted` claim | 14 | 13 |

| seed | rows per structure (median / max) | structures per asserted edge (median / max) |
|---|---|---|
| 20261201 | 4 / 4 | 1.0 / 2 |
| 20261202 | 2.0 / 2 | 1 / 2 |
| 20261203 | 2 / 2 | 1 / 2 |
| 20261204 | 2 / 2 | 1 / 2 |
| 20261205 | 2 / 2 | 1.0 / 2 |

## Parent links in the raw snapshots

Deduplication keeps the highest-generation snapshot of a structure, so a
statement that a structure has no parents describes that snapshot only. These
counts ask both questions separately: whether **any** raw snapshot of an id
carried parent links, and whether the **latest** one does. A structure that
lost its links is not a structure that never had any.

| type | limb | raw rows | raw rows with parents | unique ids | ids ever with parents | ids with parents in the latest snapshot | ids whose parents appear only in earlier snapshots |
|---|---|---|---|---|---|---|---|
| `hypothesis` | formation | 150 | 150 | 63 | 63 | 63 | 0 |
| `prediction` | formation | 3792 | 0 | 1581 | 0 | 0 | 0 |
| `hypothesis` | revision | 125 | 125 | 57 | 57 | 57 | 0 |
| `prediction` | revision | 3515 | 0 | 1596 | 0 | 0 | 0 |

## By claim type

| type | limb | claims | complete `world_rooted` | incomplete | unresolved |
|---|---|---|---|---|---|
| `hypothesis` | formation | 63 | 14 | 49 | 0 |
| `prediction_candidate` | formation | 1581 | 0 | 0 | 1581 |
| `hypothesis` | revision | 57 | 13 | 44 | 0 |
| `prediction_candidate` | revision | 1596 | 0 | 0 | 1596 |

## By lineage depth (ancestors resolved)

| depth | limb | claims | complete `world_rooted` | incomplete | unresolved |
|---|---|---|---|---|---|
| 0 | formation | 1581 | 0 | 0 | 1581 |
| 7+ | formation | 63 | 14 | 49 | 0 |
| 0 | revision | 1596 | 0 | 0 | 1596 |
| 7+ | revision | 57 | 13 | 44 | 0 |

## Per seed

| seed | limb | claims | complete `world_rooted` | incomplete | unresolved |
|---|---|---|---|---|---|
| 20261201 | formation | 329 | 3 | 11 | 315 |
| 20261201 | revision | 328 | 3 | 9 | 316 |
| 20261202 | formation | 340 | 1 | 12 | 327 |
| 20261202 | revision | 342 | 3 | 10 | 329 |
| 20261203 | formation | 329 | 5 | 7 | 317 |
| 20261203 | revision | 334 | 2 | 9 | 323 |
| 20261204 | formation | 311 | 2 | 9 | 300 |
| 20261204 | revision | 316 | 2 | 8 | 306 |
| 20261205 | formation | 335 | 3 | 10 | 322 |
| 20261205 | revision | 333 | 3 | 8 | 322 |

## What each outcome means, agreed in advance

As fixed in the plan before the run: a mostly unresolved result points to
missing lineage in the recorded structures, and the next instrument would
need a store-time record of the content's origin. A mostly vocabulary-overlap
result says useful chains exist, which is consistent with world inheritance
*and* with self-generated content that reuses world words, so it does not
establish that the links track world evidence. Either way, the next
confirmatory study needs its own preregistration and fresh seeds; the closed
study's failure stays intact.
