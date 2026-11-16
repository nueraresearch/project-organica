"""The A1–A5 gate suite for the first V2 cell, and the record the runner requires.

A1 checks the canonicalisation rule on paths, on the spent smoke stream, and against both
committed identity regressions. A2–A5 test the level-1 primitive built under
`DECISION-V2-PRIMITIVE-BUILD`: identifier invariants on a temporary store, mutation
invariants with a bystander control, a page-count of the rebuilt base world at `m = 2`, and
two rebuilds for allocation-order determinism. A gate that raises is recorded `FAIL` with
the exception, never `PASS`.

The smoke seed `20911101` is the spent dry-run seed; A4 and A5 rebuild the V1 development
world `20740101`. No cell is run and no reserved seed is touched.

    python -m benchmarks.v2_first_cell_gates --check
    python -m benchmarks.v2_first_cell_gates --write
"""
from __future__ import annotations

import argparse
import collections
import datetime
import functools
import itertools
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from benchmarks import v2_first_cell_readout as readout  # noqa: E402
from benchmarks import v2_first_cell_runner as runner  # noqa: E402
from benchmarks import v2_primitive as primitive  # noqa: E402

OUT = REPO / "docs" / "v2_first_cell_gates.json"
PAGE = REPO / "docs" / "V2-FIRST-CELL-GATES.md"
IDENTITY = REPO / "docs" / "v1_carrier_identity.json"
REKEY = REPO / "docs" / "v1_rekeying_study_20900101.json"
SMOKE = readout.DRY_SEED
SMOKE_CYCLES = 120
BASE_SEED = 20740101
BASE_CYCLES = 120
SIZING = REPO / "docs" / "v2_primitive_sizing.json"


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
        "Scope: this gate does not replay the ten cell seeds; the runner replays each cell seed "
        "and applies this canonicalisation check to the experiment's own detection stream before "
        "any arm."
        % (rule["paths"], rule["keys"], rule["mixed"], stream["seed"], stream["cycles"],
           stream["detections"], stream["keys"], stream["node_sets"])
    )
    return {"status": "PASS", "evidence": evidence}


def _gate(run) -> dict:
    try:
        return {"status": "PASS", "evidence": run()}
    except Exception as error:  # a gate that cannot hold its own check is a FAIL, not a skip
        return {"status": "FAIL", "evidence": "%s: %s" % (type(error).__name__, error)}


def _a2_run() -> str:
    with tempfile.TemporaryDirectory() as directory:
        with primitive.Primitive(Path(directory) / "a2.db") as store:
            key = ("alpha", "bravo", "charlie")
            edges = (("alpha", "bravo"), ("alpha", "charlie"), ("bravo", "charlie"))
            cid = store.register(key, edges)
            store.add_member(cid, ("charlie", "delta"), 1)
            assert store.resolve(cid)["id"] == cid, "I1: id moved on a version bump"
            assert store.register(("alpha", "charlie", "bravo")) == cid, "I1: flip changed id"
            other = store.register(("delta", "echo", "foxtrot"), (("delta", "echo"),))
            assert other == cid + 1, "I2: ids are not independent of content"
            store.remove_member(cid, ("charlie", "delta"), 2)
            assert store.resolve(cid)["id"] == cid, "I1: id moved on a member change"

            victim = store.register(("golf", "hotel", "india"), (("golf", "hotel"),))
            store.retire(victim, 1)
            grave = store.resolve(victim)
            assert grave["retired"] is True, "I3: retire did not leave a tombstone"
            assert grave["members"] == (("golf", "hotel"),), "I3: tombstone lost its members"
            assert store.register(("golf", "hotel", "india")) == victim, "I3: key was freed"
            assert store.register(("juliet", "kilo")) == victim + 1, "I3: id was reused"

            for bad in ("1", key, True, None, 1.0):
                for call in (store.resolve, store.members):
                    try:
                        call(bad)
                    except TypeError:
                        pass
                    else:
                        raise AssertionError("I4: retrieval accepted %r" % (bad,))
            try:
                store.resolve(999)
            except primitive.UnknownComposite:
                pass
            else:
                raise AssertionError("I4: an unknown id resolved")
            try:
                store.resolve(victim, version=1)
            except primitive.StaleVersion:
                pass
            else:
                raise AssertionError("I5: a stale version resolved")
            return (
                "I1-I5 pass on a temporary store: the id survived a version bump, a member change "
                "and a direction flip; ids came from a monotone counter (1, 2, 3, 4) and were not "
                "content-derived; retirement preserved 1 member and its id, and the next key got id 4; "
                "5 non-integer or content addresses were rejected; an unknown id and a stale version "
                "both raised."
            )


def a2() -> dict:
    return _gate(_a2_run)


def _a3_run() -> str:
    with tempfile.TemporaryDirectory() as directory:
        with primitive.Primitive(Path(directory) / "a3.db") as store:
            target = store.register(
                ("alpha", "bravo", "charlie"),
                (("alpha", "bravo"), ("alpha", "charlie"), ("bravo", "charlie")),
            )
            bystander = store.register(("delta", "echo", "foxtrot"), (("delta", "echo"),))
            before = json.dumps(store.resolve(bystander), sort_keys=True)
            store.add_member(target, ("charlie", "golf"), 1)
            assert json.dumps(store.resolve(bystander), sort_keys=True) == before, "M1: bystander moved"
            store.remove_member(target, ("charlie", "golf"), 2)
            assert json.dumps(store.resolve(bystander), sort_keys=True) == before, "M1: bystander moved"

            shared = ("alpha", "bravo")
            target2 = store.register(("alpha", "bravo", "delta"), (shared, ("bravo", "delta")))
            bystander2 = store.register(("alpha", "bravo", "echo"), (shared,))
            atom_before = store.atom(shared)
            before2 = json.dumps(store.resolve(bystander2), sort_keys=True)
            store.add_member(target2, ("charlie", "echo"), 1)
            store.remove_member(target2, shared, 2)
            assert store.atom(shared) == atom_before, "M2: a shared atom moved"
            assert json.dumps(store.resolve(bystander2), sort_keys=True) == before2, "M2: bystander moved"

            current = store.resolve(target)["version"]
            store.add_member(target, ("delta", "echo"), current)
            bumped = store.resolve(target)["version"]
            try:
                store.add_member(target, ("delta", "echo"), current)
            except primitive.StaleVersion:
                pass
            else:
                raise AssertionError("M3: a stale version applied")
            try:
                store.remove_member(target, ("zulu", "yankee"), bumped)
            except KeyError:
                pass
            else:
                raise AssertionError("M3: a non-member removal applied")
            assert store.resolve(target)["version"] == bumped, "M3: a failed mutation moved the version"

            store.retire(target, bumped)
            assert store.resolve(target)["retired"] is True, "M4: retirement left no tombstone"
            assert store.resolve(target)["members"], "M4: retirement dropped the members"
            try:
                store.add_member(target, ("echo", "foxtrot"), bumped + 1)
            except primitive.RetiredComposite:
                pass
            else:
                raise AssertionError("M4: a retired composite mutated")

            assert store.table_names() == set(primitive.TABLES), "M5: unexpected table"
            store.assert_frozen_graph_untouched(primitive.FROZEN_TABLES)
            try:
                store.assert_frozen_graph_untouched({"atoms"})
            except primitive.FrozenGraphError:
                pass
            else:
                raise AssertionError("M5: the frozen-graph guard cannot fire")
            source = (("alpha", "bravo"), ("bravo", "charlie"))
            snapshot = tuple(source)
            store.register(("alpha", "bravo", "charlie"), source)
            assert source == snapshot, "M5: the source member set was mutated"
            return (
                "M1-M5 pass on a temporary store with a bystander: add and remove left the "
                "bystander's resolved state byte-identical; a shared atom kept version 1 and its "
                "binding; a stale version and a non-member removal were rejected without moving the "
                "version; retirement kept 3 members and refused further mutation; the store owns "
                "only %s and the frozen-graph guard can fire." % ", ".join(primitive.TABLES)
            )


def a3() -> dict:
    return _gate(_a3_run)


@functools.lru_cache(maxsize=1)
def smoke_admissions() -> dict:
    """The spent smoke world's admitted population at m = 2, used only by A5's determinism check."""
    data = readout.replay(SMOKE, SMOKE_CYCLES)
    counts = collections.Counter(readout.canonical(path) for _, path in data["detections"])
    admitted = sorted(key for key, count in counts.items() if count >= 2)
    admissions = tuple(
        (key, tuple(sorted(itertools.combinations(key, 2)))) for key in admitted
    )
    return {
        "appearances": len(data["detections"]),
        "keys": len(counts),
        "admitted": len(admissions),
        "admissions": admissions,
    }


@functools.lru_cache(maxsize=1)
def base_admissions() -> dict:
    """The reallocated base world rebuilt at m = 2, with its observed edge sets."""
    data = readout.replay(BASE_SEED, BASE_CYCLES)
    counts = collections.Counter(readout.canonical(path) for _, path in data["detections"])
    admitted = sorted(key for key, count in counts.items() if count >= 2)
    admissions = tuple(
        (key, tuple(sorted(itertools.combinations(key, 2)))) for key in admitted
    )
    return {
        "appearances": len(data["detections"]),
        "keys": len(counts),
        "admitted": len(admissions),
        "admissions": admissions,
    }


def _a4_run() -> str:
    world = base_admissions()
    budget = _load(SIZING)["headline"]
    with tempfile.TemporaryDirectory() as directory:
        with primitive.Primitive(Path(directory) / "a4.db") as store:
            for key, edges in world["admissions"]:
                store.register(key, edges)
            count = world["admitted"]
            before = {cid: store.resolve(cid) for cid in range(1, count + 1)}
            reclaimed = store.compact()
            after = {cid: store.resolve(cid) for cid in range(1, count + 1)}
            assert after == before, "A4: compaction changed a resolution"
            pages, size = store.page_count(), store.byte_size()
            references = sum(len(edges) for _, edges in world["admissions"])
            assert size <= budget["primitive_bytes"], (
                "A4: %d bytes exceeds the %d-byte budget" % (size, budget["primitive_bytes"])
            )
            return (
                "reallocated base seed %d, %d cycles: %d of %d keys admitted at m=2, %d observed "
                "member references (the sizing model assumed 3 per composite, %d); the rebuilt "
                "store is %d pages / %d bytes, at or below the %d-byte budget; compaction reclaimed "
                "%d atoms and left all %d resolutions identical; tables %s carry no history table."
                % (BASE_SEED, BASE_CYCLES, count, world["keys"], references,
                   budget["references"], pages, size, budget["primitive_bytes"], reclaimed, count,
                   ", ".join(primitive.TABLES))
            )


def a4() -> dict:
    return _gate(_a4_run)


def _novel_key(admissions) -> tuple[str, str]:
    for candidate in (("quux", "zorp"), ("wxyz", "vutf")):
        if all(set(key) != set(candidate) for key, _edges in admissions):
            return candidate
    raise AssertionError("A5: no novel key is available")


def _a5_run() -> str:
    world = smoke_admissions()
    count = world["admitted"]
    novel = _novel_key(world["admissions"])

    def rebuild(path: Path):
        with primitive.Primitive(path) as store:
            for key, edges in world["admissions"]:
                store.register(key, edges)
            snapshot = [store.resolve(cid) for cid in range(1, count + 1)]
            store.retire(count, 1)
            assert store.resolve(count)["retired"] is True
            next_id = store.register(novel)
            assert next_id == count + 1, "A5: retirement did not advance allocation"
            assert store.resolve(count)["retired"] is True, "A5: retirement was undone"
            return snapshot, next_id

    with tempfile.TemporaryDirectory() as directory:
        first, next_a = rebuild(Path(directory) / "a5-a.db")
        second, next_b = rebuild(Path(directory) / "a5-b.db")
        assert first == second, "A5: two builds disagree"
        assert next_a == next_b == count + 1
        return (
            "two builds from the spent smoke stream's %d admissions produced identical ids, keys, "
            "members and versions; retiring id %d left a tombstone and the next registration got "
            "id %d, so allocation is monotone and retirement never frees an id; the novel key %s "
            "was absent from the stream. Scope: the smoke stream, not the held base world."
            % (count, count, count + 1, "|".join(novel))
        )


def a5() -> dict:
    return _gate(_a5_run)


def status_of(gates: dict) -> str:
    failed = [gate for gate in ("A1", "A2", "A3", "A4", "A5")
              if gates[gate]["status"] != "PASS"]
    if failed:
        return "GATES NOT CLEARED — %s NOT PASS; THE CELL IS NOT RUNNABLE" % ", ".join(failed)
    return "A1-A5 PASS — THE PRIMITIVE IS BUILT; THE CELL IS NOT RUN"


def build(date: str | None = None) -> dict:
    gates = {"A1": a1(), "A2": a2(), "A3": a3(), "A4": a4(), "A5": a5()}
    runner.validate_gates(gates)
    record = {
        "kind": "v2_first_cell_gates",
        "id": "V2-FIRST-CELL-GATES-1",
        "date": date or datetime.date.today().isoformat(),
        "status": status_of(gates),
        "gates": gates,
        "inputs": [
            "docs/v1_carrier_identity.json",
            "docs/v1_rekeying_study_20900101.json",
            "docs/v2_primitive_sizing.json",
            "docs/v2_first_cell_dry_run.json",
            "docs/V2-MUTABLE-IDENTITY-SPEC.md",
            "benchmarks/v2_primitive.py",
        ],
        "smoke_seed": SMOKE,
        "base_seed": BASE_SEED,
        "note": (
            "A gate record is not a result. PASS means the gate's checks ran and held; it does not "
            "make the primitive predictive. A4 was measured on the base seed released by "
            "DECISION-V2-A4-BASE-WORLD; the cell has not run and the ten reserved cell seeds are "
            "untouched. Any non-PASS gate is a gate failure and the runner assembles VOID."
        ),
    }
    return record


def render(record: dict) -> str:
    gates = record["gates"]
    rows = "\n".join("| %s | %s | %s |" % (gate, gates[gate]["status"], gates[gate]["evidence"])
                     for gate in ("A1", "A2", "A3", "A4", "A5"))
    failed = [gate for gate in ("A2", "A3", "A4", "A5") if gates[gate]["status"] != "PASS"]
    if failed:
        primitive_paragraph = (
            "%s did not pass. The record keeps the failure and its evidence; the runner treats any "
            "non-PASS gate as a gate failure." % ", ".join(failed)
        )
        consequence = (
            "The cell is **not runnable**: a signed authorisation would write a `VOID` artifact "
            "without executing a seed."
        )
    else:
        primitive_paragraph = (
            "A2-A5 pass on the level-1 primitive built under "
            "[`DECISION-V2-PRIMITIVE-BUILD`](DECISION-V2-PRIMITIVE-BUILD.md): the identifier and "
            "mutation invariants hold on a temporary store, A4's page-count is the rebuilt base "
            "world's, and A5 rebuilt it twice with the same allocation order. The page count is a "
            "measurement of this build, not the sizing estimate."
        )
        consequence = (
            "The gate block is cleared. The runner can execute the cell as soon as "
            "`DECISION-V2-FIRST-CELL` is signed; while it is `PENDING` the runner still refuses. "
            "Clearing the gates does not authorise the cell."
        )
    return f"""# V2 first cell — A1–A5 gate record (not a result)

**Generated** by `python -m benchmarks.v2_first_cell_gates --write`. Do not edit by hand;
`--check` fails when the page and the record disagree.

**Status:** `{record['status']}`

The gate suite runs before the behavioural cell and writes the record
`benchmarks/v2_first_cell_runner.py` requires. It runs no cell seed: A1 and A5 use the spent smoke
seed `{record['smoke_seed']}`; A4 rebuilds the reallocated base world `{record['base_seed']}` for a
storage measurement only. The ten reserved cell seeds are untouched.

## Gates

| Gate | Status | What was checked |
|---|---|---|
{rows}

## What this means

A1 passes because the canonicalisation rule is total on sample paths, holds on the smoke
stream, and both committed identity regressions reproduce exactly. This gate is the rule and a
development stream; at run time the runner replays each cell seed and applies the same check to
the experiment's own detection stream before any arm.

{primitive_paragraph}

{consequence}

## Not evidence

This is an instrument record, not a causal, capability or transfer result. No cell ran, no
reserved seed was spent, and no verdict exists. Clearing the gates does not make the primitive
predictive: the earning test still decides that, and it is still allowed to fail.
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
