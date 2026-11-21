"""The prediction cap moves A at loop cap 120; joint C1 moves less than min(A,K)."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json
from pathlib import Path

from benchmarks import a1_prediction_cap_c1 as pc

DOC = json.loads(Path("docs/a1_prediction_cap_c1.json").read_text(encoding="utf-8"))
C1 = json.loads(Path("docs/a1_c1_cap120.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert pc.problems(DOC) == []
    assert pc.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["rows"]) == 54


def test_cap_40_control_reproduces_the_committed_cap_120_rows():
    control = {(row["block"], row["seed"]): row
               for row in C1["rows"] if row["cap"] == 120}
    for row in DOC["rows"]:
        if row["prediction_cap"] != 40:
            continue
        want = control[(row["block"], row["seed"])]
        assert (row["A"], row["K"], row["A_and_K"]) == (
            want["A"], want["K"], want["A_and_K"])


def test_a_rises_while_k_is_flat():
    rows = {row["prediction_cap"]: row for row in DOC["summaries"]}
    assert (rows[20]["A_total"], rows[40]["A_total"], rows[80]["A_total"]) == (
        744, 913, 1129)
    assert (rows[20]["K_total"], rows[40]["K_total"], rows[80]["K_total"]) == (
        1499, 1498, 1497)
    assert rows[80]["A_total"] - rows[40]["A_total"] == 216
    assert abs(rows[80]["K_total"] - rows[40]["K_total"]) <= 1


def test_marginal_and_joint_pass_counts_diverge():
    rows = {row["prediction_cap"]: row for row in DOC["summaries"]}
    assert (rows[20]["C1_marginal_pass"], rows[20]["C1_joint_pass"]) == (0, 0)
    assert (rows[40]["C1_marginal_pass"], rows[40]["C1_joint_pass"]) == (2, 0)
    assert (rows[80]["C1_marginal_pass"], rows[80]["C1_joint_pass"]) == (6, 4)
    assert rows[80]["A_and_K_total"] == 1025


def test_only_larger_28_passes_jointly():
    blocks = {row["label"]: row for row in DOC["by_block"]}
    for label, low, a40, a80, k80, both, passes in (
            ("current-16", 243, 281, 317, 382, 317, 0),
            ("fresh-16", 230, 279, 314, 383, 314, 0),
            ("larger-28", 271, 353, 498, 732, 394, 4)):
        assert blocks[label]["20"]["A"] == low
        assert blocks[label]["40"]["A"] == a40
        assert blocks[label]["80"]["A"] == a80
        assert blocks[label]["80"]["K"] == k80
        assert blocks[label]["80"]["A_and_K"] == both
        assert blocks[label]["80"]["C1_joint_pass"] == passes


def test_the_four_joint_passes_are_named():
    rows = [row for row in DOC["rows"]
            if row["prediction_cap"] == 80 and row["C1_joint_pass"]]
    assert {row["seed"]: row["C1_joint"] for row in rows} == {
        20660101: 68, 20660104: 77, 20660105: 72, 20660106: 70,
    }
    assert all(row["block"] == "larger-28" for row in rows)
    failed = {row["seed"]: row["C1_joint"] for row in DOC["rows"]
              if row["prediction_cap"] == 80
              and row["block"] == "larger-28" and not row["C1_joint_pass"]}
    assert failed == {20660102: 56, 20660103: 51}


def test_16_tag_joint_maximum_is_still_short():
    rows = [row for row in DOC["rows"]
            if row["prediction_cap"] == 80 and row["block"] != "larger-28"]
    assert max(row["C1_joint"] for row in rows) == 59
    assert all(not row["C1_joint_pass"] for row in rows)


def test_a_tampered_joint_ceiling_is_reported():
    bad = copy.deepcopy(DOC)
    row = next(row for row in bad["rows"] if row["prediction_cap"] == 80)
    row["C1_joint"] += 1

    assert pc.problems(bad), "a joint ceiling inconsistent with A∩K must fail"


def test_page_is_current():
    assert pc.PAGE_PATH.read_text(encoding="utf-8") == pc.render(DOC)
    text = pc.PAGE_PATH.read_text(encoding="utf-8")
    assert "A responds to the prediction cap" in text
    assert "4/18" in text
    assert "6/18" in text
