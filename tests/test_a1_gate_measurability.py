"""A1 gates must fail on an unmeasurable input, never read it as a pass."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

from benchmarks.a1_gate_readiness import (  # noqa: E402
    C1_MIN, C7_MAX, C8_MAX, fixture, gate_c1, gate_c2, gate_c7, gate_c8)


def _with(cell, field, value):
    return [dict(row, **{field: value}) if row["cell"] == cell else row
            for row in fixture()]


def test_the_fixture_still_passes_every_gate():
    """The repair must not make a measurable fixture fail."""
    rows = fixture()
    assert gate_c1(rows, C1_MIN)
    assert gate_c2(rows)
    assert gate_c7(rows, C7_MAX)
    assert gate_c8(rows, C8_MAX)


def test_c1_does_not_read_a_nan_flag_as_retained():
    """``nan`` is truthy, so a bare ``if row[field]`` counts it as a pass."""
    assert gate_c1(_with("A-K+", "K", float("nan")), C1_MIN) is False


def test_c1_does_not_read_a_null_flag_as_retained_or_lost_by_accident():
    assert gate_c1(_with("A-K+", "K", None), C1_MIN) is False


def test_c2_does_not_read_a_null_path_as_a_zeroed_path():
    """C2 wants A driven to zero; ``not None`` is True, which fakes it."""
    assert gate_c2(_with("A-K+", "A", None)) is False
    assert gate_c2(_with("A+K-", "K", None)) is False
    assert gate_c2(_with("Y_MINUS_A+K+", "Y", None)) is False
    assert gate_c2(_with("Y_MINUS_A+K+", "A", None)) is False


def test_c8_does_not_read_a_null_control_as_non_assertion():
    """C8 is a positive control: an unmeasured row must not read as 0% asserted."""
    assert gate_c8(_with("A-K-", "Y", None), C8_MAX) is False
    assert gate_c8(_with("A-K-", "Y", float("nan")), C8_MAX) is False


def test_c7_does_not_read_a_non_finite_delta_as_within_tolerance():
    assert gate_c7(_with("Y_MINUS_A+K+", "delta_from_baseline",
                         {"A": float("nan"), "K": 0.0}), C7_MAX) is False
    assert gate_c7(_with("Y_MINUS_A+K+", "delta_from_baseline",
                         {"A": 0.0, "K": float("inf")}), C7_MAX) is False


def test_c7_refuses_a_null_delta_instead_of_crashing():
    assert gate_c7(_with("Y_MINUS_A+K+", "delta_from_baseline",
                         {"A": None, "K": 0.0}), C7_MAX) is False


def test_c7_refuses_a_delta_that_is_missing_a_path():
    assert gate_c7(_with("Y_MINUS_A+K+", "delta_from_baseline",
                         {"A": 0.0}), C7_MAX) is False


def test_c7_does_not_read_a_nan_y_flag_as_lowering_assertion():
    assert gate_c7(_with("Y_MINUS_A+K+", "Y", float("nan")), C7_MAX) is False
