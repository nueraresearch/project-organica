"""The engine binding may only run the design block, and its gates must be able to fail."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
import pathlib

import pytest

from benchmarks import functional_harness as fh

ARTIFACT = pathlib.Path("docs/functional_structure_design_audit.json")


def test_confirmatory_seeds_are_refused():
    """Step 2 may not touch a confirmatory seed: §8 allows exactly one run of those."""
    for seed in fh.CONFIRMATORY_SEEDS:
        with pytest.raises(SystemExit):
            fh.refuse_confirmatory(seed)


def test_a_seed_outside_every_block_is_refused():
    with pytest.raises(SystemExit):
        fh.refuse_confirmatory(20261201)      # the closed study's calibration cell


def test_design_block_is_the_protocol_block():
    assert fh.DESIGN_SEEDS == (20270201, 20270202, 20270203, 20270204, 20270205)
    assert set(fh.DESIGN_SEEDS).isdisjoint(fh.CONFIRMATORY_SEEDS)
    assert len(fh.CONFIRMATORY_SEEDS) == 15
    assert fh.CAP == 1000 and fh.ALPHA == 256.0 and fh.TUNING_CYCLES == 15


def test_liveness_needs_an_edge_out_of_a_tag_that_occurs():
    """Total edge weight is not liveness: the edges must touch a source tag in the window."""
    cells = [{"pair": 0, "source": "amber", "target": "birch", "y": 1, "p": 0.6}]
    dead = fh.gate_liveness({"rows": {"cedar": {"maple": 4.0}}}, cells)
    assert dead["passed"] is False
    assert dead["edges"] == 1 and dead["realised_cells_with_support"] == 0
    empty = fh.gate_liveness({"rows": {}}, cells)
    assert empty["passed"] is False
    live = fh.gate_liveness({"rows": {"amber": {"birch": 2.0}}}, cells)
    assert live["passed"] is True


def test_denominator_gate_rejects_a_mismatch():
    vocab = {"aaaa", "bbbb", "cccc"}
    ctx = [["aaaa", "bbbb"], ["cccc", "aaaa"]]
    good = [{"pair": i, "source": "aaaa", "target": "bbbb", "y": 0, "p": 0.5}
            for i in range(sum(len(c) for c in ctx) * len(vocab))]
    gate = fh.gate_denominators(ctx, good, good, [["aaaa"]], vocab)
    assert gate["passed"] is True
    assert gate["cells_expected"] == 12
    short = good[:-1]
    assert fh.gate_denominators(ctx, short, good, [["aaaa"]], vocab)["passed"] is False
    assert fh.gate_denominators(ctx, good, good, [], vocab)["passed"] is False


def test_constants_gate_checks_the_hash_seed(monkeypatch):
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert fh.gate_constants(20270201)["passed"] is True
    monkeypatch.setenv("PYTHONHASHSEED", "12345")
    assert fh.gate_constants(20270201)["passed"] is False


def test_design_artifact_forms_no_endpoint():
    """§10: the endpoint is not formed on a design seed, whatever the gates say."""
    if not ARTIFACT.exists():
        pytest.skip("design audit artifact not present in this checkout")
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert art["confirmatory_seeds_run"] == 0
    assert art["seeds"] == list(fh.DESIGN_SEEDS)
    for cell in art["cells"]:
        assert cell["delta"] is None
        assert "not formed" in cell["endpoint"]
        for wiring in cell["disqualifier_wiring"].values():
            assert wiring["shares_reported"] is False
    # The boundary is declared, not implied: what was computed, and what was not.
    boundary = art["endpoint_boundary"]
    assert boundary["counts_as"] == "endpoint-derived diagnostic"
    assert any("per-cell losses" in s for s in boundary["computed_on_design_seeds"])
    assert any("pooled delta" in s for s in boundary["not_computed_on_design_seeds"])
    # The limb's status is a statement about the measure, and it says so.
    limb = art["transfer_limb"]
    assert limb["status"] == "not attributable under the current provenance measure"
    assert limb["claim_available"] is False
    assert "not evidence that Organica failed to transfer" in limb["meaning"]
    # A design-seed status is an instrument reading, not a verdict on the study.
    assert limb["design_seed_status_is_a_verdict"] is False
    for cell in art["cells"]:
        for wiring in cell["disqualifier_wiring"].values():
            assert wiring["verdict_on_the_study"] is False
            assert "instrument reading" in wiring["reason"]
    # And the 0.50 withholding on that window is structural: no withheld relation
    # is world-majority on any design seed.
    for cell in art["cells"]:
        assert cell["provenance_coverage"]["withheld_world_majority"] == 0
    # Every gate that ran passed; the artifact's own verdict must agree.
    assert art["failures"] == []
    assert "passed" in art["status"]


def test_artifact_counts_are_what_the_protocol_quotes():
    """The numbers in §10.1 are read off this artifact, not typed beside it."""
    if not ARTIFACT.exists():
        pytest.skip("design audit artifact not present in this checkout")
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    doc = pathlib.Path("docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md").read_text(encoding="utf-8")
    sec = doc.split("### 10.1", 1)[1].split("---", 1)[0]
    first = art["cells"][0]["disqualifier_wiring"]["primary"]["cells_by_group"]
    assert str(first["world"]) in sec
    assert str(first["unattributed"]) in sec
    assert str(len(art["seeds"])) in sec


# ---------------------------------------------------------------------------
# The confirmatory block's arithmetic (§4)
# ---------------------------------------------------------------------------

def test_pooling_weights_by_cells_not_by_seeds():
    """§11.2 pools over cells, so a seed with twice the cells carries twice the weight."""
    assert fh._pool([(0.0, 100), (1.0, 100)]) == pytest.approx(0.5)
    assert fh._pool([(0.0, 300), (1.0, 100)]) == pytest.approx(0.25)
    with pytest.raises(ValueError):
        fh._pool([(0.0, 0)])


def test_outcome_uses_the_upper_bound_only():
    """§4: the bar is the upper bound below zero, and the wrong direction is named."""
    assert fh.outcome({"low": -0.2, "high": -0.1}) == "improvement"
    assert fh.outcome({"low": 0.1, "high": 0.2}) == "reversed"
    assert fh.outcome({"low": -0.1, "high": 0.1}) == "no improvement detected"
    assert fh.outcome({"low": -0.1, "high": 0.0}) == "no improvement detected"


def test_interval_is_ordered_and_deterministic():
    weighted = [(0.10, 100), (0.12, 100), (0.15, 100), (0.05, 100), (0.30, 100)]
    first = fh.interval(weighted, resamples=500)
    again = fh.interval(weighted, resamples=500)
    assert first == again                      # the bootstrap seed is fixed
    assert first["low"] <= first["pooled_delta"] <= first["high"]
    assert first["level"] == fh.INTERVAL_LEVEL == 0.9833
    assert first["resamples"] == 500


def test_pooled_share_sums_margins_not_counts():
    """§11.5 pools the share as margin over margin; a count ratio is a different number."""
    def cell(margins, by_group):
        return {"attribution": {"margins": margins, "by_group": by_group}}
    # Counts say self-majority (9 of 10); margins say world-majority (0.9 of 1.0).
    pooled = fh._pooled_attribution([
        cell({"world": 0.9, "self": 0.0, "unattributed": 0.1, "positive": 1.0},
             {"world": 1, "self": 9, "unattributed": 0}),
    ])
    assert pooled["status"] == fh.fs.STATUS_WORLD
    assert pooled["share_world"] == pytest.approx(0.9)
    empty = fh._pooled_attribution([
        cell({"world": 0.0, "self": 0.0, "unattributed": 0.0, "positive": 0.0},
             {"world": 0, "self": 0, "unattributed": 0}),
    ])
    assert empty["status"] == fh.fs.STATUS_EMPTY


def test_confirmatory_mode_refuses_design_seeds():
    with pytest.raises(SystemExit):
        fh.refuse_design(fh.DESIGN_SEEDS[0])
    with pytest.raises(SystemExit):
        fh.refuse_design(20261201)
    assert fh.refuse_design(fh.CONFIRMATORY_SEEDS[0]) == fh.CONFIRMATORY_SEEDS[0]


def test_confirmatory_artifact_is_consistent():
    """The one confirmatory run's arithmetic must be internally coherent."""
    path = pathlib.Path("docs/functional_structure_confirmatory.json")
    if not path.exists():
        pytest.skip("confirmatory artifact not present in this checkout")
    art = json.loads(path.read_text(encoding="utf-8"))
    assert art["seeds"] == list(fh.CONFIRMATORY_SEEDS) and art["n"] == 15
    for window in ("primary", "co_primary"):
        block = art[window]
        assert block["interval"]["low"] <= block["pooled_delta"] <= block["interval"]["high"]
        assert block["passed"] == (block["interval"]["high"] < 0)
        assert block["outcome"] == fh.outcome(block["interval"])
        weighted = [(c["windows"][window]["delta"], c["windows"][window]["cells"])
                    for c in art["cells"]]
        assert block["pooled_delta"] == pytest.approx(fh._pool(weighted), abs=1e-6)
        # The share is a ratio of margins, and the status follows from it.
        att = block["attribution_pooled"]
        if att["share_self"] >= 0.5:
            assert att["status"] == fh.fs.STATUS_SELF
        elif att["share_unattributed"] >= 0.5:
            assert att["status"] == fh.fs.STATUS_UNATTRIBUTED
        else:
            assert att["status"] == fh.fs.STATUS_WORLD
    # A withheld transfer claim must be reflected in the headline, not only a field.
    if art["co_primary"]["attribution_pooled"]["withheld"]:
        assert "held-out generalization" in art["claim"] or "no improvement" in art["claim"]
