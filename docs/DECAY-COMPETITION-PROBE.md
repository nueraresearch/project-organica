# The competition-collapse signature at 0.9924 — result

Generated from `docs/decay_competition_probe.json` by `python -m benchmarks.decay_competition_probe --render`. Do not edit by hand.

Protocol: `docs/DECAY-THRESHOLD-PREREGISTRATION.md` section 15. The probe records the engine's retained hypotheses, formed theories and pre-decay edge counts for cycles 295-300. Seed 20302701 is the control against the committed support probe.

**Label: `SAME_PAIR`**

| Seed | Last live | Death | Top subject | Support | Competing supports |
| --- | --- | --- | --- | --- | --- |
| 20302701 | 299 | 300 | bravo | 866 | charlie 433, alpha 433 |
| 20302702 | 299 | 300 | bravo | 866 | charlie 433, alpha 433 |
| 20302703 | 299 | 300 | bravo | 866 | charlie 433, alpha 433 |

**Pair-loss signature on all three seeds:** yes.

At the death cycle each subject retains one competing hypothesis plus one `high_structural_significance` marker; the engine drops that marker before theory formation, so the competing population has one member per subject. The artifact keeps both counts.

**Seed variation:** none; the three cells reproduce the same trajectory, so this is not three independent draws.

## Gates

| Gate | Result |
| --- | --- |
| G1_factor_live | pass |
| G2_capture_window | pass |
| G3_control_reproduced | pass |
| G4_threshold_block | pass |
| G5_artifact_matches_parts | pass |

## Scope

This is a mechanism diagnostic on the three threshold seeds, requested after the paired edge check. It does not change Q050's label, is not a new threshold, and scores no adaptation or capability task. The supports are temporal transition counts, not observations, and survival is theory-layer presence, not theory identity.
