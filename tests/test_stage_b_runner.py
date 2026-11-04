"""The Stage B runner's guards and controls, tested without running a world.

The runner's most important property is a refusal: a pre-assigned seed is not an
allocated one, and the four spares are never drawn. Those are tested by calling the
guard, not by reading the prose. The analysis is tested both ways -- a planted
relation must be detected and a flat outcome must not be -- because a statistic that
cannot fail is decoration (AGENTS rule 25c).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks import stage_b_runner as runner


def test_an_unallocated_confirmatory_seed_is_refused():
    empty = {"allocated": False, "seeds": [], "why": "control"}
    with pytest.raises(RuntimeError, match="pre-assigned but NOT allocated"):
        runner.assert_runnable(700000001, record=empty)


def test_a_reserved_spare_is_refused_even_when_an_allocation_exists(tmp_path, monkeypatch):
    record = tmp_path / "allocation.json"
    record.write_text(json.dumps({"allocated": True, "seeds": [700000721]}), encoding="utf-8")
    monkeypatch.setattr(runner, "ALLOCATION", record)
    with pytest.raises(RuntimeError, match="never drawn"):
        runner.assert_runnable(700000721)


def test_an_allocated_seed_is_accepted_once_it_is_recorded(tmp_path, monkeypatch):
    record = tmp_path / "allocation.json"
    record.write_text(json.dumps({"allocated": True, "seeds": [700000001]}), encoding="utf-8")
    monkeypatch.setattr(runner, "ALLOCATION", record)
    runner.assert_runnable(700000001)


def test_a_seed_outside_the_block_is_refused():
    with pytest.raises(RuntimeError, match="not in the Stage B block"):
        runner.assert_runnable(700000725)


def test_the_consumed_design_block_remains_runnable_for_smoke_runs():
    for seed in runner.DESIGN_SEEDS:
        runner.assert_runnable(seed)


def test_the_eligibility_rule_is_the_recorded_one():
    """onset + 101 <= horizon, and no onset is never eligible."""
    assert runner.FOLLOW_UP == 101
    assert runner.eligible(539, 640) is True
    assert runner.eligible(540, 640) is False
    assert runner.eligible(602, 640) is False
    assert runner.eligible(None, 640) is False


def test_the_seed_block_matches_the_protocol():
    assert runner.seed_block("2:1")[0] == 700000001
    assert runner.seed_block("6:1")[-1] == 700000720
    assert sum(len(runner.seed_block(c)) for c in runner.CLAIMED) == 720
    assert all(len(runner.seed_block(c)) == runner.PER_CONFIG for c in runner.CLAIMED)
    assert runner.config_of(700000001) == "2:1"
    assert runner.config_of(700000180) == "2:1"
    assert runner.config_of(700000181) == "3:1"
    assert runner.config_of(700000541) == "6:1"


def test_the_horizon_is_confirmation_plus_the_follow_up():
    for config in runner.CLAIMED:
        assert runner.horizon_cycles(config) == \
            runner.CONFIRMATION_CYCLE[config] + 101


def test_a_readout_that_knows_the_withheld_pair_scores_better():
    withheld = {("alpha", "beta")}
    events = ["alpha", "beta", "alpha", "beta"]
    knows = runner.make_organica_backoff({"alpha": {"beta": 10.0}}, {"beta": 0.5},
                                         runner.ALPHA)
    blind = runner.make_organica_backoff({}, {"beta": 0.5}, runner.ALPHA)
    good = runner.score_withheld(knows, events, withheld)
    bad = runner.score_withheld(blind, events, withheld)
    assert good["measurable"] and bad["measurable"]
    assert good["log_loss"] < bad["log_loss"]
    assert good["occurrences"] == 2 and bad["occurrences"] == 2


def test_an_empty_window_is_not_measurable_rather_than_zero():
    result = runner.score_withheld(lambda a, b: 0.5, ["alpha", "gamma"], {("alpha", "beta")})
    assert result["log_loss"] is None
    assert result["measurable"] is False
    assert result["cells"] == 0


def _planted(config: str = "2:1", slope: float = -0.001,
             n: int = runner.PER_CONFIG) -> list[dict]:
    return [{"configuration": config, "seed": 1000 + i, "complete": True,
             "eligible": True, "censored": False, "onset": 100 + i,
             "asserted_pairs_at_onset": 10 + i,
             "outcome": 0.16 + slope * i, "outcome_cells": 4,
             "outcome_occurrences": 2, "outcome_measurable": True}
            for i in range(n)]


def test_the_analysis_detects_a_planted_relation():
    found = runner.analyse(_planted(), reps=200)["by_configuration"]["2:1"]
    assert found["spearman"] < 0
    assert found["predicted_sign_held"] is True
    assert found["interval"][1] < 0


def test_the_permutation_control_finds_nothing_in_the_same_data():
    found = runner.analyse(_planted(), reps=200)["by_configuration"]["2:1"]
    assert found["permutation_interval"][0] <= 0 <= found["permutation_interval"][1]


def test_the_analysis_does_not_detect_a_flat_outcome():
    flat = [dict(cell, outcome=0.5) for cell in _planted()]
    found = runner.analyse(flat, reps=100)["by_configuration"]["2:1"]
    assert found["predicted_sign_held"] is False


def test_the_conjunction_is_not_a_best_configuration_finding():
    cells = []
    for config in runner.CLAIMED:
        cells += _planted(config)
    assert runner.analyse(cells, reps=100)["verdict"] == "SUPPORTED"
    short = [c for c in cells if c["configuration"] != "6:1"]
    short += [dict(c, configuration="6:1", outcome=0.5) for c in _planted("6:1")]
    result = runner.analyse(short, reps=100)
    assert result["verdict"] == "MIXED"
    assert "never a best-configuration finding" in result["aggregation_rule"]


def test_no_world_is_reported_when_no_world_ran():
    assert runner.analyse([])["verdict"] == "NO WORLD RAN"


def test_the_self_test_passes_and_its_controls_can_fail():
    result = runner.self_test()
    assert result["passed"] is True, [k for k, v in result["checks"].items() if not v]
    # the controls are not vacuous: each is a real boolean the code computes
    assert isinstance(result["checks"], dict) and len(result["checks"]) >= 8


def test_an_ineligible_cell_is_reported_rather_than_truncated(tmp_path):
    """The rule's other half: a world whose follow-up does not fit is excluded."""
    cell = {"configuration": "2:1", "seed": 700000001, "complete": True,
            "eligible": False, "ineligible_because": "onset + 101 exceeds the horizon",
            "onset": 602, "outcome": None}
    stats = runner.analyse([cell])["by_configuration"]["2:1"]
    assert stats["worlds"] == 1
    assert stats["eligible_scored"] == 0
    assert stats["ineligible"] == 1
    assert stats["spearman"] is None


def test_a_cell_specification_is_parsed_from_the_right():
    """`6:1:20261023` must not be split on its first colon."""
    assert runner.parse_cell("6:1:20261023") == ("6:1", 20261023)
    assert runner.parse_cell("2:1:700000001") == ("2:1", 700000001)
    with pytest.raises(ValueError, match="unknown configuration"):
        runner.parse_cell("9:1:20261023")


def test_the_smoke_artifact_shows_the_outcome_was_scored():
    """The smoke run is labelled as one, and its onset is the harness's own onset."""
    import json as _json

    doc = _json.loads((runner.ROOT / "docs" / "stage_b_runner_smoke.json").read_text(encoding="utf-8"))
    assert doc["not_a_measurement"] is True
    cell = doc["cell"]
    assert (cell["configuration"], cell["design_block_cell"]) == ("6:1", 20261023)
    assert cell["eligible"] is True and cell["outcome_measurable"] is True
    assert cell["outcome_cells"] > 0 and cell["outcome"] is not None
    assert cell["outcome_occurrences"] > 0
    onsets = _json.loads((runner.ROOT / "docs" / "stage_b_onset_withholding.json").read_text(
        encoding="utf-8"))["cells"]
    same = [c for c in onsets if c["configuration"] == cell["configuration"]
            and c["design_block_cell"] == cell["design_block_cell"]]
    assert len(same) == 1
    assert cell["onset"] == same[0]["onset"], (cell["onset"], same[0]["onset"])


def test_a_cached_cell_is_reloaded_rather_than_rerun(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "CACHE", tmp_path)
    cell = {"configuration": "2:1", "seed": 20261023, "complete": True, "pid": 1}
    path = runner.save_cell(cell)
    assert path == runner.cell_path("2:1", 20261023)
    assert runner.load_cell("2:1", 20261023) == cell
    assert runner.load_cell("2:1", 20261024) is None
    assert runner.cell_is_done(cell)
    assert not runner.cell_is_done(None)
    paused = dict(cell, complete=False, stopped_at_budget=True)
    assert not runner.cell_is_done(paused), (
        "a paused cell cached on disk must count as pending, or --all would skip "
        "the work it stopped halfway through")


def test_the_seed_block_is_dispersed_across_configurations():
    seen = {config: runner.seed_block(config) for config in runner.CLAIMED}
    for config, seeds in seen.items():
        assert len(seeds) == runner.PER_CONFIG, config
        assert seeds == list(range(min(seeds), max(seeds) + 1)), config
    flat = [seed for seeds in seen.values() for seed in seeds]
    assert len(flat) == len(set(flat)) == runner.PER_CONFIG * len(runner.CLAIMED)


def test_the_batch_refuses_before_dispatching_when_a_seed_is_unallocated(monkeypatch):
    constructed = []

    def spy(*args, **kwargs):
        constructed.append(1)
        raise AssertionError("no worker pool may be built before the guard passes")

    monkeypatch.setattr(runner, "ProcessPoolExecutor", spy)
    monkeypatch.setattr(runner, "run_cell", spy)
    empty = {"allocated": False, "seeds": [], "why": "control"}
    monkeypatch.setattr(runner, "allocation", lambda: empty)
    with pytest.raises(RuntimeError, match="pre-assigned but NOT allocated"):
        runner.run_many([("2:1", 20261023), ("2:1", 700000001)], workers=4)
    assert constructed == [], "the guard must refuse the batch before any work starts"


def test_a_spare_in_the_batch_is_refused_even_after_allocated_seeds(monkeypatch):
    monkeypatch.setattr(runner, "run_cell", lambda *a, **k: {})
    with pytest.raises(RuntimeError, match="never drawn"):
        runner.run_many([("2:1", 20261023), ("2:1", 700000722)], workers=2)


def test_assemble_writes_where_asked_and_labels_a_design_block_assembly(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    cache.mkdir()
    monkeypatch.setattr(runner, "CACHE", cache)
    cell = {"configuration": "6:1", "seed": runner.DESIGN_SEEDS[0], "complete": True,
            "eligible": True, "censored": False, "onset": 200, "outcome": 0.2,
            "asserted_pairs_at_onset": 5, "outcome_cells": 1, "outcome_occurrences": 1,
            "outcome_measurable": True}
    runner.save_cell(cell)
    out = tmp_path / "art.json"
    assert runner.main(["--assemble", "--out", str(out)]) == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert len(doc["cells"]) == 1
    assert "design-block" in doc["what_this_is"], (
        "an assembly of consumed design seeds must say so, or it reads as a run")
    assert not runner.OUT.exists() or runner.OUT.read_text(encoding="utf-8") != out.read_text(
        encoding="utf-8")


def test_an_empty_assembly_reports_that_no_world_ran(tmp_path, monkeypatch):
    cache = tmp_path / "empty"
    cache.mkdir()
    monkeypatch.setattr(runner, "CACHE", cache)
    out = tmp_path / "art.json"
    assert runner.main(["--assemble", "--out", str(out)]) == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["cells"] == []
    assert doc["analysis"]["verdict"] == "NO WORLD RAN"


def test_a_partial_assembly_carries_no_verdict():
    planted = [{"configuration": "6:1", "seed": 1000 + i, "complete": True,
                "eligible": True, "censored": False, "onset": 100 + i,
                "asserted_pairs_at_onset": 10, "outcome": 0.5,
                "outcome_cells": 1, "outcome_occurrences": 1, "outcome_measurable": True}
               for i in range(10)]
    partial = runner.analyse(planted, reps=50)["verdict"]
    assert partial == "NO VERDICT: PARTIAL ASSEMBLY", (
        "an assembly with one configuration missing must not report a claim verdict; "
        "both SUPPORTED and NOT SUPPORTED would be read as results about the claim")


def test_the_projection_covers_the_block_and_scales_with_workers():
    cells = [{"configuration": "6:1", "seed": 20261023, "complete": True,
              "engine_seconds": 429.0, "cycles_run": 379}]
    est = runner.cost_estimate(cells, cpu_count=8, efficiency=1.0)
    assert est["worlds"] == runner.PER_CONFIG * len(runner.CLAIMED) == 720
    expected_cycles = sum(runner.PER_CONFIG * (runner.horizon_cycles(c) - 1)
                          for c in runner.CLAIMED)
    assert est["cycles_total"] == expected_cycles
    seconds_per_cycle = 429.0 / (379 + runner.TEST_CYCLES)
    assert est["measured_seconds_per_cycle"]["mean"] == round(seconds_per_cycle, 6)
    assert est["serial_hours"] == round(expected_cycles * seconds_per_cycle / 3600.0, 2)
    wall = est["wall_hours_by_workers"]
    assert wall["1"] == est["serial_hours"]
    assert wall["8"] < wall["2"] < wall["1"]
    assert est["planning_only"] is True and est["no_seed_allocated"] is True
    assert len(est["assumptions"]) == 3


def test_the_projection_refuses_to_invent_a_rate():
    est = runner.cost_estimate([], cpu_count=8)
    assert est["estimated"] is False and est["worlds"] == 0
    assert "no cell has run" in est["why"]


def test_the_projection_is_written_where_the_mode_says(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    cache.mkdir()
    monkeypatch.setattr(runner, "CACHE", cache)
    monkeypatch.setattr(runner, "ESTIMATE_OUT", tmp_path / "estimate.json")
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    runner.save_cell({"configuration": "6:1", "seed": 20261023, "complete": True,
                      "engine_seconds": 100.0, "cycles_run": 379})
    assert runner.main(["--estimate"]) == 0
    doc = json.loads((tmp_path / "estimate.json").read_text(encoding="utf-8"))
    assert doc["estimated"] is True
    assert doc["measured_from"][0]["cycles"] == 379 + runner.TEST_CYCLES


def test_a_pure_per_cycle_cost_passes_the_rate_check():
    cells = []
    for config, cycles in (("2:1", 639), ("4:1", 462)):
        for _ in range(2):
            cells.append({"configuration": config, "complete": True,
                          "cycles_run": cycles - runner.TEST_CYCLES,
                          "engine_seconds": cycles * 0.25})
    check = runner.rate_proportionality(cells)
    assert check["checked"] is True and check["configurations"] == ["2:1", "4:1"]
    assert check["proportional_within_measured_range"] is True
    assert abs(check["fit"]["intercept_seconds"]) < 1.0
    assert check["fit"]["r_squared"] == 1.0


def test_a_per_world_charge_fails_the_rate_check_and_shows_as_an_intercept():
    cells = []
    for config, cycles in (("2:1", 639), ("6:1", 429)):
        for _ in range(2):
            cells.append({"configuration": config, "complete": True,
                          "cycles_run": cycles - runner.TEST_CYCLES,
                          "engine_seconds": 60.0 + 0.2 * cycles})
    check = runner.rate_proportionality(cells)
    assert check["proportional_within_measured_range"] is False, (
        "a fixed per-world charge makes the short horizon look dearer per cycle; if this "
        "passes, the check cannot see the thing the estimate assumes away")
    assert 55.0 < check["fit"]["intercept_seconds"] < 65.0
    assert check["shared_rate_interval"] is None


def test_the_rate_check_refuses_one_configuration():
    cells = [{"configuration": "6:1", "complete": True, "cycles_run": 379,
              "engine_seconds": 101.0}]
    check = runner.rate_proportionality(cells)
    assert check["checked"] is False and "minimum" in check["why"]


def test_the_allocation_record_matches_the_preassigned_block():
    """A hand-edited record cannot add a spare or a seed outside the block."""
    path = Path("docs/stage_b_allocation.json")
    if not path.exists():
        pytest.skip("no allocation record yet; the guard refuses every confirmatory seed")
    record = json.loads(path.read_text(encoding="utf-8"))
    stage = json.loads(Path("docs/stage_b_protocol.json").read_text(encoding="utf-8"))
    expected = sorted(seed for chunk in stage["seeds"]["preassigned"].values()
                      for seed in range(chunk["first"], chunk["last"] + 1))
    assert record["allocated"] is True
    assert sorted(record["seeds"]) == expected, "the record must equal the pre-assignment"
    assert len(expected) == stage["sample_size"]["worlds_total"]
    assert not (set(record["seeds"]) & set(range(runner.SPARES[0], runner.SPARES[1] + 1))), (
        "a spare must never appear in an allocation record")
    assert record["substitution_allowed"] is False
    runner.assert_runnable(700000001)
    runner.assert_runnable(700000720)


def test_shard_partitions_the_block_exactly_once():
    full = runner.block_jobs()
    assert len(full) == len(set(full)) == 720
    seen = []
    for index in range(1, 5):
        part = runner.shard_jobs(index, 4)
        assert len(part) == 180, len(part)
        assert {config for config, _ in part} == set(runner.CLAIMED), (
            "each shard must cover every configuration, or one machine that dies takes a "
            "whole configuration with it")
        seen.extend(part)
    assert sorted(seen) == sorted(full), "the shards must partition the block, not sample it"


def test_a_bad_shard_is_refused():
    assert runner.parse_shard("2/3") == (2, 3)
    for bad in ("0/3", "4/3", "3", "a/b", "1/0"):
        with pytest.raises(SystemExit):
            runner.parse_shard(bad)


def test_a_shard_half_block_carries_no_verdict_even_when_the_relation_shows():
    cells = []
    for config in runner.CLAIMED:
        cells += _planted(config, n=runner.PER_CONFIG // 2)
    result = runner.analyse(cells, reps=50)
    assert result["by_configuration"]["2:1"]["worlds"] == runner.PER_CONFIG // 2
    assert result["verdict"] == "NO VERDICT: PARTIAL ASSEMBLY", (
        "a shard covers every configuration but half the worlds; if this reports SUPPORTED, "
        "half the block can be read as the result")
    assert result["worlds_expected_per_configuration"] == runner.PER_CONFIG


def _block_assembly(reps: int = 10) -> dict:
    starts = {config: 700000001 + 180 * i for i, config in enumerate(runner.CLAIMED)}
    cells = []
    for config, start in starts.items():
        for i in range(runner.PER_CONFIG):
            cells.append({"configuration": config, "seed": start + i, "complete": True,
                          "eligible": True, "censored": False,
                          "horizon": runner.horizon_cycles(config),
                          "onset": 100 + i, "asserted_pairs_at_onset": 10 + i,
                          "outcome": 0.20 - 0.0005 * i, "outcome_cells": 4,
                          "outcome_occurrences": 2, "outcome_measurable": True})
    return {"cells": cells, "analysis": runner.analyse(cells, reps=reps)}


def test_verify_accepts_an_honest_assembly(tmp_path):
    doc = _block_assembly()
    path = tmp_path / "assembly.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    result = runner.verify_assembly(path, reps=10)
    assert result["passed"], result["problems"]
    assert result["block_complete"] is True
    assert result["verdict"]["match"] is True
    assert result["worlds_by_configuration"] == {c: 180 for c in runner.CLAIMED}


def test_verify_refuses_a_drawn_spare(tmp_path):
    doc = _block_assembly()
    doc["cells"][0]["seed"] = runner.SPARES[0]
    path = tmp_path / "assembly.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    result = runner.verify_assembly(path, reps=10)
    assert not result["passed"]
    assert any("spare" in problem for problem in result["problems"]), result["problems"]


def test_verify_catches_a_verdict_the_cells_do_not_support(tmp_path):
    doc = _block_assembly()
    assert doc["analysis"]["verdict"] == "SUPPORTED", doc["analysis"]["verdict"]
    doc["analysis"]["verdict"] = "NOT SUPPORTED"
    path = tmp_path / "assembly.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    result = runner.verify_assembly(path, reps=10)
    assert not result["passed"]
    assert result["verdict"]["match"] is False
    assert result["verdict"]["recomputed"] == "SUPPORTED"
    assert any("verdict" in problem for problem in result["problems"]), result["problems"]
