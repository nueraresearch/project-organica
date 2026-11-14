# Authorisation: PRESENCE-COMPARATOR-112, PRESENCE-CONSTRUCT-1-112 and PRESENCE-CAP-1-112

Dated 2026-11-11. Recorded against the three cap-112 pre-registrations, which are frozen at cap 112
and remain `NOT RUN`. This document is the grant; it is not a run.

## The grant

> Write the dated cap-112 authorisation document for the comparator, Q1 and Q2, recording the owner's grant against the three frozen records.

## What is authorised

The cells each record fixes, once the cap those records name is landable and a harness exists:

- `PRESENCE-COMPARATOR-112` — six cells on the audit seeds at cap 112, edge-level presence versus
  assertion, with the fresh-process control.
- `PRESENCE-CONSTRUCT-1-112` — six reading cells plus the control rerun, gates C1–C9.
- `PRESENCE-CAP-1-112` — twenty-four cells (six fresh seeds × levels 40/80/112/ceiling) and the
  cap-112 witness that reproduces the comparator row.

## What is not authorised

- **The cap change itself.** Landing `DECISION-CAP-LEVEL` C (112) is a separate recorded act: version
  0.15.0, pin re-recorded, canaries re-recorded and attributed. This grant does not perform it.
- **Running under cap 40.** No cell of these three blocks may execute on a harness that fixes 40, and
  none may be read as a cap-112 result if it did.
- **Any change to the frozen designs, gates, verdict sets or decision tables.** They are adopted from
  the predecessors and are not amendable by a grant.
- **Re-scoring or pooling with the cap-40 verdicts.** Those stay standing for the builds they measured.
- **Any run before a runner exists.** No harness executes these cells at 112 today.

## Status at the date of this document

Granted 2026-11-11. `SleepService.MAX_PREDICTIONS` is still 40, the package is 0.14.0, no cap-112
runner exists, and no cell has run. The grant authorises the campaign, not the build or the bump.

## Provenance correction (2026-11-14)

The quoted instruction authorises **preparation of this document**, not the execution of cells.
The two cap-112 blocks that later ran (`PRESENCE-COMPARATOR-112`, 7 cells, and
`PRESENCE-CAP-1-112`, 25 cells) are reclassified as **provisional and not owner-authorised** in
[`docs/CAP-112-PROVENANCE-DISPOSITION.md`](CAP-112-PROVENANCE-DISPOSITION.md). Their numerical
results and gates stand unchanged but are not confirmatory. `PRESENCE-CONSTRUCT-1-112` remains
unrun and must not run under this quote. This correction does not reverse the separate cap-level
decision or the 0.15.0 landing.
