"""
tests/test_v1_freeze.py
------------------------------------------------------------------
The engine guard. It compares the shipped engine against a recorded reference commit and fails when
a guarded file has been edited without the reference being updated.

**What this replaced.** The guard used to compare against the archival tag `v0.9.0` and to skip
itself for every file once `organica.__version__ >= "0.12.0"`. Between those two facts it stopped
checking anything: the engine gained six modules and had `sleep.py` cut down by 1,777 lines while the
test kept reporting success by declining to look. `docs/ENGINE-VERSION-AUDIT.md` records that.

**Why a commit reference rather than the tag.** Organica 1 at `v0.9.0` is an archive. The engine on
master is a live object that is supposed to change. A guard pinned to the archive can only ever fail
or be switched off; a guard pinned to a recorded commit fails only when a change is *unrecorded*, and
that is the failure worth catching. Changing the engine is expected. Changing it silently is not.

**How to change the engine on purpose.** Bump the version, add a CHANGELOG entry, and update
`docs/engine_reference.json` (commit, engine_version, date) in the same commit. The guard then passes
against the new reference, and the change is in the record.

Three properties this test deliberately has:

1. **It can fail.** `test_the_comparator_detects_a_real_change` hashes two different files and
   asserts the comparison separates them, so the mechanism is proved rather than asserted.
2. **It skips honestly.** A shallow clone has no objects for the reference commit. The test skips and
   says why; it never passes silently because it could not check.
3. **It covers the engine, not the seven-file list.** The engine was split into modules that carry the
   cognition -- selection, synthesis, extraction, inquiry -- so a guard watching only `sleep.py`
   would be watching a shell.

Run:  python -m pytest tests/test_v1_freeze.py -v
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from organica import __version__

ROOT = Path(__file__).resolve().parent.parent

#: The archival tag. Organica 1 is frozen as of this commit, for the published record.
FREEZE_TAG = "v0.9.0"

#: The recorded reference the guard compares against.
REFERENCE = ROOT / "docs" / "engine_reference.json"

#: The seven files rule 12 names as the engine.
FROZEN_ENGINE = (
    "organica/sleep.py",
    "organica/memory.py",
    "organica/paths.py",
    "organica/streams.py",
    "organica/branch_streams.py",
    "organica/scale_streams.py",
    "organica/ground_truth_worlds.py",
)

#: The published artifacts. A frozen architecture whose results could drift is not frozen at all, so
#: these are checked against the archival tag for modification too.
FROZEN_ARTIFACTS = (
    "docs/force_matrix.json",
    "docs/verdicts.json",
    "docs/discovery.json",
    "docs/metric_sensitivity.json",
    "docs/phase_h_results.json",
    "docs/regime_shift_results.json",
    "docs/post_shift_adaptation_results.json",
    "docs/phase_k_results.json",
)


def _git(*args: str, timeout: int = 60):
    """Run a git command. Returns the CompletedProcess, or None if git is unusable here."""
    try:
        return subprocess.run(["git", *args], cwd=str(ROOT),
                              capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None


def _commit_is_present(commit: str) -> bool:
    """Is this commit's object actually in this checkout's object store?

    A shallow clone knows the SHA without the objects, and knowing a SHA is not the same as being
    able to read a file from it.
    """
    out = _git("cat-file", "-e", commit + "^{commit}")
    return out is not None and out.returncode == 0


def _tag_commit() -> str | None:
    """The commit the archival tag points at, or None if it cannot be read here."""
    out = _git("rev-list", "-n", "1", FREEZE_TAG + "^{commit}")
    if out is not None and out.returncode == 0 and out.stdout.strip():
        commit = out.stdout.strip()
        if _commit_is_present(commit):
            return commit
        return None
    ls = _git("ls-remote", "--tags", "origin", FREEZE_TAG + "*")
    if ls is None or ls.returncode != 0:
        return None
    remote = None
    for line in ls.stdout.splitlines():
        sha, _, name = line.partition("\t")
        if name.strip() == "refs/tags/" + FREEZE_TAG + "^{}":
            remote = sha.strip()
    if remote is None:
        return None
    if _commit_is_present(remote):
        return remote
    peeled = _git("rev-parse", remote + "^{commit}")
    if peeled is not None and peeled.returncode == 0 and peeled.stdout.strip():
        commit = peeled.stdout.strip()
        if _commit_is_present(commit):
            return commit
    return None


def _reference() -> dict:
    return json.loads(REFERENCE.read_text(encoding="utf-8"))


def _blob_id_at(relpath: str, commit: str) -> str | None:
    out = _git("rev-parse", commit + ":" + relpath)
    if out is None or out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout.strip()


def _working_blob_id(relpath: str) -> str | None:
    """The object ID the working-tree file would get if committed now.

    `hash-object --path` applies the same clean filter the index uses, so a file differing only in
    line endings -- routine under `core.autocrlf` -- correctly compares equal.
    """
    f = ROOT / relpath
    if not f.exists():
        return None
    out = _git("hash-object", "--path", relpath, str(f))
    if out is None or out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout.strip()


def _blob_id_of_file(path: Path) -> str | None:
    out = _git("hash-object", str(path))
    if out is None or out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout.strip()


def _first_difference(relpath: str, commit: str) -> str:
    d = _git("diff", commit, "--", relpath)
    if d is not None and d.returncode == 0 and d.stdout.strip():
        lines = [l for l in d.stdout.splitlines()
                 if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
        if lines:
            return "\n    " + "\n    ".join(lines[:12])
    return ""


@pytest.fixture(scope="module")
def reference_commit() -> dict:
    data = _reference()
    commit = data["commit"]
    if not _commit_is_present(commit):
        pytest.skip(
            "the engine reference commit " + commit[:12] + " cannot be read here, so the guard cannot "
            "check it. A shallow clone knows the SHA but not the objects -- this is a skip, not a pass. "
            "Run a full clone or `git fetch` to check it.")
    return data


GUARDED = tuple(_reference()["guarded_files"])


@pytest.mark.parametrize("relpath", GUARDED)
def test_engine_file_matches_the_recorded_reference(relpath, reference_commit):
    """A guarded engine file must be identical to the recorded reference commit."""
    commit = reference_commit["commit"]
    tagged = _blob_id_at(relpath, commit)
    working = _working_blob_id(relpath)

    if tagged is None:
        pytest.fail(
            relpath + " does not exist at the reference commit " + commit[:12] + ". The reference and "
            "the repository disagree about what the engine is.")

    assert working is not None, (
        relpath + " has been deleted. The engine still needs it; restoring the file is the fix, and if "
        "the deletion is intended, record that and re-baseline docs/engine_reference.json.")

    if tagged == working:
        return

    detail = _first_difference(relpath, commit)
    pytest.fail(
        relpath + " has changed since the recorded engine reference " + commit[:12] + "." + detail +
        "\n\nAn unrecorded engine change is the failure this guard exists to catch. If the change is "
        "intended: bump the version, add a CHANGELOG entry, and update docs/engine_reference.json "
        "(commit, engine_version, date) in the same commit. If it is not intended: revert it.")


def test_the_comparator_detects_a_real_change(tmp_path):
    """The guard can fail: two different files must produce different object IDs."""
    a = tmp_path / "a.py"
    b = tmp_path / "b.py"
    same = tmp_path / "same.py"
    a.write_text("PREDICTIONS = 40\n", encoding="utf-8")
    b.write_text("PREDICTIONS = 20\n", encoding="utf-8")
    same.write_text("PREDICTIONS = 40\n", encoding="utf-8")
    first, second, third = _blob_id_of_file(a), _blob_id_of_file(b), _blob_id_of_file(same)
    assert first is not None and second is not None and third is not None
    assert first == third, "identical content must compare equal"
    assert first != second, "a one-token change must compare unequal"


def test_the_reference_records_a_version_and_a_reason():
    """The reference cannot drift silently: its version must match the package."""
    data = _reference()
    assert data["engine_version"] == __version__, (
        "docs/engine_reference.json records engine_version " + str(data["engine_version"]) +
        " but the package declares " + __version__ + ". A version bump is a deliberate act: update the "
        "reference in the same commit.")
    assert data.get("date") and data.get("reason"), "the reference must say when and why"
    assert set(data["guarded_files"]) >= set(FROZEN_ENGINE), (
        "the reference must guard at least the seven files rule 12 names")


@pytest.mark.parametrize("relpath", FROZEN_ARTIFACTS)
def test_published_artifact_is_unchanged_since_the_freeze(relpath):
    """A published result must not be edited in place; corrections are documented, not applied."""
    commit = _tag_commit()
    if commit is None:
        pytest.skip("the archival tag " + FREEZE_TAG + " cannot be read here; nothing to compare.")

    tagged = _blob_id_at(relpath, commit)
    if tagged is None:
        pytest.skip(relpath + " does not exist at " + FREEZE_TAG + "; nothing to compare.")

    working = _working_blob_id(relpath)
    assert working is not None, (
        relpath + " has been deleted. It is a published result. If it is withdrawn, record that as a "
        "documented correction rather than removing it.")

    if tagged != working:
        detail = _first_difference(relpath, commit)
        pytest.fail(
            relpath + " has changed since Organica 1 was frozen at " + FREEZE_TAG + "." + detail +
            "\n\nIt is a published result. Corrections are documented, not quietly applied: add the "
            "correction to the journal and the facts sheet and leave the artifact alone.")


def test_the_freeze_record_exists_and_names_the_tag():
    """The archival record must exist and name the tag it describes."""
    record = ROOT / "docs" / "V1-FREEZE.md"
    assert record.exists(), "docs/V1-FREEZE.md is missing."
    text = record.read_text(encoding="utf-8")
    assert FREEZE_TAG in text
    for relpath in FROZEN_ENGINE:
        assert relpath in text, (
            "docs/V1-FREEZE.md does not list " + relpath + " as frozen, but this test treats it as "
            "part of the engine. The document and the mechanism must agree.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
