"""Block-6 calibration: pooled dose evidence, the mean criterion, its bar and its power.

The intervention was calibrated at two doses and the second showed they are one function: with hundreds
of candidates there are always at least `cap` non-loop edges, so "sort loop-asserted last" and "reserve
the cap" select the identical set. That is recorded as a structural fact about the arm, not as two
experiments, and the block runs one intervention arm (Y).

The calibrated per-seed effect is 0 on half the seeds and large on the rest (0 to 0.0625), so a median
or sign criterion cannot see it at 100 seeds: median +0.0044, 5/10 positive, ~3% power. The mean is the
quantity the mechanism predicts -- the intervention reallocates a fixed admission budget away from edges
loops already assert, and that pays whenever a displaced edge was a world edge -- so the block's primary
criterion is the paired mean difference. Its bar is fixed at 0.01: one fifth of the R-over-C gain the
intervention is trying to add to (mean 0.0485 on block 5's 100 seeds, read from that artifact), a size
worth claiming rather than the smallest detectable one.

Writes `docs/gate13_loop_free_block6_calibration.json`. The allocation is carried over from
`docs/gate13_loop_free_admission_calibration.json` unchanged and is never re-derived here: a fresh scan
would read this workspace's own artifacts and move the window.
"""
from __future__ import annotations

import json
import random
import statistics as st
from pathlib import Path
from benchmarks import engine_stamp

REPO = Path(__file__).resolve().parent.parent
SOFT = json.loads((REPO / "docs/gate13_loop_free_admission_calibration.json").read_text())
DOSE = json.loads((REPO / "docs/gate13_loop_free_dose_calibration.json").read_text())
B5 = json.loads((REPO / "docs/gate13_temporal_redundancy_block5.json").read_text())
BAND = [float(x) for x in json.loads((REPO / "docs/gate13_c1_respecification.json").read_text())["band"]]

BARS = [0.005, 0.01, 0.015, 0.02, 0.03]
BAR = 0.01
N = 100

SHARED = ["mean", "median", "sd", "min", "max", "positive_share", "positive_n", "n",
          "spearman_vs_disp", "mean_r_coverage"]
_bad = [k for k in SHARED if SOFT["effect"][k] != DOSE["effect"][k]]
assert not _bad, f"the two doses disagree on {_bad}; the 'one function' claim would be false"
rows = DOSE["calibration_rows"]
diffs = [float(r["diff"]) for r in rows]
novel = [float(r["y_covered_novel"] - r["r_covered_novel"]) for r in rows]
loopd = [float(r["y_covered_loop"] - r["r_covered_loop"]) for r in rows]
disp = [int(r["disp_total"]) for r in rows]
mean_gain_r_over_c = float(B5["descriptive"]["mean_gain"])


def bootstrap_mean(x, reps=4000, seed=0):
    rng = random.Random(seed)
    m = sorted(st.fmean(rng.choice(x) for _ in x) for _ in range(reps))
    return [round(m[100], 5), round(m[3899], 5)]


def power(bar, reps=4000, seed=0):
    """Resample the ten calibration pairs to n=100 and count the two conditions of M1."""
    rng = random.Random(seed)
    ok_pt = ok_ci = 0
    for _ in range(reps):
        d = [rng.choice(diffs) for _ in range(N)]
        m = st.fmean(d)
        ok_pt += m >= bar
        if m >= bar:
            # normal-approximation lower bound, cheap and adequate for a 100-seed mean
            se = st.stdev(d) / (N ** 0.5)
            ok_ci += (m - 1.96 * se) > 0
    return {"bar": bar, "power_point": round(ok_pt / reps, 3), "power_point_and_ci": round(ok_ci / reps, 3)}


cal = {
    "what": "pooled calibration, criterion choice, bar provenance and power for block 6 (loop-free preference arm Y vs R)",
    "judged_by_block": False,
    "arm": DOSE["arm"],
    "doses_are_one_function": {
        "claim": "the soft reorder (X) and the reserved cap (Y) select the same candidates whenever at least cap "
                 "edges in the pool are not loop-asserted, which held on every cycle of every calibration seed",
        "evidence": "the two calibration artifacts' per-seed effect, composition and displacement statistics are "
                    "identical on all ten seeds, field for field",
        "consequence": "the block runs one intervention arm (Y); X is not a second dose",
        "floor": "the two arms would diverge only on a seed whose candidate pool holds fewer than 20 non-loop edges",
    },
    "calibration_seeds": DOSE["calibration_seeds"],
    "reused_from": ["docs/gate13_loop_free_admission_calibration.json", "docs/gate13_loop_free_dose_calibration.json"],
    "effect": {
        "mean": round(st.fmean(diffs), 4), "median": round(st.median(diffs), 4),
        "sd": round(st.stdev(diffs), 4), "min": min(diffs), "max": max(diffs),
        "positive_share": round(sum(1 for d in diffs if d > 0) / len(diffs), 3),
        "positive_n": sum(1 for d in diffs if d > 0), "n": len(diffs),
        "mean_ci": bootstrap_mean(diffs),
        "mean_se_at_100": round(st.stdev(diffs) / (N ** 0.5), 5),
        "novel_mean": round(st.fmean(novel), 3), "novel_ci": bootstrap_mean(novel),
        "loop_covered_mean": round(st.fmean(loopd), 4),
        "mean_r_coverage": DOSE["effect"]["mean_r_coverage"],
        "mean_y_coverage": DOSE["effect"]["mean_y_coverage"],
    },
    "perturbation": DOSE["perturbation"],
    "composition": DOSE["composition"],
    "criterion_choice": {
        "primary": "paired mean difference in coverage, Y - R",
        "why_mean": "the per-seed effect is 0 on half the calibration seeds and 0.027-0.063 on the rest, so median and "
                    "sign criteria are near-blind at n=100 (power 0.03) while the mean is bounded (se 0.0021 at n=100)",
        "why_not_median": "a median criterion would report the structural zeros as the effect and discard the large "
                          "gains the mechanism predicts",
        "disclosure": "the mean is sensitive to the tail; the artifact reports the median, the positive share and "
                      "the per-seed rows beside it, and no criterion reads them",
    },
    "bar": {
        "m1_mean_difference": BAR,
        "provenance": f"one fifth of the R-over-C gain on block 5's 100 fresh seeds (mean {mean_gain_r_over_c}), "
                      f"read from docs/gate13_temporal_redundancy_block5.json; the intervention is meant to add to "
                      f"that gain, and 0.01 is a fifth of it rather than the smallest detectable effect",
        "calibrated_effect": round(st.fmean(diffs), 4),
    },
    "band": BAND,
    "allocation": SOFT["allocation"],
    "allocation_rule": SOFT["allocation_rule"],
    "bars_simulated": BARS,
    "power": {str(b): power(b) for b in BARS},
    "null_check": "at bar 0.01 with a true effect of zero the point criterion passes ~0% of the time by construction; "
                  "the calibration therefore also reports the bar's distance from the calibrated mean in sd units "
                  "below",
    "bar_in_sd_units": round((st.fmean(diffs) - BAR) / (st.stdev(diffs) / (N ** 0.5)), 2),
    "caveat": "ten seeds give a noisy sd and a noisy mean; the power table is an estimate from them, and the block "
              "reports its own observed mean and interval beside the bar either way",
}
(REPO / "docs" / "gate13_loop_free_block6_calibration.json").write_text(json.dumps(engine_stamp.stamp(cal), indent=2) + "\n")

print("effect:", json.dumps(cal["effect"], indent=1))
print("bar:", cal["bar"])
print("power:", json.dumps(cal["power"], indent=1))
print("bar in sd units:", cal["bar_in_sd_units"])
print("allocation:", cal["allocation"])
