"""Tests for benchmarks/acquisition_harness.py — the §8 prerequisite gates.

Design discipline (mirrors AGENTS.md):
  * Every gate has a PASS test (normal operation) and a FAIL test (deliberately
    broken condition).  A gate that cannot be demonstrated to fail is not a gate.
  * No engine files are edited.  Failure branches are produced by monkeypatching
    the harness's own helper functions or by injecting a bad DB state after the
    fact.
  * Standard library only; no third-party imports beyond pytest.

Speed note: tests that spin up a world use FAST_CYCLES (40) so they complete in
~15s each.  Gate 13 needs SHORT_CYCLES (120) to reach a settled acquisition
state, so its two expensive runs are computed ONCE in module-scoped fixtures
and shared by the assertions that read them.
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

@pytest.fixture(scope="module")
def gate13_frozen():
    """Gate 13 on the FROZEN engine, computed once (a 120-cycle run is slow)."""
    return gate_acquisition_sufficiency(
        seed=DEFAULT_SEED, cycles=SHORT_CYCLES, threshold=SUFFICIENCY_THRESHOLD)


@pytest.fixture(scope="module")
def gate13_capped():
    """Gate 13 with the Layer-1 prediction cap raised to 1000 (treatment arm)."""
    return gate_acquisition_sufficiency(
        seed=DEFAULT_SEED, cycles=SHORT_CYCLES, threshold=SUFFICIENCY_THRESHOLD,
        max_predictions=1000)


class TestGate13AcquisitionSufficiency:
    """Gate 13 measures ASSERTED structure coverage (Amendment 1).

    On the frozen engine the gate FIRES.  The raw temporal log holds every
    world edge while the organism's asserted structure holds almost none of
    them, and that asymmetry is the measured finding.  So the "normal run"
    expectation for this gate is a FAILURE, and the treatment arm — the same
    gate with the Layer-1 prediction cap raised — is what shows the failure is
    attributable rather than mysterious.
    """

    def test_gate_fires_on_the_frozen_engine(self, gate13_frozen):
        """The gate must FAIL at the preregistered threshold, not pass."""
        result = gate13_frozen
        assert result["passed"] is False
        assert result["acquisition_failed"] is True
        assert result["asserted_coverage"] < SUFFICIENCY_THRESHOLD
        assert result["coverage_basis"] == "asserted_structure"
        assert result["world_edges"] > 0
        assert result["failure_reason"] is not None

    def test_raw_memory_holds_the_world_the_assertions_lack(self, gate13_frozen):
        """Raw temporal coverage is high while asserted coverage is near zero.

        This is the discrimination the dual accounting exists for: the world
        was present in the organism's memory and the organism failed to assert
        it.  A harness measuring only the raw figure would pass here.
        """
        result = gate13_frozen
        assert result["raw_temporal_coverage"] > 0.9
        assert result["asserted_coverage"] < 0.1
        assert (result["covered_temporal_edges"]
                > result["covered_asserted_edges"])

    def test_gate_passes_when_the_prediction_cap_is_raised(self, gate13_capped):
        """Attribution: the same gate passes when the Layer-1 cap is relaxed."""
        result = gate13_capped
        assert result["asserted_coverage"] >= SUFFICIENCY_THRESHOLD
        assert result["passed"] is True
        assert result["acquisition_failed"] is False

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
        # and pass threshold=0.0 so every gate's own mechanics are exercised
        # without asserting anything about the organism's acquisition.
        result = run_all_gates(seed=DEFAULT_SEED, cycles=FAST_CYCLES,
                               threshold=0.0)
        assert result["all_passed"] is True
        assert "ALL GATES PASSED" in result["summary"]
        assert len(result["gates"]) == 4

    def test_aggregate_reports_gate13_failure_at_the_real_threshold(self):
        """At the preregistered threshold the prerequisite check must NOT pass.

        §8 requirement 13 is a prerequisite of the acquisition study.  A
        harness that reported "all gates passed" on the frozen engine would
        authorise a study the same harness says is not measurable.
        """
        result = run_all_gates(seed=DEFAULT_SEED, cycles=FAST_CYCLES,
                               threshold=SUFFICIENCY_THRESHOLD)
        assert result["all_passed"] is False
        assert "gate13" in result["summary"]
        assert result["gates"]["gate13_sufficiency"]["acquisition_failed"] is True

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
