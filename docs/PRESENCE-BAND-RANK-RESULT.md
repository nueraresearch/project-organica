# PRESENCE-BAND-1 -- result

**VOID.** A gate failed, so the block is unrun or non-reproducible and no acceptance is read.

## Gates

| Gate | Result |
| --- | --- |
| `B1_build` | PASS |
| `B2_world` | PASS |
| `B3_band_identity` | PASS |
| `B4_control_40` | PASS |
| `B5_cap_live` | FAIL |
| `B6_denominator` | PASS |
| `B7_determinism` | PASS |
| `B8_seed_axis` | PASS |

## Named edges served at 112

| Seed | Served at 112 (of 62) |
| ---: | ---: |
| 20611601 | 12 |
| 20611602 | 9 |
| 20611603 | 16 |
| 20611604 | 9 |
| 20611605 | 14 |
| 20611606 | 2 |

## Decision

Record VOID; fix the harness and register a new block; read no acceptance.

The block ran under the dated grant; it reads whether the 62 named edges enter service, not a capability or retention claim.
