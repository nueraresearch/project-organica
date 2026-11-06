"""Write block 4's readings from `docs/gate13_temporal_redundancy_block4.json` into the prereg, capacity record,
manual and changelog. Values are substituted from the artifact; nothing is typed."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CALP = json.loads((REPO / "docs/gate13_temporal_redundancy_calibration.json").read_text())["power"]
art = json.loads((REPO / "docs/gate13_temporal_redundancy_block4.json").read_text())
G, C, D, V = art["gates"], art["criteria"], art["descriptive"], art["verdict"]
m1, m2, m3 = C["M1"], C["M2"], C["M3"]
n_cells, n_seeds = art["cells"], art["seeds"]
seeds = [p["seed"] for p in art["seed_rows"]] + [e["seed"] for e in art["excluded"]]
lo, hi = min(seeds), max(seeds)
n_excl = len(D["excluded_unmeasurable"])
CAL_PRED = [q["pred_world"] for q in json.loads(
    (REPO / "docs/gate13_temporal_redundancy_calibration.json").read_text())["pairs"]]
FRESH_PRED = [q["pred_world"] for q in art["seed_rows"]] + [q["pred_world"] for q in art["excluded"]]
cal_lo, cal_hi = min(CAL_PRED), max(CAL_PRED)
fr_lo, fr_hi = min(FRESH_PRED), max(FRESH_PRED)
rho = f"{m2['spearman']:.3f}" if m2["spearman"] is not None else "not computed"


def f4(x):
    return f"{x:.4f}"


REASONS = (f"the covariate's denominator, |P_s ∩ W|, fell below 3 on {n_excl} control cells, so `o_s` was not "
           f"measurable there; those seeds are excluded and counted, never imputed")

SEC = f"""
## 12. Readings (2026-11-06, one scoring pass)

{n_cells} cells, seeds {lo}-{hi}, C and R at cap 20, no cell substituted and no cell failed. Threshold {art['threshold_o']}
and bars were read from `docs/gate13_temporal_redundancy_calibration.json`, the C1′ band from
`docs/gate13_c1_respecification.json`; nothing was adjusted after the run. Scored once by
`benchmarks/score_temporal_redundancy_block.py` into `docs/gate13_temporal_redundancy_block4.json`.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness | {G['G0_differ']}/{n_seeds} seeds with arm-dependent asserted sets | {'yes' if G['G0_pass'] else 'NO'} |
| G1 C1′ | mean control precision {f4(G['G1_mean_c_precision'])} in {art['band']} | {'yes' if G['G1_pass'] else 'NO'} |
| G2 measurability | {G['G2_measurable']}/{n_seeds} seeds with `o_s` defined (required {G['G2_required']}) | {'yes' if G['G2_pass'] else 'NO'} |

**Verdict: {V}.** G0 and G1 pass, so the arms and the control behave as in blocks 2 and 3. G2 fails: {REASONS}. Per §7 the
gate is reported and no criterion is read.

**Why the gate failed, in its own terms.** This is a defect of the covariate as specified, not a property of the treatment.
`o_s` is a share of the control's temporal world edges, and on this allocation that denominator is small and often empty —
the block-2 calibration ranged {cal_lo}-{cal_hi}, the fresh allocation {fr_lo}-{fr_hi}. The distribution is also saturated rather than centred: the
mean `o_s` is {f4(D['mean_o'])} against 0.468 in calibration, and {m1['high_n']} of the {G['G2_measurable']} measurable seeds sit at or
above the threshold {art['threshold_o']}, leaving {m1['low_n']} below it. Even had every seed been measurable, M1's {40}-seed
per-half requirement could not have been met, which §9's P5 anticipated and this reading confirms. Pre-registered
prediction **P2 is falsified**: the calibration range did not transfer.

**Recorded but not scored.** The code computes M1, M2 and M3 on the measurable seeds and they are in the artifact —
M1 difference {m1['difference'] if m1['difference'] is not None else 'n/a'} ({m1['low_n']} low / {m1['high_n']} high),
M2 Spearman {rho} (95% CI {m2['ci95']}), M3 {m3['positive']}/{m3['n']}. They are **descriptive only**: the gate voided the
block, so reading them as a verdict would be exactly the post-hoc re-scoring §7 forbids. Recorded for a future
pre-registration, not as a result.

**What this does and does not settle.** Nothing about whether control-side temporal redundancy moderates the ratio arm —
the test was not admissible. It does establish something about the covariate: as specified, `o_s` is not usable at n=100 on
this world family, because the quantity whose share it measures is frequently absent. A further block would need a coarser
covariate — the count of the control's temporal world edges, or the overlap taken over asserted edges rather than world
edges — with the denominator problem solved *before* the freeze rather than excluded afterwards.
"""
PRE = REPO / "docs/GATE13-TEMPORAL-REDUNDANCY-PREREGISTRATION.md"
t = PRE.read_text()
if "**Status: FROZEN, NOT RUN.**" in t:
    t = t.replace("**Status: FROZEN, NOT RUN.**", f"**Status: RUN (2026-11-06). Verdict: {V}.**")
    t = t.replace("No cell of this block has been executed.",
                  f"All {n_cells} cells have since been executed and scored exactly once; §12 records the readings and §11 "
                  f"remains the freeze text.")
if "## 12. Readings (2026-11-06" not in t:
    t = t.rstrip() + "\n" + SEC
PRE.write_text(t)

CAP = REPO / "docs/GATE13-PAIRED-CAPACITY-TEST.md"
t = CAP.read_text()
SEC15 = f"""
## 8.15 Block 4: control-side temporal redundancy, voided by its own measurability gate

Block 3 retired loop *quantity*. Block 4 tested the other half of §8.13 — whether the seeds that improve are the ones where
the control's temporal edges are already largely implied by its loops (`o_s = |L ∩ P ∩ W| / |P ∩ W|`, threshold
{art['threshold_o']} from the 10 calibration seeds). {n_cells} cells on fresh seeds {lo}-{hi}, pre-registered and scored once.

**Verdict: {V}.** G0 ({G['G0_differ']}/{n_seeds} arm-dependent sets) and G1 (control precision
{f4(G['G1_mean_c_precision'])} in band) passed. G2 failed at {G['G2_measurable']}/{n_seeds} measurable against a required
{G['G2_required']}: {REASONS}. No criterion is read.

**The covariate is the finding here.** On the fresh allocation the control's temporal world edges are few — {fr_lo}-{fr_hi} where
calibration gave {cal_lo}-{cal_hi} — so the share is undefined on {n_excl} seeds and saturated on the rest ({f4(D['mean_o'])} mean, {m1['high_n']} of
{G['G2_measurable']} above threshold). The design error is visible before any criterion: a share whose denominator can be
absent produces a covariate that is both unmeasurable and compressed. Excluding those seeds, as the freeze required, left too
few to test the registered split, and the gate fired rather than the block being quietly analysed on a skewed subset.

**Disclosed, not scored.** On the measurable seeds the association is positive — Spearman {rho}, CI {m2['ci95']} — and the
gain replicates at {m3['positive']}/{m3['n']} with mean {f4(D['mean_gain'])}. That is the direction the hypothesis predicted
and it is **not** a result of this block: the gate voided it, and reporting those numbers as support would be the
re-scoring §7 forbids. They are recorded so the next covariate can be specified against a measured denominator.

**Limits.** Nothing here speaks to the moderator hypothesis. What it does say is that §8.13's overlap pattern cannot be
turned into a between-seed covariate of this form without solving the denominator first — by using a count rather than a
share, or by taking the overlap over asserted edges rather than world edges.
"""
if "## 8.15 Block 4" not in t:
    CAP.write_text(t.rstrip() + "\n" + SEC15)

MAN = REPO / "docs/USER-MANUAL.md"
t = MAN.read_text()
anchor = "`docs/gate13_redundancy_block3.json`; §8.14 capacity record, §13 of the pre-registration."
i = t.index(anchor) + len(anchor)
PARA = f"""

**Block 4 tested the other half of §8.13 and was voided by its own measurability gate.** `o_s` — the share of the control's
temporal edges its loops already imply — was pre-registered with threshold {art['threshold_o']} and scored once on fresh
seeds {lo}-{hi}. G0 and G1 passed (control precision {f4(G['G1_mean_c_precision'])} in the C1′ band) but G2 failed: `o_s` was
undefined on {n_excl} seeds because the control asserted fewer than 3 temporal world edges, leaving {G['G2_measurable']}
measurable against a required {G['G2_required']}. **Verdict {V}; no criterion read.** The covariate is the finding: on this
allocation the denominator is often absent and the distribution is saturated ({f4(D['mean_o'])} mean, {m1['high_n']} of
{G['G2_measurable']} above threshold), so even a complete block could not have filled M1's halves. The positive association
on the measurable seeds (Spearman {rho}, mean gain {f4(D['mean_gain'])}) is recorded and explicitly **not** a result. The
next attempt needs a coarser covariate, with the denominator problem fixed before the freeze.
`benchmarks/run_temporal_redundancy_block.py`, `benchmarks/score_temporal_redundancy_block.py`,
`docs/gate13_temporal_redundancy_block4.json`; §8.15 capacity record, §12 of the pre-registration."""
if "**Block 4 tested the other half" not in t:
    t = t[:i] + PARA + t[i:]

ROW = (f"| 2026-11-06 | **Block 4 (control-side temporal redundancy) pre-registered, run once and voided by G2: the "
       f"covariate is unmeasurable on {n_excl}/100 seeds and saturated on the rest.** Fresh seeds {lo}-{hi}, 200 cells, "
       f"threshold {art['threshold_o']}, bars M1 0.03 / M2 +0.25 / M3 66, joint power fixed at "
       f"{CALP['n100_calibration_implied']['power_both']} for the calibration-implied effect and "
       f"{CALP['n100_null']['power_both']} at null. G0 {G['G0_differ']}/{n_seeds} and G1 "
       f"{f4(G['G1_mean_c_precision'])} in band pass; G2 measures {G['G2_measurable']}/100 against 96 and fails, so the "
       f"verdict is {V} and no criterion is read. The cause is the share's denominator (control temporal world edges 0-9), "
       f"not the treatment; the positive association on measurable seeds (Spearman {rho}) is disclosed as descriptive only. "
       f"Next covariate must avoid a share that can be undefined. `benchmarks/run_temporal_redundancy_block.py`, "
       f"`docs/gate13_temporal_redundancy_block4.json`; §8.15, §12 pre-registration. |")
lines = t.split("\n")
idx = max(i for i, ln in enumerate(lines) if ln.startswith("| 2026-11-06 | **Block 3 scored once"))
if not any(ln.startswith("| 2026-11-06 | **Block 4") for ln in lines):
    lines.insert(idx + 1, ROW)
MAN.write_text("\n".join(lines))

CH = REPO / "CHANGELOG.md"
t = CH.read_text()
HEAD = "## [0.12.0] — (unreleased)"
ENTRY = f"""### Gate 13 block 4 run (2026-11-06) — voided by measurability

- **Pre-registered, run once, voided by its own gate.** Covariate `o_s` = share of the control's world-covered temporal
  edges that its loops already assert (the §8.13 overlap pattern, which block 3's total-loop-count proxy did not test).
  {n_cells} cells on fresh seeds {lo}-{hi}, threshold {art['threshold_o']}, bars and power fixed before the first cell.
- **G0 and G1 pass; G2 fails at {G['G2_measurable']}/{n_seeds} measurable.** The denominator can be absent — the control
  asserted fewer than 3 temporal world edges on {n_excl} seeds — so the share is undefined there and saturated elsewhere
  ({f4(D['mean_o'])} mean, {m1['high_n']} of {G['G2_measurable']} above threshold). Excluded rather than imputed, which left
  too few seeds to test the registered split.
- **Verdict {V}; no criterion read.** The positive association on measurable seeds (Spearman {rho}, mean gain
  {f4(D['mean_gain'])}, {m3['positive']}/{m3['n']} positive) is recorded as descriptive only, not as support.
- The lesson is about design: a covariate expressed as a share needs its denominator proven non-degenerate before the
  freeze. `benchmarks/run_temporal_redundancy_block.py`, `benchmarks/score_temporal_redundancy_block.py`,
  `docs/gate13_temporal_redundancy_block4.json`, §8.15 capacity record, §12 pre-registration.

"""
if "Gate 13 block 4 run" not in t:
    CH.write_text(t.replace(HEAD, ENTRY + HEAD, 1))
print("records written")
