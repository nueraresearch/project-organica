"""Per-cell N3 tables: allocation and rank, read from the observer's own universe records.

N3 requires two things of the campaign's parts: every served row carries whether it is a
transition or a cooccurrence, and every cycle records how many of each were served, with the
two counts summing to the window. The observer already records the pre-cap universe (rank,
edge, relation, strength, support) and one allocation row per cycle, so this module turns
those records into a per-cell table rather than a second measurement.

What it writes is **not a campaign result**. ``docs/presence_conversion_2_n3_tables.json``
holds the twelve frozen design cells, and for the six observer-on cells it now carries the
campaign's own universe and allocation records, persisted from the run's parts so the rank
tables are readable from the repository rather than only from ``.scratch``. The six
observer-off cells record no universe by construction and therefore carry counts only. The
campaign's own artifact remains ``docs/presence_conversion_repair_run.json``, which only a
runner may write.

    ./.venv/bin/python -m benchmarks.presence_conversion_repair_n3 --write
    ./.venv/bin/python -m benchmarks.presence_conversion_repair_n3 --check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks import presence_conversion_repair_observer as observer
from benchmarks.presence_construct_audit import _digest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "presence_conversion_2_n3_tables.json"
PAGE = ROOT / "docs" / "PRESENCE-CONVERSION-2-N3-TABLES.md"
PREREG = ROOT / "docs" / "presence_conversion_repair_prereg.json"
RUN = ROOT / "docs" / "presence_conversion_repair_run.json"
PARTS = ROOT / ".scratch" / "presence_repair" / "parts"
RELATION_CODE = {"transition": "t", "cooccurrence": "c"}
KIND = "presence_conversion_n3_tables"
RELATIONS = ("transition", "cooccurrence")
#: Fixture settings the pre-run artifact is built from: the shipped setting and the far corner
#: of the widened N2 fixture, so the table shape is exercised at two caps without a grant.
CASES = ((observer.FIXTURE_SEED, 40), (observer.SECOND_SEED, 112))


def _design_cells() -> list[dict]:
    """The twelve frozen cells, joined to the campaign's own rows when the block has run."""
    design = json.loads(PREREG.read_text(encoding="utf-8"))["design"]
    run = json.loads(RUN.read_text(encoding="utf-8")) if RUN.exists() else None
    by_key = {(cell["seed"], cell["arm"]): cell for cell in (run or {}).get("cells", [])}
    cells = []
    for seed in design["seeds"]:
        for arm in design["arms"]:
            cell = {"seed": seed, "arm": arm, "state": "not run",
                    "rank_table": "campaign" if arm == "on" else "none (observer off)"}
            got = by_key.get((seed, arm))
            if got:
                cell.update({"state": "run", "present": got["present"],
                             "s_ever": got["s_ever"], "a_w": got["a_w"],
                             "served_fingerprint": got["served_fingerprint"]})
            cells.append(cell)
    return cells


def cell_table(record: dict, seed: int, cap: int) -> dict:
    """One cell's N3 table, derived only from what the observer recorded."""
    windows = record.get("windows") or []
    universe = record.get("universe") or []
    allocation = record.get("allocation") or []
    if not (len(windows) == len(universe) == len(allocation)):
        raise ValueError("the record has %d windows, %d universes, %d allocations"
                         % (len(windows), len(universe), len(allocation)))
    cycles, problems = [], []
    served_total = universe_total = 0
    relation_counts = {name: 0 for name in RELATIONS}
    served_ranks: list[int] = []
    for cycle_no, (window, cycle_rows, counts) in enumerate(
            zip(windows, universe, allocation), start=1):
        served = {tuple(edge) for edge in window}
        rows = []
        for row in cycle_rows:
            edge = tuple(row["edge"])
            is_served = edge in served
            rows.append({"rank": row["rank"], "edge": list(edge), "relation": row["relation"],
                         "strength": row["strength"], "support": row["support"],
                         "served": is_served})
            if is_served:
                served_total += 1
                served_ranks.append(row["rank"])
                relation_counts[row["relation"]] = relation_counts.get(row["relation"], 0) + 1
        universe_total += len(rows)
        served_here = sum(1 for row in rows if row["served"])
        missing = len(served - {tuple(row["edge"]) for row in rows})
        if missing:
            problems.append("cycle %d: %d served edge(s) absent from the universe"
                            % (cycle_no, missing))
        if not counts.get("sum_matches"):
            problems.append("cycle %d: the allocation counts do not sum to the window" % cycle_no)
        if counts.get("served") != served_here:
            problems.append("cycle %d: allocation served %r, table has %d served rows"
                            % (cycle_no, counts.get("served"), served_here))
        cycles.append({"cycle": cycle_no, "allocation": counts, "rows": rows})
    rank_range = [min(served_ranks), max(served_ranks)] if served_ranks else None
    return {
        "seed": seed,
        "cap": cap,
        "arm": record.get("arm"),
        "cycles_recorded": len(cycles),
        "served_rows": served_total,
        "universe_rows": universe_total,
        "rank_range_of_served": rank_range,
        "relations_served": relation_counts,
        "unknown_relation_served": relation_counts.get("unknown", 0),
        "problems": problems,
        "cycles": cycles,
    }


def campaign_cell(record: dict, seed: int) -> dict:
    """One observer-on campaign cell, in a compact encoding of the recorded universe.

    The encoding is structural, not a summary: `universe.edges` is the engine's construction
    order, so a row's rank is its position; `relations` is one code per row; `strength` is the
    recorded value rounded to six places; and `served` is the served window in its own order.
    `support` is `None` in every recorded row, so it is not stored -- and a record where it is
    not `None` is refused rather than silently dropped.
    """
    windows = record.get("windows") or []
    universe = record.get("universe") or []
    allocation = record.get("allocation") or []
    if not windows:
        raise ValueError("%d: the observer-on part records no universe" % seed)
    if not (len(windows) == len(universe) == len(allocation)):
        raise ValueError("%d: %d windows, %d universes, %d allocations"
                         % (seed, len(windows), len(universe), len(allocation)))
    cycles = []
    served_total = universe_total = 0
    served_ranks: list[int] = []
    for cycle_no, (window, rows, counts) in enumerate(zip(windows, universe, allocation), start=1):
        if any(int(row["rank"]) != index for index, row in enumerate(rows, start=1)):
            raise ValueError("%d cycle %d: a rank is not the row's position" % (seed, cycle_no))
        if any(row.get("support") is not None for row in rows):
            raise ValueError("%d cycle %d: support is populated; persist it" % (seed, cycle_no))
        relations = [RELATION_CODE.get(row["relation"], str(row["relation"])) for row in rows]
        if any(code not in ("t", "c") for code in relations):
            raise ValueError("%d cycle %d: an unlabelled relation" % (seed, cycle_no))
        rank_of = {tuple(row["edge"]): int(row["rank"]) for row in rows}
        for edge in window:
            served_ranks.append(rank_of[tuple(edge)])
        cycles.append({
            "cycle": cycle_no,
            "allocation": dict(counts),
            "served": [[str(edge[0]), str(edge[1])] for edge in window],
            "universe": {
                "edges": ["%s>%s" % (row["edge"][0], row["edge"][1]) for row in rows],
                "relations": relations,
                "strength": [round(float(row["strength"]), 6) for row in rows],
            },
        })
        served_total += len(window)
        universe_total += len(rows)
    return {
        "seed": seed, "arm": "on", "cap": int(record.get("cap") or 40),
        "cycles_recorded": len(cycles), "served_rows": served_total,
        "universe_rows": universe_total,
        "rank_range_of_served": [min(served_ranks), max(served_ranks)] if served_ranks else None,
        "encoding": {"rank": "1-based position in `universe.edges`",
                     "relations": "t = transition, c = cooccurrence",
                     "strength": "rounded to 6 decimal places",
                     "support": "None in every recorded row, so not stored",
                     "served": "the served window, in the order the engine returned it"},
        "cycles": cycles,
    }


def _campaign_cells() -> list[dict]:
    design = json.loads(PREREG.read_text(encoding="utf-8"))["design"]
    cells = []
    for seed in design["seeds"]:
        path = PARTS / ("%d-on.json" % seed)
        if not path.exists():
            raise FileNotFoundError("missing on-arm part %s; run --measure first" % path.name)
        cells.append(campaign_cell(json.loads(path.read_text(encoding="utf-8")), seed))
    return cells


def _campaign_problems(art: dict, run: dict) -> list[str]:
    """The campaign tables must reproduce the run: order, coverage and fingerprint."""
    found: list[str] = []
    cells = art.get("campaign_cells") or []
    on_seeds = sorted(cell["seed"] for cell in art.get("design_cells") or []
                      if cell.get("arm") == "on")
    if sorted(cell["seed"] for cell in cells) != on_seeds:
        found.append("the campaign tables do not cover exactly the observer-on cells")
    by_key = {(cell["seed"], cell["arm"]): cell for cell in run.get("cells", [])}
    for cell in cells:
        got = by_key.get((cell["seed"], cell["arm"]))
        label = "%d/%s" % (cell["seed"], cell["arm"])
        if got is None:
            found.append("%s: no run cell" % label)
            continue
        if cell.get("cycles_recorded") != got.get("cycles"):
            found.append("%s: %r cycles recorded, the run has %r"
                         % (label, cell.get("cycles_recorded"), got.get("cycles")))
        served: list[tuple[str, str]] = []
        for cycle in cell.get("cycles") or []:
            edges = [tuple(edge) for edge in cycle.get("served") or []]
            row = cycle.get("universe") or {}
            universe = [str(edge) for edge in row.get("edges") or []]
            relations = row.get("relations") or []
            where = "%s cycle %s" % (label, cycle.get("cycle"))
            if len(set(universe)) != len(universe):
                found.append("%s: a duplicate universe edge" % where)
            if len(relations) != len(universe) or len(row.get("strength") or []) != len(universe):
                found.append("%s: the parallel arrays disagree" % where)
            if not {"%s>%s" % edge for edge in edges} <= set(universe):
                found.append("%s: a served edge is absent from the universe" % where)
            if (cycle.get("allocation") or {}).get("served") != len(edges):
                found.append("%s: the allocation disagrees with the served list" % where)
            if not (cycle.get("allocation") or {}).get("sum_matches"):
                found.append("%s: the counts do not sum" % where)
            served.extend(edges)
        if _digest(served) != got.get("served_fingerprint"):
            found.append("%s: the persisted served order does not reproduce the run's "
                         "fingerprint" % label)
    return found


def build() -> dict:
    cells = []
    for seed, cap in CASES:
        arms = observer.fixture(seed=seed, cap=cap)
        cells.append(cell_table(arms["on"], seed=seed, cap=cap))
    campaign = _campaign_cells() if RUN.exists() else []
    return engine_stamp.stamp({
        "kind": KIND,
        "not_a_result": True,
        "source": ("benchmarks.presence_conversion_repair_observer.fixture, %d cycles, "
                   "observer-on arm, plus the campaign's six observer-on parts"
                   % observer.FIXTURE_CYCLES),
        "note": ("The twelve design cells carry the campaign's own per-cell counts; the six "
                 "observer-on cells carry their universe and allocation records in "
                 "`campaign_cells`, and the six observer-off cells record no universe by "
                 "construction. This is a derived table, not the result artifact."),
        "design_cells": _design_cells(),
        "campaign_cells": campaign,
        "fixture_cells": cells,
    })


BANDS = ((1, 10), (11, 20), (21, 40), (41, 80), (81, 112))


def _band(rank: int) -> str:
    for low, high in BANDS:
        if low <= rank <= high:
            return "%d-%d" % (low, high)
    return "outside"


def cycle_rows(cycle: dict) -> list[dict]:
    """One row per candidate, in rank order, from either table shape.

    Fixture cells store explicit `rows`; campaign cells store the compact parallel arrays
    (`universe.edges` / `relations` / `served`), where a row's rank is its 1-based position.
    Both shapes feed the same band table, so the two can be read side by side.
    """
    if "rows" in cycle:
        return cycle["rows"]
    universe = cycle.get("universe") or {}
    served = {tuple(edge) for edge in cycle.get("served") or []}
    rows = []
    for index, (edge, code) in enumerate(zip(universe.get("edges") or [],
                                             universe.get("relations") or []), start=1):
        source, target = str(edge).split(">")
        rows.append({"rank": index, "edge": [source, target],
                     "relation": {"t": "transition", "c": "cooccurrence"}.get(code, code),
                     "served": (source, target) in served})
    return rows


def band_breakdown(cell: dict) -> list[dict]:
    """Per cycle: served transitions and cooccurrences in each rank band.

    Only served rows are counted. The bands are fixed so the two fixture cells can be read
    side by side, and a rank above the shipped cap still lands in a named band rather than
    being dropped.
    """
    table = []
    for cycle in cell["cycles"]:
        bands = {label: {"transition": 0, "cooccurrence": 0}
                 for label in [("%d-%d" % pair) for pair in BANDS] + ["outside"]}
        for row in cycle_rows(cycle):
            if not row["served"]:
                continue
            bands[_band(row["rank"])][row["relation"]] += 1
        table.append({"cycle": cycle["cycle"], "bands": bands})
    return table


def band_totals(cell: dict) -> dict:
    totals = {label: {"transition": 0, "cooccurrence": 0}
              for label in [("%d-%d" % pair) for pair in BANDS] + ["outside"]}
    for cycle in band_breakdown(cell):
        for label, counts in cycle["bands"].items():
            for relation in ("transition", "cooccurrence"):
                totals[label][relation] += counts[relation]
    return totals


def band_table(lines: list[str], cell: dict, title: str, labels: list[str]) -> list[str]:
    """One per-cycle band table, in the one format both cell shapes render to."""
    lines += ["### %s" % title, "",
              "| Cycle | %s |" % " | ".join(labels),
              "| ---: | %s |" % " | ".join("---:" for _ in labels)]
    for cycle in band_breakdown(cell):
        lines.append("| %d | %s |" % (cycle["cycle"], " | ".join(
            "%d/%d" % (cycle["bands"][label]["transition"],
                       cycle["bands"][label]["cooccurrence"]) for label in labels)))
    totals = band_totals(cell)
    lines.append("| **All** | %s |" % " | ".join(
        "**%d/%d**" % (totals[label]["transition"], totals[label]["cooccurrence"])
        for label in labels))
    lines.append("")
    return lines


def render_page(art: dict) -> str:
    lines = [
        "# PRESENCE-CONVERSION-2 \u2014 per-cell N3 allocation and rank tables",
        "",
        "Generated from `docs/presence_conversion_2_n3_tables.json` by "
        "`python -m benchmarks.presence_conversion_repair_n3 --write`. Do not edit by hand.",
        "",
        "**Not a result artifact.** The twelve design cells carry the campaign's own per-cell "
        "counts, and the six observer-on cells carry their universe and allocation records in "
        "`campaign_cells`; the two fixture cells are kept as the instrument's fixture record. The "
        "file is marked `not_a_result` because the result artifact is "
        "`docs/presence_conversion_repair_run.json`.",
        "",
        "## Design cells",
        "",
        "| Seed | Arm | State | Present | S_ever | A_W | Rank table |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for cell in art["design_cells"]:
        lines.append("| %d | %s | %s | %s | %s | %s | %s |"
                     % (cell["seed"], cell["arm"], cell["state"],
                        cell.get("present", "-"), cell.get("s_ever", "-"),
                        cell.get("a_w", "-"), cell.get("rank_table", "-")))
    lines += ["", "## Campaign cells", "",
              "Each observer-on cell's universe and allocation record is in "
              "`campaign_cells[].cycles[]`: `universe.edges` in the engine's construction order "
              "(a row's rank is its 1-based position), `universe.relations` (`t`/`c`), "
              "`universe.strength`, the per-cycle `allocation`, and the `served` window in order. "
              "The six observer-off cells record no universe by construction, so they carry "
              "counts only rather than an empty table.", ""]
    campaign = art.get("campaign_cells") or []
    if campaign:
        lines += ["| Seed | Cycles | Served rows | Universe rows | Served rank range |",
                  "| ---: | ---: | ---: | ---: | --- |"]
        for cell in campaign:
            ranks = cell.get("rank_range_of_served")
            lines.append("| %d | %d | %d | %d | %s |"
                         % (cell["seed"], cell["cycles_recorded"], cell["served_rows"],
                            cell["universe_rows"], "%d-%d" % tuple(ranks) if ranks else "none"))
        lines.append("")
    lines += ["", "## Fixture cells", "",
              "| Seed | Cap | Cycles | Served rows | Universe rows | Served rank range | Transitions | Cooccurrences |",
              "| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |"]
    for cell in art["fixture_cells"]:
        ranks = cell["rank_range_of_served"]
        lines.append("| %d | %d | %d | %d | %d | %s | %d | %d |"
                     % (cell["seed"], cell["cap"], cell["cycles_recorded"], cell["served_rows"],
                        cell["universe_rows"], "%d-%d" % tuple(ranks) if ranks else "none",
                        cell["relations_served"].get("transition", 0),
                        cell["relations_served"].get("cooccurrence", 0)))
    lines += ["", "Each fixture cell's full rank table \u2014 one row per constructed candidate with "
              "its rank in the engine's order, edge, relation, strength, support and whether it "
              "was served \u2014 is in the JSON artifact's `fixture_cells[].cycles[].rows`.", ""]
    lines += ["## Relation mix per cycle and rank band", "",
              "Served rows only, as `transitions/cooccurrences`. The same bands are used for the "
              "two fixture cells and the six campaign cells, so a campaign cycle and a fixture "
              "cycle can be read side by side; a rank above the shipped cap still has a named "
              "band.", ""]
    labels = [("%d-%d" % pair) for pair in BANDS] + ["outside"]
    for cell in art["fixture_cells"]:
        lines = band_table(lines, cell, "Seed %d, cap %d" % (cell["seed"], cell["cap"]), labels)
    if art.get("campaign_cells"):
        lines += ["### Campaign cells", "",
                  "One table per observer-on cell. The rank is the row's 1-based position in that "
                  "cycle's `universe.edges`, the same field the fixture tables read.", ""]
        for cell in art["campaign_cells"]:
            lines = band_table(lines, cell, "Campaign seed %d" % cell["seed"], labels)
    lines += ["## What the table checks", "",
              "- every served edge appears in the universe with `served: true`;",
              "- every cycle's allocation counts sum to the served window;",
              "- every served row carries `transition` or `cooccurrence`, never `unknown`;",
              "- the rank is the one recorded in the pre-cap universe; it is not recomputed from the "
              "served list, and a served row's rank can exceed the shipped cap, which is why the "
              "last band is `outside`;",
              "- each cycle's band cells sum to its served window, and each cell's band totals "
              "sum to that cell's relation totals;",
              "- each campaign cell reproduces the run's `served_fingerprint` from its persisted "
              "served order, and its allocation rows agree with its served lists;",
              "- a campaign row's rank is its 1-based position in `universe.edges`, and `support` "
              "is absent because it is `None` in every recorded row.", ""]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = json.loads(ARTIFACT.read_text(encoding="utf-8")) if art is None else art
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("artifact kind")
    if art.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    design = art.get("design_cells") or []
    if len(design) != 12:
        found.append("the design block holds %d cells, not 12" % len(design))
    states = {cell.get("state") for cell in design}
    if RUN.exists():
        cells = json.loads(RUN.read_text(encoding="utf-8"))["cells"]
        keys = {(cell["seed"], cell["arm"]) for cell in cells}
        missing = [(cell["seed"], cell["arm"]) for cell in design
                   if (cell["seed"], cell["arm"]) not in keys]
        if states != {"run"} or missing:
            found.append("the run exists but the design cells do not all record it: %r" % (missing,))
        elif any(not cell.get("served_fingerprint") for cell in design):
            found.append("a run cell carries no served fingerprint")
    elif states != {"not run"}:
        found.append("no run exists but a design cell is marked run")
    run = json.loads(RUN.read_text(encoding="utf-8")) if RUN.exists() else None
    if run is not None:
        found.extend(_campaign_problems(art, run))
    for cell in art.get("campaign_cells") or []:
        label = "campaign %d" % cell.get("seed")
        cycles = cell.get("cycles") or []
        breakdown = band_breakdown(cell)
        if len(breakdown) != len(cycles):
            found.append("%s: the band table has %d cycles, the cell has %d"
                         % (label, len(breakdown), len(cycles)))
            continue
        for cycle, bands in zip(cycles, breakdown):
            counted = sum(count for pair in bands["bands"].values() for count in pair.values())
            window = len(cycle.get("served") or [])
            if counted != window:
                found.append("%s cycle %d: the band table counts %d rows, the window has %d"
                             % (label, cycle.get("cycle"), counted, window))
        totals = band_totals(cell)
        counted = sum(count for pair in totals.values() for count in pair.values())
        if counted != cell.get("served_rows"):
            found.append("%s: the band totals count %d rows, the cell has %d served"
                         % (label, counted, cell.get("served_rows")))
    cells = art.get("fixture_cells") or []
    if not cells:
        found.append("no fixture cells")
    for cell in cells:
        label = "%s/%s" % (cell.get("seed"), cell.get("cap"))
        if cell.get("problems"):
            found.append("%s: %s" % (label, "; ".join(cell["problems"])))
        if cell.get("unknown_relation_served"):
            found.append("%s: %d served row(s) with no relation"
                         % (label, cell["unknown_relation_served"]))
        for cycle in cell.get("cycles") or []:
            allocation = cycle.get("allocation") or {}
            served_here = sum(1 for row in cycle.get("rows") or [] if row.get("served"))
            if allocation.get("served") != served_here:
                found.append("%s cycle %s: allocation disagrees with the table"
                             % (label, cycle.get("cycle")))
            if not allocation.get("sum_matches"):
                found.append("%s cycle %s: counts do not sum" % (label, cycle.get("cycle")))
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the pre-run artifact and page")
    parser.add_argument("--check", action="store_true", help="verify the artifact and page")
    args = parser.parse_args(argv)

    if args.write:
        art = build()
        ARTIFACT.write_text(json.dumps(art, separators=(",", ":")) + "\n", encoding="utf-8")
        PAGE.write_text(render_page(art), encoding="utf-8")
        for cell in art["fixture_cells"]:
            print("%d @ cap %d: %d served / %d universe rows"
                  % (cell["seed"], cell["cap"], cell["served_rows"], cell["universe_rows"]))
        for cell in art.get("campaign_cells") or []:
            print("campaign %d: %d cycles, %d served / %d universe rows"
                  % (cell["seed"], cell["cycles_recorded"], cell["served_rows"],
                     cell["universe_rows"]))
        print("wrote %s and %s" % (ARTIFACT.relative_to(ROOT), PAGE.relative_to(ROOT)))
        return 0

    if args.check or not argv:
        found = problems()
        if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render_page(
                json.loads(ARTIFACT.read_text(encoding="utf-8"))):
            found.append("the page is stale against the artifact")
        for problem in found:
            print("FAIL:", problem)
        if found:
            return 1
        art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        states = sorted({cell["state"] for cell in art["design_cells"]})
        print("n3 tables: %d design cells (%s), %d campaign cells, %d fixture cells, %d served rows"
              % (len(art["design_cells"]), ", ".join(states), len(art.get("campaign_cells") or []),
                 len(art["fixture_cells"]),
                 sum(cell["served_rows"] for cell in art["fixture_cells"])))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
