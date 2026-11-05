"""The structural-contribution preregistration must stay fixed and match its audit.

These guards cover the committed protocol and the design-block record: the four
arms, the rewiring rule, the outcome table, the fresh seeds, the stop rules — and
the audit figures, which are read off `docs/structural_contribution_design_audit.json`
rather than typed.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

DOC = pathlib.Path("docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md")
AUDIT = pathlib.Path("docs/structural_contribution_design_audit.json")


def test_protocol_is_committed_and_stopped_at_the_design_block():
    text = DOC.read_text(encoding="utf-8")
    assert text.startswith("# Structural contribution — pre-registration")
    assert "DRAFT" not in text
    assert "**Status: committed 2026-11-02 (v1)" in text
    assert "failed gate S3b on all five" in text
    assert "no confirmatory seed has been read" in text


def test_question_is_the_four_armed_comparison():
    text = DOC.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "Does the **content** of the edge structure" in flat
    assert "improve log-loss on the relations it" in flat
    for arm in ("**Full**", "**Edge-removed**", "**Rewired**", "**Tuned bigram**"):
        assert arm in text, arm
    # The table escapes the pipe in the formula; §3 restates it unescaped.
    assert "= m(b)" in text and "p(b\\|a) = m(b)" in text


def test_it_is_not_a_transfer_test():
    text = DOC.read_text(encoding="utf-8")
    assert "structural-contribution test, not a transfer test" in text
    assert "does not make a transfer claim" in text


def test_rewiring_rule_and_control_gate_are_fixed():
    text = DOC.read_text(encoding="utf-8")
    assert "Maslov–Sneppen" in text
    assert "10 * len(edges)" in text
    assert "K = 25" in text
    assert "seed * 1009 + draw" in text
    for invariant in ("out-degree", "in-degree", "weight multiset", "node set", "edge count"):
        assert invariant in text, invariant
    assert "≤ 0.20" in text
    assert "best draw is never used" in text


def test_primary_criterion_requires_both_controls():
    text = DOC.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "both** `d_removed` and `d_rewired`" in flat
    assert "not** part of this criterion" in flat
    for key in ("d_removed", "d_rewired", "d_bigram"):
        assert f"`{key}" in text, key
    assert "10,000 cluster-bootstrap resamples" in text
    assert "20261102" in text


def test_every_outcome_row_is_named_in_advance():
    text = DOC.read_text(encoding="utf-8")
    rows = [
        "Structural contribution supported within this design",
        "not enough for a predictive advantage over the simple baseline",
        "its specific content is not established",
        "the current interpretation needs rethinking",
        "No detectable contribution from the formed edges",
    ]
    for row in rows:
        assert row in text, row


def test_second_world_family_is_deferred_and_named():
    text = DOC.read_text(encoding="utf-8")
    assert "## 11. Second world family, deferred" in text
    sec11 = " ".join(text.split("## 11. Second world family, deferred", 1)[1]
                   .split("## 12.", 1)[0].split())
    assert "replication" in sec11
    assert "its own preregistration" in sec11
    assert "one world family" in sec11


def test_seed_blocks_are_fresh_and_disjoint_from_every_prior_block():
    text = DOC.read_text(encoding="utf-8")
    design = set(range(20270301, 20270306))
    confirmatory = set(range(20270306, 20270321))
    prior = (set(range(20270201, 20270221)) | set(range(20261201, 20261227))
             | set(range(20270101, 20270121)) | set(range(20261101, 20261131))
             | {20261099})
    assert design.isdisjoint(confirmatory)
    assert (design | confirmatory).isdisjoint(prior)
    for block in (design, confirmatory):
        assert str(min(block)) in text and str(max(block)) in text


def test_gates_and_stop_rules_are_fixed():
    text = DOC.read_text(encoding="utf-8")
    for gate in ("**S1 liveness.**", "**S2 denominators.**", "**S3 the controls can fail.**",
                 "**S4 invariants.**", "**S5 constants pinned.**", "**S6 reproducibility.**"):
        assert gate in text, gate
    flat = " ".join(text.split())
    for rule in ("No endpoint on the design block", "One confirmatory run.",
                 "No threshold movement.", "The frozen study stays frozen.",
                 "planted-signal"):
        assert rule in flat, rule


def test_design_audit_record_matches_the_artifact():
    """§12 quotes the artifact; a drift between them is a defect."""
    if not AUDIT.exists():
        pytest.skip("design audit artifact not present in this checkout")
    art = json.loads(AUDIT.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")
    sec = " ".join(doc.split("## 12.", 1)[1].split("## 13.", 1)[0].split())
    assert art["status"].startswith("design block FAILED")
    assert art["confirmatory_seeds_run"] == 0
    assert [cell["seed"] for cell in art["cells"]] == list(art["seeds"])
    failed = {f["gate"] for f in art["failures"]}
    assert failed == {"S3"}, failed
    for cell in art["cells"]:
        share = cell["gates"]["S3"]["S3b_rewiring_changes_cells"]["unchanged_share_max"]
        assert f"{share:.6f}" in sec, (cell["seed"], share)
        for key in ("edges", "source_tags", "distinct_targets",
                    "possible_pairs_over_vocab"):
            assert str(cell["readout"][key]) in sec, (cell["seed"], key)
        for gate in ("S1", "S2", "S3c", "S4", "S5", "S6"):
            assert cell["gates"][gate]["passed"], (cell["seed"], gate)
    assert f"{art['seconds']}" in sec


def test_the_study_is_closed_and_the_weight_shift_is_not_substituted():
    """The closure is the record; an amendment chosen after the failure would be a new study."""
    text = DOC.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "### 12.6 Decision (owner, 2026-11-02): closed at the design gate" in text
    assert "Keep this preregistration unchanged, and close the study at the failed design gate." in flat
    assert "No confirmatory run." in flat
    assert "The 0.20 limit stays at 0.20." in flat
    assert "is not substituted into this study" in flat
    assert "shuffle weights **within each source row**" in flat
    assert "needs its own preregistration and its own success criterion" in flat
    assert "not identifiable with this readout and remains null" in flat
    assert "no confirmatory result" in flat
    # The header must not still describe the decision as outstanding.
    head = " ".join(text.split("## 1. Question", 1)[0].split())
    assert "neither has been chosen" not in head
    assert "\u00a712.6" in head


def test_no_placeholder_survives():
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))
