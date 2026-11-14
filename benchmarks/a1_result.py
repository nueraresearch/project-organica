"""Assemble A1 cell parts into C1/C4 and complete structural-gate decisions.

This is the result-assembly layer between ``a1_arms`` cell output and the
precommitted identity gates.  It never opens a database, assigns a seed or
runs a cell.  The synthetic fixture is a control for the assembly itself,
not an A1 result.

    python -m benchmarks.a1_result --synthetic
    python -m benchmarks.a1_result --self-test
    python -m benchmarks.a1_result --parts
    python -m benchmarks.a1_result --parts .scratch/a1_two_path/parts
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import a1_arms
from benchmarks.a1_gate_readiness import C1_MIN, C4_MAX

KIND = "a1_result_assembly"
C1_DENOMINATOR_FLOOR = 60


def _observed_denominator(payloads: list[dict], c1: dict, c4: dict) -> dict:
    """Summarise the denominators actually supplied by the cell parts.

    These counts are observed rows, not the planned 63-64 C1 denominator.  A
    missing cell or a non-target edge absent from the paired control reduces
    the observed denominator, which is why the assembly reports it explicitly.
    """
    seeds = sorted({int(payload["seed"]) for payload in payloads})
    cells = sorted({str(payload.get("cell")) for payload in payloads})
    by_seed = {
        seed: {
            "a_minus": row["a_minus_denominator"],
            "k_minus": row["k_minus_denominator"],
        }
        for seed, row in c1["seeds"].items()
    }
    return {
        "status": "OBSERVED" if payloads else "NOT_RUN",
        "parts": len(payloads),
        "seeds": seeds,
        "cells": cells,
        "c1": {
            "a_minus": c1["a_minus"]["denominator"],
            "k_minus": c1["k_minus"]["denominator"],
            "by_seed": by_seed,
        },
        "c4": {
            "rows": c4["rows"],
            "measured": c4["measured"],
            "unmeasured": len(c4["unmeasured"]),
        },
    }


def _c1_reason(c1: dict) -> str:
    denominators = []
    for row in c1.get("seeds", {}).values():
        denominators.append(int(row.get("a_minus_denominator", 0)))
        denominators.append(int(row.get("k_minus_denominator", 0)))
    if not denominators or min(denominators) == 0:
        return "C1_NO_DENOMINATOR"
    if min(denominators) < C1_DENOMINATOR_FLOOR:
        return "C1_DENOMINATOR_BELOW_FLOOR"
    return "C1_THRESHOLD"


def _void_reasons(payloads: list[dict], c1: dict, c4: dict) -> list[str]:
    """Return the adopted C1/C4 VOID reason codes for a failed assembly."""
    if not payloads:
        return ["C1_C4_INCOMPLETE"]
    reasons = []
    if not c1.get("pass"):
        reasons.append(_c1_reason(c1))
    if not c4.get("pass"):
        if c4.get("rows", 0) == 0 or c4.get("measured", 0) == 0 or c4.get("unmeasured"):
            reasons.append("C4_UNMEASURABLE")
        if c4.get("violations"):
            reasons.append("C4_DELTA")
    if not reasons:
        reasons.append("C1_C4_INCOMPLETE")
    return list(dict.fromkeys(reasons))


def assemble(payloads: list[dict], c1_tolerance: float | None = None,
             c4_tolerance: float | None = None,
             expected_targets: dict | None = None,
             complete: bool | None = None) -> dict:
    """Score the assembled C1 and C4 streams, plus complete structural gates.

    The adopted C1/C4 gate reports ``PASS`` or ``VOID``. A failed or
    unmeasurable C1/C4 pair is never published as a scientific ``FAIL``.
    When the parts carry target lists (as every real cell does), C2/C3/C5/C7/C9
    are scored over the expected six-seed, six-cell target coverage as well;
    their failure does not rewrite the separate C1/C4 disposition.
    """
    c1 = a1_arms.score_c1(payloads, c1_tolerance)
    c4 = a1_arms.score_c4(payloads, c4_tolerance)
    has_targets = any(isinstance(payload.get("targets"), list)
                      and payload.get("targets") for payload in payloads)
    if complete is None:
        complete = bool(has_targets or expected_targets is not None)
    if complete and expected_targets is None:
        expected_targets = a1_arms.registered_target_map() or None
    complete_report = (a1_arms.score_complete_gates(payloads, expected_targets)
                       if complete else None)
    passed = bool(c1["pass"] and c4["pass"] and payloads)
    reasons = [] if passed else _void_reasons(payloads, c1, c4)
    void_gates = [] if passed else [
        gate for gate, prefix in (
            ("C1_path_separation", "C1_"),
            ("C4_no_interference", "C4_"),
        )
        if (not payloads or any(reason.startswith(prefix) for reason in reasons))
    ]
    gates = {
        "C1_path_separation": c1["pass"],
        "C4_no_interference": c4["pass"],
    }
    if complete_report:
        gates.update({name: row["pass"]
                      for name, row in complete_report["gates"].items()})
    return {
        "kind": KIND,
        "status": "PASS" if passed else "VOID",
        "void_gates": void_gates,
        "reason_codes": reasons,
        "parts": len(payloads),
        "c1": c1,
        "c4": c4,
        "complete_coverage": complete_report,
        "complete_status": (
            "NOT SCORED — NO TARGET LISTS" if complete_report is None
            else "PASS" if complete_report["pass"] else "FAIL"
        ),
        "all_gates_pass": bool(passed and (complete_report is None
                                           or complete_report["pass"])),
        "observed_denominator": _observed_denominator(payloads, c1, c4),
        "gates": gates,
        "not_evidence": (
            "A result-assembly decision over supplied cell parts. A VOID is not "
            "a scientific verdict; the synthetic fixture is a control, not an A1 "
            "result, causal estimate or capability claim."
        ),
    }


def _target_row(cell: str, edge: str, a: bool, k: bool, y: bool) -> dict:
    return {
        "seed": 1,
        "cell": cell,
        "edge": edge,
        "target": True,
        "A": a,
        "K": k,
        "Y": y,
        "carrier_cycle": 1,
        "k_cycle": 1,
        "y_cycle": 1,
        "control_A": cell == "A+K-",
        "control_K": cell == "A-K+",
        "U": {"direct_count": 1, "reverse_count": 1, "strength": 2,
              "measured_cycle": 36},
        "object_fingerprint": "synthetic-seed-1",
    }


def _payload(cell: str, target_rows: list[dict],
             counts: dict[tuple[str, str], dict[str, int]]) -> dict:
    edges = set(counts)
    neighbors = a1_arms.neighbor_rows(
        1, cell, edges, counts, 100, "synthetic-seed-1", set()
    )
    return {
        "kind": "a1_two_path_cell",
        "seed": 1,
        "cell": cell,
        "rows": target_rows,
        "neighbor_rows": neighbors,
        "neighbor_count": len(neighbors),
    }


def synthetic_parts(c4_delta: float = 0.04) -> list[dict]:
    """Build a three-cell fixture with a known C1 pass and configurable C4 delta."""
    targets = ["e%d>t%d" % (i, i) for i in range(4)]
    neighbor_edges = [("n%d" % i, "m%d" % i) for i in range(16)]
    # Baseline A/K availability makes the non-target rows eligible for C1;
    # the rates are 1/100, below the C4 margin.  Only Y is absent.
    zero = {edge: {"A": 1, "K": 1, "Y": 0} for edge in neighbor_edges}

    baseline_targets = [_target_row("A+K+", edge, True, True, True)
                        for edge in targets]
    a_minus_targets = [_target_row("A-K+", edge, False, True, True)
                       for edge in targets]
    k_minus_targets = [_target_row("A+K-", edge, True, False, True)
                       for edge in targets]

    # C1: A- keeps K on 19/20 pairs; K- keeps A on 20/20 pairs.
    a_minus_counts = {edge: {"A": 0, "K": 1, "Y": 0}
                      for edge in neighbor_edges}
    a_minus_counts[neighbor_edges[0]]["K"] = 0
    # C4: one non-target Y rate is exactly the requested delta; A/K stay at 0.01.
    y_cycles = int(round(c4_delta * 100))
    a_minus_counts[neighbor_edges[0]]["Y"] = y_cycles
    k_minus_counts = {edge: {"A": 1, "K": 0, "Y": 0}
                      for edge in neighbor_edges}

    return [
        _payload("A+K+", baseline_targets, zero),
        _payload("A-K+", a_minus_targets, a_minus_counts),
        _payload("A+K-", k_minus_targets, k_minus_counts),
    ]


def render(report: dict) -> str:
    c1 = report["c1"]
    c4 = report["c4"]
    observed = report["observed_denominator"]
    lines = [
        "A1 result assembly: %s" % report["status"],
    ]
    if report["status"] == "VOID":
        lines += [
            "VOID gates: %s" % (", ".join(report["void_gates"]) or "none"),
            "Reason codes: %s" % (", ".join(report["reason_codes"]) or "none"),
        ]
    lines += [
        "",
        "Observed denominator: %s; %d part(s), %d seed(s), cells %s" % (
            observed["status"], observed["parts"], len(observed["seeds"]),
            ", ".join(observed["cells"]) or "none",
        ),
        "  C1 observed denominator: A- %d rows; K- %d rows" % (
            observed["c1"]["a_minus"], observed["c1"]["k_minus"],
        ),
        "  C4 observed denominator: %d rows; %d measured; %d unmeasured" % (
            observed["c4"]["rows"], observed["c4"]["measured"],
            observed["c4"]["unmeasured"],
        ),
        "",
        "C1 %s: A- %d/%d = %.3f; K- %d/%d = %.3f; tolerance %.3f" % (
            "PASS" if c1["pass"] else "FAIL",
            c1["a_minus"]["available"], c1["a_minus"]["denominator"],
            c1["a_minus"]["fraction"],
            c1["k_minus"]["available"], c1["k_minus"]["denominator"],
            c1["k_minus"]["fraction"], c1["tolerance"],
        ),
    ]
    for seed, row in c1["seeds"].items():
        lines.append(
            "  seed %s: A- %d/%d=%.3f K- %d/%d=%.3f -> %s" % (
                seed, row["a_minus_available"], row["a_minus_denominator"],
                row["a_minus_fraction"], row["k_minus_available"],
                row["k_minus_denominator"], row["k_minus_fraction"],
                "PASS" if row["pass"] else "FAIL",
            )
        )
    lines += [
        "C4 %s: %d non-target rows, %d measured; max A/K/Y = %.6f/%.6f/%.6f; "
        "tolerance %.3f" % (
            "PASS" if c4["pass"] else "FAIL",
            c4["rows"], c4["measured"], c4["max_delta"]["A"],
            c4["max_delta"]["K"], c4["max_delta"]["Y"], c4["tolerance"],
        ),
    ]
    for violation in c4["violations"]:
        lines.append(
            "  violation: seed=%s cell=%s edge=%s path=%s delta=%s" % (
                violation["seed"], violation["cell"], violation["edge"],
                violation["path"], violation["delta"],
            )
        )
    for row in c4["unmeasured"]:
        lines.append(
            "  unmeasured: seed=%s cell=%s edge=%s" % (
                row["seed"], row["cell"], row["edge"],
            )
        )
    complete = report.get("complete_coverage")
    if complete:
        lines += [
            "",
            "Complete-coverage gates: %s; %d failed" % (
                "PASS" if complete["pass"] else "FAIL", len(complete["failed"]),
            ),
        ]
        for name, row in complete["gates"].items():
            coverage = row["coverage"]
            lines.append(
                "  %s: %s; rows %d/%d; coverage problems %d" % (
                    name, "PASS" if row["pass"] else "FAIL",
                    coverage["rows_observed"], coverage["rows_expected"],
                    len(coverage["problems"]),
                )
            )
    return "\n".join(lines)


def load_parts(directory: Path) -> list[dict]:
    payloads = []
    for path in sorted(directory.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("kind") == "a1_two_path_cell" and not doc.get("control"):
            payloads.append(doc)
    return payloads


def self_test() -> list[str]:
    found: list[str] = []
    passed = assemble(synthetic_parts(0.04))
    if passed["status"] != "PASS":
        found.append("the passing fixture does not assemble to PASS")
    if passed["void_gates"] or passed["reason_codes"]:
        found.append("the passing fixture carries VOID metadata")
    if passed["c1"]["a_minus"]["denominator"] != 20:
        found.append("C1 fixture denominator is not 20")
    if passed["c1"]["a_minus"]["available"] != 19:
        found.append("C1 fixture A- availability is not 19")
    if passed["c1"]["k_minus"]["available"] != 20:
        found.append("C1 fixture K- availability is not 20")
    if passed["c4"]["max_delta"]["Y"] != 0.04:
        found.append("C4 fixture Y delta is not 0.04")
    observed = passed["observed_denominator"]
    if observed["status"] != "OBSERVED" or observed["c1"]["a_minus"] != 20:
        found.append("the fixture does not report its observed C1 A- denominator")
    if observed["c4"]["measured"] != 48:
        found.append("the fixture does not report its observed C4 denominator")
    failed = assemble(synthetic_parts(0.06))
    if failed["status"] != "VOID":
        found.append("the failing C4 fixture does not assemble to VOID")
    if failed["void_gates"] != ["C4_no_interference"]:
        found.append("the failing C4 fixture records the wrong VOID gate")
    if failed["reason_codes"] != ["C4_DELTA"]:
        found.append("the failing C4 fixture records the wrong reason code")
    if not failed["c4"]["violations"]:
        found.append("the failing C4 fixture records no violation")
    if failed["c1"]["pass"] is not True:
        found.append("C4 failure incorrectly changes C1")
    incomplete = assemble([])
    if incomplete["status"] != "VOID" or incomplete["reason_codes"] != ["C1_C4_INCOMPLETE"]:
        found.append("the empty assembly does not record C1_C4_INCOMPLETE")
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--synthetic", action="store_true")
    group.add_argument("--parts", type=Path, nargs="?", const=a1_arms.PARTS)
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        found = self_test()
        for problem in found:
            print("FAIL:", problem)
        if not found:
            print("A1 result assembly: self-test clean")
        return 1 if found else 0
    if args.synthetic:
        payloads = synthetic_parts()
    else:
        payloads = load_parts(args.parts)
        if not payloads:
            print("A1 result assembly: NOT RUN — no cell parts in %s" % args.parts)
            print("No observed denominator exists until a cell writes a part.")
            return 2
    report = assemble(payloads)
    print(render(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
