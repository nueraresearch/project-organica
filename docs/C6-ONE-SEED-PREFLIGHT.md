# C6 one-seed preflight

**Status: PREFLIGHT — ONE SEED, NOT A RESULT; SUPERSEDED BY THE SIX-SEED C6-TIMING-1 BLOCK.**

This is the first real-world off/on run of the passive C6 observer. It uses the
Q4 world family on seed **20611601**, **120** cycles, cap **40**, and the same
acquisition schedule as the provenance replay. The stock and observed services
are compared on the same deterministic event stream.

## Result

| Quantity | Value |
| --- | ---: |
| World edges | 112 |
| Asserted world edges at the final cycle | 70 |
| World edges that ever entered `Y_full` | 106 |
| World edges with `Y_ind` | 92 |
| World edges with `K` | 94 |
| `K_BEFORE_Y_IND` | 36 |
| `Y_IND_BEFORE_K` | 32 |
| `SAME_CYCLE` | 12 |
| `NO_K` | 12 |
| `NO_Y_IND` | 14 |

`Y_ind` exists on **92 of 106** asserted world edges. Both timing orders occur
on this seed, so the preflight clears the narrow question "does order variation
exist?" The real off/on arms also pass neutrality (`N1`) and final-readout parity
(`N3`). That preflight alone did **not** clear C6: one seed is not a seed block,
and no minimum per-order count had been precommitted. The later six-seed
[`C6-TIMING-1`](C6-TIMING-BLOCK.md) block did.

## What this means

- The non-carrier readout is not empty: the C6 design has something to order.
- The order is not one-sided on this seed: both directions occur.
- The result does **not** select a mechanism. `SAME_CYCLE`, `NO_K` and
  `NO_Y_IND` are reported separately and are not folded into a direction.
- The 70 final asserted world edges and the 106 ever-asserted edges are
  different quantities; the timing rows describe the latter.
- The earlier report-only snapshot had 101 edges while the live set had 196; the 95
  missing carried survivors are why the observer must not use the report alone.
  See [`C6-N3-LIVE-SET-NOTE.md`](C6-N3-LIVE-SET-NOTE.md).

## What is not established

The run does not establish that `Y_ind` is independent of the carrier in the
causal sense. It only establishes the operational readout: assertion supported
by non-loop/dream structures. The C6 protocol still needs the preregistered seed
block and the minimum per-order counts before any C6 verdict.

## Reproduce

```bash
python -m benchmarks.c6_timing_observer --run-one-seed --seed 20611601
```
