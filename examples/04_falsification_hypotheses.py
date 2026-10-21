"""
Test Sleep V3: Falsifiable Hypotheses, Competing Beliefs, and Changing Mind.

Demonstrates:
  1. Hypotheses formed strictly from WorkflowConcepts, Processes & MetaConcepts.
  2. Competing hypotheses (e.g. subject 'suite' -> expectation 'failure' vs 'passed').
  3. Reversal: Initial experience favors failure, then flawless runs cause
     the organism to adapt, revising confidence up/down without human language.
"""

from pathlib import Path
import sys
from pathlib import Path

# Allow running this file directly from a fresh clone, with no install:
# walk up until we find the repository root, then make it importable.
_REPO_ROOT = Path(__file__).resolve()
while not (_REPO_ROOT / "pyproject.toml").exists() and _REPO_ROOT != _REPO_ROOT.parent:
    _REPO_ROOT = _REPO_ROOT.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from organica.paths import scratch_db
from organica import MemoryService
from organica.sleep import SleepService
import json

db = scratch_db("memory.db")
db.unlink(missing_ok=True)

mem = MemoryService(db)

# -------------------------------------------------------------
# Era 1: The Buggy Era (Failures follow suite and modifications)
# -------------------------------------------------------------
ERA_1 = [
    "File modified: src/auth/login.py",
    "Test suite run: 3 failures, 47 passed",
    "Failure: test_login_session — AssertionError: session token expired",
    "File modified: src/auth/session.py",
    "Test suite run: 2 failures, 48 passed",
    "Failure: test_oauth_callback — ConnectionRefusedError: port 8080",
    "File modified: src/auth/oauth.py",
    "Test suite run: 1 failure, 49 passed",
    "Failure: test_token — KeyError: token",
    "File modified: src/auth/middleware.py",
    "Test suite run: 2 failures, 48 passed",
    "Failure: test_auth_middleware — AttributeError: NoneType",
    "File modified: src/auth/middleware.py",
    "Test suite run: 1 failure, 49 passed",
    "Failure: test_auth_middleware — AttributeError: NoneType",
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

for e in ERA_1:
    mem.store(e, event_type="observe", source="env")

sleep = SleepService(mem)

print("=" * 65)
print("  CYCLE 1: Seeding Layer 1-3 Candidates (from Era 1)")
print("=" * 65)
sleep.run()

print("\n" + "=" * 65)
print("  CYCLE 2: Stabilizing Workflows & Generating Hypotheses")
print("=" * 65)
r2 = sleep.run()

print(f"Generated {len(r2.hypotheses)} Hypotheses. Inspecting sample:")
for h in r2.hypotheses[:8]:
    print(f"  [{h.id}] subject='{h.subject}' -> expectation='{h.expectation}'")
    print(f"      conf: {h.confidence:.4f} | support: {h.support_count} | contradiction: {h.contradiction_count}")
    print(f"      parents: {h.parent_ids}")

# Focus on competing expectations for 'suite'
suite_hyps_c2 = [h for h in r2.hypotheses if h.subject == "suite"]
print("\n--- Competing Hypotheses for subject='suite' in Cycle 2 ---")
for h in suite_hyps_c2:
    print(f"  suite -> {h.expectation:<12} confidence: {h.confidence:.4f} (support: {h.support_count}, contra: {h.contradiction_count})")

# -------------------------------------------------------------
# Era 2: The Flawless Era (30 consecutive passes, 0 failures)
# -------------------------------------------------------------
print("\n" + "=" * 65)
print("  ERA 2: Shift to Flawless Passes (30 consecutive clean runs)")
print("=" * 65)
ERA_2 = []
for i in range(15):
    ERA_2.append(f"File modified: src/feature_{i}.py")
    ERA_2.append("Test suite run: 0 failures, 50 passed")

for e in ERA_2:
    mem.store(e, event_type="observe", source="env")

r3 = sleep.run()

print("\n" + "=" * 65)
print("  CYCLE 3: Belief Revision & Falsification Inspection")
print("=" * 65)
suite_hyps_c3 = [h for h in r3.hypotheses if h.subject == "suite"]
print("--- Competing Hypotheses for subject='suite' in Cycle 3 ---")
for h in suite_hyps_c3:
    delta = h.evidence.get('revision_delta', 0.0)
    sign = "+" if delta >= 0 else ""
    print(f"  suite -> {h.expectation:<12} confidence: {h.confidence:.4f} ({sign}{delta:.4f})")
    print(f"       support: {h.support_count} | contradiction: {h.contradiction_count}")

# Check ancestry
if suite_hyps_c3:
    print("\n" + "=" * 65)
    print("  GENEALOGY of Dominant Hypothesis (suite -> passed)")
    print("=" * 65)
    passed_hyp = next((h for h in suite_hyps_c3 if h.expectation == "passed"), suite_hyps_c3[0])
    ancestry = sleep.get_ancestry(passed_hyp.id)
    print(json.dumps(ancestry, indent=2))

mem.close()
