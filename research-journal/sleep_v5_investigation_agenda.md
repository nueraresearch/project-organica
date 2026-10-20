# Sleep V5: Categorized Dreams & Expected Information Gain (EIG)

The developmental architecture has progressed across 7 distinct generations:

$$\text{Events} \to \text{Candidates} \to \text{Composites} \to \text{Workflows} \to \text{Hypotheses} \to \text{Theories \& Questions} \to \text{Categorized Dreams} \to \text{Investigation Agenda}$$

---

## 1. Categorized Dreams (Layer 6)
Dreams are differentiated across four specific functional archetypes:

1. **Completion Dreams**:
   - Transitive closure across observed process paths ($A \to B \to C \implies A \to C$).
2. **Analogy Dreams**:
   - Structural synonym substitution using co-occurrence neighbor clusters ($A \to C \land A \sim B \implies B \to C$).
3. **Mutation Dreams**:
   - Path extensions and variations injecting unmodelled anchors into stable workflows.
4. **Conditional Dreams**:
   - Structural search for hidden context tags separating conflicting outcomes in high-uncertainty questions.

```json
{
  "type": "dream",
  "id": "dream_mut_ea04430f",
  "generation": 5,
  "dream_category": "mutation",
  "subject": "passed",
  "path_or_context": ["passed", "suite", "modified"],
  "confidence": 0.04,
  "novelty": 0.85,
  "parent_ids": ["workflow_25a96efc", "meta_b8001285"]
}
```

---

## 2. Investigation Candidates & The Attention Economy (Layer 7)
The currency shifts from confidence to **Expected Information Gain (EIG)**:

$$\text{EIG}_{\text{question}} = \text{Uncertainty} \times (1.0 + \text{Novelty})$$
$$\text{EIG}_{\text{dream}} = (1.0 - \text{Confidence}) \times \text{Novelty}$$

The organism ranks questions and dreams to decide what to investigate next:

```json
{
  "type": "investigation",
  "id": "inv_909e4fb4",
  "generation": 6,
  "target_id": "question_19b34d93",
  "target_type": "question",
  "subject": "failures",
  "novelty": 0.5,
  "uncertainty": 1.0,
  "expected_information_gain": 1.5,
  "parent_ids": ["question_19b34d93"],
  "evidence": {
    "formula": "uncertainty * (1.0 + novelty)",
    "competing_outcomes": ["passed", "suite"]
  }
}
```

---

## 3. Epistemic Priority: Importance $\neq$ Confidence
- Highly confident, well-established workflows yield near-zero EIG.
- Unresolved structural forks (e.g. `subject: failures` with $50/50$ uncertainty) maximize EIG ($1.5000$).
- High-novelty dreams ($0.85$) generate significant EIG ($0.8160$), prioritizing bold counterfactual tests over routine verification.
