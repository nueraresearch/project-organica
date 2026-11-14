# A1 pre-freeze checklist

**ID:** `A1-PRE-FREEZE-CHECKLIST-1`  
**Date:** 2026-11-14  
**Status:** `P0 PASS — FREEZE READINESS OPEN (PASS: NO); TARGET FREEZE NOT AUTHORISED; RUN NOT AUTHORISED`

**Formal compliance record:** [`A1-PROTOCOL-COMPLIANCE-REPORT.md`](A1-PROTOCOL-COMPLIANCE-REPORT.md). Power/prevalence evidence: [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md).

**This is a compliance record, not a target freeze, a grant or a result.** The six
target sets are a feasibility artifact. They are not fixed experimental targets
until the manifest is frozen by a separate act.

## Must pass before freeze

| Check | Result | Evidence |
| --- | --- | --- |
| Cycle-36 `U` sampled before the sleep call | **PASS** | `a1_arms.run_cell`; `tests/test_a1_prefreeze.py::test_cycle_36_u_is_sampled_before_consolidation`; [audit](A1-ADVERSARIAL-AUDIT.md) P0 |
| Candidate universe restricted to the first 36 acquisition cycles | **PASS** | [selection implementation](../benchmarks/a1_target_selection.py); P0 pre-37 check |
| Future-blindness: 36-cycle vs 120-cycle world | **PASS** | [audit](A1-ADVERSARIAL-AUDIT.md) |
| Report-blindness | **PASS** | [audit](A1-ADVERSARIAL-AUDIT.md) |
| Sleep-blindness | **PASS** | [audit](A1-ADVERSARIAL-AUDIT.md) |
| Determinism | **PASS** | [audit](A1-ADVERSARIAL-AUDIT.md) |
| Six-seed feasibility: four disjoint targets per seed | **PASS** | [selection artifact](a1_target_selection.json); [audit](A1-ADVERSARIAL-AUDIT.md) |
| Selection artifact generated | **PASS** | [artifact](a1_target_selection.json); 24 selected edges |
| Selection digest stable | **PASS** | `selection_digest` checked against contents; independent determinism pass in the audit |

The audit's P0 block records all six protocol-compliance conditions as passing, and the audit now records the selection-representativeness measurement beside them.

## Selection representativeness

**Measurement (2026-11-14).**

| Measurement | Result |
| --- | ---: |
| Selected target observations | **24** |
| Unique target edges | **23** |
| Unselected candidates | **358** |
| Candidates | **382** |
| All candidates eligible | **yes** |
| Selected mean strength | **15.333** |
| Unselected mean strength | **15.215** |
| Selected median strength | **16** |
| Unselected median strength | **16** |
| Descriptive permutation p | **0.918** |

**Estimand:** a **representative eligible pre-37 cycle-membership directed-edge population**.

**Conclusion:** the selected targets are a representative eligible pre-37 sample; A1 does not estimate a high-`U`, hard-edge or carrier-enriched effect. The permutation p-value is descriptive; failure to reject a difference is not an equivalence test. The design fact is that every candidate is eligible and the hash order ignores `U`.

If a high-propensity estimand is required, the selector must be redesigned before freeze. This is a design statement, not a result and not a P0 condition.
`a1_target_selection --check` and `a1_adversarial_audit --check` are the
machine checks for the artifact and its page.

## Not yet complete

| Item | State | Consequence |
| --- | --- | --- |
| Power/prevalence review for `N = 4` | **DONE — FREEZE READINESS OPEN** | [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md) finds C1 denominator fragility: four target rows make the 0.95 floor effectively 100%. |
| C4 non-target neighbour rows | **IMPLEMENTED — NOT RUN** | A1 cell output now emits `neighbor_rows` for every non-target edge, with A/K/Y availability rates; `attach_neighbor_deltas` joins them to the seed’s A+K+ control, and `c1_rows` includes baseline-available non-target edges in the C1 denominator. No cell has run, so C4 is not cleared and C1/C4 are not measured. |
| Freeze decision | **DO NOT FREEZE (2026-11-14)** | The dated record in [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md) answers the freeze question **NO — NOT AS CURRENTLY EMITTED**; this is not an owner grant. |
| Freeze readiness PASS? | **NO — OPEN** | The C1 floor is effectively 100% at four target rows; C4 rows are instrumented but no cell has run. The review records `can_move_now: false`; C1/C4 must be measured before this can become PASS. |
| Target sets worth freezing? | **NO — HOLD AS DRAFT UNTIL C1/C4 ARE MEASURED** | The selected edges are compliant and representative and C4 rows are instrumented, but no cell has run; the C1/C4 denominators remain unmeasured. Regenerate targets only if Path B is chosen. |
| Manifest freeze | **NOT DONE** | The target block remains `UNRESOLVED`; `a1_two_path --check` still refuses. |
| Dated owner grant | **NOT DONE** | No cell may open a database. |

## What the evidence does and does not mean

It means the selector can produce four disjoint targets for all six provisional
seeds from information available before acquisition cycle 37, and that the
implementation passes the blindness and determinism checks recorded in the audit.
It does **not** validate target selection as a scientific result, establish power,
clear C4, freeze the targets or authorise a run.

**Not evidence:** A compliance gate and a feasibility artifact. No A1 cell has
run; no target is frozen; no seed is reserved; no result exists.
