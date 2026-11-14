# A1 successor preflight — no-arm C1/K gate

**ID:** `A1-SUCCESSOR-PREFLIGHT-1`
**Status:** `NOT RUN — NO SUCCESSOR UNIVERSE; CURRENT CONTROL FAILS`

**No target is selected, frozen or run.** This checks whether a supplied successor universe clears the **≥60 independent K/A rows per seed** gate before any target freeze. Without a candidate, the result is **NOT RUN**.

## Gate

| Check | Requirement |
| --- | --- |
| Independent stream | ≥60 independent edges/seed; no duplicate or reverse-duplicate orientations |
| C1 ceiling | `min(A available, K available, independent edges)` ≥60/seed |
| Targets | If in scope, a capacity-respecting **20-row** baseline A+K matching |
| Seeds | At least **6** |

## Current six-seed control

This is a negative control, not a successor candidate.

| Seed | Independent | A | K | C1 ceiling | Gap to 60 | Target pool | Matching | Result |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20630101` | 64 | 44 | 44 | 44 | 16 | 32 | 32 | FAIL |
| `20630102` | 63 | 44 | 31 | 31 | 29 | 23 | 23 | FAIL |
| `20630103` | 64 | 52 | 39 | 39 | 21 | 36 | 36 | FAIL |
| `20630104` | 64 | 43 | 35 | 35 | 25 | 27 | 27 | FAIL |
| `20630105` | 64 | 49 | 43 | 43 | 17 | 35 | 35 | FAIL |
| `20630106` | 63 | 49 | 36 | 36 | 24 | 33 | 33 | FAIL |

**Control result:** `FAIL` — 0/6 seeds pass.

## Successor candidate

**NOT RUN.** No successor universe or fresh seed block has been supplied. The current universe is not eligible: its C1 ceiling is **31–44**, below 60.

Supply a `--spec` JSON with one orientation per undirected pair and no-arm A/K rows per edge; the preflight will return `PASS` or `FAIL` before any target freeze.

## Disposition

Even a `PASS` here does **not** freeze or authorise a run. It establishes only that the supplied no-arm universe clears the C1/K gate and, if in scope, the 20-target matching gate. A new protocol, freeze, seed reservation, grant and run remain separate acts.

**Not evidence:** A no-arm preflight. It evaluates supplied baseline rows, selects no target, freezes no target, reserves no seed, issues no grant and runs no A1 cell. The current six-seed universe is a negative control, not a successor candidate.

## Reproduce

```bash
python -m benchmarks.a1_successor_preflight --check
python -m benchmarks.a1_successor_preflight --self-test
python -m benchmarks.a1_successor_preflight --spec candidate.json --write
```
