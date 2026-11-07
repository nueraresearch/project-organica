"""The density interaction's runner: engine pools per (seed, density, scheme), both arms.

This module owns execution, not verdict. It builds one pool per cell with the frozen
engine, ranks it both ways at the registered caps, and writes the cells and recovery rows
`benchmarks/score_density_interaction.py` scores. The criteria live in the registration.

    ./.venv/bin/python -m benchmarks.run_density_interaction --self-test   # no engine
    ./.venv/bin/python -m benchmarks.run_density_interaction --plan
    ./.venv/bin/python -m benchmarks.run_density_interaction --run

The block is 160 engine pools for A2 (80 for A1), which is more than one sitting on a small
machine, so the runner can be sliced and the slices appended:

    ./.venv/bin/python -m benchmarks.run_density_interaction --run --scheme primary --seeds 0-3
    ./.venv/bin/python -m benchmarks.run_density_interaction --run --scheme primary --seeds 4-7 --append

`--append` merges into the existing artifact and refuses to overwrite a cell, so a cell
can never be silently re-run or dropped. `--force` is for a deliberate fresh block.

The engine is used, never edited: every database is a scratch database, and the live one is
refused before anything is opened. A registration that a review has placed on hold refuses
to run, so a hold cannot be defeated by forgetting it.

"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from benchmarks.density_worlds import (CAPS, EVENTS_PER_CYCLE, PRIMARY_CAP, RANKERS,
                                       TOTAL_EVENTS, designed_pool, identity_cell,
                                       is_intra_cell, leverage_audit, measure, stream,
                                       universe_size, world_edges)

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "density_interaction_prereg.json"
OUT = ROOT / "docs" / "density_interaction_run.json"

FROZEN = ("organica/sleep.py", "organica/memory.py", "organica/paths.py",
          "organica/streams.py", "organica/branch_streams.py",
          "organica/scale_streams.py", "organica/ground_truth_worlds.py")

#: The recovery caps are a characterization of the budget curve, never a criterion.
RECOVERY_CAPS = (80, 160, 240)


def prereg(path: Path = PREREG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# The grid
# ---------------------------------------------------------------------------

def plan(record: dict | None = None) -> list[dict]:
    record = record or prereg()
    design = record["design"]
    cells = [{"seed": int(seed), "rho_world": float(rho), "scheme": scheme,
              "arm": arm, "cap": int(cap)}
             for seed in design["seeds"] for rho in design["densities"]
             for scheme in design["schemes"] for cap in design["caps"]
             for arm in design["arms"]]
    if len(cells) != design["cells"] + design["sensitivity_cells"]:
        raise SystemExit("the plan has %d cells; the registration has %d + %d"
                         % (len(cells), design["cells"], design["sensitivity_cells"]))
    return cells


def assert_grid(record: dict) -> None:
    """Refuse anything that is not the frozen grid, before an engine is touched."""
    head = record["status"].split("(")[0].split(",")[0].strip()
    if head not in ("FROZEN", "HELD", "RUN"):
        raise SystemExit("the registration is not frozen, held or run; no cell may run")
    design = record["design"]
    seeds = [int(seed) for seed in design["seeds"]]
    if len(seeds) < 8 or len(set(seeds)) != len(seeds):
        raise SystemExit("the grid carries %d seeds; a block needs at least eight distinct "
                         "seeds" % len(seeds))
    if seeds != list(range(seeds[0], seeds[0] + len(seeds))):
        raise SystemExit("the seed block is not contiguous")
    if design["schemes"] != ["primary", "sensitivity"]:
        raise SystemExit("both exposure schemes must be registered")
    if design["arms"] != ["control", "intra_cell_excluded"]:
        raise SystemExit("the arms are not the registered pair")
    if design["primary_cap"] != PRIMARY_CAP:
        raise SystemExit("the primary cap is not the frozen cap")
    for rho in design["densities"]:
        if not 0.0 < float(rho) <= 0.8:
            raise SystemExit("density outside (0, 0.8]: %r" % (rho,))
    if round(max(design["densities"]) * universe_size()) != len(world_edges(seeds[0], 0.8)):
        raise SystemExit("the top density is not the full cross-cell universe")


# ---------------------------------------------------------------------------
# The engine pool
# ---------------------------------------------------------------------------

def run_pool(seed: int, rho: float, scheme: str,
             filler: str = "proportional") -> dict:
    """Ingest one world with the frozen engine and return the pool a ranker sees.

    The pool is the `precedes` table: the rows the engine can select from at the end of
    the run. The ingest loop stores the event, runs a sleep cycle every
    `EVENTS_PER_CYCLE` events, and then reads the table. The database is a scratch
    database and the live one is refused before anything is opened.
    """
    from organica.memory import MemoryService
    from organica.paths import LIVE_DB, temp_db
    from organica.sleep import SleepService

    db_path = temp_db("density_%d_%d_%s_%s" % (seed, round(rho * 100), scheme, filler))
    if db_path.resolve() == LIVE_DB.resolve():
        raise SystemExit("refusing to open the live database")

    events = stream(seed, rho, scheme, filler)
    mem = MemoryService(str(db_path))
    try:
        service = SleepService(mem)
        for index, text in enumerate(events, start=1):
            mem.store(text, event_type="observe", source="env")
            if index % EVENTS_PER_CYCLE == 0:
                service.run_sleep_cycle()
        rows = mem._conn.execute(
            "SELECT tag_from, tag_to, count FROM precedes ORDER BY tag_from, tag_to"
        ).fetchall()
        return {
            "seed": seed, "rho_world": float(rho), "scheme": scheme,
            "events": len(events),
            "cycles": len(events) // EVENTS_PER_CYCLE,
            "pool": [(str(a), str(b), int(c)) for a, b, c in rows],
        }
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass


def cells_for(seed: int, rho: float, scheme: str, pool, record: dict | None = None) -> dict:
    """Both arms at both caps for one pool, plus the recovery rows at the higher caps.

    The pool is shared, so every cell is paired against its counterpart by construction.
    """
    record = record or prereg()
    world = world_edges(seed, rho)
    cells, recovery = [], []
    for cap in record["design"]["caps"]:
        for arm in record["design"]["arms"]:
            selected = RANKERS[arm](pool, int(cap))
            stats = measure(pool, world, selected)
            row = {
                "seed": seed, "rho_world": float(rho), "scheme": scheme, "arm": arm,
                "cap": int(cap), "coverage": stats["coverage"],
                "precision": stats["precision"], "covered": stats["covered"],
                "asserted": stats["asserted"], "presence": stats["presence"],
                "rho_rank": stats["rho_rank"], "pool_rows": stats["pool_rows"],
                "pool_intra_cell_rows": stats["pool_intra_cell_rows"],
                "intra_cell_share": stats["intra_cell_share"],
                "selected": ["%s>%s" % edge for edge in selected],
            }
            cells.append(row)
    for cap in RECOVERY_CAPS:
        for arm in record["design"]["arms"]:
            selected = RANKERS[arm](pool, cap)
            stats = measure(pool, world, selected)
            recovery.append({"seed": seed, "rho_world": float(rho), "scheme": scheme,
                             "arm": arm, "cap": int(cap),
                             "coverage": stats["coverage"],
                             "precision": stats["precision"]})
    return {"cells": cells, "recovery": recovery}


# ---------------------------------------------------------------------------
# Harness audits: no engine, no judged cell
# ---------------------------------------------------------------------------

def generator_audit(record: dict | None = None) -> dict:
    """Every registered cell's world and stream must be what the registration says."""
    record = record or prereg()
    filler = record["design"].get("filler", "proportional")
    problems, checked = [], 0
    for seed in record["design"]["seeds"]:
        for rho in record["design"]["densities"]:
            world = world_edges(seed, rho)
            expected = round(float(rho) * universe_size())
            if len(world) != expected:
                problems.append("%d/%s: %d edges, expected %d"
                                % (seed, rho, len(world), expected))
            if any(a == b for a, b in world):
                problems.append("%d/%s: a self pair" % (seed, rho))
            if any(is_intra_cell(a, b) for a, b in world):
                problems.append("%d/%s: an intra-cell row is a world edge" % (seed, rho))
            primary = stream(seed, rho, "primary", filler)
            sensitivity = stream(seed, rho, "sensitivity", filler)
            if len(primary) != TOTAL_EVENTS:
                problems.append("%d/%s: primary exposure is %d events, not the declared %d"
                                % (seed, rho, len(primary), TOTAL_EVENTS))
            if len(sensitivity) != len(stream(seed, rho, "sensitivity", filler)):
                problems.append("%d/%s: the sensitivity stream is not deterministic"
                                % (seed, rho))
            emitted = set()
            for text in sensitivity:
                tags = text.split()
                for a in tags:
                    for b in tags:
                        if a != b:
                            emitted.add((a, b))
            missing = [edge for edge in world if edge not in emitted]
            if missing:
                problems.append("%d/%s: %d world edges never emitted"
                                % (seed, rho, len(missing)))
            pool = designed_pool(seed, rho, filler)
            stats = measure(pool, world, [])
            if not stats["pool_intra_cell_rows"]:
                problems.append("%d/%s: no intra-cell rows, so the treatment is a no-op"
                                % (seed, rho))
            if stats["presence"] != 1.0:
                problems.append("%d/%s: presence %r, not 1.0"
                                % (seed, rho, stats["presence"]))
            checked += 1
    return {"passed": not problems, "cells_checked": checked, "problems": problems[:8]}


def liveness_audit() -> dict:
    """The arms must differ, and neither may be empty, on a pool the world could build.

    The fixture carries both row classes at comparable counts, so the treatment has a real
    row to promote. A fixture whose only rows were intra-cell would let an empty selection
    pass a difference check and prove nothing.
    """
    pool = [("amber", "birch", 9), ("amber", "cedar", 8),
            ("birch", "amber", 7), ("birch", "cedar", 3),
            ("amber", "indigo", 6), ("birch", "fern", 5),
            ("cedar", "willow", 4)]
    control = RANKERS["control"](pool, 4)
    treated = RANKERS["intra_cell_excluded"](pool, 4)
    return {"passed": bool(control) and bool(treated) and control != treated,
            "control": ["%s>%s" % edge for edge in control],
            "treated": ["%s>%s" % edge for edge in treated],
            "note": "amber/birch/cedar share one cell; indigo/fern/willow the next"}


def identity_audit(record: dict | None = None) -> dict:
    """G5: with every row a world edge and no intra-cell row, the arms must agree.

    This is the design record's `rho -> 1` condition. It cannot be a ladder cell, because
    this world's top density still holds intra-cell rows that are never world edges; it is
    a fixture, and a non-zero Delta here is a harness defect.
    """
    record = record or prereg()
    return identity_cell(int(record["design"]["seeds"][0]))


def freshness_audit(record: dict | None = None) -> dict:
    """The seed block must not appear in any file that predates this block."""
    record = record or prereg()
    seeds = {int(s) for s in record["design"]["seeds"]} | {int(record["seeds"]["bootstrap"])}
    # Both density blocks' own artifacts cite their seeds, so they are not collisions.
    recorded = {ROOT / "docs" / name for name in (
        "density_interaction_prereg.json", "density_interaction_run.json",
        "density_interaction_result.json", "DENSITY-INTERACTION-PREREGISTRATION.md",
        "density_interaction_a2_prereg.json", "density_interaction_a2_run.json",
        "density_interaction_a2_result.json",
        "DENSITY-INTERACTION-A2-PREREGISTRATION.md",
        "stage_b_protocol.json", "USER-MANUAL.md")}
    # A block that *declares* the A2 grid as inherited is a paired re-use, not a collision.
    # The exemption is conditional on that declaration, so a file cannot earn it by name.
    declared = ROOT / "docs" / "density_padding_prereg.json"
    if declared.exists():
        body = json.loads(declared.read_text(encoding="utf-8"))
        if body.get("amends") is None and "density_interaction_a2_prereg.json" in str(
                body.get("inherits")):
            recorded |= {ROOT / "docs" / name for name in (
                "density_padding_prereg.json", "density_padding_run.json",
                "density_padding_result.json", "DENSITY-PADDING-PREREGISTRATION.md")}
    hits = []
    for directory in ("docs", "tests", "benchmarks", "research-journal", "papers"):
        base = ROOT / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path in recorded:
                continue
            if path.suffix not in (".md", ".json", ".py", ".txt", ".jsonl", ".cff", ".svg"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            found = {int(m.group()) for m in re.finditer(r"\b\d{8}\b", text)} & seeds
            if found:
                hits.append({"path": str(path.relative_to(ROOT)), "seeds": sorted(found)})
    return {"passed": not hits, "collisions": hits[:5], "seeds": sorted(seeds)}


def boundary(record: dict | None = None) -> dict:
    diff = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *FROZEN],
                          cwd=str(ROOT), capture_output=True, text=True)
    status = subprocess.run(["git", "status", "--porcelain", "--", *FROZEN],
                            cwd=str(ROOT), capture_output=True, text=True)
    return {"frozen_files_clean": diff.returncode == 0 and not status.stdout.strip(),
            "checked": list(FROZEN)}


def self_test(record: dict | None = None) -> dict:
    record = record or prereg()
    try:
        assert_grid(record)
        planned = plan(record)
        design = record["design"]
        grid = {"passed": len(planned) == design["cells"] + design["sensitivity_cells"],
                "cells": len(planned)}
    except SystemExit as exc:                        # pragma: no cover - guard surface
        grid = {"passed": False, "problem": str(exc)}
    checks = {
        "grid": grid,
        "generator": generator_audit(record),
        "liveness": liveness_audit(),
        "identity": identity_audit(record),
        "freshness": freshness_audit(record),
    }
    gates = {"leverage": leverage_audit(record["design"]["seeds"],
                                        record["design"]["densities"],
                                        record["design"].get("filler", "proportional"))}
    ready = (all(c["passed"] for c in checks.values())
             and all(g["passed"] for g in gates.values()))
    return {"all_passed": ready, "checks": checks, "gates": gates}


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def _key(cell: dict) -> tuple:
    return (int(cell["seed"]), round(float(cell["rho_world"]), 6),
            cell["scheme"], cell["arm"], int(cell["cap"]))


def run(out: Path = OUT, record: dict | None = None, scheme: str | None = None,
        seeds: tuple[int, ...] | None = None, append: bool = False,
        force: bool = False) -> dict:
    record = record or prereg()
    if record["status"].startswith("HELD"):
        review = record.get("review", {}).get("review", "a pre-run review")
        raise SystemExit("the registration is held by %s; a held block may not run. "
                         "A2 must be registered on its own artifact" % review)
    assert_grid(record)
    report = self_test(record)
    if not report["all_passed"]:
        raise SystemExit("the harness self-tests failed; no cell may run: %r"
                         % {k: v for k, v in report["checks"].items() if not v["passed"]})

    schemes = [scheme] if scheme else list(record["design"]["schemes"])
    chosen = seeds or tuple(int(s) for s in record["design"]["seeds"])
    cells, recovery = [], []
    for seed in chosen:
        for rho in record["design"]["densities"]:
            for name in schemes:
                built = run_pool(int(seed), float(rho), name,
                                 record["design"].get("filler", "proportional"))
                produced = cells_for(int(seed), float(rho), name, built["pool"], record)
                cells.extend(produced["cells"])
                recovery.extend(produced["recovery"])

    if out.exists() and not force:
        previous = json.loads(out.read_text(encoding="utf-8"))
        if not append:
            raise SystemExit("%s exists; pass --append to add slices or --force to "
                             "replace the block" % out)
        seen = {_key(cell) for cell in previous["cells"]}
        repeated = [cell for cell in cells if _key(cell) in seen]
        if repeated:
            raise SystemExit("refusing to overwrite %d existing cells; a cell may not be "
                             "re-run inside one block" % len(repeated))
        cells = previous["cells"] + cells
        recovery = previous.get("recovery", []) + recovery

    payload = {
        "prereg": record["prereg"],
        "cells": cells,
        "recovery": recovery,
        "identity": identity_audit(record),
        "boundary": boundary(record),
        "provenance": {
            "runner": "benchmarks/run_density_interaction.py",
            "world": "benchmarks/density_worlds.py",
            "instrument": "the frozen engine's precedes table, ranked by the two arms",
            "engine_runs": 0,
            "slices": {"scheme": scheme, "seeds": list(chosen)},
            "events_per_cycle": EVENTS_PER_CYCLE,
            "primary_events": TOTAL_EVENTS,
            "recovery_caps": list(RECOVERY_CAPS),
            "cap_ladder": list(CAPS),
        },
    }
    out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print("wrote", out, "| cells:", len(cells), "| recovery:", len(recovery))
    return payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="audit the harness; no engine, no judged cell")
    parser.add_argument("--plan", action="store_true", help="print the 320 planned cells")
    parser.add_argument("--run", action="store_true", help="execute the block or a slice")
    parser.add_argument("--scheme", choices=["primary", "sensitivity"], default=None)
    parser.add_argument("--seeds", default=None,
                        help="slice, e.g. 0-3 (positions in the registered block) or "
                             "first-last seed")
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--prereg", default=str(PREREG),
                        help="which registration to run (A1 is held and refuses)")
    args = parser.parse_args(argv)

    record = prereg(Path(args.prereg))
    if args.run:
        chosen = None
        if args.seeds:
            first, _, last = args.seeds.partition("-")
            if int(first) < 1000:
                block = [int(s) for s in record["design"]["seeds"]]
                chosen = tuple(block[int(first):int(last or first) + 1])
            else:
                chosen = tuple(range(int(first), int(last or first) + 1))
        run(Path(args.out), record, scheme=args.scheme, seeds=chosen,
            append=args.append, force=args.force)
        return 0
    if args.plan:
        for cell in plan(record):
            print("%d  rho=%.1f  %-11s cap=%d  %s"
                  % (cell["seed"], cell["rho_world"], cell["scheme"], cell["cap"],
                     cell["arm"]))
        return 0
    report = self_test(record)
    print(json.dumps(report, indent=1))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
