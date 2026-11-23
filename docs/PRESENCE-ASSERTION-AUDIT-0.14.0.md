# Presence vs assertion at the 40-slot cap — same-build audit

Generated from `docs/presence_assertion_audit_0.14.0.json` by `python -m benchmarks.presence_assertion_audit --run`. Do not edit by hand.

**Build:** `0.14.0`, `477aeb2ff34dd2cc`; Layer-1 cap **40**.

**Verdict: `PRESENCE NOT ASSERTION`.**

## What was measured

On one build, with the shipped 40-slot Layer-1 prediction cap, how many of the world's edges are present in raw temporal memory, and how many survive into the final asserted structure?

gate_acquisition_sufficiency on the Gate-13 compositional world, six historical seeds, cycles=120 (warmup + acquisition), max_predictions=None so SleepService.MAX_PREDICTIONS=40 is used unchanged. Presence is measured from database temporal edges before the cap; assertion is measured from the final structure after the acquisition loop.

**Cap scope.** The 40-slot cap is the Layer-1 prediction admission budget. presence is measured before that budget is applied. The final asserted structure aggregates all six structure types, so final_asserted_edges is not capped at 40 and must not be read as the number of prediction slots.

## Per-seed audit

| Seed | World edges | Present | Presence rate | Asserted world edges | Assertion rate | Conversion | Present, not asserted | Final asserted structures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20261100 | 112 | 112 | 1.0000 | 40 | 0.3571 | 0.3571 | 72 | 119 |
| 20261101 | 112 | 112 | 1.0000 | 44 | 0.3929 | 0.3929 | 68 | 118 |
| 20261102 | 112 | 112 | 1.0000 | 38 | 0.3393 | 0.3393 | 74 | 111 |
| 20261103 | 112 | 112 | 1.0000 | 46 | 0.4107 | 0.4107 | 66 | 106 |
| 20261104 | 112 | 112 | 1.0000 | 34 | 0.3036 | 0.3036 | 78 | 100 |
| 20261105 | 112 | 112 | 1.0000 | 47 | 0.4196 | 0.4196 | 65 | 132 |

## Summary

| Quantity | Result |
| --- | --- |
| Seeds | 6 |
| World edges | 112 |
| Presence rate | 1.0000–1.0000 |
| Assertion rate | 0.3036–0.4196 |
| Presence → assertion conversion | 0.3036–0.4196 |
| Present but not asserted | 65–78 edges |
| Final asserted structures (all types) | 100–132 |

## Reading

The two quantities answer different questions. Presence is availability in the temporal substrate; assertion is survival in the final structure. A presence rate near 1.0 with a lower assertion rate is a construct separation, not by itself a defect or a causal claim about selection.

## What this does not establish

This audit does not identify which stage loses a present edge, does not manipulate the cap, and does not authorize an engine change. It is a same-build construct check, not a mechanism experiment.

## Prior reference (not pooled)

`docs/temporal_presence_0.13.0.json`, build `0.13.0`: presence 1.0, asserted coverage [0.25, 0.321429]. descriptive prior only; the same-build audit does not re-score or pool the 0.13.0 rows

## Reproduce

```bash
python -m benchmarks.presence_assertion_audit --run
python -m benchmarks.presence_assertion_audit --check
```
