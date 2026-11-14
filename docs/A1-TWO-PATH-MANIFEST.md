# A1 two-path dry-run manifest

**ID:** `A1-TWO-PATH-1`  
**Status:** `REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT`

**This is not an experimental result. No cell, seed or database is used.**

The manifest fixes the six cells and the candidate seed block for the A−, K− and Y− arms.
The treatments are implemented; it does not authorise a run.

## Object

| Field | Value |
| --- | --- |
| World | compositional world family |
| Candidate universe | fixed compositional-world directed-edge universe |
| Seeds | 20630101, 20630102, 20630103, 20630104, 20630105, 20630106 |
| Cycles | 120 |
| Cap | 40 |
| Frozen | no |
| U cycle | 36 |
| Target edges | UNRESOLVED — MUST BE FIXED BEFORE FREEZE |
| Cells | 36 |
| Determinism control | seed 20630101, `A+K+` |

The seeds are **provisional candidates**, not reserved or frozen. `U` is fixed before
carrier, K and Y, and every cell of a seed must carry one object fingerprint. The target
edges are **unresolved** and must be fixed before freeze: `UNRESOLVED — MUST BE FIXED BEFORE FREEZE`.

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
quote fails. The manifest is currently `REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT` and its target edges are `UNRESOLVED — MUST BE FIXED BEFORE FREEZE`, so the gate
refuses every cell. The A-/K-/Y- treatments are implemented; only the gate is closed.

## Commands

```bash
python -m benchmarks.a1_two_path --dry-run
python -m benchmarks.a1_two_path --check
python -m benchmarks.a1_two_path --self-test
python -m benchmarks.a1_two_path --cell A+K+ --seed 20630101
python -m benchmarks.a1_two_path --measure
```

**Not evidence:** A dry-run manifest and grant gate. No cell, seed or database is used; this is not a result and does not authorise a run.
