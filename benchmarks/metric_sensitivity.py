"""
Metric sensitivity audit.

The question this answers: **can each metric actually move?**

A metric that returns the same number for every colony is not measuring
the difference between the colonies, and running 3,000 cycles per colony
to measure it would be the same mistake as running a degenerate
experiment -- only slower.

For each of M1-M9 this computes the value in every colony, the absolute
spread, and the relative spread, and classifies the metric:

  SENSITIVE          the metric takes different values across colonies
  INSENSITIVE        the metric is (near-)constant across colonies
  STRUCTURALLY ZERO  the metric is identically zero -- it cannot move

The classification is made against the FROZEN definitions in
`docs/FORCE-MATRIX-PREREGISTRATION.md` §2; nothing here redefines a
metric. Metrics that turn out to be insensitive are reported, not
quietly dropped.

Usage:
    python benchmarks/metric_sensitivity.py --matrix docs/force_matrix.json
Writes docs/metric_sensitivity.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def metric_value(metrics: dict, key: str):
    """The canonical scalar for each metric, per the frozen definitions."""
    if key == "M1":
        return metrics["M1_theory_duty_cycle"]["whole_run"]
    if key == "M2":
        return metrics["M2_question_duty_cycle"]["whole_run"]
    if key == "M3":
        return metrics["M3_contradiction_density"]["mean"]
    if key == "M4":
        return metrics["M4_contradiction_survival"]["rate"]
    if key == "M5":
        return metrics["M5_development_velocity"]["new_per_100_cycles"]
    if key == "M6":
        return metrics["M6_lineage_depth"]["max_generation"]
    if key == "M7":
        return metrics["M7_mean_hypothesis_lifetime"]["mean"]
    if key == "M8":
        return metrics["M8_population_stability"]["beliefs"]
    if key == "M9":
        return metrics["M9_cognitive_revolutions"]["revolutions"]
    raise KeyError(key)


NAMES = {
    "M1": "Theory duty cycle",
    "M2": "Question duty cycle",
    "M3": "Contradiction density (mean)",
    "M4": "Contradiction survival",
    "M5": "Development velocity (new/100 cycles)",
    "M6": "Lineage depth (max generation)",
    "M7": "Mean hypothesis lifetime",
    "M8": "Population stability (beliefs)",
    "M9": "Cognitive revolutions",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default=str(REPO / "docs" / "force_matrix.json"))
    ap.add_argument("--out", default=str(REPO / "docs" / "metric_sensitivity.json"))
    args = ap.parse_args()

    path = Path(args.matrix)
    if not path.exists():
        print("matrix artifact not present:", path)
        sys.exit(1)
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = doc["rows"]
    colonies = [r["colony"] for r in rows]

    table = []
    for key in ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"]:
        values = {}
        for r in rows:
            v = metric_value(r["metrics"], key)
            values[r["colony"]] = v
        nums = [v for v in values.values() if v is not None]
        if not nums:
            verdict = "NOT MEASURABLE"
            spread = rel = None
        elif all(v == 0 for v in nums):
            verdict = "STRUCTURALLY ZERO"
            spread = 0.0
            rel = 0.0
        else:
            spread = max(nums) - min(nums)
            base = max(abs(min(nums)), abs(max(nums)))
            rel = round(spread / base, 4) if base else 0.0
            if rel >= 0.05:
                verdict = "SENSITIVE"
            else:
                verdict = "INSENSITIVE"
        table.append({
            "metric": key,
            "name": NAMES[key],
            "values": values,
            "spread": spread,
            "relative_spread": rel,
            "verdict": verdict,
        })

    print("=" * 96)
    print(f"METRIC SENSITIVITY AUDIT -- {doc.get('cycles')} cycles/colony, "
          f"stimulus {doc.get('stimulus')}")
    print("=" * 96)
    header = f"{'metric':<5} {'name':<34}" + "".join(f"{c[:11]:>12}" for c in colonies)
    print(header)
    print("-" * len(header))
    for t in table:
        line = f"{t['metric']:<5} {t['name'][:33]:<34}"
        for c in colonies:
            v = t["values"].get(c)
            line += f"{(str(round(v, 4)) if isinstance(v, (int, float)) else str(v)):>12}"
        print(line)
        print(f"{'':<5} {'':<34}{'spread=' + str(t['spread']) + '  rel=' + str(t['relative_spread']) + '  -> ' + t['verdict']}")
    print()
    n_sens = sum(1 for t in table if t["verdict"] == "SENSITIVE")
    print(f"{n_sens} of {len(table)} metrics are SENSITIVE.")

    try:
        matrix_ref = str(path.relative_to(REPO))
    except ValueError:
        matrix_ref = str(path)

    Path(args.out).write_text(json.dumps({
        "matrix_artifact": matrix_ref,
        "cycles": doc.get("cycles"),
        "stimulus": doc.get("stimulus"),
        "table": table,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
