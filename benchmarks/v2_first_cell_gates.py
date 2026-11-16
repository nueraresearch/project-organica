"""The A1–A5 gate suite for the first V2 cell, and the record the runner requires.

The suite runs the gates that exist and refuses to mark the ones that do not. A1 is
checkable now: the canonicalisation rule is exercised on paths, on the smoke stream, and
against both committed identity regressions. A2–A5 are the primitive's invariants, and the
primitive is not built — there is no stored id, no mutation API and no rebuilt store — so
they are recorded `NOT RUN`, not `PASS`. The runner treats `NOT RUN` as a gate failure and
assembles a `VOID`; that is the honest state of the cell.

The smoke seed `20911101` is the spent dry-run seed, never one of the ten reserved seeds.
No cell is run and no reserved seed is touched.

    python -m benchmarks.v2_first_cell_gates --check
    python -m benchmarks.v2_first_cell_gates --write
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from benchmarks import v2_first_cell_readout as readout, v2_first_cell_runner as runner  # noqa: E402

OUT = REPO / "docs" / "v2_first_cell_gates.json"
PAGE = REPO / "docs" / "V2-FIRST-CELL-GATES.md"
IDENTITY = REPO / "docs" / "v1_carrier_identity.json"
REKEY = REPO / "docs" / "v1_rekeying_study_20900101.json"
SIZING = REPO / "docs" / "v2_primitive_sizing.json"
SMOKE = readout.DRY_SEED
STATUS = "A1 PASS; A2-A5 NOT RUN — THE PRIMITIVE IS NOT BUILT, SO THE CELL IS NOT RUNNABLE"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def a1_rule() -> dict:
    """The canonicalisation is total: flips share a key, distinct node sets never do."""
    samples = [
        ("alpha", "beta", "gamma"),
        ("gamma", "beta", "alpha"),
        ("alpha", "beta", "gamma", "alpha"),
        ("alpha", "delta", "beta", "gamma"),
        ("delta", "gamma", "beta"),
    ]
    keys = {}
    for path in samples:
        key = readout.canonical(path)
        if key != tuple(sorted(set(path))):
            raise AssertionError("canonical is not the sorted tag set")
        if readout.canonical(tuple(reversed(path))) != key:
            raise AssertionError("a direction flip changed the key")
        keys.setdefault(key, set()).add(frozenset(path))
    mixed = [key for key, node_sets in keys.items() if len(node_sets) > 1]
    if mixed:
        raise AssertionError("one key mapped to two node sets")
    if readout.canonical(("alpha", "beta", "gamma")) == readout.canonical(("alpha", "beta", "delta")):
        raise AssertionError("distinct node sets collided")
    return {"paths": len(samples), "keys": len(keys), "mixed": len(mixed)}


def a1_regressions() -> dict:
    """The two committed regressions the pre-registration names."""
    identity = _load(IDENTITY)
    rekey = _load(REKEY)
    checks = {
        "177->158": (
            identity["distinct_paths"] == 177
            and identity["distinct_node_sets"] == 158
            and identity["paths_per_node_set"] == {"1": 139, "2": 19}
        ),
        "138->125": (
            rekey["observed"]["distinct_paths"] == 138
            and rekey["observed"]["distinct_node_sets"] == 125
            and rekey["direction_free"]["identities"] == 125
        ),
        "no-id-collisions": identity["id_collisions"] == 0,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise AssertionError("committed regression(s) failed: %s" % ", ".join(failed))
    return {"checks": sorted(checks), "177": [177, 158, 139, 19], "138": [138, 125]}


def a1_stream(seed: int = SMOKE, cycles: int = 120) -> dict:
    """Exercise the rule on the spent smoke stream, never on a reserved seed."""
    data = readout.replay(seed, cycles)
    paths = [tuple(path) for _, path in data["detections"] if len(set(path)) >= 2]
    by_key = collections.defaultdict(set)
    for path in paths:
        by_key[readout.canonical(path)].add(frozenset(path))
    mixed = [key for key, node_sets in by_key.items() if len(node_sets) > 1]
    flips = sum(1 for path in paths if readout.canonical(tuple(reversed(path))) != readout.canonical(path))
    node_sets = {frozenset(path) for path in paths}
    if mixed:
        raise AssertionError("the smoke stream produced a key that mixed node sets")
    if flips:
        raise AssertionError("a direction flip changed a key on the smoke stream")
    if len(by_key) != len(node_sets):
        raise AssertionError("keys and distinct node sets differ on the smoke stream")
    return {
        "seed": seed,
        "cycles": cycles,
        "detections": len(paths),
        "keys": len(by_key),
        "node_sets": len(node_sets),
        "mixed": len(mixed),
        "flips": flips,
    }


def a1() -> dict:
    rule = a1_rule()
    regressions = a1_regressions()
    stream = a1_stream()
    evidence = (
        "canonicalisation rule: %d sample paths, %d keys, %d mixed keys, 0 flips changed a key; "
        "smoke seed %d (%d cycles, spent dry-run seed, not a cell seed): %d detected paths -> "
        "%d keys over %d distinct node sets, 0 mixed, 0 flip failures; committed regressions "
        "177->158 with multiplicities {1: 139, 2: 19} and 138->125 reproduce; 0 id collisions. "
        "Scope: the ten cell seeds are not replayed, so this is the rule and a development stream, "
        "not the experiment's own detection stream."
        % (rule["paths"], rule["keys"], rule["mixed"], stream["seed"], stream["cycles"],
           stream["detections"], stream["keys"], stream["node_sets"])
    )
    return {"status": "PASS", "evidence": evidence}


def a2() -> dict:
    return {
        "status": "NOT RUN",
        "evidence": (
            "no stored composite id exists: the readout keys membership by the canonical tag set, "
            "and there is no composite_ids table, register(), id/version API or tombstone. "
            "I1-I5 are unimplemented, so this gate is not run."
        ),
    }


def a3() -> dict:
    return {
        "status": "NOT RUN",
        "evidence": (
            "no mutation API (add_member, remove_member, retire) and no stored rows; the readout "
            "recomputes members in memory, so there is no bystander row set to assert byte-identical. "
            "M1-M5 are unimplemented, so this gate is not run."
        ),
    }


def a4() -> dict:
    sizing = _load(SIZING)["headline"]
    return {
        "status": "NOT RUN",
        "evidence": (
            "no rebuilt primitive store to page-count. v2_primitive_sizing is a static estimate of "
            "%d bytes at %s on the measured graph, not the required page-count of the built primitive "
            "and not a before/after resolution comparison."
            % (sizing["primitive_bytes"], sizing["threshold"])
        ),
    }


def a5() -> dict:
    return {
        "status": "NOT RUN",
        "evidence": (
            "no ids, versions or retirements exist to replay. The readout's key and member computation "
            "is deterministic in --check, but that is the harness, not the primitive's allocation order."
        ),
    }


def build(date: str | None = None) -> dict:
    gates = {"A1": a1(), "A2": a2(), "A3": a3(), "A4": a4(), "A5": a5()}
    runner.validate_gates(gates)
    record = {
        "kind": "v2_first_cell_gates",
        "id": "V2-FIRST-CELL-GATES-1",
        "date": date or datetime.date.today().isoformat(),
        "status": STATUS,
        "gates": gates,
        "inputs": [
            "docs/v1_carrier_identity.json",
            "docs/v1_rekeying_study_20900101.json",
            "docs/v2_primitive_sizing.json",
            "docs/v2_first_cell_dry_run.json",
        ],
        "smoke_seed": SMOKE,
        "note": (
            "A gate record is not a result. NOT RUN means the gate has no implementation to test, "
            "not that it passed; the runner treats it as a gate failure and assembles VOID. The ten "
            "reserved seeds are untouched."
        ),
    }
    return record


def render(record: dict) -> str:
    gates = record["gates"]
    rows = "\n".join("| %s | %s | %s |" % (gate, gates[gate]["status"], gates[gate]["evidence"])
                     for gate in ("A1", "A2", "A3", "A4", "A5"))
    return f"""# V2 first cell — A1–A5 gate record (not a result)

**Generated** by `python -m benchmarks.v2_first_cell_gates --write`. Do not edit by hand;
`--check` fails when the page and the record disagree.

**Status:** `{record['status']}`

The gate suite runs before the behavioural cell and writes the record
`benchmarks/v2_first_cell_runner.py` requires. It runs no cell seed: A1 uses the spent smoke
seed `{record['smoke_seed']}` as a development stream, and the ten reserved seeds are untouched.

## Gates

| Gate | Status | What was checked |
|---|---|---|
{rows}

## What this means

A1 passes because the canonicalisation rule is total on sample paths, holds on the smoke
stream, and both committed identity regressions reproduce exactly. It is the rule and a
development stream, not the experiment's own detection stream.

A2, A3, A4 and A5 are **not run**, not passed. The mutable-identity primitive those gates
test does not exist in this repository: there is no stored composite id, no mutation API,
no rebuilt store, and no id/version/tombstone sequence. A sizing estimate is not a page
count, and a deterministic readout is not a deterministic allocation order. Marking any of
them PASS would claim a check that was never made.

Because the runner treats `NOT RUN` as a gate failure, the cell is **not runnable**: if the
authorisation were signed now, `--run` would write a `VOID` artifact without executing a
seed. The missing input is the primitive the charter specified but did not authorise; a bounded
build is drafted in [`DECISION-V2-PRIMITIVE-BUILD`](DECISION-V2-PRIMITIVE-BUILD.md) and remains
unsigned.

## Not evidence

This is an instrument record, not a causal, capability or transfer result. No cell ran, no
reserved seed was spent, and no verdict exists.
"""


def check() -> None:
    if not OUT.exists():
        raise SystemExit("no gate record; run --write")
    committed = _load(OUT)
    # Rebuild the checks, not the clock: a record is stale when its evidence moved, not when
    # the date changed.
    record = build(date=committed["date"])
    if committed != record:
        raise SystemExit("the gate record is stale; run --write")
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(record):
        raise SystemExit("the gate page is stale; run --write")
    statuses = {gate: record["gates"][gate]["status"] for gate in record["gates"]}
    print("check: %s; %s; record and page fresh"
          % (record["status"], ", ".join("%s=%s" % item for item in statuses.items())))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="rebuild and compare; writes nothing")
    group.add_argument("--write", action="store_true", help="write the record and the page")
    args = parser.parse_args(argv)
    if args.write:
        record = build()
        OUT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        PAGE.write_text(render(record), encoding="utf-8")
        print("wrote %s and %s: %s" % (OUT, PAGE, record["status"]))
        return 0
    check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
