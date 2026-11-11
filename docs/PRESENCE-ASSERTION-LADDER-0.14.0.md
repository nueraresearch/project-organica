# Presence to assertion: where the missing world edges are lost

Generated from `docs/presence_assertion_ladder_0.14.0.json` by `python -m benchmarks.presence_assertion_ladder --run`. Do not edit by hand.

**Status: EXPLORATORY trace. Behaviour-neutral recording, proven against the published audit.**

The engine is unchanged. The shipped arm's presence count, asserted count and asserted fingerprint were required to equal `docs/presence_assertion_audit_0.14.0.json` on every seed, and did: **0 mismatches**.

## The question

Of the world edges that are present in raw temporal memory but absent from the final asserted structure, at which Layer-1 stage is each one lost: never offered, offered but not admitted to the 40-row window, or admitted but not asserted?

## The four readings

| Stage | Basis | What it means |
| --- | --- | --- |
| present | `mem.temporal_edges(min_count=1)` | the audit's presence basis |
| offered | returned prediction window, cap raised (diagnostic arm) | the ranked list with the cap removed (counterfactual) |
| admitted | returned prediction window, shipped cap 40 | the window the shipped engine returns |
| asserted | structure_edges over the surviving candidate snapshots, all six types | the published audit's assertion basis |

## Per seed

| Seed | Present | Asserted | Missed | Offered | Admitted | Not offered | Offered, not admitted | Admitted, not asserted | Leading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20261100 | 112 | 40 | 72 | 112 | 84 | 0 | 25 | 47 | admitted_not_asserted |
| 20261101 | 112 | 44 | 68 | 112 | 73 | 0 | 33 | 35 | admitted_not_asserted |
| 20261102 | 112 | 38 | 74 | 112 | 82 | 0 | 23 | 51 | admitted_not_asserted |
| 20261103 | 112 | 46 | 66 | 112 | 78 | 0 | 26 | 40 | admitted_not_asserted |
| 20261104 | 112 | 34 | 78 | 112 | 68 | 0 | 36 | 42 | admitted_not_asserted |
| 20261105 | 112 | 47 | 65 | 112 | 75 | 0 | 28 | 37 | admitted_not_asserted |

## How often an edge got a slot

| Set | Edges | Bypass | Never admitted (non-bypass) | Median admissions | Min-max |
| --- | --- | --- | --- | --- | --- |
| asserted | 249 | 41 | 0 | 3.0-13.5 | 0-93 |
| admitted_not_asserted | 252 | 0 | 0 | 5-9 | 1-54 |
| offered_not_admitted | 171 | 0 | 171 | 0-0 | 0-0 |

**Bypass is not a miss.** The 41 never-admitted edges in the asserted set are the bypass: they are asserted through a non-prediction structure type without ever entering a prediction window. They are not part of the 423 present-but-unasserted misses; the 171 offered-but-not-admitted edges are the misses in that table.

## Pooled over the six seeds

| Stage the edge failed | Edges | Share of misses |
| --- | --- | --- |
| not_offered | 0 | 0.0000 |
| offered_not_admitted | 171 | 0.4043 |
| admitted_not_asserted | 252 | 0.5957 |

**Verdict: `MIXED`**

The largest bucket is `admitted_not_asserted` with 252 of 423 misses (0.5957), leading on 6 of 6 seeds; the declared rule requires a 0.60 pooled share and a majority of seeds, so the label is `MIXED` and the bar is not moved. The split is reported per seed above, and the admission counts below show how close the two fates are.

## What the window was doing

| Reading | Range across seeds |
| --- | --- |
| shipped window size (median per seed) | 40, 40, 40.0, 40.0, 40.0, 40.0 |
| cycles whose window reached the cap of 40 | 72-112 of 120 |
| world edges as a share of admitted rows | 0.2393-0.2782 |
| candidates per cycle with the cap removed (median) | 225-238 |
| asserted world edges that no window ever admitted | 3-9 |
| admitted world edges the counterfactual arm never offered | 0-0 |

## What this does not claim

One engine build, one world family, two designs' acquisition phase, six seeds. The 'offered' arm is a counterfactual: raising the cap changes the run, so an edge counted as offered is one the ranking would have produced with the budget removed, not one the shipped engine saw. Nothing here licenses an engine change; the label is descriptive and no criterion is scored.

**Resolution.** edge: each world edge is classified individually; the trace cannot attribute assertion that arrives from a non-prediction structure type, which is why the admitted->asserted step is measured as a set difference and not as a lineage.
