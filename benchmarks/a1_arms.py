"""A1 A-/K-/Y- arms: edge-level treatments and cell measurement.

The treatments are benchmark-only subclasses of the shipped ``SleepService``.
They never edit an engine file:

* ``A-`` removes the target edge from the served prediction window;
* ``K-`` removes loop/dream carriers that contain the target edge from the
  structure-to-assertion readout;
* ``Y-`` blocks the assertion readout for the target edge without removing
  admission or carrier formation.

Every entry point calls the manifest gate first.  The current manifest has no
frozen target edges and no owner grant, so no cell can open a database.

    python -m benchmarks.a1_two_path --dry-run
    python -m benchmarks.a1_two_path --cell A+K+ --seed 20630101
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

from benchmarks import a1_two_path
from benchmarks import engine_stamp
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import (
    PHASE_ACQUISITION,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, _world_compositional_edges, structure_edges
from organica.sleep import SleepService

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / ".scratch" / "a1_two_path" / "parts"
KIND = "a1_two_path_cell"
ACQ_SOURCE = "env_acq"


def targets_for_seed(seed: int, doc: dict | None = None) -> set[tuple[str, str]]:
    """Return the frozen target edges for one seed, or an empty set if unfixed."""
    doc = a1_two_path.manifest() if doc is None else doc
    by_seed = (doc.get("targets") or {}).get("by_seed") or {}
    edges = by_seed.get(str(seed), by_seed.get(seed, []))
    if not isinstance(edges, list):
        raise ValueError("targets for seed %d are not a list" % seed)
    found: set[tuple[str, str]] = set()
    for edge in edges:
        if not isinstance(edge, str) or edge.count(">") != 1:
            raise ValueError("target edge is not a directed string: %r" % (edge,))
        a, b = edge.split(">", 1)
        if not a or not b:
            raise ValueError("target edge has an empty endpoint: %r" % (edge,))
        found.add((a, b))
    return found


def _path_pairs(path: list[str]) -> set[tuple[str, str]]:
    return set(zip(path, path[1:]))


def admission_filter(predictions: list, blocked: set[tuple[str, str]]) -> list:
    """A-: remove the target edge from the served prediction window."""
    return [p for p in predictions
            if (p.source, p.target) not in blocked]


def carrier_filter(loops: list, dreams: list,
                   blocked: set[tuple[str, str]]) -> tuple[list, list]:
    """K-: remove loop/dream paths that carry the target edge.

    A loop path is read in both directions by ``structure_edges``; a dream path
    is read in its stored direction.  Removing both orientations is the
    conservative carrier block.
    """
    def hit(path: list[str]) -> bool:
        pairs = _path_pairs(path)
        return any(edge in pairs or (edge[1], edge[0]) in pairs for edge in blocked)

    return ([loop for loop in loops if not hit(list(loop.path or []))],
            [dream for dream in dreams if not hit(list(dream.path_or_context or []))])


def assertion_visible(edge: tuple[str, str], blocked: set[tuple[str, str]]) -> bool:
    """Y-: the target edge's assertion readout is blocked, not its formation."""
    return edge not in blocked


def _carrier_edges(report) -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for loop in report.loops:
        pairs = _path_pairs(list(loop.path or []))
        for a, b in pairs:
            found.add((a, b))
            found.add((b, a))
    for dream in report.dreams:
        for pair in _path_pairs(list(dream.path_or_context or [])):
            found.add(pair)
    return found


def _report_edges(report) -> set[tuple[str, str]]:
    names = (
        "concepts", "phrases", "loops", "predictions", "anomalies",
        "meta_concepts", "processes", "roles", "workflow_concepts", "schemas",
        "hypotheses", "theories", "questions", "dreams", "investigations",
        "experiments",
    )
    candidates = []
    for name in names:
        candidates.extend(asdict(candidate) for candidate in
                          (getattr(report, name, []) or []))
    return {(a, b) for a, targets in structure_edges(candidates).items()
            for b in targets}


class A1ArmSleepService(SleepService):
    """The shipped sleep service with only the requested edge filters applied."""

    def __init__(self, memory, blocked_admission=(), blocked_carrier=()):
        super().__init__(memory)
        self.blocked_admission = set(blocked_admission)
        self.blocked_carrier = set(blocked_carrier)

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        predictions = super()._build_predictions(temporal, freqs, prior_schemas)
        return admission_filter(predictions, self.blocked_admission)

    def _build_loops(self, temporal):
        loops = super()._build_loops(temporal)
        filtered, _ = carrier_filter(loops, [], self.blocked_carrier)
        return filtered

    def _generate_categorized_dreams(self, *args, **kwargs):
        dreams = super()._generate_categorized_dreams(*args, **kwargs)
        _, filtered = carrier_filter([], dreams, self.blocked_carrier)
        return filtered


def _u_row(temporal: dict, edge: tuple[str, str], cycle: int) -> dict:
    direct = int(temporal.get(edge[0], {}).get(edge[1], 0))
    reverse = int(temporal.get(edge[1], {}).get(edge[0], 0))
    return {
        "direct_count": direct,
        "reverse_count": reverse,
        "strength": direct + reverse,
        "measured_cycle": cycle,
    }


def _fingerprint(seed: int, cycles: int, cap: int, universe: set[tuple[str, str]],
                 u: dict[tuple[str, str], dict], targets: set[tuple[str, str]]) -> str:
    payload = {
        "seed": seed,
        "cycles": cycles,
        "cap": cap,
        "universe": sorted("%s>%s" % edge for edge in universe),
        "targets": sorted("%s>%s" % edge for edge in targets),
        "U": {"%s>%s" % edge: value for edge, value in sorted(u.items())},
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def run_cell(seed: int, cell_id: str, control: bool = False) -> int:
    """Run one planned cell after the gate, target and object checks.

    This function is reached only after ``a1_two_path.refuse()``.  No database
    is opened before the gate, the target set and the target-in-world check.
    """
    a1_two_path.refuse()
    doc = a1_two_path.manifest()
    cell = next((row for row in doc["cells"] if row["id"] == cell_id), None)
    planned = (a1_two_path.is_planned(seed, cell_id, control=True) if control
               else a1_two_path.is_planned(seed, cell_id))
    if cell is None or not planned:
        print("REFUSED: %s/%s (control=%s) is not a planned cell"
              % (seed, cell_id, control), file=sys.stderr)
        return 2
    try:
        targets = targets_for_seed(seed, doc)
    except ValueError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 2
    if not targets:
        print("REFUSED: the manifest fixes no target edge for seed %d" % seed,
              file=sys.stderr)
        return 2

    cycles = int(doc["seed_block"]["cycles"])
    cap = int(doc["seed_block"]["cap"])
    u_cycle = int(doc["targets"]["u_cycle"])
    if not 1 <= u_cycle <= cycles:
        print("REFUSED: U cycle %d is outside 1..%d" % (u_cycle, cycles),
              file=sys.stderr)
        return 2

    world = generate_compositional_world(seed=seed, cycles=cycles)
    universe = _world_compositional_edges(world)
    unknown = targets - universe
    if unknown:
        print("REFUSED: target edges are not in seed %d's universe: %s"
              % (seed, ", ".join(sorted("%s>%s" % edge for edge in unknown))),
              file=sys.stderr)
        return 2

    admission_blocked = targets if cell["admission"] == "blocked" else set()
    carrier_blocked = targets if cell["carrier"] == "blocked" else set()
    assertion_blocked = targets if cell["assertion"] == "blocked" else set()
    db_path = _make_scratch_db("a1_two_path")
    memory = _CountingMemoryService(str(db_path))
    service = A1ArmSleepService(memory, admission_blocked, carrier_blocked)
    service.MAX_PREDICTIONS = cap
    served_first: dict[tuple[str, str], int] = {}
    carrier_first: dict[tuple[str, str], int] = {}
    asserted_first: dict[tuple[str, str], int] = {}
    u: dict[tuple[str, str], dict] = {}
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                report = service.run_sleep_cycle()
                cycle = int(report.cycle)
                predictions = {(p.source, p.target) for p in report.predictions}
                carriers = _carrier_edges(report)
                asserted = _report_edges(report)
                for edge in targets:
                    if edge in predictions:
                        served_first.setdefault(edge, cycle)
                    if edge in carriers:
                        carrier_first.setdefault(edge, cycle)
                    if edge in asserted:
                        asserted_first.setdefault(edge, cycle)
                if cycle == u_cycle:
                    temporal = defaultdict(dict)
                    for a, b, count in memory.temporal_edges(min_count=1):
                        temporal[a][b] = count
                    for edge in targets:
                        u[edge] = _u_row(temporal, edge, cycle)
        final_asserted = {(a, b) for a, targets_ in
                          structure_edges(service._load_prior_candidates()).items()
                          for b in targets_}
    finally:
        memory.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    fingerprint = _fingerprint(seed, cycles, cap, universe, u, targets)
    rows = []
    # The A1 gate contracts read eligible target rows, not the whole universe.
    # Emitting every world edge would make C2 see nontarget rows that are
    # correctly served in A-K+ and correctly absent in A+K-.
    for edge in sorted(targets):
        target = True
        carrier_cycle = carrier_first.get(edge)
        asserted_cycle = asserted_first.get(edge)
        visible = assertion_visible(edge, assertion_blocked) if target else True
        rows.append({
            "seed": seed,
            "cell": cell_id,
            "edge": "%s>%s" % edge,
            "target": target,
            "A": edge in served_first,
            "K": edge in carrier_first,
            "Y": edge in final_asserted and visible,
            "carrier_cycle": carrier_cycle,
            "k_cycle": carrier_cycle,
            # Y- masks the readout, but the underlying assertion time is still
            # recorded so the pre-outcome U check can be evaluated.
            "y_cycle": asserted_cycle,
            "control_A": target and cell_id == "A+K-",
            "control_K": target and cell_id == "A-K+",
            "U": u.get(edge, {"direct_count": None, "reverse_count": None,
                              "strength": None, "measured_cycle": None}),
            "object_fingerprint": fingerprint,
        })
    payload = {
        "kind": KIND,
        "id": doc["id"],
        "seed": seed,
        "cell": cell_id,
        "control": control,
        "cycles": cycles,
        "cap": cap,
        "u_cycle": u_cycle,
        "targets": sorted("%s>%s" % edge for edge in targets),
        "rows": rows,
        "not_evidence": (
            "One A1 cell output. It is not a verdict until every gate is scored; "
            "it makes no causal, capability or transfer claim."
        ),
    }
    payload = engine_stamp.stamp(payload)
    PARTS.mkdir(parents=True, exist_ok=True)
    suffix = "-control" if control else ""
    path = PARTS / ("%d-%s%s.json" % (seed, cell_id, suffix))
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("ran %s" % path)
    return 0


def run_all() -> int:
    """Run every planned cell. The gate refuses before this loop in the current state."""
    a1_two_path.refuse()
    for seed in a1_two_path.SEEDS:
        for cell in a1_two_path.CELLS:
            result = run_cell(seed, cell["id"])
            if result:
                return result
    result = run_cell(a1_two_path.CONTROL["seed"], a1_two_path.CONTROL["cell"],
                      control=True)
    return result


def self_test() -> list[str]:
    """Exercise each treatment filter without starting an engine."""
    found: list[str] = []
    edge = ("a", "b")
    reverse = ("b", "a")
    other = ("c", "d")

    class P:
        def __init__(self, source, target):
            self.source, self.target = source, target

    preds = [P("a", "b"), P("b", "a"), P("c", "d")]
    filtered = admission_filter(preds, {edge})
    if [(p.source, p.target) for p in filtered] != [reverse, other]:
        found.append("A- does not remove only the target prediction")

    class Path:
        def __init__(self, path):
            self.path = path
            self.path_or_context = path

    loops = [Path(["a", "b", "c"]), Path(["c", "d", "a"])]
    dreams = [Path(["a", "b"]), Path(["d", "e"])]
    kept_loops, kept_dreams = carrier_filter(loops, dreams, {edge})
    if any("a" in loop.path and "b" in loop.path for loop in kept_loops):
        found.append("K- leaves a loop carrier containing the target")
    if any(dream.path_or_context[:2] == ["a", "b"] for dream in kept_dreams):
        found.append("K- leaves a dream carrier containing the target")
    if len(kept_loops) != 1 or len(kept_dreams) != 1:
        found.append("K- removes a non-target carrier")

    if not assertion_visible(other, {edge}) or assertion_visible(edge, {edge}):
        found.append("Y- does not block only the target assertion")

    both_preds = admission_filter(preds, {edge})
    both_loops, both_dreams = carrier_filter(loops, dreams, {edge})
    if any((p.source, p.target) == edge for p in both_preds):
        found.append("A-K- leaves the target in the served window")
    if any(edge in _path_pairs(loop.path) for loop in both_loops):
        found.append("A-K- leaves a target loop carrier")
    if any(edge in _path_pairs(dream.path_or_context) for dream in both_dreams):
        found.append("A-K- leaves a target dream carrier")

    try:
        targets_for_seed(1, {"targets": {"by_seed": {"1": ["a>b", "c>d"]}}})
    except ValueError:
        found.append("a valid target list is rejected")
    for bad in (["a"], ["a>"], ["a>b>c"], [1]):
        try:
            targets_for_seed(1, {"targets": {"by_seed": {"1": bad}}})
        except ValueError:
            pass
        else:
            found.append("an invalid target list is accepted: %r" % (bad,))
    return found


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="A1 A-/K-/Y- treatment self-test")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if not args.self_test:
        parser.error("only --self-test is available here; use benchmarks.a1_two_path for cells")
    found = self_test()
    for problem in found:
        print("FAIL:", problem)
    if not found:
        print("A1 arms: self-test clean")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
