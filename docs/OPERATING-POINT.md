# The decay operating point — result

Generated from `docs/operating_point.json` by
`python -m benchmarks.operating_point --render`. Do not edit by hand.

Pre-registration: `docs/OPERATING-POINT-PREREGISTRATION.md`. Six conditions on the
falsifier's `lattice_L1` world, reference arm FULL, seeds 20302401-20302403.

**Label: `PARTIAL_LADDER`**

| Condition | Death cycles | Median | Viable | Stable zero |
| --- | --- | --- | --- | --- |
| shipped | [39, 39, 39] | 39 | no | [142, 142, 142] |
| floor2 | [39, 39, 39] | 39 | no | [142, 142, 142] |
| floor5 | [39, 39, 39] | 39 | no | [142, 142, 142] |
| factor099 | [228, 228, 228] | 228 | yes | [301, 301, 301] |
| recency | [76, 76, 76] | 76 | yes | [301, 301, 301] |
| no_decay | [301, 301, 301] | 301 | yes | [301, 301, 301] |

## Gates

| Gate | Result |
| --- | --- |
| G1_neutral_observer | pass |
| G2_baseline_39 | pass |
| G3_floor_live | FAIL |
| G4_factor_live | pass |
| G5_recency_live | pass |
| G6_no_decay_live | pass |
| G7_denominators | pass |
| G8_seed_independence | pass |

## Predictions

| Prediction | Result |
| --- | --- |
| P1_baseline_39 | held |
| P2_no_decay_highest | held |
| P3_factor099_viable | held |
| P4_recency_viable | held |
| P5_floor5_between | failed |
| P6_floor2_control | held |
| P7_perturbations_fire | failed |
| P8_ordering | failed |
| P9_stable_zero_later | held |

## Reading

The primary endpoint is theory death, with 301 meaning alive at cycle 300. A condition is
viable when it gains at least 10 cycles on at least 2 of 3 paired seeds.

**`floor5` is an eligibility intervention, not a retention intervention.** It lifts every
edge with count 1-4 to 5, so the `>= 5` admission gate stops filtering; admitted edges
above 5 decay exactly as shipped. `floor2` lifts only count 1 to 2 and is the negative
control, not a repair.

**`no_decay` is an upper bound measured here for the first time on `lattice_L1`.** The
degree-12 hub's no-decay survival is not evidence for this world.

A viable arm is a persistence candidate, not an adoption recommendation. Adoption needs a
capability study and an owner decision; this protocol scores no prediction, revision or
adaptation task.

The control (shipped FULL at seed 20261023) matched the committed falsifier theories: **True**;
beliefs: **True**.
