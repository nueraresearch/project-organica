"""Score block 2 against the criteria frozen in docs/GATE13-RATIO-BLOCK2-PREREGISTRATION.md.

Reads the raw cells (one JSON line per arm/cap/seed) and evaluates C0, C1', C2, C3, C4 once, in that order, then
applies the pre-registered decision table. Writes `docs/gate13_ratio_block2.json`.

C1' is the comparability criterion from `docs/gate13_c1_respecification.json`: the block mean of arm C's cap-20
precision must lie within the frozen margin of the structural comparator 0.4667. The margin is read from the
calibration artifact -- it is never recomputed from this block, and nothing here may be re-specified after the fact.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as st
from pathlib import Path

BASE, N, CAPS, CR = 0.4667, 25, (20, 100, 1000), (10, 20, 100, 1000)


def sign_test_p(k: int, n: int) -> float:
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", nargs="+", default=[".scratch/ratio_block2.jsonl"])
    ap.add_argument("--out", default="docs/gate13_ratio_block2.json")
    args = ap.parse_args()

    rows = []
    for p in args.jsonl:
        rows += [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
    cell = {(r["arm"], r["cap"], r["seed"]): r for r in rows}
    seeds = sorted({r["seed"] for r in rows})
    assert len(seeds) == N, f"expected {N} seeds, found {len(seeds)}"
    assert len(rows) == 275, f"expected 275 cells, found {len(rows)}"
    g = lambda a, c, s: cell[(a, c, s)]  # noqa: E731

    respec = json.loads(Path("docs/gate13_c1_respecification.json").read_text())
    delta, band = respec["margin"]["chosen"], respec["band"]

    by_cap = {c: sum(1 for s in seeds if g("R", c, s)["asserted_hash"] != g("C", c, s)["asserted_hash"]) for c in CR}
    full = {"C": sum(1 for s in seeds if g("C", 1000, s)["coverage"] == 1.0),
            "R": sum(1 for s in seeds if g("R", 1000, s)["coverage"] == 1.0)}
    c0_pass = by_cap[20] >= 21

    c_prec = [g("C", 20, s)["precision"] for s in seeds]
    c1_mean = st.fmean(c_prec)
    c1_pass = abs(c1_mean - BASE) <= delta
    c1_dir = "high" if c1_mean > BASE + delta else ("low" if c1_mean < BASE - delta else "in band")

    c2_rows = [{"seed": s, "C_distinct": g("C", 20, s)["distinct_values"],
                "R_distinct": g("R", 20, s)["distinct_values"],
                "passes": g("R", 20, s)["distinct_values"] >= 3 * g("C", 20, s)["distinct_values"]} for s in seeds]
    c2_n = sum(r["passes"] for r in c2_rows)

    c3_rows = [{"seed": s, "C_coverage": g("C", 20, s)["coverage"], "R_coverage": g("R", 20, s)["coverage"],
                "delta": round(g("R", 20, s)["coverage"] - g("C", 20, s)["coverage"], 4),
                "passes": g("R", 20, s)["coverage"] > g("C", 20, s)["coverage"]} for s in seeds]
    c3_n = sum(r["passes"] for r in c3_rows)
    p3 = sign_test_p(c3_n, N)

    c4_rows = []
    for s in seeds:
        c20, r20 = g("C", 20, s), g("R", 20, s)
        pts = sorted((g("R", c, s)["asserted"], g("R", c, s)["precision"]) for c in CR)
        size, interp = c20["asserted"], None
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= size <= x1 and x1 > x0:
                interp = round(y0 + (y1 - y0) * (size - x0) / (x1 - x0), 4)
                break
        c4_rows.append({"seed": s, "C_precision": c20["precision"], "R_precision": r20["precision"],
                        "same_cap_delta": round(r20["precision"] - c20["precision"], 4),
                        "size_matched_delta": None if interp is None else round(interp - c20["precision"], 4)})
    sd = [r["same_cap_delta"] for r in c4_rows]
    matched = [r for r in c4_rows if r["size_matched_delta"] is not None]
    c4_median, c4_min = st.median(sd), min(sd)
    c4_pass = c4_median >= -0.02 and c4_min >= -0.05 and all(r["size_matched_delta"] >= -0.02 for r in matched)

    if not c0_pass:
        verdict = "INVALID"
    elif not c1_pass:
        verdict = "NOT COMPARABLE"
    elif c2_n < 21:
        verdict = "TIE NOT BROKEN"
    elif c3_n < 21:
        verdict = "TREATMENT NOT REPRODUCED"
    elif not c4_pass:
        verdict = "COVERAGE GAIN AT PRECISION COST"
    else:
        verdict = "CONFIRMED"

    per_cap = {a: {str(c): {"coverage_median": round(st.median([g(a, c, s)["coverage"] for s in seeds]), 4),
                            "precision_median": round(st.median([g(a, c, s)["precision"] for s in seeds]), 4),
                            "asserted_median": st.median([g(a, c, s)["asserted"] for s in seeds])}
                     for c in (CR if a in ("C", "R") else CAPS)} for a in ("C", "R", "E")}
    marg = {}
    for a in ("C", "R"):
        dw = sum(g(a, 1000, s)["covered"] - g(a, 20, s)["covered"] for s in seeds)
        dn = sum(g(a, 1000, s)["asserted"] - g(a, 20, s)["asserted"] for s in seeds)
        marg[a] = {"d_world": dw, "d_asserted": dn, "marginal_precision": round(dw / dn, 4)}

    art = {
        "block": "2", "preregistration": "docs/GATE13-RATIO-BLOCK2-PREREGISTRATION.md",
        "allocations": f"{seeds[0]}-{seeds[-1]}", "seeds": seeds, "cells": len(rows), "hash_seed": 0,
        "commit": sorted({r.get("commit", "unknown") for r in rows}),
        "verdict": verdict,
        "C0": {"passes": c0_pass, "hash_differs_by_cap": {str(k): v for k, v in by_cap.items()},
               "note": "cap 1000 coincides by construction: both arms reach the full pool",
               "cap1000_full": full},
        "C1p": {"passes": c1_pass, "delta": delta, "band": band, "mean_C_precision": round(c1_mean, 4),
                "offset_from_base": round(c1_mean - BASE, 4), "direction": c1_dir, "seeds": len(seeds),
                "reference_mean": respec["reference"]["mean"], "reference_se": respec["reference"]["se_of_block_mean"]},
        "C2": {"passes": c2_n >= 21, "seeds_passing": c2_n,
               "min_ratio": round(min(r["R_distinct"] / r["C_distinct"] for r in c2_rows), 2), "rows": c2_rows},
        "C3": {"passes": c3_n >= 21, "seeds_passing": c3_n, "sign_test_p": round(p3, 8),
               "median_delta": round(st.median([r["delta"] for r in c3_rows]), 4), "rows": c3_rows},
        "C4": {"passes": c4_pass, "median_delta": round(c4_median, 4), "min_delta": round(c4_min, 4),
               "seeds_falling": sum(1 for x in sd if x < 0), "bracketed": len(matched), "rows": c4_rows},
        "per_cap": per_cap, "marginal_cap20_to_1000": marg, "raw": rows,
    }
    Path(args.out).write_text(json.dumps(art, indent=2) + "\n")
    print(f"verdict: {verdict}")
    print(f"C0 {'pass' if c0_pass else 'FAIL'} digest-diffs {by_cap} cap1000 full {full}")
    print(f"C1' {'pass' if c1_pass else 'FAIL'} mean {c1_mean:.4f} offset {c1_mean - BASE:+.4f} band {band} ({c1_dir})")
    print(f"C2 {c2_n}/25 (min ratio {art['C2']['min_ratio']})  C3 {c3_n}/25 p {p3:.2g} med {art['C3']['median_delta']:+.4f}")
    print(f"C4 {'pass' if c4_pass else 'FAIL'} med {c4_median:+.4f} min {c4_min:+.4f} falling {art['C4']['seeds_falling']}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
