# Organica V2 — Design Notes

> **Which "V2"?** This file is about the **architecture generation**
> *Organica 2* — the planned successor to the frozen eight-layer engine that
> runs today (*Organica 1*). It is **not** the package version (0.6.0, SemVer
> 2) and **not** the second research campaign (*Ablation Study 2*, whose
> pre-registration is `docs/FORCE-MATRIX-PREREGISTRATION.md`). The three
> namespaces are tabulated in `CHANGELOG.md` and `docs/USER-MANUAL.md` §11.6.

**Status: PLANNING ONLY. Nothing here is built, and nothing here is a
decision.** This file records what the measurements of V1 and V1.5 have
established, so that V2 can be designed from evidence rather than from
intuition.

The rule this file exists to protect: if Organica is ever abandoned, the
answer to *"why did V1 fail?"* must be **"we measured X"**, not *"we think
X"*.

Everything below cites a committed artifact. Nothing here is a claim
without one.

---

## 1. What survived scrutiny

These held up under audit, ablation, and a substrate change.

| Finding | Evidence |
|---|---|
| **Sleep is foundational.** Remove it and every developmental structure goes to zero. | V1 condition A; unchanged on the fixed substrate (`docs/v1_impact.json`) |
| **A structured substrate is foundational.** Memory Without Structure produces nothing. | V1 condition J; unchanged on the fixed substrate |
| **Lineage is governance, not cognition.** Removing it leaves the populations *identical* and moves only the lineage metric. | V1 condition B — the control; still byte-identical post-fix |
| **The layer orderings are structural.** Dreams carry the upper ladder; questions are not the gateway; curiosity alone produces investigations and experiments. | V1 conditions C, E, G; unchanged post-fix |
| **EIG is an excellent ranker.** Top-k precision 1.000 against 0.584 random, and a genuinely different selection from random curiosity (Jaccard 0.111). | `docs/ablation_verification.json` |
| **The layer model is real.** Concepts → predictions → processes → workflows → beliefs → theories → questions is a dependency chain, not a list. | `docs/lineage_audit.json` (138/138 grounded) |
| **The 8-layer engine is efficient enough to run for months.** ~250 ms/cycle, bounded substrate, append-only log, monotonic counter. | 4,400+ cycles, 0 failures (`benchmarks/study_health.py`) |
| **The G1–G4 perturbation ladder works.** It caught the workflow-measurement defect, the archive defect, and the runner bug that made FULL and SALIENCE identical. | This file, §6 |

## 2. What failed scrutiny

Hypotheses that measurement killed.

| Hypothesis | Killed by |
|---|---|
| *"More vocabulary creates more cognition."* | 42 world tags → 1 theory; 97 tags → **0** theories. More diversity *reduced* theory production (`docs/instrumentation_audit.json` → stimulus sweep) |
| *"EIG buys developmental performance."* | EIG is a perfect ranker and removes nothing measurable. V1 condition H; `docs/ablation_verification.json` |
| *"The retention policy is the bottleneck, so fix the policy."* | The cap bound in **0 of 600** cycles. The policy could not matter because nothing was truncated (journal §19) |
| *"The contradiction series shows a flat population because the metric is wrong."* | No — it shows a *flat population with growing evidence*, which is a different and more interesting fact (facts sheet B4) |
| *"The r=4 / r=6 collapse is a developmental boundary."* | A measurement artifact. All three repeat counts behave identically once the frequency scope is corrected (journal §21.6) |
| *"No Falsification freezes the organism."* | **Reversed.** Post-fix it is the best-supplied condition in the study: 18 beliefs, MBSD 1.000 (journal §22) |
| *"The proposed MBSD gate is a predictive developmental quantity."* | It is **structural** — the theory count *is* the competing-subject count, by construction (journal §20) |

## 3. What turned out inert

Parameters and mechanisms that look load-bearing and are not.

| Thing | Status |
|---|---|
| `MAX_HYPOTHESES` | **INERT on the study stream** — the pool reaches 6 against a cap of 15. **Binds on the branch stimulus** (pool 18), where the policy finally matters |
| `MAX_WORKFLOWS`, `MAX_META_CONCEPTS`, `WORKFLOW_MIN_MATCHED_METAS`, `META_CONCEPT_MIN_REFS`, `CONCEPT_MIN_DEGREE`, `CONCEPT_MIN_REACH`, `PHRASE_MIN_CLUSTERING` | **INERT** — changing them at any level changes nothing |
| Alphabetical retention | A real defect (decided by sorting strings) that was **inert** until the cap began to bind. On the branch stimulus it changes the theory count 5 → 4 |
| The 90-day single arm | **A flat line.** Plateaued at cycle 261; stdev 0.000000 over the last 931 cycles |
| `cy` (questions resolved) and `eig_star` | **Structurally unmeasurable** — no experiment executor exists, so both are identically zero by construction |

## 4. What turned out essential

| Thing | Why it is essential |
|---|---|
| **Competing expectations per subject** | Layer 5 forms exactly one theory per subject holding ≥ 2 beliefs. It is the *only* source of a theory, and it is what the whole gate is built on (journal §20, §21.7) |
| **The triangle (3-cycle)** | A workflow's components are the tags of a 3-cycle, and a 3-cycle is the only structure that gives a subject more than one expectation. It is the unit of design (journal §21.7) |
| **Reciprocal structure** | A 2-cycle or 3-cycle is the only thing the process builder accepts. Without it: 0 processes, 0 workflows, 0 beliefs |
| **Scope consistency between a counter and the graph it normalises** | The single most consequential finding of the project. A counter scoped to *all* events, normalising a *world-only* graph, silently discarded the world's own structure (journal §21.5) |
| **The measurement framework** | The G1–G4 ladder, the influence map, the cap census, the gate re-runs. Every defect in this project was found by an instrument, not by reading code |

## 5. What became bottlenecks

| Bottleneck | Layer | Evidence |
|---|---|---|
| **Belief supply, not selection** | Layer 4 | On the study stream: 5–8 beliefs for 15 slots, pressure 0.35. On a branch stimulus: 18 beliefs, pressure 1.20, cap binding |
| **Layer-1 truncation** | Layer 1 | 936 loops / 621 predictions / 309 anomalies generated, 15 / 20 / 10 kept — pressure 61×, 30×, 29× |
| **The experiment executor** | Layer 8 | Nothing ever executes an experiment, so no question ever closes and EIG can never pay off. This is why `cy` and `eig_star` are unmeasurable |
| **The world vocabulary** | Layer 1 | 42 tags → 1 theory. The organism needs *structure*, not words |

## 6. The defects this project found in itself

Every one of these was found by an instrument, and every one changed the
plan.

| Defect | Found by | Cost if missed |
|---|---|---|
| The archived contradiction series read `null` instead of 0 | cross-checking the archive against the log | A headline number would have been wrong |
| The first audit read `workflows` instead of `workflow_concepts` | the perturbation ladder | A working layer was reported dead |
| The tag counter was scoped to all events while the graph was world-only | the branch-stimulus collapse, traced layer by layer | The organism's own schema out-competed the world's structure; a whole experiment was mis-specified |
| The apparent r=4/r=6 phase transition | the frequency-scope probe | A parameter would have been shipped on the strength of a coincidence |
| The matrix runner instantiated the instrument instead of the colony subclass | the G1 code-path check | **FULL and SALIENCE would have been identical**, and the campaign would have measured nothing |
| The first G-SUS implementation used a subject count as a proxy for the theory cap | reading the gate table | A design was wrongly failed |

## 7. The open architectural questions — and what the Tier-1 matrix answered

The matrix ran on 2026-10-23: six colonies, 3,000 cycles each, 18,000
colony-cycles. Full results in
[`FORCE-MATRIX-RESULTS.md`](FORCE-MATRIX-RESULTS.md). These were the
questions the matrix existed to answer.

1. **How much does the retention policy matter relative to contradiction,
   dreams, questions and curiosity?** **Answered, and smaller than the metric
   spread suggested.** All six arms reach the *same* structural fixed point
   on cycle 1 — 18 pre-retention beliefs, 7 competing subjects, 15 retained
   beliefs — and hold it for 2,999 cycles. The retention policy changes
   *which* beliefs persist and how many items are discovered before
   saturation (44 to 112 across the arms); it does not change the
   attractor.
   *(Corrected 2026-10-24, journal §31: the retained belief count is exactly
   15 in every cycle, but the pre-retention pool is modal rather than
   constant — 98.1–99.5% of cycles for five arms, 75.9% for `NO_QUESTIONS`.
   The attractor conclusion is unaffected.)*
2. **Is contradiction developmental fuel or bookkeeping?** **Answered: not
   fuel, on this substrate.** With contradiction's weight in the confidence
   formula removed, development velocity goes *up* (2.467 → 2.633) and
   contradiction survival falls (0.9375 → 0.750). The removal helps.
   *(Caveat: the colony zeroes contradiction's influence, not contradiction
   itself — see the results document §6.)*
3. **Does dreaming contribute to trajectory, or only to the upper ladder's
   population?** **Answered: it contributes to both, and more than the
   population column suggests.** Removing dreams drops the development rate
   to the lowest in the campaign (1.467 against 2.467) and removes 30 items
   from the whole inventory, not just the 11 dreams.
4. **Does curiosity require explicit unresolved questions?** **Answered: no,
   on this substrate.** Removing question creation *raises* development
   velocity (2.467 → 3.733) and leaves the fixed point unchanged. It costs
   the question layer and nothing else.
5. **Does EIG remain orthogonal when the candidate pool is not empty?** **No.**
   Selecting the lowest-EIG experiment develops *more* per 100 cycles
   (2.833) than selecting the highest-EIG one (2.467). EIG selection is not
   orthogonal on this substrate; it is counterproductive.
6. **Can a Question ever close?** **Still blocked** on the experiment
   executor, which is an architecture decision, not a measurement.

**And one question the matrix raised that it could not answer:** is
stabilisation the desired outcome, or evidence of a bottleneck? See §10.

## 8. What the matrix changed about the plan

**The stimulus, not the architecture, is the binding constraint on the next
experiment.**

The Tier-1 stimulus (`lattice_L1`) contains **9 distinct events** and the
organism's experience **repeats every 9 cycles**. Every colony discovered
**zero new items in its final 100 cycles**, and the full inventory is 44 to
112 items. A repertoire cannot grow in a world that does not change, so the
campaign cannot distinguish *"the organism found everything the world
contains and held it"* from *"the organism cannot restructure once it has
stabilised"*. On this stimulus both hypotheses predict identical numbers.

A second, quieter problem: **M5 ("development velocity") is not a rate.**
It is `new items per 100 cycles` over the whole run, so it divides a finite
inventory by the run length. The FULL arm recorded 74 new items over 300
cycles and the same 74 over 3,000; the "velocity" fell from 24.667 to 2.467
because the numerator stopped growing. The metric was measuring the
exhaustion of a repertoire and calling it development.

**The next experiment therefore needs a world that does not repeat, and a
development metric defined over a fixed prefix window.** That is a change to
the experimental design, not to the engine, and it follows the rule the
project has kept throughout: learn what V1 can teach before changing what
V1 is.

## 9. What V2 should *not* do

* **Not replace the architecture.** V1 has not been shown to fail. It has
  been shown to be *unmeasured* in the places that mattered.
* **Not add layers.** Every attempt to get more cognition by adding
  structure has produced less. The organism's limits have consistently
  been in supply and in measurement, never in expressiveness.
* **Not redefine a metric after seeing it.** The sensitivity audit
  (`docs/metric_sensitivity.json`) is recorded *before* the campaign, and
  the metrics that turn out to be decorative are reported as decorative.
* **Not relax a gate to make a campaign runnable.** The gates were closed
  by measurement; the campaign runs because they closed, not because they
  were adjusted.
* **Not treat a null as a failure.** Zero cognitive revolutions across all
  six arms, a zero retention pressure on the study stream, a zero
  `cy` — these are results with causes, and they are reported with the
  cause attached.

## 10. The one-sentence version

> V1 established that the architecture works and that most of the
> apparent limits were the instrument's; the Tier-1 matrix established that
> the **next** limit is the **stimulus's** — a closed, repeating world in
> which every arm converges on cycle 1 and then only accumulates evidence —
> so V2's first requirement is a world that does not repeat, and its second
> is a development metric that measures discovery rather than the
> exhaustion of a repertoire.
