"""Calibration, threshold and power for block 4's covariate.

Covariate: o_s = |L_s and P_s and W| / |P_s and W| on the CONTROL cell -- the share of the control's world-covered
temporal (prediction_candidate) edges that its loop candidates already assert. Read from the control cell before the
ratio cell is scored. Calibrated on the 10 block-2 seeds, which block 4 does not contain.

Writes `docs/gate13_temporal_redundancy_calibration.json`. Asserts the covariate is not degenerate.
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
import sys
from pathlib import Path

import os
os.environ.setdefault("PYTHONHASHSEED", "0")

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.run_temporal_redundancy_block import run_cell  # noqa: E402

PREV = json.loads((REPO / "docs/gate13_redundancy_moderator_calibration.json").read_text())
GAINS = {int(p["seed"]): float(p["gain"]) for p in PREV["pairs"]}
SEEDS = sorted(GAINS)
CAND_START = 20271201


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


pairs = []
for s in SEEDS:
    cell = run_cell("C", s)
    pairs.append({"seed": s, "o": cell["o"], "overlap": cell["overlap"], "pred_world": cell["pred_world"],
                  "loop_world": cell["loop_world"], "gain": GAINS[s]})
    print("calib", s, "o =", cell["o"], "overlap", cell["overlap"], "/", cell["pred_world"],
          "gain", GAINS[s], flush=True)

usable = [p for p in pairs if p["o"] is not None]
os_, gs = [p["o"] for p in usable], [p["gain"] for p in usable]
assert len(set(os_)) >= 5, f"covariate degenerate: {sorted(set(os_))}"
THR = round(st.median(os_), 4)
mx, my = st.fmean(os_), st.fmean(gs)
b = sum((x - mx) * (y - my) for x, y in zip(os_, gs)) / sum((x - mx) ** 2 for x in os_)
a = my - b * mx
resid = math.sqrt(sum((y - (a + b * x)) ** 2 for x, y in zip(os_, gs)) / (len(os_) - 2))

DIFF_BAR, RHO_BAR, POS_BAR = 0.03, 0.25, 0.66   # positive direction: higher control-side overlap -> larger gain


def simulate(n, slope, sd, reps=4000, seed=0):
    rng = random.Random(seed)
    m1 = m2 = both = m3 = 0
    for _ in range(reps):
        g = [(d["o"], slope * (d["o"] - 0.5) + rng.gauss(0, sd))
             for d in (rng.choice(usable) for _ in range(n))]
        low = [y for x, y in g if x < THR]
        high = [y for x, y in g if x >= THR]
        ok1 = len(low) >= 8 and len(high) >= 8 and (st.median(high) - st.median(low)) >= DIFF_BAR
        ok2 = spearman([x for x, _ in g], [y for _, y in g]) >= RHO_BAR
        m1 += ok1
        m2 += ok2
        both += ok1 and ok2
        m3 += sum(1 for _, y in g if y > 0) / n >= POS_BAR
    return {"n": n, "slope": round(slope, 4), "sd": round(sd, 4),
            "power_m1_half_split": round(m1 / reps, 3), "power_m2_spearman": round(m2 / reps, 3),
            "power_both": round(both / reps, 3), "power_m3_replication": round(m3 / reps, 3)}


seen, files = set(), 0
for p in REPO.rglob("*"):
    if not p.is_file() or p.suffix not in {".py", ".md", ".json"}:
        continue
    if any(part in {".git", ".venv", "node_modules", ".scratch", "__pycache__"} for part in p.parts):
        continue
    files += 1
    try:
        text = p.read_text(errors="ignore")
    except OSError:
        continue
    for tok in text.replace(",", " ").replace(":", " ").split():
        if len(tok) == 8 and tok.startswith("2027") and tok.isdigit():
            seen.add(int(tok))


def first_free_run(present, start, length):
    s = start
    while not all((s + i) not in present for i in range(length)):
        s += 1
    return s, s + length - 1


LO, HI = first_free_run(seen, CAND_START, 100)

cal = {
    "what": "threshold, calibration association and power for block 4 (control-side loop-prediction overlap)",
    "judged_by_block": False,
    "covariate": "o_s = |L and P and W| / |P and W| on the control cell, P = prediction_candidate edges, L = loop edges",
    "min_denominator": 3,
    "allocation": {"lo": LO, "hi": HI, "seeds": HI - LO + 1},
    "freshness": {"files_scanned": files, "rejected_hits": sorted(x for x in seen if CAND_START <= x < LO)},
    "pairs": pairs,
    "threshold_o": THR,
    "threshold_note": "median of the calibration seeds; fixed before any block cell is run",
    "association": {"pearson": round(pearson(os_, gs), 3), "spearman": round(spearman(os_, gs), 3), "n": len(os_)},
    "linear_fit": {"intercept": round(a, 4), "slope": round(b, 4), "resid_sd": round(resid, 4)},
    "bars": {"m1_median_gain_difference": DIFF_BAR, "m2_spearman_min": RHO_BAR, "m3_positive_share": POS_BAR},
    "power": {},
}
for n in (100,):
    cal["power"][f"n{n}_mechanism_sized"] = simulate(n, 0.10, resid)
    cal["power"][f"n{n}_calibration_implied"] = simulate(n, b, resid)
    cal["power"][f"n{n}_null"] = simulate(n, 0.0, resid)
(REPO / "docs/gate13_temporal_redundancy_calibration.json").write_text(json.dumps(cal, indent=2) + "\n")
print("threshold o*:", THR, "| association:", cal["association"], "| fit:", cal["linear_fit"])
for k, v in cal["power"].items():
    print(" ", k, v)
print("allocation:", LO, HI, "| rejected:", cal["freshness"]["rejected_hits"], "| files:", files)
