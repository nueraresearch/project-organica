"""
tests/test_versioning.py
------------------------------------------------------------------
Keep the three version declarations from drifting apart, and keep the
version itself honest.

The repository declares a version in three places:

  * `organica.__version__`      -- the single source of truth
  * `pyproject.toml`            -- what pip installs
  * `CITATION.cff`              -- what a reader cites

They disagreed once already (`pyproject.toml` said 0.1.0 while
`CITATION.cff` said 0.5.0), and a reader who cited one and installed the
other would have had no way to tell. These tests make that impossible.

They also pin the SemVer 2 rules this project relies on: the version is
well-formed, and the project is **pre-1.0**, which is what makes the
"the public API is not stable yet" promise honest.

**The version has to describe this commit.** Two failure modes are
covered, and both have happened here:

  1. *A version was claimed but never published.* The changelog says
     0.8.0 is released, but there is no `v0.8.0` tag, so nobody can
     check out what the changelog describes.
  2. *The version was left behind.* The changelog and the code still say
     0.7.0, but `v0.7.0` was tagged at an earlier commit and master has
     moved on. The version then names a release that master is not, and
     anyone installing from master gets a different artifact under the
     same number.

Rule 2 is why a version bump is required after a release, and why the
bump is enough: an *unreleased* version (the changelog heading says
"(unreleased)") is allowed to have no tag, because there is nothing to
check out yet.

Run:  python -m pytest tests/test_versioning.py -v
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import organica  # noqa: E402

SEMVER = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z.-]+))?$")

UNRELEASED_MARKER = "unreleased"


def _pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    assert m, "no version found in pyproject.toml"
    return m.group(1)


def _citation_version() -> str:
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    m = re.search(r"^version:\s*(\S+)\s*$", text, re.M)
    assert m, "no version found in CITATION.cff"
    return m.group(1).strip('"')


def _git(*args: str, timeout: int = 30):
    """Run a git command. Returns the CompletedProcess, or None if git is
    unusable here."""
    import subprocess
    try:
        return subprocess.run(["git", *args], cwd=str(ROOT),
                              capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None


def _changelog_heading(version: str) -> str:
    """The text of this version's changelog heading, or '' if there is none."""
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(rf"^##\s+\[?{re.escape(version)}\]?(.*)$", changelog, re.M)
    return m.group(1).strip() if m else ""


def _is_shallow_clone() -> bool:
    """True when this checkout was made with `git clone --depth N`."""
    return (ROOT / ".git" / "shallow").exists()


def _local_tag_commit(tag: str) -> str | None:
    """The commit a local tag points at, or None if the tag is not here."""
    out = _git("tag", "-l", tag)
    if out is None or out.returncode != 0 or not out.stdout.strip():
        return None
    rev = _git("rev-list", "-n", "1", tag)
    if rev is None or rev.returncode != 0:
        return None
    return rev.stdout.strip() or None


def _remote_ref(ref: str) -> str | None:
    """A ref's commit on `origin`, or None if the remote has no such ref."""
    out = _git("ls-remote", "--tags", "origin", ref, timeout=60)
    if out is None or out.returncode != 0:
        return None
    peeled = plain = None
    for line in out.stdout.splitlines():
        sha, _, name = line.partition("\t")
        name = name.strip()
        if name == "refs/tags/" + ref + "^{}":
            peeled = sha
        elif name == f"refs/tags/{ref}":
            plain = sha
    return peeled or plain or None


def _remote_master() -> str | None:
    """The tip of `origin/master`, or None if it cannot be read."""
    out = _git("ls-remote", "origin", "refs/heads/master", timeout=60)
    if out is None or out.returncode != 0:
        return None
    for line in out.stdout.splitlines():
        sha, _, name = line.partition("\t")
        if name.strip() == "refs/heads/master":
            return sha.strip()
    return None


def test_version_is_semver_2():
    assert SEMVER.match(organica.__version__), (
        f"{organica.__version__!r} is not a Semantic Versioning 2.0.0 string")


def test_version_is_pre_1_0():
    """The project promises an unstable public API; that promise is only
    honest while the major version is 0."""
    major = int(SEMVER.match(organica.__version__).group("major"))
    assert major == 0, (
        "the package has reached 1.0.0, which declares the public API "
        "stable. If that is intended, the stability promise has to be "
        "made explicitly and the API audited first.")


def test_all_three_declarations_agree():
    versions = {
        "organica.__version__": organica.__version__,
        "pyproject.toml": _pyproject_version(),
        "CITATION.cff": _citation_version(),
    }
    assert len(set(versions.values())) == 1, (
        f"the version declarations disagree: {versions}")


def test_version_has_a_changelog_entry():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert re.search(rf"^##\s+\[?{re.escape(organica.__version__)}\]?",
                     changelog, re.M), (
        f"CHANGELOG.md has no entry for {organica.__version__}")


def test_a_released_version_is_checkable():
    """The version must describe *this* commit, and if it is published it
    must be checkable.

    The witness has to be the right one, or the test lies. A local tag
    list is the obvious witness, but it is *absent by construction* in a
    shallow clone: `git clone --depth 1` fetches only tags pointing at the
    commit it fetched, so a release tag on an ancestor commit (which is
    what every release tag is, once you have made a commit after tagging)
    is missing locally even though it exists on the remote.

    `benchmarks/clone_check.py` clones exactly that way, so the check it
    runs has to consult the remote. And the remote is the more faithful
    witness anyway: the question is not "is the tag in this checkout", it
    is "can a stranger check this version out", and a stranger fetches
    from the remote.
    """
    version = organica.__version__
    tag = f"v{version}"
    heading = _changelog_heading(version)
    released = bool(heading) and UNRELEASED_MARKER not in heading.lower()

    local_commit = _local_tag_commit(tag)
    if local_commit is not None:
        head = _git("rev-parse", "HEAD")
        head = head.stdout.strip() if head and head.returncode == 0 else ""
        assert local_commit == head, (
            f"version {version} is tagged at {local_commit[:12]} but this "
            f"commit is {head[:12]}. The version number is describing a "
            f"release that this commit is not. Bump the version, or move "
            f"the tag to this commit if this commit *is* the release.")
        return

    # No local tag. Either the version was never published (legitimate on a
    # working branch between releases), or this is a shallow clone and the
    # tag is on the remote.
    remote_commit = _remote_ref(tag)
    if remote_commit is None:
        if released:
            # The changelog claims this version is released, but there is no
            # tag anywhere for it: nobody can check out what it describes.
            out = _git("ls-remote", "--tags", "origin", tag, timeout=60)
            if out is None or out.returncode != 0:
                pytest.skip("the remote is not reachable from this environment")
            pytest.fail(
                f"CHANGELOG.md presents {version} as released, but there is "
                f"no git tag '{tag}'. A released version must be "
                f"checkable.")
        # Unreleased version, nothing published yet. Nothing to check.
        return

    # The tag exists on the remote. In a shallow clone we cannot see it
    # locally, so compare it against the remote's master tip.
    remote_head = _remote_master()
    if remote_head is None:
        pytest.skip("the remote is not reachable from this environment")
    assert remote_commit == remote_head, (
        f"version {version} is published at {remote_commit[:12]} but the "
        f"remote master is at {remote_head[:12]}. The version number is "
        f"describing a release that master is not. Bump the version.")


def test_versioning_is_documented():
    """The three version namespaces must be written down somewhere a
    reader will find, because 'v1' and 'v2' appear in several senses in
    this repository."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    manual = (ROOT / "docs" / "USER-MANUAL.md").read_text(encoding="utf-8")
    assert "Organica 1" in readme or "architecture generation" in readme.lower(), (
        "README.md does not say which 'v1' the architecture refers to")
    assert "SemVer" in manual or "Semantic Versioning" in manual, (
        "the manual does not state the versioning scheme")
