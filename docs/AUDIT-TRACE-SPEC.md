# Development Audit Trace — Specification

**Status: SPECIFICATION. Not a build, not a result, not an outcome.**
**Organica 1 remains frozen at `v0.9.0`. Nothing in this document changes the engine.**

**What this document is.** A concrete specification of the trace an investigator
would need in order to reconstruct *why* a structure survived — written against
the engine's **actual** report fields and its **actual** persistence limits, as
read from the source on 2026-10-25. It is the input to a build, not the build.

**Why it exists.** The project's ambition is a blank slate that learns like a
human. The moment it learns something useful, the question becomes *"how do we
know it learned the right thing?"* — and that question cannot be answered by
asking the organism. It has to be answered by inspecting its developmental
history. This specification defines that history in a form an outside reviewer
can check.

**The question this specification answers:**

> **Could an investigator reconstruct the reason — what evidence was used, how
> the claim was formed, what the competing candidates were — without asking the
> system?**

Not "can it explain itself." Not in natural language. A structured, checkable
record.

---

## 0. Scope, and three things this specification refuses to do

| | |
|---|---|
| **In scope** | The trace record: its fields, their exact semantics, how each is obtained, and the acceptance tests for a build that produces it. |
| **Out of scope** | The build itself (next step), the learning experiment that will depend on it (later step), and any change to the frozen engine. |
| **Refuses #1** | **Natural-language explanation.** A renderer may turn the record into prose later; the prose is derived from the record, never the other way round. No language model may supply a reason that is not in the trace. |
| **Refuses #2** | **Counterfactual claims inside the trace.** "Candidate B would have survived without A" is a **replay result**, run separately and labelled as such. A trace records what happened, not what would have. |
| **Refuses #3** | **Instrumenting the engine by default.** Where the record can be assembled from what the engine already exposes and the substrate already persists, it is assembled that way. Instrumentation is the fallback, not the starting point. |

---

## 1. The three levels, and where each one lands

| Level | Question | Verdict against the current engine |
|---|---|---|
| **1. Provenance** | Can every structure be traced to the structures it was built from? | **Available.** `get_ancestry()` exists (`sleep.py:841`) with parent links already stored on every candidate. Bounded by depth 7 and a 4,000-event window (§4.1). |
| **2. Evidence** | Can a belief's support count be resolved to the specific experiences that produced it? | **Available, with one correction.** The counts are temporal transition counts, not observation counts, and "contradiction" is *not* a count of contradicting observations (§3.1, §3.3). |
| **3. Selection** | Can it be established *why this structure survived and that one disappeared*? | **Available under the default retention policy** — and **now demonstrated**, not merely read off the source (§10). The contest set is not exposed by the report, but it is reconstructible from the report's own Layer-2/3 outputs plus the persisted prior candidates (§3.4). This is the valuable level, and it is the one Phase L makes urgent. |

**Level 3 is the point.** Level 1 shows what a structure was made of; Level 2
shows what it rests on; Level 3 shows **the choice**. After Phase L the choice is
the scientifically interesting thing: the organism is not merely accumulating
structure, it is selecting, and the selection has a reproducible transition
region.

---

## 2. Ground truth this specification is written against

Every row was read from the source on 2026-10-25. Nothing here is recalled.

### 2.1 What a cycle's report exposes

| Fact | Where |
|---|---|
| A cycle returns **14** candidate lists: concepts, phrases, loops, predictions, anomalies, meta_concepts, processes, workflow_concepts, hypotheses, theories, questions, dreams, investigations, experiments — plus four dynamics counters (`candidates_strengthened`, `candidates_decayed`, `candidates_pruned`, `composites_created`). | `sleep.py:266-298` |
| `PredictionCandidate`: `source`, `target`, `strength`, `evidence`, `parent_ids`. | `sleep.py:88-98` |
| `HypothesisCandidate`: `subject`, `expectation`, `confidence`, `support_count`, `contradiction_count`, `parent_ids`, and `evidence` = {`support_count`, `contradiction_count`, `raw_contradiction_count`, `total_flow`, `prior_confidence`, `revision_delta`}. | `sleep.py:147-159`, `sleep.py:1505-1512` |
| **The report contains only survivors.** Pre-retention candidates and discarded candidates are never emitted. | `sleep.py:1406-1528` |
| `get_ancestry(candidate_id, max_depth=7)` returns a nested tree of `id`, `type`, `generation`, `confidence`, `parents`; a node absent from the persisted window returns `{"id":…, "found": False}`. | `sleep.py:841-858` |
| The persisted window is the **most recent 4,000 `sleep` events**; `sleep:meta` markers occupy slots in that window and are filtered afterwards. | `sleep.py:876-886`, `memory.py:387-396` |

### 2.2 What the substrate persists

| Fact | Where |
|---|---|
| `events(id, time, source, event_type, content, tags)`; ids are uuid4; `tags` is the comma-joined tokenizer output. | `memory.py:102-112` |
| `cooccurrences(tag_a, tag_b, count)` — order-normalised pairs **within** one event. | `memory.py:306-319` |
| `precedes(tag_from, tag_to, count)` — temporal edges built from the **last 3 events** (`lookback=3`), every prior tag crossed with every new tag. | `memory.py:321-343` |
| `tag_counts`, `sleep_cycles` (the authoritative monotonic counter), `meta`. | `memory.py:142-172` |
| Experience events (`event_type != 'sleep'`) and `sleep:meta` markers are **never pruned**. Sleep *candidate* rows are pruned beyond `DEFAULT_SLEEP_RETENTION = 20000`. | `memory.py:452-490`, `memory.py:31` |
| Candidates are stored as JSON payloads with `event_type='sleep'`, `source='sleep:<type>'`; the cycle marker is stored as `sleep:meta`. | `sleep.py:1916-1967` |
| The tokenizer is `\b[a-zA-Z]{4,}\b` minus a fixed stopword list — **words of three characters or fewer are invisible to the entire substrate** (AGENTS rule 9). | `memory.py:513+` |

### 2.3 How a belief is formed, scored, and kept

| Fact | Where |
|---|---|
| A belief candidate is a **pair**: every ordered pair of a workflow's components, every adjacent pair of a process cycle (wrapping), and every meta-concept with ≥ 5 related candidates. | `sleep.py:1418-1469` |
| `support = precedes[subject][expectation]` — a **temporal transition count**. | `sleep.py:1480-1481` |
| `raw_contradiction = max(0, total_flow − support)`, where `total_flow` is **all** outgoing flow from the subject; `contradiction = raw_contradiction × CONTRADICTION_SCALE (1.0)`. **This is the subject's competing flow — not a count of observations that contradict the claim.** | `sleep.py:1482-1489` |
| `confidence = support / (support + contradiction)`; zero when both are zero. | `sleep.py:1494-1497` |
| **Death rule:** a candidate with `confidence < 0.15` and `support + contradiction ≥ 3` is dropped **before** retention — it never reaches the contest. | `sleep.py:1499-1500` |
| Retention budget: `MAX_HYPOTHESES = 15` beliefs; structural markers (`expectation == "high_structural_significance"`) are held in a **separate** allowance of `MAX_STRUCTURAL_MARKERS = 15` and cannot consume the belief budget. | `sleep.py:336`, `sleep.py:421`, `sleep.py:1520-1527` |
| Salience score = `0.25·tension + 0.25·curiosity + 0.25·novelty + 0.25·revision`, where `tension = raw_contradiction / (support + raw_contradiction)`, `curiosity` is the normalised Shannon entropy of the subject's outgoing flow, `novelty = 1` if the belief was never held before, `revision = |confidence − prior_confidence|`. | `sleep.py:1534-1602` |
| **The default retention policy is `"salience"`**, and its ranking is deterministic: `sorted(by (−score, subject))`, first 15 kept. The tiebreak is lexicographic on the subject. | `sleep.py:392`, `sleep.py:1641-1643` |
| Alternative policies exist (`alphabetical`, `confidence`, `contradiction`, `tension`, `stochastic`). Under `stochastic` the retained set is a **weighted lottery** over salience — not a function of the scores, and not reconstructible without the RNG state. | `sleep.py:397-408`, `sleep.py:1644-1667` |
| A separate stage, `_natural_selection`, reinforces Layer-1 candidates (+0.05) or decays them (×0.8) and prunes those falling under the death threshold. It operates on **Layer 1 only** — `_candidate_key` has no hypothesis branch, so beliefs are never decayed or pruned there. | `sleep.py:1752-1802`, `sleep.py:1804-1817`, `sleep.py:1819-1865` |

---

## 3. The trace record

### 3.1 The proposed record format — with one field corrected

The format proposed in discussion:

```text
Claim: subject → expectation
Current confidence: 0.75
Evidence: 12 supporting observations, 4 contradictory observations
Change: confidence rose from 0.60 after cycle 18
Origin: derived from workflow W and process P
Selection: retained at rank 4 of 15
```

**The third line is wrong as written, and writing it that way would put a false
claim at the centre of the audit record.** "4 contradictory observations" says
the world produced four observations that contradicted `subject → expectation`.
What the engine actually holds is the subject's **total outgoing flow** minus
the flow that supports this expectation — i.e. *four transitions from the same
subject to other expectations*. Those are competing expectations, not
contradictions of this one. `contradiction_count` is a **contention** measure.

The corrected record, with the field names the engine actually uses:

```text
Claim:            subject → expectation
Confidence:       0.75   (= support / (support + competing_flow))
Support:          12 temporal transitions subject→expectation
                  contributing events: [e_0341, e_0344, e_0352, ...]   ← event ids
Competing flow:   4 transitions from subject to other expectations
                  (NOT "4 contradictory observations")
                  competing targets: expectation_b ×3, expectation_c ×1
Prior confidence: 0.60   revision_delta: +0.15   (cycle 18)
Origin:           parents [workflow W, process P]
                  ancestry: workflow W ← meta M ← process P ← events …
Selection:        salience 0.41  (tension 0.20, curiosity 0.35, novelty 1.00, revision 0.15)
                  rank 4 of 31 candidates, cap 15 → RETAINED
                  nearest discarded: candidate at rank 16, salience 0.29
```

Three disciplines are visible in that record and are not optional:

1. **A count is named as what it counts.** "12 temporal transitions", not
   "12 observations". "4 competing transitions", not "4 contradictions".
2. **Every count carries the events behind it.** `support = 12` is a claim;
   `support = 12, and here are the twelve transitions` is auditable.
3. **Every number in the salience line is shown, not just the total.** A single
   composite score hides which component drove the decision.

### 3.2 Level 1 — provenance

**Field.** For each candidate: `id`, `type`, `generation`, `parent_ids`,
`confidence`/`strength`, and the ancestry tree from `get_ancestry()`.

**How it is obtained.** `get_ancestry(candidate_id, max_depth=7)`. The engine
already stores `parent_ids` on every candidate and already persists every
candidate as a JSON payload.

**Limits, stated in the record itself, not in a footnote:**

- **Depth 7.** A chain deeper than 7 is truncated and the truncation is
  recorded as such.
- **Window 4,000 sleep events.** A parent outside the window returns
  `found: False`. The record must say *not found in window*, never *no parent*.
- **Provenance terminates at candidates, not at events.** A hypothesis's parents
  are structures; a structure's parents are structures. **No parent link in the
  engine points at an event.** The structure→event link exists only as counts.
  So Level 1 and Level 2 are different kinds of link, and a record that
  presented them as one continuous chain would be misleading.

### 3.3 Level 2 — evidence

**Field.** For each belief: `support_count`, `contradiction_count`,
`raw_contradiction_count`, `total_flow`, `prior_confidence`, `revision_delta`,
and — the part that makes it auditable — **the list of contributing event
transitions**.

The counts are in the report. Resolving them to the experiences behind them
is **two separate jobs**, and conflating them is what would make the trace
look more auditable than it is.

**Level 2a — aggregate counts.** The engine's own counting rule, read from the
substrate's `precedes` table. The auditor recomputes every belief's support,
competing flow and confidence from it and compares against the report. **No
observer is needed for this**, and the acceptance test is exactness, not
plausibility: the auditor's recomputed count must **equal** the engine's
reported `support_count` for every belief in every cycle. If it does not, the
auditor is wrong, not the engine — and the discrepancy is the finding.

**Level 2b — event-level attribution.** The *individual* transitions behind a
count, each resolved to the event ids that produced it. This is where the
engine's actual rule has to be written down exactly, and it is not what the
first draft of this specification said:

> The lookback window is the **three most recent rows by
> `ORDER BY time DESC LIMIT 3`** — and it **includes the event being stored**,
> because `store()` inserts the row *before* recording edges. So the window is
> the event itself plus two others, and **within-event tag pairs also become
> temporal edges**: a pair of tags in one event produces a transition from
> that event to itself.

Two consequences, both verified by measurement:

- **A post-hoc replay from the final log is not guaranteed to agree.** The
  engine's query has **no `rowid` tiebreak**, so under equal timestamps the
  window is not determined by the schema; and sleep-candidate rows are
  **pruned** from the log (`DEFAULT_SLEEP_RETENTION = 20000`), so a window the
  engine actually saw may no longer be in the log at all. In the probe run
  **no timestamps tied** (48 of 48 distinct), and `time.time()` showed ~0.5 ms
  effective resolution, so ties are possible in principle and did not occur
  there — but they are not excluded by the schema.
- **Therefore event-level attribution requires a store-time observer**: a
  passive subclass of `MemoryService` that calls the parent unchanged and
  re-runs the *same* lookback query immediately afterwards, recording exactly
  the window the engine used. The observer must mirror the engine's own guard
  — edges are recorded only when `event_type != "sleep"` — and the attribution
  must reconcile with the aggregate table exactly, transition by transition.

**Two denominators, and they must not be confused.** A belief's support count
is **cumulative**: it is the number of transitions on that edge so far. So the
same piece of evidence appears in the support of a belief for as long as the
belief survives, and any total summed over beliefs and cycles is a count of
**support references**, not of distinct evidence. The trace must report both:
the **distinct** count (each transition once, deduplicated) and the
**reference** count (each appearance). The disqualifier in §11 reads the
distinct one, because the question it asks is about distinct evidence.

**The record must also carry the attribution split**, because the engine's
counting rule is not scoped to the world: the lookback window is
`SELECT tags FROM events ORDER BY time DESC LIMIT 3` with **no `event_type`
filter** (`memory.py:332-334`), so a transition's source event may be the
organism's **own previous sleep payload**. The `store()` method scopes
co-occurrence and tag-frequency edges to world events (`memory.py:261-263`), and
the temporal graph is not scoped the same way. The trace therefore reports, for
each belief, how many of its supporting transitions were world-sourced and how
many were self-sourced. **This is disclosed, not fixed** — the engine is frozen,
and a self-sourced support edge is a finding about V1, not a bug to patch here.

### 3.4 Level 3 — selection (the contest)

This is the level that answers *"why did this survive and that disappear?"* and
it is the one that is invisible in the report.

**The contest set.** The report shows the retained candidates only. The full
candidate pool for a cycle is the union of:

- every ordered component pair of the cycle's **workflow concepts**,
- every adjacent pair (with wrap) of the cycle's **process candidates**,
- every meta-concept with `related_candidates ≥ 5` (the structural markers),

and each pool member is then subject to the death rule (`confidence < 0.15` and
`support + contradiction ≥ 3`), which removes it **before** the contest.

**Every input to that pool is externally readable:**

- The cycle's current `workflow_concepts`, `processes` and `meta_concepts` are
  **in the report** (`sleep.py:549-554`).
- The prior ones are in the **persisted substrate**: `all_workflows`,
  `all_processes` and `all_metas` add back any stable prior candidate of the
  same type whose id is not already in the current set (`sleep.py:473-509`),
  where `stable_prior` is the persisted candidate set filtered to
  `confidence/strength ≥ 0.3` (`STABLE_THRESHOLD`, `sleep.py:463-465`).

So the pool — **including the candidates that died and the candidates that
lost** — can be rebuilt from the report plus the substrate, without touching
the engine.

**The decision.** For each pool member the auditor computes the four salience
components (§2.3), ranks by `(−salience, subject)`, and compares the resulting
top 15 against the engine's reported retained set.

**The acceptance test:** the auditor's retained set must **equal** the engine's
retained set, cycle by cycle, and the auditor must additionally be able to
report, for every discarded candidate, its rank, its salience, its component
scores, and the margin to the nearest survivor — the counterfactual selection
record, as a *description of this run*, not as a claim about what would have
happened.

**The one condition that breaks this.** Under the `stochastic` policy the
retained set is a weighted lottery over salience (`sleep.py:1649-1667`), so the
survivors are not a function of the scores and cannot be reconstructed from
them. The default is `salience`, so this is a **recorded precondition, not a
live problem**: the trace must record the active policy, and when the policy is
stochastic the reconstruction degrades to a **bound** (the probability that the
candidate would have been drawn) rather than a decision.

**A second, smaller contest** runs in Layer 1: `_natural_selection` reinforces
surviving Layer-1 candidates by +0.05, decays the rest by ×0.8, and prunes
those that fall below the death threshold (`sleep.py:1752-1802`). The report
exposes the **counts** (`candidates_strengthened`, `_decayed`, `_pruned`) but
not the **identities**. The identities are derivable — current keys from the
report, priors from the substrate — and the trace must include them, because a
count without identities cannot answer "which one lost".

### 3.5 What the trace deliberately does not contain

| Not in the trace | Why |
|---|---|
| "Candidate B would have survived without A" | A **counterfactual**. It requires a replay with A removed, which is a different run and a different claim. The trace records what happened; the replay is run separately and labelled as a replay. |
| Any natural-language reason | Prose is a rendering of the record, never a source. A language model may format the record; it may not supply a reason the record does not contain. |
| Any claim that the engine "understood" | The trace records structural operations. Understanding is not observable here and is not asserted. |
| Anything about experiment outcomes | The engine **proposes** experiments (`ExperimentCandidate`: payload, expected outcome, cost, priority) but **nothing executes them** (facts sheet G1: "No experiment executor"). A proposal can be traced; its outcome cannot, because there is none. |

---

## 4. Feasibility verdict per limb

| Limb | Verdict | Grounded in |
|---|---|---|
| **Predict** | **Supported.** Prediction candidates carry `source`, `target`, `strength`, `evidence` and lineage, and a harness can snapshot them before revealing the next events and score them against the stream. | `sleep.py:88-98` |
| **Trace** | **Supported** as a structured record — provenance, evidence, selection — subject to the depth-7 and 4,000-event limits and the evidence semantics correction in §3.1. | §3.2–3.4 |
| **Revise** | **Supported as a structural operation.** `revision_delta`, `prior_confidence`, support/contradiction and generation counters expose *that* a belief moved. This is an operational test of revision, not evidence of rational revision. | `sleep.py:1505-1512`, `sleep.py:1785-1799` |
| **Experiment** | **Not supported.** Proposals exist; execution does not. Active learning stays out of scope until an executor exists, and its absence is a recorded gap, not a solved problem. | facts sheet G1 |

**Two precision notes on the inputs a future protocol will rely on:**

- `strength` on a prediction is an internal score normalised against source
  frequency — **not a calibrated probability**, and it must not be scored as one.
- `support` and `contradiction` are **transitions and competing flow**. A
  protocol that says "12 observations" where the engine says 12 transitions has
  already misdescribed the instrument.

---

## 5. The observer build, and the invariance requirement

**Default: no observer — for Level 3.** Per §3.4, the *selection* contest is
assemblable from what the engine already exposes and the substrate already
persists. The auditor reads through the substrate's own read APIs (`recent`,
`temporal_edges`, `cooccurrences`, `tag_frequencies`) rather than
re-implementing them, so window and ordering semantics are **inherited, not
emulated**.

**Required: an observer — for Level 2b.** Event-level attribution cannot be
reconstructed from the persisted log (§3.3), so a passive store-time observer
is required for it. The observer subclasses `MemoryService`, calls the parent
unchanged, and only *reads*. Its two obligations are that it mirrors the
engine's own edge-recording guard exactly, and that it provably changes
nothing (A4).

**Fallback: a labelled observer build,** used only where a hook inside the
engine is genuinely unavoidable. The project's existing precedent is the
sanctioned one: benchmarks **subclass** `SleepService` / `MemoryService` and
override methods; they never edit `organica/sleep.py` or `organica/memory.py`
(AGENTS.md, "Ablations are applied in-process").

**The invariance requirement, non-negotiable:**

> A build that records a trace must demonstrate that **recording the trace
> leaves the engine's outputs unchanged**. Same seed, observer off and on,
> byte-identical reports. If the observer changes anything, it is not an
> observer and the trace it produces is a different engine's trace.

The demo must be **capable of failing**: the check must be built to fire, and
proved to fire by mutating the condition it guards — the same standard the
project applies to the V1 freeze test, the degeneracy audit and the
seed-exchangeability audit.

**Which hooks, if any, would be needed:** a single override of
`_retain_hypotheses` (to capture the pool, its scores and the kept set) and
`_natural_selection` (to capture the reinforce/decay/prune identities). Under
the default `salience` policy neither is required, because both stages are
externally reconstructible — which is why the observer is the fallback and not
the plan.

---

## 6. Acceptance criteria for the build

The build is accepted only if all six hold, and each is a check that can fail:

| # | Criterion | Test |
|---|---|---|
| **A1** | **Evidence replay exactness** | For every belief in every cycle, the auditor's replayed `support_count` equals the engine's reported value. Any mismatch fails the build. |
| **A2** | **Selection reconstruction exactness** | The auditor's reconstructed retained set equals the engine's reported retained set, cycle by cycle, under the default `salience` policy — including the candidates that died and the ones that lost, with ranks and margins. |
| **A3** | **Ancestry honesty** | Every ancestry node is either resolved within the window, or explicitly marked `found: False` with the window bound stated. A record that reports a parent as absent when it was merely out of window fails. |
| **A4** | **Behaviour invariance** | Observer on vs off, same seed: byte-identical cycle reports. Proven to fail by a deliberate mutation. |
| **A5** | **Field-honesty** | Every numeric field in the record carries its exact semantics (`support` = temporal transitions; `contradiction` = competing flow). A check that the rendered record contains no mislabelled count fails the build. |
| **A6** | **Trace/ counterfactual separation** | The trace contains no counterfactual field; any replay lives in a separate artifact with its own label. A check that greps the trace schema for counterfactual claims fails the build. |
| **A7** | **Event-level attribution** | Every temporal edge resolves to the concrete events that produced it, the attributed total for each edge **equals** its aggregate count, and each belief's support resolves to event ids with a **world/self split**. Requires the store-time observer, and the observer's own guard must mirror the engine's. |

**Status of the criteria at the time of writing (2026-10-26):** **A1, A2, A4
and A7 are met** by the probe (§10) — A7 including a **forced-tie arm** in
which the engine's lookback window is genuinely ambiguous. **A3 (ancestry
completeness), A5 (field-honesty) and A6 (trace/counterfactual separation) are
still pending** and belong to the build.

**Completion metrics the trace should report** (diagnostics, not pass/fail):
evidence-trace completeness (fraction of beliefs whose support resolves to
concrete event ids), lineage completeness (fraction of claims with a fully
resolved ancestry path within depth 7), and selection reproducibility (fraction
of retention decisions explained by the reconstructed ranking alone).

---

## 7. Known limits, and two disclosed defects

| # | Limit or defect | Status |
|---|---|---|
| **L1** | Ancestry depth 7 and the 4,000-event window bound provenance. | Inherent. Recorded per record, not hidden. |
| **L2** | `recent()` orders by `time DESC` with no explicit tiebreak, so the window boundary under equal timestamps is not fully determined by the schema. | Resolved by **reading through the substrate's API** rather than emulating it. |
| **L3** | The trace can describe what the organism proposed, never what an experiment would have shown. | Inherent (no executor). Active learning stays out of scope. |
| **D1** | `contradiction_count` is the subject's competing flow, not contradicting observations. It is easy to misread and the audit record must not. | Corrected in the record format (§3.1) and enforced by A5. |
| **D2** | The temporal graph's lookback window has **no `event_type` filter**, so a supporting transition can originate from the organism's own previous sleep payload, while co-occurrence and tag-frequency edges are world-scoped. | **Disclosed, not fixed** — the engine is frozen. The trace reports the world/self split of support (§3.3). |

**D2 is a finding, not an oversight in this document.** It is exactly the kind
of thing the audit layer exists to surface: a belief that appears to be
supported by the world may partly be supported by the organism's own output.
A future phase can measure how much that matters; it cannot be patched here.

---

## 8. What this specification does not claim

- **It does not claim the engine is explainable.** It claims a specific,
  checkable subset is reconstructible, and §6 states the test for each part.
- **It does not claim a causal explanation.** It claims a structural audit:
  what was counted, what was chosen, against what.
- **It does not claim the organism learns like a human.** It defines the record
  that would let that question be asked without taking the system's word for it.
- **It does not authorise a learning experiment.** The blank-slate acquisition
  test depends on this trace existing; it does not exist yet.
- **It changes no engine behaviour.** Organica 1 is frozen at `v0.9.0`.
## 9. Next steps

1. **Build the auditor** — an external, read-only reconstructor over the
   substrate plus the report, implementing §3.2–3.4. No engine changes.
   *The selection and evidence axes of this are already validated by the
   probe (§10); what remains is the full record — event-level evidence
   lists, ancestry resolution, the selection counterfactuals, and the
   four remaining acceptance criteria.*
2. **Meet §6.** A1 and A2 are the load-bearing ones, and both can fail —
   **both are now met by the probe** (§10). A3, A4, A5 and A6 belong to
   the build.
3. **Run it on a live instrumented world** — a world with known ground truth,
   so the trace can be checked against something external, not only against the
   engine's own numbers.
4. **Then** the blank-slate acquisition experiment: a small world with objects,
   properties and rules, with predict → trace → revise as the limbs, against a
   same-memory statistical learner and a fixed-rule ceiling — designed *after*
   the trace exists, so that "it revised" is a claim with a record behind it.

---

## 10. The probe: the central claim, tested

**What was claimed.** §3.4 asserted that the selection contest is externally
reconstructible — that an outside auditor, reading only the report and the
substrate, can reproduce **which candidates survived, which died, and which
lost**. That claim was read out of the source. A specification whose load-bearing
claim is unverified is a guess with citations, so it was tested.

**How it was tested.** `benchmarks/audit_trace_probe.py` — an **instrument
probe, not an experiment about the organism**. It runs the frozen engine on the
frozen ground-truth world generator, and at every cycle it takes the report and
the substrate state, rebuilds the contest from the documented rules, and
compares. It makes **no claim about what Organica does**; it checks whether an
outside auditor can reproduce what the engine did. No engine file was modified
or instrumented; the observer subclasses `MemoryService`, calls the parent
unchanged, and only reads.

**What the first version of the probe actually verified was narrower than it
claimed, and the spec was corrected to match.** The first pass reconciled the
**aggregate** `precedes` table against the report — which shows the auditor
reproduces Organica's *counts* and its *selection decisions*, and does **not**
show that it can identify the individual experiences behind a count. Event-level
attribution is therefore now its own check (A7), and the earlier result is
named for what it is: **aggregate evidence reconciliation and selection
reconstruction passed.**

| Arm | Belief cap | Cycles | A1 aggregate evidence | A2 selection | A7 event-level attribution | Distinct evidence self-sourced | Died | **Lost on rank** |
|---|---|---|---|---|---|---|---|---|
| Default | 15 (the engine's own) | 120 | **1,412 beliefs, 0 failures** | **120/120 cycles** | **1,412 beliefs, 0 failures; 244 edges reconcile** | **17.9%** | 4 | 0 |
| Stress | 5 (cap binding) | 60 | **290 beliefs, 0 failures** | **60/60 cycles** | **290 beliefs, 0 failures; 241 edges reconcile** | **15.2%** | 3 | **403** |
| Forced tie | 15 | 60 | **692 beliefs, 0 failures** | **60/60 cycles** | **692 beliefs, 0 failures; 241 edges reconcile; 479 tied windows** | **17.5%** | 4 | 0 |

Artifacts: `docs/audit_trace_probe.json`, `docs/audit_trace_probe_stress.json`.

**The default arm alone would have been a weak test, and the table says so.**
Its pool peaked at 12 candidates against a cap of 15, so the cap never bound
and **no candidate ever lost on rank** — the interesting branch went untested.
The stress arm tightens the belief budget to 5 so that the pool exceeds the
cap, and **403 candidates were lost on rank** across the run. The reconstruction stayed exact in both arms.

**What the stress arm does and does not show.** It shows the auditor can
reconstruct a **binding-cap decision** — that the ranking, not just the pool,
is reproduced. It does **not** show that the cap commonly determines outcomes
under default conditions: in the default arm it never bound at all. The
honest statement is *the auditor handles the case in which the cap decides*,
not *the cap decides often*.

**The checks can fail.** `tests/test_audit_trace_probe.py` breaks the auditor
on purpose — zeroing the curiosity term, dropping a tag from the temporal graph,
and lifting the observer's own sleep-event guard — and requires A1, A2 and A7
to go red. They do. A check that cannot fail is decoration, and this one is not.

**The probe found two defects in itself, which is the point of having checks
that can fail.** Its first observer attributed transitions for sleep events as
well as world events — the engine deliberately skips those — so the attributed
totals ran an order of magnitude above the aggregate counts and A7 caught it.
And its first invariance check compared whole reports including `ran_at`, a
wall-clock timestamp, so two identical runs differed for a reason that had
nothing to do with behaviour. Both were the auditor's errors, both were found
by the checks rather than by inspection, and both are recorded here rather than
quietly fixed.

**D2 is now a measured quantity — and the denominator had to be fixed
first.** The first version of this figure pooled the support of every reported
belief across every cycle in which that belief was reported. Because a belief's
support count is **cumulative**, a transition that occurred early is counted
again in every later cycle where the belief survives, so that pooled number
counts **support references**, not distinct evidence. It is a valid weighted
view; it is not the share of unique transitions.

**The probe now reports three numbers, and they answer different questions:**

| View | Default arm | What it is |
|---|---|---|
| **Distinct evidence behind reported beliefs** | **802 of 4,481 = 17.9%** self-sourced | each transition counted once, restricted to the edges that actually back a reported belief. **This is the disqualifier's figure.** |
| Pooled support references | 53,980 of 307,857 = 17.5% | the same support counted once per belief per cycle it appears in. A weighted view, not a share of unique transitions. |
| All distinct transitions recorded | 5,436 of 12,583 = 43.2% | every transition the observer saw, **including edges that no reported belief ever rested on**. Context, not the disqualifier's figure. |

**Correcting the denominator moved the headline only slightly** — 17.5% to 17.9% — and that agreement is worth
stating plainly. **But the correction did surface a separate and much larger
number**: across all 12,583 distinct transitions the observer recorded, **43.2% are
self-sourced** — transitions on edges that no reported belief ever rested on.
Those are the organism's own tag-to-tag edges: the substrate of its
self-generated output, carrying twice the self-sourcing of the evidence
actually behind its claims. The two numbers describe different surfaces, and
the trace must report both rather than let one stand in for the other.

**The forced-tie arm.** The engine's lookback query has no tie-breaker, so the
schema does not determine which rows a tied window selects. The forced-tie arm
patches the clock so that every four consecutive stores share a timestamp,
producing **479 stores with a genuinely tied window**, and requires the
observer to reproduce the engine's choice anyway. **It does:** A7 stays exact
(2,589 distinct transitions, 241 aggregate edges reconciling, 0 mismatches). The honest
statement is that the *implementation* is deterministic for identical queries
over identical data — so the observer's re-run selects the same rows — while
the *schema* still does not guarantee it, and a replayer that did not observe
at store time could not rely on it.

### What the probe establishes, and what it does not

**Establishes:** the rules transcribed into §3.3 and §3.4 are a *faithful*
transcription. An outside auditor, given the report and the substrate, can
reproduce the engine's evidence counts and its selection decisions exactly —
including the candidates that died under the confidence rule and the hundreds
that lost on rank. **The selection contest does not require a hook inside the
engine.**

**Does not establish:**

- **Generality.** One world family (the frozen cause generator), one
  configuration, one policy. The probe validates the *transcription*; it does
  not validate the auditor on worlds it has not seen, and it says so.
- **Behaviour under timestamp ties — now tested, with a limit.** The
  forced-tie arm produces genuinely tied windows and the observer reproduces
  the engine's choice every time, because the implementation is deterministic
  for identical queries over identical data. The **schema** still does not
  determine the window under a tie, so a replayer that did not observe at
  store time could not rely on it. The observer is the reason, not a proof
  about the engine.
- **The `stochastic` policy.** Under a weighted lottery the retained set is not
  a function of the scores; the reconstruction degrades to a bound (§3.4).
- **The whole trace.** The probe checks the *selection* and *evidence* axes.
  The ancestry completeness metric (A3), the behaviour-invariance proof (A4),
  the field-honesty check (A5) and the trace/counterfactual separation (A6)
  belong to the build, and the build has not happened.
- **Anything about learning.** No claim is made or implied that the organism
  learns, transfers, or generalises. This is an audit of a mechanism.

---

## 11. Keeping the trace honest

**The risk this section exists to name.** A layer that makes developmental
decisions reconstructible is attractive, and attractive things become projects.
The trace could become the new displacement curve: infrastructure that is
built, extended and admired without ever adjudicating a question the project
wanted answered. Then it would be a *second* inventory — *"how many events
resolve?"* — and the project would have swapped one measurement habit for
another.

**The rule.** The trace must be **load-bearing for a question that was
pre-committed before the trace existed.** Concretely: the next protocol's
success criteria must contain at least one **trace-derived diagnostic**, and a
result that fails that diagnostic **fails the protocol even if the headline
behaviour is correct**.

### What that means for the next phase

The blank-slate acquisition test asks whether experience can produce knowledge
that transfers, predicts and revises. The standing criticism of any such
success is: *"it predicted correctly — but what did it actually learn?"* The
trace is the answer to that criticism, and the pre-commitment is what stops it
from being decoration:

- A claimed **transfer** must be supported by **world-derived** evidence. The
  trace reports the world/self split of every belief's support (§3.3, D2), and
  if the support carrying the claim is **self-sourced** — the organism's own
  previous sleep payload — the claim does not count as transfer.
- A claimed **revision** must be visible in the trace as a change in a claim
  whose support is world-derived, with the prior state resolved
  (`revision_delta`, `prior_confidence`).
- A claimed **explanation** must resolve to event ids (§3.3) — not to counts,
  and never to the system's own account of itself.

**The disqualifier, stated plainly:**

> **A predicted-correct result whose supporting evidence is self-sourced is not
> a transfer result.**

**Calibrated, not binary.** The disqualifier is not a mood: the trace reports
a *share*, and the probe measured what that share looks like on a world where
the organism is doing ordinary work — **17.9% of the distinct evidence behind reported beliefs
was self-sourced** (§10). So the criterion is about the support *carrying the
claim*, not about the trace's average: a claim resting on the self-sourced
minority fails, and a claim resting on world-derived support stands. The
measurement gives the criterion a baseline instead of a vibe.

That is the first concrete use of D2, and it is what turns a disclosed defect
into a live scientific instrument. A defect that can defeat a claim is worth
more than a defect that is merely recorded.

**A second guard: the trace's own metrics must not become the target.**
Evidence-trace completeness, lineage completeness and selection reproducibility
are **diagnostics of the instrument**, not measurements of the organism. They
are reported; they are never criteria.

### The roadmap this sits in

| Stage | What it established |
|---|---|
| **V1** | Developmental properties: development occurs, history matters, curriculum matters, stable regimes emerge. |
| **Phase L** | Regime behaviour with a stable transition region — and the protocol verdict and the characterisation kept as separate artefacts. |
| **Development audit trace** | The developmental *decision* becomes reconstructible by an outside investigator. Demonstrated, not asserted (§10). |
| **Next** | Can experience produce knowledge that **transfers, predicts and revises** — judged with trace-derived diagnostics pre-committed in advance. |

A coherent progression: *what structures exist* → *what develops and survives*
→ *why it survived* → *whether what it developed is usable in a new situation*.

---

*Specification written against the frozen `v0.9.0` engine, source read
2026-10-25. The load-bearing claim was subsequently tested by
`benchmarks/audit_trace_probe.py` (§10). Companion documents:
`docs/phase_l_results.md` (the measurement record),
`docs/PHASE-L-SYNTHESIS.md` (the characterisation),
`docs/USER-MANUAL.md` (§8.13, finding 18).*
