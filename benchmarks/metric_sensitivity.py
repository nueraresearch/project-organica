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

# Metrics that ARE a colony's intervention, rather than a consequence of it.
# NO_QUESTIONS disables question creation, so M2 (question duty cycle) reads
# zero by construction; NO_CONTRADICTIONS scales contradiction to zero, so
# M3 and M4 read the intervention rather than its consequences. These are
# excluded from the DOWNSTREAM deviation ranking only -- the raw ranking and
# the per-metric tables still report them in full, because a switch that does
# not flip its own metric is a finding in itself.
OWN_METRIC = {
    "NO_QUESTIONS": ("M2",),
    "NO_CONTRADICTIONS": ("M3", "M4"),
    "NO_DREAMS": (),
    "ANTI_EIG": (),
    "SALIENCE": (),
    "FULL": (),
}


def distance_from_reference(values: dict, ref: str) -> dict:
    """How far each colony sits from the reference arm.

    The campaign's claim is always a comparison, and the reference arm is
    FULL. Reporting a raw spread says "these colonies differ"; it does not
    say which one is the odd one out. This does.
    """
    base = values.get(ref)
    out = {}
    for colony, v in values.items():
        if not isinstance(base, (int, float)) or not isinstance(v, (int, float)):
            out[colony] = {"absolute": None, "relative": None}
            continue
        absolute = abs(v - base)
        scale = max(abs(base), abs(v))
        out[colony] = {
            "absolute": round(absolute, 6),
            "relative": round(absolute / scale, 6) if scale else 0.0,
        }
    return out


def most_sensitive(values: dict, ref: str) -> str | None:
    """The colony furthest from the reference arm."""
    dists = distance_from_reference(values, ref)
    candidates = [(d["relative"], c) for c, d in dists.items()
                  if c != ref and d["relative"] is not None]
    if not candidates:
        return None
    best_rel = max(r for r, _ in candidates)
    if best_rel == 0:
        return None
    # Ties are reported by the first colony in a stable order, and the
    # caller sees the same number for every tied colony.
    for r, c in candidates:
        if r == best_rel:
            return c
    return None


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
    ref = "FULL" if "FULL" in colonies else (colonies[0] if colonies else None)
    if ref is None:
        print("no colonies in the artifact")
        sys.exit(1)

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
            "distance_from_reference": distance_from_reference(values, ref),
            "most_sensitive_colony": most_sensitive(values, ref),
        })

    # ---- the populations, which carry the signal the duty cycles lose ------
    pop_table = []
    for name, key in [("theories", "theories_mean"),
                      ("questions", "questions_mean"),
                      ("dreams", "dreams_mean"),
                      ("experiments", "experiments_mean"),
                      ("pre_beliefs", "pre_beliefs_mean"),
                      ("pre_ge2", "pre_ge2_mean")]:
        values = {}
        for r in rows:
            try:
                values[r["colony"]] = r["metrics"]["_populations"][key]
            except Exception:
                values[r["colony"]] = None
        nums = [v for v in values.values() if isinstance(v, (int, float))]
        if not nums:
            continue
        spread = max(nums) - min(nums)
        base = max(abs(min(nums)), abs(max(nums)))
        pop_table.append({
            "population": name,
            "values": values,
            "spread": round(spread, 6),
            "relative_spread": round(spread / base, 4) if base else 0.0,
            "distance_from_reference": distance_from_reference(values, ref),
            "most_sensitive_colony": most_sensitive(values, ref),
        })

    # ---- which colony deviates most overall ------------------------------
    #
    # A colony that DISABLES a mechanism zeroes the metric that measures
    # that mechanism. Counting that as deviation would rank NO_QUESTIONS
    # first for M2 (0 vs 0.9967) when the only thing it shows is that the
    # switch works. The interesting quantity is the DOWNSTREAM effect: what
    # the organism does differently once the mechanism is gone. So the
    # deviation is reported twice -- raw, and with each colony's own
    # intervention metric excluded.
    deviation = []
    for c in colonies:
        if c == ref:
            continue
        rels = []
        for t in table:
            d = t["distance_from_reference"].get(c)
            if d is not None:
                rels.append(d["relative"])
        down_rels = []
        excluded = OWN_METRIC.get(c, ())
        for t in table:
            if t["metric"] in excluded:
                continue
            d = t["distance_from_reference"].get(c)
            if d is not None:
                down_rels.append(d["relative"])
        deviation.append({
            "colony": c,
            "mean_relative_distance": round(
                sum(rels) / len(rels), 5) if rels else 0.0,
            "max_relative_distance": round(max(rels), 5) if rels else 0.0,
            "metrics_moved": sum(1 for r in rels if r > 0),
            "excluded_own_metrics": list(excluded),
            "downstream_mean_relative_distance": round(
                sum(down_rels) / len(down_rels), 5) if down_rels else 0.0,
            "downstream_metrics_moved": sum(1 for r in down_rels if r > 0),
        })
    deviation.sort(key=lambda d: d["mean_relative_distance"], reverse=True)
    by_dev = list(deviation)
    downstream = sorted(
        deviation,
        key=lambda d: d["downstream_mean_relative_distance"], reverse=True)

    print("=" * 96)
    print(f"METRIC SENSITIVITY AUDIT -- {doc.get('cycles')} cycles/colony, "
          f"stimulus {doc.get('stimulus')}")
    print(f"reference arm: {ref}")
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
    print()
    print("MOST SENSITIVE COLONY PER METRIC (furthest from the reference arm)")
    print("-" * 96)
    print(f"{'metric':<5} {'name':<34} {'most sensitive colony':<24} "
          f"{'abs dist':>10} {'rel dist':>10}")
    for t in table:
        ms = t["most_sensitive_colony"]
        d = t["distance_from_reference"].get(ms, {}) if ms else {}
        print(f"{t['metric']:<5} {t['name'][:33]:<34} {str(ms):<24} "
              f"{str(round(d.get('absolute', 0), 4)):>10} "
              f"{str(d.get('relative', 0)):>10}")
    print()
    print("POPULATIONS -- the signal the saturated duty cycles lose")
    print("-" * 96)
    header = f"{'population':<14}" + "".join(f"{c[:11]:>12}" for c in colonies)
    print(header)
    for p in pop_table:
        line = f"{p['population']:<14}"
        for c in colonies:
            v = p["values"].get(c)
            line += f"{(str(round(v, 4)) if isinstance(v, (int, float)) else str(v)):>12}"
        print(line)
        print(f"{'':<14}{'spread=' + str(p['spread']) + '  rel=' + str(p['relative_spread']) + '  most sensitive: ' + str(p['most_sensitive_colony'])}")
    print()
    print("DEVIATION FROM THE REFERENCE ARM, OVERALL")
    print("-" * 96)
    print(f"{'colony':<22} {'mean rel dist':>14} {'max rel dist':>14} "
          f"{'metrics moved':>14}")
    for d in by_dev:
        print(f"{d['colony']:<22} {d['mean_relative_distance']:>14} "
              f"{d['max_relative_distance']:>14} {d['metrics_moved']:>14}")
    print()
    print("DOWNSTREAM DEVIATION -- each colony's OWN intervention metric excluded")
    print("-" * 96)
    print("A colony that disables a mechanism zeroes the metric that measures")
    print("that mechanism. That is the switch working, not a finding. This")
    print("ranking excludes it and asks what the organism does DIFFERENTLY.")
    print(f"{'colony':<22} {'mean rel dist':>14} {'metrics moved':>14} "
          f"{'excluded':<26}")
    for d in downstream:
        print(f"{d['colony']:<22} {d['downstream_mean_relative_distance']:>14} "
              f"{d['downstream_metrics_moved']:>14} "
              f"{','.join(d['excluded_own_metrics']) or '-':<26}")
    print()
    if len(downstream) > 1:
        print(f"By raw deviation: the most surprising colony is "
              f"**{by_dev[0]['colony']}** "
              f"(mean relative distance {by_dev[0]['mean_relative_distance']}).")
        print(f"By downstream deviation: the most surprising colony is "
              f"**{downstream[0]['colony']}** "
              f"(mean relative distance "
              f"{downstream[0]['downstream_mean_relative_distance']}), "
              f"then {downstream[1]['colony']} "
              f"({downstream[1]['downstream_mean_relative_distance']}).")

    try:
        matrix_ref = str(path.relative_to(REPO))
    except ValueError:
        matrix_ref = str(path)

    Path(args.out).write_text(json.dumps({
        "matrix_artifact": matrix_ref,
        "cycles": doc.get("cycles"),
        "stimulus": doc.get("stimulus"),
        "reference_arm": ref,
        "table": table,
        "populations": pop_table,
        "deviation_from_reference": by_dev,
        "downstream_deviation_from_reference": downstream,
        "own_metric_exclusions": {k: list(v) for k, v in OWN_METRIC.items()},
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
