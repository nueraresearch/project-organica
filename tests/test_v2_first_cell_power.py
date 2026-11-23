"""The power diagnostic is computed from the measured null and checks its own arithmetic."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
import statistics
from pathlib import Path

from benchmarks import v2_first_cell_power as power

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "v2_first_cell_power.json"
PAGE = ROOT / "docs" / "V2-FIRST-CELL-POWER.md"
NULL = ROOT / "docs" / "v2_first_cell_null.json"


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_it_reads_the_measured_null_and_keeps_its_bias() -> None:
    nulls = json.loads(NULL.read_text(encoding="utf-8"))
    record = _record()
    assert record["kind"] == "v2_first_cell_power"
    assert "NOT A CELL" in record["status"] and "NOT A VERDICT" in record["status"]
    assert record["source"]["null_seeds"] == [row["seed"] for row in nulls["per_seed"]]
    bias = statistics.fmean(row["d"] for row in nulls["per_seed"])
    assert abs(record["source"]["null_mean_d"] - bias) < 1e-6


def test_power_is_monotone_and_zero_at_zero_benefit() -> None:
    curve = _record()["power_curve"]
    powers = [row["power"] for row in curve]
    assert powers == sorted(powers)
    assert curve[0]["benefit"] == 0.0 and curve[0]["power"] == 0.0


def test_the_detectable_benefits_are_ordered_and_consistent() -> None:
    record = _record()
    mde = record["mde"]
    assert mde["0.8"] <= mde["0.9"] <= mde["0.95"]
    for target, benefit in mde.items():
        assert abs((record["source"]["null_mean_d"] - benefit) - record["required_mean_d"][target]) < 1e-6
    assert record["power_at_null_bias"] <= 0.01


def test_the_curve_actually_reaches_its_targets() -> None:
    record = _record()
    for target in ("0.8", "0.9", "0.95"):
        mde = record["mde"][target]
        at_or_above = [row for row in record["power_curve"] if row["benefit"] >= mde]
        assert at_or_above and at_or_above[0]["power"] >= float(target), target


def test_the_page_restates_the_artifact() -> None:
    record = _record()
    page = PAGE.read_text(encoding="utf-8")
    for target in ("0.8", "0.9", "0.95"):
        assert "%.6f" % record["mde"][target] in page
    assert "%.6f" % record["source"]["null_mean_d"] in page
    assert "%.8f" % record["convergence"]["max_abs_upper_bound_delta"] in page


def test_the_check_entry_point_passes() -> None:
    power.check()
