"""The signature sheet must list exactly the A1 decisions that are still pending.

Its failure mode is quiet and expensive: a record gets signed, the sheet keeps saying "sign these three",
and the owner is asked to decide something already decided. So the sheet and the records are checked
against each other in both directions.
"""

from __future__ import annotations

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"
SHEET = DOCS / "A1-SIGNATURE-SHEET.md"


def blocks() -> list[str]:
    return re.split(r"\n## D\d — ", SHEET.read_text(encoding="utf-8"))[1:]


def record_of(block: str) -> str:
    found = re.search(r"\*\*Record:\*\* `([A-Z0-9-]+)`", block)
    assert found, block[:120]
    return found.group(1)


def sheet_status(block: str) -> str:
    found = re.search(r"\*\*Status:\*\* `([A-Z]+)", block)
    assert found, block[:120]
    return found.group(1)


def file_status(stem: str) -> str:
    text = (DOCS / ("%s.md" % stem)).read_text(encoding="utf-8")
    found = re.search(r"\*\*Status:\*\* `([A-Z]+)", text)
    assert found, stem
    return found.group(1)


def pending() -> set[str]:
    return {path.stem for path in DOCS.glob("DECISION-A1-*.md")
            if file_status(path.stem) == "PENDING"}


def test_the_sheet_lists_every_pending_record() -> None:
    listed = {record_of(block) for block in blocks()}
    assert pending() <= listed, pending() - listed
    assert listed == {"DECISION-A1-C1-CEILING", "DECISION-A1-C8-SELECTION",
                      "DECISION-A1-COMPETENT-ESTIMAND"}


def test_each_block_states_the_record_s_real_status() -> None:
    for block in blocks():
        assert sheet_status(block) == file_status(record_of(block)), record_of(block)


def test_each_block_says_what_a_signature_would_do() -> None:
    """A pending record carries its sign/withdraw lines; a signed one records the status it wrote."""
    for block in blocks():
        stem = record_of(block)
        if file_status(stem) == "PENDING":
            assert "**Sign:**" in block and "**Withdraw:**" in block, stem
        else:
            assert "**Signed 2026-11-15.**" in block, stem


def test_the_signed_blocks_name_the_status_line_they_wrote() -> None:
    """A reader must be able to check the sheet's claim against the record without opening two files."""
    for block in blocks():
        stem = record_of(block)
        if file_status(stem) == "ADOPTED":
            assert "ADOPTED BY OWNER 2026-11-15" in block, stem


def test_the_manual_says_what_is_waiting_on_the_owner() -> None:
    """The action list must name every pending A1 decision, so the block is visible where the owner looks."""
    manual = (DOCS / "USER-MANUAL.md").read_text(encoding="utf-8")
    start = manual.index("### 7.0 Waiting on you")
    block = manual[start:manual.index("### 7.1 Do today")]
    for stem in pending():
        assert stem in block, stem
    assert "A1-SIGNATURE-SHEET.md" in block
