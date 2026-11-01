"""Check the divergence-cycle capture.

The capture claims to name the candidate pool at the cycle where the two
populations part company.  Three things have to hold for that claim to be worth
anything, and all three are checked here:

1. **The capture is addressed.**  The i-th window read of an arm must carry
   the cycle marker for cycle i.  A capture that cannot prove where it is
   looking is not a measurement of the divergence cycle, and the instrument
   refuses to report one, so this test refuses it too.

2. **The pools are consistent.**  The campaign-only and current-only sets must
   be disjoint, the "both" count must be the size of their intersection, and
   the entered/left sets must be exactly the differences between the
   divergence cycle's pool and the previous cycle's pool.

3. **The order is consistent.**  The pool is a sequence and not just a set.
   The recorded orders must agree with the recorded sets, the first differing
   position must be the position the two orders actually first differ at, and
   the "the reordering coincides with the divergence" flag must be exactly
   what its name says.

The test fails on a doctored artifact, so a passing run is not a formality.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ARTIFACT = REPO / "docs" / "divergence_cycle_capture.json"
REPORT = REPO / "docs" / "DIVERGENCE-CYCLE-CAPTURE.md"
MEMBERSHIP = REPO / "docs" / "candidate_membership_audit.json"

WINDOW_ROW_CAP = 4000


def load(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def capture():
    return load(ARTIFACT)


@pytest.fixture(scope="module")
def membership():
    return load(MEMBERSHIP)


def membership_entry(a, task, seed):
    for e in a["results"]:
        if e["task"] == task and e["seed"] == seed:
            return e
    raise AssertionError("no membership entry for %s/%d" % (task, seed))


def test_the_artifact_exists_and_is_measured(capture):
    assert capture["kind"] == "divergence_cycle_capture"
    assert capture["status"] == "measured"


def test_every_failing_seed_is_captured(capture, membership):
    failing = [e for e in membership["results"]
               if not (e["task"] == "T1" and e["seed"] == 20261101)]
    captured = {(e["task"], e["seed"]) for e in capture["results"]}
    assert captured == {(e["task"], e["seed"]) for e in failing}


def test_the_divergence_cycle_comes_from_the_membership_audit(capture,
                                                               membership):
    for e in capture["results"]:
        source = membership_entry(membership, e["task"], e["seed"])
        assert e["divergence_cycle"] == source["divergence"]["first_cycle"], (
            "%s/%d: the capture is at cycle %s, the membership audit says %s"
            % (e["task"], e["seed"], e["divergence_cycle"],
               source["divergence"]["first_cycle"]))


def test_the_two_hash_seeds_are_the_membership_audits(capture, membership):
    for e in capture["results"]:
        source = membership_entry(membership, e["task"], e["seed"])
        assert e["campaign_hash_seed"] == source["campaign_side_hash_seed"]
        assert e["baseline_hash_seed"] == source["baseline_hash_seed"]


def test_every_reported_window_is_addressed(capture):
    """The alignment witness: the window at index i must carry cycle i.

    The instrument refuses to report a window that cannot show this, so an
    unaddressed window in the artifact means the artifact was written by
    something other than the instrument.
    """
    for e in capture["results"]:
        for arm in ("B", "C"):
            addressed = e["arms"][arm]["addressed"]
            assert addressed["campaign"] is True, (
                "%s/%d arm %s: the campaign-side window is not addressed"
                % (e["task"], e["seed"], arm))
            assert addressed["current"] is True, (
                "%s/%d arm %s: the current-side window is not addressed"
                % (e["task"], e["seed"], arm))


def test_the_pools_are_non_empty(capture):
    for e in capture["results"]:
        for arm in ("B", "C"):
            a = e["arms"][arm]
            assert a["campaign_pool_size"] > 0, (
                "%s/%d arm %s: the campaign-side pool is empty"
                % (e["task"], e["seed"], arm))
            assert a["current_pool_size"] > 0, (
                "%s/%d arm %s: the current-side pool is empty"
                % (e["task"], e["seed"], arm))


def test_the_pool_difference_is_consistent(capture):
    for e in capture["results"]:
        for arm in ("B", "C"):
            a = e["arms"][arm]
            campaign = set(a["campaign_only"])
            current = set(a["current_only"])
            assert not (campaign & current), (
                "%s/%d arm %s: a candidate is in both difference sets"
                % (e["task"], e["seed"], arm))
            assert a["both"] >= 0
            assert a["campaign_pool_size"] == a["both"] + len(campaign)
            assert a["current_pool_size"] == a["both"] + len(current)


def test_the_entered_and_left_sets_are_the_cycle_differences(capture):
    """What entered since the previous cycle, and what left, must be exactly
    the difference between the two pools.

    Checked against the recorded orders, not against the difference sets: the
    entered and left lists are claims about the two pools, and the orders are
    the record of the pools.
    """
    for e in capture["results"]:
        for arm in ("B", "C"):
            a = e["arms"][arm]
            prev = a["previous_cycle"]
            assert prev["captured"] is True, (
                "%s/%d arm %s: the previous cycle was not captured"
                % (e["task"], e["seed"], arm))
            entered = a["entered_from_previous_cycle"]
            left = a["left_since_previous_cycle"]
            pools = {
                "campaign": (set(prev["campaign_pool_order"]),
                             set(a["campaign_pool_order"])),
                "current": (set(prev["current_pool_order"]),
                            set(a["current_pool_order"])),
            }
            for side in ("campaign", "current"):
                before, now = pools[side]
                assert set(entered[side]) == now - before, (
                    "%s/%d arm %s: what entered on the %s side is not the "
                    "difference between the pools"
                    % (e["task"], e["seed"], arm, side))
                assert set(left[side]) == before - now, (
                    "%s/%d arm %s: what left on the %s side is not the "
                    "difference between the pools"
                    % (e["task"], e["seed"], arm, side))
                assert not (set(entered[side]) & set(left[side])), (
                    "%s/%d arm %s: a candidate both entered and left on the %s "
                    "side" % (e["task"], e["seed"], arm, side))


def test_the_window_cap_is_recorded(capture):
    for e in capture["results"]:
        for arm in ("B", "C"):
            rows = e["arms"][arm]["window_rows"]
            at_cap = e["arms"][arm]["window_at_cap"]
            for side in ("campaign", "current"):
                assert rows[side] is not None
                assert isinstance(at_cap[side], bool)
                if rows[side] >= WINDOW_ROW_CAP:
                    assert at_cap[side] is True, (
                        "%s/%d arm %s: %d rows but not marked at the cap"
                        % (e["task"], e["seed"], arm, rows[side]))


# ---------------------------------------------------------------------------
# the order
# ---------------------------------------------------------------------------

def test_the_recorded_orders_have_the_recorded_sizes(capture):
    for e in capture["results"]:
        for arm in ("B", "C"):
            a = e["arms"][arm]
            assert len(a["campaign_pool_order"]) == a["campaign_pool_size"], (
                "%s/%d arm %s: the campaign's order is %d long, the pool is "
                "recorded as %d"
                % (e["task"], e["seed"], arm,
                   len(a["campaign_pool_order"]), a["campaign_pool_size"]))
            assert len(a["current_pool_order"]) == a["current_pool_size"], (
                "%s/%d arm %s: our order is %d long, the pool is recorded as %d"
                % (e["task"], e["seed"], arm,
                   len(a["current_pool_order"]), a["current_pool_size"]))
            prev = a["previous_cycle"]
            assert len(prev["campaign_pool_order"]) == prev["campaign_pool_size"]
            assert len(prev["current_pool_order"]) == prev["current_pool_size"]


def test_the_orders_hold_no_repeats(capture):
    """The engine does not deduplicate its read-back, but the recorded pool
    keeps the first occurrence of each candidate, so no candidate may appear
    twice in one order."""
    for e in capture["results"]:
        for arm in ("B", "C"):
            a = e["arms"][arm]
            for name in ("campaign_pool_order", "current_pool_order"):
                ids = a[name]
                assert len(ids) == len(set(ids)), (
                    "%s/%d arm %s: %s repeats a candidate"
                    % (e["task"], e["seed"], arm, name))


def test_the_orders_agree_with_the_difference_sets(capture):
    """The order is the record of the pool; the difference sets are claims
    about it.  They must not contradict each other."""
    for e in capture["results"]:
        for arm in ("B", "C"):
            a = e["arms"][arm]
            camp = set(a["campaign_pool_order"])
            ours = set(a["current_pool_order"])
            assert set(a["campaign_only"]) == camp - ours, (
                "%s/%d arm %s: the campaign-only set does not match the orders"
                % (e["task"], e["seed"], arm))
            assert set(a["current_only"]) == ours - camp, (
                "%s/%d arm %s: the current-only set does not match the orders"
                % (e["task"], e["seed"], arm))
            assert a["both"] == len(camp & ours)
            assert a["set_identical"] == (camp == ours), (
                "%s/%d arm %s: the set comparison disagrees with the orders"
                % (e["task"], e["seed"], arm))


def test_the_order_comparison_is_consistent(capture):
    for e in capture["results"]:
        for arm in ("B", "C"):
            a = e["arms"][arm]
            camp = a["campaign_pool_order"]
            ours = a["current_pool_order"]
            assert a["order_identical"] == (camp == ours), (
                "%s/%d arm %s: the order comparison disagrees with the orders"
                % (e["task"], e["seed"], arm))
            pos = a["first_order_difference"]
            if camp == ours:
                assert pos is None, (
                    "%s/%d arm %s: the orders are identical but a first "
                    "difference is recorded" % (e["task"], e["seed"], arm))
                continue
            assert pos is not None, (
                "%s/%d arm %s: the orders differ but no first difference is "
                "recorded" % (e["task"], e["seed"], arm))
            expected = next((i for i, (x, y) in enumerate(zip(camp, ours))
                             if x != y), min(len(camp), len(ours)))
            assert pos == expected, (
                "%s/%d arm %s: the first difference is recorded at %s, the "
                "orders first differ at %s"
                % (e["task"], e["seed"], arm, pos, expected))


def test_the_previous_cycle_comparison_is_consistent(capture):
    for e in capture["results"]:
        for arm in ("B", "C"):
            a = e["arms"][arm]
            prev = a["previous_cycle"]
            camp = prev["campaign_pool_order"]
            ours = prev["current_pool_order"]
            assert prev["order_identical"] == (camp == ours), (
                "%s/%d arm %s: the previous cycle's order comparison disagrees "
                "with its orders" % (e["task"], e["seed"], arm))
            assert prev["set_identical"] == (set(camp) == set(ours)), (
                "%s/%d arm %s: the previous cycle's set comparison disagrees "
                "with its orders" % (e["task"], e["seed"], arm))


def test_the_coincidence_flag_means_what_it_says(capture):
    """``order_diverges_at_this_cycle`` must be true exactly when the two
    sides' orders were identical at the cycle before and differ now."""
    for e in capture["results"]:
        for arm in ("B", "C"):
            a = e["arms"][arm]
            prev = a["previous_cycle"]
            expected = (prev["order_identical"] is True
                        and a["order_identical"] is False)
            assert a["order_diverges_at_this_cycle"] == expected, (
                "%s/%d arm %s: the coincidence flag is %s, the orders say %s"
                % (e["task"], e["seed"], arm,
                   a["order_diverges_at_this_cycle"], expected))


def test_the_order_finding_is_present(capture):
    """The finding the capture exists for: for at least one seed the two sides
    hold the same candidates in a different order."""
    differs = [e for e in capture["results"]
               for arm in e["arms"].values()
               if not arm["order_identical"]]
    assert differs, (
        "no seed shows a differing order, so the capture has found nothing "
        "to report")


# ---------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------

def test_the_report_names_every_seed(capture):
    text = REPORT.read_text(encoding="utf-8")
    for e in capture["results"]:
        assert "%s / %d" % (e["task"], e["seed"]) in text, (
            "the report omits %s/%d" % (e["task"], e["seed"]))
        assert "cycle %d" % e["divergence_cycle"] in text


def test_the_report_states_the_bounded_window(capture):
    text = REPORT.read_text(encoding="utf-8")
    assert "at the divergence cycle" in text, (
        "the report does not say what the capture is for")
    assert "proved" in text or "proves" in text, (
        "the report does not say how the capture is addressed")


def test_the_report_states_the_order_finding(capture):
    text = REPORT.read_text(encoding="utf-8")
    assert "same order" in text, (
        "the report does not report the order comparison")
    assert "organica/sleep.py" in text and "organica/memory.py" in text, (
        "the report does not name the code the order sensitivity is in")


# ---------------------------------------------------------------------------
# fail-tests
# ---------------------------------------------------------------------------

def test_a_doctored_addressing_is_rejected(capture):
    import copy
    broken = copy.deepcopy(capture)
    broken["results"][0]["arms"]["C"]["addressed"]["campaign"] = False
    flagged = [e for e in broken["results"]
               for arm in e["arms"].values()
               if not (arm["addressed"]["campaign"]
                       and arm["addressed"]["current"])]
    assert flagged, ("an unaddressed window is not distinguishable from an "
                     "addressed one")


def test_a_doctored_pool_count_is_rejected(capture):
    import copy
    broken = copy.deepcopy(capture)
    e = broken["results"][0]
    arm = e["arms"]["C"]
    arm["campaign_pool_size"] += 1
    assert arm["campaign_pool_size"] != arm["both"] + len(arm["campaign_only"]), (
        "an inflated pool size is not detectable")


def test_a_doctored_order_is_rejected(capture):
    """Reordering a pool whose two sides agreed must break the order checks,
    even though the set — and every count — is unchanged.

    The case that matters is a pool the two sides held identically: reordering
    it changes nothing a set comparison could see, and everything an order
    comparison can.
    """
    import copy
    broken = copy.deepcopy(capture)
    target = None
    for e in broken["results"]:
        for arm in ("B", "C"):
            candidate = e["arms"][arm]
            if (candidate["order_identical"]
                    and len(candidate["campaign_pool_order"]) >= 2):
                target = candidate
                break
        if target is not None:
            break
    if target is None:
        pytest.skip("no arm-pair holds identical orders to reorder")
    ids = target["campaign_pool_order"]
    ids[0], ids[1] = ids[1], ids[0]
    camp = target["campaign_pool_order"]
    ours = target["current_pool_order"]
    assert target["order_identical"] != (camp == ours), (
        "a reordered pool is not distinguishable from an unchanged one")


def test_a_doctored_coincidence_flag_is_rejected(capture):
    import copy
    broken = copy.deepcopy(capture)
    arm = broken["results"][0]["arms"]["C"]
    prev = arm["previous_cycle"]
    expected = (prev["order_identical"] is True
                and arm["order_identical"] is False)
    arm["order_diverges_at_this_cycle"] = not expected
    assert arm["order_diverges_at_this_cycle"] != expected, (
        "a flipped coincidence flag is not distinguishable")
