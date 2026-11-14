"""At cap 112, only two of twelve 16-tag seeds clear the joint C1 floor."""
import copy
import json
from pathlib import Path

from benchmarks import a1_prediction_cap_112 as pc

DOC = json.loads(Path("docs/a1_prediction_cap_112.json").read_text(encoding="utf-8"))
C1 = json.loads(Path("docs/a1_c1_cap120.json").read_text(encoding="utf-8"))
REF = json.loads(Path("docs/a1_prediction_cap_c1.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert pc.problems(DOC) == []
    assert pc.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["rows"]) == 54


def test_both_controls_reproduce_their_committed_rows():
    control = {(row["block"], row["seed"]): row
               for row in C1["rows"] if row["cap"] == 120}
    reference = {(row["block"], row["seed"]): row
                 for row in REF["rows"] if row["prediction_cap"] == 80}
    for row in DOC["rows"]:
        if row["prediction_cap"] == 40:
            want = control[(row["block"], row["seed"])]
        elif row["prediction_cap"] == 80:
            want = reference[(row["block"], row["seed"])]
        else:
            continue
        assert (row["A"], row["K"], row["A_and_K"]) == (
            want["A"], want["K"], want["A_and_K"])


def test_cap_112_lifts_a_but_not_k():
    rows = {row["prediction_cap"]: row for row in DOC["summaries"]}
    assert (rows[40]["A_total"], rows[80]["A_total"], rows[112]["A_total"]) == (
        913, 1129, 1269)
    assert (rows[40]["K_total"], rows[80]["K_total"], rows[112]["K_total"]) == (
        1498, 1497, 1497)
    assert rows[112]["A_total"] - rows[80]["A_total"] == 140


def test_joint_c1_reaches_eight_and_equals_marginal_at_112():
    rows = {row["prediction_cap"]: row for row in DOC["summaries"]}
    assert (rows[40]["C1_marginal_pass"], rows[40]["C1_joint_pass"]) == (2, 0)
    assert (rows[80]["C1_marginal_pass"], rows[80]["C1_joint_pass"]) == (6, 4)
    assert (rows[112]["C1_marginal_pass"], rows[112]["C1_joint_pass"]) == (8, 8)
    assert rows[112]["A_and_K_total"] == 1150
    assert rows[112]["binding_A"] == 18


def test_only_two_16_tag_seeds_clear():
    rows = [row for row in DOC["rows"]
            if row["prediction_cap"] == 112 and row["C1_joint_pass"]]
    got = {row["seed"]: (row["block"], row["C1_joint"]) for row in rows
           if row["block"] != "larger-28"}
    assert got == {
        20630103: ("current-16", 60),
        20650104: ("fresh-16", 63),
    }
    failed = [row for row in DOC["rows"]
              if row["prediction_cap"] == 112
              and row["block"] != "larger-28" and not row["C1_joint_pass"]]
    assert len(failed) == 10
    assert max(row["C1_joint"] for row in failed) == 59


def test_larger_28_clears_all_six():
    rows = [row for row in DOC["rows"]
            if row["prediction_cap"] == 112 and row["block"] == "larger-28"]
    assert all(row["C1_joint_pass"] for row in rows)
    assert min(row["C1_joint"] for row in rows) == 60


def test_blocks_report_the_split():
    blocks = {row["label"]: row for row in DOC["by_block"]}
    assert (blocks["current-16"]["112"]["A"],
            blocks["current-16"]["112"]["A_and_K"],
            blocks["current-16"]["112"]["C1_joint_pass"]) == (345, 345, 1)
    assert (blocks["fresh-16"]["112"]["A"],
            blocks["fresh-16"]["112"]["A_and_K"],
            blocks["fresh-16"]["112"]["C1_joint_pass"]) == (346, 346, 1)
    assert (blocks["larger-28"]["112"]["A"],
            blocks["larger-28"]["112"]["A_and_K"],
            blocks["larger-28"]["112"]["C1_joint_pass"]) == (578, 459, 6)


def test_a_tampered_joint_pass_is_reported():
    bad = copy.deepcopy(DOC)
    row = next(row for row in bad["rows"] if row["prediction_cap"] == 112)
    row["A_and_K"] += 1

    assert pc.problems(bad), "a joint ceiling inconsistent with A∩K must fail"


def test_page_is_current():
    assert pc.PAGE_PATH.read_text(encoding="utf-8") == pc.render(DOC)
    text = pc.PAGE_PATH.read_text(encoding="utf-8")
    assert "2/12" in text
    assert "8/18" in text
    assert "6/6" in text
