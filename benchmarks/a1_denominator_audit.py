"""Audit whether A1 gate thresholds are finer than their planned denominators.

The smallest nonzero change in a proportion is ``1 / n``.  For a gate with a
floor or ceiling margin, that step is finer than the gate when it is larger
than the margin.  This audit reads only the precommitted thresholds and the
target-selection counts; it opens no engine and runs no cell.

    python -m benchmarks.a1_denominator_audit --write
    python -m benchmarks.a1_denominator_audit --check
    python -m benchmarks.a1_denominator_audit --self-test
    python -m benchmarks.a1_denominator_audit --parts [DIR]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks.a1_gate_readiness import (
    C7_C8_DENOMINATOR_RECORD,
    C7_C8_DENOMINATOR_UNIT,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SELECTION_PATH = DOCS / "a1_target_selection.json"
THRESHOLDS_PATH = DOCS / "a1_precommitted_thresholds.json"
OUT_PATH = DOCS / "a1_denominator_resolution.json"
PAGE_PATH = DOCS / "A1-DENOMINATOR-RESOLUTION.md"
OBSERVED_OUT_PATH = DOCS / "a1_denominator_resolution_observed.json"
OBSERVED_PAGE_PATH = DOCS / "A1-DENOMINATOR-RESOLUTION-OBSERVED.md"
DEFAULT_PARTS = ROOT / ".scratch" / "a1_two_path" / "parts"
KIND = "a1_denominator_resolution_audit"
OBSERVED_KIND = "a1_denominator_resolution_observed"
DATE = "2026-11-14"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _greedy_disjoint_count(edges, limit: int) -> int:
    """Count a greedy disjoint prefix; enough to show N=8 is feasible here."""
    used: set[str] = set()
    count = 0
    for edge in sorted(edges):
        left, right = edge.split(">")
        if left in used or right in used:
            continue
        used.update((left, right))
        count += 1
        if count == limit:
            break
    return count


def _denominator_unit() -> dict:
    """The adopted C7/C8 evaluation unit, recorded beside every denominator table."""
    return {
        "status": "ADOPTED — BINDING FOR A1",
        "record": C7_C8_DENOMINATOR_RECORD,
        "C7_assertion_block": C7_C8_DENOMINATOR_UNIT,
        "C8_third_route": C7_C8_DENOMINATOR_UNIT,
        "units": {
            "C7_assertion_block": "PER SEED, PER EDGE RATE",
            "C8_third_route": "PER SEED, PER TARGET ROW",
        },
        "rule": (
            "C7 and C8 are evaluated on each seed's own rows. Rows are not pooled "
            "across seeds; no averaging or best-seed reading is permitted. C7's 0.05 "
            "margin is an A/K rate over 120 cycles per edge, not a proportion over "
            "the 2N Y- rows."
        ),
        "per_seed_rows": {"C7_N4": 8, "C8_N4": 4, "C7_N8": 16, "C8_N8": 8, "C8_N20": 20},
        "row_role": {
            "C7": "The 2N Y- rows establish cell completeness and the assertion-order check; they are not the 0.05 A/K rate denominator.",
            "C8": "The N A-K- target rows are the assertion-rate denominator.",
        },
        "c7_rate_denominator_cycles": 120,
        "c7_rate_step": 0.008333,
        "c8_per_seed_steps": {"C8_N4": 0.25, "C8_N8": 0.125, "C8_N20": 0.05},
        "minimum_targets_for_one_step_resolution": {"C7": 1, "C8": 20},
        "resolved": {"C7_N4": True, "C7_N8": True, "C8_N4": False, "C8_N8": False, "C8_N20": True},
        "registered_design": {
            "id": "A1-C8-EXPANSION-1",
            "record": "docs/A1-C8-EXPANSION.md",
            "selection_artifact": "docs/a1_c8_target_selection.json",
            "n_per_seed": 20,
            "C8_step": 0.05,
            "status": "REGISTERED — NOT FROZEN, NOT RUN; NOT THE LIVE MANIFEST",
        },
        "pooled_reading": "REJECTED — not an A1 denominator for C7 or C8",
        "pooled_rows_if_it_were_used": {
            "C7_N4": 48, "C8_N4": 24, "C7_N8": 96, "C8_N8": 48,
        },
        "reason": (
            "Pooling would let one seed's 1/4 A-K- assertion rate pass as 1/24, "
            "hiding exactly the per-seed third route C8 is meant to detect. Pooling "
            "C7 also averages a failing seed's per-edge A/K rate into a passing one."
        ),
    }


def _row(gate: str, scenario: str, quantity: str, threshold: float | None,
         threshold_kind: str, denominator: int | None,
         denominator_max: int | None, basis: str,
         consequence: str) -> dict:
    if threshold is None or denominator is None:
        return {
            "gate": gate,
            "scenario": scenario,
            "quantity": quantity,
            "threshold": threshold,
            "threshold_kind": threshold_kind,
            "denominator": denominator,
            "denominator_max": denominator_max,
            "denominator_basis": basis,
            "smallest_step": None,
            "margin": None,
            "finer_than_denominator": None,
            "status": "NOT_APPLICABLE",
            "consequence": consequence,
        }
    margin = (1.0 - threshold) if threshold_kind == "floor" else threshold
    step = 1.0 / denominator
    return {
        "gate": gate,
        "scenario": scenario,
        "quantity": quantity,
        "threshold": threshold,
        "threshold_kind": threshold_kind,
        "denominator": denominator,
        "denominator_max": denominator_max,
        "denominator_basis": basis,
        "smallest_step": round(step, 6),
        "margin": round(margin, 6),
        "finer_than_denominator": step > margin,
        "status": "FLAGGED" if step > margin else "PASS",
        "consequence": consequence,
    }


def build() -> dict:
    selection = _load(SELECTION_PATH)
    thresholds = _load(THRESHOLDS_PATH)["values"]
    candidates = [int(row["candidate_count"])
                  for row in selection["per_seed"].values()]
    planned_c1_min, planned_c1_max = min(candidates), max(candidates)
    non_target_min = planned_c1_min - 4
    non_target_max = planned_c1_max - 4
    c1 = float(thresholds["C1_A_minus_carrier_preservation_min"])
    c4 = float(thresholds["C4_neighbor_delta_max"])
    c7 = float(thresholds["C7_A_delta_max"])
    c8 = float(thresholds["C8_third_route_assertion_max"])
    tag_vertex_counts = []
    feasible_seeds = 0
    for row in selection["per_seed"].values():
        edges = row["u"]
        tag_vertex_counts.append(len({tag for edge in edges for tag in edge.split(">")}))
        if _greedy_disjoint_count(edges, 8) >= 8:
            feasible_seeds += 1
    max_by_vertices = min(count // 2 for count in tag_vertex_counts)
    n8 = 8
    n8_non_target_min = planned_c1_min - n8
    n8_non_target_max = planned_c1_max - n8

    gates = [
        _row(
            "C1_path_separation", "target-only fallback",
            "A-/K- preservation", c1, "floor", 4, 4,
            "four target rows, no C4 expansion",
            "3/4 = 0.75; one loss fails the 0.95 floor.",
        ),
        _row(
            "C1_path_separation", "N=8 maximum-feasibility target-only",
            "A-/K- preservation", c1, "floor", n8, n8,
            "eight disjoint target rows, no C4 expansion",
            "7/8 = 0.875; one loss still fails the 0.95 floor.",
        ),
        _row(
            "C1_path_separation", "expanded C4 denominator",
            "A-/K- preservation", c1, "floor", planned_c1_min, planned_c1_max,
            "four targets plus 59-60 baseline-available non-target rows",
            "The planned denominator clears the one-step resolution test; the observed denominator is still unknown.",
        ),
        _row(
            "C1_path_separation", "N=8 maximum-feasibility expanded denominator",
            "A-/K- preservation", c1, "floor", planned_c1_min, planned_c1_max,
            "eight targets plus 55-56 baseline-available non-target rows",
            "The 63-64 total denominator still clears the resolution test; the observed denominator is still unknown.",
        ),
        _row(
            "C4_no_interference", "all cells", "A/K/Y neighbour delta",
            c4, "ceiling", non_target_min, non_target_max,
            "59-60 non-target edges per seed",
            "The planned row count resolves a 0.05 rate margin; per-edge cycle rates are finer still.",
        ),
        _row(
            "C4_no_interference", "N=8 maximum-feasibility all cells",
            "A/K/Y neighbour delta", c4, "ceiling", n8_non_target_min, n8_non_target_max,
            "55-56 non-target edges per seed",
            "1/55 = 0.018182; the denominator shrinks but still resolves the 0.05 margin.",
        ),
        _row(
            "C7_assertion_block", "Y- blocked rows", "A/K rate delta",
            c7, "ceiling", 120, 120,
            "120 cycles on each paired target edge; eight Y- rows are completeness/order evidence",
            "1/120 = 0.008333, below the 0.05 margin; C7 is resolved at N=4. The eight rows are not the rate denominator.",
        ),
        _row(
            "C7_assertion_block", "N=8 maximum-feasibility Y- blocked rows",
            "A/K rate delta", c7, "ceiling", 120, 120,
            "120 cycles on each paired target edge; sixteen Y- rows are completeness/order evidence",
            "The rate step stays 1/120 = 0.008333; N does not change C7 rate resolution, so C7 is resolved at N=8.",
        ),
        _row(
            "C8_third_route", "A-K- blocked rows", "assertion rate",
            c8, "ceiling", 4, 4,
            "four A-K- target rows",
            "One row changes the assertion rate by 1/4 = 0.25, above the 0.05 ceiling.",
        ),
        _row(
            "C8_third_route", "N=8 maximum-feasibility A-K- blocked rows",
            "assertion rate", c8, "ceiling", n8, n8,
            "eight A-K- target rows",
            "1/8 = 0.125; still above 0.05. C8 needs at least 20 rows (N>=20) for a one-step resolution.",
        ),
        _row(
            "C8_third_route", "registered N=20 C8 expansion",
            "assertion rate", c8, "ceiling", 20, 20,
            "twenty A-K- target rows per seed; registered design, not the live manifest",
            "1/20 = 0.05; equality is not finer than the ceiling, so the registered N=20 design resolves C8 if adopted.",
        ),
        _row(
            "C2_treatment_consistency", "per manipulated arm",
            "named-path check", None, "structural", 4, 4,
            "four target rows per arm",
            "No numeric tolerance; this is a structural all-rows check, not a rate.",
        ),
        _row(
            "C3_positivity", "per target edge", "cell coverage",
            None, "structural", 4, 4,
            "four target edges x all six cells",
            "No numeric tolerance; this is a coverage check.",
        ),
        _row(
            "C5_common_cause", "target rows", "pre-outcome U",
            None, "structural", 4, 4,
            "four target rows",
            "No numeric tolerance; this is a measurement-order check.",
        ),
        _row(
            "C6_temporal_resolution", "six-seed block", "K/Y order floors",
            None, "structural", 653, 672,
            "653 observed rows of 672 world-edge slots",
            "No numeric tolerance; C6 is a satisfied order-resolution block.",
        ),
        _row(
            "C9_same_object", "paired cells", "object fingerprint",
            None, "structural", 6, 6,
            "six cells per seed",
            "No numeric tolerance; this is an identity check.",
        ),
    ]

    flagged = [row["gate"] + " — " + row["scenario"]
               for row in gates if row["status"] == "FLAGGED"]
    passed = [row["gate"] + " — " + row["scenario"]
              for row in gates if row["status"] == "PASS"]
    not_applicable = [row["gate"] + " — " + row["scenario"]
                      for row in gates if row["status"] == "NOT_APPLICABLE"]
    return {
        "kind": KIND,
        "id": KIND,
        "date": DATE,
        "status": (
            "FLAGGED — %d GATE SCENARIO(S) FINER THAN PLANNED DENOMINATOR"
            % len(flagged) if flagged else "PASS — ALL NUMERIC GATES RESOLVABLE"
        ),
        "rule": (
            "For a proportion over n rows, the smallest nonzero change is 1/n. "
            "For a floor threshold t, the margin is 1-t; for a ceiling threshold "
            "t, the margin is t. A gate is FLAGGED when 1/n is greater than its "
            "margin; equality is not finer. C8 uses each seed's own A-K- rows. "
            "C7's 0.05 margin is an A/K rate difference over the 120 cycles on "
            "each paired target edge, not over the 2N Y- rows."
        ),
        "denominator_unit": _denominator_unit(),
        "sources": {
            "selection": "docs/a1_target_selection.json",
            "thresholds": "docs/a1_precommitted_thresholds.json",
        },
        "inputs": {
            "candidate_counts": candidates,
            "planned_c1_min": planned_c1_min,
            "planned_c1_max": planned_c1_max,
            "planned_non_target_min": non_target_min,
            "planned_non_target_max": non_target_max,
            "tag_vertices_per_seed": tag_vertex_counts,
            "maximum_feasibility": {
                "n_targets": n8,
                "max_disjoint_targets_from_tag_vertices": max_by_vertices,
                "feasible_seeds_with_eight_disjoint": feasible_seeds,
                "n8_non_target_min": n8_non_target_min,
                "n8_non_target_max": n8_non_target_max,
            },
        },
        "summary": {
            "flagged": flagged,
            "passed": passed,
            "not_applicable": not_applicable,
        },
        "gates": gates,
        "not_evidence": (
            "A resolution audit over planned denominators and precommitted "
            "thresholds. It runs no cell, assigns no seed, and does not measure "
            "C1, C4, C7 or C8."
        ),
    }


def _observed_range(values: list[int]) -> tuple[int | None, int | None]:
    return (min(values), max(values)) if values else (None, None)


def _observed_row(gate: str, scenario: str, quantity: str, threshold: float,
                  threshold_kind: str, denominator: int | None,
                  denominator_max: int | None, basis: str,
                  consequence: str) -> dict:
    row = _row(gate, scenario, quantity, threshold, threshold_kind,
               denominator, denominator_max, basis, consequence)
    if denominator is None:
        row["status"] = "UNMEASURED"
        row["consequence"] = "No observed denominator is available for this gate."
    return row


def observed_build(payloads: list[dict], source: Path | None = None) -> dict:
    """Recompute the resolution test from actual A1 cell parts.

    The planned audit answers whether the design *would* be resolvable. This
    observed update answers whether the parts that actually exist are. It uses
    the minimum supplied denominator per gate, never fills a missing value
    with zero, and writes a separate artifact from the planned audit.
    """
    from benchmarks import a1_result, a1_two_path
    from benchmarks.a1_gate_readiness import Y_CELLS

    assembly = a1_result.assemble(payloads)
    seeds = sorted({str(int(payload["seed"])) for payload in payloads})
    cells = sorted({str(payload.get("cell")) for payload in payloads})
    expected_cells = [cell["id"] for cell in a1_two_path.CELLS]
    expected_pairs = {
        (str(seed), cell) for seed in a1_two_path.SEEDS for cell in expected_cells
    }
    present_pairs = {
        (str(int(payload["seed"])), str(payload.get("cell")))
        for payload in payloads
    }
    missing = sorted("%s/%s" % pair for pair in expected_pairs - present_pairs)

    c1_by_seed = {
        str(seed): {
            "a_minus": int(row["a_minus_denominator"]),
            "k_minus": int(row["k_minus_denominator"]),
        }
        for seed, row in assembly["c1"]["seeds"].items()
    }
    c1_values = [value for row in c1_by_seed.values()
                 for value in (row["a_minus"], row["k_minus"]) if value > 0]
    c1_min, c1_max = _observed_range(c1_values)

    c4_by_seed: dict[str, set[str]] = {}
    c4_unmeasured: dict[str, set[str]] = {}
    for payload in payloads:
        seed = str(int(payload["seed"]))
        for row in payload.get("neighbor_rows", []):
            if row.get("target"):
                continue
            edge = str(row["edge"])
            if row.get("neighbor_delta") is not None:
                c4_by_seed.setdefault(seed, set()).add(edge)
            else:
                c4_unmeasured.setdefault(seed, set()).add(edge)
    c4_counts = [len(edges) for edges in c4_by_seed.values() if edges]
    c4_min, c4_max = _observed_range(c4_counts)

    c7_by_seed: dict[str, list[int]] = {seed: [] for seed in seeds}
    c8_by_seed = {seed: 0 for seed in seeds}
    for payload in payloads:
        seed = str(int(payload["seed"]))
        cell = str(payload.get("cell"))
        for row in payload.get("rows", []):
            if not row.get("target"):
                continue
            if cell in Y_CELLS:
                cycles = (row.get("A_cycles"), row.get("K_cycles"))
                if all(isinstance(value, int) and value > 0 for value in cycles):
                    c7_by_seed[seed].append(min(cycles))
            if cell == "A-K-":
                c8_by_seed[seed] += 1
    c7_values = [min(values) for values in c7_by_seed.values() if values]
    c8_values = [value for value in c8_by_seed.values() if value > 0]
    c7_min, c7_max = _observed_range(c7_values)
    c8_min, c8_max = _observed_range(c8_values)

    c1 = float(_load(THRESHOLDS_PATH)["values"]["C1_A_minus_carrier_preservation_min"])
    c4 = float(_load(THRESHOLDS_PATH)["values"]["C4_neighbor_delta_max"])
    c7 = float(_load(THRESHOLDS_PATH)["values"]["C7_A_delta_max"])
    c8 = float(_load(THRESHOLDS_PATH)["values"]["C8_third_route_assertion_max"])

    gates = [
        _observed_row(
            "C1_path_separation", "observed paired-control rows",
            "A-/K- preservation", c1, "floor", c1_min, c1_max,
            "minimum observed C1 paired-control rows across seeds and A-/K- paths",
            "Resolution only. A PASS here does not satisfy C1's separate 60-row floor.",
        ),
        _observed_row(
            "C4_no_interference", "observed non-target edges",
            "A/K/Y neighbour delta", c4, "ceiling", c4_min, c4_max,
            "minimum distinct non-target edges with paired-control deltas per seed",
            "Observed non-target edges; a missing delta is unmeasured, not a zero-row denominator.",
        ),
        _observed_row(
            "C7_assertion_block", "observed A/K cycle denominator",
            "A/K rate delta", c7, "ceiling", c7_min, c7_max,
            "minimum observed A/K cycle count on paired Y- target edges per seed",
            "Observed per-edge cycle rates; a missing cycle count is unmeasured, not a row denominator.",
        ),
        _observed_row(
            "C8_third_route", "observed A-K- blocked rows",
            "assertion rate", c8, "ceiling", c8_min, c8_max,
            "minimum target rows in the A-K- cell per seed",
            "Observed positive-control rows; this is a denominator statement, not a C8 verdict.",
        ),
    ]
    flagged = [row["gate"] + " — " + row["scenario"]
               for row in gates if row["status"] == "FLAGGED"]
    passed = [row["gate"] + " — " + row["scenario"]
              for row in gates if row["status"] == "PASS"]
    unmeasured = [row["gate"] + " — " + row["scenario"]
                  for row in gates if row["status"] == "UNMEASURED"]
    if flagged:
        status = ("%d GATE(S) FINER THAN OBSERVED DENOMINATOR"
                  % len(flagged))
    elif unmeasured:
        status = "%d GATE(S) UNMEASURED" % len(unmeasured)
    else:
        status = "ALL NUMERIC GATES RESOLVABLE"
    if unmeasured and flagged:
        status += "; %d UNMEASURED" % len(unmeasured)
    status = "OBSERVED — " + status
    if missing:
        status = "OBSERVED — PARTIAL COVERAGE; " + status[len("OBSERVED — "):]
    return {
        "kind": OBSERVED_KIND,
        "id": OBSERVED_KIND,
        "date": DATE,
        "status": status,
        "source": str(source) if source is not None else None,
        "rule": (
            "For a proportion over n observed rows, the smallest nonzero change "
            "is 1/n. For a floor threshold t the margin is 1-t; for a ceiling "
            "threshold t the margin is t. A gate is FLAGGED when 1/n is greater "
            "than its margin; equality is not finer. C8 uses each seed's own "
            "A-K- rows. C7 uses the observed A/K cycles on each paired Y- edge, "
            "not a row count; pooled rows are not a denominator."
        ),
        "denominator_unit": _denominator_unit(),
        "coverage": {
            "status": "PARTIAL" if missing else "COMPLETE",
            "parts": len(payloads),
            "seeds": seeds,
            "cells": cells,
            "expected_seeds": [str(seed) for seed in a1_two_path.SEEDS],
            "expected_cells": expected_cells,
            "expected_parts": len(expected_pairs),
            "missing": missing,
        },
        "assembly": {
            "status": assembly["status"],
            "parts": assembly["parts"],
        },
        "observed": {
            "c1": {"min": c1_min, "max": c1_max, "by_seed": c1_by_seed},
            "c4": {"min": c4_min, "max": c4_max,
                   "by_seed": {seed: sorted(edges)
                               for seed, edges in c4_by_seed.items()},
                   "unmeasured": {seed: sorted(edges)
                                  for seed, edges in c4_unmeasured.items()}},
            "c7": {"min": c7_min, "max": c7_max,
                   "by_seed": {seed: (min(values) if values else None)
                               for seed, values in c7_by_seed.items()}},
            "c8": {"min": c8_min, "max": c8_max, "by_seed": c8_by_seed},
        },
        "summary": {
            "flagged": flagged,
            "passed": passed,
            "unmeasured": unmeasured,
        },
        "gates": gates,
        "not_evidence": (
            "A post-run denominator record computed from supplied A1 cell parts. "
            "It scores no gate, selects no model and makes no capability claim; "
            "it only asks whether the observed denominators can resolve the "
            "precommitted margins. C1's 60-row floor is a separate rule."
        ),
    }


def render_observed(doc: dict) -> str:
    coverage = doc["coverage"]
    lines = [
        "# A1 denominator-resolution audit — observed",
        "",
        "**Date:** %s" % doc["date"],
        "**Status:** `%s`" % doc["status"],
        "**Source:** `%s`" % (doc["source"] or "—"),
        "",
        "**This is not an A1 result or a gate PASS/FAIL.** It recomputes the "
        "resolution test from supplied parts; no model, C7 or C8 verdict follows.",
        "",
        doc["rule"],
        "",
        "**Denominator unit:** C7 and C8 are per seed; pooled rows are rejected. "
        "See [`A1-C7-C8-DENOMINATOR.md`](A1-C7-C8-DENOMINATOR.md).",
        "",
        "## Coverage",
        "",
        "**%s** — %d part(s), %d seed(s), cells %s." % (
            coverage["status"], coverage["parts"], len(coverage["seeds"]),
            ", ".join(coverage["cells"]) or "none",
        ),
    ]
    if coverage["missing"]:
        lines.append(
            "Missing planned cells: **%d** of %d. Denominators below are the "
            "minimum over supplied parts, not a complete six-seed result." % (
                len(coverage["missing"]), coverage["expected_parts"],
            )
        )
    lines += [
        "",
        "## Observed gates",
        "",
        "| Gate | Scenario | Threshold | Denominator | Step | Status |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in doc["gates"]:
        threshold = "%.2f" % row["threshold"]
        denominator = ("%d" % row["denominator"]
                       if row["denominator"] is not None else "—")
        if (row["denominator_max"] is not None
                and row["denominator_max"] != row["denominator"]):
            denominator = "%d–%d" % (row["denominator"], row["denominator_max"])
        step = "%.6f" % row["smallest_step"] if row["smallest_step"] is not None else "—"
        lines.append("| `%s` | %s | %s | %s | %s | **%s** |" % (
            row["gate"], row["scenario"], threshold, denominator, step,
            row["status"]))
    lines += [
        "",
        "## Flags",
        "",
    ]
    lines += (["- `%s`" % item for item in doc["summary"]["flagged"]]
              if doc["summary"]["flagged"] else ["- none"])
    if doc["summary"]["unmeasured"]:
        lines += ["", "## Unmeasured", ""]
        lines += ["- `%s`" % item for item in doc["summary"]["unmeasured"]]
    lines += [
        "",
        "**C1 note:** the observed C1 denominator is the minimum across seeds "
        "and both paths. A resolution PASS does not satisfy C1's separate 60-row "
        "floor; resolution and gate status are different questions.",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def write_observed(payloads: list[dict], source: Path | None = None) -> int:
    doc = observed_build(payloads, source)
    OBSERVED_OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    OBSERVED_PAGE_PATH.write_text(render_observed(doc), encoding="utf-8")
    print("wrote %s and %s" % (OBSERVED_OUT_PATH, OBSERVED_PAGE_PATH))
    print(doc["status"])
    return 0


def render(doc: dict) -> str:
    lines = [
        "# A1 denominator-resolution audit",
        "",
        "**Date:** %s" % doc["date"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** No cell was run; the observed denominators are still unknown.",
        "",
        doc["rule"],
        "",
        "## Denominator unit",
        "",
        "**ADOPTED — BINDING FOR A1 (2026-11-14): C7 and C8 are per seed.** See "
        "[`A1-C7-C8-DENOMINATOR.md`](A1-C7-C8-DENOMINATOR.md). Rows are not pooled "
        "across seeds; every seed must pass on its own rows. The pooled reading is "
        "rejected, not an alternative interpretation.",
        "",
        "| Gate | Unit | N=4 rows/seed | N=4 step | N=8 rows/seed | N=8 step | N=20 registered rows/seed | N=20 step |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        "| `C7_assertion_block` | per seed, per edge rate | 8 (completeness/order) | 0.008333 (120 cycles) | 16 (completeness/order) | 0.008333 (120 cycles) | 40 (completeness/order) | 0.008333 (120 cycles) |",
        "| `C8_third_route` | per seed, per target row | 4 | 0.250000 | 8 | 0.125000 | 20 | 0.050000 |",
        "",
        "C7's 0.05 margin is an A/K rate over 120 cycles on each paired target edge, so "
        "one cycle is 1/120 = 0.008333 and **C7 is resolved at N=4 and N=8**. The 2N Y- "
        "rows are for cell completeness and the assertion-order check, not the rate "
        "denominator. C8 is a per-target assertion rate: N=4 gives 0.25 and N=8 gives "
        "0.125, both above 0.05, and the registered N=20 design gives 0.05; C8 needs at least 20 rows per seed (N>=20) for "
        "one-step resolution. The maximum disjoint target block is N=8, so the current "
        "design is **UNDER-RESOLVED for C8 only**. A separate registered N=20 C8 "
        "expansion design gives 20 A-K- rows per seed and a 0.05 step, so it resolves "
        "the C8 denominator **if adopted**; it is registered, not frozen, and is not "
        "the live manifest. The pooled counts at N=4 would be 48 C7 rows and 24 C8 "
        "rows; they are recorded only to show what was rejected, and the 24-row C8 "
        "pooled count would turn 1/4 = 0.25 into 1/24 = 0.041667.",
        "",
        "## Gates",
        "",
        "| Gate | Scenario | Threshold | Denominator | Step | Status |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in doc["gates"]:
        threshold = ("%.2f" % row["threshold"]) if row["threshold"] is not None else "—"
        denominator = ("%d" % row["denominator"]) if row["denominator"] is not None else "—"
        if row["denominator_max"] is not None and row["denominator_max"] != row["denominator"]:
            denominator = "%d–%d" % (row["denominator"], row["denominator_max"])
        step = ("%.6f" % row["smallest_step"]) if row["smallest_step"] is not None else "—"
        lines.append("| `%s` | %s | %s | %s | %s | **%s** |" % (
            row["gate"], row["scenario"], threshold, denominator, step, row["status"]))
    lines += [
        "",
        "## N=8 maximum-feasibility reading",
        "",
        "Eight disjoint targets use all 16 tag vertices, so N=8 is the maximum "
        "disjoint target block; eight disjoint edges are available in every seed. "
        "At that maximum, C7 has 16 Y- rows and C8 has 8 A-K- target rows. C7's rate "
        "step remains 1/120 = 0.008333, below the 0.05 margin, so C7 stays resolved. "
        "C8's step is 1/8 = 0.125, above 0.05, so C8 remains under-resolved and needs "
        "at least 20 rows (N>=20) for one-step resolution. C1 target-only at 8 "
        "rows is also still flagged (7/8 = 0.875); expanded C1 at 63–64 rows and "
        "C4 at 55–56 rows remain resolved. This is a planned-denominator statement, "
        "not a C7/C8 measurement.",
        "",
        "## Flags",
        "",
    ]
    if doc["summary"]["flagged"]:
        lines += ["- `%s`" % item for item in doc["summary"]["flagged"]]
    else:
        lines.append("- none")
    lines += [
        "",
        "`C1` is listed for both target-only and expanded-denominator cases. The 4-row "
        "and 8-row target-only cases are flagged; the expanded 63–64 row cases pass the "
        "resolution test, but the observed baseline-available count is still unknown.",
        "",
        "## Post-run update",
        "",
        "When A1 cell parts exist, `python -m benchmarks.a1_denominator_audit --parts [DIR]` "
        "recomputes the numeric denominators from those parts and writes a separate "
        "`A1-DENOMINATOR-RESOLUTION-OBSERVED.md` and JSON record. It uses "
        "the minimum observed denominator per gate, marks missing values **UNMEASURED** "
        "rather than zero, and does not overwrite this planned audit. An empty directory "
        "is **NOT RUN**. The observed record is a denominator statement, not a C7/C8 "
        "verdict or an A1 PASS/FAIL.",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def write() -> int:
    doc = build()
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(doc["status"])
    return 0


def problems(doc: dict | None = None) -> list[str]:
    doc = build() if doc is None else doc
    found: list[str] = []
    unit = doc.get("denominator_unit") or {}
    if unit.get("status") != "ADOPTED — BINDING FOR A1":
        found.append("C7/C8 denominator unit is not the adopted per-seed unit")
    if unit.get("C7_assertion_block") != C7_C8_DENOMINATOR_UNIT:
        found.append("C7 denominator unit is not per seed")
    if unit.get("C8_third_route") != C7_C8_DENOMINATOR_UNIT:
        found.append("C8 denominator unit is not per seed")
    if unit.get("pooled_reading") != "REJECTED — not an A1 denominator for C7 or C8":
        found.append("the pooled C7/C8 reading is not recorded as rejected")
    expected = {
        "C1_path_separation — target-only fallback",
        "C1_path_separation — N=8 maximum-feasibility target-only",
        "C8_third_route — A-K- blocked rows",
        "C8_third_route — N=8 maximum-feasibility A-K- blocked rows",
    }
    flagged = set(doc["summary"]["flagged"])
    if flagged != expected:
        found.append("flagged scenarios changed: %r" % sorted(flagged))
    c1_planned = [row for row in doc["gates"]
                  if row["gate"] == "C1_path_separation"
                  and row["scenario"] == "expanded C4 denominator"]
    if not c1_planned or c1_planned[0]["status"] != "PASS":
        found.append("expanded C1 denominator is not passing the resolution check")
    c4 = [row for row in doc["gates"] if row["gate"] == "C4_no_interference"]
    if not c4 or c4[0]["status"] != "PASS":
        found.append("C4 denominator is not passing the resolution check")
    for row in doc["gates"]:
        if row["status"] == "FLAGGED" and not row["consequence"]:
            found.append("%s has no consequence" % row["gate"])
    return found


def check() -> int:
    if not OUT_PATH.exists() or not PAGE_PATH.exists():
        print("FAIL: the denominator audit artifact or page is missing")
        return 1
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    found = problems(doc)
    if doc != build():
        found.append("denominator audit is stale against its sources")
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("denominator audit page is stale")
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    print("A1 denominator audit: clean; %s" % doc["status"])
    return 0


def self_test() -> list[str]:
    doc = build()
    found = problems(doc)
    if "C4" in " ".join(doc["summary"]["flagged"]):
        found.append("C4 was incorrectly flagged")
    if "expanded C4 denominator" in " ".join(doc["summary"]["flagged"]):
        found.append("the expanded C1 denominator was incorrectly flagged")
    if len(doc["summary"]["not_applicable"]) != 5:
        found.append("structural gates are not classified as not applicable")
    flagged = set(doc["summary"]["flagged"])
    if doc["denominator_unit"]["minimum_targets_for_one_step_resolution"] != {
            "C7": 1, "C8": 20}:
        found.append("the C7/C8 one-step target minima changed")
    if doc["denominator_unit"]["resolved"] != {
            "C7_N4": True, "C7_N8": True, "C8_N4": False,
            "C8_N8": False, "C8_N20": True}:
        found.append("the C7/C8 resolution flags changed")
    scenario = "C8_third_route — N=8 maximum-feasibility A-K- blocked rows"
    if scenario not in flagged:
        found.append("C8 N=8 scenario is not flagged")
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--parts", type=Path, nargs="?", const=DEFAULT_PARTS)
    args = parser.parse_args(argv)
    if args.parts is not None:
        from benchmarks import a1_result
        payloads = a1_result.load_parts(args.parts)
        if not payloads:
            print("A1 observed denominator audit: NOT RUN — no cell parts in %s"
                  % args.parts)
            print("No observed denominator exists until a cell writes a part.")
            return 2
        return write_observed(payloads, args.parts)
    if args.self_test:
        found = self_test()
        for problem in found:
            print("FAIL:", problem)
        if not found:
            print("A1 denominator audit: self-test clean")
        return 1 if found else 0
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
