"""C1-C9 preflight: can the two-path design be admitted with the records in hand?

This is a design audit, not an experimental result. It reads the existing A0,
provenance and carrier-trace artifacts, classifies each identifiability
condition as SATISFIED, REQUIRES INSTRUMENTATION or UNSATISFIABLE, and writes
a reproducible record.

Usage:
    python -m benchmarks.c1_c9_preflight --write
    python -m benchmarks.c1_c9_preflight --check
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

A0_PATH = DOCS / "carrier_formation_a0.json"
PROVENANCE_PATH = DOCS / "assertion_provenance.json"
TRACE_PATH = DOCS / "assertion_carrier_trace.json"
OUT_PATH = DOCS / "c1_c9_preflight.json"
DOC_PATH = DOCS / "C1-C9-PREFLIGHT.md"

DATE = "2026-11-13"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _keys(value: object, prefix: str = "") -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(str(key))
            found |= _keys(child, prefix + str(key) + ".")
    elif isinstance(value, list):
        for child in value:
            found |= _keys(child, prefix)
    return found


def build() -> dict:
    a0 = _load(A0_PATH)
    provenance = _load(PROVENANCE_PATH)
    trace = _load(TRACE_PATH)

    if a0.get("not_a_result") is not True:
        raise SystemExit("REFUSED: A0 is not marked not_a_result")
    if provenance.get("not_a_result") is not True:
        raise SystemExit("REFUSED: provenance is not marked not_a_result")
    if trace.get("not_a_result") is not True:
        raise SystemExit("REFUSED: carrier trace is not marked not_a_result")

    rows = a0["rows"]
    if len(rows) != 26:
        raise SystemExit("REFUSED: expected 26 A0 rows, got %d" % len(rows))

    provenance_rows = {
        (int(row["seed"]), str(row["edge"])): row
        for row in provenance["rows"]
    }
    missing = [
        (int(row["seed"]), str(row["edge"]))
        for row in rows
        if (int(row["seed"]), str(row["edge"])) not in provenance_rows
    ]
    if missing:
        raise SystemExit("REFUSED: A0 rows without provenance: %r" % (missing[:3],))

    carrier_rows = sum(bool(row["formation_cycles"]) for row in rows)
    no_carrier_rows = len(rows) - carrier_rows
    direct_served_zero = sum(
        int(provenance_rows[(int(row["seed"]), str(row["edge"]))][
            "direct_committed_windows"
        ]) == 0
        for row in rows
    )

    if direct_served_zero != len(rows):
        raise SystemExit(
            "REFUSED: the A0 slice is not uniformly never-served; %d/%d have zero direct service"
            % (direct_served_zero, len(rows))
        )

    # The A0 slice is selected on never-served edges. Every row carries a
    # carrier. It therefore contributes only A-K+ rows and cannot show
    # positivity across the four cells.
    cells = {
        "A+K+": 0,
        "A+K-": 0,
        "A-K+": len(rows),
        "A-K-": 0,
    }

    formation_cycles = [
        int(cycle)
        for row in rows
        for cycle in row["formation_cycles"]
    ]
    all_keys = _keys(a0) | _keys(provenance) | _keys(trace)
    assertion_cycle_fields = sorted(
        key for key in all_keys
        if "assertion" in key.lower() and "cycle" in key.lower()
    )
    edge_strength_fields = sorted(
        key for key in all_keys
        if key.lower() == "strength" or key.lower().endswith(".strength")
    )
    u_count_fields = sorted(
        key for key in all_keys
        if key in {"direct_temporal_count", "reverse_temporal_count"}
    )

    stages = {stage["stage"]: stage for stage in a0["stage_map"]}
    candidate = stages["candidate_formation"]
    admission = stages["admission"]

    conditions = [
        {
            "id": "C1_path_separation",
            "status": "REQUIRES INSTRUMENTATION",
            "basis": (
                "A0 supports the parallel-path premise: %d/%d rows form a carrier with zero direct "
                "service; candidate formation is upstream but not independent, and admission leaves "
                "the carrier intact. No A- or K- cross-block was executed, so the two manipulations "
                "have not been shown to leave each other's path intact."
                % (carrier_rows, len(rows))
            ),
            "clears_with": (
                "Implement A- and K-; show A- leaves K intact and K- leaves served availability intact "
                "on every seed within the precommitted tolerance."
            ),
            "evidence": {
                "candidate_formation_independently_manipulable": candidate["independently_manipulable"],
                "admission_independently_manipulable": admission["independently_manipulable"],
                "admission_leaves_carrier_intact": admission["leaves_carrier_intact"],
            },
        },
        {
            "id": "C2_treatment_consistency",
            "status": "REQUIRES INSTRUMENTATION",
            "basis": (
                "No A-, K- or Y- execution exists in the committed artifacts. The A0 and provenance "
                "records are observational joins, not manipulations."
            ),
            "clears_with": (
                "Run each manipulation and verify it drives its named path to zero while leaving the "
                "other path's measured quantity above zero."
            ),
            "evidence": {"intervention_artifacts": 0},
        },
        {
            "id": "C3_positivity",
            "status": "REQUIRES INSTRUMENTATION",
            "basis": (
                "The 26-row A0 slice is selected on never-served direct edges and every row has a "
                "carrier: %d A-K+, 0 A+K+, 0 A+K- and 0 A-K-. The full candidate set has 492 served "
                "edges, but it has not been joined to carrier availability, so no four-cell denominator "
                "exists." % cells["A-K+"]
            ),
            "clears_with": (
                "Join every eligible edge to both factors and require a non-zero denominator in all "
                "four cells and in the Y- arm at A+K+ and A-K+."
            ),
            "evidence": {
                "a0_slice_cells": cells,
                "a0_slice_selected_on": "direct_committed_windows == 0",
                "full_candidate_set_served_ever": a0["summary"]["stage_totals"]["served_ever"],
            },
        },
        {
            "id": "C4_no_interference",
            "status": "REQUIRES INSTRUMENTATION",
            "basis": (
                "No edge-level intervention was run, so there is no neighbour or spillover measurement "
                "to compare against a tolerance."
            ),
            "clears_with": (
                "Run an edge-level manipulation with precommitted neighbour tolerances for A, K and Y; "
                "cluster or redesign if the tolerance is exceeded."
            ),
            "evidence": {"intervention_artifacts": 0},
        },
        {
            "id": "C5_common_cause",
            "status": "REQUIRES INSTRUMENTATION",
            "basis": (
                "Direct and reverse temporal counts are present for all 26 rows (%d-%d direct), and they "
                "are formed before the carrier. The specified U also includes strength, but no edge-level "
                "strength field exists; carrier strength is a different quantity. U has not been joined to "
                "all four cells."
                % (
                    a0["summary"]["direct_temporal_min"],
                    a0["summary"]["direct_temporal_max"],
                )
            ),
            "clears_with": (
                "Record direct count, reverse count and edge strength before the outcome for every "
                "eligible edge, and join U to all cells without using a post-outcome rank."
            ),
            "evidence": {
                "u_count_fields": u_count_fields,
                "edge_strength_fields": edge_strength_fields,
                "a0_rows_with_u_counts": len(rows),
            },
        },
        {
            "id": "C6_temporal_resolution",
            "status": "REQUIRES INSTRUMENTATION",
            "basis": (
                "Carrier formation cycles are present (%d-%d, median %.1f), but no artifact records an "
                "assertion cycle. K and Y therefore cannot be ordered at the same cycle resolution."
                % (
                    min(formation_cycles),
                    max(formation_cycles),
                    float(a0["summary"]["formation_cycle_median"]),
                )
            ),
            "clears_with": (
                "Record the assertion cycle per edge at the same resolution as formation, then test "
                "K-before-Y against Y-before-K without reverse-time imputation."
            ),
            "evidence": {
                "carrier_formation_cycle_min": min(formation_cycles),
                "carrier_formation_cycle_max": max(formation_cycles),
                "assertion_cycle_fields": assertion_cycle_fields,
            },
        },
        {
            "id": "C7_assertion_block",
            "status": "REQUIRES INSTRUMENTATION",
            "basis": (
                "No assertion blockade exists. The Y- arm is a design specification, not an implemented "
                "manipulation, so its independence from A and K has not been measured."
            ),
            "clears_with": (
                "Implement Y- and show it reduces assertion without changing A or K formation beyond "
                "the precommitted tolerance."
            ),
            "evidence": {"intervention_artifacts": 0},
        },
        {
            "id": "C8_third_route",
            "status": "REQUIRES INSTRUMENTATION",
            "basis": (
                "No A-K- double block exists and no precommitted ceiling has been fixed. The positive "
                "control is specified but not executable."
            ),
            "clears_with": (
                "Fix the A-K- ceiling before the run, execute the double block, and distinguish no route "
                "from a third route."
            ),
            "evidence": {"intervention_artifacts": 0},
        },
        {
            "id": "C9_same_object",
            "status": "REQUIRES INSTRUMENTATION",
            "basis": (
                "No four-cell runner exists. A0 fixes six committed seeds, one world family, 120 cycles "
                "and cap 40, but it does not pair the four cells or the Y- arm."
            ),
            "clears_with": (
                "Build a runner that fixes world, seed, cycles, cap, candidate universe and U across all "
                "cells; refuse any cell whose object differs."
            ),
            "evidence": {
                "a0_seeds": 6,
                "a0_cycles": 120,
                "a0_cap": 40,
                "paired_cells": 0,
            },
        },
    ]

    counts = {
        "satisfied": sum(c["status"] == "SATISFIED" for c in conditions),
        "requires_instrumentation": sum(
            c["status"] == "REQUIRES INSTRUMENTATION" for c in conditions
        ),
        "unsatisfiable": sum(c["status"] == "UNSATISFIABLE" for c in conditions),
    }
    if counts["satisfied"] or counts["unsatisfiable"]:
        raise SystemExit("REFUSED: unexpected preflight classification: %r" % (counts,))

    return {
        "kind": "c1_c9_preflight",
        "not_a_result": True,
        "historical_snapshot": True,
        "snapshot_status": "HISTORICAL PREFLIGHT SNAPSHOT — not current admissibility status",
        "snapshot_scope": (
            "The C1-C9 classification and verdict below are the 2026-11-13 preflight record. "
            "They are retained, not re-scored."
        ),
        "later_update": {
            "date": "2026-11-13",
            "c6": "C6-TIMING-1 satisfies C6_temporal_resolution on six fresh seeds.",
            "remaining": "C1-C5 and C7-C9 remain uncleared; the design remains not admissible.",
            "record": "docs/C6-TIMING-BLOCK.md",
        },
        "date": DATE,
        "question": (
            "Can the registered two-path design be admitted with the records in hand?"
        ),
        "definition": (
            "A read-only audit of C1-C9 against the A0, provenance and carrier-trace artifacts. "
            "It runs no cell and chooses no intervention."
        ),
        "sources": {
            "a0": "docs/carrier_formation_a0.json",
            "provenance": "docs/assertion_provenance.json",
            "carrier_trace": "docs/assertion_carrier_trace.json",
        },
        "verdict": (
            "NOT ADMISSIBLE — 0 SATISFIED, 9 REQUIRING INSTRUMENTATION, 0 UNSATISFIABLE"
        ),
        "reading": (
            "No condition is impossible. None is cleared. The design is blocked by missing "
            "instrumentation, not by a demonstrated impossibility."
        ),
        "counts": counts,
        "conditions": conditions,
        "evidence": {
            "a0_rows": len(rows),
            "a0_carrier_rows": carrier_rows,
            "a0_no_carrier_rows": no_carrier_rows,
            "a0_direct_served_zero": direct_served_zero,
            "a0_slice_cells": cells,
            "formation_cycle_min": min(formation_cycles),
            "formation_cycle_max": max(formation_cycles),
            "formation_cycle_median": a0["summary"]["formation_cycle_median"],
            "assertion_cycle_fields": assertion_cycle_fields,
            "edge_strength_fields": edge_strength_fields,
        },
        "not_evidence": (
            "A design audit on six committed Q4 seeds, one world family, one build and one cap. "
            "It establishes no mechanism and runs no intervention."
        ),
    }


def render(payload: dict) -> str:
    conditions = payload["conditions"]
    lines = [
        "# C1–C9 preflight admissibility audit",
        "",
        "**Date:** %s  " % payload["date"],
        "**Status at preflight:** `%s`" % payload["verdict"],
        "",
        "**This is not an experimental result.** No cell, seed, intervention or engine change was made.",
        "",
        "**Update 2026-11-13:** the `C6_temporal_resolution` row is a preflight snapshot. The separate",
        "`C6-TIMING-1` block has since satisfied C6 on six fresh seeds; `C1`–`C5` and `C7`–`C9` remain",
        "uncleared. The table below is retained as the preflight record, not as a current 0/9 count. See",
        "[`C6-TIMING-BLOCK.md`](C6-TIMING-BLOCK.md).",
        "",
        "## Question",
        "",
        payload["question"],
        "",
        "The audit reads the committed A0, provenance and carrier-trace records and asks whether the",
        "registered two-path design is admissible **now**. It does not ask whether the design is",
        "scientifically worthwhile.",
        "",
        "## Verdict",
        "",
        "| Classification | Count |",
        "| --- | ---: |",
        "| Satisfied | %d |" % payload["counts"]["satisfied"],
        "| Requiring instrumentation | %d |" % payload["counts"]["requires_instrumentation"],
        "| Unsatisfiable | %d |" % payload["counts"]["unsatisfiable"],
        "",
        "At preflight, no condition was impossible and none was cleared. The design was blocked by missing",
        "instrumentation, not by a demonstrated impossibility. C6 has since been cleared; the remaining",
        "eight conditions still block admissibility.",
        "",
        "## Evidence in hand",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        "| A0 rows | %d |" % payload["evidence"]["a0_rows"],
        "| Rows with a carrier | %d |" % payload["evidence"]["a0_carrier_rows"],
        "| Rows without a carrier | %d |" % payload["evidence"]["a0_no_carrier_rows"],
        "| Rows with zero direct service | %d |" % payload["evidence"]["a0_direct_served_zero"],
        "| A0 slice `A+K+` / `A+K−` / `A−K+` / `A−K−` | %d / %d / %d / %d |"
        % (
            payload["evidence"]["a0_slice_cells"]["A+K+"],
            payload["evidence"]["a0_slice_cells"]["A+K-"],
            payload["evidence"]["a0_slice_cells"]["A-K+"],
            payload["evidence"]["a0_slice_cells"]["A-K-"],
        ),
        "| Formation cycles | %d–%d, median %.1f |"
        % (
            payload["evidence"]["formation_cycle_min"],
            payload["evidence"]["formation_cycle_max"],
            payload["evidence"]["formation_cycle_median"],
        ),
        "| Assertion-cycle fields | %s |"
        % (", ".join(payload["evidence"]["assertion_cycle_fields"]) or "**none**"),
        "",
        "The A0 slice is selected on never-served direct edges. Every row has a carrier. It therefore",
        "contributes only `A−K+` rows and cannot establish positivity across the matrix.",
        "",
        "## Conditions",
        "",
        "| ID | Status | Why | What would clear it |",
        "| --- | --- | --- | --- |",
    ]
    for condition in conditions:
        lines.append(
            "| `%s` | `%s` | %s | %s |"
            % (
                condition["id"],
                condition["status"],
                condition["basis"].replace("|", "\\|"),
                condition["clears_with"].replace("|", "\\|"),
            )
        )

    lines += [
        "",
        "## What the audit does not say",
        "",
        "It does not say the design is impossible. All nine conditions are potentially satisfiable.",
        "It says none is cleared, and that the missing pieces are instrumentation rather than a",
        "scientific refutation.",
        "",
        "**Not evidence:** %s" % payload["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.c1_c9_preflight --check",
        "```",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="write the JSON and Markdown records")
    group.add_argument("--check", action="store_true", help="fail if the records are stale")
    args = parser.parse_args(argv)

    payload = build()
    document = render(payload)

    if args.check:
        if not OUT_PATH.exists() or not DOC_PATH.exists():
            print("FAIL: preflight records are missing")
            return 1
        existing = _load(OUT_PATH)
        if existing != payload:
            print("FAIL: %s is stale" % OUT_PATH)
            return 1
        if DOC_PATH.read_text(encoding="utf-8") != document:
            print("FAIL: %s is stale" % DOC_PATH)
            return 1
        print("C1-C9 preflight: clean")
        return 0

    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    DOC_PATH.write_text(document, encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, DOC_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
