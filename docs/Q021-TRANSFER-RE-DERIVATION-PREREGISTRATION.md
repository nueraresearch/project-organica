# Q021 transfer re-derivation: the v1 TR = 3.2 claim on 0.13.0

**Status: FROZEN, NOT RUN.** No cell of this protocol has run. The engine is unchanged; this is a
re-derivation of an existing claim, not a repair and not a new mechanism.

**Question.** Can a transfer claim rest on the v1 `TR = 3.2` result?

**What is already in the record.** The v1 run (`docs/cross_context_reuse_benchmark.json`) reported
treatment 1.0 cycle against naïve 3.2, `TR = 3.2`, and `REUSE_DEMONSTRATED`. That verdict was
withdrawn: its advantage came from a confidence-derived boost that lifted a one-transition edge
past `PREDICTION_MIN_COUNT` (`docs/DECISION-EARNED-SCHEMA-PRIMING.md`, D1), and its schema identity
was not content-bearing (D3). The earned-evidence rerun measured treatment 3.6, naïve 3.4,
`TR = 0.944`, and returned `STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE`
(`docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md`). Neither artifact records an `engine_version` in
the form the pinned registry audit requires, so neither settles the claim on 0.13.0.

The missing measurement is not another mechanism. It is the same four-arm design, run on the
pinned engine with the earned-evidence rule already implemented in the harness.

## 1. Design

The harness is `benchmarks/cross_context_reuse_benchmark.py`. Its acquisition rule already
requires `temporal_count >= PREDICTION_MIN_COUNT` on the prediction itself and refuses an
`effective_count` different from the observed count, so the v1 substitution cannot silently
return.

| Arm | Context A | Context B | What it isolates |
| --- | --- | --- | --- |
| `treatment` | structured A | B | the prior formed in A |
| `control_naive` | none | B | acquisition without any prior |
| `control_pruned` | A, candidate layer and temporal graph excised | B | the prior's causal contribution |
| `control_orthogonal` | flat Context C | B | whether any prior helps, not this one |

Contexts use the harness's disjoint four-letter vocabularies. Phase A is 40 cycles; Phase B is
40 cycles. The four arms of a seed see the same seed-determined worlds; only the arm differs.

| Field | Value |
| --- | --- |
| world seeds | 20262101, 20262102, 20262103, 20262104, 20262105, 20262106, 20262107, 20262108, 20262109, 20262110 |
| bootstrap seed | 20262111 |
| cells | 40 (4 arms x 10 seeds = 40 cells) |
| cycles per cell | 80 (40 Context A + 40 Context B) |
| seed freshness | the first contiguous block of eleven integers at or above 20262101 that appears in no artifact, harness, test, document or journal in the repository; the eleventh is the bootstrap seed and is not a world seed |

The harness takes `--seed_offset 1000`, which maps its base 20261101 to 20262101. The run command
is:

```bash
./.venv/bin/python -m benchmarks.cross_context_reuse_benchmark \
  --seeds 10 --seed_offset 1000 \
  --phase_a_cycles 40 --phase_b_cycles 40 \
  --out_path docs/q021_transfer_rederivation.json
```

No cell may run before this file is committed. The block was checked against the repository when
this record was frozen; if a later artifact collides with it, the collision is disclosed and the
block is re-frozen before any cell — no seed is substituted silently.

## 2. Endpoints

- **TR, the primary endpoint.** `mean cycles_to_acquire(control_naive) / mean
  cycles_to_acquire(arm)`, exactly the harness's own metric. The v1 run reported 3.2; the earned
  run reported 0.944.
- **Paired acquisition difference.** Per seed, `cycles_to_acquire(control_naive) -
  cycles_to_acquire(treatment)`; positive means treatment was faster.
- **TR against both controls.** The same ratio computed for `control_pruned` and
  `control_orthogonal`, so the prior's content is separated from the existence of a prior.
- **TP.** The harness's `persistence_cycles`, the number of Context B cycles after acquisition in
  which the target remains admitted (cumulative, not necessarily consecutive). This is observed
  persistence, not provenance; Q021 does not test Q028's trace.

## 3. Criteria, judged whole

All intervals are 95% paired bootstrap intervals over seeds, 10,000 resamples, bootstrap seed
20262111, fixed before the run.

| Criterion | Quantity | Rule | Bar | Provenance |
| --- | --- | --- | --- | --- |
| T1_transfer | `TR(treatment)` | point estimate at or above the bar, and the bootstrap lower bound above 1.00 | 1.25 | the v1 protocol's own bar, carried unchanged (`docs/CROSS-CONTEXT-REUSE-PREREGISTRATION.md` §5); this is a re-derivation, so the bar is not recalibrated |
| T2_attribution | `TR(treatment)` minus `TR(control_pruned)` and `TR(control_orthogonal)` | both differences at or above the bar, with lower bounds above zero | 0.10 | declared, not calibrated: the earned run gives no positive effect to calibrate from, and the bar is the smallest gap this instrument has been asked to separate |
| T3_paired | per-seed acquisition difference | treatment strictly faster than naïve on at least 8 of 10 seeds | 8 of 10 | declared before the run; a mean advantage carried by one seed is not a transfer result |
| T4_persistence | mean `TP(treatment)` | at or above the bar | 20 cycles | v1's R5 persistence threshold, carried unchanged; it is a guard, not a transfer claim |

**The criteria are not a score.** If T1 passes but T2 fails, the result is a prior effect, not a
transfer result. If T1 fails with an interval width at or below 0.30, the v1 claim is not
re-derived; if the width is above 0.30, the block is underpowered and says so.

## 4. Gates, which void the block before any criterion is read

| Gate | Requirement |
| --- | --- |
| G1_denominator | every one of the 40 cells must acquire within 40 Context B cycles; a censored cell has no acquisition denominator and the block is void, not scored as a zero |
| G2_seed_block | the cells must be exactly the frozen 40, ten seeds and four arms, with no seed outside the block and no substitution |
| G3_earned_evidence | the harness must complete without an `unaudited count` assertion on every cell; a raised assertion is a void block, not a measurement |
| G4_engine | the run artifact must be stamped with the pinned engine's version and SHA-256; a different engine is a different experiment |
| G5_no_engine_change | no file under `organica/` may differ from the pin when the block runs |

Void rule: a failed gate voids the block and no criterion is read. A missing cell is not a
negative result.

## 5. Decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
| any gate fails | `VOID` | the block is unrun; the failed gate names what did not happen |
| gates pass; T1, T2, T3 and T4 pass | `TRANSFER_CLAIM_RE_DERIVED` | on 0.13.0, under earned evidence, the treatment clears the v1 bar and both attribution controls; the v1 number may be cited only with this block's arm, seed block and engine |
| gates pass; T1 passes; T2 fails | `NOT_ATTRIBUTABLE` | an advantage exists but is not the prior's content; no transfer claim |
| gates pass; T1 fails; interval width at or below 0.30 | `NO_TRANSFER_ADVANTAGE` | the v1 3.2 claim does not re-derive; the earned run's null is reproduced on the pinned engine |
| gates pass; T1 fails; interval width above 0.30 | `UNDERPOWERED` | the block cannot place the effect; absence of an advantage is not established |
| gates pass; T1 passes; T2 passes; T3 or T4 fails | `PARTIAL` | the headline ratio passes but the paired or persistence guard fails; the block is recorded and no transfer claim is licensed |

## 6. Prediction, stated before the run

The earned run predicts `T1` fails and `TR(treatment)` lands near 1.0, because the v1 advantage
was the schema-derived admission boost and the harness now refuses it. That is a prediction, not
a criterion: a re-derived 3.2 that also clears T2, T3 and T4 would be a genuine reversal of the
earned result, and this record must be able to report it.

## 7. What this block does not claim

- It does not test Q028's provenance, Q012's role abstraction, or any cross-domain transfer.
- It does not make the prior useful; a null re-derivation closes the v1 claim on this engine, not
  transfer in general.
- It does not establish a rank effect; the harness's acquisition endpoint ignores rank.
- It does not change the engine or adopt a mechanism.

## 8. Stop condition

One design, four arms, ten fresh seeds, one analysis. The record may be fixed if it is found
wrong; it may not grow into a second endpoint, a role trace, a different world family or an
additional seed block without a new preregistration. No criterion, bar, seed or arm may change
after the first cell.
