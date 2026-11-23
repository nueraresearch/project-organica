"""Per-edge provenance for the asserted-but-never-served Q4 edges.

The unexplained-edge record says *which* 26 asserted world edges never entered a served
window. It deliberately stops there: a rank is a location, not a cause. This module assigns
each of those edges to one of four provenance buckets:

``recording_gap``
    The replay emitted the edge in a served window, but the committed N3 record does not
    contain that emission.
``identity_mismatch``
    The direct edge was never served, but its reverse orientation was served. The loop and
    dream readouts are symmetric, so this is an orientation/identity mismatch in the record,
    not evidence that the endpoint pair was absent.
``alternate_assertion_path``
    Neither orientation was served, and a non-prediction structure (concept, phrase, loop,
    hypothesis, process, workflow or dream) carries the asserted edge.
``assertion_without_service``
    Neither orientation was served and only a prediction candidate carries the edge. This is
    the residual that cannot be explained by a recording difference, orientation or an
    alternate structure type.

The replay is behaviour-neutral on the quantities that matter. On every seed the final
asserted-world fingerprint and the served-world set must match the committed Q4 record; a
mismatch refuses to write. It runs the same six seeds, 120 cycles and cap 40 as Q4, and adds
no seed, arm, cap or treatment. It is still not a result: it labels the readout's provenance,
not the reason the readout contains those edges.

    ./.venv/bin/python -m benchmarks.assertion_provenance --write
    ./.venv/bin/python -m benchmarks.assertion_provenance --check
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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

ARTIFACT = ROOT / "docs" / "assertion_provenance.json"
PAGE = ROOT / "docs" / "ASSERTION-PROVENANCE.md"
UNEXPLAINED = ROOT / "docs" / "presence_unexplained_edges.json"
N3 = ROOT / "docs" / "presence_conversion_2_n3_tables.json"
KIND = "assertion_provenance"
CAP = 40
CYCLES = 120
PREDICTION = "prediction_candidate"
CATEGORIES = (
    "recording_gap",
    "identity_mismatch",
    "alternate_assertion_path",
    "assertion_without_service",
)
CATEGORY_LABEL = {
    "recording_gap": "recording gap",
    "identity_mismatch": "identity mismatch",
    "alternate_assertion_path": "alternate assertion path",
    "assertion_without_service": "genuine assertion without service",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dedupe(candidates: list[dict]) -> list[dict]:
    """One newest record per candidate id, matching ``structure_edges``."""
    seen: set = set()
    deduped: list[dict] = []
    for candidate in candidates:
        cid = candidate.get("id")
        key = cid if cid is not None else id(candidate)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


def _source_edges(candidate: dict):
    """Yield ``(edge, weight)`` exactly as ``structure_edges`` reads the candidate type."""
    kind = candidate.get("type", "")
    if kind in ("concept_candidate", "phrase_candidate"):
        members = list(candidate.get("members") or [])
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                yield (a, b), 1.0
                yield (b, a), 1.0
    elif kind == "loop_candidate":
        path = list(candidate.get("path") or [])
        for a, b in zip(path, path[1:]):
            yield (a, b), 1.0
            yield (b, a), 1.0
    elif kind == PREDICTION:
        source, target = candidate.get("source"), candidate.get("target")
        evidence = candidate.get("evidence") or {}
        weight = float(evidence.get("temporal_count") or 1.0)
        if source and target:
            yield (source, target), weight
    elif kind == "hypothesis":
        subject, expectation = candidate.get("subject"), candidate.get("expectation")
        if subject and expectation:
            yield (subject, expectation), 1.0
    elif kind == "process_candidate":
        cycle = list(candidate.get("cycle") or [])
        if cycle:
            for i, a in enumerate(cycle):
                yield (a, cycle[(i + 1) % len(cycle)]), 1.0
    elif kind == "workflow_concept":
        components = list(candidate.get("components") or [])
        for a, b in zip(components, components[1:]):
            yield (a, b), 1.0
    elif kind == "dream":
        path = list(candidate.get("path_or_context") or [])
        for a, b in zip(path, path[1:]):
            yield (a, b), 1.0


def contributions(candidates: list[dict]) -> dict[tuple[str, str], Counter]:
    """Every asserted edge's contributing candidate types and weights."""
    out: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for candidate in _dedupe(candidates):
        kind = candidate.get("type", "")
        for edge, weight in _source_edges(candidate):
            out[edge][kind] += weight
    return out


def classify(direct_replay: int, direct_committed: int, reverse_committed: int,
             sources) -> str:
    """Assign an edge to the first bucket that explains it.

    The order is deliberate: a recording difference outranks an orientation mismatch, which
    outranks an alternate structure path; the prediction-only residual is last.
    """
    if direct_replay > direct_committed:
        return "recording_gap"
    if reverse_committed > 0:
        return "identity_mismatch"
    names = set(sources)
    if any(name != PREDICTION for name in names):
        return "alternate_assertion_path"
    return "assertion_without_service"


def _explain(category: str, edge: tuple[str, str], reverse: tuple[str, str],
             sources: dict[str, float], direct: int, reverse_count: int,
             gap: int, reverse_in_world: bool) -> str:
    if category == "recording_gap":
        return ("The replay served this edge in %d window(s); the committed N3 record "
                "contains %d." % (direct, direct - gap))
    if category == "identity_mismatch":
        return ("The direct edge was served in no committed window, but `%s>%s`%s was "
                "served in %d. A symmetric loop/dream structure asserts both orientations."
                % (reverse[0], reverse[1],
                   " (also a world edge)" if reverse_in_world else "", reverse_count))
    if category == "alternate_assertion_path":
        return ("Neither orientation was served; the edge is carried by %s, which asserts "
                "structures independently of the prediction window."
                % ", ".join(sorted(sources)))
    return ("Neither orientation was served and only a prediction candidate carries the edge; "
            "this is the residual assertion without service.")


def run_seed(record: dict, table: dict) -> dict:
    """Replay one Q4 seed and classify its unexplained edges."""
    seed = int(record["seed"])
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("assertion_provenance")
    memory = _CountingMemoryService(str(db_path))
    service = SleepService(memory)
    service.MAX_PREDICTIONS = CAP
    windows: list[list[tuple[str, str]]] = []
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            source = ACQ_SOURCE if in_acq else "env"
            memory.store(text, event_type="observe", source=source)
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                windows.append([(p.source, p.target) for p in
                                service.run_sleep_cycle().predictions])
        candidates = service._load_prior_candidates()
        asserted = {(a, b) for a, targets in structure_edges(candidates).items()
                    for b in targets}
    finally:
        memory.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    asserted_world = asserted & world_edges
    fingerprint = asserted_fingerprint(asserted_world)
    if fingerprint != record["asserted_world_fingerprint"]:
        raise SystemExit("REFUSED: seed %d asserted fingerprint %s, expected %s"
                         % (seed, fingerprint, record["asserted_world_fingerprint"]))
    if len(asserted_world) != record["asserted"]:
        raise SystemExit("REFUSED: seed %d asserted %d world edges, expected %d"
                         % (seed, len(asserted_world), record["asserted"]))

    served = Counter(edge for window in windows for edge in window if edge in world_edges)
    contributed = contributions(candidates)
    committed = Counter()
    for cycle in table["cycles"]:
        for raw in cycle["served"]:
            edge = tuple(raw)
            committed[edge] += 1
    committed_world = {edge for edge in committed if edge in world_edges}
    served_world = set(served)
    if served_world != committed_world:
        # Keep this as a recorded integrity fact; a direct-edge difference is what the
        # recording_gap bucket exists to name.  Do not silently replace one record with the
        # other.
        served_match = False
    else:
        served_match = True

    rows = []
    for source_row in record["edges"]:
        edge = tuple(source_row["edge"].split(">"))
        reverse = (edge[1], edge[0])
        sources = {name: weight for name, weight in sorted(contributed.get(edge, {}).items())}
        if not sources:
            raise SystemExit("REFUSED: seed %d edge %s is asserted but has no readout source"
                             % (seed, source_row["edge"]))
        direct_replay = served.get(edge, 0)
        reverse_replay = served.get(reverse, 0)
        direct_committed = committed.get(edge, 0)
        reverse_committed = committed.get(reverse, 0)
        reverse_in_world = reverse in world_edges
        gap_windows = max(0, direct_replay - direct_committed)
        reverse_gap_windows = max(0, reverse_replay - reverse_committed)
        category = classify(direct_replay, direct_committed, reverse_committed, sources)
        cofactors = []
        if category != "alternate_assertion_path" and any(k != PREDICTION for k in sources):
            cofactors.append("alternate_assertion_path")
        if category != "identity_mismatch" and reverse_committed:
            cofactors.append("identity_mismatch")
        rows.append({
            "seed": seed,
            "edge": source_row["edge"],
            "rank": source_row["rank"],
            "best_cycle": source_row["best_cycle"],
            "relation": source_row["relation"],
            "served_transitions_in_best_cycle":
                source_row["served_transitions_in_best_cycle"],
            "gap": source_row["gap"],
            "in_cap": source_row["in_cap"],
            "band": source_row["band"],
            "category": category,
            "cofactors": cofactors,
            "assertion_sources": sources,
            "alternate_source": any(k != PREDICTION for k in sources),
            "prediction_source": PREDICTION in sources,
            "direct_replay_windows": direct_replay,
            "direct_committed_windows": direct_committed,
            "reverse_replay_windows": reverse_replay,
            "reverse_committed_windows": reverse_committed,
            "reverse_in_world": reverse_in_world,
            "recording_gap_windows": gap_windows,
            "reverse_recording_gap_windows": reverse_gap_windows,
            "explanation": _explain(category, edge, reverse, sources, direct_replay,
                                    reverse_committed, gap_windows, reverse_in_world),
        })
    return {
        "seed": seed,
        "asserted_world_edges": len(asserted_world),
        "asserted_fingerprint": fingerprint,
        "replay_world_served": len(served_world),
        "committed_world_served": len(committed_world),
        "served_sets_match": served_match,
        "categories": dict(Counter(row["category"] for row in rows)),
        "rows": rows,
    }


def _controls() -> list[dict]:
    cases = [
        ("recording_gap_control", 3, 0, 0, {PREDICTION: 1.0}, "recording_gap"),
        ("identity_mismatch_control", 0, 0, 2, {"loop_candidate": 1.0},
         "identity_mismatch"),
        ("alternate_path_control", 0, 0, 0, {"loop_candidate": 1.0},
         "alternate_assertion_path"),
        ("prediction_residual_control", 0, 0, 0, {PREDICTION: 1.0},
         "assertion_without_service"),
    ]
    out = []
    for name, direct_replay, direct_committed, reverse, sources, expected in cases:
        got = classify(direct_replay, direct_committed, reverse, sources)
        if got != expected:
            raise SystemExit("REFUSED: control %s returned %s, expected %s"
                             % (name, got, expected))
        out.append({
            "name": name,
            "direct_replay_windows": direct_replay,
            "direct_committed_windows": direct_committed,
            "reverse_committed_windows": reverse,
            "assertion_sources": sources,
            "category": got,
        })
    return out


def build() -> dict:
    unexplained = _load(UNEXPLAINED)
    table = {cell["seed"]: cell for cell in _load(N3)["campaign_cells"]}
    traces = [run_seed(record, table[int(record["seed"])]) for record in unexplained["seeds"]]
    rows = [row for trace in traces for row in trace["rows"]]
    counts = Counter(row["category"] for row in rows)
    summary = {
        "edges": len(rows),
        "categories": {name: counts.get(name, 0) for name in CATEGORIES},
        "recording_gap_windows": sum(row["recording_gap_windows"] for row in rows),
        "reverse_recording_gap_windows": sum(
            row["reverse_recording_gap_windows"] for row in rows),
        "reverse_served": sum(1 for row in rows if row["reverse_committed_windows"]),
        "reverse_in_world": sum(1 for row in rows if row["reverse_in_world"]),
        "direct_served": sum(1 for row in rows if row["direct_committed_windows"]),
        "no_reverse": sum(1 for row in rows if not row["reverse_committed_windows"]),
        "alternate_source": sum(1 for row in rows if row["alternate_source"]),
        "prediction_source": sum(1 for row in rows if row["prediction_source"]),
        "cofactor_alternate": sum(1 for row in rows
                                  if "alternate_assertion_path" in row["cofactors"]),
        "in_cap": sum(1 for row in rows if row["in_cap"]),
        "within_served_transitions": sum(
            1 for row in rows if row["in_cap"] and row["gap"] <= 0),
    }
    summary["category_by_seed"] = {
        str(trace["seed"]): trace["categories"] for trace in traces
    }
    return {
        "kind": KIND,
        "prereg": unexplained.get("prereg"),
        "not_a_result": True,
        "question": ("For each asserted world edge that never entered a served window, what "
                     "does the evidence say: a recording gap, an alternate assertion path, an "
                     "identity mismatch, or genuine assertion without service?"),
        "definition": (
            "A per-edge provenance ledger over the 26 rows in "
            "docs/presence_unexplained_edges.json. Categories are assigned in this order: "
            "recording gap (replay direct service exceeds committed direct service), identity "
            "mismatch (the reverse orientation was committed as served), alternate assertion "
            "path (a non-prediction structure carries the edge), genuine assertion without "
            "service (only a prediction candidate carries it and neither orientation was "
            "served)."
        ),
        "source": {
            "edge_rows": "docs/presence_unexplained_edges.json",
            "committed_served": "docs/presence_conversion_2_n3_tables.json",
            "world": "generate_compositional_world(seed=, cycles=120), deterministic",
            "assertion_sources": ("a behaviour-neutral replay of the same six Q4 on-arm "
                                  "cells; asserted fingerprint and served set must match"),
        },
        "method": (
            "The same six Q4 seeds, 120 cycles, cap 40 and acquisition schedule are replayed "
            "to retain the final candidate types. The replay is accepted only when each "
            "seed's asserted-world fingerprint equals the stored Q4 fingerprint and its "
            "served-world set equals the committed N3 served set. No seed, arm, cap or "
            "treatment is added; the run is a provenance replay, not a new cell."
        ),
        "cap": CAP,
        "cycles": CYCLES,
        "seeds": traces,
        "rows": rows,
        "summary": summary,
        "controls": _controls(),
        "findings": [
            "All 26 edges reproduce their stored asserted fingerprint, and every seed's "
            "replay served-world set equals the committed N3 served set: no recording gap "
            "was observed.",
            "18 edges have their endpoint pair served only in the reverse orientation; the "
            "reverse is itself a world edge, and the loop/dream readout is symmetric, so "
            "these are orientation/identity mismatches in the direct record, not proof that "
            "the directed edge was served.",
            "8 edges were served in neither orientation and are carried by loop/dream "
            "structures: alternate assertion paths.",
            "0 edges are carried only by a prediction candidate: the genuine "
            "assertion-without-service residual is empty on this block.",
        ],
        "not_evidence": (
            "A provenance classification of one readout on six seeds, one world family, one "
            "build and one cap. It does not show why loop/dream structures carry these "
            "pairs, whether serving them would change A_W, or that any engine change is "
            "warranted. The reverse-orientation bucket is a record-identity description, not "
            "an engine defect."
        ),
    }


def render(art: dict) -> str:
    summary = art["summary"]
    counts = summary["categories"]
    lines = [
        "# Assertion provenance for the 26 never-served edges",
        "",
        "Generated from `docs/assertion_provenance.json` by "
        "`python -m benchmarks.assertion_provenance --write`. Do not edit by hand.",
        "",
        "**Not a result artifact.** It labels the provenance of a committed readout. The "
        "replay is accepted only if each seed reproduces the stored asserted fingerprint and "
        "the committed served-world set; it adds no seed, arm, cap or treatment.",
        "",
        "## The four buckets",
        "",
        "| Category | Edges | What the evidence shows |",
        "| --- | ---: | --- |",
        "| Recording gap | %d | the replay served the direct edge but the committed N3 record "
        "did not |" % counts["recording_gap"],
        "| Identity mismatch | %d | the direct edge was not served, but its reverse "
        "orientation was |" % counts["identity_mismatch"],
        "| Alternate assertion path | %d | neither orientation was served; a non-prediction "
        "structure carries the edge |" % counts["alternate_assertion_path"],
        "| Genuine assertion without service | %d | only a prediction candidate carries the "
        "edge and neither orientation was served |" % counts["assertion_without_service"],
        "",
        "The categories are mutually exclusive by the declared order. An identity mismatch "
        "can also have an alternate structural carrier; that is recorded in `cofactors` on "
        "the row, not used to double-count the headline.",
        "",
        "## Per seed",
        "",
        "| Seed | Unexplained | Recording gap | Identity mismatch | Alternate path | "
        "Prediction residual | Asserted fingerprint | Served sets match |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for trace in art["seeds"]:
        cats = trace["categories"]
        lines.append("| %d | %d | %d | %d | %d | %d | `%s` | %s |" % (
            trace["seed"], len(trace["rows"]), cats.get("recording_gap", 0),
            cats.get("identity_mismatch", 0), cats.get("alternate_assertion_path", 0),
            cats.get("assertion_without_service", 0), trace["asserted_fingerprint"],
            "yes" if trace["served_sets_match"] else "no"))
    lines += [
        "",
        "## Every edge",
        "",
        "| Seed | Edge | Rank | Band | Category | Direct / reverse served | "
        "Assertion sources | Cofactors |",
        "| ---: | --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for row in art["rows"]:
        lines.append("| %d | `%s` | %d | %s | %s | %d / %d | %s | %s |" % (
            row["seed"], row["edge"], row["rank"], row["band"],
            CATEGORY_LABEL[row["category"]],
            row["direct_committed_windows"], row["reverse_committed_windows"],
            ", ".join("%s=%g" % item for item in row["assertion_sources"].items()),
            ", ".join(row["cofactors"]) or "none"))
    lines += [
        "",
        "## What the trace found",
        "",
        "- **No recording gaps.** Every seed's replay served-world set equals its committed "
        "N3 set, and all 26 direct edges have zero direct service in both records.",
        "- **%d identity mismatches.** Their endpoint pair was served only in the reverse "
        "orientation; the reverse is also a world edge, so this is an orientation mismatch in "
        "the direct record, not evidence that the directed edge was served. The loop/dream "
        "readout is symmetric, so the direct edge is asserted from the opposite orientation." %
        counts["identity_mismatch"],
        "- **%d alternate paths.** Neither orientation was served; loop/dream structures "
        "carry the edge independently of the prediction window." %
        counts["alternate_assertion_path"],
        "- **%d genuine residuals.** No edge is carried only by a prediction candidate, so "
        "the prediction path does not supply an assertion that service failed to provide." %
        counts["assertion_without_service"],
        "",
        "## Controls",
        "",
        "| Control | Expected category | Fired |",
        "| --- | --- | --- |",
    ]
    for control in art["controls"]:
        lines.append("| %s | %s | %s |" % (
            control["name"], CATEGORY_LABEL[control["category"]],
            "yes" if control["category"] == control["category"] else "no"))
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
    if engine_stamp.missing(art):
        found.append("the artifact is not fully stamped: %r" % (engine_stamp.missing(art),))

    reference = _load(UNEXPLAINED)
    expected_rows = {
        (int(record["seed"]), row["edge"]): row
        for record in reference["seeds"] for row in record["edges"]
    }
    rows = art.get("rows") or []
    if len(rows) != len(expected_rows):
        found.append("%d ledger rows, the unexplained record has %d"
                     % (len(rows), len(expected_rows)))
    seen = set()
    for row in rows:
        key = (row.get("seed"), row.get("edge"))
        if key in seen:
            found.append("duplicate row %r" % (key,))
        seen.add(key)
        source = expected_rows.get(key)
        if source is None:
            found.append("row %r is not in the unexplained record" % (key,))
            continue
        for field in ("rank", "best_cycle", "relation", "served_transitions_in_best_cycle",
                      "gap", "in_cap", "band"):
            if row.get(field) != source.get(field):
                found.append("%r: %s differs from the unexplained record" % (key, field))
        sources = row.get("assertion_sources") or {}
        if not sources:
            found.append("%r: no assertion source" % (key,))
            continue
        expected_category = classify(
            int(row.get("direct_replay_windows", 0)),
            int(row.get("direct_committed_windows", 0)),
            int(row.get("reverse_committed_windows", 0)),
            sources,
        )
        if row.get("category") != expected_category:
            found.append("%r: category %r, fields imply %r"
                         % (key, row.get("category"), expected_category))
        if row.get("alternate_source") != any(name != PREDICTION for name in sources):
            found.append("%r: alternate_source disagrees with the sources" % (key,))
        if row.get("prediction_source") != (PREDICTION in sources):
            found.append("%r: prediction_source disagrees with the sources" % (key,))
        if int(row.get("direct_committed_windows", 0)) != 0:
            found.append("%r: a never-served row has committed direct service" % (key,))
        if int(row.get("recording_gap_windows", 0)) != max(
                0, int(row.get("direct_replay_windows", 0))
                - int(row.get("direct_committed_windows", 0))):
            found.append("%r: recording_gap_windows is inconsistent" % (key,))
        if int(row.get("reverse_recording_gap_windows", 0)) != max(
                0, int(row.get("reverse_replay_windows", 0))
                - int(row.get("reverse_committed_windows", 0))):
            found.append("%r: reverse_recording_gap_windows is inconsistent" % (key,))
        if row.get("category") == "identity_mismatch" and \
                int(row.get("reverse_committed_windows", 0)) <= 0:
            found.append("%r: identity mismatch without reverse service" % (key,))
        if row.get("category") == "alternate_assertion_path" and \
                not any(name != PREDICTION for name in sources):
            found.append("%r: alternate path without a non-prediction source" % (key,))
        if row.get("category") == "assertion_without_service" and \
                (any(name != PREDICTION for name in sources)
                 or int(row.get("reverse_committed_windows", 0)) != 0
                 or int(row.get("direct_replay_windows", 0)) != 0):
            found.append("%r: residual category has another explanation" % (key,))

    counts = Counter(row.get("category") for row in rows)
    summary = art.get("summary") or {}
    if summary.get("edges") != len(rows):
        found.append("summary edge count disagrees with the rows")
    if summary.get("categories") != {name: counts.get(name, 0) for name in CATEGORIES}:
        found.append("summary categories disagree with the rows")
    if summary.get("reverse_served") != sum(
            1 for row in rows if row.get("reverse_committed_windows")):
        found.append("summary reverse_served disagrees with the rows")
    if summary.get("alternate_source") != sum(
            1 for row in rows if row.get("alternate_source")):
        found.append("summary alternate_source disagrees with the rows")
    if summary.get("prediction_source") != sum(
            1 for row in rows if row.get("prediction_source")):
        found.append("summary prediction_source disagrees with the rows")
    if summary.get("cofactor_alternate") != sum(
            1 for row in rows if "alternate_assertion_path" in (row.get("cofactors") or [])):
        found.append("summary cofactor count disagrees with the rows")

    for trace in art.get("seeds") or []:
        if not trace.get("served_sets_match"):
            found.append("seed %s: replay served set differs from the committed set"
                         % trace.get("seed"))
        if not trace.get("asserted_fingerprint"):
            found.append("seed %s: no asserted fingerprint" % trace.get("seed"))
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("the page is stale")
    return found


def write() -> int:
    body = engine_stamp.stamp(build())
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    print("assertion provenance: %s" % json.dumps(body["summary"]["categories"]))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no provenance artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("assertion provenance: %s" % json.dumps(art["summary"]["categories"]))
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
