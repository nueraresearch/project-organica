# `DECISION-V2-RUNTIME-FAILURE` — a started-but-unfinished run is VOID or unrun, and is never retried

**Status:** `ADOPTED 2026-11-16 — A STARTED-BUT-UNFINISHED RUN IS VOID OR UNRUN AND IS NEVER RETRIED`

**Decision ID:** `DECISION-V2-RUNTIME-FAILURE` · **Date:** 2026-11-16

**Instruction:** draft and adopt the runtime-failure policy before the first V2 cell can run
(owner, 2026-11-16).

**Narrows:** the runtime half of [`DECISION-V2-FIRST-CELL-INTERPRETATION`](DECISION-V2-FIRST-CELL-INTERPRETATION.md),
which fixes VOID as no effect estimate and requires a fresh pre-registration, a fresh seed block
and a new dated grant for a further attempt. It changes no endpoint, gate, beta, seed, scorer,
engine file or result.

## 1. The decision

- A run is started when `docs/v2_first_cell_run.json` exists; an attempt with a `STARTED` marker, a missing result, or an incomplete artifact set is VOID, while a run with no marker or artifact is UNRUN.
- A VOID run reports no interval, no effect estimate and no scientific reading, and it is not a negative result.
- A started-but-unfinished run is never retried: no resume, deletion, replacement or second execution is permitted, and the one-shot guard refuses every later --run.
- A completed attempt is audit-only; a further attempt needs a new pre-registration, a fresh seed block and a new dated grant, not a retry of this cell.

The marker is written before the first world is replayed. That ordering is the evidence the policy
rests on: a process that dies after the marker has already started an attempt, even if no seed was
reached. A process that dies before the marker leaves no attempt and is `UNRUN`, not a failed try.
The conservative classification is deliberate; it cannot turn an interrupted execution into a
fresh first attempt.

## 2. Classification is observable, not inferred after the fact

`benchmarks/v2_first_cell_runner.py --status` reads the marker, result, manifest and raw-log paths
and returns exactly one of these states. It writes nothing and executes no world.

| Marker | Artifacts | Status | Retry |
|---|---|---|---|
| absent | none of result, manifest or raw log | `UNRUN` | not applicable; no attempt started |
| absent | any artifact | `VOID` — incomplete artifact set | refused |
| `STARTED` | any | `VOID` — started, not completed | refused |
| unreadable, not an object, or unknown status | any | `VOID` — unreadable marker | refused |
| `COMPLETED` | result, manifest and raw log all present | `COMPLETED` — audit only | refused |
| `COMPLETED` | any of result, manifest or raw log missing | `VOID` — finished marker without the complete artifact set | refused |

A `VOID` is not an unrun experiment. It is the cell's one attempt, classified honestly, and it
carries the same prohibition on a second execution as a completed attempt. The distinction matters
when the record is read later: `UNRUN` says no seed was reached; `VOID` says the attempt was
started and cannot be presented as evidence either way. The presence of a partial result file does
not make an interrupted attempt complete: the status classifier is authoritative, and a result left
by a `VOID` attempt is an artifact, not a result.

The existing guard is unchanged in substance and now states the policy: any run marker, manifest,
raw log or result at either the canonical or the custom paths refuses `--run`. A crash cannot evade
it by using a different output path, and recovery is not a supported operation. `--status` is
read-only, so it can report the disposition without weakening the guard.

## 3. Why the alternatives are refused

| Alternative | Why not |
|---|---|
| Delete the marker and retry the block | Deleting the marker to run again is a second execution and would make the stop condition depend on inspecting the outcome. |
| Resume from the partial raw log | Resuming from a partial raw log would start a new run with state the protocol never fixed, and the interval would not be the pre-registered one. |
| Report the crash as a null result | Reporting a crash as a null or negative result converts an instrument failure into evidence, which the adopted reading forbids. |
| Treat every missing result as unrun | Calling an interrupted attempt unrun erases the marker that proves the one-shot attempt began. |

The first two alternatives are operationally tempting because they preserve the spent seed block.
That is exactly why they are refused: the block is spent once, and an interruption is a disposition
of that attempt, not a licence to spend it again.

## 4. Pre-commitment and scope

This record was adopted **before** `--run` was invoked and before any cell seed was executed. The
policy is fixed before the outcome is known and cannot be amended by the run's result. A future
policy change is a new dated decision; it does not retroactively reclassify a VOID as a result or
authorise a retry of this cell.

The decision does not authorise a cell, execute a seed, write a result, change an engine file,
change the seed block or alter the report shape. It only fixes what the runner reports and refuses
when an attempt ends without a complete result.

## 5. Evidence

- [`DECISION-V2-FIRST-CELL-INTERPRETATION`](DECISION-V2-FIRST-CELL-INTERPRETATION.md) — VOID authorises no effect estimate and a further attempt needs a new grant.
- [`V2-FIRST-EXPERIMENT-PREREGISTRATION`](V2-FIRST-EXPERIMENT-PREREGISTRATION.md) — the one cell and its one-report stop.
- `benchmarks/v2_first_cell_runner.py` — the marker-first runner, `--status` classifier and one-shot guard.
- `tests/test_v2_first_cell_runner.py` — the unrun, started-VOID, incomplete-artifact and audit-only cases.
- [`USER-MANUAL`](USER-MANUAL.md) — the command and the operating rule.
- `CHANGELOG.md` — the dated addendum.

## 6. Signature

**Signed 2026-11-16.** The signature sets this decision's `docs/decisions.json` row to `ADOPTED`.
No seed has been executed. `docs/v2_first_cell_result.json` remains absent.

| Check | State at this review |
|---|---|
| Run marker | absent |
| Result | absent |
| Raw log | absent |
| Manifest | absent |
| Cell seeds | ten spent; none executed |
| Runner guard | refuses any marker, manifest, raw log or result |
| Status classifier | `UNRUN` with no artifacts; `VOID` for an interrupted attempt; `COMPLETED` only for an audit-only finished attempt |

| | |
|---|---|
| **Owner** | owner |
| **Status** | `ADOPTED` |
| **Date** | 2026-11-16 |
| **Note** | A started-but-unfinished run is VOID; no retry is permitted. |
