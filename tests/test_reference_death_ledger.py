"""Controls for the reference-arm death ledger.

Each control targets a rule that could silently pass: the death-cycle convention, the
decision table's two sides, the precedence of the attribution vocabulary, and the guard's
pre-run/post-run states.
"""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import copy

from benchmarks import reference_death_ledger as r


def _rows(series):
    return [
        {
            "theories": count,
            "retained_beliefs": 0,
            "theory_removals": {reason: 0 for reason in r.THEORY_REASONS},
            "belief_removals": {reason: 0 for reason in r.BELIEF_REASONS},
        }
        for count in series
    ]


def test_death_cycle_is_one_past_the_last_theory():
    facts = r.cell_facts(_rows([0, 1, 2, 0, 0]))
    assert facts["last_nonzero_cycle"] == 3
    assert facts["death_cycle"] == 4
    assert facts["theory_cycles"] == 2


def test_an_arm_that_never_forms_a_theory_dies_at_cycle_one():
    facts = r.cell_facts(_rows([0, 0, 0]))
    assert facts["last_nonzero_cycle"] == 0
    assert facts["death_cycle"] == 1


def test_a_returning_theory_does_not_reset_the_death_cycle_to_its_return():
    facts = r.cell_facts(_rows([1, 0, 1, 0, 0]))
    assert facts["death_cycle"] == 4


def test_a_failed_gate_is_unmeasurable_before_the_table_is_read():
    deaths = {"FULL": 39, **{arm: 39 for arm in r.ARMS if arm != "FULL"}}
    gates = {name: True for name in ("G1", "G2", "G3", "G4", "G5")}
    assert r.decide(gates, deaths) == "SHARED_DOMINANT"
    gates["G3"] = False
    assert r.decide(gates, deaths) == "UNMEASURABLE"


def _deaths(reference, others):
    return {"FULL": reference, **dict(zip([a for a in r.ARMS if a != "FULL"], others))}


def test_shared_death_when_every_arm_dies_within_the_margin():
    deaths = _deaths(39, [39, 40, 41, 38, 44])
    assert r.decide({name: True for name in "12345"}, deaths) == "SHARED_DOMINANT"


def test_reference_dominant_when_every_ablation_outlives_it_by_the_margin():
    deaths = _deaths(39, [55, 60, 58, 55, 70])
    assert r.decide({name: True for name in "12345"}, deaths) == "REFERENCE_DOMINANT"


def test_ablation_dominant_when_any_ablation_dies_first_by_the_margin():
    deaths = _deaths(39, [25, 60, 58, 55, 70])
    assert r.decide({name: True for name in "12345"}, deaths) == "ABLATION_DOMINANT"


def test_a_difference_within_the_margin_is_not_a_lead():
    # One ablation is 9 cycles early, inside the margin; the latest is 31 late.
    deaths = _deaths(39, [30, 60, 58, 55, 70])
    assert r.decide({name: True for name in "12345"}, deaths) == "REFERENCE_DOMINANT"


def test_superseded_takes_precedence_over_a_lost_parent():
    reason = r.theory_removal_reason(
        "hub", ["missing"], set(), {}, at_cap=False, subject_has_theory=True
    )
    assert reason == "superseded"


def test_parent_loss_precedes_cap_and_collapse():
    reason = r.theory_removal_reason(
        "hub", ["gone"], {"other"}, {"hub": 1}, at_cap=True, subject_has_theory=False
    )
    assert reason == "parent_loss"


def test_competing_collapse_is_named_when_parents_survive_but_too_few_do():
    reason = r.theory_removal_reason(
        "hub", ["a"], {"a"}, {"hub": 1}, at_cap=True, subject_has_theory=False
    )
    assert reason == "competing_collapse"


def test_cap_is_named_only_when_the_layer_is_full_and_support_survives():
    reason = r.theory_removal_reason(
        "hub", ["a"], {"a"}, {"hub": 3}, at_cap=True, subject_has_theory=False
    )
    assert reason == "capped"


def test_a_removal_with_no_mechanism_is_unexplained_rather_than_absorbed():
    reason = r.theory_removal_reason(
        "hub", ["a"], {"a"}, {"hub": 3}, at_cap=False, subject_has_theory=False
    )
    assert reason == "unexplained"


def test_belief_removal_distinguishes_cap_from_absence():
    assert r.belief_removal_reason(True) == "capped"
    assert r.belief_removal_reason(False) == "not_reformed"


def test_modal_mechanism_ties_break_alphabetically():
    assert r.modal_mechanism({"capped": 2, "parent_loss": 2}) == "capped"
    assert r.modal_mechanism({"capped": 0}) is None


# ==================================================================
# The guard's two states
# ==================================================================

def _text(executions=0, outcome="**Not yet written.**", body=None):
    body = body or "## 1. One\n\nfrozen body\n\n## 2. Two\n\nmore\n\n"
    return (
        "# Protocol\n\n<!-- reference-death-ledger\nexecutions: %d\n-->\n\n%s"
        "## 9. Outcome\n\n%s\n" % (executions, body, outcome)
    )


def _artifact(digest, label="SHARED_DOMINANT"):
    return {
        "protocol_digest": digest,
        "label": label,
        "seeds": list(r.SEEDS),
    }


def test_a_frozen_unexecuted_protocol_is_accepted():
    text = _text()
    digest = r.protocol_digest(text)
    assert r.validate(text, None, digest=digest) == []


def test_an_artifact_under_an_unexecuted_protocol_is_rejected():
    text = _text()
    digest = r.protocol_digest(text)
    problems = r.validate(text, _artifact(digest), digest=digest)
    assert any("executions" in problem for problem in problems)


def test_a_written_outcome_without_an_artifact_is_rejected():
    text = _text(outcome="**Measured: `SHARED_DOMINANT`.**")
    digest = r.protocol_digest(text)
    problems = r.validate(text, None, digest=digest)
    assert any("section 9" in problem for problem in problems)


def test_a_frozen_executed_protocol_with_matching_artifact_is_accepted():
    text = _text(executions=1, outcome="**Measured: `SHARED_DOMINANT`.**")
    digest = r.protocol_digest(text)
    assert r.validate(text, _artifact(digest), digest=digest) == []


def test_a_moved_frozen_digest_is_rejected():
    text = _text()
    problems = r.validate(text, None, digest="0" * 64)
    assert any("digest" in problem for problem in problems)


def test_a_label_the_outcome_does_not_name_is_rejected():
    text = _text(executions=1, outcome="**Measured: `SHARED_DOMINANT`.**")
    digest = r.protocol_digest(text)
    problems = r.validate(text, _artifact(digest, label="REFERENCE_DOMINANT"), digest=digest)
    assert any("label" in problem for problem in problems)


def test_a_different_seed_block_is_rejected():
    text = _text(executions=1, outcome="**Measured: `SHARED_DOMINANT`.**")
    digest = r.protocol_digest(text)
    artifact = _artifact(digest)
    artifact["seeds"] = [1, 2, 3]
    problems = r.validate(text, artifact, digest=digest)
    assert any("seeds" in problem for problem in problems)


# ==================================================================
# The page is a function of the artifact
# ==================================================================

def _page_artifact():
    summary = {}
    for arm in r.ARMS:
        summary[arm] = {
            "cells": 3,
            "death_cycles": [39, 39, 39],
            "median_death_cycle": 39,
            "min_death_cycle": 39,
            "max_death_cycle": 39,
            "theory_cycles": 37,
            "theory_removals": {reason: (1 if reason == "parent_loss" else 0)
                                for reason in r.THEORY_REASONS},
            "belief_removals": {reason: (3 if reason == "not_reformed" else 0)
                                for reason in r.BELIEF_REASONS},
            "unexplained": 0,
            "theories_total": 13,
        }
    return {
        "date": "2026-11-07",
        "engine_version": "0.13.0",
        "seeds": list(r.SEEDS),
        "cycles": 300,
        "arms": list(r.ARMS),
        "summary": summary,
        "label": "SHARED_DOMINANT",
        "q042": {"outcome": "SUPPORTED", "answer": "Yes, but shared."},
        "gates": {name: True for name in
                  ("G1_neutral_observer", "G2_attribution_complete", "G3_axis_live",
                   "G4_denominators", "G5_seed_independence")},
        "predictions": {name: True for name in
                        ("P1_every_arm_dies_before_end", "P2_every_ablation_within_margin",
                         "P3_reference_modal_parent_loss", "P4_no_unexplained_in_reference")},
        "control": {"seed": r.CONTROL_SEED, "theory_match": True, "belief_match": True},
        "secondary": {
            "reference_theory_removals": 9,
            "total_theory_removals": 54,
            "reference_share_of_theory_removals": 0.1667,
            "modal_mechanism": {arm: "parent_loss" for arm in r.ARMS},
            "reference_belief_removals": {"capped": 0, "not_reformed": 12},
            "unexplained_share": 0.0,
        },
        "protocol_digest": "d",
    }


def test_the_page_names_the_label_and_leaves_no_placeholder():
    page = r.render(copy.deepcopy(_page_artifact()))
    assert "`SHARED_DOMINANT`" in page
    assert "{" not in page
    assert "parent_loss" in page


def test_the_page_reports_a_failed_gate_rather_than_hiding_it():
    artifact = _page_artifact()
    artifact["gates"]["G3_axis_live"] = False
    artifact["label"] = "UNMEASURABLE"
    page = r.render(artifact)
    assert "FAIL" in page
    assert "`UNMEASURABLE`" in page
