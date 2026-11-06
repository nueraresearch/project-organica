"""Write block 3's readings from `docs/gate13_redundancy_block3.json` into the prereg, capacity record, manual, changelog."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
art = json.loads((REPO / "docs/gate13_redundancy_block3.json").read_text())
g, c, d, V = art["gates"], art["criteria"], art["descriptive"], art["verdict"]
m1, m2, m3 = c["M1"], c["M2"], c["M3"]
n, per_seed = art["cells"], art["seeds"]
seeds = [row["seed"] for row in per_seed]


def f4(x):
    return f"{x:.4f}"


# ---------------------------------------------------------------- prereg ----
PRE = REPO / "docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md"
t = PRE.read_text()
if "**Status: FROZEN, NOT RUN.**" in t:
    t = t.replace("**Status: FROZEN, NOT RUN.**", f"**Status: RUN (2026-11-06). Verdict: {V}.**")
    t = t.replace("No cell of this block has been executed.",
                  f"All {n} cells have since been executed and scored exactly once; §13 records the readings and §11 remains the freeze text.")

SEC13 = f"""
## 13. Readings (2026-11-06, one scoring pass)

{n} cells, seeds {seeds[0]}-{seeds[-1]}, C and R at cap {art['allocation']['cap'] if 'cap' in art['allocation'] else 20},
no cell substituted and no cell failed. Threshold {art['threshold_r']} and bars were read from
`docs/gate13_redundancy_moderator_calibration.json`, the C1′ band from `docs/gate13_c1_respecification.json`; nothing was
adjusted after the run. Scored once, by `benchmarks/score_redundancy_block.py`, into
`docs/gate13_redundancy_block3.json`.

**Gates** — all three pass, so the block is admissible and the criteria below are read as a test, not as a void.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness | {g['G0_differ']}/{len(seeds)} seeds with arm-dependent asserted sets | {'yes' if g['G0_pass'] else 'NO'} |
| G1 C1′ | mean control precision {f4(g['G1_mean_c_precision'])} in [{g['G1_band'][0]}, {g['G1_band'][1]}] | {'yes' if g['G1_pass'] else 'NO'} |
| G2 loop invariance | {g['G2_loop_hashes_equal']}/{len(seeds)} seeds with identical loop edge sets across arms | {'yes' if g['G2_pass'] else 'NO'} |

**Criteria** — evaluated in the registered order, once.

| Criterion | Reading | Bar | Pass |
| --- | --- | --- | --- |
| M1 half-split | low `r` (n={m1['low_n']}) median {f4(m1['low_median'])} vs high (n={m1['high_n']}) {f4(m1['high_median'])}; difference {f4(m1['median_difference'])} | ≥ +{m1['bar']} | {'yes' if m1['pass'] else 'no'} |
| M2 monotone | Spearman {m2['spearman']}, 95% bootstrap CI [{m2['ci95'][0]}, {m2['ci95'][1]}] | ≤ {m2['bar']} | {'yes' if m2['pass'] else 'no'} |
| M3 replication (secondary) | {m3['positive']}/{m3['n']} seeds with a positive gain | ≥ {m3['bar']} | {'yes' if m3['pass'] else 'no'} |

**Verdict: {V}.**

M3 passes: the ratio arm's gain replicates again in a fresh allocation of 100 seeds, {m3['positive']} of them positive,
mean gain {f4(d['mean_gain'])} coverage and median {f4(d['median_gain'])}, against control coverage
{f4(d['mean_c_coverage'])} and ratio coverage {f4(d['mean_r_coverage'])}. M1 and M2 both fail. Pre-run loop redundancy does
not predict where the arm pays: the low-redundancy half gains *more* than the high-redundancy half
({f4(m1['low_median'])} vs {f4(m1['high_median'])}, difference {f4(m1['median_difference'])}, opposite to the registered
sign), and the rank association is {m2['spearman']} with an interval that spans zero and excludes the registered direction
(the bar, {m2['bar']}, lies outside the interval). The covariate spans `r` {f4(d['r_min'])} to {f4(d['r_max'])} across the
100 seeds, so the test was not starved of variation.

Two limits are recorded rather than smoothed over. First, M1 as specified requires at least 40 seeds per half and the
allocation produced {m1['low_n']}/{m1['high_n']} against the fixed threshold {art['threshold_r']}, so M1 is not satisfied on
size as well as on sign; its point estimate points the wrong way regardless, so the failure does not rest on the split.
Second, §8 fixed joint power at 0.327 under a mechanism-sized effect and 0.002 under no association, so this miss is
evidence against the redundancy mechanism — moderate against a mechanism that shifts the gain by ~0.10 across the covariate,
weak against a small one. It does not weaken the replication finding, which is M3's separate claim.

What this does and does not license, per §10: the redundancy story is retired as the explanation for the 20/5 split. The
§8.13 fact stands unchanged — the arm's effect is carried by `prediction_candidate` edges, not loops — and this block adds
that the *quantity* of pre-existing loop coverage does not predict the payoff. The question the 20/5 split posed is
therefore open again, and a further block would need a different pre-treatment covariate, not a re-run of this one.
"""
if "## 13. Readings (2026-11-06" not in t:
    t = t.rstrip() + "\n" + SEC13
PRE.write_text(t)

# -------------------------------------------------------------- capacity ----
CAP = REPO / "docs/GATE13-PAIRED-CAPACITY-TEST.md"
t = CAP.read_text()
SEC814 = f"""
## 8.14 Block 3: loop redundancy as a moderator, on a fresh allocation

The 20/5 split survived §8.11-§8.13's three structural explanations, so block 3 tested the strongest remaining one on
seeds that had never been used: that the arm pays only where the pre-run loops leave room. {n} cells, seeds
{seeds[0]}-{seeds[-1]}, C and R at cap 20, pre-registered with its bars, threshold ({art['threshold_r']}), power and
decision table fixed before the first cell (`docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md`), and scored once.

Gates held: {g['G0_differ']}/{len(seeds)} seeds had arm-dependent asserted sets, mean control precision
{f4(g['G1_mean_c_precision'])} sat inside the C1′ band [{g['G1_band'][0]}, {g['G1_band'][1]}], and the loop edge sets were
identical across arms on {g['G2_loop_hashes_equal']}/{len(seeds)} seeds, so the covariate is arm-independent as designed.

| Criterion | Reading | Bar | Pass |
| --- | --- | --- | --- |
| M1 half-split | low `r` (n={m1['low_n']}) {f4(m1['low_median'])} vs high (n={m1['high_n']}) {f4(m1['high_median'])}; difference {f4(m1['median_difference'])} | ≥ +{m1['bar']} | no |
| M2 monotone | Spearman {m2['spearman']}, CI [{m2['ci95'][0]}, {m2['ci95'][1]}] | ≤ {m2['bar']} | no |
| M3 replication | {m3['positive']}/{m3['n']} positive | ≥ {m3['bar']} | yes |

**Verdict: {V}.** The gain itself is now a three-block fact: {m3['positive']}/100 fresh seeds improve, mean
{f4(d['mean_gain'])} coverage. Its moderator is not. Where pre-run loops cover more of the world the arm does slightly
*worse* ({f4(m1['high_median'])} vs {f4(m1['low_median'])}), and the rank correlation is {m2['spearman']} — the registered
threshold of {m2['bar']} is outside the interval, not merely unattained. Since §8 fixed joint power at 0.327 for a
mechanism-sized effect, a miss is evidence against that mechanism, and the redundancy explanation is retired.

**Limits.** Only {m1['low_n']} seeds fall below the fixed threshold, because `r` in this allocation sits higher than in
calibration ({f4(d['r_min'])}-{f4(d['r_max'])}), so M1 is additionally undersized on its low half; the sign is wrong
either way. The covariate was measured on the control arm before the ratio arm was scored, but both arms share the seed's
world, so this tests redundancy as a *predictor*, not as an intervention. Nothing here revises §8.11-§8.13 or the earlier
verdicts.
"""
if "## 8.14 Block 3" not in t:
    CAP.write_text(t.rstrip() + "\n" + SEC814)

# ---------------------------------------------------------------- manual ----
MAN = REPO / "docs/USER-MANUAL.md"
t = MAN.read_text()
anchor = "`docs/gate13_redundancy_moderator_calibration.json`."
i = t.index(anchor + "\n")
PARA = f"""
**Block 3 ran, once, and retired the redundancy explanation.** All {n} pre-registered cells executed on fresh seeds
{seeds[0]}-{seeds[-1]}; the gates held (control precision {f4(g['G1_mean_c_precision'])} inside the C1′ band, loop edge
sets identical across arms on {g['G2_loop_hashes_equal']}/{len(seeds)} seeds), and the scoring returned
**{V}**. Pre-run loop redundancy does not predict the ratio arm's payoff: the high-redundancy half gains
{f4(m1['high_median'])} against {f4(m1['low_median'])} for the low half, the sign opposite to the registered one, and the
rank correlation is {m2['spearman']} (CI [{m2['ci95'][0]}, {m2['ci95'][1]}]) where the bar was {m2['bar']}. The gain itself
replicated a third time — {m3['positive']}/100 seeds positive, mean {f4(d['mean_gain'])} coverage — so what fails is the
explanation, not the effect. `benchmarks/score_redundancy_block.py`, `benchmarks/write_redundancy_block3_record.py`,
`docs/gate13_redundancy_block3.json`; §8.14 capacity record, §13 of the pre-registration.
"""
if "**Block 3 ran, once, and retired the redundancy explanation.**" not in t:
    t = t[: i + len(anchor) + 1] + PARA + t[i + len(anchor) + 1:]

ROW = (f"| 2026-11-06 | **Block 3 scored once on a fresh allocation: the ratio gain replicates (88/100, +0.0442 coverage) "
       f"but loop redundancy does not predict it — moderator retired.** {n} pre-registered cells, seeds "
       f"{seeds[0]}-{seeds[-1]}, C and R at cap 20; gates held (control precision {f4(g['G1_mean_c_precision'])} in band, "
       f"loop sets identical on {g['G2_loop_hashes_equal']}/100 seeds). M1 failed and pointed the wrong way "
       f"({f4(m1['low_median'])} low vs {f4(m1['high_median'])} high), M2 failed with Spearman {m2['spearman']} "
       f"(CI [{m2['ci95'][0]}, {m2['ci95'][1]}], bar {m2['bar']} excluded), M3 passed. Joint power was fixed at 0.327 for a "
       f"mechanism-sized effect, so the miss is evidence against it. Verdict MODERATOR NOT SUPPORTED; no earlier verdict "
       f"moved. `benchmarks/score_redundancy_block.py`, `docs/gate13_redundancy_block3.json`; §8.14 capacity record, §13 "
       f"pre-registration. |")
lines = t.split("\n")
idx = max(i for i, ln in enumerate(lines) if "gate13_redundancy_moderator_calibration.json`. |" in ln)
if not any("**Block 3 scored once on a fresh allocation" in ln for ln in lines):
    lines.insert(idx + 1, ROW)
MAN.write_text("\n".join(lines))

# ------------------------------------------------------------- changelog ----
CH = REPO / "CHANGELOG.md"
t = CH.read_text()
HEAD = "## [0.12.0] — (unreleased)"
ENTRY = f"""### Gate 13 block 3 run (2026-11-06) — redundancy moderator retired

- **Scored once, exactly as pre-registered.** {n} cells on the first unused 100-seed run ({seeds[0]}-{seeds[-1]}), C and R
  at cap 20, bars and threshold ({art['threshold_r']}) fixed before the first cell, `loop_hash` recorded under Amendment 1
  so G2 could compare loop attribution across arms rather than by count.
- **Gates held.** Arms differed on {g['G0_differ']}/100 seeds, mean control precision {f4(g['G1_mean_c_precision'])} sat
  inside the C1′ band [{g['G1_band'][0]}, {g['G1_band'][1]}], loop edge sets were identical on
  {g['G2_loop_hashes_equal']}/100 seeds.
- **Verdict: {V}.** M3 passed — {m3['positive']}/100 seeds gain, mean {f4(d['mean_gain'])} coverage — so the effect
  replicates for the third time, but M1 failed in the registered direction ({f4(m1['low_median'])} low vs
  {f4(m1['high_median'])} high redundancy, bar +{m1['bar']}) and M2 failed (Spearman {m2['spearman']},
  CI [{m2['ci95'][0]}, {m2['ci95'][1]}], bar {m2['bar']} outside it). Pre-run loop redundancy is not the moderator, and the
  20/5 split is open again to a different covariate; no earlier verdict moved.
- `benchmarks/score_redundancy_block.py`, `benchmarks/write_redundancy_block3_record.py`,
  `docs/gate13_redundancy_block3.json`, §8.14 capacity record, §12-§13 pre-registration.

"""
if "Gate 13 block 3 run (2026-11-06)" not in t:
    CH.write_text(t.replace(HEAD, ENTRY + HEAD, 1))
print("records written")
