"""The entry-transition runner captures full appearance cycles and refuses unrun."""
LAYER = "synthetic"

import json

import pytest

from benchmarks import retention_entry_transition as runner
from benchmarks import retention_entry_transition_prereg as block


def test_dry_run_prints_twenty_four_cell_commands_without_opening_a_database(
        monkeypatch, capsys):
    def forbidden():
        raise AssertionError("dry-run opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    assert runner.main(["--dry-run"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert lines == [runner.command(seed) for seed in block.SEEDS]
    assert len(lines) == 24


def _ungranted(monkeypatch):
    doc = block.record()
    doc["status"] = "FROZEN, NOT RUN"
    doc["authorisation"] = {"required": True, "granted": False,
                            "document": None, "quote": None}
    doc["runner"]["built"] = True
    doc["runner"]["planned_module"] = runner.MODULE
    monkeypatch.setattr(block, "record", lambda: doc)
    return doc


def test_ungranted_paths_refuse_before_a_database_is_opened(monkeypatch):
    _ungranted(monkeypatch)

    def forbidden():
        raise AssertionError("ungranted path opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    for call in (lambda: runner.cell(block.SEEDS[0]),
                 lambda: runner.run_cell(block.SEEDS[0]),
                 runner.measure, runner.finish):
        with pytest.raises(SystemExit) as exc:
            call()
        assert exc.value.code == 2
    assert runner.preflight()


def test_granted_cell_uses_the_collection_hook_only(monkeypatch, tmp_path):
    doc = block.record()
    doc["status"] = "GRANTED, NOT RUN"
    doc["runner"]["cells_run"] = 0
    doc["runner"]["built"] = True
    doc["runner"]["planned_module"] = runner.MODULE
    doc["authorisation"] = {
        "required": True,
        "granted": True,
        "granted_on": "2026-11-13",
        "document": "docs/USER-MANUAL.md",
        "quote": "synthetic grant for a runner test",
    }
    monkeypatch.setattr(block, "record", lambda: doc)
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    called = []

    def fake_run(seed):
        called.append(seed)
        return {"seed": seed, "rows": []}

    monkeypatch.setattr(runner, "run_cell", fake_run)
    assert runner.cell(block.SEEDS[0]) == 0
    assert called == [block.SEEDS[0]]
    assert runner.part_path(block.SEEDS[0]).exists()


def test_sustained_entry_needs_two_adjacent_cycles_after_the_quiet_interval():
    formation = 30
    assert runner._entry_cycle([70], formation, 120) is None
    assert runner._entry_cycle([70, 71], formation, 120) == 70
    assert runner._entry_cycle([70, 75, 76], formation, 120) == 75
    assert runner._entry_cycle([69, 70, 71], formation, 120) == 70
    assert runner._entry_cycle([119, 120], formation, 120) == 119
    assert runner._entry_cycle([120], formation, 120) is None
    assert runner._entry_cycle([70, 71], None, 120) is None


def test_structure_free_rejects_any_appearance_through_f_plus_39():
    assert runner._structure_free([], 30) is True
    assert runner._structure_free([70, 71], 30) is True
    assert runner._structure_free([69], 30) is False
    assert runner._structure_free([30, 70, 71], 30) is False
    assert runner._structure_free([], None) is None


def _row(seed, j, formation=30, appearances=None, entry=True):
    if appearances is None:
        appearances = [formation + 40, formation + 41] if entry else []
    return {
        "seed": seed,
        "edge": "a%d-%d>b%d-%d" % (seed, j, seed, j),
        "served_windows": 0,
        "ever_loop": True,
        "formation_cycle": formation,
        "loop_cycles": list(range(formation, 120, 3)),
        "appearances": sorted(appearances),
        "structure_free_through_f39": runner._structure_free(appearances, formation),
        "early_retention": 0.05 + (j % 17) / 20.0,
        "proximal_retention": 0.05 + ((j * 7) % 19) / 20.0,
        "followup": (120 - (formation + 40) + 1) / 120.0,
        "rank20": 1 + (j % 40),
        "rank40": 1 + ((j * 3) % 40),
        "count20": j % 20,
        "count40": (j * 3) % 20,
        "strength20": 0.1 + (j % 9) / 10.0,
        "strength40": 0.1 + ((j * 5) % 9) / 10.0,
        "entry_cycle": runner._entry_cycle(appearances, formation, 120),
        "final_assertion": entry and j % 2 == 0,
    }


def test_eligible_requires_a_complete_sorted_appearance_list_and_no_early_presence():
    good = _row(block.SEEDS[0], 1)
    reentry = _row(block.SEEDS[0], 2, appearances=[30, 70, 71])
    unsorted = _row(block.SEEDS[0], 3)
    unsorted["appearances"] = [71, 70]
    eligible = {row["edge"] for row in runner._eligible([good, reentry, unsorted])}
    assert good["edge"] in eligible
    assert reentry["edge"] not in eligible
    assert unsorted["edge"] not in eligible


def test_entry_validity_checks_both_cycles_and_the_quiet_interval():
    assert runner._entry_valid(_row(block.SEEDS[0], 1))
    one_cycle = _row(block.SEEDS[0], 2, appearances=[70])
    assert runner._entry_valid(one_cycle)
    early = _row(block.SEEDS[0], 3, appearances=[69, 70, 71])
    assert not runner._entry_valid(early)


def test_adjudicator_reports_all_ten_gates_on_a_full_synthetic_block():
    rows = []
    for si, seed in enumerate(block.SEEDS):
        for j in range(3):
            rows.append(_row(seed, si * 3 + j,
                             formation=30 + (si * 3 + j) % 10,
                             entry=(si + j) % 2 == 0))
    summary = runner._adjudicate(rows)
    assert summary["n_eligible"] == 72
    assert summary["n_events"] == 36
    assert list(summary["gates"]) == [
        "D1_population", "D2_structure_free", "D3_rank_coverage",
        "D4_seed_levels", "D5_convergence", "D6_complete",
        "D7_entry_validity", "D8_no_collision", "D9_separation",
        "D10_exposure",
    ]
    assert summary["gates"]["D1_population"] is True
    assert summary["gates"]["D2_structure_free"] is True
    assert summary["gates"]["D5_convergence"] is True
    assert summary["gates"]["D7_entry_validity"] is True
    assert summary["gates"]["D10_exposure"] is True
    assert summary["verdict"] != "VOID"
    assert summary["verdict"] in block.build_prereg()["verdicts"]


def test_load_parts_rejects_an_incomplete_120_cycle_appearance_capture(
        monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned", lambda: [block.SEEDS[0]])
    part = {
        "prereg": block.ID,
        "seed": block.SEEDS[0],
        "cycles": block.CYCLES,
        "cap": block.CAP,
        "appearance_cycles_captured": block.CYCLES - 1,
        "rows": [],
    }
    runner.part_path(block.SEEDS[0]).write_text(json.dumps(part), encoding="utf-8")
    with pytest.raises(SystemExit, match="did not capture every cycle"):
        runner._load_parts()
    assert not runner.ARTIFACT.exists()


def _part_with_appearances(appearances):
    return {
        "prereg": block.ID,
        "seed": block.SEEDS[0],
        "cycles": block.CYCLES,
        "cap": block.CAP,
        "appearance_cycles_captured": block.CYCLES,
        "rows": [{"seed": block.SEEDS[0], "edge": "a>b",
                  "appearances": appearances}],
    }


@pytest.mark.parametrize("appearances", [
    [0, 70], [70, 121], [70, 70],
    [70, "121"], [70, 120.5], [70, True], "70", None,
])
def test_load_parts_rejects_invalid_row_appearance_cycles(
        monkeypatch, tmp_path, appearances):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned", lambda: [block.SEEDS[0]])
    part = _part_with_appearances(appearances)
    runner.part_path(block.SEEDS[0]).write_text(json.dumps(part), encoding="utf-8")
    with pytest.raises(SystemExit, match="invalid appearance cycles"):
        runner._load_parts()
    runner.part_path(block.SEEDS[0]).write_text(
        json.dumps(_part_with_appearances([1, 120])), encoding="utf-8")
    assert len(runner._load_parts()) == 1
    assert not runner.ARTIFACT.exists()


def test_load_parts_rejects_duplicate_row_edges_within_a_seed(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned", lambda: [block.SEEDS[0]])
    part = _part_with_appearances([70, 71])
    part["rows"].append({"seed": block.SEEDS[0], "edge": "a>b",
                         "appearances": [1, 120]})
    runner.part_path(block.SEEDS[0]).write_text(json.dumps(part), encoding="utf-8")
    with pytest.raises(SystemExit, match="duplicates edge"):
        runner._load_parts()
    part["rows"][1]["edge"] = "c>d"
    runner.part_path(block.SEEDS[0]).write_text(json.dumps(part), encoding="utf-8")
    assert len(runner._load_parts()) == 1
    assert not runner.ARTIFACT.exists()


def test_load_parts_rejects_a_row_seed_that_differs_from_its_part(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned", lambda: [block.SEEDS[0]])
    part = _part_with_appearances([1, 120])
    part["rows"].append({"seed": block.SEEDS[0] + 1, "edge": "c>d",
                         "appearances": [1, 120]})
    runner.part_path(block.SEEDS[0]).write_text(json.dumps(part), encoding="utf-8")
    with pytest.raises(SystemExit, match="does not match part seed"):
        runner._load_parts()
    part["rows"][1]["seed"] = block.SEEDS[0]
    runner.part_path(block.SEEDS[0]).write_text(json.dumps(part), encoding="utf-8")
    assert len(runner._load_parts()) == 1
    assert not runner.ARTIFACT.exists()


@pytest.mark.parametrize("appearances", ["70", None, 70])
def test_load_parts_rejects_non_list_row_appearances(
        monkeypatch, tmp_path, appearances):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned", lambda: [block.SEEDS[0]])
    part = _part_with_appearances(appearances)
    runner.part_path(block.SEEDS[0]).write_text(json.dumps(part), encoding="utf-8")
    with pytest.raises(SystemExit, match="appearances are not a list"):
        runner._load_parts()
    assert not runner.ARTIFACT.exists()


def test_load_parts_keeps_every_row_of_a_valid_multi_edge_part(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned", lambda: [block.SEEDS[0]])
    part = _part_with_appearances([1, 120])
    part["rows"] = [
        {"seed": block.SEEDS[0], "edge": "a>b", "appearances": [1, 120]},
        {"seed": block.SEEDS[0], "edge": "b>c", "appearances": [70, 71]},
        {"seed": block.SEEDS[0], "edge": "c>d", "appearances": [120]},
    ]
    runner.part_path(block.SEEDS[0]).write_text(json.dumps(part), encoding="utf-8")
    loaded = runner._load_parts()
    assert len(loaded) == 1
    assert loaded[0]["rows"] == part["rows"]
    assert [row["edge"] for row in loaded[0]["rows"]] == ["a>b", "b>c", "c>d"]
    assert not runner.ARTIFACT.exists()


def test_load_parts_rejects_an_empty_planned_seed_block(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned", lambda: [])
    with pytest.raises(SystemExit, match="planned seed block is empty"):
        runner._load_parts()
    assert not runner.ARTIFACT.exists()


def test_empty_planned_seed_guard_fires_even_when_a_part_exists(
        monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    seed = block.SEEDS[0]
    part = _part_with_appearances([1, 120])
    runner.part_path(seed).write_text(json.dumps(part), encoding="utf-8")

    monkeypatch.setattr(runner, "planned", lambda: [seed])
    assert runner._load_parts() == [part]

    monkeypatch.setattr(runner, "planned", lambda: [])
    with pytest.raises(SystemExit, match="planned seed block is empty"):
        runner._load_parts()
    assert runner.part_path(seed).exists()
    assert not runner.ARTIFACT.exists()


def test_load_parts_rejects_duplicate_planned_seeds(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned",
                        lambda: [block.SEEDS[0], block.SEEDS[0]])
    part = _part_with_appearances([1, 120])
    runner.part_path(block.SEEDS[0]).write_text(json.dumps(part), encoding="utf-8")
    with pytest.raises(SystemExit, match="duplicate planned seeds"):
        runner._load_parts()
    assert not runner.ARTIFACT.exists()


def test_duplicate_planned_seed_guard_fails_with_a_clean_part_on_disk(
        monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    seed = block.SEEDS[0]
    part = _part_with_appearances([1, 120])
    runner.part_path(seed).write_text(json.dumps(part), encoding="utf-8")

    monkeypatch.setattr(runner, "planned", lambda: [seed])
    assert runner._load_parts() == [part]

    monkeypatch.setattr(runner, "planned", lambda: [seed, seed])
    with pytest.raises(SystemExit, match="duplicate planned seeds"):
        runner._load_parts()
    assert not runner.ARTIFACT.exists()


def test_load_parts_preserves_planned_seed_order(monkeypatch, tmp_path):
    order = [block.SEEDS[2], block.SEEDS[0], block.SEEDS[1]]
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned", lambda: order)
    for seed in [block.SEEDS[1], block.SEEDS[2], block.SEEDS[0]]:
        part = _part_with_appearances([1, 120])
        part["seed"] = seed
        part["rows"][0]["seed"] = seed
        runner.part_path(seed).write_text(json.dumps(part), encoding="utf-8")
    assert [part["seed"] for part in runner._load_parts()] == order
    assert not runner.ARTIFACT.exists()


def test_load_parts_keeps_unique_edges_across_multiple_parts(monkeypatch, tmp_path):
    seeds = [block.SEEDS[0], block.SEEDS[1]]
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    monkeypatch.setattr(runner, "planned", lambda: seeds)
    written = {}
    for index, seed in enumerate(seeds):
        part = _part_with_appearances([1, 120])
        part["seed"] = seed
        part["rows"] = [
            {"seed": seed, "edge": "a%d>b%d" % (index, index),
             "appearances": [1, 120]},
            {"seed": seed, "edge": "b%d>c%d" % (index, index),
             "appearances": [70, 71]},
        ]
        written[seed] = part
        runner.part_path(seed).write_text(json.dumps(part), encoding="utf-8")
    loaded = runner._load_parts()
    assert [part["seed"] for part in loaded] == seeds
    assert [part["rows"] for part in loaded] == [written[seed]["rows"] for seed in seeds]
    assert not runner.ARTIFACT.exists()


def test_check_is_ready_and_reports_the_missing_grant(capsys):
    assert not block.RESULT.exists()
    assert runner.main(["--check"]) == 0
    out = capsys.readouterr().out
    assert "runner built; no result has been written" in out
    assert "the dated grant is not recorded" in out
