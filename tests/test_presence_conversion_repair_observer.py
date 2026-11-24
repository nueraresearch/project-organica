"""N2 on a fixture: the repaired observer must change nothing except what it records.

The block's gate is behavioural, not just "the served list is equal". So this module runs three
arms on one fixture world -- the untouched engine, the observer without its second call, and the
observer with it -- and requires:

    served equality     the on arm's windows equal the untouched engine's, in order;
    next-cycle identity the off and on arms agree on every window, the asserted edges and the
                        memory rows, so the observation cannot leak into the following cycle;
    universe            the second call runs on every cycle and records the pre-cap universe.

On 0.16.0 the fixture world never reaches the within-event floor of 35, so the engine serves
nothing. That makes the window channel empty and the pre-cap universe empty -- the retirement
reason, not a pass. So the empty case is asserted as ``NOT MEASURABLE`` with its denominator
named, and the allocation/label arithmetic is proved on a synthetic served list. The inertness
comparison still has content: the assertion channel carries 92 world edges, not nothing.

A comparison that cannot fail is decoration, so ``test_the_comparison_can_fail`` feeds
``differs()`` a tampered arm and requires it to report the change.
"""
from __future__ import annotations
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_conversion_repair_observer as observer  # noqa: E402


def _retirement() -> dict:
    path = REPO / "docs" / "conversion_observer_retirement.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate(source, target, flag, count=3):
    return SimpleNamespace(source=source, target=target, strength=0.5,
                           evidence={"is_cooccurrence": flag, "count": count})


def test_the_observer_ran_every_cycle_and_the_engine_served_nothing():
    """The empty universe is a measured empty: the second call has to have happened."""
    arms = observer.fixture()
    on, off, plain = arms["on"], arms["off"], arms["plain"]

    assert len(on["allocation"]) == observer.FIXTURE_CYCLES
    assert len(on["universe"]) == observer.FIXTURE_CYCLES
    assert all(cycle == [] for cycle in on["universe"]), (
        "0.16.0 admits nothing on this fixture -- the floor is 35 and the world never "
        "reaches it -- so the emptiness is the retirement reason")
    # `observe=False` appends nothing: the off arm is a true control, not a silent copy.
    assert off["universe"] == [] and off["allocation"] == []
    assert plain["universe"] == [] and plain["allocation"] == []

    run = json.loads((REPO / "docs" / "presence_conversion_repair_run.json")
                     .read_text(encoding="utf-8"))
    assert run["stage_table"], "the 0.15.0 universe is preserved in the historical artifact"


def test_observation_changes_nothing_including_the_next_cycle():
    arms = observer.fixture()

    assert observer.differs(arms["off"], arms["on"]) == []
    assert arms["on"]["asserted"] == arms["off"]["asserted"]
    assert arms["on"]["store_counts"] == arms["off"]["store_counts"]
    # The equality above is only worth something if the compared channels are not empty.
    assert arms["on"]["asserted"], "the fixture asserted no world edge; the comparison is empty"
    assert arms["on"]["store_counts"]


def test_a_zero_denominator_is_not_reported_as_a_pass():
    """The retirement reason, stated by the report itself rather than by a doc beside it."""
    report = observer.n2_report()

    assert report["status"] == "NOT MEASURABLE"
    assert "zero denominator" in report["reason"]
    assert report["observed_cycles"] == observer.FIXTURE_CYCLES
    assert report["served_edges"] == 0
    assert report["allocation_rows"] == observer.FIXTURE_CYCLES
    assert report["allocation_served"] == 0
    assert report["allocation_sum_matches"] is None, (
        "a sum over nothing is not agreement; True here would score a zero denominator")
    assert report["served_inside_universe"] is None
    assert report["relation_labelling"]["status"] == "NOT MEASURABLE"

    rows = observer.fixture()["on"]["allocation"]
    assert rows and all(row["status"] == "NOT MEASURABLE" for row in rows)
    assert all(row["sum_matches"] is None for row in rows)


def test_the_allocation_record_sums_to_a_served_list():
    """The arithmetic is proved on a served list, since the shipped build serves none."""
    served = [_candidate("alpha", "beta", False),
              _candidate("gamma", "delta", True),
              _candidate("epsilon", "zeta", None)]
    rows = observer.record_universe(served)

    row = observer.allocation_row(served, rows)
    assert row["status"] == "MEASURED"
    assert row["served"] == 3
    assert (row["transitions"], row["cooccurrences"], row["unknown"]) == (1, 1, 1)
    assert row["sum_matches"] is True

    empty = observer.allocation_row([], [])
    assert (empty["status"], empty["sum_matches"]) == ("NOT MEASURABLE", None)

    # The sum check must be able to fail: withhold one served row's universe entry.
    short = observer.allocation_row(served, rows[:1])
    assert short["sum_matches"] is False


def test_every_row_carries_the_relation_its_table_implies():
    """Both directions: agreement is recorded, and a mismatched flag is caught."""
    agreeing = _candidate("alpha", "beta", True)
    row = observer.record_universe([agreeing], cooc={"alpha": {"beta": 4}})[0]
    assert (row["relation"], row["expected_relation"], row["label_agrees"]) == \
        ("cooccurrence", "cooccurrence", True)

    mismatched = _candidate("alpha", "beta", True)
    row = observer.record_universe([mismatched], cooc={})[0]
    assert (row["relation"], row["expected_relation"], row["label_agrees"]) == \
        ("cooccurrence", "transition", False)

    unlabelled = _candidate("alpha", "beta", None)
    row = observer.record_universe([unlabelled], cooc={"alpha": {"beta": 4}})[0]
    assert (row["relation"], row["expected_relation"], row["label_agrees"]) == \
        ("unknown", "cooccurrence", False)


def test_the_comparison_can_fail():
    """The guard takes plain records, so it survives the retirement and still has to fail."""
    left = {"windows": [["a>b"]], "asserted": [["a", "b"]], "store_counts": {"a>b": 1}}
    assert observer.differs(left, copy.deepcopy(left)) == []

    tampered = copy.deepcopy(left)
    tampered["windows"][-1] = []
    assert observer.differs(left, tampered) == ["windows"]

    ordered = {"windows": [["a>b", "b>a"]], "asserted": [], "store_counts": {}}
    reordered = {"windows": [["b>a", "a>b"]], "asserted": [], "store_counts": {}}
    assert observer.differs(ordered, reordered) == ["windows"]


def test_the_report_states_each_part_with_its_denominator():
    report = observer.n2_report()

    assert report["fixture"]["cycles"] == observer.FIXTURE_CYCLES
    assert report["status"] == "NOT MEASURABLE"
    assert report["observed_cycles"] == observer.FIXTURE_CYCLES
    assert report["universe_recorded"] == 0
    assert report["relation_labelling"]["checked"] == 0
    assert _retirement()["measurable_on_shipped_build"] is False


@pytest.mark.parametrize("seed", (observer.FIXTURE_SEED, observer.SECOND_SEED))
@pytest.mark.parametrize("cap", (80, 112))
def test_the_observer_stays_inert_away_from_the_shipped_setting(seed, cap):
    """Neutrality must not be a cap-40 coincidence: the same three-part check at 80 and 112.

    The served list is the engine's own at any cap, so a difference in any channel here would
    mean the repair depends on the shipped value rather than on the construction.
    """
    arms = observer.fixture(seed=seed, cap=cap)
    assert arms["on"]["cap"] == cap
    assert len(arms["on"]["windows"]) == observer.FIXTURE_CYCLES
    assert arms["on"]["windows"] == arms["plain"]["windows"]
    assert observer.differs(arms["off"], arms["on"]) == []
    assert arms["on"]["asserted"], "the inertness comparison would otherwise be empty"
    assert len(arms["on"]["allocation"]) == observer.FIXTURE_CYCLES
    assert sum(len(cycle) for cycle in arms["on"]["universe"]) == 0
    assert all(row["status"] == "NOT MEASURABLE" for row in arms["on"]["allocation"])
    assert all(row["sum_matches"] is None for row in arms["on"]["allocation"])


@pytest.mark.parametrize("cap", (80, 112))
def test_the_report_states_the_same_parts_at_other_caps(cap):
    report = observer.n2_report(cap=cap)

    assert report["fixture"]["cap"] == cap
    assert report["fixture"]["seed"] == observer.FIXTURE_SEED
    assert report["status"] == "NOT MEASURABLE"
    assert report["observed_cycles"] == observer.FIXTURE_CYCLES
    assert report["allocation_sum_matches"] is None
    assert report["served_inside_universe"] is None


def test_the_relation_label_is_not_measurable_on_the_shipped_build():
    labelling = observer.n2_report()["relation_labelling"]

    assert labelling["status"] == "NOT MEASURABLE"
    assert labelling["checked"] == 0
    assert labelling["mismatches"] == 0, "no row was labelled, so no mismatch can exist"
    assert "NOT MEASURABLE" in _retirement()["disposition"]


def test_the_engine_label_and_append_list_were_deleted_with_the_partition():
    """Absence alone would pass on an emptied file, so the replacement law is asserted too."""
    source = (REPO / "organica" / "sleep_extraction.py").read_text(encoding="utf-8")
    assert "is_cooc = tuple(sorted([tag_from, tag_to])) in cooc_pairs" not in source
    assert '"is_cooccurrence": is_cooc' not in source
    assert "cooccurrences.append(cand)" not in source
    assert "PREDICTION_COOCURRENCE_FLOOR = 35" in source
    assert '"is_cooccurrence": True' in source
    assert "NOT MEASURABLE" in _retirement()["disposition"]
