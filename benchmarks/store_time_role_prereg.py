"""Scope guard for the store-time role record: an engine change with its own preregistration.

The change itself is not written yet, and this module's job is to keep that honest. It checks the
preregistration against criteria fixed before any edit — not against a run:

* the document is **scoped and not applied**, so a claim of "preregistered" cannot hide an edit;
* the trace bar is CCRE-2's frozen P4 bar, not a number this document chose;
* the calibration seed is outside CCRE-2's confirmatory block, so nothing is fitted to the run it
  will judge (AGENTS.md rule 19);
* every neutrality criterion carries the mutation control that can fail (rule 25), every trace
  criterion names a leg of the claim, and the decision table's buckets lead to different decisions
  (rule 30);
* the engine does not already carry `schema_prior_roles` while the scope block says NOT APPLIED.

`validate` is pure and takes a parsed record, so its tests can tamper with one field at a time and
require the corresponding failure. `main --check` reads the document and the engine, writes nothing,
and exits non-zero on any defect.

    ./.venv/bin/python -m benchmarks.store_time_role_prereg --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "STORE-TIME-ROLE-RECORD-PREREGISTRATION.md"
EXTRACTION = ROOT / "organica" / "sleep_extraction.py"

# Frozen from CCRE-2's committed P4, written before any cell ran. Carried here, never fitted.
CCRE2_P4_BAR = 0.90
# Frozen from CCRE-2's committed confirmatory block. The calibration cell must fall outside it.
CONFIRMATORY_BLOCK = (20272001, 20272024)
FIELD = "schema_prior_roles"
SCOPE_KEYS = ("scope", "applied", "decision", "evidence", "bar_share",
               "calibration_seed", "confirmatory_block")
REQUIRED_SECTIONS = (
    "## 1. Scope",
    "## 2. What is recorded",
    "## 3. Why it can stay inert",
    "## 4. Neutrality criteria",
    "## 5. Trace criteria",
    "## 6. Falsifiers and the decision table",
    "## 7. Stop condition, version and pin",
    "## 8. What this cannot establish",
)
BUCKETS = ("APPLIES", "NEUTRAL_BUT_UNDURABLE", "BEHAVIOUR_CHANGED", "COVERAGE_MISFIRE")


def _scope_block(text: str) -> dict:
    values: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        for key in SCOPE_KEYS:
            if line.startswith(key + ":"):
                values[key] = line.split(":", 1)[1].strip()
    return values


def _buckets(text: str) -> dict[str, str]:
    """The decision-table cells: bucket -> the decision column, as written."""
    found: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3:
            continue
        name = cells[0].strip("`").strip()
        if name in BUCKETS:
            found[name] = cells[2]
    return found


def parse(text: str) -> dict:
    scope = _scope_block(text)
    block = scope.get("confirmatory_block", "")
    bounds = None
    if re.fullmatch(r"\d+-\d+", block):
        low, high = block.split("-")
        bounds = (int(low), int(high))
    return {
        "sections": [name for name in REQUIRED_SECTIONS if name in text],
        "scope": scope.get("scope"),
        "applied": {"true": True, "false": False}.get(scope.get("applied", "").lower()),
        "bar_share": float(scope["bar_share"]) if "bar_share" in scope else None,
        "calibration_seed": (
            int(scope["calibration_seed"])
            if scope.get("calibration_seed", "").isdigit()
            else None
        ),
        "confirmatory_block": bounds,
        "decision": scope.get("decision"),
        "evidence": scope.get("evidence"),
        "retired": "RETIRED" in text.split("---")[0],
        "neutrality": sorted(set(re.findall(r"\*\*N(\d)", text))),
        "trace": sorted(set(re.findall(r"\*\*T(\d)", text))),
        "stop_condition": "**Stop condition**" in text,
        "buckets": _buckets(text),
        "reserved_language": "held in reserve" in text or "in reserve" in text,
    }


def validate(record: dict, engine_applied: bool, evidence_decision=None) -> dict:
    errors: list[str] = []

    missing = [name for name in REQUIRED_SECTIONS if name not in record["sections"]]
    if missing:
        errors.append("missing sections: %s" % ", ".join(missing))
    if record["scope"] != "engine":
        errors.append("the scope block says %r, not 'engine': this is not an engine change"
                      % record["scope"])
    if record["applied"] is not False:
        errors.append("the scope block must say 'applied: false' while the change is a "
                      "preregistration")
    bar = record["bar_share"]
    if bar is None:
        errors.append("the scope block carries no trace bar")
    elif abs(bar - CCRE2_P4_BAR) > 1e-9:
        errors.append("the trace bar is %s, not CCRE-2's frozen P4 bar %s: a bar may not be set "
                      "by the document it judges" % (bar, CCRE2_P4_BAR))
    block = record["confirmatory_block"]
    if block is None:
        errors.append("the scope block carries no confirmatory block")
    elif tuple(block) != CONFIRMATORY_BLOCK:
        errors.append("the confirmatory block is %s, not CCRE-2's committed %s"
                      % (block, CONFIRMATORY_BLOCK))
    seed = record["calibration_seed"]
    if seed is None:
        errors.append("the scope block names no calibration seed")
    elif CONFIRMATORY_BLOCK[0] <= seed <= CONFIRMATORY_BLOCK[1]:
        errors.append("the calibration seed %d is inside CCRE-2's confirmatory block %d-%d"
                      % (seed, CONFIRMATORY_BLOCK[0], CONFIRMATORY_BLOCK[1]))
    if record["neutrality"] != ["1", "2", "3", "4"]:
        errors.append("neutrality criteria are %s, not N1-N4 (N4 is the mutation control)"
                      % record["neutrality"])
    if record["trace"] != ["1", "2", "3", "4"]:
        errors.append("trace criteria are %s, not T1-T4 (T4 is the durability leg)"
                      % record["trace"])
    if not record["stop_condition"]:
        errors.append("the document states no stop condition (rule 23c)")
    missing_buckets = [name for name in BUCKETS if name not in record["buckets"]]
    if missing_buckets:
        errors.append("the decision table lacks buckets: %s" % ", ".join(missing_buckets))
    elif len({decision.lower() for decision in record["buckets"].values()}) < 3:
        errors.append("two or more decision buckets lead to the same decision (rule 30)")
    if record["reserved_language"]:
        errors.append("the document still describes the change as held in reserve; that status "
                      "was superseded when it was scoped")
    decision = record.get("decision")
    if decision == "no_engine_change":
        if not record.get("evidence"):
            errors.append("the record says no engine change but names no evidence artifact")
        elif evidence_decision is None:
            errors.append("the evidence artifact it names is missing")
        elif evidence_decision != "NO_ENGINE_CHANGE":
            errors.append("the evidence says %s, but the record says no engine change"
                          % evidence_decision)
        if not record.get("retired"):
            errors.append("the record decides no engine change but its status does not say "
                          "RETIRED")
    elif decision not in (None, "apply"):
        errors.append("unknown decision %r (expected no_engine_change or apply)" % decision)
    if engine_applied:
        errors.append("the engine already carries %s while the scope block says NOT APPLIED"
                      % FIELD)
    return {"passed": not errors, "errors": errors,
            "checked": len(REQUIRED_SECTIONS) + 8, "buckets": sorted(record["buckets"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scope guard for the store-time role record.")
    parser.add_argument("--check", action="store_true", help="validate and write nothing")
    args = parser.parse_args(argv)
    if not args.check:
        parser.print_help()
        return 2
    if not DOC.exists():
        print("FAIL: %s is missing" % DOC.name)
        return 1
    engine_applied = FIELD in EXTRACTION.read_text(encoding="utf-8")
    record = parse(DOC.read_text(encoding="utf-8"))
    evidence_decision = None
    evidence = record.get("evidence")
    if evidence and (ROOT / evidence).exists():
        evidence_decision = json.loads(
            (ROOT / evidence).read_text(encoding="utf-8"))["measurement"]["decision"]
    report = validate(record, engine_applied, evidence_decision)
    if not report["passed"]:
        print("FAIL:")
        for error in report["errors"]:
            print(" - %s" % error)
        return 1
    print("store-time role preregistration: %s, not applied (%d checks)"
          % ("retired on evidence" if record.get("decision") == "no_engine_change"
             else "scoped", report["checked"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
