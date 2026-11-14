# A1 power and prevalence review

**Status:** `FREEZE READINESS OPEN — C1 DENOMINATOR FRAGILITY`

**This is not an A1 result.** No arm cell was run; no target was frozen.

| Finding | Evidence |
| --- | --- |
| **selection_is_random_on_u** — The 24 targets are statistically indistinguishable from the 358 unselected candidates on cycle-36 strength. | selected_n=24; unselected_n=358; selected_median=16.0; unselected_median=16.0; selected_mean=15.333; unselected_mean=15.215; permutation_p=0.91765 |
| **all_candidates_eligible** — Cycle membership and positive U do not narrow the candidate universe; every candidate is eligible. | candidate_counts={'20630101': 64, '20630102': 63, '20630103': 64, '20630104': 64, '20630105': 64, '20630106': 63}; eligible_counts={'20630101': 64, '20630102': 63, '20630103': 64, '20630104': 64, '20630105': 64, '20630106': 63} |
| **c6_denominator_proxy** — C6 supplies a high K/Y_ind denominator in its own world; this is a proxy, not target validation. | c6_k=602; c6_world_edges=672; c6_y=586; c6_k_rate=0.896; c6_y_rate=0.872; per_seed_k_rate_min=0.848; per_seed_k_rate_max=0.991; per_seed_all_four_k=[0.636, 0.563, 0.965, 0.586, 0.661, 0.518]; all_six_all_four_k_independence=0.069; target_overlap_observations=53; target_overlap_k=50; target_overlap_y=46 |
| **c1_denominator_fragility** — With four target rows, the 0.95 C1 floor is effectively 100% preservation; one lost row gives 0.75. | rows_per_seed=4; c1_floor=0.95; max_losses_at_4=0; effective_floor_at_4=1.0; illustration_3_of_4=0.75; max_losses_if_112_rows=5 |
| **hard_edge_baseline** — A0's hard-edge prevalence is low, but a random 24-target sample has a material chance of containing one. | a0_hard_edges=26; a0_present_edges=672; hard_rate=0.0387; expected_hard_targets=0.93; prob_any_hard_independence=0.612 |

## Decision

**FREEZE READINESS OPEN — C1 DENOMINATOR FRAGILITY**

P0 and feasibility pass, but four target rows per seed make the precommitted 0.95 C1 floor a 100% preservation rule. The current cell emits target rows only; C4 non-target rows are needed to give C1 a denominator larger than four. Do not freeze on the current target artifact.

### Next
- Implement C4 non-target rows so C1 can use all paired-control available edges.
- Re-run this review against that larger denominator.
- Only then decide whether N = 4 is adequate or the target rule needs redesign.

**Not evidence:** A read-only power/prevalence review over different-seed C6 and A0 records. It runs no A1 cell, assigns no seed, freezes no target and establishes no causal, capability or transfer claim.
