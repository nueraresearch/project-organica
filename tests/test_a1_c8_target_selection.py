"""The registered C8 expansion must supply 20 A-K- rows per seed without freezing."""
import json

from benchmarks import a1_c8_target_selection as c8
from benchmarks import a1_denominator_audit as audit


def test_c8_expansion_artifact_has_twenty_rows_per_seed():
    doc = json.loads(c8.OUT_PATH.read_text(encoding="utf-8"))
    assert c8.problems(doc) == []
    assert c8.check() == 0
    assert c8.self_test() == []
    assert doc["n_per_seed"] == 20
    assert doc["threshold"] == 0.05
    assert doc["threshold_changed"] is False
    for seed, row in doc["per_seed"].items():
        assert len(row["selected"]) == 20
        assert len(set(row["selected"])) == 20
        assert max(row["endpoint_degree"].values()) <= 3
        assert row["candidate_count"] >= 20
        assert row["eligible_count"] >= 20
        assert all(value is True for value in row["cycle_member"].values())
        assert all(value["strength"] > 0 for value in row["u"].values())


def test_c8_expansion_is_the_registered_n20_denominator():
    doc = audit.build()
    row = next(row for row in doc["gates"]
               if row["scenario"] == "registered N=20 C8 expansion")
    assert row["denominator"] == 20
    assert row["smallest_step"] == 0.05
    assert row["smallest_step"] <= row["margin"]
    assert row["status"] == "PASS"
    assert "C8_third_route — registered N=20 C8 expansion" not in doc["summary"]["flagged"]
    assert doc["denominator_unit"]["registered_design"]["n_per_seed"] == 20
    assert doc["denominator_unit"]["resolved"]["C8_N20"] is True


def test_c8_expansion_design_record_matches_artifact_and_stays_unfrozen():
    import json
    from pathlib import Path

    design = json.loads(Path("docs/a1_c8_expansion.json").read_text(encoding="utf-8"))
    artifact = json.loads(c8.OUT_PATH.read_text(encoding="utf-8"))
    assert design["kind"] == "a1_c8_expansion_design"
    assert design["id"] == c8.ID
    assert design["n_per_seed"] == 20
    assert design["disjoint"] is False
    assert design["max_endpoint_degree"] == 3
    assert design["threshold"] == 0.05
    assert design["threshold_changed"] is False
    assert design["not_a_result"] is True
    assert design["current_manifest_targets"]["n_per_seed"] == 4
    assert design["current_manifest_targets"]["changed"] is False
    assert set(design["per_seed"]) == set(artifact["per_seed"])
    for seed, row in design["per_seed"].items():
        assert row["selected_count"] == 20
        assert row["max_endpoint_degree"] <= 3
        assert row["selection_digest"] == artifact["per_seed"][seed]["selection_digest"]


def test_c8_n20_allows_one_assertion_and_rejects_two():
    from benchmarks.a1_gate_readiness import gate_c8

    rows = [{"seed": 1, "cell": "A-K-", "Y": index == 0} for index in range(20)]
    assert gate_c8(rows, 0.05) is True
    rows[1]["Y"] = True
    assert gate_c8(rows, 0.05) is False
