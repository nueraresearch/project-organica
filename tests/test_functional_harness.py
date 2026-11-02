"""The engine binding may only run the design block, and its gates must be able to fail."""
from __future__ import annotations

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
