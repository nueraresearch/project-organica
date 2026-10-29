# Organica V2 — Capacity Sub-Brief
## Preserve useful structure under bounded capacity

> **This is a SUB-BRIEF of [`docs/ORGANICA-V2-DESIGN-BRIEF.md`](ORGANICA-V2-DESIGN-BRIEF.md)**,
> which is the overall V2 plan. This one scopes a single question. The two are
> not competing plans, and neither authorises a build.
>
> **Read the addendum below before using this brief.** Four diagnostic probes
> run on 2026-10-28 changed the premise of this document.

### Addendum (2026-10-28): the premise of this brief was measured and it does not hold

The brief below frames the V2 problem as **bounded structural allocation** —
how to preserve more useful structure under a declared budget. Four probes
(`docs/GATE13-CAUSAL-ACCOUNT.md`) say the frame is wrong: **the constraint is
not the budget, and not the allocation rule either. It is precision.**

| Measurement | Result |
|---|---|
| The world's 112 edges are in the `precedes` table | **yes** — raw temporal coverage **0.97–1.00** on every seed and both stimulus shapes |
| The engine's asserted structure at the frozen cap | **0–3 of 112** — inter-cell (law-bearing) edges **0–3**, intra-cell **28–39** |
| Coverage vs the global cap (20 / 40 / 80 / uncapped) | **0.00 → 0.04–0.07 → 0.09–0.18 → 0.99–1.00** — a steep monotone dose-response needing **240–244** asserted edges, ~12× the budget |
| Coverage vs a **per-source** allocation rule (objective 1 below) | **not** the fix — per-source K=10 retains 258–286 edges for coverage 0.72–0.77, where the global rule reaches 0.95–0.97 at 320 |
| Precision at every budget and under both rules | **never exceeds 0.3443** |
| A world-vocabulary filter (oracle) | precision **0.35 → 0.5333** at **unchanged coverage 1.0000** |

**Two of this brief's design objectives are now measured and must be restated.**

**Objective 1 (source-level budget distribution) is refuted as the primary
fix.** A per-source quota does not rescue acquisition at a modest budget; it
merely spends a comparable number of edges more evenly and reaches lower
coverage than the global rule does at a slightly larger budget. Per-source
distribution may still be worth having — it is the mechanism by which a
high-frequency node stops monopolising slots — but **it is not sufficient**, and
it is not the thing to build first.

**Objective 2 (evidence-type separation) is necessary but not sufficient.** The
within-cell/cross-cell crowding is real, but a 1-tag stimulus removes the
within-cell pairs *by construction* and still fails Gate 13 on **0 of 6** seeds
(asserted coverage 0.1719–0.1953). Separating evidence types cannot be the
whole fix.

**What the measurements point at instead.** In a candidate space where the
world's edges are about a third of the rows and are not clustered at the top of
any frequency ordering, **no frequency-based selection can find them**. Layer 1
ranks by raw count; the world does not co-occur in count order. The two halves
of the real question are therefore:

1. **Vocabulary.** Can the organism tell which of its vocabulary items are its
   own, rather than incidental words? A perfect filter buys precision
   0.35 → 0.53 at no coverage cost — and the filter measured is an **oracle**
   (`TAG_POOL`), so the organism-side version is the open question.
2. **Ranking.** Can candidates be ranked by something other than raw frequency?
   The engine currently has no criterion to offer.

**No V2 build is authorised by this addendum.** It narrows the question and
records what has been ruled out.

---

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
