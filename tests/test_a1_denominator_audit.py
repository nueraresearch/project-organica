"""The denominator-resolution audit must flag only the under-resolved gates."""
import json

from benchmarks import a1_denominator_audit as audit


def test_audit_flags_c1_fallback_c7_and_c8():
    doc = audit.build()
    assert doc["summary"]["flagged"] == [
        "C1_path_separation — target-only fallback",
        "C7_assertion_block — Y- blocked rows",
        "C8_third_route — A-K- blocked rows",
    ]
    assert "C1_path_separation — expanded C4 denominator" in doc["summary"]["passed"]
    assert "C4_no_interference — all cells" in doc["summary"]["passed"]
    assert len(doc["summary"]["not_applicable"]) == 5


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
