# Project Organica: Architecture Specification (v1.0 Frozen)

> **Status**: FROZEN. No new cognitive primitives or generations will be introduced until Phase G endurance and multi-domain validations are completed.

---

## 1. System Topology

```
             ┌─────────────────────────────────────────────────────────┐
             │                     ENVIRONMENT                         │
             │           (Code, Web, Filesystem, Robotics)             │
             └─────────────▲─────────────────────────────┬─────────────┘
                           │ (Probes / Experiments)      │ (Events)
                           │                             ▼
                 ┌─────────┴─────────┐         ┌───────────────────┐
                 │ Experiment Runner │         │   MemoryService   │
                 └───────────────────┘         │  (Event Log & DB) │
                                               └─────────┬─────────┘
                                                         │
                                    ┌────────────────────┴────────────────────┐
                                    │                                         │
                                    ▼ (Non-sleep events)                      ▼ (Sleep Candidates)
                         ┌─────────────────────┐                   ┌─────────────────────┐
                         │   Empirical Graph   │                   │ Candidate Registry  │
                         │ (cooc & precedes)   │                   │ (Generations 1 - 8) │
                         └──────────┬──────────┘                   └──────────▲──────────┘
                                    │                                         │
                                    └────────────────────┬────────────────────┘
                                                         │
                                               ┌─────────▼─────────┐
                                               │   SleepService    │
                                               │ (Layers 1 to 8)   │
                                               └───────────────────┘
```

---

## 2. The 8 Generational Primitives

### G0: Experience (`Event`)
- **Schema**: `id`, `timestamp`, `content`, `event_type`, `source`, `tags`.
- **Invariant**: Strictly records interactions. Sleep events (`event_type="sleep"`) are stored for history and lineage lookup but are **excluded** from empirical graph edge weight calculations.

### G1: Empirical Candidates
- **Topological Invariants**:
  - `ConceptCandidate`: $k$-clustering $\le 0.40$, predictive reach $\ge 4$, degree $\ge 4$.
  - `PhraseCandidate`: $k$-clustering $\ge 0.70$, predictive reach $\le 2$.
  - `PredictionCandidate`: Temporal directionality ratio $\ge \text{PREDICTION\_MIN\_COUNT} / \text{SourceFreq}$.
  - `LoopCandidate`: Directed cycles ($L \in \{2, 3\}$) with edge support $\ge \text{LOOP\_MIN\_STRENGTH}$.

### G2: Composite Structures
- `MetaConceptCandidate`: Emerges when a tag acts as an anchor linking $\ge 3$ distinct candidates across $\ge 2$ distinct candidate types.
- `ProcessCandidate`: Closed dynamical cycles formed by composing validated prediction candidates.

### G3: High-Order Workflows
- `WorkflowConceptCandidate`: Multi-step sequences synthesized when a process cycle is anchored by $\ge 2$ meta-concepts.

### G4: Falsifiable Hypotheses
- `HypothesisCandidate`: Synthesizes an explicit expectation ($A \rightarrow B$). Records real-time `support_count` and `contradiction_count`.
- **Invariant**: Confidence is empirically updated: $\text{conf} = \frac{\text{support}}{\text{support} + \text{contradiction}}$. Pruned when $\text{conf} < 0.15$.

### G5: Theories & Questions
- `TheoryCandidate`: Groups competing hypotheses sharing the same subject ($A \rightarrow B_1, A \rightarrow B_2$).
- `QuestionCandidate`: Quantifies structural tension using normalized Shannon entropy multiplied by observation maturity:
  $$\text{Uncertainty} = - \sum p_i \log_2(p_i) \times \min\left(1.0, \frac{\text{Obs}}{10}\right)$$

### G6: Categorized Dreams
- `DreamCandidate`: Strictly bounded counterfactual perturbations across 4 archetypes:
  1. *Completion*: Transitive closure of unlinked causal pairs.
  2. *Analogy*: Substitution of co-occurring structural synonyms.
  3. *Mutation*: Path extension by grafting unvisited meta-anchors.
  4. *Conditional*: Hypothesis of a hidden context tag separating conflicting question outcomes.
- **Invariant**: Initial confidence is clamped to $\le 0.06$. Dreams never directly modify existing beliefs.

### G7: Investigation Agenda
- `InvestigationCandidate`: Focus of epistemic attention ranked by Expected Information Gain:
  $$\text{EIG} = \text{Uncertainty} \times (1.0 + \text{Novelty})$$

### G8: Active Experiments
- `ExperimentCandidate`: Executable interventions prioritized by:
  $$\text{Priority} = \frac{\text{EIG}}{\text{Cost}}$$
- **Invariant**: Contains unambiguous test vectors. Probes return empirical outcomes that either validate or refute underlying questions/dreams.
