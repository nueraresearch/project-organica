"""Dose calibration for block 6: the strict loop-free reservation (arm Y) against R.

The soft preference (arm X) was calibrated first and is too weak to test: on ten seeds it displaced
~6 admitted edges per cycle yet moved final coverage by a median of +0.004 (sd 0.021), which leaves the
100-seed sign criterion at ~3% power. Reordering the cap is not the same as removing the redundancy, so
the same preference is calibrated at full dose before anything is frozen: reserving the cap for edges no
loop asserts, with loop-asserted edges admitted only as backfill.

Runs on the same ten calibration seeds as `calibrate_loop_free_admission.py` (those seeds are not judged
by the block) and reuses their R rows from that artifact. It does **not** touch the allocation: the
block's window was fixed by the first calibration and is carried over unchanged, because re-deriving it
here would scan this artifact's own seeds and shift the window (rule 19's prohibition, in reverse).

Writes `docs/gate13_loop_free_dose_calibration.json`.
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.run_loop_free_admission_block import run_cell

BASE = json.loads((REPO / "docs/gate13_loop_free_admission_calibration.json").read_text())
SEEDS = [int(s) for s in BASE["calibration_seeds"]]
ALLOC = BASE["allocation"]
BARS = [0.005, 0.01, 0.015, 0.02, 0.03]
SIGN_BAR = 0.60


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(x, y):
    mx, my = st.fmean(x), st.fmean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def power(diffs, n, bar, sign_bar, reps=4000, seed=0):
    rng = random.Random(seed)
    m1 = m2 = both = 0
    for _ in range(reps):
        d = [rng.choice(diffs) for _ in range(n)]
        ok1 = st.median(d) >= bar
        ok2 = sum(1 for v in d if v > 0) / n >= sign_bar
        m1 += ok1
        m2 += ok2
        both += ok1 and ok2
    return {"n": n, "bar": bar, "sign_bar": sign_bar,
            "power_m1_median": round(m1 / reps, 3), "power_m2_sign": round(m2 / reps, 3),
            "power_both": round(both / reps, 3)}


rows = []
for seed in SEEDS:
    y = run_cell("Y", seed)
    base = next(b for b in BASE["calibration_rows"] if int(b["seed"]) == seed)
    row = {
        "seed": seed,
        "r_coverage": base["r_coverage"], "y_coverage": y["coverage"],
        "diff": round(y["coverage"] - base["r_coverage"], 4),
        "r_asserted": base["r_asserted"], "y_asserted": y["asserted"],
        "r_precision": base["r_precision"], "y_precision": y["precision"],
        "r_covered_loop": base["r_covered_loop"], "y_covered_loop": y["covered_loop"],
        "r_covered_novel": base["r_covered_novel"], "y_covered_novel": y["covered_novel"],
        "disp_total": y.get("disp_total", 0), "disp_cycles": y.get("disp_cycles", 0),
        "disp_max": y.get("disp_max", 0), "disp_mean": y.get("disp_mean", 0.0),
        "loop_edges": y["loop_edges"], "y_asserted_loop": y["asserted_loop"],
        "y_asserted_hash": y["asserted_hash"],
        "runtime_s": y["runtime_s"],
    }
    rows.append(row)
    print(json.dumps(row), flush=True)

diffs = [r["diff"] for r in rows]
disp = [r["disp_total"] for r in rows]
mean_d, median_d = st.fmean(diffs), st.median(diffs)
sd_d = st.stdev(diffs) if len(diffs) > 1 else 0.0

cal = {
    "what": "dose calibration for block 6: strict loop-free reservation (Y) against R on the ten calibration seeds",
    "arm": "Y = R with the cap reserved for edges no loop asserts; loop-asserted edges admitted only as backfill",
    "why": "the soft dose (X) displaced ~6 admitted edges per cycle but moved final coverage by a median of +0.004 "
           "with sd 0.021, so the 100-seed criteria had ~3% power; reordering is not removing",
    "calibration_seeds": SEEDS,
    "calibration_rows": rows,
    "reused_from": "docs/gate13_loop_free_admission_calibration.json (the R rows for these seeds)",
    "allocation_carried_over": ALLOC,
    "effect": {
        "mean": round(mean_d, 4), "median": round(median_d, 4), "sd": round(sd_d, 4),
        "min": min(diffs), "max": max(diffs),
        "positive_share": round(sum(1 for d in diffs if d > 0) / len(diffs), 3),
        "positive_n": sum(1 for d in diffs if d > 0), "n": len(diffs),
        "mean_r_coverage": round(st.fmean(r["r_coverage"] for r in rows), 4),
        "mean_y_coverage": round(st.fmean(r["y_coverage"] for r in rows), 4),
        "spearman_vs_disp": (round(pearson(ranks(disp), ranks(diffs)), 3)
                             if len(set(disp)) > 1 and len(set(diffs)) > 1 else None),
    },
    "perturbation": {
        "seeds_with_any_displacement": sum(1 for d in disp if d > 0),
        "mean_disp_total": round(st.fmean(disp), 3), "median_disp_total": st.median(disp),
        "max_disp_total": max(disp), "min_disp_total": min(disp),
        "mean_cycles_with_displacement": round(st.fmean(r["disp_cycles"] for r in rows), 1),
        "loop_edges_mean": round(st.fmean(r["loop_edges"] for r in rows), 2),
    },
    "composition": {
        "r_covered_loop_mean": round(st.fmean(r["r_covered_loop"] for r in rows), 2),
        "y_covered_loop_mean": round(st.fmean(r["y_covered_loop"] for r in rows), 2),
        "r_covered_novel_mean": round(st.fmean(r["r_covered_novel"] for r in rows), 2),
        "y_covered_novel_mean": round(st.fmean(r["y_covered_novel"] for r in rows), 2),
    },
    "power": {str(b): power(diffs, 100, b, SIGN_BAR) for b in BARS},
    "sign_bar": SIGN_BAR,
    "caveat": "ten seeds give a noisy sd and a noisy sign share; the power table is an estimate from them, and the "
              "block reports its own observed effect beside the bar either way",
}
(REPO / "docs" / "gate13_loop_free_dose_calibration.json").write_text(json.dumps(cal, indent=2) + "\n")

print("effect:", cal["effect"])
print("perturbation:", cal["perturbation"])
print("composition:", cal["composition"])
for b, p in cal["power"].items():
    print(" power", b, p)
