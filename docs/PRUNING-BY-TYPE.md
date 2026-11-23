# What pruning removes, by candidate type — measurement

Generated from `docs/pruning_by_type.json` by
`python -m benchmarks.pruning_by_type --aggregate`. Do not edit by hand.

## Label

**PRUNING_PARTIAL**

## The terminal event of every peak edge

Each edge that made the peak is followed to the end of the horizon and placed in exactly
one category. `pruned` means the engine wrote a retirement record for its candidate;
`withdrawn_without_pruning` means the edge left the stable set and no retirement record
was written; `alive` means it was still stable at the last cycle and is not a death.

| Category | Engine arm | No-decay control |
| --- | --- | --- |
| Peak edges | 105 | 126 |
| Pruned | 96 | 42 |
| Withdrawn, never pruned | 9 | 0 |
| Alive at the end | 0 | 84 |
| Deaths | 105 | 42 |
| Pruned share of deaths | 0.9143 | 1.0 |

## What the engine retired, by type

The observer counts the record the engine writes, so this is the same population its own
counter totals. The reconciliation column is what makes the split attributable: the
observed retirements must equal the engine's `pruned` return value on every cycle.

| Candidate type | Engine arm | No-decay control |
| --- | --- | --- |
| `dream` | 1326 | 1047 |
| `experiment` | 1320 | 1038 |
| `hypothesis` | 123 | 39 |
| `investigation` | 1320 | 1038 |
| `loop_candidate` | 21 | 18 |
| `phrase_candidate` | 3 | 3 |
| `prediction_candidate` | 2478 | 78 |
| `process_candidate` | 246 | 474 |
| `question` | 93 | 819 |
| `role_candidate` | 9 | 9 |
| `schema_candidate` | 18 | 18 |
| `theory` | 51 | 33 |
| `workflow_concept` | 114 | 306 |

| Quantity | Engine arm | No-decay control |
| --- | --- | --- |
| Seeds | 3 | 3 |
| Cycles per seed | 300 | 300 |
| Reconciliation mismatches | 0 | 0 |

## Per seed, engine arm

| Seed | Peak edges | Pruned | Withdrawn | Alive |
| --- | --- | --- | --- | --- |
| 20300601 | 35 | 32 | 3 | 0 |
| 20300602 | 35 | 32 | 3 | 0 |
| 20300603 | 35 | 32 | 3 | 0 |

## What this changes

- **The fourth category is now measured for edges, not only for candidates.** The share
  above is pruning's part in the deaths of the structures that formed, which the
  attribution ledger's window could not express.
- **`decayed` and `pruned` are two stages of one process.** An edge crossing 0.30 is
  labelled `decayed` by the attribution ledger; the candidate behind it is retired when
  it reaches 0.15, and this record counts that retirement as the terminal event.
- **The engine's total counter is now split.** A total of prunings across every surviving
  generation said nothing about edges; the type table says how much of it they are.

## What this does not establish

- **One world, one degree, three seeds.** It measures this collapse, as the attribution
  record does, and inherits its scope.
- **Retirement is not deletion.** The engine stores a retired record so the candidate
  cannot resurrect; whether the row is later removed from the substrate is a different
  question.
- **A withdrawn edge was not pruned inside the horizon.** It says nothing about whether it
  would have been pruned later.
