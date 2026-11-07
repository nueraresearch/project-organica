"""DENSITY-PADDING-1: the registration, the phase gate, and a criterion that can fire.

Every number is recomputed from the committed artifacts. The negative control is part of the file
because a monotonicity criterion that cannot fail on the profile it was written for is decoration.
"""

import json
from pathlib import Path

import pytest

from benchmarks import density_padding as dp

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "density_padding_prereg.json"
RUN = ROOT / "docs" / "density_padding_run.json"
RESULT = ROOT / "docs" / "density_padding_result.json"
DOC = ROOT / "docs" / "DENSITY-PADDING-PREREGISTRATION.md"
A2_PREREG = ROOT / "docs" / "density_interaction_a2_prereg.json"
A2_RESULT = ROOT / "docs" / "density_interaction_a2_result.json"


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def test_the_registration_precedes_its_run():
    body = json.loads(PREREG.read_text(encoding="utf-8"))
    seeds, densities = dp.seeds_and_densities()
    assert body["prereg"] == "DENSITY-PADDING-1"
    assert body["date"] == "2026-11-07"
    assert body["amends"] is None
    assert body["status"] == "RUN"
    assert body["run"]["cells"] == len(seeds) * len(densities) * 2
    assert body["run"]["seeds"] == len(seeds)
    assert body["run"]["gate_passed"] is True


def test_the_registration_is_not_rewritten_once_committed():
    with pytest.raises(SystemExit):
        dp.write_registration()


def test_the_registered_block_is_not_amended():
    a2 = json.loads(A2_PREREG.read_text(encoding="utf-8"))
    assert a2["design"]["schemes"] == ["primary", "sensitivity"]
    assert a2["status"].startswith("RUN")


def test_the_phase_gate_holds_and_the_primary_stream_fails_it():
    gate = dp.phase_gate()
    seeds, densities = dp.seeds_and_densities()
    assert gate["passed"]
    assert [row["rho_world"] for row in gate["rows"]] == densities
    assert all(row["equal_exposure"] and row["ends_on_filler"] for row in gate["rows"])
    assert gate["primary_control"]["passed"] is False
    assert len(gate["primary_control"]["distinct_exposure_ratios"]) > 1


def test_the_third_scheme_is_whole_passes_and_leaves_the_other_schemes_alone():
    seeds, densities = dp.seeds_and_densities()
    for rho in densities:
        base = dp.base_stream(seeds[0], rho, dp.FILLER)
        events = dp.stream(seeds[0], rho, dp.SCHEME, dp.FILLER)
        assert len(events) == len(base) * -(-dp.TOTAL_EVENTS // len(base))
        assert len(dp.stream(seeds[0], rho, "primary", dp.FILLER)) == dp.TOTAL_EVENTS
        assert len(dp.stream(seeds[0], rho, "sensitivity", dp.FILLER)) == len(base)
    with pytest.raises(ValueError):
        dp.stream(seeds[0], 0.1, "whole-cycles", dp.FILLER)


def test_the_criteria_are_recomputed_from_the_cells():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    cells = json.loads(RUN.read_text(encoding="utf-8"))["cells"]
    seeds, densities = dp.seeds_and_densities()
    assert len(cells) == len(seeds) * len(densities) * 2
    index = {(c["arm"], round(c["rho_world"], 6), c["seed"]): c for c in cells}
    means = {}
    for rho in densities:
        diffs = [index[("intra_cell_excluded", rho, s)]["precision"]
                 - index[("control", rho, s)]["precision"] for s in seeds]
        means[rho] = sum(diffs) / len(diffs)
        assert abs(means[rho] - result["profile"]["%.1f" % rho]["delta_mean"]) < 5e-7
    steps = [means[b] - means[a] for a, b in zip(densities, densities[1:])]
    for step, recorded in zip(steps, result["steps"]):
        assert abs(step - recorded["step"]) < 5e-7
    assert result["criteria"]["P1"]["passed"] is all(step >= 0 for step in steps)
    assert result["criteria"]["P2"]["passed"] is (means[0.6] >= means[0.1])


def test_the_negative_control_shows_the_criterion_can_fire():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    a2 = json.loads(A2_RESULT.read_text(encoding="utf-8"))
    seeds, densities = dp.seeds_and_densities()
    primary = [a2["criteria"]["profile"]["%.1f" % rho]["primary"]["delta_precision_mean"]
               for rho in densities]
    assert any(right - left < 0 for left, right in zip(primary, primary[1:]))
    assert result["negative_control"]["P1_passed"] is False


def test_the_document_quotes_the_artifact():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    flat = _flat()
    assert result["decision"]["verdict"] in flat
    assert "## 8. Result" in flat
    for rho, row in result["profile"].items():
        line = "| %s | %.4f | %.4f | %.4f | %d of %d |" % (
            rho, row["control_mean"], row["treated_mean"], row["delta_mean"],
            row["seeds_positive"], row["of"])
        assert line in flat, line
    for rho, row in result["slots"].items():
        line = "| %s | %.2f | %.2f | %.2f |" % (
            rho, row["control_intra"], row["control_cross"], row["treated_cross"])
        assert line in flat, line
    for step in result["steps"]:
        assert "- %.1f -> %.1f: %+.4f" % (step["from"], step["to"], step["step"]) in flat
    assert "{" not in flat and "}" not in flat


def test_the_shared_grid_is_declared_so_the_freshness_audit_excuses_it():
    """The exemption is earned by declaring the inheritance, not by naming an artifact."""
    from benchmarks import run_density_interaction as runner
    body = json.loads(PREREG.read_text(encoding="utf-8"))
    assert body["amends"] is None
    assert "density_interaction_a2_prereg.json" in str(body["inherits"])
    report = runner.freshness_audit()
    assert report["passed"], report["collisions"]
    a2_seeds = set(dp.seeds_and_densities()[0])
    cells = json.loads(RUN.read_text(encoding="utf-8"))["cells"]
    assert {c["seed"] for c in cells} == a2_seeds
