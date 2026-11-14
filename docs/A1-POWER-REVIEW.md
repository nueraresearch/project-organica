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

## What population A1 tests

**Estimand:** representative eligible pre-37 cycle-membership directed-edge population.

A1 tests a representative eligible-edge effect. It does not test an effect among high-propensity or anomalous edges; that would require a different selector and a new target set before freeze.

It is **not** a sample of high-U edges, hard edges, carrier-enriched anomalies.

## Freeze question

**Does a random eligible-edge design have enough expected measurable structure to justify freeze?**

**Answer: NO — NOT AS CURRENTLY EMITTED.** K and Y_ind prevalence are high enough that missing structure is not the blocker. The blocker is C1: four rows make the 0.95 floor a 100% rule, and the all-six all-four-K proxy is 6.9% under independence. C4 rows or a larger N must change the denominator before freeze.

- If yes: Freeze the representative eligible-edge design after the manifest review.
- If no: Do not freeze; enlarge the C1 denominator with C4 rows or redesign the target block.

## Freeze decision

**DO NOT FREEZE (2026-11-14).** Answer: **NO — NOT AS CURRENTLY EMITTED**.

**Scope:** the current six-seed target artifact and the current four-target A1 cell output.

**Are the target sets worth freezing?** **NO — HOLD AS DRAFT UNTIL C1/C4 ARE MEASURED.** The target sets are compliant and representative, but no cell has run with the new C4 neighbour stream, so the C1 and C4 denominators remain unmeasured. Do not regenerate targets unless Path B is chosen.

**Basis:**
- The C6 prevalence proxy is adequate: 602/672 K and 586/672 Y_ind.
- The C1 denominator is at most four target rows, so the 0.95 floor is a 100% rule (3/4 = 0.75).
- All six seeds having all four K rows is 6.9% under independence; the design is fragile, not merely underpowered.

**Revisit when:**
- The planned cells run with the C4 neighbour stream and C1/C4 are scored.
- A larger target block or a redesigned selector is registered before freeze.

## Decision

**FREEZE READINESS OPEN — C1 DENOMINATOR FRAGILITY**

P0 and feasibility pass, but four target rows per seed make the precommitted 0.95 C1 floor a 100% preservation rule. The prevalence proxy is adequate; the denominator is not. The current cell emits target rows only; C4 non-target rows are needed to give C1 a denominator larger than four. Do not freeze on the current target artifact.

### Next
- If Path A (representative eligible-edge effect) is retained: run the planned cells with the C4 neighbour stream and score C1/C4.
- If Path B (high-carrier-propensity effect) is required: redesign the selector and regenerate targets before freeze; that is a different experiment.
- Re-run this review after C1/C4 are measured; do not freeze before that.

**Not evidence:** A read-only power/prevalence review over different-seed C6 and A0 records. It runs no A1 cell, assigns no seed, freezes no target and establishes no causal, capability or transfer claim.
