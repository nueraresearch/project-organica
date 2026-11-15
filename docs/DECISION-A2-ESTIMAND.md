# `DECISION-A2-ESTIMAND` — A2 is closed

**Status:** `ADOPTED — A2 IS CLOSED AND NO A2 ARM RUNS`

**Decision ID:** `DECISION-A2-ESTIMAND-1` · **Date:** 2026-11-15 · **Tallied:** Q058
**Instruction:** decide the estimand question and record the choice as adopted (owner, 2026-11-15).

## 1. What the evidence fixes

Four things are settled, and none of them selects a branch.

1. **A1 is `VOID` and stays `VOID`.** The assembly is the study's outcome; nothing here rescinds it or re-scores it.
2. **A per-edge placebo has no witnessed construction from this selection.** On three of six seeds fewer than 95% of
   non-target edges land within the 6-cycle tolerance — 90.2%, 88.4%, 92.9%, with worst differences of 30, 51 and 78
   cycles — and a max-first search over the same budget did not find one either (89.3%, 75.9%, 85.7%). Two search
   regimes, not a proof: this does not establish that no such construction exists.
3. **An aggregate placebo is constructible.** On all six seeds the mean absolute per-edge difference is at most 2.76
   cycles and the two arms' predicted total losses agree within 8.1%.
4. **The aggregate criterion is a different criterion, not a rescue criterion.** It was specified after the per-edge test
   failed, and no document may describe it as the per-edge design succeeding.

## 2. The fork

| | **A2c′** — aggregate criterion | **A2b** — carrier-level unit |
|---|---|---|
| **Unit of inference** | the edge, as in A1 | the carrier |
| **Intervention** | remove a block of carriers | remove the carrier it names |
| **Interference criterion** | mean non-target perturbation, matched on all six seeds | local by construction; the unit *is* the removed thing |
| **Comparability with A1** | high: same target object, weaker criterion | low: a different study that inherits A1's framing |
| **What it can claim** | an edge-level effect under a stated, weaker locality condition | a carrier-level effect, which A1's question was not about |
| **What it cannot claim** | anything about per-edge locality | comparability with A1, or an edge-level effect |

## 3. Why neither branch is adopted

**A2c′ controls the total, not the distribution.** The sham matches the mean and the total, but on the three failing seeds
individual non-target edges still differ by 30, 51 and 78 cycles. The estimand is per edge, and a per-edge effect cannot
be separated from a redistribution of interference across the edges that couple to the target. Matching a mean does not
control a distribution, and adding more searches would not change that: the criterion admits the redistribution by
construction. A study whose control differs from its treatment on the quantity the estimand depends on does not identify
the effect, and A1 already failed once for precisely this reason.

**A2b's criterion cannot fail.** With the carrier as the unit and carrier removal as the intervention, the locality
condition is satisfied by definition, so it cannot fire as a check — and a gate that cannot fire is decoration (rule
25(c)). Worse, the estimand changes: a carrier-level effect is not A1's question, and calling it A2 would put a different
study's result where a reader expects this one's. That is a new study, and it would need its own target set, its own
denominators and its own criterion.

**So the fork does not reduce to an estimand preference.** Both branches were coherent as designs; neither is a test of
the question A1 asked. The choice is to close the line rather than to run a study that cannot answer it.

### The two closures are not the same kind

A1 ended because its **control failed**: the intervention perturbed non-target edges enough that C4 could not pass, and
the block was `VOID` on the assembly rather than on the idea.

A2 ends because its **control can only be obtained by changing the question**: no sham in this family is local at the
edge, and the one construction that restores locality makes the carrier the unit of inference.

The second closure is the more informative one. It does not say *we could not build the control*; it says the estimand
and this intervention family are mismatched. Stated no wider than the evidence: **within this engine, world family and
carrier-removal family, an edge-level removal effect cannot be estimated against a control that is local at the edge —
obtaining one requires changing the unit of inference.** That is a statement about this family, not about every design a
future charter might contain.

One nuance the record should not lose: **A2b is not rejected as science, only as A1's continuation.** A carrier-level
study may be worth running; it is simply not this study, and the difference is the estimand rather than the quality.

## 4. The decision

A2 is closed: the edge-level question A1 asked is not testable with this intervention, because the only control that can be matched differs from the treatment on the same per-edge quantity the estimand depends on.
The carrier-level alternative is not adopted as A2: its locality condition is satisfied by construction, so it cannot fail, and its estimand belongs to a different study.
A1 remains `VOID`, frozen and un-rescored, and this decision changes no verdict, no frozen file and no published artifact.
A future carrier-level study, if one is wanted, arrives as its own charter with its own estimand, target set and a criterion that can fail; nothing here authorises one.

## 5. What this does not do

- It does **not** assert that no A2 design exists. It asserts that none found here tests this estimand with a control that
  can carry it, and the record says so in those words.
- It authorises **no code, no cells, no engine change and no spending**.
- It does not reopen A1, alter the `VOID`, or touch the repaired scorer pin.
- It does not decide the V2 charter, which is a separate pending decision ([`DECISION-V2-CHARTER`](DECISION-V2-CHARTER.md)).

## 6. Rejected alternatives

**Adopt A2c′ because the aggregate match exists.** Because a matched total is not a matched distribution, and the per-edge estimand depends on the distribution.

**Adopt A2b because it makes interference local.** Because a criterion that cannot fail cannot license a result, and the unit change makes it a different study.

**Keep the fork open and wait for a measurement to settle it.** Because no measurement can settle an estimand question, and an open choice that nothing can close holds the line open without producing information.

**Describe the aggregate criterion as the per-edge design succeeding.** Because that is the pattern the record spent months eliminating: a failed condition, a new condition, and the new one described as if it were the old one.

**Choose by implementation convenience.** Because the two branches cost about the same to build, and the difference between them is what the study would mean.

**Run more sham search to decide.** Because a search cannot answer an estimand question; it can only report what a criterion admits, which is already known for both.

## 7. Evidence

- [`A2-SHAM-FEASIBILITY`](A2-SHAM-FEASIBILITY.md), `docs/a2_sham_feasibility.json`
- [`DECISION-A1-VOID-ACCEPTED`](DECISION-A1-VOID-ACCEPTED.md), [`A1-RUN`](A1-RUN.md)
- `docs/a1_two_path_result.json`, `docs/A1-REDESIGN-REQUIREMENTS.md`

## 8. Adoption

**ADOPTED 2026-11-15** on the owner's instruction to decide the estimand question and record the choice. This is a
delegated decision: the reasoning and its limits are above, and reversing it takes a new dated decision rather than an
edit to this one.
