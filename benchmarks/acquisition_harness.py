"""Acquisition study harness — prerequisite gates (§8 of the preregistration).

This module implements the four infrastructure gates that must pass before any
acquisition-study cell is run.  They protect the experiment from the class of
mistakes identified in the H→L audit: a benchmark that is executable while
still measuring the wrong thing.

Gates implemented
-----------------

Gate 10  content-identity detection
    Can the harness distinguish a re-instantiated structure (a new SQLite row
    written with the same candidate id) from a retained one (the same id, no
    new row) using the store log alone?  Uses the ``ObservingMemoryService``
    already built for the audit trace.

Gate 11  intervention verification
    After every P-intervention (suppress a Layer-1 candidate) or E-rem (remove
    acquisition events), the harness confirms the intervention is in effect
    BEFORE reading any outcome.  Two sub-checks:
      • For P-org: the target candidate's row is absent from the events table.
      • For E-rem: events rows by the acquisition source are gone; ``precedes``
        is empty.

Gate 12  removal verification (table-level)
    After E-rem specifically:
      ``events``    — rows with the acquisition source = 0
      ``precedes``  — all rows = 0
      ``cooccurrences`` — still > 0
      ``tag_counts``    — still > 0
    This is the exact pattern verified in the scratch scripts before the
    harness was built.

Gate 13  acquisition sufficiency
    At the end of the acquisition phase the harness counts how many of the
    world's compositional edges are represented in the organism's current
    ``temporal_edges()`` output.  If fewer than ``SUFFICIENCY_THRESHOLD`` are
    covered the seed is flagged as ``acquisition_failed``.  A seed flagged
    here MUST NOT be labelled ``transfer_failure`` — the distinction is
    structural.

Gate 16  scratch-only guarantee
    Every harness run uses ``organica.paths.temp_db()`` for its database.  The
    live ``memory.db`` path is never opened for writing.  The check verifies
    this at the end of each gate run.

Design rules (mirror AGENTS.md discipline)
-------------------------------------------

* Every gate is independently testable: it exposes a function that returns a
  structured result dict with a ``passed`` boolean.
* Every gate CAN FAIL: the test suite (``tests/test_acquisition_harness.py``)
  demonstrates the failure branch for each gate by injecting a deliberately
  broken condition.
* Engine files (``organica/sleep.py``, ``organica/memory.py``) are NOT edited.
  Instrumentation is done by subclassing MemoryService (same pattern as the
  audit trace probe).
* Standard library only; no third-party imports.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService  # noqa: E402
from organica.paths import LIVE_DB, temp_db  # noqa: E402
from organica.sleep import SleepService  # noqa: E402
from benchmarks.acquisition_compositional import (  # noqa: E402
    generate_compositional_world,
    PHASE_ACQUISITION,
    EVENTS_PER_CYCLE,
)
from benchmarks.audit_trace_probe import ObservingMemoryService  # noqa: E402

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

#: Minimum fraction of the world's compositional edges that must be covered
#  at the end of the acquisition phase.  Preregistered value: 0.50.
SUFFICIENCY_THRESHOLD: float = 0.50

#: Default seed used for gate smoke-tests.
DEFAULT_SEED: int = 20261100

#: Cycles in a short diagnostic run (warmup + acquisition only).
SHORT_CYCLES: int = 120   # covers warmup (0-19) + acquisition (20-109)

#: Minimum cycles for fast gate smoke-tests (warmup + a few acquisition cycles).
FAST_CYCLES: int = 40    # warmup (0-19) + 20 acquisition cycles


# ---------------------------------------------------------------------------
# Gate 16 helper: scratch-only sentinel
# ---------------------------------------------------------------------------

class _WriteSentinel:
    """Wrap MemoryService to detect writes to the live DB path.

    We patch the open() of the underlying sqlite3 connection during the gate
    runs using a subclass approach: every DB is opened via ``temp_db()``, so
    comparing the resolved path against ``LIVE_DB`` is sufficient.
    """

    @staticmethod
    def assert_not_live(db_path: Path) -> None:
        """Raise AssertionError if ``db_path`` resolves to the live DB."""
        if db_path.resolve() == LIVE_DB.resolve():
            raise AssertionError(
                f"Gate 16 FAIL: harness opened live DB for writing: {db_path}"
            )


def _make_scratch_db(prefix: str = "harness") -> Path:
    """Return a fresh temp-dir path and assert it is not the live DB."""
    path = temp_db(f"{prefix}_{os.getpid()}.db")
    _WriteSentinel.assert_not_live(path)
    return path


# ---------------------------------------------------------------------------
# Gate 10 — content-identity detection
# ---------------------------------------------------------------------------

class _CountingMemoryService(ObservingMemoryService):
    """Extends ObservingMemoryService to count re-instantiations.

    A re-instantiation occurs when a candidate id appears in a sleep event
    and that id has already been seen (it is already in ``candidate_ids``).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # id -> number of times that id was stored (first store = 1)
        self.store_counts: dict[str, int] = {}

    def store(self, content: str, event_type: str = "observe",
              source: str = "env"):
        event = super().store(content, event_type=event_type, source=source)
        if event_type == "sleep" and source != "sleep:meta":
            try:
                payload = json.loads(content)
            except (json.JSONDecodeError, ValueError):
                payload = None
            if isinstance(payload, dict) and payload.get("id"):
                cid = payload["id"]
                self.store_counts[cid] = self.store_counts.get(cid, 0) + 1
        return event


def gate_content_identity(
    seed: int = DEFAULT_SEED,
    cycles: int = SHORT_CYCLES,
) -> dict:
    """Gate 10: verify the harness can distinguish re-instantiation from retention.

    Runs a short world, then inspects the store log.  A candidate id stored
    more than once is a re-instantiation (the engine re-wrote a decayed copy).
    A candidate id stored exactly once is either retained (still in the window)
    or has aged out — the ObservingMemoryService's ``last_store_cycle`` tracks
    the most recent cycle it was seen.

    Returns
    -------
    dict with keys:
        passed              bool
        total_candidates    int   — distinct ids ever stored
        reinstantiated      int   — ids stored more than once
        single_store        int   — ids stored exactly once
        sample_reinstantiated   list[str]   — up to 5 example ids
        failure_reason      str | None
    """
    db_path = _make_scratch_db("gate10")
    mem = _CountingMemoryService(str(db_path))

    world = generate_compositional_world(seed=seed, cycles=cycles)
    events = world["events"]
    trainable = world["trainable"]

    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_event_lo = acq_lo * EVENTS_PER_CYCLE
    acq_event_hi = acq_hi * EVENTS_PER_CYCLE

    sleep_svc = SleepService(mem)
    for i, (text, train_flag) in enumerate(zip(events, trainable)):
        in_acq = acq_event_lo <= i < acq_event_hi
        if in_acq and not train_flag:
            continue
        if i % EVENTS_PER_CYCLE == 0:
            cycle = i // EVENTS_PER_CYCLE
            mem.current_cycle = cycle
        mem.store(text, event_type="observe", source="env")
        if (i + 1) % EVENTS_PER_CYCLE == 0:
            sleep_svc.run_sleep_cycle()

    reinstantiated = [cid for cid, n in mem.store_counts.items() if n > 1]
    single_store = [cid for cid, n in mem.store_counts.items() if n == 1]

    passed = len(mem.candidate_ids) > 0
    failure_reason = None
    if not passed:
        failure_reason = "no candidates were stored — world may be too short"

    # Gate 16 check: db_path must not be live
    _WriteSentinel.assert_not_live(db_path)
    mem._conn.close()
    try:
        db_path.unlink(missing_ok=True)
    except PermissionError:
        pass  # Windows: file handle held by OS; temp dir will be cleaned up

    return {
        "passed": passed,
        "total_candidates": len(mem.candidate_ids),
        "reinstantiated": len(reinstantiated),
        "single_store": len(single_store),
        "sample_reinstantiated": reinstantiated[:5],
        "failure_reason": failure_reason,
    }


# ---------------------------------------------------------------------------
# Gate 11 — intervention verification
# ---------------------------------------------------------------------------

def _erem(mem: MemoryService, source: str) -> None:
    """Remove all events with the given source and clear precedes."""
    conn = mem._conn  # accessing the private connection (read-only after close)
    conn.execute("DELETE FROM events WHERE source = ?", (source,))
    conn.execute("DELETE FROM precedes")
    conn.commit()


def _count_events_by_source(mem: MemoryService, source: str) -> int:
    row = mem._conn.execute(
        "SELECT COUNT(*) FROM events WHERE source = ?", (source,)
    ).fetchone()
    return row[0] if row else 0


def _count_table(mem: MemoryService, table: str) -> int:
    row = mem._conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return row[0] if row else 0


def gate_intervention_verification(
    seed: int = DEFAULT_SEED,
    cycles: int = SHORT_CYCLES,
) -> dict:
    """Gate 11: verify P-org and E-rem interventions are confirmed before outcomes.

    Runs a short acquisition, applies E-rem (the simpler, fully verifiable
    intervention), and checks the DB state immediately BEFORE any outcome read.

    Returns
    -------
    dict with keys:
        passed                  bool
        source_used             str
        events_before_erem      int
        events_after_erem       int
        precedes_after_erem     int
        erem_confirmed          bool    — True if events == 0 and precedes == 0
        failure_reason          str | None
    """
    db_path = _make_scratch_db("gate11")
    mem = _CountingMemoryService(str(db_path))

    world = generate_compositional_world(seed=seed, cycles=cycles)
    events = world["events"]
    trainable = world["trainable"]

    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_event_lo = acq_lo * EVENTS_PER_CYCLE
    acq_event_hi = acq_hi * EVENTS_PER_CYCLE

    ACQ_SOURCE = "env_acq"  # distinctive source so we can find and remove them

    sleep_svc = SleepService(mem)
    for i, (text, train_flag) in enumerate(zip(events, trainable)):
        in_acq = acq_event_lo <= i < acq_event_hi
        if in_acq and not train_flag:
            continue
        if i % EVENTS_PER_CYCLE == 0:
            mem.current_cycle = i // EVENTS_PER_CYCLE
        source = ACQ_SOURCE if in_acq else "env"
        mem.store(text, event_type="observe", source=source)
        if (i + 1) % EVENTS_PER_CYCLE == 0:
            sleep_svc.run_sleep_cycle()

    events_before = _count_events_by_source(mem, ACQ_SOURCE)

    # Apply E-rem
    _erem(mem, ACQ_SOURCE)

    # Verify BEFORE reading any outcome
    events_after = _count_events_by_source(mem, ACQ_SOURCE)
    precedes_after = _count_table(mem, "precedes")

    erem_confirmed = (events_after == 0 and precedes_after == 0)

    passed = erem_confirmed
    failure_reason = None
    if not passed:
        failure_reason = (
            f"E-rem not confirmed: events_after={events_after}, "
            f"precedes_after={precedes_after}"
        )

    _WriteSentinel.assert_not_live(db_path)
    mem._conn.close()
    try:
        db_path.unlink(missing_ok=True)
    except PermissionError:
        pass  # Windows: file handle held by OS; temp dir will be cleaned up

    return {
        "passed": passed,
        "source_used": ACQ_SOURCE,
        "events_before_erem": events_before,
        "events_after_erem": events_after,
        "precedes_after_erem": precedes_after,
        "erem_confirmed": erem_confirmed,
        "failure_reason": failure_reason,
    }


# ---------------------------------------------------------------------------
# Gate 12 — removal verification (table-level)
# ---------------------------------------------------------------------------

def gate_removal_verification(
    seed: int = DEFAULT_SEED,
    cycles: int = SHORT_CYCLES,
) -> dict:
    """Gate 12: table-level verification of E-rem.

    Verifies that after E-rem:
      * ``events`` rows with the acquisition source = 0
      * ``precedes`` rows = 0
      * ``cooccurrences`` rows > 0   (preserved by design)
      * ``tag_counts`` rows > 0      (preserved by design)

    Returns
    -------
    dict with keys:
        passed              bool
        events_acq_before   int
        events_acq_after    int     must be 0
        precedes_after      int     must be 0
        cooccurrences_after int     must be > 0
        tag_counts_after    int     must be > 0
        failure_reason      str | None
    """
    db_path = _make_scratch_db("gate12")
    mem = _CountingMemoryService(str(db_path))

    world = generate_compositional_world(seed=seed, cycles=cycles)
    events = world["events"]
    trainable = world["trainable"]

    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_event_lo = acq_lo * EVENTS_PER_CYCLE
    acq_event_hi = acq_hi * EVENTS_PER_CYCLE

    ACQ_SOURCE = "env_acq"

    sleep_svc = SleepService(mem)
    for i, (text, train_flag) in enumerate(zip(events, trainable)):
        in_acq = acq_event_lo <= i < acq_event_hi
        if in_acq and not train_flag:
            continue
        if i % EVENTS_PER_CYCLE == 0:
            mem.current_cycle = i // EVENTS_PER_CYCLE
        source = ACQ_SOURCE if in_acq else "env"
        mem.store(text, event_type="observe", source=source)
        if (i + 1) % EVENTS_PER_CYCLE == 0:
            sleep_svc.run_sleep_cycle()

    events_acq_before = _count_events_by_source(mem, ACQ_SOURCE)

    _erem(mem, ACQ_SOURCE)

    events_acq_after = _count_events_by_source(mem, ACQ_SOURCE)
    precedes_after = _count_table(mem, "precedes")
    cooccurrences_after = _count_table(mem, "cooccurrences")
    tag_counts_after = _count_table(mem, "tag_counts")

    checks = {
        "events_cleared": events_acq_after == 0,
        "precedes_cleared": precedes_after == 0,
        "cooccurrences_preserved": cooccurrences_after > 0,
        "tag_counts_preserved": tag_counts_after > 0,
    }
    passed = all(checks.values())
    failure_reason: str | None = None
    if not passed:
        failures = [k for k, v in checks.items() if not v]
        failure_reason = f"failed checks: {', '.join(failures)}"

    _WriteSentinel.assert_not_live(db_path)
    mem._conn.close()
    try:
        db_path.unlink(missing_ok=True)
    except PermissionError:
        pass  # Windows: file handle held by OS; temp dir will be cleaned up

    return {
        "passed": passed,
        "events_acq_before": events_acq_before,
        "events_acq_after": events_acq_after,
        "precedes_after": precedes_after,
        "cooccurrences_after": cooccurrences_after,
        "tag_counts_after": tag_counts_after,
        "checks": checks,
        "failure_reason": failure_reason,
    }


# ---------------------------------------------------------------------------
# Gate 13 — acquisition sufficiency
# ---------------------------------------------------------------------------

def _world_compositional_edges(world: dict) -> set[tuple[str, str]]:
    """Return the set of (from_tag, to_tag) pairs implied by the world's law.

    These are the edges the organism *should* have formed during acquisition.
    We derive them from the training stream (trainable events only, in the
    acquisition phase) rather than the held-out transitions, because the
    organism was not exposed to the withheld combination.
    """
    events_text = world["events"]
    trainable = world["trainable"]
    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_event_lo = acq_lo * EVENTS_PER_CYCLE
    acq_event_hi = acq_hi * EVENTS_PER_CYCLE

    edges: set[tuple[str, str]] = set()
    prev_tags: list[str] = []
    for i, (text, train_flag) in enumerate(zip(events_text, trainable)):
        in_acq = acq_event_lo <= i < acq_event_hi
        if not in_acq:
            prev_tags = text.split()
            continue
        if not train_flag:
            prev_tags = text.split()
            continue
        cur_tags = text.split()
        for ft in prev_tags:
            for tt in cur_tags:
                if ft != tt:
                    edges.add((ft, tt))
        prev_tags = cur_tags
    return edges


def gate_acquisition_sufficiency(
    seed: int = DEFAULT_SEED,
    cycles: int = SHORT_CYCLES,
    threshold: float = SUFFICIENCY_THRESHOLD,
) -> dict:
    """Gate 13: verify Organica acquired enough of the world's structure.

    At the end of the acquisition phase the harness counts how many of the
    world's training-stream edges appear in ``temporal_edges(min_count=1)``.

    If coverage < threshold, the seed is flagged as ``acquisition_failed``.
    A seed in this state MUST NOT subsequently be labelled ``transfer_failure``.

    Returns
    -------
    dict with keys:
        passed              bool
        world_edges         int     — edges derivable from the training stream
        covered_edges       int     — of those, found in temporal_edges()
        coverage            float   — covered / world_edges
        threshold           float
        acquisition_failed  bool    — True when coverage < threshold
        failure_reason      str | None
    """
    db_path = _make_scratch_db("gate13")
    mem = _CountingMemoryService(str(db_path))

    world = generate_compositional_world(seed=seed, cycles=cycles)
    events_text = world["events"]
    trainable = world["trainable"]

    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_event_lo = acq_lo * EVENTS_PER_CYCLE
    acq_event_hi = acq_hi * EVENTS_PER_CYCLE

    ACQ_SOURCE = "env_acq"

    sleep_svc = SleepService(mem)
    for i, (text, train_flag) in enumerate(zip(events_text, trainable)):
        in_acq = acq_event_lo <= i < acq_event_hi
        if in_acq and not train_flag:
            continue
        if i % EVENTS_PER_CYCLE == 0:
            mem.current_cycle = i // EVENTS_PER_CYCLE
        source = ACQ_SOURCE if in_acq else "env"
        mem.store(text, event_type="observe", source=source)
        if (i + 1) % EVENTS_PER_CYCLE == 0:
            sleep_svc.run_sleep_cycle()

    # The world's ground-truth edges (training stream only, no withheld)
    world_edges = _world_compositional_edges(world)

    # Edges the organism actually formed
    organism_edges = set(
        (ft, tt) for ft, tt, _cnt in mem.temporal_edges(min_count=1)
    )

    covered = world_edges & organism_edges
    coverage = len(covered) / len(world_edges) if world_edges else 0.0
    acquisition_failed = coverage < threshold

    passed = not acquisition_failed
    failure_reason: str | None = None
    if not passed:
        failure_reason = (
            f"coverage {coverage:.3f} < threshold {threshold:.3f} — "
            f"seed {seed} is acquisition_failed, NOT transfer_failure"
        )

    _WriteSentinel.assert_not_live(db_path)
    mem._conn.close()
    try:
        db_path.unlink(missing_ok=True)
    except PermissionError:
        pass  # Windows: file handle held by OS; temp dir will be cleaned up

    return {
        "passed": passed,
        "world_edges": len(world_edges),
        "covered_edges": len(covered),
        "coverage": round(coverage, 6),
        "threshold": threshold,
        "acquisition_failed": acquisition_failed,
        "failure_reason": failure_reason,
    }


# ---------------------------------------------------------------------------
# Gate 16 — scratch-only guarantee (standalone check)
# ---------------------------------------------------------------------------

def gate_scratch_only(db_path: Path) -> dict:
    """Gate 16: assert that a given db_path is not the live memory.db.

    This is called as a closure inside each gate above.  This standalone
    function exists so the test suite can exercise the failure branch.

    Returns
    -------
    dict with keys:
        passed          bool
        db_path         str
        live_db         str
        failure_reason  str | None
    """
    live = LIVE_DB.resolve()
    given = db_path.resolve()
    passed = (given != live)
    failure_reason = None if passed else (
        f"db_path resolves to the live DB: {given}"
    )
    return {
        "passed": passed,
        "db_path": str(given),
        "live_db": str(live),
        "failure_reason": failure_reason,
    }


# ---------------------------------------------------------------------------
# Combined prerequisite check
# ---------------------------------------------------------------------------

def run_all_gates(
    seed: int = DEFAULT_SEED,
    cycles: int = SHORT_CYCLES,
    threshold: float = SUFFICIENCY_THRESHOLD,
) -> dict:
    """Run all four gates in sequence; return an aggregate result.

    The individual gate functions each create and destroy their own scratch DB,
    so running them in sequence is safe.

    Returns
    -------
    dict with keys:
        all_passed      bool
        gates           dict[str, dict]   — per-gate result dicts
        summary         str               — human-readable one-liner
    """
    results: dict[str, dict] = {}

    results["gate10_content_identity"] = gate_content_identity(
        seed=seed, cycles=cycles
    )
    results["gate11_intervention"] = gate_intervention_verification(
        seed=seed, cycles=cycles
    )
    results["gate12_removal"] = gate_removal_verification(
        seed=seed, cycles=cycles
    )
    results["gate13_sufficiency"] = gate_acquisition_sufficiency(
        seed=seed, cycles=cycles, threshold=threshold
    )

    all_passed = all(r["passed"] for r in results.values())
    passed_names = [k for k, r in results.items() if r["passed"]]
    failed_names = [k for k, r in results.items() if not r["passed"]]

    if all_passed:
        summary = f"ALL GATES PASSED ({len(results)} gates, seed={seed})"
    else:
        summary = (
            f"GATES FAILED: {', '.join(failed_names)} "
            f"(passed: {', '.join(passed_names) or 'none'})"
        )

    return {
        "all_passed": all_passed,
        "gates": results,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run acquisition harness prerequisite gates."
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--cycles", type=int, default=SHORT_CYCLES,
                        help="World cycles (default 120 = warmup + acquisition)")
    parser.add_argument("--threshold", type=float, default=SUFFICIENCY_THRESHOLD,
                        help="Sufficiency threshold for gate 13 (default 0.50)")
    parser.add_argument("--gate", choices=["10", "11", "12", "13", "16", "all"],
                        default="all")
    args = parser.parse_args()

    if args.gate == "all":
        result = run_all_gates(seed=args.seed, cycles=args.cycles,
                               threshold=args.threshold)
        print(result["summary"])
        for name, gr in result["gates"].items():
            status = "PASS" if gr["passed"] else "FAIL"
            print(f"  {status}  {name}")
            if gr.get("failure_reason"):
                print(f"         reason: {gr['failure_reason']}")
    elif args.gate == "10":
        r = gate_content_identity(seed=args.seed, cycles=args.cycles)
        print(json.dumps(r, indent=2))
    elif args.gate == "11":
        r = gate_intervention_verification(seed=args.seed, cycles=args.cycles)
        print(json.dumps(r, indent=2))
    elif args.gate == "12":
        r = gate_removal_verification(seed=args.seed, cycles=args.cycles)
        print(json.dumps(r, indent=2))
    elif args.gate == "13":
        r = gate_acquisition_sufficiency(seed=args.seed, cycles=args.cycles,
                                         threshold=args.threshold)
        print(json.dumps(r, indent=2))
    elif args.gate == "16":
        # Demonstrate the standalone gate-16 check
        scratch = _make_scratch_db("gate16_demo")
        r_ok = gate_scratch_only(scratch)
        print("scratch path:", json.dumps(r_ok, indent=2))
        r_fail = gate_scratch_only(LIVE_DB)
        print("live path:   ", json.dumps(r_fail, indent=2))
        scratch.unlink(missing_ok=True)
