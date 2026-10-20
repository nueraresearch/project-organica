"""
Run Sleep V0 — the first sleep cycle.

Fresh database from the same event stream, then sleep.
Inspects: what candidates emerged, their provenance, and
whether the structures are stable enough to evolve.
"""

from pathlib import Path
from organica import MemoryService
from organica.sleep import SleepService
import json

# ── Fresh database ──────────────────────────────────────────────────
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

# ── Sleep cycle 1 ───────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  SLEEP CYCLE 1")
print("=" * 60)

sleep = SleepService(mem)
report = sleep.run()

# ── Inspect candidates ──────────────────────────────────────────────
def show(label, items):
    print(f"\n--- {label} ({len(items)}) ---")
    for item in items:
        print(json.dumps(item.__dict__ if hasattr(item, '__dict__') else item, indent=2))

show("CONCEPT CANDIDATES", report.concepts)
show("PHRASE CANDIDATES", report.phrases)
show("LOOP CANDIDATES", report.loops)
show("PREDICTION CANDIDATES", report.predictions[:8])
show("ANOMALY CANDIDATES", report.anomalies[:5])

print(f"\n--- EVOLUTION ---")
print(f"  Prior candidates loaded:  {report.prior_candidates_loaded}")
print(f"  Candidates strengthened:  {report.candidates_strengthened}")
print(f"  Candidates decayed:       {report.candidates_decayed}")

# ── Sleep cycle 2 (immediate re-run to test stability) ──────────────
print("\n" + "=" * 60)
print("  SLEEP CYCLE 2 (stability test — same data, no new events)")
print("=" * 60)

report2 = sleep.run()

show("CONCEPT CANDIDATES", report2.concepts)
show("LOOP CANDIDATES", report2.loops)

print(f"\n--- EVOLUTION ---")
print(f"  Prior candidates loaded:  {report2.prior_candidates_loaded}")
print(f"  Candidates strengthened:  {report2.candidates_strengthened}")
print(f"  Candidates decayed:       {report2.candidates_decayed}")

# ── Check: did any candidates get strengthened? ─────────────────────
print("\n" + "=" * 60)
print("  KEY QUESTION: Did sleep N+1 build on sleep N?")
print("=" * 60)

for c in report2.concepts:
    if c.evidence.get("strengthened"):
        print(f"\n  [+] STRENGTHENED concept: {c.members}")
        print(f"    confidence now:    {c.confidence:.4f}")
        print(f"    prior confidence:  {c.evidence.get('prior_confidence', '?')}")

for l in report2.loops:
    if l.evidence.get("strengthened"):
        print(f"\n  [+] STRENGTHENED loop: {' -> '.join(l.path)}")
        print(f"    strength now:    {l.strength}")

for p in report2.predictions[:8]:
    if p.evidence.get("strengthened"):
        print(f"\n  [+] STRENGTHENED prediction: {p.source} -> {p.target}")
        print(f"    strength now:    {p.strength:.4f}")
        print(f"    prior strength:  {p.evidence.get('prior_strength', '?')}")

# Check if any decayed
sleep_events = mem.search("sleep:", limit=500)
decayed = [e for e in sleep_events if "decay_cycle" in e.content]
if decayed:
    print(f"\n  [!] {len(decayed)} candidates decayed (no longer observed)")

print("\n" + "=" * 60)
print("  Done. The organism has slept twice.")
print("=" * 60)

mem.close()
