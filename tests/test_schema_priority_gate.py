"""The schema-priority gate stays a bounded, post-hoc ranking diagnostic."""
LAYER = "static"

from benchmarks import schema_priority_gate as gate


def test_artifact_is_current_and_gate_retains_strong_seats():
    assert gate.main(["--check"]) == 0
    art = gate._load(gate.ARTIFACT)
    assert art["posthoc"] is True
    assert art["prereg"] is None
    s = art["summary"]
    assert s["schema_rows"] == 1816
    assert s["ungated"]["schema_seats"] == 1816
    assert s["gated"]["schema_seats"] == 1400
    assert s["gated"]["weak_priority_seats"] == 0
    assert s["gate_effect"]["strong_schema_seats_lost"] == 0
    assert all(s["checks"].values())


def test_gate_endpoints_reproduce_ungated_and_no_priority():
    sweep = {row["gate"]: row for row in
             gate._load(gate.ARTIFACT)["summary"]["threshold_sweep"]}
    assert sweep[5]["schema_seats"] == 1816
    assert sweep[5]["priority_seats"] == 1434
    assert sweep[10]["schema_seats"] == 1400
    assert sweep[999]["schema_seats"] == 382
    assert sweep[999]["priority_seats"] == 0


def test_gate_removes_priority_not_admissibility():
    art = gate._load(gate.ARTIFACT)
    e = art["summary"]["gate_effect"]
    assert e["weak_priority_removed"] == 395
    assert e["weak_schema_seats_remaining"] == 147
    assert e["weak_remaining_on_merit"] == 147
    assert e["non_schema_seats_returned"] == 416
