# Project Organica

> **A Developmental Machine Intelligence.**
> Growing intelligence from memory, structure, sleep, curiosity, and experimentation rather than pre-trained weights.

```bash
git clone https://github.com/nueraresearch/project-organica.git
cd project-organica
python build.py          # builds an organism from nothing -- ~30 seconds
```

**No dependencies. No GPU. No API keys. Python 3.11+ is the only requirement.**

📘 **[Getting Started](GETTING-STARTED.md)** — the guide for a first-time reader
📕 **[Owner's Manual](docs/USER-MANUAL.md)** — operating the organism and research campaigns
🔬 **[The Organica Challenge](CHALLENGE.md)** — the replication protocol
⚖️ [Apache 2.0](LICENSE) · 📌 [Cite this](CITATION.cff)

---

## The idea

Most modern AI architectures follow a top-down paradigm:

$$\text{Foundation Model (Trillions of parameters)} \longrightarrow \text{Fine-Tuning} \longrightarrow \text{Tools / Memory bolted on}$$

**Project Organica reverses this order:**

$$\text{Memory First} \longrightarrow \text{Experience} \longrightarrow \text{Sleep} \longrightarrow \text{Structural Synthesis} \longrightarrow \text{Emergent Epistemology}$$

Organica contains **zero pretrained neural networks and no hand-coded grammar or domain model**. Its lexical atom and stopword list are explicit English-specific priors, alongside its other developmental machinery. It is designed like a digital infant: an organism whose cognitive capabilities emerge through repeated cycles of waking experience, graph consolidation during sleep, hypothesis formation, structural curiosity, and active experimentation.

**What is built in, stated precisely.** The developmental machinery is specified in advance — the ladder itself, the lexical atom (words of four or more characters, minus a stopword list), co-occurrence and temporal edge construction, the extinction threshold, the Expected-Information-Gain attention rule, the dream categories. None of that is learned. What is *not* built in is any knowledge: no grammar, no vocabulary, no domain content, no pretrained weights. The claim is **"no pretrained knowledge and no domain-specific cognitive content; the mechanisms of development are specified, and knowledge structures emerge within them."** It is the same position developmental psychology takes about human infants: enormous built-in machinery, and essentially all of the *content* learned.

The honest limits of that claim are documented, measured, and kept current in [`docs/EMERGENCE-CRITERIA.md`](docs/EMERGENCE-CRITERIA.md) — including the one place where the organism currently needs help.

---

## Core principles

1. **Every Generation Emerges from Previous Generations**
   New cognitive capabilities are never manually hardcoded. Every higher-order structure ($N+1$) is synthesized strictly from structures produced by layer $N$.
2. **Sleep Never Explains — It Only Creates Structures**
   Sleep is not an LLM summarizer or chat prompt. It is a graph transformation and natural selection process that emits discrete, typed candidate nodes with explicit numeric provenance.
3. **Native Genealogical Lineage**
   Every abstract workflow, hypothesis, question, and dream maintains 100% verified ancestral parent links down to raw experience events.
4. **Natural Selection & Falsifiability**
   Candidates must earn their survival. Confirmed structures strengthen; unreinforced structures decay; refuted structures go extinct.
5. **The Attention Economy**
   Importance is not confidence. Importance is **Expected Information Gain (EIG)**. The organism prioritizes its curiosity toward resolving maximal uncertainty.

The six inviolable laws are in [`docs/DESIGN_LAWS.md`](docs/DESIGN_LAWS.md).

---

## The developmental ladder

```
[Gen 0] Events (Experience Stream)
  ↓
[Gen 1] Concepts, Predictions & Loops
  ↓
[Gen 2] Process Candidates & Meta-Concepts
  ↓
[Gen 3] Workflow Concepts
  ↓
[Gen 4] Hypothesis Candidates
  ↓
[Gen 5] Theory & Question Candidates
  ↓
[Gen 6] Categorized Dreams
  ↓
[Gen 7] Investigation Candidates
  ↓
[Gen 8] Experiments
  ↓
[Gen 9] Self-Modeling            ← reserved; requires its own evidence and review
```

**Generation 5 is the pivot.** It requires the organism to hold *two contradictory beliefs about the same subject*. The Shannon entropy of that contradiction becomes a Question, and the system spends its attention there. A run that never reaches G5 is not a healthy run — it is an inert one, and the telemetry will look fine while it happens.

---

## What to run

### See it build itself

```bash
python build.py                     # from an empty substrate, layer by layer
python build.py --all               # in all four reproduction worlds
python examples/domains/01_developer_workflow.py
```

### Run the 90-day longitudinal study

```bash
start_organica.bat                  # Windows
python run_continuous.py            # macOS / Linux

python benchmarks/study_health.py   # is it alive? is the counter monotonic?
```

### Verify the claims

| Claim | Command |
|---|---|
| Lineage really resolves to Generation 0 | `python benchmarks/lineage_audit.py` |
| The stream can reach Generation 5 | `python benchmarks/g5_gap_diagnostic.py --cycles 10` |
| The substrate stays bounded | `python benchmarks/substrate_probe.py` |
| Growth benchmarks hold | `python benchmarks/benchmark_suite.py` |
| The four domains reproduce | `python benchmarks/cross_domain_validation.py` |
| The code is correct | `python -m pytest tests -q` |
| A fresh clone works | `python benchmarks/clone_check.py` |

Every one of these writes a machine-readable report into `docs/`.

### Reproduce the research

```bash
# The V1 ablation study, and its re-run on the fixed substrate
python benchmarks/ablation_study.py --cycles 300 --out docs/ablation_study.json
python benchmarks/ablation_study.py --cycles 300 --out docs/ablation_study_postfix.json

# V1 before vs after, including the RETRACTED interpretations
python benchmarks/v1_impact.py

# The Tier-1 matrix: 6 colonies x 3,000 cycles
python benchmarks/run_matrix.py --cycles 3000 --out docs/force_matrix.json

# Which metrics can discriminate at all, and the measured noise floor
python benchmarks/metric_sensitivity.py --matrix docs/force_matrix.json
python benchmarks/process_noise.py --sweep --cycles 3000

# The pre-registered predictions, bucketed
python benchmarks/verdicts.py

# The discovery curve -- what was found, and when
python benchmarks/discovery_report.py

# Frozen held-out prediction pilot: Organica vs simple baselines
$env:PYTHONHASHSEED='0'; python benchmarks/heldout_prediction.py

# Known-cause structure recovery pilot
$env:PYTHONHASHSEED='0'; python benchmarks/ground_truth_recovery.py
```

The campaign is **pre-registered**: the metric definitions, the gate
definitions, the sensitivity audit and the noise floor were all fixed and
committed *before* the run. → [`docs/FORCE-MATRIX-PREREGISTRATION.md`](docs/FORCE-MATRIX-PREREGISTRATION.md)

The held-out prediction script is a **single-seed pilot**, not yet a
preregistered multi-run evaluation. Its first result favors the tag-level
Markov baseline over Organica on this synthetic curriculum; see the output
artifact and journal §24 before interpreting it.

The known-cause recovery pilot also favors a simple same-event co-occurrence
graph over Organica's surviving structures (F1 0.800 vs 0.706). Its feature
families are deliberately clean, so the result is a benchmark shakedown, not
evidence about real-world causal discovery. See the generator, result artifact,
and journal §25.

### Explore it interactively

```bash
pip install -r requirements-ui.txt
streamlit run dashboard_ui.py

pip install -r requirements-api.txt
python inception_api.py             # POST /inception to perturb a live organism
```

---

## Repository structure

```
project-organica/
├── organica/
│   ├── memory.py       # SQLite substrate: events, co-occurrence, temporal graphs
│   ├── sleep.py        # the eight-layer sleep transformation service
│   ├── streams.py      # the experience streams the organism can be run against
│   ├── branch_streams.py  # branch-structured stimuli (the unit of competing expectation)
│   ├── scale_streams.py   # worlds of increasing information content (the H24 ladder)
│   ├── ground_truth_worlds.py  # synthetic causes, regime changes, and noise with hidden labels
│   └── paths.py        # canonical paths; disposable scratch space
├── build.py            # build an organism from scratch
├── run_continuous.py   # the study daemon
├── metrics.py          # log parsing and metric aggregation
├── observation/        # time-window snapshots and the structural event journal
├── benchmarks/         # the audits, benchmarks and campaigns above
├── examples/           # one script per generation + the four domains
├── tests/              # the test suite
├── papers/             # research manuscripts
├── research-journal/   # the full development record, including the failures
└── docs/               # architecture, design laws, failure history, reports
```

---

---

## What the research has found

The project keeps a full development record in
[`research-journal/phase_g_findings_20261021.md`](research-journal/phase_g_findings_20261021.md),
including the failures. The findings that changed the plan:

**A measurement defect was suppressing the organism's own structure.** The
tag-frequency counter that normalises every Layer-1 edge strength was
maintained over *all* stored events, including the organism's own sleep
payloads, while the graph it normalises was built from world events only.
The numerator and the denominator of the same ratio were measuring different
populations, and the survival filter discarded the world's own edges.
Measured on the study stream: 4 surviving edges, 0 processes, 0 workflows, 0
beliefs. Fixed, and a regression test now asserts the two populations match.
→ [journal §21](research-journal/phase_g_findings_20261021.md), [manual §8.4](docs/USER-MANUAL.md)

**That fix reversed a V1 conclusion.** "No Falsification freezes the organism"
is **withdrawn**. Pre-fix it produced nothing; post-fix it is the
best-supplied condition in the study — 18 beliefs, every subject competing,
MBSD 1.000 — and it is the only V1 condition that clears the launch gates.
Across the twelve comparable scalars, 21 deltas **reversed**, 36 changed
magnitude, 14 survived. Three *interpretations* were retracted outright.
→ [journal §22](research-journal/phase_g_findings_20261021.md), [`docs/v1_impact.json`](docs/v1_impact.json)

**The Tier-1 matrix ran: 6 colonies × 3,000 cycles = 18,000 colony-cycles.**
Every arm reaches its complete structural configuration — 18 pre-retention
beliefs, 7 competing subjects, 15 retained beliefs — **on cycle 1**, and
holds it for 2,999 cycles while mean support grows **+10,776%**. Structure
flat, evidence growing by three orders of magnitude.

The five pre-registered predictions came back **2 SUPPORTED and 3 REVERSED**:

| # | Prediction | Verdict |
|---|---|---|
| P1 | Retention policy affects development | **SUPPORTED** (M7: 212 vs 2,990 cycles) |
| P2 | Contradiction is developmental fuel | **REVERSED** — removing it *raises* development |
| P3 | Curiosity needs explicit questions | **REVERSED** — removing questions *raises* development |
| P4 | Dreams contribute to trajectory | **SUPPORTED** — removing them lowers it |
| P5 | EIG is orthogonal to development | **REVERSED** — lowest-EIG develops *more* than highest-EIG |

The verdicts are **direction-aware**. A naive "did the metric move?" test
would have scored all five as confirmed and reported a clean sweep of
confirmations. → [`docs/FORCE-MATRIX-RESULTS.md`](docs/FORCE-MATRIX-RESULTS.md), [`docs/verdicts.json`](docs/verdicts.json)

**And the campaign measured something other than what it was named.** M5,
"development velocity", is `new items ÷ run length`. The reference arm
discovered **74** items over 300 cycles and **74** over 3,000 — the rate fell
from 24.667 to 2.467 because the *numerator stopped growing*. The stimulus
**repeats every 9 cycles**: 9 distinct events, seen 333 times. A repertoire
cannot grow in a world that does not change, so the plateau is consistent
with *the organism exhausted the environment* — which is not the same
statement as *the organism cannot develop*.

That produced the project's current hypothesis, **H24**:

> Organica's apparent developmental plateau is primarily constrained by
> **environmental information content** rather than by architectural inability
> to reorganise.

H24 is stated with its evidence and falsification criteria. Uniformly larger
worlds reduced inventory; scaffolded and reinforced novelty raised it. The
exploratory 1,200-cycle burst horizon reached 128 items against a 91-item core
baseline, but discovery slowed to two items in the final 100 cycles. This
supports curriculum-dependent structure formation, while the longer-term
ceiling remains unresolved. The first usefulness pilots now compare frozen
Organica predictions and recovered structures with simple baselines. On the
single-seed held-out task, Markov leads Organica in known-tag F1 (0.504 vs
0.413) and log loss (0.182 vs 0.775); on known-cause pair recovery, same-event
co-occurrence leads in F1 (0.800 vs 0.706). These pilots do not establish
general performance: both need multi-seed and harder-world evaluation. →
[world-scale record](docs/WORLD-SCALE-PREREGISTRATION.md),
[prediction results](docs/heldout_prediction.json),
[recovery results](docs/ground_truth_recovery.json),
[journal §§24–25](research-journal/phase_g_findings_20261021.md)

---

## Current state

**Package version 0.7.0** (Semantic Versioning 2.0.0 — the project is pre-1.0, so the public API is not declared stable). The **architecture generation is Organica 1**, frozen. The **research campaign is Ablation Study 2**, and its Tier-1 matrix has now run.

Phases A–E (architecture, reproduction pack, growth benchmarks, five research papers, community infrastructure) are complete. Phase F (cross-domain validation) passes. Phase G (endurance) is complete. The current evaluation record includes the instrumentation audit, gate validation, substrate correction, V1 before/after audit, Tier-1 matrix, extended burst horizon, and first held-out prediction and known-cause recovery pilots. See [`research-journal/phase_g_findings_20261021.md`](research-journal/phase_g_findings_20261021.md).

> **Which "v1"?** This repository uses three separate version namespaces, and they are deliberately distinct: the **package version** (`0.7.0`, SemVer 2), the **architecture generation** (*Organica 1*, *Organica 2*), and the **research campaigns** (*Ablation Study 1*, *Ablation Study 2*). The table is in [`CHANGELOG.md`](CHANGELOG.md).

**The project is not at "v1" or "v2" as a release.** It is at 0.7.0, pre-1.0.

**Generation 9 is not available yet, deliberately.** The project exists to earn it.

**What is not established, and is not claimed:** that the organism is
developmental in the strong sense, or that its structures improve prediction
or recover latent structure better than simple alternatives. Tier-1's
repeating stimulus saturates quickly; richer curricula increase inventory,
but the first predictive and recovery pilots favor simpler baselines. H24
captures the curriculum question; external usefulness now needs replicated,
harder evaluations.

---

## Contributing

Read [`AGENTS.md`](AGENTS.md) first — it states the rules that keep the architecture honest, including which parts are frozen and what may not change while a study run is live. Then see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
