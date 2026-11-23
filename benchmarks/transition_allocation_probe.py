"""Does a larger transition allocation serve the transitions that ranked 21-40?

The Q4 remainder record (`docs/presence_unexplained_edges.json`) found ten asserted world
edges in rank band 21-40 at cap 40, all transitions, none of them ever served. That record
says in its own page that whether cap 112 would serve them is the registered cap-112 arm's
question. This probe answers the narrower, cheaper version for **one seed**: at cap 112 on
the landed build, are those edges served under (a) the shipped allocation, half the window
to transitions, and (b) an allocation that gives transitions the whole window?

The manipulation is benchmark-side and in process. `MAX_PREDICTIONS` is widened only for
the duration of the call and the returned list is truncated to the shipped window, so the
engine's own ordering is used and the only changed quantity is the transition share. No
engine file changes and no class constant is left moved. Under rule 31 this is a direction,
not a shipped-engine finding: one seed, one world family, one build.

This is not a result and licenses no capability, retention or transfer claim. It runs one
cell per arm, on a seed the conversion block already used, and stores what it saw.

    ./.venv/bin/python -m benchmarks.transition_allocation_probe --write
    ./.venv/bin/python -m benchmarks.transition_allocation_probe --check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks import presence_conversion_repair_observer as repair
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.presence_construct_audit import _world_compositional_edges, asserted_fingerprint

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "presence_unexplained_edges.json"
ARTIFACT = ROOT / "docs" / "transition_allocation_probe.json"
PAGE = ROOT / "docs" / "TRANSITION-ALLOCATION-PROBE.md"
KIND = "transition_allocation_probe"
CAP = 112
CYCLES = 120
SEED = 20611603  # the seed the 21-40 band is densest on: three of its ten edges
BAND = "21-40"
ARMS = ("shipped-112", "all-transitions-112")


class AllTransitionsFirst(repair.RepairedObserverSleepService):
    """The shipped selection, with transitions given the whole window.

    `_build_predictions` spends `MAX_PREDICTIONS` as half transitions, rest cooccurrences,
    then backfills from the transition tail if cooccurrences are short. Doubling the budget
    for the call makes the transition share equal the whole window; truncating the result to
    the shipped window drops the cooccurrences that followed. The constant is restored before
    the cycle continues, so only the allocation inside this call differs.
    """

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        shipped = self.MAX_PREDICTIONS
        self.MAX_PREDICTIONS = shipped * 2
        try:
            candidates = super()._build_predictions(temporal, freqs, prior_schemas)
        finally:
            self.MAX_PREDICTIONS = shipped
        return candidates[:shipped]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def band_edges() -> list[str]:
    """The edges the source record puts in rank band 21-40 on this probe's seed."""
    art = _load(SOURCE)
    rows = [row for record in art["seeds"] if record["seed"] == SEED
            for row in record["edges"] if row["band"] == BAND]
    return sorted(row["edge"] for row in rows)


def _run(seed: int, cycles: int, arm: str) -> dict:
    world = generate_compositional_world(seed=seed, cycles=cycles)
    db_path = _make_scratch_db("transition_allocation")
    mem = _CountingMemoryService(str(db_path))
    svc = (repair.RepairedObserverSleepService(mem, observe=True, cap=CAP)
           if arm == "shipped-112" else AllTransitionsFirst(mem, observe=True, cap=CAP))
    windows: list[list[tuple[str, str]]] = []
    try:
        for index, text in enumerate(world["events"]):
            if index % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = index // EVENTS_PER_CYCLE
            mem.store(text, event_type="observe", source="env")
            if (index + 1) % EVENTS_PER_CYCLE == 0:
                report = svc.run_sleep_cycle()
                windows.append([(p.source, p.target) for p in report.predictions])
        asserted = {(a, b) for a, targets in structure_edges(svc._load_prior_candidates()).items()
                    for b in targets}
        universe = [list(cycle) for cycle in svc.universe]
        allocation = [dict(row) for row in svc.allocation]
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass
    return {"windows": windows, "asserted": asserted, "universe": universe,
            "allocation": allocation, "world": _world_compositional_edges(world)}


def _relation_evidence(run: dict, edges: list[tuple[str, str]]) -> dict:
    """What the transition/cooccurrence label means on these rows.

    The engine sets `is_cooccurrence` from its cooccurrence table in the same branch that
    appends the candidate to one list or the other, so a transition-labelled edge cannot be
    in the table *within a cycle*. That is an invariant, not a measurement result. What does
    vary is the label across cycles: the table evolves, so a pair can be a transition in one
    cycle and a cooccurrence in another; on this probe's seed it did not (0 of 240 edges
    carried both), so the label was stable across the run there. Both labels carry
    `temporal_count`, so neither names a kind of evidence.
    """
    transitions = cooccurrences = overlap = duplicates = 0
    histories: dict[tuple[str, str], dict[str, int]] = {}
    for cycle in run["universe"]:
        pairs = [tuple(row["edge"]) for row in cycle]
        duplicates = max(duplicates, len(pairs) - len(set(pairs)))
        for row in cycle:
            edge = tuple(row["edge"])
            history = histories.setdefault(edge, {"transition": 0, "cooccurrence": 0})
            if row["relation"] == "transition":
                transitions += 1
                history["transition"] += 1
                if row.get("expected_relation") == "cooccurrence":
                    overlap += 1
            elif row["relation"] == "cooccurrence":
                cooccurrences += 1
                history["cooccurrence"] += 1
    both = [edge for edge, history in histories.items()
            if history["transition"] and history["cooccurrence"]]
    return {
        "rows": transitions + cooccurrences,
        "transition_rows": transitions,
        "cooccurrence_rows": cooccurrences,
        "within_cycle_transition_in_cooc": overlap,
        "within_cycle_share": round(overlap / transitions, 6) if transitions else None,
        "distinct_edges": len(histories),
        "edges_labelled_both": len(both),
        "max_duplicate_pairs_in_a_cycle": duplicates,
        "band": [{"edge": "%s>%s" % edge,
                  "transition_cycles": histories.get(edge, {}).get("transition", 0),
                  "cooccurrence_cycles": histories.get(edge, {}).get("cooccurrence", 0)}
                 for edge in edges],
    }


def _arm_record(arm: str, run: dict, edges: list[tuple[str, str]]) -> dict:
    served = {edge for window in run["windows"] for edge in window}
    admissions = {edge: sum(1 for window in run["windows"] if edge in window) for edge in edges}
    first = {}
    for cycle, window in enumerate(run["windows"], start=1):
        for edge in edges:
            if edge in window and edge not in first:
                first[edge] = cycle
    best: dict[str, tuple[int, int, int]] = {}
    seen: dict[str, list[int]] = {edge: [] for edge in edges}
    for index, cycle in enumerate(run["universe"]):
        transitions = sum(1 for row in cycle if row["relation"] == "transition")
        for row in cycle:
            edge = tuple(row["edge"])
            if edge not in seen:
                continue
            seen[edge].append(row["rank"])
            if edge in best or row["rank"] > CAP:
                continue
            best[edge] = (row["rank"], index + 1, transitions)
    detail = [{
        "edge": "%s>%s" % edge,
        "served": edge in served,
        "admissions": admissions[edge],
        "first_served_cycle": first.get(edge),
        "asserted": edge in run["asserted"],
        "min_rank": min(seen[edge]) if seen[edge] else None,
        "cycles_in_universe": len(seen[edge]),
        "best_rank": best.get(edge, (None, None, None))[0],
        "best_cycle": best.get(edge, (None, None, None))[1],
        "transitions_served_in_best_cycle": best.get(edge, (None, None, None))[2],
    } for edge in edges]
    return {
        "arm": arm,
        "cap": CAP,
        "cycles": len(run["windows"]),
        "world_edges": len(run["world"]),
        "served_world_edges": len(served & run["world"]),
        "asserted_world_edges": len(run["asserted"] & run["world"]),
        "band_edges": len(edges),
        "band_served": sum(1 for row in detail if row["served"]),
        "band_asserted": sum(1 for row in detail if row["asserted"]),
        "relation_evidence": _relation_evidence(run, edges),
        "allocation": {
            "returned_served_median": sorted(len(window) for window in run["windows"])[
                len(run["windows"]) // 2],
            "recorded_served_median": sorted(row["served"] for row in run["allocation"])[
                len(run["allocation"]) // 2],
            "transitions_median": sorted(row["transitions"] for row in run["allocation"])[
                len(run["allocation"]) // 2],
            "cooccurrences_median": sorted(row["cooccurrences"] for row in run["allocation"])[
                len(run["allocation"]) // 2],
        },
        "edges": detail,
    }


def build() -> dict:
    edges = band_edges()
    if not edges:
        raise SystemExit("the source record has no %s edges on seed %d" % (BAND, SEED))
    pairs = [tuple(edge.split(">")) for edge in edges]
    arms = [_arm_record(arm, _run(SEED, CYCLES, arm), pairs) for arm in ARMS]
    return engine_stamp.stamp({
        "kind": KIND,
        "not_a_result": True,
        "question": ("On one seed, does giving transitions a larger share of the cap serve the "
                     "asserted world edges that ranked 21-40 at cap 40?"),
        "source": {"artifact": "docs/presence_unexplained_edges.json", "band": BAND,
                   "seed": SEED},
        "design": {
            "seed": SEED, "cycles": CYCLES, "cap": CAP, "band": BAND,
            "edges": edges,
            "edges_digest": asserted_fingerprint(set(pairs)),
            "manipulation": ("transitions are given the whole processed window for the duration "
                             "of one `_build_predictions` call; the returned list is truncated to "
                             "the shipped cap"),
            "control": "the shipped half-and-half allocation at the same cap and seed",
        },
        "arms": arms,
        "summary": {
            "band_served_shipped": next(a["band_served"] for a in arms
                                        if a["arm"] == "shipped-112"),
            "band_served_all_transitions": next(a["band_served"] for a in arms
                                                if a["arm"] == "all-transitions-112"),
        },
        "not_evidence": ("One seed, one world family, one build, two arms, no preregistration. "
                         "A direction for a registered block, not a cap, conversion, mechanism "
                         "or capability result."),
    })


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("artifact kind")
    if art.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    if art.get("design", {}).get("seed") != SEED or art.get("design", {}).get("cap") != CAP:
        found.append("the artifact is not the declared seed and cap")
    edges = band_edges()
    if art.get("design", {}).get("edges") != edges:
        found.append("the band edge set is not the source record's %s set on seed %d"
                     % (BAND, SEED))
    if art.get("design", {}).get("edges_digest") != asserted_fingerprint(
            {tuple(edge.split(">")) for edge in edges}):
        found.append("the band edge digest does not match the source record")
    arms = art.get("arms") or []
    if [row.get("arm") for row in arms] != list(ARMS):
        found.append("the two declared arms are not recorded in order")
    for row in arms:
        if [detail.get("edge") for detail in row.get("edges") or []] != edges:
            found.append("%s: the per-edge rows are not the band set" % row.get("arm"))
        if row.get("band_served") != sum(1 for detail in row.get("edges") or []
                                         if detail.get("served")):
            found.append("%s: the served count is not the per-edge sum" % row.get("arm"))
        if row.get("band_asserted") != sum(1 for detail in row.get("edges") or []
                                          if detail.get("asserted")):
            found.append("%s: the asserted count is not the per-edge sum" % row.get("arm"))
        if row.get("served_world_edges", 0) > row.get("world_edges", 0):
            found.append("%s: more served than present" % row.get("arm"))
        evidence = row.get("relation_evidence") or {}
        if evidence.get("within_cycle_transition_in_cooc") != 0:
            found.append("%s: a transition-labelled edge is in the cooccurrence table within a "
                         "cycle; the construction invariant has broken" % row.get("arm"))
        if (evidence.get("transition_rows", 0) + evidence.get("cooccurrence_rows", 0)
                != evidence.get("rows")):
            found.append("%s: the relation rows do not sum to the universe rows" % row.get("arm"))
        if evidence.get("edges_labelled_both", 0) > evidence.get("distinct_edges", 0):
            found.append("%s: more dual-labelled edges than distinct edges" % row.get("arm"))
    return found


def render(art: dict) -> str:
    design = art["design"]
    arms = {row["arm"]: row for row in art["arms"]}
    lines = [
        "# Does a larger transition allocation serve the 21-40 transitions?", "",
        "Generated from `docs/transition_allocation_probe.json` by "
        "`python -m benchmarks.transition_allocation_probe --write`. Do not edit by hand.", "",
        "**Not a result.** One seed, two in-process arms, one build. It answers a narrow "
        "question left open by `docs/PRESENCE-UNEXPLAINED-EDGES.md` and licenses no claim.",
        "",
        "## The question", "",
        "At cap 40 the engine served half the window as transitions, %d. Ten asserted world "
        "edges ranked 21-40 and were never served. At cap 112 the shipped transition share is "
        "%d. Does that serve them, and does giving transitions the whole window change it?" % (40 // 2, CAP // 2),
        "",
        "## Design", "",
        "| Field | Value |", "| --- | --- |",
        "| Seed | `%d` (the band's densest seed; %d of the ten edges) |" % (
            design["seed"], len(design["edges"])),
        "| Cycles | `%d` |" % design["cycles"], "| Cap | `%d` |" % design["cap"],
        "| Edges | %s |" % ", ".join("`%s`" % edge for edge in design["edges"]),
        "| Control | the shipped half-and-half allocation, same seed and cap |",
        "| Manipulation | %s |" % design["manipulation"],
        "| Seed reuse | one of `PRESENCE-CONVERSION-2`'s design seeds, reused for a derived "
        "one-seed diagnostic and declared as an allowed source in that block's freshness scan |",
        "",
        "## Result", "",
        "| Arm | Band served | Band asserted | Served world | Asserted world | Returned window (median) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm in ARMS:
        row = arms[arm]
        alloc = row["allocation"]
        lines.append("| %s | %d / %d | %d / %d | %d | %d | %d |" % (
            arm, row["band_served"], row["band_edges"], row["band_asserted"], row["band_edges"],
            row["served_world_edges"], row["asserted_world_edges"],
            alloc["returned_served_median"]))
    lines += ["", "### Per edge", "",
              "| Edge | Shipped: served (first, admissions) | All-transitions: served (first, admissions) | Min rank at 112 | Cycles in universe |",
              "| --- | --- | --- | ---: | ---: |"]
    for index, edge in enumerate(design["edges"]):
        shipped = arms["shipped-112"]["edges"][index]
        other = arms["all-transitions-112"]["edges"][index]
        lines.append("| `%s` | %s (%s, %d) | %s (%s, %d) | %s | %d |" % (
            edge, "yes" if shipped["served"] else "no", shipped["first_served_cycle"],
            shipped["admissions"], "yes" if other["served"] else "no",
            other["first_served_cycle"], other["admissions"], shipped["min_rank"],
            shipped["cycles_in_universe"]))
    lines += ["", "## What the transition label means", "",
              "Within a cycle a transition-labelled edge is absent from the cooccurrence table by "
              "construction: the engine sets `is_cooccurrence` from that table and appends the "
              "candidate to one list or the other, so the zero is an invariant, not a finding. "
              "Both labels carry `temporal_count`, so the label names the branch the candidate "
              "took, not the kind of evidence behind it.", "",
              "| Arm | Transition rows | Cooc rows | In cooc within a cycle | Dual-labelled edges across cycles | Max duplicate pairs |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for arm in ARMS:
        evidence = arms[arm]["relation_evidence"]
        lines.append("| %s | %d | %d | %d | %d | %d |" % (
            arm, evidence["transition_rows"], evidence["cooccurrence_rows"],
            evidence["within_cycle_transition_in_cooc"], evidence["edges_labelled_both"],
            evidence["max_duplicate_pairs_in_a_cycle"]))
    lines += ["", "The band's label history: " + "; ".join(
        "`%s` transition in %d cycles, cooccurrence in %d" % (
            row["edge"], row["transition_cycles"], row["cooccurrence_cycles"])
        for row in arms["shipped-112"]["relation_evidence"]["band"]) + ".",
              "", "So the band is not a set of temporal-only edges: `transition` means the pair "
              "was outside the cooccurrence table in the cycle that ranked it. On this seed no "
              "band edge ever carried the other label, and no edge at all carried both (0 of "
              + str(arms["shipped-112"]["relation_evidence"]["distinct_edges"]) +
              "), so the label was stable across the 120 cycles; a flip is possible in the "
              "engine but was not observed here.", ""]
    lines += ["", "## What this does and does not license", "",
              "- It answers, for one seed, whether the band is served at 112: %d of %d on the "
              "shipped allocation and %d of %d when transitions get the whole window." % (
                  art["summary"]["band_served_shipped"], len(design["edges"]),
                  art["summary"]["band_served_all_transitions"], len(design["edges"])),
              "- A rank is the edge's position in the ceiling call's list. `Min rank at 112` is "
              "the smallest rank the edge reached in 120 cycles, so a minimum above 112 means "
              "the allocation was never the binding constraint on this seed; a null minimum "
              "means the edge was not constructed at all and `Cycles in universe` is zero.",
              "- The recorded split counts in the artifact are the observer's own call. For the "
              "all-transitions arm they are taken before this arm truncates to 112, so the "
              "returned window is the comparable field across arms.",
              "- It does not establish that serving these edges changes assertion, conversion "
              "or capability: the asserted-set counts are reported, not interpreted.",
              "- It is not a cap-112 block result, not a preregistered comparison, and not a "
              "mechanism. The registered comparator, Q1 and Q2 remain unrun.", ""]
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
        print("transition allocation probe: %d of %d band edges served shipped, %d with all "
              "transitions (seed %d)" % (
                  art["summary"]["band_served_shipped"], len(art["design"]["edges"]),
                  art["summary"]["band_served_all_transitions"], SEED))
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
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
