"""Conditioned sampler for the preregistered reusable-knowledge study.

This is generator-side infrastructure only. It does not instantiate Organica,
write to a memory database, or run a study cell. The frozen compositional
generator remains unchanged and supplies the per-seed latent tag mapping and
the unmodified held-out windows. Formation is a separate, continuous path under
the same mapping and law, conditioned to omit the two preregistered directed
cell transitions.

Variant and withholding parameters are read from the machine-readable protocol
artifacts rather than duplicated as unexplained numbers.
"""
from __future__ import annotations

import json
import random
import sys
import ast
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp
from benchmarks.acquisition_compositional import (
    CELLS,
    EVENTS_PER_CYCLE,
    LAW_R0,
    LAW_R1,
    PHASE_ACQUISITION,
    PHASE_RETENTION,
    PHASE_TRANSFER,
    REGIME_SWITCH_CYCLE,
    TAGS_PER_CELL,
    TAGS_PER_EVENT,
    CYCLES,
    cell_name,
    flip_p,
    flip_q,
    generate_compositional_world,
)

VARIANT_CONFIG = ROOT / "docs" / "reusable_knowledge_variant.json"
GATE_CONFIG = ROOT / "docs" / "reusable_knowledge_gate_definitions.json"
FEASIBILITY_CONFIG = ROOT / "docs" / "reusable_knowledge_feasibility.json"
FORMATION_SEED_XOR = 0x5EEDC0DE


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def protocol_config() -> tuple[dict[str, Any], dict[str, Any]]:
    """Load the committed variant and gate definitions, validating their fit."""
    variant = _load_json(VARIANT_CONFIG)
    gate = _load_json(GATE_CONFIG)
    if variant.get("name") != "V1.1-cap(1000)" or variant.get("max_predictions") != 1000:
        raise ValueError("The preregistered V1.1-cap configuration is not cap 1,000")
    if variant.get("transfer_floor_per_withheld_transition") != 20:
        raise ValueError("Transfer-window floor disagrees with the preregistered 20-instance minimum")
    if gate.get("available_during_formation") != 96:
        raise ValueError("Gate F denominator does not match the preregistered 96 relations")
    if gate.get("withheld_relations") != 32 or gate.get("total_relations") != 128:
        raise ValueError("Withheld/total relation counts do not match the preregistration")
    sampler = variant.get("conditioned_sampler")
    if not isinstance(sampler, dict):
        raise ValueError("The variant artifact does not declare the conditioned sampler")
    if sampler.get("formation_seed_rule") != "seed XOR 0x5EEDC0DE":
        raise ValueError("Formation RNG derivation disagrees with the variant artifact")
    selected = _load_json(FEASIBILITY_CONFIG).get("chosen_rule")
    configured = sampler.get("withheld_transitions")
    if not isinstance(selected, list) or not isinstance(configured, list):
        raise ValueError("The selected withholding rule is missing from a protocol artifact")
    parsed_selected = sorted((tuple(ast.literal_eval(cell)), kind) for cell, kind in selected)
    parsed_configured = sorted((tuple(item["context_cell"]), item["kind"]) for item in configured)
    if parsed_selected != parsed_configured:
        raise ValueError("Variant withholding rule disagrees with the feasibility artifact")
    return variant, gate


def withheld_transitions() -> frozenset[tuple[tuple[int, int], str]]:
    """Read the adopted transition pair from the machine-readable config."""
    variant = _load_json(VARIANT_CONFIG)
    entries = variant["conditioned_sampler"]["withheld_transitions"]
    return frozenset((tuple(item["context_cell"]), item["kind"]) for item in entries)


def _transition(cell: tuple[int, int], kind: str) -> tuple[int, int]:
    if kind == "flip_p":
        return flip_p(cell)
    if kind == "flip_q":
        return flip_q(cell)
    raise ValueError(f"Unknown transition kind: {kind}")


def _kind(source: tuple[int, int], target: tuple[int, int]) -> str:
    if target == flip_p(source):
        return "flip_p"
    if target == flip_q(source):
        return "flip_q"
    raise ValueError(f"Cells are not one-factor neighbors: {source} -> {target}")


def available_relations(world: dict[str, Any]) -> frozenset[tuple[str, str]]:
    """Return the 96 directed tag-pair relations not withheld from formation."""
    blocked = withheld_transitions()
    tag_map = world["cell_tags"]
    out: set[tuple[str, str]] = set()
    for source in CELLS:
        for kind in ("flip_p", "flip_q"):
            if (source, kind) in blocked:
                continue
            target = _transition(source, kind)
            for left in tag_map[cell_name(source)]:
                for right in tag_map[cell_name(target)]:
                    out.add((left, right))
    if len(out) != 96:
        raise AssertionError(f"Available relation set has {len(out)} members, expected 96")
    return frozenset(out)


def withheld_relations(world: dict[str, Any]) -> frozenset[tuple[str, str]]:
    """Return the 32 directed tag-pair relations held out of formation."""
    tag_map = world["cell_tags"]
    out: set[tuple[str, str]] = set()
    for source, kind in withheld_transitions():
        target = _transition(source, kind)
        for left in tag_map[cell_name(source)]:
            for right in tag_map[cell_name(target)]:
                out.add((left, right))
    if len(out) != 32:
        raise AssertionError(f"Withheld relation set has {len(out)} members, expected 32")
    return frozenset(out)


def _sample_formation(
    *,
    rng: random.Random,
    cell_tags: dict[str, list[str]],
    cycles: int,
    events_per_cycle: int,
) -> dict[str, Any]:
    """Generate all warmup/acquisition events without skipped transitions.

    The exact transition sampler first draws from the unconditioned law. If it
    draws a withheld transition, it resamples from the permitted transitions
    for the current cell using their original relative weights. This is
    distributionally equivalent to conditioning the law and records how often
    conditioning changed the draw.
    """
    formation_end = PHASE_ACQUISITION[1]
    formation_events: list[str] = []
    formation_cells: list[str] = []
    source_cells: list[str] = []
    transition_kinds: list[str] = []
    cycles_for_event: list[int] = []
    resamples_by_cycle: dict[int, int] = {}
    start_cell = CELLS[rng.randrange(len(CELLS))]
    state = start_cell
    blocked = withheld_transitions()

    for cycle in range(cycles):
        regime = (cycle // REGIME_SWITCH_CYCLE) % 2
        law = LAW_R0 if regime == 0 else LAW_R1
        for _ in range(events_per_cycle):
            kinds = ("flip_p", "flip_q")
            kind = rng.choices(kinds, weights=[law[k] for k in kinds], k=1)[0]
            if cycle < formation_end and (state, kind) in blocked:
                permitted = [k for k in kinds if (state, k) not in blocked]
                if not permitted:
                    raise AssertionError(f"No permitted transition from {state}")
                kind = rng.choices(permitted, weights=[law[k] for k in permitted], k=1)[0]
                resamples_by_cycle[cycle] = resamples_by_cycle.get(cycle, 0) + 1

            nxt = _transition(state, kind)
            selected = rng.sample(cell_tags[cell_name(nxt)], TAGS_PER_EVENT)
            formation_events.append(" ".join(sorted(selected)))
            formation_cells.append(cell_name(nxt))
            source_cells.append(cell_name(state))
            transition_kinds.append(kind)
            cycles_for_event.append(cycle)
            state = nxt

    return {
        "events": formation_events,
        "cells": formation_cells,
        "source_cells": source_cells,
        "transition_kinds": transition_kinds,
        "cycles": cycles_for_event,
        "start_cell": cell_name(start_cell),
        "resamples_by_cycle": resamples_by_cycle,
    }


def _pair_transition_counts(
    world: dict[str, Any],
    phase: tuple[int, int],
    events_per_cycle: int,
) -> dict[str, int]:
    """Count consecutive-event transitions exactly as the scoring windows do."""
    cell_names = world["cells"]
    lo = phase[0] * events_per_cycle
    hi = phase[1] * events_per_cycle
    counts = {str((cell_name(c), k)): 0 for c, k in withheld_transitions()}
    # Pair i -> i+1 is labelled by the hidden transition that produced event i+1.
    for i in range(lo, hi - 1):
        source = tuple(map(int, (cell_names[i][1], cell_names[i][3])))
        target = tuple(map(int, (cell_names[i + 1][1], cell_names[i + 1][3])))
        kind = _kind(source, target)
        key = str((cell_name(source), kind))
        if key in counts:
            counts[key] += 1
    return counts


def build_conditioned_study_world(
    seed: int,
    *,
    cycles: int = CYCLES,
    events_per_cycle: int = EVENTS_PER_CYCLE,
) -> dict[str, Any]:
    """Build one seed's common event stream and conditioned formation stream.

    The base generator supplies the world's randomized latent tag mapping and
    the unchanged retention/transfer/revision test windows. The formation path
    is then generated continuously under the same regime-0 law, conditioned on
    the two adopted withheld transitions over warmup plus acquisition. Every
    generated formation event is retained; there is no skip mask or adjacency
    jump. Both streams share the same latent world and tag mapping.
    """
    variant, gate = protocol_config()
    if cycles < PHASE_TRANSFER[1] or cycles < PHASE_RETENTION[1]:
        raise ValueError("Study world must include the complete retention and transfer windows")
    base = generate_compositional_world(
        seed=seed,
        cycles=cycles,
        events_per_cycle=events_per_cycle,
    )
    # Separate, deterministic random stream for the conditioned formation path.
    # The base stream remains the fixed held-out evaluation sample.
    formation_rng = random.Random(seed ^ FORMATION_SEED_XOR)
    formation = _sample_formation(
        rng=formation_rng,
        cell_tags=base["cell_tags"],
        cycles=PHASE_ACQUISITION[1],
        events_per_cycle=events_per_cycle,
    )

    withheld = withheld_transitions()
    formation_pairs = list(zip(formation["cells"], formation["cells"][1:]))
    forbidden_in_formation = []
    for a, b in formation_pairs:
        source = tuple(map(int, (a[1], a[3])))
        target = tuple(map(int, (b[1], b[3])))
        edge = (source, _kind(source, target))
        if edge in withheld:
            forbidden_in_formation.append((a, b))

    if len(formation["events"]) != PHASE_ACQUISITION[1] * events_per_cycle:
        raise AssertionError("Conditioned formation did not generate the full scheduled exposure")
    if forbidden_in_formation:
        raise AssertionError("A withheld transition appeared in conditioned formation")
    warmup_resamples = sum(
        count for cycle, count in formation["resamples_by_cycle"].items()
        if cycle < PHASE_ACQUISITION[0]
    )
    acquisition_resamples = sum(
        count for cycle, count in formation["resamples_by_cycle"].items()
        if PHASE_ACQUISITION[0] <= cycle < PHASE_ACQUISITION[1]
    )
    if not warmup_resamples or not acquisition_resamples:
        raise AssertionError("Both warmup and acquisition must exercise conditioning")

    # The scoreable relation belongs to adjacent event rows, not to the
    # unobserved initial hidden state before event 0.
    transfer_counts = _pair_transition_counts(base, PHASE_TRANSFER, events_per_cycle)
    available = available_relations(base)
    withheld_pairs = withheld_relations(base)
    if len(available) != gate["available_during_formation"]:
        raise AssertionError("Available relation count disagrees with the gate artifact")
    floor = int(variant["transfer_floor_per_withheld_transition"])
    transfer_floor_passed = all(n >= floor for n in transfer_counts.values())

    # Strip the original generator's legacy one-transition storage mask so a
    # future runner cannot accidentally reuse the protocol-rejected skip rule.
    test_world = {
        key: value for key, value in base.items()
        if key not in {"trainable", "withheld", "held_cell", "held_cell_tags", "held_cell_flip_p"}
    }

    return {
        "kind": "reusable_knowledge_conditioned_world",
        "seed": seed,
        "variant": variant["name"],
        "max_predictions": variant["max_predictions"],
        "world": test_world,
        "formation": formation,
        "available_relations": available,
        "withheld_relations": withheld_pairs,
        "withheld_transitions": sorted(
            (cell_name(c), k) for c, k in withheld
        ),
        "formation_audit": {
            "cycles": PHASE_ACQUISITION[1],
            "events_per_cycle": events_per_cycle,
            "events_generated": len(formation["events"]),
            "withheld_transition_instances": 0,
            "conditioned_resamples": sum(formation["resamples_by_cycle"].values()),
            "warmup_resamples": warmup_resamples,
            "acquisition_resamples": acquisition_resamples,
            "both_formation_phases_conditioned": True,
            "conditioned_resamples_by_cycle": formation["resamples_by_cycle"],
            "sampling_seed": seed ^ FORMATION_SEED_XOR,
            "all_events_stored": True,
            "consecutive_event_pairs": len(formation_pairs),
            "forbidden_pairs": len(forbidden_in_formation),
        },
        "transfer_audit": {
            "phase_cycles": list(PHASE_TRANSFER),
            "window_cycles": PHASE_TRANSFER[1] - PHASE_TRANSFER[0],
            "withheld_transition_counts": transfer_counts,
            "minimum_per_transition": min(transfer_counts.values()),
            "required_floor": floor,
            "floor_passed": transfer_floor_passed,
        },
        "legacy_mask_reused": False,
    }


def main() -> None:
    """Generator-only calibration-seed probe; no engine or study cells."""
    variant, _ = protocol_config()
    seeds = variant["gate_f_calibration"]["seeds"]
    worlds = [build_conditioned_study_world(s) for s in seeds]
    summary = {
        "kind": "reusable_knowledge_conditioned_sampler_probe",
        "variant": variant["name"],
        "method": "generator-only; no Organica engine, no memory database, no study cells",
        "formation_rng_rule": variant["conditioned_sampler"]["formation_seed_rule"],
        "calibration_seeds": seeds,
        "confirmatory_seeds_touched": False,
        "seeds": [
            {
                "seed": w["seed"],
                "formation": w["formation_audit"],
                "transfer": w["transfer_audit"],
            }
            for w in worlds
        ],
        "all_transfer_floors_passed": all(w["transfer_audit"]["floor_passed"] for w in worlds),
    }
    out = ROOT / "docs" / "reusable_knowledge_sampler_probe.json"
    summary = engine_stamp.stamp(summary)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": str(out),
        "variant": variant["name"],
        "all_transfer_floors_passed": summary["all_transfer_floors_passed"],
        "per_seed_min_transfer_count": {
            str(w["seed"]): w["transfer_audit"]["minimum_per_transition"] for w in worlds
        },
    }, indent=2))


if __name__ == "__main__":
    main()
