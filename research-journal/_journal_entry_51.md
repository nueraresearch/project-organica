
---

## §51 — The endpoint did not test the claim; the benchmark was rebuilt; and the campaign stopped at its own gate

**What this section records.** A review of the acquisition pre-registration
found that its endpoint could not measure what the study claims to measure.
Every one of the five objections was checked against the code and the frozen
generator, and **every one was confirmed**. Two further defects were found
that the review did not raise. A third was found in the *redesign*, and it
changed the study's structure.

This is the same class of defect that killed earlier Organica hypotheses, one
level up. There, a *plan* used a metric (`DI`) that measured something else.
Here, a *plan* asked the world a question the world could not answer, and
would have scored the answer as though it did.

### What the review objected to, and what the measurements showed

**1. The task and the readout were measuring different things.** The frozen
generator draws each event's cause **independently** — the regime changes
which cause is *more common*, but consecutive events are not coupled. Measured
on the frozen world, holding the regime fixed:

| | P(next = same cause) | P(next = that cause) | difference |
|---|---|---|---|
| regime 0, `cause_a` | 0.7903 | 0.7761 | **+0.0142** |
| regime 0, `cause_b` | 0.1148 | 0.1375 | **−0.0227** |
| regime 1, `cause_a` | 0.1597 | 0.1342 | **+0.0254** |
| regime 1, `cause_b` | 0.7712 | 0.7668 | **+0.0044** |

So within a regime the causes are independent, to within 3 percentage points.
The apparent dependence in the raw numbers (0.6966 vs a 0.4551 marginal) is
**Simpson's paradox** — the shared regime block, not any coupling between
consecutive events. And the relation that the endpoint's gold set encodes
describes features co-occurring **within** one event: in the follow-up
window, a same-cause partner of the context appears in the next event only
**0.2969** of the time, while **0.3214** of next-event tags are carried over
from the context event itself. **A within-event relation does not predict the
next event.** The endpoint was asking the world a question the world never
asserted an answer to.

**2. F1 at a fixed 0.5 threshold is degenerate here — worse than suspected.**
The most common feature's next-event probability is about **0.38**. So a
*calibrated* model never crosses 0.5 and predicts nothing, while Organica's
edge readout emits hard 0/1. Scored on the frozen world's follow-up window:

| model | F1@0.5 | Brier |
|---|---|---|
| calibrated (knows the true law) | **0.0000** | 0.1080 |
| frozen-at-acquisition marginal | 0.0000 | 0.1591 |
| hard graph readout, one direction | 0.3703 | 0.1961 |
| hard graph readout, symmetric | 0.3963 | 0.2353 |
| constant zero | **0.0000** | 0.1397 |

**The Bayes-optimal model scores exactly what the trivial model scores.**
F1 at 0.5 was measuring *threshold behavior*, not knowledge quality. The
reviewer's phrasing — that F1 might compare threshold behavior rather than
learning quality — is confirmed without qualification, and the endpoint was
unusable as specified.

**3. The readout was directed; the target relation was not.**
`edges_implied_by_structures` adds concept and phrase member pairs in **one
list direction** (`for i, a in enumerate(members): for b in members[i+1:]`).
The gold same-cause pairs are **undirected**. On the frozen world, **10 of 12**
gold pairs appeared in exactly one direction — the direction is the order the
tags happened to land in the event text, not a property of the relation.

**4. The "fixed-rule ceiling" was not a prediction ceiling.** Knowing the gold
same-cause pair set tells you which features co-occur *within* an event. It
does not tell you the conditional distribution of the *next* event, which
needs the regime and the cause frequencies. The generator's marginal for a
dominant-cause tag in the follow-up regime is **0.3825**, and the gold pair
set carries **no** frequency information at all. The ceiling was a **relation
oracle** being used as a **prediction ceiling**.

**5. Retention and transfer were one number with two names.** The 110–149
window is labelled RETENTION in the phase table and is also used as TRANSFER
in the prose, while the study-level rule gates on them separately. A frozen
state scored before the switch and the same state scored after it are
**different numbers** (measured Brier **0.1583** pre-switch vs **0.1081**
post-switch), and the design only had the second one. A failure would have
been undiagnosable: it could not have distinguished "did not retain" from
"did not transfer".

### Two further defects the review did not raise

**6. The frozen engine never forms a group concept in that world.** Reading
the source: `_find_communities` is connected components on the co-occurrence
graph, and `_build_concepts` makes one concept per component, and
`edges_implied_by_structures` asserts **every pair** among a concept's
members — so a concept *would* generalize to pairs never directly
co-observed. But `_classify` requires a concept to have
`degree >= 4 and clustering <= 0.4 and predictive_reach >= 4`, and a group
defined *by* co-occurrence has **clustering 1.000** — the opposite of what
the concept rule asks for. Measured over the frozen world's 12 tags: **all
twelve classify as `unclassified`; zero concepts form.** The engine's
taxonomy has no category for "tight group". A feature sweep confirmed it is
not a threshold-tuning accident:

| features per cause | co-occurrence degree | concepts formed | relation F1 |
|---|---|---|---|
| 4 (the frozen world) | 3.0 | **0** | 0.3158 |
| 5 | 3.7 | **0** | 0.5714 |
| 6 | 4.5 | **0** | 0.5600 |
| 8 | 6.2 | **0** | 0.4444 |

Above the degree threshold and still zero concepts, because clustering stays
at 1.0. And the readout's edges came overwhelmingly from **3,604
`loop_candidate`s** and **0** concept candidates — so the graph being scored
was a **temporal adjacency** graph, not a group-relation graph. The endpoint
was asking about group structure and the readout was supplying sequence
structure.

**7. The generator's regime switch is relation-invariant.** The gold
same-cause pair set is **identical in both regimes** — the same causes, the
same feature sets; only which cause is *dominant* changes. So a
relation-scored endpoint **cannot** distinguish pre-switch from post-switch by
itself, and the transfer limb would have to be scored on a different
observable than the relation set. The world and the endpoint were pulling in
different directions.

### Three measurements that superseded the first redesign

The first redesign built a law-governed transition world and a new endpoint.
Three later measurements changed what that world could be used for. The
numbers below replace an earlier, pre-alignment set (a "ceiling" of 0.3382 /
0.3146) that no longer describes the instrument.

**A. The metric's shape, not just its threshold.** The house scoring rule
excludes `target == source`. With that exclusion the base rate is
**0.329263**; without it, **0.402159** — while the ceiling barely moves
(**0.224231** to **0.230751**). So the exclusion **shrinks the baseline's
handicap** while leaving the target nearly untouched. Measured headroom
against the base rate is **0.171408** in the self-cells shape and
**0.105032** in the house shape. The exclusion is not cosmetic; it decides
how much room the study appears to have.

**B. The readout was the limiter, not the organism.** The same frozen
structures (3,996 candidates, 10 of 16 vocabulary tags present) were scored
two ways:

| readout | house shape | self-cells shape |
|---|---|---|
| ad-hoc (0.9 for a neighbour, ~0.1/k) | 1.302721 | **1.655377** |
| base rate | 0.329263 | 0.402159 |
| backoff-smoothed graph, alpha 2.0 on a **tuning split** | **0.277761** — 0.9784 of span | **0.362233** — 0.9592 of span |
| ceiling (knows the law) | 0.224231 | 0.230751 |

The ad-hoc readout scores **worse than the base rate**; the backoff-smoothed
readout on the *same structures* reaches 0.9784 of the achievable span. Two
earlier readings of this comparison — −0.579, and then 0.940 — were
superseded; the committed artifact records 0.277761 against a 0.224231
ceiling. **The readout was the limiter.** And a readout that can turn 0.2778
into 1.3027 without the structures changing is an instrument defect, because a
scoring defect is indistinguishable from a learning failure.

**C. The redesigned world's law is first-order Markov — so counting and
understanding were not separable.** Against the strongest simple baselines,
all selected on a tuning split:

| predictor | log-loss (house shape, retention) |
|---|---|
| ceiling (knows the law) | 0.224231 |
| cell counter (strongest baseline) | 0.229878 |
| tuned bigram / decayed bigram | 0.240949 / 0.240949 |
| base rate | 0.329263 |
| grouping oracle (knows only which group it is in) | 0.252139 |
| first-order Markov on raw rows | 0.251693 |
| trivial | 2.706801 |

Headroom over the base rate is **0.105032** and would have passed the probe's
own 0.05-nat bar. Headroom over the **strongest** baseline is **0.005647**,
and would not. A plain bigram sits **0.027462** from the ceiling. The
grouping oracle alone captures **0.8679** of the span.

**The world's law *is* first-order Markov, so a bigram table is its natural
learner: "understood the law" and "counted transitions" are not separable by
a next-event score alone.** That world was therefore reclassified
**CALIBRATION / CONTROL**, not a generalization benchmark.

### The compositional task — a benchmark that can fail

A new task was built to measure what the transition world could not:
generalization to a **withheld combination** of familiar elements. Four
cells in a 2 × 2 grid of two latent factors, 4 tags each (16 total); the law
is that the successor cell differs in exactly one factor (flip-P 0.65 /
flip-Q 0.35, rotating at the regime switch); the tag-to-cell mapping is
**randomised per world**. One held cell per world has its flip-P transitions
removed **from the training stream only** — the held cell's tags remain
visible as contexts (155–202 context events per world), so the withheld thing
is a *combination*, not a tag.

Thirty independent worlds, seeds 20261200–20261229, all checks pass:

| gate | what it establishes | measured |
|---|---|---|
| **G1** | the ceiling beats the **strongest** simple baseline, with the **lower** uncertainty bound clearing 0.05 nats | gap **+0.1035**, 99 % interval **[+0.0996, +0.1074]**; binding baseline bigram in **23 / 30** worlds, cell counter in **7** |
| **G2** | a positive control holding the rule reaches the ceiling | exact |
| **G3** | a broken-rule control is clearly worse | ≥ **+0.1015** worse |
| **G4 / G4b / G4c / G4d** | the withheld combination is genuinely absent from training; the held cell is still observed; every flagged event is excluded; the split is not empty | all pass |
| **G5** | monotone in structure: ceiling < cell counter < base rate | every world |
| **G6** | the held cell varies across worlds | 4 distinct held cells |
| **G7** | **the withheld combination is what creates the gap** | held-cell **+0.1963** [+0.1901, +0.2033] vs other cells **+0.0425** [+0.0411, +0.0444] — **4.6×** |

**G7 is the load-bearing gate.** Without it, G1 could be passing because of
generic estimation error. With it, the headroom is demonstrably
*generalization* headroom on the withheld combination specifically.

A sensitivity, reported and not gated: a control with the right structure but
the two transition weights swapped is only **+0.0307** worse [+0.0283,
+0.0332]. The endpoint resolves the law's **structure** sharply and its
**weights** only weakly — a resolution fact that bounds what any result on
this task may claim.

> **The +0.1035 is the benchmark's headroom, not an Organica margin.** The
> compositional probe runs **no engine** and scores no learner. It answers
> *"is there room for something better than transition counting?"* — yes.

### The acquisition gate — where the campaign stopped

The instrument gate passed; the organism-side gate did not.

| seed | asserted structure coverage | raw temporal coverage | verdict |
|---|---|---|---|
| `20261100` (exploratory) | 0 / 112 = **0.0 %** | 112 / 112 = **100 %** | FAIL |
| `20261101`–`20261105` (diagnostic) | **0.0 % – 2.7 %** (0–3 of 112) | 112 / 112 = **100 %** | FAIL |

The world **is** in memory; the organism did not **assert** it. The cause is
one named bound: `_build_predictions` sorts candidates by raw temporal count
and truncates at `MAX_PREDICTIONS = 20`, and on this stimulus the two tags of
a cell co-occur in every event of that cell, so within-cell pairs
out-count the cross-cell transitions that carry the law and take all 20 slots.
The counterfactual audit confirmed the split: on seed `20261101` the 22
asserted `prediction_candidate` edges were 22 intra-cell and 0 inter-cell,
with **0 / 112** world overlap.

**The treatment is decisive.** Raising **only** the cap to 1,000 — same
engine, same observation stream, same five seeds, every other constant
identical — gives **98.2 %–100 %** coverage and clears the gate every time.
The failure is a **capacity limit**, not a missing signal and not a readout
defect. Downstream selection does not discard the cross-cell predictions
once admitted: they survive natural selection and decay across 110 cycles.

**Organica's readout lost.** Pilot 0, seed `20261100`, with identical raw
exposure for every learner:

| learner | retention | transfer | revision |
|---|---|---|---|
| **Organica** | **0.453018** | 0.453912 | 0.463372 |
| Replay | 0.347521 | 0.349592 | 0.351989 |
| Statistical | 0.347273 | 0.350723 | 0.352194 |
| base rate | 0.409581 | 0.409511 | 0.406124 |
| Bayes ceiling | 0.276259 | 0.272365 | 0.275176 |

Organica scored **worse than the baselines did after their episodes were
deleted** (the 0.403045 floor those cells collapse to). That is coherent
with the cause rather than surprising: the asserted structure is mostly
within-cell co-occurrence, so the readout answers *which cell the context is
in* when the task asks *which cell comes next*.

**Transfer was not measured, and it is not a transfer failure.** A seed that
fails acquisition is reported `acquisition_failed`, and transfer is reported
as not measurable. The campaign stopped at the gate; the 600-cell factorial
did not run.

### An instrument defect found while reconciling the two results

Two different functions implemented "Gate 13" under one name. The runner
evaluated the **asserted** basis, as the pre-registration's Amendment 1
requires, and failed correctly. The harness evaluated the **raw temporal**
basis, returned **100 %**, and passed — on the same seed, on the same world.
Its test asserted `passed is True`.

So the harness contained a gate that **could not fire** on the very condition
the study exists to detect. A check that cannot fire is decoration; a gate
that passes while the protocol's gate of the same name fails is worse than
decoration, because it authorises a study the protocol says is not
measurable.

**Fixed.** The harness now computes both figures, gates on the asserted one,
records `coverage_basis = "asserted_structure"`, and exposes the cap-raised
treatment so the failure can be *attributed* rather than merely observed.
The test was rewritten so that the "normal run" expectation for Gate 13 is a
**failure**, the treatment arm is asserted to **pass**, and the aggregate
prerequisite check is asserted to report the gate-13 failure at the
preregistered threshold.

### One bookkeeping consequence, recorded rather than rewritten

The pre-registration's Amendment 2 defined the confirmatory sample as thirty
seeds, `20261101` through `20261130`. Amendment 3 then designated
`20261101`–`20261105` as diagnostic preflight seeds. **Five of the thirty
confirmatory seeds are now diagnostic**, leaving a usable confirmatory sample
of **25**. The frozen amendment text is not rewritten; the consequence is
recorded here, and any future campaign must re-specify its seed set rather
than inherit one that has been partly spent.

### The lessons

**1. A benchmark must be able to fail, and so must the question it asks.** A
pre-registration can pin the seeds, the sample size, the cell matrix and the
decision rule with perfect care and still be measuring nothing — because the
*world* and the *endpoint* were never checked against each other.

**2. Run the perfect model *and the strongest simple model*, and require the
lower uncertainty bound of the gap across independent worlds.** The first
lesson was "run the perfect model and the trivial model". That was not
enough: the perfect-versus-trivial check **passed** on a world where a bigram
table was within 0.0275 nats of the ceiling. A base rate is the weakest
possible comparator. The gate that would have caught the real problem is
cheap — one more baseline over a declared grid, and a bootstrap over worlds
instead of a single number.

**3. The metric choice and the readout choice are not separable.** A hard 0/1
readout loses to the base rate under log-loss even when it holds the world's
exact edge set. Only a proper scoring rule with a soft, tuning-split-calibrated
readout can measure anything — and the readout has to be proved against the
construct *before* it is used to diagnose a learner.

**4. A grading-only control is not a control set.** "Knows the grouping"
reaches 0.87 of the achievable span. The headroom must be measured against
the strongest comparator, and the strongest comparator is often something
nobody named in the protocol.

**5. A benchmark's headroom is not a learner's margin.** The compositional
probe's +0.1035 nats is the room between the ceiling and the best simple
model. It is not what any learner achieved. Two numbers on the same task
answering two different questions are not a contradiction, and reading one as
the other is how a task-validity result gets reported as a capability result.

**6. Two gates can share a name and disagree.** The harness's Gate 13 and the
protocol's Gate 13 returned 100 % and 0.0 % on the same seed. The difference
between the two figures *was* the finding. A named gate that is implemented
twice has to be reconciled against the protocol, not against the first
implementation found.

This is the same lesson as the `DI` endpoint defect, one level up: there, a
metric imported from another study measured a different quantity; here, a
metric from the house scoring code measured a different quantity than the
claim, on a world that could not supply the quantity at all. **The endpoint
is part of the hypothesis, and it is the part that most often goes unchecked.**
