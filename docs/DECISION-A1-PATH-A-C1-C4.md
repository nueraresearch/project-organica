# Owner decision memo — A1 Path A and C1/C4 gate order

**ID:** `A1-OWNER-DECISION-1`

**Date:** 2026-11-14

**Status:** `DRAFT — C1/C4 GATE ADOPTED ELSEWHERE; PATH A CONFIRMATION AND PROVISIONAL FREEZE NOT ADOPTED`

**Decision owner:** ____________________

**Signature and date:** ____________________

**This is a draft memo for the remaining Path A confirmation and provisional-freeze decisions.** The C1/C4 ordering below was adopted separately on 2026-11-14 in [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md), together with the 60-row denominator floor. This memo does not re-adopt that gate and does not itself freeze targets, reserve seeds, issue a grant, run a cell or create evidence.

## 1. Decisions for the owner

| # | Decision | Proposed record |
| --- | --- | --- |
| 1 | **Path A is the A1 estimand.** A1 tests the representative eligible pre-37 cycle-membership directed-edge effect. Path B is a separate future experiment. | Recorded in the target-selection protocol; confirmed here. |
| 2 | **C1/C4 are post-freeze validity gates, not pre-freeze admissibility gates.** The freeze, grant and run come first; C1/C4 then decide whether the executed comparison is admissible. | **Adopted separately** in [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md). |
| 3 | **The gate order is freeze → grant → run → measure C1/C4 → PASS or VOID.** | **Adopted separately** in [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md). |
| 4 | **“Provisional freeze” describes the result's evidentiary status, not revocable target identity.** The targets are fixed before outcomes; a VOID does not unfreeze them, permit re-selection or license a retry. | Still draft; not adopted. |
| 5 | **A C1/C4 failure or unmeasurability makes the run `A1 VOID — C1/C4`.** No model is read. | **Adopted separately** in [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md). |

This memo does **not** perform decision 3's freeze. It records the ordering. A separate dated owner act must freeze the Path A targets and manifest target block.

## 2. Path A decision

A1 tests:

> the representative eligible pre-37 cycle-membership directed-edge effect.

The selector is outcome-blind and has already produced the six draft target sets. Path A uses those targets; it does not regenerate them. The current target sets remain **DRAFT — NOT FROZEN** until a separate freeze act.

Path B — the high-carrier-propensity, hard-edge or carrier-enriched effect — is **not selected**. It would require a new selector, a new target artifact and a new registered design. It is not a continuation of A1 Path A and cannot be reached by re-labelling the current targets after an outcome.

Recording Path A does not by itself establish that the targets are worth freezing, that the C1 denominator is adequate, or that C1/C4 will pass. Those are separate questions.

## 3. C1/C4 ordering decision

**Decision: C1 and C4 are post-freeze validity gates. They are not pre-freeze admissibility gates.**

Neither C1 nor C4 is a property of the target set:

- C1 needs executed `A−` and `K−` cells and a paired-control denominator.
- C4 needs executed edge-level interventions and non-target neighbour rows.

A pre-freeze C1/C4 requirement therefore forces one of three bad orders:

| Alternative | Defect |
| --- | --- |
| Freeze first, then measure C1/C4, then freeze again | Circular: the second freeze is conditioned on data the first freeze was supposed to make possible. |
| Run an unregistered diagnostic first | Outcome leakage: the observed denominator can influence what becomes frozen. |
| Assume the planned denominator and freeze on it | Weak measurement: the freeze claim is not the observed denominator, and the actual denominator can still invalidate the run. |

Post-freeze validity avoids all three:

- the targets are fixed before outcomes are seen;
- C1/C4 are observed only after the planned cells run;
- passing makes the comparison admissible;
- failing or being unmeasurable makes it VOID, without changing the targets;
- no model is read before the validity decision.

This is why the circularity is not a defect in the experiment. It is a defect in a gate order that puts validity before the freeze. The freeze fixes **what is tested**; C1/C4 decide **whether the test is admissible**.

## 4. Gate order

```text
P0 compliance and target feasibility
        ↓
Path A estimand recorded
        ↓
separate provisional target freeze
        ↓
separate dated grant
        ↓
planned A1 cells run
        ↓
assemble C1 + C4 from actual parts
        ↓
both pass ──► read C7/C8 and the remaining gates
either fails or is unmeasurable ──► A1 VOID — C1/C4
```

C4 already has this post-freeze VOID status. This memo extends the same ordering to C1 and makes C1/C4 one validity decision. The C1 threshold remains **0.95** preservation; the C4 threshold remains a **0.05** absolute neighbour-delta ceiling. No threshold changes.

## 5. What “provisional freeze” means

The freeze is provisional in its **evidentiary status**, not in its **target identity**.

- Before the grant, the owner fixes the Path A targets and manifest target block against the selection artifact.
- C1/C4 are not preconditions of that freeze.
- The run's result is provisional until C1/C4 pass.
- A C1/C4 failure makes the run VOID; it does not unfreeze the targets.
- The target identity is not revocable after outcomes are seen.
- “Provisional” is not a licence to retry, re-select, add a cell or substitute a seed.

A freeze that could be undone after a C1/C4 failure would make target selection outcome-dependent. That is the failure the pre-outcome protocol exists to prevent.

This memo does not reserve seeds. Seed reservation and the grant remain separate acts.

## 6. C1/C4 VOID conditions

| Gate | Condition | Reason code |
| --- | --- | --- |
| C1 | No paired-control denominator is available for a required seed or required row. A missing denominator is not zero. | `C1_NO_DENOMINATOR` |
| C1 | The observed minimum paired-control denominator is below **60** on any seed or path, even if every available row is retained. The 60-row floor is recorded in [`DECISION-A1-PATH-A-C1-RULE.md`](DECISION-A1-PATH-A-C1-RULE.md). | `C1_DENOMINATOR_BELOW_FLOOR` |
| C1 | On any seed, `A−` carrier preservation is below 0.95, or `K−` served preservation is below 0.95. | `C1_THRESHOLD` |
| C4 | The non-target stream is absent, incomplete, or has no measurable paired delta. | `C4_UNMEASURABLE` |
| C4 | Any measurable non-target A, K or Y neighbour delta exceeds 0.05. | `C4_DELTA` |
| Assembly | Required cell parts are missing, duplicated, or cannot be paired for C1/C4. The gate is unmeasurable; it is not a zero-row pass. | `C1_C4_INCOMPLETE` |

A run with any one of these conditions is **`A1 VOID — C1/C4`**. If both gates fail, both reason codes are recorded; one gate cannot be suppressed by the other.

**Denominator floor.** The 60-row floor is **ADOPTED — BINDING FOR A1** together with the C1/C4 gate in [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md). A perfect 59/59 is VOID; the fraction cannot rescue a denominator below 60.

## 7. What a VOID run means

A VOID run means the experiment **did not produce an admissible comparison**. It does not mean the carrier model is false, the two-path model is false, or the intervention had no effect.

For a VOID run:

- The recorded status is **`A1 VOID — C1/C4`**, with the failing gate or gates and the reason code.
- No causal model is selected: no `M-K`, `M-N`, `M-S` or `M-R` label.
- No M1 branch is assigned, and no V2, capability, transfer, external-advantage or generalization claim may be read.
- C7 and C8 are **not adjudicated**. If they were not evaluated before the VOID, they are reported as `NOT ADJUDICATED — RUN VOID`, not as pass or fail.
- The run is **not a negative result**. It is not evidence for or against any model, and it may not be reported as a null finding or a failed replication.
- The observed C1 denominators and C4 row counts are retained for audit, even when the gate fails. A missing denominator is reported as missing, never as `0.0`.
- The planned seeds and cells are consumed. No substitute seed, extra cell or post-hoc target may be added.
- No row may be dropped, no threshold changed, no target re-selected and no denominator expanded after the failure is seen.
- The parts and observed counts are preserved. They may support instrument diagnostics, but may not be re-labelled as an A1 result.
- The target freeze remains recorded. A VOID does not return the attempt to an unfrozen state or authorise a second attempt under the same registration.

## 8. What a VOID run does not mean

A VOID run does **not**:

- establish that C1 or C4 can never pass;
- establish that the two-path model is untestable in principle;
- license a new selector, a new target count or a new threshold under the same registration;
- convert a failed C1 into a C4 problem or a failed C4 into a C1 problem;
- permit re-reading a failed run as “near pass” or “descriptively supportive”;
- authorise a second attempt. A further attempt requires a **new registered design**, a fresh seed block and a new dated owner grant.

A **pass** is also not a model verdict. C1/C4 passing means only that the comparison is admissible; C2, C3, C5, C7, C8 and C9 still decide whether a model may be read.

## 9. VOID is not PARKED, NOT IDENTIFIED or UNSATISFIABLE

| Status | When it applies | What it records |
| --- | --- | --- |
| `A1 PARKED — …` | The run did not execute: missing target set, missing rule, or no grant. | A preparation or authorisation stop, not an experimental outcome. |
| `A1 VOID — C1/C4` | The planned run executed but the C1/C4 validity test failed or was unmeasurable. | No admissible comparison; no model read. |
| `NOT IDENTIFIED` | The current C1 result-gate failure when the comparison exists but model separation is not achieved. | A scientific result-gate outcome under the current disposition. |
| `UNSATISFIABLE` | The current disposition for a gate that cannot be measured under the registered design. | A design/measurement limit under the current disposition. |

Because C1/C4 has been adopted separately, C1 failure and unmeasurability are already **VOID**; C4 already uses VOID. This memo does not re-adopt them, and the one-attempt rule is unchanged.

## 10. No rescue rule

- A passing C4 cannot rescue a failing C1.
- A passing C1 cannot rescue a failing C4.
- A passing C2, C3, C5, C7 or C8 cannot rescue a C1/C4 VOID.
- A larger observed denominator discovered after the run cannot be used to re-score C1. The C4 non-target rows must be part of the registered design.
- A failed or unmeasurable gate is terminal for this registration. The one-attempt rule in [`A1-GATE-READINESS.md`](A1-GATE-READINESS.md) applies unchanged.

## 11. Effect of signing

Signing and dating this memo would record the remaining Path A confirmation and provisional-freeze decisions. It would not re-adopt the C1/C4 gate, change the 60-row floor, freeze targets, reserve seeds, issue the grant, run a cell or create evidence. The target freeze, grant and run remain separate owner acts.

## 12. What remains open after this memo

- The **target freeze act** (Path A targets and manifest block).
- The **dated grant**.
- **C7/C8 classification** (structural versus quantitative rate).
- **Authorisation policy** for the run.

The memo does not resolve those by implication.

## 13. Current state before signature

| Item | State |
| --- | --- |
| Path A | **RECORDED** in the protocol and freeze log |
| Path B | **NOT SELECTED**; future experiment |
| C1/C4 ordering | **ADOPTED — BINDING FOR A1** in [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md) |
| 60-row denominator floor | **ADOPTED — BINDING FOR A1** with the C1/C4 gate |
| Target sets | **DRAFT — NOT FROZEN** |
| Freeze decision | **DO NOT FREEZE (2026-11-14)** |
| Seed reservation | **NONE** |
| Grant | **NOT ISSUED** |
| Run | **NOT STARTED** |
| Observed C1/C4 | **NONE** |

**Not evidence:** An unsigned owner decision memo and a definition of VOID. It makes no causal, capability, transfer or generalization claim.
