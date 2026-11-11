# Decision: the prediction budget is an allocation, not a capacity

Dated 2026-11-10. Recorded by the owner after PRESENCE-CONVERSION-1 returned `OBSERVER NOT NEUTRAL`,
which exposed that an instrument reading `MAX_PREDICTIONS` literally produced a different served
window from the engine's. The name described a capacity; the engine was using an allocation.

## The decision

**E1 — split it, values linked.** Split the prediction budget into named transition and
cooccurrence allocations, with their values derived from the returned window.

In force: the split landed through a recorded lineage link, proven by unchanged canary digests.

## How it landed

The split was implemented and proven behaviour-identical: the four block-canary cell digests did not
move, so no served row changed. What blocked it was the build stamp: the frozen presence artifacts —
`docs/presence_assertion_audit_0.14.0.json`, the construct audit's six reading cells and the cap
block's audit — record the engine bytes that produced them, and their checks required the shipped
bytes. Re-running those blocks is not a restamp: it would re-derive their verdicts, and Q1's derived
verdict on a changed build is `VOID`.

So the engine lineage carries it instead. `docs/engine_lineage.json` records a link from the build
the canaries were recorded on to the split build, authorised by this decision, whose proof is the
full set of recorded canary digests. `benchmarks/engine_lineage.same_build` is now the build check
for the block canaries, the assertion audit, the construct audit and the cap block: a stamped
artifact passes on the shipped engine or on a recorded behaviour-identical successor, and
`block_canaries --check` re-runs the cells on the successor, so a link cannot bless a build that
serves different rows. No measurement was restamped and no verdict was re-derived.

## The mechanism

`MAX_PREDICTIONS` keeps one job and one value: it is the **returned window**, 40 rows at the
shipped cap. Inside `_build_predictions` the window is now named before it is spent:

- `returned_budget` — the rows the cycle may serve (`self.MAX_PREDICTIONS`);
- `transition_budget` — the share transitions are guaranteed, `returned_budget // 2` (20 at the
  shipped cap);
- `cooccurrence_budget` — the remainder after transitions are actually served, which is what the
  engine already did by seating cooccurrences in the unused quota.

Every override that moves `MAX_PREDICTIONS` — the cap experiment's 80 and 112, the diagnostic
ceiling, the pool probe — moves all three together, because they are derived, not stored. That is
what makes the split provable: the served rows cannot change without the canaries changing, and
they did not.

**Reconciliation, 2026-11-11.** The transition budget is a floor, not the served transition count:
at 112 it guarantees 56 and the band arm observed 64-69 after backfill. The split's meaning and the
canary proof are unchanged; no level or split decision is re-scored.

## Why not a level change with it

A level change re-records the canary digests, and a moved digest cannot distinguish "the split
changed behaviour" from "the level did". The level is a separate decision with its own date,
record, version and re-recorded digests; the 40-row window stays shipped until that decision is
taken.

## Rejected alternatives

**Alternative.** Leave the constant as one integer.
**Because.** Leaving the constant as one integer keeps the coupling implicit and the name misleading.

**Alternative.** Rename `MAX_PREDICTIONS` and give the allocations stored values.
**Because.** A stored value can drift from the window it is spent from, and a second override site is a second way for the served set to change without a digest moving.

## What this does not cover

The budget level (40 stays), any predictive or retention claim attached to the split, other world
families, or the diagnostic ceiling's use as a measurement. The canaries prove the served rows are
unchanged at the shipped cap; they say nothing about caps that have never shipped.

## Evidence

- `docs/CAP-DECISION-BRIEF.md` §9 — the option, the sequencing rule and the levels it does not choose.
- `docs/presence_cap_run.json` — the Q2 block that showed the cap is an allocation policy.
- `docs/block_canaries.json` — four cell digests, unchanged across the re-pin.
