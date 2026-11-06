"""Derive C1' -- the prospective re-specification of the control criterion -- from the 200-seed sweep.

Calibration only: this script tests no hypothesis and reads no confirmatory cell. It takes the dispersion of arm
C's cap-20 precision from `docs/gate13_control_precision_sweep.json` (200 fresh seeds, disjoint from both
completed blocks) and fixes the equivalence margin as the smallest 0.001 grid value at which 90% of bootstrap
25-seed blocks satisfy |mean - 0.4667| <= delta. It also records the power curve, the margin's stability under
resampling of the calibration data, and what the criterion cannot see. Writes
`docs/gate13_c1_respecification.json`.
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SWEEP = REPO / "docs" / "gate13_control_precision_sweep.json"
OUT = REPO / "docs" / "gate13_c1_respecification.json"
BASE, N, REPS, Z90 = 0.4667, 25, 20000, 1.2815515655446004


def main() -> None:
    prec = [r["precision"] for r in json.loads(SWEEP.read_text())["raw"]]
    mean, sd = st.fmean(prec), st.stdev(prec)
    se = sd / math.sqrt(N)
    offset = mean - BASE
    delta_analytic = abs(offset) + Z90 * se

    rng = random.Random(0)
    draws = [[prec[rng.randrange(len(prec))] for _ in range(N)] for _ in range(REPS)]
    means = [st.fmean(d) for d in draws]
    sds = [st.stdev(d) for d in draws]

    grid = [round(0.020 + 0.001 * i, 4) for i in range(41)]
    cov = {d: sum(1 for m in means if abs(m - BASE) <= d) / REPS for d in grid}
    delta = min(d for d in grid if cov[d] >= 0.90)
    lo, hi = BASE - delta, BASE + delta

    shifts = [0.0, -0.005, -0.010, -0.015, -0.022, -0.032, -0.050, 0.020]
    curve = [{"shift": s, "pass": round(sum(1 for m in means if abs(m + s - BASE) <= delta) / REPS, 3)}
             for s in shifts]
    shift_50 = None
    for i in range(201):
        s = -0.001 * i
        if sum(1 for m in means if abs(m + s - BASE) <= delta) / REPS < 0.5:
            shift_50 = round(s, 3)
            break

    rng2 = random.Random(1)
    deltas = []
    for _ in range(500):
        b = [prec[rng2.randrange(len(prec))] for _ in range(len(prec))]
        deltas.append(abs(st.fmean(b) - BASE) + Z90 * st.stdev(b) / math.sqrt(N))
    deltas.sort()

    inband = [(m, s) for m, s in zip(means, sds) if abs(m - BASE) <= delta]
    blind = sum(1 for _m, s in inband if s > 2 * sd) / len(inband)

    art = {
        "what": "C1' -- prospective re-specification of the control-at-chance criterion, power computed in advance",
        "status": ("PROSPECTIVE. Amendment 1 to the confirmatory pre-registration; not applicable to "
                   "20270602-20270626 and not a re-score of it."),
        "calibration_source": "docs/gate13_control_precision_sweep.json (200 seeds, 20270701-20270900, arm C cap 20, NOT confirmatory)",
        "blocks_not_used": ["20261101-20261105 (development)", "20270602-20270626 (confirmatory)"],
        "n_seeds_per_block": N,
        "comparator": BASE,
        "reference": {"n": len(prec), "mean": round(mean, 4), "sd": round(sd, 4),
                      "se_of_block_mean": round(se, 4), "offset_from_base": round(offset, 4)},
        "margin": {"analytic_closed_form": round(delta_analytic, 4), "z90": 1.2816,
                   "grid_step": 0.001, "chosen": delta,
                   "empirical_pass_at_chosen": round(cov[delta], 3),
                   "grid_coverage": {str(d): round(cov[d], 3) for d in grid}},
        "band": [round(lo, 4), round(hi, 4)],
        "power_curve": curve,
        "shift_at_which_pass_falls_below_half": shift_50,
        "margin_stability_over_calibration_data": {
            "reps": 500, "p05": round(deltas[25], 4), "median": round(st.median(deltas), 4), "p95": round(deltas[474], 4)},
        "dispersion_blind_spot": {"share_of_in_band_blocks_with_sd_above_2x_reference": round(blind, 4),
                                  "threshold_sd": round(2 * sd, 4)},
        "decision_rule": {"pass": "|mean(C at cap 20) - 0.4667| <= delta", "band": [round(lo, 4), round(hi, 4)],
                          "fail_low_and_fail_high": "both are 'not comparable'; reported separately"},
    }
    OUT.write_text(json.dumps(art, indent=2) + "\n")
    print(f"reference n={len(prec)} mean={mean:.4f} sd={sd:.4f} se={se:.4f} offset={offset:+.4f}")
    print(f"margin analytic={delta_analytic:.4f} chosen={delta:.3f} pass={cov[delta]:.3f} band=[{lo:.4f},{hi:.4f}]")
    print(f"shift at 50%: {shift_50} | stability p05/med/p95 = {deltas[25]:.4f}/{st.median(deltas):.4f}/{deltas[474]:.4f}")
    print(f"blind spot: {blind:.3%} of in-band blocks have sd > {2*sd:.4f}")
    for row in curve:
        print(f"  shift {row['shift']:+.3f} -> pass {row['pass']:.3f}")


if __name__ == "__main__":
    main()
