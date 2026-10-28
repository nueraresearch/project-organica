"""Tests for benchmarks/acquisition_harness.py — the §8 prerequisite gates.

Design discipline (mirrors AGENTS.md):
  * Every gate has a PASS test (normal operation) and a FAIL test (deliberately
    broken condition).  A gate that cannot be demonstrated to fail is not a gate.
  * No engine files are edited.  Failure branches are produced by monkeypatching
    the harness's own helper functions or by injecting a bad DB state after the
    fact.
  * Standard library only; no third-party imports beyond pytest.

Speed note: tests that spin up a world use FAST_CYCLES (40) so they complete in
~15s each.  The sufficiency PASS test uses SHORT_CYCLES (120) to ensure enough
acquisition events are present to exceed the 0.50 coverage threshold.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.acquisition_harness import (  # noqa: E402
    gate_content_identity,
    gate_intervention_verification,
    gate_removal_verification,
    gate_acquisition_sufficiency,
    gate_scratch_only,
    run_all_gates,
    _make_scratch_db,
    _erem,
    SUFFICIENCY_THRESHOLD,
    DEFAULT_SEED,
    SHORT_CYCLES,
    FAST_CYCLES,
)
from organica.paths import LIVE_DB, temp_db  # noqa: E402


# ---------------------------------------------------------------------------
# Gate 10 — content-identity detection
# ---------------------------------------------------------------------------

class TestGate10ContentIdentity:
    def test_passes_on_normal_run(self):
        result = gate_content_identity(seed=DEFAULT_SEED, cycles=FAST_CYCLES)
        assert result["passed"] is True
        assert result["total_candidates"] > 0
        # re-instantiated + single_store must account for every candidate.
        assert result["total_candidates"] == (
            result["reinstantiated"] + result["single_store"]
        )
        assert result["failure_reason"] is None

    def test_fails_when_no_candidates_stored(self, monkeypatch):
        """Force the ObservingMemoryService to never record a candidate_id."""
        from benchmarks import acquisition_harness as harness

        original_cls = harness._CountingMemoryService

        class _EmptyCountingMemoryService(original_cls):
            """Override store() to suppress candidate_id tracking."""
            def store(self, content, event_type="observe", source="env"):
                event = super().store(content, event_type=event_type,
                                      source=source)
                if event_type == "sleep":
                    self.candidate_ids.clear()
                    self.store_counts.clear()
                return event

        monkeypatch.setattr(harness, "_CountingMemoryService",
                            _EmptyCountingMemoryService)

        result = gate_content_identity(seed=DEFAULT_SEED, cycles=FAST_CYCLES)
        assert result["passed"] is False
        assert result["total_candidates"] == 0
        assert result["failure_reason"] is not None


# ---------------------------------------------------------------------------
# Gate 11 — intervention verification
# ---------------------------------------------------------------------------

class TestGate11InterventionVerification:
    def test_passes_on_normal_run(self):
        result = gate_intervention_verification(seed=DEFAULT_SEED,
                                                cycles=FAST_CYCLES)
        assert result["passed"] is True
        assert result["erem_confirmed"] is True
        assert result["events_after_erem"] == 0
        assert result["precedes_after_erem"] == 0
        assert result["events_before_erem"] > 0
        assert result["failure_reason"] is None

    def test_fails_when_erem_incomplete(self, monkeypatch):
        """Simulate a broken E-rem that leaves events rows behind."""
        from benchmarks import acquisition_harness as harness

        def _broken_erem(mem, source):
            # Delete precedes but NOT the events rows — intervention incomplete
            mem._conn.execute("DELETE FROM precedes")
            mem._conn.commit()

        monkeypatch.setattr(harness, "_erem", _broken_erem)

        result = gate_intervention_verification(seed=DEFAULT_SEED,
                                                cycles=FAST_CYCLES)
        assert result["passed"] is False
        assert result["erem_confirmed"] is False
        assert result["events_after_erem"] > 0
        assert result["failure_reason"] is not None


# ---------------------------------------------------------------------------
# Gate 12 — removal verification
# ---------------------------------------------------------------------------

class TestGate12RemovalVerification:
    def test_passes_on_normal_run(self):
        result = gate_removal_verification(seed=DEFAULT_SEED,
                                           cycles=FAST_CYCLES)
        assert result["passed"] is True
        assert result["events_acq_after"] == 0
        assert result["precedes_after"] == 0
        assert result["cooccurrences_after"] > 0
        assert result["tag_counts_after"] > 0
        assert result["failure_reason"] is None

    def test_fails_when_cooccurrences_wiped(self, monkeypatch):
        """Simulate an over-aggressive removal that clears cooccurrences."""
        from benchmarks import acquisition_harness as harness

        original_erem = harness._erem

        def _nuclear_erem(mem, source):
            original_erem(mem, source)
            mem._conn.execute("DELETE FROM cooccurrences")
            mem._conn.commit()

        monkeypatch.setattr(harness, "_erem", _nuclear_erem)

        result = gate_removal_verification(seed=DEFAULT_SEED,
                                           cycles=FAST_CYCLES)
        assert result["passed"] is False
        assert result["cooccurrences_after"] == 0
        assert result["checks"]["cooccurrences_preserved"] is False
        assert result["failure_reason"] is not None

    def test_fails_when_precedes_not_cleared(self, monkeypatch):
        """Simulate an incomplete removal that leaves precedes rows."""
        from benchmarks import acquisition_harness as harness

        def _partial_erem(mem, source):
            # Remove events but NOT precedes
            mem._conn.execute("DELETE FROM events WHERE source = ?", (source,))
            mem._conn.commit()

        monkeypatch.setattr(harness, "_erem", _partial_erem)

        result = gate_removal_verification(seed=DEFAULT_SEED,
                                           cycles=FAST_CYCLES)
        assert result["passed"] is False
        assert result["precedes_after"] > 0
        assert result["checks"]["precedes_cleared"] is False


# ---------------------------------------------------------------------------
# Gate 13 — acquisition sufficiency
# ---------------------------------------------------------------------------

class TestGate13AcquisitionSufficiency:
    def test_passes_on_normal_run(self):
        # Use SHORT_CYCLES here: FAST_CYCLES (40) has only 20 acquisition cycles,
        # which may not produce enough coverage to exceed the 0.50 threshold.
        result = gate_acquisition_sufficiency(
            seed=DEFAULT_SEED,
            cycles=SHORT_CYCLES,
            threshold=SUFFICIENCY_THRESHOLD,
        )
        assert result["passed"] is True
        assert result["acquisition_failed"] is False
        assert result["coverage"] >= SUFFICIENCY_THRESHOLD
        assert result["world_edges"] > 0
        assert result["covered_edges"] > 0
        assert result["failure_reason"] is None

    def test_fails_when_threshold_impossibly_high(self):
        """Force failure by using a threshold of 1.1 (above any possible coverage)."""
        result = gate_acquisition_sufficiency(
            seed=DEFAULT_SEED,
            cycles=FAST_CYCLES,
            threshold=1.1,
        )
        assert result["passed"] is False
        assert result["acquisition_failed"] is True
        assert result["failure_reason"] is not None

    def test_failure_reason_names_acquisition_not_transfer(self):
        """The failure message must say acquisition_failed and NOT transfer_failure."""
        result = gate_acquisition_sufficiency(
            seed=DEFAULT_SEED,
            cycles=FAST_CYCLES,
            threshold=1.1,
        )
        reason = result["failure_reason"]
        assert "acquisition_failed" in reason
        # The phrase "NOT transfer_failure" must appear — make sure the label
        # distinction is explicit in the output.
        assert "NOT transfer_failure" in reason

    def test_world_edges_non_empty(self):
        """The world must expose a non-trivial edge set."""
        result = gate_acquisition_sufficiency(
            seed=DEFAULT_SEED,
            cycles=FAST_CYCLES,
            threshold=0.0,   # always pass
        )
        assert result["world_edges"] > 0


# ---------------------------------------------------------------------------
# Gate 16 — scratch-only guarantee
# ---------------------------------------------------------------------------

class TestGate16ScratchOnly:
    def test_passes_for_temp_db(self, tmp_path):
        fake_scratch = tmp_path / "harness_test.db"
        fake_scratch.touch()
        result = gate_scratch_only(fake_scratch)
        assert result["passed"] is True
        assert result["failure_reason"] is None

    def test_fails_for_live_db(self):
        result = gate_scratch_only(LIVE_DB)
        assert result["passed"] is False
        assert result["failure_reason"] is not None
        assert "live" in result["failure_reason"].lower()

    def test_make_scratch_db_is_not_live(self):
        """_make_scratch_db() must never return the live DB path."""
        path = _make_scratch_db("test_gate16")
        assert path.resolve() != LIVE_DB.resolve()
        path.unlink(missing_ok=True)
        try:
            path.parent.rmdir()
        except OSError:
            pass

    def test_assert_not_live_raises_on_live_db(self):
        from benchmarks.acquisition_harness import _WriteSentinel
        with pytest.raises(AssertionError, match="live DB"):
            _WriteSentinel.assert_not_live(LIVE_DB)


# ---------------------------------------------------------------------------
# Combined run_all_gates
# ---------------------------------------------------------------------------

class TestRunAllGates:
    def test_all_gates_pass_normal_run(self):
        # run_all_gates uses SHORT_CYCLES by default; we override to FAST_CYCLES
        # but gate 13 may not reach threshold.  Pass threshold=0.0 to guarantee.
        result = run_all_gates(seed=DEFAULT_SEED, cycles=FAST_CYCLES,
                               threshold=0.0)
        assert result["all_passed"] is True
        assert "ALL GATES PASSED" in result["summary"]
        assert len(result["gates"]) == 4

    def test_aggregate_fails_when_one_gate_fails(self, monkeypatch):
        """Monkeypatch gate 13 to force a failure; aggregate must be False."""
        from benchmarks import acquisition_harness as harness

        def _failing_gate(**kwargs):
            return {
                "passed": False,
                "world_edges": 10,
                "covered_edges": 0,
                "coverage": 0.0,
                "threshold": 0.5,
                "acquisition_failed": True,
                "failure_reason": "injected failure",
            }

        monkeypatch.setattr(harness, "gate_acquisition_sufficiency",
                            _failing_gate)

        result = run_all_gates(seed=DEFAULT_SEED, cycles=FAST_CYCLES,
                               threshold=0.0)
        assert result["all_passed"] is False
        assert "GATES FAILED" in result["summary"]
        assert "gate13" in result["summary"]
