"""CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1: collection and adjudication.

The block is frozen and ungranted.  Every executing path calls ``refuse()``
before a scratch database is opened.  ``--dry-run`` prints the twenty-four
commands without touching a database; ``--cell``, ``--measure`` and ``--finish``
refuse until the record carries a complete dated grant.

Collection captures the complete structure-appearance list for every
never-served world edge across all 120 sleep cycles, not only a first
post-landmark appearance.  The event is the first sustained two-cycle entry at
``formation + 40`` or later, after a structure-free interval through
``formation + 39``.  Final presence at cycle 120 is descriptive only.

    python -m benchmarks.retention_entry_transition --dry-run
    python -m benchmarks.retention_entry_transition --cell 20620101
    python -m benchmarks.retention_entry_transition --measure
    python -m benchmarks.retention_entry_transition --finish
    python -m benchmarks.retention_entry_transition --check
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from benchmarks import authorisation_guard
from benchmarks import engine_stamp
from benchmarks import retention_entry_transition_prereg as block
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.never_served_assertion_model import (
    _auc,
    _fit_firth,
    _p_value,
    _sigmoid,
)
from benchmarks.presence_construct_audit import (
    ACQ_SOURCE,
    PHASE_ACQUISITION,
    _world_compositional_edges,
)
from benchmarks.presence_conversion_repair_observer import RepairedObserverSleepService

MODULE = "benchmarks.retention_entry_transition"
ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / ".scratch" / "retention_entry_transition" / "parts"
ARTIFACT = ROOT / "docs" / "retention_entry_transition.json"
PAGE = ROOT / "docs" / "RETENTION-ENTRY-TRANSITION.md"

PRIMARY = ("early", "proximal", "rank", "count", "strength", "followup")
BASE = ("early", "rank", "count", "strength", "followup")
FULL = PRIMARY + ("rank40", "count40", "strength40")
MODEL_NOTE = (
    "The primary coefficient is early retention. Proximal retention is a "
    "pre-outcome control measured in f+20..f+39, not a reverse-time variable. "
    "The base, full-sensitivity and final-presence models are diagnostics."
)


def result_not_evidence(verdict: str) -> str:
    if verdict == "VOID":
        return (
            "An observational entry-transition model on one synthetic world "
            "family.  The block is VOID on its own gates, so it establishes no "
            "retention, temporal-order, capability, causal or general engine "
            "property.  A failed population gate is a measurement about this "
            "design, not evidence that retention has no effect."
        )
    if verdict == "CONFIRMED":
        return (
            "An observational entry-transition model on one synthetic world "
            "family.  Early loop retention is associated with a later sustained "
            "structure entry beyond proximal retention and the measured "
            "controls.  It does not establish a mechanism, capability, transfer, "
            "causal effect, or general engine property."
        )
    return (
        "An observational entry-transition model on one synthetic world family. "
        "It does not establish a mechanism, capability, transfer, causal effect, "
        "or general engine property."
    )


def planned() -> list[int]:
    return [int(seed) for seed in block.record()["design"]["seeds"]]


def command(seed: int) -> str:
    return "python -m %s --cell %d" % (MODULE, seed)


def dry_run() -> int:
    """Print the frozen commands.  This path never reads a database."""
    for seed in planned():
        print(command(seed))
    return 0


def preflight() -> list[str]:
    """Every reason a cell may not run.  Read before any database is opened."""
    doc = block.record()
    found: list[str] = list(authorisation_guard.problems(doc))
    if doc.get("status") not in ("FROZEN, NOT RUN", "GRANTED, NOT RUN"):
        found.append("the block is %r, not frozen or granted" % doc.get("status"))
    auth = doc.get("authorisation") or {}
    if auth.get("granted") is not True:
        found.append("the dated grant is not recorded")
    if not auth.get("granted_on"):
        found.append("the grant has no date")
    else:
        try:
            date.fromisoformat(str(auth["granted_on"]))
        except ValueError:
            found.append("the grant date is not ISO YYYY-MM-DD")
    if not auth.get("document"):
        found.append("the grant names no document")
    elif not (ROOT / str(auth["document"])).exists():
        found.append("the grant document does not exist")
    if not auth.get("quote"):
        found.append("the grant records no quote")
    if getattr(__import__("organica"), "__version__", None) != "0.15.0":
        found.append("the shipped build is not 0.15.0")
    runner = doc.get("runner") or {}
    if runner.get("built") is not True:
        found.append("the record does not mark the runner built")
    if runner.get("planned_module") != MODULE:
        found.append("the record names a different runner module")
    if block.RESULT.exists():
        found.append("the block already has a result")
    return found


def refuse() -> None:
    reasons = preflight()
    if reasons:
        print("REFUSED: %s will not run:" % block.ID, file=sys.stderr)
        for reason in reasons:
            print("  -", reason, file=sys.stderr)
        raise SystemExit(2)


def part_path(seed: int) -> Path:
    return PARTS / ("%d.json" % seed)


def _entry_cycle(appearances: list[int], formation: int | None,
                 cycles: int) -> int | None:
    """First sustained entry at or after formation + 40.

    A sustained entry is two adjacent structure appearances.  A one-cycle
    flicker, an appearance before the outcome window, and an isolated final
    appearance do not count.
    """
    if formation is None:
        return None
    start = formation + block.OUTCOME_START
    seen = set(appearances)
    for cycle in range(start, cycles):
        if cycle in seen and cycle + 1 in seen:
            return cycle
    return None


def _structure_free(appearances: list[int], formation: int | None) -> bool | None:
    if formation is None:
        return None
    return all(cycle > formation + block.STRUCTURE_FREE_THROUGH
               for cycle in appearances)


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return float("nan")
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return float("nan")
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy)


def _counts(mem) -> dict[tuple[str, str], int]:
    return {(a, b): int(c) for a, b, c in
            mem._conn.execute("SELECT tag_from, tag_to, count FROM precedes")}


def _capture_seed(seed: int) -> dict:
    """Replay one seed and capture full cycle-level appearance lists."""
    doc = block.record()
    cycles = int(doc["design"]["cycles"])
    max_formation = int(doc["design"]["max_formation_cycle"])
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("retention_entry_transition_%d" % seed)
    mem = _CountingMemoryService(str(db_path))
    svc = RepairedObserverSleepService(mem, observe=True, cap=block.CAP)
    served = Counter()
    loop_cycles: dict[tuple[str, str], set[int]] = defaultdict(set)
    strengths: dict[tuple[str, str], list[tuple[int, float]]] = defaultdict(list)
    ranks: dict[tuple[str, str], dict[int, int]] = defaultdict(dict)
    counts: dict[tuple[str, str], dict[int, int]] = defaultdict(dict)
    appearances: dict[tuple[str, str], list[int]] = defaultdict(list)
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    cycle = 0
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            if not (in_acq and not trainable):
                mem.store(text, event_type="observe",
                          source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE != 0:
                continue
            report = svc.run_sleep_cycle()
            cycle += 1
            for candidate in report.predictions:
                edge = (candidate.source, candidate.target)
                if edge in world_edges:
                    served[edge] += 1

            for loop in report.loops:
                path = list(loop.path)
                for a, b in zip(path, path[1:]):
                    for edge in ((a, b), (b, a)):
                        if edge in world_edges:
                            loop_cycles[edge].add(cycle)
                            strengths[edge].append((cycle, float(loop.strength)))

            universe = getattr(svc, "universe", [])
            if universe:
                for row in universe[-1]:
                    edge = tuple(row["edge"])
                    if edge not in world_edges:
                        continue
                    rank = int(row["rank"])
                    previous = ranks[edge].get(cycle)
                    ranks[edge][cycle] = rank if previous is None else min(previous, rank)

            current = {(a, b) for a, targets in
                       structure_edges(svc._load_prior_candidates()).items()
                       for b in targets}
            for edge in world_edges & current:
                appearances[edge].append(cycle)

            counts_now = _counts(mem)
            for edge in world_edges:
                counts[edge][cycle] = int(counts_now.get(edge, 0))

        final = {(a, b) for a, targets in
                 structure_edges(svc._load_prior_candidates()).items()
                 for b in targets}
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    final_asserted = final & world_edges
    rows = []
    for edge in sorted(world_edges):
        if served.get(edge, 0):
            continue
        observed = sorted(loop_cycles.get(edge, set()))
        formation = observed[0] if observed else None
        app = sorted(appearances.get(edge, []))
        early = None
        proximal = None
        followup = None
        rank20 = None
        rank40 = None
        count20 = None
        count40 = None
        strength20 = 0.0
        strength40 = 0.0
        if formation is not None:
            early_end = formation + block.WINDOW - 1
            proximal_start = early_end + 1
            proximal_end = proximal_start + block.WINDOW - 1
            in_early = [c for c in observed if formation <= c <= early_end]
            in_proximal = [c for c in observed if proximal_start <= c <= proximal_end]
            early = len(set(in_early)) / float(block.WINDOW)
            proximal = len(set(in_proximal)) / float(block.WINDOW)
            available = cycles - (formation + block.OUTCOME_START) + 1
            followup = available / float(cycles)
            rank_values = [ranks[edge][c] for c in range(formation, early_end + 1)
                           if c in ranks.get(edge, {})]
            rank20 = min(rank_values) if rank_values else None
            proximal_ranks = [ranks[edge][c] for c in range(proximal_start, proximal_end + 1)
                              if c in ranks.get(edge, {})]
            rank40 = min(proximal_ranks) if proximal_ranks else None
            count20 = counts.get(edge, {}).get(early_end)
            count40 = counts.get(edge, {}).get(proximal_end)
            early_strengths = [s for c, s in strengths.get(edge, [])
                               if formation <= c <= early_end]
            strength20 = max(early_strengths) if early_strengths else 0.0
            proximal_strengths = [s for c, s in strengths.get(edge, [])
                                  if proximal_start <= c <= proximal_end]
            strength40 = max(proximal_strengths) if proximal_strengths else 0.0
        rows.append({
            "seed": seed,
            "edge": "%s>%s" % edge,
            "served_windows": int(served.get(edge, 0)),
            "ever_loop": bool(observed),
            "formation_cycle": formation,
            "loop_cycles": observed,
            "appearances": app,
            "structure_free_through_f39": _structure_free(app, formation),
            "early_retention": early,
            "proximal_retention": proximal,
            "followup": followup,
            "rank20": rank20,
            "rank40": rank40,
            "count20": count20,
            "count40": count40,
            "strength20": strength20,
            "strength40": strength40,
            "entry_cycle": _entry_cycle(app, formation, cycles),
            "final_assertion": edge in final_asserted,
        })
    return engine_stamp.stamp({
        "kind": "retention_entry_transition_cell",
        "prereg": block.ID,
        "seed": seed,
        "cycles": cycle,
        "cap": block.CAP,
        "max_formation_cycle": max_formation,
        "appearance_cycles_captured": cycle,
        "world_edges": len(world_edges),
        "served_world_edges": sum(1 for edge in world_edges if served.get(edge, 0)),
        "final_asserted_world_edges": len(final_asserted),
        "never_served": len(rows),
        "never_served_loop": sum(1 for row in rows if row["ever_loop"]),
        "never_served_entries": sum(1 for row in rows
                                    if row["entry_cycle"] is not None),
        "rows": rows,
    })


def run_cell(seed: int) -> dict:
    refuse()
    if seed not in planned():
        raise SystemExit("REFUSED: %d is not a planned seed" % seed)
    return _capture_seed(seed)


def cell(seed: int, force: bool = False) -> int:
    refuse()
    if seed not in planned():
        print("REFUSED: %d is not a planned seed" % seed, file=sys.stderr)
        return 2
    path = part_path(seed)
    if path.exists() and not force:
        print("REFUSED: %s already exists; use --force to rerun" % path,
              file=sys.stderr)
        return 2
    part = run_cell(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(part, indent=1) + "\n", encoding="utf-8")
    print("wrote %s" % path)
    return 0


def measure(force: bool = False) -> int:
    refuse()
    for seed in planned():
        path = part_path(seed)
        if path.exists() and not force:
            print("cached %d" % seed)
            continue
        part = run_cell(seed)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(part, indent=1) + "\n", encoding="utf-8")
        print("collected %d: never-served %d, entries %d"
              % (seed, part["never_served"], part["never_served_entries"]))
    return 0


def _appearance_problems(part: dict) -> list[str]:
    """Row-level schema errors in a part's full appearance-cycle capture."""
    found = []
    seen_edges = set()
    for index, row in enumerate(part.get("rows") or []):
        if row.get("seed") != part.get("seed"):
            found.append("row %d seed %r does not match part seed %r"
                         % (index, row.get("seed"), part.get("seed")))
        edge = row.get("edge")
        if not isinstance(edge, str) or not edge:
            found.append("row %d has no edge string" % index)
        elif edge in seen_edges:
            found.append("row %d duplicates edge %r within seed %s"
                         % (index, edge, part.get("seed")))
        else:
            seen_edges.add(edge)
        appearances = row.get("appearances")
        if not isinstance(appearances, list):
            found.append("row %d appearances are not a list" % index)
            continue
        if not all(type(cycle) is int for cycle in appearances):
            found.append("row %d appearance cycles are not integers: %r"
                         % (index, appearances))
            continue
        if appearances != sorted(set(appearances)):
            found.append("row %d appearances are not a sorted unique list" % index)
            continue
        if any(cycle < 1 or cycle > block.CYCLES for cycle in appearances):
            found.append("row %d appearances fall outside 1..%d: %r"
                         % (index, block.CYCLES, appearances))
    return found


def _load_parts() -> list[dict]:
    seeds = planned()
    if not seeds:
        raise SystemExit("planned seed block is empty")
    duplicates = sorted({seed for seed in seeds if seeds.count(seed) > 1})
    if duplicates:
        raise SystemExit("duplicate planned seeds: %r" % duplicates)
    missing = [seed for seed in seeds if not part_path(seed).exists()]
    if missing:
        raise SystemExit("missing parts: %r; run --measure" % missing)
    parts = []
    for seed in seeds:
        part = json.loads(part_path(seed).read_text(encoding="utf-8"))
        if part.get("prereg") != block.ID or part.get("seed") != seed:
            raise SystemExit("part %d does not belong to this block" % seed)
        if part.get("cycles") != block.CYCLES or part.get("cap") != block.CAP:
            raise SystemExit("part %d has the wrong cycles or cap" % seed)
        if part.get("appearance_cycles_captured") != block.CYCLES:
            raise SystemExit("part %d did not capture every cycle" % seed)
        bad = _appearance_problems(part)
        if bad:
            raise SystemExit("part %d has invalid appearance cycles: %s"
                             % (seed, "; ".join(bad)))
        parts.append(part)
    return parts


def _exp(value: float) -> float:
    if value > 709.0:
        return 1e308
    if value < -745.0:
        return 0.0
    return math.exp(value)


def _finite_value(value) -> bool:
    return value is not None and math.isfinite(float(value))


def _fit(rows: list[dict], predictors: tuple[str, ...],
         outcome: str = "entry", use_seeds: list[int] | None = None,
         with_loo: bool = False) -> dict:
    use_seeds = planned() if use_seeds is None else list(use_seeds)
    data = [row for row in rows
            if row["seed"] in use_seeds and row.get("rank20") is not None]
    if any(name in predictors for name in ("rank40", "count40", "strength40")):
        data = [row for row in data
                if all(row.get(name) is not None
                       for name in ("rank40", "count40", "strength40"))]
    if not data:
        raise ValueError("empty fit population")
    raw = {
        "rank": [math.log2(float(row["rank20"])) if row.get("rank20") is not None
                 else float("nan") for row in data],
        "count": [float(row["count20"]) if row.get("count20") is not None
                  else float("nan") for row in data],
        "strength": [float(row["strength20"]) if row.get("strength20") is not None
                     else float("nan") for row in data],
        "followup": [float(row["followup"]) if row.get("followup") is not None
                     else float("nan") for row in data],
        "early": [float(row["early_retention"]) if row.get("early_retention") is not None
                  else float("nan") for row in data],
        "proximal": [float(row["proximal_retention"])
                     if row.get("proximal_retention") is not None
                     else float("nan") for row in data],
        "rank40": [math.log2(float(row["rank40"])) if row.get("rank40") is not None
                   else float("nan") for row in data],
        "count40": [float(row["count40"]) if row.get("count40") is not None
                    else float("nan") for row in data],
        "strength40": [float(row["strength40"]) if row.get("strength40") is not None
                       else float("nan") for row in data],
    }
    for name in predictors:
        if any(not math.isfinite(value) for value in raw[name]):
            raise ValueError("non-finite predictor: " + name)
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
    if outcome == "entry":
        y = [1.0 if row["entry_cycle"] is not None else 0.0 for row in data]
    elif outcome == "final_assertion":
        y = [1.0 if row["final_assertion"] else 0.0 for row in data]
    else:
        raise ValueError("unknown outcome: " + outcome)
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
            "odds_ratio": _exp(beta),
            "ci95": [_exp(beta - 1.959963984540054 * se),
                     _exp(beta + 1.959963984540054 * se)],
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

    ame = {name: statistics.fmean(predict(row, {name: 1.0}) - predict(row)
                                  for row in data)
           for name in predictors}
    loo = []
    if with_loo:
        for seed in use_seeds:
            sub = [row for row in rows if row["seed"] != seed]
            try:
                fold = _fit(sub, predictors, outcome,
                            [s for s in use_seeds if s != seed], with_loo=False)
                entry = {"held_out": seed}
                for name in predictors:
                    entry[name] = fold[name]["beta"]
                loo.append(entry)
            except Exception as exc:
                loo.append({"held_out": seed,
                            "error": type(exc).__name__ + ": " + str(exc)})
    return {
        "data": data,
        "outcome": outcome,
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
        "levels": levels,
        **{name: by_name[name] for name in predictors},
    }


def _summary(model: dict, predictors: tuple[str, ...]) -> dict:
    return {
        "n": model["n"],
        "events": model["events"],
        "outcome": model["outcome"],
        "converged": model["converged"],
        "coefficients": {name: model[name] for name in predictors},
        "auc": model["auc"] if math.isfinite(model["auc"]) else None,
        "brier": model["brier"],
        "average_marginal_effects": model["ame"],
        "leave_one_seed_out": model["loo"],
    }


def _eligible(rows: list[dict]) -> list[dict]:
    """The frozen population, including full appearance-cycle capture."""
    out = []
    for row in rows:
        if not row.get("ever_loop"):
            continue
        formation = row.get("formation_cycle")
        if formation is None or formation > block.MAX_FORMATION:
            continue
        app = row.get("appearances")
        if not isinstance(app, list) or app != sorted(set(app)):
            continue
        if any(cycle < 1 or cycle > block.CYCLES for cycle in app):
            continue
        if row.get("structure_free_through_f39") is not True:
            continue
        if any(not _finite_value(row.get(name))
               for name in ("early_retention", "proximal_retention", "followup")):
            continue
        if block.CYCLES - (formation + block.OUTCOME_START) + 1 < block.WINDOW:
            continue
        out.append(row)
    return out


def _finite_coefficients(model: dict) -> bool:
    return all(math.isfinite(float(coef["beta"]))
               and math.isfinite(float(coef["se"]))
               for coef in model["coefficients"])


def _entry_valid(row: dict) -> bool:
    app = row.get("appearances") or []
    formation = row.get("formation_cycle")
    entry = row.get("entry_cycle")
    if formation is None or any(cycle <= formation + block.STRUCTURE_FREE_THROUGH
                                for cycle in app):
        return False
    if entry is None:
        return True
    return (entry > formation + block.STRUCTURE_FREE_THROUGH
            and entry in app and entry + 1 in app and entry + 1 <= block.CYCLES)


def _adjudicate(rows: list[dict]) -> dict:
    eligible = _eligible(rows)
    base = [row for row in eligible if row["rank20"] is not None]
    try:
        primary = _fit(base, PRIMARY)
        base_model = _fit(base, BASE)
        error = None
    except Exception as exc:
        primary = base_model = None
        error = type(exc).__name__ + ": " + str(exc)
    full = final = None
    full_error = final_error = None
    if base:
        try:
            full = _fit(base, FULL)
        except Exception as exc:
            full_error = type(exc).__name__ + ": " + str(exc)
        try:
            final = _fit(base, BASE, outcome="final_assertion")
        except Exception as exc:
            final_error = type(exc).__name__ + ": " + str(exc)

    correlations = [float(row["early_retention"]) for row in eligible]
    proximals = [float(row["proximal_retention"]) for row in eligible]
    separation = _pearson(correlations, proximals)
    gates = {
        "D1_population": (
            len(eligible) >= block.MIN_EDGES
            and sum(1 for row in eligible if row["entry_cycle"] is not None)
            >= block.MIN_EVENTS
            and len({(row["seed"], row["edge"]) for row in eligible}) == len(eligible)
        ),
        "D2_structure_free": all(
            row["formation_cycle"] is not None
            and row["formation_cycle"] <= block.MAX_FORMATION
            and row["structure_free_through_f39"] is True
            and _finite_value(row["early_retention"])
            and _finite_value(row["proximal_retention"])
            for row in eligible),
        "D3_rank_coverage": (len(base) / len(eligible) >= 0.95
                             if eligible else False),
        "D4_seed_levels": (len({row["seed"] for row in eligible})
                           == len(planned()) if eligible else False),
        "D5_convergence": bool(primary and base_model
                               and primary["converged"] and base_model["converged"]
                               and _finite_coefficients(primary)
                               and _finite_coefficients(base_model)),
        "D6_complete": all(
            _finite_value(row.get("count20"))
            and _finite_value(row.get("strength20"))
            and _finite_value(row.get("followup")) for row in base),
        "D7_entry_validity": all(_entry_valid(row) for row in eligible),
        "D8_no_collision": False,
        "D9_separation": bool(math.isfinite(separation)
                              and abs(separation) <= 0.80),
        "D10_exposure": all(
            block.CYCLES - (row["formation_cycle"] + block.OUTCOME_START) + 1
            >= block.WINDOW for row in eligible),
    }
    try:
        from benchmarks.presence_cap_experiment import seed_collisions
        gates["D8_no_collision"] = not seed_collisions(
            planned(), allow=(block.PREREG, block.RESULT))
    except Exception:
        gates["D8_no_collision"] = False
    if error or primary is None or base_model is None:
        criteria = {"P1": False, "P2": False, "P3": False, "P4": False}
        verdict = "VOID"
    else:
        p1 = primary["early"]["odds_ratio"] > 1.0
        p2 = primary["early"]["ci95"][0] > 1.0
        p3 = all(gates.values())
        p4 = (primary["proximal"]["odds_ratio"] <= 1.0
              or primary["proximal"]["ci95"][0] <= 1.0)
        criteria = {"P1": p1, "P2": p2, "P3": p3, "P4": p4}
        if not p3:
            verdict = "VOID"
        elif p1 and p2 and p4:
            verdict = "CONFIRMED"
        elif p1 and p2 and not p4:
            verdict = "CONFIRMED, PROXIMALLY AMBIGUOUS"
        elif p1:
            verdict = "DIRECTIONAL ONLY"
        else:
            verdict = "NOT CONFIRMED"
    return {
        "n_never_served": len(rows),
        "n_loop": sum(1 for row in rows if row["ever_loop"]),
        "n_structure_free": sum(1 for row in rows
                                if row["ever_loop"]
                                and row["structure_free_through_f39"] is True),
        "n_pre_entry_presence": sum(
            1 for row in rows if row["ever_loop"]
            and row["structure_free_through_f39"] is False),
        "n_eligible": len(eligible),
        "n_complete": len(base),
        "n_events": sum(1 for row in eligible if row["entry_cycle"] is not None),
        "n_final_assertion": sum(1 for row in eligible if row["final_assertion"]),
        "n_seeds": len({row["seed"] for row in eligible}),
        "eligible_by_seed": {
            str(seed): sum(1 for row in eligible if row["seed"] == seed)
            for seed in planned()},
        "separation": separation if math.isfinite(separation) else None,
        "primary": _summary(primary, PRIMARY) if primary else None,
        "base": _summary(base_model, BASE) if base_model else None,
        "full": _summary(full, FULL) if full else None,
        "final_presence": _summary(final, BASE) if final else None,
        "full_error": full_error,
        "final_presence_error": final_error,
        "gates": gates,
        "criteria": criteria,
        "verdict": verdict,
        "fit_error": error,
    }


def build() -> dict:
    parts = _load_parts()
    rows = [row for part in parts for row in part["rows"]]
    summary = _adjudicate(rows)
    doc = block.record()
    body = engine_stamp.stamp({
        "kind": "retention_entry_transition",
        "status": "RUN",
        "prereg": block.PREREG.relative_to(ROOT).as_posix(),
        "question": doc["question"],
        "scope": (
            "Twenty-four fresh seeds, 120 cycles, cap 40, compositional world; "
            "per-edge structure-free interval through f+39, full appearance "
            "cycle capture, and a sustained two-cycle entry at f+40 or later."
        ),
        "design": doc["design"],
        "model": doc["model"],
        "model_note": MODEL_NOTE,
        "criteria": doc["criteria"],
        "gates": doc["gates"],
        "seeds": [{
            "seed": part["seed"],
            "never_served": part["never_served"],
            "loop": part["never_served_loop"],
            "entries": part["never_served_entries"],
        } for part in parts],
        "rows": rows,
        "summary": summary,
        "not_evidence": result_not_evidence(summary["verdict"]),
    })
    return body


def _fmt(value, digits=3):
    return "NA" if value is None else ("%.*f" % (digits, value))


def render(art: dict) -> str:
    s = art["summary"]
    p = s["primary"]
    b = s["base"]
    lines = [
        "# Retention entry-transition — result",
        "",
        "Generated from `%s` by `python -m benchmarks.retention_entry_transition --finish`. "
        "Do not edit by hand." % ARTIFACT.relative_to(ROOT),
        "",
        "**Verdict: `%s`.** The design was frozen in `%s` before this block ran."
        % (s["verdict"], block.PREREG.relative_to(ROOT)),
        "",
        "## Design",
        "",
        "- Seeds: **%s**." % ", ".join(str(seed) for seed in art["design"]["seeds"]),
        "- **%d** cycles, cap **%d**, structure-free through `f + %d`."
        % (art["design"]["cycles"], art["design"]["cap"],
           art["design"]["structure_free_through_offset"]),
        "- Outcome: the first sustained two-cycle structure entry at `f + %d` or later."
        % art["design"]["outcome_start_offset"],
        "- Final presence at cycle 120 is descriptive, not the event.",
        "",
        "**Model note.** %s" % art.get("model_note", MODEL_NOTE),
        "",
        "## Result",
        "",
    ]
    failed = [name for name, passed in s["gates"].items() if not passed]
    lines += [
        "| Quantity | Value |",
        "| --- | ---: |",
        "| Never-served edges | **%d** |" % s["n_never_served"],
        "| Loop-forming edges | **%d** |" % s["n_loop"],
        "| Structure-free edges | **%d** |" % s["n_structure_free"],
        "| Pre-entry presence excluded | **%d** |" % s["n_pre_entry_presence"],
        "| Eligible edges | **%d** |" % s["n_eligible"],
        "| Sustained entries | **%d** |" % s["n_events"],
        "| Final assertions (descriptive) | **%d** |" % s["n_final_assertion"],
        "| Fitted complete cases | **%d** |" % s["n_complete"],
        "| Early/proximal separation | %s |" % _fmt(s["separation"]),
    ]
    if p and b:
        lines += [
            "| Early-retention OR | **%.2f** (%.2f–%.2f) |" % (
                p["coefficients"]["early"]["odds_ratio"],
                p["coefficients"]["early"]["ci95"][0],
                p["coefficients"]["early"]["ci95"][1]),
            "| Proximal-retention OR | **%.2f** (%.2f–%.2f) |" % (
                p["coefficients"]["proximal"]["odds_ratio"],
                p["coefficients"]["proximal"]["ci95"][0],
                p["coefficients"]["proximal"]["ci95"][1]),
            "| Early-retention AUC | %s |" % _fmt(p["auc"]),
        ]
    else:
        lines += ["| Fit | %s |" % (s["fit_error"] or "not estimated")]
    if failed:
        lines += ["", "Failed gates: %s."
                  % ", ".join("`%s`" % name for name in failed)]
    lines += [
        "",
        "## Criteria",
        "",
        "| Criterion | Passes |",
        "| --- | --- |",
    ]
    for name, passed in s["criteria"].items():
        reading = "not read" if s["verdict"] == "VOID" else ("yes" if passed else "no")
        lines.append("| `%s` | %s |" % (name, reading))
    lines += ["", "## Gates", "", "| Gate | Passes |", "| --- | --- |"]
    for name, passed in s["gates"].items():
        lines.append("| `%s` | %s |" % (name, "yes" if passed else "no"))
    lines += ["", "## Per seed", "",
              "| Seed | Never served | Loop | Entries |", "| ---: | ---: | ---: | ---: |"]
    for row in art["seeds"]:
        lines.append("| %d | %d | %d | %d |" % (
            row["seed"], row["never_served"], row["loop"], row["entries"]))
    lines += ["", "## What this does and does not establish", "", art["not_evidence"], ""]
    return "\n".join(lines)


def _mark_run() -> None:
    """Record the run state in the frozen prereg, after all twenty-four parts exist."""
    doc = block.record()
    doc["status"] = "FROZEN, RUN"
    doc["runner"]["cells_run"] = len(planned())
    doc = engine_stamp.stamp(doc)
    block.PREREG.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    block.PAGE.write_text(block.render(doc), encoding="utf-8")


def finish() -> int:
    refuse()
    body = build()
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    _mark_run()
    s = body["summary"]
    payload = {"eligible": s["n_eligible"], "entries": s["n_events"],
               "complete": s["n_complete"]}
    if s["verdict"] == "VOID":
        payload["failed"] = [name for name, passed in s["gates"].items()
                             if not passed]
    else:
        payload["early"] = (round(s["primary"]["coefficients"]["early"]["odds_ratio"], 3)
                            if s["primary"] else None)
        payload["proximal"] = (round(s["primary"]["coefficients"]["proximal"]["odds_ratio"], 3)
                               if s["primary"] else None)
    print("retention entry-transition: %s %s" % (s["verdict"], json.dumps(payload)))
    return 0


def problems(art: dict | None = None) -> list[str]:
    art = json.loads(ARTIFACT.read_text(encoding="utf-8")) if art is None else art
    found = []
    if art.get("kind") != "retention_entry_transition":
        found.append("artifact kind")
    if art.get("status") != "RUN":
        found.append("artifact status")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    if art.get("prereg") != block.PREREG.relative_to(ROOT).as_posix():
        found.append("prereg path")
    found.extend(block._validate(block.record()))
    summary = _adjudicate(art.get("rows") or [])
    if art.get("summary") != summary:
        found.append("summary stale")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    return found


def check() -> int:
    if not ARTIFACT.exists():
        reasons = preflight()
        print("runner built; no result has been written")
        for reason in reasons:
            print("  -", reason)
        return 0
    found = problems()
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    s = json.loads(ARTIFACT.read_text(encoding="utf-8"))["summary"]
    print("retention entry-transition: %s" % s["verdict"])
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--cell", type=int)
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.dry_run:
        return dry_run()
    if args.cell is not None:
        return cell(args.cell, force=args.force)
    if args.measure:
        return measure(force=args.force)
    if args.finish:
        return finish()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
