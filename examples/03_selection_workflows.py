"""
Run Sleep V2 — Testing Natural Selection, Extinction (Pruning),
High-Order Synthesis (Workflow Concepts), and Multi-Generational Ancestry Traversal.
"""

from pathlib import Path
from organica import MemoryService
from organica.sleep import SleepService
import json

db = Path("memory.db")
db.unlink(missing_ok=True)

mem = MemoryService(db)

STREAM = [
    "File modified: src/auth/login.py",
    "Test suite run: 3 failures, 47 passed",
    "Failure: test_login_session — AssertionError: session token expired",
    "Failure: test_oauth_callback — ConnectionRefusedError: port 8080",
    "Failure: test_refresh_token — KeyError: 'expires_at'",
    "File modified: src/auth/session.py",
    "Test suite run: 1 failure, 49 passed",
    "Failure: test_oauth_callback — ConnectionRefusedError: port 8080",
    "File modified: src/auth/oauth.py",
    "Test suite run: 0 failures, 50 passed",
    "File modified: src/api/endpoints.py",
    "Test suite run: 2 failures, 48 passed",
    "Failure: test_rate_limiting — AssertionError: expected 429, got 200",
    "Failure: test_auth_middleware — AttributeError: 'NoneType' has no 'token'",
    "File modified: src/auth/middleware.py",
    "Test suite run: 1 failure, 49 passed",
    "Failure: test_auth_middleware — AttributeError: 'NoneType' has no 'token'",
    "File modified: src/auth/middleware.py",
    "Test suite run: 0 failures, 50 passed",
    "File modified: src/db/models.py",
    "Test suite run: 0 failures, 50 passed",
    "File modified: src/db/migrations/0042_add_user_index.sql",
    "File modified: src/db/models.py",
    "Test suite run: 4 failures, 46 passed",
    "Failure: test_user_lookup — DatabaseError: relation 'users_new' does not exist",
    "Failure: test_session_store — DatabaseError: relation 'users_new' does not exist",
    "Failure: test_auth_middleware — DatabaseError: relation 'users_new' does not exist",
    "Failure: test_login_session — DatabaseError: relation 'users_new' does not exist",
    "File modified: src/db/migrations/0042_add_user_index.sql",
    "Test suite run: 0 failures, 50 passed",
]

for event in STREAM:
    mem.store(event, event_type="observe", source="env")

print(f"Events stored: {mem.count()}")

sleep = SleepService(mem)

print("\n" + "=" * 60)
print("  CYCLE 1: Raw Experience -> Layer 1 Candidates")
print("=" * 60)
r1 = sleep.run()
print(f"Candidates generated: {len(r1.concepts)} concepts, {len(r1.loops)} loops, {len(r1.predictions)} predictions")

print("\n" + "=" * 60)
print("  CYCLE 2: Natural Selection + Layer 2 Composition")
print("=" * 60)
r2 = sleep.run()
print(f"Strengthened: {r2.candidates_strengthened} | Decayed: {r2.candidates_decayed} | Pruned: {r2.candidates_pruned}")
print(f"Composites: {len(r2.meta_concepts)} MetaConcepts, {len(r2.processes)} Processes")

print("\n" + "=" * 60)
print("  CYCLE 3: Layer 3 Synthesis (Workflow Concepts)")
print("=" * 60)
r3 = sleep.run()
print(f"Workflow Concepts (Layer 3) created: {len(r3.workflow_concepts)}")

for w in r3.workflow_concepts:
    print(json.dumps(w.__dict__, indent=2))

print("\n" + "=" * 60)
print("  CYCLE 4 & 5: Testing Environmental Shift (Extinction of unreinforced nodes)")
print("=" * 60)
# Feed an entirely new context stream (e.g., pure frontend / css / styling, no db or auth)
SHIFT_STREAM = [
    "File modified: web/styles/theme.css",
    "File modified: web/components/button.tsx",
    "Test suite run: 0 failures, 60 passed",
    "File modified: web/styles/theme.css",
    "Test suite run: 0 failures, 60 passed",
]
for event in SHIFT_STREAM:
    mem.store(event, event_type="observe", source="env")

r4 = sleep.run()
print(f"Cycle 4 (Post-Shift): Strengthened: {r4.candidates_strengthened} | Decayed: {r4.candidates_decayed} | Pruned (Died): {r4.candidates_pruned}")

r5 = sleep.run()
print(f"Cycle 5 (Continued Shift): Strengthened: {r5.candidates_strengthened} | Decayed: {r5.candidates_decayed} | Pruned (Died): {r5.candidates_pruned}")

print("\n" + "=" * 60)
print("  GENEALOGY: Ancestry Tree of a High-Order Workflow Concept")
print("=" * 60)
if r3.workflow_concepts:
    target_id = r3.workflow_concepts[0].id
    ancestry = sleep.get_ancestry(target_id)
    print(json.dumps(ancestry, indent=2))

mem.close()
