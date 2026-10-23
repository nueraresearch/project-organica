"""
Gate validation: does Multi-Belief Subject Density predict theory formation?

Jeremy's proposal, 2026-10-23:

    MBSD = (subjects holding >= 2 active beliefs) / (all belief subjects)

with the binding criterion being the ABSOLUTE count (>= 3 subjects with
competition), not the ratio.

Before writing any branch-stimulus code, test the hypothesis against the
11 V1 ablation conditions that already exist. The V1 harness already
recorded, per cycle, the number of subjects holding >= 2 distinct
expectations (`competing_subjects`) alongside the theory count -- so the
numerator of the proposed gate is already in the committed artifact and
needs no new run.

This script answers:
  1. Does the number of competing subjects predict the theory count?
  2. Is the within-cycle relationship an identity (theories == competing
     subjects, capped at MAX_THEORIES)?
  3. If so, which conditions break the identity, and why?

Usage: python benchmarks/gate_validation.py
Writes docs/gate_validation.json
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AB = REPO / "docs" / "ablation_study.json"

MAX_THEORIES = 8


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) *
                    sum((y - my) ** 2 for y in ys))
    return num / den if den else None


def main() -> None:
    ab = json.loads(AB.read_text(encoding="utf-8"))
    conds = ab["conditions"]

    rows = []
    for c in conds:
        hist = c["observations"]["contradiction_history"]
        comp = [h["competing_subjects"] for h in hist]
        th = [h["theories"] for h in hist]
        q = [h["questions"] for h in hist]
        hyps = [h["hypotheses"] for h in hist]

        # Within-cycle identity check.
        capped = [min(x, MAX_THEORIES) for x in comp]
        identity_cycles = sum(1 for a, b in zip(capped, th) if a == b)
        # Correlation across cycles.
        r = pearson(comp, th)

        rows.append({
            "condition": c["condition"],
            "name": c["name"],
            "final_theories": c["final_populations"].get("G5 theories", 0),
            "final_questions": c["final_populations"].get("G5 questions", 0),
            "final_hypotheses": c["final_populations"].get("G4 hypotheses", 0),
            "competing_subjects_mean": round(statistics.fmean(comp), 3),
            "competing_subjects_max": max(comp),
            "competing_subjects_p95": sorted(comp)[max(0, math.ceil(0.95 * len(comp)) - 1)],
            "theories_mean": round(statistics.fmean(th), 3),
            "theories_max": max(th),
            "identity_cycles": identity_cycles,
            "identity_pct": round(100 * identity_cycles / len(hist), 1),
            "corr_competing_theories": (round(r, 4) if r is not None else None),
            "g2_processes": c["final_populations"].get("G2 processes", 0),
            "g3_workflows": c["final_populations"].get("G3 workflows", 0),
        })

    print("=== MBSD GATE VALIDATION (from docs/ablation_study.json) ===\n")
    hdr = (f"{'cond':<8}{'name':<26}{'compSubj':>9}{'max':>5}{'finalT':>8}"
           f"{'T_mean':>8}{'ident%':>8}{'r':>8}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['condition']:<8}{r['name']:<26}"
              f"{r['competing_subjects_mean']:>9.2f}{r['competing_subjects_max']:>5}"
              f"{r['final_theories']:>8}{r['theories_mean']:>8.2f}"
              f"{r['identity_pct']:>8.1f}"
              f"{(r['corr_competing_theories'] if r['corr_competing_theories'] is not None else float('nan')):>8.3f}")

    # Cross-condition correlation: final theory count vs competing subjects.
    xt = [r["final_theories"] for r in rows]
    xc = [r["competing_subjects_mean"] for r in rows]
    xm = [r["competing_subjects_max"] for r in rows]
    r_final = pearson(xc, xt)
    r_max = pearson(xm, xt)

    # The same, excluding the condition that bypasses Layer 4 by design.
    normal = [r for r in rows if r["condition"] != "F"]
    r_final_normal = pearson([r["competing_subjects_mean"] for r in normal],
                              [r["final_theories"] for r in normal])
    r_max_normal = pearson([r["competing_subjects_max"] for r in normal],
                            [r["final_theories"] for r in normal])

    print("\n=== CROSS-CONDITION ===")
    print(f"corr(mean competing subjects, final theories)      = {r_final:.4f}")
    print(f"corr(max  competing subjects, final theories)      = {r_max:.4f}")
    print(f"  ... excluding F (bypasses Layer 4 by design)     = "
          f"{r_final_normal:.4f} / {r_max_normal:.4f}")

    # "Does every high-theory condition have high MBSD?"
    print("\n=== HIGH-THEORY vs HIGH-COMPETING-SUBJECTS ===")
    high_t = [r for r in rows if r["final_theories"] >= 3]
    for r in high_t:
        ok = r["competing_subjects_max"] >= 3
        print(f"  {r['condition']:<4} {r['name']:<26} theories={r['final_theories']:<3}"
              f" maxCompetingSubjects={r['competing_subjects_max']:<3}"
              f" -> {'HAS >=3 competing subjects' if ok else '*** VIOLATES THE GATE ***'}")

    # Which conditions break the within-cycle identity, and why.
    print("\n=== IDENTITY BREAKS (theories != min(competing_subjects, 8)) ===")
    for r in rows:
        if r["identity_pct"] < 100.0:
            print(f"  {r['condition']:<4} {r['name']:<26} identity holds in "
                  f"{r['identity_pct']}% of cycles   "
                  f"(G2 processes={r['g2_processes']}, G3 workflows={r['g3_workflows']})")

    out = {
        "generated_at": "2026-10-23T07:05:00Z",
        "purpose": "Validate the proposed Multi-Belief Subject Density gate "
                   "against the 11 existing V1 conditions, before designing "
                   "any branch-structured stimulus.",
        "source": "docs/ablation_study.json (observations.contradiction_history)",
        "rows": rows,
        "cross_condition": {
            "corr_mean_competing_vs_final_theories": (round(r_final, 4)
                                                      if r_final is not None else None),
            "corr_max_competing_vs_final_theories": (round(r_max, 4)
                                                     if r_max is not None else None),
            "corr_mean_excluding_F": (round(r_final_normal, 4)
                                      if r_final_normal is not None else None),
            "corr_max_excluding_F": (round(r_max_normal, 4)
                                     if r_max_normal is not None else None),
        },
    }
    p = REPO / "docs" / "gate_validation.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()
