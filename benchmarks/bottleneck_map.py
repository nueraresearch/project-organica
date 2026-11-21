"""Render the bottleneck map's tables from `docs/bottleneck_map.json`.

Three tables in `docs/BOTTLENECK-MAP.md` restate the artifact: the historical candidate map in
section 2, the constraint ledger in section 2b, and the label table in section 3. All are
generated here between markers, and `tests/test_bottleneck_map.py` asserts that the committed
document is exactly what this module produces -- a hand-maintained restatement drifts, which is
what `AGENTS.md` rule 27 exists for.

The constraint ledger is deliberately separate from the historical map. The map records what an
explanation may claim; the ledger records the constraints under consideration and, at most one at
a time, the constraint in test. Its lifecycle is `open -> in-test -> retired`; the ledger may have
zero `in-test` rows before the first test and after the active row retires. A row needs evidence,
a hypothesis, an intervention and a decision rule before it can enter test; retirement requires a
result and an architectural consequence.

The status column of the map table carries the artifact's statuses verbatim, so a
compound status reads as its two statuses joined by ` + `. The check column is
kept to one sentence per row (`MAX_CHECK_CHARS`), because a markdown table cell
cannot wrap and an over-long cell is where readability goes.

The map table also carries each row's **provenance tag**, and the paragraph beneath it is
generated from those tags rather than from a count typed beside them. The tags themselves are
validated by `benchmarks.provenance` before anything is rendered: a row whose tag its evidence
cannot back stops the write instead of reaching the page.

Regenerate with:

    python -m benchmarks.bottleneck_map --write

Standard library only; no engine file is read or written.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import provenance as prov

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "bottleneck_map.json"
DOC = ROOT / "docs" / "BOTTLENECK-MAP.md"

MAP_BEGIN = ("<!-- BEGIN MAP TABLE: generated from docs/bottleneck_map.json by "
             "benchmarks/bottleneck_map.py; do not edit by hand -->")
MAP_END = "<!-- END MAP TABLE -->"
BEGIN = ("<!-- BEGIN LABEL TABLE: generated from docs/bottleneck_map.json by "
         "benchmarks/bottleneck_map.py; do not edit by hand -->")
END = "<!-- END LABEL TABLE -->"
PROV_BEGIN = ("<!-- BEGIN PROVENANCE: generated from docs/bottleneck_map.json by "
              "benchmarks/bottleneck_map.py; do not edit by hand -->")
PROV_END = "<!-- END PROVENANCE -->"

LABEL_COLUMNS = ("| Map label | What it means | Status it maps to |", "|---|---|---|")
MAP_COLUMNS = ("| Candidate | Map label | Status | The check behind it | Provenance |",
               "|---|---|---|---|---|")

CONSTRAINT_BEGIN = ("<!-- BEGIN CONSTRAINT LEDGER: generated from docs/bottleneck_map.json by "
                    "benchmarks/bottleneck_map.py; do not edit by hand -->")
CONSTRAINT_END = "<!-- END CONSTRAINT LEDGER -->"
CONSTRAINT_COLUMNS = ("| Constraint (state) | Evidence | Hypothesis | Intervention | Decision rule |",
                      "|---|---|---|---|---|")
CONSTRAINT_STATES = ("open", "in-test", "retired")
TRANSITIONS = {("open", "in-test"), ("in-test", "retired")}
REGISTRATION_FIELDS = ("id", "constraint", "status_date", "intervention", "endpoint",
                       "comparator", "decision_threshold", "threshold_values")
OUTCOMES = ("pass", "fail", "inconclusive", "attempt_invalid")
THRESHOLD_KEYS = ("baseline_gap", "pass_min_improvement", "pass_max_k1_abs_change",
                  "fail_below_improvement", "inconclusive_min_improvement",
                  "inconclusive_max_improvement")


def _record(relative, root, what: str) -> dict:
    path = Path(root) / str(relative)
    if not path.is_file():
        raise ValueError("%s record does not exist: %s" % (what, relative))
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError("%s record is not JSON: %s (%s)" % (what, relative, exc))
    if not isinstance(record, dict):
        raise ValueError("%s record is not an object: %s" % (what, relative))
    return record


def _history(row: dict, name: str, state: str) -> None:
    history = row.get("history") or []
    if not isinstance(history, list):
        raise ValueError("%s transition history is not a list" % name)
    if state == "open":
        if history:
            raise ValueError("%s is open but carries transition history" % name)
        return
    if not history:
        raise ValueError("%s is %s but carries no transition history" % (name, state))
    previous = "open"
    for step in history:
        if not isinstance(step, dict):
            raise ValueError("%s transition history contains a non-object step" % name)
        if step.get("from") != previous:
            raise ValueError("%s has a broken transition history: expected from %r, got %r"
                             % (name, previous, step.get("from")))
        if (previous, step.get("to")) not in TRANSITIONS:
            raise ValueError("%s has an invalid transition: %s -> %s"
                             % (name, previous, step.get("to")))
        previous = step["to"]
    if previous != state:
        raise ValueError("%s history ends at %s, not its state %s" % (name, previous, state))


def _registration(row: dict, root: Path) -> dict:
    name = str(row.get("constraint") or "<unnamed constraint>")
    relative = row.get("registration")
    if not relative:
        raise ValueError("%s is %s but names no registration record"
                         % (name, row.get("state")))
    record = _record(relative, root, "registration")
    missing = [field for field in REGISTRATION_FIELDS
               if not str(record.get(field) or "").strip()]
    if missing:
        raise ValueError("%s registration is missing %s" % (name, ", ".join(missing)))
    thresholds = record["decision_threshold"]
    if not isinstance(thresholds, dict) or not all(
            str(thresholds.get(key) or "").strip()
            for key in ("pass", "fail", "inconclusive")):
        raise ValueError("%s registration needs pass, fail and inconclusive thresholds" % name)
    values = record.get("threshold_values")
    if not isinstance(values, dict) or not all(
            isinstance(values.get(key), (int, float)) and not isinstance(values.get(key), bool)
            for key in THRESHOLD_KEYS):
        raise ValueError("%s registration needs numeric threshold values" % name)
    if not (values["fail_below_improvement"] <= values["inconclusive_min_improvement"]
            <= values["inconclusive_max_improvement"]
            and values["inconclusive_max_improvement"] <= values["pass_min_improvement"]):
        raise ValueError("%s registration has non-monotone thresholds" % name)
    if record["constraint"] != row.get("constraint"):
        raise ValueError("%s registration names a different constraint" % name)
    history = row.get("history") or []
    if history and history[-1].get("registration") not in (None, record["id"]):
        raise ValueError("%s transition history names a different registration" % name)
    return record


def _retirement(row: dict, root: Path, registration: dict) -> None:
    name = str(row.get("constraint") or "<unnamed constraint>")
    if not str(row.get("retirement_reason") or "").strip():
        raise ValueError("%s is retired but has no retirement reason" % name)
    result = _record(row.get("result") or "", root, "result")
    decision = _record(row.get("decision") or "", root, "decision")
    if result.get("outcome") not in OUTCOMES:
        raise ValueError("%s result outcome must be one of %s" % (name, list(OUTCOMES)))
    if result["outcome"] == "attempt_invalid":
        if result.get("hypothesis_status") != "untested":
            raise ValueError("invalid attempt must record hypothesis_status 'untested'")
        if result.get("criteria_read") is not False:
            raise ValueError("invalid attempt must record criteria_read false")
        text = str(decision.get("decision") or "").lower()
        if "untested" not in text:
            raise ValueError("invalid-attempt retirement must say the hypothesis is untested")
        # Every invalid attempt records how many cells it started.  The field is
        # required rather than optional: a result that omits it could otherwise
        # dodge the unrun branch below, which is the only place a withdrawal is
        # held to the wording a withdrawal needs.
        if "cells_started" not in result:
            raise ValueError(
                "invalid attempt must record cells_started, so an unrun retirement "
                "cannot dodge the not-refuted check")
        cells_started = result["cells_started"]
        if (not isinstance(cells_started, int) or isinstance(cells_started, bool)
                or cells_started < 0):
            raise ValueError("%s result has a non-integer cells_started" % name)
        # Zero cells started is a registration withdrawn before a grant, not a
        # block that ran and returned VOID.  It carries the same meaning -- no
        # admissible comparison exists -- so the decision must say what a reader
        # would otherwise have to infer: nothing was refuted.
        if cells_started == 0 and "not refuted" not in text:
            raise ValueError(
                "an unrun retirement must say the hypothesis is not refuted")
    if not str(result.get("id") or "").strip():
        raise ValueError("%s result has no record id" % name)
    if not str(decision.get("id") or "").strip():
        raise ValueError("%s decision has no record id" % name)
    if result.get("registration") not in (registration.get("id"), row.get("registration")):
        raise ValueError("%s result does not reference its registration" % name)
    if decision.get("result") not in (result.get("id"), row.get("result")):
        raise ValueError("%s decision does not reference its result" % name)
    if not str(decision.get("decision") or "").strip():
        raise ValueError("%s decision record has no architectural decision" % name)


def validate_constraint_row(row: dict, root: Path = ROOT) -> dict:
    """Validate one row and the artifacts its state claims, returning its registration."""
    name = str(row.get("constraint") or "<unnamed constraint>")
    state = row.get("state")
    if state not in CONSTRAINT_STATES:
        raise ValueError("%s has state %r, not one of %s"
                         % (name, state, list(CONSTRAINT_STATES)))
    for field in ("evidence", "hypothesis", "intervention", "decision_rule"):
        if not str(row.get(field) or "").strip():
            raise ValueError("%s has no %s" % (name, field))
    _history(row, name, state)
    if state == "open":
        if row.get("registration") or row.get("result") or row.get("decision"):
            raise ValueError("%s is open but carries a registration, result or decision" % name)
        return {}
    registration = _registration(row, root)
    if state == "retired":
        _retirement(row, root, registration)
    elif row.get("result") or row.get("decision"):
        raise ValueError("%s is in-test but already has a result or decision" % name)
    return registration


def constraint_rows(body: dict, root: Path = ROOT) -> list[dict]:
    """The ledger rows, refusing a malformed, over-subscribed or unchained ledger."""
    ledger = body.get("constraint_ledger")
    if not isinstance(ledger, dict):
        raise ValueError("the artifact has no constraint_ledger")
    rows = ledger.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("the constraint ledger has no rows")
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("the constraint ledger contains a non-object row")
        validate_constraint_row(row, root)
    in_test = [row for row in rows if row["state"] == "in-test"]
    if len(in_test) > 1:
        raise ValueError("the constraint ledger must have at most one in-test row, not %d"
                         % len(in_test))
    return rows

# A check cell is one sentence the reader can hold. Beyond this the row stops
# being a table and becomes a paragraph with pipes in it.
MAX_CHECK_CHARS = 400


def load_artifact(path: Path = ARTIFACT) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cell(value, where: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("%s is empty and cannot be a table cell" % where)
    if "|" in text or "\n" in text:
        raise ValueError("%s cannot be one table cell: %r" % (where, text[:60]))
    return text


def render_table(body: dict) -> str:
    """The section 3 label table, rendered from `label_meanings`."""
    lines = list(LABEL_COLUMNS)
    for label, meaning in body["label_meanings"].items():
        lines.append("| %s | %s | %s |" % (
            _cell(label, "label"),
            _cell(meaning["means"], "meaning of %r" % label),
            _cell(meaning["status"], "mapping of %r" % label),
        ))
    return "\n".join(lines)


def render_constraint_table(body: dict) -> str:
    """The section 2b constraint ledger, rendered from `constraint_ledger`."""
    lines = list(CONSTRAINT_COLUMNS)
    for row in constraint_rows(body):
        constraint = str(row["constraint"])
        lines.append("| %s (%s) | %s | %s | %s | %s |" % (
            _cell(constraint, "constraint"),
            _cell(row["state"], "state of %r" % constraint),
            _cell(row["evidence"], "evidence of %r" % constraint),
            _cell(row["hypothesis"], "hypothesis of %r" % constraint),
            _cell(row["intervention"], "intervention of %r" % constraint),
            _cell(row["decision_rule"], "decision rule of %r" % constraint),
        ))
    return "\n".join(lines)


def render_map_table(body: dict) -> str:
    """The section 2 historical candidate table, rendered from `rows`."""
    lines = list(MAP_COLUMNS)
    for row in body["rows"]:
        candidate = row["candidate"]
        check = _cell(row["check"], "check for %r" % candidate)
        if len(check) > MAX_CHECK_CHARS:
            raise ValueError(
                "the check for %r is %d characters, over the %d-character budget for a "
                "readable cell; shorten it in the artifact rather than in the document"
                % (candidate, len(check), MAX_CHECK_CHARS))
        lines.append("| %s | %s | %s | %s | %s |" % (
            _cell(candidate, "candidate"),
            _cell(row["label"], "label of %r" % candidate),
            _cell(" + ".join(row["status"]), "status of %r" % candidate),
            check,
            _cell(row["provenance"], "provenance of %r" % candidate),
        ))
    return "\n".join(lines)


def _replace_block(text: str, begin: str, end: str, rendered: str) -> str:
    start = text.find(begin)
    stop = text.find(end)
    if start < 0 or stop < 0 or stop < start:
        raise ValueError("the markers for %r are missing from the document" % begin[:40])
    return text[:start] + begin + "\n" + rendered + "\n" + end + text[stop + len(end):]


def render_document(text: str, body: dict) -> str:
    """Return `text` with every marked table replaced by a freshly rendered one.

    Idempotent: rendering an already-rendered document returns it unchanged.
    Raises `ValueError` when a marker pair is missing, because a silently
    unrendered table is the failure this module exists to prevent.
    """
    findings = prov.check_map(body, ROOT)
    if findings:
        raise ValueError(
            "the artifact's provenance tags do not hold: "
            + "; ".join(f["message"] for f in findings))
    for begin, end, render in ((MAP_BEGIN, MAP_END, render_map_table),
                               (PROV_BEGIN, PROV_END, prov.render_summary),
                               (CONSTRAINT_BEGIN, CONSTRAINT_END, render_constraint_table),
                               (BEGIN, END, render_table)):
        text = _replace_block(text, begin, end, render(body))
    return text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="rewrite both tables in the document")
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if either table is stale")
    args = parser.parse_args(argv)

    body = load_artifact()
    text = DOC.read_text(encoding="utf-8")
    fresh = render_document(text, body)
    if args.write:
        DOC.write_text(fresh, encoding="utf-8")
        per_tag = prov.counts(body)
        print("wrote %d map rows, %d constraint rows, %d label rows and %d provenance tags "
              "into %s" % (len(body["rows"]), len(constraint_rows(body)),
                            len(body["label_meanings"]), sum(per_tag.values()),
                            DOC.relative_to(ROOT).as_posix()))
        return 0
    if args.check:
        if fresh != text:
            print("a table is stale: run python -m benchmarks.bottleneck_map --write")
            return 1
        print("every generated table matches the artifact")
        return 0
    print(render_map_table(body))
    print()
    print(prov.render_summary(body))
    print()
    print(render_table(body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
