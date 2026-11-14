# A1 precommitted thresholds

**Date:** 2026-11-14  
**Status:** `PRECOMMITTED BEFORE ANY A1 CELL`

**This is not an experimental result and not a grant.** No cell, seed or engine change was made.

These values were fixed before any A1 cell. They are manipulation and independence margins,
not predictions of the primary effect, and they are not estimated from A0 or any run.

| Gate | Quantity | Value | Definition |
| --- | --- | ---: | --- |
| `C1_path_separation` | A- carrier preservation | 0.95 | Proportion of paired-control carrier-available edges still carrier-available under A-, per seed. |
| `C1_path_separation` | K- served preservation | 0.95 | Proportion of paired-control served edges still served under K-, per seed. |
| `C4_no_interference` | neighbour delta | 0.05 | Maximum absolute A, K or Y availability-rate difference on non-target edges against the paired control. |
| `C7_assertion_block` | A delta under Y- | 0.05 | Absolute A formation-rate difference between Y- and the paired no-Y- control. |
| `C7_assertion_block` | K delta under Y- | 0.05 | Absolute K formation-rate difference between Y- and the paired no-Y- control. |
| `C8_third_route` | A-K- assertion ceiling | 0.05 | Assertion rate in A-K-; above the ceiling is THIRD ROUTE PRESENT. |

## Reading

`C1` needs at least 95% preservation of the other path on every seed; the denominator is
the paired control's available edges, not the whole candidate universe. `C4` and `C7` use a
0.05 absolute-rate margin. `C8` reads `THIRD ROUTE PRESENT` above a 0.05 assertion rate in
`A-K-`.

A condition with no available edges is NOT MEASURABLE, not zero, and does not pass.

## Fragility

At 26 paired carrier rows, a 0.95 preservation floor allows one edge to differ and fails at two; at larger denominators it allows proportionally more. A descriptive sensitivity at 0 and 0.10 is reported beside the result but cannot change the precommitted gate.

**Source:** Design convention fixed 2026-11-14 before any A1 cell. No A0 row, seed or run result was used to choose a value.

**Not evidence:** Thresholds and definitions only. No cell has run; this is not a grant and makes no causal, capability or transfer claim.

## Reproduce

```bash
python -m benchmarks.a1_gate_readiness --check
```
