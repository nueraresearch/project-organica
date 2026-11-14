# A1 C8 expansion target design — registered, not frozen

**ID:** `A1-C8-EXPANSION-1`

**Date:** 2026-11-14

**Status:** `REGISTERED — NOT FROZEN, NOT RUN, NO GRANT; CURRENT MANIFEST REMAINS N=4`

**Parent:** `A1-TARGET-SELECTION-1` (the registered four-target Path A design)

**This is a registered target design, not a target freeze, a seed reservation, a grant or a result.** It does not change the current manifest, the current four-target artifact or the C8 ceiling. No A1 arm cell has run.

## 1. Why this design exists

C8 is a per-seed assertion proportion over the `N` target rows in the `A−K−` cell. At the current N=4 block the smallest nonzero change is `1/4 = 0.25`, and at the N=8 maximum-disjoint block it is `1/8 = 0.125`. Both are above the precommitted **0.05** ceiling, so the current design cannot resolve C8 at its own margin. The adopted unit decision is recorded in [`A1-C7-C8-DENOMINATOR.md`](A1-C7-C8-DENOMINATOR.md).

This design supplies **20 A−K− target rows per seed**. The step is `1/20 = 0.05`; equality is not finer than the ceiling under the audit's rule, so the denominator is resolved. The C8 ceiling remains **0.05** and is not changed.

## 2. Selection rule

The design reuses the registered selection boundary and eligibility rule:

- the candidate universe is the first 36 acquisition cycles only;
- an edge is eligible only when it is in that universe, has positive cycle-36 `U` strength, and is a cycle member;
- the selection order is the same hash order as `A1-TARGET-SELECTION-1`, blind to the magnitude of `U`.

The difference is the set size and the overlap rule:

| Field | Current Path A | C8 expansion |
| --- | ---: | ---: |
| Targets per seed | 4 | **20** |
| Endpoint rule | all targets disjoint | **overlap permitted** |
| Maximum selected degree per tag | 1 (implied) | **3** |
| A−K− rows per seed | 4 | **20** |
| C8 step at 0.05 | 0.25 | **0.05** |

Twenty fully disjoint edges would need 40 distinct tags; the design's 16-tag universe cannot supply them. The design therefore permits a tag to appear in more than one target edge, but caps each tag at **three** selected edges. This limits cross-target overlap while keeping 20 distinct rows; no target edge is repeated.

The selection pass is a no-arm, 36-cycle run, not one of the 36 A1 cells. It writes [`a1_c8_target_selection.json`](a1_c8_target_selection.json); the artifact records 20 selected edges, the cycle-36 `U` row and the cycle-member status for every selected edge, and each seed's endpoint degrees. All six provisional seeds formed 20 rows with maximum degree 3.

## 3. What the design resolves and what it does not

| Gate | Current N=4 | Registered N=20 | Status |
| --- | --- | --- | --- |
| `C8_third_route` | 4 rows; step 0.25 | 20 rows; step 0.05 | **Resolved by the registered design if adopted** |
| `C7_assertion_block` | per-edge A/K rate over 120 cycles | unchanged per-edge rate over 120 cycles | Already rate-resolved; the registered design has 40 Y− rows per seed |
| C1 target-only fallback | 4 rows | 20 rows; step 0.05 | 20 rows still cannot satisfy the separate 60-row C1 floor |
| C3 positivity | six cells per seed | six cells per seed | Unchanged; every target edge still needs all four A×K cells |
| C4 non-target stream | 59–60 planned non-target edges | 43–44 planned non-target edges | C4 is still unmeasured; the target block changes the split |

The N=20 design does **not** supply the C1 60-row floor by itself. C1 still needs the paired-control available non-target rows; the current C1 feasibility risk remains.

The N=20 design does **not** make target rows independent. Endpoint overlap means a target edge can share a tag — and potentially a carrier structure — with another target edge. C8 reads the assertion rate over the 20 rows and does not pool across seeds; it does not license an independence claim across rows.

### 3.1 Superset check against the current Path A targets

**VERIFIED — all four current targets are retained in every seed.** This is a read-only comparison of the committed [four-target artifact](a1_target_selection.json) and the [N=20 artifact](a1_c8_target_selection.json); it does not regenerate either set.

| Seed | Current N=4 targets | N=20 targets | Retained | New rows | N=4 subset? |
| ---: | ---: | ---: | ---: | ---: | --- |
| `20630101` | 4 | 20 | 4 | 16 | yes |
| `20630102` | 4 | 20 | 4 | 16 | yes |
| `20630103` | 4 | 20 | 4 | 16 | yes |
| `20630104` | 4 | 20 | 4 | 16 | yes |
| `20630105` | 4 | 20 | 4 | 16 | yes |
| `20630106` | 4 | 20 | 4 | 16 | yes |

Adopting this design would therefore preserve the current Path A target identity and add 16 rows per seed; it would not require re-selecting the four existing targets. The cell matrix remains the same 36 cells, although each cell would carry 20 target rows instead of four, and that per-cell runtime cost has not been measured. The C4 non-target stream changes from **59–60** to **43–44** rows because 16 candidates move into the target block; the C1 total upper bound remains **63–64** because 20 + 43/44 equals the same candidate count. C1 target-only is still only **20** rows, below the separate **60-row floor**, so this design does not make C1 admissible by itself. The [power review](A1-POWER-REVIEW.md#c1-denominator-feasibility-risk-note) records the per-seed availability budget for that floor.

## 4. What this registration does not do

- It does not replace or regenerate the current four-target `A1-TARGET-SELECTION-1` artifact.
- It does not update `A1-TWO-PATH-1`, whose target block remains `UNRESOLVED` with `n_per_seed: 4`.
- It does not freeze the new targets, reserve the six seeds, issue a grant or authorise a run.
- It does not change the 0.05 C8 ceiling, the 0.05 C7 A/K margin or the C1/C4 gate.
- It does not measure C8; no A−K− cell has run.

Adopting this design requires a separate target-freeze act that names `A1-C8-EXPANSION-1`, replaces the N=4 target set in the manifest and records the selection artifact. The prepared N=20 act is [`A1-TARGET-FREEZE-N20-1`](A1-TARGET-FREEZE-ACT-N20.md); it is **DRAFT — READY FOR OWNER SIGNATURE**. C5 target timing is cleared by the fixed cycle-4 earlier-`U` protocol, and its 20-row block validates under the `a1_two_path` N=20 target profile. If the owner does not adopt it, the current freeze must carry the explicit limitation `C8: NOT ADJUDICATED BY DESIGN`.

## 5. Integrity checks

The registered artifact is checked by `python -m benchmarks.a1_c8_target_selection --check`. The check requires:

- exactly 20 selected edges per seed;
- no repeated target edge;
- every selected edge in the cycle-36 candidate universe with positive strength, `measured_cycle == 36` and `cycle_member == true`;
- maximum selected endpoint degree at most 3;
- the per-seed selection digest matches the selected set and design constants;
- the C8 threshold is still 0.05 and the design is still marked `disjoint: false`.

No check in this record scores C8. The artifact is a target-design record, not an A1 result.

## 6. Related records

| Record | Relationship |
| --- | --- |
| [`A1-C7-C8-DENOMINATOR.md`](A1-C7-C8-DENOMINATOR.md) | Adopts the per-seed unit; this design supplies the C8 rows |
| [`A1-TARGET-SELECTION-PROTOCOL.md`](A1-TARGET-SELECTION-PROTOCOL.md) | Current four-target Path A protocol; unchanged |
| [`A1-TWO-PATH-MANIFEST.md`](A1-TWO-PATH-MANIFEST.md) | Current manifest; still N=4, unresolved and unfrozen |
| [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md) | C1 denominator-feasibility risk and the per-seed 60-row availability budget |
| [`A1-TARGET-FREEZE-ACT-N20.md`](A1-TARGET-FREEZE-ACT-N20.md) | Prepared N=20 target-freeze act; preserves the four current targets; validated by the N=20 target profile; C5 target timing cleared by the earlier-`U` protocol; ready for owner signature |
| [`A1-PRE-FREEZE-CHECKLIST.md`](A1-PRE-FREEZE-CHECKLIST.md) | Records the N=20 design as registered but not adopted |
| [`A1-DENOMINATOR-RESOLUTION.md`](A1-DENOMINATOR-RESOLUTION.md) | Shows the current C8 flags and the registered N=20 pass |

**Not evidence:** A registered target design and a no-arm selection artifact. No A1 cell has run; no C8 measurement, target freeze, seed reservation or grant exists.
