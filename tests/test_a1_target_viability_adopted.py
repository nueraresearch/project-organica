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
