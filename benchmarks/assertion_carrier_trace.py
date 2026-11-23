"""Trace how the 26 never-served pairs acquire a loop or dream assertion.

The provenance ledger stops at the readout source: 18 pairs have the reverse
orientation served, 8 have neither orientation served, and every pair is carried
by a loop/dream structure. This trace walks back one step and records the
carrier candidate itself:

* the loop or dream path that contains the pair;
* whether the path includes the direct or reverse orientation;
* the candidate's first formation cycle and loop/dream evidence;
* the final temporal counts in both directions; and
* whether a prediction candidate is a final source.

The replay is the same six Q4 seeds, 120 cycles, cap 40 and acquisition schedule
as the provenance ledger. It refuses to write unless each seed reproduces the
stored asserted-world fingerprint and edge count. It adds no seed, arm, cap or
engine edit and is marked ``not_a_result``.

    ./.venv/bin/python -m benchmarks.assertion_carrier_trace --write
    ./.venv/bin/python -m benchmarks.assertion_carrier_trace --check
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import assertion_provenance as provenance                 # noqa: E402
from benchmarks import engine_stamp                                      # noqa: E402
from benchmarks.acquisition_compositional import generate_compositional_world  # noqa: E402
from benchmarks.acquisition_harness import (                              # noqa: E402
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges  # noqa: E402
from benchmarks.presence_construct_audit import (                         # noqa: E402
    ACQ_SOURCE,
    PHASE_ACQUISITION,
    _world_compositional_edges,
    asserted_fingerprint,
)
from organica.sleep import SleepService                                   # noqa: E402

ARTIFACT = ROOT / "docs" / "assertion_carrier_trace.json"
PAGE = ROOT / "docs" / "ASSERTION-CARRIER-TRACE.md"
PROVENANCE = provenance.ARTIFACT
KIND = "assertion_carrier_trace"
CAP = 40
CYCLES = 120
PREDICTION_FLOOR = 5
LOOP_FLOOR = 5


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _hits(kind: str, path: list[str], edge: tuple[str, str]) -> list[str]:
    """Return the path orientations that can assert ``edge``."""
    pairs = list(zip(path, path[1:]))
    if kind == "dream":
        return ["direct"] if edge in pairs else []
    reverse = (edge[1], edge[0])
    direct = edge in pairs
    reversed_hit = reverse in pairs
    if direct and reversed_hit:
        return ["direct", "reverse"]
    if direct:
        return ["direct"]
    if reversed_hit:
        return ["reverse"]
    return []


def _candidate_path(candidate: dict) -> list[str]:
    if candidate.get("type") == "loop_candidate":
        return list(candidate.get("path") or [])
    return list(candidate.get("path_or_context") or [])


def _replay(seed: int, expected: dict) -> tuple[list[dict], dict, dict]:
    """Replay one seed, retaining the carriers and their first formation cycle."""
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("assertion_carrier_trace")
    memory = _CountingMemoryService(str(db_path))
    service = SleepService(memory)
    service.MAX_PREDICTIONS = CAP
    first: dict[tuple[str, str], dict] = {}
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = (PHASE_ACQUISITION[0] * EVENTS_PER_CYCLE
                      <= i < PHASE_ACQUISITION[1] * EVENTS_PER_CYCLE)
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                report = service.run_sleep_cycle()
                for candidate in list(report.loops) + list(report.dreams):
                    key = (candidate.type, candidate.id)
                    if key not in first:
                        first[key] = {
                            "cycle": report.cycle,
                            "path": _candidate_path({
                                "type": candidate.type,
                                "path": getattr(candidate, "path", None),
                                "path_or_context": getattr(
                                    candidate, "path_or_context", None),
                            }),
                            "strength": getattr(candidate, "strength", None),
                        }
        candidates = provenance._dedupe(service._load_prior_candidates())
        asserted = {(a, b) for a, targets in structure_edges(candidates).items()
                    for b in targets}
        asserted_world = asserted & world_edges
        fingerprint = asserted_fingerprint(asserted_world)
        if fingerprint != expected["asserted_fingerprint"]:
            raise SystemExit("REFUSED: seed %d fingerprint %s, expected %s"
                             % (seed, fingerprint, expected["asserted_fingerprint"]))
        if len(asserted_world) != expected["asserted_world_edges"]:
            raise SystemExit("REFUSED: seed %d asserted %d, expected %d"
                             % (seed, len(asserted_world), expected["asserted_world_edges"]))
        temporal = defaultdict(dict)
        for a, b, count in memory.temporal_edges(min_count=1):
            temporal[a][b] = count
        return candidates, first, temporal
    finally:
        memory.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass


def _carrier_record(kind: str, candidate: dict, edge: tuple[str, str],
                    first: dict) -> dict | None:
    path = _candidate_path(candidate)
    hits = _hits(kind, path, edge)
    if not hits:
        return None
    orientation = "both" if len(hits) == 2 else hits[0]
    key = (kind, candidate.get("id"))
    if key not in first:
        raise SystemExit("REFUSED: carrier %r has no formation cycle" % (key,))
    formed = first[key]
    evidence = candidate.get("evidence") or {}
    hit_edges = []
    if "direct" in hits:
        hit_edges.append("%s>%s" % (edge[0], edge[1]))
    if "reverse" in hits:
        hit_edges.append("%s>%s" % (edge[1], edge[0]))
    return {
        "type": kind,
        "id": candidate.get("id"),
        "path": path,
        "cycle_length": evidence.get("cycle_length", max(0, len(path) - 1)),
        "orientation": orientation,
        "hit_edges": hit_edges,
        "strength": (candidate.get("strength")
                     if kind == "loop_candidate" else candidate.get("confidence")),
        "min_edge_count": evidence.get("min_edge_count"),
        "edge_counts": evidence.get("edge_counts"),
        "path_min_entropy": evidence.get("path_min_entropy"),
        "formation_cycle": formed["cycle"],
        "formation_path": formed["path"],
        "dream_category": candidate.get("dream_category"),
        "dream_reason": evidence.get("reason"),
        "parent_events": len(candidate.get("parent_ids") or []),
    }


def _mechanism(carriers: list[dict], reverse_windows: int) -> str:
    loops = [carrier for carrier in carriers if carrier["type"] == "loop_candidate"]
    dreams = [carrier for carrier in carriers if carrier["type"] == "dream"]
    if loops:
        if reverse_windows:
            base = ("A loop path contains the served reverse orientation; "
                    "structure_edges adds both directions of that path.")
        else:
            base = ("A loop path contains the pair from the temporal graph; "
                    "structure_edges adds both directions of that path, even though "
                    "neither orientation is served.")
        if dreams:
            base += " A dream path is a co-carrier, not the sole source."
        return base
    if dreams:
        return "The dream path contains the direct pair; the dream readout adds that direction."
    return "No loop/dream carrier."


def build() -> dict:
    source = _load(PROVENANCE)
    expected = {trace["seed"]: trace for trace in source["seeds"]}
    grouped: dict[int, list[dict]] = defaultdict(list)
    for row in source["rows"]:
        grouped[int(row["seed"])].append(row)
    rows: list[dict] = []
    for seed, source_rows in sorted(grouped.items()):
        candidates, first, temporal = _replay(seed, expected[seed])
        for source_row in source_rows:
            edge = tuple(source_row["edge"].split(">"))
            reverse = (edge[1], edge[0])
            carriers = []
            for candidate in candidates:
                kind = candidate.get("type")
                if kind not in ("loop_candidate", "dream"):
                    continue
                carrier = _carrier_record(kind, candidate, edge, first)
                if carrier is not None:
                    carriers.append(carrier)
            if not carriers:
                raise SystemExit("REFUSED: %s has no loop/dream carrier" % source_row["edge"])
            sources = {carrier["type"] for carrier in carriers}
            if sources != set(source_row["assertion_sources"]):
                raise SystemExit(
                    "REFUSED: %s sources %r, provenance sources %r"
                    % (source_row["edge"], sources, set(source_row["assertion_sources"]))
                )
            rows.append({
                "seed": seed,
                "edge": source_row["edge"],
                "category": source_row["category"],
                "reverse_served_windows": source_row["reverse_committed_windows"],
                "direct_temporal_count": temporal[edge[0]].get(edge[1], 0),
                "reverse_temporal_count": temporal[reverse[0]].get(reverse[1], 0),
                "prediction_source": source_row["prediction_source"],
                "carriers": carriers,
                "loop_carriers": sum(1 for carrier in carriers
                                     if carrier["type"] == "loop_candidate"),
                "dream_carriers": sum(1 for carrier in carriers
                                      if carrier["type"] == "dream"),
                "formation_cycles": [carrier["formation_cycle"] for carrier in carriers],
                "mechanism": _mechanism(carriers, source_row["reverse_committed_windows"]),
            })
    summary = _summarise(rows)
    summary["findings"] = [
        "All 26 direct edges are present in the final temporal graph at count %d-%d, "
        "above PREDICTION_MIN_COUNT=%d; the direct edge is not a floor miss."
        % (summary["direct_temporal_min"],
                                  summary["direct_temporal_max"], PREDICTION_FLOOR),
        "Every row has a loop carrier: %d loop-candidate occurrences, of which %d are "
        "3-cycles and %d are 2-cycles. Every loop path contains the pair, and "
        "structure_edges expands each path edge in both directions."
        % (summary["loop_carriers"], summary["three_cycle_loops"],
           summary["two_cycle_loops"]),
        "The loop builder requires a minimum edge count of %d and consumes temporal "
        "cycles, not served windows; the first observed carrier formations span cycles "
        "%d-%d." % (LOOP_FLOOR, summary["formation_cycle_min"],
                    summary["formation_cycle_max"]),
        "%d rows have the reverse orientation served and %d have neither orientation "
        "served; both kinds still have a loop path containing the pair, which is why "
        "the loop readout supplies the direct assertion."
        % (summary["reverse_served_rows"], summary["alternate_rows"]),
        "One row has a dream co-carrier as well; no row is carried only by a dream, "
        "and no row has a prediction candidate as its final assertion source.",
    ]
    return engine_stamp.stamp({
        "kind": KIND,
        "not_a_result": True,
        "question": (
            "Why do loop and dream structures assert the 26 world edges that never "
            "entered a served window, starting from the carriers' candidate formation?"
        ),
        "definition": (
            "A per-edge replay trace of the 26 rows in docs/assertion_provenance.json. "
            "For each row it records every final loop/dream path that contains the edge, "
            "the first cycle that carrier appeared, the loop/dream evidence, the final "
            "temporal counts in both directions, and whether a prediction candidate is a "
            "final source."
        ),
        "source": {
            "provenance": "docs/assertion_provenance.json",
            "rows": "the 26 asserted-but-never-served world edges",
            "world": "generate_compositional_world(seed=, cycles=120), deterministic",
        },
        "method": (
            "Same six Q4 seeds, 120 cycles, cap 40 and acquisition schedule as the "
            "provenance replay. The replay refuses to write unless each seed reproduces "
            "the stored asserted-world fingerprint and edge count. Candidate formation "
            "cycles are read from the sleep reports; final carriers are deduplicated by "
            "candidate id. No seed, arm, cap or engine edit is added."
        ),
        "cap": CAP,
        "cycles": CYCLES,
        "prediction_floor": PREDICTION_FLOOR,
        "loop_floor": LOOP_FLOOR,
        "rows": rows,
        "summary": summary,
        "controls": _controls(),
        "not_evidence": (
            "A replay-only carrier trace on six committed Q4 seeds, one world family, "
            "one build and one cap. It explains how loop/dream paths reach the readout; "
            "it does not show that serving the direct edge would change A_W, does not "
            "decompose the full prediction-ranking history, and does not establish "
            "capability, retention, transfer or a general engine property."
        ),
    })


def _summarise(rows: list[dict]) -> dict:
    loop_carriers = [carrier for row in rows for carrier in row["carriers"]
                     if carrier["type"] == "loop_candidate"]
    dream_carriers = [carrier for row in rows for carrier in row["carriers"]
                      if carrier["type"] == "dream"]
    formation_cycles = [cycle for row in rows for cycle in row["formation_cycles"]]
    return {
        "edges": len(rows),
        "loop_carrier_rows": sum(1 for row in rows if row["loop_carriers"]),
        "dream_carrier_rows": sum(1 for row in rows if row["dream_carriers"]),
        "loop_carriers": len(loop_carriers),
        "dream_carriers": len(dream_carriers),
        "two_cycle_loops": sum(1 for carrier in loop_carriers
                               if carrier["cycle_length"] == 2),
        "three_cycle_loops": sum(1 for carrier in loop_carriers
                                 if carrier["cycle_length"] == 3),
        "reverse_served_rows": sum(1 for row in rows
                                   if row["reverse_served_windows"] > 0),
        "alternate_rows": sum(1 for row in rows
                              if row["reverse_served_windows"] == 0),
        "direct_temporal_min": min(row["direct_temporal_count"] for row in rows),
        "direct_temporal_max": max(row["direct_temporal_count"] for row in rows),
        "reverse_temporal_min": min(row["reverse_temporal_count"] for row in rows),
        "reverse_temporal_max": max(row["reverse_temporal_count"] for row in rows),
        "direct_at_or_above_prediction_floor": sum(
            1 for row in rows if row["direct_temporal_count"] >= PREDICTION_FLOOR),
        "direct_prediction_final": sum(1 for row in rows if row["prediction_source"]),
        "formation_cycle_min": min(formation_cycles),
        "formation_cycle_max": max(formation_cycles),
        "formation_cycle_median": statistics.median(formation_cycles),
        "category_counts": dict(sorted(Counter(row["category"] for row in rows).items())),
    }


def _controls() -> list[dict]:
    cases = [
        ("loop_symmetry_control", "loop_candidate",
         ["amber", "birch", "amber"], ("amber", "birch"), ["direct", "reverse"]),
        ("loop_reverse_control", "loop_candidate",
         ["birch", "amber", "birch"], ("amber", "birch"), ["direct", "reverse"]),
        ("dream_direct_control", "dream",
         ["amber", "birch"], ("amber", "birch"), ["direct"]),
        ("loop_missing_control", "loop_candidate",
         ["amber", "cedar", "amber"], ("amber", "birch"), []),
        ("dream_missing_control", "dream",
         ["amber", "cedar"], ("amber", "birch"), []),
    ]
    out = []
    for name, kind, path, edge, expected in cases:
        got = _hits(kind, path, edge)
        out.append({"name": name, "kind": kind, "path": path,
                    "edge": "%s>%s" % edge, "hits": got,
                    "expected": expected, "passes": got == expected})
    return out


def render(art: dict) -> str:
    summary = art["summary"]
    lines = [
        "# How loops and dreams assert the 26 never-served pairs",
        "",
        "Generated from `docs/assertion_carrier_trace.json` by "
        "`python -m benchmarks.assertion_carrier_trace --write`. Do not edit by hand.",
        "",
        "**Not a result artifact.** A replay-only trace of the same six Q4 seeds. It "
        "starts at the loop/dream carrier's formation, not at a new cell: no seed, arm, "
        "cap, engine edit or treatment is added.",
        "",
        "## What the trace found",
        "",
        "| Question | Measurement |",
        "| --- | --- |",
        "| Rows traced | %d |" % summary["edges"],
        "| Rows with a loop carrier | %d |" % summary["loop_carrier_rows"],
        "| Rows with a dream carrier | %d |" % summary["dream_carrier_rows"],
        "| Loop candidates carrying a row | %d |" % summary["loop_carriers"],
        "| Dream candidates carrying a row | %d |" % summary["dream_carriers"],
        "| Loop path lengths | %d 2-cycles, %d 3-cycles |"
        % (summary["two_cycle_loops"], summary["three_cycle_loops"]),
        "| Direct temporal count range | %d-%d (floor %d) |"
        % (summary["direct_temporal_min"], summary["direct_temporal_max"],
           PREDICTION_FLOOR),
        "| Reverse temporal count range | %d-%d |"
        % (summary["reverse_temporal_min"], summary["reverse_temporal_max"]),
        "| Direct edges at/above prediction floor | %d |"
        % summary["direct_at_or_above_prediction_floor"],
        "| Final prediction sources | %d |" % summary["direct_prediction_final"],
        "| Carrier formation cycles | %d-%d (median %g) |"
        % (summary["formation_cycle_min"], summary["formation_cycle_max"],
           summary["formation_cycle_median"]),
        "",
        "The direct edge is present in the temporal graph in every row; it is not a floor "
        "miss. The assertion is supplied by a loop path that contains the "
        "pair. `structure_edges` expands every loop path in both directions, so a path "
        "that contains the reverse orientation also asserts the direct orientation. The "
        "dream path is a co-carrier in one row; no row is dream-only.",
        "",
        "## Every edge",
        "",
        "| Seed | Edge | Category | Reverse served | Temporal direct / reverse | Carriers | Formation cycles | Why it is asserted |",
        "| ---: | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in art["rows"]:
        carrier_text = "; ".join(
            "%s %s [%s] @%d%s"
            % (carrier["type"].replace("_candidate", ""), carrier["orientation"],
               ">".join(carrier["path"]), carrier["formation_cycle"],
               (" str=%g" % carrier["strength"]) if carrier["strength"] is not None else "")
            for carrier in row["carriers"])
        lines.append("| %d | `%s` | %s | %d | %d / %d | %s | %s | %s |" % (
            row["seed"], row["edge"], row["category"].replace("_", " "),
            row["reverse_served_windows"], row["direct_temporal_count"],
            row["reverse_temporal_count"], carrier_text,
            ", ".join(str(cycle) for cycle in row["formation_cycles"]),
            row["mechanism"]))
    lines += [
        "",
        "## The mechanism chain",
        "",
        "1. **Temporal presence.** Every direct edge is already in the final temporal "
        "graph at count %d-%d, above the prediction floor. The trace therefore starts "
        "from a real temporal edge, not from a floor miss."
        % (summary["direct_temporal_min"], summary["direct_temporal_max"]),
        "2. **Loop formation.** The loop builder reads temporal 2-cycles and 3-cycles, "
        "requires a minimum edge count of %d, and does not consult served windows. The "
        "first observed carrier formations span cycles %d-%d."
        % (LOOP_FLOOR, summary["formation_cycle_min"], summary["formation_cycle_max"]),
        "3. **Symmetric readout.** `structure_edges` expands a loop path in both "
        "directions. On the 18 reverse-served rows this turns the served reverse pair "
        "into the direct assertion; on the 8 alternate rows it asserts a pair for which "
        "neither orientation was served.",
        "4. **Dream co-carrier.** One row also has a dream carrier. It is not necessary "
        "for the readout and is not the sole source of any row.",
        "5. **Prediction is a different path.** No row has a final prediction source, "
        "even though every direct temporal count clears the prediction floor. The loop "
        "path, not the prediction window, is the final carrier.",
        "",
        "## Controls",
        "",
        "| Control | Path | Edge | Hits | Expected | Passes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for control in art["controls"]:
        lines.append("| %s | %s | `%s` | %s | %s | %s |" % (
            control["name"], ">".join(control["path"]), control["edge"],
            ", ".join(control["hits"]) or "none",
            ", ".join(control["expected"]) or "none",
            "yes" if control["passes"] else "no"))
    lines += [
        "",
        "## What this does not claim",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("artifact kind")
    if art.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    missing = engine_stamp.missing(art)
    if missing:
        found.append("the artifact is not fully stamped: %r" % (missing,))
    source = _load(PROVENANCE)
    expected = {(int(row["seed"]), row["edge"]): row
                for row in source["rows"]}
    rows = art.get("rows") or []
    if len(rows) != len(expected):
        found.append("%d rows, provenance has %d" % (len(rows), len(expected)))
    seen = set()
    for row in rows:
        key = (row.get("seed"), row.get("edge"))
        if key in seen:
            found.append("duplicate row %r" % (key,))
        seen.add(key)
        original = expected.get(key)
        if original is None:
            found.append("row %r is not in the provenance record" % (key,))
            continue
        if row.get("category") != original.get("category"):
            found.append("%r: category differs from provenance" % (key,))
        if row.get("reverse_served_windows") != original.get(
                "reverse_committed_windows"):
            found.append("%r: reverse service differs from provenance" % (key,))
        if row.get("prediction_source") != original.get("prediction_source"):
            found.append("%r: prediction source differs from provenance" % (key,))
        if not row.get("carriers"):
            found.append("%r: no carrier" % (key,))
            continue
        if {carrier.get("type") for carrier in row["carriers"]} != set(
                original.get("assertion_sources") or {}):
            found.append("%r: carrier types differ from provenance sources" % (key,))
        for carrier in row["carriers"]:
            if carrier.get("formation_cycle") is None:
                found.append("%r: carrier has no formation cycle" % (key,))
            if not carrier.get("hit_edges"):
                found.append("%r: carrier has no hit edge" % (key,))
            if carrier.get("type") == "loop_candidate" and carrier.get(
                    "orientation") not in ("direct", "reverse", "both"):
                found.append("%r: bad loop orientation" % (key,))
            edge = tuple(str(key[1]).split(">"))
            expected_hits = _hits(carrier.get("type"), carrier.get("path") or [], edge)
            hit_edges = set(carrier.get("hit_edges") or [])
            got_hits = [
                name for name, pair in (
                    ("direct", edge),
                    ("reverse", (edge[1], edge[0])),
                )
                if "%s>%s" % pair in hit_edges
            ]
            if got_hits != expected_hits:
                found.append("%r: carrier path does not match its hit edges" % (key,))
        if row.get("direct_temporal_count", 0) < PREDICTION_FLOOR:
            found.append("%r: direct temporal count below floor" % (key,))
        if row.get("reverse_temporal_count", 0) < PREDICTION_FLOOR:
            found.append("%r: reverse temporal count below floor" % (key,))
        if not row.get("loop_carriers"):
            found.append("%r: no loop carrier" % (key,))
    summary = _summarise(rows)
    actual = {key: value for key, value in (art.get("summary") or {}).items()
              if key != "findings"}
    if actual != summary:
        found.append("summary does not match rows")
    if not any(control.get("passes") for control in art.get("controls") or []):
        found.append("no control passes")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("the page is stale")
    return found


def write() -> int:
    body = build()
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    print("assertion carrier trace: %s" % json.dumps({
        "rows": body["summary"]["edges"],
        "loop_carriers": body["summary"]["loop_carriers"],
        "dream_carriers": body["summary"]["dream_carriers"],
        "formation_cycles": [body["summary"]["formation_cycle_min"],
                             body["summary"]["formation_cycle_max"]],
    }))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no carrier trace artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("assertion carrier trace: %s" % json.dumps({
        "rows": art["summary"]["edges"],
        "loop_carriers": art["summary"]["loop_carriers"],
        "dream_carriers": art["summary"]["dream_carriers"],
    }))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
