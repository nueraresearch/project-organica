"""
conftest.py
------------------------------------------------------------------
Make the repository root importable no matter how pytest is invoked.

Without this, `import organica` inside the tests only resolves when you
run `python -m pytest` from the repository root. Running the `pytest`
console script, or pointing pytest at the tests from another directory,
fails with `ModuleNotFoundError: No module named 'organica'` -- which is
exactly the failure a first-time contributor hits.

pytest imports this file before collecting anything, so inserting the
repository root here fixes every invocation style.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
