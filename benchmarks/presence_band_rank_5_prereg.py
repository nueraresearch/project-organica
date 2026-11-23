"""PRESENCE-BAND-5: a runnable fresh-world allocation-law band block.

The block reuses the defensible B5 specified by BAND-4: at cap 112 a full
window has ``transitions + cooccurrences = 112``, ``transitions >= 56`` and
``cooccurrences <= 56``. The six seeds are fresh. The dated grant is recorded
before the arm is built or a cell is opened. The arm writes a per-edge ledger.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.presence_band_rank_4_prereg import b5_fixture_results

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "presence_band_rank_5_prereg.json"
PAGE = ROOT / "docs" / "PRESENCE-BAND-RANK-5-PREREGISTRATION.md"
RUN = ROOT / "docs" / "presence_band_rank_5_run.json"
ARM = ROOT / "benchmarks" / "presence_band_rank_5_arm.py"
AUTH = ROOT / "docs" / "AUTHORISATION-PRESENCE-BAND-5.md"

ID = "PRESENCE-BAND-5"
FROZEN_ON = "2026-11-11"
SEEDS = (20612601, 20612602, 20612603, 20612604, 20612605, 20612606)
GRANT_QUOTE = (
    "Register a new band block with a defensible B5 allocation rule and a fresh dated "
    "grant, then run its twelve cells into a per-edge result."
)


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def build() -> dict:
    return {
        "prereg": ID,
        "status": "FROZEN, NOT RUN",
        "frozen_on": FROZEN_ON,
        "no_cells_run": True,
        "question": (
            "On the shipped 0.15.0 build, with six fresh worlds, does the cap-112 "
            "allocation satisfy the full-window floor-plus-backfill law and does every "
            "measured rank-21-40 transition enter service, with allocation and band "
            "service able to fail independently?"
        ),
        "program": {
            "draft": "docs/DECISION-ADMISSION-STEP.md",
            "question": "Q054",
            "relationship": (
                "BAND-1 was VOID on exact-56; BAND-2/3 corrected the floor; BAND-4 "
                "specified the full-window allocation-law B5 but was never granted or "
                "run. BAND-5 is the runnable block: a fresh seed set, the same "
                "allocation law, a dated grant before any cell, and a per-edge result."
            ),
        },
        "reconciliation": {
            "floor": "At cap 112, transition_budget = 112 // 2 = 56.",
            "backfill": (
                "The engine fills the remaining 56 seats with cooccurrences, then "
                "backfills unused cooccurrence seats with further transitions. A full "
                "window therefore has transitions + cooccurrences = 112."
            ),
            "observed_64_69": (
                "BAND-1 observed 64-69 transitions; those are 56 plus backfill, with "
                "48-43 cooccurrences. 64-69 is not an acceptance threshold."
            ),
            "rule": (
                "Defensible B5: at least one full 112-row window; every full window has "
                "transitions >= 56, cooccurrences <= 56 and the sum 112; every allocation "
                "row sums to its window; the maximum served transition rank is above 40; "
                "every served edge parses and every served transition is ranked."
            ),
        },
        "design": {
            "arms": ["cap 40", "cap 112"],
            "caps": [40, 112],
            "shipped_cap": 112,
            "seeds": list(SEEDS),
            "cycles": 120,
            "cells": 12,
            "cells_arithmetic": "2 caps x 6 seeds = 12 cells",
            "variable": "SleepService.MAX_PREDICTIONS, set per cell",
            "observer": "the repaired observer of PRESENCE-CONVERSION-2",
            "world": "the PHASE_ACQUISITION compositional world at 120 cycles",
            "pairing": "each seed's world and stimulus are identical at both caps",
            "freshness": "Six fresh seeds; seed_collisions is empty at freeze time.",
            "reuse": "No prior block's cells, named band or result is reused.",
        },
        "band": {
            "definition": (
                "For each seed, every present transition at minimum cap-112 block rank "
                "21-40; measured from the 112 universe and not filtered by cap-40 service."
            ),
            "zero_band": "A zero band is a zero denominator and makes the block VOID.",
        },
        "engine": {"version": "0.15.0", "cap": 112, "edit": "none"},
        "gates": {
            "B1_build": "one shipped 0.15.0 build across all cells; only MAX_PREDICTIONS differs",
            "B2_world": "each seed has the same world digest and present fingerprint at both caps",
            "B3_band_identity": "each band edge is a present transition at rank 21-40 with a recorded rank",
            "B4_control_40": "cap 40 serves no band edge and its full 40-row windows sum with a 20-transition floor",
            "B5_allocation_law": "cap 112 full windows satisfy transitions + cooccurrences = 112, transitions >= 56, cooccurrences <= 56, with rank and parsing live",
            "B6_denominator": "every seed has a non-empty band and every band edge reaches the ledger",
            "B7_determinism": "a fresh-process rerun of seed 20612601 at 112 reproduces its ledger",
            "B8_seed_axis": "at least three distinct served-band sets across the six seeds",
        },
        "b5_fixture": b5_fixture_results(),
        "acceptance": {
            "kind": "co-primary, independently falsifiable",
            "criterion_a": "B5 allocation law passes.",
            "criterion_b": "every band edge is served at 112 and none at 40, with a live seed axis.",
            "confirmed": "CONFIRMED only when both criteria pass.",
            "independent_failure": (
                "Perfect band service cannot rescue a failed B5; a perfect allocation "
                "cannot rescue an unserved band edge."
            ),
            "not_fitted": "64-69 is not used as a threshold.",
        },
        "decision_table": [
            {
                "condition": "B1, B2, B3 identity, B6, B7 or B8 fails",
                "verdict": "VOID",
                "reading": "the block is non-reproducible and the failed gate names what did not happen",
                "decision": "record VOID; fix the failed gate and register a new block; read no acceptance",
            },
            {
                "condition": "B5 allocation law fails",
                "verdict": "ALLOCATION LAW NOT CONFIRMED",
                "reading": "band service cannot establish the full-window floor-plus-backfill allocation",
                "decision": "report the allocation failure; fix the allocation rule before another band block; no band confirmation",
            },
            {
                "condition": "B5 passes and no measured band edge is served at 112",
                "verdict": "BAND NOT CONFIRMED",
                "reading": "the allocation is correct but the measured rank-21-40 band does not enter service",
                "decision": "report the refutation; the next step is the admission rule, not another cap level",
            },
            {
                "condition": "B5 passes and some but not all measured band edges are served at 112",
                "verdict": "BAND PARTLY NOT CONFIRMED",
                "reading": "the allocation is correct but the band does not enter service uniformly",
                "decision": "report the per-edge misses; the next step is the admission rule",
            },
            {
                "condition": "B5 and every measured band edge pass, with the 40 control and seed axis live",
                "verdict": "CONFIRMED",
                "reading": "the floor-plus-backfill law and fresh-world rank-21-40 service both hold",
                "decision": "record the confirmation; the owner decides any engine or promotion step; no capability claim",
            },
        ],
        "authorisation": {
            "required": True,
            "granted": True,
            "granted_on": FROZEN_ON,
            "document": "docs/AUTHORISATION-PRESENCE-BAND-5.md",
            "quote": GRANT_QUOTE,
            "note": "Granted before the arm was built or any cell opened.",
        },
        "runner": {
            "built": False,
            "planned_module": "benchmarks/presence_band_rank_5_arm.py",
            "cells_run": 0,
            "why": "the record and grant precede the arm",
        },
        "cost": {"cells": 12, "witness_cells": "one determinism rerun", "cycles": 120},
        "not_evidence": (
            "A preregistration until the cells run; after the run it reads allocation and "
            "band service on this world family, not capability, retention or transfer."
        ),
        "amendments": [
            {"date": FROZEN_ON, "kind": "granted", "note": "Grant recorded before the arm or any cell."}
        ],
    }


def render(doc: dict) -> str:
    lines = [
        "# PRESENCE-BAND-5 — runnable allocation-law band block",
        "",
        "**Status.** %s. Generated from `%s`." % (doc["status"], RECORD.relative_to(ROOT).as_posix()),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Seeds | %s |" % ", ".join(str(s) for s in doc["design"]["seeds"]),
        "| Cells | %d |" % doc["design"]["cells"],
        "| Caps | 40, 112 |",
        "| Cycles | 120 |",
        "| Grant | %s |" % doc["authorisation"]["granted_on"],
        "| Runner | %s |" % ("built" if doc["runner"]["built"] else "not built"),
        "| Cells run | %d |" % doc["runner"]["cells_run"],
        "",
        "## Reconciliation",
        "",
        doc["reconciliation"]["backfill"],
        "",
        doc["reconciliation"]["observed_64_69"],
        "",
        "**B5 rule.** %s" % doc["reconciliation"]["rule"],
        "",
        "## Acceptance",
        "",
        "**A.** %s" % doc["acceptance"]["criterion_a"],
        "",
        "**B.** %s" % doc["acceptance"]["criterion_b"],
        "",
        doc["acceptance"]["independent_failure"],
        "",
        "## Grant",
        "",
        "> %s" % doc["authorisation"]["quote"],
        "",
        "`%s`" % doc["authorisation"]["document"],
        "",
        "## Gates",
        "",
        "| Gate | Rule |",
        "| --- | --- |",
    ]
    for gate, rule in doc["gates"].items():
        lines.append("| `%s` | %s |" % (gate, rule))
    if doc.get("result"):
        lines += ["", "## Result", "", "**%s** — `%s`" % (
            doc["result"]["verdict"], doc["result"]["artifact"])]
    lines += ["", doc["not_evidence"], ""]
    return "\n".join(lines)


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
    if doc["authorisation"].get("granted") is not True:
        found.append("grant")
    auth = ROOT / doc["authorisation"]["document"]
    if not auth.exists() or doc["authorisation"]["quote"] not in auth.read_text(encoding="utf-8"):
        found.append("grant document/quote")
    if len(doc["design"]["seeds"]) != 6 or doc["design"]["cells"] != 12:
        found.append("design")
    from benchmarks.presence_cap_experiment import seed_collisions
    if seed_collisions(doc["design"]["seeds"], allow=(RECORD, PAGE, AUTH, RUN)):
        found.append("seed collision")
    for name in ("pass_64_plus_48", "pass_56_plus_56"):
        if doc["b5_fixture"].get(name, {}).get("passed") is not True:
            found.append("B5 fixture %s" % name)
    for name, result in doc["b5_fixture"].items():
        if name.startswith("fail_") and result.get("passed") is not False:
            found.append("B5 fixture %s" % name)
    if doc["runner"]["cells_run"] not in (0, 13):
        found.append("runner cells")
    if doc["status"] == "FROZEN, RUN" and not RUN.exists():
        found.append("run artifact missing")
    if doc["status"] == "FROZEN, NOT RUN" and RUN.exists():
        found.append("unrun block has a result")
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


def mark_result(art: dict) -> None:
    doc = record()
    doc["status"] = "FROZEN, RUN"
    doc["no_cells_run"] = False
    doc["runner"].update({"built": True, "cells_run": 13})
    doc["result"] = {"verdict": art["verdict"], "artifact": str(RUN.relative_to(ROOT).as_posix())}
    doc["amendments"].append({
        "date": FROZEN_ON,
        "kind": "run-completed",
        "note": "12 design cells plus the determinism rerun completed; per-edge result written.",
    })
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
    doc = record()
    print("presence band 5: %s, %d cells, grant %s, runner %s" % (
        doc["status"], doc["design"]["cells"], doc["authorisation"]["granted"],
        doc["runner"]["cells_run"]))
    return 0
