# A1 power and prevalence review

**Status:** `FREEZE READINESS OPEN — C1 DENOMINATOR FRAGILITY`

**This is not an A1 result.** No arm cell was run; no target was frozen.

| Finding | Evidence |
| --- | --- |
| **selection_is_random_on_u** — The 24 targets are statistically indistinguishable from the 358 unselected candidates on cycle-36 strength. | selected_n=24; unselected_n=358; selected_median=16.0; unselected_median=16.0; selected_mean=15.333; unselected_mean=15.215; permutation_p=0.91765 |
| **all_candidates_eligible** — Cycle membership and positive U do not narrow the candidate universe; every candidate is eligible. | candidate_counts={'20630101': 64, '20630102': 63, '20630103': 64, '20630104': 64, '20630105': 64, '20630106': 63}; eligible_counts={'20630101': 64, '20630102': 63, '20630103': 64, '20630104': 64, '20630105': 64, '20630106': 63} |
| **c6_prevalence_observation** — C6 reports high K/Y_ind prevalence in its own seed block. This is a different-world observation, not a C1 baseline-availability measurement and not a target-validation proxy. | c6_k=602; c6_world_edges=672; c6_y=586; c6_k_rate=0.896; c6_y_rate=0.872; per_seed_k_rate_min=0.848; per_seed_k_rate_max=0.991; per_seed_all_four_k=[0.636, 0.563, 0.965, 0.586, 0.661, 0.518]; all_six_all_four_k_independence=0.069; target_overlap_observations=53; target_overlap_k=50; target_overlap_y=46 |
| **c1_denominator_fragility** — With four target rows, the 0.95 C1 floor is effectively 100% preservation; one lost row gives 0.75. | rows_per_seed=4; c1_floor=0.95; max_losses_at_4=0; effective_floor_at_4=1.0; illustration_3_of_4=0.75 |
| **c1_denominator_expansion** — Even if every candidate edge were baseline-available, C4 plus the four target rows would produce at most 63-64 C1 rows per seed. This is an upper bound, not an observed or estimated denominator; unavailable rows reduce it and can push the run below the 60-row floor. | planned_c1_rows_by_seed={'20630101': 64, '20630102': 63, '20630103': 64, '20630104': 64, '20630105': 64, '20630106': 63}; planned_non_target_rows_by_seed={'20630101': 60, '20630102': 59, '20630103': 60, '20630104': 60, '20630105': 60, '20630106': 59}; planned_min_rows=63; planned_max_rows=64; planned_total_rows=382; planned_non_target_total=358; allowed_losses_min=3; allowed_losses_max=3; max_losses_with_planned_c4={'20630101': 3, '20630102': 3, '20630103': 3, '20630104': 3, '20630105': 3, '20630106': 3}; status=UNMEASURED — no A1 cell has run; denominator_kind=UPPER BOUND — NOT AN OBSERVED OR ESTIMATED BASELINE-AVAILABILITY DENOMINATOR; observed_baseline_available_rows=None; floor=60; below_floor_disposition=VOID — C1_DENOMINATOR_BELOW_FLOOR; baseline_caveat=C1 counts only edges available in the paired A+K+ control. The 63-64 figure assumes every candidate edge is available; the actual denominator can be lower and may fall below the 60-row floor. No baseline-availability estimate exists. |
| **hard_edge_baseline** — A0's hard-edge prevalence is low, but a random 24-target sample has a material chance of containing one. | a0_hard_edges=26; a0_present_edges=672; hard_rate=0.0387; expected_hard_targets=0.93; prob_any_hard_independence=0.612 |

## C1 denominator-feasibility risk note

**Status:** `RISK RECORDED — UNMEASURED; 63-64 IS AN UPPER BOUND`

The planned **63–64** C1 rows are an **upper bound**, not an observed or estimated denominator. They equal the candidate-universe counts and assume every candidate edge is available in the paired A+K+ control. C1 counts only baseline-available rows; the observed denominator can be lower, and if the minimum falls below **60** on any seed or path, the run is **VOID — C1_DENOMINATOR_BELOW_FLOOR** before any model is read.

**Unrelated percentages are not baseline-availability proxies.** C6's K/Y_ind rates and A0's hard-edge rate come from different seed blocks, worlds and quantities; they must not be used to estimate, bound or certify the C1 denominator.

**Per-seed availability budget.** The floor is **60** rows. `max_unavailable_rows` is the number of candidate rows that can be baseline-unavailable before the seed's denominator falls below the floor; this is arithmetic on the upper bound, not an observed rate. It is separate from the three-loss retention allowance, which applies after the observed denominator is formed.

| Seed | Candidate rows | Max unavailable | Required availability |
| ---: | ---: | ---: | ---: |
| 20630101 | 64 | 4 | 93.75% |
| 20630102 | 63 | 3 | 95.24% |
| 20630103 | 64 | 4 | 93.75% |
| 20630104 | 64 | 4 | 93.75% |
| 20630105 | 64 | 4 | 93.75% |
| 20630106 | 63 | 3 | 95.24% |

**Risk disposition:** `RISK RECORDED — UNMEASURED; 63-64 IS AN UPPER BOUND`; no baseline-availability denominator has been measured.


## C1 power curve

At a true retention of 0.95, the 63-row upper-bound scenario gives a 61.3% chance for one arm, 37.6% for both arms on one seed, and 0.3% across all six seeds. At 0.98, the corresponding all-six chance is 63.2%. A denominator of 20 is the smallest listed value that can still pass with one lost row.

**Model:** Independent Bernoulli retention on each row; the stated retention rate q is common to A- and K-; a seed passes only when both arms meet 0.95; all-six assumes independent seeds. The separate correlation_sensitivity block relaxes the path and seed independence.

The denominators below are scenario sizes, not observed baseline-available counts; the 63–64 scenarios are the C4 upper bound recorded in the risk note above.

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

**C1 power-design criterion:** the C1 design is sized for **80%** all-six-seed power at the **upper-bound 63-row** scenario. Under the independent model this requires a common retention of **q=0.984017**; at 64 rows it is **q=0.984271**, and at the 60-row floor **q=0.983204**. This is a design criterion for the planned design, not an observed retention rate and not a second acceptance gate; the 0.95 preservation rule above remains the observed-run acceptance rule.


### Correlation sensitivity

**Model:** Gaussian copulas on the pass/fail indicators. Within a seed, the A- and K- pass indicators have correlation rho_paths; across seeds, the per-seed pass indicators have equicorrelation rho_seeds through one shared factor. Per-arm marginals remain the independent Bernoulli probabilities. The copulas are applied sequentially; no path-specific cross-seed correlation is added beyond the seed factor.

The correlation values are sensitivity settings, not estimates from A1. The independent curve above is the baseline; a positive correlation raises joint pass probabilities relative to the product of marginals.

**At n=63, q=.95:** independent paths and seeds give per-seed **0.375577** and all-six **0.002807**. Path correlation `.5` gives per-seed **0.453562**; seed correlation `.5` gives all-six **0.073188**; both at `.5` give all-six **0.113341**.

| Scenario at n=63, q=.95 | Per-seed | All-six |
| --- | ---: | ---: |
| independent | 0.375577 | 0.002807 |
| A/K path rho=.5 | 0.453562 | 0.008706 |
| seed rho=.5 | 0.375577 | 0.073188 |
| both rho=.5 | 0.453562 | 0.113341 |

**Path correlation at n=63, q=.95** (all-six assumes independent seeds):

| rho_paths | Per-seed | All-six |
| ---: | ---: | ---: |
| 0.00 | 0.375577 | 0.002807 |
| 0.25 | 0.412949 | 0.004959 |
| 0.50 | 0.453562 | 0.008706 |
| 0.75 | 0.502658 | 0.016130 |
| 0.95 | 0.564355 | 0.032308 |

**Seed correlation at n=63, q=.95** (independent paths):

| rho_seeds | Per-seed | All-six |
| ---: | ---: | ---: |
| 0.00 | 0.375577 | 0.002807 |
| 0.25 | 0.375577 | 0.025715 |
| 0.50 | 0.375577 | 0.073188 |
| 0.75 | 0.375577 | 0.151694 |
| 0.95 | 0.375577 | 0.271151 |

**Joint correlation at n=63:**

| q | rho_paths | rho_seeds | Per-seed | All-six |
| ---: | ---: | ---: | ---: | ---: |
| 0.95 | 0.50 | 0.50 | 0.453562 | 0.113341 |
| 0.95 | 0.75 | 0.75 | 0.502658 | 0.249079 |
| 0.95 | 0.95 | 0.95 | 0.564355 | 0.451062 |

At n=63 and q=.95, independent paths and independent seeds give a per-seed pass probability of 0.375577 and an all-six probability of 0.002807. A path correlation of .5 raises the per-seed probability to 0.453562; a seed correlation of .5 raises the all-six probability to 0.073188; both at .5 give 0.113341. Positive correlation makes the six seeds share their fate: all-six can rise while the chance that none pass also rises. These are sensitivity scenarios, not correlation estimates.

The `q=.98` rows are retained in the artifact. Positive seed correlation raises all-six more than the independent product because the seeds share a fate; it also raises the chance that none pass. That is a property of the sensitivity model, not evidence that the seeds are correlated.

### C1 denominator floor

**Status: ADOPTED — BINDING FOR A1.** **Record:** [`DECISION-A1-PATH-A-C1-RULE.md`](DECISION-A1-PATH-A-C1-RULE.md). **Adopted together with the C1/C4 VOID gate:** [`A1-C1-C4-VOID-GATE.md`](A1-C1-C4-VOID-GATE.md).

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

A perfect 59/59 is still VOID: the fraction cannot rescue a denominator below the resolution floor.

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

**Answer: NO — NOT AS CURRENTLY EMITTED.** C6 prevalence is a different-seed observation, not C1 baseline availability. The blocker is C1: four rows make the 0.95 floor a 100% rule. The 63-64 C4 expansion is an upper bound from candidate counts, not an estimate; the observed denominator can be lower and may fail the 60-row floor. No cell has run.

- If yes: Freeze the representative eligible-edge design after the manifest review.
- If no: Do not freeze until the post-freeze C1/C4 order and the separate target-freeze act are recorded; do not require a pre-freeze C1/C4 denominator.

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

**Provisional-freeze draft:** [docs/A1-PROVISIONAL-FREEZE-GATE-ORDER.md](A1-PROVISIONAL-FREEZE-GATE-ORDER.md) — **DRAFT — PROVISIONAL FREEZE ONLY**. Would provisionally freeze the Path A targets; the C1/C4 VOID gate is already adopted separately. No freeze is recorded until the owner adopts the wrapper.

**Owner memo draft:** [docs/DECISION-A1-PATH-A-C1-C4.md](DECISION-A1-PATH-A-C1-C4.md) — **DRAFT — C1/C4 GATE ADOPTED ELSEWHERE**. Remains draft for the remaining Path A confirmation and provisional freeze; the C1/C4 gate and 60-row floor are adopted separately. It does not freeze, grant or authorise.

**Target-freeze act draft:** [docs/A1-TARGET-FREEZE-ACT.md](A1-TARGET-FREEZE-ACT.md) — **DRAFT — AWAITING OWNER SIGNATURE; NOT FROZEN**. Prepares the separate act that would freeze the six Path A target sets and the manifest/seed block; no grant or run is included.

**Are the target sets worth freezing?** **NO — HOLD AS DRAFT; TARGET FREEZE NOT AUTHORIZED.** The Path A target sets are compliant and representative, but no separate target freeze has been performed. C4 is now a post-freeze VOID gate, so the C1/C4 measurement cannot be a pre-freeze condition. Path B is not selected and would require a new selector and target artifact.

**Basis:**
- C6's 602/672 K and 586/672 Y_ind rates are observations from a different seed block and are not baseline-availability proxies. They do not establish C1 feasibility.
- The C1 denominator is four target rows, so the 0.95 floor is a 100% rule (3/4 = 0.75). C4 would add at most 59-60 non-target rows per seed, giving an upper bound of 63-64 C1 rows; the observed denominator can be lower and may fall below the 60-row floor.
- All six seeds having all four K rows is 6.9% under independence; the design is fragile, not merely underpowered.

**Revisit when:**
- The planned cells run with the C4 neighbour stream and C1/C4 are scored.
- A larger target block or a redesigned selector is registered before freeze.

## Decision

**FREEZE READINESS OPEN — C1 DENOMINATOR FRAGILITY**

P0 and feasibility pass, but four target rows per seed make the precommitted 0.95 C1 floor a 100% preservation rule. C6's K/Y_ind prevalence is a different-seed observation and does not establish C1 baseline availability. The 63-64 C1 figure is an upper bound, not an estimate; the observed denominator can be lower and may fail the 60-row floor. C1 remains unmeasured; do not freeze on the current target artifact.

### Next
- Path A is recorded: after target freeze and a dated grant, run the planned cells with the C4 neighbour stream and score C1/C4.
- Path B is not selected; it would require a new selector, target artifact and registered design, not a regeneration of the Path A targets.
- The C1 acceptance rule is recorded; the target freeze remains a separate act.
- Record the C1/C4 gate order and the separate target freeze before a grant; C1/C4 are measured only after the run.

**Not evidence:** A read-only power/prevalence review over different-seed C6 and A0 records. Its 63-64 C1 expansion is an upper bound derived from A1 candidate counts, not an observed or estimated baseline-availability denominator; C6 and A0 percentages are not C1 proxies. It runs no A1 cell, assigns no seed, freezes no target and establishes no causal, capability or transfer claim.
