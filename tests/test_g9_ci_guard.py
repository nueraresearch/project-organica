"""The G9 validator CI guard must run in the local suite, not only in GitHub Actions."""

LAYER = "dry-run"  # the guard reads the workflow as text; it runs no engine

from benchmarks import g9_ci_guard as guard


def test_the_committed_workflow_passes_the_guard():
    assert guard.main(["--check"]) == 0


def test_the_guard_rejects_its_tamper_cases():
    assert guard.main(["--self-test"]) == 0
