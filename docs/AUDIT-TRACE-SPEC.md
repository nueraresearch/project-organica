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
  re-runs the lookback immediately afterwards, recording the window the engine
  used. The observer must mirror the engine's own guard — edges are recorded
  only when `event_type != "sleep"` — and the attribution must reconcile with
  the aggregate table exactly, transition by transition.

**A precision about the observer's query, because "the same query" is slightly
too strong.** The engine runs `SELECT tags FROM events ORDER BY time DESC
LIMIT 3`; the observer runs `SELECT id, time, event_type, tags, rowid FROM
events ORDER BY time DESC LIMIT 3` — the **same ordering clause and limit**,
with a **wider projection** so that the contributing rows can be identified.
The two are not byte-identical SQL, and SQLite does not promise a stable order
among rows that tie on `time`. The correct statement is therefore:

> **The observer's window matched the engine's in every tested case, as an
> empirical match on the tested SQLite implementation** — and the evidence for
> that match is **A7's exactness**: if the observer's window had differed from
> the engine's on any store, the attributed totals would not have matched the
> aggregate counts, and A7 would have failed. The forced-tie arm pushes on this
> deliberately (479 stores with a genuinely tied window, 0 mismatches).

That is a demonstration, not a guarantee, and it is stated that way here.

**Two denominators, and they must not be confused.** A belief's support count
is **cumulative**: it is the number of transitions on that edge so far. So the
same piece of evidence appears in the support of a belief for as long as the
belief survives, and any total summed over beliefs and cycles is a count of
**support references**, not of distinct evidence. The trace must report both:
the **distinct** count (each transition once, deduplicated) and the
**reference** count (each appearance). The disqualifier in §11 reads the
distinct one, because the question it asks is about distinct evidence.

**What the run-level share is, and is not.** The figure below is a share of
the **union of the unique evidence transitions behind beliefs reported during
the run** — deduplicated, and restricted to the edges those beliefs rested on.
It is **not** a per-claim share (a particular claim's own support can be far
more or far less self-sourced), and it is **not** evidence that self-sourced
support caused an incorrect prediction. It is a population-level measurement of
how much of the organism's belief evidence is its own output. The disqualifier
in §11 is therefore written as a **per-claim rule**, and the run-level figure
is the baseline that rule is read against.

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

The build is accepted only if all **seven** hold, and each is a check that can fail:

| # | Criterion | Test |
|---|---|---|
| **A1** | **Evidence replay exactness** | For every belief in every cycle, the auditor's replayed `support_count` equals the engine's reported value. Any mismatch fails the build. |
| **A2** | **Selection reconstruction exactness** | The auditor's reconstructed retained set equals the engine's reported retained set, cycle by cycle, under the default `salience` policy — including the candidates that died and the ones that lost, with ranks and margins. |
| **A3** | **Ancestry honesty** | Every ancestry node is either resolved within the window, or explicitly marked `found: False` with the window bound stated. A record that reports a parent as absent when it was merely out of window fails. |
| **A4** | **Behaviour invariance** | Observer on vs off, same seed: byte-identical cycle reports. Proven to fail by a deliberate mutation. |
| **A5** | **Field-honesty** | Every numeric field in the record carries its exact semantics (`support` = temporal transitions; `contradiction` = competing flow). A check that the rendered record contains no mislabelled count fails the build. |
| **A6** | **Trace/ counterfactual separation** | The trace contains no counterfactual field; any replay lives in a separate artifact with its own label. A check that greps the trace schema for counterfactual claims fails the build. |
| **A7** | **Event-level attribution** | Every temporal edge resolves to the concrete events that produced it, the attributed total for each edge **equals** its aggregate count, and each belief's support resolves to event ids with a **world/self split**. Requires the store-time observer, and the observer's own guard must mirror the engine's. |

**Status of the criteria (updated 2026-10-27):** **All seven criteria (A1, A2, A3, A4, A5, A6, A7) are MET** by the probe (`benchmarks/audit_trace_probe.py`) and verified by acceptance tests (`tests/test_audit_trace_probe.py`, `tests/test_audit_ancestry.py`):
- **A1, A2, A7**: Reconciled across default, stress, and forced-tie arms.
- **A3**: Lineage reachability and honesty verified with depth/window sweeps.
- **A4**: Behaviour invariance verified with byte-identical output check.
- **A5**: Field honesty enforced; records verified to contain zero mislabelled count fields, and proved to fail if competing flow is mislabelled as contradictory observations.
- **A6**: Counterfactual separation enforced; trace records and schema verified to contain zero counterfactual claims, and proved to fail on counterfactual injection.

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

### D3 — the engine's charter claims a link the engine does not have

**`docs/DESIGN_LAWS.md` Law II** reads:

> *Every cognitive primitive must trace an unbroken, deterministic DAG of
> `parent_ids` back to Generation 0 empirical events.*

The DAG part holds. **The "back to empirical events" part does not.** Measured
by the A3 auditor: the `parent_ids` chain **terminates at Layer 1** — concepts,
phrases, loops, predictions — which are built from tags. **No parent link in
the engine points at an event.** The structure→event link exists only as
*counts* (support, contradiction), which is a different kind of link, and
§3.2 has said so since this specification was first written.

**This is disclosed, not resolved.** Law II is the frozen engine's constitution
and Organica 1 is frozen, so amending the charter is **the owner's decision,
not a documentation fix**. The README's restatement of the law was corrected to
match what the engine does; the law itself is left as written, with this
disclosure attached, pending the owner's ruling.

**Why it is disclosed rather than dropped.** The trace's own claim depends on
it: the auditor reconstructs **surviving developmental state** (§3.2), and a
reader who believes Law II literally would expect a reconstruction back to
events. The trace cannot deliver that, and says so.

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
### What the trace is for next, and its stop condition

The trace's next job is to be **an input to the acquisition experiment**
(`docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`, Revision 2), not to be
extended. The audit build is finished when **A5 and A6 are closed** — those
two are the only pending criteria — and then it is **tagged, frozen, and
stopped**. After that, **no feature may be added to the instrumentation**; a
new requirement goes to the study's wish-list instead. The instrumentation may
be *fixed* if it is found to be wrong, but not *extended*.

**A1, A2, A3, A4 and A7 are closed and are not reopened.**


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
(2,589 distinct transitions, 241 aggregate edges reconciling, 0 mismatches).

**The result is an implementation match, not a schema guarantee.** The observer
runs the same *ordering clause* as the engine with a wider projection, so the
match is empirical on the tested SQLite implementation — and the evidence for
it is A7's exactness, since a window mismatch would have broken the
reconciliation. The schema still does not settle tied ordering, and a replayer
that did not observe at store time could not rely on it. That is precisely why
A7 requires store-time observation.

**The artifact is committed:** `docs/audit_trace_probe_tie.json` — 60 cycles, 479 tied
windows, A1 692 beliefs / 0 failures, A2 60/60 cycles, A7 692 beliefs / 0 failures with
241 aggregate edges reconciling.

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
  belong to the build. **A3 and A4 have since been measured and are met**
  (§13); **A5 and A6 remain pending.**
- **Independent replication.** "Independently auditable" means **independently
  reconstructed from the engine's state** — an outside reader with the report
  and the substrate can rebuild the decision and check it. It does **not** mean
  **independently replicated by another lab**. No second laboratory has
  reproduced this work; nothing here is a replication result, and the probe's
  generality is bounded to one world family, one configuration and one policy
  (above).
- **The organism's past.** The lineage the trace reconstructs is the
  organism's **surviving, current** structures and their present descent. It
  does not reconstruct the full history of those structures' development
  (see §12, and the present-lineage finding in the journal).
- **Sufficiency.** The probe establishes **fidelity to the implemented rule**:
  the auditor reproduces what the engine did. It does **not** establish that an
  intact reconstruction is a *uniquely correct account of why a belief arose*.
  A reconstruction can be exactly faithful to the algorithm and still be a
  shallow account of development — it explains the arithmetic of selection, not
  why the structures formed in the first place. That is a separate validation
  question, and A3 (§12) is where it begins.
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
  the split is read **for the claim's own support**, under the four conditions
  below — not against a run-level average.
- A claimed **revision** must be visible in the trace as a change in a claim
  whose support is world-derived, with the prior state resolved
  (`revision_delta`, `prior_confidence`).
- A claimed **explanation** must resolve to event ids (§3.3) — not to counts,
  and never to the system's own account of itself.

**And the question this leaves open, which is now measurable.** Whether
self-sourced support *hurts* — whether a claim's self-sourced share predicts
its correctness — is a testable question, and the trace is the first
instrument that can ask it. It is not asked here.

**The disqualifier, stated as a per-claim rule and fixed in advance.** A
run-level share cannot carry a per-claim claim, so the rule is written against
the **claim's own support**:

> **A transfer claim must rest on world-derived evidence, and it must be shown
> to do so.** Concretely, four conditions, all fixed before the next protocol
> runs:
>
> 1. **Report the split for the claim's own support** — the trace's world/self
>    split over that claim's *distinct* evidence. A run-level average is not
>    acceptable evidence for a particular claim.
> 2. **A majority of that support must be world-derived.** A claim resting
>    mainly on the organism's own output is not a transfer claim.
> 3. **Its self-sourced share must be no higher than the reference rate
>    fixed below** — a claim that leans on self-generated evidence *more* than
>    an ordinary belief does has not been carried by the world.
> 4. **The comparison is against the claim, never against the organism in
>    general** — and a failed condition fails the protocol **even if the
>    prediction was correct**.

**The reference rate is FROZEN, not recomputed on the run being judged.**

> **Reference rate: 17.9%** — the distinct-evidence self-sourced share measured on the
> calibration probe (default arm, 120 cycles, `docs/audit_trace_probe.json`).

Two rules about it, both fixed now:

- **It is not recomputed on the evaluated run.** A threshold derived from the
  same data it judges is not a threshold; it is a description that moves with
  the result. A run whose beliefs happen to be unusually self-sourced would
  otherwise relax the criterion that was supposed to constrain it.
- **It may only be re-calibrated on data that is not being judged**, and any
  re-calibration must be recorded before the next protocol runs.

**And it is a provisional calibration value, not a precise universal cutoff.**
It rests on **one run, one world, one policy** (`salience`, the engine's
default). It is a starting point for a rule that needs one, not a constant
nature has been shown to have. The honest description of condition 3 is
therefore *"no more self-sourced than the reference claim's support was"* —
a comparison against a fixed calibration, with all the fragility that implies,
rather than a claim about a universal threshold.

**Why the rule is conservative, and why that is stated rather than hidden.**
The contamination is now **measured, not shown to be consequential**: nothing
yet demonstrates that a self-sourced transition caused a wrong answer. The
qualification is exactly right — the figure is not evidence of harm. So the
disqualifier is a statement about **what counts as evidence of transfer**, not
a claim that the organism is damaged by its own output. That is also why it is
pre-committed: a criterion that only bites once the harm has already been
demonstrated would never bite at all.

**And the question this leaves open, which is now measurable.** Whether
self-sourced support *hurts* — whether a claim's self-sourced share predicts
its correctness — is a testable question, and the trace is the first
instrument that can ask it. It is not asked here.

**Calibrated, not binary.** The disqualifier is not a mood: the trace reports
a *share*, and the probe measured what that share looks like on a world where
the organism is doing ordinary work — **17.9% of the distinct evidence behind reported beliefs
was self-sourced** (§10). That figure is the **baseline** condition 3 above
compares against; it is not itself a per-claim verdict. The measurement gives
the criterion a baseline instead of a vibe.

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
| **V1** | Developmental properties: development occurs, outcomes vary with the experience *schedule* (path dependence; strict order dependence is **not** isolated, because the curriculum comparisons vary the event multiset and order together), curriculum matters, stable regimes emerge. |
| **Phase L** | Regime behaviour with a stable transition region — and the protocol verdict and the characterisation kept as separate artefacts. The transition is robust **within** this engine, world family and support-ratio axis, not a general threshold. |
| **Development audit trace** | The developmental *decision* becomes reconstructible by an outside investigator. Demonstrated, not asserted (§10) — **reconstructed from the engine's state**, not replicated by another lab. |
| **Next** | Can experience produce knowledge that **transfers, predicts and revises** — judged with trace-derived diagnostics pre-committed in advance. |

A coherent progression: *what structures exist* → *what develops and survives*
→ *why it survived* → *whether what it developed is usable in a new situation*.

---

## 12. A3: what it will measure, fixed in advance

**Why this section exists.** A3 is the next measurement, and a criterion whose
definition is written *after* the measurement is not a criterion. This section
fixes what A3 counts, what each number means, and what each outcome would
imply — before anything is run.

### The two graphs, and why they are separate

The trace carries two different kinds of link, and conflating them makes A3
silently impossible:

- **Level 1 — developmental lineage**: candidate → candidate, through
  `parent_ids`. A belief's parents are structures; a structure's parents are
  structures. **This chain terminates at Layer 1** — concepts, phrases, loops,
  predictions — which are built from tags. **No parent link points at an
  event.**
- **Level 2 — evidential linkage**: claim → supporting transitions → events,
  through the counts.

Level 1 answers *"where did this structure come from?"*. Level 2 answers *"what
evidence supports it?"*. A true audit trace needs both, and **success in one
cannot stand in for success in the other**. Asking ancestry resolution to
"reach events" would be asking Level 1 to prove something it was never
designed to represent.

### The three quantities A3 will report, separately

1. **Lineage reachability** — the share of extant structures whose parent chain
   resolves back to **Layer 1** within depth 7.
2. **Evidence linkage** — the share of extant claims whose support resolves to
   **event ids** with a world/self split (A7's machinery, applied as a rate
   rather than as a check).
3. **Truncation split** — for the structures that do *not* resolve, why not, in
   four disjoint categories:
   - **aged out** — the ancestor existed but fell outside the cognition window
     (**a persistence limit**);
   - **depth-truncated** — the chain was longer than depth 7 (**a representation
     limit**);
   - **no parent** — the structure never had one (Layer-1 candidates, markers);
   - **missing record** — a parent id was referenced but no record exists
     (**a data defect**, and the one that would matter most).

### The interpretation the split buys

*"Aged out"* means **history existed and retention erased it** — a persistence
problem. *"Depth-truncated"* means **the developmental chain exists and the
tracing machinery cut it** — a representation problem. They have different
causes and different fixes, and a single percentage cannot distinguish them.
The window's span is now **measured rather than estimated**: the engine
stores **2,374.68 sleep events per cycle**, so the 4,000-event cognition window spans only
**1.7 cycles of stores**. But the measurement went further, and **corrected the
sentence that followed it**: the window's span is **not** the binding constraint
on lineage depth. See §13. The binding constraint is the **death of an
ancestor**, not the window's recency.

**That corrects an earlier estimate by more than an order of magnitude.** This
specification previously said the window spanned "roughly 40–130 cycles",
inferred from a guess about how many sleep events a cycle stores. The
measurement says **1.7 cycles**. The estimate was wrong, and the correction is recorded rather than
quietly fixed — the same way every other correction in this project has been.

Two consequences follow, and they point in opposite directions:

- A lineage that is **still being produced** stays inside the window, because
  candidates are re-stored every cycle. So active lineages may resolve far
  better than the window's tiny span suggests.
- A lineage that **stopped being produced** is gone within about 1.7 cycles. So
  the developmental history of *anything* the organism has moved on from is
  unrecoverable — not censored by a slow decay, but simply not there.

### The boundary A3 cannot cross

A3 measures **reachability**, not **sufficiency**. A high reachability rate
would mean the auditor can follow extant structures back to Layer 1; it would
not mean the reconstructed chain is the *true* developmental history, nor that
the account is complete. And a low rate would not mean the organism has no
developmental history — only that the window no longer holds it. The key
outcome is therefore not the percentage but this:

> **Does the incompleteness reflect the architecture's actual developmental
> history, or the observer's retention limit?**

### What each outcome would mean

| Outcome | Reading |
|---|---|
| High reachability, truncation dominated by "no parent" | The trace is a genuine **developmental** trace for extant structures. |
| High reachability, truncation dominated by "aged out" | The trace is developmental only for the recent past; history older than ~1.7 cycles is **gone**, not censored. |
| Low reachability dominated by "aged out" | The organism's developmental history is **not recoverable** at this window. A persistence finding about V1, not a tracing failure. |
| Low reachability dominated by "depth-truncated" | A **representation** finding: the chains exist but the tracing machinery cuts them, and the auditor needs a deeper walk. |
| Any "missing record" | A **data defect** — a parent id with no record — and the one that would most damage trust in the trace. |

### And the question this leaves open, now that it is measurable

Whether self-sourced support *hurts* — and if so, in what way. The candidate
outcomes, none of them pre-committed: **correctness** (does a
self-sourced-heavy claim predict more errors?), **persistence** (does it last
longer?), **revision resistance** (does it survive contradicting evidence?),
**confidence inflation** (does its confidence overstate what its support
warrants?), and **false-positive rate**. The trace is the first instrument that
can ask these questions. They are a **characterisation study**, not a protocol,
and they are not asked here.

---

## 13. A3: the measurement

**What was run.** An ancestry auditor, added to the probe, that walks each
cycle's reported structures' parent chains against the engine's own cognition
window and classifies every branch that fails to resolve. The definition was
fixed in advance in §12; the criterion is in §6.

### The result

| Quantity | Default arm (120 cycles) |
|---|---|
| **Lineage reachability** | **1.000** — 8,061 of 8,061 structures resolve back to Layer 1 within depth 7 |
| **Evidence linkage** | **1.000** — 1,412 of 1,412 claims resolve to event ids with a world/self split |
| **Truncation split** (structures) | aged out 0 / depth-truncated 0 / no parent 0 / missing record 0 |
| **Branch-level counts** | layer-1 resolved 25,168 / aged out 105 / depth-truncated 0 / no parent 0 |
| **Honesty errors** | 0 |

The same holds on the stress arm (3,240 structures, 1.000) and the forced-tie
arm (3,988 structures, 1.000).

**Read the two counts together.** The *structure-level* split is empty, but
**105 branches were aged out**. Every structure nonetheless resolves, because each one has at
least one parent branch still inside the window. The empty split is therefore
not "nothing aged out" — it is "nothing failed to resolve". Both numbers are
reported for exactly that reason.

### The correction this measurement forced

§12 said the window was *"the more likely binding constraint"*, on the
reasoning that the window spans only 1.7 cycles. **That was wrong, and the
measurement corrected it.**

**Surviving candidates are re-stored every cycle** — Layer-1 candidates by the
natural-selection decay path (`sleep.py:1784-1800`), and higher-layer
candidates by the report's own re-derivation and the stable-prior add-back
(`sleep.py:476-509`). So an ancestor that is still alive stays inside the
window no matter how old it is. **A lineage's depth is not bounded by the
window's recency.**

What the window does bound is the history of anything that **died**. A
candidate that decays below the death threshold is pruned and never stored
again; its last store eventually leaves the 4,000-event window, and the parent
link that pointed at it becomes unresolvable. That is the 105 aged-out branches.

### How much history does Organica actually keep?

**Measured: the window's content age is at most 1 cycle, spanning 2 distinct cycles.**
The window holds 3,998 candidates, and the oldest of them was last stored
one cycle ago. So a *dead* structure's history is unrecoverable almost
immediately, while a *living* one's is recoverable indefinitely — and the
difference is the decay rule, not the window.

### A3's key question, answered

§12 asked: **does the incompleteness reflect the architecture's actual
developmental history, or the observer's retention limit?**

> **It is the same limit, and there is no incompleteness to explain. The
> engine's cognition window *is* its memory. An investigator cannot recover
> more developmental history than Organica retains, because there is no more
> to recover.**

Read that twice, because it cuts both ways. It is good news for the trace:
the auditor reconstructs the lineage of **everything the organism still
holds**, exactly, with zero honesty errors. It is a hard ceiling on the
project's distinguishing property: **developmental provenance in Organica 1
has a horizon of the organism's own memory, and that horizon is about two
cycles for anything that has died.** A claim of developmental provenance that
reaches further back than the organism's own window would be a claim about a
history that does not exist.

### The two sweeps, and why they are diagnostics

A category that never fires is a category that has not been tested. Both
sweeps are **diagnostics of the instrument**, never criteria:

- **Window sweep** — reachability as a function of window size. At the
  engine's window it is 1.000; at 100 candidates it falls to 0.971 with 2
  structures aged out; at 25–50 it falls to 0.000, with 68 structures aged
  out. **"Aged out" is reachable and the measurement moves.**
- **Depth sweep** — reachability as a function of the depth limit. At depth 7
  it is 1.000; at depth 5, 0.985; at depth 3, 0.809; at depth 1, 0.221, with
  53 structures depth-truncated. **"Depth-truncated" is reachable, and the
  engine's depth limit of 7 is not binding** — the chains are shorter than it.

### What this does not establish

It does not establish that the reconstructed chain is the *true* developmental
history (§10's fidelity-is-not-sufficiency boundary still applies), that the
result generalises beyond one world family, one policy and one configuration,
or anything at all about learning or transfer. And **it does not establish
that A3 was the bottleneck** — the measurement says it was not.


---

*Specification written against the frozen `v0.9.0` engine, source read
2026-10-25. The load-bearing claim was subsequently tested by
`benchmarks/audit_trace_probe.py` (§10). Companion documents:
`docs/phase_l_results.md` (the measurement record),
`docs/PHASE-L-SYNTHESIS.md` (the characterisation),
`docs/USER-MANUAL.md` (§8.13, finding 18).*
