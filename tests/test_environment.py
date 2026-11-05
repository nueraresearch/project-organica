"""
tests/test_environment.py
Unit tests for organica.environment: ReactiveWorld and ActiveInquiryLoop.
"""

import pytest
from organica.environment import ReactiveWorld, ActiveInquiryLoop
from organica.memory import MemoryService
from organica.sleep import SleepService
from organica.paths import temp_db


def test_reactive_world_step_and_intervene():
    world = ReactiveWorld()
    ev1 = world.step()
    assert len(ev1) == 1
    assert "developer executed test suite" in ev1[0]

    # Intervene with matching rule
    feedback = world.intervene("probe_context", "developer", {"subject": "developer"})
    assert feedback == ["developer executed test suite"]

    # Intervene with non-matching subject
    fallback = world.intervene("probe_unknown", "database", {"subject": "database"})
    assert "neutral state response" in fallback[0]


def test_active_inquiry_loop_e2e():
    db = temp_db("test_active_inquiry.db")
    if db.exists():
        db.unlink()

    mem = MemoryService(str(db))
    svc = SleepService(mem)
    world = ReactiveWorld()
    loop = ActiveInquiryLoop(mem, svc, world, events_per_step=3)

    # Run for 15 cycles so memory accumulates and hypotheses/experiments emerge
    total_experiments = 0
    total_executed = 0

    for _ in range(15):
        report, inquiry = loop.step_and_sleep()
        total_experiments += len(report.experiments)
        total_executed += inquiry.experiments_executed

    assert loop.cycle_count == 15
    assert len(world.history) > 0
    
    # Verify that interventions were stored in memory with intervention source
    intervention_events = [
        e for e in mem.recent(n=500, event_type="observe")
        if e.source.startswith("intervention:")
    ]
    if total_executed > 0:
        assert len(intervention_events) > 0

    mem.close()
    db.unlink(missing_ok=True)
