"""The audit-trace probe must be able to fail.

`benchmarks/audit_trace_probe.py` claims that an outside auditor can
reconstruct the engine's selection contest exactly, and that every temporal
edge resolves to the concrete events that produced it.  Those claims are only
worth anything if the checks can go red, so this test breaks the auditor on
purpose and requires the checks to notice.

Three breaks, one per axis:

  * the curiosity term zeroed   -> the ranking changes  -> A2 must fail
  * a tag dropped from the graph -> the counts change    -> A1 must fail
  * the sleep-event guard lifted -> extra transitions are attributed
                                                          -> A7 must fail

The last one matters: the observer must mirror the engine's own guard
(`if event_type != "sleep"`), and the only way to know it does is to remove it
and watch the reconciliation break.

Reference: docs/AUDIT-TRACE-SPEC.md, acceptance criteria A1, A2, A4, A7.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import audit_trace_probe as probe  # noqa: E402

CYCLES = 8
STRESS_CAP = 5


def test_probe_reconstructs_the_engine_decision():
    """The auditor reproduces the engine's retained set, exactly."""
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    assert result["summary"]["cycles_with_beliefs"] > 0, "no beliefs formed; test is vacuous"
    assert result["A1_evidence_replay_aggregate"]["pass"], result["A1_evidence_replay_aggregate"]
    assert result["A2_selection_reconstruction"]["pass"], result["A2_selection_reconstruction"]
    assert result["A7_event_level_attribution"]["pass"], result["A7_event_level_attribution"]
    # the stress arm must actually exercise the "lost on rank" branch,
    # otherwise the reconstruction check is not testing what it claims to.
    assert result["summary"]["total_lost"] > 0, "stress arm never lost a candidate"


def test_observer_does_not_change_the_engine():
    """A4 — recording the trace must leave the engine's outputs unchanged."""
    result = probe.run_invariance(cycles=6, seed=20261025)
    assert result["A4_behaviour_invariance"]["pass"], result["A4_behaviour_invariance"]


def test_forced_timestamp_ties_are_reproduced():
    """The engine's lookback query has no tie-breaker; the observer must
    still reproduce the engine's choice when timestamps collide."""
    result = probe.run(cycles=8, seed=20261025, force_tie=True)
    ties = result["A7_event_level_attribution"]["timestamp_ties"]
    assert ties["stores_with_tied_window"] > 0, (
        "the forced-tie arm produced no tied windows — the tie case was not "
        "actually exercised, so the check is vacuous"
    )
    assert result["A7_event_level_attribution"]["pass"], result["A7_event_level_attribution"]


def test_distinct_evidence_is_deduplicated():
    """The distinct-evidence view must count each transition once.

    The support-reference view is a weighted sum over belief-by-cycle
    snapshots, so it counts the same transition again in every later cycle
    where the belief is still reported. The distinct view must not.
    """
    result = probe.run(cycles=8, seed=20261025, max_hypotheses=STRESS_CAP)
    a7 = result["A7_event_level_attribution"]
    distinct = a7["distinct_evidence"]
    references = a7["support_references"]
    assert distinct["total_transitions"] > 0
    assert references["total"] >= distinct["total_transitions"], (
        "the support-reference view must count at least as many references as "
        "there are distinct transitions"
    )
    # a dedup bug would make the distinct total equal the reference total
    assert distinct["total_transitions"] < references["total"], (
        "the distinct view equals the weighted view — it is not deduplicating"
    )
    assert (distinct["self_sourced"] + distinct["world_sourced"]
            == distinct["total_transitions"])
    assert (references["self_sourced"] + references["world_sourced"]
            == references["total"])


def test_a_wrong_auditor_is_caught(monkeypatch):
    """A deliberately wrong auditor must make the selection check fail."""
    monkeypatch.setattr(probe, "_subject_entropy", lambda subject, temporal: 0.0)
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    assert not result["A2_selection_reconstruction"]["pass"], (
        "the reconstruction check passed with a broken auditor — "
        "the check cannot fail, so it is decoration"
    )


def test_a_wrong_auditor_is_caught_on_the_evidence_axis(monkeypatch):
    """A wrong support count must make the aggregate evidence check fail."""
    original = probe._temporal_graph

    def broken(mem):
        graph = original(mem)
        return {k: {kk: vv for kk, vv in v.items() if kk != "amber"}
                for k, v in graph.items()}

    monkeypatch.setattr(probe, "_temporal_graph", broken)
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    assert not result["A1_evidence_replay_aggregate"]["pass"], (
        "the evidence replay passed with a broken count — "
        "the check cannot fail, so it is decoration"
    )


def test_a_wrong_observer_is_caught_on_the_attribution_axis(monkeypatch):
    """Attributing sleep-event transitions must break the reconciliation.

    The engine records graph edges only for world events.  An observer that
    lifts that guard attributes transitions the engine never made, and the
    attributed totals stop matching the aggregate table.  This is the check
    that keeps the observer honest.
    """
    original_store = probe.ObservingMemoryService.store

    def sloppy_store(self, content, event_type="observe", source="env"):
        # same as the observer, but WITHOUT the engine's sleep-event guard
        event = original_store(self, content, event_type=event_type, source=source)
        if event_type == "sleep":
            rows = self._conn.execute(
                "SELECT id, time, event_type, tags, rowid FROM events "
                "ORDER BY time DESC LIMIT 3"
            ).fetchall()
            for prior_id, _t, prior_type, prior_tags, _rowid in rows:
                for tag_from in (prior_tags or "").split(","):
                    if not tag_from:
                        continue
                    for tag_to in event.tags:
                        if tag_from != tag_to:
                            self.attribution.setdefault((tag_from, tag_to), []).append(
                                (prior_id, prior_type, event.id)
                            )
        return event

    monkeypatch.setattr(probe.ObservingMemoryService, "store", sloppy_store)
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    assert not result["A7_event_level_attribution"]["pass"], (
        "the attribution reconciliation passed with an observer that "
        "over-attributes — the check cannot fail, so it is decoration"
    )
