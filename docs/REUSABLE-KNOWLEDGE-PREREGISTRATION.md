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
  coverage** of the **96 relations available during formation**
  (`docs/reusable_knowledge_gate_definitions.json`) must reach **≥ 0.95 on at least 15 of
  the 20 confirmatory seeds**, with precision reported beside it and **not** gated. The
  denominator is the available set, not the law's whole 128: the 32
  withheld relations are excluded from Gate F's numerator and denominator both, because a
  denominator of 128 would cap coverage at 0.75 and no arm could
  ever clear the threshold. Asserting a withheld relation is scored by the transfer limb
  and by nothing in Gate F. See §14.
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
| `V1.1-cap(1000)` | **1,000, fixed** (§15) | **variant**, never V1 |
| ~~`oracle-admitted`~~ | not run | **deferred** — no reproducible candidate-level rule yet; no verdict may reference it (§15) |

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
5. **Calibration Gate F fails on any of the five calibration seeds** (V1.1-cap(1000) only)
   → stop before any confirmatory seed; report *formation not achieved at the calibration
   operating point*, never a transfer result (§15).

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
- That a result **clears the ceiling**. The latent-rule holder (§14) is reported beside every
  score and is not a competitor; a result is measured *against* it, never as beating it.

---

## 10. Build, cost, and what is not built yet

**Not built.** No harness extension exists for this protocol. Five pieces of work,
all in `benchmarks/` (§15):

1. the **conditioned sampler** — two declared cell transitions withheld across warmup *and*
   acquisition, no skipped events; the existing one-transition mask is **not** reused;
2. the **Gate F audit** over the available-relation denominator, with its precision companion;
3. the **held-out scoring pass** at the variant capacity, on the real transfer window;
4. the **latent-rule holder**, implementing the closed-form ceiling of §14;
5. the **comparator sweep** under the naming rule of §4, with the oracle arm deferred.

Machine-readable parameters: `docs/reusable_knowledge_variant.json`.

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

---

## 14. Amendment 1 — Gate F's denominator and the ceiling, fixed before the harness build

**Why this is an amendment.** §2 left Gate F's denominator implicit and §4 called the
oracle-admitted arm a ceiling. Both are fixed here, before any build or cell, in the
owner's terms. **§14 supersedes §2's denominator and §4's ceiling; everything else in
those sections stands**, including the 0.95 / 15-of-20 operating point, the seed sets,
the limb definitions, the uncertainty method and every stop rule. The numbers below are
written from `docs/reusable_knowledge_gate_definitions.json`, generated by
`benchmarks/reusable_knowledge_feasibility.py`, not typed.

**Gate F counts the relations available during formation — 96.**
The law expands to 128 tag-pair relations; the transfer manipulation withholds two of
eight cell transitions, which is 32 tag pairs. So

    coverage = |asserted ∩ available| / 96

A denominator of 128 would cap coverage at 0.75 by construction, because the 32
withheld relations can never appear in formation — the gate would fail every arm and
authorise nothing, which is the "a gate that cannot fire is decoration" failure in its
mirror image. The withheld relations are excluded from numerator and denominator alike.
**They are not, however, excluded from the world:** they are what the transfer limb
scores, and asserting one there is the only place it counts.

**The ceiling is the full latent-rule holder.** Given the law, the successor of cell `c`
is `flip_p(c)` with probability 0.65 and `flip_q(c)` with 0.35, and each tag of the
successor cell appears in the next two-tag event with probability 2/4. So
`P(tag v appears | context cell c) = 0.5 × LAW[k]`, which is **0.325** for a flip_p
successor and **0.175** for a flip_q successor. Every tag belongs to exactly one
cell, so this conditional is exact and needs no estimation: the ceiling is computable in
closed form and cannot be tuned.

**The oracle-admitted arm is a mechanism arm, not a ceiling.** It applies admission
filtering at fixed evidence, which is informative about whether candidate selection is
the binding constraint. Its label in every artifact is `oracle-admitted (mechanism arm)`,
and **no headline may call it the ceiling**. The older acquisition-era oracle-filtered
candidate set is the same, weaker object — weaker because the ceiling above is given the
law itself rather than the support of the answer.

**What the amendment leaves in place.** §9's limits gain one line: a result here may not
be reported as clearing the ceiling, only as being measured against it.

---

## 15. Amendment 2 — the variant's capacity, the calibration gate, and the deferred arm

**Why an amendment.** §4 left V1.1-cap's capacity as "the variant's declared cap" and
carried an oracle-admitted arm whose candidate-level rule was never specified. Both are
settled here, before the harness is built, together with how Gate F governs calibration.
**§15 supersedes §4's capacity column and oracle row, and adds a fifth stop rule**;
everything else stands, including §3.1's transfer definition and §14's ceiling.

**1. The variant is fixed at `MAX_PREDICTIONS = 1,000`.** This is the capacity at which
formation has been demonstrated — the paired capacity test measured asserted coverage of
0.0–2.7 % at 20 against 98.2–100 % at 1,000 — so it is the only capacity with a precedent
behind the Gate F operating point. The value is fixed **now**, not tuned later: the
variant is `V1.1-cap(1000)`, a capacity change and nothing else, built in `benchmarks/`
as a subclass. `organica/` is untouched and `v0.9.0` stays the reference. **A different
capacity is a different variant and needs its own amendment.**

**2. Gate F governs the calibration pass on V1.1 only, and all five calibration seeds
must pass.** Calibration runs `V1.1-cap(1000)` alone on `20261201–20261205`, and Gate F
must clear **≥ 0.95 on all five**. One failure stops the study before any confirmatory
seed is touched, and is reported as *formation not achieved at the calibration operating
point* — never as a transfer result. The confirmatory rule is unchanged: ≥ 0.95 on at
least **15 of 20** seeds, every seed contributing, with the rate reported against its
denominator.

**The asymmetry is deliberate and stated so it cannot be read as convenience.**
Calibration is a **go/no-go with n = 5**, where a single seed is a fifth of the evidence,
so a single failure is disqualifying. Confirmatory is a **measurement with n = 20**, where
one seed is not, so the criterion is a rate with a majority floor — fixed in §2 and not
moved here. Neither rule may be swapped for the other after a result.

**3. The oracle-admitted arm is deferred and is not run.** Its candidate-level admission
rule has never been specified precisely enough to reproduce, and an arm whose mechanism is
a label is precisely how the divergence work lost a generation (journal §87). It is
removed from calibration and confirmatory, **not replaced, not approximated, and no
verdict may reference it**. If it returns, it returns through an amendment that states the
rule and its provenance **before** any cell runs. The comparator set is otherwise
unchanged: **replay, bigram, decayed bigram** as the primary same-experience set, the
**latent-rule holder** as the ceiling, and the **cell counter** as a privileged reference
reported separately.

**4. A build consequence recorded now.** The existing generator and runner use the earlier
**one-transition** mask — one held cell's flip-P transitions, 1 of 8 — together with the
storage-skip pattern §3.1 rejects. The conditioned sampler (two declared transitions, both
formation phases, no skipped events) is therefore **new work in `benchmarks/`**, and the
old mask must not be reused. The five build items are listed in §10.

**What this leaves in place.** The seed sets, §3.1's transfer rule and feasibility result,
the 0.95 threshold, the 98.33 % paired bootstrap, the four existing stop rules, and every
§9 limit. **No cell has run and the harness is still not built.**

---

## 16. Build record and calibration (post-promotion)

**Status statement, not an amendment.** §10's "Not built" described the state
before the harness existed. This section records what was built and what the
Gate F calibration returned. **No hypothesis, gate, arm, seed set or stop rule
is changed here**, and §14's ceiling, §15's three decisions and the 15-of-20
confirmatory rule all stand exactly as committed.

**The five items of §10 are built in `benchmarks/reusable_knowledge.py`.**

1. **The conditioned sampler** generates the formation stream *under* the
   condition: when the law would take a withheld transition the other
   transition from the same context is taken instead, weighted by the law. No
   event is skipped, the hidden state never jumps, and the rejected
   `trainable` mask is not used.
2. **Gate F** counts asserted relations in the **available** set over **96**,
   with its precision companion.
3. **The held-out limbs**: retention over the whole window, and transfer over
   the **withheld relations only** — the study's endpoint.
4. **The latent-rule holder** of §14, closed form.
5. **The comparator sweep**: replay, bigram and decayed bigram, each swept over
   its declared grid with the best configuration selected on a tuning split
   excluded from the fitting rows; the cell counter is the **privileged
   reference**, reported separately. The oracle-admitted arm is **not
   implemented**, per §15.3.

**The harness audit passes, and each check can fail** (`harness_audit`): the
endpoint separates the ceiling from a one-transition learner; Gate F fires on a
readout with ~10 % of the available relations dropped; no withheld transition
appears in any formation exposure; every limb has a denominator. Generator-level
tests are `tests/test_reusable_knowledge.py`.

**Calibration (V1.1-cap(1000), `20261201–20261205`, all five must pass).**

| seed | Gate F (covered / 96) | Organica transfer | best primary | ceiling | Organica − best primary |
|---|---|---|---|---|---|
| 20261201 | 1.0000 (96/96) | 0.5957 | decayed_bigram 0.7709 | 0.3726 | +0.1752 |
| 20261202 | 0.9792 (94/96) | 0.6033 | decayed_bigram 0.7717 | 0.3795 | +0.1684 |
| 20261203 | 0.9896 (95/96) | 0.5985 | decayed_bigram 0.7684 | 0.3691 | +0.1699 |
| 20261204 | 1.0000 (96/96) | 0.6006 | decayed_bigram 0.7622 | 0.3760 | +0.1616 |
| 20261205 | 1.0000 (96/96) | 0.5982 | decayed_bigram 0.7418 | 0.3690 | +0.1436 |

Gate F passes **5 of 5** (minimum coverage 0.9792); the study therefore
proceeds under §15.2. The calibration is a **go/no-go, not a result**: n = 5, one
seed is a fifth of the evidence, and no confirmatory seed was touched — the artifact records
`confirmatory_seeds_touched` as false.
On the transfer limb Organica is below every primary comparator on all five seeds
(worst margin +0.1752 nats) and **above** the ceiling on all five — the ceiling
sits 0.2231 to 0.2294 nats below it — so a substantial part of the
ceiling's advantage is **not** recovered. **That is a characterization of five calibration
seeds and nothing more** — the confirmatory set, not calibration, is what may
carry a verdict.

Artifact: `docs/reusable_knowledge_calibration.json`.

---

## 17. Amendment 3 — the attribution share, and a calibration that names its variant

**Why this is an amendment.** Two things were missing before a campaign could run, and
neither is a change to a hypothesis. First, §4.3's readout sums evidence over **every**
structure type, so a transfer margin can be carried by concepts, loops, phrases or
hypotheses rather than by the Layer-1 transition structure this study forms — and this
protocol had no rule making that share explicit, unlike the formation-utilization
campaign's A7. Second, the harness accepted a capacity override while labelling every
result `V1.1-cap(1000)`, so a calibration at another capacity could have authorised the
confirmatory seeds under a variant label it never ran. **This section adds one criterion
and two guards. It changes no hypothesis, no existing gate, no threshold and no seed.**

### 17.1 The attribution share

**Definition.** On each seed, let `w(type)` be the readout's total edge weight contributed
by candidates of that structure type, taken from the same deduplicated candidate set the
readout uses. Then

    attribution share = w(prediction_candidate) / Σ w(type)

**The minimum is 0.50**, the operating point A7 used for the same question in the
formation-utilization campaign. It is adopted **before any confirmatory seed** and was not
chosen by looking at these numbers; the calibration measurement below is reported as a
diagnostic, and the threshold stands whatever it returned.

**Where it applies.** Calibration: every one of the five seeds must reach the minimum, on
the same all-must-pass logic as Gate F, and a failure stops the study before any
confirmatory seed. Confirmatory: the share is reported for every seed and **every** seed
must reach the minimum; if any seed falls below it, the endpoint is reported as **not
attributable to the learned transition structure**, whatever its margin, and the
per-type decomposition is published beside the failure.

**What it is not.** It measures *where* the readout's evidence sits by structure type. It
does not measure whether that evidence is correct, and it is not a causal attribution: a
high share is necessary for the margin to be about Layer-1, not sufficient for the margin
to be about the law. An unmeasurable share — a readout with no edge weight at all — is
reported as **not measurable and excluded**, never as `0.0` (§9 and AGENTS rule 13).

**The control, and it fires.** A readout holding no Layer-1 evidence at all returns a share
of exactly 0.0, below the minimum. That counterfactual is checked on every cell (audit
`E5`), so the gate is shown to be wired to Layer-1 rather than to a constant. The first
version of this control cut Layer-1's weight to a tenth of itself and returned 0.88 on a
real cell — a control that could not fire, because Layer-1 is most of the weight; it was
replaced, and the replacement is asserted in `tests/test_reusable_knowledge.py`.

**Calibration measurement (diagnostic, not a result).**

| seed | attribution share | Layer-1 weight of total | gate |
|---|---|---|---|
| 20261201 | 0.9866 | 12,105 of 12,270 | PASS |
| 20261202 | 0.9860 | 12,076 of 12,248 | PASS |
| 20261203 | 0.9848 | 12,090 of 12,276 | PASS |
| 20261204 | 0.9863 | 12,115 of 12,283 | PASS |
| 20261205 | 0.9856 | 12,157 of 12,334 | PASS |

### 17.2 The calibration names its variant

- **The label is derived from the capacity.** `variant_label(cap)` returns
  `V1.1-cap(1000)` only at 1,000 and `V1.1-cap(<cap>)` otherwise, so a diagnostic run
  cannot borrow the calibrated name.
- **Calibration refuses another capacity.** A capacity other than 1,000 is a different
  variant (§15.1) and would need its own amendment; `--calibration` exits non-zero instead
  of producing an artifact.
- **The confirmatory guard reads the artifact, not only its pass flag.** Confirmatory seeds
  are refused unless the artifact's `cap` is 1,000, its `variant` is `V1.1-cap(1000)`, its
  seed set is exactly the five calibration seeds, Gate F passed on all five, the harness
  audit passed on all five, and the attribution share reached its minimum on all five.
  Otherwise the refusal names the field that failed.
- **Calibration is reproducible or it is refused.** The engine's candidate ordering is
  hash-sensitive: seed `20261204` scored **0.60055** in one calibration and **0.6025** in
  another, with the code unchanged, and reproduces bit-identically under a fixed
  `PYTHONHASHSEED`. Calibration therefore requires `PYTHONHASHSEED` to be set and records
  its value in the artifact; the canonical artifact records `0`.

### 17.3 The V1 / V1.1 boundary

**V1 is frozen at `v0.9.0`** and remains the archival reference; `organica/` is untouched by
this study and `tests/test_v1_freeze.py` enforces it. **V1.1-cap(1000)** is a
benchmark-side variant: a Layer-1 truncation change only, living entirely in
`benchmarks/`, with its own label, its own artifact (`docs/reusable_knowledge_calibration.json`)
and its own protocol (this document). The two are never pooled: a V1.1 measurement is not a
V1 result, a V1 result is not evidence about V1.1, and a capacity other than 1,000 is a
third variant that has no results here.

**What this leaves in place.** §14's ceiling and denominator, §15's three decisions, the
0.95 threshold, the 15-of-20 confirmatory rule, the four original stop rules and §15's
fifth. **No confirmatory seed has been run.**

---

## 18. Amendment 4 — the revision limb, the trace-derived diagnostic, and the stop it produced

**Why this is an amendment.** §5 defines three limbs and names a revision-held-out window as a
co-primary, but the harness scored only retention and transfer — an omission, not a decision.
And AGENTS rule 18 requires this protocol's criteria to contain a **trace-derived** diagnostic,
while §17's attribution share is a structure-type count that cannot distinguish world-derived
from self-sourced support. Both are fixed here, before any confirmatory seed. **No hypothesis,
limb definition, threshold or seed set is changed; one limb is implemented as §5 already
defined it, and one diagnostic is added.**

### 18.1 The revision limb

The law rotates at cycle 200 (`LAW_R1`). After the formation snapshot the organism is exposed to
the **revision-learning window 200–250** under the rotated law, with the **same two transitions
withheld** by the same conditioned sampler, and its readout is frozen again. It is then scored on
the **revision-test window 250–300**, which it never sees:

- **`revision`** — every pair in that window;
- **`revision_held_out`** — the co-primary: only pairs whose transition was withheld from both
  formation and revision learning.

Conditioning the learning window is what keeps the co-primary held out; without it the window
would show the pair and the limb would be a retention measurement under a new name. Held-out
pairs per seed: **82–110**. Comparators are fitted on formation **plus** revision
learning, so every arm sees the same stream, and the ceiling is the rotated law's closed form.

| arm | revision | revision_held_out |
|---|---|---|
| Organica | 0.4456–0.4630 | 0.6309–0.6618 |
| replay | — | 0.6602–0.7978 |
| bigram | — | 0.7867–0.8940 |
| decayed bigram | — | 0.7529–0.7814 |
| ceiling (rotated law) | — | 0.3193–0.3266 |

### 18.2 The trace-derived diagnostic (D2)

A store-time observer repeats the engine's **own** lookback query
(`SELECT tags, event_type FROM events ORDER BY time DESC LIMIT 3`, which includes the event just
stored) after every write and labels each support transition **world** or **self**, where *self*
means the prior event was the organism's own sleep payload. The reported quantity is the share of
self-sourced support over the edges the readout actually asserts. It is a transition-resolution
measurement, not an aggregate and not an event-level lineage (AGENTS rule 17d).

**The maximum is 0.25, declared before this measurement** and chosen so that no more than a
quarter of a claim's support can be the organism's own output. An unmeasurable share is reported
as not measurable, never as zero.

**The result fails it on every calibration seed.** Formation readout **0.4092–0.4155**;
revision readout **0.4129–0.4167**; sleep rows reached the lookback window
in **218–218** stores per seed, so the mechanism is present and measured rather than
vacuous. At roughly two-fifths self-sourced, the transfer margin cannot be reported as a transfer
result: per AGENTS rule 18 the supporting evidence is not world evidence.

### 18.3 The stop, recorded before any confirmatory seed

The canonical calibration now reads: Gate F **5 of 5**, harness audit **7 of 7 checks on every seed**, revision limbs present on every seed, attribution share clear at 0.9848–0.9866 — and **support provenance 0.4092–0.4155 against a maximum of 0.25**. The artifact therefore records `authorises_confirmatory: false` and the confirmatory set **stays closed**.

This is §6 stop rule 3 operating: an audit outside its declared band means the unit is reported as
**not attributable**, not as a result. §16's sentence that Gate F cleared and the study proceeds is
superseded on this one point and nothing else: it cleared, and the diagnostic stopped the study
before a single confirmatory seed. **No threshold was relaxed after seeing the number**, and no
confirmatory seed was run. Resolving this — for instance by a variant whose readout excludes
self-sourced support, which would be a new amendment and a new measurement — is a decision for the
owner, not a fix to be applied quietly.

---

## 19. Amendment 5 — the per-claim rule is the criterion, and the run-level share is a diagnostic

**Why this is an amendment.** §18.2 measured a **run-level** share: all of the readout's asserted
edges summed into one number. The audit-trace specification's disqualifier is not written that way
— it is a **per-claim rule** (`docs/AUDIT-TRACE-SPEC.md` §11, four fixed conditions), and §3.3
says explicitly that a run-level figure "is **not** a per-claim share". §18.2 also counted
**support references** (one increment per store) rather than **distinct** evidence, which the spec
reserves for the disqualifier. Both are corrected here. **No threshold, limb, seed or hypothesis is
changed; the criterion is replaced with the one that was already committed, and the stop from §18.3
is preserved.**

### 19.1 What is measured

For **each claim** — every Layer-1 prediction and every hypothesis the readout asserts — the
distinct prior events behind its support are split world / self, deduplicated by event id. A claim
passes when all three hold:

1. it has measurable support;
2. **no more of that support is self-sourced than the frozen reference, 17.9 %**;
3. **a majority of it is world-derived.**

The reference is the audit-trace probe's distinct-evidence figure — **802 of 4,481** transitions,
default arm — and it is **not recomputed on this run** (AGENTS rule 19). It is a provisional
calibration value from one world, one policy and one run, and it is labelled as such.

**A run-level average cannot stand in for this.** It averages claims whose evidence is
almost entirely world-derived with claims whose evidence is almost entirely the organism's own
output, and the two can be equally wrong for different reasons.

### 19.2 The result

> **Withdrawn.** The counts in this subsection were computed on a *collapsed* transition
> unit — support keyed by the source event alone — so repeated transitions from one prior
> event to different targets were counted once. The audit-trace specification defines a
> distinct transition by the pair (prior event, target event) (§3.3), so these figures are
> not on the same unit as the frozen reference. §20 restates the measurement on the correct
> unit and supersedes every count below; they are kept only as the record of the defect.

| seed | measurable claims | failing | self-sourced share, min–max |
|---|---|---|---|
| 20261201 | 1277 | 592 (46.4 %) | 0.0000–1.0000 |
| 20261202 | 664 | 348 (52.4 %) | 0.0000–1.0000 |
| 20261203 | 642 | 332 (51.7 %) | 0.0000–1.0000 |
| 20261204 | 604 | 264 (43.7 %) | 0.0000–1.0000 |
| 20261205 | 653 | 336 (51.5 %) | 0.0000–1.0000 |

Every seed fails, and the failures are not marginal: the maximum per-claim share is **1.0000**
(some claims rest entirely on the organism's own output), and roughly half of the measurable claims
exceed a 17.9 % reference that an ordinary belief met during the audit-trace build. On the revision
readout the counts are 290–516 failing claims per seed.

**The run-level diagnostic, restated on distinct evidence:** 0.4209–0.4287 of the
readout's distinct support is self-sourced (6,732–6,806 world vs
4,947–5,051 self transitions), which supersedes §18.2's 0.4092–0.4155 — that figure
counted support references, not distinct evidence. The conclusion does not change; the quantity
does, and the corrected quantity is the one the spec's rule reads.

### 19.3 What this changes, and what it does not

- **The criterion is now the per-claim rule.** `authorises_confirmatory` depends on it; the
  run-level share is reported as a diagnostic and keeps its declared 0.25 band without gating.
- **The stop stands.** The artifact records `authorises_confirmatory: false`; no confirmatory seed
  has run, and none may run until a variant whose readout is world-carried passes this rule on
  calibration.
- **It does not claim harm.** Nothing here shows that self-sourced support caused a wrong
  prediction. It shows that the support behind these claims is not predominantly world-derived, so
  by the pre-committed rule the margins cannot be reported as transfer. That distinction is the
  spec's own and is not blurred here.
- **The audit gained a check, not a verdict.** `E8` verifies that the per-claim rule has measurable
  claims and that its all-self control fails; the audit passes 8 of 8 checks on
  every seed. The failure is the criterion, not the instrument.

**What this leaves in place.** §14's ceiling and denominator, §15's decisions, §17's attribution
share, §18's revision limb and provenance layer, the 0.95 threshold, the 15-of-20 rule and both
stop rules. **No confirmatory seed has been run.**

---

## 20. Amendment 6 — the transition identity, a control that runs the evaluator, and the population the rule governs

§19 got the resolution right and three details wrong. This section corrects the measurement, fixes
the control, and settles the two scope choices §19 left implicit. **No threshold, limb, seed or
hypothesis changes; the stop of §18.3 and §19.3 is preserved and still binding.**

### 20.1 The unit was wrong: a distinct transition is (prior event, target event)

§19 keyed a claim's support by the **source event id** alone, so two transitions out of the same
prior event to different targets counted once. The audit-trace observer identifies a distinct
transition by the pair — `(tag_from, tag_to, prior_event_id, to_event_id)` — and
`docs/AUDIT-TRACE-SPEC.md` §3.3 defines distinct evidence that way. The comparator was therefore
the number the specification freezes, applied to a **different unit**: the same defect rule 19
prohibits in its usual form, one level down. A reference cannot govern a count that is not of the
same kind.

Support is now stored under `(prior_event_id, to_event_id)`. Distinct support rises from about
10,400 to **12,076–12,157** transitions per seed, and the run-level share falls to
**0.4092–0.4155** (7,106–7,143 world against 4,947–5,051
self).

### 20.2 The control must judge claims, not compare a constant

§19's `control_all_self_fails` evaluated `_claim_passes` on two literal arguments and compared the
result to a boolean constant, and `E8` then checked that constant. It could not fail for the reason
a control exists, because it never passed a claim through the evaluator — it was a second inventory
of the expression it was supposed to test.

The control now **builds an all-self support map over the same claim set and passes it through the
same evaluator**, and `E8` checks the arithmetic rather than a flag: the control's claim count must
equal the population's, every one of them must fail, and its maximum share must be 1.0. Measured on
seed 20261201: **1,313 control claims, all
1,313 failing, maximum share 1.0**, and
the same on every seed. `tests/test_reusable_knowledge.py` proves the case directly with a
single-claim all-self map, so the control cannot regress to a constant comparison unnoticed. The
rebuilt `E8` also caught its own breakage during this work — the audit reported failure the moment
the population's field names changed, which is what a check on an instrument should do.

### 20.3 Which claims the rule governs

**Decided: every claim the readout asserts — Layer-1 predictions and hypotheses.** The justification,
stated because the narrower alternative is defensible: the readout's prediction for a *scored* pair
is not computed from a claim about that pair. An unasserted relation falls back through smoothing to
the structure that *is* asserted, so the evidence behind a withheld-pair prediction is the asserted
population, not a claim object that does not exist. A rule governing only claims about the withheld
relations would measure almost nothing and, on this run, sometimes literally nothing: that
sub-population has 0–20 claims, of which 0–20 are measurable, and on
**2 of 5 seeds it has none at all**. A criterion that is unevaluable on two seeds
cannot be the rule that decides the study (rule 13b).

The withheld sub-population is **reported beside it** with its own denominator, as a diagnostic: it
answers "are the scored relations themselves carried by world evidence?" without pretending to be
the criterion. Where it is measurable it fails too (0–20 of 0–20).

### 20.4 How unmeasurable claims count

Unmeasurable claims are **excluded** from the pass/fail count and **reported** (rule 13b: an
unmeasurable quantity is not a zero). **The floor is not refusal-only, and §20 originally said it was — that was wrong.** A floor bounds
how much of the population may be excluded; it does not forbid a pass over what remains. At 50 %, a
pass may cover as little as **half** the asserted claims, and the code would then report
`all_claims_passed: true` with half the readout unjudged. That is a permissive rule, not a
conservative one, and it is stated here as such before it governs anything.

**What the criterion now records, and why 50 %.** Beside `all_seeds_passed` it reports
`pass_coverage` — the share of asserted claims that were measurable and passed — and
`excluded_share`. A unit test pins the worst case: one measurable passing claim beside one
unmeasurable claim yields `evaluable: true`, `all_claims_passed: true` and `pass_coverage: 0.5`, so
the permissive reading is a recorded property rather than an inference. Any future pass must be
quoted with its coverage: a pass at 0.50 is a statement about half the readout, not about the
organism. The value 50 % is chosen because below it the criterion would speak about a minority of the
population the readout actually asserts — the shape of claim rule 24 forbids — and it is a declared
parameter of this protocol, not a derivation from data. On this run it is not binding: measured
fraction **97.11–97.65 %**,
with 16–36 unmeasurable claims per seed, so the rule is
evaluable on all five.

### 20.5 The result on the corrected unit

| seed | asserted claims | measurable | unmeasurable | failing | withheld sub-population, measurable / total |
|---|---|---|---|---|---|
| 20261201 | 1313 | 1277 (97.3 %) | 36 | 576 (45.1 %) | 20 / 20 |
| 20261202 | 680 | 664 (97.6 %) | 16 | 346 (52.1 %) | 14 / 14 |
| 20261203 | 658 | 642 (97.6 %) | 16 | 326 (50.8 %) | 4 / 4 |
| 20261204 | 622 | 604 (97.1 %) | 18 | 254 (42.1 %) | 0 / 0 |
| 20261205 | 669 | 653 (97.6 %) | 16 | 332 (50.8 %) | 0 / 0 |

The failure survives both corrections, and this is the final calibration result of this protocol:
**254–576 of 604–1277 measurable claims fail per seed**
(42.1–52.1 %), with per-claim shares reaching **1.0000**, and the
revision limb adds 282–510 failing claims per seed. §19.2's 264–592 is **withdrawn**
rather than silently replaced: every seed's count falls slightly on the correct unit
(592, 348, 332, 264, 336 → 576, 346, 326, 254, 332), so the defect was not
flattering the failure — which is exactly why it still had to be fixed. The conclusion does not rest
on the exact number either way: the best seed fails 254 of 604
measurable claims (42.1 %) against a reference an ordinary belief met.

**The instrument passes; the criterion fails.** Gate F 5 of 5, audit 8 of 8
checks on every seed including the rebuilt `E8`, `authorises_confirmatory: false`. No confirmatory
seed has run, and none may run until a variant whose readout is world-carried passes this rule on
calibration.

### 20.6 The target event's identity does not come from the window

The per-claim counts rest on the observer's transition identity, and that identity had a second
defect the §20 correction did not touch: the observer read the **target** event id off `rows[0]` of
its own lookback query. That query is
`SELECT rowid, tags, event_type FROM events ORDER BY time DESC LIMIT 3` — the window the engine
itself uses, which has **no `rowid` tiebreak and no index on `time`**, so when timestamps tie the
first row is not guaranteed to be the event just stored (§3.3 of the audit-trace specification).
A store whose target is misread carries its whole transition set under the wrong event, and the
per-claim rule would then judge claims on transitions they did not have.

The fix removes the dependence rather than narrowing it. `store()` already returns the event it
inserted, so the observer now takes `stored_rowid(mem, event.id)` — a keyed lookup on the primary
key — and uses the window query only to identify the **source** events. The engine's own
within-window behaviour is untouched: because `_record_temporal_edges` runs after the insert, the
stored row is legitimately one of the three sources, and it stays one.

Two checks, because only one of them could have caught it on its own:

- **Measured tie arm** (`test_a_tied_window_still_names_the_event_the_store_inserted`): a clock
  returning one timestamp per four stores produces **5 tied windows in 6 stores** on SQLite
  **3.45.1**, and every recorded transition of every store names the row that store inserted. On
  this build the window's first row also **agreed** with the stored row in all 6 stores, so the old
  rule was *latent* here rather than misfiring — an empirical tie arm alone would have acquitted it.
- **Contrary tie order** (`test_target_identity_does_not_come_from_the_window_order`): the
  connection is wrapped so the lookback returns the tied window with the stored row last, an order
  SQLite may legitimately choose. The test asserts that the reordered rows genuinely tie on `time`
  (so the order is one the schema leaves open), that `rows[0]` really is a different event, and
  then requires the recorded target to be the stored one anyway. That is the check that can fire,
  and it is the one that pins the identity.

**Effect on the numbers: none.** Calibration was rerun after the fix and reproduced
`docs/reusable_knowledge_calibration.json` **byte for byte** — the real runs use a wall clock, so no
tied window occurred — and the counts of §20.5 stand unchanged: 254–576 of 604–1277 measurable
claims failing per seed, `authorises_confirmatory: false`, audit 8 of 8. The repair replaces an
implementation observation with a guarantee; the study stays stopped on the criterion, not on the
instrument.

### 20.7 The study is closed at calibration, and what the postmortem can and cannot say

**Closed.** The per-claim rule failed on all five calibration seeds, so this protocol ends here: no
confirmatory seed runs under it, no threshold is changed, and §20.5's verdict and §19.2's withdrawal
stand exactly as written. `authorises_confirmatory` stays `false` and the confirmatory seeds have not
been touched.

**The postmortem** (`docs/reusable_knowledge_postmortem.json`, `--postmortem`) re-reads the same five
calibration cells and classifies every self-sourced transition by what the sleep row actually carries.
A sleep row is a candidate serialised as JSON, so the engine's own tag extractor turns its field names
into tags as well as its content:

| class | what it establishes |
|---|---|
| `claim_restated` | the payload asserts this very pair — circular support |
| `field_name_both` | **both** endpoints are the payload's own field names — the encoding alone |
| `field_name_one` | **one** endpoint is a field name, the other is content — encoding mixed with content, reported apart because it is a different defect |
| `content_unresolved` | neither endpoint is a field name and the payload does not restate the pair — non-schema content, **origin not traced** |
| `meta` | the sleep row is the cycle marker |

**This classifier was corrected before it informed any design decision, and the first version was
too strong.** It called any transition with *one* field-name endpoint `schema`, which read as though
the transition were between two field names; and it called non-schema content `relayed`, which
asserted that the content was world-rooted when nothing in a payload traces back to a world event. The
classes above replace those labels and the two field-name cases are now counted separately, because
the counterfactual depends on which one is excluded.

Nothing about the rule moves: the per-seed failing counts reproduced the calibration exactly
(576, 346, 326, 254, 332), `rule_unchanged: true`, `authorises_confirmatory: false`,
and `_assert_diagnostic` refuses to write an artifact that would authorise anything.

Self-sourced transitions across the five seeds, formation / revision: `field_name_both` 0 / 0;
`field_name_one` 15,576 / 20,876; `content_unresolved` 44,897 / 60,695; `claim_restated` 8 / 7;
`meta` 44 / 46. Of 3,942 formation claims, 3,840 are measurable and
1,834 fail; of 3,640 revision claims, 3,548 are measurable and
1,792 fail.

**What the classes support.**

- **Circular self-support is negligible.** 8 formation and
  7 revision transitions are the payload asserting the very pair the
  claim is about.
- **Pure encoding is not what fails the claims.** Excluding only transitions between two field names
  rescues **0 of 1,834** failing formation claims and **0 of
  1,792** failing revision claims.
- **Field-name involvement is real but cannot rescue a claim either.** Excluding every transition
  that *touches* a field name rescues **0** and **0** as well. There is no gap between the
  two counterfactuals on these cells, and the reason is structural: `field_name_both` is **0**
  formation and **0** revision transitions, because the observer records only after a **world**
  store and a transition's target is therefore always a tag of the event just stored — a field name
  can only ever sit on the prior side. The encoding's entire footprint is `field_name_one`
  (15,576 / 20,876), so the split changes no count here; what it changes is the description,
  because "either endpoint" was never the same claim as "both endpoints" and the old label said the
  latter.

**What the classes do not support.** `content_unresolved` is the largest self class
(44,897 of 60,525 formation and
60,695 of 81,624 revision self transitions), and it establishes
**only** that non-schema content appeared in a sleep row. Its origin is **unresolved**: across the
five seeds the payloads carry 2340 parent ids and
0 event references, and their fields are
`action_type, composites_created, confidence, context, cost, cycle, evidence, expected, expected_outcomes, generation, id, investigation_id, members, observed, parent_ids, priority, probe_payload, ran_at, source, status, strength, target, target_id, target_type, type` with evidence keys `avg_clustering, avg_predictive_reach, cost, decay_cycle, decayed_from, dominance_ratio, edge_count, expected_count, formula, investigation_eig, observed_count, ratio, source_frequency, target_frequency, temporal_count`. Nothing there
names the world events behind the content, so these cells cannot say whether it is world-rooted,
whether it is the organism's own prior assertion in another form, or neither.

**The honest reading.** The disqualifier measures **whether the immediately preceding event was the
world's**. It does not establish that the organism's support is circular, and the postmortem does not
establish that it is world-rooted either — the earlier phrasing claimed more than the data. Both
remain open, and that is the question the next design has to answer, in a separately named variant
with its own preregistration and fresh calibration seeds.
