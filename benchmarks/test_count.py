"""Record the test count from a real suite run and write it into the documents.

AGENTS.md said "250 tests" long after the suite had passed four times that, and
nothing failed, because a hand-typed count is a number with no source. This
module gives it a source: the count is measured by running the suite, stored in
``docs/test_count.json``, and substituted into a marked region of each document.

``--check`` is the gate. It fails when a document disagrees with the record, and
it also fails when the record disagrees with a fresh collection of the suite --
so adding a test without re-running the recorder leaves the count stale and the
gate red, instead of leaving a number that quietly describes an older suite.

Nothing is written in ``--check`` mode: a gate that regenerates before judging
would pass a stale count every time.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "test_count.json"
TARGETS = (ROOT / "AGENTS.md", ROOT / "docs" / "USER-MANUAL.md")

MARK_START = "<!-- tests:auto -->"
MARK_END = "<!-- /tests:auto -->"

COMMAND = [sys.executable, "-m", "pytest", "tests", "-q"]
COLLECT_COMMAND = [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q"]


def _run(args, timeout=900):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)


def parse_summary(text):
    """Read pytest's summary counts out of its output, without assuming a layout."""
    counts = {}
    for name in ("passed", "skipped", "failed", "error", "errors", "xfailed", "xpassed"):
        match = re.search(r"(\d+) " + name + r"\b", text)
        if match:
            counts[name] = int(match.group(1))
    return counts


def collect_count():
    """How many tests the suite currently contains, by collection rather than by run."""
    proc = _run(COLLECT_COMMAND, timeout=300)
    match = re.search(r"(\d+) tests? collected", proc.stdout)
    if not match:
        raise RuntimeError("could not read the collection count:\n" + proc.stdout[-2000:])
    return int(match.group(1))


def run_suite():
    """Run the whole suite and return the record its result justifies."""
    proc = _run(COMMAND)
    counts = parse_summary(proc.stdout + proc.stderr)
    return {
        "command": "python -m pytest tests -q",
        "date": date.today().isoformat(),
        "exit_code": proc.returncode,
        "collected": collect_count(),
        "passed": counts.get("passed", 0),
        "skipped": counts.get("skipped", 0),
        "failed": counts.get("failed", 0) + counts.get("error", 0) + counts.get("errors", 0),
    }


def render_fragment(record):
    """The one sentence a document may say about the test count."""
    return "%d passed, %d skipped, %d failed of %d collected (%s)" % (
        record["passed"],
        record["skipped"],
        record["failed"],
        record["collected"],
        record["date"],
    )


def region_of(text):
    """Return the current contents of the single marked region."""
    if text.count(MARK_START) != 1 or text.count(MARK_END) != 1:
        raise ValueError("expected exactly one %s ... %s region" % (MARK_START, MARK_END))
    start = text.index(MARK_START) + len(MARK_START)
    end = text.index(MARK_END)
    if end < start:
        raise ValueError("the test-count markers are out of order")
    return text[start:end]


def with_fragment(text, fragment):
    """Replace the marked region, leaving every other character alone."""
    region_of(text)
    start = text.index(MARK_START) + len(MARK_START)
    end = text.index(MARK_END)
    return text[:start] + fragment + text[end:]


def load_record():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def problems(record, live=None):
    """Everything wrong with the published count, as a list of sentences."""
    found = []
    if live is None:
        try:
            live = collect_count()
        except (RuntimeError, subprocess.SubprocessError) as exc:
            return ["could not collect the suite: %s" % exc]
    if live != record.get("collected"):
        found.append(
            "the record says %d collected but the suite collects %d; run python -m benchmarks.test_count"
            % (record.get("collected"), live)
        )
    fragment = render_fragment(record)
    for path in TARGETS:
        if not path.exists():
            found.append("%s does not exist" % path.name)
            continue
        text = path.read_text(encoding="utf-8")
        try:
            current = region_of(text)
        except ValueError as exc:
            found.append("%s: %s" % (path.name, exc))
            continue
        if current != fragment:
            found.append("%s states a stale test count; run python -m benchmarks.test_count" % path.name)
    return found


def write(record):
    ARTIFACT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    fragment = render_fragment(record)
    for path in TARGETS:
        path.write_text(with_fragment(path.read_text(encoding="utf-8"), fragment), encoding="utf-8")
    return fragment


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the recorded count against the documents and a fresh collection, without writing",
    )
    args = parser.parse_args(argv)

    if args.check:
        found = problems(load_record())
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("test count:", render_fragment(load_record()))
        return 0

    record = run_suite()
    if record["exit_code"] != 0:
        print(
            "FAIL: the suite is not green (%d failed of %d collected); nothing written"
            % (record["failed"], record["collected"])
        )
        return 1
    print("test count:", write(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
