# A1 two-path dry-run manifest

**ID:** `A1-TWO-PATH-1`  
**Status:** `GRANTED, RUN — VOID (C4_DELTA)`

**This is not an experimental result. No cell, seed or database is used.**

The manifest fixes the six cells and the candidate seed block for the A−, K− and Y− arms.
The treatments are implemented; it does not authorise a run.

## Object

| Field | Value |
| --- | --- |
| World | compositional world family |
| Candidate universe | fixed compositional-world directed-edge universe |
| Seeds | 20740101, 20740102, 20740103, 20740104, 20740105, 20740106 |
| Cycles | 120 |
| Cap | 40 |
| Frozen | yes |
| C5 U cycle | 4 |
| Target-selection U cycle | 36 |
| Target edges | FIXED BEFORE FREEZE — FROZEN BY A1-TARGET-FREEZE-N20-1, SIGNED 2026-11-15 |
| Cells | 36 |
| Determinism control | seed 20740101, `A+K+` |

The seeds are **provisional candidates**, not reserved or frozen. The C5 `U` is fixed before
carrier, K and Y, and every cell of a seed must carry one object fingerprint. The cycle-36
sample remains the target-selection diagnostic. The target edges are **unresolved** and must
be fixed before freeze: `FIXED BEFORE FREEZE — FROZEN BY A1-TARGET-FREEZE-N20-1, SIGNED 2026-11-15`.

## Cells

| Cell | Admission | Carrier | Assertion |
| --- | --- | --- | --- |
| `A+K+` | allowed | available | on |
| `A+K-` | allowed | blocked | on |
| `A-K+` | blocked | available | on |
| `A-K-` | blocked | blocked | on |
| `Y_MINUS_A+K+` | allowed | available | blocked |
| `Y_MINUS_A-K+` | blocked | available | blocked |

## Gate

Every executing path calls `refuse()` before a database is opened. The gate checks the
frozen flag, a dated run-authorising grant, the shipped engine, the built arms, the
planned cell set, the fixed target set, the object fields and seed freshness.

A grant must be recorded in this manifest as `authorisation.granted: true`, with
`granted_on`, an existing `document`, and a run-authorising `quote`. A preparation-only
quote fails. The manifest is currently `GRANTED, RUN — VOID (C4_DELTA)` and its target edges are `FIXED BEFORE FREEZE — FROZEN BY A1-TARGET-FREEZE-N20-1, SIGNED 2026-11-15`, so the gate
refuses every cell. The A-/K-/Y- treatments are implemented; only the gate is closed.

## Commands

```bash
python -m benchmarks.a1_two_path --dry-run
python -m benchmarks.a1_two_path --check
python -m benchmarks.a1_two_path --self-test
python -m benchmarks.a1_c5_target_timing --check
python -m benchmarks.a1_two_path --cell A+K+ --seed 20630101
python -m benchmarks.a1_two_path --measure
```

**Not evidence:** A frozen manifest whose block has run once. The assembly is VOID on C4 and five structural gates were read against the wrong target list; nothing here is an effect estimate, and the manifest now refuses a second run.
