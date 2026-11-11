"""Density must be |W|/|P_world|, the ranker's own population must be reported, and the
predicted direction must be registered before any cell.

The arithmetic is recomputed from the artifact, so a counts-as-density slip, a vocabulary
change or a silently different candidate universe cannot hide in prose.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

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


def test_the_world_universe_is_quadratic_in_the_tag_count():
    table = _body()["universe"]["world_pairs"]["table"]
    for row in table:
        assert row["pairs"] == row["tags"] * (row["tags"] - 1)
    assert {r["tags"]: r["pairs"] for r in table}[16] == 240


def test_both_universes_exist_and_only_one_is_manipulated():
    universe = _body()["universe"]
    assert "world_pairs" in universe and "rank_population" in universe
    assert "measured" in universe["rank_population"]["role"]
    density = _body()["density"]
    assert density["manipulated"] == "rho_world"
    assert density["measured"] == "rho_rank"
    flat = _flat()
    assert "P_rank" in flat and "P_world" in flat
    assert "measured per cell, never set" in flat


def test_edge_counts_are_derived_from_density_not_declared():
    density = _body()["density"]
    assert density["counts_at_16_tags"] == [round(level * 240) for level in density["levels"]]
    assert max(density["counts_at_16_tags"]) <= 240


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
    assert "Held fixed: the tag count" in _flat()


def test_the_treatment_is_named_for_what_it_changes():
    treatment = _body()["treatment"]
    assert treatment["control"]["name"] == "global count-ranked top-k"
    assert treatment["treatment"]["name"] == "intra-cell-excluded ranking"
    for arm in ("control", "treatment"):
        assert "improved" not in treatment[arm]["name"]
        assert "better" not in treatment[arm]["name"]
    assert "budget competition" in treatment["mechanism_claim"]
    assert "intra-cell" in treatment["why_this_one"]


def test_precision_is_bounded_by_the_selection_not_the_pool_share():
    """The record's first bound was false; the corrected one binds the selection."""
    rules = " ".join(_body()["analysis_rules"])
    assert "cannot exceed min(1," in rules
    assert "NOT bounded by rho_rank" in rules
    assert "rho_rank must move with rho_world" in rules
    flat = _flat().replace("**", "")
    assert "cannot exceed min(1," in flat
    assert "said precision cannot exceed rho_rank" in flat
    assert "1.000 against" in flat and "0.800" in flat


def test_the_predicted_direction_is_registered_with_its_limit():
    prediction = _body()["predicted_direction"]
    joined = " ".join(prediction["predictions"])
    assert "declines as rho_world rises" in joined
    assert "mechanically" in joined
    assert "must go to 0" in prediction["limit"]
    falsifiers = " ".join(prediction["falsifiers"])
    assert "flat in rho" in falsifiers
    assert "rising in rho" in falsifiers
    flat = _flat()
    assert "Delta(rho) = treated − control declines" in flat
    assert "harness defect, not a" in flat


def test_the_claim_is_an_interaction_not_a_main_effect():
    comparison = _body()["comparison"]
    assert "Delta(d)" in comparison["estimand"] or "Delta(rho)" in comparison["estimand"]
    assert "depends on density" in comparison["claim"]
    flat = _flat()
    assert "main effect of density" in flat and "is not an interaction" in flat.lower()
    assert "Delta(rho)" in flat


def test_the_decay_null_is_not_offered_as_evidence():
    assert "varied only the threshold" in " ".join(_body()["not_evidence"])
    assert "not evidence for or against this hypothesis" in _flat()


def test_the_precision_ceiling_is_not_called_a_universal_bound():
    caveat = _body()["ranking_bottleneck"]["ceiling_caveat"]
    assert "0.3438" in caveat and "not an information-theoretic bound" in caveat


def test_the_record_allocates_nothing_and_consumes_no_seeds():
    allocation = _body()["allocation"]
    assert allocation["seeds"] == 0 and allocation["cells"] == 0
    assert allocation["thresholds"] == 0 and allocation["bars"] == 0
    assert not re.search(r"\b20\d{6}\b", ARTIFACT.read_text(encoding="utf-8"))


def test_the_document_quotes_the_artifact_and_has_no_placeholders():
    body = _body()
    flat = _flat()
    assert f"|P_world| = **{body['universe']['world_pairs']['table'][0]['pairs']}**" in flat
    assert str(body["counts_are_not_densities"]["min_tags"]) in flat
    assert str(body["counts_are_not_densities"]["density_then"]) in flat
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))
