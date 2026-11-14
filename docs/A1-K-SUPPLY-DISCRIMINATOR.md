# A1 K-supply discriminator — capacity vs support

**ID:** `A1-K-SUPPLY-DISCRIMINATOR-1`
**Status:** `DIAGNOSTIC — CAPACITY VS SUPPORT; NO TARGET, NO PROTOCOL CHANGE, NO RUN`

**This is a diagnostic, not an A1 result.** It changes only the prediction cap on a fixed no-arm world and stratifies existing pair support. It selects no target, changes no protocol and runs no A1 cell.

## Predeclared axes

- **Capacity:** the fixed 28-tag world at caps **20, 40, 80**. A capacity signal requires K at 80 at least **10%** above 40, K at 20 at least **10%** below 40, and at least **4/6** seeds moving each way.
- **Support:** candidate edges binned by directed pair occurrences in the trainable acquisition stream. A support signal requires a monotone K-density gradient (2 pp tolerance) across bins with at least **20** edges and a high-minus-low spread of at least **20 pp**.
- **Matched support:** for bins with at least **20** edges in both worlds, the edge-weighted 16-vs-28 K-density gap must be at most **15 pp**.

These thresholds are a reporting convention fixed before the cap runs, not an A1 gate.

## Capacity sweep — fixed 28-tag world

| Cap | Candidate edges | A | K | A&K | K density | K vs cap 40 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 1000 | 271 | 240 | 89 | 24.0% | -4 |
| 40 | 1000 | 353 | 244 | 119 | 24.4% | +0 |
| 80 | 1000 | 498 | 244 | 154 | 24.4% | +0 |

**Capacity result:** high lift **+0.0%**, low drop **+1.6%**; seed agreement **1/6** high and **3/6** low. `capacity_signal` = **False**.

**A/K decoupling:** across caps 20 → 40 → 80, A rises **271 → 353 → 498** while K stays **240 → 244 → 244**. The prediction cap moves the prediction path strongly and the carrier path not at all. This closes **prediction-cap** capacity as the K bound; it does not test every possible capacity bound.

## Support stratification — cap 40

| Support bin | 16-tag edges | 16-tag K density | 28-tag edges | 28-tag K density |
| --- | ---: | ---: | ---: | ---: |
| 1 | — | — | 3 | 33.3% |
| 2-3 | — | — | 75 | 10.7% |
| 4-7 | — | — | 437 | 21.7% |
| 8-15 | 82 | 42.7% | 463 | 28.3% |
| 16+ | 301 | 68.8% | 22 | 40.9% |

**Support result:** eligible bins **2-3, 4-7, 8-15, 16+**, monotone **True**, spread **30.2 pp**. `support_signal` = **True**.

Support is real but not sufficient. At matched support, the 16-tag world still has more K: the 8–15 bin is **42.7% vs 28.3%** and 16+ is **68.8% vs 40.9%**. The weighted gap is **25.0 pp**, above the predeclared 15 pp matched threshold.

## Matched support

| Bin | 16-tag edges | 16-tag K density | 28-tag edges | 28-tag K density | Gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| 8-15 | 82 | 42.7% | 463 | 28.3% | +14.4 pp |
| 16+ | 301 | 68.8% | 22 | 40.9% | +27.9 pp |

Weighted matched gap: **25.0 pp**. `matched_support_signal` = **False**.

## Reading

| Axis | Signal |
| --- | --- |
| Capacity | **False** |
| Support | **True** |
| Matched support | **False** |

**Classification:** `SUPPORT-ASSOCIATED, NOT FULLY EXPLANATORY`.

This is a diagnostic reading, not a redesign decision. The cap result says the K path is not prediction-cap-bound. The support result says pair frequency is part of the story, but the residual 16-vs-28 gap at matched support means support alone is not the whole story. The next discriminator should target the carrier path directly, not another prediction cap or another tag count.

## Limits

- Cap 80 is a diagnostic condition, not an A1 protocol or a proposed cap.
- The capacity axis tests prediction capacity only; a null result does not close every possible carrier-capacity bound.
- A and K are no-arm availability flags over 120 cycles, not treatment measurements.
- Support is directed pair count over the full acquisition window, not a pre-U predictor; its direction is not identified.
- Support is not a latent support probability.
- The 16-tag and 28-tag worlds differ in tag count and mapping; matched-support bins are descriptive, not a controlled experiment.
- Six seeds per world; the classification thresholds are a reporting convention and can be overturned by a different construction.
- No target, threshold, freeze, grant or run changed.

**Not evidence:** A no-arm diagnostic on fixed worlds.  It manipulates only the prediction cap for a capacity read and stratifies existing support; it selects no target, changes no protocol and runs no A1 cell.

## Reproduce

```bash
python -m benchmarks.a1_k_supply_discriminator --check
python -m benchmarks.a1_k_supply_discriminator --self-test
```
