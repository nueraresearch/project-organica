# Reusable knowledge — protocol draft, for owner decision

**Status: PREREGISTRATION, Revision 2 — committed 2026-11-01.** §0 is signed (Option A),
the four review points are closed (§12), and two defects found in the feasibility record
are corrected here (§13): a seed designated confirmatory had informed the rule selection,
and the check's windows did not match this protocol's schedule. **No cell has run and the
harness is not built.** No cell of this study has run, no harness has been
extended for it, and no engine file may change for it. Organica 1 stays frozen at
`v0.9.0`.

**Revision 1 — 2026-11-01, after owner review.** The owner **authorised Option A** and
required four things settled before promotion to a preregistration: the precision
claim's denominator, the comparators' roles and grants, the definition of transfer, and
the seeds / uncertainty method / calibration split. All four are closed here (§0, §1,
§3.1, §4, §8, §12). **No cell has run, and no harness has been extended.**

**Why it is a draft and not a commitment.** The previous campaign in this line
(formation vs. utilization) was committed before its run and then reported a result
that closed one door and opened this one. Writing the next protocol *after* seeing
which door is open is exactly the situation in which a protocol quietly becomes a
description of what the author now expects. So this document stops at the decision
point and asks the owner to choose before any cell is specified further.

---

## 0. The decision this document asks for

| Option | What it means | Consequence for the record |
|---|---|---|
| **A — authorise `V1.1-cap`** | A formally named diagnostic variant, built entirely in `benchmarks/`, used only for this study | Results are reported as **V1.1**, never as V1; the V1 capacity finding stands unchanged |
| **B — leave V1 frozen** | No variant is built; the capacity limit is reported as a finding about V1 | This protocol does not run and no transfer question is answered |

Both are legitimate. Option B is the cheaper and the more conservative, and it loses
only the ability to say whether formed structure is *usable* at a capacity where it
can be formed at all. Option A buys that answer at the cost of a variant that must
never be confused with the published engine.

**Decision recorded 2026-11-01: Option A authorised.** A formally separate
diagnostic variant, `V1.1-cap`, built in `benchmarks/`, is the direct way to ask
whether *formed* structure is usable, and it does so without touching the V1 finding or
the frozen engine. **What the authorisation does not buy is restated because it will be
tempting:** it does not show that V1 formed the law, that V1.1 is the engine, or that
Organica learns in any human sense.

**Promotion condition, now met and recorded:** this draft becomes a preregistration only
once the three review points — precision's denominator, the comparators' roles, and the
definition of transfer — are closed, and the seed count, uncertainty method and
calibration/confirmatory split are fixed. Those are closed in this revision (§1, §3.1,
§4, §8, §12). **No cell may run until the preregistration is committed, and none has.**

---

## 1. The question, and the cell the record does not have

**Question.** Given structure that the organism formed from experience at a stated
capacity, does that structure support better prediction on **held-out** events than
the strongest simple learner given the **same experience**?

**What the record already contains, as design inputs and not predictions.**

| Fact | Value | Source |
|---|---|---|
| Asserted coverage at the published cap of 20 | 0.0 %–2.7 % of the world's edges | `docs/GATE13-PAIRED-CAPACITY-TEST.md` |
| Asserted coverage at cap 1,000 | 98.2 %–100 %, five diagnostic seeds | same |
| **Precision of the engine's own count-ranked selection**, at any budget measured | **never above 0.3438**, over **36** measured cells (3 seeds × 7 global budgets × 5 per-source budgets); best cell is seed 20261101, top-160 globally: **55 world edges of 160 retained** = 0.34375. Per-source allocation does not help (best 0.314) | `docs/gate13_allocation_rule.json` |
| **Precision of a narrow filtered candidate set**, reported separately and **not** a counter-example | **0.4500**, but on a different denominator: the `world_plus_self_freq` + `ratio` filter retained **20** pairs of which **9** are world edges (coverage **0.0804** = 9 of 112) — and it was **below its own 0.50 gate** | `docs/GATE13-RANKING-CRITERION.md` §"the gate is 0.50" |
| Transfer, both formed arms, both tasks | loss on all four cells (T1 d = −0.0296 / −0.0262; T2 d = −0.0795 / −0.0227) | `docs/formation_utilization_results.md` |
| Retention | loss for both formed arms on both tasks | same |
| Revision | C wins T1 (d = +0.1002), ties T2 (d = +0.0007) | same |
| Fraction of A's gap C closes | 65.2 % (T1), 79.6 % (T2) | same |
| Isolated cost per arm run | 72.2 s | same |

**What is missing**, and what this protocol would supply: a measurement of **use on
events the organism never saw during formation**, at a capacity where formation is
demonstrated rather than assumed, against bars that are given the same experience and
whose grants are named.

**What a result here could support.** A statement of the form: *at capacity X, on
world family Y, formed structure did (or did not) beat the named comparators on
retention, transfer, and revision, by the measured margins.* **What it cannot
support:** that the organism discovered the law (an admitted arm is a ceiling, not a
learner), that V2 is authorised, that the result generalizes beyond the world family,
or any claim at all about the frozen V1's capacity.

---

## 2. The formation gate — and why it is the first thing, not the last

The acquisition study's lesson is that a transfer score is uninterpretable when the
structure was never formed. So formation is gated **before** any limb is scored, and
the gate is defined so that it can fail loudly.

- **Gate F.** On the final acquisition store of the arm being tested, **asserted
  coverage** of the generator's permitted transitions must reach a threshold fixed
  before the run. Proposed: **≥ 0.95 coverage on at least 15 of 20 seeds**, with
  precision reported beside it and **not** gated.
- **Provenance of the threshold.** It is derived from calibration data only — the
  measured 98.2 %–100 % at cap 1,000 — and never recomputed on the run it judges.
- **If Gate F fails**, the study **stops**. The result is reported as *formation not
  achieved at this capacity*, which is **not measurable** for the transfer question
  and must never be reported as a transfer failure.
- **Attribution requirement.** Every unit records candidate-space **precision** beside
  coverage, so that a null can be attributed to formation, to ranking, or to use, and
  not left to one undifferentiated "it lost".

---

## 3. The world, and why this one

- **The compositional world** (`benchmarks/acquisition_compositional.py`) — not the
  group world, and not `organica/ground_truth_worlds.py`, which is the older
  hidden-cause generator: four cells from two latent factors, four tags per cell, and a
  law in which the successor differs from the context in exactly one factor. Its law is
  **eight directed cell transitions**, which expand to **128 distinct tag pairs**. The
  **112 cross-cell edges** belong to the other task's generator
  (`benchmarks/acquisition_world.py`, four groups); the two counts must never stand in
  for each other.
- **Scored events are outside the formation window**, with the same endpoint for every
  learner: log-loss over a fixed denominator (`|contexts| × |vocabulary|`), the same
  labels throughout, the readout calibrated on calibration seeds and frozen before the
  run. Whether that limb may be called *transfer* is decided by §3.1, not by taste.
- **Revision is a structural change at a fixed point**, with its own held-out window,
  so that "revision" cannot be scored as "the old structure still happened to be
  right".

**Requirement the world must meet before the study runs:** the target relation must be
learnable **at the arm's own capacity** — demonstrated by Gate F on the calibration
seeds, not assumed from the world's design.

---

### 3.1 What is withheld — the manipulation that makes "transfer" a claim

**A later sample from the same distribution is held-out generalization, not transfer.**
The distinction is fixed here so it cannot be made in the write-up:

- **Held-out generalization** — events drawn from the **same** law as formation, after the
  formation window. Nothing about the relation was withheld; only individual events are
  new. This is worth measuring, and it is **not** called transfer.
- **Transfer** — prediction on combinations the organism **never had the opportunity to
  observe**. To earn the word, the design must **withhold a declared set of the law's
  transitions from all formation exposure** and score prediction on those.

**The unit, settled on the generator's terms.** A *transition* is a **directed cell
transition** — one context cell plus one flip type — of which the compositional law has
**8**, expanding to **128** distinct tag pairs. Withholding 25 % therefore means **two of
the eight**; the **112** is the group world's tag-level count and is not a quantity of this
world.

**Conditioned sampling, not a mask.** The generator's `trainable` mask
(`benchmarks/acquisition_compositional.py:210`) is rejected: it still generates the withheld
event and advances the hidden state, and the runner only skips *storing* it, so stored
events become adjacent across a gap the world never had. The sampler must **resample among
the permitted transitions** of the current cell and store every event it generates.

**The schedule the check uses is this protocol's schedule**, taken from the module rather
than assumed: warmup cycles 0–20 and
acquisition cycles 20–110 are
**all** formation exposure — **110 cycles**, 8 events per cycle — and the transfer limb is scored on cycles
150–200, a **50-cycle window**. Withheld transitions must be absent from every formation phase, not only
from acquisition.

**Feasibility, generator-only, run before any build.**
`benchmarks/reusable_knowledge_feasibility.py` imports the generator and walks its law — no
engine, no study cell — and writes `docs/reusable_knowledge_feasibility.json`. It uses only
the **calibration seeds `20261201–20261205`** (§8), never a confirmatory seed. Seven criteria
were fixed before any subset was evaluated: strong connectivity; in-degree and out-degree at
least 1 for every cell; all four cells present as contexts; every permitted transition
instantiated at least once; stored events genuinely consecutive; every formation phase
conditioned; and at least **20** instances of each withheld
transition in the **real 50-cycle transfer window** of the generated world.

**Result.** All **28** two-transition subsets were evaluated against those
criteria and **16 are feasible** on every calibration seed. The rule is
**`(0, 0)` flip_p and `(0, 1)` flip_q**, the first feasible subset in the generator's own ordering, and it is the
same pair the earlier generation selected — now confirmed on design seeds under this
schedule rather than on a confirmatory seed under a mismatched one. Its check: connected;
every cell in and out; all four contexts present; the sparsest permitted transition seen
**38** times; consecutive pairs genuine; 831 formation events conditioned across
the five seeds; and **at least 30** instances of each withheld transition in the
transfer window, against a floor of 20.

**The fallback, unchanged.** Had no subset been feasible, the limb would be reported as
**held-out generalization** and the word *transfer* would not appear in the result. The
check exists so that decision cannot be made after seeing a score.

## 4. Arms and comparators — same experience, named grants

**Arms.**

| Arm | Capacity | Label in every artifact |
|---|---|---|
| `V1` | 20 (as published) | frozen reference |
| `V1.1-cap` | the variant's declared cap | **variant**, never V1 |
| `oracle-admitted` | as `V1.1-cap` | **ceiling**, never a learning claim |

**Primary comparators — the same-experience set.** Each is swept over a declared
hyperparameter grid, its **best** score selected on a tuning split, and each is reported
with what it is granted beside its score. These, and only these, define the bar:

- episodic **replay** — granted: the event history, nothing more;
- **bigram** — granted: adjacent-pair counts;
- **decayed bigram** — granted: the same counts with a declared decay constant.

**Privileged reference — reported separately, never the bar.** A **cell-level
latent-state counter** *is* run, because it is informative, but it receives the
generator's latent cell map and is therefore a **privileged reference**, not a
same-experience comparator. It must appear in a separate block, labelled with its grant,
and **no verdict may be computed against it**. The phrase "data-only learner" is
forbidden for it and for any comparator whose grant includes latent structure; the
utilization campaign recorded that phrase as a naming defect when this exact counter was
its T2 bar.

**Requirement.** Every arm and every comparator sees the **same event stream** in the
same order. No comparator is handicapped by a different experience, and no arm is
granted an experience the comparators lack.

---

## 5. The three limbs, scored separately

- **Retention** — prediction on events after formation, within the learned regime.
- **Transfer** — prediction on held-out events from the same law, never shown during
  formation.
- **Revision** — prediction after the law changes, plus the revision-held-out window as
  a co-primary.

**Rules fixed in advance.** Direction is `d = bar − arm`, positive favouring the arm.
Intervals are paired by seed, with the uncertainty level and replicate count fixed
before the run. **No limb is averaged into a total**, and a verdict must name the limb
that failed — "three of four limbs" is not a score.

---

## 6. Stop rules

The study stops, and reports what it has, if **any** of the following occurs:

1. **Gate F fails** on the tested arm → formation not achieved; transfer not measurable.
2. **A comparator's tuning is not complete** before scoring → the comparison is invalid.
3. **An audit fails** — leakage, denominator, arm differential, or attribution share
   outside its declared band → the unit is reported as not attributable, not as a result.
4. **The readout's span is inadequate** on the world as built → the endpoint cannot see
   the effect and the study does not proceed to scoring.

And, after the run begins: **no raising n**, no re-reading a criterion, no restating a
gate after seeing it, and no limb added to rescue a verdict.

---

## 7. Capacity and ordering are variants, never adjustments

- **Any** change to `MAX_PREDICTIONS`, to candidate ordering, or to the site at which
  candidate construction is canonicalised is a **variant**: formally named
  (`V1.1-…`), built **only** in `benchmarks/` as a subclass, labelled in every artifact
  and every document, and never described as V1.
- The frozen reference stays `v0.9.0`, `tests/test_v1_freeze.py` stays green, and no
  variant may change the behaviour of the frozen engine files.
- **A variant result answers a question about the variant.** The V1 finding — that at
  the published capacity the organism does not form the world's relations — remains as
  recorded, and a variant's success does not erase it.
- **Ordering interventions are closed for now.** The hash-order line was closed as
  inadmissible on 2026-11-01 (journal §87–§88, `docs/divergence_arm_b_prime_AUDIT.md`).
  No ordering intervention may be introduced into this protocol as a silent
  improvement, and a capacity variant may not smuggle one in.

---

## 8. Population, seeds, and what counts as fresh

**Calibration split — seeds `20261201–20261205`, five seeds.** Used to fix Gate F's
operating point, the readout's smoothing constant and each comparator's hyperparameters.
They are also the **only** seeds the generator-only feasibility check (§3.1) used, so no
confirmatory seed informed any design choice. **No confirmatory score is ever computed on
them.**

**Diagnostic and burned — seed `20261206`.** The first published generation of the
feasibility check used this seed to select the withholding rule, so it cannot serve as a
confirmatory seed. It is recorded as **diagnostic**, excluded from every scored limb, and
not replaced by re-labelling any seed that has already been touched.

**Confirmatory split — seeds `20261207–20261226`, twenty seeds, n = 20, fixed.** These are
the only seeds any scored limb uses. All are disjoint from `20261101–20261130` (formation
vs. utilization), from every seed in the divergence pairs, and from the burned seed above.

**Uncertainty method, fixed in advance.** Paired percentile bootstrap over the twenty
confirmatory seeds, **10,000 replicates**, **98.33 % intervals** — the level used for
three limbs elsewhere in this record (1 − 0.05/3). A limb is called a win only when the
**lower** bound clears zero in the arm's favour; a loss when the upper bound is below
zero; otherwise it is a **tie**, and ties are reported as ties.

**Rules that do not bend.** A later increase in n is a **new study**, not a continuation.
No seed may be added because a result was close. If an interval straddles zero, that is
the result.

---

## 9. What this protocol cannot support, stated before it runs

- That the organism **discovered** the law — an admitted arm is a ceiling.
- That **V2 is authorised**, or that any V2 design follows from it.
- **Generality** beyond the tested world family and the tested capacity.
- Any statement about the **frozen V1's** capability at capacity 20, beyond the finding
  already recorded.
- Any **ordering** claim: hash-order effects are out of scope here and closed elsewhere.
- Any claim that "reusable knowledge" in the human sense has been demonstrated. What is
  measured is prediction on held-out events from the same generative law.

---

## 10. Build, cost, and what is not built yet

**Not built.** No harness extension exists for this protocol. The draft implies three
pieces of work, all in `benchmarks/`: a held-out scoring pass at the variant capacity,
the Gate F audit with its precision companion, and the comparator sweep under the
naming rule of §4.

**Cost, as a design input rather than a promise.** The utilization campaign measured
72.2 s per isolated arm run, 205–225 s under contention, and 12.72 worker-hours for a
240-arm, 180-fit campaign (`docs/formation_utilization_results.md` §7). A study at
similar scale is therefore tens of worker-hours, not minutes.

**Stop condition for the build.** The build closes when those three pieces exist and a
calibration run passes Gate F. It does not grow afterwards; a defect may be fixed, a
feature may not be added.

---

## 11. Amendments

Append and disclose. An amendment states what it supersedes, what it leaves in place,
and whether any cell has already run. No amendment may alter §5's limb definitions,
§6's stop rules, or §9's limits after a result is seen.

---

## 12. Owner review, 2026-11-01 — the three reconciliations

**1. Precision.** The draft's unqualified "never above 0.3438" was too wide. It is true
of the **engine's own count-ranked selection** over the 36 measured cells in
`docs/gate13_allocation_rule.json`, whose best cell is 55 world edges of 160 retained.
The **0.4500** in the ranking record is a different quantity on a different denominator:
a `world_plus_self_freq` + `ratio` filter retaining 20 pairs, 9 of them world edges
(coverage 0.0804), below its own 0.50 gate. Both are now stated in §1 with their
denominators, and neither is used as the other.

**2. Comparator roles.** Replay, bigram and decayed bigram are promoted to the **primary
same-experience set** and they alone define the bar. The cell counter is demoted to a
**privileged reference**, reported in its own block with its grant named, and no verdict
is computed against it — so it can no longer become "the strongest learner given the same
experience" by relabelling.

**3. Transfer.** §3.1 now defines the manipulation rather than the sample: 25 % of the
law's cross-cell edges are withheld from the formation stream by a rule stated in
advance, with a minimum denominator of 20 transitions per seed, and a limb that cannot
honour that rule is called **held-out generalization** instead. A later draw from the
same law is no longer allowed to carry the word.

**What remains open.** Nothing in this section; the four items the owner required are
closed. What is *not* done is the build (§10), and it begins only after this document is
promoted to a preregistration.

---

## 13. Corrective revision and promotion — 2026-11-01

**Defect 1 — a confirmatory seed selected the rule.** The first published feasibility
generation used `20261206` as its test seed while checking all 28 candidate rules, and
§8 had designated `20261206–20261225` as confirmatory. A seed that informed a design
choice cannot then serve as an untouched confirmatory seed, so the check was re-run on
the **calibration seeds only** (`20261201–20261205`), and `20261206` is now marked
**diagnostic and burned**, with the confirmatory set moved to `20261207–20261226` so that
**n = 20 is preserved** rather than quietly reduced to 19.

**Defect 2 — the check's schedule was not this protocol's schedule.** The first
generation used 90 formation cycles and a 100-cycle test window. The module's schedule is
warmup `0–19` **plus** acquisition `20–109` as formation exposure — 110 cycles — and a
transfer window of cycles `150–199`, 50 cycles. The check now derives formation cover
from `PHASE_ACQUISITION[1]`, conditions **both** formation phases, and verifies the
20-instance floor inside the **real generated world's** transfer window rather than in a
100-cycle synthetic one.

**What survived, and what that means.** Under the corrected conditions — design seeds
only, formation = warmup + acquisition, floor in the real 50-cycle window — **16 of 28**
subsets remain feasible and the adopted pair is unchanged: `(0,0)` flip_p with `(0,1)`
flip_q, the sparsest permitted transition seen **38** times, and at least **30** instances
of each withheld transition in the transfer window. The pair therefore survives on
evidence that is independent of the burned seed; its earlier selection is superseded, not
silently reused.

**Promotion.** §0 is signed, §12 closes the four review points, and §13 closes the two
defects. This document is a **preregistration**. The next steps, in order: build the
harness (§10), run the calibration pass on `20261201–20261205`, and only then run the
confirmatory cells on `20261207–20261226`. **No cell has run and no harness exists.**
