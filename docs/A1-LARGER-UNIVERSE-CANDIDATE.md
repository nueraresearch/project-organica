# A1 larger-universe candidate

**ID:** `A1-LARGER-UNIVERSE-CANDIDATE-1`  
**Status:** `CANDIDATE SPEC — NO ARM, NO TARGET, NOT FROZEN, NOT RUN`

**No target is selected, frozen or run.** This is a separately declared **28-tag**, 7-tags-per-cell world on the same four-cell law and 120-cycle horizon, evaluated through the no-arm preflight.

## Construction

The 16-tag world tops out at 64 independent candidate edges. This candidate fixes a **28-tag** pool before measuring K, with 7 tags per cell, 8 events per cycle, and the same first-36-cycle one-orientation rule. The edge count is structural; no K value chose the pool or the size.

| Seed | Candidate edges | Independent | A | K | A&K |
| ---: | ---: | ---: | ---: | ---: | ---: |
| `20660101` | 169 | 169 | 59 | 23 | 18 |
| `20660102` | 167 | 167 | 50 | 40 | 15 |
| `20660103` | 172 | 172 | 57 | 42 | 16 |
| `20660104` | 165 | 165 | 67 | 55 | 26 |
| `20660105` | 169 | 169 | 66 | 47 | 26 |
| `20660106` | 158 | 158 | 54 | 37 | 18 |

## Preflight result

**`FAIL`** — 0/6 seeds pass.

| Seed | C1 ceiling | Gap to 60 | 20-row matching | Result |
| ---: | ---: | ---: | ---: | --- |
| `20660101` | 23 | 37 | 18 | FAIL |
| `20660102` | 40 | 20 | 15 | FAIL |
| `20660103` | 42 | 18 | 16 | FAIL |
| `20660104` | 55 | 5 | 26 | FAIL |
| `20660105` | 47 | 13 | 26 | FAIL |
| `20660106` | 37 | 23 | 18 | FAIL |

**This is a candidate result, not a freeze or a run.** A PASS would only mean the declared universe clears the 60-row C1 gate and, if in scope, the 20-row matching; a new protocol, freeze, seed reservation and grant remain separate acts.

**Not evidence:** a no-arm candidate and preflight. It selects no target, reserves no seed, freezes no target, issues no grant and runs no cell.

## Reproduce

```bash
python -m benchmarks.a1_larger_universe --check
python -m benchmarks.a1_larger_universe --self-test
python -m benchmarks.a1_successor_schema --check
```
