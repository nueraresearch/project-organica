"""PRESENCE-CAP-LADDER-1: cell runner and dry-run planner.

The block is frozen and ungranted. ``--dry-run`` prints the 24 ``--cell SEED
CAP`` commands without opening a database. ``--cell`` runs one planned cell,
but only after the record carries a dated grant; without one it refuses before
any database is opened. Each successful cell writes a part under
``.scratch/presence_cap_ladder/parts``.

The runner changes only ``MAX_PREDICTIONS`` through the repaired observer. It
does not grant the block, does not write a result artifact and does not
adjudicate the ladder.

    python -m benchmarks.presence_cap_ladder_arm --dry-run
    python -m benchmarks.presence_cap_ladder_arm --cell 20614101 40
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from organica.sleep import SleepService

from benchmarks import engine_stamp
from benchmarks import presence_cap_ladder_prereg as block
from benchmarks import presence_conversion_repair_observer as observer
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.presence_construct_audit import (ACQ_SOURCE, PHASE_ACQUISITION,
                                                 _digest, _world_compositional_edges,
                                                 asserted_fingerprint)

MODULE = "benchmarks.presence_cap_ladder_arm"
PARTS = Path(__file__).resolve().parents[1] / ".scratch" / "presence_cap_ladder" / "parts"


def planned() -> list[tuple[int, int]]:
    """The frozen cells, in record order: each seed at 40, 56, 80 and 112."""
    design = block.record()["design"]
    return [(int(seed), int(cap)) for seed in design["seeds"] for cap in design["caps"]]


def command(seed: int, cap: int) -> str:
    return "python -m %s --cell %d %d" % (MODULE, seed, cap)


def dry_run() -> int:
    for seed, cap in planned():
        print(command(seed, cap))
    return 0


def preflight() -> list[str]:
    """Every reason a cell may not run. Read before any database is opened."""
    doc = block.record()
    found: list[str] = []
    if doc.get("status") != "FROZEN, NOT RUN":
        found.append("the block is %r, not FROZEN, NOT RUN" % doc.get("status"))
    auth = doc.get("authorisation") or {}
    if auth.get("granted") is not True:
        found.append("the dated grant is not recorded")
    if not auth.get("granted_on"):
        found.append("the grant has no date")
    else:
        try:
            date.fromisoformat(str(auth["granted_on"]))
        except ValueError:
            found.append("the grant date is not ISO YYYY-MM-DD")
    if not auth.get("document"):
        found.append("the grant names no document")
    if not auth.get("quote"):
        found.append("the grant records no quote")
    if getattr(__import__("organica"), "__version__", None) != "0.15.0":
        found.append("the shipped build is not 0.15.0")
    if SleepService.MAX_PREDICTIONS != 112:
        found.append("the shipped cap is not 112")
    runner = doc.get("runner") or {}
    if runner.get("built") is not True:
        found.append("the record does not mark the runner built")
    if runner.get("planned_module") != MODULE:
        found.append("the record names a different runner module")
    return found


def refuse() -> None:
    reasons = preflight()
    if reasons:
        print("REFUSED: PRESENCE-CAP-LADDER-1 will not run:", file=sys.stderr)
        for reason in reasons:
            print("  -", reason, file=sys.stderr)
        raise SystemExit(2)


def part_path(seed: int, cap: int) -> Path:
    return PARTS / ("%d-%d.json" % (seed, cap))


def run_cell(seed: int, cap: int) -> dict:
    """Run one cap-ladder cell on a fresh scratch database and return its part."""
    if (seed, cap) not in planned():
        raise SystemExit("REFUSED: (%d, %d) is not one of the 24 planned cells"
                         % (seed, cap))
    cycles = int(block.record()["design"]["cycles"])
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("presence_cap_ladder_%d_%d" % (seed, cap))
    mem = _CountingMemoryService(str(db_path))
    svc = observer.RepairedObserverSleepService(mem, observe=True, cap=cap)
    windows: list[list[tuple[str, str]]] = []
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, train_flag) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not train_flag:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            mem.store(text, event_type="observe",
                      source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                windows.append([(p.source, p.target)
                                for p in svc.run_sleep_cycle().predictions])
        asserted = {(a, b) for a, targets in
                    structure_edges(svc._load_prior_candidates()).items()
                    for b in targets}
        rows = {(a, b) for a, b in
                mem._conn.execute("SELECT tag_from, tag_to FROM precedes").fetchall()}
        store_counts = dict(getattr(mem, "store_counts", {}))
        universe = [list(cycle) for cycle in getattr(svc, "universe", [])]
        allocation = [dict(row) for row in getattr(svc, "allocation", [])]
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass
    present = world_edges & rows
    cell = {
        "kind": "presence_cap_ladder_cell",
        "prereg": block.ID,
        "seed": int(seed),
        "cap": int(cap),
        "cycles": len(windows),
        "engine_version": engine_stamp.engine_version(),
        "engine_sha256": engine_stamp.engine_sha256(),
        "world_digest": _digest(world_edges),
        "present_fingerprint": _digest(present),
        "world_edges": len(world_edges),
        "present_world_edges": len(present),
        "windows": [[list(edge) for edge in window] for window in windows],
        "windows_world": [["%s>%s" % edge for edge in window if edge in world_edges]
                          for window in windows],
        "present_edges": sorted([list(edge) for edge in present]),
        "asserted_edges": sorted([list(edge) for edge in asserted & world_edges]),
        "asserted_fingerprint": asserted_fingerprint(asserted),
        "universe": universe,
        "allocation": allocation,
        "store_counts": store_counts,
    }
    return engine_stamp.stamp(cell)


def cell(seed: int, cap: int, force: bool = False) -> int:
    refuse()
    if (seed, cap) not in planned():
        print("REFUSED: (%d, %d) is not one of the 24 planned cells" % (seed, cap),
              file=sys.stderr)
        return 2
    path = part_path(seed, cap)
    if path.exists() and not force:
        print("REFUSED: %s already exists; use --force to rerun this cell" % path,
              file=sys.stderr)
        return 2
    part = run_cell(seed, cap)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(part), encoding="utf-8")
    print("wrote %s" % path)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the 24 cell commands without opening a database")
    parser.add_argument("--cell", nargs=2, metavar=("SEED", "CAP"), type=int,
                        help="run one planned cell after the dated grant")
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing cell part")
    args = parser.parse_args(argv)
    if args.dry_run:
        return dry_run()
    if args.cell:
        return cell(args.cell[0], args.cell[1], force=args.force)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
