"""Phase L: Plasticity-Coherence Measurement -- the harness.

A MEASUREMENT phase, not a benchmark hunt. Every previous phase asked "can
Organica do X?"; this one asks how much displacement pressure is required for
new structure to displace old structure.

The protocol is frozen in docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md
and was committed before any outcome existed.

The two instrument audits run BEFORE the campaign and the campaign does not run
if either fails:

  1. THE DISCRIMINATION CONTROL. First-seen-wins must score DI ~ 0 and
     PI ~ 1; last-seen-wins must score DI ~ 1 and PI ~ 0. If the metric
     cannot separate "never revises" from "always revises", it is measuring
     nothing.
  2. THE ENDPOINT CEILING CHECK. A synthetic perfect model must score 1.0 on
     both DI and PI. A metric a perfect model cannot reach is broken.

The engine is Organica 1, FROZEN. This harness imports it; it never edits it.
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
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from benchmarks.ablation_metrics import edges_implied_by_structures  # noqa: E402

# ----------------------------------------------------------------------
# Protocol constants. Every one of these is declared in the frozen
# preregistration; none of them may be tuned to fit an outcome.
# ----------------------------------------------------------------------

PREREGISTRATION = "docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md"

SEEDS = tuple(20261023 + i for i in range(10))
CYCLES = 600
EVENTS_PER_CYCLE = 12
NOISE_RATE = 0.10
BOOTSTRAP_REPLICATES = 10_000

#: The decision interval. The frozen preregistration states a "98.33% paired
#: percentile bootstrap" twice (section 6, criterion 4, and the protocol
#: table in section 8), so that is the number implemented here.
#:
#: Note for protocol review: 98.33% corresponds to a two-sided alpha of
#: 0.0167 = 0.05/3, whereas "Bonferroni across the arms" over five arms
#: gives 0.05/5 = 0.01 and therefore a 99% interval. The two readings
#: disagree, and the code follows the NUMBER the preregistration states
#: rather than the parenthetical gloss. This is flagged in Amendment 1 for
#: the owner to settle before the campaign runs; it has no effect on any
#: outcome that exists today, because no Phase L outcome exists yet.
DECISION_ALPHA = 0.05 / 3
DECISION_LOWER_Q = DECISION_ALPHA / 2
DECISION_UPPER_Q = 1 - DECISION_ALPHA / 2

#: When the late group arrives, as a FRACTION of the run, unless an arm says
#: otherwise. 150/600 = 0.25 at full scale.
#:
#: It is a fraction and not an absolute cycle number because an absolute
#: number is not scale-invariant: a reduced-scale pilot then runs fewer
#: cycles than the late group's arrival, the late group never becomes active,
#: and the late structure is never available to be measured. See
#: `degeneracy_audit()` and Amendment 1.
ARRIVAL_FRACTION = 0.25

#: The primary axis: the support ratio (late : early).
#: 1:4 through 6:1. The K3 2x2 located the boundary between 1:3 and 3:1.
SUPPORT_RATIOS = ((1, 4), (1, 3), (1, 2), (1, 1), (2, 1), (3, 1), (4, 1), (6, 1))

#: The secondary axes, each swept alone with everything else at baseline.
ARRIVAL_TIMINGS = (50, 100, 150, 250, 400)
NOVELTY_DENSITIES = (0.5, 1.0, 2.0, 4.0)
BELIEF_CAP_PRESSURES = (3, 6, 12, 18, 24)
CONTRADICTION_PRESSURES = (False, True)

#: Baselines. The grids are declared; the BEST score is always used.
COOC_WINDOW_GRID = ("all", 300, 150, 75, 30)
COOC_MIN_COUNT_GRID = (3, 5, 10)
TEMPORAL_LOOKBACK_GRID = (1, 3, 5)
TEMPORAL_MIN_COUNT_GRID = (3, 5, 10)

NOISE_FEATURES = ("quartz", "static", "velvet", "random")


@dataclass(frozen=True)
class Entity:
    """An entity is a feature set active over a window of cycles."""
    name: str
    features: tuple[str, ...]
    start: int
    end: int | None = None
    weight: float = 1.0


@dataclass
class Arm:
    """One point on one axis."""
    arm: str                 # "V1" .. "V5"
    variable: str            # human name
    label: str               # the parameterised value
    params: dict = field(default_factory=dict)


def _core_entities(count: int = 6, features_per: int = 4) -> list[tuple[str, ...]]:
    """Twenty-four distinct tags. Every tag is >= 4 characters, because the
    engine extracts with r"\\b[a-zA-Z]{4,}\\b" and a shorter one is invisible."""
    alphabet = ("amber", "birch", "cedar", "maple", "indigo", "fern",
                "willow", "yarrow", "signal", "marker", "context", "shared",
                "harbor", "lantern", "meadow", "nectar", "orchard", "pebble",
                "quarry", "ribbon", "summit", "thicket", "urchin", "walnut")
    out = []
    for i in range(count):
        chunk = alphabet[i * features_per:(i + 1) * features_per]
        if len(chunk) < features_per:
            raise ValueError("not enough distinct tags")
        out.append(chunk)
    return out


def build_world(seed: int, *, support_ratio: tuple[int, int] = (1, 3),
                arrival: int | None = None, density: float = 1.0,
                cap_pressure: int = 6, contradiction: bool = False,
                cycles: int = CYCLES):
    """One world, parameterised.

    The world has an EARLY group (the incumbent) and a LATE group (the
    newcomer). The late group arrives at `arrival` and never stops. The
    support ratio sets the relative weight of the two groups, which is the
    primary independent variable.

    `arrival` defaults to ARRIVAL_FRACTION of the run, NOT to a fixed cycle
    number: a fixed arrival is not scale-invariant, and a reduced-scale pilot
    then runs out of cycles before the late group ever appears -- at which
    point the late structure is never available and DI is unmeasurable.

    `cap_pressure` adds extra competing singleton entities so the belief pool
    has to choose between more candidates.

    `contradiction` makes the late group share ONE feature with the early
    group, so the two compete for the same subject rather than merely
    coexisting. This is the arm that could show the operative variable is
    conflict rather than strength.
    """
    late_w, early_w = support_ratio
    if arrival is None:
        arrival = max(1, int(round(cycles * ARRIVAL_FRACTION)))
    feats = _core_entities(6)
    entities = [Entity(f"early_{i}", feats[i], 0, weight=early_w) for i in range(3)]
    entities += [Entity(f"late_{i}", feats[3 + i], arrival, weight=late_w)
                 for i in range(3)]

    if contradiction:
        # The late group shares ONE feature with the EARLY group: the same
        # subject, two expectations -- the thing Layer 5 coalesces.
        #
        # The shared feature must come from the early entity. Sharing a
        # late feature with itself would rebuild late_0 exactly as it already
        # was, and the arm would measure nothing at all.
        shared = feats[0][0]
        entities[3] = Entity("late_0", (shared,) + feats[3][1:], arrival, weight=late_w)

    # Extra competing entities for belief-cap pressure.
    extra_alphabet = ("cobalt", "dapple", "ember", "fable", "glimmer", "hollow")
    for i in range(max(0, cap_pressure - 6)):
        name = extra_alphabet[i % len(extra_alphabet)] + str(i)
        entities.append(Entity(f"extra_{i}", (name, name + "north", name + "south"),
                               0, weight=1.0))

    events_per_cycle = max(1, int(round(EVENTS_PER_CYCLE * density)))
    return _generate(seed, cycles, entities, events_per_cycle)


def _generate(seed: int, cycles: int, entities: list[Entity], events_per_cycle: int):
    rng = random.Random(seed)
    events: list[str] = []
    for cycle in range(cycles):
        active = [e for e in entities
                  if e.start <= cycle and (e.end is None or cycle < e.end)]
        if not active:
            continue
        weights = [e.weight for e in active]
        for _ in range(events_per_cycle):
            if rng.random() < NOISE_RATE:
                pair = rng.sample(NOISE_FEATURES, 2)
            else:
                e = rng.choices(active, weights=weights, k=1)[0]
                pair = rng.sample(e.features, 2)
            events.append(" ".join(pair))
    gold = {}
    for e in entities:
        gold[e.name] = {tuple(sorted((a, b)))
                         for i, a in enumerate(e.features)
                         for b in e.features[i + 1:]}
    return {"events": events, "gold": gold, "entities": entities,
            "cycles": cycles, "events_per_cycle": events_per_cycle}


# ----------------------------------------------------------------------
# The metrics
# ----------------------------------------------------------------------

def gold_groups(world, contradiction: bool = False):
    """(early pairs, late pairs). The extra competing entities are neither:
    they are the pool's other competitors, not part of either group."""
    early, late = set(), set()
    for name, pairs in world["gold"].items():
        if name.startswith("early_"):
            early |= pairs
        elif name.startswith("late_"):
            late |= pairs
    return early, late


def _available(world, pairs: set) -> int:
    """How many of `pairs` actually occur in the event stream. A pair that
    never co-occurs was never available to be retained, so counting it in
    the denominator would measure the generator, not the organism."""
    seen = set()
    for ev in world["events"]:
        t = sorted(set(ev.split()))
        for i, a in enumerate(t):
            for b in t[i + 1:]:
                seen.add((a, b))
    return len(pairs & seen)


def indices(predicted: set, early_gold: set, late_gold: set,
            early_available: int, late_available: int) -> dict:
    """The Displacement Index, the Preservation Index, and the raw counts.

    DI = late_retained / late_available
    PI = early_retained / early_available

    **An index whose denominator is zero is NOT MEASURABLE, and is reported
    as `None` -- never as 0.0.** A zero denominator means the structure in
    question was never available to the organism, so the ratio is undefined;
    scoring it 0.0 would report "the organism retained nothing" for a
    condition in which the organism was never given anything to retain.
    That is the difference between a measurement and a fabrication, and this
    project has been burned by exactly that difference before: the Phase L
    pilot at reduced scale reported DI = 0.000 across the whole sweep for
    exactly this reason. Such cells are EXCLUDED from the curve and counted
    as unmeasurable, never silently included as zeros.
    """
    late_ret = len(predicted & late_gold)
    early_ret = len(predicted & early_gold)
    di = (late_ret / late_available) if late_available else None
    pi = (early_ret / early_available) if early_available else None
    return {
        "displacement_index": round(di, 6) if di is not None else None,
        "preservation_index": round(pi, 6) if pi is not None else None,
        "displacement_measurable": bool(late_available),
        "preservation_measurable": bool(early_available),
        "late_retained": late_ret,
        "late_available": late_available,
        "early_retained": early_ret,
        "early_available": early_available,
    }


# ----------------------------------------------------------------------
# The models
# ----------------------------------------------------------------------

def organica_pairs(events: list[str], cycles: int, seed: int,
                   events_per_cycle: int = EVENTS_PER_CYCLE) -> set:
    """Run the FROZEN engine over the stream and return the feature pairs its
    surviving structures imply.

    The engine is not modified. This is the same extraction the published
    campaigns use, so Phase L's numbers are comparable with Phase K's.

    `events_per_cycle` is the world's own density. It must be passed in: the
    V3 arm varies the event density, and chunking a denser stream at the
    default rate would feed the engine only part of the world while
    reporting it as a complete run.
    """
    from dataclasses import asdict

    from organica.memory import MemoryService
    from organica.paths import temp_db
    from organica.sleep import SleepService

    db = temp_db("phase_l.db")
    db.unlink(missing_ok=True)
    mem = MemoryService(db_path=str(db))
    svc = SleepService(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    report = None
    try:
        for cycle in range(cycles):
            chunk = events[cycle * events_per_cycle:(cycle + 1) * events_per_cycle]
            for event in chunk:
                mem.store(event, event_type="event", source=f"cycle:{cycle}")
            if chunk:
                report = svc.run_sleep_cycle()
        structures = []
        if report:
            for name in ("concepts", "phrases", "loops", "predictions",
                         "anomalies", "meta_concepts", "processes",
                         "workflow_concepts", "hypotheses", "theories",
                         "questions", "dreams", "investigations", "experiments"):
                structures.extend(asdict(item) for item in getattr(report, name, []))
        edges = edges_implied_by_structures(structures)
        return {tuple(sorted((a, b))) for a, t in edges.items() for b in t if a != b}
    finally:
        mem.close()
        db.unlink(missing_ok=True)
        try:
            db.parent.rmdir()
        except OSError:
            pass


def cooc_pairs(events, *, window_cycles, min_count, events_per_cycle=EVENTS_PER_CYCLE):
    if window_cycles == "all":
        window = events
    else:
        cut = len(events) - int(window_cycles) * events_per_cycle
        window = events[max(0, cut):]
    counts: dict[tuple[str, str], int] = {}
    for ev in window:
        tags = sorted(set(ev.split()))
        for i, a in enumerate(tags):
            for b in tags[i + 1:]:
                counts[(a, b)] = counts.get((a, b), 0) + 1
    return {p for p, n in counts.items() if n >= min_count}


def temporal_pairs(events, *, lookback, min_count, events_per_cycle=EVENTS_PER_CYCLE):
    counts: dict[tuple[str, str], int] = {}
    for i, ev in enumerate(events):
        here = sorted(set(ev.split()))
        for a in here:
            for j in range(max(0, i - lookback), i):
                there = sorted(set(events[j].split()))
                for b in there:
                    if a != b:
                        counts[(a, b)] = counts.get((a, b), 0) + 1
    return {p for p, n in counts.items() if n >= min_count}


def first_seen_wins(events, early_gold, late_gold, **kw):
    """The control: keep the first structure, ignore everything after."""
    return set(early_gold)


def last_seen_wins(events, early_gold, late_gold, **kw):
    """The mirror control: keep only the most recent structure."""
    return set(late_gold)


def perfect_model(events, early_gold, late_gold, **kw):
    """The ceiling: hold everything."""
    return set(early_gold) | set(late_gold)


# ----------------------------------------------------------------------
# One cell of the design
# ----------------------------------------------------------------------

def run_cell(job) -> dict:
    """Run one (arm, parameter, seed) cell: every model on one world."""
    arm, label, params, seed = job["arm"], job["label"], job["params"], job["seed"]
    world = build_world(seed, **params)
    early_gold, late_gold = gold_groups(world)
    early_avail = _available(world, early_gold)
    late_avail = _available(world, late_gold)
    events = world["events"]
    epc = world["events_per_cycle"]

    results = {}

    predicted = organica_pairs(events, world["cycles"], seed,
                               events_per_cycle=epc)
    results["organica"] = indices(predicted, early_gold, late_gold,
                                  early_avail, late_avail)

    # The simple baselines, swept over their declared grids. BEST is used.
    # "Best" is measured on DI, the axis under study. A configuration whose
    # DI is unmeasurable (the late structure was never available) cannot be
    # the best and is ranked last -- not treated as a zero.
    best_cooc = None
    for w in COOC_WINDOW_GRID:
        for mc in COOC_MIN_COUNT_GRID:
            p = cooc_pairs(events, window_cycles=w, min_count=mc,
                           events_per_cycle=epc)
            idx = indices(p, early_gold, late_gold, early_avail, late_avail)
            if best_cooc is None or _di_rank(idx) > _di_rank(best_cooc[1]):
                best_cooc = ((w, mc), idx)
    results["best_cooccurrence"] = best_cooc[1]
    results["best_cooccurrence_config"] = {"window": best_cooc[0][0],
                                           "min_count": best_cooc[0][1]}

    best_temp = None
    for lb in TEMPORAL_LOOKBACK_GRID:
        for mc in TEMPORAL_MIN_COUNT_GRID:
            p = temporal_pairs(events, lookback=lb, min_count=mc,
                               events_per_cycle=epc)
            idx = indices(p, early_gold, late_gold, early_avail, late_avail)
            if best_temp is None or _di_rank(idx) > _di_rank(best_temp[1]):
                best_temp = ((lb, mc), idx)
    results["best_temporal_graph"] = best_temp[1]
    results["best_temporal_graph_config"] = {"lookback": best_temp[0][0],
                                             "min_count": best_temp[0][1]}

    results["first_seen_wins"] = indices(
        first_seen_wins(events, early_gold, late_gold), early_gold, late_gold,
        early_avail, late_avail)
    results["last_seen_wins"] = indices(
        last_seen_wins(events, early_gold, late_gold), early_gold, late_gold,
        early_avail, late_avail)
    results["perfect_model"] = indices(
        perfect_model(events, early_gold, late_gold), early_gold, late_gold,
        early_avail, late_avail)

    return {"arm": arm, "label": label, "params": params, "seed": seed,
            "results": results}


def _di_rank(idx: dict) -> float:
    """A sortable stand-in for DI, used to pick a baseline's best config.

    An unmeasurable DI (None) ranks below every real score, because a
    configuration that could not measure displacement is not a
    configuration that displaced anything.
    """
    di = idx["displacement_index"]
    return -1.0 if di is None else di


# ----------------------------------------------------------------------
# The instrument audits
# ----------------------------------------------------------------------

def degeneracy_audit(scale: int = 1) -> dict:
    """The design must be LIVE before any cell is run.

    The two preregistered audits check the METRIC: can it separate the two
    poles, and can a perfect model reach the ceiling. This third audit
    checks the DESIGN: does each arm actually vary what it claims to vary,
    in a world where the late structure is available to be measured at all?

    It exists because the Phase L pilot produced a clean-looking result
    (DI = 0.000 at every point of the sweep) that was in fact an artefact:
    at reduced scale the late group arrived after the run had ended, so the
    late structure was never available, and the metric dutifully reported
    zero displacement for a condition in which nothing could have been
    displaced. The other two audits passed on that world, because they check
    the metric and the metric was fine. The DESIGN was dead.

    Every check here is failable by construction:
      1. Both groups must be available for measurement in every arm cell.
      2. The support ratio must actually change the event mix.
      3. The contradiction arm must actually differ from the non-contradiction
         arm (it is easy to write an arm that rebuilds the world unchanged).
      4. The density arm must actually change the number of events.
    """
    problems = []
    checked = []

    def world_for(arm: str, label: str):
        cycles = CYCLES // scale
        if arm == "V1":
            lw, ew = (int(x) for x in label.split(":"))
            return build_world(SEEDS[0], support_ratio=(lw, ew), cycles=cycles)
        if arm == "V2":
            # The same PROPORTIONAL scaling build_jobs applies, so the audit
            # examines the world the campaign would actually run.
            frac = int(label) / CYCLES
            return build_world(SEEDS[0],
                               arrival=max(1, int(round(frac * cycles))),
                               cycles=cycles)
        if arm == "V3":
            return build_world(SEEDS[0], density=float(label), cycles=cycles)
        if arm == "V4":
            return build_world(SEEDS[0], cap_pressure=int(label), cycles=cycles)
        if arm == "V5":
            return build_world(SEEDS[0], contradiction=(label == "on"),
                               cycles=cycles)
        raise ValueError(arm)

    # 1. Both groups available everywhere.
    for arm, labels in (("V1", [f"{a}:{b}" for a, b in SUPPORT_RATIOS]),
                        ("V2", [str(a) for a in ARRIVAL_TIMINGS]),
                        ("V3", [str(d) for d in NOVELTY_DENSITIES]),
                        ("V4", [str(c) for c in BELIEF_CAP_PRESSURES]),
                        ("V5", ["off", "on"])):
        for label in labels:
            w = world_for(arm, label)
            e, l = gold_groups(w)
            ea, la = _available(w, e), _available(w, l)
            checked.append({"arm": arm, "label": label,
                            "early_available": ea, "late_available": la})
            if la == 0:
                problems.append(
                    f"{arm} {label}: the late structure is never available, so "
                    f"DI is unmeasurable (the late group never became active)")
            if ea == 0:
                problems.append(
                    f"{arm} {label}: the early structure is never available, "
                    f"so PI is unmeasurable")

    # 2. The support ratio must change the mix of early vs late events.
    late_shares = {}
    for (lw, ew) in SUPPORT_RATIOS:
        w = build_world(SEEDS[0], support_ratio=(lw, ew), cycles=CYCLES // scale)
        late_tags = set()
        for ent in w["entities"]:
            if ent.name.startswith("late_"):
                late_tags.update(ent.features)
        n = sum(1 for ev in w["events"]
                if late_tags & set(ev.split()))
        late_shares[f"{lw}:{ew}"] = n / max(1, len(w["events"]))
    values = list(late_shares.values())
    if max(values) - min(values) < 0.01:
        problems.append(
            "the support ratio does not change the early/late event mix, so "
            f"V1 cannot move DI (shares: {late_shares})")

    # 3. The contradiction arm must differ from the plain arm, AND must
    # actually make the two groups compete for the same subject.
    off = build_world(SEEDS[0], contradiction=False, cycles=CYCLES // scale)
    on = build_world(SEEDS[0], contradiction=True, cycles=CYCLES // scale)
    if off["events"] == on["events"]:
        problems.append(
            "the contradiction arm produces an identical event stream, so V5 "
            "measures nothing")
    if off["gold"] == on["gold"]:
        problems.append(
            "the contradiction arm produces an identical gold set, so the "
            "early and late groups are scored against the same structure")
    # The shared feature must come from the EARLY group, or the two groups
    # do not compete for the same subject and the arm is not testing
    # conflict at all.
    early_feats = set()
    for ent in on["entities"]:
        if ent.name.startswith("early_"):
            early_feats.update(ent.features)
    late_feats = set()
    for ent in on["entities"]:
        if ent.name.startswith("late_"):
            late_feats.update(ent.features)
    if not (early_feats & late_feats):
        problems.append(
            "the contradiction arm shares no feature between the early and "
            "late groups, so it is not testing conflict")

    # 3b. The early and late gold sets must stay disjoint in EVERY arm, or
    # DI and PI are scored against overlapping structure and neither index
    # means what the preregistration says it means.
    for arm, labels in (("V1", [f"{a}:{b}" for a, b in SUPPORT_RATIOS]),
                        ("V2", [str(a) for a in ARRIVAL_TIMINGS]),
                        ("V3", [str(d) for d in NOVELTY_DENSITIES]),
                        ("V4", [str(c) for c in BELIEF_CAP_PRESSURES]),
                        ("V5", ["off", "on"])):
        for label in labels:
            w = world_for(arm, label)
            e, l = gold_groups(w)
            overlap = len(e & l)
            if overlap:
                problems.append(
                    f"{arm} {label}: the early and late gold sets overlap in "
                    f"{overlap} pair(s), so DI and PI are not separable")

    # 4. The density arm must change the number of events.
    densities = {}
    for d in NOVELTY_DENSITIES:
        w = build_world(SEEDS[0], density=d, cycles=CYCLES // scale)
        densities[str(d)] = len(w["events"])
    if len(set(densities.values())) != len(densities):
        problems.append(
            f"the density arm does not change the event count ({densities})")

    return {"passed": not problems, "problems": problems,
            "cells": checked, "late_event_shares": late_shares,
            "event_counts_by_density": densities,
            "scale": scale,
            "note": "Instrument audit. Produces no experimental claim."}


def discrimination_control() -> dict:
    """The metric must separate 'never revises' from 'always revises'.

    If first-seen-wins and last-seen-wins score the same, the metric is
    measuring nothing and the campaign does not run.
    """
    world = build_world(SEEDS[0])
    early_gold, late_gold = gold_groups(world)
    early_avail = _available(world, early_gold)
    late_avail = _available(world, late_gold)

    fsw = indices(first_seen_wins(world["events"], early_gold, late_gold),
                  early_gold, late_gold, early_avail, late_avail)
    lsw = indices(last_seen_wins(world["events"], early_gold, late_gold),
                  early_gold, late_gold, early_avail, late_avail)

    ok = True
    problems = []
    if fsw["displacement_index"] > 0.05:
        ok = False
        problems.append(
            f"first-seen-wins scored DI {fsw['displacement_index']}, expected ~0")
    if fsw["preservation_index"] < 0.95:
        ok = False
        problems.append(
            f"first-seen-wins scored PI {fsw['preservation_index']}, expected ~1")
    if lsw["displacement_index"] < 0.95:
        ok = False
        problems.append(
            f"last-seen-wins scored DI {lsw['displacement_index']}, expected ~1")
    if lsw["preservation_index"] > 0.05:
        ok = False
        problems.append(
            f"last-seen-wins scored PI {lsw['preservation_index']}, expected ~0")
    if abs(fsw["displacement_index"] - lsw["displacement_index"]) < 0.5:
        ok = False
        problems.append(
            "the metric does not separate never-revises from always-revises")

    return {"passed": ok, "first_seen_wins": fsw, "last_seen_wins": lsw,
            "problems": problems,
            "note": "Instrument audit. Produces no experimental claim."}


def ceiling_check() -> dict:
    """A perfect model must score 1.0 on both indices.

    A metric a perfect model cannot reach is a broken instrument.
    """
    world = build_world(SEEDS[0])
    early_gold, late_gold = gold_groups(world)
    early_avail = _available(world, early_gold)
    late_avail = _available(world, late_gold)
    got = indices(perfect_model(world["events"], early_gold, late_gold),
                  early_gold, late_gold, early_avail, late_avail)

    problems = []
    if got["displacement_index"] < 1.0:
        problems.append(f"perfect model DI {got['displacement_index']}, expected 1.0")
    if got["preservation_index"] < 1.0:
        problems.append(f"perfect model PI {got['preservation_index']}, expected 1.0")

    return {"passed": not problems, "perfect_model": got, "problems": problems,
            "note": "Instrument audit. Produces no experimental claim."}


# ----------------------------------------------------------------------
# The arms
# ----------------------------------------------------------------------

def build_jobs(families: list[str], seeds: list[int], scale: int = 1) -> list[dict]:
    """Every cell of every requested arm."""
    jobs = []
    for fam in families:
        if fam == "V1":
            for (lw, ew) in SUPPORT_RATIOS:
                for s in seeds:
                    jobs.append({"arm": "V1", "label": f"{lw}:{ew}",
                                 "params": {"support_ratio": (lw, ew),
                                            "cycles": CYCLES // scale},
                                 "seed": s})
        elif fam == "V2":
            for a in ARRIVAL_TIMINGS:
                for s in seeds:
                    # Arrival is scaled PROPORTIONALLY with the run, so that
                    # "arrives at cycle 400 of 600" stays that proportion at
                    # any scale and the late group is always present for
                    # part of the run.
                    frac = a / CYCLES
                    jobs.append({"arm": "V2", "label": str(a),
                                 "params": {"arrival": max(1, int(round(frac * (CYCLES // scale)))),
                                            "cycles": CYCLES // scale},
                                 "seed": s})
        elif fam == "V3":
            for d in NOVELTY_DENSITIES:
                for s in seeds:
                    jobs.append({"arm": "V3", "label": str(d),
                                 "params": {"density": d,
                                            "cycles": CYCLES // scale},
                                 "seed": s})
        elif fam == "V4":
            for c in BELIEF_CAP_PRESSURES:
                for s in seeds:
                    jobs.append({"arm": "V4", "label": str(c),
                                 "params": {"cap_pressure": c,
                                            "cycles": CYCLES // scale},
                                 "seed": s})
        elif fam == "V5":
            for c in CONTRADICTION_PRESSURES:
                for s in seeds:
                    jobs.append({"arm": "V5", "label": "on" if c else "off",
                                 "params": {"contradiction": c,
                                            "cycles": CYCLES // scale},
                                 "seed": s})
        else:
            raise ValueError(f"unknown arm {fam}")
    return jobs


# ----------------------------------------------------------------------
# The analysis
# ----------------------------------------------------------------------

def _quantile(values, q):
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return ordered[lo] if lo == hi else ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def paired_interval(values: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    n = len(values)
    means = sorted(statistics.mean(values[rng.randrange(n)] for _ in range(n))
                   for _ in range(BOOTSTRAP_REPLICATES))
    return [round(_quantile(means, DECISION_LOWER_Q), 6),
            round(_quantile(means, DECISION_UPPER_Q), 6)]


def summarize_arm(cells: list[dict], arm: str) -> dict:
    """One arm: the DI and PI curves, and the Revision Threshold if the
    curves cross."""
    by_label: dict[str, list[dict]] = {}
    for c in cells:
        if c["arm"] == arm:
            by_label.setdefault(c["label"], []).append(c)

    order = [lbl for lbl in _label_order(arm) if lbl in by_label]
    curve = []
    unmeasurable = []
    for lbl in order:
        rows = by_label[lbl]
        # Cells whose DI or PI could not be measured are EXCLUDED, not
        # included as zeros. A cell with no denominator has no value to
        # average.
        dis = [r["results"]["organica"]["displacement_index"] for r in rows
               if r["results"]["organica"]["displacement_index"] is not None]
        pre = [r["results"]["organica"]["preservation_index"] for r in rows
               if r["results"]["organica"]["preservation_index"] is not None]
        excluded = len(rows) - min(len(dis), len(pre))
        if excluded:
            unmeasurable.append({"label": lbl, "excluded_cells": excluded})
        curve.append({
            "label": lbl,
            "n_seeds": len(rows),
            "n_measurable": min(len(dis), len(pre)),
            "n_excluded_unmeasurable": excluded,
            "displacement_index_mean": round(statistics.mean(dis), 6) if dis else None,
            "displacement_index_stdev": round(statistics.stdev(dis), 6) if len(dis) > 1 else 0.0,
            "preservation_index_mean": round(statistics.mean(pre), 6) if pre else None,
            "preservation_index_stdev": round(statistics.stdev(pre), 6) if len(pre) > 1 else 0.0,
        })

    di = [c["displacement_index_mean"] for c in curve]
    pi = [c["preservation_index_mean"] for c in curve]

    # An arm with any unmeasurable point cannot be judged: a missing point
    # is not a value, and treating it as one would manufacture a curve.
    all_measurable = all(x is not None for x in di) and all(x is not None for x in pi)

    if not all_measurable:
        criteria = {"di_monotone_increasing": False,
                    "pi_monotone_decreasing": False,
                    "di_range_at_least_0_25": False,
                    "curves_cross": False,
                    "crossing_interior": False}
        return {"arm": arm, "n_seeds": len(by_label[order[0]]) if order else 0,
                "curve": curve, "criteria": criteria,
                "verdict": "UNMEASURABLE",
                "unmeasurable_cells": unmeasurable,
                "crossing_label": None, "rt_bootstrap_interval": None,
                "decision_interval": {
                    "level": f"{100*(1-DECISION_ALPHA):.2f}%",
                    "rule": "as stated in the frozen preregistration"}}

    monotone_di = all(a <= b + 1e-9 for a, b in zip(di, di[1:]))
    monotone_pi = all(a >= b - 1e-9 for a, b in zip(pi, pi[1:]))
    range_ok = bool(di) and (max(di) - min(di)) >= 0.25

    # The Revision Threshold: the first label where DI crosses PI.
    crossing = None
    for i in range(1, len(curve)):
        if di[i - 1] <= pi[i - 1] and di[i] > pi[i]:
            crossing = i
            break
    interior = crossing is not None and 0 < crossing < len(curve) - 1

    # The paired bootstrap over seeds: does the crossing reproduce?
    #
    # The statistic resampled is the CROSSING LOCATION -- the index of the
    # first label at which DI overtakes PI -- because that is what the
    # preregistration calls the RT and what criterion 4 is about ("the RT
    # estimated from a paired bootstrap over seeds has a 98.33% interval
    # that excludes both endpoints of the sweep"). The interval is a
    # PERCENTILE interval over the resampled crossing locations, and it
    # excludes both endpoints when every resample places the crossing
    # strictly inside the sweep.
    #
    # Seeds are resampled PAIRED across labels: one bootstrap replicate
    # draws a seed set and evaluates every label on that same seed set, so
    # the common-mode structure of the seed pairing is preserved.
    rt_interval = None
    rt_replicates_with_crossing = 0
    if crossing is not None:
        labels_with_rows = [lbl for lbl in order if by_label.get(lbl)]
        n_seeds = min(len(by_label[lbl]) for lbl in labels_with_rows)
        crossings = []
        for b in range(BOOTSTRAP_REPLICATES):
            rng = random.Random(9000 + b)
            # One paired draw of seed positions, shared by every label.
            picks = [rng.randrange(n_seeds) for _ in range(n_seeds)]
            d_sampled, p_sampled = [], []
            for lbl in labels_with_rows:
                rows = by_label[lbl]
                ds = [rows[p % len(rows)]["results"]["organica"]["displacement_index"]
                      for p in picks]
                ps = [rows[p % len(rows)]["results"]["organica"]["preservation_index"]
                      for p in picks]
                d_sampled.append(statistics.mean(ds))
                p_sampled.append(statistics.mean(ps))
            # Where does THIS resample place the crossing?
            for i in range(1, len(d_sampled)):
                if d_sampled[i - 1] <= p_sampled[i - 1] and d_sampled[i] > p_sampled[i]:
                    crossings.append(i)
                    break
        rt_replicates_with_crossing = len(crossings)
        if crossings:
            rt_interval = [round(_quantile(crossings, DECISION_LOWER_Q), 6),
                           round(_quantile(crossings, DECISION_UPPER_Q), 6)]

    criteria = {
        "di_monotone_increasing": monotone_di,
        "pi_monotone_decreasing": monotone_pi,
        "di_range_at_least_0_25": range_ok,
        "curves_cross": crossing is not None,
        "crossing_interior": interior,
    }
    primary = arm == "V1"
    if primary:
        # Criterion 4: the RT interval must exclude BOTH endpoints of the
        # sweep -- a crossing that can land anywhere on the axis is not a
        # boundary. The interval is over crossing locations (indices), so
        # "excludes both endpoints" means strictly inside the sweep.
        criteria["rt_reproducible"] = bool(
            rt_interval is not None
            and rt_interval[0] > 0
            and rt_interval[1] < len(curve) - 1)
        verdict = ("BOUNDARY" if all(criteria.values())
                   else "NO_BOUNDARY" if not criteria["curves_cross"]
                   else "INCONCLUSIVE")
    else:
        # A secondary arm cannot overrule the primary axis.
        verdict = ("SECONDARY_TREND" if criteria["di_monotone_increasing"]
                   and criteria["di_range_at_least_0_25"]
                   else "NO_TREND")

    return {"arm": arm, "n_seeds": len(by_label[order[0]]) if order else 0,
            "curve": curve, "criteria": criteria, "verdict": verdict,
            "unmeasurable_cells": unmeasurable,
            "crossing_label": curve[crossing]["label"] if crossing else None,
            "rt_bootstrap_interval": rt_interval,
            "rt_replicates_with_crossing": rt_replicates_with_crossing,
            "decision_interval": {
                "level": f"{100*(1-DECISION_ALPHA):.2f}%",
                "rule": "as stated in the frozen preregistration"}}


def _label_order(arm: str) -> list[str]:
    if arm == "V1":
        return [f"{lw}:{ew}" for (lw, ew) in SUPPORT_RATIOS]
    if arm == "V2":
        return [str(a) for a in ARRIVAL_TIMINGS]
    if arm == "V3":
        return [str(d) for d in NOVELTY_DENSITIES]
    if arm == "V4":
        return [str(c) for c in BELIEF_CAP_PRESSURES]
    if arm == "V5":
        return ["off", "on"]
    return []


# ----------------------------------------------------------------------
# The campaign runner
# ----------------------------------------------------------------------

def run_campaign(families: list[str], seeds: list[int], workers: int,
                 scale: int = 1, out_path: Path | None = None,
                 resume: bool = False, checkpoint_path: Path | None = None) -> dict:
    jobs = build_jobs(families, seeds, scale)
    started = time.time()
    records: list[dict] = []

    if checkpoint_path is None and out_path is not None:
        checkpoint_path = out_path.with_suffix(".ndjson")

    def checkpoint(rec):
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
        try:
            checkpoint_path.unlink()
        except OSError:
            pass

    if resume and out_path is not None and out_path.exists():
        try:
            prior = json.loads(out_path.read_text(encoding="utf-8"))
            records = prior.get("records", [])
        except Exception:
            records = []

    if records:
        done = {(r["arm"], r["label"], r["seed"]) for r in records}
        jobs = [j for j in jobs if (j["arm"], j["label"], j["seed"]) not in done]
        print(f"  resuming: {len(records)} cell(s) already done, {len(jobs)} to go",
              flush=True)

    def flush(complete: bool = False):
        if out_path is None:
            return
        payload = {
            "protocol": {
                "preregistration": PREREGISTRATION,
                "arms": families,
                "seeds": list(seeds),
                "workers": workers,
                "python_hash_seed": "0",
                "bootstrap_replicates": BOOTSTRAP_REPLICATES,
                "decision_alpha": DECISION_ALPHA,
                "cycle_scale": scale,
                "baseline_rule": ("every simple baseline is swept over the declared "
                                  "grid and its BEST score is used"),
                "wall_clock_seconds": round(time.time() - started, 1),
                "complete": complete,
            },
            "control": discrimination_control(),
            "ceiling_check": ceiling_check(),
            "summaries": {a: summarize_arm(records, a) for a in families
                          if any(r["arm"] == a for r in records)},
            "records": records,
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_path.with_suffix(out_path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp, out_path)

    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(run_cell, j): j for j in jobs}
            for fut in as_completed(futures):
                rec = fut.result()
                records.append(rec)
                checkpoint(rec)
                flush()
                r = rec["results"]["organica"]
                print(f"  {rec['arm']} {rec['label']} seed {rec['seed']}: "
                      f"DI={r['displacement_index']:.3f} PI={r['preservation_index']:.3f}",
                      flush=True)
    else:
        for job in jobs:
            rec = run_cell(job)
            records.append(rec)
            checkpoint(rec)
            flush()
            r = rec["results"]["organica"]
            print(f"  {rec['arm']} {rec['label']} seed {rec['seed']}: "
                  f"DI={r['displacement_index']:.3f} PI={r['preservation_index']:.3f}",
                  flush=True)

    summaries = {a: summarize_arm(records, a) for a in families
                 if any(r["arm"] == a for r in records)}
    flush(complete=True)
    return {"protocol": {"preregistration": PREREGISTRATION,
                         "arms": families, "seeds": list(seeds),
                         "workers": workers,
                         "wall_clock_seconds": round(time.time() - started, 1)},
            "summaries": summaries,
            "control": discrimination_control(),
            "ceiling_check": ceiling_check(),
            "records": records}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--families", nargs="+", default=["V1", "V2", "V3", "V4", "V5"])
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--scale", type=int, default=1)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true",
                    help="run the instrument audits only")
    ap.add_argument("--smoke", action="store_true",
                    help="a tiny run to confirm the harness executes (a pilot, "
                         "never a result)")
    args = ap.parse_args()

    if args.self_test:
        print("=" * 70)
        print("DISCRIMINATION CONTROL (the metric must separate the two poles)")
        print("=" * 70)
        ctrl = discrimination_control()
        print(json.dumps(ctrl, indent=2))
        print()
        print("=" * 70)
        print("ENDPOINT CEILING CHECK (a perfect model must score 1.0)")
        print("=" * 70)
        ceil = ceiling_check()
        print(json.dumps(ceil, indent=2))
        print()
        print("=" * 70)
        print("DEGENERACY AUDIT (the design must be live)")
        print("=" * 70)
        degen = degeneracy_audit(scale=args.scale)
        print(json.dumps({k: v for k, v in degen.items() if k != "cells"},
                         indent=2))
        print()
        if not ctrl["passed"] or not ceil["passed"] or not degen["passed"]:
            print("INSTRUMENT AUDIT FAILED. The campaign does not run.")
            for p in ctrl["problems"] + ceil["problems"] + degen["problems"]:
                print(f"  - {p}")
            return 1
        print("all endpoints are reachable, the metric discriminates, and the "
              "design is live.")
        return 0

    seeds = list(SEEDS[:args.seeds])
    if args.smoke:
        seeds = seeds[:1]
        args.scale = 4
        print("SMOKE RUN -- a pilot to confirm the harness executes. "
              "This is NOT evidence and is never a result.")

    out = args.out or (REPO / "docs" / "phase_l_results.json")

    print("=" * 70)
    print("Phase L -- Plasticity-Coherence Measurement")
    print("=" * 70)
    ctrl = discrimination_control()
    ceil = ceiling_check()
    degen = degeneracy_audit(scale=args.scale)
    if not ctrl["passed"] or not ceil["passed"] or not degen["passed"]:
        print("INSTRUMENT AUDIT FAILED. The campaign does not run.")
        for p in ctrl["problems"] + ceil["problems"] + degen["problems"]:
            print(f"  - {p}")
        return 1
    print("  discrimination control: passed")
    print("  endpoint ceiling check: passed")
    print("  degeneracy audit: passed")
    print()

    result = run_campaign(args.families, seeds, args.workers, args.scale,
                           out, args.resume)

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for arm, s in result["summaries"].items():
        print(f"  {arm}: {s['verdict']}")
        for c in s["curve"]:
            print(f"      {c['label']:>8s}  DI={c['displacement_index_mean']:.3f}"
                  f"  PI={c['preservation_index_mean']:.3f}")
        if s.get("crossing_label"):
            print(f"      Revision Threshold at {s['crossing_label']}")
    print()
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
