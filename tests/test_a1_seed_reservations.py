"""Reserved-but-unspent seed blocks are visible to the freshness guard."""
import json
from pathlib import Path

from benchmarks import a1_seed_reservations as reservations
from benchmarks import a1_two_path

PAIR_SPLIT = [20690101, 20690102, 20690103, 20690104, 20690105, 20690106]
MANIFEST = Path("docs/a1_two_path_manifest.json")


def test_registry_and_guard_are_clean():
    assert reservations.problems() == []
    assert reservations.self_test() == []
    assert reservations.reservation_problems([20690101], MANIFEST)


def test_the_pair_split_block_is_held_unspent():
    rows = reservations.reservations()
    assert len(rows) == 1
    block = rows[0]
    assert block["seeds"] == PAIR_SPLIT
    assert block["owner"] == "docs/a1_offset_discriminator_spec.json"
    assert block["restated_by"] == ["docs/a1_pair_split_rule_amended.json"]
    assert block["spent"] is False


def test_only_the_reserving_artifacts_may_list_the_block():
    owner = Path("docs/a1_offset_discriminator_spec.json")
    restated = Path("docs/a1_pair_split_rule_amended.json")
    assert reservations.reservation_problems(PAIR_SPLIT, owner) == []
    assert reservations.reservation_problems(PAIR_SPLIT, restated) == []
    refusals = reservations.reservation_problems(PAIR_SPLIT, MANIFEST)
    assert len(refusals) == 1
    assert "reserved by" in refusals[0]
    assert "unspent" in refusals[0]


def test_a_spent_reservation_stops_refusing():
    doc = reservations.registry()
    doc["reservations"][0]["spent"] = True
    assert reservations.reservation_problems(PAIR_SPLIT, MANIFEST, doc) == []


def test_the_preflight_refuses_a_manifest_that_reuses_the_block():
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    baseline = [row for row in a1_two_path.preflight(doc) if "reserved" in row]
    assert baseline == []
    leak = json.loads(json.dumps(doc))
    leak["seed_block"]["seeds"] = PAIR_SPLIT
    refusals = [row for row in a1_two_path.preflight(leak) if "reserved" in row]
    assert len(refusals) == 1


def test_overlapping_reservations_are_refused():
    doc = reservations.registry()
    doc["reservations"].append({
        "label": "a second block that reuses the first",
        "owner": "docs/a1_pair_split_rule_amended.json",
        "restated_by": [],
        "seeds": PAIR_SPLIT[:2],
        "spent": False,
    })
    found = reservations.problems(doc)
    assert any("reserved by two blocks" in row for row in found)


def test_an_owner_that_does_not_name_its_seeds_is_refused():
    doc = reservations.registry()
    doc["reservations"][0]["owner"] = "docs/a1_split_power.json"
    found = reservations.problems(doc)
    assert any("does not name" in row for row in found)


def test_no_other_artifact_names_a_reserved_seed():
    allowed = {"docs/a1_offset_discriminator_spec.json",
               "docs/a1_pair_split_rule_amended.json",
               "docs/a1_seed_reservations.json"}
    offenders = {}
    for path in sorted(Path("docs").glob("*.json")):
        if path.as_posix() in allowed:
            continue
        values = reservations._seeds_of(
            json.loads(path.read_text(encoding="utf-8")))
        shared = sorted(values & set(PAIR_SPLIT))
        if shared:
            offenders[path.as_posix()] = shared
    assert offenders == {}


DECLARED_BLOCKS = {
    "docs/a1_baseline_availability.json",
    "docs/a1_larger_universe_candidate.json",
    "docs/a1_successor_candidate.json",
    "docs/a1_two_path_manifest.json",
    "docs/presence_cap_1_112_prereg.json",
    "docs/presence_comparator_112_prereg.json",
    "docs/presence_construct_1_112_prereg.json",
}


def test_every_declared_block_is_checked():
    blocks = dict(reservations.candidate_blocks())
    assert set(blocks) == DECLARED_BLOCKS
    assert all(len(seeds) == 6 for seeds in blocks.values())
    assert reservations.candidate_problems() == []


def test_both_committed_block_shapes_are_read():
    assert reservations.declared_seeds({"seed_block": PAIR_SPLIT}) == PAIR_SPLIT
    assert reservations.declared_seeds(
        {"seed_block": {"seeds": PAIR_SPLIT, "status": "x"}}) == PAIR_SPLIT
    assert reservations.declared_seeds({"seed_block": None}) == []
    assert reservations.declared_seeds({"seed_block": "20690101"}) == []
    assert reservations.declared_seeds({}) == []
    assert reservations.declared_seeds([]) == []


def test_a_bare_list_candidate_is_refused():
    refusals = reservations.candidate_problems(
        [("docs/a1_successor_candidate.json", {"seed_block": PAIR_SPLIT})])
    assert len(refusals) == 1
    assert refusals[0].startswith("docs/a1_successor_candidate.json:")
    assert "reserved by" in refusals[0]
    assert reservations.candidate_problems(
        [("docs/a1_successor_candidate.json", {"seed_block": [20630101]})]) == []


def test_the_reserving_artifact_is_not_refused_by_the_block_scan():
    assert reservations.candidate_problems(
        [("docs/a1_offset_discriminator_spec.json", {"seed_block": PAIR_SPLIT})]) == []
