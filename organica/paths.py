"""
organica/paths.py
------------------------------------------------------------------
Canonical locations for Organica's files.

Two things live here:

  * `REPO_ROOT` -- so any script can find the project regardless of the
    directory it was launched from.
  * `scratch_db()` -- a disposable database location for examples and
    demos.

The scratch location matters: several example scripts used to open
`Path("memory.db")` in the *current working directory*, which meant that
running a demo from the repository root would delete the live 90-day
study's substrate. Every example now writes to `.scratch/` instead, so
demonstrations can never touch a real run.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

# organica/paths.py -> organica/ -> repository root
REPO_ROOT = Path(__file__).resolve().parent.parent

#: Disposable working area for examples, demos and scratch databases.
SCRATCH_DIR = REPO_ROOT / ".scratch"

#: The live study substrate.
LIVE_DB = REPO_ROOT / "memory.db"

#: The daemon's append-only cycle log.
LIVE_LOG = REPO_ROOT / "organica.log"


def scratch_db(name: str) -> Path:
    """Return a path for a disposable database, creating `.scratch/`."""
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    return SCRATCH_DIR / name


def temp_db(name: str) -> Path:
    """Return a path for a database in the system temp directory."""
    return Path(tempfile.mkdtemp(prefix="organica_")) / name


__all__ = [
    "REPO_ROOT",
    "SCRATCH_DIR",
    "LIVE_DB",
    "LIVE_LOG",
    "scratch_db",
    "temp_db",
]
