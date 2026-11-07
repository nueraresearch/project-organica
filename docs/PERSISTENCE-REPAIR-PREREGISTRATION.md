study: persistence repair by prediction budget and ranking
executions: 0
seeds: 20302101, 20302102, 20302103
arms: shipped, budget, ranking, both
artifact: docs/persistence_repair.json
question: Q045

# Does the readout lever reach persistence? — pre-registration

**Written before the run.** The machine-readable block above and sections 1–11 are the protocol;
section 12 is the outcome and is appended after the measurement. The runner records the SHA-256 of
sections 1–11 in its artifact, and the guard pins the same digest, so a later edit cannot pass as
the protocol that was committed.

## 1. The question, and why it is the next one

Q044 split every missed re-emission on the degree-12 hub and found a single gate: **1,920 of 1,920
misses were slot losses**, none were admission losses. The admitted candidate set was **54** against
**40** slots in each of the **284 binding cycles per seed**, so fourteen admitted candidates were
cut every cycle. That result names two levers — the **budget** and the **ranking** — and stops
there: it measures which gate an edge missed, not whether opening the gate extends anything.

The ranking lever has since been tested, but only at the coverage endpoint. The ordering block
returned `ORDERING SUPPORTED` with a mean coverage delta of **0.1615** (95 percent interval
[0.1094, 0.2031]) at the sparsest density, and the confirmatory block returned `ADOPT THE ADMISSION
RULE` with a mean gain of **0.171875** ([0.135417, 0.213542], 8 of 8 seeds positive). That rule is
diversity-first admission over the source side, with count as the tie-break. Its own record says
plainly: **coverage is not behaviour**, and which world edges a selection surfaces is not whether
surfacing them improves prediction, revision or retention. The budget route was measured out at the
same coverage endpoint — coverage needs **240–244** asserted edges, about **twelve times** the
budget, and precision never exceeded **0.3438** — but that is a coverage finding, not a persistence
finding.

The persistence side of the record points the other way. On this world the theory layer is last live
at cycle **28** and the stable-edge layer reaches zero at cycle **173**; **68.97 percent** of the
attributed edge deaths are `decayed`; and the death ledger found **0 capped theory removals** in the
reference arm on the falsifier's world, with supersession and parent loss accounting for the rest.
So the record predicts a dissociation: the readout lever should move which edges are selected, and
should not move when the theory layer dies.

**Q045.** Does raising the prediction budget or applying the adopted diversity-first ranking extend
theory-layer persistence on the degree-12 hub?

The two outcomes license different decisions:

- **an extension** means the readout lever reaches retention, and the budget or the adopted rule is
  a persistence lever as well as a coverage lever;
- **no extension** confines the readout lever to coverage, closes budget and ranking as persistence
  repairs on this world, and leaves decay and formation as the only live levers.

## 2. The world and the setting

The decay-attribution replication's world, unchanged: `lattice_stream`, six triangles sharing hub
`alpha` at degree **12**, **60** world edges, **300** cycles, **8** theories and **15** hypotheses,
a bootstrap of **12** events, and the shipped admission floor of **5**.

This is the world where both quantities are live. Q044 measured the cap binding and the theory
layer dying here, so a null cannot be blamed on an intervention that never fired. The falsifier's
`lattice_L1` world is deliberately out of scope: its candidate count against a cap of 40 has not
been measured, so a budget arm there could be an unrun experiment rather than a null.

## 3. The arms

A 2 x 2 design, four arms, one world and one seed block.

| Arm | Prediction cap | Selection |
| --- | --- | --- |
| `shipped` | 40 | the engine's own order: schema tier, then target entropy ascending, then transition probability descending, then temporal count descending, then source and target |
| `budget` | 320 | the engine's own order |
| `ranking` | 40 | the adopted diversity-first admission rule |
| `both` | 320 | the adopted diversity-first admission rule |

**The budget arm removes the cap; it is not an eight-times dose.** Q044 measured **54** admitted
candidates, so the realized budget is 54, not 320, and the expected change is from 40 selected to 54
selected. The cap of 320 is chosen to be above any measured candidate set, so the arm tests whether
the cap is a constraint at all. If the admitted set never exceeds 40, the arm did not fire and the
budget question is unmeasured (G2a).

**The ranking arm is the rule the project has already adopted, not a new ranking.** From
`docs/RANKING-ADMISSION-DESIGN.md` section 1: each slot takes the eligible candidate whose
left-hand tag has the fewest already-admitted outgoing edges, with count as the tie-break. The
deterministic tie-break used here is higher temporal count, then lower target entropy, then higher
transition probability, then source, then target. Eligibility is unchanged and includes
co-occurrence rows. The rule is applied over the whole eligible pool and replaces the engine's
stratified half-transitions, half-co-occurrences allocation, so the arm changes both the ordering
and the allocation. That is what adopting the rule would do; the label attributes an effect to the
policy, not to ordering alone.

The engine default is unchanged in 0.13.0. The adopted rule exists as a recorded decision and is
applied here in-process on a copy, which is the route the design's section 4 requires for a
cognition change: the frozen files are untouched and no re-pin is made.

The shipped cap of 40 clears the adopted rule's budget floor on this world, because the floor is the
number of eligible source tags and this six-triangle world has fewer than 40 tags. The ranking arm
therefore tests the rule rather than a floor failure.

There is no decay arm here. The decay repair is a separate pre-registration; mixing it into this
2 x 2 would confound the readout lever with the substrate.

## 4. The instrument

`benchmarks/persistence_repair.py`, one run, one artifact, in-process against the pinned 0.13.0
engine. The engine is unchanged; the observation is a subclass that records the engine's own
candidate list and selected set without altering what the engine returns.

The pre-slice candidate pool is observed the way Q044 observed it: the engine's builder is called
twice per cycle, once at the arm's real cap (the call whose result the engine uses) and once with
`MAX_PREDICTIONS` temporarily raised to **1,000,000**, whose side effects are discarded. The real
slice is reconstructed from the full list under the engine's own stratified rule and **must equal
the engine's actual selection on every cycle of every cell** (G3). A disagreement is a fidelity
failure and voids the run. For the two `ranking` arms the reconstruction is of the shipped slice;
the arm's own selection is the diversity-first policy, recorded separately.

Every cycle records: stable edges, world hits, coverage, theories, beliefs, strengthened, decayed and
pruned counts, emitted, admitted and selected counts, whether the budget bound, a digest of the
selected edge set, the decay call's factor and row count, and the theory count after the cycle.

**Persistence endpoint.** A theory count above zero is the falsifier's own definition of a live
theory layer. The death cycle is one past the last cycle with at least one theory, and 1 if the
layer never holds one. This is persistence of the **layer**, not of any particular theory: a layer
that replaces every theory each cycle still counts as live. That limitation is recorded in section
10 rather than repaired here, because changing the endpoint would make the result incomparable to
the falsifier and the ledger.

## 5. Seeds

**20302101, 20302102 and 20302103**, three consecutive seeds, checked against every seed under
`docs/` at freeze time and found unused. The runner refuses to start if any judged seed appears in
an artifact outside its own record.

The neutrality control uses **20301201**, the first seed of the committed decay-attribution
replication, and is not a judged cell. Reusing a control seed is deliberate: the control must
reproduce a series that is already committed, which a fresh seed cannot do.

## 6. The endpoint and the margin

**Primary.** For each arm and seed, the change is the arm's death cycle minus the `shipped` death
cycle on the same seed. An arm **extends** persistence when it gains at least **10 cycles** on at
least **2 of the 3** seeds; a single seed cannot carry the label, and the median is reported beside
the paired gains rather than used alone.

**Margin.** 10 cycles, reused unchanged from `docs/REFERENCE-DEATH-LEDGER-PREREGISTRATION.md`, where
it was fixed from the falsifier's **37-cycle** theory lifetime. It is deliberately not rescaled to
this world's 29-cycle death, so it is not computed from the run it judges (rule 19). On this world
it is about a third of the lifetime.

**Secondary.** Alive at cycle 300, final theory count, final stable edges, peak coverage, admitted
maximum, binding cycles, and the number of cycles on which the ranking arm's selected set differs
from shipped.

## 7. Gates

- **G1, the neutral observer.** The shipped arm at control seed 20301201 reproduces the committed
  decay-attribution engine series' theories and beliefs exactly, cycle for cycle.
- **G2a, the budget can fire.** The admitted candidate set exceeds 40 in at least one cycle of every
  judged seed. If it never does, the budget question is unmeasured, not null.
- **G2b, the ranking can fire.** The ranking arm's selected edge set differs from shipped in at
  least one cycle of every judged seed. If it never does, the ranking question is unmeasured.
- **G3, the instrument is faithful.** The reconstruction of the shipped slice equals the engine's
  actual selection on every cycle of every cell.
- **G4, the denominator exists.** Every cell has 300 cycles, and the shipped arm has at least 10
  cycles with a live theory layer.
- **G5, the seeds are fresh.** No judged seed appears under `docs/` outside this protocol.

G1, G3, G4 or G5 failing makes the run `VOID_INSTRUMENT`: no verdict. G2a and G2b failing are named
not-live outcomes, not voids, because one lever can be tested while the other is not.

## 8. Pre-committed predictions

These are predictions, not descriptions; each can fail.

| Prediction | Condition |
| --- | --- |
| P1 | the shipped arm dies at cycle 29 in all three judged seeds, reproducing the committed last-live cycle 28 |
| P2 | the budget lever is live: admitted exceeds 40 in at least one cycle of every seed |
| P3 | the ranking lever is live: the selected set differs from shipped in at least one cycle of every seed |
| P4 | neither single lever extends persistence by 10 cycles on 2 of 3 seeds, so the label is `NEITHER` |
| P5 | the ranking arm raises peak coverage above shipped in at least 2 of 3 seeds without extending the theory death |
| P6 | the budget arm raises final stable edges above shipped in at least 2 of 3 seeds without extending the theory death |

P4 is the substantive hypothesis: on this world the theory layer dies by decay and supersession, and
the slot gate that Q044 measured is a gate on the **edge** layer. P5 and P6 are the dissociation: if
the levers move coverage or stable edges and still do not move theory death, the readout lever is
confined to the edge layer.

## 9. Decision table

Committed before the run. Exactly one label is applied. A void takes precedence over every other
bucket; a not-live bucket takes precedence over the extension buckets for the lever it names.

| Label | Condition | Decision |
| --- | --- | --- |
| `VOID_INSTRUMENT` | G1, G3, G4 or G5 fails | no verdict; the instrument is repaired first and Q045 stays open |
| `BOTH_LEVERS_NOT_LIVE` | neither the cap nor the ranking changes the selection (G2a and G2b fail) | neither lever is expressible on this world; the question is unrun and no claim is made; move to a world where both can fire |
| `BUDGET_NOT_LIVE` | G2a fails, G2b passes | the budget question stays unmeasured on this world; report the ranking reading and do not infer anything about the cap |
| `RANKING_NOT_LIVE` | G2b fails, G2a passes | the ranking question stays unmeasured on this world; report the budget reading and do not infer anything about the adopted rule |
| `BOTH_EXTEND` | both single levers extend, and the combined arm also extends | the readout lever reaches retention through both routes; adopt the ranking rule as the default and keep the cap removal as a second, independent lever |
| `ANTAGONISTIC` | both single levers extend, but the combined arm does not | each lever helps alone and they interfere together; adopt one, not both, and record the interaction as the finding |
| `BUDGET_ONLY` | the budget arm extends and the ranking arm does not | the cap is the retention lever; adopt a larger budget for persistence, and record that the coverage finding that a larger budget buys noise does not generalize to retention |
| `RANKING_ONLY` | the ranking arm extends and the budget arm does not | the adopted rule is a retention lever as well as a coverage lever; wire it as the default through a recorded cognition decision and do not raise the budget |
| `INTERACTION_ONLY` | neither single lever extends, but the combined arm does | neither change is licensed alone; adopt both together and record that the effect is the combination, not either component |
| `NEITHER` | no arm extends by the margin | the readout lever is confined to coverage; persistence is not budget- or ranking-bound on this world, and the next lever is decay and formation |

## 10. What this cannot establish

- One world, one degree, one cap pair and three seeds. Three seeds test seed sensitivity, not new
  worlds (rule 24b).
- The endpoint is theory-layer presence, not theory identity. A layer that replaces its theories
  every cycle counts as live, and the run cannot distinguish retention of a theory from turnover
  inside a live layer.
- The ranking arm tests the adopted diversity-first rule as a whole policy. It changes both the
  ordering and the allocation, so an effect is attributable to the policy, not to the ordering
  alone.
- The budget arm removes the cap. With 54 admitted candidates the realized change is 40 to 54, not
  40 to 320, and the result says nothing about a budget larger than the candidate pool.
- Coverage and stable-edge gains are not prediction quality. No held-out task is scored here.
- There is no decay arm and no formation arm. A `NEITHER` label closes this readout question; it
  does not identify which substrate change would repair persistence.
- The falsifier's `lattice_L1` world is not tested, and its cap liveness is not established.

## 11. Stop condition and freeze

The study is closed when the artifact exists, the page is generated from it, one label from section
9 is recorded with its conditions, and every gate is reported. No instrumentation may be added
afterwards; a new question gets a new protocol. A correction is a dated amendment appended after
section 12, never an edit in place.

Sections 1–11 are hashed and pinned in `benchmarks/persistence_repair_prereg.py`. A one-byte edit to
the frozen text fails the guard.

## 12. Outcome

**Not yet written.** No cell has run, no artifact exists, and `executions` is 0. This section is
replaced only by the runner's recorded label and figures after the frozen protocol has executed.
