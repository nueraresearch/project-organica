# Cross-Context Reuse Experiment — earned-evidence run

**Generated from** `docs/cross_context_reuse_benchmark_earned.json` and `docs/cross_context_reuse_priming_provenance.json` (this run), and `docs/cross_context_reuse_benchmark.json` (v1, superseded). **Protocol**: earned-evidence (docs/DECISION-EARNED-SCHEMA-PRIMING.md).
**Seeds**: [20261101, 20261102, 20261103, 20261104, 20261105] at 40/40 cycles; 477.61 s across 5 processes.

## 1. Verdict

`STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE`

Acquisition is flat across all four arms: treatment 3.6, naïve 3.4, pruned 3.4, orthogonal 3.4 cycles → TR 0.944 / 1.0 / 1.0. No arm is faster than a naïve organism at this endpoint, and the treatment arm is marginally slower.

**The priming is not inert.** The single-seed provenance probe separates priming applied by the pre-B schema from priming applied by Context B's own emerging schema: treatment 162 vs 270, orthogonal 92 vs 317 (`schema_prior` applications). Both arms acquire at cycle 4 and 4 respectively, so the prior crosses the vocabulary boundary and buys no latency.

## 2. Per-seed results

Cells are `cycles_to_acquire / persistence_cycles / primed_predictions`.

| seed | treatment | naïve | pruned | orthogonal |
|---|---|---|---|---|
| 20261101 | 4 / 29 / 432 | 4 / 28 / 299 | 4 / 30 / 618 | 4 / 32 / 409 |
| 20261102 | 4 / 27 / 423 | 4 / 31 / 338 | 4 / 28 / 549 | 4 / 29 / 340 |
| 20261103 | 2 / 29 / 514 | 2 / 37 / 382 | 2 / 28 / 442 | 2 / 28 / 422 |
| 20261104 | 4 / 25 / 468 | 4 / 26 / 119 | 4 / 26 / 471 | 4 / 27 / 392 |
| 20261105 | 4 / 31 / 461 | 3 / 29 / 374 | 3 / 33 / 718 | 3 / 33 / 480 |

## 3. What changed from the v1 run

| quantity | v1 (`7becdb5`) | earned-evidence |
|---|---|---|
| treatment acquisition | 1.0 | 3.6 |
| naïve acquisition | 3.2 | 3.4 |
| pruned acquisition | 3.2 | 3.4 |
| orthogonal acquisition | 1.4 | 3.4 |
| TR treatment | 3.2 | 0.944 |
| TR orthogonal | 2.286 | 1.0 |
| verdict | `REUSE_DEMONSTRATED` | `STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE` |

The v1 advantage came from raising a one-transition edge past `PREDICTION_MIN_COUNT` with a confidence-derived boost keyed only on the existence of a schema (decision D1). Removing that substitution flattens acquisition in every arm. The v1 run also could not attribute its result to Context A: its schema id depended on the role names alone, so Context A and the orthogonal Context C produced the *same* schema identity and the two arms matched on four of five seeds, persistence included. Schema identity is now content-bearing (D3), and the probe above shows the two contexts' schemas are distinct and separately countable.

## 4. What this establishes, and what it does not

**Established.** (a) Scored on unboosted evidence, a consolidated schema confers no acquisition advantage in this world family — neither Context A's nor Context C's. (b) The prior is applied, so the flat result is a measurement rather than an unrun manipulation (rules 13a, 25c). (c) The congruence gate can admit and reject, and schema identity distinguishes contexts (`tests/test_relational_schema_layer.py`).

**Not established.** (a) That a rank-sensitive endpoint would show nothing: the prior reorders candidates, and the target edge's rank at acquisition was [7, 5, 4, 20, 7] in treatment, but the acquisition endpoint does not reward ranking. (b) Any retention claim: at the time of this run the prior reader returned every historical copy, so a decayed schema never superseded its own earlier version; that defect was measured and fixed afterwards (docs/DECISION-CANDIDATE-SUPERSESSION.md), and this run has not been repeated on the corrected reader. (c) Any statistical claim: n = 5, no p-value; the preregistered `TR > 1.25` at `p < 0.01` over 10 seeds is not met and is not claimed. (d) That the pruned arm isolates `S_A` — it deletes the entire candidate layer and the temporal graph.

