"""Phase H multi-seed evaluation campaign.

Runs the frozen held-out prediction task and known-cause recovery task across
the preregistered seed set. Hash iteration is held common with
PYTHONHASHSEED=0. The prediction curriculum is deterministic and identical
across seeds, so only Organica's seeded sleep RNG varies there; recovery-world
samples and Organica's RNG both vary across seeds. Intervals summarize only
these sources of variation.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.ground_truth_recovery import run as run_recovery  # noqa: E402
from benchmarks.heldout_prediction import run as run_prediction  # noqa: E402

DEFAULT_SEEDS = list(range(20261023, 20261033))
BOOTSTRAP_REPLICATES = 10_000
METRICS = ("precision", "recall", "f1", "brier", "log_loss")
RECOVERY_METRICS = ("precision", "recall", "f1")
SCENARIOS = {
    "clean": {"noise_rate": 0.10, "overlap_features": 0,
              "false_correlation_rate": 0.0},
    "overlapping": {"noise_rate": 0.20, "overlap_features": 2,
                    "false_correlation_rate": 0.10},
    "stress": {"noise_rate": 0.30, "overlap_features": 3,
               "false_correlation_rate": 0.25},
}


def _quantile(sorted_values: list[float], q: float) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return sorted_values[lo]
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def summarize(values: list[float], *, bootstrap_seed: int) -> dict:
    """Mean, sample SD, range and deterministic percentile bootstrap CI."""
    if not values:
        return {"n": 0, "mean": None, "sd": None, "min": None,
                "max": None, "bootstrap_95_ci": [None, None]}
    rng = random.Random(bootstrap_seed)
    n = len(values)
    boot_means = sorted(
        sum(values[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(BOOTSTRAP_REPLICATES)
    )
    return {
        "n": n,
        "mean": round(statistics.mean(values), 6),
        "sd": round(statistics.stdev(values), 6) if n > 1 else 0.0,
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "bootstrap_95_ci": [round(_quantile(boot_means, .025), 6),
                             round(_quantile(boot_means, .975), 6)],
    }


def _aggregate(records: list[dict], models: list[str], metrics: tuple[str, ...],
               *, section_key: str) -> tuple[dict, dict]:
    by_seed = {r["seed"]: r[section_key] for r in records}
    model_summaries = {}
    paired = {}
    for model_index, model in enumerate(models):
        model_summaries[model] = {}
        for metric_index, metric in enumerate(metrics):
            vals = [by_seed[s][model][metric] for s in sorted(by_seed)]
            model_summaries[model][metric] = summarize(
                vals, bootstrap_seed=91000 + 100 * model_index + metric_index)
    if "organica_g1_predictions" in models:
        reference = "organica_g1_predictions"
    else:
        reference = "organica_surviving_structures"
    for model_index, model in enumerate(models):
        if model == reference:
            continue
        paired[model] = {}
        for metric_index, metric in enumerate(metrics):
            diffs = [by_seed[s][model][metric] - by_seed[s][reference][metric]
                     for s in sorted(by_seed)]
            paired[model][metric] = summarize(
                diffs, bootstrap_seed=73000 + 100 * model_index + metric_index)
    return model_summaries, {
        "reference_model": reference,
        "delta_convention": "comparison model minus reference; positive favors comparison model",
        "comparison_minus_reference": paired,
    }


def difficulty_trends(recovery_records: dict[str, list[dict]]) -> dict:
    """Paired change in Organica's F1 advantage from clean to harder worlds."""
    by_condition = {
        condition: {record["seed"]: record["results"] for record in records}
        for condition, records in recovery_records.items()
    }
    org = "organica_surviving_structures"
    trends = {}
    for condition_index, harder in enumerate(("overlapping", "stress")):
        trends[harder] = {}
        shared_seeds = sorted(set(by_condition["clean"]) & set(by_condition[harder]))
        models = [m for m in by_condition["clean"][shared_seeds[0]] if m != org]
        for model_index, model in enumerate(models):
            values = [
                (by_condition[harder][seed][org]["f1"]
                 - by_condition[harder][seed][model]["f1"])
                - (by_condition["clean"][seed][org]["f1"]
                   - by_condition["clean"][seed][model]["f1"])
                for seed in shared_seeds
            ]
            trends[harder][model] = summarize(
                values, bootstrap_seed=85000 + 100 * condition_index + model_index)
    return {
        "quantity": "(Organica F1 - baseline F1) in harder condition minus the same gap in clean condition",
        "positive_means": "Organica's relative F1 position improved as the condition became harder",
        "interval_rule": "95% percentile bootstrap interval wholly above/below zero indicates a relative improvement/worsening; otherwise inconclusive",
        "paired_changes": trends,
    }


def _run_seed_block(seed: int) -> tuple[dict, dict]:
    prediction = run_prediction(seed)
    prediction_record = {
        "seed": seed,
        "known_tags": {
            row["model"]: {m: row[m] for m in METRICS}
            for row in prediction["results_known_training_tags"]
        },
        "including_test_only_tags": {
            row["model"]: {m: row[m] for m in METRICS}
            for row in prediction["results_including_test_only_tags"]
        },
    }
    recovery_records = {}
    for name, config in SCENARIOS.items():
        result = run_recovery(seed, **config)
        recovery_records[name] = {
            "seed": seed,
            "results": {
                row["model"]: {m: row[m] for m in RECOVERY_METRICS}
                for row in result["results"]
            },
        }
    return prediction_record, recovery_records


def run_campaign(seeds: list[int], workers: int = 3) -> dict:
    if len(seeds) < 2:
        raise ValueError("At least two seeds are required for uncertainty summaries")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seed list must not contain duplicates")
    if workers < 1:
        raise ValueError("workers must be positive")
    prediction_records = []
    recovery_records = {name: [] for name in SCENARIOS}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for prediction_record, recovery_by_scenario in pool.map(_run_seed_block, seeds):
            prediction_records.append(prediction_record)
            for name, record in recovery_by_scenario.items():
                recovery_records[name].append(record)

    pred_models = list(prediction_records[0]["known_tags"])
    prediction_summary = {}
    prediction_deltas = {}
    for section in ("known_tags", "including_test_only_tags"):
        models, deltas = _aggregate(
            prediction_records, pred_models, METRICS, section_key=section)
        prediction_summary[section] = models
        prediction_deltas[section] = deltas

    structure_summary = {}
    structure_deltas = {}
    for name, records in recovery_records.items():
        models, deltas = _aggregate(
            records, list(records[0]["results"]), RECOVERY_METRICS,
            section_key="results")
        structure_summary[name] = models
        structure_deltas[name] = deltas

    return {
        "protocol": {
            "preregistration": "docs/PHASE-H-PREREGISTRATION.md",
            "seeds": seeds,
            "seed_count": len(seeds),
            "workers": workers,
            "python_hash_seed": os.environ.get("PYTHONHASHSEED"),
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "confidence_interval": "95% percentile bootstrap over per-seed scores; synthetic-seed uncertainty only",
            "prediction_protocol": "heldout_prediction.py defaults: train cycles 1-200, freeze, test 201-300; fixed F1 threshold 0.5",
            "recovery_protocol": "ground_truth_recovery.py defaults: train cycles 1-200; hidden labels withheld from models",
            "recovery_scenarios": SCENARIOS,
        },
        "prediction": {
            "per_seed": prediction_records,
            "summary": prediction_summary,
            "paired_differences": prediction_deltas,
        },
        "structure_recovery": {
            "per_seed": recovery_records,
            "summary": structure_summary,
            "paired_differences": structure_deltas,
            "difficulty_trends": difficulty_trends(recovery_records),
        },
        "limitations": [
            "The prediction curriculum is deterministic and identical across seeds; its intervals reflect Organica's seeded sleep RNG only, while baseline scores repeat on the same stream.",
            "Recovery seeds vary synthetic samples and Organica's seeded sleep RNG; neither task samples real-world environments.",
            "PYTHONHASHSEED is fixed at 0 to control process-level enumeration variation, not estimated as another uncertainty source.",
            "F1 uses the preregistered fixed 0.5 threshold; no threshold is tuned on test data.",
            "Organica G1 strengths are not calibrated probabilities; its Brier and log-loss comparisons are descriptive.",
            "Structure recovery is undirected pairwise same-cause recovery, not intervention-based causal discovery or held-out regime prediction.",
            "The overlap and false-correlation levels are controlled synthetic stress conditions, not a representative distribution of natural worlds.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=10,
                        help="number of consecutive preregistered seeds (default: 10)")
    parser.add_argument("--first-seed", type=int, default=20261023)
    parser.add_argument("--workers", type=int, default=3,
                        help="parallel independent seed blocks (default: 3)")
    parser.add_argument("--out", default=str(REPO / "docs" / "phase_h_results.json"))
    parser.add_argument("--summarize-existing", action="store_true",
                        help="add preregistered difficulty-trend intervals to an existing result file")
    args = parser.parse_args()
    output = Path(args.out)
    if args.summarize_existing:
        result = json.loads(output.read_text(encoding="utf-8"))
        result["structure_recovery"]["difficulty_trends"] = difficulty_trends(
            result["structure_recovery"]["per_seed"])
        result["limitations"] = [
            item for item in result.get("limitations", [])
            if not item.startswith("The ten seeds vary synthetic samples")
        ] + [
            "The prediction curriculum is deterministic and identical across seeds; its intervals reflect Organica's seeded sleep RNG only, while baseline scores repeat on the same stream.",
            "Recovery seeds vary synthetic samples and Organica's seeded sleep RNG; neither task samples real-world environments.",
        ]
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result["structure_recovery"]["difficulty_trends"], indent=2))
        print(f"updated {output}")
        return
    if os.environ.get("PYTHONHASHSEED") != "0":
        parser.error("launch with PYTHONHASHSEED=0 to hold process hash order fixed")
    seeds = list(range(args.first_seed, args.first_seed + args.seeds))
    result = run_campaign(seeds, workers=args.workers)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["protocol"], indent=2))
    print(json.dumps({
        "prediction": result["prediction"]["summary"],
        "prediction_deltas": result["prediction"]["paired_differences"],
        "structure_recovery": result["structure_recovery"]["summary"],
        "structure_deltas": result["structure_recovery"]["paired_differences"],
    }, indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
