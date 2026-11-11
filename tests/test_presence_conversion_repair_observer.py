"""N2 on a fixture: the repaired observer must change nothing except what it records.

The block's gate is behavioural, not just "the served list is equal". So this module runs three
arms on one fixture world -- the untouched engine, the observer without its second call, and the
observer with it -- and requires:

    served equality     the on arm's windows equal the untouched engine's, in order;
    next-cycle identity the off and on arms agree on every window, the asserted edges and the
                        memory rows, so the observation cannot leak into the following cycle;
    universe            the second call records the pre-cap universe, superset of what was
                        served and larger than the cap at least once.

A comparison that cannot fail is decoration, so ``test_the_comparison_can_fail`` feeds
``differs()`` a tampered arm and requires it to report the change.
"""
from __future__ import annotations
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import copy
import sys

import pytest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_conversion_repair_observer as observer  # noqa: E402


def test_the_served_window_is_the_engines_own_list():
    arms = observer.fixture()

    assert arms["on"]["windows"] == arms["plain"]["windows"]
    assert len(arms["on"]["windows"]) == observer.FIXTURE_CYCLES


def test_observation_changes_nothing_including_the_next_cycle():
    arms = observer.fixture()

    assert observer.differs(arms["off"], arms["on"]) == []
    assert arms["on"]["asserted"] == arms["off"]["asserted"]
    assert arms["on"]["store_counts"] == arms["off"]["store_counts"]


def test_the_pre_cap_universe_is_recorded_and_covers_what_was_served():
    arms = observer.fixture()
    recorded = arms["on"]["universe"]

    assert len(recorded) == observer.FIXTURE_CYCLES
    assert max(len(cycle) for cycle in recorded) > observer.SHIPPED_CAP
    served = {edge for window in arms["on"]["windows"] for edge in window}
    universe = {tuple(row["edge"]) for cycle in recorded for row in cycle}
    assert served <= universe
    assert all(row["rank"] >= 1 for cycle in recorded for row in cycle)
    assert any(row["rank"] > observer.SHIPPED_CAP for cycle in recorded for row in cycle)


def test_the_allocation_record_sums_to_the_served_window():
    arms = observer.fixture()

    assert arms["on"]["allocation"]
    for row in arms["on"]["allocation"]:
        assert row["sum_matches"] is True
        assert row["transitions"] + row["cooccurrences"] + row["unknown"] == row["served"]


def test_every_row_carries_its_relation_not_a_guess():
    """N3 needs transition/cooccurrence per row; an `unknown` label would silently pass a sum."""
    arms = observer.fixture()

    for row in arms["on"]["allocation"]:
        assert row["unknown"] == 0
    relations = {row["relation"] for cycle in arms["on"]["universe"] for row in cycle}
    assert relations == {"transition", "cooccurrence"}


def test_the_comparison_can_fail():
    arms = observer.fixture()

    assert observer.differs(arms["off"], arms["on"]) == []

    tampered = copy.deepcopy(arms["off"])
    tampered["windows"][-1] = tampered["windows"][-1][:-1]
    assert observer.differs(arms["off"], tampered) == ["windows"]

    reordered = copy.deepcopy(arms["off"])
    if len(reordered["windows"][-1]) > 1:
        reordered["windows"][-1] = list(reversed(reordered["windows"][-1]))
        assert observer.differs(arms["off"], reordered) == ["windows"]


def test_the_report_states_all_three_parts():
    report = observer.n2_report()

    assert report["served_equals_engine"] is True
    assert report["next_cycle_identical"] is True
    assert report["universe_recorded"] > observer.SHIPPED_CAP
    assert report["served_inside_universe"] is True
    assert report["allocation_sum_matches"] is True


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
    assert all(len(window) <= cap for window in arms["on"]["windows"])
    served = {edge for window in arms["on"]["windows"] for edge in window}
    universe = {tuple(row["edge"]) for cycle in arms["on"]["universe"] for row in cycle}
    assert served <= universe
    assert arms["on"]["universe"]
    assert all(row["sum_matches"] for row in arms["on"]["allocation"])


@pytest.mark.parametrize("cap", (80, 112))
def test_the_report_states_the_same_parts_at_other_caps(cap):
    report = observer.n2_report(cap=cap)
    assert report["fixture"]["cap"] == cap
    assert report["fixture"]["seed"] == observer.FIXTURE_SEED
    assert report["served_equals_engine"] is True
    assert report["next_cycle_identical"] is True
    assert report["served_inside_universe"] is True
    assert report["allocation_sum_matches"] is True


def test_the_relation_label_is_recomputed_from_the_engines_own_cooccurrence_table():
    labelling = observer.n2_report()["relation_labelling"]

    assert labelling["checked"] > 0
    assert labelling["mismatches"] == 0
    assert labelling["unlabelled"] == 0


def test_the_relation_check_can_fail_on_a_tampered_flag():
    from types import SimpleNamespace

    candidate = SimpleNamespace(source="alpha", target="beta", strength=0.5,
                                evidence={"is_cooccurrence": True, "count": 3})
    assert observer.expected_relation("alpha", "beta", {"beta": {"alpha": 2}}) == "cooccurrence"
    rows = observer.record_universe([candidate], cooc={})

    assert rows[0]["expected_relation"] == "transition"
    assert rows[0]["label_agrees"] is False


def test_the_engine_uses_one_variable_for_the_label_and_the_append_list():
    import re

    source = (REPO / "organica" / "sleep_extraction.py").read_text(encoding="utf-8")
    assert "is_cooc = tuple(sorted([tag_from, tag_to])) in cooc_pairs" in source
    assert '"is_cooccurrence": is_cooc' in source
    assert re.search(r"if is_cooc:\s*\n\s*cooccurrences\.append\(cand\)\s*\n\s*else:\s*\n"
                     r"\s*transitions\.append\(cand\)", source)
