# The store-time observer: verdicts at the recorded hash-seed pairs

**Status: frozen on generation.** Written by `--verdict-pairs` from
`docs/store_time_observer_verdicts_pairs.json`. Pre-registration:
`docs/STORE-TIME-OBSERVER-BRIEF.md` section 11.

Each case runs at the pair `docs/candidate_membership_audit.json`
measured it at. The earlier pass at hash seeds 0/1 is kept separately in
`docs/STORE-TIME-OBSERVER-VERDICTS.md` and is not reinterpreted here.

| Case | Pair | Cycle | Pool sizes | Differences | Attributed | Labels | Outcome |
|---|---|---|---|---|---|---|---|
| T1 / 20261125 / B | 0 / 2 | 12 | 268/271 | 27 | 27 | `pool:anomaly`, `pool:dream`, `pool:experiment`, `pool:hypothesis`, `pool:investigation`, `pool:loop_candidate`, `pool:prediction_candidate`, `pool:question`, `pool:theory` | **construction_other:pool:anomaly+pool:dream+pool:experiment+pool:hypothesis+pool:investigation+pool:loop_candidate+pool:prediction_candidate+pool:question+pool:theory** |
| T1 / 20261125 / C | 0 / 2 | 12 | 268/271 | 27 | 27 | `pool:anomaly`, `pool:dream`, `pool:experiment`, `pool:hypothesis`, `pool:investigation`, `pool:loop_candidate`, `pool:prediction_candidate`, `pool:question`, `pool:theory` | **construction_other:pool:anomaly+pool:dream+pool:experiment+pool:hypothesis+pool:investigation+pool:loop_candidate+pool:prediction_candidate+pool:question+pool:theory** |
| T2 / 20261120 / B | 0 / 13 | 6 | 98/98 | 14 | 8 | `pool:anomaly`, `pool:dream`, `pool:experiment`, `pool:investigation`, `pool:prediction_candidate`, `restore:loop_candidate` | **indeterminate** |
| T2 / 20261120 / C | 0 / 13 | 6 | 98/98 | 14 | 8 | `pool:anomaly`, `pool:dream`, `pool:experiment`, `pool:investigation`, `pool:prediction_candidate`, `restore:loop_candidate` | **indeterminate** |
| T2 / 20261121 / B | 0 / 2 | 6 | 82/82 | 6 | 6 | `pool:anomaly`, `pool:dream`, `pool:prediction_candidate` | **construction_other:pool:anomaly+pool:dream+pool:prediction_candidate** |

## Outcome counts

- `construction_other:pool:anomaly+pool:dream+pool:experiment+pool:hypothesis+pool:investigation+pool:loop_candidate+pool:prediction_candidate+pool:question+pool:theory`: 2
- `construction_other:pool:anomaly+pool:dream+pool:prediction_candidate`: 1
- `indeterminate`: 2
