# Paper 2: Reconstructing Evidence and Selection from Organica’s Surviving State

**Authors:** Jeremy et al. (Nuera Research)  
**Draft status:** Evidence-alignment revision, 2026-10-27; A5/A6 closed and the audit layer frozen at `audit-trace-v1` on 2026-10-28. Not submitted or published.  
**Scope:** Reconstruction fidelity for tested probes and surviving current structures.

## Abstract

Developmental systems can expose a record of how their current structures were formed, but a reconstruction claim must specify what the record can recover and under which conditions. We report the Organica audit-trace probes as bounded reconstruction tests, not as proof of universal explainability or complete historical memory. In the measured A3 runs, all 8,061 of 8,061 structures resolved to Layer 1 within the configured depth, and all 1,412 of 1,412 claims resolved to event identifiers with a world/self evidence split. The forced-tie and stress probes also retained structure-level reachability, while branch-level accounting recorded aged-out ancestors. These results support exact reconstruction of the tested surviving state under the tested SQLite implementation. They do not recover ancestry that the engine itself no longer retains, establish causal sufficiency, or constitute independent replication by another laboratory. A5 field honesty and A6 separation of trace from counterfactual remain pending; the audit instrumentation is not yet frozen.

## 1. Claim under test

The claim is that an external observer can reconstruct specified evidence and selection decisions from Organica’s stored state and report, without asking the organism to narrate its own reasoning. “Independent” means independent reconstruction from the engine’s state; it does not mean an independent laboratory has replicated the result.

The trace has two distinct graphs. Candidate ancestry links structures back to Layer 1. Evidence linkage connects claims to supporting transitions and event identifiers. Candidate ancestry does not terminate at raw events, and evidence linkage is not a candidate-parent chain.

## 2. Probe results

A3 measured lineage reachability of 1.000 (8,061/8,061 structures) and evidence linkage of 1.000 (1,412/1,412 claims). The structure-level truncation split was empty, while branch-level accounting recorded 105 aged-out branches; these statements are compatible because each structure resolved through at least one surviving branch. The same structure-level result was reported for stress and forced-tie probes. The window and depth sweeps showed that truncation branches were reachable and that the configured depth limit was not binding in the measured default case.

The trace is bounded by the organism’s effective memory. It reconstructs what the organism currently retains; it cannot recover a developmental history that has disappeared from the organism’s state. Fidelity is not causal sufficiency: a faithful trace does not by itself show that a recorded parent caused a structure to be useful or correct.

See [`docs/AUDIT-TRACE-SPEC.md`](../docs/AUDIT-TRACE-SPEC.md), [`docs/audit_trace_probe.json`](../docs/audit_trace_probe.json), [`docs/audit_trace_probe_stress.json`](../docs/audit_trace_probe_stress.json), and [`docs/audit_trace_probe_tie.json`](../docs/audit_trace_probe_tie.json).

## 3. Remaining acceptance work

A5 must establish that every reported numeric field has exact semantics and is rendered without mislabelling. A6 must keep observed trace records separate from counterfactual replay. Until both close and the prescribed probes regenerate, the instrumentation is not ready to be tagged and frozen. The paper’s final methods and results should be updated from those artifacts after closure, without widening the claims.

## 4. Limitations

These probes test a defined observer, implementation, database behavior, and set of engine states. They do not establish all-history reconstruction, causal explanation, usefulness of the reconstructed structures, or general auditability of other systems. The observer-window match is empirical for the tested implementation. The reported self-sourcing rate is a measured support-composition statistic, not evidence that self-sourcing causes errors; transfer claims must use the preregistered per-claim rule.

## Conclusion

The present evidence supports a narrow result: tested surviving Organica structures and claims can be reconstructed from engine state with exact measured linkage in the audited probes. A5/A6 are now closed (2026-10-28) and the instrumentation is tagged and frozen at `audit-trace-v1`; the bounded wording above remains a prerequisite to a submission.
