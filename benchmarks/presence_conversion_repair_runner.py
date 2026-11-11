"""PRESENCE-CONVERSION-2: the harness the grant was waiting for.

Runs the twelve design cells (six seeds x observer-off/on), the observer-off witness at
seed 20261100 and the fresh-process determinism rerun of the first seed. N1 also needs a
plain `SleepService` reference for every seed, so six reference runs accompany the
fourteen planned runs; they are controls, not cells, and are recorded as such.

    ./.venv/bin/python -m benchmarks.presence_conversion_repair_runner --measure
    ./.venv/bin/python -m benchmarks.presence_conversion_repair_runner --finish
    ./.venv/bin/python -m benchmarks.presence_conversion_repair_runner --check
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from organica.sleep import SleepService

from benchmarks import engine_stamp
from benchmarks import presence_cap_experiment as cap
from benchmarks import presence_conversion_repair as repair
from benchmarks import presence_conversion_repair_observer as observer
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.presence_construct_audit import (ACQ_SOURCE, PHASE_ACQUISITION,
                                                 _digest, _world_compositional_edges,
                                                 asserted_fingerprint)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "presence_conversion_repair_run.json"
PAGE = ROOT / "docs" / "PRESENCE-CONVERSION-2-RESULT.md"
PARTS = ROOT / ".scratch" / "presence_repair" / "parts"
KIND = "presence_conversion_repair_run"
ARMS = ("plain", "off", "on")
RELATIONS = ("transition", "cooccurrence")
WITNESS = 20261100


def prereg() -> dict:
    return repair.prereg()


def design() -> dict:
    return prereg()["design"]


def planned() -> list[tuple[int, str]]:
    body = design()
    cells = [(seed, arm) for seed in body["seeds"] for arm in body["arms"]]
    return cells + [(WITNESS, "off"), (body["seeds"][0], "on")]


def run_cell(seed: int, arm: str, cap_value: int = 40) -> dict:
    if arm not in ARMS:
        raise SystemExit("unknown arm %r" % (arm,))
    cycles = int(design()["cycles"])
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("presence_conversion_repair")
    mem = _CountingMemoryService(str(db_path))
    if arm == "plain":
        svc = SleepService(mem)
        svc.MAX_PREDICTIONS = int(cap_value)
    else:
        svc = observer.RepairedObserverSleepService(mem, observe=(arm == "on"), cap=cap_value)
    windows: list[list[tuple[str, str]]] = []
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, train_flag) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not train_flag:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            mem.store(text, event_type="observe", source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                windows.append([(p.source, p.target) for p in svc.run_sleep_cycle().predictions])
        asserted = {(a, b) for a, targets in
                    structure_edges(svc._load_prior_candidates()).items() for b in targets}
        temporal = {(a, b) for a, b, _c in mem.temporal_edges(min_count=1)}
        store_counts = dict(getattr(mem, "store_counts", {}))
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass
    present = world_edges & temporal
    ever = {edge for window in windows for edge in window} & world_edges
    asserted_world = asserted & world_edges
    cell = {
        "seed": seed, "arm": arm, "cap": int(cap_value), "cycles": len(windows),
        "engine_version": engine_stamp.engine_version(),
        "engine_sha256": engine_stamp.engine_sha256(),
        "world_edges": len(world_edges), "world_digest": _digest(world_edges),
        "present_world_edges": len(present), "present_fingerprint": _digest(present),
        "s_ever_world_edges": len(ever), "s_ever_fingerprint": _digest(ever),
        "asserted_world_edges": len(asserted_world),
        "asserted_fingerprint": asserted_fingerprint(asserted),
        "asserted_world_fingerprint": _digest(asserted_world),
        "served_fingerprint": _digest([edge for window in windows for edge in window]),
        "windows": [[list(edge) for edge in window] for window in windows],
        "windows_world": [["%s>%s" % edge for edge in window if edge in world_edges]
                          for window in windows],
        "present_edges": sorted([list(edge) for edge in present]),
        "ever_edges": sorted([list(edge) for edge in ever]),
        "asserted_edges": sorted([list(edge) for edge in asserted_world]),
        "universe": [[dict(row) for row in cycle] for cycle in getattr(svc, "universe", [])],
        "allocation": [dict(row) for row in getattr(svc, "allocation", [])],
        "store_counts": store_counts,
    }
    return engine_stamp.stamp(cell)


def part_path(seed: int, arm: str, label: str = "") -> Path:
    return PARTS / ("%d-%s%s.json" % (seed, arm, label))


def measure(force: bool = False) -> int:
    PARTS.mkdir(parents=True, exist_ok=True)
    body = design()
    jobs = [(seed, "plain", "") for seed in body["seeds"]]
    jobs += [(seed, arm, "") for seed, arm in planned()[:-1]]
    jobs += [(body["seeds"][0], "on", "-rerun")]
    for seed, arm, label in jobs:
        path = part_path(seed, arm, label)
        if path.exists() and not force:
            print("have %s" % path.name); continue
        cell = run_cell(seed, arm)
        path.write_text(json.dumps(cell), encoding="utf-8")
        print("ran %s: %d cycles, %d served-world" % (path.name, cell["cycles"],
                                                      cell["s_ever_world_edges"]))
    return 0


def load(seed: int, arm: str) -> dict:
    path = part_path(seed, arm)
    if not path.exists():
        raise SystemExit("missing part %s; run --measure" % path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def _edges(cell: dict, key: str) -> set[tuple[str, str]]:
    return {tuple(edge) for edge in cell[key]}


def adjudicate(parts: dict) -> dict:
    body = design()
    seeds = list(body["seeds"])
    gates: dict[str, dict] = {}

    n1_fail = []
    for seed in seeds:
        if load(seed, "on")["windows"] != load(seed, "plain")["windows"]:
            n1_fail.append(seed)
    gates["N1_served_is_engine"] = {"passed": not n1_fail, "failed_seeds": n1_fail}

    leak = []
    for seed in seeds:
        off, on = load(seed, "off"), load(seed, "on")
        diff = observer.differs({"windows": [tuple(w) for w in off["windows"]],
                                 "asserted": [tuple(e) for e in off["asserted_edges"]],
                                 "store_counts": off["store_counts"]},
                                {"windows": [tuple(w) for w in on["windows"]],
                                 "asserted": [tuple(e) for e in on["asserted_edges"]],
                                 "store_counts": on["store_counts"]})
        if diff:
            leak.append({"seed": seed, "channels": diff})
    gates["N2_observation_cannot_leak"] = {"passed": not leak, "leaks": leak}

    n3_fail = []
    for seed in seeds:
        on = load(seed, "on")
        if not on["universe"] or len(on["allocation"]) != on["cycles"]:
            n3_fail.append({"seed": seed, "why": "no universe"}); continue
        for index, (window, cycle, counts) in enumerate(
                zip(on["windows"], on["universe"], on["allocation"])):
            served = {tuple(edge) for edge in window}
            rows = {tuple(row["edge"]): row for row in cycle}
            if not served <= set(rows):
                n3_fail.append({"seed": seed, "cycle": index + 1, "why": "served not in universe"})
            if any(rows[edge]["relation"] not in RELATIONS for edge in served
                   if edge in rows):
                n3_fail.append({"seed": seed, "cycle": index + 1, "why": "served row has no relation"})
            if not counts.get("sum_matches") or counts.get("served") != len(window):
                n3_fail.append({"seed": seed, "cycle": index + 1, "why": "allocation disagrees"})
    gates["N3_allocation_recorded"] = {"passed": not n3_fail, "failures": n3_fail}

    stage, n4_fail = [], []
    cap_value = int(prereg()["engine"]["cap"])
    for seed in seeds:
        on = load(seed, "on")
        row = stage_row(on, cap_value)
        present = _edges(on, "present_edges")
        imputed = sorted(_edges(on, "asserted_edges") - present)
        if not present:
            n4_fail.append({"seed": seed, "why": "zero present denominator"})
        if imputed:
            n4_fail.append({"seed": seed, "why": "asserted edge not present", "edges": len(imputed)})
        if row["constructed"] + row["below_minimum"] != row["present"]:
            n4_fail.append({"seed": seed, "why": "an edge is in no bucket"})
        if (row["never_served_within_transition_budget"] + row["never_served_rank_half_to_cap"]
                + row["never_served_rank_above_cap"]) != row["never_served"]:
            n4_fail.append({"seed": seed, "why": "the rank bands do not sum"})
        stage.append(dict(row, seed=seed))
    gates["N4_stage_complete"] = {"passed": not n4_fail, "failures": n4_fail}
    semantics = rank_semantics(seeds, cap_value)
    semantics["never_served_within_transition_budget"] = sum(
        row["never_served_within_transition_budget"] for row in stage)
    semantics["never_served_relations"] = sorted(
        name for name in RELATIONS + ("unknown",)
        if any(row["never_served_relations"][name] for row in stage))

    audit = json.loads((ROOT / "docs" / "presence_assertion_audit_0.14.0.json")
                       .read_text(encoding="utf-8"))
    row = [item for item in audit["rows"] if item["seed"] == WITNESS][0]
    witness = load(WITNESS, "off")
    n5 = {"witness_seed": WITNESS, "expected": {
        "present_world_edges": row["present_world_edges"],
        "asserted_world_edges": row["asserted_world_edges"],
        "asserted_fingerprint": row["asserted_fingerprint"]},
        "observed": {"present_world_edges": witness["present_world_edges"],
                     "asserted_world_edges": witness["asserted_world_edges"],
                     "asserted_fingerprint": witness["asserted_fingerprint"]}}
    n5["passed"] = all(n5["expected"][key] == n5["observed"][key] for key in n5["expected"])
    gates["N5_witness_reproduces_audit"] = n5

    # The block's own records are not consumers: freshness was proved before the result was
    # written, and the prereg and result name the block by definition.
    allow = (repair.PREREG, repair.DOC, repair.N3_ARTIFACT, repair.UNEXPLAINED_ARTIFACT,
             repair.PROBE_ARTIFACT, repair.TURNOVER_ARTIFACT, ARTIFACT)
    collisions = cap.seed_collisions(seeds + [body["bootstrap"]], allow=allow)
    world_diff = [seed for seed in seeds if
                  load(seed, "off")["world_digest"] != load(seed, "on")["world_digest"]]
    gates["N6_seed_axis"] = {"passed": not collisions and not world_diff,
                             "collisions": sorted(collisions), "world_diffs": world_diff,
                             "bootstrap": body["bootstrap"]}

    first = seeds[0]
    rerun = json.loads(part_path(first, "on", "-rerun").read_text(encoding="utf-8"))
    original = json.loads(part_path(first, "on").read_text(encoding="utf-8"))
    gates["N7_determinism"] = {"passed": rerun["windows"] == original["windows"],
                               "seed": first,
                               "fingerprint": rerun["served_fingerprint"]}

    if not gates["N1_served_is_engine"]["passed"]:
        verdict, reading = "SERVED NOT ENGINE", "The wiring is not what the record claims; nothing about conversion is measured."
        decision = "Void the block; fix the wiring and register a new block, never re-read this one."
    elif not gates["N2_observation_cannot_leak"]["passed"]:
        verdict, reading = "OBSERVATION LEAKS", "The double-call construction is not observation-only."
        decision = "Void the block; conversion needs a different instrument."
    elif not all(gates[name]["passed"] for name in gates if name.startswith(("N3", "N4", "N5", "N6", "N7"))):
        verdict, reading = "VOID", "The record is incomplete or non-reproducible and no stage table is read."
        decision = "Fix the harness and register a new block."
    else:
        verdict = "CONVERSION STAGE MEASURED"
        lost = [row for row in stage if row["never_served"]]
        reading = (("The stage table locates the loss at admission: %d of %d present edges became "
                    "candidates (C) and %d-%d per seed were never served, so construction is not the "
                    "step that loses them. This is a measurement of the path, not a capability result.")
                   % (sum(row["constructed"] for row in stage), sum(row["present"] for row in stage),
                      min(row["never_served"] for row in lost),
                      max(row["never_served"] for row in lost)) if lost else
                   "Every present world edge became a candidate and was served on these seeds.")
        decision = ("Report the stage table; the next step is an owner decision on the named step, "
                    "with no engine change implied.")
    return engine_stamp.stamp({
        "kind": KIND, "prereg": repair.PREREG_ID,
        "cells": [{"seed": seed, "arm": arm, "cycles": load(seed, arm)["cycles"],
                   "present": load(seed, arm)["present_world_edges"],
                   "s_ever": load(seed, arm)["s_ever_world_edges"],
                   "a_w": load(seed, arm)["asserted_world_edges"],
                   "served_fingerprint": load(seed, arm)["served_fingerprint"]}
                  for seed in seeds for arm in body["arms"]],
        "stage_table": stage, "rank_semantics": semantics, "gates": gates, "verdict": verdict,
        "reading": reading, "decision": decision,
        "runs_executed": len(planned()) + len(seeds),
        "controls": {"plain_references": len(seeds), "witness": 1, "determinism_rerun": 1},
        "not_evidence": ("A stage measurement on six seeds; it is not a capability, retention or "
                         "transfer result."),
    })


def rank_semantics(seeds: list[int], cap_value: int) -> dict:
    """What a recorded universe rank is: a position in the ceiling call's list, not an
    admission position. The list concatenates every transition (schema prior, target entropy,
    transition probability, count) before every cooccurrence (count-ranked), so a cooccurrence's
    rank is offset by the whole transition block that the shipped call never builds."""
    cycles = subsequence = trans_prefix = cooc_prefix = blocked = unlabelled = 0
    max_trans_rank = max_cooc_rank = max_block = max_alloc = 0
    for seed in seeds:
        on = load(seed, "on")
        for window, cycle, alloc in zip(on["windows"], on["universe"], on["allocation"]):
            cycles += 1
            served = [tuple(edge) for edge in window]
            served_set = set(served)
            order = [tuple(row["edge"]) for row in cycle]
            rank_of = {tuple(row["edge"]): int(row["rank"]) for row in cycle}
            trans = [tuple(row["edge"]) for row in cycle if row["relation"] == "transition"]
            cooc = [tuple(row["edge"]) for row in cycle if row["relation"] == "cooccurrence"]
            if [edge for edge in order if edge in served_set] == served:
                subsequence += 1
            served_trans = [rank_of[edge] for edge in trans if edge in served_set]
            if served_trans == list(range(1, len(served_trans) + 1)):
                trans_prefix += 1
            if [rank_of[edge] for edge in cooc if edge in served_set] == \
                    [rank_of[edge] for edge in cooc[:len([e for e in cooc if e in served_set])]]:
                cooc_prefix += 1
            max_trans_rank = max([max_trans_rank] + served_trans)
            max_cooc_rank = max([max_cooc_rank] + [rank_of[edge] for edge in cooc
                                                  if edge in served_set])
            max_block = max(max_block, len(trans))
            max_alloc = max(max_alloc, int(alloc.get("transitions") or 0))
            names = [row["relation"] for row in cycle]
            unlabelled += sum(1 for name in names if name == "unknown")
            if names == ([name for name in names if name == "transition"]
                         + [name for name in names if name == "cooccurrence"]):
                blocked += 1
    never_in_cap = unexp_in_cap = 0
    never_in_cap_within = unexp_in_cap_within = 0
    closest = None
    for seed in seeds:
        on = load(seed, "on")
        present = _edges(on, "present_edges")
        asserted = _edges(on, "asserted_edges")
        ever = _edges(on, "ever_edges")
        best: dict[tuple[str, str], tuple[int, int]] = {}
        served_transitions: list[int] = []
        for index, (window, cycle) in enumerate(zip(on["windows"], on["universe"])):
            served = {tuple(edge) for edge in window}
            served_transitions.append(sum(
                1 for row in cycle
                if row["relation"] == "transition" and tuple(row["edge"]) in served))
            for row in cycle:
                edge = tuple(row["edge"])
                rank = int(row["rank"])
                if edge not in best or rank < best[edge][0]:
                    best[edge] = (rank, index)
        groups = (("never", present - ever), ("unexplained", (present & asserted) - ever))
        for name, group in groups:
            for edge in group:
                if edge not in best:
                    continue
                rank, index = best[edge]
                if rank > int(cap_value):
                    continue
                if name == "never":
                    never_in_cap += 1
                else:
                    unexp_in_cap += 1
                gap = rank - served_transitions[index]
                if gap <= 0:
                    if name == "never":
                        never_in_cap_within += 1
                    else:
                        unexp_in_cap_within += 1
                else:
                    closest = gap if closest is None else min(closest, gap)
    return {"cycles": cycles, "served_is_order_subsequence": subsequence,
            "served_transitions_are_prefix": trans_prefix,
            "served_cooccurrences_are_prefix": cooc_prefix,
            "max_served_transition_rank": max_trans_rank,
            "max_served_cooccurrence_rank": max_cooc_rank,
            "max_transition_block": max_block, "max_allocated_transitions": max_alloc,
            "unlabelled_universe_rows": unlabelled,
            "cycles_with_contiguous_relation_blocks": blocked,
            "in_cap_never_served": never_in_cap,
            "in_cap_never_served_within_served_transitions": never_in_cap_within,
            "in_cap_asserted_without_admission": unexp_in_cap,
            "in_cap_asserted_without_admission_within_served_transitions": unexp_in_cap_within,
            "closest_in_cap_miss_gap": closest}


def stage_row(cell: dict, cap_value: int) -> dict:
    """Classify one cell's present world edges against its recorded pre-cap universe.

    `constructed` is C from the frozen chain -- present edges that appear as a candidate in the
    recorded universe -- and not the union of served windows. The first revision of this table
    reported S_ever under the name `constructed` and every never-served edge under the name
    `below minimum`, which read as a construction loss; the recorded universe refutes that.
    """
    present = _edges(cell, "present_edges")
    ever = _edges(cell, "ever_edges")
    asserted = _edges(cell, "asserted_edges")
    rank: dict[tuple[str, str], int] = {}
    relation: dict[tuple[str, str], str] = {}
    for cycle in cell.get("universe") or []:
        for row in cycle:
            edge = tuple(row["edge"])
            rank[edge] = min(rank.get(edge, 10 ** 9), int(row["rank"]))
            relation[edge] = row["relation"]
    candidates = present & set(rank)
    below = present - candidates
    never = candidates - ever
    half = max(1, int(cap_value) // 2)
    within_budget = {edge for edge in never if rank[edge] <= half}
    half_to_cap = {edge for edge in never if half < rank[edge] <= int(cap_value)}
    above_cap = {edge for edge in never if rank[edge] > int(cap_value)}
    unexplained = (present & asserted) - ever
    ranks = sorted(rank[edge] for edge in never)
    return {
        "present": len(present), "constructed": len(candidates), "below_minimum": len(below),
        "served_ever": len(ever), "never_served": len(never),
        "never_served_within_transition_budget": len(within_budget),
        "never_served_rank_half_to_cap": len(half_to_cap),
        "never_served_rank_above_cap": len(above_cap),
        "never_served_relations": {name: sum(1 for edge in never if relation[edge] == name)
                                   for name in RELATIONS + ("unknown",)},
        "asserted_final": len(asserted), "unexplained": len(unexplained),
        "never_served_min_rank": ranks[0] if ranks else None,
        "never_served_max_rank": ranks[-1] if ranks else None,
        "never_served_median_rank": ranks[len(ranks) // 2] if ranks else None,
        "below_minimum_edges": sorted("%s>%s" % edge for edge in below),
    }


def render(art: dict) -> str:
    lines = ["# PRESENCE-CONVERSION-2 -- result", "",
             "**%s.** %s" % (art["verdict"], art["reading"]), "",
             "## Gates", "", "| Gate | Result |", "| --- | --- |"]
    for name, gate in art["gates"].items():
        lines.append("| `%s` | %s |" % (name, "PASS" if gate["passed"] else "FAIL"))
    stage = art["stage_table"]
    best = [row["never_served_min_rank"] for row in stage
            if row["never_served_min_rank"] is not None]
    worst = [row["never_served_max_rank"] for row in stage
             if row["never_served_max_rank"] is not None]
    lines += ["", "## Stage table", "",
              "`C` is the present edges that appear as candidates in the recorded pre-cap universe; "
              "`S_ever` is the union of served windows. `A_W` is the asserted world edges at the end "
              "of the run -- an end-state stock, not a union -- so the S_ever-to-A_W difference is not "
              "read as a loss step. `Unexplained` counts asserted world edges that were never served.",
              "",
              "| Seed | P | C | Below minimum | S_ever | Never admitted | Within 20 | 21-40 | Above 40 | A_W | Unexplained |",
              "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in stage:
        lines.append("| %d | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            row["seed"], row["present"], row["constructed"], row["below_minimum"],
            row["served_ever"], row["never_served"], row["never_served_within_transition_budget"],
            row["never_served_rank_half_to_cap"], row["never_served_rank_above_cap"],
            row["asserted_final"], row["unexplained"]))
    lines.append("| **total** | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
        sum(row["present"] for row in stage), sum(row["constructed"] for row in stage),
        sum(row["below_minimum"] for row in stage), sum(row["served_ever"] for row in stage),
        sum(row["never_served"] for row in stage),
        sum(row["never_served_within_transition_budget"] for row in stage),
        sum(row["never_served_rank_half_to_cap"] for row in stage),
        sum(row["never_served_rank_above_cap"] for row in stage),
        sum(row["asserted_final"] for row in stage), sum(row["unexplained"] for row in stage)))
    sem = art["rank_semantics"]
    lines += ["", "**What a rank is, and is not.** The universe is the ceiling call's list: every "
              "transition precedes every cooccurrence, so a rank is a block position, not an admission "
              "position. Served windows are an order-preserving subsequence of that list in %d/%d "
              "cycles; served transitions are the transition prefix in %d/%d and never rank above %d "
              "(the %d-slot half-budget); served cooccurrences are the cooccurrence prefix in %d/%d, so "
              "their ranks are offset by up to %d transition rows (maximum served rank %d) and cannot "
              "be compared with the cap. %d never-admitted present edges, relation(s) %s, and %d of them "
              "ranked inside the transition budget; of the %d asserted-without-admission edges, %d rank "
              "inside the cap and %d ranked inside the transitions served in its best cycle (the closest "
              "miss is %d rank(s) short). Every recorded row is labelled and the labels form two "
              "contiguous blocks in %d/%d cycles. The label is not inferred: the engine computes it "
              "from its own cooccurrence table and uses the same variable to choose the append list, "
              "a guard test checks that in the source, and the fixture recomputes every row's label "
              "independently with no mismatch."
              % (sem["served_is_order_subsequence"], sem["cycles"],
                 sem["served_transitions_are_prefix"], sem["cycles"],
                 sem["max_served_transition_rank"], sem["max_allocated_transitions"],
                 sem["served_cooccurrences_are_prefix"], sem["cycles"],
                 sem["max_transition_block"], sem["max_served_cooccurrence_rank"],
                 sum(row["never_served"] for row in stage),
                 "/".join(sem["never_served_relations"]) or "none",
                 sem["never_served_within_transition_budget"],
                 sum(row["unexplained"] for row in stage),
                 sem["in_cap_asserted_without_admission"],
                 sem["in_cap_asserted_without_admission_within_served_transitions"],
                 sem["closest_in_cap_miss_gap"],
                 sem["cycles_with_contiguous_relation_blocks"], sem["cycles"]),
              "", "Never-admitted edges: the best rank one ever carried is %d-%d across seeds and the "
              "worst is %d; the per-seed median is %s. Below-minimum edges: %s."
              % (min(best) if best else 0, max(best) if best else 0, max(worst) if worst else 0,
                 ", ".join(str(row["never_served_median_rank"]) for row in stage),
                 "; ".join("%d: %s" % (row["seed"], ", ".join(row["below_minimum_edges"]) or "none")
                 for row in stage if row["below_minimum_edges"]) or "none"),
              "", "## Decision", "", art["decision"], "",
              "Fourteen planned runs (%d design cells, one witness, one determinism rerun) plus %d plain "
              "N1 references. This is a measurement of the path, not a capability result."
              % (len(art["cells"]), art["controls"]["plain_references"]), ""]
    return "\n".join(lines)


def check() -> int:
    if not ARTIFACT.exists():
        print("FAIL: no result artifact; run --finish"); return 1
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    found = []
    if art.get("kind") != KIND: found.append("kind")
    if len(art.get("cells") or []) != 12: found.append("12 cells")
    if page() != PAGE.read_text(encoding="utf-8"): found.append("the page is stale")
    if not art.get("verdict"): found.append("no verdict")
    for problem in found: print("FAIL:", problem)
    if not found: print("conversion-2: %s, %d cells, gates %d/%d" %
                        (art["verdict"], len(art["cells"]),
                         sum(1 for g in art["gates"].values() if g["passed"]), len(art["gates"])))
    return 1 if found else 0


def page() -> str:
    return render(json.loads(ARTIFACT.read_text(encoding="utf-8")))


def finish() -> int:
    art = adjudicate({})
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(art), encoding="utf-8")
    print("verdict: %s" % art["verdict"])
    for name, gate in art["gates"].items():
        print("  %-28s %s" % (name, "PASS" if gate["passed"] else "FAIL"))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measure", action="store_true")
    parser.add_argument("--finish", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cell", nargs=2, metavar=("SEED", "ARM"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.dry_run:
        for seed, arm in planned():
            print("--cell %d %s" % (seed, arm))
        print("--finish")
        return 0
    if args.cell:
        seed, arm = int(args.cell[0]), args.cell[1]
        cell = run_cell(seed, arm)
        PARTS.mkdir(parents=True, exist_ok=True)
        part_path(seed, arm).write_text(json.dumps(cell), encoding="utf-8")
        print("ran %d %s" % (seed, arm))
        return 0
    if args.measure:
        return measure(args.force)
    if args.finish:
        return finish()
    if args.check or not argv:
        return check()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
