"""The pressure test's figures must come from the artifact, not from a typist."""
from benchmarks import assertion_provenance_pressure_test as pressure

LAYER = "static"


def test_the_pressure_test_figures_match_the_phase_k_artifact():
    assert pressure.main(["--check"]) == 0


def test_the_figure_checker_can_fail():
    assert pressure.main(["--self-test"]) == 0
