"""PRESENCE-CAP-LADDER-1: a multi-seed transition-budget ladder.

The block varies only ``SleepService.MAX_PREDICTIONS`` across 40, 56, 80 and
112 on six fresh worlds.  The shipped allocation is half transitions and half
cooccurrences, so those caps correspond to transition floors of 20, 28, 40 and
56.  The primary rung is 80: the smallest cap whose nominal transition floor
reaches rank 40.

The block does not rerun BAND-5's 40-versus-112 endpoints.  It measures the
intermediate rungs and prices the served rows that are not present world
edges, so "the band came back" cannot be reported without its false-admission
cost.

This module writes the frozen record and its generated page.  It runs no cell.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "presence_cap_ladder_prereg.json"
PAGE = ROOT / "docs" / "PRESENCE-CAP-LADDER-PREREGISTRATION.md"
RESULT = ROOT / "docs" / "presence_cap_ladder_run.json"

ID = "PRESENCE-CAP-LADDER-1"
FROZEN_ON = "2026-11-12"
SEEDS = (20614101, 20614102, 20614103, 20614104, 20614105, 20614106)
CAPS = (40, 56, 80, 112)
PRIMARY_CAP = 80
FALSE_ADMISSION_MARGIN = 0.10

VERDICTS = (
    "CONFIRMED",
    "RECOVERY WITH COST",
    "RECOVERY AT 112 ONLY",
    "PARTIAL RECOVERY",
    "NO RECOVERY",
    "VOID",
)


def rungs() -> list[dict]:
    return [
        {"cap": cap, "transition_floor": cap // 2, "cooccurrence_cap": cap // 2}
        for cap in CAPS
    ]


def build() -> dict:
    return {
        "prereg": ID,
        "status": "FROZEN, NOT RUN",
        "frozen_on": FROZEN_ON,
        "no_cells_run": True,
        "question": (
            "On the shipped 0.15.0 build, with six fresh worlds, does a transition "
            "budget of 40 recover the measured rank-21-40 band without a false-admission "
            "rate more than 10 percentage points above the cap-40 baseline, and at which "
            "lower rung does recovery begin?"
        ),
        "program": {
            "draft": "docs/DECISION-ADMISSION-STEP.md",
            "relationship": (
                "BAND-5 established the endpoints on fresh worlds: 0 of 89 measured "
                "rank-21-40 edges entered service at cap 40 and 89 of 89 did at cap 112. "
                "This block is the dose-response between those endpoints. It does not "
                "reuse BAND-5 cells, band identities or verdicts."
            ),
        },
        "reconciliation": {
            "endpoints_known": (
                "BAND-5 measured 0/89 band service at cap 40 and 89/89 at cap 112 on "
                "seeds 20612601-20612606. Those endpoints are prior evidence, not cells "
                "of this block."
            ),
            "gap": (
                "Caps 56 and 80 are the untested rungs. Cap 80 is the smallest rung "
                "whose nominal 40-transition floor reaches rank 40; cap 56 reaches only "
                "rank 28."
            ),
            "allocation": (
                "The shipped split gives half the cap to entropy-ranked transitions and "
                "half to count-ranked cooccurrences. The engine may backfill unused "
                "cooccurrence seats with further transitions, so actual transition "
                "counts are recorded per window rather than assumed."
            ),
            "false_admission": (
                "A higher cap can recover the band by serving more rows. The block "
                "therefore charges every served row that is not a present world edge, "
                "not only rows outside the named band."
            ),
        },
        "design": {
            "arms": ["cap 40", "cap 56", "cap 80", "cap 112"],
            "caps": list(CAPS),
            "rungs": rungs(),
            "primary_cap": PRIMARY_CAP,
            "shipped_cap": 112,
            "seeds": list(SEEDS),
            "seed_clusters": 6,
            "cycles": 120,
            "cells": 24,
            "cells_arithmetic": "4 caps x 6 seeds = 24 cells; one fresh-process determinism rerun at cap 80",
            "variable": "SleepService.MAX_PREDICTIONS, set per cell",
            "observer": "the repaired observer of PRESENCE-CONVERSION-2",
            "world": "the PHASE_ACQUISITION compositional world at 120 cycles",
            "pairing": "each seed's world and stimulus are identical at all four caps",
            "freshness": "Six fresh seeds; seed_collisions is empty at freeze time.",
            "reuse": "No prior block's cells, named band or verdict is reused; BAND-5 is cited only as prior evidence.",
        },
        "band": {
            "definition": (
                "For each seed, every present transition at minimum cap-112 block rank "
                "21-40; measured from the 112 universe and not filtered by service at "
                "any lower cap."
            ),
            "identity": (
                "Each band edge is named by source>target and carries its minimum "
                "cap-112 rank; a missing rank is a ledger failure, not a zero."
            ),
            "expected_size": (
                "Measured per seed; BAND-5 observed 11-19 edges per seed, and no fixed "
                "band size is assumed."
            ),
            "zero_band": "A zero band is a zero denominator and makes the block VOID.",
        },
        "false_admission": {
            "definition": (
                "A served row whose source>target edge is not in the seed's present "
                "world transitions, where present = world edges intersected with the "
                "temporal rows retained at the end of the cell."
            ),
            "numerator": "served rows that are not present world transitions, summed over all cycles and windows",
            "denominator": "all served rows, summed over all cycles and windows",
            "unit": "computed per seed and pooled by summing rows, never by averaging per-cycle ratios",
            "baseline_cap": 40,
            "margin": FALSE_ADMISSION_MARGIN,
            "comparison": (
                "Paired cap-80 minus cap-40 false-admission rate for each seed; the "
                "upper bound of a 10,000-resample seed-cluster bootstrap must be at or "
                "below +0.10."
            ),
            "why_10pp": (
                "The margin is pre-set, not fitted. The earlier cap-40 ladder recorded "
                "a world-row share of 0.239-0.278, so the non-world baseline is roughly "
                "0.72-0.76; +10 pp bounds the worsening to about one-eighth of that "
                "baseline rather than permitting a free precision collapse."
            ),
            "not_the_same_as": (
                "A served world edge outside rank 21-40 is collateral service, not a "
                "false admission; it is reported separately."
            ),
        },
        "engine": {"version": "0.15.0", "cap": 112, "edit": "none"},
        "gates": {
            "L1_build": "one shipped 0.15.0 build across all cells; only MAX_PREDICTIONS differs",
            "L2_world": "each seed has the same world digest and present fingerprint at all four caps",
            "L3_band_identity": "each band edge is a present transition at rank 21-40 with a recorded rank and source>target identity",
            "L4_control_40": "cap 40 serves no band edge and its full 40-row windows satisfy the 20-transition floor and the 20-cooccurrence cap",
            "L5_allocation_law": "every full window has transitions + cooccurrences = cap, transitions >= cap//2, cooccurrences <= cap//2, with actual counts and relations recorded",
            "L6_denominator": "every seed has a non-empty band, at least one served row, and every band edge reaches the ledger",
            "L7_determinism": "a fresh-process rerun of seed 20614101 at cap 80 reproduces its windows and ledger",
            "L8_seed_axis": "at least three distinct served-band sets across the six seeds",
            "L9_false_ledger": "every served row is classified present or not-present, and no served row is unparsed or missing a rank where a transition rank is required",
        },
        "endpoints": {
            "kind": "co-primary, independently falsifiable",
            "primary_band_recovery": {
                "cap": PRIMARY_CAP,
                "metric": "measured band edges served at least once / measured band edges",
                "bar": 0.90,
                "pooled": "pooled numerator and denominator across the six seeds",
                "per_seed": "reported; no seed is dropped",
                "prediction": "0.85-1.00, with schema cycles the likely shortfall",
            },
            "co_primary_false_admission": {
                "cap": PRIMARY_CAP,
                "metric": "paired cap-80 minus cap-40 false-admission rate",
                "non_inferiority_margin": FALSE_ADMISSION_MARGIN,
                "decision_rule": "upper 95% seed-cluster-bootstrap bound <= +0.10",
                "per_seed": "reported with numerator and denominator",
            },
            "ceiling": {
                "cap": 112,
                "metric": "measured band edges served at least once / measured band edges",
                "bar": 0.95,
                "role": "ceiling control, not the primary rung",
                "false_admission": {
                    "metric": "paired cap-112 minus cap-40 false-admission rate",
                    "margin": FALSE_ADMISSION_MARGIN,
                    "decision_rule": "upper 95% seed-cluster-bootstrap bound <= +0.10",
                },
            },
            "secondary": [
                "cap-56 band recovery",
                "cap-80 and cap-112 actual transition and cooccurrence counts",
                "served world edges outside the band (collateral service)",
                "monotonicity of band recovery across the four caps",
            ],
        },
        "predictions": [
            {
                "id": "P1",
                "cap": 40,
                "prediction": "0.00 band recovery; the cap-40 control serves no rank-21-40 edge.",
            },
            {
                "id": "P2",
                "cap": 56,
                "prediction": "0.30-0.60 band recovery, because only ranks 21-28 are nominally reached.",
            },
            {
                "id": "P3",
                "cap": 80,
                "prediction": "0.85-1.00 band recovery; schema rows can push a few rank-40 edges past the 40-transition floor.",
            },
            {
                "id": "P4",
                "cap": 112,
                "prediction": "0.95-1.00 band recovery; BAND-5 observed 89/89 at this cap.",
            },
            {
                "id": "P5",
                "cap": "all",
                "prediction": "false-admission rate rises weakly with cap; the cap-80 paired upper bound stays at or below +0.10.",
            },
            {
                "id": "P6",
                "cap": "all",
                "prediction": "band recovery is nondecreasing across 40, 56, 80 and 112.",
            },
        ],
        "analysis": {
            "primary": (
                "Pooled and per-seed band recovery at cap 80; exact McNemar on the "
                "paired band-edge service indicator against cap 40, where the cap-40 "
                "control should leave every band edge unserved."
            ),
            "false_admission": (
                "Per-seed false-admission rates with numerators and denominators; "
                "paired cap-80 minus cap-40 difference, plus the cap-112 minus cap-40 "
                "difference used by the ceiling branch; 10,000-resample seed-cluster "
                "bootstrap for each upper 95% bound. The seed is the resampling unit."
            ),
            "dose": (
                "Report cap 56 and cap 112 recovery and the four-rung sequence. A "
                "monotonicity failure is reported as a failure, not smoothed."
            ),
            "multiplicity": (
                "The cap-80 band and false-admission endpoints are co-primary; all "
                "other rungs and outcomes are secondary and labelled so."
            ),
            "missing_data": "No seed, cap or cycle is dropped; a missing cell makes the block VOID.",
            "no_fitting": "The band definition, primary rung, margin and bars are frozen before any cell.",
        },
        "decision_table": [
            {
                "condition": "L1-L4, L6 or L9 fails; a band is empty; or a required ledger row is missing",
                "verdict": "VOID",
                "reading": "the block did not produce a readable band, a valid control or a complete false-admission ledger",
                "decision": "record VOID; fix the failed gate and register a new block; read no recovery",
            },
            {
                "condition": "L5, L7 or L8 fails",
                "verdict": "VOID",
                "reading": "the allocation, determinism or seed-axis gate did not hold",
                "decision": "record VOID; do not interpret a band rate from an unreadable ladder",
            },
            {
                "condition": "gates pass and cap-112 band recovery is below 0.50",
                "verdict": "NO RECOVERY",
                "reading": "even the ceiling control does not recover the band on these worlds",
                "decision": "the cap or transition budget is not the gate; next test candidate formation or the rank itself",
            },
            {
                "condition": "gates pass and cap-112 band recovery is 0.50-0.90",
                "verdict": "PARTIAL RECOVERY",
                "reading": "the budget helps but does not recover the measured band uniformly",
                "decision": "report the per-edge misses; do not adopt a cap; next test the residual rank or allocation rule",
            },
            {
                "condition": "gates pass; cap-80 recovery is below 0.90; cap-112 recovery is at least 0.90 and its false-admission upper bound is at most +0.10",
                "verdict": "RECOVERY AT 112 ONLY",
                "reading": "80 is insufficient, while the shipped 112 budget recovers the band at acceptable false-admission cost",
                "decision": "record the threshold; the owner may consider 112 as the operating rung, with the measured cost",
            },
            {
                "condition": "gates pass; cap-80 recovery is at least 0.90; false-admission upper bound is above +0.10",
                "verdict": "RECOVERY WITH COST",
                "reading": "the band returns at 80, but the window pays more than the pre-set false-admission margin",
                "decision": "do not adopt 80 on band recovery alone; report the trade-off and test a precision-preserving admission rule",
            },
            {
                "condition": "gates pass; cap-80 recovery is at least 0.90; false-admission upper bound is at most +0.10; cap-112 recovery is at least 0.95",
                "verdict": "CONFIRMED",
                "reading": "the 80 rung recovers the measured 21-40 band without excessive false admissions, and 112 remains the ceiling control",
                "decision": "record the confirmation; the owner decides any engine or operating change; no capability claim",
            },
        ],
        "authorisation": {
            "required": True,
            "granted": False,
            "granted_on": None,
            "document": None,
            "quote": None,
            "note": (
                "No grant is recorded and no authorisation request is made by this "
                "record. The runner and every cell refuse while granted is false."
            ),
        },
        "runner": {
            "built": True,
            "planned_module": "benchmarks.presence_cap_ladder_arm",
            "cells_run": 0,
            "why": (
                "The cell runner is built behind the grant check. It opens no "
                "database and runs no cell while granted is false."
            ),
        },
        "cost": {
            "cells": 24,
            "witness_cells": "one determinism rerun at cap 80",
            "cycles": 120,
            "runtime": "not claimed; no cell has run",
        },
        "not_evidence": (
            "A preregistration, not a result. It measures band service and false "
            "admissions on one synthetic world family. It does not establish "
            "capability, retention, transfer, or a general operating cap."
        ),
        "amendments": [],
    }


def render(doc: dict) -> str:
    lines = [
        "# PRESENCE-CAP-LADDER-1 — multi-seed transition-budget ladder",
        "",
        "**Status.** %s. Generated from `%s`; never edited by hand."
        % (doc["status"], RECORD.relative_to(ROOT).as_posix()),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Preregistration | `%s` |" % doc["prereg"],
        "| Freeze date | %s |" % doc["frozen_on"],
        "| Seeds | %s |" % ", ".join(str(seed) for seed in doc["design"]["seeds"]),
        "| Caps | 40, 56, 80, 112 |",
        "| Primary rung | %d |" % doc["design"]["primary_cap"],
        "| Cells | %d |" % doc["design"]["cells"],
        "| Cycles | %d |" % doc["design"]["cycles"],
        "| Grant | %s |" % ("granted" if (doc.get("authorisation") or {}).get("granted")
                           else "not granted"),
        "| Runner | %s |" % ("built" if doc["runner"]["built"] else "not built"),
        "| Cells run | %d |" % doc["runner"]["cells_run"],
        "",
        "## Question",
        "",
        doc["question"],
        "",
        "## What is already known",
        "",
        doc["reconciliation"]["endpoints_known"],
        "",
        doc["reconciliation"]["gap"],
        "",
        doc["reconciliation"]["allocation"],
        "",
        doc["reconciliation"]["false_admission"],
        "",
        "## Design",
        "",
        "| Cap | Transition floor | Cooccurrence cap |",
        "| ---: | ---: | ---: |",
    ]
    for rung in doc["design"]["rungs"]:
        lines.append("| %d | %d | %d |" % (
            rung["cap"], rung["transition_floor"], rung["cooccurrence_cap"]))
    lines += [
        "",
        "Only `SleepService.MAX_PREDICTIONS` changes. The six seeds share the same "
        "world and stimulus across all four caps. The cap-80 rung is primary because "
        "its nominal 40-transition floor is the first to reach rank 40.",
        "",
        "## Band",
        "",
        doc["band"]["definition"],
        "",
        doc["band"]["identity"],
        "",
        doc["band"]["expected_size"],
        "",
        doc["band"]["zero_band"],
        "",
        "## False admissions",
        "",
        doc["false_admission"]["definition"],
        "",
        "**Rate.** %s, divided by %s; %s."
        % (doc["false_admission"]["numerator"][:1].upper()
           + doc["false_admission"]["numerator"][1:],
           doc["false_admission"]["denominator"], doc["false_admission"]["unit"]),
        "",
        "**Bar.** %s" % doc["false_admission"]["comparison"],
        "",
        "**Why this margin.** %s" % doc["false_admission"]["why_10pp"],
        "",
        "**Not the same as collateral service.** %s" % doc["false_admission"]["not_the_same_as"],
        "",
        "## Endpoints",
        "",
        "| Endpoint | Cap | Rule |",
        "| --- | ---: | --- |",
        "| Band recovery | %d | at least %.2f pooled, per seed reported |"
        % (doc["endpoints"]["primary_band_recovery"]["cap"],
           doc["endpoints"]["primary_band_recovery"]["bar"]),
        "| False admission | %d | paired upper bound at most +%.2f |"
        % (doc["endpoints"]["co_primary_false_admission"]["cap"],
           doc["endpoints"]["co_primary_false_admission"]["non_inferiority_margin"]),
        "| Band ceiling | %d | at least %.2f |"
        % (doc["endpoints"]["ceiling"]["cap"], doc["endpoints"]["ceiling"]["bar"]),
        "| False admission (ceiling) | %d | paired upper bound at most +%.2f |"
        % (doc["endpoints"]["ceiling"]["cap"],
           doc["endpoints"]["ceiling"]["false_admission"]["margin"]),
        "",
        "The two cap-80 endpoints are co-primary: a band recovery cannot rescue an "
        "excessive false-admission rate, and a clean false-admission rate cannot rescue "
        "an unserved band.",
        "",
        "## Predictions",
        "",
        "| ID | Cap | Prediction |",
        "| --- | ---: | --- |",
    ]
    for prediction in doc["predictions"]:
        lines.append("| %s | %s | %s |" % (
            prediction["id"], prediction["cap"], prediction["prediction"]))
    lines += [
        "",
        "## Gates",
        "",
        "| Gate | Rule |",
        "| --- | --- |",
    ]
    for gate, rule in doc["gates"].items():
        lines.append("| `%s` | %s |" % (gate, rule))
    lines += [
        "",
        "## Decision table",
        "",
        "| Condition | Verdict | Reading | Decision |",
        "| --- | --- | --- | --- |",
    ]
    for row in doc["decision_table"]:
        lines.append("| %s | **%s** | %s | %s |" % (
            row["condition"], row["verdict"], row["reading"], row["decision"]))
    lines += [
        "",
        "## Analysis",
        "",
        doc["analysis"]["primary"],
        "",
        doc["analysis"]["false_admission"],
        "",
        doc["analysis"]["dose"],
        "",
        doc["analysis"]["multiplicity"],
        "",
        doc["analysis"]["missing_data"],
        "",
        doc["analysis"]["no_fitting"],
        "",
        "## What this does not license",
        "",
        doc["not_evidence"],
        "",
        "No authorisation is recorded. The runner is built but refuses every cell "
        "while the grant is absent. No cell has run.",
        "",
    ]
    return "\n".join(lines)


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def problems(doc: dict | None = None, page: str | None = None) -> list[str]:
    doc = record() if doc is None else doc
    page = PAGE.read_text(encoding="utf-8") if page is None else page
    found: list[str] = []
    if doc.get("prereg") != ID:
        found.append("prereg id")
    if doc.get("status") != "FROZEN, NOT RUN":
        found.append("status")
    if doc.get("frozen_on") != FROZEN_ON:
        found.append("freeze date")
    if doc.get("no_cells_run") is not True:
        found.append("no_cells_run")
    if (doc.get("authorisation") or {}).get("granted") is not False:
        found.append("grant must be false")
    if (doc.get("runner") or {}).get("cells_run") != 0:
        found.append("runner cells")
    if (doc.get("runner") or {}).get("built") is not True:
        found.append("runner built")
    if (doc.get("runner") or {}).get("planned_module") != "benchmarks.presence_cap_ladder_arm":
        found.append("runner module")
    design = doc.get("design") or {}
    if design.get("caps") != list(CAPS):
        found.append("caps")
    if design.get("primary_cap") != PRIMARY_CAP:
        found.append("primary cap")
    if len(design.get("seeds") or []) != 6 or design.get("cells") != 24:
        found.append("design")
    if design.get("cycles") != 120:
        found.append("cycles")
    if len(design.get("rungs") or []) != 4:
        found.append("rungs")
    if (doc.get("false_admission") or {}).get("margin") != FALSE_ADMISSION_MARGIN:
        found.append("false-admission margin")
    if (doc.get("false_admission") or {}).get("baseline_cap") != 40:
        found.append("false-admission baseline")
    verdicts = {row.get("verdict") for row in doc.get("decision_table") or []}
    for verdict in VERDICTS:
        if verdict not in verdicts:
            found.append("decision verdict %s" % verdict)
    if "21-40" not in (doc.get("band") or {}).get("definition", ""):
        found.append("band definition")
    if RESULT.exists():
        found.append("unrun block has a result")
    from benchmarks.presence_cap_experiment import seed_collisions
    collisions = seed_collisions(list(SEEDS), allow=(RECORD, PAGE))
    if collisions:
        found.append("seed collisions: %s" % sorted(collisions))
    if page.strip() != render(doc).strip():
        found.append("page stale")
    return found


def freeze() -> int:
    if RECORD.exists():
        print("REFUSED: record exists")
        return 2
    doc = engine_stamp.stamp(build())
    RECORD.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(doc), encoding="utf-8")
    print("froze %s and %s" % (RECORD.relative_to(ROOT).as_posix(), PAGE.relative_to(ROOT).as_posix()))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.freeze:
        return freeze()
    found = problems()
    for item in found:
        print("FAIL:", item)
    if found:
        return 1
    doc = record()
    print("presence cap ladder: %s, %d cells, grant %s, runner %s, cells run %d" % (
        doc["status"], doc["design"]["cells"], doc["authorisation"]["granted"],
        doc["runner"]["built"], doc["runner"]["cells_run"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
