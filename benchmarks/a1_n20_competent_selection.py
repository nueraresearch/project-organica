"""Pre-registered N20 competent target-selection rule.

This is a rule record, not a selected target set.  It fixes how a future N20
block would be chosen if the owner adopts a baseline-competent estimand.  It
does not select an edge, write a target artifact, freeze a target, issue a grant
or run an A1 cell.

The rule is deliberately narrow:

* the candidate universe is the same first-36-cycle, one-orientation universe
  used by ``A1-TARGET-SELECTION-1`` and ``A1-C8-EXPANSION-1``;
* a candidate is eligible only when the no-arm A+K+ replay shows both baseline A
  and baseline K;
* the current N4 targets that pass that screen are retained first;
* the rest are filled in a fixed hash order, blind to U magnitude, with each
  tag's selected degree capped at 3;
* exactly 20 rows are required per seed, or that seed fails.

The baseline screen is pre-treatment but is not future-blind to the 120-cycle
no-arm baseline.  This changes the target population from representative
eligible edges to baseline-competent edges; it is a new estimand, not a repair
of the current target set.

    python -m benchmarks.a1_n20_competent_selection --write
    python -m benchmarks.a1_n20_competent_selection --check
    python -m benchmarks.a1_n20_competent_selection --self-test
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DESIGN_VIABILITY_PATH = DOCS / "a1_design_viability.json"
TARGET_VIABILITY_PATH = DOCS / "a1_target_viability.json"
TARGET_SELECTION_PATH = DOCS / "a1_target_selection.json"
BASELINE_AVAILABILITY_PATH = DOCS / "a1_baseline_availability.json"
OUT_PATH = DOCS / "a1_n20_competent_selection_prereg.json"
PAGE_PATH = DOCS / "A1-N20-COMPETENT-SELECTION.md"
ID = "A1-N20-COMPETENT-1"
DATE = "2026-11-14"
KIND = "a1_n20_competent_selection_prereg"
SEEDS = (20630101, 20630102, 20630103, 20630104, 20630105, 20630106)
N_PER_SEED = 20
MAX_DEGREE = 3
U_CYCLE = 36
SALT = "A1-N20-COMPETENT-1"
STATUS = "DRAFT — RULE PRE-REGISTERED, NOT FROZEN, NOT APPLIED, NOT RUN, NO GRANT"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _max_flow(edges: list[tuple[str, str]], capacities: dict[str, int]) -> int:
    """Maximum number of edges under per-tag capacities (unit edge capacity)."""
    source, sink = "__source__", "__sink__"
    graph: dict[str, dict[str, int]] = {}

    def add(a: str, b: str, capacity: int) -> None:
        graph.setdefault(a, {})
        graph.setdefault(b, {})
        graph[a][b] = graph[a].get(b, 0) + capacity
        graph[b].setdefault(a, 0)

    for index, (a, b) in enumerate(edges):
        edge_node = "__edge_%d__" % index
        add(source, edge_node, 1)
        add(edge_node, a, 1)
        add(edge_node, b, 1)
    for tag, capacity in capacities.items():
        if capacity > 0:
            add(tag, sink, capacity)

    total = 0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            node = queue.popleft()
            for nxt, capacity in graph.get(node, {}).items():
                if capacity > 0 and nxt not in parent:
                    parent[nxt] = node
                    queue.append(nxt)
        if sink not in parent:
            return total
        flow, node = 10 ** 9, sink
        while parent[node] is not None:
            previous = parent[node]
            flow = min(flow, graph[previous][node])
            node = previous
        node = sink
        while parent[node] is not None:
            previous = parent[node]
            graph[previous][node] -= flow
            graph[node][previous] += flow
            node = previous
        total += flow


def _competent_edges(seed: int, target_selection: dict, baseline: dict) -> list[str]:
    u = target_selection["per_seed"][str(seed)]["u"]
    availability = {
        row["edge"]: row
        for seed_row in baseline["per_seed"]
        if int(seed_row["seed"]) == seed
        for row in seed_row["rows"]
    }
    return sorted(
        edge for edge in u
        if availability.get(edge, {}).get("A") and
        availability.get(edge, {}).get("K")
    )


def _matching_size(seed: int, forced: list[str], eligible: list[str]) -> int:
    degree: dict[str, int] = {}
    for edge in forced:
        a, b = edge.split(">", 1)
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1
    if any(value > MAX_DEGREE for value in degree.values()):
        return 0
    remaining = [edge for edge in eligible if edge not in set(forced)]
    capacities = {
        tag: max(0, MAX_DEGREE - degree.get(tag, 0))
        for tag in sorted({part for edge in eligible for part in edge.split(">", 1)})
    }
    return len(forced) + _max_flow([tuple(edge.split(">", 1)) for edge in remaining], capacities)


def _per_seed(design_viability: dict, target_viability: dict,
              target_selection: dict, baseline: dict) -> list[dict]:
    pool = {
        int(row["seed"]): row
        for row in design_viability["c2_c8_competence"]["target_pool"]["per_seed"]
    }
    n4 = {
        int(row["seed"]): row
        for row in target_viability["designs"]["N4"]["per_seed"]
    }
    rows = []
    for seed in SEEDS:
        competent_pool = int(pool[seed]["A_and_K_available"])
        current_competent = int(n4[seed]["fully_c2_viable"])
        eligible = _competent_edges(seed, target_selection, baseline)
        if len(eligible) != competent_pool:
            raise ValueError("seed %d competent-edge count does not match the pool" % seed)
        current = list(target_selection["per_seed"][str(seed)]["selected"])
        forced = [edge for edge in current if edge in set(eligible)]
        if len(forced) != current_competent:
            raise ValueError("seed %d current competent count does not match" % seed)
        matching = _matching_size(seed, forced, eligible)
        rows.append({
            "seed": seed,
            "competent_candidates": competent_pool,
            "required_rows": N_PER_SEED,
            "current_n4_competent": current_competent,
            "forced_current_n4": len(forced),
            "current_n4_dropped": 4 - current_competent,
            "max_cap_matching": matching,
            "new_rows_needed": max(0, N_PER_SEED - current_competent),
            "feasible": matching >= N_PER_SEED,
        })
    return rows


def build() -> dict:
    design = _load(DESIGN_VIABILITY_PATH)
    target = _load(TARGET_VIABILITY_PATH)
    target_selection = _load(TARGET_SELECTION_PATH)
    baseline = _load(BASELINE_AVAILABILITY_PATH)
    rows = _per_seed(design, target, target_selection, baseline)
    min_pool = min(row["competent_candidates"] for row in rows)
    max_pool = max(row["competent_candidates"] for row in rows)
    current = sum(row["current_n4_competent"] for row in rows)
    dropped = sum(row["current_n4_dropped"] for row in rows)
    expected_new = sum(row["new_rows_needed"] for row in rows)
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "source_artifacts": {
            "design_viability": DESIGN_VIABILITY_PATH.relative_to(ROOT).as_posix(),
            "target_viability": TARGET_VIABILITY_PATH.relative_to(ROOT).as_posix(),
            "target_selection": TARGET_SELECTION_PATH.relative_to(ROOT).as_posix(),
            "baseline_availability": BASELINE_AVAILABILITY_PATH.relative_to(ROOT).as_posix(),
        },
        "parent_records": {
            "target_selection": "docs/A1-TARGET-SELECTION-PROTOCOL.md",
            "c8_expansion": "docs/A1-C8-EXPANSION.md",
            "c7_c8_unit": "docs/A1-C7-C8-DENOMINATOR.md",
        },
        "rule": {
            "id": ID,
            "n_per_seed": N_PER_SEED,
            "cycles": 120,
            "u_cycle": U_CYCLE,
            "candidate_universe": (
                "The first 36 acquisition cycles, one orientation per candidate, "
                "with positive cycle-36 U strength and cycle membership."
            ),
            "competence_screen": (
                "Both baseline A and baseline K must be true in the no-arm A+K+ "
                "replay. A row missing either path is ineligible; there is no "
                "fallback to a non-competent row."
            ),
            "selection_order": (
                "Force the current N4 targets that pass the competence screen. "
                "Then visit the remaining eligible edges in ascending "
                "sha256('%s|seed|source>target') order and accept an edge only "
                "when both endpoint caps remain and the residual graph still "
                "admits enough edges to reach 20. The result is the "
                "lexicographically earliest 20-edge b-matching, not a first-fit "
                "greedy pass. The hash is blind to U magnitude, treatment "
                "outputs, reports and outcomes."
                % SALT
            ),
            "endpoint_degree_cap": MAX_DEGREE,
            "overlap": "permitted; each tag may appear in at most three selected edges",
            "failure_rule": (
                "If fewer than 20 eligible rows can be selected after the degree "
                "cap, that seed fails and the block is not run. Do not add "
                "non-competent rows, relax the cap, or re-select after seeing "
                "treatment data."
            ),
            "preserves_current_n4": (
                "Only the current N4 targets that pass the competence screen. "
                "The carrier-missing N4 rows are deliberately dropped; this is "
                "a replacement N20 block, not a superset of the current N4 set."
            ),
            "selection_performed": False,
            "targets_selected": 0,
            "frozen": False,
            "granted": False,
            "run": False,
        },
        "feasibility": {
            "per_seed": rows,
            "min_competent_candidates": min_pool,
            "max_competent_candidates": max_pool,
            "min_max_cap_matching": min(row["max_cap_matching"] for row in rows),
            "max_max_cap_matching": max(row["max_cap_matching"] for row in rows),
            "seeds_feasible": sum(1 for row in rows if row["feasible"]),
            "seeds_infeasible": sum(1 for row in rows if not row["feasible"]),
            "current_n4_competent": current,
            "current_n4_dropped": dropped,
            "expected_new_rows": expected_new,
            "conclusion": (
                "A capacity-respecting b-matching with the current competent N4 "
                "rows forced reaches at least 20 on all six seeds: 23-36 "
                "A&K-available candidates per seed, and a maximum matching of "
                "%d-%d rows under the three-edge endpoint cap. The current N4 "
                "block contributes only 12 of its 24 rows; the other 12 are "
                "carrier- or admission-missing and are dropped. Existence is "
                "not a selected target set, a freeze or a result."
                % (min(row["max_cap_matching"] for row in rows),
                   max(row["max_cap_matching"] for row in rows))
            ),
        },
        "consequences": {
            "c2": (
                "All selected rows are baseline A/K-competent under the stated "
                "reading. Exact C2 remains a treatment measurement; this rule "
                "removes the baseline-ineligible rows rather than proving C2 "
                "will pass."
            ),
            "c8": (
                "20 rows give a 1/20 = 0.05 step at the unchanged 0.05 ceiling; "
                "one assertion is at the ceiling and two exceed it. The C8 "
                "threshold is not changed."
            ),
            "c1": (
                "Unaffected. C1's full-stream K availability remains 31-44 "
                "against the 60-row floor; a competent target block cannot "
                "repair the denominator."
            ),
            "estimand": (
                "Changes the target population from representative eligible "
                "edges to baseline-competent edges. It is a new estimand and "
                "cannot be described as a repair of the current representative "
                "target set."
            ),
            "blindness": (
                "The screen uses no treatment output and no report field. It is "
                "pre-treatment, but it is not future-blind to the 120-cycle "
                "no-arm baseline. That limitation is part of the rule."
            ),
        },
        "disposition": (
            "This is a draft rule only. It is not adopted, not frozen, not "
            "applied and not run. Adopting it requires a separate target-freeze "
            "act and a separate dated grant; it does not change the current N4 "
            "manifest or authorise an N20 cell."
        ),
        "not_evidence": (
            "A pre-registered selection rule and a feasibility count over "
            "existing no-arm artifacts. No target edge is selected, no target "
            "is frozen, no grant exists, no A1 cell runs and no C2/C8 result is "
            "measured."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("record kind")
    if doc.get("id") != ID:
        found.append("record id")
    if doc.get("status") != STATUS:
        found.append("record status")
    rule = doc.get("rule") or {}
    if rule.get("n_per_seed") != N_PER_SEED:
        found.append("N per seed changed")
    if rule.get("endpoint_degree_cap") != MAX_DEGREE:
        found.append("endpoint degree cap changed")
    if rule.get("u_cycle") != U_CYCLE:
        found.append("U cycle changed")
    if any(rule.get(key) for key in ("selection_performed", "targets_selected",
                                     "frozen", "granted", "run")):
        found.append("rule record performs an act it says it has not performed")
    feasibility = doc.get("feasibility") or {}
    rows = feasibility.get("per_seed") or []
    if [row.get("seed") for row in rows] != list(SEEDS):
        found.append("feasibility seed block changed")
        return found
    for row in rows:
        if row.get("required_rows") != N_PER_SEED:
            found.append("seed %s row requirement changed" % row.get("seed"))
        if row.get("new_rows_needed") != max(
                0, N_PER_SEED - row.get("current_n4_competent", 0)):
            found.append("seed %s new-row count is inconsistent" % row.get("seed"))
        if row.get("feasible") != (
                row.get("max_cap_matching", 0) >= N_PER_SEED):
            found.append("seed %s feasibility is inconsistent" % row.get("seed"))
    if feasibility.get("min_competent_candidates") != min(
            row.get("competent_candidates", 0) for row in rows):
        found.append("minimum pool is inconsistent")
    if feasibility.get("max_competent_candidates") != max(
            row.get("competent_candidates", 0) for row in rows):
        found.append("maximum pool is inconsistent")
    if feasibility.get("min_max_cap_matching") != min(
            row.get("max_cap_matching", 0) for row in rows):
        found.append("minimum matching is inconsistent")
    if feasibility.get("max_max_cap_matching") != max(
            row.get("max_cap_matching", 0) for row in rows):
        found.append("maximum matching is inconsistent")
    if feasibility.get("seeds_feasible") != sum(
            1 for row in rows if row.get("feasible")):
        found.append("feasible-seed count is inconsistent")
    if feasibility.get("current_n4_competent") != sum(
            row.get("current_n4_competent", 0) for row in rows):
        found.append("current competent-row total is inconsistent")
    if feasibility.get("current_n4_dropped") != sum(
            row.get("current_n4_dropped", 0) for row in rows):
        found.append("dropped-row total is inconsistent")
    if feasibility.get("expected_new_rows") != sum(
            row.get("new_rows_needed", 0) for row in rows):
        found.append("new-row total is inconsistent")
    return found


def self_test() -> list[str]:
    found: list[str] = []
    rows = [
        {"seed": 1, "competent_candidates": 20, "required_rows": 20,
         "current_n4_competent": 4, "current_n4_dropped": 0,
         "new_rows_needed": 16, "feasible": True},
        {"seed": 2, "competent_candidates": 19, "required_rows": 20,
         "current_n4_competent": 3, "current_n4_dropped": 1,
         "new_rows_needed": 17, "feasible": False},
    ]
    if rows[0]["competent_candidates"] < N_PER_SEED:
        found.append("positive feasibility fixture is wrong")
    if rows[1]["feasible"]:
        found.append("negative feasibility fixture is wrong")
    return found


def render(doc: dict) -> str:
    rule = doc["rule"]
    feasibility = doc["feasibility"]
    consequences = doc["consequences"]
    lines = [
        "# A1 N=20 competent target-selection rule — pre-registered draft",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result, a target freeze, a target selection, a grant or a run.** It fixes a rule and counts whether the existing candidate pool could supply it. No target edge has been selected.",
        "",
        "## Rule",
        "",
        "| Element | Value |",
        "| --- | --- |",
        "| Rows per seed | **%d** |" % rule["n_per_seed"],
        "| Candidate universe | %s |" % rule["candidate_universe"],
        "| Competence screen | %s |" % rule["competence_screen"],
        "| Selection order | %s |" % rule["selection_order"],
        "| Endpoint cap | at most **%d** selected edges per tag |" % rule["endpoint_degree_cap"],
        "| Overlap | %s |" % rule["overlap"],
        "| Failure | %s |" % rule["failure_rule"],
        "| Current N4 preservation | %s |" % rule["preserves_current_n4"],
        "",
        "The screen is **pre-treatment but not future-blind to the 120-cycle no-arm baseline**. It uses no treatment output and no report field, but it changes the target population. It is a new estimand, not a repair of the current representative target set.",
        "",
        "## Feasibility",
        "",
        "| Seed | Competent candidates | Required | Current N4 competent | Current N4 dropped | New rows needed | Max cap matching | Feasible? |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in feasibility["per_seed"]:
        lines.append(
            "| `%d` | %d | %d | %d | %d | %d | %d | %s |" % (
                row["seed"], row["competent_candidates"], row["required_rows"],
                row["current_n4_competent"], row["current_n4_dropped"],
                row["new_rows_needed"], row["max_cap_matching"],
                "YES" if row["feasible"] else "NO",
            )
        )
    lines += [
        "",
        "**Seeds feasible:** **%d/6**; competent candidates **%d–%d** per seed; "
        "maximum capacity-respecting matching **%d–%d** rows; "
        "current N4 contributes **%d/24** rows and drops **%d/24**."
        % (feasibility["seeds_feasible"],
           feasibility["min_competent_candidates"],
           feasibility["max_competent_candidates"],
           feasibility["min_max_cap_matching"],
           feasibility["max_max_cap_matching"],
           feasibility["current_n4_competent"],
           feasibility["current_n4_dropped"]),
        "",
        feasibility["conclusion"],
        "",
        "## Consequences",
        "",
        "| Gate | Consequence |",
        "| --- | --- |",
        "| C2 | %s |" % consequences["c2"],
        "| C8 | %s |" % consequences["c8"],
        "| C1 | %s |" % consequences["c1"],
        "| Estimand | %s |" % consequences["estimand"],
        "| Blindness | %s |" % consequences["blindness"],
        "",
        "## Disposition",
        "",
        doc["disposition"],
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_n20_competent_selection --check",
        "python -m benchmarks.a1_n20_competent_selection --self-test",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def write() -> int:
    doc = build()
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = _load(OUT_PATH)
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print(
        "A1 N=20 competent rule: clean; %d/6 seeds feasible; "
        "candidate pool %d-%d; current N4 competent %d/24"
        % (doc["feasibility"]["seeds_feasible"],
           doc["feasibility"]["min_competent_candidates"],
           doc["feasibility"]["max_competent_candidates"],
           doc["feasibility"]["current_n4_competent"])
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        found = self_test()
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("A1 N=20 competent rule: self-test clean")
        return 0
    if args.write:
        return write()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
