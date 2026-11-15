# Can a treatment-side noise measurement be declared pre-freeze?

**Date:** 2026-11-15

**Status:** `ANALYSIS — NO RUN, NO CELL, NOTHING IN FORCE`

**Scope:** whether the C4 VOID probability can be measured before the freeze, and what that would cost. No threshold, row set or gate changes here, and no cell runs.

## First: a premise I stated was wrong

[`A1-C4-DECLARATION`](DECISION-A1-C4-POSTURE.md) clause 3 says the probability cannot be measured because "the engine is deterministic, so two no-arm replays are identical and their delta is exactly zero". **That is too strong, and the repository's own artifacts contradict it.**

CPython randomises string hashing per process, so set and dict iteration order varies between runs; that is why `benchmarks/process_noise.py` exists and why it re-runs a cell under six `PYTHONHASHSEED` values and reports the spread of every field. Its recorded result: across six hash seeds, **16 of 17 measured fields have exactly zero spread**, and one field (`M5_development_velocity.new_per_100_cycles`) varies slightly (`docs/process_noise.json`).

So the accurate statement is: the engine is **deterministic within a process and nearly invariant across processes** — not invariant by construction. Which means a treatment-side noise measurement is **well-posed**, and this question has a real answer instead of a definitional one.

## What such a measurement would be

Replay the A1 arms on a declared block under several hash seeds and record the spread of the **non-target neighbour deltas** C4 reads — the same design `process_noise.py` already uses for the matrix, applied to the C4 quantity instead of the matrix metrics. Cost scales as `seeds × cells × hash seeds`; at four cells and six hash seeds per seed that is 144 cell-runs for a six-seed block.

It would answer exactly the question the risk page left open: **the dispersion of a C4 delta under these arms**, and therefore whether 324 comparisons against a 0.05 ceiling is comfortable or fragile.

## The blindness problem, stated precisely

The freeze order forbids this as things stand, and not by implication:

> "The post-freeze route preserves the precommitted thresholds and blindness: **no outcome is observed before the target manifest and grant are fixed**." — [`A1-C4-GATE-ORDER`](A1-C4-GATE-ORDER.md)

A noise measurement of the arms observes outcomes — deltas — before that. It is not a no-arm preflight: it runs the intervention, sees how the intervention behaves, and hands the owner a number that bears directly on whether to freeze and run. Any claim that this "does not break blindness" rests on narrowing blindness to *the reserved block's* outcomes, which is a **change to the rule, not an application of it**.

It can be done without breaking the parts of blindness that matter most, but only if the owner amends the rule in these terms:

1. **Disjoint block.** A diagnostic seed block drawn and named before the run, disjoint from every reserved seed, with its own digest.
2. **Dispersion only.** The output is a spread statistic — standard deviation and quantiles of the absolute non-target delta — with **no gate verdict, no sign, no per-arm mean** reported. It may not be described as an effect of any kind.
3. **Sealed use.** The number may not change the target rule, the threshold, the row set, the N_min floor or the decision to freeze. Any design change it motivates must be recorded as a design change, dated, and disclosed as motivated by pre-freeze outcome data.
4. **One block, once.** No re-running to tighten the estimate after seeing it.

Even then, the honest description is "**no outcome from the reserved block before the freeze**", not "no outcome before the freeze". That sentence is the amendment, and it is the owner's to make.

## What it would cost

| Cost | Size | Note |
| --- | --- | --- |
| Cells | 144 runs (6 seeds × 4 arms × 6 hash seeds) | the closest precedent is the no-arm preflight, not a full campaign; per-cell runtime is not recorded for A1 |
| Seeds | one six-seed block | drawn from the declared space, named and digest-recorded before use |
| **The first grant** | a dated authorisation | cells cannot run without one, so the project's first grant would authorise a diagnostic rather than the experiment |
| The blindness rule | amended in writing | the property that most protects the freeze, traded for a dispersion estimate |
| Disclosure | permanent | every later reading must note that pre-freeze outcome data existed |
| Transfer | assumption | dispersion on a disjoint block is not the reserved block's dispersion |

## What it would buy, and whether that is worth it

It converts "unquantified VOID risk" into an estimate, which is the one thing the C4 posture currently cannot offer. That is genuine decision value — the posture becomes a calculation instead of a tolerance.

Against that: the engine's measured near-invariance across hash seeds (**16 of 17 fields exactly zero spread**, one slightly variable) suggests the dispersion component is *small*, so the number is likely to come back saying the risk is modest — plausible, useful, and unremarkable. And the dominant source of C4 spread may not be hash order at all but the **world**: deltas differ across seeds because the world differs, and that is variation the diagnostic cannot reduce, only describe.

## Recommendation, marked as one

**Do not run it.** Three reasons, in order of weight:

1. It requires **amending the blindness rule** to buy a number. The freeze's protection rests on no outcome existing before the manifest is fixed; spending that to learn a dispersion is a poor trade for a diagnostic whose likely answer is "small".
2. Its **information value is low given the measured invariance**: 16 of 17 fields move not at all across six hash seeds. If C4 turns out fragile, the likelier cause is the ceiling relative to world-level variation, which no hash-seed replay reduces.
3. It costs the project's **first grant**, normalising pre-freeze treatment runs — a precedent that would be expensive in every later phase.

What to do instead, at no cost: keep the unquantified probability **and correct the reason** — not "determinism makes it exactly zero", but "the engine is nearly hash-invariant and the arms' C4 dispersion is unmeasured". Then pre-declare how a VOID will be read (one edge versus many, largest delta first), so the number is interpretable when it exists without being purchaseable in advance.

If the owner's tolerance genuinely requires a number, do it under the four amendments above, on a named disjoint block, disclosing that pre-freeze outcome data exists. That is defensible; calling it "not breaking blindness" would not be.

## What would change this

A hash-seed replay of a **single no-arm cell** that shows the non-target availability rows varying at all would raise the prior considerably and make the diagnostic worth its cost. That measurement is no-arm, cheap, declares no treatment outcome, and does not touch the blindness rule — it is the one pre-freeze probe available without an amendment, and it has not been run for the A1 arms.

## What this document changes elsewhere

It corrects the determinism premise in [`A1-C4-DECLARATION`](DECISION-A1-C4-POSTURE.md) clause 3 and the matching sentence on [`A1-C4-RISK-POSTURE`](A1-C4-RISK-POSTURE.md). The conclusion of both documents stands — the probability is unmeasured — but the reason is a narrow, measured near-invariance rather than an exact zero.
