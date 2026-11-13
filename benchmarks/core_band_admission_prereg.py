"""CORE-BAND-ADMISSION-1: freeze the six-seed core+band rule before any cell."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "core_band_admission_prereg.json"
PAGE = ROOT / "docs" / "CORE-BAND-ADMISSION-PREREGISTRATION.md"
RESULT = ROOT / "docs" / "core_band_admission.json"
GRANT = ROOT / "docs" / "AUTHORISATION-CORE-BAND-1.md"

ID = "CORE-BAND-ADMISSION-1"
FROZEN_ON = "2026-11-12"
SEEDS = (20617101, 20617102, 20617103, 20617104, 20617105, 20617106)
CAP = 112
CYCLES = 120
ARMS = ("control", "treatment")
MARGIN = 0.10
COVERAGE_BAR = 0.95


def build() -> dict:
    return {
        "prereg": ID,
        "status": "FROZEN, NOT RUN",
        "frozen_on": FROZEN_ON,
        "no_cells_run": True,
        "question": (
            "At the cap-112 ceiling, does an admission rule that guarantees the "
            "rank-1-20 core and the rank-21-40 band recover every core+band edge "
            "without a false-admission rate more than 10 percentage points worse "
            "than the normal cap-112 window?"
        ),
        "design": {
            "seeds": list(SEEDS),
            "arms": list(ARMS),
            "cap": CAP,
            "cycles": CYCLES,
            "cells": 12,
            "pairing": "each seed's world and stimulus are identical in both arms",
            "control": "the shipped cap-112 engine ordering",
            "treatment": (
                "the same cap-112 run, with every top-20 core and rank-21-40 "
                "band transition guaranteed a served seat; a missing tier edge "
                "replaces the lowest-priority non-tier transition, then a "
                "cooccurrence if no transition remains"
            ),
            "tier": (
                "core is transition rank 1-20 in the cycle's full pre-cap "
                "universe; band is rank 21-40 in that same universe"
            ),
            "window": "the engine's served list remains 112 rows; treatment only replaces seats",
        },
        "endpoints": {
            "coverage": {
                "metric": "served tier edges / available tier edges, pooled over cycles and seeds",
                "bar": COVERAGE_BAR,
                "per_seed": "reported",
            },
            "false_admission": {
                "metric": (
                    "served rows whose edge is not a present world transition, "
                    "divided by all served rows; treatment minus control"
                ),
                "margin": MARGIN,
                "unit": (
                    "pooled by summing rows, per seed reported; a 10,000-resample "
                    "seed-cluster bootstrap gives the upper bound"
                ),
            },
            "binding": (
                "a replacement in any treatment cycle; if none occurs and the "
                "window digests match, the rule is non-binding at 112"
            ),
        },
        "gates": {
            "C1_build": "one 0.15.0 build and cap 112 across all cells",
            "C2_world": "each seed has the same world digest in both arms",
            "C3_tier": "each cycle has 40 tier edges when the pre-cap universe has at least 40 transitions",
            "C4_length": "every served window has 112 rows",
            "C5_ledger": "every tier edge is accounted for as served or missing",
            "C6_control": "control is the unmodified repaired observer",
            "C7_treatment": "treatment differs only by the tier guarantee",
        },
        "decision_table": [
            {"condition": "a gate fails or a window is short",
             "verdict": "VOID", "reading": "the block did not produce a readable window",
             "decision": "fix the ledger; do not read coverage"},
            {"condition": "gates pass, no replacement, all window digests equal",
             "verdict": "NON-BINDING AT 112",
             "reading": "the normal cap-112 window already serves every core+band edge",
             "decision": "do not add a separate admission rule at this ceiling"},
            {"condition": "gates pass, replacements occur, coverage >= 0.95 and false-admission difference <= +0.10",
             "verdict": "BINDING, ACCEPTABLE",
             "reading": "the guarantee changes the window and preserves the cost bar",
             "decision": "consider the rule only with its measured cost"},
            {"condition": "gates pass, replacements occur, coverage < 0.95",
             "verdict": "RULE FAILS COVERAGE",
             "reading": "the guarantee did not recover the tier",
             "decision": "do not adopt; inspect the missing ledger"},
            {"condition": "gates pass, replacements occur, false-admission difference > +0.10",
             "verdict": "RULE PAYS COST",
             "reading": "the guarantee recovers the tier by serving more non-world rows",
             "decision": "do not adopt on coverage alone; report the trade"},
        ],
        "authorisation": {
            "required": True,
            "granted": True,
            "granted_on": FROZEN_ON,
            "document": GRANT.relative_to(ROOT).as_posix(),
            "quote": "Preregister and run the core+band admission rule on a fresh six-seed block with a cap-112 ceiling.",
            "note": "The owner's instruction is the grant for these twelve cells.",
        },
        "runner": {
            "built": True,
            "planned_module": "benchmarks.core_band_admission",
            "cells_run": 0,
        },
        "not_evidence": (
            "A twelve-cell test of one admission guarantee on one synthetic world "
            "family. It does not establish capability, retention, transfer or a "
            "general operating cap."
        ),
        "amendments": [],
    }


def render(doc: dict) -> str:
    d = doc["design"]
    lines = [
        "# CORE-BAND-ADMISSION-1 — core+band at the cap-112 ceiling",
        "",
        "Generated from `%s`; never edited by hand." % RECORD.relative_to(ROOT).as_posix(),
        "",
        "**Status.** %s. **Grant.** %s." % (
            doc["status"], "granted" if doc["authorisation"]["granted"] else "not granted"),
        "",
        "## Question",
        "",
        doc["question"],
        "",
        "## Design",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Seeds | %s |" % ", ".join(str(seed) for seed in d["seeds"]),
        "| Arms | control, treatment |",
        "| Cap | %d |" % d["cap"],
        "| Cycles per cell | %d |" % d["cycles"],
        "| Cells | %d |" % d["cells"],
        "| Core | transition ranks 1-20 |",
        "| Band | transition ranks 21-40 |",
        "",
        "**Control.** %s." % d["control"],
        "",
        "**Treatment.** %s." % d["treatment"],
        "",
        "**Window.** %s." % d["window"],
        "",
        "## Endpoints",
        "",
        "- **Coverage:** %s; bar **%.2f**." % (
            doc["endpoints"]["coverage"]["metric"],
            doc["endpoints"]["coverage"]["bar"]),
        "- **False admission:** %s; margin **+%.2f**." % (
            doc["endpoints"]["false_admission"]["metric"],
            doc["endpoints"]["false_admission"]["margin"]),
        "- **Binding:** %s." % doc["endpoints"]["binding"],
        "",
        "## Gates",
        "",
        "| Gate | Rule |",
        "| --- | --- |",
    ]
    for gate, rule in doc["gates"].items():
        lines.append("| `%s` | %s |" % (gate, rule))
    lines += ["", "## Decision table", "",
              "| Condition | Verdict | Reading | Decision |",
              "| --- | --- | --- | --- |"]
    for row in doc["decision_table"]:
        lines.append("| %s | **%s** | %s | %s |" % (
            row["condition"], row["verdict"], row["reading"], row["decision"]))
    lines += [
        "",
        "## What this does not license",
        "",
        doc["not_evidence"],
        "",
        "The grant covers these twelve cells only. It does not authorise an engine edit, a "
        "promotion, a different cap, or a new seed block.",
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
    if doc.get("status") not in ("FROZEN, NOT RUN", "FROZEN, RUN"):
        found.append("status")
    if doc.get("frozen_on") != FROZEN_ON:
        found.append("freeze date")
    if doc.get("design", {}).get("seeds") != list(SEEDS):
        found.append("seeds")
    if doc.get("design", {}).get("cap") != CAP or doc.get("design", {}).get("cycles") != CYCLES:
        found.append("design")
    if doc.get("design", {}).get("cells") != 12:
        found.append("cells")
    if (doc.get("authorisation") or {}).get("granted") is not True:
        found.append("grant")
    if page.strip() != render(doc).strip():
        found.append("page stale")
    if doc.get("status") == "FROZEN, RUN" and not RESULT.exists():
        found.append("run artifact missing")
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


def mark_result(art: dict) -> None:
    doc = record()
    doc["status"] = "FROZEN, RUN"
    doc["no_cells_run"] = False
    doc["runner"]["cells_run"] = int(art["cells"])
    doc["result"] = RESULT.relative_to(ROOT).as_posix()
    doc["verdict"] = art["verdict"]
    doc = engine_stamp.stamp(doc)
    RECORD.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(doc), encoding="utf-8")


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
    print("core-band prereg: %s, %d cells, grant %s, runner %s" % (
        record()["status"], record()["design"]["cells"],
        record()["authorisation"]["granted"], record()["runner"]["built"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
