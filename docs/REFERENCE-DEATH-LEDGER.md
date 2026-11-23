# Reference-arm death ledger — result

**Measured 2026-11-07: `SHARED_DOMINANT`.** Six arms × three seeds × 300 cycles on the falsifier's `lattice_L1` stimulus, engine 0.13.0. Yes, but shared: every arm's theory layer dies within the margin, so death is the system's dominant failure mode and the lever is the common belief-formation and decay substrate, not any arm's policy.

## Death cycles

| Arm | Per-seed death cycle | Median | Theory cycles | Theory removals |
| --- | --- | --- | --- | --- |
| FULL | 39, 39, 39 | 39 | 111 | 126 |
| SALIENCE | 39, 39, 39 | 39 | 111 | 354 |
| NO_CONTRADICTIONS | 39, 39, 39 | 39 | 111 | 357 |
| NO_QUESTIONS | 39, 39, 39 | 39 | 111 | 354 |
| NO_DREAMS | 39, 39, 39 | 39 | 111 | 354 |
| ANTI_EIG | 39, 39, 39 | 39 | 111 | 354 |

The reference arm's median death cycle is **39**; the earliest ablation death is **39** and the latest is **39**. Reference-arm theory removals are **126 of 1899** events (6.6%), and the reference's modal mechanism is `superseded`.

## Mechanisms

### Theory removals

| Arm | superseded | parent_loss | competing_collapse | capped | unexplained |
| --- | --- | --- | --- | --- | --- |
| FULL | 102 | 24 | 0 | 0 | 0 |
| SALIENCE | 105 | 249 | 0 | 0 | 0 |
| NO_CONTRADICTIONS | 102 | 255 | 0 | 0 | 0 |
| NO_QUESTIONS | 105 | 249 | 0 | 0 | 0 |
| NO_DREAMS | 105 | 249 | 0 | 0 | 0 |
| ANTI_EIG | 105 | 249 | 0 | 0 | 0 |

### Belief removals

| Arm | capped | not_reformed |
| --- | --- | --- |
| FULL | 30 | 60 |
| SALIENCE | 300 | 54 |
| NO_CONTRADICTIONS | 306 | 54 |
| NO_QUESTIONS | 300 | 54 |
| NO_DREAMS | 300 | 54 |
| ANTI_EIG | 300 | 54 |

## Gates

| Gate | Result |
| --- | --- |
| G1_neutral_observer | pass |
| G2_attribution_complete | pass |
| G3_axis_live | pass |
| G4_denominators | pass |
| G5_seed_independence | pass |

The neutrality control compared the ledgered reference arm at seed 20261023 against `docs/decay_falsifier/parts/FULL.json`: theories match **yes**, beliefs match **yes**.

## Predictions

| Prediction | Result |
| --- | --- |
| P1_every_arm_dies_before_end | held |
| P2_every_ablation_within_margin | held |
| P3_reference_modal_parent_loss | failed |
| P4_no_unexplained_in_reference | held |

## Q042

**SUPPORTED.** Yes, but shared: every arm's theory layer dies within the margin, so death is the system's dominant failure mode and the lever is the common belief-formation and decay substrate, not any arm's policy.

Removal events are not distinct objects: a theory that returns and dies again counts again. The ledger is observational, and it cannot see why an edge failed to form — only that the belief carrying it was not formed.

The outcome section of the pre-registration is written from this artifact, and `--check` rejects a protocol whose execution record and artifact disagree.
