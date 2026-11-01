"""Regression guards for the cycle base both divergence instruments read.

The candidate-membership audit stores its divergence cycle as a **zero-based
index** into ``c_cycle_digests``.  Both instruments that consume it number
cycles from one, and both, as first shipped, read that index as if it were a
cycle.  These tests are written to fail on the old code: they assert the
one-based reading, not merely that some number is returned.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks"))

import divergence_cycle_capture as dcc
import divergence_mechanism as dm


def test_capture_reads_the_divergence_cycle_and_the_one_before_it():
    """The audit's index 11 denotes engine cycles 12 and 11, not 11 and 10."""
    assert dcc.capture_cycles(11) == (12, 11)


def test_capture_uses_the_same_base_as_the_mechanism_instrument():
    for index in (1, 2, 5, 11):
        divergence, previous = dcc.capture_cycles(index)
        assert divergence == dm.divergence_cycle(index)
        assert previous == divergence - 1


def test_capture_refuses_a_divergence_at_the_first_cycle():
    for bad in (0, -1):
        try:
            dcc.capture_cycles(bad)
        except ValueError:
            continue
        raise AssertionError("capture_cycles(%r) must refuse" % (bad,))


def test_mechanism_divergence_cycle_is_one_based():
    assert dm.divergence_cycle(11) == 12
    assert dm.divergence_cycle(0) == 1


def test_reproduction_field_can_be_false():
    """The field that replaced the tautology must be able to return False."""
    assert dm.audit_cycle_reproduced(11, 12) is True
    assert dm.audit_cycle_reproduced(11, 11) is False
    assert dm.audit_cycle_reproduced(11, 13) is False
    assert dm.audit_cycle_reproduced(11, None) is None


def test_the_tautological_field_is_gone():
    src = (REPO / "benchmarks/divergence_mechanism.py").read_text(encoding="utf-8")
    # The field, not the word: the replacement helper explains the old name.
    assert '"admitted_same_at_divergence":' not in src


def test_a_refused_window_is_not_an_empty_pool():
    """An unaddressed window is not measured, never an empty pool."""
    assert dcc.pool_identity([], [], False) == (None, None)
    assert dcc.pool_identity([], [], True) == (True, True)
    assert dcc.pool_identity(["a"], ["b"], True) == (False, False)
