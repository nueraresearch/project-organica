# Authorisation — `PRESENCE-CONVERSION-2` (Q4)

**Status: GRANTED, 2026-11-11. The block is frozen, granted and still unrun: no runner is installed.**

The owner's words, given on 2026-11-11 in the instruction that recorded this grant:

> then run the twelve-cell campaign and adjudicate N1–N7

## What the grant covers

The fourteen runs the frozen record fixes, on the pinned 0.14.0 engine at cap 40, 120 cycles each:

- **12 design cells** — arms `off` and `on` × seeds `20611601`–`20611606`;
- **1 witness cell** — seed `20261100`, observer off, to reproduce the published audit row;
- **1 determinism rerun** — seed `20611601`, observer on, in a fresh process.

It authorises those runs and their N1–N7 adjudication, nothing more. It does not authorise an engine
edit, a change to `MAX_PREDICTIONS`, a capability claim, or any re-reading of `PRESENCE-CONVERSION-1`.

## What the grant does not install

The block has **no runner**. `presence_conversion_repair.refuse()` refuses `--measure` with
"authorised but has no runner": the repaired observer exists and its N2 fixture passes, but no harness
executes the fourteen runs or adjudicates N1–N7. The grant authorises the campaign; it does not build
it, and no cell has run.

## How the record answers

| Outcome | Verdict |
|---|---|
| `N1` fails on any seed — served window differs from a plain engine run | `SERVED NOT ENGINE` |
| `N2` fails — mutating or disabling the observation changes the served window | `OBSERVATION LEAKS` |
| Any other gate fails (`N3`–`N7`) | `VOID` |
| All gates pass and `A_pred < S_ever` | `CONVERSION STAGE MEASURED` |

— Recorded 2026-11-11 against the uncommitted worktree at `fb701f4`.
