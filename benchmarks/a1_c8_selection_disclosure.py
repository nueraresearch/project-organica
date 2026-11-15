"""Write the S5 disclosure: the unfiltered selection beside the competent one.

`DECISION-A1-C8-SELECTION` S5 asks that the unfiltered selection be reported beside the filtered
block, so the filter's effect is visible rather than baked in. The numbers here are generated from
the two committed artifacts; the paragraph that says what they mean is written once, in this module,
and reviewed as prose — because the table cannot say whether a filter ran before or after a run.

The table deliberately does **not** present a subtraction. The two blocks are selected from
different candidate pools, so the filtered block is not the unfiltered block minus some rows: it
shares a handful of edges and contributes a dozen the unfiltered rule never chose. A "dropped" column
would be a true count of a false relation.

    python -m benchmarks.a1_c8_selection_disclosure --write
    python -m benchmarks.a1_c8_selection_disclosure --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PARENT = ROOT / "docs" / "a1_c8_target_selection.json"
FILTERED = ROOT / "docs" / "a1_c8_target_selection_competent.json"
PAGE = ROOT / "docs" / "A1-C8-SELECTION-DISCLOSURE.md"
DOCS = ROOT / "docs"
ACT = DOCS / "A1-TARGET-FREEZE-ACT-N20.md"

# The timing claim is not argued from timestamps. It holds because no cell has run at all, and these
# are the two places that say so: the act's own status line, and the absence of any grant or run record
# for A1. When one of those changes, the sentence needs a human read, so the check fails.
UNSIGNED = "AWAITING THE OWNER'S SIGNATURE"
NOT_RUN = "NOT FROZEN, NO GRANT, NO RUN"
RECORD_MARKERS = ("GRANT", "AUTHORIS", "RUN", "RESULT", "CELLS")

STATUS = "DISCLOSURE — NOT A RESULT; S5 RECORD FOR THE FREEZE ACT; NOTHING FROZEN, NOTHING RUN"

TIMING = (
    "**The filter ran before any cell.** The competence predicate was applied to the no-arm baseline, the block was "
    "constructed from the resulting pool, and both artifacts were written before any arm was run. No outcome was "
    "observed when the excluded rows were excluded, so the exclusions are a design decision and not a correction."
)

READING = (
    "**This is not a subtraction, and reading it as one would be wrong.** The unfiltered block and the filtered block "
    "come from different candidate pools, so the filtered block is not the unfiltered block with rows removed: it keeps a "
    "few of the same edges and adds edges the unfiltered rule never chose, while the unfiltered block contains edges that "
    "are competent but were not selected. The three right-hand columns separate those cases; a single \"dropped\" figure "
    "would merge an exclusion with a substitution."
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _seeds(document: dict) -> list[str]:
    return sorted(document["per_seed"])


def rows(parent: dict, filtered: dict) -> list[dict]:
    found = []
    for seed in _seeds(filtered):
        unfiltered = set(parent["per_seed"][seed]["selected"])
        chosen = set(filtered["per_seed"][seed]["selected"])
        pool = set(filtered["per_seed"][seed]["competent_edges"])
        excluded = unfiltered - chosen
        found.append({
            "seed": seed,
            "unfiltered": len(unfiltered),
            "filtered": len(chosen),
            "shared": len(unfiltered & chosen),
            "excluded_incompetent": len([edge for edge in excluded if edge not in pool]),
            "excluded_not_chosen": len([edge for edge in excluded if edge in pool]),
            "added": len(chosen - unfiltered),
        })
    return found


def totals(table: list[dict]) -> dict:
    keys = ("unfiltered", "filtered", "shared", "excluded_incompetent", "excluded_not_chosen", "added")
    return {key: sum(row[key] for row in table) for key in keys}


def evidence(act: Path = ACT, docs: Path = DOCS) -> list[str]:
    """Grounds for "the filter ran before any cell": an unsigned act and no grant or run on record."""
    if not act.exists():
        return ["the freeze act is missing, so the timing claim has no standing"]
    text = act.read_text(encoding="utf-8")
    found = []
    if UNSIGNED not in text:
        found.append("the act no longer says %r" % UNSIGNED)
    if NOT_RUN not in text:
        found.append("the act no longer says %r" % NOT_RUN)
    for path in sorted(docs.iterdir()):
        name = path.name.upper()
        if not (name.startswith("A1-") or name.startswith("A1_")):
            continue
        if any(marker in name for marker in RECORD_MARKERS):
            found.append("%s exists: a grant or a run would date the filter, and the timing claim must be "
                         "re-read rather than asserted" % path.name)
    return found


def render(parent: dict | None = None, filtered: dict | None = None) -> str:
    parent = parent if parent is not None else json.loads(PARENT.read_text(encoding="utf-8"))
    filtered = filtered if filtered is not None else json.loads(FILTERED.read_text(encoding="utf-8"))
    table = rows(parent, filtered)
    total = totals(table)
    grounds = evidence()
    mark = "❌" if grounds else "✅"
    lines = [
        "# C8 selection — the unfiltered block beside the competent one",
        "",
        "**ID:** `A1-C8-SELECTION-DISCLOSURE-1`  ",
        "**Date:** %s  " % filtered["date"],
        "**Status:** `%s`" % STATUS,
        "",
        "**This is not an experimental result.** No arm cell ran; no manifest was frozen; nothing is granted.",
        "",
        "## What this record is for",
        "",
        "`DECISION-A1-C8-SELECTION` S5 requires the unfiltered selection to be reported beside the filtered block. The "
        "unfiltered selection is [`%s`](%s) — the published rule applied to the same seeds without the competence "
        "predicate. The filtered block is [`%s`](%s). Every number below is generated from those two files."
        % (parent["id"], PARENT.name, filtered["id"], FILTERED.name),
        "",
        TIMING,
        "",
        "## The two selections, side by side",
        "",
        "| Seed | Unfiltered block | Filtered block | Shared edges | Excluded: not competent | Excluded: competent, not chosen | Added: not in the unfiltered block |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in table:
        lines.append("| `%s` | %d | %d | %d | %d | %d | %d |"
                     % (row["seed"], row["unfiltered"], row["filtered"], row["shared"],
                        row["excluded_incompetent"], row["excluded_not_chosen"], row["added"]))
    lines.append("| **total** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** |"
                 % (total["unfiltered"], total["filtered"], total["shared"],
                    total["excluded_incompetent"], total["excluded_not_chosen"], total["added"]))
    lines += [
        "",
        READING,
        "",
        "## Grounds for the timing claim",
        "",
        "The claim above is not argued from timestamps, which a reader cannot audit. It is argued from the fact that "
        "**no cell has run at all**:",
        "",
        "- %s the freeze act reads `%s` and `%s`" % (mark, UNSIGNED, NOT_RUN),
        "- %s no grant, authorisation, run or result record for A1 exists under `docs/`" % mark,
    ]
    if grounds:
        lines += ["", "**The claim does not currently hold:**", ""]
        lines += ["- " + ground for ground in grounds]
    lines += [
        "",
        "`--check` verifies both, and fails when either stops holding — a signed act, a grant, or a run record — "
        "because at that point this paragraph needs a person to reread it rather than a generator to keep it in date.",
        "",
        "## What this record does and does not show",
        "",
        "- **Shown:** which edges the unfiltered rule chose, which the competent construction chose, how many they share, "
        "and how the exclusions divide between rows that fail the predicate and rows that pass it but were not selected.",
        "- **Shown:** that the filter was applied to the baseline, in artifacts written before any cell ran.",
        "- **Not shown:** any treatment effect. There is none to show: no cell has run.",
        "- **Not shown:** whether the filtered block is the *only* block the construction could have chosen. The "
        "constructor's search is recorded in its own artifact, not here.",
        "",
        "## Provenance",
        "",
        "| Artifact | ID | sha256 |",
        "| --- | --- | --- |",
        "| [`%s`](%s) | `%s` | `%s` |" % (PARENT.name, PARENT.name, parent["id"], _digest(PARENT)),
        "| [`%s`](%s) | `%s` | `%s` |" % (FILTERED.name, FILTERED.name, filtered["id"], _digest(FILTERED)),
        "",
        "_Generated by `python -m benchmarks.a1_c8_selection_disclosure --write`; `--check` fails when this page and "
        "either artifact disagree. The two paragraphs above the tables are the only hand-written text, and they are "
        "checked for their presence, not their argument._",
        "",
    ]
    return "\n".join(lines)


def problems(text: str | None = None) -> list[str]:
    text = text if text is not None else (PAGE.read_text(encoding="utf-8") if PAGE.exists() else "")
    if not text:
        return ["the disclosure page is missing"]
    found: list[str] = []
    if text != render():
        found.append("the page is stale against its source artifacts")
    if TIMING not in text:
        found.append("the page no longer says the filter ran before any cell")
    if READING not in text:
        found.append("the page no longer warns that the table is not a subtraction")
    found.extend(evidence())
    return found


def write() -> int:
    PAGE.write_text(render(), encoding="utf-8")
    table = rows(json.loads(PARENT.read_text(encoding="utf-8")),
                 json.loads(FILTERED.read_text(encoding="utf-8")))
    total = totals(table)
    print("wrote %s" % PAGE.name)
    print("  shared %d, excluded (not competent) %d, excluded (not chosen) %d, added %d"
          % (total["shared"], total["excluded_incompetent"],
             total["excluded_not_chosen"], total["added"]))
    return 0


def check() -> int:
    found = problems()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 C8 disclosure: clean; %d seeds, no cell run" % len(rows(
        json.loads(PARENT.read_text(encoding="utf-8")),
        json.loads(FILTERED.read_text(encoding="utf-8")))))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    sys.exit(main())
