# V2 first cell — A1–A5 gate record (not a result)

**Generated** by `python -m benchmarks.v2_first_cell_gates --write`. Do not edit by hand;
`--check` fails when the page and the record disagree.

**Status:** `A1 PASS; A2-A5 NOT RUN — THE PRIMITIVE IS NOT BUILT, SO THE CELL IS NOT RUNNABLE`

The gate suite runs before the behavioural cell and writes the record
`benchmarks/v2_first_cell_runner.py` requires. It runs no cell seed: A1 uses the spent smoke
seed `20911101` as a development stream, and the ten reserved seeds are untouched.

## Gates

| Gate | Status | What was checked |
|---|---|---|
| A1 | PASS | canonicalisation rule: 5 sample paths, 3 keys, 0 mixed keys, 0 flips changed a key; smoke seed 20911101 (120 cycles, spent dry-run seed, not a cell seed): 1216 detected paths -> 107 keys over 107 distinct node sets, 0 mixed, 0 flip failures; committed regressions 177->158 with multiplicities {1: 139, 2: 19} and 138->125 reproduce; 0 id collisions. Scope: the ten cell seeds are not replayed, so this is the rule and a development stream, not the experiment's own detection stream. |
| A2 | NOT RUN | no stored composite id exists: the readout keys membership by the canonical tag set, and there is no composite_ids table, register(), id/version API or tombstone. I1-I5 are unimplemented, so this gate is not run. |
| A3 | NOT RUN | no mutation API (add_member, remove_member, retire) and no stored rows; the readout recomputes members in memory, so there is no bystander row set to assert byte-identical. M1-M5 are unimplemented, so this gate is not run. |
| A4 | NOT RUN | no rebuilt primitive store to page-count. v2_primitive_sizing is a static estimate of 135168 bytes at m>=2 on the measured graph, not the required page-count of the built primitive and not a before/after resolution comparison. |
| A5 | NOT RUN | no ids, versions or retirements exist to replay. The readout's key and member computation is deterministic in --check, but that is the harness, not the primitive's allocation order. |

## What this means

A1 passes because the canonicalisation rule is total on sample paths, holds on the smoke
stream, and both committed identity regressions reproduce exactly. It is the rule and a
development stream, not the experiment's own detection stream.

A2, A3, A4 and A5 are **not run**, not passed. The mutable-identity primitive those gates
test does not exist in this repository: there is no stored composite id, no mutation API,
no rebuilt store, and no id/version/tombstone sequence. A sizing estimate is not a page
count, and a deterministic readout is not a deterministic allocation order. Marking any of
them PASS would claim a check that was never made.

Because the runner treats `NOT RUN` as a gate failure, the cell is **not runnable**: if the
authorisation were signed now, `--run` would write a `VOID` artifact without executing a
seed. The missing input is the primitive the charter specified but did not authorise.

## Not evidence

This is an instrument record, not a causal, capability or transfer result. No cell ran, no
reserved seed was spent, and no verdict exists.
