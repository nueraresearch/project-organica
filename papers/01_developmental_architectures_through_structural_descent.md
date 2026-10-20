# Paper 1: Developmental Cognitive Architectures Through Structural Descent

**Authors**: Jeremy et al. (Nuera Research)  
**Date**: October 2026  
**Status**: Pre-print Candidate  
**Repository**: `https://github.com/nueraresearch/project-organica`

---

## Abstract
Modern artificial intelligence models compress vast linguistic corpora into static parameter weights, trading epistemic provenance and developmental growth for statistical prediction. In this work, we introduce **Project Organica**, a non-parametric developmental architecture where higher-order cognitive primitives (concepts, processes, workflows, falsifiable hypotheses, theories, questions, counterfactual dreams, and active experiments) emerge through **structural descent**. Rather than relying on LLM prompting or gradient updates, each generational layer $N+1$ operates deterministically upon the topological graphs produced by Layer $N$. We demonstrate across four diverse domains (developer workflows, bug trackers, synthetic ecologies, and robotic kinematics) that complex cognitive structures consistently emerge, maintain 100% verified ancestral lineage, and self-direct inquiry without external reward shaping.

---

## 1. Introduction & The Developmental Paradigm
Artificial intelligence has converged on the "Oracle Paradigm": pre-training monolithic networks that provide probabilistic responses while severing the connection between knowledge and experience. Once weights are updated, the empirical genealogy of an assertion is permanently lost.

We demonstrate an alternative framework grounded in developmental biology and Piagetian epistemology:
$$G_0 \xrightarrow{\text{Filter}} G_1 \xrightarrow{\text{Compose}} G_2 \xrightarrow{\text{Synthesize}} G_3 \xrightarrow{\text{Falsify}} G_4 \xrightarrow{\text{Entropy}} G_5 \xrightarrow{\text{Perturb}} G_6 \xrightarrow{\text{EIG}} G_7 \xrightarrow{\text{Probe}} G_8$$

Every cognitive state in Organica can explain why it exists, what observations generated it, what competing hypotheses it opposes, and what experiment would falsify it.

---

## 2. Structural Descent Formalism

### 2.1 Topological Filtering ($G_0 \rightarrow G_1$)
Given an event stream $S$, we maintain a directed temporal graph $G_{\text{temporal}} = (V, E_{\tau})$ and an undirected co-occurrence graph $G_{\text{cooc}} = (V, E_{\sigma})$. Cognitive primitives are distinguished by their local clustering coefficient $C(v)$ and out-neighborhood predictive reach $R(v)$:
- **Concepts**: $C(v) \le 0.40, R(v) \ge 4$ (structural bridges).
- **Phrase Fragments**: $C(v) \ge 0.70, R(v) \le 2$ (localized collocations).

### 2.2 Higher-Order Composition ($G_1 \rightarrow G_3$)
Let $\mathcal{P}$ denote closed directed 2- and 3-cycles in $G_{\text{temporal}}$ and $\mathcal{M}$ denote meta-concept anchors participating across multiple candidate types. A **Workflow** $W$ emerges when:
$$W = \mathcal{P} \bowtie \mathcal{M}, \quad |\text{Anchors}(W)| \ge 2$$
Workflows represent learned behavioral sequences formed strictly from proven dynamical cycles.

---

## 3. Results Across Diverse Domains
Organica was evaluated across four distinct domains without hyperparameter tuning:
1. **Developer Traces**: Spontaneous emergence of `failure -> modified -> passed`.
2. **Issue Lifecycles**: Spontaneous emergence of triage-to-verification processes.
3. **Synthetic Ecologies**: Discovery of closed metabolic foraging loops (`food -> organism`).
4. **Autonomous Kinematics**: Discovery of obstacle-turn-clear sensorimotor loops.

In all cases, 100% of generated high-order structures traced complete parentage back to raw events.

---

## 4. Conclusion
Structural descent provides a foundation for continual learning without catastrophic forgetting, post-hoc explainability layers, or hallucination. Intelligence does not require billions of parameters; it requires the developmental discipline of structural descent.
