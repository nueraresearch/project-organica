"""The provenance tracer's controls, before it touches any real data."""
from __future__ import annotations

import pytest

from benchmarks import provenance_trace as pt


def test_every_control_matches_its_known_ancestry():
    result = pt.run_controls()
    assert result["all_passed"], result["controls"]
    for name, row in result["controls"].items():
        assert row["status"] == row["expected"], (name, row)


def test_the_tracer_can_change_its_answer():
    """A control that cannot fire proves nothing (AGENTS rule 25)."""
    claim, index, vocab, _ = pt._fixtures()["world_derived"]
    assert pt.trace(claim, index, vocab)["status"] == "world_rooted"
    assert pt.trace(claim, index, set())["status"] == "self_only"


def test_content_tags_read_values_not_field_names():
    payload = {"id": "phrase_1", "type": "phrase_candidate",
               "members": ["willow", "teal"]}
    assert pt.content_tags(payload, {"willow", "teal"}) == {"willow", "teal"}
    assert pt.content_tags(payload, {"willow", "members"}) == {"willow"}, (
        "a field NAME must never count as content")


def test_missing_parents_are_reported_not_dropped():
    claim, index, vocab, _ = pt._fixtures()["missing_parent"]
    got = pt.trace(claim, index, vocab)
    assert got["status"] == "unresolved_missing_records"
    assert got["missing"] == 1


def test_a_cycle_is_unresolved_and_does_not_loop_forever():
    claim, index, vocab, _ = pt._fixtures()["cycle"]
    got = pt.trace(claim, index, vocab)
    assert got["status"] == "unresolved_cycle"
    assert got["cycle"] is True


def test_depth_cap_reports_truncation_rather_than_self_only():
    claim, index, vocab, _ = pt._fixtures()["depth_capped"]
    got = pt.trace(claim, index, vocab)
    assert got["status"] == "unresolved_depth_truncated"
    assert got["depth_hit"] is True


def test_status_vocabulary_separates_resolution_from_verdict():
    """`self_only` and `unresolved_*` must never be collapsed into one another."""
    assert "self_only" in pt.STATUSES
    assert all(s.startswith("unresolved_") for s in pt.STATUSES
               if s.startswith("unresolved"))
    assert len(pt.STATUSES) == len(set(pt.STATUSES))


def test_trace_claims_reports_counts_and_no_verdict():
    claim, index, vocab, _ = pt._fixtures()["world_derived"]
    summary = pt.trace_claims([claim], index.values(), vocab)
    assert summary["claims"] == 1
    assert summary["statuses"]["world_rooted"] == 1
    assert "no threshold and no verdict" in summary["note"]


def test_a_claim_without_ancestors_is_not_self_only():
    """No parent links is `unresolved_no_ancestry`, not evidence either way.

    Crediting the claim's own words would make every claim that names a world tag
    "world_rooted" by definition, so grounding is judged on the ancestors.
    """
    bare = {"id": "bare", "type": "prediction_candidate",
            "source": "willow", "target": "teal", "parent_ids": []}
    got = pt.trace(bare, pt.build_index([bare]), {"willow", "teal"})
    assert got["status"] == "unresolved_no_ancestry"
    assert "unresolved_no_ancestry" in pt.STATUSES


def test_a_resolved_branch_cannot_hide_a_missing_one():
    claim, index, vocab, _ = pt._fixtures()["world_rooted_with_missing_parent"]
    got = pt.trace(claim, index, vocab)
    assert got["status"] == "world_rooted_incomplete"
    assert "missing_records" in got["defects"]
    assert got["complete"] is False
    assert got["terminals"], "the resolved branch must still be summarised"


def test_a_resolved_branch_cannot_hide_a_cycle():
    claim, index, vocab, _ = pt._fixtures()["self_only_with_cycle"]
    got = pt.trace(claim, index, vocab)
    assert got["status"] == "self_only_incomplete"
    assert "cycle" in got["defects"]
    assert got["complete"] is False


def test_a_resolved_branch_cannot_hide_a_truncated_branch():
    claim, index, vocab, _ = pt._fixtures()["world_rooted_with_depth_truncation"]
    got = pt.trace(claim, index, vocab)
    assert got["status"] == "world_rooted_incomplete"
    assert "depth_truncated" in got["defects"]
    assert got["complete"] is False


def test_only_a_complete_lineage_may_be_read_as_world_rooted():
    for name in ("world_derived", "self_only", "mixed"):
        claim, index, vocab, expected = pt._fixtures()[name]
        got = pt.trace(claim, index, vocab)
        assert got["status"] == expected
        assert got["complete"] is True
        assert got["defects"] == []
