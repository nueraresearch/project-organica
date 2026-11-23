"""Confirmation harness for Option 2r: degree worlds, sealed calibration,
held-out cells, and the conjunctive decision.

The protocol is `docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md` as amended by
its sections 13–17.  Nothing here changes the engine: the shipped arm is
`SleepService`; the candidate arms are harness subclasses — a ratio-strength
threshold control and the transition-probability arm — and neither changes an
engine file.

Subcommands:

    audit       realised out-degree of every degree world, and the tag-length
                check (rule 9); no engine runs
    calibrate   threshold grid on the calibration seed block; writes a sealed
                artifact and refuses to seal an incomplete protocol run
    heldout     stationary, shift and task cells on the held-out seed block;
                reads `tau*` from the seal and never recomputes it
    analyze     the conjunctive decision, with every condition reported

The harness is built to fail: calibration returns `None` when no threshold
clears every degree regime, the decision returns a named rejection label rather
than a weak pass, and `--smoke` artifacts are marked `"protocol": false` so they
cannot be quoted as a verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.heldout_prediction import (  # noqa: E402
    DECAY_HALF_LIFE_CYCLES, TEST_CYCLES, TRAIN_CYCLES,
    _probability, _score, _transition_counts,
)
from organica.memory import MemoryService, _extract_tags    # noqa: E402
from organica.paths import temp_db                          # noqa: E402
from organica.scale_streams import expanding_triangles, scale_stream  # noqa: E402
from organica.sleep import SleepService                     # noqa: E402
from organica.streams import EVENTS_PER_CYCLE               # noqa: E402
from benchmarks import engine_stamp

# Regimes are measured hub out-degrees.  Each triangle contributes two hub
# targets through the engine's lookback, so only even degrees are constructible
# in this world family.
DEGREES = (2, 4, 6, 12)
CALIBRATION_SEEDS = tuple(range(20300101, 20300109))
HELDOUT_SEEDS = tuple(range(20300109, 20300129))
GRID = (0.05, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30)
CYCLES = 300
SHIFT_A = 80
SHIFT_B = 40
SHIFT_DEGREES = (4, 12)
ARMS = ("shipped", "ratio", "transition")
MARKERS = 7
LOOKBACK = 3
MIN_STABLE_FOR_PRECISION = 40
PRECISION_FLOOR = 0.95
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20261023
CONFIRMATION_DIR = REPO / "docs" / "confirmation"
SMOKE_DIR = REPO / ".scratch" / "confirmation"


# ---------------------------------------------------------------------------
# Worlds and the design audit
# ---------------------------------------------------------------------------

def degree_world(degree: int, prefix: str = "") -> list[str]:
    """A hub with a **measured** out-degree of `degree` (even degrees only).

    `scale_stream` emits `h a`, `a b`, `b h` per triangle, and the 3-event
    lookback records hub->leafA and hub->leafB, so one triangle contributes two
    hub targets: `degree // 2` triangles are emitted.  An odd target degree is
    not constructible here and is rejected rather than silently rounded.
    """
    if degree < 2 or degree % 2:
        raise ValueError("degree worlds are even hub out-degrees, got %r" % (degree,))
    triangles = expanding_triangles(degree // 2, hub="alpha")
    events = scale_stream(triangles, mode="block", block_repeat=4)
    if prefix:
        events = [" ".join(prefix + tok for tok in event.split()) for event in events]
    return events


def world_edges(events: list[str]) -> set[tuple[str, str]]:
    """Directed tag pairs the stimulus presents, by the engine's lookback rule."""
    tags = [_extract_tags(text) for text in events]
    edges: set[tuple[str, str]] = set()
    for i in range(1, len(events)):
        current = tags[i]
        prior = {t for j in range(max(0, i - LOOKBACK), i) for t in tags[j]}
        for src in prior:
            for tgt in current:
                if src != tgt:
                    edges.add((src, tgt))
    return edges


def realised_out_degree(events: list[str], hub: str = "alpha") -> int:
    return len({tgt for src, tgt in world_edges(events) if src == hub})


def audit_worlds(degrees=DEGREES) -> dict:
    """Every degree world must have the degree it claims and tags of >= 4 letters."""
    problems, rows = [], []
    for degree in degrees:
        events = degree_world(degree)
        tags = {tag for event in events for tag in _extract_tags(event)}
        short = sorted(tag for tag in tags if len(tag) < 4)
        measured = realised_out_degree(events)
        rows.append({"degree": degree, "realised": measured,
                     "tags": len(tags), "short_tags": short})
        if measured != degree:
            problems.append("%d: realised out-degree %d" % (degree, measured))
        if short:
            problems.append("%d: short tags %s" % (degree, short))
    return {"ok": not problems, "problems": problems, "worlds": rows}


# ---------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------

class Counted(SleepService):
    """Counts the layers the liveness gate reads."""

    def __init__(self, memory):
        super().__init__(memory)
        self.theories = 0
        self.beliefs = 0

    def _form_and_test_hypotheses(self, *args, **kwargs):
        out = super()._form_and_test_hypotheses(*args, **kwargs)
        items = out[0] if isinstance(out, tuple) else out
        self.beliefs = max(0, len(items) - MARKERS)
        return out

    def _form_theories_and_questions(self, *args, **kwargs):
        out = super()._form_theories_and_questions(*args, **kwargs)
        self.theories = len(out[0]) if isinstance(out, tuple) else 0
        return out


class Ratio(Counted):
    """The shipped strength formula with a calibrated threshold.

    The threshold control: same formula as the engine, its own threshold
    selected by the same rule on the same seeds, so a gain the formula alone
    can produce is visible instead of being credited to the formula change.
    """

    def __init__(self, memory, tau: float):
        super().__init__(memory)
        self.STABLE_THRESHOLD = float(tau)


class Shipped(Ratio):
    """The engine as committed: ratio strength at STABLE_THRESHOLD = 0.30."""

    def __init__(self, memory):
        super().__init__(memory, 0.30)


class Transition(Counted):
    """Option 2r: strength = the engine's own transition_prob, threshold tau."""

    def __init__(self, memory, tau: float):
        super().__init__(memory)
        self.STABLE_THRESHOLD = float(tau)

    def _build_predictions(self, temporal, freqs):
        out = super()._build_predictions(temporal, freqs)
        for cand in out:
            cand.strength = min(1.0, float(cand.evidence.get("transition_prob", 0.0)))
        return out


def build_arm(arm: str, tau):
    if arm == "shipped":
        return Shipped
    if arm == "ratio":
        return lambda memory: Ratio(memory, tau)
    if arm == "transition":
        return lambda memory: Transition(memory, tau)
    raise ValueError("unknown arm %r" % (arm,))


# ---------------------------------------------------------------------------
# One cell
# ---------------------------------------------------------------------------

def _stable(service) -> list[tuple[str, str]]:
    edges = []
    for cand in service._load_prior_candidates():
        if cand.get("type") != "prediction_candidate":
            continue
        src, tgt = cand.get("source"), cand.get("target")
        strength = float(cand.get("confidence") or cand.get("strength") or 0.0)
        if src and tgt and strength >= service.STABLE_THRESHOLD:
            edges.append((src, tgt))
    return edges


def _feed(memory, events, cycle):
    start = (cycle * EVENTS_PER_CYCLE) % len(events)
    for text in events[start:start + EVENTS_PER_CYCLE]:
        memory.store(text, event_type="event", source=f"cycle:{cycle}")


def _open(arm, tau, events, seed):
    db = temp_db("confirm_%s_%s_%s.db" % (arm, tau if tau is not None else "shipped", seed))
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = build_arm(arm, tau)(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    for text in events[:EVENTS_PER_CYCLE]:
        memory.store(text, event_type="event", source="seed:bootstrap")
    return db, memory, service


def stationary_cell(arm: str, tau, degree: int, seed: int,
                    cycles: int = CYCLES) -> dict:
    events = degree_world(degree)
    world = world_edges(events)
    db, memory, service = _open(arm, tau, events, seed)
    theory_counts, belief_counts = [], []
    try:
        for cycle in range(cycles):
            _feed(memory, events, cycle)
            service.run_sleep_cycle()
            stable = _stable(service)
            hit = [edge for edge in stable if edge in world]
            theory_counts.append(service.theories)
            belief_counts.append(service.beliefs)
            last = {
                "stable": len(stable),
                "precision": (len(hit) / len(stable)) if stable else None,
                "coverage": (len(hit) / len(world)) if world else None,
                "false_assertions": len(stable) - len(hit),
            }
    finally:
        memory.close()
        db.unlink(missing_ok=True)
    tail = theory_counts[-max(1, cycles // 10):]
    beliefs_tail = belief_counts[-max(1, cycles // 10):]
    return {
        "kind": "stationary", "arm": arm, "tau": tau, "degree": degree,
        "seed": seed, "cycles": cycles,
        "world_edges": len(world),
        "liveness": bool(min(tail) >= 1 and sum(beliefs_tail) / len(beliefs_tail) >= 2),
        "theories_final": theory_counts[-1],
        "beliefs_tail_mean": round(sum(beliefs_tail) / len(beliefs_tail), 3),
        "stable_final": last["stable"], "precision": last["precision"],
        "coverage": last["coverage"],
        "false_assertions": last["false_assertions"],
        "theory_counts": theory_counts,
    }


def shift_cell(arm: str, tau, degree: int, seed: int) -> dict:
    events_a = degree_world(degree)
    events_b = degree_world(degree, prefix="z")
    world_a, world_b = world_edges(events_a), world_edges(events_b)
    db, memory, service = _open(arm, tau, events_a, seed)
    rows = []
    try:
        for cycle in range(SHIFT_A + SHIFT_B):
            stream = events_a if cycle < SHIFT_A else events_b
            _feed(memory, stream, cycle)
            service.run_sleep_cycle()
            stable = _stable(service)
            b_hit = [edge for edge in stable if edge in world_b]
            a_hit = [edge for edge in stable if edge in world_a]
            rows.append({
                "stable": len(stable),
                "b_coverage": round(len(b_hit) / len(world_b), 4),
                "a_share": (len(a_hit) / len(stable)) if stable else None,
            })
    finally:
        memory.close()
        db.unlink(missing_ok=True)
    return {
        "kind": "shift", "arm": arm, "tau": tau, "degree": degree, "seed": seed,
        "b_coverage_final": rows[-1]["b_coverage"],
        "b_coverage_at_shift": rows[SHIFT_A - 1]["b_coverage"],
        "a_share_final": rows[-1]["a_share"],
        "theories_final": service.theories,
    }


def task_cell(arm: str, tau, degree: int, seed: int) -> dict:
    """Frozen-model held-out next-tag log-loss, on this degree world.

    Reuses the held-out instrument's own scoring functions and smoothing so the
    endpoint is the same quantity; only the world is the degree world rather
    than the rung-0 burst curriculum.  The preregistration's amendment records
    that substitution.
    """
    events = degree_world(degree)
    need = (TRAIN_CYCLES + TEST_CYCLES) * EVENTS_PER_CYCLE
    stream = [events[i % len(events)] for i in range(need)]
    cut = TRAIN_CYCLES * EVENTS_PER_CYCLE
    train_stream, test_stream = stream[:cut], stream[cut:]
    bootstrap = events[:EVENTS_PER_CYCLE]
    train_history = bootstrap + train_stream
    vocabulary = {tag for event in train_history for tag in _extract_tags(event)}

    db, memory, service = _open(arm, tau, events, seed)
    try:
        for cycle in range(TRAIN_CYCLES):
            chunk = train_stream[cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]
            for text in chunk:
                memory.store(text, event_type="event", source=f"cycle:{cycle}")
            report = service.run_sleep_cycle()
        strengths = {(p.source, p.target): float(p.strength)
                     for p in (report.predictions if report else [])}
    finally:
        memory.close()
        db.unlink(missing_ok=True)

    evaluation = train_stream[-1:] + test_stream
    contexts = [_extract_tags(e) for e in evaluation[:-1]]
    observations = [_extract_tags(e) for e in evaluation[1:]]

    organica = _score("organica", lambda a, b: strengths.get((a, b), 0.0),
                      contexts, observations, vocabulary)
    markov_pos, markov_exp = _transition_counts(train_history)
    markov = _score("markov", lambda a, b: _probability(markov_pos, markov_exp, a, b),
                    contexts, observations, vocabulary)
    decay_pos, decay_exp = _transition_counts(
        train_history, window=1,
        half_life_events=DECAY_HALF_LIFE_CYCLES * EVENTS_PER_CYCLE)
    decayed = _score("decayed", lambda a, b: _probability(decay_pos, decay_exp, a, b),
                     contexts, observations, vocabulary)
    baselines = [m["log_loss"] for m in (markov, decayed) if m["log_loss"] is not None]
    return {
        "kind": "task", "arm": arm, "tau": tau, "degree": degree, "seed": seed,
        "log_loss": organica["log_loss"],
        "best_baseline_log_loss": min(baselines) if baselines else None,
        "brier": organica["brier"],
    }


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

def choose_threshold(cells: list[dict]) -> dict:
    """The section 3 rule: highest mean coverage among thresholds that pass
    liveness and keep precision >= 0.95 on EVERY calibration cell."""
    passing, rejected = {}, {}
    for tau in sorted({c["tau"] for c in cells}):
        rows = [c for c in cells if c["tau"] == tau]
        if not rows:
            continue
        failures = []
        for row in rows:
            if not row["liveness"]:
                failures.append("d%d s%d: not live" % (row["degree"], row["seed"]))
            elif row["precision"] is None or row["precision"] < PRECISION_FLOOR:
                failures.append("d%d s%d: precision %s" % (row["degree"], row["seed"],
                                                           row["precision"]))
        if failures:
            rejected[str(tau)] = failures[:3]
            continue
        passing[tau] = statistics.mean(r["coverage"] for r in rows)
    if not passing:
        return {"tau_star": None, "reason": "no global threshold clears all degree regimes",
                "passing": {}, "rejected": rejected}
    best = max(passing.values())
    winners = [tau for tau, value in passing.items() if abs(value - best) < 1e-12]
    tau_star = max(winners)          # tie-break toward the larger, more conservative tau
    return {"tau_star": tau_star, "coverage": round(best, 4),
            "passing": {str(k): round(v, 4) for k, v in passing.items()},
            "rejected": rejected, "reason": "highest mean coverage among passing thresholds"}


def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def seal(payload: dict, path: Path) -> dict:
    # The stamp is part of the sealed content. A seal that covers less than is written verifies a
    # file that no longer exists, so the record is stamped first and the stamp is hashed with it.
    sealed = engine_stamp.stamp(dict(payload))
    sealed["sha256"] = hashlib.sha256(_canonical(sealed)).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sealed, indent=1), encoding="utf-8")
    return sealed


def _read_artifact(path: Path, what: str, require_cells: bool = False) -> dict:
    """A missing or malformed artifact is a usage error, not a traceback."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit("no %s at %s" % (what, path))
    except OSError as error:
        raise SystemExit("%s: %s" % (path, error))
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise SystemExit("%s is not JSON: %s" % (path, error))
    if not isinstance(payload, dict):
        raise SystemExit("%s is not an artifact object" % path)
    if require_cells and not isinstance(payload.get("cells"), list):
        raise SystemExit("%s carries no cell list; is it a %s?" % (path, what))
    return payload


def verify_seal(path: Path) -> dict:
    payload = _read_artifact(path, "artifact")
    recorded = payload.pop("sha256", None)
    actual = hashlib.sha256(_canonical(payload)).hexdigest()
    if recorded != actual:
        raise SystemExit("%s: seal mismatch (recorded %s, computed %s)"
                         % (path, recorded, actual))
    payload["sha256"] = recorded
    return payload


# ---------------------------------------------------------------------------
# Seeds and the decision
# ---------------------------------------------------------------------------

def harvest_seeds(directory: Path = REPO / "docs") -> set[int]:
    """Every integer under a key naming a seed, in every JSON directly under docs."""
    found: set[int] = set()

    def ints(value):
        if isinstance(value, int):
            found.add(value)
        elif isinstance(value, list):
            for item in value:
                ints(item)
        elif isinstance(value, dict):
            for item in value.values():
                ints(item)

    for path in sorted(directory.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        def walk(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if "seed" in key.lower():
                        ints(value)
                    else:
                        walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(doc)
    return found


def paired_interval(diffs: list[float], level: float = 0.99,
                    reps: int = BOOTSTRAP_REPLICATES) -> tuple[float, float] | None:
    if len(diffs) < 2:
        return None
    rng = random.Random(BOOTSTRAP_SEED)
    means = []
    n = len(diffs)
    for _ in range(reps):
        means.append(sum(diffs[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    lo = means[int((1 - level) / 2 * reps)]
    hi = means[int((1 + level) / 2 * reps) - 1]
    return lo, hi


def _by(cells, kind, arm, degree):
    return [c for c in cells if c.get("kind") == kind and c.get("arm") == arm
            and c.get("degree") == degree]


def _live_rate(cells) -> float | None:
    return (sum(1 for c in cells if c["liveness"]) / len(cells)) if cells else None


def decide(cells, calibration=None, reps=BOOTSTRAP_REPLICATES):
    """The amended conjunctive rule over three arms.

    S = shipped ratio at 0.30, R = ratio at its calibrated threshold (the
    threshold control), T = transition probability at its calibrated threshold.
    Adoption needs T to beat R, not merely S, so a threshold-only gain cannot be
    credited to the formula.
    """
    conditions = {}
    arms = ("shipped", "ratio", "transition")

    live = {arm: {d: _live_rate(_by(cells, "stationary", arm, d)) for d in DEGREES}
            for arm in arms}

    conditions["1_comparability"] = {
        "live_rate": live,
        "required": "ratio and transition >= 0.9 at 2, 4, 6; shipped >= 0.9 at 2, 4",
        "ok": (all((live[a][d] or 0) >= 0.9 for a in ("ratio", "transition")
                   for d in (2, 4, 6))
               and all((live["shipped"][d] or 0) >= 0.9 for d in (2, 4))),
        "note": "the candidate's degree-12 liveness is judged by condition 2",
    }

    d12 = _by(cells, "stationary", "transition", 12)
    false_free = (sum(1 for c in d12 if c["false_assertions"] == 0) / len(d12)) if d12 else 0.0
    coverages = [c["coverage"] for c in d12 if c["coverage"] is not None]
    coverage12 = statistics.median(coverages) if coverages else None
    conditions["2_high_degree_safety"] = {
        "transition_live_rate": live["transition"].get(12),
        "zero_false_share": round(false_free, 3),
        "median_coverage": coverage12,
        "required": "live >= 0.9, zero false assertions in >= 0.9 of cells, median coverage >= 0.5",
        "ok": bool((live["transition"].get(12) or 0) >= 0.9 and false_free >= 0.9
                   and coverage12 is not None and coverage12 >= 0.5),
        "note": "shipped is absent at d>=4; the ratio control is reported beside it",
    }

    t_stat = [c for c in cells if c.get("kind") == "stationary"
              and c.get("arm") == "transition"]
    r_stat = [c for c in cells if c.get("kind") == "stationary" and c.get("arm") == "ratio"]
    zero_share = (sum(1 for c in t_stat if c["false_assertions"] == 0)
                  / len(t_stat)) if t_stat else 0.0
    r_zero = (sum(1 for c in r_stat if c["false_assertions"] == 0)
              / len(r_stat)) if r_stat else 0.0
    big = [c for c in t_stat
           if c["stable_final"] >= MIN_STABLE_FOR_PRECISION and c["precision"] is not None]
    precision_ok = all(c["precision"] >= PRECISION_FLOOR for c in big)
    conditions["3_assertion_honesty"] = {
        "transition_zero_false_share": round(zero_share, 3),
        "ratio_zero_false_share": round(r_zero, 3),
        "transition_large_cells": len(big),
        "min_precision_in_large_cells": min((c["precision"] for c in big), default=None),
        "required": ("transition: zero false assertions in >= 0.9 of cells; "
                     "precision >= 0.95 where stable >= 40"),
        "ok": bool(zero_share >= 0.9 and precision_ok),
    }

    def contrast(top, base):
        pooled = []
        for degree in (2, 4):
            a = {c["seed"]: c for c in _by(cells, "task", top, degree)
                 if c.get("log_loss") is not None}
            b = {c["seed"]: c for c in _by(cells, "task", base, degree)
                 if c.get("log_loss") is not None}
            pooled.extend(a[k]["log_loss"] - b[k]["log_loss"]
                          for k in sorted(a.keys() & b.keys()))
        interval = paired_interval(pooled, reps=reps) if pooled else None
        return {"paired": len(pooled),
                "mean": round(statistics.mean(pooled), 6) if pooled else None,
                "interval": [round(interval[0], 6), round(interval[1], 6)] if interval else None}

    detail, diffs, losses = {}, [], []
    baseline_failures, baseline_missing = [], []
    for degree in (2, 4):
        r = {c["seed"]: c for c in _by(cells, "task", "ratio", degree)
             if c.get("log_loss") is not None}
        t = {c["seed"]: c for c in _by(cells, "task", "transition", degree)
             if c.get("log_loss") is not None}
        paired = [r[k]["log_loss"] - t[k]["log_loss"]
                  for k in sorted(r.keys() & t.keys())]
        interval = paired_interval(paired, reps=reps) if paired else None
        t_losses = [t[k]["log_loss"] for k in sorted(t)]
        base_losses = [t[k]["best_baseline_log_loss"] for k in sorted(t)
                       if t[k].get("best_baseline_log_loss") is not None]
        t_median = statistics.median(t_losses) if t_losses else None
        base_median = statistics.median(base_losses) if base_losses else None
        if t_median is None or base_median is None:
            baseline_missing.append(degree)
        elif t_median > base_median + 0.05:
            baseline_failures.append(degree)
        detail[str(degree)] = {
            "paired": len(paired),
            "mean_difference": round(statistics.mean(paired), 6) if paired else None,
            "interval": [round(interval[0], 6), round(interval[1], 6)] if interval else None,
            "transition_median": round(t_median, 6) if t_median is not None else None,
            "best_baseline_median": round(base_median, 6) if base_median is not None else None,
            "baseline_gap": round(t_median - base_median, 6)
            if t_median is not None and base_median is not None else None,
        }
        if interval:
            diffs.extend(paired)
            if interval[1] < 0:
                losses.append(degree)
    pooled = paired_interval(diffs, reps=reps) if diffs else None
    conditions["4_formula_effect"] = {
        "per_degree": detail,
        "pooled_mean": round(statistics.mean(diffs), 6) if diffs else None,
        "pooled_interval": [round(pooled[0], 6), round(pooled[1], 6)] if pooled else None,
        "regimes_with_loss": losses,
        "baseline_failures": baseline_failures,
        "baseline_missing": baseline_missing,
        "shipped_vs_ratio": contrast("shipped", "ratio"),
        "shipped_vs_transition": contrast("shipped", "transition"),
        "required": ("R - T log-loss pooled 99% lower > 0, no regime loss, and T within "
                     "0.05 nats of the best simple baseline in each regime"),
        "ok": bool(pooled and pooled[0] > 0 and not losses
                   and not baseline_failures and not baseline_missing),
    }

    coverage_detail, coverage_ok = {}, True
    for degree in (2, 4):
        r = [c["coverage"] for c in _by(cells, "stationary", "ratio", degree)
             if c["coverage"] is not None]
        t = [c["coverage"] for c in _by(cells, "stationary", "transition", degree)
             if c["coverage"] is not None]
        if not r or not t:
            coverage_ok = False
            coverage_detail[str(degree)] = {"ratio": None, "transition": None}
            continue
        rm, tm = statistics.median(r), statistics.median(t)
        coverage_detail[str(degree)] = {"ratio": round(rm, 4), "transition": round(tm, 4)}
        if tm < rm - 0.05:
            coverage_ok = False
    conditions["5_coverage"] = {
        "per_degree": coverage_detail,
        "required": "transition median >= ratio median at 2, 4; no drop > 0.05",
        "ok": coverage_ok,
    }

    revision = {}
    r4 = {c["seed"]: c for c in _by(cells, "shift", "ratio", 4)}
    t4 = {c["seed"]: c for c in _by(cells, "shift", "transition", 4)}
    common = sorted(r4.keys() & t4.keys())
    b4 = [t4[k]["b_coverage_final"] for k in common
          if t4[k]["b_coverage_final"] is not None]
    a_not_worse = [t4[k]["a_share_final"] <= r4[k]["a_share_final"] for k in common
                   if t4[k]["a_share_final"] is not None
                   and r4[k]["a_share_final"] is not None]
    t12 = [c["b_coverage_final"] for c in _by(cells, "shift", "transition", 12)
           if c["b_coverage_final"] is not None]
    revision["d4"] = {"median_b_coverage": round(statistics.median(b4), 4) if b4 else None,
                      "a_share_not_worse": (sum(a_not_worse) / len(a_not_worse))
                      if a_not_worse else None}
    revision["d12"] = {"median_b_coverage": round(statistics.median(t12), 4) if t12 else None}
    conditions["6_revision"] = {
        "detail": revision,
        "required": ("d4: B coverage >= 0.5 and A share no worse than ratio; "
                     "d12: B coverage >= 0.4"),
        "ok": bool(b4 and statistics.median(b4) >= 0.5 and a_not_worse
                   and all(a_not_worse) and t12 and statistics.median(t12) >= 0.4),
    }

    if not conditions["1_comparability"]["ok"]:
        label = "not comparable"
    elif not conditions["2_high_degree_safety"]["ok"]:
        label = "improves low-degree only"
    elif not conditions["3_assertion_honesty"]["ok"]:
        label = "trades precision for coverage"
    elif conditions["4_formula_effect"]["baseline_missing"]:
        label = "task endpoint not measurable"
    elif conditions["4_formula_effect"]["baseline_failures"]:
        label = "worse than the simple baseline"
    elif not conditions["4_formula_effect"]["ok"]:
        mean = conditions["4_formula_effect"]["pooled_mean"]
        label = "threshold alone suffices" if (mean is not None and mean <= 0) else "no task effect"
    elif not conditions["5_coverage"]["ok"]:
        label = "coverage regression"
    elif not conditions["6_revision"]["ok"]:
        label = "no useful revision"
    else:
        label = "adopt"

    thresholds = (calibration or {}).get("thresholds") or {}
    boundary = {arm: thresholds.get(arm) == 0.075 for arm in ("ratio", "transition")}
    return {"verdict": "ADOPT" if label == "adopt" else label.upper(),
            "label": label,
            "all_conditions_met": all(c["ok"] for c in conditions.values()),
            "conditions": conditions,
            "thresholds": thresholds,
            "boundary_selected": boundary}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _pool(func, tasks, workers, progress=False):
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results, total = [], len(tasks)
        for i, result in enumerate(pool.map(func, tasks), 1):
            results.append(result)
            if progress and (i % 8 == 0 or i == total):
                print("  %d/%d cells" % (i, total), flush=True)
        return results


def _calibration_task(args):
    arm, tau, degree, seed, cycles = args
    return stationary_cell(arm, tau, degree, seed, cycles)


def _heldout_task(args):
    kind, arm, tau, degree, seed = args
    if kind == "stationary":
        return stationary_cell(arm, tau, degree, seed)
    if kind == "shift":
        return shift_cell(arm, tau, degree, seed)
    return task_cell(arm, tau, degree, seed)


def _smoke_guard(args, full_seeds, full_degrees, full_cycles):
    if args.smoke:
        return False
    assert tuple(full_seeds) == CALIBRATION_SEEDS, "protocol seeds are fixed"
    assert tuple(full_degrees) == DEGREES, "protocol degrees are fixed"
    assert full_cycles == CYCLES, "protocol cycles are fixed"
    return True


def cmd_audit(args):
    report = audit_worlds()
    print(json.dumps(report, indent=1))
    return 0 if report["ok"] else 1


def cmd_calibrate(args):
    seeds = tuple(args.seeds) if args.seeds else CALIBRATION_SEEDS
    degrees = tuple(args.degrees) if args.degrees else DEGREES
    cycles = args.cycles or CYCLES
    protocol = _smoke_guard(args, seeds, degrees, cycles)
    overlapping = set(seeds) & harvest_seeds()
    if overlapping:
        raise SystemExit("calibration seeds already used: %s" % sorted(overlapping))
    tasks = [(arm, tau, d, s, cycles) for arm in ("ratio", "transition")
             for tau in GRID for d in degrees for s in seeds]
    print("calibration: %d cells (%d arms), %d workers"
          % (len(tasks), 2, args.workers), flush=True)
    cells = _pool(_calibration_task, tasks, args.workers, progress=True)
    choices = {arm: choose_threshold([c for c in cells if c["arm"] == arm])
               for arm in ("ratio", "transition")}
    thresholds = {arm: choices[arm]["tau_star"] for arm in choices}
    payload = {"protocol": protocol, "kind": "calibration", "version": 2,
               "seeds": list(seeds), "degrees": list(degrees), "grid": list(GRID),
               "cycles": cycles, "thresholds": thresholds,
               "boundary_selected": {arm: thresholds[arm] == 0.075 for arm in thresholds},
               "choices": choices, "cells": cells}
    out = Path(args.out) if args.out else (
        SMOKE_DIR / "calibration.smoke.json" if args.smoke else
        CONFIRMATION_DIR / "calibration.json")
    if not protocol and CONFIRMATION_DIR in out.parents:
        raise SystemExit("a smoke calibration may not be written under docs/confirmation")
    seal(payload, out)
    print(json.dumps({arm: {"tau": thresholds[arm],
                            "reason": choices[arm]["reason"]}
                      for arm in choices}, indent=1))
    print("wrote %s (protocol=%s)" % (out, protocol))
    return 0 if all(value is not None for value in thresholds.values()) else 1


def cmd_heldout(args):
    calibration = verify_seal(Path(args.calibration))
    thresholds = calibration.get("thresholds") or {
        "transition": calibration.get("tau_star")}
    if not all(thresholds.get(arm) is not None for arm in ("ratio", "transition")):
        raise SystemExit("calibration selected no threshold for one of the arms")
    tau_for = {"shipped": None, "ratio": thresholds["ratio"],
               "transition": thresholds["transition"]}
    seeds = tuple(args.seeds) if args.seeds else HELDOUT_SEEDS
    protocol = (not args.smoke) and calibration.get("protocol") is True
    if not args.smoke:
        overlapping = set(seeds) & harvest_seeds()
        if overlapping:
            raise SystemExit("held-out seeds already used: %s" % sorted(overlapping))
    tasks = []
    for arm in ARMS:
        arm_tau = tau_for[arm]
        for degree in DEGREES:
            for seed in seeds:
                tasks.append(("stationary", arm, arm_tau, degree, seed))
        for degree in SHIFT_DEGREES:
            for seed in seeds:
                tasks.append(("shift", arm, arm_tau, degree, seed))
        for degree in DEGREES:
            for seed in seeds:
                tasks.append(("task", arm, arm_tau, degree, seed))
    print("held-out: %d cells, %d workers" % (len(tasks), args.workers), flush=True)
    cells = _pool(_heldout_task, tasks, args.workers, progress=True)
    payload = {"protocol": protocol, "kind": "heldout", "version": 2,
               "thresholds": thresholds, "calibration_sha256": calibration["sha256"],
               "seeds": list(seeds), "cells": cells, "audit": audit_worlds()}
    out = Path(args.out) if args.out else (
        SMOKE_DIR / "heldout.smoke.json" if args.smoke else
        CONFIRMATION_DIR / "heldout.json")
    if not protocol and CONFIRMATION_DIR in out.parents:
        raise SystemExit("a smoke held-out run may not be written under docs/confirmation")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(engine_stamp.stamp(payload), indent=1), encoding="utf-8")
    print("wrote %s (protocol=%s)" % (out, protocol))
    return 0


def cmd_analyze(args):
    calibration = verify_seal(Path(args.calibration))
    heldout = _read_artifact(Path(args.heldout), "held-out artifact", require_cells=True)
    recorded = heldout.get("calibration_sha256")
    if recorded is not None and recorded != calibration["sha256"]:
        raise SystemExit("held-out artifact was produced under a different calibration "
                         "(records %s, given %s)" % (recorded, calibration["sha256"]))
    verdict = decide(heldout["cells"], calibration, reps=args.reps)
    verdict["protocol"] = bool(heldout.get("protocol")) and bool(calibration.get("protocol"))
    if not verdict["protocol"]:
        verdict["verdict"] = "SMOKE — not a verdict"
    print(json.dumps(verdict, indent=1))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(engine_stamp.stamp(verdict), indent=1), encoding="utf-8")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit")
    audit.set_defaults(func=cmd_audit)

    cal = sub.add_parser("calibrate")
    cal.add_argument("--smoke", action="store_true")
    cal.add_argument("--seeds", type=int, nargs="*")
    cal.add_argument("--degrees", type=int, nargs="*")
    cal.add_argument("--cycles", type=int)
    cal.add_argument("--workers", type=int, default=4)
    cal.add_argument("--out")
    cal.set_defaults(func=cmd_calibrate)

    held = sub.add_parser("heldout")
    held.add_argument("--calibration", required=True)
    held.add_argument("--smoke", action="store_true")
    held.add_argument("--seeds", type=int, nargs="*")
    held.add_argument("--workers", type=int, default=4)
    held.add_argument("--out")
    held.set_defaults(func=cmd_heldout)

    ana = sub.add_parser("analyze")
    ana.add_argument("--calibration", required=True)
    ana.add_argument("--heldout", required=True)
    ana.add_argument("--reps", type=int, default=BOOTSTRAP_REPLICATES)
    ana.add_argument("--out")
    ana.set_defaults(func=cmd_analyze)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
