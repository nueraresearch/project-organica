# Sleep V6: Active Experiment Probes & Closed-Loop Validation (Path B)

With **Sleep V6**, Project Organica completes the bridge from internal curiosity to external empirical action (**Path B: Active Organism**).

```
Experience (G0)
     ↓
Candidates (G1)
     ↓
Composites (G2)
     ↓
Workflows (G3)
     ↓
Hypotheses (G4)
     ↓
Theories & Questions (G5)
     ↓
Categorized Dreams (G6)
     ↓
Investigation Agenda [EIG] (G7)
     ↓
Experiment Candidates [Priority = EIG / Cost] (G8)
     ↓
Environment Action & Empirical Feedback
```

---

## 1. Experiment Candidate Structure

Every `ExperimentCandidate` is an actionable probe designed to test an `InvestigationCandidate`:

```json
{
  "type": "experiment",
  "id": "exp_a49f120c",
  "generation": 7,
  "investigation_id": "inv_question_19b34d93",
  "target_id": "question_19b34d93",
  "target_type": "question",
  "action_type": "discriminating_probe",
  "probe_payload": {
    "subject": "failures",
    "target_question_id": "question_19b34d93",
    "competing_outcomes": ["passed", "suite"],
    "test_vector": "probe:failures -> ? (passed vs suite)"
  },
  "expected_outcomes": ["passed", "suite"],
  "cost": 1.0,
  "priority": 1.5000,
  "status": "proposed",
  "parent_ids": ["inv_question_19b34d93"],
  "evidence": {
    "investigation_eig": 1.5000,
    "cost": 1.0,
    "formula": "EIG / cost"
  }
}
```

---

## 2. Priority Allocation: $\text{Priority} = \frac{\text{EIG}}{\text{Cost}}$

Investigations represent what would theoretically yield the highest information gain. Experiments weigh that gain against the cost of empirical execution:

| Target Type | Action Type | EIG | Cost | Priority | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Question** (Uncertainty 1.0) | `discriminating_probe` | 1.5000 | 1.0 | **1.5000** | Decisive resolution between `passed` vs `suite` |
| **Conditional Dream** | `verify_conditional_dream` | 0.8460 | 1.2 | **0.7050** | Validated hidden contextual fork |
| **Completion Dream** | `verify_completion_dream` | 0.6650 | 0.8 | **0.8312** | Validated shortcut pathway |

---

## 3. Lineage Verification: 100% Unbroken Lineage to Generation 0

In Sleep V6, an experiment retains full provenance back through investigations, questions/dreams, hypotheses, workflows, processes, predictions, and raw events:

```
Experiment (exp_a49f120c)
  └── Investigation (inv_question_19b34d93)
        └── Question (question_19b34d93)
              ├── Hypothesis (hyp_b26d6aea: failures -> passed)
              │     └── Workflow (workflow_failure_modified_passed)
              │           └── Process (process_failure_modified)
              │                 └── Prediction (failures -> modified)
              └── Hypothesis (hyp_77de28a2: failures -> suite)
```
Every node is mathematically and architecturally falsifiable.
