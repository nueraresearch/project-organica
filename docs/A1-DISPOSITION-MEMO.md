# A1 disposition memo — redesign or park

**ID:** `A1-DISPOSITION-1`  
**Date:** 2026-11-14  
**Status:** `DRAFT — OWNER DECISION REQUIRED; NO FREEZE, NO GRANT, NO RUN`  
**Decision owner:** ____________________  
**Decision and date:** ____________________

**This memo records the choice and its criteria; it does not choose.** The manifest remains `REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT`; no target is frozen, no seed is reserved and no A1 cell has run.

## 1. The decision

Should A1 be **redesigned as a new protocol**, or **parked**? The current design is blocked below the adopted C1 floor. The choice is whether to fund a successor that can reach it, or close the branch without claiming an answer.

## 2. Fixed evidence

- **C1:** the candidate ceiling is **31–44** rows per seed. Changing N, replacing N4 with N20, or reranking targets cannot raise it. The 112-row stream is **382 candidate + 286 reverse + 4 extra** rows, collapsing to **384 unique undirected edges**; reverse orientation is duplication, not a rescue.
- **K is limiting:** A is available on **281/382**, K on **228/382**. **95** rows have A without K, **42** have K without A, **59** have neither. The shortfall to 60 is **16–29 rows** per seed; K is lower than A on five seeds and tied on one.
- **No cheap local lever:** K rises from **31.8%** in the lowest cycle-36 U quartile to **89.1%** in the highest, but the high-U half has only **28–31 edges** per seed. **154/382** rows never form K; only **28/228** available rows form it after cycle 60. Tag rates span **44.7–77.1%** pooled but **0–100%** by seed; candidate/reverse pairs agree **97.2%**; the universe is near-regular. Tags, orientation and degree are not credible levers on these six seeds.
- **C2/C8 are a selection problem, conditionally:** the pool has **23–36 A&K-available rows** per seed and a 20-row matching exists on **6/6**; the current N4 block supplies only **12/24** competent rows. A competent N20 block is constructible but **pre-treatment rather than future-blind** to the no-arm baseline; it changes the estimand and **still does not repair C1**.

## 3. Redesign branch — requirements

A successor is admissible only if **all** requirements are met before any target freeze. The table compares what each branch changes.

| Scope | Redesign | Park |
| --- | --- | --- |
| C1 stream | New independent universe or seed block; no-arm preflight shows **≥60 K-available independent rows per seed**. | Close the current **31–44** stream; do not retry target selection. |
| K rate / size | At 63–64 edges, **93.8–95.2% K**; a larger universe lowers the rate: 80 edges → **75%**, 96 → **62.5%**, 120 → **50%**. | No K repair; park does not claim K is unavailable in principle. |
| Targets | If C2/C8 remain in scope, **20 competent targets per seed** under a declared baseline A+K screen, with the estimand change recorded. | No new target selection; C2/C8 are **not adjudicated**. |
| Estimator / floor | Keep the **0.95 / 60** rule unless separately reopened as a scientific change. | No change. |
| Universe / scorer | `run_cell`, selection, result assembly and manifest use **one edge universe**; the N20/N4 mismatch is removed. | Fix independently if desired; not a condition of park. |
| Governance | New protocol, freeze, seed reservation and dated grant; current acts are not reused. | **No freeze, no grant, no run.** |
| Cost | Fund the preflight, then a new campaign only if it passes. | No new campaign; preserve the existing artifacts. |

**Stop rule:** if the no-arm preflight cannot show 60 K-available rows on every seed, **do not freeze, do not grant and do not run**. Return to disposition; do not relax the floor, add non-competent rows, or select a more favourable seed subset after seeing the preflight.

A redesign may target **C1 only**, but must declare C2/C8 **not adjudicated**; it may not claim C2/C8 coverage without the competent-target protocol.

## 4. Park branch — criteria

Park is defensible if any of the following holds:

- No fresh universe or seed block reaches 60 K rows without selecting seeds or edges on the same no-arm baseline that judges them.
- The only route to 60 is changing the estimator or lowering the floor without independent justification — a different study, not a repair.
- The competent-target policy is rejected as too large an estimand change, and C1-only redesign is not worth the cost.
- The universe/scorer inconsistency and governance work cannot be closed within a bounded protocol, or the expected information gain does not justify a new freeze/grant cycle.

**Park means** recording A1 as **not run / not identified under the current design**, with C1 as the blocking gate. It **does not mean treatment failure**, a negative C2/C8 result, or evidence that the effect is absent. Preserve the ceiling, dedupe, baseline, target-viability and K-decomposition records; do not re-select targets or reinterpret the unrun cells.

## 5. Decision rule

| Condition | Disposition |
| --- | --- |
| Fresh universe/seed block passes **≥60 K on every seed**, with one scorer and a pre-registered competence policy if C2/C8 are in scope. | **Redesign**, then freeze, grant and run under the new protocol. |
| No such preflight exists; only a floor/estimator change or selection on the judging baseline remains. | **Park**, without a treatment claim. |
| The preflight is not built, but a bounded path to it exists. | **Hold**; sign nothing and fund only the preflight. |

**Current default:** hold. The N4 and N20 freeze acts remain unsigned, the grant is absent and the manifest is unfrozen. Holding is not a third disposition; it is the required state until one branch is chosen.

## 6. What would settle it

The decisive artifact is the **no-arm successor preflight**, now exercised on a predeclared fresh seed block: the block `20650101–20650106` fails **0/6**, with C1 ceilings **40, 37, 46, 42, 31, 38** and a best gap of **14** rows. It was fixed without K screening and was not selected on high K, so this is not a selected-on-the-baseline result; a one-seed timing probe did not alter the block. The preflight reports independent edges, K-available count and C1 ceiling per seed, whether 20 competent targets can be matched if C2/C8 are in scope, and the exact universe used by the runner and result layer. This one block does not clear 60; it also does not prove that no fresh block could. A second predeclared candidate, a **28-tag larger universe**, cleared the structural target at **158–172** independent edges but failed worse at C1 **23, 40, 42, 55, 47, 37**, with K diluted to **23–55** and matching below 20 on four seeds. Under the stop rule, the tested same-world and larger-world constructions both fail; **park** is the defensible default unless a different predeclared construction clears the floor without post-hoc selection.

**Not evidence:** a decision memo. It runs no cell, freezes no target, reserves no seed, issues no grant and makes no treatment claim.

## References

- [C1 ceiling and conditional C2/C8](A1-DESIGN-VIABILITY.md)
- [K-availability decomposition](A1-K-DECOMPOSITION.md)
- [N20 competent-selection rule](A1-N20-COMPETENT-SELECTION.md)
- [Baseline availability](A1-BASELINE-AVAILABILITY.md)
- [Target viability](A1-TARGET-VIABILITY.md)
- [Successor preflight](A1-SUCCESSOR-PREFLIGHT.md)
- [Fresh-seed candidate](A1-SUCCESSOR-CANDIDATE.md)
- [Successor requirements](A1-REDESIGN-REQUIREMENTS.md)
- [Candidate schema](A1-SUCCESSOR-SCHEMA.md)
- [Park recommendation](A1-PARK-RECOMMENDATION.md)
- [Pre-freeze checklist](A1-PRE-FREEZE-CHECKLIST.md)
