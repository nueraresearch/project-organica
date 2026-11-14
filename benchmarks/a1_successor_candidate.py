"""A fresh six-seed candidate for the A1 successor preflight.

The block is fixed without K screening: six contiguous seeds,
``20650101``-``20650106``, on the same 16-tag compositional world family and the
same first-36-cycle candidate universe.  It is deliberately **not** screened for
high K availability; that would select on the quantity the preflight is meant to
test.  Every seed is replayed with no A-, K- or Y- treatment, once for the
36-cycle candidate universe and once for the 120-cycle A/K baseline.

This module writes a candidate spec only.  It selects no target, freezes no
target, reserves no seed, issues no grant and runs no A1 cell.  The spec is then
fed to ``benchmarks.a1_successor_preflight``.

    python -m benchmarks.a1_successor_candidate --write
    python -m benchmarks.a1_successor_candidate --check
    python -m benchmarks.a1_successor_candidate --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import a1_baseline_availability
from benchmarks import a1_successor_preflight
from benchmarks import a1_target_selection

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_successor_candidate.json"
PAGE_PATH = DOCS / "A1-SUCCESSOR-CANDIDATE.md"
ID = "A1-SUCCESSOR-CANDIDATE-1"
DATE = "2026-11-14"
KIND = "a1_successor_candidate"
SEEDS = (20650101, 20650102, 20650103, 20650104, 20650105, 20650106)
STATUS = "CANDIDATE SPEC — NO ARM, NO TARGET, NOT FROZEN, NOT RUN"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(seed: int) -> tuple[dict, dict]:
    selection = a1_target_selection.run_seed(seed, boundary_safe=True)
    baseline = a1_baseline_availability._run_seed(seed)
    available = {row["edge"]: row for row in baseline["rows"]}
    rows = []
    for edge in sorted(selection["u"]):
        row = available[edge]
        rows.append({
            "edge": edge,
            "A": bool(row["A"]),
            "K": bool(row["K"]),
        })
    return selection, rows


def build() -> dict:
    per_seed = {}
    summaries = []
    for seed in SEEDS:
        selection, rows = _rows(seed)
        per_seed[str(seed)] = rows
        summaries.append({
            "seed": seed,
            "candidate_edges": len(rows),
            "independent_edges": len({
                tuple(sorted(edge.split(">", 1))) for edge in (r["edge"] for r in rows)
            }),
            "A_available": sum(row["A"] for row in rows),
            "K_available": sum(row["K"] for row in rows),
            "A_and_K": sum(row["A"] and row["K"] for row in rows),
            "selection_status": selection["status"],
        })
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "seed_block": list(SEEDS),
        "targets_in_scope": True,
        "selection": {
            "source": "A1-TARGET-SELECTION-1",
            "u_cycle": 36,
            "cycles": 120,
            "one_orientation_per_pair": True,
            "boundary_safe": True,
            "boundary_note": "candidate uses the opt-in cycle-boundary correction; the registered selector remains legacy",
            "screen": "none — the block was fixed without K screening; a one-seed timing probe did not alter it",
            "targets_selected": 0,
        },
        "baseline": {
            "source": "A1-BASELINE-AVAILABILITY-1",
            "cycles": 120,
            "treatment": "none",
            "A": "prediction path available at least once",
            "K": "carrier path available at least once",
        },
        "per_seed": per_seed,
        "summaries": summaries,
        "not_evidence": (
            "A no-arm candidate specification and its raw A/K rows. It selects "
            "no target, freezes no target, reserves no seed, issues no grant and "
            "runs no A1 cell. Passing the preflight would not authorise a run."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("candidate kind")
    if doc.get("id") != ID:
        found.append("candidate id")
    if doc.get("status") != STATUS:
        found.append("candidate status")
    if doc.get("seed_block") != list(SEEDS):
        found.append("candidate seed block")
    if doc.get("selection", {}).get("targets_selected") != 0:
        found.append("candidate selects targets")
    if doc.get("selection", {}).get("screen") != "none — the block was fixed without K screening; a one-seed timing probe did not alter it":
        found.append("candidate K screen is not declared")
    per_seed = doc.get("per_seed") or {}
    if set(per_seed) != {str(seed) for seed in SEEDS}:
        found.append("candidate per-seed block")
        return found
    for seed, rows in per_seed.items():
        edges = [row.get("edge") for row in rows]
        if len(edges) != len(set(edges)):
            found.append("seed %s has duplicate edges" % seed)
        pairs = []
        for edge in edges:
            if not isinstance(edge, str) or edge.count(">") != 1:
                found.append("seed %s has an invalid edge" % seed)
                continue
            a, b = edge.split(">", 1)
            if a == b:
                found.append("seed %s has a self-loop" % seed)
            pairs.append(tuple(sorted((a, b))))
        if len(pairs) != len(set(pairs)):
            found.append("seed %s is not one-orientation-per-pair" % seed)
        for row in rows:
            if not isinstance(row.get("A"), bool) or not isinstance(row.get("K"), bool):
                found.append("seed %s has a non-boolean A/K row" % seed)
                break
    result = a1_successor_preflight.evaluate(doc)
    if result["seeds_total"] != len(SEEDS):
        found.append("candidate preflight seed count")
    return found


def self_test() -> list[str]:
    found: list[str] = []
    spec = {
        "kind": KIND,
        "id": ID,
        "status": STATUS,
        "seed_block": list(SEEDS),
        "selection": {
            "targets_selected": 0,
            "screen": "none — the block was fixed without K screening; a one-seed timing probe did not alter it",
            "boundary_safe": True,
        },
        "per_seed": {
            str(seed): [{"edge": "a>b", "A": True, "K": True}]
            for seed in SEEDS
        },
    }
    # The fixture is intentionally tiny; it must not be mistaken for the real
    # candidate, which has 63-64 edges per seed.
    result = a1_successor_preflight.evaluate(spec)
    if result["seeds_total"] != 6:
        found.append("candidate self-test seed count")
    return found


def render(doc: dict) -> str:
    result = a1_successor_preflight.evaluate(doc)
    lines = [
        "# A1 successor candidate — fresh seed block",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**No target is selected, frozen or run.** This is a fresh six-seed candidate for the no-arm preflight, not a successor design adopted by the project. It uses the opt-in cycle-boundary correction for candidate formation; the registered selector remains unchanged.",
        "",
        "## Why this block",
        "",
        "The block is **20650101–20650106**, fixed without K screening: six contiguous fresh seeds on the same 16-tag compositional world family and the same first-36-cycle candidate universe. It is not screened for high K availability; screening on K would select on the quantity being tested.",
        "",
        "| Seed | Candidate edges | Independent | A | K | A&K |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["summaries"]:
        lines.append(
            "| `%d` | %d | %d | %d | %d | %d |" % (
                row["seed"], row["candidate_edges"], row["independent_edges"],
                row["A_available"], row["K_available"], row["A_and_K"],
            )
        )
    lines += [
        "",
        "## Preflight result",
        "",
        "**`%s`** — %d/%d seeds pass." % (
            result["status"], result["seeds_passed"], result["seeds_total"]),
        "",
        "| Seed | C1 ceiling | Gap to 60 | Target matching | Result |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in result["per_seed"]:
        lines.append(
            "| `%d` | %d | %d | %d | %s |" % (
                row["seed"], row["C1_ceiling"], row["gap_to_60"],
                row["target_matching"], "PASS" if row["pass"] else "FAIL",
            )
        )
    lines += [
        "",
        "**This is a candidate result, not a freeze or a run.** A PASS would only mean the no-arm universe clears the 60-row C1/K gate; a new protocol, freeze, seed reservation and grant remain separate acts.",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_successor_candidate --check",
        "python -m benchmarks.a1_successor_candidate --self-test",
        "python -m benchmarks.a1_successor_candidate --write",
        "python -m benchmarks.a1_successor_preflight --spec docs/a1_successor_candidate.json --write",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def write() -> int:
    doc = build()
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
    result = a1_successor_preflight.evaluate(doc)
    print(
        "A1 successor candidate: clean; preflight %s; %d/%d seeds pass"
        % (result["status"], result["seeds_passed"], result["seeds_total"]))
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
        print("A1 successor candidate: self-test clean")
        return 0
    if args.write:
        return write()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
