# Paper 3: Curiosity Through Contradiction: EIG-Driven Attention in Self-Supervised Systems

**Authors**: Jeremy et al. (Nuera Research)  
**Date**: October 2026  
**Status**: Pre-print Candidate  
**Repository**: `https://github.com/nueraresearch/project-organica`

---

## Abstract
Reinforcement learning agents typically formulate curiosity as an extrinsic reward bonus derived from prediction error or state novelty. However, error-based exploration frequently falls victim to the "noisy TV problem," pursuing unpredictable noise rather than meaningful structure. In this work, we propose **Curiosity Through Contradiction (CTC)**. In Project Organica, curiosity is not an arbitrary scalar reward; it emerges naturally from topological conflict between co-existing hypotheses. When opposing expectations emerge from the same subject, the architecture groups them into a `TheoryCandidate` and computes normalized Shannon entropy as structural uncertainty. By prioritizing investigations via **Expected Information Gain (EIG)**, the organism allocates attention specifically to resolve epistemic contradictions that maximize structural reorganization.

---

## 1. Contradiction Formalism
Given two competing hypotheses sharing subject $S$:
$$H_1: S \rightarrow E_1 \quad (\text{support } s_1), \quad H_2: S \rightarrow E_2 \quad (\text{support } s_2)$$
The probability distribution of competing outcomes is $p_i = \frac{s_i}{s_1 + s_2}$.

The structural uncertainty $U(S)$ is defined as:
$$U(S) = -\left(\sum_{i=1}^2 p_i \log_2 p_i\right) \times \min\left(1.0, \frac{s_1 + s_2}{10}\right)$$
Uncertainty peaks at $1.000$ when observations are evenly split ($50/50$), and approaches $0.000$ when one expectation completely dominates ($99/1$).

---

## 2. Attention Economy: Expected Information Gain
Rather than investigating high-confidence truths, Organica allocates cognitive focus using:
$$\text{EIG} = U(S) \times (1.0 + \text{Novelty})$$
Experimental intervention priority is balanced against resource cost:
$$\text{Priority} = \frac{\text{EIG}}{\text{Cost}}$$
Empirical trials confirm that high-priority probes selectively target and resolve the core forks of the system's behavioral graph.
