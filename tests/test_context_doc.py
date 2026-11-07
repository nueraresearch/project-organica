"""docs/CONTEXT.md is a register of provenance, so every row must stay labelled.

The document exists because three kinds of fact were being carried in conversation:
owner capacity, audience, and the not-claimed list. A row whose marker drifts, or a
"would be licensed by" cell pointing at nothing, would turn testimony back into an
unlabelled assertion — which is the failure the document was written to prevent.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "CONTEXT.md"
MARKERS = ("`repo`", "`owner-reported`", "`unknown`")


def text() -> str:
    return DOC.read_text(encoding="utf-8")


def tables() -> list[tuple[list[str], list[list[str]]]]:
    lines = text().splitlines()
    found: list[tuple[list[str], list[list[str]]]] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        looks_like_header = stripped.startswith("|") and i + 1 < len(lines) and set(
            lines[i + 1].strip().replace("|", "").replace(" ", "")
        ) <= set("-:")
        if looks_like_header:
            header = [cell.strip() for cell in stripped.strip("|").split("|")]
            rows: list[list[str]] = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append([cell.strip() for cell in lines[j].strip().strip("|").split("|")])
                j += 1
            found.append((header, rows))
            i = j
        else:
            i += 1
    return found


def test_document_exists_and_declares_its_markers() -> None:
    assert DOC.exists()
    body = text()
    for marker in MARKERS:
        assert marker in body, marker


def test_every_provenance_row_carries_exactly_one_marker() -> None:
    checked = 0
    for header, rows in tables():
        if "Provenance" not in header:
            continue
        column = header.index("Provenance")
        for row in rows:
            cell = row[column]
            starts = [marker for marker in MARKERS if cell.startswith(marker)]
            assert len(starts) == 1, (row[0], cell)
            checked += 1
    assert checked >= 20, checked


def test_the_unknown_rows_are_present_and_named() -> None:
    body = text()
    assert body.count("`unknown`") >= 6, body.count("`unknown`")
    for fact in ("Hours available per week", "Machine the studies run on", "Funding received"):
        assert fact in body, fact


def test_stage_b_compute_figure_agrees_with_the_artifact() -> None:
    estimate = json.loads((ROOT / "docs" / "stage_b_cost_estimate.json").read_text(encoding="utf-8"))
    hours = estimate["cycles_total"] * estimate["measured_seconds_per_cycle"]["mean"] / 3600
    assert f"about {round(hours)} hours" in text().lower(), round(hours)


def test_every_not_claimed_row_names_something_that_can_settle_it() -> None:
    seen = False
    for header, rows in tables():
        if not any("Not claimed" in cell for cell in header):
            continue
        seen = True
        assert len(rows) >= 10, len(rows)
        for row in rows:
            licence = row[-2]
            paths = re.findall(r"`((?:docs|papers)/[^`]+)`", licence)
            questions = re.findall(r"\bQ0\d\d\b", licence)
            assert paths or questions, row[0]
            for path in paths:
                assert (ROOT / path).exists(), path
    assert seen


def test_outreach_points_at_this_register() -> None:
    outreach = (ROOT / "docs" / "OUTREACH.md").read_text(encoding="utf-8")
    assert "CONTEXT.md" in outreach
