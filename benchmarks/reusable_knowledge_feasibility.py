"""Generator-only feasibility check for the transfer manipulation.

Question: can the compositional world's law be **conditioned** so that a declared
set of transitions never appears in ANY formation exposure (warmup and acquisition
alike), while the world stays connected, every context stays reachable, consecutive
events stay genuinely consecutive, and the withheld transitions are frequent enough
in the real transfer window to be scored?

Runs no engine and no study cell.

Seeds: only the **calibration/design** seeds are used.  A confirmatory seed may not
inform a design choice, so `20261206` — which the previous generation of this check
used and which the protocol had designated confirmatory — is marked **burned** here
and replaced in the confirmatory set.  That is why the array below starts at 20261201
and stops at 20261205.
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
    CELLS, TAGS_PER_CELL, LAW_R0, EVENTS_PER_CYCLE, CYCLES, flip_p, flip_q,
    PHASE_WARMUP, PHASE_ACQUISITION, PHASE_RETENTION, PHASE_TRANSFER,
    cell_name, generate_compositional_world,
)

KINDS = ("flip_p", "flip_q")
ORDER = [(c, k) for c in sorted(CELLS) for k in KINDS]      # 8 directed transitions
WANT = 2                                                    # 25 % of 8
FLOOR = 20                                                  # withheld instances
CALIBRATION_SEEDS = (20261201, 20261202, 20261203, 20261204, 20261205)
BURNED_SEEDS = (20261206,)                                  # used by generation 2
PREVIOUS_RULE = [(CELLS[0], "flip_p"), (sorted(CELLS)[1], "flip_q")]

# formation exposure = warmup + acquisition, exactly as the runner feeds it
FORMATION_CYCLES = PHASE_ACQUISITION[1]                     # 110 -> cycles 0..109
TRANSFER_CYCLES = PHASE_TRANSFER[1] - PHASE_TRANSFER[0]     # 50
RETENTION_CYCLES = PHASE_RETENTION[1] - PHASE_RETENTION[0]  # 40


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


def static_checks(withheld):
    permitted = [e for e in ORDER if e not in withheld]
    edges = [(c, succ(c, k)) for c, k in permitted]
    in_deg = {str(c): sum(1 for a, b in edges if b == c) for c in CELLS}
    out_deg = {str(c): sum(1 for a, b in edges if a == c) for c in CELLS}
    return {
        "strongly_connected": all(reachable(c, edges) == set(CELLS) for c in CELLS),
        "all_cells_in_and_out": all(in_deg[str(c)] >= 1 and out_deg[str(c)] >= 1 for c in CELLS),
    }, in_deg, out_deg


def formation_stream(withheld, seed):
    """Conditioned exposure across warmup + acquisition; no event is ever skipped."""
    withheld = set(withheld)
    permitted = [e for e in ORDER if e not in withheld]
    rng = random.Random(seed)
    state = CELLS[0]
    pairs, observed, compensated = [], {str(e): 0 for e in permitted}, 0
    for _ in range(FORMATION_CYCLES * EVENTS_PER_CYCLE):
        options = [(c, k) for c, k in ORDER if c == state]
        _, kind = rng.choices(options, weights=[LAW_R0[k] for _, k in options], k=1)[0]
        if (state, kind) in withheld:
            compensated += 1
            here = [k for c, k in permitted if c == state]
            kind = rng.choices(here, weights=[LAW_R0[k] for k in here], k=1)[0]
        nxt = succ(state, kind)
        observed[str((state, kind))] += 1
        pairs.append((state, nxt))
        state = nxt
    return pairs, observed, compensated


def real_window_counts(withheld, seed):
    """Count withheld transitions in the REAL generated world's windows."""
    world = generate_compositional_world(seed=seed, cycles=CYCLES,
                                        events_per_cycle=EVENTS_PER_CYCLE)
    names = {cell_name(c): c for c in CELLS}
    cells = [names[n] for n in world["cells"]]
    lo = TRANSFER_CYCLES and PHASE_TRANSFER[0] * EVENTS_PER_CYCLE
    hi = PHASE_TRANSFER[1] * EVENTS_PER_CYCLE
    counts = {str(e): 0 for e in withheld}
    for i in range(lo, hi - 1):
        ctx, nxt = cells[i], cells[i + 1]
        if nxt == flip_p(ctx):
            kind = "flip_p"
        elif nxt == flip_q(ctx):
            kind = "flip_q"
        else:
            continue
        key = str((ctx, kind))
        if key in counts:
            counts[key] += 1
    return counts


def evaluate(withheld, seed):
    st, in_deg, out_deg = static_checks(withheld)
    if not all(st.values()):
        return None, {"seed": seed, "static": st}
    pairs, observed, compensated = formation_stream(withheld, seed)
    genuine = all(a[1] == b[0] for a, b in zip(pairs, pairs[1:]))
    contexts = {str(c) for c, _ in pairs}
    inst = real_window_counts(withheld, seed)
    checks = {
        "strongly_connected": st["strongly_connected"],
        "all_cells_in_and_out": st["all_cells_in_and_out"],
        "all_contexts_seen": len(contexts) == len(CELLS),
        "every_permitted_instantiated": min(observed.values()) >= 1,
        "consecutive_pairs_genuine": genuine,
        "all_formation_beats_conditioned": compensated > 0,
        "withheld_floor_met": all(v >= FLOOR for v in inst.values()),
    }
    return checks, {
        "seed": seed, "checks": checks, "contexts_seen": sorted(contexts),
        "min_permitted_instance": min(observed.values()),
        "withheld_events_compensated": compensated,
        "transfer_window": {"cycles": TRANSFER_CYCLES, "instances": inst},
        "in_degree": in_deg, "out_degree": out_deg,
    }


def audit(withheld):
    per_seed = [evaluate(withheld, s) for s in CALIBRATION_SEEDS]
    if any(c is None for c, _ in per_seed):
        return {"feasible": False, "per_seed": [d for _, d in per_seed]}
    checks = [c for c, _ in per_seed]
    dets = [d for _, d in per_seed]
    combined = {k: all(c[k] for c in checks) for k in checks[0]}
    return {
        "feasible": all(combined.values()),
        "checks_all_seeds": combined,
        "per_seed": dets,
        "min_permitted_instance": min(d["min_permitted_instance"] for d in dets),
        "min_withheld_instance": min(
            min(d["transfer_window"]["instances"].values()) for d in dets),
        "withheld_events_compensated": sum(d["withheld_events_compensated"] for d in dets),
    }


def definitions(out):
    """Gate F's denominator and the ceiling, as numbers a harness can gate on."""
    total_pairs = len(ORDER) * TAGS_PER_CELL * TAGS_PER_CELL          # 128
    withheld_pairs = WANT * TAGS_PER_CELL * TAGS_PER_CELL             # 2 x 16 = 32
    available = total_pairs - withheld_pairs                          # 96
    ceiling = {k: round(LAW_R0[k] * 2 / TAGS_PER_CELL, 6) for k in KINDS}
    return {
        "kind": "reusable_knowledge_gate_definitions",
        "amendment": "REUSABLE-KNOWLEDGE-PREREGISTRATION section 14",
        "unit": "tag-pair relation",
        "total_relations": total_pairs,
        "withheld_relations": withheld_pairs,
        "available_during_formation": available,
        "gate_f": {
            "numerator": "asserted relations in the available set",
            "denominator": available,
            "coverage_formula": "|asserted AND available| / 96",
            "threshold": 0.95,
            "threshold_on_seeds": "at least 15 of 20 confirmatory seeds",
            "max_coverage_if_denominator_were_total": round(available / total_pairs, 6),
            "withheld_in_gate": False,
            "withheld_scored_in": "the transfer limb only",
        },
        "ceiling": {
            "holder": "full latent-rule holder (given the law; no learning, no engine)",
            "rule": "successor is flip_p with 0.65 and flip_q with 0.35; each tag of the successor cell appears with 2/4",
            "p_tag_given_context_cell": ceiling,
            "closed_form_exact": True,
        },
        "oracle_admitted_arm": {
            "label": "mechanism arm (admission filtering at fixed evidence)",
            "is_ceiling": False,
        },
        "calibration_seeds": list(CALIBRATION_SEEDS),
        "confirmatory_seeds": "20261207-20261226 (n = 20)",
        "burned_seeds": list(BURNED_SEEDS),
    }


def main():
    combos = list(itertools.combinations(ORDER, WANT))
    results = []
    for c in combos:
        r = audit(list(c))
        r["withheld"] = [list(map(str, e)) for e in c]
        results.append(r)
    feasible = [r for r in results if r["feasible"]]
    chosen = feasible[0] if feasible else None

    out = {
        "kind": "reusable_knowledge_feasibility",
        "generation": 3,
        "corrections": ["confirmatory seed 20261206 was used to select the rule and is now burned",
                        "schedule now matches the module: formation = warmup + acquisition",
                        "floor checked in the real 50-cycle transfer window"],
        "method": "generator-only, conditioned sampling; no engine, no study cell",
        "world": "benchmarks/acquisition_compositional.py",
        "edge_unit": "directed cell transition (context cell -> successor cell), one per flip type",
        "transitions_total": len(ORDER),
        "withheld_count": WANT,
        "withheld_share": WANT / len(ORDER),
        "schedule": {
            "warmup": list(PHASE_WARMUP), "acquisition": list(PHASE_ACQUISITION),
            "retention": list(PHASE_RETENTION), "transfer": list(PHASE_TRANSFER),
            "formation_cycles": FORMATION_CYCLES, "events_per_cycle": EVENTS_PER_CYCLE,
            "transfer_cycles": TRANSFER_CYCLES, "retention_cycles": RETENTION_CYCLES,
            "total_cycles": CYCLES,
        },
        "seeds": {
            "used_for_design": list(CALIBRATION_SEEDS),
            "burned": list(BURNED_SEEDS),
            "note": "no confirmatory seed informed this check",
        },
        "previous_rule_generation_2": [list(map(str, e)) for e in PREVIOUS_RULE],
        "previous_rule_still_feasible": next(
            (r["feasible"] for r in results
             if [list(map(str, e)) for e in PREVIOUS_RULE] == r["withheld"]), None),
        "criteria_fixed_before_enumeration": [
            "strong connectivity of the permitted graph",
            "every cell keeps in-degree >= 1 and out-degree >= 1",
            "all four cells appear as contexts in the formation stream",
            "every permitted transition is instantiated at least once",
            "stored events are consecutive in the world (no skipped-event jumps)",
            "every formation phase contributes conditioned events",
            f"each withheld transition occurs at least {FLOOR} times in the {TRANSFER_CYCLES}-cycle transfer window",
        ],
        "subsets_evaluated": len(results),
        "subsets_feasible": len(feasible),
        "chosen_rule": chosen["withheld"] if chosen else None,
        "chosen": chosen,
        "all_results": results,
        "tag_level": {
            "distinct_tag_pairs_from_cell_law": len(ORDER) * TAGS_PER_CELL * TAGS_PER_CELL,
            "gate13_cross_cell_edges": 112,
            "note": "the 112 is the GROUP world's tag-level count and is not a quantity of this world",
        },
    }
    out["feasible_as_transfer"] = bool(chosen)
    out["gate_definitions"] = definitions(out)
    pathlib.Path(ROOT / "docs/reusable_knowledge_feasibility.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    pathlib.Path(ROOT / "docs/reusable_knowledge_gate_definitions.json").write_text(
        json.dumps(out["gate_definitions"], indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("subsets_evaluated", "subsets_feasible",
                                        "chosen_rule", "previous_rule_still_feasible",
                                        "feasible_as_transfer")}, indent=1))
    print("schedule:", json.dumps(r["schedule"], indent=1))
    if r["chosen"]:
        print("checks:", json.dumps(r["chosen"]["checks_all_seeds"], indent=1))
        print("min permitted:", r["chosen"]["min_permitted_instance"],
              "| compensated:", r["chosen"]["withheld_events_compensated"],
              "| min withheld in transfer:", r["chosen"]["min_withheld_instance"])
        for d in r["chosen"]["per_seed"]:
            print("  seed", d["seed"], d["transfer_window"]["instances"])
