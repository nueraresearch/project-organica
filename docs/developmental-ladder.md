# The Developmental Ladder (Generations 0 through 8)

Every new capability in Organica must emerge strictly from the structures produced by preceding layers.

---

### Generation 0: Experience & Events
- **Input**: Raw environment observations (file modifications, test suites, status changes).
- **Structure**: Append-only log with lightweight tokenization.
- **Substrate**: SQLite persistent storage.

### Generation 1: Spatial & Temporal Graphs
- **Co-occurrence Graph**: Non-directional edge weights between co-occurring tags within an event.
- **Temporal Graph**: Directional lookback edges ($N-1, N-2, N-3 \to N$) capturing empirical sequence flow.
- **Nodes Created**:
  - `ConceptCandidate`: Low clustering coefficient, high predictive reach beyond local cluster.
  - `PhraseCandidate`: High clustering coefficient (clique), low outward predictive reach.
  - `LoopCandidate`: 2-cycles and 3-cycles in the temporal graph.
  - `PredictionCandidate`: Strong directional predictive edges.

### Generation 2: Structural Composition
- **Input**: Stable, reinforced Generation 1 candidates.
- **Nodes Created**:
  - `ProcessCandidate`: Chains of directional predictions compressed into cyclic workflows.
  - `MetaConceptCandidate`: Structural anchors that appear across multiple distinct candidate types (loops, predictions, concepts).

### Generation 3: Workflows
- **Input**: Generation 2 ProcessCandidates intersecting multiple MetaConcepts.
- **Nodes Created**:
  - `WorkflowConceptCandidate`: Multi-anchor operational cycles (e.g., `failure -> modified -> passed`).

### Generation 4: Hypotheses
- **Input**: Workflows, Processes, and Meta-Concepts.
- **Structure**: Typed graph nodes containing `subject` and `expectation`.
- **Dynamics**: Tested against empirical stream. Support increases confidence; contradiction reduces confidence. Falsified hypotheses drop below death threshold ($0.15$) and go extinct.

### Generation 5: Theories & Questions (Curiosity)
- **TheoryCandidate**: Groups competing hypotheses sharing a common subject, capturing dialectic systemic tension.
- **QuestionCandidate**: Quantifies structural entropy. Reaches peak uncertainty ($1.0$) when competing outcomes are evenly split ($50/50$) over repeated observations.

### Generation 6: Categorized Dreams
- **Completion Dreams**: Transitive closure shortcuts.
- **Analogy Dreams**: Knowledge transfer across co-occurrence synonym clusters.
- **Mutation Dreams**: Path extensions and structural variations of workflows.
- **Conditional Dreams**: Searching for hidden context tags separating conflicting forks.

### Generation 7: Investigation Agenda (The Attention Economy)
- **InvestigationCandidate**: Prioritizes questions and dreams strictly by **Expected Information Gain (EIG)**:
  $$\text{EIG}_{\text{question}} = \text{Uncertainty} \times (1.0 + \text{Novelty})$$
  $$\text{EIG}_{\text{dream}} = (1.0 - \text{Confidence}) \times \text{Novelty}$$

### Generation 8: Active Experiments (Next Milestone)
- **ExperimentCandidate**: Translates top-ranked investigations into active probes and interventions in the environment, validating or refuting dreams and collapsing question uncertainty.
