# Sleep V4: Theory Formation, Curiosity & Daydreaming

The developmental architecture has progressed across 6 distinct generations:

$$\text{Events} \to \text{Candidates} \to \text{Composites} \to \text{Workflows} \to \text{Hypotheses} \to \text{Theories \& Questions} \to \text{Dreams}$$

---

## 1. Theories (Explaining Co-Existing Conflicts)
A `TheoryCandidate` groups competing hypotheses that share a subject:
```json
{
  "type": "theory",
  "id": "theory_19b34d93",
  "generation": 4,
  "subject": "failures",
  "hypotheses": ["hyp_b26d6aea", "hyp_77de28a2"],
  "confidence": 0.2083,
  "support_count": 20,
  "contradiction_count": 76,
  "evidence": {
    "competing_count": 2,
    "expectations": ["passed", "suite"],
    "hypothesis_confidences": [0.2083, 0.2083]
  }
}
```

---

## 2. Questions (Structural Curiosity)
Uncertainty is quantified using entropy weighted by observation volume. When competing expectations are evenly split ($50/50$), uncertainty peaks at $1.0$:
```json
{
  "type": "question",
  "id": "question_19b34d93",
  "generation": 4,
  "subject": "failures",
  "competing_expectations": ["passed", "suite"],
  "uncertainty": 1.0,
  "parent_ids": ["hyp_b26d6aea", "hyp_77de28a2"],
  "evidence": {
    "ratio": [0.5, 0.5],
    "supports": [10, 10],
    "total_pair_evidence": 20
  }
}
```

---

## 3. Dreams (Synthetic Counterfactual Perturbations)
Stable workflows are counterfactually perturbed by injecting structural anchors, initialized with low confidence ($0.05$):
```json
{
  "type": "dream",
  "id": "dream_ea04430f",
  "generation": 5,
  "original_workflow_id": "workflow_25a96efc",
  "perturbed_path": ["modified", "suite"],
  "confidence": 0.05,
  "parent_ids": ["workflow_25a96efc"],
  "evidence": {
    "original_components": ["passed", "suite"],
    "injected_anchor": "modified",
    "source_workflow_confidence": 1.0
  }
}
```

---

## 4. Full Lineage Descent (6 Generations)
```
Dream (Gen 5: modified -> suite)
  └── WorkflowConcept (Gen 2: workflow_passed_suite)
        ├── ProcessCandidate (Gen 1: cycle [passed, suite])
        │     ├── PredictionCandidate (Gen 1: passed -> suite)
        │     └── PredictionCandidate (Gen 1: suite -> passed)
        ├── MetaConcept (Gen 1: anchor 'passed')
        └── MetaConcept (Gen 1: anchor 'suite')
              └── Raw Event Graph Foundations
```
Lineage integrity is maintained with $100\%$ verified parentage.
