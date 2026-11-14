"""A1 baseline availability: observed C1 denominators and C4 non-target rows.

This is a no-arm replay of the six registered worlds.  It applies no A-, K- or
Y- treatment and reads no A1 result.  It records, for every edge in the actual
A1 cell stream, the A, K and Y availability counts from the untreated A+K+
schedule.  Those counts answer the denominator question before freeze:

* C1 A- denominator: baseline K-available edges (the A-K+ cells preserve the
  carrier path);
* C1 K- denominator: baseline A-available edges (the A+K- cells preserve the
  served path);
* C4 non-target rows: the actual cell stream minus the target block.

The audit also records the narrower one-orientation candidate universe used by
target selection and the 63-64 plan.  The two streams are not the same size:
``a1_arms.run_cell`` takes its stream from the full 120-cycle directed world,
while target selection takes one orientation per unordered pair from the first
36 cycles.  Recording both makes the divergence explicit instead of treating
either count as if it were the other.

It does not measure treatment effects.  C4 deltas, C7 formation differences
and C8 assertion rates still require cell parts.

    python -m benchmarks.a1_baseline_availability --write
    python -m benchmarks.a1_baseline_availability --check
    python -m benchmarks.a1_baseline_availability --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import a1_arms
from benchmarks import a1_two_path
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import (
    PHASE_ACQUISITION,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, _world_compositional_edges

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CURRENT_PATH = DOCS / "a1_target_selection.json"
N20_PATH = DOCS / "a1_c8_target_selection.json"
AUDIT_PATH = DOCS / "a1_baseline_availability.json"
PAGE_PATH = DOCS / "A1-BASELINE-AVAILABILITY.md"
ID = "A1-BASELINE-AVAILABILITY-1"
DATE = "2026-11-14"
KIND = "a1_baseline_availability"
CYCLES = a1_two_path.CYCLES
CAP = a1_two_path.CAP
C1_FLOOR = 60
C4_MAX = 0.05
SEEDS = a1_two_path.SEEDS


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _selected(path: Path, seed: int) -> list[str]:
    row = (_load(path).get("per_seed") or {}).get(str(seed)) or {}
    return list(row.get("selected") or [])


def _candidates(seed: int) -> set[str]:
    """The one-orientation candidate universe recorded by target selection."""
    row = (_load(CURRENT_PATH).get("per_seed") or {}).get(str(seed)) or {}
    return set((row.get("u") or {}).keys())


def _targets() -> tuple[dict[int, set[tuple[str, str]]], dict[int, set[tuple[str, str]]]]:
    current = {
        seed: {tuple(edge.split(">", 1)) for edge in _selected(CURRENT_PATH, seed)}
        for seed in SEEDS
    }
    n20 = {
        seed: {tuple(edge.split(">", 1)) for edge in _selected(N20_PATH, seed)}
        for seed in SEEDS
    }
    return current, n20


def _run_seed(seed: int) -> dict:
    """Replay one registered world with no treatment and record all cell edges."""
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    universe = _world_compositional_edges(world)
    counts = {
        edge: {"A": 0, "K": 0, "Y": 0,
               "A_first": None, "K_first": None, "Y_first": None}
        for edge in universe
    }
    db_path = _make_scratch_db("a1_baseline_availability")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = CAP
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=a1_arms.ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                cycle = (i + 1) // EVENTS_PER_CYCLE
                report = service.run_sleep_cycle()
                predictions = {(p.source, p.target) for p in report.predictions}
                carriers = a1_arms._carrier_edges(report)
                asserted = a1_arms._report_edges(report)
                for edge, count in counts.items():
                    if edge in predictions:
                        count["A"] += 1
                        count["A_first"] = count["A_first"] or cycle
                    if edge in carriers:
                        count["K"] += 1
                        count["K_first"] = count["K_first"] or cycle
                    if edge in asserted:
                        count["Y"] += 1
                        count["Y_first"] = count["Y_first"] or cycle
    finally:
        memory.close()
        db_path.unlink(missing_ok=True)

    rows = []
    for edge in sorted(universe):
        count = counts[edge]
        rows.append({
            "edge": "%s>%s" % edge,
            "A": count["A"] > 0,
            "K": count["K"] > 0,
            "Y": count["Y"] > 0,
            "A_cycles": count["A"],
            "K_cycles": count["K"],
            "Y_cycles": count["Y"],
            "A_rate": round(count["A"] / CYCLES, 6),
            "K_rate": round(count["K"] / CYCLES, 6),
            "Y_rate": round(count["Y"] / CYCLES, 6),
            "first_A_cycle": count["A_first"],
            "first_K_cycle": count["K_first"],
            "first_Y_cycle": count["Y_first"],
        })
    return {"seed": seed, "universe": len(universe), "rows": rows}


def _stream(rows: list[dict], current: set[str], n20: set[str]) -> dict:
    """C1/C4 counts for one edge stream, without treatment deltas."""
    a = [row for row in rows if row["A"]]
    k = [row for row in rows if row["K"]]
    y = [row for row in rows if row["Y"]]
    a_minus = len(k)      # A-K+ rows whose control has a carrier
    k_minus = len(a)      # A+K- rows whose control has a served edge
    min_denominator = min(a_minus, k_minus)
    return {
        "rows": len(rows),
        "A_available": len(a),
        "K_available": len(k),
        "Y_available": len(y),
        "c1_a_minus_denominator": a_minus,
        "c1_k_minus_denominator": k_minus,
        "c1_min_denominator": min_denominator,
        "c1_floor": C1_FLOOR,
        "c1_loss_budget": min_denominator - C1_FLOOR,
        "c1_floor_pass": min_denominator >= C1_FLOOR,
        "c1_target_only_n4": {
            "rows": sum(1 for row in rows if row["edge"] in current),
            "A_available": sum(1 for row in rows
                               if row["edge"] in current and row["A"]),
            "K_available": sum(1 for row in rows
                               if row["edge"] in current and row["K"]),
        },
        "c1_target_only_n20": {
            "rows": sum(1 for row in rows if row["edge"] in n20),
            "A_available": sum(1 for row in rows
                               if row["edge"] in n20 and row["A"]),
            "K_available": sum(1 for row in rows
                               if row["edge"] in n20 and row["K"]),
        },
        "c4_non_target_rows_n4": len(rows) - sum(
            1 for row in rows if row["edge"] in current),
        "c4_non_target_rows_n20": len(rows) - sum(
            1 for row in rows if row["edge"] in n20),
        "c4_non_target_with_any_baseline_n4": sum(
            1 for row in rows if row["edge"] not in current
            and (row["A"] or row["K"] or row["Y"])),
        "c4_non_target_with_any_baseline_n20": sum(
            1 for row in rows if row["edge"] not in n20
            and (row["A"] or row["K"] or row["Y"])),
    }


def _summary(seed: int, rows: list[dict],
             current: set[str], n20: set[str], candidates: set[str]) -> dict:
    actual = _stream(rows, current, n20)
    protocol_rows = [row for row in rows if row["edge"] in candidates]
    protocol = _stream(protocol_rows, current, n20)
    protocol["candidate_rows"] = len(candidates)
    protocol["missing_candidate_rows"] = len(candidates) - len(protocol_rows)
    return {
        "seed": seed,
        "candidate_rows": actual["rows"],
        "A_available": actual["A_available"],
        "K_available": actual["K_available"],
        "Y_available": actual["Y_available"],
        "c1_a_minus_denominator": actual["c1_a_minus_denominator"],
        "c1_k_minus_denominator": actual["c1_k_minus_denominator"],
        "c1_min_denominator": actual["c1_min_denominator"],
        "c1_floor": C1_FLOOR,
        "c1_loss_budget": actual["c1_loss_budget"],
        "c1_floor_pass": actual["c1_floor_pass"],
        "c1_target_only_n4": actual["c1_target_only_n4"],
        "c1_target_only_n20": actual["c1_target_only_n20"],
        "c4_non_target_rows_n4": actual["c4_non_target_rows_n4"],
        "c4_non_target_rows_n20": actual["c4_non_target_rows_n20"],
        "c4_non_target_with_any_baseline_n4": actual["c4_non_target_with_any_baseline_n4"],
        "c4_non_target_with_any_baseline_n20": actual["c4_non_target_with_any_baseline_n20"],
        "c4_rows": actual["c4_non_target_rows_n4"],
        "c4_rows_n20": actual["c4_non_target_rows_n20"],
        "c4_measured_deltas": 0,
        "c4_status": "ROWS COUNTED; DELTAS WAITING FOR TREATMENT CELLS",
        "protocol": protocol,
        "rows": rows,
    }


def _totals(per_seed: list[dict]) -> dict:
    def total(key: str) -> int:
        return sum(row[key] for row in per_seed)

    def minimum(key: str) -> int:
        return min((row[key] for row in per_seed), default=0)

    protocol = [row["protocol"] for row in per_seed]
    return {
        "candidate_rows": total("candidate_rows"),
        "c1_a_minus_denominator": total("c1_a_minus_denominator"),
        "c1_k_minus_denominator": total("c1_k_minus_denominator"),
        "c1_min_denominator": minimum("c1_min_denominator"),
        "c1_floor_pass": all(row["c1_floor_pass"] for row in per_seed),
        "c4_non_target_rows_n4": total("c4_non_target_rows_n4"),
        "c4_non_target_rows_n20": total("c4_non_target_rows_n20"),
        "c4_measured_deltas": 0,
        "protocol": {
            "candidate_rows": sum(row["candidate_rows"] for row in protocol),
            "c1_a_minus_denominator": sum(row["c1_a_minus_denominator"] for row in protocol),
            "c1_k_minus_denominator": sum(row["c1_k_minus_denominator"] for row in protocol),
            "c1_min_denominator": min(
                (row["c1_min_denominator"] for row in protocol), default=0),
            "c1_floor_pass": all(row["c1_floor_pass"] for row in protocol),
            "c4_non_target_rows_n4": sum(row["c4_non_target_rows_n4"] for row in protocol),
            "c4_non_target_rows_n20": sum(row["c4_non_target_rows_n20"] for row in protocol),
            "c4_measured_deltas": 0,
        },
    }


def build() -> dict:
    current, n20 = _targets()
    current_edges = {
        seed: {"%s>%s" % edge for edge in current[seed]} for seed in SEEDS
    }
    n20_edges = {
        seed: {"%s>%s" % edge for edge in n20[seed]} for seed in SEEDS
    }
    candidate_sets = {seed: _candidates(seed) for seed in SEEDS}
    per_seed = []
    for seed in SEEDS:
        replay = _run_seed(seed)
        row = _summary(seed, replay["rows"], current_edges[seed], n20_edges[seed],
                       candidate_sets[seed])
        if row["protocol"]["missing_candidate_rows"]:
            row.setdefault("problems", []).append(
                "candidate edges are missing from the cell stream")
        if not current_edges[seed] <= candidate_sets[seed]:
            row.setdefault("problems", []).append(
                "current targets are outside the candidate universe")
        if not n20_edges[seed] <= candidate_sets[seed]:
            row.setdefault("problems", []).append(
                "N20 targets are outside the candidate universe")
        per_seed.append(row)

    totals = _totals(per_seed)
    actual_floor = totals["c1_floor_pass"]
    protocol_floor = totals["protocol"]["c1_floor_pass"]
    divergence = (
        totals["c4_non_target_rows_n4"] != totals["protocol"]["c4_non_target_rows_n4"]
        or any(row["candidate_rows"] != row["protocol"]["candidate_rows"]
               for row in per_seed)
    )
    if not actual_floor and not protocol_floor:
        status = "FLAGGED — C1 FLOOR NOT REACHED IN EITHER STREAM"
    elif not actual_floor:
        status = "FLAGGED — C1 FLOOR NOT REACHED IN THE CELL STREAM"
    elif not protocol_floor:
        status = "FLAGGED — C1 FLOOR NOT REACHED IN THE CANDIDATE STREAM"
    else:
        status = "OBSERVED — C1 FLOOR REACHED"
    if divergence:
        status += "; C4 CELL STREAM IS WIDER THAN THE CANDIDATE PLAN"
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": status,
        "cycles": CYCLES,
        "cap": CAP,
        "c1_floor": C1_FLOOR,
        "c4_max": C4_MAX,
        "seed_block": [row["seed"] for row in per_seed],
        "per_seed": per_seed,
        "totals": totals,
        "stream_divergence": {
            "cell_stream": "full 120-cycle directed-edge world used by a1_arms.run_cell",
            "candidate_stream": "one-orientation candidate universe from target selection",
            "extra_cell_rows": totals["candidate_rows"]
            - totals["protocol"]["candidate_rows"],
            "extra_c4_n4_rows": totals["c4_non_target_rows_n4"]
            - totals["protocol"]["c4_non_target_rows_n4"],
            "extra_c4_n20_rows": totals["c4_non_target_rows_n20"]
            - totals["protocol"]["c4_non_target_rows_n20"],
            "disposition": (
                "DESIGN INCONSISTENCY — the cell stream and the 63-64 candidate "
                "plan are not the same edge set; do not treat one denominator as "
                "the other."
            ),
        },
        "c1_interpretation": (
            "Observed baseline denominators from the untreated A+K+ replay. "
            "The C1 A- denominator is the count of baseline K-available edges; "
            "the K- denominator is the count of baseline A-available edges. The "
            "floor is applied per seed and path by a1_result; any value below 60 "
            "is a VOID risk. The cell-stream and candidate-stream counts are "
            "reported separately because they are not the same edge set."
        ),
        "c4_interpretation": (
            "The C4 non-target rows are counted, not scored. Treatment deltas "
            "still require the A+K+, A+K-, A-K+ and A-K- cell parts."
        ),
        "not_evidence": (
            "A no-arm baseline-availability audit. It runs no A1 cell, freezes "
            "no target, makes no causal, capability or transfer claim, and does "
            "not measure C1, C4, C7 or C8."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("audit kind")
    if doc.get("id") != ID:
        found.append("audit id")
    if doc.get("cycles") != CYCLES or doc.get("cap") != CAP:
        found.append("run object changed")
    if doc.get("c1_floor") != C1_FLOOR:
        found.append("C1 floor changed")
    per_seed = doc.get("per_seed") or []
    if [row.get("seed") for row in per_seed] != list(SEEDS):
        found.append("seed block changed")
    for row in per_seed:
        seed = row.get("seed")
        if row.get("candidate_rows") != len(row.get("rows") or []):
            found.append("seed %s candidate count does not match rows" % seed)
        if row.get("c1_a_minus_denominator") != row.get("K_available"):
            found.append("seed %s C1 A- denominator is not K availability" % seed)
        if row.get("c1_k_minus_denominator") != row.get("A_available"):
            found.append("seed %s C1 K- denominator is not A availability" % seed)
        if row.get("c1_min_denominator") != min(
                row.get("c1_a_minus_denominator", 0),
                row.get("c1_k_minus_denominator", 0)):
            found.append("seed %s minimum denominator is inconsistent" % seed)
        if row.get("c1_floor_pass") != (row.get("c1_min_denominator", 0) >= C1_FLOOR):
            found.append("seed %s floor status is inconsistent" % seed)
        if row.get("c4_rows") != row.get("c4_non_target_rows_n4"):
            found.append("seed %s C4 N4 count is inconsistent" % seed)
        if row.get("c4_rows_n20") != row.get("c4_non_target_rows_n20"):
            found.append("seed %s C4 N20 count is inconsistent" % seed)
        protocol = row.get("protocol") or {}
        if protocol.get("c1_a_minus_denominator") != protocol.get("K_available"):
            found.append("seed %s protocol C1 A- denominator is not K" % seed)
        if protocol.get("c1_k_minus_denominator") != protocol.get("A_available"):
            found.append("seed %s protocol C1 K- denominator is not A" % seed)
        if protocol.get("c1_min_denominator") != min(
                protocol.get("c1_a_minus_denominator", 0),
                protocol.get("c1_k_minus_denominator", 0)):
            found.append("seed %s protocol minimum denominator is inconsistent" % seed)
        if protocol.get("c1_floor_pass") != (
                protocol.get("c1_min_denominator", 0) >= C1_FLOOR):
            found.append("seed %s protocol floor status is inconsistent" % seed)
        if protocol.get("candidate_rows") != len(
                [r for r in row.get("rows") or [] if r.get("edge") in _candidates(seed)]):
            found.append("seed %s protocol candidate count is inconsistent" % seed)
        if protocol.get("c4_non_target_rows_n4") != protocol.get("candidate_rows") - 4:
            found.append("seed %s protocol C4 N4 count is inconsistent" % seed)
        if protocol.get("c4_non_target_rows_n20") != protocol.get("candidate_rows") - 20:
            found.append("seed %s protocol C4 N20 count is inconsistent" % seed)
        for edge in row.get("rows") or []:
            if edge.get("A") != (edge.get("A_cycles", 0) > 0):
                found.append("seed %s edge %s A flag is inconsistent"
                             % (seed, edge.get("edge")))
            if edge.get("K") != (edge.get("K_cycles", 0) > 0):
                found.append("seed %s edge %s K flag is inconsistent"
                             % (seed, edge.get("edge")))
            if edge.get("Y") != (edge.get("Y_cycles", 0) > 0):
                found.append("seed %s edge %s Y flag is inconsistent"
                             % (seed, edge.get("edge")))
    totals = doc.get("totals") or {}
    if totals.get("c1_min_denominator") != min(
            (row.get("c1_min_denominator", 0) for row in per_seed), default=0):
        found.append("total minimum denominator is inconsistent")
    if totals.get("c1_floor_pass") != all(row.get("c1_floor_pass") for row in per_seed):
        found.append("total floor status is inconsistent")
    protocol_totals = totals.get("protocol") or {}
    if protocol_totals.get("c1_min_denominator") != min(
            (row.get("protocol", {}).get("c1_min_denominator", 0)
             for row in per_seed), default=0):
        found.append("total protocol minimum denominator is inconsistent")
    if protocol_totals.get("c1_floor_pass") != all(
            row.get("protocol", {}).get("c1_floor_pass") for row in per_seed):
        found.append("total protocol floor status is inconsistent")
    divergence = doc.get("stream_divergence") or {}
    if divergence.get("extra_cell_rows") != (
            totals.get("candidate_rows", 0)
            - protocol_totals.get("candidate_rows", 0)):
        found.append("stream divergence row count is inconsistent")
    return found


def _summary_fixture() -> dict:
    rows = [
        {"edge": "a>b", "A": True, "K": True, "Y": True},
        {"edge": "c>d", "A": True, "K": False, "Y": False},
        {"edge": "e>f", "A": False, "K": True, "Y": False},
    ]
    return _summary(1, rows, {"a>b"}, {"a>b", "c>d"}, {"a>b", "c>d"})


def self_test() -> list[str]:
    found: list[str] = []
    row = _summary_fixture()
    if row["c1_a_minus_denominator"] != 2:
        found.append("C1 A- denominator does not count K availability")
    if row["c1_k_minus_denominator"] != 2:
        found.append("C1 K- denominator does not count A availability")
    if row["c4_non_target_rows_n4"] != 2:
        found.append("C4 N4 count does not remove the target block")
    if row["c4_non_target_rows_n20"] != 1:
        found.append("C4 N20 count does not remove the target block")
    if row["protocol"]["candidate_rows"] != 2:
        found.append("protocol candidate count is not the narrow stream")
    if row["protocol"]["c4_non_target_rows_n4"] != 1:
        found.append("protocol C4 N4 count is not narrowed to candidates")
    if row["c1_floor_pass"]:
        found.append("the small fixture incorrectly clears the C1 floor")
    return found


def _table(per_seed: list[dict], rows_key: str | None, totals: dict) -> list[str]:
    lines = [
        "| Seed | Rows | Baseline A | Baseline K | C1 A− denom | C1 K− denom | Min | Floor | C4 non-target N4 | C4 non-target N20 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in per_seed:
        source = row if rows_key is None else row[rows_key]
        lines.append(
            "| `%d` | %d | %d | %d | %d | %d | %d | %s | %d | %d |" % (
                row["seed"], source["candidate_rows"], source["A_available"],
                source["K_available"], source["c1_a_minus_denominator"],
                source["c1_k_minus_denominator"], source["c1_min_denominator"],
                "PASS" if source["c1_floor_pass"] else "FAIL",
                source["c4_non_target_rows_n4"], source["c4_non_target_rows_n20"],
            )
        )
    lines += [
        "",
        "| Total rows | Total C1 A− rows | Total C1 K− rows | Overall minimum | Floor reached? | C4 N4 | C4 N20 |",
        "| ---: | ---: | ---: | ---: | --- | ---: | ---: |",
        "| %d | %d | %d | %d | **%s** | %d | %d |" % (
            totals["candidate_rows"], totals["c1_a_minus_denominator"],
            totals["c1_k_minus_denominator"], totals["c1_min_denominator"],
            "YES" if totals["c1_floor_pass"] else "NO",
            totals["c4_non_target_rows_n4"], totals["c4_non_target_rows_n20"],
        ),
    ]
    return lines


def render(doc: dict) -> str:
    totals = doc["totals"]
    protocol = totals["protocol"]
    lines = [
        "# A1 baseline availability — observed C1/C4 denominators",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** It is a no-arm A+K+ replay; no A-, K- or Y- treatment was applied and no target was changed.",
        "",
        "## Definition",
        "",
        "C1's A− denominator is the count of edges that have a carrier in the baseline; C1's K− denominator is the count of edges that are served in the baseline. C4's non-target rows are the stream minus the target block. Treatment deltas and gate verdicts still require cells.",
        "",
        "## Cell stream",
        "",
        "This is the full 120-cycle directed-edge stream that `a1_arms.run_cell` currently uses for `rows + neighbor_rows`.",
        "",
    ]
    lines += _table(doc["per_seed"], None, totals)
    lines += [
        "",
        "## Candidate-protocol stream",
        "",
        "This is the narrower one-orientation, first-36-cycle candidate universe used by target selection and the 63–64 plan.",
        "",
    ]
    lines += _table(doc["per_seed"], "protocol", protocol)
    divergence = doc["stream_divergence"]
    lines += [
        "",
        "## Stream divergence",
        "",
        "| Extra cell-stream rows | Extra C4 N4 rows | Extra C4 N20 rows | Disposition |",
        "| ---: | ---: | ---: | --- |",
        "| %d | %d | %d | **%s** |" % (
            divergence["extra_cell_rows"], divergence["extra_c4_n4_rows"],
            divergence["extra_c4_n20_rows"], divergence["disposition"],
        ),
        "",
        "The cell stream is wider than the candidate universe. Its C4 non-target counts are therefore not the 59–60 and 43–44 candidate-plan counts, and its C1 denominator can exceed the 63–64 candidate upper bound. That is a design inconsistency, not a larger sample: the extra edges were not candidate targets and are not licensed by the 63–64 plan.",
        "",
        "## Target-only context",
        "",
        "| Seed | N4 target rows | N4 baseline A/K available | N20 target rows | N20 baseline A/K available |",
        "| ---: | ---: | --- | ---: | --- |",
    ]
    for row in doc["per_seed"]:
        n4 = row["c1_target_only_n4"]
        n20 = row["c1_target_only_n20"]
        lines.append(
            "| `%d` | %d | %d / %d | %d | %d / %d |" % (
                row["seed"], n4["rows"], n4["A_available"], n4["K_available"],
                n20["rows"], n20["A_available"], n20["K_available"],
            )
        )
    lines += [
        "",
        "The target-only rows are below the 60-row C1 floor by construction; they are shown to keep the target and expanded denominators separate.",
        "",
        "## Limits",
        "",
        "C4 treatment deltas are **not** measured: `c4_measured_deltas` is 0 and C4 remains waiting for A+K+, A+K−, A−K+ and A−K− parts. C7 and C8 also remain unrun. A baseline count does not turn any gate into a verdict. This audit does not change the runner or the target set; it records the denominator that the current implementation and the candidate protocol would supply.",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_baseline_availability --check",
        "python -m benchmarks.a1_baseline_availability --self-test",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def write() -> int:
    doc = build()
    AUDIT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("wrote %s and %s" % (AUDIT_PATH, PAGE_PATH))
    return 0


def check() -> int:
    if not AUDIT_PATH.exists():
        print("FAIL: %s is missing" % AUDIT_PATH)
        return 1
    doc = _load(AUDIT_PATH)
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 baseline availability: clean; cell C1 min %d, cell C4 N4 %d; "
          "candidate C1 min %d, candidate C4 N4 %d"
          % (doc["totals"]["c1_min_denominator"],
             doc["totals"]["c4_non_target_rows_n4"],
             doc["totals"]["protocol"]["c1_min_denominator"],
             doc["totals"]["protocol"]["c4_non_target_rows_n4"]))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        found = self_test()
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("A1 baseline availability: self-test clean")
        return 0
    if args.write:
        return write()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
