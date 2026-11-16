# V2 first cell — A1–A5 gate record (not a result)

**Generated** by `python -m benchmarks.v2_first_cell_gates --write`. Do not edit by hand;
`--check` fails when the page and the record disagree.

**Status:** `A1-A5 PASS — THE PRIMITIVE IS BUILT; THE CELL IS NOT RUN`

The gate suite runs before the behavioural cell and writes the record
`benchmarks/v2_first_cell_runner.py` requires. It runs no cell seed: A1 and A5 use the spent smoke
seed `20911101`; A4 rebuilds the reallocated base world `20740101` for a
storage measurement only. The ten reserved cell seeds are untouched.

## Gates

| Gate | Status | What was checked |
|---|---|---|
| A1 | PASS | canonicalisation rule: 5 sample paths, 3 keys, 0 mixed keys, 0 flips changed a key; smoke seed 20911101 (120 cycles, spent dry-run seed, not a cell seed): 1216 detected paths -> 107 keys over 107 distinct node sets, 0 mixed, 0 flip failures; committed regressions 177->158 with multiplicities {1: 139, 2: 19} and 138->125 reproduce; 0 id collisions. Scope: this gate does not replay the ten cell seeds; the runner replays each cell seed and applies this canonicalisation check to the experiment's own detection stream before any arm. |
| A2 | PASS | I1-I5 pass on a temporary store: the id survived a version bump, a member change and a direction flip; ids came from a monotone counter (1, 2, 3, 4) and were not content-derived; retirement preserved 1 member and its id, and the next key got id 4; 5 non-integer or content addresses were rejected; an unknown id and a stale version both raised. |
| A3 | PASS | M1-M5 pass on a temporary store with a bystander: add and remove left the bystander's resolved state byte-identical; a shared atom kept version 1 and its binding; a stale version and a non-member removal were rejected without moving the version; retirement kept 3 members and refused further mutation; the store owns only atoms, composite_ids, composites, members, tombstones and the frozen-graph guard can fire. |
| A4 | PASS | reallocated base seed 20740101, 120 cycles: 115 of 158 keys admitted at m=2, 275 observed member references (the sizing model assumed 3 per composite, 345); the rebuilt store is 16 pages / 65536 bytes, at or below the 135168-byte budget; compaction reclaimed 0 atoms and left all 115 resolutions identical; tables atoms, composite_ids, composites, members, tombstones carry no history table. |
| A5 | PASS | two builds from the spent smoke stream's 96 admissions produced identical ids, keys, members and versions; retiring id 96 left a tombstone and the next registration got id 97, so allocation is monotone and retirement never frees an id; the novel key quux|zorp was absent from the stream. Scope: the smoke stream, not the held base world. |

## What this means

A1 passes because the canonicalisation rule is total on sample paths, holds on the smoke
stream, and both committed identity regressions reproduce exactly. This gate is the rule and a
development stream; at run time the runner replays each cell seed and applies the same check to
the experiment's own detection stream before any arm.

A2-A5 pass on the level-1 primitive built under [`DECISION-V2-PRIMITIVE-BUILD`](DECISION-V2-PRIMITIVE-BUILD.md): the identifier and mutation invariants hold on a temporary store, A4's page-count is the rebuilt base world's, and A5 rebuilt it twice with the same allocation order. The page count is a measurement of this build, not the sizing estimate.

The gate block is cleared. The runner can execute the cell as soon as `DECISION-V2-FIRST-CELL` is signed; while it is `PENDING` the runner still refuses. Clearing the gates does not authorise the cell.

## Not evidence

This is an instrument record, not a causal, capability or transfer result. No cell ran, no
reserved seed was spent, and no verdict exists. Clearing the gates does not make the primitive
predictive: the earning test still decides that, and it is still allowed to fail.
