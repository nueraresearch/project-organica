"""Reserved-but-unspent seed blocks, visible to the freshness guard.

The freshness scan in `benchmarks.presence_cap_experiment.seed_collisions`
answers one question: has any committed artifact already named this seed?  It
skips an allow list of artifacts so that a candidate does not collide with
itself, and that skip is exactly the hole here: a seed block declared in an
allow-listed artifact (the pair-split construction, `20690101-20690106`) is
invisible to the scan, so a future candidate could list the same seeds, find no
collision and pass.

This module gives reserved blocks their own declaration and their own check:

* `docs/a1_seed_reservations.json` names each unspent block, the artifact that
  reserves it, and any artifact that restates it,
* `reservation_problems(seeds, candidate)` refuses a candidate that lists a
  reserved seed unless it *is* the reserving artifact or one that restates it,
* `problems()` validates the registry against the tree: owners and restatements
  exist, every reserved seed is actually named by its owner, blocks do not
  overlap, and no other artifact names a reserved seed.

A reservation is a note that seeds are held, not a claim that they were spent.

    python -m benchmarks.a1_seed_reservations --check
    python -m benchmarks.a1_seed_reservations --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REGISTRY_PATH = DOCS / "a1_seed_reservations.json"
# A generated census names every seed-bearing artifact, so it names every reserved
# seed by construction. Naming a reserve is not spending it: the census runs no
# cell and allocates no seed, so its repetition of a block is not a claim on it.
CENSUS_ARTIFACT = "docs/stage_b_protocol.json"
ID = "A1-SEED-RESERVATIONS-1"
KIND = "a1_seed_reservations"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    if not path.is_absolute():
        return path.as_posix().lstrip("./")
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def registry(path: Path | None = None) -> dict:
    return _load(REGISTRY_PATH if path is None else path)


def _seeds_of(node) -> set[int]:
    out: set[int] = set()

    def walk(value):
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, bool):
            return
        elif isinstance(value, int):
            out.add(value)
        elif isinstance(value, float) and value.is_integer():
            out.add(int(value))

    walk(node)
    return out


def declared_seeds(doc: dict) -> list[int]:
    """The seed block an artifact declares, in either committed shape.

    Newer manifests store `seed_block` as an object with a `seeds` list; the
    older candidates and the three cap-112 preregistrations store it as a bare
    list. Both are declarations of a block, and the check reads both.
    """
    block = doc.get("seed_block") if isinstance(doc, dict) else None
    if isinstance(block, dict):
        block = block.get("seeds")
    if not isinstance(block, list):
        return []
    return [int(seed) for seed in block
            if isinstance(seed, int) and not isinstance(seed, bool)]


def candidate_blocks(docs=None) -> list[tuple[str, list[int]]]:
    """Every artifact in the tree that declares a seed block."""
    if docs is not None:
        return [(_relative(Path(path)), declared_seeds(doc))
                for path, doc in docs]
    out = []
    for path in sorted(DOCS.glob("*.json")):
        seeds = declared_seeds(_load(path))
        if seeds:
            out.append((_relative(path), seeds))
    return out


def candidate_problems(docs=None) -> list[str]:
    """Refusals for every declared block in the tree, each on its own behalf."""
    found: list[str] = []
    for rel, seeds in candidate_blocks(docs):
        for row in reservation_problems(seeds, rel):
            found.append("%s: %s" % (rel, row))
    return found


def shared_blocks(doc: dict | None = None) -> list[dict]:
    """Seed blocks that more than one artifact declares on purpose."""
    doc = registry() if doc is None else doc
    out = []
    for row in doc.get("shared_blocks") or []:
        out.append({
            "label": row.get("label", ""),
            "seeds": [int(seed) for seed in row.get("seeds") or []],
            "artifacts": list(row.get("artifacts") or []),
            "declared_by": row.get("declared_by", ""),
            "basis": row.get("basis", ""),
            "provenance": row.get("provenance", ""),
            "pending": row.get("pending", ""),
        })
    return out


def _reservation_holders() -> set[str]:
    """Artifacts a reservation already speaks for, by path."""
    holders: set[str] = set()
    for row in reservations():
        holders.add(_relative(Path(row["owner"])))
        holders.update(_relative(Path(entry)) for entry in row["restated_by"])
    return holders


def shared_block_problems(doc: dict | None = None,
                          blocks=None) -> list[str]:
    """Declared sharing is verified; undeclared sharing is refused.

    Two artifacts declaring the same seeds is only a defect if nothing says
    why. Each `shared_blocks` entry must name artifacts that really declare
    that block, each of which must carry the declared field, and the seeding
    source it names must hold those seeds. Sharing that no entry covers — and
    that no reservation already speaks for — is refused.
    """
    doc = registry() if doc is None else doc
    entries = shared_blocks(doc)
    blocks = candidate_blocks() if blocks is None else list(blocks)
    found: list[str] = []
    declared: set[frozenset[int]] = set()
    for row in entries:
        seeds = frozenset(row["seeds"])
        label = row["label"] or "unnamed shared block"
        declared.add(seeds)
        if not row["basis"]:
            found.append("%s: no basis is recorded" % label)
        if not row["declared_by"] and not row["pending"]:
            found.append("%s: no declaring field is named and nothing is pending"
                         % label)
        for entry in row["artifacts"]:
            declared_doc = ROOT / entry
            if not entry or not declared_doc.exists():
                found.append("%s: %s is missing" % (label, entry))
                continue
            own = declared_seeds(_load(declared_doc))
            if frozenset(own) != seeds:
                found.append("%s: %s does not declare that block" % (label, entry))
                continue
            if not row["declared_by"]:
                continue
            declared_value = _load(declared_doc).get(row["declared_by"])
            if not isinstance(declared_value, str) or not declared_value.strip():
                found.append("%s: %s does not carry %s"
                             % (label, entry, row["declared_by"]))
        if row["provenance"]:
            source = ROOT / row["provenance"]
            if not source.exists():
                found.append("%s: the seeding source %s is missing"
                             % (label, row["provenance"]))
            elif not seeds <= _seeds_of(_load(source)):
                found.append("%s: the seeding source %s does not hold those seeds"
                             % (label, row["provenance"]))
    holders = _reservation_holders()
    groups: dict[frozenset[int], list[str]] = {}
    for rel, seeds in blocks:
        if not seeds or rel in holders:
            continue
        groups.setdefault(frozenset(seeds), []).append(rel)
    for seeds, artifacts in sorted(groups.items(), key=lambda item: sorted(item[1])):
        if len(artifacts) < 2 or seeds in declared:
            continue
        found.append("a block is declared by %s and is not a recorded shared block"
                     % " and ".join(sorted(artifacts)))
    return found


def reservations(doc: dict | None = None) -> list[dict]:
    """The reserved blocks, each with its seed set as integers."""
    doc = registry() if doc is None else doc
    out = []
    for row in doc.get("reservations") or []:
        out.append({
            "label": row.get("label", ""),
            "owner": row.get("owner", ""),
            "restated_by": list(row.get("restated_by") or []),
            "seeds": sorted({int(seed) for seed in row.get("seeds") or []}),
            "spent": bool(row.get("spent", False)),
        })
    return out


def reservation_problems(seeds, candidate: Path | str,
                         doc: dict | None = None) -> list[str]:
    """Refusals for a candidate that lists a reserved, unspent seed."""
    holder = {_relative(Path(str(candidate)))}
    found: list[str] = []
    for row in reservations(doc):
        allowed = {_relative(Path(entry))
                   for entry in [row["owner"]] + row["restated_by"]}
        shared = sorted(set(int(seed) for seed in seeds) & set(row["seeds"]))
        if not shared or holder & allowed:
            continue
        if row["spent"]:
            found.append(
                "seed(s) %s were spent by %s (%s); a spent block may not be reused"
                % (", ".join(str(seed) for seed in shared), row["owner"],
                   row["label"]))
            continue
        found.append(
            "seed(s) %s are reserved by %s (%s) and unspent"
            % (", ".join(str(seed) for seed in shared), row["owner"],
               row["label"]))
    return found


def problems(doc: dict | None = None) -> list[str]:
    doc = registry() if doc is None else doc
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("registry kind")
    rows = doc.get("reservations") or []
    if not rows:
        found.append("the registry reserves nothing")
    seen: dict[int, str] = {}
    for row in rows:
        label = row.get("label") or "unnamed reservation"
        owner = row.get("owner") or ""
        owner_path = ROOT / owner
        if not owner or not owner_path.exists():
            found.append("%s: the reserving artifact is missing" % label)
            continue
        seeds = [int(seed) for seed in row.get("seeds") or []]
        if not seeds:
            found.append("%s: no seeds reserved" % label)
        if len(seeds) != len(set(seeds)):
            found.append("%s: duplicate seeds inside the block" % label)
        for seed in seeds:
            if seed in seen:
                found.append("seed %d is reserved by two blocks" % seed)
            seen[seed] = label
        owner_seeds = _seeds_of(_load(owner_path))
        missing = sorted(set(seeds) - owner_seeds)
        if missing:
            found.append("%s: the reserving artifact does not name %s"
                         % (label, missing))
        for entry in [row.get("owner")] + list(row.get("restated_by") or []):
            if entry and not (ROOT / entry).exists():
                found.append("%s: restating artifact %s is missing"
                             % (label, entry))
        allowed = {_relative(Path(entry))
                   for entry in [owner] + list(row.get("restated_by") or [])}
        if row.get("spent"):
            continue
        for path in sorted(DOCS.glob("*.json")):
            rel = _relative(path)
            if (rel in allowed or rel == _relative(REGISTRY_PATH)
                    or rel == CENSUS_ARTIFACT):
                continue
            shared = sorted(_seeds_of(_load(path)) & set(seeds))
            if shared:
                found.append("%s: %s names reserved seed(s) %s"
                             % (label, rel, shared))
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    doc = registry()
    rows = reservations()
    if not rows:
        failures.append("no reservations to test")
        return failures
    block = rows[0]
    reserved = block["seeds"][:1]
    owner = Path(block["owner"])
    if reservation_problems(reserved, owner):
        failures.append("the reserving artifact collides with itself")
    if reservation_problems(reserved, Path("docs/a1_two_path_manifest.json")):
        pass  # a foreign candidate must be refused
    else:
        failures.append("a foreign candidate listing a reserved seed was allowed")
    if reservation_problems([20880101], Path("docs/a1_two_path_manifest.json")):
        failures.append("a seed outside every reservation was refused")
    spent = dict(doc, reservations=[dict(block, spent=True, seeds=reserved)])
    spent_refusals = reservation_problems(
        reserved, Path("docs/a1_two_path_manifest.json"), spent)
    if not spent_refusals or "were spent by" not in spent_refusals[0]:
        failures.append("a spent block does not refuse a foreign candidate")
    if reservation_problems(reserved, Path(block["owner"]), spent):
        failures.append("a spent block refuses the artifact that spent it")
    return failures


def check() -> int:
    if not REGISTRY_PATH.exists():
        raise SystemExit("no seed-reservation registry")
    found = problems() + candidate_problems() + shared_block_problems()
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    total = sum(len(row["seeds"]) for row in reservations() if not row["spent"])
    blocks = candidate_blocks()
    for rel, seeds in blocks:
        print("  %-45s %d seed(s)" % (rel, len(seeds)))
    shared = shared_blocks()
    for row in shared:
        print("  shared: %s -- %s" % (row["label"], ", ".join(row["artifacts"])))
        if row["pending"]:
            print("  PENDING: %s" % row["pending"])
    print("seed reservations: clean (%d unspent seeds held, %d declared block(s) "
          "checked, %d declared shared block(s))" % (total, len(blocks), len(shared)))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        found = self_test()
        if found:
            raise SystemExit("FAIL: " + "; ".join(found))
        print("seed reservations: self-test clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
