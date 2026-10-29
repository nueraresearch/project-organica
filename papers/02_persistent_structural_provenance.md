# Paper 2: Reconstructing Evidence and Selection from Organica's Surviving State

**Authors:** Jeremy et al. (Nuera Research)
**Draft status:** Evidence-alignment revision, 2026-10-27; A5/A6 closed and the audit layer frozen at `audit-trace-v1` on 2026-10-28. Academic-grade revision, 2026-10-29: the abstract and §3 still stated that A5 and A6 "remain pending" and that the instrumentation "is not yet frozen", contradicting this line and the conclusion of the same document; the contradiction is corrected here and recorded in this line rather than applied silently. Not submitted or published.
**Scope:** Reconstruction fidelity for tested probes and surviving current structures.
**Repository:** [`nueraresearch/project-organica`](https://github.com/nueraresearch/project-organica), branch `master`; instrumentation frozen at tag `audit-trace-v1`.

## Abstract

Developmental systems can expose a record of how their current structures were formed, but a reconstruction claim must specify what the record can recover and under which conditions. We report the Organica audit-trace probes as bounded reconstruction tests, not as proof of universal explainability or complete historical memory. In the measured A3 runs, all 8,061 of 8,061 structures resolved to Layer 1 within the configured depth, and all 1,412 of 1,412 claims resolved to event identifiers with a world/self evidence split. The forced-tie and stress probes also retained structure-level reachability, while branch-level accounting recorded aged-out ancestors. These results support exact reconstruction of the tested surviving state under the tested SQLite implementation. They do not recover ancestry that the engine itself no longer retains, establish causal sufficiency, or constitute independent replication by another laboratory. A5 field honesty and A6 trace/counterfactual separation are closed (2026-10-28), each verified by a proof-of-firing test, and the audit instrumentation is tagged and frozen at `audit-trace-v1`.

We make three contributions beyond this bounded result. **First, a non-vacuity argument.** A reconstruction test is only informative if the reconstruction was in a position to fail; we therefore report the conditions under which the selection axis became load-bearing (the default arm's candidate cap never bound, so the stress arm — in which 403 candidates lost on rank — carries that test) and the conditions under which it did not. **Second, an explicit accounting of every reported rate.** Self-sourcing is reported against three separately named populations — the distinct supporting transitions behind reported beliefs (802 of 4,481 = 17.9%), the pooled support references across reporting cycles (53,980 of 307,857 = 17.5%), and all distinct transitions the observer recorded (5,436 of 12,583 = 43.2%) — because a single unqualified "self-sourced share" would misrepresent the record by more than a factor of two. **Third, a stated boundary on the instrument's reach.** The cognition window holds 4,000 sleep events, which the engine's own storage rate (2,374.68 sleep events per cycle) makes equivalent to 1.7 cycles, so the developmental history of any structure the organism has moved on from is unrecoverable — not slowly censored.

## 1. Introduction

A developmental architecture forms candidate structures from experience. Those structures are then reported: as beliefs, concepts, predictions, hypotheses, workflows. The natural question is whether the system's own account of *why* it holds a belief can be checked. Three positions are commonly taken, and the present work is deliberately narrower than all three.

The first is that the system's self-report is sufficient: the belief carries a support count and a confidence, and those numbers are the explanation. The second is that an outside observer can reconstruct the formation history from the substrate alone, with no reliance on the system's self-report. The third, which we adopt, is that reconstruction is possible **within a stated scope**, and that the scope — which structures, which history, which implementation, which population — must be part of the claim rather than a caveat appended to it.

Our subject is Organica 1, a developmental architecture in which candidate structures are formed by a fixed engine over a stream of tagged events and consolidated across cycles. The engine is frozen at tag `v0.9.0` and the audit instrumentation is frozen at `audit-trace-v1`; no engine file was modified, instrumented, or re-run with different semantics for the measurements reported here.

We report three measurements. **A1** tests whether an outside observer can replay the evidence behind every reported belief; **A2** tests whether it can reproduce the selection contest exactly, including the candidates that died and the candidates that lost on rank; **A7** tests whether it can attribute every supporting transition to specific event identifiers and split them by world/self provenance. **A3** separately tests ancestry honesty, **A4** separately tests that the observer does not perturb the organism, and **A5**/**A6** enforce that every numeric field in the emitted record carries its exact semantics and that no counterfactual field appears in the trace.

The paper's claim is deliberately narrow: *for the tested probes, the tested engine states, and the tested SQLite implementation, an outside observer can reconstruct the surviving developmental state and the evidence behind it exactly, and can be held to account when it is wrong.* It is not a claim of causal explanation, of complete historical recovery, or of independent replication.

## 2. Positioning

This paper sits in the space between two established concerns. The first is **interpretability by external reconstruction**: the practice of building an outside account of a model's internal state that a reader can check, rather than trusting a narrative the model produces about itself. The second is **provenance in machine-generated data and scientific workflows**: the requirement that an artifact record where each item came from, so that a downstream claim can be traced and a contamination source can be identified.

Organica's audit trace is an instance of the first applied to a developmental system, with the discipline of the second: every reported belief must resolve to concrete event identifiers, and every supporting transition must be attributed by provenance.

Three distinctions place this work relative to that literature.

**Reconstruction is not replication.** The observer here runs against the same substrate as the engine. It is independent of the engine's *implementation* in the sense that it re-derives the decision from persisted state and published rules rather than reading the engine's internals, but it is not independent of the engine's *run*: it observes the same database, and no second laboratory has reproduced this work. Where a community standard treats "independently auditable" as implying a second implementation, our usage is narrower and the difference is load-bearing.

**Fidelity is not sufficiency.** Reproducing the implemented rule exactly does not establish that the reconstruction is the uniquely correct account of *why* a belief arose. The implemented rule is one defensible account; an exact replay of it is evidence that the implementation was understood, not that the resulting explanation is the right one.

**Scope is part of the claim.** The trace reconstructs the organism's *surviving, current* structures and their present descent. It does not reconstruct the full history of how those structures formed, because the organism does not retain that history either (§4.4).

**Open for submission.** This section states the paper's position; it is not a literature survey, and the citations for each distinction above must be supplied before submission. No claim in this paper depends on a citation that has not been read.

## 3. Methods

### 3.1 System under audit

Organica 1 receives a stream of tagged events, stores them in a SQLite substrate (`events`, `precedes`, `cooccurrences`, `tag_counts`, `sleep_cycles`, `meta`), and forms candidate structures during a periodic consolidation cycle. Beliefs are hypotheses: a subject, an expectation, a support count, a competing-flow count, and a confidence, together with a salience computed from tension, curiosity, novelty and revision components.

The engine is frozen at `v0.9.0`; `tests/test_v1_freeze.py` compares every frozen file against that tag and fails if one differs. The audit instrumentation is frozen at `audit-trace-v1`; no feature may be added to it from that tag, though it may be *fixed* if found wrong.

### 3.2 The observer

The observer subclasses `MemoryService`, calls the parent implementation unchanged, and only reads. It never writes to the substrate and never alters engine state. This is verified rather than asserted: **A4** runs the same seed with the observer on and off and requires that every reported field is identical (`A4_behaviour_invariance`, 12 cycles, seed 20261025, `observer_on_equals_observer_off` = true).

The observer re-derives each decision from persisted state using the engine's published rules — the lookback window, the selection policy, the retention rule — rather than inspecting the engine's in-memory objects.

### 3.3 The two graphs

The trace carries two graphs, and conflating them is the most common way this kind of record is misread.

**Level 1 — provenance.** Candidate ancestry links structures back to their parents, terminating at Layer 1. The engine's `parent_ids` chain terminates at Layer 1: concepts, phrases and loops are built from tags, and **no parent link points at an experience event**. A structure's connection to raw experience exists only as a count.

**Level 2 — evidence.** Evidence linkage connects each reported claim to the supporting transitions that back it, and each transition to the event identifiers that produced it, with a world/self split.

The two are separate populations and neither stands in for the other. Lineage reachability is computed over reported structures **whose type is not a Layer-1 type**; Layer-1 structures are terminals and have no parent link, so including them would inflate the rate with a trivial population.

### 3.4 Protocol and arms

The probe runs against the frozen ground-truth world generator (`generate_cause_world`, in `organica/ground_truth_worlds.py`), 8 events per cycle, retention policy `salience`, seed 20261025, in three arms.

| Arm | Cycles | Hypothesis cap | Purpose |
|---|---|---|---|
| default | 120 | 15 | the engine's default configuration; longest horizon |
| stress | 60 | 5 | cap tightened so **selection is load-bearing** — candidates must lose on rank |
| forced-tie | 60 | 15 | timestamps patched so the lookback window is **genuinely ambiguous** |

The default arm is the engine as it runs. The stress arm exists because of a property of the default arm that is easy to miss and decisive for the interpretation of A2: the belief pool peaked at **12** against a cap of **15**, so **the cap never bound and no candidate ever lost on rank** (`total_lost` = 0, `total_died` = 4). An exact-reconstruction test on that arm cannot distinguish a correct reconstruction of *ranking* from a correct reconstruction of *nothing to rank*. The stress arm restores the contrast: with the cap at 5, **403 candidates lost on rank** and the reconstruction stayed exact.

The forced-tie arm exists because the engine's lookback query is `ORDER BY time DESC LIMIT 3` with no tie-breaker. Under equal timestamps the window is not determined by the schema. The arm patches the clock so that every four consecutive stores share a timestamp, producing **479 stores with a genuinely tied window**, and requires the observer to reproduce the engine's choice anyway.

### 3.5 Measured quantities, and their populations

Every rate in this paper is reported against a named population. The table is the paper's central methodological commitment.

| Quantity | Definition | Population | Default-arm value |
|---|---|---|---|
| Lineage reachability | share of reported non-Layer-1 structures resolving back to Layer 1 within depth 7 | reported structures of non-Layer-1 type | 8,061 / 8,061 = **1.000** |
| Evidence linkage | share of reported claims whose support resolves to event ids with a world/self split fully accounting for the reported support count | reported hypotheses with a real expectation | 1,412 / 1,412 = **1.000** |
| Truncation split | unresolved structures split into *aged out* / *depth-truncated* / *no parent* / *missing record* | reported non-Layer-1 structures | 0 / 0 / 0 / 0 |
| Branch-level accounting | the same split computed over branches rather than structures | surviving branches | **105 aged out**; 25,168 Layer-1 terminals |
| Self-sourced share (disqualifier's figure) | share of *distinct* supporting transitions behind reported beliefs that are self-sourced | deduplicated by (from, to, prior event id, to event id), restricted to edges backing a reported belief | 802 / 4,481 = **17.9 %** |
| Self-sourced share (weighted view) | the same support counted once per belief per cycle in which the belief is reported | belief-cycle support references | 53,980 / 307,857 = **17.5 %** |
| Self-sourced share (context) | share of *all* distinct transitions the observer recorded that are self-sourced | every distinct transition recorded, including edges no reported belief rested on | 5,436 / 12,583 = **43.2 %** |
| Cognition-window span | cycles of history recoverable from the engine's 4,000-event cognition window | engine storage rate, 2,374.68 sleep events per cycle | **1.7 cycles** |

The three self-sourced shares are **not** three estimates of one quantity, and the differences are not noise. The disqualifier's figure (17.9 %) describes the evidence actually behind the system's claims. The context figure (43.2 %) describes the organism's whole distinct transition surface — nearly half of it is its own sleep output. Reporting either without the other would misrepresent the record by more than a factor of two.

### 3.6 Acceptance criteria, and the requirement that each can fail

Seven criteria govern the instrumentation. A criterion that cannot fail is decoration, so each is verified by a test that **proves the check fires** when it should.

| Criterion | Requirement | Proof-of-firing test |
|---|---|---|
| A1 | evidence replay exactness: replayed support equals reported support for every belief in every cycle | `test_a_wrong_auditor_is_caught_on_the_evidence_axis` |
| A2 | selection reconstruction exactness: reconstructed retained set equals reported retained set, cycle by cycle, including who died and who lost on rank | `test_a_wrong_auditor_is_caught` |
| A3 | ancestry honesty: every ancestry node is resolved within the window or explicitly marked absent **with the window bound stated** | `test_a3_can_fail_when_an_out_of_window_parent_is_called_absent`, `test_a3_can_fail_when_an_in_window_parent_is_called_absent`, `test_a3_can_fail_when_the_window_bound_is_missing` |
| A4 | behavior invariance: the observer changes no reported field | `test_observer_does_not_change_the_engine` |
| A5 | field honesty: every numeric field carries its exact semantics | `test_a5_field_honesty_fails_on_mislabelled_count` |
| A6 | trace / counterfactual separation: the trace contains no counterfactual field; any replay lives in a separate, labeled artifact | `test_a6_counterfactual_separation_fails_on_counterfactual_field` |
| A7 | event-level attribution: every supporting transition resolves to event ids with a world/self split | `test_a_wrong_observer_is_caught_on_the_attribution_axis` |

Supporting tests cover the deduplication of the distinct-evidence view (`test_distinct_evidence_is_deduplicated`), the reproduction of the engine's choice under forced ties (`test_forced_timestamp_ties_are_reproduced`), the sensitivity and reachability of the truncation split (`test_the_truncation_split_is_reachable_and_sensitive`), the ordering of the window sweep (`test_the_window_sweep_takes_the_newest_candidates`), the exclusion of Layer-1 terminals from the lineage population (`test_layer1_structures_are_terminals_and_are_not_counted_as_lineage`), and the end-to-end reconstruction (`test_probe_reconstructs_the_engine_decision`).

The distinction the acceptance criteria are designed to catch is the one that matters most for this kind of record: a field that is *nearly right* — "4 contradictory observations" when the quantity is the subject's **competing flow** — is more damaging than an obviously wrong one, because it passes an inattentive read. A5 exists because of it.

### 3.7 Reproduction

The probe is an instrument probe, not an experiment about the organism. It makes no claim about what Organica does; it checks whether an outside auditor can reproduce what the engine did.

```bash
# the three arms (defaults: --cycles 120 --seed 20261025, --out docs/audit_trace_probe.json)
python benchmarks/audit_trace_probe.py
python benchmarks/audit_trace_probe.py --cycles 60 --max-hypotheses 5 \
    --out docs/audit_trace_probe_stress.json
python benchmarks/audit_trace_probe.py --cycles 60 --force-tie \
    --out docs/audit_trace_probe_tie.json

# the acceptance tests
python -m pytest tests/test_audit_trace_probe.py tests/test_audit_ancestry.py -q
```

## 4. Results

### 4.1 Selection reconstruction (A1, A2)

Across all three arms, the reconstruction was exact and no cycle failed.

| Arm | Cycles | A1 beliefs checked | A1 failures | A2 cycles checked | A2 failures | Candidates lost on rank | Candidates that died |
|---|---|---|---|---|---|---|---|
| default | 120 | 1,412 | **0** | 120 | **0** | **0** | 4 |
| stress | 60 | 290 | **0** | 60 | **0** | **403** | 3 |
| forced-tie | 60 | 692 | **0** | 60 | **0** | **0** | 4 |

The stress arm is the load-bearing row. It is the only arm in which the selection contest actually decided anything — 403 candidates lost on rank — and it is the arm in which the reconstruction still matched exactly, cycle by cycle, for both the retained and the rejected candidates.

### 4.2 Event-level attribution (A7)

Every supporting transition resolved to event identifiers, with no mismatches and nothing attributed that was absent from the aggregate.

| Arm | Claims checked | Failures | Aggregate edges reconciled | Edge mismatches | Attributed but absent |
|---|---|---|---|---|---|
| default | 1,412 | **0** | 244 | **0** | **0** |
| stress | 290 | **0** | 241 | **0** | **0** |
| forced-tie | 692 | **0** | 241 | **0** | **0** |

The three self-sourced views, reported separately with their populations as set out in §3.5:

| View | Default | Stress | Forced-tie |
|---|---|---|---|
| Distinct evidence behind reported beliefs (the disqualifier's figure) | 802 / 4,481 = **17.9 %** | 384 / 2,521 = **15.2 %** | 452 / 2,589 = **17.5 %** |
| Pooled support references (weighted) | 53,980 / 307,857 = **17.5 %** | 4,554 / 30,529 = **14.9 %** | 12,897 / 77,361 = **16.7 %** |
| All distinct transitions recorded (context) | 5,436 / 12,583 = **43.2 %** | 2,692 / 6,291 = **42.8 %** | 2,676 / 6,275 = **42.6 %** |

The **17.9 %** figure is **frozen** as the reference rate for the project's pre-committed per-claim disqualifier, and is not recomputed on any run it judges; it is a provisional calibration value from one world, one policy and one run, not a universal constant. It is a **support-composition statistic**: it says what fraction of the evidence behind the system's claims is the system's own prior output. It is **not** an error rate, and it does not by itself establish that self-sourced support causes errors.

### 4.3 Ancestry honesty (A3)

| Arm | Structures checked | Resolved | Reachability | Truncation split (all four cells) | Aged-out branches | Layer-1 terminals | Honesty errors | Evidence linkage |
|---|---|---|---|---|---|---|---|---|
| default | 8,061 | 8,061 | **1.000** | 0 / 0 / 0 / 0 | 105 | 25,168 | **0** | 1,412 / 1,412 = **1.000** |
| stress | 3,240 | 3,240 | **1.000** | 0 / 0 / 0 / 0 | 43 | 9,449 | **0** | 290 / 290 = **1.000** |
| forced-tie | 3,988 | 3,988 | **1.000** | 0 / 0 / 0 / 0 | 224 | 12,887 | **0** | 692 / 692 = **1.000** |

The empty structure-level truncation split and the non-empty branch-level count are compatible: every structure resolved through at least one branch that remained in the window. The branch-level count is the informative one — it records branches that aged out, which is the signature of history the organism no longer holds (§4.4).

Structures reported in cycle *N* are traced against the window the engine would read for them, namely the window as it stands **after** cycle *N*'s candidates are persisted. Tracing against the window read *before* that cycle would miss the structures' own parents, which do not yet exist in the substrate at that point.

### 4.4 Behavioral invariance, and the boundary of the instrument

**A4** passed: with the observer on and off, every reported field was identical over 12 cycles.

The boundary is set by the engine's own memory, and it was measured rather than estimated. The cognition window is the most recent **4,000 sleep events**, and the engine stores **2,374.68 sleep events per cycle** in the default arm (284,962 sleep events over 120 cycles; **2,230.85** in the stress arm and **2,259.33** in the forced-tie arm). The window therefore spans **1.7 cycles** in the default arm and **1.8** in the other two — not the 40–130 cycles an earlier estimate in this project asserted from a guess. The consequence is sharp: a structure that keeps being produced stays inside the window, because candidates are re-stored every cycle; one that stops being produced is gone within about 1.7 cycles. **The developmental history of anything the organism has moved on from is unrecoverable** — not slowly censored, absent — and the trace is bounded by the organism's memory rather than by the observer's.

### 4.5 What the results do and do not show

They show that the observer can reproduce the engine's selection decisions exactly, resolve every reported belief's support to event identifiers with a provenance split, resolve every reported structure's ancestry to a Layer-1 terminal within the window, and do so without perturbing the organism. In the one arm where selection was load-bearing, it stayed exact while candidates were being discarded.

They do not show that the reconstruction is the uniquely correct account of why a belief arose; that the organism's discarded developmental history can be recovered; that the self-sourced share represents an error rate; or that any second laboratory can reproduce the result independently.

## 5. Discussion

The most transferable finding of this work is not the reconstruction rate — it is the **non-vacuity argument**. A reconstruction test is easy to pass by construction if the system under audit never had to make a decision the observer could get wrong. Reporting the conditions under which each criterion became load-bearing, and including an arm in which it did, is what converts "the auditor agreed" into evidence about the auditor. The default arm, where the cap never bound and nobody lost on rank, is retained in this paper precisely because it is the arm that would otherwise have made A2 look stronger than it was.

The second finding concerns **how a reconstruction record can mislead**. The engine's support and competing-flow fields are structurally similar and semantically different; a record that says "4 contradictory observations" where the quantity is the subject's competing flow is a small textual error with a large interpretive cost, and it is invisible to any check that verifies only that a field is present and numeric. This is why A5 is an acceptance criterion with its own failure test rather than a review note.

The third finding concerns **the boundary of the substrate**. The window's span in cycles is not a constant of the architecture; it is a ratio between a fixed event budget and a storage rate that depends on the system's own output volume. Here it is 1.7 cycles, and it is measured, because the alternative is to assert a retention horizon that the system does not have.

## 6. Limitations

These probes test a defined observer, a defined implementation (SQLite), a defined world generator, a defined retention policy, and a defined set of engine states. Specifically:

- They do **not** establish all-history reconstruction. The window bounds the record at 1.7 cycles (§4.4).
- They do **not** establish causal explanation or causal sufficiency. A faithful trace does not show that a recorded parent caused a structure to be useful or correct.
- They do **not** establish independent replication by another laboratory. The observer shares the substrate with the engine; "independent" here means independent reconstruction from the engine's state, never independent replication (§2).
- They do **not** establish the usefulness, correctness or quality of the reconstructed structures. Reconstruction fidelity and utility are separate properties.
- The observer-window match is empirical for the tested implementation. Under the forced-tie arm the **implementation** is deterministic for identical queries over identical data, so the observer's re-run selects the same rows; the **schema** still does not determine the window under a tie, and a replayer that did not observe at store time could not rely on it.
- The self-sourced rate is a measured support-composition statistic, not evidence that self-sourcing causes errors; transfer claims must use the pre-committed per-claim rule.
- All measurements come from a single seed per arm. The claim is about the instrument's exactness on tested states, not about a distribution over worlds.
- The 17.9 % reference rate is a provisional calibration value from one world, one policy and one run.

## 7. Conclusion

The present evidence supports a narrow result: tested surviving Organica structures and claims can be reconstructed from engine state with exact measured linkage in the audited probes. A5/A6 are closed (2026-10-28) and the instrumentation is tagged and frozen at `audit-trace-v1`; the bounded wording above remains a prerequisite to a submission.

What remains for submission is assembly rather than acceptance: the methods and results sections above must be reconciled against the committed artifacts one final time, the citations in §2 must be supplied, and the figures must be generated from the same artifacts. None of those steps may widen a claim.

## Data and code availability

All measurements, protocols and artifacts are public in the repository at [`nueraresearch/project-organica`](https://github.com/nueraresearch/project-organica) (branch `master`). The engine is frozen at tag `v0.9.0`; the audit instrumentation is frozen at tag `audit-trace-v1`. Probe outputs are committed as `docs/audit_trace_probe.json`, `docs/audit_trace_probe_stress.json` and `docs/audit_trace_probe_tie.json`. The full specification, including the two disclosed defects (D1, the competing-flow misreading, and D2, the unfiltered lookback window) and their consequences, is in [`docs/AUDIT-TRACE-SPEC.md`](../docs/AUDIT-TRACE-SPEC.md); the measured consequence of D2 is quantified separately in [`docs/GATE13-RELATION-SEPARATION.md`](../docs/GATE13-RELATION-SEPARATION.md).

## Repository evidence

- [`docs/AUDIT-TRACE-SPEC.md`](../docs/AUDIT-TRACE-SPEC.md) — the specification, the acceptance criteria, the disclosed defects, and the measurement
- [`docs/audit_trace_probe.json`](../docs/audit_trace_probe.json), [`docs/audit_trace_probe_stress.json`](../docs/audit_trace_probe_stress.json), [`docs/audit_trace_probe_tie.json`](../docs/audit_trace_probe_tie.json) — the three arms
- [`benchmarks/audit_trace_probe.py`](../benchmarks/audit_trace_probe.py) — the observer
- [`tests/test_audit_trace_probe.py`](../tests/test_audit_trace_probe.py), [`tests/test_audit_ancestry.py`](../tests/test_audit_ancestry.py) — the proof-of-firing tests
- [`docs/USER-MANUAL.md`](../docs/USER-MANUAL.md) §2, §8.17, §8.19 — the project's own record of the same work
- [`research-journal/phase_g_findings_20261021.md`](../research-journal/phase_g_findings_20261021.md) — journal §41–§48, §53
