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
COMPLETE_CELLS = tuple(cell["id"] for cell in a1_two_path.CELLS)
C2_CELLS = ("A+K-", "A-K+", "Y_MINUS_A+K+", "Y_MINUS_A-K+")
C7_CELLS = ("A+K+", "A-K+", "Y_MINUS_A+K+", "Y_MINUS_A-K+")
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


def sample_u(memory, targets: set[tuple[str, str]], cycle: int) -> dict:
    """Read pre-sleep U for the targets at the start of ``cycle``.

    This helper is deliberately separate from ``run_sleep_cycle`` so the
    caller's ordering is explicit and testable: cycle observations must be
    stored, U must be read, and only then may consolidation run.
    """
    temporal = defaultdict(dict)
    for a, b, count in memory.temporal_edges(min_count=1):
        temporal[a][b] = count
    return {edge: _u_row(temporal, edge, cycle) for edge in targets}


def neighbor_rows(seed: int, cell_id: str, edges: set[tuple[str, str]],
                  counts: dict[tuple[str, str], dict[str, int]], cycles: int,
                  fingerprint: str, target_tags: set[str]) -> list[dict]:
    """Build non-target rows for C4, kept separate from the target rows.

    The stream covers every non-target edge in the candidate universe, not
    only one-hop neighbours: C4's contract is about other edges, and a one-hop
    restriction would leave indirect spillover unmeasured.  Mixing these into
    ``rows`` would make C2 see non-target edges in the manipulated cells and
    would make C3 require every non-target edge to have all four treatment
    cells.  C4 reads this stream instead.
    """
    rows = []
    for edge in sorted(edges):
        count = counts[edge]
        rows.append({
            "seed": seed,
            "cell": cell_id,
            "edge": "%s>%s" % edge,
            "target": False,
            "relation": "non_target",
            "shares_target_endpoint": bool(set(edge) & target_tags),
            "A": count["A"] > 0,
            "K": count["K"] > 0,
            "Y": count["Y"] > 0,
            "A_cycles": count["A"],
            "K_cycles": count["K"],
            "Y_cycles": count["Y"],
            "cycles": cycles,
            "A_rate": round(count["A"] / cycles, 6),
            "K_rate": round(count["K"] / cycles, 6),
            "Y_rate": round(count["Y"] / cycles, 6),
            "delta_status": "AWAITING_PAIRED_CONTROL",
            "control_A": False,
            "control_K": False,
            "object_fingerprint": fingerprint,
        })
    return rows


def attach_neighbor_deltas(payloads: list[dict]) -> list[dict]:
    """Attach C4 deltas against the same seed's untreated A+K+ cell.

    The cell output records raw availability rates.  This join is deliberately
    separate: a treated cell can be written before its paired control exists.
    """
    baseline: dict[tuple[int, str], dict] = {}
    for payload in payloads:
        if payload.get("cell") != "A+K+":
            continue
        for row in payload.get("neighbor_rows", []):
            baseline[(int(payload["seed"]), row["edge"])] = row
    for payload in payloads:
        for row in payload.get("neighbor_rows", []):
            base = baseline.get((int(payload["seed"]), row["edge"]))
            if base is None:
                row.setdefault("delta_status", "AWAITING_PAIRED_CONTROL")
                continue
            row["neighbor_delta"] = {
                path: round(abs(float(row[path + "_rate"]) - float(base[path + "_rate"])), 6)
                for path in ("A", "K", "Y")
            }
            row["paired_control"] = "%d/A+K+" % int(payload["seed"])
            row["delta_status"] = "MEASURED"
    return payloads


def c4_neighbor_rows(payloads: list[dict]) -> list[dict]:
    """Flatten the C4 stream after ``attach_neighbor_deltas`` has run."""
    return [row for payload in payloads for row in payload.get("neighbor_rows", [])]


def score_c1(payloads: list[dict], tolerance: float | None = None) -> dict:
    """Recompute C1 from cell payloads, including non-target edges."""
    from benchmarks.a1_gate_readiness import C1_MIN, gate_c1

    tolerance = C1_MIN if tolerance is None else tolerance
    rows = c1_rows(payloads)
    def fraction(group: list[dict], path: str) -> float:
        return (sum(1 for row in group if row[path]) / len(group)) if group else 0.0

    a_rows = [row for row in rows
              if row["cell"] == "A-K+" and row.get("control_K")]
    k_rows = [row for row in rows
              if row["cell"] == "A+K-" and row.get("control_A")]
    seeds: dict[str, dict] = {}
    for seed in sorted({int(row["seed"]) for row in rows}):
        group = [row for row in rows if int(row["seed"]) == seed]
        a_seed = [row for row in group
                  if row["cell"] == "A-K+" and row.get("control_K")]
        k_seed = [row for row in group
                  if row["cell"] == "A+K-" and row.get("control_A")]
        a_fraction = fraction(a_seed, "K")
        k_fraction = fraction(k_seed, "A")
        seeds[str(seed)] = {
            "a_minus_denominator": len(a_seed),
            "a_minus_available": sum(1 for row in a_seed if row["K"]),
            "a_minus_fraction": round(a_fraction, 6),
            "k_minus_denominator": len(k_seed),
            "k_minus_available": sum(1 for row in k_seed if row["A"]),
            "k_minus_fraction": round(k_fraction, 6),
            "pass": bool(a_seed and k_seed
                         and a_fraction >= tolerance and k_fraction >= tolerance),
        }

    return {
        "pass": gate_c1(rows, tolerance),
        "tolerance": tolerance,
        "rows": len(rows),
        "a_minus": {
            "denominator": len(a_rows),
            "available": sum(1 for row in a_rows if row["K"]),
            "fraction": round(fraction(a_rows, "K"), 6),
        },
        "k_minus": {
            "denominator": len(k_rows),
            "available": sum(1 for row in k_rows if row["A"]),
            "fraction": round(fraction(k_rows, "A"), 6),
        },
        "seeds": seeds,
    }


def score_c4(payloads: list[dict], tolerance: float | None = None) -> dict:
    """Attach C4 deltas and score the non-target stream."""
    from benchmarks.a1_gate_readiness import C4_MAX, gate_c4

    tolerance = C4_MAX if tolerance is None else tolerance
    attach_neighbor_deltas(payloads)
    rows = c4_neighbor_rows(payloads)
    measured = [row for row in rows if "neighbor_delta" in row]
    max_delta = {"A": 0.0, "K": 0.0, "Y": 0.0}
    violations: list[dict] = []
    unmeasured: list[dict] = []
    for row in rows:
        delta = row.get("neighbor_delta")
        if delta is None:
            unmeasured.append({"seed": row.get("seed"), "cell": row.get("cell"),
                               "edge": row.get("edge")})
            continue
        for path in ("A", "K", "Y"):
            value = delta.get(path)
            if value is None:
                violations.append({"seed": row.get("seed"), "cell": row.get("cell"),
                                   "edge": row.get("edge"), "path": path,
                                   "delta": None})
                continue
            value = float(value)
            max_delta[path] = max(max_delta[path], value)
            if value > tolerance:
                violations.append({"seed": row.get("seed"), "cell": row.get("cell"),
                                   "edge": row.get("edge"), "path": path,
                                   "delta": value})
    return {
        "pass": gate_c4(rows, tolerance),
        "tolerance": tolerance,
        "rows": len(rows),
        "measured": len(measured),
        "max_delta": {path: round(value, 6) for path, value in max_delta.items()},
        "violations": violations,
        "unmeasured": unmeasured,
    }


def registered_target_map() -> dict[str, list[str]]:
    """Return the registered N=20 per-seed targets, or an empty mapping."""
    path = a1_two_path.C8_TARGET_SELECTION_PATH
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if doc.get("n_per_seed") != 20:
        return {}
    return {str(seed): list((row or {}).get("selected") or [])
            for seed, row in (doc.get("per_seed") or {}).items()}


def _target_rows(payload: dict) -> list[dict]:
    return [row for row in payload.get("rows", []) if row.get("target", True)]


def _target_list(payload: dict) -> set[str]:
    return {str(edge) for edge in (payload.get("targets") or [])}


def target_coverage(payloads: list[dict], cells: tuple[str, ...],
                    expected_targets: dict | None = None) -> dict:
    """Check that every expected seed, cell and target row is present once.

    A gate that sees one row must not pass merely because that row is
    internally consistent.  The expected target map defaults to the union of
    the cell payloads' own ``targets`` lists; a caller can pass the frozen
    per-seed target map explicitly to reject a partial or differently selected
    run.  The result assembler supplies the registered N=20 map by default.
    """
    expected_seeds = {str(seed) for seed in a1_two_path.SEEDS}
    if expected_targets is None:
        expected = {seed: set() for seed in expected_seeds}
        for payload in payloads:
            try:
                seed = str(int(payload.get("seed")))
            except (TypeError, ValueError):
                continue
            if seed in expected:
                expected[seed].update(_target_list(payload))
    else:
        expected = {str(seed): {str(edge) for edge in edges}
                    for seed, edges in expected_targets.items()}

    by_key: dict[tuple[str, str], dict] = {}
    problems: list[str] = []
    observed_rows = 0
    for payload in payloads:
        try:
            seed = str(int(payload.get("seed")))
        except (TypeError, ValueError):
            problems.append("a payload has no integer seed")
            continue
        cell = str(payload.get("cell"))
        if (seed, cell) in by_key:
            problems.append("duplicate payload for seed %s cell %s" % (seed, cell))
            continue
        by_key[(seed, cell)] = payload

    for seed in sorted(expected_seeds):
        wanted = expected.get(seed) or set()
        if not wanted:
            problems.append("seed %s has no expected target set" % seed)
        for cell in cells:
            payload = by_key.get((seed, cell))
            if payload is None:
                problems.append("missing seed %s cell %s" % (seed, cell))
                continue
            actual_targets = _target_list(payload)
            if wanted and actual_targets != wanted:
                problems.append("seed %s cell %s target list does not match" % (seed, cell))
            rows = _target_rows(payload)
            edges = [str(row.get("edge")) for row in rows]
            observed_rows += len(rows)
            if set(edges) != wanted:
                problems.append("seed %s cell %s does not cover the target rows"
                                % (seed, cell))
            if len(edges) != len(set(edges)):
                problems.append("seed %s cell %s repeats a target row" % (seed, cell))

    expected_rows = sum(len(expected.get(seed) or set()) * len(cells)
                        for seed in expected_seeds)
    return {
        "pass": bool(expected_rows and not problems),
        "seeds_expected": len(expected_seeds),
        "cells_per_seed": len(cells),
        "rows_expected": expected_rows,
        "rows_observed": observed_rows,
        "targets_per_seed": {seed: len(expected.get(seed) or set())
                             for seed in sorted(expected_seeds)},
        "problems": problems,
    }


def _score_rows(payloads: list[dict], cells: tuple[str, ...],
                expected_targets: dict | None, gate) -> dict:
    coverage = target_coverage(payloads, cells, expected_targets)
    rows = [row for payload in payloads if payload.get("cell") in cells
            for row in _target_rows(payload)]
    try:
        gate_pass = bool(gate(rows))
    except (KeyError, TypeError, ValueError):
        gate_pass = False
    return {
        "pass": bool(coverage["pass"] and gate_pass),
        "coverage": coverage,
        "gate_pass": gate_pass,
        "rows": len(rows),
    }


def score_c2(payloads: list[dict], expected_targets: dict | None = None) -> dict:
    """Score C2 on every expected seed and target row, including Y- A/K."""
    from benchmarks.a1_gate_readiness import gate_c2
    return _score_rows(payloads, C2_CELLS, expected_targets, gate_c2)


def score_c3(payloads: list[dict], expected_targets: dict | None = None) -> dict:
    """Score C3 only when all six cells cover the expected target sets."""
    from benchmarks.a1_gate_readiness import gate_c3
    return _score_rows(payloads, COMPLETE_CELLS, expected_targets, gate_c3)


def score_c5(payloads: list[dict], expected_targets: dict | None = None) -> dict:
    """Score C5 on every expected target row in all six cells."""
    from benchmarks.a1_gate_readiness import gate_c5
    return _score_rows(payloads, COMPLETE_CELLS, expected_targets, gate_c5)


def score_c7(payloads: list[dict], expected_targets: dict | None = None,
             tolerance: float | None = None) -> dict:
    """Score C7 on the paired baseline and both Y- cells per seed."""
    from benchmarks.a1_gate_readiness import C7_MAX, gate_c7
    reported = _score_rows(payloads, C7_CELLS, expected_targets,
                           lambda rows: gate_c7(
                               rows, C7_MAX if tolerance is None else tolerance))
    reported["tolerance"] = C7_MAX if tolerance is None else tolerance
    return reported


def score_c9(payloads: list[dict], expected_targets: dict | None = None) -> dict:
    """Score C9 only when every expected cell and target row exists."""
    from benchmarks.a1_gate_readiness import gate_c9
    return _score_rows(payloads, COMPLETE_CELLS, expected_targets, gate_c9)


def score_complete_gates(payloads: list[dict],
                         expected_targets: dict | None = None) -> dict:
    """Score the five structural gates with complete seed/cell/target coverage."""
    results = {
        "C2_treatment_consistency": score_c2(payloads, expected_targets),
        "C3_positivity": score_c3(payloads, expected_targets),
        "C5_common_cause": score_c5(payloads, expected_targets),
        "C7_assertion_block": score_c7(payloads, expected_targets),
        "C9_same_object": score_c9(payloads, expected_targets),
    }
    return {
        "pass": all(row["pass"] for row in results.values()),
        "gates": results,
        "failed": [name for name, row in results.items() if not row["pass"]],
    }


def c1_rows(payloads: list[dict]) -> list[dict]:
    """Build the C1 rows with the non-target edges included in the denominator.

    C1's denominator is the paired control's available edges.  Target rows are
    joined to the same seed's A+K+ row; non-target rows are joined the same way.
    Only edges available in the paired control enter the denominator, so a
    missing control edge is not counted as a preservation failure.
    """
    baseline: dict[tuple[int, str], dict] = {}
    for payload in payloads:
        if payload.get("cell") != "A+K+":
            continue
        for row in payload.get("rows", []) + payload.get("neighbor_rows", []):
            baseline[(int(payload["seed"]), row["edge"])] = row
    rows: list[dict] = []
    for payload in payloads:
        for row in payload.get("rows", []) + payload.get("neighbor_rows", []):
            base = baseline.get((int(payload["seed"]), row["edge"]))
            if base is None:
                continue
            copied = dict(row)
            copied["control_K"] = (
                payload.get("cell") == "A-K+" and bool(base.get("K"))
            )
            copied["control_A"] = (
                payload.get("cell") == "A+K-" and bool(base.get("A"))
            )
            rows.append(copied)
    return rows


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
    neighbor_edges = universe - targets
    neighbor_counts = {edge: {"A": 0, "K": 0, "Y": 0} for edge in neighbor_edges}
    target_counts = {edge: {"A": 0, "K": 0, "Y": 0} for edge in targets}
    target_tags = {tag for edge in targets for tag in edge}
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
                cycle = (i + 1) // EVENTS_PER_CYCLE
                # Pre-outcome: cycle-36 observations are stored, but the
                # cycle-36 consolidation has not run yet.  The boundary is
                # the acquisition cycle, not the engine's sleep counter,
                # which can lag when early cycles produce no candidates.
                if cycle == u_cycle:
                    pending_u = sample_u(memory, targets, cycle)
                report = service.run_sleep_cycle()
                if cycle == u_cycle:
                    u.update(pending_u)
                predictions = {(p.source, p.target) for p in report.predictions}
                carriers = _carrier_edges(report)
                asserted = _report_edges(report)
                for edge in targets:
                    if edge in predictions:
                        served_first.setdefault(edge, cycle)
                        target_counts[edge]["A"] += 1
                    if edge in carriers:
                        carrier_first.setdefault(edge, cycle)
                        target_counts[edge]["K"] += 1
                    if edge in asserted and assertion_visible(edge, assertion_blocked):
                        asserted_first.setdefault(edge, cycle)
                        target_counts[edge]["Y"] += 1
                for edge, count in neighbor_counts.items():
                    if edge in predictions:
                        count["A"] += 1
                    if edge in carriers:
                        count["K"] += 1
                    if edge in asserted:
                        count["Y"] += 1
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
        counts = target_counts[edge]
        rows.append({
            "seed": seed,
            "cell": cell_id,
            "edge": "%s>%s" % edge,
            "target": target,
            "A": edge in served_first,
            "K": edge in carrier_first,
            "Y": edge in final_asserted and visible,
            "A_cycles": counts["A"],
            "K_cycles": counts["K"],
            "Y_cycles": counts["Y"],
            "A_rate": round(counts["A"] / cycles, 6),
            "K_rate": round(counts["K"] / cycles, 6),
            "Y_rate": round(counts["Y"] / cycles, 6),
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
    neighbor_payload = neighbor_rows(
        seed, cell_id, neighbor_edges, neighbor_counts, cycles, fingerprint, target_tags
    )
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
        "neighbor_rows": neighbor_payload,
        "neighbor_count": len(neighbor_payload),
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
