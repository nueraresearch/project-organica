"""The C6 block guard must run in the local suite, not only in CI."""

LAYER = "synthetic"  # guard --check runs the observer's synthetic self-test

from benchmarks import c6_timing_guard as guard


def test_the_committed_block_passes_the_guard():
    assert guard.main(["--check"]) == 0


def test_the_guard_rejects_its_tamper_cases():
    assert guard.main(["--self-test"]) == 0
