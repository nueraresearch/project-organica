# Engine-change audit — what changed, what the freeze still enforces, and what a rerun would actually test

**Status: written. This document runs nothing.** It is the first step of a proposed
engine-improvement validation campaign: before any preregistration exists, establish what
actually changed in the engine after the archival freeze, and map those changes to the
failures on record. There are no cells, no seeds and no verdicts here. Every figure is
quoted from an artifact or a commit message, and the artifact outranks this page.

The reason it exists is the one fact that decides the whole campaign:

> **None of the recorded failures was measured on the engine at HEAD.**

Phase H, I, J, K1, K2 and K3, the acquisition gate and Phase L were all run in October, on
the frozen engine or immediately after it. Between 2026-10-25 and 2026-11-07 the engine
changed in material ways — new layers, a different candidate ranking, a raised prediction
cap, a fix to the evidence lookback, and a submodule split. So "does the improved engine
still fail?" is not a question about replication. It is a question about a different system,
and it needs its own preregistration.

## 1. Three reference points

| Reference | Commit | What it is |
| --- | --- | --- |
| `v0.9.0` | `af32854` (annotated tag object `2c5df7b`) | the archival freeze reference; `AGENTS.md` rule 12 and `docs/V1-FREEZE.md` |
| `v0.12.0` | `5804e60` | the deposit object: the release a reader can cite today (`CHANGELOG.md`) |
| HEAD | `0.13.0` (unreleased) | current master |

**21** commits after `v0.9.0` touched `organica/`, the first on 2026-10-25 and the last on
2026-11-07. That number is derived from git, not typed: `tests/test_engine_change_audit.py`
recomputes it and fails if this document disagrees.

## 2. What changed, by file

| File | Added | Deleted | Note |
| --- | --- | --- | --- |
| `organica/sleep.py` | 291 | 1777 | the concentration of the diff; most of the deletion is the submodule split (`7becdb5`), not removed behaviour |
| `organica/memory.py` | 64 | 13 | covering indexes and the substrate work |
| `organica/candidates.py` | 315 | 0 | new: candidate dataclasses, including the `carried_forward` marker |
| `organica/sleep_extraction.py` | 826 | 0 | new: extraction, split out of `sleep.py` |
| `organica/sleep_inquiry.py` | 401 | 0 | new: active inquiry |
| `organica/sleep_selection.py` | 454 | 0 | new: natural selection, split out |
| `organica/sleep_synthesis.py` | 448 | 0 | new: composition, split out |
| `organica/environment.py` | 239 | 0 | new: active environment dispatcher |
| `organica/__init__.py` | 5 | 1 | version only |

The split is the largest single structural change, and its behaviour-preserving claim is
**not currently checked by anything**. That matters because of §3.

## 3. The freeze check no longer checks the engine

Run against this tree on 2026-11-07:

```
tests/test_v1_freeze.py::test_engine_file_is_unchanged_since_the_freeze[organica/sleep.py]      SKIPPED
... (all seven frozen engine files) ...
tests/test_v1_freeze.py::test_published_artifact_is_unchanged_since_the_freeze[docs/...]       PASSED  (8 of 8)
tests/test_v1_freeze.py::test_the_freeze_record_exists_and_names_the_tag                       PASSED
9 passed, 7 skipped
```

The seven skips are exactly `FROZEN_ENGINE`. The cause is the first executable line of the
test body:

```python
import organica
if organica.__version__ >= "0.12.0":
    pytest.skip(f"Engine files on master active in {organica.__version__}")
```

This is a **version gate, not a shallow clone**: the eight published-artifact checks in the
same file pass, and they use the same tag resolution, so the tag is readable here. (A side
effect worth recording: the test's docstring now sits *below* the `pytest.skip` call, so it
is a bare string expression rather than documentation.)

The frozen set is seven files — `organica/sleep.py`, `organica/memory.py`,
`organica/paths.py`, `organica/streams.py`, `organica/branch_streams.py`,
`organica/scale_streams.py` and `organica/ground_truth_worlds.py`. Five of the seven are
unchanged since the tag; the other two are the ones §2 measures.

The record already says this, in two places. `docs/V1-FREEZE.md` §6 states that "the
engine-file identity check in `tests/test_v1_freeze.py` already skips at package versions ≥
0.12.0, so this amendment is recorded rather than enforced by editing that mechanism", and
the admission amendment repeats it and adds that the amendment is licensed by `git diff`
rather than by the test.

**Consequences, stated plainly.**

1. Since 0.12.0, no mechanism in the repository would fail if a frozen engine file changed.
   The freeze is documentary from 0.12.0 onward; the archival text at `v0.9.0` is preserved,
   but nothing is comparing the live engine against it.
2. A campaign that says "freeze both engines" cannot use this mechanism. It has to pin its
   own reference points and enforce them, or the comparison has no fixed object at either end.
3. The submodule split in §2 is the change most in need of a behaviour-preserving proof, and
   it is exactly the class of change the disabled check was written to catch.

**Resolved 2026-11-08.** The gate is gone, and consequence 1 no longer holds: since 2026-11-07 a
frozen engine file that changes without a version bump fails the suite. The mechanism is
`docs/engine_pin.json` -- a SHA-256 of every module under `organica/`, checked by
`benchmarks/engine_pin.py --check` and by `tests/test_engine_pin.py` -- and
`tests/test_v1_freeze.py` now keeps the artifact comparison while asserting that the pin still
covers the seven frozen files and can still report a changed one. Section 3 above is left as
written, because it is the measurement that motivated the pin; `docs/ENGINE-VERSION-AUDIT.md`
section 11 records the mechanism as it stands.

## 4. The changes, in order

21 commits, grouped into 15 entries. The last two columns are the audit's actual product and
are the weakest part of it: they name a *plausible* connection, not a measured one.

| Commits | Date | What the commit says it did | Failure it could touch | Measured on that build? |
| --- | --- | --- | --- | --- |
| `fa47ae0` | 2026-11-04 | cognitive determinism; fix lookback contamination (D2) | every belief-support figure: the lookback window included the organism's own sleep rows | No |
| `8752c66`, `5d9538f`, `b955ccb` | 2026-11-04 | relation-family stratification, transition predictive ranking, generation-index alignment | Gate 13 ranking; the precision ceiling | No |
| `52c43f4` | 2026-11-04 | Layer 1 grounding (D3), conditional-entropy ranking, experiment execution (Law IV) | known gap G1 (no executor); held-out prediction | No |
| `c13d67e` | 2026-11-04 | EIG fix (Law V), G2–G8 natural-selection decay, promotion loop, temporal edge decay | K2 and K3; the decay-necessity question | No |
| `9f2c8e1` | 2026-11-04 | cap raised to 40, loop and anomaly structural ranking, M3 contradiction density, question closure | the acquisition bound; non-frequency ranking | No |
| `6165523`, `7201d79` | 2026-11-04 | substrate performance; single-pass selection and candidate caching | substrate only, then selection behaviour | Substrate claim tested; selection not |
| `9dd6fe0` | 2026-11-04 | active environment dispatcher; H24 ladder confirmation | K1 and K2 depend on the environment | No |
| `6d45eb7` | 2026-11-04 | Active Inquiry (Option B), retention pressure audit | the P3 reversal (question generation) | No |
| `19246a2` | 2026-11-05 | RoleCandidate and SchemaCandidate for cross-context reuse | the orthogonal-context dependence; question Q012 | No |
| `7becdb5` | 2026-11-05 | split `sleep.py` into submodules; memory indexes | nothing by design; it claims equivalence | No |
| `e6d1bcc` | 2026-11-06 | score acquisition on unboosted evidence; content-sensitive priming | the earned cross-context run is on this build | Yes, for that run |
| `6c87f63`, `0507b8f` | 2026-11-06 | candidate supersession (Amendment 1); decay confirmation harness | Gate 13 asserted coverage; decay | Yes: 26/112 → 22/112 → 34/112 of 112 |
| `c845fd8`, `024a475` | 2026-11-07 | adopt diversity-first admission, then withdraw it the same day | admission and allocation | Yes, and the arm no longer exists in the package |
| `a95305d`, `fdb505d` | 2026-10-25, 2026-10-31 | four Phase L harness defects; release-state documentation | Phase L measurement; no engine behaviour | Yes, for Phase L |

## 5. What this establishes

**The mapping does not exist.** Twenty changes, nine recorded failures, and not one artifact
says *this change was made because that failure was expected to move*. Every "could touch"
cell in §4 is reconstruction from commit messages, not a recorded hypothesis.

That is the finding, and it is why the sequencing matters. A rerun campaign launched from
this state would carry twenty changes and no mechanism, so a positive result could not be
attributed to any of them and a negative result could not be explained. The preregistration
has to be built from a change-to-failure map in which each row names a mechanism and a
falsifier, and rows without one are excluded from the campaign rather than bundled into it.

## 6. Which failures cannot be rerun as they stand

Four traps, each of which would produce a number that looks like a replication and is not.

1. **The acquisition experiment.** Its failure was recorded with a named bound,
   `MAX_PREDICTIONS = 20`. A commit in §4 raised the cap, so rerunning it now measures a
   different engine under a different bound. The recorded `0–3 / 112` belongs to the
   pre-change build.
2. **Gate 13.** The precision ceiling `0.3438`, the `240–244` asserted edges and the ~12x
   budget multiple were all measured at cap 20, before Amendment 1. Amendment 1 moved
   asserted coverage from 26/112 to 34/112 on one seed and world, and `docs/V1-FREEZE.md` §6
   says plainly that every Gate 13 figure recorded before it describes the pre-amendment
   engine. Re-measuring is legitimate; comparing is not.
3. **The cross-context run.** The earned result (TR 0.944, 3.6 against 3.4 cycles, prior
   applied 162 times against 270, five seeds, no p-value) is on `e6d1bcc` or later, so it is
   not comparable to the October campaigns. It is also the only transfer number the record
   currently stands behind.
4. **Phase L, which is the exception.** Its characterization — a 3:1 transition, stable
   across every resampling the campaign could run, on a step-shaped curve — is the most
   robust object in the repository, and the phase's verdict stays `INCONCLUSIVE` regardless.
   It is the one campaign whose rerun would be directly informative rather than merely new.

## 7. Two corrections to carry into the campaign

**C1 and H2 are not as they are usually summarised.** The divergence investigation recorded
`C1` as **FAILED as pre-registered** — the control seed's assembled lists were required to be
identical at every hash seed (P2) and were not (`docs/DIVERGENCE-MECHANISM-RESULTS.md` §C1). A
narrower post-hoc observation, that the control's *admitted stream* is identical across hash
seeds while its builder sequences differ, is recorded there and explicitly **not** as a held
control; the same section discloses that an earlier version reported C1 as invariant. `H2` is
**untested in an admissible form**, because F2 fired before Arm B could speak. Carrying "C1 had
support" into a new campaign would import a status the record already corrected.

**This audit has no mechanism column it can defend.** §4's fourth column is a hypothesis at
best. The campaign's first real document is the one that replaces it.

## 8. Prerequisites before any preregistration

Ordered, and none of them runs a cell.

1. **Pin the improved engine.** A commit plus a SHA-256 of every file under `organica/`, in an
   artifact, with a check that fails when the engine moves without a version bump. Without a
   pin, "the improved engine" is a moving target and no protocol can be frozen against it.

**In place from 2026-11-07.** `docs/engine_pin.json` records a SHA-256 for each of the 14
modules under `organica/` at version 0.13.0, with the commit the pin was taken at, and
`python -m benchmarks.engine_pin --check` fails when one is added, removed or changed. It
distinguishes the two cases: an engine that moved while the package still claims 0.13.0, and a pin
that a version bump has outdated. `tests/test_engine_pin.py` runs that check inside the suite.
2. **Choose the comparison, and choose it explicitly.** `v0.9.0` is the archival reference;
   `v0.12.0` is the deposit object and already contains most of the changes in §4. A
   three-way comparison (`v0.9.0`, `v0.12.0`, pinned candidate) costs one more arm and settles
   which of the two the campaign is actually arguing against.
3. **Enforce the pin.** The existing freeze check was off above 0.12.0 (§3); since 2026-11-08 identity is enforced by `docs/engine_pin.json`, which fails the suite when a module is added, removed or changed without a version bump. A campaign that
   depends on a fixed object needs its own identity check, built to fail, and proved to fire.
4. **Replace §4's fourth column with mechanism and falsifier.** One row per change that stays
   in the campaign; rows without a named mechanism are out.

**In place from 2026-11-07.** `docs/ENGINE-CHANGE-FAILURE-MAP.md` is generated from
`docs/engine_change_failure_map.json`: **15** rows over the **21** commits that touched
`organica/`, **10** staying in the campaign and **4** excluded. Every staying row names the
failure, the mechanism, a falsifier, its observables, the pre-change measurement and two decisions
that differ. `python -m benchmarks.change_map --check` recomputes coverage from git, so a new engine
commit fails until a row explains it.
5. **Fix the C1/H2 record before it is cited.** §7.
6. **Get the preregistration reviewed independently.** `docs/DECISION-STAGE-B-SEQUENCE.md`
   already makes external review the gate for Stage B; the same gate applies to a campaign
   whose whole purpose is to be inconvenient to its author.

## 9. What this document does not do

It does not re-score a verdict, does not re-run a campaign, does not assert that any change
in §4 improved anything, and does not authorise a build. It establishes three facts — the
engine moved, the freeze no longer checks it, and no change-to-failure mapping exists — and
it names what has to be true before a preregistration can be written.
