"""Score block 7 once against the frozen table in docs/GATE13-LOOP-FREE-ADMISSION-PREREGISTRATION-B7.md.

Every bar, the band and the allocation come from `docs/gate13_loop_free_block7_calibration.json`. M1 is the paired mean
difference in coverage (Y - R) against the unchanged bar, with the bootstrap lower bound required to clear zero; M2 is
the mechanism check on the novel-edge channel. No cell may be missing and none is substituted; a failed gate is a void
and is reported as the gate.
"""
from __future__ import annotations

import json
import random
import statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAL = json.loads((REPO / "docs/gate13_loop_free_block7_calibration.json").read_text())
BAR = float(CAL["bar"]["m1_mean_difference"])
NOVEL_BAR = float(CAL["bar"]["novel_bar"])
BAND = [float(x) for x in CAL["gates"]["band"]]
G0_BAR = int(CAL["gates"]["G0_bar"])
G0B_BAR = int(CAL["gates"]["G0b_bar"])
G2_BAR = int(CAL["gates"]["G2_bar"])
ALLOC = CAL["allocation"]
N = 100

rows = [json.loads(x) for x in (REPO / ".scratch" / "loop_free_block7.jsonl").read_text().splitlines() if x.strip()]
cells = {(r["arm"], r["cap"], r["seed"]): r for r in rows}
seeds = sorted({r["seed"] for r in rows})
assert len(rows) == 3 * N, f"expected 300 cells, found {len(rows)}"
assert seeds == list(range(ALLOC["lo"], ALLOC["hi"] + 1)), "cells are outside the frozen allocation"
missing = [(a, s) for s in seeds for a in ("C", "R", "Y") if (a, 20, s) not in cells]
assert not missing, f"missing cells: {missing[:5]}"


def boot_ci(x, reps=4000, seed=0):
    rng = random.Random(seed)
    m = sorted(st.fmean(rng.choice(x) for _ in x) for _ in range(reps))
    return [round(m[100], 5), round(m[3899], 5)]


per = []
for s in seeds:
    c, r, y = cells[("C", 20, s)], cells[("R", 20, s)], cells[("Y", 20, s)]
    per.append({
        "seed": s,
        "c_coverage": c["coverage"], "r_coverage": r["coverage"], "y_coverage": y["coverage"],
        "diff": round(y["coverage"] - r["coverage"], 4),
        "r_gain_over_c": round(r["coverage"] - c["coverage"], 4),
        "r_covered_loop": r["covered_loop"], "y_covered_loop": y["covered_loop"],
        "r_covered_novel": r["covered_novel"], "y_covered_novel": y["covered_novel"],
        "novel_diff": y["covered_novel"] - r["covered_novel"],
        "loop_diff": y["covered_loop"] - r["covered_loop"],
        "c_precision": c["precision"], "r_precision": r["precision"], "y_precision": y["precision"],
        "hash_differs_r_y": r["asserted_hash"] != y["asserted_hash"],
        "hashes_differ_c_r": c["asserted_hash"] != r["asserted_hash"],
        "disp_total": y.get("disp_total", 0), "disp_cycles": y.get("disp_cycles", 0),
    })

diffs = [p["diff"] for p in per]
novel = [p["novel_diff"] for p in per]
loopd = [p["loop_diff"] for p in per]
disp = [p["disp_total"] for p in per]

g0 = sum(1 for p in per if p["hash_differs_r_y"])
g0b = sum(1 for p in per if p["hashes_differ_c_r"])
g1_mean = round(st.fmean(p["c_precision"] for p in per if p["c_precision"] is not None), 4)
g1 = BAND[0] <= g1_mean <= BAND[1]
g2 = sum(1 for d in disp if d >= 1)
gates_ok = g0 >= G0_BAR and g0b >= G0B_BAR and g1 and g2 >= G2_BAR

mean_diff = st.fmean(diffs)
ci = boot_ci(diffs)
m1 = mean_diff >= BAR and ci[0] > 0
novel_mean = st.fmean(novel)
novel_ci = boot_ci(novel)
loop_mean = st.fmean(loopd)
m2 = novel_mean >= NOVEL_BAR and novel_ci[0] > 0 and loop_mean >= 0

if not gates_ok:
    verdict = "VOID / NOT COMPARABLE"
elif m1 and m2:
    verdict = "INTERVENTION SUPPORTED"
elif m1:
    verdict = "COVERAGE ONLY"
else:
    verdict = "INTERVENTION NOT SUPPORTED"

art = {
    "block": "7", "allocation": ALLOC, "cells": len(rows), "seeds": len(seeds),
    "arms": ["C", "R", "Y"], "intervention": CAL["arm"],
    "bar": BAR, "novel_bar": NOVEL_BAR, "band": BAND,
    "gate_bars": {"G0": G0_BAR, "G0b": G0B_BAR, "G2": G2_BAR},
    "gates": {
        "G0_liveness_y_vs_r": g0, "G0_pass": g0 >= G0_BAR,
        "G0b_liveness_c_vs_r": g0b, "G0b_pass": g0b >= G0B_BAR,
        "G1_mean_c_precision": g1_mean, "G1_pass": g1,
        "G2_seeds_preference_displaced": g2, "G2_pass": g2 >= G2_BAR,
        "all_pass": gates_ok,
    },
    "criteria": {
        "M1": {"pass": bool(m1), "mean_difference": round(mean_diff, 4), "ci95": ci, "bar": BAR,
               "median": round(st.median(diffs), 4), "positive": sum(1 for d in diffs if d > 0), "n": len(diffs)},
        "M2": {"pass": bool(m2), "novel_mean": round(novel_mean, 3), "novel_ci": novel_ci,
               "novel_bar": NOVEL_BAR, "loop_covered_mean_diff": round(loop_mean, 4)},
    },
    "descriptive": {
        "mean_diff": round(mean_diff, 4), "median_diff": round(st.median(diffs), 4),
        "sd_diff": round(st.stdev(diffs), 4), "min": min(diffs), "max": max(diffs),
        "positive_share": round(sum(1 for d in diffs if d > 0) / len(diffs), 3),
        "mean_r_gain_over_c": round(st.fmean(p["r_gain_over_c"] for p in per), 4),
        "mean_y_gain_over_c": round(st.fmean(p["y_coverage"] - p["c_coverage"] for p in per), 4),
        "mean_disp_total": round(st.fmean(disp), 2),
        "seeds_with_displacement": g2,
        "calibrated_mean": CAL["effect"]["mean"], "calibrated_median": CAL["effect"]["median"],
        "calibrated_sd": CAL["effect"]["sd"], "block6_mean": CAL["effect"]["block6_mean"],
    },
    "verdict": verdict,
    "seed_rows": per,
}
(REPO / "docs" / "gate13_loop_free_block7.json").write_text(json.dumps(art, indent=2) + "\n")
print("gates:", art["gates"])
print("criteria:", json.dumps(art["criteria"], indent=2))
print("descriptive:", art["descriptive"])
print("VERDICT:", verdict)
