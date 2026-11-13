"""How much the served transition set turns over, and whether that tracks S_ever.

The Q4 campaign recorded every cycle's pre-cap universe in the engine's construction order and the
served window. Served transitions are the transition prefix of that list and never exceed the
20-slot transition allocation, so "the top-20 transition set" is not a proxy for the served
transitions in that cycle -- it is the same set. This module measures how that set changes between
consecutive cycles, decomposes the repeated slots into carried and returned edges, and reports the
rank association between per-seed turnover and S_ever.

``S_ever`` is the union of served *world* edges, not of every served row: the windows also carry
transitions among tags outside the world. So the measurement keeps three quantities apart -- all
served transition edges, those that are world edges, and ``S_ever`` -- and checks that
``S_ever = |top-20 union ∩ world| + served world cooccurrences`` (the second term is zero on this
campaign). The association is therefore constrained by construction but not identical: the
turnover counts non-world churn that ``S_ever`` cannot see.

Two disclosures frame it further:

- **Six seeds are six points.** The rank correlation is reported with its exact permutation
  distribution over all 720 orderings; it is a direction, not a result about the engine.
- **The union contains the outcome.** ``S_ever`` is a subset of the top-20 union, so a positive
  association is partly arithmetic; the page states which component is shared.

    ./.venv/bin/python -m benchmarks.transition_turnover --write
    ./.venv/bin/python -m benchmarks.transition_turnover --check
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.presence_construct_audit import _world_compositional_edges

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "transition_turnover.json"
PAGE = ROOT / "docs" / "TRANSITION-TURNOVER.md"
RUN = ROOT / "docs" / "presence_conversion_repair_run.json"
N3 = ROOT / "docs" / "presence_conversion_2_n3_tables.json"
KIND = "transition_turnover"
TOP = 20


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cycle_sets(cell: dict) -> list[tuple[int, list[tuple[str, str]]]]:
    """Each cycle's served transition set, as the transition prefix of the universe.

    The check is deliberately strict: if the served transitions were ever not the prefix, the
    top-20 label would be a description rather than the engine's own set, and the turnover would
    not be measuring what it says.
    """
    series = []
    for cycle in cell["cycles"]:
        edges = [tuple(edge.split(">")) for edge in cycle["universe"]["edges"]]
        relations = cycle["universe"]["relations"]
        if len(edges) != len(relations):
            raise ValueError("%d: the universe arrays disagree" % cell["seed"])
        transitions = [edge for edge, name in zip(edges, relations) if name == "t"]
        served = {tuple(edge) for edge in cycle["served"]}
        top = transitions[:TOP]
        if any(edge not in served for edge in top):
            raise ValueError("%d cycle %d: a top-%d transition is not served"
                             % (cell["seed"], cycle["cycle"], TOP))
        served_top = [edge for edge in transitions if edge in served]
        if served_top != top:
            raise ValueError("%d cycle %d: served transitions are not the transition prefix"
                             % (cell["seed"], cycle["cycle"]))
        if len(served_top) != min(TOP, len(transitions)):
            raise ValueError("%d cycle %d: %d transitions served of %d available"
                             % (cell["seed"], cycle["cycle"], len(served_top), len(transitions)))
        series.append((cycle["cycle"], top))
    return series


def turnover_rows(series: list[tuple[int, list[tuple[str, str]]]],
                  world: set[tuple[str, str]]) -> tuple[list[dict], set, int, int, int]:
    """Per cycle: new, carried, returned, removed and Jaccard against the previous set.

    ``carried`` is an edge that stays from the previous cycle; ``returned`` is an edge seen
    earlier but absent from the previous cycle. Both are repeats, and the identity
    ``slots = union + carried + returned`` is checked rather than assumed. ``first_seen_world``
    counts entries that are world edges, whose sum is ``S_ever`` by construction.
    """
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    carried = returned = world_seen = 0
    for index, (cycle_no, top) in enumerate(series):
        current = set(top)
        previous = set(series[index - 1][1]) if index else set()
        keep = current & previous
        earlier = current & (seen - previous)
        new = current - previous
        first = current - seen
        if new != first | earlier:
            raise ValueError("cycle %d: the new set does not decompose" % cycle_no)
        rows.append({
            "cycle": cycle_no,
            "size": len(current),
            "new": len(new),
            "first_seen": len(first),
            "first_seen_world": len(first & world),
            "carried": len(keep),
            "returned": len(earlier),
            "removed": len(previous - current),
            "jaccard": round(len(keep) / len(current | previous), 6)
            if current | previous else None,
        })
        seen |= current
        carried += len(keep)
        returned += len(earlier)
        world_seen += len(first & world)
    return rows, seen, carried, returned, world_seen


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index
        while end + 1 < len(order) and values[order[end + 1]] == values[order[index]]:
            end += 1
        rank = (index + end) / 2.0 + 1.0
        for position in range(index, end + 1):
            ranks[order[position]] = rank
        index = end + 1
    return ranks


def spearman(x: list[float], y: list[float]) -> float:
    rx, ry = _ranks(x), _ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    numerator = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    denominator = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    if not denominator:
        raise ValueError("a constant series has no rank correlation")
    return round(numerator / denominator, 6)


def permutation_p(x: list[float], y: list[float]) -> tuple[int, int]:
    """Two-sided exact permutation count over every ordering of ``y``."""
    observed = abs(spearman(x, y))
    hits = total = 0
    for ordering in itertools.permutations(y):
        total += 1
        if abs(spearman(x, list(ordering))) + 1e-12 >= observed:
            hits += 1
    return hits, total


def _association(x: list[float], y: list[float]) -> dict:
    hits, total = permutation_p(x, y)
    return {"spearman": spearman(x, y), "permutation_p": round(hits / total, 6),
            "hits": hits, "permutations": total}


def analyse(run: dict, n3: dict) -> dict:
    stage = {row["seed"]: row for row in run["stage_table"]}
    cells = {cell["seed"]: cell for cell in n3["campaign_cells"]}
    if sorted(stage) != sorted(cells):
        raise ValueError("the campaign tables and the stage table name different seeds")
    records = []
    for seed in sorted(stage):
        cell = cells[seed]
        world = _world_compositional_edges(
            generate_compositional_world(seed=seed, cycles=cell["cycles_recorded"]))
        series = cycle_sets(cell)
        rows, union, carried, returned, world_seen = turnover_rows(series, world)
        slots = sum(row["size"] for row in rows)
        if slots != len(union) + carried + returned:
            raise ValueError("%d: slots do not decompose into union and repeats" % seed)
        if world_seen != sum(row["first_seen_world"] for row in rows):
            raise ValueError("%d: the world entries do not sum" % seed)
        served = set()
        for cycle in cell["cycles"]:
            served |= {tuple(edge) for edge in cycle["served"]}
        s_ever = int(stage[seed]["served_ever"])
        served_world = served & world
        if len(served_world) != s_ever:
            raise ValueError("%d: %d served world edges, the stage table says %d"
                             % (seed, len(served_world), s_ever))
        union_world = union & world
        if not union_world <= served_world:
            raise ValueError("%d: a world transition-set edge is outside the served union" % seed)
        if world_seen != len(union_world):
            raise ValueError("%d: world first appearances do not sum to the world union" % seed)
        world_cooccurrence = served_world - union_world
        if len(union_world) + len(world_cooccurrence) != s_ever:
            raise ValueError("%d: the served world union does not decompose" % seed)
        new = [row["new"] for row in rows[1:]]
        new_world = [row["first_seen_world"] for row in rows[1:]]
        jaccard = [row["jaccard"] for row in rows[1:] if row["jaccard"] is not None]
        records.append({
            "seed": seed,
            "cycles": len(rows),
            "transition_slots": slots,
            "top20_union": len(union),
            "top20_union_world": len(union_world),
            "top20_union_outside_world": len(union) - len(union_world),
            "carried": carried,
            "returned": returned,
            "mean_new_per_cycle": round(sum(new) / len(new), 4),
            "mean_new_world_per_cycle": round(sum(new_world) / len(new_world), 4),
            "median_new_per_cycle": sorted(new)[len(new) // 2],
            "min_new_per_cycle": min(new),
            "max_new_per_cycle": max(new),
            "mean_jaccard": round(sum(jaccard) / len(jaccard), 4),
            "cycles_with_no_turnover": sum(1 for row in rows[1:]
                                           if row["new"] == 0 and row["removed"] == 0),
            "first_transition_cycle": next((row["cycle"] for row in rows if row["size"]),
                                           None),
            "s_ever": s_ever,
            "world_cooccurrence_served": len(world_cooccurrence),
            "turnover": rows,
        })
    s_ever = [record["s_ever"] for record in records]
    mean_new = [record["mean_new_per_cycle"] for record in records]
    world_new = [record["mean_new_world_per_cycle"] for record in records]
    union = [record["top20_union"] for record in records]
    return {
        "kind": KIND,
        "not_a_result": True,
        "question": ("How much does the served top-20 transition set change each cycle, and does "
                     "its per-seed turnover rank-associate with S_ever?"),
        "definition": ("Each cycle's top-20 transition set is the served transition prefix of the "
                       "recorded universe. `new` is the set difference from the previous cycle, "
                       "`carried` an edge kept from it, `returned` an edge seen earlier but absent "
                       "from it, `removed` an edge dropped, and `jaccard` their overlap share. "
                       "`first_seen_world` counts entries that are world edges; its sum over the "
                       "run is `S_ever`."),
        "source": {
            "served_and_universe": "docs/presence_conversion_2_n3_tables.json",
            "s_ever": "docs/presence_conversion_repair_run.json",
            "world": "generate_compositional_world(seed=, cycles=120), deterministic",
        },
        "engine_version": run.get("engine_version"),
        "run_engine_version": run.get("engine_version"),
        "top": TOP,
        "seeds": records,
        "associations": {
            "n": len(records),
            "mean_new_vs_s_ever": _association(mean_new, s_ever),
            "mean_new_world_vs_s_ever": _association(world_new, s_ever),
            "top20_union_vs_s_ever": _association(union, s_ever),
            "s_ever": s_ever,
            "mean_new": mean_new,
            "mean_new_world": world_new,
            "top20_union": union,
        },
        "summary": {
            "seeds": len(records),
            "transition_slots": sum(record["transition_slots"] for record in records),
            "top20_union": sum(record["top20_union"] for record in records),
            "top20_union_world": sum(record["top20_union_world"] for record in records),
            "top20_union_outside_world": sum(record["top20_union_outside_world"]
                                             for record in records),
            "carried": sum(record["carried"] for record in records),
            "returned": sum(record["returned"] for record in records),
            "s_ever": sum(s_ever),
            "world_cooccurrence_served": sum(record["world_cooccurrence_served"]
                                             for record in records),
            "min_mean_new": min(mean_new),
            "max_mean_new": max(mean_new),
        },
        "not_evidence": ("A derived table of one campaign on six seeds, one world family and one "
                         "cap. The rank association is six points, and S_ever is a subset of the "
                         "turnover union."),
    }


def build() -> dict:
    return engine_stamp.stamp(analyse(_load(RUN), _load(N3)))


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("artifact kind")
    if art.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    if art.get("top") != TOP:
        found.append("the top-k does not match the module")
    run, n3 = _load(RUN), _load(N3)
    if art.get("run_engine_version") != run.get("engine_version"):
        found.append("the run's engine version does not match the stage table")
    try:
        derived = analyse(run, n3)
    except (KeyError, ValueError) as error:
        found.append("the committed inputs do not derive: %s" % error)
        return found
    if [record.get("seed") for record in art.get("seeds") or []] != \
            [record["seed"] for record in derived["seeds"]]:
        found.append("the seeds do not match the campaign tables")
        return found
    for record in art["seeds"]:
        seed = record["seed"]
        expected = next(row for row in derived["seeds"] if row["seed"] == seed)
        for key in ("cycles", "transition_slots", "top20_union", "top20_union_world",
                    "top20_union_outside_world", "carried", "returned",
                    "mean_new_per_cycle", "mean_new_world_per_cycle",
                    "median_new_per_cycle", "min_new_per_cycle", "max_new_per_cycle",
                    "mean_jaccard", "cycles_with_no_turnover", "first_transition_cycle",
                    "s_ever", "world_cooccurrence_served", "turnover"):
            if record.get(key) != expected[key]:
                found.append("%d: %s does not match the recomputation" % (seed, key))
    if art.get("associations") != derived["associations"]:
        found.append("the associations do not match the recomputation")
    if art.get("summary") != derived["summary"]:
        found.append("the summary does not match the recomputation")
    return found


def render(art: dict) -> str:
    assoc = art["associations"]
    summary = art["summary"]
    lines = [
        "# Transition-set turnover and `S_ever`",
        "",
        "Generated from `docs/transition_turnover.json` by "
        "`python -m benchmarks.transition_turnover --write`. Do not edit by hand.",
        "",
        "**Not a result artifact.** It is a derived table of the Q4 campaign's six observer-on "
        "cells. The served transitions are the transition prefix of the recorded universe, so the "
        "top-20 set is the engine's own served set, not a reconstruction; nothing here re-runs a "
        "cell. The campaign ran on 0.14.0 at cap 40; this table was derived from the committed "
        "records on 0.15.0.",
        "",
        "## What is measured",
        "",
        "For each cycle: `new` edges entering the top-20 set from the previous cycle, `carried` "
        "edges kept from it, `returned` edges seen earlier but not in the previous cycle, "
        "`removed` edges dropped, and `jaccard` as the overlap share. `first_seen` counts edges "
        "entering the union, so the identity `slots = union + carried + returned` holds per seed. "
        "`first_seen_world` counts entries that are world edges; their sum is `S_ever`, the union "
        "of served world edges.",
        "",
        "## Per seed",
        "",
        "| Seed | Slots | Union | Union in world | Union outside world | Carried | Returned | "
        "New/cycle mean | World new/cycle | Median | Max | Mean Jaccard | No-turnover cycles | "
        "`S_ever` |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | "
        "---: | ---: |",
    ]
    for record in art["seeds"]:
        lines.append("| %d | %d | %d | %d | %d | %d | %d | %.2f | %.2f | %d | %d | %.2f | %d | %d |" % (
            record["seed"], record["transition_slots"], record["top20_union"],
            record["top20_union_world"], record["top20_union_outside_world"],
            record["carried"], record["returned"], record["mean_new_per_cycle"],
            record["mean_new_world_per_cycle"], record["median_new_per_cycle"],
            record["max_new_per_cycle"], record["mean_jaccard"],
            record["cycles_with_no_turnover"], record["s_ever"]))
    lines.append("| **total** | %d | %d | %d | %d | %d | %d | %.2f-%.2f | | | | | | %d |" % (
        summary["transition_slots"], summary["top20_union"], summary["top20_union_world"],
        summary["top20_union_outside_world"], summary["carried"], summary["returned"],
        summary["min_mean_new"], summary["max_mean_new"], summary["s_ever"]))
    lines += [
        "",
        "Every cycle has 20 served transitions once 20 exist; the first cycle with a served "
        "transition is %s. The union exceeds the slot count only through repeats; it exceeds "
        "`S_ever` because most served transitions are not world edges." % ", ".join(
            "%d: %s" % (record["seed"], record["first_transition_cycle"])
            for record in art["seeds"]),
        "",
        "## Across the six seeds",
        "",
        "| Predictor | Outcome | Spearman rho | Exact permutation p (two-sided, 720) |",
        "| --- | --- | ---: | ---: |",
    ]
    for key, label in (
            ("mean_new_vs_s_ever", "Mean new edges per cycle (all served transitions)"),
            ("mean_new_world_vs_s_ever", "Mean new world edges per cycle"),
            ("top20_union_vs_s_ever", "Top-20 union size (all served transitions)")):
        row = assoc[key]
        lines.append("| %s | `S_ever` | %+.3f | %.4f |" % (
            label, row["spearman"], row["permutation_p"]))
    lines += [
        "",
        "Six points give a coarse permutation distribution: with n = 6 the smallest two-sided "
        "p is 2/720. The second row is close to an identity, because the world entries summed "
        "over the run are exactly `S_ever`; the first and third are the non-arithmetic readings, "
        "and even they are constrained because `S_ever` is a subset of the union.",
        "",
        "## The arithmetic, stated",
        "",
        "`S_ever` = |top-20 union ∩ world| + served world cooccurrences. Across the six seeds "
        "that is %d = %d + %d: every served world edge is a transition, and %d of the %d union "
        "edges are not world edges. Turnover therefore counts churn that `S_ever` cannot see, "
        "while `S_ever` remains a subset of what the union has accumulated." % (
            summary["s_ever"], summary["top20_union_world"],
            summary["world_cooccurrence_served"], summary["top20_union_outside_world"],
            summary["top20_union"]),
        "",
        "## Per-cycle turnover",
        "",
    ]
    for record in art["seeds"]:
        lines += ["### Seed %d" % record["seed"], "",
                  "| Cycle | Size | New | New world | Carried | Returned | Removed | Jaccard |",
                  "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for row in record["turnover"]:
            lines.append("| %d | %d | %d | %d | %d | %d | %d | %s |" % (
                row["cycle"], row["size"], row["new"], row["first_seen_world"],
                row["carried"], row["returned"], row["removed"],
                "-" if row["jaccard"] is None else "%.2f" % row["jaccard"]))
        lines.append("")
    lines += [
        "## What this licenses",
        "",
        "- **The set turns over slowly.** Mean new edges per cycle is %.2f-%.2f across the six "
        "seeds, and each seed's top-20 union reaches %d-%d edges; across the six seeds %d of "
        "the %d union edges are world edges." % (
            summary["min_mean_new"], summary["max_mean_new"],
            min(record["top20_union"] for record in art["seeds"]),
            max(record["top20_union"] for record in art["seeds"]),
            summary["top20_union_world"], summary["top20_union"]),
        "- **Most slots are repeats.** %d of %d transition slots are repeats: %d carried from "
        "the previous cycle and %d returned after an absence." % (
            summary["carried"] + summary["returned"], summary["transition_slots"],
            summary["carried"], summary["returned"]),
        "- **The rank association with `S_ever` is reported, not established.** With six seeds "
        "and a shared set, the direction cannot separate turnover from the union arithmetic.",
        "",
        "## What it does not license",
        "",
        "- Not a mechanism and not a cause: turnover does not explain why an edge is ranked, and "
        "`S_ever` is a subset of the turnover union by construction.",
        "- Not a result about the engine: one world family, one cap, six seeds, one build, and no "
        "preregistration.",
        "- Not a prediction about cap 112: the registered block is the place to test whether a "
        "larger transition budget changes this set.",
        "",
    ]
    return "\n".join(lines)


def check() -> int:
    if not ARTIFACT.exists():
        print("FAIL: no artifact; run --write")
        return 1
    art = _load(ARTIFACT)
    found = problems(art)
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(art):
        found.append("the page is stale against the artifact")
    for problem in found:
        print("FAIL:", problem)
    if not found:
        summary = art["summary"]
        print("transition turnover: %d slots, %d union (%d world), mean new/cycle %.2f-%.2f, "
              "rho(new, S_ever) %+.3f"
              % (summary["transition_slots"], summary["top20_union"],
                 summary["top20_union_world"], summary["min_mean_new"],
                 summary["max_mean_new"],
                 art["associations"]["mean_new_vs_s_ever"]["spearman"]))
    return 1 if found else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        art = build()
        ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
        PAGE.write_text(render(art), encoding="utf-8")
        print("wrote %s and %s" % (ARTIFACT.relative_to(ROOT).as_posix(), PAGE.relative_to(ROOT).as_posix()))
        return 0
    if args.check or not argv:
        return check()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
