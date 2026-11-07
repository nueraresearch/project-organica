# Decision: diversity-first admission, adopted then withdrawn

**Date:** 2026-11-07
**Status:** **WITHDRAWN (2026-11-07).** The rule was adopted on this evidence and withdrawn the
same day, when the two-arm comparison in `docs/ADMISSION-TWO-ARM-PREREGISTRATION.md` closed its
layer (§6). The adopted module and its test were removed, and the reference engine is again the
only admission path (§7).
**Scope:** the admission rule — which eligible candidates occupy a budget slot. Not extraction,
not the confidence formula, not the death and stability thresholds, not the caps.

## 1. What licensed this

The confirmatory block registered in `docs/RANKING-ADMISSION-PREREGISTRATION.md` ran on its
pre-registered 160 cells after that file was committed, and the frozen analysis path returned
**ADOPT THE ADMISSION RULE**: every gate passed, the adoption conjunction was met whole (mean
coverage gain clear of the calibrated bar, interval lower bound clear of zero, all eight seeds
positive), and the dense-end guard passed. The numbers are in
`docs/ranking_admission_result.json` and the cells in `docs/ranking_admission_run.json`.

The change was specified before the run in `docs/RANKING-ADMISSION-DESIGN.md`, which also named
what the verdict would and would not license. This record is the decision that document said
adoption would require; it adds no evidence and re-scores nothing.

## 2. The decision

**D1 — Diversity-first admission replaces count-ranked admission.** Each slot takes the eligible
candidate whose left-hand tag owns the fewest already-admitted outgoing edges; ties break on
count, then on the stable key. The rule changes *which eligible candidate occupies a slot*.
Eligibility, candidate construction, strength, the ``PREDICTION_MIN_COUNT`` filter and the caps
are unchanged.

**D2 — The budget rule is a floor, not an increase.** Under the adopted rule the cap is
`max(cap, number of eligible source tags)`, because below the source count the diversity order
has at most one slot per source and degenerates toward count order. At the engine's own caps
(`MAX_PREDICTIONS = 40`) the floor is inert in a 16-source world, which is what the confirmatory
block relied on: **the adoption raises no cap.** The floor only binds where a caller sets a cap
below the source count, and there it is a validity condition rather than a gain.

## 3. The implementation vehicle

> *Removed at withdrawal (§7). This section records what was built and why that shape was
> chosen; the module and its test no longer exist.*

`organica/sleep.py` is frozen. Its own code says how a change of this kind is made: *the cap is
changed by subclassing — the frozen file is never edited* (`benchmarks/acquisition_harness.py`,
`_CapOverrideSleepService`). The adopted rule follows that instrument exactly:

- **`organica/admission.py`** — new module, additive and importable on its own. It holds the two
  orderings (`count`, which is the reference engine's rule, and `diversity`, which is adopted),
  the budget floor, and `DiversityFirstSleepService`, a `SleepService` subclass that overrides
  `_build_predictions` and nothing else.
- **`organica/sleep.py` is not edited.** Neither is any other frozen file. The archival `v0.9.0`
  tag remains the reference for what Organica 1 was, and `0.12.0` remains immutable.
- **The reference class keeps the reference rule.** `SleepService` still admits by count, so every
  published Gate 13 figure and every archived measurement remains reproducible from the code that
  produced it. Code that runs the adopted engine uses `DiversityFirstSleepService`.
- **`COUNT` is the control ordering, not the engine's ordering.** It is retained
  because it is what the confirmatory block compared against, and because the adopted
  service's `COUNT` arm delegates to the engine and returns its admission unchanged.
- **The override delegates under the reference policy.** With `admission_policy = COUNT` the
  adopted service calls the engine's own builder and returns its admission unchanged; only the
  adopted policy takes the other path, so nothing about the reference behaviour is
  re-implemented here.

## 4. What the frozen boundary now means

The boundary rule is unchanged: **nothing changes the behavior of the frozen engine.** What was
adopted is a *new* admission path that an engine version may use, not a modification of the
frozen one. Three properties make that checkable rather than asserted:

1. The `count` arm of `organica/admission.py` must reproduce `SleepService._build_predictions`
   exactly — same candidates, same order, same truncation — on the same inputs. If it drifts, the
   claim that only the ordering changed is false, and `tests/test_admission_rule.py` fails.
2. The `diversity` arm must produce a *different* admission on a crowded fixture, so the
   manipulation can be seen to occur. Identical admissions would be an unrun experiment.
3. `git diff` over the frozen engine files must be empty, checked mechanically rather than by
   reading, and the freeze record carries an amendment that says so.

## 5. What is disclosed rather than smoothed over

- **Coverage is not behaviour.** The confirmatory block measured which world edges a selection
  surfaces, at one cap, one world family and eight seeds. Nothing here shows that surfacing more
  world edges improves prediction, revision or retention, and the bottleneck map's selection row
  keeps its "effect on behavior untested" half.
- **The engine's ordering is not the control the experiment ran.** The confirmatory block's
  control was a count-ranked top-k over a pooled edge table. `SleepService._build_predictions`
  orders by transition probability inside a stratified transition/co-occurrence quota, with a
  schema prior; measured on a crowded fixture it already spreads across sources. So the measured
  gain belongs to *count-ranked* admission, and applying the adopted order to the engine's pool is
  a rule adoption whose coverage consequence on this layer is **untested**. A run through the
  adopted service must name its arm and may not cite the confirmatory figure as its own.
- **The adopted policy supersedes the engine's stratified quota.** The engine splits the
  prediction budget between transitions and co-occurrences. A diversity order over sources
  cannot be expressed inside that split, so under the adopted policy the ranking is over the
  eligible pool and the split is not applied. This is a consequence of the change rather than
  a second change, and it is why a run must name its arm.
- **A future Gate 13 run through the adopted service will differ from the published figure.** Any
  such run must say which arm it ran. Published figures are count-basis and are not re-scored.

## 6. The measured outcome (2026-11-07)

The two-arm comparison registered in `docs/ADMISSION-TWO-ARM-PREREGISTRATION.md` ran after that
file was committed. All gates passed and the frozen analysis path returned **NO GAIN ON THIS
LAYER**: mean paired coverage gain **-0.077009**, 95% interval **[-0.099331, -0.056920]**, width
0.042411 against a bar of 0.08, **0 of 8** seeds positive, and the precision guard also failed at
**-0.096528**. The figures are in `docs/admission_two_arm_result.json`, the cells that produced
them in `docs/admission_two_arm_run.json`.

**What this means, in the decision table's own words:** the adopted rule does not cover more of
the world here. The gain the confirmatory block measured belongs to count-ranked admission on the
pooled-edge instrument, and it **does not transfer** to the engine's prediction layer. This layer
is closed to this rule.

**What was not done to the result.** No criterion was re-read, no bar recomputed, no seed dropped.
The block is negative on its own pre-registered terms: the effect is negative on every seed, with
an interval that excludes zero and a width far below the underpowered threshold, so this is a
measured loss and not an absence of evidence.

**What followed for the code.** When the block closed, `organica/admission.py` and
`DiversityFirstSleepService` stood as implemented and as the *non-default* policy; nothing in the
engine used them by default and no document was to present them as a gain. Whether to withdraw
the adoption outright was an owner decision left pending at that point, and it was taken in §7
below.

**What survives.** The methodological result survives: the same rule that gains on a pooled edge
table loses on the engine's own ordering, which is exactly why the layer had to be measured. The
confirmatory block's verdict is untouched and remains scoped to its instrument.

## 7. The withdrawal (2026-11-07)

**Status: WITHDRAWN.** The adoption was reversed on the day it was made, on the measurement in
§6. This section is the decision; it adds no evidence and re-scores nothing. Every present-tense
statement about the module elsewhere in this record describes the period before this section.

**Removed, not marked.** Withdrawal is the removal of the code, so the package no longer offers
the rule at all:

- **`organica/admission.py`** — deleted, with the rule, the budget floor and the subclass.
- **`tests/test_admission_rule.py`** — deleted. Its subject no longer exists, so the reproduction
  claim it carried is now discharged by the commit named below rather than by a live test.
- **`benchmarks/run_admission_two_arm.py`** — no longer imports the adopted service. The arms are
  resolved lazily, and asking for the adopted arm stops with a message naming the commit that
  still contains it instead of raising an `ImportError`.

**The reference engine is the only admission path again.** `SleepService._build_predictions` is
the one ordering an engine version can reach, so the state before Amendment 2 is restored and
there is no non-default arm left to maintain, to document, or to mistake for a gain.
`organica/sleep.py` was not edited at any point, before or after the adoption, which is what makes
the restoration a removal rather than a second change.

**What is not withdrawn.** The negative result stands exactly as the frozen analysis returned it:
its numbers are in §6 and its artifacts are untouched. The withdrawal is not a re-reading of it
and does not soften it. The confirmatory block's `ADOPT THE ADMISSION RULE` verdict also stands,
and remains scoped to its own instrument — a pooled edge table with a count-ranked control — which
is the instrument it was registered on.

**Reproducibility.** The adopted arm was last present at commit **`a82e890`**. Checking that
commit out reproduces this block end to end, which is why the runner names it rather than letting
the arm look as though it was never built.

**Not a finding about the rule in general.** The withdrawal closes the admission question on the
engine's prediction layer, in one world family and at one horizon. It does not establish that
diversity-first ordering is wrong anywhere else, and the pooled-table gain is neither retracted
nor revived.

## 8. Stop condition

This record is closed on 2026-11-07: **adopted, measured, withdrawn.** It may be fixed if it is
found wrong; it may not grow, and **no admission variant may be added here.**
