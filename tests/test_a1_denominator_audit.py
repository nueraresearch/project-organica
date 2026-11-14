"""The denominator-resolution audit must flag only the under-resolved gates."""
import json

from benchmarks import a1_denominator_audit as audit


def test_audit_flags_c1_fallback_c7_and_c8():
    doc = audit.build()
    assert doc["summary"]["flagged"] == [
        "C1_path_separation — target-only fallback",
        "C1_path_separation — N=8 maximum-feasibility target-only",
        "C7_assertion_block — Y- blocked rows",
        "C7_assertion_block — N=8 maximum-feasibility Y- blocked rows",
        "C8_third_route — A-K- blocked rows",
        "C8_third_route — N=8 maximum-feasibility A-K- blocked rows",
    ]
    assert "C1_path_separation — expanded C4 denominator" in doc["summary"]["passed"]
    assert "C1_path_separation — N=8 maximum-feasibility expanded denominator" in doc["summary"]["passed"]
    assert "C4_no_interference — all cells" in doc["summary"]["passed"]
    assert "C4_no_interference — N=8 maximum-feasibility all cells" in doc["summary"]["passed"]
    assert len(doc["summary"]["not_applicable"]) == 5
    maximum = doc["inputs"]["maximum_feasibility"]
    assert maximum["n_targets"] == 8
    assert maximum["max_disjoint_targets_from_tag_vertices"] == 8
    assert maximum["feasible_seeds_with_eight_disjoint"] == 6
    c7 = [row for row in doc["gates"]
          if row["scenario"] == "N=8 maximum-feasibility Y- blocked rows"][0]
    c8 = [row for row in doc["gates"]
          if row["scenario"] == "N=8 maximum-feasibility A-K- blocked rows"][0]
    assert c7["denominator"] == 16 and c7["status"] == "FLAGGED"
    assert c7["smallest_step"] > c7["margin"]
    assert c8["denominator"] == 8 and c8["status"] == "FLAGGED"
    assert c8["smallest_step"] > c8["margin"]


def test_audit_artifact_and_self_test_are_current():
    assert audit.main(["--check"]) == 0
    assert audit.main(["--self-test"]) == 0


def test_audit_records_no_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "OUT_PATH", tmp_path / "audit.json")
    monkeypatch.setattr(audit, "PAGE_PATH", tmp_path / "audit.md")
    assert audit.write() == 0
    doc = json.loads((tmp_path / "audit.json").read_text(encoding="utf-8"))
    assert doc["summary"]["flagged"]
    assert "not_evidence" in doc
