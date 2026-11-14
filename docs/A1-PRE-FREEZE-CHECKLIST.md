# A1 pre-freeze checklist

**ID:** `A1-PRE-FREEZE-CHECKLIST-1`  
**Date:** 2026-11-14  
**Status:** `P0 PASS — TARGET FREEZE NOT AUTHORISED; RUN NOT AUTHORISED`

**Formal compliance record:** [`A1-PROTOCOL-COMPLIANCE-REPORT.md`](A1-PROTOCOL-COMPLIANCE-REPORT.md).

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

The audit's P0 block records all six protocol-compliance conditions as passing.
`a1_target_selection --check` and `a1_adversarial_audit --check` are the
machine checks for the artifact and its page.

## Not yet complete

| Item | State | Consequence |
| --- | --- | --- |
| Power/prevalence review for `N = 4` | **NOT DONE** | The target sets must not be frozen before this review. |
| C4 non-target neighbour rows | **NOT DONE** | A1 cell output emits target rows only; C4 is not cleared and must not be claimed. |
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
