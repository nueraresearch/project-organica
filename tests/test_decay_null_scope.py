"""The null's scope must be derived, not restated, and no wider than its gates.

Every count here is recomputed from the harness constants or from the reported
rejection pattern, so the record cannot drift from the grid it describes, and the
claim about the selection rule is checked against the rule's own source.
"""

import inspect
import json
import re
from pathlib import Path

from benchmarks import decay_confirmation as dc

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "decay_null_scope.json"
DOC = ROOT / "docs" / "DECAY-NULL-SCOPE.md"


def _artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _text():
    return DOC.read_text(encoding="utf-8")


def test_the_design_is_the_harness_design():
    art = _artifact()["design"]
    assert art["grid"] == list(dc.GRID)
    assert art["degrees"] == list(dc.DEGREES)
    assert art["calibration_seeds"] == list(dc.CALIBRATION_SEEDS)
    assert len(art["grid"]) * len(art["degrees"]) * len(art["calibration_seeds"]) * 2 == 448
    assert art["cells_total"] == 448
    assert art["cells_per_arm_per_tau"] == 32
    assert art["precision_floor"] == dc.PRECISION_FLOOR


def test_the_derived_sets_follow_from_the_reported_pattern():
    body = _artifact()
    per_tau = body["reported_rejections"]["per_tau"]
    grid = body["design"]["grid"]
    assert set(per_tau) == {str(t) for t in grid}
    live_ok = [t for t in grid if not any("liveness" in f for f in per_tau[str(t)])]
    prec_ok = [t for t in grid if not any("precision" in f for f in per_tau[str(t)])]
    derived = body["derived_from_reported_pattern"]
    assert derived["taus_with_no_reported_liveness_failure"] == live_ok
    assert derived["taus_with_no_reported_precision_failure"] == prec_ok
    assert derived["intersection"] == []
    assert derived["every_tested_tau_fails_at_least_one_gate"] is True
    assert derived["boundary_gap"] == [max(live_ok), min(prec_ok)]
    assert derived["gap_width"] == round(min(prec_ok) - max(live_ok), 4)


def test_the_document_quotes_the_derived_numbers():
    body = _artifact()
    derived = body["derived_from_reported_pattern"]
    text = _text()
    lo, hi = derived["boundary_gap"]
    assert f"**{body['design']['cells_total']}**" in text
    assert f"({lo}, {hi})" in text
    assert f"**{derived['gap_width']}**" in text
    assert f"**{derived['gap_midpoint']}**" in text
    assert "empty" in text
    assert "not decidable from this worktree" in text
    assert not re.search(r"\{[a-z_]+\}", text), "a template placeholder survived"


def test_the_selection_rule_description_matches_its_source():
    src = inspect.getsource(dc.choose_threshold)
    # The documented semantics: a None precision rejects, and there is no minimum size.
    assert 'row["precision"] is None' in src
    assert "MIN_STABLE_FOR_PRECISION" not in src
    text = _text()
    assert "no stable edges at all" in text
    assert "no such floor" in text


def test_the_absent_artifact_is_named_as_absent():
    art = _artifact()
    assert "docs/confirmation/calibration.json" in art["provenance"]["not_recomputable_here"]
    assert not (ROOT / "docs" / "confirmation" / "calibration.json").exists()
    assert "absent from this worktree" in _text()


def test_the_ratio_arm_pattern_is_not_claimed():
    text = _text()
    assert "For the **ratio control** the same argument cannot be made" in text
