# V2 first cell — A1–A5 gate record (not a result)

**Generated** by `python -m benchmarks.v2_first_cell_gates --write`. Do not edit by hand;
`--check` fails when the page and the record disagree.

**Status:** `GATES NOT CLEARED — A4 NOT PASS; THE CELL IS NOT RUNNABLE`

The gate suite runs before the behavioural cell and writes the record
`benchmarks/v2_first_cell_runner.py` requires. It runs no cell seed: A1 and A5 use the spent smoke
seed `20911101`; A4 is not run because its base world is held for another block. The
ten reserved seeds are untouched.

## Gates

| Gate | Status | What was checked |
|---|---|---|
| A1 | PASS | canonicalisation rule: 5 sample paths, 3 keys, 0 mixed keys, 0 flips changed a key; smoke seed 20911101 (120 cycles, spent dry-run seed, not a cell seed): 1216 detected paths -> 107 keys over 107 distinct node sets, 0 mixed, 0 flip failures; committed regressions 177->158 with multiplicities {1: 139, 2: 19} and 138->125 reproduce; 0 id collisions. Scope: the ten cell seeds are not replayed, so this is the rule and a development stream, not the experiment's own detection stream. |
| A2 | PASS | I1-I5 pass on a temporary store: the id survived a version bump, a member change and a direction flip; ids came from a monotone counter (1, 2, 3, 4) and were not content-derived; retirement preserved 1 member and its id, and the next key got id 4; 5 non-integer or content addresses were rejected; an unknown id and a stale version both raised. |
| A3 | PASS | M1-M5 pass on a temporary store with a bystander: add and remove left the bystander's resolved state byte-identical; a shared atom kept version 1 and its binding; a stale version and a non-member removal were rejected without moving the version; retirement kept 3 members and refused further mutation; the store owns only atoms, composite_ids, composites, members, tombstones and the frozen-graph guard can fire. |
| A4 | NOT RUN | the preregistered base world is held by the A1-TWO-PATH-1 candidate block; rebuilding it here would spend a reserved seed, and no committed detection stream exists to rebuild it without one. The spent smoke world is not the base world, so it is not substituted. A4 is unmeasured and the gate blocks the cell until the base world is released or a committed stream is available. |
| A5 | PASS | two builds from the spent smoke stream's 96 admissions produced identical ids, keys, members and versions; retiring id 96 left a tombstone and the next registration got id 97, so allocation is monotone and retirement never frees an id; the novel key quux|zorp was absent from the stream. Scope: the smoke stream, not the held base world. |

## What this means

A1 passes because the canonicalisation rule is total on sample paths, holds on the smoke
stream, and both committed identity regressions reproduce exactly. It is the rule and a
development stream, not the experiment's own detection stream.

A4 did not pass. The record keeps the failure and its evidence; the runner treats any non-PASS gate as a gate failure.

The cell is **not runnable**: a signed authorisation would write a `VOID` artifact without executing a seed.

## Not evidence

This is an instrument record, not a causal, capability or transfer result. No cell ran, no
reserved seed was spent, and no verdict exists. Clearing the gates does not make the primitive
predictive: the earning test still decides that, and it is still allowed to fail.
