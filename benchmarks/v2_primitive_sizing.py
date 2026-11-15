"""What would the mutable-identity primitive cost on a real V1 world?

Reads the identity artifact (measured carrier counts and store facts) and sizes the primitive's
tables for it. The primitive side is a schema-with-rows measurement in SQLite, not an
implementation: nothing here is authorised to run in the engine.

Read-only: no arm, no target, no freeze, no grant, no engine change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

SOURCE = Path("docs/v1_carrier_identity.json")
OUT = "docs/v2_primitive_sizing.json"

SCHEMA = """
CREATE TABLE atoms (a TEXT NOT NULL, b TEXT NOT NULL, PRIMARY KEY (a, b));
CREATE TABLE composites (id TEXT PRIMARY KEY, created_cycle INTEGER NOT NULL,
                         version INTEGER NOT NULL, retired_cycle INTEGER);
CREATE TABLE composite_keys (key TEXT PRIMARY KEY, composite_id TEXT NOT NULL UNIQUE,
                             kind TEXT NOT NULL, first_cycle INTEGER NOT NULL);
CREATE TABLE members (composite_id TEXT NOT NULL, position INTEGER NOT NULL,
                      atom_a TEXT NOT NULL, atom_b TEXT NOT NULL,
                      member_version INTEGER NOT NULL,
                      PRIMARY KEY (composite_id, position));
"""
ATOM_INDEX = "CREATE INDEX members_by_atom ON members (atom_a, atom_b);"


def _pairs(count: int) -> list[tuple[str, str]]:
    """A deterministic stand-in vocabulary with the measured number of pairs."""
    pairs = []
    for i in range(16):
        for j in range(i + 1, 16):
            pairs.append(("tag%02d" % i, "tag%02d" % j))
    return pairs[:count]


def measure(composites: int, atoms: list[tuple[str, str]], history: int = 0,
            atom_index: bool = True) -> dict:
    """Materialise the primitive's tables with this many rows and measure the file."""
    handle = tempfile.NamedTemporaryFile(prefix="v2_sizing_", suffix=".db", delete=False)
    handle.close()
    path = Path(handle.name)
    con = sqlite3.connect(str(path))
    schema = SCHEMA
    if history:
        # Keeping history changes the key: one row per (composite, position, version).
        schema = schema.replace("PRIMARY KEY (composite_id, position))",
                                "PRIMARY KEY (composite_id, position, member_version))")
    con.executescript(schema)
    if atom_index:
        con.execute(ATOM_INDEX)
    con.executemany("INSERT INTO atoms VALUES (?, ?)", atoms)
    rows = []
    for i in range(composites):
        cid = "%032x" % (i + 1)
        rows.append((cid, i % 120, 1, None))
    con.executemany("INSERT INTO composites VALUES (?, ?, ?, ?)", rows)
    con.executemany("INSERT INTO composite_keys VALUES (?, ?, ?, ?)",
                    [("%032x" % (i + 1), "%032x" % (i + 1), "cycle3", i % 120)
                     for i in range(composites)])
    refs = []
    for i in range(composites):
        cid = "%032x" % (i + 1)
        for position in range(3):
            a, b = atoms[(3 * i + position) % len(atoms)]
            refs.append((cid, position, a, b, 1))
    con.executemany("INSERT INTO members VALUES (?, ?, ?, ?, ?)", refs)
    if history:
        old = []
        for i in range(composites):
            cid = "%032x" % (i + 1)
            for position in range(3):
                a, b = atoms[(3 * i + position) % len(atoms)]
                for version in range(2, 2 + history):
                    old.append((cid, position, a, b, version))
        con.executemany("INSERT INTO members VALUES (?, ?, ?, ?, ?)", old)
    con.commit()
    con.execute("VACUUM")
    pages = con.execute("PRAGMA page_count").fetchone()[0]
    page_size = con.execute("PRAGMA page_size").fetchone()[0]
    counted = {table: con.execute("SELECT COUNT(*) FROM %s" % table).fetchone()[0]
               for table in ("atoms", "composites", "composite_keys", "members")}
    con.close()
    path.unlink(missing_ok=True)
    return {"bytes": pages * page_size, "pages": pages, "page_size": page_size, "rows": counted}


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    curve = {int(k): v for k, v in source["appearances_per_node_set"].items()}
    graph = source["graph"]
    atoms = _pairs(graph["rows"]["cooccurrences"])
    pair_bytes = graph["bytes"]["cooccurrences"] + graph["bytes"]["precedes"] + graph["bytes"]["tag_counts"]

    admission = {}
    for threshold in (2, 3, 5, 10, 20):
        admitted = sum(count for appearances, count in curve.items() if appearances >= threshold)
        measured = measure(admitted, atoms)
        admission["m>=%d" % threshold] = {
            "composites": admitted,
            "references": measured["rows"]["members"],
            "registry_rows": measured["rows"]["composite_keys"],
            "primitive_bytes": measured["bytes"],
            "bytes_per_composite": round(measured["bytes"] / admitted, 1),
            "ratio_to_pair_tables": round(measured["bytes"] / pair_bytes, 3),
            "ratio_to_store": round(measured["bytes"] / graph["db_bytes"], 5),
        }

    top = admission["m>=2"]
    base = measure(top["composites"], atoms)
    no_index = measure(admission["m>=2"]["composites"], atoms, atom_index=False)
    history = measure(admission["m>=2"]["composites"], atoms, history=1)
    return {
        "kind": "v2_primitive_sizing",
        "date": "2026-11-15",
        "source": {"artifact": str(SOURCE), "sha256": digest},
        "world": {
            "cycles": 120,
            "carrier_appearances": source["appearances"],
            "distinct_carriers": source["distinct_node_sets"],
            "graph_rows": graph["rows"],
            "graph_bytes": graph["bytes"],
            "store_bytes": graph["db_bytes"],
            "page_size": graph["page_size"],
        },
        "atoms": {"count": len(atoms), "note": "count-matched to the measured cooccurrence table"},
        "headline": {
            "threshold": "m>=2",
            "composites": top["composites"],
            "references": top["references"],
            "references_per_atom": round(top["references"] / len(atoms), 1),
            "distinct_carriers": source["distinct_node_sets"],
            "admitted_share": round(top["composites"] / source["distinct_node_sets"], 3),
            "primitive_bytes": top["primitive_bytes"],
            "pair_table_bytes": pair_bytes,
            "store_bytes": graph["db_bytes"],
            "store_bytes_that_are_events": graph["bytes"]["events"],
            "ratio_to_pair_tables": top["ratio_to_pair_tables"],
            "ratio_to_store": top["ratio_to_store"],
            "pages": top["primitive_bytes"] // graph["page_size"],
            "page_bound": True,
        },
        "admission": admission,
        "index": {"with_atom_index_bytes": base["bytes"], "without_atom_index_bytes": no_index["bytes"],
                  "index_cost_bytes": base["bytes"] - no_index["bytes"]},
        "churn": {
            "storage_under_mutation": "invariant: a member row is updated in place and versioned by an integer",
            "history_variant": {"extra_rows_per_composite": 3, "bytes": history["bytes"],
                                "cost_over_current": history["bytes"] - base["bytes"]},
        },
        "assumptions": [
            "the primitive side is a schema-with-rows measurement, not the engine's implementation",
            "atoms are shared and immutable, so the atom table is not copied per composite",
            "ids are 32 hex characters, the width the engine's own carrier ids use",
            "one world (120 cycles); no second world was measured",
            "no mutation history is stored, per the specification's version-counter rule",
        ],
    }


DOC = Path("docs/V2-PRIMITIVE-SIZING.md")


def render_doc(d: dict) -> str:
    """The page, rendered from the artifact. Never hand-typed: a test compares the two."""
    h, w = d["headline"], d["world"]
    m2, m3, m5, m10, m20 = (d["admission"][k] for k in ("m>=2", "m>=3", "m>=5", "m>=10", "m>=20"))
    events_share = round(100 * h["store_bytes_that_are_events"] / h["store_bytes"], 1)
    per_composite = round(h["primitive_bytes"] / h["composites"])
    pct_store = round(100 * h["ratio_to_store"], 2)
    population_span = round(m2["composites"] / m20["composites"], 2)
    history_pct = round(100 * d["churn"]["history_variant"]["cost_over_current"] / m2["primitive_bytes"])
    page = w["page_size"]
    rows, gbytes = w["graph_rows"], w["graph_bytes"]
    return f"""# The primitive's storage cost on a real V1 world

**Status:** `PLANNING-ONLY ESTIMATE. Authorises no code, no table, no build.`

Serves [`DECISION-V2-PRIMITIVE-RESOLUTIONS`](DECISION-V2-PRIMITIVE-RESOLUTIONS.md) and §12 of
[`V2-MUTABLE-IDENTITY-SPEC`](V2-MUTABLE-IDENTITY-SPEC.md): the charter should know what it is buying before it signs. The
numbers come from [`docs/v2_primitive_sizing.json`](v2_primitive_sizing.json); this page is rendered from that artifact by
`python -m benchmarks.v2_primitive_sizing --doc`, and a test fails if the two differ.

## 1. What was measured, and what was modelled

Two different things, kept apart:

- **Measured.** The store itself: a replay of one no-arm world (120 cycles), read with SQLite's own `dbstat` so every
  table's pages are counted, not estimated.
- **Modelled.** The primitive's tables. Nothing implements the primitive, so its four tables were created in SQLite and
  filled with the measured row counts, then measured the same way. That is a sizing estimate, not a benchmark.

Both sides use {page}-byte pages, and the per-table bytes reconcile to the store's page count except for one page —
SQLite's schema page. The store's **total** size is not bit-reproducible: the event table's overflow pages move by a page or
two between replays, which is why the identity check asserts row counts and the pair tables' pages rather than the total.

## 2. The store as it actually is

| Table | Rows | Bytes |
|---|---|---|
| `events` | {rows['events']:,} | {gbytes['events']:,} |
| `precedes` | {rows['precedes']:,} | {gbytes['precedes']:,} |
| `cooccurrences` | {rows['cooccurrences']:,} | {gbytes['cooccurrences']:,} |
| `tag_counts` | {rows['tag_counts']:,} | {gbytes['tag_counts']:,} |
| `sleep_cycles` | {rows['sleep_cycles']:,} | {gbytes['sleep_cycles']:,} |
| **whole store** | — | **{h['store_bytes']:,}** |

**Events are {events_share}% of the store.** The pair graph the primitive annotates is {h['pair_table_bytes']:,} bytes —
{rows['cooccurrences']:,} co-occurrence rows, {rows['precedes']:,} precedence rows and {rows['tag_counts']:,} tag rows. Any overhead figure quoted against the
whole store is really a statement about how loud the event text is; the honest comparator is the pair tables.

## 3. Admission is the lever, and it is not fixed

The decision adopts admission on total appearances `m` without fixing `m`. That matters more than any other choice here:

| Threshold | Composites | References | Primitive bytes | Ratio to pair tables | Ratio to store |
|---|---|---|---|---|---|
| `m>=2` | {m2['composites']} | {m2['references']} | {m2['primitive_bytes']:,} | {m2['ratio_to_pair_tables']}× | {m2['ratio_to_store']} |
| `m>=3` | {m3['composites']} | {m3['references']} | {m3['primitive_bytes']:,} | {m3['ratio_to_pair_tables']}× | {m3['ratio_to_store']} |
| `m>=5` | {m5['composites']} | {m5['references']} | {m5['primitive_bytes']:,} | {m5['ratio_to_pair_tables']}× | {m5['ratio_to_store']} |
| `m>=10` | {m10['composites']} | {m10['references']} | {m10['primitive_bytes']:,} | {m10['ratio_to_pair_tables']}× | {m10['ratio_to_store']} |
| `m>=20` | {m20['composites']} | {m20['references']} | {m20['primitive_bytes']:,} | {m20['ratio_to_pair_tables']}× | {m20['ratio_to_store']} |

At the loosest threshold the primitive holds {h['composites']} objects — {round(100*h['admitted_share'],1)}% of the {h['distinct_carriers']} distinct carriers the world
produces — and at `m>=20` it holds {m20['composites']}. That is a {population_span}× range in population from one unset parameter, so the
charter should fix `m` with the population it wants, not default to "seen twice".

## 4. The cost

At `m>=2`: **{h['primitive_bytes']:,} bytes** — {h['pages']} pages, {h['ratio_to_pair_tables']}× the pair tables it annotates, and **{pct_store}% of the
store**.

Per composite that is {per_composite:,} bytes, which is an upper bound rather than a marginal cost: at this scale the tables
are page-bound, so a few rows cost a whole {page}-byte page. The figure that scales is the reference count, not the byte
count.

The atom index costs {d['index']['index_cost_bytes']:,} bytes at this population; without it the tables are
{d['index']['without_atom_index_bytes']:,}.

## 5. References: where the sharing shows up

{h['references']} references over {d['atoms']['count']} atoms — {h['references_per_atom']} references per atom, three per composite. The atom table is
{d['atoms']['count']} rows and is not copied per composite, which is the collision rule doing its job: sharing is free because
atoms are immutable, and what is per-composite is the reference.

## 6. Mutation does not grow the store

Under binding-level copy-on-write a member change updates one row and increments an integer, so storage is invariant in the
number of mutations. Keeping history instead — one row per version — costs
{d['churn']['history_variant']['cost_over_current']:,} bytes at this population ({d['churn']['history_variant']['bytes']:,} against
{m2['primitive_bytes']:,}), about {history_pct}% more, and it buys a history the specification does not need.

## 7. What this does not establish

- **Not built.** The primitive side is a schema with rows, not the engine's implementation; a real implementation could be
  smaller or larger depending on its indexes.
- **One world.** 120 cycles, one seed (recorded in the source artifact, not here). No denser or longer world was sized.
- **Page-bound.** At {h['pages']} pages the measurement is dominated by page granularity, so the per-composite figure is an upper
  bound. A world with ten times the composites would give a much smaller bytes-per-object.
- **Store size moves.** The total is a page or two unstable between replays, so the store ratios carry that noise; the pair
  tables' pages and every row count are stable.
- **`m` is unset.** The five rows above are five different primitives, not one estimate with error bars.

## 8. What it does say

Storage is not the obstacle. At {h['primitive_bytes']:,} bytes the primitive is {pct_store}% of this world's store and about
{h['ratio_to_pair_tables']}× the pair tables it annotates — small enough that the decision to build should turn entirely on
the earning test, which is the one thing no storage measurement can answer.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--doc", action="store_true")
    args = parser.parse_args()
    if args.check:
        stored = json.loads(Path(OUT).read_text(encoding="utf-8"))
        fresh = build()
        if stored != fresh:
            differing = sorted(k for k in set(stored) | set(fresh) if stored.get(k) != fresh.get(k))
            print("FAIL: the artifact drifted from a fresh measurement: %r" % (differing,))
            return 1
        print("primitive sizing: clean (rebuild matches, %d composites at m>=2)"
              % fresh["admission"]["m>=2"]["composites"])
        return 0
    doc = build()
    if args.doc:
        DOC.write_text(render_doc(doc), encoding="utf-8")
        print("wrote", DOC)
        return 0
    if args.write:
        with open(OUT, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print("wrote", OUT)
    print(json.dumps(doc["admission"], indent=1)[:1200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
