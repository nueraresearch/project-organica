"""Sibling independence of the three run conversion records, checked rather than asserted.

Q1, Q2 and Q3 share an engine build and an audit lineage and partly a seed set. Their verdicts must stay
independent of one another: no pooled rows, no sibling verdict used as evidence, no sibling failure
voiding a record and no record rescuing a sibling. Each frozen record carries the clause as a dated
amendment; this check requires it, and the tests prove the check fails on a removed clause, a wrong date
and a copied verdict.

    ./.venv/bin/python -m benchmarks.conversion_sibling_independence --check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-11-11"
SIBLINGS = ("PRESENCE-CONSTRUCT-1", "PRESENCE-CAP-1", "PRESENCE-CONVERSION-1")
RECORDS = {
    "docs/presence_construct_audit_prereg.json": ("PRESENCE-CONSTRUCT-1", "CONSTRUCT VALID"),
    "docs/presence_cap_prereg.json": ("PRESENCE-CAP-1", "CAP LIMITING"),
    "docs/presence_conversion_observer_prereg.json": ("PRESENCE-CONVERSION-1",
                                                       "OBSERVER NOT NEUTRAL"),
}
PHRASES = ("No rows are pooled", "is not evidence", "does not void", "does not rescue",
           "same engine build")
UNCHANGED = {"status", "verdict", "gates", "seeds", "result", "authorisation"}
EVIDENCE_KEYS = ("artifact", "evidence", "source")


def load() -> dict:
    return {path: json.loads((ROOT / path).read_text(encoding="utf-8")) for path in RECORDS}


def _flatten(node) -> list[str]:
    """Every string under ``node``, so a list of paths is read as paths."""
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [value for child in node.values() for value in _flatten(child)]
    if isinstance(node, list):
        return [value for child in node for value in _flatten(child)]
    return []


def _evidence_strings(node) -> list[str]:
    """Values held under an artifact, evidence or source key, at any depth.

    The scope is deliberate: a record that names a sibling's artifact in free prose is making a
    statement, while a record that lists it under one of these keys is offering it as evidence --
    which is the thing the clause forbids.
    """
    if isinstance(node, dict):
        values = []
        for key, value in node.items():
            if any(marker in key.lower() for marker in EVIDENCE_KEYS):
                values.extend(_flatten(value))
            values.extend(_evidence_strings(value))
        return values
    if isinstance(node, list):
        return [value for child in node for value in _evidence_strings(child)]
    return []


def _names(value: str, artifact: str) -> bool:
    """The path or its basename, so a record cannot hide a sibling behind `./` or a basename."""
    value = value.strip().rstrip("/")
    return value == artifact or Path(value).name == Path(artifact).name


def sibling_artifacts(records: dict) -> dict[str, str | None]:
    return {path: ((records.get(path) or {}).get("result") or {}).get("artifact")
            for path in RECORDS}


def problems(records: dict | None = None) -> list[str]:
    """Everything a record must say, and every way it can borrow a sibling's result."""
    records = load() if records is None else records
    found: list[str] = []
    artifacts = sibling_artifacts(records)
    for path, (prereg_id, verdict) in RECORDS.items():
        rec = records.get(path)
        if rec is None:
            found.append("%s: missing record" % path)
            continue
        if rec.get("prereg") != prereg_id:
            found.append("%s: prereg is %r" % (path, rec.get("prereg")))
        for sibling_path, artifact in artifacts.items():
            if sibling_path == path or not artifact:
                continue
            if any(_names(value, artifact) for value in _evidence_strings(rec)):
                found.append("%s: lists sibling %s's artifact %s as evidence"
                             % (path, RECORDS[sibling_path][0], artifact))
        clauses = [a for a in rec.get("amendments") or []
                   if a.get("kind") == "sibling-independence"]
        if len(clauses) != 1:
            found.append("%s: %d sibling-independence clauses" % (path, len(clauses)))
            continue
        clause = clauses[0]
        if clause.get("date") != DATE:
            found.append("%s: the clause is dated %r" % (path, clause.get("date")))
        text = clause.get("clause") or ""
        for phrase in PHRASES:
            if phrase not in text:
                found.append("%s: the clause omits %r" % (path, phrase))
        for sibling in SIBLINGS:
            if sibling not in text:
                found.append("%s: the clause does not name %s" % (path, sibling))
        if not (clause.get("specific") or "").strip():
            found.append("%s: the clause does not state this record's own shared dependency" % path)
        if set(clause.get("unchanged") or []) != UNCHANGED:
            found.append("%s: the clause does not state what it leaves unchanged" % path)
        if (rec.get("result") or {}).get("verdict") != verdict:
            found.append("%s: verdict is %r, not %r"
                         % (path, (rec.get("result") or {}).get("verdict"), verdict))
    verdicts = [(records.get(path) or {}).get("result", {}).get("verdict") for path in RECORDS]
    if len(set(verdicts)) != len(RECORDS):
        found.append("two conversion records share a verdict: %r" % (verdicts,))
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args(argv)
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    print("conversion siblings: %d records, %d distinct verdicts, clauses dated %s"
          % (len(RECORDS), len({verdict for _, verdict in RECORDS.values()}), DATE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
