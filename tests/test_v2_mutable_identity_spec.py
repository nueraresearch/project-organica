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


def test_every_open_question_carries_an_argued_recommendation() -> None:
    text = _text()
    recs = SPEC["recommendations"]
    assert len(recs) == 4
    for rec in recs:
        assert rec["chosen"] and rec["basis"] and rec["rejected"]
        assert rec["doc_anchor"] in text, rec["question"]
    assert "## 11. Recommendation summary" in text
    assert "members are edges, not tags" in text
    assert "recommendations for the charter" in text


def test_the_cycle3_acceptance_test_matches_the_measured_artifact() -> None:
    """The spec's acceptance criterion is arithmetic on the identity artifact, so check it there."""
    doc = json.loads((ROOT / "docs" / "v1_carrier_identity.json").read_text(encoding="utf-8"))
    mult = {int(k): v for k, v in doc["paths_per_node_set"].items()}
    assert sum(mult.values()) == doc["distinct_node_sets"]
    assert sum(k * v for k, v in mult.items()) == doc["distinct_paths"]
    assert mult == {1: 139, 2: 19}


def test_requirement_six_states_its_content_and_signs_with_the_resolutions() -> None:
    charter = (ROOT / "docs" / "DECISION-V2-CHARTER.md").read_text(encoding="utf-8")
    for phrase in ("composition-bearing", "content-free id", "copy-on-write at the level of **bindings**",
                   "total", "never reclaim an id", "signed together"):
        assert phrase in charter, phrase
    assert "adopts or rejects them explicitly" not in charter
    decisions = json.loads((ROOT / "docs" / "decisions.json").read_text(encoding="utf-8"))
    status = {d["decision_id"]: d["status"] for d in decisions["decisions"]}
    assert status["DECISION-V2-CHARTER"] == "PENDING"
    assert status["DECISION-V2-PRIMITIVE-RESOLUTIONS"] == "PENDING"


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
