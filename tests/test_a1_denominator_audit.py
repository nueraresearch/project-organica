"""The denominator-resolution audit must flag only the under-resolved gates."""
import json

from benchmarks import a1_denominator_audit as audit
from benchmarks.a1_gate_readiness import gate_c7, gate_c8


def test_audit_flags_c1_fallback_and_c8():
    doc = audit.build()
    assert doc["summary"]["flagged"] == [
        "C1_path_separation — target-only fallback",
        "C1_path_separation — N=8 maximum-feasibility target-only",
        "C8_third_route — A-K- blocked rows",
        "C8_third_route — N=8 maximum-feasibility A-K- blocked rows",
    ]
    assert "C1_path_separation — expanded C4 denominator" in doc["summary"]["passed"]
    assert "C1_path_separation — N=8 maximum-feasibility expanded denominator" in doc["summary"]["passed"]
    assert "C4_no_interference — all cells" in doc["summary"]["passed"]
    assert "C4_no_interference — N=8 maximum-feasibility all cells" in doc["summary"]["passed"]
    assert len(doc["summary"]["not_applicable"]) == 5
    assert doc["denominator_unit"]["C7_assertion_block"] == "PER SEED"
    assert doc["denominator_unit"]["C8_third_route"] == "PER SEED"
    assert doc["denominator_unit"]["pooled_reading"].startswith("REJECTED")
    assert doc["denominator_unit"]["pooled_rows_if_it_were_used"]["C8_N4"] == 24
    assert doc["denominator_unit"]["resolved"] == {
        "C7_N4": True, "C7_N8": True, "C8_N4": False,
        "C8_N8": False, "C8_N20": True}
    maximum = doc["inputs"]["maximum_feasibility"]
    assert maximum["n_targets"] == 8
    assert maximum["max_disjoint_targets_from_tag_vertices"] == 8
    assert maximum["feasible_seeds_with_eight_disjoint"] == 6
    c7 = [row for row in doc["gates"]
          if row["scenario"] == "N=8 maximum-feasibility Y- blocked rows"][0]
    c8 = [row for row in doc["gates"]
          if row["scenario"] == "N=8 maximum-feasibility A-K- blocked rows"][0]
    assert c7["denominator"] == 120 and c7["status"] == "PASS"
    assert c7["smallest_step"] <= c7["margin"]
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
        "OBSERVED — PARTIAL COVERAGE; 2 GATE(S) FINER THAN OBSERVED DENOMINATOR; "
        "1 UNMEASURED"
    )
    coverage = doc["coverage"]
    assert coverage["parts"] == 6
    assert coverage["status"] == "PARTIAL"
    assert coverage["expected_parts"] == 36
    assert len(coverage["missing"]) == 30
    assert doc["observed"]["c1"]["min"] == 20
    assert doc["observed"]["c4"]["min"] == 16
    assert doc["observed"]["c7"]["min"] is None
    assert doc["observed"]["c8"]["min"] == 4
    assert doc["summary"]["flagged"] == [
        "C4_no_interference — observed non-target edges",
        "C8_third_route — observed A-K- blocked rows",
    ]
    assert doc["summary"]["passed"] == [
        "C1_path_separation — observed paired-control rows",
    ]
    assert doc["summary"]["unmeasured"] == [
        "C7_assertion_block — observed A/K cycle denominator",
    ]
    assert doc["assembly"]["status"] == "PASS"

    page = observed_page.read_text(encoding="utf-8")
    assert "A1 denominator-resolution audit — observed" in page
    assert "C7_assertion_block" in page and "C8_third_route" in page
    assert "separate 60-row floor" in page


def _gate_row(seed, cell, y, delta=(0.0, 0.0)):
    return {
        "seed": seed,
        "cell": cell,
        "Y": y,
        "delta_from_baseline": {"A": delta[0], "K": delta[1]},
    }


def test_c8_rejects_a_seed_that_pooling_would_hide():
    rows = []
    for seed in range(1, 7):
        for index in range(4):
            rows.append(_gate_row(seed, "A-K-", seed == 1 and index == 0))
    assert sum(1 for row in rows if row["Y"]) / len(rows) == 1 / 24
    assert gate_c8(rows, 0.05) is False


def test_c7_requires_both_y_cells_on_every_seed():
    rows = []
    for seed in range(1, 7):
        rows.append(_gate_row(seed, "A+K+", True))
        rows.append(_gate_row(seed, "Y_MINUS_A+K+", False))
        if seed != 1:
            rows.append(_gate_row(seed, "Y_MINUS_A-K+", False))
    assert gate_c7(rows, 0.05) is False


def test_c7_passes_only_with_both_y_cells_per_seed():
    rows = []
    for seed in range(1, 7):
        rows += [
            _gate_row(seed, "A+K+", True),
            _gate_row(seed, "Y_MINUS_A+K+", False),
            _gate_row(seed, "Y_MINUS_A-K+", False),
        ]
    assert gate_c7(rows, 0.05) is True


def _rate_row(seed, cell, edge, a_rate, k_rate, y):
    return {
        "seed": seed,
        "cell": cell,
        "edge": edge,
        "Y": y,
        "A_rate": a_rate,
        "K_rate": k_rate,
    }


def test_c7_computes_per_edge_delta_from_target_rates():
    rows = []
    for seed in range(1, 7):
        edge = "s%d>t%d" % (seed, seed)
        rows += [
            _rate_row(seed, "A+K+", edge, 1.0, 1.0, True),
            _rate_row(seed, "Y_MINUS_A+K+", edge, 0.98, 0.99, False),
            _rate_row(seed, "Y_MINUS_A-K+", edge, 0.97, 1.0, False),
        ]
    assert gate_c7(rows, 0.05) is True
    rows[1]["A_rate"] = 0.90
    assert gate_c7(rows, 0.05) is False
    del rows[1]["A_rate"]
    assert gate_c7(rows, 0.05) is False


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
