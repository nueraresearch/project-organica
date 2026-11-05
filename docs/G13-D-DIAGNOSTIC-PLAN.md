# G13-D — diagnostic plan

**Date:** 2026-11-02
**Status:** plan committed **before** execution. It authorizes exactly one run of
five seeds and one report, under `docs/DECISION-V2-SCOPE.md` D2.
**Not an amendment.** This plan does not touch the closed acquisition
preregistration, its Gate 13 threshold, the Task 2 stopped verdict, or any
confirmatory seed assignment.

Related: `docs/DECISION-V2-SCOPE.md` (the authorization), `docs/V2-CAPACITY-DESIGN-BRIEF.md`
(the capacity condition and the world-only separation),
`docs/GATE13-RELATION-SEPARATION.md` (the measured 35.7 %–40.7 % of relation rows the
separation removes), `benchmarks/acquisition_runner.py` (scoring functions and
calibrated baselines reused here), `benchmarks/g13d_diagnostic.py` (the adapter).

## 1. Question

How much of the Gate 13 failure survives when the two confounds that can be removed
without designing anything — **capacity** and **provenance** — are removed
together, with the prediction readout held at its calibrated value?

This is a diagnostic of the frozen engine's failure mode. It is not a successor
architecture, and it may not be described as one.

## 2. The two interventions, and the one fixed constant

| element | value | kind |
|---|---|---|
| capacity | `MAX_PREDICTIONS = 1,000` on the diagnostic `SleepService` subclass | intervention |
| provenance | `_record_temporal_edges` overridden so its lookback selects `event_type != 'sleep'` rows | intervention |
| readout smoothing | `alpha = 256.0` | **fixed constant**, not an intervention |

`alpha` was calibrated on seed `20261099`, is a constant across both arms, and is
the last entry of `ALPHAS_ORGANICA`. It is not retuned on the diagnostic seeds. A
different alpha would be a different arm and is out of scope.

Both overrides live in process. No frozen engine file is edited, and
`tests/test_v1_freeze.py` must stay green.

## 3. Arms and the exact paired comparison

Per seed, the same world and the same event stream are run twice:

- **baseline** — the frozen engine unchanged: cap 20, unfiltered lookback.
- **g13d** — cap 1,000 and the world-only lookback.

Everything else is identical: the same `generate_compositional_world(seed)`, the
same `trainable` mask, the same exposure stream, the same cycle schedule, the same
scratch-database path pattern, and the same fitted-in-process readout.

**Paired statistic:** `delta = log_loss(g13d) − log_loss(baseline)` for each
window and metric shape. Negative means the combined intervention scored better.
Reported per seed and pooled across the five, with the five deltas visible — never
as a single averaged number alone.

## 4. Seeds

`20261101`–`20261105`, and no other seed. No confirmatory seed is read, and no
calibration cell of the closed study is re-scored. The seeds are not used to tune
anything: there is no grid, no selection and no re-run on this set.

## 5. Windows, shapes and baselines

- **Windows:** retention (cycles 110–149), transfer-diagnostic (150–199), revision
  (250–299 after learning 200–249), exactly as `acquisition_runner` defines them.
- **Shapes:** house shape (`exclude_self=True`, primary) and self-cells shape
  (`exclude_self=False`, co-primary). Both are reported.
- **Baselines:** the calibrated replay learner (`window=1, half_life=None,
  alpha=0.5`), the calibrated cell counter (`alpha=0.1`), the Bayes ceiling and the
  base rate, all reused unchanged from `acquisition_runner`. They are reported
  beside both arms so the diagnostic can be read against the same reference the
  closed study used.

## 6. Intervention verification (before any score is read)

A perturbation that did not occur is not a null result.

- **P1 provenance.** After acquisition, count `precedes` rows whose `tag_from` never
  occurs in a world event. The baseline arm must have more than zero; the g13d arm
  must have zero. If the filter did not bite, the run aborts.
- **P2 capacity.** Record the largest frozen-candidate count each arm reached. If
  the g13d arm never exceeded 20, the cap did not bind and that is reported as
  `cap_binding: false` — a diagnostic fact, not a failure.
- **P3 freeze.** `git diff --stat -- organica/` must be empty.

## 7. Reporting

- One artifact, `docs/g13d_diagnostic.json`, labelled `kind: g13d_diagnostic`,
  `status: diagnostic`, naming both interventions, the fixed alpha, the seeds, and
  stating `authorises_confirmatory: false` and `no_verdict: true`.
- One report, `docs/G13D-DIAGNOSTIC.md`, rendered from that artifact rather than
  typed.
- The report says what the numbers are and are not: they describe how the frozen
  engine scores under the combined condition on five diagnostic seeds.

## 8. Stop rules

- **One run, one report.** No re-run on these seeds, no seed added, dropped or
  re-drawn, no parameter changed after a number is seen.
- If P1 fails, the diagnostic is void and is reported as void; it is not
  reinterpreted.
- No threshold is created here. Gate 13's threshold and the Task 2 verdict are
  unchanged, and this plan creates no new criterion for any future study.
- After the report, this thread stops. Broader work requires a new recorded owner
  decision.

## 9. What G13-D cannot establish

Acquisition, transfer, general intelligence, or comparative advantage. It cannot
establish that the combined condition is sufficient, because it varies two
confounds and leaves relation-family separation and frequency-based ranking
unresolved. A favorable result authorizes a question for the owner, not a V2 build
and not a confirmatory campaign; an unfavorable result does not by itself
establish that either intervention is irrelevant.

## 10. Post-run amendment (2026-11-02, same day, after the run, before interpretation)

P2 as built counted prior candidates of **all types** — 3,998 in both arms — so it could
not show that the prediction cap bound. The committed artifact records the capacity check
as **not measured**, not as passed. Scores were not recomputed and no second run was made.
What remains verified about capacity is structural: `organica/sleep.py:1160` truncates to
`self.MAX_PREDICTIONS`, and the diagnostic subclass sets that constant to 1,000 against a
baseline of 20. The paired result therefore describes the **combined** condition and is not
decomposed into a capacity effect and a provenance effect. This note changes no threshold,
no seed and no number; it corrects a check that claimed more than it measured.
The per-seed artifact entries, the caches and the aggregation path were normalised on
the same day; regeneration from cache reproduces the same scores with the check
recorded as not measured at every level.
