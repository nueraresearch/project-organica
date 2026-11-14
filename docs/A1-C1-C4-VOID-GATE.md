# A1 C1/C4 post-freeze VOID gate — draft decision

**ID:** `A1-C1-C4-VOID-GATE-1`

**Date:** 2026-11-14

**Status:** `DRAFT — NOT DECIDED; THE CURRENT C4-ONLY RECORD REMAINS IN FORCE`

**This is a draft decision record, not an adopted decision, a target freeze, a grant or a result.** It proposes a narrower replacement for the C1 disposition in [`A1-GATE-READINESS.md`](A1-GATE-READINESS.md) and consolidates it with the already-recorded C4 gate in [`A1-C4-GATE-ORDER.md`](A1-C4-GATE-ORDER.md). Until the owner records adoption, the current records remain authoritative.

## 1. Proposed decision

Treat **C1 path separation** and **C4 no interference** as one **post-freeze result-validity test**:

1. The owner freezes the representative target manifest in a separate act.
2. The owner records the dated grant; the planned cells run.
3. `a1_result.assemble` reads the actual cell parts and reports the observed C1 denominators and C4 deltas.
4. **Both C1 and C4 must pass.** Either gate failing, or either being unmeasurable, makes the A1 run **VOID** before any model is read.
5. Only after both pass may the remaining gates and the four model labels be considered.

This is not a change to the thresholds. C1 remains at **0.95** preservation; C4 remains at a **0.05** absolute neighbour-delta ceiling. The proposal changes only the **disposition** of a failed or unmeasurable C1 from `NOT IDENTIFIED` / `UNSATISFIABLE` to **VOID**, and makes the C1/C4 pair a single validity decision.

## 2. Why the gate is post-freeze

Neither C1 nor C4 is a property of the target set:

- C1 needs the executed `A−` and `K−` cells and a paired-control denominator.
- C4 needs executed edge-level interventions and non-target neighbour rows.

Making either a pre-freeze admissibility condition would require a circular freeze or an unregistered diagnostic run. The gate therefore sits after the frozen cells exist. It does not delay or condition the target freeze; it decides whether the executed run is admissible as evidence.

## 3. Gate order

```text
P0 compliance and target feasibility
        ↓
separate target freeze
        ↓
separate dated grant
        ↓
planned A1 cells run
        ↓
assemble C1 + C4 from actual parts
        ↓
both pass ──► read C7/C8 and the remaining gates
either fails or is unmeasurable ──► A1 VOID
```

A VOID stops the result. It does not trigger a second run, a repaired denominator, a threshold change or a model choice.

## 4. VOID conditions

| Gate | Condition | Reason code |
| --- | --- | --- |
| C1 | No paired-control denominator is available for a required seed or required row. A missing denominator is not zero. | `C1_NO_DENOMINATOR` |
| C1 | On any seed, `A−` carrier preservation is below 0.95, or `K−` served preservation is below 0.95. | `C1_THRESHOLD` |
| C4 | The non-target stream is absent, incomplete, or has no measurable paired delta. | `C4_UNMEASURABLE` |
| C4 | Any measurable non-target A, K or Y neighbour delta exceeds 0.05. | `C4_DELTA` |
| Assembly | Required cell parts are missing, duplicated, or cannot be paired for C1/C4. The gate is unmeasurable; it is not a zero-row pass. | `C1_C4_INCOMPLETE` |

A run with any one of these conditions is `A1 VOID — C1/C4`. If both gates fail, both reason codes are recorded; one gate cannot be suppressed by the other.

## 5. What a VOID run means

A VOID run means the experiment **did not produce an admissible comparison**. It does not mean the carrier model is false, the two-path model is false, or the intervention had no effect.

For a VOID run:

- The recorded status is **`A1 VOID — C1/C4`**, with the failing gate or gates and the reason code.
- No causal model is selected: no `M-K`, `M-N`, `M-S` or `M-R` label.
- No M1 branch is assigned, and no V2, capability, transfer, external-advantage or generalization claim may be read.
- C7 and C8 are **not adjudicated**. If they were not evaluated before the VOID, they are reported as `NOT ADJUDICATED — RUN VOID`, not as pass or fail.
- The run is **not a negative result**. It is not evidence for or against any model, and it may not be reported as a null finding.
- The observed C1 denominators and C4 row counts are retained in the record for audit, even when the gate fails. A missing denominator is reported as missing, never as `0.0`.
- The planned seeds and cells are consumed. No substitute seed, extra cell or post-hoc target may be added.
- No row may be dropped, no threshold changed, no target re-selected and no denominator expanded after the failure is seen.
- The parts and the observed counts are preserved. They may be used for instrument diagnostics, but not re-labelled as an A1 result.

## 6. What a VOID run does not mean

A VOID run does **not**:

- establish that C1 or C4 can never pass;
- establish that the two-path model is untestable in principle;
- license a new selector, a new target count or a new threshold under the same registration;
- convert a failed C1 into a C4 problem or a failed C4 into a C1 problem;
- permit re-reading a failed run as “near pass” or “descriptively supportive”;
- authorise a second attempt. A further attempt requires a **new registered design**, a fresh seed block and a new dated owner grant.

A pass is also not a model verdict. C1 and C4 passing means only that the comparison is admissible; C2, C3, C5, C7, C8 and C9 still decide whether a model may be read.

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
reason_codes: [] | [C1_NO_DENOMINATOR, C1_THRESHOLD, C4_UNMEASURABLE, C4_DELTA, C1_C4_INCOMPLETE]
observed_denominator:
  c1: {a_minus, k_minus, by_seed}
  c4: {rows, measured, unmeasured}
model: null when status is VOID
not_evidence: "A gate decision, not a causal, capability or transfer result."
```

`a1_result.assemble` currently returns `PASS` or `FAIL`. If this draft is adopted, the assembly caller maps a C1/C4 `FAIL` to `VOID`; it must not publish `FAIL` as a scientific verdict. The mapping and its tests are an adoption task, not part of this draft.

## 9. Relationship to the current records

| Record | Current state | Effect if this draft is adopted |
| --- | --- | --- |
| [`A1-C4-GATE-ORDER.md`](A1-C4-GATE-ORDER.md) | C4 is a post-freeze VOID gate; C1 is a post-freeze result gate | C4 trigger is unchanged; the C1 relationship is superseded by this consolidated gate |
| [`a1_c4_gate_order.json`](a1_c4_gate_order.json) | Machine record of the C4-only decision | Add a cross-reference to this record; do not rewrite the historical C4 decision |
| [`A1-GATE-READINESS.md`](A1-GATE-READINESS.md) | C1 failure is `NOT IDENTIFIED`; C1 unmeasurable is `UNSATISFIABLE` | C1 failure and unmeasurable become `VOID`; the one-attempt bound is unchanged |
| `benchmarks/a1_gate_readiness.py` | `BOUNDS` carries the C1 result-gate disposition | Update C1 failure and unmeasurable dispositions to `VOID` and regenerate the readiness artifact |
| `benchmarks/a1_result.py` | Returns `PASS` / `FAIL` | Caller maps a C1/C4 failure to `VOID`; the assembly object should carry the reason codes |

Until adoption, none of these rows changes. The C4-only record continues to govern, and C1 remains a result gate.

## 10. Adoption check

Adoption requires a dated owner decision. It must update, in the same act:

- the C1 `BOUNDS` failure and unmeasurable dispositions;
- the readiness artifact and page;
- the C1/C4 gate-order cross-references;
- the result-assembly `VOID` mapping and its tests;
- the manual, checklist and changelog.

Adoption does not freeze targets, reserve seeds, issue a grant, run a cell or create evidence.

## 11. What this draft is not

This is not an A1 result, a grant, a freeze, a seed reservation, a threshold change or a claim that C1 or C4 failed. No cell has run. The observed denominator remains unknown, and the current `DO NOT FREEZE` state and the separate target-freeze blocker are unchanged.

**Not evidence:** A proposed gate order and a definition of VOID. It makes no causal, capability, transfer or generalization claim.
