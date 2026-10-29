# Paper 1: Developmental Structure Formation in Organica 1

**Authors:** Jeremy et al. (Nuera Research)  
**Draft status:** Evidence-alignment revision, 2026-10-27. Not submitted or published.  
**Scope:** Organica 1; developmental outcomes and their measurement.

## Abstract

Project Organica is a developmental architecture that constructs candidate structures from a stream of events through repeated consolidation. We examine what Organica 1 has demonstrated after a sequence of preregistered developmental and external-task studies. The evidence supports history- and curriculum-dependent changes in internal structure: different curricula produce different structural trajectories, and prior assumptions that inventory ceilings were fixed were overturned in later experiments. These findings establish developmental dynamics in the operational sense used here; they do not establish human-like learning, open-ended growth, or general intelligence. In external evaluations to date, Organica has not demonstrated an advantage over the tested lightweight baselines on held-out prediction, latent-structure recovery, regime-shift response, or the Phase K task families. We describe the architecture, summarize the measured developmental results, and separate those results from the still-open question of whether developed structures provide reusable knowledge.

## 1. Research question and scope

This paper asks whether a frozen developmental architecture changes its internal structural state as a function of experience and curriculum. It does not treat inventory growth as a proxy for intelligence, nor does it assume that a structure is useful because it persists or has a long lineage.

“Development” here means measured change in the architecture’s candidate structures over cycles. “Path dependence” means that the measured final state varies with the experienced history or curriculum. The existing curriculum comparisons vary event content and presentation schedule together; they do not isolate strict order dependence while holding the event multiset constant.

## 2. Architecture

Organica 1 receives tagged event streams and periodically forms higher-level candidates through fixed engine procedures. The engine has built-in inductive structure, including a tag extractor, candidate types, thresholds, persistence rules, and a fixed consolidation process. It is therefore a system without pretrained domain content, not a system without prior structure or assumptions.

The architecture and frozen-engine boundary are described in [`docs/architecture.md`](../docs/architecture.md) and [`docs/V1-FREEZE.md`](../docs/V1-FREEZE.md). The implementation should be reported as it exists, not as an idealized eight-layer hierarchy: each claimed layer or capability requires a direct mapping to the frozen code and an observable output.

## 3. Evidence and interpretation

The developmental record documents curriculum-sensitive trajectories and repeated movement beyond earlier inventory attractors. The project’s synthesis concludes that history-dependent cognitive structure can form, while external task advantage remains unestablished ([`docs/V1-SYNTHESIS.md`](../docs/V1-SYNTHESIS.md); [`research-journal/phase_g_findings_20261021.md`](../research-journal/phase_g_findings_20261021.md)).

External evaluations are material counterevidence to any claim that structural development already yields useful task performance. Phase K’s three preregistered task families were all classified **REVERSED**; its belief-revision comparison was 0.4111 for Organica versus 0.9846 for the strongest simple baseline ([`docs/phase_k_results.md`](../docs/phase_k_results.md)). Phase L measured structural displacement indices, not belief revision, and its preregistered overall verdict was **H3-L — INCONCLUSIVE** ([`docs/phase_l_results.md`](../docs/phase_l_results.md)). These outcomes must remain distinct.

## 4. Limitations

The evidence is from synthetic and task-specific environments, and does not show learning like a human. Curriculum sensitivity is not the same as strict order dependence. Increasing inventory is not evidence of prediction, transfer, causal understanding, or improved future learning. The audit results apply to the reconstruction tasks and tested engine states; they do not establish independent replication by another laboratory or complete reconstruction of lost historical state.

## 5. Conclusion

Organica 1 provides evidence for curriculum-sensitive developmental structure formation. It has not yet shown that this development produces reusable knowledge or an advantage over simple alternatives. The acquisition study is preregistered but not yet built or run; its benchmark must first be aligned with the structure the engine can actually express. This paper should be completed only after its methods, figures, and every numerical claim are tied to committed artifacts.

## Repository evidence

- [`docs/V1-SYNTHESIS.md`](../docs/V1-SYNTHESIS.md)
- [`docs/phase_k_results.md`](../docs/phase_k_results.md)
- [`docs/phase_l_results.md`](../docs/phase_l_results.md)
- [`docs/EMERGENCE-CRITERIA.md`](../docs/EMERGENCE-CRITERIA.md)
