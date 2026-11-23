"""The Q3 conversion-observer preregistration must stay frozen, neutral and falsifiable.

The record is unrun and unauthorised, the observer replaces one method and restores the cap,
the neutrality control is driven with identical, dropped and reordered arms so it is shown to
fire, and the loss rule is driven with a tie, a gain and a zero denominator.
"""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import copy
import inspect
import json
from types import SimpleNamespace

from benchmarks import presence_conversion_observer as O

BODY = O.prereg()


def _run(windows, asserted="a", present="p", s_ever="s", asserted_world="aw"):
    return {
        "present_fingerprint": present,
        "windows": windows,
        "s_ever_fingerprint": s_ever,
        "asserted_fingerprint": asserted,
        "asserted_world_fingerprint": asserted_world,
    }


def test_the_record_is_frozen_authorised_and_run():
    assert BODY["prereg"] == "PRESENCE-CONVERSION-1"
    assert BODY["status"] == "FROZEN, RUN"
    assert BODY["no_cells_run"] is False
    auth = BODY["authorisation"]
    assert auth["granted"] is True
    assert auth["granted_on"] == "2026-11-10"
    assert auth["quote"] == "Authorize all runs"
    assert auth["document"] == "docs/" + O.AUTHORISATION_DOC.name
    assert auth["scope"].startswith("all three frozen conversion blocks")
    assert O.authorisation_problems(BODY) == []
    assert O.ARTIFACT.exists(), "the authorised block ran and wrote its artifact"
    assert BODY["result"]["verdict"] == "OBSERVER NOT NEUTRAL"
    assert BODY["result"]["artifact"] == "docs/" + O.ARTIFACT.name
    assert O.check() == 0
    assert O.validate(BODY) == []


def test_the_observer_replaces_one_method_and_restores_the_cap():
    assert O.observer_overrides() == ["_build_predictions"]
    assert BODY["engine"]["overrides"] == ["_build_predictions"]
    assert BODY["engine"]["edit"] == "none"
    source = inspect.getsource(O.StageObserverSleepService._build_predictions)
    assert "super()._build_predictions" in source
    assert "finally" in source and "MAX_PREDICTIONS" in source
    assert "return full[:shipped]" in source
    assert O.SleepService.MAX_PREDICTIONS == 112
    assert BODY["observer"]["shipped_cap"] == BODY["build_superseded"]["recorded_cap"] == 40


def test_a_second_override_would_be_caught():
    class TwoMethods(O.StageObserverSleepService):
        def run_sleep_cycle(self):  # pragma: no cover - never called
            return None

    assert O.observer_overrides(TwoMethods) == ["_build_predictions", "run_sleep_cycle"]


def test_the_neutrality_control_passes_identical_arms_and_fails_a_changed_one():
    base = _run([[[("a", "b")], [("b", "c")]], [[("b", "c")]]])
    assert O.neutrality(base, copy.deepcopy(base))["neutral"] is True

    dropped = _run([[[("a", "b")]]])
    result = O.neutrality(base, dropped)
    assert result["neutral"] is False
    assert "admission windows" in result["differs"]

    reordered = _run([[[("b", "c")], [("a", "b")]], [[("b", "c")]]])
    result = O.neutrality(base, reordered)
    assert result["neutral"] is False and "admission windows" in result["differs"]

    asserted = dict(copy.deepcopy(base), asserted_fingerprint="different")
    result = O.neutrality(base, asserted)
    assert result["neutral"] is False and "final assertion" in result["differs"]

    presence = dict(copy.deepcopy(base), present_fingerprint="different")
    result = O.neutrality(base, presence)
    assert result["neutral"] is False and "presence fingerprint" in result["differs"]


def test_the_observer_record_carries_c_e_and_r_per_candidate():
    candidates = [
        SimpleNamespace(source="a", target="b", strength=0.5,
                        evidence={"count": 3, "ratio": 0.1}),
        SimpleNamespace(source="b", target="c", strength=0.25,
                        evidence={"count": 2, "ratio": 0.2}),
    ]
    rows = O.record_window(candidates, cap=1)
    assert [row["rank"] for row in rows] == [1, 2]
    assert [row["edge"] for row in rows] == [["a", "b"], ["b", "c"]]
    assert [row["admitted"] for row in rows] == [True, False]
    assert rows[0]["support"] == 3 and rows[1]["ratio"] == 0.2
    assert rows[0]["strength"] == 0.5


def test_eligibility_records_a_reason_for_every_present_edge():
    rows = [{"edge": ["a", "b"]}]
    temporal = {"a": {"b": 3}, "b": {"c": 1}}
    reasons = O.eligibility([("a", "b"), ("b", "c")], rows, temporal, min_count=2)
    assert reasons["a->b"] == "constructed"
    assert reasons["b->c"] == "below_prediction_min_count"
    # An edge that meets the minimum but has no candidate must be visible, not smoothed away.
    unexplained = O.eligibility([("a", "b"), ("b", "c")], rows,
                                {"a": {"b": 3}, "b": {"c": 5}}, min_count=2)
    assert unexplained["b->c"] == "unexplained"


def test_the_loss_rule_takes_the_largest_absolute_drop_and_the_earlier_tie():
    chain = O.loss_chain({"W": 112, "P": 112, "C": 90, "S_cycle": 40,
                          "S_ever": 60, "A_pred": 30})
    assert chain["absolute_drop"]["P->C"] == 22
    assert chain["absolute_drop"]["C->S_cycle"] == 50
    assert chain["absolute_drop"]["S_cycle->S_ever"] == -20
    assert chain["gains"] == ["S_cycle->S_ever"]
    assert chain["primary_suspect"] == "C->S_cycle"

    tie = O.loss_chain({"W": 100, "P": 100, "C": 90, "S_cycle": 80,
                        "S_ever": 80, "A_pred": 70})
    assert tie["absolute_drop"]["P->C"] == 10
    assert tie["absolute_drop"]["C->S_cycle"] == 10
    assert tie["absolute_drop"]["S_ever->A_pred"] == 10
    assert tie["primary_suspect"] == "P->C"


def test_a_zero_denominator_is_not_measurable_not_zero():
    chain = O.loss_chain({"W": 0, "P": 0, "C": 0, "S_cycle": 0,
                          "S_ever": 0, "A_pred": 0})
    assert chain["primary_suspect"] is None
    assert "P->C" in chain["not_measurable"]
    for step in chain["not_measurable"]:
        assert step not in chain["absolute_drop"]


def test_the_bypass_is_reported_and_never_counted_as_retention():
    chain = O.loss_chain({"W": 112, "P": 112, "C": 112, "S_cycle": 40,
                          "S_ever": 60, "A_pred": 30}, bypass=41)
    assert chain["bypass"] == 41
    assert chain["retained"]["A_pred"] == 30
    assert "A_other" not in chain["retained"]


def test_the_declared_stages_are_the_fields_the_observer_records():
    source = inspect.getsource(O.record_window)
    for field in ("rank", "edge", "strength", "admitted", "support", "ratio"):
        assert field in source, field
    for stage in ("C", "E", "R"):
        assert BODY["observer"]["records"][stage]


def test_the_witness_is_the_published_audit_row():
    witness = O.derived()["witness"]
    assert BODY["design"]["witness_cell"]["seed"] == witness["seed"] == 20261100
    assert BODY["design"]["witness_cell"]["arm"] == "off"
    assert BODY["gates"]["X8_control_reproduces_audit"]


def test_the_seed_block_is_fresh_and_the_check_can_fail():
    assert O.seed_fresh() == {}
    assert 20261100 in O.cap.seed_collisions([20261100], allow=(O.PREREG,))
    broken = copy.deepcopy(BODY)
    broken["status"] = "AUTHORISED"
    assert O.validate(broken), "a changed status must fail validation"
    broken = copy.deepcopy(BODY)
    broken["gates"].pop("X1_observer_neutral")
    assert any("X1" in problem for problem in O.validate(broken))


def test_the_page_is_current_and_the_gate_passes():
    assert O.DOC.read_text(encoding="utf-8") == O.render_prereg(BODY)
    assert O.check_prereg() == 0
    assert set(row["verdict"] for row in BODY["decision_table"]) == set(O.VERDICTS)


def test_the_ladder_prior_is_labelled_exploratory():
    assert "| presence-to-assertion ladder trace (exploratory) |" in O.render_prereg(O.prereg())
