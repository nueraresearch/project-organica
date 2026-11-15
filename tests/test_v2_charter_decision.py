"""The V2 charter draft must be a draft: nothing authorised, and the untested-arm disclosure carried."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _decisions() -> list[dict]:
    return json.loads((DOCS / "decisions.json").read_text(encoding="utf-8"))["decisions"]


def _record() -> dict:
    return next(d for d in _decisions() if d["decision_id"] == "DECISION-V2-CHARTER")


def test_the_charter_is_pending_so_it_authorises_nothing() -> None:
    record = _record()
    assert record["status"] == "PENDING"
    assert record["superseded_by"] is None
    text = (DOCS / "DECISION-V2-CHARTER.md").read_text(encoding="utf-8")
    assert "DRAFT — AWAITING THE OWNER'S SIGNATURE" in text
    assert "commissions nothing" in text


def test_it_carries_the_untested_arm_and_the_three_lines() -> None:
    text = (DOCS / "DECISION-V2-CHARTER.md").read_text(encoding="utf-8")
    assert "No admissible test of H2 was ever run" in text
    for number in ("0.3438", "0.005647", "510 of 2,785", "180 of 200"):
        assert number in text, number
    assert "98.33%" in text
    assert "G13-D" in text


def test_it_leaves_the_frozen_engine_and_the_G13_D_authorisation_alone() -> None:
    text = (DOCS / "DECISION-V2-CHARTER.md").read_text(encoding="utf-8")
    assert "**Leaves untouched:** D2 of that decision" in text
    assert "no code, no cells, no engine change" in text
    assert "docs/engine_pin.json" in text


def test_a_question_tallies_it() -> None:
    registry = json.loads((DOCS / "research_question_registry.json").read_text(encoding="utf-8"))
    tallies = [q["id"] for q in registry["questions"]
               if "DECISION-V2-CHARTER.md" in q.get("decisions", [])]
    assert len(tallies) == 1
    question = next(q for q in registry["questions"] if q["id"] == tallies[0])
    assert question["status"] == "open"
    assert question["kind"] == "governance"
