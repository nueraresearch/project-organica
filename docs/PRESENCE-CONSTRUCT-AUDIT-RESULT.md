# Presence to assertion: the construct audit — result

Generated from `docs/presence_construct_audit_run.json` by `python -m benchmarks.presence_construct_audit --finish`. Do not edit by hand.

**Verdict: `CONSTRUCT VALID`**

| Seed | W | P | S_ever | S_final | A_W | A_pred | A_other |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20261100 | 112 | 112 | 84 | 37 | 40 | 37 | 3 |
| 20261101 | 112 | 112 | 73 | 38 | 44 | 38 | 6 |
| 20261102 | 112 | 112 | 82 | 31 | 38 | 31 | 7 |
| 20261103 | 112 | 112 | 78 | 38 | 46 | 38 | 8 |
| 20261104 | 112 | 112 | 68 | 26 | 34 | 26 | 8 |
| 20261105 | 112 | 112 | 75 | 38 | 47 | 38 | 9 |

## Gates

| Gate | Result |
| --- | --- |
| `C1_build` | PASS |
| `C2_world` | PASS |
| `C3_presence` | PASS |
| `C4_denominator` | PASS |
| `C5_object` | PASS |
| `C6_witnesses` | PASS |
| `C7_seed_axis` | PASS |
| `C8_determinism` | PASS |
| `C9_audit_row_reproduced` | PASS |

The gates are read in the record's declared order: `C1_build` -> `C8_determinism` -> `C5_object` -> `C4_denominator` -> `C2_world` -> `C3_presence` -> `C6_witnesses` -> `C7_seed_axis` -> `C9_audit_row_reproduced`. The first failure names the verdict.

## What this does not claim

This block does not show that the cap causes the presence/assertion gap, that conversion is efficient or defective, or that any mechanism is responsible. It does not measure `C`, `E`, `R` or `U`, and it does not establish a conversion rate beyond these six historical seeds. It may show only whether the endpoints are the same object on the same world, build and window; a `CONSTRUCT VALID` result is a measurement precondition, not a finding about the organism.

## Reproduce

```bash
python -m benchmarks.presence_construct_audit --measure
python -m benchmarks.presence_construct_audit --finish
python -m benchmarks.presence_construct_audit --check
```
