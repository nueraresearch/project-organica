"""The adopted-block viability table is a claim about two committed artifacts.

`docs/A1-TARGET-VIABILITY-ADOPTED.md` states a count per seed for two target designs.  Every one of
those numbers is derived from `a1_baseline_availability_adopted.json` and a selection artifact, so the
table is checked mechanically rather than trusted: a transcription that drifts from the artifacts is a
new claim about the world, and this one decides whether two freeze acts can be signed.
"""

from __future__ import annotations

import json
from pathlib import Path

LAYER = "static"

DOCS = Path(__file__).resolve().parents[1] / "docs"
DOC = DOCS / "A1-TARGET-VIABILITY-ADOPTED.md"
BASELINE = DOCS / "a1_baseline_availability_adopted.json"
DESIGNS = {
    "N4": DOCS / "a1_target_selection.json",
    "N20": DOCS / "a1_c8_target_selection.json",
}


def _rows() -> dict[str, dict[str, dict]]:
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    return {str(record["seed"]): {row["edge"]: row for row in record["rows"]}
            for record in base["per_seed"]}


def _counts() -> dict[str, dict[str, tuple[int, int, int]]]:
    rows = _rows()
    out: dict[str, dict[str, tuple[int, int, int]]] = {}
    for design, path in DESIGNS.items():
        selection = json.loads(path.read_text(encoding="utf-8"))
        per_seed: dict[str, tuple[int, int, int]] = {}
        for seed, block in selection["per_seed"].items():
            targets = block["selected"]
            stream = rows[str(seed)]
            per_seed[str(seed)] = (
                len(targets),
                sum(1 for edge in targets if not stream[edge]["A"]),
                sum(1 for edge in targets if not stream[edge]["K"]),
            )
        out[design] = per_seed
    return out


def _doc_row(design: str, seed: str, text: str) -> str:
    marker = f"| {design} | `{seed}` |"
    for line in text.splitlines():
        if line.startswith(marker):
            return line
    raise AssertionError(f"no table row for {design} {seed}")


def _doc_total(design: str, text: str) -> str:
    marker = f"| **{design} total** |"
    for line in text.splitlines():
        if line.startswith(marker):
            return line
    raise AssertionError(f"no total row for {design}")


def _assert_table_matches(text: str, counts: dict) -> None:
    for design, per_seed in counts.items():
        targets_total = missing_a_total = missing_k_total = 0
        for seed, (targets, missing_a, missing_k) in per_seed.items():
            row = _doc_row(design, seed, text)
            cells = [cell.strip() for cell in row.split("|")]
            assert cells[3] == str(targets), (design, seed, "targets", cells[3], targets)
            assert cells[4] == str(missing_a), (design, seed, "no A carrier", cells[4], missing_a)
            assert cells[5] == str(missing_k), (design, seed, "no K served", cells[5], missing_k)
            targets_total += targets
            missing_a_total += missing_a
            missing_k_total += missing_k
        # The total row is bold; the numbers inside it are still plain counts.
        total = [cell.strip().strip("*") for cell in _doc_total(design, text).split("|")]
        assert total[3] == str(targets_total), (design, "total targets", total[3], targets_total)
        assert total[4] == str(missing_a_total), (design, "total no A", total[4], missing_a_total)
        assert total[5] == str(missing_k_total), (design, "total no K", total[5], missing_k_total)


def test_every_viability_figure_matches_the_adopted_artifacts() -> None:
    _assert_table_matches(DOC.read_text(encoding="utf-8"), _counts())


def test_the_viability_checker_can_fail() -> None:
    """A guard nobody has seen reject anything is not a guard."""
    text = DOC.read_text(encoding="utf-8")
    drifted = text.replace("| N20 | `20740102` | 20 | 4 | 11 | NO |",
                           "| N20 | `20740102` | 20 | 5 | 11 | NO |", 1)
    assert drifted != text, "the control row is missing; the checker would be vacuous"
    try:
        _assert_table_matches(drifted, _counts())
    except AssertionError:
        return
    raise AssertionError("a drifted count passed the viability check")


def _competent_pool(seed: int) -> list[str]:
    """The protocol's eligible universe screened to both baseline paths."""
    import importlib

    module = importlib.import_module("benchmarks.a1_competence_filter_draft")
    availability = module._load(module.AVAILABILITY_PATH)
    universe = module._load(module.N4_PATH)
    flags = {row["edge"]: (bool(row["A"]), bool(row["K"]))
             for record in availability["per_seed"] if int(record["seed"]) == seed
             for row in record["rows"]}
    block = (universe.get("per_seed") or {})[str(seed)]
    u, members = block["u"], block["cycle_member"]
    return [edge for edge in sorted(u)
            if int((u.get(edge) or {}).get("strength") or 0) > 0
            and members.get(edge) is True
            and flags.get(edge, (False, False))[0]
            and flags.get(edge, (False, False))[1]]


def _feasible(pool: list[str], need: int, cap: int = 3, budget: int = 4_000_000) -> bool:
    """Exactly: is there a ``need``-subset with every tag's degree at most ``cap``?"""
    total = len(pool)
    nodes = 0

    def choose(start: int, degree: dict[str, int], taken: int) -> bool:
        nonlocal nodes
        nodes += 1
        if nodes > budget:
            raise TimeoutError("node budget exhausted")
        if taken == need:
            return True
        if total - start < need - taken:
            return False
        for index in range(start, total):
            left, right = pool[index].split(">")
            if degree.get(left, 0) >= cap or degree.get(right, 0) >= cap:
                continue
            degree[left] = degree.get(left, 0) + 1
            degree[right] = degree.get(right, 0) + 1
            if choose(index + 1, degree, taken + 1):
                return True
            degree[left] -= 1
            degree[right] -= 1
            if not degree[left]:
                del degree[left]
            if not degree[right]:
                del degree[right]
        return False

    return choose(0, {}, 0)


def test_a_competent_block_of_seventeen_exists_on_every_seed() -> None:
    """C8's adopted floor is the frontier: 17 forms everywhere, 18 already fails on one seed."""
    for seed in (20740101, 20740102, 20740103, 20740104, 20740105, 20740106):
        pool = _competent_pool(seed)
        assert _feasible(pool, 17), seed

    narrow = _competent_pool(20740102)
    assert not _feasible(narrow, 18), "18 was recorded as impossible on 20740102"
    assert not _feasible(narrow, 20), "20 was recorded as impossible on 20740102"


def _decision_table_row(label: str, text: str) -> list[int]:
    for line in text.splitlines():
        if line.startswith("| %s |" % label):
            return [int(cell.strip().strip("*").replace(",", ""))
                    for cell in line.split("|")[2:-1]]
    raise AssertionError("no row labelled %r" % label)


def test_the_estimand_decision_restates_c4_multiplicity_correctly() -> None:
    """The record's C4 table is arithmetic on the baseline; a drift here would restate an adopted clause."""
    doc = (DOCS / "DECISION-A1-COMPETENT-ESTIMAND.md").read_text(encoding="utf-8")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    rows = [record["candidate_rows"] for record in baseline["per_seed"]]

    sizes = _decision_table_row("Target rows", doc)[:-1]
    non_target = _decision_table_row("Non-target rows", doc)[:-1]
    deltas = _decision_table_row("Deltas (×3 paths)", doc)[:-1]

    assert non_target == [total - size for total, size in zip(rows, sizes)]
    assert deltas == [value * 3 for value in non_target]
    assert _decision_table_row("Target rows", doc)[-1] == sum(sizes)
    assert _decision_table_row("Non-target rows", doc)[-1] == sum(non_target)
    assert _decision_table_row("Deltas (×3 paths)", doc)[-1] == sum(deltas)

    # The sizes are C8's adopted operative block sizes, not a new choice made here.
    c8 = (DOCS / "DECISION-A1-C8-NMIN.md").read_text(encoding="utf-8")
    assert ", ".join(str(size) for size in sizes) in c8


def test_the_frontier_moves_with_the_endpoint_cap() -> None:
    """17 is not corroborated twice: the cap decides whether it binds."""
    narrow = _competent_pool(20740102)
    assert not _feasible(narrow, 17, cap=2), "cap 2 was recorded as failing 17 on 20740102"
    assert _feasible(narrow, 20, cap=4), "cap 4 was recorded as taking 20 on 20740102"
