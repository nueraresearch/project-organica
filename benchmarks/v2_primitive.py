"""The level-1 mutable-identity primitive: a stored composite with an id that is not its content.

This is the bounded build authorised by `DECISION-V2-PRIMITIVE-BUILD`: one SQLite store, level 1
only, members are undirected edges, the canonical key is the direction-free tag set, ids come from a
monotone counter, mutations are versioned compare-and-set, retirement leaves a tombstone, and atoms
are immutable. It writes only its own store and never opens the live `memory.db`.

What is deliberately absent: level 2, `fork`, per-version history, `set_direction`, and any
consumer that predicts. A direction flip is a registration of the same key, not a mutation.

    python -m benchmarks.v2_primitive --demo      # a small store, no world, no cell
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path
from typing import Iterable

TAG = re.compile(r"^[A-Za-z]{4,}$")
FROZEN_TABLES = frozenset({"events", "precedes", "cooccurrences", "tag_counts", "sleep_cycles"})
TABLES = ("atoms", "composite_ids", "composites", "members", "tombstones")

SCHEMA = """
CREATE TABLE composite_ids (next_id INTEGER NOT NULL);
INSERT INTO composite_ids (next_id) VALUES (1);
CREATE TABLE composites (
    id INTEGER PRIMARY KEY,
    canonical_key TEXT NOT NULL UNIQUE,
    version INTEGER NOT NULL,
    retired INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE atoms (
    atom TEXT PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE members (
    composite_id INTEGER NOT NULL REFERENCES composites(id),
    atom TEXT NOT NULL REFERENCES atoms(atom),
    atom_version INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (composite_id, atom)
);
CREATE INDEX members_by_atom ON members(atom);
CREATE TABLE tombstones (
    composite_id INTEGER PRIMARY KEY REFERENCES composites(id),
    version INTEGER NOT NULL
);
"""


class PrimitiveError(Exception):
    """The base class for the primitive's refusals."""


class UnknownComposite(PrimitiveError):
    """No composite has that id."""


class RetiredComposite(PrimitiveError):
    """The composite is retired; its members are frozen."""


class StaleVersion(PrimitiveError):
    """The expected version is not the current one."""


class FrozenGraphError(PrimitiveError):
    """A write would touch the frozen V1 graph, or the store is the live one."""


def normalise_tag(tag: str) -> str:
    if not isinstance(tag, str) or not TAG.match(tag):
        raise ValueError("a tag must be at least four ASCII letters: %r" % (tag,))
    return tag


def normalise_edge(edge: Iterable[str]) -> tuple[str, str]:
    try:
        a, b = tuple(edge)
    except ValueError as error:
        raise ValueError("an edge is exactly two tags") from error
    a, b = normalise_tag(a), normalise_tag(b)
    if a == b:
        raise ValueError("an edge joins two distinct tags")
    return (a, b) if a < b else (b, a)


def normalise_key(key: Iterable[str] | str) -> tuple[str, ...]:
    tags = key.split("|") if isinstance(key, str) else list(key)
    if not tags:
        raise ValueError("a canonical key has at least one tag")
    return tuple(sorted({normalise_tag(tag) for tag in tags}))


def _atom(edge: tuple[str, str]) -> str:
    return "%s|%s" % edge


class Primitive:
    """A level-1 composite store, addressed by id and versioned by compare-and-set."""

    def __init__(self, path: str | Path):
        if str(path) != ":memory:" and Path(path).name == "memory.db":
            raise FrozenGraphError("the primitive never opens the live memory.db")
        self.path = str(path)
        self._conn = sqlite3.connect(self.path, isolation_level=None)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("PRAGMA journal_mode = DELETE")
        if not self._conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'composites'"
        ).fetchone():
            self._conn.executescript(SCHEMA)
            self._conn.execute("PRAGMA user_version = 1")

    # -- lifecycle -------------------------------------------------------------------------
    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Primitive":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def _write(self):
        class _Tx:
            def __init__(self, conn):
                self.conn = conn

            def __enter__(self):
                if self.conn.in_transaction:
                    raise RuntimeError("the primitive does not nest transactions")
                self.conn.execute("BEGIN IMMEDIATE")
                return self

            def __exit__(self, exc_type, exc, tb):
                if exc_type is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()
                return False

        return _Tx(self._conn)

    # -- identity --------------------------------------------------------------------------
    def _code(self, composite_id) -> int:
        if type(composite_id) is not int or composite_id <= 0:
            raise TypeError("a composite id is a positive integer, and nothing else")
        return composite_id

    def _row(self, composite_id: int):
        row = self._conn.execute(
            "SELECT id, canonical_key, version, retired FROM composites WHERE id = ?",
            (composite_id,),
        ).fetchone()
        if row is None:
            raise UnknownComposite("no composite with id %d" % composite_id)
        return row

    def register(self, key: Iterable[str] | str, members: Iterable[Iterable[str]] = ()) -> int:
        """Register a canonical key; a known key returns its existing id, retired or not."""
        canonical = normalise_key(key)
        edges = tuple(sorted({normalise_edge(edge) for edge in members}))
        with self._write():
            existing = self._conn.execute(
                "SELECT id FROM composites WHERE canonical_key = ?", ("|".join(canonical),)
            ).fetchone()
            if existing:
                return int(existing[0])
            next_id = int(self._conn.execute("SELECT next_id FROM composite_ids").fetchone()[0])
            self._conn.execute(
                "INSERT INTO composites (id, canonical_key, version, retired) VALUES (?, ?, 1, 0)",
                (next_id, "|".join(canonical)),
            )
            for edge in edges:
                atom = _atom(edge)
                self._conn.execute("INSERT OR IGNORE INTO atoms (atom) VALUES (?)", (atom,))
                self._conn.execute(
                    "INSERT INTO members (composite_id, atom, atom_version) VALUES (?, ?, 1)",
                    (next_id, atom),
                )
            self._conn.execute("UPDATE composite_ids SET next_id = next_id + 1")
            return next_id

    def resolve(self, composite_id, version: int | None = None) -> dict:
        """Resolve the object by id; `(id, version)` resolves the current state at that version."""
        composite_id = self._code(composite_id)
        row = self._row(composite_id)
        if version is not None:
            if type(version) is not int:
                raise TypeError("a version is an integer")
            if version != row[2]:
                raise StaleVersion(
                    "composite %d is at version %d, not %d" % (composite_id, row[2], version)
                )
        members = tuple(
            tuple(atom.split("|"))
            for (atom,) in self._conn.execute(
                "SELECT atom FROM members WHERE composite_id = ? ORDER BY atom", (composite_id,)
            )
        )
        return {
            "id": row[0],
            "key": tuple(row[1].split("|")),
            "version": row[2],
            "retired": bool(row[3]),
            "members": members,
        }

    def members(self, composite_id) -> tuple[tuple[str, str], ...]:
        return self.resolve(composite_id)["members"]

    def atom(self, edge: Iterable[str]) -> dict:
        atom = _atom(normalise_edge(edge))
        row = self._conn.execute("SELECT atom, version FROM atoms WHERE atom = ?", (atom,)).fetchone()
        if row is None:
            raise KeyError("no atom %s" % atom)
        return {"atom": row[0], "version": row[1]}

    # -- mutation --------------------------------------------------------------------------
    def _mutable(self, composite_id: int, expected_version: int):
        row = self._row(composite_id)
        if row[3]:
            raise RetiredComposite("composite %d is retired" % composite_id)
        if type(expected_version) is not int or expected_version != row[2]:
            raise StaleVersion(
                "composite %d is at version %d, not %r" % (composite_id, row[2], expected_version)
            )
        return row

    def _bump(self, composite_id: int, version: int) -> None:
        changed = self._conn.execute(
            "UPDATE composites SET version = version + 1 WHERE id = ? AND version = ?",
            (composite_id, version),
        ).rowcount
        if changed != 1:
            raise StaleVersion("composite %d moved during the mutation" % composite_id)

    def add_member(self, composite_id, edge: Iterable[str], expected_version: int) -> int:
        composite_id = self._code(composite_id)
        edge = normalise_edge(edge)
        with self._write():
            self._mutable(composite_id, expected_version)
            atom = _atom(edge)
            if self._conn.execute(
                "SELECT 1 FROM members WHERE composite_id = ? AND atom = ?", (composite_id, atom)
            ).fetchone():
                raise KeyError("composite %d already holds %s" % (composite_id, atom))
            self._conn.execute("INSERT OR IGNORE INTO atoms (atom) VALUES (?)", (atom,))
            self._conn.execute(
                "INSERT INTO members (composite_id, atom, atom_version) VALUES (?, ?, 1)",
                (composite_id, atom),
            )
            self._bump(composite_id, expected_version)
            return expected_version + 1

    def remove_member(self, composite_id, edge: Iterable[str], expected_version: int) -> int:
        composite_id = self._code(composite_id)
        edge = normalise_edge(edge)
        with self._write():
            self._mutable(composite_id, expected_version)
            atom = _atom(edge)
            changed = self._conn.execute(
                "DELETE FROM members WHERE composite_id = ? AND atom = ?", (composite_id, atom)
            ).rowcount
            if changed != 1:
                raise KeyError("composite %d does not hold %s" % (composite_id, atom))
            self._reclaim(atom)
            self._bump(composite_id, expected_version)
            return expected_version + 1

    def _reclaim(self, atom: str) -> None:
        self._conn.execute(
            "DELETE FROM atoms WHERE atom = ? AND NOT EXISTS "
            "(SELECT 1 FROM members WHERE members.atom = atoms.atom)",
            (atom,),
        )

    def retire(self, composite_id, expected_version: int) -> int:
        composite_id = self._code(composite_id)
        with self._write():
            self._mutable(composite_id, expected_version)
            self._conn.execute(
                "INSERT INTO tombstones (composite_id, version) VALUES (?, ?)",
                (composite_id, expected_version + 1),
            )
            self._conn.execute("UPDATE composites SET retired = 1 WHERE id = ?", (composite_id,))
            self._bump(composite_id, expected_version)
            return expected_version + 1

    # -- measurement and guards ------------------------------------------------------------
    def compact(self) -> int:
        """Drop unreferenced atoms; ids, keys, tombstones and member rows are never dropped."""
        with self._write():
            return self._conn.execute(
                "DELETE FROM atoms WHERE NOT EXISTS "
                "(SELECT 1 FROM members WHERE members.atom = atoms.atom)"
            ).rowcount

    def table_names(self) -> set[str]:
        return {
            row[0]
            for row in self._conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        }

    def assert_frozen_graph_untouched(self, frozen: Iterable[str]) -> None:
        overlap = set(frozen) & self.table_names()
        if overlap:
            raise FrozenGraphError("the primitive owns table(s) in the frozen graph: %r" % sorted(overlap))

    def page_count(self) -> int:
        return int(self._conn.execute("PRAGMA page_count").fetchone()[0])

    def page_size(self) -> int:
        return int(self._conn.execute("PRAGMA page_size").fetchone()[0])

    def byte_size(self) -> int:
        return self.page_count() * self.page_size()


def demo() -> int:
    primitive = Primitive(":memory:")
    try:
        cid = primitive.register(
            ("alpha", "bravo", "charlie"),
            (("alpha", "bravo"), ("alpha", "charlie"), ("bravo", "charlie")),
        )
        print("registered id=%d version=%d members=%d"
              % (cid, primitive.resolve(cid)["version"], len(primitive.members(cid))))
        primitive.add_member(cid, ("charlie", "delta"), 1)
        primitive.retire(cid, 2)
        print("retired id=%d version=%d tombstone=%s tables=%s pages=%d"
              % (cid, primitive.resolve(cid)["version"], primitive.resolve(cid)["retired"],
                 ",".join(sorted(primitive.table_names())), primitive.page_count()))
        return 0
    finally:
        primitive.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="run a small in-memory demonstration")
    args = parser.parse_args(argv)
    if not args.demo:
        parser.error("--demo is required; this module is a library, not a cell runner")
    return demo()


if __name__ == "__main__":
    sys.exit(main())
