"""Bounded canary cells for the frozen presence blocks.

One 120-cycle cell per frozen block, run inside the suite and reduced to a digest stored in
``docs/block_canaries.json``. A canary is not a result and licenses nothing: it exists so that a
change to the engine, a block's runner path, or the harness that feeds it turns the suite red
before anyone reads a stale verdict as current.

Three blocks have a runner and contribute a cell, using the first seed their own record names and
the shipped side of their design (cap 40, observer off). ``PRESENCE-CONVERSION-2`` has a built
observer but no cell entry point -- the instrument is not a runner -- so its canary asserts the
refusal: frozen, unrun, ungranted, no cell entry point, and ``runner_built`` as the fact it is.

No seed integer is written to the digest file. Stage B harvests every integer under a key naming
a seed, and a canary is not a consumed seed block, so the file records the cell's place in the
record (``first_cell``) rather than a seed value.

    python -m benchmarks.block_canaries --write    # record the digests
    python -m benchmarks.block_canaries --check    # compare, exit 1 on any change
    python -m benchmarks.block_canaries --cell PRESENCE-CAP-1
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path

from benchmarks import engine_lineage, engine_stamp

ROOT = Path(__file__).resolve().parent.parent
DIGESTS = ROOT / "docs" / "block_canaries.json"
PRE_REGS = ROOT / "docs"

CYCLES = 120

# Scalars compared when the cell is digested. Lists and profiles are skipped so the digest stays
# stable across a re-render that does not change behaviour. No key here may name a seed.
CANARY_KEYS = (
    "cap", "arm", "cycles", "cycles_run", "world_edges", "present_world_edges",
    "present_fingerprint", "s_ever_world_edges", "s_ever_fingerprint", "admitted_world_edges",
    "asserted_world_edges", "asserted_and_admitted", "asserted_without_admission",
    "asserted_fingerprint", "max_window", "median_window", "windows",
)
REQUIRED = ("present_fingerprint", "asserted_fingerprint")

CELLS = {
    "PRESENCE-CONSTRUCT-1": {
        "runner": "benchmarks.presence_construct_audit:run_cell",
        "extra": {},
    },
    "PRESENCE-CAP-1": {
        "runner": "benchmarks.presence_cap_experiment:run_cell",
        "extra": {"cap": 40},
    },
    "PRESENCE-CONVERSION-1": {
        "runner": "benchmarks.presence_conversion_observer:run_cell",
        "extra": {"arm": "off"},
    },
}
REFUSALS = {
    "PRESENCE-CONVERSION-2": ("the observer is built, but the block has no cell entry point, so the canary is the refusal itself"),
}

_CACHE: dict[str, dict] = {}


def record_paths() -> dict[str, Path]:
    """The frozen pre-registration that owns each canary."""
    found: dict[str, Path] = {}
    for path in sorted(PRE_REGS.glob("*prereg.json")):
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        identity = body.get("prereg")
        if identity in CELLS or identity in REFUSALS:
            found[identity] = path
    return found


def frozen_blocks() -> list[str]:
    return sorted(record_paths())


def spec(block: str) -> dict:
    """The runnable specification of one canary, taken from the block's own record."""
    paths = record_paths()
    if block not in paths:
        raise KeyError("no frozen record names %r" % (block,))
    body = json.loads(paths[block].read_text(encoding="utf-8"))
    design = body.get("design") or {}
    seeds = design.get("seeds") or []
    out = {
        "block": block,
        "record": paths[block].relative_to(ROOT).as_posix(),
        "status": body.get("status"),
        "cycles": CYCLES,
        "kind": "refusal" if block in REFUSALS else "cell",
    }
    if out["kind"] == "refusal":
        out["why"] = REFUSALS[block]
        out["runner_built"] = (body.get("runner") or {}).get("built")
        out["no_cells_run"] = body.get("no_cells_run")
        out["granted"] = (body.get("authorisation") or {}).get("granted")
        return out
    if not seeds:
        raise KeyError("%s: the record names no seed to canary" % block)
    entry = CELLS[block]
    out["runner"] = entry["runner"]
    out["first_cell"] = True
    out["kwargs"] = dict(entry["extra"], seed=seeds[0], cycles=CYCLES)
    return out


def _resolve(path: str):
    module_name, _, attr = path.partition(":")
    if not module_name or not attr:
        raise LookupError("not a module:attribute path: %r" % (path,))
    module = importlib.import_module(module_name)
    try:
        runner = getattr(module, attr)
    except AttributeError:
        raise LookupError("the runner path %r does not resolve: %s has no %r"
                          % (path, module_name, attr))
    if not callable(runner):
        raise LookupError("the runner path %r is not callable" % (path,))
    return runner


def payload(block: str, runner_override: str | None = None) -> dict:
    """The digestable record of one canary cell, or an error record that will not match."""
    if runner_override is None and block in _CACHE:
        return _CACHE[block]
    try:
        one = spec(block)
    except KeyError as exc:
        return {"block": block, "error": str(exc)}

    if one["kind"] == "refusal":
        result = {
            "block": block, "kind": "refusal", "status": one["status"],
            "runner_built": one["runner_built"], "no_cells_run": one["no_cells_run"],
            "granted": one["granted"], "cell_entry_points": _entry_points(block),
        }
    else:
        path = runner_override or one["runner"]
        result = _cell_payload(block, path, one)

    if runner_override is None:
        _CACHE[block] = result
    return result


def _cell_payload(block: str, path: str, one: dict) -> dict:
    try:
        runner = _resolve(path)
        cell = runner(**one["kwargs"])
    except (LookupError, ImportError, AttributeError) as exc:
        return {"block": block, "error": "runner unusable: %s" % exc}
    except Exception as exc:  # a broken runner must be reported, not swallowed
        return {"block": block, "error": "%s: %s" % (type(exc).__name__, exc)}
    missing = [key for key in REQUIRED if key not in cell]
    if missing:
        return {"block": block, "error": "the cell returned no %s" % ", ".join(missing)}
    fields = {key: cell[key] for key in CANARY_KEYS
              if key in cell and isinstance(cell[key], (int, float, str))
              and not isinstance(cell[key], bool)}
    return {"block": block, "kind": "cell", "runner": path, "cycles": one["cycles"],
            "first_cell": one["first_cell"], "fields": fields}


def _entry_points(block: str) -> list[str]:
    """Any cell entry point a refusal canary must not find, in the record or in the observer.

    The repaired observer is built and must stay an instrument: if it ever grows ``run_cell`` or
    ``measure`` it becomes a runner, the refusal canary's premise fails, and the digest moves.
    """
    modules = {
        "PRESENCE-CONVERSION-2": (
            "benchmarks.presence_conversion_repair",
            "benchmarks.presence_conversion_repair_observer",
        ),
    }[block]
    found = []
    for module_name in modules:
        module = importlib.import_module(module_name)
        short = module_name.rsplit(".", 1)[-1]
        found.extend("%s.%s" % (short, name) for name in ("run_cell", "measure")
                     if callable(getattr(module, name, None)))
    return sorted(found)


def digest(one: dict) -> str:
    canonical = json.dumps(one, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build() -> dict:
    cells = {}
    for block in frozen_blocks():
        one = payload(block)
        cells[block] = dict(one, digest=digest(one))
    doc = {
        "kind": "block_canaries",
        "cycles": CYCLES,
        "cells": cells,
        "engine_version": engine_stamp.engine_version(),
        "engine_commit": engine_stamp.pinned_commit(),
        "engine_sha256": engine_stamp.engine_sha256(),
        "runner": _runner_name(),
    }
    return doc


def _runner_name() -> str:
    try:
        return engine_stamp.runner()
    except Exception:
        return "__main__"


def load() -> dict:
    return json.loads(DIGESTS.read_text(encoding="utf-8"))


def check(only: str | None = None, runner_override: str | None = None,
          committed: dict | None = None) -> list[str]:
    """Problems with the recorded digests; empty means every canary is as recorded."""
    committed = committed or load()
    recorded = committed.get("cells") or {}
    problems: list[str] = []
    if committed.get("cycles") != CYCLES:
        problems.append("the digest file records %r cycles, not %d"
                        % (committed.get("cycles"), CYCLES))
    if not engine_lineage.same_build(committed.get("engine_sha256")):
        problems.append("the canaries were recorded on engine bytes that are neither the shipped "
                        "engine nor a recorded behaviour-identical successor "
                        "(docs/engine_lineage.json); re-record them with --write only after a "
                        "version bump and a re-pin")
    for block in frozen_blocks():
        if only and block != only:
            continue
        if block not in recorded:
            problems.append("%s: no digest recorded" % block)
            continue
        one = payload(block, runner_override=runner_override)
        current = digest(one)
        if one.get("error"):
            problems.append("%s: the canary cannot run: %s" % (block, one["error"]))
        elif current != recorded[block].get("digest"):
            problems.append("%s: the digest changed (recorded %s, now %s)"
                            % (block, recorded[block].get("digest", "?")[:16], current[:16]))
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="record the canary digests")
    parser.add_argument("--check", action="store_true", help="compare against the record")
    parser.add_argument("--cell", metavar="BLOCK", help="print one canary's payload")
    args = parser.parse_args(argv)
    if args.cell:
        print(json.dumps(payload(args.cell), indent=2))
        return 0
    if args.write:
        doc = build()
        DIGESTS.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        for block, cell in sorted(doc["cells"].items()):
            print("%-24s %s" % (block, cell["digest"][:16]))
        return 0
    problems = check()
    for problem in problems:
        print("FAIL:", problem)
    print("block canaries: %d cells, %s" % (len(frozen_blocks()),
                                          "all as recorded" if not problems else "CHANGED"))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
