# Tuning without laundering the old result (2026-11-07)

**Status: a design record for a new cycle. No candidate rule, no cell, no claim.**
The seed blocks live in `docs/decay_tuning_cycle.json`; this document describes how
a tuned rule may earn adoption, and what it may never inherit.

## 1. What the old campaign established, and its boundary

The 448-cell calibration found no threshold on its fixed grid that was live on
every cell while holding precision at or above 0.95 on every cell, for either the
transition arm or the ratio control
(`docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md` §18). That is a result about
**that grid and that selection rule on those cells**. It does not establish that
every real value fails, and it is not evidence for whatever value a later search
prefers.

## 2. Two phases with different epistemic standing

**Exploratory phase -- may use the 448 cells.** Candidate rules may be designed
from those results: a degree-aware threshold, a different strength normalisation,
or a revised grid. Every output of this phase is labelled *exploratory*. It may
generate a hypothesis. It is **never confirmation**, and a rule chosen here
inherits nothing from the campaign that suggested it.

**Freeze.** Before the first confirmatory cell, the rule is fixed on **development
seeds** that appear nowhere else in the repository. The freeze records, in a new
pre-registration: the rule in closed form; every parameter and how it was
selected; the degree ladder; the endpoints, gates and labels; and the outcome
table including a *no rule passes* branch. After the freeze the rule may not
change, and a failure is recorded against that rule.

**Confirmatory phase -- fresh seeds only.** The frozen rule runs on the
confirmatory block in fresh worlds at the same degrees. Adoption requires that
study to pass; a pass is support within its tested scope, nothing wider.

## 3. What the new pre-registration must contain before any cell

1. The rule in closed form, and the mechanism it claims -- not just a grid.
2. Its parameter-selection rule, fixed before cells and applied to development
   seeds only: a threshold may not be computed from the run it judges.
3. The confirmatory seeds from the artifact, checked mechanically against every
   seed in the repository.
4. The same endpoints as the old protocol: liveness as a comparability gate and
   never a success, precision, coverage, false assertions, revision, and task
   log-loss against the **strongest** simple baseline.
5. **A contrast that separates the rule from a threshold change.** A degree-aware
   rule must be compared with the best global-threshold arm on the same cells, so
   that "degree-aware helps" cannot be a relabelled threshold win.
6. The outcome table, with a named rejection for every way the rule can fail.

## 4. What tuning cannot buy

* **Safety.** A rule that improves a task endpoint has not been shown safe across
  degrees unless the safety endpoints pass on fresh data.
* **Generality.** One ladder of synthetic worlds at degrees 2/4/6/12 is the tested
  scope; a pass does not generalise to other world families.
* **Task value.** Improved liveness or growth is not an improved task outcome.
  Those are separate endpoints and are reported separately.

## 5. Seeds, and what can be renewed

Development: **20310101-20310108** (8 seeds). Confirmatory:
**20310109-20310128** (20 seeds). They are the first contiguous window of
28 seed numbers that appears in no file under `docs`, `tests`, `benchmarks`,
`research-journal` or `papers`; `tests/test_decay_tuning_cycle.py` repeats that
scan and fails if any recorded seed appears elsewhere. Recording the block also
makes it *consumed* for Stage B's seed audit, which is the intended effect: a
declared block is registered rather than left free to be reallocated.

The **degree ladder cannot be renewed**: degree 3 is not constructible
(`expanding_triangles` realises even degrees only) and the even ladder is fixed by
Amendment 2 of the decay pre-registration. "Fresh held-out degree regimes"
therefore means fresh worlds at degrees 2/4/6/12, not new degrees.

## 6. Relation to the existing records

* The old pre-registration and its §18 outcome stand unchanged; nothing here
  amends them, and no old cell becomes confirmatory.
* `docs/COMPARISON-0.9-0.12-PREREGISTRATION.md` is untouched: a new engine
  version still requires its amendment **before** cells.
* `benchmarks/decay_operability.py` answers a different question -- whether a build
  stays usable -- and its result cannot substitute for confirmation of a rule.
