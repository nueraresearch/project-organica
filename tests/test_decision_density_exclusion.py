"""The adoption record must quote the committed result, not a remembered one.

Every figure it states is recomputed here from `docs/density_interaction_a2_result.json`, and the
scope sentences are asserted so a later edit cannot quietly widen the claim to behaviour or to the
descriptive slope.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "DECISION-DENSITY-EXCLUSION.md"
RESULT = ROOT / "docs" / "density_interaction_a2_result.json"
PREREG = ROOT / "docs" / "density_interaction_a2_prereg.json"
RUN = ROOT / "docs" / "density_interaction_a2_run.json"


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def test_the_record_is_dated_recorded_and_not_an_implementation():
    flat = _flat()
    assert "**Date**: 2026-11-07" in flat.replace("*", "*")
    assert "RECORDED" in flat
    assert "NOT IMPLEMENTED" in flat
    assert "rule 2" in flat and "rule 30" in flat
    assert "No code changed with this record" in flat


def test_every_quoted_figure_is_the_result_s_own():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    flat = _flat()
    c1 = result["criteria"]["C1_sparse_level"]
    slope = result["criteria"]["descriptive_interaction"]
    exposure = result["criteria"]["exposure"]
    tokens = ["%.6f" % c1["mean"], "%.6f" % c1["interval"][0],
              "%.6f" % c1["interval"][1], "%.2f" % c1["bar"],
              "%d of %d" % (c1["seeds_positive"], c1["of"]),
              "%.6f" % slope["mean"], "%.6f" % slope["interval"][0],
              "%.6f" % slope["interval"][1],
              "%.6f" % exposure["sensitivity_sparse_mean"],
              "%d of %d" % (exposure["seeds_positive"], exposure["of"])]
    for token in tokens:
        assert token in flat, token
    assert str(result["cells"]) in flat
    assert result["gates"]["all_passed"] is True
    assert result["decision"]["verdict"] in flat.replace("\n", " ")


def test_the_decision_is_the_level_and_the_slope_is_refused_as_a_reason():
    flat = _flat()
    assert "sparse-end level" in flat
    assert "descriptive" in flat and "not judged" in flat
    assert "not the reason for this decision" in flat
    assert "not monotone" in flat
    assert "pinned" in flat


def test_the_scope_refuses_behaviour_generality_and_the_slope():
    flat = _flat()
    assert "does not cover" in flat
    assert "Behaviour." in flat
    assert "One world family" in flat
    assert "cap 20" in flat
    assert "must not be read as one" in flat


def test_the_withdrawn_admission_rule_is_not_revived():
    flat = _flat()
    assert "DECISION-ADMISSION-RULE.md" in flat
    assert "withdrawn" in flat
    assert "does not revive it" in flat


def test_the_predecessor_block_stays_held():
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    predecessor = json.loads((ROOT / "docs" / "density_interaction_prereg.json")
                             .read_text(encoding="utf-8"))
    assert predecessor["status"].startswith("HELD")
    assert prereg["held_predecessor"]["prereg"] == "DENSITY-INTERACTION-1"
    assert "stays held and unrun" in _flat()


def test_the_reversal_conditions_are_named():
    flat = _flat()
    assert "What would reverse this decision" in flat
    assert "loses" in flat and "replication on fresh seeds" in flat
    assert "Absence of a behavioural gain is not a reversal" in flat


def _slots(scheme, rho):
    from benchmarks.density_worlds import is_intra_cell, world_edges
    cells = json.loads(RUN.read_text(encoding="utf-8"))["cells"]
    seeds = sorted({c["seed"] for c in cells})
    ix = {(c["scheme"], c["arm"], c["cap"], round(c["rho_world"], 6), c["seed"]): c
          for c in cells}
    intra = cross = 0.0
    for seed in seeds:
        world = world_edges(seed, rho)
        for row in ix[(scheme, "control", 20, rho, seed)]["selected"]:
            a, b = row.split(">")
            if (a, b) in world:
                continue
            if is_intra_cell(a, b):
                intra += 1
            else:
                cross += 1
    return intra / len(seeds), cross / len(seeds)


def _delta(scheme, rho):
    cells = json.loads(RUN.read_text(encoding="utf-8"))["cells"]
    seeds = sorted({c["seed"] for c in cells})
    ix = {(c["scheme"], c["arm"], c["cap"], round(c["rho_world"], 6), c["seed"]): c
          for c in cells}
    return sum(ix[(scheme, "intra_cell_excluded", 20, rho, s)]["precision"]
               - ix[(scheme, "control", 20, rho, s)]["precision"]
               for s in seeds) / len(seeds)


def test_the_mid_ladder_table_is_recomputed_from_the_run():
    flat = _flat()
    assert "Why the middle is non-monotone under the primary scheme" in flat
    for rho in (0.1, 0.2, 0.4, 0.6, 0.8):
        pi, pc = _slots("primary", rho)
        si, sc = _slots("sensitivity", rho)
        row = "| %.1f | %.2f / %.2f | %.2f / %.2f | %.4f / %.4f |" % (
            rho, pi, si, pc, sc, _delta("primary", rho),
            _delta("sensitivity", rho))
        assert row in flat, row


def test_the_padding_phase_claim_matches_the_generator():
    """The explanation is about where each stream ends, so check the generator, not prose."""
    from benchmarks.density_worlds import base_stream, stream
    # A calibration seed: the phase claim depends on rho and the base length, not on
    # the seed, and a block seed here would trip the freshness audit.
    seed = 992001
    for rho in (0.1, 0.2, 0.4, 0.6, 0.8):
        primary = stream(seed, rho, "primary", "constant")
        sensitivity = stream(seed, rho, "sensitivity", "constant")
        primary_tail = {len(t.split()) for t in primary[-8:]}
        sensitivity_tail = {len(t.split()) for t in sensitivity[-8:]}
        expected = {4} if rho == 0.8 else {2}
        assert primary_tail == expected, (rho, primary_tail)
        assert sensitivity_tail == {4}, (rho, sensitivity_tail)
        assert len(base_stream(seed, rho, "constant")) == 2 * len(
            __import__("benchmarks.density_worlds", fromlist=["world_edges"]).world_edges(seed, rho)
        ) + 24
    flat = _flat()
    assert "world-edge head" in flat and "filler tail" in flat
    assert "The non-monotonicity is an **exposure artifact of the primary scheme**" in flat
    assert "must not be quoted as evidence that the advantage shrinks with density" in flat
