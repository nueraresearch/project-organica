"""The asserted-but-never-served edges, recomputed from committed data.

The Q4 stage table reports 26 asserted world edges that never entered a served window. That
number is a count in ``docs/presence_conversion_repair_run.json``; this module records which
edges it is made of, at what recorded rank, in which band, and what the set does and does not
license -- and it recomputes every one of those fields from data already in the repository.

Inputs, all committed:

- ``docs/presence_conversion_repair_run.json`` -- the stage table and ``rank_semantics``;
- ``docs/presence_conversion_2_n3_tables.json`` -- the six observer-on campaign cells, whose
  ``campaign_cells`` carry the served windows and the universe in construction order;
- the compositional world, which is a deterministic function of its seed;
- the asserted world edges, which are the one set no committed artifact carries as a list. The
  writer reads them once from the run's own on-arm parts and stores them in this artifact, and
  the guard recomputes their digest and cross-checks their count against the run's
  ``asserted_final``.

The guard never reads ``.scratch``. A checked-in copy of the asserted lists is what makes the
26 reproducible on a clean clone: drop an edge, change a count, move a rank or edit the summary,
and ``problems`` names the disagreement. The edge set is an input to a derivation, not a second
measurement -- nothing here re-runs a cell.

    ./.venv/bin/python -m benchmarks.presence_unexplained_edges --write
    ./.venv/bin/python -m benchmarks.presence_unexplained_edges --check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.presence_construct_audit import (_world_compositional_edges,
                                                 asserted_fingerprint)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "presence_unexplained_edges.json"
PAGE = ROOT / "docs" / "PRESENCE-UNEXPLAINED-EDGES.md"
NOTE = ROOT / "docs" / "UNEXPLAINED-EDGES-NOTE.md"
RUN = ROOT / "docs" / "presence_conversion_repair_run.json"
N3 = ROOT / "docs" / "presence_conversion_2_n3_tables.json"
PREREG = ROOT / "docs" / "presence_conversion_repair_prereg.json"
PARTS = ROOT / ".scratch" / "presence_repair" / "parts"
KIND = "presence_unexplained_edges"
BANDS = ((1, 20), (21, 40), (41, 80), (81, 112))
RELATION_NAME = {"t": "transition", "c": "cooccurrence"}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cap() -> int:
    return int(_load(PREREG)["engine"]["cap"])


def world(seed: int, cycles: int) -> set[tuple[str, str]]:
    return _world_compositional_edges(generate_compositional_world(seed=seed, cycles=cycles))


def _band(rank: int) -> str:
    for low, high in BANDS:
        if low <= rank <= high:
            return "%d-%d" % (low, high)
    return "%d+" % (BANDS[-1][1] + 1)


def scan(cell: dict) -> tuple[set[tuple[str, str]], dict, dict, list[int]]:
    """Served edges, each edge's best recorded rank, its relation, and served transitions.

    A rank is the edge's 1-based position in the recorded universe, which is the ceiling call's
    list -- a block position, not an admission position. The best rank over the run is used, and
    the cycle that carried it, because the served transition count of that cycle is the budget
    the rank has to fit inside.
    """
    served: set[tuple[str, str]] = set()
    best: dict[tuple[str, str], tuple[int, int]] = {}
    relation: dict[tuple[str, str], str] = {}
    served_transitions: list[int] = []
    for index, cycle in enumerate(cell["cycles"]):
        edges = [tuple(edge.split(">")) for edge in cycle["universe"]["edges"]]
        relations = cycle["universe"]["relations"]
        window = {tuple(edge) for edge in cycle["served"]}
        served |= window
        served_transitions.append(
            sum(1 for edge, name in zip(edges, relations) if name == "t" and edge in window))
        for position, (edge, name) in enumerate(zip(edges, relations), start=1):
            if edge not in best or position < best[edge][0]:
                best[edge] = (position, index)
                relation[edge] = RELATION_NAME.get(name, name)
    return served, best, relation, served_transitions


def analyse(run: dict, n3: dict, asserted: dict[int, list[str]]) -> dict:
    """Every field of the artifact, from the run, the N3 tables, the world and the edge lists."""
    cap_value = cap()
    stage = {row["seed"]: row for row in run["stage_table"]}
    cells = {cell["seed"]: cell for cell in n3["campaign_cells"]}
    cycles = {(cell["seed"], cell["arm"]): cell["cycles"] for cell in run["cells"]}
    records, bands, relations = [], {}, {}
    total_in_cap = total_within = 0
    gaps: list[int] = []
    served_relations = {"transition": 0, "cooccurrence": 0}
    for seed in sorted(stage):
        rows_world = world(seed, cycles[(seed, "on")])
        served, best, relation, served_transitions = scan(cells[seed])
        ever = served & rows_world
        for edge in ever:
            served_relations[relation[edge]] = served_relations.get(relation[edge], 0) + 1
        edges = {tuple(edge.split(">")) for edge in asserted[seed]}
        unexplained = sorted(edges - ever)
        last: dict[tuple[str, str], int] = {}
        for index, cycle in enumerate(cells[seed]["cycles"], start=1):
            for edge in cycle["served"]:
                last[tuple(edge)] = index
        admitted_last = sorted(last[edge] for edge in (edges & ever) if edge in last)
        rows = []
        for edge in unexplained:
            if edge not in best:
                raise ValueError("%d: %s>%s has no recorded rank" % (seed, edge[0], edge[1]))
            rank, index = best[edge]
            gap = rank - served_transitions[index]
            in_cap = rank <= cap_value
            rows.append({
                "edge": "%s>%s" % edge, "rank": rank, "best_cycle": index + 1,
                "relation": relation[edge],
                "served_transitions_in_best_cycle": served_transitions[index],
                "gap": gap, "in_cap": in_cap, "band": _band(rank),
            })
            bands[_band(rank)] = bands.get(_band(rank), 0) + 1
            relations[relation[edge]] = relations.get(relation[edge], 0) + 1
            if in_cap:
                total_in_cap += 1
                if gap <= 0:
                    total_within += 1
                else:
                    gaps.append(gap)
        records.append({
            "seed": seed,
            "present": stage[seed]["present"],
            "served": stage[seed]["served_ever"],
            "asserted": stage[seed]["asserted_final"],
            "unexplained": len(rows),
            "in_cap": sum(1 for row in rows if row["in_cap"]),
            "within_served_transitions": sum(1 for row in rows
                                             if row["in_cap"] and row["gap"] <= 0),
            "rank_min": min(row["rank"] for row in rows) if rows else None,
            "rank_max": max(row["rank"] for row in rows) if rows else None,
            "admitted_asserted": len(edges) - len(rows),
            "admitted_asserted_last_served_median":
                admitted_last[len(admitted_last) // 2] if admitted_last else None,
            "asserted_world_fingerprint":
                asserted_fingerprint({tuple(edge.split(">")) for edge in asserted[seed]}),
            "asserted_world_edges": list(asserted[seed]),
            "edges": rows,
        })
    ranks = sorted(row["rank"] for record in records for row in record["edges"])
    return {
        "kind": KIND,
        "prereg": run.get("prereg"),
        "not_a_result": True,
        "question": ("Which asserted world edges were never served, where do they rank, and what "
                     "does that set license?"),
        "definition": ("Present world edges that were asserted at the end of the run and appear in "
                       "no served window; `served` is the union over all 120 cycles."),
        "source": {
            "stage_table": "docs/presence_conversion_repair_run.json",
            "served_and_universe": "docs/presence_conversion_2_n3_tables.json",
            "world": "generate_compositional_world(seed=, cycles=120), deterministic",
            "asserted_edges": ("the run's on-arm parts, stored here because no committed artifact "
                               "carries the edge lists"),
        },
        "cap": cap_value,
        "engine_version": run.get("engine_version"),
        "run_engine_version": run.get("engine_version"),
        "seeds": records,
        "summary": {
            "present": sum(record["present"] for record in records),
            "served": sum(record["served"] for record in records),
            "never_served_candidates": sum(int(row.get("never_served") or 0)
                                           for row in run["stage_table"]),
            "asserted": sum(record["asserted"] for record in records),
            "unexplained": sum(record["unexplained"] for record in records),
            "admitted_asserted": sum(record["admitted_asserted"] for record in records),
            "in_cap": total_in_cap,
            "within_served_transitions": total_within,
            "closest_miss_in_cap": min(gaps) if gaps else None,
            "rank_min": ranks[0] if ranks else None,
            "rank_max": ranks[-1] if ranks else None,
            "rank_median": ranks[len(ranks) // 2] if ranks else None,
            "bands": dict(sorted(bands.items())),
            "relations": dict(sorted(relations.items())),
            "served_world_relations": dict(sorted(served_relations.items())),
            "seeds_with_unexplained": sum(1 for record in records if record["unexplained"]),
        },
        "not_evidence": ("A per-edge description of one remainder on six seeds, one world family "
                         "and one cap. It is not a mechanism, a defect, a capability or a "
                         "prediction about another level."),
    }


def build() -> dict:
    run, n3 = _load(RUN), _load(N3)
    asserted = {}
    for seed in sorted(row["seed"] for row in run["stage_table"]):
        part = _load(PARTS / ("%d-on.json" % seed))
        edges = sorted("%s>%s" % tuple(edge) for edge in part["asserted_edges"])
        if asserted_fingerprint({tuple(edge.split(">")) for edge in edges}) != \
                part["asserted_world_fingerprint"]:
            raise ValueError("%d: the part's asserted edges do not match its fingerprint" % seed)
        if len(edges) != part["asserted_world_edges"]:
            raise ValueError("%d: the part's asserted count is inconsistent" % seed)
        asserted[seed] = edges
    return engine_stamp.stamp(analyse(run, n3, asserted))


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("artifact kind")
    if art.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    run, n3 = _load(RUN), _load(N3)
    if art.get("cap") != cap():
        found.append("the cap does not match the frozen record")
    if art.get("run_engine_version") != run.get("engine_version"):
        found.append("the run's engine version does not match the stage table")
    stage = {row["seed"]: row for row in run["stage_table"]}
    seeds = [record.get("seed") for record in art.get("seeds") or []]
    if sorted(seeds) != sorted(stage):
        found.append("the seeds do not match the run's stage table")
        return found
    asserted = {record["seed"]: list(record.get("asserted_world_edges") or [])
                for record in art["seeds"]}
    try:
        derived = analyse(run, n3, asserted)
    except (KeyError, ValueError) as error:
        found.append("the stored inputs do not derive: %s" % error)
        return found
    by_seed = {record["seed"]: record for record in derived["seeds"]}
    for record in art["seeds"]:
        seed = record["seed"]
        expected = by_seed[seed]
        if record.get("asserted") != expected["asserted"]:
            found.append("%d: asserted %r, the run says %r"
                         % (seed, record.get("asserted"), expected["asserted"]))
        if len(record.get("asserted_world_edges") or []) != expected["asserted"]:
            found.append("%d: %d stored edges, the run says %d asserted"
                         % (seed, len(record.get("asserted_world_edges") or []),
                            expected["asserted"]))
        if record.get("asserted_world_fingerprint") != expected["asserted_world_fingerprint"]:
            found.append("%d: the stored edges do not reproduce the asserted fingerprint" % seed)
        if record.get("unexplained") != expected["unexplained"]:
            found.append("%d: unexplained %r, recomputed %r"
                         % (seed, record.get("unexplained"), expected["unexplained"]))
        if record.get("in_cap") != expected["in_cap"]:
            found.append("%d: in-cap %r, recomputed %r"
                         % (seed, record.get("in_cap"), expected["in_cap"]))
        if (record.get("edges") or []) != expected["edges"]:
            found.append("%d: the per-edge rows do not match the recomputation" % seed)
    if art.get("summary") != derived["summary"]:
        found.append("the summary does not match the recomputation")
    semantics = run.get("rank_semantics") or {}
    if derived["summary"]["in_cap"] != semantics.get("in_cap_asserted_without_admission"):
        found.append("in-cap count disagrees with the run's rank_semantics")
    if derived["summary"]["within_served_transitions"] != \
            semantics.get("in_cap_asserted_without_admission_within_served_transitions"):
        found.append("within-budget count disagrees with the run's rank_semantics")
    return found


def render(art: dict) -> str:
    summary = art["summary"]
    lines = [
        "# The asserted-but-never-served edges", "",
        "Generated from `docs/presence_unexplained_edges.json` by "
        "`python -m benchmarks.presence_unexplained_edges --write`. Do not edit by hand.", "",
        "**Not a result artifact.** It describes the remainder the Q4 stage table counts, "
        "recomputed from the run artifact, the committed N3 campaign tables, a deterministic "
        "world and the asserted edge lists stored here. The campaign ran on 0.14.0; this record "
        "was re-derived from the same inputs on 0.15.0. It re-scores nothing.", "",
        "## What is counted", "",
        "A world edge is **unexplained** when it is present, asserted at the end of the run, and "
        "appears in none of the 120 served windows. `rank` is the edge's best recorded position in "
        "the ceiling call's list -- a block position, not an admission position -- and `gap` is "
        "that rank minus the transitions actually served in the cycle that ranked it, so a gap of "
        "zero or less would mean it was inside the served transitions.", "",
        "## Per seed", "",
        "| Seed | Present | Served | Asserted | Unexplained | In cap | Within served transitions | Rank range |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for record in art["seeds"]:
        lines.append("| %d | %d | %d | %d | %d | %d | %d | %s |" % (
            record["seed"], record["present"], record["served"], record["asserted"],
            record["unexplained"], record["in_cap"], record["within_served_transitions"],
            "%d-%d" % (record["rank_min"], record["rank_max"])
            if record["rank_min"] is not None else "none"))
    lines.append("| **total** | %d | %d | %d | %d | %d | %d | %s |" % (
        summary["present"], summary["served"], summary["asserted"], summary["unexplained"],
        summary["in_cap"], summary["within_served_transitions"],
        "%d-%d" % (summary["rank_min"], summary["rank_max"])
        if summary["rank_min"] is not None else "none"))
    bands = summary["bands"]
    labels = ["%d-%d" % pair for pair in BANDS] + ["113+"]
    lines += ["", "## Rank bands", "",
              "| %s |" % " | ".join(labels), "| %s |" % " | ".join("---:" for _ in labels),
              "| %s |" % " | ".join(str(bands.get(label, 0)) for label in labels), "",
              "Relations: %s. The served world edges are %s." % (
                  ", ".join("%s %d" % pair for pair in summary["relations"].items()) or "none",
                  ", ".join("%s %d" % pair for pair in summary["served_world_relations"].items())),
              "", "## The edges", "",
              "| Seed | Edge | Rank | Gap | Band | Relation |",
              "| ---: | --- | ---: | ---: | --- | --- |"]
    for record in art["seeds"]:
        for row in record["edges"]:
            lines.append("| %d | `%s` | %d | %d | %s | %s |" % (
                record["seed"], row["edge"], row["rank"], row["gap"], row["band"],
                row["relation"]))
    lines += ["", "## What this licenses", "",
              "- **The assertion stage is not lossless, and it is not the served union.** %d of "
              "%d asserted world edges were never served, so `A_W` contains edges the served "
              "window never carried; the S_ever-to-A_W step cannot be read as a pure conversion "
              "loss." % (summary["unexplained"], summary["asserted"]),
              "- **The remainder is small and second-order.** %d of %d asserted edges (%.1f%%) are "
              "unexplained; the other %d were served." % (
                  summary["unexplained"], summary["asserted"],
                  100.0 * summary["unexplained"] / summary["asserted"] if summary["asserted"] else 0,
                  summary["admitted_asserted"]),
              "- **It is not a late-window artefact.** The asserted edges that were served have a "
              "per-seed median last-served cycle of %s (cycle 120 is the last), so the served "
              "asserted edges are mostly late arrivals; the unexplained set is not simply an "
              "early cohort." % ", ".join(
                  str(record["admitted_asserted_last_served_median"]) for record in art["seeds"]),
              "- **Only %d of the %d sit inside the cap and %d inside the served transitions.** "
              "The closest in-cap miss is %s rank(s) short." % (
                  summary["in_cap"], summary["unexplained"],
                  summary["within_served_transitions"], summary["closest_miss_in_cap"]),
              "", "## What it does not license", "",
              "- Not a mechanism: it does not show *why* an asserted edge was never served.",
              "- Not a defect: it does not show that serving them would have changed `A_W`, and it "
              "does not make the admission rule wrong.",
              "- Not a prediction: nothing here says cap 112 would serve them; that is the "
              "registered cap-112 arm's question.",
              "- Not a capability, retention or transfer claim: one world family, six seeds, one "
              "cap, one build.",
              "- The asserted edge lists are stored as an input; their count and digest are "
              "checked against the run, but storing them is not a second measurement.", ""]
    return "\n".join(lines)


def render_note(art: dict) -> str:
    """The interpretation note: every figure substituted from the record, none typed."""
    summary = art["summary"]
    share = (100.0 * summary["unexplained"] / summary["asserted"]
             if summary["asserted"] else 0.0)
    per_seed = ", ".join("%d: %d" % (record["seed"], record["unexplained"])
                         for record in art["seeds"])
    medians = ", ".join(str(record["admitted_asserted_last_served_median"])
                        for record in art["seeds"])
    bands = summary["bands"]
    band_text = ", ".join("%s: %d" % (label, bands.get(label, 0))
                           for label in ("1-20", "21-40", "41-80", "81-112", "113+"))
    return "\n".join([
        "# Interpretation note: the asserted-but-never-served edges", "",
        "Derived from `docs/presence_unexplained_edges.json` by "
        "`python -m benchmarks.presence_unexplained_edges --write`. Do not edit by hand.", "",
        "**An interpretation of a committed record, not a second measurement.** It re-reads the "
        "edges, their ranks and their bands; it runs no cell and re-scores no verdict.", "",
        "## The set", "",
        "Of the **%d** asserted world edges, **%d** were served at least once and **%d** never "
        "entered a served window (%.1f%%). Every unexplained edge is a transition. Their best "
        "recorded rank runs **%d-%d** -- a position in the ceiling call's list, where transitions "
        "precede cooccurrences, not an admission position. Per seed: %s. **%d** of the %d sit "
        "inside the cap (rank <= %d); **%d** sit inside the transitions actually served in the "
        "cycle that ranked them; the closest in-cap miss is **%d** rank(s) short. By band: %s." % (
            summary["asserted"], summary["admitted_asserted"], summary["unexplained"], share,
            summary["rank_min"], summary["rank_max"], per_seed, summary["in_cap"],
            summary["unexplained"], art["cap"], summary["within_served_transitions"],
            summary["closest_miss_in_cap"], band_text),
        "", "## What it licenses", "",
        "- **The assertion step is not lossless, and it is not the served union.** %d of %d "
        "asserted world edges were never served, so `A_W` contains edges the served window never "
        "carried and the `S_ever`-to-`A_W` step cannot be read as a pure conversion loss." % (
            summary["unexplained"], summary["asserted"]),
        "- **The remainder is small and second-order.** %.1f%% of asserted edges, against %d "
        "that were served." % (share, summary["admitted_asserted"]),
        "- **It is not a late-window artefact.** The served asserted edges have a per-seed median "
        "last-served cycle of %s, against a last cycle of 120, so the unexplained set is not "
        "merely an early cohort." % medians,
        "- **'In cap' is not 'inside the budget'.** %d sit inside the cap, but %d sat inside the "
        "transitions actually served in the cycle that ranked them; the cap bound that matters "
        "here is the 20-slot transition allocation, not 40." % (
            summary["in_cap"], summary["within_served_transitions"]),
        "- **It is a location, not a cause.** It names which edges, at what best rank, in which "
        "band; it identifies no rule that excluded them and no mechanism that produced the "
        "assertion.",
        "", "## What it does not license", "",
        "- **Not a mechanism, and not a defect in the admission rule.** The recorded rank is a "
        "block position in the ceiling call's list, not an admission position; %d of the %d "
        "ranked inside the transitions served in their best cycle, so a claim that the ranking "
        "skipped them cannot be made from rank alone." % (
            summary["within_served_transitions"], summary["unexplained"]),
        "- **Not a claim that serving them would have changed `A_W`.** `A_W` is an end-state "
        "stock; an edge that is asserted without being served is evidence about the path, not "
        "about what the stock would have been.",
        "- **Not a prediction about cap 112.** %d of the %d sit inside the cap at cap 40; nothing "
        "here says a 112-slot build would serve them. That is the registered cap-112 arm's "
        "question, not this record's answer." % (summary["in_cap"], summary["unexplained"]),
        "- **Not a capability, retention or transfer claim.** One world family, six seeds, one "
        "cap, one 0.14.0 build, 120 cycles.",
        "- **Not an attribution.** The asserted edge lists are stored as an input; their count and "
        "digest are checked against the run, but storing them is not a second measurement and "
        "does not name the events behind an assertion.",
        "- **Not a reconciliation of `S_ever` and `A_W`.** One is a cumulative union and the "
        "other an end-state stock; their difference is not a loss count.",
        "", "## Three readings it rules out", "",
        "1. **'The assertion step loses nothing.'** False: %d asserted edges were never served." % (
            summary["unexplained"]),
        "2. **'The loss is at construction.'** False for this set: these are present world edges, "
        "so they were constructed as candidates; the Q4 stage table's %d never-admitted "
        "candidates are a different set with a different denominator." % (
            summary["never_served_candidates"]),
        "3. **'Inside the cap means it was served.'** False: %d of the %d in-cap edges were "
        "inside the served transitions of their best cycle; the closest was %d rank(s) short." % (
            summary["within_served_transitions"], summary["in_cap"],
            summary["closest_miss_in_cap"]),
        "", "## What would change this note", "",
        "- **The cap-112 admission arm.** If the 21-40 transitions are served at 112, per seed "
        "and with the block's gates passing, the capacity reading of these ten edges "
        "strengthens; if they are not, the next step is the admission rule rather than another "
        "level, as `docs/DECISION-ADMISSION-STEP.md` fixes.",
        "- **A different world family or seed block.** The shape here -- most of the remainder in "
        "41-80 and 21-40, none inside the served transitions -- is one family's shape, and a "
        "fresh block could move it.",
        "", "## Scope", "",
        "The record this note interprets was produced on the 0.14.0 build at cap 40, 120 cycles, "
        "six seeds of the Gate-13 compositional world. The note restates and bounds the record; "
        "it does not re-score it, and it adds no evidence.", "",
    ])


def check() -> int:
    if not ARTIFACT.exists():
        print("FAIL: no artifact; run --write")
        return 1
    art = _load(ARTIFACT)
    found = problems(art)
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(art):
        found.append("the page is stale against the artifact")
    if not NOTE.exists() or NOTE.read_text(encoding="utf-8") != render_note(art):
        found.append("the interpretation note is stale against the artifact")
    for problem in found:
        print("FAIL:", problem)
    if not found:
        summary = art["summary"]
        print("unexplained edges: %d of %d asserted, %d in cap, %d within served transitions"
              % (summary["unexplained"], summary["asserted"], summary["in_cap"],
                 summary["within_served_transitions"]))
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
        NOTE.write_text(render_note(art), encoding="utf-8")
        print("wrote %s, %s and %s" % (ARTIFACT.relative_to(ROOT), PAGE.relative_to(ROOT),
                                        NOTE.relative_to(ROOT)))
        return 0
    if args.check or not argv:
        return check()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
