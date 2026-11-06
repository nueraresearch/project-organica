"""Freeze the loop-redundancy moderator pre-registration from the calibration artifact. No cell of the block is run."""
from __future__ import annotations

import json
from pathlib import Path

CAL = json.loads(Path("docs/gate13_redundancy_moderator_calibration.json").read_text())
A, FR = CAL["allocation"], CAL["freshness"]
P = CAL["power"]
N = A["seeds"]
MECH, IMPL, NULL = P[f"n{N}_mechanism_sized"], P[f"n{N}_calibration_implied"], P["n100_null"]
ASSOC, FIT, BARS = CAL["association"], CAL["linear_fit"], CAL["bars"]
R_THR = CAL["threshold_r"]

DOC = f"""# Gate 13 — loop-redundancy moderator pre-registration (block 3)

**Status: FROZEN, NOT RUN.** No cell of this block has been executed. The criteria below were fixed before the first cell,
from artifacts that the block does not contain (§4). Amendments, if any, are appended with a date; this text is not edited
to match a result.

## 1. Question

Block 2 returned `TREATMENT NOT REPRODUCED` with C1′ passing for the first time, and §8.11-§8.13 narrowed the variation to
one place: the ratio arm always adds temporal (`prediction_candidate`) edges, loop (`loop_candidate`) coverage is identical
across arms, and the 20/5 split tracked whether those temporal edges were **already present in the loop structure**.

That mechanism makes a prediction about *which seeds* the treatment should help: where the loops already cover most of the
world, there is less for admission to add. This block tests that prediction on a fresh allocation, with a covariate that is
readable from the control cell before the ratio cell is scored.

## 2. What is registered, and what is not

Registered: the covariate, its threshold, three gates, three criteria, the decision table, and the power of every bar under
two effect sizes. Not registered and not changed: the arms (count control C, ratio arm R as defined in
`benchmarks/run_ratio_admission_arm.py`), cap 20, the world generator, the readout, and the frozen engine.

## 3. Allocation and cells

- Seeds **{A['lo']}-{A['hi']}**, **{N} seeds**, chosen as the first run of {N} consecutive seeds at or after 20271001 that
  appears nowhere in the tree. Freshness scan: **{FR['files_scanned']} files** (`.py`, `.md`, `.json`), **{len(FR['occurrences_in_range'])}
  occurrences in the allocated range**. The candidate window 20271001-{A['lo'] - 1} was rejected for {len(FR['rejected_hits'])} pre-existing
  occurrences ({', '.join(str(x) for x in FR['rejected_hits'])}), which is why the allocation starts at {A['lo']} and not at 20271001.
- Cells: **C and R at cap 20, {N * 2} cells**. No other cap and no E arm — no criterion here reads them.
- Runner: `benchmarks/run_redundancy_block.py`, which records the asserted-set digest, coverage, precision and the store-time
  loop attribution. Command for the block:
  `PYTHONPATH="$PWD" PYTHONHASHSEED=0 .venv/bin/python benchmarks/run_redundancy_block.py --block {A['lo']}:{A['hi']} --budget 200 --jsonl .scratch/redundancy_block.jsonl`
- The runner was self-tested **before** the block on the excluded seed 20270901: both arms reproduce block 2's `asserted`,
  `covered` and digest (C 90/34/`1a51184e43b546a7`, R 87/34/`129da0ffd2052b85`). A runner that cannot reproduce a scored
  cell is not a runner for this block.

## 4. Covariate (pre-treatment, arm-independent)

`r_s = |W and L_s| / |W|`: the share of the world's {CAL['world_edges']} edges that the control cell's **loop** candidates
assert, where `L_s` is measured by a store-time observer over the same sleep payloads `structure_edges` aggregates. Loops are
built from the stream and are not what the admission cap ranks; §8.13 measured loop attribution identical across arms on
10/10 seeds, and gate **G2** re-checks that on every block cell.

- Threshold `r*` = {R_THR}, fixed from the {ASSOC['n']} calibration seeds (block 2) as their median, which the block does
  not contain. `r_s < r*` is the *low-redundancy* half.
- The covariate uses the control cell. The outcome is the paired difference R − C. Disclosed: the control therefore appears
  on both sides, which is why the covariate is defined on **loop** edges only (arm-invariant, G2) and not on the arm's
  prediction edges (which would be the treatment's own output).

**Calibration, stated honestly.** On the {ASSOC['n']} calibration seeds the association between `r_s` and the gain is
**Pearson {ASSOC['pearson']}, Spearman {ASSOC['spearman']}** — the *wrong* sign for the mechanism's prediction, with a linear
slope of {FIT['slope']} and residual sd {FIT['resid_sd']}. Ten seeds cannot separate +{ASSOC['pearson']} from −0.4. The block
therefore tests the proxy's directional prediction *against* the calibration's hint, not with it.

## 5. Gates (a failed gate voids the block; it is not a negative result)

- **G0 liveness**: the C and R asserted sets differ on at least 96 of {N} seeds. If they do not, the arm is not manipulating
  admission and nothing downstream is interpretable.
- **G1 comparability (C1′)**: the block-mean cap-20 control precision lies in [0.4347, 0.4987] (δ = 0.032 from
  `docs/gate13_control_precision_sweep.json`, as in block 2). If it does not, the block is `NOT COMPARABLE` and no criterion
  is read.
- **G2 loop invariance**: loop attribution is identical between arms on at least 98 of {N} seeds. If it is not, the covariate
  is treatment-dependent and the moderator framing is void.

## 6. Criteria (evaluated once, in this order, by committed code)

- **M1 — half-split contrast.** Let `gain_s = coverage_R - coverage_C`. Split at `r*`. Pass iff both halves have at least 40
  seeds and `median(gain, low) - median(gain, high) >= {BARS['m1_median_gain_difference']}`.
- **M2 — directional association.** Pass iff `Spearman(r_s, gain_s) <= {BARS['m2_spearman_max']}` across all {N} seeds
  (one-sided; the mechanism predicts lower redundancy, larger gain).
- **M3 — replication (secondary, never confirmatory).** Pass iff at least {int(BARS['m3_positive_share'] * N)} of {N} seeds have
  `gain_s > 0`. Block 2 gave 20/25; this bar only asks whether that rate survives a fresh allocation.

## 7. Decision table (fixed)

| M1 | M2 | G0-G2 | verdict |
|---|---|---|---|
| pass | pass | pass | **MODERATOR SUPPORTED** — pre-treatment loop redundancy predicts where the ratio arm helps |
| fail | pass | pass | **DIRECTIONAL ONLY** — the association is there, the half-split contrast is not |
| pass | fail | pass | **HALF-SPLIT ONLY** — a threshold contrast without a monotone association; read as fragile |
| fail | fail | pass | **MODERATOR NOT SUPPORTED** — the proxy is not a predictor at this n |
| — | — | fail | **VOID / NOT COMPARABLE** — report the gate, not a verdict |

M3 is reported beside the verdict and never substitutes for M1 or M2.

## 8. Power, computed in advance

Simulated by resampling the {ASSOC['n']} calibration pairs and adding Gaussian noise at the fitted residual sd
({FIT['resid_sd']}), 4,000 replicates per row. "Mechanism-sized" is a slope of {MECH['slope']} — the effect the mechanism
implies, i.e. about 0.055 of coverage across the observed r range.

| scenario | n | M1 | M2 | M1 and M2 | M3 |
|---|---|---|---|---|---|
| mechanism-sized | {MECH['n']} | {MECH['power_m1_half_split']} | {MECH['power_m2_spearman']} | {MECH['power_both']} | {MECH['power_m3_replication']} |
| calibration-implied | {IMPL['n']} | {IMPL['power_m1_half_split']} | {IMPL['power_m2_spearman']} | {IMPL['power_both']} | {IMPL['power_m3_replication']} |
| null (no association) | {NULL['n']} | {NULL['power_m1_half_split']} | {NULL['power_m2_spearman']} | {NULL['power_both']} | {NULL['power_m3_replication']} |

**What this means, before the data arrive.** The joint bar has **{MECH['power_both']}** power against a real,
mechanism-sized moderator, and the false-positive rate at no association is **{NULL['power_both']}**. The test is therefore
**asymmetric by design**: a `MODERATOR SUPPORTED` verdict would be strong evidence; a `MODERATOR NOT SUPPORTED` verdict is
**weak evidence against the mechanism** and only meaningful evidence against the proxy. If the calibration's
+{ASSOC['spearman']} is the truth, the expected verdict is `MODERATOR NOT SUPPORTED` with power {IMPL['power_both']} to have
said otherwise — so that outcome must not be reported as a refutation of §8.13.

For scale: 25 seeds would have given {P['n25_mechanism_sized']['power_both']}; {N} is the smallest allocation in this design
that keeps the joint power above {MECH['power_both']} without exceeding a 15-minute block.

## 9. Pre-registered predictions

- **P1** G2 holds: loops are arm-invariant on at least 98 of {N} seeds (they were on 10/10).
- **P2** M3 passes: the overall gain replicates at 20/25-like rates, since nothing about the arm changed.
- **P3** M2 fails at the {BARS['m2_spearman_max']} bar, because the calibration association is positive
  (+{ASSOC['spearman']}); if it passes, the signal is negative and the proxy is live.
- **P4** If M2 passes, M1 also passes (the half-split contrast is the easier of the two at a mechanism-sized effect:
  {MECH['power_m1_half_split']} vs {MECH['power_m2_spearman']}).
- **P5** The block's loop-coverage distribution is close to the calibration's (0.24-0.79); if `r_s` is compressed near 0 or 1,
  the split has too few seeds per half and M1 is `INCONCLUSIVE BY SIZE`, which is recorded as such.

## 10. What each outcome would and would not license

- `MODERATOR SUPPORTED`: loop redundancy is a usable pre-run covariate for this arm on this world family. It does **not**
  establish the mechanism's causal claim (loops pre-empting temporal edges) — that needs the time-ordered observer §8.13
  could not provide, or the loop-novelty arm below.
- `MODERATOR NOT SUPPORTED`: the proxy is not a predictor at n={N}. It does **not** refute §8.13's composition finding, and it
  does **not** refute the mechanism; it says the between-seed implication is too weak to detect at this size.
- The decisive test of the mechanism is an **intervention**, not a moderator: an arm identical to R that prefers temporal
  candidates whose edge is not already asserted by a loop at admission time. That arm changes the outcome directly and is
  not registered here.

## 11. Freeze

Criteria, gates, threshold, bars, allocation and decision table are frozen as written. No cell of {A['lo']}-{A['hi']} has been
run. Scoring code must read the threshold and bars from `docs/gate13_redundancy_moderator_calibration.json` rather than
recompute them. Artifacts: `docs/gate13_redundancy_moderator_calibration.json`,
`docs/gate13_structure_provenance.json`, `docs/gate13_ratio_block2.json`.
"""

assert "{" not in DOC.replace("|W and L_s|", "") and "}" not in DOC
Path("docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md").write_text(DOC)

MANUAL = f"""**A fresh-allocation block is pre-registered to test pre-treatment loop redundancy as the moderator of the ratio arm's
gain — and nothing has run.** Seeds {A['lo']}-{A['hi']} ({N} seeds, zero occurrences across {FR['files_scanned']} files; the window
starting at 20271001 was rejected for {len(FR['rejected_hits'])} pre-existing hits), C and R at cap 20 only, 200 cells. The covariate is
`r_s` — the share of the world's edges the control cell's loop candidates already assert — split at the frozen threshold
{R_THR}, with gates for arm liveness, C1′ comparability and loop invariance. Bars: M1 median gain contrast ≥ {BARS['m1_median_gain_difference']},
M2 Spearman ≤ {BARS['m2_spearman_max']}, M3 replication ≥ {int(BARS['m3_positive_share'] * N)}/{N}. Power is stated in advance: {MECH['power_both']} joint
against a mechanism-sized effect, {NULL['power_both']} at no association — so a pass is strong evidence and a miss is weak evidence
against the mechanism, which is exactly how the document says to read it. Calibration gives the covariate the wrong sign
(Spearman +{ASSOC['spearman']} on {ASSOC['n']} seeds), disclosed in the document. Runner `benchmarks/run_redundancy_block.py`
self-tested against block 2 on the excluded seed 20270901 before the freeze. `docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md`;
`docs/gate13_redundancy_moderator_calibration.json`.
"""

ROW = f"""| 2026-11-06 | **Block 3 pre-registered and frozen, unrun: loop redundancy as the moderator of the ratio arm's gain.** Seeds {A['lo']}-{A['hi']} (first unused {N}-seed run; 20271001 onward was rejected for pre-existing hits), C and R at cap 20, 200 cells. Covariate `r_s` = loop-asserted share of the world, read from the control cell before the ratio cell is scored; threshold {R_THR} fixed from the 10 calibration seeds. Gates G0 liveness, G1 C1′, G2 loop invariance (void, not negative); criteria M1 half-split ≥ {BARS['m1_median_gain_difference']}, M2 Spearman ≤ {BARS['m2_spearman_max']}, M3 replication ≥ {int(BARS['m3_positive_share'] * N)}/{N} (secondary). Power fixed in advance: {MECH['power_both']} joint under a mechanism-sized effect, {NULL['power_both']} under no association, so a miss is weak evidence against the mechanism and is labeled that way. Calibration's association is the wrong sign (+{ASSOC['spearman']}), disclosed. Runner self-tested against block 2 on excluded seed 20270901. `docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md`; `docs/gate13_redundancy_moderator_calibration.json`. |
"""

CHANGELOG = f"""### Pre-registered — loop-redundancy moderator block (frozen, unrun) (2026-11-06)

- Block 3 freezes the §8.13 mechanism as a prediction about *which seeds* the ratio arm should help: pre-treatment loop
  coverage of the world (`r_s`, the share of the world's edges the control's loop candidates already assert) should predict
  the gain. Seeds {A['lo']}-{A['hi']} ({N} seeds, zero occurrences in the tree; 20271001 onward rejected for
  {len(FR['rejected_hits'])} pre-existing hits), C and R at cap 20, 200 cells, nothing run.
- Threshold {R_THR} and all bars are fixed from the 10 calibration seeds, which the block does not contain. Gates: arm
  liveness, C1′ comparability, and loop invariance across arms (a failed gate voids rather than negatives the block).
- Power is published **before** the data: {MECH['power_both']} joint for M1 and M2 against a mechanism-sized moderator,
  {NULL['power_both']} at no association. The decision table therefore reads a pass as strong evidence and a miss as weak
  evidence against the mechanism — and the document says so in those words.
- Disclosed honestly: on the 10 calibration seeds the covariate's association is **+{ASSOC['spearman']}**, the wrong sign
  for the mechanism. The block tests the proxy against that hint rather than with it.
- `benchmarks/run_redundancy_block.py` self-tested on the excluded seed 20270901 and reproduces block 2's asserted sets,
  coverages and digests for both arms before the freeze.
- `docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md`, `benchmarks/run_redundancy_block.py`,
  `benchmarks/calibrate_redundancy_moderator.py`, `docs/gate13_redundancy_moderator_calibration.json`.

"""

man = Path("docs/USER-MANUAL.md")
text = man.read_text()
if "A fresh-allocation block is pre-registered to test pre-treatment loop redundancy" not in text:
    lines = text.split("\n")
    start = next(k for k, ln in enumerate(lines)
                 if "What carries the ratio arm's coverage" in ln and not ln.startswith("|"))
    end = next((k for k in range(start + 1, len(lines)) if lines[k] == ""), len(lines))
    lines[end:end] = MANUAL.rstrip("\n").split("\n") + [""]
    text = "\n".join(lines)
if "Block 3 pre-registered and frozen, unrun" not in text:
    text = text.rstrip() + "\n" + ROW
man.write_text(text)

chg = Path("CHANGELOG.md")
text = chg.read_text()
if "### Pre-registered — loop-redundancy moderator block" not in text:
    chg.write_text(text.replace("## [0.12.0] — (unreleased)",
                                CHANGELOG + "## [0.12.0] — (unreleased)", 1))
print("prereg + manual + changelog written")
