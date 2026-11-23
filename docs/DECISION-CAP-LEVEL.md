# Decision: raise the Layer-1 prediction cap to 112

Dated 2026-11-11. Recorded by the owner against Question 2 of `docs/CAP-DECISION-BRIEF.md`, after E1
(the semantics of the constant) landed on 2026-11-10. The evidence is `PRESENCE-CAP-1`'s verdict,
`CAP LIMITING`, in `docs/presence_cap_run.json`.

## The decision

**C — Raise the Layer-1 prediction cap from 40 to 112.**

Decided, not in force: the cap-40 comparator and the three frozen blocks cannot run under 112, so landing it needs a version bump and fresh records for them.

## The rationale

`CAP LIMITING` licenses a cap-change decision; it does not take one. Of the three recorded options,
112 is the level the block fixed in advance and the only one with a passed criterion: mean paired
gain **15.833333** asserted world edges, 95% lower bound **8.081175** against a pre-committed bar of
**10**, positive on **6 of 6** seeds, with the world's 112 edges as the natural comparison. It is the
easiest to defend later because nothing about it was chosen after the data arrived. The block proved
112 is *beneficial*, not that it is *necessary*: no criterion was judged at 80 that 80 fails, and
inventing one now would score the protocol after the fact. The owner chose the pre-registered
comparison over the ladder step.

## Why it is not in force

- **The comparator is a cap-40 artifact.** `benchmarks/presence_assertion_audit.py` declares
  `CAP = 40` and its `build()` refuses to run when `SleepService.MAX_PREDICTIONS` is not 40; its six
  rows are the same-object comparator Q1's `C9` reproduces and Q2's `K5` takes its witness from.
- **The three frozen blocks are designed at 40.** `PRESENCE-CONSTRUCT-1`'s record fixes cap 40, and
  `PRESENCE-CAP-1`'s design is levels 40/80/112 plus the diagnostic ceiling, with a cap-40 witness row
  that must reproduce the published audit row. Raising the shipped cap makes the witness claim false.
- **The canaries were recorded at 40.** A level change moves them by design; an unchanged digest would
  be the defect. Re-recording them is correct and destroys the split's *live* proof, which is exactly
  the sequencing the brief pre-committed to.
- **The lineage link's proof is anchored to the live canary record.** `DECISION-CAP-SEMANTICS`'s link
  proves the digests recorded on `1fc7be8f…`; once the canaries are re-recorded for the level, that
  proof must either preserve the predecessor record as a historical file or the link must be retired.
  That is a landing step, disclosed here rather than improvised later.
- **A rebuild on the split build must not run first.** The rebuild plan's three blocks are cap-40
  blocks; a rebuild on the split build would be superseded the moment the level lands, so the level
  decision precedes it.

## What landing will require

1. **A version bump.** The cap is a cognition change (AGENTS.md rule 2): bump the package version to
   **0.15.0**, add its changelog entry, re-pin `docs/engine_pin.json`.
2. **Re-record the canaries** and attribute the move to the level, not to E1; preserve the
   0.14.0-era digest record so the E1 link remains a historical fact or retire the link explicitly.
3. **Fresh records for the three blocks at cap 112.** The comparator, Q1 and Q2 cannot be re-read
   under a different cap; each needs its own pre-registration at 112, and the runs need an owner grant.
4. **Re-derive, do not carry, the affected verdicts.** The new blocks' verdicts are whatever their own
   decision tables return; the cap-40 verdicts stay standing for the build they measured.
5. **Run the full checks:** `engine_pin --check`, `block_canaries --check` (new digests expected),
   the three block checks, `engine_lineage --check`, `test_versioning`, the suite and the gates.

## Rejected alternatives

**Alternative.** B — raise the cap to 80.
**Because.** The midpoint is descriptive, not judged: its mean gain is 3.50 asserted edges and no interval was registered for it, so choosing 80 would trade the one pre-registered comparison for a smaller step with no passed criterion.

**Alternative.** A — keep the cap at 40.
**Because.** Keeping 40 would record the CAP LIMITING reading and then discard the only pre-registered comparison that cleared its bar, closing the budget route at this cap and world family.

## What this does not cover

Any capability, prediction, retention or transfer claim; worlds of other sizes or edge counts; a claim
that 112 is necessary, optimal or general; the blocks' re-derivation (step 3 above); or a change to any
other parameter. The uncapped arm remains a diagnostic ceiling and must never ship.

## Status of the shipped build

This record changes nothing on disk in the engine: `SleepService.MAX_PREDICTIONS` is still 40, the pin,
the canaries and every artifact are unchanged, and the package version is still 0.14.0. It records the
owner's choice and the conditions under which it becomes real.
