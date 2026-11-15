"""The board's decision half is generated, and stale rows must fail.

The earlier guard checked one direction: every pending decision had to appear on the board. A row
marked `CLOSED`, `ADOPTED` or `AWAITING SIGNATURE` could then survive its record changing, and no
check would notice — the same defect as the prose it replaced.

`benchmarks/a1_board` renders the block from `docs/decisions.json` and each record's own scope
line. These tests hold the two properties that make that useful:

* the committed block is the render — so a status change on disk fails the check until the board
  is regenerated, in both directions;
* the state of every row is a function of the index, never typed.
"""

from __future__ import annotations

import json
from pathlib import Path

from benchmarks import a1_board

LAYER = "static"

DOCS = Path(__file__).resolve().parents[1] / "docs"
CHECKLIST = DOCS / "A1-PRE-FREEZE-CHECKLIST.md"
STALE_SENTENCE = "No substantive owner choice remains open"


def _text() -> str:
    return CHECKLIST.read_text(encoding="utf-8")


def _entries() -> list[dict]:
    return json.loads((DOCS / "decisions.json").read_text(encoding="utf-8"))["decisions"]


def test_the_committed_block_is_the_render() -> None:
    found = a1_board.block_problems(_text())
    assert not found, found


def test_every_a1_decision_is_rendered_exactly_once() -> None:
    body = a1_board.block(_text())
    assert body is not None
    a1 = [entry for entry in _entries() if entry["decision_id"].startswith(a1_board.PREFIX)]
    assert len(a1) == 11
    for entry in a1:
        assert body.count("[`%s`]" % entry["decision_id"]) == 1, entry["decision_id"]


def test_row_states_are_a_function_of_the_index() -> None:
    body = a1_board.block(_text())
    for entry in _entries():
        if not entry["decision_id"].startswith(a1_board.PREFIX):
            continue
        row = next(line for line in body.splitlines() if "[`%s`]" % entry["decision_id"] in line)
        expected = a1_board._state(entry)
        assert "| %s |" % expected in row, (entry["decision_id"], expected, row)
    # The two signable drafts, and only those, are awaiting a signature.
    awaiting = [row["id"] for row in a1_board.rows() if row["state"] == "**AWAITING SIGNATURE**"]
    assert awaiting == ["DECISION-A1-C1-CEILING", "DECISION-A1-COMPETENT-ESTIMAND"]


def test_a_status_change_on_disk_makes_the_block_stale() -> None:
    """The direction the first guard could not see: a row outliving its status."""
    entries = json.loads(json.dumps(_entries()))
    target = next(entry for entry in entries
                  if entry["decision_id"] == "DECISION-A1-COMPETENT-ESTIMAND")
    target["status"] = "ADOPTED"
    target["status_quote"] = "ADOPTED BY OWNER 2026-11-15"
    found = a1_board.block_problems(_text(), entries)
    assert any("stale" in problem for problem in found), found


def test_a_dropped_row_is_a_missing_decision() -> None:
    body = a1_board.render()
    first = body.splitlines()[3]
    broken = a1_board.splice(_text(), body.replace(first + "\n", "", 1))
    assert a1_board.block_problems(broken)


def test_the_hand_maintained_table_keeps_its_two_invariants() -> None:
    text = _text()
    assert STALE_SENTENCE not in text
    assert "| **C1 denominator ceiling** |" not in text, "decision rows belong in the generated block"
    assert "324" in text and "1,944" in text and "OPEN UNTIL THE ESTIMAND IS ADOPTED" in text, \
        "an adopted record's multiplicity must stay visible while the estimand is pending"
    for target in [part.split("](")[1].split(")")[0] for part in text.split("[")[1:]
                   if "](" in part]:
        if target.startswith("http") or target.startswith("#"):
            continue
        # Anchors name a section, not a file: check the path before the '#'.
        path = target.split("#", 1)[0]
        assert (DOCS / path).exists(), target
