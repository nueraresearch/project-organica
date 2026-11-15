"""Fill a freeze act's S2 selection record from the artifact the constructor wrote.

`DECISION-A1-C8-SELECTION` S2 asks a freeze act to record the competent pool, the selected block
and the constructor's identity before any cell runs. Typing those into the act would be a
transcription, and transcription is how this repository's tables have drifted before. So the act's
`s2-fields` block is generated from the selection artifact and the constructor's own bytes, with
`--check` failing when the act and its sources disagree.

The N=20 act is derived; the N=4 act is not. Its block is not produced by the competence
constructor, so its rows stay `NOT RECORDED` — stated by this module rather than implied.

    python -m benchmarks.a1_freeze_fields --write
    python -m benchmarks.a1_freeze_fields --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACT = ROOT / "docs" / "A1-TARGET-FREEZE-ACT-N20.md"
ARTIFACT = ROOT / "docs" / "a1_c8_target_selection_competent.json"
CONSTRUCTOR = ROOT / "benchmarks" / "a1_c8_target_selection_competent.py"

START = "<!-- s2-fields:start -->"
END = "<!-- s2-fields:end -->"

# Fields this act can derive; anything else stays unrecorded and blocks the signature.
DISCLOSURE = "no S5 disclosure document exists yet"


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _seeds(document: dict) -> list[str]:
    return sorted(document["per_seed"])


def pool_sizes(document: dict) -> dict[str, int]:
    """The pool's size per seed — all the artifact states.

    It records the count (`competent_pool`) but not the members: `competent` is a per-edge flag over
    the selected block, not the pool. A digest over the wrong list would look like provenance and be
    worthless, so the pool digest is reported as unrecorded, with that reason.
    """
    return {seed: document["per_seed"][seed]["competent_pool"] for seed in _seeds(document)}


def block(document: dict) -> dict[str, list[str]]:
    return {seed: list(document["per_seed"][seed]["selected"]) for seed in _seeds(document)}


def _canonical(rows: dict[str, list[str]]) -> str:
    return "\n".join("%s:%s" % (seed, ",".join(rows[seed])) for seed in sorted(rows))


def fields(document: dict | None = None) -> list[tuple[str, str, str]]:
    """(field, what the act must contain, state) — the state is the second half of S2's answer."""
    document = document if document is not None else json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sizes_by_seed = pool_sizes(document)
    blocks = block(document)
    counts = [sizes_by_seed[seed] for seed in _seeds(document)]
    sizes = [len(blocks[seed]) for seed in _seeds(document)]
    total = sum(counts)
    return [
        ("Act ID", "`A1-TARGET-FREEZE-ACT-N20`", "`RECORDED`"),
        ("Competent pool per seed",
         "%s (%d rows in total)" % (", ".join(str(n) for n in counts), total), "`RECORDED`"),
        ("Competent pool digest",
         "the artifact records the pool's size, not its members", "`NOT RECORDED`"),
        ("Selected block per seed", ", ".join(str(n) for n in sizes), "`RECORDED`"),
        ("Selected block digest", "`%s`" % _digest(_canonical(blocks)), "`RECORDED`"),
        ("Row count per seed",
         ", ".join("%d→%d" % (counts[i], sizes[i]) for i in range(len(counts))), "`RECORDED`"),
        ("Constructor identity",
         "`benchmarks/a1_c8_target_selection_competent.py`, source sha256 `%s`"
         % _file_digest(CONSTRUCTOR), "`RECORDED`"),
        ("Constructor output digest",
         "`%s`, sha256 `%s`" % (ARTIFACT.name, _file_digest(ARTIFACT)), "`RECORDED`"),
        ("Competence predicate", "`DECISION-A1-C8-NMIN`, its *Unit* row", "`FIXED BY RECORD`"),
        ("Unfiltered selection", DISCLOSURE, "`NOT RECORDED`"),
    ]


def render(document: dict | None = None) -> str:
    document = document if document is not None else json.loads(ARTIFACT.read_text(encoding="utf-8"))
    lines = ["| Field | What it must contain | State |", "| --- | --- | --- |"]
    for name, value, state in fields(document):
        lines.append("| %s | %s | %s |" % (name, value, state))
    return "\n".join(lines)


def span(text: str) -> tuple[int, int]:
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("the act does not carry exactly one s2-fields block")
    left, right = text.index(START) + len(START), text.index(END)
    if right < left:
        raise ValueError("the s2-fields markers are out of order")
    return left, right


def committed(text: str) -> str:
    left, right = span(text)
    return text[left:right].strip("\n")


def problems(text: str | None = None) -> list[str]:
    text = text if text is not None else ACT.read_text(encoding="utf-8")
    found: list[str] = []
    try:
        current = committed(text)
    except ValueError as error:
        return [str(error)]
    if current != render():
        found.append("the act's S2 fields are stale against the selection artifact")
    missing = [name for name, _, _ in fields()
               if ("| %s |" % name) not in current]
    if missing:
        found.append("the act is missing fields: %s" % ", ".join(missing))
    if "not signable while any row above reads `NOT RECORDED`" not in text:
        found.append("the act no longer says a blank row withholds the signature")
    return found


def write() -> int:
    text = ACT.read_text(encoding="utf-8")
    left, right = span(text)
    updated = text[:left] + "\n" + render() + "\n" + text[right:]
    ACT.write_text(updated, encoding="utf-8")
    recorded = sum(1 for _, _, state in fields() if state != "`NOT RECORDED`")
    print("wrote %s: %d of %d fields recorded" % (ACT.name, recorded, len(fields())))
    print("  blocked on: %s" % ", ".join(name for name, _, state in fields()
                                        if state == "`NOT RECORDED`"))
    return 0


def check() -> int:
    found = problems()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    recorded = sum(1 for _, _, state in fields() if state != "`NOT RECORDED`")
    print("A1 freeze fields: clean; %d of %d rows recorded, %d blocking the signature"
          % (recorded, len(fields()), len(fields()) - recorded))
    print("  the N=4 act is not derived: its block is not produced by the competence constructor")
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
