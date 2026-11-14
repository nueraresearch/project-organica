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

## C1 power curve

At a true retention of 0.95, the 63-row denominator gives a 61.3% chance for one arm, 37.6% for both arms on one seed, and 0.3% across all six seeds. At 0.98, the corresponding all-six chance is 63.2%. A denominator of 20 is the smallest listed value that can still pass with one lost row.

**Model:** Independent Bernoulli retention on each row; the stated retention rate q is common to A- and K-; a seed passes only when both arms meet 0.95; all-six assumes independent seeds.

**Retention rate assumption:** each column names the assumed `q`; these are reference probabilities, not A1 measurements.

| Denominator | Required | Allowed losses | q=.95 arm | q=.95 seed | q=.95 all six | q=.98 arm | q=.98 seed | q=.98 all six |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 4 | 0 | 0.814506 | 0.663420 | 0.085258 | 0.922368 | 0.850763 | 0.379185 |
| 20 | 19 | 1 | 0.735840 | 0.541460 | 0.025200 | 0.940101 | 0.883790 | 0.476534 |
| 56 | 54 | 2 | 0.464557 | 0.215814 | 0.000101 | 0.898193 | 0.806750 | 0.275698 |
| 59 | 57 | 2 | 0.428928 | 0.183979 | 0.000039 | 0.885585 | 0.784261 | 0.232683 |
| 60 | 57 | 3 | 0.647281 | 0.418973 | 0.005409 | 0.967806 | 0.936648 | 0.675241 |
| 63 | 60 | 3 | 0.612844 | 0.375577 | 0.002807 | 0.962453 | 0.926317 | 0.631767 |
| 64 | 61 | 3 | 0.601409 | 0.361693 | 0.002239 | 0.960563 | 0.922681 | 0.617035 |

The curve also records `q=.97` and `q=1.00` in the artifact. The `all six` columns are the product of six independent per-seed probabilities, because C1 must pass on every seed.

At `.95` and 63 rows, one arm passes with probability **0.612844**, both arms on one seed with **0.375577**, and all six seeds with **0.002807**. At `.98`, the all-six probability is **0.631767**. The target-only four-row fallback is the first row; 20 rows is the smallest listed denominator that can still pass with one loss.


### Denominator impact at q=.95

The `all six` column is the probability that C1 passes on every seed under the stated independent-retention model. `Change` is relative to the previous listed denominator, not an empirical effect.

| Denominator | Required | Allowed losses | Effective floor | q=.95 all six | Change |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 4 | 0 | 1.0000 | 0.085258 | — |
| 20 | 19 | 1 | 0.9500 | 0.025200 | -0.060058 |
| 56 | 54 | 2 | 0.9643 | 0.000101 | -0.025099 |
| 59 | 57 | 2 | 0.9661 | 0.000039 | -0.000062 |
| 60 | 57 | 3 | 0.9500 | 0.005409 | +0.005370 |
| 63 | 60 | 3 | 0.9524 | 0.002807 | -0.002602 |
| 64 | 61 | 3 | 0.9531 | 0.002239 | -0.000568 |

### The 60-row cliff

At 59 rows, 57/59 = 0.9661 and only two losses pass; at 60 rows, 57/60 = 0.95 and three losses pass. The extra row crosses a loss boundary in the gate arithmetic, not an empirical effect.

At `q=.95`, the all-six probability moves from **0.000039** at 59 rows to **0.005409** at 60 rows, a **138.69x** step. This is a loss-boundary effect: the extra row is not a new measurement, and the cliff is not evidence that 60 rows are scientifically special.

### Required retention for all-six power

Each cell is the assumed `q` needed for the stated all-six-seed power under the same independent model. These are scenarios, not observed retention rates.

| Target all-six | n=4 | n=20 | n=56 | n=59 | n=60 | n=63 | n=64 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50% | 0.985663 | 0.980723 | 0.984518 | 0.985313 | 0.975996 | 0.977154 | 0.977515 |
| 80% | 0.995362 | 0.989516 | 0.990057 | 0.990569 | 0.983204 | 0.984017 | 0.984271 |
| 90% | 0.997807 | 0.992924 | 0.992486 | 0.992874 | 0.986566 | 0.987217 | 0.987420 |
| 95% | 0.998932 | 0.995121 | 0.994217 | 0.994515 | 0.989079 | 0.989609 | 0.989775 |

The required-retention table makes the cost explicit: at 63 rows, 80% all-six power needs `q=0.984017`; 50% needs `q=0.977154`. The target-only four-row design needs a still higher rate for the same power because it allows no losses.


### Proposed C1 denominator floor

**Status: PROPOSED — NOT ADOPTED.** This is the pre-run rule the project still needs; it is not adopted by this review.

**Floor:** 60 paired-control available rows, measured as the minimum across all six seeds and both `A−` and `K−` paths. The planned range is 63–64.

If the observed minimum is below 60 on any seed or path, the A1 run is VOID — C1_DENOMINATOR_BELOW_FLOOR, before any model is read.

At 59 rows, 57/59 = 0.9661 and only two losses pass; at 60 rows, 57/60 = 0.95 and three losses pass. 60 is the first denominator with the planned three-loss tolerance.

| Observed minimum | Allowed losses | Disposition |
| ---: | ---: | --- |
| 0 | 0 | VOID — C1_NO_DENOMINATOR |
| 1–19 | 0 | VOID — C1_DENOMINATOR_BELOW_FLOOR |
| 20–59 | 1–2 | VOID — C1_DENOMINATOR_BELOW_FLOOR |
| 60–64 | 3 | C1 gate may be read |
| >64 | n/a | VOID — design inconsistency |

A perfect 59/59 is still VOID: the fraction cannot rescue a denominator below the proposed resolution floor.

PARKED is for a missing target set or grant. This is an executed run whose planned resolution was not reached, so it is VOID.

No model verdict is read. VOID is not NOT IDENTIFIED.

Below 20 rows even one loss fails; the denominator is too small to express the 0.95 criterion and the same VOID applies.

A denominator above 64 is a design inconsistency: score only the preplanned rows and do not add rows after the fact.


## What population A1 tests

**Estimand:** representative eligible pre-37 cycle-membership directed-edge population.

A1 tests a representative eligible-edge effect. It does not test an effect among high-propensity or anomalous edges; that would require a different selector and a new target set before freeze.

It is **not** a sample of high-U edges, hard edges, carrier-enriched anomalies.

## Path selection

**Path A — recorded (2026-11-14).** The selected estimand is the representative eligible pre-37 cycle-membership directed-edge effect.

**Protocol:** [`A1-TARGET-SELECTION-PROTOCOL.md`](A1-TARGET-SELECTION-PROTOCOL.md). **Status:** RECORDED — PROTOCOL SELECTED; TARGET SETS STILL DRAFT.

**Target sets:** DRAFT — NOT FROZEN. Path A selects the estimand; it does not freeze the manifest, reserve a seed, issue a grant or authorise a cell.

**Path B:** High-carrier-propensity, hard-edge or carrier-enriched effect; requires a new selector, target artifact and registered design. It is not selected and is not a continuation of this protocol.

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

**Path:** A — RECORDED — TARGET SETS STILL DRAFT. Record: [`A1-TARGET-SELECTION-PROTOCOL.md`](A1-TARGET-SELECTION-PROTOCOL.md).

**Path effect:** The current six target sets are the Path A draft. Selecting Path A does not freeze the manifest, reserve a seed, issue a grant or authorise a cell.

**Provisional-freeze draft:** [docs/A1-PROVISIONAL-FREEZE-GATE-ORDER.md](A1-PROVISIONAL-FREEZE-GATE-ORDER.md) — **DRAFT — NOT DECIDED**. Would provisionally freeze the Path A targets and make C1/C4 a post-freeze VOID gate; no freeze is recorded until the owner adopts it.

**Are the target sets worth freezing?** **NO — HOLD AS DRAFT; TARGET FREEZE NOT AUTHORIZED.** The Path A target sets are compliant and representative, but no separate target freeze has been performed. C4 is now a post-freeze VOID gate, so the C1/C4 measurement cannot be a pre-freeze condition. Path B is not selected and would require a new selector and target artifact.

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
- Path A is recorded: after target freeze and a dated grant, run the planned cells with the C4 neighbour stream and score C1/C4.
- Path B is not selected; it would require a new selector, target artifact and registered design, not a regeneration of the Path A targets.
- Adopt or reject the proposed 60-row C1 denominator floor before target freeze.
- Re-run this review after C1/C4 are measured; do not freeze before that.

**Not evidence:** A read-only power/prevalence review over different-seed C6 and A0 records. Its C1 expansion is a planned count from the A1 candidate counts, not an observed denominator. It runs no A1 cell, assigns no seed, freezes no target and establishes no causal, capability or transfer claim.
