# The decay threshold inside 0.99–0.9925 — result

Generated from `docs/decay_threshold.json` by `python -m benchmarks.decay_threshold --render`. Do not edit by hand.

Pre-registration: `docs/DECAY-THRESHOLD-PREREGISTRATION.md`. Twenty-four four-decimal candidates, screen seed 20302701, confirmation seeds 20302701–20302703.

**Label: `NO_INTERIOR_SURVIVOR`**

| Factor | Screen death | Alive at 300 |
| --- | --- | --- |
| 0.9901 | 231 | no |
| 0.9902 | 237 | no |
| 0.9903 | 237 | no |
| 0.9904 | 237 | no |
| 0.9905 | 243 | no |
| 0.9906 | 243 | no |
| 0.9907 | 246 | no |
| 0.9908 | 249 | no |
| 0.9909 | 255 | no |
| 0.991 | 255 | no |
| 0.9911 | 257 | no |
| 0.9912 | 261 | no |
| 0.9913 | 264 | no |
| 0.9914 | 267 | no |
| 0.9915 | 273 | no |
| 0.9916 | 273 | no |
| 0.9917 | 279 | no |
| 0.9918 | 282 | no |
| 0.9919 | 282 | no |
| 0.992 | 288 | no |
| 0.9921 | 291 | no |
| 0.9922 | 297 | no |
| 0.9923 | 300 | no |
| 0.9924 | 300 | no |

**Smallest confirmed survivor:** none.

**Screen boundary:** none.

## Confirmation

No boundary was confirmed; see the label.

## Gates

| Gate | Result |
| --- | --- |
| G1_screen_factor_live | pass |
| G2_confirmation_factor_live | pass |
| G3_denominators | pass |
| G4_seeds_fresh | pass |
| G5_screen_complete | pass |
| G6_confirmation_complete | pass |

## Predictions

| Prediction | Result |
| --- | --- |
| P1_screen_monotone | held |
| P2_interior_survivor | failed |
| P3_below_09925 | failed |
| P4_boundary_alive_3 | failed |
| P5_lower_dead_3 | failed |
| P6_upper_alive_3 | failed |

## Reading

This is a 0.0001-resolution screen plus a three-seed confirmation at the boundary and its
two immediate neighbours. The screen is one seed per candidate; only the confirmed
boundary is a claim. Survival is theory-layer presence, not theory identity, and no
adaptation or capability task is scored here.

The endpoints 0.99 and 0.9925 are Q048 results on a different seed block; this page
does not re-measure them.
