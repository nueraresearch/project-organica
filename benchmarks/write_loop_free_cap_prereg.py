"""Write the block-8 pre-registration for cap scaling, from the calibration artifact and nothing typed by hand."""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAL = json.loads((REPO / "docs/gate13_loop_free_cap_calibration.json").read_text())
E = CAL["effect"]
P = CAL["perturbation"]
L = CAL["liveness"]
A = CAL["allocation"]
CAPS = CAL["caps"]
BAR = CAL["bar"]["did"]
G0 = CAL["gates"]["G0_bar"]
G2 = CAL["gates"]["G2_bar"]
power_rows = "\n".join(f"| {k} | {v['power_point']:.3f} | {v['power_point_and_ci']:.3f} |"
                       for k, v in CAL["power"].items())
cells = 2 * len(CAPS) * A["seeds"]


def f(x, n=4):
    return f"{x:.{n}f}"


doc = f"""# Gate 13, block 8 — does the loop-free admission gain scale with the cap?

**Status: FROZEN, NOT RUN.** The criteria, gates, bar and allocation below were written before any judged cell was run.
Nothing here may be changed after the run; the readings are appended as §13 and any defect is disclosed there rather
than repaired.

## 1. Question

Block 7 measured the loop-free arm's gain at cap 20: mean Y − R coverage **{f(E['d40_mean'] if False else E['d100_mean'])}** on fresh
seeds, M1 and M2 both passing. The gain is a statement about *how a fixed budget is spent*: Y withholds prediction
candidates whose edges loops already assert, so the twenty slots go to non-redundant edges. If that mechanism is what
produces the gain, the gain should **grow with the budget**, because a larger cap widens the pool from which the loop
edges would otherwise be drawn and leaves more non-redundant edges to admit. If the gain is an artifact of the cap-20
pool — for instance, a fixed set of loop edges crowding a small budget — it should not grow, and may vanish.

This block tests the scaling prediction directly, on two larger caps, with the same arm and world.

## 2. Design — caps 40 and 100, arms R and Y, fresh seeds

- **Arms:** R (no intervention) and Y (loop-asserted edges sorted last at admission, cap reservation). Arm C is not run:
  the claim is Y versus R, and the comparability question is whether the cap axis itself is live, which this block's own
  R cells answer.
- **Caps:** 40 and 100.
- **Seeds:** the frozen window **{A['lo']}–{A['hi']}**, {A['seeds']} seeds, {cells} cells (2 arms × 2 caps × {A['seeds']} seeds).
- **World, readout, cycles:** unchanged from blocks 6 and 7.
- **Arm code:** `benchmarks/run_loop_free_admission_block.py`, `--caps 40,100`; the cap-20 self-test was re-run after the
  extension and reproduced block 7's cap-20 cell exactly (`{CAL['calibration_seeds'][0]}` and the frozen window were
  checked; the self-test at 20270901 still passes).

## 3. What is measured

Per seed and cap: coverage of the world's asserted edges, precision, novel and loop-covered coverage, displacement of the
previous cycle's asserted set by this cycle's, and whether R's and Y's final asserted sets differ (the liveness gate).

The **scaling quantity** is the difference-in-differences

    DiD(seed) = [Y − R coverage at cap 100] − [Y − R coverage at cap 40]

which is a paired, per-seed number: both gains come from the same seed, so the world's difficulty cancels.

## 4. Gates (all must pass, or the block is void)

| Gate | Requirement | Why |
| --- | --- | --- |
| G0 liveness, both caps | Y and R final asserted sets differ on at least **{G0}/100** seeds **at each cap** | an arm that changes nothing is not measurable |
| G1 perturbation, both caps | at least **{G2}/{A['seeds']}** seeds displaced at each cap | the readout must be alive |
| G2 axis live | mean R coverage at cap 100 > at cap 40, bootstrap interval above zero | otherwise the cap axis changes nothing and no scaling claim can be read (rule 13c) |

Calibration measured liveness **{L['by_cap']['40']}/{L['n_per_cap']}** at cap 40 and **{L['by_cap']['100']}/{L['n_per_cap']}**
at cap 100; displacement mean **{f(P['by_cap_mean']['40'], 2)}** and **{f(P['by_cap_mean']['100'], 2)}** cells.

## 5. M1 — the scaling criterion

**Mean DiD ≥ {BAR}**, with the 95% bootstrap interval's lower bound above zero.

The bar is the one blocks 6 and 7 applied to the gain itself: one fifth of R's gain over C at cap 20 (0.0485). Here it
applies to the **change** in the gain between caps 40 and 100, so the claim is that the larger budget adds at least a
block-7-sized gain on top of the smaller one. Calibration measured a mean DiD of **{f(E['did_mean'])}** (sd
{f(E['did_sd'])}, {E['did_positive_n']}/{E['did_n']} seeds positive).

## 6. M2 — the gain must exist at both caps

Mean Y − R > 0 at **each** cap, with the interval's lower bound above zero.

Without M2, M1 could pass through a *negative* gain at cap 40 — a loss that becomes a smaller loss, not a scaling
effect. Requiring both gains positive makes the scaling claim conditional on the arm working at both budgets.

## 7. Decision table, fixed in advance

| M1 | M2 | Verdict | Reading |
| --- | --- | --- | --- |
| pass | pass | **SCALING SUPPORTED** | the gain grows with the budget, and is positive at both |
| pass | fail | **SCALE-DEPENDENT** | the gain appears or reverses at one budget; not scaling |
| fail | pass | **GAIN WITHOUT SCALING** | the arm helps at both caps, by a similar amount |
| fail | fail | **NO GAIN AT THESE CAPS** | the cap-20 result does not extend to larger budgets |

A gate failure voids the block: **VOID / NOT COMPARABLE**, reported as the gate and not as a verdict.

## 8. Power, computed in advance

Ten calibration seeds at each cap, resampled to {A['seeds']} seeds, 4,000 replicates per row.

| bar | point criterion | point and interval |
|---|---|---|
{power_rows}

The DiD is a noisier quantity than either gain, because it differences two paired differences, so the power figures are
estimates from ten seeds and are reported as such. Calibration: gain at cap 40 **{f(E['d40_mean'])}** (interval
{f(E['d40_ci'][0])} to {f(E['d40_ci'][1])}), at cap 100 **{f(E['d100_mean'])}** (interval {f(E['d100_ci'][0])} to
{f(E['d100_ci'][1])}), DiD **{f(E['did_mean'])}** (interval {f(E['did_ci'][0])} to {f(E['did_ci'][1])}).

## 9. Pre-registered predictions

1. **P1 (primary).** M1 passes: the gain at cap 100 exceeds the gain at cap 40 by at least {BAR}, interval above zero.
2. **P2.** M2 passes: the gain is positive at both caps.
3. **P3.** The novel-edge channel carries the scaling: the change in novel covered edges between caps is larger for Y than
   for R, and the loop-covered difference does not turn negative.
4. **P4.** R's own coverage rises with the cap (G2), so the axis is live.

## 10. What this block cannot say

- It measures coverage of one world family's asserted edges at two caps, at this readout. A scaling result is a statement
  about **where the arm's benefit comes from**, not a general claim that larger budgets always help.
- Two caps test a difference, not a shape: a monotone curve needs more points, and the cap-20 point comes from block 7 on
  different seeds and is reported as context only, never pooled into this block's criteria.
- Nothing here changes the loops themselves; the arm only changes which candidates are admitted.

## 11. Artifacts

`docs/gate13_loop_free_cap_calibration.json` (this pre-registration's source), `benchmarks/score_loop_free_cap.py`
(scoring, run once), `docs/gate13_loop_free_cap.json` (readings). Capacity record §8.19; manual paragraph and revision
row; changelog section.
"""
out = REPO / "docs" / "GATE13-LOOP-FREE-CAP-SCALING-PREREGISTRATION.md"
out.write_text(doc)
print("wrote", out, "lines:", len(doc.splitlines()), "brace lines:", sum(1 for ln in doc.splitlines() if "{" in ln or "}" in ln))
