"""Score block 5 once against the frozen table in docs/GATE13-TEMPORAL-REDUNDANCY-B5-PREREGISTRATION.md.

Cut and bars come from `docs/gate13_temporal_redundancy_b5_calibration.json`; the C1' band from
`docs/gate13_c1_respecification.json`. The covariate is recomputed here at the registered floor of 1 from the recorded
`overlap` and `pred_world` counts -- the runner's own `o` field is the block-4 floor of 3 and is not used.
Unmeasurable seeds (zero denominator) are excluded and counted, never imputed.
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAL = json.loads((REPO / "docs/gate13_temporal_redundancy_b5_calibration.json").read_text())
THR, BARS, FLOOR = CAL["cut_o"], CAL["bars"], CAL["floor"]
BAND = [float(x) for x in json.loads((REPO / "docs/gate13_c1_respecification.json").read_text())["band"]]
N_REQUIRED, MEASURABLE_REQUIRED, HALF_MIN = 100, 96, 40

rows = [json.loads(x) for x in open(REPO / ".scratch" / "temporal_redundancy_b5.jsonl") if x.strip()]
cells = {(r["arm"], r["cap"], r["seed"]): r for r in rows}
seeds = sorted({r["seed"] for r in rows})
assert len(cells) == 200 and len(seeds) == 100, (len(cells), len(seeds))


def o5(overlap: int, pred_world: int):
    return round(overlap / pred_world, 4) if pred_world >= FLOOR else None


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


per, excluded = [], []
for s in seeds:
    c, r = cells[("C", 20, s)], cells[("R", 20, s)]
    rec = {"seed": s, "o": o5(c["overlap"], c["pred_world"]), "pred_world": c["pred_world"],
           "overlap": c["overlap"], "c_covered": c["covered"], "r_covered": r["covered"],
           "gain": round(r["coverage"] - c["coverage"], 4), "c_precision": c["precision"],
           "hashes_differ": c["asserted_hash"] != r["asserted_hash"]}
    (excluded if rec["o"] is None else per).append(rec)

g0 = sum(1 for s in seeds if cells[("C", 20, s)]["asserted_hash"] != cells[("R", 20, s)]["asserted_hash"])
g1_mean = round(st.fmean(cells[("C", 20, s)]["precision"] for s in seeds), 4)
g1 = BAND[0] <= g1_mean <= BAND[1]
g2 = len(per)
os_, gains = [p["o"] for p in per], [p["gain"] for p in per]
low = [p["gain"] for p in per if p["o"] < THR]
high = [p["gain"] for p in per if p["o"] >= THR]
g3 = len(low) >= HALF_MIN and len(high) >= HALF_MIN
gates_ok = g0 >= 96 and g1 and g2 >= MEASURABLE_REQUIRED and g3
med_diff = (st.median(high) - st.median(low)) if low and high else None

if len(per) >= 5 and len(set(os_)) > 1:
    rho = spearman(os_, gains)
    rng = random.Random(0)
    boot = []
    for _ in range(2000):
        idx = [rng.randrange(len(per)) for _ in per]
        boot.append(spearman([os_[i] for i in idx], [gains[i] for i in idx]))
    boot.sort()
    rho_ci = [round(boot[50], 3), round(boot[1949], 3)]
else:
    rho, rho_ci = None, None

M1 = len(low) >= HALF_MIN and len(high) >= HALF_MIN and med_diff is not None \
    and med_diff >= BARS["m1_median_gain_difference"]
M2 = rho is not None and rho >= BARS["m2_spearman_min"]
M3 = sum(1 for p in per if p["gain"] > 0) >= round(BARS["m3_positive_share"] * N_REQUIRED)

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
    "block": "5", "allocation": CAL["allocation"], "cells": len(rows), "seeds": len(seeds),
    "covariate": CAL["covariate"], "floor": FLOOR, "cut_o": THR, "bars": BARS, "band": BAND,
    "gates": {"G0_differ": g0, "G0_pass": g0 >= 96,
              "G1_mean_c_precision": g1_mean, "G1_pass": g1,
              "G2_measurable": g2, "G2_required": MEASURABLE_REQUIRED, "G2_pass": g2 >= MEASURABLE_REQUIRED,
              "G3_split_low": len(low), "G3_split_high": len(high), "G3_pass": g3,
              "all_pass": gates_ok},
    "criteria": {"M1": {"pass": bool(M1), "low_n": len(low), "high_n": len(high),
                        "low_median": round(st.median(low), 4) if low else None,
                        "high_median": round(st.median(high), 4) if high else None,
                        "difference": round(med_diff, 4) if med_diff is not None else None,
                        "bar": BARS["m1_median_gain_difference"]},
                 "M2": {"pass": bool(M2), "spearman": rho, "ci95": rho_ci, "bar": BARS["m2_spearman_min"]},
                 "M3": {"pass": bool(M3), "positive": sum(1 for p in per if p["gain"] > 0), "n": len(per),
                        "bar": round(BARS["m3_positive_share"] * N_REQUIRED)}},
    "descriptive": {"mean_gain": round(st.fmean(gains), 4) if gains else None,
                    "median_gain": round(st.median(gains), 4) if gains else None,
                    "mean_o": round(st.fmean(os_), 4) if os_ else None,
                    "o_min": min(os_) if os_ else None, "o_max": max(os_) if os_ else None,
                    "measurable_share": round(g2 / N_REQUIRED, 4),
                    "excluded_unmeasurable": [e["seed"] for e in excluded]},
    "verdict": verdict,
    "seed_rows": per, "excluded": excluded,
}
(REPO / "docs/gate13_temporal_redundancy_block5.json").write_text(json.dumps(art, indent=2) + "\n")
print("gates:", art["gates"])
print("criteria:", json.dumps(art["criteria"], indent=2))
print("descriptive:", art["descriptive"])
print("VERDICT:", verdict)
