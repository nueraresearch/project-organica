# The acquisition experiment — pre-registration

**Revision 3. Supersedes Revision 2 (2026-10-26) in full.**
**Revision 3 is committed BEFORE any cell is run.** Nothing here has been
measured against a factorial cell, and no cell has been run.

> ### Why Revision 3 exists — the audit that produced it
>
> On 2026-10-26 the owner directed: **pause the acquisition build; resolve
> the task-to-readout mapping; prove the benchmark measures reusable
> knowledge; then run it.** A review of Revision 2 was carried out against
> that instruction, and **every one of its five objections was verified as
> correct against the code.** Two further defects were found that the review
> did not raise, and one further defect was found in the *redesign* itself.
>
> The full record is in `docs/ACQUISITION-ENDPOINT-AUDIT.md` and journal
> §51. The defects are listed here rather than quietly fixed, because a
> pre-registration that silently absorbs its own errors is not a
> pre-registration.

| # | Defect in Revision 2 | Measured evidence | Correction in Revision 3 |
|---|---|---|---|
| 1 | **The endpoint measured the wrong thing.** The generator draws each event's cause *independently*; within a regime, P(causeₜ₊₁ = c \| causeₜ = c) differs from P(causeₜ₊₁ = c) by at most **0.03**. A same-cause pair is a *within-event* fact, and the endpoint scored a *next-event* prediction. The apparent dependence (0.6966 vs 0.4551 marginal) is **Simpson's paradox** — a shared regime block. | The next-event relation was not in the world. | §4 replaces the world with a **temporally coupled, group-structured, regime-switching** generator in which next-event prediction is *intrinsic*. |
| 2 | **F1 at 0.5 was degenerate.** The most common feature's next-event probability is ~0.38, so a calibrated model predicts no positives at the fixed threshold while Organica's readout emits hard 0/1. | The Bayes-optimal calibrated model scores **F1 = 0.0000 — identical to predicting nothing**. | §4.3 makes **log-loss the primary metric** and pins the readout to it. F1 is demoted to a reported diagnostic. |
| 3 | **The projection was directional; the target relation was not.** `edges_implied_by_structures` adds concept and phrase member pairs in one list direction, while the gold pairs were undirected same-cause pairs. | **10 of 12** gold pairs appeared in exactly one direction — the order tags landed in the event text. | §4.3 states the readout's mapping to the endpoint explicitly and pins it. |
| 4 | **The "fixed-rule ceiling" was a relation oracle, not a prediction ceiling.** The gold pair set carries no frequency information; the dominant tag's follow-up probability is 0.3825. | A relation oracle was being used as a prediction ceiling. | §4.2 derives the ceiling from the generator's **full conditional distribution**, in closed form. |
| 5 | **Retention and transfer were conflated.** One window (110–149) carried two labels and two gates. | One window, two names, two decision gates. | §4.4 gives the three limbs **three different windows under three different laws**. |
| 6 | **The frozen engine never forms a group concept in that world** (found during the audit, not by the review). `_classify` requires `degree ≥ 4 AND clustering ≤ 0.4 AND reach ≥ 4` for a concept, but a group defined *by* co-occurrence has **clustering 1.000**. | All **12** tags classified `unclassified`; **0** concepts formed at 4, 5, 6 and 8 features/cause. | §4.1 and §4.3 use a world whose structure the engine's taxonomy *can* represent, and §4.5 records the taxonomy's limit as a **known constraint on what any result can mean**. |
| 7 | **The generator's regime switch was relation-invariant** (found during the audit). `gold_same_cause_pairs` is identical in both regimes; only dominance changes. | A relation-scored endpoint could not distinguish pre-switch from post-switch. | §4.1's law *rotates* at the switch, so revision has something to revise. |
| 8 | **The revision's own readout artifact, and then the deeper one.** A first pass scored structures with `prediction_candidate` edges only, under a hard 0/1 readout, and reported a span of **−0.579** — worse than predicting nothing. That was an artifact. But the correction exposed something worse. | With all six structure types and a **soft, tuning-split-calibrated** readout, the same structures reach **0.278** against a base rate of 0.329 and a ceiling of 0.224. The **ad-hoc** readout scores **1.655 — worse than the base rate**. | §4.3 pins the readout to a backoff-smoothed form whose smoothing is chosen **on the tuning split**, and §4.6 records the artifact correction. |
| 9 | **The headroom check compared the ceiling against a BASE RATE** (found 2026-10-27, after the redesign). A base rate is the weakest possible comparator, so the check could pass while the benchmark had no room to show an advantage over transition counting. | Against a **cell-level counter** — the strongest count-based baseline — the transition world's headroom is **+0.0056 nats**, far below the probe's own 0.05 bar. Against the base rate it was **+0.1050**, which passed. | §4.2 splits the study into **two tasks with two roles**: the transition world is reclassified **CALIBRATION / CONTROL**, and the new **compositional** task carries the discriminativeness claim, with the gate measured against the strongest baseline and its **lower 99% bound** required to clear 0.05 nats. |

**Owner direction (2026-10-26, and extended 2026-10-27).** V2 is not cut.
The live study is not restarted. V2–V5 are not run. No further months of
audit-infrastructure refinement. The roadmap is: **finish the audit build →
freeze it → run the acquisition experiment → compare against the replay
learner → publish whatever happens → only then discuss V2.**

**The 2026-10-27 extension, in the owner's words:** *"Change what the
benchmark tests — or narrow the claim. … If the new task still gives a
bigram table nearly ceiling-level performance, that is a useful answer: it
means the task doesn't demonstrate added value beyond counting. Don't make
the world artificially harder just to force Organica to win. The target is
evidence of **generalization beyond observed transitions**, not proof of an
unobservable inner state called 'understanding.'"* This document is written
to that instruction, and §4.2 records the consequence: **the transition
world cannot carry the claim, so it does not.**

---

## 1. The question, and the claim it can support

**The question.** Can a controlled experience leave behind a structure that
helps on later events, **after the raw episodes that produced it are
unavailable**?

**The claim this study can support, stated at its true strength:**

> **Does this frozen, development-first system turn experience into a
> representation that predicts a genuinely held-out outcome — including
> outcomes built from combinations it never observed — after raw episodes
> are unavailable?**

**What it cannot support, stated up front:**

- **Not** that Organica learns *like a human*. Its inputs are tokenized
  events; its development rules, layer ladder, thresholds, attention
  formula and candidate types are all **designer-specified**.
- **Not** that it learns at all, in the sense the project's own Phase L
  protocol would accept — that verdict is a separate question, and Phase
  L's was `H3-L — INCONCLUSIVE`.
- **Not** anything biological. "Persistent reconstruction" is a description
  of a mechanism in this code; the resemblance to how some biological
  systems are described is a **motivation for the experiment, never a claim
  about its result**.
- **Not** that the trace reconstructs *developmental history*. It
  reconstructs the **present** lineage of surviving structures (§2.1).
- **Not** that the acquisition experiment demonstrates *abstraction*.
  §4.2 states precisely which task can support that claim, and it is the
  compositional one. The transition world cannot.
- **Not** that the frozen engine *can* represent a group of interchangeable
  elements. Measured: it has no taxonomic category for one (§4.5). This
  is a **constraint on the interpretation of any result**, stated before
  the run so it cannot be discovered afterwards as an excuse.

---

## 2. What is already known — design inputs, not predictions

Read-only diagnostic probes were run before this design was written. They
are **design inputs**, and every prediction in §6 is about the factorial
cells, **which have not been run**.

### 2.1 The trace shows the present lineage, not the historical one

A candidate's identity is a content hash — `_make_id` is
`sha256("|".join(key_parts))[:8]` (`sleep.py:45-48`) — but the identity
**does not include the parent set**. Higher-layer structures are re-formed
every cycle with parents **recomputed** from current state (`sleep.py:1432`,
`1450`, `1467`, `1384`). The same content identity can therefore carry a
**different lineage** later — measured, `meta_concept`'s parent set changed
in 57 of 220 structure-cycles while its own identity was unchanged.

**Consequence:** the trace reconstructs the organism's **current** descent,
not the history of that descent.

### 2.2 The lineage is re-derived, not carried

| Diagnostic | Result |
|---|---|
| A surviving structure's parent set is identical across consecutive cycles | **94.8 %** of 3,883 structure-cycles |
| …but what do those links point at? | **87.2 % active** (parent re-derived that same cycle) / **12.8 % carried** (alive, not re-derived) — of 8,416 links |

The identical parent sets are **deterministic re-derivation**, not copied
edges. (This corrected an earlier reading of mine that called them "carried
forward"; the link-state measurement is the discriminating evidence.)

### 2.3 The survival rule is asymmetric across layers

`_natural_selection` (`sleep.py:1752-1802`) reinforces a structure whose key
current experience re-produced, and otherwise decays it ×0.8 and prunes it
below `DEATH_THRESHOLD = 0.15` (`334`). **But `_candidate_key` returns `""`
for every type except concept, phrase, loop and prediction**
(`1804-1817`), so **meta-concepts, processes, workflows, hypotheses, theories,
questions, dreams, investigations and experiments are never decayed and never
pruned by that path.**

- **Layer 1** survives only if current experience keeps producing its content
  key — *persistent reconstruction* proper.
- **Layers 2–4** persist as rows while they remain in the window, and are
  re-formed with recomputed parents.

**So "the structure survived" is not one thing**, and the study must not
treat it as one.

---

## 3. Definitions, fixed in advance

### 3.1 Content identity

**A structure's content identity is its candidate id** (a content hash). A
**row** is not an identity: the laboratory records every store, so for each id
it knows whether the structure was **re-instantiated** (a new row written) or
**left alone**. Both are reported.

### 3.2 Lineage connection

A structure's lineage is **connected** when its parent chain resolves back to
a Layer-1 terminal within depth 7, under the A3 auditor
(`benchmarks/audit_trace_probe.py` → `audit_ancestry`). A3's honesty criterion
applies unchanged: an unresolvable parent is reported as **aged out** or
**unresolved**, never as absent.

### 3.3 The E-rem condition, named exactly

**"Source experiences removed"** means: the acquisition-phase `events` rows
and their `precedes` edges are deleted. It does **not** mean a clean slate.
Ingest also accumulates **`cooccurrences`** and **`tag_counts`**
(`memory.py:282`, `306`), which outlive the rows. The condition is therefore
named:

> **"episode removal with learned graph retained"**

And what it leaves behind is stated exactly, because a removal that leaves
different things behind for different subjects is a comparison about
unequal access rather than about the mechanism:

| Retained after E-rem | Removed by E-rem |
|---|---|
| `cooccurrences` (the accumulated co-occurrence table) | the acquisition `events` rows |
| `tag_counts` (the accumulated tag-frequency table) | the `precedes` (temporal) edges |
| every derived structure the organism has formed | the raw episodes themselves |
| the laboratory's per-cycle snapshots (never readable by any learner) | |

**Every learner receives the identical removal.** The comparison learners'
stores are emptied the same way, and their memory budget is accounted in
§6.5.

### 3.4 The two questions, kept separate

| | Question | Answered by |
|---|---|---|
| **Q1 — internal persistence** | Does the organism still hold the knowledge? | the organism's own state: current beliefs, current lineage, current support |
| **Q2 — external provenance** | Can the laboratory prove how it developed? | the laboratory's record: per-cycle snapshots, the store log, the trace |

A result on Q1 is not a result on Q2. The **laboratory's snapshots are written
to the laboratory's own store and are never readable by any learner** —
including the replay learner, which could otherwise reconstruct from them,
which is exactly the mechanism under test.

---

## 4. The world, the task, and the endpoint

### 4.1 Two tasks, two roles — and why the split is necessary

**The measurement that forces this split.** On the redesigned transition
world, the endpoint's headroom was measured against the *strongest* count-based
baseline rather than against the base rate:

| Model (retention window, house metric shape) | log-loss |
|---|---|
| ceiling — knows the law | **0.2242** |
| copy-context — knows only *which group* it is in | 0.2521 |
| cell-level counter — a latent-state count over groups | **0.2299** |
| tuned bigram on raw rows | 0.2409 |
| base rate | 0.3293 |
| trivial | 2.7068 |

The gap between the ceiling and the **strongest** simple baseline is
**+0.0056 nats** — against a base rate it is **+0.1050 nats**, which passes
any bar, and against the strongest baseline it is not merely below the 0.05
bar but **almost nothing at all**.

**Why.** The world's law is **first-order Markov**, and a first-order Markov
chain is exactly what a bigram table represents. With enough data, "understood
the law" and "estimated the transition table" are **not distinguishable by a
next-event score**. The transition world therefore *cannot* carry the study's
claim, and a study that ran it and reported "Organica won" would have been
reporting a compression-fidelity result while claiming a knowledge result.

**So the study has two tasks, and each is used only for what it can support:**

| Task | World | Role | What it can support | What it cannot |
|---|---|---|---|---|
| **T1 — transition** | `benchmarks/acquisition_world.py` | **CALIBRATION / CONTROL** | ordinary transition learning; adaptation to a changed law; that the harness runs and the metrics behave | any claim of abstraction beyond counts |
| **T2 — compositional** | `benchmarks/acquisition_compositional.py` | **PRIMARY** | generalization to a **withheld combination** of familiar elements; retention of that; revision of it | a claim about a human-like "understanding"; anything about worlds other than this one |

**The owner's instruction is honoured in the strict form: the world was not
hardened to force a win.** The compositional task was built so that the gap is
created by *generalization* — and it was then measured (§4.2) to confirm that
the gap comes from the withheld combination and not from generic estimation
error. If the compositional task had also failed to separate the ceiling from
the strongest baseline, that would have been reported as "the task does not
demonstrate added value beyond counting", and the study would have said so.

### 4.2 T2 — the compositional task, and the discriminativeness gate

**The world.** Four **cells** arranged in a 2×2 grid of two latent factors:

```
        Q0        Q1
   P0  (P0,Q0)   (P0,Q1)
   P1  (P1,Q0)   (P1,Q1)
```

Each cell holds 4 tags (16 tags total). An event draws 2 tags uniformly from
one cell. The **law is compositional**:

> **The successor cell is the one that differs in exactly one factor** —
> flip-P with probability 0.65, flip-Q with probability 0.35 (regime 0), and
> the weights rotate at the regime switch (regime 1: 0.35 / 0.65).

The law is a single rule that applies to all four cells and says nothing
about any particular tag. The **tag-to-cell mapping is randomised per world**
from a fixed 16-word pool, so no fixed tag association can solve it and no
result can be carried between seeds. (Measured: the held cell takes all four
grid positions across 30 worlds — `p0q0`, `p0q1`, `p1q0`, `p1q1`.)

**The withheld combination.** One cell per world, chosen at random, is the
**held** cell. Its flip-P transitions are withheld from the **training
stream** only: the events in which the held cell is the context and the
successor is its flip-P neighbour are removed from the acquisition phase.
Everything else in the world is untouched, and the **test stream is the
unmodified world**.

**Why this is fair, and not a rigged hole.** Measured on all 30 worlds:

- the held cell's tags are **still present** in the training stream, and
  still appear as contexts — so the learner can still learn which cell they
  belong to (held-cell context events in training: 155–202 per world);
- the held cell's **flip-Q** transitions are still present, so the learner
  has *some* evidence about that cell;
- the other three cells show **both** transition types, so the rule "flip
  exactly one factor" is fully supported by the training data;
- the learner must therefore **apply** the rule to the one cell where the
  evidence is missing, instead of recounting the transition.

A tag-level bigram, and even a cell-level counter, has **zero support** for
the withheld transition and must fall back to a backoff. A learner holding
the rule does not.

**The gate, and its numbers.** `benchmarks/acquisition_compositional_probe.py`,
30 independent worlds, the gap measured against the **best** of {base rate,
tuned bigram, decayed bigram, cell-level latent-state counter}, each swept
over a declared grid and selected on the **tuning split** only:

| Quantity | Value |
|---|---|
| mean gap, ceiling − strongest simple baseline | **+0.1035 nats** |
| **99% interval over worlds** | **[+0.0996, +0.1074]** |
| **lower bound vs the 0.05-nat gate** | **PASS** |
| the binding baseline | **bigram** in 23 of 30 worlds, cell counter in 7 |
| gap on the **held cell's** contexts | **+0.1963** [+0.1901, +0.2033] |
| gap on the **other cells'** contexts | **+0.0425** [+0.0411, +0.0444] |
| broken-rule control (latched onto one transition type) | ≥ **+0.1015** worse than the ceiling |
| positive control (holds the generating rule) | reaches the ceiling, exactly |

**The last two rows are the ones that make the gate mean anything.** The
positive control proves the ceiling is reachable by a learner that holds the
rule, and the broken-rule control proves the endpoint can tell a wrong law
from the right one. And the last-but-two row is the check that the gap comes
from **generalization rather than estimation error**: the gap on the held
cell is **4.6×** the gap on the cells whose transitions were fully observed.
**Without that check, G1 could have been passing for the wrong reason.**

**A reported sensitivity, not a gate.** A control with the right *structure*
but the two transition *weights* swapped is only **+0.0307** worse
[+0.0283, +0.0332]. So the endpoint resolves the law's **structure** sharply
and its exact **weights** only weakly. This is a resolution fact about the
endpoint, it bounds what a result can claim, and it is recorded here so that
no future write-up claims weight-level resolution it does not have.

### 4.3 The endpoint, pinned

**Prediction unit.** For each evaluation event `e_{t+1}` and each tag `v` in a
**fixed vocabulary**, predict whether `v` appears in `e_{t+1}`, given the
context = the tags of `e_t`.

**Ground truth.** The **observed** tags of `e_{t+1}`. The hidden cell/group
labels and regime labels are never fed to any learner; they are used only to
verify the world and to compute the ceiling.

**Fixed denominator.** `|contexts| × |vocabulary|`. Every learner is scored on
exactly the same labels, so no learner can gain by scoring on a different set.

**Vocabulary.** The set of tags appearing in the **acquisition-phase** events
(for T2: the *training stream's* events), fixed before the follow-up begins.

**Primary metric — log-loss.** The house pairwise shape, as in
`benchmarks/heldout_prediction.py` → `_score`. **F1 is demoted to a reported
diagnostic**, for the measured reason in defect 2 above.

**The metric's shape is reported both ways.** The house shape excludes the
cell where `target == source`. On the transition world that exclusion was
measured to **shield the baseline**: with it, the base rate scores 0.3293;
without it, 0.4022, while the ceiling barely moves (0.2242 → 0.2308). So the
exclusion *discards real signal* (276 of 10,208 cells — in a world whose law
**prefers** the same group, so self-recurrence is law-governed, not noise) and
it *flatters the baseline*. **Revision 3 reports both shapes**, with the house
shape as primary for comparability with the project's earlier studies, and
states the difference in every write-up. The decision rule (§6.4) is
evaluated on the **house shape**, and the **self-cell shape is reported
alongside it as a co-primary**. A result that flips between the two shapes is
reported as a result that flips.

**Organica's readout — pinned, and tuned on the tuning split.** For a context
tag `a` and a target tag `b`:

```
p(b | a) = ( w(a, b) + α · m(b) ) / ( W(a) + α )
```

where `w(a, b)` is the structure's own evidence for `a → b` (accumulated over
all six structure types), `W(a)` the row total, `m(b)` the base rate measured
on the acquisition phase, and **α the smoothing parameter, chosen on the
tuning split** — never on a scoring window.

**Why this form, and not the ad-hoc one.** The ad-hoc readout (0.9 for a
graph neighbour, ~0.1/k otherwise) scores **1.6554** against a base rate of
**0.3293** — it is *worse than knowing nothing*, and it made the structures
look useless. With the backoff-smoothed form, the same structures reach
**0.2778**, i.e. **0.978 of the achievable span**, and beat the base rate
without reaching the grouping oracle (0.2521) or the ceiling (0.2242). **The
readout was the limiter, not the organism.** (The full correction history is
in §4.6.)

**The readout's mapping to the endpoint, stated explicitly** (defect 3). The
compositional world's target relation is over **cells**, and the readout is
over **tags**. The mapping is: the structure's evidence for `a → b` is
evidence about the *relation* between `a`'s cell and `b`'s cell, and it is
scored as a conditional over tags. The readout is **directional by
construction** and the endpoint is scored on the **observed next event**,
so no undirected relation is being read in a directed way: the readout
predicts, and the truth is what was observed.

**Organica's structures, and the tag-coverage limit.** The frozen compressed
graph covered only **9–10 of the 16** vocabulary tags on the new world.
This was diagnosed rather than assumed: the groups are visited comparably
(26.7 / 30.8 / 23.9 / 18.6 %, ratio 1.7×), and the top-20 temporal edges are
dominated by one group (16 of 20 sources from one group, 3 from a second, 1
from a third, 0 from a fourth) — so the crowding is **`MAX_PREDICTIONS = 20`
in Layer 1**, an organism-side capacity finding, **not** a stimulus artifact.
This caps what Organica can score, and it is stated here so that a low
Organica score is not misread as "the organism cannot learn this world" when
part of it is "the organism's own layer-1 cap discarded a third of the
vocabulary".

### 4.4 The three limbs, separately scored

**The three limbs are three different questions about the same run, and none
substitutes for another.** A learner can retain without transferring (it
knows the old regime perfectly and cannot use it in the new one), or transfer
without revising.

| Limb | Window (T1 / T2) | Law in force | State used | Question |
|---|---|---|---|---|
| **RETENTION** | 110–149 / 110–149 | old (r0) | **frozen** at the end of acquisition | does the acquired structure still predict the world it was acquired from, after the source episodes are removed? |
| **TRANSFER** | 150–199 / 150–199 | old (r0) | **frozen** | does it generalize to a **new combination** under the *same* law? |
| **REVISION** | 200–249 / 200–249 | **new (r1)** | after continued learning | does it update when the law changes? |
| **REVISION (held out)** | 250–299 / 250–299 | new (r1) | after continued learning | does the *updated* structure generalize to a **new combination** under the new law? |

The **revision** limb is scored on a **separate held-out test**, not on the
window it was learned in — because a learner that merely memorised the
revision window's own transitions would otherwise score a "revision" it did
not achieve.

**Score per independent world or seed, not per cycle.** The unit of analysis
is the **seed**: each seed contributes one score per metric per learner, and
all statistics are over seeds, paired by seed. (This is the same correction
Phase L's Amendment 3 made to the bootstrap's pairing.)

**A note on the three names.** The word "revision" is used in three distinct
senses across this project's documents, and confusing them would be a real
error:

| Sense | Where | What it measures |
|---|---|---|
| **Structural displacement** | Phase L (`DI`/`PI`) | whether later *structure* displaces earlier *structure* — a structure-retention index |
| **Belief revision** | Phase K (K2) | whether a *belief* is corrected against ground truth — Organica **0.4111** vs baseline **0.9846**, **REVERSED** |
| **Revision (this study)** | here, §4.4 | the **state after a window of continued learning**, scored on a ground-truth prediction score over held-out combinations — closer to belief revision than to displacement |

### 4.5 What the frozen engine's taxonomy cannot represent — a stated constraint

`_classify` in `organica/sleep.py` assigns mutually exclusive categories. A
`concept` requires `degree ≥ 4 AND clustering ≤ 0.4 AND reach ≥ 4`; a
`phrase_fragment` requires `clustering ≥ 0.7 AND reach ≤ 2`; `noise` is
`freq ≤ 1 AND degree ≤ 1`; `hub` is `degree ≥ 5`; everything else is
`unclassified`.

**A group defined by co-occurrence has clustering 1.000** — the opposite of
what a concept requires — and with 8 co-occurring tags it has reach 8, so it
is not a phrase fragment either. Measured on a purpose-built group-structured
world: **all 12 tags classified `unclassified`, 0 concepts formed** at 4, 5, 6
and 8 features per cause.

**The engine's taxonomy has no category for "tight group."** This is a
**standing constraint on the interpretation of every result in this study**:

> A result in which Organica scores at or below the count-based baselines is
> **consistent with** the organism having failed to represent the relation.
> It is **not** evidence that the organism cannot represent relations in
> general, because the category that would carry a group of interchangeable
> elements does not exist in the frozen taxonomy.

This constraint is recorded **before** the run, so it cannot be discovered
afterwards as an excuse for a null result.

### 4.6 The readout corrections, kept visible

Two corrections were made to my own readout during this work, and both are
recorded rather than quietly applied.

| # | The reading | Why it was wrong | Corrected reading |
|---|---|---|---|
| 1 | Structures capture **−0.579** of the achievable span — worse than predicting nothing. | The read was **partial** (only `prediction_candidate` edges) **and over-confident** (hard 0/1). A confident wrong answer costs ~7 nats under log-loss. | With all six structure types and a soft readout, the same structures capture **0.940** of the span. |
| 2 | The ad-hoc soft readout scores **1.6554** against a base rate of **0.3293** — the organism's structures look useless. | The readout's constants (0.9 / ~0.1/k) were arbitrary and uncalibrated, and the "worse than the base rate" result was **the readout's**, not the organism's. | With a backoff-smoothed readout, α chosen on the **tuning split**, the same structures reach **0.2778** — **0.978 of the span** — beating the base rate. |

**The lesson this earns, and it is the reason the readout is pinned at all:**
*the readout is part of the hypothesis, and it is the part that was going
unchecked.* A benchmark whose readout is arbitrary will report the readout's
constants as a finding about the organism.

---

## 5. The cell matrix — one complete table

**Factors.**

- **P** (the parent structure): `P-none` (no intervention) / `P-org` (removed
  from the organism's state) / `P-obs` (withheld from the auditor's
  reconstruction only).
- **E** (the source episodes): `E-pres` (retained) / `E-rem` (removed, §3.3).

**`P-none × E-pres` IS the untreated baseline.** It is not an extra cell on
top of six.

**Learners.** The factorial P × E applies to **Organica only**. The two
comparison learners have no parent structures and no lineage, so P is
undefined for them; they run under both E conditions, because E is about
access to evidence and is exactly what must be equalised.

**The exact number of runs, per seed, per task:**

| Learner | Cells | Runs per seed |
|---|---|---|
| **Organica** | P ∈ {none, org, obs} × E ∈ {pres, rem} | **6** |
| **Replay learner** | E ∈ {pres, rem} | **2** |
| **Statistical learner** (bigram / decayed bigram / cell counter) | E ∈ {pres, rem} | **2** |
| **Grouping oracle** (knows which group it is in; T1 only) | — | **0** (a reference, computed) |
| **Bayes ceiling** (T2 only) | — | **0** (a reference, computed) |
| | **Total** | **10 runs per seed per task** |

With **30 seeds** (§6.1) and **two tasks**, that is **600 engine runs** and
**1,200 learner-scores**.

**Predictions for every cell.** `RE` = content reappears; `LC` = lineage
connected; `TS` = still supports the task.

| # | Cell | Learner | RE | LC | TS |
|---|---|---|---|---|---|
| 1 | `P-none × E-pres` | Organica | yes | yes | yes |
| 2 | `P-org × E-pres` | Organica | no (after ≤1 cycle) | no | no |
| 3 | `P-org × E-rem` | Organica | no | no | no |
| 4 | `P-obs × E-pres` | Organica | yes (organism untouched) | **no — the trace is incomplete** | yes |
| 5 | `P-obs × E-rem` | Organica | yes (organism untouched by P; E applies) | **no — the trace is incomplete** | degraded only by E |
| 6 | `P-none × E-rem` | Organica | yes, if the key is still produced | yes, re-derived | degraded only if support is lost |
| 7 | `E-pres` | Replay | n/a | n/a | yes — it has the episodes |
| 8 | `E-rem` | Replay | n/a | n/a | **no — it has nothing** |
| 9 | `E-pres` | Statistical | n/a | n/a | yes |
| 10 | `E-rem` | Statistical | n/a | n/a | **no — it has nothing** |
| — | reference | Grouping oracle / Bayes ceiling | n/a | n/a | the reference score |

**Read the last four rows carefully — they are where the mechanism question
lives.** In the `E-pres` cells the comparison learners have the raw episodes
**and** Organica has them too, but **Organica cannot read them at test time**
(they are outside its cognition window) while the replay learner can. **So in
`E-pres` the comparison learners have strictly MORE usable access than
Organica.** A win for Organica there is therefore **conservative**: it cannot
be an artifact of unequal access. In the `E-rem` cells the comparison learners
have nothing at all, so those cells measure **Organica's retention**, not the
mechanism head-to-head. **The head-to-head comparison is the `E-pres`
comparison.**

**The predicted dissociation, and it is the interesting one:** in cell 4
(`P-obs × E-pres`) the organism retains everything while the laboratory's
provenance is broken. **That cell separates Q1 from Q2 directly, in the
auditor's own hands.**

---

## 6. The plan

### 6.1 Seeds and sample size

**30 independent seeds**, declared as `SEEDS = [20261101 + i for i in range(30)]` (seeds `20261101` through `20261130`, per Amendment 2, excluding exploratory pilot seed `20261100`).
Each seed is one independent world and one paired comparison, per task.

**There is no post-hoc raising of n.** The analysis in §6.4 is fixed at 30 seeds
and 99% intervals. (Phase L's lesson: a criterion that flips with n measures
the draw. The remedy here is to fix n in advance, not to raise it later.)

### 6.2 Choosing the P-intervention target

**Deterministic rule, fixed in advance, so the target cannot be cherry-picked:**

1. Consider the Layer-1 candidates present in the **final acquisition report**.
2. Keep only those present in **two or more consecutive acquisition cycles**
   (so the target is genuinely re-derived, and its removal is meaningful).
3. Among those, take the one with the **greatest `strength`**.
4. Break ties by **ascending candidate id**.

If no candidate satisfies (2), the seed is recorded as **"no eligible target"**
and excluded — **and the exclusion count is reported**, never silently
dropped.

**P-org** suppresses the target's key from being re-derived and removes its
rows. **P-obs** withholds the target from the auditor's reconstruction and
changes nothing in the organism.

### 6.3 What each learner is, precisely

**Organica.** The engine, frozen, on a scratch database. Readout at the
evaluation point: the compressed graph from `edges_implied_by_structures` over
the surviving candidates, read through the pinned backoff-smoothed form
(§4.3) with $\alpha = 256.0$ fixed by independent calibration on seed `20261099` (Amendment 1 & 2; see `docs/acquisition_alpha_calibration.json`).

**Replay learner — retrieval, no model.**
- **Store:** the identical raw world-event rows Organica was fed (warmup + acquisition cycles 0–109).
- **Test-time procedure:** given context tags `C`, retrieve the stored
  episodes whose tags intersect `C`; the predicted probability for target `b`
  is the fraction of those episodes in which `b` followed.
- **Tuning grid (declared):** context window `{1, 2, 3}` episodes × decay
  half-life `{none, 25, 50, 100}` cycles × smoothing `α ∈ {0.5, 1.0}`.
- **Selected by:** calibrated on independent calibration seed `20261099` (Amendment 2; see `docs/acquisition_baseline_calibration.json`) yielding `window=1, half_life=None, alpha=0.5`.
- **Memory accounting:** holds the same raw rows as Organica. **In `E-rem` those
  same rows are removed from its store** — which is what makes the comparison
  fair.

**Statistical learner — aggregation, a model.** The house family from
`benchmarks/heldout_prediction.py`: **first-order Markov** and **recency-decayed
temporal association** (Beta(0.5, 0.5) smoothing), plus the **cell-level
latent-state counter** for T2.
- **Tuning grid (declared):** `α ∈ {0.1, 0.5, 1.0}` × half-life
  `{none, 25, 50, 100}` cycles × decay window `{none, 200, 400, 800}`.
- **Selected by:** calibrated on independent calibration seed `20261099` (Amendment 2; see `docs/acquisition_baseline_calibration.json`) yielding `alpha=0.1, half_life=None, decay_window=None`.
- **Test-time procedure:** the transition table is frozen at the evaluation
  point; no test-time updates.
- **Memory accounting:** the same raw rows, the same E-rem removal.

**Grouping oracle (T1 reference, computed).** Knows which group the context
belongs to and predicts uniformly within it, with a floor elsewhere. It is
**not** a baseline a learner could implement — it is handed the hidden group
labels — and it is reported to bound *how much of the achievable score is
available to a learner that has learned the grouping but not the law*. On the
transition world it scores **0.2521** against the ceiling's **0.2242**: about
**0.87 of the achievable span**. A "reusable knowledge" claim must beat
*that*, not merely the base rate.

**Bayes ceiling (T2 reference, computed).** The generator's full conditional
distribution, in closed form, with the hidden labels used only for scoring.

### 6.4 The tuning split, the decision rule, and the metric

**The tuning split and independent calibration.** Under the original design, each seed's acquisition phase was split
by cycle to select hyperparameters. Per Amendment 2, to prevent data exposure asymmetries and avoid within-seed
leakage, all hyperparameters (Organica's $\alpha = 256.0$, Replay `(1, None, 0.5)`, and Statistical `(0.1, None, None)`)
are frozen across confirmatory seeds via independent calibration on seed `20261099`.
**No parameter is ever selected on a scoring window or confirmatory seed.**

**The comparator.** The single best configuration across **all** baseline
families, selected via the independent calibration protocol (AGENTS rule 11 — no baseline is
handicapped; the best configuration is used).

**Per seed and per metric**, the paired difference is
`d = score(Organica) − score(comparator)`.

**Interval.** 99% bootstrap CI of the mean paired difference, **10,000
replicates, paired by seed** (the Amendment 3 correction: pair by seed, not
by list position).

**Per-metric verdict.** **Win**: CI lower bound > 0. **Tie**: CI contains 0.
**Loss**: CI upper bound < 0.

**Study-level verdict — exactly one of:**

- **"Reconstruction does work."** Organica **wins on transfer** and does
  **not lose** on retention or revision.
- **"The comparator's mechanism wins."** The comparator **wins on transfer**.
  The report then names which metric it won and which it lost, so the failure
  is specific rather than general.
- **"Inconclusive."** Anything else. The per-metric results are reported in
  full, and the report states exactly which claim is and is not supported.

**Every branch publishes.** A loss publishes as a loss, with the same headline
discipline as a win: the headline matches the check, the resolution of every
check is named, the population of every share is named, and a weaker arm is
reported as weaker.

**Both metric shapes are reported** (§4.3). The decision rule is evaluated on
the house shape; the self-cell shape is co-primary. A verdict that differs
between the two shapes is reported as differing.

### 6.5 Memory accounting — what "same memory budget" means

> **Every learner receives the identical raw experience rows, and the
> identical episode removal.** That is the budget, and it is equalised.

**Derived state is deliberately NOT equalised**, because derived state *is the
mechanism under test* — equalising it would remove the very difference the
experiment measures. The asymmetry that remains is stated, and it runs
**against** Organica: in the `E-pres` cells the comparison learners can read
the raw episodes that Organica's cognition window has already dropped.

---

## 7. The audit build's stop condition

**The audit instrumentation is finished when, and only when, these four things
are true — and not before:**

1. **A5 (field honesty) is closed.** Every numeric field in the trace record
   carries its exact semantics, and a check asserts the rendered record
   contains no mislabelled count. *Implementation: one schema pass over the
   record; a field that cannot be reproduced is removed, not caveated.*
2. **A6 (trace / counterfactual separation) is closed.** The trace contains no
   counterfactual field, and any replay lives in a separate artifact with its
   own label. *Implementation: a grep of the trace schema for counterfactual
   vocabulary, plus the label on the separate artifact.*
3. The three probe arms (default, stress, forced-tie) regenerate with A1–A7
   present, and `tests/test_audit_trace_probe.py` and
   `tests/test_audit_ancestry.py` pass.
4. **Then: tag, freeze, stop.**

**The ceiling.** After that point **no feature may be added to the
instrumentation.** A new requirement raised by this study is recorded in the
study's wish-list, not implemented in the instrumentation. The instrumentation
may be **fixed** if it is found to be wrong, but not **extended**.

**A3, A1, A2, A4 and A7 are closed and are not reopened.**

---

## 8. Instrument requirements, checked before any cell is run

Each must be **proved able to fire**. The two probes and the test file are
committed and runnable:

```bash
python benchmarks/acquisition_endpoint_probe.py         # T1, calibration
python benchmarks/acquisition_compositional_probe.py    # T2, primary
python -m pytest tests/test_acquisition_endpoint.py -q  # 20 proof-of-firing tests
```

| # | Requirement | Where it is checked | Status |
|---|---|---|---|
| 1 | **T1 is non-degenerate** — the ceiling beats the trivial model, and the metric is monotone in structure. | `acquisition_endpoint_probe.py` I1 | PASS |
| 2 | **T1's role is computed, not assumed** — its headroom over the *strongest* simple baseline is measured. | `acquisition_endpoint_probe.py` I2 | PASS — **classified CALIBRATION** (gap +0.0056 vs the strongest baseline; +0.1050 vs the base rate) |
| 3 | **T2 is discriminative** — the gap over the strongest simple baseline has a **lower 99% bound** above 0.05 nats across independent worlds. | `acquisition_compositional_probe.py` G1 | PASS — **+0.1035** [+0.0996, +0.1074] |
| 4 | **The positive control reaches the ceiling** — a learner holding the generating rule. | G2 | PASS |
| 5 | **The broken-rule control fails** — a learner with the wrong law is clearly worse. | G3 | PASS (≥ +0.1015 worse) |
| 6 | **The withheld combination is genuinely withheld**, and the held cell is still observed in training (the world is not rigged). | G4, G4b, G4c, G4d | PASS |
| 7 | **The gap comes from generalization, not estimation error** — the held cell's gap dominates the rest. | G7 | PASS — +0.1963 vs +0.0425 |
| 8 | **The metric and readout are pinned together** — a hard 0/1 read loses to the base rate under log-loss. | I4 | PASS (5.9441 vs 0.3293) |
| 9 | **The three limbs are separate numbers**, under three different laws. | I1/R3 | PASS |
| 10 | **Content-identity detector** — the laboratory can tell a re-instantiated structure from a retained one, by id, from the store log alone. | `tests/test_audit_trace_probe.py` | pending — A5 |
| 11 | **Intervention verification** — after each intervention the laboratory confirms the intervention happened **before** any outcome is interpreted. | study harness | pending |
| 12 | **Removal verification** — after E-rem, the acquisition `events` rows and their `precedes` edges are gone, and the `cooccurrences` / `tag_counts` aggregates are **still present**. | study harness | pending |
| 13 | **Acquisition sufficiency** — at the end of acquisition, the organism's asserted structure must contain a preregistered minimum share of the world's relations. If it does not, that seed is reported as **"acquisition failed"** and its transfer result is **reported as not measurable** — **not** as a transfer failure. | study harness | pending |
| 14 | **Observer invariance** — observer on/off byte-identical, as A4 requires. | A4 | met |
| 15 | **Honesty check** — A3's criterion, in every cell. | A3 | met |
| 16 | **Scratch-only guarantee** — the live `memory.db` is never opened for writing. | study harness | pending |

**If any of these cannot be proved to fire, the study does not run.**

---

## 10. Amendments

### Amendment 1 (2026-10-28): Protocol Calibrations on Deduplication, P-obs, Gate 13, and Tuning Split

1. **Candidate Deduplication (Record-Order Latest)**:
   The engine's `_load_prior_candidates()` returns up to 4,000 recent sleep events ordered by `time DESC`.
   Because sleep events record cumulative candidate snapshots across cycles, candidates with the same unique `id`
   appear repeatedly. Readouts deduplicate by keeping the first encountered occurrence in `recent()` order
   (strictly the newest record by database insertion order). Unnamed candidates (without an `id`) are preserved.

2. **P-obs Observer-Only Scope**:
   In accordance with §5 and §6.2 ("P-obs withholds the target from the auditor's reconstruction and changes nothing
   in the organism"), $P_{\text{obs}}$ does not alter the organism's memory or its task-prediction readout. Instead,
   the target candidate is withheld exclusively from the laboratory auditor's provenance and structural reconstruction
   artifact (`audit_reconstruction`). The task prediction readout $p(b|a)$ operates on the organism's true internal state.

3. **Gate 13 (Acquisition Sufficiency Dual Accounting)**:
   Gate 13 computes both:
   - `asserted_structure_coverage`: the fraction of world ground-truth transition edges asserted by the organism's
     candidate structure (`structure_edges`).
   - `raw_temporal_coverage`: the fraction present in raw transition logs (`mem.temporal_edges(min_count=1)`).
   The preregistered sufficiency gate threshold is pinned at **0.50** (reconciling with `acquisition_harness.py`).
   Coverage is evaluated against `asserted_structure_coverage`. If coverage falls below threshold, the seed is
   explicitly reported as `acquisition_failed = True` and transfer is reported as not measurable rather than a
   transfer failure.

4. **Tuning Data Isolation and Exploratory Seed Separation (Amendment 2)**:
   - **Exclusion of Seed 20261100 from Confirmatory Set**: Seed `20261100` was repeatedly inspected during pilot
     diagnostics, bug remediation (deduplication), and instrumentation audits. To maintain strict confirmatory
     integrity, seed `20261100` is designated an **exploratory pilot seed** and excluded from the confirmatory campaign.
   - **Confirmatory 30-Seed Sample**: The confirmatory campaign sample of 30 seeds is formally defined as
     `SEEDS = [20261101 + i for i in range(30)]` (seeds `20261101` through `20261130`).
   - **Exposure Symmetry and In-Seed Split Accounting**:
     In §6.3 and §6.5, the preregistration specifies that Organica and the comparison learners receive the identical
     raw event stream during acquisition (`cycles 20..109`). With Organica's smoothing parameter $\alpha = 256.0$
     fixed by independent calibration (seed `20261099`), the in-seed acquisition stream is not split to tune Organica.
     To establish strict exposure symmetry, the simple baselines (Replay and Statistical) are likewise fitted on the
     entire acquisition training stream (`train_rows_all`), with their hyperparameters selected on the independent
     calibration seed `20261099` (Replay: `window=1, half_life=None, alpha=0.5`; Statistical: `alpha=0.1, half_life=None, decay_window=None`; see `docs/acquisition_baseline_calibration.json`).
     This ensures all learners are evaluated against identical observation exposure without split contamination.




### Amendment 3 (2026-10-28): Task 2 Stopped at Acquisition Gate (V1 Capacity Boundary on Inspected Seeds)

1. **Gate 13 Diagnostic Preflight Execution & Outcome**:
   In accordance with §8 Requirement 13, acquisition sufficiency (threshold $\ge 0.50$ asserted structure coverage)
   was preflight-checked on exploratory seed `20261100` and diagnostic seeds `20261101` through `20261105`.
   - **All 6 inspected seeds failed Gate 13**: asserted structure coverage was between **0.0% and 2.7% (0 to 3 of 112 edges)**,
     despite raw temporal memory containing **112/112 (100.0%)** of target transition edges.
   - Diagnostic status: Seeds `20261100` through `20261105` are permanently recorded as **diagnostic preflight seeds**.

2. **Causal Mechanism Established**:
   A controlled paired diagnostic experiment (`docs/GATE13-PAIRED-CAPACITY-TEST.md`, `docs/gate13_paired_capacity_test.json`)
   established that the acquisition failure is caused by the frozen engine's Layer-1 prediction capacity cap
   (`MAX_PREDICTIONS = 20` in `organica/sleep.py`). Because within-cell temporal edges occur with higher frequency than
   cross-cell transitions, sorting by raw temporal count saturates all 20 prediction slots with within-cell edges.
   When the cap was raised (treatment: `MAX_PREDICTIONS = 1000`) across the five paired diagnostic seeds (`20261101`–`20261105`),
   the resulting predictions survived downstream natural selection and decay across 110 cycles, achieving **98.2% to 100.0% coverage**
   and clearing Gate 13 on all five tested seeds. This demonstrates that the cap is a causal bottleneck for this engine–task
   pairing on these specific seeds; it does not constitute an empirical measurement of all 30 planned seeds or other task designs.

3. **Study-Level Conclusion on Frozen V1 Engine**:
   - The engine files (`organica/sleep.py`, `organica/memory.py`) remain strictly frozen and unmodified.
   - The preregistered Gate 13 threshold (0.50) is preserved without post-hoc modification.
   - Per §8 Requirement 13, transfer is **not measurable** due to acquisition failure.
   - Task 2 is **stopped at the acquisition gate without running the 600-cell factorial campaign**.
     Transfer was not measured, and this outcome is reported as an acquisition gate failure on the inspected sample
     attributable to the frozen engine's Layer-1 prediction capacity limit under this stimulus structure.

---

## 11. Documents

- `docs/ACQUISITION-ENDPOINT-AUDIT.md` — the full audit that produced this
  revision, with every defect and its measurement.
- `docs/AUDIT-TRACE-SPEC.md` — the trace's specification and limits (§6, §13).
- `docs/USER-MANUAL.md` — §8.19.
- `docs/FACTS-SHEET.md` — §AC.
- `research-journal/phase_g_findings_20261021.md` — §51.
- `AGENTS.md` — rule 25.
- `docs/acquisition_endpoint_audit.json`,
  `docs/acquisition_compositional_gate.json` — the committed artifacts the
  numbers above come from.


