"""The engine-change audit has to stay checkable, or it is just prose about git.

Its reference commits, its frozen-file list and its commit count are all facts the
repository can re-derive. A typed count drifts, which is the exact failure the audit
documents, so the test recomputes rather than trusts.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import subprocess
from pathlib import Path

import pytest

from tests.test_v1_freeze import FROZEN_ENGINE, FREEZE_TAG

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "ENGINE-CHANGE-AUDIT.md"
GUARD = ROOT / "tests" / "test_v1_freeze.py"


def text() -> str:
    return DOC.read_text(encoding="utf-8")


def git(*args: str):
    try:
        out = subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    except Exception:
        return None
    return out if out.returncode == 0 else None


def test_document_exists_and_runs_nothing() -> None:
    assert DOC.exists()
    body = text().lower()
    assert "runs nothing" in body
    assert "no cells" in body


def test_it_names_the_freeze_tag_and_every_frozen_file() -> None:
    body = text()
    assert FREEZE_TAG in body
    for relpath in FROZEN_ENGINE:
        assert relpath in body, relpath


def test_pinned_commits_match_the_tags() -> None:
    body = text()
    for tag in (FREEZE_TAG, "v0.12.0"):
        out = git("rev-parse", "--short", f"{tag}^{{commit}}")
        if out is None:
            pytest.skip("git unavailable here")
        assert out.stdout.strip() in body, (tag, out.stdout.strip())


def test_engine_commit_count_is_derived_from_git() -> None:
    out = git("rev-list", "--count", f"{FREEZE_TAG}..HEAD", "--", "organica/")
    if out is None:
        pytest.skip("git unavailable here")
    count = int(out.stdout.strip())
    assert f"**{count}** commits" in text(), count


def test_the_skip_finding_is_resolved_and_the_guard_agrees() -> None:
    """The audit's central finding was that the freeze check skipped at >= 0.12.0.

    That was true when it was written, so the document keeps it; it is no longer true of the
    code, so the test asserts both halves. An audit test that demanded the defect remain
    would pin a bug in place and call it documentation.
    """
    guard = GUARD.read_text(encoding="utf-8")
    assert 'organica.__version__ >= "0.12.0"' not in guard, (
        "the version gate is back in tests/test_v1_freeze.py: the engine files would skip again, "
        "and the freeze would silently stop checking the engine (see docs/ENGINE-VERSION-AUDIT.md)")
    body = text()
    assert "0.12.0" in body
    assert "SKIPPED" in body
    assert "version gate, not a shallow clone" in body
    assert "Resolved 2026-11-08" in body, (
        "section 3 records a defect that has since been fixed and must say when it was resolved")


def test_c1_is_recorded_as_failed_not_supported() -> None:
    body = text()
    assert "FAILED as pre-registered" in body
    results = (ROOT / "docs" / "DIVERGENCE-MECHANISM-RESULTS.md").read_text(encoding="utf-8")
    assert "FAILED as pre-registered" in results
    for line in body.splitlines():
        if "C1" in line and "carrying" not in line.lower():
            assert "support within" not in line.lower(), line
