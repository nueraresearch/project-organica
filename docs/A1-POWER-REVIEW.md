# A1 power and prevalence review

**Status:** `FREEZE READINESS OPEN — C1 DENOMINATOR FRAGILITY`

**This is not an A1 result.** No arm cell was run; no target was frozen.

| Finding | Evidence |
| --- | --- |
| **selection_is_random_on_u** — The 24 targets are statistically indistinguishable from the 358 unselected candidates on cycle-36 strength. | selected_n=24; unselected_n=358; selected_median=16.0; unselected_median=16.0; selected_mean=15.333; unselected_mean=15.215; permutation_p=0.91765 |
| **all_candidates_eligible** — Cycle membership and positive U do not narrow the candidate universe; every candidate is eligible. | candidate_counts={'20630101': 64, '20630102': 63, '20630103': 64, '20630104': 64, '20630105': 64, '20630106': 63}; eligible_counts={'20630101': 64, '20630102': 63, '20630103': 64, '20630104': 64, '20630105': 64, '20630106': 63} |
| **c6_denominator_proxy** — C6 supplies a high K/Y_ind denominator in its own world; this is a proxy, not target validation. | c6_k=602; c6_world_edges=672; c6_y=586; c6_k_rate=0.896; c6_y_rate=0.872; per_seed_k_rate_min=0.848; per_seed_k_rate_max=0.991; per_seed_all_four_k=[0.636, 0.563, 0.965, 0.586, 0.661, 0.518]; all_six_all_four_k_independence=0.069; target_overlap_observations=53; target_overlap_k=50; target_overlap_y=46 |
| **c1_denominator_fragility** — With four target rows, the 0.95 C1 floor is effectively 100% preservation; one lost row gives 0.75. | rows_per_seed=4; c1_floor=0.95; max_losses_at_4=0; effective_floor_at_4=1.0; illustration_3_of_4=0.75 |
| **c1_denominator_expansion** — C4 plus the four target rows would raise the planned C1 denominator from four to 63-64 rows per seed, allowing 3 losses at 0.95; the observed denominator is still unmeasured. | planned_c1_rows_by_seed={'20630101': 64, '20630102': 63, '20630103': 64, '20630104': 64, '20630105': 64, '20630106': 63}; planned_non_target_rows_by_seed={'20630101': 60, '20630102': 59, '20630103': 60, '20630104': 60, '20630105': 60, '20630106': 59}; planned_min_rows=63; planned_max_rows=64; planned_total_rows=382; planned_non_target_total=358; allowed_losses_min=3; allowed_losses_max=3; max_losses_with_planned_c4={'20630101': 3, '20630102': 3, '20630103': 3, '20630104': 3, '20630105': 3, '20630106': 3}; status=UNMEASURED — no A1 cell has run; baseline_caveat=C1 counts only edges available in the paired A+K+ control, so the observed denominator will be at most 63-64. |
| **hard_edge_baseline** — A0's hard-edge prevalence is low, but a random 24-target sample has a material chance of containing one. | a0_hard_edges=26; a0_present_edges=672; hard_rate=0.0387; expected_hard_targets=0.93; prob_any_hard_independence=0.612 |

## What population A1 tests

**Estimand:** representative eligible pre-37 cycle-membership directed-edge population.

A1 tests a representative eligible-edge effect. It does not test an effect among high-propensity or anomalous edges; that would require a different selector and a new target set before freeze.

It is **not** a sample of high-U edges, hard edges, carrier-enriched anomalies.

## Freeze question

**Does a random eligible-edge design have enough expected measurable structure to justify freeze?**

**Answer: NO — NOT AS CURRENTLY EMITTED.** K and Y_ind prevalence are high enough that missing structure is not the blocker. The blocker is C1: four rows make the 0.95 floor a 100% rule, and the all-six all-four-K proxy is 6.9% under independence. C4 rows plus targets would raise the planned denominator to 63-64 per seed, but no cell has run, so the observed denominator is still unmeasured.

- If yes: Freeze the representative eligible-edge design after the manifest review.
- If no: Do not freeze; enlarge the C1 denominator with C4 rows or redesign the target block.

## Freeze readiness

**Status: OPEN. Can it move to PASS now? NO.**

C4 is a post-freeze void gate, so C1/C4 are no longer pre-freeze measurement blockers. The targets remain draft and the manifest remains unfrozen because no separate owner freeze act has been recorded; no grant or run exists.

**To reach PASS:**
- Freeze the representative target manifest in a separate owner act.
- Record the dated grant and run the planned cells.
- Assemble C1/C4; a failed C4 VOIDs the result.

## Gate order

**C4 decision: POST-FREEZE VOID GATE.** C4 is not a pre-freeze blocker. C1 and C4 are scored in the same post-freeze result assembly; a C4 failure VOIDs the run.

**Record:** [`A1-C4-GATE-ORDER.md`](A1-C4-GATE-ORDER.md).

## Freeze decision

**DO NOT FREEZE (2026-11-14).** Answer: **NO — NOT AS CURRENTLY EMITTED**.

**Scope:** the current six-seed target artifact and the current four-target A1 cell output.

**Are the target sets worth freezing?** **NO — HOLD AS DRAFT; TARGET FREEZE NOT AUTHORIZED.** The target sets are compliant and representative, but no separate target freeze has been performed. C4 is now a post-freeze VOID gate, so the C1/C4 measurement cannot be a pre-freeze condition. Do not regenerate targets unless Path B is chosen.

**Basis:**
- The C6 prevalence proxy is adequate: 602/672 K and 586/672 Y_ind.
- The C1 denominator is four target rows, so the 0.95 floor is a 100% rule (3/4 = 0.75); C4 would add 59-60 planned non-target rows per seed, bringing the planned C1 denominator to 63-64, but none has been observed.
- All six seeds having all four K rows is 6.9% under independence; the design is fragile, not merely underpowered.

**Revisit when:**
- The planned cells run with the C4 neighbour stream and C1/C4 are scored.
- A larger target block or a redesigned selector is registered before freeze.

## Decision

**FREEZE READINESS OPEN — C1 DENOMINATOR FRAGILITY**

P0 and feasibility pass, but four target rows per seed make the precommitted 0.95 C1 floor a 100% preservation rule. The prevalence proxy is adequate; the denominator is not. C4 non-target rows are implemented and, with the four target rows, would raise the planned denominator to 63-64 per seed, allowing 3 losses, but no cell has run. C1 remains unmeasured; do not freeze on the current target artifact.

### Next
- If Path A (representative eligible-edge effect) is retained: run the planned cells with the C4 neighbour stream and score C1/C4.
- If Path B (high-carrier-propensity effect) is required: redesign the selector and regenerate targets before freeze; that is a different experiment.
- Re-run this review after C1/C4 are measured; do not freeze before that.

**Not evidence:** A read-only power/prevalence review over different-seed C6 and A0 records. Its C1 expansion is a planned count from the A1 candidate counts, not an observed denominator. It runs no A1 cell, assigns no seed, freezes no target and establishes no causal, capability or transfer claim.
