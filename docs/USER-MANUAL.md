# Project Organica — Owner's Manual

> **Audience:** Jeremy (project owner). This is the single document that tells you what the project is, what state it is in, how to run it, how to read its output, and what you personally need to decide and do.
>
> **Currency:** This manual is maintained live. Every change to the project's state, commands, findings, or your action list must be reflected here **in the same turn it happens** — see [§18 Keeping this manual current](#18-keeping-this-manual-current).

---

## Table of contents

1. [Five-minute quickstart](#1-five-minute-quickstart)
2. [Where things stand right now](#2-where-things-stand-right-now)
3. [What Organica actually is](#3-what-organica-actually-is)
4. [Running everything](#4-running-everything)
5. [Reading the output](#5-reading-the-output)
6. [What the study is measuring](#6-what-the-study-is-measuring)
7. [What you need to do](#7-what-you-need-to-do)
8. [The ten findings, and what each means for you](#8-the-ten-findings-and-what-each-means-for-you)
9. [Troubleshooting](#9-troubleshooting)
10. [File map](#10-file-map)
11. [Vocabulary](#11-vocabulary)
12. [Abbreviations and acronyms](#12-abbreviations-and-acronyms)
13. [Data dictionary](#13-data-dictionary)
14. [The eight layers, in detail](#14-the-eight-layers-in-detail)
15. [The formulas, with worked examples](#15-the-formulas-with-worked-examples)
16. [Metric cheat sheet](#16-metric-cheat-sheet)
17. [Common misreadings](#17-common-misreadings)
18. [Keeping this manual current](#18-keeping-this-manual-current)

---

## 1. Five-minute quickstart

```bash
cd C:\Users\monte\anti\project-organica

# Is the study alive and healthy? (30 seconds, do this first)
python benchmarks/study_health.py

# Start the daemon if it is not running
start_organica.bat

# Watch it work
Get-Content organica.log -Wait -Tail 20      # PowerShell
tail -f organica.log                          # bash / git-bash
```

The one-line summary you want to see:

```
daemon              : ALIVE - PID <n> since <time>
sleep_cycle 1..N    : non-monotonic steps: 0   OK
G5 duty cycle       : 100.0%
failed cycles       : 0
```

**Full picture in 3 commands:**

| Goal | Command |
|---|---|
| Health / status | `python benchmarks/study_health.py` |
| Watch it grow from nothing | `python build.py` |
| The full Phase G findings | `research-journal/phase_g_findings_20261021.md` |
| The research write-ups | `papers/` and `research-journal/` |
| Brand new to this project? | `GETTING-STARTED.md` |

---

## 2. Where things stand right now

**As of 2026-10-22 13:40 MDT** (this section is refreshed on every manual update):

| | |
|---|---|
| Study status | **RUNNING** — daemon PID 19916, since 2026-10-21 11:21 MDT |
| Cycles completed | 3,423 |
| Sleep-cycle counter | 1 → 3,423, **0 non-monotonic steps** |
| G5 duty cycle (last 200 cycles) | **100.0%** (theories and questions) |
| Cycle latency | median 282 ms, max 584 ms |
| Failed cycles | 0, all time |
| Substrate | 15.2 MB, bounded by retention (≈109 rows pruned/cycle) |
| Mean population | 13.0 hypotheses, 8.0 dreams, 1.0 theories, 1.0 questions |
| Lineage (Law II) | 100% grounded, 0 unverifiable, 0 ungrounded |
| Git | `master` is **3 commits ahead of `origin/master`**, unpushed — see [§7.1](#71-do-today) |
| Cold-start study | **complete** — see [§8.1](#81-the-cold-start-study) |
| Ablation study | **complete** — see [§8.2](#82-the-ablation-study-which-mechanisms-are-actually-doing-the-work) |

**The headline:** the 90-day longitudinal study is running, healthy, and recording continuous Generation-5 activity. The first attempt (2026-10-20) was invalid and has been diagnosed; see [§8](#8-the-ten-findings-and-what-each-means-for-you).

**The long-horizon answer:** the cold-start ablation is done. The organism bootstraps G1, G4, G6, G7 and G8 from an unengineered stream with no assistance — but **G5 never emerges unassisted**, and the cause is now *proven causal*, not guessed. Read [§8.1](#81-the-cold-start-study) before you decide anything about the architecture.

**The unflattering answer:** the ablation study is also done, and it says that most of the architecture's layers are not load-bearing. Sleep and the substrate graph are foundational. **Lineage changes nothing at all except auditability.** The attention economy changes what it selects without changing what the organism achieves. Read [§8.2](#82-the-ablation-study-which-mechanisms-are-actually-doing-the-work) — it is the most important section in this manual for your next decision.

> **Read the status table this way:** `sleep_cycle` monotonic and `failed cycles` at 0 mean the *machinery* is sound. `G5 duty cycle` at 100% means the *experiment* is valid — a run can be perfectly healthy and still be measuring nothing (see [§17](#17-common-misreadings)).

---

## 3. What Organica actually is

**One paragraph:** Organica is a program that tries to grow a mind instead of loading one. It ingests a raw event stream (timestamps and text, no schema), builds a graph of which tags co-occur and which tend to follow which, and then repeatedly "sleeps" — a cycle that reads the graph, proposes higher-order structures, tests them against the evidence, and lets the ones that don't hold up decay and die.

The important claim is not that it works well. It's that **every structure it holds must trace back to raw experience through unbroken parent links** (Law II), and that it **never hard-codes a cognitive concept** (Law I) — concepts, loops, workflows, hypotheses, theories, questions, dreams, investigations and experiments are all supposed to emerge from the layer below.

**The developmental ladder** (from `CHALLENGE.md` and `docs/developmental-ladder.md`):

```
[Gen 0] Events (Experience Stream)
  ↓
[Gen 1] Concepts, Predictions & Loops
  ↓
[Gen 2] Process Candidates & Meta-Concepts
  ↓
[Gen 3] Workflow Concepts
  ↓
[Gen 4] Hypothesis Candidates          (falsifiable A → B)
  ↓
[Gen 5] Theory & Question Candidates   ← epistemic tension, Shannon entropy
  ↓
[Gen 6] Categorized Dreams             (completion, analogy, mutation, conditional)
  ↓
[Gen 7] Investigation Candidates        (ranked by Expected Information Gain)
  ↓
[Gen 8] Experiments                    (concrete, executable interventions)
  ↓
[Gen 9] Self-Modeling                  ← LOCKED until the study concludes
```

**The six design laws** (`docs/DESIGN_LAWS.md`) are the constitution. The three that matter most for reading the data:

- **Law I — Strict upward layer induction.** Layer N+1 only ever operates on Layer N's output.
- **Law II — 100% verified structural provenance.** Everything traces to Generation 0. *Verified — see [§8, finding 8](#8-the-ten-findings-and-what-each-means-for-you).*
- **Law V — Epistemic attention (EIG over confidence).** The organism spends effort where *uncertainty* is, not where it's already certain. `EIG = Uncertainty × (1 + Novelty)`.

**Generation 9 is deliberately locked.** The whole point of the current study is to earn it.

---

## 4. Running everything

Everything lives in `C:\Users\monte\anti\project-organica`. Open a PowerShell there.

### 4.1 The study daemon

```bat
start_organica.bat
```

Launches `run_continuous.py` in the background. It writes one JSON summary line per cycle to `organica.log` and never truncates it. The cycle interval is 30 seconds (override with a file named `INTERVAL` containing a number of seconds).

| Behaviour | Detail |
|---|---|
| Log | `organica.log` — **appended**, never truncated |
| Console mirror | `console.log` |
| Database | `memory.db` (SQLite) |
| Working memory | newest 4,000 sleep events |
| Candidate retention | newest 20,000 (bounded; older ones evicted) |
| Stop | `Stop-Process -Id <pid> -Force` — see [§9](#9-troubleshooting) |

### 4.2 Making it survive 90 days ⚠️

**The daemon is stable but unprotected.** It is a `start /b` child of a transient console, and this machine's own shell history contains broad `Get-Process python | Stop-Process -Force` sweeps. Run 1 died exactly that way — not a bug, but it will cost you the study.

A Windows Scheduled Task fixes it: it survives console close and logoff, and restarts the daemon if it exits.

```powershell
$action  = New-ScheduledTaskAction -Execute 'C:\Users\monte\.local\bin\python.exe' `
                                   -Argument 'C:\Users\monte\anti\project-organica\run_continuous.py' `
                                   -WorkingDirectory 'C:\Users\monte\anti\project-organica'
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
                                     -RepetitionInterval (New-TimeSpan -Minutes 1) `
                                     -RepetitionDuration (New-TimeSpan -Days 95)
$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
                                          -ExecutionTimeLimit (New-TimeSpan -Days 95) `
                                          -StartWhenAvailable -DontStopIfGoingOnBatteries `
                                          -AllowStartIfOnBatteries
Register-ScheduledTask -TaskName 'OrganicaStudy' -Action $action -Trigger $trigger `
                       -Settings $settings -Description 'Project Organica 90-day longitudinal study' `
                       -RunLevel Highest
```

Stop and remove it later:

```powershell
Stop-ScheduledTask -TaskName 'OrganicaStudy'
Unregister-ScheduledTask -TaskName 'OrganicaStudy'
```

### 4.3 Observation snapshots

```bat
run_daily_observer.bat      :: daily snapshot + appends new events to the journal
run_weekly_monthly.bat      :: weekly aggregate + monthly genome + velocity
```

Outputs land in `snapshots/`:

| File | Contents |
|---|---|
| `snapshots/daily/daily_YYYYMMDD.json` | populations, births/deaths over the trailing 24 h, latest cycle |
| `snapshots/weekly/weekly_YYYYMMDD.json` | aggregate over the trailing 7 days, largest births/deaths |
| `snapshots/monthly/monthly_YYYYMMDD.json` | belief population + hypothesis lifecycle + dream distribution |
| `snapshots/velocity/velocity_YYYYMMDD.json` | new theories/questions/dreams/experiments per day over 7 days |
| `snapshots/event_journal.log` | append-only structural event log (theory births/deaths, hypothesis births/deaths, generation milestones) |

These are **time-window based**, not cycle based: "today" means the trailing 24 hours, "this week" means the trailing 7 days. The writers refuse to write an empty artifact — if there is no data, they write nothing and say so.

**Set these on a schedule too.** The same Scheduled Task pattern works; run them hourly or daily and the study will accumulate a real longitudinal record without you remembering.

### 4.4 Dashboards and API

```bat
run_dashboard_and_api.bat
```

- **Inception API** — `inception_api.py`, exposes health metrics and accepts injected payloads at `/inception`. The Streamlit UI uses it to inject seed events (Auth Failure, Contradictory Belief, Dream Trigger, or a custom JSON payload).
- **Streamlit UI** — `dashboard_ui.py`, the live health dashboard.
- `dashboard.py` is the older CLI dashboard; `study_health.py` is the current command-line health tool and is what to trust.

### 4.5 Audits and analyses

| Tool | What it answers |
|---|---|
| `python benchmarks/study_health.py` | Is it alive? Is the counter monotonic? Latency? G5 duty cycle? |
| `python benchmarks/g5_gap_diagnostic.py --cycles 10` | Can this stream reach Generation 5, and what is the ceiling on theories? |
| `python benchmarks/lineage_audit.py` | Does every candidate actually resolve to a Generation 0 experience event? (Law II) |
| `python benchmarks/substrate_probe.py` | What does the substrate cost per cycle, and is the database bounded? |
| `python benchmarks/stream_sweep.py` | Scores candidate event streams on G5 sustainment and EIG |
| `python benchmarks/cold_start.py --cycles 40` | **Would the organism bootstrap later generations with no help?** Ablates pre-seeding, the engineered branch point, the lookback window and the hypothesis cap. |
| `python benchmarks/benchmark_suite.py` | BM1–BM5 growth benchmarks |
| `python benchmarks/cross_domain_validation.py` | Phase F: the four reproduction domains, writes `docs/validation_report.json` |
| `python -m pytest tests -q` | The test suite (17 tests) |

### 4.6 The four reproduction domains

```bash
python examples/domains/01_developer_workflow.py
python examples/domains/02_bug_tracking.py
python examples/domains/03_synthetic_ecology.py
python examples/domains/04_robot_simulation.py
```

Each runs a short, self-contained emergence demo in its own world, in about a second.

### 4.7 Building an organism from nothing

```bash
python build.py
```

**This is the one command you give a stranger.** It creates an empty substrate, feeds it the study stream, runs the sleep cycles, and prints the full developmental ladder, the Law II integrity check, and whether Law V's attention economy ever engaged. It writes only to `.scratch/` — your live `memory.db` is never touched.

```
python build.py --all              # every domain, not just the study stream
python build.py --domain robot_simulation
python build.py --cycles 25        # longer run (default 12)
python build.py --keep             # keep the scratch DB for inspection
```

Verified output on the current build: 48 events in, ladder reaching **G8**, **100% lineage**, **G5 reached**, uncertainty **1.000**, top priority **1.500**.

`GETTING-STARTED.md` is the stranger-facing version of the same thing, and `README.md` links to it.

---

## 5. Reading the output

### 5.1 The log line

Every cycle appends one line to `organica.log`:

```
2026-10-21 11:31:00,123 INFO Cycle 42: {"cycle": 42, "sleep_cycle": 285, "timestamp": "2026-10-21T17:31:00Z", "status": "success", ...}
```

| Field | Meaning | Watch for |
|---|---|---|
| `cycle` | counter **since the last daemon start** | resets to 0 on restart — *not* the global counter |
| `sleep_cycle` | **global** counter, survives restarts | must increase by 1 every line; a reset means the counter bug is back |
| `timestamp` | UTC wall clock of the cycle | the anchor for every time-window metric |
| `status` | `success` or `failed` | anything other than `success` is an error |
| `duration_ms` | wall time of the sleep cycle | should be ~150–300 ms; drift upward = substrate degrading |
| `consecutive_errors` | error streak | should stay 0 |
| `concepts` `predictions` `loops` | Gen 1 populations | |
| `hypotheses` | Gen 4 population | 13–15 in a healthy run |
| `hypothesis_snapshot` | per-hypothesis `id`, `subject`, `confidence`, `support_count`, `contradiction_count` | the raw material for every belief-revision metric |
| `theories` `questions` | Gen 5 populations | **0 here means the study is invalid** — see finding 1 |
| `dreams` `dream_categories` | Gen 6 | `conditional` dreams only appear when there are uncertain Questions — a good sign |
| `investigations` `experiments` | Gen 7 / Gen 8 | |
| `composites_created` `total_composites` | cumulative structure count | |
| `candidates_strengthened` `candidates_pruned` | Law VI selection pressure | `pruned` ≫ `strengthened` is normal |
| `substrate_rows_pruned` | rows evicted by retention | should be a steady non-zero number, not zero |

### 5.2 The headline metric: G5 duty cycle

**Do not read "theories > 0" as a per-cycle yes/no.** The organism oscillates between a G4 fixed point and a G5 state, so the right metric is a **duty cycle over a rolling window**:

```
G5 duty cycle = fraction of the last 200 cycles that carried at least one Theory
```

`study_health.py` prints it. Current value: **100.0%**.

> **Why this matters:** in the first (invalid) run the same metric read ~0%. A number that reads 0% and a number that reads 100% look similar in a snapshot — one is a dead study, the other is a healthy one. Always report the window, not a single cycle.

### 5.3 The snapshots

`snapshots/daily/*.json` is the artifact to look at when you want "how is the organism doing today":

```json
{
  "cycle": 285, "timestamp": "2026-10-21T17:31:00Z",
  "active_concepts": 2, "active_hypotheses": 13, "active_theories": 1, ...
  "births_today": 963, "deaths_today": 919,
  "window_hours": 24.0, "cycles_in_window": 200
}
```

`snapshots/event_journal.log` is the narrative record — one JSON object per structural event:

```json
{"event": "theory_birth", "cycle": 285, "timestamp": "...", "subject": "developer"}
{"event": "hypothesis_death", "cycle": 284, "timestamp": "...", "id": "hyp_..."}
{"event": "generation_milestone", "cycle": 12, "generation": "questions"}
```

It is idempotent — running the observer twice appends nothing the second time.

### 5.4 The lineage audit

```bash
python benchmarks/lineage_audit.py
```

Reports how many candidates resolve to an actual Generation 0 experience event, and separates the two ways a chain can fail:

- **GROUNDED** — the chain resolves to a Layer 1 anchor whose tags appear in a real experience event. This is the only good outcome.
- **UNVERIFIABLE** — the chain was broken because an intermediate candidate was *evicted* by bounded retention. Not a lineage failure, but not provable either.
- **UNGROUNDED** — the chain resolves, but the Layer 1 anchor's tags appear in no experience event. This is a genuine violation.

Current: **100% grounded, 0 unverifiable, 0 ungrounded.**

---

## 6. What the study is measuring

### 6.1 The nine emergence targets

`CHALLENGE.md` defines success as all nine emerging **without hand-coded domain knowledge**:

| | Target | How you see it in the data |
|---|---|---|
| G0 | Pure experience | raw events in the DB, no schema assumed |
| G1 | Signal extraction | `concepts`, `predictions`, `loops` > 0 |
| G2 | Composites | meta-concepts and 2–3 cycle processes |
| G3 | Workflows | multi-anchor sequences |
| G4 | Falsifiable hypotheses | `hypotheses` > 0, with support/contradiction counters |
| G5 | Epistemic tension | `theories` > 0 **and** `questions` > 0, with non-zero uncertainty |
| G6 | Grounded dreams | `dreams` > 0, including `conditional` dreams |
| G7 | Attention economy | `investigations` > 0, ranked by EIG |
| G8 | Active experiments | `experiments` > 0 with a real priority spread |

Plus the **integrity constraint**: 100% of candidate nodes resolve their parental ancestry back to Generation 0.

### 6.2 What G5 means, precisely

G5 is the pivot of the whole architecture. Layer 5 coalesces **two hypotheses about the same subject with competing expectations** into a Theory, and scores the Shannon entropy of that split as the Question's uncertainty.

That means G5 requires the organism to hold *two contradictory beliefs about one thing*. Concretely, in the current study stream, "developer executed test suite" is followed sometimes by a failures report and sometimes by a passed report — so "developer" carries two expectations, and the organism must notice.

**G5 is where the EIG economy gets its fuel.** Zero contradictions → zero entropy → zero EIG → the attention economy is dead even though the counters all look "fine". This is the single most important thing to understand about the telemetry: *a run can look healthy and be epistematically inert.*

### 6.3 What the study deliberately does not yet do

- **It does not execute experiments.** G8 produces *candidates*; nothing runs a probe against the world and measures whether a belief moved. So a Question can never actually close — the study measures **epistemic tension**, not **epistemic resolution**. (Finding 9.)
- **It does not use Generation 9.** Self-modeling is locked until the study concludes.
- **It does not yet touch a real external world.** The stream is synthetic and fixed, so it measures development, not usefulness.

### 6.4 Rules for a clean run

**A "run" is one constant engine plus one constant stimulus.** That is the whole definition, and it decides every question about whether a change ruins the experiment.

| Change | Ruins the run? | Why |
|---|---|---|
| `organica/sleep.py` — any change to the cognitive pipeline | **YES** | The organism's behaviour changes mid-history. Archive and start fresh. |
| `organica/memory.py` — a change to substrate *semantics* | **YES** | Same: the substrate is part of the organism. |
| `organica/memory.py` — a **performance-only** change proven behaviour-preserving | **No** | If a test proves the result is identical, the organism cannot tell. (This is why `tests/test_substrate_equivalence.py` exists.) |
| The event stream in `organica/streams.py` | **YES** | A different stimulus is a different experiment. |
| `run_continuous.py` log fields, `metrics.py`, `observation/`, `dashboard*`, `inception_api.py` | **No** | Measurement and presentation only. The daemon does not import them. |
| `benchmarks/`, `examples/`, `docs/`, `papers/`, this manual, LICENSE, CI | **No** | No effect on the running organism. |
| **Pausing** the daemon (stop it, leave the DB and log, start it later) | **No** | The counter is monotonic and the log appends, so a pause is a gap in wall-clock time, not a corruption. *Record the gap* — the organism did not experience the missing time. |
| **Restarting** the daemon after a crash or reboot | **No** | The counter and log survive restarts. This is exactly what the Scheduled Task's restart-on-failure relies on. |
| Running an **example script** | **No** — and now impossible | Examples write to `.scratch/`. They used to open `Path("memory.db")` in the working directory, which would have deleted the live study's substrate. |

**The three questions, answered directly:**

1. *"Do we need a fresh start every time?"* — **No.** You run for 90 days without restarting. A fresh start is needed only when the engine or the stream changes, and then the old run is archived, not erased.
2. *"Can we pause and change the programs?"* — **Yes, with one line.** Tooling, docs, dashboards, analysis, and the UI can change freely. The engine and the stream are frozen for the duration of the run.
3. *"Does a pause ruin it?"* — **No.** It leaves a gap in the time series. Note the gap in the report; that is all.

**Auditability.** To prove a run was clean, check the engine's modification time against the daemon's start time, and check that `sleep_cycle` is contiguous. Both are cheap:

```powershell
Get-Item organica\memory.py, organica\sleep.py | Select-Object Name, LastWriteTime
Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
  Where-Object { $_.CommandLine -match 'run_continuous' } |
  Select-Object ProcessId, CreationDate
python benchmarks/study_health.py
```

**Current run's audit record (2026-10-21):**

| Check | Result |
|---|---|
| `organica/memory.py` last modified | 10-20 10:00:45 — before the run started |
| `organica/sleep.py` last modified | 10-20 10:01:10 — before the run started |
| Stream the daemon is running | byte-identical to `organica/streams.py` (verified against the live DB) |
| Writers to `memory.db` | only the daemon (`seed:bootstrap`, `cycle:N`) — no analysis tool, example, or API call ever wrote to it |
| `sleep_cycles` table | 921 rows, contiguous 1–921, no gaps |
| Log | 921 records, `sleep_cycle` strictly increasing, 0 gaps, 0 failures |

**Two caveats, stated plainly.**

**Caveat 1 — the first ~264 cycles ran on the pre-optimisation build**, before transaction batching and candidate retention were added. Neither changes cognition — batching writes the same rows in the same order, and retention keeps a window 5× larger than the organism's 4,000-event working memory, so the working set is identical either way (proven by `test_prune_keeps_working_memory_intact`). But a paper should not have to argue that, so the recommendation is a **clean restart on the final build**. It costs about an hour of data and removes the argument entirely. **This is decision #4 in [§7.2](#72-decide-this-week) and it is still yours to make.**

**Caveat 2 — the cognitive freeze has now been tested, not just asserted.** The cold-start ablation ([§8.1](#81-the-cold-start-study)) ran the *unchanged* engine against eight different assistance levels and confirmed that the engine is still the engine. That matters for provenance: the cognitive code has not been touched since the run began, and the substrate changes were proven behaviour-preserving by test, so the run is a legitimate experiment against the current engine — you are not comparing two engines, you are comparing one engine against two substrates with identical behaviour.


---

## 7. What you need to do

Ordered by how much they cost you if you skip them.

### 7.1 Do today

| # | Action | Why | Effort |
|---|---|---|---|
| 1 | **Install the Scheduled Task supervisor** ([§4.2](#42-making-it-survive-90-days-)) | The daemon is unprotected. Run 1 was killed by a stray `Stop-Process`. Without this you may lose the study at any point. | 5 min |
| 2 | **Schedule the snapshot jobs** | Daily/weekly/monthly snapshots are the actual longitudinal data. Run them from a Scheduled Task, not from memory. | 10 min |
| 3 | **Decide the clean restart** (decision [#5](#72-decide-this-week)) | The current run is legitimate but carries a ~264-cycle preamble from an earlier build. A fresh start on the final build removes the caveat from the paper. | 5 min, then ~1 h of data |
| 4 | **Write the designer-surprise predictions** | One metric answers your actual question — *"did it produce anything I did not anticipate?"* — and it cannot be automated, because only you can say what you expected. The scorer is built; it needs your predictions recorded **before** a run. | 20 min |

**Completed on 2026-10-21 — recorded, not just done** (per rule 3 of [§18](#18-keeping-this-manual-current)):

| Action | Outcome |
|---|---|
| Commit and push the whole working set | `master` is in sync with `origin/master`. Commit `dacf170` — 59 files, +20,853 / −4,065. Nothing uncommitted except the live `organica.log` and `memory.db`, both gitignored, both alive. |
| Repair the observation pipeline | Snapshots contain real numbers instead of `{}`; the event journal is idempotent and time-windowed. |
| Make the repo usable by a stranger | `GETTING-STARTED.md`, `build.py`, `LICENSE`, `CITATION.cff`, `requirements*.txt`, `conftest.py`, and 9 examples that can no longer delete the live substrate. |
| Answer the long-horizon question | The cold-start ablation is complete and reported — [§8.1](#81-the-cold-start-study). |
| Answer the harder question: which parts are load-bearing? | The ablation study is complete: 11 conditions, pre-registered before the run, with a mechanism-verification stage run before any interpretation. [§8.2](#82-the-ablation-study-which-mechanisms-are-actually-doing-the-work) |
| Make the claims checkable by anyone | `docs/EMERGENCE-CRITERIA.md` defines what emergence means here, level by level, and states plainly which levels the project can currently evidence and which it cannot. |

### 7.2 Decide this week

| # | Decision | Why it matters | Detail |
|---|---|---|---|
| 4 | **The confidence-formula amendment** — *now the top-ranked decision* | Confidence is a **share**: `support / (support + contradiction)`. A hypothesis is scored against the *total flow of its siblings*, so a subject with many successors dilutes every minority expectation below the death threshold of 0.15. This is now **proven causal, not guessed**: the `wide_lookback` ablation (lookback 3 → 30, nothing else changed) destroyed G5 outright, while `no_truncation` and `no_dev_stopwords` were byte-identical to baseline. The proposed fix is a Laplace/Beta-smoothed posterior, which keeps a genuinely split belief alive, makes the lookback width irrelevant, and is *simpler* than what it replaces. | [§8.1](#81-the-cold-start-study), journal [§14](../research-journal/phase_g_findings_20261021.md) |
| 5 | **Clean restart on the final build** | The current run is valid, but the first ~264 cycles ran pre-batching and pre-retention. A fresh start costs about an hour of data and removes an argument from the paper. **Do this after the architecture decision above, not before** — otherwise you restart twice. | [§6.4](#64-rules-for-a-clean-run) |
| 6 | **The hypothesis-cap amendment** | Layer 4's 15-hypothesis cap is applied after an *alphabetical* sort, so which hypotheses survive is decided by name order rather than merit. The ablation study showed this is not a cosmetic issue: the cap is what decides whether a subject's *competing* belief survives at all, which means the reported G5 duty cycle is partly an artifact of alphabetical ordering rather than a property of the organism. | Journal [§7](../research-journal/phase_g_findings_20261021.md) |
| 7 | **Scope the experiment executor** | The largest remaining design gap, and it now blocks two things at once: the emergence claim at Level 5, and the ability to tell whether the attention economy actually buys anything (the metric that would separate EIG from random is exactly the one that needs an executor). Needs a probe format, a probe→event mapping, and a belief-delta measurement. | Journal [§13](../research-journal/phase_g_findings_20261021.md) |
| 8 | **Should `cross_domain_validation.py` use the real lineage audit?** | The shipped check measures a proxy (parent ids present among candidates) and would report 100% even if nothing touched raw experience. The real audit is `benchmarks/lineage_audit.py`. Aligning them means the published report and the shipped verification agree. | Journal [§12](../research-journal/phase_g_findings_20261021.md) |
| 9 | **Decide whether the architecture should be simplified** | The ablation study found that several layers contribute nothing measurable. The stated goal was "the simplest possible architecture that emulates living human learning and memory perfectly" — and simplification only happens if you are willing to *remove* what the measurement says is ornament. That decision is yours, and it needs a recorded rationale either way. | [§8.2](#82-the-ablation-study-which-mechanisms-are-actually-doing-the-work) |

> **Phase A freeze reminder.** Decisions 4 and 6 are *cognitive* changes — the confidence formula and the layer-selection logic. Under the Phase A freeze they remain **proposals only**; nothing in this turn applied them. What shipped this turn was substrate and measurement only. Any change to decision 4 ends the current run and requires a fresh start ([§6.4](#64-rules-for-a-clean-run)).

### 7.3 Keep doing

| # | Cadence | Action |
|---|---|---|
| 7 | Daily (30 sec) | `python benchmarks/study_health.py` — glance at the duty cycle and the failure count. |
| 8 | Daily | `run_daily_observer.bat` (or let the scheduled task do it). |
| 9 | Weekly | `run_weekly_monthly.bat`; skim `snapshots/event_journal.log` for the narrative. |
| 10 | At day 7, 30, 90 | Write a real Phase G report: G5 duty cycle over the whole window, belief-revision events, memory bound, and a Generation 9 recommendation. |
| 11 | After **any** engine change | Re-run `python benchmarks/cold_start.py --cycles 40`. It is the regression test for "did we accidentally make the organism depend on us?" — if a condition that used to bootstrap now fails, that change was cognitive, not cosmetic. |

### 7.4 When to worry

- `theories` = 0 across a **rolling window** (not one cycle) → the stream or the substrate is broken. Re-run `benchmarks/g5_gap_diagnostic.py`.
- `duration_ms` median drifting above ~1 s → substrate growth. Run `benchmarks/substrate_probe.py`.
- `sleep_cycle` going backwards → the counter bug regressed. Everything time-derived is suspect until fixed.
- `status: failed` appearing → check `console.log` for the traceback.
- G5 duty cycle dropping below ~95% → *something changed*. Check the engine's modification time against the daemon's start time ([§6.4](#64-rules-for-a-clean-run)), then re-run `benchmarks/cold_start.py`.

---

## 8. The ten findings, and what each means for you

Full detail and evidence: **`research-journal/phase_g_findings_20261021.md`**.

| # | Finding | What it means for you |
|---|---|---|
| 1 | **The original study stream could never reach G5.** No subject ever had two competing expectations, so Layer 5 had nothing to coalesce. 0 theories, 0 questions, and **zero contradictions** across 670 cycles. | The first 90-day attempt would have recorded a flat G4 line with confident-looking telemetry. Law V's EIG economy never ran. *Fixed* by a branch-structured stream chosen by sweep. |
| 2 | **The substrate could not have survived 90 days.** A full-table scan every cycle (4,826 ms at 1.65M rows) projected to ~370M rows / **~210 GB** and ~12 min/cycle. | The study was infeasible as designed. *Fixed* with an incremental counter table (result proven identical) and bounded retention. |
| 3 | **The cycle counter reset mid-run.** It was read from a 500-row window of the table it writes to; once candidates/cycle exceeded 500 the marker vanished and the counter fell from 319 to 4. | Every longitudinal time series was suspect. The health report's "670 cycles" was a count of *log lines*, not cycles. *Fixed* with a monotonic table; 426 cycles now show 0 resets. |
| 4 | **The log was truncated on every restart.** The launcher used `>` against a file the daemon's own append-mode FileHandler owns. | The longitudinal record was being destroyed. *Fixed*; the log now appends and survives restarts. |
| 5 | **The observation pipeline had never actually run.** The weekly snapshot contained literally `{}`; the event journal parsed a dead log format; "births today" was a 30-second delta; "per day" velocity used 7 cycles. | There was no data pipeline behind the study. *Fixed*: time-window based, idempotent, refuses to write empty artifacts. |
| 6 | **G5 is an oscillation, not a state.** It fires, collapses, and returns. Minority expectations sit at confidence 0.15–0.20 against a `DEATH_THRESHOLD` of 0.15 — a competitor can be extinguished by the success of its sibling. | Report Generation 5 as a **duty cycle**, never a per-cycle boolean. Also sharpens the case for the architecture amendment. |
| 7 | **One fsync per candidate dominated the cycle.** 1,023 commits = 3.0 s of a 4.5 s cycle. | *Fixed* by transaction batching: 4,500 ms → **263 ms**. The cycle is now cognition-bound, not disk-bound. |
| 8 | **Law II holds — but nothing was measuring it.** `get_ancestry()` cannot reach G0, and the shipped validation only checked that parent ids were present among other candidates. | The invariant is **true** (100% grounded, both stores). The gap was in the *verification*, not the architecture. `benchmarks/lineage_audit.py` now tests the real thing. |
| 9 | **Experiments are generated but never executed.** Every consumer only prints them. | Law IV is never exercised and **no Question can ever close**. The study measures epistemic *tension*, not *resolution*. Largest remaining design gap. |
| 10 | **The organism bootstraps most of itself, but not Generation 5.** Measured across eight assistance levels: G1, G4, G6, G7 and G8 appear from an unengineered stream with no seeding. G5 never does. | The project's central claim holds for most of the ladder and fails precisely at the pivot — and the cause is now proven causal, not guessed. See [§8.1](#81-the-cold-start-study). |

### 8.1 The cold-start study

**The question:** *would G1 have eventually built out the generations above it, with no assistance and no code changes on our end?*

**The answer, measured:** **mostly yes — and one crucial no.**

**Method.** `benchmarks/cold_start.py` runs the *unchanged* engine under eight levels of assistance. Ablations are applied in-process (subclassing and rebinding), so the engine's source is never edited and the running study is unaffected. 40 cycles per condition. The most unassisted condition, `real_git_history`, feeds the organism this repository's own commit messages — nobody designed those to cooperate.

**Results** — sleep cycles until each generation first appears (`—` = never):

| Condition | G1 | G2 proc | G3 | G4 | **G5** | G6 | G7 | G8 |
|---|---|---|---|---|---|---|---|---|
| `baseline` (seeded, engineered) | 1 | 2 | 2 | 2 | **2** | 2 | 2 | 2 |
| `no_branch` (the original stream) | 1 | 6 | 6 | 4 | **never** | 2 | 2 | 2 |
| `cold_start` (no seed, 1 event/cycle) | 5–8 | never | never | 9 | **never** | 9 | 9 | 9 |
| `cold_start_unbranched` | 6 | never | never | never | **never** | never | never | never |
| `real_git_history` (real commits) | 5 | never | never | 12 | **never** | 12 | 12 | 12 |
| `no_truncation` (cap 15→200) | 1 | 2 | 2 | 2 | **2** | 2 | 2 | 2 |
| `no_dev_stopwords` | 1 | 2 | 2 | 2 | **2** | 2 | 2 | 2 |
| `wide_lookback` (3→30) | 1 | 2 | 2 | 2 | **never** | 2 | 2 | 2 |

**What bootstraps on its own:** G1 (concepts, predictions, loops) within 5–8 cycles; G4 (hypotheses) and G6/G7/G8 (dreams, investigations, experiments) once there is anything to work on. These are genuine emergences — no seed, no engineered structure, no code change.

**What never emerges unassisted:** G2 processes, G3 workflows, and above all **G5**.

**The mechanism, proven causally.** Confidence is a *share*, not a probability:

```python
confidence = support / (support + contradiction)   # organica/sleep.py:1402
```

`contradiction` is the subject's *total outgoing flow minus this hypothesis's support*, so a hypothesis is measured against its **siblings**. The more successors a subject has, the more every minority expectation is diluted — and below `DEATH_THRESHOLD = 0.15` with ≥3 observations, it is pruned permanently.

The `wide_lookback` row is the proof: widening the temporal lookback from 3 events to 30 — **changing nothing else** — destroys G5 completely, while `no_truncation` and `no_dev_stopwords` are *identical* to baseline. More context → the organism is *less* able to hold two beliefs at once. That is the opposite of how human memory behaves, and it is a property of the formula, not of the data.

*(This also corrected an earlier hypothesis of ours: the alphabetical truncation of hypotheses was **not** what blocked G5. `no_truncation` falsified that, and the journal entry was corrected in place.)*

**Three things this means for you:**

1. **The organism is not a stub.** G1, G4, G6, G7 and G8 bootstrap themselves from real, uncooperative input. The core claim of the project holds.
2. **G5 currently requires help.** It appears in the study because the study stream was *engineered* to contain a branch point — two competing expectations about one subject. Without that engineering it does not appear, and it would not appear later either: the confidence formula actively destroys it as the subject accumulates successors.
3. **The fix is small, and it is the direction you asked for.** A Laplace/Beta-smoothed posterior instead of a share: `confidence = (support + α) / (support + contradiction + α + β)`. It is *simpler* than the formula it replaces, it keeps a genuinely split belief alive regardless of how many siblings the subject has, and it makes the lookback width irrelevant — the human-like behaviour the project is aiming at. **It is a proposal, not a change**: it is a cognitive change, and Phase A freezes those ([§7.2](#72-decide-this-week), decision #4).

**The caveat, stated plainly.** `real_git_history` used only **8 commit messages**. It is under-powered: it shows the result is not a one-line artefact, but it is not a general proof about arbitrary real-world streams. Before this goes in a paper, that condition should be re-run on a much larger real corpus.

**The other half of the answer — the self-build loop.** G8 experiments are *generated but never executed* (finding 9). Until something runs the probe and feeds the result back, the organism cannot create its own branch points, and the only source of branch points is the stream you designed. An **experiment executor** closes that loop and is the other half of "would it have built the next generations itself" — decision #7 in [§7.2](#72-decide-this-week).

**Where the evidence lives:** `benchmarks/cold_start.py`, `docs/cold_start.json`, journal [§14](../research-journal/phase_g_findings_20261021.md).

### 8.2 The ablation study: which mechanisms are actually doing the work?

The cold-start study asks *"how much help does it need?"*. The ablation study asks the complementary and less flattering question: *"which parts are load-bearing, and which are ornament?"*

Eleven conditions — a full-system reference (`O_FULL`) plus ten ablations, each removing or replacing exactly one mechanism, all applied **in-process** so the engine source is never touched. Metrics: predictive accuracy (PA), information preservation (IP), structural compression (SCR), survival selectivity (SS), lineage completeness (LC), contradiction density (CD), cross-domain transfer (CDT) and novel structure rate (NSR).

Two of the specified metrics — `CY` (questions resolved ÷ generated) and `EIG*` (entropy removed by an experiment) — are **structurally unmeasurable** here: nothing resolves a Question and nothing executes an experiment, so both are identically zero for every condition including the full system. They are excluded from the aggregate rather than zeroed, because zeroing them would look like a measurement and is not one. The Designer Surprise metrics need your protocol before a run and are pending.

**Verification comes before interpretation.** `benchmarks/ablation_verify.py` runs first and asks, for every condition, *"did the ablation actually change the organism?"* — the perturbation census (which populations changed), the Random Curiosity overlap and score-distribution check, and a contradiction-provenance analysis that re-runs the same conditions with the Layer-4 hypothesis cap removed. A condition that changed nothing was not an ablation, and saying so before reading the outcomes is the difference between a result and a coincidence.

**The pre-registration is amended, not rewritten.** `docs/ABLATION-PREREGISTRATION.md` records the predictions written before the run *and* six measurement defects found afterwards — including one that had inverted a prediction. All six are disclosed in place; §4's predictions were never revised.

**What the study found.** Nine findings, in plain words. Full evidence and reasoning: journal [§17](../research-journal/phase_g_findings_20261021.md).

| # | Finding | What it means for you |
|---|---|---|
| 1 | **Sleep and the graph are the architecture.** Removing either one produces **zero** structures of any kind. | The two foundations are real and load-bearing. |
| 2 | **Nothing leaks in.** With the graph edges removed, not one concept, loop or hypothesis emerges. | The contamination check passes cleanly. This is the most reassuring result in the study. |
| 3 | **Lineage is governance, not cognition.** Stripping every parent link changes *nothing* measurable except Lineage Completeness (1.000 → 0.000). | Law II is what makes the other claims checkable. It is not a cognitive mechanism, and the design documents should stop implying otherwise. |
| 4 | **Curiosity does not drive belief formation — it drives action on belief.** Removing it *raises* hypotheses (13→15), theories (1→3) and contradictions (12.2→17.7); only investigations and experiments vanish. | The belief layer never consults the curiosity layer. Curiosity is an output channel. |
| 5 | **Removing falsification does not cause runaway belief growth — it freezes the organism.** Hypotheses fall 13→7, theories to zero, contradictions collapse from 61% of cycles to 5%. | Our pre-registered prediction was wrong, and the real result is better: forgetting is load-bearing for holding a *current* view. Stale beliefs crowd out live ones. |
| 6 | **Dreams are structurally load-bearing for everything above Layer 5** — yet score "cosmetic". Removing them leaves 6 hypotheses, no theories, no questions, no investigations, no experiments. | The aggregate score is blind to population size. This is why the population table is part of the result. |
| 7 | **Removing the hypothesis layer produces MORE theories and LESS provenance** — 6 theories instead of 1, with lineage dropping to 0.641. | A system without lineage can produce more and prove less. |
| 8 | **Questions are not the gateway to inquiry. Dreams are.** Remove Questions and investigations and experiments carry on unchanged, because Layer 7 draws on dreams as well. | **Our pre-registered prediction was falsified.** Questions are not load-bearing for inquiry. |
| 9 | **Random curiosity performs identically to EIG curiosity** on every metric that can currently be measured — identical predictive accuracy, slightly higher aggregate, smaller organism. | **But the metric that would separate them cannot be computed without an experiment executor.** This is a blind spot with a known cause, not a null result. |

**Two of our predictions were falsified by the run** — #5 and #8. Both are recorded as such in the pre-registration rather than quietly restated. That is the point of writing predictions down first.

**A blind spot worth knowing about:** the aggregate `ES` score does not count structures. Condition #6 removed most of the organism and still scored −3.0 ("cosmetic"). Read the per-metric deltas and the population table together; treat `ES` as a convenience index over six of the eight computable metrics.

**One number to carry away:** cross-domain transfer is **−0.486** across 12 domain pairs, with a mean shared vocabulary of **0.17 tags**. Organica cannot carry knowledge from one domain to another, because its substrate is lexical co-occurrence and there is no representation above the tag that could cross a vocabulary boundary. That is the sharpest evidence that the current architecture is a knowledge-compression engine rather than a general learner — and it is exactly where the next architectural work belongs.

**The single highest-value next step** is the **experiment executor**. It unblocks four things at once: it makes EIG testable against random curiosity (#9), it makes `CY` and `EIG*` measurable so the aggregate stops being blind, it lets a Question actually close, and it is the missing half of the self-build loop. Everything else in the remedy list is downstream of it.

Full protocol, predictions and disclosure: **`docs/ABLATION-PREREGISTRATION.md`**. Results: **`docs/ablation_study.json`** and **`docs/ablation_verification.json`**. What emergence means and which levels Organica can evidence: **`docs/EMERGENCE-CRITERIA.md`**.

---

## 9. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `study_health.py` says "NO CYCLES PARSED" | the daemon has not written a cycle yet, or `organica.log` is missing | `start_organica.bat`, then wait ~40 s |
| daemon not running | it was killed, or the console it was started from closed | `start_organica.bat`; for durability install the Scheduled Task ([§4.2](#42-making-it-survive-90-days-)) |
| `theories` stuck at 0 | the stream cannot produce competing expectations | run `python benchmarks/g5_gap_diagnostic.py --cycles 10` — if `g5_eligible_subjects` is 0, the stream is the problem |
| `duration_ms` climbing | substrate growth | `python benchmarks/substrate_probe.py`; check that `substrate_rows_pruned` is non-zero in the log |
| `sleep_cycle` went backwards | the counter regression | stop the daemon, restore `organica/memory.py`'s `sleep_cycles` handling, restart |
| `status: failed` | an exception in the sleep cycle | read `console.log` for the traceback |
| `snapshots/` empty or `{}` | the observer ran against an empty/partial log | the writers now refuse to write empty artifacts; re-run after the daemon has logged cycles |
| "no such table: events" | you ran a script from the wrong directory | `cd C:\Users\monte\anti\project-organica` first, or pass absolute paths |
| disk filling up | a stray `.db` copy, or retention disabled | check `memory.db.run1_20261020` (898 MB, archived run-1 evidence — keep or delete deliberately) |

**Stopping the daemon cleanly:**

```powershell
Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
  Where-Object { $_.CommandLine -match 'run_continuous' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

The log and the database are both safe to stop and restart — the counter is monotonic and the log appends.

---

## 10. File map

```
project-organica/
├── organica/
│   ├── memory.py              # SQLite substrate: events, co-occurrence, temporal
│   │                          #   graphs, tag counts, cycle counter, retention
│   └── sleep.py               # the 8-layer sleep pipeline (68 KB — the core)
│
├── run_continuous.py           # the study daemon
├── start_organica.bat          # daemon launcher (appends, never truncates)
├── run_daily_observer.bat      # daily snapshot + event journal
├── run_weekly_monthly.bat      # weekly + monthly + velocity snapshots
├── run_dashboard_and_api.bat   # Inception API + Streamlit dashboard
│
├── metrics.py                  # log parsing + metric aggregation
├── observation/
│   └── metrics_observer.py     # time-window snapshot writers + event journal
│
├── dashboard.py / dashboard_ui.py / inception_api.py
│
├── benchmarks/
│   ├── benchmark_suite.py         # BM1–BM5 growth benchmarks
│   ├── cross_domain_validation.py # Phase F: 4 domains -> docs/validation_report.json
│   ├── endurance_soak.py          # Phase G endurance harness
│   ├── g5_gap_diagnostic.py       # WHY G5 does or does not happen
│   ├── stream_sweep.py            # choosing the study event stream
│   ├── cold_start.py              # how much assistance does it need? (unassisted bootstrap)
│   ├── ablation_study.py          # ten ablations: which mechanisms are load-bearing?
│   ├── ablation_metrics.py        # the metric contract (PA, IP, SCR, SS, LC, CD, CDT, NSR, ES)
│   ├── lineage_audit.py           # Law II: real resolution to Generation 0
│   ├── substrate_probe.py         # live substrate cost + page accounting
│   ├── substrate_scaling_analysis.py  # latency vs cycle, from the real log
│   └── study_health.py            # standing health check  ← use this daily
│
├── build.py                     # one command: build an organism from nothing
├── GETTING-STARTED.md           # stranger-facing guide
├── LICENSE  CITATION.cff        # Apache 2.0; how to cite this work
├── requirements.txt             # core dependencies (deliberately empty)
├── requirements-ui.txt / requirements-api.txt
├── conftest.py                  # makes `pytest` work from any directory
│
├── examples/domains/            # the four reproduction worlds
├── tests/                       # 17 tests (incl. substrate equivalence)
├── papers/                      # research manuscripts
├── research-journal/            # development history + Phase G findings
├── docs/                        # architecture, design laws, failures, reports
│   ├── USER-MANUAL.md           # ← this document
│   ├── ABLATION-PREREGISTRATION.md  # predictions written before the run
│   ├── EMERGENCE-CRITERIA.md    # what counts as emergence, and what we can evidence
│   └── ablation_study.json      # the ablation results
├── snapshots/                   # the longitudinal data  ← the study's output
├── organica.log                 # one JSON line per cycle (appended, gitignored)
└── memory.db                    # the substrate (gitignored)
```

---

## 11. Vocabulary

Every term the project uses, what it means, and where you will meet it. Grouped by area.

### 11.1 The substrate

| Term | Definition | Where you see it |
|---|---|---|
| **Event** | A single observation: a timestamp, a source, a type, some text. The only thing the organism ever ingests. | `events` table; `event_type` is `event` (experience) or `sleep` (internal). |
| **Experience event** | An event from the outside world. These are the only source of grounding. | `event_type != 'sleep'`. **2,344 in the current study.** |
| **Sleep event** | An event the system wrote about itself. Never used to build graphs. | `event_type == 'sleep'`; `source` begins `sleep:`. |
| **Tag** | A word of ≥4 characters extracted from an event's text, minus a stopword list. The atom of the graph. | `events.tags`; ~29 distinct in the current study. |
| **Co-occurrence edge** | "These two tags appeared in the same event." | `cooccurrences` table. |
| **Temporal edge (precedes)** | "This tag was seen within the previous 3 events of that tag." The organism's first guess at causality. | `precedes` table. |
| **Working memory** | The newest **4,000** sleep events. The population the organism reasons over. | `SleepService._load_prior_candidates()`. |
| **Candidate store** | Where persisted candidates live, bounded to the newest **20,000** rows by retention. | `events` where `source LIKE 'sleep:%'`. |
| **Retention** | Periodic eviction of old candidate rows so the database cannot grow without bound. It evicts, it does not delete history of experience events. | `MemoryService.prune_sleep_candidates()`. |
| **Backfill** | One-time reconstruction of the accounting tables (`tag_counts`, `sleep_cycles`) when opening a database created before they existed. | `MemoryService._backfill_accounting()`. |
| **Batch** | Grouping many writes into one transaction. Cuts 1,023 disk syncs per cycle to 2. | `MemoryService.batch()`. |

### 11.2 The structures (one per layer)

| Term | Definition | Recognised by |
|---|---|---|
| **Concept** | A cluster of tags that co-occur densely but spread widely — a hub of meaning. | `concepts`, `concept_candidate` |
| **Phrase** | Tags that cluster tightly but lead nowhere — a recurring idiom, not a concept. | `phrases`, `phrase_candidate` |
| **Loop** | A repeated temporal cycle of tags, e.g. `failure → modified → passed → failure`. | `loops`, `loop_candidate` |
| **Prediction** | A directed temporal edge strong enough to be worth expecting. | `predictions`, `prediction_candidate` |
| **Anomaly** | An observed value where something else was expected. | `anomalies`, `anomaly` |
| **Meta-concept** | A tag that anchors many other structures — a structural hub. | `meta_concept`, `anchor_tag` |
| **Process** | A 2–3 tag cycle in the temporal graph, a recurring behaviour. | `processes`, `process_candidate` |
| **Workflow** | A multi-step sequence joining a process and its meta-concept anchors. | `workflow_concepts`, `workflow_concept` |
| **Hypothesis** | A falsifiable claim: "subject *A* tends to be followed by *B*", with support and contradiction counters. | `hypotheses`, `hypothesis` |
| **Theory** | Two or more hypotheses about the **same subject** with **competing expectations**, coalesced. | `theories`, `theory` |
| **Question** | The entropy of that competition, scaled by how much evidence backs it. | `questions`, `question` |
| **Dream** | A proposed counterfactual path, with near-zero confidence and zero belief authority. | `dreams`, `dream` |
| **Investigation** | A ranked proposal for where to look next, scored by EIG. | `investigations`, `investigation` |
| **Experiment** | A concrete probe derived from an investigation, scored by EIG ÷ cost. | `experiments`, `experiment` |

### 11.3 The quantities

| Term | Definition |
|---|---|
| **Support** | How many times the experience stream backed a hypothesis. |
| **Contradiction** | How many times the stream produced a *different* outcome for that subject. |
| **Confidence** | `support / (support + contradiction)` — a hypothesis's **share** of its subject's outgoing flow, not a probability of being true. |
| **Death threshold** | 0.15. Below this confidence with ≥3 observations, a hypothesis is permanently pruned. |
| **Uncertainty** | Normalized Shannon entropy of a Question's two competing expectations, scaled by evidence maturity. |
| **Novelty** | How far a dream is from established reality. 0.65 completion, 0.75 analogy, 0.85 mutation, 0.90 conditional. |
| **EIG** | Expected Information Gain — `uncertainty × (1 + novelty)` for questions, `uncertainty × novelty` for dreams. The attention currency. |
| **Priority** | `EIG / cost`. Costs: discriminating probe 1.0, dream probe 0.8, mutation/conditional probe 1.2. |
| **Clustering coefficient** | How tightly a tag's neighbours interlink, 0–1. High = phrase, low = concept. |
| **Predictive reach** | How many tags a tag leads to that its neighbours do not. High = concept. |
| **Lineage** | The chain of `parent_ids` from a candidate up to the layer below. |
| **Grounded** | A candidate whose lineage provably reaches a Generation 0 experience event. |
| **Unverifiable** | Lineage broken by eviction from the candidate store. Unprovable, but not disproven. |
| **Ungrounded** | Lineage resolves, but its Layer 1 anchor appears in no experience event. A genuine violation. |
| **Duty cycle** | The fraction of a rolling window of cycles in which a generation is present. The correct way to report intermittent emergence. |
| **Cognitive revolution** | A shift in which structure dominates the population. Logged as an event-journal entry. |

### 11.4 The process

| Term | Definition |
|---|---|
| **Sleep** | One consolidation cycle. Reads the graph, proposes structures, tests them against evidence, lets the failures decay and die. Not a summariser, not a prompt. |
| **Sleep cycle / `sleep_cycle`** | The global, restart-surviving counter of sleep cycles. The x-axis of every time series. |
| **Run / process cycle** | The `cycle` field — resets to 0 on every daemon start. Not a time axis. |
| **Consolidation** | The part of a sleep cycle that merges the graph into higher-order candidates. |
| **Natural selection** | Law VI: candidates that are not reinforced decay by ×0.80 per cycle; below 0.15 they are pruned. |
| **Reinforcement** | A candidate reappearing in the current population; its confidence is boosted by +0.05. |
| **Decay** | A prior candidate absent from the current population, kept alive but weakened. |
| **Pruning** | A prior candidate whose confidence fell below threshold. Counted, and excluded from the next cycle's population. |
| **Ground truth** | Generation 0 experience events. The only thing that can confirm a belief. |

### 11.5 The experiment vocabulary

Terms from the cold-start and ablation studies.

| Term | Definition |
|---|---|
| **Cold start** | Running the organism with no pre-seeding, so the world arrives one observation at a time. Tests what bootstraps unaided. |
| **Ablation** | Removing or replacing one mechanism and measuring what changes. All ablations here are applied **in-process**, so the engine source is never edited. |
| **O_FULL** | The full-system reference condition. Every ablation is compared against it. |
| **Forward-looking scoring** | Snapshotting the organism's graph and predictions *before* a cycle's events arrive, then scoring them against what happened. The organism is always predicting unseen events. |
| **PA** | Predictive accuracy — the F1 of the organism's own Layer-1 predictions against what actually happened. |
| **PA_substrate** | The same F1 computed on the substrate's temporal graph. Separates "the substrate learned it" from "the organism represents it". |
| **IP** | Information Preservation — how much predictive power survives when the raw event stream is replaced by the organism's own abstractions. |
| **SCR** | Structural Compression Ratio — experience events represented per surviving structure. Undefined when nothing survived. |
| **SS** | Survival Selectivity — the fraction of created candidates that died. `CSR = 1 − SS`. |
| **LC** | Lineage Completeness — the fraction of structures whose ancestry resolves to a Generation 0 event. Target 1.0. |
| **CD** | Contradiction Density — unresolved contradictions per 1000 active nodes. Undefined when there are no nodes. |
| **CDT** | Cross-Domain Transfer — accuracy with transfer minus accuracy without. Negative means the donor domain hurt. |
| **NSR** | Novel Structure Rate — the fraction of new nodes whose exact topology never existed before. |
| **ES** | Emergence Score — a weighted convenience index over the computable metrics. **A summary, not a measurement**; the per-metric deltas are the result. |
| **Impact(S)** | `ES_full − ES_without_S`. Bands: cosmetic / supportive / important / foundational / existential. |
| **Not measurable** | A metric that is structurally impossible to compute here (e.g. experiment information gain, with no experiment executor). Excluded from the aggregate rather than zeroed. |
| **Emergence level** | The seven-step ladder in `docs/EMERGENCE-CRITERIA.md`, from compression emergence to ontological emergence. |

---

## 12. Abbreviations and acronyms

| Short | Full | Meaning |
|---|---|---|
| **EIG** | Expected Information Gain | The attention currency of Law V. |
| **G0–G9** | Generation 0 – Generation 9 | The developmental ladder, bottom to top. |
| **BM1–BM5** | Benchmark 1 – 5 | The growth-benchmark suite in `benchmarks/benchmark_suite.py`. |
| **CFA** | Cross-Domain Validation | Phase F. The four reproduction domains. |
| **Phase G** | Endurance / External Soak | The current phase. 24h / 7d / 30d endurance. |
| **Law I–VI** | Design Laws I–VI | The architectural constitution, `docs/DESIGN_LAWS.md`. |
| **LLM** | Large Language Model | Not used by the core — the whole point is to avoid one. |
| **G5 duty cycle** | — | Fraction of recent cycles carrying ≥1 Theory. |
| **ETL** | Extract-Transform-Load | Not used; the observer is a direct log reader. |

---

## 13. Data dictionary

### 13.1 The log line (`organica.log`)

One JSON object per cycle, appended. Fields:

| Field | Type | Meaning | Typical healthy value |
|---|---|---|---|
| `cycle` | int | Cycles since the last daemon start | 0, 1, 2, … (resets on restart) |
| `sleep_cycle` | int | **Global** sleep-cycle counter | increases by exactly 1 per line |
| `timestamp` | string | UTC ISO-8601 | `2026-10-21T18:41:17Z` |
| `status` | string | `success` or `failed` | `success` |
| `duration_ms` | int | Wall time of the sleep cycle | 150–300 ms |
| `consecutive_errors` | int | Error streak | 0 |
| `concepts` `predictions` `loops` | int | Gen 1 populations | 2 / 20 / 15 |
| `hypotheses` | int | Gen 4 population | 13–15 |
| `hypothesis_snapshot` | array | Per-hypothesis detail | see below |
| `theories` `questions` | int | Gen 5 populations | 1 / 1 |
| `dreams` | int | Gen 6 population | 8 |
| `dream_categories` | object | Dreams by category | `{"conditional": 6, "mutation": 2}` |
| `investigations` `experiments` | int | Gen 7 / Gen 8 | 5 / 5 |
| `composites_created` | int | New structures this cycle | 60–70 |
| `total_composites` | int | Cumulative | grows monotonically |
| `candidates_strengthened` | int | Law VI reinforcement count | 30–90 |
| `candidates_pruned` | int | Law VI pruning count | 0–3000 |
| `substrate_rows_pruned` | int | Rows evicted by retention | ~109, steady |

Each `hypothesis_snapshot` entry:

```json
{"id": "hyp_e7423150", "subject": "developer", "confidence": 0.19,
 "support_count": 61, "contradiction_count": 260, "generation": 3}
```

> **Reading it:** `subject` is the tag the claim is about. `confidence` is its *share* of that subject's outgoing flow. A subject appearing **twice** in the snapshot is the organism holding two competing beliefs about it — that is exactly what G5 needs. `support_count` and `contradiction_count` are the raw evidence.

### 13.2 The database (`memory.db`)

| Table | Contents |
|---|---|
| `events` | Every experience event and every persisted candidate. `event_type` separates them. |
| `cooccurrences` | `(tag_a, tag_b, count)` — which tags appear together. |
| `precedes` | `(tag_from, tag_to, count)` — which tags follow which. |
| `tag_counts` | `(tag, count)` — incremental tag frequencies. Replaces a full-table scan. |
| `sleep_cycles` | `(cycle, ran_at)` — the authoritative monotonic counter. |

### 13.3 The snapshot artifacts (`snapshots/`)

| File | Key fields |
|---|---|
| `daily/daily_YYYYMMDD.json` | `active_*` populations, `births_today`, `deaths_today`, `window_hours`, `cycles_in_window` |
| `weekly/weekly_YYYYMMDD.json` | `window_cycles`, `aggregated`, `largest_births`, `largest_deaths` |
| `monthly/monthly_YYYYMMDD.json` | `belief_population`, `hypothesis_lifecycle`, `dream_distribution` |
| `velocity/velocity_YYYYMMDD.json` | `new_theories_per_day`, `new_questions_per_day`, `new_dreams_per_day`, `new_experiments_per_day` |
| `event_journal.log` | Append-only structural events |

---

## 14. The eight layers, in detail

| Layer | Produces | Recognised by | Typical value |
|---|---|---|---|
| **G1** | Concepts, phrases, loops, predictions, anomalies | graph topology separates signal from noise | 2 concepts, 20 predictions, 15 loops |
| **G2** | Meta-concepts, processes | high-degree anchors; 2–3 tag cycles | ~5–8 processes |
| **G3** | Workflows | process + matching meta-concept anchors | ~4–8 workflows |
| **G4** | Hypotheses | workflow component pairs and process cycles, each with evidence | 13–15 |
| **G5** | Theories, Questions | ≥2 hypotheses sharing a subject with competing expectations | 1–3 |
| **G6** | Dreams | four categories, confidence 0.04–0.08, no belief authority | up to 8 |
| **G7** | Investigations | ranked by EIG | up to 5 |
| **G8** | Experiments | ranked by EIG ÷ cost | up to 5 |

### 14.1 The four dream categories

| Category | What it proposes | Confidence | Novelty |
|---|---|---|---|
| **Completion** | A transitive shortcut: if A→B and B→C, dream A→C. | 0.08 | 0.65 |
| **Analogy** | A transfer through a co-occurrence neighbour: if A~B and A→C, dream B→C. | 0.05 | 0.75 |
| **Mutation** | A structural path extension. | 0.04 | 0.85 |
| **Conditional** | The hidden context tag that might separate a Question's two outcomes. | 0.06 | 0.90 |

> **Conditional dreams only exist when there are uncertain Questions.** If you see `conditional` in `dream_categories`, G5 is live. If you only ever see `analogy`, the stream has no competing expectations and the study is invalid.

---

## 15. The formulas, with worked examples

**Confidence** — a hypothesis's share of its subject's outgoing flow:

```
confidence = support / (support + contradiction)
```

*Example:* `developer → failures` has support 61, contradiction 260.
`61 / 321 = 0.19`. That is above the 0.15 death threshold, so it survives — barely. A sibling hypothesis `developer → passed` with support 37 and contradiction 0 gets `37/37 = 1.00`, so `developer` holds one certainty and one doubt. That pair is what Layer 5 needs.

**Question uncertainty** — Shannon entropy of the two competing expectations, scaled by evidence:

```
p1 = s1 / (s1 + s2)         p2 = 1 - p1
entropy     = -(p1·log2(p1) + p2·log2(p2))
maturity    = min(1.0, (s1 + s2) / 10)
uncertainty = entropy × maturity
```

*Example:* supports 12 and 8 → p1 = 0.6, p2 = 0.4.
`entropy = 0.6·0.737 + 0.4·1.322 = 0.971`. `maturity = min(1, 20/10) = 1.0`.
`uncertainty = 0.971`. Evenly split expectations give near-maximum uncertainty — exactly the state Law V wants the organism to investigate.

**EIG** — the attention currency:

```
question target:  EIG = uncertainty × (1.0 + novelty),   novelty = 0.50
dream target:     EIG = uncertainty × novelty,             uncertainty = 1 - dream confidence
```

*Example:* a Question with uncertainty 0.97 → `EIG = 0.97 × 1.5 = 1.46`.

**Experiment priority** — value per unit cost:

```
priority = EIG / cost
cost: discriminating probe 1.0 | dream probe 0.8 | mutation/conditional probe 1.2
```

*Example:* `1.46 / 1.0 = 1.46`, which matches the ~1.49 peaks seen in the study.

**Concept vs phrase** — the two classification rules, which pull in opposite directions:

```
clustering = (edges among neighbours) / (possible edges)     high = phrase
reach      = targets the tag leads to that its neighbours do not   high = concept
```

A tag with degree ≥ 4, clustering ≤ 0.4 and reach ≥ 4 is a **concept**. A tag with clustering ≥ 0.7 and reach ≤ 2 is a **phrase**.

---

## 16. Metric cheat sheet

What a healthy run looks like, and when to worry.

| Metric | Healthy | Investigate if |
|---|---|---|
| `sleep_cycle` | +1 every line | it ever goes backwards |
| `status` | always `success` | any `failed` |
| `duration_ms` | 150–300 ms | median drifts above ~1,000 ms |
| `theories` (windowed) | 1–3, duty cycle 90–100% | duty cycle 0% over 200 cycles |
| `questions` | 1–3 | 0 across a window |
| `hypotheses` | 13–15 | drops below ~8 |
| `dreams` | 6–8 | 0 |
| `dream_categories` | contains `conditional` | only `analogy` → stream is inert |
| `contradiction_total` | 1,000–30,000 | exactly 0 → no competing expectations |
| `candidates_strengthened` | 30–90 | 0 |
| `substrate_rows_pruned` | ~109, steady | 0 → retention not running |
| `candidates_pruned` | 0–3,000 | 0 → selection pressure gone |
| DB size | ~15 MB, flat | growing without bound |
| Law II (lineage audit) | 100% grounded | any `ungrounded` |

**The two most important sanity checks:**

1. **`theories` > 0 over a window.** If this reads 0 across 200 cycles, the study is invalid regardless of how healthy everything else looks.
2. **Contradictions > 0.** Zero contradictions means zero entropy means zero EIG — a run can look perfectly healthy and be epistemantically inert.

---

## 17. Common misreadings

Things that look like findings but are not, and things that look fine but are not.

| Misreading | The truth |
|---|---|
| "The health report said 670 cycles." | That was a count of **log lines** across 4 process restarts, not cycles. The database's own count was 504, and the `sleep_cycle` counter was itself resetting mid-run. |
| "`theories` is 0, so Generation 5 failed." | Check the **window**. G5 oscillates; a single cycle reading 0 is normal. Read the duty cycle over 200 cycles. |
| "The report says `lineage_integrity_pct: 100.0`." | That check verified parent ids were present among *other candidates in a 4,000-event window*. It never reached Generation 0. The real audit (`benchmarks/lineage_audit.py`) also reports 100% — but that one actually resolves to experience events. |
| "Contradiction count is 0, so the organism is stable." | Zero contradictions means no competing expectations, so no entropy, so no EIG. That is a dead study, not a stable one. |
| "The run is dead because the daemon crashed." | It was terminated by a person (`Stop-Process` in the shell history). 504 cycles, **zero** errors. |
| "The database is 942 MB, so memory is unbounded." | That was the *unbounded* store. The current build retains a bounded window and sits flat at ~15 MB. The 942 MB file is archived run-1 evidence. |
| "Adding more domains makes the organism smarter." | Measured: adding the ecology and robot domains **reduced** G5 sustainment from 0.70 to 0.57, because more workflow structures crowd the 15-slot hypothesis budget. |
| "The organism actively experiments." | It *generates* experiment candidates. Nothing executes a probe or measures a belief delta. The study measures epistemic **tension**, not **resolution**. |
| "`sleep_cycle` and `cycle` are the same thing." | `cycle` resets per process; `sleep_cycle` is global. Only `sleep_cycle` is a time axis. |
| "The dashboard shows the same numbers as the study." | `dashboard.py` is the older CLI tool. `study_health.py` is current and is what the manual quotes. |
| "The organism will eventually work out the higher generations on its own." | Measured, and no: G1, G4 and G6–G8 bootstrap unassisted, but **G5 never appears from any unengineered stream** — and it will not appear later either, because the confidence formula destroys a minority belief as the subject accumulates successors. [§8.1](#81-the-cold-start-study) |
| "The ablation study showed the architecture works." | It did not. It showed *which parts* matter, and the answer is uncomfortable: sleep and the graph are foundational, and lineage is pure governance with **zero** behavioural effect. |
| "Lineage is one of the six design laws, so it must be doing something." | It is load-bearing for **auditability** — removing it drops Lineage Completeness from 1.0 to 0.0 — while changing no other measured behaviour. Governance, not cognition. |
| "Random curiosity performed the same, so curiosity is fake." | Not yet proven. Random and EIG curiosity score the same on the metrics that count *populations*, but the metrics that would separate them (experiment value, experiment information gain) are exactly the ones that cannot be computed without an experiment executor. |
| "The 90-day run proves the organism is emergent." | It proves the organism runs, is reproducible, and maintains lineage. Emergence is a separate claim with its own instruments: the ablation study and the designer-surprise protocol. |
| "The study measured 1,665 cycles, so the data is richer than 60 cycles." | More cycles is more of the same world. The study stream is a 48-event rotation; the cross-world measurement is CDT, and it is negative. |

---

## 18. Keeping this manual current

**This manual is a living document. It must be updated in the same turn as any change it describes.** Concretely:

**Update this file when any of these change:**

- The daemon's running state, cycle counts, or any metric in [§2](#2-where-things-stand-right-now)
- A command, launcher, or path in [§4](#4-running-everything)
- A log field's meaning in [§5](#5-reading-the-output)
- The study protocol or the nine targets in [§6](#6-what-the-study-is-measuring)
- **Your** action list in [§7](#7-what-you-need-to-do) — completed, deferred, or newly identified
- A finding in [§8](#8-the-ten-findings-and-what-each-means-for-you)
- A symptom or fix in [§9](#9-troubleshooting)
- A file's role in [§10](#10-file-map)

**The rules:**

1. **Same turn, not deferred.** If you changed the code, the manual is updated before the turn ends.
2. **No stale numbers.** A status block with old numbers is worse than no status block.
3. **Decisions get recorded, not just made.** When you decide something in [§7](#7-what-you-need-to-do), move it with a date and a one-line rationale — that trail is part of the project's contribution.
4. **Findings link to evidence.** Every claim in [§8](#8-the-ten-findings-and-what-each-means-for-you) points at a section of `research-journal/phase_g_findings_20261021.md` or a JSON report in `docs/`.
5. **The manual is for you, the journal is for the field.** The manual explains *what to do*; the journal is the scientific record. Write for the former in plain language; keep the latter rigorous.
6. **This rule is also recorded in `AGENTS.md`** at the repository root, so any agent working on this project picks it up automatically.

**Revision log:**

| Date | Change |
|---|---|
| 2026-10-21 | Created. Documented the Phase G audit, the corrected study daemon, the nine findings, the action list, and the scheduled-task recipe. |
| 2026-10-21 | Added the reference block: full vocabulary (§11), abbreviations (§12), data dictionary (§13), layer-by-layer reference (§14), formulas with worked examples (§15), metric cheat sheet with alert thresholds (§16), and common misreadings (§17). |
| 2026-10-22 | Added the cold-start study (§8.1): eight assistance levels, what bootstraps unaided, and the proof that share-based confidence is what blocks G5. Added finding 10. Added §4.7 (build an organism from nothing), the new file map entries, §11.5 (experiment vocabulary), and the new files to §4.5. |
| 2026-10-22 | Added §8.2: the ablation study — ten ablations, the metric suite, the two structurally unmeasurable metrics, and the pending designer-surprise protocol. Recorded `docs/ABLATION-PREREGISTRATION.md` (predictions written before the run) and `docs/EMERGENCE-CRITERIA.md` (the measurable emergence ladder). |
