"""The K-supply discriminator separates prediction-cap from support evidence."""
import json
from pathlib import Path

from benchmarks import a1_k_supply_discriminator as diagnostic

DOC = json.loads(Path("docs/a1_k_supply_discriminator.json").read_text(
    encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert diagnostic.problems(DOC) == []
    assert diagnostic.self_test() == []
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert DOC["capacity"]["caps"] == [20, 40, 80]
    assert DOC["capacity"]["base_cap"] == 40


def test_capacity_moves_a_but_not_k():
    assert [DOC["capacity"]["results"][str(cap)]["total"]["A_available"]
            for cap in (20, 40, 80)] == [271, 353, 498]
    assert [DOC["capacity"]["results"][str(cap)]["total"]["K_available"]
            for cap in (20, 40, 80)] == [240, 244, 244]
    assert DOC["capacity"]["high_lift"] == 0.0
    assert DOC["capacity"]["low_drop"] == 0.016393
    assert DOC["capacity"]["high_seed_agreement"] == 1
    assert DOC["capacity"]["low_seed_agreement"] == 3
    assert DOC["capacity"]["signal"] is False


def test_support_gradient_is_real_but_not_sufficient():
    bins = {row["support_bin"]: row for row in DOC["support"]["bins"]}
    assert bins["2-3"]["K_density"] == 0.106667
    assert bins["4-7"]["K_density"] == 0.217391
    assert bins["8-15"]["K_density"] == 0.282937
    assert bins["16+"]["K_density"] == 0.409091
    assert DOC["support"]["monotone"] is True
    assert DOC["support"]["spread"] == 0.302424
    assert DOC["support"]["signal"] is True

    shared = {row["support_bin"]: row for row in
              DOC["matched_support"]["shared_bins"]}
    assert shared["8-15"]["density_16"] == 0.426829
    assert shared["8-15"]["density_28"] == 0.282937
    assert shared["16+"]["density_16"] == 0.687708
    assert shared["16+"]["density_28"] == 0.409091
    assert DOC["matched_support"]["weighted_gap"] == 0.249772
    assert DOC["matched_support"]["signal"] is False


def test_reading_is_support_associated_not_support_dominant():
    assert DOC["reading"] == {
        "capacity_signal": False,
        "support_signal": True,
        "matched_support_signal": False,
        "classification": "SUPPORT-ASSOCIATED, NOT FULLY EXPLANATORY",
    }


def test_page_is_current_and_does_not_claim_capacity():
    assert diagnostic.render(DOC) + "\n" == Path(
        "docs/A1-K-SUPPLY-DISCRIMINATOR.md").read_text(encoding="utf-8")
    text = Path("docs/A1-K-SUPPLY-DISCRIMINATOR.md").read_text(
        encoding="utf-8")
    assert "A/K decoupling" in text
    assert "closes **prediction-cap** capacity" in text
    assert "Support is real but not sufficient." in text
    assert "The next discriminator should target the carrier path directly" in text
    assert "not an A1 gate" in text
