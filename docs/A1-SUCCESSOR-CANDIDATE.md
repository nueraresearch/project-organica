# A1 successor candidate — fresh seed block

**ID:** `A1-SUCCESSOR-CANDIDATE-1`
**Status:** `CANDIDATE SPEC — NO ARM, NO TARGET, NOT FROZEN, NOT RUN`

**No target is selected, frozen or run.** This is a fresh six-seed candidate for the no-arm preflight, not a successor design adopted by the project. It uses the opt-in cycle-boundary correction for candidate formation; the registered selector remains unchanged.

## Why this block

The block is **20650101–20650106**, fixed before any K measurement: six contiguous fresh seeds on the same 16-tag compositional world family and the same first-36-cycle candidate universe. It is not screened for high K availability; screening on K would select on the quantity being tested.

| Seed | Candidate edges | Independent | A | K | A&K |
| ---: | ---: | ---: | ---: | ---: | ---: |
| `20650101` | 64 | 64 | 49 | 40 | 33 |
| `20650102` | 64 | 64 | 46 | 37 | 30 |
| `20650103` | 64 | 64 | 54 | 46 | 46 |
| `20650104` | 64 | 64 | 53 | 42 | 36 |
| `20650105` | 63 | 63 | 31 | 39 | 20 |
| `20650106` | 64 | 64 | 46 | 38 | 32 |

## Preflight result

**`FAIL`** — 0/6 seeds pass.

| Seed | C1 ceiling | Gap to 60 | Target matching | Result |
| ---: | ---: | ---: | ---: | --- |
| `20650101` | 40 | 20 | 33 | FAIL |
| `20650102` | 37 | 23 | 30 | FAIL |
| `20650103` | 46 | 14 | 46 | FAIL |
| `20650104` | 42 | 18 | 36 | FAIL |
| `20650105` | 31 | 29 | 20 | FAIL |
| `20650106` | 38 | 22 | 32 | FAIL |

**This is a candidate result, not a freeze or a run.** A PASS would only mean the no-arm universe clears the 60-row C1/K gate; a new protocol, freeze, seed reservation and grant remain separate acts.

**Not evidence:** A no-arm candidate specification and its raw A/K rows. It selects no target, freezes no target, reserves no seed, issues no grant and runs no A1 cell. Passing the preflight would not authorise a run.

## Reproduce

```bash
python -m benchmarks.a1_successor_candidate --check
python -m benchmarks.a1_successor_candidate --self-test
python -m benchmarks.a1_successor_candidate --write
python -m benchmarks.a1_successor_preflight --spec docs/a1_successor_candidate.json --write
```
