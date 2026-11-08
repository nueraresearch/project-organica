"""A scale-stream world that withholds a declared transition set by construction.

Why this file exists
--------------------
Option A's endpoint, `held_out_next_tag`, scores ordered tag transitions the formation
window never exhibited. On the unmodified scale-stream family that set is empty
(`docs/stage_b_endpoint_scale.json`), so the endpoint had no denominator. Withholding
cannot be a scoring rule there; it has to be a rule of the world.

This module imposes it. One declared directed **entity** transition -- `early_0 ->
late_0` by default -- is refused during generation by conditioned sampling: when the
world draws `late_0` as the successor of `early_0`, it resamples from the other active
entities instead. No event is skipped and no adjacency is manufactured, the discipline
the compositional family's `WITHHELD` limb already uses.

The scored set follows by construction: every ordered tag pair `(u, v)` with `u` in
`early_0`'s features and `v` in `late_0`'s features is absent from formation and present
in the behavioural window. The audit checks exactly that rather than assuming it.

Nothing here touches `organica/`. The engine is not imported and no world runs.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path

from benchmarks.acquisition_compositional import score
from benchmarks.phase_l_campaign import (
    ARRIVAL_FRACTION, EVENTS_PER_CYCLE, NOISE_FEATURES, NOISE_RATE, Entity,
    _core_entities,
)
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "stage_b_stream_withholding.json"

CONFIG_RATIOS: dict[str, tuple[int, int]] = {"2:1": (2, 1), "3:1": (3, 1),
                                            "4:1": (4, 1), "6:1": (6, 1)}
CONFIRMATION_CYCLE: dict[str, int] = {"2:1": 539, "3:1": 404, "4:1": 362, "6:1": 329}
DESIGN_SEEDS = (20261023, 20261024, 20261025)
WITHHOLD = ("early_0", "late_0")
LEARN_CYCLES = 50
TEST_CYCLES = 50
REPS = 600
EFFECT_GAP = 0.05
EPS = 1e-12
PRNG = 20261106


def entity_sets() -> list[Entity]:
    feats = _core_entities(6)
    out = [Entity(f"early_{i}", feats[i], 0) for i in range(3)]
    out += [Entity(f"late_{i}", feats[3 + i], 0) for i in range(3)]
    return out


def withheld_tag_pairs() -> set[tuple[str, str]]:
    ents = {e.name: e for e in entity_sets()}
    src, dst = ents[WITHHOLD[0]].features, ents[WITHHOLD[1]].features
    return {(u, v) for u in src for v in dst if u != v}


def build_world(seed: int, support_ratio: tuple[int, int] = (2, 1),
                cycles: int = 200, withhold: bool = True,
                withhold_until: int | None = None) -> dict:
    """A scale-stream world with one directed entity transition refused.

    `withhold_until` bounds the conditioning in cycles: the transition is refused
    while the organism is exposed (formation and learning) and permitted afterwards,
    so the behavioural test window contains the withheld transition and can be scored.
    Refusing it for the whole run empties the scored set -- which the audit caught.
    """
    late_w, early_w = support_ratio
    arrival = max(1, int(round(cycles * ARRIVAL_FRACTION)))
    feats = _core_entities(6)
    entities = [Entity(f"early_{i}", feats[i], 0, weight=early_w) for i in range(3)]
    entities += [Entity(f"late_{i}", feats[3 + i], arrival, weight=late_w)
                 for i in range(3)]
    rng = random.Random(seed)
    events: list[str] = []
    compensations = 0
    previous: str | None = None
    for cycle in range(cycles):
        active = [e for e in entities if e.start <= cycle]
        weights = [e.weight for e in active]
        for _ in range(EVENTS_PER_CYCLE):
            if rng.random() < NOISE_RATE:
                events.append(" ".join(rng.sample(NOISE_FEATURES, 2)))
                previous = None
                continue
            choice = rng.choices(active, weights=weights, k=1)[0]
            conditioned = withhold and (withhold_until is None or cycle < withhold_until)
            if conditioned and previous == WITHHOLD[0] and choice.name == WITHHOLD[1]:
                compensation = [e for e in active if e.name != WITHHOLD[1]]
                if compensation:
                    compensations += 1
                    choice = rng.choices(compensation,
                                         weights=[e.weight for e in compensation],
                                         k=1)[0]
            events.append(" ".join(rng.sample(choice.features, 2)))
            previous = choice.name
    return {"events": events, "cycles": cycles, "events_per_cycle": EVENTS_PER_CYCLE,
            "compensations": compensations, "entities": entities}


def occurrence_count(events: list[str], pairs: set[tuple[str, str]]) -> int:
    n = 0
    for i in range(len(events) - 1):
        for u in set(events[i].split()):
            for v in set(events[i + 1].split()):
                if (u, v) in pairs:
                    n += 1
    return n


def window(world: dict, lo: int, hi: int) -> list[str]:
    epc = world["events_per_cycle"]
    return world["events"][lo * epc:hi * epc]


def audit(cycles: int | None = None) -> dict:
    pairs = withheld_tag_pairs()
    confirmation = CONFIRMATION_CYCLE["2:1"]
    until = confirmation + LEARN_CYCLES
    floor = until + TEST_CYCLES + 1
    cycles = floor if cycles is None else max(cycles, floor)
    world = build_world(DESIGN_SEEDS[0], (2, 1), cycles, withhold=True,
                        withhold_until=until)
    open_world = build_world(DESIGN_SEEDS[0], (2, 1), cycles, withhold=False)
    formation = window(world, 0, confirmation)
    behavioural = window(world, confirmation + LEARN_CYCLES,
                         confirmation + LEARN_CYCLES + TEST_CYCLES)
    shares = {}
    for label, ratio in CONFIG_RATIOS.items():
        w = build_world(DESIGN_SEEDS[0], ratio, cycles, withhold_until=until)
        late_tags = set()
        for e in w["entities"]:
            if e.name.startswith("late_"):
                late_tags |= set(e.features)
        shares[label] = round(sum(1 for ev in w["events"] if late_tags & set(ev.split()))
                              / max(1, len(w["events"])), 4)
    checks = {
        "withheld_pairs_declared": len(pairs),
        "withheld_pairs_in_formation_of_the_withholding_world": occurrence_count(formation, pairs),
        "withheld_pairs_in_behavioural_window": occurrence_count(behavioural, pairs),
        "withheld_pairs_in_the_open_world_formation": occurrence_count(
            window(open_world, 0, confirmation), pairs),
        "compensations": world["compensations"],
        "late_share_by_configuration": shares,
        "late_share_spread": round(max(shares.values()) - min(shares.values()), 4),
    }
    checks["the_intervention_fired"] = checks["compensations"] > 0
    checks["formation_is_disjoint_from_the_scored_set"] = \
        checks["withheld_pairs_in_formation_of_the_withholding_world"] == 0
    checks["the_scored_set_is_reachable"] = checks["withheld_pairs_in_behavioural_window"] > 0
    checks["the_open_world_does_show_them"] = \
        checks["withheld_pairs_in_the_open_world_formation"] > 0
    checks["the_axis_is_live"] = checks["late_share_spread"] > 0.01
    checks["passed"] = all(checks[k] for k in
                           ("the_intervention_fired", "formation_is_disjoint_from_the_scored_set",
                            "the_scored_set_is_reachable", "the_open_world_does_show_them",
                            "the_axis_is_live"))
    return checks


def empirical_law(world: dict) -> dict[tuple[str, str], float]:
    counts: dict[str, int] = {}
    pair_counts: dict[tuple[str, str], int] = {}
    for i in range(len(world["events"]) - 1):
        sources = set(world["events"][i].split())
        targets = set(world["events"][i + 1].split())
        for u in sources:
            counts[u] = counts.get(u, 0) + 1
            for v in targets:
                if u != v:
                    pair_counts[(u, v)] = pair_counts.get((u, v), 0) + 1
    vocab = {t for ev in world["events"] for t in ev.split()}
    return {(u, v): (c + 0.5) / (counts[u] + 0.5 * len(vocab))
            for (u, v), c in pair_counts.items()}


def prob_from(law: dict[tuple[str, str], float], floor: float = 0.001):
    def prob(u: str, v: str) -> float:
        return max(floor, law.get((u, v), floor))
    return prob


def losses(prob, ctx, obs, vocabulary) -> list[tuple[float, int]]:
    out = []
    for context, observation in zip(ctx, obs):
        truth = set(observation) & vocabulary
        ll, cells = 0.0, 0
        for source in context:
            for target in vocabulary:
                p = min(1 - EPS, max(EPS, prob(source, target)))
                y = int(target in truth and target != source)
                ll -= y * math.log(p) + (1 - y) * math.log1p(-p)
                cells += 1
        out.append((ll, cells))
    return out


def bootstrap(per, reps, rng):
    means, total = [], len(per)
    for _ in range(reps):
        num, den = 0.0, 0
        for _ in range(total):
            ll, cells = per[rng.randrange(total)]
            num += ll
            den += cells
        means.append(num / den)
    return statistics.fmean(means), statistics.stdev(means)


def probe(label: str, seed: int, reps: int) -> dict:
    late, early = CONFIG_RATIOS[label]
    confirmation = CONFIRMATION_CYCLE[label]
    cycles = confirmation + LEARN_CYCLES + TEST_CYCLES + 1
    until = confirmation + LEARN_CYCLES
    world = build_world(seed, (late, early), cycles, withhold=True, withhold_until=until)
    pairs = withheld_tag_pairs()
    formation = window(world, 0, confirmation)
    epc = world["events_per_cycle"]
    events = world["events"]
    lo = (confirmation + LEARN_CYCLES) * epc
    hi = lo + TEST_CYCLES * epc
    ctx, obs = [], []
    for i in range(lo, hi - 1):
        sources = sorted(set(events[i].split()))
        targets = sorted(set(events[i + 1].split()))
        if any((u, v) in pairs for u in sources for v in targets if u != v):
            ctx.append(sources)
            obs.append(targets)
    base = {"configuration": label, "design_block_cell": seed,
            "withheld_pairs": len(pairs),
            "withheld_occurrences_in_formation": occurrence_count(formation, pairs),
            "withheld_occurrences_in_test": occurrence_count(
                window(world, confirmation + LEARN_CYCLES,
                       confirmation + LEARN_CYCLES + TEST_CYCLES), pairs),
            "scored_positions": len(ctx)}
    if not ctx:
        return dict(base, measurable=False)
    vocabulary = {t for ev in events for t in ev.split()}
    open_law = empirical_law(build_world(seed + 1, (late, early), 400, withhold=False))
    uniform = {key: 1.0 / (2.0 * len(vocabulary)) for key in open_law}
    rows = {}
    for name, law in (("ceiling_open_law", open_law), ("wrong_law_uniform", uniform)):
        prob = prob_from(law)
        per = losses(prob, ctx, obs, vocabulary)
        total = sum(ll for ll, _ in per) / sum(n for _, n in per)
        house = score(prob, ctx, obs, vocabulary)["log_loss"]
        assert abs(total - house) < 1e-6
        rng = random.Random(PRNG + seed + len(name))
        _, se = bootstrap(per, reps, rng)
        rows[name] = {"score_nats": round(total, 6), "cluster_se": round(se, 6),
                      "twice_cluster_se": round(2 * se, 6),
                      "clears_the_assumed_gap": bool(2 * se < EFFECT_GAP)}
    return dict(base, measurable=True, readouts=rows)


def build(reps: int = REPS) -> dict:
    checks = audit()
    if not checks["passed"]:
        print(json.dumps(checks, indent=1))
        raise SystemExit("the withholding audit failed; no probe is meaningful")
    cells = [probe(label, seed, reps) for label in CONFIG_RATIOS for seed in DESIGN_SEEDS]
    measurable = [c for c in cells if c.get("measurable")]
    by_config = {}
    for label in CONFIG_RATIOS:
        rows = [c["readouts"] for c in measurable if c["configuration"] == label]
        if rows:
            by_config[label] = {
                "ceiling_twice_se_min": min(r["ceiling_open_law"]["twice_cluster_se"] for r in rows),
                "ceiling_twice_se_max": max(r["ceiling_open_law"]["twice_cluster_se"] for r in rows),
                "wrong_law_twice_se_min": min(r["wrong_law_uniform"]["twice_cluster_se"] for r in rows),
                "wrong_law_twice_se_max": max(r["wrong_law_uniform"]["twice_cluster_se"] for r in rows),
                "clears_the_assumed_gap": all(r["ceiling_open_law"]["clears_the_assumed_gap"]
                                              for r in rows),
            }
    return {
        "what_this_is": "A scale-stream world that withholds the declared entity transition "
                        "early_0 -> late_0 by conditioned sampling, the audit proving the "
                        "withholding fired and the scored set is reachable, and the per-world "
                        "standard error of `held_out_next_tag` on design-block cells.",
        "why_it_exists": "protocol 3.2: on the unmodified stream formation saturates the "
                         "ordered-pair space, so an absence-based withheld set is empty and the "
                         "endpoint has no denominator. Withholding has to be imposed by the world.",
        "declared_withheld_transition": {"from": WITHHOLD[0], "to": WITHHOLD[1]},
        "method": "when the generator draws the withheld successor after the withheld source it "
                  "resamples from the other active entities by weight; no event is skipped and "
                  "no adjacency is manufactured",
        "audit": checks,
        "replicates": reps,
        "effect_gap_assumed": EFFECT_GAP,
        "design_block_cells": list(DESIGN_SEEDS),
        "cells_are": "consumed Phase L seeds, regenerated deterministically; no seed is spent "
                     "and none is re-allocated",
        "confirmation_cycles_are": "the protocol 2 medians, used only to position the "
                                   "behavioural window; no onset is measured here",
        "configurations": by_config,
        "cells": cells,
        "limits": [
            "the readouts are empirical laws estimated from an auxiliary stream, not the "
            "engine's readout; they bracket prediction quality rather than measure a learner",
            "one declared entity transition is withheld; whether that is the right size or pair "
            "is a pre-run enumeration question and is not settled here",
            "three design-block seeds per configuration measure the estimator; they do not "
            "authorise the run and they are not the confirmatory block",
            "the wrong-law control is a uniform law, and a constant predictor's per-position loss "
            "has zero variance, so its per-world standard error is exactly 0.0 and the control "
            "brackets nothing: it shows the ceiling is not the worst possible readout, not how "
            "wrong a wrong law would score",
            "this world is a reconstruction of the scale family (six entities in two groups, the "
            "same arrival fraction, noise rate and twelve events a cycle) and not "
            "`phase_l_campaign.build_world`, and no `DI` onset has been measured on it: the "
            "predictor side of the protocol is untested in the world that now carries the outcome",
            "the confirmation cycles are the protocol's medians, so the window position is "
            "plausible rather than observed",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=REPS)
    args = ap.parse_args()
    result = build(args.reps)
    OUT.write_text(json.dumps(engine_stamp.stamp(result), indent=2), encoding="utf-8")
    a = result["audit"]
    print("audit:", {k: a[k] for k in ("passed", "withheld_pairs_declared",
                                       "withheld_pairs_in_formation_of_the_withholding_world",
                                       "withheld_pairs_in_behavioural_window",
                                       "compensations", "late_share_spread")})
    for label, row in result["configurations"].items():
        print(f"{label}: ceiling 2SE {row['ceiling_twice_se_min']}-{row['ceiling_twice_se_max']} "
              f"| open law {row['wrong_law_twice_se_min']}-{row['wrong_law_twice_se_max']} "
              f"| clears gap: {row['clears_the_assumed_gap']}")
    print("measurable cells:", sum(1 for c in result["cells"] if c.get("measurable")),
          "of", len(result["cells"]))


if __name__ == "__main__":
    main()
