# A1 Path A estimand and C1 acceptance rule — decision record

**ID:** `A1-PATH-A-C1-RULE-1`

**Date:** 2026-11-14

**Status:** `RECORDED — BINDING FOR A1; NO FREEZE, NO GRANT, NO RUN`

**Decision source:** owner direction, 2026-11-14.

**Current authority:** this record fixes the estimand and the C1 acceptance rule. The target freeze, the C1/C4 gate-order memo, the grant and the run remain separate and unrecorded.

## 1. Path A is the A1 estimand

A1 tests:

> the representative eligible pre-37 cycle-membership directed-edge effect.

The six existing target sets are the Path A draft. Path A does not regenerate them, and the C1 rule below does not depend on replacing them. Path B — the high-carrier-propensity, hard-edge or carrier-enriched effect — is not selected and would require a new selector, target artifact and registered design.

This record makes Path A the **A1 estimand**. It does not freeze the targets, reserve seeds or authorise the run.

## 2. C1 acceptance rule

C1 passes only when **all six seeds and both the `A−` and `K−` paths** satisfy the rule. There is no averaging across seeds or paths.

### 2.1 Unit and threshold

| Field | Rule |
| --- | --- |
| Unit | Observed minimum paired-control **available rows** across the six seeds and both paths |
| Preservation threshold | **0.95** |
| Minimum denominator | **60 rows** |
| Allowed losses at 60–64 | **3** |
| Planned range | 63–64 rows per seed |
| Missing denominator | Not zero; reported as missing and `C1_NO_DENOMINATOR` |
| Observed minimum below 60 | **`VOID — C1_DENOMINATOR_BELOW_FLOOR`** |

### 2.2 Decision table

| Observed minimum | Required retained at 0.95 | Allowed losses | Disposition |
| ---: | ---: | ---: | --- |
| 0 | — | — | `VOID — C1_NO_DENOMINATOR` |
| 1–19 | all available | 0 | `VOID — C1_DENOMINATOR_BELOW_FLOOR` |
| 20–59 | 1–2 fewer than available | 1–2 | `VOID — C1_DENOMINATOR_BELOW_FLOOR` |
| 60 | 57 | 3 | C1 may be read |
| 61 | 58 | 3 | C1 may be read |
| 62 | 59 | 3 | C1 may be read |
| 63 | 60 | 3 | C1 may be read |
| 64 | 61 | 3 | C1 may be read |
| >64 | n/a | n/a | `VOID — design inconsistency; score preplanned rows only` |

At 60–64 the pass condition is the usual **`retained / denominator >= 0.95`**, which is why 60 allows 57 retained and 64 requires 61. The number of allowed losses is exactly three; it is not a second threshold.

### 2.3 Below-floor disposition

If the observed minimum is **1–59**, the run is:

> **`VOID — C1_DENOMINATOR_BELOW_FLOOR`**

even when every available row is retained. A perfect **59/59** is still VOID. The fraction cannot rescue a denominator below the designed resolution.

If the observed minimum is **0**, the run is **`C1_NO_DENOMINATOR`**; a missing denominator is not a zero-row pass.

If the observed minimum is **above 64**, the run is **`VOID — design inconsistency`**. Score only the preplanned rows; do not add rows after the fact.

Under the proposed combined C1/C4 gate, the run-level status is **`A1 VOID — C1/C4`**, carrying the C1 reason code. The C1 rule itself is binding whether or not the combined gate memo is signed.

### 2.4 What VOID means here

`VOID — C1_DENOMINATOR_BELOW_FLOOR` means the experiment did not produce an admissible comparison:

- no causal model is selected and no M1 branch is assigned;
- no capability, transfer, V2, external-advantage or generalization claim may be read;
- C7/C8 are `NOT ADJUDICATED — RUN VOID`, not pass or fail;
- the run is not a negative result, null finding or failed replication;
- observed denominators are retained for audit; missing values are never reported as `0.0`;
- seeds and cells are consumed; no substitute seed, extra cell or post-hoc denominator expansion;
- no row is dropped, no threshold changed and no target re-selected;
- a second attempt requires a new registered design, fresh seeds and a new dated grant.

It is **not** `PARKED` (no run), `NOT IDENTIFIED` (a model result) or `UNSATISFIABLE` (the old unmeasurable-gate disposition).

## 3. What this record does not do

- It does not freeze the Path A targets or manifest.
- It does not sign the owner gate-order memo.
- It does not issue a grant, reserve seeds or run a cell.
- It does not observe C1 or C4.
- It does not classify C7/C8.
- It does not change the 0.95 C1 threshold or the 0.05 C4 ceiling.

The target-freeze act remains **DRAFT — AWAITING OWNER SIGNATURE**. The combined C1/C4 gate-order memo remains **DRAFT — AWAITING OWNER SIGNATURE**.

## 4. Current state

| Item | State |
| --- | --- |
| Path A estimand | **RECORDED** |
| Path B | **NOT SELECTED** |
| C1 acceptance rule | **RECORDED — BINDING FOR A1** |
| Minimum C1 denominator | **60** |
| Below-floor disposition | **`VOID — C1_DENOMINATOR_BELOW_FLOOR`** |
| Target sets | **DRAFT — NOT FROZEN** |
| Freeze decision | **DO NOT FREEZE (2026-11-14)** |
| Target freeze | **NOT AUTHORIZED** |
| Grant | **NOT ISSUED** |
| Run | **NOT STARTED** |
| Observed C1/C4 | **NONE** |

## 5. Checks

- `python -m benchmarks.a1_power_review --check`
- `python -m benchmarks.a1_gate_readiness --check`
- `python -m benchmarks.a1_target_selection --check`
- `python -m benchmarks.a1_two_path --check`

**Not evidence:** A recorded estimand and acceptance rule. It freezes nothing, grants nothing, runs no cell and makes no causal, capability or transfer claim.
