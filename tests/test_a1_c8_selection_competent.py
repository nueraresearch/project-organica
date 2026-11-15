"""The competent selection is a claim about three artifacts, and it is recomputed here.

`docs/a1_c8_target_selection_competent.json` forms the block a freeze act would carry under the
competence contract.  Every figure in it is derivable — which edges are competent from the
baseline artifact, which are eligible from the universe artifact, the block from an exact
search, and C1's denominator from a fold over the recorded flags — so the file is checked
rather than trusted.

One test exists to keep a mistake out of the corpus.  An earlier audit asserted that C1's
denominator had to be re-measured once targets became competent rows.  It does not: C1 counts
every recorded row, targets included, so the denominator is a property of the universe and the
competent selection reproduces it exactly.  That invariance is pinned here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from benchmarks import a1_c8_target_selection_competent as module

LAYER = "static"

DOCS = Path(__file__).resolve().parents[1] / "docs"
ARTIFACT = DOCS / "a1_c8_target_selection_competent.json"
BASELINE = DOCS / "a1_baseline_availability_adopted.json"
ESTIMAND = DOCS / "DECISION-A1-COMPETENT-ESTIMAND.md"

SIZES = [20, 17, 20, 20, 18, 20]


def _doc() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _baseline() -> dict[int, dict[str, tuple[bool, bool]]]:
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    return {int(record["seed"]): {row["edge"]: (bool(row["A"]), bool(row["K"]))
                                  for row in record["rows"]}
            for record in data["per_seed"]}


def test_the_sizes_are_the_ones_the_estimand_decision_fixes() -> None:
    """The artifact and the pending decision must not disagree on the block."""
    assert _doc()["sizes"] == SIZES
    text = ESTIMAND.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("| Target rows |"):
            cells = [cell.strip().strip("*") for cell in line.split("|")[2:-2]]
            assert [int(cell) for cell in cells] == SIZES
            return
    raise AssertionError("the estimand decision lost its Target rows table")


def test_every_selected_edge_is_baseline_competent() -> None:
    flags = _baseline()
    for seed, block in _doc()["per_seed"].items():
        for edge in block["selected"]:
            a, k = flags[int(seed)][edge]
            assert a and k, (seed, edge, a, k)


def test_the_endpoint_cap_and_uniqueness_hold() -> None:
    for seed, block in _doc()["per_seed"].items():
        selected = block["selected"]
        assert len(selected) == len(set(selected)), seed
        assert block["endpoint_degree"] == module._endpoint_degrees(selected)
        assert max(block["endpoint_degree"].values()) <= 3, seed
        assert len(selected) >= 17, seed


def test_no_size_above_a_block_is_left_undecided() -> None:
    """Every block is the largest that exists, not the largest one was found.

    `20740105` was reported as undecided at 19 and 20 under a four-million-node budget.  The
    search was re-run with a budget large enough to finish (26.1M and 14.7M nodes), so the
    whole block is now exhaustive and no seed carries a "not found" standing in for a ceiling.
    """
    doc = _doc()
    for seed, block in doc["per_seed"].items():
        assert block["undecided_sizes"] == [], seed
        searched = {item["n"]: item for item in block["searches"]}
        for need in range(len(block["selected"]) + 1, 21):
            assert searched[need]["exhausted"] is True, (seed, need)
            assert searched[need]["feasible"] is False, (seed, need)
    assert doc["sizes"] == SIZES
    pool = module._competent(module._eligible(*module._universe(20740105)),
                             _baseline()[20740105])
    assert module._witness(pool, 18)["feasible"] is True


def test_the_small_block_is_small_because_eighteen_is_impossible() -> None:
    """Re-derives the frontier that the earlier measurement reported, from the pool."""
    flags = _baseline()
    universe = {seed: module._universe(seed) for seed in module.SEEDS}
    pool = module._competent(module._eligible(*universe[20740102]), flags[20740102])
    block = _doc()["per_seed"]["20740102"]
    assert block["competent_pool"] == len(pool)
    assert len(block["selected"]) == 17
    assert module._witness(pool, 18)["exhausted"] is True, "18 must be exhausted, not undecided"
    assert module._witness(pool, 17)["feasible"] is True


def test_c1s_denominator_is_invariant_to_the_target_selection() -> None:
    """C1 counts every recorded row, so the target set cannot change it.

    This is the correction of an audit error: the denominator was asserted to need
    re-measuring once targets were drawn from competent rows.  It is the same number, and the
    competent artifact reproduces every one of them.
    """
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    competent = _doc()
    for record in baseline["per_seed"]:
        seed = str(record["seed"])
        assert record["rows"] and record["candidate_rows"] == len(record["rows"]), \
            "C1's stream is the whole universe, targets included"
        a_minus = sum(1 for row in record["rows"] if row["K"])
        k_minus = sum(1 for row in record["rows"] if row["A"])
        assert (a_minus, k_minus) == (record["c1_a_minus_denominator"],
                                      record["c1_k_minus_denominator"])
        assert min(a_minus, k_minus) == record["c1_min_denominator"]
        assert competent["per_seed"][seed]["c1"]["c1_min_denominator"] == \
            record["c1_min_denominator"]

    text = ESTIMAND.read_text(encoding="utf-8")
    assert "does not move" in text
    assert "must be re-derived from the competent selection" not in text


def test_the_c1_table_in_the_page_matches_the_artifact() -> None:
    page = (DOCS / "A1-C8-TARGET-SELECTION-COMPETENT.md").read_text(encoding="utf-8")
    minima = [int(match) for match in re.findall(r"\| \*\*(\d+)\*\* \|$", page, re.M)]
    artifact = [record["c1"]["c1_min_denominator"]
                for record in _doc()["per_seed"].values()]
    assert minima[-len(artifact):] == artifact


def test_the_artifact_checker_can_fail() -> None:
    """A guard nobody has watched reject anything is not a guard."""
    doc = json.loads(json.dumps(_doc()))
    seed = str(module.SEEDS[1])
    flags = _baseline()[module.SEEDS[1]]
    non_competent = next(edge for edge, (a, k) in sorted(flags.items())
                         if not (a and k) and edge.count(">") == 1)
    doc["per_seed"][seed]["selected"][0] = non_competent
    assert module.problems(doc), "a non-competent target was accepted"

    doc = json.loads(json.dumps(_doc()))
    doc["per_seed"][seed]["undecided_sizes"] = [20, 19]
    doc["per_seed"][seed]["searches"] = [{"n": 20, "feasible": True, "exhausted": False,
                                          "nodes": 1}]
    assert module.problems(doc), "a feasible larger size was accepted next to a short block"
