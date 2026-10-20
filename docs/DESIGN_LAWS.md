# Project Organica: Inviolable Design Laws

These six laws form the architectural constitution of Project Organica. Any modification or extension that violates these invariants is considered an architectural regression.

---

### Law I: Strict Upward Layer Induction
> *Layer $N+1$ operates exclusively on the structural objects synthesized by Layer $N$.*

Higher-order cognitive primitives (concepts, processes, workflows, hypotheses, theories) are never hard-coded, prompt-engineered, or injected from the top down. They must emerge naturally from below through structural composition.

---

### Law II: 100% Verified Structural Provenance
> *Every cognitive primitive must trace an unbroken, deterministic DAG of `parent_ids` back to Generation 0 empirical events.*

- No post-hoc approximations (e.g. attention heatmaps or embedding distances) are permitted as a substitute for true ancestry.
- If a candidate cannot prove its parents, it is discarded.
- Lineage queries must resolve in finite time with zero ungrounded nodes.

---

### Law III: Cognitive Isolation
> *Internal cognitive operations (sleep consolidation, dream generation, hypothesis pruning) must never pollute the empirical experience graphs.*

- Event logs must partition internal reflection (`event_type="sleep"`) from external observation.
- Co-occurrence graphs and temporal precedes matrices are strictly computed on non-sleep events.
- Failure to enforce this law results in catastrophic recursive hallucination on the system's own serialization schema.

---

### Law IV: Grounded Dreaming (No Self-Delusion)
> *Dreams propose possibilities; only empirical reality confirms beliefs.*

- Dreams are assigned minimal baseline confidence ($0.04 - 0.06$) and zero belief authority.
- Dreams cannot modify hypothesis support counters or belief confidences.
- A dream can only become a belief if an external experiment generates empirical events that confirm its structure.

---

### Law V: Epistemic Attention (EIG Over Confidence)
> *Cognitive importance is governed by Expected Information Gain, not probability.*

- Traditional systems spend compute confirming what they already know with high probability.
- Organica allocates attention where uncertainty and novelty intersect:
  $$\text{EIG} = \text{Uncertainty} \times (1.0 + \text{Novelty})$$
- A mature, highly confident hypothesis has an EIG approaching $0.0$; an evenly split contradiction has peak EIG.

---

### Law VI: Natural Selection Over Beliefs
> *Structures that fail to receive recurring empirical reinforcement decay and face permanent extinction.*

- Candidates that are not observed or reinforced across sleep cycles decay by an exponential factor ($\times 0.80$/cycle).
- Any candidate falling below the death threshold ($\text{confidence} < 0.15$) is permanently pruned from active consideration.
- Memory is not an infinite accumulation of stale assertions; it is a competitive ecosystem.
