"""The null's scope must be derived, not restated, and no wider than its gates.

Counts are recomputed from the harness constants or from the verified rejection
pattern, so the record cannot drift from the grid it describes; the claim about
the selection rule is checked against the rule's own source.
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


def _flat():
    """Prose wraps, so assertions about sentences must not depend on line breaks."""
    return " ".join(_text().split())


def test_the_design_is_the_harness_design():
    art = _artifact()["design"]
    seeds = list(dc.CALIBRATION_SEEDS)
    assert art["grid"] == list(dc.GRID)
    assert art["degrees"] == list(dc.DEGREES)
    assert "calibration_seeds" not in art, "seed integers would be harvested as consumed"
    assert f"{seeds[0]}-{seeds[-1]}" in art["calibration_block"]
    assert len(art["grid"]) * len(art["degrees"]) * len(seeds) * 2 == 448
    assert art["cells_total"] == 448
    assert art["cells_per_arm_per_tau"] == 32
    assert art["precision_floor"] == dc.PRECISION_FLOOR


def test_recording_the_design_does_not_consume_the_calibration_block():
    """A scope record must not make the harness refuse to run its own calibration."""
    assert not (set(dc.harvest_seeds()) & set(dc.CALIBRATION_SEEDS))


def test_the_derived_sets_follow_from_the_verified_pattern():
    body = _artifact()
    transition = body["reported_rejections"]["transition"]
    grid = body["design"]["grid"]
    assert set(transition) == {str(t) for t in grid}
    live = [t for t in grid if not any("liveness" in f for f in transition[str(t)])]
    prec = [t for t in grid if not any("precision" in f for f in transition[str(t)])]
    derived = body["derived_from_reported_pattern"]
    assert derived["transition_liveness_clean"] == live == [0.05, 0.075, 0.1]
    assert derived["transition_precision_clean"] == prec
    assert derived["intersection"] == []
    assert derived["every_tested_tau_fails_at_least_one_gate"] is True
    assert derived["crossing_interval"] == [max(live), min(prec)] == [0.1, 0.15]
    assert derived["gap_width"] == 0.05
    assert derived["gap_midpoint"] == 0.125


def test_the_ratio_arm_is_recorded_as_asserting_nothing_at_the_high_end():
    ratio = _artifact()["reported_rejections"]["ratio"]
    assert "no stable predictions" in ratio["at_or_above_0.20"]
    assert "None" in ratio["at_or_above_0.20"]


def test_the_correction_is_disclosed_not_silently_rewritten():
    correction = _artifact()["correction"]
    assert "0.15, 0.20" in correction["earlier_claim"]
    assert "0.10, 0.15" in correction["now"]
    assert "resolution artifact" in correction["effect_on_reading"]
    assert "unchanged" in correction["verdict"]
    assert "Correction (2026-11-07)" in _flat()


def test_the_document_quotes_the_derived_numbers():
    body = _artifact()
    derived = body["derived_from_reported_pattern"]
    text, flat = _text(), _flat()
    lo, hi = derived["crossing_interval"]
    assert f"**{body['design']['cells_total']}**" in text
    assert f"({lo}, {hi})" in flat
    assert f"**{derived['gap_midpoint']}**" in text
    assert "resolution artifact" in flat
    assert not re.search(r"\{[a-z_]+\}", text), "a template placeholder survived"


def test_the_selection_rule_description_matches_its_source():
    src = inspect.getsource(dc.choose_threshold)
    assert 'row["precision"] is None' in src
    assert "MIN_STABLE_FOR_PRECISION" not in src
    assert "no such floor" in _flat()


def test_the_artifact_is_named_as_absent_but_verified_elsewhere():
    provenance = _artifact()["provenance"]
    assert "docs/confirmation/calibration.json" in provenance["artifact"]
    assert "not recomputed in this worktree" in provenance["per_cell_readings"]
    assert not (ROOT / "docs" / "confirmation" / "calibration.json").exists()
