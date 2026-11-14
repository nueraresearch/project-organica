"""A1 gate readiness: exact C1-C5 and C7-C9 contracts, and what remains to run.

This is a preflight, not an intervention. It freezes the *gate logic* the two-path
design needs, proves each gate can pass and fail on synthetic rows, and records why
none of the eight remaining gates can be cleared from the committed observational
records. No engine is started, no seed is spent, and no cell is written.

C6 is the one exception: the separate C6-TIMING-1 block is read from its committed
result and is reported as satisfied.

Usage:
    python -m benchmarks.a1_gate_readiness --write
    python -m benchmarks.a1_gate_readiness --check
    python -m benchmarks.a1_gate_readiness --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_gate_readiness.json"
PAGE_PATH = DOCS / "A1-GATE-READINESS.md"

C6_PATH = DOCS / "c6_timing_block.json"
A0_PATH = DOCS / "carrier_formation_a0.json"
DISPOSITION_PATH = DOCS / "CAP-112-PROVENANCE-DISPOSITION.md"

DATE = "2026-11-14"
PRIMARY_CELLS = ("A+K+", "A+K-", "A-K+", "A-K-")
Y_CELLS = ("Y_MINUS_A+K+", "Y_MINUS_A-K+")

#: Precommitted before any A1 cell. These are manipulation/independence margins, not effect-size
#: predictions; they are not estimated from A0 or from any run. A 0.95 preservation floor allows
#: at most a 5% cross-path leak, and 0.05 is the same margin as an absolute rate.
C1_MIN = 0.95
C4_MAX = 0.05
C7_MAX = 0.05
C8_MAX = 0.05
C7_RATE_DENOMINATOR_CYCLES = 120
C7_RATE_STEP = round(1.0 / C7_RATE_DENOMINATOR_CYCLES, 6)
C7_C8_DENOMINATOR_UNIT = "PER SEED"
C7_C8_DENOMINATOR_RECORD = "docs/A1-C7-C8-DENOMINATOR.md"
THRESHOLDS = {
    "C1_A_minus_carrier_preservation_min": C1_MIN,
    "C1_K_minus_served_preservation_min": C1_MIN,
    "C4_neighbor_delta_max": C4_MAX,
    "C7_A_delta_max": C7_MAX,
    "C7_K_delta_max": C7_MAX,
    "C8_third_route_assertion_max": C8_MAX,
}
THRESHOLD_ROWS = (
    ("C1_path_separation", "A- carrier preservation", C1_MIN,
     "Proportion of paired-control carrier-available edges still carrier-available under A-, per seed."),
    ("C1_path_separation", "K- served preservation", C1_MIN,
     "Proportion of paired-control served edges still served under K-, per seed."),
    ("C4_no_interference", "neighbour delta", C4_MAX,
     "Maximum absolute A, K or Y availability-rate difference on non-target edges against the paired control."),
    ("C7_assertion_block", "A delta under Y-", C7_MAX,
     "Absolute A formation-rate difference between Y- and the paired no-Y- control, per seed; the rate denominator is 120 cycles per edge."),
    ("C7_assertion_block", "K delta under Y-", C7_MAX,
     "Absolute K formation-rate difference between Y- and the paired no-Y- control, per seed; the rate denominator is 120 cycles per edge."),
    ("C8_third_route", "A-K- assertion ceiling", C8_MAX,
     "Assertion rate in A-K- per seed over its N target rows; above the ceiling is THIRD ROUTE PRESENT on that seed."),
)
THRESHOLDS_PATH = DOCS / "a1_precommitted_thresholds.json"
THRESHOLDS_PAGE = DOCS / "A1-PRECOMMITTED-THRESHOLDS.md"

BOUND_RULE = (
    "One implementation and one registered run per gate. A failed or unmeasurable C1 or "
    "C4 is VOID under the adopted C1/C4 gate; other gate dispositions are recorded in "
    "their own rows. All are terminal: no A1 patch, threshold change, extra cell or rerun. "
    "A new registered design is required to try again."
)
BOUNDS = {
    "C1_path_separation": {
        "attempts": 1,
        "attempt": "Implement A- and K- once and run the registered 2x2 cells.",
        "success": "The C1 contract passes on every seed.",
        "on_failure": "VOID: C1 path separation failed; the A1 run is not admissible.",
        "on_unmeasurable": "VOID: no paired-control denominator; the A1 run is not measurable.",
    },
    "C2_treatment_consistency": {
        "attempts": 1,
        "attempt": "Run each manipulation once and read its named path.",
        "success": "The C2 contract passes on every seed.",
        "on_failure": "VOID: the intervention did not happen as specified.",
        "on_unmeasurable": "UNSATISFIABLE: a required manipulation has no denominator.",
    },
    "C3_positivity": {
        "attempts": 1,
        "attempt": "Join every eligible edge to both factors once and read all six cells.",
        "success": "The C3 contract passes on every seed and edge.",
        "on_failure": "VOID: a required cell is empty.",
        "on_unmeasurable": "UNSATISFIABLE: no eligible edge can populate the cells.",
    },
    "C4_no_interference": {
        "attempts": 1,
        "attempt": "Freeze the targets, grant the run, and measure non-target spillover once.",
        "success": "The C4 contract passes on every non-target edge.",
        "on_failure": "VOID: a non-target A, K or Y delta exceeds 0.05; the A1 run is invalid.",
        "on_unmeasurable": "VOID: no non-target edge has a measurable delta; the A1 run is not measurable.",
    },
    "C5_common_cause": {
        "attempts": 1,
        "attempt": "Measure edge strength and join pre-outcome U to every cell once.",
        "success": "The C5 contract passes on every row.",
        "on_failure": "SHARED CAUSE / NO CARRIER RELATION NOT SEPARATED.",
        "on_unmeasurable": "UNSATISFIABLE: U has no pre-outcome measurement on a required row.",
    },
    "C7_assertion_block": {
        "attempts": 1,
        "attempt": "Implement Y- once and read assertion and A/K formation at A+K+ and A-K+.",
        "success": "The C7 contract passes on every seed and at both Y- cells.",
        "on_failure": "SHARED CAUSE / READOUT NOT SEPARATED.",
        "on_unmeasurable": "UNSATISFIABLE: no Y- cell has a paired control.",
    },
    "C8_third_route": {
        "attempts": 1,
        "attempt": "Implement the A-K- double block once and read assertion.",
        "success": "A-K- assertion is at or below the precommitted 0.05 ceiling on every seed.",
        "on_failure": "THIRD ROUTE PRESENT: the two-path model is incomplete.",
        "on_unmeasurable": "UNSATISFIABLE: A-K- has no denominator.",
    },
    "C9_same_object": {
        "attempts": 1,
        "attempt": "Run the paired cells once and compare their object fingerprints.",
        "success": "The C9 contract passes for every seed.",
        "on_failure": "VOID: the comparison is not paired.",
        "on_unmeasurable": "UNSATISFIABLE: a paired cell has no object fingerprint.",
    },
}

GATE_ORDER = {
    "C4_no_interference": {
        "decision": "POST-FREEZE VOID GATE",
        "date": DATE,
        "pre_freeze_admissibility": False,
        "record": "docs/A1-C4-GATE-ORDER.md",
        "void_condition": (
            "Any measurable non-target A, K or Y neighbour delta above 0.05, "
            "or an unmeasurable non-target stream, makes the A1 run VOID."
        ),
        "freeze_effect": (
            "C4 is not a pre-freeze blocker. The targets remain draft and the "
            "manifest remains unfrozen because no separate owner freeze act exists."
        ),
    },
    "C1_path_separation": {
        "decision": "POST-FREEZE VOID GATE",
        "date": DATE,
        "pre_freeze_admissibility": False,
        "record": "docs/A1-C1-C4-VOID-GATE.md",
        "void_condition": (
            "A missing or below-60 paired-control denominator, or a C1 preservation "
            "failure on any seed or path, makes the A1 run VOID."
        ),
        "note": "C1 and C4 are one adopted validity decision; C1 is scored in the same "
                "post-freeze assembly and uses the C4 denominator.",
    },
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fraction(rows: list[dict], field: str) -> float:
    return sum(1 for row in rows if row[field]) / len(rows) if rows else 0.0


def gate_c1(rows: list[dict], tolerance: float | None) -> bool:
    """On every seed, A- leaves carrier availability and K- leaves served availability."""
    if tolerance is None:
        return False
    by_seed: dict[int, list[dict]] = {}
    for row in rows:
        by_seed.setdefault(int(row["seed"]), []).append(row)
    for group in by_seed.values():
        a_minus = [row for row in group if row["cell"] == "A-K+" and row.get("control_K")]
        k_minus = [row for row in group if row["cell"] == "A+K-" and row.get("control_A")]
        if not a_minus or not k_minus:
            return False
        if (_fraction(a_minus, "K") < tolerance
                or _fraction(k_minus, "A") < tolerance):
            return False
    return bool(by_seed)


def gate_c2(rows: list[dict], tolerance: float | None = None) -> bool:
    """Per seed, each manipulation drives its named path to zero.

    The Y- cells also check the unmanipulated A/K paths: Y_MINUS_A+K+ must
    keep both A and K, and Y_MINUS_A-K+ must keep K while A is blocked.  A
    pooled check would let one seed's correct rows hide another seed's bad
    manipulation.
    """
    by_seed = _by_seed(rows)
    if not by_seed:
        return False
    for group in by_seed.values():
        a_minus = [row for row in group if row["cell"] == "A-K+"]
        k_minus = [row for row in group if row["cell"] == "A+K-"]
        y_plus = [row for row in group if row["cell"] == "Y_MINUS_A+K+"]
        y_minus_a = [row for row in group if row["cell"] == "Y_MINUS_A-K+"]
        if not a_minus or not k_minus or not y_plus or not y_minus_a:
            return False
        if not all(not row["A"] and row["K"] for row in a_minus):
            return False
        if not all(row["A"] and not row["K"] for row in k_minus):
            return False
        if not all(not row["Y"] and row["A"] and row["K"] for row in y_plus):
            return False
        if not all(not row["Y"] and not row["A"] and row["K"] for row in y_minus_a):
            return False
    return True


def gate_c3(rows: list[dict], tolerance: float | None = None) -> bool:
    """Every eligible edge has all four A x K cells, and every seed the two Y- cells."""
    by_seed: dict[int, set[str]] = {}
    by_seed_edge: dict[tuple[int, str], set[str]] = {}
    for row in rows:
        seed = int(row["seed"])
        by_seed.setdefault(seed, set()).add(row["cell"])
        by_seed_edge.setdefault((seed, str(row["edge"])), set()).add(row["cell"])
    return (bool(by_seed_edge)
            and all(all(cell in seen for cell in PRIMARY_CELLS)
                    for seen in by_seed_edge.values())
            and all(all(cell in seen for cell in Y_CELLS)
                    for seen in by_seed.values()))


def gate_c4(rows: list[dict], tolerance: float | None) -> bool:
    """Neighbour spillover stays within the precommitted tolerance."""
    if tolerance is None:
        return False
    non_target = [row for row in rows if not row.get("target")]
    for row in non_target:
        delta = row.get("neighbor_delta") or {}
        if any(path not in delta or float(delta[path]) > tolerance
               for path in ("A", "K", "Y")):
            return False
    return bool(non_target)


def gate_c5(rows: list[dict], tolerance: float | None = None) -> bool:
    """U is measured before the carrier and either outcome, and is not post-hoc rank."""
    required = ("direct_count", "reverse_count", "strength", "measured_cycle")
    if not rows:
        return False
    for row in rows:
        u = row.get("U") or {}
        if any(u.get(field) is None for field in required):
            return False
        try:
            measured = int(u["measured_cycle"])
            carrier = int(row["carrier_cycle"])
            k_cycle = int(row["k_cycle"])
            y_cycle = int(row["y_cycle"])
        except (KeyError, TypeError, ValueError):
            return False
        if not (measured <= carrier and measured <= k_cycle and measured <= y_cycle):
            return False
    return True


def _by_seed(rows: list[dict]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = {}
    for row in rows:
        grouped.setdefault(int(row["seed"]), []).append(row)
    return grouped


def gate_c7(rows: list[dict], tolerance: float | None) -> bool:
    """On every seed, Y- lowers assertion while A and K stay within tolerance.

    C7 is a per-seed manipulation/readout check.  Pooling Y- rows across seeds
    would let a seed that is missing a Y- cell borrow another seed's rows, and
    would let a small per-seed delta be averaged into a pooled pass.
    """
    if tolerance is None:
        return False
    by_seed = _by_seed(rows)
    if not by_seed:
        return False
    for group in by_seed.values():
        controls = {
            cell: [row for row in group if row["cell"] == cell]
            for cell in ("A+K+", "A-K+")
        }
        blocked = [row for row in group if row["cell"] in Y_CELLS]
        if not controls["A+K+"] or not blocked:
            return False
        if {str(row["cell"]) for row in blocked} != set(Y_CELLS):
            return False
        # Y_MINUS_A+K+ is paired with A+K+, and Y_MINUS_A-K+ with A-K+.
        # Falling back to A+K+ for the second pair keeps older, coarser
        # fixtures readable; complete scoring requires the A-K+ control.
        pairing = {
            "Y_MINUS_A+K+": controls["A+K+"],
            "Y_MINUS_A-K+": controls["A-K+"] or controls["A+K+"],
        }
        for cell, control in pairing.items():
            cell_rows = [row for row in blocked if row["cell"] == cell]
            if not cell_rows or not control:
                return False
            control_edges = {str(row["edge"]) for row in control
                             if row.get("edge") is not None}
            if control_edges and {str(row.get("edge")) for row in cell_rows} != control_edges:
                return False
            if _fraction(cell_rows, "Y") >= _fraction(control, "Y"):
                return False
            by_edge = {str(row["edge"]): row for row in control
                       if row.get("edge") is not None}
            for row in cell_rows:
                delta = row.get("delta_from_baseline")
                if delta is None:
                    base = by_edge.get(str(row.get("edge")))
                    if base is None:
                        return False
                    fields = ("A_rate", "K_rate")
                    if any(row.get(field) is None or base.get(field) is None
                           for field in fields):
                        return False
                    delta = {
                        path: abs(float(row[path + "_rate"]) - float(base[path + "_rate"]))
                        for path in ("A", "K")
                    }
                if any(path not in delta or float(delta[path]) > tolerance
                       for path in ("A", "K")):
                    return False
    return True


def gate_c8(rows: list[dict], ceiling: float | None) -> bool:
    """On every seed, the A-K- positive control is at or below its ceiling.

    C8 is an existence check for a third route.  Pooling A-K- rows across seeds
    would let one seed with a 1/4 assertion rate pass as 1/24; that is exactly
    the per-seed failure the control exists to detect.
    """
    if ceiling is None:
        return False
    by_seed = _by_seed(rows)
    if not by_seed:
        return False
    for group in by_seed.values():
        both_blocked = [row for row in group if row["cell"] == "A-K-"]
        if not both_blocked:
            return False
        if _fraction(both_blocked, "Y") > ceiling:
            return False
    return True


def gate_c9(rows: list[dict], tolerance: float | None = None) -> bool:
    """Every expected cell of a seed names the same world/cycles/U object."""
    by_seed: dict[int, set[str]] = {}
    cells_by_seed: dict[int, set[str]] = {}
    for row in rows:
        fingerprint = row.get("object_fingerprint")
        if fingerprint is None:
            return False
        seed = int(row["seed"])
        by_seed.setdefault(seed, set()).add(str(fingerprint))
        cells_by_seed.setdefault(seed, set()).add(str(row.get("cell")))
    return (bool(by_seed)
            and all(all(cell in cells_by_seed[seed] for cell in PRIMARY_CELLS + Y_CELLS)
                    for seed in by_seed)
            and all(len(fingerprints) == 1
                    for fingerprints in by_seed.values()))


CONTRACTS = {
    "C1_path_separation": gate_c1,
    "C2_treatment_consistency": gate_c2,
    "C3_positivity": gate_c3,
    "C4_no_interference": gate_c4,
    "C5_common_cause": gate_c5,
    "C7_assertion_block": gate_c7,
    "C8_third_route": gate_c8,
    "C9_same_object": gate_c9,
}


def validate_bounds(bounds: dict | None = None, conditions: list[dict] | None = None) -> list[str]:
    """Every open gate needs one attempt, a success rule and a terminal failure disposition."""
    bounds = BOUNDS if bounds is None else bounds
    if conditions is None:
        conditions = [{"id": gate, "status": "CONTRACT BUILT"} for gate in bounds]
    open_gates = {condition["id"] for condition in conditions
                  if condition["status"] != "SATISFIED"}
    errors: list[str] = []
    for gate in sorted(open_gates):
        if gate not in bounds:
            errors.append("%s has no stop condition" % gate)
            continue
        bound = bounds[gate]
        if bound.get("attempts") != 1:
            errors.append("%s does not have exactly one attempt" % gate)
        for field in ("attempt", "success", "on_failure", "on_unmeasurable"):
            if not bound.get(field):
                errors.append("%s has no %s" % (gate, field))
    for gate in bounds:
        if gate not in open_gates:
            errors.append("%s has a stop condition but is not open" % gate)
    return errors


def _row(seed: int, cell: str, edge: str, a: int, k: int, y: int) -> dict:
    return {
        "seed": seed,
        "cell": cell,
        "edge": edge,
        "target": False,
        "control_A": 1,
        "control_K": 1,
        "A": a,
        "K": k,
        "Y": y,
        "U": {"direct_count": 20, "reverse_count": 10, "strength": 0.8,
              "measured_cycle": 2},
        "carrier_cycle": 4,
        "k_cycle": 5,
        "y_cycle": 6,
        "neighbor_delta": {"A": 0.0, "K": 0.0, "Y": 0.0},
        "delta_from_baseline": {"A": 0.0, "K": 0.0},
        "object_fingerprint": "seed-%d" % seed,
    }


def fixture() -> list[dict]:
    rows: list[dict] = []
    for seed in (1, 2):
        for edge in ("a>b", "b>c"):
            rows += [
                _row(seed, "A+K+", edge, 1, 1, 1),
                _row(seed, "A+K-", edge, 1, 0, 0),
                _row(seed, "A-K+", edge, 0, 1, 1),
                _row(seed, "A-K-", edge, 0, 0, 0),
                _row(seed, "Y_MINUS_A+K+", edge, 1, 1, 0),
                _row(seed, "Y_MINUS_A-K+", edge, 0, 1, 0),
            ]
    return rows


def _mutate(rows: list[dict], cell: str, field: str, value: object) -> list[dict]:
    changed = [dict(row) for row in rows]
    for row in changed:
        if row["cell"] == cell:
            row[field] = value
    return changed


def self_test() -> list[str]:
    """Each contract must accept the passing fixture and reject a targeted defect."""
    found: list[str] = []
    rows = fixture()
    args = {
        "C1_path_separation": (C1_MIN,),
        "C2_treatment_consistency": (),
        "C3_positivity": (),
        "C4_no_interference": (C4_MAX,),
        "C5_common_cause": (),
        "C7_assertion_block": (C7_MAX,),
        "C8_third_route": (C8_MAX,),
        "C9_same_object": (),
    }
    for gate, function in CONTRACTS.items():
        if not function(rows, *args[gate]):
            found.append("%s does not accept the passing fixture" % gate)

    defects = {
        "C1_path_separation": _mutate(rows, "A-K+", "K", 0),
        "C2_treatment_consistency": _mutate(rows, "A-K+", "A", 1),
        "C3_positivity": [row for row in rows if row["cell"] != "A-K-"],
        "C4_no_interference": _mutate(rows, "A+K+", "neighbor_delta",
                                      {"A": 0.9, "K": 0.0, "Y": 0.0}),
        "C5_common_cause": [
            dict(row, U=dict(row["U"], strength=None)) if row["cell"] == "A+K+" else row
            for row in rows
        ],
        "C7_assertion_block": [
            dict(row, Y=1) if row["cell"] in Y_CELLS else row for row in rows
        ],
        "C8_third_route": _mutate(rows, "A-K-", "Y", 1),
        "C9_same_object": [
            dict(row, object_fingerprint="different") if row["cell"] == "A-K-" else row
            for row in rows
        ],
    }
    for gate, broken in defects.items():
        if CONTRACTS[gate](broken, *args[gate]):
            found.append("%s does not reject its targeted defect" % gate)

    if gate_c2(_mutate(rows, "Y_MINUS_A+K+", "A", 0)):
        found.append("C2 does not reject a broken Y- A path")
    missing_cycle = [dict(row, carrier_cycle=None) if row["cell"] == "A+K+" else row
                     for row in rows]
    if gate_c5(missing_cycle):
        found.append("C5 accepts a missing carrier cycle")
    if gate_c9(rows[:1]):
        found.append("C9 accepts a single row")

    if gate_c1(rows, None):
        found.append("C1 accepts a missing tolerance")
    if gate_c4(rows, None):
        found.append("C4 accepts a missing tolerance")
    if gate_c7(rows, None):
        found.append("C7 accepts a missing tolerance")
    if gate_c8(rows, None):
        found.append("C8 accepts a missing ceiling")

    conditions = [{"id": gate, "status": "CONTRACT BUILT"} for gate in BOUNDS]
    if validate_bounds(BOUNDS, conditions):
        found.append("the stop-condition set is not complete")
    missing = dict(BOUNDS)
    missing.pop("C7_assertion_block")
    if not validate_bounds(missing, conditions):
        found.append("an open gate with no stop condition is accepted")
    multiple = {gate: dict(bound) for gate, bound in BOUNDS.items()}
    multiple["C1_path_separation"]["attempts"] = 2
    if not validate_bounds(multiple, conditions):
        found.append("a gate with more than one attempt is accepted")
    return found


def audit() -> dict:
    c6 = _load(C6_PATH)
    a0 = _load(A0_PATH)
    c6_satisfied = (
        c6.get("outcome") == "C6 ORDER VARIATION CONFIRMED"
        and all(c6.get("gates", {}).values())
    )
    a0_rows = a0["rows"]
    cells = {"A+K+": 0, "A+K-": 0, "A-K+": len(a0_rows), "A-K-": 0}
    u_rows = sum(1 for row in a0_rows
                 if row.get("direct_temporal_count") is not None
                 and row.get("reverse_temporal_count") is not None)
    edge_strength = sum(1 for row in a0_rows if row.get("strength") is not None)

    conditions = [
        {
            "id": "C1_path_separation",
            "status": "CONTRACT BUILT; THRESHOLD PRECOMMITTED, NOT RUN",
            "current_evidence": (
                "A0 supports the parallel-path premise: 26/26 rows form a carrier with zero "
                "direct service, and admission leaves the carrier intact. No A- or K- arm has "
                "been executed, so cross-path separation has not been observed. Threshold: "
                "at least 95% preservation of the other path, per seed."
            ),
            "contract": "gate_c1(rows, tolerance): among paired-control available edges, A- keeps K and K- keeps A at or above the tolerance on every seed.",
            "remaining": "Implement A-/K- and run the arms; the threshold is already fixed.",
        },
        {
            "id": "C2_treatment_consistency",
            "status": "CONTRACT BUILT; NO ARM RUN",
            "current_evidence": "No A-, K- or Y- execution exists; the A0 records are observational joins.",
            "contract": "gate_c2(rows): A- drives A to zero, K- drives K to zero, Y- drives Y to zero while the other path stays above zero.",
            "remaining": "Run each manipulation and verify its named path moved.",
        },
        {
            "id": "C3_positivity",
            "status": "CONTRACT BUILT; ONE CELL ONLY",
            "current_evidence": (
                "The A0 slice contributes only A-K+ (%d rows); A+K+, A+K- and A-K- have no "
                "denominators, and the Y- cells do not exist." % cells["A-K+"]
            ),
            "contract": "gate_c3(rows): every eligible edge has all four A x K cells and every seed has both Y- cells.",
            "remaining": "Join every eligible edge to both factors and observe all six cells.",
        },
        {
            "id": "C4_no_interference",
            "status": "CONTRACT BUILT; THRESHOLD PRECOMMITTED, NOT RUN",
            "current_evidence": (
                "No edge-level intervention was run, so there is no neighbour delta to compare. "
                "Threshold: absolute A/K/Y delta no greater than 0.05 on non-target edges."
            ),
            "contract": "gate_c4(rows, tolerance): every non-target edge's A, K and Y neighbour delta stays within tolerance.",
            "remaining": "Implement the edge-level arms and measure spillover; the threshold is already fixed.",
        },
        {
            "id": "C5_common_cause",
            "status": "CONTRACT BUILT; U NOT JOINED",
            "current_evidence": (
                "Direct and reverse counts exist for all %d A0 rows; an edge-level strength field "
                "is present on %d rows, and U is not joined to all four cells or either Y- cell."
                % (u_rows, edge_strength)
            ),
            "contract": "gate_c5(rows): direct count, reverse count and strength are present and measured before the carrier, K and Y on every row.",
            "remaining": "Measure edge strength for every eligible edge and join U to all cells before the outcome.",
        },
        {
            "id": "C6_temporal_resolution",
            "status": "SATISFIED" if c6_satisfied else "REQUIRES INSTRUMENTATION",
            "current_evidence": (
                "C6-TIMING-1 returned `%s` on six fresh seeds; N1-N7 pass."
                % c6.get("outcome") if c6_satisfied else "The C6 block is not confirmed."
            ),
            "contract": "The C6 block's N1-N7 and per-order floors are the gate.",
            "remaining": "None for C6." if c6_satisfied else "Complete C6.",
        },
        {
            "id": "C7_assertion_block",
            "status": "CONTRACT BUILT; THRESHOLD PRECOMMITTED, NOT RUN",
            "current_evidence": (
                "No Y- assertion blockade exists; A and K have not been held fixed under Y-. "
                "Threshold: absolute A/K formation delta no greater than 0.05. C7 is "
                "evaluated per seed and per edge; the margin is a rate over 120 cycles "
                "(one cycle = 0.008333), so it is resolvable at N=4. The eight Y- rows "
                "are for cell completeness and the assertion-order check, not the 0.05 "
                "rate denominator. Target rows now emit A/K/Y rates."
            ),
            "contract": "gate_c7(rows, tolerance): on every seed, both Y- cells lower assertion while A and K formation stay within tolerance.",
            "remaining": "Implement Y- and run it at A+K+ and A-K+; the threshold is already fixed.",
        },
        {
            "id": "C8_third_route",
            "status": "CONTRACT BUILT; CEILING PRECOMMITTED, NOT RUN",
            "current_evidence": (
                "No A-K- double block exists. The T8 ceiling is precommitted at 0.05, so a "
                "double-block assertion rate above 5% on any seed reads THIRD ROUTE PRESENT. "
                "C8 is evaluated per seed; at N=4 that is four rows and a 0.25 step. "
                "A separate N=20 expansion design is registered; it is not the live "
                "manifest and is not frozen."
            ),
            "contract": "gate_c8(rows, ceiling): on every seed, A-K- assertion is at or below the precommitted ceiling.",
            "remaining": "Implement the double block and run it; the ceiling is already fixed.",
        },
        {
            "id": "C9_same_object",
            "status": "CONTRACT BUILT; NO PAIRED CELLS",
            "current_evidence": (
                "A0 fixes six committed seeds, 120 cycles and cap 40; the design fixes A+K+, A+K-, "
                "A-K+, A-K- and Y- at A+K+/A-K+, but no cell exists to pair."
            ),
            "contract": "gate_c9(rows): every cell of a seed carries one world/cycles/cap/candidate-universe/U fingerprint.",
            "remaining": "Run the paired cells and refuse any cell whose object fingerprint differs.",
        },
    ]
    counts = {
        "satisfied": sum(condition["status"] == "SATISFIED" for condition in conditions),
        "contract_not_run": sum(condition["status"].startswith("CONTRACT BUILT") for condition in conditions),
        "unsatisfiable": 0,
    }
    bounds_errors = validate_bounds(BOUNDS, conditions)
    return {
        "kind": "a1_gate_readiness",
        "not_a_result": True,
        "date": DATE,
        "question": "Which of the remaining A1 identifiability gates are ready, satisfied, or still require a run?",
        "verdict": (
            "NOT ADMISSIBLE — %d SATISFIED, %d CONTRACT-BUILT BUT UNRUN, 0 UNSATISFIABLE"
            % (counts["satisfied"], counts["contract_not_run"])
        ),
        "reading": (
            "C6 is satisfied by the committed C6-TIMING-1 block. The other eight gates have "
            "executable contracts and synthetic controls; C1/C4/C7 thresholds and the C8 ceiling "
            "are precommitted. C1 and C4 are one adopted post-freeze VOID gate; a failed or "
            "unmeasurable C1 or C4 makes the run VOID. Other open gates retain their own "
            "terminal dispositions. Each open gate has one attempt: no A1 patch, threshold change, "
            "extra cell or rerun; a new registered design is required to try again. None can be "
            "cleared from the observational records because each needs an A-, K-, Y- or A-K- cell "
            "that has not run. The design remains not admissible and no causal model is read."
        ),
        "counts": counts,
        "conditions": conditions,
        "bounds": {
            "status": "BOUNDED" if not bounds_errors else "UNBOUNDED",
            "rule": BOUND_RULE,
            "gates": BOUNDS,
            "errors": bounds_errors,
        },
        "thresholds": {
            "status": "PRECOMMITTED BEFORE ANY A1 CELL",
            "date": DATE,
            "values": THRESHOLDS,
            "record": "docs/A1-PRECOMMITTED-THRESHOLDS.md",
        },
        "gate_order": GATE_ORDER,
        "denominator_unit": {
            "status": "ADOPTED — BINDING FOR A1",
            "record": C7_C8_DENOMINATOR_RECORD,
            "C7_assertion_block": C7_C8_DENOMINATOR_UNIT,
            "C8_third_route": C7_C8_DENOMINATOR_UNIT,
            "rule": (
                "Every seed must pass C7 and C8 on its own rows. Rows are not "
                "pooled across seeds and there is no averaging or best-seed reading. "
                "C7's 0.05 margin is a per-edge A/K rate over 120 cycles; C8's 0.05 "
                "ceiling is a per-target-edge assertion rate."
            ),
            "units": {
                "C7_assertion_block": "PER SEED, PER EDGE RATE",
                "C8_third_route": "PER SEED, PER TARGET ROW",
            },
            "rows": {
                "C7_N4": 8, "C8_N4": 4, "C7_N8": 16, "C8_N8": 8,
            },
            "c7_rate_denominator_cycles": C7_RATE_DENOMINATOR_CYCLES,
            "c7_rate_step": C7_RATE_STEP,
            "c8_steps": {"C8_N4": 0.25, "C8_N8": 0.125},
            "minimum_targets_for_one_step_resolution": {"C7": 1, "C8": 20},
            "resolved": {"C7_N4": True, "C7_N8": True, "C8_N4": False, "C8_N8": False},
            "registered_design": {
                "id": "A1-C8-EXPANSION-1",
                "record": "docs/A1-C8-EXPANSION.md",
                "selection_artifact": "docs/a1_c8_target_selection.json",
                "n_per_seed": 20,
                "C8_step": 0.05,
                "status": "REGISTERED — NOT FROZEN, NOT RUN; NOT THE LIVE MANIFEST",
            },
            "current_design": "C7 RESOLVED; C8 UNDER-RESOLVED — N=4 and the N=8 maximum are both above the 0.05 ceiling; an N=20 design is registered but not frozen",
        },
        "evidence": {
            "a0_rows": len(a0_rows),
            "a0_slice_cells": cells,
            "a0_rows_with_u_counts": u_rows,
            "a0_rows_with_edge_strength": edge_strength,
            "c6_outcome": c6.get("outcome"),
            "c6_gates": c6.get("gates", {}),
        },
        "remaining": [condition["id"] for condition in conditions
                      if condition["status"] != "SATISFIED"],
        "not_evidence": (
            "A gate-contract audit on committed records. It runs no cell, assigns no seed and "
            "establishes no causal, capability or transfer claim."
        ),
    }


def thresholds_payload() -> dict:
    return {
        "kind": "a1_precommitted_thresholds",
        "not_a_result": True,
        "date": DATE,
        "status": "PRECOMMITTED BEFORE ANY A1 CELL",
        "design": "docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md",
        "values": THRESHOLDS,
        "rows": [
            {"gate": gate, "quantity": quantity, "value": value, "definition": definition}
            for gate, quantity, value, definition in THRESHOLD_ROWS
        ],
        "source": (
            "Design convention fixed 2026-11-14 before any A1 cell. No A0 row, seed or run "
            "result was used to choose a value."
        ),
        "fragility": (
            "At 26 paired carrier rows, a 0.95 preservation floor allows one edge to differ and "
            "fails at two; at larger denominators it allows proportionally more. A descriptive "
            "sensitivity at 0 and 0.10 is reported beside the result but cannot change the "
            "precommitted gate."
        ),
        "missing_denominator": (
            "A condition with no available edges is NOT MEASURABLE, not zero, and does not pass."
        ),
        "not_evidence": (
            "Thresholds and definitions only. No cell has run; this is not a grant and makes no "
            "causal, capability or transfer claim."
        ),
    }


def render_thresholds(payload: dict) -> str:
    lines = [
        "# A1 precommitted thresholds",
        "",
        "**Date:** %s  " % payload["date"],
        "**Status:** `%s`" % payload["status"],
        "",
        "**This is not an experimental result and not a grant.** No cell, seed or engine change was made.",
        "",
        "These values were fixed before any A1 cell. They are manipulation and independence margins,",
        "not predictions of the primary effect, and they are not estimated from A0 or any run.",
        "",
        "| Gate | Quantity | Value | Definition |",
        "| --- | --- | ---: | --- |",
    ]
    for row in payload["rows"]:
        lines.append("| `%s` | %s | %.2f | %s |" % (
            row["gate"], row["quantity"], row["value"], row["definition"]))
    lines += [
        "",
        "## Reading",
        "",
        "`C1` needs at least 95% preservation of the other path on every seed; the denominator is",
        "the paired control's available edges, not the whole candidate universe. `C4` uses a 0.05",
        "absolute-rate margin. `C7` is read per seed at both Y- cells with a 0.05 A/K formation",
        "margin. `C8` reads `THIRD ROUTE PRESENT` when any seed's `A-K-` assertion rate is above",
        "0.05; rows are not pooled across seeds.",
        "",
        "%s" % payload["missing_denominator"],
        "",
        "## Fragility",
        "",
        payload["fragility"],
        "",
        "**Source:** %s" % payload["source"],
        "",
        "**Not evidence:** %s" % payload["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_gate_readiness --check",
        "```",
        "",
    ]
    return "\n".join(lines)


def render(payload: dict) -> str:
    lines = [
        "# A1 gate readiness",
        "",
        "**Date:** %s  " % payload["date"],
        "**Verdict:** `%s`" % payload["verdict"],
        "",
        "**This is not an experimental result.** No cell, seed, intervention or engine change was made.",
        "",
        payload["reading"],
        "",
        "## Counts",
        "",
        "| Classification | Count |",
        "| --- | ---: |",
        "| Satisfied | %d |" % payload["counts"]["satisfied"],
        "| Contract built, not run | %d |" % payload["counts"]["contract_not_run"],
        "| Unsatisfiable | %d |" % payload["counts"]["unsatisfiable"],
        "",
        "## Precommitted thresholds",
        "",
        "| Gate | Quantity | Value |",
        "| --- | --- | ---: |",
    ]
    for row in THRESHOLD_ROWS:
        lines.append("| `%s` | %s | %.2f |" % (row[0], row[1], row[2]))
    lines += [
        "",
        "See [`A1-PRECOMMITTED-THRESHOLDS.md`](A1-PRECOMMITTED-THRESHOLDS.md) for definitions and fragility.",
        "",
        "## Bounded paths",
        "",
        payload["bounds"]["rule"],
        "",
        "| Gate | Attempts | Success | Failure | Unmeasurable |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for gate, bound in payload["bounds"]["gates"].items():
        lines.append("| `%s` | %d | %s | %s | %s |" % (
            gate, bound["attempts"], bound["success"].replace("|", "\\|"),
            bound["on_failure"].replace("|", "\\|"),
            bound["on_unmeasurable"].replace("|", "\\|")))
    lines += [
        "",
        "C6 is satisfied and closed; it needs no stop condition. A terminal failure is not a\n"
        "reason to patch A1, retune a threshold or add a cell.",
        "",
        "## Gate order",
        "",
        "**C1 and C4 are one POST-FREEZE VOID GATE**, not pre-freeze admissibility "
        "conditions. Neither can be observed before cells exist. Freeze the targets, "
        "grant the run, then assemble C1/C4; a C1 or C4 failure, or either being "
        "unmeasurable, makes the run VOID. The targets remain draft because no separate "
        "owner freeze act has been recorded.",
        "",
        "**C1:** %s" % GATE_ORDER["C1_path_separation"]["void_condition"],
        "",
        "**C4:** %s" % GATE_ORDER["C4_no_interference"]["void_condition"],
        "",
        "## C7/C8 denominator unit",
        "",
        "**ADOPTED — BINDING FOR A1 (2026-11-14).** C7 and C8 are evaluated **per seed**; "
        "rows are not pooled across seeds. Every seed must pass on its own rows. See "
        "[`A1-C7-C8-DENOMINATOR.md`](A1-C7-C8-DENOMINATOR.md).",
        "",
        "At N=4 C7 has **8** Y- rows for cell completeness and the assertion-order check, but its "
        "0.05 A/K margin is a **per-edge rate over 120 cycles** (`1/120 = 0.008333`), so C7 is "
        "**RESOLVED** at N=4. C8 has **4** A-K- target rows (`1/4 = 0.25`); at the N=8 maximum "
        "it has **8** (`1/8 = 0.125`). C8 needs at least 20 rows (N>=20) for one-step resolution, "
        "above the 16-vertex, eight-target maximum. A separate **N=20 C8 expansion "
        "design** is registered in [`A1-C8-EXPANSION.md`](A1-C8-EXPANSION.md); it gives "
        "20 A-K- rows per seed and a 0.05 step, resolving C8 **if adopted**, but it is "
        "not the live manifest and is not frozen. The current design is therefore "
        "**UNDER-RESOLVED for C8 only**; that is a design blocker, not a threshold change.",
        "",
        "## Gates",
        "",
        "| ID | Status | Current evidence | Contract | Remaining |",
        "| --- | --- | --- | --- | --- |",
    ]
    for condition in payload["conditions"]:
        lines.append("| `%s` | `%s` | %s | %s | %s |" % (
            condition["id"], condition["status"],
            condition["current_evidence"].replace("|", "\\|"),
            condition["contract"].replace("|", "\\|"),
            condition["remaining"].replace("|", "\\|")))
    lines += [
        "",
        "## Controls",
        "",
        "`python -m benchmarks.a1_gate_readiness --self-test` builds a passing six-cell fixture and a",
        "targeted defect for every contract. Each gate must accept the fixture and reject its defect;",
        "a missing tolerance or ceiling must fail. The self-test runs no engine.",
        "",
        "Complete-coverage scoring for C2, C3, C5, C7 and C9 is implemented in",
        "`a1_arms.score_complete_gates`. Each score requires all six seeds, its required cells, and every",
        "expected target row; a missing cell or target is a coverage failure, not a pass. `a1_result.assemble`",
        "adds these scores when the cell parts carry target lists, using the registered N=20 target map by",
        "default. These are assembly checks, not measurements: no cell has run.",
        "",
        "**Not evidence:** %s" % payload["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_gate_readiness --check",
        "python -m benchmarks.a1_gate_readiness --self-test",
        "```",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        found = self_test()
        for problem in found:
            print("FAIL:", problem)
        if not found:
            print("A1 gate contracts: every gate accepts its fixture and rejects its defect")
        return 1 if found else 0
    payload = audit()
    if payload["bounds"]["errors"]:
        for problem in payload["bounds"]["errors"]:
            print("FAIL:", problem)
        return 1
    page = render(payload)
    threshold_record = thresholds_payload()
    threshold_page = render_thresholds(threshold_record)
    if args.write:
        OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        PAGE_PATH.write_text(page, encoding="utf-8")
        THRESHOLDS_PATH.write_text(json.dumps(threshold_record, indent=2) + "\n", encoding="utf-8")
        THRESHOLDS_PAGE.write_text(threshold_page, encoding="utf-8")
        print("wrote %s, %s, %s and %s" % (
            OUT_PATH, PAGE_PATH, THRESHOLDS_PATH, THRESHOLDS_PAGE))
        return 0
    if args.check:
        for path in (OUT_PATH, PAGE_PATH, THRESHOLDS_PATH, THRESHOLDS_PAGE):
            if not path.exists():
                print("FAIL: readiness record is missing: %s" % path)
                return 1
        if _load(OUT_PATH) != payload:
            print("FAIL: %s is stale" % OUT_PATH)
            return 1
        if PAGE_PATH.read_text(encoding="utf-8") != page:
            print("FAIL: %s is stale" % PAGE_PATH)
            return 1
        if _load(THRESHOLDS_PATH) != threshold_record:
            print("FAIL: %s is stale" % THRESHOLDS_PATH)
            return 1
        if THRESHOLDS_PAGE.read_text(encoding="utf-8") != threshold_page:
            print("FAIL: %s is stale" % THRESHOLDS_PAGE)
            return 1
        found = self_test()
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("A1 gate readiness: clean; %s" % payload["verdict"])
        return 0
    parser.error("choose --write, --check or --self-test")


if __name__ == "__main__":
    raise SystemExit(main())
