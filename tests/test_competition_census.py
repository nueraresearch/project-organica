"""The Q052 census classifies from its cells, and refuses when its control fails.

The committed artifact's label must be the one its own data implies, and each refusal
branch must be reachable: a control that does not reproduce, a control whose mass floor
fails, an intermittent arm, and an arm that still had competition when its theory layer
died. The last two are the labels Q053's scope decision turns on, so a classifier that
could only ever return VOID would be decoration.
"""

import json

from benchmarks import competition_census as cc


def cell(**overrides) -> dict:
    base = {
        "seed": 1,
        "family": "burst_L1",
        "factor": 0.9925,
        "last_live_cycle": 10,
        "death_cycle": 11,
        "theories_at_last_live": 2,
        "theories_at_death": 0,
        "top_theory": {"subject": "alpha", "support_count": 600,
                       "competing": [{"expectation": "bravo", "support_count": 300},
                                     {"expectation": "charlie", "support_count": 300}]},
        "subjects_with_pairs_at_death": {"alpha": 2, "bravo": 2},
        "subjects_with_competing_at_death": {},
        "subjects_with_pairs_at_last_live": {"alpha": 2},
        "subjects_with_competing_at_last_live": {"alpha": 2},
        "edge_mass_at_last_live": 1000,
        "edge_mass_at_death": 950,
        "mass_ratio": 0.95,
        "retained_at_death": [],
    }
    base.update(overrides)
    return base


def control(**overrides) -> dict:
    base = {"reproduced": True, "mass_ratio": 0.95, "mass_floor_met": True,
            "last_live_cycle": 299, "death_cycle": 300,
            "subjects_with_competing_at_death": {}}
    base.update(overrides)
    return base


def test_the_committed_label_is_the_one_its_cells_imply():
    artifact = json.loads(cc.ARTIFACT.read_text(encoding="utf-8"))
    label, fired = cc.classify(artifact["cells"], artifact["control"],
                               artifact["probed"]["live_to_dead_transitions"])
    assert label == artifact["label"], (label, artifact["label"])
    assert fired["control_reproduced"] is True, (
        "the control must be reported as reproduced; the corpus comment depends on it")


def test_a_control_that_does_not_reproduce_is_void():
    label, fired = cc.classify([cell(), cell(seed=2)], control(reproduced=False), {1: 1, 2: 1})
    assert label == "VOID"
    assert fired["control_reproduced"] is False


def test_a_control_below_its_mass_floor_is_void_and_names_the_floor():
    """The branch that fired on the real block: the premise failed, not the family."""
    below = control(mass_ratio=0.578, mass_floor_met=False)
    label, fired = cc.classify([cell(), cell(seed=2)], below, {1: 1, 2: 1})
    assert label == "VOID"
    assert fired["control_mass_floor"] is False
    assert fired["competition_present"] is False, "the VOID must not be blamed on the family"


def test_two_deaths_in_the_window_are_intermittent():
    label, fired = cc.classify([cell(), cell(seed=2)], control(), {1: 2, 2: 1})
    assert fired["intermittent"] is True
    assert label == "DIFFERENT_INTERMITTENT"


def test_competition_still_present_at_death_is_a_different_failure():
    present = cell(subjects_with_competing_at_death={"bravo": 2})
    label, _ = cc.classify([present, cell(seed=2)], control(), {1: 1, 2: 1})
    assert label == "DIFFERENT_COMPETITION_PRESENT"


def test_the_same_mechanism_label_is_reachable():
    label, fired = cc.classify([cell(), cell(seed=2)], control(), {1: 1, 2: 1})
    assert label == "SAME_COMPETITION_LOSS", fired
