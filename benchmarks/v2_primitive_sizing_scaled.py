"""Does the primitive's page-bound per-object cost fall as the world grows?

The first sizing measured one 120-cycle world and found 1,175 bytes per composite, which is an upper
bound because 33 pages are dominated by page granularity. This module measures the same primitive on
the same seed at four times the horizon and at twice the stimulus density, so the per-object figure can
be read against object count rather than assumed.

Read-only: no arm, no target, no freeze, no grant, no engine change.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

from benchmarks import a1_arms, a1_c5_target_timing as timing, engine_stamp
from benchmarks.a1_arms import ACQ_SOURCE
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.v1_carrier_identity import _canonical, _store_facts
from benchmarks.v2_primitive_sizing import measure
from benchmarks.a2_sham_feasibility import CYCLES as BASE_CYCLES

SEED = 20800101
OUT = "docs/v2_primitive_sizing_scaled.json"
WORLDS = (
    {"label": "reference-120", "cycles": BASE_CYCLES, "events_per_cycle": 8},
    {"label": "longer-480", "cycles": BASE_CYCLES * 4, "events_per_cycle": 8},
    {"label": "denser-2x", "cycles": BASE_CYCLES, "events_per_cycle": 16},
)


def replay(cycles: int, events_per_cycle: int) -> tuple[list[tuple[str, ...]], dict]:
    world = generate_compositional_world(seed=SEED, cycles=cycles,
                                         events_per_cycle=events_per_cycle,
                                         regime_cycles=cycles + 1)
    db_path = _make_scratch_db("v2_sizing_scaled")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = timing.CAP
    acq_lo, acq_hi = timing.PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * events_per_cycle, acq_hi * events_per_cycle
    paths: list[tuple[str, ...]] = []
    for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
        in_acq = event_lo <= i < event_hi
        if in_acq and not trainable:
            continue
        if i % events_per_cycle == 0:
            memory.current_cycle = i // events_per_cycle
        memory.store(text, event_type="observe",
                     source=ACQ_SOURCE if in_acq else "env")
        if (i + 1) % events_per_cycle:
            continue
        report = service.run_sleep_cycle()
        for loop in getattr(report, "loops", []) or []:
            path = tuple(getattr(loop, "path", []) or ())
            if len(path) >= 2:
                paths.append(path)
    facts = _store_facts(db_path)
    memory.close()
    return paths, facts


def size_world(spec: dict) -> dict:
    paths, facts = replay(spec["cycles"], spec["events_per_cycle"])
    curve = collections.Counter()
    appearances = collections.Counter(paths)
    for path in appearances:
        curve[appearances[path]] += 1
    per_key = collections.Counter()
    for path, count in appearances.items():
        per_key[_canonical(path)] += count
    atoms = min(facts["rows"]["cooccurrences"] or 0, 756)
    admission = {}
    for threshold in (2, 3, 5):
        admitted = sum(count for appearances_, count in curve.items() if appearances_ >= threshold)
        measured = measure(admitted, _pairs(atoms))
        admission["m>=%d" % threshold] = {
            "composites": admitted,
            "primitive_bytes": measured["bytes"],
            "bytes_per_composite": round(measured["bytes"] / admitted, 1) if admitted else None,
            "pages": measured["bytes"] // measured["page_size"],
        }
    pair_bytes = (facts["bytes"].get("cooccurrences", 0) + facts["bytes"].get("precedes", 0)
                  + facts["bytes"].get("tag_counts", 0))
    return {
        "label": spec["label"],
        "seed": SEED,
        "cycles": spec["cycles"],
        "events_per_cycle": spec["events_per_cycle"],
        "carrier_appearances": len(paths),
        "distinct_paths": len(appearances),
        "distinct_node_sets": len(per_key),
        "atoms": atoms,
        "graph_rows": facts["rows"],
        "pair_table_bytes": pair_bytes,
        "store_bytes": facts["db_bytes"],
        "admission": admission,
    }


def _pairs(count: int) -> list[tuple[str, str]]:
    pairs = []
    for i in range(16):
        for j in range(i + 1, 16):
            pairs.append(("tag%02d" % i, "tag%02d" % j))
    return (pairs * (1 + count // len(pairs)))[:count] or pairs[:1]


def stable(doc: dict) -> dict:
    """The projection --check compares: the store's page allocation is not bit-reproducible.

    Row counts, carrier counts and the pair tables' pages are stable; the event table's overflow pages
    move by a page or two between replays, which is recorded per world but not asserted.
    """
    out = dict(doc)
    out["worlds"] = []
    for world in doc["worlds"]:
        copy = dict(world)
        copy.pop("store_bytes", None)
        out["worlds"].append(copy)
    return out


def build() -> dict:
    worlds = [size_world(spec) for spec in WORLDS]
    reference = worlds[0]["admission"]["m>=2"]["bytes_per_composite"]
    for world in worlds:
        per = world["admission"]["m>=2"]["bytes_per_composite"]
        world["per_object_vs_reference"] = round(per / reference, 3) if per and reference else None
    return {
        "kind": "v2_primitive_sizing_scaled",
        "date": "2026-11-15",
        "note": ("one seed, three worlds: the same stream for 120 and 480 cycles, and the same horizon at twice the "
                 "stimulus density. The primitive side is the same schema-with-rows measurement as the base sizing."),
        "worlds": worlds,
        "comparison": {
            "reference_bytes_per_composite": reference,
            "objects_at_m2": [w["admission"]["m>=2"]["composites"] for w in worlds],
            "bytes_per_composite_at_m2": [w["admission"]["m>=2"]["bytes_per_composite"] for w in worlds],
        },
    }


DOC = Path("docs/V2-PRIMITIVE-SIZING-SCALED.md")


def render_doc(d: dict) -> str:
    worlds = d["worlds"]
    ref = worlds[0]
    lines = []
    for w in worlds:
        m2 = w["admission"]["m>=2"]
        m3 = w["admission"]["m>=3"]
        m5 = w["admission"]["m>=5"]
        lines.append(
            "| `%s` | %d | %d | %d | %d | %d | %d | %d | %s | %s |" % (
                w["label"], w["cycles"], w["events_per_cycle"], w["carrier_appearances"],
                w["distinct_node_sets"], m2["composites"], m3["composites"], m5["composites"],
                format(m2["bytes_per_composite"], ",") + " | " + str(m2["pages"]),
                str(w.get("per_object_vs_reference")),
            )
        )
    table = "\n".join(lines)
    longest = max(worlds, key=lambda w: w["admission"]["m>=2"]["composites"])
    densest = max(worlds, key=lambda w: w["events_per_cycle"])
    longer = max(worlds, key=lambda w: w["cycles"])
    return f"""# Primitive sizing on a longer and a denser world

**Status:** `MEASUREMENT. Planning-only; authorises no code, no table, no build.`

Companion to [`V2-PRIMITIVE-SIZING`](V2-PRIMITIVE-SIZING.md). That page measured one 120-cycle world and reported
{ref['admission']['m>=2']['bytes_per_composite']:,} bytes per composite, noting the figure was page-bound and therefore an upper
bound. This page tests the note: same seed, same generator, three worlds — the reference horizon, four times the horizon, and
twice the stimulus density. Rendered from [`docs/v2_primitive_sizing_scaled.json`](v2_primitive_sizing_scaled.json) by
`python -m benchmarks.v2_primitive_sizing_scaled`.

## 1. The three worlds

| World | Cycles | Events/cycle | Carrier appearances | Distinct node sets | Objects at `m>=2` | at `m>=3` | at `m>=5` | Bytes/object at `m>=2` | Pages | vs reference |
|---|---|---|---|---|---|---|---|---|---|---|
{table}

## 2. The expectation did not hold

The conjecture was that a bigger world would amortise the fixed page cost, so bytes per object would fall. It did not.
The four-times-longer world has **{longer['admission']['m>=2']['composites']} objects at {format(longer['admission']['m>=2']['bytes_per_composite'], ',')} bytes each**, and the twice-denser world has
**{densest['admission']['m>=2']['composites']} at {format(densest['admission']['m>=2']['bytes_per_composite'], ',')}** — both at or above the reference's {ref['admission']['m>=2']['bytes_per_composite']:,}. Nothing here is amortising.

## 3. Why, and what would actually test amortisation

The object population saturates, not the page cost. Carrier appearances grow fourfold ({ref['carrier_appearances']} to
{longer['carrier_appearances']}) while *admitted* objects grow only from {ref['admission']['m>=2']['composites']} to {longer['admission']['m>=2']['composites']}, because the compositional
generator draws from a fixed universe of 16 tags: the number of distinct triples is bounded well below the appearance count,
and after one horizon almost every triple that can clear `m>=2` already has. Density raises counts, not structures — the
denser world found {densest['distinct_node_sets']} distinct node sets against the reference's {ref['distinct_node_sets']}.

So a longer or denser run of this world cannot test amortisation: it saturates the thing that would have to grow. The
measurement that would is a **wider tag universe**, which the compositional generator does not provide — the scale ladders
in `benchmarks/scale_streams.py` do, and that is where a real test belongs. Until then, the honest reading of both sizings
is that a composite costs on the order of a kilobyte, flat, at every population this project can currently generate.

## 4. What this changes

- The base page's note that a world with ten times the composites would give a much smaller bytes-per-object was a
  **conjecture**, and it is now labelled as untested rather than expected.
- The cost answer for the charter does not move: at ~1 KB per composite and populations in the low hundreds, the primitive
  is tens of kilobytes against a store that reaches hundreds of megabytes. Storage is not the constraint; the earning test
  is.
- The scaling question is now a question about the **structure count**, not the horizon: to make the primitive look cheap you
  need more distinct structures, not more cycles.

## 5. Limits

One seed, one generator, three worlds. The primitive side is the same schema-with-rows measurement as the base sizing, not
an implementation. The horizons share a seed, so the two horizon worlds are the same stream truncated, not independent
worlds; nothing here estimates variance across worlds.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--doc", action="store_true")
    args = parser.parse_args()
    if args.check:
        stored = stable(json.loads(Path(OUT).read_text(encoding="utf-8")))
        fresh = stable(build())
        if stored != fresh:
            differing = sorted(k for k in set(stored) | set(fresh) if stored.get(k) != fresh.get(k))
            print("FAIL: the artifact drifted from a fresh replay: %r" % (differing,))
            return 1
        print("scaled sizing: clean (rebuild matches)")
        return 0
    doc = build()
    if args.doc:
        DOC.write_text(render_doc(doc), encoding="utf-8")
        print("wrote", DOC)
        return 0
    if args.write:
        with open(OUT, "w", encoding="utf-8") as handle:
            json.dump(engine_stamp.stamp(doc), handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print("wrote", OUT)
    print(json.dumps(doc["comparison"], indent=1))
    for w in doc["worlds"]:
        print(w["label"], w["carrier_appearances"], w["distinct_node_sets"],
              w["admission"]["m>=2"]["composites"], w["admission"]["m>=2"]["bytes_per_composite"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
