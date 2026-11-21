# Assertion provenance: the pressure test

**Status: `CONSTRAINT-ASSERTION-PROVENANCE-1` was withdrawn as written on 2026-11-19, before a
grant. No cell ran.** The draft and its term sheet are kept in
[`constraint_registrations/assertion-provenance.json`](constraint_registrations/assertion-provenance.json);
this page records why it cannot enter test in that form. Every figure below is derived from
`docs/phase_k_results_0.15.0.json` and checked by
`benchmarks/assertion_provenance_pressure_test.py --check` — do not type a number into this page;
change the artifact and run `--write`.

## The figures

<!-- BEGIN PRESSURE TEST FIGURES: generated from docs/phase_k_results_0.15.0.json by benchmarks/assertion_provenance_pressure_test.py; do not edit by hand -->
| Quantity | Value |
|---|---|
| K1 seeds | 10 |
| Organica precision | 0.181818-0.189474 |
| Organica recall | 1.000000 |
| Organica F1 | 0.307692-0.318584 |
| Organica mean F1 | 0.312011 |
| Best-of-grid precision | 0.782609-0.947368 |
| Best-of-grid recall | 1.000000 |
| Best-of-grid F1 | 0.878049-0.972973 |
| Best-of-grid mean F1 | 0.935972 |
| Mean gap (Organica minus best) | -0.623961 |
| Emitted pairs behind the eighteen true ones | 19-23 |
| Cooccurrence grid | 15 configurations per seed |
| Distinct results per seed | 3-5 |
| Seeds whose nine long-window configurations coincide | 10 of 10 |
| That collapsed point's F1 | 0.857143 |
| Gain of the best configuration over it | 0.020906-0.115830 |
| Seeds whose maximum is tied | 6 |
| Configurations that ever win | window 30 / floor 5, window 75 / floor 10 |
| Draft pass bar | 0.412011 |
| Pass bar below the best-of-grid mean | 0.523961 |
<!-- END PRESSURE TEST FIGURES -->

## What the engine already does

Two facts settle most of it before any measurement.

1. **The rule is already a label.** `organica/sleep_extraction.py` `_build_predictions` sets
   `is_cooccurrence` on a candidate iff the *unordered* pair is in the co-occurrence table, which
   `organica/memory.py` `_record_cooccurrences` fills from the tags of one event. Allocation then
   spends half the budget on transition-labelled rows, fills the rest from cooccurrence-labelled
   rows, and backfills unused seats with further transitions. "Count a pair as asserted only with
   within-event support" therefore selects a bucket the engine already computes and already caps.
2. **The rule is already a baseline.** `benchmarks/phase_k_campaign.py` `_score_models` sweeps
   `cooccurrence` — pairs that co-occur inside a window with a count floor — over a window x
   `min_count` grid and keeps the best. That best is the strongest-of-grid the endpoint subtracts,
   and it is what the ledger's `baseline_gap` measures against.

## Q1: the recall guard has no firing condition on this world

The guard was supposed to fire when a true pair lacks within-event support. It cannot, here. The
comparator recalls all eighteen gold pairs at a count floor of ten within a 75-cycle window (eight
of ten seeds; the other two reach the same at 30 cycles and a floor of five). So every gold pair is
in the co-occurrence table with a high count. Organica already asserts all eighteen, and each of
those rows is cooccurrence-labelled because its pair is in the table. The filter therefore cannot
remove a true pair: recall stays at its ceiling by construction and the guard holds automatically.

A guard that cannot fail is decoration (rule 25). The condition is not merely unmet — it is absent
from the world. K1's three entities are four-feature bundles, so a gold pair is two features of one
entity, written into one event. A cross-event gold relation would make the guard live; no K1 entity
has one.

## Q2: the top-N truncation control cannot fail

The control was supposed to show that a deletion of the same size drops true pairs while the
provenance rule does not. It cannot, for two independent reasons.

- **By count.** The comparator covers all eighteen gold pairs with the handful of pairs in the
  block's emitted-pairs row. The arm retains at least that many, since it keeps every
  cooccurrence-labelled row Organica serves. Any truncation to the arm's retained count therefore
  still has room for all eighteen, whatever the ordering.
- **By rank.** The gold pairs are the highest-count pairs in the world — they are the world's law,
  which is why a count floor of ten alone finds every one of them. A count- or score-based
  truncation puts them at the top, exactly where truncation keeps them.

So the control passes. It could only fail by truncating below eighteen pairs, and at that point the
arm's own rule would be failing the guard with it — the arm would be VOID, not informative.

## The arm is dominated by its own comparator

This is the finding that decides it. The strongest-of-grid the endpoint subtracts *is* a
within-event cooccurrence model, swept and tuned across the grid in the block. Organica under the
rule keeps a **superset** of that set — every cooccurrence-labelled row it already serves, with no
count floor — so on every seed its precision is at most the comparator's and its F1 is at most the
comparator's. The treatment is strictly weaker than the comparator that scores it.

A fail would therefore be arithmetic, not evidence about provenance. And a pass is unreachable: an
arm that is a superset of the set holding the best-of-grid mean cannot exceed it.

## The grid is half-inert, so the comparator is tuned but thin

The block settles a question worth stating plainly, because it cuts against reading the baseline as
a strong, well-explored model. Of the grid's configurations, the nine long-window ones
(windows 150, 300 and all, at every count floor) return **one and the same result on every seed**
— the count floor is inert there, because the pair counts at those windows are already far above
it. All of the tuning that produces the best-of-grid number comes from the two short windows.

That is not saturation: the sweep does move, and the best configuration beats the collapsed point on
every seed by the margin in the block. But the maximum is a **maximum, not a plateau**. It comes
from a non-monotone corner — at window 30 a floor of ten actually costs recall and lowers F1, while
at window 75 the same floor wins — and on some seeds more than one configuration reaches it. So the
ledger's comparator does have tuned headroom; that headroom rests on two of five windows and is
fragile to the seed.

Reading it the other way — "the sweep is saturated, so the comparator has no tuned headroom" — is
wrong, and the artifact says so: nine identical configurations coexist with six that differ, and
the best of the six is what the gap is measured against.

## The bar is below the comparator

`pass_min_improvement` was set against Organica's own mean, so PASS requires the bar in the block,
which sits below the best-of-grid mean by the block's margin. Even a passing arm would still lose to
a simple model by more than half an F1 point. For a claim about precision, that is not a bar.

## What the test does establish

The information is present and the readout discards it. Within-event evidence alone reaches the
comparator's F1 range in the block, on the same ten seeds where the engine's structures reach the
organica range beside it. The deficit is a **selection defect inside `_build_predictions`**, not a
missing signal — which is a stronger result than the draft was written to produce, and it is
already in the record.

## What remains: a build, not a diagnostic

Rule 30 applies. Both outcomes of this line now lead to the same place: the claim worth earning is
subject-side — *the engine asserts more precisely* — and that needs the co-occurrence test inside
`_build_predictions`, which is a frozen-engine change under rule 12. The build is scoped in
[`COOCCURRENCE-SELECTION-BUILD.md`](COOCCURRENCE-SELECTION-BUILD.md); it is not started, and it
allocates no cell.

The draft's term sheet is retained for that build. The recall floor, the returned-edge-set liveness
gate and the scope check are still the right instruments; only the readout-side endpoint is
withdrawn.

## Reproduce

    python -m benchmarks.assertion_provenance_pressure_test --check
    python -m benchmarks.assertion_provenance_pressure_test --self-test

`--check` re-derives every figure and fails on a stale block, on a figure quoted outside the block,
on a six-decimal range that is not one the artifact derives as a pair, on a per-seed figure that no
single K1 row carries together with the figures quoted beside it, and on a `baseline_gap` — in the
ledger's K1 registration or in the draft — that differs from the mean gap derived here.
`--self-test` proves each refusal can fire.

No cell ran. Nothing here re-scores a K1 cell, the 0.9.0 campaign or the 0.15.0 replication, and no
threshold in the draft is in force.
