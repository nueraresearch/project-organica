"""NEVER-SERVED-ASSERTION-MODEL-REPLICATION-1.

Replication of the frozen never-served assertion model on the fresh provenance
block (seeds 20613101-20613106).  The original Q4 model was

    logit P(asserted) = b0 + b_loop*loop + b_rank*z(log2(min_rank))
                        + b_count*z(direct_count) + seed fixed effects

fitted by Firth penalized likelihood because the no-loop cell was empty.  This
module applies the same population, predictors, standardization, estimator and
seed fixed effects to the six seeds that were already used for the provenance
replication.  They are fresh relative to Q4, but they are not a new independent
draw; that limit is stated in the preregistration and the result.

The replay uses the repaired observer: the served window is the engine's own
cap-40 list, and a second observational call records the full pre-cap universe.
`min_rank` is the minimum 1-based position of the edge in that universe over all
120 cycles.  `ever_loop` is any reported `loop_candidate` path containing the
edge in either orientation.  The direct count is the final temporal count.

    python -m benchmarks.never_served_assertion_model_replication --freeze
    python -m benchmarks.never_served_assertion_model_replication --write
    python -m benchmarks.never_served_assertion_model_replication --identity
    python -m benchmarks.never_served_assertion_model_replication --check
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                      # noqa: E402
from benchmarks.acquisition_compositional import generate_compositional_world  # noqa: E402
from benchmarks.acquisition_harness import (                              # noqa: E402
    _CountingMemoryService,
    _make_scratch_db,
    _world_compositional_edges,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges  # noqa: E402
from benchmarks.never_served_assertion_model import (                     # noqa: E402
    _auc,
    _fit,
    _fit_firth,
    _p_value,
    _separation,
    _sigmoid,
)
from benchmarks.presence_construct_audit import (                         # noqa: E402
    ACQ_SOURCE,
    PHASE_ACQUISITION,
)
from benchmarks.presence_conversion_repair_observer import (              # noqa: E402
    RepairedObserverSleepService,
)

ID = "NEVER-SERVED-ASSERTION-MODEL-REPLICATION-1"
FROZEN_ON = "2026-11-12"
SEEDS = [20613101, 20613102, 20613103, 20613104, 20613105, 20613106]
CYCLES = 120
CAP = 40
PREREG = ROOT / "docs" / "never_served_assertion_model_replication_prereg.json"
ARTIFACT = ROOT / "docs" / "never_served_assertion_model_replication.json"
PAGE = ROOT / "docs" / "NEVER-SERVED-ASSERTION-MODEL-REPLICATION.md"
ORIGINAL = ROOT / "docs" / "never_served_assertion_model.json"
PROV_RESULT = ROOT / "docs" / "assertion_provenance_replication.json"
PROV_PREREG = ROOT / "docs" / "assertion_provenance_replication_prereg.json"
REGISTRY = ROOT / "docs" / "research_question_registry.json"
COLLISION_ALLOW = (PREREG, ARTIFACT, PROV_PREREG, PROV_RESULT, REGISTRY)
PREDICTORS = ("loop", "rank_log2_z", "count_z")
VERDICTS = ("REPLICATED", "DIRECTIONAL ONLY", "NOT REPLICATED", "VOID")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fit_coef(fitted: dict, name: str) -> dict:
    return next(row for row in fitted["coefs"] if row["name"] == name)


def build_prereg() -> dict:
    return {
        "prereg": ID,
        "kind": "never_served_assertion_model_replication_prereg",
        "status": "FROZEN, NOT FIT",
        "frozen_on": FROZEN_ON,
        "question": (
            "Does the frozen never-served assertion model reproduce on the fresh "
            "provenance block: does loop formation dominate, and are the rank and "
            "count associations in the same direction, with seed held fixed?"
        ),
        "reference": {
            "source": "docs/never_served_assertion_model.json",
            "n_complete": 179,
            "n_events": 26,
            "loop_or": 75.10,
            "loop_ci95": [6.66, 847.08],
            "rank_or": 1.09,
            "rank_ci95": [0.61, 1.95],
            "count_or": 1.96,
            "count_ci95": [0.87, 4.40],
            "separation": {
                "loop_1_asserted": 26,
                "loop_1_not": 35,
                "loop_0_asserted": 0,
                "loop_0_not": 118,
            },
        },
        "design": {
            "seeds": SEEDS,
            "cells": len(SEEDS),
            "cycles": CYCLES,
            "cap": CAP,
            "world": (
                "generate_compositional_world(seed=, cycles=120) with the "
                "PHASE_ACQUISITION schedule and one replay per seed"
            ),
            "population": "every world edge with zero direct served windows",
            "rank": (
                "minimum 1-based position in the repaired observer's full pre-cap "
                "universe across all 120 cycles; the served window remains the "
                "engine's own cap-40 list"
            ),
            "loop": (
                "ever_loop: at least one reported loop_candidate path contains the "
                "edge in either orientation in any cycle"
            ),
            "count": "final direct temporal transition count from service._load_temporal",
            "replay": (
                "One replay per seed. The repaired observer's second call records "
                "the full universe without changing the served list."
            ),
            "freshness_note": (
                "These six seeds already carry ASSERTION-PROVENANCE-REPLICATION-1. "
                "They are fresh relative to the Q4 model, but this is a replication "
                "on that existing fresh block, not a new independent seed draw."
            ),
        },
        "model": {
            "family": "binary logistic regression",
            "formula": (
                "logit P(asserted) = b0 + b_loop*loop + b_rank*z(log2(min_rank)) "
                "+ b_count*z(direct_count) + seed fixed effects"
            ),
            "estimator": (
                "Firth penalized likelihood (Jeffreys prior), fixed before the fit, "
                "because the original model had an empty no-loop asserted cell"
            ),
            "standardization": "complete-case mean and population SD",
            "convergence": "max absolute Newton step < 1e-8, at most 200 iterations",
        },
        "inference": {
            "primary": "Firth Wald 95% intervals for loop, rank and count",
            "odds_ratios": (
                "loop is 0/1; rank and count are per 1 SD. A rank OR below 1 means a "
                "worse rank is associated with lower assertion."
            ),
            "sensitivity": (
                "leave-one-seed-out refits with the same model; no cluster-robust SE "
                "claim is made."
            ),
            "alpha": 0.05,
            "multiplicity": "one model, three reported coefficients; unadjusted",
            "no_causal_claim": (
                "The model is descriptive; no coefficient is read as a causal effect."
            ),
        },
        "criteria": [
            {"id": "R1", "name": "loop direction", "test": "loop OR > 1"},
            {"id": "R2", "name": "loop interval", "test": "loop 95% CI lower bound > 1"},
            {"id": "R3", "name": "loop variation", "test": "both loop levels are present"},
            {"id": "R4", "name": "gates", "test": "all replication gates pass"},
        ],
        "verdicts": {
            "REPLICATED": "R1-R4 all pass.",
            "DIRECTIONAL ONLY": "R1, R3 and R4 pass, but the loop interval includes 1.",
            "NOT REPLICATED": "The loop OR is at or below 1, or the model does not reproduce.",
            "VOID": "A replication gate fails; no coefficient is read.",
        },
        "gates": {
            "M1_population": "at least one never-served edge and one event; no duplicate seed-edge rows",
            "M2_rank_coverage": "at least 95% of never-served edges have a finite minimum rank",
            "M3_provenance_replay": "per-seed asserted and never-served-asserted counts match the provenance replication",
            "M4_loop_variation": "both loop levels are present",
            "M5_convergence": "the Firth fit converges with finite coefficients and information",
            "M6_complete_predictors": "every fitted row has loop, rank and count; no silent row loss",
            "M7_seed_levels": "all six seeds contribute rows and the seed fixed effect is full rank",
        },
        "engine": {"version": "0.15.0", "cap": CAP, "cycles": CYCLES, "edit": "none"},
        "result": ARTIFACT.relative_to(ROOT).as_posix(),
        "not_evidence": (
            "A six-seed replication on one synthetic world family. The seeds were "
            "already used for the provenance split, so this is not a new independent "
            "draw. It does not establish causation, capability, retention or a general "
            "engine property."
        ),
    }


def _validate_prereg(body: dict) -> list[str]:
    found: list[str] = []
    if body.get("prereg") != ID:
        found.append("prereg id")
    if body.get("status") not in ("FROZEN, NOT FIT", "FROZEN, FIT"):
        found.append("prereg status")
    design = body.get("design") or {}
    if design.get("seeds") != SEEDS:
        found.append("seed block")
    if design.get("cells") != len(SEEDS):
        found.append("cell count")
    if design.get("cycles") != CYCLES or design.get("cap") != CAP:
        found.append("cycles or cap")
    reference = body.get("reference") or {}
    if reference.get("n_complete") != 179 or reference.get("n_events") != 26:
        found.append("reference population")
    if [row.get("id") for row in body.get("criteria") or []] != ["R1", "R2", "R3", "R4"]:
        found.append("criteria")
    if set(body.get("verdicts") or {}) != set(VERDICTS):
        found.append("verdict vocabulary")
    if body.get("result") != ARTIFACT.relative_to(ROOT).as_posix():
        found.append("result path")
    return found


def _run_seed(seed: int) -> dict:
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("never_served_assertion_replication")
    memory = _CountingMemoryService(str(db_path))
    service = RepairedObserverSleepService(memory, observe=True, cap=CAP)
    windows: list[list[tuple[str, str]]] = []
    loop_edges: set[tuple[str, str]] = set()
    loop_cycles: dict[tuple[str, str], list[int]] = defaultdict(list)
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                report = service.run_sleep_cycle()
                windows.append([(p.source, p.target) for p in report.predictions])
                cycle = len(windows)
                for loop in report.loops:
                    path = list(loop.path)
                    for a, b in zip(path, path[1:]):
                        for edge in ((a, b), (b, a)):
                            if edge in world_edges:
                                loop_edges.add(edge)
                                loop_cycles[edge].append(cycle)
        temporal = service._load_temporal()
        candidates = service._load_prior_candidates()
        asserted = {(a, b) for a, targets in structure_edges(candidates).items()
                    for b in targets}
        universe = [list(cycle) for cycle in service.universe]
    finally:
        memory.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    asserted_world = asserted & world_edges
    served = Counter(edge for window in windows for edge in window
                     if edge in world_edges)
    rank_obs: dict[tuple[str, str], list[tuple[int, int, int]]] = defaultdict(list)
    for cycle, rows in enumerate(universe, start=1):
        for row in rows:
            edge = tuple(row["edge"])
            if edge in world_edges:
                rank_obs[edge].append((int(row["rank"]), cycle, len(rows)))

    rows = []
    for edge in sorted(world_edges):
        if served.get(edge, 0):
            continue
        observations = rank_obs.get(edge) or []
        min_obs = min(observations, key=lambda item: (item[0], item[1])) if observations else None
        last_cycle = max(item[1] for item in observations) if observations else None
        final_rank = (min(item[0] for item in observations if item[1] == last_cycle)
                      if observations else None)
        rows.append({
            "seed": seed,
            "edge": "%s>%s" % edge,
            "asserted": edge in asserted_world,
            "ever_loop": edge in loop_edges,
            "loop_cycles": loop_cycles.get(edge, []),
            "direct_count": int(temporal.get(edge[0], {}).get(edge[1], 0)),
            "min_rank": min_obs[0] if min_obs else None,
            "min_rank_cycle": min_obs[1] if min_obs else None,
            "universe_at_min": min_obs[2] if min_obs else None,
            "cycles_ranked": len({item[1] for item in observations}),
            "median_rank": statistics.median([item[0] for item in observations])
                           if observations else None,
            "final_rank": final_rank,
        })
    return {
        "seed": seed,
        "world_edges": len(world_edges),
        "served_world_edges": len(served),
        "asserted_world_edges": len(asserted_world),
        "never_served": len(rows),
        "never_served_asserted": sum(row["asserted"] for row in rows),
        "rows": rows,
    }


def _fit_rows(rows: list[dict]) -> dict:
    data = []
    for row in rows:
        item = dict(row)
        item["loop"] = 1.0 if row["ever_loop"] else 0.0
        item["asserted_i"] = 1.0 if row["asserted"] else 0.0
        data.append(item)
    fitted = _fit(data, SEEDS)
    loo = []
    for seed in SEEDS:
        sub = [row for row in data if row["seed"] != seed]
        try:
            fold = _fit(sub, [s for s in SEEDS if s != seed])
            loo.append({
                "held_out": seed,
                "loop": fold["coefs"][1]["beta"],
                "rank": fold["coefs"][2]["beta"],
                "count": fold["coefs"][3]["beta"],
            })
        except Exception as exc:
            loo.append({"held_out": seed, "error": type(exc).__name__ + ": " + str(exc)})
    return {"data": data, "fitted": fitted, "loo": loo}


def _identity_adjustment(rows: list[dict]) -> dict:
    """Post-hoc count check with source and target identity fixed effects."""
    data = [row for row in rows if row["min_rank"] is not None]
    if not data:
        raise ValueError("no complete rows")
    rank_vals = [math.log2(float(row["min_rank"])) for row in data]
    count_vals = [float(row["direct_count"]) for row in data]
    rank_mean, rank_sd = statistics.fmean(rank_vals), statistics.pstdev(rank_vals)
    count_mean, count_sd = statistics.fmean(count_vals), statistics.pstdev(count_vals)
    seeds = sorted({row["seed"] for row in data})
    sources = sorted({row["edge"].split(">")[0] for row in data})
    targets = sorted({row["edge"].split(">")[1] for row in data})
    ref_seed, ref_source, ref_target = seeds[0], sources[0], targets[0]

    def vector(row, loop=None, rank_shift=0.0, count_shift=0.0):
        source, target = row["edge"].split(">")
        values = [
            1.0,
            (1.0 if row["ever_loop"] else 0.0) if loop is None else loop,
            (math.log2(float(row["min_rank"])) - rank_mean) / rank_sd + rank_shift,
            (float(row["direct_count"]) - count_mean) / count_sd + count_shift,
        ]
        values += [1.0 if row["seed"] == seed else 0.0 for seed in seeds[1:]]
        values += [1.0 if source == level else 0.0 for level in sources[1:]]
        values += [1.0 if target == level else 0.0 for level in targets[1:]]
        return values

    X = [vector(row) for row in data]
    y = [1.0 if row["asserted"] else 0.0 for row in data]
    fit = _fit_firth(X, y)
    names = (["intercept", "loop", "rank_log2_z", "count_z"]
             + ["seed_%d" % seed for seed in seeds[1:]]
             + ["source_%s" % level for level in sources[1:]]
             + ["target_%s" % level for level in targets[1:]])

    def coefficient(name: str) -> dict:
        index = names.index(name)
        beta, se = fit["beta"][index], fit["se"][index]
        z = beta / se if se else float("nan")
        return {
            "name": name,
            "beta": beta,
            "se": se,
            "z": z,
            "p": _p_value(z) if math.isfinite(z) else None,
            "odds_ratio": math.exp(beta),
            "ci95": [math.exp(beta - 1.959963984540054 * se),
                     math.exp(beta + 1.959963984540054 * se)],
        }

    def probability(row, loop=None, rank_shift=0.0, count_shift=0.0):
        values = vector(row, loop=loop, rank_shift=rank_shift,
                        count_shift=count_shift)
        return _sigmoid(sum(value * beta for value, beta in zip(values, fit["beta"])))

    ame_loop = statistics.fmean(probability(row, loop=1.0) - probability(row, loop=0.0)
                                for row in data)
    ame_rank = statistics.fmean(probability(row, rank_shift=1.0) - probability(row)
                                for row in data)
    ame_count = statistics.fmean(probability(row, count_shift=1.0) - probability(row)
                                 for row in data)
    return {
        "post_hoc": True,
        "preregistered": False,
        "question": (
            "Does the count association remain once source and target identity are "
            "held fixed by categorical fixed effects?"
        ),
        "n": len(data),
        "events": int(sum(y)),
        "parameters": len(X[0]),
        "source_levels": len(sources),
        "target_levels": len(targets),
        "source_event_levels": len({row["edge"].split(">")[0] for row in data
                                    if row["asserted"]}),
        "target_event_levels": len({row["edge"].split(">")[1] for row in data
                                    if row["asserted"]}),
        "reference": {"seed": ref_seed, "source": ref_source, "target": ref_target},
        "loop": coefficient("loop"),
        "rank": coefficient("rank_log2_z"),
        "count": coefficient("count_z"),
        "average_marginal_effects": {
            "loop": ame_loop,
            "rank_per_sd": ame_rank,
            "count_per_sd": ame_count,
        },
        "fit": {
            "converged": fit["converged"],
            "iterations": fit["iterations"],
            "max_se": max(fit["se"]),
            "auc_in_sample": _auc(y, fit["prob"]),
            "brier_in_sample": statistics.fmean((p - t) ** 2 for p, t in zip(fit["prob"], y)),
        },
        "reading": (
            "The count point estimate does not attenuate when source and target "
            "identity enter, but its interval still includes 1 and the identity model "
            "is saturated in sample. This is a robustness check on an association that "
            "was already null, not evidence of a count effect."
        ),
    }


def build() -> dict:
    prereg = _load(PREREG)
    problems = _validate_prereg(prereg)
    from benchmarks.presence_cap_experiment import seed_collisions
    collisions = seed_collisions(SEEDS, allow=COLLISION_ALLOW)
    if collisions:
        problems.append("seed collision: %r" % (collisions,))
    if problems:
        raise SystemExit("REFUSED: " + "; ".join(problems))

    traces = [_run_seed(seed) for seed in SEEDS]
    rows = [row for trace in traces for row in trace["rows"]]
    fitted = _fit_rows(rows)
    fit = fitted["fitted"]
    separation = _separation(rows)
    data = fit["data"]
    n_population = len(rows)
    n_complete = len(data)
    n_events = sum(1 for row in data if row["asserted"])
    provenance = _load(PROV_RESULT)
    prov = {int(item["seed"]): item for item in provenance["seeds"]}
    provenance_match = all(
        trace["asserted_world_edges"] == prov[trace["seed"]]["asserted_world_edges"]
        and trace["never_served_asserted"] == prov[trace["seed"]]["never_served_asserted"]
        for trace in traces
    )
    gates = {
        "M1_population": (
            n_population > 0 and n_events > 0
            and len({(row["seed"], row["edge"]) for row in rows}) == n_population
        ),
        "M2_rank_coverage": n_complete / n_population >= 0.95 if n_population else False,
        "M3_provenance_replay": provenance_match,
        "M4_loop_variation": len({row["loop"] for row in data}) == 2,
        "M5_convergence": bool(fit["fit"]["converged"]),
        "M6_complete_predictors": all(row["min_rank"] is not None for row in data),
        "M7_seed_levels": len({row["seed"] for row in data}) == len(SEEDS),
    }
    all_gates = all(gates.values())
    loop = _fit_coef(fit, "loop")
    rank = _fit_coef(fit, "rank_log2_z")
    count = _fit_coef(fit, "count_z")
    criteria = {
        "R1_loop_direction": loop["odds_ratio"] > 1.0,
        "R2_loop_interval": loop["ci95"][0] > 1.0,
        "R3_loop_variation": gates["M4_loop_variation"],
        "R4_gates": all_gates,
    }
    if not all_gates:
        verdict = "VOID"
    elif criteria["R1_loop_direction"] and criteria["R2_loop_interval"]:
        verdict = "REPLICATED"
    elif criteria["R1_loop_direction"]:
        verdict = "DIRECTIONAL ONLY"
    else:
        verdict = "NOT REPLICATED"
    summary = {
        "n_population": n_population,
        "n_complete": n_complete,
        "n_events": n_events,
        "loop": loop,
        "rank": rank,
        "count": count,
        "separation": separation,
        "average_marginal_effects": fit["ame"],
        "auc": fit["auc"] if math.isfinite(fit["auc"]) else None,
        "brier": fit["brier"],
        "gates": gates,
        "all_gates": all_gates,
        "criteria": criteria,
        "verdict": verdict,
        "provenance_match": provenance_match,
    }
    return engine_stamp.stamp({
        "kind": "never_served_assertion_model_replication",
        "status": "RUN",
        "prereg": PREREG.relative_to(ROOT).as_posix(),
        "question": prereg["question"],
        "scope": (
            "Six seeds already used for the provenance replication, one compositional "
            "world family, 120 cycles and cap 40. This is a replication on that "
            "existing fresh block, not a new independent seed draw."
        ),
        "design": prereg["design"],
        "reference": prereg["reference"],
        "model": prereg["model"],
        "inference": prereg["inference"],
        "criteria": prereg["criteria"],
        "gates": prereg["gates"],
        "seeds": [{key: value for key, value in trace.items() if key != "rows"}
                  for trace in traces],
        "rows": rows,
        "summary": summary,
        "identity_adjustment": _identity_adjustment(rows),
        "leave_one_seed_out": fitted["loo"],
        "not_evidence": prereg["not_evidence"],
    })


def _fmt(value, digits=3):
    return "NA" if value is None else ("%.*f" % (digits, value))


def render(art: dict) -> str:
    summary = art["summary"]
    ref = art["reference"]
    loop = summary["loop"]
    rank = summary["rank"]
    count = summary["count"]
    sep = summary["separation"]
    identity = art["identity_adjustment"]
    lines = [
        "# Never-served assertion model — replication",
        "",
        "Generated from `%s` by `python -m benchmarks.never_served_assertion_model_replication --write`. "
        "Do not edit by hand." % ARTIFACT.relative_to(ROOT),
        "",
        "**Verdict: `%s`.** The model and gates were frozen in `%s` before the replay."
        % (summary["verdict"], PREREG.relative_to(ROOT)),
        "",
        "## Design",
        "",
        "- Seeds: **%s** — the existing provenance block, fresh relative to Q4 but not a new draw."
        % ", ".join(str(seed) for seed in art["design"]["seeds"]),
        "- **%d** cycles, cap **%d**, PHASE_ACQUISITION schedule, one replay per seed."
        % (art["design"]["cycles"], art["design"]["cap"]),
        "- Population: every world edge with zero direct served windows.",
        "- `min_rank`: minimum 1-based position in the repaired observer's full pre-cap universe.",
        "- `ever_loop`: any reported loop path containing the edge in either orientation.",
        "- Direct count: final temporal transition count.",
        "",
        "## Result",
        "",
        "| Term | Original Q4 | Fresh block |",
        "| --- | ---: | ---: |",
        "| Population | %d complete / 180 | %d complete / %d |"
        % (ref["n_complete"], summary["n_complete"], summary["n_population"]),
        "| Events | %d | %d |" % (ref["n_events"], summary["n_events"]),
        "| Loop OR | %.2f | %.2f |" % (ref["loop_or"], loop["odds_ratio"]),
        "| Loop 95%% CI | %.2f–%.2f | %.2f–%.2f |"
        % (ref["loop_ci95"][0], ref["loop_ci95"][1], loop["ci95"][0], loop["ci95"][1]),
        "| Rank OR | %.2f | %.2f |" % (ref["rank_or"], rank["odds_ratio"]),
        "| Rank 95%% CI | %.2f–%.2f | %.2f–%.2f |"
        % (ref["rank_ci95"][0], ref["rank_ci95"][1], rank["ci95"][0], rank["ci95"][1]),
        "| Count OR | %.2f | %.2f |" % (ref["count_or"], count["odds_ratio"]),
        "| Count 95%% CI | %.2f–%.2f | %.2f–%.2f |"
        % (ref["count_ci95"][0], ref["count_ci95"][1], count["ci95"][0], count["ci95"][1]),
        "| AUC | 0.925 | %s |" % _fmt(summary["auc"]),
        "| Brier | 0.074 | %s |" % _fmt(summary["brier"], 4),
        "",
        "## Separation",
        "",
        "| | Asserted | Not asserted |",
        "| --- | ---: | ---: |",
        "| Loop formed | %d | %d |" % (sep["loop_1_asserted"], sep["loop_1_not"]),
        "| No loop | %d | %d |" % (sep["loop_0_asserted"], sep["loop_0_not"]),
        "",
        "## Post-hoc identity adjustment",
        "",
        "The preregistered model did not include source or target identity. This check adds "
        "categorical fixed effects for both tags to the same Firth specification, holding "
        "seed fixed as before. It is post hoc and does not change the verdict.",
        "",
        "| Term | Unadjusted | + source/target identity |",
        "| --- | ---: | ---: |",
        "| Loop OR | %.2f | %.2f |" % (loop["odds_ratio"], identity["loop"]["odds_ratio"]),
        "| Loop 95%% CI | %.2f–%.2f | %.2f–%.2f |"
        % (loop["ci95"][0], loop["ci95"][1], identity["loop"]["ci95"][0],
           identity["loop"]["ci95"][1]),
        "| Rank OR | %.2f | %.2f |" % (rank["odds_ratio"], identity["rank"]["odds_ratio"]),
        "| Rank 95%% CI | %.2f–%.2f | %.2f–%.2f |"
        % (rank["ci95"][0], rank["ci95"][1], identity["rank"]["ci95"][0],
           identity["rank"]["ci95"][1]),
        "| Count OR | %.2f | %.2f |" % (count["odds_ratio"], identity["count"]["odds_ratio"]),
        "| Count 95%% CI | %.2f–%.2f | %.2f–%.2f |"
        % (count["ci95"][0], count["ci95"][1], identity["count"]["ci95"][0],
           identity["count"]["ci95"][1]),
        "| In-sample AUC | %s | %s |"
        % (_fmt(summary["auc"]), _fmt(identity["fit"]["auc_in_sample"])),
        "| Brier | %s | %s |"
        % (_fmt(summary["brier"], 4), _fmt(identity["fit"]["brier_in_sample"], 4)),
        "",
        "The count point estimate moves from **%.2f** to **%.2f**, but its interval still "
        "includes 1. The count association was already unsupported, and identity adjustment "
        "does not create one. Loop attenuates from **%.2f** to **%.2f** but remains positive; "
        "rank remains null."
        % (count["odds_ratio"], identity["count"]["odds_ratio"], loop["odds_ratio"],
           identity["loop"]["odds_ratio"]),
        "",
        "The identity model has **%d** parameters (30 source/target indicators and 9 other "
        "terms) for **%d** rows and **%d** events. Its in-sample AUC of **%s** is overfit and "
        "is not a predictive comparison."
        % (identity["parameters"], identity["n"], identity["events"],
           _fmt(identity["fit"]["auc_in_sample"])),
        "",
        "## Gates",
        "",
        "| Gate | Passes |",
        "| --- | --- |",
    ]
    for name, passed in summary["gates"].items():
        lines.append("| `%s` | %s |" % (name, "yes" if passed else "no"))
    lines += [
        "",
        "## Average marginal effects",
        "",
        "| Contrast | Probability difference |",
        "| --- | ---: |",
        "| Loop 1 vs 0 | %+.3f |" % summary["average_marginal_effects"]["loop"],
        "| Rank +1 SD | %+.3f |" % summary["average_marginal_effects"]["rank_per_sd"],
        "| Count +1 SD | %+.3f |" % summary["average_marginal_effects"]["count_per_sd"],
        "",
        "## Leave-one-seed-out",
        "",
        "| Held out | Loop beta | Rank beta | Count beta |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in art["leave_one_seed_out"]:
        if "error" in row:
            lines.append("| %d | %s | — | — |" % (row["held_out"], row["error"]))
        else:
            lines.append("| %d | %.3f | %.3f | %.3f |"
                         % (row["held_out"], row["loop"], row["rank"], row["count"]))
    lines += [
        "",
        "## Per seed",
        "",
        "| Seed | Asserted world | Served world | Never served | Never-served asserted |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in art["seeds"]:
        lines.append("| %d | %d | %d | %d | %d |" % (
            row["seed"], row["asserted_world_edges"], row["served_world_edges"],
            row["never_served"], row["never_served_asserted"]))
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "The replay uses seeds that already carried the provenance replication, so it "
        "tests whether the model reproduces on that existing fresh block; it is not a "
        "new independent draw. The model is descriptive: the loop coefficient is "
        "quasi-separated if the no-loop asserted cell remains empty, and its interval "
        "is not a precise effect. No causal, capability, retention or engine-effect "
        "claim follows.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != "never_served_assertion_model_replication":
        found.append("artifact kind")
    if art.get("status") != "RUN":
        found.append("artifact status")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    prereg = _load(PREREG)
    found.extend(_validate_prereg(prereg))
    if art.get("prereg") != PREREG.relative_to(ROOT).as_posix():
        found.append("prereg path")
    if art.get("design", {}).get("seeds") != SEEDS:
        found.append("artifact seed block")
    rows = art.get("rows") or []
    if len({(row["seed"], row["edge"]) for row in rows}) != len(rows):
        found.append("duplicate rows")
    fitted = _fit_rows(rows)["fitted"]
    summary = art.get("summary") or {}
    if summary.get("n_population") != len(rows):
        found.append("summary population")
    if summary.get("n_complete") != len(fitted["data"]):
        found.append("summary complete")
    if summary.get("n_events") != sum(1 for row in fitted["data"] if row["asserted"]):
        found.append("summary events")
    for name in PREDICTORS:
        if summary.get("loop" if name == "loop" else "rank" if name == "rank_log2_z" else "count") != _fit_coef(fitted, name):
            found.append("summary %s" % name)
    if summary.get("separation") != _separation(rows):
        found.append("summary separation")
    if art.get("identity_adjustment") != _identity_adjustment(rows):
        found.append("identity adjustment")
    if summary.get("verdict") != ("VOID" if not summary.get("all_gates")
                                  else "REPLICATED" if (summary["loop"]["odds_ratio"] > 1
                                                         and summary["loop"]["ci95"][0] > 1)
                                  else "DIRECTIONAL ONLY" if summary["loop"]["odds_ratio"] > 1
                                  else "NOT REPLICATED"):
        found.append("summary verdict")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    from benchmarks.presence_cap_experiment import seed_collisions
    if seed_collisions(SEEDS, allow=COLLISION_ALLOW):
        found.append("seed collision")
    return found


def freeze() -> int:
    if PREREG.exists():
        print("REFUSED: prereg exists")
        return 2
    doc = engine_stamp.stamp(build_prereg())
    PREREG.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print("froze %s" % PREREG.relative_to(ROOT))
    return 0


def identity_update() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no replication artifact; run --write")
    body = _load(ARTIFACT)
    body["identity_adjustment"] = _identity_adjustment(body["rows"])
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    identity = body["identity_adjustment"]
    print("identity adjustment: count OR %.3f (%.3f-%.3f), loop OR %.3f (%.3f-%.3f)" % (
        identity["count"]["odds_ratio"], identity["count"]["ci95"][0],
        identity["count"]["ci95"][1], identity["loop"]["odds_ratio"],
        identity["loop"]["ci95"][0], identity["loop"]["ci95"][1]))
    return 0


def write() -> int:
    body = build()
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    prereg = _load(PREREG)
    prereg["status"] = "FROZEN, FIT"
    prereg["completed_on"] = FROZEN_ON
    prereg["verdict"] = body["summary"]["verdict"]
    PREREG.write_text(json.dumps(prereg, indent=1) + "\n", encoding="utf-8")
    summary = body["summary"]
    print("never-served model replication: %s %s" % (summary["verdict"], json.dumps({
        "n_complete": summary["n_complete"],
        "events": summary["n_events"],
        "loop_or": round(summary["loop"]["odds_ratio"], 3),
        "loop_ci": [round(v, 3) for v in summary["loop"]["ci95"]],
        "rank_or": round(summary["rank"]["odds_ratio"], 3),
        "rank_ci": [round(v, 3) for v in summary["rank"]["ci95"]],
        "count_or": round(summary["count"]["odds_ratio"], 3),
        "count_ci": [round(v, 3) for v in summary["count"]["ci95"]],
    })))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no replication artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    summary = art["summary"]
    print("never-served model replication: %s %s" % (summary["verdict"], json.dumps({
        "n_complete": summary["n_complete"],
        "events": summary["n_events"],
        "loop_or": round(summary["loop"]["odds_ratio"], 3),
        "loop_ci": [round(v, 3) for v in summary["loop"]["ci95"]],
    })))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--identity", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.freeze:
        return freeze()
    if args.identity:
        return identity_update()
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
