# Organica V2 — Design Notes

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

## 7. The open architectural questions — to be settled by measurement, not opinion

These are the questions the six-colony matrix exists to answer. Until it
runs, they are questions.

1. **How much does the retention policy matter relative to contradiction,
   dreams, questions and curiosity?** For the first time there is a causal
   signal available: the cap binds, and the interventions execute.
2. **Is contradiction developmental fuel or bookkeeping?** No experiment has
   isolated it on a substrate where the organism is not starved.
3. **Does dreaming contribute to trajectory, or only to the upper ladder's
   population?**
4. **Does curiosity require explicit unresolved questions?**
5. **Does EIG remain orthogonal when the candidate pool is not empty?**
6. **Can a Question ever close?** This is blocked on the experiment
   executor, which is an architecture decision, not a measurement.

## 8. What V2 should *not* do

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

## 9. The one-sentence version

> V1 established that the architecture works and that most of the
> apparent limits were the instrument's; V2 should therefore be designed
> around **supply, scope consistency and honest nulls**, and should
> finally answer the retention question on a stimulus where the answer can
> be different from "no difference".
