# The Developmental Ladder: From Memory to Autonomous Agency

The architecture has advanced through the epistemological phases:

```
[V0] Memory (Events & Temporal Graph)                     ✅ Complete
  ↓
[V1] Concepts (Graph Topology & Co-occurrence)             ✅ Complete
  ↓
[V2] Composition & Selection (Workflows & Ancestry)        ✅ Complete
  ↓
[V3] Falsifiable Hypotheses (Belief Revision & Survival)   ✅ Complete
  ↓
[V4] Curiosity & Questions (Structural Tension & Entropy)  ✅ Complete
  ↓
[V5] Dreams (Counterfactual Daydreaming Perturbations)     ✅ Complete
  ↓
[V6] Experiments (Active Probing & Intervention)           ⏳ Next
  ↓
[V7] Goal Formation (Autonomous Research Agenda)           ⏳ Planned
  ↓
[V8] Self-Model (Metacognition: Knowledge Boundary)        ⏳ Planned
  ↓
[V9] Open-Ended Development (Multi-Year Evolution)         ⏳ Long-term
```

---

## The Critical Transition: From Passive Observer to Active Agent

Until **V5**, the organism was passive:
$$\text{Experience arrives} \longrightarrow \text{Structure updates}$$

Beginning with **V6 (Experiments)**, causality reverses:
$$\text{Structural Uncertainty (Question/Dream)} \longrightarrow \text{Action / Intervention} \longrightarrow \text{Observation}$$

### Anatomy of V6 (Active Experimentation)
1. **ExperimentCandidate**:
   - `question_id` / `dream_id`: What specific uncertainty is this probe resolving?
   - `intervention`: Specific synthetic action (e.g. modify file, toggle flag, invoke test).
   - `expected_outcomes`: Hypothesized forks.
   - `outcome_delta`: Post-probe evidence update directly strengthening or disproving the parent hypothesis.

2. **Closing the Dream Loop**:
   - Dreams start as low-confidence ($0.05$) counterfactuals.
   - Experiments test dreams against reality.
   - If confirmed, dreams are promoted to genuine concepts; if refuted, they are pruned.

3. **Attention Economy**:
   - Rank questions by $\text{Uncertainty} \times \text{Centrality}$.
   - Allocate finite action bandwidth to top-priority probes.
