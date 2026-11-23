# The paired 0.9924/0.9925 edge check — result

Generated from `docs/decay_paired_bracket.json` by `python -m benchmarks.decay_paired_bracket --render`. Do not edit by hand.

Protocol: `docs/DECAY-THRESHOLD-PREREGISTRATION.md` section 14. Both factors are measured on the same three seeds, world, arm and runner; the 0.9924 cells are the committed Q050 screen and section-13 edge cells.

**Label: `PAIRED_BRACKET_CONFIRMED`**

| Seed | 0.9924 death | 0.9925 death | Paired |
| --- | --- | --- | --- |
| 20302701 | 300 | 301 | lower dead, upper alive |
| 20302702 | 300 | 301 | lower dead, upper alive |
| 20302703 | 300 | 301 | lower dead, upper alive |

**Prediction (all three 0.9924 dead, all three 0.9925 alive):** held.

## Gates

| Gate | Result |
| --- | --- |
| G1_factor_live | pass |
| G2_denominators | pass |
| G3_cells_complete | pass |
| G4_seed_pairing | pass |
| G5_artifact_matches_parts | pass |

## Scope

This is a paired robustness check requested after Q050, not a new threshold. It fixes the seed block, so the only difference between the two sides of the edge is the decay factor. The resolution remains 0.0001; survival is theory-layer presence, not theory identity; and no adaptation or capability task is scored. Q050 keeps its `NO_INTERIOR_SURVIVOR` label, and 0.9925 remains the first tested survivor.
