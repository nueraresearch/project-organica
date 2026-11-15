# `DECISION-A2-ESTIMAND` — what A2 must preserve

**Status:** `DRAFT — AWAITING THE OWNER'S ESTIMAND CHOICE`

**Decision ID:** `DECISION-A2-ESTIMAND-1` · **Date:** 2026-11-15

**Decides:** whether an A2 study keeps the edge as its unit of inference and weakens the interference criterion, or
changes the unit to the carrier and keeps the criterion strict.
**Does not decide:** whether A2 runs. Either branch needs its own charter, criterion and grant, and neither is authorised
here.

## 1. What the evidence fixes

Three things are no longer open.

1. **A1 is `VOID` and stays `VOID`.** The assembly is the study's outcome; nothing here rescinds it or re-scores it.
2. **A per-edge placebo has no witnessed construction from this selection.** On three of six seeds fewer than 95% of
   non-target edges land within the 6-cycle tolerance — 90.2%, 88.4%, 92.9%, with worst differences of 30, 51 and 78
   cycles — and a max-first search over the same budget did not find one either (89.3%, 75.9%, 85.7%). Two search
   regimes, not a proof: this does not establish that no such construction exists.
3. **An aggregate placebo is constructible.** On all six seeds the mean absolute per-edge difference is at most 2.76
   cycles and the two arms' predicted total losses agree within 8.1%.

Fixed, too, is the language: the aggregate check is **a different criterion, not a rescue criterion**. It was specified
after the per-edge test failed, and no document may describe it as the per-edge design succeeding.

## 2. The fork

The two survivors differ in what they ask, not in how well they are engineered.

| | **A2c′** — aggregate criterion | **A2b** — carrier-level unit |
|---|---|---|
| **Unit of inference** | the edge, as in A1 | the carrier |
| **Intervention** | remove a block of carriers | remove the carrier it names |
| **Interference criterion** | mean non-target perturbation, matched on all six seeds | local by construction; the unit *is* the removed thing |
| **Comparability with A1** | high: same target object, weaker criterion | low: a different study that inherits A1's framing |
| **What it can claim** | an edge-level effect under a stated, weaker locality condition | a carrier-level effect, which A1's question was not about |
| **What it cannot claim** | anything about per-edge locality | comparability with A1, or an edge-level effect |

## 3. The question that decides it

**Does the study's next claim need to be about edges, or about carriers?**

- If the claim is about edges — "this edge's removal changed behaviour" — choose **A2c′**, and write the aggregate
  criterion into the charter as the weaker locality condition it is.
- If the claim is about carriers — "this carrier's removal changed behaviour" — choose **A2b**, and state in the charter
  that the estimand changed, so nothing later can be compared to A1 as if it had not.

There is no fourth option in which the edge-level estimand keeps its per-edge criterion without a witnessed
construction: item 2 above leaves that option unbuilt.

### The record, in three sentences

A2 keeps the edge as its unit of inference and adopts an aggregate non-target criterion, or it changes the unit to the carrier and keeps a strict criterion; the record chooses neither until the owner states which claim the study must support.
Whichever branch is chosen, its criterion is pre-committed in its own charter, and the aggregate criterion is never described as A1's per-edge criterion succeeding.
Neither branch is authorised to run by this record: each needs its own charter, freeze and grant.

## 4. What either branch must carry

- Its own pre-committed criterion, fixed before a cell runs, in the charter's own words.
- The disclosure sentence: *this criterion is not A1's, and the difference is the point*.
- A statement of what the branch cannot claim, written before the result is known.
- Its own freeze, pin and gate order, with `VOID` stopping interpretation before any effect is quoted.

## 5. Rejected alternatives

**Describe the aggregate criterion as the per-edge design succeeding.** Because that is the pattern the record spent months eliminating: a failed condition, a new condition, and the new one described as if it were the old one.

**Choose by implementation convenience.** Because the two branches cost about the same to build, and the difference between them is what the study would mean.

**Run more sham search to decide.** Because a search cannot answer an estimand question; it can only report what a criterion admits, which is already known for both.

**Keep A1's C4 unchanged and call A2 "A1 with a better placebo".** Because no placebo meets C4, so that description has no referent.

## 6. Evidence

- [`A2-SHAM-FEASIBILITY`](A2-SHAM-FEASIBILITY.md), `docs/a2_sham_feasibility.json`
- [`DECISION-A1-VOID-ACCEPTED`](DECISION-A1-VOID-ACCEPTED.md), [`A1-RUN`](A1-RUN.md)
- `docs/a1_two_path_result.json`, `docs/A1-REDESIGN-REQUIREMENTS.md`

## 7. Signature

**Choose:** `DECISION-A2-ESTIMAND — A2c′ (edge-level, aggregate criterion)` or
`DECISION-A2-ESTIMAND — A2b (carrier-level unit)`, owner, date. **Or close the line:**
`DECISION-A2-ESTIMAND — NEITHER`, owner, date.

Until signed, this document records a fork and chooses nothing.
