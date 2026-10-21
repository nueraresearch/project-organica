"""
Test Sleep V5: Categorized Dreams & Expected Information Gain (Investigation Candidates).

Demonstrates:
  1. 4 Categories of Dreams:
       - completion_dream (transitive closure)
       - analogy_dream (co-occurrence synonym substitution)
       - mutation_dream (path extension)
       - conditional_dream (hidden context disambiguating questions)
  2. Investigation Candidates:
       - Ranked strictly by Expected Information Gain (EIG)
       - Demonstrates: Importance != Confidence; Importance ~= Expected Information Gain
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

STREAM = [
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
    "File modified: src/db/models.py",
    "Test suite run: 4 failures, 46 passed",
    "Failure: test_user_lookup — DatabaseError: relation 'users_new' does not exist",
    "File modified: src/db/migrations/0042_add_user_index.sql",
    "Test suite run: 0 failures, 50 passed",
]

for e in STREAM:
    mem.store(e, event_type="observe", source="env")

sleep = SleepService(mem)

print("=" * 65)
print("  CYCLE 1 & 2: Growing from Events to Workflows & Questions")
print("=" * 65)
sleep.run()
sleep.run()

print("\n" + "=" * 65)
print("  CYCLE 3: Sleep V5 Categorized Dreams & Investigation Agenda")
print("=" * 65)
r3 = sleep.run()

print(f"\nCategorized Dreams Generated ({len(r3.dreams)}):")
for d in r3.dreams:
    print(f"  [{d.id}] category={d.dream_category:<12} subject={d.subject:<10} novelty={d.novelty:.2f} path/context={d.path_or_context}")

print(f"\nInvestigation Agenda (Ranked by Expected Information Gain) ({len(r3.investigations)}):")
for inv in r3.investigations:
    print(f"  [{inv.id}] target={inv.target_type:<10} subject={inv.subject:<10} EIG={inv.expected_information_gain:.4f} (uncertainty={inv.uncertainty:.2f}, novelty={inv.novelty:.2f})")
    print(f"       parent_ids={inv.parent_ids} | formula: {inv.evidence.get('formula')}")

mem.close()
