# The store-time observer: verdicts over the five search cases

**Status: frozen on generation.** Written by `--verdict` from
`docs/store_time_observer_verdicts.json`. Pre-registration:
`docs/STORE-TIME-OBSERVER-BRIEF.md` section 10, committed before the run.

Hash seeds 0 and 1. Arm C is run as a staged pair: arm B first, its per-cycle temporal
graphs handed to C, both observed.

| Case | Cycle | Pool sizes | Differences | Attributed | Labels | Outcome |
|---|---|---|---|---|---|---|
| T1 / 20261125 / B | 12 | 268/268 | 0 | 0 | none | **no_difference_at_pair** |
| T1 / 20261125 / C | 12 | 268/268 | 0 | 0 | none | **no_difference_at_pair** |
| T2 / 20261120 / B | 6 | 98/98 | 0 | 0 | none | **no_difference_at_pair** |
| T2 / 20261120 / C | 6 | 98/98 | 0 | 0 | none | **no_difference_at_pair** |
| T2 / 20261121 / B | 6 | 82/82 | 0 | 0 | none | **no_difference_at_pair** |

## Outcome counts

- `no_difference_at_pair`: 5

## What the buckets mean

`no_difference_at_pair` - the windows were identical at this hash-seed
pair, so the cell measured nothing; it is not `C_accounted`.
`C_accounted` - differences exist, no write explains them, and the
writes fully reconciled. `indeterminate` - unreconciled, or only
partially explained. A partial explanation is never folded into
`C_accounted`.
