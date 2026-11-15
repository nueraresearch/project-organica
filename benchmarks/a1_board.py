"""Render the owner-decision half of the A1 board from `docs/decisions.json`.

The checklist's board used to be hand-written prose that a test audited in one direction only:
every pending decision had to appear, but a row marked closed could survive its record being
adopted, amended or withdrawn and every check would still pass.  Half of that board is derivable,
so it is now derived rather than described:

* the **state** comes from `status` — and for an open entry, from whether its `status_quote` says
  it is *for owner adoption*, which is what distinguishes a signable draft from an entry that is
  pending with nothing left to sign;
* the **link** comes from the decision id;
* what the row **decides** comes from the record's own `**Scope:**` line, falling back to its title.

Nothing about a decision row is typed by hand.  `--check` re-renders and compares the block in
place, so a status change on disk makes the board stale until it is regenerated — which is the
direction the earlier guard could not see.

    python -m benchmarks.a1_board --write
    python -m benchmarks.a1_board --check
    python -m benchmarks.a1_board --self-test
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX_PATH = DOCS / "decisions.json"
CHECKLIST_PATH = DOCS / "A1-PRE-FREEZE-CHECKLIST.md"
START = "<!-- a1-board:start -->"
END = "<!-- a1-board:end -->"
PREFIX = "DECISION-A1"
SCOPE_LIMIT = 210


def _index() -> dict:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def _text(decision_id: str) -> str:
    return (DOCS / ("%s.md" % decision_id)).read_text(encoding="utf-8")


def _clip(text: str) -> str:
    text = " ".join(text.replace("|", "/").split())
    if text:
        text = text[0].upper() + text[1:]
    if len(text) <= SCOPE_LIMIT:
        return text
    window = text[:SCOPE_LIMIT]
    # Prefer a sentence end, then a word end, so a cell rarely stops mid-clause.
    for cut in (window.rfind(". "), window.rfind("; "), window.rfind(" ")):
        if cut > SCOPE_LIMIT // 2:
            return window[:cut].rstrip(",;:.") + " …"
    return window.rstrip(",;:") + " …"


def _scope(decision_id: str) -> str:
    """The record's own statement of what it decides, else its title."""
    text = _text(decision_id)
    match = re.search(r"^\*\*Scope:\*\*\s*(.+?)(?=\n\s*\n)", text, re.M | re.S)
    if match:
        return _clip(match.group(1))
    title = re.search(r"^#\s+(.+)$", text, re.M)
    if not title:
        return "—"
    return _clip(re.sub(r"\s+—\s+(decision record|a decision record).*$", "", title.group(1)))


def _state(entry: dict) -> str:
    status = entry.get("status")
    if status == "ADOPTED":
        return "**ADOPTED**"
    if status == "WITHDRAWN":
        return "**WITHDRAWN**"
    if "FOR OWNER ADOPTION" in (entry.get("status_quote") or ""):
        return "**AWAITING SIGNATURE**"
    return "**PENDING — NOT BLOCKING**"


def _rank(entry: dict) -> tuple:
    state = _state(entry)
    order = {"**AWAITING SIGNATURE**": 0, "**PENDING — NOT BLOCKING**": 1,
             "**WITHDRAWN**": 2, "**ADOPTED**": 3}[state]
    return (order, entry.get("date") or "", entry["decision_id"])


def rows(entries: list[dict] | None = None) -> list[dict]:
    entries = entries if entries is not None else _index()["decisions"]
    a1 = [entry for entry in entries if entry["decision_id"].startswith(PREFIX)]
    return [{"id": entry["decision_id"], "state": _state(entry), "date": entry.get("date"),
             "scope": _scope(entry["decision_id"])} for entry in sorted(a1, key=_rank)]


def _non_a1_pending(entries: list[dict]) -> list[str]:
    return sorted(entry["decision_id"] for entry in entries
                  if entry["status"] == "PENDING"
                  and not entry["decision_id"].startswith(PREFIX))


def render(entries: list[dict] | None = None) -> str:
    """The block that lives between the markers, markers excluded."""
    entries = entries if entries is not None else _index()["decisions"]
    table = rows(entries)
    counts = {state: sum(1 for row in table if row["state"] == state)
              for state in ("**AWAITING SIGNATURE**", "**PENDING — NOT BLOCKING**",
                            "**WITHDRAWN**", "**ADOPTED**")}
    header = ("**Owner decisions** — %d A1 records in `docs/decisions.json`: %d adopted, %d withdrawn, "
              "%d awaiting signature, %d pending and blocking nothing. Generated from the index and each "
              "record's own scope line; a status change on disk makes this block stale until it is "
              "regenerated." % (len(table), counts["**ADOPTED**"], counts["**WITHDRAWN**"],
                                counts["**AWAITING SIGNATURE**"],
                                counts["**PENDING — NOT BLOCKING**"]))
    lines = [header, "",
             "| Decision | State | What it decides |",
             "| --- | --- | --- |"]
    for row in table:
        lines.append("| [`%s`](%s.md) | %s | %s |"
                     % (row["id"], row["id"], row["state"], row["scope"]))
    outside = _non_a1_pending(entries)
    if outside:
        lines += ["", "_Also `PENDING` in the index, outside A1 (`PENDING` is not an open question; these are decided "
                  "and not in force): %s._" % ", ".join("`%s`" % name for name in outside)]
    return "\n".join(lines)


def _span(text: str) -> tuple[int, int] | None:
    if text.count(START) != 1 or text.count(END) != 1:
        return None
    start = text.index(START) + len(START)
    end = text.index(END)
    if end < start:
        return None
    return start, end


def block(text: str) -> str | None:
    span = _span(text)
    if span is None:
        return None
    return text[span[0]:span[1]].strip("\n")


def splice(text: str, body: str) -> str:
    span = _span(text)
    if span is None:
        raise ValueError("the checklist has no single %s / %s pair" % (START, END))
    return text[:span[0]] + "\n" + body + "\n" + text[span[1]:]


def block_problems(text: str, entries: list[dict] | None = None) -> list[str]:
    found: list[str] = []
    span = _span(text)
    if span is None:
        return ["the board markers are missing, duplicated or out of order"]
    current = block(text)
    expected = render(entries)
    if current != expected:
        found.append("the generated decision block is stale against docs/decisions.json")
    entries = entries if entries is not None else _index()["decisions"]
    for entry in entries:
        if not entry["decision_id"].startswith(PREFIX):
            continue
        occurrences = (current or "").count("[`%s`]" % entry["decision_id"])
        if occurrences != 1:
            found.append("%s appears %d times in the generated block, not once"
                         % (entry["decision_id"], occurrences))
    return found


def written_text() -> str:
    text = CHECKLIST_PATH.read_text(encoding="utf-8")
    return splice(text, render())


def write() -> int:
    text = CHECKLIST_PATH.read_text(encoding="utf-8")
    try:
        updated = splice(text, render())
    except ValueError as error:
        print("FAIL:", error)
        return 1
    CHECKLIST_PATH.write_text(updated, encoding="utf-8")
    print("wrote the decision block into %s" % CHECKLIST_PATH.name)
    print("  " + render().splitlines()[0])
    return 0


def check() -> int:
    text = CHECKLIST_PATH.read_text(encoding="utf-8")
    found = block_problems(text)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    table = rows()
    print("A1 board: clean; %d A1 records, %d awaiting signature"
          % (len(table), sum(1 for row in table if row["state"] == "**AWAITING SIGNATURE**")))
    return 0


def self_test() -> list[str]:
    found: list[str] = []
    entries = _index()["decisions"]
    text = CHECKLIST_PATH.read_text(encoding="utf-8")
    if block_problems(text, entries):
        found.append("the committed checklist was rejected: %s" % block_problems(text, entries))
    # A status flip on disk must make the block stale: this is the direction the old guard missed.
    flipped = json.loads(json.dumps(entries))
    target = next(entry for entry in flipped
                  if entry["decision_id"] == "DECISION-A1-C1-CEILING")
    target["status"] = "ADOPTED"
    target["status_quote"] = "ADOPTED"
    if not block_problems(text, flipped):
        found.append("an adopted decision left its AWAITING SIGNATURE row in place")
    # A dropped row is a missing decision.
    body = render(entries)
    first_row = body.splitlines()[3]
    trimmed = splice(text, body.replace(first_row + "\n", "", 1))
    if not block_problems(trimmed, entries):
        found.append("a missing decision row was accepted")
    # Duplicated markers make the block unlocatable.
    if not block_problems(text.replace(END, END + "\n" + END, 1), entries):
        found.append("duplicated markers were accepted")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.check:
        return check()
    found = self_test()
    for problem in found:
        print("FAIL:", problem)
    if not found:
        print("A1 board: self-test clean")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
