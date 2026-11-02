# Provenance diagnostic — five already-used calibration seeds

**Generated from [`docs/provenance_diagnostic.json`](provenance_diagnostic.json);
do not edit by hand.** Regenerate with
`PYTHONHASHSEED=0 python -m benchmarks.provenance_trace --report`.

Plan: [`docs/PROVENANCE-ANALYSIS-PLAN.md`](PROVENANCE-ANALYSIS-PLAN.md), frozen at commit
`c5b4d49e8075b7076d54c24cea436fa32c16b882` before this run. Seeds:
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
