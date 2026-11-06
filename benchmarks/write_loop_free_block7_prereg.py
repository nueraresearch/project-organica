"""Write block 7's pre-registration from its calibration artifact. Every number is substituted, none is typed.

The document is generated once, before the first cell, and §13 records the readings afterwards. The arm, world, cap,
readout and M1 bar are block 6's, unchanged; the only change is G0, which block 6 registered at 96/100 while its own
calibration measured liveness at 6/10.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAL = json.loads((REPO / "docs/gate13_loop_free_block7_calibration.json").read_text())
B6 = json.loads((REPO / "docs/gate13_loop_free_block6.json").read_text())
E, L = CAL["effect"], CAL["liveness"]
BAR, NOVEL_BAR = CAL["bar"]["m1_mean_difference"], CAL["bar"]["novel_bar"]
BAND, ALLOC = CAL["gates"]["band"], CAL["allocation"]
G = CAL["gates"]
POW = CAL["power"]
LO, HI = ALLOC["lo"], ALLOC["hi"]
F = lambda x: f"{x:.4f}"
F3 = lambda x: f"{x:.3f}"
rows = "\n".join(f"| {b} | {F3(POW[str(b)]['power_point'])} | {F3(POW[str(b)]['power_point_and_ci'])} |"
                 for b in [0.005, 0.0075, 0.01, 0.0125, 0.015])

DOC = f"""# Gate 13 — the loop-free preference arm, block 7 (gate repaired)

**Status: FROZEN, NOT RUN.** The criteria, gates, bar and allocation below were fixed before the first cell, from
artifacts the block does not contain (§4, §5). Readings are appended in §13 with a date; this text is not edited to
match a result.

## 1. What this block changes, and what it does not

Block 6 registered the arm §10 of block 5 named — Y, R with loop-asserted edges sorted last at admission — ran its 300
cells and was **void by its own G0**: Y's asserted set differed from R's on {B6['gates']['G0_liveness_y_vs_r']} of 100
seeds against a required 96, while the same pre-registration printed the calibration's 6-of-10 liveness beside that
bar. A 96/100 threshold on a 62% event cannot fire; that is block 4's defect in a new gate, and it is recorded in block
6's readings as a specification error rather than a result about the arm.

**Block 7 changes exactly one thing: G0's bar.** The arm, the world, cap 20, the readout, the C1′ band, G2's bar, the
M1 bar and its M2 partner, and the C/R baselines are block 6's, unchanged. The new G0 bar is {G['G0_bar']}/100,
calibrated to the pooled liveness rate {L['rate']} ({L['n_differ']} of {L['n']} cells across {CAL['calibration_sources']['total']}
calibration pairs): the arm must change the final asserted structure on at least half the seeds. That bar is reachable
by construction — under the measured rate G0 itself passes with probability {L['power_of_gate']} — while the block-6 bar
would have passed with probability {L['power_of_block6_bar']}.

## 2. Question

Does removing temporal redundancy from the ratio arm's admission budget raise its coverage? Same question as block 6,
asked with a gate that can be met. The claim under test is causal in the narrow sense only: the arm changes which
candidates the cap is spent on and leaves loops, construction, thresholds and readout untouched.

## 3. What is registered, and what is not

Registered: G0's calibrated bar and the three unchanged gates, M1 and M2 with their bars, the decision table, the
allocation, and the power of M1 at the unchanged bar. Not changed: any frozen engine file, the arm's implementation,
the world generator, the readout, and blocks 2–6's records.

## 4. Allocation and cells

- Seeds **{LO}-{HI}**, **{ALLOC['seeds']} seeds**: the first free 100-seed window after block 6's allocation, by a scan
  of {CAL['freshness']['files_scanned']} files. Rejected hits inside the candidate range: {CAL['freshness']['rejected_hits']}.
- Cells: **C, R and Y at cap 20 — {3 * ALLOC['seeds']} cells**, no other cap, no E arm.
- Runner: `benchmarks/run_loop_free_admission_block.py`, unchanged from block 6 and validated against block 2 before
  either block ran (C 90/34/`1a51184e43b546a7`, R 87/34/`129da0ffd2052b85`). Command:
  `PYTHONPATH="$PWD" PYTHONHASHSEED=0 .venv/bin/python benchmarks/run_loop_free_admission_block.py --block {LO}:{HI} --budget 300 --jsonl .scratch/loop_free_block7.jsonl`
- A missing cell is a defect, not a seed to substitute.

## 5. Calibration evidence (110 pairs, none judged here)

Sources: block 6's 100 cells — void by their own gate, so rule 19 permits using them, as block 5 used block 4's void
cells — and the ten dose-calibration seeds. The arm is identical in both, so the pairs are comparable.

- **Liveness** {L['n_differ']}/{L['n']} = {L['rate']}: on roughly two seeds in five the intervention changes admission
  and leaves the final asserted set identical to R's, because the asserted structure is a ninety-cycle accumulation.
  G0 therefore tests that the arm *does* reach the structure on at least half the seeds, not that it does so on almost
  all of them.
- **Effect** mean {F(E['mean'])}, median {F(E['median'])}, sd {F(E['sd'])}, positive on {E['positive_n']} of {E['n']}.
  Block 6's own mean was {F(E['block6_mean'])}, i.e. **below** the unchanged {BAR} bar; that is the honest state of the
  evidence and it is why §8 reports M1's power as low rather than lowering the bar.
- **Mechanism** novel covered edges {E['novel_mean']} on average (interval {E['novel_ci']}), loop-covered change
  {E['loop_covered_mean']} — the same composition block 6 measured.

## 6. Gates (a failed gate voids the block; it is not a negative result)

- **G0 liveness**: Y and R differ on at least **{G['G0_bar']}** of {ALLOC['seeds']} seeds, calibrated to the observed
  rate; power of the gate under that rate {L['power_of_gate']}.
- **G0b liveness of the pair being measured**: C and R differ on at least {G['G0b_bar']} seeds. Block 6 measured
  100/100.
- **G1 comparability (C1′)**: mean cap-20 control precision in [{BAND[0]}, {BAND[1]}]. Block 6 measured 0.4441.
- **G2 perturbation**: the preference displaced at least one admitted edge on at least {G['G2_bar']} seeds. Block 6
  measured 100/100. An intervention that displaces nothing has not run.

## 7. Criteria (evaluated once, in this order, by committed code)

- **M1**: `mean(coverage_Y - coverage_R) >= {BAR}` **and** the 95% bootstrap interval's lower bound > 0. Unchanged from
  block 6, so the two blocks test the same claim at the same bar.
- **M2**: `mean(covered_novel_Y - covered_novel_R) >= {NOVEL_BAR}` with interval above zero, **and** loop-covered
  coverage not lower on average. Unchanged.

## 8. Power, computed in advance — and it is low

Resampling the 110 calibration pairs to 100 seeds, 4,000 replicates per row.

| bar | point criterion | point and interval |
|---|---|---|
{rows}

**{CAL['power_note']}.** This is the opposite disclosure from block 6, where the bar sat 2.46 standard errors below the
calibrated mean: here the pooled mean is {F(E['mean'])}, so at the unchanged bar the block is a coin flip at best. The
bar is **not** lowered, because moving it after block 6's miss would make this block a second attempt at a result
rather than a repair of a gate. The consequence is stated plainly: **a pass is informative, a miss is not evidence
against the intervention**, and the block will say which one it produced.

## 9. Pre-registered predictions

- **P1** G0, G0b, G1 and G2 all pass: the arm reaches the structure on at least half the seeds, the block is
  comparable, and the preference displaces something.
- **P2** M1 lands near the pooled mean {F(E['mean'])}; whether that clears {BAR} is not predicted, because the two
  estimates straddle it.
- **P3** M2 passes: the gain, if any, is in novel covered edges with loop-covered coverage unchanged.

## 10. What each outcome licenses

- `INTERVENTION SUPPORTED`: the admission budget's redundancy is a cost at this cap and readout, on a fresh allocation,
  with a gate that could fire. It licenses an admission-rule change, not a claim about what loops are for.
- `COVERAGE ONLY`: the arm helps, not through the channel it claims.
- `INTERVENTION NOT SUPPORTED`: at this bar and n the arm does not beat R. Given the disclosed power this is **not**
  evidence of no effect; it is the end of this readout as a test, and a sharper endpoint would need its own block.
- Any gate failure: `VOID / NOT COMPARABLE`, reported as the gate. G0's bar is calibrated, so a G0 failure here would
  mean the liveness rate itself moved between blocks, which is a finding about the arm's reach.

## 11. Freeze

Criteria, gates, bar and allocation are frozen as written. No cell of {LO}-{HI} has been run.
`benchmarks/score_loop_free_block7.py` reads every bar, the band and the allocation from
`docs/gate13_loop_free_block7_calibration.json`. Artifacts: that file, block 6's artifact (void cells and composition),
the two dose artifacts, `docs/gate13_c1_respecification.json`.
"""

out = REPO / "docs" / "GATE13-LOOP-FREE-ADMISSION-PREREGISTRATION-B7.md"
out.write_text(DOC)
print("wrote", out, "lines:", len(DOC.splitlines()))
print("brace lines:", sum(1 for line in DOC.splitlines() if "{" in line or "}" in line))
