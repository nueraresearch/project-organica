# The 0.9924 upper-edge check — result

Generated from `docs/decay_threshold_edge.json`. The screen cell for seed 20302701 is
reused; seeds 20302702 and 20302703 are the post-screen addition.

**Label: `EDGE_CONFIRMED`**

| Seed | Death cycle | Alive at 300 | Stable zero |
| --- | --- | --- | --- |
| 20302701 | 300 | no | 301 |
| 20302702 | 300 | no | 301 |
| 20302703 | 300 | no | 301 |

**Prediction (all three seeds dead):** held.

## Gates

| Gate | Result |
| --- | --- |
| G1_factor_live | pass |
| G2_denominators | pass |
| G3_seed_block | pass |
| G4_cells_complete | pass |

## Scope

This is a post-screen robustness check requested after Q050, not a new threshold and not a
change to the Q050 label. All three seeds die at cycle 300, one cycle before survival; the
0.9924 cell is therefore dead on the three-seed block. 0.9925 remains Q048's first confirmed
survivor. One world, one arm and one factor; no adaptation or capability task is scored.
