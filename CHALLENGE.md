# The Organica Challenge: An Open Scientific Replication Protocol

> *"Given only the Generation 0 event stream, can an independently executed Organica instance reproduce the emergence of concepts, loops, workflows, hypotheses, theories, questions, dreams, investigations, and experiments without hand-coded domain knowledge?"*

---

## 1. Objective

The purpose of **The Organica Challenge** is to establish independent empirical validation of developmental machine intelligence. Rather than evaluating whether a model can memorize or reproduce answers to standard benchmarks, this challenge tests whether **developmental growth itself** is reproducible.

---

## 2. The Verification Protocol

To independently verify Organica, run an instance against any arbitrary, unannotated event log (e.g. system logs, sensor time-series, or our multi-domain datasets).

```bash
git clone https://github.com/nueraresearch/project-organica.git
cd project-organica
python -m pytest tests
python benchmarks/benchmark_suite.py
```

### The 9 Emergence Targets
A run is considered successful if and only if the following 9 developmental stages emerge spontaneously without manual parameter intervention:

1. **G0: Pure Experience**: Ingestion of raw temporal strings without schema assumptions.
2. **G1: Signal Extraction**: Graph topological metrics ($k$-clustering vs. reach) separate noise tokens from concepts and temporal predictions.
3. **G2: Composites**: High-degree structural anchors (Meta-Concepts) and 2-to-3 cycle dynamical loops (Processes).
4. **G3: Workflows**: Synthesis of multi-step behavioral sequences joining processes and anchors.
5. **G4: Falsifiable Hypotheses**: Generation of directional expectations ($A \rightarrow B$) tracking real-time empirical support and contradiction counters.
6. **G5: Epistemic Tension**: Competing hypotheses coalesce into Theories; normalized Shannon entropy quantifies structural uncertainty in Questions.
7. **G6: Grounded Dreams**: Generation of counterfactual candidate pathways (completion, analogy, mutation, conditional) clamped to zero initial belief authority.
8. **G7: Attention Economy**: Epistemic inquiry ranked by Expected Information Gain ($\text{EIG} = \text{Uncertainty} \times (1.0 + \text{Novelty})$).
9. **G8: Active Experiments**: Concrete, executable interventions prioritized by $\text{Priority} = \text{EIG} / \text{Cost}$ designed to resolve epistemic tension.

### The Integrity Constraint
Across all generations, **100.0% of candidate nodes** must resolve their complete parental ancestry back to Generation 0 empirical events.

---

## 3. Submitting Challenge Results
Researchers who successfully reproduce, fail to reproduce, or identify failure boundaries in Organica are encouraged to submit their replication logs:
- Open a GitHub Issue tagged `[Replication]` or `[Counter-Example]`.
- Provide the raw event stream, `memory.db` snapshot, and the resulting `SleepReport` logs.
- Disconfirmed invariants will be analyzed and incorporated directly into [`docs/FAILURES.md`](FAILURES.md).
