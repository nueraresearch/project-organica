# The acquisition endpoint audit — what was wrong, and what was measured

**Status: AUDIT RECORD.** This document records the audit that produced
[`ACQUISITION-EXPERIMENT-PREREGISTRATION.md`](ACQUISITION-EXPERIMENT-PREREGISTRATION.md)
**Revision 3**, and it is committed **before** any acquisition cell is run.

It exists because the project's own rule is that **corrections are documented,
not quietly applied** — and because a benchmark that was wrong in five
different ways at once deserves a record of how each was found, so the next
one can be recognized faster.

> ### The origin
>
> On 2026-10-26 the owner reviewed Revision 2 and raised a **fundamental
> methodological** objection, not a wording one: *does the benchmark actually
> measure the thing it claims?* His framing: the desirable property is
> **abstraction → transfer → revision**, not "event_t predicts event_t+1"
> *unless that sequence prediction is intrinsic to the world*. His direction
> was: **pause acquisition; resolve the task-to-readout mapping; prove the
> benchmark measures reusable knowledge; then run it.**
>
> Every one of his objections was verified as correct against the code. Two
> further defects were found that the review did not raise. A third was found
> in the *redesign* — and it is the one that changed the study's structure.

---

## 1. The five objections, verified

Each was checked against the code and, where the claim was quantitative,
measured. None was dismissed.

### 1.1 The task and the readout did not match — **CONFIRMED**

`organica/ground_truth_worlds.py::generate_cause_world` draws each event's
cause **independently**. The gold relation is `gold_same_cause_pairs` — the
feature pairs that co-occur **within one event** because they share a latent
cause. The endpoint, however, scored whether tags in event *t* predict tags
in event *t+1*.

**Measured.** Within a regime, P(causeₜ₊₁ = c | causeₜ = c) differs from
P(causeₜ₊₁ = c) by **at most 0.03**. The events are independent given the
regime, so a within-event relation does not predict the next event.

The apparent dependence in the marginals (0.6966 vs 0.4551) is **Simpson's
paradox**: a shared regime block, not a causal link. A same-cause partner
appears in the next event only **0.2969** of the time, and **0.3214** of
next-event tags are carried from the context event itself.

**Consequence.** A win or a loss on this world would have mostly reflected
how the readout handled changing tag frequencies, not whether the learned
structure was reusable knowledge. **A study may not ask a question its world
cannot answer.**

### 1.2 F1 at a 0.5 threshold was degenerate — **CONFIRMED**

The most common feature's next-event probability is only about 0.38 under
the specified noise and cause rates. A calibrated probability model therefore
predicts **no positives at the fixed threshold**, while Organica's edge
readout emits hard 0/1 predictions.

**Measured.** The **Bayes-optimal calibrated model scores F1 = 0.0000 —
identical to the trivial model.** The hard 0/1 readout scores 0.3703 (one
direction) / 0.3963 (symmetric). F1 was measuring **threshold behavior, not
knowledge quality**.

**Consequence.** Log-loss becomes the primary metric, and F1 is demoted to a
reported diagnostic.

### 1.3 The projection was directional; the target relation was not — **CONFIRMED**

`benchmarks/ablation_metrics.py` → `edges_implied_by_structures` adds concept
and phrase member pairs in **one list direction**:

```python
for i, a in enumerate(members):
    for b in members[i+1:]:
```

The study used that graph for **directed** next-event predictions, while the
gold pairs were **undirected** same-cause pairs.

**Measured.** **10 of 12** gold pairs appeared in exactly **one** direction —
because the order tags landed in the event text.

**Consequence.** The readout's mapping to the endpoint is now stated
explicitly, and the endpoint is scored on the **observed next event**, so no
undirected relation is read in a directed way.

### 1.4 The "fixed-rule ceiling" was a relation oracle — **CONFIRMED**

The gold pair set carries **no frequency information**. The dominant tag's
follow-up probability is **0.3825**. A relation oracle was being used as a
**prediction** ceiling — a category error, since a relation oracle cannot
score a prediction without the conditional distribution.

**Consequence.** The ceiling is derived from the generator's **full
conditional distribution**, in closed form, and is checked against the
generator empirically (the closed-form conditional must track the generator
to within 0.15 in every well-populated cell).

### 1.5 Retention and transfer were conflated — **CONFIRMED**

The 110–149 window was labelled RETENTION, the same score was also used as
TRANSFER under the switched regime, and the study-level rule then treated
transfer and retention as separate gates. **One window, two labels, two
gates.**

**Measured.** Pre-switch and post-switch are genuinely different numbers
(log-loss 0.1583 vs 0.1081 on the old world) — which is exactly why one
window cannot be both.

**Consequence.** The three limbs have **three windows under three laws**,
and the revision limb is scored on a **separate held-out test** rather than
on the window it was learned in.

---

## 2. Two further defects, found during the audit

These were not in the owner's review. They are recorded because a record that
only contains the objections that were raised is a record of the review, not
of the work.

### 2.1 The frozen engine never forms a group concept in that world

`organica/sleep.py::_classify` assigns mutually exclusive categories. A
`concept` requires `degree >= 4 AND clustering <= 0.4 AND predictive_reach
>= 4`; a `phrase_fragment` requires `clustering >= 0.7 AND reach <= 2`.

**A group defined *by* co-occurrence has clustering 1.000** — the opposite of
what a concept requires — and with 8 co-occurring tags it has reach 8, so it
is not a phrase fragment either. It falls through to `unclassified`.

**Measured.** All **12** tags classified `unclassified`; **0** concepts formed
at 4, 5, 6 and 8 features per cause. A feature sweep showed degree rising
3.0 → 6.2 while concepts stayed at 0 throughout, and relation F1 of
0.3158 / 0.5714 / 0.5600 / 0.4444 across the sweep.

**This is a standing constraint on the interpretation of any result** — see
§5.

### 2.2 The generator's regime switch was relation-invariant

`gold_same_cause_pairs` is **identical** in both regimes; only the dominance
changes. A relation-scored endpoint therefore **could not distinguish
pre-switch from post-switch**: the gold pairs are the same either way.

**Consequence.** The redesigned world's law **rotates** at the switch, so
revision has something to revise, and the revision limb is measurable.

---

## 3. The readout corrections, kept visible

Two corrections were made to my own readout. Both are recorded rather than
quietly applied.

| # | The reading | Why it was wrong | Corrected reading |
|---|---|---|---|
| 1 | Structures capture **−0.579** of the achievable log-loss span — worse than predicting nothing. | The read was **partial** (only `prediction_candidate` edges) **and over-confident** (hard 0/1). A confident wrong answer costs ~7 nats under log-loss, so a partial, over-confident read can be worse than no read at all. | With **all six structure types** and a **soft** readout, the same structures capture **0.940** of the span. |
| 2 | The ad-hoc soft readout scores **1.6554** against a base rate of **0.3293** — the organism's structures look useless. | The readout's constants (0.9 for a graph neighbour, ~0.1/k otherwise) were arbitrary and uncalibrated. The "worse than the base rate" result was **the readout's**, not the organism's. | With a **backoff-smoothed** readout, `p(b|a) = (w(a,b) + α·m(b)) / (W(a) + α)`, and α chosen on a **tuning split**, the same structures reach **0.2778** — **0.978 of the achievable span** — beating the base rate without reaching the grouping oracle (0.2521) or the ceiling (0.2242). |

**The lesson this earns, and it is the reason the readout is pinned at all:**
*the readout is part of the hypothesis, and it is the part that was going
unchecked.* A benchmark whose readout is arbitrary will report the readout's
constants as a finding about the organism.

**A related correction, this time in the metric's shape.** The house `_score`
shape sets `y = int(target in truth and target != source)`, skipping the
self-cell. On the redesigned world the law **prefers** the same group, so
self-recurrence is law-governed, not noise.

**Measured.** With the exclusion, the base rate scores **0.3293**; without it,
**0.4022**, while the ceiling barely moves (0.2242 → 0.2308). The exclusion
therefore **discards real signal** — 276 of 10,208 cells — **and flatters the
baseline**, shrinking measured headroom from 0.1714 to 0.1050.

**Consequence.** Both shapes are reported; the house shape is primary for
comparability, the self-cell shape is co-primary, and a verdict that differs
between them is reported as differing.

---

## 4. The defect that changed the study's structure

The redesign was validated by a committed probe. The probe passed. **And the
benchmark was still unable to separate "understood the law" from "counted
transitions."**

### 4.1 What the probe checked, and what it missed

The probe's headroom check compared the Bayes ceiling against a **base-rate**
predictor. A base rate is the weakest possible comparator. Measured against
the **strongest** count-based baselines — each swept over a declared grid and
selected on the tuning split — the picture changes:

| Model (retention window, house shape) | log-loss |
|---|---|
| ceiling — knows the law | **0.2242** |
| copy-context — knows only *which group* it is in | 0.2521 |
| cell-level counter — a latent-state count over groups | **0.2299** |
| tuned bigram on raw rows | 0.2409 |
| base rate | 0.3293 |
| trivial | 2.7068 |

| Headroom | vs base rate | vs **strongest** baseline |
|---|---|---|
| value | **+0.1050** (passes) | **+0.0056** (fails the 0.05 bar) |

### 4.2 Why

**The world's law is first-order Markov, and a first-order Markov chain is
exactly what a bigram table represents.** With enough data, "understood the
law" and "estimated the transition table" are not distinguishable by a
next-event score. The transition world therefore **cannot carry the study's
claim**, and a study that ran it and reported "Organica won" would have been
reporting a compression-fidelity result while claiming a knowledge result.

### 4.3 The fix — change what the benchmark tests

**The world was not hardened.** The owner's instruction was explicit: *don't
make the world artificially harder just to force Organica to win.* So a
**second task** was built, and the first was **reclassified** rather than
tuned.

**T1 — the transition world: CALIBRATION / CONTROL.** It tests ordinary
transition learning and adaptation to a changed law. It is **not** evidence
of abstraction beyond counts, and the protocol says so.

**T2 — the compositional task: PRIMARY.** Four cells in a 2×2 grid of two
latent factors, 4 tags each. The law is *the successor cell is the one that
differs in exactly one factor*. The tag-to-cell mapping is **randomised per
world**, so no fixed tag association can solve it.

**The withheld combination.** One cell per world is held out: its flip-P
transitions are removed from the **training stream only**. The held cell's
tags remain visible in training (155–202 context events per world), its
flip-Q transitions remain visible, and the other three cells show both
transition types — so the rule is fully supported by the training data, and
the learner must **apply** it where the evidence is missing.

**The gate, and its numbers** (30 independent worlds):

| Quantity | Value |
|---|---|
| mean gap, ceiling − strongest simple baseline | **+0.1035 nats** |
| **99% interval over worlds** | **[+0.0996, +0.1074]** |
| lower bound vs the 0.05-nat gate | **PASS** |
| the binding baseline | **bigram** in 23 of 30 worlds; cell counter in 7 |
| gap on the **held cell's** contexts | **+0.1963** [+0.1901, +0.2033] |
| gap on the **other cells'** contexts | **+0.0425** [+0.0411, +0.0444] |
| positive control (holds the generating rule) | reaches the ceiling exactly |
| broken-rule control (latched onto one transition type) | ≥ **+0.1015** worse |

**The row that makes the gate mean something.** The gap on the held cell is
**4.6×** the gap on the cells whose transitions were fully observed. That is
what shows the gap comes from **generalization** rather than from generic
estimation error — without it, the gate could have been passing for the wrong
reason. It is check **G7**, and it is a check the earlier probe could not
have contained.

**A reported sensitivity, not a gate.** A control with the right *structure*
but the two transition *weights* swapped is only **+0.0307** worse
[+0.0283, +0.0332]. The endpoint resolves the law's **structure** sharply and
its exact **weights** only weakly. That is a resolution fact about the
endpoint, it bounds what a result may claim, and it is recorded so that no
future write-up claims weight-level resolution it does not have.

---

## 5. A constraint on the interpretation of any result

`docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §4.5 states this in full.
It is repeated here because it constrains what this project may say about
its own results.

**The frozen engine's taxonomy has no category for "tight group."** A group
defined by co-occurrence has clustering 1.000, which the `concept` rule
excludes; and with reach 8 it is not a `phrase_fragment` either. It is
`unclassified`.

> Therefore: a result in which Organica scores at or below the count-based
> baselines is **consistent with** the organism having failed to represent the
> relation. It is **not** evidence that the organism cannot represent
> relations in general, because the category that would carry a group of
> interchangeable elements does not exist in the frozen taxonomy.

A second, independent limit: **Layer-1 retention crowds out the structure it
would need.** The surviving compressed graph covered only **9–10 of 16**
vocabulary tags, with the top-20 temporal edges dominated by one group
(16 of 20 sources from one group, 3 from a second, 1 from a third, 0 from a
fourth) even though the groups were visited comparably (26.7 / 30.8 / 23.9 /
18.6 %, ratio 1.7×). That is **`MAX_PREDICTIONS = 20` in Layer 1** — an
organism-side capacity finding, not a stimulus artifact.

Both limits are recorded **before** the run, so neither can be discovered
afterwards as an excuse for a null result.

---

## 6. What this audit establishes, and what it does not

**Establishes.**

- A benchmark can pass every instrument check it contains and still be unable
  to test its claim. This one did, and the check that would have caught it —
  run the **strongest** simple model through the endpoint, and require the
  **lower uncertainty bound** of the gap to clear the bar across independent
  worlds — is cheap.
- The metric choice and the readout choice are **not separable**. A hard 0/1
  readout loses to the base rate under log-loss (5.9441 vs 0.3293) even when
  it holds the world's exact edge set. Only a proper scoring rule with a soft,
  tuning-split-calibrated readout can measure anything.
- A **grading-only control is not a control set**. A "knows the grouping"
  oracle reaches 0.87 of the achievable span; the headroom must be measured
  against the strongest comparator, and the strongest comparator is often
  something nobody named in the protocol.

**Does not establish.**

- That Organica can do any of this. **The confirmatory study has not been
  run.** Every number in this document and in Revision 3 is a property of the
  *instrument*, measured before the experiment. The subsequent Pilot 0 and the
  Gate 13 preflight *did* execute engine runs; they are recorded in §8, and
  they bear on the organism, not on the instrument.
- That the compositional task is the right test forever. It is a test of
  generalization to a **withheld combination** in one synthetic world family.
  If it also fails to separate the ceiling from the strongest baseline, that
  is a publishable finding about the task, and it is reported as one.
- Anything about "understanding". The target is evidence of **generalization
  beyond observed transitions**, not proof of an unobservable inner state.

---

## 7. Reproducing this audit

```bash
# T1 — the transition world, now classified CALIBRATION / CONTROL
python benchmarks/acquisition_endpoint_probe.py

# T2 — the compositional task, the PRIMARY discriminativeness gate
python benchmarks/acquisition_compositional_probe.py

# 20 proof-of-firing tests: every check above, with a variant in which it fails
python -m pytest tests/test_acquisition_endpoint.py -q
```

**Committed artifacts:**

- `docs/acquisition_endpoint_audit.json` — the T1 probe's output.
- `docs/acquisition_compositional_gate.json` — the T2 gate's output, per world.
- `docs/acquisition_level_audit.json` — the four-level read: where the world's
  law is present in the organism's own state (raw rows 0.96, memory tables
  0.93, structures 0.55).
- `docs/acquisition_coverage_audit.json` — the coverage diagnosis: the groups
  are visited comparably, so the missing tags are an organism-side pruning
  finding.
- `docs/acquisition_readout_design.json` — the readout sweep, under both
  metric shapes, with the frozen and final states.

---

## 8. The reconciliation — the task gate and the acquisition gate

*Added 2026-10-28, after the Gate 13 preflight. This section reconciles two
results that were produced separately and that look, at first reading, like a
contradiction. They are not one.*

### 8.1 Two gates, two questions

|  | **Compositional probe (T2)** | **Gate 13 preflight** |
|---|---|---|
| Question | Is there room for an abstraction to beat counting? | Does V1's own state contain the world's relations? |
| Engine run? | **No.** No engine is run; no cell is scored. | Yes — 110 cycles per seed, 6 seeds |
| What is compared | the closed-form Bayes ceiling against a base rate, a tuned bigram and a cell counter | the organism's **asserted structure** against the world's edges |
| Verdict | **PASS** (G1–G7 all pass) | **FAIL** — 0.0 %–2.7 % asserted against 100 % raw |

There is no contradiction. The first is a statement about the **benchmark**;
the second is a statement about the **organism**. Together they say something
sharper than either alone: **the benchmark is discriminative, and V1 cannot
currently reach the state that would make it answerable.**

### 8.2 What the compositional gate measured — and what it did not

The compositional task withholds one cell of the 2 × 2 latent grid from the
training stream and tests on that cell's contexts, with the tag-to-cell
mapping randomised per world (30 worlds, seeds 20261200–20261229).

| Quantity | Value |
|---|---|
| Bayes ceiling (world 0) | 0.2706 |
| Base rate | 0.4199 |
| Tuned bigram | 0.3839 |
| Cell counter | 0.3962 |
| **Gap, ceiling vs strongest simple baseline** | **+0.1035 nats**, 99 % interval **[+0.0996, +0.1074]** |
| Binding baseline | bigram in **23 / 30** worlds, cell counter in **7** |
| G7 — gap on the **held cell's** contexts | **+0.1963** [+0.1901, +0.2033] |
| G7 — gap on the **other** cells' contexts | **+0.0425** [+0.0411, +0.0444] |

The lower bound clears the 0.05-nat bar, so the benchmark is discriminative,
and G7 shows *why*: the gap on the withheld combination is **4.6×** the gap
elsewhere, so it comes from generalization rather than from estimation error.

> **The +0.1035 nats is the benchmark's headroom. It is not Organica's margin.**
> The compositional probe runs no engine and scores no learner. It answers one
> question: *is there room for something better than transition counting?*
> Yes. It does not answer whether Organica occupies that room.

### 8.3 What the acquisition gate measured

Gate 13 asks the organism-side question: after acquisition, does the
organism's asserted structure contain the world's compositional edges?

| Seed | Asserted coverage | Raw temporal coverage | Verdict |
|---|---|---|---|
| 20261100 (exploratory) | 0 / 112 = 0.0 % | 112 / 112 = 100 % | FAIL |
| 20261101 | 0 / 112 = 0.0 % | 112 / 112 = 100 % | FAIL |
| 20261102 | 1 / 112 = 0.9 % | 112 / 112 = 100 % | FAIL |
| 20261103 | 1 / 112 = 0.9 % | 112 / 112 = 100 % | FAIL |
| 20261104 | 0 / 112 = 0.0 % | 112 / 112 = 100 % | FAIL |
| 20261105 | 3 / 112 = 2.7 % | 112 / 112 = 100 % | FAIL |

**The causal account, measured rather than inferred.** The signal is present:
every world edge is in the raw temporal log. What is missing is the
*assertion*. `_build_predictions` sorts candidates by raw temporal count and
truncates at `MAX_PREDICTIONS = 20`. On this stimulus, the two tags of a cell
co-occur in every event of that cell, so **within-cell pairs accumulate far
higher counts than the cross-cell transitions that carry the law**; the top
20 slots are filled 95–100 % by within-cell pairs and the cross-cell edges
are discarded at rank 21+. The counterfactual audit confirmed the split: on
seed 20261101 the 22 asserted `prediction_candidate` edges were 22 intra-cell
and 0 inter-cell, with 0 / 112 world overlap.

**The treatment flips it.** A paired diagnostic raised only the cap to 1,000,
leaving every other constant identical, and re-ran the same five seeds:

| Seed | Cap 20 | Cap 1000 |
|---|---|---|
| 20261101 | 0 / 112 (FAIL) | 110 / 112 = 98.2 % (PASS) |
| 20261102 | 1 / 112 (FAIL) | 112 / 112 = 100 % (PASS) |
| 20261103 | 1 / 112 (FAIL) | 112 / 112 = 100 % (PASS) |
| 20261104 | 0 / 112 (FAIL) | 112 / 112 = 100 % (PASS) |
| 20261105 | 3 / 112 (FAIL) | 112 / 112 = 100 % (PASS) |

So the failure is **one named bound**, and it is attributable rather than
mysterious: a capacity limit, not a missing signal, not a readout defect, and
not a property of the world.

> **Refined on 2026-10-28 — "bottleneck" is not "deepest cause".** Four
> further diagnostic probes (`docs/GATE13-CAUSAL-ACCOUNT.md`) measured this
> bound and found that it is **not the deepest cause**. Coverage is a steep
> monotone dose-response in the cap and needs **240–244** asserted edges to
> clear the gate; switching from a global to a **per-source** allocation rule
> does not help (per-source K=10 retains 258–286 edges for coverage 0.72–0.77
> where the global rule reaches 0.95–0.97 at 320); and **precision never
> exceeds 0.3443** at any budget under either rule. A 1-tag stimulus removes
> the within-cell pairs by construction and still fails on 0 of 6 seeds
> (asserted coverage 0.1719–0.1953). The deeper constraint is therefore
> **precision** — in a candidate space where the world's edges are about a
> third of the rows and are not clustered at the top of any frequency
> ordering, no frequency-based selection can find them. The statement in §8.3
> is accurate as written ("raising the cap restores coverage"), but it names
> the proximate bound, not the deepest cause.

### 8.4 The organism lost

Pilot 0 (seed 20261100) scored the cells it could score. Under Amendment 2
the baselines received the identical raw exposure, so the comparison is fair.

| Learner | Retention | Transfer | Revision |
|---|---|---|---|
| **Organica** | **0.453018** | 0.453886 | 0.463391 |
| Replay | 0.347521 | 0.349592 | 0.351989 |
| Statistical | 0.347273 | 0.350723 | 0.352194 |
| Base rate | 0.409581 | 0.409529 | 0.406084 |
| Bayes ceiling | 0.276259 | 0.272383 | 0.275208 |

Organica scored **worse than the baselines did after their episodes were
deleted** (0.453018 against the 0.403045 floor those cells collapse to). That
is coherent with §8.3 rather than surprising: the asserted structure is
overwhelmingly within-cell co-occurrence, so the readout projects *which cell
the context is in* when the task asks *which cell comes next*.

**Transfer was not measured, and it is not a transfer failure.** Per §8
requirement 13, a seed that fails acquisition is reported as
`acquisition_failed` and transfer is reported as not measurable. The pilot
recorded `transfer_status = "not_measurable_due_to_acquisition_failure"`.

### 8.5 An instrument defect found while reconciling — and fixed

Two different functions implemented "Gate 13" under the same name:

- `benchmarks/acquisition_runner.py` evaluated the **asserted** basis, as
  Amendment 1 requires. It failed, correctly.
- `benchmarks/acquisition_harness.py::gate_acquisition_sufficiency` evaluated
  the **raw temporal** basis. It returned **100 %** and passed.

So the harness contained a gate that **could not fire** on the very condition
the study exists to detect, and its test asserted `passed is True`. A check
that cannot fail is decoration; a gate that passes while the protocol's gate
of the same name fails is worse than decoration, because it authorises a study
the protocol says is not measurable.

**Fixed.** `gate_acquisition_sufficiency` now implements Amendment 1's dual
accounting — it computes `asserted_coverage` **and** `raw_temporal_coverage`,
gates on the asserted figure, and records `coverage_basis =
"asserted_structure"`. It also accepts `max_predictions`, the treatment arm,
so the failure can be *attributed* rather than merely observed. The test was
rewritten accordingly: the "normal run" expectation for Gate 13 is now a
**failure** on the frozen engine with raw coverage above 0.9 and asserted
coverage below 0.1, the treatment arm is asserted to **pass**, and the
aggregate prerequisite check is asserted to report the gate-13 failure at the
preregistered threshold.

The difference between the two figures is the finding. Raw 1.0 with asserted
0.0 means *the world was fully present in memory and the organism failed to
assert it*. A harness measuring only the raw figure could not tell that apart
from a world that never presented the relation.

### 8.6 The consequences for the pre-registration

1. **The campaign stops at the gate.** The 600-cell factorial does not run.
   Transfer is not measurable. Amendment 3 records this; nothing here changes
   it.
2. **The confirmatory sample has shrunk, and that is bookkeeping, not a
   result.** Amendment 2 defined the confirmatory 30 seeds as `20261101`
   through `20261130`. Amendment 3 then designated `20261101`–`20261105` as
   diagnostic preflight seeds. **Five of the thirty confirmatory seeds are now
   diagnostic**, leaving a usable confirmatory sample of **25**
   (`20261106`–`20261130`). The frozen Amendment 2 text is not rewritten; the
   consequence is recorded here, and any future campaign must re-specify its
   seed set rather than inherit one that has been partly spent.
3. **The compositional task remains a valid instrument.** It is
   pre-registered, its gate passes, and it is the thing V2 would be measured
   on. It is **not** a result about V1.

### 8.7 What this does not change

- **T1 stays a CALIBRATION / CONTROL task.** Nothing in §8 rehabilitates it.
- **The six negative task families stand.** Phase K's three REVERSED verdicts,
  Phase L's `H3-L — INCONCLUSIVE`, and Phase H/I/J's failures are untouched.
- **No V2 is authorised by this.** But §8.3 supplies the one thing the V2
  brief's gate 5 asked for: a **specific, named failure**. The V2 brief named
  two — weak transfer despite correct internal structure, and failure to
  retain useful structure after episode removal. The failure actually
  observed is a **third**: the organism never formed the structure at all,
  because one bounded Layer-1 selection step discarded it. Naming a failure
  is not the same as authorising a build.
- **Nothing here is evidence of understanding.** The target was and remains
  evidence of generalization beyond observed transitions.

---

## 9. Reproducing the reconciliation

```bash
# the task gate — no engine run, ~2 min
python benchmarks/acquisition_compositional_probe.py

# the acquisition gate on the frozen engine, and its treatment arm
python benchmarks/acquisition_harness.py --gate 13
python -m pytest tests/test_acquisition_harness.py -q -k Gate13
```

**Artifacts:**

- `docs/acquisition_compositional_gate.json` — the T2 gate, per world.
- `docs/GATE13-PREFLIGHT-AUDIT.md`, `docs/gate13_counterfactual_audit.json` —
  the counterfactual decomposition of the coverage failure.
- `docs/GATE13-PAIRED-CAPACITY-TEST.md`,
  `docs/gate13_paired_capacity_test.json` — the paired cap treatment.
- `docs/PILOT-0-INSTRUMENTATION-AUDIT.md`,
  `docs/acquisition_single_seed_pilot.json` — the ten-cell Pilot 0.
