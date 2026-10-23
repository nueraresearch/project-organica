"""
Final verdicts: every pre-registered prediction, forced into a bucket.

`docs/FORCE-MATRIX-PREREGISTRATION.md` §6 lists five falsification
predictions. This script takes the campaign artifact, the sensitivity audit
and the measured noise floor, and returns one verdict per prediction.

The buckets are the ones the campaign was designed to produce:

  SUPPORTED          the prediction held.
  UNSUPPORTED        the prediction did not hold. Recorded as falsified, not
                     quietly revised.
  REVERSED           the effect ran the OPPOSITE way to the prediction.
  NOT INTERPRETABLE  the campaign cannot answer this one, and says so.

`NOT INTERPRETABLE` is not a consolation category. A metric that is
saturated, structurally zero, or whose delta is below the measured noise
floor cannot support a claim, and a claim built on one is not a weak
finding -- it is not a finding. Those cases are named here rather than
absorbed into `UNSUPPORTED`, which would read as "we looked and it wasn't
there" when the truth is "we could not have seen it either way".

**The verdicts are direction-aware.** "The colony differs from the reference
arm" is not the same as "the prediction was supported". If removing
contradiction *raises* development velocity, then contradiction is not
developmental fuel -- it is developmental drag, and the prediction is
REVERSED, not supported. Each prediction therefore declares an
`expect` mode and the metric whose direction carries the claim.

Usage:
    python benchmarks/verdicts.py --matrix docs/force_matrix.json
Writes docs/verdicts.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.metric_sensitivity import metric_value  # noqa: E402

# The five predictions from the pre-registration's §6, with the colony each
# one is about and the metrics it is about.
#
# `expect` is the condition for SUPPORTED:
#   "differs"    -- the colony must move away from the reference arm.
#   "harm"       -- removing the mechanism must make development WORSE.
#   "orthogonal" -- the colony must agree with the reference arm.
#
# `effect_metric` is the metric whose direction carries the claim. It is
# the metric the directional verdict is read from; the rest are context.
PREDICTIONS = [
    {
        "id": "P1",
        "claim": "Retention policy affects development",
        "colony": "SALIENCE",
        "metrics": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"],
        "expect": "differs",
        "effect_metric": None,
        "falsified_if": "FULL and SALIENCE agree on every M1-M9 metric",
    },
    {
        "id": "P2",
        "claim": "Contradiction is developmental fuel",
        "colony": "NO_CONTRADICTIONS",
        "metrics": ["M1", "M5", "M6"],
        "expect": "harm",
        "effect_metric": "M5",
        "falsified_if": "NO_CONTRADICTIONS matches FULL on M1, M5, M6",
    },
    {
        "id": "P3",
        "claim": "Curiosity needs explicit questions",
        "colony": "NO_QUESTIONS",
        "metrics": ["M1", "M5"],
        "expect": "harm",
        "effect_metric": "M5",
        "falsified_if": "NO_QUESTIONS collapses M1 and M5",
        "collapse_rule": "M5 below 20% of the reference arm's value, or M1 at 0",
    },
    {
        "id": "P4",
        "claim": "Dreams contribute to trajectory",
        "colony": "NO_DREAMS",
        "metrics": ["M1", "M5", "M6"],
        "expect": "harm",
        "effect_metric": "M5",
        "falsified_if": "NO_DREAMS leaves M1/M5/M6 unchanged",
    },
    {
        "id": "P5",
        "claim": "EIG is orthogonal to development",
        "colony": "ANTI_EIG",
        "metrics": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"],
        "expect": "orthogonal",
        "effect_metric": "M5",
        "falsified_if": "ANTI_EIG matches FULL on M1-M9",
    },
]


def load(path: Path):
    if not path.exists():
        print("not present:", path)
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default=str(REPO / "docs" / "force_matrix.json"))
    ap.add_argument("--sensitivity",
                    default=str(REPO / "docs" / "metric_sensitivity.json"))
    ap.add_argument("--noise",
                    default=str(REPO / "docs" / "process_noise_3000.json"))
    ap.add_argument("--out", default=str(REPO / "docs" / "verdicts.json"))
    args = ap.parse_args()

    doc = load(Path(args.matrix))
    if doc is None:
        sys.exit(1)
    sens = load(Path(args.sensitivity)) or {}
    noise = load(Path(args.noise)) or {}

    rows = {r["colony"]: r for r in doc["rows"]}
    ref_name = "FULL" if "FULL" in rows else next(iter(rows))

    # The measured noise floor per metric, from the process-level sweep.
    # Every floor is READ from the measurement, including the zeros: "this
    # field was measured and did not vary" is not the same as "no floor was
    # established", and the difference is recorded.
    NOISE_FIELD = {
        "M1": "M1_theory_duty_cycle.whole_run",
        "M2": "M2_question_duty_cycle.whole_run",
        "M3": "M3_contradiction_density.mean",
        "M4": "M4_contradiction_survival.rate",
        "M5": "M5_development_velocity.new_per_100_cycles",
        "M6": "M6_lineage_depth.max_generation",
        "M7": "M7_mean_hypothesis_lifetime.mean",
        "M8": "M8_population_stability.beliefs",
        "M9": "M9_cognitive_revolutions.revolutions",
    }
    measured = {t.get("field"): t.get("spread", 0.0) or 0.0
                for t in noise.get("table", [])}
    floor = {}
    for key, field in NOISE_FIELD.items():
        if field in measured:
            floor[key] = measured[field]
        else:
            floor[key] = None      # not measured -> cannot judge
    measured_at = noise.get("cycles")
    measured_colony = noise.get("colony")

    sensitivity = {t["metric"]: t for t in sens.get("table", [])}

    def value(colony: str, metric: str):
        r = rows.get(colony)
        if r is None:
            return None
        try:
            return metric_value(r["metrics"], metric)
        except Exception:
            return None

    results = []
    for p in PREDICTIONS:
        colony = p["colony"]
        if colony not in rows:
            results.append({
                "id": p["id"], "claim": p["claim"],
                "verdict": "NOT INTERPRETABLE",
                "reason": f"colony {colony} is not in the artifact",
            })
            continue

        detail = []
        moved = []
        any_capable = False
        for metric in p["metrics"]:
            ref_v = value(ref_name, metric)
            col_v = value(colony, metric)
            if ref_v is None or col_v is None:
                detail.append({"metric": metric, "verdict": "not measurable"})
                continue
            delta = col_v - ref_v
            s = sensitivity.get(metric, {})
            can_move = s.get("verdict") == "SENSITIVE"
            fl = floor.get(metric)
            if fl is None:
                exceeds = False
                floor_state = "no noise floor measured"
            else:
                exceeds = abs(delta) > fl
                floor_state = fl
            if not can_move:
                verdict = "metric cannot move"
            elif fl is None:
                verdict = "no noise floor measured"
            elif not exceeds:
                verdict = "delta within the noise floor"
            else:
                verdict = "moved"
                moved.append(metric)
            any_capable = any_capable or can_move
            detail.append({
                "metric": metric,
                "reference_value": ref_v,
                "colony_value": col_v,
                "delta": round(delta, 6),
                "metric_can_move": can_move,
                "noise_floor": floor_state,
                "exceeds_noise": exceeds,
                "verdict": verdict,
            })

        effect = None
        if p["effect_metric"]:
            effect = next((d for d in detail
                           if d["metric"] == p["effect_metric"]), None)
        effect_moved = bool(effect and effect.get("verdict") == "moved")

        if not any_capable:
            verdict = "NOT INTERPRETABLE"
            reason = ("no metric in this prediction can move on this "
                      "substrate, so the prediction could not be tested")
        elif p["expect"] == "differs":
            if moved:
                verdict = "SUPPORTED"
                reason = (f"{len(moved)} of {len(p['metrics'])} metrics moved "
                          f"beyond the noise floor ({', '.join(moved)})")
            else:
                verdict = "UNSUPPORTED"
                reason = ("the colony agrees with the reference arm on every "
                          "metric that can move")
        elif p["expect"] == "harm":
            if effect_moved:
                if effect["delta"] < 0:
                    verdict = "SUPPORTED"
                    reason = (f"{p['effect_metric']} falls by "
                              f"{abs(effect['delta'])} when the mechanism is "
                              f"removed -- the predicted harm is present")
                else:
                    verdict = "REVERSED"
                    reason = (f"{p['effect_metric']} RISES by "
                              f"{effect['delta']} when the mechanism is "
                              f"removed -- the opposite of the prediction")
            elif moved:
                verdict = "UNSUPPORTED"
                reason = (f"other metrics moved ({', '.join(moved)}) but "
                          f"{p['effect_metric']}, the metric that carries the "
                          f"claim, did not move beyond the noise floor")
            else:
                verdict = "NOT INTERPRETABLE"
                reason = ("no metric in this prediction moved beyond the "
                          "measured noise floor")
        elif p["expect"] == "orthogonal":
            if not moved:
                verdict = "SUPPORTED"
                reason = ("the colony agrees with the reference arm on every "
                          "metric that can move")
            elif effect_moved and effect["delta"] > 0:
                verdict = "REVERSED"
                reason = (f"selecting the LOWEST-EIG experiment develops "
                          f"{effect['delta']} MORE per 100 cycles than "
                          f"selecting the highest-EIG one -- EIG selection is "
                          f"not orthogonal, it is counterproductive")
            else:
                verdict = "UNSUPPORTED"
                reason = (f"{len(moved)} of {len(p['metrics'])} metrics moved "
                          f"beyond the noise floor ({', '.join(moved)}), so "
                          f"the two selection rules are not equivalent")
        else:
            verdict = "NOT INTERPRETABLE"
            reason = f"unknown expectation mode {p['expect']!r}"

        results.append({
            "id": p["id"],
            "claim": p["claim"],
            "colony": colony,
            "expect": p["expect"],
            "effect_metric": p["effect_metric"],
            "falsified_if": p["falsified_if"],
            "verdict": verdict,
            "reason": reason,
            "metrics_moved": moved,
            "detail": detail,
        })

    buckets = {"SUPPORTED": [], "UNSUPPORTED": [], "REVERSED": [],
               "NOT INTERPRETABLE": []}
    for r in results:
        buckets.setdefault(r["verdict"], []).append(r["id"])

    print("=" * 96)
    print(f"PRE-REGISTERED PREDICTIONS -- {doc.get('cycles')} cycles/colony, "
          f"reference arm {ref_name}")
    print("=" * 96)
    for r in results:
        print(f"  [{r['id']}] {r['verdict']:<18} {r['claim']}")
        print(f"       colony      : {r.get('colony')}")
        print(f"       falsified if: {r.get('falsified_if')}")
        print(f"       reason      : {r.get('reason')}")
        for d in r.get("detail", []):
            if d.get("verdict") == "moved":
                print(f"         {d['metric']}: {d['reference_value']} -> "
                      f"{d['colony_value']} (delta {d['delta']}, floor "
                      f"{d['noise_floor']})")
            else:
                print(f"         {d['metric']}: {d['verdict']}")
        print()

    print("SUMMARY")
    print("-" * 96)
    for k in ("SUPPORTED", "UNSUPPORTED", "REVERSED", "NOT INTERPRETABLE"):
        ids = buckets.get(k, [])
        print(f"  {k:<18} {len(ids):>2}  {', '.join(ids) if ids else '-'}")

    Path(args.out).write_text(json.dumps({
        "matrix_artifact": args.matrix,
        "cycles": doc.get("cycles"),
        "stimulus": doc.get("stimulus"),
        "reference_arm": ref_name,
        "noise_floor": floor,
        "noise_measured_at": {
            "cycles": measured_at,
            "colony": measured_colony,
            "note": ("the floor is measured at the scale of the run it judges. "
                     "M5 is a rate, so its floor scales with run length; the "
                     "scale-invariant form is the item count."),
        },
        "results": results,
        "buckets": buckets,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
