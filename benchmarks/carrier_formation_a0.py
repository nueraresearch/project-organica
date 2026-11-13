"""A0: can a single upstream selection stage be named for the carrier design?

Read-only. This joins four committed records:

- docs/assertion_carrier_trace.json          (when each carrier formed)
- docs/assertion_provenance.json             (rank and assertion source)
- docs/presence_unexplained_edges.json       (the 26 never-served asserted edges)
- docs/presence_conversion_repair_run.json   (the Q4 stage table)

It runs no cell, assigns no seed and changes no engine file.  The output is a
read of the existing records, not a new measurement.

    python -m benchmarks.carrier_formation_a0 --write
    python -m benchmarks.carrier_formation_a0 --check
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARTIFACT = DOCS / "carrier_formation_a0.json"
PAGE = DOCS / "CARRIER-FORMATION-A0.md"

SOURCES = {
    "carrier": "docs/assertion_carrier_trace.json",
    "provenance": "docs/assertion_provenance.json",
    "unexplained": "docs/presence_unexplained_edges.json",
    "stage": "docs/presence_conversion_repair_run.json",
}


def _load(name: str) -> dict:
    return json.loads((ROOT / SOURCES[name]).read_text(encoding="utf-8"))


def _stage_totals(stage_rows: list[dict]) -> dict:
    keys = (
        "present",
        "constructed",
        "below_minimum",
        "served_ever",
        "never_served",
        "never_served_within_transition_budget",
        "asserted_final",
        "unexplained",
    )
    return {key: sum(int(row.get(key, 0)) for row in stage_rows) for key in keys}


def build() -> dict:
    trace = _load("carrier")
    provenance = _load("provenance")
    unexplained = _load("unexplained")
    stage = _load("stage")

    trace_rows = {(row["seed"], row["edge"]): row for row in trace["rows"]}
    provenance_rows = {(row["seed"], row["edge"]): row for row in provenance["rows"]}
    unexplained_rows = {
        (seed["seed"], edge["edge"]): edge
        for seed in unexplained["seeds"]
        for edge in seed["edges"]
    }

    if not (set(trace_rows) == set(provenance_rows) == set(unexplained_rows)):
        raise SystemExit("REFUSED: the 26-edge sets do not agree across the records")

    rows = []
    for key in sorted(trace_rows):
        carrier = trace_rows[key]
        prov = provenance_rows[key]
        lost = unexplained_rows[key]
        formations = [int(cycle) for cycle in carrier["formation_cycles"]]
        if not formations:
            raise SystemExit("REFUSED: carrier row has no formation cycle: %r" % (key,))
        first = min(formations)
        best = int(prov["best_cycle"])
        rows.append(
            {
                "seed": key[0],
                "edge": key[1],
                "category": carrier["category"],
                "direct_temporal_count": carrier["direct_temporal_count"],
                "reverse_temporal_count": carrier["reverse_temporal_count"],
                "rank": prov["rank"],
                "best_cycle": best,
                "in_cap": prov["in_cap"],
                "band": prov["band"],
                "served_transitions_in_best_cycle": prov["served_transitions_in_best_cycle"],
                "within_served_transition_budget": int(prov["rank"])
                <= int(prov["served_transitions_in_best_cycle"]),
                "formation_cycles": formations,
                "first_formation_cycle": first,
                "last_formation_cycle": max(formations),
                "carrier_before_best_rank": first <= best,
                "assertion_sources": prov.get("assertion_sources") or [],
                "prediction_source": bool(prov.get("prediction_source")),
            }
        )

    stage_totals = _stage_totals(stage["stage_table"])
    before = sum(row["carrier_before_best_rank"] for row in rows)
    after = len(rows) - before
    categories = dict(sorted(Counter(row["category"] for row in rows).items()))
    in_cap = sum(bool(row["in_cap"]) for row in rows)
    within_transition_budget = sum(
        row["within_served_transition_budget"] for row in rows
    )
    prediction_sources = sum(row["prediction_source"] for row in rows)

    summary = {
        "edges": len(rows),
        "loop_carrier_rows": sum(
            1 for row in trace_rows.values() if row.get("loop_carriers")
        ),
        "categories": categories,
        "formation_cycle_min": min(row["first_formation_cycle"] for row in rows),
        "formation_cycle_max": max(row["last_formation_cycle"] for row in rows),
        "formation_cycle_median": statistics.median(
            row["first_formation_cycle"] for row in rows
        ),
        "direct_temporal_min": min(row["direct_temporal_count"] for row in rows),
        "direct_temporal_max": max(row["direct_temporal_count"] for row in rows),
        "in_cap": in_cap,
        "within_served_transition_budget": within_transition_budget,
        "prediction_sources": prediction_sources,
        "carrier_before_best_rank": before,
        "carrier_after_best_rank": after,
        "stage_totals": stage_totals,
    }

    stage_map = [
        {
            "stage": "candidate_formation",
            "observable": True,
            "observable_evidence": "carrier formation cycles %d-%d; %d loop carriers"
            % (
                summary["formation_cycle_min"],
                summary["formation_cycle_max"],
                trace["summary"]["loop_carriers"],
            ),
            "independently_manipulable": True,
            "leaves_carrier_intact": False,
            "upstream_of_carrier": True,
            "eligible_as_s": False,
            "why": "it creates C; manipulation changes C, so it is upstream but not independent",
        },
        {
            "stage": "admission",
            "observable": True,
            "observable_evidence": "%d present edges never served; %d asserted edges never served; %d of the 26 inside the served transition budget"
            % (
                stage_totals["never_served"],
                stage_totals["unexplained"],
                within_transition_budget,
            ),
            "independently_manipulable": True,
            "leaves_carrier_intact": True,
            "upstream_of_carrier": False,
            "eligible_as_s": False,
            "why": "served-window allocation can be varied and the carrier forms without it, but it is parallel to the carrier path, not upstream of it",
        },
        {
            "stage": "service",
            "observable": True,
            "observable_evidence": "the served window is the engine's own cap-40 list in all 720 cycles; the 26 never enter it",
            "independently_manipulable": False,
            "leaves_carrier_intact": True,
            "upstream_of_carrier": False,
            "eligible_as_s": False,
            "why": "the current records do not separate service from admission; both are the served-window path",
        },
        {
            "stage": "assertion",
            "observable": True,
            "observable_evidence": "%d asserted world edges, including the 26 never-served rows" % stage_totals["asserted_final"],
            "independently_manipulable": True,
            "leaves_carrier_intact": True,
            "upstream_of_carrier": False,
            "eligible_as_s": False,
            "why": "assertion can be blocked by the ordering arm, but it is downstream of both paths; it cannot be the upstream S",
        },
    ]

    return {
        "kind": "carrier_formation_a0",
        "not_a_result": True,
        "date": "2026-11-13",
        "question": "Can a single upstream selection stage be named for the carrier-selection discrimination design?",
        "definition": "A read-only join of the 26 asserted-never-served carrier rows, their provenance ranks, the Q4 stage table and the 26 unexplained edges.",
        "sources": SOURCES,
        "verdict": "NO SINGLE UPSTREAM SELECTION STAGE IDENTIFIED",
        "reading": (
            "Admission is the stage that excludes the direct edge from service; candidate "
            "formation is the stage that creates the loop carrier. The records place them on "
            "parallel paths to assertion, not in one upstream chain. The design's S cannot be "
            "named from the existing records without a new stage-level intervention."
        ),
        "summary": summary,
        "stage_map": stage_map,
        "rows": rows,
        "not_evidence": (
            "An analysis of six committed Q4 seeds in one synthetic world family at one build "
            "and one cap. It runs no cell and establishes no causal, capability, retention or "
            "transfer claim. The absence of a single upstream stage is a limit of this design, "
            "not evidence that no selection process exists."
        ),
    }


def render(doc: dict) -> str:
    s = doc["summary"]
    lines = [
        "# Carrier formation A0 — stage identification",
        "",
        "Generated from `docs/carrier_formation_a0.json` by `python -m benchmarks.carrier_formation_a0 --write`. Do not edit by hand.",
        "",
        "**Status: ANALYSIS, NOT A RUN.** This reads six committed Q4 seeds and the Q4 stage table. It runs no cell, assigns no seed and changes no engine file.",
        "",
        "## Verdict",
        "",
        "**`NO SINGLE UPSTREAM SELECTION STAGE IDENTIFIED`**",
        "",
        doc["reading"],
        "",
        "## What the records show",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        "| Asserted-never-served rows | %d |" % s["edges"],
        "| Loop-carrier rows | %d |" % s["loop_carrier_rows"],
        "| Carrier formation cycles | %d–%d (median first formation %.1f) |"
        % (s["formation_cycle_min"], s["formation_cycle_max"], s["formation_cycle_median"]),
        "| Direct temporal count | %d–%d (prediction floor 5) |"
        % (s["direct_temporal_min"], s["direct_temporal_max"]),
        "| Rows with rank inside cap 40 | %d |" % s["in_cap"],
        "| Rows inside the served transition budget | %d |" % s["within_served_transition_budget"],
        "| Final prediction sources | %d |" % s["prediction_sources"],
        "| Carrier formed at or before the best rank | %d |" % s["carrier_before_best_rank"],
        "| Carrier formed after the best rank | %d |" % s["carrier_after_best_rank"],
        "",
        "The 26 rows have a direct temporal count of 23–47, above the prediction floor of 5, so "
        "the direct edge is not a floor miss. Every row has a loop carrier; one also has a dream "
        "co-carrier. No row has a final prediction source.",
        "",
        "## Q4 stage totals",
        "",
        "| Stage quantity | Count |",
        "| --- | ---: |",
        "| Present | %d |" % s["stage_totals"]["present"],
        "| Constructed | %d |" % s["stage_totals"]["constructed"],
        "| Below prediction minimum | %d |" % s["stage_totals"]["below_minimum"],
        "| Served ever | %d |" % s["stage_totals"]["served_ever"],
        "| Never served | %d |" % s["stage_totals"]["never_served"],
        "| Never served but inside the transition budget | %d |"
        % s["stage_totals"]["never_served_within_transition_budget"],
        "| Asserted at end | %d |" % s["stage_totals"]["asserted_final"],
        "| Asserted but never served | %d |" % s["stage_totals"]["unexplained"],
        "",
        "Construction is not the loss: 671 of 672 present edges became candidates. The direct "
        "edges are present and constructed, but none enters the served transition budget. The "
        "carrier is built from temporal cycles, not from the served window, so the carrier can "
        "exist when admission fails.",
        "",
        "## Stage map",
        "",
        "| Stage | Observable? | Manipulable? | Independent of carrier? | Upstream of carrier? | Eligible as `S`? | Reading |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in doc["stage_map"]:
        lines.append(
            "| `%s` | %s | %s | %s | %s | %s | %s |"
            % (
                row["stage"],
                "yes" if row["observable"] else "no",
                "yes" if row["independently_manipulable"] else "no",
                "yes" if row["leaves_carrier_intact"] else "no",
                "yes" if row["upstream_of_carrier"] else "no",
                "yes" if row["eligible_as_s"] else "no",
                row["why"],
            )
        )
    lines += [
        "",
        "No stage satisfies all four. Candidate formation is upstream but not independent; "
        "admission and service are independent but parallel; assertion is independent but "
        "downstream. The 2×2 design needs an `S` that is upstream of `C` and independently "
        "manipulable, and the existing records do not contain one.",
        "",
        "## Timing",
        "",
        "| Carrier first formation relative to the best-rank cycle | Rows |",
        "| --- | ---: |",
        "| At or before | %d |" % s["carrier_before_best_rank"],
        "| After | %d |" % s["carrier_after_best_rank"],
        "",
        "The mixed order matters. In 17 rows the carrier exists at or before the best recorded "
        "rank; in 9 it appears afterwards. The record therefore does not support a single "
        "temporal ordering in which carrier formation precedes admission for every edge.",
        "",
        "## Per-edge rows",
        "",
        "| Seed | Edge | Category | Rank | In transition budget? | Best cycle | First carrier | Carrier before best? |",
        "| ---: | --- | --- | ---: | --- | ---: | ---: | --- |",
    ]
    for row in doc["rows"]:
        lines.append(
            "| %d | `%s` | %s | %d | %s | %d | %d | %s |"
            % (
                row["seed"],
                row["edge"],
                row["category"].replace("_", " "),
                row["rank"],
                "yes" if row["within_served_transition_budget"] else "no",
                row["best_cycle"],
                row["first_formation_cycle"],
                "yes" if row["carrier_before_best_rank"] else "no",
            )
        )
    lines += [
        "",
        "## What this licenses",
        "",
        "- **A0 does not license A1 as currently designed.** The design needs a single upstream "
        "`S`; the records contain two parallel stages instead.",
        "- **Admission remains the named exclusion stage for the direct edge.** Q4 places the loss "
        "there, not at construction.",
        "- **Candidate formation remains the carrier stage.** The loop builder creates the carrier "
        "from temporal cycles; the served window is not its input.",
        "- **A revised design must be a two-path design or must name a new stage-level lever.** "
        "A carrier-only manipulation cannot separate common cause from readout, and an admission "
        "manipulation does not move the carrier path.",
        "- **No causal, capability, retention or transfer claim follows.** This is a stage-"
        "identification result on one world family, one build and 120 cycles.",
        "",
        "## What would change the verdict",
        "",
        "A stage-level intervention that changes carrier availability without changing the "
        "carrier itself, or a design that treats admission and carrier as two parallel paths with "
        "separate interventions. Until one is registered, the 2×2 remains `NOT IDENTIFIED`.",
        "",
        "## What this does not establish",
        "",
        doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    doc = build()
    text = render(doc)
    if args.write:
        ARTIFACT.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        PAGE.write_text(text, encoding="utf-8")
        print("wrote %s and %s" % (ARTIFACT.relative_to(ROOT), PAGE.relative_to(ROOT)))
        return
    current = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if current != doc:
        raise SystemExit("REFUSED: artifact differs from the records; rerun --write")
    if PAGE.read_text(encoding="utf-8") != text:
        raise SystemExit("REFUSED: page differs from the generator; rerun --write")
    print("carrier formation A0: clean")


if __name__ == "__main__":
    main()
