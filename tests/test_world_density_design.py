"""Density must be measured as |W|/|C|, and the record must allocate nothing.

The arithmetic is recomputed from the artifact, so a counts-as-density slip or a
vocabulary change cannot hide in prose; the non-inference about the decay null and
the ceiling caveat are asserted rather than trusted.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "world_density_design.json"
DOC = ROOT / "docs" / "WORLD-DENSITY-DESIGN.md"


def _body():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def test_the_candidate_universe_is_quadratic_in_the_tag_count():
    body = _body()
    for row in body["universe"]["table"]:
        assert row["pairs"] == row["tags"] * (row["tags"] - 1)
    assert {r["tags"]: r["pairs"] for r in body["universe"]["table"]}[16] == 240


def test_edge_counts_are_derived_from_density_not_declared():
    body = _body()
    levels = body["density"]["levels"]
    counts = body["density"]["counts_at_16_tags"]
    assert counts == [round(level * 240) for level in levels]
    assert max(counts) <= 240, "a 16-tag world cannot hold more than 240 directed pairs"


def test_a_five_hundred_edge_world_is_nearly_complete_and_needs_more_tags():
    block = _body()["counts_are_not_densities"]
    n, pairs = block["min_tags"], block["pairs_then"]
    assert n == min(k for k in range(2, 200) if k * (k - 1) >= block["example_edges"])
    assert pairs == n * (n - 1)
    assert block["density_then"] == round(block["example_edges"] / pairs, 3)
    assert block["density_then"] > 0.95


def test_the_exposure_choice_and_its_confound_rule_are_named():
    exposure = _body()["exposure"]
    assert "fixed total exposure" in exposure["primary"]
    assert "fixed exposure per edge" in exposure["sensitivity"]
    assert "exposure artifact, not geometry" in exposure["confound_rule"]
    flat = _flat()
    assert "fixed total exposure" in flat and "fixed exposure per edge" in flat
    assert "fix the **tag count**" in flat


def test_the_claim_is_an_interaction_not_a_main_effect():
    comparison = _body()["comparison"]
    assert "Delta(d)" in comparison["estimand"]
    assert "depends on density" in comparison["claim"]
    assert any("main effect of density is not an interaction" in x
               for x in comparison["not_claimed"])
    flat = _flat()
    assert "a main effect of density is **not** an interaction" in flat.lower()
    assert "Delta(d)" in flat


def test_the_decay_null_is_not_offered_as_evidence():
    not_evidence = " ".join(_body()["not_evidence"])
    assert "varied only the threshold" in not_evidence
    flat = _flat()
    assert "not evidence for or against this hypothesis" in flat


def test_the_precision_ceiling_is_not_called_a_universal_bound():
    caveat = _body()["ranking_bottleneck"]["ceiling_caveat"]
    assert "0.3438" in caveat
    assert "not an information-theoretic bound" in caveat
    flat = _flat()
    assert "not an information-theoretic bound" in flat


def test_the_record_allocates_nothing_and_consumes_no_seeds():
    allocation = _body()["allocation"]
    assert allocation["seeds"] == 0 and allocation["cells"] == 0
    assert allocation["thresholds"] == 0 and allocation["bars"] == 0
    text = ARTIFACT.read_text(encoding="utf-8")
    assert not re.search(r"\b20\d{6}\b", text), "a seed block must not be allocated here"


def test_the_document_quotes_the_artifact_and_has_no_placeholders():
    body = _body()
    flat = _flat()
    assert f"|C| = {body['universe']['table'][0]['pairs']}" in flat
    assert str(body["counts_are_not_densities"]["min_tags"]) in flat
    assert str(body["counts_are_not_densities"]["density_then"]) in flat
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))
