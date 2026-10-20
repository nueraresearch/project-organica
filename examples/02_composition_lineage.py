"""
Run Sleep V1 — Testing Structural Composition and Higher-Order Descendants.

We run multiple sleep cycles:
Cycle 1: Raw events -> V0 candidates (concepts, predictions, loops).
Cycle 2: Stability & strengthening of V0 candidates.
Cycle 3: Sleep V1 composition runs on the stable prior candidates,
         producing MetaConcepts and ProcessCandidates with explicit parent_ids.
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
print("  CYCLE 1: Seeding initial candidate nodes")
print("=" * 60)
r1 = sleep.run()
print(f"Cycle 1 generated: {len(r1.concepts)} concepts, {len(r1.loops)} loops, {len(r1.predictions)} predictions")

print("\n" + "=" * 60)
print("  CYCLE 2: Strengthening candidates into stable knowledge")
print("=" * 60)
r2 = sleep.run()
print(f"Cycle 2: {r2.candidates_strengthened} candidates strengthened")
print(f"Composites created in Cycle 2: {r2.composites_created}")
if r2.meta_concepts:
    print(f"  Meta-concepts: {len(r2.meta_concepts)}")
if r2.processes:
    print(f"  Processes: {len(r2.processes)}")

print("\n" + "=" * 60)
print("  CYCLE 3: Higher-Order Composition Inspection")
print("=" * 60)
r3 = sleep.run()
print(f"Cycle 3: {r3.composites_created} higher-order composites created")

print("\n--- META-CONCEPTS (Tags bridging multiple candidate structures) ---")
for m in r3.meta_concepts:
    print(json.dumps(m.__dict__, indent=2))

print("\n--- PROCESS CANDIDATES (Cycles composed of prediction candidate parents) ---")
for p in r3.processes:
    print(json.dumps(p.__dict__, indent=2))

print("\n" + "=" * 60)
print("  VERIFICATION: Are parent_ids pointing to real prior candidates?")
print("=" * 60)
prior_ids = {c["id"] for c in sleep._load_prior_candidates() if "id" in c}
all_parents = []
for m in r3.meta_concepts:
    all_parents.extend(m.parent_ids)
for p in r3.processes:
    all_parents.extend(p.parent_ids)

valid_parents = [pid for pid in all_parents if pid in prior_ids]
print(f"Total parent links in composites: {len(all_parents)}")
print(f"Valid parent IDs matched in memory: {len(valid_parents)}")
print(f"Lineage integrity: {len(valid_parents) / max(len(all_parents), 1) * 100:.1f}%")

mem.close()
