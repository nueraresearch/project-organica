# PRESENCE-CAP-LADDER-1 — multi-seed transition-budget ladder

**Status.** FROZEN, NOT RUN. Generated from `docs/presence_cap_ladder_prereg.json`; never edited by hand.

| Field | Value |
| --- | --- |
| Preregistration | `PRESENCE-CAP-LADDER-1` |
| Freeze date | 2026-11-12 |
| Seeds | 20614101, 20614102, 20614103, 20614104, 20614105, 20614106 |
| Caps | 40, 56, 80, 112 |
| Primary rung | 80 |
| Cells | 24 |
| Cycles | 120 |
| Grant | not granted |
| Runner | built |
| Cells run | 0 |

## Question

On the shipped 0.15.0 build, with six fresh worlds, does a transition budget of 40 recover the measured rank-21-40 band without a false-admission rate more than 10 percentage points above the cap-40 baseline, and at which lower rung does recovery begin?

## What is already known

BAND-5 measured 0/89 band service at cap 40 and 89/89 at cap 112 on seeds 20612601-20612606. Those endpoints are prior evidence, not cells of this block.

Caps 56 and 80 are the untested rungs. Cap 80 is the smallest rung whose nominal 40-transition floor reaches rank 40; cap 56 reaches only rank 28.

The shipped split gives half the cap to entropy-ranked transitions and half to count-ranked cooccurrences. The engine may backfill unused cooccurrence seats with further transitions, so actual transition counts are recorded per window rather than assumed.

A higher cap can recover the band by serving more rows. The block therefore charges every served row that is not a present world edge, not only rows outside the named band.

## Design

| Cap | Transition floor | Cooccurrence cap |
| ---: | ---: | ---: |
| 40 | 20 | 20 |
| 56 | 28 | 28 |
| 80 | 40 | 40 |
| 112 | 56 | 56 |

Only `SleepService.MAX_PREDICTIONS` changes. The six seeds share the same world and stimulus across all four caps. The cap-80 rung is primary because its nominal 40-transition floor is the first to reach rank 40.

## Band

For each seed, every present transition at minimum cap-112 block rank 21-40; measured from the 112 universe and not filtered by service at any lower cap.

Each band edge is named by source>target and carries its minimum cap-112 rank; a missing rank is a ledger failure, not a zero.

Measured per seed; BAND-5 observed 11-19 edges per seed, and no fixed band size is assumed.

A zero band is a zero denominator and makes the block VOID.

## False admissions

A served row whose source>target edge is not in the seed's present world transitions, where present = world edges intersected with the temporal rows retained at the end of the cell.

**Rate.** Served rows that are not present world transitions, summed over all cycles and windows, divided by all served rows, summed over all cycles and windows; computed per seed and pooled by summing rows, never by averaging per-cycle ratios.

**Bar.** Paired cap-80 minus cap-40 false-admission rate for each seed; the upper bound of a 10,000-resample seed-cluster bootstrap must be at or below +0.10.

**Why this margin.** The margin is pre-set, not fitted. The earlier cap-40 ladder recorded a world-row share of 0.239-0.278, so the non-world baseline is roughly 0.72-0.76; +10 pp bounds the worsening to about one-eighth of that baseline rather than permitting a free precision collapse.

**Not the same as collateral service.** A served world edge outside rank 21-40 is collateral service, not a false admission; it is reported separately.

## Endpoints

| Endpoint | Cap | Rule |
| --- | ---: | --- |
| Band recovery | 80 | at least 0.90 pooled, per seed reported |
| False admission | 80 | paired upper bound at most +0.10 |
| Band ceiling | 112 | at least 0.95 |
| False admission (ceiling) | 112 | paired upper bound at most +0.10 |

The two cap-80 endpoints are co-primary: a band recovery cannot rescue an excessive false-admission rate, and a clean false-admission rate cannot rescue an unserved band.

## Predictions

| ID | Cap | Prediction |
| --- | ---: | --- |
| P1 | 40 | 0.00 band recovery; the cap-40 control serves no rank-21-40 edge. |
| P2 | 56 | 0.30-0.60 band recovery, because only ranks 21-28 are nominally reached. |
| P3 | 80 | 0.85-1.00 band recovery; schema rows can push a few rank-40 edges past the 40-transition floor. |
| P4 | 112 | 0.95-1.00 band recovery; BAND-5 observed 89/89 at this cap. |
| P5 | all | false-admission rate rises weakly with cap; the cap-80 paired upper bound stays at or below +0.10. |
| P6 | all | band recovery is nondecreasing across 40, 56, 80 and 112. |

## Gates

| Gate | Rule |
| --- | --- |
| `L1_build` | one shipped 0.15.0 build across all cells; only MAX_PREDICTIONS differs |
| `L2_world` | each seed has the same world digest and present fingerprint at all four caps |
| `L3_band_identity` | each band edge is a present transition at rank 21-40 with a recorded rank and source>target identity |
| `L4_control_40` | cap 40 serves no band edge and its full 40-row windows satisfy the 20-transition floor and the 20-cooccurrence cap |
| `L5_allocation_law` | every full window has transitions + cooccurrences = cap, transitions >= cap//2, cooccurrences <= cap//2, with actual counts and relations recorded |
| `L6_denominator` | every seed has a non-empty band, at least one served row, and every band edge reaches the ledger |
| `L7_determinism` | a fresh-process rerun of seed 20614101 at cap 80 reproduces its windows and ledger |
| `L8_seed_axis` | at least three distinct served-band sets across the six seeds |
| `L9_false_ledger` | every served row is classified present or not-present, and no served row is unparsed or missing a rank where a transition rank is required |

## Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| L1-L4, L6 or L9 fails; a band is empty; or a required ledger row is missing | **VOID** | the block did not produce a readable band, a valid control or a complete false-admission ledger | record VOID; fix the failed gate and register a new block; read no recovery |
| L5, L7 or L8 fails | **VOID** | the allocation, determinism or seed-axis gate did not hold | record VOID; do not interpret a band rate from an unreadable ladder |
| gates pass and cap-112 band recovery is below 0.50 | **NO RECOVERY** | even the ceiling control does not recover the band on these worlds | the cap or transition budget is not the gate; next test candidate formation or the rank itself |
| gates pass and cap-112 band recovery is 0.50-0.90 | **PARTIAL RECOVERY** | the budget helps but does not recover the measured band uniformly | report the per-edge misses; do not adopt a cap; next test the residual rank or allocation rule |
| gates pass; cap-80 recovery is below 0.90; cap-112 recovery is at least 0.90 and its false-admission upper bound is at most +0.10 | **RECOVERY AT 112 ONLY** | 80 is insufficient, while the shipped 112 budget recovers the band at acceptable false-admission cost | record the threshold; the owner may consider 112 as the operating rung, with the measured cost |
| gates pass; cap-80 recovery is at least 0.90; false-admission upper bound is above +0.10 | **RECOVERY WITH COST** | the band returns at 80, but the window pays more than the pre-set false-admission margin | do not adopt 80 on band recovery alone; report the trade-off and test a precision-preserving admission rule |
| gates pass; cap-80 recovery is at least 0.90; false-admission upper bound is at most +0.10; cap-112 recovery is at least 0.95 | **CONFIRMED** | the 80 rung recovers the measured 21-40 band without excessive false admissions, and 112 remains the ceiling control | record the confirmation; the owner decides any engine or operating change; no capability claim |

## Analysis

Pooled and per-seed band recovery at cap 80; exact McNemar on the paired band-edge service indicator against cap 40, where the cap-40 control should leave every band edge unserved.

Per-seed false-admission rates with numerators and denominators; paired cap-80 minus cap-40 difference, plus the cap-112 minus cap-40 difference used by the ceiling branch; 10,000-resample seed-cluster bootstrap for each upper 95% bound. The seed is the resampling unit.

Report cap 56 and cap 112 recovery and the four-rung sequence. A monotonicity failure is reported as a failure, not smoothed.

The cap-80 band and false-admission endpoints are co-primary; all other rungs and outcomes are secondary and labelled so.

No seed, cap or cycle is dropped; a missing cell makes the block VOID.

The band definition, primary rung, margin and bars are frozen before any cell.

## What this does not license

A preregistration, not a result. It measures band service and false admissions on one synthetic world family. It does not establish capability, retention, transfer, or a general operating cap.

No authorisation is recorded. The runner is built but refuses every cell while the grant is absent. No cell has run.
