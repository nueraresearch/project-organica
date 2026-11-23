# CORE-BAND-ADMISSION-1 — core+band at the cap-112 ceiling

Generated from `docs/core_band_admission_prereg.json`; never edited by hand.

**Status.** FROZEN, RUN. **Grant.** granted.

## Question

At the cap-112 ceiling, does an admission rule that guarantees the rank-1-20 core and the rank-21-40 band recover every core+band edge without a false-admission rate more than 10 percentage points worse than the normal cap-112 window?

## Design

| Field | Value |
| --- | --- |
| Seeds | 20617101, 20617102, 20617103, 20617104, 20617105, 20617106 |
| Arms | control, treatment |
| Cap | 112 |
| Cycles per cell | 120 |
| Cells | 12 |
| Core | transition ranks 1-20 |
| Band | transition ranks 21-40 |

**Control.** the shipped cap-112 engine ordering.

**Treatment.** the same cap-112 run, with every top-20 core and rank-21-40 band transition guaranteed a served seat; a missing tier edge replaces the lowest-priority non-tier transition, then a cooccurrence if no transition remains.

**Window.** the engine's served list remains 112 rows; treatment only replaces seats.

## Endpoints

- **Coverage:** served tier edges / available tier edges, pooled over cycles and seeds; bar **0.95**.
- **False admission:** served rows whose edge is not a present world transition, divided by all served rows; treatment minus control; margin **+0.10**.
- **Binding:** a replacement in any treatment cycle; if none occurs and the window digests match, the rule is non-binding at 112.

## Gates

| Gate | Rule |
| --- | --- |
| `C1_build` | one 0.15.0 build and cap 112 across all cells |
| `C2_world` | each seed has the same world digest in both arms |
| `C3_tier` | each cycle has 40 tier edges when the pre-cap universe has at least 40 transitions |
| `C4_length` | every served window has 112 rows |
| `C5_ledger` | every tier edge is accounted for as served or missing |
| `C6_control` | control is the unmodified repaired observer |
| `C7_treatment` | treatment differs only by the tier guarantee |

## Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| a gate fails or a window is short | **VOID** | the block did not produce a readable window | fix the ledger; do not read coverage |
| gates pass, no replacement, all window digests equal | **NON-BINDING AT 112** | the normal cap-112 window already serves every core+band edge | do not add a separate admission rule at this ceiling |
| gates pass, replacements occur, coverage >= 0.95 and false-admission difference <= +0.10 | **BINDING, ACCEPTABLE** | the guarantee changes the window and preserves the cost bar | consider the rule only with its measured cost |
| gates pass, replacements occur, coverage < 0.95 | **RULE FAILS COVERAGE** | the guarantee did not recover the tier | do not adopt; inspect the missing ledger |
| gates pass, replacements occur, false-admission difference > +0.10 | **RULE PAYS COST** | the guarantee recovers the tier by serving more non-world rows | do not adopt on coverage alone; report the trade |

## What this does not license

A twelve-cell test of one admission guarantee on one synthetic world family. It does not establish capability, retention, transfer or a general operating cap.

The grant covers these twelve cells only. It does not authorise an engine edit, a promotion, a different cap, or a new seed block.
