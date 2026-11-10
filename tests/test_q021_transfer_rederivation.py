"""The Q021 result must be the frozen block's result, not a typed summary."""
import copy
import json

from benchmarks import q021_transfer_rederivation as Q


def test_the_record_is_exactly_the_frozen_block():
    record = json.loads(Q.ARTIFACT.read_text(encoding="utf-8"))
    assert Q.check() == []
    assert tuple(record["seeds"]) == Q.SEEDS
    assert len(record["cells"]) == 40
    assert {cell["arm"] for cell in record["cells"]} == set(Q.ARMS)
    assert record["verdict"] == "NO_TRANSFER_ADVANTAGE"
    assert record["metrics"]["transfer_ratio"]["treatment"] == 1.0
    assert record["metrics"]["paired_treatment_faster"] == 0
    assert all(record["gates"].values())


def test_the_page_is_generated_from_the_record():
    record = json.loads(Q.ARTIFACT.read_text(encoding="utf-8"))
    assert Q.PAGE.read_text(encoding="utf-8") == Q.render(record)
    assert "NO_TRANSFER_ADVANTAGE" in Q.PAGE.read_text(encoding="utf-8")


def test_the_check_can_fail_on_a_changed_verdict():
    record = json.loads(Q.ARTIFACT.read_text(encoding="utf-8"))
    changed = copy.deepcopy(record)
    changed["verdict"] = "TRANSFER_CLAIM_RE_DERIVED"
    assert Q.check(changed), "a changed verdict must be reported"
