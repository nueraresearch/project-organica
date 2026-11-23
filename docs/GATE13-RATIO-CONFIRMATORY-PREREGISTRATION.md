**Status: AUTHORISED AND RUN (2026-11-06) on allocation B (20270602–20270626). Verdict: PARTIAL / NOT COMPARABLE.**
All 275 cells completed. C0, C2, C3 and C4 pass; C1 fails — the count-sorted control is below the
frozen chance baseline on 22 of 25 seeds — so the frozen table's last row applies and the block is
reported as not comparable rather than as a confirmation. Readings: §8.7 of
`docs/GATE13-PAIRED-CAPACITY-TEST.md`, artifact `docs/gate13_ratio_confirm.json`. A prospective re-specification of C1 (C1′), with its power computed in advance from the 200-seed
sweep, is recorded as Amendment 1 in §13; it does not apply to this block.

## 1. What is being confirmed

The development block (`docs/GATE13-RATIO-ADMISSION-PREREGISTRATION.md`; §8.6 of
`docs/GATE13-PAIRED-CAPACITY-TEST.md`) ran 55 cells on five seeds that had been visible throughout
this record. All four predictions passed: at cap 20 the stored-`ratio` ordering beat the count-sorted
control's coverage on every seed, by 0.0536 to 0.0804, while paired precision moved by
-0.0031 to 0.0313, and the score tie collapsed from
0.7833–0.8625 of the pool to
0.1083–0.1375.

Those five seeds were used to *design* the arm, so a reader cannot separate an arm effect from a property of
those worlds. This block asks the harder question — does the same contrast hold on seeds that took no part in
the arm's design? It cannot re-score the development block, and the development block cannot rescue this one:
the readings here stand whatever they say.

## 2. Seeds — the requested range, the collision it contains, and a verified alternative

The requested range is **20261106–20261130**, 25 seeds. It is not fresh in the sense of being unnamed. A scan
of 440 files under `docs/`, `benchmarks/`, `tests/`, `organica/` plus `CHANGELOG.md` and `AGENTS.md`
found **25 of 25 seeds already named** in **63 files**
(21 JSON artifacts, 30 documents, 12 source files). Three things follow, and
none of them is a reason to quietly pick a different range.

1. **No file scores this comparison on these seeds, and 17 of them report asserted coverage itself.** They
   report acquisition log-loss, use-path audits, divergence evidence and formation utilization on the same
   seed integers, and several report asserted coverage under *other* arms and tasks. No artifact reports the
   count-versus-ratio ordering on 20261106–20261130, so the range carries no information about *this*
   comparison — but it is not seed-blind to the endpoint, and the block must not claim to be.
2. **The range is reserved to another study.** `docs/FACTS-SHEET.md` AC10 records that the confirmatory sample
   shrank from 30 to 25 because Amendment 3 designated `20261101`–`20261105` as diagnostic, which makes
   **20261106–20261130 the acquisition experiment's confirmatory sample**. Running this block on it spends
   that reservation, and a reservation spent by an unplanned consumer cannot be restored.
3. **The label has to match the allocation.** On this range the block is *confirmatory on seeds that were
   visible in other studies but never scored on this endpoint* — which is what matters for leakage, and is
   weaker than "unseen seeds". That sentence is what a pass may claim, not the stronger one.

| allocation | seeds | occurrences in this tree | what a pass may claim |
|---|---|---|---|
| **A — the requested range** | 20261106–20261130 | 25 of 25 named in 63 files | confirmatory on seeds reserved elsewhere, on which this arm's comparison was never scored; spends the acquisition study's reservation |
| **B — a verified-empty block** | 20270602–20270626 | 0 in 440 files scanned | confirmatory on seeds named nowhere in this tree; leaves the acquisition reservation intact |

Allocation **B** is pre-registered as the default recommendation because it costs the same 275 cells and
weakens no claim. Allocation **A** is what was requested and remains available on the owner's ruling. The
choice is a decision, not a default: amending this document after a block runs is not permitted, and mixing
the two allocations is not permitted.

**Failure rule, fixed now:** a cell that fails technically is reported failed and its seed is not replaced;
more than two failed seeds in any arm makes the block **void**, not negative.

## 3. The arms, exactly as run

| arm | admission ordering | caps | seeds | cells |
|---|---|---|---|---|
| **C** (control) | `temporal_count`, the harness rule | 10 / 20 / 100 / 1,000 | 25 | 100 |
| **R** (treatment) | `ratio = count / max(source_freq, 1)`, tiebreak `-ratio, -count, source, target` | 10 / 20 / 100 / 1,000 | 25 | 100 |
| **E** (reference) | the engine's `_build_predictions` at the same budget | 20 / 100 / 1,000 | 25 | 75 |
| | | | **total** | **275** |

`benchmarks/run_ratio_admission_arm.py` in its 2026-11-06 state, `PYTHONHASHSEED=0` in all three arms, no edit
to any frozen file. **Any change to the harness, the caps, the metrics or the predictions requires a new
pre-registration.** The development block already lost seven cells to a treatment subclass that reproduced the
control exactly; a confirmatory block that repaired its own instrument after seeing a result would repeat that
defect at five times the scale. Cap 10 exists only for C4's size-matched comparison and carries no prediction.

## 4. Metrics — unchanged, and the comparator is frozen

M1–M5 as frozen in the development pre-registration §3. The chance comparator is **0.4667, taken from the
development pool and not recomputed here** — a threshold derived from the data it judges is not a threshold.

## 5. Predictions, frozen before the run

- **C0 — liveness (a control the harness can fail).** R's asserted set must differ from C's on ≥ 21 of 25
  seeds, and coverage at cap 1,000 must reach **1.0000** on every seed in both arms. If either fails the
  instrument is dead or the world changed: **void**, not negative.
- **C1 — the control is still at chance.** |M2(C) − 0.4667| ≤ 0.05 at cap 20 on ≥ 21 of 25 seeds.
- **C2 — R still breaks the tie.** R's distinct score values ≥ 3× C's on each arm's own final pool, on
  ≥ 21 of 25 seeds (tightest development margin was 3.08×).
- **C3 — the directional hypothesis.** R's paired M1 exceeds C's at cap 20 on ≥ 21 of 25 seeds. The count
  is fixed by the null, not by the development result: 21 of 25 is the smallest count whose one-sided
  exact sign-test probability falls below 0.001 (0.00046), and the requirement is the larger of that
  and 80 % of the block, giving 21 of 25 (p = 0.00046).
- **C4 — the precision guard.** Median paired precision delta at cap 20 ≥ −0.02; no seed worse than −0.05; and
  where a size-matched point is bracketed, that delta ≥ −0.02.

## 6. Decision rule and outcome table, fixed now

| result | reading |
|---|---|
| C0 fails | **void** — instrument or world; nothing is reported about the hypothesis |
| C1–C4 all pass | the development reading **confirms** at this cap, in this world family, on the allocation used |
| C3 passes, C4 fails | fresh coverage was bought with noise; the reading does not reproduce as a gain |
| exactly one of C2/C3 fails | **partial** confirmation only; report which failed |
| C3 fails, C2 passes | the tie is breakable and breaking it does not help; the "admission is binding" reading is withdrawn for this cap |
| C1 fails | the control is no longer at chance, so the block is not comparable to the development block |

No result licenses an engine edit. A full pass is the strongest evidence one world family can supply and it is
still an argument for a proposed decision, not a change.

## 7. Cost and execution

275 cells at the development block's measured median of 7.3 s per cell is about 33
minutes (0.56 h) here, beyond a single command's limit, so the block runs in resumable chunks
(~40 cells) against `.scratch/ratio_confirm.jsonl`, one JSON line per (arm, cap, seed). A partial run reports
its completed cells and no readings. The estimate assumes per-cell cost is unchanged; the development spread
was 6.0–9.4 s.

## 8. Confounds and limits, disclosed before the run

- **One world family, one engine build.** Twenty-five seeds reduce seed variance; they do not generalise.
- **C is the harness's rule, not the engine's** — the C/R contrast sizes the ordering effect inside this
  benchmark. E carries the engine's rule and scores no prediction.
- **The ratio's standing still rests on the development block's 1.47 SE.** This block tests whether *applying*
  the ordering helps, not whether `ratio` is the best of the six candidates.
- **Allocation A's seeds were visible in other studies.** That is not leakage for this comparison — no artifact reports the count/ratio contrast on them,
  though 17 report asserted coverage under other arms — but it is weaker than a block on unnamed seeds, and the claim must be cut to fit.
- Cap 10 is a guard bracket, not an operating point; asserted sizes between caps are interpolated.

## 9. What confirmation would and would not license

A full pass licenses one sentence scoped to the allocation used: *in this world family, at caps up to 1,000,
ordering admission by the stored ratio raises asserted coverage without lowering precision, on 25 seeds
allocated before the run.* It does not license an engine change (frozen primitive, rule 2), a claim that
`ratio` is the right criterion, a claim beyond this world family, or a claim about precision at saturation,
which is arithmetic.

## 10. What an authorisation must contain

The date; this document's commit; the allocation chosen (**A** or **B**) and, for A, an explicit statement that
the acquisition study's confirmatory reservation is spent; the 275-cell plan, the caps and the pin; and an
acknowledgement that C0–C4 will be scored exactly as written.

## 11. Authorisation (2026-11-06) — allocation B, and the two mechanical changes it required

The owner ruled on the open decision, in these words:

> *"I would choose Allocation B (20270602–20270626) and authorize the confirmatory run."*

> *"Final ruling: Authorize the confirmatory experiment. Use Allocation B (20270602–20270626). Leave the engine
> unchanged. Treat the result as decisive for the admission-rule hypothesis regardless of whether it succeeds or
> fails."*

Allocation A is recorded as **permissible, not preferred** — the reasoning being that confirmation requires
seeds unexposed to any result that could influence interpretation, and A is named in 63 files. **B is the
allocation of record:** 20270602–20270626, 25 seeds, 0 occurrences across 440 scanned files. The engine is not
changed, and a null result is to be reported as decisive rather than as a reason to try another allocation.

**Two mechanical harness changes, recorded before the first cell:**

1. **Seed parameterisation.** `--block START:END` supplies the seed list; arms, caps, cell ordering, evidence
   fields, thresholds and cap values are untouched, and the development seeds remain the default.
2. **Asserted-set digest.** C0 as written compares *sets*, and the development harness recorded only their size.
   Each cell now also records a 16-hex SHA-1 of the sorted asserted edges. Nothing in admission reads it.

Neither change touches `organica/`, and both are recording/parameter plumbing rather than semantics: the same
per-cell code path runs, with `PYTHONHASHSEED=0`, and C0–C4 are scored exactly as written in §5.

## 12. Readings (2026-11-06)

All 275 cells completed, no failed seed, no substitution. **Verdict: PARTIAL / NOT COMPARABLE**, which is the frozen table's
last row and not a confirmation.

| criterion | result | detail |
|---|---|---|
| C0 liveness | **passes** | asserted sets differ on 25/25 seeds at cap 20; both arms at 1.0000 coverage by cap 1,000 |
| C1 control at chance | **FAILS** | 18/25 within ±0.05 of 0.4667; 22/25 below the base rate, median 0.4348, range 0.3656–0.4921 |
| C2 tie broken | passes | 24/25 at ≥3×; tightest margin 2.83× |
| C3 coverage | passes | 24/25; median delta 0.0446; exact one-sided p = 7.7e-07 |
| C4 precision guard | passes | median 0.0128, worst -0.0084, 4/25 falling |

C1 was written to catch exactly this and it fired: the development block's "count is at chance" reading does not
reproduce on fresh worlds, where the same rule sits below chance on 22 of 25 seeds. The treatment contrast
survives that — C2, C3 and C4 all pass — but under the pre-registered decision rule the block is **not
comparable**, and that is how it is recorded. The predictions were not re-read, relaxed or reinterpreted.

## 13. Amendment 1 (2026-11-06): C1 re-specified, with its power computed in advance

**At the owner's direction (2026-11-06), after this block's readings were recorded.** This amendment re-specifies the
control criterion for *future* blocks. It does not alter §1–§12, does not re-score any cell of 20270602–20270626, and
leaves §12's verdict exactly as the frozen table returned it. For future blocks it supersedes C1's row of §6; §6 is
left as written.

**Why it is needed.** C1 asked for |M2(C) − 0.4667| ≤ 0.05 at cap 20 on ≥ 21 of 25 seeds. §8.8 of the capacity
record measured that band against 200 fresh worlds: it covers 81.5% of seeds, so a 21-of-25 bar passes 49.7% of the
time on a block drawn from a population that matches the reference. A criterion that fails half the time for sampling
reasons cannot distinguish a control that has drifted from its own noise, which is the one thing it exists to do.

**C1′ — the control is at the structural base rate, within a calibrated equivalence margin.**

- *Statistic.* m̄, the mean of M2(C) at cap 20 over the block's n = 25 seeds, one cell per seed.
- *Comparator.* β = 0.4667 — the pool's composition, 112 world edges in 240 rows — verified per cell by
  `pool_diagnostics`, not estimated from any block.
- *Margin.* δ = 0.032. Fixed from the 200-seed calibration sweep (seeds 20270701–20270900, disjoint from every scored
  block) as the smallest 0.001-grid value at which 90.8% of 20,000 bootstrap 25-seed blocks satisfy |m̄ − β| ≤ δ. Closed
  form |offset| + z₀.₉₀·se = -0.0218 + 1.282 × 0.0075 = 0.0315, rounded up to the grid.
- *Decision.* Pass iff |m̄ − 0.4667| ≤ 0.032, i.e. m̄ ∈ [0.4347, 0.4987]. Fail-low (control below the base rate by more than
  the margin) and fail-high (above it) are recorded separately; both mark the block **not comparable**.
- *Power.* 0.908 empirical, 0.0315 closed-form, against the reference population.

| shift in the control's true mean | P(C1′ passes) |
|---|---|
| +0.000 | 0.908 |
| -0.005 | 0.761 |
| -0.010 | 0.527 |
| -0.015 | 0.269 |
| -0.022 | 0.052 |
| -0.032 | 0.001 |
| -0.050 | 0.000 |
| +0.020 | 1.000 |

**What it buys, and what it costs.** Against a matching population it now fails 9.2% of the time instead of 50%, so
a failure carries information. The price is sensitivity: the margin absorbs a further 0.0102 (1.4 se) of systematic
shortfall before failing, and a shift of -0.011 is where the pass rate drops below half — so a control that worsens by
less than about a hundredth still passes. That is deliberate: a criterion that cannot separate that much drift from
noise should not pretend to. **The criterion is about the mean only** and is blind to a block whose mean is right and
whose dispersion has changed; in the calibration data 0.0% of in-band
blocks had a within-block sd above 0.0753 (twice the reference), which is why no dispersion clause is
attached — one that fires almost never is decoration, not rigour.

**Margin fragility.** Recomputing δ from 500 bootstrap resamples of the 200 calibration seeds gives
0.0269–0.0367 (median 0.0314), so the chosen value is not knife-edge on the calibration
draw. It is still a calibration from one sweep of one world family, and a different family or cap would need its own.

**Not retroactive.** δ is a function of the calibration sweep alone; no cell of 20270602–20270626 entered it. For
completeness, since a reader will compute it: that block's mean is 0.4338, |m̄ − β| = 0.0329, which is 0.0009 outside the
band. That is reported, not adjudicated — applying a criterion to the data that motivated writing it is the re-scoring
§12 refuses, and §12 stands.

**Provenance.** `docs/gate13_c1_respecification.json`, generated by `benchmarks/derive_c1_respecification.py` from
`docs/gate13_control_precision_sweep.json`. Calibration, not confirmation.

**Owner review (2026-11-06): approved as written.** On the record: δ derives from calibration data this block
did not contribute to, the power curve and the blind spot are disclosed, the dispersion clause was measured
before being omitted, and 0.4338 is reported without being re-scored. The reviewer's framing is adopted
because it states what the test is for: C1′ asks whether the block is *consistent with the calibration
population*, not whether it reproduces a point estimate — and the published margin is only meaningful beside
the shift at which its power falls below half (-0.011). The amendment is unchanged by the review.
