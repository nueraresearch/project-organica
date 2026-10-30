"""Tests that every document restating the Pilot-0 readout matches its artifact.

Why this file exists
--------------------
On 2026-10-29 a review found that the 10-cell score matrix in
``docs/PILOT-0-INSTRUMENTATION-AUDIT.md`` had been **transcribed by hand**
from ``docs/acquisition_single_seed_pilot.json``, and that **18 of its 36
values** disagreed with that artifact in the fourth and fifth decimal of
log-loss.  The artifact never changed; the transcription did.

The generalisable rule is the one recorded in the audit's own section 2.1:

    **a table transcribed from an artifact is a new claim, and it needs a
    mechanical check against that artifact.**

These tests are that mechanical check, run by ``pytest`` so the drift cannot
reappear unnoticed.  They read the artifact and the documents, compare them,
and fail on any disagreement.

Discipline (mirrors AGENTS.md):

  * The check must be able to FAIL.  ``test_check_detects_a_deliberate_drift``
    feeds the checker a deliberately corrupted table and asserts that the
    checker reports it.  A check that cannot disagree with its subject is not
    a check.
  * Standard library only.
  * No engine files are read or written; this is a documentation check.
"""
from __future__ import annotations

import io
import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ART = REPO / "docs" / "acquisition_single_seed_pilot.json"
AUDIT = REPO / "docs" / "PILOT-0-INSTRUMENTATION-AUDIT.md"

COLS = ("retention", "transfer", "revision")

# The documents that restate the readout as a five-row learner table.  The
# audit carries the full 10-cell matrix, and the facts sheet states it in
# prose (AC7) — each of those has its own check below.
SUMMARY_DOCS = [
    "docs/ACQUISITION-ENDPOINT-AUDIT.md",
    "docs/ORGANICA-V2-DESIGN-BRIEF.md",
    "papers/01_developmental_structure_formation.md",
    "research-journal/phase_g_findings_20261021.md",
    "research-journal/_journal_entry_51.md",
]

# The values that the transcription carried before the correction.  They are
# listed here so that a reappearance of any of them anywhere in the repository
# is a test failure.  This file is excluded from its own scan below, because it
# necessarily contains them.
STALE = [
    "0.453912", "0.463372", "0.453842", "0.463321", "0.428071",
    "0.427814", "0.272365", "0.275176", "0.409511", "0.406124",
]


# ---------------------------------------------------------------------------
# Artifact
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def truth():
    """The Pilot-0 readout, read from the artifact."""
    data = json.loads(io.open(ART, encoding="utf-8").read())
    cells = {}
    for key, cell in data["cells"].items():
        n = int(key.split("_")[1])
        s = cell["scores"]
        # Organica's cells name the middle column "transfer_diagnostic";
        # the baselines name it "transfer".
        mid = s["transfer"] if "transfer" in s else s["transfer_diagnostic"]
        cells[n] = {
            "retention": float(s["retention"]["house_shape"]["log_loss"]),
            "transfer": float(mid["house_shape"]["log_loss"]),
            "revision": float(s["revision"]["house_shape"]["log_loss"]),
        }
    refs = {}
    for name, key in (("bayes ceiling", "bayes_ceiling"), ("base rate", "base_rate")):
        r = data["references"][key]
        refs[name] = {c: float(r[c]["house_shape"]["log_loss"]) for c in COLS}
    return {"cells": cells, "refs": refs}


def read(path: Path) -> str:
    return io.open(path, encoding="utf-8").read()


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

CELL_ROW = re.compile(
    r"^\|\s*\*\*(\d+)\*\*\s*\|.*?\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|"
)
REF_ROW = re.compile(
    r"^\|\s*\*Ref\*\s*\|\s*\*([\w ]+?)\*\s*\|.*?\|\s*\*([\d.]+)\*\s*\|"
    r"\s*\*([\d.]+)\*\s*\|\s*\*([\d.]+)\*\s*\|"
)
LEARNER_ROW = re.compile(
    r"^\|\s*\**([\w ]+?)\**\s*\|\s*\**([\d.]+)\**\s*\|\s*\**([\d.]+)\**\s*\|"
    r"\s*\**([\d.]+)\**\s*\|"
)


def parse_matrix(text: str):
    """Parse the audit's 10-cell matrix and its two reference rows."""
    cells, refs = [], []
    for i, line in enumerate(text.split("\n"), 1):
        m = CELL_ROW.match(line)
        if m:
            cells.append({
                "line": i,
                "cell": int(m.group(1)),
                "vals": {
                    "retention": float(m.group(2)),
                    "transfer": float(m.group(3)),
                    "revision": float(m.group(4)),
                },
            })
            continue
        m = REF_ROW.match(line)
        if m:
            refs.append({
                "line": i,
                "name": m.group(1).strip().lower(),
                "vals": {
                    "retention": float(m.group(2)),
                    "transfer": float(m.group(3)),
                    "revision": float(m.group(4)),
                },
            })
    return cells, refs


def parse_summary(text: str):
    """Parse a five-row learner summary table into {learner: {col: value}}."""
    out = {}
    for line in text.split("\n"):
        m = LEARNER_ROW.match(line)
        if not m:
            continue
        name = m.group(1).strip().lower()
        if name not in ("organica", "replay", "statistical", "base rate", "bayes ceiling"):
            continue
        out[name] = {
            "retention": float(m.group(2)),
            "transfer": float(m.group(3)),
            "revision": float(m.group(4)),
        }
    return out


def check_matrix(text: str, truth) -> list:
    """Return a list of problems in the audit's matrix.  Empty means clean."""
    problems = []
    cells, refs = parse_matrix(text)
    seen = {}
    for row in cells:
        seen.setdefault(row["cell"], []).append(row["line"])
        want = truth["cells"].get(row["cell"])
        if want is None:
            problems.append(f"line {row['line']}: unknown cell {row['cell']}")
            continue
        for col in COLS:
            if abs(row["vals"][col] - want[col]) > 1e-9:
                problems.append(
                    f"line {row['line']}: cell {row['cell']} {col} is "
                    f"{row['vals'][col]!r}, artifact says {want[col]!r}"
                )
    for cell, lines in seen.items():
        if len(lines) > 1:
            problems.append(f"cell {cell} appears on lines {lines} (duplicate row)")
    missing = sorted(set(truth["cells"]) - set(seen))
    if missing:
        problems.append(f"cells missing from the matrix: {missing}")
    ref_seen = {}
    for row in refs:
        ref_seen[row["name"]] = row["line"]
        want = truth["refs"].get(row["name"])
        if want is None:
            problems.append(f"line {row['line']}: unknown reference row {row['name']!r}")
            continue
        for col in COLS:
            if abs(row["vals"][col] - want[col]) > 1e-9:
                problems.append(
                    f"line {row['line']}: {row['name']} {col} is "
                    f"{row['vals'][col]!r}, artifact says {want[col]!r}"
                )
    for name in truth["refs"]:
        if name not in ref_seen:
            problems.append(f"reference row {name!r} is missing from the matrix")
    return problems


def check_summary(text: str, truth) -> list:
    """Return a list of problems in a five-row learner summary."""
    problems = []
    rows = parse_summary(text)
    if not rows:
        return ["no learner summary table found"]
    want = {
        "organica": truth["cells"][1],
        "replay": truth["cells"][7],
        "statistical": truth["cells"][9],
        "base rate": truth["refs"]["base rate"],
        "bayes ceiling": truth["refs"]["bayes ceiling"],
    }
    for name, expect in want.items():
        got = rows.get(name)
        if got is None:
            problems.append(f"summary row {name!r} is missing")
            continue
        for col in COLS:
            if abs(got[col] - expect[col]) > 1e-9:
                problems.append(
                    f"summary row {name!r} {col} is {got[col]!r}, "
                    f"artifact says {expect[col]!r}"
                )
    return problems


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAuditMatrix:
    def test_matrix_matches_the_artifact(self, truth):
        problems = check_matrix(read(AUDIT), truth)
        assert not problems, "the Pilot-0 matrix has drifted from its artifact:\n" + "\n".join(problems)

    def test_matrix_has_ten_cells_and_two_reference_rows(self, truth):
        cells, refs = parse_matrix(read(AUDIT))
        assert len(cells) == 10, f"expected 10 cell rows, found {len(cells)}"
        assert len(refs) == 2, f"expected 2 reference rows, found {len(refs)}"

    def test_correction_is_recorded(self):
        """The drift and its correction must stay on the record, not vanish."""
        text = read(AUDIT)
        assert "transcription drift" in text.lower()
        assert "18 of its 36 values" in text, "the recorded count of drifted values is wrong"
        assert "6.7\\times10^{-5}" in text, "the recorded maximum disagreement is wrong"
        assert "mechanical check against that artifact" in text


class TestSummaryTables:
    @pytest.mark.parametrize("rel", SUMMARY_DOCS)
    def test_summary_matches_the_artifact(self, rel, truth):
        path = REPO / rel
        if not path.exists():
            pytest.skip(f"{rel} not present")
        problems = check_summary(read(path), truth)
        assert not problems, f"{rel} has drifted from the artifact:\n" + "\n".join(problems)

    def test_facts_sheet_readout_is_artifact_authoritative(self, truth):
        """AC7 states the readout in prose, so it needs its own check."""
        text = read(REPO / "docs" / "FACTS-SHEET.md")
        rows = parse_summary(text.replace("**", ""))
        # AC7 is a prose sentence, not a table; check the triples it states.
        triples = re.findall(
            r"(?:\*\*)?(Organica|Replay|Statistical|base rate|Bayes ceiling)(?:\*\*)?"
            r"[^0-9]{0,12}\*\*?([\d.]+) / ([\d.]+) / ([\d.]+)",
            text,
        )
        assert triples, "AC7's readout statement was not found"
        for name, r, t, v in triples:
            key = name.lower()
            if key == "organica":
                want = truth["cells"][1]
            elif key == "replay":
                want = truth["cells"][7]
            elif key == "statistical":
                want = truth["cells"][9]
            else:
                want = truth["refs"][key]
            for col, got in (("retention", r), ("transfer", t), ("revision", v)):
                assert abs(float(got) - want[col]) <= 1e-9, (
                    f"AC7 {key} {col} is {got}, artifact says {want[col]}"
                )


class TestNoStaleReadout:
    def test_no_stale_literal_survives_in_the_repository(self):
        """No tracked text file may still carry a pre-correction value."""
        pattern = re.compile(
            r"(?<![\d.])(?:" + "|".join(re.escape(s) for s in STALE) + r")(?![\d])"
        )
        this_file = Path(__file__).resolve()
        offenders = []
        files = subprocess.check_output(
            ["git", "-C", str(REPO), "ls-files"], text=True, encoding="utf-8"
        ).split("\n")
        for rel in files:
            rel = rel.strip()
            if not rel or rel.startswith(("logs/", "snapshots/")):
                continue
            path = REPO / rel
            if not path.exists() or path.resolve() == this_file:
                continue
            if path.suffix.lower() not in (".md", ".json", ".py", ".txt", ".cff"):
                continue
            try:
                text = io.open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for i, line in enumerate(text.split("\n"), 1):
                if pattern.search(line):
                    offenders.append(f"{rel}:{i}: {line.strip()[:120]}")
        assert not offenders, (
            "a pre-correction readout value survives in:\n" + "\n".join(offenders)
        )


class TestTheCheckCanFail:
    """A check that cannot disagree with its subject is not a check."""

    def test_check_detects_a_deliberate_drift(self, truth):
        clean = read(AUDIT)
        assert check_matrix(clean, truth) == [], "the checker is not clean on clean input"

        drifted = clean.replace("0.453886", "0.453912", 1)
        problems = check_matrix(drifted, truth)
        assert problems, "the checker failed to notice a single drifted value"
        assert any("transfer" in p for p in problems)

    def test_check_detects_a_duplicated_row(self, truth):
        clean = read(AUDIT)
        duplicated = clean.replace(
            "| **10** | `E-rem` | Statistical | 0.403045 | 0.403045 | 0.403045 |",
            "| **10** | `E-rem` | Statistical | 0.403045 | 0.403045 | 0.403045 |\n"
            "| **10** | `E-rem` | Statistical | 0.403045 | 0.403045 | 0.403045 |",
            1,
        )
        problems = check_matrix(duplicated, truth)
        assert any("duplicate row" in p for p in problems), problems

    def test_check_detects_a_dropped_reference_row(self, truth):
        clean = read(AUDIT)
        dropped = "\n".join(
            line for line in clean.split("\n")
            if not line.startswith("| *Ref* | *Bayes ceiling*")
        )
        problems = check_matrix(dropped, truth)
        assert any("bayes ceiling" in p for p in problems), problems

    def test_summary_check_detects_a_drift(self, truth):
        clean = read(REPO / "docs" / "ACQUISITION-ENDPOINT-AUDIT.md")
        assert check_summary(clean, truth) == []
        drifted = clean.replace("0.347521", "0.347999", 1)
        problems = check_summary(drifted, truth)
        assert problems
