"""The per-world precision probe must measure what the gate needs, and no more.

The granularity gate consumes a per-world standard error. `score()` returns an
aggregate over nested cells, so the count of withheld transitions is not a count of
independent contributions and the probe has to bootstrap transitions instead. These
tests check the reconstruction against the house scorer, that the bracket really does
straddle the assumed gap, and that the document quotes the artifact rather than the
other way round.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.acquisition_compositional import score
from benchmarks.reusable_knowledge import (
    CYCLES, broken_rule_holder, generate_compositional_world, latent_rule_holder, limbs,
)
from benchmarks.stage_b_endpoint_precision import (
    EFFECT_GAP, OUT, build, cell_losses, per_transition_losses,
)

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "STAGE-B-PROTOCOL.md"


@pytest.fixture(scope="module")
def artifact() -> dict:
    return build()


def test_the_stored_artifact_is_current(artifact):
    assert json.loads(OUT.read_text(encoding="utf-8")) == artifact


def test_the_transition_aggregate_reproduces_the_house_scorer():
    """If the two disagree, the probe is measuring a different quantity."""
    world = generate_compositional_world(seed=20261201, cycles=CYCLES)
    ctx, obs = limbs(world)["revision_held_out"]
    vocabulary = {t for event in world["events"] for t in event.split()}
    prob = latent_rule_holder(world, 0)
    per = per_transition_losses(prob, ctx, obs, vocabulary)
    total = sum(ll for ll, _ in per) / sum(n for _, n in per)
    assert total == pytest.approx(score(prob, ctx, obs, vocabulary)["log_loss"],
                                  abs=1e-6)
    # and the per-cell decomposition is the same arithmetic
    cells = cell_losses(prob, ctx, obs, vocabulary)
    assert sum(cells) / len(cells) == pytest.approx(total, abs=1e-6)


def test_the_bootstrap_separates_transitions_from_cells(artifact):
    """Clusters are not cells: the two standard errors are visibly different."""
    ratios = [row["cluster_over_naive_se_ratio"]
              for cell in artifact["cells"] for row in cell["readouts"].values()]
    assert all(r > 0 for r in ratios)
    # if clustering did not matter the ratio would sit at 1.0 in every cell
    assert max(ratios) > 1.2 or min(ratios) < 0.8


def test_the_bracket_straddles_the_gap_rather_than_settling_it(artifact):
    by = artifact["by_readout"]
    assert by["ceiling"]["clears_the_assumed_gap"] is True
    assert by["broken_rule"]["clears_the_assumed_gap"] is False
    assert artifact["the_bracket_straddles_the_gap"] is True
    assert by["ceiling"]["max_twice_cluster_se"] < EFFECT_GAP
    assert by["broken_rule"]["min_twice_cluster_se"] > EFFECT_GAP
    assert artifact["status"].startswith("method discharged")
    assert "NOT confirmed" in artifact["status"]


def test_the_document_quotes_these_numbers(artifact, stage_text):
    by = artifact["by_readout"]
    for key in ("ceiling", "broken_rule"):
        quoted = "**%.3f to %.3f" % (by[key]["min_twice_cluster_se"],
                                     by[key]["max_twice_cluster_se"])
        assert quoted in stage_text, quoted
    assert "straddles" in stage_text


@pytest.fixture(scope="module")
def stage_text() -> str:
    return DOC.read_text(encoding="utf-8")
