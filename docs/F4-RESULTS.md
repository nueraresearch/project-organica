# F4 — the known-positive control: results

**Status: FROZEN.** This document records the control that decides whether the
store-time observer may produce verdicts at all. It is written once, after the
control ran, from `docs/store_time_observer_f4.json`. Corrections are appended
with a date; the decision is not rewritten.

## The question

**Can the observer identify the write behind a membership difference the record
already contains?** Not "can it explain divergence", and not "is `_score_tags`
causal" — only whether it can see the thing it was built to see.

## What ran

The control seed **T1/20261101**, arm B, at hash seeds **0 and 1**, capturing the
read-back window at engine cycles **10, 11 and 12** and every store call in the
same runs. 2 runs, 0 cached, 96.3 s. Windows are addressed by their own
`sleep:meta` markers, which both sides report as **10, 11, 12** over 162 sleep
reads each.

## 1. Reconciliation audit (before any attribution)

A cycle may only be interpreted if the calls the observer saw equal the rows the
store accepted and nothing was removed.

| Cycle | Side | Observed writes | Accepted rows | Net delta | Reconciled |
|---|---|---|---|---|---|
| 10 | hs0 | 647 | 647 | 647 | **yes** |
| 10 | hs1 | 647 | 647 | 647 | **yes** |
| 11 | hs0 | 1148 | 1148 | 1148 | **yes** |
| 11 | hs1 | 1148 | 1148 | 1148 | **yes** |
| 12 | hs0 | 2137 | 2137 | 2137 | **yes** |
| 12 | hs1 | 2137 | 2137 | 2137 | **yes** |

**Every affected cycle reconciles on both sides.** No cycle was reported as
`indeterminate`, and no attribution was read from an unreconciled cycle.

## 2. Attribution

| Cycle | Pool sizes (hs0/hs1) | Members on one side only | Attributed to a write |
|---|---|---|---|
| 10 | 230/230 | 4 | 4 |
| 11 | 250/250 | 4 | 4 |
| 12 | 283/283 | 4 | 4 |

Pool sizes are equal on both sides at every cycle, with two candidates each way —
the signature of an insertion/removal pair seen from the pool's side.

## 3. Outcome

All **12** differences were traced to a **construction-stage** write, of type
**`dream`**, offered on one side and **absent from the other side's write record** at
the same cycle. That is outcome **(B)** in the brief's result space: the cycle's
own construction supplied the differing candidate, not an earlier ingest write.

## 4. Admissibility decision

**PASS.** The observer is admissible for verdicts on the failing seeds.

It earned that in the only way available: it resolved a difference the record
already contains, and its reconciliation held where it looked. The first attempt
at this control returned `not_measured` on every cycle — the window index was
incremented before the read, so each window sat one read off its own marker — and
that failure is the reason this pass means something.

## 5. What this does not establish

- **Nothing about D0.** This is the control seed's own hash-seed difference; the
  failing seeds are untouched and no verdict over them exists.
- **Not that construction writes cause divergence.** On the control case the
  differing candidate is a construction write. That is a location, on one seed,
  at one hash-seed pair.
- **Not that `_score_tags` is or is not causal.** The control case does not
  isolate the scoring step from the rest of the cycle's construction.

## 6. Provenance

`docs/store_time_observer_f4.json` (this run), `docs/store_time_observer_self_test.json`
(neutrality, C2), `docs/store_time_observer_trace.jsonl.gz` (per-call trace of the
observed run), journal §81, `docs/STORE-TIME-OBSERVER-BRIEF.md`.

## 7. Correction, 2026-11-01 (appended; §3 is not rewritten)

Sections 3 and 4 first described the result as "outcome **(B)**". That label was
too narrow a claim and is corrected here.

The brief's **(B)** is *the `_score_tags` write is identified*. What the control
actually established is weaker and more precise: the differing candidate is
written during **the cycle's own construction**, not by ingest, and the write is
absent from the other side's record at that cycle. The observer's stage split is
binary — **ingest vs construction** — so "construction" covers the whole of
`_store_candidates`, and it does **not** by itself isolate `_score_tags` from the
rest of the cycle's construction.

So the control's outcome is: **a construction-stage write, identified at cycle
resolution; the scoring step is not separated from the rest of construction.**
That is outcome (B) *unlocalized* — admissible as a control, because the question
F4 asks is whether the observer can see the thing it was built to see, and it can.
It would not be reportable as a (B) verdict on a failing seed without the stage
split being finer than it is.

**The decision in §4 is unchanged.** The correction is to the label, not to
admissibility, and it is recorded rather than edited away because the label is
what a later reader would quote.

