"""The computed sign resolution must be reproducible from its module and quoted from its artifact."""

from pathlib import Path
import json

import pytest

import benchmarks.sign_resolution_behavior as srb

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "docs/sign_resolution_structure_behavior.json"
PROTOCOL = ROOT / "docs/STRUCTURE-BEHAVIOR-DESIGN.md"


def _art():
    if not ART.exists():
        pytest.skip("the sign resolution has not been computed yet")
    return json.loads(ART.read_text(encoding="utf-8"))


def test_the_reference_rule_is_named_and_is_a_relation_not_a_power_target():
    art = _art()
    assert art["reference_rule"]["name"] == "smallest relation of interest"
    assert art["reference_rule"]["rho"] == 0.50
    assert art["threshold"] == 0.90
    assert art["level"] == 0.9833
    assert art["reference_rule"]["why"].strip()


def test_the_analytic_column_reproduces_from_the_module():
    art = _art()
    grid = art["grid"]["analytic"]
    for n in ("10", "50", "100"):
        for rho in ("0.30", "0.50", "0.70"):
            assert abs(float(grid[n][rho]) - srb.analytic_p(int(n), float(rho))) < 1e-3


def test_minimum_n_is_monotone_in_the_relation():
    mins = _art()["minimum_n"]
    seq = [mins[k] for k in ("0.30", "0.40", "0.50", "0.60", "0.70")]
    assert seq == sorted(seq, reverse=True), seq
    assert mins["0.50"] == 48


def test_the_bootstrap_simulation_agrees_with_the_closed_form():
    rows = _art()["bootstrap_validation"]["rows"]
    assert len(rows) >= 5
    for row in rows:
        tolerance = 4.0 * row["monte_carlo_se"] + 0.01
        assert abs(row["difference"]) <= tolerance, row


def test_the_protocol_quotes_the_artifact_rather_than_a_memory():
    art = _art()
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "docs/sign_resolution_structure_behavior.json" in text
    n_ref = str(art["verdict"]["reference_n"])
    assert f"**{n_ref}** worlds per configuration" in text
    assert f"{art['verdict']['p_at_reference_n']:.3f}" in text
    for key, value in art["minimum_n"].items():
        assert f"| {value} |" in text or f"{value} |" in text, (key, value)
    assert "No seed is allocated by this document" in text


def test_the_bound_is_stated_in_both_directions():
    """A probability upper bound is a floor on the worlds required, and the artifact must say so."""
    art = _art()
    assert art["bound_direction"]["probability"] == "upper bound"
    assert "floor" in art["bound_direction"]["minimum_n"]
    assert art["status"].startswith("provisional")
    assert any("posterior" in item for item in art["what_the_number_is_not"])


def test_attenuation_prices_the_error_and_only_ever_raises_the_requirement():
    art = _art()
    rows = art["attenuation"]["rows"]
    assert len(rows) >= 4
    req = [r["worlds_required"] for r in rows]
    assert req == sorted(req), req          # weaker instrument, more worlds
    assert rows[0]["worlds_required"] == art["verdict"]["reference_n"]
    for row in rows:
        assert abs(row["measured_rho"] - art["reference_rule"]["rho"] * row["reliability"]) < 1e-3
        assert row["worlds_required"] == srb.minimum_n(row["measured_rho"])


def test_the_protocol_carries_the_corrected_direction_and_the_table():
    art = _art()
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "floor, not a ceiling" in text
    assert "not a posterior probability" in text
    assert "lag-1 correlation" in text
    for row in art["attenuation"]["rows"]:
        cell = f"| {row['reliability']:.2f} | {row['measured_rho']:.2f} | {row['worlds_required']} |"
        assert cell in text, cell
