# PRESENCE-COMPARATOR-112 -- pre-registration at cap 112

**Status: FROZEN, RUN, PROVISIONAL, NOT OWNER-AUTHORISED.** Drafted 2026-11-11; the recorded grant authorises preparation only, and the run is provisional (see `docs/CAP-112-PROVENANCE-DISPOSITION.md`). The planned runs executed on 2026-11-11 and the result is below.

## Question

On a build whose Layer-1 cap is 112, are presence and assertion the same object on the same world edges, the same build and the same observation window -- and does the 0.14.0 comparator's reading survive the level?

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
| `A1_build` | one build, one sha256, the cap 112 the pin will name; no mixed-build row |
| `A2_world` | one W per seed, no perturbation of order or window |
| `A3_denominator` | W, P and S_ever non-empty in every cell; a zero denominator is not measurable |
| `A4_object` | the asserted edge set is recorded as a set, not a count |
| `A5_seed_axis` | at least two distinct (P, S_ever, A_W) fingerprints across the six seeds |
| `A6_control` | a fresh-process rerun of seed 20261100 reproduces its fingerprints |

## Verdicts this block can return

the comparator's own `_verdict(rows)` over the six cells, unchanged: `PRESENCE NOT FULL`, `PRESENCE NOT ASSERTION`, `PRESENCE AND ASSERTION COINCIDE`

The decision table is the predecessor's, adopted unchanged: `docs/presence_assertion_audit_0.14.0.json`.

## Result

**Verdict: `PRESENCE NOT ASSERTION`.** Artifact `docs/presence_comparator_112_run.json`; page `docs/PRESENCE-COMPARATOR-112-RESULT.md`. The design, seeds, gates and verdict rule above are unchanged.

## Provenance disposition

**Status: PROVISIONAL, NOT OWNER-AUTHORISED (2026-11-14).** The numerical result and gates stand as recorded; the run is not owner-authorised and may not be cited as a confirmatory cap-112 result. See `docs/CAP-112-PROVENANCE-DISPOSITION.md`.

## Controls

`_verdict` is checked against a hand-built row set for each of its three verdicts before any cell runs, so a verdict that cannot be reached is a draft defect rather than a result.

## Not evidence

Executed without a recorded owner run authorisation. The numerical result and gates stand as recorded but are provisional; this is not an owner-authorised or confirmatory cap-112 result.
