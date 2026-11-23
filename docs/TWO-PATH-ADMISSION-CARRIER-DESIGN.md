# Two-path admission and carrier discrimination — design

**Status: REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT.** This replaces the blocked
single-stage 2×2 in [`CARRIER-SELECTION-DISCRIMINATION-DESIGN.md`](CARRIER-SELECTION-DISCRIMINATION-DESIGN.md).
It assigns no seeds, implements no runner and authorises no cell. A runnable block requires a separate
frozen preregistration with seed, power and materiality decisions, implemented arms and an owner grant.
Nothing here changes the engine, a verdict, a seed allocation or an artifact.

## Why the single-stage design is replaced

A0 returned **`NO SINGLE UPSTREAM SELECTION STAGE IDENTIFIED`**
([`CARRIER-FORMATION-A0.md`](CARRIER-FORMATION-A0.md)). The records name two parallel stages, not one
upstream chain:

- **Admission** excludes the direct edge: **672** present, **671** constructed, **179** never served,
  **26** asserted but never served, and **0** of the 26 inside the served transition budget.
- **Candidate formation** creates the carrier: **26/26** rows, formation cycles **37–117**, median
  first formation **76**.
- The carrier exists at or before the best recorded rank in **17** rows and after it in **9**.
- Admission can fail while a carrier still supplies the assertion. The routes are parallel.

A design that requires one `S` upstream of `C` therefore has no identified lever. The replacement
does not search for a better single `S`; it treats admission and carrier availability as two factors
and tests whether either route contributes to assertion.

## Question

Does carrier availability contribute to assertion **independently of admission**, and is the
carrier–assertion association causal, a shared-cause association, no carrier relation, or a
readout of assertion?

## The two paths

```text
U — pre-treatment temporal salience
├──► A — admission (served-window availability) ──► Y — assertion
└──► K — carrier availability ────────────────────► Y
```

`A` and `K` are parallel paths from the same temporal substrate. `U` is the measured candidate common
cause: the edge's pre-treatment temporal count, reverse count and strength. `U` is not a post-outcome
rank, and it is not inferred from the intervention.

The paths are not assumed independent. The design tests whether they are:

- `A` is manipulated at the served-window allocation.
- `K` is manipulated at the carrier-to-readout step.
- Each manipulation must leave the other path's availability intact. If it does not, the cell is
  `VOID`.

## The four models

```text
M-K — Carrier causal
U ──► K ──► Y
U ──► A ──► Y

M-N — No carrier relation
U ──► A ──► Y
K ⫫ Y | A            (K has no path to Y)

M-S — Shared cause
U ──► K
U ──► Y
U ──► A ──► Y          (K has no path to Y)

M-R — Readout
U ──► A ──► Y ──► K     (K follows assertion; K has no path to Y)
```

M-N and M-S differ in the conditional association: M-N predicts `K ⫫ Y | A`; M-S predicts a residual
association through `U`. M-S and M-R differ in temporal order and in what an assertion blockade does to
`K`. If `U` cannot be measured, M-N and M-S are not separated; the design says so rather than choosing.

All four labels are graph-level statements about the relation between `K` and `Y`. `M-N` is not a
stage claim; it says the carrier is independent of assertion given admission. The routing target is a
separate decision.

## Identifiability conditions — before intervention or outcome

These are preconditions, not results. The order is fixed:

1. establish the conditions below,
2. choose only the interventions they admit,
3. then read the outcome.

A design that chooses an intervention first and checks identifiability afterwards has reversed the
order. No cell may run while a condition is unresolved, and no secondary outcome can rescue a failed
condition.

| ID | Condition | What must be true | If it fails |
| --- | --- | --- | --- |
| `C1_path_separation` | The two paths are separately manipulable | `A−` changes served availability without changing carrier availability; `K−` changes carrier availability without changing served availability | `NOT IDENTIFIED`: the two-path model is not testable |
| `C2_treatment_consistency` | Each intervention changes the path it names | `A−` reduces the target edge's served availability to zero; `K−` reduces its carrier availability to zero; `Y−` reduces assertion | `VOID`: the intervention did not happen as specified |
| `C3_positivity` | Every required cell is observable | Eligible edges and both path states exist in all four `A×K` cells on every seed; `Y−` is observable at `A+K+` and `A−K+` | `VOID` or `NOT MEASURABLE`: an empty cell cannot be read as zero |
| `C4_no_interference` | Edge-level interventions do not move other edges | An intervention on one edge leaves other edges' `A`, `K` and `Y` within the precommitted tolerance | `NOT IDENTIFIED`: the edge-level estimand is not defined; cluster or redesign |
| `C5_common_cause` | `U` is measured before the outcome | Direct temporal count, reverse count and strength are fixed before the carrier becomes available and before `Y` is read; no post-outcome rank is used | `SHARED CAUSE / NO CARRIER RELATION NOT SEPARATED`: the two non-carrier models remain equivalent |
| `C6_temporal_resolution` | `K` and `Y` are ordered at the same cycle resolution | The record can distinguish `K` before `Y` from `Y` before `K`; no reverse-time imputation is used | `SHARED CAUSE / READOUT NOT SEPARATED`: order cannot be read |
| `C7_assertion_block` | `Y−` is independent of both paths | `Y−` reduces assertion without changing `A` or `K` formation beyond tolerance | `SHARED CAUSE / READOUT NOT SEPARATED`: the ordering arm is confounded |
| `C8_third_route` | The double block is interpretable | `A−K−` has a precommitted ceiling and can distinguish “no route” from “third route” | `TWO-PATH MODEL NOT TESTABLE`: the completeness control is absent |
| `C9_same_object` | The cells compare the same object | Same world, seed, cycles, cap, candidate universe and `U` across all cells; no frozen engine file changes | `VOID`: the comparison is not paired |

**What “identified” means here.** An outcome is identified only if `C1`–`C9` hold, the four cells and
the `Y−` arm are observable, each intervention moves its own path and not the other, `U` is measured
before the outcome, and `A−K−` can test for a third route. Otherwise the design returns the failure
verdict in the table before any model is read.

**What is not allowed.** A significant `K` effect cannot rescue a failed `C1`; a strong `A` effect
cannot substitute for `C5`; and an assertion blockade that changes carrier formation cannot be used
as evidence for readout. Those are design failures, not weak results.

## Design: 2×2 plus two ordering arms

The primary 2×2:

| Cell | Admission | Carrier availability |
| --- | --- | --- |
| `A+ K+` | allowed | available |
| `A+ K−` | allowed | blocked |
| `A− K+` | blocked | available |
| `A− K−` | blocked | blocked |

The `A− K−` cell is a **positive control**: if assertion remains high when both known routes are
blocked, a third route exists and the two-path model is incomplete. The block is then
**`THIRD ROUTE PRESENT`**, not evidence for any of the four models.

Two ordering arms:

- **`Y−` assertion blockade**, run at `A+ K+` and `A− K+`: block the assertion readout while leaving
  admission and carrier formation intact, and measure whether carrier availability falls.
- **`U` measurement**, fixed before the outcome window: direct temporal count, reverse count and
  strength at carrier formation. These are used for pre-intervention stratification, not as
  post-treatment covariates that absorb the carrier.

The interventions below are admissible only after `C1`–`C9` are established. They are not chosen
first and justified afterwards.

## What each intervention leaves behind

**`A−` — admission blocked.** The target edge is held out of the served window. The temporal graph,
co-occurrence counts, tag counts and the carrier trace remain. The condition is **served-window
availability blocked with carrier substrate retained**, not “edge erased.”

**`K−` — carrier blocked.** The carrier is held out of the structure-to-assertion readout. The
admission path remains. The carrier trace remains. The condition is **carrier availability blocked
with learned substrate retained**, not “carrier deleted from the record.”

**`Y−` — assertion blocked.** The assertion/readout step is removed while admission and carrier
formation remain. If it cannot be implemented without changing either path, the arm is not run and the
design returns **`SHARED CAUSE / READOUT NOT SEPARATED`**.

## Precommitted predictions

Let `Y` be the assertion rate. The signatures are fixed before any cell. They are qualitative; the
runnable preregistration must fix the estimator, seed count and materiality bar.

| Signature | M-K Carrier causal | M-N No carrier relation | M-S Shared cause | M-R Readout |
| --- | --- | --- | --- | --- |
| `K` effect at `A−` (`A−K+` vs `A−K−`) | positive | null | null | null |
| `A` effect at `K−` (`A+K−` vs `A−K−`) | positive | positive | positive | positive |
| `A−K−` assertion | near zero | near zero | near zero | near zero |
| `K`–`Y` association given `A` | positive | null | positive | positive |
| `K`–`Y` association given `A` and `U` | positive | null | null | positive |
| `Y−` effect on `K` | none | none | none | reduces |
| Temporal order of `K` and `Y` | `K` before `Y` | no required order | both follow `U` | `Y` before `K` |

The `K` effect at `A−` is the primary causal contrast. The `A` effect at `K−` is the admission-route
check. The `A−K−` cell is the completeness check. The `U`-conditional row separates M-K from M-S. The
`Y−` row and the temporal order separate M-S from M-R.

## Manipulation and independence checks

| Check | Requirement | Failure |
| --- | --- | --- |
| `T1_admission_block` | `A−` reduces served availability of the target edge to zero on every seed | `VOID`; admission was not blocked |
| `T2_carrier_block` | `K−` reduces carrier availability of the target edge to zero on every seed | `VOID`; carrier was not blocked |
| `T3_cross_path` | `A−` leaves carrier availability within its precommitted tolerance and `K−` leaves served availability within its tolerance | `VOID`; the factors are confounded |
| `T4_same_world` | all cells of a seed share world, cycles, cap, candidate universe and `U` | `VOID`; the comparison is not paired |
| `T5_no_engine_edit` | the arms are benchmark-only subclasses; no frozen engine file changes | `VOID`; the build is not the shipped engine |
| `T6_determinism` | a fresh-process rerun of the first seed reproduces its cell fingerprints | `VOID`; the arm is not reproducible |
| `T7_assertion_block` | `Y−` reduces assertion while leaving `A` and `K` formation intact | `SHARED CAUSE / READOUT NOT SEPARATED`; do not guess |
| `T8_third_route` | `A−K−` assertion is at or below the precommitted ceiling | `THIRD ROUTE PRESENT`; the two-path model is incomplete |

`T1`–`T6` are void gates. `T7` and `T8` are structural gates with their own verdicts.

**Thresholds fixed 2026-11-14, before any cell.** `C1` requires at least 95% preservation of the
other path on every seed, measured against the paired control's available edges. `C4` and `C7` use a
0.05 absolute-rate margin. `C8` reads `THIRD ROUTE PRESENT` above a 0.05 assertion rate in `A−K−`.
These are design conventions, not estimates from A0 or any run; the definitions and fragility are
recorded in [`A1-PRECOMMITTED-THRESHOLDS.md`](A1-PRECOMMITTED-THRESHOLDS.md). Fixing them does not
authorise a run.

## Decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
| any `T1`–`T6` fails | `VOID` | the intervention did not happen as specified; no model is read |
| `T8` fails | `THIRD ROUTE PRESENT` | assertion survives both known routes; the two-path model is incomplete and no model is selected |
| `K` effect at `A−` is positive; association persists within `U`; `K` precedes `Y`; `Y−` does not reduce `K` | `CARRIER CAUSAL` | carrier availability contributes independently of admission |
| `K` effect at `A−` is null; `K`–`Y` association vanishes given `A`; `A` effect is positive | `NO CARRIER RELATION` | the carrier is not a route; admission carries the assertion |
| `K` effect is null; association persists given `A` but vanishes within `U`; `Y−` does not reduce `K` | `SHARED CAUSE` | `U` moves both carrier and assertion; the carrier is not the path |
| `K` effect is null; `Y−` reduces `K`; `Y` precedes `K` | `READOUT` | the carrier follows assertion; it is not a cause |
| `T7` cannot be run or is not implemented | `SHARED CAUSE / READOUT NOT SEPARATED` | the two non-causal models remain observationally equivalent under the available interventions |
| signatures conflict across seeds or estimands | `MIXED / NOT DISCRIMINATED` | no model is eliminated; report the conflict, do not choose the convenient one |

## M1 mapping

The roadmap records the outcome by branch:

| Design verdict | M1 branch | A3 target | V2 implication |
| --- | --- | --- | --- |
| `CARRIER CAUSAL` | `M1-C` | Carrier → external | Carrier-targeted V2 eligible |
| `NO CARRIER RELATION` | `M1-A` | Admission → external | Admission-targeted V2 eligible; no carrier V2 |
| `SHARED CAUSE` | `M1-CC` | `U` → external | Shared-cause V2 eligible; no carrier V2 |
| `READOUT` | `M1-RO` | Assertion or admission → external, never carrier | No carrier-targeted V2 |
| `THIRD ROUTE PRESENT`, `MIXED`, `VOID` | `M1-X` or `M1-V` | None | None |

M1-CC and M1-RO are target-identification branches, not claims that the full selection mechanism is
understood. The target is identified at the resolution of the manipulated path.

## What must be fixed before a runnable preregistration

1. **Implement the four 2×2 arms and the `Y−` arm** without touching a frozen engine file. *(Implemented 2026-11-14 in `benchmarks/a1_arms.py`; a target set is still unresolved and no cell has run.)*
2. **Fix the `A−`, `K−` and `A−K−` tolerances and the `T8` ceiling** before any cell. *(Thresholds fixed 2026-11-14; see the record above.)*
3. **Fix the `U` measurement** and its stratification rule; do not use a post-outcome rank.
4. **Fix a fresh seed block, a materiality bar and a power calculation.** No seeds are assigned here.
5. **Record an owner grant.** This design is not a grant and no cell may run under it.

## What this does not establish

This is a design, not a result. It assigns no seed, runs no cell and makes no causal, transfer,
capability or external-advantage claim. It does not authorise an engine change or a V2 build. The
existing carrier enrichment remains an association until a runnable block returns one of the verdicts
above.
