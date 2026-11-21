"""Pin the code that turns A1 cells into a verdict, before any cell runs.

Every other campaign in this tree froze its analysis path before cells: a registered scoring module,
named in the protocol, so the criteria could not be computed by a version of the code chosen after the
data existed. A1 adopted its gates but never pinned the two modules that apply them, which left one way
for a reading to change after the fact — edit the scorer, re-score, and the gate moves while the cells
stay the same.

This module records the SHA-256 of the gate module (`a1_arms`) and the assembler (`a1_result`) in
`docs/a1_scorer_pin.json`, and `a1_result.assemble` refuses to score when either file differs from its
pin. A deliberate change is still possible: re-pin with `--write`, which is a commit somebody reviews.

    python -m benchmarks.a1_scorer_pin --write
    python -m benchmarks.a1_scorer_pin --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]

PIN = ROOT / "docs" / "a1_scorer_pin.json"
MODULES = (ROOT / "benchmarks" / "a1_arms.py", ROOT / "benchmarks" / "a1_result.py")

ID = "A1-SCORER-PIN-1"
DATE = "2026-11-15"
STATUS = "PINNED — THE VERDICT-PRODUCING CODE IS FIXED BEFORE ANY CELL; RE-PINNING IS A REVIEWED COMMIT"
RULE = (
    "`a1_result.assemble` refuses to score when either module's content differs from the digest recorded "
    "here. Re-pinning is allowed and is a commit: the point is that the scorer cannot change without the "
    "change being visible in at least one reviewable place."
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    return {
        "kind": "a1_scorer_pin",
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "rule": RULE,
        "modules": {str(path.relative_to(ROOT)): _digest(path) for path in MODULES},
    }


def verify(doc: dict | None = None) -> list[str]:
    """Problems with the pin, as a list. Empty means the scorer is the one that was frozen."""
    doc = doc if doc is not None else (json.loads(PIN.read_text(encoding="utf-8")) if PIN.exists() else None)
    if doc is None:
        return ["the scorer pin is missing"]
    found = []
    recorded = doc.get("modules") or {}
    for path in MODULES:
        name = str(path.relative_to(ROOT))
        if name not in recorded:
            found.append("%s is not pinned" % name)
        elif recorded[name] != _digest(path):
            found.append("%s differs from its pin: scoring is not authorised with this code" % name)
    for name in recorded:
        if not (ROOT / name).exists():
            found.append("%s is pinned but missing" % name)
    return found


def table() -> list[tuple[str, str]]:
    return [(str(path.relative_to(ROOT)), _digest(path)) for path in MODULES]


def write() -> int:
    PIN.write_text(json.dumps(engine_stamp.stamp(build()), indent=2) + "\n", encoding="utf-8")
    print("pinned %d modules in %s" % (len(MODULES), PIN.name))
    for name, digest in table():
        print("  %s %s" % (name, digest))
    return 0


def check() -> int:
    found = verify()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 scorer pin: clean; %d modules pinned" % len(MODULES))
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
