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
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import audit_trace_probe as probe  # noqa: E402

#: 0.16.0 admits a prediction only after a pair co-occurs 35 times, so 8 cycles
#: formed no belief at all and every check below passed on an empty denominator.
#: 40 keeps ~11 cycles with beliefs and 12 rank losses — the smallest arm measured
#: that stays live — so a break below has something to break.
CYCLES = 40
STRESS_CAP = 5


def test_probe_reconstructs_the_engine_decision():
    """The auditor reproduces the engine's retained set, exactly."""
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    assert result["summary"]["cycles_with_beliefs"] > 0, "no beliefs formed; test is vacuous"
    assert result["A1_evidence_replay_aggregate"]["pass"], result["A1_evidence_replay_aggregate"]
    assert result["A2_selection_reconstruction"]["pass"], result["A2_selection_reconstruction"]
    assert result["A7_event_level_attribution"]["pass"], result["A7_event_level_attribution"]
    assert result["A5_field_honesty"]["pass"], result["A5_field_honesty"]
    assert result["A6_trace_counterfactual_separation"]["pass"], result["A6_trace_counterfactual_separation"]
    assert result["A5_field_honesty"]["records_checked"] > 0, "no trace records rendered for A5"
    assert result["A6_trace_counterfactual_separation"]["records_checked"] > 0, "no trace records rendered for A6"
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
    result = probe.run(cycles=CYCLES, seed=20261025, force_tie=True)
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
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
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
    check = result["A2_selection_reconstruction"]
    assert check["cycles_checked"] > 0, (
        "the arm reconstructed no selection, so the failure would not be attributable")
    assert check["cycles_failing"] > 0, (
        "the check failed with no cycle attributable to the broken auditor")
    assert not check["pass"], (
        "the reconstruction check passed with a broken auditor — "
        "the check cannot fail, so it is decoration"
    )


def test_a_wrong_auditor_is_caught_on_the_evidence_axis(monkeypatch):
    """A wrong support count must make the aggregate evidence check fail."""
    original = probe._temporal_graph

    def broken(mem):
        graph = original(mem)
        # Drop the busiest source tag rather than a fixed name: "amber" need not
        # appear in this arm's graph at all, and a break that changes no count
        # tests nothing. The busiest tag is guaranteed to carry edges.
        victim = max(graph, key=lambda tag: (sum(graph[tag].values()), tag))
        return {k: {kk: vv for kk, vv in v.items() if k != victim}
                for k, v in graph.items()}

    monkeypatch.setattr(probe, "_temporal_graph", broken)
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    check = result["A1_evidence_replay_aggregate"]
    assert check["beliefs_checked"] > 0, (
        "the arm formed no belief to replay, so the failure would not be attributable")
    assert check["cycles_failing"] > 0, (
        "the check failed with no cycle attributable to the broken count")
    assert not check["pass"], (
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
    assert result["A7_event_level_attribution"]["cycles_failing"] > 0, (
        "no cycle attributed anything wrong, so the failure would not be attributable")
    assert not result["A7_event_level_attribution"]["pass"], (
        "the attribution reconciliation passed with an observer that "
        "over-attributes — the check cannot fail, so it is decoration"
    )


def test_a5_field_honesty_fails_on_mislabelled_count(monkeypatch):
    """A rendered record calling competing flow 'contradictory observations' must fail A5."""
    original_render = probe.render_trace_record

    def dishonest_render(*args, **kwargs):
        rec = original_render(*args, **kwargs)
        rec["rendered_text"] += "\nEvidence: 4 contradictory observations"
        return rec

    monkeypatch.setattr(probe, "render_trace_record", dishonest_render)
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    check = result["A5_field_honesty"]
    assert check["records_checked"] > 0, (
        "no trace record was rendered, so A5 audited nothing")
    assert not check["pass"], (
        "A5 field honesty passed with 'contradictory observations' in record — check cannot fail!"
    )
    assert len(check["errors"]) > 0


def test_a6_counterfactual_separation_fails_on_counterfactual_field(monkeypatch):
    """A trace containing a counterfactual claim must fail A6."""
    original_render = probe.render_trace_record

    def counterfactual_render(*args, **kwargs):
        rec = original_render(*args, **kwargs)
        rec["would_have_survived_without_competing"] = True
        rec["rendered_text"] += "\nNote: candidate would_have_survived under replay_without competitor"
        return rec

    monkeypatch.setattr(probe, "render_trace_record", counterfactual_render)
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    check = result["A6_trace_counterfactual_separation"]
    assert check["records_checked"] > 0, (
        "no trace record was rendered, so A6 audited nothing")
    assert not check["pass"], (
        "A6 counterfactual check passed with counterfactual claim — check cannot fail!"
    )
    assert len(check["errors"]) > 0
