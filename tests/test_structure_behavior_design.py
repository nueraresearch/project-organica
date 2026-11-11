"""The design record must state a level it can defend, and name no seed."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

from pathlib import Path
import re

from benchmarks.acquisition_compositional import (
    PHASE_RETENTION, PHASE_REVISION_TEST)

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs/STRUCTURE-BEHAVIOR-DESIGN.md"


def _doc():
    if not DOC.exists():
        import pytest
        pytest.skip("the design record has not been written yet")
    return DOC.read_text(encoding="utf-8")


def test_the_record_targets_prediction_and_refuses_causation():
    text = _doc()
    assert "Level 2" in text
    assert "not attempted here" in text or "not attempted" in text
    assert "predicts" in text
    # The causal sentence has to be absent as a claim, present as a refusal.
    assert "no causal" in text.lower()


def test_the_record_names_all_six_required_items():
    text = _doc()
    for needle in ("structural variable", "behavioral outcome",
                   "held-out", "generating configuration",
                   "Null", "Falsifier A", "Falsifier B", "independent reviewer"):
        assert needle.lower() in text.lower(), needle


def test_the_record_quotes_the_windows_it_imported():
    text = _doc()
    for phase in (PHASE_RETENTION, PHASE_REVISION_TEST):
        window = f"{phase[0]}\u2013{phase[1]}"
        assert window in text, window


def test_the_record_names_no_seed_from_any_unspent_block():
    text = _doc()
    numbers = {int(n) for n in re.findall(r"\b20\d{6}\b", text)}
    forbidden = set(range(20270406, 20270421)) | set(range(20261207, 20261227))
    assert not (numbers & forbidden), numbers & forbidden


def test_the_manual_points_at_the_record_and_the_journal_entry():
    manual = (ROOT / "docs/USER-MANUAL.md").read_text(encoding="utf-8")
    row = [l for l in manual.split("\n")
           if l.startswith("| 13 | **Settle the central scientific claim")]
    assert len(row) == 1
    assert "STRUCTURE-BEHAVIOR-DESIGN.md" in row[0]
    assert "Level 2" in row[0]
    assert "no seed" in row[0].lower()
    journal = (ROOT / "research-journal/phase_g_findings_20261021.md").read_text(encoding="utf-8")
    assert "## \u00a7138" in journal


def test_the_prior_result_is_quoted_and_kept_distinct():
    """The provenance result is the nearest prior test; its numbers come from the artifact."""
    import json
    text = _doc()
    prov = json.loads((ROOT / "docs/formation_provenance_study.json").read_text(encoding="utf-8"))
    assert "## 2a." in text
    for value in (prov["difference"], *prov["interval"]):
        assert f"{value:.6f}" in text, value
    for arm in prov["arms"].values():
        assert f"{arm['rate']:.4f}" in text, arm["rate"]
    assert "occurrence" in text and "response" in text
    assert "useful or reusable" in text


def test_the_two_independence_guards_are_stated():
    """Disjoint pairs are not independence; the size baseline and permutation are required."""
    text = _doc()
    assert "mechanical baseline" in text
    assert "permutation control" in text.lower()
    assert "interval must include zero" in text


def test_the_record_documents_how_to_verify_it():
    text = _doc()
    assert "## 9. Verifying this record" in text
    assert "docs/formation_provenance_study.json" in text
    assert "tests/test_structure_behavior_design.py" in text


def test_the_shared_instrument_limitation_is_in_the_limits_section():
    """The guards bound the shared-readout explanation; the record must say so where limits live."""
    text = _doc()
    limits = text.split("## 7.", 1)[1].split("## 8.", 1)[0]
    assert "shared instrument" in limits
    assert "bound" in limits
