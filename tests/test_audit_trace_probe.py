"""The audit-trace probe must be able to fail.

`benchmarks/audit_trace_probe.py` claims that an outside auditor can
reconstruct the engine's selection contest exactly.  That claim is only worth
anything if the check can go red, so this test breaks the auditor on purpose
and requires the check to notice.

The break is surgical: the probe's own `_subject_entropy` is replaced with a
wrong one.  The engine keeps its real implementation, so a wrong auditor must
reproduce a different retained set.  The stress arm (a tightened belief
budget) is used, because with the default budget the pool does not exceed the
cap and the ranking would not matter.

Reference: docs/AUDIT-TRACE-SPEC.md, acceptance criteria A1 and A2.
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
    assert result["A1_evidence_replay"]["pass"], result["A1_evidence_replay"]
    assert result["A2_selection_reconstruction"]["pass"], result["A2_selection_reconstruction"]
    # the stress arm must actually exercise the "lost on rank" branch,
    # otherwise the reconstruction check is not testing what it claims to.
    assert result["summary"]["total_lost"] > 0, "stress arm never lost a candidate"


def test_a_wrong_auditor_is_caught(monkeypatch):
    """A deliberately wrong auditor must make the reconstruction fail."""
    monkeypatch.setattr(probe, "_subject_entropy", lambda subject, temporal: 0.0)
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    assert not result["A2_selection_reconstruction"]["pass"], (
        "the reconstruction check passed with a broken auditor — "
        "the check cannot fail, so it is decoration"
    )


def test_a_wrong_auditor_is_caught_on_the_evidence_axis(monkeypatch):
    """A wrong support count must make the evidence check fail too."""
    original = probe._temporal_graph

    def broken(mem):
        graph = original(mem)
        return {k: {kk: vv for kk, vv in v.items() if kk != "amber"}
                for k, v in graph.items()}

    monkeypatch.setattr(probe, "_temporal_graph", broken)
    result = probe.run(cycles=CYCLES, seed=20261025, max_hypotheses=STRESS_CAP)
    assert not result["A1_evidence_replay"]["pass"], (
        "the evidence replay passed with a broken count — "
        "the check cannot fail, so it is decoration"
    )
