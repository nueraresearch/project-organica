"""
tests/test_sleep_split_equivalence.py
------------------------------------------------------------------
The sleep-path split is a claim about behaviour, so it is checked by two runs.

`7becdb5` removed 2,400 lines from `organica/sleep.py` and added 2,313 across
`sleep_extraction`, `sleep_selection`, `sleep_synthesis`, `sleep_inquiry` and `candidates`,
plus twelve lines of covering indexes to `memory.py`. A diff cannot show that this changed nothing: a moved line
and a rewritten line look identical. So the engine is run twice -- once at the parent commit and
once at the split -- on the same stream, in separate processes, and the outputs are compared.

**What is compared.** Every field of every `SleepReport` for twelve cycles, and then every row of
every table in the substrate the run produced, with three exclusions:

* wall-clock fields (`ran_at`, the `events.time` column, and the like), which differ between any
  two runs and carry no behaviour -- including inside sleep payloads, because the marker event
  stores `ran_at` in its own JSON, so the fingerprint parses payload text and cleans it at depth;
* the `events.id` handle, which the store issues per row (a fresh id for a byte-identical payload),
  so it is an address rather than a result -- the payload's own content-derived identifiers are
  inside `content` and *are* compared;
* nothing else. Rows, counts, payloads and every structure identifier are compared.

**Isolated processes.** Each variant is extracted from git with `git archive` into its own
directory and run with that directory first on `PYTHONPATH`, so the two engines cannot share a
module cache, and `PYTHONHASHSEED=0` is pinned for both. The same stream is fed by each variant
from its own `organica/streams.py`, which the split did not touch.

**Controls, because equality is easy to fake.** `test_the_probe_is_deterministic` runs one variant
twice and requires equality, so a fingerprint that moved on its own could not pass the main test.
`test_the_probe_can_tell_two_runs_apart` changes one word of the stream and requires a different
fingerprint, so "identical" is not what the probe returns unconditionally.

**What this does not establish.** One stream, twelve cycles, the default policy. It attributes
nothing about commits after `7becdb5`; the shipped engine is not the object under test here, the
split is. Wall-clock columns are outside the comparison by construction.

Run:  python -m pytest tests/test_sleep_split_equivalence.py -v
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

#: The commit that split sleep.py, and the commit it replaced.
AFTER = "7becdb5"
BEFORE = AFTER + "^"

#: Cycles per run. Enough for concepts, predictions and the later layers to have something to do.
CYCLES = 12

DRIVER = '''"""Run one engine variant on a fixed stream and print a behaviour fingerprint."""
import dataclasses
import json
import os
import sqlite3
import sys

from organica.memory import MemoryService
from organica.sleep import SleepService
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM

CYCLES = __CYCLES__

#: Wall-clock fields. They differ between any two runs and say nothing about behaviour.
VOLATILE = {
    "ran_at", "time", "timestamp", "ts", "created_at", "updated_at", "started_at",
    "finished_at", "first_seen", "last_seen", "last_used", "wall_clock", "elapsed",
    "duration", "duration_s", "seconds", "pid", "path", "db", "db_path", "file",
}


def clean(value):
    if isinstance(value, str):
        text = value.strip()
        if text[:1] in ("{", "["):
            try:
                return json.dumps(clean(json.loads(text)), sort_keys=True)
            except ValueError:
                return value
        return value
    if isinstance(value, dict):
        return {k: clean(v) for k, v in sorted(value.items()) if k not in VOLATILE}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted(clean(v) for v in value)
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return repr(value)


def main(mode):
    database = "fingerprint.sqlite"
    if os.path.exists(database):
        os.remove(database)
    memory = MemoryService(database)
    service = SleepService(memory)

    reports = []
    for cycle in range(CYCLES):
        chunk = [STUDY_STREAM[(cycle * EVENTS_PER_CYCLE + i) % len(STUDY_STREAM)]
                 for i in range(EVENTS_PER_CYCLE)]
        if mode == "edited" and cycle == 0:
            chunk[0] = chunk[0] + " zebra"
        for text in chunk:
            memory.store(text, event_type="event", source="equivalence")
        reports.append(clean(dataclasses.asdict(service.run())))
    memory.close()

    connection = sqlite3.connect(database)
    tables = sorted(row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
    inventory = {}
    for table in tables:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(%s)" % table)]
        keep = [i for i, name in enumerate(columns)
                if name not in VOLATILE and not (table == "events" and name == "id")]
        rows = connection.execute("SELECT * FROM %s" % table).fetchall()
        inventory[table] = {
            "columns": [columns[i] for i in keep],
            "rows": sorted(json.dumps([clean(row[i]) for i in keep], sort_keys=True)
                           for row in rows),
        }
    connection.close()
    print(json.dumps({"reports": reports, "tables": inventory}, sort_keys=True))


main(sys.argv[1] if len(sys.argv) > 1 else "normal")
'''


def _git(*args):
    try:
        return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True,
                              timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None


def _commit(ref):
    out = _git("rev-parse", "--verify", ref + "^{commit}")
    if out is None or out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout.strip()


def _extract(commit, dest: Path) -> bool:
    """The engine as it existed at one commit, with no dependence on the working tree."""
    try:
        out = subprocess.run(["git", "archive", commit, "organica"], cwd=str(ROOT),
                             capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return False
    if out.returncode != 0 or not out.stdout:
        return False
    with tarfile.open(fileobj=io.BytesIO(out.stdout)) as archive:
        try:
            archive.extractall(dest, filter="data")
        except TypeError:  # Python < 3.12 has no extraction filter
            archive.extractall(dest)
    return (dest / "organica" / "sleep.py").exists()


def _fingerprint(dest: Path, mode: str = "normal") -> dict:
    driver = dest / "fingerprint.py"
    driver.write_text(DRIVER.replace("__CYCLES__", str(CYCLES)), encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(dest)
    env["PYTHONHASHSEED"] = "0"
    proc = subprocess.run([sys.executable, str(driver), mode], cwd=str(dest),
                          capture_output=True, text=True, env=env, timeout=600)
    assert proc.returncode == 0, (
        "the variant under %s failed to run, so nothing was compared:\n%s"
        % (dest.name, proc.stderr[-3000:]))
    return json.loads(proc.stdout)


@pytest.fixture(scope="module")
def engine(tmp_path_factory):
    before, after = _commit(BEFORE), _commit(AFTER)
    if before is None or after is None:
        pytest.skip("the split commit " + AFTER + " or its parent is not in this clone")
    root = tmp_path_factory.mktemp("sleep_split")
    variants = {}
    for name, commit in (("before", before), ("after", after)):
        dest = root / name
        dest.mkdir()
        if not _extract(commit, dest):
            pytest.skip("git archive could not read the " + name + " engine")
        variants[name] = dest
    return variants


def _first_difference(a: dict, b: dict) -> str:
    for index, (left, right) in enumerate(zip(a["reports"], b["reports"])):
        if left != right:
            fields = sorted(k for k in set(left) | set(right) if left.get(k) != right.get(k))
            return "cycle %d differs in %r" % (index + 1, fields[:8])
    if len(a["reports"]) != len(b["reports"]):
        return "the runs produced %d and %d reports" % (len(a["reports"]), len(b["reports"]))
    for table in sorted(set(a["tables"]) | set(b["tables"])):
        left, right = a["tables"].get(table), b["tables"].get(table)
        if left == right:
            continue
        if left is None or right is None:
            return "table %r exists in only one run" % table
        if left["columns"] != right["columns"]:
            return "table %r has different columns: %r vs %r" % (
                table, left["columns"], right["columns"])
        return "table %r differs (%d vs %d rows)" % (table, len(left["rows"]), len(right["rows"]))
    return "the fingerprints differ outside the reports and the tables"


def test_the_split_reproduces_the_pre_split_engine(engine):
    """The ship of Theseus, checked by running it twice: same reports, same substrate."""
    before = _fingerprint(engine["before"])
    after = _fingerprint(engine["after"])
    assert after == before, (
        "the engine at %s does not reproduce the engine at %s: %s"
        % (AFTER, BEFORE, _first_difference(before, after)))

    reports = before["reports"]
    assert len(reports) == CYCLES
    produced = [report for report in reports
                if report["composites_created"] or report["concepts"] or report["predictions"]]
    assert produced, "the run produced no structure, so equality between two empties proves nothing"
    assert before["tables"]["events"]["rows"], "the substrate is empty, so equality proves nothing"
    assert len(before["tables"]["precedes"]["rows"]) > 0, "the graph is empty, so equality proves nothing"


def test_the_probe_is_deterministic(engine):
    """Same variant, second process: a fingerprint that moved on its own could not prove anything."""
    first = _fingerprint(engine["before"])
    second = _fingerprint(engine["before"])
    assert second == first, "the probe is not deterministic: " + _first_difference(first, second)


def test_the_probe_can_tell_two_runs_apart(engine):
    """One extra word in the stream must change the fingerprint, or equality means nothing."""
    normal = _fingerprint(engine["after"])
    edited = _fingerprint(engine["after"], mode="edited")
    assert edited != normal, (
        "changing the stream produced an identical fingerprint, so the comparison cannot "
        "detect a behavioural difference at all")
