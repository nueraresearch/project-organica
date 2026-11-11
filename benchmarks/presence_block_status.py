"""Derive the manual's conversion-block row from the three frozen records.

The manual's status section carried a hand-typed row naming Q1, Q2 and Q3's freeze
dates, record paths, authorisation and run state. It was typed while all three were
unrun, annotated by hand when they were authorised, and rewritten by hand again when
they ran -- three edits to one sentence, each of which had to be remembered. A status
row that exists to stop a reader confusing *protocol built* with *evidence produced*
is the last place worth trusting to a habit.

This module removes the habit. The row's cell is rendered from the three records, and
``--check`` is the gate: it fails when the manual disagrees with a fresh render, and it
also fails when a record's *own* fields contradict each other -- a ``FROZEN, RUN`` record
that says no cell ran, a result naming an artifact or page that does not exist, or a
grant whose dated authorisation document is missing. So a record edited without
re-rendering, or rendered from a record that is internally inconsistent, leaves the
check red rather than leaving a row that describes an older state.

Nothing is written in ``--check`` mode: a gate that regenerates before judging would
pass stale text every time. The plain invocation regenerates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "docs" / "USER-MANUAL.md"

# The program's own order: construct, cap, conversion. The labels a reader sees are the
# records' own ids -- this tuple fixes only which records the row speaks for.
RECORDS = (
    ROOT / "docs" / "presence_construct_audit_prereg.json",
    ROOT / "docs" / "presence_cap_prereg.json",
    ROOT / "docs" / "presence_conversion_observer_prereg.json",
)

MARK_START = "<!-- presence-blocks:auto -->"
MARK_END = "<!-- /presence-blocks:auto -->"

RUN = "FROZEN, RUN"
NOT_RUN = "FROZEN, NOT RUN"


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_records() -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in RECORDS]


def _words(items: list[str]) -> str:
    """`a`, `b` and `c` -- the way the rest of the manual lists three things."""
    quoted = ["`%s`" % item for item in items]
    if len(quoted) <= 1:
        return "".join(quoted)
    return ", ".join(quoted[:-1]) + " and " + quoted[-1]


def _block(record: dict, path: Path) -> str:
    """One record, stated as the five things a reader needs: when, where, allowed, ran, verdict."""
    auth = record.get("authorisation") or {}
    result = record.get("result") or {}

    frozen = record.get("frozen_on") or "no freeze date recorded"
    if auth.get("granted"):
        allowed = "authorised %s by `%s`" % (
            auth.get("granted_on") or "with no date recorded",
            auth.get("document") or "no document recorded",
        )
    else:
        allowed = "unauthorised"

    if result:
        ran = "verdict **`%s`**, artifact `%s`, page `%s`" % (
            result.get("verdict") or "none recorded",
            result.get("artifact") or "none recorded",
            result.get("page") or "none recorded",
        )
    else:
        ran = "unrun, with no verdict and no result artifact"

    return "`%s` — frozen %s, record `%s`, %s, status **%s**, %s" % (
        record.get("prereg") or "unnamed block",
        frozen,
        _rel(path),
        allowed,
        record.get("status") or "no status recorded",
        ran,
    )


def render(records: list[dict] | None = None) -> str:
    """The manual cell, derived. Never type this; regenerate it."""
    records = load_records() if records is None else records
    if len(records) != len(RECORDS):
        raise ValueError("expected %d records, got %d" % (len(RECORDS), len(records)))

    statuses = {record.get("status") for record in records}
    verdicts = [(record.get("result") or {}).get("verdict") for record in records]

    if len(statuses) == 1 and None not in verdicts:
        head = "**All three blocks are `%s`; the verdicts are %s.**" % (
            statuses.pop(), _words(verdicts))
    elif len(statuses) == 1:
        head = "**All three blocks are `%s`; not every one has run.**" % statuses.pop()
    else:
        head = "**The three blocks do not stand in one state.**"

    body = "; ".join(
        _block(record, path) for path, record in zip(RECORDS, records))
    return "%s Derived from the three records by `python -m benchmarks.presence_block_status`: %s." % (
        head, body)


def region_of(text: str) -> str:
    """Return the current contents of the single marked region."""
    if text.count(MARK_START) != 1 or text.count(MARK_END) != 1:
        raise ValueError("expected exactly one %s ... %s region" % (MARK_START, MARK_END))
    start = text.index(MARK_START) + len(MARK_START)
    end = text.index(MARK_END)
    if end < start:
        raise ValueError("the conversion-block markers are out of order")
    return text[start:end]


def with_fragment(text: str, fragment: str) -> str:
    """Replace the marked region, leaving every other character alone."""
    region_of(text)
    start = text.index(MARK_START) + len(MARK_START)
    end = text.index(MARK_END)
    return text[:start] + fragment + text[end:]


def _state_problems(path: Path, record: dict) -> list[str]:
    """Everything wrong with one record's own state, independent of the manual."""
    name = _rel(path)
    found: list[str] = []
    if not path.exists():
        return ["%s does not exist" % name]

    status = record.get("status")
    result = record.get("result") or {}
    auth = record.get("authorisation") or {}

    if not record.get("frozen_on"):
        found.append("%s records no freeze date" % name)

    if status == RUN:
        if record.get("no_cells_run"):
            found.append("%s says %s but also that no cell ran" % (name, RUN))
        if not result:
            found.append("%s says %s but carries no result block" % (name, RUN))
        for field in ("verdict", "artifact", "page", "ran_on"):
            if not result.get(field):
                found.append("%s's result names no %s" % (name, field))
        for field in ("artifact", "page"):
            declared = result.get(field)
            if declared and not (ROOT / declared).exists():
                found.append("%s names %s `%s`, which does not exist" % (name, field, declared))
    elif status == NOT_RUN:
        if not record.get("no_cells_run"):
            found.append("%s says %s but does not say no cell ran" % (name, NOT_RUN))
        if result:
            found.append("%s says %s but carries a result block" % (name, NOT_RUN))
    else:
        found.append("%s carries an unrecognised status %r" % (name, status))

    if auth.get("granted"):
        document = auth.get("document")
        if not auth.get("granted_on"):
            found.append("%s is granted with no grant date" % name)
        if not document:
            found.append("%s is granted with no authorisation document" % name)
            return found
        target = ROOT / document
        if not target.exists():
            found.append("%s names authorisation `%s`, which does not exist" % (name, document))
            return found
        text = target.read_text(encoding="utf-8")
        if record.get("prereg") and record["prereg"] not in text:
            found.append("`%s` does not name %s" % (document, record["prereg"]))
        quote = auth.get("quote")
        if quote and quote not in text:
            found.append("`%s` does not carry the recorded quote" % document)
    return found


def problems(text: str | None = None, records: list[dict] | None = None) -> list[str]:
    """Everything wrong with the published row, as a list of sentences."""
    found: list[str] = []
    try:
        expected = render(records)
    except (OSError, ValueError, KeyError) as exc:
        return ["could not render the conversion-block row: %s" % exc]

    if text is None:
        text = MANUAL.read_text(encoding="utf-8")
    try:
        current = region_of(text)
    except ValueError as exc:
        found.append("the manual: %s" % exc)
    else:
        if current != expected:
            found.append(
                "the manual's conversion-block row is stale; "
                "run python -m benchmarks.presence_block_status")

    for path, record in zip(RECORDS, records if records is not None else load_records()):
        found.extend(_state_problems(path, record))
    return found


def write(fragment: str | None = None) -> str:
    fragment = render() if fragment is None else fragment
    MANUAL.write_text(with_fragment(MANUAL.read_text(encoding="utf-8"), fragment), encoding="utf-8")
    return fragment


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the manual row against the records and each record against itself, without writing",
    )
    args = parser.parse_args(argv)

    if args.check:
        found = problems()
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("conversion blocks:", region_of(MANUAL.read_text(encoding="utf-8")))
        return 0

    print("conversion blocks:", write())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
