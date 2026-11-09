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
| Re-derivations | **14** | `reopening.reopened` |
| First answers | **24** | every question in neither `reopened` nor `kept_closed` |
| First answers runnable now | **19** | of the 24, status `open` |
| First answers gated | **5** | of the 24, status `future` |
| Kept closed, outside the campaign | **13** | `reopening.kept_closed` |
| Campaign questions | **38** | 14 + 24 |
| Registry questions | **51** | 38 + 13 |

The reopening was made against `engine_version` 0.13.0, whose bytes are
`ed0851d119470d2561900471f79f3302ea44184a278c0c622f49ae80e487c4c2` in the same record. That
pin — not a date and not the word "HEAD" — is the campaign's fixed object.

**Disclosure.** The request for this plan named 25 first answers. The registry supports
**24**: 19 `open` and 5 `future`, with no question carrying a prior outcome, and
14 + 24 + 13 is the 51 the partition test checks. The plan uses the artifact's 24. If a
twenty-fifth question is meant, it has to arrive as a registry row with a status and a
question, because a campaign slot with no row behind it cannot be preregistered.

## 3. Half A — the 14 re-derivations

Every one of these carries `measured_on: unattributed -- no artifact it rests on records an
engine_version`, and every one was reopened for that reason. The question text, the
preregistration the registry names, and the first artifact in its evidence are reproduced
below from the registry.

| ID | The question, as the registry records it | Preregistration named | First artifact in its evidence |
| --- | --- | --- | --- |
| **Q004** | Does excluding intra-cell rows buy precision at a fixed cap? | `docs/density_interaction_a2_prereg.json` | `docs/density_interaction_a2_result.json` |
| **Q005** | Does the primary scheme's partial final pass explain the ladder's non-monotonicity? | `docs/density_padding_prereg.json` | `docs/density_padding_result.json` |
| **Q006** | Does a Layer-1 admission filter change candidate availability on this engine? | `docs/ADMISSION-TWO-ARM-PREREGISTRATION.md` | `docs/DECISION-ADMISSION-RULE.md` |
| **Q017** | Should further Layer-1 admission variants be tried? | none recorded | `docs/DECISION-ADMISSION-RULE.md` |
| **Q021** | Can a transfer claim rest on the v1 TR = 3.2 result? | none recorded | `docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md` |
| **Q024** | Does diversity-first admission improve the real engine? | `docs/RANKING-ADMISSION-PREREGISTRATION.md`, `docs/ADMISSION-TWO-ARM-PREREGISTRATION.md` | `docs/DECISION-ADMISSION-RULE.md` |
| **Q029** | Why do the structures that reach 35 stable edges on a degree-12 hub disappear? | `DECAY-ATTRIBUTION-PREREGISTRATION.md`, `DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md` | `docs/decay_attribution.json` |
| **Q030** | Is the engine's temporal edge decay the mechanism that removes the structure? | `DECAY-ATTRIBUTION-PREREGISTRATION.md`, `DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md` | `docs/decay_attribution.json` |
| **Q031** | At which cycle does the degree-12 fall begin, and how long does it take? | `DECAY-ATTRIBUTION-PREREGISTRATION.md`, `DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md` | `docs/decay_attribution.json` |
| **Q032** | Do theories die before the edges, so that theory death causes the edge loss? | `DECAY-ATTRIBUTION-PREREGISTRATION.md`, `DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md` | `docs/decay_attribution.json` |
| **Q036** | What is the persistence half-life of the peak structure? | `DECAY-ATTRIBUTION-PREREGISTRATION.md`, `DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md` | `docs/decay_attribution.json` |
| **Q043** | Does the engine need a store-time role record, or does the stored record already contain the evidence a transfer trace needs? | `STORE-TIME-ROLE-RECORD-PREREGISTRATION.md` | `docs/store_time_role_durability.json` |
| **Q044** | When a stable edge misses re-emission, is the cause the admission count or the ranked slot? | `DECAY-ADMISSION-SLOT-PREREGISTRATION.md` | `docs/decay_attribution.json` |
| **Q051** | Does 0.9925 rank next-cycle tags better than shipped 0.95 at a late horizon where the shipped theory layer is already dead, but not early? | `LONG-DELAY-CAPABILITY-PREREGISTRATION.md` | `docs/LONG-DELAY-CAPABILITY-PREREGISTRATION.md` |

Twelve of the fourteen name a preregistration. **Q017 and Q021 name none**, and a re-derivation
without a protocol is a fresh measurement wearing an old question's number — so each of those
two needs its own preregistration before its first cell. Several of the named records are
written without the `docs/` prefix; each is resolved to a file path at freeze, because a
citation that does not resolve cannot be checked.

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

## 5. Half B — the 24 first answers

None of these has an outcome on record, so none has a comparator. Nineteen are `open`; five are
`future` and name the question that gates them.

| ID | The question, as the registry records it | Preregistration named |
| --- | --- | --- |
| **Q001** | Can developmental structure form in Organica 1? | none recorded |
| **Q002** | Are the world's own edges present in memory at the engine's budget, so that a candidate shortage is ruled out? | none recorded |
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

The five gated rows are not scheduled. They are valid only after their prerequisite, and
**Q012 is the lock on four of them**:

| ID | The question, as the registry records it | Gated by |
| --- | --- | --- |
| **Q022** | Can role representations transfer across domains? | `Q012` |
| **Q023** | Can transfer recursively improve future transfer? | `Q022` |
| **Q025** | What fraction of the transfer signal is role-specific rather than general priming? | `Q012` |
| **Q026** | Does role-based transfer persist once the origin context is gone? | `Q012` |
| **Q027** | Do transferred structures survive selection on their own? | `Q012` |

Seven of the twenty-four name a preregistration; the other seventeen need one written. Two of
them are live questions the record already constrains: Q018's space is closed by measurement
rather than by taste — precision never exceeded the ceiling across the measurements in
`docs/gate13_allocation_rule.json` under two allocation rules, and a per-source rule does worse
than the global one — and Q015 asks about the necessity of the mechanism that Q029 to Q037 are
about to re-derive.

## 6. Half B protocol

1. **Say in the protocol's first line that it is a first measurement.** A first answer may not
   be compared to a pre-0.13.0 number as though the two were one series; where the old number
   is quoted it is labelled a cross-build observation.
2. **One preregistration per question, before its cells.** The seventeen without one are
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
7. **Q012 runs first among the open nineteen**, because four gated rows and one further
   question wait on it. The gated five are scheduled only after their prerequisite is answered
   in this build.

## 7. What is outside the campaign

The thirteen kept-closed questions are not cells. Nine are kept closed because an artifact
behind the answer names the pinned release; four because the closure was a governance or design
decision rather than a measurement. The registry itself says the stamped ones are the first
candidates for **byte-level re-verification**, which is a check of attribution, not a research
cell — and the four governance closures are not measurements that a cell could re-derive.

## 8. Sequencing and gates

**Half A before Half B.** Half A's protocols are already frozen for twelve of its fourteen rows,
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
