"""Generator-only feasibility check for the transfer manipulation.

Question: can the compositional world's law be **conditioned** so that a declared
set of transitions never appears in the formation stream, while the world stays
connected, every context stays reachable, consecutive events stay genuinely
consecutive, and the withheld transitions are still frequent enough in the test
window to be scored?

Runs no engine and no study cell: it imports the generator and walks its law.

The criteria below are fixed before any subset is evaluated, and the rule is
chosen by them — never by any study outcome.  The existing `trainable` mask in
`acquisition_compositional.py` is deliberately not reused: that mask still
generates the withheld event and advances the hidden state, and the runner skips
storing it, making the surviving events adjacent across a gap the world never had.
"""
from __future__ import annotations

import itertools
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmarks.acquisition_compositional import (  # noqa: E402
    CELLS, TAGS_PER_CELL, LAW_R0, flip_p, flip_q,
)

KINDS = ("flip_p", "flip_q")
ORDER = [(c, k) for c in sorted(CELLS) for k in KINDS]      # 8 directed transitions
WANT = 2                                                    # 25 % of 8
FLOOR = 20                                                  # withheld instances
ACQ_CYCLES, EVENTS_PER_CYCLE = 90, 8
TEST_CYCLES = 100
ACQ_SEED, TEST_SEED = 20261201, 20261206


def succ(cell, kind):
    return flip_p(cell) if kind == "flip_p" else flip_q(cell)


def reachable(start, edges):
    seen, stack = {start}, [start]
    while stack:
        u = stack.pop()
        for a, b in edges:
            if a == u and b not in seen:
                seen.add(b)
                stack.append(b)
    return seen


def evaluate(withheld):
    withheld = set(withheld)
    permitted = [e for e in ORDER if e not in withheld]
    edges = [(c, succ(c, k)) for c, k in permitted]
    strong = all(reachable(c, edges) == set(CELLS) for c in CELLS)
    in_deg = {str(c): sum(1 for a, b in edges if b == c) for c in CELLS}
    out_deg = {str(c): sum(1 for a, b in edges if a == c) for c in CELLS}

    whole = all(out_deg[str(c)] >= 1 and in_deg[str(c)] >= 1 for c in CELLS)
    if not whole or not strong:
        # a cell with no permitted exit cannot be sampled from at all: this
        # subset is infeasible as a manipulation, and simulating it would be
        # a crash dressed up as a measurement
        return {
            "withheld": [list(map(str, e)) for e in sorted(withheld)],
            "checks": {
                "strongly_connected": strong,
                "all_cells_in_and_out": whole,
                "all_contexts_seen": False,
                "every_permitted_instantiated": False,
                "consecutive_pairs_genuine": False,
                "withheld_floor_met": False,
            },
            "feasible": False, "strongly_connected": strong,
            "in_degree_permitted": in_deg, "out_degree_permitted": out_deg,
            "contexts_seen": [], "permitted_transition_instances": {},
            "min_permitted_instance": 0, "withheld_events_compensated": 0,
            "withheld_instances_test_window": {}, "min_withheld_instances": 0,
        }

    # conditioned formation stream: resample among the permitted transitions
    rng = random.Random(ACQ_SEED)
    state = CELLS[0]
    pairs, observed, compensated = [], {str(e): 0 for e in permitted}, 0
    for _ in range(ACQ_CYCLES * EVENTS_PER_CYCLE):
        options = [(c, k) for c, k in ORDER if c == state]
        cell, kind = rng.choices(options, weights=[LAW_R0[k] for _, k in options], k=1)[0]
        if (cell, kind) in withheld:
            compensated += 1
            here = [k for c, k in permitted if c == state]
            kind = rng.choices(here, weights=[LAW_R0[k] for k in here], k=1)[0]
        nxt = succ(state, kind)
        observed[str((state, kind))] += 1
        pairs.append((state, nxt))
        state = nxt
    # each stored event must start where the previous one ended
    genuine = all(a[1] == b[0] for a, b in zip(pairs, pairs[1:]))
    contexts = {str(c) for c, _ in pairs}

    # test window under the UNCONDITIONED law
    rng2 = random.Random(TEST_SEED)
    state = CELLS[0]
    inst = {str(e): 0 for e in withheld}
    for _ in range(TEST_CYCLES * EVENTS_PER_CYCLE):
        cell, kind = rng2.choices(ORDER, weights=[LAW_R0[k] for _, k in ORDER], k=1)[0]
        if (state, kind) in withheld:
            inst[str((state, kind))] += 1
        state = succ(state, kind)

    checks = {
        "strongly_connected": strong,
        "all_cells_in_and_out": all(in_deg[str(c)] >= 1 and out_deg[str(c)] >= 1 for c in CELLS),
        "all_contexts_seen": len(contexts) == len(CELLS),
        "every_permitted_instantiated": min(observed.values()) >= 1,
        "consecutive_pairs_genuine": genuine,
        "withheld_floor_met": all(v >= FLOOR for v in inst.values()),
    }
    return {
        "withheld": [list(map(str, e)) for e in withheld],
        "checks": checks,
        "feasible": all(checks.values()),
        "strongly_connected": strong,
        "in_degree_permitted": in_deg,
        "out_degree_permitted": out_deg,
        "contexts_seen": sorted(contexts),
        "permitted_transition_instances": observed,
        "min_permitted_instance": min(observed.values()),
        "withheld_events_compensated": compensated,
        "withheld_instances_test_window": inst,
        "min_withheld_instances": min(inst.values()),
    }


def main():
    every_fourth = [ORDER[3], ORDER[7]]
    baseline = evaluate(every_fourth)
    print("every-fourth:", json.dumps(baseline["checks"]), flush=True)

    combos = list(itertools.combinations(ORDER, WANT))
    results = [evaluate(list(c)) for c in combos]
    feasible = [r for r in results if r["feasible"]]
    chosen = feasible[0] if feasible else None
    print("subsets:", len(results), "feasible:", len(feasible), flush=True)

    out = {
        "kind": "reusable_knowledge_feasibility",
        "generation": 2,
        "method": "generator-only, conditioned sampling; no engine, no study cell",
        "world": "benchmarks/acquisition_compositional.py",
        "edge_unit": "directed cell transition (context cell -> successor cell), one per flip type",
        "transitions_total": len(ORDER),
        "withheld_count": WANT,
        "withheld_share": WANT / len(ORDER),
        "criteria_fixed_before_enumeration": [
            "strong connectivity of the permitted graph",
            "every cell keeps in-degree >= 1 and out-degree >= 1",
            "all four cells appear as contexts in the formation stream",
            "every permitted transition is instantiated at least once",
            "stored events are consecutive in the world (no skipped-event jumps)",
            f"each withheld transition occurs at least {FLOOR} times in a {TEST_CYCLES}-cycle test window",
        ],
        "acquisition": {"cycles": ACQ_CYCLES, "events_per_cycle": EVENTS_PER_CYCLE,
                        "seeds": {"acquisition": ACQ_SEED}},
        "test_window": {"cycles": TEST_CYCLES, "seed": TEST_SEED, "floor": FLOOR},
        "proposed_rule_every_fourth": baseline,
        "subsets_evaluated": len(results),
        "subsets_feasible": len(feasible),
        "chosen_rule": chosen["withheld"] if chosen else None,
        "chosen_rule_index": combos.index(tuple(every_fourth)) if False else (
            results.index(chosen) if chosen else None),
        "chosen": chosen,
        "all_results": results,
        "tag_level": {
            "distinct_tag_pairs_from_cell_law": len(ORDER) * TAGS_PER_CELL * TAGS_PER_CELL,
            "gate13_cross_cell_edges": 112,
            "note": "the 112 is a tag-level count of the GROUP world "
                    "(benchmarks/acquisition_world.py); the compositional law yields "
                    f"{len(ORDER) * TAGS_PER_CELL * TAGS_PER_CELL} distinct tag pairs",
        },
    }
    out["feasible_as_transfer"] = bool(chosen)
    pathlib.Path(ROOT / "docs/reusable_knowledge_feasibility.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("subsets_evaluated", "subsets_feasible",
                                        "chosen_rule", "feasible_as_transfer")}, indent=1))
    if r["chosen"]:
        print("chosen checks:", json.dumps(r["chosen"]["checks"], indent=1))
        print("chosen acq:", r["chosen"]["min_permitted_instance"],
              r["chosen"]["withheld_events_compensated"], r["chosen"]["contexts_seen"])
        print("chosen test:", r["chosen"]["withheld_instances_test_window"])
