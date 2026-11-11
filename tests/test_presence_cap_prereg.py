"""The cap-only preregistration must stay frozen, derived, unauthorised and reachable.

The bar and the ceiling are recomputed from the audit and ladder artifacts, the treatment is
checked for method overrides, and every verdict in the decision table is driven from a
synthetic run so no outcome is unreachable code.
"""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import copy
import inspect
import json
import statistics

import pytest

from benchmarks import presence_cap_experiment as C

BODY = C.prereg()
SEEDS = list(BODY["design"]["seeds"])
LEVELS = list(BODY["design"]["levels"])
AUDIT = json.loads(C.AUDIT.read_text(encoding="utf-8"))
WITNESS = AUDIT["rows"][0]


def _cell(seed, level, asserted, ever, max_window, world_digest, presence_digest):
    return {
        "seed": seed,
        "cap": level,
        "cap_effective": level,
        "engine_sha256": "sha",
        "engine_version": BODY["engine"]["version"],
        "world_edges": 112,
        "world_digest": world_digest,
        "present_world_edges": 112,
        "present_fingerprint": presence_digest,
        "s_ever_world_edges": ever,
        "s_ever_fingerprint": "ever-%d-%d" % (seed, ever),
        "asserted_world_edges": asserted,
        "max_window": max_window,
    }


def _run(asserted, ever, windows=None, witness=None, world_digest=None):
    """A synthetic run: `asserted[seed][cap]`, `ever[seed][cap]` (or one value per cap)."""
    cells = []
    for seed in SEEDS:
        for level in LEVELS:
            a = asserted[seed][level]
            e = (ever[level] if isinstance(ever, dict) and level in ever
                 else ever[seed][level])
            w = (windows or {}).get((seed, level), 40 if level == 40 else min(level, 240))
            cells.append(_cell(seed, level, a, e, w,
                               world_digest or "world-%d" % seed,
                               "presence-%d" % seed))
    return {
        "cells": cells,
        "engine": {"sha256": "sha", "version": BODY["engine"]["version"]},
        "witness": witness or {"seed": WITNESS["seed"], "cap": 40,
                               "present_world_edges": WITNESS["present_world_edges"],
                               "asserted_world_edges": WITNESS["asserted_world_edges"],
                               "asserted_fingerprint": WITNESS["asserted_fingerprint"]},
    }


def _flat(value=40):
    return {seed: {level: value for level in LEVELS} for seed in SEEDS}


def _steps(base=40, steps=(4, 4, 4)):
    out = {}
    for seed in SEEDS:
        row, value = {}, base
        row[40] = value
        for level, step in zip(LEVELS[1:], steps):
            value += step
            row[level] = value
        out[seed] = row
    return out


def test_the_record_is_frozen_authorised_and_run():
    assert BODY["prereg"] == "PRESENCE-CAP-1"
    assert BODY["status"] == "FROZEN, RUN"
    assert BODY["no_cells_run"] is False
    assert BODY["design"]["no_cells_run"] is False
    auth = BODY["authorisation"]
    assert auth["granted"] is True
    assert auth["granted_on"] == "2026-11-10"
    assert auth["quote"] == "Authorize all runs"
    assert auth["document"] == "docs/" + C.AUTHORISATION_DOC.name
    assert auth["scope"].startswith("all three frozen conversion blocks")
    assert C.authorisation_problems(BODY) == []
    assert C.ARTIFACT.exists(), "the authorised block ran and wrote its artifact"
    assert BODY["result"]["verdict"] == "CAP LIMITING"
    assert BODY["result"]["artifact"] == "docs/" + C.ARTIFACT.name
    assert C.check() == 0


def test_a_grant_needs_a_dated_document_and_a_quote():
    doc = C.AUTHORISATION_DOC
    assert doc.exists(), "Q2 had no request document before the grant"
    text = doc.read_text(encoding="utf-8")
    assert BODY["authorisation"]["quote"] in text
    assert "REQUESTED — NOT GRANTED" not in text
    bare = copy.deepcopy(BODY)
    bare["authorisation"] = {"required": True, "granted": True,
                             "request": BODY["authorisation"]["request"]}
    assert any("granted without" in problem for problem in C.validate(bare))


def test_the_treatment_overrides_no_pipeline_method():
    assert C.treatment_overrides() == ["__init__"]
    assert BODY["engine"]["overrides"] == ["__init__"]
    assert BODY["engine"]["changes"] == ["MAX_PREDICTIONS"]
    shipped = C.SleepService.MAX_PREDICTIONS
    service = C.CapOnlySleepService.__new__(C.CapOnlySleepService)
    service.MAX_PREDICTIONS = 112
    assert service.MAX_PREDICTIONS == 112 and shipped == 112


def test_the_levels_seeds_and_cells_are_the_declared_block():
    assert LEVELS == [40, 80, 112, 10 ** 9]
    assert len(SEEDS) == 6 and len(set(SEEDS)) == 6
    assert BODY["design"]["bootstrap"] not in SEEDS
    assert BODY["design"]["cells"] == len(SEEDS) * len(LEVELS) == 24
    assert BODY["design"]["cycles"] == 120
    assert BODY["design"]["witness_cell"]["seed"] == WITNESS["seed"] == 20261100


def test_the_seed_block_is_fresh_against_every_other_artifact():
    assert C.seed_collisions(SEEDS + [BODY["design"]["bootstrap"]],
                             allow=(C.PREREG, C.ARTIFACT)) == {}
    # The freshness check can fail: the audit seed is already consumed.
    assert 20261100 in C.seed_collisions([20261100], allow=(C.PREREG,))


def test_the_bar_is_derived_from_the_audit_and_not_typed():
    counts = C.audit_counts()
    assert counts == [40, 44, 38, 46, 34, 47]
    assert round(2 * statistics.stdev(counts)) == C.derived_bar() == BODY["bar"]["value"] == 10
    assert "stdev" in BODY["bar"]["derivation"]


def test_the_ceiling_is_derived_from_the_ladder():
    ladder = json.loads(C.LADDER.read_text(encoding="utf-8"))
    never = [row["buckets"]["offered_not_admitted"] for row in ladder["rows"]]
    assert never == [25, 33, 23, 26, 36, 28]
    assert statistics.mean(never) == C.derived_ceiling() == BODY["ceiling"]["value"] == 28.5


def test_the_gate_cannot_make_a_reading_unreachable():
    notes = " ".join(BODY["freeze_notes"]["corrections_before_any_cell"])
    assert "unreachable" in notes and "K4" in notes
    assert "at least one seed" in BODY["gates"]["K4_cap_live"]
    # With no reach change anywhere the cap is not live, so no reading is made.
    assert C.verdict(BODY, _run(_flat(), {level: 70 for level in LEVELS}))[0] == "CAP NOT BINDING"


def test_the_retention_profile_names_the_largest_drop():
    cell = {"world_edges": 112, "present_world_edges": 112, "s_ever_world_edges": 80,
            "asserted_world_edges": 40, "asserted_without_admission": 4}
    profile = C.retention_profile(cell)
    assert profile["steps"]["P/W"]["ratio"] == 1.0
    assert profile["steps"]["S_ever/P"]["ratio"] == 0.714286
    assert profile["steps"]["A_W/S_ever"]["ratio"] == 0.5
    assert profile["ratios"]["A_W|admitted/S_ever"] == 0.45
    assert profile["retained"] == {"W": 112, "P": 112, "S_ever": 80, "A_pred": 36}
    assert profile["absolute_drop"] == {"P->S_ever": 28, "S_ever->A_W": 44}
    assert sum(profile["absolute_drop"].values()) == 112 - 40
    assert profile["bypass"] == 4
    assert profile["primary_suspect"] == "S_ever->A_W"


def test_a_ratio_with_no_denominator_is_not_measurable_not_zero():
    profile = C.retention_profile({"world_edges": 0, "present_world_edges": 0,
                                   "s_ever_world_edges": 0, "asserted_world_edges": 0})
    assert profile["not_measurable"] == ["P/W", "S_ever/P", "A_W/S_ever",
                                         "A_W|admitted/S_ever"]
    for step in profile["steps"].values():
        assert step["ratio"] == "not measurable"
    assert profile["primary_suspect"] is None


def test_the_bypass_is_reported_and_never_counted_as_retention():
    cell = {"world_edges": 112, "present_world_edges": 112, "s_ever_world_edges": 60,
            "asserted_world_edges": 40, "asserted_without_admission": 10}
    profile = C.retention_profile(cell)
    assert profile["ratios"]["A_W/S_ever"] == 0.666667
    assert profile["ratios"]["A_W|admitted/S_ever"] == 0.5
    assert profile["retained"]["A_pred"] == 30
    assert profile["absolute_drop"]["S_ever->A_W"] == 30
    assert profile["absolute_drop"]["P->S_ever"] == 42
    assert sum(profile["absolute_drop"].values()) == 112 - 40
    assert profile["bypass"] == 10


def test_the_largest_relative_loss_does_not_name_the_suspect_alone():
    # The last step loses more of a smaller denominator; the absolute rule must still decide.
    cell = {"world_edges": 100, "present_world_edges": 100, "s_ever_world_edges": 90,
            "asserted_world_edges": 45, "asserted_without_admission": 0}
    profile = C.retention_profile(cell)
    assert profile["loss_share"]["S_ever->A_W"] > profile["loss_share"]["P->S_ever"]
    assert profile["absolute_drop"] == {"P->S_ever": 10, "S_ever->A_W": 45}
    assert profile["primary_suspect"] == "S_ever->A_W"


def test_the_declared_retention_steps_are_the_fields_the_run_records():
    source = inspect.getsource(C.run_cell)
    for step in BODY["retention_profile"]["steps"]:
        assert step["cell_fields"], step
        for field in step["cell_fields"]:
            assert field in source, field


def test_the_prior_profile_is_the_ladder_record_and_reconciles_its_buckets():
    prior = C.ladder_prior()
    ladder = json.loads(C.LADDER.read_text(encoding="utf-8"))
    pooled = ladder["summary"]["pooled_buckets"]
    assert prior["ratios"]["P/W"] == 1.0
    assert prior["consistent"]
    # The retained chain ends at A_pred, so the last drop is the admitted-not-asserted count and
    # the bypass never inflates it.
    assert prior["absolute_drop"]["S_ever->A_W"] == pooled["admitted_not_asserted"]
    assert prior["absolute_drop"]["P->S_ever"] == pooled["offered_not_admitted"] == 171
    assert prior["stage_difference"]["P->S_ever"] == 212
    assert prior["stage_difference"]["P->S_ever"] == \
        prior["absolute_drop"]["P->S_ever"] + prior["edges"]["bypass"]
    assert sum(prior["absolute_drop"].values()) == prior["misses_total"] == 423
    assert prior["retained"]["A_pred"] + prior["edges"]["bypass"] == \
        prior["edges"]["A_W"]
    assert prior["edges"]["admitted_asserted"] == \
        prior["retained"]["S_ever"] - pooled["admitted_not_asserted"]
    assert prior["primary_suspect"] == "S_ever->A_W"
    assert prior["normalized"] if "normalized" in prior else True


def test_the_two_loss_rules_agree_on_the_committed_ladder():
    prior = C.ladder_prior()
    drops = prior["absolute_drop"]
    assert drops["S_ever->A_W"] > drops["P->S_ever"], drops
    assert prior["loss_share"]["S_ever->A_W"] > prior["loss_share"]["P->S_ever"]
    assert prior["bucket_share"]["admitted_not_asserted"] > \
        prior["bucket_share"]["offered_not_admitted"]


def test_the_page_reports_the_prior_suspect_and_the_bypass():
    page = (C.ROOT / "docs" / "PRESENCE-CAP-PREREGISTRATION.md").read_text(encoding="utf-8")
    assert "primary suspect stage is **S_ever->A_W**" in page
    assert "excluded from the retained chain" in page
    assert "no edge is counted twice" in page


def test_the_live_audit_is_current():
    assert C.audit_problems() == []


def test_a_stale_audit_page_fails_the_cap_check(tmp_path):
    page = tmp_path / "audit.md"
    page.write_text(C.AUDIT_PAGE.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    problems = C.audit_problems(page=page)
    assert any("audit page is stale" in problem for problem in problems), problems


def test_an_audit_built_by_another_engine_fails_the_cap_check(tmp_path):
    art = json.loads(C.AUDIT.read_text(encoding="utf-8"))
    art["same_build"]["sha256"] = "0" * 64
    forged = tmp_path / "audit.json"
    forged.write_text(json.dumps(art), encoding="utf-8")
    problems = C.audit_problems(artifact=forged)
    assert any("different engine" in problem for problem in problems), problems


def test_check_prereg_refuses_when_the_audit_is_stale(monkeypatch):
    monkeypatch.setattr(C, "audit_problems", lambda *args, **kwargs: ["the audit page is stale"])
    with pytest.raises(SystemExit) as caught:
        C.check_prereg()
    assert "the audit page is stale" in str(caught.value)


def test_the_page_is_the_record():
    assert C.DOC.read_text(encoding="utf-8") == C.render_prereg(BODY)


def test_check_prereg_is_clean():
    assert C.check_prereg() == 0


def test_a_moved_bar_is_caught():
    forged = copy.deepcopy(BODY)
    forged["bar"]["value"] = 9
    assert any("bar" in problem for problem in C.validate(forged))


def test_a_reused_seed_is_caught():
    forged = copy.deepcopy(BODY)
    forged["design"]["seeds"][0] = 20261100
    assert any("fresh" in problem for problem in C.validate(forged))


def test_an_engine_edit_is_refused():
    forged = copy.deepcopy(BODY)
    forged["engine"]["edit"] = "the cap was changed in organica/sleep.py"
    assert any("engine" in problem for problem in C.validate(forged))


def test_nothing_runs_and_nothing_is_written_without_authorisation(monkeypatch, tmp_path):
    """The refusal path is driven by a forged ungranted record, never by the real one.

    The shipped record is authorised, so calling `measure` against it would run 24 cells.
    """
    forged = copy.deepcopy(BODY)
    forged["status"] = "FROZEN, NOT RUN"
    forged["no_cells_run"] = True
    forged["design"]["no_cells_run"] = True
    forged.pop("result", None)
    forged["authorisation"] = {"required": True, "granted": False,
                               "request": BODY["authorisation"]["request"],
                               "note": "an ungranted record is refused"}
    monkeypatch.setattr(C, "prereg", lambda: forged)
    monkeypatch.setattr(C, "ARTIFACT", tmp_path / "run.json")
    monkeypatch.setattr(C, "RESULT", tmp_path / "RESULT.md")
    with pytest.raises(SystemExit, match="not authorised"):
        C.measure()
    with pytest.raises(SystemExit, match="not authorised"):
        C.finish()
    assert not (tmp_path / "run.json").exists()
    assert not (tmp_path / "RESULT.md").exists()


def test_a_cap_that_never_fills_is_not_binding():
    run = _run(_flat(), {level: 100 for level in LEVELS},
               windows={(seed, 40): 39 for seed in SEEDS})
    label, details = C.verdict(BODY, run)
    assert label == "CAP NOT BINDING"
    assert details["gate"] == "K4_cap_live"


def test_admission_scaling_without_assertion_is_its_own_verdict():
    run = _run(_flat(), {40: 70, 80: 95, 112: 108, 10 ** 9: 112})
    assert C.verdict(BODY, run)[0] == "ADMISSION-ONLY BOTTLENECK"
    # Flat assertion with reach changing on only half the seeds is not a cap verdict: the cap is
    # live somewhere but does not move the endpoint, and K4 still passes on three seeds.
    ever = {seed: {level: (70 + list(LEVELS).index(level) * 5 if index < 3 else 70)
                   for level in LEVELS} for index, seed in enumerate(SEEDS)}
    assert C.verdict(BODY, _run(_flat(), ever))[0] == "CAP NOT LIMITING"


def test_scaling_above_the_bar_is_cap_limiting():
    label, details = C.verdict(BODY, _run(_steps(steps=(6, 6, 6)),
                                          {40: 70, 80: 95, 112: 108, 10 ** 9: 112}))
    assert label == "CAP LIMITING"
    assert details["mean_gain"] == 12 and details["lower_bound"] > 0
    assert details["positive_seeds"] == 6


def test_scaling_below_the_bar_is_reported_as_such():
    label, details = C.verdict(BODY, _run(_steps(steps=(1, 2, 3)),
                                          {40: 70, 80: 95, 112: 108, 10 ** 9: 112}))
    assert label == "CAP LIMITING BELOW BAR"
    assert details["mean_gain"] == 3 < BODY["bar"]["value"]


def test_neither_scaling_nor_flat_is_mixed():
    asserted = {}
    for index, seed in enumerate(SEEDS):
        row = {40: 40}
        step = 6 if index % 2 == 0 else -6
        for level in LEVELS[1:]:
            row[level] = row[list(LEVELS)[list(LEVELS).index(level) - 1]] + step
        asserted[seed] = row
    label, details = C.verdict(BODY, _run(asserted, {40: 70, 80: 80, 112: 90, 10 ** 9: 100}))
    assert label == "MIXED"
    assert details["scaling_seeds"] == 3


def test_a_world_that_moves_across_caps_is_void():
    run = _run(_flat(), {level: 70 for level in LEVELS})
    for cell in run["cells"]:
        if cell["cap"] == 40:
            cell["world_digest"] = "different"
    label, details = C.verdict(BODY, run)
    assert label == "VOID" and details["gate"] == "K2_same_world"


def test_a_shipped_cap_that_does_not_reproduce_the_audit_is_void():
    witness = {"seed": WITNESS["seed"], "cap": 40,
               "present_world_edges": 112, "asserted_world_edges": 41,
               "asserted_fingerprint": WITNESS["asserted_fingerprint"]}
    label, details = C.verdict(BODY, _run(_flat(), {40: 70, 80: 95, 112: 108, 10 ** 9: 112},
                                          witness=witness))
    assert label == "VOID" and details["gate"] == "K5_cap_only"


def test_an_empty_denominator_is_void():
    run = _run(_flat(), {40: 70, 80: 95, 112: 108, 10 ** 9: 112})
    run["cells"][0]["s_ever_world_edges"] = 0
    label, details = C.verdict(BODY, run)
    assert label == "VOID" and details["gate"] == "K6_denominator"


def test_the_result_page_renders_from_a_scored_run():
    body = _run(_steps(steps=(6, 6, 6)), {40: 70, 80: 95, 112: 108, 10 ** 9: 112})
    label, details = C.verdict(BODY, body)
    artifact = dict(body, verdict=label, details=details,
                    engine={"version": BODY["engine"]["version"]},
                    gains=[{"seed": seed, "40": 40, "80": 46, "112": 52, str(10 ** 9): 58,
                            "gain_112": 12} for seed in SEEDS])
    page = C.render_result(artifact)
    assert label in page and "bar" in page
    assert "{" not in page, "a placeholder survived into the result page"

def test_the_witness_cell_fingerprints_the_set_the_audit_published():
    """The audit's asserted_fingerprint covers the whole asserted structure, not A_W."""
    source = inspect.getsource(C.run_cell)
    assert '"asserted_fingerprint": witness_rows.fingerprint(asserted_pairs)' in source
    assert '"asserted_fingerprint": witness_rows.fingerprint(world_asserted)' not in source


def test_the_prior_miss_count_is_the_artifact_s_not_misses_plus_bypass():
    ladder = json.loads(C.LADDER.read_text(encoding="utf-8"))
    page = C.render_prereg(BODY)
    total = ladder["summary"]["misses_total"]
    bypass = sum(row["asserted_without_admission"] for row in ladder["rows"])
    assert "over its %d misses" % total in page
    assert "over its %d misses" % (total + bypass) not in page
    assert "| presence-to-assertion ladder trace (exploratory) |" in page
