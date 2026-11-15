"""Amended pair-split decision rule and its seed budget."""
import json
from pathlib import Path

from benchmarks import a1_pair_split_rule_amended as rule

DOC = json.loads(Path("docs/a1_pair_split_rule_amended.json").read_text(
    encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert rule.problems(DOC) == []
    assert rule.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }


def test_the_amended_rule_moves_exactly_one_number():
    body = DOC["rule"]
    assert body["floor"] == 0.05
    assert body["ceiling"] == 0.07
    assert body["size_if"] == "|d| <= 0.05"
    assert body["density_if"] == "d <= -0.07"
    assert body["size_prediction"] == 0.0
    assert body["density_prediction"] == -0.11638
    assert DOC["found"]["new_rule"]["seeds_per_block"] == 6
    assert DOC["found"]["seeds_saved_per_block"] == 3


def test_the_committed_construction_and_seeds_are_kept():
    body = DOC["rule"]
    assert body["seeds_per_block"] == 6
    assert body["seeds"] == [20690101, 20690102, 20690103,
                             20690104, 20690105, 20690106]
    assert body["blocks"] == ["split-32", "split-48"]
    assert DOC["found"]["unchanged"]["equal_m_check"] == 0.05


def test_the_six_committed_seeds_now_meet_the_budget():
    amended = DOC["found"]["amended_at_six"]
    assert DOC["found"]["admissible_at_six"] is True
    assert amended["se"] == 0.038484
    assert amended["size_if_size"] == 0.81794
    assert amended["density_if_density"] == 0.893506
    assert amended["density_if_size"] == 0.035678
    assert amended["size_if_density"] == 0.042472
    assert amended["density_if_size"] <= 0.05
    assert amended["size_if_density"] <= 0.05


def test_the_ceiling_only_touches_the_density_branch():
    old = DOC["found"]["old_rule"]
    amended = DOC["found"]["amended_at_six"]
    assert old["power_size_at_six"] == amended["size_if_size"]
    assert old["false_size_at_six"] == amended["size_if_density"]
    assert amended["density_if_density"] > old["power_density_at_six"]


def test_the_superseded_numbers_are_named_against_their_artifacts():
    superseded = {row["field"]: row for row in DOC["found"]["supersedes"]}
    assert "decision_rule.if_abs_above" in superseded
    assert superseded["decision_rule.if_abs_above"]["committed"].startswith(
        "0.09")
    assert "found.seeds_both_at_primary" in superseded
    assert superseded["found.seeds_both_at_primary"]["committed"] == 9
    provenance = {row["field"]: row for row in DOC["provenance"]}
    assert provenance["found.cheapest_ceiling"]["artifact"] == (
        "a1_band_frontier.json")
    assert provenance["constants.decision_ceiling"]["artifact"] == (
        "a1_offset_discriminator_spec.json")


PAIR_SPLIT_SEEDS = (20690101, 20690102, 20690103, 20690104, 20690105, 20690106)
PAIR_SPLIT_ARTIFACTS = {
    "docs/a1_offset_discriminator_spec.json",
    "docs/a1_pair_split_rule_amended.json",
    "docs/a1_seed_reservations.json",
}


def _integers(node, out):
    if isinstance(node, dict):
        for value in node.values():
            _integers(value, out)
    elif isinstance(node, list):
        for value in node:
            _integers(value, out)
    elif isinstance(node, bool):
        return
    elif isinstance(node, int):
        out.add(node)
    elif isinstance(node, float) and node.is_integer():
        out.add(int(node))


def test_the_reserved_seeds_appear_in_no_committed_artifact():
    """The pair-split block must be unspent: no other artifact may name a seed."""
    offenders = {}
    for path in sorted(Path("docs").glob("*.json")):
        values = set()
        _integers(json.loads(path.read_text(encoding="utf-8")), values)
        shared = sorted(values & set(PAIR_SPLIT_SEEDS))
        if shared and path.as_posix() not in PAIR_SPLIT_ARTIFACTS:
            offenders[path.as_posix()] = shared
    assert offenders == {}


def test_the_reserved_seeds_are_not_the_manifest_block():
    manifest = json.loads(
        Path("docs/a1_two_path_manifest.json").read_text(encoding="utf-8"))
    assert not set(manifest["seed_block"]["seeds"]) & set(PAIR_SPLIT_SEEDS)
