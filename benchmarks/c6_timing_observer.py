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

from benchmarks.acquisition_runner import structure_edges
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


def report_candidates_as_dicts(report: Any) -> list[dict]:
    """Serialize the report's candidate lists without reading the database."""
    out: list[dict] = []
    for field in REPORT_FIELDS:
        for candidate in getattr(report, field, []) or []:
            out.append(_candidate_dict(candidate))
    return out


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
        self.observer.record(report.cycle, report_candidates_as_dicts(report))
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
    args = parser.parse_args(argv)
    if not args.self_test:
        parser.error("--self-test is required")

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
