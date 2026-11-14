"""A1 target selection: a pre-cycle-37, no-arm selection pass.

The selector is deliberately separate from the A1 arm runner.  It runs no
A-/K-/Y- cell, reads no ``SleepReport`` field and writes no experimental
result.  It builds a 36-cycle world, records the pre-37 temporal graph,
and selects four disjoint target edges per seed by a deterministic hash.
The output is a selection artifact, not a frozen manifest.

    python -m benchmarks.a1_target_selection --write
    python -m benchmarks.a1_target_selection --check
    python -m benchmarks.a1_target_selection --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import PHASE_ACQUISITION, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, _world_compositional_edges
from organica.memory import MemoryService
from organica.sleep import SleepService

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_target_selection.json"
PAGE_PATH = DOCS / "A1-TARGET-SELECTION.md"
ID = "A1-TARGET-SELECTION-1"
DATE = "2026-11-14"
SEEDS = (20630101, 20630102, 20630103, 20630104, 20630105, 20630106)
CYCLES = 120
U_CYCLE = 36
CAP = 40
N_PER_SEED = 4
KIND = "a1_target_selection"
SALT = "A1-TARGET-1"
ORIENTATION_SALT = "A1-TARGET-ORIENTATION-1"


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def orientation(seed: int, a: str, b: str) -> tuple[str, str]:
    """Choose one orientation for an unordered tag pair, deterministically."""
    left, right = sorted((a, b))
    digest = _hash("%s|%d|%s|%s" % (ORIENTATION_SALT, seed, left, right))
    return (left, right) if int(digest[0], 16) % 2 == 0 else (right, left)


def candidate_edges(seed: int, universe: set[tuple[str, str]]) -> list[tuple[str, str]]:
    """One deterministic orientation per unordered pair present in the universe."""
    by_pair: dict[tuple[str, str], tuple[str, str]] = {}
    for a, b in universe:
        if a == b:
            continue
        pair = tuple(sorted((a, b)))
        if pair in by_pair:
            continue
        chosen = orientation(seed, a, b)
        if chosen not in universe:
            chosen = (chosen[1], chosen[0])
        if chosen in universe:
            by_pair[pair] = chosen
    return sorted(by_pair.values())


def cycle_members(temporal: dict[str, dict[str, int]],
                  candidates: list[tuple[str, str]]) -> dict[tuple[str, str], bool]:
    """True when the candidate edge lies on a directed cycle in the temporal graph."""
    adjacency: dict[str, set[str]] = {}
    for a, targets in temporal.items():
        adjacency.setdefault(a, set()).update(targets)
    found: dict[tuple[str, str], bool] = {}
    for a, b in candidates:
        seen = {b}
        stack = [b]
        while stack and a not in seen:
            node = stack.pop()
            for nxt in adjacency.get(node, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        found[(a, b)] = a in seen
    return found


def select_edges(seed: int, candidates: list[tuple[str, str]],
                 u: dict[tuple[str, str], dict],
                 members: dict[tuple[str, str], bool],
                 n: int = N_PER_SEED) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Return (selected, eligible), both in deterministic selection order."""
    eligible = [
        edge for edge in candidates
        if int((u.get(edge) or {}).get("strength") or 0) > 0
        and members.get(edge) is True
    ]
    eligible.sort(key=lambda edge: (_hash("%s|%d|%s>%s" % (SALT, seed, edge[0], edge[1])),
                                     "%s>%s" % edge))
    selected: list[tuple[str, str]] = []
    used: set[str] = set()
    for edge in eligible:
        if edge[0] in used or edge[1] in used:
            continue
        selected.append(edge)
        used.update(edge)
        if len(selected) == n:
            return selected, eligible
    # The protocol permits exactly n targets or none; never a partial set.
    return [], eligible


def _u_row(temporal: dict[str, dict[str, int]],
           edge: tuple[str, str], cycle: int) -> dict:
    direct = int(temporal.get(edge[0], {}).get(edge[1], 0))
    reverse = int(temporal.get(edge[1], {}).get(edge[0], 0))
    return {
        "direct_count": direct,
        "reverse_count": reverse,
        "strength": direct + reverse,
        "measured_cycle": cycle,
    }


def _temporal(memory) -> dict[str, dict[str, int]]:
    temporal: dict[str, dict[str, int]] = {}
    for a, b, count in memory.temporal_edges(min_count=1):
        temporal.setdefault(a, {})[b] = count
    return temporal


def run_seed(seed: int, world: dict | None = None) -> dict:
    """Stream through acquisition cycle 36 and return its selection record.

    The candidate universe is built from the first 36 acquisition cycles,
    not from the full 120-cycle world.  The engine's sleep counter can lag
    the acquisition index, so the boundary is the acquisition cycle; no
    SleepReport field is read.  ``world`` is injectable so the
    future-blindness audit can compare a 36-cycle world with the first 36
    cycles of a 120-cycle world.
    """
    if world is None:
        world = generate_compositional_world(seed=seed, cycles=CYCLES)
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    db_path = _make_scratch_db("a1_target_selection")
    memory = MemoryService(str(db_path))
    service = SleepService(memory)
    service.MAX_PREDICTIONS = CAP
    temporal_at_u: dict[str, dict[str, int]] | None = None
    stop = 0
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source="env_acq" if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                cycle = (i + 1) // EVENTS_PER_CYCLE
                if cycle == U_CYCLE:
                    temporal_at_u = _temporal(memory)
                    stop = i + 1
                service.run_sleep_cycle()
                if cycle == U_CYCLE:
                    break
    finally:
        memory.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    truncated = dict(world)
    truncated["events"] = world["events"][:stop]
    truncated["trainable"] = world["trainable"][:stop]
    universe = _world_compositional_edges(truncated)
    candidates = candidate_edges(seed, universe)
    temporal = temporal_at_u or {}
    u = {edge: _u_row(temporal, edge, U_CYCLE) for edge in candidates}
    members = cycle_members(temporal, candidates)
    selected, eligible = select_edges(seed, candidates, u, members)
    status = "TARGET SET FORMED" if len(selected) == N_PER_SEED else "TARGET SET NOT FORMED"
    payload = {
        "seed": seed,
        "status": status,
        "cycles": len(world["events"]) // EVENTS_PER_CYCLE,
        "event_cycles": (stop + EVENTS_PER_CYCLE - 1) // EVENTS_PER_CYCLE,
        "u_cycle": U_CYCLE,
        "n_per_seed": N_PER_SEED,
        "candidate_count": len(candidates),
        "eligible_count": len(eligible),
        "selected": ["%s>%s" % edge for edge in selected],
        "u": {
            "%s>%s" % edge: u.get(edge, {
                "direct_count": None,
                "reverse_count": None,
                "strength": None,
                "measured_cycle": None,
            })
            for edge in candidates
        },
        "cycle_member": {"%s>%s" % edge: members.get(edge, False) for edge in candidates},
        "universe_digest": _hash("\n".join(sorted("%s>%s" % edge for edge in universe)))[:16],
    }
    payload["selection_digest"] = _hash(
        json.dumps({k: payload[k] for k in (
            "seed", "status", "candidate_count", "eligible_count",
            "selected", "u", "cycle_member", "universe_digest", "event_cycles",
        )}, sort_keys=True)
    )[:16]
    return payload


def build() -> dict:
    per_seed = {str(seed): run_seed(seed) for seed in SEEDS}
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": "TARGET SETS FORMED — DRAFT, NOT FROZEN, NOT A RESULT",
        "protocol": "docs/A1-TARGET-SELECTION-PROTOCOL.md",
        "engine": "0.15.0",
        "cycles": CYCLES,
        "u_cycle": U_CYCLE,
        "n_per_seed": N_PER_SEED,
        "salt": SALT,
        "orientation_salt": ORIENTATION_SALT,
        "per_seed": per_seed,
        "not_evidence": (
            "A no-arm, 36-cycle target-selection pass. It chooses targets but "
            "freezes no manifest, authorises no cell and records no result."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("selection kind")
    if doc.get("n_per_seed") != N_PER_SEED:
        found.append("selection n_per_seed")
    if doc.get("cycles") != CYCLES or doc.get("u_cycle") != U_CYCLE:
        found.append("selection cycle boundary")
    per_seed = doc.get("per_seed") or {}
    if set(per_seed) != {str(seed) for seed in SEEDS}:
        found.append("selection seed block")
    for seed, row in per_seed.items():
        selected = row.get("selected") or []
        if not isinstance(selected, list):
            found.append("seed %s selected is not a list" % seed)
            continue
        digest = _hash(json.dumps({k: row.get(k) for k in (
            "seed", "status", "candidate_count", "eligible_count",
            "selected", "u", "cycle_member", "universe_digest", "event_cycles",
        )}, sort_keys=True))[:16]
        if row.get("selection_digest") != digest:
            found.append("seed %s selection digest is stale" % seed)
        if row.get("status") == "TARGET SET FORMED" and len(selected) != N_PER_SEED:
            found.append("seed %s formed a set of %d" % (seed, len(selected)))
        if len(selected) != N_PER_SEED:
            continue
        used: set[str] = set()
        for edge in selected:
            if not isinstance(edge, str) or edge.count(">") != 1:
                found.append("seed %s has an invalid edge" % seed)
                continue
            a, b = edge.split(">", 1)
            if a in used or b in used:
                found.append("seed %s targets are not disjoint" % seed)
            used.update((a, b))
            u = (row.get("u") or {}).get(edge) or {}
            if u.get("measured_cycle") != U_CYCLE:
                found.append("seed %s target %s has no cycle-36 U" % (seed, edge))
            if (u.get("strength") or 0) <= 0:
                found.append("seed %s target %s has no positive strength" % (seed, edge))
            if not (row.get("cycle_member") or {}).get(edge):
                found.append("seed %s target %s is not cycle-member" % (seed, edge))
    return found


def render(payload: dict) -> str:
    rows = [
        "# A1 target selection",
        "",
        "**Status:** `%s`" % payload["status"],
        "",
        "**This is not an experimental result.** No arm cell was run; no manifest was frozen.",
        "",
        "| Seed | Status | Candidates | Eligible | Selected |",
        "| ---: | --- | ---: | ---: | --- |",
    ]
    for seed in SEEDS:
        row = payload["per_seed"][str(seed)]
        rows.append("| %d | %s | %d | %d | %s |" % (
            seed, row["status"], row["candidate_count"], row["eligible_count"],
            ", ".join("`%s`" % edge for edge in row["selected"]) or "none",
        ))
    rows += ["", "**Not evidence:** %s" % payload["not_evidence"], ""]
    return "\n".join(rows)


def write() -> int:
    payload = build()
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(payload), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    found = problems(doc)
    if not PAGE_PATH.exists():
        found.append("selection page is missing")
    elif PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("selection page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 target selection: clean; %d seeds" % len(doc["per_seed"]))
    return 0


def self_test() -> list[str]:
    found: list[str] = []
    universe = {
        ("a", "b"), ("b", "a"), ("c", "d"), ("d", "c"),
        ("e", "f"), ("f", "e"), ("g", "h"), ("h", "g"),
    }
    candidates = candidate_edges(1, universe)
    if len(candidates) != 4:
        found.append("candidate orientation count")
    if any(candidate_edges(1, universe) != candidates for _ in range(2)):
        found.append("candidate orientation is not deterministic")
    temporal = {
        "a": {"b": 3}, "b": {"a": 2},
        "c": {"d": 4}, "d": {"c": 1},
        "e": {"f": 2}, "f": {"e": 1},
        "g": {"h": 2}, "h": {"g": 1},
    }
    members = cycle_members(temporal, candidates)
    ab = next(edge for edge in candidates if set(edge) == {"a", "b"})
    if not members.get(ab):
        found.append("the a/b orientation is not seen as cycle-member")
    u = {edge: _u_row(temporal, edge, U_CYCLE) for edge in candidates}
    selected, _ = select_edges(1, candidates, u, members)
    if len(selected) != 4:
        found.append("four disjoint targets are not selected")
    changed = dict(u)
    for edge in changed:
        changed[edge] = dict(changed[edge], strength=changed[edge]["strength"] + 100)
    if select_edges(1, candidates, changed, members)[0] != selected:
        found.append("selection changes when U magnitude changes")
    if len(select_edges(1, candidates[:3], u, members)[0]) == 4:
        found.append("selection made four targets from three")
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
        print("A1 target selection: self-test clean")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
