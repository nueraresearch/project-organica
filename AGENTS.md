# Project Organica — Agent Guide

This file is the standing brief for any agent (or person) working on this repository. Read it before changing anything.

## What this project is

Project Organica is a research codebase for a *developmental* machine intelligence: a program that grows cognitive structures from a raw event stream through repeated sleep/consolidation cycles, rather than loading pre-trained weights. The full architecture, the nine emergence targets, the six design laws, and the current state of the 90-day longitudinal study are documented in:

- **`docs/USER-MANUAL.md`** — the owner's manual. Start here. It covers what the project is, how to run everything, how to read the telemetry, the action list, and troubleshooting.
- `research-journal/phase_g_findings_20261021.md` — the full research record (§1–§38), including the failures and the retractions.
- `docs/phase_l_results.md` — the Phase L V1 result: the primary-axis curve, the four pre-committed criteria, and the `H3-L — INCONCLUSIVE` verdict. Read this before proposing anything that follows Phase L.
- `docs/V1-SYNTHESIS.md` — the formal synthesis of V1: what was established, what was not, and the question the evidence leaves open. **Read this before proposing the next phase.** It adds no new evidence; it is a reading of the record.
- `CHALLENGE.md` — the nine emergence targets and the integrity constraint.
- `docs/DESIGN_LAWS.md` — the six inviolable laws.
- `docs/ABLATION-PREREGISTRATION.md` — the ablation study's predictions, written **before** the run. Do not edit §4 to match a result; amend and disclose instead.
- `docs/FORCE-MATRIX-PREREGISTRATION.md` — Ablation Study 2's frozen metrics, gates, sensitivity audit and noise floor. §1–§7 are committed **before** the campaign; §8 and §9 are the post-freeze records.
- `docs/FORCE-MATRIX-RESULTS.md` — the Tier-1 matrix results, the verdicts, and **H24**.
- `docs/FACTS-SHEET.md` — every claim with its provenance, separated from assumptions.
- `docs/EMERGENCE-CRITERIA.md` — what counts as emergence here, and which levels the project can currently evidence.
- `docs/PHASE-H-PREREGISTRATION.md`, `docs/REGIME-SHIFT-PREREGISTRATION.md`, `docs/PHASE-J-ADAPTATION-PREREGISTRATION.md`, `docs/PHASE-K-PREREGISTRATION.md`, `docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md` — the external-validity campaigns, the comparative-advantage search, and the plasticity–coherence measurement. **The protocol is committed before the run; do not edit it to match a result, amend and disclose instead.**
- `docs/V1-FREEZE.md` — the Organica 1 freeze: what is frozen, what is not, and why it is enforced rather than declared.

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
12. **Organica 1 is frozen.** The `v0.9.0` tag is the archival reference. Do not modify the frozen engine files — `organica/sleep.py`, `memory.py`, `paths.py`, `streams.py`, `branch_streams.py`, `scale_streams.py`, `ground_truth_worlds.py` — nor the published result artifacts. `tests/test_v1_freeze.py` enforces this and fails if one differs. Benchmarks, harnesses, documentation, the action list and the owner's decisions all stay free; Phase L lives entirely in `benchmarks/`. The one boundary rule: nothing may change the **behaviour** of the frozen engine. See `docs/V1-FREEZE.md`.
13. **An audit of the metric is not an audit of the design, and an unmeasurable quantity is not a zero.** The Phase L pilot returned `DI = 0.000` at every point of the sweep — a clean-looking negative result that was entirely an artefact, because the late group arrived after the run had ended and the late structure was never available. The two existing audits both passed on that world, because they checked the *metric* and the metric was perfect; the *design* was dead. Three rules follow. **(a)** A harness must also audit that its independent variable actually varies what it claims to vary — that the arms differ, that the manipulated quantity is present in the world, and that every condition has a denominator to measure against. Phase L's degeneracy audit does this, and the campaign does not run if it fails. **(b)** A ratio with a zero denominator is **not measurable**, and must be reported as not measurable and **excluded** — never as `0.0`. Reporting "nothing was retained" for a condition in which nothing was available to retain is a fabrication, and it is the same failure as Phase K's collapsed harmonic mean. **(c)** An identical value at every point of a sweep is a measurement defect until proven otherwise: check that the axis is live before reading the sweep as a result.

14. **A criterion set is judged whole, and a stable headline statistic is not a substitute for a criterion that failed.** Phase L's primary axis produced a crossing at 3:1 that survived everything — a 10,000-replicate paired bootstrap put it at [5.0, 5.0] with every replicate finding it, eight alternative bootstrap seeds all returned `INTERIOR`, and leave-one-seed-out left it at 3:1 in 10 of 10 folds — and the phase still could not claim a boundary, because one of the four pre-committed criteria (*PI is monotone decreasing*) was not met. **The number of criteria satisfied is not a score**, and a phase that reports "three of four, and the missing one was incidental" has re-scored its own protocol after the fact. The criterion was evaluated once by the committed code and it failed; it was not re-read, relaxed, or reinterpreted afterwards. The same applies to the wording of the outcome buckets: when a label and its stated rationale come apart — the `H3-L` bucket is described as *"intervals too wide to place RT"*, which is not what happened — record the gap and do not exploit it. **A protocol's job is to be inconvenient, and the moment it becomes convenient it has stopped being one.**
15. **A criterion that flips when n changes is measuring the draw, not the organism — and a criterion set that only a few percent of random draws satisfy is not a bar.** Phase L's primary axis was re-run at n=30 (the protocol's own remedy for `H3-L`, "raise n"), and the verdict came back `H3-L — INCONCLUSIVE` again, with **two** of the four criteria unmet — because *DI monotone increasing*, which was **met** at n=10, is **not met** at n=30. The Revision Threshold did not move at all (3:1, [5.0, 5.0], 10,000/10,000 replicates, leave-one-seed-out 3:1 in 30 of 30 folds), and the reason the monotone criteria fail is that the displacement curve is a **step function**: DI is exactly 0.000 across 1:4–1:1 for every seed and saturates at DI ≈ 0.71 across the top, so both failing criteria are sign tests on adjacent differences whose 99% paired intervals contain zero. Resampling the 30 measured seeds settles the diagnosis cheaply: the two *stable* criteria (DI range, interior crossing) hold in **100%** of random subsets, the two monotone ones in **7–19%**, and all four together in **0–2.9%**. **Apply when:** a criterion set must be judged whole — but before treating a pass *or* a fail as a property of the system, ask **how often does this criterion hold across random subsets of the data already in hand?** That question is cheap, it converts a verdict into a characterisation, and it distinguishes "the organism does not have this property" from "this test cannot see a property the organism has". Corollary: never let a headline statistic stand in for a criterion that failed, and never let "raise n" quietly become "raise n until it says what I want" — when raising n has stopped changing the thing being measured, say that the remedy is exhausted rather than raising n again.

16. **A protocol verdict and a scientific characterisation are different artefacts, and publishing one must not re-score the other.** Phase L's primary axis ended at `H3-L — INCONCLUSIVE` while the *shape* of what was measured was unambiguous: the displacement curve is a step function, not a ramp — a preservation plateau (DI **exactly 0.000** for every seed across 1:4–1:1), a transition region, and a displacement plateau — separated by a reproducible transition whose location (3:1) is stable under every resampling the campaign could run. Both facts are true, and they live in different documents: the measurement record (`docs/phase_l_results.md`) carries the verdict, the synthesis (`docs/PHASE-L-SYNTHESIS.md`) carries the characterisation, and neither re-scores the other. **Apply when:** a phase ends and the result is more interesting than the verdict. Write the characterisation as its own artefact, keep the verdict intact and visible inside it, and name the two merges a reader will want to make: **(a)** *a stable, reproducible threshold is not a boundary* — a threshold divides a continuum only if the trade-off is a continuum, and this curve is flat on both sides of the crossing; **(b)** *raising n is exhausted* — the reason to raise n was to separate "the tiny reversal is noise around a monotone curve" from "the curve is genuinely step-shaped", and n=30 separated them, so more seeds would change nothing. Corollary: "regime" describes the shape of a displacement index, a preservation index and a latency on synthetic worlds — **it is not a claim about intelligence**, and a better story is never a licence to re-score a criterion that failed.

17. **A count must be named as what it counts; a trace is not a counterfactual; and observation must be proven behaviour-neutral.** The audit-trace specification (`docs/AUDIT-TRACE-SPEC.md`) exists because the next question for a developmental learner is *"how do we know it learned the right thing?"* — and the answer cannot come from asking the organism. Three rules follow from writing that specification against the real engine. **(a) Name the quantity.** The engine's `support_count` counts **temporal transitions**, and `contradiction_count` is the subject's **competing flow** — *not* a count of observations that contradicted the claim. A record that calls 12 transitions "12 observations" and 4 competing transitions "4 contradictions" puts a false claim at the centre of the audit, which is the one place a false claim cannot be afforded. **Apply when:** a number is copied into a report, a prompt, a model input or a paper — carry the unit with the number. **(b) A trace records what happened; a replay records what would have.** *"Candidate B would have survived without A"* is a counterfactual, and needs a separate run, a separate artifact and its own label. It can never be a field of the trace. **(c) An observer that changes behaviour is not an observer.** Where a trace needs a hook inside the engine, the build must be labelled separately and must demonstrate that recording the trace leaves the engine's outputs unchanged, with the check built to fail and proved to fire. Corollary: **prefer assembly over instrumentation.** On this engine the entire selection contest is reconstructible externally under the default `salience` policy, so no hook is needed at all — and reaching for one first would have meant trusting the engine less than it deserves to be trusted, while adding risk.

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
python -m pytest tests -q                 # 69 tests, must be green
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
python benchmarks/phase_k_diagnose.py --scale 4 --seeds 5   # the K3 root cause
python benchmarks/phase_l_campaign.py --self-test   # the Phase L instrument audits
python benchmarks/phase_l_analyze.py --results docs/phase_l_results.json
python benchmarks/audit_trace_probe.py --cycles 60  # the audit-trace reconstruction probe
```

The study daemon may be running against `memory.db`. Prefer read-only inspection, or work on a copy, so you do not disturb a multi-week run.

**Ablations are applied in-process.** `benchmarks/ablation_study.py` subclasses `SleepService` / `MemoryService` and overrides methods; it never edits `organica/sleep.py` or `organica/memory.py`. Keep it that way — it is what lets the live study stay auditable while the ablations run.
