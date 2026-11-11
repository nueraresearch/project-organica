# PRESENCE-CAP-1-112 -- pre-registration at cap 112

**Status: FROZEN, RUN, AUTHORISED.** Drafted 2026-11-11; the owner's cap-112 grant is recorded in `docs/AUTHORISATION-PRESENCE-CAP-112.md`. The planned runs executed on 2026-11-11 and the result is below.

## Question

With 112 as the shipped Layer-1 cap, does the 40-to-112 paired gain in asserted world edges reproduce on a fresh seed block -- and is 112 still limiting?

## Design

| Field | Value |
| --- | --- |
| Cap | 112 |
| Seeds | 20611901, 20611902, 20611903, 20611904, 20611905, 20611906 |
| Cycles | 120 |
| Cells | 24 |
| Levels | 40, 80, 112, 1000000000 |
| Shipped cap | 112 |
| World | the Gate-13 compositional world |

## Gates

| Gate | Requirement |
| --- | --- |
| `K1_build` | all cells and the witness name one engine version, one sha256 and the effective cap |
| `K2_same_world` | W identical across the four caps of every seed |
| `K3_presence_invariant` | P identical across the four caps of every seed |
| `K4_cap_live` | each cell records its cap; the 40 arm never returns more than 40 rows; the 112 arm never more than 112; higher caps change S_ever on at least one seed |
| `K5_cap_only` | the treatment overrides no pipeline method and the cap-112 witness reproduces the comparator-112 row; a failure is VOID |
| `K6_denominator` | W, P and S_ever non-empty in every cell |

## Verdicts this block can return

Q2's own decision table, adopted unchanged from `docs/presence_cap_prereg.json`: VOID, CAP NOT BINDING, ADMISSION-ONLY BOTTLENECK, CAP LIMITING, CAP LIMITING BELOW BAR, CAP NOT LIMITING, MIXED

The decision table is the predecessor's, adopted unchanged: `docs/presence_cap_prereg.json`.

## Result

**Verdict: `CAP LIMITING`.** Artifact `docs/presence_cap_1_112_run.json`; page `docs/PRESENCE-CAP-1-112-RESULT.md`. The design, seeds, gates and verdict rule above are unchanged.

## Controls

the level list, the shipped cap and the witness cap are each checked against a mutated record that must be rejected; `K4` is checked against a row set whose 40 arm returns 41 rows.

## Not evidence

A draft is not a run. No cell has executed, no verdict is adjudicated, and none of these records may be cited as a cap-112 result.
