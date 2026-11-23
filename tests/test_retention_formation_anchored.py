"""The formation-anchored runner is built, but refuses before any database without a grant."""
LAYER = "synthetic"

import json
import random

import pytest

from benchmarks import retention_formation_anchored as runner
from benchmarks import retention_formation_anchored_prereg as block


def _unregistered_boundary_docs(docs_dir, registered, quoted):
    found = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if all(value in text for value in quoted) and path.name not in registered:
            found.append(path.name)
    return found


def test_dry_run_prints_twelve_cell_commands_without_opening_a_database(monkeypatch, capsys):
    def forbidden():
        raise AssertionError("dry-run opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    assert runner.main(["--dry-run"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert lines == [runner.command(seed) for seed in block.SEEDS]


def _ungranted(monkeypatch):
    doc = block.record()
    doc["status"] = "FROZEN, NOT RUN"
    doc["authorisation"] = {"required": True, "granted": False,
                            "document": None, "quote": None}
    doc["runner"]["built"] = True
    doc["runner"]["planned_module"] = runner.MODULE
    monkeypatch.setattr(block, "record", lambda: doc)
    return doc


def test_ungranted_cell_refuses_before_a_database_is_opened(monkeypatch):
    _ungranted(monkeypatch)

    def forbidden():
        raise AssertionError("ungranted cell opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    with pytest.raises(SystemExit) as exc:
        runner.cell(block.SEEDS[0])
    assert exc.value.code == 2
    assert runner.preflight()


def test_ungranted_run_cell_refuses_before_a_database_is_opened(monkeypatch):
    _ungranted(monkeypatch)

    def forbidden():
        raise AssertionError("ungranted run_cell opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    with pytest.raises(SystemExit) as exc:
        runner.run_cell(block.SEEDS[0])
    assert exc.value.code == 2


def test_ungranted_measure_refuses_before_a_database_is_opened(monkeypatch):
    _ungranted(monkeypatch)

    def forbidden():
        raise AssertionError("ungranted measure opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    with pytest.raises(SystemExit) as exc:
        runner.measure()
    assert exc.value.code == 2


def test_ungranted_finish_refuses_before_reading_parts(monkeypatch):
    _ungranted(monkeypatch)

    def forbidden():
        raise AssertionError("ungranted finish opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    with pytest.raises(SystemExit) as exc:
        runner.finish()
    assert exc.value.code == 2


def _granted(monkeypatch):
    doc = block.record()
    doc["status"] = "GRANTED, NOT RUN"
    doc["runner"]["cells_run"] = 0
    doc["runner"]["built"] = True
    doc["runner"]["planned_module"] = runner.MODULE
    doc["authorisation"] = {
        "required": True,
        "granted": True,
        "granted_on": "2026-11-12",
        "document": "docs/USER-MANUAL.md",
        "quote": "synthetic grant for a runner test",
    }
    monkeypatch.setattr(block, "record", lambda: doc)
    monkeypatch.setattr(block, "RESULT", block.ROOT / ".scratch" / "no_result.json")
    return doc


def test_complete_grant_passes_preflight(monkeypatch):
    _granted(monkeypatch)
    assert runner.preflight() == []


def test_recorded_run_is_confirmed_but_temporally_ambiguous():
    assert block.record()["status"] == "FROZEN, RUN"
    assert block.record()["runner"]["cells_run"] == 12
    assert block.RESULT.exists()
    summary = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))["summary"]
    assert summary["verdict"] == "CONFIRMED, TEMPORALLY AMBIGUOUS"
    assert summary["n_eligible"] == 172
    assert summary["n_complete"] == 166
    assert summary["n_events"] == 70
    assert summary["n_late_edges"] == 36
    assert summary["n_late_events"] == 18
    boundary = summary["reverse_boundary"]
    assert boundary == {"late_zero_edges": 55, "late_zero_events": 1,
                        "late_mid_edges": 100, "late_mid_events": 58,
                        "late_one_edges": 11, "late_one_events": 11}
    assert all(summary["gates"].values())
    assert summary["criteria"] == {"P1": True, "P2": True, "P3": True, "R1": False}


def test_granted_cell_uses_the_collection_hook_only(monkeypatch, tmp_path):
    _granted(monkeypatch)
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    called = []

    def fake_run(seed):
        called.append(seed)
        return {"seed": seed, "rows": []}

    monkeypatch.setattr(runner, "run_cell", fake_run)
    assert runner.cell(block.SEEDS[0]) == 0
    assert called == [block.SEEDS[0]]
    assert runner.part_path(block.SEEDS[0]).exists()


def test_cell_outside_the_seed_block_is_refused_after_the_grant(monkeypatch):
    _granted(monkeypatch)
    assert runner.cell(20619999) == 2


def test_finish_requires_every_part(monkeypatch, tmp_path):
    _granted(monkeypatch)
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    with pytest.raises(SystemExit) as exc:
        runner.finish()
    assert "missing parts" in str(exc.value)


def _row(seed, j, formation, asserted):
    landmark = formation + 19
    return {
        "seed": seed,
        "edge": "a%d-%d>b%d-%d" % (seed, j, seed, j),
        "asserted": asserted,
        "assertion_cycle": (landmark + 1 + (j % 10)) if asserted else None,
        "served_windows": 0,
        "ever_loop": True,
        "formation_cycle": formation,
        "landmark_cycle": landmark,
        "loop_cycles": list(range(formation, 120, 7)),
        "early_retention": 0.05 + (j % 17) / 20.0,
        "late_retention": 0.05 + (j % 13) / 20.0,
        "followup": (101 - formation) / 120.0,
        "rank20": 1 + (j % 40),
        "count20": j % 20,
        "strength20": 0.1 + (j % 9) / 10.0,
        "late_strength": 0.1 + (j % 7) / 10.0,
        "direct_count_final": j % 20,
    }


def _synthetic_rows():
    rows = []
    for si, seed in enumerate(block.SEEDS):
        for j in range(10):
            formation = 30 if j < 5 else 75
            rows.append(_row(seed, si * 10 + j, formation,
                             (si * 10 + j) % 3 == 0))
    return rows


def test_model_uses_followup_as_the_single_horizon_control():
    assert "followup" in runner.PRIMARY
    assert "formation" not in runner.PRIMARY
    assert "followup" in runner.REVERSE
    assert "formation" not in runner.REVERSE
    assert "single horizon control" in runner.MODEL_NOTE


def test_adjudicator_admits_the_late_cohort_and_applies_m9():
    rows = _synthetic_rows()
    summary = runner._adjudicate(rows)
    assert summary["n_eligible"] == len(rows)
    assert summary["n_events"] == sum(1 for row in rows if row["asserted"])
    assert summary["n_late_edges"] == 60
    assert summary["n_late_events"] >= block.MIN_LATE_EVENTS
    assert summary["gates"]["M9_late_representation"] is True
    assert summary["gates"]["M2_window_complete"] is True
    assert summary["verdict"] in block.build_prereg()["verdicts"]
    assert summary["verdict"] != "VOID"
    assert list(summary["criteria"]) == ["P1", "P2", "P3", "R1"]
    assert len(summary["gates"]) == 9


def test_post_landmark_onset_uses_the_first_cycle_after_the_landmark():
    assert runner._post_landmark_onset([10, 20, 30], True, 19) == 20
    assert runner._post_landmark_onset([10, 11, 12], True, 19) is None
    assert runner._post_landmark_onset([10, 20, 30], False, 19) is None
    assert runner._post_landmark_onset([], True, 19) is None


def test_first_appearance_before_the_landmark_plus_persistence_is_eligible():
    row = _row(block.SEEDS[0], 1, 30, True)
    appearances = [30, 49, 50, 60]
    assert min(appearances) == row["formation_cycle"]
    assert min(appearances) <= row["landmark_cycle"]
    row["assertion_cycle"] = runner._post_landmark_onset(
        appearances, row["asserted"], row["landmark_cycle"])
    assert row["assertion_cycle"] == 50
    assert row["edge"] in {eligible["edge"] for eligible in runner._eligible([row])}


def test_first_appearance_before_the_landmark_without_persistence_is_excluded():
    row = _row(block.SEEDS[0], 2, 30, True)
    appearances = [30, 40, 49]
    assert min(appearances) <= row["landmark_cycle"]
    assert max(appearances) == row["landmark_cycle"]
    row["assertion_cycle"] = runner._post_landmark_onset(
        appearances, row["asserted"], row["landmark_cycle"])
    assert row["assertion_cycle"] is None
    assert row["edge"] not in {eligible["edge"] for eligible in runner._eligible([row])}


def test_true_first_post_landmark_assertion_is_not_a_reentry():
    true_first = _row(block.SEEDS[0], 3, 30, True)
    true_first["assertion_cycle"] = 50
    true_first["first_structure_cycle"] = 50
    reentry = _row(block.SEEDS[0], 4, 30, True)
    reentry["assertion_cycle"] = 50
    reentry["first_structure_cycle"] = 30
    eligible = {row["edge"] for row in runner._eligible([true_first, reentry])}
    assert true_first["edge"] in eligible
    assert reentry["edge"] not in eligible


def test_first_structure_at_landmark_plus_one_is_admitted():
    at_landmark = _row(block.SEEDS[0], 8, 30, True)
    at_landmark["first_structure_cycle"] = at_landmark["landmark_cycle"]
    at_next = _row(block.SEEDS[0], 9, 30, True)
    at_next["first_structure_cycle"] = at_next["landmark_cycle"] + 1
    assert at_landmark["landmark_cycle"] == 49
    assert at_next["first_structure_cycle"] == 50
    eligible = {row["edge"] for row in runner._eligible([at_landmark, at_next])}
    assert at_landmark["edge"] not in eligible
    assert at_next["edge"] in eligible


def test_non_asserted_edge_with_pre_landmark_structure_presence_is_excluded():
    no_presence = _row(block.SEEDS[0], 5, 30, False)
    no_presence["first_structure_cycle"] = None
    pre_landmark = _row(block.SEEDS[0], 6, 30, False)
    pre_landmark["first_structure_cycle"] = 30
    assert pre_landmark["assertion_cycle"] is None
    eligible = {row["edge"] for row in runner._eligible([no_presence, pre_landmark])}
    assert no_presence["edge"] in eligible
    assert pre_landmark["edge"] not in eligible


def test_non_asserted_edge_with_post_landmark_structure_is_admitted():
    row = _row(block.SEEDS[0], 7, 30, False)
    row["first_structure_cycle"] = 50
    assert row["asserted"] is False
    assert row["assertion_cycle"] is None
    assert row["first_structure_cycle"] > row["landmark_cycle"]
    assert row["edge"] in {item["edge"] for item in runner._eligible([row])}


def test_eligible_requires_a_full_window_and_a_post_landmark_assertion():
    rows = [
        _row(block.SEEDS[0], 1, 90, True),
        _row(block.SEEDS[0], 2, 91, False),
    ]
    rows[0]["assertion_cycle"] = 109
    assert all(row["edge"] != rows[0]["edge"] for row in runner._eligible(rows))
    rows[0]["assertion_cycle"] = 110
    eligible = runner._eligible(rows)
    assert rows[0]["edge"] in {row["edge"] for row in eligible}
    assert rows[1]["edge"] not in {row["edge"] for row in eligible}


def test_every_fitted_row_falls_into_exactly_one_boundary_group():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    fitted = [row for row in runner._eligible(art["rows"])
              if row["rank20"] is not None]
    assert len(fitted) == art["summary"]["n_complete"] == 166
    for row in fitted:
        late = float(row["late_retention"])
        memberships = [late == 0.0, 0.0 < late < 1.0, late == 1.0]
        assert sum(memberships) == 1
    boundary = art["summary"]["reverse_boundary"]
    assert sum(1 for row in fitted if float(row["late_retention"]) == 0.0) == (
        boundary["late_zero_edges"])
    assert sum(1 for row in fitted if 0.0 < float(row["late_retention"]) < 1.0) == (
        boundary["late_mid_edges"])
    assert sum(1 for row in fitted if float(row["late_retention"]) == 1.0) == (
        boundary["late_one_edges"])
    assert (boundary["late_zero_edges"] + boundary["late_mid_edges"]
            + boundary["late_one_edges"] == len(fitted))


def test_every_asserted_event_falls_into_exactly_one_boundary_group():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    fitted = [row for row in runner._eligible(art["rows"])
              if row["rank20"] is not None]
    events = [row for row in fitted if row["asserted"]]
    assert len(events) == art["summary"]["n_events"] == 70
    for row in events:
        late = float(row["late_retention"])
        memberships = [late == 0.0, 0.0 < late < 1.0, late == 1.0]
        assert sum(memberships) == 1
    boundary = art["summary"]["reverse_boundary"]
    assert sum(1 for row in events if float(row["late_retention"]) == 0.0) == (
        boundary["late_zero_events"])
    assert sum(1 for row in events if 0.0 < float(row["late_retention"]) < 1.0) == (
        boundary["late_mid_events"])
    assert sum(1 for row in events if float(row["late_retention"]) == 1.0) == (
        boundary["late_one_events"])
    assert (boundary["late_zero_events"] + boundary["late_mid_events"]
            + boundary["late_one_events"] == len(events))
    assert (boundary["late_zero_events"] + boundary["late_mid_events"]
            + boundary["late_one_events"] == 70)


def test_rendered_boundary_line_matches_the_recorded_group_counts():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    b = art["summary"]["reverse_boundary"]
    expected = (
        "| Late-retention boundary | — | **%d/%d** at 0.0; **%d/%d** in between; "
        "**%d/%d** at 1.0 |" % (
            b["late_zero_events"], b["late_zero_edges"],
            b["late_mid_events"], b["late_mid_edges"],
            b["late_one_events"], b["late_one_edges"]))
    assert expected in runner.PAGE.read_text(encoding="utf-8")


def test_rendered_boundary_sentence_matches_the_recorded_group_counts():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    b = art["summary"]["reverse_boundary"]
    expected = (
        "The reverse OR is a boundary contrast, not a dose-response: "
        "**%d/%d** edges at late retention 0.0 were asserted, **%d/%d** in "
        "between, against **%d/%d** at 1.0. Both coefficients remain "
        "observational." % (
            b["late_zero_events"], b["late_zero_edges"],
            b["late_mid_events"], b["late_mid_edges"],
            b["late_one_events"], b["late_one_edges"]))
    assert expected in runner.PAGE.read_text(encoding="utf-8")


def test_manual_boundary_row_matches_the_recorded_group_counts():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    b = art["summary"]["reverse_boundary"]
    expected = (
        "reverse boundary **%d/%d** at 0.0, **%d/%d** in between, "
        "**%d/%d** at 1.0" % (
            b["late_zero_events"], b["late_zero_edges"],
            b["late_mid_events"], b["late_mid_edges"],
            b["late_one_events"], b["late_one_edges"]))
    manual = (runner.ROOT / "docs" / "USER-MANUAL.md").read_text(encoding="utf-8")
    assert expected in manual


def test_hierarchy_boundary_sentence_matches_the_recorded_group_counts():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    b = art["summary"]["reverse_boundary"]
    expected = (
        "but the reverse OR is a boundary contrast: **%d/%d** edges at late "
        "retention **1.0** are asserted, **%d/%d** in between, against "
        "**%d/%d** at **0.0**." % (
            b["late_one_events"], b["late_one_edges"],
            b["late_mid_events"], b["late_mid_edges"],
            b["late_zero_events"], b["late_zero_edges"]))
    hierarchy = (runner.ROOT / "docs" / "RESEARCH-HIERARCHY.md").read_text(
        encoding="utf-8")
    assert expected in hierarchy


def test_audit_boundary_sentence_matches_the_recorded_group_counts():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    b = art["summary"]["reverse_boundary"]
    expected = (
        "**%d/%d** ceiling cases are asserted, **%d/%d** middle cases are "
        "asserted, and **%d/%d** zero cases are asserted." % (
            b["late_one_events"], b["late_one_edges"],
            b["late_mid_events"], b["late_mid_edges"],
            b["late_zero_events"], b["late_zero_edges"]))
    audit = (runner.ROOT / "docs" / "RETENTION-REVERSE-OVERLAP-AUDIT.md"
             ).read_text(encoding="utf-8")
    assert expected in audit


def test_entry_prereg_boundary_sentence_matches_the_recorded_group_counts():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    b = art["summary"]["reverse_boundary"]
    expected = (
        "The reverse audit found the late OR stable to the follow-up control "
        "but concentrated at the boundaries: **%d/%d** edges at late "
        "retention **1.0** were asserted, **%d/%d** in between, against "
        "**%d/%d** at **0.0**." % (
            b["late_one_events"], b["late_one_edges"],
            b["late_mid_events"], b["late_mid_edges"],
            b["late_zero_events"], b["late_zero_edges"]))
    page = (runner.ROOT / "docs" /
            "RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md").read_text(
                encoding="utf-8")
    assert expected in page


def test_every_boundary_document_carries_the_recorded_group_counts():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    b = art["summary"]["reverse_boundary"]
    counts = (b["late_zero_events"], b["late_zero_edges"],
              b["late_mid_events"], b["late_mid_edges"],
              b["late_one_events"], b["late_one_edges"])
    expected = {
        "RETENTION-FORMATION-ANCHORED.md": [
            "| Late-retention boundary | — | **%d/%d** at 0.0; **%d/%d** in "
            "between; **%d/%d** at 1.0 |" % counts,
            "The reverse OR is a boundary contrast, not a dose-response: "
            "**%d/%d** edges at late retention 0.0 were asserted, **%d/%d** "
            "in between, against **%d/%d** at 1.0. Both coefficients remain "
            "observational." % counts,
        ],
        "USER-MANUAL.md": [
            "reverse boundary **%d/%d** at 0.0, **%d/%d** in between, "
            "**%d/%d** at 1.0" % counts,
        ],
        "RESEARCH-HIERARCHY.md": [
            "but the reverse OR is a boundary contrast: **%d/%d** edges at "
            "late retention **1.0** are asserted, **%d/%d** in between, "
            "against **%d/%d** at **0.0**." % (
                counts[4], counts[5], counts[2], counts[3], counts[0], counts[1]),
        ],
        "RETENTION-REVERSE-OVERLAP-AUDIT.md": [
            "**%d/%d** ceiling cases are asserted, **%d/%d** middle cases are "
            "asserted, and **%d/%d** zero cases are asserted." % (
                counts[4], counts[5], counts[2], counts[3], counts[0], counts[1]),
        ],
        "RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md": [
            "The reverse audit found the late OR stable to the follow-up "
            "control but concentrated at the boundaries: **%d/%d** edges at "
            "late retention **1.0** were asserted, **%d/%d** in between, "
            "against **%d/%d** at **0.0**." % (
                counts[4], counts[5], counts[2], counts[3], counts[0], counts[1]),
        ],
        "RETENTION-ENTRY-TRANSITION-DESIGN.md": [
            "The reverse association was also a boundary contrast, not a "
            "dose-response: **%d/%d** edges at late retention **1.0** were "
            "asserted, **%d/%d** in between, against **%d/%d** at **0.0**." % (
                counts[4], counts[5], counts[2], counts[3], counts[0], counts[1]),
        ],
    }
    for name, needles in expected.items():
        text = (runner.ROOT / "docs" / name).read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text, name
    quoted = ["%d/%d" % (counts[index], counts[index + 1])
              for index in (0, 2, 4)]
    unregistered = _unregistered_boundary_docs(
        runner.ROOT / "docs", set(expected), quoted)
    assert not unregistered, (
        "%s quote all three boundary counts; add them to expected"
        % ", ".join(unregistered))


def test_entry_design_boundary_sentence_matches_the_recorded_group_counts():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    b = art["summary"]["reverse_boundary"]
    expected = (
        "The reverse association was also a boundary contrast, not a "
        "dose-response: **%d/%d** edges at late retention **1.0** were "
        "asserted, **%d/%d** in between, against **%d/%d** at **0.0**." % (
            b["late_one_events"], b["late_one_edges"],
            b["late_mid_events"], b["late_mid_edges"],
            b["late_zero_events"], b["late_zero_edges"]))
    design = (runner.ROOT / "docs" / "RETENTION-ENTRY-TRANSITION-DESIGN.md"
              ).read_text(encoding="utf-8")
    assert expected in design


def test_boundary_inventory_scan_flags_an_unregistered_document(tmp_path):
    (tmp_path / "KNOWN.md").write_text("1/55 58/100 11/11", encoding="utf-8")
    (tmp_path / "UNREGISTERED.md").write_text(
        "quotes 1/55, 58/100 and 11/11", encoding="utf-8")
    assert _unregistered_boundary_docs(
        tmp_path, {"KNOWN.md"}, ["1/55", "58/100", "11/11"]) == [
            "UNREGISTERED.md"]


def test_check_reports_the_confirmed_result_and_the_page_reads_coefficients():
    assert runner.ARTIFACT.exists()
    assert runner.main(["--check"]) == 0
    page = runner.PAGE.read_text(encoding="utf-8")
    assert "**Verdict: `CONFIRMED, TEMPORALLY AMBIGUOUS`.**" in page
    assert "Early-retention OR" in page
    assert "Post-landmark retention also has a positive association" in page
    assert "| Late-retention boundary | — | **1/55** at 0.0; **58/100** in between; **11/11** at 1.0 |" in page
    assert "The reverse OR is a boundary contrast" in page
    assert "preregistration, not a result" not in page
