"""
tests/test_v1_freeze.py
------------------------------------------------------------------
The freeze, in the two parts it actually has.

**Part 1 -- the published artifacts are immutable.** Organica 1's published results are compared with
the archival tag `v0.9.0` and fail if edited in place. Corrections are documented, not applied.

**Part 2 -- the engine is pinned, not archived.** The engine on master is supposed to move, so its
identity is enforced by `docs/engine_pin.json` and `benchmarks/engine_pin.py`: a SHA-256 for every
module under `organica/`, and a `--check` that fails when a module is added, removed or changed
without the version bump that records the change. This file asserts the pin passes, that it covers
the seven files `AGENTS.md` rule 12 names, and that its comparator can report a change in one of
them -- so a pin that silently shrank, or a check that cannot fire, cannot be read as a passing
freeze.

**Why not one guard against the tag.** The original test compared the seven frozen files with
`v0.9.0` and skipped itself at package version 0.12.0 and above. Between those two facts it stopped
checking anything: the engine gained six modules and lost 1,777 lines of `sleep.py` while the test
reported success by declining to look. A guard pinned to an archive can only fail or be switched off;
a guard pinned to recorded bytes fails only on an *unrecorded* change. `docs/ENGINE-VERSION-AUDIT.md`
records that history, and `tests/test_engine_pin.py` owns the pin's own behaviour.

Run:  python -m pytest tests/test_v1_freeze.py -v
"""

from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import pytest

from benchmarks import engine_pin
from organica import __version__

ROOT = Path(__file__).resolve().parent.parent

#: The archival tag. Organica 1 is frozen as of this commit, for the published record.
FREEZE_TAG = "v0.9.0"

#: The seven files rule 12 names as the engine. The pin must cover at least these.
FROZEN_ENGINE = (
    "organica/sleep.py",
    "organica/memory.py",
    "organica/paths.py",
    "organica/streams.py",
    "organica/branch_streams.py",
    "organica/scale_streams.py",
    "organica/ground_truth_worlds.py",
)

#: The published artifacts. A frozen architecture whose results could drift is not frozen at all.
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
    """Is this commit's object actually in this checkout's object store?"""
    out = _git("cat-file", "-e", commit + "^{commit}")
    return out is not None and out.returncode == 0


def _tag_commit():
    """The commit the archival tag points at, or None if it cannot be read here."""
    out = _git("rev-list", "-n", "1", FREEZE_TAG + "^{commit}")
    if out is None or out.returncode != 0 or not out.stdout.strip():
        return None
    commit = out.stdout.strip()
    return commit if _commit_is_present(commit) else None


def _blob_id_at(relpath: str, commit: str):
    out = _git("rev-parse", commit + ":" + relpath)
    if out is None or out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout.strip()


def _working_blob_id(relpath: str):
    """The object ID the working-tree file would get if committed now."""
    f = ROOT / relpath
    if not f.exists():
        return None
    out = _git("hash-object", "--path", relpath, str(f))
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


def test_the_engine_pin_describes_the_engine():
    """The engine's identity is the pin's job, and the pin must currently hold."""
    problems = engine_pin.compare(engine_pin.load_pin())
    assert problems == [], problems


def test_the_pin_covers_the_engine_this_record_freezes():
    """A pin that quietly stopped covering a frozen file would be a freeze that stopped."""
    pin = engine_pin.load_pin()
    missing = sorted(set(FROZEN_ENGINE) - set(pin["files"]))
    assert not missing, (
        "docs/engine_pin.json does not cover " + repr(missing) + ", so a change to it would not be "
        "caught. Re-pin with python -m benchmarks.engine_pin.")
    assert pin["version"] == __version__, (
        "the pin records version " + str(pin["version"]) + " but the package declares " + __version__ +
        "; a version bump is a deliberate act and the pin records it.")
    assert pin.get("pinned") and pin.get("head_at_pin"), "the pin must say when and where it was taken"


def test_the_pin_comparator_reports_a_change_in_a_frozen_file():
    """Not vacuous: the comparison this file relies on must separate a changed frozen file."""
    pin = copy.deepcopy(engine_pin.load_pin())
    name = "organica/sleep.py"
    now = dict(pin["files"])
    now[name] = "0" * 64
    found = engine_pin.compare(pin, now=now, version=pin["version"])
    assert any(name in message for message in found), found


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
