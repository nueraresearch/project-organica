# Verification sweep — 2026-11-09

The `AGENTS.md` "Verifying a change" block lists eight commands. This sweep ran
the six that had not been exercised in this checkout during the current session,
and records what each reported. The other two (`python -m pytest tests -q` and
`python benchmarks/clone_check.py`) were already run; the suite is green at
**1630 passed, 6 skipped, 0 failed of 1636 collected** and `clone_check` is
**7/8**, which the last section explains.

Context: HEAD `1f9f713`, package version **0.13.0**, a fresh cloud worktree.
`memory.db` and `organica.log` are gitignored and **not present here**, which
decides two of the results below.

## What each command reported

| Command | Exit | What it reported |
|---|---|---|
| `python benchmarks/study_health.py` | **2** | `NO CYCLES PARSED - the daemon has not written a cycle summary yet` |
| `python benchmarks/lineage_audit.py` | **1** | `ERROR: <repo>/memory.db not found` |
| `python benchmarks/g5_gap_diagnostic.py --cycles 10` | 0 | Study stream peaks at **0** G5-eligible subjects and **0** theories; control stream peaks at **1** and **1** |
| `python benchmarks/cold_start.py --cycles 40` | 0 | Generation outcomes identical to the committed artifact for all 8 conditions (baseline reaches G5 at cycle 2, `cold_start` at 9, `real_git_history` at 34; three conditions never) |
| `python -m benchmarks.engine_stamp --check` | 0 | `engine stamp: 217 artifact writer(s) stamp, 17 artifact(s) grandfathered, 225 attributable` |
| `python benchmarks/ablation_study.py --cycles 300` | **1** | Crashes after four of eleven conditions; see below |
| `python benchmarks/clone_check.py` | **1** | 7/8; the deposit cannot archive `v0.12.0`, which is not on the remote |
| `python -m pytest tests -q` | 0 | Not re-run in this sweep; green at 1630 passed / 6 skipped / 0 failed of 1636 (2026-11-09) |

## The two live-substrate commands cannot report here

`study_health.py` and `lineage_audit.py` both read `memory.db`, and
`study_health` summarizes `organica.log`; both files are gitignored, so a fresh
checkout has neither. The first prints the answer it prints in any checkout with
no run yet, and exits 2; the second exits 1 naming the missing file. **These are
not repository failures and they are not evidence about the study.** Law II
(100% grounding) and the live duty cycle were not re-measured by this sweep, and
nothing here should be read as re-measuring them.

## `g5_gap_diagnostic --cycles 10`: finding reproduced, numbers not reproduced

Exit 0, and the substantive finding is unchanged: the study stream never makes
two expectations compete on one subject, so it peaks at 0 G5-eligible subjects
and 0 theories, while the control stream (same vocabulary in tight repeating
loops) reaches 1 and 1. The G5 gate is a property of the event stream, not of the
engine.

The numbers are not the committed artifact's. Against
`docs/g5_gap_diagnostic.json` (generated 2026-10-30), **1,132 of 1,885 leaf
values differ**, including `peak_experiment_priority` **0.8906 -> 2.0781**,
`mean_hypothesis_confidence` **0.6879 -> 0.7058**, and
`scaling.final_total_events` **2150 -> 839**. The committed artifact was
**restored unchanged**; this sweep did not overwrite it.

## `cold_start --cycles 40`: the outcome holds, the counts do not

Exit 0. The interpretive result reproduces exactly — the deepest generation each
condition reaches is identical to the committed artifact for all eight
conditions, so the claim "the organism bootstraps unaided, and the study stream
is what blocks G5" still stands.

The counts do not. **22 leaf values differ** from `docs/cold_start.json`
(2026-10-30): baseline `experience_events` **92,778 -> 8,313** and
`wall_seconds` **18.6 -> 2.7**, `unengineered_stream_size` **11 -> 400**, and
structure counts such as G1 predictions **20 -> 40** and G2 meta-concepts
**9 -> 15**.

This is not run-to-run noise. Two runs today agreed on **every non-timing leaf**
(8 timing leaves varied), and each agreed with the earlier run. The committed
artifact predates the engine changes of 2026-11-06 (`6c87f63` touched
`organica/sleep.py` and `organica/sleep_selection.py`), so its numbers are from
an older engine than the one it now sits beside. That is the likely cause; this
sweep did not prove it. **The committed artifact was restored unchanged** — a
stale record is a finding to disclose and regenerate deliberately, not to
overwrite with a fresh run.

## `engine_stamp --check` passes

Exit 0, `217 artifact writer(s) stamp, 17 artifact(s) grandfathered, 225
attributable`. The check also emits `SyntaxWarning: invalid escape sequence
'\s'` twice from `<unknown>:163`; the warnings do not affect the exit status.

## `ablation_study --cycles 300` fails

Exit 1. Four conditions completed and printed before the crash:

```
O_FULL  Full system    ES=59.440  PA=0.199  LC=1.000  NSR=0.942  (23.8s)
A       No Sleep       ES=0.000  PA=0.000  LC=  n/a  NSR=  n/a  (2.2s)
B       No Lineage     ES=59.440  PA=0.199  LC=0.000  NSR=0.942  (25.5s)
C       No Curiosity   ES=59.356  PA=0.199  LC=1.000  NSR=0.935  (23.4s)
```

then, inside condition D:

```
File "benchmarks/ablation_study.py", line 228, in _natural_selection
TypeError: NoFalsificationService._natural_selection() got an unexpected keyword argument 'meta_concepts'
```

The engine calls `_natural_selection` at `organica/sleep.py:315` with the five
positional arguments plus `meta_concepts`, `processes`, `roles`, `workflows`,
`schemas` and `hypotheses`; the definition is at
`organica/sleep_selection.py:102`. The harness's `NoFalsificationService` still
overrides the old signature `(prior, concepts, phrases, loops, predictions)`, so
the ablation layer no longer matches the engine it ablates. **Conditions D
onward were not measured, and no results artifact was written.** The harness was
not modified in this sweep: a verification run records what it finds.

## `clone_check` is 7/8, for a reason already identified

`benchmarks/deposit_bundle.py` archives `SOFTWARE_REF = "v0.12.0"`, and
`git ls-remote --tags origin` returns `v0.6.0`, `v0.7.0`, `v0.8.0`, `v0.9.0`,
`v0.10.0` and `audit-trace-v1` but **no `v0.12.0`**. The tag exists only in
local checkouts, so `git archive v0.12.0` fails in any fresh clone: 13 module
errors plus `test_a_missing_cited_artifact_is_detected`. The `--depth 1` clone
in `clone_check.py` was also a defect (it cannot run a suite that walks history)
and is fixed in the working tree. The check goes green once the tag is pushed.

## What this sweep did not do

- It did not re-run `pytest`, and it did not re-measure anything that needs the
  live substrate.
- It did not overwrite `docs/g5_gap_diagnostic.json` or `docs/cold_start.json`;
  both were restored to their committed state after the re-runs, which are kept
  in `.scratch/verify/` (gitignored and disposable).
- It did not change an engine file, a frozen artifact, a protocol, or a version.

## Second block — the campaign tooling

AGENTS.md's second list is the campaign tooling, "separate from the engine and safe to re-run". Six of
its sixteen commands are analysis over committed artifacts and all exit 0: `verdicts` (SUPPORTED 2 —
P1, P4; REVERSED 3 — P2, P3, P5; nothing NOT INTERPRETABLE), `discovery_report`,
`metric_sensitivity --matrix docs/force_matrix.json` (most surprising colony: NO_QUESTIONS, mean
relative distance 0.27764 raw / 0.18735 downstream), `phase_l_analyze --results docs/phase_l_results.json`
(the four criteria read False/False/True/True, `H3-L inconclusive`, and its own line "NO OUTCOME HERE
AUTHORISES A V2"), `phase_l_campaign --self-test` and `phase_k_campaign --self-test` (both report all
endpoints reachable; K1/K2/K3 perfect-model scores 1.000000).

The four simulation benchmarks run here reported:

| Command | Exit | What it reported |
|---|---|---|
| `python benchmarks/heldout_prediction.py` | 0 | `wrote /workspace/chats/41c104dc975752552e0b5d73/docs/heldout_prediction.json` |
| `python benchmarks/ground_truth_recovery.py` | 0 | `wrote /workspace/chats/41c104dc975752552e0b5d73/docs/ground_truth_recovery.json` |
| `python benchmarks/scale_ladder.py --cycles 300` | 124 | `rung 3s ...` |
| `python benchmarks/audit_trace_probe.py` | 0 | `wrote /workspace/chats/41c104dc975752552e0b5d73/docs/audit_trace_probe.json` |

`scale_ladder --cycles 300` is recorded as **exit 124** because it was stopped at this session's 65-second per-command cap: rungs 0-3 had completed (inventory 107-113, theories 0.82-0.85) and the sweep had not finished. **That is an incomplete run, not a verified command**, and it is listed with the campaigns below rather than with the benchmarks above.

`verdicts`, `discovery_report` and `metric_sensitivity` rewrote their committed JSON. The diffs were an
absolute path and the newly added engine-stamp fields — **no measured value moved** — and the committed
copies were restored, with the re-runs kept in `.scratch/verify/`.

**Not run, and why.** `run_matrix --cycles 3000`, `process_noise --sweep --cycles 3000`,
`phase_h_campaign`, `regime_shift`, `post_shift_adaptation`, the full `phase_k_campaign` and
`phase_k_diagnose --scale 4 --seeds 5` are campaigns of many seeds at thousands of cycles. Each far
exceeds this session's five-minute command budget, and each writes a result artifact that would have to
be adjudicated as a *new-engine experiment* under the direction recorded in
`docs/DECISION-V0.13.0-RELEASE.md` §5 — not silently produced here and read as a reproduction.


## Amendment — 2026-11-09: the ablation harness was repaired and all eleven conditions ran

The failure recorded above stands as the state of this checkout before the repair:
`ablation_study.py --cycles 300` exited 1 at condition D because
`NoFalsificationService._natural_selection()` did not accept the engine's `meta_concepts` keyword.

The harness was then repaired. The override now takes the engine's G1-G8 keyword set and re-stores
the composite generations untouched (no decay, no extinction), and both sides of the identity
comparison are built with `_candidate_key`. The second part also closes a latent mismatch: the old
override joined member lists unsorted while the engine's key sorts them, so a multi-member concept
could fail to match its prior copy and lose the reinforcement the arm is meant to keep.

Re-run: `ablation_study.py --cycles 300 --out docs/ablation_study_0.13.0.json` — exit 0, **11/11**
conditions, 266.6 s wall, artifact stamped `engine_version 0.13.0`, `engine_commit
6e0ff24d84d3`, `engine_sha256 ed0851d1...`, `generated_at 2026-11-09T03:01:52Z`.
`engine_stamp --check` passes (226 attributable). The committed `docs/ablation_study.json` was not
touched, and this sweep's original failure line is left as written.
