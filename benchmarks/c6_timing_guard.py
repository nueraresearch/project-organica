"""Guard the C6-TIMING-1 block against a confirmation the record does not support.

The block's outcome is not a label to trust. This guard reads the frozen
preregistration, the six per-seed harness parts, the fresh-process determinism
rerun and the block summary, then recomputes the per-order floors and the
N1-N7 gates. A confirmed outcome is accepted only when all of them hold.

Run:

    python -m benchmarks.c6_timing_guard --check
    python -m benchmarks.c6_timing_guard --self-test

``--self-test`` proves the guard can fail by tampering with a copy of the
committed evidence in memory; it writes nothing.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from benchmarks import c6_timing_observer
from benchmarks import engine_pin

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs" / "c6_timing_prereg.json"
BLOCK = ROOT / "docs" / "c6_timing_block.json"
PARTS = ROOT / "docs" / "c6_timing_parts"

ORDERED = ("K_BEFORE_Y_IND", "Y_IND_BEFORE_K", "SAME_CYCLE")
GATES = (
    "N1_neutrality",
    "N2_mutation",
    "N3_parity",
    "N4_coverage",
    "N5_engine",
    "N6_order_variation",
    "N7_determinism",
)
CONFIRMED = "C6 ORDER VARIATION CONFIRMED"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_sources() -> tuple[dict, dict, dict[int, dict], dict]:
    prereg = _load(PREREG)
    block = _load(BLOCK)
    seeds = [int(seed) for seed in prereg.get("design", {}).get("seeds", [])]
    parts = {seed: _load(PARTS / ("%d.json" % seed)) for seed in seeds}
    determinism = _load(PARTS / ("%d_determinism.json" % seeds[0])) if seeds else {}
    return prereg, block, parts, determinism


def _ordered(rows: list[dict]) -> list[dict]:
    return [
        row for row in rows
        if row.get("first_k") is not None and row.get("first_y_ind") is not None
    ]


def _class_sum(part: dict) -> int:
    classes = part.get("classes") or {}
    return sum(int(classes.get(name, 0)) for name in ORDERED)


def problems(
    prereg: dict,
    block: dict,
    parts: dict[int, dict],
    determinism: dict,
    *,
    pin_problems: list[str] | None = None,
    harness: dict | None = None,
) -> list[str]:
    """Every reason the committed evidence cannot support a confirmation."""
    found: list[str] = []

    if prereg.get("id") != "C6-TIMING-1":
        found.append("the preregistration does not identify C6-TIMING-1")
    if block.get("id") != "C6-TIMING-1":
        found.append("the block does not identify C6-TIMING-1")
    if prereg.get("status") != "FROZEN, RUN":
        found.append("the preregistration is not FROZEN, RUN")
    if block.get("status") != "RUN":
        found.append("the block is not RUN")

    design = prereg.get("design") or {}
    seeds = [int(seed) for seed in design.get("seeds") or []]
    if len(seeds) != 6:
        found.append("the preregistration does not fix six seeds")
    if sorted(parts) != sorted(seeds):
        found.append("the per-seed parts do not match the preregistered seeds")
    if block.get("seeds") != seeds:
        found.append("the block summary does not name the preregistered seeds")
    if block.get("cycles") != design.get("cycles"):
        found.append("the block summary changes the preregistered cycle count")
    if block.get("cap") != design.get("cap"):
        found.append("the block summary changes the preregistered cap")
    if block.get("cells") != design.get("cells"):
        found.append("the block summary changes the preregistered cell count")
    if design.get("preflight_seed_excluded") in seeds:
        found.append("the preflight seed is inside the confirmatory block")

    criteria = prereg.get("criteria") or {}
    floor = int(criteria.get("min_per_order_per_seed", 0))
    coverage = int(criteria.get("min_seeds_with_both_orders", 0))
    if floor < 1:
        found.append("the preregistration has no positive per-order floor")
    if coverage < 1 or coverage > len(seeds):
        found.append("the preregistration has an impossible seed-coverage rule")

    block_by_seed = {
        int(row.get("seed")): row for row in block.get("per_seed") or []
        if isinstance(row, dict) and row.get("seed") is not None
    }
    both = 0
    totals = {name: 0 for name in ORDERED}
    for seed in seeds:
        part = parts.get(seed) or {}
        if int(part.get("seed", -1)) != seed:
            found.append("seed %d part names the wrong seed" % seed)
            continue
        if part.get("cycles") != design.get("cycles"):
            found.append("seed %d part changes the cycle count" % seed)
        if part.get("cap") != design.get("cap"):
            found.append("seed %d part changes the cap" % seed)

        gates = part.get("gates") or {}
        for gate in ("N1_neutrality", "N3_parity", "N6_order_variation"):
            if gates.get(gate) is not True:
                found.append("seed %d fails %s" % (seed, gate))

        classes = part.get("classes") or {}
        k_before = int(classes.get("K_BEFORE_Y_IND", 0))
        y_before = int(classes.get("Y_IND_BEFORE_K", 0))
        totals["K_BEFORE_Y_IND"] += k_before
        totals["Y_IND_BEFORE_K"] += y_before
        totals["SAME_CYCLE"] += int(classes.get("SAME_CYCLE", 0))
        if k_before < floor:
            found.append("seed %d has %d K_BEFORE_Y_IND, below the floor of %d"
                         % (seed, k_before, floor))
        if y_before < floor:
            found.append("seed %d has %d Y_IND_BEFORE_K, below the floor of %d"
                         % (seed, y_before, floor))
        if k_before > 0 and y_before > 0:
            both += 1

        rows = part.get("rows") or []
        ordered = _ordered(rows)
        from_rows = {name: 0 for name in ORDERED}
        for row in rows:
            name = row.get("class_") or row.get("class")
            if name in from_rows:
                from_rows[name] += 1
        if from_rows != {name: int(classes.get(name, 0)) for name in ORDERED}:
            found.append("seed %d class counts do not match its rows" % seed)
        if len(ordered) != _class_sum(part):
            found.append("seed %d N4 order counts do not match the ordered rows" % seed)
        if part.get("y_ind_edges", 0) <= 0:
            found.append("seed %d has no Y_ind edge" % seed)
        if int(part.get("y_ind_edges", 0)) > len(rows):
            found.append("seed %d reports more Y_ind edges than rows" % seed)

        summary = block_by_seed.get(seed) or {}
        if summary.get("classes") != classes:
            found.append("seed %d summary classes do not match the harness part" % seed)

    if both < coverage:
        found.append("both orders occur on %d seeds, below the required %d" % (both, coverage))
    block_totals = block.get("totals") or {}
    for name in ORDERED:
        if int(block_totals.get(name, -1)) != totals[name]:
            found.append("the block total for %s does not match the parts" % name)

    if block_by_seed.keys() != set(seeds):
        found.append("the block summary does not carry exactly the six seed rows")

    pin_problems = engine_pin.compare(engine_pin.load_pin()) if pin_problems is None else pin_problems
    if pin_problems:
        found.extend("engine pin: %s" % problem for problem in pin_problems)
    if harness is None:
        harness = c6_timing_observer.self_test()
    if (harness.get("gates") or {}).get("N2_mutation_fails") is not True:
        found.append("the mutation harness did not pass N2")

    if not determinism:
        found.append("the fresh-process determinism rerun is missing")
    elif (
        determinism.get("seed") != seeds[0]
        or parts.get(seeds[0], {}).get("rows") != determinism.get("rows")
        or parts.get(seeds[0], {}).get("classes") != determinism.get("classes")
    ):
        found.append("the fresh-process determinism rerun does not reproduce seed %d" % seeds[0])

    block_gates = block.get("gates") or {}
    for gate in GATES:
        if block_gates.get(gate) is not True:
            found.append("the block summary does not pass %s" % gate)

    if block.get("outcome") == CONFIRMED and found:
        found.append("the block reports confirmation despite the failures above")
    if block.get("outcome") != CONFIRMED and not found:
        found.append("the block meets the gates but does not report confirmation")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the committed block")
    parser.add_argument("--self-test", action="store_true", help="prove the guard can fail")
    args = parser.parse_args(argv)
    if not args.check and not args.self_test:
        parser.error("choose --check or --self-test")

    prereg, block, parts, determinism = load_sources()
    harness = c6_timing_observer.self_test()
    found = problems(prereg, block, parts, determinism, harness=harness)
    if args.check:
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print(
            "C6-TIMING-1 guard: pass; %d seeds, floors %d/%d, totals %d/%d/%d"
            % (
                len(parts),
                (prereg.get("criteria") or {}).get("min_per_order_per_seed", 0),
                (prereg.get("criteria") or {}).get("min_seeds_with_both_orders", 0),
                (block.get("totals") or {}).get("K_BEFORE_Y_IND", 0),
                (block.get("totals") or {}).get("Y_IND_BEFORE_K", 0),
                (block.get("totals") or {}).get("SAME_CYCLE", 0),
            )
        )
        return 0

    if found:
        print("FAIL: the committed block does not pass its own guard:")
        for problem in found:
            print(" -", problem)
        return 1

    seed = sorted(parts)[0]
    bad_parts = copy.deepcopy(parts)
    bad_parts[seed]["classes"]["K_BEFORE_Y_IND"] = 9
    floor_found = problems(prereg, block, bad_parts, determinism, harness=harness)
    if not any("below the floor" in problem for problem in floor_found):
        print("FAIL: the floor tamper was not caught")
        return 1

    bad_block = copy.deepcopy(block)
    bad_block["gates"]["N1_neutrality"] = False
    gate_found = problems(prereg, bad_block, parts, determinism, harness=harness)
    if not any("does not pass N1_neutrality" in problem for problem in gate_found):
        print("FAIL: the gate tamper was not caught")
        return 1

    bad_determinism = copy.deepcopy(determinism)
    if bad_determinism.get("rows"):
        bad_determinism["rows"][0]["first_k"] = None
    determinism_found = problems(prereg, block, parts, bad_determinism, harness=harness)
    if not any("determinism" in problem for problem in determinism_found):
        print("FAIL: the determinism tamper was not caught")
        return 1

    unconfirmed = copy.deepcopy(block)
    unconfirmed["outcome"] = "C6 NOT SEPARATED"
    outcome_found = problems(prereg, unconfirmed, parts, determinism, harness=harness)
    if not any("does not report confirmation" in problem for problem in outcome_found):
        print("FAIL: a passing but unconfirmed block was accepted")
        return 1

    print("C6-TIMING-1 guard self-test: pass (floor, gate, determinism and outcome tampers rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
