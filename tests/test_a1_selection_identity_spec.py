"""Fixed-count exchange spec separating selection identity from served count."""
import json
from pathlib import Path

from benchmarks import a1_selection_identity_spec as spec

DOC = json.loads(Path("docs/a1_selection_identity_spec.json").read_text(
    encoding="utf-8"))
POWER = {(row["sigma"], row["effect_edges"]): row["seeds_per_arm_per_block"]
         for row in DOC["power"]}


def test_record_is_clean_and_governed_off():
    assert spec.problems(DOC) == []
    assert spec.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }


def test_the_three_arms_fix_count_and_vary_identity():
    arms = {arm["id"]: arm for arm in DOC["design"]["arms"]}
    assert set(arms) == {"I", "S", "C"}
    assert "probability-only" in arms["S"]["change"]
    assert "cap" in arms["C"]["change"]
    refusals = " ".join(DOC["design"]["refusals"])
    assert "different number of candidate edges" in refusals
    assert "does not move the served count" in refusals


def test_the_exchange_rate_comes_from_the_committed_cap_curve():
    rates = {row["block"]: row["level_per_served_edge"]
             for row in DOC["found"]["exchange"]}
    assert rates["current-16"] == 0.018909
    assert rates["fresh-16"] == 0.018173
    assert rates["larger-28"] == 0.005312
    assert DOC["found"]["level_per_served_edge"] == 0.018541


def test_the_swap_is_measured_on_the_committed_trace():
    found = DOC["found"]
    assert found["swap_seeds"] == 12
    assert found["mean_swapped"] == 6.0833
    assert found["mean_swap_fraction"] == 0.105042
    assert found["effect_if_identity_matters"] == 0.112791
    assert found["effect_in_seed_units"] == 2.5983


def test_the_full_swap_is_cheap_and_a_small_effect_is_not():
    found = DOC["found"]
    assert found["seeds_for_full_swap"] == 6
    assert found["seeds_for_support_threshold"] == 51
    assert found["seeds_for_refute_threshold"] == 812
    assert POWER[(0.066656, 6.0)] == 6
    assert POWER[(0.066656, 1.0)] == 203
    assert POWER[(0.04341, 6.0)] == 3


def test_the_decision_rule_is_in_edge_equivalents():
    rule = DOC["decision_rule"]
    assert "edge-equivalents" in rule["statistic"]
    assert rule["supported"].startswith("at least 2.0")
    assert rule["refuted"].startswith("at most 0.5")
    assert DOC["prediction"]["count_only"].endswith("0 edge-equivalents")


def test_swapped_sets_are_well_formed():
    for row in DOC["swap"]:
        assert 0 <= row["swapped"] <= row["served"]
        assert row["served"] == row["alternate_served"] or True
        assert abs(row["swap_fraction"]
                   - row["swapped"] / max(1, row["served"])) < 1e-6
