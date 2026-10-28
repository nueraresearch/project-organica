# Organica V2 Design Brief
## Preserve useful structure under bounded capacity

### Purpose

Organica V1 failed the preregistered acquisition gate on the tested compositional worlds. In five paired diagnostic runs, raising the prediction-candidate cap from 20 to 1,000 changed final asserted coverage from 0–3 of 112 world edges to 110–112. This is strong evidence that the V1 cap and its frequency-based ranking block acquisition on this task.

The finding is specific to this engine–task pairing. It does not establish that higher capacity improves learning on other tasks, or that transfer has been demonstrated.

### Research question

Can Organica preserve useful, lower-frequency structure under a fixed resource budget, without receiving task labels or privileged knowledge of the world’s latent factors?

### Design objective

Replace the single global top-20-by-count bottleneck with a bounded candidate-selection method that retains both strong evidence and structurally diverse evidence. The selection rule must be generic: it cannot use the generator’s cell identities, hidden causes, or ground-truth edges.

Specific architectural objectives include:
1. **Source-level budget distribution:** The single global ranking allows high-frequency source tags to monopolize all candidate slots, starving other vocabulary elements. V2 should explore generic structural distribution rules (e.g. per-source prediction quotas, coverage-aware allocation, or entropy-weighted ranking) so that outgoing predictive capacity is distributed across the observed vocabulary rather than captured by a few high-count nodes.
2. **Evidence-type separation:** V2 should distinguish candidate evidence types—such as within-event co-occurrence and temporal predecessor/successor transitions—so that high-density co-occurrence clustering cannot silently crowd out temporal transition structure.
3. **Inspectable lifecycle:** Candidate admission, survival through natural selection, and readout projection must remain separately tracked and verifiable.

### Design constraints

- Keep the V1 engine frozen and preserve its results as the comparison baseline.
- Treat cap 1,000 as a diagnostic upper-capacity condition, not as the presumed V2 solution.
- Define a resource budget before choosing a new selection rule.
- Record which candidates were admitted, retained, displaced, and why.
- Keep task metadata and ground truth outside the organism’s input.
- Preserve explicit acquisition, transfer, and revision outcomes; report transfer as unmeasurable when acquisition fails its preregistered gate.

### Evaluation plan

Before confirmatory runs, compare V1, the high-capacity diagnostic, and the proposed V2 selection rule on scratch runs. Measure:

1. **Asserted-edge coverage, precision, and efficiency:** Evaluate not merely recall against world edges ($\text{coverage} \ge 0.50$), but also graph precision:
   $$\text{Precision} = \frac{|\text{asserted} \cap \text{world}|}{|\text{asserted}|}, \quad F1_{\text{graph}} = \frac{2 \cdot |\text{asserted} \cap \text{world}|}{|\text{asserted}| + |\text{world}|}$$
   A viable V2 mechanism must not solve coverage through indiscriminate candidate explosion (as cap 1,000 did with 241 asserted edges for 110 world edges).
2. **Candidate survival lifecycle:** Track retention and decay rates from initial admission through natural selection to ensure candidate stability across sleep cycles.
3. **Downstream layer protection & distractor resistance:** Test on decoy worlds with high-frequency noise distractors. The selection rule must resist filling its diversity budget with spurious noise, and downstream layers (Layers 2–5: composites, workflows, and hypotheses) must not suffer combinatorial degradation from the candidate pool.
4. **Prediction and transfer performance:** Benchmark prediction accuracy against the fixed Replay, Statistical, and Bayes ceiling references.
5. **Resource bounding:** Audit memory footprints, DB insertion volumes, and sleep-cycle computation times under the declared budget.

Pre-register the selection rule, resource budget, seeds, gates, and analysis before using untouched confirmatory seeds. Keep the five inspected seeds diagnostic.

### Decision rule

Proceed with the V2 design only if it improves useful structure retention within the declared budget, maintains acceptable graph precision without degrading downstream layers on distractor worlds, and passes the acquisition gate on untouched seeds. Passing that gate permits a transfer test; it does not itself establish transfer or human-like learning.
