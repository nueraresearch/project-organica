"""Calibration, allocation and power for block 6: the loop-free preference arm.

The intervention manipulates admission instead of measuring a between-seed covariate: X is R with one
extra sort key, so a candidate whose edge a loop already asserts sorts after one that no loop asserts.
Two things have to be measured before that can be frozen honestly:

  (a) **Does the preference bind?** If loops rarely assert any edge competing for the top of the ratio
      ordering, the arm changes nothing and a 300-cell block would be a null ritual (rule 25(d)).
  (b) **How large is the effect, and what bar is worth claiming?** The paired difference X - R on
      coverage, and the power of candidate bars at that effect.

Calibration runs R and X on ten fresh seeds. Those seeds are not judged by the block, and the block's
allocation is chosen afterwards from the tree *plus* the calibration seeds, so the two never overlap
(rule 19). Writes `docs/gate13_loop_free_admission_calibration.json`.

Do not rerun this script: each run's artifact is scanned for seed tokens, so a rerun would move the
allocation. One run, one allocation.
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
from benchmarks import engine_stamp

CAND_START = 20271603      # first candidate after block 5's 20271403-20271502
N_CAL = 10
BARS = [0.005, 0.01, 0.015, 0.02, 0.03]


def scan_tokens() -> tuple[set[int], int]:
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
    return seen, files


def first_free_run(present: set[int], start: int, length: int) -> int:
    s = start
    while not all((s + i) not in present for i in range(length)):
        s += 1
    return s


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


SEEN, FILES = scan_tokens()
CAL_LO = first_free_run(SEEN, CAND_START, N_CAL)
CAL_SEEDS = list(range(CAL_LO, CAL_LO + N_CAL))
print(f"calibration seeds {CAL_LO}-{CAL_LO + N_CAL - 1} (files scanned {FILES})", flush=True)

rows = []
for seed in CAL_SEEDS:
    r = run_cell("R", seed)
    x = run_cell("X", seed)
    row = {
        "seed": seed,
        "r_coverage": r["coverage"], "x_coverage": x["coverage"],
        "diff": round(x["coverage"] - r["coverage"], 4),
        "r_asserted": r["asserted"], "x_asserted": x["asserted"],
        "r_precision": r["precision"], "x_precision": x["precision"],
        "r_covered": r["covered"], "x_covered": x["covered"],
        "r_covered_loop": r["covered_loop"], "x_covered_loop": x["covered_loop"],
        "r_covered_novel": r["covered_novel"], "x_covered_novel": x["covered_novel"],
        "loop_edges": r["loop_edges"], "r_asserted_loop": r["asserted_loop"], "x_asserted_loop": x["asserted_loop"],
        "disp_total": x.get("disp_total", 0), "disp_cycles": x.get("disp_cycles", 0),
        "disp_max": x.get("disp_max", 0), "disp_mean": x.get("disp_mean", 0.0),
        "hash_differs": r["asserted_hash"] != x["asserted_hash"],
        "runtime_s": round(r["runtime_s"] + x["runtime_s"], 1),
    }
    rows.append(row)
    print(json.dumps(row), flush=True)

diffs = [r["diff"] for r in rows]
disp = [r["disp_total"] for r in rows]
cycles_with_disp = [r["disp_cycles"] for r in rows]
mean_d, median_d = st.fmean(diffs), st.median(diffs)
sd_d = st.stdev(diffs) if len(diffs) > 1 else 0.0
sign_share = sum(1 for d in diffs if d > 0) / len(diffs)
binds_seeds = sum(1 for d in disp if d > 0)

# The allocation is chosen after calibration, excluding the calibration seeds themselves.
present = set(SEEN) | set(CAL_SEEDS)
BLOCK_LO = first_free_run(present, CAL_LO + N_CAL, 100)
BLOCK_HI = BLOCK_LO + 99


def power(n, bar, sign_bar, reps=4000, seed=0):
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


SIGN_BAR = 0.60
cal = {
    "what": "effect size, perturbation size, allocation and power for block 6 (loop-free preference arm X vs R)",
    "judged_by_block": False,
    "arm": "X = R with loop-asserted edges sorted last at admission; identical construction, cap, world and readout",
    "calibration_seeds": CAL_SEEDS,
    "calibration_rows": rows,
    "effect": {
        "mean": round(mean_d, 4), "median": round(median_d, 4), "sd": round(sd_d, 4),
        "min": min(diffs), "max": max(diffs),
        "positive_share": round(sign_share, 3), "positive_n": sum(1 for d in diffs if d > 0),
        "n": len(diffs),
        "spearman_vs_disp": (round(pearson(ranks(disp), ranks(diffs)), 3)
                             if len(set(disp)) > 1 and len(set(diffs)) > 1 else None),
        "mean_r_coverage": round(st.fmean(r["r_coverage"] for r in rows), 4),
        "mean_x_coverage": round(st.fmean(r["x_coverage"] for r in rows), 4),
    },
    "perturbation": {
        "seeds_with_any_displacement": binds_seeds,
        "mean_disp_total": round(st.fmean(disp), 3),
        "median_disp_total": st.median(disp),
        "max_disp_total": max(disp),
        "min_disp_total": min(disp),
        "mean_cycles_with_displacement": round(st.fmean(cycles_with_disp), 1),
        "hash_differs_seeds": sum(1 for r in rows if r["hash_differs"]),
        "loop_edges_mean": round(st.fmean(r["loop_edges"] for r in rows), 2),
        "r_asserted_loop_mean": round(st.fmean(r["r_asserted_loop"] for r in rows), 2),
    },
    "composition": {
        "r_covered_loop_mean": round(st.fmean(r["r_covered_loop"] for r in rows), 2),
        "x_covered_loop_mean": round(st.fmean(r["x_covered_loop"] for r in rows), 2),
        "r_covered_novel_mean": round(st.fmean(r["r_covered_novel"] for r in rows), 2),
        "x_covered_novel_mean": round(st.fmean(r["x_covered_novel"] for r in rows), 2),
    },
    "allocation": {"lo": BLOCK_LO, "hi": BLOCK_HI, "seeds": 100},
    "allocation_rule": "first free 100-seed window after the calibration block, scanned over the tree plus the "
                       "calibration seeds; an allocation may not contain a seed already written into the tree",
    "bars_simulated": BARS,
    "sign_bar": SIGN_BAR,
    "power": {str(b): power(100, b, SIGN_BAR) for b in BARS},
    "caveat": "ten calibration seeds give a noisy sd; the power table is an estimate from them, not a guarantee, "
              "and the block reports its own observed effect beside the bar either way",
}
(REPO / "docs" / "gate13_loop_free_admission_calibration.json").write_text(json.dumps(engine_stamp.stamp(cal), indent=2) + "\n")

print("effect:", cal["effect"])
print("perturbation:", cal["perturbation"])
print("composition:", cal["composition"])
for b, p in cal["power"].items():
    print(" power", b, p)
print("allocation:", BLOCK_LO, BLOCK_HI)
