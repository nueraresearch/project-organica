# Does persistence cost adaptation? — result

Generated from `docs/decay_adaptation.json` by
`python -m benchmarks.decay_adaptation --render`. Do not edit by hand.

Pre-registration: `docs/DECAY-ADAPTATION-PREREGISTRATION.md`. Four decay arms on the
two Phase J gradual-shift families, 5 seeds, 80 cycles; endpoint is final NLL over
cycles 60-79 on the shifted world.

**Label: `NO_COST_DETECTED`**

| Arm | Family | Final NLL | Delta vs shipped | 97.5% CI | Cells |
| --- | --- | --- | --- | --- | --- |
| shipped | cause_mix | 2.202999 | +0.000000 | [0.0, 0.0] | 5 |
| shipped | mapping_mix | 3.205089 | +0.000000 | [0.0, 0.0] | 5 |
| **shipped** | **pooled** |  | **+0.000000** | **[0.0, 0.0]** | **10** |
| factor099 | cause_mix | 2.300530 | +0.097530 | [-0.034696, 0.235862] | 5 |
| factor099 | mapping_mix | 3.078843 | -0.126246 | [-0.344486, 0.090045] | 5 |
| **factor099** | **pooled** |  | **-0.014358** | **[-0.173089, 0.133606]** | **10** |
| factor09925 | cause_mix | 2.476437 | +0.273437 | [-0.026161, 0.743281] | 5 |
| factor09925 | mapping_mix | 3.094914 | -0.110175 | [-0.330307, 0.106713] | 5 |
| **factor09925** | **pooled** |  | **+0.081631** | **[-0.15496, 0.416613]** | **10** |
| no_decay | cause_mix | 2.303472 | +0.100473 | [-0.02941, 0.246805] | 5 |
| no_decay | mapping_mix | 3.108074 | -0.097015 | [-0.319781, 0.120702] | 5 |
| **no_decay** | **pooled** |  | **+0.001729** | **[-0.154944, 0.146584]** | **10** |

A positive delta means the arm has higher post-shift loss than shipped, so it adapted
worse. Cost is a pooled mean of at least 0.05 nats per event with the interval's lower
bound above zero; better is the reverse. The 0.99 arm is descriptive only.

## Gates

| Gate | Result |
| --- | --- |
| G1_factor_live | pass |
| G2_denominators | pass |
| G3_seed_independence | pass |
| G4_complete_design | pass |
| G5_perturbation_changes_mass | pass |

## Predictions

| Prediction | Result |
| --- | --- |
| P1_no_decay_mass_unchanged | held |
| P2_shipped_mass_declines | held |
| P3_no_decay_mapping_cost | failed |
| P4_operating_no_worse_than_ceiling | failed |
| P5_cost_detected | failed |
| P6_anchor_not_better | held |

## Reading

This is a five-seed pilot on two synthetic gradual-shift families. It is not a Phase J
verdict, and it does not generalize to other generators or natural environments. The
endpoint is online next-event NLL; it does not show that the organism learned the right
structure. No capability, held-out prediction, revision or transfer task is scored.

Survival at 1.0 is a persistence result. A no-cost adaptation result here would not make
1.0 or 0.9925 an adoption recommendation, and a cost result prices a trade rather than
closing the persistence question.
