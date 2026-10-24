"""Phase I: preregistered online regime-shift detection campaign.

Models predict the next tag in a shared stream. A per-world surprise threshold
is set from the pre-shift period; alarm rules and all outcome summaries follow
docs/REGIME-SHIFT-PREREGISTRATION.md. The live study is never opened.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService  # noqa: E402
from organica.paths import temp_db  # noqa: E402
from organica.sleep import SleepService  # noqa: E402

FAMILIES = ("cause_mix", "mapping_swap")
MODELS = ("organica", "first_order_markov", "decayed_association")
FIRST_SEED = 20261201
SEEDS = tuple(range(FIRST_SEED, FIRST_SEED + 20))
CYCLES = 90
SHIFT_CYCLE = 60
TRIALS_PER_CYCLE = 8
CALIBRATION_START = 20
CALIBRATION_END = 60
WINDOW = 5
Z_THRESHOLD = 3.0
DETECTION_HORIZON = 30
MAX_DELAY = DETECTION_HORIZON + 1
ALPHA = 0.5
DECAY_HALF_LIFE = 20
EPSILON = 1e-9
BOOTSTRAP_REPLICATES = 10_000

CAUSE_OUTCOMES = {
    "causea": ("amber", "birch", "cedar", "maple"),
    "causeb": ("indigo", "fern", "willow", "yarrow"),
}
MAPPING_CONTEXTS = ("ctxa", "ctxb", "ctxc", "ctxd")
MAPPING_OUTCOMES = ("amber", "birch", "cedar", "maple")
MAPPING_BEFORE = dict(zip(MAPPING_CONTEXTS, MAPPING_OUTCOMES))
MAPPING_AFTER = dict(zip(MAPPING_CONTEXTS,
                         ("birch", "amber", "maple", "cedar")))


def generate_world(family: str, seed: int, *, shifted: bool) -> dict:
    """Return cycles of ordered (context, outcome) event pairs and gold regimes."""
    if family not in FAMILIES:
        raise ValueError(f"unknown generator family: {family}")
    rng = random.Random(seed)
    cycles = []
    regimes = []
    for cycle in range(CYCLES):
        regime = int(shifted and cycle >= SHIFT_CYCLE)
        regimes.append(regime)
        trials = []
        for _ in range(TRIALS_PER_CYCLE):
            if family == "cause_mix":
                p_cause_a = (0.85 if regime == 0 else 0.15)
                cause = "causea" if rng.random() < p_cause_a else "causeb"
                outcome_pool = tuple(tag for tags in CAUSE_OUTCOMES.values()
                                     for tag in tags)
                outcome = (rng.choice(outcome_pool) if rng.random() < 0.10
                           else rng.choice(CAUSE_OUTCOMES[cause]))
                context = cause
            else:
                context = rng.choice(MAPPING_CONTEXTS)
                mapping = MAPPING_AFTER if regime else MAPPING_BEFORE
                outcome = (rng.choice(MAPPING_OUTCOMES)
                           if rng.random() < 0.10 else mapping[context])
            trials.append((context, outcome))
        cycles.append(trials)
    tags = (tuple(CAUSE_OUTCOMES) +
            tuple(tag for group in CAUSE_OUTCOMES.values() for tag in group)
            if family == "cause_mix" else
            MAPPING_CONTEXTS + MAPPING_OUTCOMES)
    return {"cycles": cycles, "regimes": regimes, "tags": tags,
            "family": family, "seed": seed, "shifted": shifted}


def _distribution(weights: dict[str, float], vocabulary: tuple[str, ...]) -> dict[str, float]:
    values = {tag: max(0.0, float(weights.get(tag, 0.0))) for tag in vocabulary}
    total = sum(values.values())
    if total <= 0:
        return {tag: 1.0 / len(vocabulary) for tag in vocabulary}
    floored = {tag: max(EPSILON, value / total) for tag, value in values.items()}
    norm = sum(floored.values())
    return {tag: value / norm for tag, value in floored.items()}


def _baseline_distributions(history: list[str], history_cycles: list[int],
                            current_cycle: int, vocabulary: tuple[str, ...]) -> tuple[dict, dict]:
    markov = defaultdict(lambda: defaultdict(float))
    decayed = defaultdict(lambda: defaultdict(float))
    for i, (source, target) in enumerate(zip(history, history[1:])):
        markov[source][target] += 1.0
        age = max(0, current_cycle - history_cycles[i])
        weight = 0.5 ** (age / DECAY_HALF_LIFE)
        decayed[source][target] += weight

    def rows(counts: dict) -> dict:
        result = {}
        for source, targets in counts.items():
            result[source] = _distribution(
                {tag: targets.get(tag, 0.0) + ALPHA for tag in vocabulary},
                vocabulary)
        return result

    return rows(markov), rows(decayed)


def _organica_distributions(report, vocabulary: tuple[str, ...]) -> dict:
    weights = defaultdict(dict)
    if report:
        for prediction in report.predictions:
            weights[prediction.source][prediction.target] = prediction.strength
    return {source: _distribution(targets, vocabulary)
            for source, targets in weights.items()}


def _cycle_loss(events: list[str], previous: str | None,
                distributions: dict, vocabulary: tuple[str, ...]) -> float:
    sequence = ([previous] if previous is not None else []) + events
    losses = []
    for source, target in zip(sequence, sequence[1:]):
        probs = distributions.get(source)
        if probs is None:
            probs = {tag: 1.0 / len(vocabulary) for tag in vocabulary}
        losses.append(-math.log(max(EPSILON, probs.get(target, 0.0))))
    return statistics.mean(losses) if losses else 0.0


def run_world(family: str, seed: int, *, shifted: bool) -> dict:
    world = generate_world(family, seed, shifted=shifted)
    db = temp_db("phase_i_regime_shift.db")
    db.unlink(missing_ok=True)
    mem = MemoryService(db_path=str(db))
    svc = SleepService(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    history: list[str] = []
    history_cycles: list[int] = []
    losses = {name: [] for name in MODELS}
    internal = []
    report = None
    try:
        for cycle, trials in enumerate(world["cycles"]):
            events = [tag for pair in trials for tag in pair]
            previous = history[-1] if history else None
            markov_rows, decayed_rows = _baseline_distributions(
                history, history_cycles, cycle, world["tags"])
            organica_rows = _organica_distributions(report, world["tags"])
            losses["organica"].append(_cycle_loss(
                events, previous, organica_rows, world["tags"]))
            losses["first_order_markov"].append(_cycle_loss(
                events, previous, markov_rows, world["tags"]))
            losses["decayed_association"].append(_cycle_loss(
                events, previous, decayed_rows, world["tags"]))

            for event in events:
                mem.store(event, event_type="event", source=f"phase_i:{cycle}")
            report = svc.run_sleep_cycle()
            history.extend(events)
            history_cycles.extend([cycle] * len(events))
            internal.append({
                "cycle": cycle,
                "hypotheses": len(report.hypotheses) if report else 0,
                "theories": len(report.theories) if report else 0,
                "questions": len(report.questions) if report else 0,
                "anomalies": len(report.anomalies) if report else 0,
            })
    finally:
        mem.close()
        db.unlink(missing_ok=True)

    alarms = {}
    for model, series in losses.items():
        blocks = [statistics.mean(series[i:i + WINDOW])
                  for i in range(CALIBRATION_START, CALIBRATION_END, WINDOW)]
        baseline = statistics.mean(blocks)
        spread = statistics.stdev(blocks) if len(blocks) > 1 else 0.0
        threshold = baseline + Z_THRESHOLD * max(spread, 1e-6)
        consecutive = 0
        alarm_cycle = None
        for cycle in range(SHIFT_CYCLE, CYCLES):
            if cycle < WINDOW - 1:
                continue
            observed = statistics.mean(series[cycle - WINDOW + 1:cycle + 1])
            consecutive = consecutive + 1 if observed > threshold else 0
            if consecutive >= 2:
                alarm_cycle = cycle
                break
        if shifted and alarm_cycle is not None and alarm_cycle - SHIFT_CYCLE <= DETECTION_HORIZON:
            delay = alarm_cycle - SHIFT_CYCLE
        else:
            delay = MAX_DELAY
        alarms[model] = {
            "alarm_cycle": alarm_cycle,
            "threshold": round(threshold, 8),
            "calibration_mean": round(baseline, 8),
            "calibration_sd": round(spread, 8),
            "restricted_delay": delay if shifted else None,
            "false_alarm": bool(not shifted and alarm_cycle is not None),
            "detected_within_horizon": bool(shifted and delay <= DETECTION_HORIZON),
        }
    return {"family": family, "seed": seed, "shifted": shifted,
            "models": alarms, "internal_cycle_counts": internal}


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return ordered[lo] if lo == hi else ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def _paired_interval(values: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    n = len(values)
    means = sorted(statistics.mean(values[rng.randrange(n)] for _ in range(n))
                   for _ in range(BOOTSTRAP_REPLICATES))
    # Two-sided 97.5% interval: Bonferroni-adjusted across the two families.
    return [round(_quantile(means, 0.0125), 6),
            round(_quantile(means, 0.9875), 6)]


def summarize(records: list[dict]) -> dict:
    result = {}
    for family in FAMILIES:
        shifted = sorted((r for r in records if r["family"] == family and r["shifted"]),
                         key=lambda r: r["seed"])
        controls = [r for r in records if r["family"] == family and not r["shifted"]]
        family_result = {"models": {}, "paired_baseline_minus_organica": {},
                         "stationary_control_false_alarm_rate": {}}
        for model_index, model in enumerate(MODELS):
            delays = [r["models"][model]["restricted_delay"] for r in shifted]
            family_result["models"][model] = {
                "n": len(delays),
                "restricted_mean_delay": round(statistics.mean(delays), 6),
                "restricted_delay_sd": round(statistics.stdev(delays), 6),
                "detection_fraction_within_30_cycles": round(
                    sum(d <= DETECTION_HORIZON for d in delays) / len(delays), 6),
            }
            alarmed = sum(r["models"][model]["false_alarm"] for r in controls)
            family_result["stationary_control_false_alarm_rate"][model] = {
                "n": len(controls), "false_alarms": alarmed,
                "rate": round(alarmed / len(controls), 6),
            }
            if model == "organica":
                continue
            diffs = [r["models"][model]["restricted_delay"]
                     - r["models"]["organica"]["restricted_delay"]
                     for r in shifted]
            family_result["paired_baseline_minus_organica"][model] = {
                "n": len(diffs), "mean_advantage_cycles": round(statistics.mean(diffs), 6),
                "bootstrap_97_5_ci": _paired_interval(diffs, 20261023 + model_index),
                "positive_favors_organica": True,
            }
        fpr_ok = all(v["rate"] <= 0.10
                     for v in family_result["stationary_control_false_alarm_rate"].values())
        comparisons_ok = all(
            v["mean_advantage_cycles"] >= 2.0 and v["bootstrap_97_5_ci"][0] > 0
            for v in family_result["paired_baseline_minus_organica"].values())
        family_result["primary_rule_met"] = bool(fpr_ok and comparisons_ok)
        family_result["fpr_gate_passed"] = fpr_ok
        result[family] = family_result
    return result


def _run_seed(seed: int) -> list[dict]:
    records = []
    for family in FAMILIES:
        records.append(run_world(family, seed, shifted=True))
        records.append(run_world(family, seed, shifted=False))
    return records


def run_campaign(workers: int = 3) -> dict:
    records = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for seed_records in pool.map(_run_seed, SEEDS):
            records.extend(seed_records)
    return {
        "protocol": {
            "preregistration": "docs/REGIME-SHIFT-PREREGISTRATION.md",
            "seed_range": [SEEDS[0], SEEDS[-1]], "seed_count": len(SEEDS),
            "cycles": CYCLES, "shift_cycle": SHIFT_CYCLE,
            "trials_per_cycle": TRIALS_PER_CYCLE,
            "workers": workers, "python_hash_seed": os.environ.get("PYTHONHASHSEED"),
            "models": list(MODELS), "families": list(FAMILIES),
            "alarm": {"calibration_cycles": [CALIBRATION_START, CALIBRATION_END - 1],
                      "window_cycles": WINDOW, "z_threshold": Z_THRESHOLD,
                      "consecutive_windows": 2, "horizon_cycles": DETECTION_HORIZON},
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "bootstrap_interval": "97.5% paired percentile; Bonferroni-adjusted across two generator families",
        },
        "summary": summarize(records),
        "per_world": records,
        "limitations": [
            "Results generalize only to the two specified synthetic generator families.",
            "The detector is based on predictive surprise; the benchmark does not isolate a causal contribution from contradiction or belief-revision machinery.",
            "The per-world threshold uses eight stable-period five-cycle blocks; false-alarm rates are reported empirically and may be imprecise with 20 controls.",
            "This benchmark does not establish performance in natural or operational environments.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--out", default=str(REPO / "docs" / "regime_shift_results.json"))
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    if os.environ.get("PYTHONHASHSEED") != "0":
        parser.error("launch with PYTHONHASHSEED=0 as required by the preregistration")
    result = run_campaign(args.workers)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["protocol"], indent=2))
    print(json.dumps(result["summary"], indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
