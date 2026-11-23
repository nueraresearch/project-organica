"""The 0/6 viability finding, priced. The numbers must reconcile and the levers must stay closed.

Two things can go wrong here and both are quiet. The screen can stop matching the baseline (so the
per-seed counts drift), or the prose can start promising a lever that the arithmetic does not support —
for instance if a future block happened to contain no row lacking both paths, which would make
"weakening C2" viable and the verdict false. Both are checked against the source artifacts.
"""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

from benchmarks import a1_viability_levers as levers

DOCS = Path(__file__).resolve().parents[1] / "docs"


def baseline() -> dict[int, dict[str, tuple[bool, bool]]]:
    doc = json.loads((DOCS / "a1_baseline_availability_adopted.json").read_text(encoding="utf-8"))
    return {int(group["seed"]): {row["edge"]: (bool(row["A"]), bool(row["K"]))
                                 for row in group["rows"]}
            for group in doc["per_seed"]}


def test_the_artifact_and_page_are_their_build() -> None:
    assert levers.problems() == []
    record = json.loads(levers.OUT.read_text(encoding="utf-8"))
    expected = levers.engine_stamp.stamp(levers.build())
    assert record["runner"] == "__main__"
    assert {k: v for k, v in record.items() if k != "runner"} == {
        k: v for k, v in expected.items() if k != "runner"
    }
    assert levers.PAGE.read_text(encoding="utf-8").strip() == levers.render(levers.build()).strip()


def test_the_screen_reconciles_per_seed() -> None:
    flags = baseline()
    for row in levers.build()["seeds"]:
        n20 = row["n20"]
        selected = levers._selected(levers.UNFILTERED_N20, row["seed"])
        missing_a = [edge for edge in selected if not flags[row["seed"]][edge][0]]
        missing_k = [edge for edge in selected if not flags[row["seed"]][edge][1]]
        assert n20["missing_a"] == len(missing_a)
        assert n20["missing_k"] == len(missing_k)
        assert n20["neither"] == len(set(missing_a) & set(missing_k))
        assert n20["viable"] == len(selected) - len(set(missing_a) | set(missing_k))
        assert n20["either_one"] == len(selected) - n20["neither"]


def test_the_finding_is_still_a_finding() -> None:
    totals = levers.build()["totals"]
    assert totals["seeds_n20_viable"] == 0
    assert totals["n20_viable"] < totals["n20_rows"]
    assert totals["neither"] > 0, "if no row lacked both paths, weakening C2 would be a lever"


def test_the_filtered_block_is_viable_by_construction() -> None:
    flags = baseline()
    doc = json.loads(levers.FILTERED.read_text(encoding="utf-8"))
    checked = 0
    for seed, group in doc["per_seed"].items():
        for edge in group["selected"]:
            a, k = flags[int(seed)][edge]
            assert a and k, (seed, edge)
            checked += 1
    assert checked == levers.build()["totals"]["filtered_rows"] == 115


def test_raising_n_cannot_help() -> None:
    for row in levers.build()["seeds"]:
        draws = row["draw"]
        assert draws["4"] >= draws["17"] >= draws["20"]


def test_a_doctored_page_fails() -> None:
    text = levers.PAGE.read_text(encoding="utf-8")
    doctored = text.replace("| `20740101` | 20 | 7 | 6 |", "| `20740101` | 20 | 6 | 6 |", 1)
    assert doctored != text
    assert levers.problems(doctored)


def test_a_doctored_artifact_fails() -> None:
    doc = levers.build()
    doc["totals"]["neither"] = 0
    assert levers.problems(levers.PAGE.read_text(encoding="utf-8"), doc)
