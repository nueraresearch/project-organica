"""POSTHOC-LOOP-PERSISTENCE-1.

A post-hoc extension of the confirmed loop-only assertion model.  The
confirmatory block found a count association among 177 never-served edges that
ever formed a loop.  This block asks whether that association survives two
measured loop properties:

    retention = observed loop span / cycles available after first loop detection
    strength  = maximum loop_candidate strength (within-loop min edge count)

It also asks whether retention survives the cycle at which the loop first
appeared, since retention is measured against the cycles available after that
point.  `formation` is the fraction of the 120-cycle run elapsed before first
detection.

The extension is not preregistered and carries no confirmatory verdict.  It
replays the same twelve seeds to recover carrier strength, which the
confirmatory trace cache did not retain.  No fresh seed is spent.

    python -m benchmarks.loop_persistence_assertion_model --collect
    python -m benchmarks.loop_persistence_assertion_model --write
    python -m benchmarks.loop_persistence_assertion_model --check
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
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
    _fit_firth,
    _p_value,
    _sigmoid,
)
from benchmarks.never_served_assertion_model_replication import (         # noqa: E402
    CAP,
    CYCLES,
)
from benchmarks.presence_construct_audit import (                         # noqa: E402
    ACQ_SOURCE,
    PHASE_ACQUISITION,
)
from benchmarks.presence_conversion_repair_observer import (              # noqa: E402
    RepairedObserverSleepService,
)

ID = "POSTHOC-LOOP-PERSISTENCE-1"
SEEDS = list(range(20616101, 20616113))
BASE = ROOT / "docs" / "loop_only_assertion_model.json"
ARTIFACT = ROOT / "docs" / "loop_persistence_assertion_model.json"
PAGE = ROOT / "docs" / "LOOP-PERSISTENCE-ASSERTION-MODEL.md"
CACHE = ROOT / ".scratch" / "loop_persistence_traces"
PERSISTENCE = ("rank", "count", "retention", "strength")
CONTROLLED = PERSISTENCE + ("formation",)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _base_rows() -> list[dict]:
    art = _load(BASE)
    if art.get("kind") != "loop_only_assertion_model":
        raise SystemExit("REFUSED: base artifact kind")
    rows = art.get("rows") or []
    if not rows:
        raise SystemExit("REFUSED: base artifact has no rows")
    return rows


def _round(value, digits=6):
    if value is None:
        return None
    return round(float(value), digits)


def _capture_seed(seed: int) -> dict:
    """Replay one seed and keep every loop's cycle and strength per edge."""
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("loop_persistence_assertion")
    memory = _CountingMemoryService(str(db_path))
    service = RepairedObserverSleepService(memory, observe=True, cap=CAP)
    cycles: dict[tuple[str, str], list[int]] = defaultdict(list)
    strengths: dict[tuple[str, str], list[float]] = defaultdict(list)
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
                cycle = report.cycle
                for loop in report.loops:
                    path = list(loop.path)
                    for a, b in zip(path, path[1:]):
                        for edge in ((a, b), (b, a)):
                            if edge in world_edges:
                                cycles[edge].append(cycle)
                                strengths[edge].append(float(loop.strength))
        candidates = service._load_prior_candidates()
        asserted = {(a, b) for a, targets in structure_edges(candidates).items()
                    for b in targets}
    finally:
        memory.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    loops = {}
    for edge in sorted(cycles):
        observed = sorted(set(cycles[edge]))
        first, last = observed[0], observed[-1]
        span = last - first + 1
        loops["%s>%s" % edge] = {
            "loop_cycles": sorted(cycles[edge]),
            "strengths": strengths[edge],
            "retention_cycles": span,
            "retention": span / float(CYCLES - first + 1),
            "strength": max(strengths[edge]),
            "strength_observations": len(strengths[edge]),
            "formation_cycle": first,
            "formation_fraction": first / float(CYCLES),
        }
    asserted_world = asserted & world_edges
    return {
        "seed": seed,
        "asserted_world_edges": len(asserted_world),
        "asserted_edges": sorted("%s>%s" % edge for edge in asserted_world),
        "loops": loops,
    }


def collect() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    base = _base_rows()
    by_seed: dict[int, list[dict]] = defaultdict(list)
    for row in base:
        by_seed[row["seed"]].append(row)
    for seed in SEEDS:
        captured = _capture_seed(seed)
        expected = {row["edge"]: row for row in by_seed[seed]}
        if not set(expected) <= set(captured["loops"]):
            raise SystemExit("REFUSED: seed %d loop edge set changed" % seed)
        captured["asserted_edges"] = sorted(
            set(captured["asserted_edges"]) & set(expected))
        if set(captured["asserted_edges"]) != {
                row["edge"] for row in by_seed[seed] if row["asserted"]}:
            raise SystemExit("REFUSED: seed %d assertion labels changed" % seed)
        captured["loops"] = {edge: captured["loops"][edge] for edge in expected}
        for edge, item in captured["loops"].items():
            if sorted(item["loop_cycles"]) != sorted(expected[edge]["loop_cycles"]):
                raise SystemExit("REFUSED: seed %d loop cycles changed for %s"
                                 % (seed, edge))
        path = CACHE / ("%d.json" % seed)
        path.write_text(json.dumps(captured, indent=1) + "\n", encoding="utf-8")
        print("collected %d: %d loop edges, asserted %d"
              % (seed, len(expected), captured["asserted_world_edges"]))
    return 0


def _load_captures() -> dict[int, dict]:
    missing = [seed for seed in SEEDS if not (CACHE / ("%d.json" % seed)).exists()]
    if missing:
        raise SystemExit("missing loop captures: %r; run --collect" % missing)
    return {seed: _load(CACHE / ("%d.json" % seed)) for seed in SEEDS}


def _augment(rows: list[dict], captures: dict[int, dict]) -> list[dict]:
    out = []
    for row in rows:
        item = dict(row)
        loop = captures[row["seed"]]["loops"].get(row["edge"])
        if loop is None:
            raise SystemExit("REFUSED: no loop capture for %s %s"
                             % (row["seed"], row["edge"]))
        formation = min(loop["loop_cycles"])
        item.update({
            "retention": loop["retention"],
            "retention_cycles": loop["retention_cycles"],
            "strength": loop["strength"],
            "strength_observations": loop["strength_observations"],
            "formation_cycle": formation,
            "formation_fraction": formation / float(CYCLES),
        })
        out.append(item)
    return out


def _pearson(x: list[float], y: list[float]) -> float:
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sx = math.sqrt(sum((v - mx) ** 2 for v in x))
    sy = math.sqrt(sum((v - my) ** 2 for v in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def _fit_model(rows: list[dict], predictors: tuple[str, ...],
               use_seeds: list[int] | None = None, with_loo: bool = True) -> dict:
    use_seeds = list(SEEDS) if use_seeds is None else list(use_seeds)
    data = [row for row in rows
            if row["seed"] in use_seeds and row.get("min_rank") is not None]
    if not data:
        raise ValueError("empty fit population")
    raw = {
        "rank": [math.log2(float(row["min_rank"])) for row in data],
        "count": [float(row["direct_count"]) for row in data],
        "retention": [float(row["retention"]) for row in data],
        "strength": [float(row["strength"]) for row in data],
        "formation": [float(row["formation_fraction"]) for row in data],
    }
    stats = {}
    for name in predictors:
        mean = statistics.fmean(raw[name])
        sd = statistics.pstdev(raw[name])
        if sd == 0:
            raise ValueError("constant predictor: " + name)
        stats[name] = (mean, sd)
    levels = use_seeds[1:]
    X = []
    for i, row in enumerate(data):
        values = [1.0]
        for name in predictors:
            mean, sd = stats[name]
            values.append((raw[name][i] - mean) / sd)
        values += [1.0 if row["seed"] == seed else 0.0 for seed in levels]
        X.append(values)
    y = [1.0 if row["asserted"] else 0.0 for row in data]
    fit = _fit_firth(X, y)
    names = ["intercept"] + list(predictors) + ["seed_%d" % seed for seed in levels]
    coefs = []
    for name, beta, se in zip(names, fit["beta"], fit["se"]):
        z = beta / se if se else float("nan")
        coefs.append({
            "name": name,
            "beta": beta,
            "se": se,
            "z": z,
            "p": _p_value(z) if math.isfinite(z) else None,
            "odds_ratio": math.exp(beta),
            "ci95": [math.exp(beta - 1.959963984540054 * se),
                     math.exp(beta + 1.959963984540054 * se)],
        })
    by_name = {row["name"]: row for row in coefs}
    positions = {id(row): i for i, row in enumerate(data)}

    def predict(row, shifts=None):
        shifts = shifts or {}
        values = [1.0]
        i = positions[id(row)]
        for name in predictors:
            mean, sd = stats[name]
            values.append((raw[name][i] - mean) / sd + shifts.get(name, 0.0))
        values += [1.0 if row["seed"] == seed else 0.0 for seed in levels]
        return _sigmoid(sum(value * beta for value, beta in zip(values, fit["beta"])))

    ame = {}
    for name in predictors:
        ame[name] = statistics.fmean(
            predict(row, {name: 1.0}) - predict(row) for row in data)
    loo = []
    if with_loo:
        for seed in SEEDS:
            sub = [row for row in rows if row["seed"] != seed]
            try:
                fold = _fit_model(sub, predictors,
                                  [s for s in SEEDS if s != seed], with_loo=False)
                entry = {"held_out": seed}
                for name in predictors:
                    entry[name] = fold[name]["beta"]
                loo.append(entry)
            except Exception as exc:
                loo.append({"held_out": seed,
                            "error": type(exc).__name__ + ": " + str(exc)})
    return {
        "data": data,
        "n": len(data),
        "events": int(sum(y)),
        "coefficients": coefs,
        "stats": stats,
        "auc": _auc(y, fit["prob"]),
        "brier": statistics.fmean((p - t) ** 2 for p, t in zip(fit["prob"], y)),
        "ame": ame,
        "loo": loo,
        "converged": bool(fit["converged"]),
        "beta": fit["beta"],
        "means": {name: stats[name][0] for name in predictors},
        "sds": {name: stats[name][1] for name in predictors},
        "levels": levels,
        **{name: by_name[name] for name in predictors},
    }


def _summary_model(model: dict, predictors: tuple[str, ...]) -> dict:
    return {
        "n": model["n"],
        "events": model["events"],
        "converged": model["converged"],
        "coefficients": {name: model[name] for name in predictors},
        "auc": model["auc"] if math.isfinite(model["auc"]) else None,
        "brier": model["brier"],
        "auc_scope": "in-sample",
        "average_marginal_effects": model["ame"],
    }


def _integrity(rows: list[dict], captures: dict[int, dict],
               base: dict, baseline: dict, extended: dict,
               controlled: dict) -> dict:
    base_rows = base.get("rows") or []
    checks = {
        "population_unchanged": len(rows) == len(base_rows),
        "events_unchanged": sum(1 for row in rows if row["asserted"])
                            == sum(1 for row in base_rows if row["asserted"]),
        "replay_edges_match": all(
            set(captures[seed]["loops"])
            == {row["edge"] for row in base_rows if row["seed"] == seed}
            for seed in SEEDS),
        "replay_assertions_match": all(
            set(captures[seed]["asserted_edges"])
            == {row["edge"] for row in base_rows
                if row["seed"] == seed and row["asserted"]}
            for seed in SEEDS),
        "retention_finite": all(
            math.isfinite(float(row["retention"])) and 0 < row["retention"] <= 1
            for row in rows),
        "formation_finite": all(
            math.isfinite(float(row["formation_fraction"]))
            and 0 < row["formation_fraction"] <= 1
            and row["formation_cycle"] == round(row["formation_fraction"] * CYCLES)
            for row in rows),
        "strength_finite": all(
            math.isfinite(float(row["strength"])) and float(row["strength"]) > 0
            for row in rows),
        "baseline_converged": baseline["converged"],
        "extended_converged": extended["converged"],
        "controlled_converged": controlled["converged"],
    }
    expected = base.get("summary", {}).get("count", {}).get("odds_ratio")
    if expected is not None:
        checks["baseline_reproduces_confirmed"] = (
            abs(baseline["count"]["odds_ratio"] - float(expected)) < 1e-12)
    return checks


def _readout(baseline: dict, extended: dict) -> str:
    base_or = baseline["count"]["odds_ratio"]
    adj_or = extended["count"]["odds_ratio"]
    ci_lo, ci_hi = extended["count"]["ci95"]
    if adj_or < 1.0 and ci_lo <= 1.0 <= ci_hi:
        return "COUNT ATTENUATES AND REVERSES"
    if adj_or < base_or and ci_lo <= 1.0 <= ci_hi:
        return "COUNT ATTENUATES TO NULL"
    if ci_lo > 1.0:
        return "COUNT PERSISTS"
    return "INDETERMINATE"


def _controlled_readout(controlled: dict) -> str:
    or_value = controlled["retention"]["odds_ratio"]
    lo, hi = controlled["retention"]["ci95"]
    if lo > 1.0:
        return "RETENTION SURVIVES FORMATION CONTROL"
    if hi < 1.0:
        return "RETENTION REVERSES UNDER FORMATION CONTROL"
    if or_value < 1.0:
        return "RETENTION ATTENUATES AND REVERSES"
    return "RETENTION ATTENUATES TO NULL"


def _quartiles(rows: list[dict]) -> list[dict]:
    ordered = sorted(rows, key=lambda row: (float(row["strength"]),
                                             row["seed"], row["edge"]))
    n = len(ordered)
    groups = []
    start = 0
    for end in (n // 4, n // 2, 3 * n // 4, n):
        if end <= start:
            continue
        sub = ordered[start:end]
        groups.append({
            "rank": len(groups) + 1,
            "n": len(sub),
            "events": sum(1 for row in sub if row["asserted"]),
            "strength_min": min(float(row["strength"]) for row in sub),
            "strength_max": max(float(row["strength"]) for row in sub),
            "mean_count": statistics.fmean(float(row["direct_count"]) for row in sub),
            "mean_retention": statistics.fmean(float(row["retention"]) for row in sub),
        })
        start = end
    return groups


def _descriptives(rows: list[dict]) -> dict:
    out = {}
    for name in ("direct_count", "retention", "retention_cycles", "strength",
                 "formation_cycle", "formation_fraction"):
        values = sorted(float(row[name]) for row in rows)
        out[name] = {
            "min": values[0],
            "p25": values[len(values) // 4],
            "median": statistics.median(values),
            "p75": values[3 * len(values) // 4],
            "max": values[-1],
            "mean": statistics.fmean(values),
            "sd": statistics.pstdev(values),
        }
    return out


def build() -> dict:
    base = _load(BASE)
    rows = _augment(_base_rows(), _load_captures())
    baseline = _fit_model(rows, ("rank", "count"))
    extended = _fit_model(rows, PERSISTENCE)
    controlled = _fit_model(rows, CONTROLLED)
    integrity = _integrity(rows, _load_captures(), base, baseline, extended,
                           controlled)
    if not all(integrity.values()):
        raise SystemExit("REFUSED: integrity " +
                         ", ".join(k for k, v in integrity.items() if not v))
    correlations = {}
    series = {
        "rank": [math.log2(float(row["min_rank"])) for row in rows],
        "count": [float(row["direct_count"]) for row in rows],
        "retention": [float(row["retention"]) for row in rows],
        "strength": [float(row["strength"]) for row in rows],
        "formation": [float(row["formation_fraction"]) for row in rows],
    }
    for a in series:
        for b in series:
            if a < b:
                correlations["%s~%s" % (a, b)] = _pearson(series[a], series[b])
    base_beta = baseline["count"]["beta"]
    adj_beta = extended["count"]["beta"]
    attenuation = 1.0 - adj_beta / base_beta if base_beta else None
    readout = _readout(baseline, extended)
    formation_readout = _controlled_readout(controlled)
    summary = {
        "n": len(rows),
        "events": sum(1 for row in rows if row["asserted"]),
        "baseline": _summary_model(baseline, ("rank", "count")),
        "extended": _summary_model(extended, PERSISTENCE),
        "controlled": _summary_model(controlled, CONTROLLED),
        "count_log_odds_attenuation": attenuation,
        "count_or_change": extended["count"]["odds_ratio"]
                           - baseline["count"]["odds_ratio"],
        "controlled_count_or": controlled["count"]["odds_ratio"],
        "formation_or": controlled["formation"]["odds_ratio"],
        "retention_or_without_formation": extended["retention"]["odds_ratio"],
        "retention_or_with_formation": controlled["retention"]["odds_ratio"],
        "retention_beta_change": (controlled["retention"]["beta"]
                                  - extended["retention"]["beta"]),
        "correlations": correlations,
        "descriptives": _descriptives(rows),
        "strength_quartiles": _quartiles(rows),
        "integrity": integrity,
        "posthoc_readout": readout,
        "formation_control_readout": formation_readout,
        "confirmatory_verdict": None,
    }
    loo = []
    for base_fold, ext_fold, ctrl_fold in zip(
            baseline["loo"], extended["loo"], controlled["loo"]):
        entry = {"held_out": base_fold["held_out"]}
        if "error" in base_fold or "error" in ext_fold or "error" in ctrl_fold:
            entry["error"] = (base_fold.get("error") or ext_fold.get("error")
                              or ctrl_fold.get("error"))
        else:
            entry["baseline_count"] = base_fold["count"]
            entry["extended_count"] = ext_fold["count"]
            entry["retention"] = ext_fold["retention"]
            entry["strength"] = ext_fold["strength"]
            entry["controlled_count"] = ctrl_fold["count"]
            entry["controlled_retention"] = ctrl_fold["retention"]
            entry["controlled_formation"] = ctrl_fold["formation"]
        loo.append(entry)
    return engine_stamp.stamp({
        "kind": "loop_persistence_assertion_model",
        "status": "POST-HOC, RUN",
        "prereg": None,
        "posthoc": True,
        "base": BASE.relative_to(ROOT).as_posix(),
        "question": (
            "Among never-served loop-forming world edges, does the confirmed "
            "direct-count association survive measured loop retention and strength, "
            "and does retention survive the cycle at which the loop first appeared?"
        ),
        "scope": (
            "Post-hoc extension on the same twelve consumed seeds, one compositional "
            "world family, 120 cycles, cap 40. No fresh seed."
        ),
        "definitions": {
            "retention": (
                "Observed loop span, (last reported loop cycle - first reported loop "
                "cycle + 1), divided by the cycles available from first detection to "
                "cycle 120. Bounded (0, 1]; single-cycle loops are not assigned zero."
            ),
            "strength": (
                "Maximum loop_candidate.strength over all reported loops containing "
                "the edge in either orientation. Strength is the within-loop minimum "
                "temporal edge count, so it is a measured carrier property."
            ),
            "formation": (
                "First reported loop cycle for the edge divided by 120, in (0, 1]. "
                "The control is linear in this fraction; it does not model a nonlinear "
                "onset effect."
            ),
            "population": (
                "The confirmed block's 177 never-served loop-forming edges; replay "
                "must reproduce each seed's loop edge set and loop cycles exactly."
            ),
            "standardization": "complete-case mean and population SD",
            "seed": "twelve-level fixed effect, first seed as reference",
            "interactions": "none",
            "selection": "none",
        },
        "models": {
            "baseline": (
                "logit P(asserted) = b0 + b_rank*z(log2(min_rank)) "
                "+ b_count*z(direct_count) + seed fixed effects"
            ),
            "extended": (
                "baseline + b_retention*z(retention) + b_strength*z(strength)"
            ),
            "controlled": (
                "extended + b_formation*z(formation); formation is the first loop "
                "cycle as a fraction of the 120-cycle run"
            ),
            "estimator": "Firth penalized likelihood",
        },
        "inference": (
            "Post hoc and descriptive. Coefficients, intervals, in-sample AUC/Brier, "
            "correlations, strength quartiles and leave-one-seed-out folds are "
            "reported; no confirmatory verdict and no multiplicity-adjusted claim. "
            "The formation control is a linear covariate for first-detection timing, "
            "not a causal identification strategy."
        ),
        "seeds": [{
            "seed": seed,
            "loop_edges": len(_load_captures()[seed]["loops"]),
            "asserted": sum(1 for row in rows
                            if row["seed"] == seed and row["asserted"]),
        } for seed in SEEDS],
        "rows": rows,
        "summary": summary,
        "leave_one_seed_out": loo,
        "not_evidence": (
            "A post-hoc observational extension in one synthetic world family on "
            "already-consumed seeds. Retention and strength are measured, not "
            "manipulated. The formation control is a linear covariate for "
            "first-detection timing, not a randomisation or an identification "
            "strategy. Attenuation is consistent with a proxy reading but does not "
            "establish mediation, causation, capability, transfer or a general engine "
            "property."
        ),
    })


def _fmt(value, digits=3):
    return "NA" if value is None else ("%.*f" % (digits, value))


def _fmt_p(value):
    return "NA" if value is None else "%.2e" % value


def render(art: dict) -> str:
    s = art["summary"]
    b = s["baseline"]
    e = s["extended"]
    c = s["controlled"]
    lines = [
        "# Loop retention, strength and formation timing in the loop-only model — post hoc",
        "",
        "Generated from `%s` by "
        "`python -m benchmarks.loop_persistence_assertion_model --write`. "
        "Do not edit by hand." % ARTIFACT.relative_to(ROOT).as_posix(),
        "",
        "**Post hoc, not confirmatory.** This extends the confirmed model on the "
        "same twelve consumed seeds. It has no preregistration and no verdict. "
        "The formation control was added before the controlled model was read.",
        "",
        "## Design",
        "",
        "- Population: the confirmed block's **%d** never-served loop-forming edges "
        "(**%d** asserted)." % (s["n"], s["events"]),
        "- Seeds: **%s**; no fresh seed." % ", ".join(str(v) for v in SEEDS),
        "- **Retention:** observed loop span divided by the cycles available after "
        "first detection, in **(0, 1]**. A loop seen in one cycle is not assigned zero.",
        "- **Strength:** maximum `loop_candidate.strength` over loops containing the "
        "edge; strength is the within-loop minimum temporal edge count.",
        "- **Formation:** first loop cycle divided by 120. It controls for when the "
        "loop first appeared, because retention's denominator is the cycles "
        "available after that point.",
        "- All models are Firth logistic with twelve seed fixed effects. The "
        "baseline is the confirmed rank + count model; the persistence model adds "
        "retention and strength; the controlled model adds formation. Predictors "
        "are per 1 SD.",
        "",
        "## Count association",
        "",
        "| Model | Count OR | 95% CI | Count beta | In-sample AUC | Brier |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        "| Baseline (confirmed form) | %.3f | %.3f–%.3f | %.3f | %s | %s |"
        % (b["coefficients"]["count"]["odds_ratio"],
           b["coefficients"]["count"]["ci95"][0],
           b["coefficients"]["count"]["ci95"][1],
           b["coefficients"]["count"]["beta"], _fmt(b["auc"]), _fmt(b["brier"], 4)),
        "| + retention + strength | %.3f | %.3f–%.3f | %.3f | %s | %s |"
        % (e["coefficients"]["count"]["odds_ratio"],
           e["coefficients"]["count"]["ci95"][0],
           e["coefficients"]["count"]["ci95"][1],
           e["coefficients"]["count"]["beta"], _fmt(e["auc"]), _fmt(e["brier"], 4)),
        "| + formation control | %.3f | %.3f–%.3f | %.3f | %s | %s |"
        % (c["coefficients"]["count"]["odds_ratio"],
           c["coefficients"]["count"]["ci95"][0],
           c["coefficients"]["count"]["ci95"][1],
           c["coefficients"]["count"]["beta"], _fmt(c["auc"]), _fmt(c["brier"], 4)),
        "",
        "The count log-odds coefficient changes by **%+.1f%%** from baseline to "
        "adjusted (positive means attenuation). The adjusted count OR is **%.3f** "
        "(95%% CI **%.3f–%.3f**, p **%s**)."
        % (100.0 * s["count_log_odds_attenuation"],
           e["coefficients"]["count"]["odds_ratio"],
           e["coefficients"]["count"]["ci95"][0],
           e["coefficients"]["count"]["ci95"][1],
           _fmt_p(e["coefficients"]["count"]["p"])),
        "",
        "**Post-hoc readout: `%s`.** This is a descriptive label, not a verdict."
        % s["posthoc_readout"],
        "",
        "The adjusted count OR is below 1, so the association does not merely lose "
        "significance: after persistence enters, the point estimate changes sign and "
        "its interval includes 1. The in-sample AUC rises to **%s** and the Brier "
        "score falls to **%s**, but these are fit statistics on the same rows, not "
        "held-out predictions."
        % (_fmt(e["auc"]), _fmt(e["brier"], 4)),
        "",
        "## Retention and strength",
        "",
        "| Predictor | Model | OR per 1 SD | 95% CI | p | AME |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for model, label in ((e, "persistence"), (c, "+ formation")):
        for name, display in (("retention", "Retention"), ("strength", "Strength")):
            row = model["coefficients"][name]
            lines.append("| %s | %s | %.3f | %.3f–%.3f | %s | %+.3f |"
                         % (display, label, row["odds_ratio"], row["ci95"][0],
                            row["ci95"][1], _fmt_p(row["p"]),
                            model["average_marginal_effects"][name]))
    formation = c["coefficients"]["formation"]
    lines.append("| Formation | + formation | %.3f | %.3f–%.3f | %s | %+.3f |"
                 % (formation["odds_ratio"], formation["ci95"][0],
                    formation["ci95"][1], _fmt_p(formation["p"]),
                    c["average_marginal_effects"]["formation"]))
    rank_base = b["coefficients"]["rank"]
    rank_ext = e["coefficients"]["rank"]
    lines += [
        "",
        "Strength's 1-SD step is **%.2f** raw units, so its **%.2f** OR per SD is "
        "about **%.2f** per raw strength unit; retention's 1-SD step is **%.3f**, so "
        "its OR per +0.1 retention is about **%.2f**."
        % (s["descriptives"]["strength"]["sd"],
           e["coefficients"]["strength"]["odds_ratio"],
           math.exp(e["coefficients"]["strength"]["beta"]
                    / s["descriptives"]["strength"]["sd"]),
           s["descriptives"]["retention"]["sd"],
           math.exp(0.1 * e["coefficients"]["retention"]["beta"]
                    / s["descriptives"]["retention"]["sd"])),
        "",
        "The formation control moves the retention OR from **%.3f** to **%.3f** "
        "(controlled 95%% CI **%.3f–%.3f**, p **%s**); the controlled formation "
        "OR is **%.3f** (95%% CI **%.3f–%.3f**). **Formation-control readout: "
        "`%s`.** This is descriptive, not a verdict."
        % (s["retention_or_without_formation"], s["retention_or_with_formation"],
           c["coefficients"]["retention"]["ci95"][0],
           c["coefficients"]["retention"]["ci95"][1],
           _fmt_p(c["coefficients"]["retention"]["p"]),
           formation["odds_ratio"], formation["ci95"][0], formation["ci95"][1],
           s["formation_control_readout"]),
        "",
        "Rank is shown for completeness: baseline OR **%.3f** (%.3f–%.3f), "
        "adjusted OR **%.3f** (%.3f–%.3f), controlled OR **%.3f** (%.3f–%.3f)."
        % (rank_base["odds_ratio"], rank_base["ci95"][0], rank_base["ci95"][1],
           rank_ext["odds_ratio"], rank_ext["ci95"][0], rank_ext["ci95"][1],
           c["coefficients"]["rank"]["odds_ratio"],
           c["coefficients"]["rank"]["ci95"][0],
           c["coefficients"]["rank"]["ci95"][1]),
        "",
        "Strength is not a subtle gradient in this sample. Its upper quartile is "
        "almost entirely asserted while its lower quartile is almost entirely not:",
        "",
        "| Strength quartile | Range | Edges | Asserted | Mean count | Mean retention |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for group in s["strength_quartiles"]:
        lines.append("| %d | %.0f–%.0f | %d | %d | %.1f | %.3f |"
                     % (group["rank"], group["strength_min"], group["strength_max"],
                        group["n"], group["events"], group["mean_count"],
                        group["mean_retention"]))
    lines += [
        "",
        "## Descriptives",
        "",
        "| Variable | Min | P25 | Median | P75 | Max | Mean | SD |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("direct_count", "retention", "retention_cycles", "strength",
                 "formation_cycle", "formation_fraction"):
        d = s["descriptives"][name]
        lines.append("| `%s` | %.3f | %.3f | %.3f | %.3f | %.3f | %.3f | %.3f |"
                     % (name, d["min"], d["p25"], d["median"], d["p75"],
                        d["max"], d["mean"], d["sd"]))
    lines += [
        "",
        "## Predictor correlations",
        "",
        "| Pair | Pearson r |",
        "| --- | ---: |",
    ]
    for key, value in s["correlations"].items():
        lines.append("| `%s` | %.3f |" % (key, value))
    lines += [
        "",
        "## Leave-one-seed-out",
        "",
        "| Held out | Baseline count | Adjusted count | Retention | Strength | "
        "Controlled count | Controlled retention | Controlled formation |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in art["leave_one_seed_out"]:
        if "error" in row:
            lines.append("| %d | %s | — | — | — | — | — | — |"
                         % (row["held_out"], row["error"]))
        else:
            lines.append("| %d | %.3f | %.3f | %.3f | %.3f | %.3f | %.3f | %.3f |"
                         % (row["held_out"], row["baseline_count"],
                            row["extended_count"], row["retention"],
                            row["strength"], row["controlled_count"],
                            row["controlled_retention"],
                            row["controlled_formation"]))
    lines += [
        "",
        "## Integrity",
        "",
        "| Check | Passes |",
        "| --- | --- |",
    ]
    for name, passed in s["integrity"].items():
        lines.append("| `%s` | %s |" % (name, "yes" if passed else "no"))
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "Retention and strength are measured at the edge, not assigned by treatment. "
        "The count coefficient falls below zero when they enter, which is consistent "
        "with count being a marker for how long and how strongly the loop was present. "
        "It does not follow that persistence causes assertion: strength is close to a "
        "separating variable here, retention and strength correlate at **%.2f**, and "
        "the model is observational. The formation control does not attenuate the "
        "retention association in this sample; the controlled retention OR is larger "
        "than the uncontrolled one, and later formation has its own positive "
        "association. That is consistent with timing and retention carrying separate "
        "information, but the control is linear, the timing is measured rather than "
        "assigned, and onset may proxy for unmeasured loop quality. The sample is "
        "small, the seeds are reused and the world family is synthetic."
        % s["correlations"]["retention~strength"],
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != "loop_persistence_assertion_model":
        found.append("artifact kind")
    if art.get("status") != "POST-HOC, RUN" or not art.get("posthoc"):
        found.append("post-hoc status")
    if art.get("confirmatory_verdict") is not None:
        found.append("confirmatory verdict present")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    rows = art.get("rows") or []
    if len({(row["seed"], row["edge"]) for row in rows}) != len(rows):
        found.append("duplicate rows")
    if not all("retention" in row and "strength" in row
               and "formation_cycle" in row and "formation_fraction" in row
               for row in rows):
        found.append("missing persistence fields")
    base = _load(BASE)
    baseline = _fit_model(rows, ("rank", "count"))
    extended = _fit_model(rows, PERSISTENCE)
    controlled = _fit_model(rows, CONTROLLED)
    summary = art.get("summary") or {}
    if summary.get("n") != len(rows):
        found.append("summary n")
    if summary.get("events") != sum(1 for row in rows if row["asserted"]):
        found.append("summary events")
    if summary.get("baseline") != _summary_model(baseline, ("rank", "count")):
        found.append("summary baseline")
    if summary.get("extended") != _summary_model(extended, PERSISTENCE):
        found.append("summary extended")
    if summary.get("controlled") != _summary_model(controlled, CONTROLLED):
        found.append("summary controlled")
    if summary.get("posthoc_readout") != _readout(baseline, extended):
        found.append("summary readout")
    if summary.get("formation_control_readout") != _controlled_readout(controlled):
        found.append("summary formation readout")
    integrity = _integrity(rows, _load_captures(), base, baseline, extended,
                           controlled)
    if summary.get("integrity") != integrity or not all(integrity.values()):
        found.append("integrity")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    return found


def write() -> int:
    art = build()
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(art), encoding="utf-8")
    s = art["summary"]
    b, e, c = s["baseline"], s["extended"], s["controlled"]
    print("loop persistence assertion model: %s / %s %s"
          % (s["posthoc_readout"], s["formation_control_readout"], json.dumps({
              "n": s["n"],
              "events": s["events"],
              "baseline_count_or": round(b["coefficients"]["count"]["odds_ratio"], 3),
              "adjusted_count_or": round(e["coefficients"]["count"]["odds_ratio"], 3),
              "controlled_count_or": round(c["coefficients"]["count"]["odds_ratio"], 3),
              "retention_or": round(e["coefficients"]["retention"]["odds_ratio"], 3),
              "controlled_retention_or": round(
                  c["coefficients"]["retention"]["odds_ratio"], 3),
              "controlled_retention_ci": [round(v, 3)
                                          for v in c["coefficients"]["retention"]["ci95"]],
              "formation_or": round(c["coefficients"]["formation"]["odds_ratio"], 3),
              "strength_or": round(e["coefficients"]["strength"]["odds_ratio"], 3),
              "attenuation": round(s["count_log_odds_attenuation"], 3),
          })))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    s = art["summary"]
    e, c = s["extended"], s["controlled"]
    print("loop persistence assertion model: %s / %s %s"
          % (s["posthoc_readout"], s["formation_control_readout"], json.dumps({
              "n": s["n"],
              "adjusted_count_or": round(e["coefficients"]["count"]["odds_ratio"], 3),
              "controlled_count_or": round(c["coefficients"]["count"]["odds_ratio"], 3),
              "retention_or": round(e["coefficients"]["retention"]["odds_ratio"], 3),
              "controlled_retention_or": round(
                  c["coefficients"]["retention"]["odds_ratio"], 3),
              "controlled_retention_ci": [round(v, 3)
                                          for v in c["coefficients"]["retention"]["ci95"]],
              "formation_or": round(c["coefficients"]["formation"]["odds_ratio"], 3),
          })))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--collect", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.collect:
        return collect()
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
