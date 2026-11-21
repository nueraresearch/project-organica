"""The scaled sizing is reproducible from its artifact, and its page reports the negative result."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

from benchmarks import v2_primitive_sizing_scaled as scaled

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs" / "v2_primitive_sizing_scaled.json"
DOC = ROOT / "docs" / "V2-PRIMITIVE-SIZING-SCALED.md"


def _doc() -> dict:
    return json.loads(ART.read_text(encoding="utf-8"))


def test_the_page_is_rendered_from_the_artifact() -> None:
    assert DOC.read_text(encoding="utf-8") == scaled.render_doc(_doc())


def test_the_three_worlds_vary_only_the_axis_they_claim() -> None:
    worlds = {w["label"]: w for w in _doc()["worlds"]}
    assert set(worlds) == {"reference-120", "longer-480", "denser-2x"}
    assert {w["seed"] for w in worlds.values()} == {scaled.SEED}
    assert worlds["longer-480"]["cycles"] == 4 * worlds["reference-120"]["cycles"]
    assert worlds["denser-2x"]["events_per_cycle"] == 2 * worlds["reference-120"]["events_per_cycle"]


def test_the_comparison_matches_the_worlds() -> None:
    doc = _doc()
    assert doc["comparison"]["objects_at_m2"] == [w["admission"]["m>=2"]["composites"] for w in doc["worlds"]]
    assert doc["comparison"]["bytes_per_composite_at_m2"] == [
        w["admission"]["m>=2"]["bytes_per_composite"] for w in doc["worlds"]]


def test_the_seed_is_registered_before_it_is_used() -> None:
    reservations = json.loads((ROOT / "docs" / "a1_seed_reservations.json").read_text(encoding="utf-8"))
    owners = [r for r in reservations["reservations"]
              if "docs/v2_primitive_sizing_scaled.json" in (r["owner"], *r.get("restated_by", []))]
    assert owners and scaled.SEED in owners[0]["seeds"]


def test_the_page_states_the_result_it_found() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "{" not in text
    assert "The expectation did not hold" in text
    assert "Nothing here is amortising" in text
    assert "untested" in text or "not confirmed" in text
