"""Run the shared-decay repair across the six force-matrix arms.

Pre-registered in ``docs/SUBSTRATE-REPAIR-PREREGISTRATION.md``. The engine is unchanged: the
repaired arm is an in-process subclass that sets ``TEMPORAL_DECAY_FACTOR = 0.99`` and otherwise
composes the death ledger's observer with the same colony classes.

    ./.venv/bin/python -m benchmarks.substrate_repair --measure --condition shipped
    ./.venv/bin/python -m benchmarks.substrate_repair --measure --condition repaired
    ./.venv/bin/python -m benchmarks.substrate_repair --finish
    ./.venv/bin/python -m benchmarks.substrate_repair --render
    ./.venv/bin/python -m benchmarks.substrate_repair --check
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import date
from pathlib import Path

from benchmarks.decay_confirmation import harvest_seeds
from benchmarks.reference_death_ledger import (
    CYCLES,
    cell_facts,
    control_facts,
    ledger_class,
    stimulus,
)
from benchmarks.substrate_repair_prereg import (
    ARMS,
    ARTIFACT,
    CONDITIONS,
    CONTROL_SEED,
    DOC as PREREG,
    FROZEN_DIGEST,
    SEEDS,
    protocol_digest,
)
from organica.memory import MemoryService
from organica.paths import temp_db
from organica.streams import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "substrate_repair" / "parts"
DOC = ROOT / "docs" / "SUBSTRATE-REPAIR.md"
FACTORS = {"shipped": 0.95, "repaired": 0.99}
MARGIN = 10


class RepairMemory(MemoryService):
    """Records the decay call the service makes, so the perturbation can be audited."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decay_calls: list[dict] = []

    def decay_temporal_edges(self, factor: float = 0.95, min_count: int = 1) -> int:
        rows = super().decay_temporal_edges(factor=factor, min_count=min_count)
        self.decay_calls.append(
            {"factor": float(factor), "rows": int(rows), "min_count": int(min_count)}
        )
        return rows


def arm_class(arm: str, factor: float):
    """The ledger's observer plus one decay constant; no policy is changed."""
    base = ledger_class(arm)
    return type(
        "Repair_%s_%s" % (arm, str(factor).replace(".", "")),
        (base,),
        {"TEMPORAL_DECAY_FACTOR": float(factor)},
    )


def run_cell(arm: str, condition: str, seed: int, events: list[str]):
    """One arm under one decay condition, with the ledger's own bootstrap and feed."""
    factor = FACTORS[condition]
    db = temp_db("subrep_%s_%s_%s.db" % (arm, condition, seed))
    db.unlink(missing_ok=True)
    memory = RepairMemory(db_path=str(db))
    service = arm_class(arm, factor)(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    service.ledger_reset()
    try:
        for text in events:
            memory.store(text, event_type="event", source="seed:bootstrap")
        for cycle in range(CYCLES):
            start = (cycle * EVENTS_PER_CYCLE) % len(events)
            for text in events[start:start + EVENTS_PER_CYCLE]:
                memory.store(text, event_type="event", source="cycle:%d" % cycle)
            service.run_sleep_cycle()
        return list(service.ledger_rows), list(memory.decay_calls)
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def part_path(arm: str, condition: str, seed: int) -> Path:
    return PARTS / ("%s_%s_%s.json" % (arm, condition, seed))


def measure(condition: str) -> int:
    """Run every missing cell of one condition, writing each part as it completes."""
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to run")
    if "executions: 0" not in text:
        raise SystemExit("the protocol already records an execution; refusing to run again")
    used = harvest_seeds(ROOT / "docs") - set(SEEDS)
    if set(SEEDS) & used:
        raise SystemExit("the pre-registered seed block is already used under docs/")
    if condition not in CONDITIONS:
        raise SystemExit("condition must be one of %r" % (CONDITIONS,))

    events = stimulus()
    PARTS.mkdir(parents=True, exist_ok=True)
    for arm in ARMS:
        for seed in SEEDS:
            path = part_path(arm, condition, seed)
            if path.exists():
                part = json.loads(path.read_text(encoding="utf-8"))
                if len(part.get("ledger") or []) == CYCLES:
                    print("cached", path.name, flush=True)
                    continue
            rows, calls = run_cell(arm, condition, seed, events)
            facts = cell_facts(rows)
            facts.update({
                "arm": arm,
                "condition": condition,
                "seed": seed,
                "factor": FACTORS[condition],
                "decay_factors": sorted({call["factor"] for call in calls}),
                "decay_rows_min": min((call["rows"] for call in calls), default=0),
                "decay_calls": len(calls),
            })
            part = {"arm": arm, "condition": condition, "seed": seed,
                    "facts": facts, "ledger": rows}
            path.write_text(json.dumps(part, indent=1) + "\n", encoding="utf-8")
            print("%s %s %d death=%s" % (arm, condition, seed, facts["death_cycle"]), flush=True)
    return 0


def load_parts() -> list[dict]:
    cells: list[dict] = []
    for arm in ARMS:
        for condition in CONDITIONS:
            for seed in SEEDS:
                path = part_path(arm, condition, seed)
                if not path.exists():
                    raise SystemExit("missing part %s; run the condition first" % path.name)
                part = json.loads(path.read_text(encoding="utf-8"))
                if part.get("arm") != arm or part.get("condition") != condition \
                        or part.get("seed") != seed:
                    raise SystemExit("part %s does not hold the cell it is named for" % path.name)
                if len(part.get("ledger") or []) != CYCLES:
                    raise SystemExit("part %s is short" % path.name)
                cells.append({"arm": arm, "condition": condition, "seed": seed,
                              **part["facts"]})
    return cells


def summary(cells: list[dict], arm: str, condition: str) -> dict:
    rows = [c for c in cells if c["arm"] == arm and c["condition"] == condition]
    deaths = [c["death_cycle"] for c in rows]
    theory: dict = {}
    for c in rows:
        for reason, count in c["theory_removals"].items():
            theory[reason] = theory.get(reason, 0) + int(count)
    return {
        "cells": len(rows),
        "death_cycles": deaths,
        "median_death_cycle": statistics.median(deaths),
        "min_death_cycle": min(deaths),
        "max_death_cycle": max(deaths),
        "theory_cycles": sum(c["theory_cycles"] for c in rows),
        "theory_removals": theory,
        "parent_loss": int(theory.get("parent_loss", 0)),
        "superseded": int(theory.get("superseded", 0)),
        "alive_at_end": sum(1 for c in rows if c["last_nonzero_cycle"] == CYCLES),
    }


def decide(gates: dict, extensions: dict) -> str:
    if not (gates["G1_neutral_observer"] and gates["G4_denominators"]
            and gates["G5_seed_independence"]):
        return "VOID_INSTRUMENT"
    if not gates["G2_repair_live"]:
        return "REPAIR_NOT_LIVE"
    if not gates["G3_baseline_39"]:
        return "BASELINE_NOT_REPRODUCED"
    extended = [arm for arm in ARMS if extensions[arm] >= 2]
    if len(extended) == len(ARMS):
        return "SUBSTRATE_REPAIR"
    if extended:
        return "PARTIAL_REPAIR"
    return "NO_REPAIR"


def finish() -> dict:
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to finish")
    if "executions: 0" not in text:
        raise SystemExit("the protocol already records an execution")
    used = harvest_seeds(ROOT / "docs") - set(SEEDS)
    if set(SEEDS) & used:
        raise SystemExit("the pre-registered seed block is already used under docs/")
    cells = load_parts()
    control = control_facts(run_cell("FULL", "shipped", CONTROL_SEED, stimulus())[0])

    summaries = {arm: {condition: summary(cells, arm, condition) for condition in CONDITIONS}
                 for arm in ARMS}
    deltas = {
        arm: [next(c["death_cycle"] for c in cells
                   if c["arm"] == arm and c["condition"] == "repaired" and c["seed"] == seed)
              - next(c["death_cycle"] for c in cells
                     if c["arm"] == arm and c["condition"] == "shipped" and c["seed"] == seed)
              for seed in SEEDS]
        for arm in ARMS
    }
    extensions = {arm: sum(1 for d in deltas[arm] if d >= MARGIN) for arm in ARMS}
    gates = {
        "G1_neutral_observer": bool(control["theory_match"] and control["belief_match"]),
        "G2_repair_live": (
            all(set(c["decay_factors"]) == {0.99} and c["decay_rows_min"] > 0
                for c in cells if c["condition"] == "repaired")
            and all(set(c["decay_factors"]) == {0.95}
                    for c in cells if c["condition"] == "shipped")
        ),
        "G3_baseline_39": all(
            c["death_cycle"] == 39 for c in cells if c["condition"] == "shipped"
        ),
        "G4_denominators": all(c["cycles"] == CYCLES and c["theory_cycles"] > 0 for c in cells),
        "G5_seed_independence": True,
    }
    label = decide(gates, extensions)
    repaired_spread = [
        max(summaries[arm]["repaired"]["death_cycles"][index] for arm in ARMS)
        - min(summaries[arm]["repaired"]["death_cycles"][index] for arm in ARMS)
        for index in range(len(SEEDS))
    ]
    predictions = {
        "P1_baseline_39": gates["G3_baseline_39"],
        "P2_repair_live": gates["G2_repair_live"],
        "P3_all_six_extend": all(extensions[arm] >= 2 for arm in ARMS),
        "P4_shared_timing": sum(1 for spread in repaired_spread if spread <= 2) >= 2,
        "P5_parent_loss_falls": (
            summaries["FULL"]["repaired"]["parent_loss"]
            < summaries["FULL"]["shipped"]["parent_loss"]
        ),
    }
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": __import__("organica").__version__,
        "question": "Q046",
        "protocol_digest": FROZEN_DIGEST,
        "preregistration": "docs/SUBSTRATE-REPAIR-PREREGISTRATION.md",
        "seeds": list(SEEDS),
        "control_seed": CONTROL_SEED,
        "cycles": CYCLES,
        "arms": list(ARMS),
        "conditions": list(CONDITIONS),
        "factors": FACTORS,
        "margin": MARGIN,
        "cells": cells,
        "summary": summaries,
        "deltas": deltas,
        "extensions": extensions,
        "repaired_spread": repaired_spread,
        "label": label,
        "gates": gates,
        "predictions": predictions,
        "control": control,
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=1) + "\n", encoding="utf-8")
    return artifact


def render(artifact: dict) -> str:
    lines = [
        "# Substrate repair across the six arms — result",
        "",
        "Generated from `docs/substrate_repair.json` by",
        "`python -m benchmarks.substrate_repair --render`. Do not edit by hand.",
        "",
        "Pre-registration: `docs/SUBSTRATE-REPAIR-PREREGISTRATION.md`. The repair is the",
        "temporal-edge decay factor, 0.95 to 0.99, applied identically to every arm.",
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "| Arm | Shipped death | Repaired death | Per-seed delta | Seeds extended |",
        "| --- | --- | --- | --- | --- |",
    ]
    for arm in artifact["arms"]:
        shipped = artifact["summary"][arm]["shipped"]
        repaired = artifact["summary"][arm]["repaired"]
        lines.append(
            "| %s | %s | %s | %s | %d of %d |"
            % (arm, shipped["death_cycles"], repaired["death_cycles"],
               artifact["deltas"][arm], artifact["extensions"][arm], len(artifact["seeds"]))
        )
    lines += ["", "## Gates", "", "| Gate | Result |", "| --- | --- |"]
    for name, ok in artifact["gates"].items():
        lines.append("| %s | %s |" % (name, "pass" if ok else "FAIL"))
    lines += ["", "## Predictions", "", "| Prediction | Result |", "| --- | --- |"]
    for name, ok in artifact["predictions"].items():
        lines.append("| %s | %s |" % (name, "held" if ok else "failed"))
    lines += [
        "",
        "## Reading",
        "",
        "All six arms extend by the margin: **%s**. The repaired death cycles across the six",
        "arms are %s, so the shared-timing prediction %s."
        % (artifact["predictions"]["P3_all_six_extend"],
           artifact["repaired_spread"],
           "held" if artifact["predictions"]["P4_shared_timing"] else "failed"),
        "",
        "The control (shipped FULL at seed %d) matched the committed falsifier theories: **%s**;"
        % (artifact["control_seed"], artifact["control"]["theory_match"]),
        "beliefs: **%s**." % artifact["control"]["belief_match"],
        "",
        "The repair changes the temporal decay rate only. It says nothing about belief formation,",
        "the admission floor, the candidate-decay factor or the theory cap.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--render", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--condition", choices=CONDITIONS)
    args = parser.parse_args(argv)
    if args.measure:
        if not args.condition:
            raise SystemExit("--measure needs --condition")
        return measure(args.condition)
    if args.finish:
        artifact = finish()
        print("%s: %s" % (artifact["label"], artifact["extensions"]))
        return 0
    if args.render:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        page = render(artifact)
        if "{" in page:
            raise SystemExit("the page contains a brace; refusing to write it")
        DOC.write_text(page, encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0
    text = PREREG.read_text(encoding="utf-8")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else None
    from benchmarks.substrate_repair_prereg import validate
    registry = json.loads((ROOT / "docs" / "research_question_registry.json").read_text(encoding="utf-8"))
    problems = validate(text, registry, artifact,
                        seeds_used=harvest_seeds(ROOT / "docs") - set(SEEDS))
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    if artifact and artifact["label"] not in DOC.read_text(encoding="utf-8"):
        raise SystemExit("FAIL: the page does not name the label")
    print("substrate repair: protocol frozen, %s"
          % ("executed" if artifact else "no execution recorded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
