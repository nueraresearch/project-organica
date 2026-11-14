"""Audit whether A1 gate thresholds are finer than their planned denominators.

The smallest nonzero change in a proportion is ``1 / n``.  For a gate with a
floor or ceiling margin, that step is finer than the gate when it is larger
than the margin.  This audit reads only the precommitted thresholds and the
target-selection counts; it opens no engine and runs no cell.

    python -m benchmarks.a1_denominator_audit --write
    python -m benchmarks.a1_denominator_audit --check
    python -m benchmarks.a1_denominator_audit --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SELECTION_PATH = DOCS / "a1_target_selection.json"
THRESHOLDS_PATH = DOCS / "a1_precommitted_thresholds.json"
OUT_PATH = DOCS / "a1_denominator_resolution.json"
PAGE_PATH = DOCS / "A1-DENOMINATOR-RESOLUTION.md"
KIND = "a1_denominator_resolution_audit"
DATE = "2026-11-14"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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

    gates = [
        _row(
            "C1_path_separation", "target-only fallback",
            "A-/K- preservation", c1, "floor", 4, 4,
            "four target rows, no C4 expansion",
            "3/4 = 0.75; one loss fails the 0.95 floor.",
        ),
        _row(
            "C1_path_separation", "expanded C4 denominator",
            "A-/K- preservation", c1, "floor", planned_c1_min, planned_c1_max,
            "four targets plus 59-60 baseline-available non-target rows",
            "The planned denominator clears the one-step resolution test; the observed denominator is still unknown.",
        ),
        _row(
            "C4_no_interference", "all cells", "A/K/Y neighbour delta",
            c4, "ceiling", non_target_min, non_target_max,
            "59-60 non-target edges per seed",
            "The planned row count resolves a 0.05 rate margin; per-edge cycle rates are finer still.",
        ),
        _row(
            "C7_assertion_block", "Y- blocked rows", "A/K delta",
            c7, "ceiling", 8, 8,
            "two Y- cells x four targets",
            "One row changes the blocked rate by 1/8 = 0.125, above the 0.05 margin.",
        ),
        _row(
            "C8_third_route", "A-K- blocked rows", "assertion rate",
            c8, "ceiling", 4, 4,
            "four A-K- target rows",
            "One row changes the assertion rate by 1/4 = 0.25, above the 0.05 ceiling.",
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
            "margin; equality is not finer."
        ),
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
        "## Flags",
        "",
    ]
    if doc["summary"]["flagged"]:
        lines += ["- `%s`" % item for item in doc["summary"]["flagged"]]
    else:
        lines.append("- none")
    lines += [
        "",
        "`C1` is listed twice: the target-only fallback has four rows and is flagged; "
        "the expanded C4 denominator is planned at 63–64 rows and passes the resolution "
        "test, but its observed baseline-available count is still unknown.",
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
    expected = {
        "C1_path_separation — target-only fallback",
        "C7_assertion_block — Y- blocked rows",
        "C8_third_route — A-K- blocked rows",
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
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
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
