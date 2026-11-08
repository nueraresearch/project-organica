"""Score block 8 once: does the loop-free admission gain scale with the cap?

Every bar and the allocation come from `docs/gate13_loop_free_cap_calibration.json`. M1 tests the
difference-in-differences (gain at cap 100 minus gain at cap 40) against the frozen bar with a bootstrap interval above
zero; M2 requires the gain to be positive at both caps, so a scaling pass cannot be manufactured by a negative at 40.
G2 tests that the cap axis is live at all: R at cap 100 must beat R at cap 40 on coverage.
"""
from __future__ import annotations

import json
import random
import statistics as st
from pathlib import Path
from benchmarks import engine_stamp

REPO = Path(__file__).resolve().parent.parent
CAL = json.loads((REPO / "docs/gate13_loop_free_cap_calibration.json").read_text())
BAR = float(CAL["bar"]["did"])
G0_BAR = int(CAL["gates"]["G0_bar"])
G2_BAR = int(CAL["gates"]["G2_bar"])
CAPS = [int(c) for c in CAL["caps"]]
ALLOC = CAL["allocation"]
N = 100

rows = [json.loads(x) for x in (REPO / ".scratch" / "loop_free_cap.jsonl").read_text().splitlines() if x.strip()]
cells = {(r["arm"], r["cap"], r["seed"]): r for r in rows}
seeds = sorted({r["seed"] for r in rows})
assert len(rows) == 2 * len(CAPS) * N, f"expected {2 * len(CAPS) * N} cells, found {len(rows)}"
assert seeds == list(range(ALLOC["lo"], ALLOC["hi"] + 1)), "cells are outside the frozen allocation"
missing = [(a, c, s) for s in seeds for c in CAPS for a in ("R", "Y") if (a, c, s) not in cells]
assert not missing, f"missing cells: {missing[:5]}"


def boot_ci(x, reps=4000, seed=0):
    rng = random.Random(seed)
    m = sorted(st.fmean(rng.choice(x) for _ in x) for _ in range(reps))
    return [round(m[100], 5), round(m[3899], 5)]


per = []
for s in seeds:
    c = {cap: (cells[("R", cap, s)], cells[("Y", cap, s)]) for cap in CAPS}
    p = {"seed": s}
    for cap in CAPS:
        r, y = c[cap]
        p[f"r{cap}"] = r["coverage"]
        p[f"y{cap}"] = y["coverage"]
        p[f"d{cap}"] = round(y["coverage"] - r["coverage"], 4)
        p[f"hash{cap}"] = r["asserted_hash"] != y["asserted_hash"]
        p[f"disp{cap}"] = y.get("disp_total", 0)
        p[f"novel{cap}"] = y["covered_novel"] - r["covered_novel"]
        p[f"loop{cap}"] = y["covered_loop"] - r["covered_loop"]
        p[f"r_prec{cap}"] = r["precision"]
    p["did"] = round(p[f"d{CAPS[-1]}"] - p[f"d{CAPS[0]}"], 4)
    p["r_lift"] = round(p[f"r{CAPS[-1]}"] - p[f"r{CAPS[0]}"], 4)
    per.append(p)

d = {cap: [p[f"d{cap}"] for p in per] for cap in CAPS}
did = [p["did"] for p in per]
lift = [p["r_lift"] for p in per]

g0 = {cap: sum(1 for p in per if p[f"hash{cap}"]) for cap in CAPS}
g1 = {cap: sum(1 for p in per if p[f"disp{cap}"] >= 1) for cap in CAPS}
lift_mean = st.fmean(lift)
lift_ci = boot_ci(lift)
g2 = lift_mean > 0 and lift_ci[0] > 0
gates_ok = all(g0[c] >= G0_BAR for c in CAPS) and all(g1[c] >= G2_BAR for c in CAPS) and g2

did_mean = st.fmean(did)
did_ci = boot_ci(did)
m1 = did_mean >= BAR and did_ci[0] > 0
m2 = all(st.fmean(d[c]) > 0 and boot_ci(d[c])[0] > 0 for c in CAPS)

if not gates_ok:
    verdict = "VOID / NOT COMPARABLE"
elif m1 and m2:
    verdict = "SCALING SUPPORTED"
elif m1:
    verdict = "SCALE-DEPENDENT"
elif m2:
    verdict = "GAIN WITHOUT SCALING"
else:
    verdict = "NO GAIN AT THESE CAPS"

art = {
    "block": "8", "allocation": ALLOC, "cells": len(rows), "seeds": len(seeds), "caps": CAPS,
    "arms": ["R", "Y"], "bar": BAR,
    "gates": {
        "G0_by_cap": {str(c): g0[c] for c in CAPS}, "G0_bar": G0_BAR,
        "G0_pass": all(g0[c] >= G0_BAR for c in CAPS),
        "G1_by_cap": {str(c): g1[c] for c in CAPS}, "G1_bar": G2_BAR,
        "G1_pass": all(g1[c] >= G2_BAR for c in CAPS),
        "G2_r_lift_mean": round(lift_mean, 4), "G2_r_lift_ci": lift_ci, "G2_pass": bool(g2),
        "all_pass": gates_ok,
    },
    "criteria": {
        "M1": {"pass": bool(m1), "did_mean": round(did_mean, 4), "did_ci": did_ci, "bar": BAR,
               "did_median": round(st.median(did), 4), "positive_n": sum(1 for v in did if v > 0), "n": len(did)},
        "M2": {str(c): {"mean": round(st.fmean(d[c]), 4), "ci95": boot_ci(d[c]),
                        "median": round(st.median(d[c]), 4),
                        "positive_n": sum(1 for v in d[c] if v > 0)} for c in CAPS},
        "M2_pass": bool(m2),
    },
    "descriptive": {
        "did_sd": round(st.stdev(did), 4), "did_min": min(did), "did_max": max(did),
        "r_coverage": {str(c): round(st.fmean(p[f"r{c}"] for p in per), 4) for c in CAPS},
        "y_coverage": {str(c): round(st.fmean(p[f"y{c}"] for p in per), 4) for c in CAPS},
        "mean_disp": {str(c): round(st.fmean(p[f"disp{c}"] for p in per), 2) for c in CAPS},
        "novel_diff": {str(c): round(st.fmean(p[f"novel{c}"] for p in per), 3) for c in CAPS},
        "loop_diff": {str(c): round(st.fmean(p[f"loop{c}"] for p in per), 4) for c in CAPS},
        "calibrated": {"d40": CAL["effect"]["d40_mean"], "d100": CAL["effect"]["d100_mean"],
                       "did": CAL["effect"]["did_mean"], "did_sd": CAL["effect"]["did_sd"]},
        "r_precision": {str(c): round(st.fmean(p[f"r_prec{c}"] for p in per if p[f"r_prec{c}"] is not None), 4)
                        for c in CAPS},
    },
    "verdict": verdict,
    "seed_rows": per,
}
(REPO / "docs" / "gate13_loop_free_cap.json").write_text(json.dumps(engine_stamp.stamp(art), indent=2) + "\n")
print("gates:", art["gates"])
print("criteria:", json.dumps(art["criteria"], indent=2))
print("descriptive:", art["descriptive"])
print("VERDICT:", verdict)
