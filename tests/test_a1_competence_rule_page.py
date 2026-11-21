"""The competence-rule reading page must cite records that bind, and must state no constants.

The page exists to say *which* record binds each part of the rule without becoming a second place
where the rule's numbers are kept. That is a checkable property, so it is checked: the links must
resolve, the records they name must be adopted rather than drafted, and the constants must not
appear at all.
"""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "A1-COMPETENCE-RULE-IN-FORCE.md"
INDEX = ROOT / "docs" / "decisions.json"

LITERALS = ("0.05", "N_min =", "17 rows", "3 selected")


def page() -> str:
    assert PAGE.exists(), "the reading page is missing"
    return PAGE.read_text(encoding="utf-8")


def decision_links(text: str) -> list[str]:
    return sorted(set(re.findall(r"\((DECISION-[A-Za-z0-9-]+\.md)\)", text)))


def statuses() -> dict[str, str]:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    return {entry["decision_id"]: entry["status"] for entry in data["decisions"]}


def constant_literals(text: str) -> list[str]:
    return [literal for literal in LITERALS if literal in text]


def test_the_page_cites_the_competence_contract() -> None:
    text = page()
    assert "DECISION-A1-C8-NMIN.md" in decision_links(text)
    assert "DECISION-A1-C1-UNIT.md" in decision_links(text)


BOUNDARY = "## What does not bind yet"


def sections(text: str) -> tuple[str, str]:
    """The binding half, and the *one* section listing what does not bind yet."""
    assert BOUNDARY in text, "the page no longer separates what binds from what does not"
    head, tail = text.split(BOUNDARY, 1)
    following = tail.split("\n## ", 1)[0]
    return head, following


def test_every_decision_it_calls_binding_is_adopted() -> None:
    """The binding half may cite only adopted records; the other half only unadopted ones."""
    binding, pending = sections(page())
    status = statuses()
    for target in decision_links(binding):
        assert status.get(target[: -len(".md")]) == "ADOPTED", target
    for target in decision_links(pending):
        assert status.get(target[: -len(".md")]) != "ADOPTED", \
            "%s is cited as not binding but is adopted; the page is stale" % target


def test_no_decision_is_on_both_sides() -> None:
    binding, pending = sections(page())
    assert set(decision_links(binding)) & set(decision_links(pending)) == set()


def test_the_draft_is_called_a_draft() -> None:
    text = page()
    assert "A1-C2-C8-COMPETENCE-RULE.md" in text
    assert "DRAFT" in text
    assert "does not bind yet" in text.lower()


def test_the_page_states_no_constants() -> None:
    """By-reference is a property, not a style: nothing here may restate a value."""
    assert constant_literals(page()) == []


def test_the_constant_detector_can_fail() -> None:
    """A guard that never fires is decoration, so the detector is proved on a doctored page."""
    doctored = page() + "\nThe floor is 17 rows per seed.\n"
    assert constant_literals(doctored) == ["17 rows"]


def test_the_page_says_what_it_cannot_do() -> None:
    text = page()
    assert "if this page and a record disagree" in text
    assert "What this page cannot tell you" in text
