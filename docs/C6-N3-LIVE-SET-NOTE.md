# Methods note — N3 and the report-derived observer

**Status: methods note, not a result. 2026-11-13.**

This note records one instrument failure from the C6 preflight and the rule it
implies. It is not evidence for carrier causation, readout, or order.

## The observation

On seed **20611601**, **120** cycles and cap **40**, the report-only observer’s
last `SleepReport` contained **101** readout edges. The live candidate set
contained **196**. The missing **95** were carried survivors that were not
re-emitted in the final cycle. `N3_parity` failed: the report view was not a
faithful reconstruction of the state from which final assertion is computed.

The failure was not a crash or a changed engine output. It was a mismatch
between two views of the same cycle.

## Why the report is not the live set

`SleepReport` is this cycle’s emitted candidate report. A carried candidate can
remain live in the candidate store and still enter the final assertion without
being emitted again in the last report. The report is therefore a
**post-selection, per-cycle summary**, not the full set of candidates available
to the engine.

For C6, that distinction is decisive. The timing question is not “when did an
edge appear in the report?” It is “when did the engine first make this edge
available as `K` or `Y_ind`?” A report that omits a live survivor cannot answer
the second question.

## Why this is unsafe for timing claims

Four failures follow from using the report as the observer’s state.

1. **Absence becomes ambiguous.** A missing edge can mean “not live” or “live but
   not re-emitted.” C6 reads absence as a timing fact, so the two cases cannot be
   conflated.
2. **The sample is conditioned on reporting.** Edges that are emitted repeatedly
   and edges that persist without re-emission are not a random subset. The 95
   missing survivors were systematically the carried population, so the loss can
   shift `K_BEFORE_Y_IND`, `Y_IND_BEFORE_K`, `SAME_CYCLE`, `NO_K` and `NO_Y_IND`
   rather than merely reduce the denominator.
3. **A neutral observer can still be unfaithful.** `N1_neutrality` tests whether
   observation changes the engine. It does not test whether the observer sees the
   engine’s state completely. A passive report-only observer can pass `N1` and
   fail `N3`; neutrality and reconstruction fidelity are separate requirements.
4. **Timing is a time series, not a final cross-section.** Reconstructing first
   appearance from reports risks reverse-time imputation and makes a later
   reappearance look like a first appearance. C6 explicitly forbids that.

`N3` is therefore not a redundant parity check. It is the gate that makes a
live-set readout admissible for timing at all.

## Repair

The observer now snapshots `_load_prior_candidates()` after the parent cycle.
That is the same live set the final readout uses. The snapshot is read-only, does
not populate `_prior_cache`, and the parent cycle is called once with its return
value passed through unchanged.

`N3` compares the live-set `Y_full` with
`structure_edges(_load_prior_candidates())` at the final cycle. A mismatch voids
C6; it is not reported as a null timing result.

The repaired observer passed `N1` and `N3` in the preflight; the harness
self-test passes `N1`–`N3`, and `N3` passes on all six seeds of the six-seed
block. See
[`C6-ASSERTION-TIMING-INSTRUMENTATION.md`](C6-ASSERTION-TIMING-INSTRUMENTATION.md),
[`C6-ONE-SEED-PREFLIGHT.md`](C6-ONE-SEED-PREFLIGHT.md) and
[`C6-TIMING-BLOCK.md`](C6-TIMING-BLOCK.md).

## Scope

This note explains an instrument defect on one preflight seed. It does not
establish C6, select a mechanism, or license a causal reading of the later block.
The block’s own scope limits still apply.
