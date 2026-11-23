# Formation provenance — study report

**Generated from [`docs/formation_provenance_study.json`](formation_provenance_study.json);
do not edit by hand.** Regenerate with `python -m benchmarks.formation_provenance_study --report`.

Seeds: 20270106–20270120 (15), run once under
[`docs/FORMATION-PROVENANCE-PREREGISTRATION.md`](FORMATION-PROVENANCE-PREREGISTRATION.md).

## Endpoint

| arm | hits | n | rate |
|---|---|---|---|
| `pair_world_attributed` | 1938 | 4280 | 0.4528 |
| `origin_includes_self` | 2036 | 8528 | 0.2387 |

Difference: **0.214061** with a 98.33 % interval [0.195886, 0.228119], lower bound must be above zero.

Permutation control: difference 0.000359, interval [-0.016244, 0.016023], includes zero: **True**.

Excluded as `pair_unattributed` (never merged): **0**.

## Gates

- G1_liveness: **True**
- G2_denominators: **True**
- G3_permutation_includes_zero: **True**
- G4_instrument_neutrality: **True**

Verdict: **association detected**.

## What this means, and what it does not

It means, among the candidates this engine formed on these worlds, the recorded
provenance of a prediction's pair is associated with whether that pair occurs in a
window the organism was never shown. It does **not** mean that the knowledge is useful
or reusable, that the closed study's transfer failed, that the content originated in
the world, or anything about observation-level causation.
