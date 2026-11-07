study: decay admission versus ranked slot
executions: 0
seeds: 20301601, 20301602, 20301603, 20301604, 20301605, 20301606, 20301607, 20301608
arms: engine, no_temporal_decay
artifact: docs/decay_admission_slot.json
question: Q044

# Admission count or ranked slot? — pre-registration

**Written before the run.** The machine-readable block above and sections 1–9 are the protocol;
section 10 is the outcome and is appended after the measurement. The runner records the SHA-256 of
sections 1–9 in its artifact, and the guard pins the same digest, so a later edit cannot pass as the
protocol that was committed.

## 1. The question, and why it is the next one

`docs/DECAY-ATTRIBUTION.md` closes with a disclosed limitation: of the engine-arm deaths **68.97
percent** were not re-emitted at all, so the engine's candidate decay took them below the storage
threshold — but that ledger cannot say *why* they were not re-emitted. There are two different
reasons an edge can miss re-emission, and they lead to different repairs:

- **admission loss** — the edge's temporal count fell below the engine's own admission floor,
  `PREDICTION_MIN_COUNT = 5`, so no candidate was ever built from it;
- **slot loss** — the edge cleared the admission floor and a candidate *was* built, but it lost one
  of the `MAX_PREDICTIONS = 40` slots to a better-ranked candidate.

The first is a decay/count problem. The second is a ranking or budget problem. The first study
attributed the deaths to candidate decay without separating them, which is exactly the gap this
protocol closes.

**Q044.** When a stable edge misses re-emission, is the cause the admission count or the ranked
slot?

## 2. The instrument

`benchmarks/decay_admission_slot.py`, one run, one artifact, run in-process against the pinned
0.13.0 engine. The engine is unchanged; the observation is a subclass that records the engine's own
candidate list without altering what the engine returns.

- **World and setting**: the first study's own — `lattice_stream`, six triangles sharing hub
  `alpha` at degree 12, 60 world edges, 300 cycles, 8 theories and 15 hypotheses, bootstrap of 12
  events, shipped admission floor and slot budget.
- **Arms**: `engine`, and `no_temporal_decay` with `TEMPORAL_DECAY_FACTOR = 1.0` and nothing else
  changed. The control answers whether the split depends on the decay the engine actually applies.
- **Cells**: 2 arms x 8 seeds = **16**.
- **Seeds**: **20301601 through 20301608**, verified unused against every seed under `docs/` at
  freeze time.
- **Output**: `docs/decay_admission_slot.json` and a page rendered from it.

### How the pre-slice list is observed without changing the engine

The engine ranks candidates and slices them inside one method. The instrument calls that method
twice per cycle: once normally, so the engine receives and uses its real 40 candidates, and once with
`MAX_PREDICTIONS` temporarily raised to a value larger than any candidate set, so the full ranked
list is observable. The raised call's side effects are discarded and the real call's are kept. The
real slice is then reconstructed from the full list with the engine's own stratified rule — half the
budget to transitions, then cooccurrences, then the remainder to further transitions — and **the
reconstruction must equal the engine's actual selection on every cycle**. A disagreement is a
fidelity failure and voids the run (G3).

Note the consequence for the names: "admission" here is the engine's `PREDICTION_MIN_COUNT` on the
temporal count, not the storage-level strength rule. A missed edge is classified against the
engine's own quantities, never a re-derived score.

## 3. Seeds

**20301601 through 20301608**: eight consecutive seeds, checked against every seed under `docs/` at
freeze time (the first study's block was 20300601–20300603, the replication's is
20301201–20301212, and neither overlaps this one). The runner refuses to start if any seed in the
block appears under `docs/` outside its own record.

## 4. Quantities

Every cycle records: stable edges, coverage, world hits, theories, beliefs, the engine's
strengthened/decayed/pruned counts, the temporal graph's sum and maximum, the number of edges at or
above the admission floor, the number of admitted candidates, the number of selected candidates,
whether the slot budget bound (admitted greater than the budget), and the decay call's factor and
row count.

A **miss** is an edge stable at the end of the previous cycle, not stable at the end of this cycle,
and **not re-emitted** this cycle. Each miss is classified into exactly one of:

| Class | Condition |
| --- | --- |
| `below_admission` | the edge was not an admitted candidate and its temporal count is below `PREDICTION_MIN_COUNT` |
| `slot_loss` | the edge was an admitted candidate and was not among the selected candidates |
| `unexplained` | neither: the edge cleared the floor and was still not built, or a re-emitted edge was misread as absent |
| `reemitted` | the edge was re-emitted; it is not a miss and leaves the denominator |

An `unexplained` miss voids that cell's attribution (G5). It is an instrument defect, never a class.

## 5. Controls and gates

- **G1, the perturbation happened** (rule 22): the engine arm records factor 0.95 with a non-zero row
  count every cycle, and the control records factor 1.0.
- **G2, the ceiling is reproduced**: peak stable count 35 and peak coverage 0.5833 in every engine
  seed.
- **G3, the instrument is faithful**: the reconstructed slice equals the engine's actual selection on
  every cycle of every cell.
- **G4, the denominator exists**: at least one miss in every engine seed.
- **G5, the attribution is complete**: zero `unexplained` misses in every cell.
- **G6, the slot can fire** (rule 25): the slot budget binds — admitted candidates exceed 40 — in at
  least one cycle of the run. If it never binds, slot loss is structurally impossible in this
  setting and that is reported as `SLOT_NEVER_BOUND`, not as zero.

G1, G2, G3, G4 or G5 failing makes the run `VOID_INSTRUMENT`: no verdict, per
`docs/DECISION-UNCERTIFIED-RUN.md`. G6 failing is a named outcome about reachability, not a void.

## 6. Pre-committed predictions

These are predictions, not descriptions; each can fail.

| Prediction | Condition |
| --- | --- |
| P1 | the engine arm reaches 0 stable edges in all 8 seeds |
| P2 | every miss is classified: zero `unexplained` in every cell |
| P3 | `below_admission` is the larger of the two classes in at least 6 of the 8 engine seeds |
| P4 | the slot budget binds in at least 6 of the 8 engine seeds |
| P5 | the reconstructed slice equals the engine's selection on every cycle of every cell |
| P6 | the control arm's `below_admission` share is lower than the engine arm's in at least 6 of 8 paired seeds |

P3 is the substantive hypothesis: the engine's temporal counts decay 5 percent per cycle while tag
frequencies do not, so an edge should fall under the admission floor before its rank matters. P6 is
its contrast: with decay disabled, admission loss should be rarer.

## 7. Decision table

Committed before the run. Exactly one label is applied; a void takes precedence over every other
bucket, and `SLOT_NEVER_BOUND` over the shares.

| Label | Condition | Decision |
| --- | --- | --- |
| `ADMISSION_DOMINANT` | `below_admission` is at least 60 percent of pooled misses and the majority class in at least 6 of 8 engine seeds | the admission count is the gate; the lever is the decay rule or the admission floor, and the ranking is exonerated for this world |
| `SLOT_DOMINANT` | `slot_loss` is at least 60 percent of pooled misses and the majority class in at least 6 of 8 engine seeds | the ranked slot is the gate; the lever is the ordering basis or the budget, and the decay rule is not the binding constraint |
| `MIXED` | neither class reaches 60 percent, or the pooled share and the seed majority disagree | both gates bind at different phases; the report must give the split early and late, and no single lever is licensed |
| `SLOT_NEVER_BOUND` | the budget never binds in any cycle (G6 fails) | the slot class cannot occur here; only the admission split is reported, and no claim about ranking is made in either direction |
| `VOID_INSTRUMENT` | G1, G2, G3, G4 or G5 fails | no verdict; the instrument is repaired first and the question stays open |

The 60 percent bar and the 6-of-8 seed majority are fixed here, before any cell, and are not computed
from the run (rule 19).

## 8. What this cannot establish

- One world, one degree, one admission floor, one slot budget. It separates two mechanisms in this
  setting, not in every setting.
- It measures which gate an edge missed, not whether raising either gate would repair persistence.
  That is the repair protocol's question.
- Eight seeds test seed sensitivity, not new worlds (rule 24b).
- It does not reopen the first study's label; it splits one of its reasons into two.

## 9. Stop condition and freeze

The study is closed when the artifact exists, the page is generated from it, one label from section 7
is recorded with its conditions, and every engine-arm miss is classified. No instrumentation is
added afterwards; a new question gets a new protocol.

Sections 1–9 are hashed and pinned in the guard. A correction is a dated amendment appended to
section 10, never an edit in place.

## 10. Outcome

**Not yet written.** The runner may not write this section until `docs/decay_admission_slot.json`
exists. Until then the protocol has not executed, and
`benchmarks.decay_admission_slot_prereg --check` asserts exactly that state.
