"""The handicap decomposition adds up, and no non-trivial readout is unbiased on the null."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

from benchmarks import v2_first_cell_handicap as handicap

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "v2_first_cell_handicap.json"
PAGE = ROOT / "docs" / "V2-FIRST-CELL-HANDICAP.md"
NULL = ROOT / "docs" / "v2_first_cell_null.json"


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_decomposition_is_the_stored_null_and_adds_up() -> None:
    nulls = json.loads(NULL.read_text(encoding="utf-8"))["per_seed"]
    beta_only = [row["arms"]["B"]["log_loss"] - row["arms"]["A"]["log_loss"] for row in nulls]
    net = [row["d"] for row in nulls]
    dec = _record()["decomposition"]
    assert abs(dec["beta_only_mean"] - statistics.fmean(beta_only)) < 1e-6
    assert abs(dec["net_mean"] - statistics.fmean(net)) < 1e-6
    assert abs(dec["beta_only_mean"] + dec["revision_mean"] - dec["net_mean"]) < 1e-9
    assert dec["revision_mean"] < 0 < dec["beta_only_mean"]


def test_the_revision_rule_reduces_the_member_mass() -> None:
    mass = _record()["mass"]
    assert mass["mean_edges_maintained"] < mass["mean_edges_frozen"]
    assert mass["mean_mutations"] > 0 and mass["mean_composites"] > 0


def test_every_non_trivial_readout_is_positive_and_mixtures_rise_with_lambda() -> None:
    record = _record()
    for lam, arms in record["mixture"].items():
        for arm, row in arms.items():
            assert row["mean"] > 0, (lam, arm)
    assert record["mixture"]["0.2"]["B"]["mean"] > record["mixture"]["0.1"]["B"]["mean"]
    assert record["mixture"]["0.2"]["C"]["mean"] > record["mixture"]["0.1"]["C"]["mean"]
    assert record["mixture"]["0.1"]["C"]["mean"] > record["decomposition"]["net_mean"]
    assert record["beta_zero"]["B"] == record["beta_zero"]["C"] == 0.0


def test_the_verdict_is_no_and_the_alternative_is_priced_in() -> None:
    record = _record()
    assert record["verdict"]["unbiased_possible"] is False
    power = json.loads((ROOT / "docs" / "v2_first_cell_power.json").read_text(encoding="utf-8"))
    page = PAGE.read_text(encoding="utf-8")
    assert "%.6f" % power["mde"]["0.9"] in page
    assert "%.6f" % power["required_mean_d"]["0.9"] in page
    assert "%.6f" % record["decomposition"]["beta_only_mean"] in page
    assert "%.6f" % record["decomposition"]["revision_mean"] in page
    assert "%.6f" % record["mixture"]["0.1"]["C"]["mean"] in page


def test_the_check_entry_point_passes() -> None:
    handicap.check()
