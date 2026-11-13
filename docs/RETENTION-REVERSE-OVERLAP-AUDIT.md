# Reverse-time model overlap audit

**Scope:** the recorded `CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` result. This audit reads `docs/retention_formation_anchored.json`; it runs no cell and spends no seed. It is a diagnostic, not a new primary test and not evidence for a temporal-order claim.

**Population:** the 166 fitted complete cases, 70 asserted events, from the corrected 172 eligible edges.

## Definitions at issue

The reverse model uses:

```
late_retention = distinct loop cycles in f+20..120 / (120 - (f + 20) + 1)
followup       = (120 - (f + 20) + 1) / 120
```

Let `available = 120 * followup = 101 - f`. Then:

```
late_retention = late_loop_cycles / available
```

The follow-up control is therefore the denominator of the late-retention rate, scaled by 120. That is a structural overlap by construction. The question is whether it materially destabilizes the fitted reverse coefficient.

## 1. Correlation and collinearity

| Quantity | Value |
| --- | ---: |
| Pearson `late_retention` vs `followup` | **−0.298** |
| Spearman `late_retention` vs `followup` | **−0.251** |
| Pearson after within-seed centering | **−0.323** |
| Pairwise VIF, either variable | **1.097** |
| Multivariate VIF, `late_retention` | **1.199** |
| Multivariate VIF, `followup` | **5.446** |
| Pearson `early_retention` vs `late_retention` | **0.524** |

The late-retention/follow-up pair is not materially collinear: pairwise VIF is **1.10**, and late retention's multivariate VIF is **1.20**. The higher follow-up VIF (**5.45**) comes from its joint structure with rank, count, strength and the seed fixed effects, not from late retention alone. The seed-residual correlation (**−0.32**) is close to the raw correlation, so seed composition is not hiding a stronger relationship.

## 2. Refits

All models are Firth logistic with seed fixed effects and the recorded controls (`rank20`, `count20`, `strength20`), on the same 166 complete cases and 70 events. The late coefficient is per 1 SD of the named variable.

| Model | Late OR | 95% CI | Follow-up OR | AUC |
| --- | ---: | ---: | ---: | ---: |
| Recorded reverse (`late_retention` + `followup`) | **32.83** | **8.66–124.44** | 0.88 (0.22–3.45) | 0.961 |
| Reverse without `followup` | **33.50** | **9.05–124.03** | — | 0.961 |
| `late_retention` + `followup` only | **31.17** | **9.01–107.89** | 1.13 (0.61–2.07) | 0.961 |
| `late_retention` only | **33.23** | **9.20–120.02** | — | 0.960 |
| Raw late count + `followup` | **31.43** | **9.15–107.87** | — | 0.964 |
| Raw late count, no `followup` | **26.89** | **8.59–84.15** | — | 0.963 |

The late coefficient is stable across every specification. Dropping the follow-up control changes the OR from **32.83** to **33.50**; replacing the rate with a raw late count and keeping follow-up gives **31.43**. The intervals overlap almost completely. The reverse association is therefore **not** an artifact of follow-up collinearity.

This does not make the reverse coefficient an effect estimate. It makes it robust to the specific overlap being audited.

## 3. The larger fragility: boundary separation

| `late_retention` | Edges | Asserted | Event rate |
| --- | ---: | ---: | ---: |
| `0.0` | **55** | **1** | **1.8%** |
| `0 < x < 1` | **100** | **58** | **58.0%** |
| `1.0` | **11** | **11** | **100.0%** |

Eleven edges sit at the ceiling and all eleven are asserted; fifty-five sit at zero and only one is asserted. The OR of **32.83** is therefore largely a **boundary contrast**, not a graded dose-response. Firth keeps the coefficient finite, but the interval is wide (**8.66–124.44**) and the coefficient should not be read as "each SD of late retention multiplies the odds by 33."

The follow-up quartiles show the same pattern without a monotone late-retention gradient:

| Follow-up quartile | Mean follow-up | Mean late retention | Asserted | Event rate |
| --- | ---: | ---: | ---: | ---: |
| Q1 | 0.266 | 0.391 | 19/41 | 46.3% |
| Q2 | 0.437 | 0.432 | 26/42 | 61.9% |
| Q3 | 0.616 | 0.303 | 14/41 | 34.1% |
| Q4 | 0.726 | 0.167 | 11/42 | 26.2% |

The event rate falls with follow-up, and late retention also falls after Q2, but neither pattern is the source of the stable reverse OR. The ceiling/zero split is.

## 4. Conclusion

1. **No material late-retention/follow-up collinearity.** Pairwise VIF is **1.10**, late VIF is **1.20**, and the late OR moves by less than one unit when follow-up is removed. The **32.83** is not a follow-up artifact.

2. **The structural overlap is real even though the statistical overlap is modest.** Follow-up is the denominator of the late-retention rate by construction. A future block should avoid a rate whose denominator is also a fitted control; fixed 20-cycle windows do that directly.

3. **The reverse coefficient is a boundary contrast.** **11/11** ceiling cases are asserted, **58/100** middle cases are asserted, and **1/55** zero cases are asserted. Report all three groups beside the OR; do not present **32.83** as a dose-response effect.

4. **The verdict does not move.** `CONFIRMED, TEMPORALLY AMBIGUOUS` stands: R1 fails because post-landmark retention separates the outcome, and the reverse model cannot establish that early retention precedes assertion. This audit narrows the reason: the reverse signal is real in this sample but is concentrated at the boundaries, and it is not caused by the follow-up control.

## 5. Consequence for the proposed entry-transition block

The proposed `PROPOSED-RETENTION-ENTRY-TRANSITION-1` design avoids this overlap in three ways:

- both predictors are fixed 20-cycle rates: early `f..f+19`, proximal `f+20..f+39`;
- both windows end before the outcome window `f+40..120`;
- the follow-up control is not the denominator of either rate.

It also replaces the ceiling/zero contrast with a two-cycle entry transition and a structure-free interval, so the outcome is a state change rather than final presence. See `docs/RETENTION-ENTRY-TRANSITION-DESIGN.md`.
