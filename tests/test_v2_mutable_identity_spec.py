"""The primitive specification is planning-only and internally consistent."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "V2-MUTABLE-IDENTITY-SPEC.md"
SPEC = json.loads((ROOT / "docs" / "v2_mutable_identity_spec.json").read_text(encoding="utf-8"))


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_the_spec_is_planning_only() -> None:
    text = _text()
    assert SPEC["status"] == "PLANNING_ONLY"
    assert SPEC["authorises"] == []
    assert "PLANNING ONLY" in text
    assert "Nothing here is authorised" in text
    assert "does not amend V1".lower() in text.lower()
    assert "no authorisation to build" in text


def test_the_spec_covers_the_four_requested_semantics() -> None:
    text = _text()
    for heading in ("## 2. The object", "## 3. Identifier semantics", "## 5. Mutation semantics",
                    "## 6. The collision rule"):
        assert heading in text
    low = text.lower()
    for word in ("storage", "identifier", "ownership", "mutation"):
        assert word in low, word


def test_every_invariant_is_named_in_the_document() -> None:
    text = _text()
    for invariant in SPEC["identifier_invariants"] + SPEC["mutation_invariants"]:
        assert "`%s`" % invariant["id"] in text, invariant["id"]
    ids = [i["id"] for i in SPEC["identifier_invariants"] + SPEC["mutation_invariants"]]
    assert len(ids) == len(set(ids)) == 10


def test_the_primitives_cannot_be_built_by_accident() -> None:
    """A planning note must not be wired into the engine or adopted as a decision."""
    spec_name = "V2-MUTABLE-IDENTITY-SPEC"
    engine_hits = [p for p in (ROOT / "organica").rglob("*.py") if spec_name in p.read_text(encoding="utf-8")]
    assert not engine_hits, engine_hits
    decisions = json.loads((ROOT / "docs" / "decisions.json").read_text(encoding="utf-8"))
    adopted = [d["decision_id"] for d in decisions["decisions"]
               if d.get("status") == "ADOPTED" and "MUTABLE-IDENTITY" in d["decision_id"]]
    assert not adopted, adopted
    charter = (ROOT / "docs" / "DECISION-V2-CHARTER.md").read_text(encoding="utf-8")
    assert "V2-MUTABLE-IDENTITY-SPEC.md" in charter
    assert "planning only" in charter
