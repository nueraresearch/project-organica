"""The presence-to-assertion ladder must stay the trace it was measured as.

Every number here is read from the stamped artifact and recomputed where it can be, so a
change to a cell, to the declared rule or to the renderer is caught rather than restated.
The declared dominance threshold is pinned too: the result sits just under it, and moving
the threshold after the run would be re-scoring the protocol.
"""

import copy
import json

import pytest

from benchmarks import presence_assertion_ladder as L

BODY = json.loads(L.ARTIFACT.read_text(encoding="utf-8"))
ROWS = {row["seed"]: row for row in BODY["rows"]}

# The exact bucket split the six seeds produced, per seed: (not_offered, offered_not_admitted,
# admitted_not_asserted).
BUCKETS = {
    20261100: (0, 25, 47),
    20261101: (0, 33, 35),
    20261102: (0, 23, 51),
    20261103: (0, 26, 40),
    20261104: (0, 36, 42),
    20261105: (0, 28, 37),
}


def test_the_trace_reproduces_the_published_audit_on_all_six_seeds():
    assert BODY["kind"] == L.KIND
    assert BODY["trace_mismatches"] == []
    assert [row["seed"] for row in BODY["rows"]] == list(L.SEEDS)
    audit = json.loads(L.AUDIT.read_text(encoding="utf-8"))
    reference = {row["seed"]: row for row in audit["rows"]}
    for row in BODY["rows"]:
        other = reference[row["seed"]]
        assert row["present_world_edges"] == other["present_world_edges"] == 112
        assert row["asserted_world_edges"] == other["asserted_world_edges"]
        assert row["asserted_fingerprint"] == other["asserted_fingerprint"]
    assert [row["asserted_world_edges"] for row in BODY["rows"]] == [40, 44, 38, 46, 34, 47]


def test_every_world_edge_is_offered_and_none_are_lost_before_the_ranking():
    for row in BODY["rows"]:
        assert row["offered_world_edges"] == 112
        assert row["buckets"]["not_offered"] == 0
        assert row["admitted_not_offered"] == 0
    assert BODY["summary"]["pooled_buckets"]["not_offered"] == 0


def test_each_miss_is_assigned_to_the_first_stage_it_failed():
    assert {seed: (row["buckets"]["not_offered"],
                   row["buckets"]["offered_not_admitted"],
                   row["buckets"]["admitted_not_asserted"]) for seed, row in ROWS.items()} == BUCKETS
    for row in BODY["rows"]:
        total = sum(row["buckets"].values())
        assert total == row["present_not_asserted"] == 112 - row["asserted_world_edges"]
        for name, edges in row["bucket_edges"].items():
            assert len(edges) == row["buckets"][name]
            assert not set(edges) & set(row["bucket_edges"][
                "admitted_not_asserted" if name != "admitted_not_asserted" else "not_offered"])
    assert BODY["summary"]["pooled_buckets"] == {
        "not_offered": 0, "offered_not_admitted": 171, "admitted_not_asserted": 252}
    assert BODY["summary"]["misses_total"] == 423


def test_the_window_is_full_and_the_ranking_is_a_superset_of_it():
    for row in BODY["rows"]:
        assert row["shipped_window"]["median_window"] == 40
        assert 72 <= row["shipped_window"]["cycles_at_cap"] <= 112
        assert row["shipped_window"]["world_row_share"] < 0.30
        assert 225 <= row["offered_window"]["median_window"] <= 238
        # An edge is present but never admitted either because it was ranked out or because it
        # was asserted by another structure type without ever entering a prediction window.
        assert row["admitted_world_edges"] == (
            112 - row["buckets"]["offered_not_admitted"] - row["asserted_without_admission"])
        assert 3 <= row["asserted_without_admission"] <= 9


def test_admission_frequency_is_recorded_for_every_present_world_edge():
    for row in BODY["rows"]:
        assert len(row["admissions"]) == 112
        zeros = sum(1 for value in row["admissions"].values() if value == 0)
        assert zeros == (row["buckets"]["offered_not_admitted"]
                         + row["asserted_without_admission"])
        assert row["admission_stats"]["admitted_not_asserted"]["zero"] == 0
    # Repetition does not separate the two fates: the medians overlap and cross over on some seeds.
    assert [row["asserted_admission_stats"]["median"] for row in BODY["rows"]] == [
        5.0, 6.5, 11.0, 3.0, 13.5, 4]
    assert [row["admission_stats"]["admitted_not_asserted"]["median"]
            for row in BODY["rows"]] == [5, 5, 5, 6, 5, 9]


def test_the_verdict_is_mixed_under_the_threshold_declared_before_the_run():
    assert L.DOMINANT == 0.60 and L.MAJORITY_SEEDS == 5
    shares = BODY["summary"]["pooled_share"]
    assert shares["admitted_not_asserted"] == 0.595745
    assert shares["admitted_not_asserted"] < L.DOMINANT, (
        "the declared dominance bar was 0.60 before the run; the result sits just below it")
    assert BODY["verdict"] == L.label_for(BODY["rows"]) == "MIXED"


def test_the_label_rule_can_return_every_branch():
    def row(not_offered, offered, admitted):
        buckets = {"not_offered": not_offered, "offered_not_admitted": offered,
                   "admitted_not_asserted": admitted}
        return {"buckets": buckets,
                "leading_bucket": max(buckets, key=lambda name: buckets[name])}

    assert L.label_for([row(10, 0, 0)] * 6) == "LOSS_BEFORE_OFFER"
    assert L.label_for([row(0, 10, 0)] * 6) == "LOSS_AT_ADMISSION"
    assert L.label_for([row(0, 0, 10)] * 6) == "LOSS_AFTER_ADMISSION"
    assert L.label_for([row(4, 4, 4)] * 6) == "MIXED"
    assert L.label_for([row(0, 0, 0)] * 6) == "VOID_NO_MISSES"
    assert L.label_for([row(0, 1, 1)] * 6) == "MIXED"
    # A bucket below the minimum miss count cannot carry the label.
    assert L.label_for([row(1, 0, 0)] * 3) == "MIXED"
    # A dominant pooled share that only three seeds lead is still MIXED.
    assert L.label_for([row(10, 0, 0)] * 3 + [row(0, 6, 6)] * 3) == "MIXED"


def test_classify_orders_the_ladder_by_first_failure():
    present = {("a", "b"), ("a", "c"), ("a", "d"), ("a", "e")}
    asserted = {("a", "e")}
    offered = {("a", "b"), ("a", "c")}
    admitted = {("a", "d")}
    found = L.classify(present, offered, admitted, asserted)
    assert found["not_offered"] == [("a", "b")] or found["not_offered"] == []
    assert set(found["offered_not_admitted"]) | set(found["not_offered"]) == {("a", "b"), ("a", "c")}
    assert found["admitted_not_asserted"] == [("a", "d")]


def test_the_page_is_the_artifact():
    assert L.PAGE.read_text(encoding="utf-8") == L.render(BODY)


def test_the_gate_fails_on_a_stale_verdict(tmp_path, monkeypatch):
    forged = copy.deepcopy(BODY)
    forged["verdict"] = "LOSS_AT_ADMISSION"
    artifact = tmp_path / "ladder.json"
    artifact.write_text(json.dumps(forged), encoding="utf-8")
    monkeypatch.setattr(L, "ARTIFACT", artifact)
    monkeypatch.setattr(L, "PAGE", tmp_path / "page.md")
    with pytest.raises(SystemExit, match="not what the rows imply"):
        L.check()


def test_the_runner_check_is_clean():
    assert L.check() == 0
