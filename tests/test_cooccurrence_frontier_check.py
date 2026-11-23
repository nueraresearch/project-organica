"""The T2 frontier figures must come from the artifact, not from a typist."""
from benchmarks import cooccurrence_frontier_check as frontier

LAYER = "static"


def test_the_frontier_figures_match_the_phase_k_artifact():
    assert frontier.main(["--check"]) == 0


def test_the_frontier_checker_can_fail():
    assert frontier.main(["--self-test"]) == 0
