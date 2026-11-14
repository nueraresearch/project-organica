# A1 gate readiness

**Date:** 2026-11-14  
**Verdict:** `NOT ADMISSIBLE — 1 SATISFIED, 8 CONTRACT-BUILT BUT UNRUN, 0 UNSATISFIABLE`

**This is not an experimental result.** No cell, seed, intervention or engine change was made.

C6 is satisfied by the committed C6-TIMING-1 block. The other eight gates have executable contracts and synthetic controls; C1/C4/C7 thresholds and the C8 ceiling are precommitted. C1 and C4 are one adopted post-freeze VOID gate; a failed or unmeasurable C1 or C4 makes the run VOID. Other open gates retain their own terminal dispositions. Each open gate has one attempt: no A1 patch, threshold change, extra cell or rerun; a new registered design is required to try again. None can be cleared from the observational records because each needs an A-, K-, Y- or A-K- cell that has not run. The design remains not admissible and no causal model is read.

## Counts

| Classification | Count |
| --- | ---: |
| Satisfied | 1 |
| Contract built, not run | 8 |
| Unsatisfiable | 0 |

## Precommitted thresholds

| Gate | Quantity | Value |
| --- | --- | ---: |
| `C1_path_separation` | A- carrier preservation | 0.95 |
| `C1_path_separation` | K- served preservation | 0.95 |
| `C4_no_interference` | neighbour delta | 0.05 |
| `C7_assertion_block` | A delta under Y- | 0.05 |
| `C7_assertion_block` | K delta under Y- | 0.05 |
| `C8_third_route` | A-K- assertion ceiling | 0.05 |

See [`A1-PRECOMMITTED-THRESHOLDS.md`](A1-PRECOMMITTED-THRESHOLDS.md) for definitions and fragility.

## Bounded paths

One implementation and one registered run per gate. A failed or unmeasurable C1 or C4 is VOID under the adopted C1/C4 gate; other gate dispositions are recorded in their own rows. All are terminal: no A1 patch, threshold change, extra cell or rerun. A new registered design is required to try again.

| Gate | Attempts | Success | Failure | Unmeasurable |
| --- | ---: | --- | --- | --- |
| `C1_path_separation` | 1 | The C1 contract passes on every seed. | VOID: C1 path separation failed; the A1 run is not admissible. | VOID: no paired-control denominator; the A1 run is not measurable. |
| `C2_treatment_consistency` | 1 | The C2 contract passes on every seed. | VOID: the intervention did not happen as specified. | UNSATISFIABLE: a required manipulation has no denominator. |
| `C3_positivity` | 1 | The C3 contract passes on every seed and edge. | VOID: a required cell is empty. | UNSATISFIABLE: no eligible edge can populate the cells. |
| `C4_no_interference` | 1 | The C4 contract passes on every non-target edge. | VOID: a non-target A, K or Y delta exceeds 0.05; the A1 run is invalid. | VOID: no non-target edge has a measurable delta; the A1 run is not measurable. |
| `C5_common_cause` | 1 | The C5 contract passes on every row. | SHARED CAUSE / NO CARRIER RELATION NOT SEPARATED. | UNSATISFIABLE: U has no pre-outcome measurement on a required row. |
| `C7_assertion_block` | 1 | The C7 contract passes on every seed and at both Y- cells. | SHARED CAUSE / READOUT NOT SEPARATED. | UNSATISFIABLE: no Y- cell has a paired control. |
| `C8_third_route` | 1 | A-K- assertion is at or below the precommitted 0.05 ceiling on every seed. | THIRD ROUTE PRESENT: the two-path model is incomplete. | UNSATISFIABLE: A-K- has no denominator. |
| `C9_same_object` | 1 | The C9 contract passes for every seed. | VOID: the comparison is not paired. | UNSATISFIABLE: a paired cell has no object fingerprint. |

C6 is satisfied and closed; it needs no stop condition. A terminal failure is not a
reason to patch A1, retune a threshold or add a cell.

## Gate order

**C1 and C4 are one POST-FREEZE VOID GATE**, not pre-freeze admissibility conditions. Neither can be observed before cells exist. Freeze the targets, grant the run, then assemble C1/C4; a C1 or C4 failure, or either being unmeasurable, makes the run VOID. The targets remain draft because no separate owner freeze act has been recorded.

**C1:** A missing or below-60 paired-control denominator, or a C1 preservation failure on any seed or path, makes the A1 run VOID.

**C4:** Any measurable non-target A, K or Y neighbour delta above 0.05, or an unmeasurable non-target stream, makes the A1 run VOID.

## C7/C8 denominator unit

**ADOPTED — BINDING FOR A1 (2026-11-14).** C7 and C8 are evaluated **per seed**; rows are not pooled across seeds. Every seed must pass on its own rows. See [`A1-C7-C8-DENOMINATOR.md`](A1-C7-C8-DENOMINATOR.md).

At N=4 C7 has **8** Y- rows for cell completeness and the assertion-order check, but its 0.05 A/K margin is a **per-edge rate over 120 cycles** (`1/120 = 0.008333`), so C7 is **RESOLVED** at N=4. C8 has **4** A-K- target rows (`1/4 = 0.25`); at the N=8 maximum it has **8** (`1/8 = 0.125`). C8 needs at least 20 rows (N>=20) for one-step resolution, above the 16-vertex, eight-target maximum. A separate **N=20 C8 expansion design** is registered in [`A1-C8-EXPANSION.md`](A1-C8-EXPANSION.md); it gives 20 A-K- rows per seed and a 0.05 step, resolving C8 **if adopted**, but it is not the live manifest and is not frozen. The current design is therefore **UNDER-RESOLVED for C8 only**; that is a design blocker, not a threshold change.

## Gates

| ID | Status | Current evidence | Contract | Remaining |
| --- | --- | --- | --- | --- |
| `C1_path_separation` | `CONTRACT BUILT; THRESHOLD PRECOMMITTED, NOT RUN` | A0 supports the parallel-path premise: 26/26 rows form a carrier with zero direct service, and admission leaves the carrier intact. No A- or K- arm has been executed, so cross-path separation has not been observed. Threshold: at least 95% preservation of the other path, per seed. | gate_c1(rows, tolerance): among paired-control available edges, A- keeps K and K- keeps A at or above the tolerance on every seed. | Implement A-/K- and run the arms; the threshold is already fixed. |
| `C2_treatment_consistency` | `CONTRACT BUILT; NO ARM RUN` | No A-, K- or Y- execution exists; the A0 records are observational joins. | gate_c2(rows): A- drives A to zero, K- drives K to zero, Y- drives Y to zero while the other path stays above zero. | Run each manipulation and verify its named path moved. |
| `C3_positivity` | `CONTRACT BUILT; ONE CELL ONLY` | The A0 slice contributes only A-K+ (26 rows); A+K+, A+K- and A-K- have no denominators, and the Y- cells do not exist. | gate_c3(rows): every eligible edge has all four A x K cells and every seed has both Y- cells. | Join every eligible edge to both factors and observe all six cells. |
| `C4_no_interference` | `CONTRACT BUILT; THRESHOLD PRECOMMITTED, NOT RUN` | No edge-level intervention was run, so there is no neighbour delta to compare. Threshold: absolute A/K/Y delta no greater than 0.05 on non-target edges. | gate_c4(rows, tolerance): every non-target edge's A, K and Y neighbour delta stays within tolerance. | Implement the edge-level arms and measure spillover; the threshold is already fixed. |
| `C5_common_cause` | `CONTRACT BUILT; U NOT JOINED` | Direct and reverse counts exist for all 26 A0 rows; an edge-level strength field is present on 0 rows, and U is not joined to all four cells or either Y- cell. | gate_c5(rows): direct count, reverse count and strength are present and measured before the carrier, K and Y on every row. | Measure edge strength for every eligible edge and join U to all cells before the outcome. |
| `C6_temporal_resolution` | `SATISFIED` | C6-TIMING-1 returned `C6 ORDER VARIATION CONFIRMED` on six fresh seeds; N1-N7 pass. | The C6 block's N1-N7 and per-order floors are the gate. | None for C6. |
| `C7_assertion_block` | `CONTRACT BUILT; THRESHOLD PRECOMMITTED, NOT RUN` | No Y- assertion blockade exists; A and K have not been held fixed under Y-. Threshold: absolute A/K formation delta no greater than 0.05. C7 is evaluated per seed and per edge; the margin is a rate over 120 cycles (one cycle = 0.008333), so it is resolvable at N=4. The eight Y- rows are for cell completeness and the assertion-order check, not the 0.05 rate denominator. Target rows now emit A/K/Y rates. | gate_c7(rows, tolerance): on every seed, both Y- cells lower assertion while A and K formation stay within tolerance. | Implement Y- and run it at A+K+ and A-K+; the threshold is already fixed. |
| `C8_third_route` | `CONTRACT BUILT; CEILING PRECOMMITTED, NOT RUN` | No A-K- double block exists. The T8 ceiling is precommitted at 0.05, so a double-block assertion rate above 5% on any seed reads THIRD ROUTE PRESENT. C8 is evaluated per seed; at N=4 that is four rows and a 0.25 step. A separate N=20 expansion design is registered; it is not the live manifest and is not frozen. | gate_c8(rows, ceiling): on every seed, A-K- assertion is at or below the precommitted ceiling. | Implement the double block and run it; the ceiling is already fixed. |
| `C9_same_object` | `CONTRACT BUILT; NO PAIRED CELLS` | A0 fixes six committed seeds, 120 cycles and cap 40; the design fixes A+K+, A+K-, A-K+, A-K- and Y- at A+K+/A-K+, but no cell exists to pair. | gate_c9(rows): every cell of a seed carries one world/cycles/cap/candidate-universe/U fingerprint. | Run the paired cells and refuse any cell whose object fingerprint differs. |

## Controls

`python -m benchmarks.a1_gate_readiness --self-test` builds a passing six-cell fixture and a
targeted defect for every contract. Each gate must accept the fixture and reject its defect;
a missing tolerance or ceiling must fail. The self-test runs no engine.

**Not evidence:** A gate-contract audit on committed records. It runs no cell, assigns no seed and establishes no causal, capability or transfer claim.

## Reproduce

```bash
python -m benchmarks.a1_gate_readiness --check
python -m benchmarks.a1_gate_readiness --self-test
```
