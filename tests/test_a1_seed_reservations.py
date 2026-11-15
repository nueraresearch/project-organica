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
    rows = [row for row in reservations.reservations()
            if row["owner"] == "docs/a1_offset_discriminator_spec.json"]
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


def test_a_spent_reservation_refuses_others_but_not_its_owner():
    doc = reservations.registry()
    doc["reservations"][0]["spent"] = True
    refusals = reservations.reservation_problems(PAIR_SPLIT, MANIFEST, doc)
    assert len(refusals) == 1
    assert "were spent by" in refusals[0]
    owner = Path("docs/a1_offset_discriminator_spec.json")
    assert reservations.reservation_problems(PAIR_SPLIT, owner, doc) == []


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
    "docs/a1_baseline_availability_adopted.json",
    "docs/a1_c5_carrier_divergence.json",
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
        [("docs/a1_successor_candidate.json", {"seed_block": [20880101]})]) == []


def test_the_reserving_artifact_is_not_refused_by_the_block_scan():
    assert reservations.candidate_problems(
        [("docs/a1_offset_discriminator_spec.json", {"seed_block": PAIR_SPLIT})]) == []


CAP112_AUDIT_SEEDS = [20261100, 20261101, 20261102, 20261103,
                      20261104, 20261105]


def test_the_shared_cap112_block_is_declared_and_verified():
    rows = {row["label"]: row for row in reservations.shared_blocks()}
    assert len(rows) == 1
    entry = rows["the six historical audit seeds at cap 112"]
    assert entry["seeds"] == CAP112_AUDIT_SEEDS
    assert entry["declared_by"] == "seed_reuse"
    assert entry["pending"] == ""
    assert entry["artifacts"] == ["docs/presence_comparator_112_prereg.json",
                                  "docs/presence_construct_1_112_prereg.json"]
    for path in entry["artifacts"]:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
        assert doc["seed_block"] == CAP112_AUDIT_SEEDS
        assert "paired" in doc["seed_reuse"]
        assert "presence_assertion_audit_0.14.0.json" in doc["seed_reuse"]
    assert reservations.shared_block_problems() == []


TWO_PATH_SEEDS = NEW_BLOCK = [
    20740101, 20740102, 20740103, 20740104, 20740105, 20740106]
BASELINE_SEEDS = [20630101, 20630102, 20630103,
                  20630104, 20630105, 20630106]


def test_the_two_path_block_is_adopted_and_held():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["seed_block"]["seeds"] == TWO_PATH_SEEDS
    assert manifest["control"]["seed"] == TWO_PATH_SEEDS[0]
    rows = {row["owner"]: row for row in reservations.reservations()}
    held = rows["docs/a1_two_path_manifest.json"]
    assert held["seeds"] == TWO_PATH_SEEDS
    assert held["spent"] is False
    assert "docs/a1_c5_target_timing.json" in held["restated_by"]
    assert reservations.reservation_problems(TWO_PATH_SEEDS, MANIFEST) == []


def test_the_baseline_block_is_recorded_as_spent():
    rows = {row["owner"]: row for row in reservations.reservations()}
    spent = rows["docs/a1_baseline_availability.json"]
    assert spent["seeds"] == BASELINE_SEEDS
    assert spent["spent"] is True
    refusals = reservations.reservation_problems(BASELINE_SEEDS, MANIFEST)
    assert len(refusals) == 1
    assert "were spent by" in refusals[0]


def test_undeclared_sharing_is_refused():
    shared = [("docs/a1_successor_candidate.json", [9, 10]),
              ("docs/a1_larger_universe_candidate.json", [9, 10])]
    found = reservations.shared_block_problems(blocks=shared)
    assert len(found) == 1
    assert "not a recorded shared block" in found[0]


def test_a_shared_entry_that_the_artifact_contradicts_is_refused():
    doc = reservations.registry()
    doc["shared_blocks"][0]["seeds"] = CAP112_AUDIT_SEEDS[:3]
    found = reservations.shared_block_problems(doc)
    assert any("does not declare that block" in row for row in found)


def test_a_recorded_shared_block_is_not_refused():
    shared = [("docs/presence_comparator_112_prereg.json", CAP112_AUDIT_SEEDS),
              ("docs/presence_construct_1_112_prereg.json", CAP112_AUDIT_SEEDS)]
    assert reservations.shared_block_problems(blocks=shared) == []
