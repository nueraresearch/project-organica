"""PRESENCE-CONVERSION-2: the repaired conversion observer, built and fixture-proven.

Q3's observer was not neutral because it lifted the cap *before* the only call and returned the
first ``cap`` rows of the lifted list. That made the served window depend on the diagnostic
ceiling: the engine allocates the quota from ``MAX_PREDICTIONS`` (half the budget to transitions,
the rest to cooccurrences), so raising the cap changes *which* rows are served, not merely how
many. The block's repair is to change the order:

1. call the engine's own ``_build_predictions`` at the shipped cap and keep that list -- it is
   the served window, returned untouched;
2. call it a second time with ``MAX_PREDICTIONS`` temporarily at the diagnostic ceiling, record
   the full pre-cap universe (rank, edge, strength, support, relation), and throw the list away;
3. restore the cap.

The second call is observation only. The engine permits it -- ``_prediction_frequencies`` updates
once per sleep cycle, candidate ids are content hashes with no counter, and ``_build_predictions``
performs no memory write -- but it is not assumed: ``fixture()`` below runs three arms on one
fixture world and ``differs()`` compares them channel by channel, including the *next* cycle and
the memory rows.

No cell has run and none may run: this module has no cell entry point, runs only at fixture scale
(24 cycles), at the shipped cap and at 80 and 112 on two seeds, and ``organica/`` is not
edited.

    ./.venv/bin/python -m benchmarks.presence_conversion_repair_observer --fixture
"""
from __future__ import annotations

import functools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from organica.sleep import SleepService                                        # noqa: E402
from benchmarks.acquisition_compositional import generate_compositional_world  # noqa: E402
from benchmarks.acquisition_harness import (                                   # noqa: E402
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges     # noqa: E402

CEILING = 10 ** 9
SHIPPED_CAP = 40
FIXTURE_SEED = 20261110
SECOND_SEED = 20261118
FIXTURE_CYCLES = 24
RELATIONS = ("transition", "cooccurrence")


def relation(candidate) -> str:
    """`transition` or `cooccurrence`, read from the engine's own evidence flag.

    The engine appends each constructed candidate to one of two lists and sets
    ``evidence["is_cooccurrence"]`` accordingly, so the label is read rather than guessed. A
    candidate without the flag is ``unknown``, and N3 counts it: an inferred label would make the
    allocation record look complete while it was not.
    """
    evidence = getattr(candidate, "evidence", None)
    if not isinstance(evidence, dict):
        return "unknown"
    flag = evidence.get("is_cooccurrence")
    if flag is True:
        return "cooccurrence"
    if flag is False:
        return "transition"
    return "unknown"


def cooccurrence_pairs(cooc) -> set[tuple[str, str]]:
    """The engine's own cooccurrence table, as unordered pairs, rebuilt from its state."""
    pairs: set[tuple[str, str]] = set()
    for source, targets in (cooc or {}).items():
        for target in targets:
            pairs.add(tuple(sorted([source, target])))
    return pairs


def label_from_pairs(source: str, target: str, pairs: set[tuple[str, str]]) -> str:
    return "cooccurrence" if tuple(sorted([source, target])) in pairs else "transition"


def expected_relation(source: str, target: str, cooc) -> str:
    """The label the engine's construction implies, computed from the engine's cooccurrence
    table rather than read from the candidate. `relation()` reads the flag the engine sets in
    the same branch that chooses the append list; this function is the independent check."""
    return label_from_pairs(source, target, cooccurrence_pairs(cooc))


def record_universe(candidates, cooc=None) -> list[dict]:
    """One row per constructed candidate, in the order the engine built it.

    With the engine's cooccurrence table supplied, every row also carries the label that table
    implies and whether it agrees with the engine's own flag, so the transition/cooccurrence
    split is checked rather than inferred from the flag alone.
    """
    pairs = cooccurrence_pairs(cooc) if cooc is not None else None
    rows = []
    for rank, candidate in enumerate(candidates, start=1):
        evidence = getattr(candidate, "evidence", None) or {}
        row = {
            "rank": rank,
            "edge": [candidate.source, candidate.target],
            "relation": relation(candidate),
            "strength": float(getattr(candidate, "strength", 0.0)),
            "support": evidence.get("count") if isinstance(evidence, dict) else None,
        }
        if pairs is not None:
            expected = label_from_pairs(candidate.source, candidate.target, pairs)
            row["expected_relation"] = expected
            row["label_agrees"] = row["relation"] == expected
        rows.append(row)
    return rows


class RepairedObserverSleepService(SleepService):
    """The shipped engine whose served list is the engine's own, with a second, observational call.

    Only ``_build_predictions`` is replaced. With ``observe=False`` the method *is* the engine's:
    no lift, no second call, no recorded state, which makes the off arm a true control.
    """

    def __init__(self, memory, observe: bool = True, cap: int = SHIPPED_CAP):
        super().__init__(memory)
        self.MAX_PREDICTIONS = int(cap)
        self.observe = bool(observe)
        self.universe: list[list[dict]] = []
        self.allocation: list[dict] = []

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        served = super()._build_predictions(temporal, freqs, prior_schemas)
        if not self.observe:
            return served

        shipped = self.MAX_PREDICTIONS
        self.MAX_PREDICTIONS = CEILING
        try:
            full = super()._build_predictions(temporal, freqs, prior_schemas)
        finally:
            self.MAX_PREDICTIONS = shipped

        self.full_candidates = list(full)
        rows = record_universe(full, getattr(self, "_current_cooc", None))
        self.universe.append(rows)
        served_rows = [row for row in rows
                       if (row["edge"][0], row["edge"][1]) in
                       {(c.source, c.target) for c in served}]
        by_relation = {name: sum(1 for row in served_rows if row["relation"] == name)
                       for name in RELATIONS}
        self.allocation.append({
            "served": len(served),
            "universe": len(rows),
            "transitions": by_relation["transition"],
            "cooccurrences": by_relation["cooccurrence"],
            "unknown": sum(1 for row in served_rows if row["relation"] == "unknown"),
            "relation_checked": sum(1 for row in rows if "label_agrees" in row),
            "relation_mismatch": sum(1 for row in rows if row.get("label_agrees") is False),
            "relation_unlabelled": sum(1 for row in rows if row["relation"] == "unknown"),
            "sum_matches": by_relation["transition"] + by_relation["cooccurrence"]
                           + sum(1 for row in served_rows if row["relation"] == "unknown")
                           == len(served),
        })
        return served


def run_arm(seed: int = FIXTURE_SEED, cycles: int = FIXTURE_CYCLES, arm: str = "on",
            cap: int = SHIPPED_CAP) -> dict:
    """One fixture arm. ``plain`` is the untouched engine, ``off`` the observer without the
    second call, ``on`` the observer with it -- so each comparison isolates one thing."""
    if arm not in ("plain", "off", "on"):
        raise SystemExit("unknown arm %r" % (arm,))
    world = generate_compositional_world(seed=seed, cycles=cycles)
    db_path = _make_scratch_db("repair_observer")
    mem = _CountingMemoryService(str(db_path))
    if arm == "plain":
        svc = SleepService(mem)
        svc.MAX_PREDICTIONS = int(cap)
    else:
        svc = RepairedObserverSleepService(mem, observe=(arm == "on"), cap=cap)
    windows: list[list[tuple[str, str]]] = []
    try:
        for i, text in enumerate(world["events"]):
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            mem.store(text, event_type="observe", source="env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                report = svc.run_sleep_cycle()
                windows.append([(p.source, p.target) for p in report.predictions])
        asserted = {(a, b) for a, targets in structure_edges(svc._load_prior_candidates()).items()
                    for b in targets}
        store_counts = dict(getattr(mem, "store_counts", {}))
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass
    return {
        "arm": arm,
        "seed": seed,
        "cap": int(cap),
        "cycles": len(windows),
        "windows": windows,
        "asserted": sorted(asserted),
        "store_counts": store_counts,
        "universe": [list(cycle) for cycle in getattr(svc, "universe", [])],
        "allocation": [dict(row) for row in getattr(svc, "allocation", [])],
    }


CHANNELS = ("windows", "asserted", "store_counts")


def differs(left: dict, right: dict) -> list[str]:
    """Which recorded channels differ. Ordering counts: a reordered window is a changed engine."""
    return [name for name in CHANNELS if left.get(name) != right.get(name)]


@functools.lru_cache(maxsize=None)
def fixture(seed: int = FIXTURE_SEED, cap: int = SHIPPED_CAP) -> dict:
    """All three arms of one N2 fixture, run once per (seed, cap) per process."""
    return {arm: run_arm(seed=seed, cap=cap, arm=arm) for arm in ("plain", "off", "on")}


def n2_report(seed: int = FIXTURE_SEED, cap: int = SHIPPED_CAP) -> dict:
    arms = fixture(seed=seed, cap=cap)
    served = {edge for window in arms["on"]["windows"] for edge in window}
    universe = {tuple(row["edge"]) for cycle in arms["on"]["universe"] for row in cycle}
    return {
        "fixture": {"seed": seed, "cycles": FIXTURE_CYCLES, "cap": int(cap),
                    "ceiling": CEILING},
        "served_equals_engine": arms["on"]["windows"] == arms["plain"]["windows"],
        "next_cycle_identical": differs(arms["off"], arms["on"]) == [],
        "differs": differs(arms["off"], arms["on"]),
        "universe_recorded": max((len(cycle) for cycle in arms["on"]["universe"]), default=0),
        "served_inside_universe": served <= universe,
        "served_edges": len(served),
        "allocation_sum_matches": all(row["sum_matches"] for row in arms["on"]["allocation"]),
        "relation_labelling": {
            "checked": sum(1 for cycle in arms["on"]["universe"] for row in cycle
                           if "label_agrees" in row),
            "mismatches": sum(1 for cycle in arms["on"]["universe"] for row in cycle
                              if row.get("label_agrees") is False),
            "unlabelled": sum(1 for cycle in arms["on"]["universe"] for row in cycle
                               if row["relation"] == "unknown"),
        },
    }


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--fixture"]:
        rest, seed, cap = argv[1:], FIXTURE_SEED, SHIPPED_CAP
        if rest[:1] == ["--seed"] and len(rest) >= 2:
            seed, rest = int(rest[1]), rest[2:]
        if rest[:1] == ["--cap"] and len(rest) >= 2:
            cap, rest = int(rest[1]), rest[2:]
        if rest:
            print("usage: --fixture [--seed N] [--cap N]")
            return 2
        print(json.dumps(n2_report(seed=seed, cap=cap), indent=1))
        return 0
    print("usage: python -m benchmarks.presence_conversion_repair_observer --fixture")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
