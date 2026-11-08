# Engine-version audit — the freeze, and the build every result ran on (2026-11-08)

**Status: an audit record and a correction, not an experiment.** It measures the engine's actual
delta since the archival tag, establishes which build each result artifact ran on, and reopens the
questions whose evidence predates the rework. It changes no engine file, runs no cell and claims no
result is false. Everything numeric below is computed from git and from the artifacts by
`docs/engine_version_audit.json`, which this document restates.

## 1. The claim that was being made

`docs/V1-FREEZE.md` says Organica 1 is a fixed reference object and that everything after it
*measures* the engine. Rule 12 of `AGENTS.md` says the seven frozen engine files must not change and
that `tests/test_v1_freeze.py` enforces it. That is the premise every later verdict inherited: one
engine, many measurements.

## 2. What the repository contains

Since `v0.9.0`, **20 commits** touch `organica/`, changing **9 files** by **+3043 / -1791** lines.

| File | Commits since v0.9.0 | Lines |
| --- | --- | --- |
| `organica/__init__.py` | 6 | +5 / -1 |
| `organica/candidates.py` | 2 | +315 / -0 |
| `organica/environment.py` | 1 | +239 / -0 |
| `organica/memory.py` | 5 | +64 / -13 |
| `organica/sleep.py` | 12 | +291 / -1777 |
| `organica/sleep_extraction.py` | 2 | +826 / -0 |
| `organica/sleep_inquiry.py` | 1 | +401 / -0 |
| `organica/sleep_selection.py` | 3 | +454 / -0 |
| `organica/sleep_synthesis.py` | 1 | +448 / -0 |

Two of the seven files rule 12 calls frozen are among them: `organica/sleep.py`, `organica/memory.py`. The others are new modules that the
old `sleep.py` was split into, plus `candidates.py` and `environment.py` — all of them live on the
path `SleepService` takes every cycle.

## 3. The guard was switched off

`tests/test_v1_freeze.py` returns `pytest.skip` for **every** frozen engine file once
`organica.__version__ >= "0.12.0"`. That condition entered in `fa47ae0` (2026-11-04), in the commit titled
"Advance to 0.12.0". The test still passes today — and it passes because it skips, not because the
files match the tag. Rule 12's enforcement has been inert on master since that commit, which is why
the delta in section 2 could accumulate without a single failing test.

`docs/V1-FREEZE.md` records two amendments, the carried-forward scoring correction and the
admission rule (adopted, then withdrawn the same day). Neither describes the rework above: the
submodule split, single-pass natural selection, `MAX_PREDICTIONS` moving from 20 to 40, Layer 1
grounding, conditional-entropy and transition predictive ranking, relation-family stratification,
temporal edge decay, Layer 2b and 3b, active inquiry, the determinism change and the lookback
contamination fix. Those are the changes rule 2 says require a recorded decision *before* they are
implemented, and the freeze record does not name them.

## 4. Which build each result ran on

Artifacts that record their engine version:

| Engine | Date | Artifact |
| --- | --- | --- |
| `0.11.0` | 2026-10-31 | docs/candidate_membership_audit.json |
| `0.13.0` | 2026-11-07 | docs/decay_adaptation.json |
| `0.13.0` | 2026-11-08 | docs/decay_competition_probe.json |
| `0.13.0` | 2026-11-07 | docs/decay_falsifier.json |
| `0.13.0` | 2026-11-08 | docs/decay_paired_bracket.json |
| `0.13.0` | 2026-11-07 | docs/decay_sweep.json |
| `0.13.0` | 2026-11-08 | docs/decay_threshold.json |
| `0.13.0` | 2026-11-08 | docs/decay_threshold_edge.json |
| `0.10.0` | 2026-10-31 | docs/formation_utilization.json |
| `0.10.0` | 2026-10-31 | docs/formation_utilization_pre_correction.json |
| `0.10.0` | 2026-10-31 | docs/formation_utilization_timing.json |
| `0.10.0` | 2026-10-30 | docs/formation_utilization_timing_pre_amendment.json |
| `0.10.0` | 2026-10-31 | docs/formation_utilization_timing_pre_correction.json |
| `0.13.0` | 2026-11-07 | docs/operating_point.json |
| `0.13.0` | 2026-11-07 | docs/reference_death_ledger.json |
| `0.13.0` | 2026-11-07 | docs/substrate_repair.json |
| `0.10.0` | 2026-10-31 | docs/use_path_diagnostic.json |

Artifacts that record no engine version at all, and whose dates place them before or across the
rework:

- `docs/gate13_allocation_rule.json`
- `docs/acquisition_single_seed_pilot.json`
- `docs/acquisition_endpoint_audit.json`
- `docs/functional_structure_confirmatory.json`
- `docs/density_interaction_a2_result.json`
- `docs/density_padding_result.json`
- `docs/transfer_provenance.json`
- `docs/store_time_role_durability.json`
- `docs/decay_attribution.json`
- `docs/decay_admission_slot.json`
- `docs/candidate_membership_audit.json`

Tags: the engine was released through `v0.10.0` (2026-10-31) and `v0.12.0` (2026-11-06); `0.11.0`
and `0.13.0` were never tagged. The Gate 13 artifacts are dated 2026-10-29 — before the `v0.10.0`
tag — and the acquisition confirmatory block is dated 2026-11-02. So the closed record spans at
least four builds, and no artifact from the pre-0.12 era names the commit it ran on.

## 5. What this invalidates, and what it does not

- **Comparisons across builds are not measurements of one system.** A verdict obtained on the 0.10.0
  engine is a verdict about the 0.10.0 engine. It does not transfer to 0.13.0 by being in the same
  repository.
- **Comparisons within one build remain valid** as measurements of that build. Nothing here says any
  result was wrong when it was made.
- **The decay programme is the only family pinned to the current build.** `Q046` through `Q051` cite
  artifacts that record `engine_version: 0.13.0` and reproduce each other's cells, which is why they
  are not reopened here.
- **Nothing here is a capability claim** in either direction. A different engine is not a better one.

## 6. Questions reopened (2026-11-08)

| Question | Why |
| --- | --- |
| Q001 | the recorded answer rests on the V1 synthesis, measured on the 0.9.x engine before the 0.12.0 cognitive rework. Whether structure still forms under the current build is unmeasured on it. |
| Q002 | the 112-edge presence figure comes from docs/gate13_allocation_rule.json (2026-10-29), produced before the 0.10.0 tag and before MAX_PREDICTIONS moved from 20 to 40. |
| Q003 | the precision ceiling and the coverage budget were measured on a pre-0.10.0 build; the 0.13.0 engine's ordering basis, relation-family stratification and entropy ranking did not exist when they were measured. |
| Q007 | the confirmatory endpoint ran on 2026-11-02, before the 0.12.0 rework introduced single-pass natural selection, Layer 1 grounding and the new ranking. The structures that reach the readout are not the same structures. |
| Q008 | the motivational reversals were measured on the pre-0.12.0 engine; contradiction density and the EIG fix both landed in the 0.12.0 work, so the mechanisms scored are not the mechanisms now shipped. |
| Q018 | the retirement was argued from a pre-0.10.0 precision ceiling. That measurement does not describe the current engine, so the variant space is unmeasured there rather than closed. |

Each was moved from `closed` (or, for `Q018`, `retired`) to `open`. The former outcome and answer
are kept in the record, labelled as a measurement of the build it ran on, because deleting them
would erase what was actually observed.

## 7. Questions deliberately not reopened

- **`Q009` and `Q010`** are governance questions. They close decisions about process, not
  measurements, so no engine version can affect them.
- **`Q004`, `Q005`, `Q006`, `Q024`, `Q043`, `Q044`** are dated after the 0.12.0 rework, so their
  evidence is current-era, but their artifacts record no version. That gap is a defect of the
  artifacts, not evidence against the results, and it is recorded rather than silently accepted.
- **`Q029`–`Q037`, `Q040`–`Q042`, `Q046`–`Q051`** are pinned to 0.13.0 and mutually reproducing.
- **`Q017`, `Q019`, `Q020`** were retired on decision structure rather than on a measurement, and
  **`Q021`, `Q024`** were withdrawn because the mechanism they described failed on the engine's own
  ordering. Reopening those would re-run a decision, not a measurement.

## 8. Claims downgraded

`C001`, `C002`, `C003` moved from `DEMONSTRATED` or `SUPPORTED` to `HYPOTHESIS`, because the ledger rule is that a
load-bearing claim may cite only a closed, supported question and the questions behind them are no
longer closed. The ledger keeps the original statements and the reason.

## 9. What would close any of them again

A measurement on the current build, with the engine version recorded in the artifact and the
question record naming that artifact. Recording the version is now part of the artifact, not a
courtesy: an artifact without one cannot be attributed to a build at all, which is the defect that
made this audit necessary in the first place.

## 10. What this does not claim

It does not claim the current engine is better or worse than the one that produced the closed
record, that any published number is false, or that the reopened questions will resolve differently.
It claims one thing: the record spans several engines, and no verdict from before the 0.12.0 rework
describes the engine that is in this repository now.

## 12. The guard is unlocked and re-baselined (2026-11-08)

`tests/test_v1_freeze.py` no longer skips at version 0.12.0 and above. It compares the shipped engine
against a recorded commit in `docs/engine_reference.json` instead of the archival tag, and it guards
thirteen files: the seven rule 12 names plus `candidates.py`, `sleep_extraction.py`,
`sleep_selection.py`, `sleep_synthesis.py`, `sleep_inquiry.py` and `environment.py`, because the
engine was split into modules and a guard watching only `sleep.py` would be watching a shell.

The semantics changed with it. A guard pinned to `v0.9.0` could only fail or be switched off, since
the engine is supposed to move; a guard pinned to a recorded commit fails only when a change is
**unrecorded**. Changing the engine on purpose still requires bumping the version, adding a CHANGELOG
entry and updating the reference in the same commit -- the guard fails until that happens, which is
what makes the change a recorded act rather than a silent one. `test_the_comparator_detects_a_real_change`
proves the mechanism separates two differing files, so the check is demonstrated rather than asserted.

This does not amend `docs/V1-FREEZE.md`, which remains the owner's record of the archival reference;
the discrepancy between what it says and what the engine is stays disclosed in sections 2 and 3.

## 11. Stop condition

One audit, one reopening, one record. This is not a licence to re-run the project, and it does not
authorise a decay sweep, an intervention or a capability cell. Re-closing a reopened question needs
its own measurement and its own recorded build.
