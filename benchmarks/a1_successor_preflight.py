"""No-arm successor preflight for the A1 C1/K gate.

This is the gate the disposition memo asks for: before any target freeze, test a
candidate successor universe or fresh seed block for

* at least 60 independent edges per seed;
* at least 60 K-available rows per seed (and at least 60 A-available rows, so the
  C1 ceiling ``min(A, K)`` clears 60);
* one orientation per undirected pair, with no duplicate or reverse-duplicate
  stream;
* if C2/C8 are in scope, a capacity-respecting matching of at least 20
  baseline A+K-competent targets.

It never opens a database, runs an engine, selects a target, freezes a target,
reserves a seed or issues a grant.  A candidate is supplied as a small JSON
spec with no-arm A/K rows; absent a candidate, the report is NOT RUN.

The current six-seed universe is included only as a **negative control**: it is
known to fail the C1/K gate at 31-44 rows per seed.  It is not a successor and
is not a target set.

    python -m benchmarks.a1_successor_preflight --write
    python -m benchmarks.a1_successor_preflight --check
    python -m benchmarks.a1_successor_preflight --self-test
    python -m benchmarks.a1_successor_preflight --spec candidate.json --write

Spec shape::

    {
      "kind": "a1_successor_candidate",
      "id": "candidate-id",
      "seed_block": [20630101, ...],
      "targets_in_scope": true,
      "per_seed": {
        "20630101": [
          {"edge": "a>b", "A": true, "K": true},
          ...
        ]
      }
    }
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_successor_preflight.json"
PAGE_PATH = DOCS / "A1-SUCCESSOR-PREFLIGHT.md"
BASELINE_PATH = DOCS / "a1_baseline_availability.json"
TARGET_SELECTION_PATH = DOCS / "a1_target_selection.json"
ID = "A1-SUCCESSOR-PREFLIGHT-1"
DATE = "2026-11-14"
KIND = "a1_successor_preflight"
SEEDS = (20630101, 20630102, 20630103, 20630104, 20630105, 20630106)
C1_FLOOR = 60
TARGET_ROWS = 20
MAX_ENDPOINT_DEGREE = 3
MIN_SEEDS = 6


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _max_flow(edges: list[tuple[str, str]], capacities: dict[str, int]) -> int:
    """Maximum edge count under per-tag capacities, unit edge capacity."""
    source, sink = "__source__", "__sink__"
    graph: dict[str, dict[str, int]] = {}

    def add(a: str, b: str, capacity: int) -> None:
        graph.setdefault(a, {})
        graph.setdefault(b, {})
        graph[a][b] = graph[a].get(b, 0) + capacity
        graph[b].setdefault(a, 0)

    for index, (a, b) in enumerate(edges):
        edge_node = "__edge_%d__" % index
        add(source, edge_node, 1)
        add(edge_node, a, 1)
        add(edge_node, b, 1)
    for tag, capacity in capacities.items():
        if capacity > 0:
            add(tag, sink, capacity)

    total = 0
    while True:
        parent: dict[str, str | None] = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            node = queue.popleft()
            for nxt, capacity in graph.get(node, {}).items():
                if capacity > 0 and nxt not in parent:
                    parent[nxt] = node
                    queue.append(nxt)
        if sink not in parent:
            return total
        flow, node = 10 ** 9, sink
        while parent[node] is not None:
            previous = parent[node]
            flow = min(flow, graph[previous][node])
            node = previous
        node = sink
        while parent[node] is not None:
            previous = parent[node]
            graph[previous][node] -= flow
            graph[node][previous] += flow
            node = previous
        total += flow


def _matching(eligible: list[str]) -> int:
    tags = sorted({tag for edge in eligible for tag in edge.split(">", 1)})
    capacities = {tag: MAX_ENDPOINT_DEGREE for tag in tags}
    return _max_flow(
        [tuple(edge.split(">", 1)) for edge in eligible], capacities)


def _spec_from_current() -> dict:
    baseline = _load(BASELINE_PATH)
    selection = _load(TARGET_SELECTION_PATH)
    per_seed = {}
    for seed in SEEDS:
        rows = {
            row["edge"]: row
            for row in next(
                block for block in baseline["per_seed"]
                if int(block["seed"]) == seed
            )["rows"]
        }
        u = selection["per_seed"][str(seed)]["u"]
        per_seed[str(seed)] = [
            {"edge": edge, "A": bool(rows[edge]["A"]), "K": bool(rows[edge]["K"])}
            for edge in sorted(u)
        ]
    return {
        "kind": "a1_successor_candidate",
        "id": "current-six-seed-control",
        "seed_block": list(SEEDS),
        "targets_in_scope": True,
        "per_seed": per_seed,
    }


def evaluate(spec: dict) -> dict:
    """Evaluate one candidate spec, fail closed, and never select a target."""
    seed_block = spec.get("seed_block") or []
    problems: list[str] = []
    if len(seed_block) != len(set(seed_block)):
        problems.append("DUPLICATE_SEED")
    if len(seed_block) < MIN_SEEDS:
        problems.append("TOO_FEW_SEEDS")
    if set(str(seed) for seed in seed_block) != set(spec.get("per_seed", {})):
        problems.append("SEED_BLOCK_MISMATCH")

    per_seed = []
    for seed in seed_block:
        rows = spec.get("per_seed", {}).get(str(seed), []) or []
        seen_directed = set()
        seen_reverse = set()
        directed_duplicates = 0
        reverse_duplicates = 0
        self_loops = 0
        by_pair: dict[tuple[str, str], str] = {}
        for row in rows:
            edge = str(row.get("edge", ""))
            if edge.count(">") != 1:
                problems.append("INVALID_EDGE")
                continue
            source, target = edge.split(">", 1)
            if not source or not target or source == target:
                self_loops += 1
                continue
            if edge in seen_directed:
                directed_duplicates += 1
                continue
            seen_directed.add(edge)
            pair = tuple(sorted((source, target)))
            if edge in seen_reverse:
                reverse_duplicates += 1
            if pair in by_pair:
                reverse_duplicates += 1
                continue
            by_pair[pair] = edge
            seen_reverse.add(target + ">" + source)

        independent = list(by_pair.values())
        A = sum(bool(row.get("A")) for row in rows)
        K = sum(bool(row.get("K")) for row in rows)
        c1 = min(A, K, len(independent))
        target_pool = [
            edge for edge in independent
            if next(row for row in rows
                    if row.get("edge") == edge).get("A") and
            next(row for row in rows
                 if row.get("edge") == edge).get("K")
        ]
        matching = _matching(target_pool)
        reasons = []
        if directed_duplicates:
            reasons.append("DUPLICATE_EDGE")
        if reverse_duplicates:
            reasons.append("REVERSE_DUPLICATE")
        if self_loops:
            reasons.append("SELF_LOOP")
        if len(independent) < C1_FLOOR:
            reasons.append("INDEPENDENT_BELOW_60")
        if c1 < C1_FLOOR:
            reasons.append("C1_BELOW_60")
        if spec.get("targets_in_scope", True) and matching < TARGET_ROWS:
            reasons.append("TARGET_POOL_BELOW_20")
        per_seed.append({
            "seed": seed,
            "edges": len(rows),
            "independent_edges": len(independent),
            "A_available": A,
            "K_available": K,
            "C1_ceiling": c1,
            "gap_to_60": max(0, C1_FLOOR - c1),
            "K_gap_to_60": max(0, C1_FLOOR - K),
            "directed_duplicates": directed_duplicates,
            "reverse_duplicates": reverse_duplicates,
            "self_loops": self_loops,
            "target_pool": len(target_pool),
            "target_matching": matching,
            "reasons": reasons,
            "pass": not reasons,
        })
    if any(not row["pass"] for row in per_seed):
        status = "FAIL"
    elif problems:
        status = "FAIL"
    else:
        status = "PASS"
    return {
        "id": spec.get("id"),
        "status": status,
        "problems": sorted(set(problems)),
        "per_seed": per_seed,
        "seeds_passed": sum(1 for row in per_seed if row["pass"]),
        "seeds_total": len(per_seed),
    }


def build(spec: dict | None = None) -> dict:
    current = evaluate(_spec_from_current())
    successor = (
        {"status": "NOT RUN", "problems": ["NO_SUCCESSOR_UNIVERSE"],
         "per_seed": [], "seeds_passed": 0, "seeds_total": 0}
        if spec is None else evaluate(spec)
    )
    if successor["status"] == "PASS":
        overall = "PASS — SUCCESSOR CANDIDATE CLEARS GATE"
    elif successor["status"] == "FAIL":
        overall = "FAIL — SUCCESSOR CANDIDATE BELOW GATE"
    else:
        overall = "NOT RUN — NO SUCCESSOR UNIVERSE; CURRENT CONTROL FAILS"
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": overall,
        "gate": {
            "c1_floor": C1_FLOOR,
            "target_rows": TARGET_ROWS,
            "max_endpoint_degree": MAX_ENDPOINT_DEGREE,
            "min_seeds": MIN_SEEDS,
            "independent_stream": True,
            "targets_in_scope": "declared per candidate",
            "no_arm": True,
            "freeze": False,
            "grant": False,
            "run": False,
        },
        "current_control": current,
        "successor": successor,
        "not_evidence": (
            "A no-arm preflight. It evaluates supplied baseline rows, selects no "
            "target, freezes no target, reserves no seed, issues no grant and "
            "runs no A1 cell. The current six-seed universe is a negative "
            "control, not a successor candidate."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("record kind")
    if doc.get("id") != ID:
        found.append("record id")
    gate = doc.get("gate") or {}
    if gate.get("c1_floor") != C1_FLOOR:
        found.append("C1 floor changed")
    if any(gate.get(key) for key in ("freeze", "grant", "run")):
        found.append("preflight claims an act it did not perform")
    for name in ("current_control", "successor"):
        block = doc.get(name) or {}
        rows = block.get("per_seed") or []
        if block.get("seeds_passed") != sum(1 for row in rows if row.get("pass")):
            found.append("%s seed count is inconsistent" % name)
        for row in rows:
            if row.get("C1_ceiling") != min(
                    row.get("A_available", 0), row.get("K_available", 0),
                    row.get("independent_edges", 0)):
                found.append("%s C1 ceiling is inconsistent" % name)
            if row.get("pass") != (not row.get("reasons")):
                found.append("%s pass flag is inconsistent" % name)
    if doc.get("current_control", {}).get("status") != "FAIL":
        found.append("current control must remain a negative control")
    if doc.get("successor", {}).get("status") == "NOT RUN":
        if "NO_SUCCESSOR_UNIVERSE" not in doc["successor"].get("problems", []):
            found.append("missing NOT RUN reason")
    return found


def self_test() -> list[str]:
    found: list[str] = []
    # A regular 16-tag candidate with 64 independent edges per seed.
    tags = ["t%02d" % i for i in range(16)]
    edges = []
    for i in range(16):
        for j in range(1, 5):
            edges.append("%s>%s" % (tags[i], tags[(i + j) % 16]))
    edges = sorted(set(edges))[:64]
    spec = {
        "kind": "a1_successor_candidate",
        "id": "fixture",
        "seed_block": list(range(1, 7)),
        "targets_in_scope": True,
        "per_seed": {
            str(seed): [{"edge": edge, "A": True, "K": True} for edge in edges]
            for seed in range(1, 7)
        },
    }
    result = evaluate(spec)
    if result["status"] != "PASS":
        found.append("clean fixture should pass")
    bad = json.loads(json.dumps(spec))
    first = bad["per_seed"]["1"][0]["edge"]
    reverse = first.split(">")[1] + ">" + first.split(">")[0]
    bad["per_seed"]["1"].append({"edge": reverse, "A": True, "K": True})
    result = evaluate(bad)
    if result["status"] != "FAIL":
        found.append("reverse-duplicate fixture should fail")
    return found


def render(doc: dict) -> str:
    gate = doc["gate"]
    current = doc["current_control"]
    successor = doc["successor"]
    lines = [
        "# A1 successor preflight — no-arm C1/K gate",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**No target is selected, frozen or run.** This checks whether a supplied successor universe clears the **≥%d independent K/A rows per seed** gate before any target freeze. Without a candidate, the result is **NOT RUN**." % gate["c1_floor"],
        "",
        "## Gate",
        "",
        "| Check | Requirement |",
        "| --- | --- |",
        "| Independent stream | ≥%d independent edges/seed; no duplicate or reverse-duplicate orientations |" % gate["c1_floor"],
        "| C1 ceiling | `min(A available, K available, independent edges)` ≥%d/seed |" % gate["c1_floor"],
        "| Targets | If in scope, a capacity-respecting **%d-row** baseline A+K matching |" % gate["target_rows"],
        "| Seeds | At least **%d** |" % gate["min_seeds"],
        "",
        "## Current six-seed control",
        "",
        "This is a negative control, not a successor candidate.",
        "",
        "| Seed | Independent | A | K | C1 ceiling | Gap to 60 | Target pool | Matching | Result |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in current["per_seed"]:
        lines.append(
            "| `%d` | %d | %d | %d | %d | %d | %d | %d | %s |" % (
                row["seed"], row["independent_edges"], row["A_available"],
                row["K_available"], row["C1_ceiling"], row["gap_to_60"],
                row["target_pool"], row["target_matching"],
                "PASS" if row["pass"] else "FAIL",
            )
        )
    lines += [
        "",
        "**Control result:** `%s` — %d/%d seeds pass." % (
            current["status"], current["seeds_passed"], current["seeds_total"]),
        "",
        "## Successor candidate",
        "",
    ]
    if successor["status"] == "NOT RUN":
        lines += [
            "**NOT RUN.** No successor universe or fresh seed block has been supplied. The current universe is not eligible: its C1 ceiling is **31–44**, below 60.",
            "",
            "Supply a `--spec` JSON with one orientation per undirected pair and no-arm A/K rows per edge; the preflight will return `PASS` or `FAIL` before any target freeze.",
        ]
    else:
        lines += [
            "| Seed | Independent | A | K | C1 ceiling | Gap to 60 | Target pool | Matching | Result |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
        for row in successor["per_seed"]:
            lines.append(
                "| `%d` | %d | %d | %d | %d | %d | %d | %d | %s |" % (
                    row["seed"], row["independent_edges"], row["A_available"],
                    row["K_available"], row["C1_ceiling"], row["gap_to_60"],
                    row["target_pool"], row["target_matching"],
                    "PASS" if row["pass"] else "FAIL",
                )
            )
        lines += [
            "",
            "**Candidate result:** `%s` — %d/%d seeds pass." % (
                successor["status"], successor["seeds_passed"],
                successor["seeds_total"]),
        ]
    lines += [
        "",
        "## Disposition",
        "",
        "Even a `PASS` here does **not** freeze or authorise a run. It establishes only that the supplied no-arm universe clears the C1/K gate and, if in scope, the 20-target matching gate. A new protocol, freeze, seed reservation, grant and run remain separate acts.",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_successor_preflight --check",
        "python -m benchmarks.a1_successor_preflight --self-test",
        "python -m benchmarks.a1_successor_preflight --spec candidate.json --write",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def write(spec_path: Path | None = None) -> int:
    spec = _load(spec_path) if spec_path else None
    doc = build(spec)
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = _load(OUT_PATH)
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print(
        "A1 successor preflight: clean; %s; control %s"
        % (doc["status"], doc["current_control"]["status"]))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--spec", type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        found = self_test()
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("A1 successor preflight: self-test clean")
        return 0
    if args.write:
        return write(args.spec)
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
