"""At a 120-loop window, A must be the C1 binding path on every seed."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json
from pathlib import Path

from benchmarks import a1_c1_cap120 as c1

DOC = json.loads(Path("docs/a1_c1_cap120.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert c1.problems(DOC) == []
    assert c1.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["rows"]) == 36


def test_cap_120_moves_the_binding_path_from_k_to_a():
    rows = {row["cap"]: row for row in DOC["summaries"]}
    assert (rows[15]["A_total"], rows[15]["K_total"], rows[15]["C1_pass"]) == (
        913, 714, 0)
    assert (rows[15]["binding_A"], rows[15]["binding_K"],
            rows[15]["binding_both"]) == (1, 16, 1)
    assert (rows[120]["A_total"], rows[120]["K_total"], rows[120]["C1_pass"]) == (
        913, 1498, 2)
    assert (rows[120]["binding_A"], rows[120]["binding_K"],
            rows[120]["binding_both"]) == (18, 0, 0)
    assert (rows[120]["A_and_K_total"], rows[120]["C1_joint_pass"]) == (842, 0)
    assert (rows[120]["C1_joint_min"], rows[120]["C1_joint_max"]) == (31, 58)


def test_blocks_show_a_becoming_the_floor():
    blocks = {row["label"]: row for row in DOC["by_block"]}
    for label, low, high in (
            ("current-16", (281, 228, 31, 44), (382, 43, 52, 0)),
            ("fresh-16", (279, 242, 31, 46), (383, 31, 54, 0)),
            ("larger-28", (353, 244, 23, 55), (733, 50, 67, 2))):
        assert (
            blocks[label]["15"]["A"], blocks[label]["15"]["K"],
            blocks[label]["15"]["C1_ceiling_min"],
            blocks[label]["15"]["C1_ceiling_max"],
        ) == low
        assert (
            blocks[label]["120"]["K"],
            blocks[label]["120"]["C1_ceiling_min"],
            blocks[label]["120"]["C1_ceiling_max"],
            blocks[label]["120"]["C1_pass"],
        ) == high


def test_every_cap_120_seed_is_a_bound():
    rows = [row for row in DOC["rows"] if row["cap"] == 120]
    assert len(rows) == 18
    assert all(row["binding"] == "A" for row in rows)
    assert all(row["A"] == row["C1_ceiling"] for row in rows)
    assert [row["C1_ceiling"] for row in rows] == [
        44, 44, 52, 43, 49, 49,
        49, 46, 54, 53, 31, 46,
        59, 50, 57, 67, 66, 54,
    ]
    assert sum(row["C1_floor_pass"] for row in rows) == 2


def test_a_is_unchanged_by_the_loop_cap():
    by_seed = {}
    for row in DOC["rows"]:
        by_seed.setdefault((row["block"], row["seed"]), {})[row["cap"]] = row
    assert all(values[15]["A"] == values[120]["A"]
               for values in by_seed.values())


def test_a_tampered_binding_is_reported():
    bad = copy.deepcopy(DOC)
    row = next(row for row in bad["rows"] if row["cap"] == 120)
    row["binding"] = "K"

    assert c1.problems(bad), "a wrong binding path must fail"


def test_page_is_current():
    assert c1.PAGE_PATH.read_text(encoding="utf-8") == c1.render(DOC)
    text = c1.PAGE_PATH.read_text(encoding="utf-8")
    assert "A is the C1 binding path on every seed" in text
    assert "2/18" in text
    assert "0/18" in text
    assert "31-67" in text
    assert "31-58" in text
