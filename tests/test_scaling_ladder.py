"""The scaling ladder's guards and its diagnostics, without running a world.

The ladder itself is five engine runs; these tests cover the parts that decide
whether its numbers mean anything: the seed guard, the decision rule, the
clustering diagnostic, and the prefix check the slicing depends on.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

from benchmarks import scaling_ladder as sl

ROOT = pathlib.Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Guards and the rule
# ---------------------------------------------------------------------------

def test_a_study_seed_is_refused_before_a_database_opens():
    """Design and confirmatory seeds of both studies are off limits."""
    for seed in (20270401, 20270407, 20261201, 20261210):
        with pytest.raises(SystemExit):
            sl.refuse_study_seed(seed)


def test_the_methodology_block_is_itself_refused_when_not_asked_for():
    with pytest.raises(SystemExit):
        sl.refuse_study_seed(20270101)


def test_its_own_seeds_are_allowed_and_fresh():
    for seed in sl.SEEDS:
        assert sl.refuse_study_seed(seed) == seed
    assert not set(sl.SEEDS) & sl.FORBIDDEN_SEEDS


def test_the_verdict_table_is_the_one_that_was_committed():
    """§5, at its boundaries: the rule cannot drift with the numbers."""
    assert sl.verdict(None) == "not measurable"
    assert sl.verdict(0.10) == "replication-limited"
    assert sl.verdict(0.50) == "replication-limited"
    assert sl.verdict(0.51) == "both"
    assert sl.verdict(0.99) == "both"
    assert sl.verdict(1.00) == "resolution-limited"
    assert sl.verdict(3.00) == "resolution-limited"


# ---------------------------------------------------------------------------
# The diagnostics
# ---------------------------------------------------------------------------

def test_clustering_is_detected_not_assumed():
    """Two series with the same mean and spread: one clustered, one not.

    A block bootstrap must return a much larger error for the clustered series.
    If it did not, the quarters would be decoration.
    """
    import random
    rng = random.Random(11)
    clustered = ([0.10] * 100 + [0.12] * 100 + [0.08] * 100 + [0.11] * 100)
    independent = [0.10 + rng.gauss(0.0, 0.01) for _ in range(400)]
    c = sl.block_stats(clustered)
    i = sl.block_stats(independent)
    assert c["block_over_iid"] and i["block_over_iid"]
    assert c["block_over_iid"] > 5 * i["block_over_iid"], (c, i)
    assert abs(sum(clustered) / len(clustered) - sum(independent) / len(independent)) < 0.005


def test_consistency_counts_the_quarters():
    same = sl.block_stats([0.05] * 400)
    assert same["quarters_positive"] == sl.BLOCKS
    flipped = sl.block_stats([0.05] * 200 + [-0.05] * 200)
    assert flipped["quarters_positive"] == 2
    assert flipped["spread"] > 0


def test_runs_for_precision_is_derived_and_can_be_unreachable():
    assert sl.runs_for_precision(0.05, 0.01) == pytest.approx(4.76, abs=0.01)
    assert sl.runs_for_precision(0.05, 0.03) is None      # within already exceeds the target
    assert sl.runs_for_precision(None, 0.01) is None


# ---------------------------------------------------------------------------
# The slicing the ladder depends on
# ---------------------------------------------------------------------------

def test_the_window_arithmetic_and_the_dead_axis_guard():
    """A scale is a length; the scorer takes an end cycle. Empty must shout.

    The first ladder run passed a length where an end belonged, scored `150 -> 50`
    — no observations — and only failed when an empty list was averaged.
    """
    assert sl.window_end(1) == sl.PHASE_TRANSFER[1]
    assert sl.window_end(16) == 950
    with pytest.raises(AssertionError):
        sl.window_pairs(["alpha beta gamma delta"] * 100, 50)


def test_the_shorter_worlds_are_prefixes_of_the_longest():
    """Every scale must score the same world, just less of it."""
    check = sl.prefix_check(sl.SEEDS[0])
    assert check["consistent"], check["checked"]
    assert len(check["checked"]) == len(sl.SCALES)


# ---------------------------------------------------------------------------
# The document must contain the artifact's numbers
# ---------------------------------------------------------------------------

def test_the_document_quotes_the_artifact():
    """Every delta in the results table is the artifact's, to six decimals."""
    art_path = ROOT / sl.OUT
    doc = (ROOT / "docs/SCALING-LADDER.md").read_text(encoding="utf-8")
    if not art_path.exists():
        pytest.skip("the ladder has not been run yet")
    art = json.loads(art_path.read_text(encoding="utf-8"))
    if "| `1x` |" not in doc or "## 7." not in doc:
        pytest.skip("the results section has not been written yet")
    block = doc.split("## 7.", 1)[1]
    for label in sl.SCALES:
        row = art["summary"][label]
        for value in (row["delta_mean"], row["within_se_block_mean"],
                      row["delta_sd_between"]):
            assert f"{value:.6f}".lstrip("-") in block, (label, value)
        assert re.search(rf"`{re.escape(label)}`", block), label


def test_the_sign_section_quotes_the_artifact():
    """§8 restates the derived numbers, so they are checked, not remembered."""
    art_path = ROOT / sl.OUT
    if not art_path.exists():
        pytest.skip("the ladder has not been run yet")
    art = json.loads(art_path.read_text(encoding="utf-8"))
    if "sign_resolution" not in art:
        pytest.skip("the derived sign analysis has not been computed yet")
    doc = (ROOT / "docs/SCALING-LADDER.md").read_text(encoding="utf-8")
    if "## 8." not in doc:
        pytest.skip("the sign section has not been written yet")
    block = doc.split("## 8.", 1)[1]
    sign = art["sign_resolution"]
    for label, row in sign["scales"].items():
        for value in (row["p_correct"], row["p_correct_min"],
                      row["p_correct_max"], row["p_pooled_sign"]):
            assert f"{value:.3f}".lstrip("-") in block, (label, value)
        assert re.search(rf"`{re.escape(label)}`", block), label
    for world in sign["worlds"]:
        assert str(world["seed"]) in block, world["seed"]


# ---------------------------------------------------------------------------
# The sign question (docs §8)
# ---------------------------------------------------------------------------

def test_a_ratio_is_not_a_probability():
    """SE/delta is a t-statistic: 1 is 0.84, and 1.57 is still 0.74.

    The threshold was first read off that ratio, so the conversion is pinned: a
    ratio above one was taken to mean a run cannot resolve its own sign, which
    is not what a ratio of one implies.
    """
    assert sl.sign_probability(1.0, 1.0) == pytest.approx(0.8413, abs=5e-4)
    assert sl.sign_probability(1.0 / 1.57, 1.0) == pytest.approx(0.7379, abs=5e-4)
    assert sl.sign_probability(0.0, 1.0) == pytest.approx(0.5)
    assert sl.sign_probability(-3.0, 1.0) == sl.sign_probability(3.0, 1.0)
    assert sl.sign_probability(5.0, 0.0) == 1.0
    assert sl.sign_probability(0.5, None) == 0.0


def test_the_reference_scale_is_never_the_scale_it_judges():
    """A cell judged against its own estimate would manufacture the answer."""
    for label in sl.SCALES:
        ref = sl._reference_scale(label)
        assert ref != label and ref in sl.SCALES
    assert sl._reference_scale("16x") == "8x"


def _cell(seed, delta, ses):
    return {"seed": seed,
            "scales": {l: {"delta": delta, "se_block": ses[l]} for l in sl.SCALES}}


def test_the_sign_estimate_separates_a_strong_world_from_a_weak_one():
    """The statistic must rise with the effect and fall with the error."""
    ses = {"1x": 0.0088, "2x": 0.0038, "4x": 0.0033, "8x": 0.0026, "16x": 0.00145}
    out = sl.sign_resolution([_cell(1, 0.008, ses), _cell(2, 0.0004, ses)],
                             replicates=4_000)
    wide = out["scales"]["8x"]
    assert wide["p_correct_max"] > 0.97
    # Propagation lifts the weak world above its plug-in value (0.55 -> 0.67),
    # because a reference with its own error sometimes draws a larger effect.
    assert wide["p_correct_min"] < 0.72
    assert wide["p_correct_min"] < wide["plugin_mean"]
    assert wide["worlds_at_target"] == 1
    assert out["worlds"][0]["p_by_scale"]["16x"] > out["worlds"][0]["p_by_scale"]["1x"]
    # A world the window cannot resolve is reported, not rounded up to the target.
    assert out["worlds"][1]["window_for_target"] is None
    assert out["all_worlds_at_target_from"] is None


def test_the_decision_section_records_the_adopted_rule():
    """Adoption makes the window a convention, so it is checked, not asserted."""
    doc = (ROOT / "docs/SCALING-LADDER.md").read_text(encoding="utf-8")
    if "## 9." not in doc:
        pytest.skip("the decision section has not been written yet")
    block = doc.split("## 9.", 1)[1]
    for phrase in ("100-cycle", "`2x`", "0.90", "`rho`",
                   "No confirmatory seed allocation"):
        assert phrase in block, phrase
    art_path = ROOT / sl.OUT
    if not art_path.exists():
        pytest.skip("the ladder has not been run yet")
    sign = json.loads(art_path.read_text(encoding="utf-8")).get("sign_resolution")
    if not sign:
        pytest.skip("the derived sign analysis has not been computed yet")
    row = sign["scales"]["2x"]
    assert f"{row['p_correct_min']:.3f}" in block
    assert f"{row['p_correct_max']:.3f}" in block


def test_the_manual_records_the_adoption():
    """A decision the manual recommends has to stop reading as unadopted."""
    manual = (ROOT / "docs/USER-MANUAL.md").read_text(encoding="utf-8")
    rows = [l for l in manual.split("\n")
            if l.startswith("| 12 | **Decide the scaling rule")]
    assert len(rows) == 1
    assert "Adopted on 2026-11-02" in rows[0]
    assert "SCALING-LADDER.md` \u00a79" in rows[0]
    assert "not acted on" not in rows[0]
    revs = [l for l in manual.split("\n") if l.startswith("| 2026-11-02 |")]
    assert any("adopt" in l.lower() and "\u00a79" in l for l in revs)


def test_the_sign_simulation_is_reproducible_and_needs_data():
    ses = {l: 0.004 for l in sl.SCALES}
    cells = [_cell(1, 0.006, ses), _cell(2, 0.004, ses)]
    assert sl.sign_resolution(cells, replicates=500) == sl.sign_resolution(
        cells, replicates=500)
    with pytest.raises(AssertionError):
        sl.sign_resolution([])


# ---------------------------------------------------------------------------
# The audit of the sign estimator (docs §9)
# ---------------------------------------------------------------------------

def test_the_nesting_correlation_cannot_exceed_one():
    """The first version returned 1.78 at 16x: impossible, so it is pinned."""
    art_path = ROOT / sl.OUT
    if not art_path.exists():
        pytest.skip("the ladder has not been run yet")
    art = json.loads(art_path.read_text(encoding="utf-8"))
    nest = sl.nested_overlap(art["summary"])
    for label, row in nest.items():
        assert 0.0 < row["correlation_if_independent_pairs"] <= 1.0, (label, row)
        shorter = min(row["judged_pairs"], row["reference_pairs"])
        longer = max(row["judged_pairs"], row["reference_pairs"])
        assert row["overlap_of_smaller_in_larger"] == pytest.approx(shorter / longer, abs=1e-4)
        assert row["correlation_if_independent_pairs"] <= shorter / longer ** 0.5 + 0.1
    assert nest["16x"]["judged_contains_reference"] is True
    assert nest["2x"]["judged_contains_reference"] is False


def test_a_zero_effect_is_excluded_not_scored():
    """No sign to report means not measurable, not a large error (AGENTS 13b)."""
    out = sl.calibrate_sign_estimator(effects=(0.0, 1.0), worlds=3, runs=200,
                                      replicates=60, seed=7)
    zero = [r for r in out["rows"] if r["sign_undefined"]]
    assert len(zero) == len(sl.SCALES)
    assert out["excluded_zero_effect"] == len(sl.SCALES)
    scored = [r for r in out["rows"] if not r["sign_undefined"]]
    assert out["max_abs_calibration_error"] == max(abs(r["calibration_error"]) for r in scored)
    assert out["max_abs_calibration_error"] <= 0.2


def test_the_reference_rule_never_judges_a_scale_against_itself():
    for rule in sl.REFERENCE_RULES:
        for label in sl.SCALES:
            ref = sl.reference_label(label, rule)
            assert ref != label and ref in sl.SCALES
    assert sl.reference_label("2x", "fixed_8x") == "8x"
    assert sl.reference_label("16x", "fixed_8x") == "8x"
    with pytest.raises(SystemExit):
        sl.reference_label("2x", "nonsense")


def test_the_audit_section_quotes_the_artifact():
    audit_path = ROOT / sl.SIGN_AUDIT_OUT
    if not audit_path.exists():
        pytest.skip("the audit has not been run yet")
    doc = (ROOT / "docs/SCALING-LADDER.md").read_text(encoding="utf-8")
    if "## 9." not in doc:
        pytest.skip("the audit section has not been written yet")
    block = doc.split("## 9.", 1)[1]
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    for label, row in audit["nesting"].items():
        assert f"{row['correlation_if_independent_pairs']:.3f}" in block, label
    for rule, r in audit["reference_sensitivity"].items():
        assert f"{r['scales']['2x']['p_correct']:.3f}" in block, rule
    assert f"{audit['calibration']['max_abs_calibration_error']:.3f}" in block
