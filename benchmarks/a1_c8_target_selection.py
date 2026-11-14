"""A1 C8 expansion target selection: 20 A-K- rows per seed.

This is a *separate registered design*, not a change to the current four-target
Path A set.  It reuses the same pre-36 acquisition selection and eligibility
rule, but selects 20 target edges per seed so C8's per-seed assertion rate has
a 1/20 = 0.05 step.  Twenty disjoint edges cannot fit on 16 tags, so the design
allows endpoint overlap while capping each tag's selected degree at three.

    python -m benchmarks.a1_c8_target_selection --write
    python -m benchmarks.a1_c8_target_selection --check
    python -m benchmarks.a1_c8_target_selection --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks.a1_target_selection import (
    CYCLES,
    SEEDS,
    U_CYCLE,
    _hash,
    run_seed,
    select_edges,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_c8_target_selection.json"
PAGE_PATH = DOCS / "A1-C8-TARGET-SELECTION.md"
ID = "A1-C8-EXPANSION-1"
DATE = "2026-11-14"
N_PER_SEED = 20
MAX_ENDPOINT_DEGREE = 3
KIND = "a1_c8_target_selection"


def _endpoint_degrees(selected: list[str]) -> dict[str, int]:
    degree: dict[str, int] = {}
    for value in selected:
        a, b = value.split(">", 1)
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1
    return dict(sorted(degree.items()))


def _seed_row(seed: int) -> dict:
    row = run_seed(seed, n=N_PER_SEED, disjoint=False,
                   max_endpoint_degree=MAX_ENDPOINT_DEGREE)
    selected = list(row["selected"])
    payload = {
        "seed": seed,
        "status": row["status"],
        "candidate_count": row["candidate_count"],
        "eligible_count": row["eligible_count"],
        "n_per_seed": N_PER_SEED,
        "disjoint": False,
        "max_endpoint_degree": MAX_ENDPOINT_DEGREE,
        "selected": selected,
        "endpoint_degree": _endpoint_degrees(selected),
        "u": {edge: row["u"].get(edge) for edge in selected},
        "cycle_member": {edge: row["cycle_member"].get(edge) for edge in selected},
    }
    payload["selection_digest"] = _hash(json.dumps({
        "seed": seed,
        "selected": selected,
        "n_per_seed": N_PER_SEED,
        "max_endpoint_degree": MAX_ENDPOINT_DEGREE,
    }, sort_keys=True))[:16]
    return payload


def build() -> dict:
    per_seed = {str(seed): _seed_row(seed) for seed in SEEDS}
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": "TARGET SETS FORMED — REGISTERED, NOT FROZEN, NOT A RESULT",
        "protocol": "docs/A1-C8-EXPANSION.md",
        "parent_protocol": "docs/A1-TARGET-SELECTION-PROTOCOL.md",
        "design_record": "docs/A1-C8-EXPANSION.md",
        "engine": "0.15.0",
        "cycles": CYCLES,
        "u_cycle": U_CYCLE,
        "n_per_seed": N_PER_SEED,
        "disjoint": False,
        "max_endpoint_degree": MAX_ENDPOINT_DEGREE,
        "threshold": 0.05,
        "threshold_changed": False,
        "selection_rule": (
            "Same 36-cycle pre-treatment universe, same positive-strength and "
            "cycle-member eligibility, same hash order as the four-target "
            "protocol; take the first 20 eligible edges while no tag degree "
            "exceeds 3.  Endpoint overlap is permitted; target rows are not "
            "independent, and no target edge is repeated."
        ),
        "per_seed": per_seed,
        "not_evidence": (
            "A no-arm, 36-cycle target-selection pass for a registered design. "
            "It freezes no manifest, reserves no seed, authorises no cell and "
            "records no C8 measurement."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("C8 expansion kind")
    if doc.get("id") != ID:
        found.append("C8 expansion id")
    if doc.get("n_per_seed") != N_PER_SEED:
        found.append("C8 expansion n_per_seed")
    if doc.get("threshold") != 0.05 or doc.get("threshold_changed") is not False:
        found.append("C8 expansion changed the 0.05 ceiling")
    if doc.get("disjoint") is not False:
        found.append("C8 expansion must record permitted endpoint overlap")
    if doc.get("max_endpoint_degree") != MAX_ENDPOINT_DEGREE:
        found.append("C8 expansion endpoint-degree cap")
    if doc.get("cycles") != CYCLES or doc.get("u_cycle") != U_CYCLE:
        found.append("C8 expansion cycle boundary")
    per_seed = doc.get("per_seed") or {}
    if set(per_seed) != {str(seed) for seed in SEEDS}:
        found.append("C8 expansion seed block")
    for seed, row in per_seed.items():
        selected = row.get("selected") or []
        if row.get("status") != "TARGET SET FORMED":
            found.append("seed %s did not form a C8 expansion set" % seed)
        if len(selected) != N_PER_SEED:
            found.append("seed %s has %d A-K- target rows, not %d"
                         % (seed, len(selected), N_PER_SEED))
            continue
        if len(set(selected)) != N_PER_SEED:
            found.append("seed %s repeats a target edge" % seed)
        degree = _endpoint_degrees(selected)
        if any(value > MAX_ENDPOINT_DEGREE for value in degree.values()):
            found.append("seed %s exceeds the endpoint-degree cap" % seed)
        for edge in selected:
            if not isinstance(edge, str) or edge.count(">") != 1:
                found.append("seed %s has an invalid target edge" % seed)
                continue
            u = (row.get("u") or {}).get(edge) or {}
            if u.get("measured_cycle") != U_CYCLE:
                found.append("seed %s target %s has no cycle-36 U" % (seed, edge))
            if (u.get("strength") or 0) <= 0:
                found.append("seed %s target %s has no positive strength" % (seed, edge))
            if not (row.get("cycle_member") or {}).get(edge):
                found.append("seed %s target %s is not cycle-member" % (seed, edge))
        digest = _hash(json.dumps({
            "seed": int(seed),
            "selected": selected,
            "n_per_seed": N_PER_SEED,
            "max_endpoint_degree": MAX_ENDPOINT_DEGREE,
        }, sort_keys=True))[:16]
        if row.get("selection_digest") != digest:
            found.append("seed %s C8 selection digest is stale" % seed)
    return found


def render(doc: dict) -> str:
    lines = [
        "# A1 C8 expansion target selection",
        "",
        "**ID:** `%s`  " % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an experimental result.** No A1 arm cell was run; no manifest was frozen.",
        "",
        "The design selects **20 A-K- target rows per seed** with the same pre-36 "
        "eligibility and hash order as the four-target protocol. Endpoint overlap is "
        "permitted and each tag's selected degree is capped at **3**; target rows are "
        "therefore not independent and no target edge is repeated. The C8 ceiling "
        "remains **0.05**, so the per-seed step is `1/20 = 0.05`.",
        "",
        "| Seed | Status | Candidates | Eligible | A-K- rows | Max degree |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for seed in SEEDS:
        row = doc["per_seed"][str(seed)]
        degree = max((row.get("endpoint_degree") or {"": 0}).values())
        lines.append("| %d | %s | %d | %d | %d | %d |" % (
            seed, row["status"], row["candidate_count"], row["eligible_count"],
            len(row["selected"]), degree,
        ))
    lines += [
        "",
        "**Registered, not frozen:** the live N=4 manifest is unchanged. Adopting this "
        "design requires a target-protocol/freeze act that replaces the current target "
        "set; this artifact authorises no run.",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def write() -> int:
    doc = build()
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    found = problems(doc)
    if not PAGE_PATH.exists():
        found.append("C8 expansion page is missing")
    elif PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("C8 expansion page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 C8 expansion selection: clean; %d seeds x %d rows"
          % (len(doc["per_seed"]), N_PER_SEED))
    return 0


def self_test() -> list[str]:
    found: list[str] = []
    # Twenty distinct edges over sixteen tags, each tag used at most three times.
    vertices = [chr(ord("a") + i) for i in range(16)]
    pairs = [(vertices[i], vertices[(i + 1) % 16]) for i in range(16)]
    pairs += [
        (vertices[0], vertices[8]),
        (vertices[1], vertices[9]),
        (vertices[2], vertices[10]),
        (vertices[3], vertices[11]),
    ]
    candidates = sorted(set(pairs))
    if len(candidates) != 20:
        return ["the C8 synthetic edge set is not twenty distinct edges"]
    u = {edge: {"strength": 1, "measured_cycle": U_CYCLE} for edge in candidates}
    members = {edge: True for edge in candidates}
    selected, _ = select_edges(1, candidates, u, members, n=20, disjoint=False,
                               max_endpoint_degree=3)
    if len(selected) != 20:
        found.append("the endpoint-degree cap cannot select twenty rows")
    degree = _endpoint_degrees(["%s>%s" % edge for edge in selected])
    if any(value > 3 for value in degree.values()):
        found.append("a synthetic selected edge exceeds the endpoint cap")
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.check:
        return check()
    found = self_test()
    for problem in found:
        print("FAIL:", problem)
    if not found:
        print("A1 C8 expansion selection: self-test clean")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
