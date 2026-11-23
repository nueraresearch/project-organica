"""A frozen block whose measured build is no longer the shipped build.

The cap moved to 112 on 2026-11-11 (`DECISION-CAP-LEVEL`, landed in 0.15.0). The cap-40
preregistrations are frozen records of a build, not live claims about the engine: re-scoring
them to the new cap would rewrite what they fixed, and deleting them would lose the design the
cap-112 runners extend. So each carries a dated `build_superseded` block naming the build it
was written on, and its checks accept that build explicitly instead of the shipped one.

`accepts` is the only place that decides this. A record without the block is held to the
shipped build exactly as before; a record with the block must agree with the live version and
cap it declares, so a second landing cannot leave the disclosure silently stale.
"""
from __future__ import annotations

import json
from pathlib import Path

from benchmarks import engine_lineage

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "docs" / "engine_lineage_0.14.0.json"

FIELDS = ("date", "recorded_version", "recorded_cap", "recorded_sha256",
          "shipped_version", "shipped_cap", "note")


def disclosure(body: dict | None) -> dict | None:
    block = (body or {}).get("build_superseded")
    return block if isinstance(block, dict) else None


def matches(body: dict | None, field: str, value) -> bool:
    """Does the record disclose `value` as the build's recorded `field`?"""
    block = disclosure(body)
    return bool(block and block.get("recorded_" + field) == value)


def history() -> dict:
    """The retired 0.14.0 links, which join the record's own build to the one it was written on."""
    if not HISTORY.exists():
        return {"links": []}
    return json.loads(HISTORY.read_text(encoding="utf-8"))


def accepts(body: dict | None, stamp: str | None) -> bool:
    """The stamp is the shipped engine, or the build this record discloses it was measured on."""
    if engine_lineage.same_build(stamp):
        return True
    block = disclosure(body)
    if not block or not stamp:
        return False
    if block.get("recorded_sha256") == stamp:
        return True
    return engine_lineage.same_build(stamp, current=block.get("recorded_sha256"),
                                     record=history())


def problems(body: dict | None, version: str | None = None,
             cap: int | None = None) -> list[str]:
    """Everything that makes a supersession disclosure incomplete or stale."""
    block = disclosure(body)
    if block is None:
        return []
    found = ["the supersession disclosure has no `%s`" % field
             for field in FIELDS if block.get(field) in (None, "")]
    if version is not None and block.get("shipped_version") != version:
        found.append("the disclosure names shipped version %r, not the installed %r"
                     % (block.get("shipped_version"), version))
    if cap is not None and block.get("shipped_cap") != cap:
        found.append("the disclosure names shipped cap %r, not the installed %r"
                     % (block.get("shipped_cap"), cap))
    return found


def note(body: dict | None) -> str:
    """One table cell for a rendered page: which build the record was written on."""
    block = disclosure(body)
    if not block:
        return "the shipped build"
    return ("recorded on `%s` at cap `%s`; superseded by `%s` at cap `%s` on %s"
            % (block.get("recorded_version"), block.get("recorded_cap"),
               block.get("shipped_version"), block.get("shipped_cap"), block.get("date")))
