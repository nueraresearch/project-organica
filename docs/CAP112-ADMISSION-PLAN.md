# Plan: the cap-112 admission arm on the landed 0.15.0 build

Generated from `docs/cap112_admission_plan.json` by `python -m benchmarks.cap112_admission_plan --write`. Do not edit by hand.

**Status: ARM DONE.** 0.15.0 landed on 2026-11-11, so the landing checklist is a record, not a to-do list (`docs/LANDING-0.15.0.md`). This plan covers the arm the landing was needed for: what each remaining step needs, and what still blocks it.

**Not a result.** No cell has run; the decision stays **PENDING**, and the acceptance condition is *21–40 transitions must be served at 112*, per seed, with the block's gates passing.

## The landed build

| Item | Value |
| --- | --- |
| Package version | `0.15.0` |
| Layer-1 cap | `112` |
| Pin | `0.15.0` over `14` files |
| Canaries | `0.15.0` |
| Runner preflight | empty |

## Steps, needs and blockers

| # | Step | State | Needs | Blocked by |
| ---: | --- | --- | --- | --- |
| 1 | `land` | **DONE** | version 0.15.0 in the three declarations; the Layer-1 cap 112; a fourteen-file pin at 0.15.0; canaries re-recorded on those bytes | nothing |
| 2 | `frozen-records` | **DONE** | the comparator, Q1 and Q2 records FROZEN (RUN or NOT RUN), granted, with their runners built | nothing |
| 3 | `runner-preflight` | **DONE** | benchmarks/presence_cap112_runners.py, its preflight empty on the installed build, and its self-test green | nothing |
| 4 | `comparator-112` | **DONE** | `--measure --block comparator` on the six audit seeds, then `--finish --block comparator`; this is the row Q1's C9 anchors to | nothing |
| 5 | `admission-arm` | **DONE** | `--measure --block Q2` on six seeds × four levels (24 cells) plus the 112 witness, then `--finish --block Q2`; the acceptance condition is that the 21–40 transitions are served at 112, per seed, with K1–K6 passing | nothing |
| 6 | `verdict` | **DONE** | the arm's 24 cells, its witness and the Q2 verdict rule, read against the bar the cap-40 record fixes | nothing |
| 7 | `band-arm` | **DONE** | record a dated grant for PRESENCE-BAND-1, then `--measure` and `--finish`; the band arm reads the 62 named rank-21-40 edges at 40 and 112 on Q4's six worlds and is the decision's designated test | nothing |
| 8 | `decision` | **BLOCKED** | the band arm's verdict (recorded: VOID on B5), then the owner updates the PENDING admission-step decision with a date and a rationale | the owner's update of the PENDING decision |

`done` is derived from the records; `ready` means its prerequisites hold now; `waiting` means it can be measured but not finished until the named artifact exists; `blocked` means it follows a measurement.

## What still blocks the arm

**Nothing.** The landing, the frozen records and the runner preflight are all satisfied, and the arm's result artifact does not yet exist.

The steps after the arm wait on the recorded verdict, then on the owner: the owner's update of the PENDING decision.

The arm is the **admission** question, not the comparator: Q2 varies only the Layer-1 cap across 40 / 80 / 112 / uncapped on the same six seeds and worlds, with a witness at 112. The comparator-112 is a dependency, because Q2's finish reads its rows for the K gates and Q1's C9 anchors to it; it is not the arm's own test.

## The decision's designated test

The acceptance condition is read on `PRESENCE-BAND-1` (`docs/presence_band_rank_prereg.json`), the 62 named rank-21-40 edges at 40 and 112 on Q4's six worlds. The step is **DONE**.

## Commands, in order

```
python -m benchmarks.presence_cap112_runners --check        # preflight, no cell
python -m benchmarks.presence_cap112_runners --self-test     # gates and verdict rules
python -m benchmarks.presence_cap112_runners --measure --block comparator
python -m benchmarks.presence_cap112_runners --finish  --block comparator
python -m benchmarks.presence_cap112_runners --measure --block Q2
python -m benchmarks.presence_cap112_runners --finish  --block Q2
python -m benchmarks.presence_band_rank_arm --check             # preflight, no cell
python -m benchmarks.presence_band_rank_arm --self-test
python -m benchmarks.presence_band_rank_arm --measure           # REFUSED until granted
python -m benchmarks.presence_band_rank_arm --finish
```

A single cell can be opened with `--cell --block Q2 --seed <seed> --cap <level>`; the parts are cached, so an interrupted measure resumes without re-running a cell.

## What this does not do

- It does not run a cell, adjudicate a verdict or promote the PENDING decision.
- It does not re-derive Q1 or Q2's design, gates, seeds or verdict rules; they are frozen and cited, not restated as new commitments.
- It does not claim 112 is necessary or optimal: the arm tests whether the 21–40 transitions are served, and a negative result moves the next step to the admission rule rather than to another level.

A plan is not a run. No cell was started, no verdict is adjudicated, and the admission-step decision stays PENDING until the arm's verdict exists.
