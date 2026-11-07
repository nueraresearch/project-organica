"""The decay-operability measurement: arms, gate, growth report, guards.

The engine run here is 40 cycles on the matrix stimulus -- enough for the decay
arm to diverge from the no-decay arm, which is the audit that matters: an arm
comparison whose intervention never fired is not a comparison.
"""

import pytest

from benchmarks import decay_operability as do
from organica.sleep import SleepService


def _rows(n=100, theories=1, beliefs=3, mass_start=100, edges_start=10):
    return [{"cycle": i, "theories": theories, "beliefs": beliefs, "processes": 2,
             "stable": 3, "edges": edges_start + i,
             "edge_mass": mass_start + 2 * i, "db_bytes": 1000 + 5 * i}
            for i in range(n)]


def test_the_arms_differ_only_in_the_decay_factor():
    assert SleepService.TEMPORAL_DECAY_FACTOR == 0.95
    assert do.DecayOn.TEMPORAL_DECAY_FACTOR == 0.95
    assert do.DecayOff.TEMPORAL_DECAY_FACTOR == 1.0
    assert do.DecayOff.__mro__[1] is do.Arm


def test_the_decay_intervention_actually_fires():
    """Decay off must leave strictly more edge mass than decay on."""
    events = do.matrix_events()
    on = do.run_arm(0.95, 40, do.SEED, events)
    off = do.run_arm(1.0, 40, do.SEED, events)
    assert off["rows"][-1]["edge_mass"] > on["rows"][-1]["edge_mass"], (
        "the no-decay arm did not diverge; the comparison would measure nothing")


def test_liveness_is_the_decay_study_gate():
    assert do.liveness(_rows(theories=1, beliefs=3))
    dead = _rows(theories=1, beliefs=3)
    for row in dead[-10:]:
        row["theories"] = 0
    assert do.liveness(dead) is False
    thin = _rows(theories=1, beliefs=1)
    assert do.liveness(thin) is False
    assert do.liveness([]) is False


def test_growth_reports_deciles_and_rates_from_the_rows():
    out = do.growth(_rows(100))
    assert len(out["deciles"]) == 10
    assert out["deciles"][0]["cycle"] == 9
    assert out["deciles"][-1]["cycle"] == 99
    assert out["edge_mass_per_cycle"] == 2.0
    assert out["edge_mass_ratio_end_over_first"] == round((100 + 2 * 99) / 100, 3)
    assert not any("verdict" in key or "criterion" in key for key in out), \
        "growth must report, not judge"


def test_only_the_matrix_settings_may_call_themselves_protocol():
    assert do.protocol_run(3000, 20261023, "0") is True
    assert do.protocol_run(3000, 20261023, None) is False
    assert do.protocol_run(3000, 20261023, "12345") is False
    assert do.protocol_run(40, 20261023, "0") is False
    assert do.protocol_run(3000, 1, "0") is False


def test_a_pilot_may_not_be_written_under_docs():
    assert do.destination(True, None) == do.REPO / "docs" / "decay_operability.json"
    assert do.destination(False, None) == do.REPO / ".scratch" / "decay_operability.smoke.json"
    with pytest.raises(SystemExit, match="may not be written under docs"):
        do.destination(False, str(do.REPO / "docs" / "decay_operability.json"))
