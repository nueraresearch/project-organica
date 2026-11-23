"""Generate the N=20 freeze act's target sets and scorer pin from their sources.

The act has to state, before any cell runs, exactly which edges are frozen and exactly which code will
turn their cells into a verdict. Both were previously transcribed by hand — the edge lists from a
selection artifact, the module identities from memory — and transcription is how this tree's tables
have drifted before.

Two generated blocks, each rewritten in place and checked for staleness:

* `s2-block` — the per-seed target sets and the summary row for each seed, read from the competent
  selection artifact and the adopted baseline;
* `s2-scorers` — the SHA-256 of the two modules that produce the verdict, read from
  `benchmarks/a1_scorer_pin.py`'s pin.

    python -m benchmarks.a1_act_blocks --write
    python -m benchmarks.a1_act_blocks --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

ACT = DOCS / "A1-TARGET-FREEZE-ACT-N20.md"
ARTIFACT = DOCS / "a1_c8_target_selection_competent.json"
BASELINE = DOCS / "a1_baseline_availability_adopted.json"

BLOCK_START = "<!-- s2-block:start -->"
BLOCK_END = "<!-- s2-block:end -->"
SCORER_START = "<!-- s2-scorers:start -->"
SCORER_END = "<!-- s2-scorers:end -->"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_block() -> str:
    document = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    base = {int(group["seed"]): group
            for group in json.loads(BASELINE.read_text(encoding="utf-8"))["per_seed"]}
    lines: list[str] = []
    rows = []
    for seed in sorted(document["per_seed"]):
        row = document["per_seed"][seed]
        selected = list(row["selected"])
        rows.append((seed, selected, row, base[int(seed)]))
    for seed, selected, row, baseline in rows:
        lines += [
            "### Seed `%s` — %d rows" % (seed, len(selected)),
            "",
            "**All %d, in selection order:** %s"
            % (len(selected), ", ".join("`%s`" % edge for edge in selected)),
        ]
        if len(selected) < 20:
            lines += [
                "",
                "*%d rows, not 20: the constructor finds no 20-row block for this seed at the endpoint cap, and "
                "`N_min = 17` is the adopted floor. Its verdict at this size: `%s`.*"
                % (len(selected), row.get("verdict", "FORMS")),
            ]
        lines.append("")
    lines += [
        "| Seed | Candidates | C1 cell min | Competent pool | Block | Max degree | Selection digest |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for seed, selected, row, baseline in rows:
        lines.append("| `%s` | %d | %d | %d | %d | %d | `%s` |"
                     % (seed, baseline["candidate_rows"], baseline["c1_min_denominator"],
                        len(row["competent_edges"]), len(selected),
                        int(row.get("cap") or document.get("cap") or 3),
                        row["selection_digest"]))
    total = sum(len(selected) for _, selected, _, _ in rows)
    unique = len({edge for _, selected, _, _ in rows for edge in selected})
    lines += [
        "",
        "**Target observations:** %d. **Unique target edges:** %d. **Selection artifact digest (SHA-256):** `%s`"
        % (total, unique, _digest(ARTIFACT)),
    ]
    return "\n".join(lines)


def render_scorers() -> str:
    from benchmarks import a1_scorer_pin
    lines = ["| Module | sha256 |", "| --- | --- |"]
    for name, digest in a1_scorer_pin.table():
        lines.append("| `%s` | `%s` |" % (name, digest))
    lines += [
        "",
        "`a1_result.assemble` refuses to assemble a verdict when either digest differs from the pin recorded in "
        "`docs/a1_scorer_pin.json`; `python -m benchmarks.a1_scorer_pin --check` runs in the suite. Re-pinning is "
        "allowed and is a commit somebody reviews — the requirement is that the scorer cannot move unseen.",
    ]
    return "\n".join(lines)


def _swap(text: str, start: str, end: str, body: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError("the act must carry exactly one %s/%s pair" % (start, end))
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return head + start + "\n" + body.strip() + "\n" + end + tail


def refreshed(text: str | None = None) -> str:
    text = text if text is not None else ACT.read_text(encoding="utf-8")
    text = _swap(text, BLOCK_START, BLOCK_END, render_block())
    return _swap(text, SCORER_START, SCORER_END, render_scorers())


def problems() -> list[str]:
    text = ACT.read_text(encoding="utf-8")
    found = []
    for start, end, name in ((BLOCK_START, BLOCK_END, "target sets"),
                             (SCORER_START, SCORER_END, "scorer pin")):
        if text.count(start) != 1 or text.count(end) != 1:
            found.append("the act does not carry exactly one %s block" % name)
    if found:
        return found
    if refreshed(text) != text:
        found.append("the act's generated blocks are stale against their sources")
    return found


def write() -> int:
    ACT.write_text(refreshed(), encoding="utf-8")
    print("wrote %s: %d target rows, scorer pin" % (ACT.name,
                                                    sum(len(row["selected"])
                                                        for row in json.loads(
                                                            ARTIFACT.read_text(encoding="utf-8"))["per_seed"].values())))
    return 0


def check() -> int:
    found = problems()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 act blocks: clean; target sets and scorer pin match their sources")
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
