"""Calibration, gate and allocation for block 7: the same loop-free arm, a liveness gate that can be met.

Block 6 was **void by G0**: Y's asserted set differed from R's on 62 of 100 seeds against a registered 96, while the
same pre-registration printed the calibration's own 6-of-10 liveness beside that bar. The arm was not at fault; the gate
was unreachable. Block 7 changes nothing about the arm, the world, the cap, the readout or the M1 bar, and replaces G0
with a bar calibrated to the observed liveness rate.

Calibration sources, all of them **not judged by block 7**:

  * block 6's 100 cells (seeds 20271614-20271713) -- void by their own gate, so rule 19's re-calibration allowance
    applies, exactly as block 5 used block 4's void cells;
  * the ten dose-calibration seeds (20271604-20271613), run under the same arm.

Two things are estimated from those 110 pairs: the per-seed effect (pooled mean and sd, for M1's power at the unchanged
0.01 bar) and the liveness rate (for G0's bar and G0's own power). The bar is deliberately **not** lowered: block 6's
observed mean was 0.0095, just under 0.01, so the honest consequence is that block 7 is underpowered at M1 and this
artifact says so instead of moving the goalposts.

Writes `docs/gate13_loop_free_block7_calibration.json`. Do not rerun: the allocation is derived from a tree scan, and
this artifact's own seeds would shift it.
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
from pathlib import Path
from benchmarks import engine_stamp

REPO = Path(__file__).resolve().parent.parent
B6 = json.loads((REPO / "docs/gate13_loop_free_block6.json").read_text())
DOSE = json.loads((REPO / "docs/gate13_loop_free_dose_calibration.json").read_text())
SOFT = json.loads((REPO / "docs/gate13_loop_free_admission_calibration.json").read_text())
BAND = [float(x) for x in json.loads((REPO / "docs/gate13_c1_respecification.json").read_text())["band"]]

R6 = B6["seed_rows"]
R10 = DOSE["calibration_rows"]
DIFF = [float(r["diff"]) for r in R6] + [float(r["diff"]) for r in R10]
NOVEL = [float(r["novel_diff"]) for r in R6] + [float(r["y_covered_novel"] - r["r_covered_novel"]) for r in R10]
LOOPD = [float(r["loop_diff"]) for r in R6] + [float(r["y_covered_loop"] - r["r_covered_loop"]) for r in R10]
assert len(DIFF) == 110

LIVE_N = int(B6["gates"]["G0_liveness_y_vs_r"]) + sum(1 for r in SOFT["calibration_rows"] if r["hash_differs"])
LIVE_RATE = LIVE_N / len(DIFF)

BAR = 0.01          # unchanged from block 6, so the two blocks' M1 tests are comparable
G0_BAR = 50         # the arm must change the final structure on at least half the seeds
G0B_BAR = 96        # C vs R, as in blocks 2-6
G2_BAR = 96         # the preference must displace something, as in block 6
N = 100
BARS_SIM = [0.005, 0.0075, 0.01, 0.0125, 0.015]


def binom_tail(n, k, p):
    """P(X >= k) for X ~ Binomial(n, p), exactly."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def power_m1(bar, reps=4000, seed=0):
    rng = random.Random(seed)
    pt = ci = 0
    for _ in range(reps):
        d = [rng.choice(DIFF) for _ in range(N)]
        m = st.fmean(d)
        pt += m >= bar
        if m >= bar:
            se = st.stdev(d) / N ** 0.5
            ci += (m - 1.96 * se) > 0
    return {"bar": bar, "power_point": round(pt / reps, 3), "power_point_and_ci": round(ci / reps, 3)}


def boot_ci(x, reps=4000, seed=0):
    rng = random.Random(seed)
    m = sorted(st.fmean(rng.choice(x) for _ in x) for _ in range(reps))
    return [round(m[100], 5), round(m[3899], 5)]


SEEN, FILES = set(), 0
for p in REPO.rglob("*"):
    if not p.is_file() or p.suffix not in {".py", ".md", ".json"}:
        continue
    if any(part in {".git", ".venv", "node_modules", ".scratch", "__pycache__"} for part in p.parts):
        continue
    FILES += 1
    try:
        text = p.read_text(errors="ignore")
    except OSError:
        continue
    for tok in text.replace(",", " ").replace(":", " ").split():
        if len(tok) == 8 and tok.startswith("2027") and tok.isdigit():
            SEEN.add(int(tok))

START = 20271714
LO = START
while not all((LO + i) not in SEEN for i in range(N)):
    LO += 1
HI = LO + N - 1

cal = {
    "what": "liveness gate, pooled effect and power for block 7 (same loop-free arm, gate calibrated to the observed rate)",
    "judged_by_block": False,
    "arm": DOSE["arm"],
    "changed_from_block6": {
        "G0": f"96/100, which the calibration's own liveness (6/10) could not reach -> {G0_BAR}/100, calibrated to the "
              f"pooled rate {round(LIVE_RATE, 3)}",
        "unchanged": "arm Y, world, cap 20, readout, C1' band, G2 bar, M1 bar 0.01, M2 novel bar 0.005, C/R baselines",
    },
    "calibration_sources": {
        "block6": {"n": len(R6), "seeds": [int(B6["allocation"]["lo"]), int(B6["allocation"]["hi"])],
                   "why": "block 6 was void by its own gate, so its cells are not being judged by block 7; rule 19 "
                          "permits re-calibration on data that is not being judged"},
        "dose_seeds": {"n": len(R10), "seeds": DOSE["calibration_seeds"]},
        "total": len(DIFF),
    },
    "effect": {
        "mean": round(st.fmean(DIFF), 4), "median": round(st.median(DIFF), 4), "sd": round(st.stdev(DIFF), 4),
        "min": min(DIFF), "max": max(DIFF),
        "positive_share": round(sum(1 for d in DIFF if d > 0) / len(DIFF), 3),
        "positive_n": sum(1 for d in DIFF if d > 0), "n": len(DIFF),
        "mean_ci": boot_ci(DIFF), "mean_se_at_100": round(st.stdev(DIFF) / N ** 0.5, 5),
        "novel_mean": round(st.fmean(NOVEL), 3), "novel_ci": boot_ci(NOVEL),
        "loop_covered_mean": round(st.fmean(LOOPD), 4),
        "block6_mean": B6["criteria"]["M1"]["mean_difference"],
        "block6_median": B6["criteria"]["M1"]["median"],
    },
    "liveness": {
        "rate": round(LIVE_RATE, 4), "n_differ": LIVE_N, "n": len(DIFF),
        "block6": int(B6["gates"]["G0_liveness_y_vs_r"]),
        "ten_seeds": sum(1 for r in SOFT["calibration_rows"] if r["hash_differs"]),
        "bar": G0_BAR,
        "bar_rule": "at least half the seeds, a bar the pooled rate clears with the probability below; it is reachable "
                    "by construction, which 96/100 was not",
        "power_of_gate": round(binom_tail(N, G0_BAR, LIVE_RATE), 4),
        "power_of_block6_bar": round(binom_tail(N, 96, LIVE_RATE), 6),
    },
    "gates": {"G0_bar": G0_BAR, "G0b_bar": G0B_BAR, "G2_bar": G2_BAR, "band": BAND},
    "bar": {"m1_mean_difference": BAR, "novel_bar": BAR / 2,
            "provenance": "unchanged from block 6: one fifth of R's gain over C on block 5's 100 fresh seeds, so blocks "
                          "6 and 7 test the same claim at the same bar"},
    "power": {str(b): power_m1(b) for b in BARS_SIM},
    "power_note": f"at the unchanged bar {BAR} the pooled mean {round(st.fmean(DIFF), 4)} sits "
                  f"{round((st.fmean(DIFF) - BAR) / (st.stdev(DIFF) / N ** 0.5), 2)} standard errors from it, so this "
                  f"block is underpowered at M1 and a miss does not distinguish 'no effect' from 'smaller than 0.01'; "
                  f"a pass would be informative",
    "allocation": {"lo": LO, "hi": HI, "seeds": N},
    "freshness": {"files_scanned": FILES, "rejected_hits": sorted(x for x in SEEN if START <= x < LO)},
    "caveat": "the pooled sd is dominated by block 6's void cells, which is the best estimate available and still a "
              "single draw of 110; the block reports its own observed mean and interval beside the bar",
}
(REPO / "docs" / "gate13_loop_free_block7_calibration.json").write_text(json.dumps(engine_stamp.stamp(cal), indent=2) + "\n")

print("liveness:", cal["liveness"])
print("effect:", json.dumps(cal["effect"], indent=1))
print("power:", json.dumps(cal["power"], indent=1))
print("allocation:", LO, HI, "| rejected:", cal["freshness"]["rejected_hits"], "| files:", FILES)
