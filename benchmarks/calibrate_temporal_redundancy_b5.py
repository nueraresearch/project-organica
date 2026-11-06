"""Calibration and power for block 5: the block-4 covariate with its two defects repaired.

Block 4's covariate was o_s = |L and P and W| / |P and W|, the share of the control cell's world-covered temporal
(prediction_candidate) edges that its loops already assert. It failed G2 at 87/100 and could not have met M1's
40-per-half rule. Two causes, both in the specification rather than the treatment:

  (a) the floor was 3. On this world family the control asserts fewer than 3 world-covered temporal edges on ~13% of
      cells, so a 96/100 measurability gate was unreachable. A share with denominator 1 or 2 is coarse, not undefined.
  (b) the cut was the median of 10 calibration seeds (0.3095), which sat far below the distribution's mass (mean 0.719),
      leaving 78 of 87 seeds on the high side.

Block 5 keeps the covariate, drops the floor to 1 (denominator zero is still not measurable), and chooses the cut by a
stated balance rule over 110 non-judged cells. Calibration data: the 10 block-2 seeds and the 100 block-4 seeds. Block 4
was voided by its own gate, so those cells are not being judged here (rule 19's re-calibration allowance).

Writes `docs/gate13_temporal_redundancy_b5_calibration.json`.
"""
from __future__ import annotations

import json
import math
import os
import random
import statistics as st
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")

REPO = Path(__file__).resolve().parent.parent
B2G = {int(p["seed"]): float(p["gain"])
       for p in json.loads((REPO / "docs/gate13_redundancy_moderator_calibration.json").read_text())["pairs"]}
C4 = json.loads((REPO / "docs/gate13_temporal_redundancy_calibration.json").read_text())
B4 = json.loads((REPO / "docs/gate13_temporal_redundancy_block4.json").read_text())

CAND_START = 20271302
FLOOR = 1            # denominator zero is not measurable; 1 and 2 are coarse but defined


def o5(overlap: int, pred_world: int):
    return round(overlap / pred_world, 4) if pred_world >= FLOOR else None


pairs = [{"seed": int(p["seed"]), "overlap": int(p["overlap"]), "pred_world": int(p["pred_world"]),
          "o": o5(int(p["overlap"]), int(p["pred_world"])), "gain": B2G[int(p["seed"])], "source": "block2"}
         for p in C4["pairs"]]
pairs += [{"seed": int(r["seed"]), "overlap": int(r["overlap"]), "pred_world": int(r["pred_world"]),
           "o": o5(int(r["overlap"]), int(r["pred_world"])), "gain": float(r["gain"]), "source": "block4"}
          for r in (B4["seed_rows"] + B4["excluded"])]
pairs.sort(key=lambda p: (p["source"], p["seed"]))
assert len(pairs) == 110 and len({p["seed"] for p in pairs}) == 110

usable = [p for p in pairs if p["o"] is not None]
xs = [p["o"] for p in usable]
ys = [p["gain"] for p in usable]
assert len(usable) >= 100, f"measurable on only {len(usable)} of 110 calibration cells"


def pearson(x, y):
    mx, my = st.fmean(x), st.fmean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


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


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


# Balance rule, fixed before any block-5 cell exists: among the observed values, take the cut that maximises the smaller
# half; ties broken by smaller imbalance, then lower cut. The outcome does not enter the choice.
cands = []
for v in sorted(set(xs)):
    low = sum(1 for x in xs if x < v)
    high = len(xs) - low
    cands.append({"cut": v, "low": low, "high": high, "smaller": min(low, high), "imbalance": abs(low - high)})
best = max(cands, key=lambda c: (c["smaller"], -c["imbalance"], -c["cut"]))
THR = best["cut"]
assert best["smaller"] >= 40, f"no balanced cut on calibration data: {best}"
assert len(set(xs)) >= 5, f"covariate degenerate: {sorted(set(xs))}"

mx, my = st.fmean(xs), st.fmean(ys)
b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
a = my - b * mx
resid = math.sqrt(sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)) / (len(xs) - 2))
low_g = [y for x, y in zip(xs, ys) if x < THR]
high_g = [y for x, y in zip(xs, ys) if x >= THR]
low_m = [x for x in xs if x < THR]
high_m = [x for x in xs if x >= THR]
span = st.fmean(high_m) - st.fmean(low_m)
SLOPE_MECH = round(0.03 / span, 4) if span else 0.0

# sensitivity: the same covariate restricted to the block-4 floor (denominator >= 3)
sub = [(p["o"], p["gain"]) for p in usable if p["pred_world"] >= 3]
SENS = {"n": len(sub), "spearman": round(spearman([u for u, _ in sub], [v for _, v in sub]), 3)}

DIFF_BAR, RHO_BAR, POS_BAR = 0.03, 0.25, 0.66


def simulate(n, slope, sd, reps=4000, seed=0):
    rng = random.Random(seed)
    m1 = m2 = both = m3 = 0
    for _ in range(reps):
        g = [(d["o"], my + slope * (d["o"] - mx) + rng.gauss(0, sd)) for d in (rng.choice(usable) for _ in range(n))]
        lo = [y for x, y in g if x < THR]
        hi = [y for x, y in g if x >= THR]
        ok1 = len(lo) >= 40 and len(hi) >= 40 and (st.median(hi) - st.median(lo)) >= DIFF_BAR
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
    "what": "cut, calibration association and power for block 5 (block-4 covariate, floor lowered, cut re-estimated)",
    "judged_by_block": False,
    "covariate": "o_s = |L_s and P_s and W| / |P_s and W| on the control cell, measurable when |P_s and W| >= 1",
    "floor": FLOOR,
    "fixes_from_block4": {
        "floor": "3 -> 1: at floor 3 only 87/100 block-4 cells were measurable, so G2's 96/100 was unreachable",
        "cut": "median of 10 calibration seeds (0.3095) -> balance-optimal cut over 110 cells",
        "why_not_a_count": "the count |L and P and W| is always defined but carries only Spearman 0.241 on 110 cells "
                           "with an expected half-split gap of 0.015 against a 0.03 bar; it would be a null ritual",
    },
    "calibration_sources": {"block2": 10, "block4": 100, "total": len(pairs), "measurable": len(usable),
                            "note": "block 4 was voided by its own gate, so its cells are not being judged by block 5; "
                                    "rule 19 permits re-calibration on data that is not being judged"},
    "allocation": {"lo": LO, "hi": HI, "seeds": HI - LO + 1},
    "freshness": {"files_scanned": files, "rejected_hits": sorted(x for x in seen if CAND_START <= x < LO)},
    "pairs": pairs,
    "cut_rule": "among observed values, maximise the smaller calibration half; ties by smaller imbalance, then lower cut",
    "cut_candidates": cands,
    "cut_o": THR,
    "calibration_split": {"low_n": len(low_m), "high_n": len(high_m),
                          "low_median_gain": round(st.median(low_g), 4),
                          "high_median_gain": round(st.median(high_g), 4),
                          "observed_difference": round(st.median(high_g) - st.median(low_g), 4)},
    "association": {"pearson": round(pearson(xs, ys), 3), "spearman": round(spearman(xs, ys), 3), "n": len(usable)},
    "linear_fit": {"intercept": round(a, 4), "slope": round(b, 4), "resid_sd": round(resid, 4),
                   "expected_half_split_gap": round(b * span, 4)},
    "sensitivity_floor3": SENS,
    "o_range": {"min": min(xs), "max": max(xs), "mean": round(st.fmean(xs), 4),
                "distinct": sorted(set(round(x, 4) for x in xs))},
    "denominator": {"le2": sum(1 for p in usable if p["pred_world"] <= 2),
                    "min": min(p["pred_world"] for p in usable), "max": max(p["pred_world"] for p in usable)},
    "bars": {"m1_median_gain_difference": DIFF_BAR, "m2_spearman_min": RHO_BAR, "m3_positive_share": POS_BAR},
    "power": {},
}
for label, slope in (("mechanism_sized", SLOPE_MECH), ("calibration_implied", b), ("null", 0.0)):
    cal["power"][f"n100_{label}"] = simulate(100, slope, resid)
(REPO / "docs/gate13_temporal_redundancy_b5_calibration.json").write_text(json.dumps(cal, indent=2) + "\n")

print("o range:", cal["o_range"])
print("denominator <=2:", cal["denominator"])
print("cut o*:", THR, "| split:", cal["calibration_split"], "| sens floor3:", SENS)
print("association:", cal["association"], "| fit:", cal["linear_fit"])
for k, v in cal["power"].items():
    print(" ", k, v)
print("allocation:", LO, HI, "| rejected:", cal["freshness"]["rejected_hits"], "| files:", files)
