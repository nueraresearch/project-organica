# C1–C9 preflight admissibility audit

**Date:** 2026-11-13  
**Status at preflight:** `NOT ADMISSIBLE — 0 SATISFIED, 9 REQUIRING INSTRUMENTATION, 0 UNSATISFIABLE`

**This is not an experimental result.** No cell, seed, intervention or engine change was made.

**Update 2026-11-13:** the `C6_temporal_resolution` row is a preflight snapshot. The separate
`C6-TIMING-1` block has since satisfied C6 on six fresh seeds; `C1`–`C5` and `C7`–`C9` remain
uncleared. The table below is retained as the preflight record, not as a current 0/9 count. See
[`C6-TIMING-BLOCK.md`](C6-TIMING-BLOCK.md).

**Readiness 2026-11-14:** `benchmarks/a1_gate_readiness.py` gives each remaining gate an
executable contract and a synthetic control. C6 is satisfied; the other eight are
`CONTRACT BUILT, NOT RUN`. C1/C4/C7 thresholds and the C8 ceiling are precommitted before any
cell, and each open gate has one attempt and a terminal failure disposition. None is cleared,
so the design is still not admissible. See
[`A1-GATE-READINESS.md`](A1-GATE-READINESS.md) and
[`A1-PRECOMMITTED-THRESHOLDS.md`](A1-PRECOMMITTED-THRESHOLDS.md).

## Question

Can the registered two-path design be admitted with the records in hand?

The audit reads the committed A0, provenance and carrier-trace records and asks whether the
registered two-path design is admissible **now**. It does not ask whether the design is
scientifically worthwhile.

## Verdict

| Classification | Count |
| --- | ---: |
| Satisfied | 0 |
| Requiring instrumentation | 9 |
| Unsatisfiable | 0 |

At preflight, no condition was impossible and none was cleared. The design was blocked by missing
instrumentation, not by a demonstrated impossibility. C6 has since been cleared; the remaining
eight conditions still block admissibility.

## Evidence in hand

| Quantity | Value |
| --- | --- |
| A0 rows | 26 |
| Rows with a carrier | 26 |
| Rows without a carrier | 0 |
| Rows with zero direct service | 26 |
| A0 slice `A+K+` / `A+K−` / `A−K+` / `A−K−` | 0 / 0 / 26 / 0 |
| Formation cycles | 37–117, median 76.0 |
| Assertion-cycle fields | **none** |

The A0 slice is selected on never-served direct edges. Every row has a carrier. It therefore
contributes only `A−K+` rows and cannot establish positivity across the matrix.

## Conditions

| ID | Status | Why | What would clear it |
| --- | --- | --- | --- |
| `C1_path_separation` | `REQUIRES INSTRUMENTATION` | A0 supports the parallel-path premise: 26/26 rows form a carrier with zero direct service; candidate formation is upstream but not independent, and admission leaves the carrier intact. No A- or K- cross-block was executed, so the two manipulations have not been shown to leave each other's path intact. | Implement A- and K-; show A- leaves K intact and K- leaves served availability intact on every seed within the precommitted tolerance. |
| `C2_treatment_consistency` | `REQUIRES INSTRUMENTATION` | No A-, K- or Y- execution exists in the committed artifacts. The A0 and provenance records are observational joins, not manipulations. | Run each manipulation and verify it drives its named path to zero while leaving the other path's measured quantity above zero. |
| `C3_positivity` | `REQUIRES INSTRUMENTATION` | The 26-row A0 slice is selected on never-served direct edges and every row has a carrier: 26 A-K+, 0 A+K+, 0 A+K- and 0 A-K-. The full candidate set has 492 served edges, but it has not been joined to carrier availability, so no four-cell denominator exists. | Join every eligible edge to both factors and require a non-zero denominator in all four cells and in the Y- arm at A+K+ and A-K+. |
| `C4_no_interference` | `REQUIRES INSTRUMENTATION` | No edge-level intervention was run, so there is no neighbour or spillover measurement to compare against a tolerance. | Run an edge-level manipulation with precommitted neighbour tolerances for A, K and Y; cluster or redesign if the tolerance is exceeded. |
| `C5_common_cause` | `REQUIRES INSTRUMENTATION` | Direct and reverse temporal counts are present for all 26 rows (23-47 direct), and they are formed before the carrier. The specified U also includes strength, but no edge-level strength field exists; carrier strength is a different quantity. U has not been joined to all four cells. | Record direct count, reverse count and edge strength before the outcome for every eligible edge, and join U to all cells without using a post-outcome rank. |
| `C6_temporal_resolution` | `REQUIRES INSTRUMENTATION` | Carrier formation cycles are present (37-117, median 76.0), but no artifact records an assertion cycle. K and Y therefore cannot be ordered at the same cycle resolution. | Record the assertion cycle per edge at the same resolution as formation, then test K-before-Y against Y-before-K without reverse-time imputation. |
| `C7_assertion_block` | `REQUIRES INSTRUMENTATION` | No assertion blockade exists. The Y- arm is a design specification, not an implemented manipulation, so its independence from A and K has not been measured. | Implement Y- and show it reduces assertion without changing A or K formation beyond the precommitted tolerance. |
| `C8_third_route` | `REQUIRES INSTRUMENTATION` | No A-K- double block exists and no precommitted ceiling has been fixed. The positive control is specified but not executable. | Fix the A-K- ceiling before the run, execute the double block, and distinguish no route from a third route. |
| `C9_same_object` | `REQUIRES INSTRUMENTATION` | No four-cell runner exists. A0 fixes six committed seeds, one world family, 120 cycles and cap 40, but it does not pair the four cells or the Y- arm. | Build a runner that fixes world, seed, cycles, cap, candidate universe and U across all cells; refuse any cell whose object differs. |

## What the audit does not say

It does not say the design is impossible. All nine conditions are potentially satisfiable.
It says none is cleared, and that the missing pieces are instrumentation rather than a
scientific refutation.

**Not evidence:** A design audit on six committed Q4 seeds, one world family, one build and one cap. It establishes no mechanism and runs no intervention.

## Reproduce

```bash
python -m benchmarks.c1_c9_preflight --check
```
