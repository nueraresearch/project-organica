"""The primitive's sizing estimate is reproducible and its page carries its own numbers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from benchmarks import v2_primitive_sizing as sizing

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs" / "v2_primitive_sizing.json"
DOC = ROOT / "docs" / "V2-PRIMITIVE-SIZING.md"


def _doc() -> dict:
    return json.loads(ART.read_text(encoding="utf-8"))


def test_the_artifact_matches_a_fresh_measurement() -> None:
    assert _doc() == sizing.build()


def test_the_arithmetic_is_consistent() -> None:
    doc = _doc()
    for row in doc["admission"].values():
        assert row["references"] == 3 * row["composites"]
        assert row["registry_rows"] == row["composites"]
    head = doc["headline"]
    assert head["composites"] == doc["admission"]["m>=2"]["composites"]
    assert head["primitive_bytes"] == head["pages"] * doc["world"]["page_size"]
    assert head["pair_table_bytes"] < head["store_bytes"]


def test_the_source_digest_names_the_current_identity_artifact() -> None:
    digest = hashlib.sha256((ROOT / "docs" / "v1_carrier_identity.json").read_bytes()).hexdigest()
    assert _doc()["source"]["sha256"] == digest


def test_the_page_is_rendered_from_the_artifact() -> None:
    assert DOC.read_text(encoding="utf-8") == sizing.render_doc(_doc())


def test_the_page_carries_the_measured_numbers() -> None:
    doc, head, text = _doc(), _doc()["headline"], DOC.read_text(encoding="utf-8")
    assert "PLANNING-ONLY ESTIMATE" in text
    assert "{%.0f}" % 0 not in text and "{" not in text
    for fragment in (f"{head['primitive_bytes']:,} bytes", str(head["composites"]),
                     f"{head['references']}", "m>=20", f"{head['pair_table_bytes']:,}"):
        assert fragment in text, fragment
    assert "page-bound" in text
