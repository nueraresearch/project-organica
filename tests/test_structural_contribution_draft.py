"""The structural-contribution draft must fix its controls and its seeds before a harness exists."""
from __future__ import annotations

import pathlib
import re

DOC = pathlib.Path("docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md")


def test_draft_is_labelled_a_draft_and_auth_nodes_nothing():
    text = DOC.read_text(encoding="utf-8")
    assert text.startswith("# Structural contribution — pre-registration DRAFT")
    assert "**Status: DRAFT" in text
    assert "No harness exists for it" in text
    assert "nothing in it authorizes a run" in text


def test_question_is_the_three_armed_comparison():
    text = DOC.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "Does the **content** of the edge structure" in flat
    assert "improve log-loss on the relations it" in flat
    for arm in ("**Full**", "**Edge-removed**", "**Rewired**", "**Tuned bigram**"):
        assert arm in text, arm
    # The edge-removed arm's identity with base-rate backoff is stated, not assumed.
    assert "p(b|a) = m(b)" in text.replace("\\|", "|")


def test_it_is_not_a_transfer_test():
    text = DOC.read_text(encoding="utf-8")
    assert "structural-contribution test, not a transfer test" in text
    assert "does not make a transfer claim" in text
    assert "does not use that measure" in text


def test_rewiring_rule_is_degree_preserving_and_fixed():
    text = DOC.read_text(encoding="utf-8")
    assert "Maslov–Sneppen" in text
    assert "10 * len(edges)" in text
    assert "K = 25" in text
    assert "seed * 1009 + draw" in text
    for invariant in ("out-degree", "in-degree", "weight multiset", "node set", "edge count"):
        assert invariant in text, invariant
    # The control gate has a number, so it cannot be chosen later.
    assert "≤ 0.20" in text
    # The mean over draws is pre-specified and the best draw is excluded.
    assert "best draw is never used" in text


def test_primary_criterion_requires_both_controls_and_excludes_bigram():
    text = DOC.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "upper" in flat and "below zero" in flat
    assert "both** `d_removed` and `d_rewired`" in flat
    assert "not** part of this criterion" in flat
    assert "Beating the bigram is reported beside it" in flat
    for key in ("d_removed", "d_rewired", "d_bigram"):
        assert f"`{key}" in text, key
    assert "20261102" in text
    assert "10,000 cluster-bootstrap resamples" in text


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
    # The five-row table is a table, not prose: four bound + four bound + budget cells.
    table = text.split("| `d_removed` | `d_rewired` | `d_bigram` | Reported outcome |", 1)[1]
    body = [line for line in table.splitlines() if line.startswith("|")]
    assert sum(1 for line in body if "below 0" in line or "No detectable" in line) == 5


def test_seed_blocks_are_fresh_and_disjoint_from_every_prior_block():
    text = DOC.read_text(encoding="utf-8")
    design = set(range(20270301, 20270306))
    confirmatory = set(range(20270306, 20270321))
    prior = (
        set(range(20270201, 20270221))   # frozen functional study
        | set(range(20261201, 20261227))  # closed reusable-knowledge study
        | set(range(20270101, 20270121))  # provenance study
        | set(range(20261100, 20261131))  # acquisition study
        | {20261099}                      # alpha calibration world
    )
    assert design.isdisjoint(confirmatory)
    assert (design | confirmatory).isdisjoint(prior)
    for block in (design, confirmatory):
        assert str(min(block)) in text and str(max(block)) in text
    # The prior blocks are named, so a future run cannot quietly reuse one.
    for bound in ("20270220", "20261226", "20270120", "20261130", "20261099"):
        assert bound in text, bound


def test_gates_and_stop_rules_are_fixed():
    text = DOC.read_text(encoding="utf-8")
    for gate in ("**S1 liveness.**", "**S2 denominators.**", "**S3 the controls can fail.**",
                 "**S4 invariants.**", "**S5 constants pinned.**", "**S6 reproducibility.**"):
        assert gate in text, gate
    flat = " ".join(text.split())
    assert "planted-signal" in flat
    assert "not measurable" in flat
    assert "No endpoint on the design block" in flat
    assert "One confirmatory run." in flat
    assert "No threshold movement." in flat
    assert "The frozen study stays frozen." in flat
    assert "endpoint-derived diagnostic" in flat


def test_constants_match_the_frozen_study():
    text = DOC.read_text(encoding="utf-8")
    for constant in ("1,000", "256.0", "110 formation cycles", "15", "20261102"):
        assert constant in text, constant
    # The draft must not soften the frozen result it points at.
    assert "does not revise its §10.4 finding" in text


def test_no_placeholder_survives():
    text = DOC.read_text(encoding="utf-8")
    assert not re.search(r"\{[a-z_]+\}", text)
