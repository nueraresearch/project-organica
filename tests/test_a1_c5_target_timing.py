"""The fixed earlier-U protocol clears C5 timing without changing targets."""
import json
from pathlib import Path

from benchmarks import a1_c5_target_timing as timing
from benchmarks import a1_two_path
from benchmarks.a1_gate_readiness import gate_c5


def _artifact():
    return json.loads(Path("docs/a1_c5_target_timing.json").read_text(encoding="utf-8"))


def test_timing_audit_is_clean_and_preserves_the_current_targets():
    doc = _artifact()
    assert timing.problems(doc) == []
    assert doc["u_cycle"] == 4
    assert doc["selection_u_cycle"] == 36
    assert doc["current_target_observations"] == 24
    assert doc["current_observed_carriers"] == 14
    assert doc["current_missing_carriers"] == 10
    assert doc["current_carriers_before_u"] == 0
    assert doc["earliest_current_carrier_cycle"] == 5
    assert doc["u_before_earliest_carrier"] is True
    current = json.loads(Path("docs/a1_target_selection.json").read_text(encoding="utf-8"))
    n20 = json.loads(Path("docs/a1_c8_target_selection.json").read_text(encoding="utf-8"))
    for seed, row in current["per_seed"].items():
        assert set(row["selected"]) <= set(n20["per_seed"][seed]["selected"])
        assert {r["edge"] for r in doc["current_rows"] if str(r["seed"]) == seed} == set(row["selected"])


def test_page_is_rendered_from_the_audit():
    doc = _artifact()
    page = Path("docs/A1-C5-TARGET-TIMING.md").read_text(encoding="utf-8")
    assert page == timing.render(doc) + "\n"
    assert "cycle 4" in page
    assert "cycle 5" in page


def test_manifest_uses_the_earlier_cycle_for_c5_and_keeps_selection_diagnostic():
    doc = a1_two_path.manifest()
    assert doc["targets"]["u_cycle"] == 4
    assert doc["targets"]["selection_u_cycle"] == 36
    assert doc["U"]["measured_cycle"] == 4
    assert doc["targets"]["c5_timing_audit"] == "docs/a1_c5_target_timing.json"
    problems = a1_two_path.manifest_problems(doc)
    assert not any("U cycle" in problem or "C5 timing audit" in problem
                   for problem in problems)


def test_c5_accepts_an_absent_carrier_and_rejects_a_preceding_one():
    base = {
        "carrier_cycle": None,
        "k_cycle": None,
        "y_cycle": None,
        "U": {"direct_count": 0, "reverse_count": 0, "strength": 0,
              "measured_cycle": 4},
    }
    assert gate_c5([base]) is True
    assert gate_c5([dict(base, carrier_cycle=3, k_cycle=3)]) is False
    assert gate_c5([dict(base, carrier_cycle=4, k_cycle=4)]) is True
    assert gate_c5([dict(base, carrier_cycle="bad")]) is False


def test_timing_self_test_is_clean():
    assert timing.self_test() == []
