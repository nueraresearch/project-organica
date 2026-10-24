# Project Organica — Agent Guide

This file is the standing brief for any agent (or person) working on this repository. Read it before changing anything.

## What this project is

Project Organica is a research codebase for a *developmental* machine intelligence: a program that grows cognitive structures from a raw event stream through repeated sleep/consolidation cycles, rather than loading pre-trained weights. The full architecture, the nine emergence targets, the six design laws, and the current state of the 90-day longitudinal study are documented in:

- **`docs/USER-MANUAL.md`** — the owner's manual. Start here. It covers what the project is, how to run everything, how to read the telemetry, the action list, and troubleshooting.
- `research-journal/phase_g_findings_20261021.md` — the full research record (§1–§32), including the failures and the retractions.
- `CHALLENGE.md` — the nine emergence targets and the integrity constraint.
- `docs/DESIGN_LAWS.md` — the six inviolable laws.
- `docs/ABLATION-PREREGISTRATION.md` — the ablation study's predictions, written **before** the run. Do not edit §4 to match a result; amend and disclose instead.
- `docs/FORCE-MATRIX-PREREGISTRATION.md` — Ablation Study 2's frozen metrics, gates, sensitivity audit and noise floor. §1–§7 are committed **before** the campaign; §8 and §9 are the post-freeze records.
- `docs/FORCE-MATRIX-RESULTS.md` — the Tier-1 matrix results, the verdicts, and **H24**.
- `docs/FACTS-SHEET.md` — every claim with its provenance, separated from assumptions.
- `docs/EMERGENCE-CRITERIA.md` — what counts as emergence here, and which levels the project can currently evidence.
- `docs/PHASE-H-PREREGISTRATION.md`, `docs/REGIME-SHIFT-PREREGISTRATION.md`, `docs/PHASE-J-ADAPTATION-PREREGISTRATION.md`, `docs/PHASE-K-PREREGISTRATION.md` — the external-validity campaigns and the comparative-advantage search. **The protocol is committed before the run; do not edit it to match a result, amend and disclose instead.**

## Standing rule — keep the manual current

> **`docs/USER-MANUAL.md` must be updated in the same turn as any change it describes.**

This is not optional and not deferrable. Specifically, update the manual when any of these change:

- the daemon's running state or any metric in its status section
- a command, launcher, script, or path
- the meaning of a log field or snapshot artifact
- the study protocol or the emergence targets
- **the owner's action list** — when a decision is made, record it with a date and a one-line rationale
- a finding
- a troubleshooting symptom or fix
- a file's role in the file map

Also append a row to the manual's **Revision log** whenever you edit it.

Rationale: the manual is the single place the owner looks to answer "where are we at, what do I need to do, and what does this output mean". A stale manual is worse than no manual, because it is trusted. The research journal is the scientific record and is updated separately; the manual is the operational one.

## Rules that are not negotiable in this repo

1. **Generation 9 is locked.** Do not implement self-modeling. The project exists to earn it.
2. **Phase A froze the cognitive primitives at v1.0.** Do not change *which* structures compete, how confidence is computed, or how the layers select candidates without an explicit recorded decision. Substrate and measurement changes are fine; cognition changes need a decision first. There is a known pending amendment (journal §7) — do not silently apply it.
3. **Never truncate `organica.log`.** It is the longitudinal record and is append-only. The daemon owns it through its logging `FileHandler`.
4. **The sleep-cycle counter must stay monotonic.** `organica/memory.py` keeps it in the `sleep_cycles` table. Do not reintroduce a sliding-window read of the events table for this — that was the bug that reset the counter mid-run.
5. **Substrate changes must be behaviour-preserving and proven so.** `tests/test_substrate_equivalence.py` is the pattern: if you change how anything is read or written, add a test showing the result is identical to the old behaviour.
6. **Do not commit or push without being asked.** The owner authorises commits and pushes as a standing arrangement, but still expects to be asked before a release is tagged or published. Work may sit uncommitted by design until they say otherwise.
7. **Do not add third-party runtime dependencies.** The core is standard library only.
8. **Do not name a colony after something it does not do.** `NO_CONTRADICTIONS` removes contradiction's *weight in the confidence formula*, not contradictions; the name overstates the intervention and the discrepancy is disclosed in the results document. If a new arm needs a name that a reader would take literally, name it for the mechanism it actually changes.
9. **Tags must be ≥ 4 letters.** The engine extracts tags with `re.findall(r"\b[a-zA-Z]{4,}\b", ...)`, so a stimulus word of three characters or fewer is invisible to the entire substrate. A ladder whose leaves are silently dropped measures nothing and looks like a null result.
10. **The package version must describe the commit it is on.** If `v<version>` exists as a tag, it must point at the current commit. Master drifting past a published tag while still declaring that version means the version names a release that master is not, and anyone installing from master gets a different artifact under the same number. Bump the version (`organica/__init__.py`, `pyproject.toml`, `CITATION.cff`) and add the changelog entry. A version whose changelog heading says `(unreleased)` is allowed to have no tag yet — there is nothing to check out. `tests/test_versioning.py` enforces both halves.
11. **A baseline may never be handicapped, and every harness needs a control it can fail.** Every simple baseline is swept over a declared hyperparameter grid and its *best* score is the number used. A benchmark that a strong baseline cannot solve is not evidence of anything — Phases H, I and J each failed against baselines that were given no tuning advantage at all — and a strawman baseline is the easiest way to manufacture a false positive. Where a protocol builds a harness, it must build a control the harness can fail: Phase K's K0 reruns the Phase H task, where Organica's loss is already known, and the campaign does not run if that control fails.

## If a study run is live, the engine is frozen

A live run is one constant engine plus one constant stimulus. While the daemon is running against `memory.db`:

- **Do not change `organica/sleep.py` or the semantics of `organica/memory.py`.** That ends the run; the old one must be archived and a fresh database started.
- **Do not change the event stream in `organica/streams.py`.** A different stimulus is a different experiment.
- **Performance-only substrate changes are allowed only if a test proves the result is identical.** That is what `tests/test_substrate_equivalence.py` is for.
- Everything else — harness, metrics, dashboards, API, benchmarks, examples, docs — is free to change.

Pausing and restarting the daemon are both fine: the counter is monotonic and the log appends across restarts. Note any pause in the write-up, because the organism did not experience the missing wall-clock time.

**Never let a script write to the live `memory.db`.** Use `organica.paths.scratch_db()` for anything disposable. Several example scripts used to open `Path("memory.db")` in the working directory, which would have deleted the live study's substrate; they now write to `.scratch/`.

See `docs/USER-MANUAL.md` §6.4 for the full table.


## Verifying a change

```bash
python -m pytest tests -q                 # 42 tests, must be green
python benchmarks/study_health.py          # study must stay healthy
python benchmarks/lineage_audit.py         # Law II must stay at 100% grounded
python benchmarks/g5_gap_diagnostic.py --cycles 10   # G5 must remain reachable
python benchmarks/cold_start.py --cycles 40          # unassisted bootstrap
python benchmarks/clone_check.py           # a fresh clone works end to end
python benchmarks/ablation_study.py --cycles 300     # the ablation suite (~25 min)
```

The campaign tooling is separate from the engine and is safe to re-run:

```bash
python benchmarks/run_matrix.py --cycles 3000         # the Tier-1 matrix
python benchmarks/metric_sensitivity.py --matrix docs/force_matrix.json
python benchmarks/process_noise.py --sweep --cycles 3000   # the measured floor
python benchmarks/verdicts.py                        # the pre-registered predictions
python benchmarks/discovery_report.py                # the inventory and discovery curves
python benchmarks/scale_ladder.py --cycles 300       # the H24 world-complexity ladder
python benchmarks/heldout_prediction.py              # Organica vs Markov vs decayed, held out
python benchmarks/ground_truth_recovery.py           # structure recovery vs hidden causes
python benchmarks/phase_h_campaign.py                # Phase H, 10 seeds
python benchmarks/regime_shift.py                    # Phase I, 20 seeds x 2 families
python benchmarks/post_shift_adaptation.py           # Phase J, 20 seeds x 2 families
python benchmarks/phase_k_campaign.py --families K1 K2 K3 --seeds 10 --workers 3
```

The study daemon may be running against `memory.db`. Prefer read-only inspection, or work on a copy, so you do not disturb a multi-week run.

**Ablations are applied in-process.** `benchmarks/ablation_study.py` subclasses `SleepService` / `MemoryService` and overrides methods; it never edits `organica/sleep.py` or `organica/memory.py`. Keep it that way — it is what lets the live study stay auditable while the ablations run.
