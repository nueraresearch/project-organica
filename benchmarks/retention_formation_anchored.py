"""CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1: collection and adjudication.

The block is frozen and ungranted.  Every executing path calls ``refuse()``
before a scratch database is opened.  ``--dry-run`` prints the twelve commands
without touching a database; ``--cell`` and ``--measure`` refuse until the
record carries a complete dated grant.

Collection captures one row per never-served world edge.  The predictor window
is the first twenty cycles from that edge's own first loop, through
``formation + 19``.  Edges that form after cycle 60 are admitted; the record's
M9 gate requires enough late-cohort edges and events before the late-forming
claim can be read.

    python -m benchmarks.retention_formation_anchored --dry-run
    python -m benchmarks.retention_formation_anchored --cell 20619101
    python -m benchmarks.retention_formation_anchored --measure
    python -m benchmarks.retention_formation_anchored --finish
    python -m benchmarks.retention_formation_anchored --check
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
from benchmarks import retention_formation_anchored_prereg as block
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.never_served_assertion_model import _auc, _fit_firth, _p_value, _sigmoid
from benchmarks.presence_construct_audit import (
    ACQ_SOURCE,
    PHASE_ACQUISITION,
    _world_compositional_edges,
)
from benchmarks.presence_conversion_repair_observer import RepairedObserverSleepService

MODULE = "benchmarks.retention_formation_anchored"
ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / ".scratch" / "retention_formation_anchored" / "parts"
ARTIFACT = ROOT / "docs" / "retention_formation_anchored.json"
PAGE = ROOT / "docs" / "RETENTION-FORMATION-ANCHORED.md"

PRIMARY = ("rank", "count", "strength", "followup", "early")
REVERSE = ("rank", "count", "strength", "followup", "late")
MODEL_NOTE = block.MODEL_NOTE
def result_not_evidence(verdict: str) -> str:
    if verdict == "VOID":
        return (
            "An observational formation-anchored landmark model on one synthetic "
            "world family.  The block is VOID on its own gates, so it establishes "
            "no retention, temporal-order, capability, causal or general engine "
            "property.  The zero-event or failed-gate population is a measurement "
            "about this design, not evidence that retention has no effect."
        )
    if verdict == "CONFIRMED, TEMPORALLY AMBIGUOUS":
        return (
            "An observational formation-anchored landmark model on one synthetic "
            "world family.  Early and post-landmark retention both carry positive "
            "associations, so this block does not establish that early retention "
            "precedes assertion.  It does not establish a mechanism, capability, "
            "transfer, causal effect, or general engine property."
        )
    return (
        "An observational formation-anchored landmark model on one synthetic "
        "world family.  It does not establish a mechanism, capability, transfer, "
        "causal effect, or general engine property."
    )


def planned() -> list[int]:
    return [int(seed) for seed in block.record()["design"]["seeds"]]


def command(seed: int) -> str:
    return "python -m %s --cell %d" % (MODULE, seed)


def dry_run() -> int:
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
        print("REFUSED: CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1 will not run:",
              file=sys.stderr)
        for reason in reasons:
            print("  -", reason, file=sys.stderr)
        raise SystemExit(2)


def part_path(seed: int) -> Path:
    return PARTS / ("%d.json" % seed)


def _post_landmark_onset(appearances: list[int], asserted: bool,
                         landmark: int | None) -> int | None:
    """First structure appearance strictly after the row's landmark."""
    if not asserted or landmark is None:
        return None
    later = [cycle for cycle in appearances if cycle > landmark]
    return min(later) if later else None


def _counts(mem) -> dict[tuple[str, str], int]:
    return {(a, b): int(c) for a, b, c in
            mem._conn.execute("SELECT tag_from, tag_to, count FROM precedes")}


def _capture_seed(seed: int) -> dict:
    """Replay one seed and capture formation-anchored predictor fields."""
    doc = block.record()
    cycles = int(doc["design"]["cycles"])
    window = int(doc["design"]["window_cycles"])
    max_formation = int(doc["design"]["max_formation_cycle"])
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("retention_formation_anchored_%d" % seed)
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

            # The repaired observer exposes the full pre-cap universe, one
            # entry per sleep.  Keep every rank in the edge's eventual window.
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

            # Counts are needed at each edge's landmark, which is not known
            # until its first loop.  Record the evolving count for every edge
            # that has looped at least once.
            counts_now = _counts(mem)
            for edge in loop_cycles:
                if edge in world_edges:
                    counts[edge][cycle] = int(counts_now.get(edge, 0))

        final = {(a, b) for a, targets in
                 structure_edges(svc._load_prior_candidates()).items()
                 for b in targets}
        counts_final = _counts(mem)
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    asserted = final & world_edges
    rows = []
    for edge in sorted(world_edges):
        if served.get(edge, 0):
            continue
        observed = sorted(loop_cycles.get(edge, set()))
        formation = observed[0] if observed else None
        early = None
        late = None
        followup = None
        rank20 = None
        count20 = None
        strength20 = 0.0
        late_strength = 0.0
        landmark = None
        if formation is not None:
            landmark = formation + window - 1
            in_window = [c for c in observed if formation <= c <= landmark]
            early = len(set(in_window)) / float(window)
            available = cycles - (formation + window) + 1
            after = [c for c in observed if formation + window <= c <= cycles]
            if available > 0:
                late = len(set(after)) / float(available)
                followup = available / float(cycles)
            rank_values = [ranks[edge][c] for c in range(formation, landmark + 1)
                           if c in ranks.get(edge, {})]
            rank20 = min(rank_values) if rank_values else None
            count20 = counts.get(edge, {}).get(landmark)
            window_strengths = [s for c, s in strengths.get(edge, [])
                                if formation <= c <= landmark]
            strength20 = max(window_strengths) if window_strengths else 0.0
            late_strengths = [s for c, s in strengths.get(edge, [])
                              if c > landmark]
            late_strength = max(late_strengths) if late_strengths else 0.0
        first_assertion = _post_landmark_onset(
            appearances.get(edge, []), edge in asserted, landmark)
        rows.append({
            "seed": seed,
            "edge": "%s>%s" % edge,
            "asserted": edge in asserted,
            "assertion_cycle": first_assertion,
            "first_structure_cycle": (
                min(appearances[edge]) if appearances.get(edge) else None),
            "served_windows": int(served.get(edge, 0)),
            "ever_loop": bool(observed),
            "formation_cycle": formation,
            "landmark_cycle": landmark,
            "loop_cycles": observed,
            "early_retention": early,
            "late_retention": late,
            "followup": followup,
            "rank20": rank20,
            "count20": count20,
            "strength20": strength20,
            "late_strength": late_strength,
            "direct_count_final": int(counts_final.get(edge, 0)),
        })
    return engine_stamp.stamp({
        "kind": "retention_formation_anchored_cell",
        "prereg": block.ID,
        "seed": seed,
        "cycles": cycle,
        "cap": block.CAP,
        "window_cycles": window,
        "max_formation_cycle": max_formation,
        "world_edges": len(world_edges),
        "served_world_edges": sum(1 for edge in world_edges if served.get(edge, 0)),
        "asserted_world_edges": len(asserted),
        "never_served": len(rows),
        "never_served_asserted": sum(1 for row in rows if row["asserted"]),
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
        print("collected %d: never-served %d, asserted %d"
              % (seed, part["never_served"], part["never_served_asserted"]))
    return 0


def _load_parts() -> list[dict]:
    missing = [seed for seed in planned() if not part_path(seed).exists()]
    if missing:
        raise SystemExit("missing parts: %r; run --measure" % missing)
    parts = []
    for seed in planned():
        part = json.loads(part_path(seed).read_text(encoding="utf-8"))
        if part.get("prereg") != block.ID or part.get("seed") != seed:
            raise SystemExit("part %d does not belong to this block" % seed)
        if part.get("cycles") != block.CYCLES or part.get("cap") != block.CAP:
            raise SystemExit("part %d has the wrong cycles or cap" % seed)
        parts.append(part)
    return parts


def _exp(value: float) -> float:
    """exp without raising when a separated Firth coefficient is very large."""
    if value > 709.0:
        return 1e308
    if value < -745.0:
        return 0.0
    return math.exp(value)


def _fit(rows: list[dict], predictors: tuple[str, ...],
         use_seeds: list[int] | None = None, with_loo: bool = True) -> dict:
    use_seeds = planned() if use_seeds is None else list(use_seeds)
    data = [row for row in rows
            if row["seed"] in use_seeds and row.get("rank20") is not None]
    if not data:
        raise ValueError("empty fit population")
    raw = {
        "rank": [math.log2(float(row["rank20"])) for row in data],
        "count": [float(row["count20"]) for row in data],
        "formation": [float(row["formation_cycle"]) / float(block.CYCLES)
                      for row in data],
        "strength": [float(row["strength20"]) for row in data],
        "followup": [float(row["followup"]) for row in data],
        "early": [float(row["early_retention"]) for row in data],
        "late": [float(row["late_retention"]) for row in data],
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
                fold = _fit(sub, predictors, [s for s in use_seeds if s != seed],
                            with_loo=False)
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
        "levels": levels,
        **{name: by_name[name] for name in predictors},
    }


def _summary(model: dict, predictors: tuple[str, ...]) -> dict:
    return {
        "n": model["n"],
        "events": model["events"],
        "converged": model["converged"],
        "coefficients": {name: model[name] for name in predictors},
        "auc": model["auc"] if math.isfinite(model["auc"]) else None,
        "brier": model["brier"],
        "average_marginal_effects": model["ame"],
        "leave_one_seed_out": model["loo"],
    }


def _eligible(rows: list[dict]) -> list[dict]:
    return [row for row in rows
            if row["ever_loop"]
            and row["formation_cycle"] is not None
            and row["formation_cycle"] <= block.MAX_FORMATION
            and row["early_retention"] is not None
            # Legacy parts predate first_structure_cycle. When the field is
            # present, a pre-landmark presence makes the row a re-entry, not a
            # true first post-landmark assertion.
            and (row.get("first_structure_cycle") is None
                 or row["first_structure_cycle"] > row["landmark_cycle"])
            and (not row["asserted"]
                 or (row["assertion_cycle"] is not None
                     and row["assertion_cycle"] > row["landmark_cycle"]))]


def _finite_coefficients(model: dict) -> bool:
    return all(math.isfinite(float(coef["beta"]))
               and math.isfinite(float(coef["se"]))
               for coef in model["coefficients"])


def _adjudicate(rows: list[dict]) -> dict:
    eligible = _eligible(rows)
    base = [row for row in eligible if row["rank20"] is not None]
    late_eligible = [row for row in eligible
                     if row["formation_cycle"] > block.LATE_AFTER]
    late = [row for row in base if row["formation_cycle"] > block.LATE_AFTER]
    try:
        primary = _fit(base, PRIMARY)
        reverse = _fit(base, REVERSE)
        error = None
    except Exception as exc:
        primary = reverse = None
        error = type(exc).__name__ + ": " + str(exc)
    late_model = None
    late_error = None
    late_seeds = sorted({row["seed"] for row in late})
    if late_seeds:
        try:
            late_model = _fit(late, PRIMARY, use_seeds=late_seeds, with_loo=False)
        except Exception as exc:
            late_error = type(exc).__name__ + ": " + str(exc)

    gates = {
        "M1_population": (
            len(eligible) >= block.MIN_EDGES
            and sum(1 for row in eligible if row["asserted"]) >= block.MIN_EVENTS
            and len({(row["seed"], row["edge"]) for row in eligible}) == len(eligible)
        ),
        "M2_window_complete": all(
            row["formation_cycle"] is not None
            and row["formation_cycle"] <= block.MAX_FORMATION
            and row["landmark_cycle"] == row["formation_cycle"] + block.WINDOW - 1
            and row["landmark_cycle"] <= block.CYCLES
            and math.isfinite(float(row["early_retention"]))
            and not (row["asserted"]
                     and row["assertion_cycle"] is not None
                     and row["assertion_cycle"] <= row["landmark_cycle"])
            for row in eligible),
        "M3_rank_coverage": (len(base) / len(eligible) >= 0.95
                             if eligible else False),
        "M4_seed_levels": len({row["seed"] for row in base}) == len(planned()),
        "M5_convergence": bool(primary and reverse
                               and primary["converged"] and reverse["converged"]
                               and _finite_coefficients(primary)
                               and _finite_coefficients(reverse)),
        "M6_complete": all(
            math.isfinite(float(row["count20"]))
            and math.isfinite(float(row["strength20"]))
            and math.isfinite(float(row["followup"])) for row in base),
        "M7_reverse_onset": all(
            (row["asserted"] and row["assertion_cycle"] is not None
             and row["assertion_cycle"] > row["landmark_cycle"])
            or (not row["asserted"] and row["assertion_cycle"] is None)
            for row in eligible),
        "M8_no_collision": True,
        "M9_late_representation": (
            len(late_eligible) >= block.MIN_LATE_EDGES
            and sum(1 for row in late_eligible if row["asserted"])
            >= block.MIN_LATE_EVENTS
        ),
    }
    try:
        from benchmarks.presence_cap_experiment import seed_collisions
        gates["M8_no_collision"] = not seed_collisions(
            planned(), allow=(block.PREREG, block.RESULT))
    except Exception:
        gates["M8_no_collision"] = False
    if error or primary is None or reverse is None:
        criteria = {"P1": False, "P2": False, "P3": False, "R1": False}
        verdict = "VOID"
    else:
        p1 = primary["early"]["odds_ratio"] > 1.0
        p2 = primary["early"]["ci95"][0] > 1.0
        p3 = all(gates.values())
        r1 = (reverse["late"]["odds_ratio"] <= 1.0
              or reverse["late"]["ci95"][0] <= 1.0)
        criteria = {"P1": p1, "P2": p2, "P3": p3, "R1": r1}
        if not p3:
            verdict = "VOID"
        elif p1 and p2 and r1:
            verdict = "CONFIRMED"
        elif p1 and p2 and not r1:
            verdict = "CONFIRMED, TEMPORALLY AMBIGUOUS"
        elif p1:
            verdict = "DIRECTIONAL ONLY"
        else:
            verdict = "NOT CONFIRMED"
    return {
        "n_never_served": len(rows),
        "n_loop": sum(1 for row in rows if row["ever_loop"]),
        "n_eligible": len(eligible),
        "n_complete": len(base),
        "n_events": sum(1 for row in eligible if row["asserted"]),
        "n_late_edges": len(late_eligible),
        "n_late_events": sum(1 for row in late_eligible if row["asserted"]),
        "primary": _summary(primary, PRIMARY) if primary else None,
        "reverse": _summary(reverse, REVERSE) if reverse else None,
        "reverse_boundary": {
            "late_zero_edges": sum(1 for row in base
                                   if float(row["late_retention"]) == 0.0),
            "late_zero_events": sum(1 for row in base
                                    if float(row["late_retention"]) == 0.0
                                    and row["asserted"]),
            "late_mid_edges": sum(1 for row in base
                                  if 0.0 < float(row["late_retention"]) < 1.0),
            "late_mid_events": sum(1 for row in base
                                   if 0.0 < float(row["late_retention"]) < 1.0
                                   and row["asserted"]),
            "late_one_edges": sum(1 for row in base
                                  if float(row["late_retention"]) == 1.0),
            "late_one_events": sum(1 for row in base
                                   if float(row["late_retention"]) == 1.0
                                   and row["asserted"]),
        },
        "late_cohort": _summary(late_model, PRIMARY) if late_model else None,
        "late_cohort_error": late_error,
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
        "kind": "retention_formation_anchored",
        "status": "RUN",
        "prereg": block.PREREG.relative_to(ROOT).as_posix(),
        "question": doc["question"],
        "scope": (
            "Twelve fresh seeds, 120 cycles, cap 40, compositional world; "
            "per-edge 20-cycle predictor window from formation through "
            "formation + 19; formation ceiling 90."
        ),
        "design": doc["design"],
        "model": doc["model"],
        "model_note": MODEL_NOTE,
        "criteria": doc["criteria"],
        "gates": doc["gates"],
        "seeds": [{
            "seed": part["seed"],
            "never_served": part["never_served"],
            "asserted": part["never_served_asserted"],
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
    r = s["reverse"]
    late = s["late_cohort"]
    lines = [
        "# Retention formation-anchored — result",
        "",
        "Generated from `%s` by `python -m benchmarks.retention_formation_anchored --finish`. "
        "Do not edit by hand." % ARTIFACT.relative_to(ROOT),
        "",
        "**Verdict: `%s`.** The design was frozen in `%s` before this block ran."
        % (s["verdict"], block.PREREG.relative_to(ROOT)),
        "",
        "## Design",
        "",
        "- Seeds: **%s**." % ", ".join(str(seed) for seed in art["design"]["seeds"]),
        "- **%d** cycles, cap **%d**, per-edge **%d**-cycle window."
        % (art["design"]["cycles"], art["design"]["cap"],
           art["design"]["window_cycles"]),
        "- Population: never-served loop-forming edges with "
        "`formation_cycle <= %d` that were not asserted in their window."
        % art["design"]["max_formation_cycle"],
        "- Primary: early retention over the first twenty cycles, with rank20, "
        "count20, strength20 and the follow-up horizon control; formation is "
        "descriptive.",
        "",
        "**Model identification note.** %s" % art.get("model_note", ""),
        "- Late cohort: edges with formation after cycle %d."
        % art["design"]["late_formation_after"],
        "",
        "## Result",
        "",
    ]
    failed = [name for name, passed in s["gates"].items() if not passed]
    if s["verdict"] == "VOID":
        lines += [
            "**VOID: no coefficient is read.** The pre-registered gates failed: "
            "%s." % ", ".join("`%s`" % name for name in failed),
            "",
            "| Quantity | Value |",
            "| --- | ---: |",
            "| Never-served edges | **%d** |" % s["n_never_served"],
            "| Loop-forming edges | **%d** |" % s["n_loop"],
            "| Eligible edges | **%d** |" % s["n_eligible"],
            "| Asserted events | **%d** |" % s["n_events"],
            "| Late-cohort edges | **%d** |" % s["n_late_edges"],
            "| Late-cohort events | **%d** |" % s["n_late_events"],
            "| Fitted complete cases | **%d** |" % s["n_complete"],
            "| Failed gates | %s |" % ", ".join("`%s`" % name for name in failed),
        ]
    elif p and r:
        lines += [
            "| Quantity | Primary | Reverse |",
            "| --- | ---: | ---: |",
            "| Eligible edges | **%d** | **%d** |" % (
                s["n_eligible"], s["n_eligible"]),
            "| Fitted complete cases | **%d** | **%d** |" % (p["n"], r["n"]),
            "| Asserted events | **%d** | **%d** |" % (p["events"], r["events"]),
            "| Retention OR | **%.2f** | **%.2f** |" % (
                p["coefficients"]["early"]["odds_ratio"],
                r["coefficients"]["late"]["odds_ratio"]),
            "| Retention 95%% CI | %.2f–%.2f | %.2f–%.2f |" % (
                p["coefficients"]["early"]["ci95"][0],
                p["coefficients"]["early"]["ci95"][1],
                r["coefficients"]["late"]["ci95"][0],
                r["coefficients"]["late"]["ci95"][1]),
            "| Late-retention boundary | — | **%d/%d** at 0.0; **%d/%d** in between; **%d/%d** at 1.0 |" % (
                s["reverse_boundary"]["late_zero_events"],
                s["reverse_boundary"]["late_zero_edges"],
                s["reverse_boundary"]["late_mid_events"],
                s["reverse_boundary"]["late_mid_edges"],
                s["reverse_boundary"]["late_one_events"],
                s["reverse_boundary"]["late_one_edges"]),
            "| AUC | %s | %s |" % (_fmt(p["auc"]), _fmt(r["auc"])),
            "| Brier | %s | %s |" % (_fmt(p["brier"], 4), _fmt(r["brier"], 4)),
        ]
    else:
        lines += ["| Fit | %s | — |" % (s["fit_error"] or "not estimated")]
    if s["verdict"] == "CONFIRMED, TEMPORALLY AMBIGUOUS":
        lines += [
            "",
            "The primary coefficient is early retention per 1 SD. Post-landmark "
            "retention also has a positive association, so the block cannot "
            "separate early timing from concurrent or reverse timing. The "
            "reverse OR is a boundary contrast, not a dose-response: **%d/%d** "
            "edges at late retention 0.0 were asserted, **%d/%d** in between, "
            "against **%d/%d** at 1.0. Both coefficients remain observational." % (
                s["reverse_boundary"]["late_zero_events"],
                s["reverse_boundary"]["late_zero_edges"],
                s["reverse_boundary"]["late_mid_events"],
                s["reverse_boundary"]["late_mid_edges"],
                s["reverse_boundary"]["late_one_events"],
                s["reverse_boundary"]["late_one_edges"]),
        ]
    elif s["verdict"] != "VOID":
        lines += [
            "",
            "The primary coefficient is early retention per 1 SD. Both "
            "coefficients remain observational.",
        ]
    if late and s["verdict"] != "VOID":
        lines += [
            "",
            "## Late cohort",
            "",
            "The late cohort is reported descriptively; it does not replace the "
            "all-cohort primary or M9.",
            "",
            "| Quantity | Late cohort |",
            "| --- | ---: |",
            "| Edges | **%d** |" % late["n"],
            "| Asserted events | **%d** |" % late["events"],
            "| Early-retention OR | **%.2f** |"
            % late["coefficients"]["early"]["odds_ratio"],
            "| Early-retention 95%% CI | %.2f–%.2f |" % (
                late["coefficients"]["early"]["ci95"][0],
                late["coefficients"]["early"]["ci95"][1]),
        ]
    elif s["late_cohort_error"] and s["verdict"] != "VOID":
        lines += ["", "## Late cohort", "",
                  "The late-cohort model was not estimated: `%s`."
                  % s["late_cohort_error"]]
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
    lines += [
        "",
        "## Gates",
        "",
        "| Gate | Passes |",
        "| --- | --- |",
    ]
    for name, passed in s["gates"].items():
        lines.append("| `%s` | %s |" % (name, "yes" if passed else "no"))
    lines += ["", "## Per seed", "",
              "| Seed | Never served | Asserted |", "| ---: | ---: | ---: |"]
    for row in art["seeds"]:
        lines.append("| %d | %d | %d |" % (
            row["seed"], row["never_served"], row["asserted"]))
    if p and r and s["verdict"] != "VOID":
        lines += ["", "## Leave-one-seed-out sensitivity", "",
                  "| Held out | Early beta | Late beta |",
                  "| ---: | ---: | ---: |"]
        for left, right in zip(p["leave_one_seed_out"], r["leave_one_seed_out"]):
            lines.append("| %s | %s | %s |" % (
                left["held_out"], _fmt(left.get("early")), _fmt(right.get("late"))))
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "A formation-anchored landmark model on one synthetic world family. It "
        "tests whether early retention predicts assertion beyond the measured "
        "controls, including among edges that form late. It does not establish a "
        "mechanism, a capability, transfer, or a general engine property. The "
        "reverse-time model is a diagnostic, not a second primary test.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def _mark_run() -> None:
    """Record the run state in the frozen prereg, after all twelve parts exist."""
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
    payload = {"eligible": s["n_eligible"], "events": s["n_events"],
               "late_edges": s["n_late_edges"], "late_events": s["n_late_events"]}
    if s["verdict"] == "VOID":
        payload["failed"] = [name for name, passed in s["gates"].items()
                             if not passed]
    else:
        payload["primary"] = (round(s["primary"]["coefficients"]["early"]["odds_ratio"], 3)
                              if s["primary"] else None)
        payload["reverse"] = (round(s["reverse"]["coefficients"]["late"]["odds_ratio"], 3)
                              if s["reverse"] else None)
    print("retention formation-anchored: %s %s"
          % (s["verdict"], json.dumps(payload)))
    return 0


def problems(art: dict | None = None) -> list[str]:
    art = json.loads(ARTIFACT.read_text(encoding="utf-8")) if art is None else art
    found = []
    if art.get("kind") != "retention_formation_anchored":
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
        if reasons:
            print("runner ready, but the block will not run:")
            for reason in reasons:
                print("  -", reason)
            return 0
        print("runner ready; no result has been written")
        return 0
    found = problems()
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    s = json.loads(ARTIFACT.read_text(encoding="utf-8"))["summary"]
    print("retention formation-anchored: %s" % s["verdict"])
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
