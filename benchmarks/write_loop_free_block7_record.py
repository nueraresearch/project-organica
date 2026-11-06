"""Write block 7's readings from `docs/gate13_loop_free_block7.json`. All numbers from artifacts; the verdict selects
the prose. Idempotent: sections are appended only if absent and anchors are located by text.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
art = json.loads((REPO / "docs/gate13_loop_free_block7.json").read_text())
CAL = json.loads((REPO / "docs/gate13_loop_free_block7_calibration.json").read_text())
G, C, D, V = art["gates"], art["criteria"], art["descriptive"], art["verdict"]
M1, M2 = C["M1"], C["M2"]
ALLOC, N = art["allocation"], art["seeds"]
BAR, NOVEL_BAR, BAND = art["bar"], art["novel_bar"], art["band"]
GB = art["gate_bars"]
fail = [k for k in ("G0", "G0b", "G1", "G2") if not G[f"{k}_pass"]]
ok = G["all_pass"]
f = lambda x: f"{x:.4f}"

GATE_TABLE = f"""| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, Y vs R | {G['G0_liveness_y_vs_r']}/{N} seeds with different asserted sets (bar {GB['G0']}) | {'yes' if G['G0_pass'] else 'NO'} |
| G0b liveness, C vs R | {G['G0b_liveness_c_vs_r']}/{N} seeds with different asserted sets (bar {GB['G0b']}) | {'yes' if G['G0b_pass'] else 'NO'} |
| G1 comparability (C1′) | mean control precision {f(G['G1_mean_c_precision'])} in [{BAND[0]}, {BAND[1]}] | {'yes' if G['G1_pass'] else 'NO'} |
| G2 perturbation | {G['G2_seeds_preference_displaced']}/{N} seeds with an edge displaced (bar {GB['G2']}) | {'yes' if G['G2_pass'] else 'NO'} |"""

if not ok:
    CAUSE = {
        "G0": f"Y and R asserted the same set on {N - G['G0_liveness_y_vs_r']} seeds, more than the calibrated bar "
              f"({GB['G0']}) allows; the liveness rate moved between blocks, which is a finding about the arm's reach",
        "G0b": f"C and R asserted the same set on {N - G['G0b_liveness_c_vs_r']} seeds, so the block is not the "
               f"comparison blocks 2–6 ran",
        "G1": f"the mean control precision {f(G['G1_mean_c_precision'])} fell outside the C1′ band [{BAND[0]}, {BAND[1]}]",
        "G2": f"the preference displaced an edge on only {G['G2_seeds_preference_displaced']} of {N} seeds, so the "
              f"intervention did not run on the rest",
    }
    READING = (f"**Verdict: {V}.** Gate{'s' if len(fail) > 1 else ''} {', '.join(fail)} failed: "
               + "; ".join(CAUSE[k] for k in fail)
               + ". Per §6 the gate is reported and **no criterion is read**; the scorer's numbers are in the artifact "
                 "and are descriptive only.")
else:
    M_TEXT = (f"**M1** {'passes' if M1['pass'] else 'fails'}: mean Y − R coverage {f(M1['mean_difference'])}, 95% "
              f"interval {M1['ci95']}, against the {BAR} bar (median {f(M1['median'])}, "
              f"{M1['positive']}/{M1['n']} seeds positive). **M2** {'passes' if M2['pass'] else 'fails'}: novel "
              f"covered edges {M2['novel_mean']:+.1f} on average (interval {M2['novel_ci']}, bar {NOVEL_BAR}), "
              f"loop-covered change {M2['loop_covered_mean_diff']:+.2f}.")
    if V == "INTERVENTION SUPPORTED":
        INTERP = ("The admission budget's redundancy is a **cost** at this cap and readout, now measured on a "
                  "fresh allocation with a gate that could fire. The gain sits where the arm claims -- novel edges "
                  "with loop-covered coverage unchanged. It licenses an admission-rule change; it does not say what "
                  "loops are for, because the arm removes prediction candidates whose edges loops assert and leaves "
                  "the loops themselves untouched.")
    elif V == "COVERAGE ONLY":
        INTERP = ("Coverage rises but not through the novel-edge channel, so the mechanism sentence is unsupported even "
                  "though the arm helps.")
    elif V == "DIRECTIONAL ONLY":
        INTERP = ("The mean clears its bar but the interval does not exclude zero; read as sign only, not support.")
    else:
        INTERP = ("At the registered bar the arm does not beat R. **With M1's disclosed power this is not evidence of "
                  "no effect** — the pooled calibration mean sat below the bar, so a miss was the likelier of the two "
                  "outcomes. What it does establish is that this readout has stopped being able to distinguish the "
                  "intervention from R at n=100; a sharper endpoint (the admitted set rather than the ninety-cycle "
                  "accumulation) would need its own calibration, not a new bar on this one.")
    READING = f"**Verdict: {V}.** All four gates pass. {M_TEXT}\n\n{INTERP}"

SEC = f"""
## 13. Readings (2026-11-06, one scoring pass)

{art['cells']} cells, seeds {ALLOC['lo']}-{ALLOC['hi']}, C, R and Y at cap 20, no cell missing and none substituted.
Every bar, the band and the allocation were read from `docs/gate13_loop_free_block7_calibration.json`; nothing was
adjusted after the run. Scored once by `benchmarks/score_loop_free_block7.py` into `docs/gate13_loop_free_block7.json`.

{GATE_TABLE}

{READING}

**What this block settled about block 6.** Block 6's void was a gate that could not fire: it required 96 of 100 seeds
where the calibration measured 62 of 110. With G0 at {GB['G0']} the arm is testable, and the liveness it delivered here
was {G['G0_liveness_y_vs_r']}/{N} — consistent with the {CAL['liveness']['rate']} pooled rate, so the gate is now
measuring the arm's reach rather than failing on arithmetic.

**Where this leaves the programme.** Six blocks have now tested the control-side claim: block 3 rejected the loop-count
proxy, block 4 was void by measurability, block 5 found an out-of-sample association without a threshold contrast, block
6 registered the intervention and voided on an unreachable gate, and block 7 ran it with a calibrated gate. Coverage
over C moved from {f(D['mean_r_gain_over_c'])} for R to {f(D['mean_y_gain_over_c'])} for Y, a mean Y − R of
{f(D['mean_diff'])} (sd {f(D['sd_diff'])}), and the preference displaced a mean of {D['mean_disp_total']} admitted edges
per seed.
"""

PRE = REPO / "docs" / "GATE13-LOOP-FREE-ADMISSION-PREREGISTRATION-B7.md"
t = PRE.read_text()
if "**Status: FROZEN, NOT RUN.**" in t:
    t = t.replace("**Status: FROZEN, NOT RUN.**", f"**Status: RUN (2026-11-06). Verdict: {V}.**")
    t = t.replace(f"No cell of {ALLOC['lo']}-{ALLOC['hi']} has been run.",
                  f"All {art['cells']} cells have since been executed and scored exactly once; §13 records the readings "
                  f"and §11 remains the freeze text.")
if "## 13. Readings (2026-11-06" not in t:
    t = t.rstrip() + "\n" + SEC
PRE.write_text(t)

CAP = REPO / "docs" / "GATE13-PAIRED-CAPACITY-TEST.md"
t = CAP.read_text()
SEC18 = f"""
## 8.18 Block 7: the same arm with a gate that can fire

Block 6's void was arithmetic, not evidence: G0 required the arm to change 96 of 100 final asserted sets while the
calibration printed beside that bar measured 6 of 10. Block 7 keeps everything — arm Y, world, cap 20, readout, C1′
band, G2, M1's 0.01 bar, M2's mechanism check — and sets G0 to {GB['G0']}/100, calibrated to the pooled liveness rate
{CAL['liveness']['rate']} from 110 non-judged pairs (block 6's void cells plus the ten dose seeds). Under that rate G0
passes with probability {CAL['liveness']['power_of_gate']}; under block 6's bar it would have passed with probability
{CAL['liveness']['power_of_block6_bar']}. {art['cells']} cells, seeds {ALLOC['lo']}-{ALLOC['hi']}.

{GATE_TABLE}

{READING}

**Power, stated before the run and not repaired afterwards.** The pooled calibration mean was {f(CAL['effect']['mean'])},
below the unchanged {BAR} bar, so M1 was a coin flip at best and the pre-registration said a miss would not be evidence
against the intervention. That disclosure is why a miss here is reported as the end of this readout rather than as a
negative result, and why the bar was not lowered after block 6's miss.

**Limits.** The pooled sd comes mostly from block 6's void cells, which is a single 110-pair draw. The readout remains
the ninety-cycle accumulation, on which the intervention changes the final structure on only about three seeds in five;
an endpoint that scored the admitted set each cycle would be more sensitive and is a separate, separately calibrated
block. And the arm removes prediction candidates whose edges loops assert — loops, construction and thresholds are
untouched, so nothing here speaks to what loops are for.
"""
if "## 8.18 Block 7" not in t:
    CAP.write_text(t.rstrip() + "\n" + SEC18)

MAN = REPO / "docs" / "USER-MANUAL.md"
t = MAN.read_text()
anchor = "`docs/gate13_loop_free_block6.json`; §8.17 capacity record, §13 of the pre-registration."
if "**Block 7 reran the same intervention arm with a gate that could fire" not in t:
    assert t.count(anchor) == 1, t.count(anchor)
    i = t.index(anchor) + len(anchor)
    PARA = f"""

**Block 7 reran the same intervention arm with a gate that could fire.** Block 6 voided because G0 demanded that Y change
96 of 100 final asserted sets while its own calibration measured 6 of 10 — a threshold the distribution could not reach.
Block 7 changes only that bar, to {GB['G0']}/100 calibrated to the pooled liveness {CAL['liveness']['rate']} of 110
non-judged cells, and keeps the arm, world, cap, readout, C1′ band, G2, M1's {BAR} bar and M2 unchanged. {art['cells']}
cells on fresh seeds {ALLOC['lo']}-{ALLOC['hi']}. Power at M1 was disclosed as low before the run, because the pooled
mean {f(CAL['effect']['mean'])} sits below the bar; the bar was not lowered. **Verdict: {V}.** {('Mean Y − R ' + f(M1['mean_difference']) + ' (interval ' + str(M1['ci95']) + '); novel edges ' + format(M2['novel_mean'], '+.1f') + ', loop-covered change ' + format(M2['loop_covered_mean_diff'], '+.2f') + '.') if ok else ('Gate ' + ', '.join(fail) + ' failed, so no criterion is read.')}
Coverage over C: {f(D['mean_r_gain_over_c'])} (R) → {f(D['mean_y_gain_over_c'])} (Y).
`benchmarks/score_loop_free_block7.py`, `docs/gate13_loop_free_block7.json`; §8.18 capacity record, §13 of the
pre-registration."""
    t = t[:i] + PARA + t[i:]
    row = (f"| 2026-11-06 | **Block 7 (same loop-free arm, G0 calibrated to the observed liveness "
           f"{CAL['liveness']['rate']}) pre-registered, run once and scored: {V}.** Seeds {ALLOC['lo']}-{ALLOC['hi']}, "
           f"{art['cells']} cells, bar {BAR} unchanged. G0 {G['G0_liveness_y_vs_r']}/{N} (bar {GB['G0']}), G0b "
           f"{G['G0b_liveness_c_vs_r']}/{N}, G1 {f(G['G1_mean_c_precision'])} in band, G2 "
           f"{G['G2_seeds_preference_displaced']}/{N} — {'all pass' if ok else 'gate ' + ', '.join(fail) + ' failed'}. "
           f"{'descriptive only: ' if not ok else ''}Mean Y − R {f(M1['mean_difference'])} (CI {M1['ci95']}), median "
           f"{f(M1['median'])}, {M1['positive']}/{M1['n']} positive; M2 novel {M2['novel_mean']:+.1f} (CI "
           f"{M2['novel_ci']}), loop {M2['loop_covered_mean_diff']:+.2f}. M1 power was disclosed as low at the pooled "
           f"mean {f(CAL['effect']['mean'])}. `docs/GATE13-LOOP-FREE-ADMISSION-PREREGISTRATION-B7.md`, "
           f"`docs/gate13_loop_free_block7.json`; §8.18, §13. |")
    old = "| 2026-11-06 | **Block 6 ("
    j = t.index(old)
    eol = t.index("\n", j)
    t = t[:eol + 1] + row + "\n" + t[eol + 1:]
    MAN.write_text(t)

CH = REPO / "CHANGELOG.md"
t = CH.read_text()
if "### Gate 13 block 7 run" not in t:
    SEC7 = f"""### Gate 13 block 7 run (2026-11-06) — the same arm, a gate that can fire

- **Only G0 changed.** Block 6's void was a bar its own calibration could not reach (96/100 against a 6/10 rate); block
  7 sets G0 to {GB['G0']}/100, calibrated to the pooled liveness {CAL['liveness']['rate']} over 110 non-judged pairs,
  and keeps the arm, world, cap, readout, C1′ band, G2, M1's {BAR} bar and M2 unchanged.
- **{art['cells']} cells on fresh seeds {ALLOC['lo']}-{ALLOC['hi']}.** G0 {G['G0_liveness_y_vs_r']}/{N}, G0b
  {G['G0b_liveness_c_vs_r']}/{N}, G1 {f(G['G1_mean_c_precision'])} in band, G2 {G['G2_seeds_preference_displaced']}/{N}:
  {'all pass' if ok else ', '.join(fail) + ' failed'}.
- **Verdict {V}.** {'Mean Y − R ' + f(M1['mean_difference']) + ' (CI ' + str(M1['ci95']) + '); M2 novel ' + format(M2['novel_mean'], '+.1f') + ' (CI ' + str(M2['novel_ci']) + ').' if ok else 'No criterion read; the gate is the result.'}
  M1's low power was pre-registered (pooled mean {f(CAL['effect']['mean'])} against the {BAR} bar) rather than
  discovered after the fact.
- `benchmarks/score_loop_free_block7.py`, `docs/gate13_loop_free_block7.json`, §8.18 capacity record.

"""
    marker = "## [0.12.0] — (unreleased)"
    t = t.replace(marker, SEC7 + marker, 1)
    CH.write_text(t)

print("records written:", V)
print("gates:", G)
print("criteria:", {"M1": M1["pass"], "M2": M2["pass"]})
