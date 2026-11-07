study: decay-attribution confirmation
executions: 0
seeds: 20301201, 20301202, 20301203, 20301204, 20301205, 20301206, 20301207, 20301208, 20301209, 20301210, 20301211, 20301212
arms: engine, no_temporal_decay
artifact: docs/decay_attribution_study.json
questions: Q029, Q030, Q031, Q032, Q036
unassigned: Q033, Q034, Q035, Q037

# The decay-attribution replication — pre-registration

**Written before the run.** The machine-readable block above and sections 1–9 are the protocol;
section 10 is the outcome and is appended after the measurement. The runner must record the SHA-256
of sections 1–9 in its artifact, and the digest is pinned in
`benchmarks/decay_attribution_study_prereg.py`, so a later edit to the protocol cannot pass as the
one that was committed.

## 1. Scope, and the question numbers that do not exist

The request behind this protocol was to answer Q029–Q037 from one instrumented run. The registry does
not hold that range. It holds **Q029, Q030, Q031, Q032 and Q036**, all closed by the first
decay-attribution study on seeds 20300601–20300603, and it holds **no Q033, Q034, Q035 or Q037**.
Those four numbers are unassigned, and a protocol cannot pre-register an answer to a question that
has not been asked. They are named in the block above so the gap stays visible instead of being
filled by invention.

What this protocol can do is the thing a closed question still needs: an **independent replication**
on a seed block the first study never touched. The five questions keep their status; this study adds
or withholds confirmatory evidence.

- **Q029.** Why do the structures that reach 35 stable edges on a degree-12 hub disappear?
- **Q030.** Is the engine's temporal edge decay the mechanism that removes the structure?
- **Q031.** At which cycle does the degree-12 fall begin, and how long does it take?
- **Q032.** Do theories die before the edges, so that theory death causes the edge loss?
- **Q036.** What is the persistence half-life of the peak structure?

The first study's answers are recorded in `docs/decay_attribution.json` and
`docs/DECAY-ATTRIBUTION.md`: `TEMPORAL_EDGE_DECAY`, with the edges falling upstream of the theory
layer and the strength ratio's denominator growing while its numerator decays. This protocol does not
re-read those answers; it asks whether they survive twelve new seeds.

## 2. The instrument and the single run

One instrumented run: one invocation, one artifact, one analysis.

- **Runner.** `benchmarks/decay_attribution_study.py`, to be written after this protocol is
  committed. It reuses the first harness's world, ledger and death attribution but carries its own
  artifact path and seed block, so the first study's committed artifact and digest are not touched.
- **World.** `lattice_stream`, six triangles sharing hub `alpha` at degree 12; 60 world edges; 300
  cycles; shipped budget of 8 theories and 15 hypotheses; bootstrap of 12 events.
- **Arms.** `engine`, and `no_temporal_decay` with `TEMPORAL_DECAY_FACTOR = 1.0` and nothing else
  changed — an in-process ablation, never a shipped change.
- **Cells.** 2 arms x 12 seeds = **24**.
- **Output.** `docs/decay_attribution_study.json`, and a page rendered from it.

## 3. Seeds

**20301201 through 20301212**: twelve consecutive seeds, verified unused against every seed under
`docs/` at freeze time (2,609 seeds harvested, zero overlap). The runner must refuse to run if any
seed in the block appears under `docs/` outside its own record, and must record the block verbatim in
the artifact.

## 4. Quantities, and what counts as measurable

After every cycle the ledger records: stable edges, world hits, coverage, theories, beliefs, the
engine's strengthened / decayed / pruned counts, the temporal graph's sum, the number of temporal
edges at or above the engine's admission count, the largest temporal count, prediction candidates
emitted, edge deaths with a reason, the median stored strength of stable edges, the hub's tag
frequency, and the decay call's factor and row count.

- **Death shares** are shares of that seed's engine-arm deaths. A seed with zero deaths is reported
  **not measurable**, never 0 percent.
- **Half-life** is reported in cycles after the peak. It is **not measurable** when the peak is zero
  or the series never returns to half of it (rule 13b), and is never scored as zero.
- **Unexplained deaths** void that cell's attribution. They are an instrument defect, never a
  mechanism.

## 5. Controls and gates

- **G1, the perturbation happened** (rule 22): the engine arm records the decay call with factor 0.95
  and a non-zero row count every cycle, and the control records factor 1.0.
- **G2, the ceiling is reproduced**: peak stable count 35 and peak coverage 0.5833 in every engine
  seed.
- **G3, the collapse is visible**: the engine arm reaches 0 stable edges in at least 11 of 12 seeds.
- **G4, the contrast exists**: the control ends with at least 1 stable edge and never reaches 0 in at
  least 11 of 12 seeds.
- **G5, the attribution is complete**: unexplained deaths are 0 in every engine seed.
- **G6, the denominator exists**: deaths are greater than 0 in every engine seed whose peak is
  greater than 0.

A failure of **G1, G2, G5 or G6** makes the run `VOID_INSTRUMENT`: it has no verdict, per
`docs/DECISION-UNCERTIFIED-RUN.md`. A failure of **G3 or G4** is a scientific result
(`NOT_REPLICATED`), not a void — those gates are the claim, not the instrument. Keeping the two kinds
of failure apart is the point of splitting them here.

## 6. Pre-committed predictions, as replication targets

These restate the first study's measured values as the hypothesis to replicate. They are not new
predictions, and saying so is part of the protocol.

| Prediction | Condition | First study |
| --- | --- | --- |
| P1 | engine peak stable = 35 and peak coverage = 0.5833 in all 12 seeds | 35 and 0.5833 in all 3 |
| P2 | engine final stable = 0 in all 12 seeds | 0 in all 3 |
| P3 | first fall at or before the theory layer's last live cycle in at least 11 of 12 | fall at 16, last live theory cycle 28 |
| P4 | control ends with at least 1 stable edge and never reaches 0 in at least 11 of 12 | 30 edges, coverage 0.50, never 0 |
| P5 | `below_threshold` share between 25 and 40 percent in all 12 seeds | 31.03 percent per seed |
| P6 | half-life measurable and between 40 and 90 cycles after the peak in all 12 | 65 cycles after the peak (cycle 80) |

The bands in P5 and P6 are fixed wide on purpose: wide enough that seed-level wobble is not a
failure, narrow enough to exclude the original protocol's "at least half" claim (P5) and a series
that never recovers (P6). They are derived from the committed first study, not from this run.

## 7. Decision table

Committed before the run. Exactly one label is applied, and **a void takes precedence over every
scientific bucket**.

| Label | Condition | Decision |
| --- | --- | --- |
| `REPLICATED` | P1, P2, P5 and P6 hold in all 12 seeds, and P3 and P4 in at least 11 | the attribution is a property of the pinned engine on this world, not of three seeds; record confirmatory evidence on Q029, Q030, Q031, Q032 and Q036, and move the line to the repair question rather than running another attribution |
| `REPLICATED_WITH_SHIFT` | P1 and P2 hold and the control contrast holds, but P5 or P6 fails its band | the mechanism stands and its quantities are seed-sensitive; report distributions, and stop quoting 31.03 percent or 65 cycles as constants anywhere |
| `NOT_REPLICATED` | G3 or G4 fails, or P1 or P2 fails in 2 or more seeds | the first label was seed-specific; reopen Q029, Q030, Q031, Q032 and Q036 against this evidence rather than editing their answers, and treat the decay mechanism as not established |
| `VOID_INSTRUMENT` | G1, G2, G5 or G6 fails | no verdict; the run is void, the instrument is repaired first, and the five questions keep the evidence they already had |

## 8. What this cannot establish

- Twelve seeds test **seed sensitivity**, not new worlds, degrees or stimuli (rule 24b).
- Structural coverage only; it counts world edges asserted, not prediction quality.
- No repair arm: the candidate decay of x0.8 is unchanged in both arms.
- It cannot answer Q033, Q034, Q035 or Q037, because those questions are not registered.

## 9. Stop condition and freeze

The study is closed when the artifact exists, the page is generated from it, one label from section 7
is recorded with its conditions, and every death in the engine arm carries a named reason. No
instrumentation is added afterwards; a new question gets a new protocol.

Sections 1–9 are hashed and the digest is pinned in the guard. Changing any byte of the protocol
fails `--check`; a correction is a dated amendment appended to section 10, never an edit in place.

## 10. Outcome

**Not yet written.** The runner may not write this section until `docs/decay_attribution_study.json`
exists. Until then the protocol has not executed, and
`benchmarks.decay_attribution_study_prereg --check` asserts exactly that state.
