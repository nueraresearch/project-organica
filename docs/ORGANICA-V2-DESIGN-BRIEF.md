# Organica V2 — Design Brief

> ### Status: PLANNING ONLY. No architecture decision, no build authorisation, nothing built.
>
> This document is a **set of testable options**, not a design. It authorises no
> code, no harness, no engine change, and no V2. Organica 1 remains frozen at
> `v0.9.0` (`docs/V1-FREEZE.md`).
>
> **It supersedes the forward-looking conclusions of
> [`docs/ORGANICA-V2-DESIGN-NOTES.md`](ORGANICA-V2-DESIGN-NOTES.md) for
> planning purposes, and leaves that file's measurement record intact.** The
> notes are dated 2026-10-23/24 and therefore **predate Phase K, Phase L, the
> audit-trace build, and the 2026-10-26 claim-narrowing**. Where the two
> disagree about what comes next, this brief wins; where they agree about what
> was measured, they both stand.
>
> **Every claim below cites a committed artifact or a named measurement.**
> Corrections to earlier prose are recorded in §10 rather than applied quietly.
>
> **Companion document.** [`docs/V2-CAPACITY-DESIGN-BRIEF.md`](V2-CAPACITY-DESIGN-BRIEF.md)
> is a **sub-project of this brief**, not a competing plan. It asks one scoped
> question — how to preserve useful, lower-frequency structure under a bounded
> candidate budget, without task labels — and it exists because §9.7 measured
> a failure that makes that question concrete. It authorises no build either.

---

## 1. What this document is

A brief for the **first V2 question**, written after the negative-results map was
established and after the acquisition endpoint was instrumented. It states the north star
in a form that can fail (§2), names the standing record a V2 must be built against (§4),
and lays out options, gates, comparisons and deferrals that stay testable without
deciding anything (§5–§8). §9.1–§9.5 are dated 2026-10-27 and §9.6–§9.7 are dated
2026-10-28; §10 records where the ingested draft was wrong.

---

## 2. The north star, made testable

The project's ambition is a **blank slate that learns like a human**
(`docs/AUDIT-TRACE-SPEC.md` §1) — a system that develops structure from experience
rather than being handed it.

**"Blank slate" means no pretrained domain knowledge.** It cannot mean *no built-in
assumptions*, because the representation, the learning rules and the input format are
all designed — the organism is specified to produce graph nodes rather than English
summaries (`docs/vision.md`, "Epistemology Over Text"; `docs/manifesto.md`). A claim of
"no assumptions" would be false on the face of the architecture. The defensible claim is
narrower: **nothing about the world is given in advance.**

For V2 planning, the north star is reduced to one question a benchmark can answer:

> **Can experience give the system a reusable model of a world — one that
> supports predictions in unfamiliar situations, persists when the original
> episodes are unavailable, and changes when the world changes?**

Three properties, three separate measurements. Any one of them can be true while the
others are false, and the record of the six negative task families shows exactly that
pattern in the other direction.

---

## 3. What V1 carries forward

**Carry forward as measured fact:**

| Finding | Axis and population | Source |
|---|---|---|
| Development capacity is not fixed; it depends on the novelty structure and presentation schedule | inventory of distinct structures, Tier-1 and burst-assimilation arms: 74 → 91 → 113 → 119 → 128 | `docs/V1-SYNTHESIS.md` §2.3 |
| Trajectories diverge under identical engine and stimulus | six Tier-1 arms, 3,000 cycles each, inventories 44–112 items | `docs/ORGANICA-V2-DESIGN-NOTES.md` §7; `docs/V1-SYNTHESIS.md` §2.5 |
| The developmental machinery is **not** what drives development | five Tier-1 predictions, three REVERSED; Phase K's three matched ablations, all intervals containing zero | `docs/V1-SYNTHESIS.md` §2.6; `docs/phase_k_results.md` §4.1 |
| The internal cognitive ladder is real | 138/138 grounded, concepts → predictions → processes → workflows → beliefs → theories → questions | `docs/V1-SYNTHESIS.md` §2.1; `docs/lineage_audit.json` |
| EIG ranks candidates well | top-k precision 1.000 vs 0.584 random | `docs/ORGANICA-V2-DESIGN-NOTES.md` §1 |

**Carry forward with the claim cut to its evidence:**

- **History matters — as path dependence.** The schedule experiments vary the event
    **multiset and order together**, so they establish that the outcome depends on the
    history. They do **not** establish **strict order dependence**, which needs the
    multiset held fixed and only the sequence changed; **that comparison has not been
    run**. An organism that merely accumulated evidence would also look path-dependent
    here.
  → `docs/V1-SYNTHESIS.md` §2.2; `docs/PHASE-L-SYNTHESIS.md` §8
- **Structure displaces structure — not belief.** Phase L's `DI`/`PI` are
    **structure-retention indices**; the protocol verdict is `H3-L — INCONCLUSIVE` and its
    remedy ("raise n; conclude nothing") was carried out to the end. Belief revision was
    measured separately, in Phase K's K2, and lost (0.4111 vs 0.9846). →
    `docs/PHASE-L-SYNTHESIS.md` §2.3a, §3.1
- **Transfer is unestablished, and the one measured axis was negative.** Cross-domain
    transfer is **−0.486** across **12 domain pairs**, with a mean shared vocabulary of
    **0.17 tags**. Other forms of transfer remain untested.
  → `docs/V1-SYNTHESIS.md` §3

**Carry forward as a candidate mechanism, not an inheritance:** V1's developmental
machinery (contradiction, curiosity, questions, dreams, EIG) is preserved as the
**frozen reference object** and as a **candidate mechanism a V2 may or may not need**.
V1 has not demonstrated an advantage on the external tasks tested; it has also not been
shown to fail in the places that matter.
→ `docs/V1-SYNTHESIS.md` §8

---

## 4. The standing record a V2 must be built against

### 4.1 Six negative task families

All six are negative. The Phase K verdicts are clean losses rather than near-misses:
every 98.33% decision interval lies wholly below zero, and every verdict survives eight
bootstrap seeds and both leave-one-out checks.

| Task family | Organica | Best simple baseline | Difference | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| Incremental world modeling (K1) | 0.5923 | 0.9360 | −0.3437 | [−0.3773, −0.3123] | **REVERSED** |
| Belief revision (K2) | 0.4111 | 0.9846 | −0.5735 | [−0.6162, −0.5309] | **REVERSED** |
| Longitudinal integration (K3) | 0.0000 | 0.8578 | −0.8578 | [−0.8598, −0.8571] | **REVERSED** |

The other three: next-event prediction (Phase H) scored **0.413** against Markov **0.504**
and decayed **0.485**; latent-structure recovery (Phase H) scored **0.704 / 0.547 / 0.109**
against **0.800 / 0.764 / 0.796**; regime-shift detection (Phase I) had **no family meet its
preregistered success rule**; post-shift adaptation (Phase J) had **neither primary gate
pass, in either family**.

Population and axis: Phase K is **10 seeds (20261023–20261032)**, engine frozen, paired
percentile bootstrap with a **98.33%** interval (Bonferroni across the three families),
scored on that family's task metric. The Phase H/I/J numbers are the project's own
summary in `docs/V1-SYNTHESIS.md` §3. → `docs/phase_k_results.md` §4;
`docs/phase_k_results.json`; `docs/V1-SYNTHESIS.md` §3

### 4.2 No phase has authorised a V2

Phase K's pre-committed terminal outcomes name **H1**, **H2** and **H3**. The campaign
landed on **H2 — the search failed**, and H2's own sentence is **"Do not design V2."**
Phase K additionally states that no result in it authorises a V2 design, and that a V2
design is downstream of a positive answer that has not arrived. Phase L's verdict is
`H3-L — INCONCLUSIVE`, and its own summary says no V2 is authorised.
→ `docs/PHASE-K-PREREGISTRATION.md` §7; `docs/PHASE-L-SYNTHESIS.md` §3.1

**So: V2 is not authorised by any completed phase.** This brief is a **plan**, and the
plan's first job is to earn authorisation.

### 4.3 The audit build is nearly, but not fully, closed

**Closed and not reopened:** A1 evidence replay exactness, A2 selection reconstruction,
A3 ancestry honesty, A4 behaviour invariance, A7 event-level attribution. **Still
open:** **A5 field honesty** (every numeric field carries its exact semantics) and **A6
trace / counterfactual separation** (no counterfactual field in the trace).
→ `docs/AUDIT-TRACE-SPEC.md` §7, §13

The probe that is already built reconstructs the selection and evidence axes exactly,
including a binding-cap case: in the default arm the belief pool peaked at **12** against a
cap of **15**, so the cap never bound and no candidate ever lost on rank; in the stress arm
the cap was tightened to **5** and **403** candidates lost on rank, with the reconstruction
staying exact in both arms. → `docs/AUDIT-TRACE-SPEC.md` §10

**Two boundaries on the word "auditable":**

- "Independently auditable" means independently **reconstructed from the engine's state**
    — never independently **replicated by another lab**. No second laboratory has
    reproduced this work.
- The trace reconstructs the organism's **surviving, current** structures and their
    present descent. It does **not** reconstruct the full history of how those structures
    formed.

→ `docs/AUDIT-TRACE-SPEC.md` §8, §13; `docs/USER-MANUAL.md` §8.18

---

## 5. The smallest useful V2 target

**Plan around relational learning, not around a broad intelligence benchmark.** Give a
learner experience generated by a known world rule, then ask five questions. They are
deliberately separable, because the record shows that conflating them hides the cause.

| # | Question | Success means |
|---|---|---|
| **R1** | Can it infer the relation from observed cases? | the relation is present in the learner's state, scored against ground truth |
| **R2** | Can it predict outcomes for held-out cases that recombine familiar elements? | correct predictions on combinations never seen together, against a strong baseline |
| **R3** | Can it use the learned relation after the source episodes are unavailable? | the score holds with the source rows removed and the derived graph retained |
| **R4** | Can it revise its predictions after a clearly specified rule change? | predictions move toward the new rule within the scored window |
| **R5** | Can it provide a trace that separates world evidence from its own generated structure? | the reconstruction distinguishes substrate evidence from organism output |

**Why each has to be scored separately.** Success at forming a structure is not success
at using it; retaining a rule is not transferring it; updating after a change is
neither. A learner that forms R1 and fails R2 has a representation problem; one that
forms R1 and passes R2 but fails R3 has a persistence problem; one that passes R3 but
fails R4 has an updating problem. **The diagnosis depends on keeping the limbs apart**,
and R3's condition must be named honestly: *episode removal with learned graph retained*
is **not** a blank-slate condition (`docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`
§3.3).

**R5 is a boundary, not a goal.** The trace's reach is fixed: it reconstructs surviving
current structure, not the organism's past (§4.3).

---

## 6. What to compare against

Keep V1 in the comparison, and make every baseline answer a specific question.

| Comparator | Question it answers | Notes |
|---|---|---|
| **Replay** — stores episodes verbatim, regenerates nothing | can storing and retrieving episodes account for the performance? | If continuity is reconstruction rather than recall, perfect recall is the **harder** baseline; beating it is the result. `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §8 |
| **Simple relational learner** — a compact rule or graph learner | can a compact learner do the task at all? | Must be swept over a declared grid with its **best** score used. `AGENTS.md` rule 11 |
| **Count-based learners** — bigram, decayed bigram, compact/latent-state rule learner | can transition counting do the task? | Required by §9.5; see the defect recorded there |
| **V2** | does the developmental machinery add value? | |
| **Ceilings and oracles** — knows the law; knows only the grouping | how much room is there at all? | The grouping oracle is mandatory, not optional (§9.4) |

**Two rules that travel with the comparison:**

- **Same world evidence and same test cases for every system.** Every learner receives the
    identical raw experience rows and the identical removal; derived state is deliberately
    *not* equalised, because derived state is the mechanism under test. →
    `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §6.5
- **Report an internal readout *and* an end-to-end score.** A V2 that contains the
    relation but cannot use it is a different diagnosis from one that never formed it, and
    only the pair distinguishes them. §9.3 is the measured precedent for how badly a
    single readout can mislead.

---

## 7. Build gates

Gates, in order. Passing a gate authorises the next step's *planning*, not its build.

1. **Define the construct.** Specify what "reusable knowledge" means for **one small
    world**, in terms a third party can score.
2. **Prove the readout matches the construct.** Ground truth, model output and score must
    describe the same relation. A readout that can manufacture a loss is disqualifying;
    see §9.3.
3. **Freeze the protocol.** Independent worlds, strong baselines, primary metric,
    uncertainty method, failure criteria — committed **before** any cell runs.
4. **Close and freeze A5/A6.** The audit instrumentation is finished only when those two
    close, and then it is tagged and frozen; no feature may be added afterwards, though
    the instrumentation may be **fixed** if it is found wrong.
   → `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §7
5. **Run the corrected V1 acquisition study and use its result to decide what V2 needs to
    change.** A V2 build becomes justified when that process identifies a **specific**
    failure — weak transfer despite correct internal structure, or failure to retain
    useful structure after episode removal.
   → **PARTIALLY EXECUTED (2026-10-28).** The campaign stopped at the preregistered
   acquisition gate: Gate 13 failed on every inspected seed, so transfer was reported
   as *not measurable* and the 600-cell factorial did not run (§9.7). The process did
   identify a **specific failure** — but a **third** kind, not the two named here: the
   organism never formed the structure at all, because one bounded Layer-1 selection
   step discarded it. The gate is therefore **satisfied as a process** and **unsatisfied
   as a test**, and a V2 build is *not* thereby authorised: gates 4 (A5/A6) and the
   study itself remain open.

**Until gate 5 is passed, this brief stays a set of testable options.** Designing V2
against a *named* weakness is right; designing it against a *guessed* mechanism is what
this project has spent its life learning not to do (`docs/V1-SYNTHESIS.md` §8, Path B).

---

## 8. What to defer

Not part of the V2 core: **emotions, agents, consciousness, broad autonomy, or
additional structural layers.**

The first V2 question is whether a learner can acquire and reuse a simple relation with
better results than replay or a lightweight rule learner. If it cannot, adding layers
makes the cause harder to identify — the record already shows that adding developmental
richness produced a richer organism and a **losing** one on six task families
(`docs/V1-SYNTHESIS.md` §6). "More layers" is the move this project has already measured
and rejected.

---

## 9. What 2026-10-27 and 2026-10-28 added

Seven measured findings that the ingested draft predated. Each is stated with its
population, its axis, and its source. §9.1–§9.5 are dated 2026-10-27; §9.6–§9.7
are dated 2026-10-28.

### 9.1 The frozen engine has no representational category for a co-occurrence-defined group

`_classify` (`organica/sleep.py:940`) is a chain of mutually exclusive rules
with these thresholds (`organica/sleep.py:323`): a `concept` needs
`degree >= 4` **and** `clustering <= 0.4` **and** `predictive_reach >= 4`; a
`phrase_fragment` needs `clustering >= 0.7` **and** `predictive_reach <= 2`.

A group defined **by** co-occurrence has **clustering 1.000** — the opposite of what
`concept` requires — and, on the group-structured world, a **predictive reach of 8**,
which excludes it from `phrase_fragment` as well. It therefore falls through to
`unclassified`.

Measured on the purpose-built group-structured world (seed 20261100): **all 12 tags
classified `unclassified`, 0 concepts formed** — each tag at degree 3, clustering 1.000,
reach 8. Sweeping the number of features per cause, the candidate count for
`concept_candidates` is **0** at **4, 5, 6 and 8** features per cause. →
`docs/acquisition_feature_sweep.json`; `organica/sleep.py`

**Why it matters for V2:** the engine's taxonomy has **no category for "tight group"**.
Any V2 that claims relational learning must either add that category or accept that the
substrate cannot represent the thing it is being asked to learn — a constraint on the
representational vocabulary, found before any V2 code exists, which is the cheapest
possible time to find it.

### 9.2 Layer-1 retention crowds out the structure it would need

`_natural_selection` decays and prunes **Layer 1 only** — `_candidate_key`
returns an empty key for every type outside concept, phrase, loop and prediction
(`organica/sleep.py:1804`, `organica/sleep.py:1752`) — and
`MAX_PREDICTIONS = 20` caps the prediction layer (`organica/sleep.py:357`,
applied at `organica/sleep.py:1160`).

Measured on the same world:

| Quantity | Value | Source |
|---|---|---|
| Vocabulary tags in the frozen compressed graph | **10 of 16** (6 absent) | `docs/acquisition_readout_design.json` |
| Group visit shares in the acquisition window | **26.7 % / 30.8 % / 23.9 % / 18.6 %** | `docs/acquisition_coverage_audit.json` (`per_tag_counts`) |
| Distinct temporal edges in the substrate | **192** | `docs/acquisition_coverage_audit.json` (`temporal_edge_total`) |
| Source-group composition of the **top 20** edges by count | **16 / 3 / 1 / 0** — one group supplies 16 of 20 sources, a second 3, a third 1, a fourth 0 | recomputed from `benchmarks/acquisition_world.py` on the same world and seed |

**This is an organism-side capacity finding, not a stimulus artefact.** The four groups
were visited comparably (26.7 / 30.8 / 23.9 / 18.6 %), so the world is not the
explanation; the 20-edge cap is. A group visited at 18.6 % of the experience loses its
edges to groups visited at 30.8 % and 26.7 %.

### 9.3 The readout can manufacture a loss

An ad-hoc readout — **0.9** for a graph neighbour, roughly **0.1/k** otherwise — scored
**far worse than the base rate** on structures that, read with a backoff-smoothed
parameter chosen on a **tuning split**, scored well. Log loss, both scoring shapes,
retention window:

| Readout | House shape (`self_cells` excluded) | Self-cells scored |
|---|---|---|
| Ad-hoc (0.9 / ~0.1-k) — compressed graph, soft | **1.302721** | **1.655377** |
| Base rate | 0.329263 | 0.402159 |
| Backoff-smoothed graph (alpha 2.0, frozen) | **0.277761** — **0.9784** of the achievable span | **0.362233** — **0.9592** of the span |
| Ceiling (knows the law) | 0.224231 | 0.230751 |

→ `docs/acquisition_level_audit.json`; `docs/acquisition_readout_design.json`

**The readout was the limiter, not the organism.** A readout that can turn 0.2778 into
1.3027 without the structures changing is an instrument defect, and a scoring defect is
indistinguishable from a learning failure unless the two are separated. **Consequence
for gate 2:** a readout must be proved against the construct *before* it is used to
diagnose a learner, and the tuning split must be separate from the scoring window.

### 9.4 A grading-only control is not enough — the control set needs a "knows the grouping" oracle

A model that knows only **which group it is in** is a strong control, and it is stronger
than a base-rate predictor. House shape, retention window:

| Control | Log loss | Note |
|---|---|---|
| Ceiling (knows the law) | 0.224231 | upper bound |
| **Copy-context (grouping only, floored)** | **0.252139** | leaves only **0.0279 nats** between itself and the ceiling; it captures 0.0771 of the 0.1050-nat base-rate-to-ceiling headroom |
| Base rate | 0.329263 | |
| Copy-context with hard zeros | 0.552239 | recorded at **0.8679** of the achievable span in the level audit — punished for its own confidence, which is why the floored reading is the fair one |
| Trivial | 2.706801 | |

In the **revision window** the same grouping-only control collapses to **0.548027**
against the new-law ceiling's **0.231028** — grouping alone becomes the wrong answer,
which is exactly what makes the revision limb meaningful.

→ `docs/acquisition_readout_design.json`; `docs/acquisition_level_audit.json`

**Any "reusable knowledge" claim has to beat *that*, not merely the base rate.** A
control set of trivial, base rate and ceiling is not a control set that a benchmark can
fail.

### 9.5 The redesigned world is first-order Markov — and that has a consequence

On the redesigned rule world, a plain **bigram table over the raw rows** reaches within
**0.0275 nats** of the Bayes ceiling on the retention window (0.251693 against a ceiling
of 0.224231; the self-cells shape is 0.298303 against 0.230751). The readout-design
probe measures the same margin as **0.027908** nats over the grouping oracle and
**0.021388** in the self-cells shape.

→ `docs/acquisition_baseline_capability.json`; `docs/acquisition_readout_design.json`

And the recombination probe makes the consequence explicit. On that world's scoring, the
**tag-level Markov** baseline (counts only) **beats** the law-ceiling — headroom over
counting is **−0.018689** (house shape) and **−0.027308** (self cells) — while the
**group-level** abstraction beats the ceiling by only **0.001905** and **0.001119**
nats.
→ `docs/acquisition_recombination_probe.json`

**In that world, "understood the law" and "estimated the transition table" are not
separable by a next-event score alone.**

**Consequence for V2 planning:**

- That world is a **calibration and control task** — ordinary transition learning and
    law-change adaptation. It is **not** evidence of abstraction beyond counts, and it
    must not be reported as such.
- A **compositional generalisation task** is required to test generalisation beyond
    observed transitions: latent factors, training on combinations that reveal each
    factor, testing on withheld combinations, with the factor-to-tag mapping **randomised
    per world** so that no tag identity can be memorised across worlds. Its comparison set
    is the tuned count-based baselines: bigram, decayed bigram, and a compact/latent-state
    rule learner.
- **Do not make a world artificially harder to force a win.** The target is evidence of
    generalisation beyond observed transitions — not proof of an inner state called
    "understanding."

---

### 9.6 The compositional task exists, and it is discriminative

§9.5 called for a compositional generalisation task. It has been **built and
gated**: `benchmarks/acquisition_compositional.py`, checked by
`benchmarks/acquisition_compositional_probe.py` over **30 independent worlds**
(seeds 20261200–20261229).

Four cells in a 2 × 2 grid of two latent factors, 4 tags each (16 total). The law is
that the successor cell differs in exactly one factor (flip-P 0.65 / flip-Q 0.35,
rotating at the regime switch). The tag-to-cell mapping is **randomised per world**.
One held cell per world has its flip-P transitions removed **from the training
stream only**; the held cell's tags remain visible as contexts (155–202 context
events per world), so the withheld thing is a **combination**, not a tag.

| Gate | What it establishes | Measured |
|---|---|---|
| **G1** | the ceiling beats the **strongest** simple baseline, with the **lower** uncertainty bound clearing 0.05 nats | gap **+0.1035**, 99 % interval **[+0.0996, +0.1074]**; binding baseline bigram in **23 / 30** worlds, cell counter in **7** |
| **G2** | a positive control holding the rule reaches the ceiling | exact |
| **G3** | a broken-rule control is clearly worse | at least **+0.1015** worse |
| **G4 / G4b / G4c / G4d** | the withheld combination is genuinely absent from training; the held cell is still observed; every flagged event is excluded; the split is not empty | all pass |
| **G5** | monotone in structure: ceiling < cell counter < base rate | every world |
| **G6** | the held cell varies across worlds, so no tag identity can solve it | 4 distinct held cells |
| **G7** | **the withheld combination is what creates the gap** | held-cell **+0.1963** [+0.1901, +0.2033] vs other cells **+0.0425** [+0.0411, +0.0444] — **4.6x** |

**G7 is the load-bearing one.** Without it, G1 could be passing because of generic
estimation error. With it, the benchmark's headroom is demonstrably
*generalisation* headroom, on the withheld combination specifically.

**A sensitivity, reported and not gated:** a control with the right structure but
the two transition weights swapped is only **+0.0307** worse [+0.0283, +0.0332]. The
endpoint therefore resolves the law's **structure** sharply and its **weights** only
weakly. That bounds what any result on this task may claim.

> **Read the +0.1035 correctly.** It is the **benchmark's headroom**, not an Organica
> margin. The probe runs **no engine** and scores no learner; it answers *"is there
> room for something better than transition counting?"* — yes. It does not answer
> whether Organica occupies that room. §9.7 answers that, and the answer is no.

→ `docs/acquisition_compositional_gate.json`; `benchmarks/acquisition_compositional_probe.py`

### 9.7 V1 cannot reach the state that task would ask about

The compositional task is the **instrument**; the acquisition gate is the
**organism-side** measurement. On the frozen engine it fails.

| Seed class | Asserted structure coverage | Raw temporal coverage |
|---|---|---|
| `20261100` (exploratory) | 0 / 112 = **0.0 %** | 112 / 112 = **100 %** |
| `20261101`–`20261105` (diagnostic) | **0.0 % – 2.7 %** (0–3 of 112) | 112 / 112 = **100 %** |

The world **is** in memory; the organism did not **assert** it. The cause is one
named bound. `_build_predictions` sorts candidates by raw temporal count and
truncates at `MAX_PREDICTIONS = 20`; on this stimulus the two tags of a cell
co-occur in every event of that cell, so **within-cell pairs accumulate higher
counts than the cross-cell transitions that carry the law** and take all 20 slots.
The counterfactual audit confirmed the split — on seed `20261101` the 22 asserted
`prediction_candidate` edges were 22 intra-cell and 0 inter-cell, with **0 / 112**
world overlap.

**The treatment is decisive.** Raising **only** the cap to 1,000, same engine,
same observation stream, same five seeds, every other constant identical:

| Seed | Cap 20 | Cap 1,000 |
|---|---|---|
| `20261101` | 0 / 112 (FAIL) | 110 / 112 = **98.2 %** (PASS) |
| `20261102` | 1 / 112 (FAIL) | 112 / 112 = **100 %** (PASS) |
| `20261103` | 1 / 112 (FAIL) | 112 / 112 = **100 %** (PASS) |
| `20261104` | 0 / 112 (FAIL) | 112 / 112 = **100 %** (PASS) |
| `20261105` | 3 / 112 (FAIL) | 112 / 112 = **100 %** (PASS) |

So the failure is a **capacity limit**, not a missing signal and not a readout
defect. Downstream selection does **not** discard the cross-cell predictions once
they are admitted: they survive natural selection and decay across 110 cycles.

**Organica's readout lost.** On the Pilot 0 seed, with identical raw exposure for
every learner:

| Learner | Retention | Transfer | Revision |
|---|---|---|---|
| **Organica** | **0.453018** | 0.453912 | 0.463372 |
| Replay | 0.347521 | 0.349592 | 0.351989 |
| Statistical | 0.347273 | 0.350723 | 0.352194 |
| Base rate | 0.409581 | 0.409511 | 0.406124 |
| Bayes ceiling | 0.276259 | 0.272365 | 0.275176 |

Organica scored **worse than the baselines did after their episodes were deleted**
(0.453018 against the 0.403045 floor those cells collapse to). That is coherent
with the cause rather than surprising: the asserted structure is mostly
within-cell co-occurrence, so the readout answers *which cell the context is in*
when the task asks *which cell comes next*.

**Transfer was not measured**, and it is **not** a transfer failure. Per §8
requirement 13, a seed that fails acquisition is reported `acquisition_failed`, and
transfer is reported as not measurable.

→ `docs/GATE13-PREFLIGHT-AUDIT.md`; `docs/GATE13-PAIRED-CAPACITY-TEST.md`;
`docs/PILOT-0-INSTRUMENTATION-AUDIT.md`; `docs/ACQUISITION-ENDPOINT-AUDIT.md` §8

**Consequence for V2 planning.** This is a **third** kind of specific failure. The
build gate in §7 names two — weak transfer despite correct internal structure, and
failure to retain useful structure after episode removal — and the failure actually
observed is that **the organism never formed the structure at all**. The capacity
question is now concrete and scoped in
[`docs/V2-CAPACITY-DESIGN-BRIEF.md`](V2-CAPACITY-DESIGN-BRIEF.md): how to preserve
useful, lower-frequency structure under a bounded budget, without task labels or
privileged knowledge of the world's latent factors. Naming a failure is not the same
as authorising a build.

---

## 10. Corrections to the ingested draft

The draft this brief ingests was a conversation transcript. Five statements in it were
wrong or under-stated, and each is corrected here rather than dropped.

| # | What the draft said | Correction | Source of the correction |
|---|---|---|---|
| **1** | "Phase K's three task families were reversed" | Understated the record. There are **six** negative families — Phase H (next-event prediction), Phase I (regime-shift detection), Phase J (post-shift adaptation), plus K1, K2, K3 — and **all three K families are REVERSED**: clean losses, not inconclusive ones. Phase K's pre-committed terminal outcome was **H2, the search failed**, whose own text reads **"Do not design V2."** V2 is therefore authorised by **no** completed phase. | `docs/phase_k_results.md` §4; `docs/PHASE-K-PREREGISTRATION.md` §7; `docs/V1-SYNTHESIS.md` §3 |
| **2** | "The audit work is promising" | Needs its boundary. The audit trace reconstructs the organism's **current, surviving** structures from the engine's state; it is **not an independent replication** and does not reconstruct a structure's full past. **A5 (field honesty) and A6 (trace/counterfactual separation) remain open**; A1–A4 and A7 are closed. "Independently auditable" means independently **reconstructed**, never **replicated**. | `docs/AUDIT-TRACE-SPEC.md` §7, §8, §13; `docs/USER-MANUAL.md` §8.18 |
| **3** | "History-dependent internal structure" | Right, but the claim must be cut to its evidence: the schedule experiments vary the event **multiset and order together**, so they establish **path dependence**, not **strict order dependence**; isolating order requires the multiset held fixed, and that comparison **has not been run**. Phase L's verdict is `H3-L — INCONCLUSIVE`, and its `DI`/`PI` are **structure-retention** indices — so the established finding is **structural displacement**, not belief revision, which was measured separately in K2 and lost (0.4111 vs 0.9846). | `docs/V1-SYNTHESIS.md` §2.2, §5; `docs/PHASE-L-SYNTHESIS.md` §2.3a, §3.1 |
| **4** | The new endpoint files "are reusable benchmark infrastructure", and the probe "mostly validates the world, metric, and theoretical readout" | **Defect, and it has been corrected.** As of 2026-10-27 the endpoint probe could **pass every check it contains** and still leave the benchmark with no room to show an advantage over a strong baseline. The probe's own I2 headroom check compared the ceiling only against a **base-rate** predictor (`headroom` = 0.105032, `I2_headroom` = true); against the **strongest simple baseline** — a first-order bigram over the raw rows — the margin was **0.027462 nats**, and against the grouping oracle **0.027908** nats, both below the probe's own **0.05-nat** bar. **The fix has been made** (§9.6): the compositional task's gap against the strongest simple baseline is **+0.1035 nats** with a 99 % lower bound of **+0.0996**, and G7 shows the gap is generalisation headroom on the withheld combination, not estimation error. | `docs/acquisition_endpoint_audit.json`; `docs/acquisition_baseline_capability.json`; `docs/acquisition_readout_design.json`; `docs/acquisition_compositional_gate.json` |
| **5** | "Those files refer to Revision 3, while the preregistration, README, and manual still describe Revision 2" | True **on 2026-10-27** and corrected in the same work cycle — this is a transient state, not a standing discrepancy. The committed pre-registration now reads **Revision 3**, with **Amendment 3** (2026-10-28) recording that the Task 2 campaign **stopped at the acquisition gate** without measuring transfer. | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` (header, §10); `docs/USER-MANUAL.md` §2 |

**One more correction the draft needed and did not have:** it described the acquisition
endpoint work as reusable benchmark infrastructure. The measurements above show that the
endpoint's *checks* pass while its *headroom* does not survive contact with a strong
baseline (§9.5, correction 4). The infrastructure is reusable; the world as designed is
a **calibration task**, and calling it a generalisation benchmark would overstate it.

**And a sixth correction, made on 2026-10-28, to this brief's own §9.1–§9.2:** those
two findings were measured on **seed 20261100**, which Amendment 2 of the
pre-registration designates an **exploratory pilot seed**. The taxonomy finding of
§9.1 is a structural fact about `_classify` and does not depend on the seed; the
coverage figures of §9.2 are **diagnostic**, not confirmatory, and are labelled as
such.

---

## 11. What would change this plan

Named, specific findings. Each of these forces a V2 decision rather than a further
measurement.

| Finding | Consequence |
|---|---|
| **OBSERVED 2026-10-28.** Gate 13 fails: V1 asserts **0.0 %–2.7 %** of the world's edges while its raw memory holds **100 %** (§9.7) | the defect is in **formation**, before persistence or use — a capacity bound in Layer-1 selection, not a retention or readout defect. V2 work targets candidate selection under a declared budget. **This is the third kind of failure**, not the two below. |
| The acquisition study shows **weak transfer despite correct internal structure** (R1 passes, R2 fails) | the defect is in *use*, not formation — V2 work targets the readout/use path, and the readout is not the limiter (§9.3). **NOT OBSERVED:** R1 did not pass; the structure was never formed (§9.7) |
| The acquisition study shows **failure to retain useful structure after episode removal** (R3 fails) | the defect is in *persistence* — V2 work targets Layer-1 retention and its asymmetry, and `MAX_PREDICTIONS` becomes a named suspect (§9.2). **NOT MEASURABLE:** R3 cannot be scored while R1 fails (§9.7) |
| The engine gains a category for a **tight group** and concepts then form on a group-structured world (§9.1) | the representational constraint is lifted and the relational task becomes runnable on V1's frozen taxonomy |
| **RESOLVED 2026-10-28, in the negative.** The compositional task does **not** let a count-based baseline solve the withheld combinations (§9.6) | the compositional world is not too easy. Gap against the strongest baseline **+0.1035**, lower bound **+0.0996**, and the held cell's gap is **4.6×** the rest. The task stands as the instrument |
| A5 and A6 close and freeze | gate 4 is satisfied and the acquisition study may be run; until then no V2 design may consume the trace |
| The acquisition study's verdict is **"Reconstruction does work"** | V1's developmental machinery becomes a *candidate mechanism* with a positive measurement behind it |
| The acquisition study's verdict is **"the comparator's mechanism wins"** | replay or the rule learner is the mechanism; V2 is either a better replay or not a V2 |
| The acquisition study's verdict is **"Inconclusive"** | the plan repeats: raise n, do not design |

**Rows that are now settled by measurement, and how.** The acquisition campaign
**stopped at the acquisition gate** (§9.7), so there is no verdict of the three
kinds above to report: transfer was not measured, and the baseline comparison that
did run was a **loss** (Organica 0.453018 against Replay 0.347521 and Statistical
0.347273, under identical exposure). The three rows remain in this table because they
are the outcomes a **future** study under a fixed acquisition gate would have to
distinguish — and because the failure actually observed is not one of them, which is
the point of §9.7.

---

## 12. What this brief does not decide

- **It does not authorise a build.** No architecture decision, no harness, no engine
    change. Organica 1 is frozen at `v0.9.0`.
- **It does not decide that V2 exists.** Six task families are negative, no phase has
    authorised a V2, and the acquisition campaign **stopped at the acquisition gate**
    without measuring transfer (§9.7).
- **It does not select a representation.** §9.1 identifies a missing category; it does not
    say which category to add, or that V2 should add it.
- **It does not choose the world's difficulty.** §9.5 fixes the requirement — evidence of
    generalisation beyond observed transitions — and explicitly forbids making a world
    harder to manufacture a win.
- **It does not change the acquisition protocol.** The cell matrix, seeds, decision rule
    and baselines are set in `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`.
- **It does not claim that a developmental architecture can win**, and it does not extend
    the audit instrument (A5 and A6 close it; no feature may be added afterwards), and it
    does not re-read any verdict: Phase K's three REVERSED verdicts, Phase L's `H3-L —
    INCONCLUSIVE`, and the six negative families all stand as recorded.

---

*Prepared for the Project Organica record — Nuera RDL. Planning document; no experiment
described here has been run.*
