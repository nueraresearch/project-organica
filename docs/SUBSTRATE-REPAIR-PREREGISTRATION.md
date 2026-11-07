study: substrate repair across the six arms
executions: 0
seeds: 20302301, 20302302, 20302303
arms: FULL, SALIENCE, NO_CONTRADICTIONS, NO_QUESTIONS, NO_DREAMS, ANTI_EIG
conditions: shipped, repaired
artifact: docs/substrate_repair.json
question: Q046

# Does repairing the shared decay layer delay the cycle-39 death in every arm? — pre-registration

**Written before the run.** The machine-readable block above and sections 1–10 are the protocol;
section 11 is the outcome and is appended after the measurement. The runner records the SHA-256 of
sections 1–10 in its artifact, and the guard pins the same digest, so a later edit cannot pass as the
protocol that was committed.

## 1. The question, and why it is the next one

Q042 adjudicated reference-arm death as **shared**: on the falsifier's `lattice_L1` world, all six
force-matrix arms die at cycle **39**, and the reference is not a distinct failure mode. The route
differs — the reference's removals are supersession-dominated (102 of 126 events, 24 parent losses),
while each ablation is parent-loss dominated (249) — but the timing does not. The death ledger
changed which **retention policy** was in force and the death cycle did not move.

That leaves one untested reading of the shared label: if death is caused by the common
belief-formation and decay substrate rather than by any arm's policy, then a repair applied
**identically to every arm** should delay every arm. If only some arms move, the death is shared in
timing but not in cause, and the policy still matters.

**Q046.** Does repairing the shared temporal decay layer delay the cycle-39 death across all six
arms?

The two outcomes license different decisions:

- **all six delay** — the shared substrate is the lever; the arm policies are exonerated for this
  world, and the next question is how much decay repair persistence needs;
- **not all six delay** — death is shared in timing but the repair is arm-dependent; the substrate
  account is incomplete and the arm differences have to be explained before a common repair is
  adopted.

## 2. The world and the setting

The death ledger's own setting, unchanged: the falsifier's `lattice_L1` stimulus,
`lattice_stream(lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)["L1_hub1_t3_disjoint"]["triangles"])`,
**300** cycles, the six force-matrix arms, the shipped bootstrap and the shipped per-cycle feed.

This is the world where the cycle-39 death is established. The degree-12 hub is **not** used here:
its death cycle is 29, its candidate pool binds differently, and the question is specifically
whether the **shared** death in the six-arm ledger moves.

## 3. The repair

One change, applied identically to all six arms: the temporal-edge decay factor moves from **0.95 to
0.99**. The engine is unchanged; the repair is an in-process subclass that sets
`TEMPORAL_DECAY_FACTOR = 0.99`, the same composition the death ledger uses to observe the six arms.

What is deliberately **not** changed:

- no arm's retention policy, selection rule or question/dream/contradiction setting;
- no belief-formation rule, admission floor, strength threshold or theory cap;
- no candidate-decay factor and no budget.

The repair is therefore a **decay-rate** repair, not a belief-formation repair. The wording “shared
belief-formation and decay layer” in the question names the substrate the arms have in common; this
protocol tests its decay half only, and section 9 says so.

The no-decay arm is not used. Factor 1.0 is a diagnostic control, not a repair, and the question is
whether a **usable** setting short of disabling decay delays death.

## 4. Cells and seeds

Six arms × two conditions × three seeds = **36 cells**.

- **Conditions:** `shipped` (factor 0.95) and `repaired` (factor 0.99).
- **Arms:** `FULL`, `SALIENCE`, `NO_CONTRADICTIONS`, `NO_QUESTIONS`, `NO_DREAMS`, `ANTI_EIG`.
- **Seeds:** **20302301, 20302302, 20302303**, verified unused under `docs/` at freeze time.
- **Neutrality control:** the shipped `FULL` arm at seed **20261023** must reproduce the committed
  `docs/decay_falsifier/parts/FULL.json` theory and belief series exactly. This is the ledger's own
  control, and it is not a judged cell.

The runner writes one part per cell and refuses to assemble if any is missing or short.

## 5. The endpoint and the comparison

A theory count above zero is a live theory layer, the falsifier's own definition. The death cycle is
one past the last cycle with at least one theory, and **301** if the layer is still live at cycle 300.

For each arm and seed, the change is:

repaired death cycle − shipped death cycle on the same seed.

An arm **extends** when it gains at least **10 cycles** on at least **2 of the 3** seeds. The margin
is reused unchanged from the death ledger, where it was fixed from the falsifier's 37-cycle theory
lifetime; it is not computed from this run.

The primary label is about **all six arms**. The per-arm paired gains and their spread are reported
beside it. Secondary quantities: alive at cycle 300, theory cycles, final theory count, and the
reference arm's supersession and parent-loss counts.

## 6. Gates

- **G1, the neutral observer.** The shipped `FULL` arm at control seed 20261023 reproduces the
  committed falsifier theory and belief series exactly.
- **G2, the repair is live.** Every repaired cell records factor 0.99 with a non-zero decay row
  count in every cycle; every shipped cell records 0.95. A repair that did not apply is an unrun
  experiment, not a null.
- **G3, the baseline is the ledger's.** The shipped arm dies at cycle **39** in all six arms and all
  three seeds. If it does not, this is not the ledger's world and no repair comparison is read.
- **G4, the denominators exist.** Every cell has 300 cycles and at least one theory-bearing cycle.
- **G5, the seeds are fresh.** No judged seed appears under `docs/` outside this protocol.

G1, G4 or G5 failing is `VOID_INSTRUMENT`. G2 failing is `REPAIR_NOT_LIVE` and G3 failing is
`BASELINE_NOT_REPRODUCED`; neither is a scientific verdict about the repair.

## 7. Pre-committed predictions

| Prediction | Condition |
| --- | --- |
| P1 | the shipped arm dies at cycle 39 in all six arms and all three seeds |
| P2 | the repair applies: every repaired cell records factor 0.99 with non-zero decay rows in every cycle |
| P3 | all six arms extend by at least 10 cycles on at least 2 of 3 seeds, so the label is `SUBSTRATE_REPAIR` |
| P4 | the six repaired death cycles stay within 2 cycles of one another in at least 2 of 3 seeds |
| P5 | the repaired `FULL` arm records fewer parent-loss removals than the shipped `FULL` arm, pooled over seeds |

P3 is the substantive hypothesis: the shared substrate, not any arm's policy, is the cause. P4 is the
shared-timing prediction: a uniform repair should move the arms together, not scatter them. P5 is a
mechanism prediction: slower decay should protect the parents whose loss the ablations record.

## 8. Decision table

Committed before the run. Exactly one label is applied, in this order: a void, a not-live repair, a
failed baseline, then the scientific labels.

| Label | Condition | Decision |
| --- | --- | --- |
| `VOID_INSTRUMENT` | G1, G4 or G5 fails | no verdict; the instrument is repaired first and Q046 stays open |
| `REPAIR_NOT_LIVE` | G2 fails | the factor did not apply; the repair was not run and no claim is made in either direction |
| `BASELINE_NOT_REPRODUCED` | G3 fails | this is not the ledger's cycle-39 setting; no repair comparison is read and the baseline is repaired first |
| `SUBSTRATE_REPAIR` | all six arms extend by the margin | the shared decay layer is the lever across every policy; the arm policies are exonerated for this world and the substrate repair is the candidate |
| `PARTIAL_REPAIR` | one to five arms extend | the repair is arm-dependent; the shared account is incomplete and the arm differences are the next object |
| `NO_REPAIR` | no arm extends and no arm loses at least 10 cycles | the shared decay rate is not the lever on this world; death is common but not reached by this repair, and the next lever is belief formation or admission |
| `REPAIR_HARMS` | no arm extends and at least one arm loses at least 10 cycles | the repair shortens persistence in at least one policy; it is rejected rather than adopted and the harm is the finding |

## 9. What this cannot establish

- One world, one stimulus and three seeds. Three seeds test seed sensitivity, not new worlds.
- The repair changes the temporal decay **rate only**. It does not repair belief formation, the
  admission floor, the candidate-decay factor or the theory cap, and a null does not exonerate them.
- Theory presence is not theory identity. A layer that replaces its theories every cycle counts as
  live, and the endpoint cannot distinguish retention from turnover.
- The all-six criterion is a strong conjunction: a `PARTIAL_REPAIR` says the repair is not uniform,
  not that it failed in the arms that moved.
- No selection or ranking arm runs here. The persistence repair study covers that lever separately.
- The factor 0.99 is one point on the decay axis. A monotone dose-response is not established, and a
  larger or smaller repair could behave differently.

## 10. Stop condition and freeze

The study is closed when the artifact exists, the page is generated from it, one label from section 8
is recorded with its conditions, and every gate is reported. No instrumentation may be added
afterwards; a new question gets a new protocol. A correction is a dated amendment appended after
section 11, never an edit in place.

Sections 1–10 are hashed and pinned in `benchmarks/substrate_repair_prereg.py`. A one-byte edit to
the frozen text fails the guard.

## 11. Outcome

**Not yet written.** No cell has run, no artifact exists, and `executions` is 0. This section is
replaced only by the runner's recorded label and figures after the frozen protocol has executed.
