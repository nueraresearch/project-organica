"""A1 two-path dry-run manifest and fail-closed grant gate.

The manifest fixes the planned cells, candidate seed block, cycles, cap and object
fingerprint for the A-/K-/Y- design. The treatments are implemented in
``benchmarks.a1_arms``, but every executing path calls ``refuse()`` before a
database is opened; the current manifest has no target edges, no freeze and no grant.

    python -m benchmarks.a1_two_path --dry-run
    python -m benchmarks.a1_two_path --write
    python -m benchmarks.a1_two_path --check
    python -m benchmarks.a1_two_path --self-test
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date
from functools import lru_cache
from pathlib import Path

from benchmarks import authorisation_guard
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MANIFEST_PATH = DOCS / "a1_two_path_manifest.json"
PAGE_PATH = DOCS / "A1-TWO-PATH-MANIFEST.md"
MODULE = "benchmarks.a1_two_path"
ID = "A1-TWO-PATH-1"
DATE = "2026-11-14"

SEEDS = (20630101, 20630102, 20630103, 20630104, 20630105, 20630106)
CELLS = (
    {"id": "A+K+", "admission": "allowed", "carrier": "available", "assertion": "on"},
    {"id": "A+K-", "admission": "allowed", "carrier": "blocked", "assertion": "on"},
    {"id": "A-K+", "admission": "blocked", "carrier": "available", "assertion": "on"},
    {"id": "A-K-", "admission": "blocked", "carrier": "blocked", "assertion": "on"},
    {"id": "Y_MINUS_A+K+", "admission": "allowed", "carrier": "available", "assertion": "blocked"},
    {"id": "Y_MINUS_A-K+", "admission": "blocked", "carrier": "available", "assertion": "blocked"},
)
CYCLES = 120
CAP = 40
WORLD = "compositional world family"
UNIVERSE = "fixed compositional-world directed-edge universe"
CONTROL = {"seed": SEEDS[0], "cell": "A+K+", "why": "fresh-process determinism rerun"}
EXPECTED_CELLS = {cell["id"] for cell in CELLS}
PLANNED = {(seed, cell["id"]) for seed in SEEDS for cell in CELLS}
TARGET_N = 4
TARGET_PROTOCOL = "docs/A1-TARGET-SELECTION-PROTOCOL.md"
TARGET_SELECTION_PATH = DOCS / "a1_target_selection.json"


def manifest() -> dict:
    return {
        "kind": "a1_two_path_manifest",
        "id": ID,
        "date": DATE,
        "status": "REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT",
        "frozen": False,
        "design": "docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md",
        "thresholds": "docs/A1-PRECOMMITTED-THRESHOLDS.md",
        "engine": "0.15.0",
        "seed_block": {
            "status": "PROVISIONAL CANDIDATE — NOT RESERVED, NOT FROZEN",
            "seeds": list(SEEDS),
            "cycles": CYCLES,
            "cap": CAP,
            "freshness": "seed_collisions over docs JSON is empty at manifest time",
        },
        "world": WORLD,
        "candidate_universe": UNIVERSE,
        "cells": list(CELLS),
        "cell_count": len(SEEDS) * len(CELLS),
        "planned_cells": len(PLANNED),
        "control": CONTROL,
        "object_fingerprint": {
            "fields": ["world", "seed", "cycles", "cap", "candidate_universe", "U"],
            "rule": "every cell of a seed must carry one fingerprint",
        },
        "targets": {
            "status": "UNRESOLVED — MUST BE FIXED BEFORE FREEZE",
            "protocol": TARGET_PROTOCOL,
            "n_per_seed": TARGET_N,
            "selection_artifact": TARGET_SELECTION_PATH.relative_to(ROOT).as_posix(),
            "by_seed": {},
            "u_cycle": 36,
            "rule": (
                "Directed world edges fixed per seed before any cell; one target set "
                "is applied in every cell of that seed; no post-outcome target selection. "
                "U is measured at cycle 36, before the earliest A0 carrier formation at cycle 37."
            ),
        },
        "U": {
            "direct_count": "pre-carrier",
            "reverse_count": "pre-carrier",
            "strength": "pre-carrier",
            "measured_cycle": 36,
            "measured_before": ["carrier", "K", "Y"],
        },
        "authorisation": {
            "granted": False,
            "granted_on": None,
            "document": None,
            "quote": None,
        },
        "runner": {
            "built": True,
            "planned_module": MODULE,
            "note": "A-/K-/Y- treatments built; execution still requires frozen targets and a grant",
        },
        "result": {"path": "docs/a1_two_path_result.json", "exists": False},
        "not_evidence": (
            "A dry-run manifest and grant gate. No cell, seed or database is used; "
            "this is not a result and does not authorise a run."
        ),
    }


def manifest_problems(doc: dict | None = None) -> list[str]:
    doc = manifest() if doc is None else doc
    found: list[str] = []
    if doc.get("kind") != "a1_two_path_manifest":
        found.append("manifest kind")
    if doc.get("id") != ID:
        found.append("manifest id")
    seeds = doc.get("seed_block", {}).get("seeds") or []
    if len(seeds) != 6 or len(set(seeds)) != 6:
        found.append("the seed block is not six unique seeds")
    if doc.get("seed_block", {}).get("cycles") != CYCLES:
        found.append("cycles are not %d" % CYCLES)
    if doc.get("seed_block", {}).get("cap") != CAP:
        found.append("cap is not %d" % CAP)
    cells = doc.get("cells") or []
    ids = [cell.get("id") for cell in cells]
    if len(ids) != 6 or len(set(ids)) != 6 or set(ids) != EXPECTED_CELLS:
        found.append("the cell set is not the six planned cells")
    if sum(1 for cell in cells if cell.get("assertion") == "blocked") != 2:
        found.append("Y- is not present at exactly two cells")
    if doc.get("cell_count") != len(seeds) * 6:
        found.append("cell_count does not match seeds x cells")
    if doc.get("planned_cells") != len(seeds) * 6:
        found.append("planned_cells does not match seeds x cells")
    if doc.get("control", {}).get("seed") not in seeds:
        found.append("the control seed is not in the block")
    if doc.get("control", {}).get("cell") not in EXPECTED_CELLS:
        found.append("the control cell is not planned")
    fields = set(doc.get("object_fingerprint", {}).get("fields") or [])
    if fields != {"world", "seed", "cycles", "cap", "candidate_universe", "U"}:
        found.append("the object fingerprint is incomplete")
    if set(doc.get("U", {}).get("measured_before") or []) != {"carrier", "K", "Y"}:
        found.append("U is not fixed before carrier, K and Y")
    if not isinstance(doc.get("frozen"), bool):
        found.append("the freeze flag is not recorded")
    targets = doc.get("targets") or {}
    if not isinstance(targets.get("by_seed"), dict):
        found.append("the target block is not a per-seed mapping")
    u_cycle = targets.get("u_cycle")
    cycle_limit = (doc.get("seed_block") or {}).get("cycles")
    if (not isinstance(u_cycle, int) or not isinstance(cycle_limit, int)
            or not 1 <= u_cycle <= cycle_limit):
        found.append("the U cycle is not an integer in the run")
    if (doc.get("runner") or {}).get("planned_module") != MODULE:
        found.append("the runner module does not match")
    return found


def command(seed: int, cell: str, control: bool = False) -> str:
    suffix = " --control" if control else ""
    return "python -m %s --cell %s --seed %d%s" % (MODULE, cell, seed, suffix)


def is_planned(seed: int, cell: str, control: bool = False) -> bool:
    if control:
        return seed == CONTROL["seed"] and cell == CONTROL["cell"]
    return (seed, cell) in PLANNED


@lru_cache(maxsize=None)
def _seed_universe(seed: int) -> set[tuple[str, str]]:
    """The full 120-cycle world universe; engine-free and cached for preflight."""
    from benchmarks.acquisition_compositional import generate_compositional_world
    from benchmarks.acquisition_runner import _world_compositional_edges
    return _world_compositional_edges(generate_compositional_world(seed=seed, cycles=CYCLES))


def _artifact_targets(seed: int) -> list[str]:
    """The selected target strings recorded for a seed, or an empty list."""
    if not TARGET_SELECTION_PATH.exists():
        return []
    doc = json.loads(TARGET_SELECTION_PATH.read_text(encoding="utf-8"))
    row = (doc.get("per_seed") or {}).get(str(seed)) or {}
    return list(row.get("selected") or [])


def target_set_problems(doc: dict) -> list[str]:
    """Validate the fixed target sets before a freeze can be accepted."""
    found: list[str] = []
    targets = doc.get("targets") or {}
    by_seed = targets.get("by_seed") or {}
    if targets.get("protocol") != TARGET_PROTOCOL:
        found.append("the target protocol is not recorded")
    if targets.get("n_per_seed") != TARGET_N:
        found.append("the target-set size is not %d" % TARGET_N)
    expected = {str(seed) for seed in SEEDS}
    if set(by_seed) != expected:
        found.append("the target sets do not cover exactly the six seeds")
    for seed in SEEDS:
        raw = by_seed.get(str(seed), by_seed.get(seed))
        if not isinstance(raw, list) or len(raw) != TARGET_N:
            found.append("seed %d does not have %d targets" % (seed, TARGET_N))
            continue
        parsed: list[tuple[str, str]] = []
        for value in raw:
            if not isinstance(value, str) or value.count(">") != 1:
                found.append("seed %d has an invalid target edge" % seed)
                continue
            a, b = value.split(">", 1)
            if not a or not b or a == b:
                found.append("seed %d has an empty or self target edge" % seed)
                continue
            parsed.append((a, b))
        if len(parsed) != TARGET_N:
            continue
        used: set[str] = set()
        for a, b in parsed:
            if a in used or b in used:
                found.append("seed %d targets do not have disjoint endpoints" % seed)
            used.update((a, b))
        unknown = set(parsed) - _seed_universe(seed)
        if unknown:
            found.append("seed %d targets are outside the world universe" % seed)

    artifact = targets.get("selection_artifact")
    if not artifact or not (ROOT / str(artifact)).exists():
        found.append("the target selection artifact is missing")
        return found
    try:
        selection_doc = json.loads((ROOT / str(artifact)).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        found.append("the target selection artifact is unreadable: %s" % exc)
        return found
    from benchmarks import a1_target_selection as selection
    found.extend("selection: %s" % problem for problem in selection.problems(selection_doc))
    for seed in SEEDS:
        row = (selection_doc.get("per_seed") or {}).get(str(seed)) or {}
        if row.get("selected") != by_seed.get(str(seed), by_seed.get(seed)):
            found.append("seed %d targets do not match the selection artifact" % seed)
    return found


def _grant_problems(doc: dict) -> list[str]:
    found: list[str] = []
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
    elif not (ROOT / str(auth["document"])).exists():
        found.append("the grant document does not exist")
    if not auth.get("quote"):
        found.append("the grant records no quote")
    elif authorisation_guard.preparation_only(auth["quote"]):
        found.append("the grant quote is preparation-only, not a run authorisation")
    elif not authorisation_guard.RUN_MARKER.search(str(auth["quote"])):
        found.append("the grant quote does not authorise a run")
    return found


def preflight(doc: dict | None = None) -> list[str]:
    doc = manifest() if doc is None else doc
    found = manifest_problems(doc)
    found.extend(_grant_problems(doc))
    if doc.get("frozen") is not True:
        found.append("the manifest is not frozen")
    if doc.get("status") not in ("FROZEN, NOT RUN", "GRANTED, NOT RUN"):
        found.append("the manifest is %r, not frozen or granted" % doc.get("status"))
    try:
        import organica
        if getattr(organica, "__version__", None) != doc.get("engine"):
            found.append("the shipped build is not %s" % doc.get("engine"))
    except Exception as exc:  # pragma: no cover - import failure is a refusal reason
        found.append("the engine version could not be read: %s" % exc)
    runner = doc.get("runner") or {}
    if runner.get("built") is not True:
        found.append("the A-/K-/Y- arms are not implemented")
    targets = doc.get("targets") or {}
    by_seed = targets.get("by_seed") or {}
    if not by_seed:
        found.append("the target edge(s) are not fixed")
    if str(targets.get("status", "")).upper().startswith("UNRESOLVED"):
        found.append("the target edges are still marked unresolved")
    for seed, edges in by_seed.items():
        try:
            int(seed)
        except (TypeError, ValueError):
            found.append("a target key is not a seed: %r" % (seed,))
            continue
        if not isinstance(edges, list) or not edges:
            found.append("seed %s has no target edge" % seed)
    if by_seed and not str(targets.get("status", "")).upper().startswith("UNRESOLVED"):
        found.extend(target_set_problems(doc))
    result = doc.get("result") or {}
    if result.get("path") and (ROOT / str(result["path"])).exists():
        found.append("the manifest already names a result")
    try:
        from benchmarks.presence_cap_experiment import seed_collisions
        allow = (MANIFEST_PATH, TARGET_SELECTION_PATH)
        collisions = seed_collisions(list(doc.get("seed_block", {}).get("seeds") or []),
                                     allow=allow)
        if collisions:
            found.append("candidate seeds collide with committed artifacts: %r" % collisions)
    except Exception as exc:  # pragma: no cover - a failed scan is a refusal reason
        found.append("the seed-freshness scan failed: %s" % exc)
    return found


def refuse() -> None:
    reasons = preflight()
    if reasons:
        print("REFUSED: %s will not open a database:" % ID, file=sys.stderr)
        for reason in reasons:
            print("  -", reason, file=sys.stderr)
        raise SystemExit(2)


def dry_run() -> int:
    """Print the 37 planned commands. This path never opens a database."""
    for seed in SEEDS:
        for cell in CELLS:
            print(command(seed, cell["id"]))
    print(command(CONTROL["seed"], CONTROL["cell"], control=True))
    print("36 cells + 1 determinism control; no grant, no fixed targets, no database.",
          file=sys.stderr)
    return 0


def cell(seed: int, cell_id: str, control: bool = False) -> int:
    if not is_planned(seed, cell_id, control):
        print("REFUSED: (%d, %s, control=%s) is not planned"
              % (seed, cell_id, control), file=sys.stderr)
        return 2
    refuse()
    from benchmarks import a1_arms
    return a1_arms.run_cell(seed, cell_id, control=control)


def measure() -> int:
    refuse()
    from benchmarks import a1_arms
    return a1_arms.run_all()


def render(doc: dict) -> str:
    lines = [
        "# A1 two-path dry-run manifest",
        "",
        "**ID:** `%s`  " % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an experimental result. No cell, seed or database is used.**",
        "",
        "The manifest fixes the six cells and the candidate seed block for the A−, K− and Y− arms.",
        "The treatments are implemented; it does not authorise a run.",
        "",
        "## Object",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| World | %s |" % doc["world"],
        "| Candidate universe | %s |" % doc["candidate_universe"],
        "| Seeds | %s |" % ", ".join(str(seed) for seed in doc["seed_block"]["seeds"]),
        "| Cycles | %d |" % doc["seed_block"]["cycles"],
        "| Cap | %d |" % doc["seed_block"]["cap"],
        "| Frozen | %s |" % ("yes" if doc["frozen"] else "no"),
        "| U cycle | %d |" % doc["targets"]["u_cycle"],
        "| Target edges | %s |" % doc["targets"]["status"],
        "| Cells | %d |" % doc["cell_count"],
        "| Determinism control | seed %d, `%s` |" % (
            doc["control"]["seed"], doc["control"]["cell"]),
        "",
        "The seeds are **provisional candidates**, not reserved or frozen. `U` is fixed before",
        "carrier, K and Y, and every cell of a seed must carry one object fingerprint. The target",
        "edges are **unresolved** and must be fixed before freeze: `%s`." % doc["targets"]["status"],
        "",
        "## Cells",
        "",
        "| Cell | Admission | Carrier | Assertion |",
        "| --- | --- | --- | --- |",
    ]
    for cell_doc in doc["cells"]:
        lines.append("| `%s` | %s | %s | %s |" % (
            cell_doc["id"], cell_doc["admission"], cell_doc["carrier"],
            cell_doc["assertion"]))
    lines += [
        "",
        "## Gate",
        "",
        "Every executing path calls `refuse()` before a database is opened. The gate checks the",
        "frozen flag, a dated run-authorising grant, the shipped engine, the built arms, the",
        "planned cell set, the fixed target set, the object fields and seed freshness.",
        "",
        "A grant must be recorded in this manifest as `authorisation.granted: true`, with",
        "`granted_on`, an existing `document`, and a run-authorising `quote`. A preparation-only",
        "quote fails. The manifest is currently `%s` and its target edges are `%s`, so the gate"
        % (doc["status"], doc["targets"]["status"]),
        "refuses every cell. The A-/K-/Y- treatments are implemented; only the gate is closed.",
        "",
        "## Commands",
        "",
        "```bash",
        "python -m benchmarks.a1_two_path --dry-run",
        "python -m benchmarks.a1_two_path --check",
        "python -m benchmarks.a1_two_path --self-test",
        "python -m benchmarks.a1_two_path --cell A+K+ --seed 20630101",
        "python -m benchmarks.a1_two_path --measure",
        "```",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def check() -> int:
    doc = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) if MANIFEST_PATH.exists() else None
    if doc is None:
        print("FAIL: the manifest is missing")
        return 1
    if doc != manifest():
        print("FAIL: %s is stale" % MANIFEST_PATH)
        return 1
    if not PAGE_PATH.exists():
        print("FAIL: %s is missing" % PAGE_PATH)
        return 1
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        print("FAIL: %s is stale" % PAGE_PATH)
        return 1
    found = manifest_problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 two-path manifest: clean; %d cells + 1 control; gate refuses (no grant, not frozen, targets unresolved)"
          % doc["cell_count"])
    for reason in preflight(doc):
        print("  -", reason)
    return 0


def self_test() -> list[str]:
    found: list[str] = []
    base = manifest()
    if manifest_problems(base):
        found.append("the committed manifest fails its own invariants")
    if not any("grant" in reason for reason in preflight(base)):
        found.append("a missing grant is not a refusal reason")
    duplicate = copy.deepcopy(base)
    duplicate["cells"][1]["id"] = duplicate["cells"][0]["id"]
    if not manifest_problems(duplicate):
        found.append("a duplicate cell is accepted")
    missing_y = copy.deepcopy(base)
    missing_y["cells"] = [cell for cell in missing_y["cells"]
                          if cell["id"] != "Y_MINUS_A-K+"]
    if not manifest_problems(missing_y):
        found.append("a missing Y- cell is accepted")
    missing_field = copy.deepcopy(base)
    missing_field["object_fingerprint"]["fields"] = ["world", "seed"]
    if not manifest_problems(missing_field):
        found.append("an incomplete object fingerprint is accepted")
    bad_grant = copy.deepcopy(base)
    bad_grant["authorisation"] = {
        "granted": True, "granted_on": "2026-11-14",
        "document": "docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md",
        "quote": "Write the dated authorisation document without running a cell.",
    }
    if not any("preparation-only" in reason for reason in preflight(bad_grant)):
        found.append("a preparation-only grant quote is accepted")
    no_run = copy.deepcopy(base)
    no_run["authorisation"] = {
        "granted": True, "granted_on": "2026-11-14",
        "document": "docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md",
        "quote": "Approved.",
    }
    if not any("does not authorise a run" in reason for reason in preflight(no_run)):
        found.append("a non-run grant quote is accepted")
    good_grant = copy.deepcopy(base)
    good_grant["status"] = "GRANTED, NOT RUN"
    good_grant["frozen"] = True
    good_grant["runner"]["built"] = True
    good_grant["targets"]["status"] = "FIXED BEFORE FREEZE"
    good_grant["targets"]["by_seed"] = {str(seed): _artifact_targets(seed) for seed in SEEDS}
    good_grant["authorisation"] = {
        "granted": True, "granted_on": "2026-11-14",
        "document": "docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md",
        "quote": "Approve and run the A1 two-path cells.",
    }
    # The manifest file itself is the only allowed seed source; its candidate seeds are fresh.
    reasons = preflight(good_grant)
    if reasons:
        found.append("a complete run grant is rejected: %r" % reasons)
    not_frozen = copy.deepcopy(good_grant)
    not_frozen["frozen"] = False
    if not any("not frozen" in reason for reason in preflight(not_frozen)):
        found.append("a grant without a frozen manifest is accepted")
    unfixed = copy.deepcopy(good_grant)
    unfixed["targets"]["by_seed"] = {}
    if not any("target edge(s) are not fixed" in reason for reason in preflight(unfixed)):
        found.append("a frozen grant without target edges is accepted")
    if not is_planned(SEEDS[0], "A+K+") or is_planned(99999999, "A+K+"):
        found.append("the planned-cell predicate is wrong")
    from benchmarks import a1_arms
    found.extend("arms: %s" % problem for problem in a1_arms.self_test())
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--cell", metavar="CELL")
    group.add_argument("--measure", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args(argv)
    if args.dry_run:
        return dry_run()
    if args.cell is not None:
        if args.seed is None:
            parser.error("--cell requires --seed")
        return cell(args.seed, args.cell, control=args.control)
    if args.measure:
        return measure()
    if args.write:
        MANIFEST_PATH.write_text(json.dumps(manifest(), indent=2) + "\n", encoding="utf-8")
        PAGE_PATH.write_text(render(manifest()), encoding="utf-8")
        print("wrote %s and %s" % (MANIFEST_PATH, PAGE_PATH))
        return 0
    if args.self_test:
        found = self_test()
        for problem in found:
            print("FAIL:", problem)
        if not found:
            print("A1 two-path manifest: self-test clean")
        return 1 if found else 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
