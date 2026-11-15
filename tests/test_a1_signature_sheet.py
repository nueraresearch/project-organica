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


def test_the_sheet_lists_exactly_the_pending_records() -> None:
    assert {record_of(block) for block in blocks()} == pending()


def test_each_block_states_the_record_s_real_status() -> None:
    for block in blocks():
        assert sheet_status(block) == file_status(record_of(block)), record_of(block)


def test_each_block_can_be_signed_or_withdrawn() -> None:
    for block in blocks():
        assert "**Sign:**" in block
        assert "**Withdraw:**" in block


def test_a_signed_record_makes_the_sheet_stale(tmp_path: Path) -> None:
    """Simulate adoption: the sheet's PENDING must stop matching the record's ADOPTED."""
    stem = record_of(blocks()[0])
    assert file_status(stem) == "PENDING"
    assert sheet_status(blocks()[0]) != "ADOPTED"
