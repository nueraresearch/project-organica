"""Render and check the judged-block inventory on the engine evidence synthesis.

The synthesis indexes the engine's evidence by build, and its largest claim is
an inventory: every block that returned a decision-bearing verdict, with the
build it ran on. A table like that is exactly where a transcription drifts --
"PERSISTENCE REPAIRED" becomes "PERSISTENCE CONFIRMED" one edit at a time, and
nothing fails because the sentence reads perfectly.

So the inventory is a record (`docs/engine_evidence_inventory.json`) and the
page is generated from it. Every row checks against the artifact it names: the
verdict is resolved at its recorded path and compared exactly, the build is
either read from the artifact's `engine_version` or verified in the document
that records it, and a row claiming `unrecorded` fails if its artifact does
carry an engine version. A missing artifact, a moved field or a changed verdict
is a failure, not a stale sentence.

    python -m benchmarks.engine_evidence_inventory --check
    python -m benchmarks.engine_evidence_inventory --write
    python -m benchmarks.engine_evidence_inventory --self-test

``--check`` writes nothing. The page's prose is not generated; only the table
between the markers is.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "engine_evidence_inventory.json"
PAGE = ROOT / "docs" / "ENGINE-EVIDENCE-SYNTHESIS.md"

BEGIN = (
    "<!-- BEGIN JUDGED BLOCKS: generated from docs/engine_evidence_inventory.json by "
    "benchmarks/engine_evidence_inventory.py; do not edit by hand -->"
)
END = "<!-- END JUDGED BLOCKS -->"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(payload, path: str):
    current = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(path)
        current = current[part]
    return current


def _has_engine_version(payload) -> bool:
    if isinstance(payload, dict):
        if payload.get("engine_version"):
            return True
        return any(_has_engine_version(value) for value in payload.values())
    if isinstance(payload, list):
        return any(_has_engine_version(value) for value in payload)
    return False


def row_problems(row: dict) -> list[str]:
    """Every way one inventory row disagrees with the record it names."""
    found: list[str] = []
    artifact = ROOT / row["artifact"] if row.get("artifact") else None
    if not artifact or not artifact.exists():
        found.append("%s: artifact %s is missing" % (row["id"], row.get("artifact")))
        return found

    if row.get("verdict_path"):
        try:
            payload = _load(artifact)
        except ValueError as exc:
            return ["%s: artifact is not readable JSON: %s" % (row["id"], exc)]
        try:
            actual = _resolve(payload, row["verdict_path"])
        except KeyError:
            found.append(
                "%s: verdict path %r is not in %s"
                % (row["id"], row["verdict_path"], row["artifact"])
            )
        else:
            if actual != row["verdict"]:
                found.append(
                    "%s: verdict is %r at %s, inventory says %r"
                    % (row["id"], actual, row["verdict_path"], row["verdict"])
                )
    else:
        record = ROOT / row["record"]
        if not record.exists():
            found.append("%s: record %s is missing" % (row["id"], row["record"]))
        elif row.get("verbatim") and row["verbatim"] not in record.read_text(encoding="utf-8"):
            found.append(
                "%s: the page does not contain the quoted verdict %r"
                % (row["id"], row["verbatim"])
            )

    if row.get("build_field"):
        payload = _load(artifact)
        try:
            actual_build = _resolve(payload, row["build_field"])
        except KeyError:
            found.append(
                "%s: build field %r is not in %s"
                % (row["id"], row["build_field"], row["artifact"])
            )
        else:
            if actual_build != row["build"]:
                found.append(
                    "%s: build is %r, inventory says %r"
                    % (row["id"], actual_build, row["build"])
                )
    elif row.get("build_record"):
        source = ROOT / row["build_record"]
        if not source.exists():
            found.append("%s: build record %s is missing" % (row["id"], row["build_record"]))
        elif row["build_verbatim"] not in source.read_text(encoding="utf-8"):
            found.append(
                "%s: build %r is not recorded by %s"
                % (row["id"], row["build"], row["build_record"])
            )
    elif row.get("build") == "unrecorded":
        try:
            payload = _load(artifact)
        except ValueError:
            payload = None
        if payload is not None and _has_engine_version(payload):
            found.append(
                "%s: inventory says unrecorded, but %s carries an engine_version"
                % (row["id"], row["artifact"])
            )
    else:
        found.append("%s: build %r has no source" % (row["id"], row.get("build")))
    return found


def table(manifest: dict) -> str:
    lines = ["| Block | Build | Verdict | Record |", "|---|---|---|---|"]
    for row in manifest["rows"]:
        record = row["record"].split("/")[-1]
        lines.append(
            "| %s | %s | `%s` | [%s](%s) |"
            % (row["block"], row["build"], row["verdict"], record, record)
        )
    return "\n".join(lines)


def _region(text: str) -> str:
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("expected exactly one judged-block marker pair")
    start = text.index(BEGIN) + len(BEGIN)
    stop = text.index(END)
    if stop < start:
        raise ValueError("the judged-block markers are out of order")
    return text[start:stop]


def problems(text: str, manifest: dict, *, rows_only: bool = False) -> list[str]:
    found: list[str] = []
    ids = [row["id"] for row in manifest["rows"]]
    if len(ids) != len(set(ids)):
        found.append("duplicate block id in the inventory")
    for row in manifest["rows"]:
        found.extend(row_problems(row))
    if not rows_only:
        expected = "\n" + table(manifest) + "\n"
        try:
            current = _region(text)
        except ValueError as exc:
            found.append(str(exc))
        else:
            if current != expected:
                found.append(
                    "the judged-block table is stale; run "
                    "python -m benchmarks.engine_evidence_inventory --write"
                )
    return found


def write(text: str, manifest: dict) -> str:
    start = text.index(BEGIN) + len(BEGIN)
    stop = text.index(END)
    return text[:start] + "\n" + table(manifest) + "\n" + text[stop:]


def self_test(text: str, manifest: dict) -> list[str]:
    failures: list[str] = []
    if problems(text, manifest):
        failures.append("the committed inventory does not pass its own check")
    tampered = json.loads(json.dumps(manifest))
    machine_row = next(row for row in tampered["rows"] if row["verdict_path"])
    machine_row["verdict"] = "SUPPORTED"
    if not problems(text, tampered, rows_only=True):
        failures.append("the check accepted a tampered verdict")
    moved_build = json.loads(json.dumps(manifest))
    build_row = next(row for row in moved_build["rows"] if row["build_field"])
    build_row["build"] = "9.9.9"
    if not problems(text, moved_build, rows_only=True):
        failures.append("the check accepted a moved build")
    dropped = json.loads(json.dumps(manifest))
    dropped["rows"] = dropped["rows"][1:]
    if not problems(text, dropped):
        failures.append("the check accepted a shortened inventory")
    return failures


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="verify the page; writes nothing")
    group.add_argument("--write", action="store_true", help="regenerate the table")
    group.add_argument("--self-test", action="store_true", help="prove the check can fail")
    args = parser.parse_args(argv)

    manifest = _load(MANIFEST)
    text = PAGE.read_text(encoding="utf-8")

    if args.write:
        PAGE.write_text(write(text, manifest), encoding="utf-8")
        print("wrote the judged-block table into", PAGE.relative_to(ROOT))
        return 0

    if args.self_test:
        failures = self_test(text, manifest)
        for failure in failures:
            print("FAIL:", failure)
        if failures:
            return 1
        print("self-test: the inventory accepts its page and rejects a tampered verdict")
        return 0

    failures = problems(text, manifest)
    for failure in failures:
        print("FAIL:", failure)
    if failures:
        return 1
    print(
        "judged-block inventory: %d rows match their artifacts and builds"
        % len(manifest["rows"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
