# Paper 3: Contradiction, Information Gain, and Inquiry in Organica

**Authors:** Jeremy et al. (Nuera Research)  
**Draft status:** Hypothesis and evidence review, 2026-10-27. Not submitted or published.  
**Scope:** Candidate curiosity mechanisms; no causal efficacy claim is made.

## Abstract

Project Organica includes mechanisms intended to represent competing expectations, uncertainty, and information-gain-guided inquiry. Their presence in the architecture does not establish that contradiction or expected information gain drives useful learning. Earlier descriptions treated these mechanisms as an explanatory account of attention allocation; subsequent experiments narrowed that interpretation. The available record does not establish that increasing contradiction or EIG improves external task performance, accelerates acquisition, or produces better questions. This manuscript reframes the proposal as a set of testable mechanism hypotheses. It specifies the distinctions needed for future tests: a mechanism’s implementation, its effect on internal structure, and its effect on externally scored learning are separate claims. The paper is not a positive result until a controlled intervention shows that changing the mechanism changes a preregistered outcome against a control the harness can fail.

## 1. Mechanism proposal

Organica represents competing expectations and computes internal quantities intended to prioritize unresolved structure. The original proposal links contradiction, uncertainty, novelty, and expected information gain to inquiry priority. This is a description of the design hypothesis, not evidence that the chosen quantity is a calibrated estimate of information gain or that the resulting priority is useful.

The earlier formulation should be treated as a historical design proposal; its equations and implementation mapping must be checked against the frozen engine before publication.

## 2. What the current evidence permits

The project’s later task evaluations do not support a broad claim that the curiosity machinery gives Organica an external advantage. Phase K’s three tested task families were all REVERSED against the strongest eligible simple baseline ([`docs/phase_k_results.md`](../docs/phase_k_results.md)). That result does not by itself identify curiosity as the cause: the matched ablation intervals included zero, so the causal contribution of individual layers remains unresolved.

Accordingly, this paper does not claim that contradiction or EIG is the dominant developmental variable, that questions drive development, or that inquiry is optimally allocated. Such claims require an intervention that changes the mechanism while holding the stream, engine, opportunity set, and evaluation fixed.

## 3. Falsifiable next test

A suitable study would preregister: (1) the exact implementation quantity manipulated; (2) a mechanism-off or shuffled-priority control; (3) equal experience and compute budgets; (4) an external outcome such as held-out latent-rule acquisition or adaptation; and (5) a decision rule with uncertainty over independent worlds. Internal counts of questions, theories, or experiments should be secondary outcomes, not substitutes for learning performance.

## Conclusion

Contradiction and EIG remain plausible design hypotheses, not demonstrated explanations of Organica’s learning or comparative advantage. The scientifically useful contribution at present is the separation of implementation claims from causal and utility claims, and a protocol that could distinguish them.

