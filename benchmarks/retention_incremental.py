"""CONFIRMATORY-RETENTION-INCREMENTAL-1: collection and adjudication runner.

The block is frozen and ungranted.  Every executing path calls ``refuse()``
before a scratch database is opened.  ``--dry-run`` prints the twelve commands
without touching a database; ``--cell`` and ``--measure`` refuse until the
record carries a complete dated grant.

Collection captures one row per never-served world edge with the cycle-60
landmark predictors and the first final-assertion cycle.  ``--finish`` reads the
twelve parts, fits the primary early-retention model and the reverse late-
retention model, applies the frozen gates and writes the result artifact.

    python -m benchmarks.retention_incremental --dry-run
    python -m benchmarks.retention_incremental --cell 20618101
    python -m benchmarks.retention_incremental --measure
    python -m benchmarks.retention_incremental --finish
    python -m benchmarks.retention_incremental --check
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
from benchmarks import retention_incremental_prereg as block
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

MODULE = "benchmarks.retention_incremental"
ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / ".scratch" / "retention_incremental" / "parts"
ARTIFACT = ROOT / "docs" / "retention_incremental.json"
PAGE = ROOT / "docs" / "RETENTION-INCREMENTAL.md"

PRIMARY = ("rank", "count", "formation", "strength", "early")
REVERSE = ("rank", "count", "formation", "strength", "late")


def planned() -> list[int]:
    return [int(seed) for seed in block.record()["design"]["seeds"]]


def command(seed: int) -> str:
    return "python -m %s --cell %d" % (MODULE, seed)


def dry_run() -> int:
    for seed in planned():
        print(command(seed))
    return 0


def preflight() -> list[str]:
    """Every reason a cell may not run. Read before any database is opened."""
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
    return found


def refuse() -> None:
    reasons = preflight()
    if reasons:
        print("REFUSED: CONFIRMATORY-RETENTION-INCREMENTAL-1 will not run:",
              file=sys.stderr)
        for reason in reasons:
            print("  -", reason, file=sys.stderr)
        raise SystemExit(2)


def part_path(seed: int) -> Path:
    return PARTS / ("%d.json" % seed)


def _counts(mem) -> dict[tuple[str, str], int]:
    return {(a, b): int(c) for a, b, c in
            mem._conn.execute("SELECT tag_from, tag_to, count FROM precedes")}


def _capture_seed(seed: int) -> dict:
    """Replay one seed and capture the landmark and final-assertion fields."""
    cycles = int(block.record()["design"]["cycles"])
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("retention_incremental_%d" % seed)
    mem = _CountingMemoryService(str(db_path))
    svc = RepairedObserverSleepService(mem, observe=True, cap=block.CAP)
    served = Counter()
    loop_cycles: dict[tuple[str, str], set[int]] = defaultdict(set)
    strengths: dict[tuple[str, str], list[tuple[int, float]]] = defaultdict(list)
    rank60: dict[tuple[str, str], int] = {}
    appearances: dict[tuple[str, str], list[int]] = defaultdict(list)
    counts60: dict[tuple[str, str], int] = {}
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
            if cycle <= block.LANDMARK:
                for row in (getattr(svc, "universe", [])[-1]
                            if getattr(svc, "universe", []) else []):
                    edge = tuple(row["edge"])
                    if edge in world_edges:
                        rank60[edge] = min(rank60.get(edge, int(row["rank"])),
                                          int(row["rank"]))
            current = {(a, b) for a, targets in
                       structure_edges(svc._load_prior_candidates()).items()
                       for b in targets}
            for edge in world_edges & current:
                appearances[edge].append(cycle)
            if cycle == block.LANDMARK:
                counts60 = _counts(mem)
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
        if formation is not None and formation <= block.LANDMARK:
            early_cycles = {c for c in observed if c <= block.LANDMARK}
            late_cycles = {c for c in observed if c > block.LANDMARK}
            early = len(early_cycles) / float(block.LANDMARK + 1 - formation)
            late = len(late_cycles) / float(block.CYCLES - block.LANDMARK)
        s60 = [s for c, s in strengths.get(edge, []) if c <= block.LANDMARK]
        s_late = [s for c, s in strengths.get(edge, []) if c > block.LANDMARK]
        first_assertion = (min(appearances[edge]) if edge in asserted
                           and appearances.get(edge) else None)
        rows.append({
            "seed": seed,
            "edge": "%s>%s" % edge,
            "asserted": edge in asserted,
            "assertion_cycle": first_assertion,
            "served_windows": int(served.get(edge, 0)),
            "ever_loop": bool(observed),
            "formation_cycle": formation,
            "loop_cycles": observed,
            "early_retention": early,
            "late_retention": late,
            "rank60": rank60.get(edge),
            "count60": int(counts60.get(edge, 0)),
            "strength60": max(s60) if s60 else 0.0,
            "late_strength": max(s_late) if s_late else 0.0,
            "direct_count_final": int(counts_final.get(edge, 0)),
        })
    return engine_stamp.stamp({
        "kind": "retention_incremental_cell",
        "prereg": block.ID,
        "seed": seed,
        "cycles": cycle,
        "cap": block.CAP,
        "world_edges": len(world_edges),
        "served_world_edges": sum(1 for edge in world_edges if served.get(edge, 0)),
        "asserted_world_edges": len(asserted),
        "never_served": len(rows),
        "never_served_asserted": sum(1 for row in rows if row["asserted"]),
        "rows": rows,
    })


def run_cell(seed: int) -> dict:
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
    return [json.loads(part_path(seed).read_text(encoding="utf-8"))
            for seed in planned()]


def _exp(value: float) -> float:
    """exp without raising when a separated Firth coefficient is very large."""
    if value > 709.0:
        return 1e308
    if value < -745.0:
        return 0.0
    return math.exp(value)


def _fit(rows: list[dict], predictors: tuple[str, ...],
         use_seeds: list[int] | None = None, with_loo: bool = True) -> dict:
    use_seeds = list(block.record()["design"]["seeds"]) if use_seeds is None else use_seeds
    data = [row for row in rows
            if row["seed"] in use_seeds and row.get("rank60") is not None]
    if not data:
        raise ValueError("empty fit population")
    raw = {
        "rank": [math.log2(float(row["rank60"])) for row in data],
        "count": [float(row["count60"]) for row in data],
        "formation": [float(row["formation_cycle"]) / float(block.CYCLES)
                      for row in data],
        "strength": [float(row["strength60"]) for row in data],
        "early": [float(row["early_retention"]) for row in data],
        "late": [float(row["late_retention"]) for row in data],
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
            and row["formation_cycle"] <= block.LANDMARK
            and row["early_retention"] is not None
            and (not row["asserted"]
                 or (row["assertion_cycle"] is not None
                     and row["assertion_cycle"] > block.LANDMARK))]


def _adjudicate(rows: list[dict]) -> dict:
    eligible = _eligible(rows)
    base = [row for row in eligible if row["rank60"] is not None]
    try:
        primary = _fit(base, PRIMARY)
        reverse = _fit(base, REVERSE)
        error = None
    except Exception as exc:
        primary = reverse = None
        error = type(exc).__name__ + ": " + str(exc)
    gates = {
        "M1_population": (
            len(eligible) >= block.MIN_EDGES
            and sum(1 for row in eligible if row["asserted"]) >= block.MIN_EVENTS
            and len({(row["seed"], row["edge"]) for row in eligible}) == len(eligible)
        ),
        "M2_landmark_complete": all(
            row["formation_cycle"] is not None
            and row["formation_cycle"] <= block.LANDMARK
            and row["early_retention"] is not None
            and not (row["asserted"]
                     and row["assertion_cycle"] is not None
                     and row["assertion_cycle"] <= block.LANDMARK)
            for row in eligible),
        "M3_rank_coverage": (len(base) / len(eligible) >= 0.95
                             if eligible else False),
        "M4_seed_levels": len({row["seed"] for row in base}) == len(planned()),
        "M5_convergence": bool(primary and reverse
                               and primary["converged"] and reverse["converged"]),
        "M6_complete": all(
            math.isfinite(float(row["count60"]))
            and math.isfinite(float(row["strength60"])) for row in base),
        "M7_reverse_onset": all(
            (row["asserted"] and row["assertion_cycle"] is not None
             and row["assertion_cycle"] > block.LANDMARK)
            or (not row["asserted"] and row["assertion_cycle"] is None)
            for row in eligible),
        "M8_no_collision": True,
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
        "primary": _summary(primary, PRIMARY) if primary else None,
        "reverse": _summary(reverse, REVERSE) if reverse else None,
        "gates": gates,
        "criteria": criteria,
        "verdict": verdict,
        "fit_error": error,
    }


def build() -> dict:
    parts = _load_parts()
    rows = [row for part in parts for row in part["rows"]]
    summary = _adjudicate(rows)
    body = engine_stamp.stamp({
        "kind": "retention_incremental",
        "status": "RUN",
        "prereg": block.PREREG.relative_to(ROOT).as_posix(),
        "question": block.record()["question"],
        "scope": (
            "Twelve fresh seeds, 120 cycles, cap 40, compositional world; "
            "cycle-60 landmark."
        ),
        "design": block.record()["design"],
        "model": block.record()["model"],
        "criteria": block.record()["criteria"],
        "gates": block.record()["gates"],
        "seeds": [{
            "seed": part["seed"],
            "never_served": part["never_served"],
            "asserted": part["never_served_asserted"],
        } for part in parts],
        "rows": rows,
        "summary": summary,
        "run_note": (
            "A preliminary collection stopped at 88-92 cycles for seven seeds "
            "because a withheld acquisition event at a block boundary skipped "
            "that sleep. The boundary was fixed, all twelve parts were regenerated "
            "at 120 cycles, and no preliminary part entered this result."
        ),
        "not_evidence": block.record()["not_evidence"],
    })
    return body


def _fmt(value, digits=3):
    return "NA" if value is None else ("%.*f" % (digits, value))


def _fmt_p(value):
    return "NA" if value is None else "%.2e" % value


def render(art: dict) -> str:
    s = art["summary"]
    p = s["primary"]
    r = s["reverse"]
    lines = [
        "# Retention incremental — result",
        "",
        "Generated from `%s` by `python -m benchmarks.retention_incremental --finish`. "
        "Do not edit by hand." % ARTIFACT.relative_to(ROOT),
        "",
        "**Verdict: `%s`.** The design was frozen in `%s` before this block ran."
        % (s["verdict"], block.PREREG.relative_to(ROOT)),
        "",
        "## Design",
        "",
        "- Seeds: **%s**." % ", ".join(str(seed) for seed in art["design"]["seeds"]),
        "- **%d** cycles, cap **%d**, cycle-60 landmark." % (
            art["design"]["cycles"], art["design"]["cap"]),
        "- Population: never-served loop-forming edges formed by 60 and not "
        "asserted by 60.",
        "- Primary: early retention, with rank, count, strength and formation "
        "measured through 60.",
        "- Reverse-time diagnostic: late retention over cycles 61-120.",
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
            "| Fitted complete cases | **%d** |" % s["n_complete"],
            "| Failed gates | %s |" % ", ".join("`%s`" % name for name in failed),
        ]
    elif p and r:
        lines += [
            "| Quantity | Primary | Reverse |",
            "| --- | ---: | ---: |",
            "| Eligible edges | **%d** | **%d** |" % (p["n"], r["n"]),
            "| Asserted events | **%d** | **%d** |" % (p["events"], r["events"]),
            "| Retention OR | **%.2f** | **%.2f** |" % (
                p["coefficients"]["early"]["odds_ratio"],
                r["coefficients"]["late"]["odds_ratio"]),
            "| Retention 95%% CI | %.2f–%.2f | %.2f–%.2f |" % (
                p["coefficients"]["early"]["ci95"][0],
                p["coefficients"]["early"]["ci95"][1],
                r["coefficients"]["late"]["ci95"][0],
                r["coefficients"]["late"]["ci95"][1]),
            "| AUC | %s | %s |" % (_fmt(p["auc"]), _fmt(r["auc"])),
            "| Brier | %s | %s |" % (_fmt(p["brier"], 4), _fmt(r["brier"], 4)),
        ]
    else:
        lines += ["| Fit | %s | — |" % (s["fit_error"] or "not estimated")]
    if s["verdict"] != "VOID":
        lines += [
            "",
            "The primary coefficient is early retention per 1 SD. A positive early "
            "result with a null late result is the temporal-order reading the block "
            "was designed to test. Both coefficients remain observational.",
        ]
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
    if art.get("run_note"):
        lines += ["", "## Run note", "", art["run_note"]]
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "A landmark model on one synthetic world family. It tests whether "
        "pre-assertion retention predicts final assertion beyond the measured "
        "controls. It does not establish a mechanism, a capability, transfer, or "
        "a general engine property. The reverse-time model is a diagnostic, not a "
        "second primary test.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def finish() -> int:
    body = build()
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    s = body["summary"]
    payload = {"eligible": s["n_eligible"], "events": s["n_events"]}
    if s["verdict"] == "VOID":
        payload["failed"] = [name for name, passed in s["gates"].items()
                             if not passed]
    else:
        payload["primary"] = (round(s["primary"]["coefficients"]["early"]["odds_ratio"], 3)
                              if s["primary"] else None)
        payload["reverse"] = (round(s["reverse"]["coefficients"]["late"]["odds_ratio"], 3)
                              if s["reverse"] else None)
    print("retention incremental: %s %s" % (s["verdict"], json.dumps(payload)))
    return 0


def problems(art: dict | None = None) -> list[str]:
    art = json.loads(ARTIFACT.read_text(encoding="utf-8")) if art is None else art
    found = []
    if art.get("kind") != "retention_incremental":
        found.append("artifact kind")
    if art.get("status") != "RUN":
        found.append("artifact status")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    if art.get("prereg") != block.PREREG.relative_to(ROOT).as_posix():
        found.append("prereg path")
    from benchmarks import retention_incremental_prereg as prereg
    found.extend(prereg._validate(prereg.record()))
    summary = _adjudicate(art.get("rows") or [])
    if art.get("summary") != summary:
        found.append("summary stale")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    return found


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no result; run --finish")
    found = problems()
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    s = json.loads(ARTIFACT.read_text(encoding="utf-8"))["summary"]
    print("retention incremental: %s" % s["verdict"])
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
