# PRESENCE-CONSTRUCT-1-112 -- pre-registration at cap 112

**Status: FROZEN, NOT RUN, GRANTED FOR PREPARATION.** Drafted 2026-11-11; the recorded instruction authorises preparation of `docs/AUTHORISATION-PRESENCE-CAP-112.md`, not a run. No cell has executed and no verdict is adjudicated.

## Question

At cap 112, are presence, admitted and asserted measured as comparable quantities on the same world edges, the same build and the same window, so a conversion or cap reading rests on an edge-level measurement?

## Design

| Field | Value |
| --- | --- |
| Cap | 112 |
| Seeds | 20261100, 20261101, 20261102, 20261103, 20261104, 20261105 |
| Cycles | 120 |
| Cells | 6 |
| World | the Gate-13 compositional world (16 tags, 112 derivable edges) |

## Gates

| Gate | Requirement |
| --- | --- |
| `C1_build` | one build at the pinned sha256 and cap 112 |
| `C2_world` | one W per seed |
| `C3_presence` | P is a set with a digest and per-edge membership |
| `C4_denominator` | W, P and S_ever non-empty; a zero denominator is NOT MEASURABLE |
| `C5_object` | A_W is a subset of P; failure is OBJECT MISMATCH |
| `C6_witnesses` | at least one positive A_W edge and one P-minus-A_W edge per seed |
| `C7_seed_axis` | at least two distinct fingerprints across the six seeds |
| `C8_determinism` | the control rerun reproduces its fingerprints and ordered admission window |
| `C9_comparator_row` | each cell reproduces the cap-112 comparator row for its seed: world edges, present edges, asserted world edges and asserted fingerprint. This replaces the cap-40 `audit row reproduced` clause, whose published row does not exist at 112. |

## Verdicts this block can return

Q1's own gate set over C1-C9: `CONSTRUCT VALID`, `OBJECT MISMATCH`, `NOT MEASURABLE`, `VOID`

The decision table is the predecessor's, adopted unchanged: `docs/presence_construct_audit_prereg.json`.

## Why it has not run yet

- **The level.** `DECISION-CAP-LEVEL` C landed: `SleepService.MAX_PREDICTIONS` set to 112, version 0.15.0, pin re-recorded, canaries re-recorded and attributed
- **Grant recorded.** the recorded 2026-11-11 instruction authorises preparation of `docs/AUTHORISATION-PRESENCE-CAP-112.md`, not the execution of cells. The two blocks that ran are reclassified provisional in `docs/CAP-112-PROVENANCE-DISPOSITION.md`; the instruction does not land the cap and does not authorise a run under cap 40.
- **Runner built.** the three blocks are implemented against these frozen designs and their gates. On the landed build (0.15.0, cap 112) the preflight is satisfied, so `--measure` would open a cell; no cell has been started here

## Controls

`--check` builds a record with a cap-40 design and one with C1 deleted and requires both to be rejected, so the guard can fail.

## Not evidence

A draft is not a run. No cell has executed, no verdict is adjudicated, and this record may not be cited as a cap-112 result.
