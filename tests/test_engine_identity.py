"""Every released engine version has a checkable identity.

`tests/test_v1_freeze.py` compares the working tree against `v0.9.0` and, since
0.12.0, skips its engine checks because the engine legitimately moved on.  That
leaves the working tree with no engine-identity check at all: the version number
names a release, and nothing verifies that the code is that release.

This test closes the gap with a per-version record.  `docs/engine-identity/
<version>.json` stores the git blob and sha256 of every `organica/**/*.py` at the
tag.  If the tag exists, the record must exist and the working tree must match
it.  A later engine change therefore fails the suite until the version is
bumped and a new identity recorded -- which is the intended behaviour
(AGENTS.md rule 10), not a nuisance.

The check is built to fail: `test_the_check_can_fail` doctors a record and
asserts that the comparison reports it.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

import organica

REPO = Path(__file__).resolve().parent.parent
IDENTITY_DIR = REPO / "docs" / "engine-identity"


def _git(*args: str) -> str | None:
    out = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def tag_commit(version: str) -> str | None:
    """The commit `v<version>` peels to, or None when the tag is not readable."""
    return _git("rev-parse", f"v{version}^{{commit}}")


def record_path(version: str) -> Path:
    return IDENTITY_DIR / f"{version}.json"


def load_record(version: str) -> dict:
    return json.loads(record_path(version).read_text(encoding="utf-8"))


def engine_files(root: Path = REPO) -> set[str]:
    return {str(p.relative_to(root)) for p in (root / "organica").rglob("*.py")}


def mismatches(record: dict, root: Path = REPO) -> list[str]:
    """Every engine file that is missing or differs from the recorded identity."""
    problems = []
    for relpath, meta in record["files"].items():
        path = root / relpath
        if not path.exists():
            problems.append(f"{relpath}: missing from the working tree")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != meta["sha256"]:
            problems.append(f"{relpath}: sha256 {digest[:12]} != recorded {meta['sha256'][:12]}")
    return problems


@pytest.fixture(scope="module")
def record() -> dict:
    version = organica.__version__
    if tag_commit(version) is None:
        pytest.skip(f"tag v{version} is not readable here, so there is no identity to check")
    path = record_path(version)
    assert path.exists(), (
        f"v{version} is tagged but {path.relative_to(REPO)} is missing: record the "
        "engine identity for a release before tagging it")
    return load_record(version)


def test_the_record_names_the_tagged_commit(record: dict) -> None:
    commit = tag_commit(record["version"])
    assert commit is not None
    assert record["commit"] == commit, (
        f"identity records commit {record['commit']}, but v{record['version']} is {commit}")


def test_the_record_covers_the_whole_engine(record: dict) -> None:
    on_disk = engine_files()
    recorded = set(record["files"])
    assert recorded == on_disk, (
        "identity and working tree disagree about which modules are the engine: "
        f"missing from the record: {sorted(on_disk - recorded)}; "
        f"stale in the record: {sorted(recorded - on_disk)}")


def test_every_engine_module_matches_its_recorded_identity(record: dict) -> None:
    problems = mismatches(record)
    assert not problems, (
        "the working tree is not the released engine. If the change is intended, bump "
        "the version and record a new identity (AGENTS.md rule 10):\n" + "\n".join(problems))


def test_the_check_can_fail(record: dict) -> None:
    doctored = {"files": dict(record["files"])}
    first = next(iter(doctored["files"]))
    doctored["files"][first] = {"sha256": "0" * 64, "git_blob": "0" * 40}
    assert mismatches(doctored), "the identity check accepted a doctored record"
