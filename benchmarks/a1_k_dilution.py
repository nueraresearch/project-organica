"""Why did K availability collapse when the A1 universe grew?

A read-only comparison of the two declared no-arm candidate universes:

* the fresh 16-tag block ``20650101``-``20650106``;
* the 28-tag larger-universe block ``20660101``-``20660106``.

The headline is not the edge count.  Candidate edges rose from 383 to 1000,
but K-available rows rose only from 242 to 244.  The report decomposes that
near-constant K supply by seed, transition type, endpoint novelty and cycle-36
U quartile.  It selects no target, sets no threshold, chooses no redesign and
runs no A1 cell.

The quantities are descriptive.  K is "at least one carrier in the 120-cycle
no-arm baseline", not a K-cycle count.  U is measured at cycle 36.  The
association has no identified direction and six seeds do not establish a
world-family law.

    python -m benchmarks.a1_k_dilution --write
    python -m benchmarks.a1_k_dilution --check
    python -m benchmarks.a1_k_dilution --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from benchmarks import a1_larger_universe
from benchmarks import a1_target_selection
from benchmarks.acquisition_compositional import (
    TAG_POOL,
    generate_compositional_world,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_k_dilution.json"
PAGE_PATH = DOCS / "A1-K-DILUTION.md"
ID = "A1-K-DILUTION-1"
DATE = "2026-11-14"
KIND = "a1_k_dilution"
STATUS = "DESCRIPTIVE — K DILUTION ACROSS TWO DECLARED WORLDS; NO ARM, NO THRESHOLD, NO REDESIGN"
C1_FLOOR = 60
OLD_TAGS = frozenset(TAG_POOL)

WORLDS = (
    {
        "label": "16-tag",
        "path": DOCS / "a1_successor_candidate.json",
        "tags": 16,
        "world": lambda seed: generate_compositional_world(seed=seed, cycles=120),
    },
    {
        "label": "28-tag",
        "path": DOCS / "a1_larger_universe_candidate.json",
        "tags": 28,
        "world": a1_larger_universe.generate_world,
    },
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _percent(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _family(edge: str) -> str:
    source, target = edge.split(">", 1)
    old = (source in OLD_TAGS) + (target in OLD_TAGS)
    if old == 2:
        return "old-old"
    if old == 1:
        return "old-new"
    return "new-new"


def _cell_relation(world: dict, edge: str) -> str:
    source, target = edge.split(">", 1)
    source_cell = world["tag_to_cell"].get(source)
    target_cell = world["tag_to_cell"].get(target)
    if source_cell is None or target_cell is None:
        return "unknown"
    if source_cell == target_cell:
        return "same"
    sp, sq = int(source_cell[1]), int(source_cell[3])
    tp, tq = int(target_cell[1]), int(target_cell[3])
    if sp != tp and sq == tq:
        return "flip_p"
    if sp == tp and sq != tq:
        return "flip_q"
    return "diagonal"


def _assign_quartiles(rows: list[dict]) -> None:
    """Rank U within each seed, then tag Q1 (lowest) through Q4 (highest)."""
    for seed in sorted({row["seed"] for row in rows}):
        block = sorted(
            (row for row in rows if row["seed"] == seed),
            key=lambda row: (row["U_strength"], row["edge"]),
        )
        size = len(block)
        for index, row in enumerate(block):
            row["U_quartile"] = "Q%d" % min(4, index * 4 // size + 1)


def _bucket(rows: list[dict], key: str, labels: tuple[str, ...] | None = None) -> list[dict]:
    groups: dict[object, list[dict]] = {}
    for row in rows:
        groups.setdefault(row[key], []).append(row)
    names = labels if labels is not None else tuple(sorted(groups, key=str))
    out = []
    for name in names:
        block = groups.get(name, [])
        if not block:
            continue
        entry = {
            "label": name,
            "candidate_edges": len(block),
            "A_available": sum(row["A"] for row in block),
            "K_available": sum(row["K"] for row in block),
            "A_and_K": sum(row["A"] and row["K"] for row in block),
            "A_density": _percent(sum(row["A"] for row in block), len(block)),
            "K_density": _percent(sum(row["K"] for row in block), len(block)),
            "A_and_K_density": _percent(
                sum(row["A"] and row["K"] for row in block), len(block)),
        }
        if key == "U_quartile":
            entry["min_U_strength"] = min(row["U_strength"] for row in block)
            entry["max_U_strength"] = max(row["U_strength"] for row in block)
        out.append(entry)
    return out


def _rows(spec: dict) -> tuple[dict, list[dict]]:
    doc = _load(spec["path"])
    rows = []
    for seed in doc["seed_block"]:
        world = spec["world"](seed)
        selection = a1_target_selection.run_seed(
            seed, world=world, boundary_safe=True)
        u = selection["u"]
        for candidate in doc["per_seed"][str(seed)]:
            edge = candidate["edge"]
            if edge not in u:
                raise ValueError("candidate edge %s is missing from U" % edge)
            rows.append({
                "seed": seed,
                "edge": edge,
                "A": bool(candidate["A"]),
                "K": bool(candidate["K"]),
                "U_strength": int(u[edge]["strength"]),
                "family": _family(edge),
                "cell_relation": _cell_relation(world, edge),
            })
    _assign_quartiles(rows)
    return doc, rows


def _summary(label: str, doc: dict, rows: list[dict]) -> dict:
    total = {
        "candidate_edges": len(rows),
        "A_available": sum(row["A"] for row in rows),
        "K_available": sum(row["K"] for row in rows),
        "A_and_K": sum(row["A"] and row["K"] for row in rows),
    }
    total["A_density"] = _percent(total["A_available"], total["candidate_edges"])
    total["K_density"] = _percent(total["K_available"], total["candidate_edges"])
    total["A_and_K_density"] = _percent(
        total["A_and_K"], total["candidate_edges"])
    per_seed = _bucket(rows, "seed")
    for row in per_seed:
        row["K_density_needed_for_60"] = _percent(60, row["candidate_edges"])
        row["gap_to_60"] = 60 - row["K_available"]
    return {
        "label": label,
        "tags": 16 if label == "16-tag" else 28,
        "seed_block": list(doc["seed_block"]),
        "candidate_id": doc["id"],
        "candidate_digest": _digest(next(
            spec["path"] for spec in WORLDS if spec["label"] == label)),
        "total": total,
        "per_seed": per_seed,
        "by_family": _bucket(rows, "family", ("old-old", "old-new", "new-new")),
        "by_transition": _bucket(rows, "cell_relation",
                                 ("flip_p", "flip_q", "same", "diagonal", "unknown")),
        "by_U_quartile": _bucket(rows, "U_quartile", ("Q1", "Q2", "Q3", "Q4")),
    }


def build() -> dict:
    worlds = {}
    for spec in WORLDS:
        doc, rows = _rows(spec)
        worlds[spec["label"]] = _summary(spec["label"], doc, rows)

    before = worlds["16-tag"]["total"]
    after = worlds["28-tag"]["total"]
    dilution = {
        "edges_before": before["candidate_edges"],
        "edges_after": after["candidate_edges"],
        "edges_added": after["candidate_edges"] - before["candidate_edges"],
        "edges_growth": _percent(
            after["candidate_edges"] - before["candidate_edges"],
            before["candidate_edges"]),
        "A_before": before["A_available"],
        "A_after": after["A_available"],
        "A_added": after["A_available"] - before["A_available"],
        "A_growth": _percent(
            after["A_available"] - before["A_available"], before["A_available"]),
        "K_before": before["K_available"],
        "K_after": after["K_available"],
        "K_added": after["K_available"] - before["K_available"],
        "K_growth": _percent(
            after["K_available"] - before["K_available"], before["K_available"]),
        "K_density_before": before["K_density"],
        "K_density_after": after["K_density"],
        "K_density_change": round(
            after["K_density"] - before["K_density"], 6),
        "headline": (
            "Candidate edges rose %d -> %d (+%.1f%%), A-available rows rose "
            "%d -> %d (+%.1f%%), but K-available rows rose only %d -> %d "
            "(+%.1f%%). K density fell from %.1f%% to %.1f%%."
            % (
                before["candidate_edges"], after["candidate_edges"],
                100 * _percent(
                    after["candidate_edges"] - before["candidate_edges"],
                    before["candidate_edges"]),
                before["A_available"], after["A_available"],
                100 * _percent(
                    after["A_available"] - before["A_available"],
                    before["A_available"]),
                before["K_available"], after["K_available"],
                100 * _percent(
                    after["K_available"] - before["K_available"],
                    before["K_available"]),
                100 * before["K_density"], 100 * after["K_density"],
            )
        ),
    }

    family16 = {row["label"]: row for row in worlds["16-tag"]["by_family"]}
    family28 = {row["label"]: row for row in worlds["28-tag"]["by_family"]}
    transition16 = {row["label"]: row for row in worlds["16-tag"]["by_transition"]}
    transition28 = {row["label"]: row for row in worlds["28-tag"]["by_transition"]}
    quartiles16 = {row["label"]: row for row in worlds["16-tag"]["by_U_quartile"]}
    quartiles28 = {row["label"]: row for row in worlds["28-tag"]["by_U_quartile"]}

    best28 = max(worlds["28-tag"]["per_seed"], key=lambda row: row["K_density"])

    findings = [
        dilution["headline"],
        (
            "The K supply is nearly constant by transition type as well: "
            "flip-P K rows %d -> %d while flip-P candidate edges %d -> %d; "
            "flip-Q K rows %d -> %d while flip-Q candidate edges %d -> %d."
            % (
                transition16["flip_p"]["K_available"],
                transition28["flip_p"]["K_available"],
                transition16["flip_p"]["candidate_edges"],
                transition28["flip_p"]["candidate_edges"],
                transition16["flip_q"]["K_available"],
                transition28["flip_q"]["K_available"],
                transition16["flip_q"]["candidate_edges"],
                transition28["flip_q"]["candidate_edges"],
            )
        ),
        (
            "The old-old edge family also dilutes: %d -> %d edges, but "
            "K-available rows %d -> %d and K density %.1f%% -> %.1f%%. "
            "Old-new is %.1f%% and new-new is %.1f%% K in the 28-tag world, "
            "so the new tags are not the weak family by themselves; support "
            "per possible pair is what fell."
            % (
                family16["old-old"]["candidate_edges"],
                family28["old-old"]["candidate_edges"],
                family16["old-old"]["K_available"],
                family28["old-old"]["K_available"],
                100 * family16["old-old"]["K_density"],
                100 * family28["old-old"]["K_density"],
                100 * family28["old-new"]["K_density"],
                100 * family28["new-new"]["K_density"],
            )
        ),
        (
            "The U gradient survives but does not rescue the numerator: "
            "Q4 K density is %.1f%% in the 16-tag world and %.1f%% in the "
            "28-tag world, while Q1 is %.1f%% and %.1f%%. High-U edges are "
            "still the best K carriers, but Q4 supplies about %d K rows per "
            "seed (%d/6), not 60 per seed. Selecting Q4 after seeing K would "
            "also be selection on the preflight quantity."
            % (
                100 * quartiles16["Q4"]["K_density"],
                100 * quartiles28["Q4"]["K_density"],
                100 * quartiles16["Q1"]["K_density"],
                100 * quartiles28["Q1"]["K_density"],
                round(quartiles28["Q4"]["K_available"] / 6),
                quartiles28["Q4"]["K_available"],
            )
        ),
        (
            "The 28-tag block's best seed has %d K rows out of %d edges "
            "(%.1f%%), needing %.1f%% for 60 and therefore missing by %d "
            "rows. Even its best seed does not reach the floor."
            % (
                best28["K_available"], best28["candidate_edges"],
                100 * best28["K_density"],
                100 * best28["K_density_needed_for_60"],
                best28["gap_to_60"],
            )
        ),
    ]

    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "scope": (
            "Two declared no-arm candidate universes: the fresh 16-tag block "
            "and the 28-tag larger-universe block. Candidate edges are the "
            "first-36-cycle, one-orientation streams. A and K are the 120-cycle "
            "no-arm A+K+ baseline flags. U is the cycle-36 directed strength. "
            "No treatment was applied."
        ),
        "definition": {
            "candidate_edges": "one-orientation candidate edges per seed",
            "A": "prediction path available at least once in the 120-cycle no-arm baseline",
            "K": "carrier path available at least once in the 120-cycle no-arm baseline",
            "K_density": "K-available candidate edges / candidate edges",
            "K_supply": "sum of K-available candidate-edge flags across the block",
            "U_quartile": "within-seed rank of cycle-36 U strength; Q1 lowest, Q4 highest",
        },
        "inputs": {
            spec["label"]: {
                "path": spec["path"].relative_to(ROOT).as_posix(),
                "sha256": _digest(spec["path"]),
            }
            for spec in WORLDS
        },
        "worlds": worlds,
        "dilution": dilution,
        "findings": findings,
        "limits": [
            "K is a no-arm availability flag over 120 cycles, not a treatment measurement or a K-cycle rate.",
            "U is measured at cycle 36; the K-U association has no identified direction.",
            "The two worlds differ in tag count and tag mapping; six seeds per world do not isolate tag count from mapping or cell composition.",
            "U quartiles are within-seed ranks, not absolute strength thresholds; the labels are not comparable across seeds as cut points.",
            "The near-constant K total is descriptive for these two blocks, not a conservation law.",
            "No target was selected, no threshold changed, no freeze or grant exists and no A1 cell ran.",
        ],
        "not_evidence": (
            "A descriptive comparison of existing no-arm candidate rows. It does "
            "not identify a cause, select a target, set a threshold, choose a "
            "redesign or park A1."
        ),
        "governance": {
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("record kind")
    if doc.get("id") != ID:
        found.append("record id")
    if doc.get("status") != STATUS:
        found.append("record status")
    if doc.get("governance") != {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none"}:
        found.append("governance changed")
    worlds = doc.get("worlds") or {}
    if set(worlds) != {"16-tag", "28-tag"}:
        found.append("world labels")
        return found
    for label, world in worlds.items():
        total = world.get("total") or {}
        rows = world.get("per_seed") or []
        edges = sum(row.get("candidate_edges", 0) for row in rows)
        if total.get("candidate_edges") != edges:
            found.append("%s seed edges do not sum" % label)
        for key in ("A_available", "K_available", "A_and_K"):
            if total.get(key) != sum(row.get(key, 0) for row in rows):
                found.append("%s %s does not sum" % (label, key))
        for bucket_key in ("by_family", "by_transition", "by_U_quartile"):
            buckets = world.get(bucket_key) or []
            if sum(row.get("candidate_edges", 0) for row in buckets) != edges:
                found.append("%s %s edges do not sum" % (label, bucket_key))
            if sum(row.get("K_available", 0) for row in buckets) != total.get("K_available"):
                found.append("%s %s K does not sum" % (label, bucket_key))
        for row in rows:
            if row.get("K_density") != _percent(
                    row.get("K_available", 0), row.get("candidate_edges", 0)):
                found.append("%s seed %s K density" % (label, row.get("label")))
    dilution = doc.get("dilution") or {}
    before = worlds["16-tag"]["total"]
    after = worlds["28-tag"]["total"]
    if dilution.get("edges_added") != (
            after["candidate_edges"] - before["candidate_edges"]):
        found.append("edge delta")
    if dilution.get("K_added") != after["K_available"] - before["K_available"]:
        found.append("K delta")
    if dilution.get("K_density_change") != round(
            after["K_density"] - before["K_density"], 6):
        found.append("K density delta")
    return found


def self_test() -> list[str]:
    found: list[str] = []
    if _family("amber>birch") != "old-old":
        found.append("old-old family")
    if _family("amber>tagaa") != "old-new":
        found.append("old-new family")
    if _family("tagaa>tagbb") != "new-new":
        found.append("new-new family")
    world = {
        "tag_to_cell": {
            "a": "p0q0", "b": "p1q0", "c": "p0q1", "d": "p1q1",
        }
    }
    if _cell_relation(world, "a>b") != "flip_p":
        found.append("flip-P relation")
    if _cell_relation(world, "a>c") != "flip_q":
        found.append("flip-Q relation")
    rows = [
        {"seed": 1, "edge": "e%d" % i, "U_strength": i}
        for i in range(10)
    ]
    _assign_quartiles(rows)
    if {row["U_quartile"] for row in rows} != {"Q1", "Q2", "Q3", "Q4"}:
        found.append("quartile assignment")
    if [row["U_quartile"] for row in rows] != sorted(
            row["U_quartile"] for row in rows):
        found.append("quartile order")
    if _percent(1, 0) != 0.0:
        found.append("zero denominator")
    return found


def render(doc: dict) -> str:
    before = doc["worlds"]["16-tag"]
    after = doc["worlds"]["28-tag"]
    dilution = doc["dilution"]
    lines = [
        "# A1 K dilution — more edges did not buy more K",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** It compares two no-arm candidate universes; "
        "it runs no cell, selects no target, sets no threshold and chooses no redesign.",
        "",
        "## Headline",
        "",
        "| World | Tags | Seeds | Candidate edges | A available | K available | A&K | K density |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for world in (before, after):
        total = world["total"]
        lines.append(
            "| %s | %d | %d | %d | %d | %d | %d | %.1f%% |" % (
                world["label"], world["tags"], len(world["seed_block"]),
                total["candidate_edges"], total["A_available"],
                total["K_available"], total["A_and_K"],
                100 * total["K_density"],
            )
        )
    lines += [
        "",
        "%s" % dilution["headline"],
        "",
        "The edge count is not the constraint. The block-level K supply is almost "
        "unchanged while the denominator grows, so the **same K is spread across "
        "more edges**. That is dilution, not a shortage of possible edges.",
        "",
        "## By seed",
        "",
        "| World | Seed | Candidate edges | A | K | A&K | K density | K needed for 60 | Gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for world in (before, after):
        for row in world["per_seed"]:
            lines.append(
                "| %s | `%d` | %d | %d | %d | %d | %.1f%% | %.1f%% | %d |" % (
                    world["label"], row["label"], row["candidate_edges"],
                    row["A_available"], row["K_available"], row["A_and_K"],
                    100 * row["K_density"],
                    100 * row["K_density_needed_for_60"], row["gap_to_60"],
                )
            )
    lines += [
        "",
        "The 28-tag block's K supply is **%d–%d rows** per seed, versus "
        "**%d–%d** in the 16-tag block. The larger block has more edges but not "
        "more K to distribute." % (
            min(row["K_available"] for row in after["per_seed"]),
            max(row["K_available"] for row in after["per_seed"]),
            min(row["K_available"] for row in before["per_seed"]),
            max(row["K_available"] for row in before["per_seed"]),
        ),
        "",
        "## K supply by transition type",
        "",
        "| Transition | 16-tag edges | 16-tag K | 28-tag edges | 28-tag K | 16-tag K density | 28-tag K density |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    t16 = {row["label"]: row for row in before["by_transition"]}
    t28 = {row["label"]: row for row in after["by_transition"]}
    for label in ("flip_p", "flip_q"):
        one, two = t16.get(label), t28.get(label)
        if not one or not two:
            continue
        lines.append(
            "| %s | %d | %d | %d | %d | %.1f%% | %.1f%% |" % (
                "flip-P" if label == "flip_p" else "flip-Q",
                one["candidate_edges"], one["K_available"],
                two["candidate_edges"], two["K_available"],
                100 * one["K_density"], 100 * two["K_density"],
            )
        )
    lines += [
        "",
        "The absolute K counts by transition type are nearly identical across the "
        "two worlds, while the edge counts roughly double. This is the clearest "
        "signature of a numerator that does not scale with the denominator.",
        "",
        "## Endpoint novelty",
        "",
        "| Family | 16-tag edges | 16-tag K | 16-tag K density | 28-tag edges | 28-tag K | 28-tag K density |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    f16 = {row["label"]: row for row in before["by_family"]}
    f28 = {row["label"]: row for row in after["by_family"]}
    for label in ("old-old", "old-new", "new-new"):
        one, two = f16.get(label), f28.get(label)
        if not one and not two:
            continue
        lines.append(
            "| %s | %s | %s | %s | %s | %s | %s |" % (
                label,
                one["candidate_edges"] if one else "—",
                one["K_available"] if one else "—",
                "%.1f%%" % (100 * one["K_density"]) if one else "—",
                two["candidate_edges"] if two else "—",
                two["K_available"] if two else "—",
                "%.1f%%" % (100 * two["K_density"]) if two else "—",
            )
        )
    lines += [
        "",
        "The **old-old** family is not protected by being the original vocabulary: "
        "its K density falls as well. In the 28-tag world the new-involving "
        "families are not worse than old-old; the loss is not “new tags are bad”. "
        "It is lower support for each possible pair.",
        "",
        "## U-strength quartiles",
        "",
        "U quartiles are assigned **within each seed** (Q1 lowest strength, Q4 "
        "highest), then pooled. They are rank bins, not common absolute cut points.",
        "",
        "| World | Quartile | U range | Edges | K available | K density |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for world in (before, after):
        for row in world["by_U_quartile"]:
            lines.append(
                "| %s | %s | %d–%d | %d | %d | %.1f%% |" % (
                    world["label"], row["label"], row["min_U_strength"],
                    row["max_U_strength"], row["candidate_edges"],
                    row["K_available"], 100 * row["K_density"],
                )
            )
    lines += [
        "",
        "The U gradient is real in both worlds, but it does not rescue the total: "
        "the 28-tag Q4 has 121 K rows across six seeds, about 20 per seed, not "
        "60 per seed; the lower quartiles carry most of the diluted denominator."
        " Selecting Q4 after seeing K would be selection on the preflight quantity.",
        "",
        "## What this changes",
        "",
    ]
    for finding in doc["findings"]:
        lines.append("- %s" % finding)
    lines += [
        "",
        "The redesign target is therefore **K-capable edges**, not independent "
        "edges. A larger universe that merely adds pairs without preserving K "
        "support repeats this failure.",
        "",
        "## Limits",
        "",
    ]
    for limit in doc["limits"]:
        lines.append("- %s" % limit)
    lines += [
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_k_dilution --check",
        "python -m benchmarks.a1_k_dilution --self-test",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def write() -> int:
    doc = build()
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(doc["dilution"]["headline"])
    return 0


def check() -> int:
    if not OUT_PATH.exists() or not PAGE_PATH.exists():
        print("FAIL: report artifact or page is missing")
        return 1
    found = problems(_load(OUT_PATH))
    if PAGE_PATH.read_text(encoding="utf-8") != render(_load(OUT_PATH)) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    doc = _load(OUT_PATH)
    print("A1 K dilution: clean; K %d -> %d, density %.1f%% -> %.1f%%" % (
        doc["dilution"]["K_before"], doc["dilution"]["K_after"],
        100 * doc["dilution"]["K_density_before"],
        100 * doc["dilution"]["K_density_after"]))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.check:
        return check()
    found = self_test()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 K dilution: self-test clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
