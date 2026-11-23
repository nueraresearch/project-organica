# G9 activation design — criteria, stage ledger and experiment ladder

**Date:** 2026-11-14  
**Status:** `REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT`  
**Scope:** design only. No seed is assigned, no cell is authorised, no engine file changes, and no G9 layer is designed here. G9 remains locked.

**Naming:** G9 means **Generation 9**, not the emergence targets G1–G8 in `CHALLENGE.md`.

## 1. What this document decides

It defines **what evidence would make a G9 claim meaningful**, not what G9 should contain. Architecture is downstream of the criteria; a self-modeling layer is not evidence that self-modeling occurred.

The criteria are conjunctive. There is no partial-credit G9, and a strong result on one criterion cannot rescue a failed criterion. G9-D is necessary for a meaningful G9; this design also requires A, B and C.

The question is registered as **Q056**, blocked by Q054. The G8 → G9 progression gate remains **X1 — External activation** in [`DECISION-PROGRESSION-BEYOND-G8.md`](DECISION-PROGRESSION-BEYOND-G8.md).

## 2. G9 success criteria

### G9-A — Activation control

**Claim.** The system can reliably activate previously latent structures under identified conditions.

- **Population `L`.** A fixed set of structures that formed by a precommitted cycle and do **not** contribute to the baseline external readout. Membership is fixed before the intervention.
- **Intervention `I`.** A named, independently manipulable condition, with a paired control that differs only in `I`.
- **Measure.** `A` = the share of `L` that contributes to the external task readout, judged blind to condition. Report `ΔA = A_I − A_C`.
- **Pass.** `ΔA` clears a precommitted materiality bar on every seed; the sign replicates on an independent seed block; removing `I` returns activation to the control level.
- **Fail.** No change, a change that does not replicate, or a change that survives removal of `I`.

### G9-B — Development-dependent behaviour

**Claim.** Performance changes because developmental structure exists, not because the event stream alone changed.

- **Contrast.** Full developmental history versus a history-preserving ablation that removes the identified structures while holding exposure, world and cycles fixed.
- **Measure.** External endpoint difference between the two arms, with the same endpoint and baseline as X1.
- **Pass.** Removing the structures produces a measurable degradation on every seed, in the predicted direction, and the result replicates.
- **Fail.** No degradation, degradation in the wrong direction, or a difference explained by exposure rather than structure.

### G9-C — Self-modification of future development

**Claim.** Prior developmental state changes future developmental pathways beyond what raw event frequency predicts.

- **Measure.** Out-of-sample prediction of future stage transitions — formation, admission, service or assertion — from prior developmental state versus a frequency-only comparator.
- **Control.** A history-shuffled arm that preserves the marginal event distribution but destroys developmental order.
- **Pass.** The developmental-state model beats the frequency-only comparator on held-out cycles, and the advantage survives the history-shuffled control.
- **Fail.** No held-out advantage, an advantage explained by event frequency, or no difference from the shuffled-history arm.

### G9-D — External relevance

**Claim.** A development-linked mechanism affects an external endpoint.

- **Endpoint.** A task outcome external to internal counts, rank, coverage and assertion frequency. It is fixed before the run.
- **Contrast.** Mechanism present versus mechanism removed, with the same exposure and world.
- **Pass.** Presence raises the endpoint and removal lowers it; the ablation effect clears its precommitted bar and replicates.
- **Fail.** No endpoint effect, an effect that does not survive ablation, or an effect visible only in an internal metric.

**Decision rule.** G9 is eligible for a design decision only when **A, B, C and D all pass**. Any failure keeps G9 locked. A pass on A–D licenses a separate G9 design and owner decision; it does not authorise G9 implementation.

## 3. Stage ledger

The ledger replaces the overloaded word “selection” with observable transitions. It is an edge-level table, not an aggregate. Every world edge in the fixed candidate universe gets exactly one row.

### Columns

| Column | Meaning |
| --- | --- |
| `seed` | Fixed seed |
| `edge` | Directed world edge |
| `formed_cycle` | First cycle a candidate structure for the edge exists |
| `admitted_cycle` | First cycle the edge is eligible for service, before the cap |
| `served_cycle` | First cycle the edge enters a served window |
| `asserted_cycle` | First cycle the edge appears in the final structure |
| `carrier_cycle` | First cycle a carrier for the edge exists |
| `class` | One of the six classes below |

A missing stage is `null`, never `0`. A missing cycle is **not measurable at that stage**, not an early transition.

### Invariants

1. `(seed, edge)` is unique; every edge in the fixed universe has one row.
2. Every present cycle is an integer in `1..cycles`; no cycle is imputed from a later observation.
3. `formed_cycle` is present for every row.
4. `served_cycle` implies `admitted_cycle`; a served edge cannot be unadmitted.
5. `served_cycle >= admitted_cycle` and `asserted_cycle >= formed_cycle`; carrier timing may precede or follow formation.
6. No stage is inferred from an end-state stock: a final assertion cannot fill in a missing service cycle.

### Six classes, not four

| Class | Admitted | Served | Asserted | Reading |
| --- | --- | --- | --- | --- |
| **A** | yes | yes | yes | full path |
| **B** | yes | no | yes | admitted, never served, asserted |
| **C** | no | no | yes | carrier/alternate route to assertion |
| **D** | no | no | no | formed but never admitted or asserted |
| **E** | yes | no | no | admitted but latent |
| **F** | yes | yes | no | served but not asserted |

Classes E and F are required. A four-class table that stops at A–D would hide exactly the admitted-but-latent and served-but-not-asserted cases that motivate the activation question.

**Validator (2026-11-14).** [`G9-STAGE-LEDGER-VALIDATOR.md`](G9-STAGE-LEDGER-VALIDATOR.md) implements the six invariants and a synthetic fixture with one row in every class. It validates a ledger; it does not create one, run a cell, assign a seed or make a G9 result.

## 4. Experiment ladder

### Phase 1 — Map

Run the stage ledger on one fixed, fresh seed block and the fixed candidate universe. Report every row and the class counts per seed. The stage map is descriptive; it selects no mechanism.

**Gate to Phase 2.** All invariants pass, every class is reachable or its absence is explained by the world, and the map covers the full universe rather than only asserted edges.

### Phase 2 — Classify

Measure the transition boundaries between classes, not only their totals. The informative quantities are the first-cycle gaps: formation→admission, admission→service, service→assertion, and carrier→assertion. Report the full distribution and the per-seed values.

**Gate to Phase 3.** At least one stage boundary is manipulable through a named lever already established by A0/A1. If no stage is manipulable, stop: no intervention is designed from this map.

### Phase 3 — Intervene

Intervene once at the earliest identifiable stage, with a paired control. The precommitted success condition is that **at least one competing causal graph becomes untenable**. Another correlation does not satisfy the phase.

**Link to G9.** Phase 3 is an activation experiment, not a G9 demonstration. Its result feeds G9-A and X1; G9-B, C and D still require their own tests.

## 5. Stop conditions

- **One stage-map block.** If the ledger is incomplete, no Phase 2 or 3 is designed from it; a new block needs a new registered design.
- **One activation intervention.** If Phase 3 does not eliminate a competing graph, record `ACTIVATION NOT IDENTIFIED` and stop. Do not add another correlation, stage or instrument.
- **One G9 criteria evaluation.** A failed A/B/C/D closes G9 eligibility for the tested scope. Do not redefine the criterion after seeing the result.
- **G9 remains locked** until A–D pass and a separate G9 design is registered and authorised.

## 6. What this does not do

This is not evidence for activation, self-modeling, transfer or external advantage. It defines the measurements that would count. It assigns no seeds, runs no cells, changes no engine file and does not unlock Generation 9.
