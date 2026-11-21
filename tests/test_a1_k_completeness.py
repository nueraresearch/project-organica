"""K completeness separates blocks but does not explain the cap response."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json
from pathlib import Path

from benchmarks import a1_k_completeness as kc

DOC = json.loads(Path("docs/a1_k_completeness.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert kc.problems(DOC) == []
    assert kc.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["rows"]) == 72


def test_16_tag_is_k_complete_at_every_cap():
    rows = [row for row in DOC["rows"] if row["block"] != "larger-28"]
    assert len(rows) == 48
    assert {row["K_completeness"] for row in rows} == {1.0}
    assert {row["K_coverage_of_A"] for row in rows} == {1.0}


def test_larger_28_is_the_only_incomplete_block():
    rows = [row for row in DOC["rows"] if row["block"] == "larger-28"]
    assert min(row["K_completeness"] for row in rows) == 0.610465
    assert max(row["K_completeness"] for row in rows) == 0.848485
    assert all(row["K_completeness"] < 1.0 for row in rows)
    assert DOC["separation"] == {
        "min_16_completeness": 1.0,
        "max_larger_completeness": 0.848485,
        "margin": 0.151515,
        "threshold": 0.9,
        "classification_accuracy": 1.0,
        "rows": 72,
    }


def test_completeness_is_nearly_static_across_caps():
    caps = {row["prediction_cap"]: row for row in DOC["summary"]}
    assert [caps[cap]["K_completeness"] for cap in (20, 40, 80, 112)] == [
        0.849292, 0.848725, 0.848159, 0.848159,
    ]
    assert max(DOC["larger_completeness_ranges"].values()) == 0.012121


def test_joint_passes_move_while_completeness_does_not():
    assert DOC["joint_caps"] == {"20": 0, "40": 0, "80": 4, "112": 8}
    assert DOC["larger_joint_caps"] == {
        "20": 0, "40": 0, "80": 4, "112": 6,
    }
    cap112 = [row for row in DOC["rows"]
              if row["prediction_cap"] == 112 and row["block"] != "larger-28"]
    assert sum(row["C1_joint_pass"] for row in cap112) == 2


def test_completeness_does_not_order_joint_success():
    cap80 = [row for row in DOC["rows"]
             if row["prediction_cap"] == 80 and row["block"] == "larger-28"]
    passing = [row for row in cap80 if row["C1_joint_pass"]]
    failing = [row for row in cap80 if not row["C1_joint_pass"]]
    assert min(row["K_completeness"] for row in passing) == 0.656805
    assert max(row["K_completeness"] for row in failing) == 0.742515
    assert DOC["cap80_overlap_not_monotone"] is True


def test_a_tampered_completeness_is_reported():
    bad = copy.deepcopy(DOC)
    bad["rows"][0]["K_completeness"] += 0.01

    assert kc.problems(bad), "completeness must equal K / candidates"


def test_page_is_current():
    assert kc.PAGE_PATH.read_text(encoding="utf-8") == kc.render(DOC)
    text = kc.PAGE_PATH.read_text(encoding="utf-8")
    assert "regime marker" in text
    assert "0 → 0 → 4 → 8" in text
    assert "0.657" in text and "0.743" in text
