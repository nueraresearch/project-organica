"""The fresh-block replication must keep its frozen design and pre-specified verdict.

Static controls read the committed prereg and result; they do not replay a seed.
"""
LAYER = "static"

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import assertion_provenance_replication as replication  # noqa: E402


def artifact() -> dict:
    return json.loads(replication.ARTIFACT.read_text(encoding="utf-8"))


def prereg() -> dict:
    return json.loads(replication.PREREG.read_text(encoding="utf-8"))


def test_the_design_is_frozen_and_the_result_is_complete():
    body = prereg()
    art = artifact()

    assert body["status"] == "FROZEN, RUN"
    assert body["design"]["seeds"] == replication.SEEDS
    assert body["design"]["cycles"] == replication.CYCLES
    assert body["design"]["cap"] == replication.CAP
    assert body["completed_on"] == "2026-11-11"
    assert body["verdict"] == "DIRECTIONAL ONLY"
    assert replication.problems(art) == []
    assert art["status"] == "RUN"
    assert art["summary"]["never_served_asserted"] == 26
    assert art["summary"]["identity_mismatch"] == 24
    assert art["summary"]["alternate_assertion_path"] == 2
    assert art["summary"]["assertion_without_service"] == 0
    assert art["summary"]["recording_gap"] == 0
    assert art["summary"]["verdict"] == "DIRECTIONAL ONLY"


def test_the_original_magnitude_is_outside_the_fresh_interval():
    summary = artifact()["summary"]
    low, high = summary["wilson_95"]

    assert low <= summary["identity_share"] <= high
    assert not (low <= summary["original_share"] <= high)
    assert summary["criteria"]["R1_direction"] is True
    assert summary["criteria"]["R2_original_share_in_interval"] is False
    assert summary["criteria"]["R3_both_classes_present"] is True


def test_the_verdict_rule_can_reach_each_declared_verdict():
    for identity, alternate, expected in (
        (18, 8, "REPLICATED"),
        (24, 2, "DIRECTIONAL ONLY"),
        (2, 24, "NOT REPLICATED"),
        (26, 0, "NOT REPLICATED"),
        (0, 0, "VOID"),
    ):
        criteria = replication._criteria(identity, alternate)
        assert replication._verdict(identity, alternate, criteria) == expected


def test_a_tampered_verdict_is_reported():
    bad = copy.deepcopy(artifact())
    bad["summary"]["verdict"] = "REPLICATED"

    assert replication.problems(bad), "a verdict that disagrees with the counts must fail"


def test_the_page_is_current_and_the_seeds_are_fresh():
    art = artifact()

    assert replication.PAGE.read_text(encoding="utf-8") == replication.render(art)
    from benchmarks.presence_cap_experiment import seed_collisions
    assert seed_collisions(
        replication.SEEDS, allow=replication.COLLISION_ALLOW) == {}
