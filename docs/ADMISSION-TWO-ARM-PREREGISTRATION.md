# The adopted admission rule against the reference engine (2026-11-07)

**This block has run: the frozen analysis path returned NO GAIN ON THIS LAYER.** §9 records the result and §10 the withdrawal, and §1–§7 are preserved exactly as committed before the run.

**Status: FROZEN, NOT RUN (ready; no cell).** No arm has run on this registration. The bar, the
guard, the seeds, the endpoint and the decision table were committed before the first cell.

**Every figure this block produces carries its arm.** The arms are `organica.sleep.SleepService` (the frozen engine's own builder: transition probability inside a stratified transition/co-occurrence quota, with a schema prior) and
`organica.admission.DiversityFirstSleepService` (the adopted order: fewest already-admitted outgoing edges per source, ties on count then stable key, over the eligible pool). A number quoted from this block without its arm is not a number from
this block.

## 1. Question and endpoint

does the adopted diversity-first admission produce higher asserted world-edge coverage than the reference engine on the same real world, at the same budget and the same number of cycles?

The endpoint is `asserted_coverage from gate_acquisition_sufficiency: the fraction of the world's compositional edges present in the arm's asserted structure (structure_edges over the surviving candidates)`. It is coverage, not behaviour: it counts which world edges the
arm's asserted structure contains, and says nothing about prediction, revision or retention.

## 2. Design

120 cycles of the Gate 13 compositional world, identical for both arms of a seed; the only
difference is the service class. 16 cells — 2 arms x 8 seeds = 16 cells. Seeds **20320101–20320108**,
bootstrap **20320109**: the first contiguous window of nine integers at or above 20320101 that appears in no file under docs, tests, benchmarks, research-journal or papers; the ninth is the bootstrap seed and is not a world seed

## 3. The bar and the guard

**Gain bar 0.08.** carried as policy from the confirmatory block: one half of the order block's measured mean delta, 0.1615, floored to two decimals. It is NOT calibrated on this layer and this block is not a replication of that figure -- the comparison here is a different pair of orderings on a different instrument, and a pass means only that the adopted arm cleared a bar fixed before this run

**Precision guard -0.05.** declared, not calibrated: 0.05 is the smallest difference this project's instruments have been asked to distinguish

The gain is a conjunction judged whole: the mean paired coverage difference at or above the bar,
its 95% interval's lower bound above zero, and at least 7 of 8 seeds with
a positive difference. The guard can only prevent a gain being claimed.

## 4. Decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
| gates pass; gain passes; guard passes | **ADOPTED ARM GAINS** | the adopted admission covers more of the world's edges than the reference engine on this world, at the same budget, without losing precision |
| gates pass; gain passes; guard fails | **PRICED TRADE** | coverage rises and precision falls; the trade is recorded and nothing is claimed as a gain |
| gates pass; gain fails; interval width at or below 0.30 | **NO GAIN ON THIS LAYER** | the adopted rule does not cover more of the world here; the earlier pooled-table gain does not transfer, and this layer is closed to this rule |
| gates pass; gain fails; interval width above 0.30 | **UNDERPOWERED** | the interval cannot place the difference; absence of a gain is not established |
| a gate fails | **VOID** | reported as the gate, never as a verdict |

## 5. Gates

* **G0 liveness** — the two arms' asserted fingerprints must differ on at least seven of eight seeds, or the manipulation did not occur
* **G1 world present** — raw temporal coverage must be 1.0 in both arms of every seed, or the cell tests memory rather than admission
* **G2 arithmetic** — covered cannot exceed asserted, and coverage and precision must equal covered over their denominators
* **G3 determinism** — the reference arm re-run on the first seed must produce the same asserted fingerprint
* **G4 denominator** — the world must have at least one compositional edge in every seed
* **G5 boundary** — no frozen engine file may differ from HEAD when the block runs

**Void rule.** a failed gate voids the block and no criterion is read; a cell set that is not the pre-registered grid is refused

## 6. Analysis

`./.venv/bin/python -m benchmarks.score_admission_two_arm --results docs/admission_two_arm_run.json --out docs/admission_two_arm_result.json`

The analysis path is `benchmarks/score_admission_two_arm.py`, frozen with this registration. It reads only the cells the
runner writes, validates the grid, and imports nothing from the engine. The runner is `./.venv/bin/python -m benchmarks.run_admission_two_arm --run`.

## 7. Allocation

8 world seeds, 1 bootstrap seed, 16 cells, 2
thresholds, 2 bars. two thresholds are fixed here: the gain bar and the precision guard

No arm may run before this file is committed.

## 9. Result (post-freeze)

**NO GAIN ON THIS LAYER.** The adopted rule does not cover more of the world here; this layer is closed to this rule

- **Cells:** 16, all gates passed.
- **Coverage gain, adopted minus reference:** mean -0.077009, 95% interval
  [-0.099331, -0.056920], width 0.042411, bar 0.08, 0 of 8 seeds positive.
- **Precision guard:** mean -0.096528 against -0.05 — failed.

| Seed | Coverage gain (adopted − reference) | Precision difference |
| --- | --- | --- |
| 20320101 | -0.044643 | -0.065559 |
| 20320102 | -0.116072 | -0.124310 |
| 20320103 | -0.044643 | -0.086571 |
| 20320104 | -0.133929 | -0.120615 |
| 20320105 | -0.089286 | -0.134615 |
| 20320106 | -0.062500 | -0.106831 |
| 20320107 | -0.062500 | -0.050258 |
| 20320108 | -0.062500 | -0.083464 |

Every figure above is the paired difference between the two arms, and the arm order is fixed:
positive means the adopted arm covered more. Cells are in
`docs/admission_two_arm_run.json`; the decision is in `docs/admission_two_arm_result.json`.
The registration itself is unchanged: §1–§7 are exactly as committed before the run.

## 10. Withdrawal (post-freeze)

**WITHDRAWN on 2026-11-07.** The adoption this block was registered to test was removed the day
the result was read: the reference engine (`organica.sleep.SleepService`) is again the only admission path in the package.

**Removed from the package:**

- `organica/admission.py`
- `tests/test_admission_rule.py`

**Why the code and not only the record.** A rule its own measurement closed is not a policy an
engine version should carry, and a non-default arm that no document may present as a gain is a
liability that still has to be maintained. Deleting it is the version of this negative result the
code agrees with. §9 and the decision table above are unchanged: the result, the bar and the guard
keep their numbers, and the confirmatory block's verdict keeps its own instrument.

**Reproducibility.** The adopted arm was last present at commit **a82e890**. Checking that
commit out reproduces this block end to end; `benchmarks/run_admission_two_arm.py` resolves its
arms lazily and stops with that commit's name rather than raising an `ImportError`.

**Not a wider finding.** The withdrawal closes the admission question on the engine's prediction layer, in one world family and at one horizon; it does not establish that diversity-first ordering is wrong anywhere else, and the pooled-table gain is neither retracted nor revived.
