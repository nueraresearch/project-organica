"""The structural model is a claim about the code, so the code can refute it."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _model() -> dict:
    return json.loads((DOCS / "v1_structural_model.json").read_text(encoding="utf-8"))


def _text() -> str:
    return (DOCS / "V1-STRUCTURAL-MODEL.md").read_text(encoding="utf-8")


def _source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_the_schema_is_the_one_the_model_describes() -> None:
    memory = _source("organica/memory.py")
    declared = set(re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", memory))
    described = {table["name"] for table in _model()["tables"]}
    assert declared == described, (declared - described, described - declared)


def test_there_is_still_no_retrieval_by_identifier() -> None:
    """The model's central claim: ids exist, addresses do not. Add one and this fails."""
    memory = _source("organica/memory.py")
    assert "WHERE id" not in memory
    assert "def get_event" not in memory
    assert "uuid.uuid4()" in memory, "the event id is a random uuid, not a content address"
    retrieval = _model()["retrieval"]
    assert {entry["surface"] for entry in retrieval} == {"recent", "search", "prior payloads"}


def test_structures_are_still_recomputed_rather_than_fetched() -> None:
    extraction = _source("organica/sleep_extraction.py")
    assert "def _build_loops" in extraction
    assert "def canonical_cycle" in extraction
    assert '_make_id("loop"' in extraction
    candidates = _source("organica/candidates.py")
    assert "hashlib.sha256" in candidates


def test_the_carrier_block_is_still_a_filter_on_path_content() -> None:
    arms = _source("benchmarks/a1_arms.py")
    assert "def carrier_filter" in arms
    assert "any(edge in pairs or (edge[1], edge[0]) in pairs for edge in blocked)" in arms
    model = _model()["manipulation"]["carrier_block"]
    assert model["mutates_store"] is False


def test_the_document_states_its_scope_and_its_limits() -> None:
    text = _text()
    for heading in ("What object is actually stored?", "What object is actually retrieved?",
                    "What object is actually manipulated?", "Can those ever be distinct?",
                    "Does the architecture contain a true addressing primitive anywhere?"):
        assert heading in text, heading
    assert "**No — no explicit one.**" in text
    assert "**explicit** address" in text
    assert "**functional** address" in text
    assert "satisfy the charter's mutable-identity requirement" in text


def test_the_identity_result_matches_its_artifact() -> None:
    doc = json.loads((DOCS / "v1_carrier_identity.json").read_text(encoding="utf-8"))
    text = _text()
    assert "Diachronic identity** | **no**" in text
    assert "**Selection** | yes, within a cycle" in text
    assert str(doc["distinct_paths"]) in text
    assert str(doc["node_sets_with_two_directions"]) in text
    assert doc["stable_identity_across_cycles"] is False
    assert doc["node_sets_where_both_directions_share_a_cycle"] == 0
    assert doc["identical_including_cycle"] is True
    labels = {claim["id"]: claim["label"] for claim in _model()["claims"]}
    assert labels["derived-address-synchronic"] == "MEASURED"
    assert labels["no-diachronic-identity"] == "MEASURED"
    assert "derived-address-open" not in labels
    assert "## In one paragraph" in text
    assert "expected from the architecture alone" in text
    assert "It does **not** say nothing is stored" in text
    assert "does **not** convert the measured magnitudes into derivations" in text
    assert "void for that build" in text


def test_the_spill_is_labelled_a_derivation_and_its_numbers_as_measurements() -> None:
    text = _text()
    assert "The spill is a theorem, given the representation" in text
    assert "What is **empirical** is the magnitude" in text
    labels = {claim["id"]: claim["label"] for claim in _model()["claims"]}
    assert labels["spill-is-a-theorem"] == "DERIVED"
    assert labels["spill-magnitude"] == "MEASURED"
    assert labels["readout-consistency"] == "ARGUMENT"
    assert labels["derived-address-synchronic"] == "MEASURED"
    assert labels["no-diachronic-identity"] == "MEASURED"


def test_the_identity_check_is_reproducible() -> None:
    doc = json.loads((DOCS / "v1_carrier_identity.json").read_text(encoding="utf-8"))
    assert doc["identical_including_cycle"] is True
    assert doc["paths_per_node_set"] == {"1": 139, "2": 19}
    assert doc["id_is_injective"] is True
    assert doc["id_is_invertible"] is False
    assert doc["distinct_paths"] == 177


def test_no_committed_artifact_retains_carrier_identity() -> None:
    """If a carrier id ever lands in the archive, the model's persistence claim needs revisiting."""
    pattern = re.compile(r"^loop_[0-9a-f]{8}$")
    offenders = []
    for path in DOCS.glob("*.json"):
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(path.name)
    assert not offenders, offenders
    assert _model()["record_scan"]["artifacts_with_loop_id"] == 0
    assert "The record cannot name a carrier either" in _text()


def test_the_falsifiers_are_named() -> None:
    falsifiers = _model()["falsifiers"]
    assert len(falsifiers) == 4
    assert any("derived" in item.lower() for item in falsifiers)
    assert any("stable identifier" in item for item in falsifiers)
    assert any("0.3438" in item for item in falsifiers)
    assert "What would refute it" in _text()
