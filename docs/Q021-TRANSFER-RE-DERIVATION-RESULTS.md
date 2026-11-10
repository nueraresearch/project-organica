# Q021 transfer re-derivation — result

**Verdict: `NO_TRANSFER_ADVANTAGE`.**

Protocol: `docs/Q021-TRANSFER-RE-DERIVATION-PREREGISTRATION.md`. Engine: `0.13.0` (`ed0851d11947`). Seeds: 10, four arms, 40/40 cycles.

## The four arms

| arm | mean cycles to acquire | mean TP |
| --- | --- | --- |
| `treatment` | 3.40 | 20 |
| `control_naive` | 3.40 | 20 |
| `control_pruned` | 3.40 | 20 |
| `control_orthogonal` | 3.40 | 20 |

Treatment TR: **1.000** (95% interval **1.000–1.000**).
Pruned TR: **1.000**; orthogonal TR: **1.000**.

## Criteria

| criterion | value | bar | pass |
| --- | --- | --- | --- |
| T1 transfer | TR 1.000, lower 1.000 | 1.25, lower > 1.00 | no |
| T2 attribution | pruned gap 0.000, orthogonal gap 0.000 | 0.10, lower > 0 | no |
| T3 paired | 0 of 10 seeds faster | 8 | no |
| T4 persistence | mean TP 20.50 | 20 | yes |

**What this means.** All four arms acquire at the same rate on every seed, so the v1 `TR = 3.2` does not re-derive on 0.13.0: this is `NO_TRANSFER_ADVANTAGE`, not an unrun manipulation. The harness's own earned-evidence assertion ran on every cell. This closes the v1 claim on this block; it does not establish transfer in general.

The cells are in `docs/q021_transfer_rederivation.json`. No engine file changed.
