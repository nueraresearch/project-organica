"""The no-arm baseline audit measures C1 denominators and C4 stream rows."""
LAYER = "static"  # reads the committed audit and synthetic rows; runs no engine cell
import json
from pathlib import Path

from benchmarks import a1_baseline_availability as audit
from benchmarks import a1_two_path


def _artifact():
    return json.loads(Path("docs/a1_baseline_availability.json").read_text(encoding="utf-8"))


def test_baseline_audit_is_clean_and_flags_both_streams():
    doc = _artifact()
    assert audit.problems(doc) == []
    assert doc["status"].startswith("FLAGGED — C1 FLOOR NOT REACHED")
    assert doc["cycles"] == 120
    assert doc["c1_floor"] == 60
    assert doc["totals"]["c1_floor_pass"] is False
    assert doc["totals"]["protocol"]["c1_floor_pass"] is False
    assert doc["totals"]["c4_measured_deltas"] == 0
    assert a1_two_path.manifest()["frozen"] is False


def test_cell_stream_counts_are_observed_not_planned():
    doc = _artifact()
    first = doc["per_seed"][0]
    assert first["candidate_rows"] == 112
    assert first["c4_non_target_rows_n4"] == 108
    assert first["c4_non_target_rows_n20"] == 92
    assert first["c1_a_minus_denominator"] == 82
    assert first["c1_k_minus_denominator"] == 70
    assert first["c1_min_denominator"] == 70
    assert doc["totals"]["c4_non_target_rows_n4"] == 648
    assert doc["totals"]["c1_min_denominator"] == 58
    assert [row["seed"] for row in doc["per_seed"] if not row["c1_floor_pass"]] == [
        20630102, 20630104]


def test_candidate_protocol_stream_is_narrower_and_also_below_floor():
    doc = _artifact()
    first = doc["per_seed"][0]["protocol"]
    assert first["candidate_rows"] == 64
    assert first["c4_non_target_rows_n4"] == 60
    assert first["c4_non_target_rows_n20"] == 44
    assert first["c1_a_minus_denominator"] == 44
    assert first["c1_k_minus_denominator"] == 44
    assert first["c1_min_denominator"] == 44
    assert all(not row["protocol"]["c1_floor_pass"] for row in doc["per_seed"])
    assert doc["totals"]["protocol"]["c4_non_target_rows_n4"] == 358
    assert doc["totals"]["protocol"]["c1_min_denominator"] == 31
    assert doc["stream_divergence"]["extra_cell_rows"] == 290


def test_page_is_rendered_from_the_audit():
    doc = _artifact()
    page = Path("docs/A1-BASELINE-AVAILABILITY.md").read_text(encoding="utf-8")
    assert page == audit.render(doc) + "\n"
    assert "DESIGN INCONSISTENCY" in page
    assert "C1 FLOOR NOT REACHED" in page


def test_stream_counts_separate_targets_and_protocol_rows():
    rows = [
        {"edge": "a>b", "A": True, "K": True, "Y": True},
        {"edge": "c>d", "A": True, "K": False, "Y": False},
        {"edge": "e>f", "A": False, "K": True, "Y": False},
    ]
    summary = audit._summary(1, rows, {"a>b"}, {"a>b", "c>d"},
                             {"a>b", "c>d"})
    assert summary["c1_a_minus_denominator"] == 2
    assert summary["c1_k_minus_denominator"] == 2
    assert summary["c4_non_target_rows_n4"] == 2
    assert summary["c4_non_target_rows_n20"] == 1
    assert summary["protocol"]["candidate_rows"] == 2
    assert summary["protocol"]["c4_non_target_rows_n4"] == 1
    assert summary["protocol"]["c4_non_target_rows_n20"] == 0
    assert summary["c1_floor_pass"] is False


def test_audit_self_test_is_clean():
    assert audit.self_test() == []
