"""Measure whether disabling temporal decay keeps the engine live over the horizon.

Measurement only. The two arms are the same engine and differ in one class
attribute, ``TEMPORAL_DECAY_FACTOR``: ``0.95`` (shipped, `organica/sleep.py`) and
``1.0`` (the recorded counterfactual in ``docs/RERUN-0.12.0.md``). No engine file
is edited, no threshold is involved, and nothing is adopted here.

The matrix's own stimulus, seed, cadence and horizon are used, so a result sits
beside ``docs/force_matrix.json`` and ``docs/RERUN-0.12.0.md``:

    PYTHONHASHSEED=0 python benchmarks/decay_operability.py --cycles 3000
    python benchmarks/decay_operability.py --cycles 40        # pilot, marked

Both arms run in one process on purpose: the process's hash order is then
common-mode across arms, and ``PYTHONHASHSEED=0`` is required before an artifact
may claim protocol status (the repository has already measured that hash order
changes the engine's cycle-level output).

Per cycle it records theories, beliefs, processes, stable predictions, the
temporal-edge row count, the temporal-edge mass and the database size. Growth is
reported, not judged: no edge-growth bound was pre-committed, and a bound chosen
after seeing the curve would be taken from the run it judges.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import organica                                            # noqa: E402
from organica.branch_streams import (                       # noqa: E402
    NEUTRAL_HUB, NEUTRAL_PETALS, lattice_designs, lattice_stream)
from organica.memory import MemoryService                   # noqa: E402
from organica.paths import temp_db                          # noqa: E402
from organica.sleep import SleepService                     # noqa: E402
from organica.streams import EVENTS_PER_CYCLE               # noqa: E402

CYCLES = 3000
SEED = 20261023
PROTOCOL_HASH_SEED = "0"
MARKERS = 7                    # structural markers excluded from the belief count
STIMULUS = "lattice_L1 (three disjoint triangles)"


def matrix_events() -> list[str]:
    """The Tier-1 matrix's stimulus, byte for byte."""
    lattice = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
    return lattice_stream(lattice["L1_hub1_t3_disjoint"]["triangles"])


def protocol_run(cycles: int, seed: int, hash_seed: str | None) -> bool:
    """A run may call itself protocol only on the matrix's own settings."""
    return cycles == CYCLES and seed == SEED and hash_seed == PROTOCOL_HASH_SEED


def destination(protocol: bool, out: str | None) -> Path:
    if out is not None:
        path = Path(out)
    elif protocol:
        path = REPO / "docs" / "decay_operability.json"
    else:
        path = REPO / ".scratch" / "decay_operability.smoke.json"
    if not protocol and (REPO / "docs") in path.resolve().parents:
        raise SystemExit("a pilot run may not be written under docs/")
    return path


class Arm(SleepService):
    """The matrix reference arm's retention policy, with per-cycle counters."""

    HYPOTHESIS_RETENTION = "alphabetical"

    def __init__(self, memory):
        super().__init__(memory)
        self.theories = 0
        self.beliefs = 0
        self.processes = 0

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


class DecayOn(Arm):
    TEMPORAL_DECAY_FACTOR = 0.95


class DecayOff(Arm):
    TEMPORAL_DECAY_FACTOR = 1.0        # the counterfactual: decay called, counts unchanged


def _edge_stats(memory) -> tuple[int, int]:
    row = memory._conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(count), 0) FROM precedes").fetchone()
    return int(row[0] or 0), int(row[1] or 0)


def _db_bytes(db: Path) -> int:
    total = 0
    for suffix in ("", "-wal", "-shm"):
        path = Path(str(db) + suffix)
        if path.exists():
            total += path.stat().st_size
    return total


def _stable_count(service) -> int:
    """Stable predictions: the same prior the engine filters on."""
    seen: dict[tuple[str, str], float] = {}
    for cand in service._load_prior_candidates():
        if cand.get("type") != "prediction_candidate":
            continue
        src, tgt = cand.get("source"), cand.get("target")
        if not src or not tgt:
            continue
        value = float(cand.get("confidence") or cand.get("strength") or 0.0)
        if value > seen.get((src, tgt), -1.0):
            seen[(src, tgt)] = value
    return sum(1 for value in seen.values() if value >= service.STABLE_THRESHOLD)


def liveness(rows: list[dict]) -> bool:
    """The decay study's gate: theories present and beliefs held in the last tenth."""
    if not rows:
        return False
    tail = rows[-max(1, len(rows) // 10):]
    return bool(min(r["theories"] for r in tail) >= 1
                and sum(r["beliefs"] for r in tail) / len(tail) >= 2)


def growth(rows: list[dict]) -> dict:
    """Decile snapshots and per-cycle rates. Reported, never judged."""
    if len(rows) < 2:
        raise SystemExit("growth needs at least two cycles")
    marks, seen = [], set()
    n = len(rows)
    for k in range(1, 11):
        i = min(n - 1, (k * n) // 10 - 1)
        if i in seen:
            continue
        seen.add(i)
        marks.append({key: rows[i][key] for key in
                      ("cycle", "theories", "beliefs", "edges", "edge_mass", "db_bytes")})
    first, last = rows[0], rows[-1]
    span = max(1, last["cycle"] - first["cycle"])
    return {
        "deciles": marks,
        "edge_mass_per_cycle": round((last["edge_mass"] - first["edge_mass"]) / span, 3),
        "edge_count_per_cycle": round((last["edges"] - first["edges"]) / span, 3),
        "db_bytes_per_cycle": round((last["db_bytes"] - first["db_bytes"]) / span, 3),
        "edge_mass_ratio_end_over_first": round(
            last["edge_mass"] / max(1, first["edge_mass"]), 3),
        "db_bytes_ratio_end_over_first": round(
            last["db_bytes"] / max(1, first["db_bytes"]), 3),
    }


def summarise(rows: list[dict], factor: float) -> dict:
    last = rows[-1]
    with_theory = [r["cycle"] for r in rows if r["theories"] >= 1]
    with_belief = [r["cycle"] for r in rows if r["beliefs"] >= 1]
    return {
        "decay_factor": factor,
        "theories_final": last["theories"],
        "beliefs_final": last["beliefs"],
        "processes_final": last["processes"],
        "stable_final": last["stable"],
        "edges_final": last["edges"],
        "edge_mass_final": last["edge_mass"],
        "db_bytes_final": last["db_bytes"],
        "last_cycle_with_theory": max(with_theory) if with_theory else None,
        "last_cycle_with_belief": max(with_belief) if with_belief else None,
        "liveness": liveness(rows),
        "growth": growth(rows),
    }


def run_arm(factor: float, cycles: int, seed: int, events: list[str]) -> dict:
    label = "decay_off" if factor == 1.0 else "decay_on"
    cls = DecayOff if factor == 1.0 else DecayOn
    db = temp_db("operability_%s_%s.db" % (label, seed))
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = cls(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    for text in events:
        memory.store(text, event_type="event", source="seed:bootstrap")
    rows: list[dict] = []
    started = time.time()
    try:
        for cycle in range(cycles):
            start = (cycle * EVENTS_PER_CYCLE) % len(events)
            for text in events[start:start + EVENTS_PER_CYCLE]:
                memory.store(text, event_type="event", source="cycle:%d" % cycle)
            service.run_sleep_cycle()
            edges, mass = _edge_stats(memory)
            rows.append({"cycle": cycle, "theories": service.theories,
                         "beliefs": service.beliefs, "processes": service.processes,
                         "stable": _stable_count(service), "edges": edges,
                         "edge_mass": mass, "db_bytes": _db_bytes(db)})
    finally:
        memory.close()
        db.unlink(missing_ok=True)
    return {"arm": label, "decay_factor": factor, "seed": seed, "cycles": cycles,
            "seconds": round(time.time() - started, 1), "rows": rows,
            "summary": summarise(rows, factor)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycles", type=int, default=CYCLES)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--out", default=None)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(argv)

    hash_seed = os.environ.get("PYTHONHASHSEED")
    protocol = protocol_run(args.cycles, args.seed, hash_seed) and not args.smoke
    if args.smoke:
        reason = "passed --smoke"
    elif args.cycles != CYCLES:
        reason = "cycles %d is not the matrix horizon %d" % (args.cycles, CYCLES)
    elif args.seed != SEED:
        reason = "seed %d is not the matrix seed %d" % (args.seed, SEED)
    elif hash_seed != PROTOCOL_HASH_SEED:
        reason = "PYTHONHASHSEED must be 0 for a protocol run, got %r" % hash_seed
    else:
        reason = None

    events = matrix_events()
    print("decay operability: %d cycles, seed %d, %s"
          % (args.cycles, args.seed, "PROTOCOL RUN" if protocol else "NOT a protocol run"))
    if reason:
        print("  reason: %s" % reason)

    arms = {}
    for factor in (0.95, 1.0):
        arm = run_arm(factor, args.cycles, args.seed, events)
        arms[arm["arm"]] = arm
        s = arm["summary"]
        print("  %-9s theories %d beliefs %d stable %d processes %d | last live %s | "
              "live %s | edges %d mass %d db %d"
              % (arm["arm"], s["theories_final"], s["beliefs_final"], s["stable_final"],
                 s["processes_final"], s["last_cycle_with_theory"], s["liveness"],
                 s["edges_final"], s["edge_mass_final"], s["db_bytes_final"]))
        sys.stdout.flush()

    on, off = arms["decay_on"]["rows"][-1], arms["decay_off"]["rows"][-1]
    if (on["edge_mass"], on["edges"]) == (off["edge_mass"], off["edges"]):
        raise SystemExit("the two arms left identical temporal-edge state after %d cycles; "
                         "the decay intervention did not take effect" % args.cycles)

    payload = {
        "protocol": protocol,
        "protocol_reason": reason,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engine_version": organica.__version__,
        "py_hash_seed": hash_seed,
        "stimulus": STIMULUS,
        "cycles": args.cycles,
        "seed": args.seed,
        "arms": {label: {"decay_factor": arm["decay_factor"],
                         "seconds": arm["seconds"],
                         "summary": arm["summary"],
                         "series": {key: [r[key] for r in arm["rows"]] for key in
                                    ("theories", "beliefs", "stable", "edges",
                                     "edge_mass", "db_bytes")}}
                 for label, arm in arms.items()},
        "comparison": {
            "decay_on_live": arms["decay_on"]["summary"]["liveness"],
            "decay_off_live": arms["decay_off"]["summary"]["liveness"],
            "both_live": (arms["decay_on"]["summary"]["liveness"]
                          and arms["decay_off"]["summary"]["liveness"]),
            "last_cycle_with_theory": {label: arms[label]["summary"]["last_cycle_with_theory"]
                                       for label in arms},
            "edge_mass_final": {label: arms[label]["summary"]["edge_mass_final"]
                                for label in arms},
            "db_bytes_final": {label: arms[label]["summary"]["db_bytes_final"]
                               for label in arms},
            "edge_mass_ratio_off_over_on": round(
                off["edge_mass"] / max(1, on["edge_mass"]), 3),
            "growth_criterion": "unset: no bound was pre-committed, so growth is "
                                "reported and not judged",
        },
    }
    path = destination(protocol, args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print("wrote %s (protocol=%s)" % (path, protocol))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
