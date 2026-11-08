"""Calibration, allocation and power for block 8: does the loop-free admission gain scale with the cap?

Block 7 established that at cap 20 arm Y beats arm R on coverage by 0.0127 (M1 pass, M2 pass). Block 8 asks whether
that gain grows when the admission budget grows: caps **40** and **100**, arms **R and Y**, fresh seeds. Arm C is not
run: the claim under test is Y versus R, and the comparability question here is whether the cap axis is live, which the
block's own R cells answer (R at 100 must beat R at 40).

Calibration runs ten fresh seeds at both caps (40 cells) and records, per seed, the two paired gains and their
difference — the difference-in-differences that M1 tests. Nothing about the calibration seeds is judged by the block;
the block's allocation is chosen afterwards from the tree plus those seeds, so the two never overlap.

Writes `docs/gate13_loop_free_cap_calibration.json`. Do not rerun: the allocation is derived from a tree scan and this
artifact's own seeds would shift it.
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

CAND_START = 20271815     # first candidate after block 7's 20271715-20271814
N_CAL = 10
CAPS = (40, 100)
N = 100
BAR = 0.01                # DiD bar: the same size as blocks 6-7's M1 bar, and the effect block 7 measured at cap 20
G0_BAR = 50
G2_BAR = 96
BARS = [0.005, 0.01, 0.015, 0.02]


def scan_tokens():
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


def first_free_run(present, start, length):
    s = start
    while not all((s + i) not in present for i in range(length)):
        s += 1
    return s


def boot_ci(x, reps=4000, seed=0):
    rng = random.Random(seed)
    m = sorted(st.fmean(rng.choice(x) for _ in x) for _ in range(reps))
    return [round(m[100], 5), round(m[3899], 5)]


def power(bar, reps=4000, seed=0):
    rng = random.Random(seed)
    pt = ci = 0
    for _ in range(reps):
        d = [rng.choice(DID) for _ in range(N)]
        m = st.fmean(d)
        pt += m >= bar
        if m >= bar:
            se = st.stdev(d) / N ** 0.5
            ci += (m - 1.96 * se) > 0
    return {"bar": bar, "power_point": round(pt / reps, 3), "power_point_and_ci": round(ci / reps, 3)}


SEEN, FILES = scan_tokens()
CAL_LO = first_free_run(SEEN, CAND_START, N_CAL)
CAL_SEEDS = list(range(CAL_LO, CAL_LO + N_CAL))
print(f"calibration seeds {CAL_LO}-{CAL_LO + N_CAL - 1} (files {FILES})", flush=True)

rows, per_seed = [], []
for seed in CAL_SEEDS:
    by_cap = {}
    for cap in CAPS:
        r = run_cell("R", seed, cap)
        y = run_cell("Y", seed, cap)
        by_cap[cap] = (r, y)
        row = {"seed": seed, "cap": cap,
               "r_coverage": r["coverage"], "y_coverage": y["coverage"],
               "diff": round(y["coverage"] - r["coverage"], 4),
               "r_asserted": r["asserted"], "y_asserted": y["asserted"],
               "r_precision": r["precision"], "y_precision": y["precision"],
               "r_covered_loop": r["covered_loop"], "y_covered_loop": y["covered_loop"],
               "r_covered_novel": r["covered_novel"], "y_covered_novel": y["covered_novel"],
               "disp_total": y.get("disp_total", 0), "disp_cycles": y.get("disp_cycles", 0),
               "hash_differs": r["asserted_hash"] != y["asserted_hash"],
               "runtime_s": round(r["runtime_s"] + y["runtime_s"], 1)}
        rows.append(row)
        print(json.dumps(row), flush=True)
    d40 = by_cap[40][1]["coverage"] - by_cap[40][0]["coverage"]
    d100 = by_cap[100][1]["coverage"] - by_cap[100][0]["coverage"]
    per_seed.append({"seed": seed, "d40": round(d40, 4), "d100": round(d100, 4),
                     "did": round(d100 - d40, 4),
                     "r40": by_cap[40][0]["coverage"], "r100": by_cap[100][0]["coverage"],
                     "r_lift": round(by_cap[100][0]["coverage"] - by_cap[40][0]["coverage"], 4)})

D40 = [p["d40"] for p in per_seed]
D100 = [p["d100"] for p in per_seed]
DID = [p["did"] for p in per_seed]
LIFT = [p["r_lift"] for p in per_seed]
live40 = sum(1 for r in rows if r["cap"] == 40 and r["hash_differs"])
live100 = sum(1 for r in rows if r["cap"] == 100 and r["hash_differs"])
disp40 = [r["disp_total"] for r in rows if r["cap"] == 40]
disp100 = [r["disp_total"] for r in rows if r["cap"] == 100]

present = set(SEEN) | set(CAL_SEEDS)
BLOCK_LO = first_free_run(present, CAL_LO + N_CAL, N)
BLOCK_HI = BLOCK_LO + N - 1

cal = {
    "what": "paired gains at caps 40 and 100, difference-in-differences, liveness, axis liveness, power and allocation "
            "for block 8 (does the loop-free admission gain scale with the cap?)",
    "judged_by_block": False,
    "arms": ["R", "Y"],
    "caps": list(CAPS),
    "calibration_seeds": CAL_SEEDS,
    "calibration_rows": rows,
    "per_seed": per_seed,
    "effect": {
        "d40_mean": round(st.fmean(D40), 4), "d40_median": round(st.median(D40), 4), "d40_ci": boot_ci(D40),
        "d100_mean": round(st.fmean(D100), 4), "d100_median": round(st.median(D100), 4), "d100_ci": boot_ci(D100),
        "did_mean": round(st.fmean(DID), 4), "did_median": round(st.median(DID), 4),
        "did_sd": round(st.stdev(DID), 4), "did_ci": boot_ci(DID),
        "did_positive_n": sum(1 for d in DID if d > 0), "did_n": len(DID),
        "r_lift_mean": round(st.fmean(LIFT), 4), "r_lift_ci": boot_ci(LIFT),
        "r40_mean": round(st.fmean(p["r40"] for p in per_seed), 4),
        "r100_mean": round(st.fmean(p["r100"] for p in per_seed), 4),
    },
    "liveness": {
        "by_cap": {"40": live40, "100": live100}, "n_per_cap": N_CAL, "bar": G0_BAR,
        "rate": round((live40 + live100) / (2 * N_CAL), 3),
        "bar_rule": "at least half the seeds at each cap, fixed from block 7's calibrated bar; it is reachable by "
                    "construction",
    },
    "perturbation": {
        "by_cap_mean": {"40": round(st.fmean(disp40), 2), "100": round(st.fmean(disp100), 2)},
        "seeds_moved_by_cap": {"40": sum(1 for d in disp40 if d > 0), "100": sum(1 for d in disp100 if d > 0)},
        "bar": G2_BAR,
    },
    "gates": {"G0_bar": G0_BAR, "G2_bar": G2_BAR, "axis": "mean R coverage at cap 100 must exceed cap 40 with the "
                                                           "bootstrap interval above zero, otherwise the cap axis is "
                                                           "not live and no scaling claim can be read"},
    "bar": {"did": BAR,
            "provenance": "the same bar blocks 6 and 7 used for the gain itself: one fifth of R's gain over C at cap 20 "
                          "(0.0485). Here it is applied to the change in that gain between caps 40 and 100, so the "
                          "claim is that doubling-and-then-some the budget adds at least a block-7-sized gain"},
    "power": {str(b): power(b) for b in BARS},
    "caveat": "ten calibration seeds give a noisy sd for the difference-in-differences, which is a noisier quantity "
              "than either gain; the power table is an estimate and the block reports its own mean and interval beside "
              "the bar",
    "allocation": {"lo": BLOCK_LO, "hi": BLOCK_HI, "seeds": N},
    "allocation_rule": "first free 100-seed window after the calibration block, scanned over the tree plus the "
                       "calibration seeds",
    "freshness": {"files_scanned": FILES, "rejected_hits": sorted(x for x in SEEN if CAND_START <= x < CAL_LO)},
}
(REPO / "docs" / "gate13_loop_free_cap_calibration.json").write_text(json.dumps(engine_stamp.stamp(cal), indent=2) + "\n")

print("effect:", json.dumps(cal["effect"], indent=1))
print("liveness:", cal["liveness"], "| perturbation:", cal["perturbation"])
print("power:", json.dumps(cal["power"], indent=1))
print("allocation:", BLOCK_LO, BLOCK_HI)
