"""The cell report has one shape, and the shape is enforced before a cell exists."""
import copy

import pytest

from benchmarks import v2_first_cell_report as report


def test_the_template_is_current_and_check_writes_nothing():
    before = report.PAGE.read_bytes()
    assert report.main(["--check"]) == 0
    assert report.PAGE.read_bytes() == before


def test_the_label_is_derived_from_the_interval_and_a_contradiction_is_refused():
    assert report.derive_label(-0.002, -0.001) == "PASS"
    assert report.derive_label(-0.001, 0.001) == "BOOKKEEPING"
    assert report.derive_label(0.001, 0.002) == "REVERSAL"
    assert report.derive_label(-0.001, 0.0) == "BOOKKEEPING"
    assert report.derive_label(0.0, 0.001) == "BOOKKEEPING"

    result = report._fixture("PASS")
    result["interval"] = {"mean": 0.003, "lo": 0.0028, "hi": 0.0032,
                          "level": report.LEVEL, "resamples": report.RESAMPLES}
    errors = report.validate(result)
    assert any("contradicts interval" in error for error in errors), errors


def test_every_declared_seed_is_accounted_for():
    dropped = report._fixture("PASS")
    dropped["per_seed"] = dropped["per_seed"][:-1]
    assert any("declared seeds missing" in error for error in report.validate(dropped))

    duplicated = report._fixture("PASS")
    duplicated["per_seed"][-1]["seed"] = duplicated["per_seed"][0]["seed"]
    assert any("duplicated" in error for error in report.validate(duplicated))

    unreasoned = report._fixture("PASS")
    row = unreasoned["per_seed"][0]
    row.update({"measurable": False})
    for field in ("d", "d_B", "beta"):
        row.pop(field)
    assert any("exclusion reason" in error for error in report.validate(unreasoned))


def test_fewer_than_eight_measurable_seeds_voids_the_cell():
    result = report._fixture("BOOKKEEPING")
    for row in result["per_seed"][7:]:
        row.update({"measurable": False, "exclusion": "no held-out positives"})
        for field in ("d", "d_B", "beta"):
            row.pop(field)
    assert any("fewer than 8" in error for error in report.validate(result))

    result["outcome"] = "VOID"
    result["interval"] = None
    result["void"] = {"codes": ["SEEDS_MEASURABLE"], "detail": "seven measurable seeds"}
    assert report.validate(result) == []
    assert "No interval is reported" in report.render(result)


def test_beta_is_the_declared_grid_and_arm_a_selects_none():
    zero = report._fixture("PASS")
    zero["per_seed"][0]["beta"]["C"] = 0
    assert any("beta C must be one of" in error for error in report.validate(zero))

    missing = report._fixture("PASS")
    del missing["per_seed"][0]["beta"]["B"]
    assert any("beta must name B and C" in error for error in report.validate(missing))

    arm_a = report._fixture("PASS")
    arm_a["per_seed"][0]["beta"]["A"] = 1
    assert any("arm A selects no beta" in error for error in report.validate(arm_a))


def test_a_failed_gate_requires_void_and_its_code():
    result = report._fixture("PASS")
    result["gates"]["A3"]["status"] = "FAIL"
    assert any("requires VOID" in error for error in report.validate(result))

    result["outcome"] = "VOID"
    result["interval"] = None
    result["void"] = {"codes": ["A3_MUTATION"], "detail": "the mutation invariant failed"}
    assert report.validate(result) == []
    assert "`A3_MUTATION`" in report.render(result)

    wrong = copy.deepcopy(result)
    wrong["void"]["codes"] = ["SEEDS_MEASURABLE"]
    assert any("name no condition" in error for error in report.validate(wrong))


def test_gates_before_a_void_can_be_not_run():
    result = report._fixture("PASS")
    for gate in report.GATE_IDS:
        result["gates"][gate] = {"status": "NOT RUN", "evidence": "the scorer pin refused the run"}
    result["outcome"] = "VOID"
    result["interval"] = None
    result["scorer_pin_ok"] = False
    result["void"] = {"codes": ["SCORER_PIN", "GATES_NOT_RUN"], "detail": "the pinned digests did not match"}
    assert report.validate(result) == []
    assert "NOT RUN" in report.render(result)

    outside = report._fixture("PASS")
    outside["gates"]["A4"]["status"] = "NOT RUN"
    assert any("did not run requires VOID" in error for error in report.validate(outside))


def test_void_carries_no_interval():
    result = report._fixture("VOID")
    result["interval"] = {"mean": 0.0, "lo": -0.1, "hi": 0.1,
                          "level": report.LEVEL, "resamples": report.RESAMPLES}
    assert any("carries no interval" in error for error in report.validate(result))


def test_a_pass_states_the_committed_selection_bound():
    reference = report.selection_reference()
    text = report.render(report._fixture("PASS"))
    assert f"{reference['null_keys']:+.6f}" in text
    assert f"{reference['planted_keys']:+.6f}" in text
    assert f"{reference['share']:.2f}%" in text
    assert "at or below the largest measured selection advantage" in text

    reversal = report.render(report._fixture("REVERSAL"))
    assert "larger than the matched null cost" in reversal


def test_every_report_quotes_the_adopted_reading_verbatim():
    for label in report.LABELS:
        text = report.render(report._fixture(label))
        assert report.reading_quote(label) in text
        assert f"**Outcome:** `{label}`" in text


def test_void_reports_quote_no_effect():
    text = report.render(report._fixture("VOID"))
    assert "No interval is reported" in text
    assert "Not read (VOID)" in text
    assert "Mean `d_C − d_A`" not in text


@pytest.mark.parametrize("field", ["level", "resamples"])
def test_the_interval_rule_is_fixed(field):
    result = report._fixture("PASS")
    result["interval"][field] = 0.95 if field == "level" else 2000
    assert any(field in error for error in report.validate(result))
