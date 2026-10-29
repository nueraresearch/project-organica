"""Quick inspection of MemoryService internals."""
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService
from organica.sleep import SleepService
from organica.paths import temp_db

db_path = temp_db('inspect_sleep')
mem = MemoryService(db_path)
sleep = SleepService(mem)

mem.store("amber birch")
mem.store("cedar yarrow")
sleep.run_sleep_cycle()

conn = mem._conn
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", tables)

for (tname,) in tables:
    cols = conn.execute(f"PRAGMA table_info({tname})").fetchall()
    col_names = [c[1] for c in cols]
    cnt = conn.execute(f"SELECT count(*) FROM {tname}").fetchone()[0]
    print(f"  {tname}: {col_names}  ({cnt} rows)")

# Check precedes
prec = conn.execute("SELECT * FROM precedes LIMIT 5").fetchall()
print("precedes sample:", prec)

# Check what temporal_edges returns
te = mem.temporal_edges(min_count=1)
print("temporal_edges(min_count=1):", te[:5])

# Check what_follows
wf = mem.what_follows("amber")
print("what_follows(amber):", wf[:5])

mem.close()
db_path.unlink(missing_ok=True)
