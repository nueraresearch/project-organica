# Disposition — cap-112 authorisation provenance

**Date:** 2026-11-14. **Scope:** `PRESENCE-COMPARATOR-112`, `PRESENCE-CAP-1-112` and the shared
grant document `docs/AUTHORISATION-PRESENCE-CAP-112.md`. This disposition runs no cell and changes
no numerical result, gate, seed, status or artifact.

**Decision: explicit reclassification.** The two executed runs are recorded as **provisional and
not owner-authorised**. No run-authorising quote is invented, and no result is re-scored.

## What is recorded

`docs/AUTHORISATION-PRESENCE-CAP-112.md` quotes:

> Write the dated cap-112 authorisation document for the comparator, Q1 and Q2, recording the owner's grant against the three frozen records.

That is an instruction to write the grant document. It authorises preparation, not the execution
of cells. No separate owner quote naming the cap-112 runs is recorded in the repository.

The audit in `docs/AUTHORISATION-PROVENANCE-AUDIT.md` established this for the two records with
`cells_run > 0`:

| Record | Cells | Recorded verdict | Provenance status |
| --- | ---: | --- | --- |
| `PRESENCE-COMPARATOR-112` | 7 | `PRESENCE NOT ASSERTION` | provisional; not owner-authorised |
| `PRESENCE-CAP-1-112` | 25 | `CAP LIMITING` | provisional; not owner-authorised |
| `PRESENCE-CONSTRUCT-1-112` | 0 | none | remains unrun; the quote does not authorise a run |

## Effect

- **Numerical results stand.** The row values, gates, verdicts, artifacts and `FROZEN, RUN` status
  are unchanged. No cell was rerun and no coefficient was edited.
- **The runs are not confirmatory.** They may be cited descriptively only with the label
  *provisional, not owner-authorised*. They may not be cited as an owner-authorised cap-112 result,
  as confirmation of the cap level, or as support for a new confirmatory claim.
- **The cap decision is separate.** The owner's `DECISION-CAP-LEVEL` choice and the 0.15.0 landing
  are not reversed by this disposition. What is missing is the recorded authorisation to execute
  these cells, not the decision to raise the cap.
- **The Q1 record stays unrun.** `PRESENCE-CONSTRUCT-1-112` must not run under the preparation-only
  quote. A run needs a genuine dated owner grant first.
- **The guard still reports the records.** `python -m benchmarks.authorisation_guard --check`
  continues to flag both run records, by design. B0 is closed under the roadmap's
  explicit-disposition branch, not by making the guard pass. A guard that accepted this quote would
  hide the very defect it exists to catch.

## Reopening

A dated owner statement that actually authorises the cap-112 cells would supersede this disposition;
it should be recorded against the records and the shared grant document. Re-running the blocks is
not required to establish the numerical values and would be a new block under a new grant, not a
repair of these records.
