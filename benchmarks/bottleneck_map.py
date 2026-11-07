"""Render the bottleneck map's tables from `docs/bottleneck_map.json`.

Two tables in `docs/BOTTLENECK-MAP.md` restate the artifact: the candidate map in
section 2 and the label table in section 3. Both are generated here between
markers, and `tests/test_bottleneck_map.py` asserts that the committed document
is exactly what this module produces -- a hand-maintained restatement drifts,
which is what `AGENTS.md` rule 27 exists for.

The status column of the map table carries the artifact's statuses verbatim, so a
compound status reads as its two statuses joined by ` + `. The check column is
kept to one sentence per row (`MAX_CHECK_CHARS`), because a markdown table cell
cannot wrap and an over-long cell is where readability goes.

The map table also carries each row's **provenance tag**, and the paragraph beneath it is
generated from those tags rather than from a count typed beside them. The tags themselves are
validated by `benchmarks.provenance` before anything is rendered: a row whose tag its evidence
cannot back stops the write instead of reaching the page.

Regenerate with:

    python -m benchmarks.bottleneck_map --write

Standard library only; no engine file is read or written.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import provenance as prov

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "bottleneck_map.json"
DOC = ROOT / "docs" / "BOTTLENECK-MAP.md"

MAP_BEGIN = ("<!-- BEGIN MAP TABLE: generated from docs/bottleneck_map.json by "
             "benchmarks/bottleneck_map.py; do not edit by hand -->")
MAP_END = "<!-- END MAP TABLE -->"
BEGIN = ("<!-- BEGIN LABEL TABLE: generated from docs/bottleneck_map.json by "
         "benchmarks/bottleneck_map.py; do not edit by hand -->")
END = "<!-- END LABEL TABLE -->"
PROV_BEGIN = ("<!-- BEGIN PROVENANCE: generated from docs/bottleneck_map.json by "
              "benchmarks/bottleneck_map.py; do not edit by hand -->")
PROV_END = "<!-- END PROVENANCE -->"

LABEL_COLUMNS = ("| Map label | What it means | Status it maps to |", "|---|---|---|")
MAP_COLUMNS = ("| Candidate | Map label | Status | The check behind it | Provenance |",
               "|---|---|---|---|---|")

# A check cell is one sentence the reader can hold. Beyond this the row stops
# being a table and becomes a paragraph with pipes in it.
MAX_CHECK_CHARS = 400


def load_artifact(path: Path = ARTIFACT) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cell(value, where: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("%s is empty and cannot be a table cell" % where)
    if "|" in text or "\n" in text:
        raise ValueError("%s cannot be one table cell: %r" % (where, text[:60]))
    return text


def render_table(body: dict) -> str:
    """The section 3 label table, rendered from `label_meanings`."""
    lines = list(LABEL_COLUMNS)
    for label, meaning in body["label_meanings"].items():
        lines.append("| %s | %s | %s |" % (
            _cell(label, "label"),
            _cell(meaning["means"], "meaning of %r" % label),
            _cell(meaning["status"], "mapping of %r" % label),
        ))
    return "\n".join(lines)


def render_map_table(body: dict) -> str:
    """The section 2 candidate table, rendered from `rows`."""
    lines = list(MAP_COLUMNS)
    for row in body["rows"]:
        candidate = row["candidate"]
        check = _cell(row["check"], "check for %r" % candidate)
        if len(check) > MAX_CHECK_CHARS:
            raise ValueError(
                "the check for %r is %d characters, over the %d-character budget for a "
                "readable cell; shorten it in the artifact rather than in the document"
                % (candidate, len(check), MAX_CHECK_CHARS))
        lines.append("| %s | %s | %s | %s | %s |" % (
            _cell(candidate, "candidate"),
            _cell(row["label"], "label of %r" % candidate),
            _cell(" + ".join(row["status"]), "status of %r" % candidate),
            check,
            _cell(row["provenance"], "provenance of %r" % candidate),
        ))
    return "\n".join(lines)


def _replace_block(text: str, begin: str, end: str, rendered: str) -> str:
    start = text.find(begin)
    stop = text.find(end)
    if start < 0 or stop < 0 or stop < start:
        raise ValueError("the markers for %r are missing from the document" % begin[:40])
    return text[:start] + begin + "\n" + rendered + "\n" + end + text[stop + len(end):]


def render_document(text: str, body: dict) -> str:
    """Return `text` with both marked tables replaced by freshly rendered ones.

    Idempotent: rendering an already-rendered document returns it unchanged.
    Raises `ValueError` when a marker pair is missing, because a silently
    unrendered table is the failure this module exists to prevent.
    """
    findings = prov.check_map(body, ROOT)
    if findings:
        raise ValueError(
            "the artifact's provenance tags do not hold: "
            + "; ".join(f["message"] for f in findings))
    for begin, end, render in ((MAP_BEGIN, MAP_END, render_map_table),
                               (PROV_BEGIN, PROV_END, prov.render_summary),
                               (BEGIN, END, render_table)):
        text = _replace_block(text, begin, end, render(body))
    return text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="rewrite both tables in the document")
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if either table is stale")
    args = parser.parse_args(argv)

    body = load_artifact()
    text = DOC.read_text(encoding="utf-8")
    fresh = render_document(text, body)
    if args.write:
        DOC.write_text(fresh, encoding="utf-8")
        per_tag = prov.counts(body)
        print("wrote %d map rows, %d label rows and %d provenance tags into %s"
              % (len(body["rows"]), len(body["label_meanings"]), sum(per_tag.values()),
                 DOC.relative_to(ROOT)))
        return 0
    if args.check:
        if fresh != text:
            print("a table is stale: run python -m benchmarks.bottleneck_map --write")
            return 1
        print("both tables match the artifact")
        return 0
    print(render_map_table(body))
    print()
    print(prov.render_summary(body))
    print()
    print(render_table(body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
