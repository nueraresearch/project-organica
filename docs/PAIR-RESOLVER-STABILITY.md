# Pair resolver stability (Q028)

**Generated from [`docs/pair_resolver_stability.json`](pair_resolver_stability.json); do not
edit by hand.** Rebuild with `python -m benchmarks.pair_resolver_stability --run`, and
check the page with `--check`.

## What was re-run

The pair resolver in `benchmarks/transfer_provenance.py`, unchanged, on the calibration
seed and on six fresh seeds. Each cell runs both contexts for 40 + 40 cycles and traces
every schema-primed prediction in context B. The published calibration cell is restated
here, not re-derived: 14 transfers, 8 resolved to the schema's role pair, 6
`unresolved_pair_not_in_roles`.

**Label: `VARIABLE_DENOMINATOR`**

| seed | role | transfers | resolved to pair | share | polarity-only | single-role resolved |
| --- | --- | --- | --- | --- | --- | --- |
| 20261101 | control | 14 | 8 | 0.5714 | 6 | 0 |
| 20301801 | fresh | 12 | 6 | 0.5000 | 6 | 0 |
| 20301802 | fresh | 25 | 6 | 0.2400 | 19 | 3 |
| 20301803 | fresh | 22 | 6 | 0.2727 | 16 | 0 |
| 20301804 | fresh | 19 | 9 | 0.4737 | 10 | 1 |
| 20301805 | fresh | 15 | 6 | 0.4000 | 9 | 2 |
| 20301806 | fresh | 14 | 2 | 0.1429 | 12 | 1 |

## What the label means

The number of transfer events itself moved across seeds, so the split is a property of the draw as well as of the resolver.

## Controls and scope

- The instrument's own control set runs before any cell; it passed: yes.
- The calibration seed is a reproduction control, and it is judged before the fresh cells.
- Every cell records the single-role reading as well, so the pair resolver's difference from the predicate it replaced stays visible.
- This is not Q028's answer and not a transfer claim. It tests whether one calibration split is stable across seeds in the same world family, at the same cycle counts.
