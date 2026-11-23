# Q053 mechanism result — the 20-cell block on `lattice_L1`

Generated from `docs/q053_mechanism_run.json` by `python -m benchmarks.q053_mechanism_run --finish`. Do not edit by hand.

Protocol: `docs/Q053-MECHANISM-PREREGISTRATION.md` (frozen 2026-11-08). Mechanism: second-competing retention floor, implemented **in process** in `benchmarks/q053_mechanism_run.py`; no engine file changed.

**Verdict: `MECHANISM DID NOT OPERATE`**

| Criterion | Result |
| --- | --- |
| M1 mechanism (late competition share, median gap, bar 0.25) | 0.0 |
| C1 capability (late recall@5, median gap, bar None) | unread: M1 failed |
| C1 interval | unread |
| C1 positive seeds | unread of 10 |
| C2 early cost (median gap, bound -0.01) | unread |

| Seed | Arm | Early recall@5 | Late recall@5 | Late competition | Late theory-zero |
| --- | --- | --- | --- | --- | --- |
| 20410101 | control | 0.9062 | 0.9078 | 0.00 | 1.00 |
| 20410101 | treatment | 0.9062 | 0.9078 | 0.00 | 1.00 |
| 20410102 | control | 0.9000 | 0.8962 | 0.00 | 1.00 |
| 20410102 | treatment | 0.9000 | 0.8962 | 0.00 | 1.00 |
| 20410103 | control | 0.9038 | 0.9036 | 0.00 | 1.00 |
| 20410103 | treatment | 0.9038 | 0.9036 | 0.00 | 1.00 |
| 20410104 | control | 0.9087 | 0.9153 | 0.00 | 1.00 |
| 20410104 | treatment | 0.9087 | 0.9153 | 0.00 | 1.00 |
| 20410105 | control | 0.9213 | 0.9110 | 0.00 | 1.00 |
| 20410105 | treatment | 0.9213 | 0.9110 | 0.00 | 1.00 |
| 20410106 | control | 0.9038 | 0.9036 | 0.00 | 1.00 |
| 20410106 | treatment | 0.9038 | 0.9036 | 0.00 | 1.00 |
| 20410107 | control | 0.9062 | 0.9036 | 0.00 | 1.00 |
| 20410107 | treatment | 0.9062 | 0.9036 | 0.00 | 1.00 |
| 20410108 | control | 0.9000 | 0.8962 | 0.00 | 1.00 |
| 20410108 | treatment | 0.9000 | 0.8962 | 0.00 | 1.00 |
| 20410109 | control | 0.9038 | 0.9025 | 0.00 | 1.00 |
| 20410109 | treatment | 0.9038 | 0.9025 | 0.00 | 1.00 |
| 20410110 | control | 0.8962 | 0.8951 | 0.00 | 1.00 |
| 20410110 | treatment | 0.8962 | 0.8951 | 0.00 | 1.00 |

The control's late theory-zero share is the liveness gate: a control that survives would compare two live arms and void the block.

**Scope.** One world family, one mechanism, one block. The verdict licenses no adoption; adoption is a separate owner decision. The mechanism changes retention only, and the raw/asserted distinction is not at issue here.

## Status reconciliation

The preregistration page says **FROZEN, NOT RUN** because that was its state at freeze on 2026-11-08, and a frozen protocol is amended rather than rewritten. The block ran on 2026-11-09 under the owner decision recorded in the manual (action row 110). The mechanism was implemented **in process only** in `benchmarks/q053_mechanism_run.py`; no engine file changed.

## Why the gate failed, and what it does not mean

The floor retained only hypotheses that formation proposed in the same cycle. Across the late windows no subject presented two competing beliefs, so the floor had nothing to exempt: M1 is exactly 0.00 on every seed. Per the frozen decision table the capability endpoint is **unread**: this is a manipulation-check failure, not a null capability result, and not evidence that preservation cannot help. The loss the preregistration targets happens after formation stops proposing the second expectation, in the prior-decay path, which this block does not touch. A retry needs a new preregistration that acts there; this block may not grow into one.
