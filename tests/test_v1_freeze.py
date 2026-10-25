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

So this is an instrument. It compares the frozen files against the `v0.9.0`
tag, using git's own notion of file identity, and fails if one of them has
changed. If it changed, the freeze has been broken and the test says which
file and how.

**Why it compares git object IDs rather than raw bytes.** This repository
checks out with `core.autocrlf` on, so a working-tree file and the blob
stored in the tag can differ in line endings while being *the same file* as
far as git is concerned. Comparing raw bytes would therefore fail on files
nobody touched -- which is worse than no test, because it trains the reader
to ignore it. So the comparison asks git the question that actually matters:
*would committing this file right now change it?* That is
`git hash-object --path`, which applies the same clean filter the index
uses, compared against the blob ID recorded in the tag.

Three properties this test deliberately has:

1. **It can fail.** It compares real content from a real tag; a changed file
   produces a real failure with the differing file named. This was verified by
   temporarily modifying a frozen file and watching the test fail.
2. **It skips honestly.** A shallow clone has no ancestor tags, so the tag is
   simply not there. The test skips and says why. It never passes silently
   because it could not check.
3. **It is about the ENGINE, not the archive.** Benchmarks, harnesses,
   documentation, and the owner's action list all stay free to change -- see
   `docs/V1-FREEZE.md` section 2. A frozen architecture whose published
   results could drift is not frozen at all, so the campaign artifacts are
   checked too.

Run:  python -m pytest tests/test_v1_freeze.py -v
"""

from __future__ import annotations

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


def _commit_is_present(commit: str) -> bool:
    """Is this commit's object actually in this checkout's object store?

    A commit SHA can be *known* without its objects being *here*. A shallow
    clone knows the SHA of a remote tag's target and cannot read a single
    file from it. Knowing the SHA is not the same as being able to check
    the freeze against it.
    """
    out = _git("cat-file", "-e", f"{commit}^{{commit}}")
    return out is not None and out.returncode == 0


def _tag_commit() -> str | None:
    """The commit the freeze tag points at, or None if it is not reachable.

    Returns the COMMIT, not the tag object. `v0.9.0` is an annotated tag, so
    `refs/tags/v0.9.0` names a tag object and `refs/tags/v0.9.0^{}` names
    the commit it points at. Resolving to the wrong one makes every
    subsequent lookup fail for a reason that has nothing to do with the
    freeze.

    Returns None when the tag's commit cannot be READ here -- a shallow
    clone knows the SHA but not the objects. The caller then skips rather
    than reporting a freeze that was never actually checked.
    """
    # Prefer the local tag, peeled to its commit.
    out = _git("rev-list", "-n", "1", f"{FREEZE_TAG}^{{commit}}")
    if out is not None and out.returncode == 0 and out.stdout.strip():
        commit = out.stdout.strip()
        if _commit_is_present(commit):
            return commit
        return None

    # Not in this checkout. It may still be on the remote -- a shallow clone
    # has no ancestor tags. Look there, but a remote SHA alone is not
    # enough: without the objects, the freeze still cannot be checked.
    ls = _git("ls-remote", "--tags", "origin", f"{FREEZE_TAG}*")
    if ls is None or ls.returncode != 0:
        return None
    remote_commit = None
    for line in ls.stdout.splitlines():
        sha, _, name = line.partition("\t")
        name = name.strip()
        if name == f"refs/tags/{FREEZE_TAG}^{{}}":
            remote_commit = sha.strip()
        elif name == f"refs/tags/{FREEZE_TAG}" and remote_commit is None:
            # The tag object itself. Peel it below if we can.
            remote_commit = sha.strip()
    if remote_commit is None:
        return None
    if _commit_is_present(remote_commit):
        return remote_commit
    # The tag object may be local even when the commit is not; try peeling.
    peeled = _git("rev-parse", f"{remote_commit}^{{commit}}")
    if peeled is not None and peeled.returncode == 0 and peeled.stdout.strip():
        commit = peeled.stdout.strip()
        if _commit_is_present(commit):
            return commit
    return None


def _blob_id_at_tag(relpath: str, commit: str) -> str | None:
    """The git object ID of `relpath` at the tagged commit, or None."""
    out = _git("rev-parse", f"{commit}:{relpath}")
    if out is None or out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout.strip()


def _working_blob_id(relpath: str) -> str | None:
    """The git object ID the working-tree file *would* get if committed now.

    This applies the same clean filter the index uses, so a file that differs
    only in line endings -- which this repository's `core.autocrlf` checkout
    makes routine -- correctly compares equal to the tagged blob.
    """
    f = ROOT / relpath
    if not f.exists():
        return None
    out = _git("hash-object", "--path", relpath, str(f))
    if out is None or out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout.strip()


def _first_difference(relpath: str, commit: str) -> str:
    """A human-readable description of how the file differs, for the failure
    message. Uses git's own diff, which normalises line endings."""
    out = _git("diff", "--no-index", "--stat",
               "-", str(ROOT / relpath), timeout=30)
    # The comparison above is only a fallback; the useful one is against the
    # tag itself.
    d = _git("diff", f"{commit}", "--", relpath)
    if d is not None and d.returncode == 0 and not d.stdout.strip():
        return ""
    if d is not None and d.stdout.strip():
        lines = [l for l in d.stdout.splitlines()
                 if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
        if lines:
            return "\n    " + "\n    ".join(lines[:12])
    return ""


@pytest.fixture(scope="module")
def freeze_commit() -> str:
    commit = _tag_commit()
    if commit is None:
        pytest.skip(
            f"the archival tag {FREEZE_TAG} cannot be read from this "
            f"environment. A shallow clone knows the tag's SHA but does not "
            f"have its objects, so the freeze cannot be checked here -- this "
            f"is a skip, not a pass. Run a full clone (or `git fetch --tags`) "
            f"to check it.")
    return commit


@pytest.mark.parametrize("relpath", FROZEN_ENGINE)
def test_engine_file_is_unchanged_since_the_freeze(relpath, freeze_commit):
    """A frozen engine file must be identical to the tagged version.

    "Identical" is git's notion: the working-tree file, cleaned the way the
    index would clean it, must have the same object ID as the blob recorded
    in the tag. A file nobody touched therefore passes, and a file that was
    edited fails.
    """
    tagged = _blob_id_at_tag(relpath, freeze_commit)
    working = _working_blob_id(relpath)

    if tagged is None:
        # The file is absent at the tagged commit. That is either real
        # breakage, or the commit's objects are not readable here. The
        # fixture already established that the commit is present, so a
        # missing path at a present commit IS a disagreement.
        pytest.fail(
            f"{relpath} does not exist at {FREEZE_TAG} ({freeze_commit[:12]}). "
            f"The freeze reference and the repository disagree about what the "
            f"engine is.")

    assert working is not None, (
        f"{relpath} has been deleted. Organica 1 is frozen; restoring the "
        f"file is the fix, not amending the freeze.")

    if tagged == working:
        return

    detail = _first_difference(relpath, freeze_commit)
    pytest.fail(
        f"{relpath} has changed since Organica 1 was frozen at {FREEZE_TAG} "
        f"({freeze_commit[:12]}).{detail}\n\n"
        f"Organica 1 is a fixed reference object: everything after it "
        f"MEASURES the engine, and nothing after it changes it quietly.\n"
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
    tagged = _blob_id_at_tag(relpath, freeze_commit)
    if tagged is None:
        # Not present at the tag: the artifact was produced after the freeze,
        # or is gitignored. Either way there is nothing to compare.
        pytest.skip(f"{relpath} does not exist at {FREEZE_TAG}; nothing to compare.")

    working = _working_blob_id(relpath)
    assert working is not None, (
        f"{relpath} has been deleted. It is a published result. If it is "
        f"withdrawn, record that as a documented correction rather than "
        f"removing it.")

    if tagged != working:
        detail = _first_difference(relpath, freeze_commit)
        pytest.fail(
            f"{relpath} has changed since Organica 1 was frozen at "
            f"{FREEZE_TAG} ({freeze_commit[:12]}).{detail}\n\n"
            f"It is a published result. Corrections are documented, not "
            f"quietly applied: add the correction to the journal and the "
            f"facts sheet, point at the section that supersedes the old "
            f"number, and leave the artifact alone.")


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
