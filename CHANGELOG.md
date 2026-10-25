# Changelog

All notable changes to Project Organica are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning 2.0.0](https://semver.org/).

## Versioning in this repository — three separate namespaces

The words "v1" and "v2" appear in this project in three different senses.
They are deliberately distinct, and they are what the version number
*does not* refer to.

| Namespace | Form | Meaning | Current |
|---|---|---|---|
| **Package version** | `0.x.y` (SemVer 2) | the released, installable, citable artifact | **0.9.0** (unreleased) · 0.8.0 is the latest tag |
| **Architecture generation** | *Organica 1*, *Organica 2* | a generation of the eight-layer engine. Organica 1 is frozen; Organica 2 is planned | **Organica 1** |
| **Research campaign** | *Ablation Study 1*, *Ablation Study 2* | the experimental series. Study 1 is the eleven-condition ablation; Study 2 is the six-colony Tier-1 matrix | **Study 2 in flight** |

The package version is **pre-1.0**, which is the honest state: the public
API is not declared stable, and the MINOR/PATCH numbers carry the
meaning instead. `tests/test_versioning.py` asserts that the three
declarations — `organica.__version__`, `pyproject.toml` and `CITATION.cff`
— never drift apart, and that the version describes *this* commit: if a
tag for the version exists, it must point here. A version whose changelog
entry is marked `(unreleased)` is allowed to have no tag yet, because
there is nothing to check out.

---

## [0.9.0] — 2026-10-24 (unreleased)

**The project question changed: from *can we make a developmental
architecture?* to *what class of problems benefits from one?* Phase K opens
the search for that task.**

### The reasoning

Phases H, I and J were three preregistered attempts to show an external
advantage and all three were negative. That is not the same statement as
*V1 failed*:

> V1 develops interesting internal structure. We do not yet know what
> problem that structure solves.

Three tasks were negative; an infinite number of tasks were not tested. So
**no V2** — the design of a successor architecture cannot be justified while
the advantage it would provide is unknown. Designing V2 first would make V2
guesswork.

### Added — Phase K: Comparative Advantage Search

A **search**, not a test. The question is *what is Organica uniquely good
at?* Three candidate task families, each derived from a mechanism the
project has actually measured, each scored against the strongest simple
baseline that could plausibly solve it.

| Family | Mechanism it targets | The baseline that could beat it |
|---|---|---|
| **K1 — Incremental world modeling** | question generation drives novelty assimilation | online co-occurrence, which won Phase H at 0.8000 vs 0.7041 |
| **K2 — Belief revision** | falsification and contradiction drive revision | change-point detection plus wholesale relearning, with a forgetting window |
| **K3 — Longitudinal knowledge integration** | dreams integrate beliefs into coherent structure (P4, SUPPORTED) | sliding-window co-occurrence, which must trade retention against acquisition |

The protocol is frozen in [`docs/PHASE-K-PREREGISTRATION.md`](docs/PHASE-K-PREREGISTRATION.md)
and was committed **before any Phase K outcome was generated**. Three things
in it keep the phase honest:

1. **The baselines get the tuning advantage.** Every simple baseline is swept
   over a declared grid and its *best* score is the number used. A strawman
   baseline is the most likely way to manufacture a false positive, and it is
   impossible by construction.
2. **The harness is validated before the campaign runs.** The Phase H
   held-out task is rerun through the same code, where Organica's loss is
   already known (0.412605 vs 0.504039). If the harness reports a win
   there, the campaign does not run.
3. **"No family confirmed" is a pre-committed terminal outcome.** Three more
   families ruled out is a publishable result, and it does not authorise a
   V2.

Decision rule: paired percentile bootstrap over ten seeds, **98.33%**
interval (Bonferroni across the three families), SUPPORTED only when the
interval for Organica − best simple baseline lies wholly above zero.
Attribution — whether the hypothesised mechanism is actually implicated — is
reported from a matched within-architecture ablation and is kept separate
from the success criterion.

**The pilot, disclosed.** The harness was run once at one seed and one tenth
of every cycle count before the protocol was frozen. Organica was behind the
baseline in all three families. That is one seed at ten per cent of the
protocol and it is **not evidence**; it is recorded in the preregistration
so it cannot later be mistaken for a result.

### The result — the search failed, and that was pre-committed

The campaign ran to completion: **ten seeds per family**, thirty in total. All
three families came back **REVERSED**.

| Family | Organica | Best simple baseline | Paired difference | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| K1 — incremental world modeling | 0.5923 | 0.9360 | −0.3437 | [−0.3773, −0.3123] | **REVERSED** |
| K2 — belief revision | 0.4111 | 0.9846 | −0.5735 | [−0.6162, −0.5309] | **REVERSED** |
| K3 — longitudinal integration | 0.0000 | 0.8578 | −0.8578 | [−0.8598, −0.8571] | **REVERSED** |

No family is SUPPORTED and none is INCONCLUSIVE: every decision interval lies
wholly below zero, so these are clean losses rather than ambiguous ones. Every
verdict survives eight different bootstrap seeds and both leave-one-out
checks. The **H2** terminal outcome fired exactly as written down before the
run: three more task families are ruled out, the negative-results map grows,
and **no V2 is designed**.

**The ablations came back empty — a negative attribution.** `NO_QUESTIONS`
(K1) −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` (K2) +0.0241 [−0.0048,
+0.0495]; `NO_DREAMS` (K3) +0.0000 [0.0000, 0.0000]. All three intervals
contain zero, so the three mechanisms the families were built around are not
load-bearing for the tasks they were meant to carry. This is within one
implementation on synthetic worlds, and it does not say the mechanisms are
inert in general.

**The K3 zero was root-caused, not assumed.** Organica scored exactly 0.000
on late incorporation on all ten seeds while a trivial co-occurrence counter
reached 0.857, so three artifacts were checked — each capable of failing.
The late structure appears in **zero of 150 cycles**, so it is not an artifact
of reading only the final cycle. Every candidate type except `anomaly` mentions
**zero of 12** late tags, so no late structure was left unread by the edge
extractor. And a 2×2 control across five seeds shows the late group is
incorporated **only when it is strictly stronger** than the group that arrived
first — so the exclusion is a salience/priority competition under a bounded
belief pool, not a blanket inability to learn late structure. This is the risk
§6 of the preregistration named before the run.

### Added

- `docs/V1-SYNTHESIS.md` — **the formal synthesis of V1.** What the project established, what it did not, the distinction between the two goals it could serve, the danger of reading six negative task families as a verdict rather than a map, and the question the evidence leaves open: *what properties must a developmental intelligence have to remain adaptable without losing coherence?* It adds no new evidence — it is a reading of the record, and every claim in it cites a committed artifact.
- `docs/phase_k_results.md` — the Phase K write-up: results, robustness, the
  K3 root cause, and what it changes.
- `docs/phase_k_results.json` — the campaign artifact: protocol block, the K0
  control, the ceiling check, all thirty per-seed records with every model's
  score and configuration, and the per-family summaries.
- `docs/phase_k_results.ndjson` — the live recording, one line per completed
  seed, appended and flushed.
- `benchmarks/phase_k_diagnose.py` — the K3 root-cause diagnostics: the
  per-cycle check, the under-read check, and the arrival-order × strength 2×2
  control.

### Changed

- The package version is **0.9.0**, cut on master; **0.8.0 is the latest
  release**. 0.8.0 was a research-integrity release: corrected clone
  verification, corrected version/tag semantics, the missing campaign
  artifacts regenerated, the cycle-1 fixation claim corrected (journal
  §31), the negative external-validity results recorded, and the
  documentation synchronised with the measurements.
- Journal §32 records the strategic shift and the negative-results map;
  **§33 records the Phase K result**, its robustness, and the K3 root cause.
- Facts sheet **§T** records the result in the one-fact-per-line form.
- The manual's status row for Phase K, its command list, its file map and its
  revision log are updated in the same turn as the change they describe.

---

## [0.8.0] — 2026-10-24

**The external-validity arc: three preregistered campaigns asking whether
Organica's structure buys anything over trivial baselines. The honest
answer recorded here is negative.**

Full detail in research journal §24–§30 and in
`docs/PHASE-H-PREREGISTRATION.md`, `docs/REGIME-SHIFT-PREREGISTRATION.md`,
`docs/PHASE-J-ADAPTATION-PREREGISTRATION.md`.

### Corrected — the structural plateau is dominant, not perfect

**0.7.0 said "the structure is decided on cycle 1" and that every colony
"holds that configuration for 2,999 cycles". The first half is right; the
second was an overstatement, and it is corrected here.**

Regenerating the Tier-1 artifact to produce `docs/discovery.json` meant
checking every published claim against the regenerated file. Measured cycle by
cycle:

| Colony | cycles at 18 beliefs / 7 subjects | of the tail half | last excursion |
|---|---:|---:|---:|
| FULL | 2,964 / 2,999 (98.8%) | 100% | cycle 212 |
| SALIENCE | 2,984 / 2,999 (99.5%) | 100% | cycle 221 |
| NO_CONTRADICTIONS | 2,957 / 2,999 (98.6%) | 100% | cycle 163 |
| **NO_QUESTIONS** | **2,277 / 2,999 (75.9%)** | **95.1%** | **cycle 2,738** |
| NO_DREAMS | 2,984 / 2,999 (99.5%) | 100% | cycle 185 |
| ANTI_EIG | 2,943 / 2,999 (98.1%) | 100% | cycle 539 |

The **retained** belief count is exactly 15 in every one of the 2,999 cycles of
every colony. The **pre-retention pool** is modal, not constant: it dips to 16
beliefs over 6 competing subjects and returns. The excursions are brief — 1–17
cycles in five arms, all over by cycle 539 — and they are real substrate
states, not a recording artifact.

**No launch gate is affected.** G-CS, G-P1, G-SUP and G-EXP hold in 100% of
cycles in all six colonies and G-SUS is 100% in every tail half, re-verified
from the regenerated artifact. G-P1/G-SUP need the pool to *exceed* 15, and 16
does. The verdicts, the noise floor, the inventory totals and the +10,776%
support growth stand as published.

The exception is the interesting part: **`NO_QUESTIONS` is also the arm that
discovers the most** (112 items; 95% of them by cycle 977, 99% by cycle 2,167)
and the only arm still finding new items deep into the run. The five arms
whose structure stops moving are the five that stop discovering; the one arm
that kept discovering kept moving. One arm in one run — a correlation, not a
cause — but it points the same way as H24.

Full record: journal §31, facts sheet §S, `docs/FORCE-MATRIX-RESULTS.md` §2.

### The position this leaves

**No external-validity task tested has produced a win for Organica.** Being
precise about what that means:

- **Held-out prediction** — beaten by both baselines (0.4126 against 0.5040
  and 0.4851).
- **Structure recovery** — beats the temporal-transition-graph baseline in
  the clean and overlapping worlds, **loses to it in the stress world**, and
  loses to plain same-event co-occurrence in all three.
- **Regime-shift detection** — no family met its preregistered success rule;
  the cause-mixture comparison was inconclusive.
- **Post-shift adaptation** — both gates failed in both families, against
  baselines with far lower predictive loss.

That is not the same statement as *the architecture has been shown useless*.
These tasks score next-event prediction, detection delay, structure recovery
and adaptation cost, and none of them is what the eight-layer engine was
designed to win. But it is the honest reading of the evidence so far, and it
is recorded **before** any redesign rather than after one.

### Added — Phase H: external validity (preregistered)

Held-out next-event prediction, F1 on known training tags:

| Model | F1 |
|---|---|
| Organica (Generation-1 prediction candidates) | **0.4126** |
| First-order Markov | **0.5040** |
| Decayed temporal association | **0.4851** |

**Disclosure:** the prediction curriculum is deterministic and identical across
seeds, so Organica's F1 is exactly 0.4126 and the Markov baseline's exactly
0.5040 in all ten seeds. The intervals there are degenerate, and they are
reported as degenerate rather than smoothed into significance.

Structure recovery against hidden cause-pair ground truth, mean F1 over the
ten seeds (range in brackets):

| World | Organica | Same-event co-occurrence | Temporal transition graph |
|---|---|---|---|
| clean | **0.7041** [0.667–0.750] | 0.8000 | 0.1482 |
| overlapping | **0.5469** [0.449–0.628] | 0.7642 | 0.2199 |
| stress | **0.1091** [0.097–0.159] | 0.7959 | 0.2803 |

Organica beats the temporal-graph baseline in the clean and overlapping
worlds and **loses to it in the stress world** — 0.1091 against 0.2803. It
loses to plain same-event co-occurrence in all three. The league is a
three-level stress test, and Organica degrades faster than either baseline
does.

### Added — Phase I: preregistered regime-shift detection

No primary success rule was met in either generator family.

- **cause-mix** — Organica's mean detection delay was **2.55** cycles,
  against **2.80** for the Markov baseline and **4.25** for decayed
  association. The paired advantage for the Markov baseline is 0.25
  cycles, 97.5% CI **[−0.25, 0.75]** — inconclusive. Organica's
  false-alarm rate is **0.0**.
- **mapping-swap** — the baselines are **faster** (Markov **1.25**,
  decayed **1.20**, against Organica **2.65**), and their **15%**
  false-alarm rate breaks the 10% gate while Organica's is **0%**. The
  benchmark is flagged invalid for this family, and the comparison is
  reported with that caveat attached.

### Added — Phase J: gradual post-shift adaptation

Both gates failed in both families.

| Family | Organica adaptation cost | Markov | Decayed |
|---|---|---|---|
| cause-mix | **2.497** | 0.178 | 0.122 |
| mapping-mix | **2.727** | 0.442 | 0.276 |

Final-stable NLL gap: **+4.478** / **+4.500** (cause-mix) and **+3.617** /
**+3.796** (mapping-mix). A clean negative result.

### Added — extended burst horizons, and the scaffold ladder

The burst curriculum was carried to longer horizons:

| Horizon | Baseline inventory | Burst inventory | Bursts delivered | Assimilation efficiency |
|---|---|---|---|---|
| 600 cycles | 91 | **119** | 19 | 1.474 |
| 1,200 cycles | 91 | **128** | 39 | 0.949 |

**Assimilation efficiency decays** — 2.44 → 1.474 → 0.949 items per burst —
so the mechanism's yield falls as the run lengthens even while the
cumulative total still climbs. At 1,200 cycles the burst arm added 8 items
between cycles 601 and 1200 and 2 in its final 100 cycles, reaching 128
against a preregistered 140+ progressive-expansion band. Neither unbounded
expansion nor a stable attractor is established; the reading is recorded as
*intermediate*.

The 300-cycle scaffold ladder, at 91 for the repeating baseline, gives 94 /
93 / 95 for the slow / medium / fast scaffold variants over 24 / 51 / 186
distinct event strings — scaffolding holds the inventory roughly flat
where uniform scaling collapses it.

### Changed

- **The live study is PAUSED** at the owner's direction, after continuous-run
  cycle 1032 (global `sleep_cycle` 5396). The pause marker is in the
  append-only log, the `INTERVAL` override was removed, and there is no
  scheduled restart. The organism did not experience the missing wall-clock
  time, and the write-up says so.
- The package version is **0.8.0**, and this release is the one that
  carries it. Master had drifted past the `v0.7.0` tag while still
  declaring 0.7.0, so the version number was naming a release that master
  was not.

### Fixed

- `tests/test_versioning.py` failed in a **fresh clone**. `clone_check.py`
  clones with `--depth 1`, which fetches only the tags pointing at the
  commit it fetched, so a release tag on an ancestor commit was absent
  locally and the test asserted against an empty tag list. The check now
  consults the remote when the checkout is shallow, and a full checkout
  with no tag still fails exactly as before.
- The version test now also fails when the version describes a commit the
  tag does not cover, which is the drift that let master sit past
  `v0.7.0` while still claiming 0.7.0.
- The local `master` branch had not actually been advanced past the
  overnight merges: a fast-forward had landed on a since-deleted PR branch
  instead, leaving `master` 13 commits behind its remote while the working
  tree still looked current. `master` is fast-forwarded and the three
  orphaned branches are gone.

### Known limitations

- Phase H's **prediction** scores are identical across all ten seeds, because
  the curriculum is deterministic; those intervals carry no information about
  seed variance. The **recovery** task does vary across seeds, and Organica's
  recovery F1 falls to 0.1091 in the stress world, below the temporal-graph
  baseline's 0.2803.
- Phase I and Phase J generalise only to their two predefined synthetic
  generator families, and Phase J's settling time is self-referenced to
  each model's own final stable loss, so it is descriptive, not
  confirmatory.
- Phase I's mapping-swap family has an **invalid benchmark** — the
  baselines' false-alarm rate is above the gate.
- The live study is paused and no restart is scheduled.

---

## [0.7.0] — 2026-10-23

**Ablation Study 2 — the Tier-1 matrix ran, and what it actually measured.**

18,000 colony-cycles: six colonies × 3,000 cycles, on the fixed substrate,
under a protocol whose metrics, gates, noise floor and sensitivity were all
fixed and committed *before* the run. The results are a scientific finding in
their own right and are published in `docs/FORCE-MATRIX-RESULTS.md` and
journal §23.

### The headline

**The structure is decided on cycle 1.** Every colony reaches 18
pre-retention beliefs, 7 competing subjects and 15 retained beliefs on the
first cycle and holds that configuration for 2,999 cycles, while mean support
grows **+10,776%**. All six arms converge to the *same* attractor despite
six different interventions. Structure flat, evidence growing by three orders
of magnitude.

> *Corrected in 0.8.0 — journal §31. "Holds that configuration for 2,999
> cycles" was an overstatement: the retained belief count is exactly 15 in
> every cycle, but the pre-retention pool is modal rather than constant
> (98.1–99.5% of cycles for five arms, 75.9% for `NO_QUESTIONS`). No launch
> gate, verdict, inventory total or noise-floor number changes.*

### The verdicts

**2 SUPPORTED · 3 REVERSED · 0 UNSUPPORTED · 0 NOT INTERPRETABLE**

| # | Prediction | Verdict |
|---|---|---|
| P1 | Retention policy affects development | **SUPPORTED** (M7: 212 vs 2,990 cycles) |
| P2 | Contradiction is developmental fuel | **REVERSED** — removing it *raises* development |
| P3 | Curiosity needs explicit questions | **REVERSED** — removing questions *raises* development |
| P4 | Dreams contribute to trajectory | **SUPPORTED** — removing them lowers it |
| P5 | EIG is orthogonal to development | **REVERSED** — lowest-EIG develops *more* than highest-EIG |

The verdicts are **direction-aware**. A naive "did the metric move?" test
would have scored all five as confirmed.

### A metric that was not a metric

M5 ("development velocity") is `new items ÷ run length`. The reference arm
discovered **74** items over 300 cycles and **74** over 3,000; the rate fell
from 24.667 to 2.467 because the numerator stopped growing. Every colony
discovered **zero** new items in its final 100 cycles. The inventory, broken
down by category, is the interpretable number: FULL 74 (16 beliefs, 11
questions, 36 dreams, 11 experiments) · SALIENCE 78 · NO_CONTRADICTIONS 79 ·
NO_QUESTIONS 112 · NO_DREAMS 44 · ANTI_EIG 85.

### A confound, disclosed

The stimulus **repeats every 9 cycles** — 9 distinct events over 7 distinct
words, seen 333 times. A repertoire cannot grow in a world that does not
change, so the plateau is consistent with *the organism exhausted the
environment*, which is not the same statement as *the organism cannot
develop*. The campaign cannot separate the two.

### The hypothesis this produced

**H24: Organica's apparent developmental plateau is primarily constrained by
environmental information content rather than by architectural inability to
reorganise.** Stated with the evidence on both sides and its falsification
criteria before the experiment that tests it. The next experiment is a
**world-complexity ladder** — a stimulus change, not an architecture change.

### The World-Scale Ladder & Burst Assimilation Findings (2026-10-23)

Immediate experimental testing of H24 during the 0.7.0 cycle revealed three
successive mechanistic insights that redefined the developmental narrative:

1. **Uniform scaling causes dilution collapse**: Multiplying distinct world
   triangles by 16× (3 → 12 → 48) collapsed inventory (91 → 66 → 56) and
   theories (10 → 4) due to frequency dilution in the `MAX_PREDICTIONS = 20`
   window.
2. **Scaffolding prevents collapse**: Maintaining a 3-triangle core scaffold
   prevented multi-layer degradation, preserving theories at 13–14 and
   stabilizing beliefs at 18.
3. **Burst reinforcement enables developmental assimilation**: Novelty requires
   local reinforcement to survive early-stage filters (`PREDICTION_MIN_COUNT = 5`,
   `STABLE_THRESHOLD = 0.3`). Introducing novelty in concentrated bursts
   drove cumulative inventory to **113 items (+24.2%)** across 300 cycles, with
   active discoveries continuing through epochs 2–5 (88, 10, 7, 2, 6, 0).
4. **Conclusion frozen**: *Organica's developmental capacity is not a fixed
   architectural constant. It is strongly dependent on the structure and
   presentation schedule of novelty.* Prior candidate ceilings (74, 91) were
   constrained measurements of environmental bottlenecks rather than hard
   architectural limits.

### Added

- `docs/FORCE-MATRIX-RESULTS.md` — the results, the verdicts, what the
  campaign can and cannot answer, and H24.
- `benchmarks/run_matrix.py` — the campaign launcher. Runs the G1
  verification once, launches the six colonies in parallel with the **same**
  `PYTHONHASHSEED=0`, and records the hash seed, git commit and wall clock
  in the artifact.
- `benchmarks/verdicts.py` — every pre-registered prediction forced into
  SUPPORTED / UNSUPPORTED / REVERSED / NOT INTERPRETABLE, direction-aware.
- `benchmarks/discovery_report.py` — the inventory breakdown and the
  cumulative discovery curves, plus the stimulus's own measured periodicity.
- `benchmarks/process_noise.py` — the process-level noise floor, with a
  parallel sweep and the scale-invariant item-count form.
- `organica/scale_streams.py` — worlds of increasing information content for
  the H24 ladder.
- `benchmarks/scale_ladder.py` — the ladder runner.
- `benchmarks/hub_degree_probe.py` — measures the Layer-1 survival threshold
  against hub degree.
- `docs/force_matrix.json`, `docs/discovery.json`, `docs/verdicts.json`,
  `docs/process_noise_3000.json`, `docs/figure_tier1_matrix.svg`,
  `docs/figure_discovery.svg`.
- Facts sheet §I (matrix results) and §J (H24).
- `docs/ORGANICA-V2-DESIGN-NOTES.md` §7–§10 rewritten with the matrix's
  answers and the new stimulus requirement.

### Changed

- `benchmarks/force_matrix.py` now records the per-cycle **discovery
  history** — new items and cumulative distinct items per category — so the
  inventory can be measured directly rather than inferred from a rate.
- `benchmarks/metric_sensitivity.py` gains the per-metric most-sensitive-
  colony ranking and a **downstream** deviation ranking that excludes each
  colony's own intervention metric.
- `benchmarks/v1_impact.py` excludes `None` metrics rather than zeroing
  them. The harness reports "n/a" for lineage completeness when a condition
  has no lineage; that is *not measurable*, not zero, and zeroing it would
  have been the same class of error as the scope defect the tool documents.
- The README now carries the research findings, the verdicts, and H24.

### Fixed

- `benchmarks/seed_noise.py` overclaimed: it measures the **within-process**
  seed floor (exactly 0.00), not the floor that binds. Disclosed in place.
- `benchmarks/figure_campaign.py` failed with a raw `KeyError` on an
  artifact predating the per-cycle series capture; it now says so.
- `benchmarks/run_matrix.py` and `force_matrix.py` print the G1 header even
  when verification is skipped.
- `organica/scale_streams.py` numbered its leaf tags (`ta0`), and the engine
  only extracts words of **four or more letters** — every leaf was silently
  invisible and the ladder measured nothing. The leaves are now spelled in
  letters.

### Known limitations

- The stimulus's 9-cycle period means the campaign cannot separate
  "exhausted the environment" from "cannot reorganise". H24 is untested.
- M7's spread rests on very few observations: the reference arm's
  212-cycle mean is the mean of **one** belief death. Reported as such.
- `NO_CONTRADICTIONS` removes contradiction's **weight in the confidence
  formula**, not contradictions. M3 is near-invariant for it by
  construction. The colony's name overstates the intervention; disclosed in
  the results document and the facts sheet.

---

## [0.6.0] — 2026-10-23

> **0.6.0 is the first release of this repository to carry a git tag.**
> The versions below were published to this repository without tags, so they
> are recorded here as history but cannot be checked out as named commits.
> The tag convention starts here: releases are tagged `v<version>`, and
> `tests/test_versioning.py` fails the build if the version has no tag.

**Milestone M0.5 — mechanism closure, and a substrate correction.**

This release changes the organism's behaviour. It is a pre-1.0 release
because the public API is not stable, but the behavioural change is
real and is disclosed in full in `research-journal/phase_g_findings_20261021.md`
§21.8 and `docs/USER-MANUAL.md` §8.4.

### Changed — substrate

- **The tag-frequency counter is now scoped to world events.** It was
  maintained over every stored event, including the organism's own sleep
  payloads, while the co-occurrence and temporal graphs it normalises are
  built from world events only. The counter is the *denominator* of the
  Layer-1 edge strength (`ratio = count / source_freq`), so the two sides
  of the ratio measured different populations and the survival filter
  discarded the world's own structure. Measured: 4 surviving edges, 0
  processes, 0 workflows, 0 beliefs.
- A `meta` table records the scope the counters were built with, so a
  database written by an older build rebuilds its counter exactly once
  instead of mixing two populations in one table.

### Added

- `docs/FORCE-MATRIX-PREREGISTRATION.md` — M1–M9 frozen, plus the launch
  gates G-CS, G-P1, G-SUP, G-EXP and G-SUS.
- `docs/ORGANICA-V2-DESIGN-NOTES.md` — planning only: what survived
  scrutiny, what failed, what turned out inert, what turned out essential,
  what became a bottleneck, and the open questions.
- `docs/gate_validation.json`, `docs/mbsd_census.json`,
  `docs/mbsd_census_postfix.json`, `docs/gate_check.json`,
  `docs/freq_scope_probe.json`, `docs/metric_sensitivity.json`,
  `docs/force_matrix_pilot.json`.
- `organica/branch_streams.py` — branch-structured stimuli built from
  triangles, derived from the measured mechanism.
- Benchmarks: `gate_validation.py`, `mbsd_census.py`, `branch_sweep.py`,
  `branch_sweep2.py`, `branch_diag.py`, `branch_diag2.py`,
  `freq_scope_probe.py`, `gate_check.py`, `force_matrix.py`,
  `metric_sensitivity.py`, `seed_noise.py`, `v1_impact.py`,
  `figure_campaign.py`.
- `tests/test_substrate_equivalence.py` — a scope-consistency regression
  test: a sleep payload must change neither the temporal graph nor the
  frequency counter that normalises it.
- `tests/test_versioning.py` — the version declarations must agree, must
  be SemVer 2, must be pre-1.0, and must have a git tag and a changelog
  entry.
- `run_continuous.py` writes `freq_scope=world` in its build marker, so
  the append-only log says which substrate produced which cycles.

### Changed — research findings

- **The proposed Multi-Belief Subject Density gate is structural, not
  predictive.** Layer 5 forms exactly one theory per subject holding ≥ 2
  beliefs; the identity `theories == min(competing_subjects, MAX_THEORIES)`
  holds in 100% of cycles in 9 of the 11 conditions. The gate is restated
  as an absolute count.
- **The `r=4 / r=6 / r=10` "phase transition" was an instrumentation
  artifact.** With the counter scoped correctly, all three repeat counts
  behave identically: a full prediction window, a belief pool of 18, seven
  competing subjects, and 100% of tail cycles passing every gate.
- **"No Falsification freezes the organism" is withdrawn.** Post-fix it is
  the best-supplied condition in the study: 18 beliefs, 6 of 6 subjects
  competing, MBSD 1.000.
- **"The organism is supply-limited, not selection-limited" is withdrawn as
  a general statement.** It was true of the study stream on the old
  substrate; on a branch-structured stimulus the cap binds and the
  retention policy changes the population.
- Facts sheet D8b is **corrected in place**; D8c–D8e are added.

### Fixed

- The G1–G4 perturbation ladder caught a measurement reading the wrong
  report attribute and reporting a working layer as dead (previously
  corrected, recorded here for the release history).
- The campaign runner instantiated the instrument instead of the colony
  subclass, which made every colony run the default service and produced
  a byte-identical FULL and SALIENCE. The runner now asserts G1 — that
  each colony's intervention is in the code path — before running a
  colony.

### Known limitations

- The ablation study in `docs/ablation_study.json` was produced on the
  **pre-fix** substrate. Every condition ran on the same substrate, so
  the comparisons stand, but the absolute densities are not comparable to
  post-fix numbers. `benchmarks/v1_impact.py` produces the before/after
  audit (`docs/v1_impact.json`).
- One seed per colony. Deltas smaller than the measured seed-noise floor
  are reported as *not interpretable*. The floor is measured by
  `benchmarks/seed_noise.py`.

---

## 0.5.0 — 2026-10-21

- Phase G endurance work: monotonic sleep-cycle counter in the database,
  bounded candidate retention, the tag-frequency counter moved from a
  full-table scan to an incremental counter.
- `docs/USER-MANUAL.md` rewritten with 18 sections.
- `docs/FACTS-SHEET.md` — facts with provenance, separated from assumptions.
- `docs/GATE-BOARD.md` — what is demonstrated versus assumed.
- `benchmarks/clone_check.py` and a passing fresh-clone check.

## 0.4.0 — 2026-10-20

- Observation pipeline repaired; `MemoryService.batch()` added after
  profiling found one fsync per candidate dominated the cycle
  (1,023 commits = 3.0 s of a 4.5 s cycle).
- `benchmarks/cold_start.py` — the eight assistance levels.

## 0.3.0 — 2026-10-20

- The eight-layer engine, the four reproduction domains, the reproduction
  pack and the growth benchmarks.

## 0.2.0 — 2026-10-19

- The study daemon, the append-only log format, and the snapshot writers.

## 0.1.0 — 2026-10-19

- First public release of the substrate and the sleep pipeline.

[0.8.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.8.0
[0.7.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.7.0
[0.6.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.6.0
