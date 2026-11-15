"""Does V1's carrier set carry a functional address?

The structural model claims V1 has no *explicit* address and leaves open whether a key derived
from the stored state can isolate a carrier. This module answers that for one no-arm world: it
replays the world, keeps every loop the engine returns with its id and path, and asks whether the
path is a collision-free key and whether the emitted id is an address.

Read-only: no arm, no target, no freeze, no grant. It rebuilds the world the same way the A2
feasibility check does, and changes nothing.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

from benchmarks import a1_arms, a1_c5_target_timing as timing
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.a2_sham_feasibility import CYCLES

SEED = 20740101
OUT = "docs/v1_carrier_identity.json"


def replay(seed: int = SEED) -> list[tuple[int, str, tuple[str, ...]]]:
    """Every (cycle, loop id, path) the engine returns, one entry per cycle."""
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    db_path = _make_scratch_db("v1_carrier_identity")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = timing.CAP
    acq_lo, acq_hi = timing.PHASE_ACQUISITION
    event_lo = acq_lo * timing.EVENTS_PER_CYCLE
    event_hi = acq_hi * timing.EVENTS_PER_CYCLE
    found: list[tuple[int, str, tuple[str, ...]]] = []
    for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
        in_acq = event_lo <= i < event_hi
        if in_acq and not trainable:
            continue
        if i % timing.EVENTS_PER_CYCLE == 0:
            memory.current_cycle = i // timing.EVENTS_PER_CYCLE
        memory.store(text, event_type="observe",
                     source=a1_arms.ACQ_SOURCE if in_acq else "env")
        if (i + 1) % timing.EVENTS_PER_CYCLE:
            continue
        report = service.run_sleep_cycle()
        for loop in getattr(report, "loops", []) or []:
            path = tuple(getattr(loop, "path", []) or ())
            if len(path) >= 2:
                found.append((i // timing.EVENTS_PER_CYCLE, str(getattr(loop, "id", "")), path))
    return found


def _canonical(path: tuple[str, ...]) -> tuple[str, ...]:
    """The path as an undirected cycle: rotation-normalised, direction-free."""
    body = list(path[:-1]) if len(path) > 1 and path[0] == path[-1] else list(path)
    if not body:
        return ()
    best = None
    for seq in (body, list(reversed(body))):
        for i in range(len(seq)):
            rotated = tuple(seq[i:] + seq[:i])
            if best is None or rotated < best:
                best = rotated
    return best or ()


def analyse(entries: list[tuple[int, str, tuple[str, ...]]]) -> dict:
    paths = collections.Counter(p for _, _, p in entries)
    ids = collections.Counter(i for _, i, _ in entries)
    id_to_paths: dict[str, set[tuple[str, ...]]] = collections.defaultdict(set)
    for _, lid, path in entries:
        id_to_paths[lid].add(path)
    collisions = {lid: sorted(ps) for lid, ps in id_to_paths.items() if len(ps) > 1}
    distinct = sorted(paths)
    cycles_of: dict[tuple[str, ...], set[int]] = collections.defaultdict(set)
    for cycle, _, path in entries:
        cycles_of[path].add(cycle)
    by_set: dict[tuple[str, ...], set[tuple[str, ...]]] = collections.defaultdict(set)
    for path in distinct:
        by_set[_canonical(path)].add(path)
    multis = {key: paths_ for key, paths_ in by_set.items() if len(paths_) > 1}
    first_seen = {path: min(cycles) for path, cycles in cycles_of.items()}
    flips = {key: paths_ for key, paths_ in multis.items()
             if len({first_seen[p] for p in paths_}) > 1}
    same_cycle = sum(1 for paths_ in multis.values()
                     if set.intersection(*[cycles_of[p] for p in paths_]))
    hist = collections.Counter(len(paths_) for paths_ in by_set.values())
    n_ids = len(ids)
    birthday = 1 - pow(1 - 1 / 2 ** 32, n_ids * (n_ids - 1) / 2)
    return {
        "seed": SEED,
        "appearances": len(entries),
        "distinct_paths": len(distinct),
        "distinct_node_sets": len(by_set),
        "distinct_ids": n_ids,
        "id_collisions": len(collisions),
        "collision_examples": list(collisions.items())[:3],
        "reversed_three_cycles_present": sum(1 for p in distinct
                                             if len(p) == 4 and tuple(reversed(p)) in set(distinct)),
        "node_sets_with_two_directions": len(multis),
        "paths_per_node_set": {str(k): v for k, v in sorted(hist.items())},
        "directions_appear_in_different_cycles": len(flips),
        "node_sets_where_both_directions_share_a_cycle": same_cycle,
        "stable_identity_across_cycles": len(multis) == 0,
        "id_bits": 32,
        "birthday_collision_probability": round(birthday, 6),
        "id_is_injective": len(collisions) == 0,
        "id_is_invertible": False,
        "recomputed_deterministically": None,
    }


def build() -> dict:
    first = replay()
    second = replay()
    doc = analyse(first)
    doc["recomputed_deterministically"] = sorted(first) == sorted(second)
    doc["identical_including_cycle"] = first == second
    return doc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        stored = json.loads(Path(OUT).read_text(encoding="utf-8"))
        fresh = build()
        if stored != fresh:
            differing = sorted(k for k in set(stored) | set(fresh) if stored.get(k) != fresh.get(k))
            print("FAIL: the artifact drifted from a fresh replay: %r" % (differing,))
            return 1
        print("carrier identity: clean (rebuild matches, %d paths)" % fresh["distinct_paths"])
        return 0
    doc = build()
    if args.write:
        with open(OUT, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print("wrote", OUT)
    print(json.dumps(doc, indent=1)[:1200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
