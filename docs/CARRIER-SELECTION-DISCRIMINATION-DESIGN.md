# Carrier selection discrimination — design

**Status: SUPERSEDED FOR DESIGN — retained as the blocked single-stage record. NOT RUN, NO GRANT.**
A0 returned `NOT IDENTIFIED`: the 2×2 required a single upstream selection stage and the records
contain two parallel stages instead. The replacement is
[`TWO-PATH-ADMISSION-CARRIER-DESIGN.md`](TWO-PATH-ADMISSION-CARRIER-DESIGN.md), which is also
design-only and unrun. This document is kept because the failed identification is part of the record;
it assigns no seed and authorises no cell.

## Question

Among asserted never-served edges, is the loop or workflow carrier a **cause** of assertion, a
**correlate of a shared upstream selection process**, or a **readout** of selection that has already
happened elsewhere?

The question is about the carrier's role in the selection path, not about whether carriers are
enriched. Enrichment is established. Causation is not.

## Scope

- Population: never-served world edges in the Gate-13 compositional world family used by the
  provenance and carrier blocks.
- Unit: edge × seed.
- Primary outcome: whether the edge is an asserted final prediction source at the readout. Final
  presence and first assertion cycle are secondary.
- Carrier: a loop or workflow structure that carries the edge before the outcome window. The exact
  carrier definition is inherited from the carrier trace; it is not redefined here.
- The world, cycle count, cap, decay, confidence rule and candidate set are held fixed across arms.
  Only the named intervention differs.

## A0 result (2026-11-13)

[`docs/CARRIER-FORMATION-A0.md`](CARRIER-FORMATION-A0.md) is a read-only join of the 26 carrier rows,
their provenance ranks, the Q4 stage table and the 26 unexplained edges. Its verdict is
**`NO SINGLE UPSTREAM SELECTION STAGE IDENTIFIED`**.

- **Admission excludes the direct edge.** Q4 records **672** present edges, **671** constructed,
  **179** never served and **26** asserted but never served. Of the 26, **0** sit inside the served
  transition budget. Construction is not the loss.
- **Candidate formation creates the carrier.** All **26/26** rows have a loop carrier, formed at cycles
  **37–117** (median first formation **76**). The loop builder reads temporal cycles, not served
  windows.
- **The order is mixed.** The carrier exists at or before the best recorded rank in **17** rows and
  after it in **9**. The records do not support a single ordering in which carrier formation precedes
  admission for every edge.
- **They are parallel paths to assertion.** Admission can fail while the carrier still supplies the
  assertion. Admission is therefore not upstream of the carrier, and candidate formation is the
  carrier itself rather than an independent upstream lever.

A0 does not say that no selection process exists. It says the current records do not contain a
single stage that is upstream of `C` and independently manipulable, which is what the 2×2 requires.

## Why a 2×2 is necessary

A carrier-only intervention cannot separate the three models. If the carrier is manipulated and
assertion does not move, both the common-cause and readout models predict that result. The design
therefore manipulates **two things**:

1. the named upstream selection stage `S`, and
2. carrier availability `C`.

The four cells are:

| Cell | Selection stage | Carrier availability |
| --- | --- | --- |
| `S0 C+` | baseline | available |
| `S0 C−` | baseline | blocked |
| `S+ C+` | shifted | available |
| `S+ C−` | shifted | blocked |

`S+` is not “turn selection on.” It is a named, stage-level shift in the selection rule. `C−` is not
“erase the carrier from the record.” It is a blockade of carrier availability on the path to
assertion, with the underlying events and traces left intact.

## The three causal graphs

The graphs are stated before the run. `S` is the named upstream selection stage, `C` is carrier
availability and `A` is assertion. `U` is any unmeasured common cause; if `S` is the only common
cause, `U` is absent.

```text
M1 — Causal carrier
S ───────► C ───────► A
└────────────────────► A   (direct path allowed, but C carries an effect)

M2 — Common cause
S ───────► C
└─────────► A             (C and A share S; C has no path to A)

M3 — Readout only
S ───────► A ───────► C   (C follows assertion, or requires it)
```

M2 and M3 must differ structurally. `S → C` together with `S → A`, with no `C → A` edge, is the
common-cause graph, not a separate readout model. A readout model requires `A → C` (or a carrier
that is a function of the outcome). If “readout” only means “selection produces a carrier marker,”
then it is M2 and cannot be separated from it by a carrier-only intervention.

The models are not distinguished by the presence of a correlation. They are distinguished by what
happens when `C` is blocked while `S` is shifted, by the temporal order of `C` and `A`, and by what
happens to `C` when `A` is blocked.

## Stage map: what `S` must name

“Selection” is not one variable. A0 filled this table from the committed records. A row that fails
any requirement cannot be the `S` of the 2×2.

| Stage | Observable? | Manipulable? | Independent of carrier? | Upstream of carrier? | Eligible as `S`? |
| --- | --- | --- | --- | --- | --- |
| Candidate formation | Yes — 26/26 carriers, cycles 37–117 | Yes in principle — loop threshold or source set (not built) | No — it creates `C` | Yes | No — not independent |
| Admission | Yes — 179 never served; 26 asserted never served; 0 inside the transition budget | Yes in principle — served-window allocation (not built) | Yes — the carrier forms without service | No — parallel path | No — not upstream |
| Service | Yes, as the served window; not separately from admission | No — not separated from admission | Yes | No | No |
| Assertion | Yes — 247 asserted world edges | Yes in principle — the `A−` ordering arm (not built) | Yes | No — downstream | No |

A stage is a valid `S` only if it is observable, manipulable, independent of `C`, and upstream of
`C`; `I3_independence` must also be checkable. **No stage satisfies all four.** Candidate formation
is upstream but not independent; admission and service are independent but parallel; assertion is
independent but downstream. The 2×2 is therefore **`NOT IDENTIFIED`** as specified.

## Identifiability assumptions

The design is only as strong as these assumptions. They are stated before the run and are not
revised after seeing an outcome.

- **Consistency:** the manipulated stage is the stage named in the table, not a proxy for it.
- **No unmeasured common cause of `C` and `A` beyond `S`:** if `U → C` and `U → A` exists and `S` is
  only a proxy for `U`, M1 and M2 can look alike. A0 did not name a candidate `U`; the
  unmeasured-common-cause limit therefore stands.
- **Independent assertion blockade:** the ordering arm must change `A` without mechanically changing
  carrier formation. If it cannot, M2 and M3 are not separable with the available interventions.
- **Positivity and pairing:** every cell has eligible edges on every seed, and the four cells are
  paired on the same world, seed and candidate universe.
- **No interference:** an intervention on one edge does not change another edge’s carrier or
  assertion status, beyond the named selection stage. If interference is present, the edge-level
  estimand is not identified.

## Precommitted predictions

Let `A` be the assertion rate, `C` the carrier-availability rate, and `S` the named selection-stage
state. The predictions below are fixed before any cell. They are qualitative signatures; the
runnable preregistration must fix the estimator, seed count and materiality bar before execution.

| Signature | M1 Causal | M2 Common cause | M3 Readout |
| --- | --- | --- | --- |
| `S+` versus `S0` on `A` | positive | positive | positive |
| `C+` versus `C−` at `S0` on `A` | positive | null | null |
| `S+ × C−` interaction on `A` | negative: the `S+` effect is attenuated when `C` is blocked | none: the `S+` effect persists | none: the `S+` effect persists |
| Temporal order of `C` and `A` | `C` precedes `A` | no required order; both follow `S` | `A` precedes `C`, or `C` requires `A` |
| Assertion blockade effect on `C` | none | none | reduces `C` |
| Carrier incidence under `S+ C−` | carrier blocked, `S+` intact | carrier blocked, `S+` intact | carrier blocked, `S+` intact |

The first three rows are the primary 2×2. The last three rows are the ordering tests that separate
M2 from M3. A design that runs only the 2×2 can return **causal versus non-causal**, but not
**common cause versus readout**. It must say so.

## What each intervention leaves behind

The intervention must name its residue, not only its target.

**`S+` — selection-stage shift.** Changes one named selection rule at one named stage. It does not
change the world, seed, cycle count, cap, decay, confidence formula or candidate universe. The
manipulation check is that the named stage’s output changes in the intended direction. If the stage
does not change, the cell is unrun, not a null.

**`C−` — carrier blockade.** Removes carrier availability from the path to assertion. It does not
erase the events, co-occurrence counts, tag counts or prior traces that produced the carrier. The
condition is therefore **carrier availability blocked with learned substrate retained**, not
“carrier removed.” The manipulation check is that carrier availability falls to the precommitted
floor while the named `S` stage remains within its precommitted tolerance.

**`A−` — assertion blockade (ordering arm).** Removes the assertion/readout step while leaving
candidate formation and carrier formation intact. It is used only to separate M2 from M3. If the
readout contract cannot be blocked without changing carrier formation, this arm is not run and the
design returns **COMMON CAUSE / READOUT NOT SEPARATED**. It does not guess.

## Independence and manipulation checks

The 2×2 is valid only if the factors are independently manipulable.

| Check | Requirement | Failure |
| --- | --- | --- |
| `I1_stage_shift` | `S+` changes the named stage’s output in the intended direction on every seed | `VOID`; the stage was not manipulated |
| `I2_carrier_block` | `C−` reduces carrier availability to the precommitted floor on every seed | `VOID`; the carrier was not blocked |
| `I3_independence` | `C−` leaves the named `S` stage within its precommitted tolerance, and `S+` does not mechanically erase carrier availability | `VOID`; the factors are confounded |
| `I4_same_world` | both arms of a seed use the same world, seed, cycles, cap and candidate universe | `VOID`; the comparison is not paired |
| `I5_no_engine_edit` | the intervention is an in-process benchmark subclass; no frozen engine file changes | `VOID`; the build is not the shipped engine |
| `I6_determinism` | a fresh-process rerun of the first seed reproduces its cell fingerprints | `VOID`; the arm is not reproducible |

`C−` must not be implemented by deleting the carrier from the observer’s reconstruction. That is an
observer-side ablation, and it tests the instrument, not the organism.

## Analysis

- Pair every cell by seed. The seed is the cluster; edges within a seed are not independent.
- Primary estimands: the `C` effect at `S0` (`S0 C+` versus `S0 C−`) and the `S × C` interaction
  (`S+ C−` versus `S+ C+`).
- Report paired risk differences with a 95% interval and the number of seeds with a positive
  difference. Do not report a seed-level sign test as a substitute for the paired estimate.
- Secondary: first assertion cycle, carrier incidence and the ordering of `C` and `A`.
- A cell with no eligible edges is **not measurable** and is excluded. It is never reported as
  `0.0`.
- No threshold is lowered after the eligible-edge count is seen. If the population gate fails, the
  block is `VOID`.

## Decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
| any `I` gate fails | `VOID` | the intervention did not happen as specified; no model is read |
| `C` effect at `S0` is positive; `S+ × C−` attenuates the `S+` effect; `C` precedes `A`; `A−` does not reduce `C` | `CAUSAL CARRIER SUPPORTED` | carrier availability is on the path from selection to assertion |
| no `C` effect at `S0`; `S+` effect persists under `C−`; `C` and `A` co-move after `S`; `A−` does not reduce `C` | `COMMON CAUSE` | selection moves both carrier and assertion; the carrier is not the path |
| no `C` effect at `S0`; `S+` effect persists under `C−`; `A` precedes `C` or `C` requires `A`; `A−` reduces `C` | `READOUT ONLY` | carrier marks selection after the fact; it is not a cause |
| the 2×2 runs but the ordering arm is not runnable | `CAUSAL VERSUS NON-CAUSAL ONLY` | the design separates causal from non-causal, not common cause from readout |
| the stage map cannot name a valid `S` or `I3_independence` fails | `NOT IDENTIFIED` | `S` and `C` are not separately manipulable; the 2×2 is not a discrimination design |
| the signatures conflict across seeds or estimands | `MIXED / NOT DISCRIMINATED` | no model is eliminated; report the conflict, do not choose the convenient one |
| the population or power gate fails | `VOID` | the block could not test the question; this is not evidence for any model |

The roadmap records these outcomes as `M1-C` (causal carrier), `M1-CC` (common cause), `M1-RO`
(readout only), `M1-X` (mixed / not discriminated) and `M1-V` (void).

## What each outcome licenses

- **Causal carrier supported:** licenses an external-link design that targets the carrier, and a
  mechanism-targeted V2 discussion. It does not establish external advantage.
- **Common cause:** closes the carrier as the causal path. The selection stage becomes the target.
  It does not license a carrier intervention or a carrier-targeted V2.
- **Readout only:** closes the carrier as a cause and as a leading indicator. Selection remains the
  target, and the carrier is demoted to a marker.
- **Mixed / not discriminated:** licenses no causal claim and no V2 design. It may license a
  redesign only if the conflict is attributable to a named check.
- **VOID:** licenses nothing. The failed gate names what did not happen.

## What must be fixed before a runnable preregistration

1. **A revised design must name a different `S`.** A0 filled the table and returned `NOT
   IDENTIFIED`: candidate formation is `C`, admission is parallel, service is the same path, and
   assertion is downstream. The 2×2 does not become runnable as written. A two-path design or a new
   stage-level lever is required.
2. **The `S+` lever must be specified.** Raising a rank threshold, changing an admission priority
   and forcing a candidate are different interventions; the runnable record must choose one.
3. **The `C−` floor and `I3` tolerance must be fixed before any cell.** A blockade that also moves
   `S` is not a carrier manipulation.
4. **The assertion-blockade arm must be shown implementable without changing carrier formation.**
   If it is not, the design returns the weaker `CAUSAL VERSUS NON-CAUSAL ONLY` verdict.
5. **A fresh seed block, a materiality bar and a power calculation must be frozen.** No seeds are
   assigned here; assigning them before A0 would create a false appearance of readiness.
6. **An owner grant must be recorded.** This document is not a grant and no cell may run under it.

## What this does not establish

This is a design, not a result. It spends no seed, runs no cell and makes no causal, transfer,
capability or external-advantage claim. It does not authorise an engine change, a V2 build or a new
experimental block. The existing carrier enrichment remains an association until a runnable block
returns one of the verdicts above.
