"""The provenance tracer's controls, before it touches any real data."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

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


def test_a_shared_ancestor_is_convergence_not_a_cycle():
    """A diamond lineage is complete: two parents sharing an ancestor is not a loop."""
    claim, index, vocab, _ = pt._fixtures()["diamond_shared_ancestor"]
    got = pt.trace(claim, index, vocab)
    assert got["status"] == "world_rooted"
    assert got["cycle"] is False, "convergence must not be reported as a cycle"
    assert got["complete"] is True and got["defects"] == []
    assert [n["id"] for n in got["nodes"]].count("dia_root") == 1


def test_a_diamond_beside_a_real_cycle_still_reports_the_cycle():
    """Convergence and a loop do not cancel: the loop is still a defect."""
    vocab = {"willow", "teal"}
    left = {"id": "l", "type": "phrase_candidate", "members": ["willow"],
            "parent_ids": ["root"]}
    right = {"id": "r", "type": "phrase_candidate", "members": ["teal"],
             "parent_ids": ["root"]}
    root = {"id": "root", "type": "concept_candidate", "members": ["willow"],
            "parent_ids": []}
    loop_a = {"id": "loopa", "type": "hypothesis", "parent_ids": ["loopb"]}
    loop_b = {"id": "loopb", "type": "hypothesis", "parent_ids": ["loopa"]}
    claim = {"id": "c", "type": "prediction_candidate", "source": "willow",
             "target": "teal", "parent_ids": ["l", "r", "loopa"]}
    got = pt.trace(claim, pt.build_index([claim, left, right, root, loop_a, loop_b]),
                   vocab)
    assert got["cycle"] is True
    assert "cycle" in got["defects"]
    assert got["status"].endswith("_incomplete")


def test_dedupe_keeps_the_newest_snapshot_of_a_candidate():
    """The engine re-stores a survivor each cycle; one lineage is counted once."""
    older = {"id": "c1", "generation": 1, "parent_ids": []}
    newer = {"id": "c1", "generation": 3, "parent_ids": ["a"]}
    kept = pt.dedupe_candidates([older, newer, {"id": "c2", "generation": 1}])
    by_id = {p["id"]: p for p in kept}
    assert len(kept) == 2
    assert by_id["c1"]["generation"] == 3


def test_only_claim_typed_structures_are_traced():
    payloads = [{"id": "p", "type": "prediction_candidate"},
                {"id": "h", "type": "hypothesis_candidate"},
                {"id": "c", "type": "concept_candidate"}]
    assert [p["id"] for p in pt.claim_structures(payloads)] == ["p", "h"]


def test_incomplete_lineages_are_never_counted_as_rooted():
    rows = [{"status": "world_rooted", "type": "prediction_candidate", "ancestor_depth": 2},
            {"status": "world_rooted_incomplete", "type": "prediction_candidate",
             "ancestor_depth": 2},
            {"status": "unresolved_cycle", "type": "prediction_candidate",
             "ancestor_depth": 1}]
    summary = pt.summarise_rows(rows)
    assert summary["complete_world_rooted"] == 1
    assert summary["incomplete_total"] == 1
    assert summary["unresolved_total"] == 1
    assert (sum(summary["complete"].values()) + summary["incomplete_total"]
            + summary["unresolved_total"]) == 3


def test_depth_buckets_split_shallow_from_deep():
    assert [pt.depth_bucket(d) for d in (0, 1, 2, 3, 4, 6, 7, 9)] == \
        ["0", "1", "2", "3", "4-6", "4-6", "7+", "7+"]


def test_a_diagnostic_may_not_carry_a_verdict():
    art = {"no_threshold": True, "no_verdict": True,
           "authorises_confirmatory": False, "study_reopened": False}
    pt._assert_diagnostic(art)
    for bad in ({"no_threshold": False}, {"no_verdict": False},
                {"authorises_confirmatory": True}, {"study_reopened": True}):
        with pytest.raises(AssertionError):
            pt._assert_diagnostic({**art, **bad})


def test_the_report_is_generated_without_placeholders():
    rows = [{"status": "world_rooted", "type": "prediction_candidate", "ancestor_depth": 1}]
    summary = pt.summarise_rows(rows)
    summary.update({"claims_with_asserted_edge": 1, "structures_indexed": 2})
    art = {"plan_doc": pt.PLAN_DOC, "plan_frozen_at_commit": "abc123",
           "seeds": [424242], "cap": 1000, "variant": "V",
           "controls": {"all_passed": True, "count": len(pt._fixtures()) + 1},
           "totals": {"formation": summary, "revision": summary},
           "seeds_detail": [{"seed": 424242, "formation": summary,
                             "revision": summary}]}
    doc = pt.render_report(art)
    assert "{" not in doc and "}" not in doc, "a leftover placeholder is silent"
    assert doc == pt.render_report(art), "the report must be a function of the artifact"
    assert doc.count("| 424242 | formation |") == 1, "the per-seed section is missing"
    assert "Counting units" in doc, "the three units must be reported"


def test_incomplete_lineages_report_why_they_are_incomplete():
    """A chain cut by our own depth cap is not a chain whose ancestors were pruned."""
    rows = [{"status": "world_rooted_incomplete", "type": "hypothesis",
             "ancestor_depth": 7, "defects": ["depth_truncated"]},
            {"status": "world_rooted_incomplete", "type": "hypothesis",
             "ancestor_depth": 3, "defects": ["missing_records", "cycle"]},
            {"status": "world_rooted", "type": "prediction_candidate",
             "ancestor_depth": 2}]
    summary = pt.summarise_rows(rows)
    assert summary["defects"] == {"missing_records": 1, "cycle": 1, "depth_truncated": 1}


def test_the_three_counting_units_are_reported_separately_and_map():
    """Rows, unique ids and unique edges are three units; none stands in for another."""
    raw = [{"id": "p1", "type": "prediction_candidate", "source": "anna", "target": "bert"},
           {"id": "p1", "type": "prediction_candidate", "source": "anna", "target": "bert"},
           {"id": "p2", "type": "prediction_candidate", "source": "anna", "target": "bert"},
           {"id": "p3", "type": "prediction_candidate"}]
    claims = pt.claim_structures(pt.dedupe_candidates(raw))
    status = {"p1": "world_rooted", "p2": "unresolved_no_ancestry",
              "p3": "unresolved_no_ancestry"}
    levels = pt.counting_levels(raw, claims, status)
    assert levels["raw_claim_rows"] == 4
    assert levels["raw_claim_rows_with_edge"] == 3
    assert levels["unique_structures"] == 3
    assert levels["unique_structures_with_edge"] == 2
    assert levels["unique_asserted_edges"] == 1, "two structures assert one edge"
    assert levels["edges_with_complete_rooted_claim"] == 1
    assert levels["rows_per_structure"]["max"] == 2
    assert levels["structures_per_edge"]["max"] == 2


def test_parent_links_are_counted_per_snapshot_not_per_structure():
    """A structure that lost its links is not a structure that never had any."""
    raw = [{"id": "p1", "type": "prediction_candidate", "generation": 1,
            "parent_ids": ["anc"]},
           {"id": "p1", "type": "prediction_candidate", "generation": 2,
            "parent_ids": []},
           {"id": "p2", "type": "prediction_candidate", "generation": 2,
            "parent_ids": []}]
    levels = pt.parent_link_levels(raw, pt.dedupe_candidates(raw))["prediction"]
    assert levels["raw_rows"] == 3
    assert levels["raw_rows_with_parents"] == 1
    assert levels["ids_ever_with_parents"] == 1
    assert levels["ids_latest_with_parents"] == 0
    assert levels["ids_with_parents_only_in_earlier_snapshots"] == 1
