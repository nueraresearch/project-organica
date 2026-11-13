"""The stored-field tie-break stays a bounded, post-hoc ranking diagnostic."""
LAYER = "static"

import json

import pytest

from benchmarks import stored_field_tiebreak as gate


def test_artifact_and_page():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    assert art["kind"] == "stored_field_tiebreak"
    assert art["status"] == "POST-HOC DIAGNOSTIC"
    assert art["posthoc"] is True
    assert art["prereg"] is None
    assert not gate.engine_stamp.missing(art)
    assert art["summary"]["top20_seats"] == 13604
    assert art["summary"]["served_set"] == {
        "changed_cycles": 0,
        "changed_seats": 0,
        "entering_pairs": 0,
        "leaving_pairs": 0,
        "new_edge_seed_pairs": 0,
        "lost_edge_seed_pairs": 0,
    }
    assert art["summary"]["order"]["changed_cycles"] == 12
    assert art["summary"]["order"]["positions_changed"] == 37
    assert art["summary"]["ties"]["cutoff_ties"] == 120
    assert art["summary"]["ties"]["cutoff_ties_resolved_by_strength"] == 0
    assert gate.PAGE.read_text(encoding="utf-8") == gate.render(art)
    assert not gate.problems(art)


def test_key_matches_shipped_descending_probability_and_count():
    rows = [
        {"edge": ["a", "b"], "entropy": 1.0, "prob": 0.2, "count": 10,
         "schema": False, "strength": 1.0},
        {"edge": ["a", "c"], "entropy": 1.0, "prob": 0.5, "count": 20,
         "schema": False, "strength": 0.4},
    ]
    ordered = sorted(rows, key=gate._base_key)
    assert [row["edge"] for row in ordered] == [["a", "c"], ["a", "b"]]
    assert gate._base_key(rows[0])[2] == -0.2
    assert gate._base_key(rows[0])[3] == -10


def test_tie_break_engages_only_inside_primary_ties():
    cycles = gate._load_cycles()
    changed = 0
    order_changed = 0
    for key, rows in cycles.items():
        base = gate._top(rows, False)
        alt = gate._top(rows, True)
        base_edges = gate._ordered_edges(base)
        alt_edges = gate._ordered_edges(alt)
        if set(base_edges) != set(alt_edges):
            changed += 1
        elif base_edges != alt_edges:
            order_changed += 1
            for left, right in zip(base, alt):
                if left["edge"] != right["edge"]:
                    assert gate._primary(left) == gate._primary(right)
    assert changed == 0
    assert order_changed == 12


def test_checks_reject_wrong_direction():
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    art["summary"]["served_set"]["changed_seats"] = 4
    assert "served set changed" in gate.problems(art)
    art = json.loads(gate.ARTIFACT.read_text(encoding="utf-8"))
    art["summary"]["checks"]["same_top20_membership"] = False
    assert "checks" in gate.problems(art)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
