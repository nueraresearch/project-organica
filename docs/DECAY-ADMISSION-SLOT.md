# Admission count or ranked slot?

Generated from `docs/decay_admission_slot.json` by
`python -m benchmarks.decay_admission_slot --render`. Do not edit by hand.

Pre-registration: `docs/DECAY-ADMISSION-SLOT-PREREGISTRATION.md` (SHA-256 of sections 1-9
recorded in the artifact). The engine is 0.13.0 and unchanged.

## Label

**SLOT_DOMINANT**

Pooled engine-arm misses: 1920, of which **0** were below the admission floor of 5
and **1920** lost a ranked slot out of 40. Shares: admission 0.0, slot 1.0.

## Per seed, engine arm

| Seed | Peak | Final | First zero | Misses | Below admission | Slot loss | Bind cycles |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20301601 | 35 | 0 | 173 | 240 | 0 | 240 | 284 |
| 20301602 | 35 | 0 | 173 | 240 | 0 | 240 | 284 |
| 20301603 | 35 | 0 | 173 | 240 | 0 | 240 | 284 |
| 20301604 | 35 | 0 | 173 | 240 | 0 | 240 | 284 |
| 20301605 | 35 | 0 | 173 | 240 | 0 | 240 | 284 |
| 20301606 | 35 | 0 | 173 | 240 | 0 | 240 | 284 |
| 20301607 | 35 | 0 | 173 | 240 | 0 | 240 | 284 |
| 20301608 | 35 | 0 | 173 | 240 | 0 | 240 | 284 |

## Gates and predictions

| Check | Result |
| --- | --- |
| G1_perturbation_recorded | pass |
| G2_ceiling_reproduced | pass |
| G3_slice_faithful | pass |
| G4_denominator_exists | pass |
| G5_attribution_complete | pass |
| G6_slot_can_fire | pass |
| P1_engine_reaches_zero | held |
| P2_every_miss_classified | held |
| P3_admission_majority_in_six | failed |
| P4_slot_binds_in_six_seeds | held |
| P5_slice_reconstructs | held |
| P6_control_admission_lower | failed |

## Control arm

| Seed | Engine misses | Engine admission share | Control misses | Control admission share |
| --- | --- | --- | --- | --- |
| 20301601 | 240 | 0.0 | 77 | 0.0 |
| 20301602 | 240 | 0.0 | 77 | 0.0 |
| 20301603 | 240 | 0.0 | 77 | 0.0 |
| 20301604 | 240 | 0.0 | 77 | 0.0 |
| 20301605 | 240 | 0.0 | 77 | 0.0 |
| 20301606 | 240 | 0.0 | 77 | 0.0 |
| 20301607 | 240 | 0.0 | 77 | 0.0 |
| 20301608 | 240 | 0.0 | 77 | 0.0 |

## What this establishes

Which gate an edge missed in this world, at this degree, admission floor and budget. It does
not establish that raising either gate would repair persistence, and it does not test other
worlds or other budgets. A `VOID_INSTRUMENT` label is not a verdict.
