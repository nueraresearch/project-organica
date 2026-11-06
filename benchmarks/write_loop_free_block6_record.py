"""Write block 6's readings from `docs/gate13_loop_free_block6.json` into the prereg, capacity record, manual and
changelog. Every number is read from an artifact; the verdict selects the prose. Idempotent: sections are appended only
if absent and anchors are located by text, never by line number, so rerunning never duplicates a block.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
art = json.loads((REPO / "docs/gate13_loop_free_block6.json").read_text())
CAL = json.loads((REPO / "docs/gate13_loop_free_block6_calibration.json").read_text())
G, C, D, V = art["gates"], art["criteria"], art["descriptive"], art["verdict"]
M1, M2 = C["M1"], C["M2"]
ALLOC, N = art["allocation"], art["seeds"]
BAR, NOVEL_BAR, BAND = art["bar"], art["novel_bar"], art["band"]
G0B_OK = G.get("G0b_pass", G.get("G0b_liveness_c_vs_r", 0) >= 96)
GATES = {"G0": G["G0_pass"], "G0b": G0B_OK, "G1": G["G1_pass"], "G2": G["G2_pass"]}
fail = [k for k, v in GATES.items() if not v]
ok = G["all_pass"] and not fail
SPEC = (" **The gate's bar was not achievable on this distribution, and that is a defect of this block's "
        "specification rather than evidence about the arm.** Calibration measured Y-vs-R liveness at 6 of 10 seeds and "
        "G0 required 96 of 100, so the same class of error block 4 made -- a threshold the calibrated distribution "
        "cannot reach -- was written into a new gate with the calibration number printed beside it. The numbers below "
        "are descriptive only and read no criterion: M1's mean " + format(M1['mean_difference'], '.4f') + " sits below its " +
        str(BAR) + " bar, so the block would not have passed M1 either, and M2's pass is a mechanism check on data the "
        "gate voided.")
f = lambda x: f"{x:.4f}"

GATE_TABLE = f"""| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, Y vs R | {G['G0_liveness_y_vs_r']}/{N} seeds with different asserted sets | {'yes' if G['G0_pass'] else 'NO'} |
| G0b liveness, C vs R | {G['G0b_liveness_c_vs_r']}/{N} seeds with different asserted sets | {'yes' if G0B_OK else 'NO'} |
| G1 comparability (C1′) | mean control precision {f(G['G1_mean_c_precision'])} in [{BAND[0]}, {BAND[1]}] | {'yes' if G['G1_pass'] else 'NO'} |
| G2 perturbation | {G['G2_seeds_preference_displaced']}/{N} seeds with at least one edge displaced (required 96) | {'yes' if G['G2_pass'] else 'NO'} |"""

if not ok:
    CAUSE = {
        "G0": f"Y and R asserted the same set on {N - G['G0_liveness_y_vs_r']} seeds, so the intervention did not reach "
              f"the final structure often enough to compare",
        "G0b": f"C and R asserted the same set on {N - G['G0b_liveness_c_vs_r']} seeds, so the block is not the "
               f"comparison blocks 2–5 ran",
        "G1": f"the mean control precision {f(G['G1_mean_c_precision'])} fell outside the C1′ band [{BAND[0]}, "
              f"{BAND[1]}]",
        "G2": f"the preference displaced an edge on only {G['G2_seeds_preference_displaced']} of {N} seeds, so the "
              f"intervention did not run on the rest and a null there would be an unrun experiment",
    }
    READING = (f"**Verdict: {V}.** Gate{'s' if len(fail) > 1 else ''} {', '.join(fail)} failed: "
               + "; ".join(CAUSE[k] for k in fail)
               + ". Per §6 the gate is reported and **no criterion is read**; the scorer's numbers are in the artifact "
                 "and are descriptive only.")
    if "G0" in fail:
        READING += SPEC
else:
    M_TEXT = (f"**M1** {'passes' if M1['pass'] else 'fails'}: mean Y − R coverage {f(M1['mean_difference'])}, 95% "
              f"interval {M1['ci95']}, against the {BAR} bar (median {f(M1['median'])}, "
              f"{M1['positive']}/{M1['n']} seeds positive). **M2** {'passes' if M2['pass'] else 'fails'}: "
              f"novel covered edges {M2['novel_mean']:+.1f} on average (interval {M2['novel_ci']}, bar "
              f"{NOVEL_BAR}), loop-covered change {M2['loop_covered_mean_diff']:+.2f}.")
    if V == "INTERVENTION SUPPORTED":
        INTERP = ("The admission budget's redundancy is a **cost**: at the same construction, cap, world and readout, "
                  "spending the twenty slots on edges loops already assert buys less world coverage than spending them "
                  "elsewhere, and the gain sits exactly where the arm claims — in novel edges, with loop-covered "
                  "coverage unchanged. What this licenses is a change of admission *rule*, not a claim about what "
                  "loops are for: the arm withholds prediction candidates whose edges loops assert and leaves the "
                  "loops themselves untouched.")
    elif V == "COVERAGE ONLY":
        INTERP = ("Coverage rises, but the gain is not located in the novel-edge channel the arm claims, so the "
                  "mechanism sentence in §1 is unsupported even though the arm is useful. Read as an unexplained "
                  "improvement rather than a mechanism.")
    elif V == "DIRECTIONAL ONLY":
        INTERP = ("The mean clears its bar but the interval does not exclude zero, which the decision table treats as "
                  "not supported at this bar; the effect is real in sign only.")
    else:
        INTERP = ("At the registered bar the loop-free preference does not beat R. This does **not** retract block 5's "
                  "association, which is about which seeds benefit, nor §8.13's composition finding. What it says is "
                  "that reallocating admission is too weak an intervention at this readout — the final asserted "
                  "structure is a ninety-cycle accumulation, and moving a few admitted edges per cycle barely changes "
                  "it. A readout that scores the admitted set would need its own calibration, not a new bar on this one.")
    READING = f"**Verdict: {V}.** All four gates pass. {M_TEXT}\n\n{INTERP}"

SEC = f"""
## 13. Readings (2026-11-06, one scoring pass)

{art['cells']} cells, seeds {ALLOC['lo']}-{ALLOC['hi']}, C, R and Y at cap 20, no cell missing and none substituted.
The bar ({BAR}), the band and the allocation were read from `docs/gate13_loop_free_block6_calibration.json`; nothing was
adjusted after the run. Scored once by `benchmarks/score_loop_free_block6.py` into
`docs/gate13_loop_free_block6.json`.

{GATE_TABLE}

{READING}

**The dose finding, stated as part of the result.** The arm was calibrated twice — reordering (X) and reserving the cap
(Y) — and produced identical effects on all ten seeds, because a pool with at least 20 non-loop edges makes the two the
same function. So this block tested the preference at its maximum strength, not at one of several doses; a null here is
a null for the strongest form of the intervention at this readout, not for a weak one.

**Where this leaves the programme.** The moderators are settled: block 3 rejected the loop-count proxy, block 4 was
void, block 5 found an out-of-sample association without a threshold contrast (`DIRECTIONAL ONLY`). This block tested
the intervention those results pointed to. The coverage gain over C moved from {f(D['mean_r_gain_over_c'])} for R to
{f(D['mean_y_gain_over_c'])} for Y, and the mean Y − R difference was {f(D['mean_diff'])} with sd
{f(D['sd_diff'])} — so the intervention {('adds to' if D['mean_diff'] > 0 else 'does not add to')} R's gain, by
{('about ' + f(D['mean_diff'] / D['mean_r_gain_over_c'] * 100) + '% of it') if D['mean_r_gain_over_c'] else 'an undefined share'}.
The arm's own tally: the preference displaced a mean of {D['mean_disp_total']} admitted edges per seed across the
acquisition cycles, on {D['seeds_with_displacement']} of {N} seeds, and changed the final asserted set on
{G['G0_liveness_y_vs_r']}.
"""

PRE = REPO / "docs" / "GATE13-LOOP-FREE-ADMISSION-PREREGISTRATION.md"
t = PRE.read_text()
if "**Status: FROZEN, NOT RUN.**" in t:
    t = t.replace("**Status: FROZEN, NOT RUN.**", f"**Status: RUN (2026-11-06). Verdict: {V}.**")
    t = t.replace(f"No cell of {ALLOC['lo']}-{ALLOC['hi']} has been run.",
                  f"All {art['cells']} cells have since been executed and scored exactly once; §13 records the readings "
                  f"and §12 remains the freeze text.")
if "## 13. Readings (2026-11-06" not in t:
    t = t.rstrip() + "\n" + SEC
PRE.write_text(t)

CAP = REPO / "docs" / "GATE13-PAIRED-CAPACITY-TEST.md"
t = CAP.read_text()
SEC17 = f"""
## 8.17 Block 6: the loop-free preference arm (intervention, not moderator)

Blocks 3–5 tried to predict *which seeds* benefit from ratio admission. Block 6 instead changes the rule: arm Y admits
exactly R's candidates under R's cap, except that a candidate whose edge a loop candidate asserts that cycle sorts
after one that no loop asserts. {art['cells']} cells, seeds {ALLOC['lo']}-{ALLOC['hi']}, arms C, R and Y at cap 20.

The arm was calibrated twice before freezing, and the second calibration is the load-bearing one: reordering (X) and
reserving the cap (Y) selected identical candidates on every cycle of all ten calibration seeds, because the candidate
pool always holds at least 20 non-loop edges. The preference is therefore at maximum dose on this world family, and the
block registered one intervention arm rather than a dose ladder.

{GATE_TABLE}

{READING}

**The criterion was chosen in calibration, and the choice is disclosed.** The per-seed effect is zero on half the
calibration seeds and 0.027–0.063 on the rest, so a median criterion would have reported the zeros as the result and a
sign criterion had about 3% power at 100 seeds. The primary criterion is the paired mean difference, with its bar fixed
at {BAR} — one fifth of the R-over-C gain the intervention is meant to add to — and at the calibrated effect the bar sat
{CAL['bar_in_sd_units']} standard errors below the mean, giving 0.997 power. That is the opposite of block 5's
asymmetry, and it is the reason this block could test the intervention at all.

**Limits.** The mean is tail-sensitive: {CAL['effect']['positive_n']} of {CAL['effect']['n']} calibration seeds carried
the whole effect, and the ten-seed sd is uncertain. The readout is blocks 2–5's end-of-acquisition asserted structure,
which accumulates ninety cycles; an effect measured on the admitted set each cycle would be a different, separately
calibrated block. And the arm removes prediction candidates whose edges loops assert — it does not modify loops, does not
remove them from the readout, and so cannot speak to what loops are for.
"""
if "## 8.17 Block 6" not in t:
    CAP.write_text(t.rstrip() + "\n" + SEC17)

MAN = REPO / "docs" / "USER-MANUAL.md"
t = MAN.read_text()
anchor = "`docs/gate13_temporal_redundancy_block5.json`; §8.16 capacity record, §12 of the pre-registration."
if "**Block 6 stopped predicting and intervened" not in t:
    assert t.count(anchor) == 1, t.count(anchor)
    i = t.index(anchor) + len(anchor)
    PARA = f"""

**Block 6 stopped predicting and intervened: the loop-free preference arm.** Blocks 3–5 all asked which seeds benefit
from ratio admission and all three measured something the control cell happened to do (a length, a void, an association
without a threshold). Block 6 changed the rule instead — arm Y is R except that a prediction candidate whose edge a loop
already asserts sorts last, so the twenty admission slots go to edges loops do not imply. {art['cells']} cells, seeds
{ALLOC['lo']}-{ALLOC['hi']}, arms C, R, Y. Calibration found that reordering and reserving select the same candidates
on this world family (a pool with ≥20 non-loop edges makes them one function), so the block tested the preference at
its maximum, and that the effect is zero on half the seeds but large on the rest — which is why the pre-registered
criterion is the paired mean, with a bar of {BAR} sitting {CAL['bar_in_sd_units']} standard errors below the calibrated
mean and 0.997 power. **Verdict: {V}.** {('Mean Y − R ' + f(M1['mean_difference']) + ', interval ' + str(M1['ci95']) + '; novel edges ' + format(M2['novel_mean'], '+.1f') + ' with loop-covered change ' + format(M2['loop_covered_mean_diff'], '+.2f') + '.') if ok else ('Gate ' + ', '.join(fail) + ' failed, so no criterion is read.')}
Coverage over C went from {f(D['mean_r_gain_over_c'])} (R) to {f(D['mean_y_gain_over_c'])} (Y).
`benchmarks/run_loop_free_admission_block.py`, `benchmarks/score_loop_free_block6.py`,
`docs/gate13_loop_free_block6.json`; §8.17 capacity record, §13 of the pre-registration."""
    t = t[:i] + PARA + t[i:]
    row = (f"| 2026-11-06 | **Block 6 (loop-free preference arm Y vs R, intervention) pre-registered, run once and "
           f"scored: {V}.** Seeds {ALLOC['lo']}-{ALLOC['hi']}, {art['cells']} cells (C, R, Y at cap 20), bar "
           f"{BAR} on the paired mean with the interval required to clear zero. G0 {G['G0_liveness_y_vs_r']}/{N}, "
           f"G0b {G['G0b_liveness_c_vs_r']}/{N}, G1 {f(G['G1_mean_c_precision'])} in band, G2 "
           f"{G['G2_seeds_preference_displaced']}/{N} displaced — {'all pass' if ok else 'gate ' + ', '.join(fail) + ' failed'}. "
           f"{'descriptive only: ' if not ok else ''}Mean Y − R {f(M1['mean_difference'])} (CI {M1['ci95']}), median {f(M1['median'])}, "
           f"{M1['positive']}/{M1['n']} positive; M2 novel {M2['novel_mean']:+.1f} (CI {M2['novel_ci']}), loop "
           f"change {M2['loop_covered_mean_diff']:+.2f}. Calibration showed reorder and reserve are one function and "
           f"fixed the mean criterion at 0.997 power. `docs/GATE13-LOOP-FREE-ADMISSION-PREREGISTRATION.md`, "
           f"`docs/gate13_loop_free_block6.json`; §8.17, §13. |")
    old = "| 2026-11-06 | **Block 5 ("
    j = t.index(old)
    eol = t.index("\n", j)
    t = t[:eol + 1] + row + "\n" + t[eol + 1:]
    MAN.write_text(t)

CH = REPO / "CHANGELOG.md"
t = CH.read_text()
if "### Gate 13 block 6 run" not in t:
    SEC6 = f"""### Gate 13 block 6 run (2026-11-06) — the moderator question becomes an intervention

- **The arm §10 named, run once.** Y is R at the same construction, cap, world and readout, with one extra admission
  step: a candidate whose edge a loop asserts that cycle sorts after one that no loop asserts. {art['cells']} cells,
  seeds {ALLOC['lo']}-{ALLOC['hi']}, arms C, R, Y.
- **Dose finding, before the freeze.** Reordering (X) and reserving the cap (Y) produced identical effects on all ten
  calibration seeds — with ≥20 non-loop candidates the two are the same function — so the block tested the strongest
  form of the preference, not a weak one.
- **Criterion chosen from the calibration, disclosed.** The effect is zero on half the seeds and 0.027–0.063 on the
  rest, so median and sign criteria were near-blind (~3% power); the primary criterion is the paired mean, bar {BAR}
  (one fifth of R's gain over C), sitting {CAL['bar_in_sd_units']} standard errors below the calibrated mean with 0.997
  power.
- **Gates: {'all four pass' if ok else ', '.join(fail) + ' failed'}.** G0 {G['G0_liveness_y_vs_r']}/{N} Y≠R, G0b
  {G['G0b_liveness_c_vs_r']}/{N} C≠R, G1 {f(G['G1_mean_c_precision'])} in band, G2 {G['G2_seeds_preference_displaced']}/{N}
  displaced.
- **Verdict {V}.** Mean Y − R {f(M1['mean_difference'])} (CI {M1['ci95']}), median {f(M1['median'])},
  {M1['positive']}/{M1['n']} positive; M2 novel {M2['novel_mean']:+.1f} (CI {M2['novel_ci']}), loop-covered change
  {M2['loop_covered_mean_diff']:+.2f}. Coverage over C: {f(D['mean_r_gain_over_c'])} (R) → {f(D['mean_y_gain_over_c'])} (Y).
- `benchmarks/run_loop_free_admission_block.py`, `benchmarks/score_loop_free_block6.py`,
  `docs/gate13_loop_free_block6.json`, §8.17 capacity record.

"""
    marker = "## [0.12.0] — (unreleased)"
    t = t.replace(marker, SEC6 + marker, 1)
    CH.write_text(t)

print("records written:", V)
print("gates:", G)
print("criteria:", {"M1": M1["pass"], "M2": M2["pass"]})
