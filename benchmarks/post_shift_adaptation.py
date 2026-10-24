"""Phase J gradual post-shift adaptation campaign.

Compares Organica, first-order Markov, and recency-decayed transition models
on paired gradual-change and stationary worlds. The protocol is frozen in
docs/PHASE-J-ADAPTATION-PREREGISTRATION.md. The live database is never opened.
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

FAMILIES = ("cause_mix", "mapping_mix")
MODELS = ("organica", "first_order_markov", "decayed_association")
SEEDS = tuple(range(20270101, 20270121))
CYCLES = 80
RAMP_START = 30
RAMP_CYCLES = 20
FINAL_START = RAMP_START + RAMP_CYCLES
TRIALS_PER_CYCLE = 8
ALPHA = 0.5
DECAY_HALF_LIFE = 20
EPSILON = 1e-9
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20270123
MIN_ADAPTATION_ADVANTAGE = 0.05
FINAL_NONINFERIORITY_MARGIN = 0.05
SETTLING_MARGIN = 0.05
WINDOW = 5

CAUSE_OUTCOMES = {
    "causea": ("amber", "birch", "cedar", "maple"),
    "causeb": ("indigo", "fern", "willow", "yarrow"),
}
CAUSE_TAGS = tuple(tag for group in CAUSE_OUTCOMES.values() for tag in group)
MAPPING_CONTEXTS = ("ctxa", "ctxb", "ctxc", "ctxd")
MAPPING_OUTCOMES = ("amber", "birch", "cedar", "maple")
MAPPING_BEFORE = dict(zip(MAPPING_CONTEXTS, MAPPING_OUTCOMES))
MAPPING_AFTER = dict(zip(MAPPING_CONTEXTS,
                         ("birch", "amber", "maple", "cedar")))


def _choice(unit: float, items: tuple[str, ...]) -> str:
    return items[min(len(items) - 1, int(unit * len(items)))]


def transition_fraction(cycle: int, *, shifted: bool) -> float:
    """Fraction of the final rule; controls remain at zero throughout."""
    if not shifted or cycle < RAMP_START:
        return 0.0
    if cycle >= RAMP_START + RAMP_CYCLES:
        return 1.0
    return (cycle - RAMP_START + 1) / RAMP_CYCLES


def generate_world(family: str, seed: int, *, shifted: bool) -> dict:
    """Generate an 80-cycle stream, pairing shifted/control draws by seed."""
    if family not in FAMILIES:
        raise ValueError(f"unknown generator family: {family}")
    rng = random.Random(seed)
    cycles = []
    fractions = []
    tags = (("causea", "causeb") + CAUSE_TAGS
            if family == "cause_mix" else MAPPING_CONTEXTS + MAPPING_OUTCOMES)
    for cycle in range(CYCLES):
        fraction = transition_fraction(cycle, shifted=shifted)
        fractions.append(fraction)
        trials = []
        for _ in range(TRIALS_PER_CYCLE):
            u_context, u_rule, u_noise, u_outcome = (rng.random() for _ in range(4))
            if family == "cause_mix":
                p_causea = 0.85 - 0.70 * fraction
                context = "causea" if u_context < p_causea else "causeb"
                pool = CAUSE_TAGS if u_noise < 0.10 else CAUSE_OUTCOMES[context]
                outcome = _choice(u_outcome, pool)
            else:
                context = _choice(u_context, MAPPING_CONTEXTS)
                mapping = MAPPING_AFTER if u_rule < fraction else MAPPING_BEFORE
                outcome = (_choice(u_outcome, MAPPING_OUTCOMES)
                           if u_noise < 0.10 else mapping[context])
            trials.append((context, outcome))
        cycles.append(trials)
    return {"family": family, "seed": seed, "shifted": shifted,
            "cycles": cycles, "transition_fraction": fractions, "tags": tags}


def _distribution(weights: dict[str, float], vocabulary: tuple[str, ...]) -> dict[str, float]:
    values = {tag: max(0.0, float(weights.get(tag, 0.0))) for tag in vocabulary}
    total = sum(values.values())
    if total <= 0:
        return {tag: 1.0 / len(vocabulary) for tag in vocabulary}
    floored = {tag: max(EPSILON, value / total) for tag, value in values.items()}
    norm = sum(floored.values())
    return {tag: value / norm for tag, value in floored.items()}


def _baseline_distributions(history: list[str], history_cycles: list[int],
                            current_cycle: int,
                            vocabulary: tuple[str, ...]) -> tuple[dict, dict]:
    markov = defaultdict(lambda: defaultdict(float))
    decayed = defaultdict(lambda: defaultdict(float))
    for index, (source, target) in enumerate(zip(history, history[1:])):
        markov[source][target] += 1.0
        age = max(0, current_cycle - history_cycles[index])
        decayed[source][target] += 0.5 ** (age / DECAY_HALF_LIFE)

    def rows(counts: dict) -> dict:
        return {
            source: _distribution(
                {tag: targets.get(tag, 0.0) + ALPHA for tag in vocabulary},
                vocabulary)
            for source, targets in counts.items()
        }

    return rows(markov), rows(decayed)


def _organica_distributions(report, vocabulary: tuple[str, ...]) -> dict:
    weights = defaultdict(dict)
    if report:
        for prediction in report.predictions:
            weights[prediction.source][prediction.target] = prediction.strength
    return {source: _distribution(targets, vocabulary)
            for source, targets in weights.items()}


def _cycle_loss(events: list[str], previous: str | None, distributions: dict,
                vocabulary: tuple[str, ...]) -> float:
    sequence = ([previous] if previous is not None else []) + events
    losses = []
    for source, target in zip(sequence, sequence[1:]):
        row = distributions.get(source)
        probability = row.get(target, 0.0) if row else 1.0 / len(vocabulary)
        losses.append(-math.log(max(EPSILON, probability)))
    return statistics.mean(losses) if losses else 0.0


def run_world(family: str, seed: int, *, shifted: bool) -> dict:
    world = generate_world(family, seed, shifted=shifted)
    db = temp_db(f"phase_j_{family}_{seed}_{int(shifted)}.db")
    mem = MemoryService(db_path=db)
    service = SleepService(mem)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)

    history: list[str] = []
    history_cycles: list[int] = []
    previous = None
    report = None
    losses = {model: [] for model in MODELS}
    internal = []
    try:
        for cycle, trials in enumerate(world["cycles"]):
            events = [tag for pair in trials for tag in pair]
            markov_rows, decayed_rows = _baseline_distributions(
                history, history_cycles, cycle, world["tags"])
            distributions = {
                "organica": _organica_distributions(report, world["tags"]),
                "first_order_markov": markov_rows,
                "decayed_association": decayed_rows,
            }
            for model in MODELS:
                losses[model].append(_cycle_loss(
                    events, previous, distributions[model], world["tags"]))

            for event in events:
                mem.store(event, event_type="event", source=f"phase_j:{cycle}")
            report = service.run_sleep_cycle()
            previous = events[-1] if events else previous
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
        db.parent.rmdir()

    return {
        "family": family, "seed": seed, "shifted": shifted,
        "transition_fraction": world["transition_fraction"],
        "cycle_nll": {name: [round(value, 8) for value in series]
                      for name, series in losses.items()},
        "internal_cycle_counts": internal,
    }


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _bootstrap_interval(values: list[float]) -> list[float]:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(values)
    means = sorted(_mean([values[rng.randrange(n)] for _ in range(n)])
                   for _ in range(BOOTSTRAP_REPLICATES))

    def quantile(q: float) -> float:
        position = (len(means) - 1) * q
        lo, hi = math.floor(position), math.ceil(position)
        if lo == hi:
            return means[lo]
        return means[lo] + (means[hi] - means[lo]) * (position - lo)

    return [round(quantile(0.0125), 6), round(quantile(0.9875), 6)]


def _interval_summary(values: list[float]) -> dict:
    return {"n": len(values), "mean": round(_mean(values), 6),
            "bootstrap_97_5_ci": _bootstrap_interval(values)}


def _window_means(series: list[float], start: int, stop: int) -> list[tuple[int, float]]:
    return [(index + WINDOW - 1, _mean(series[index:index + WINDOW]))
            for index in range(start, stop - WINDOW + 1, WINDOW)]


def settling_time(series: list[float]) -> int:
    """Cycles from ramp start to three qualifying windows; 51 if not settled."""
    final_mean = _mean(series[70:80])
    windows = _window_means(series, RAMP_START, CYCLES)
    for index in range(len(windows) - 2):
        if all(value <= final_mean + SETTLING_MARGIN
               for _, value in windows[index:index + 3]):
            return windows[index + 2][0] - RAMP_START
    return 51


def summarize(records: list[dict]) -> dict:
    result = {}
    for family in FAMILIES:
        shifted = {r["seed"]: r for r in records
                   if r["family"] == family and r["shifted"]}
        controls = {r["seed"]: r for r in records
                    if r["family"] == family and not r["shifted"]}
        by_model, costs, final_losses = {}, {}, {}
        for model in MODELS:
            shifted_mean = {
                seed: _mean(record["cycle_nll"][model][RAMP_START:CYCLES])
                for seed, record in shifted.items()}
            control_mean = {
                seed: _mean(record["cycle_nll"][model][RAMP_START:CYCLES])
                for seed, record in controls.items()}
            costs[model] = {
                seed: shifted_mean[seed] - control_mean[seed]
                for seed in sorted(shifted)}
            final_losses[model] = {
                seed: _mean(shifted[seed]["cycle_nll"][model][60:80])
                for seed in sorted(shifted)}
            by_model[model] = {
                "shifted_mean_nll_cycles_30_79": _interval_summary(
                    list(shifted_mean.values())),
                "stationary_control_mean_nll_cycles_30_79": _interval_summary(
                    list(control_mean.values())),
                "adaptation_cost": _interval_summary(list(costs[model].values())),
                "final_stable_nll_cycles_60_79": _interval_summary(
                    list(final_losses[model].values())),
                "settling_cycles_from_ramp_start": _interval_summary([
                    settling_time(shifted[seed]["cycle_nll"][model])
                    for seed in sorted(shifted)]),
            }

        adaptation_advantage, final_comparisons = {}, {}
        for baseline in MODELS[1:]:
            adaptation_diffs = [
                costs[baseline][seed] - costs["organica"][seed]
                for seed in sorted(shifted)]
            final_diffs = [
                final_losses["organica"][seed] - final_losses[baseline][seed]
                for seed in sorted(shifted)]
            adaptation_advantage[baseline] = _interval_summary(adaptation_diffs)
            final_comparisons[baseline] = _interval_summary(final_diffs)

        advantage_ok = all(
            item["mean"] >= MIN_ADAPTATION_ADVANTAGE
            and item["bootstrap_97_5_ci"][0] > 0
            for item in adaptation_advantage.values())
        final_noninferior = all(
            item["bootstrap_97_5_ci"][1] <= FINAL_NONINFERIORITY_MARGIN
            for item in final_comparisons.values())
        result[family] = {
            "n_paired_seeds": len(shifted), "models": by_model,
            "baseline_minus_organica_adaptation_cost": adaptation_advantage,
            "organica_minus_baseline_final_stable_nll": final_comparisons,
            "adaptation_advantage_gate_passed": advantage_ok,
            "final_stable_noninferiority_gate_passed": final_noninferior,
            "primary_rule_met": bool(advantage_ok and final_noninferior),
        }
    return result


def _run_seed(seed: int) -> list[dict]:
    return [run_world(family, seed, shifted=shifted)
            for family in FAMILIES for shifted in (True, False)]


def run_campaign(workers: int = 3) -> dict:
    records = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for seed_records in pool.map(_run_seed, SEEDS):
            records.extend(seed_records)
    return {
        "protocol": {
            "preregistration": "docs/PHASE-J-ADAPTATION-PREREGISTRATION.md",
            "seed_range": [SEEDS[0], SEEDS[-1]], "seed_count": len(SEEDS),
            "paired_worlds": len(SEEDS) * len(FAMILIES) * 2,
            "cycles": CYCLES, "ramp_start": RAMP_START,
            "ramp_cycles": RAMP_CYCLES, "final_stable_start": FINAL_START,
            "trials_per_cycle": TRIALS_PER_CYCLE, "workers": workers,
            "python_hash_seed": os.environ.get("PYTHONHASHSEED"),
            "models": list(MODELS), "families": list(FAMILIES),
            "common_random_numbers": True,
            "adaptation_cost_cycles": [RAMP_START, CYCLES - 1],
            "final_stable_cycles": [60, CYCLES - 1],
            "minimum_adaptation_advantage_nats_per_event": MIN_ADAPTATION_ADVANTAGE,
            "final_noninferiority_margin_nats_per_event": FINAL_NONINFERIORITY_MARGIN,
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "interval": "97.5% paired percentile bootstrap; adjusted across two families",
        },
        "summary": summarize(records), "per_world": records,
        "limitations": [
            "Results generalize only to the two predefined synthetic gradual-transition families.",
            "Shifted and stationary-control worlds share random draws, but generated event sequences differ when the rule changes.",
            "Settling time is self-referenced to each model's final stable loss and is descriptive, not confirmatory.",
            "The task scores online next-event NLL; it does not directly score causal recovery or identify which cognitive layer caused adaptation.",
            "Twenty seeds per family measure variation within these generators, not robustness across natural environments.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--out", default=str(REPO / "docs" / "post_shift_adaptation_results.json"))
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
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
