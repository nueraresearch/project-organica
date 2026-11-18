"""
Phase K -- Comparative Advantage Search
==================================================================
The harness for the three candidate task families in
`docs/PHASE-K-PREREGISTRATION.md`, plus a negative control that validates
the harness itself.

**The question Phase K asks.** Not "can Organica do X?" but "what is
Organica *uniquely* good at?" Three candidate families, each derived from a
mechanism the project has actually measured, each scored against the
strongest simple baseline that could plausibly solve it.

**Why the baselines get a grid.** Every simple baseline is swept over a
declared hyperparameter grid and its **best** score on the scored metric is
the number used in the comparison. That is deliberately generous to the
baseline: it can only make an Organica win harder to claim. A strawman
baseline is the single most likely way to manufacture a false positive, and
Phases H, I and J all failed against baselines that were given no tuning
advantage at all.

**Why there is a negative control.** `K0` reruns the Phase H held-out
next-event task, where Organica is *known* to lose to a first-order Markov
baseline (0.4126 vs 0.5040). If this harness reports an Organica win there,
the harness is broken and the campaign stops. This is an instrument check
before the campaign, not an analysis of it.

**What is not here.** No engine changes. The cognitive engine is frozen; the
matched ablations are in-process subclasses, exactly as the campaign runner
does it.

Usage:
    python benchmarks/phase_k_campaign.py --families K1 K2 K3 --seeds 10 --workers 3
    python benchmarks/phase_k_campaign.py --control-only          # the harness check
    python benchmarks/phase_k_campaign.py --smoke                 # 2 seeds, tiny worlds
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.ablation_metrics import edges_implied_by_structures  # noqa: E402
from organica.memory import MemoryService  # noqa: E402
from organica.paths import temp_db  # noqa: E402
from organica.sleep import SleepService  # noqa: E402
from benchmarks import engine_stamp

EVENTS_PER_CYCLE = 8
BOOTSTRAP_REPLICATES = 10_000

# Bonferroni across the three candidate families: alpha 0.05 / 3 = 0.016667
# two-sided, so the 98.33% percentile interval is the decision interval.
FAMILY_COUNT = 3
DECISION_ALPHA = 0.05 / FAMILY_COUNT
DECISION_LOWER_Q = DECISION_ALPHA / 2
DECISION_UPPER_Q = 1 - DECISION_ALPHA / 2

# The grid each simple baseline is swept over. Declared before the run.
COOC_WINDOW_GRID = ("all", 300, 150, 75, 30)
COOC_MIN_COUNT_GRID = (3, 5, 10)
TEMPORAL_LOOKBACK_GRID = (1, 3, 5)
TEMPORAL_MIN_COUNT_GRID = (3, 5, 10)

NOISE_FEATURES = ("quartz", "static", "velvet", "random")


# ==================================================================
# The world generator. One shape serves all three families: an entity
# is a feature set that is active over a window of cycles, and the
# events emitted during that window are pairs drawn from its features.
# ==================================================================

@dataclass(frozen=True)
class Entity:
    name: str
    features: tuple[str, ...]
    start: int
    weight: int = 3
    end: int | None = None


def generate_world(seed: int, cycles: int, entities: list[Entity], *,
                   noise_rate: float = 0.10,
                   events_per_cycle: int = EVENTS_PER_CYCLE) -> dict:
    """Emit an event stream plus the exact ground truth for scoring.

    At each cycle the active entities are those whose window contains it.
    An entity is drawn from the active set with probability proportional to
    its weight, and the event is a pair of that entity's features. With
    probability `noise_rate` a pair drawn from a noise-only vocabulary is
    emitted instead.
    """
    rng = random.Random(seed)
    events: list[str] = []
    labels: list[str] = []
    for cycle in range(cycles):
        active = [e for e in entities
                  if e.start <= cycle and (e.end is None or cycle < e.end)]
        if not active:
            continue
        weights = [e.weight for e in active]
        for _ in range(events_per_cycle):
            if rng.random() < noise_rate:
                pair = rng.sample(NOISE_FEATURES, 2)
                labels.append("noise")
            else:
                e = rng.choices(active, weights=weights, k=1)[0]
                pair = rng.sample(e.features, 2)
                labels.append(e.name)
            events.append(" ".join(pair))
    gold = {}
    for e in entities:
        gold[e.name] = sorted({
            tuple(sorted((a, b)))
            for i, a in enumerate(e.features) for b in e.features[i + 1:]
        })
    return {
        "events": events,
        "labels": labels,
        "gold_pairs": gold,
        "entities": [
            {"name": e.name, "features": list(e.features), "start": e.start,
             "end": e.end, "weight": e.weight} for e in entities
        ],
        "config": {"seed": seed, "cycles": cycles, "noise_rate": noise_rate,
                   "events_per_cycle": events_per_cycle},
    }


# ==================================================================
# Scoring
# ==================================================================

def pair_f1(predicted: set[tuple[str, str]],
             gold: set[tuple[str, str]],
             exclude_from_fp: set[tuple[str, str]] | None = None) -> dict:
    """F1 of predicted pairs against gold. Anything predicted outside gold
    counts as a false positive, except for pairs in `exclude_from_fp`.

    The exclusion matters when the gold is split across two declared groups:
    a model that holds both the scaffold and the late structure should not
    be punished for holding the scaffold when it is scored on the late
    structure. Without it, an endpoint that scores a model on two groups
    cannot reach 1.0, and an unachievable endpoint is a broken instrument.
    """
    exclude = exclude_from_fp or set()
    tp = len(predicted & gold)
    fp = len(predicted - gold - exclude)
    fn = len(gold - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 6), "recall": round(recall, 6),
            "f1": round(f1, 6), "true_positive": tp, "false_positive": fp,
            "false_negative": fn, "predicted_pairs": len(predicted),
            "gold_pairs": len(gold)}


def harmonic(a: float, b: float) -> float:
    return 2 * a * b / (a + b) if (a + b) else 0.0


# ==================================================================
# The simple baselines. These are deliberately trivial and independent of
# Organica's own machinery: they count co-occurrences and temporal
# transitions over the event text and nothing else.
# ==================================================================

def _tags(event: str) -> list[str]:
    return event.split()


def cooc_pairs(events: list[str], *, window_cycles: int | str, min_count: int,
               events_per_cycle: int = EVENTS_PER_CYCLE) -> set[tuple[str, str]]:
    """Undirected co-occurrence pairs within a trailing window of cycles."""
    if window_cycles == "all":
        window = events
    else:
        cut = len(events) - int(window_cycles) * events_per_cycle
        window = events[max(0, cut):]
    counts: dict[tuple[str, str], int] = {}
    for event in window:
        tags = sorted(set(_tags(event)))
        for i, a in enumerate(tags):
            for b in tags[i + 1:]:
                counts[(a, b)] = counts.get((a, b), 0) + 1
    return {pair for pair, n in counts.items() if n >= min_count}


def temporal_pairs(events: list[str], *, lookback: int, min_count: int,
                   window_cycles: int | str = "all",
                   events_per_cycle: int = EVENTS_PER_CYCLE) -> set[tuple[str, str]]:
    """Pairs where a tag appears within `lookback` events before another."""
    if window_cycles == "all":
        window = events
    else:
        cut = len(events) - int(window_cycles) * events_per_cycle
        window = events[max(0, cut):]
    counts: dict[tuple[str, str], int] = {}
    for i, event in enumerate(window):
        here = set(_tags(event))
        for j in range(max(0, i - lookback), i):
            there = set(_tags(window[j]))
            for a in here:
                for b in there:
                    if a == b:
                        continue
                    key = tuple(sorted((a, b)))
                    counts[key] = counts.get(key, 0) + 1
    return {pair for pair, n in counts.items() if n >= min_count}


# ==================================================================
# Organica
# ==================================================================

def organica_pairs(events: list[str], cycles: int, seed: int,
                   sleep_cls=SleepService, evidence=None) -> set[tuple[str, str]]:
    """Run the engine over the stream and return the feature pairs its
    surviving structures imply."""
    from dataclasses import asdict

    db = temp_db("phase_k.db")
    db.unlink(missing_ok=True)
    mem = MemoryService(db_path=str(db))
    svc = sleep_cls(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    report = None
    try:
        for cycle in range(cycles):
            chunk = events[cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]
            for event in chunk:
                mem.store(event, event_type="event", source=f"cycle:{cycle}")
            if chunk:
                report = svc.run_sleep_cycle()
        if evidence is not None:
            evidence.append(getattr(svc, "manipulation", None))
        structures = []
        if report:
            for name in ("concepts", "phrases", "loops", "predictions", "anomalies",
                         "meta_concepts", "processes", "workflow_concepts",
                         "hypotheses", "theories", "questions", "dreams",
                         "investigations", "experiments"):
                structures.extend(asdict(item) for item in getattr(report, name, []))
        edges = edges_implied_by_structures(structures)
        return {tuple(sorted((a, b))) for a, targets in edges.items()
                for b in targets if a != b}
    finally:
        mem.close()
        db.unlink(missing_ok=True)
        # temp_db creates a directory per call; leave nothing behind.
        try:
            db.parent.rmdir()
        except OSError:
            pass


# ==================================================================
# The matched ablations. Each removes exactly the mechanism the family
# hypothesises, so that a win can be attributed rather than merely seen.
# ==================================================================

class NoQuestionsService(SleepService):
    """K1's mechanism: question generation drives novelty assimilation."""
    def _form_theories_and_questions(self, hypotheses, prior):
        theories, _questions = super()._form_theories_and_questions(hypotheses, prior)
        return theories, []


class NoDreamsService(SleepService):
    """K3's mechanism: dreams integrate beliefs into coherent structure."""
    def _generate_categorized_dreams(self, *a, **k):
        return []


def no_falsification_service():
    """K2's mechanism: falsification drives belief revision.

    Imported rather than copied: this ablation is long and its exact
    behaviour is already recorded in the ablation study.
    """
    from benchmarks.ablation_study import NoFalsificationService
    return NoFalsificationService


# ==================================================================
# The three candidate families
# ==================================================================

def _core_entities(prefix: str, count: int, features_per: int = 4) -> list[tuple[str, ...]]:
    # Every tag must be at least four characters: the engine extracts tags
    # with r"\\b[a-zA-Z]{4,}\\b", so a shorter one would be invisible to it.
    # Six entities x four features needs twenty-four distinct tags.
    alphabet = ("amber", "birch", "cedar", "maple", "indigo", "fern",
                "willow", "yarrow", "signal", "marker", "context", "shared",
                "harbor", "lantern", "meadow", "nectar", "orchard", "pebble",
                "quarry", "ribbon", "summit", "thicket", "urchin", "walnut")
    out = []
    for i in range(count):
        start = i * features_per
        chunk = alphabet[start:start + features_per]
        if len(chunk) < features_per:
            raise ValueError(
                f"need {count * features_per} distinct tags, "
                f"the vocabulary has {len(alphabet)}")
        out.append(chunk)
    return out


def task_k1(seed: int, scale: int = 1, primary_factory=None) -> dict:
    """Incremental world modeling.

    A two-entity scaffold is observed from cycle 1; a third entity is
    introduced at cycle 150 and the world keeps running. Scored on whether
    the persistent structure covers all three.

    ``primary_factory`` is the K2 build's K1 no-op arm when this task is
    called by the K2 block. With no factory the historical shipped arm is
    used, so every existing result remains reproducible.
    """
    from benchmarks.force_matrix import NoQuestionsService
    cycles = 300 // scale
    late = 150 // scale
    feats = _core_entities("k1", 3)
    entities = [
        Entity("core_a", feats[0], 0, weight=3),
        Entity("core_b", feats[1], 0, weight=3),
        Entity("late_c", feats[2], late, weight=3),
    ]
    world = generate_world(seed, cycles, entities)
    gold_all = set(world["gold_pairs"]["core_a"]) | set(world["gold_pairs"]["core_b"]) \
        | set(world["gold_pairs"]["late_c"])
    gold_late = set(world["gold_pairs"]["late_c"])
    gold_core = set(world["gold_pairs"]["core_a"]) | set(world["gold_pairs"]["core_b"])

    scores = _score_models(world, cycles, seed, gold_all, gold_late, gold_core,
                           NoQuestionsService, "NO_QUESTIONS",
                           primary_factory=primary_factory)
    return {"family": "K1", "seed": seed, "cycles": cycles,
            "protocol": {"late_entity_cycle": late,
                         "entities": world["entities"],
                         "primary_arm": ("K1 no-op treatment"
                                         if primary_factory is not None
                                         else "shipped Organica"),
                         "primary": "pair F1 over all three entities' gold pairs"},
            **scores}


def task_k2(seed: int, scale: int = 1, primary_factory=None) -> dict:
    """Belief revision.

    One entity holds the world until cycle 200, then a different entity
    takes over and the first stops appearing. Scored on whether the
    structure tracks the new regime without carrying the old one forward.

    ``primary_factory`` is the K2 treatment arm when this task is called by
    the K2 block. With no factory the historical shipped arm is used.
    """
    cycles = 300 // scale
    switch = 200 // scale
    feats = _core_entities("k2", 2)
    entities = [
        Entity("old_a", feats[0], 0, weight=1, end=switch),
        Entity("new_b", feats[1], switch, weight=1),
    ]
    world = generate_world(seed, cycles, entities)
    gold_new = set(world["gold_pairs"]["new_b"])
    gold_old = set(world["gold_pairs"]["old_a"])

    scores = _score_models(world, cycles, seed, gold_new, None, gold_old,
                           no_falsification_service(), "NO_FALSIFICATION",
                           revision=True, primary_factory=primary_factory)
    return {"family": "K2", "seed": seed, "cycles": cycles,
            "protocol": {"switch_cycle": switch,
                         "entities": world["entities"],
                         "primary_arm": ("K2 treatment"
                                         if primary_factory is not None
                                         else "shipped Organica"),
                         "primary": "revision F1: current-regime pairs are the "
                                    "gold, the retired regime's pairs are false "
                                    "positives"},
            **scores}


def task_k3(seed: int, scale: int = 1) -> dict:
    """Longitudinal knowledge integration.

    Three scaffold entities from cycle 1, then one new entity every 100
    cycles for 600 cycles. Scored jointly on keeping the early structure
    and incorporating the late structure: a model that keeps everything
    and learns nothing scores badly, and so does the reverse.
    """
    from benchmarks.force_matrix import NoDreamsService
    cycles = 600 // scale
    step = 100 // scale
    feats = _core_entities("k3", 6)
    entities = [Entity(f"core_{i}", feats[i], 0, weight=3) for i in range(3)]
    entities += [Entity(f"late_{i}", feats[3 + i], step * (i + 1), weight=1)
                 for i in range(3)]
    world = generate_world(seed, cycles, entities)
    gold_core = set()
    for i in range(3):
        gold_core |= set(world["gold_pairs"][f"core_{i}"])
    gold_late = set()
    for i in range(3):
        gold_late |= set(world["gold_pairs"][f"late_{i}"])

    scores = _score_models(world, cycles, seed, gold_core, gold_late, None,
                           NoDreamsService, "NO_DREAMS", joint=True)
    return {"family": "K3", "seed": seed, "cycles": cycles,
            "protocol": {"entities": world["entities"],
                         "primary": "harmonic mean of core-retention F1 and "
                                    "late-incorporation F1"},
            **scores}


def _score_models(world, cycles, seed, gold_primary, gold_late, gold_retired,
                  ablation_cls, ablation_name, *, revision=False, joint=False,
                  primary_factory=None) -> dict:
    """Run every model on one world and score it."""
    events = world["events"]
    results = []

    primary_evidence = []
    organica = organica_pairs(
        events, cycles, seed, sleep_cls=primary_factory or SleepService,
        evidence=primary_evidence)
    results.append({"model": "organica", **_score_one(organica, gold_primary,
                                                       gold_late, gold_retired,
                                                       revision, joint)})

    abl = organica_pairs(events, cycles, seed, sleep_cls=ablation_cls)
    results.append({"model": f"organica_{ablation_name}",
                    **_score_one(abl, gold_primary, gold_late, gold_retired,
                                 revision, joint)})

    # --- the simple baselines, swept over the declared grid ---------------
    cooc_cfgs = [(w, m) for w in COOC_WINDOW_GRID for m in COOC_MIN_COUNT_GRID]
    for window, min_count in cooc_cfgs:
        pairs = cooc_pairs(events, window_cycles=window, min_count=min_count)
        results.append({"model": "cooccurrence", "config": {"window": window,
                         "min_count": min_count},
                        **_score_one(pairs, gold_primary, gold_late, gold_retired,
                                     revision, joint)})

    temp_cfgs = [(lb, m) for lb in TEMPORAL_LOOKBACK_GRID for m in TEMPORAL_MIN_COUNT_GRID]
    for lookback, min_count in temp_cfgs:
        pairs = temporal_pairs(events, lookback=lookback, min_count=min_count)
        results.append({"model": "temporal_graph", "config": {"lookback": lookback,
                         "min_count": min_count},
                        **_score_one(pairs, gold_primary, gold_late, gold_retired,
                                     revision, joint)})

    # --- keep the best configuration of each baseline family --------------
    best = {}
    for family in ("cooccurrence", "temporal_graph"):
        cands = [r for r in results if r["model"] == family]
        best[family] = max(cands, key=lambda r: r["primary"])
    return {
        "models": results,
        "best_baseline": best,
        "best_simple_baseline": max(
            (best["cooccurrence"], best["temporal_graph"]),
            key=lambda r: r["primary"]),
        "primary_manipulation": (primary_evidence[0]
                                 if primary_evidence else None),
    }


def _score_one(predicted, gold_primary, gold_late, gold_retired,
               revision, joint) -> dict:
    """Score one model's predicted pair set.

    normal  -- primary F1 against gold_primary
    revision-- primary F1 against gold_primary with the retired regime's
               pairs counted as false positives
    joint   -- primary is the harmonic mean of core-retention F1 and
               late-incorporation F1
    """
    if revision:
        negatives = set(gold_retired or ())
        tp = len(predicted & set(gold_primary))
        fp = len(predicted & negatives) + len(
            predicted - set(gold_primary) - negatives)
        fn = len(set(gold_primary) - predicted)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        current = pair_f1(predicted, set(gold_primary))
        stale = len(predicted & negatives)
        return {"primary": round(f1, 6),
                "current_f1": current["f1"],
                "stale_pairs": stale,
                "stale_rate": round(stale / len(negatives), 6) if negatives else 0.0}

    if joint:
        core = set(gold_primary)
        late = set(gold_late)
        # Each component is scored against its own group, with the other
        # group excluded from the false positives. A model holding both
        # scores 1.0 on both and 1.0 on the joint endpoint.
        core_score = pair_f1(predicted, core, exclude_from_fp=late)
        late_score = pair_f1(predicted, late, exclude_from_fp=core)
        return {"primary": round(harmonic(core_score["f1"], late_score["f1"]), 6),
                "core_retention_f1": core_score["f1"],
                "late_incorporation_f1": late_score["f1"],
                "core_precision": core_score["precision"],
                "core_recall": core_score["recall"],
                "late_precision": late_score["precision"],
                "late_recall": late_score["recall"]}

    primary = pair_f1(predicted, set(gold_primary))
    out = {"primary": primary["f1"], "precision": primary["precision"],
           "recall": primary["recall"]}
    if gold_late:
        # The supporting incorporation score: how much of the LATE entity's
        # structure did the model hold, without being punished for also
        # holding the scaffold.
        out["late_f1"] = pair_f1(predicted, set(gold_late),
                                 exclude_from_fp=set(gold_primary) - set(gold_late))["f1"]
    return out


TASKS = {"K1": task_k1, "K2": task_k2, "K3": task_k3}


# ==================================================================
# The negative control: K0
# ==================================================================

def control(seed: int) -> dict:
    """Rerun the Phase H held-out next-event task as a harness check.

    Organica is known to lose there (0.4126 vs the Markov baseline's
    0.5040). If this harness reports otherwise, the harness is broken.
    """
    from benchmarks.heldout_prediction import run as heldout_run
    result = heldout_run(seed)
    scores = {r["model"]: r for r in result["results_known_training_tags"]}
    organica = scores["organica_g1_predictions"]
    markov = scores["first_order_markov"]
    return {
        "seed": seed,
        "organica_f1": organica["f1"],
        "markov_f1": markov["f1"],
        "organica_loses": organica["f1"] < markov["f1"],
        "note": ("Harness validation only. Excluded from the three-family "
                 "multiplicity adjustment and from every claim."),
    }


# ==================================================================
# Statistics
# ==================================================================

def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return ordered[lo] if lo == hi else ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def paired_interval(values: list[float], seed: int) -> list[float]:
    """Bonferroni-adjusted paired percentile bootstrap interval."""
    rng = random.Random(seed)
    n = len(values)
    means = sorted(statistics.mean(values[rng.randrange(n)] for _ in range(n))
                   for _ in range(BOOTSTRAP_REPLICATES))
    return [round(_quantile(means, DECISION_LOWER_Q), 6),
            round(_quantile(means, DECISION_UPPER_Q), 6)]


def summarize(records: list[dict], family: str) -> dict:
    organica = [r["organica"] for r in records]
    best = [r["best_simple_baseline"]["primary"] for r in records]
    ablation_name = records[0]["all_models"][1]["model"]
    ablation = [r["ablation"] for r in records]

    diff_best = [o - b for o, b in zip(organica, best)]
    diff_abl = [o - a for o, a in zip(organica, ablation)]
    ci_best = paired_interval(diff_best, 20261023 + hash(family) % 1000)
    ci_abl = paired_interval(diff_abl, 20261023 + 500 + hash(family) % 1000)

    if ci_best[0] > 0:
        verdict = "SUPPORTED"
    elif ci_best[1] < 0:
        verdict = "REVERSED"
    else:
        verdict = "INCONCLUSIVE"
    # Differences are Organica minus the matched ablation, so implicating the
    # mechanism requires the whole paired interval to be above zero.
    mechanism_implicated = ci_abl[0] > 0

    return {
        "family": family,
        "n_seeds": len(records),
        "decision_interval": {
            "level": f"{100*(1-DECISION_ALPHA):.2f}%",
            "rule": "Bonferroni across the three candidate families",
            "alpha": DECISION_ALPHA,
        },
        "organica_primary_mean": round(statistics.mean(organica), 6),
        "best_simple_baseline_primary_mean": round(statistics.mean(best), 6),
        "paired_organica_minus_best_baseline": {
            "n": len(diff_best),
            "mean": round(statistics.mean(diff_best), 6),
            "interval": ci_best,
            "positive_favors_organica": True,
        },
        "matched_ablation": {
            "name": ablation_name,
            "primary_mean": round(statistics.mean(ablation), 6),
            "paired_organica_minus_ablation": {
                "n": len(diff_abl),
                "mean": round(statistics.mean(diff_abl), 6),
                "interval": ci_abl,
            },
            "mechanism_implicated": mechanism_implicated,
            "note": ("Attribution only: true when the paired Organica minus "
                     "ablation interval is wholly above zero."),
        },
        "verdict": verdict,
        "per_seed": [
            {"seed": r["seed"], "organica": r["organica"],
             "best_baseline": r["best_simple_baseline"]["primary"],
             "best_baseline_config": r["best_simple_baseline"].get("config"),
             "ablation": r["ablation"]}
            for r in records
        ],
    }


# ==================================================================
# Campaign
# ==================================================================

def _run_one(args) -> dict:
    family, seed, scale, primary_factory = args
    task = TASKS[family]
    if primary_factory is not None and family in ("K1", "K2"):
        record = task(seed, scale, primary_factory=primary_factory)
    else:
        record = task(seed, scale)
    return {
        "family": family,
        "seed": seed,
        "organica": record["models"][0]["primary"],
        "ablation": record["models"][1]["primary"],
        "best_simple_baseline": record["best_simple_baseline"],
        "all_models": record["models"],
        "manipulation": record.get("primary_manipulation"),
        "protocol": record["protocol"],
    }


def _normalise_record(r: dict) -> dict:
    """Bring a saved per-seed record into the internal shape.

    The results file has been written in two shapes over the life of this
    harness -- the flat `per_model_detail` form and the `records` form --
    so a resume has to understand both.
    """
    if "organica" in r:
        return r
    models = r.get("models", [])
    best = max((m for m in models
                if m["model"] in ("cooccurrence", "temporal_graph")),
               key=lambda m: m["primary"], default=None)
    return {
        "family": r["family"],
        "seed": r["seed"],
        "organica": r.get("organica_primary"),
        "ablation": r.get("ablation_primary"),
        "best_simple_baseline": best or {"primary": None},
        "all_models": models,
        "protocol": r.get("protocol", {}),
    }


# ==================================================================
# The live recording: one reader, used by every consumer of the file
# ==================================================================

# The row fields that name a cell.  The writer here emits ``family`` and
# ``seed``; a harness that keeps the same one-line-per-cell format names its
# own (Phase L uses ``arm``, ``label`` and ``seed``).  One reader serves all of
# them, so no two consumers of a recording can disagree about what it holds.
CHECKPOINT_KEY_FIELDS = ("family", "seed")

# The row fields that are the cell's measurement.  A repeated cell must agree
# on all of them; the key fields are its identity, not its content.
CHECKPOINT_CELL_FIELDS = (
    "organica", "ablation", "best_simple_baseline", "all_models",
    "manipulation", "protocol",
)


class CheckpointError(RuntimeError):
    """The live recording cannot be read as one complete record per cell.

    A refusal, not a crash: the recording is written before the result is
    assembled and before a resume appends to it, so a recording that cannot be
    read must not be appended to.  Skipping a broken row would hide it, and the
    next reader would inherit a file that no longer parses.

    The error carries its refusal code, message and evidence.  A caller that
    publishes a receipt -- the K2 block's runner -- adds the shape it needs in
    its own subclass, so this module does not define receipt fields it never
    produces.
    """

    def __init__(self, code: str, message: str, **evidence):
        super().__init__(message)
        self.code = code
        self.message = message
        self.evidence = evidence


def _cell_key(row: dict, families: tuple[str, ...] | None = None,
              *, key_fields: tuple[str, ...] = CHECKPOINT_KEY_FIELDS,
              ) -> tuple[str | int, ...] | None:
    """The cell a checkpoint row records, or ``None`` if it records no cell.

    ``families`` is the set of families this harness can write, not the set one
    invocation asked for: a recording legitimately holds rows from families a
    subset resume is not running, and those rows are still cells.  It names the
    row's ``family`` field, which is this campaign's filter; a harness with no
    family axis passes ``None``.

    Every key field must be present and usable as a key: a non-empty string or
    a non-boolean integer.  A row that fails that is not a cell, and the caller
    decides whether it is a torn final line or corruption.
    """
    key: list[str | int] = []
    for name in key_fields:
        value = row.get(name)
        if isinstance(value, bool):
            return None
        if isinstance(value, str):
            if not value:
                return None
        elif not isinstance(value, int):
            return None
        key.append(value)
    if families is not None and row.get("family") not in families:
        return None
    return tuple(key)


def _cell_payload(row: dict,
                  cell_fields: tuple[str, ...] = CHECKPOINT_CELL_FIELDS) -> str:
    """The measured content of a row, for comparing two rows of one cell."""
    return json.dumps({name: row.get(name) for name in cell_fields},
                      sort_keys=True, separators=(",", ":"))


def read_checkpoint_report(path: Path | str, *,
                           families: tuple[str, ...] | None = None,
                           key_fields: tuple[str, ...] = CHECKPOINT_KEY_FIELDS,
                           cell_fields: tuple[str, ...] = CHECKPOINT_CELL_FIELDS,
                           ) -> dict:
    """Read the live recording into one record per cell.

    The campaign appends one line per completed cell and flushes it, so two
    things can be true of the file without a bug, and only those two are
    tolerated:

    * **A torn final line.**  A kill during the append leaves the last line
      unparseable.  It is dropped and reported; every earlier row was written
      with a flush and an fsync, so it is complete.  A *complete* final line
      without a trailing newline parses, so it is kept and is not partial.
    * **A repeated cell.**  Rows are only ever appended, so the later row wins.
      The same seed under the same arm is deterministic, so two rows for one
      cell must agree on the measured fields: an agreeing repeat is counted, a
      disagreeing one is refused rather than silently resolved.

    Anything else is corruption.  An unreadable or non-cell row *before* the
    last line would silently remove a completed cell from the assembled
    result, which is a wrong result rather than a smaller one, so it refuses;
    so does a **parseable** final row that is not a cell, because a torn write
    is exactly a line that does not parse.  Every consumer of this file -- the
    K2 block's result assembly, this campaign's own ``--resume`` and Phase L's
    ``--resume`` -- reads it here, so they cannot disagree about what the
    recording contains.  ``key_fields`` and ``cell_fields`` let a harness with
    a different record shape use the same rules rather than its own reader.
    """
    path = Path(path)
    report = {
        "path": str(path),
        "key_fields": list(key_fields),
        "cell_fields": list(cell_fields),
        "rows": 0,
        "cells": 0,
        "duplicate_cells": 0,
        "duplicate_rows": 0,
        "blank_lines": 0,
        "partial_final_row": False,
        "partial_final_line": None,
        "records": [],
    }
    if not path.exists():
        return report

    lines = path.read_text(encoding="utf-8").splitlines()
    last = max((index for index, line in enumerate(lines) if line.strip()),
               default=None)
    rows: dict[tuple[str | int, ...], dict] = {}
    payloads: dict[tuple[str | int, ...], str] = {}
    first_lines: dict[tuple[str | int, ...], int] = {}
    repeated: set[tuple[str | int, ...]] = set()
    order: list[tuple[str | int, ...]] = []
    for index, line in enumerate(lines):
        if not line.strip():
            report["blank_lines"] += 1
            continue
        final = index == last
        parsed = True
        try:
            row = json.loads(line)
        except ValueError:
            parsed, row = False, None
        key = (_cell_key(row, families, key_fields=key_fields)
               if isinstance(row, dict) else None)
        if key is None:
            if final and not parsed:
                report["partial_final_row"] = True
                report["partial_final_line"] = index + 1
                continue
            raise CheckpointError(
                "CHECKPOINT_CORRUPT",
                "the checkpoint has a row that is not a cell",
                checkpoint_path=str(path),
                line=index + 1,
                rows_read=report["rows"],
                reason="unreadable" if not parsed else "not_a_cell_row",
            )
        report["rows"] += 1
        if key in rows:
            if _cell_payload(row, cell_fields) != payloads[key]:
                evidence = {
                    "checkpoint_path": str(path),
                    "cell": dict(zip(key_fields, key)),
                    "first_line": first_lines[key],
                    "second_line": index + 1,
                    "differing_fields": [
                        name for name in cell_fields
                        if row.get(name) != rows[key].get(name)],
                }
                for name, value in zip(key_fields, key):
                    evidence.setdefault(name, value)
                raise CheckpointError(
                    "CHECKPOINT_DUPLICATE_DISAGREES",
                    "two checkpoint rows record different values for one cell",
                    **evidence,
                )
            repeated.add(key)
            report["duplicate_rows"] += 1
        else:
            order.append(key)
            first_lines[key] = index + 1
        rows[key] = row
        payloads[key] = _cell_payload(row, cell_fields)

    report["cells"] = len(order)
    report["duplicate_cells"] = len(repeated)
    report["records"] = [rows[key] for key in order]
    return report


def read_checkpoint(path: Path | str, *,
                    families: tuple[str, ...] | None = None,
                    key_fields: tuple[str, ...] = CHECKPOINT_KEY_FIELDS,
                    cell_fields: tuple[str, ...] = CHECKPOINT_CELL_FIELDS,
                    ) -> list[dict]:
    """The checkpoint's records: one per cell, in first-appearance order."""
    return read_checkpoint_report(path, families=families,
                                  key_fields=key_fields,
                                  cell_fields=cell_fields)["records"]


def repair_partial_final_row(path: Path | str, *,
                             families: tuple[str, ...] | None = None,
                             key_fields: tuple[str, ...] = CHECKPOINT_KEY_FIELDS,
                             cell_fields: tuple[str, ...] = CHECKPOINT_CELL_FIELDS,
                             ) -> dict:
    """Truncate a torn final line, then re-read the recording.

    A partial tail is harmless while it is the last line, and becomes an
    unreadable row in the middle of the file the moment the campaign appends
    the next cell -- which would refuse the resume that was meant to recover
    the run.  The tail is not a record and never was, so cutting it back to the
    last complete row loses nothing and keeps the recording append-only.
    """
    path = Path(path)
    report = read_checkpoint_report(path, families=families,
                                    key_fields=key_fields,
                                    cell_fields=cell_fields)
    if not report["partial_final_row"]:
        return report
    data = path.read_bytes()
    offset = 0
    for line in data.splitlines(keepends=True)[:report["partial_final_line"] - 1]:
        offset += len(line)
    with open(path, "r+b") as handle:
        handle.truncate(offset)
    repaired = read_checkpoint_report(path, families=families,
                                      key_fields=key_fields,
                                      cell_fields=cell_fields)
    repaired["repaired_partial_row"] = True
    repaired["partial_final_line"] = report["partial_final_line"]
    return repaired


def run_campaign(families: list[str], seeds: list[int], workers: int,
                 scale: int = 1, out_path: Path | None = None,
                 resume: bool = False,
                 checkpoint_path: Path | None = None,
                 primary_factories: dict | None = None) -> dict:
    factories = primary_factories or {}
    jobs = [(f, s, scale, factories.get(f)) for f in families for s in seeds]
    started = time.time()
    records: list[dict] = []

    if checkpoint_path is None and out_path is not None:
        checkpoint_path = out_path.with_suffix(".ndjson")

    def checkpoint(rec: dict) -> None:
        """Append one line per completed seed and flush it.

        This is the live recording: an append-only trail of the run that
        cannot be truncated by a kill and that a human can read while the
        campaign is still going.
        """
        if checkpoint_path is None:
            return
        try:
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            with open(checkpoint_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
        except Exception:
            pass

    if not resume and checkpoint_path is not None and checkpoint_path.exists():
        # A fresh run starts a fresh recording. The JSON is the artefact;
        # the NDJSON is the live trail of this run.
        try:
            checkpoint_path.unlink()
        except OSError:
            pass

    if resume and out_path is not None:
        # The live recording is read by the same strict reader the K2 block
        # uses, so the two consumers of one file cannot disagree about it.  A
        # torn final line is truncated back to the last complete row *before*
        # anything appends, because appending past it would turn a tolerable
        # last line into an unreadable interior one.
        checkpoint_report = None
        if checkpoint_path is not None and checkpoint_path.exists():
            checkpoint_report = repair_partial_final_row(
                checkpoint_path, families=tuple(TASKS))
            if checkpoint_report.get("repaired_partial_row"):
                print(f"  the recording's last line was incomplete; truncated "
                      f"it to {checkpoint_report['cells']} complete cell(s)")
            if checkpoint_report["duplicate_cells"]:
                print(f"  the recording repeats "
                      f"{checkpoint_report['duplicate_cells']} cell(s); "
                      f"keeping one row per cell")
        prior = None
        if out_path.exists():
            try:
                prior = json.loads(out_path.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"  the results file could not be read ({exc}); "
                      f"falling back to the checkpoint log")
                prior = None
        if prior is not None:
            records = [_normalise_record(r) for r in prior.get("records", [])]
            if not records:
                records = [_normalise_record(r)
                           for r in prior.get("per_model_detail", [])]
        elif checkpoint_report is not None:
            # The results file is gone but the live recording survived.
            records = [_normalise_record(row)
                       for row in checkpoint_report["records"]]
            print(f"  rebuilt {len(records)} record(s) from the checkpoint log")
        if records:
            done = {(r["family"], r["seed"]) for r in records}
            jobs = [j for j in jobs if (j[0], j[1]) not in done]
            print(f"  resuming: {len(records)} seed(s) already done, "
                  f"{len(jobs)} to go")

    def flush(complete: bool = False) -> None:
        """Write the per-seed results as they arrive.

        Two things, because a long campaign must never lose progress:

        * the results file is written **atomically** -- to a temporary file
          and then renamed -- so a kill during the write cannot truncate it;
        * an append-only NDJSON **checkpoint** is written and flushed after
          every seed, so there is a live, human-readable record of the run
          that survives even if the results file is lost.

        The partial file is marked incomplete.
        """
        if out_path is None:
            return
        payload = {
            "protocol": {
                "preregistration": "docs/PHASE-K-PREREGISTRATION.md",
                "seeds": seeds,
                "workers": workers,
                "python_hash_seed": "0",
                "bootstrap_replicates": BOOTSTRAP_REPLICATES,
                "decision_alpha": DECISION_ALPHA,
                "cycle_scale": scale,
                "baseline_rule": ("every simple baseline is swept over the "
                                  "declared grid and its BEST score is used; "
                                  "this is generous to the baseline by design"),
                "wall_clock_seconds": round(time.time() - started, 1),
                "complete": complete,
            },
            "summaries": {
                f: summarize([r for r in records if r["family"] == f], f)
                for f in families
                if any(r["family"] == f for r in records)
            },
            "confirmed_families": [],
            "records": records,
            "per_model_detail": [
                {"family": r["family"], "seed": r["seed"],
                 "organica_primary": r["organica"],
                 "ablation_primary": r["ablation"],
                 "models": r["all_models"],
                 "protocol": r["protocol"]}
                for r in records
            ],
        }
        payload["confirmed_families"] = [
            f for f, s in payload["summaries"].items() if s["verdict"] == "SUPPORTED"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_path.with_suffix(out_path.suffix + ".tmp")
        tmp.write_text(json.dumps(engine_stamp.stamp(payload), indent=2), encoding="utf-8")
        os.replace(tmp, out_path)

    if workers > 1:
        # as_completed, not pool.map. pool.map yields in SUBMISSION order, so
        # a single slow first job blocks every checkpoint until it finishes --
        # and if the run is killed before that, every completed seed is lost.
        # as_completed yields each result the moment it is done, which is the
        # only behaviour that makes a long campaign safe to stop and resume.
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_run_one, job): job for job in jobs}
            for fut in as_completed(futures):
                rec = fut.result()
                records.append(rec)
                checkpoint(rec)
                flush()
                print(f"  {rec['family']} seed {rec['seed']}: "
                      f"organica={rec['organica']} "
                      f"baseline={rec['best_simple_baseline']['primary']} "
                      f"ablation={rec['ablation']}", flush=True)
    else:
        for job in jobs:
            rec = _run_one(job)
            records.append(rec)
            checkpoint(rec)
            flush()
            print(f"  {rec['family']} seed {rec['seed']}: "
                  f"organica={rec['organica']} "
                  f"baseline={rec['best_simple_baseline']['primary']} "
                  f"ablation={rec['ablation']}", flush=True)

    summary = {}
    for family in families:
        summary[family] = summarize([r for r in records if r["family"] == family],
                                     family)
    confirmed = [f for f, s in summary.items() if s["verdict"] == "SUPPORTED"]
    return {
        "protocol": {
            "preregistration": "docs/PHASE-K-PREREGISTRATION.md",
            "seeds": seeds,
            "workers": workers,
            "python_hash_seed": "0",
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "decision_alpha": DECISION_ALPHA,
            "baseline_rule": ("every simple baseline is swept over the declared "
                              "grid and its BEST score is used; this is "
                              "generous to the baseline by design"),
            "wall_clock_seconds": round(time.time() - started, 1),
        },
        "summaries": summary,
        "confirmed_families": confirmed,
        "per_model_detail": [
            {"family": r["family"], "seed": r["seed"],
             "organica_primary": r["organica"],
             "ablation_primary": r["ablation"],
             "models": r["all_models"],
             "protocol": r["protocol"]}
            for r in records
        ],
        "terminal_outcome": (
            "A confirmed family names the task to take to a larger-n "
            "confirmation campaign. No confirmed family means the search "
            "failed within these three families: do NOT design V2, and record "
            "the negative-results map."),
    }


def ceiling_check() -> dict:
    """Every endpoint must be reachable.

    An instrument audit, not an experiment. A metric that a *perfect* model
    cannot score 1.0 on is broken: it either has a ceiling nobody can reach,
    or it penalises two requirements that contradict each other. This is the
    K0 control's sibling -- K0 checks that the pipeline can report a loss,
    this checks that the metric can report a win.

    Found the hard way: the joint endpoint originally scored each group
    against the other group's content as false positives, so a model holding
    the scaffold AND the late structure could reach only 0.667.
    """
    core = {("a", "b"), ("a", "c"), ("b", "c")}
    late = {("x", "y"), ("x", "z"), ("y", "z")}
    noise = {("n1", "n2"), ("n3", "n4")}

    cases = [
        # (family, gold_primary, gold_late, gold_retired, revision, joint,
        #  perfect prediction, expected primary)
        ("K1", core | late, late, None, False, False, core | late, 1.0),
        ("K2", late, None, core, True, False, late, 1.0),
        ("K3", core, late, None, False, True, core | late, 1.0),
    ]
    results = []
    ok = True
    for (family, gold_p, gold_l, gold_r, revision, joint, perfect,
         expected) in cases:
        got = _score_one(perfect, gold_p, gold_l, gold_r, revision, joint)["primary"]
        passed = abs(got - expected) < 1e-9
        ok = ok and passed
        results.append({"family": family, "perfect_model_score": got,
                        "expected": expected, "passed": passed})
    return {"passed": ok, "cases": results,
            "note": ("A perfect model must score 1.0 on every endpoint. "
                     "This check is an instrument audit and produces no "
                     "experimental claim.")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="*", default=["K1", "K2", "K3"])
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--control-only", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="run the instrument audits only (K0 control + "
                         "endpoint ceiling check)")
    ap.add_argument("--resume", action="store_true",
                    help="continue from the seeds already in the output file")
    ap.add_argument("--smoke", action="store_true",
                    help="one seed per family, cycles divided by 10 -- for "
                         "harness validation only, never a result")
    ap.add_argument("--scale", type=int, default=1,
                    help="divide every cycle count by this factor")
    ap.add_argument("--out", default=str(REPO / "docs" / "phase_k_results.json"))
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    scale = args.scale
    if args.smoke and scale == 1:
        scale = 10

    if args.control_only or args.self_test:
        print("=" * 80)
        print("K0 -- HARNESS VALIDATION (expected: Organica LOSES to Markov)")
        print("=" * 80)
        c = control(20261023)
        print(json.dumps(c, indent=2))
        if not c["organica_loses"]:
            print("\n*** THE HARNESS IS BROKEN: it reported an Organica win on a "
                  "task where Organica is known to lose. STOP. ***")
            sys.exit(1)
        print("\nharness validated: the loss is reproduced.")

        print()
        print("=" * 80)
        print("ENDPOINT CEILING CHECK (expected: a perfect model scores 1.0)")
        print("=" * 80)
        ceil = ceiling_check()
        for case in ceil["cases"]:
            print(f"  {case['family']}: perfect model scores "
                  f"{case['perfect_model_score']:.6f} "
                  f"(expected {case['expected']}) "
                  f"{'ok' if case['passed'] else '*** FAIL ***'}")
        if not ceil["passed"]:
            print("\n*** AN ENDPOINT IS UNREACHABLE. STOP. ***")
            sys.exit(1)
        print("\nall endpoints are reachable.")
        return

    seeds = [20261023 + i for i in range(args.seeds)]
    if args.smoke:
        seeds = seeds[:1]

    print("=" * 80)
    print("PHASE K -- COMPARATIVE ADVANTAGE SEARCH")
    print(f"  families {args.families}   seeds {seeds}")
    print("=" * 80)

    # The control runs first. If it fails, the campaign does not run.
    c = control(20261023)
    print(f"  K0 control: organica={c['organica_f1']} markov={c['markov_f1']} "
          f"organica_loses={c['organica_loses']}")
    if not c["organica_loses"]:
        print("*** THE HARNESS IS BROKEN -- STOP. ***")
        sys.exit(1)
    print("  harness validated.")

    # The endpoint ceiling check runs second. If an endpoint cannot be
    # reached by a perfect model, the metric is broken and the campaign
    # does not run.
    ceil = ceiling_check()
    for case in ceil["cases"]:
        print(f"  ceiling {case['family']}: perfect model scores "
              f"{case['perfect_model_score']:.6f} "
              f"{'ok' if case['passed'] else '*** FAIL ***'}")
    if not ceil["passed"]:
        print("*** AN ENDPOINT IS UNREACHABLE -- STOP. ***")
        sys.exit(1)
    print("  all endpoints reachable.\n")

    result = run_campaign(args.families, seeds, args.workers, scale,
                          out_path=Path(args.out), resume=args.resume)
    result["control"] = c
    result["ceiling_check"] = ceil
    result["protocol"]["cycle_scale"] = scale
    result["protocol"]["complete"] = True

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for family, s in result["summaries"].items():
        ci = s["paired_organica_minus_best_baseline"]
        print(f"  {family}: {s['verdict']:<12} organica {s['organica_primary_mean']:.4f} "
              f"vs baseline {s['best_simple_baseline_primary_mean']:.4f}  "
              f"diff {ci['mean']:+.4f} interval {ci['interval']}")
    print()
    print(f"  confirmed families: {result['confirmed_families'] or 'none'}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(engine_stamp.stamp(result), indent=2), encoding="utf-8")
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
