# Reusable knowledge — protocol draft, for owner decision

**Status: DRAFT, 2026-11-01. This is not a preregistration and nothing in it may be
built or run until §0 is signed.** No cell of this study has run, no harness has been
extended for it, and no engine file may change for it. Organica 1 stays frozen at
`v0.9.0`.

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

**Nothing below may be run under either option until the owner has signed this
section with a date and a one-line rationale.**

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
| Precision of the asserted set at any budget measured | never above 0.3438; per-source allocation does not help | `docs/GATE13-RANKING-CRITERION.md` |
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

- A latent-cell world in the T1/T2 family, reusing the acquisition protocol's
  generator so results are comparable to the record: a **learnable law** over cells,
  of which **112 cross-cell edges** carry the relation, plus law-governed
  self-recurrence.
- **Held-out use is scored on events outside the formation window**, with the same
  endpoint for every learner: log-loss over a fixed denominator
  (`|contexts| × |vocabulary|`), the same labels throughout, the readout calibrated on
  a calibration seed and frozen before the run.
- **Revision is a structural change at a fixed point**, with its own held-out window,
  so that "revision" cannot be scored as "the old structure still happened to be
  right".

**Requirement the world must meet before the study runs:** the target relation must be
learnable **at the arm's own capacity** — demonstrated by Gate F on the calibration
seeds, not assumed from the world's design.

---

## 4. Arms and comparators — same experience, named grants

**Arms.**

| Arm | Capacity | Label in every artifact |
|---|---|---|
| `V1` | 20 (as published) | frozen reference |
| `V1.1-cap` | the variant's declared cap | **variant**, never V1 |
| `oracle-admitted` | as `V1.1-cap` | **ceiling**, never a learning claim |

**Comparators**, each swept over a declared hyperparameter grid, its **best** score
selected on a tuning split, and each reported with **what it is granted** stated beside
its score:

- episodic **replay**;
- **bigram** and **decayed bigram**;
- a **cell-level latent-state counter**, which receives the generator's latent cell map
  and is therefore **not** "data-only" — the utilization campaign recorded that phrase
  as a naming defect, and it is forbidden here.

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

- **Fresh seeds**, disjoint from every seed used in this line: not `20261101–20261130`
  (formation vs. utilization) and not any seed in the divergence pairs.
- **n fixed in advance**, with the number stated when this draft is promoted to a
  preregistration. A later increase in n is a **new study**, not a continuation.
- **No seed may be added because a result was close.** If an interval straddles zero,
  that is the result.

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
