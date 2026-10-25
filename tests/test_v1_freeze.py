"""
tests/test_v1_freeze.py
------------------------------------------------------------------
Organica 1 is frozen. This test is the mechanism that makes the freeze real.

The owner defined it precisely: *"No more architectural modifications to
Organica 1. The V1 engine becomes a fixed reference object. Everything
afterwards measures it. Nothing afterwards quietly changes it. The v0.9.0 tag
becomes the archival reference."*

A freeze that lives only in a README is a promise. This repository's history
is a history of promises drifting: the version declared a release master was
not, the changelog linked a 404, the "structure flat" claim was an
overstatement, the tag-frequency counter measured the wrong population. Each
of those was a documentation-versus-evidence gap, and each was found by an
instrument rather than by reading carefully.

So this is an instrument. It reads the frozen files out of the `v0.9.0` tag
and compares them, byte for byte, with the working tree. If one of them has
changed, the freeze has been broken and the test says so.

Three properties this test deliberately has:

1. **It can fail.** It compares real content from a real tag; a changed file
   produces a real failure with the differing file named.
2. **It skips honestly.** A shallow clone has no ancestor tags, so the tag is
   simply not there. The test skips and says why. It never passes silently
   because it could not check.
3. **It is about the ENGINE, not the archive.** Benchmarks, harnesses,
   documentation, and the owner's action list all stay free to change -- see
   `docs/V1-FREEZE.md` §2. A frozen architecture whose published results
   could drift is not frozen at all, so the campaign artifacts are checked too.

Run:  python -m pytest tests/test_v1_freeze.py -v
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

#: The archival tag. Organica 1 is frozen as of this commit.
FREEZE_TAG = "v0.9.0"

#: The engine. These define what Organica 1 *is*.
FROZEN_ENGINE = (
    "organica/sleep.py",
    "organica/memory.py",
    "organica/paths.py",
    "organica/streams.py",
    "organica/branch_streams.py",
    "organica/scale_streams.py",
    "organica/ground_truth_worlds.py",
)

#: The published artifacts. A frozen architecture whose results could drift
#: is not frozen at all, so these are checked for modification too.
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
    """Run a git command. Returns the CompletedProcess, or None if git is
    unusable here."""
    try:
        return subprocess.run(["git", *args], cwd=str(ROOT),
                              capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None


def _tag_commit() -> str | None:
    """The commit the freeze tag points at, or None if it is not reachable."""
    out = _git("rev-list", "-n", "1", FREEZE_TAG)
    if out is None or out.returncode != 0 or not out.stdout.strip():
        # Not in this checkout. It may still be on the remote -- a shallow
        # clone has no ancestor tags. Check there before giving up.
        ls = _git("ls-remote", "--tags", "origin", FREEZE_TAG)
        if ls is None or ls.returncode != 0:
            return None
        for line in ls.stdout.splitlines():
            sha, _, name = line.partition("\t")
            name = name.strip()
            if name == f"refs/tags/{FREEZE_TAG}^{{}}":
                return sha.strip()
            if name == f"refs/tags/{FREEZE_TAG}":
                return sha.strip()
        return None
    return out.stdout.strip()


def _blob_at_tag(path: str, commit: str) -> bytes | None:
    """The bytes of `path` at the tagged commit, or None if it is absent."""
    out = _git("show", f"{commit}:{path}")
    if out is None or out.returncode != 0:
        return None
    return out.stdout.encode("utf-8", errors="surrogateescape")


def _working_bytes(path: str) -> bytes | None:
    f = ROOT / path
    if not f.exists():
        return None
    return f.read_bytes()


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


@pytest.fixture(scope="module")
def freeze_commit() -> str:
    commit = _tag_commit()
    if commit is None:
        pytest.skip(
            f"the archival tag {FREEZE_TAG} is not reachable from this "
            f"environment (a shallow clone has no ancestor tags, and the "
            f"remote may be unreachable). The freeze cannot be verified "
            f"here. Run a full clone to check it.")
    return commit


@pytest.mark.parametrize("relpath", FROZEN_ENGINE)
def test_engine_file_is_unchanged_since_the_freeze(relpath, freeze_commit):
    """A frozen engine file must be byte-identical to the tagged version."""
    tagged = _blob_at_tag(relpath, freeze_commit)
    working = _working_bytes(relpath)

    assert tagged is not None, (
        f"{relpath} does not exist at {FREEZE_TAG} ({freeze_commit[:12]}). "
        f"The freeze reference and the repository disagree about what the "
        f"engine is.")
    assert working is not None, (
        f"{relpath} has been deleted. Organica 1 is frozen; restoring the "
        f"file is the fix, not amending the freeze.")

    if tagged == working:
        return

    # Name the difference precisely. A failure that says only "changed" is
    # weaker than one that says which file and how much.
    tagged_lines = tagged.decode("utf-8", errors="replace").splitlines()
    working_lines = working.decode("utf-8", errors="replace").splitlines()
    changed = [
        i + 1 for i, (a, b) in enumerate(zip(tagged_lines, working_lines))
        if a != b
    ]
    detail = ""
    if changed:
        first = changed[0]
        detail = (f" First difference at line {first}: "
                  f"tagged {tagged_lines[first - 1]!r}, "
                  f"working {working_lines[first - 1]!r}.")
    elif len(tagged_lines) != len(working_lines):
        detail = (f" Line count changed: {len(tagged_lines)} -> "
                  f"{len(working_lines)}.")

    pytest.fail(
        f"{relpath} has changed since Organica 1 was frozen at {FREEZE_TAG} "
        f"({freeze_commit[:12]}).{detail}\n\n"
        f"Organica 1 is a fixed reference object: everything after it "
        f"MEASURES the engine, and nothing after it changes it quietly. "
        f"If the change is behaviour-preserving and belongs in the engine, "
        f"put it in a NEW module instead -- the freeze covers the listed "
        f"files, not the package. If it is an intentional architecture "
        f"change, that is a decision the owner has to make and record, not "
        f"something to slip in beside a benchmark. See docs/V1-FREEZE.md.")


@pytest.mark.parametrize("relpath", FROZEN_ARTIFACTS)
def test_published_artifact_is_unchanged_since_the_freeze(relpath, freeze_commit):
    """A published result must not be edited in place.

    The project's own rule is that corrections are *documented*, not quietly
    applied: a correction appends to the record and points back at it. Editing
    a published artifact in place destroys the provenance the facts sheet
    depends on.
    """
    tagged = _blob_at_tag(relpath, freeze_commit)
    if tagged is None:
        # Not present at the tag: the artifact was produced after the freeze,
        # or is gitignored. Either way there is nothing to compare.
        pytest.skip(f"{relpath} does not exist at {FREEZE_TAG}; nothing to compare.")

    working = _working_bytes(relpath)
    assert working is not None, (
        f"{relpath} has been deleted. It is a published result. If it is "
        f"withdrawn, record that as a documented correction rather than "
        f"removing it.")

    if tagged != working:
        pytest.fail(
            f"{relpath} has changed since Organica 1 was frozen at "
            f"{FREEZE_TAG} ({freeze_commit[:12]}).\n\n"
            f"It is a published result. Corrections are documented, not "
            f"quietly applied: add the correction to the journal and the "
            f"facts sheet, point at the section that supersedes the old "
            f"number, and leave the artifact alone. The digest of the "
            f"tagged version is {_digest(tagged)} and of the working copy "
            f"{_digest(working)}.")


def test_the_freeze_record_exists_and_names_the_tag():
    """The freeze must be documented, and the document must point at the
    tag this test enforces. A freeze with no record is not a freeze."""
    record = ROOT / "docs" / "V1-FREEZE.md"
    assert record.exists(), (
        "docs/V1-FREEZE.md is missing. Organica 1 is frozen, and the freeze "
        "has to be written down: what is frozen, what is not, and why.")
    text = record.read_text(encoding="utf-8")
    assert FREEZE_TAG in text, (
        f"docs/V1-FREEZE.md does not name {FREEZE_TAG}, which is the tag "
        f"this test enforces.")
    for relpath in FROZEN_ENGINE:
        assert relpath in text, (
            f"docs/V1-FREEZE.md does not list {relpath} as frozen, but "
            f"tests/test_v1_freeze.py enforces it. The document and the "
            f"mechanism must agree.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
