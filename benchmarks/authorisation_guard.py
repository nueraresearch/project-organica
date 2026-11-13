"""Preflight guard against preparation-only authorisation quotes.

A record may be `FROZEN, RUN`, but its recorded quote must be the owner's run
authorisation, not an instruction to prepare the document or record the grant.
The guard is deliberately conservative: preparation-only means at least one
preparation marker and no run/authorise/execute marker.  A quote such as
"Preregister and run ..." is therefore a run authorisation, while "Write the
dated authorisation document ..." is not.

    python -m benchmarks.authorisation_guard --check
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PREPARATION_MARKERS = (
    "without running",
    "before running",
    "write the dated",
    "prepare the dated",
    "recording the owner's grant",
    "record its grant",
    "record the owner's grant",
)
RUN_MARKER = re.compile(r"\b(run|runs|rerun|authorize|authorise|execute)\b", re.I)


def preparation_only(quote: str | None) -> bool:
    """True when the quote is preparation language and carries no run words."""
    if not quote:
        return False
    text = " ".join(str(quote).lower().split())
    has_preparation = any(marker in text for marker in PREPARATION_MARKERS)
    return has_preparation and not RUN_MARKER.search(text)


def problems(body: dict) -> list[str]:
    """Reject a FROZEN, RUN record whose only quote is preparation-only."""
    if body.get("status") != "FROZEN, RUN":
        return []
    quote = (body.get("authorisation") or {}).get("quote")
    if preparation_only(quote):
        return ["FROZEN, RUN record cites a preparation-only authorisation quote: %r"
                % quote]
    return []


def scan(root: Path = ROOT) -> list[tuple[str, str]]:
    """Every docs record that fails the guard, as (relative path, reason)."""
    found: list[tuple[str, str]] = []
    for path in sorted((root / "docs").glob("*.json")):
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(body, dict):
            continue
        for reason in problems(body):
            found.append((path.relative_to(root).as_posix(), reason))
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True,
                        help="scan docs records and exit 1 on a violation")
    parser.parse_args(argv)
    violations = scan()
    if not violations:
        print("authorisation guard: clean")
        return 0
    for path, reason in violations:
        print("%s: %s" % (path, reason))
    print("authorisation guard: %d violation(s)" % len(violations))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
