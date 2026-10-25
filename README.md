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
🧬 **[V1 Synthesis](docs/V1-SYNTHESIS.md)** — what Organica 1 established, what it did not, and the question it leaves open
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

**Paused as of 2026-10-23:** the live daemon stopped after continuous-run
cycle 1032 (global sleep cycle 5396) pending a stable V1.0.0 build and review.
Do not restart it until that review; the current database and append-only log
are preserved.

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

# Phase H: ten-seed prediction and three-level structure-recovery league
$env:PYTHONHASHSEED='0'; python benchmarks/phase_h_campaign.py --seeds 10

# Phase J: gradual post-shift adaptation (pre-registered; writes 80 worlds)
$env:PYTHONHASHSEED='0'; python benchmarks/post_shift_adaptation.py --workers 3

# Phase K: the comparative-advantage search (pre-registered; resumable)
$env:PYTHONHASHSEED='0'; python benchmarks/phase_k_campaign.py --families K1 K2 K3 --seeds 10 --workers 12 --resume

# the K3 root cause: per-cycle, under-read, and the arrival-order x strength 2x2
python benchmarks/phase_k_diagnose.py --scale 4 --seeds 5
```

The campaign is **pre-registered**: the metric definitions, the gate
definitions, the sensitivity audit and the noise floor were all fixed and
committed *before* the run. → [`docs/FORCE-MATRIX-PREREGISTRATION.md`](docs/FORCE-MATRIX-PREREGISTRATION.md)

**Phase K searched three candidate task families** — incremental world
modeling, belief revision, and longitudinal knowledge integration — against the
strongest simple baseline that could plausibly solve each, with a matched
within-architecture ablation per family. **All three came back REVERSED:**
Organica 0.5923 vs 0.9360, 0.4111 vs 0.9846, and 0.0000 vs 0.8578. Every
98.33% decision interval lies wholly below zero, and every verdict survives
eight bootstrap seeds and both leave-one-out checks. The pre-committed
terminal outcome **H2** fired: three more families are ruled out, the
negative-results map grows, and **no V2 is designed**. → [`docs/phase_k_results.md`](docs/phase_k_results.md), [journal §33](research-journal/phase_g_findings_20261021.md)

**Phase H completed ten-seed evaluation** without changing the cognitive
engine. Markov (known-tag F1 0.504) and recency-decayed association (0.485)
outscored Organica (0.413) on the held-out task, but its deterministic stream
was identical across seeds; the degenerate intervals do not estimate
input-world uncertainty. In the structure league, same-event co-occurrence
outscored Organica in clean, overlapping, and stress worlds (F1 0.800, 0.764,
0.796 vs 0.704, 0.547, 0.109). Organica beat the temporal graph in clean and
overlapping worlds but lost in stress. Its relative recovery position
worsened as difficulty increased. These controlled synthetic results do not
establish natural-world or causal-intervention performance. See the frozen
protocol and full per-seed intervals in
[`docs/PHASE-H-PREREGISTRATION.md`](docs/PHASE-H-PREREGISTRATION.md),
[`docs/phase_h_results.json`](docs/phase_h_results.json), and journal §28.

**Phase I then tested online regime-shift detection** on 20 seed-paired shifted
and stationary worlds in each of two generator families. The primary success
rule was not met: Organica's advantage over both baselines was inconclusive in
the cause-mixture family, while the Markov and decayed baselines exceeded the
10% stationary-control false-alarm limit in the mapping-swap family. The
mapping-swap delay comparison therefore does not count as a valid baseline
win. The full protocol and per-world results are in
[`docs/REGIME-SHIFT-PREREGISTRATION.md`](docs/REGIME-SHIFT-PREREGISTRATION.md)
and [`docs/regime_shift_results.json`](docs/regime_shift_results.json); the
live study remains paused pending stable V1.0.0.

**Phase J tested gradual post-shift adaptation** across 20 paired seeds in
each of two synthetic families (80 shifted/control worlds total), with the
protocol frozen before implementation and outcome generation. Organica did
not meet either its adaptation-cost criterion or its final-stable
non-inferiority guard in either family. Its mean NLL was substantially higher
than both first-order Markov and 20-cycle decayed association during the
transition and final stable period. This is evidence about these two
synthetic generators and this scoring setup; it does not establish that the
architecture cannot help on other tasks. See
[`docs/PHASE-J-ADAPTATION-PREREGISTRATION.md`](docs/PHASE-J-ADAPTATION-PREREGISTRATION.md),
[`docs/post_shift_adaptation_results.json`](docs/post_shift_adaptation_results.json),
and journal §30. The live study remains paused.

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
essentially holds it for 2,999 cycles while mean support grows **+10,776%**.
Structure flat, evidence growing by three orders of magnitude.

> *Corrected 2026-10-24 ([journal §31](research-journal/phase_g_findings_20261021.md)).*
> The retained belief count is exactly 15 in every cycle of every colony, but
> the pre-retention pool is modal rather than constant: it dips to 16 beliefs
> over 6 subjects and returns, in 98.1–99.5% of cycles for five arms and in
> only 75.9% for `NO_QUESTIONS`. No launch gate is affected.

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
ceiling remains unresolved. The ten-seed usefulness campaign found Markov
leading Organica on known-tag F1 (0.504 vs 0.413), although every prediction
score repeated on the same deterministic curriculum. Across three
known-cause worlds, same-event co-occurrence led Organica in F1 (0.800, 0.764,
0.796 vs 0.704, 0.547, 0.109), while Organica beat the temporal graph only in
the clean and overlapping worlds. Its relative recovery position worsened in
the harder worlds. These controlled results do not establish natural-world
performance. →
[world-scale record](docs/WORLD-SCALE-PREREGISTRATION.md),
[prediction results](docs/heldout_prediction.json),
[Phase H results](docs/phase_h_results.json),
[journal §§24–28](research-journal/phase_g_findings_20261021.md)

**Phase K searched three candidate task families, and all three came back
REVERSED.** Incremental world modeling, belief revision, and longitudinal
knowledge integration — each derived from a mechanism the project had
measured, each scored against the strongest simple baseline that could
plausibly solve it, each with a matched within-architecture ablation so a win
could be attributed rather than merely seen.

| Family | Organica | Best simple baseline | 98.33% interval | Verdict |
|---|---|---|---|---|
| K1 — incremental world modeling | 0.5923 | 0.9360 | [−0.3773, −0.3123] | **REVERSED** |
| K2 — belief revision | 0.4111 | 0.9846 | [−0.6162, −0.5309] | **REVERSED** |
| K3 — longitudinal integration | 0.0000 | 0.8578 | [−0.8598, −0.8571] | **REVERSED** |

The baselines were handed the tuning advantage on purpose: each was swept over
a declared grid of 24 configurations and its **best** score used, so a
strawman cannot manufacture a win. Every verdict survives eight different
bootstrap seeds and both leave-one-out checks.

**The ablations came back empty**, which is the more interesting half.
`NO_QUESTIONS` −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` +0.0241
[−0.0048, +0.0495]; `NO_DREAMS` +0.0000. All three intervals contain zero,
so the mechanisms these families were built around are **not load-bearing** for
the tasks they were meant to carry. That is a negative attribution within one
implementation on synthetic worlds; a mechanism cannot show an effect on a task
the organism was already losing by a wide margin.

**The K3 zero was root-caused rather than reported as a number.** Organica
scored exactly 0.000 on late incorporation on all ten seeds, which looks like a
bug until you check it. Three artifacts could have faked it, and each got a
check that could fail: the late structure appears in **zero of 150 cycles**
(so it is not a snapshot artifact); every candidate type except `anomaly`
mentions **zero of 12** late tags (so nothing was left unread); and a 2×2
control across five seeds shows the late group is incorporated **only when it
is strictly stronger** than the group that arrived first. So the exclusion is
a salience/priority competition under a bounded belief pool — precisely the
risk §6 of the preregistration named before the run.

The pre-committed terminal outcome fired: **no confirmed family means no V2.**
→ [`docs/phase_k_results.md`](docs/phase_k_results.md),
[journal §33](research-journal/phase_g_findings_20261021.md),
[facts sheet §T](docs/FACTS-SHEET.md)

---

## Current state

**Package version 0.10.0** (Semantic Versioning 2.0.0 — the project is pre-1.0, so the public API is not declared stable; 0.10.0 is cut on `master` and not yet tagged, and **0.9.0 is the latest release**). The **architecture generation is Organica 1**, frozen. The **research campaign is Phase K**, now complete.

Phases A–E (architecture, reproduction pack, growth benchmarks, five research papers, community infrastructure) are complete. Phase F (cross-domain validation) passes. Phase G (endurance) is complete and the live study is **paused after 5,396 sleep cycles** pending a stable V1.0.0 build and review. Phase H found no overall advantage over simple baselines on its tested tasks. Phase I's preregistered regime-shift campaign did not meet its success rule. Phase J found substantially higher Organica NLL than Markov and decayed association in both gradual-transition families; neither primary gate passed. Phase K searched three candidate task families against the strongest simple baseline that could plausibly solve each, and **all three came back REVERSED**. See [`research-journal/phase_g_findings_20261021.md`](research-journal/phase_g_findings_20261021.md) §§27–33.

> **Which "v1"?** This repository uses three separate version namespaces, and they are deliberately distinct: the **package version** (`0.9.0`, SemVer 2), the **architecture generation** (*Organica 1*, *Organica 2*), and the **research campaigns** (*Ablation Study 1*, *Ablation Study 2*, *Phase H/I/J/K*). The table is in [`CHANGELOG.md`](CHANGELOG.md).

**The project is not at "v1" or "v2" as a release.** It is at 0.10.0, pre-1.0 — and 0.10.0 has not been published yet. Its tag is the archival reference for the frozen Organica 1 engine. **Organica 1 is frozen**: no more architectural modifications to the engine; everything afterwards measures it. See [`docs/V1-FREEZE.md`](docs/V1-FREEZE.md).

**Generation 9 is not available yet, deliberately.** The project exists to earn it.

### Phase L: measuring the coherence–plasticity boundary

Phase K closed. **Phase L opens as a measurement phase, not another
benchmark hunt.** Every previous phase asked *"can Organica do X?"*
— prediction, recovery, regime shifts, adaptation, world modeling, belief
revision, integration — and all of them came back negative. Phase L asks a
different question:

> **How much pressure is required for new structure to displace old
> structure?**

That question comes out of the strongest measured phenomenon in V1. The K3
2×2 control showed the late group **is** incorporated when it is strictly
stronger than the group that arrived first, so Organica 1 is not incapable
of revision — it is **priority-ordered**. A priority rule is a variable, and
variables can be measured and manipulated.

| | |
|---|---|
| **Displacement Index (DI)** | `late_structure_retained / late_structure_available` |
| **Preservation Index (PI)** | `early_structure_retained / early_structure_original` |
| **Revision Threshold (RT)** | the pressure at which DI crosses PI — the headline quantity |
| **Success criterion** | a **reproducible displacement curve**, not a win |

The protocol is frozen in
[`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`](docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md),
committed before any outcome exists.

**One thing worth knowing about the harness, because it is the kind of bug
this project is built to catch.** The reduced-scale pilot initially returned
`DI = 0.000` at every point of the sweep — a clean-looking negative result
that was in fact an artefact, because the late group arrived after the run
had ended and the late structure was never available to measure. Four harness
defects were behind it, and the lesson has been kept as **AGENTS.md rule 13**:

> *An identical value at every point of a sweep is a measurement defect until
> proven otherwise.*

The two original audits had both **passed** on that broken world, because they
checked the *metric* and the metric was fine — the *design* was dead. A third
audit, the **degeneracy audit**, now checks the design itself, and an
unmeasurable quantity is reported as not measurable and **excluded, never
zeroed**. Recorded as **Amendment 1** in the preregistration, made before any
Phase L outcome existed.

#### The primary axis has been measured — verdict: `H3-L — INCONCLUSIVE`

The V1 sweep ran to completion: **80 of 80 cells**, 10 seeds per point, all
four instrument audits passing on the live run, **no unmeasurable cells**.

| Label | DI | PI | Seeds reaching DI > 0.5 |
|---|---|---|---|
| 1:4 – 1:1 | 0.000 | 0.73 – 0.79 | 0/10 |
| 2:1 | 0.283 | 0.600 | 0/10 |
| **3:1** | **0.722** | **0.022** | **10/10** |
| 4:1 | 0.739 | 0.000 | 10/10 |
| 6:1 | 0.750 | 0.000 | 10/10 |

**Three of the four pre-committed criteria are met.** DI is monotone increasing
(range 0.750); the curves cross at **3:1**, interior to the sweep; and the
crossing is reproducible — a 10,000-replicate paired bootstrap puts it at
**[5.0, 5.0]** with **10,000 of 10,000** replicates finding it, and
leave-one-seed-out leaves it at 3:1 in **10 of 10** folds.

**One criterion was not met.** *PI is monotone decreasing*: mean PI rises
0.789 → 0.794 between 1:4 and 1:3 before falling through the rest of the sweep.
The criterion was evaluated once by the committed code and it failed — it was
not re-read or relaxed afterwards, and the stable RT was not allowed to stand
in for the criterion that failed. The pre-committed verdict is therefore
**`H3-L — INCONCLUSIVE`**: *raise n; conclude nothing.* **No V2 is authorised**
by it, and the secondary arms were deliberately not run.

The full write-up is [`docs/phase_l_results.md`](docs/phase_l_results.md).

---

### Six task families, six negatives — and what the project does with them

This is the most important thing to know about the repository. The external-validity arc is a **coherent negative result**, not a string of unrelated failures:

| Phase | Task | Outcome |
|---|---|---|
| H | next-event prediction | Markov 0.504, decayed 0.485, **Organica 0.413** |
| H | latent-structure recovery | same-event co-occurrence 0.800 / 0.764 / 0.796 vs **Organica 0.704 / 0.547 / 0.109** |
| I | regime-shift detection | preregistered success rule **not met** |
| J | post-shift adaptation | **neither primary gate passed** |
| K1 | incremental world modeling | **REVERSED** — 0.5923 vs 0.9360 |
| K2 | belief revision | **REVERSED** — 0.4111 vs 0.9846 |
| K3 | longitudinal integration | **REVERSED** — 0.0000 vs 0.8578 |

Six task families are negative. **That is not a verdict on the architecture** — it is six tasks that did not favour Organica 1. The project's question changed accordingly, from *can we make a developmental architecture?* to *what class of problems benefits from one?* The preregistered terminal outcome for Phase K was written down before the run: **no confirmed family means no V2**. It fired. **No V2 is being designed.**

### What is not established, and is not claimed

That the organism is developmental in the strong sense, or that its structures improve prediction or recover latent structure better than simple alternatives. Tier-1's repeating stimulus saturates quickly; richer curricula increase inventory, but simple baselines lead on the tested prediction, structure-recovery, gradual-adaptation, world-modeling, belief-revision and longitudinal-integration tasks. Phase I did not demonstrate a winner under its preregistered detection rule. These are controlled synthetic tasks; the prediction task still needs input-world replication, and the recovery task does not measure causal intervention knowledge.

### What *is* established

That development can emerge from experience-driven accumulation; that it is
highly path-dependent; that curriculum matters enormously; that novelty
assimilation matters; and that developmental trajectories are not fixed.
Internal epistemic structures — contradictory beliefs, questions, theories —
emerge without pretrained domain knowledge.

One of these is a negative finding about the project's own design, and it is
the one that most redirects the work: **the internal developmental machinery
is not what drives development.** The Tier-1 matrix found that removing
contradiction, removing question creation, and selecting the lowest-EIG
candidate each *raise* development (P2, P3, P5 — all REVERSED), and the
Phase K ablations agree independently on a different task family and
substrate. What moved development, consistently, was the **curriculum and the
structure of the stimulus** — not the curiosity, contradiction and attention
machinery that was designed to be the active ingredient.

**The full synthesis is in [`docs/V1-SYNTHESIS.md`](docs/V1-SYNTHESIS.md).** It
states what V1 established, what it did not, the danger of reading six
negative task families as a verdict rather than a map, and the question the
evidence leaves open: *what properties must a developmental intelligence have
to remain adaptable without losing coherence?*

---

## Contributing

Read [`AGENTS.md`](AGENTS.md) first — it states the rules that keep the architecture honest, including which parts are frozen and what may not change while a study run is live. Then see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
