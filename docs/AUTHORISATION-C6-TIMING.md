# Authorisation — `C6-TIMING-1`

**Status: GRANTED AND RUN, 2026-11-13. The block is frozen and the grant covers only the twelve listed runs.**

The owner's words, given on 2026-11-13 in the instruction that requested this block:

> Preregister the C6 seed block and minimum per-order counts, then run the remaining seeds.

## What the grant covers

Twelve runs on the pinned **0.15.0** engine:

- **6 seeds** — 20621101, 20621102, 20621103, 20621104, 20621105, 20621106;
- **2 arms** — observer `off` and observer `on`;
- **120 cycles**, cap **40**, the `PHASE_ACQUISITION` schedule.

It authorises the C6 timing measurement and the `N1`/`N3` adjudication for those runs, nothing more.

## What it does not authorise

- No `A−` admission block.
- No `K−` carrier block.
- No `Y−` assertion block.
- No engine edit, version bump or pin change.
- No causal mechanism claim.
- No V2 work.
- No optional seeds and no seed replacement.

## How the record answers

| Outcome | Verdict |
|---|---|
| `N1`/`N3` pass; every seed has ≥10 edges in each order; both orders on ≥5/6 seeds | `C6 ORDER VARIATION CONFIRMED` |
| Gates pass but a per-order floor or the 5/6 coverage rule fails | `C6 NOT SEPARATED` |
| Any seed has no `Y_ind` | `C6 NOT MEASURABLE` |
| Any `N1`, `N3` or engine-pin gate fails | `VOID` |

— Recorded 2026-11-13 against the frozen record `docs/c6_timing_prereg.json`. The twelve runs
completed and are recorded in `docs/C6-TIMING-BLOCK.md` and `docs/c6_timing_block.json`.
