"""The jitter diagnostic's exposure table is computed from the assembly; check it against it.

The document claims a band, a population and a cost. All three are recomputed here from the
committed artifacts, so the definition cannot drift away from the block it describes.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARGIN = 101
STRIDE = 20
REDRAWS = 3


def _doc() -> str:
    return (ROOT / "docs" / "STAGE-B-JITTER-DIAGNOSTIC.md").read_text(encoding="utf-8")


def _cells() -> list:
    return json.loads((ROOT / "docs" / "stage_b_runner.json").read_text(encoding="utf-8"))["cells"]


def _shift() -> int:
    check = json.loads((ROOT / "docs" / "stage_b_rerun_check.json").read_text(encoding="utf-8"))
    return max(abs(c["comparison"]["onset_difference"]) for c in check["cells"]
               if c["comparison"]["onset_difference"] is not None)


def test_exposure_table_matches_the_assembly():
    doc = _doc()
    cells = _cells()
    shift = _shift()
    by_cfg = {}
    for c in cells:
        by_cfg.setdefault(c["configuration"], []).append(c)
    for cfg in sorted(by_cfg):
        group = by_cfg[cfg]
        horizon = {c["horizon"] for c in group}
        assert len(horizon) == 1
        clock = horizon.pop() - MARGIN
        scored = [c for c in group if c["onset"] is not None]
        band = [c for c in scored if abs(c["onset"] - clock) <= shift]
        reach_in = [c for c in scored if 0 < c["onset"] - clock <= shift]
        reach_out = [c for c in scored if -shift <= c["onset"] - clock < 0]
        row = (f"| `{cfg}` | {clock} | {len(group)} | {len(group) - len(scored)} | "
               f"{len(band)} | {len(reach_in)} | {len(reach_out)} |")
        assert row in doc, row


def test_the_eligibility_identity_holds_for_every_cell():
    for c in _cells():
        if c["onset"] is not None:
            assert c["eligible"] == (c["onset"] + MARGIN <= c["horizon"]), c["seed"]


def test_band_and_cost_are_stated_as_computed():
    doc = _doc()
    cells = _cells()
    shift = _shift()
    by_cfg = {}
    for c in cells:
        by_cfg.setdefault(c["configuration"], []).append(c)
    band, strided_ids = [], set()
    for cfg, group in by_cfg.items():
        clock = next(iter({c["horizon"] for c in group})) - MARGIN
        band += [c for c in group if c["onset"] is not None and abs(c["onset"] - clock) <= shift]
        for c in sorted(group, key=lambda c: c["seed"])[::STRIDE]:
            strided_ids.add((c["configuration"], c["seed"]))
    band_ids = {(c["configuration"], c["seed"]) for c in band}
    extra = [c for c in cells if (c["configuration"], c["seed"]) in strided_ids - band_ids]
    runs = REDRAWS * (len(band) + len(extra))
    cycles = REDRAWS * sum(c["cycles_run"] for c in band + extra)
    assert f"{runs} cell-runs" in doc
    assert f"{cycles:,} cycles" in doc
    assert f"{len(band)}" in doc


def test_it_is_committed_unrun_and_has_a_control_that_can_void_it():
    doc = _doc()
    assert "defined and committed unrun" in doc
    assert "no conclusion is drawn" in doc
    assert "No cell has been re-executed" in doc
    assert "§D15" in doc


def test_no_template_placeholders():
    assert not re.findall(r"\{[A-Za-z_][^{}]*\}", _doc())
