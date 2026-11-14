"""The cross-world K dilution report is descriptive and internally consistent."""
import json
from pathlib import Path

from benchmarks import a1_k_dilution as report

DOC = json.loads(Path("docs/a1_k_dilution.json").read_text(encoding="utf-8"))


def test_report_is_clean_and_governed_off():
    assert report.problems(DOC) == []
    assert report.self_test() == []
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert "NO ARM, NO THRESHOLD, NO REDESIGN" in DOC["status"]


def test_headline_supply_does_not_scale_with_edges():
    dilution = DOC["dilution"]
    assert (dilution["edges_before"], dilution["edges_after"]) == (383, 1000)
    assert (dilution["A_before"], dilution["A_after"]) == (279, 353)
    assert (dilution["K_before"], dilution["K_after"]) == (242, 244)
    assert dilution["edges_added"] == 617
    assert dilution["K_added"] == 2
    assert dilution["K_growth"] == 0.008264
    assert (dilution["K_density_before"], dilution["K_density_after"]) == (
        0.631854, 0.244,
    )
    assert dilution["K_density_change"] == -0.387854


def test_per_seed_k_supply_and_density():
    assert [row["K_available"] for row in DOC["worlds"]["16-tag"]["per_seed"]] == [
        40, 37, 46, 42, 39, 38,
    ]
    assert [row["K_available"] for row in DOC["worlds"]["28-tag"]["per_seed"]] == [
        23, 40, 42, 55, 47, 37,
    ]
    assert [row["K_density"] for row in DOC["worlds"]["28-tag"]["per_seed"]] == [
        0.136095, 0.239521, 0.244186, 0.333333, 0.278107, 0.234177,
    ]


def test_old_edges_are_not_protected():
    old16 = next(row for row in DOC["worlds"]["16-tag"]["by_family"]
                 if row["label"] == "old-old")
    old28 = next(row for row in DOC["worlds"]["28-tag"]["by_family"]
                 if row["label"] == "old-old")
    new28 = next(row for row in DOC["worlds"]["28-tag"]["by_family"]
                 if row["label"] == "old-new")
    assert (old16["candidate_edges"], old16["K_available"]) == (383, 242)
    assert (old28["candidate_edges"], old28["K_available"]) == (296, 56)
    assert old28["K_density"] == 0.189189
    assert new28["K_density"] == 0.263653
    assert new28["K_density"] > old28["K_density"]


def test_transition_supply_is_nearly_constant():
    t16 = {row["label"]: row for row in DOC["worlds"]["16-tag"]["by_transition"]}
    t28 = {row["label"]: row for row in DOC["worlds"]["28-tag"]["by_transition"]}
    assert (t16["flip_p"]["candidate_edges"], t16["flip_p"]["K_available"]) == (191, 145)
    assert (t28["flip_p"]["candidate_edges"], t28["flip_p"]["K_available"]) == (517, 146)
    assert (t16["flip_q"]["candidate_edges"], t16["flip_q"]["K_available"]) == (192, 97)
    assert (t28["flip_q"]["candidate_edges"], t28["flip_q"]["K_available"]) == (483, 98)


def test_u_quartile_gradient_survives_but_not_at_60_per_seed():
    q16 = {row["label"]: row for row in DOC["worlds"]["16-tag"]["by_U_quartile"]}
    q28 = {row["label"]: row for row in DOC["worlds"]["28-tag"]["by_U_quartile"]}
    assert (q16["Q1"]["K_density"], q16["Q4"]["K_density"]) == (
        0.21875, 0.915789,
    )
    assert (q28["Q1"]["K_density"], q28["Q4"]["K_density"]) == (
        0.110672, 0.487903,
    )
    assert q28["Q4"]["K_available"] == 121
    assert q28["Q4"]["K_available"] / 6 < 60


def test_page_is_current_and_states_the_limit():
    assert report.render(DOC) + "\n" == Path("docs/A1-K-DILUTION.md").read_text(
        encoding="utf-8")
    text = Path("docs/A1-K-DILUTION.md").read_text(encoding="utf-8")
    assert "more edges did not buy more K" in text
    assert "The edge count is not the constraint." in text
    assert "not a conservation law" in text
    assert "does not identify a cause" in text
