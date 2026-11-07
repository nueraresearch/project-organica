"""Render the bottleneck map's label table from `docs/bottleneck_map.json`.

The label table in `docs/BOTTLENECK-MAP.md` section 3 restates the artifact's
`label_meanings` block, and a restatement maintained by hand drifts -- this
project has already paid for that lesson twice (`AGENTS.md` rule 27). The table
is therefore generated from the artifact between two markers, and
`tests/test_bottleneck_map.py` asserts that the committed document is exactly
what this module produces. A label added to the artifact appears in the
document only by running:

    python -m benchmarks.bottleneck_map --write

Standard library only; no engine file is read or written.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "bottleneck_map.json"
DOC = ROOT / "docs" / "BOTTLENECK-MAP.md"

BEGIN = ("<!-- BEGIN LABEL TABLE: generated from docs/bottleneck_map.json by "
         "benchmarks/bottleneck_map.py; do not edit by hand -->")
END = "<!-- END LABEL TABLE -->"

COLUMNS = ("| Map label | What it means | Status it maps to |", "|---|---|---|")


def load_artifact(path: Path = ARTIFACT) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def render_table(body: dict) -> str:
    """The label table, rendered from the artifact's `label_meanings` block."""
    lines = list(COLUMNS)
    for label, meaning in body["label_meanings"].items():
        cells = []
        for field in ("means", "status"):
            value = str(meaning[field])
            if "|" in value or "\n" in value:
                raise ValueError(
                    "label %r has a %s that cannot be a table cell" % (label, field))
            cells.append(value)
        lines.append("| %s | %s | %s |" % (label, cells[0], cells[1]))
    return "\n".join(lines)


def render_document(text: str, body: dict) -> str:
    """Return `text` with the marked label table replaced by the rendered one.

    Idempotent: rendering an already-rendered document returns it unchanged.
    Raises `ValueError` when the markers are missing, because a silently
    unrendered table is the failure this module exists to prevent.
    """
    start = text.find(BEGIN)
    end = text.find(END)
    if start < 0 or end < 0 or end < start:
        raise ValueError("the label-table markers are missing from the document")
    return (text[:start] + BEGIN + "\n" + render_table(body) + "\n" + END
            + text[end + len(END):])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="rewrite the label table in the document")
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if the document's table is stale")
    args = parser.parse_args(argv)

    body = load_artifact()
    text = DOC.read_text(encoding="utf-8")
    fresh = render_document(text, body)
    if args.write:
        DOC.write_text(fresh, encoding="utf-8")
        print("wrote %d label rows into %s"
              % (len(body["label_meanings"]), DOC.relative_to(ROOT)))
        return 0
    if args.check:
        if fresh != text:
            print("the label table is stale: run python -m benchmarks.bottleneck_map --write")
            return 1
        print("the label table matches the artifact")
        return 0
    print(render_table(body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
