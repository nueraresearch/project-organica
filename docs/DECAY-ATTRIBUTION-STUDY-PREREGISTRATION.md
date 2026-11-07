study: decay-attribution confirmation
executions: 1
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

**Measured 2026-11-07: `REPLICATED`.** 24 cells (2 arms x 12 seeds, 20301201-20301212), 300
cycles each, degree 12. The artifact is `docs/decay_attribution_study.json`; the digest of sections
1-9 is `535a6241f2a66a5441ff17edbca1222340192f30208574bbefb98a4bdf0146b5`, and the section 11 amendment digest is
`f68208a512eb63d9115d07740377836c4df1a87c41308e119a4ab8f82fe51177`.

| Gate | Result |
| --- | --- |
| G1_perturbation_happened | pass |
| G2_ceiling_reproduced | pass |
| G3_collapse_visible | pass |
| G4_contrast_exists | pass |
| G5_attribution_complete | pass |
| G6_denominator_exists | pass |

| Prediction | Result |
| --- | --- |
| P1_ceiling | held |
| P2_final_zero | held |
| P3_fall_before_theory_death | held |
| P4_control_survives | held |
| P5_below_threshold_band | held |
| P6_half_life_band | held |
| P7_decayed_majority | held |
| P8_empty_core | held |

Each engine seed recorded peak **35** at cycle **15** with coverage
**0.5833**, first fall at cycle **16**, the theory layer last
live at cycle **28**, zero stable edges at cycle **173**,
a half-life of **65** cycles, **348** deaths of which
**0.3103** were `below_threshold` and **0.6897** were
`decayed`, and **0** peak edges surviving to the collapse. The control arm recorded
peak **42**, final **30**, no zero cycle, and **25** surviving
core edges.

**Secondary characterizations.** The core is empty (`FULL_COLLAPSE`); the first-zero cycle range
across the twelve engine seeds is **0** cycles (`COLLAPSE_SCHEDULED`);
candidate decay after a missed re-emission is the main loss (`DECAY_DOMINANT`, P7 held at
**0.6897** against the 50 percent bar). Q033, Q034 and Q037 remain `open`: these
labels characterize this world, and one world family at one degree is not their answer.

**All twelve engine cells were identical on every recorded quantity.** That is an observation about
this world and this schedule, not twelve independent confirmations: the seeds change the draw, but
the lattice hub's development is deterministic given the world. The replication's strength is
therefore that the three-seed values reproduce exactly on a seed block the first study never
touched, not that twelve draws agree.

**Instrument correction, recorded rather than hidden.** The guard's digest was originally computed
over the header block plus sections 1-9, so setting `executions` from 0 to 1 necessarily moved the
digest. The domain is now sections 1-9 only, which is what section 9 says is hashed. The section
bytes themselves are unchanged: the pre-run commit pinned the old value, and the new value is the
hash of the same sections with the header excluded. The amendment digest is unaffected.

The frozen table was applied once and not re-read: `REPLICATED` is the label its own conditions
select, and no band was moved.

## 11. Amendment — 2026-11-07: the four numbers are now named

The owner supplied the four question texts that section 1 recorded as unassigned, so they are now
registered as **Q033, Q034, Q035 and Q037**. This amendment was written **before any cell ran** —
`executions` is still 0 and the artifact does not exist — so it is pre-registration, not a re-reading.
It is dated and appended rather than edited into sections 1–9, which keep their committed digest; the
amendment's own text is pinned separately by SHA-256 in the guard.

| Id | Question | Carried by this run? |
| --- | --- | --- |
| Q033 | During collapse, is a stable core retained or does the whole structure collapse? | yes, criterion S1 |
| Q034 | Is the collapse deterministic or stochastic across seeds? | yes, criterion S2 |
| Q035 | Is persistence independent of the theory budget? | **no**, needs budget arms |
| Q037 | Which mechanism accounts for most of the loss? | yes, criterion S3 |

**Q035 is out of scope on purpose.** Budget independence is a claim about a manipulated variable, and
this run holds the budget fixed at 8 theories and 15 hypotheses by design (section 2). Answering it
requires its own protocol with at least three budgets — the ceiling study used 8/15, 16/30 and
64/128 — crossed with a seed block. Registering the question here without those arms would license a
claim this instrument cannot make.

### Added predictions, committed before the run

| Prediction | Condition | First study |
| --- | --- | --- |
| P7 | `decayed` — a missed re-emission followed by the engine's x0.8 — accounts for at least 50 percent of the engine arm's deaths in all 12 seeds | 68.97 percent |
| P8 | the core is empty at collapse: no edge stays stable continuously from the peak cycle to the first cycle with zero stable edges, in at least 11 of 12 seeds | all 35 peak edges dead, the last at cycle 79 |

### Secondary characterizations, each with its own decision

Read only when the run is not `VOID_INSTRUMENT`, and never used to move the primary label of
section 7.

| Label | Condition | Decision |
| --- | --- | --- |
| `CORE_SURVIVES` | P8 fails: one edge survives from peak to collapse in 2 or more seeds | persistence has a structural core, and the repair question starts from what keeps that core alive |
| `FULL_COLLAPSE` | P8 holds | there is no core to protect, so repair must act before the collapse rather than on a remnant |
| `COLLAPSE_SCHEDULED` | the range of the first-zero cycle across the 12 seeds is at most 2 cycles | the collapse time is a property of the schedule, so repair can be tested at a fixed cycle |
| `COLLAPSE_SEEDED` | that range is greater than 2 cycles | the collapse time is seed-driven, so repair must be evaluated per seed and reported as a distribution |
| `DECAY_DOMINANT` | P7 holds | Q037 is answered for this world: candidate decay after a missed re-emission is the main loss, and the admission set is the lever |
| `THRESHOLD_DOMINANT` | `below_threshold` is at least 50 percent in a majority of seeds | the strength rule is the main loss, and the admission threshold is the lever |

Q033, Q034 and Q037 stay `open` until the run writes section 10; this amendment does not answer them.
Q035 is registered and stays open with no protocol attached.
