"""The A1 board must agree with the decision index, in both directions.

Twice now the board was redrawn in conversation while `docs/A1-PRE-FREEZE-CHECKLIST.md` still asserted that no owner
choice remained open, and still quoted the N=4 multiplicity as the operative veto. The checklist is the artifact a
reader trusts, so the disagreement is checked rather than watched for: every `PENDING` A1 decision must appear as awaiting
signature, and a record that declares a number the operative design no longer produces must appear as open.
"""

from __future__ import annotations

import json
from pathlib import Path

LAYER = "static"

DOCS = Path(__file__).resolve().parents[1] / "docs"
CHECKLIST = DOCS / "A1-PRE-FREEZE-CHECKLIST.md"
INDEX = DOCS / "decisions.json"
POSTURE = DOCS / "DECISION-A1-C4-POSTURE.md"

STALE_SENTENCE = "No substantive owner choice remains open"


def _pending_a1() -> list[str]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    return sorted(entry["decision_id"] for entry in index["decisions"]
                  if entry["status"] == "PENDING" and entry["decision_id"].startswith("DECISION-A1"))


def _board(text: str) -> list[str]:
    """Rows of the board table, which is the first table under 'Where the tree stands'."""
    rows: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## Where the tree stands"):
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if inside and line.startswith("|") and not line.startswith("| ---") and "Branch" not in line:
            rows.append(line)
    return rows


def board_problems(text: str) -> list[str]:
    found: list[str] = []
    rows = _board(text)
    if not rows:
        return ["the board table is missing"]
    pending = _pending_a1()
    for decision in pending:
        hits = [row for row in rows if decision in row]
        if not hits:
            found.append("%s is pending but has no board row" % decision)
        elif not any("AWAITING SIGNATURE" in row or "NOT BLOCKING" in row for row in hits):
            found.append("%s is pending but neither awaits a signature nor says why not"
                         % decision)
    if pending and STALE_SENTENCE in text:
        found.append("the board claims no owner choice remains open while %d decisions are pending"
                     % len(pending))
    # A declared multiplicity the operative block cannot produce has to stay visible.
    posture = POSTURE.read_text(encoding="utf-8")
    if "324 deltas per seed" in posture and "DECISION-A1-COMPETENT-ESTIMAND" in pending:
        if not any("324" in row and "1,944" in row and "OPEN" in row for row in rows):
            found.append("the N=4 multiplicity is operative in an adopted record but not flagged open")
    for row in rows:
        for target in [part.split("](")[1].split(")")[0] for part in row.split("[")[1:]
                       if "](" in part]:
            if target.startswith("http") or target.startswith("#"):
                continue
            if not (DOCS / target).exists():
                found.append("board row links a missing document: %s" % target)
    return found


def test_the_board_agrees_with_the_index() -> None:
    found = board_problems(CHECKLIST.read_text(encoding="utf-8"))
    assert not found, found


def test_the_board_names_both_decisions_that_await_a_signature() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    pending = _pending_a1()
    assert "DECISION-A1-COMPETENT-ESTIMAND" in pending
    assert "DECISION-A1-C1-CEILING" in pending
    for decision in pending:
        assert any(decision in row for row in _board(text)), decision


def test_the_board_guard_can_fail() -> None:
    """A guard nobody has seen reject anything is not a guard."""
    text = CHECKLIST.read_text(encoding="utf-8")
    stale = text.replace("## Where the tree stands — 2026-11-15",
                         "## Where the tree stands — 2026-11-15\n\n**" + STALE_SENTENCE + ".**", 1)
    assert stale != text
    assert board_problems(stale), "a board claiming no open choice was accepted"

    rows = _board(text)
    dropped = next(row for row in rows if "DECISION-A1-COMPETENT-ESTIMAND" in row)
    assert board_problems(text.replace(dropped + "\n", "", 1)), "a missing board row was accepted"

    unmarked = dropped.replace("AWAITING SIGNATURE", "CLOSED").replace("NOT BLOCKING", "DONE")
    assert board_problems(text.replace(dropped, unmarked, 1)), \
        "a pending decision marked closed was accepted"
