"""C4 must fail when the treated non-target stream is absent or short.

The gate's own document says an absent, incomplete or unmeasurable non-target stream is
``C4_UNMEASURABLE``.  Until this repair it could not fire on the first two: the control cell's
rows were compared against themselves, so a treated cell that emitted **no** non-target rows
still produced a passing population of tautological zeros, and a treated cell that emitted one
edge of five was judged on that one edge alone.

These tests are the proof of repair, so they are written to fail on the old behaviour: the absent
and short cases both passed before it.
"""

from __future__ import annotations

from benchmarks.a1_arms import score_c4

LAYER = "static"


def _row(cell: str, edge: str, a: float = 0.5, k: float = 0.5, y: float = 0.5) -> dict:
    return {"seed": 1, "cell": cell, "edge": edge, "target": False,
            "A_rate": a, "K_rate": k, "Y_rate": y,
            "delta_status": "AWAITING_PAIRED_CONTROL", "control_A": False, "control_K": False}


def _control(count: int = 5) -> dict:
    return {"seed": 1, "cell": "A+K+",
            "neighbor_rows": [_row("A+K+", "u%d>v%d" % (i, i)) for i in range(count)]}


def _treated(edges: list[str], a: float = 0.5, k: float = 0.5, y: float = 0.5) -> dict:
    return {"seed": 1, "cell": "A-K+",
            "neighbor_rows": [_row("A-K+", edge, a, k, y) for edge in edges]}


def test_an_absent_treated_stream_cannot_pass() -> None:
    report = score_c4([_control(), _treated([])])
    assert report["pass"] is False
    assert report["measured"] == 0
    assert report["rows"] == 5, "the five control edges are judged, not skipped"
    assert {item["reason"] for item in report["unmeasured"]} == {"AWAITING_TREATED_ROW"}


def test_a_short_treated_stream_cannot_pass() -> None:
    report = score_c4([_control(), _treated(["u0>v0"])])
    assert report["pass"] is False
    assert report["measured"] == 1
    missing = sorted(item["edge"] for item in report["unmeasured"])
    assert missing == ["u1>v1", "u2>v2", "u3>v3", "u4>v4"]


def test_a_complete_stream_within_tolerance_passes() -> None:
    edges = ["u%d>v%d" % (i, i) for i in range(5)]
    report = score_c4([_control(), _treated(edges)])
    assert report["pass"] is True
    assert report["measured"] == 5
    assert report["unmeasured"] == []


def test_the_control_is_never_scored_against_itself() -> None:
    edges = ["u%d>v%d" % (i, i) for i in range(5)]
    payloads = [_control(), _treated(edges)]
    report = score_c4(payloads)
    assert report["control_rows"] == 5
    for row in payloads[0]["neighbor_rows"]:
        assert row["delta_status"] == "CONTROL_NOT_SCORED"
        assert "neighbor_delta" not in row, "a self-comparison must not produce a delta"
    assert report["measured"] == len(edges), "only treated rows are measurements"


def test_a_measured_violation_still_fails() -> None:
    edges = ["u%d>v%d" % (i, i) for i in range(4)] + ["u4>v4"]
    payloads = [_control(), _treated(edges)]
    payloads[1]["neighbor_rows"][2]["A_rate"] = 0.9
    report = score_c4(payloads)
    assert report["pass"] is False
    assert report["violations"] and report["violations"][0]["path"] == "A"


def test_a_treated_edge_outside_the_control_fails() -> None:
    edges = ["u%d>v%d" % (i, i) for i in range(5)] + ["z9>q9"]
    report = score_c4([_control(), _treated(edges)])
    assert report["pass"] is False
    reasons = {item["reason"] for item in report["unmeasured"]}
    assert "AWAITING_PAIRED_CONTROL" in reasons


def test_a_gate_with_no_judged_rows_cannot_pass() -> None:
    """A population made only of control rows is empty as a comparison."""
    from benchmarks.a1_gate_readiness import gate_c4

    control_only = [dict(row, neighbor_delta={"A": 0.0, "K": 0.0, "Y": 0.0},
                         delta_status="CONTROL_NOT_SCORED")
                    for row in _control(3)["neighbor_rows"]]
    assert gate_c4(control_only, 0.05) is False
    assert gate_c4([], 0.05) is False
    assert gate_c4(control_only, None) is False
