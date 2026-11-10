# Q006 admission re-derivation — result

**Verdict: `NO GAIN ON THIS LAYER` — SURVIVED the historical answer.**

Protocol: `docs/Q006-ADMISSION-RE-DERIVATION-PREREGISTRATION.md`. Engine: `0.13.0` (`ed0851d11947`). Seeds: 20510101–20510108, two arms, 120 cycles.

The historical answer was `NO GAIN ON THIS LAYER` on an unattributed build. This block re-runs the same endpoint on the pinned engine with a fresh seed block.

## Result

| Quantity | Value |
| --- | --- |
| Mean paired coverage gain (adopted − reference) | -0.069197 |
| 95% interval | [-0.095982, -0.043527] |
| Interval width | 0.052455 |
| Seeds positive | 0 of 8 |
| Mean paired precision difference | -0.075631 |
| Gain bar / guard | 0.08 / -0.05 |
| Determinism re-run matched | True |

## Per seed

| Seed | Coverage gain | Precision difference |
| --- | --- | --- |
| 20510101 | -0.116072 | -0.124259 |
| 20510102 | -0.044643 | -0.070985 |
| 20510103 | -0.008929 | -0.025541 |
| 20510104 | -0.125000 | -0.107430 |
| 20510105 | -0.080358 | -0.092783 |
| 20510106 | -0.080357 | -0.077381 |
| 20510107 | -0.062500 | -0.065854 |
| 20510108 | -0.035714 | -0.040817 |

## Gates

All gates passed: **True**.

**What this means.** the adopted rule does not cover more of the world here; the historical negative answer survives. The historical answer is **SURVIVED** on this block.

The cells are in `docs/q006_admission_rederivation.json`. No engine file changed; the adopted arm is an in-process restoration.
