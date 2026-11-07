# Decay attribution on the degree-12 hub — pre-registration

**Written before the run.** Sections 1–7 are the protocol. Section 8 records what happened and is
appended after the measurement; sections 1–7 are not edited to match a result. The harness records
the SHA-256 of this file in its artifact, so a later edit to the protocol cannot pass as the one that
was committed.

## 1. The question

The theory-budget ceiling ends at zero: peak coverage **0.5833** (35 of 60 edges) and final coverage
**0.00**, identically at theory budgets 8/15, 16/30 and 64/128. Raising the budget moved neither
endpoint. That removes the budget as the explanation and leaves the disappearance itself as the
question this protocol asks:

- **Q029.** Why do the structures that reach 35 stable edges disappear?
- **Q030.** Is the engine's own decay the mechanism that removes them?
- **Q031.** At which cycle does the fall begin, and how long does it take?
- **Q032.** Do theories die before the edges, or after them?
- **Q036.** What is the persistence half-life of the peak structure?

Nothing here asks whether the death can be prevented, and nothing here changes the engine. The
question is what removes what is there, measured cycle by cycle.

## 2. The instrument

`benchmarks/decay_attribution.py`, run in-process against the pinned 0.13.0 engine.

- **World**: `lattice_stream` on six triangles sharing hub `alpha` at degree 12 — the ceiling
  harness's own generator, 60 world edges.
- **Setting**: 300 cycles per cell, shipped budget (8 theories / 15 hypotheses), bootstrap of 12
  events, the ceiling harness's own feed rule.
- **Seeds**: **20300601, 20300602, 20300603** (a fresh block, verified unused under `docs/`).
- **Cells**: 2 arms × 3 seeds = **6**.

### The ledger

After every cycle the harness records: stable edges (the storage-level strength rule the ceiling
measures), world hits, coverage, theories, beliefs, strengthened / decayed / pruned counts from the
engine's own natural-selection return, the temporal graph's sum, the number of temporal edges at or
above the engine's admission count, the largest temporal count, the number of prediction candidates
emitted, the number of edge deaths and the reason for each, the median stored strength of the stable
edges, the hub's tag frequency, and the decay call's factor and row count.

A **death** is an edge stable at the end of the previous cycle and not stable at the end of this one.
Each death is attributed with the engine's own quantities, not with a guess:

| Reason | Condition |
| --- | --- |
| `below_threshold` | the edge was re-emitted this cycle and its strength fell below `STABLE_THRESHOLD` (0.30) |
| `decayed` | the edge was not re-emitted, decayed by the engine's ×0.8, and landed below 0.30 but at or above `DEATH_THRESHOLD` (0.15) |
| `pruned` | the edge was not re-emitted and its ×0.8 fell below 0.15, so the engine wrote its death record |

An edge that is stable, re-emitted with strength at or above 0.30 and still not stored as stable is
counted as `unexplained` and reported as an instrument defect, never as a mechanism.

### The control

One causal control, because the engine's temporal graph decays **5% per cycle** while tag
frequencies never decay:

- **`engine`** — the shipped build.
- **`no_temporal_decay`** — the same build with `TEMPORAL_DECAY_FACTOR = 1.0` and nothing else
  changed. This is the arm that separates "the graph decay removes the edges" from "something else
  does". It is an in-process ablation, never a shipped change.

The harness records the decay call in both arms and refuses to interpret a run in which the
manipulation did not occur (rule 22): the engine arm must show factor 0.95 with a non-zero row
count each cycle, and the control must show factor 1.0.

The harness also re-checks the ceiling it is explaining: the engine's peak stable count must be
**35** (the ceiling artifact's `max_stable_edge_any_cell`). If it is not, the run is labelled
`CEILING_NOT_REPRODUCED` and no mechanism label is read from it.

## 3. Pre-committed predictions

Written before any cell was run, and falsifiable:

- **P1.** The engine arm's peak stable count is 35 and its peak coverage 0.5833 in all three seeds.
- **P2.** The engine arm's final stable count is 0 and its final coverage 0.00 in all three seeds.
- **P3.** The engine's first fall comes at or after the first cycle in which the theory layer reports
  zero — that is, theories die first or together with the edges, never after them.
- **P4.** The `no_temporal_decay` arm ends with at least 1 stable edge in at least two of three
  seeds, and its first fall, if it has one, is later than the engine's by at least **10** cycles.
- **P5.** At least half of the engine's edge deaths are attributed to `below_threshold` — the
  strength rule rejecting a re-emitted edge — rather than to `pruned`.

## 4. Decision table

Committed before the run; exactly one label is applied, and its consequences are fixed here.

| Label | Condition | Decision the label licenses |
| --- | --- | --- |
| `TEMPORAL_EDGE_DECAY` | engine collapses to 0; control ends with ≥ 1 stable edge and never falls to 0 | the graph's 5%/cycle decay is the removal mechanism; the next experiment belongs to the decay rule, not the theory budget |
| `TEMPORAL_EDGE_DECAY_PARTIAL` | engine collapses; control also falls but its first fall is ≥ 10 cycles later and it ends higher | decay contributes but does not account for the collapse; the remaining loss is a second mechanism to be named before it is attacked |
| `NOT_TEMPORAL_DECAY` | both arms fall within 10 cycles of each other and both end at 0 | temporal decay is not the killer; the strength rule or the frequency denominator is, and the next experiment moves there |
| `NO_COLLAPSE` | the engine does not reach 0 in 300 cycles | the instrument cannot see the recorded death; it is a defect and nothing is attributed |
| `CEILING_NOT_REPRODUCED` | engine peak stable ≠ 35 | the run is not the one the ceiling measured; no mechanism label is read from it |

The half-life is reported as a measured cycle count, and is reported as **not measurable** when the
peak is zero or the series never returns to half of it (rule 13b). It is never scored as zero.

## 5. What would count against this protocol

- The control collapsing as fast as the engine would kill the decay explanation, which is the point
  of running it.
- A first fall that comes before the theory layer dies would reverse P3 and make the edges the
  cause rather than the consequence.
- A death reason of `unexplained` would mean the ledger does not reproduce the engine's own
  decision, and the attribution would be void rather than reported.

## 6. What this cannot establish

- **One world, one degree, three seeds.** It attributes this collapse, not every collapse.
- **Structural coverage only.** It counts world edges asserted, not prediction quality.
- **No intervention on the candidate-decay rule.** The control changes the graph decay only; the
  ×0.8 candidate decay is unchanged in both arms, so its share is read from the reasons, not from a
  second arm.
- **It does not test whether persistence can be repaired.** That is a different protocol.

## 7. Stop condition

The build is closed when the artifact exists, the page is generated from it, and the ledger
attributes every engine-arm death to a named reason (or reports the unexplained count as a defect).
No further instrumentation is added to this harness afterwards; a new question gets a new protocol.

## 8. Outcome

The run is recorded in `docs/decay_attribution.json` and rendered in
`docs/DECAY-ATTRIBUTION.md`. The protocol sections above are identified by the SHA-256 the artifact
records; this section is written after the measurement.

**Verdict: `TEMPORAL_EDGE_DECAY`.** The control keeps its edges and the engine does not.

| Quantity | Engine | No temporal decay |
| --- | --- | --- |
| Peak stable edges (cycle) | 35 at cycle 15 | 42 at cycle 20 |
| First fall | cycle 16 | cycle 22 (a one-edge dip) |
| Half of the peak retained until | 65 cycles after the peak (cycle 80) | never reached |
| Stable edges reach zero | cycle 173 | never |
| Final stable edges / coverage | 0 / 0.00 | 30 / 0.50 |
| Edge deaths over 300 cycles | 348 per seed | 91 per seed |

**What removed them.** Of the 348 engine deaths per seed, **31.03%** were re-emitted with a
strength under 0.30, and **68.97%** were not re-emitted at all, so the engine's x0.8 candidate decay
took them below the threshold. Following only the 35 edges that made the peak (105 deaths across
three seeds), the shares are the same to within a point: 31.43% and 68.57%. All 35 are dead by the
final cycle, the last at cycle 79.

**The quantity that moves.** The stable edge's strength is `temporal_count / source_frequency`. The
median ratio among stable edges is **1.25** at the peak and **0.375** after it. Over the same run,
the hub's tag frequency grows from **88** to **1608** (18x) while the temporal graph's total grows
only from **726** to **1325** (1.8x): the denominator grows without any decay, the numerator
saturates under a 5% per-cycle loss, and the ratio falls until the strength rule and the re-emission
set both reject the edge.

**Predictions, scored.**

| Prediction | Outcome |
| --- | --- |
| P1 peak is 35 at 0.5833 | **held** in all three seeds |
| P2 final is zero | **held** in all three seeds |
| P3 edges fall at or after the theories die | **failed** -- the edges fall at cycle 16, the theory layer's last live cycle is 28 (zero at 29) |
| P4 control survives and falls 10+ cycles later | **failed** -- the control does survive and never reaches zero, but its first fall is at cycle 22, six cycles after the engine's, because its first fall is an early one-edge dip rather than a collapse |
| P5 at least half the deaths are the strength rule | **failed** -- 31.03%, because most deaths are the candidate decay that follows a missed re-emission |

P3 and P5 were written in the wrong direction, and both failures are informative rather than
inconvenient: the edges are upstream of the theory layer, and the strength rule is the smaller half
of the loss. The decision table's condition -- the control ending alive while the engine ends at
zero -- held in all three seeds, and that is the condition the label is read from.

**Disclosed limitation.** This ledger names the proximate reason for every death, and measures the
ratio and its two components. It does **not** separate the two reasons an admissible edge can miss
a re-emission: falling under the engine's admission count, or losing one of the 40 prediction slots
to a higher-ranked candidate. That separation is a new question, not a re-reading of this one.
