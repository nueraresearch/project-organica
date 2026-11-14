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


def _six_cell_parts(seed=20630101):
    import copy

    from benchmarks import a1_result

    parts = a1_result.synthetic_parts()
    by_cell = {payload["cell"]: payload for payload in parts}

    def extra(cell, base_cell, a, k, y):
        payload = copy.deepcopy(by_cell[base_cell])
        payload["cell"] = cell
        for row in payload["rows"]:
            row["cell"] = cell
            row["A"], row["K"], row["Y"] = a, k, y
            row["control_A"] = False
            row["control_K"] = False
        for row in payload["neighbor_rows"]:
            row["cell"] = cell
        return payload

    six = [
        by_cell["A+K+"],
        by_cell["A+K-"],
        by_cell["A-K+"],
        extra("A-K-", "A+K+", False, False, False),
        extra("Y_MINUS_A+K+", "A+K+", True, True, False),
        extra("Y_MINUS_A-K+", "A-K+", False, True, False),
    ]
    for payload in six:
        payload["seed"] = seed
        for row in payload["rows"] + payload["neighbor_rows"]:
            row["seed"] = seed
    return six


def test_parts_update_recomputes_observed_denominators(tmp_path, monkeypatch):
    import json

    from benchmarks import a1_denominator_audit as audit

    for index, payload in enumerate(_six_cell_parts()):
        (tmp_path / ("part-%d.json" % index)).write_text(
            json.dumps(payload), encoding="utf-8"
        )

    observed_json = tmp_path / "observed.json"
    observed_page = tmp_path / "observed.md"
    monkeypatch.setattr(audit, "OBSERVED_OUT_PATH", observed_json)
    monkeypatch.setattr(audit, "OBSERVED_PAGE_PATH", observed_page)
    assert audit.main(["--parts", str(tmp_path)]) == 0

    doc = json.loads(observed_json.read_text(encoding="utf-8"))
    assert doc["kind"] == "a1_denominator_resolution_observed"
    assert doc["status"] == (
        "OBSERVED — PARTIAL COVERAGE; 3 GATE(S) FINER THAN OBSERVED DENOMINATOR"
    )
    coverage = doc["coverage"]
    assert coverage["parts"] == 6
    assert coverage["status"] == "PARTIAL"
    assert coverage["expected_parts"] == 36
    assert len(coverage["missing"]) == 30
    assert doc["observed"]["c1"]["min"] == 20
    assert doc["observed"]["c4"]["min"] == 16
    assert doc["observed"]["c7"]["min"] == 8
    assert doc["observed"]["c8"]["min"] == 4
    assert doc["summary"]["flagged"] == [
        "C4_no_interference — observed non-target edges",
        "C7_assertion_block — observed Y- blocked rows",
        "C8_third_route — observed A-K- blocked rows",
    ]
    assert doc["summary"]["passed"] == [
        "C1_path_separation — observed paired-control rows",
    ]
    assert doc["summary"]["unmeasured"] == []
    assert doc["assembly"]["status"] == "PASS"

    page = observed_page.read_text(encoding="utf-8")
    assert "A1 denominator-resolution audit — observed" in page
    assert "C7_assertion_block" in page and "C8_third_route" in page
    assert "separate 60-row floor" in page


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
