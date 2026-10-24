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


def _is_shallow_clone() -> bool:
    """True when this checkout was made with `git clone --depth N`."""
    return (ROOT / ".git" / "shallow").exists()


def test_a_git_tag_exists_for_the_version():
    """A release without a tag is a version that cannot be checked out.

    The witness has to be the right one, or the test lies. A local tag list
    is the obvious witness, but it is *absent by construction* in a shallow
    clone: `git clone --depth 1` fetches only tags pointing at the commit it
    fetched, so a release tag on an ancestor commit (which is what every
    release tag is, once you have made a commit after tagging) is missing
    locally even though it exists on the remote.

    `benchmarks/clone_check.py` clones exactly that way, so the check it
    runs has to consult the remote. And the remote is the more faithful
    witness anyway: the question is not "is the tag in this checkout", it is
    "can a stranger check this version out", and a stranger fetches from the
    remote.
    """
    import subprocess
    tag = f"v{organica.__version__}"
    try:
        out = subprocess.run(
            ["git", "tag", "-l", tag],
            cwd=ROOT, capture_output=True, text=True, timeout=30)
    except Exception:
        pytest.skip("git is not available in this environment")
    if out.returncode != 0:
        pytest.skip("git is not usable here")
    if out.stdout.strip():
        return  # the tag is right here; no further evidence needed

    if not _is_shallow_clone():
        # A full checkout with no local tag means the tag genuinely does not
        # exist. This is the original failure, and it should keep failing.
        pytest.fail(
            f"no git tag '{tag}'. The version is declared in three files but "
            f"cannot be checked out.")

    # Shallow checkout: the local tag list cannot witness anything. Ask the
    # remote, which is what a stranger would fetch from.
    try:
        remote = subprocess.run(
            ["git", "ls-remote", "--tags", "origin", tag],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
    except Exception:
        pytest.skip("the remote is not reachable from this environment")
    if remote.returncode != 0:
        pytest.skip("the remote is not reachable from this environment")
    assert remote.stdout.strip(), (
        f"no git tag '{tag}' on the remote either. The version is declared "
        f"in three files but cannot be checked out.")


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
