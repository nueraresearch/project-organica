"""Measure the four recorded temporal-decay fixes, one arm each.

The 2026-11-06 diagnosis (``docs/RERUN-0.12.0.md``) recorded four options and
applied none.  This probe runs them side by side on the Tier-1 matrix's own
stimulus and seed, so the choice is made from measurements rather than from
the plausibility of each story:

  shipped  factor 0.95, strength = count / source_frequency, threshold 0.30
  opt1     decay skips edges observed in the current cycle (the ratchet)
  opt2     strength = transition probability count / out_counts[source]
  opt2r    opt2 with the threshold recalibrated to 0.15
  opt3     factor 0.99 (slower decay, threshold unchanged)
  opt4     factor 0.95, threshold lowered to 0.15

``opt2r`` exists because a redefined strength is not on the shipped threshold's
scale: if the definition changes and the threshold does not, the arm measures
two things at once.  Both are reported; the pair says whether the definition is
viable and what it costs.

Every arm runs two phases:

  stationary  160 cycles of one design, to test whether the stable set is
              stable at all (the shipped engine dies by cycle 112);
  shift       80 cycles of design A then 40 of a relabelled design B with a
              disjoint vocabulary, to test the thing decay exists for: dropping
              the old law and picking up the new one.

Scoring uses the world's own edge set, derived from the stimulus by the same
lookback rule the engine uses.  Labels never enter selection - they only score
what the selector kept.

This is a harness.  The engine is frozen (rule 12) and is not edited; ``opt1``
overrides the decay call and ``opt2`` rescales candidates before they are
stored, both by subclassing, the way ``ablation_study.py`` does.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from statistics import median

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.branch_streams import lattice_designs, lattice_stream  # noqa: E402
from organica.memory import MemoryService, _extract_tags              # noqa: E402
from organica.paths import temp_db                                   # noqa: E402
from organica.sleep import SleepService                              # noqa: E402
from organica.streams import EVENTS_PER_CYCLE                        # noqa: E402

STATIONARY_CYCLES = 300
SHIFT_A_CYCLES = 80
SHIFT_B_CYCLES = 40
SEED = 20261023
STIMULUS = "L1_hub1_t3_disjoint"
MARKERS = 7
LOOKBACK = 3


class Probe(SleepService):
    """Counts the upper layers and can redefine prediction strength."""

    HYPOTHESIS_RETENTION = "alphabetical"
    STRENGTH_MODE = "ratio"      # or "transition_probability"

    def __init__(self, memory):
        super().__init__(memory)
        self.beliefs = 0
        self.theories = 0
        self.processes = 0
        self.workflows = 0
        self._cycle_edges: set[tuple[str, str]] = set()
        self._prev_counts: dict[tuple[str, str], int] = {}

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        current = {(src, tgt): count for src, targets in temporal.items()
                   for tgt, count in targets.items()}
        # Only edges whose count ROSE since the last decay were reinforced by
        # this cycle's ingest.  Exempting everything present in `temporal`
        # would exempt every historical edge down to the count-1 floor and
        # silently become no-decay at all.
        self._cycle_edges = {edge for edge, count in current.items()
                             if count > self._prev_counts.get(edge, 0)}
        out = super()._build_predictions(temporal, freqs, prior_schemas)
        if self.STRENGTH_MODE == "transition_probability":
            for cand in out:
                cand.strength = min(1.0, float(cand.evidence.get("transition_prob", 0.0)))
        return out

    def _form_and_test_hypotheses(self, *args, **kwargs):
        out = super()._form_and_test_hypotheses(*args, **kwargs)
        self.beliefs = max(0, len(out) - MARKERS)
        return out

    def _form_theories_and_questions(self, *args, **kwargs):
        out = super()._form_theories_and_questions(*args, **kwargs)
        self.theories = len(out[0]) if isinstance(out, tuple) else 0
        return out

    def _compose_processes(self, *args, **kwargs):
        out = super()._compose_processes(*args, **kwargs)
        self.processes = len(out)
        return out

    def _compose_workflows(self, *args, **kwargs):
        out = super()._compose_workflows(*args, **kwargs)
        self.workflows = len(out)
        return out


class TransitionStrength(Probe):
    STRENGTH_MODE = "transition_probability"


class SlowDecay(Probe):
    TEMPORAL_DECAY_FACTOR = 0.99


class LowThreshold(Probe):
    STABLE_THRESHOLD = 0.15


class TransitionLowThreshold(TransitionStrength):
    STABLE_THRESHOLD = 0.15


ARMS = [
    ("shipped", Probe, None),
    ("opt1_decay_only_unreinforced", Probe, "exempt"),
    ("opt2_transition_probability", TransitionStrength, None),
    ("opt2r_transition_probability_low_threshold", TransitionLowThreshold, None),
    ("opt3_slow_decay_0.99", SlowDecay, None),
    ("opt4_threshold_0.15", LowThreshold, None),
]


def _install_exempt_decay(service: Probe) -> None:
    """Decay every edge except the ones observed in the current cycle.

    Harness-side implementation of option 1: the engine's bulk UPDATE is
    replaced, for this instance only, by decay-then-restore of the live edges.
    """
    memory = service.memory

    def decay(factor: float = 0.95, min_count: int = 1) -> int:
        rows = memory._conn.execute(
            "SELECT tag_from, tag_to, count FROM precedes").fetchall()
        cur = memory._conn.execute(
            "UPDATE precedes SET count = MAX(?, CAST(ROUND(count * ?) AS INTEGER))",
            (min_count, factor))
        restore = [(count, src, tgt) for src, tgt, count in rows
                   if (src, tgt) in service._cycle_edges]
        if restore:
            memory._conn.executemany(
                "UPDATE precedes SET count = ? WHERE tag_from = ? AND tag_to = ?",
                restore)
        memory._conn.commit()
        service._prev_counts = {
            (src, tgt): count for src, tgt, count in
            memory._conn.execute("SELECT tag_from, tag_to, count FROM precedes").fetchall()
        }
        return cur.rowcount

    memory.decay_temporal_edges = decay


def world_edges(events: list[str]) -> set[tuple[str, str]]:
    """Directed tag pairs the stimulus actually presents, by the engine's rule."""
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


def _stable(service: Probe) -> tuple[list[tuple[str, str]], list[float]]:
    """Current stable predictions, and the strength of every live prediction.

    Reads the same prior the engine filters on, so the measurement cannot drift
    from the mechanism under test.
    """
    seen: dict[tuple[str, str], float] = {}
    for cand in service._load_prior_candidates():
        if cand.get("type") != "prediction_candidate":
            continue
        src, tgt = cand.get("source"), cand.get("target")
        if not src or not tgt:
            continue
        value = float(cand.get("confidence") or cand.get("strength") or 0.0)
        key = (src, tgt)
        if value > seen.get(key, -1.0):
            seen[key] = value
    every = list(seen.values())
    stable = [edge for edge, value in seen.items() if value >= service.STABLE_THRESHOLD]
    return stable, every


def _edge_mass(memory) -> int:
    row = memory._conn.execute("SELECT COALESCE(SUM(count), 0) FROM precedes").fetchone()
    return int(row[0] or 0)


def run_arm(label: str, cls, mode, events: list[str], shifted: list[str],
            world_a, world_b) -> dict:
    db = temp_db(f"decay_options_{label}.db")
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = cls(memory)
    service._rng.seed(SEED)
    if mode == "exempt":
        _install_exempt_decay(service)

    for text in events[:EVENTS_PER_CYCLE]:
        memory.store(text, event_type="event", source="seed:bootstrap")

    stationary_rows = []
    shift_rows = []
    for cycle in range(STATIONARY_CYCLES):
        start = (cycle * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            memory.store(text, event_type="event", source=f"cycle:{cycle}")
        service.run_sleep_cycle()
        stable, every = _stable(service)
        hit = sum(1 for edge in stable if edge in world_a)
        stationary_rows.append({
            "cycle": cycle,
            "beliefs": service.beliefs,
            "theories": service.theories,
            "processes": service.processes,
            "workflows": service.workflows,
            "stable": len(stable),
            "stable_precision": round(hit / len(stable), 4) if stable else None,
            "stable_coverage": round(len({e for e in stable if e in world_a}) / len(world_a), 4)
            if world_a else None,
            "median_strength_all": round(median(every), 4) if every else 0.0,
            "edge_mass": _edge_mass(memory),
        })

    # Phase shift: A for 80 cycles, then B only for 40.  The A edges stop
    # arriving, so anything that keeps asserting them is failing to revise.
    shift_a = events
    for cycle in range(SHIFT_A_CYCLES + SHIFT_B_CYCLES):
        stream = shift_a if cycle < SHIFT_A_CYCLES else shifted
        start = (cycle * EVENTS_PER_CYCLE) % len(stream)
        for text in stream[start:start + EVENTS_PER_CYCLE]:
            memory.store(text, event_type="event", source=f"cycle:{cycle}")
        service.run_sleep_cycle()
        stable, _ = _stable(service)
        hit_b = sum(1 for edge in stable if edge in world_b)
        keep_a = sum(1 for edge in stable if edge in world_a)
        shift_rows.append({
            "cycle": cycle,
            "phase": "A" if cycle < SHIFT_A_CYCLES else "B",
            "stable": len(stable),
            "b_edges": hit_b,
            "b_coverage": round(hit_b / len(world_b), 4) if world_b else None,
            "a_share": round(keep_a / len(stable), 4) if stable else None,
            "theories": service.theories,
        })

    memory.close()
    db.unlink(missing_ok=True)
    return {"arm": label, "class": cls.__name__, "stationary": stationary_rows,
            "shift": shift_rows}


def _slope(rows, key: str, window: int = 40) -> float:
    tail = [r[key] for r in rows[-window:]]
    n = len(tail)
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(tail) / n
    denom = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, tail)) / denom if denom else 0.0


def _liveness(rows) -> bool:
    tail = rows[-max(1, len(rows) // 10):]
    return bool(min(r["theories"] for r in tail) >= 1
                and sum(r["beliefs"] for r in tail) / len(tail) >= 2)


def summary(arm: dict) -> dict:
    rows = arm["stationary"]
    last = rows[-1]
    tail = rows[-STATIONARY_CYCLES // 10:]
    shift = arm["shift"]
    live = [r["cycle"] for r in rows if r["theories"] >= 1]
    return {
        "arm": arm["arm"],
        "theories_c80": rows[79]["theories"],
        "theories_c160": rows[159]["theories"],
        "theories_final": last["theories"],
        "last_live_cycle": max(live) if live else None,
        "beliefs_final": last["beliefs"],
        "processes_final": last["processes"],
        "theories_tail_min": min(r["theories"] for r in tail),
        "beliefs_tail_mean": round(sum(r["beliefs"] for r in tail) / len(tail), 2),
        "stable_final": last["stable"],
        "median_strength_final": last["median_strength_all"],
        "strength_slope_last40": round(_slope(rows, "median_strength_all"), 5),
        "precision_final": last["stable_precision"],
        "coverage_final": last["stable_coverage"],
        "edge_mass_final": last["edge_mass"],
        "b_coverage_final": shift[-1]["b_coverage"],
        "b_coverage_20_into_shift": shift[SHIFT_A_CYCLES + 19]["b_coverage"],
        "b_edges_final": shift[-1]["b_edges"],
        "a_share_at_shift_end": shift[SHIFT_A_CYCLES - 1]["a_share"],
        "a_share_final": shift[-1]["a_share"],
        "liveness80": _liveness(rows[:80]),
        "liveness_pass": _liveness(rows),
    }


def main() -> int:
    designs = lattice_designs()
    events = lattice_stream(designs[STIMULUS]["triangles"])
    relabelled = [[" ".join("z" + tok for tok in word.split()) for word in tri]
                  for tri in designs[STIMULUS]["triangles"]]
    events_b = lattice_stream(relabelled)
    world_a = world_edges(events)
    world_b = world_edges(events_b)
    assert not (world_a & world_b), "shift vocabulary must be disjoint"
    for text in events_b:
        assert "z" == text.lstrip()[0], "relabelled stream must carry the prefix"

    results = []
    future_to_label = {}
    with ProcessPoolExecutor(max_workers=4) as pool:
        for label, cls, mode in ARMS:
            future = pool.submit(run_arm, label, cls, mode, events, events_b,
                                 world_a, world_b)
            future_to_label[future] = label
        collected = {}
        for future in as_completed(future_to_label):
            arm = future.result()
            arm["summary"] = summary(arm)
            collected[arm["arm"]] = arm
            print("finished %s" % arm["arm"], flush=True)
    results = [collected[label] for label, _, _ in ARMS]
    for arm in results:
        s = arm["summary"]
        print("%-46s th80=%2d th160=%2d th300=%2d bel=%3d stab=%3d prec=%s cov=%s "
              "Bcov=%s A=%s live80=%s live300=%s"
              % (s["arm"], s["theories_c80"], s["theories_c160"], s["theories_final"],
                 s["beliefs_final"],
                 s["stable_final"], s["precision_final"], s["coverage_final"],
                 s["b_coverage_final"], s["a_share_final"], s["liveness80"],
                 s["liveness_pass"]))

    out = {"config": {"seed": SEED, "stimulus": STIMULUS,
                      "stationary_cycles": STATIONARY_CYCLES,
                      "shift": [SHIFT_A_CYCLES, SHIFT_B_CYCLES],
                      "world_edges_a": len(world_a), "world_edges_b": len(world_b),
                      "lookback": LOOKBACK, "markers": MARKERS},
           "arms": results}
    path = REPO / "docs" / "prediction-decay-options.json"
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")

    by = {r["summary"]["arm"]: r["summary"] for r in results}
    problems = []
    if by["shipped"]["liveness_pass"]:
        problems.append("the shipped arm was expected to fail the liveness gate")
    if by["shipped"]["theories_final"] != 0:
        problems.append("the shipped arm was expected to have no theories at cycle 159")
    if not any(s["liveness_pass"] for name, s in by.items() if name != "shipped"):
        problems.append("no fix kept the upper layers alive - the probe would be measuring nothing")
    for problem in problems:
        print("!! " + problem)
    if problems:
        return 1
    print("wrote %s; the shipped arm dies and at least one fix survives" % path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
