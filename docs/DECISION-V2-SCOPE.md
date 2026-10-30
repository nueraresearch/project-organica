# Decision — What “No V2” Binds, and What the Freeze Leaves Free

**Date:** 2026-10-30
**Status:** DECIDED — a scope decision and a bounded diagnostic authorization, not an amendment to the acquisition preregistration
**Scope:** the Phase K terminal outcome, the Organica 1 freeze, and one Gate 13 diagnostic
**Amends:** no preregistration, verdict, frozen engine file, or published result artifact.

## 1. The question

Two committed statements can be read as if both govern every engine-adjacent action:

- **H2** (Phase K, pre-committed): no task family was supported; the search failed and **V2 must not be designed**.
- **The Gate 13 causal account:** capacity and provenance each affect asserted coverage, while relation-family separation and a ranking not based on raw frequency remain unresolved design requirements.

They answer different questions. H2 closes the search for a task family on which Organica 1 has demonstrated comparative advantage. The Gate 13 work diagnoses why the frozen engine failed to assert the required structure on the compositional task. The record should preserve both conclusions without treating the diagnosis as permission to redesign the architecture.

## 2. The decision

**D1 — H2 stands and binds V2 design.** No V2 architecture is designed, no frozen engine behavior is changed, and no capability, acquisition, transfer, or comparative-advantage claim follows from the Gate 13 diagnostics.

**D2 — H2 does not bind one diagnostic arm.** A single experiment, **G13-D**, is authorized to measure how much of the Gate 13 failure survives when the two confounds it can remove without designing anything — **capacity** and **provenance** — are removed together, with the readout held at its calibrated value. It measures the frozen engine's failure mode. It is not a successor architecture and may not be described as one.

The Organica scoring readout is **held fixed** at the already calibrated `alpha = 256.0` (calibration seed `20261099`). It is a constant across both arms, not an intervention, and must not be retuned on the diagnostic seeds. It is also the last entry of `ALPHAS_ORGANICA`, so G13-D locks this boundary value rather than extending the sweep. This combined condition has not yet been measured; the separate capacity and provenance probes do not establish its outcome.

## 3. G13-D — bounded diagnostic scope

Permitted, and nothing beyond it:

1. **In-process subclass only.** No edit to `organica/sleep.py`, `memory.py`, `paths.py`, `streams.py`, `branch_streams.py`, `scale_streams.py`, or `ground_truth_worlds.py`. `tests/test_v1_freeze.py` must stay green.
2. **Two declared interventions, plus one fixed constant.**
   - **Capacity:** `MAX_PREDICTIONS` raised to 1,000 in-process (the condition `docs/V2-CAPACITY-DESIGN-BRIEF.md` already sanctions as diagnostic).
   - **Provenance:** `_record_temporal_edges` overridden so its lookback selects world events only, removing the sleep-sourced `tag_from` rows that D2 discloses. This is a method boundary, not an engine edit.
   - **Held fixed, not varied:** the readout's smoothing constant is `alpha = 256.0`, already calibrated on `20261099`. It is a constant across both arms and is **not** an intervention; no retuning is permitted inside the arm. It is the last entry of `ALPHAS_ORGANICA`, so it is a boundary value — the arm locks it rather than extends it.
3. **Seeds `20261101`–`20261105` only.** No confirmatory seed is touched. Use the existing 10-cell runner's scoring functions and baseline definitions through a small G13-D adapter; the runner itself does not currently expose both interventions and cannot be invoked unchanged.
4. **Scored end-to-end** on the retention, transfer-diagnostic and revision windows against the fixed, independently calibrated baseline configurations — not against Gate 13 coverage. Do not tune on the five diagnostic seeds.
5. **Reported as `diagnostic`**, naming both interventions and the fixed alpha, the inspected seeds, and that both overrides run only in the in-process diagnostic subclass; no frozen engine file is edited.

The current `benchmarks/acquisition_runner.py` implements the 10-cell pilot, but it does **not** expose both interventions as configurable hooks. G13-D therefore requires a small adapter that reuses its scoring functions, calibrated baselines, and scratch-database safeguards. The adapter and its exact paired comparison must be reviewed and recorded before execution. This is harness work only, not an architecture change.

**Out of scope:** relation-family separation, source-level quotas, alternative ranking rules, candidate-quality optimization, engine edits, protocol threshold changes, tuning on these five seeds, confirmatory runs, or extending the diagnostic beyond five seeds and one report.

## 4. Interpretation and stop conditions

G13-D cannot establish acquisition, transfer, general intelligence, or comparative advantage. Its purpose is narrower: determine whether the combined cap and provenance condition changes the previously observed failure and how the existing prediction readout scores under that condition. Even a favorable diagnostic result authorizes a question for the owner, not a V2 build or confirmatory campaign.

Do not run G13-D until its adapter and paired conditions are specified in a separate, dated diagnostic plan. That plan is **not an amendment** to the closed acquisition preregistration; it must explicitly leave that preregistration, its Gate 13 threshold, Task 2 stopped verdict, and all confirmatory seed assignments unchanged. Stop after one report. Any broader work requires a new recorded owner decision.

## 5. What the freeze still binds

**Binds:** the seven engine files and published result artifacts specified by `docs/V1-FREEZE.md`; the Phase A cognitive primitives; the design laws; the frozen protocols and their verdicts, including Phase K H2 and the Task 2 acquisition-gate stop; and `v0.9.0` as the archival reference.

**Does not bind:** benchmark and harness code, documentation, the action list, or owner decisions, provided they do not change frozen-engine behavior or rewrite a committed result.

**Untouched:** package version `0.10.0` remains untagged; Generation 9 remains locked; the live study remains paused at 5,396 cycles.

## 6. Decision record

| ID | Date | Decision | Authority | Rationale |
|---|---|---|---|---|
| D1 | 2026-10-30 | Phase K H2 continues to prohibit V2 design | Phase K preregistration §7 and its fired outcome | No task family was supported; the Gate 13 diagnosis does not reverse that result. |
| D2 | 2026-10-30 | One five-seed diagnostic, G13-D, is authorized within the limits above | Owner direction recorded here | The combined cap and provenance condition is still unmeasured; measuring it does not require designing a successor architecture. |
