"""The package must name five components, cite only real artifacts, and quote real numbers."""

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "docs/REVIEW-PACKAGE.md"
PROTOCOL = ROOT / "docs/STRUCTURE-BEHAVIOR-DESIGN.md"


def _text():
    if not PKG.exists():
        import pytest
        pytest.skip("the package cover sheet has not been written yet")
    return PKG.read_text(encoding="utf-8")


def test_the_five_components_are_present_with_paths():
    text = _text()
    for component in ("Experimental protocol", "Prior evidence summary",
                      "Relevant artifacts", "Reviewer rubric", "Review report"):
        assert component in text, component
    assert "STRUCTURE-BEHAVIOR-DESIGN.md" in text
    assert "INDEPENDENT-METHODS-REVIEW.md" in text


def test_every_cited_artifact_exists():
    text = _text()
    paths = set(re.findall(r"`((?:docs|benchmarks|tests)/[^`]+)`", text))
    assert paths
    missing = sorted(p for p in paths if not (ROOT / p).exists())
    assert not missing, missing


def test_the_prior_evidence_numbers_come_from_the_artifact():
    text = _text()
    prov = json.loads((ROOT / "docs/formation_provenance_study.json").read_text(encoding="utf-8"))
    assert f"{prov['difference']:.6f}" in text
    for bound in prov["interval"]:
        assert f"{bound:.6f}" in text
    assert "0.4111" in text and "0.9846" in text


def test_the_package_does_not_claim_a_result():
    text = _text()
    assert "No result from the protocol exists" in text
    assert "No draft paper" in text


def test_the_protocol_has_its_nine_elements_and_can_reject():
    text = PROTOCOL.read_text(encoding="utf-8")
    for section in ("## 0. What this document is", "## 1.", "## 2.", "## 3.",
                    "## 6.", "## 7.", "## 10."):
        assert section in text, section
    assert "Spearman rank" in text
    assert "Sign resolution, required before seeds" in text
    assert "## 10. Rejection and acceptance" in text
    assert "reserved for a" in text and "Level 3 design" in text
    assert "98.33" in text and "10,000-replicate" in text
