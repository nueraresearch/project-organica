# Phase K mechanism attribution — correction record

**Status:** `CORRECTION DOCUMENTED; FROZEN RESULT ARTIFACT UNCHANGED`

**Date:** 2026-11-16

**Scope:** the `mechanism_implicated` field in
[`docs/phase_k_results.json`](phase_k_results.json). This record changes no
mean, interval, verdict, seed or frozen artifact.

## What was wrong

The Phase K harness computed:

```python
mechanism_implicated = ci_abl[0] <= 0
```

where `ci_abl` is the 98.33% interval for **Organica minus the matched
ablation**. A mechanism is implicated when Organica beats the ablation by an
interval wholly above zero. The old predicate instead marked the mechanism
implicated whenever the lower bound was at or below zero, including a null
interval.

The frozen artifact therefore stores `true` for all three families:

| Family | Stored `mechanism_implicated` | Correct reading | Organica − ablation interval |
|---|---|---|---|
| K1 | `true` | `false` | `[-0.03285, 0.014039]` |
| K2 | `true` | `false` | `[-0.004777, 0.049519]` |
| K3 | `true` | `false` | `[0.0, 0.0]` |

All three intervals contain zero. The result prose in
[`docs/phase_k_results.md` §4.1](phase_k_results.md) already describes this as
a **negative attribution**: the matched mechanisms are not load-bearing for
these tasks. The prose and intervals are correct; only the stored field was
inverted.

## What is unaffected

- The K1, K2 and K3 means, intervals and `REVERSED` verdicts are unchanged.
- The K2 result remains a clean negative result, not a capability win.
- The frozen artifact has **not** been edited, and it must not be edited in
  place. Its historical `true` values document the defect, not a scientific
  finding.
- The campaign was not rerun, so this is a code and documentation correction,
  not a re-score.

## What was changed

- [`benchmarks/phase_k_campaign.py`](../benchmarks/phase_k_campaign.py) now
  requires the paired interval to lie wholly above zero before setting
  `mechanism_implicated`.
- [`tests/test_phase_k_campaign.py`](../tests/test_phase_k_campaign.py) adds
  regression tests for all three interval shapes: a positive interval must
  produce `mechanism_implicated: true`; a null interval
  (`Organica == ablation` on every seed) and an interval that crosses zero
  must both produce `mechanism_implicated: false`.
- This correction record is linked from the Phase K results page. Future
  results are expected to carry the corrected field; the frozen artifact keeps
  its historical values under the freeze policy.

## How to read the frozen artifact

For `docs/phase_k_results.json`, read
`summaries.<family>.matched_ablation.paired_organica_minus_ablation` and its
interval. Treat the stored `mechanism_implicated` field as a historical
artifact defect until a new, explicitly versioned result is produced. The
negative-attribution reading in the results page and the facts sheet is the
correct one.
