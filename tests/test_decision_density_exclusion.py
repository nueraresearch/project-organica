"""The adoption record must quote the committed result, not a remembered one.

Every figure it states is recomputed here from `docs/density_interaction_a2_result.json`, and the
scope sentences are asserted so a later edit cannot quietly widen the claim to behaviour or to the
descriptive slope.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "DECISION-DENSITY-EXCLUSION.md"
RESULT = ROOT / "docs" / "density_interaction_a2_result.json"
PREREG = ROOT / "docs" / "density_interaction_a2_prereg.json"


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def test_the_record_is_dated_recorded_and_not_an_implementation():
    flat = _flat()
    assert "**Date**: 2026-11-07" in flat.replace("*", "*")
    assert "RECORDED" in flat
    assert "NOT IMPLEMENTED" in flat
    assert "rule 2" in flat and "rule 30" in flat
    assert "No code changed with this record" in flat


def test_every_quoted_figure_is_the_result_s_own():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    flat = _flat()
    c1 = result["criteria"]["C1_sparse_level"]
    slope = result["criteria"]["descriptive_interaction"]
    exposure = result["criteria"]["exposure"]
    tokens = ["%.6f" % c1["mean"], "%.6f" % c1["interval"][0],
              "%.6f" % c1["interval"][1], "%.2f" % c1["bar"],
              "%d of %d" % (c1["seeds_positive"], c1["of"]),
              "%.6f" % slope["mean"], "%.6f" % slope["interval"][0],
              "%.6f" % slope["interval"][1],
              "%.6f" % exposure["sensitivity_sparse_mean"],
              "%d of %d" % (exposure["seeds_positive"], exposure["of"])]
    for token in tokens:
        assert token in flat, token
    assert str(result["cells"]) in flat
    assert result["gates"]["all_passed"] is True
    assert result["decision"]["verdict"] in flat.replace("\n", " ")


def test_the_decision_is_the_level_and_the_slope_is_refused_as_a_reason():
    flat = _flat()
    assert "sparse-end level" in flat
    assert "descriptive" in flat and "not judged" in flat
    assert "not the reason for this decision" in flat
    assert "not monotone" in flat
    assert "pinned" in flat


def test_the_scope_refuses_behaviour_generality_and_the_slope():
    flat = _flat()
    assert "does not cover" in flat
    assert "Behaviour." in flat
    assert "One world family" in flat
    assert "cap 20" in flat
    assert "must not be read as one" in flat


def test_the_withdrawn_admission_rule_is_not_revived():
    flat = _flat()
    assert "DECISION-ADMISSION-RULE.md" in flat
    assert "withdrawn" in flat
    assert "does not revive it" in flat


def test_the_predecessor_block_stays_held():
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    predecessor = json.loads((ROOT / "docs" / "density_interaction_prereg.json")
                             .read_text(encoding="utf-8"))
    assert predecessor["status"].startswith("HELD")
    assert prereg["held_predecessor"]["prereg"] == "DENSITY-INTERACTION-1"
    assert "stays held and unrun" in _flat()


def test_the_reversal_conditions_are_named():
    flat = _flat()
    assert "What would reverse this decision" in flat
    assert "loses" in flat and "replication on fresh seeds" in flat
    assert "Absence of a behavioural gain is not a reversal" in flat
