"""A frozen record measured on a build the project no longer ships.

R1 (2026-11-24): the records written on 0.15.0 keep the build they were written on. A record's
own validation accepts that build when the record discloses the shipped one; the run gate still
refuses, because a cell opened on the shipped build would be a different experiment. Tests
exercise a gate's open path on a synthetic record stamped with the shipped build.

Nothing here runs a cell, moves a threshold or re-scores a result.
"""

from __future__ import annotations

DEFAULT = "0.15.0"


def disclosure(doc) -> dict | None:
    block = (doc or {}).get("build_superseded")
    return block if isinstance(block, dict) else None


def recorded_version(doc, default: str = DEFAULT) -> str:
    """The build a record says it was written on, from whichever field it carries."""
    engine = (doc or {}).get("engine")
    if isinstance(engine, dict) and engine.get("version"):
        return str(engine["version"])
    if isinstance(engine, str) and engine:
        return engine
    return str((doc or {}).get("engine_version") or default)


def accepts(doc, shipped: str, recorded: str = DEFAULT) -> bool:
    """The record is for the shipped build, or it discloses the build that superseded it."""
    if str(shipped) == str(recorded):
        return True
    block = disclosure(doc)
    return bool(block
                and str(block.get("recorded_version")) == str(recorded)
                and str(block.get("shipped_version")) == str(shipped))


def supersession_problem(doc, shipped: str, recorded: str = DEFAULT) -> str | None:
    """The one reason a frozen record does not account for the shipped build, or None."""
    if accepts(doc, shipped, recorded):
        return None
    return ("the record is frozen on %s, the shipped build is %s, and it carries no "
            "supersession disclosure naming that build" % (recorded, shipped))
