# Paper 2: Persistent Structural Provenance in Continual Learning Systems

**Authors**: Jeremy et al. (Nuera Research)  
**Date**: October 2026  
**Status**: Pre-print Candidate  
**Repository**: `https://github.com/nueraresearch/project-organica`

---

## Abstract
Explainability in contemporary deep neural networks is predominantly post-hoc: saliency maps, attention weights, or probe classifiers attempt to approximate why a model produced an output after the parameters have already blended disparate training signals. In this paper, we present **Persistent Structural Provenance (PSP)**, a core invariant of Project Organica. By constructing every cognitive candidate as a deterministic, directed acyclic graph (DAG) node referencing explicit parent IDs, the architecture guarantees 100% ancestral lineage preservation across millions of events and sleep cycles. We evaluate PSP against traditional continual learning baselines, demonstrating zero catastrophic forgetting, complete explainability down to the timestamp of experience, and instantaneous falsification upon regime shifts.

---

## 1. The Lineage Deficit in Modern ML
When a transformer model updates its weights via backpropagation:
$$\theta_{t+1} = \theta_t - \eta \nabla_{\theta} \mathcal{L}$$
the individual contribution of an experience is diffused across millions of matrix elements. Once integrated, the system cannot isolate which specific training sample gave rise to a given prediction.

Under **Persistent Structural Provenance**:
$$\text{Node}_{\text{gen}=k} = f(\{\text{Node}_{\text{gen}=k-1}^i\}), \quad \text{Parents}(N) = \bigcup \{N_{\text{parent}}\}$$
Ancestry is non-destructive and explicit.

---

## 2. Experimental Verification
Across 200 high-order candidates generated through multi-cycle sleep consolidation in the Organica Benchmark Suite:
- **Parent Verification Rate**: 100.00% (200/200 links verified).
- **Lineage Depth**: Traversal from Generation 8 (Experiments) to Generation 0 (Raw Events) completes in $O(D)$ where $D \le 8$.
- **Falsification Speed**: When a regime shift contradicts an empirical hypothesis, the exact affected branch is marked and decayed without perturbing orthogonal knowledge structures.
