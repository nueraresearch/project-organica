"""Passive C6 assertion-timing observer and its neutrality harness.

The observer records the three readouts specified in
``docs/C6-ASSERTION-TIMING-INSTRUMENTATION.md``:

  Y_full  -- assertion from all structures (parity with the engine)
  Y_ind   -- assertion from non-carrier structures (the C6 ordering readout)
  K       -- assertion from loop/dream carriers

It is a benchmark-only ``SleepService`` subclass.  It calls the parent cycle
once, reads the returned ``SleepReport`` and never edits an engine file, a
frozen artifact or the live database.

Usage:
    python -m benchmarks.c6_timing_observer --self-test
    python -m benchmarks.c6_timing_observer --self-test --cycles 8 --seed 20611601
"""

from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
import random
import tempfile
import time
import uuid
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.presence_construct_audit import (
    ACQ_SOURCE,
    PHASE_ACQUISITION,
    _world_compositional_edges,
)
from organica.memory import MemoryService
from organica.sleep import SleepService

REPORT_FIELDS = (
    "concepts",
    "phrases",
    "loops",
    "predictions",
    "anomalies",
    "meta_concepts",
    "processes",
    "roles",
    "workflow_concepts",
    "schemas",
    "hypotheses",
    "theories",
    "questions",
    "dreams",
    "investigations",
    "experiments",
)

CARRIER_TYPES = frozenset({"loop_candidate", "dream"})


def _candidate_dict(candidate: Any) -> dict:
    if isinstance(candidate, dict):
        return candidate
    if is_dataclass(candidate):
        return asdict(candidate)
    raise TypeError("unsupported candidate type: %r" % (type(candidate),))


def canonical_report(report: Any) -> dict:
    """A deterministic report view; excludes the wall-clock ``ran_at`` field."""
    payload = asdict(report) if is_dataclass(report) else dict(report)
    payload.pop("ran_at", None)
    return payload


def edge_set(structure: dict[str, dict[str, float]]) -> set[tuple[str, str]]:
    return {
        (str(source), str(target))
        for source, targets in structure.items()
        for target in targets
    }


def readouts(candidates: list[dict]) -> dict[str, set[tuple[str, str]]]:
    """Compute Y_full, Y_ind and K from the same candidate snapshot."""
    carrier = [c for c in candidates if c.get("type") in CARRIER_TYPES]
    independent = [c for c in candidates if c.get("type") not in CARRIER_TYPES]
    return {
        "y_full": edge_set(structure_edges(candidates)),
        "y_ind": edge_set(structure_edges(independent)),
        "k": edge_set(structure_edges(carrier)),
    }


class TimingObserver:
    """Per-edge first/last timing for the three C6 readouts."""

    def __init__(self, seed: int | None = None) -> None:
        self.seed = seed
        self.edges: dict[tuple[str, str], dict] = {}
        self.cycles: list[dict] = []
        self.last: dict[str, set[tuple[str, str]]] = {
            "y_full": set(),
            "y_ind": set(),
            "k": set(),
        }

    def _state(self, edge: tuple[str, str]) -> dict:
        if edge not in self.edges:
            self.edges[edge] = {
                "edge": "%s>%s" % edge,
                "first_y_full": None,
                "first_y_ind": None,
                "first_k": None,
                "last_y_full": None,
                "last_y_ind": None,
                "last_k": None,
                "y_full_cycles": 0,
                "y_ind_cycles": 0,
                "k_cycles": 0,
            }
        return self.edges[edge]

    def record(self, cycle: int, candidates: list[dict]) -> None:
        current = readouts(candidates)
        self.last = current
        self.cycles.append(
            {
                "cycle": int(cycle),
                "y_full": len(current["y_full"]),
                "y_ind": len(current["y_ind"]),
                "k": len(current["k"]),
            }
        )
        for edge in current["y_full"]:
            state = self._state(edge)
            if state["first_y_full"] is None:
                state["first_y_full"] = int(cycle)
            state["last_y_full"] = int(cycle)
            state["y_full_cycles"] += 1
        for edge in current["y_ind"]:
            state = self._state(edge)
            if state["first_y_ind"] is None:
                state["first_y_ind"] = int(cycle)
            state["last_y_ind"] = int(cycle)
            state["y_ind_cycles"] += 1
        for edge in current["k"]:
            state = self._state(edge)
            if state["first_k"] is None:
                state["first_k"] = int(cycle)
            state["last_k"] = int(cycle)
            state["k_cycles"] += 1

    def classify(self, state: dict) -> str:
        first_k = state["first_k"]
        first_ind = state["first_y_ind"]
        if first_k is None and first_ind is None:
            return "NO_READOUT"
        if first_ind is None:
            return "NO_Y_IND"
        if first_k is None:
            return "NO_K"
        if first_k < first_ind:
            return "K_BEFORE_Y_IND"
        if first_ind < first_k:
            return "Y_IND_BEFORE_K"
        return "SAME_CYCLE"

    def summary(self) -> dict:
        rows = []
        for state in sorted(self.edges.values(), key=lambda row: row["edge"]):
            row = dict(state)
            row["class"] = self.classify(row)
            rows.append(row)
        classes: dict[str, int] = {}
        for row in rows:
            classes[row["class"]] = classes.get(row["class"], 0) + 1
        return {
            "edges": len(rows),
            "y_full_edges": sum(1 for row in rows if row["first_y_full"] is not None),
            "y_ind_edges": sum(1 for row in rows if row["first_y_ind"] is not None),
            "k_edges": sum(1 for row in rows if row["first_k"] is not None),
            "classes": dict(sorted(classes.items())),
            "order_variation": (
                "K_BEFORE_Y_IND" in classes and "Y_IND_BEFORE_K" in classes
            ),
            "last_y_full": sorted("%s>%s" % edge for edge in self.last["y_full"]),
            "last_y_ind": sorted("%s>%s" % edge for edge in self.last["y_ind"]),
            "last_k": sorted("%s>%s" % edge for edge in self.last["k"]),
            "rows": rows,
        }


class TimingObservedSleepService(SleepService):
    """SleepService that records the C6 readouts after each normal cycle."""

    def __init__(
        self,
        memory: MemoryService,
        observer: TimingObserver,
        *,
        mutate_report: bool = False,
    ) -> None:
        super().__init__(memory)
        self.observer = observer
        self.mutate_report = mutate_report
        self.mutation_applied = False

    def run_sleep_cycle(self):
        report = super().run_sleep_cycle()
        if self.mutate_report:
            self.mutation_applied = _mutate_report(report)
        # The report holds this cycle's emitted candidates, not every live
        # survivor carried in the database. The final readout uses the live
        # set, so the observer snapshots the same set, read-only, after the
        # cycle. _load_prior_candidates() does not populate the cache.
        snapshot = self._load_prior_candidates()
        self.observer.record(report.cycle, snapshot)
        return report


def _mutate_report(report: Any) -> bool:
    """Test-only mutation that must make the neutrality comparison fail."""
    for field in REPORT_FIELDS:
        candidates = getattr(report, field, []) or []
        for candidate in candidates:
            if hasattr(candidate, "members"):
                candidate.members = list(candidate.members) + ["mutation"]
                return True
            if hasattr(candidate, "path"):
                candidate.path = list(candidate.path) + ["mutation"]
                return True
            if hasattr(candidate, "confidence"):
                candidate.confidence = float(candidate.confidence) + 1.0
                return True
    report.cycle = int(report.cycle) + 1000000
    return True


def _scenario() -> list[str]:
    """A deterministic event stream long enough to form candidates."""
    return [
        "amber birch cedar delta",
        "birch cedar delta ember",
        "cedar delta ember flora",
        "delta ember flora amber",
        "ember flora amber birch",
        "flora amber birch cedar",
        "amber cedar ember flora",
        "birch delta flora amber",
    ]


def _run_arm(
    *,
    cycles: int,
    seed: int,
    observed: bool,
    mutate: bool,
    events: list[str],
) -> dict:
    random_state = random.getstate()
    original_uuid4 = uuid.uuid4
    original_time = time.time
    uid_counter = itertools.count(1)
    tick_counter = itertools.count()
    try:
        random.seed(seed)
        # Event ids and wall-clock times are generation noise, not engine
        # behaviour. Fix both so the off/on comparison tests the observer.
        uuid.uuid4 = lambda: uuid.UUID(int=next(uid_counter))
        time.time = lambda: 1700000000.0 + next(tick_counter) * 1e-6
        with tempfile.TemporaryDirectory(prefix="c6_timing_") as tmp:
            db = Path(tmp) / "c6.db"
            memory = MemoryService(str(db))
            observer = TimingObserver(seed)
            if observed:
                service = TimingObservedSleepService(
                    memory, observer, mutate_report=mutate
                )
            else:
                service = SleepService(memory)
            reports = []
            try:
                for _ in range(cycles):
                    for content in events:
                        memory.store(content, event_type="observe", source="env")
                    reports.append(canonical_report(service.run_sleep_cycle()))
                final_full = edge_set(
                    structure_edges(service._load_prior_candidates())
                )
            finally:
                memory.close()
    finally:
        uuid.uuid4 = original_uuid4
        time.time = original_time
        random.setstate(random_state)
    return {
        "reports": reports,
        "final_full": sorted("%s>%s" % edge for edge in final_full),
        "observer": observer.summary() if observed else None,
        "mutation_applied": bool(
            getattr(service, "mutation_applied", False) if observed else False
        ),
    }


def _world_edge_rows(summary: dict, world_edges: set[tuple[str, str]]) -> list[dict]:
    rows = []
    for row in summary["rows"]:
        edge = tuple(row["edge"].split(">", 1))
        if len(edge) == 2 and edge in world_edges:
            rows.append(dict(row, class_=row["class"]))
    return rows


def _run_world_arm(*, seed: int, cycles: int, cap: int, observed: bool) -> dict:
    random_state = random.getstate()
    original_uuid4 = uuid.uuid4
    original_time = time.time
    uid_counter = itertools.count(1)
    tick_counter = itertools.count()
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("c6_one_seed_%s" % ("on" if observed else "off"))
    memory = MemoryService(str(db_path))
    observer = TimingObserver(seed)
    service = (
        TimingObservedSleepService(memory, observer)
        if observed
        else SleepService(memory)
    )
    service.MAX_PREDICTIONS = int(cap)
    reports = []
    try:
        random.seed(seed)
        # Generation noise must be identical across the two arms.
        uuid.uuid4 = lambda: uuid.UUID(int=next(uid_counter))
        time.time = lambda: 1700000000.0 + next(tick_counter) * 1e-6
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = (
                PHASE_ACQUISITION[0] * EVENTS_PER_CYCLE
                <= i < PHASE_ACQUISITION[1] * EVENTS_PER_CYCLE
            )
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            memory.store(
                text,
                event_type="observe",
                source=ACQ_SOURCE if in_acq else "env",
            )
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                reports.append(canonical_report(service.run_sleep_cycle()))
        final_full = edge_set(structure_edges(service._load_prior_candidates()))
    finally:
        memory.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass
        uuid.uuid4 = original_uuid4
        time.time = original_time
        random.setstate(random_state)
    return {
        "reports": reports,
        "world_edges": world_edges,
        "final_full": final_full,
        "observer": observer.summary() if observed else None,
    }


def run_one_seed(*, seed: int = 20611601, cycles: int = 120, cap: int = 40) -> dict:
    """Run the real Q4-shaped world off and on, then report the C6 preflight."""
    off = _run_world_arm(seed=seed, cycles=cycles, cap=cap, observed=False)
    on = _run_world_arm(seed=seed, cycles=cycles, cap=cap, observed=True)
    world_edges = on["world_edges"]
    rows = _world_edge_rows(on["observer"], world_edges)
    classes: dict[str, int] = {}
    for row in rows:
        classes[row["class_"]] = classes.get(row["class_"], 0) + 1
    y_ind_edges = sum(1 for row in rows if row["first_y_ind"] is not None)
    k_edges = sum(1 for row in rows if row["first_k"] is not None)
    order_variation = (
        "K_BEFORE_Y_IND" in classes and "Y_IND_BEFORE_K" in classes
    )
    n1 = off["reports"] == on["reports"]
    n3 = on["observer"]["last_y_full"] == sorted(
        "%s>%s" % edge for edge in on["final_full"]
    )
    if not n1 or not n3:
        verdict = "HARNESS FAILED"
    elif not y_ind_edges:
        verdict = "C6 NOT MEASURABLE"
    elif not order_variation:
        verdict = "C6 NOT SEPARATED"
    else:
        verdict = "C6 ORDER VARIATION PRESENT"

    asserted_world = on["final_full"] & world_edges
    return {
        "kind": "c6_one_seed_preflight",
        "not_a_result": True,
        "seed": seed,
        "cycles": cycles,
        "cap": cap,
        "world_edges": len(world_edges),
        "asserted_world_edges": len(asserted_world),
        "y_full_edges": sum(1 for row in rows if row["first_y_full"] is not None),
        "y_ind_edges": y_ind_edges,
        "k_edges": k_edges,
        "classes": dict(sorted(classes.items())),
        "order_variation": order_variation,
        "gates": {
            "N1_neutrality": n1,
            "N3_parity": n3,
            "N6_order_variation": order_variation,
        },
        "verdict": verdict,
        "rows": rows,
        "not_evidence": (
            "One seed, one world family, one build and one cap. It is a C6 "
            "preflight, not a seed block and not a mechanism result."
        ),
    }


def self_test(*, cycles: int = 8, seed: int = 20611601) -> dict:
    events = _scenario()
    off = _run_arm(
        cycles=cycles, seed=seed, observed=False, mutate=False, events=events
    )
    on = _run_arm(
        cycles=cycles, seed=seed, observed=True, mutate=False, events=events
    )
    mutated = _run_arm(
        cycles=cycles, seed=seed, observed=True, mutate=True, events=events
    )

    n1 = off["reports"] == on["reports"]
    n2 = (off["reports"] != mutated["reports"]) and mutated["mutation_applied"]
    n3 = (
        on["observer"] is not None
        and on["observer"]["last_y_full"] == on["final_full"]
    )
    n6 = bool(on["observer"] and on["observer"]["order_variation"])

    if not n1 or not n2 or not n3:
        verdict = "HARNESS FAILED"
    elif n6:
        verdict = "C6 ORDER VARIATION PRESENT"
    elif on["observer"] and on["observer"]["y_ind_edges"]:
        verdict = "C6 NOT SEPARATED"
    else:
        verdict = "C6 NOT MEASURABLE"

    return {
        "kind": "c6_timing_observer_self_test",
        "not_a_result": True,
        "seed": seed,
        "cycles": cycles,
        "gates": {
            "N1_neutrality": n1,
            "N2_mutation_fails": n2,
            "N3_parity": n3,
            "N6_order_variation": n6,
        },
        "verdict": verdict,
        "off_final_full": off["final_full"],
        "on_final_full": on["final_full"],
        "observer": on["observer"],
        "not_evidence": (
            "A short harness self-test on one synthetic stream. It does not run the "
            "C6 seed block and does not measure a mechanism."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the passive-observer neutrality/mutation harness",
    )
    parser.add_argument("--cycles", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20611601)
    parser.add_argument("--json", action="store_true", help="print the full JSON")
    parser.add_argument(
        "--run-one-seed",
        action="store_true",
        help="run the real 120-cycle Q4-shaped world once and report C6 preflight",
    )
    args = parser.parse_args(argv)
    if not args.self_test and not args.run_one_seed:
        parser.error("choose --self-test or --run-one-seed")

    if args.run_one_seed:
        result = run_one_seed(seed=args.seed, cycles=120, cap=40)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    result = self_test(cycles=args.cycles, seed=args.seed)
    gates = result["gates"]
    print(
        "C6 observer self-test: N1=%s N2=%s N3=%s N6=%s; %s"
        % (
            gates["N1_neutrality"],
            gates["N2_mutation_fails"],
            gates["N3_parity"],
            gates["N6_order_variation"],
            result["verdict"],
        )
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if all(
        gates[key] for key in ("N1_neutrality", "N2_mutation_fails", "N3_parity")
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
