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
    assert "Sign resolution, computed before seeds" in text
    assert "## 10. Rejection and acceptance" in text
    assert "reserved for a" in text and "Level 3 design" in text
    assert "98.33" in text and "10,000-replicate" in text


def test_the_request_letter_exists_and_cannot_be_sent_unfilled():
    root = Path(__file__).resolve().parent.parent
    letter = (root / "docs/REVIEW-REQUEST.md").read_text(encoding="utf-8")
    assert "github.com/nueraresearch/project-organica" in letter
    # the two inconvenient numbers have to be in front of the reviewer, not behind a link
    assert "48 worlds per configuration" in letter
    assert "floor, not a target" in letter
    assert "rejected" in letter.lower()
    # every artifact it names must exist
    for match in re.finditer(r"`(docs/[A-Za-z0-9_.\-/]+\.(?:md|json))`", letter):
        assert (root / match.group(1)).exists(), match.group(1)
    # the sender's fields are visibly unfilled, so the letter cannot go out by accident
    assert "[name]" in letter and "[sender name]" in letter


def test_the_package_carries_the_feasibility_result_and_a_pinned_record():
    root = Path(__file__).resolve().parent.parent
    package = (root / "docs/REVIEW-PACKAGE.md").read_text(encoding="utf-8")
    assert "sign_resolution_structure_behavior.json" in package
    assert "floor, not a target" in package
    assert "git checkout 1051313" in package
    art = json.loads((root / "docs/sign_resolution_structure_behavior.json").read_text(encoding="utf-8"))
    for row in art["attenuation"]["rows"]:
        cell = f"| {row['reliability']:.2f} | {row['measured_rho']:.2f} | {row['worlds_required']} |"
        assert cell in package, cell


def test_the_primer_is_plain_and_names_the_hard_parts():
    root = Path(__file__).resolve().parent.parent
    primer = (root / "docs/REVIEW-PRIMER.md").read_text(encoding="utf-8")
    art = json.loads((root / "docs/sign_resolution_structure_behavior.json").read_text(encoding="utf-8"))
    assert "One instrument produces both numbers" in primer
    assert "floor, not a target" in primer
    assert f"{art['verdict']['reference_n']} runs per setup" in primer
    assert f"{art['attenuation']['rows'][2]['worlds_required']} runs per setup" in primer
    assert '\"no\" is one of them' in primer
    for match in re.finditer(r"`(docs/[A-Za-z0-9_.\-/]+\.(?:md|json))`", primer):
        assert (root / match.group(1)).exists(), match.group(1)
    assert len(primer.split()) < 1100, len(primer.split())
