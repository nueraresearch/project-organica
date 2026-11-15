# C4 declaration — adopted 2026-11-15 (posture A)

**ID:** `A1-C4-POSTURE-1`

**Date:** 2026-11-15

**Status:** `ADOPTED — BINDING FOR A1; NO FREEZE, NO GRANT, NO RUN`

**Decision owner:** owner direction, 2026-11-15.

**Adopted text:** the five clauses in "The declaration, verbatim" below, unchanged at signature.

**Scope:** the C4 posture text only. It changes no threshold, no row set, no gate and no code. Adoption is a signature and a date.

## Why this is a text and not a build

[`A1-C4-RISK-POSTURE`](A1-C4-RISK-POSTURE.md) recommends accepting the exposure and declaring three things about it: the multiplicity, what a failure must name, and the fact that the failure probability is unmeasured. This document writes those three as adoptable clauses.

**Every field it requires already exists.** `a1_arms.score_c4` records `rows`, `measured`, `unmeasured`, `max_delta` and a `violations` list whose entries already carry `seed`, `cell`, `edge`, `path` (A, K or Y) and `delta`. So the declaration can be adopted **without touching a line of code or a single artifact schema** — which is the only form of declaration a pre-freeze record should take.

## The declaration, verbatim

> **C4 non-interference posture, adopted 2026-11-15.**
>
> C4 remains a post-freeze VOID gate at the unchanged **0.05** absolute neighbour-delta ceiling, read as the **maximum** over every measurable non-target A, K and Y delta. On the adopted block that is **108 non-target rows × 3 quantities = 324 deltas per seed and 1,944 across six seeds** (N=20: 92 rows, 276 per seed, 1,656 across the block). The exposure is fixed by N and the stream, not by target identity: no target filter, competence screen or estimand change alters it.
>
> **1. The multiplicity is declared, not corrected.** No multiple-comparison correction is applied before or after the run. The gate is a maximum by design — a veto on interference anywhere in the stream — and its sensitivity is that of 1,944 comparisons rather than of one test. A C4 pass may be reported as the absence of any delta above the ceiling, and may not be reported as evidence that interference is small or absent on average.
>
> **2. A failure names what fired.** A C4 failure carries `C4_DELTA` together with every violation, each with its **seed, cell, edge, quantity (A, K or Y) and delta**, ordered by delta descending, at the recorded precision. A C4 failure that cannot name its edges is not a C4 result and may not be reported as one.
>
> **3. The VOID probability is unmeasured.** No distribution of a non-target neighbour delta under these arms has been measured, and it cannot be measured before the freeze without amending the blindness rule ([`A1-C4-NOISE-FEASIBILITY`](A1-C4-NOISE-FEASIBILITY.md)). The engine is deterministic within a process and **nearly invariant across processes** — across six `PYTHONHASHSEED` values, 16 of 17 recorded fields have exactly zero spread and one varies slightly — so run-to-run dispersion exists but is small, and its size for a C4 delta is unknown. The run therefore proceeds with an **unquantified** probability of `A1 VOID — C1/C4`. This is recorded as a known unknown, not as a small risk.
>
> **4. A VOID is a result about the design.** Under `A1-C1-C4-VOID-GATE-1`, a C4 failure makes the run `A1 VOID — C1/C4`, with C7 and C8 reported as `NOT ADJUDICATED — RUN VOID`. No second run, repaired denominator, threshold change, subsetting or post-hoc correction follows from a VOID. The reason code and the named violations are the deliverable.
>
> **5. Nothing is relaxed.** The ceiling, the maximum, the 108/92-row non-target set, the six-seed scope and the `C4_UNMEASURABLE` condition are unchanged by this declaration. What is fixed here is only what the record must say.

## A defect found while writing this text, and fixed

Drafting clause 2 exposed a hole in the gate it describes, so it was repaired before this text could be
signed: **an unmeasurable delta read as a pass.**

`gate_c4` tested `float(delta[path]) > tolerance`. For `nan` that comparison is `False`, so a row whose
delta was non-finite — the exact case rule 13 of the repository charter says must be reported as *not
measurable* — passed the gate as clean. A `None` delta crashed assembly instead (`float(None)` raises), and
a delta dict missing a path was likewise only caught by accident.

Fixed on 2026-11-15 with three tests:

- `gate_c4` now fails on a missing path, a `null`, a non-numeric or a non-finite value, so an unmeasurable
  row is a **failure of the veto**, never a pass.
- `score_c4` records such rows under `unmeasured` with a `reason` (`delta_missing`, `delta_not_a_number`,
  `delta_not_finite`) instead of a violation carrying `delta: None`, so the VOID carries
  `C4_UNMEASURABLE` rather than a bare `C4_DELTA`.
- Non-finite values no longer enter `max_delta`, where `max(0.0, nan)` silently returns `0.0`.

Consequence for clause 2: **every violation now carries a finite delta**, which is what the clause promises.
No threshold, row set or gate verdict for a measurable stream changed — only the treatment of rows that
were never measurable.

## The field map the clauses rely on

| Clause | Field | Where it lives |
| --- | --- | --- |
| 1 — multiplicity | `rows`, `measured`, `unmeasured` (comparisons = `measured` × 3) | `score_c4` return |
| 1 — sensitivity | `max_delta` = {A, K, Y} | `score_c4` return |
| 2 — names the failure | `violations[]` = {`seed`, `cell`, `edge`, `path`, `delta`} | `score_c4` return |
| 3 — unmeasured probability | no field; a statement, with the near-invariance evidence | this document; `docs/process_noise.json` |
| 4 — VOID disposition | `C4_DELTA`, `C4_UNMEASURABLE`, `C1_C4_INCOMPLETE` | `a1_result._void_reasons` |

One optional addition, and only if the owner wants it: `score_c4` could record the two rates whose difference a violation reports. The delta and the edge already identify the failure, so this is a convenience, not a requirement, and adding it now would make the declaration depend on a code change it does not need.

## What adoption does and does not do

**Does:** satisfies `C4_exposure_acceptance`, the last unsatisfied precondition on both freeze acts; fixes the vocabulary (unquantified risk rather than small risk; maximum rather than average) before any outcome is seen; and makes a VOID attributable rather than mysterious.

**Does not:** freeze a target, reserve a seed, authorise a cell, change a threshold, narrow the protected set, or re-issue the freeze acts. Those remain separate owner acts — the acts still read `HELD` until they are re-issued.

## If the owner chooses differently

This text is posture A. Under posture **B** (narrow the protected set) clause 5 must be amended and the row counts replaced, and C1's denominator shrinks with them — the trade recorded on the risk page. Under posture **C** (accept a possible VOID explicitly) clauses 1–3 survive and clause 4 becomes the centre of the posture. The three clauses are independent enough that any combination can be adopted by editing only the sentences they touch.

## Adoption record

**Adopted 2026-11-15, posture A, with the five clauses unchanged.** The decision source is the dated owner
direction in the header; no clause was edited at signature, and the `nan`/`null` gate repair recorded above
is part of the state of the code the declaration describes.

What this satisfies is `C4_exposure_acceptance`, the last precondition the freeze acts were waiting on. What
it does not do: freeze a target, reserve a seed, authorise a cell, change a threshold, narrow the protected
set, or re-issue the freeze acts. Those remain separate owner acts.

In order, what follows: draft the disposition against this posture, re-issue both freeze acts with fresh
digests, then the grant, then the run.

## Reproduce

```bash
python -m benchmarks.a1_design_viability --check     # non-target rows 108 / 92, by N
```

The 324 / 1,944 figures are multiplication on those row counts (×3 quantities, ×6 seeds). No engine ran for this document.
