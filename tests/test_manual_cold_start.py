"""
tests/test_manual_cold_start.py
------------------------------------------------------------------
Keep the manual's cold-start table from drifting away from the artifact
it is supposed to describe.

The manual's §8.1 table was hand-transcribed from `docs/cold_start.json`,
and on 2026-10-30 a verification pass found that its `cold_start` row no
longer reproduced: the artifact said G5 never appeared, every retrievable
engine said cycle 10. The table had been correct when written and had
quietly stopped being correct when the artifact was superseded.

**The fix is not a careful read.** A table transcribed by hand is a new
claim every time it is edited, and a reader cannot tell a stale cell from
a fresh one. This test derives every cell from the artifact and compares
it to the manual, so a drift fails the suite instead of shipping.

The mapping is the manual's own: G1 is reported as a range over the three
G1 primitives, G2 counts only `processes` (the column is `G2 proc`), and
the remaining columns are named for one population each.

**The test proves it can fail.** `test_check_detects_a_deliberate_drift`
mutates a copy of the derived table and asserts the comparison reports it;
a checker that cannot fail is decoration.

Run:  python -m pytest tests/test_manual_cold_start.py -v
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MANUAL = ROOT / "docs" / "USER-MANUAL.md"
ARTIFACT = ROOT / "docs" / "cold_start.json"

SECTION_START = "### 8.1 The cold-start study"
SECTION_END = "### 8.2"

#: Manual column -> artifact key. G1 is special: it is a range.
COLUMNS = (
    ("G2 proc", "G2 processes"),
    ("G3", "G3 workflows"),
    ("G4", "G4 hypotheses"),
    ("G5", "G5 theories"),
    ("G6", "G6 dreams"),
    ("G7", "G7 investigations"),
    ("G8", "G8 experiments"),
)

#: The manual's condition order, and the identifier each row names.
CONDITIONS = (
    "baseline",
    "no_branch",
    "cold_start",
    "cold_start_unbranched",
    "real_git_history",
    "no_truncation",
    "no_dev_stopwords",
    "wide_lookback",
)


def _manual_text() -> str:
    return MANUAL.read_text(encoding="utf-8")


def section() -> str:
    text = _manual_text()
    start = text.find(SECTION_START)
    assert start != -1, f"{SECTION_START!r} is missing from the manual"
    end = text.find(SECTION_END, start)
    assert end != -1, f"{SECTION_END!r} is missing after §8.1"
    return text[start:end]


def table_rows() -> list[list[str]]:
    """The condition rows of the §8.1 table, as lists of cells."""
    rows = []
    for line in section().splitlines():
        line = line.strip()
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def _label_condition(label: str) -> str:
    names = re.findall(r"`([a-z_]+)`", label)
    assert names, f"no condition name in the row label {label!r}"
    return names[0]


def _first(condition: dict, key: str) -> str:
    value = condition["cycles_to_first_emergence"].get(key)
    return "never" if value is None else str(value)


def _g1_range(condition: dict) -> str:
    values = [v for k, v in condition["cycles_to_first_emergence"].items()
              if k.startswith("G1 ")]
    if not values:
        return "never"
    lo, hi = min(values), max(values)
    return str(lo) if lo == hi else f"{lo}\u2013{hi}"


def derive(artifact: dict) -> dict[str, list[str]]:
    """The table the manual should contain, from the artifact alone."""
    by_name = {c["condition"]: c for c in artifact["conditions"]}
    out = {}
    for name in CONDITIONS:
        condition = by_name[name]
        row = [_g1_range(condition)] + [_first(condition, key) for _, key in COLUMNS]
        out[name] = row
    return out


def mismatches(manual_rows: list[list[str]], expected: dict[str, list[str]]) -> list[str]:
    """Every disagreement between the manual's rows and the artifact's."""
    problems = []
    seen = []
    for cells in manual_rows:
        label = cells[0]
        name = _label_condition(label)
        seen.append(name)
        if name not in expected:
            problems.append(f"{name}: row present in the manual, absent from the artifact")
            continue
        if len(cells) != 9:
            problems.append(f"{name}: {len(cells)} cells, expected 9")
            continue
        got = [c.replace("**", "") for c in cells[1:]]
        want = expected[name]
        for column, g, w in zip(("G1",) + tuple(c for c, _ in COLUMNS), got, want):
            if g != w:
                problems.append(f"{name}.{column}: manual {g!r} != artifact {w!r}")
    if sorted(seen) != sorted(expected):
        missing = sorted(set(expected) - set(seen))
        if missing:
            problems.append(f"conditions missing from the manual table: {missing}")
    return problems


def test_table_matches_the_artifact():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    problems = mismatches(table_rows(), derive(artifact))
    assert not problems, "the §8.1 table has drifted from docs/cold_start.json:\n  " + \
        "\n  ".join(problems)


def test_every_condition_has_a_row():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rows = table_rows()
    assert len(rows) == len(CONDITIONS), (
        f"the §8.1 table has {len(rows)} condition rows, expected {len(CONDITIONS)}")
    assert sorted(_label_condition(r[0]) for r in rows) == sorted(CONDITIONS)


def test_the_correction_is_recorded():
    """The re-measurement must be disclosed, not applied silently."""
    text = _manual_text()
    log_start = text.find("**Revision log:**")
    assert log_start != -1, "the manual has no revision log"
    log = text[log_start:]
    assert "2026-10-30" in log, "no 2026-10-30 entry in the revision log"
    assert "cold-start table was re-measured" in log, (
        "the revision log does not name the cold-start re-measurement")
    assert "no longer reproduces" in log, (
        "the revision log does not disclose that the old table no longer reproduces")


def test_check_detects_a_deliberate_drift():
    """Proof that the checker can fail: mutate a derived row and catch it."""
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = derive(artifact)
    rows = table_rows()

    # A silent edit to one cell must be visible.
    mutated = [row[:] for row in rows]
    for row in mutated:
        if _label_condition(row[0]) == "cold_start":
            row[5] = "never"  # the value the 2026-10-21 table carried
    assert mismatches(mutated, expected), (
        "the checker accepted a mutated cold_start row -- it cannot fail")

    # A dropped row must be visible.
    assert mismatches(rows[:-1], expected), (
        "the checker accepted a missing condition row -- it cannot fail")


def test_artifact_and_manual_are_not_empty():
    """Guard against a silent parse failure masquerading as a pass."""
    assert len(table_rows()) >= 8
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert len(artifact["conditions"]) >= 8
