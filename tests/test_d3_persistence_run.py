"""The D3 result must stay the frozen scorer's result, with its seed defect visible."""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer
import json
from pathlib import Path

import pytest

from benchmarks import d3_persistence_prereg as P
from benchmarks import d3_persistence_run as R

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs/d3_persistence_run.json"
DOC = ROOT / "docs/D3-PERSISTENCE-RESULT.md"


def test_the_result_is_the_frozen_scorers_reading():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    label, details = P.verdict(P.prereg(), artifact)
    assert label == artifact["verdict"] == "PERSISTENCE REPAIRED"
    assert details == artifact["details"]
    assert len(artifact["cells"]) == 24


def test_the_degenerate_seed_axis_is_recorded_not_hidden():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["seed_axis"]["identical"] is True
    assert artifact["seed_axis"]["effective_n"] == 1
    assert "seed axis is degenerate" in DOC.read_text(encoding="utf-8")
    assert "PERSISTENCE REPAIRED" in DOC.read_text(encoding="utf-8")


def test_a_degenerate_run_is_refused_before_it_can_be_reported(monkeypatch, tmp_path):
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    out = tmp_path / "d3_persistence_run.json"
    doc = tmp_path / "D3-PERSISTENCE-RESULT.md"
    monkeypatch.setattr(R, "ARTIFACT", out)
    monkeypatch.setattr(R, "DOC", doc)
    monkeypatch.setattr(R, "build", lambda: artifact)
    with pytest.raises(SystemExit, match="single-world pass cannot be reported"):
        R.finish()
    assert not out.exists()
    assert not doc.exists()
