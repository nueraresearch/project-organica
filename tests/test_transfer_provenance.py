"""Q028's instrument must exist, and must be able to fail, before the run.

The pre-registration for the campaign does not exist yet, so what is testable now
is the trace itself: that each leg is read, that removing a leg changes the
answer, that a zero denominator is not reported as a zero share, and that the
control set rejects a tracer which always says "resolved".
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import transfer_provenance as tp  # noqa: E402


def test_a_complete_chain_resolves():
    fixture = tp._fixtures()["resolved"]
    got = tp.trace_transfer(fixture["transfer"], fixture["roles"],
                            fixture["events"], fixture["snapshot"])
    assert got["status"] == tp.RESOLVED
    assert got["role_id"] == "role_1"
    assert got["events"] == ["B:0:1", "B:0:2"]
    assert got["priming"] == "schema_7"


def test_each_missing_leg_has_its_own_reason():
    expected = {
        "no_role": "unresolved_no_role",
        "no_events": "unresolved_missing_events",
        "no_priming": "unresolved_no_priming",
        "missing_row": "unresolved_missing_structure",
    }
    for name, status in expected.items():
        fixture = tp._fixtures()[name]
        got = tp.trace_transfer(fixture["transfer"], fixture["roles"],
                                fixture["events"], fixture["snapshot"])
        assert got["status"] == status, name
        assert got["reason"], name


def test_removing_a_leg_from_a_resolved_chain_changes_the_answer():
    base = tp._fixtures()["resolved"]
    cases = [
        (base["transfer"], [], base["events"], "unresolved_no_role"),
        (base["transfer"], base["roles"], [], "unresolved_missing_events"),
        ({**base["transfer"], "schema_prior": None}, base["roles"], base["events"],
         "unresolved_no_priming"),
    ]
    for transfer, roles, events, status in cases:
        got = tp.trace_transfer(transfer, roles, events, base["snapshot"])
        assert got["status"] == status


def test_an_empty_denominator_is_not_a_zero_share():
    summary = tp.summarise([])
    assert summary["measurable"] is False
    assert summary["share"] is None
    assert summary["not_measurable_reason"]


def test_a_zero_share_with_a_denominator_is_measurable():
    trace = {"status": "unresolved_no_role"}
    summary = tp.summarise([trace, trace])
    assert summary["measurable"] is True
    assert summary["denominator"] == 2
    assert summary["share"] == 0.0
    assert summary["unresolved"] == 2


def test_every_status_is_counted_apart():
    traces = [{"status": s} for s in tp.STATUSES]
    summary = tp.summarise(traces)
    assert summary["denominator"] == len(tp.STATUSES)
    assert sum(summary["statuses"].values()) == len(tp.STATUSES)
    assert summary["resolved"] == 1


def test_the_controls_reject_a_tracer_that_always_resolves():
    report = tp.compare_to_expected(tp.always_resolved)
    assert report["passed"] is False
    assert "role_removed_flips" in report["failures"]
    assert "no_role" in report["failures"]


def test_the_shipped_instrument_passes_its_own_controls():
    result = tp.self_test()
    assert result["all_passed"] is True
    assert result["comparator_rejects_a_broken_tracer"] is True


def test_the_cli_exits_zero_on_a_passing_self_test():
    assert tp.main(["--self-test"]) == 0


def test_the_cli_exits_non_zero_when_the_tracer_is_broken(monkeypatch):
    monkeypatch.setattr(tp, "trace_transfer", tp.always_resolved)
    assert tp.main(["--self-test"]) == 1


# ---------------------------------------------------------------------------
# The pair resolver (P0): schema_prior -> schema row -> source_role_id,
# target_role_id -> the two role rows -> the pair in the schema's direction.
# ---------------------------------------------------------------------------

def _pair_trace(name):
    fixture = tp._pair_fixtures()[name]
    return tp.trace_transfer_pair(fixture["transfer"], fixture["schemas"],
                                  fixture["roles"], fixture["events"],
                                  fixture["snapshot"])


def test_a_schema_primed_pair_resolves_to_its_role_pair():
    got = _pair_trace("pair_resolved")
    assert got["status"] == tp.PAIR_RESOLVED
    assert got["schema_id"] == "schema_7"
    assert got["role_pair"] == ["role_geometry", "role_motion"]
    assert got["events"] == ["B:0:1", "B:0:2"]


def test_each_pair_leg_has_its_own_status():
    expected = {
        "pair_no_priming": "unresolved_no_priming",
        "pair_no_schema": "unresolved_no_schema",
        "pair_schema_without_roles": "unresolved_schema_without_roles",
        "pair_missing_role": "unresolved_missing_role",
        "pair_reversed": "unresolved_pair_not_in_roles",
        "pair_no_events": "unresolved_missing_events",
        "pair_missing_row": "unresolved_missing_structure",
    }
    for name, status in expected.items():
        got = _pair_trace(name)
        assert got["status"] == status, name
        assert got["reason"], name


def test_the_pair_resolver_reads_both_role_ids_and_the_direction():
    base = tp._pair_fixtures()["pair_resolved"]
    reversed_pair = {"id": "pred_1", "source": "amber", "target": "willow",
                     "schema_prior": "schema_7"}
    got = tp.trace_transfer_pair(reversed_pair, base["schemas"], base["roles"],
                                 [{"id": "B:9:1", "tags": ["amber", "willow"]}],
                                 base["snapshot"])
    assert got["status"] == "unresolved_pair_not_in_roles"
    assert got["role_pair"] == ["role_geometry", "role_motion"]


def test_the_pair_controls_pass_and_reject_a_tracer_that_always_resolves():
    report = tp.run_pair_controls()
    assert report["all_passed"] is True
    broken = tp.compare_to_expected(tp.always_resolved_pair, controls=tp.run_pair_controls)
    assert broken["passed"] is False
    assert "pair_schema_removed_flips" in broken["failures"]


def test_the_self_test_covers_both_resolvers():
    result = tp.self_test()
    assert result["all_passed"] is True
    assert result["pair_controls"]["all_passed"] is True
    assert result["pair_comparator_rejects_a_broken_tracer"] is True
