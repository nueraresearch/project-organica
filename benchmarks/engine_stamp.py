"""Stamp a run artifact with the engine that produced it, and check that writers do.

The engine is pinned by hash (`docs/engine_pin.json`, `benchmarks/engine_pin.py`), which answers
"are these the bytes the pin recorded?". It answers nothing about a *result*: an artifact that does
not name its build cannot be attributed to anything, and the engine-version audit
(`docs/ENGINE-VERSION-AUDIT.md`) exists because seventeen artifacts recorded a build while a long
tail of others recorded nothing.

So a harness stamps the record it writes:

    record = engine_stamp.stamp(record)
    json.dump(record, handle, indent=2)

`stamp` adds four fields and keeps the rest of the schema alone:

``engine_version``
    the package version the harness is running in, read from ``organica/__init__.py`` without
    importing the package (`benchmarks.engine_pin.package_version`).
``engine_commit``
    the commit the pin was taken at. It is provenance: the pin guarantees the bytes are unchanged
    since that commit, so the pair together says *these bytes produced this file*.
``engine_sha256``
    one digest over the pin's whole file map, so the artifact names the exact byte set rather than a
    commit that a later re-pin could point somewhere else. `engine_commit` says *when the bytes were
    recorded*; this says *which bytes*, and it is checkable against `docs/engine_pin.json` alone.
``runner``
    the module that called `stamp`, found from the call stack. The commit names the engine; this
    names the harness, which is the other half of "what produced this file" when two harnesses run
    the same pinned engine.

A list of records is stamped record by record, because several harnesses write their artifact as a
list of cells and changing that to an envelope would break every reader of it.

``--check`` fails in three cases, and each one is a defect rather than a style rule:

1. **An artifact writer that does not stamp.** A module under ``benchmarks/`` that writes JSON to a
   file and never mentions this module. "Writes" is decided from the syntax tree, not from the text:
   a call to ``json.dump``, or a write whose argument contains ``json.dumps``. A module that only
   *prints* ``json.dumps`` or round-trips it through ``json.loads`` is not an artifact writer and is
   not flagged. The generators of *derived documents* are exempt and listed with the reason, because
   a view rendered from other records is not a run.
2. **An artifact that names a version and not a commit.** Both or neither: a version alone is the
   half-stamp this module exists to stop. Artifacts stamped before this rule existed are
   grandfathered through the set the audit already recorded, derived from the audit rather than
   typed here, so it cannot drift from the document that justifies it.
3. **A commit field that is not a commit.** 40 hex characters, or the field is decoration.

Nothing is written in ``--check`` mode.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

from benchmarks import engine_pin

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
DOCS = ROOT / "docs"
AUDIT = DOCS / "engine_version_audit.json"

#: What a run artifact must carry to name its build and the process that ran it. The last two were
#: added after the first rule landed; the artifacts stamped before them are grandfathered by path,
#: and `stamp` now writes all four at once, so a new artifact cannot be written with fewer.
STAMPED = ("engine_version", "engine_commit", "engine_sha256", "runner")

#: Writers of *derived* documents: they render other records and run no engine, so a stamp would
#: name the build of a document that measured nothing.
DERIVED = {
    "change_map.py",  # renders docs/ENGINE-CHANGE-FAILURE-MAP.md from git history
    "engine_pin.py",  # writes the pin itself; the pin is the reference, not a result
    "question_survival.py",  # joins the registry to the audit; measures nothing
    "research_accountability.py",  # renders the findings and dashboard from the registry
    "research_registry.py",  # writes the question registry itself
    "test_count.py",  # records the suite's own counts
    "c1_c9_preflight.py",  # read-only audit of C1-C9; runs no engine
    "a1_gate_readiness.py",  # read-only gate contract and readiness audit; runs no engine
    "a1_baseline_availability.py",  # no-arm denominator audit; runs no A1 cell
    "a1_target_viability.py",  # read-only target/C2 viability join; runs no engine
    "a1_design_viability.py",  # read-only C1/C2 design-viability join; runs no engine
    "a1_n20_competent_selection.py",  # pre-registered rule draft; selects and runs nothing
    "a1_k_decomposition.py",  # descriptive no-arm K decomposition; runs nothing
    "a1_successor_preflight.py",  # no-arm gate harness; selects, freezes and runs nothing
    "a1_successor_candidate.py",  # no-arm candidate spec; selects, freezes and runs nothing
    "a1_successor_schema.py",  # schema/validator writer; selects, freezes and runs nothing
    "a1_two_path.py",  # dry-run manifest and grant gate; opens no database
    "g9_stage_ledger.py",  # validator fixtures/page; runs no engine and writes no ledger
    "carrier_formation_a0.py",  # read-only join of carrier and provenance rows; runs no engine
}

_COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _rel(path: Path) -> str:
    """A path for a message, whether or not it lives under the repository."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _attr(call: ast.Call):
    """The name a call is made through: `json.dump(...)` -> "dump", `f.write(...)` -> "write"."""
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def _is_json(call: ast.Call, name: str) -> bool:
    """Is this a call to `json.<name>`?"""
    func = call.func
    return (isinstance(func, ast.Attribute) and func.attr == name
            and isinstance(func.value, ast.Name) and func.value.id == "json")


def _contains_json_dumps(node: ast.AST) -> bool:
    return any(isinstance(inner, ast.Call) and _is_json(inner, "dumps") for inner in ast.walk(node))


def write_targets(source: str) -> list:
    """The expressions a module serializes into a file, found from the syntax tree.

    Two forms count, because they are the two forms the repository uses:

    * ``json.dump(record, handle)`` -- the record is the first argument;
    * ``handle.write_text(json.dumps(record) + "\\n")`` and its ``_atomic_write`` relatives -- the
      record is the first argument of the ``json.dumps`` inside the written value.

    A row-at-a-time ``f.write(json.dumps(row))`` is deliberately *not* a target: that is a data
    stream or a checkpoint, and stamping each row would change the stream the engine reads.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    targets = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _is_json(node, "dump") and node.args:
            targets.append(node.args[0])
            continue
        if _attr(node) in ("write_text", "_atomic_write", "atomic_write"):
            for argument in node.args:
                if _contains_json_dumps(argument):
                    for inner in ast.walk(argument):
                        if isinstance(inner, ast.Call) and _is_json(inner, "dumps") and inner.args:
                            targets.append(inner.args[0])
    return targets


def writes_an_artifact(source: str) -> bool:
    return bool(write_targets(source))


def engine_version() -> str:
    return engine_pin.package_version()


def engine_sha256() -> str:
    """One digest over the pinned file map: the engine's *bytes*, not the commit they were found at.

    `engine_commit` is a pointer, and a pointer can be re-pointed by a later re-pin at the same
    history. This value is computed from the hashes themselves, so an artifact that carries it can
    be compared against `docs/engine_pin.json` with no reference to git at all.
    """
    files = engine_pin.load_pin().get("files") or {}
    if not files:
        raise RuntimeError(
            "docs/engine_pin.json records no file hashes, so an artifact cannot name the bytes it "
            "ran; re-pin with python -m benchmarks.engine_pin")
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def runner() -> str:
    """The module that called `stamp`, skipping this module's own frames."""
    frame = sys._getframe(1)
    while frame is not None:
        if frame.f_globals.get("__name__") != __name__:
            return frame.f_globals.get("__name__") or "<module>"
        frame = frame.f_back
    return "<unknown>"


def pinned_commit() -> str:
    """The commit the engine pin was taken at, which is the engine's provenance."""
    pin = engine_pin.load_pin()
    commit = pin.get("head_at_pin")
    if not commit:
        raise RuntimeError(
            "docs/engine_pin.json records no head_at_pin, so an artifact cannot be attributed to a "
            "build; re-pin with python -m benchmarks.engine_pin")
    return commit


def stamp(record):
    """Add `engine_version` and `engine_commit`, keeping the record's shape and its other fields."""
    if isinstance(record, list):
        return [stamp(item) for item in record]
    if not isinstance(record, dict):
        raise TypeError(
            "engine_stamp.stamp takes a dict or a list of dicts, not %s. An artifact of another "
            "shape cannot carry its build, so the artifact needs a record shape first."
            % type(record).__name__)
    stamped = dict(record)
    stamped["engine_version"] = engine_version()
    stamped["engine_commit"] = pinned_commit()
    stamped["engine_sha256"] = engine_sha256()
    # Read before the caller's frame unwinds; a list is stamped item by item and every item must
    # name the same writer as the list, so it is resolved on the outermost call and reused.
    stamped["runner"] = record.get("runner") or runner()
    return stamped


def missing(record) -> list:
    """The stamp fields this record lacks. An empty list means it is stamped."""
    records = record if isinstance(record, list) else [record]
    gaps = []
    for item in records:
        if not isinstance(item, dict):
            continue
        gaps.extend(field for field in STAMPED if not item.get(field))
    return sorted(set(gaps))


def grandfathered() -> set:
    """Artifacts stamped before this rule existed, as the audit already recorded them.

    Derived from `docs/engine_version_audit.json` rather than typed, so the exemption cannot drift
    from the document that justifies it. Published artifacts are not edited to add a field.
    """
    if not AUDIT.exists():
        return set()
    try:
        data = json.loads(AUDIT.read_text(encoding="utf-8"))
    except ValueError:
        return set()
    return {entry["path"] for entry in data.get("artifacts_with_engine_version", [])}


def unstamped_writers() -> list:
    """Artifact writers that never stamp. This is the live enforcement of the rule."""
    offenders = []
    for path in sorted(BENCH.glob("*.py")):
        if path.name in DERIVED or path.name == Path(__file__).name:
            continue
        source = path.read_text(encoding="utf-8")
        if writes_an_artifact(source) and "engine_stamp" not in source:
            offenders.append(path.name)
    return offenders


def half_stamped() -> list:
    """Artifacts that name a version and no commit, outside the grandfathered set."""
    waived = grandfathered()
    offenders = []
    for path in sorted(DOCS.glob("*.json")):
        rel = _rel(path)
        if rel in waived:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("engine_version") and not data.get("engine_commit"):
            offenders.append(rel)
    return offenders


def bad_commits() -> list:
    offenders = []
    for path in sorted(DOCS.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("engine_commit"):
            if not _COMMIT.match(str(data["engine_commit"])):
                offenders.append(_rel(path))
    return offenders


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify that writers stamp and that artifacts are attributable")
    args = parser.parse_args(argv)

    if args.check:
        failures = ["benchmarks/%s writes a JSON artifact without engine_stamp" % name
                    for name in unstamped_writers()]
        failures += ["%s names an engine_version and does not name its build fully" % rel
                     for rel in half_stamped()]
        failures += ["%s has an engine_commit that is not a 40-character sha" % rel
                     for rel in bad_commits()]
        if failures:
            for failure in failures:
                print("FAIL:", failure)
            print("\n%d problem(s): an artifact that does not name its build cannot be attributed "
                  "to one. Stamp the writer with engine_stamp.stamp(record) before it is dumped."
                  % len(failures))
            return 1
        writers = [p for p in sorted(BENCH.glob("*.py"))
                   if p.name not in DERIVED and p.name != Path(__file__).name]
        print("engine stamp: %d artifact writer(s) stamp, %d artifact(s) grandfathered, "
              "%d attributable" % (len(writers) - len(unstamped_writers()), len(grandfathered()),
                                   len(list(DOCS.glob("*.json"))) - len(half_stamped())))
        return 0

    print("engine_stamp is a library and a check; run python -m benchmarks.engine_stamp --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
