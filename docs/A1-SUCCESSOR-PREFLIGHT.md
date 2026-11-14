# A1 successor preflight — no-arm C1/K gate

**ID:** `A1-SUCCESSOR-PREFLIGHT-1`
**Status:** `FAIL — SUCCESSOR CANDIDATE BELOW GATE`

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

| Seed | Independent | A | K | C1 ceiling | Gap to 60 | Target pool | Matching | Result |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20650101` | 64 | 49 | 40 | 40 | 20 | 33 | 33 | FAIL |
| `20650102` | 64 | 46 | 37 | 37 | 23 | 30 | 30 | FAIL |
| `20650103` | 64 | 54 | 46 | 46 | 14 | 46 | 46 | FAIL |
| `20650104` | 64 | 53 | 42 | 42 | 18 | 36 | 36 | FAIL |
| `20650105` | 63 | 31 | 39 | 31 | 29 | 20 | 20 | FAIL |
| `20650106` | 64 | 46 | 38 | 38 | 22 | 32 | 32 | FAIL |

**Candidate result:** `FAIL` — 0/6 seeds pass.

## Disposition

Even a `PASS` here does **not** freeze or authorise a run. It establishes only that the supplied no-arm universe clears the C1/K gate and, if in scope, the 20-target matching gate. A new protocol, freeze, seed reservation, grant and run remain separate acts.

**Not evidence:** A no-arm preflight. It evaluates supplied baseline rows, selects no target, freezes no target, reserves no seed, issues no grant and runs no A1 cell. The current six-seed universe is a negative control, not a successor candidate.

## Reproduce

```bash
python -m benchmarks.a1_successor_preflight --check
python -m benchmarks.a1_successor_preflight --self-test
python -m benchmarks.a1_successor_preflight --spec candidate.json --write
```
