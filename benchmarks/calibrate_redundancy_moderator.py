"""Calibration + power for the pre-registered loop-redundancy moderator block.

Covariate: r_s = |W and L_s| / |W| -- the share of the world's edges the count control's loop candidates already assert.
Loops are built from the stream, not from the admission cap (§8.13: identical across arms on 10/10 seeds), so r_s is a
seed property readable from the control cell before the ratio cell is scored.

This fixes the split threshold and the power of the registered bars, using only the 10 calibration seeds (block 2), which
the new block does not contain. Writes `docs/gate13_redundancy_moderator_calibration.json`.
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ART = json.loads((REPO / "docs/gate13_structure_provenance.json").read_text())
WORLD, CELLS = 112, ART["cells"]
SEEDS = sorted({k.split("_")[0] for k in CELLS})
CAND_START = 20271001
LO, HI = CAND_START, CAND_START + 99


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
    loop = CELLS[f"{s}_C"]["covered_by_type"].get("loop_candidate", 0)
    pairs.append({"seed": int(s), "loop_edges": loop, "r": round(loop / WORLD, 4),
                  "c_covered": CELLS[f"{s}_C"]["covered"],
                  "r_covered": CELLS[f"{s}_R"]["covered"],
                  "gain": round((CELLS[f"{s}_R"]["covered"] - CELLS[f"{s}_C"]["covered"]) / WORLD, 4)})

rs, gains = [p["r"] for p in pairs], [p["gain"] for p in pairs]
R_THR = round(st.median(rs), 4)
mx, my = st.fmean(rs), st.fmean(gains)
b = sum((x - mx) * (y - my) for x, y in zip(rs, gains)) / sum((x - mx) ** 2 for x in rs)
a = my - b * mx
resid_sd = math.sqrt(sum((y - (a + b * x)) ** 2 for x, y in zip(rs, gains)) / (len(rs) - 2))

DIFF_BAR, RHO_BAR, POS_BAR = 0.03, -0.25, 0.66

# scan: which 8-digit 2027 seeds appear anywhere in the tree
seen = set()
files = 0
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
    """First run of `length` consecutive seeds at or after `start` that appears nowhere in the tree."""
    s = start
    while True:
        if all((s + i) not in present for i in range(length)):
            return s, s + length - 1
        s += 1


LO, HI = first_free_run(seen, CAND_START, 100)
blocked = sorted(x for x in seen if CAND_START <= x < LO)
occupancy = sorted(x for x in seen if LO <= x <= HI)


def simulate(n, slope, sd, reps=4000, seed=0):
    rng = random.Random(seed)
    m1 = m2 = both = m3 = 0
    for _ in range(reps):
        g = [(d["r"], slope * (d["r"] - 0.5) + rng.gauss(0, sd))
             for d in (rng.choice(pairs) for _ in range(n))]
        low = [y for x, y in g if x < R_THR]
        high = [y for x, y in g if x >= R_THR]
        ok1 = len(low) >= 8 and len(high) >= 8 and st.median(low) - st.median(high) >= DIFF_BAR
        ok2 = spearman([x for x, _ in g], [y for _, y in g]) <= RHO_BAR
        m1 += ok1
        m2 += ok2
        both += ok1 and ok2
        m3 += sum(1 for _, y in g if y > 0) / n >= POS_BAR
    return {"n": n, "slope": round(slope, 4), "sd": round(sd, 4),
            "power_m1_half_split": round(m1 / reps, 3),
            "power_m2_spearman": round(m2 / reps, 3),
            "power_both": round(both / reps, 3),
            "power_m3_replication": round(m3 / reps, 3)}


cal = {
    "what": "threshold, calibration association and power for the pre-registered loop-redundancy moderator block",
    "judged_by_block": False,
    "allocation": {"lo": LO, "hi": HI, "seeds": HI - LO + 1},
    "freshness": {"files_scanned": files, "occurrences_in_range": occupancy, "rejected_hits": blocked,
                  "note": "8-digit 2027 tokens found by a whitespace/comma/colon split of every .py/.md/.json file"},
    "world_edges": WORLD,
    "pairs": pairs,
    "threshold_r": R_THR,
    "threshold_note": "median of the 10 calibration seeds; fixed before any block cell is run",
    "association": {"pearson": round(pearson(rs, gains), 3), "spearman": round(spearman(rs, gains), 3), "n": len(rs)},
    "linear_fit": {"intercept": round(a, 4), "slope": round(b, 4), "resid_sd": round(resid_sd, 4)},
    "bars": {"m1_median_gain_difference": DIFF_BAR, "m2_spearman_max": RHO_BAR, "m3_positive_share": POS_BAR},
    "power": {},
}
for n in (25, 50, 100):
    cal["power"][f"n{n}_calibration_implied"] = simulate(n, b, resid_sd)
    cal["power"][f"n{n}_mechanism_sized"] = simulate(n, -0.10, resid_sd)
cal["power"]["n100_null"] = simulate(100, 0.0, resid_sd)
(REPO / "docs/gate13_redundancy_moderator_calibration.json").write_text(json.dumps(cal, indent=2) + "\n")

print("files scanned:", files, "| occurrences in range:", len(occupancy))
print("threshold r*:", R_THR, "| association:", cal["association"], "| fit:", cal["linear_fit"])
for k, v in cal["power"].items():
    print(" ", k, v)
