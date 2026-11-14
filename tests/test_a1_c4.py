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
