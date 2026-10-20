from pathlib import Path
from organica import MemoryService, SleepService

def test_full_developmental_stack(tmp_path):
    db_path = tmp_path / "test_organica.db"
    mem = MemoryService(db_path)
    
    stream = [
        "File modified: src/auth/login.py",
        "Test suite run: 3 failures, 47 passed",
        "Failure: test_login_session — AssertionError: session token expired",
        "File modified: src/auth/session.py",
        "Test suite run: 0 failures, 50 passed",
        "File modified: src/auth/oauth.py",
        "Test suite run: 2 failures, 48 passed",
        "Failure: test_oauth_callback — ConnectionRefusedError: port 8080",
        "File modified: src/auth/middleware.py",
        "Test suite run: 0 failures, 50 passed",
    ]
    for event in stream:
        mem.store(event, event_type="observe", source="env")
        
    assert mem.count() == len(stream)
    
    sleep = SleepService(mem)
    
    # Cycle 1: Seed
    r1 = sleep.run()
    assert len(r1.concepts) >= 1 or len(r1.predictions) >= 1
    
    # Cycle 2: Composition
    r2 = sleep.run()
    assert r2.prior_candidates_loaded > 0
    
    # Cycle 3: Hypotheses, Questions, Dreams & Investigations
    r3 = sleep.run()
    assert len(r3.hypotheses) > 0 or len(r3.dreams) > 0 or len(r3.investigations) > 0
    
    # Genealogy verification
    if r3.investigations:
        inv = r3.investigations[0]
        ancestry = sleep.get_ancestry(inv.id)
        assert ancestry["id"] == inv.id
        assert "parents" in ancestry
        
    mem.close()
