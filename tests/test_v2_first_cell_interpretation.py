"""The pre-cell reading must say what each outcome authorises, in the artifacts' own numbers.

The document is adopted before the cell exists; a reading chosen after the interval is seen
is not a reading. These checks keep it tied to the artifacts it restates.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "DECISION-V2-FIRST-CELL-INTERPRETATION.md"


def text():
    return DOC.read_text(encoding="utf-8")


def normalised():
    return text().replace("\u2212", "-")


def artifact(name):
    return json.loads((ROOT / "docs" / name).read_text(encoding="utf-8"))


def num(value, places=6):
    return f"{value:.{places}f}"


def test_the_four_outcomes_are_defined():
    t = normalised()
    for label in ("PASS", "BOOKKEEPING", "REVERSAL", "VOID"):
        assert f"**{label}**" in t
    assert "entirely below zero" in t
    assert "includes zero" in t
    assert "entirely above zero" in t
    assert "no admissible comparison" in t


def test_the_null_numbers_are_the_null_artifact():
    t = normalised()
    null = artifact("v2_first_cell_null.json")
    calibration = null["calibration"]
    assert num(null["summary"]["mean_d"]) in t
    assert num(null["summary"]["sd_d"]) in t
    assert f"{calibration['cells']:,}" in t
    assert str(calibration["includes_zero_rate"]) in t
    assert str(calibration["excludes_above_zero"]) in t
    assert "+0.000847" in t
    assert "0.000645" in t


def test_the_power_and_handicap_numbers_are_their_artifacts():
    t = normalised()
    power = artifact("v2_first_cell_power.json")
    handicap = artifact("v2_first_cell_handicap.json")
    for value in power["mde"].values():
        assert num(value) in t
    assert num(power["required_mean_d"]["0.9"]) in t
    assert "+0.001312" in t
    assert "-0.000465" in t
    assert "2.571" in t
    assert "0.783" in t


def test_the_selection_sign_reversal_is_fixed_with_both_measurements():
    t = normalised()
    null = artifact("v2_first_cell_mass_match.json")
    planted = artifact("v2_first_cell_planted_selection.json")
    assert num(null["summary"]["mean_delta_keys"]) == "-0.000497"
    assert "-0.000497" in t
    assert "+0.002091" in t
    assert num(planted["intervals"]["keys"]["lo"]) in t
    assert num(planted["intervals"]["keys"]["hi"]) in t
    assert "+0.000834" in t
    assert "-0.000036" in t
    assert "+0.002555" in t
    assert "0.051685" in t
    ratio = planted["summary"]["mean_delta_keys"] / abs(planted["summary"]["mean_d_maintained"]) * 100
    assert f"{ratio:.2f}%" == "4.05%"
    assert f"{ratio:.2f}%" in t


def test_void_is_not_a_negative_result():
    t = text()
    assert "not a negative result" in t
    assert "not evidence for or against" in t
    assert "BOOKKEEPING is an admissible comparison" in t


def test_no_cell_has_run_and_the_decision_is_indexed():
    reservations = artifact("a1_seed_reservations.json")
    block = [r for r in reservations["reservations"]
             if r["owner"] == "docs/v2_first_cell_seeds.json"][0]
    assert block["spent"] is True
    assert block["seeds"] == list(range(20910101, 20910111))
    assert not list((ROOT / "docs").glob("v2_first_cell_cell*.json"))
    data = artifact("decisions.json")
    row = [d for d in data["decisions"]
           if d["decision_id"] == "DECISION-V2-FIRST-CELL-INTERPRETATION"][0]
    assert row["status"] == "ADOPTED"
    assert len(row["chosen"]) == 5
