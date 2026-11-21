# `CONSTRAINT-K2-RETIREMENT` — K2 retired as an invalid attempt, not a failed hypothesis

**Status:** `ADOPTED 2026-11-19 — K2 RETIRED; THE HYPOTHESIS IS UNTESTED, NOT REFUTED`
**Decision record:** [`constraint_decisions/DECISION-K2-RETIRE.json`](constraint_decisions/DECISION-K2-RETIRE.json)
**Result record:** [`constraint_results/K2-BLOCK-ATTEMPT.json`](constraint_results/K2-BLOCK-ATTEMPT.json)
**Evidence:** [`K2-BLOCK-RESULT.md`](K2-BLOCK-RESULT.md) · [`phase_k_k2_results.json`](phase_k_k2_results.json) · [`constraint_registrations/K2-belief-revision.json`](constraint_registrations/K2-belief-revision.json)

## 1. What happened

K2's one block ran on 2026-11-18 under grant `K2-BLOCK-20261118-A`. Its own gate returned
`VOID` on `G4_no_pre_boundary_demotions`: the treatment's pre-boundary pass calls the demotion
helper on every pre-boundary cycle, and the helper counts every pre-boundary association even
though it leaves the candidate unchanged. G4 therefore fires on every seed, and the frozen build
cannot return a non-`VOID` result. No criterion was read.

A `VOID` is not a null result. The block produced no admissible comparison, so it is not evidence
for or against the retention-priority hypothesis. The hypothesis is **untested**, not refuted.

## 2. The ledger amendment

Before this decision the constraint ledger accepted a retirement only with a result whose outcome
was `pass`, `fail` or `inconclusive`. That vocabulary had no honest terminal state for a block that
could not produce an admissible comparison, which left K2 in `in-test` indefinitely and blocked the
next constraint from entering test.

The ledger now also accepts `attempt_invalid`, with three conditions enforced by
[`benchmarks/bottleneck_map.py`](../benchmarks/bottleneck_map.py):

1. the result records `outcome: "attempt_invalid"`;
2. it records `hypothesis_status: "untested"` and `criteria_read: false`;
3. the retirement decision says the hypothesis is untested.

This is a **terminal disposition**, not a pass/fail outcome. It may not be reported as a failed
intervention, a null result, or evidence that lowering pre-boundary priority does not help. It also
does not authorise a second block: the one attempt is spent, and a further attempt would need a new
pre-registration, a fresh seed block and a new dated grant.

## 3. What it changes

- K2 leaves `in-test` and remains in the ledger as history.
- The K2 row is not a refutation; the mechanism question stays open and unowned.
- No seventh K family is added and the K search is closed.
- The K1 forced-selection arm is registered as the next `in-test` row
  ([`constraint_registrations/K1-served-path.json`](constraint_registrations/K1-served-path.json)),
  with the same-build 0.15.0 baseline and numeric thresholds. **No cell has run.**
- Future registered comparators use a same-build baseline, not the predating `0.9.0` value.

## 4. What this does not authorise

No engine change, no cell, no seed, no grant, no second K2 block, no seventh task family and no
re-scoring of any prior verdict. The V2 first cell, the K replication and the K2 block are
untouched.
