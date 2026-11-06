"""Score block 6 once against the frozen table in docs/GATE13-LOOP-FREE-ADMISSION-PREREGISTRATION.md.

The bar, the band and the allocation come from artifacts, never from this file's own reading of the result.
M1 is the paired mean difference in coverage (Y - R) against the frozen bar, with a bootstrap lower bound
required to clear zero. M2 is the mechanism check: the gain must sit in novel (non-loop) covered edges and
must not cost loop-covered edges. Unmeasurable cells are counted, never imputed; no cell may be missing.
"""
from __future__ import annotations

import json
import random
import statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAL = json.loads((REPO / "docs/gate13_loop_free_block6_calibration.json").read_text())
BAR = float(CAL["bar"]["m1_mean_difference"])
BAND = [float(x) for x in CAL["band"]]
ALLOC = CAL["allocation"]
N = 100
HALF = BAR / 2.0   # the mechanism criterion's bar for the novel-edge component

rows = [json.loads(x) for x in (REPO / ".scratch" / "loop_free_block6.jsonl").read_text().splitlines() if x.strip()]
cells = {(r["arm"], r["cap"], r["seed"]): r for r in rows}
seeds = sorted({r["seed"] for r in rows})
assert len(rows) == 3 * N, f"expected 300 cells, found {len(rows)}"
assert len(seeds) == N, f"expected {N} seeds, found {len(seeds)}"
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
        "disp_total": y.get("disp_total", 0), "disp_cycles": y.get("disp_cycles", 0),
        "hashes_differ_c_r": c["asserted_hash"] != r["asserted_hash"],
    })

diffs = [p["diff"] for p in per]
novel = [p["novel_diff"] for p in per]
loopd = [p["loop_diff"] for p in per]
disp = [p["disp_total"] for p in per]

g0 = sum(1 for p in per if p["hash_differs_r_y"])
g0_cr = sum(1 for p in per if p["hashes_differ_c_r"])
g1_mean = round(st.fmean(p["c_precision"] for p in per if p["c_precision"] is not None), 4)
g1 = BAND[0] <= g1_mean <= BAND[1]
g2 = sum(1 for d in disp if d >= 1)
gates_ok = g0 >= 96 and g0_cr >= 96 and g1 and g2 >= 96

mean_diff = st.fmean(diffs)
ci = boot_ci(diffs)
m1 = mean_diff >= BAR and ci[0] > 0
novel_mean = st.fmean(novel)
novel_ci = boot_ci(novel)
loop_mean = st.fmean(loopd)
m2 = novel_mean >= HALF and novel_ci[0] > 0 and loop_mean >= 0

if not gates_ok:
    verdict = "VOID / NOT COMPARABLE"
elif m1 and m2:
    verdict = "INTERVENTION SUPPORTED"
elif m1:
    verdict = "COVERAGE ONLY"
else:
    verdict = "INTERVENTION NOT SUPPORTED"

art = {
    "block": "6", "allocation": ALLOC, "cells": len(rows), "seeds": len(seeds),
    "arms": ["C", "R", "Y"],
    "intervention": CAL["arm"],
    "bar": BAR, "band": BAND, "novel_bar": HALF,
    "gates": {
        "G0_liveness_y_vs_r": g0, "G0_pass": g0 >= 96,
        "G0b_liveness_c_vs_r": g0_cr,
        "G1_mean_c_precision": g1_mean, "G1_pass": g1,
        "G2_seeds_preference_displaced": g2, "G2_pass": g2 >= 96,
        "all_pass": gates_ok,
    },
    "criteria": {
        "M1": {"pass": bool(m1), "mean_difference": round(mean_diff, 4), "ci95": ci, "bar": BAR,
               "median": round(st.median(diffs), 4),
               "positive": sum(1 for d in diffs if d > 0), "n": len(diffs)},
        "M2": {"pass": bool(m2), "novel_mean": round(novel_mean, 3), "novel_ci": novel_ci,
               "novel_bar": HALF, "loop_covered_mean_diff": round(loop_mean, 4)},
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
        "calibrated_sd": CAL["effect"]["sd"],
    },
    "verdict": verdict,
    "seed_rows": per,
}
(REPO / "docs" / "gate13_loop_free_block6.json").write_text(json.dumps(art, indent=2) + "\n")
print("gates:", art["gates"])
print("criteria:", json.dumps(art["criteria"], indent=2))
print("descriptive:", art["descriptive"])
print("VERDICT:", verdict)
