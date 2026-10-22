# Getting Started with Project Organica

> **For anyone who has never seen this project.** You need a working knowledge of Python — nothing else. No machine learning background, no GPU, no API keys, no accounts.
>
> **Time to first result: about 30 seconds.**

---

## 1. What this is, in one paragraph

Most AI systems are *loaded* with intelligence: someone trained a huge model on a huge dataset, and the result is handed to you. Project Organica takes the opposite approach. It starts with **nothing** — an empty database and a stream of plain text events — and grows its own cognitive structures out of the pattern in that text. It does this through repeated **sleep cycles**: each cycle reads the graph of what has been observed, proposes higher-order structures (concepts, loops, workflows, hypotheses, theories, questions, dreams), tests them against the evidence, and lets the ones that do not hold up decay and die.

There are no pre-trained weights. There are no hard-coded natural-language rules. The claim being tested is that intelligence is something you can *grow* rather than something you can *load*.

---

## 2. Install

```bash
git clone https://github.com/nueraresearch/project-organica.git
cd project-organica
```

That is the whole installation. **The core has zero third-party dependencies** — it runs on the Python standard library alone. You need **Python 3.11 or newer**.

Check it works:

```bash
python --version          # must be 3.11+
python build.py           # builds an organism from nothing -- see below
```

### Optional extras

Only if you want the user interface or the HTTP API:

```bash
pip install -r requirements-ui.txt     # Streamlit dashboard
pip install -r requirements-api.txt    # Flask Inception API
pip install -e ".[dev]"                # pytest, to run the test suite
```

---

## 3. The one command: watch it build itself

```bash
python build.py
```

This creates an empty substrate, feeds it raw text events with **no schema and no labels**, runs sleep cycles, and prints what emerges layer by layer:

```
  [1] ingested 48 experience events (0.01s)
  [2] cycle  1 (0.30s)  concepts  2  loops 15  workflows  8  hyps 13  theories 1  questions 1  dreams 8  exps 5
          competing subjects: 5   contradictions: 1439   max uncertainty: 0.996   top priority: 1.494
  ...
  [3] DEVELOPMENTAL LADDER
        Gen 0  Experience events         624  ####################
        Gen 1  Concepts                    2  ##
        ...
  [4] INTEGRITY (Law II)
        candidates resolving to a Generation 0 experience event: 100.0%
  [5] EPISTEMIC ACTIVITY (Law V)
        Generation 5 REACHED: competing hypotheses coalesced into
        theories, and the uncertainty between them is non-zero.
```

Other modes:

```bash
python build.py --all                        # build in all four reproduction worlds
python build.py --domain robot_simulation    # just one world
python build.py --cycles 12 --keep           # longer build; keep the scratch DB to inspect
```

`build.py` writes only into `.scratch/`. It can never touch a real run.

### The four reproduction worlds

Each is a self-contained environment where emergence is visible in about a second:

```bash
python examples/domains/01_developer_workflow.py    # CI/CD: failure -> modified -> passed
python examples/domains/02_bug_tracking.py          # issue -> engineer -> commit -> close
python examples/domains/03_synthetic_ecology.py     # forage -> consume -> replenish
python examples/domains/04_robot_simulation.py      # drive -> obstacle -> turn -> clear
```

### The ladder, one generation at a time

```bash
python examples/01_sleep_consolidation.py          # Gen 1: concepts from raw events
python examples/02_composition_lineage.py          # Gen 2: meta-concepts and processes
python examples/03_selection_workflows.py          # Gen 3: workflows
python examples/04_falsification_hypotheses.py      # Gen 4: falsifiable hypotheses
python examples/05_curiosity_investigation_agenda.py  # Gen 5-8: theories, dreams, EIG agenda
```

---

## 4. The developmental ladder

Everything the system knows sits on this ladder. Each generation is built only from the one below it.

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

**Generation 5 is the interesting one.** It requires the organism to hold *two contradictory beliefs about the same thing* — then the entropy of that contradiction becomes a Question, and the system spends its attention there. A run that never reaches G5 is not a healthy run; it is an inert one.

---

## 5. Running the 90-day longitudinal study

The study is a long-running daemon that grows one organism against a fixed stream and records everything.

```bash
# Windows
start_organica.bat

# macOS / Linux
python run_continuous.py
```

It appends one JSON summary per cycle to `organica.log` (never truncates it) and keeps its substrate in `memory.db`.

**Check on it:**

```bash
python benchmarks/study_health.py
```

```
daemon              : ALIVE - PID 19916 since 10/21/2026 11:21:35
sleep_cycle 1..626  : non-monotonic steps: 0   OK
G5 duty cycle       : 100.0%
failed cycles       : 0
```

**Collect the longitudinal data:**

```bash
run_daily_observer.bat      # daily snapshot + structural event journal
run_weekly_monthly.bat      # weekly aggregate + monthly genome + velocity
```

**Dashboards:**

```bash
run_dashboard_and_api.bat    # Streamlit UI + the Inception HTTP API
```

> **Full operating manual:** [`docs/USER-MANUAL.md`](docs/USER-MANUAL.md) — every command, every log field, the vocabulary, the formulas, the metric cheat sheet, and the rules for keeping a run scientifically clean.

---

## 6. Verifying the claims yourself

Nothing above asks you to take the project's word for it. Every claim has a script:

| Claim | Command |
|---|---|
| The lineage actually resolves to Generation 0 | `python benchmarks/lineage_audit.py` |
| The stream can reach Generation 5 at all | `python benchmarks/g5_gap_diagnostic.py --cycles 10` |
| The substrate stays bounded and affordable | `python benchmarks/substrate_probe.py` |
| The growth benchmarks hold | `python benchmarks/benchmark_suite.py` |
| The four domains reproduce | `python benchmarks/cross_domain_validation.py` |
| The organism bootstraps without help — and where it stops | `python benchmarks/cold_start.py --cycles 40` |
| Which mechanisms are actually load-bearing | `python benchmarks/ablation_study.py --cycles 300` (slow, ~25 min) |
| ...and that each ablation really perturbed the organism | `python benchmarks/ablation_verify.py --cycles 300` |
| The code is correct | `python -m pytest tests -q` |
| A fresh clone of this repo works end to end | `python benchmarks/clone_check.py` |

Each writes a machine-readable JSON report into `docs/`.

**Two of them are slow** (the ablation suite runs 11 conditions of 300 sleep cycles each). Run the fast ones first; `cold_start.py` takes about three minutes and answers the most interesting question.

---

## 7. Where to go next

| If you want to… | Read |
|---|---|
| Understand the architecture | [`docs/architecture.md`](docs/architecture.md), [`docs/DESIGN_LAWS.md`](docs/DESIGN_LAWS.md) |
| Understand why it is built this way | [`docs/FAILURES.md`](docs/FAILURES.md), [`research-journal/`](research-journal/) |
| Read the research | [`papers/`](papers/) |
| Operate the study | [`docs/USER-MANUAL.md`](docs/USER-MANUAL.md) |
| Reproduce the emergence targets | [`CHALLENGE.md`](CHALLENGE.md) |
| See how it failed and was fixed | [`research-journal/phase_g_findings_20261021.md`](research-journal/phase_g_findings_20261021.md) |

**Contributing:** [`CONTRIBUTING.md`](CONTRIBUTING.md). Please read [`AGENTS.md`](AGENTS.md) first — it states the rules that keep the architecture honest, including which parts are frozen.

**Citing:** [`CITATION.cff`](CITATION.cff).

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'organica'` | You are not in the repository directory. `cd project-organica` and retry. |
| `python: command not found` | Use `python3`, or install Python 3.11+. |
| `pip install -r requirements.txt` installs nothing | Correct — the core has zero dependencies. That is deliberate. |
| `build.py` reports Generation 5 not reached | The stream you selected gives no subject two competing expectations. Try `python build.py` (the study stream) or `python build.py --all`. |
| The daemon is not running | `start_organica.bat`. It will not survive a console close — see the Scheduled Task recipe in the manual. |
| `theories` is 0 | Check the *window*, not one cycle. `python benchmarks/study_health.py` reports the duty cycle over the last 200 cycles. |

---

## 9. One-minute orientation to the codebase

```
organica/
├── memory.py     SQLite substrate: events, co-occurrence graph, temporal graph
├── sleep.py      the eight-layer sleep pipeline -- the core of the project
├── streams.py    the experience streams the organism can be run against
└── paths.py      canonical file locations; scratch space for demos

run_continuous.py     the study daemon
build.py              build an organism from scratch (start here)
metrics.py            log parsing and metric aggregation
observation/          time-window snapshot writers and the event journal
benchmarks/           the audits and benchmarks listed in section 6
examples/             one script per generation, plus the four domains
tests/                the test suite
```

Start reading at `organica/sleep.py` if you want the real thing — it is the only file that matters, and everything else is instrumentation around it.
