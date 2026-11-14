"""C4 non-target neighbour rows and their paired-control deltas."""
from benchmarks import a1_arms
from benchmarks.a1_gate_readiness import gate_c4


def _row(cell: str, edge: str, a: float, k: float, y: float) -> dict:
    return {
        "seed": 1,
        "cell": cell,
        "edge": edge,
        "target": False,
        "A_rate": a,
        "K_rate": k,
        "Y_rate": y,
    }


def test_neighbor_rows_are_non_target_and_report_rates():
    counts = {
        ("a", "b"): {"A": 60, "K": 30, "Y": 12},
        ("c", "d"): {"A": 0, "K": 0, "Y": 0},
    }
    rows = a1_arms.neighbor_rows(1, "A-K+", set(counts), counts, 120, "fingerprint",
                                 {"a", "b"})
    assert len(rows) == 2
    first, second = rows
    assert first["target"] is False
    assert first["relation"] == "non_target"
    assert first["shares_target_endpoint"] is True
    assert first["A_rate"] == 0.5
    assert first["K_rate"] == 0.25
    assert first["Y_rate"] == 0.1
    assert first["delta_status"] == "AWAITING_PAIRED_CONTROL"
    assert second["shares_target_endpoint"] is False
    assert second["A_rate"] == 0.0


def test_attach_neighbor_deltas_pairs_against_a_plus_k_plus():
    baseline = {
        "seed": 1,
        "cell": "A+K+",
        "neighbor_rows": [_row("A+K+", "a>b", 0.5, 0.4, 0.3)],
    }
    treated = {
        "seed": 1,
        "cell": "A-K+",
        "neighbor_rows": [_row("A-K+", "a>b", 0.5, 0.35, 0.2)],
    }
    a1_arms.attach_neighbor_deltas([baseline, treated])
    row = treated["neighbor_rows"][0]
    assert row["delta_status"] == "MEASURED"
    assert row["paired_control"] == "1/A+K+"
    assert row["neighbor_delta"] == {"A": 0.0, "K": 0.05, "Y": 0.1}

    rows = a1_arms.c4_neighbor_rows([baseline, treated])
    assert len(rows) == 2
    assert gate_c4(rows, 0.05) is False
    result = a1_arms.score_c4([baseline, treated])
    assert result["pass"] is False
    assert result["measured"] == 2


def test_attach_neighbor_deltas_leaves_rows_without_a_control_unmeasured():
    treated = {
        "seed": 1,
        "cell": "A-K+",
        "neighbor_rows": [_row("A-K+", "a>b", 0.5, 0.4, 0.3)],
    }
    a1_arms.attach_neighbor_deltas([treated])
    assert treated["neighbor_rows"][0]["delta_status"] == "AWAITING_PAIRED_CONTROL"
    assert "neighbor_delta" not in treated["neighbor_rows"][0]


def test_c1_rows_use_the_non_target_denominator():
    from benchmarks.a1_gate_readiness import gate_c1

    def c1_row(cell, edge, a, k):
        return {"seed": 1, "cell": cell, "edge": edge, "target": False,
                "A": a, "K": k, "object_fingerprint": "fp"}

    baseline = {
        "seed": 1,
        "cell": "A+K+",
        "rows": [],
        "neighbor_rows": [c1_row("A+K+", "e%d" % i, True, True) for i in range(20)],
    }
    a_minus = {
        "seed": 1,
        "cell": "A-K+",
        "rows": [],
        "neighbor_rows": [
            c1_row("A-K+", "e%d" % i, False, i != 0) for i in range(20)
        ],
    }
    k_minus = {
        "seed": 1,
        "cell": "A+K-",
        "rows": [],
        "neighbor_rows": [
            c1_row("A+K-", "e%d" % i, True, False) for i in range(20)
        ],
    }
    rows = a1_arms.c1_rows([baseline, a_minus, k_minus])
    assert len(rows) == 60
    assert sum(1 for row in rows if row["control_K"]) == 20
    assert sum(1 for row in rows if row["control_A"]) == 20
    assert gate_c1(rows, 0.95) is True
    result = a1_arms.score_c1([baseline, a_minus, k_minus])
    assert result["pass"] is True
    assert result["a_minus"] == {"denominator": 20, "available": 19, "fraction": 0.95}
    assert result["k_minus"] == {"denominator": 20, "available": 20, "fraction": 1.0}


def test_result_assembly_reports_c1_and_c4_pass():
    from benchmarks import a1_result

    report = a1_result.assemble(a1_result.synthetic_parts())
    assert report["status"] == "PASS"
    assert report["c1"]["a_minus"] == {
        "denominator": 20, "available": 19, "fraction": 0.95,
    }
    assert report["c1"]["k_minus"] == {
        "denominator": 20, "available": 20, "fraction": 1.0,
    }
    assert report["c1"]["seeds"]["1"]["pass"] is True
    assert report["c4"]["measured"] == 48
    assert report["c4"]["max_delta"] == {"A": 0.01, "K": 0.01, "Y": 0.04}
    assert report["gates"] == {
        "C1_path_separation": True,
        "C4_no_interference": True,
    }


def test_parts_command_reports_observed_denominator(tmp_path, capsys):
    import json

    from benchmarks import a1_result

    for index, payload in enumerate(a1_result.synthetic_parts()):
        (tmp_path / ("part-%d.json" % index)).write_text(
            json.dumps(payload), encoding="utf-8"
        )

    assert a1_result.main(["--parts", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Observed denominator: OBSERVED; 3 part(s), 1 seed(s)" in out
    assert "C1 observed denominator: A- 20 rows; K- 20 rows" in out
    assert "C4 observed denominator: 48 rows; 48 measured; 0 unmeasured" in out


def test_parts_command_assembles_a_six_cell_directory_end_to_end(tmp_path, capsys):
    import copy
    import json

    from benchmarks import a1_result

    parts = a1_result.synthetic_parts()
    by_cell = {payload["cell"]: payload for payload in parts}

    def extra(cell, base_cell, a, k, y):
        payload = copy.deepcopy(by_cell[base_cell])
        payload["cell"] = cell
        for row in payload["rows"]:
            row["cell"] = cell
            row["A"], row["K"], row["Y"] = a, k, y
            row["control_A"] = cell == "A-K+"
            row["control_K"] = cell == "A+K-"
        for row in payload["neighbor_rows"]:
            row["cell"] = cell
        return payload

    six_cells = [
        by_cell["A+K+"],
        by_cell["A+K-"],
        by_cell["A-K+"],
        extra("A-K-", "A+K+", False, False, False),
        extra("Y_MINUS_A+K+", "A+K+", True, True, False),
        extra("Y_MINUS_A-K+", "A-K+", False, True, False),
    ]
    assert {payload["cell"] for payload in six_cells} == {
        "A+K+", "A+K-", "A-K+", "A-K-", "Y_MINUS_A+K+", "Y_MINUS_A-K+",
    }
    for index, payload in enumerate(six_cells):
        (tmp_path / ("part-%d.json" % index)).write_text(
            json.dumps(payload), encoding="utf-8"
        )

    assert len(a1_result.load_parts(tmp_path)) == 6
    assert a1_result.main(["--parts", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Observed denominator: OBSERVED; 6 part(s), 1 seed(s)" in out
    assert "C1 observed denominator: A- 20 rows; K- 20 rows" in out
    assert "C4 observed denominator: 96 rows; 96 measured; 0 unmeasured" in out
    assert "C1 PASS: A- 19/20 = 0.950; K- 20/20 = 1.000" in out
    assert "C4 PASS: 96 non-target rows, 96 measured" in out


def test_parts_command_reports_not_run_without_cells(tmp_path, capsys):
    from benchmarks import a1_result

    assert a1_result.main(["--parts", str(tmp_path)]) == 2
    out = capsys.readouterr().out
    assert "NOT RUN — no cell parts" in out
    assert "No observed denominator exists" in out


def test_result_assembly_fails_c4_without_changing_c1():
    from benchmarks import a1_result

    report = a1_result.assemble(a1_result.synthetic_parts(0.06))
    assert report["status"] == "FAIL"
    assert report["c1"]["pass"] is True
    assert report["c4"]["pass"] is False
    assert report["c4"]["max_delta"]["Y"] == 0.06
    assert report["c4"]["violations"] == [{
        "seed": 1, "cell": "A-K+", "edge": "n0>m0",
        "path": "Y", "delta": 0.06,
    }]


def test_c4_gate_order_is_recorded_as_post_freeze_void():
    import json
    from pathlib import Path

    doc = json.loads(Path("docs/a1_c4_gate_order.json").read_text(encoding="utf-8"))
    assert doc["decision"] == "POST-FREEZE VOID GATE"
    assert doc["pre_freeze_admissibility"] is False
    assert "target freeze" in doc["does_not_authorize"]
    assert "target freeze" in doc["freeze_effect"]


def test_c1_c4_void_gate_draft_names_both_gates_and_void_meaning():
    import json
    from pathlib import Path

    doc = json.loads(Path("docs/a1_c1_c4_void_gate.json").read_text(encoding="utf-8"))
    assert doc["id"] == "A1-C1-C4-VOID-GATE-1"
    assert doc["status"] == "DRAFT — NOT DECIDED"
    codes = {row["reason_code"] for row in doc["void_conditions"]}
    assert {"C1_NO_DENOMINATOR", "C1_DENOMINATOR_BELOW_FLOOR",
            "C1_THRESHOLD", "C4_UNMEASURABLE", "C4_DELTA"} <= codes
    assert any("not a negative result" in line for line in doc["void_meaning"])
    assert doc["pre_freeze_admissibility"] is False
