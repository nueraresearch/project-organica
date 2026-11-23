"""Split the non-re-emission reason for a dying edge into admission loss and slot loss.

Pre-registered in ``docs/DECAY-ADMISSION-SLOT-PREREGISTRATION.md``. The engine is unchanged: the
instrument observes the ranked candidate list by calling the engine's own builder twice, once at the
real budget (the call whose result the engine uses) and once with the budget raised above any
candidate set, discarding the raised call's side effects. The real slice is then reconstructed from
the full list with the engine's own stratified rule and must equal the engine's actual selection on
every cycle (G3).

Run::

    python -m benchmarks.decay_admission_slot --run
    python -m benchmarks.decay_admission_slot --render
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

from benchmarks.decay_attribution import (
    CYCLES,
    DEGREE,
    Ledger,
    LedgerMemory,
    _graph,
    stored,
)
from benchmarks.decay_confirmation import _feed, harvest_seeds, temp_db, world_edges
from benchmarks.decay_fix_confirm import lattice_world
from benchmarks.decay_admission_slot_prereg import (
    ARTIFACT_DIGEST_KEY,
    BUCKETS,
    DOMINANT,
    MAJORITY_SEEDS,
    SEEDS,
    protocol_digest,
)
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PREREG = DOCS / "DECAY-ADMISSION-SLOT-PREREGISTRATION.md"
ARTIFACT = DOCS / "decay_admission_slot.json"
PAGE = DOCS / "DECAY-ADMISSION-SLOT.md"
PARTS = DOCS / "decay_admission_slot" / "parts"

ARMS = ("engine", "no_temporal_decay")
BUDGET = 40
ADMISSION = 5
CLASSES = ("below_admission", "slot_loss")


def classify_miss(edge, admitted, emitted, count, admission=ADMISSION):
    """One class per miss, judged only on the engine's own quantities."""
    if edge in emitted:
        return "reemitted"
    if edge in admitted:
        return "slot_loss"
    if int(count) < int(admission):
        return "below_admission"
    return "unexplained"


def label_for(pooled, majority_admission, majority_slot, slot_binding_cycles, gates_ok):
    """The pre-registered decision table. A void outranks every bucket."""
    if not gates_ok:
        return "VOID_INSTRUMENT"
    if slot_binding_cycles == 0:
        return "SLOT_NEVER_BOUND"
    total = sum(pooled.get(name, 0) for name in CLASSES)
    if total <= 0:
        return "VOID_INSTRUMENT"
    admission_share = pooled.get("below_admission", 0) / total
    slot_share = pooled.get("slot_loss", 0) / total
    if admission_share >= DOMINANT and majority_admission >= MAJORITY_SEEDS:
        return "ADMISSION_DOMINANT"
    if slot_share >= DOMINANT and majority_slot >= MAJORITY_SEEDS:
        return "SLOT_DOMINANT"
    return "MIXED"


class SlotLedger(Ledger):
    """Records what the engine admitted, ranked and selected, without changing the selection."""

    def __init__(self, memory, decay_factor):
        super().__init__(memory, decay_factor)
        self.admitted: set[tuple[str, str]] = set()
        self.selected: set[tuple[str, str]] = set()
        self.admitted_count = 0
        self.budget_binding = False
        self.fidelity_failures = 0
        self.first_fidelity_failure: int | None = None

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        actual = super()._build_predictions(temporal, freqs, prior_schemas)
        real_budget = self.MAX_PREDICTIONS
        kept_emitted = dict(self.emitted)
        try:
            self.MAX_PREDICTIONS = 1_000_000
            everything = super()._build_predictions(temporal, freqs, prior_schemas)
        finally:
            self.MAX_PREDICTIONS = real_budget
            self.emitted = kept_emitted

        transitions = [c for c in everything if not c.evidence.get("is_cooccurrence")]
        cooccurrences = [c for c in everything if c.evidence.get("is_cooccurrence")]
        half_cap = real_budget // 2
        chosen = transitions[:half_cap]
        remaining = real_budget - len(chosen)
        chosen = chosen + cooccurrences[:remaining]
        if len(chosen) < real_budget:
            rest = [t for t in transitions[half_cap:] if t not in chosen]
            chosen = chosen + rest[: real_budget - len(chosen)]
        chosen = chosen[:real_budget]

        if [(c.source, c.target) for c in chosen] != [(c.source, c.target) for c in actual]:
            self.fidelity_failures += 1
            if self.first_fidelity_failure is None:
                self.first_fidelity_failure = getattr(self, "current_cycle", None)

        self.admitted = {(c.source, c.target) for c in everything}
        self.selected = {(c.source, c.target) for c in actual}
        self.admitted_count = len(everything)
        self.budget_binding = len(everything) > real_budget
        return actual


def cell(arm: str, seed: int, cycles: int = CYCLES) -> dict:
    events = lattice_world(DEGREE)
    world = world_edges(events)
    factor = 0.95 if arm == "engine" else 1.0
    db = temp_db("adm_slot_%s_%s.db" % (arm, seed))
    db.unlink(missing_ok=True)
    memory = LedgerMemory(db_path=str(db))
    service = SlotLedger(memory, factor)
    service._rng.seed(seed)
    for text in events[:12]:
        memory.store(text, event_type="event", source="seed:bootstrap")

    series: list[dict] = []
    previous: dict[tuple[str, str], float] = {}
    try:
        for cycle in range(cycles):
            service.current_cycle = cycle + 1
            _feed(memory, events, cycle)
            service.begin_cycle()
            memory.decay_calls = []
            service.run_sleep_cycle()
            now = stored(service)
            stable = {e: v for e, v in now.items() if v >= service.STABLE_THRESHOLD}
            hits = [e for e in stable if e in world]
            temporal, _freqs = _graph(memory)
            counts = Counter()
            for edge in previous:
                if edge in stable:
                    continue
                reason = classify_miss(
                    edge, service.admitted, service.emitted,
                    temporal.get(edge, 0), service.PREDICTION_MIN_COUNT,
                )
                counts[reason] += 1
            misses = sum(counts[name] for name in CLASSES) + counts["unexplained"]
            call = memory.decay_calls[-1] if memory.decay_calls else {"factor": None, "rows": 0}
            strengthened, decayed, pruned = service.selection
            series.append({
                "cycle": cycle + 1,
                "stable": len(stable),
                "hits": len(hits),
                "coverage": round(len(hits) / len(world), 4) if world else None,
                "theories": int(getattr(service, "theories", 0)),
                "beliefs": int(getattr(service, "beliefs", 0)),
                "strengthened": strengthened,
                "decayed": decayed,
                "pruned": pruned,
                "emitted": len(service.emitted),
                "admitted": service.admitted_count,
                "selected": len(service.selected),
                "budget_binding": bool(service.budget_binding),
                "fidelity_failures": service.fidelity_failures,
                "admitted_at_floor": sum(
                    1 for count in temporal.values() if count >= service.PREDICTION_MIN_COUNT
                ),
                "temporal_sum": sum(temporal.values()),
                "temporal_max": max(temporal.values()) if temporal else 0,
                "below_admission": counts["below_admission"],
                "slot_loss": counts["slot_loss"],
                "unexplained": counts["unexplained"],
                "reemitted": counts["reemitted"],
                "misses": misses,
                "decay_factor": call.get("factor"),
                "decay_rows": call.get("rows"),
            })
            previous = stable
    finally:
        memory.close()
        db.unlink(missing_ok=True)

    peak = max((row["stable"] for row in series), default=0)
    peak_hits = max((row["hits"] for row in series), default=0)
    final = series[-1]["stable"] if series else None
    first_zero = next((row["cycle"] for row in series if row["stable"] == 0), None)
    summary = {
        "arm": arm,
        "seed": seed,
        "degree": DEGREE,
        "cycles": cycles,
        "budget": BUDGET,
        "admission": ADMISSION,
        "world_edges": len(world),
        "decay_factor_set": factor,
        "peak": peak,
        "peak_hits": peak_hits,
        "peak_coverage": round(peak_hits / len(world), 4) if world else None,
        "final": final,
        "first_zero_cycle": first_zero,
        "misses": sum(row["misses"] for row in series),
        "below_admission": sum(row["below_admission"] for row in series),
        "slot_loss": sum(row["slot_loss"] for row in series),
        "unexplained": sum(row["unexplained"] for row in series),
        "reemitted": sum(row["reemitted"] for row in series),
        "binding_cycles": sum(1 for row in series if row["budget_binding"]),
        "admitted_max": max((row["admitted"] for row in series), default=0),
        "fidelity_failures": series[-1]["fidelity_failures"] if series else 0,
        "decay_factor_seen": sorted({row["decay_factor"] for row in series}, key=str),
        "decay_rows_min": min((row["decay_rows"] or 0) for row in series) if series else 0,
        "series": series,
    }
    return summary


def _path(arm: str, seed: int) -> Path:
    return PARTS / ("cell_%s_s%d.json" % (arm, seed))


def run(seeds=SEEDS) -> int:
    used = harvest_seeds(DOCS) - set(SEEDS)
    overlap = sorted(set(seeds) & used)
    if overlap:
        raise SystemExit("seed block overlaps an existing record under docs/: %s" % overlap)
    PARTS.mkdir(parents=True, exist_ok=True)
    for arm in ARMS:
        for seed in seeds:
            path = _path(arm, seed)
            if path.exists():
                print("cached", path.name, flush=True)
                continue
            row = cell(arm, seed)
            path.write_text(json.dumps(engine_stamp.stamp(row), indent=2) + "\n", encoding="utf-8")
            print(
                "%-17s s%d  peak=%2d final=%2d misses=%3d below=%3d slot=%3d bind=%3d"
                % (arm, seed, row["peak"], row["final"], row["misses"],
                   row["below_admission"], row["slot_loss"], row["binding_cycles"]),
                flush=True,
            )
    return 0


def load_parts(seeds=SEEDS) -> list[dict]:
    rows = []
    for arm in ARMS:
        for seed in seeds:
            path = _path(arm, seed)
            if not path.exists():
                raise SystemExit("missing cell %s; run the study first" % path.name)
            rows.append(json.loads(path.read_text(encoding="utf-8")))
    return rows


def analyse(rows: list[dict]) -> dict:
    engine = [r for r in rows if r["arm"] == "engine"]
    control = [r for r in rows if r["arm"] == "no_temporal_decay"]
    pooled = Counter()
    for row in engine:
        for name in CLASSES + ("unexplained",):
            pooled[name] += row[name]
    total = sum(pooled[name] for name in CLASSES)
    shares = {name: round(pooled[name] / total, 4) if total else None for name in CLASSES}
    majority_admission = sum(1 for r in engine if r["below_admission"] > r["slot_loss"])
    majority_slot = sum(1 for r in engine if r["slot_loss"] > r["below_admission"])

    g1 = all(
        set(r["decay_factor_seen"]) == {0.95} and r["decay_rows_min"] > 0 for r in engine
    ) and all(set(r["decay_factor_seen"]) == {1.0} for r in control)
    g2 = all(r["peak"] == 35 and r["peak_coverage"] == 0.5833 for r in engine)
    g3 = all(r["fidelity_failures"] == 0 for r in rows)
    g4 = all(r["misses"] >= 1 for r in engine)
    g5 = all(r["unexplained"] == 0 for r in rows)
    slot_binding_cycles = sum(r["binding_cycles"] for r in engine)
    gates_ok = g1 and g2 and g3 and g4 and g5
    label = label_for(shares, majority_admission, majority_slot, slot_binding_cycles, gates_ok)

    paired_lower = sum(
        1 for e, c in zip(sorted(engine, key=lambda r: r["seed"]),
                          sorted(control, key=lambda r: r["seed"]))
        if (c["below_admission"] / c["misses"] if c["misses"] else 0.0)
        < (e["below_admission"] / e["misses"] if e["misses"] else 0.0)
    )
    predictions = {
        "P1_engine_reaches_zero": all(r["first_zero_cycle"] is not None for r in engine),
        "P2_every_miss_classified": g5,
        "P3_admission_majority_in_six": majority_admission >= MAJORITY_SEEDS,
        "P4_slot_binds_in_six_seeds": sum(1 for r in engine if r["binding_cycles"] > 0) >= MAJORITY_SEEDS,
        "P5_slice_reconstructs": g3,
        "P6_control_admission_lower": paired_lower >= MAJORITY_SEEDS,
    }
    gates = {
        "G1_perturbation_recorded": g1,
        "G2_ceiling_reproduced": g2,
        "G3_slice_faithful": g3,
        "G4_denominator_exists": g4,
        "G5_attribution_complete": g5,
        "G6_slot_can_fire": slot_binding_cycles > 0,
    }
    paired = []
    for e, c in zip(sorted(engine, key=lambda r: r["seed"]), sorted(control, key=lambda r: r["seed"])):
        paired.append({
            "seed": e["seed"],
            "engine_below_share": round(e["below_admission"] / e["misses"], 4) if e["misses"] else None,
            "control_below_share": round(c["below_admission"] / c["misses"], 4) if c["misses"] else None,
            "engine_misses": e["misses"],
            "control_misses": c["misses"],
        })

    return {
        "protocol_digest": protocol_digest(PREREG.read_text(encoding="utf-8")),
        ARTIFACT_DIGEST_KEY: protocol_digest(PREREG.read_text(encoding="utf-8")),
        "date": "2026-11-07",
        "question": "Q044",
        "protocol": "docs/DECAY-ADMISSION-SLOT-PREREGISTRATION.md",
        "seeds": list(SEEDS),
        "arms": list(ARMS),
        "cycles": CYCLES,
        "degree": DEGREE,
        "budget": BUDGET,
        "admission": ADMISSION,
        "label": label,
        "gates_ok": gates_ok,
        "gates": gates,
        "pooled": {
            "misses": sum(pooled[name] for name in CLASSES) + pooled["unexplained"],
            "below_admission": pooled["below_admission"],
            "slot_loss": pooled["slot_loss"],
            "unexplained": pooled["unexplained"],
            "shares": shares,
            "majority_admission_seeds": majority_admission,
            "majority_slot_seeds": majority_slot,
            "engine_seeds": len(engine),
            "slot_binding_cycles": slot_binding_cycles,
        },
        "predictions": predictions,
        "paired": paired,
        "cells": [
            {k: v for k, v in row.items() if k != "series"} for row in rows
        ],
        "series": {("%s/s%d" % (r["arm"], r["seed"])): r["series"] for r in rows},
    }


def render(artifact: dict) -> str:
    lines = [
        "# Admission count or ranked slot?",
        "",
        "Generated from `docs/decay_admission_slot.json` by",
        "`python -m benchmarks.decay_admission_slot --render`. Do not edit by hand.",
        "",
        "Pre-registration: `docs/DECAY-ADMISSION-SLOT-PREREGISTRATION.md` (SHA-256 of sections 1-9",
        "recorded in the artifact). The engine is 0.13.0 and unchanged.",
        "",
        "## Label",
        "",
        "**%s**" % artifact["label"],
        "",
        "Pooled engine-arm misses: %d, of which **%d** were below the admission floor of %d"
        % (artifact["pooled"]["misses"], artifact["pooled"]["below_admission"], artifact["admission"]),
        "and **%d** lost a ranked slot out of %d. Shares: admission %s, slot %s."
        % (artifact["pooled"]["slot_loss"], artifact["budget"],
           artifact["pooled"]["shares"]["below_admission"],
           artifact["pooled"]["shares"]["slot_loss"]),
        "",
        "## Per seed, engine arm",
        "",
        "| Seed | Peak | Final | First zero | Misses | Below admission | Slot loss | Bind cycles |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in sorted(artifact["cells"], key=lambda r: (r["arm"], r["seed"])):
        if row["arm"] != "engine":
            continue
        lines.append(
            "| %d | %d | %s | %s | %d | %d | %d | %d |"
            % (row["seed"], row["peak"], row["final"], row["first_zero_cycle"],
               row["misses"], row["below_admission"], row["slot_loss"], row["binding_cycles"])
        )
    lines += [
        "",
        "## Gates and predictions",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    for name, ok in artifact["gates"].items():
        lines.append("| %s | %s |" % (name, "pass" if ok else "FAIL"))
    for name, ok in artifact["predictions"].items():
        lines.append("| %s | %s |" % (name, "held" if ok else "failed"))
    lines += [
        "",
        "## Control arm",
        "",
        "| Seed | Engine misses | Engine admission share | Control misses | Control admission share |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in artifact["paired"]:
        lines.append(
            "| %d | %d | %s | %d | %s |"
            % (row["seed"], row["engine_misses"], row["engine_below_share"],
               row["control_misses"], row["control_below_share"])
        )
    lines += [
        "",
        "## What this establishes",
        "",
        "Which gate an edge missed in this world, at this degree, admission floor and budget. It does",
        "not establish that raising either gate would repair persistence, and it does not test other",
        "worlds or other budgets. A `VOID_INSTRUMENT` label is not a verdict.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS))
    args = parser.parse_args(argv)
    if args.run:
        return run(tuple(args.seeds))
    if args.render:
        artifact = analyse(load_parts())
        ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=2) + "\n", encoding="utf-8")
        PAGE.write_text(render(artifact), encoding="utf-8")
        print("label: %s" % artifact["label"])
        print("pooled: %s" % artifact["pooled"])
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
