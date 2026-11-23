"""Score block 3 once against the frozen table in docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md.

Reads the threshold and bars from the calibration artifact and the C1' band from the re-specification artifact; nothing is
recomputed and no bar is adjusted. Writes `docs/gate13_redundancy_block3.json`.
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
from pathlib import Path
from benchmarks import engine_stamp

REPO = Path(__file__).resolve().parent.parent
CAL = json.loads((REPO / "docs/gate13_redundancy_moderator_calibration.json").read_text())
R_THR, BARS = CAL["threshold_r"], CAL["bars"]
LO, HI = CAL["allocation"]["lo"], CAL["allocation"]["hi"]

# C1' band, read straight from the re-specification artifact (never typed)
spec = json.loads((REPO / "docs/gate13_c1_respecification.json").read_text())
BAND = [float(spec["band"][0]), float(spec["band"][1])]
assert len(BAND) == 2 and BAND[0] < BAND[1]

rows = [json.loads(x) for x in open(REPO / ".scratch" / "redundancy_block.jsonl") if x.strip()]
cells = {(r["arm"], r["cap"], r["seed"]): r for r in rows}
seeds = sorted({r["seed"] for r in rows})
assert len(cells) == 200 and len(seeds) == 100, (len(cells), len(seeds))

per = []
for s in seeds:
    c, r = cells[("C", 20, s)], cells[("R", 20, s)]
    per.append({"seed": s, "r": c["r"], "c_covered": c["covered"], "r_covered": r["covered"],
                "gain": round(r["coverage"] - c["coverage"], 4),
                "c_precision": c["precision"], "c_precision_r": r["precision"],
                "c_loop": c["loop_world_edges"], "r_loop": r["loop_world_edges"],
                "hashes_differ": c["asserted_hash"] != r["asserted_hash"],
                "loop_hashes_equal": c["loop_hash"] == r["loop_hash"]})


def pearson(xs, ys):
    mx, my = st.fmean(xs), st.fmean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))


rs = [p["r"] for p in per]
gains = [p["gain"] for p in per]
low = [p["gain"] for p in per if p["r"] < R_THR]
high = [p["gain"] for p in per if p["r"] >= R_THR]
rho = spearman(rs, gains)
med_diff = (st.median(low) - st.median(high)) if low and high else None

rng = random.Random(0)
boot = []
for _ in range(2000):
    idx = [rng.randrange(len(per)) for _ in per]
    boot.append(spearman([rs[i] for i in idx], [gains[i] for i in idx]))
boot.sort()
rho_ci = [round(boot[50], 3), round(boot[1949], 3)]

g0 = sum(1 for p in per if p["hashes_differ"])
g1_mean = round(st.fmean(p["c_precision"] for p in per), 4)
g1 = BAND[0] <= g1_mean <= BAND[1]
g2 = sum(1 for p in per if p["loop_hashes_equal"])

M1 = (len(low) >= 40 and len(high) >= 40 and med_diff is not None
      and med_diff >= BARS["m1_median_gain_difference"])
M2 = rho <= BARS["m2_spearman_max"]
M3 = sum(1 for p in per if p["gain"] > 0) >= round(BARS["m3_positive_share"] * len(per))

gates_ok = g0 >= 96 and g1 and g2 >= 98
if not gates_ok:
    verdict = "VOID / NOT COMPARABLE"
elif M1 and M2:
    verdict = "MODERATOR SUPPORTED"
elif M2:
    verdict = "DIRECTIONAL ONLY"
elif M1:
    verdict = "HALF-SPLIT ONLY"
else:
    verdict = "MODERATOR NOT SUPPORTED"

art = {
    "block": "3", "allocation": CAL["allocation"], "cells": len(rows), "seeds": len(seeds),
    "band": BAND,
    "threshold_r": R_THR, "bars": BARS,
    "gates": {"G0_differ": g0, "G0_pass": g0 >= 96,
              "G1_mean_c_precision": g1_mean, "G1_band": BAND, "G1_pass": g1,
              "G2_loop_hashes_equal": g2, "G2_pass": g2 >= 98,
              "all_pass": gates_ok},
    "criteria": {"M1": {"pass": bool(M1), "low_n": len(low), "high_n": len(high),
                        "low_median": round(st.median(low), 4) if low else None,
                        "high_median": round(st.median(high), 4) if high else None,
                        "median_difference": round(med_diff, 4) if med_diff is not None else None,
                        "bar": BARS["m1_median_gain_difference"]},
                 "M2": {"pass": bool(M2), "spearman": round(rho, 3), "ci95": rho_ci,
                        "bar": BARS["m2_spearman_max"]},
                 "M3": {"pass": bool(M3), "positive": sum(1 for p in per if p["gain"] > 0),
                        "n": len(per), "bar": round(BARS["m3_positive_share"] * len(per))}},
    "descriptive": {"mean_gain": round(st.fmean(gains), 4), "median_gain": round(st.median(gains), 4),
                    "mean_c_coverage": round(st.fmean(p["c_covered"] for p in per) / 200, 4),
                    "mean_r_coverage": round(st.fmean(p["r_covered"] for p in per) / 200, 4),
                    "r_min": min(rs), "r_max": max(rs)},
    "verdict": verdict,
    "seeds": per,
}
(REPO / "docs/gate13_redundancy_block3.json").write_text(json.dumps(engine_stamp.stamp(art), indent=2) + "\n")

print("band:", BAND)
print("gates:", art["gates"])
print("criteria:", json.dumps(art["criteria"], indent=2))
print("descriptive:", art["descriptive"])
print("VERDICT:", verdict)
