# The acquisition experiment — pre-registration

**Revision 2. Supersedes Revision 1 (2026-10-26) in full.**
**Revision 2 is committed BEFORE any cell is run.** Nothing here has been
measured against a factorial cell.

**What Revision 1 got wrong, and why Revision 2 exists.** Revision 1 was
reviewed and five defects were found. They are recorded here rather than
quietly fixed:

| # | Defect in Revision 1 | Correction in Revision 2 |
|---|---|---|
| 1 | The task metric was **DI** (`late_structure_retained / late_structure_available`). DI measures **structural displacement**, not whether a belief predicts the world. It was the wrong metric for a prediction claim. | §4 replaces it with a **ground-truth prediction score** and names exactly which predictions are scored. |
| 2 | "Source experiences removed" did not say what derived memory survives. Ingest also accumulates **`cooccurrences`** and **`tag_counts`** (`memory.py:282`, `306`), which outlive the event rows. | §3.3 names the condition **"episode removal with learned graph retained"** and states exactly what remains. |
| 3 | The cell matrix was not specified: the heading said "2 × 2 × 3", §4.3 added a baseline on top of six cells, and the prediction table listed only five. | §5 publishes **one complete table** with the exact number of runs and a prediction for every cell. |
| 4 | Not an executable plan: no pinned target relation, warm-up, follow-up, seeds, sample size, decision rule, or baseline definitions. | §4, §6, §7, §8 pin all of them. |
| 5 | The audit build had no stop condition, so it could become the next open-ended phase. | §10 gives it a short, explicit one. |

**Owner direction (2026-10-26).** V2 is not cut. The live study is not
restarted. V2–V5 are not run. No further months of audit-infrastructure
refinement. The roadmap is: **finish the audit build → freeze it → run the
acquisition experiment → compare against the replay learner → publish whatever
happens → only then discuss V2.**

---

## 1. The question, and the claim it can support

**The question.** Can a controlled experience leave behind a structure that
helps on later events, **after the raw episodes that produced it are
unavailable**?

**The claim this study can support, stated at its true strength:**

> **Does this frozen, development-first system turn experience into a
> representation that predicts a genuinely held-out outcome after raw episodes
> are unavailable?**

**What it cannot support, stated up front:**

- **Not** that Organica learns *like a human*. Its inputs are tokenized events;
  its development rules, layer ladder, thresholds, attention formula and
  candidate types are all **designer-specified**.
- **Not** that it learns at all, in the sense the project's own Phase L
  protocol would accept — that verdict is a separate question, and Phase L's
  was `H3-L — INCONCLUSIVE`.
- **Not** anything biological. "Persistent reconstruction" is a description of
  a mechanism in this code; the resemblance to how some biological systems are
  described is a **motivation for the experiment, never a claim about its
  result**.
- **Not** that the trace reconstructs *developmental history*. It reconstructs
  the **present** lineage of surviving structures (§2.1).

---

## 2. What is already known — design inputs, not predictions

Two read-only diagnostic probes were run before this design was written. They
are **design inputs**, and every prediction in §6 is about the factorial
cells, which have not been run.

### 2.1 The trace shows the present lineage, not the historical one

A candidate's identity is a content hash — `_make_id` is
`sha256("|".join(key_parts))[:8]` (`sleep.py:45-48`) — but the identity **does
not include the parent set**. Higher-layer structures are re-formed every
cycle with parents **recomputed** from current state (`sleep.py:1432`, `1450`,
`1467`, `1384`). The same content identity can therefore carry a **different
lineage** later — measured, `meta_concept`'s parent set changed in 57 of 220
structure-cycles while its own identity was unchanged.

**Consequence:** the trace reconstructs the organism's **current** descent, not
the history of that descent.

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
**missing record**, never as "no parent", with the window bound stated.

### 3.3 The E-rem condition, named exactly

**E-rem is *episode removal with learned graph retained*.** It is never
described as "the originating experience is gone" without that qualifier.

**Removed, from every learner's store, identically:**

- the `events` rows for the acquisition-phase world events, and
- the `precedes` rows whose endpoints are among those events.

**Retained, explicitly and deliberately:**

| Retained | Why it is retained |
|---|---|
| the `cooccurrences` table | ingest accumulates it on every world event (`memory.py:306`); it is a **compressed summary of the episodes**, and deleting the episodes does not delete the summary |
| the `tag_counts` table | likewise (`memory.py:282`, `287`) — a marginal frequency, not an episode |
| all `sleep` candidate rows and the cognition window | these are the organism's own structures; the point of the condition is to test what survives *as structure* |
| every derived structure the organism holds | ditto |

**Consequence, stated plainly:** E-rem is a **compressed-experience** condition,
not a blank-slate condition. It asks: **can the organism use a representation
when the episodes are gone but the compressed graph remains?** It does **not**
ask whether the organism can learn from nothing. (A stronger condition that
also removes `cooccurrences` and `tag_counts` is a named **future option**,
`E-blank`; it is **not** part of this design and is not counted in §5.)

**The same rows are removed from every learner's store.** This is the
requirement that makes the comparison mean what it says: otherwise the
experiment would compare *different access to evidence* rather than
*reconstruction against replay*.

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

### 4.1 World generator and target relation

**Generator:** `organica.ground_truth_worlds.generate_cause_world`.

| Parameter | Value | Reason |
|---|---|---|
| `cycles` | **220** | the phase boundaries in §4.3 |
| `events_per_cycle` | **8** | the probe's value; unchanged |
| `regime_cycles` | **110** | so the regime switch lands exactly on the follow-up boundary (§4.3) |
| `noise_rate` | **0.10** | the generator's default; gives the negative class |
| `overlap_features` | **0** | no shared vocabulary between causes |
| `false_correlation_rate` | **0.0** | no decoy pairs; the world is not adversarial |
| `seed` | per seed, §6.1 | |

**Target relation:** the **gold same-cause pair set**, `gold_same_cause_pairs` —
the feature pairs that genuinely co-occur because they share a latent cause.
The generator computes it; the researcher does not choose it.

### 4.2 The endpoint — a ground-truth prediction score

**This replaces Revision 1's DI.** DI is a structural displacement ratio and
does not measure prediction.

**Prediction unit.** For each evaluation event `e_{t+1}` and each tag `v` in a
**fixed vocabulary**, predict whether `v` appears in `e_{t+1}`, given the
context = the tags of `e_t`.

**Ground truth.** The **observed** tags of `e_{t+1}`. The hidden cause and
regime labels are never fed to any learner; they are used only to verify the
world and to check the rare-cause structure (§8).

**Fixed denominator.** `|contexts| × |vocabulary|`. Every learner is scored on
exactly the same labels, so no learner can gain by scoring on a different set.
This is the scoring shape already used in
`benchmarks/heldout_prediction.py` → `_score`.

**Vocabulary.** The set of tags appearing in the **acquisition-phase** events,
fixed before the follow-up begins. Tags appearing only in the follow-up are
counted and reported separately (the house pattern's "novelty" block).

**Primary metric.** **F1 at a 0.5 decision threshold** on the fixed label set.
**Co-reported:** precision, recall, **balanced accuracy** (the label set is
imbalanced, so F1 alone would flatter a selective learner), and **Brier**.
The score is computed with the house `_score` function, unmodified, so the
metric is not redefined for this study.

**Organica's prediction function.** For a context tag `a` and a target tag
`b`, the probability that `b` follows is **1.0 if the edge (a, b) is in the
compressed graph** — `edges_implied_by_structures` over the surviving
candidates — and **0.0 otherwise**. Binary, with no partial credit for weak
assertions: the conservative choice, and the same readout the function's own
docstring describes ("what the organism would have to work with if it kept
only its own abstractions and threw the raw event stream away").

### 4.3 The three scores

| Phase | Cycles | Regime | What happens |
|---|---|---|---|
| **Warm-up** | 0–19 | r0 | the engine bootstraps; the vocabulary is fixed at the end of this phase |
| **Acquisition** | 20–109 | r0 | the episodes under study; **E-rem removes these** |
| **Follow-up** | 110–219 | r1 | held-out episodes; the regime switches at cycle 110, exactly on the boundary |

The follow-up is subdivided into three **scoring windows**:

| Window | Cycles | State used | Score |
|---|---|---|---|
| **Transfer-scored** | 110–149 | the learner's state **frozen at the end of acquisition** | **RETENTION** — does the acquired structure still predict the world it was acquired from, after the source episodes are removed? |
| **Revision-window** | 150–189 | continued learning | the learner updates |
| **Revision-scored** | 190–219 | the state after the revision window | **REVISION** — the score after continued learning, against the frozen state |

**TRANSFER** is scored on the **transfer-scored** window, in regime r1 — a
regime the acquisition phase saw only at its 15 % minority rate. The gold
pairs of *both* causes remain true across the switch, so the acquired
structure is still *usable*; what changes is which cause is dominant. So
transfer asks: **does the acquired structure apply to a regime it barely
experienced?**

**Score per independent world or seed, not per cycle.** The unit of analysis
is the **seed**: each seed contributes one score per metric per learner, and
all statistics are over seeds, paired by seed. (This is the same correction
Phase L's Amendment 3 made to the bootstrap's pairing.)

**A note on the three names.** Retention, transfer and revision are three
*different* questions about the same run, and none of them substitutes for
another. A learner can retain without transferring (it knows the old regime
perfectly and cannot use it in the new one), or transfer without revising.

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

**The exact number of runs, per seed:**

| Learner | Cells | Runs per seed |
|---|---|---|
| **Organica** | P ∈ {none, org, obs} × E ∈ {pres, rem} | **6** |
| **Replay learner** | E ∈ {pres, rem} | **2** |
| **Statistical learner** | E ∈ {pres, rem} | **2** |
| **Fixed-rule ceiling** | — | **0** (a reference computed from the generator, not a run) |
| | **Total** | **10 runs per seed** |

With **30 seeds** (§6.1), that is **180 engine runs** (the baselines are pure
computation over the stored rows) and **300 learner-scores**.

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
| — | reference | Fixed-rule ceiling | n/a | n/a | the ceiling |

**Read the last four rows carefully — they are where the mechanism question
lives.** In the `E-pres` cells the comparison learners have the raw episodes
**and** Organica has them too, but **Organica cannot read them at test time**
(they are outside its cognition window) while the replay learner can. **So in
`E-pres` the comparison learners have strictly MORE usable access than
Organica.** A win for Organica there is therefore **conservative**: it cannot
be an artefact of unequal access. In the `E-rem` cells the comparison learners
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

**30 independent seeds**, declared as `SEEDS = [20261100 + i for i in range(30)]`.
Each seed is one independent world and one paired comparison.

**There is no post-hoc raising of n.** The analysis in §8 is fixed at 30 seeds
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
the surviving candidates (§4.2).

**Replay learner — retrieval, no model.**
- **Store:** the identical raw world-event rows Organica was fed.
- **Test-time procedure:** given context tags `C`, retrieve the stored
  episodes whose tags intersect `C`; the predicted probability for target `b`
  is the fraction of those episodes in which `b` followed.
- **Tuning grid (declared):** context window `{1, 2, 3}` episodes × decay
  half-life `{none, 25, 50, 100}` cycles × smoothing `α ∈ {0.5, 1.0}`.
- **Selected by:** the best configuration on the **tuning split** (§6.4), never
  on the test windows.
- **Memory accounting:** holds the same raw rows as Organica. **In `E-rem` those
  same rows are removed from its store** — which is what makes the comparison
  fair.

**Statistical learner — aggregation, a model.**
- The house family from `benchmarks/heldout_prediction.py`: **first-order
  Markov** and **recency-decayed temporal association** (Beta(0.5, 0.5)
  smoothing, as in that file).
- **Tuning grid (declared):** window `{1, 2, 3}` × half-life
  `{none, 25, 50, 100}` cycles × `α ∈ {0.5, 1.0}`.
- **Test-time procedure:** the transition table is frozen at the evaluation
  point; no test-time updates.
- **Memory accounting:** the same raw rows, the same E-rem removal.

**Fixed-rule ceiling.** The score obtained by a system that knows the
generator's true gold pair set. Computed, not run.

### 6.4 The tuning split

Each seed's acquisition phase is split **by cycle**: the first 60 % of the
acquisition cycles are the **tuning split** and the last 40 % are the
**fit split**. Baseline configurations are selected on the tuning split and
then scored on the follow-up windows. **No baseline parameter is ever selected
on a scoring window.**

### 6.5 Memory accounting — what "same memory budget" means

> **Every learner receives the identical raw experience rows, and the identical
> episode removal.** That is the budget, and it is equalised.

**Derived state is deliberately NOT equalised**, because derived state *is the
mechanism under test* — equalising it would remove the very difference the
experiment measures. The asymmetry that remains is stated, and it runs
**against** Organica: in the `E-pres` cells the comparison learners can read
the raw episodes that Organica's cognition window has already dropped.

**No baseline is handicapped** (AGENTS rule 11): every baseline is swept over
its declared grid and its **best** score is used. The comparator in §8 is the
single best configuration across **both** baseline families, selected on the
tuning split.

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

## 8. The decision rule, fixed in advance

**Comparator.** The single best configuration across both baseline families,
selected on the tuning split (§6.4).

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

---

## 9. Instrument requirements, checked before any cell is run

Each must be **proved able to fire**:

1. **Content-identity detector** — the laboratory can tell a re-instantiated
   structure from a retained one, by id, from the store log alone.
2. **Intervention verification** — after each intervention the laboratory
   confirms the intervention happened (the target is absent from the window;
   the episodes are absent from `events`) **before** any outcome is
   interpreted. **A perturbation that did not happen is not a null result.**
3. **Removal verification** — after E-rem, the acquisition `events` rows and
   their `precedes` edges are gone, and the `cooccurrences` / `tag_counts`
   aggregates are **still present** (this is the condition's definition, so it
   is checked, not assumed).
4. **Acquisition sufficiency** — at the end of acquisition, the organism's
   asserted structure must contain the **rare cause's** gold pairs at a
   preregistered minimum rate (≥ 50 % of the rare cause's gold pairs asserted).
   If it does not, that seed is reported as **"acquisition failed"** and the
   transfer result for that seed is **reported as not measurable** — **not**
   as a transfer failure. *(This is the "verify before interpreting" rule, and
   it is what keeps the transfer test from being vacuously unachievable.)*
5. **Observer invariance** — observer on/off byte-identical, as A4 requires.
6. **Honesty check** — A3's criterion, in every cell.
7. **Scratch-only guarantee** — the live `memory.db` is never opened for
   writing.

**If any of these cannot be proved to fire, the study does not run.**

---

## 10. Documents

- `docs/AUDIT-TRACE-SPEC.md` — the trace's specification and limits (§6, §13).
- `docs/USER-MANUAL.md` — §8.17.
- `docs/FACTS-SHEET.md` — §AA23–§AA26.
- `research-journal/phase_g_findings_20261021.md` — §49.
- `AGENTS.md` — rule 23.
