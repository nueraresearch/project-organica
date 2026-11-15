# C4 risk posture — accept the exposure, accept a VOID, or redesign

**Date:** 2026-11-15

**Status:** `OPTIONS FOR OWNER DECISION — NOTHING IN FORCE; NO CELL, NO FREEZE, NO GRANT`

**Scope:** what to do about C4's exposure *before* a run. This page decides nothing, changes no threshold, adds no measurement and runs nothing. It sets out three postures and what each commits the project to.

## What C4 actually is, in the form that matters for risk

C4 is a **post-freeze VOID gate**: it cannot be evaluated before cells run, and it fails the whole run if **any** measurable non-target A, K or Y neighbour delta exceeds **0.05** (`A1-C1-C4-VOID-GATE-1`, adopted and binding). C1 is scored from the same assembly and uses the C4-expanded denominator, so the two gates share one row set.

That "any" is the whole risk. C4 is not an average, a rate or a proportion with a tolerance — it is the **maximum** over every measurable non-target delta, compared against a fixed ceiling. The exposure is therefore a count of comparisons, not a count of rows:

| Design | Non-target rows per seed | Quantities per row | Deltas per seed | Deltas across 6 seeds |
| --- | ---: | ---: | ---: | ---: |
| N=4 | **108** | A, K, Y | **324** | **1,944** |
| N=20 | **92** | A, K, Y | **276** | **1,656** |

A single edge, in a single quantity, on a single seed, above 0.05 voids the run — and per the adopted gate, C7 and C8 are then reported as `NOT ADJUDICATED — RUN VOID`, not as pass or fail.

The exposure does **not** move with target identity: 108 and 92 are the stream minus N, so filtering targets, re-selecting a competent block or changing the estimand buys **no C4 relief at all**. That is the one measured fact this page rests on, and it is why the C4 question is a risk-tolerance question rather than a design question.

## Why the failure probability is unknown, and not cheaply knowable

Nobody has measured the distribution of a non-target neighbour delta under A1's arms, so "accept the exposure" means accepting an **unquantified** VOID probability — not a small one, and not a large one. Two facts sharpen this rather than softening it:

- **There is no no-arm noise floor to borrow.** The engine is deterministic (the adversarial audit's determinism check passes), so two identical no-arm replays produce identical rows and a delta of exactly zero. A pre-freeze noise estimate from replays would measure the harness, not the intervention.
- **No multiplicity treatment is declared.** 324 comparisons per seed at a 0.05 margin, read as a maximum with no correction, is the most fragile form such a check can take. That is not an argument that C4 is wrong — a maximum is the right form for a *veto* — only that its sensitivity is unlike a single test's.

The adoption record already anticipated the honest version of this: a VOID is recorded as **not producing an admissible comparison**, not as evidence that the carrier model is false. The risk is of spending the run, not of publishing a false claim.

## The three postures

### A. Accept the current exposure

Freeze as-is: 108 / 92 non-target rows, every measurable delta, the 0.05 ceiling, no correction, no subsetting.

**Commits to:** a VOID on any single edge above 0.05 anywhere in the stream; no post-hoc correction, no "but it was only one edge" exception, no subsetting after seeing data; the reason code names the failing gate.

**Buys:** the widest possible non-interference claim — interference anywhere in the stream is caught — and C1's expanded denominator stays at full size. **Costs:** an unquantified VOID probability carried by the whole run.

### B. Narrow the measured row set before the freeze

Pre-declare a subset rule for the protected set (for example, non-target edges sharing a tag with a target, or a hash-sampled fixed count), with its own digest, before the freeze.

**Commits to:** a **narrower** claim — non-interference *on the declared subset*, not in the stream — and to declaring it early enough that it cannot be chosen with sight of any outcome.

**Buys:** fewer comparisons, so a lower VOID probability, and attention concentrated where interference is most plausible. **Costs, and this is the trap:** C1's denominator *is* the C4-expanded row set, so narrowing C4 narrows C1. On the adopted block C1 clears the floor by **three rows** at the tightest seed (64 against 61), so a protected-set haircut spends the margin of the gate that is actually the primary claim. Posture B trades the primary gate's headroom for the veto's comfort, and that trade is invisible unless it is written down.

### C. Accept that C4 may VOID and run anyway

Same design as A, with one added declaration: `A1 VOID — C1/C4` is an **expected possible outcome**, recorded in advance, and a VOID is a result about the design rather than a failed attempt.

**Commits to:** no repair, no second run, no threshold change, no denominator expansion after a VOID; the run is spent if the veto fires.

**Buys:** nothing about the probability, and it costs nothing in design — but it removes the *temptation* to renegotiate after a VOID, which is the failure mode that matters for a gate read as a maximum. **Costs:** the possibility of a run whose primary claim is unreadable because a veto on 1 of 1,944 comparisons fired.

Note that A and C are not alternatives: C is what A must say out loud. The real choice is **A (accept the exposure) versus B (buy comfort with the primary gate's margin)**.

## What each posture does to the other open decisions

| | C8 | C1 (primary) | Freeze |
| --- | --- | --- | --- |
| A | unchanged — C8's VOID is combinatorial, independent of C4 | denominator intact | can proceed |
| B | unchanged | **margin spent** (3 rows at the tightest seed) | needs the subset rule pre-registered |
| C | unchanged | denominator intact | can proceed, with the VOID declared |

C4's exposure is also independent of the competence filter, which is the reason this page can be decided before the C2/C8 rule is settled.

## Recommendation, marked as one

**A, stated as C, plus two declarations that cost nothing.**

1. **Record the multiplicity in the act**, not as a correction but as a fact: C4 is the maximum over 324 deltas per seed, 1,944 across the block, with no correction applied. A reader who knows the form can judge a VOID; a reader who does not will read a single failing edge as a broken design.
2. **Name the failing edge and quantity** in the reason code — `C4_DELTA` should carry the edge, the quantity (A, K or Y) and the seed. A veto that cannot say what fired is indistinguishable from a harness bug, and this project has already been burned once by a gate that failed on the wrong basis under the right name.
3. **Record that the VOID probability is unmeasured** and why it cannot be cheaply measured pre-freeze on a deterministic engine. That sentence is the difference between accepting a risk and forgetting one.

If the owner's tolerance is lower than that, the lever is **not** posture B — it is delaying the C4 question until a treatment-side noise measurement exists, which is a pre-freeze diagnostic and would need to be declared as one rather than slipped in as a design tweak.

## What would change this

A measured distribution of non-target neighbour deltas under the A1 arms would replace the unknown VOID probability with a number and make A or B a calculation instead of a posture. A decision to make C4 advisory rather than a VOID gate would dissolve the question — and would also remove the only check that the arms leave the rest of the stream alone, which is what licenses reading C1 as a separation effect at all.

## Reproduce the exposure figures

```bash
python -m benchmarks.a1_design_viability --check     # non-target rows 108 / 92, by N
```

Reads committed no-arm artifacts; runs no engine. The delta counts are multiplication on those row counts (×3 quantities, ×6 seeds), not a measurement.
