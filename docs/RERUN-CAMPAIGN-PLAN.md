# Rerun campaign plan — the two halves and the protocol each one needs

**Status: written. This document runs nothing and freezes nothing.** It allocates the
registry's unanswered and unresolved questions into two halves that need different protocols,
and it names what has to be true before either half's first cell. Every count here is
recomputed from `docs/research_question_registry.json` by `tests/test_rerun_plan.py`, which
fails when this page and the artifact disagree; the artifact outranks this page.

The campaign exists because of the finding in `docs/ENGINE-CHANGE-AUDIT.md`: **none of the
recorded failures was measured on the engine at HEAD.** A rerun on the pinned build is
therefore a different experiment rather than a replication, and it needs its own protocol
before it produces a number.

## 1. Why this is two halves and not one campaign

A **re-derivation** has a comparator: an answer measured on an earlier build, resting on
artifacts that do not name the build pinned now. Its protocol has to say what the old number
was, on which engine it was measured, and what would count as the same answer again. The risk
it runs is **silent drift** — a different endpoint, a different cap, a reused seed — that
produces a number which looks like a replication and is not (`ENGINE-CHANGE-AUDIT.md` §6).

A **first answer** has no comparator. Nothing has been measured, so there is nothing to
reproduce and nothing to contradict. Its protocol cannot borrow the re-derivation's discipline
of comparison and needs a different one: a decision table fixed before the cell, so that the
answer buys an architectural decision rather than another diagnostic (AGENTS.md rule 30).

Treating the two as one campaign produces the defect both halves are trying to avoid: the
first-answer half inherits a comparator it does not have, and the re-derivation half inherits
an open-ended scope it was supposed to be closed against.

## 2. The partition this plan consumes

The registry's reopening record already partitions all of its questions. This plan adds no
partition of its own; it splits one group.

| Group | Count | Where it comes from |
| --- | --- | --- |
| Re-derivations | **12** | `reopening.reopened` |
| First answers | **25** | open and future questions in neither `reopened` nor `kept_closed` |
| First answers runnable now | **19** | of the 25, status `open` |
| First answers gated | **6** | of the 25, status `future` |
| Kept closed, outside the campaign | **17** | `reopening.kept_closed` |
| Campaign questions | **37** | 12 + 25 |
| Registry questions | **54** | 37 + 17 |

The reopening was made against `engine_version` 0.13.0, whose bytes are
`ed0851d119470d2561900471f79f3302ea44184a278c0c622f49ae80e487c4c2` in the same record. That
pin — not a date and not the word "HEAD" — is the campaign's fixed object.

**Disclosure.** The request for this plan named 25 first answers. The registry supports
**25**: 19 `open` and 6 `future`, with no question carrying a prior outcome. **Q002 closed on
2026-11-09** — its presence measurement was re-made on 0.13.0 — so the table now reads 25 first
answers, 19 runnable and 37 campaign questions, with Q002 outside the campaign. The 25/19 are the
counts the campaign starts from, not a licence to schedule a closed row. Q056 is the twenty-fifth
row, registered as future and blocked by Q054; it is listed with the gated rows, not the runnable
ones.

## 3. Half A — the 12 re-derivations, triaged

The twelve reopened questions are not one kind of work. `benchmarks/rerun_triage.py` assigns
each one from the registry and the files, and `tests/test_rerun_plan.py` fails when the buckets
and the files disagree.

| Bucket | Count | Entry condition |
| --- | --- | --- |
| Re-runnable | 11 | a frozen protocol resolves, a JSON comparator exists in the evidence, and a harness module exists |
| Needs harness | 0 | code and a comparator exist, but no frozen protocol does |
| Decision-only | 1 | the question is a judgment; its protocol names the inputs and the decision rule, but it is not a cell |
| Prose-only | 0 | the answer is a judgment with no protocol and no dedicated harness |

**Disclosure.** Eight of the eleven re-runnable rows name at least one protocol without the
`docs/` prefix. The registry is not rewritten; each path is resolved under `docs/` and the
resolved path is listed below, because a citation that does not resolve cannot be checked.

### 3.1 Re-runnable — the eleven cells

| ID | The question, as the registry records it | Protocol | Comparator | Harness |
| --- | --- | --- | --- | --- |
| **Q024** | Does diversity-first admission improve the real engine? | `docs/RANKING-ADMISSION-PREREGISTRATION.md` | `docs/admission_two_arm_result.json` | `benchmarks/run_ranking_admission.py`, `benchmarks/score_ranking_admission.py` |
| **Q004** | Does excluding intra-cell rows buy precision at a fixed cap? | `docs/density_interaction_a2_prereg.json` | `docs/density_interaction_a2_result.json` | `benchmarks/run_density_interaction.py`, `benchmarks/score_density_interaction_a2.py` |
| **Q005** | Does the primary scheme's partial final pass explain the ladder's non-monotonicity? | `docs/density_padding_prereg.json` | `docs/density_padding_result.json` | `benchmarks/density_padding.py` |
| **Q029** | Why do the structures that reach 35 stable edges on a degree-12 hub disappear? | `docs/DECAY-ATTRIBUTION-PREREGISTRATION.md` | `docs/decay_attribution.json` | `benchmarks/decay_attribution.py` |
| **Q030** | Is the engine's temporal edge decay the mechanism that removes the structure? | `docs/DECAY-ATTRIBUTION-PREREGISTRATION.md` | `docs/decay_attribution.json` | `benchmarks/decay_attribution.py` |
| **Q031** | At which cycle does the degree-12 fall begin, and how long does it take? | `docs/DECAY-ATTRIBUTION-PREREGISTRATION.md` | `docs/decay_attribution.json` | `benchmarks/decay_attribution.py` |
| **Q032** | Do theories die before the edges, so that theory death causes the edge loss? | `docs/DECAY-ATTRIBUTION-PREREGISTRATION.md` | `docs/decay_attribution.json` | `benchmarks/decay_attribution.py` |
| **Q036** | What is the persistence half-life of the peak structure? | `docs/DECAY-ATTRIBUTION-PREREGISTRATION.md` | `docs/decay_attribution.json` | `benchmarks/decay_attribution.py` |
| **Q044** | When a stable edge misses re-emission, is the cause the admission count or the ranked slot? | `docs/DECAY-ADMISSION-SLOT-PREREGISTRATION.md` | `docs/decay_admission_slot.json` | `benchmarks/decay_admission_slot.py` |
| **Q043** | Does the engine need a store-time role record, or does the stored record already contain the evidence a transfer trace needs? | `docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md` | `docs/store_time_role_durability.json` | `benchmarks/store_time_role_durability.py` |
| **Q051** | Does 0.9925 rank next-cycle tags better than shipped 0.95 at a late horizon where the shipped theory layer is already dead, but not early? | `docs/LONG-DELAY-CAPABILITY-PREREGISTRATION.md` | `docs/long_delay_capability_confirm.json` | `benchmarks/long_delay_capability_confirm.py`, `benchmarks/long_delay_capability_design.py` |

### 3.2 Needs harness — none

No reopened row is waiting on code. Q021's harness and comparator already existed; the missing
piece was its protocol, now frozen at `docs/Q021-TRANSFER-RE-DERIVATION-PREREGISTRATION.md`.

### 3.3 Decision-only — Q017

| ID | The question | Why it is not a cell |
| --- | --- | --- |
| **Q017** | Should further Layer-1 admission variants be tried? | The answer is a judgment, not a mechanism. `docs/Q017-ADMISSION-DECISION-PREREGISTRATION.md` names Q006 and Q024 as inputs and decides between `RETIRE_NO_FURTHER_VARIANTS`, `BUILD_REQUIRED_VARIANT` and `UNREAD`; it runs no engine and cannot be a cell. |

### 3.4 The Half-A re-derivation list

The eleven re-runnable rows, in execution order. The selection and admission rows come first
because they reuse one comparator and carry the acquisition-bound and Gate 13 traps; the decay
cluster follows in causal order; Q044 extends it; Q043 is independent; Q051 is last because its
endpoint rests on Q024 and Q044.

1. **Q024** — diversity-first admission on the two-arm harness.
2. **Q004** — density exclusion, acquisition-bound comparison.
3. **Q005** — density padding, primary-scheme partial pass.
4. **Q029** — why the degree-12 structure disappears.
5. **Q030** — whether temporal decay is the removal mechanism.
6. **Q031** — when the fall begins and how long it takes.
7. **Q032** — whether theory death causes the edge loss.
8. **Q036** — the peak structure's half-life.
9. **Q044** — admission count or ranked slot.
10. **Q043** — store-time role record.
11. **Q051** — long-delay capability at 0.9925.

Q017 is outside the list: its decision protocol is read after Q024, and it is not a cell.
Q006 and Q021 are closed by their pinned results and are not pending rows.

## 4. Half A protocol

Each requirement exists because one of the audit's traps would otherwise produce a number that
reads as a replication and is not.

1. **Freeze before the first cell, per question.** The protocol is committed before any cell
   runs, with the pre-committed criteria and the stop rule. Rows without a protocol do not run.
2. **Pin the engine and check it twice.** `python -m benchmarks.engine_pin --check` must pass at
   freeze and again at analysis, against the 0.13.0 record named in §2. A module that moved
   under a version bump voids the campaign; it does not silently re-pin.
3. **Name the comparator explicitly.** The audit's §8 requires choosing between `v0.9.0` (the
   archival reference), `v0.12.0` (the deposit object) and the pinned candidate rather than
   letting the old artifact imply one. The old number is quoted as history, labelled with the
   build it came from, and is never the reference for a verdict.
4. **Reuse the endpoint, not a reimplementation.** The metric module the original run used is
   imported, so a re-derived answer cannot quietly be a new endpoint. An endpoint that cannot
   be computed on this build is reported **not measurable** and excluded — never `0.0`
   (AGENTS.md rule 13b).
5. **Fresh seeds, checked before the cell.** Each cell's seeds are checked against the
   consumed-seed scan that Stage B already keeps before the cell runs. A reused seed measures
   the same draw again, which is the one thing a re-derivation must not do.
6. **A control the harness can fail.** Each half-A harness reruns its known-failing case first.
   If the control passes where the record says it failed, the harness is wrong, not the engine.
7. **Judge the criterion set whole, then classify.** The classification is *survived*,
   *changed magnitude* or *reversed*, as `docs/v1_impact.json` did for V1, and it is read on all
   pre-committed criteria at once. The reopened question's old answer stays in the registry as
   the historical observation it is; nothing is re-scored (AGENTS.md rules 14 and 16).
8. **Carry the four rerun traps.** The acquisition bound (the cap moved after the recorded
   `0-3 / 112`), Gate 13 before and after Amendment 1, cross-context only at `e6d1bcc` or later,
   and Phase L as the exception whose verdict stays `INCONCLUSIVE` whatever the rerun shows
   (`ENGINE-CHANGE-AUDIT.md` §6). C1's corrected status — **failed as pre-registered** — and
   H2's **untested in an admissible form** travel with the campaign and are not upgraded in it.

## 5. Half B — the 25 first answers

None of these has an outcome on record, so none has a comparator. Nineteen are `open`; five are
`future` and name the question that gates them.

| ID | The question, as the registry records it | Preregistration named |
| --- | --- | --- |
| **Q001** | Can developmental structure form in Organica 1? | none recorded |
| **Q003** | Can a frequency-ranked selection find the world's edges at the engine's cap? | none recorded |
| **Q007** | Does internal structure improve held-out prediction at the tested endpoint? | none recorded |
| **Q008** | Do the architecture's own motivational mechanisms drive development in the predicted direction? | none recorded |
| **Q011** | Does a consolidated schema buy acquisition latency across a vocabulary boundary? | `docs/CROSS-CONTEXT-REUSE-PREREGISTRATION.md` |
| **Q012** | Does role abstraction remove the orthogonal-context dependence? | none recorded |
| **Q013** | Does the corrected prior reader change the retention reading? | none recorded |
| **Q014** | Does a rank-sensitive endpoint reward the prior that the acquisition endpoint cannot? | none recorded |
| **Q015** | Is temporal decay necessary for liveness? | none recorded |
| **Q016** | Can the candidate space be changed so that world edges cluster under some ranking? | none recorded |
| **Q018** | Should another Gate 13 ranking variant be run? | none recorded |
| **Q028** | Can a transfer event be traced to the role satisfaction that licensed it? | `STORE-TIME-ROLE-RECORD-PREREGISTRATION.md` |
| **Q033** | During collapse, is a stable core retained or does the whole structure collapse? | `DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md` |
| **Q034** | Is the collapse deterministic or stochastic across seeds? | `DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md` |
| **Q035** | Is persistence independent of the theory budget? | none recorded |
| **Q037** | Which mechanism accounts for most of the loss? | `DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md` |
| **Q045** | Does raising the prediction budget or applying the adopted diversity-first ranking extend theory-layer persistence on the degree-12 hub? | `PERSISTENCE-REPAIR-PREREGISTRATION.md` |
| **Q053** | Can competition be preserved or regenerated without globally reducing forgetting, and does that produce a capability gain over shipped 0.95? | `docs/Q053-MECHANISM-PREREGISTRATION.md` |
| **Q054** | Where do world edges leave the path between raw presence and final assertion, once the observer provably does not change what the engine admits? | `docs/PRESENCE-CONVERSION-2-PREREGISTRATION.md` |

The six gated rows are not scheduled. They are valid only after their prerequisite, and
**Q012 is the lock on five of them**; Q054 gates Q056:

| ID | The question, as the registry records it | Gated by |
| --- | --- | --- |
| **Q022** | Can role representations transfer across domains? | `Q012` |
| **Q023** | Can transfer recursively improve future transfer? | `Q022` |
| **Q025** | What fraction of the transfer signal is role-specific rather than general priming? | `Q012` |
| **Q026** | Does role-based transfer persist once the origin context is gone? | `Q012` |
| **Q027** | Do transferred structures survive selection on their own? | `Q012` |
| **Q056** | What makes a developed, admitted or asserted structure behaviourally active, and does that activation produce an external advantage? | `Q054` |

Seven of the twenty-three name a preregistration; the other sixteen need one written. Two of
them are live questions the record already constrains: Q018's space is closed by measurement
rather than by taste — precision never exceeded the ceiling across the measurements in
`docs/gate13_allocation_rule.json` under two allocation rules, and a per-source rule does worse
than the global one — and Q015 asks about the necessity of the mechanism that Q029 to Q037 are
about to re-derive.

## 6. Half B protocol

1. **Say in the protocol's first line that it is a first measurement.** A first answer may not
   be compared to a pre-0.13.0 number as though the two were one series; where the old number
   is quoted it is labelled a cross-build observation.
2. **One preregistration per question, before its cells.** The sixteen without one are
   written first. A first answer without a frozen criterion has no bar to clear, and whatever it
   returns becomes the answer by default.
3. **A decision table per row, before any cell** (AGENTS.md rule 30). Each row names the
   architectural decision a positive result enables and a **different** decision a negative one
   enables. Rows whose two outcomes both lead to "run another diagnostic" are excluded from the
   campaign rather than bundled into it — the discipline the change map used when it kept ten of
   its fourteen rows. Q018 is the row most at risk of failing this test and is decided before
   any cell. The gate is mechanical rather than a reading: `tests/test_rule30.py` judges every
   change-map campaign row and every preregistration decision table, and its controls prove it
   fires on a pair of outcomes that both point at another diagnostic.
4. **Instrument audit before the first cell.** The independent variable must vary what it claims
   to vary, every condition must have a denominator, and an identical value across a sweep is a
   measurement defect until shown otherwise (AGENTS.md rule 13). The engine pin check of §4.2
   applies unchanged.
5. **Attribution rows need a store-time observer.** Q028 and Q043 ask for event-level
   attribution, and the engine's lookback window includes the event being stored with no
   `rowid` tiebreak, so a post-hoc replay is unsound. The observer mirrors the engine's own
   guard, and its build is labelled separately (AGENTS.md rule 17d).
6. **No first answer widens past its endpoint.** The claim is what the endpoint measured, on the
   population and axis it measured it on (AGENTS.md rule 24).
7. **Q012 runs first among the open nineteen**, because five gated rows and one further
   question wait on it. The six gated rows are scheduled only after their prerequisite is answered
   in this build.

## 7. What is outside the campaign

The fourteen kept-closed questions are not cells. Ten are kept closed because an artifact
behind the answer names the pinned release; four because the closure was a governance or design
decision rather than a measurement. The registry itself says the stamped ones are the first
candidates for **byte-level re-verification**, which is a check of attribution, not a research
cell — and the four governance closures are not measurements that a cell could re-derive.

## 8. Sequencing and gates

**Half A before Half B.** Eleven of Half A's twelve rows are re-runnable; Q006 and Q021 are
closed by their pinned results, and Q017 is decision-only, so it is not scheduled as a cell.
and several Half B rows rest on instruments Half A re-derives: Q045 and Q053 assume the
diversity-first ranking and the decay/admission findings that Q024, Q044 and Q051 are about.
Running Half B first would ask a first question on top of an answer that has not yet been shown
to survive the pinned build.

**Within Half A, the four trapped rows are resolved before their neighbours.** The acquisition
bound, Gate 13 and the cross-context run each need their comparator named and their pre-change
number labelled before any cell, or the row measures a different engine under a different bound.

**Campaign-level gates, neither of which this document discharges:**

- an independently reviewed preregistration, the same gate `docs/DECISION-STAGE-B-SEQUENCE.md`
  applies to Stage B, because the campaign's purpose is to be inconvenient to its author;
- a change-to-failure map with a mechanism and a falsifier per row, which
  `docs/ENGINE-CHANGE-AUDIT.md` §8 requires and the generated
  `docs/ENGINE-CHANGE-FAILURE-MAP.md` supplies.

## 9. What this document does not do

It does not run a cell, freeze a protocol, re-score a verdict, or assert that any change improved
anything. It does not add a question, retire one, or reopen one: the partition it consumes is the
one already in the registry. It allocates the two halves and names, per half, the protocol each
needs before its first cell — which is the most a plan can do without becoming a pre-registration.
