# Substrate repair across the six arms — result

Generated from `docs/substrate_repair.json` by
`python -m benchmarks.substrate_repair --render`. Do not edit by hand.

Pre-registration: `docs/SUBSTRATE-REPAIR-PREREGISTRATION.md`. The repair is the
temporal-edge decay factor, 0.95 to 0.99, applied identically to every arm.

**Label: `SUBSTRATE_REPAIR`**

| Arm | Shipped death | Repaired death | Per-seed delta | Seeds extended |
| --- | --- | --- | --- | --- |
| FULL | [39, 39, 39] | [228, 228, 228] | [189, 189, 189] | 3 of 3 |
| SALIENCE | [39, 39, 39] | [228, 228, 228] | [189, 189, 189] | 3 of 3 |
| NO_CONTRADICTIONS | [39, 39, 39] | [228, 228, 228] | [189, 189, 189] | 3 of 3 |
| NO_QUESTIONS | [39, 39, 39] | [228, 228, 228] | [189, 189, 189] | 3 of 3 |
| NO_DREAMS | [39, 39, 39] | [228, 228, 228] | [189, 189, 189] | 3 of 3 |
| ANTI_EIG | [39, 39, 39] | [228, 228, 228] | [189, 189, 189] | 3 of 3 |

## Gates

| Gate | Result |
| --- | --- |
| G1_neutral_observer | pass |
| G2_repair_live | pass |
| G3_baseline_39 | pass |
| G4_denominators | pass |
| G5_seed_independence | pass |

## Predictions

| Prediction | Result |
| --- | --- |
| P1_baseline_39 | held |
| P2_repair_live | held |
| P3_all_six_extend | held |
| P4_shared_timing | held |
| P5_parent_loss_falls | held |

## Reading

All six arms extend by the margin: **True**. The repaired death cycles across the six arms are [0, 0, 0], so the shared-timing prediction held.

The control (shipped FULL at seed 20261023) matched the committed falsifier theories: **True**;
beliefs: **True**.

The repair changes the temporal decay rate only. It says nothing about belief formation,
the admission floor, the candidate-decay factor or the theory cap.
