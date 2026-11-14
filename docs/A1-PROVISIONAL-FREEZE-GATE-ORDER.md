# A1 provisional freeze and C1/C4 gate-order decision — draft

**ID:** `A1-PROVISIONAL-FREEZE-GATE-ORDER-1`

**Date:** 2026-11-14

**Status:** `DRAFT — NOT DECIDED; NO FREEZE, NO GRANT, NO RUN`

**Current authority:** `DO NOT FREEZE (2026-11-14)` and the C4-only [gate order](A1-C4-GATE-ORDER.md).

**Companion proposal:** [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md).

**C1/C4 gate status:** the C1/C4 post-freeze VOID gate and the 60-row denominator floor are **ADOPTED — BINDING FOR A1** in [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md). This wrapper remains draft only for the provisional target freeze. [`A1-OWNER-DECISION-1`](DECISION-A1-PATH-A-C1-C4.md) remains a draft for the remaining Path A confirmation and provisional-freeze decisions; it records no freeze, grant or run.

**This is a draft decision record for the provisional freeze, not an adopted freeze, a seed reservation, a grant or a result.** The C1/C4 gate is already adopted separately; the current `DO NOT FREEZE` state and the historical C4-only record remain in force. Adopting this wrapper would require a new dated owner act; it would not retroactively change the historical freeze decision.

## 1. Decision proposed

Adopt one gate order for the Path A attempt:

1. P0 compliance, target feasibility and the Path A estimand record stand.
2. The owner records a **provisional freeze** of the Path A target sets and manifest target block.
3. The owner records the dated grant; this remains a separate act.
4. The planned A1 cells run.
5. `a1_result.assemble` reads the actual cell parts and reports the observed C1 denominators and C4 deltas.
6. **Both C1 and C4 must pass.** Either gate failing, or either being unmeasurable, makes the run **`A1 VOID — C1/C4`** before any model is read. Only after both pass may C7/C8 and the remaining gates be considered.

The C1 threshold remains **0.95** preservation and the C4 threshold remains a **0.05** absolute neighbour-delta ceiling. The adopted C1/C4 gate changes the **disposition** of a failed or unmeasurable C1 from `NOT IDENTIFIED` / `UNSATISFIABLE` to **VOID**, and makes C1/C4 one post-freeze validity decision. This wrapper does not change a threshold and does not re-adopt that gate.

## 2. What “provisional freeze” means

The freeze is **provisional in its evidentiary status, not in its target identity**.

- Before the grant, the owner fixes the Path A target sets and the manifest target block against the selection artifact. After that act, the targets are the targets for the registered attempt.
- The freeze does **not** wait for C1 or C4. Neither gate is a pre-freeze admissibility condition, because neither can be observed without executed cells.
- The run's **result** is provisional until C1/C4 pass. A C1/C4 failure makes the run VOID; it does not unfreeze the targets, authorise a different target set, or convert the attempt into a pilot.
- The target identity is **not revocable after outcomes are seen**. A VOID run does not permit re-selection, a repaired denominator, an extra cell or a substitute seed.
- “Provisional” is **not** a licence to retry. It describes the conditional admissibility of the result, not a probationary target set.
- This draft does not itself reserve seeds, record a grant or authorise a cell. Whether seed reservation accompanies the freeze act is fixed in that owner act; no seed is reserved here.

The distinction is deliberate: a freeze that could be undone after a C1/C4 failure would make target selection outcome-dependent, which is the failure the pre-outcome protocol exists to prevent.

## 3. Gate order

```text
P0 compliance and target feasibility
        ↓
Path A estimand recorded
        ↓
provisional target freeze (no C1/C4 precondition)
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

A VOID stops the result. It does not trigger a second run, a repaired denominator, a threshold change, a target re-selection or a model choice.

## 4. C1/C4 VOID conditions

| Gate | Condition | Reason code |
| --- | --- | --- |
| C1 | No paired-control denominator is available for a required seed or required row. A missing denominator is not zero. | `C1_NO_DENOMINATOR` |
| C1 | The observed minimum paired-control denominator is below **60** on any seed or path, even if every available row is retained. The floor is adopted by [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md) and recorded in [`DECISION-A1-PATH-A-C1-RULE.md`](DECISION-A1-PATH-A-C1-RULE.md). | `C1_DENOMINATOR_BELOW_FLOOR` |
| C1 | On any seed, `A−` carrier preservation is below 0.95, or `K−` served preservation is below 0.95. | `C1_THRESHOLD` |
| C4 | The non-target stream is absent, incomplete, or has no measurable paired delta. | `C4_UNMEASURABLE` |
| C4 | Any measurable non-target A, K or Y neighbour delta exceeds 0.05. | `C4_DELTA` |
| Assembly | Required cell parts are missing, duplicated, or cannot be paired for C1/C4. The gate is unmeasurable; it is not a zero-row pass. | `C1_C4_INCOMPLETE` |

A run with any one of these conditions is **`A1 VOID — C1/C4`**. If both gates fail, both reason codes are recorded; one gate cannot be suppressed by the other.

**Denominator floor.** The 60-row floor is **ADOPTED — BINDING FOR A1** in [`A1-C1-C4-VOID-GATE.md`](A1-C1-C4-VOID-GATE.md), with the rule recorded in [`DECISION-A1-PATH-A-C1-RULE.md`](DECISION-A1-PATH-A-C1-RULE.md). A perfect 59/59 is VOID; the fraction cannot rescue a denominator below 60.

## 5. What a VOID run means

A VOID run means the experiment **did not produce an admissible comparison**. It does not mean the carrier model is false, the two-path model is false, or the intervention had no effect.

For a VOID run:

- The recorded status is **`A1 VOID — C1/C4`**, with the failing gate or gates and the reason code.
- No causal model is selected: no `M-K`, `M-N`, `M-S` or `M-R` label.
- No M1 branch is assigned, and no V2, capability, transfer, external-advantage or generalization claim may be read.
- C7 and C8 are **not adjudicated**. If they were not evaluated before the VOID, they are reported as `NOT ADJUDICATED — RUN VOID`, not as pass or fail.
- The run is **not a negative result**. It is not evidence for or against any model, and it may not be reported as a null finding or a failed replication.
- The observed C1 denominators and C4 row counts are retained in the record for audit, even when the gate fails. A missing denominator is reported as missing, never as `0.0`.
- The planned seeds and cells are consumed. No substitute seed, extra cell or post-hoc target may be added.
- No row may be dropped, no threshold changed, no target re-selected and no denominator expanded after the failure is seen.
- The parts and observed counts are preserved. They may support instrument diagnostics, but may not be re-labelled as an A1 result.
- The target freeze remains recorded. A VOID does not return the attempt to an unfrozen state and does not authorise a second attempt under the same registration.

## 6. VOID is not PARKED, NOT IDENTIFIED or UNSATISFIABLE

| Status | When it applies | What it records |
| --- | --- | --- |
| `A1 PARKED — …` | The run did not execute: missing target set, missing rule, or no grant. | A preparation or authorisation stop, not an experimental outcome. |
| `A1 VOID — C1/C4` | The planned run executed but the C1/C4 validity test failed or was unmeasurable. | No admissible comparison; no model read. |
| `NOT IDENTIFIED` (historical) | The pre-adoption C1 result-gate failure when the comparison existed but model separation was not achieved. | Historical only; A1 now uses `A1 VOID — C1/C4`. |
| `UNSATISFIABLE` (historical) | The pre-adoption disposition for a gate that could not be measured under the registered design. | Historical only; A1 now uses `A1 VOID — C1/C4`. |

The adopted C1/C4 gate already moves C1 failure and C1 unmeasurability from `NOT IDENTIFIED` / `UNSATISFIABLE` to **VOID**. C4 uses VOID. The one-attempt rule is unchanged: a VOID is terminal for this registration, and a further attempt needs a new registered design, a fresh seed block and a new dated owner grant.

A **pass** is not a model verdict either. C1/C4 passing means only that the comparison is admissible; C2, C3, C5, C7, C8 and C9 still decide whether a model may be read.

## 7. No rescue rule

- A passing C4 cannot rescue a failing C1.
- A passing C1 cannot rescue a failing C4.
- A passing C2, C3, C5, C7 or C8 cannot rescue a C1/C4 VOID.
- A larger observed denominator discovered after the run cannot be used to re-score C1. The C4 non-target rows must be part of the registered design, not an analysis-time expansion.
- A failed or unmeasurable gate is terminal for this registration. The one-attempt rule in [`A1-GATE-READINESS.md`](A1-GATE-READINESS.md) applies unchanged.

## 8. Required report shape

A result-assembly record for this gate must carry at least:

```text
status: PASS | VOID
void_gates: [] | [C1_PATH_SEPARATION, C4_NO_INTERFERENCE]
reason_codes: [] | [C1_NO_DENOMINATOR, C1_DENOMINATOR_BELOW_FLOOR, C1_THRESHOLD, C4_UNMEASURABLE, C4_DELTA, C1_C4_INCOMPLETE]
observed_denominator:
  c1: {a_minus, k_minus, by_seed}
  c4: {rows, measured, unmeasured}
model: null when status is VOID
not_evidence: "A gate decision, not a causal, capability or transfer result."
```

`a1_result.assemble` returns `PASS` or `VOID` under the adopted C1/C4 gate and carries `void_gates` and `reason_codes`. It does not publish a C1/C4 `FAIL` as a scientific verdict. This wrapper does not re-adopt that mapping.

## 9. Relationship to current records

| Record | Current state | Effect if this draft is adopted |
| --- | --- | --- |
| [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md) | `DO NOT FREEZE (2026-11-14)`; Path A recorded; targets draft | A new dated provisional-freeze record supersedes the procedural freeze blocker for this attempt; the historical decision is not rewritten |
| [`A1-TARGET-SELECTION-PROTOCOL.md`](A1-TARGET-SELECTION-PROTOCOL.md) | Path A recorded; six target sets draft | The Path A target sets and manifest target block are frozen in the adoption act; no target is regenerated |
| [`A1-C4-GATE-ORDER.md`](A1-C4-GATE-ORDER.md) | C4 is a post-freeze VOID gate; C1 is a post-freeze result gate | C4 trigger unchanged; C1 is consolidated into the C1/C4 validity gate |
| [`A1-C1-C4-VOID-GATE.md`](A1-C1-C4-VOID-GATE.md) | **ADOPTED — BINDING FOR A1**; the 60-row floor and C1/C4 VOID gate are in force | The adopted detail governs the C1/C4 gate; this wrapper does not re-adopt it |
| [`A1-GATE-READINESS.md`](A1-GATE-READINESS.md) | C1/C4 failure and unmeasurability are `VOID`; the one-attempt bound is unchanged | Already in force; this wrapper changes no gate disposition |
| `benchmarks/a1_gate_readiness.py` | `BOUNDS` carries the adopted C1/C4 `VOID` dispositions | Already in force; no change from this wrapper |
| `benchmarks/a1_result.py` | Returns `PASS` / `VOID`; carries gate names and reason codes | The adopted gate already implements this; this wrapper does not change it |

The C1/C4 rows are already in force. Until this wrapper is adopted, only the provisional freeze remains proposed; the C4-only record remains the historical C4 decision, and the targets remain draft.

## 10. Adoption check

Adoption requires a dated owner decision. It must update, in the same act:

- a new freeze record that distinguishes provisional evidentiary status from final target identity;
- the Path A target block and manifest freeze record;
- the C1 `BOUNDS` failure and unmeasurable dispositions;
- the readiness artifact and page;
- the C1/C4 gate-order cross-references;
- the result-assembly `VOID` mapping and its tests;
- the manual, checklist and changelog.

Adoption does not reserve seeds, issue a grant, run a cell or create evidence, except where the owner explicitly records the seed reservation in the same act.

## 11. What this draft is not

This is not an A1 result, a grant, a freeze, a seed reservation, a threshold change or a claim that C1 or C4 failed. No cell has run. The observed denominator remains unknown, the targets remain **DRAFT — NOT FROZEN**, and the current `DO NOT FREEZE` state remains in force.

**Not evidence:** A proposed gate order and a definition of VOID. It makes no causal, capability, transfer or generalization claim.
