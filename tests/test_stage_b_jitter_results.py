"""The jitter result document restates its artifact; check the restatement mechanically."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _art() -> dict:
    return json.loads((ROOT / "docs" / "stage_b_jitter_diagnostic.json").read_text(encoding="utf-8"))


def _doc() -> str:
    return (ROOT / "docs" / "STAGE-B-JITTER-RESULTS.md").read_text(encoding="utf-8")


def test_the_reading_matches_the_pre_committed_rule():
    art = _art()
    cells = art["cells"]
    band = [c for c in cells if c["in_band"]]
    complete = [c for c in cells if len(c["runs"]) == len(art["design"]["seeds"])]
    overshoot = [c for c in cells if (c["max_displacement"] or 0) > art["design"]["shift"]]
    band_flips = [c for c in band if c["eligibility_flips"]]
    if len(complete) < len(cells):
        expected = "INCOMPLETE"
    elif overshoot:
        expected = "R3"
    elif band_flips:
        expected = "R2"
    else:
        expected = "R1"
    assert art["reading"] == expected, (art["reading"], expected)
    assert f"**Reading: {expected}.**" in _doc()


def test_the_band_table_matches_the_artifact():
    art = _art()
    doc = _doc()
    by_cfg = {}
    for c in art["cells"]:
        if not c["in_band"]:
            continue
        row = by_cfg.setdefault(c["configuration"], {"band": 0, "flips": 0, "max": 0})
        row["band"] += 1
        row["flips"] += 1 if c["eligibility_flips"] else 0
        row["max"] = max(row["max"], c["max_displacement"] or 0)
    for cfg, v in sorted(by_cfg.items()):
        assert f"| `{cfg}` | {v['band']} | {v['flips']} | {v['max']} |" in doc


def test_displacement_extremes_match_the_artifact():
    art = _art()
    doc = _doc()
    disp = [c["max_displacement"] for c in art["cells"] if c["max_displacement"] is not None]
    moved = [c for c in art["cells"] if c["max_displacement"]]
    assert f"the largest absolute onset difference from the committed\nvalue was **{max(disp)}** cycles" in doc
    assert f"**{len(moved)}** cells moved at all" in doc


def test_every_run_completed_and_no_placeholder():
    art = _art()
    assert art["design"]["runs_present"] == art["design"]["runs_expected"]
    assert all(len(c["runs"]) == len(art["design"]["seeds"]) for c in art["cells"])
    assert not re.findall(r"\{[A-Za-z_][^{}]*\}", _doc())


def test_a_voided_reading_names_the_cells_that_broke_the_ceiling():
    art = _art()
    doc = _doc()
    if art["reading"] != "R3":
        return
    over = [c for c in art["cells"] if (c["max_displacement"] or 0) > art["design"]["shift"]]
    assert over, "R3 without a cell beyond the ceiling"
    for c in over:
        assert f"`{c['configuration']}` {c['seed']} ({c['max_displacement']} cycles)" in doc


def test_it_does_not_claim_an_eligibility_finding_when_void():
    art = _art()
    doc = _doc()
    if art["reading"] == "R3":
        assert "no conclusion is" in doc
        assert "changes no denominator" not in doc
