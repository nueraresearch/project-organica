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
📕 **[Owner's Manual](docs/USER-MANUAL.md)** — operating the 90-day study
🔬 **[The Organica Challenge](CHALLENGE.md)** — the replication protocol
⚖️ [Apache 2.0](LICENSE) · 📌 [Cite this](CITATION.cff)

---

## The idea

Most modern AI architectures follow a top-down paradigm:

$$\text{Foundation Model (Trillions of parameters)} \longrightarrow \text{Fine-Tuning} \longrightarrow \text{Tools / Memory bolted on}$$

**Project Organica reverses this order:**

$$\text{Memory First} \longrightarrow \text{Experience} \longrightarrow \text{Sleep} \longrightarrow \text{Structural Synthesis} \longrightarrow \text{Emergent Epistemology}$$

Organica begins dumb, minimal, and lightweight. It contains **zero pre-trained neural networks and zero hard-coded natural language rules**. It is designed like a digital infant: an organism whose cognitive capabilities emerge through repeated cycles of waking experience, graph consolidation during sleep, hypothesis formation, structural curiosity, and active experimentation.

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
[Gen 9] Self-Modeling            ← locked until the longitudinal study concludes
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

Every one of these writes a machine-readable report into `docs/`.

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
│   └── paths.py        # canonical paths; disposable scratch space
├── build.py            # build an organism from scratch
├── run_continuous.py   # the study daemon
├── metrics.py          # log parsing and metric aggregation
├── observation/        # time-window snapshots and the structural event journal
├── benchmarks/         # the audits and benchmarks above
├── examples/           # one script per generation + the four domains
├── tests/              # the test suite
├── papers/             # research manuscripts
├── research-journal/   # the full development record, including the failures
└── docs/               # architecture, design laws, failure history, reports
```

---

## Current state

The architecture is **frozen at v1.0** while a 90-day longitudinal study runs. Phases A–E (architecture, reproduction pack, growth benchmarks, five research papers, community infrastructure) are complete. Phase F (cross-domain validation) passes. Phase G (endurance) is underway.

The last full audit — and the nine findings that came out of it, including two that invalidated the first attempt at the study — is in [`research-journal/phase_g_findings_20261021.md`](research-journal/phase_g_findings_20261021.md).

**Generation 9 is not available yet, deliberately.** The project exists to earn it.

---

## Contributing

Read [`AGENTS.md`](AGENTS.md) first — it states the rules that keep the architecture honest, including which parts are frozen and what may not change while a study run is live. Then see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
