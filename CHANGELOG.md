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
| **Package version** | `0.x.y` (SemVer 2) | the released, installable, citable artifact | **0.7.0** |
| **Architecture generation** | *Organica 1*, *Organica 2* | a generation of the eight-layer engine. Organica 1 is frozen; Organica 2 is planned | **Organica 1** |
| **Research campaign** | *Ablation Study 1*, *Ablation Study 2* | the experimental series. Study 1 is the eleven-condition ablation; Study 2 is the six-colony Tier-1 matrix | **Study 2 in flight** |

The package version is **pre-1.0**, which is the honest state: the public
API is not declared stable, and the MINOR/PATCH numbers carry the
meaning instead. `tests/test_versioning.py` asserts that the three
declarations — `organica.__version__`, `pyproject.toml` and `CITATION.cff`
— never drift apart, and that a git tag exists for the version.

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

[0.7.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.7.0
[0.6.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.6.0
