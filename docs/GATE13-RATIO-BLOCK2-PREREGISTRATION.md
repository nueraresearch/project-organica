**Status: RUN (2026-11-06). Verdict: TREATMENT NOT REPRODUCED.** All 275 cells completed on 20270901-20270925, criteria as frozen in §4 and scored
once. C0, C1′ and C2 pass; **C3 fails at 20 of 25** against the pre-registered 21-of-25 bar; C4 passes on its
thresholds. This is the first block whose control passes C1′. Readings in §11; artifact `docs/gate13_ratio_block2.json`.

**Status: PRE-REGISTERED, NOT RUN (2026-11-06).** Written out before the first cell of this block. Block 1 and the
calibration sweep are complete; nothing below was chosen after seeing any cell of 20270901–20270925.

## 1. What this block tests, and why it is a new block

Block 1 (`docs/GATE13-RATIO-CONFIRMATORY-PREREGISTRATION.md`) ran 275 cells and returned
**PARTIAL / NOT COMPARABLE**: the treatment contrast reproduced (C2 24/25, C3 24/25 at
exact one-sided p = 7.7e-07, C4 median +0.0128 and worst -0.0084) but C1
failed. A 200-seed diagnostic sweep then showed why: C1's per-seed ±0.05 band covers 81.5% of seeds, so its 21-of-25 bar
passed only 49.7% of the time on a population matching the reference. C1 was re-specified as C1′ (Amendment 1, §13 of
that document) with its power computed in advance.

This block is therefore the **first** test of the admission rule under a comparability criterion that can do its job, on
seeds that no block, sweep or artifact has touched. It is decided once, by §4, and the result is **decisive for the
admission-rule hypothesis** whether it succeeds or fails (the owner's authorisation, 2026-11-06).

## 2. Allocation

**Seeds 20270901–20270925** (25 discrete seeds). Scan run before this document was written: 6587 files across the tree
(`.git`, `.venv`, `node_modules`, caches excluded), **zero occurrences** of any of the 25 values. Every previously used
range is excluded by construction: 20261101–20261105 (development), 20261106–20261130 (reserved by the acquisition study),
20270602–20270626 (block 1, spent), 20270701–20270900 (calibration sweep, spent as calibration).

## 3. Arms, caps, cells

Unchanged from block 1: 275 cells = 11 per seed × 25 seeds.

| arm | what it is | caps |
|---|---|---|
| C | count-sorted admission, `PairedDiagnosticSleepService` — the registered control | 10, 20, 100, 1000 |
| R | the same construction and cap, sorted by `count / max(source_freq, 1)` — the registered treatment | 10, 20, 100, 1000 |
| E | the engine's own `_build_predictions` at the same cap — reference only, never scored | 20, 100, 1000 |

Harness: `benchmarks/run_ratio_admission_arm.py` exactly as block 1 ran it, `PYTHONHASHSEED=0`, scratch DBs only, no engine
file touched (`tests/test_v1_freeze.py` enforces that). No harness change is made for this block: `--block` and `--jsonl`
predate block 1's first cell and are disclosed in its §11. Raw cells accumulate in `.scratch/ratio_block2.jsonl`.

## 4. Criteria, frozen here, evaluated once

| id | criterion | pass condition |
|---|---|---|
| C0 | liveness — the arms actually differ | asserted-set digest differs at cap 20 on ≥ 21 of 25 seeds; cap-1,000 coincidence is expected by construction (both arms reach the full pool) and is reported, not required to differ |
| **C1′** | **comparability — the control behaves like the calibrated population** | mean cap-20 C precision over the 25 seeds lies within δ = 0.032 of 0.4667, i.e. in [0.4347, 0.4987]. δ and the band are frozen from the 200-seed sweep (20270701–20270900), which this block does not overlap; power 0.908 on a matching population |
| C2 | tie broken | R's distinct score values ≥ 3 × C's at cap 20 on ≥ 21 of 25 seeds |
| C3 | directional hypothesis | R's asserted coverage > C's at cap 20 on ≥ 21 of 25 seeds (exact one-sided sign test; that bar is p ≤ 0.00046 at n = 25) |
| C4 | precision not bought with coverage | median paired precision delta (R − C at cap 20) ≥ −0.02, minimum ≥ −0.05, and every size-matched delta ≥ −0.02 where a bracket exists |

Reported but **not** criteria: per-cap coverage and precision for C and R, the E arm, marginal precision from cap 20 to
1,000, pool diagnostics (rows, world edges, base rate, distinct values, tie share).

## 5. Decision rule

| C0 | C1′ | C2 | C3 | C4 | verdict |
|---|---|---|---|---|---|
| fail | any | any | any | any | **INVALID** — the instrument failed; nothing is concluded about the rule |
| pass | fail low | any | any | any | **NOT COMPARABLE** — control sits below the calibrated population by more than δ |
| pass | fail high | any | any | any | **NOT COMPARABLE** — control flattered above the calibrated population by more than δ |
| pass | pass | pass | pass | pass | **CONFIRMED** — the ratio rule reproduces under a calibrated control |
| pass | pass | fail | any | any | **TIE NOT BROKEN** — the rule's discriminator is absent |
| pass | pass | pass | fail | any | **TREATMENT NOT REPRODUCED** — block 1's C3 does not replicate |
| pass | pass | pass | pass | fail | **COVERAGE GAIN AT PRECISION COST** |

## 6. Predictions, recorded before the run

From block 1 and the calibration sweep, not from this block:

- **C1′ passes** with probability ≈ 0.908 on the calibration population; the sweep's mean is 0.4449
  (95% CI 0.4397–0.4500), inside the band.
- **C3** 20–25 of 25, median delta between +0.03 and +0.06 (block 1: 24/25, +0.0446).
- **C2** 22–25 of 25 at ≥ 3× (block 1: 24/25, tightest 2.83×).
- **C4** passes with a median delta near +0.01 and a worst case above −0.02 (block 1: +0.0128 /
  -0.0084).

If C1′ fails, the prediction above is the thing that was wrong, and it will be reported as such.

## 7. Failure modes, and what each would mean

- Identical digests at caps 10 and 20 → **INVALID**: the treatment arm did not vary, a harness defect, not a result.
- Cap-1,000 coverage below 1.0000 on either arm → the pool was not fully reached; reported beside every verdict.
- C1′ fail-low → on these 25 worlds the count control is worse than the calibrated population by more than 0.032. Under
  §8.8 that is ≈ 1.4 se beyond a mismatch the criterion already tolerates, so it would be a real difference in the
  control's behaviour, not the old band's sampling error.
- C1′ fail-high → the control is *flattered* relative to the calibration population; a treatment advantage would then be
  partly the baseline's, and the block cannot support a ratio claim.
- C2 fails but C3 passes → the coverage gain is not coming from tie-breaking; the mechanism is unestablished.

## 8. Cost

275 cells at ≈ 7.3 s each ≈ 33 minutes, run in resumable chunks; JSONL per cell, so an interrupted chunk loses at most
the cell in flight.

## 9. What this block does not settle

One world family (2-tag compositional, 300 cycles), one engine build, caps up to 1,000, and this candidate population.
It tests *applying* the stored ratio, not choosing it among the six orderings §8.5 screened. Nothing here licenses an
engine change: a CONFIRMED verdict permits a recorded decision, not a modification of a frozen primitive.

## 10. Provenance and integrity

- Harness: `benchmarks/run_ratio_admission_arm.py` (unchanged); cells: `.scratch/ratio_block2.jsonl`;
  results artifact: `docs/gate13_ratio_block2.json`; calibration: `docs/gate13_c1_respecification.json`.
- The criteria in §4 are evaluated once, by code, in the order C0 → C1′ → C2 → C3 → C4. No criterion will be re-specified,
  relaxed or re-scored after the numbers are seen; a defect found afterwards is recorded as an amendment governing a
  *later* block, as Amendment 1 did.
- δ and the band are inputs to this document, not outputs of it.

## 11. Readings (2026-11-06)

All 275 cells completed, no failed seed, no substitution, criteria evaluated once in the order C0 → C1′ → C2 → C3 → C4.

| id | result | detail |
|---|---|---|
| C0 | **pass** | digests differ on 25/25 seeds at cap 20, and on 25 and 25 at caps 10 and 100; cap 1,000 coincides by construction |
| C1′ | **pass** | mean cap-20 C precision 0.4530, offset -0.0137 from 0.4667, inside [0.4347, 0.4987] |
| C2 | **pass** | 22/25 at ≥ 3×, tightest 2.73× |
| C3 | **FAIL** | 20/25, exact one-sided p = 0.002, median Δ +0.0535 |
| C4 | **pass** | median Δ +0.0003, worst -0.0292, 12/25 falling, 5 size-matched |

**Why C3 failed.** 5 seeds did not improve: 20270901 (Δ +0.0000); 20270905 (Δ -0.0089); 20270908 (Δ -0.0179); 20270913 (Δ +0.0000); 20270921 (Δ -0.0446). The bar was 21 of 25 (p ≤ 0.00046 at n = 25) and the
block returned 20, so the directional hypothesis as pre-registered is not supported on this allocation. It is not
re-read: the effect remains positive on 20 seeds and nominally significant at p = 0.002, and that is
reported beside the failure rather than in place of it.

**Disclosure required by §7.** Cap-1,000 coverage is 1.0000 on 21/25 seeds for C and 21/25 for R; the rest fall short of the
full pool: 20270901 (C 0.9911, R 0.9911); 20270903 (C 0.9911, R 0.9911); 20270907 (C 0.9911, R 0.9911); 20270920 (C 0.9911, R 0.9911). No criterion reads cap 1,000, and the cap-20 criteria are unaffected, but the shortfall is recorded rather
than rounded away.

**Effect size, beside block 1.** Median coverage delta +0.0535 here against +0.0446 in block 1, on 20 of 25 seeds
versus 24. The precision guard passes on its thresholds but its median has collapsed to +0.0003 (block 1:
+0.0128), with 12 of 25 seeds losing precision. C2 still passes: the discriminator exists, which locates the failure
in the size and stability of its benefit rather than in its presence.

**Verdict, as the frozen table returns it.** C1′ passes and C3 fails → **TREATMENT NOT REPRODUCED**. Under the owner's authorisation of
2026-11-06 this is decisive for the admission-rule hypothesis on this world family, and no criterion is re-specified for this
block.
