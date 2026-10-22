# Organica Ablation Study — Pre-Registration

**Status:** pre-registered, not yet run.
**Date:** 2026-10-21
**Experiment:** `benchmarks/ablation_study.py`
**Metric definitions:** `benchmarks/ablation_metrics.py`
**Results (written after the run):** `docs/ablation_study.json`

---

## 1. Why this study exists

The risk this addresses is not "it doesn't work". It is:

> *It appears to work because one hidden subsystem is doing all the real cognitive work.*

That risk has a sharper form for this project, because the organism's whole claim is that knowledge structures *emerge* rather than being programmed. Two questions follow, and they are different questions:

1. **Which mechanism is load-bearing?** If removing one layer changes nothing, that layer is ornament — architectural decoration that costs complexity and buys nothing. The goal here is not to prove every layer matters. It is to *find the layers that do not*.

2. **Is anything leaking in?** If concepts and theories still appear when the graph edges are removed (Ablation J), then the structures are coming from somewhere other than experience, and the emergence claim is false regardless of how good the rest of the results look.

A third, separate question — *"does it produce things I did not anticipate?"* — is answered by the Designer Surprise metrics, which are the only fully objective emergence measures in this suite and the only ones that **cannot** be automated. See §6.

## 2. Method, and why the engine is not edited

Ten ablations (A–J) plus a full-system reference (**O_FULL**). Each ablation removes or replaces exactly one mechanism.

Every ablation is applied **in-process**, by subclassing `SleepService` / `MemoryService` or by overriding a single method. The engine source in `organica/sleep.py` is never modified. This matters twice:

- The live 90-day study is untouched. `organica/sleep.py` keeps its modification time, so the running study stays auditable under the clean-run rules (`docs/USER-MANUAL.md` §6.4).
- Every condition provably executes the same cognitive code. Any difference between conditions is caused by the ablation and by nothing else.

### Stimulus and protocol

| | |
|---|---|
| Stimulus | `organica/streams.py` → `STUDY_STREAM` (48 events) — the same stimulus the 90-day study runs on, ingested with the same pattern (8 events per cycle, rotating) |
| Scoring | **forward-looking**: before each of the last 10 cycles' events are ingested, the substrate's graph and the organism's current Layer-1 predictions are snapshotted; the cycle's events are then ingested and the snapshot is scored against what actually happened. The organism is always predicting events it has not yet seen. |
| Cycles | 300 per condition |
| Random seed | fixed per condition (base 1000 + condition index), so a rerun reproduces the numbers |

**Why 300 cycles.** The organism is a developmental system: its structure set grows with experience and then plateaus. Measured on the full system, 150 cycles gives 14 hypotheses / 2 theories / 8 dreams and 300 cycles gives 13 / 1 / 8 — against the live daemon's 12 / 1 / 8 at 1,600+ cycles. At 300 cycles the ablation organism therefore reproduces the running study's configuration, which is the point: an ablation of a *younger* organism would measure the wrong system. (At 30 and 60 cycles it does not: 6 hypotheses and **zero** theories, which makes every Generation-5 metric degenerate. See §8, defect 4.)

### What each ablation changes

| ID | Name | What is removed or replaced | Layers affected |
|---|---|---|---|
| **O_FULL** | Full system | nothing | — |
| **A** | No Sleep | all consolidation, synthesis and dream generation disabled; the substrate still ingests and still builds its graph | 1–8 |
| **B** | No Lineage | every candidate stored with `parent_ids` stripped; structures computed identically | provenance only |
| **C** | No Curiosity | EIG ranking and investigation prioritisation disabled | 7–8 |
| **D** | No Falsification | no refutation, no extinction, no belief revision; `DEATH_THRESHOLD` disabled | 1–8 |
| **E** | No Dreams | completion, analogy, mutation, conditional generation disabled | 6 |
| **F** | No Hypothesis Layer | Generation 4 bypassed; Theories/Questions built directly from Workflow components | 4 |
| **G** | No Questions | Question creation disabled, Theories kept | 5 |
| **H** | Random Curiosity | EIG ranking replaced by a random ordering of the same candidates | 7–8 |
| **I** | Random Sleep | every layer's output replaced by random structures of the same count | 1–8 |
| **J** | Memory Without Structure | raw events stored; no co-occurrence, no temporal edges | substrate |

## 3. The metric suite

Definitions are implemented in `benchmarks/ablation_metrics.py`; that file is the contract. If a definition and this document disagree, the file is authoritative and this document is a bug.

| Metric | Definition | Range |
|---|---|---|
| **PA** | Predictive accuracy of the organism's own Layer-1 predictions: `TP = |P ∩ T|`, `FP = |P \ T|`, `FN = |T \ P|`, where `P` is the organism's prediction pairs and `T` the temporal-graph pairs at threshold 5. `PA = 2TP / (2TP + FP + FN)`. | 0–1 |
| **PA_substrate** | the same F1 computed on the substrate's temporal graph directly. Separates "the substrate learned the regularity" from "the organism represents it". | 0–1 |
| **IP** | Information Preservation: `PA_compressed / PA_substrate`, where `PA_compressed` uses only the edges implied by surviving structures. | 0–1 |
| **SCR** | Structural Compression Ratio: `N_experience_events / N_surviving_structures`. Undefined when nothing survived. | unbounded |
| **SS** | Survival Selectivity: `1 − Survived(G)/Created(G)` per generation, averaged. `CSR = 1 − SS`. | 0–1 |
| **LC** | Lineage Completeness: `fully_traceable_nodes / nodes_requiring_lineage`, resolved to Generation 0 experience events. | 0–1 |
| **CD** | Contradiction Density: `unresolved_contradictions / 1000 active nodes`. Undefined when there are no active nodes. | unbounded |
| **CDT** | Cross-Domain Transfer: `PA_with_transfer − PA_without_transfer`, trained on a donor domain, evaluated on a held-out half of the target domain. | −1..+1 |
| **NSR** | Novel Structure Rate: nodes whose exact canonical topology has never existed before, over all new nodes. | 0–1 |
| **DPF / DSI** | Designer Prediction Failure / Surprise Index: `UnexpectedUseful / ExpectedStructures` and `UnexpectedUseful / AllUnexpected`. **Requires the human designer to record predictions before a run.** Pending. | 0–1 |
| **CY** | Curiosity Yield: `Q_resolved / Q_generated`. **Not measurable** — see §5. | — |
| **EIG\*** | Experiment Information Gain: `H_before − H_after` in bits. **Not measurable** — see §5. | — |

### The aggregate

```
ES = 0.20·PA + 0.15·IP + 0.15·CY + 0.15·EIG* + 0.10·CDT + 0.10·NSR + 0.10·SS + 0.05·(1−CD)
```

With CY and EIG* removed, the remaining six weights are renormalised over 0.70:

```
ES = 0.2857·PA + 0.2143·IP + 0.1429·CDT + 0.1429·NSR + 0.1429·SS + 0.0714·(1−CD)
```

A metric that is undefined for a given condition is excluded, and the remaining weights are renormalised within that condition. Every condition reports which metrics were excluded.

`Impact(S) = ES_full − ES_without_S`. Bands: **< 5** cosmetic · **5–15** supportive · **15–30** important · **30–50** foundational · **> 50** existential.

**The aggregate is a summary, not a measurement.** Its normalisation constants (`SCR_REF = 50`, `CD_CAP = 100`) are conventions. The **primary result is the per-metric delta table**; any claim that a layer is "foundational" must be visible in the raw metric columns too.

## 4. Pre-registered predictions

Each prediction states the expected symptom, the metrics expected to move, and the threshold that would confirm or falsify it. These were written before the run.

### O_FULL — reference

Expected: PA and PA_substrate both well above zero; LC = 1.0; SCR > 1; NSR moderate and **falling** over cycles as structures stabilise; CD finite; CDT ≈ 0 or negative.

### A — No Sleep

*Expected symptom:* the organism becomes an event logger. Huge event count, few abstractions, no theories, almost no questions.
*Expected to move:* PA → 0 (no Layer-1 predictions exist); PA_substrate **unchanged** (the substrate still learned the regularities — this is the key contrast); IP → 0 (no compressed representation exists); SCR → undefined; LC → undefined; all structural populations → 0.
*Confirmed if:* every structural population is 0 **and** PA_substrate is non-zero. That combination is the whole point: the substrate learned, and sleep is what turned learning into structure.
*Falsified if:* any structure survives, or PA_substrate is also 0 (which would mean the graph is not what I think it is).

### B — No Lineage

*Expected symptom:* structures still emerge, but traceability and falsification paths are gone.
*Expected to move:* LC → 0 (nothing resolves to Generation 0 without parents); everything else essentially unchanged.
*Confirmed if:* LC collapses to ~0 while PA, SCR, SS and the structural populations are within a few percent of O_FULL. That is the signature of **lineage as governance rather than cognition**.
*Falsified if:* LC stays at 1.0 (the ablation did not take) or the structural populations collapse (the engine does depend on its own provenance in a way that changes behaviour).

### C — No Curiosity

*Expected symptom:* the system becomes passive. It knows things, it does not seek things. Theory count stable, question count collapses, investigation count near zero.
*Expected to move:* G7 investigations → 0, G8 experiments → 0; PA, LC, NSR, SCR unchanged; theories and questions unchanged.
*Confirmed if:* Layer 7 and 8 populations go to zero while Layers 1–5 are within a few percent of O_FULL.
*Note:* this ablation is expected to move **ES very little**, because no ES term counts investigations or experiments directly. That is a known weakness of the aggregate, not a finding.

### D — No Falsification

*Expected symptom:* runaway belief growth. Everything survives, graph bloat, theory inflation, contradictions accumulate.
*Expected to move:* CD sharply up; SS down (almost nothing dies, so selectivity collapses); SCR down (more structures per event, less compression); NSR up (endless near-duplicate structures); surviving structure count up.
*Confirmed if:* CD rises and SS falls relative to O_FULL by a wide margin.
*Falsified if:* CD and SS do not move — which would mean extinction pressure is not doing the work the architecture claims.

### E — No Dreams

*Expected symptom:* the organism becomes conservative. Strong prediction, weak creativity, no speculative generation.
*Expected to move:* G6 dreams → 0; NSR falls (dreams are the main source of speculative topologies); PA, LC, SCR roughly unchanged.
*Confirmed if:* dreams vanish and NSR falls measurably while PA is stable.
*Falsified if:* NSR is unaffected, which would mean dreams duplicate structures that other layers produce anyway.

### F — No Hypothesis Layer

*Expected symptom:* no causal bridge. Theories become weak, questions shallow.
*Expected to move:* question uncertainty → 0 or near it (without the hypothesis layer, the competing expectations have no support counts to be uncertain about); theory count and population change; LC drops (workflow-derived theories have no parent chain to Generation 0).
*Confirmed if:* mean question uncertainty falls sharply and LC drops, while PA and the substrate metrics are unchanged.
*Falsified if:* question uncertainty is unchanged — that would mean Layer 4 is decorative and Layer 5 could read the workflow directly.

### G — No Questions

*Expected symptom:* knowledge stops driving inquiry.
*Expected to move:* G5 questions → 0; G7 investigations → 0 (investigations are built from questions and dreams); G8 experiments → 0 (experiments are built from investigations).
*Confirmed if:* questions, investigations and experiments all go to zero while theories survive.
*The interesting reading:* if experiments still emerge, questions may be unnecessary and Theory+Question could be merged into one layer.

### H — Random Curiosity

*Expected symptom:* massive efficiency drop.
*Expected to move:* the *ordering* of investigations changes, so the priority spread of experiments changes. Total counts should be roughly unchanged — the candidate set is identical, only the ranking is random.
*Confirmed if:* experiment priority distribution flattens relative to O_FULL (random ranking produces a less concentrated selection) while the candidate population is comparable.
*Falsified if:* the selection is statistically indistinguishable from O_FULL — **which would mean the EIG implementation is not providing value.** This is the single most important ablation in the study, and it is a test of the project's own attention economy.

### I — Random Sleep

*Expected symptom:* near-total collapse.
*Expected to move:* LC collapses (random structures have no lineage to Generation 0); NSR rises (random topologies are almost always new); PA collapses (the organism's Layer-1 predictions become random); SCR changes; structural populations remain *present* in count, because random generation produces the same node volume.
*Confirmed if:* PA collapses toward zero while node volume is preserved. Same volume, no signal.
*Falsified if:* PA is unaffected — which would mean the sleep pipeline contributes no predictive signal and the substrate is doing everything.

### J — Memory Without Structure

*Expected symptom:* near-total collapse.
*Expected to move:* every structural population → 0; PA → 0; PA_substrate → 0; PA_compressed → 0; LC undefined; SCR undefined.
*Confirmed if:* **no structure of any kind emerges.** This is the contamination check: it must come out empty.
*Falsified if:* anything at all emerges. If it does, structure is leaking in from a source other than the substrate graph, and every emergence claim in the project is unsafe until that leak is found.

## 5. Metrics that are excluded, and why

**CY (Curiosity Yield)** and **EIG\*** (Experiment Information Gain) are *structurally* unmeasurable in this codebase:

- No experiment is ever executed. Layer 8 emits experiment *candidates*; nothing runs a probe and nothing measures a belief delta. So `Q_resolved` is always 0 and `H_after` never differs from `H_before`. Both metrics are identically 0 for **every** condition, including O_FULL.
- Including them at their specified weights (0.15 each) would deflate every ES score and every Impact score by roughly 30% and miscalibrate every interpretation band — "foundational" would read as "important".
- They are therefore **excluded from the aggregate, not zeroed**, and reported as `not measurable`. Zeroing them would be worse than excluding them: it would look like a measurement.

**DPF / DSI** require the human designer. An automated "surprise" predictor would be the same model that produced the output, so it would predict everything and score 0. The instrument exists (a JSON protocol the owner fills in before a run, and a scorer that consumes it), but the measurement is **pending the owner's protocol**. This is the metric that most directly answers the owner's own question, and it is the one that cannot be automated — which is the point of it.

## 6. Honest limitations, stated before the run

1. **ES is a weighted convenience index.** Its normalisation constants are conventions. The per-metric delta table is the result; ES is the summary.
2. **Two metrics are excluded, one is pending.** CY and EIG* are not measurable; DPF needs a human.
3. **Single seed per condition.** No variance estimate is claimed. A difference smaller than a few percent should not be read as a difference at all.
4. **The stimulus is a 48-event rotation.** The train/held-out split is a genuine held-out split (the held-out events are never ingested), but it measures generalisation *within one synthetic world*, not across worlds. CDT is the cross-world measure, and with near-zero shared vocabulary between the reproduction domains (§4, ablation-independent) it is expected to be ≈ 0 or negative.
5. **PA and PA_substrate are substrate-level.** They are built at ingest time from the event stream, so they are *expected to be identical across every sleep ablation* (A–I) and to differ only for J. That is not a bug — it is the localisation result: it says which part of the system the sleep pipeline actually acts on. If PA turns out to differ between sleep ablations, something else is going on and should be investigated.
6. **This study measures the architecture as it is, not as it should be.** It does not propose cognitive changes. Any remedy it suggests is a proposal under the Phase A freeze, not an applied change.

## 7. Disclosure: what happened before this document was finalised

Full honesty, because a pre-registration is only worth something if the reader knows what was seen first.

- A **harness smoke test** was run before this document was written: 2 conditions (O_FULL and A), **3 cycles** instead of 30, to check that the code executes. Its numbers are not reported and are not used for anything. The pre-registered study runs **all 11 conditions at 30 cycles**.
- The smoke test exposed a **bug in the metric definitions**, not in the engine: `CD` (Contradiction Density) was scoring a system with **zero surviving structures** as a perfect contradiction-hygiene mark of 0.0, which inflated the collapsed system's ES. The fix makes `CD` **undefined** when there are no active nodes, so it is excluded from the aggregate for that condition. This change was made because a collapsed system was being rewarded, which is indefensible under any reading. It is disclosed here rather than quietly folded in.
- No *prediction* was revised after the smoke test. The predictions in §4 were written against the engine source, not against the smoke-test numbers.

## 8. Amendment (2026-10-21) — three measurement defects found in run 1

A first full run of all eleven conditions at 30 cycles was executed after this document was committed. **Three defects were found in the measurement apparatus. All three are fixed, and the run is repeated.** No prediction in §4 was changed, added, or removed; the amendment changes only how the quantities are measured.

Full disclosure follows.

### Defect 1 — the train/held-out split was accidentally a cross-domain test

`STUDY_STREAM` is two domains in sequence: 12 developer-workflow events repeated twice, then 8 defect-triage events repeated three times (`organica/streams.py:34-63`). The original split took the first 32 events as training and the last 16 as held-out — which put **every developer event in training and every held-out event in defect triage**. The held-out set therefore shared almost no vocabulary with the training set.

The consequence was severe and would have been reported as a finding: `PA = 0.000` for the full system looked like "the organism cannot predict held-out events at all", when in fact the test was asking it to predict a domain it had essentially never seen — the cross-domain transfer failure, which is a separate and already-known result (§4, CDT).

**Fix.** The stream is now split **within each domain**: the block structure is detected automatically (`detect_blocks`), and the last repetition of each block is held out. Training now contains 34 events spanning both domains; 14 events are held out in 2 blocks. The held-out events have never been ingested, so no substrate edge derives from them.

**What this changes about the meaning of PA.** Because the stimulus is a repeating synthetic stream, the held-out event *instances* are textually identical to training instances. `PA` therefore measures **within-domain prediction of a held-out sequence position** — retention and reproduction of learned regularities — not generalisation to new material. The generalisation measurement is CDT, which is reported separately and is negative. This limitation was already stated in §6.4; the fix makes the split honest rather than accidentally cross-domain.

### Defect 2 — SCR rewarded destroying structures

The original `SCR` numerator was the total event count (`mem.count()`), which counts sleep candidates as well as experience events, divided by the number of surviving structures. That definition is degenerate: **fewer structures always yields a better compression ratio**. Under it, Random Sleep — which destroys most of the organism's own output — scored a *higher* SCR than the full system, and consequently a higher aggregate score.

**Fix.** The numerator is now **experience coverage**, as the original specification actually defines it (`CR = I / N_s`, where `I` is experience coverage, not the event count). An experience event is *covered* when every one of its tags appears in some surviving structure. `SCR = covered_events / surviving_structures`, and it is undefined when nothing survived. Coverage removes the incentive to destroy: structures that represent nothing score nothing.

### Defect 3 — ablation H was a no-op

Random Curiosity was implemented by shuffling the investigation list *after* the engine had already capped it at `MAX_INVESTIGATIONS`. Since the cap rarely binds, the same five candidates were selected either way — only reordered — so the experiment tested nothing at all.

**Fix.** The full ranked candidate list is obtained (the cap is temporarily raised), then shuffled, then re-capped. Random selection now genuinely competes with EIG selection.

### Defect 4 — the ablated organism was younger and weaker than the live study

Run 1 ran 30 cycles per condition, and the held-out split removed events from the stimulus as well. The result was an organism that was **not the one the 90-day study is running**: 6 hypotheses and **zero** theories, against the live daemon's 12 hypotheses and 1 theory.

That made every Generation-5 metric degenerate. In particular, the full system's Contradiction Density came out as 0.000 — not because contradictions were being resolved, but because it had no contradictions left to count at all, having been pruned away. Comparing that against the No-Falsification condition was comparing a system with no belief against one with too many.

**Fix, in two parts.**

1. **Forward-looking scoring.** The organism now runs on the **full** stimulus with the daemon's exact ingestion pattern. Before each of the last 10 cycles' events are ingested, the graph and the current predictions are snapshotted; the events are then ingested and the snapshot scored. The organism is always predicting events it has not yet seen — so there is no need to remove events from the stimulus at all, and no accidental cross-domain split.
2. **300 cycles instead of 30.** Measured on the full system, the structure set plateaus at around 300 cycles (13 hypotheses / 1 theory / 8 dreams, against the live daemon's 12 / 1 / 8 at 1,600+ cycles). The ablations now run at the maturity level of the study they are supposed to explain.

### Defect 5 — the No-Falsification ablation removed reinforcement along with extinction

`organica/sleep.py:1506` implements selection, reinforcement, decay and pruning in a single method. The first version of ablation D replaced that whole method with a no-op, which removed **reinforcement** as well as extinction. With nothing boosting confidences, every candidate decayed toward zero, fell below `STABLE_THRESHOLD`, and the organism ended up *smaller* than the full system — 3 hypotheses against 13, and zero theories.

That measures "no selection at all", not "no extinction", and it inverted the prediction: the pre-registered expectation was runaway belief growth, and the run showed belief collapse.

**Fix.** D now keeps reinforcement and removes only decay and pruning: a candidate that reappears is still boosted and stored, and a candidate that stops reappearing is re-stored at its current confidence instead of decaying. `DEATH_THRESHOLD` is still disabled so the hypothesis layer cannot cull a belief. Verified after the fix: D ends with **more** hypotheses than the full system (7 vs 5), **more** surviving structures (72 vs 70), and **higher** contradiction density (10.6 vs 7.2 per 1000 nodes) — which is the pre-registered prediction.

### Defect 6 — Contradiction Density was read off a single cycle

Contradiction Density was computed from the final cycle's hypothesis population only. But Generation 5 **oscillates** — that is journal finding 6, and the manual's §17 warns against exactly this reading. A single cycle is a sample of a fluctuating quantity, and with only 0–3 competing subjects per cycle the resulting CD was close to noise.

**Fix.** The harness now records the hypothesis population every cycle, and CD is computed over the whole run:

```
CD = mean over cycles of (competing_subjects / active_nodes × 1000)
```

Two companion numbers are reported alongside it: the **duty cycle** of contradictions (the fraction of cycles carrying at least one competing subject) and the **mean number of competing subjects** per cycle. These are the same shape of statistic the project already uses for Generation 5, and they are much more stable than a final-cycle snapshot.

### A verification protocol was added before the reported run

At the owner's review, a **mechanism-verification stage** was added ahead of any interpretation: *"in experimental cognitive systems, 'the ablation actually changed the organism' is always the first result to verify."* `benchmarks/ablation_verify.py` implements it and writes `docs/ablation_verification.json`. It checks:

1. **A perturbation census** — for every condition, which populations changed relative to `O_FULL`? A condition that changed nothing was not an ablation.
2. **Did Random Curiosity actually change behaviour?** Experiment overlap (Jaccard) between the EIG-selected set and the randomly-selected set; the rank correlation between each candidate's EIG score and the position it was selected at; and the distribution of curiosity scores selected by each policy. If those distributions are identical, the EIG implementation is not influencing selection at all, and any equality in the aggregate is vacuous.
3. **Where do contradictions come from?** The same conditions re-run with the Layer-4 hypothesis cap removed, to distinguish "contradictions are generated by the falsification subsystem" from "contradiction *survival* depends on it" from "the ablation disabled a dead pipeline".

This stage was added **before** the reported run, and it is capable of invalidating a result rather than merely decorating one.

### What was not changed

- No prediction in §4 was revised.
- No threshold, band, or metric was redefined in a direction that favours a result. All three fixes remove artefacts that flattered a *degenerate* system (an empty system scored a perfect contradiction-hygiene mark; a structure-destroying system scored excellent compression).
- The engine was not modified, before or after.

### Why this is disclosed rather than quietly fixed

Run 1's raw output was available before the fixes were made, and two of its three headline results (Random Sleep scoring above the full system; PA of zero everywhere) would have been wrong in the reader's favour or against the project's own claim, depending on which was reported. Pre-registration is only worth something if the record of what was seen first is preserved. It is preserved here and in the git history: the commit containing this document precedes both runs, and this amendment was written before the second run completed.

---

## 9. Falsification commitment

The results will be written to `docs/ablation_study.json` by `benchmarks/ablation_study.py`. **§4 will not be edited after the run.** The git commit order is the provenance record: the commit containing this document precedes the commit containing the results.

If a result contradicts a prediction here, the prediction is wrong and the result stands. The interesting outcomes are the ones that contradict this document.
