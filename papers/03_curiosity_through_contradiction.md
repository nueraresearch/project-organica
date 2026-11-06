# Paper 3: Contradiction, Information Gain, and Inquiry in Organica

**Authors:** Jeremy et al. (Nuera Research)  
**Draft status:** Hypothesis and evidence review, 2026-10-27; revised 2026-11-06 to record the Tier-1 mechanism ablations reported in Paper 07. Not submitted or published.  
**Scope:** Candidate curiosity mechanisms. Their internal direction is now measured; no causal efficacy claim is made for an external outcome.

## Abstract

Project Organica includes mechanisms intended to represent competing expectations, uncertainty, and information-gain-guided inquiry. Their presence in the architecture does not establish that contradiction or expected information gain drives useful learning. Earlier descriptions treated these mechanisms as an explanatory account of attention allocation; subsequent experiments narrowed that interpretation. The available record does not establish that increasing contradiction or EIG improves external task performance, accelerates acquisition, or produces better questions. This manuscript reframes the proposal as a set of testable mechanism hypotheses. It specifies the distinctions needed for future tests: a mechanism’s implementation, its effect on internal structure, and its effect on externally scored learning are separate claims.

A preregistered ablation written since this review disables each mechanism in its own colony and finds the internal development measure moving in the direction **opposite** the proposal in all three cases: removing contradiction’s weight, removing question generation, and inverting EIG selection each *raise* it (Paper 07, §4). That is a measured internal direction, not a demonstrated external benefit, and it does not yet settle whether the mechanisms matter where the original proposal claimed they would. The paper remains not a positive result: a controlled intervention must still show that changing the mechanism changes a preregistered **external** outcome against a control the harness can fail.

## 1. Mechanism proposal

Organica represents competing expectations and computes internal quantities intended to prioritize unresolved structure. The original proposal links contradiction, uncertainty, novelty, and expected information gain to inquiry priority. This is a description of the design hypothesis, not evidence that the chosen quantity is a calibrated estimate of information gain or that the resulting priority is useful.

The earlier formulation should be treated as a historical design proposal; its equations and implementation mapping must be checked against the frozen engine before publication.

## 2. What the current evidence permits

The project’s later task evaluations do not support a broad claim that the curiosity machinery gives Organica an external advantage. Phase K’s three tested task families were all REVERSED against the strongest eligible simple baseline ([`docs/phase_k_results.md`](../docs/phase_k_results.md)). That result does not by itself identify curiosity as the cause: the matched ablation intervals included zero, so the causal contribution of individual layers to an external score remains unresolved.

### 2.1 The Tier-1 matrix: the internal direction, measured

[Paper 07](07_architecture_predictions_reversed.md) reports an ablation that this review’s §3 asked for, run under a preregistered direction rule. Six colonies ran on the same engine, the same 9-event stimulus and the same seed `20261023` for 3,000 cycles each: a reference arm, a retention-policy arm, and one arm per mechanism. The mechanism arms are `NO_CONTRADICTIONS` (contradiction unweighted in the confidence formula), `NO_QUESTIONS` (question generation disabled) and `ANTI_EIG` (experiments selected by *lowest* expected information gain). Each was scored on its effect metric against a measured one-item noise floor of 0.033 new structures per 100 cycles.

All three reversed. Removing contradiction’s weight **+0.166**; removing question generation **+1.266**; inverting EIG selection **+0.366**. Two disclosures govern how those numbers may be read, both stated in Paper 07: `NO_CONTRADICTIONS` removes contradiction’s *weight in the confidence formula*, not the contradiction count, so the arm is not the intervention its name suggests; and M5 is a finite inventory divided by run length, not a velocity.

Measured against this review’s own five conditions, the matrix meets three and misses two:

| Condition (from §3) | Status | What meets it, and what is missing |
|---|---|---|
| (1) The exact implementation quantity manipulated | **Met** | contradiction’s weight in the confidence formula (not its count); question generation disabled at the layer; experiment selection ranked by lowest EIG. Paper 07 §2 names each intervention and its disclosure. |
| (2) A mechanism-off control | **Met** | each mechanism is absent in its own colony, with the reference arm on the same engine and stream. `SALIENCE` is a different manipulation (retention policy) and is not used as a control for these claims. |
| (3) Equal experience and compute budgets | **Met** | identical stimulus, 3,000 cycles, and seed `20261023` in every arm; `PYTHONHASHSEED=0` in all six processes, so hash order is common-mode. |
| (4) An external outcome | **Not met** | the outcome is the internal inventory/development measure. Phase K’s external families are a separate arm, and their matched mechanism ablations all contain zero, so they cannot attribute an external effect either. |
| (5) A decision rule with uncertainty over independent worlds | **Partly met** | the verdict rule is direction-aware and compares each delta against a noise floor measured before the run, but there is **one seed per colony and one world**, so no interval over worlds exists. Phase K has intervals over ten seeds, but on tasks the organism loses by a wide margin. |

The direction rule matters more than it looks: a two-sided “did the metric move?” test scores five confirmations on this dataset, where the direction-aware rule scores two.

### 2.2 What remains open

Accordingly, this paper does not claim that contradiction or EIG is the dominant developmental variable, that questions drive development, or that inquiry is optimally allocated. Such claims require an intervention that changes the mechanism while holding the stream, engine, opportunity set, and evaluation fixed — and, on the evidence above, they additionally require an **external** outcome and an interval over independent worlds, neither of which this matrix supplies. The internal result is a reversal of the proposal’s expectation; it is not evidence that the mechanisms are inert, and Paper 07 §5 sets out the alternative reading (that an inventory measure rewards breadth, and mechanisms that focus attention narrow it) with the experiment that would separate the two.

## 3. Falsifiable next test

A suitable study would preregister: (1) the exact implementation quantity manipulated; (2) a mechanism-off or shuffled-priority control; (3) equal experience and compute budgets; (4) an external outcome such as held-out latent-rule acquisition or adaptation; and (5) a decision rule with uncertainty over independent worlds. Internal counts of questions, theories, or experiments should be secondary outcomes, not substitutes for learning performance.

**Status of these conditions.** (1), (2) and (3) are now met by the Tier-1 matrix (§2.1). (4) is not met, and (5) is met only in the weaker form of a direction rule against a measured floor, not as an interval over worlds. The next test is therefore narrower than this section originally stated: an external outcome, measured across independent worlds, for a mechanism whose on/off manipulation has already been shown to move internal structure. Paper 07 §5 lists four candidate designs, including a branch-rich world in which removing question generation should *lower* a breadth measure — the direct test of whether the reversal is about the mechanisms or about the measure.

## Conclusion

Contradiction and EIG remain plausible design hypotheses, not demonstrated explanations of Organica’s learning or comparative advantage. The scientifically useful contribution at present is the separation of implementation claims from causal and utility claims, and a protocol that could distinguish them. The internal direction is now measured, and it is opposite the original proposal’s expectation; what remains unproven is whether that direction survives an external outcome.
