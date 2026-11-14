"""Complete-coverage scoring for the five structural A1 gates."""
from benchmarks import a1_arms
from benchmarks import a1_result
from benchmarks import a1_two_path
from benchmarks.a1_gate_readiness import gate_c5


TARGETS = ["alpha>beta", "gamma>delta"]


def _cell_values(cell):
    return {
        "A+K+": (True, True, True),
        "A+K-": (True, False, True),
        "A-K+": (False, True, True),
        "A-K-": (False, False, False),
        "Y_MINUS_A+K+": (True, True, False),
        "Y_MINUS_A-K+": (False, True, False),
    }[cell]


def _row(seed, cell, edge):
    a, k, y = _cell_values(cell)
    return {
        "seed": seed,
        "cell": cell,
        "edge": edge,
        "target": True,
        "A": a,
        "K": k,
        "Y": y,
        "A_rate": 1.0 if a else 0.0,
        "K_rate": 1.0 if k else 0.0,
        "Y_rate": 1.0 if y else 0.0,
        "carrier_cycle": 4,
        "k_cycle": 5,
        "y_cycle": 6,
        "U": {"direct_count": 2, "reverse_count": 1, "strength": 3,
              "measured_cycle": 2},
        "object_fingerprint": "seed-%d" % seed,
    }


def _payloads():
    payloads = []
    for seed in a1_two_path.SEEDS:
        for cell in a1_arms.COMPLETE_CELLS:
            payloads.append({
                "kind": a1_arms.KIND,
                "seed": seed,
                "cell": cell,
                "targets": list(TARGETS),
                "rows": [_row(seed, cell, edge) for edge in TARGETS],
                "neighbor_rows": [],
            })
    return payloads


def _expected():
    return {str(seed): list(TARGETS) for seed in a1_two_path.SEEDS}


def test_registered_n20_target_map_is_the_default_universe():
    expected = a1_arms.registered_target_map()
    assert set(expected) == {str(seed) for seed in a1_two_path.SEEDS}
    assert all(len(edges) == 20 for edges in expected.values())


def test_complete_scores_pass_on_six_seeds_and_six_cells():
    report = a1_arms.score_complete_gates(_payloads(), _expected())
    assert report["pass"] is True
    assert report["failed"] == []
    assert set(report["gates"]) == {
        "C2_treatment_consistency", "C3_positivity", "C5_common_cause",
        "C7_assertion_block", "C9_same_object",
    }
    assert report["gates"]["C2_treatment_consistency"]["rows"] == 48
    assert report["gates"]["C3_positivity"]["rows"] == 72
    assert report["gates"]["C5_common_cause"]["rows"] == 72
    assert report["gates"]["C7_assertion_block"]["rows"] == 48
    assert report["gates"]["C9_same_object"]["rows"] == 72


def test_missing_cell_is_not_hidden_by_complete_other_cells():
    payloads = [row for row in _payloads()
                if not (row["seed"] == a1_two_path.SEEDS[0]
                        and row["cell"] == "A-K+")]
    report = a1_arms.score_complete_gates(payloads, _expected())
    assert report["pass"] is False
    assert "C2_treatment_consistency" in report["failed"]
    assert "C3_positivity" in report["failed"]
    assert "C5_common_cause" in report["failed"]
    assert "C9_same_object" in report["failed"]


def test_partial_target_coverage_fails_c2_and_c7():
    payloads = _payloads()
    for payload in payloads:
        if payload["seed"] == a1_two_path.SEEDS[0] and payload["cell"] == "Y_MINUS_A+K+":
            payload["rows"] = payload["rows"][:-1]
    report = a1_arms.score_complete_gates(payloads, _expected())
    assert report["gates"]["C2_treatment_consistency"]["pass"] is False
    assert report["gates"]["C7_assertion_block"]["pass"] is False
    assert report["gates"]["C2_treatment_consistency"]["coverage"]["pass"] is False


def test_c2_checks_y_minus_a_and_k_paths():
    payloads = _payloads()
    for payload in payloads:
        if payload["seed"] == a1_two_path.SEEDS[0] and payload["cell"] == "Y_MINUS_A+K+":
            payload["rows"][0]["A"] = False
    result = a1_arms.score_c2(payloads, _expected())
    assert result["coverage"]["pass"] is True
    assert result["gate_pass"] is False
    assert result["pass"] is False


def test_c5_rejects_a_malformed_cycle_and_allows_an_absent_carrier():
    rows = [_row(1, "A+K+", "alpha>beta")]
    assert gate_c5(rows) is True
    rows[0]["carrier_cycle"] = "not-a-cycle"
    assert gate_c5(rows) is False
    rows[0]["carrier_cycle"] = None
    assert gate_c5(rows) is True
    payloads = _payloads()
    for payload in payloads:
        if payload["seed"] == a1_two_path.SEEDS[0] and payload["cell"] == "A+K+":
            payload["rows"][0]["carrier_cycle"] = "not-a-cycle"
    result = a1_arms.score_c5(payloads, _expected())
    assert result["coverage"]["pass"] is True
    assert result["gate_pass"] is False
    assert result["pass"] is False


def test_c7_checks_each_y_cell_not_a_pooled_fraction():
    payloads = _payloads()
    for payload in payloads:
        if payload["seed"] == a1_two_path.SEEDS[0] and payload["cell"] == "Y_MINUS_A-K+":
            for row in payload["rows"]:
                row["Y"] = True
    # Pooled over both Y cells this is 2 of 4 asserted, below the baseline's
    # 4 of 4; the per-cell rule must still reject the failed second Y cell.
    result = a1_arms.score_c7(payloads, _expected())
    assert result["coverage"]["pass"] is True
    assert result["gate_pass"] is False
    assert result["pass"] is False


def test_c9_requires_every_cell_and_one_fingerprint():
    payloads = _payloads()
    for payload in payloads:
        if payload["seed"] == a1_two_path.SEEDS[0] and payload["cell"] == "A-K-":
            payload["rows"][0]["object_fingerprint"] = "different"
    result = a1_arms.score_c9(payloads, _expected())
    assert result["coverage"]["pass"] is True
    assert result["gate_pass"] is False
    assert result["pass"] is False


def test_result_assembly_reports_complete_coverage_for_real_parts():
    report = a1_result.assemble(_payloads(), expected_targets=_expected(), complete=True)
    assert report["complete_status"] == "PASS"
    assert report["complete_coverage"]["pass"] is True
    assert report["gates"]["C2_treatment_consistency"] is True
    assert report["gates"]["C3_positivity"] is True
    assert report["gates"]["C5_common_cause"] is True
    assert report["gates"]["C7_assertion_block"] is True
    assert report["gates"]["C9_same_object"] is True
    assert report["all_gates_pass"] is False  # C4 has no non-target stream in this fixture
