"""Run the decay operating-point study: six conditions on the cycle-39 world.

Pre-registered in ``docs/OPERATING-POINT-PREREGISTRATION.md``. The engine is unchanged: each
condition is an in-process memory subclass that forces one decay path, and the death ledger's own
observer records the theory layer.

    ./.venv/bin/python -m benchmarks.operating_point --measure --condition shipped
    ./.venv/bin/python -m benchmarks.operating_point --finish
    ./.venv/bin/python -m benchmarks.operating_point --render
    ./.venv/bin/python -m benchmarks.operating_point --check
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import date
from pathlib import Path

from benchmarks.decay_confirmation import harvest_seeds
from benchmarks.operating_point_prereg import (
    ARTIFACT,
    CONDITIONS,
    CONTROL_SEED,
    DOC as PREREG,
    FROZEN_DIGEST,
    SEEDS,
    protocol_digest,
)
from benchmarks.reference_death_ledger import (
    CYCLES,
    cell_facts,
    control_facts,
    ledger_class,
    stimulus,
)
from organica.memory import MemoryService
from organica.paths import temp_db
from organica.streams import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "operating_point" / "parts"
DOC = ROOT / "docs" / "OPERATING-POINT.md"
MARGIN = 10

CONFIG = {
    "shipped": {"factor": 0.95, "floor": 1, "recency": False},
    "floor2": {"factor": 0.95, "floor": 2, "recency": False},
    "floor5": {"factor": 0.95, "floor": 5, "recency": False},
    "factor099": {"factor": 0.99, "floor": 1, "recency": False},
    "recency": {"factor": 0.95, "floor": 1, "recency": True},
    "no_decay": {"factor": 1.0, "floor": 1, "recency": False},
}


class OperatingMemory(MemoryService):
    """One decay path per condition, with every applied perturbation recorded."""

    def __init__(self, *args, condition: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.condition = condition
        self.cfg = CONFIG[condition]
        self.decay_calls: list[dict] = []
        self.exempt_edges: set[tuple[str, str]] = set()
        self.lifted_total = 0
        self.exempted_total = 0

    def decay_temporal_edges(self, factor: float = 0.95, min_count: int = 1) -> int:
        cfg = self.cfg
        counts = {(src, tgt): int(count) for src, tgt, count in self.temporal_edges(min_count=1)}
        floor = int(cfg["floor"])
        lifted = sum(1 for count in counts.values() if count < floor) if floor > 1 else 0
        exempt: dict[tuple[str, str], int] = {}
        if cfg["recency"] and self.exempt_edges:
            exempt = {edge: counts[edge] for edge in self.exempt_edges if edge in counts}
        before = sum(counts.values())
        rows = super().decay_temporal_edges(factor=float(cfg["factor"]), min_count=floor)
        if exempt:
            self._conn.executemany(
                "UPDATE precedes SET count = ? WHERE tag_from = ? AND tag_to = ?",
                [(count, src, tgt) for (src, tgt), count in exempt.items()],
            )
            self._conn.commit()
        after = self._conn.execute("SELECT COALESCE(SUM(count), 0) FROM precedes").fetchone()[0]
        self.lifted_total += lifted
        self.exempted_total += len(exempt)
        self.decay_calls.append({
            "factor": float(cfg["factor"]),
            "floor": floor,
            "rows": int(rows),
            "lifted": int(lifted),
            "exempted": len(exempt),
            "mass_before": int(before),
            "mass_after": int(after),
        })
        return rows


def stable_count(service) -> int:
    """Stored prediction candidates at or above the stable threshold, as the attribution reads them."""
    service._prior_cache = None
    edges: dict[tuple[str, str], float] = {}
    for cand in service._load_prior_candidates():
        if cand.get("type") != "prediction_candidate":
            continue
        src, tgt = cand.get("source"), cand.get("target")
        if not src or not tgt:
            continue
        strength = float(cand.get("confidence") or cand.get("strength") or 0.0)
        if strength >= service.STABLE_THRESHOLD:
            edges[(src, tgt)] = max(edges.get((src, tgt), 0.0), strength)
    service._prior_cache = None
    return len(edges)


def zero_cycle(series: list[int]) -> int:
    """First cycle after the peak with no stable edge, or 301 if the set never empties."""
    if not series:
        return 1
    peak = max(series)
    start = series.index(peak)
    for index in range(start + 1, len(series)):
        if series[index] == 0:
            return index + 1
    return CYCLES + 1


def run_cell(condition: str, seed: int, events: list[str]) -> tuple[list[dict], dict]:
    """One condition on one seed, with the ledger's bootstrap and feed."""
    db = temp_db("oppoint_%s_%s.db" % (condition, seed))
    db.unlink(missing_ok=True)
    memory = OperatingMemory(db_path=str(db), condition=condition)
    service = ledger_class("FULL")(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    service.ledger_reset()
    stable: list[int] = []
    try:
        for text in events:
            memory.store(text, event_type="event", source="seed:bootstrap")
        for cycle in range(CYCLES):
            before = None
            if CONFIG[condition]["recency"]:
                before = {(src, tgt): int(count)
                          for src, tgt, count in memory.temporal_edges(min_count=1)}
            start = (cycle * EVENTS_PER_CYCLE) % len(events)
            for text in events[start:start + EVENTS_PER_CYCLE]:
                memory.store(text, event_type="event", source="cycle:%d" % cycle)
            if before is not None:
                after = {(src, tgt): int(count)
                         for src, tgt, count in memory.temporal_edges(min_count=1)}
                memory.exempt_edges = {
                    edge for edge, count in after.items()
                    if count > before.get(edge, 0)
                }
            else:
                memory.exempt_edges = set()
            service.run_sleep_cycle()
            stable.append(stable_count(service))
        calls = list(memory.decay_calls)
        extra = {
            "stable_series": stable,
            "stable_peak": max(stable) if stable else 0,
            "stable_zero": zero_cycle(stable),
            "decay_calls": calls,
            "decay_rows_min": min((call["rows"] for call in calls), default=0),
            "lifted_total": memory.lifted_total,
            "exempted_total": memory.exempted_total,
            "exempted_cycles": sum(1 for call in calls if call["exempted"] > 0),
            "decay_factors": sorted({call["factor"] for call in calls}),
            "decay_floors": sorted({call["floor"] for call in calls}),
            "mass_unchanged": all(call["mass_before"] == call["mass_after"] for call in calls),
        }
        return list(service.ledger_rows), extra
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def part_path(condition: str, seed: int) -> Path:
    return PARTS / ("%s_%d.json" % (condition, seed))


def seeds_are_fresh() -> bool:
    if ARTIFACT.exists():
        try:
            recorded = json.loads(ARTIFACT.read_text(encoding="utf-8")).get("seeds") or []
        except (OSError, ValueError):
            recorded = []
        if tuple(recorded) == SEEDS:
            return True
    return not (set(SEEDS) & harvest_seeds(ROOT / "docs"))


def measure(condition: str) -> int:
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to run")
    if "executions: 0" not in text:
        raise SystemExit("the protocol already records an execution; refusing to run again")
    if not seeds_are_fresh():
        raise SystemExit("the pre-registered seed block is already used under docs/")
    if condition not in CONDITIONS:
        raise SystemExit("condition must be one of %r" % (CONDITIONS,))

    events = stimulus()
    PARTS.mkdir(parents=True, exist_ok=True)
    for seed in SEEDS:
        path = part_path(condition, seed)
        if path.exists():
            part = json.loads(path.read_text(encoding="utf-8"))
            if len(part.get("ledger") or []) == CYCLES:
                print("cached", path.name, flush=True)
                continue
        rows, extra = run_cell(condition, seed, events)
        facts = cell_facts(rows)
        facts.update({"condition": condition, "seed": seed, **extra})
        part = {"condition": condition, "seed": seed, "facts": facts,
                "ledger": rows, "stable_series": extra.pop("stable_series")}
        path.write_text(json.dumps(part, indent=1) + "\n", encoding="utf-8")
        print("%s %d death=%s stable_zero=%s lifted=%s exempted=%s"
              % (condition, seed, facts["death_cycle"], facts["stable_zero"],
                 facts["lifted_total"], facts["exempted_total"]), flush=True)
    return 0


def load_parts() -> list[dict]:
    cells: list[dict] = []
    for condition in CONDITIONS:
        for seed in SEEDS:
            path = part_path(condition, seed)
            if not path.exists():
                raise SystemExit("missing part %s; run the condition first" % path.name)
            part = json.loads(path.read_text(encoding="utf-8"))
            if part.get("condition") != condition or part.get("seed") != seed:
                raise SystemExit("part %s does not hold the cell it is named for" % path.name)
            if len(part.get("ledger") or []) != CYCLES:
                raise SystemExit("part %s is short" % path.name)
            cells.append({"condition": condition, "seed": seed, **part["facts"]})
    return cells


def summary(cells: list[dict], condition: str) -> dict:
    rows = [cell for cell in cells if cell["condition"] == condition]
    deaths = {cell["seed"]: cell["death_cycle"] for cell in rows}
    theory: dict[str, int] = {}
    for cell in rows:
        for reason, count in cell["theory_removals"].items():
            theory[reason] = theory.get(reason, 0) + int(count)
    return {
        "cells": len(rows),
        "death_cycles": [deaths[seed] for seed in SEEDS],
        "median_death_cycle": statistics.median(deaths.values()),
        "per_seed": {str(seed): deaths[seed] for seed in SEEDS},
        "stable_zero": {str(cell["seed"]): cell["stable_zero"] for cell in rows},
        "stable_peak": max(cell["stable_peak"] for cell in rows),
        "theory_cycles": sum(cell["theory_cycles"] for cell in rows),
        "peak_theories": max(cell["theories_total"] for cell in rows),
        "parent_loss": int(theory.get("parent_loss", 0)),
        "theory_removals": theory,
        "alive_at_end": sum(1 for cell in rows if cell["death_cycle"] == CYCLES + 1),
    }


def decide(gates: dict, live: dict, viable: dict, predictions: dict) -> str:
    if not (gates["G1_neutral_observer"] and gates["G7_denominators"]
            and gates["G8_seed_independence"]):
        return "VOID_INSTRUMENT"
    if not gates["G2_baseline_39"]:
        return "BASELINE_NOT_REPRODUCED"
    repair = ("floor5", "factor099", "recency", "no_decay")
    if not any(live[condition] for condition in repair):
        return "NO_REPAIR_ARM_LIVE"
    moved = [condition for condition in repair if live[condition] and viable[condition]]
    interior = [condition for condition in moved if condition != "no_decay"]
    if not moved:
        return "NO_OPERATING_POINT"
    if not interior:
        return "NO_DECAY_ONLY"
    if set(interior) == {"factor099"}:
        return "FACTOR_ONLY"
    if set(interior) == {"floor5"}:
        return "FLOOR_ONLY"
    if set(interior) == {"recency"}:
        return "RECENCY_ONLY"
    if set(interior) == {"factor099", "floor5", "recency"} and predictions["P8_ordering"]:
        return "MONOTONE_LADDER"
    return "PARTIAL_LADDER"


def finish() -> dict:
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to finish")
    if "executions: 0" not in text:
        raise SystemExit("the protocol already records an execution")
    if not seeds_are_fresh():
        raise SystemExit("the pre-registered seed block is already used under docs/")
    cells = load_parts()
    control = control_facts(run_cell("shipped", CONTROL_SEED, stimulus())[0])

    summaries = {condition: summary(cells, condition) for condition in CONDITIONS}
    shipped = summaries["shipped"]["per_seed"]
    viability = {
        condition: sum(
            1 for seed in SEEDS
            if summaries[condition]["per_seed"][str(seed)] - shipped[str(seed)] >= MARGIN
        ) >= 2
        for condition in CONDITIONS
    }
    floor_live = all(
        cell["decay_floors"] == [CONFIG[cell["condition"]]["floor"]]
        and cell["lifted_total"] > 0
        for cell in cells if cell["condition"] in ("floor2", "floor5")
    )
    gates = {
        "G1_neutral_observer": bool(control["theory_match"] and control["belief_match"]),
        "G2_baseline_39": all(cell["death_cycle"] == 39
                              for cell in cells if cell["condition"] == "shipped"),
        "G3_floor_live": floor_live,
        "G4_factor_live": all(
            cell["decay_factors"] == [0.99] and cell["decay_rows_min"] > 0
            for cell in cells if cell["condition"] == "factor099"
        ),
        "G5_recency_live": all(
            cell["exempted_total"] > 0 and cell["exempted_cycles"] > 0
            for cell in cells if cell["condition"] == "recency"
        ),
        "G6_no_decay_live": all(
            cell["decay_factors"] == [1.0] and cell["mass_unchanged"]
            for cell in cells if cell["condition"] == "no_decay"
        ),
        "G7_denominators": all(
            cell["cycles"] == CYCLES and cell["theory_cycles"] > 0 for cell in cells
        ),
        "G8_seed_independence": True,
    }
    live = {
        "shipped": True,
        "floor2": gates["G3_floor_live"],
        "floor5": gates["G3_floor_live"],
        "factor099": gates["G4_factor_live"],
        "recency": gates["G5_recency_live"],
        "no_decay": gates["G6_no_decay_live"],
    }
    medians = {condition: summaries[condition]["median_death_cycle"] for condition in CONDITIONS}
    predictions = {
        "P1_baseline_39": all(cell["death_cycle"] == 39
                              for cell in cells if cell["condition"] == "shipped"),
        "P2_no_decay_highest": medians["no_decay"] >= max(
            medians[condition] for condition in CONDITIONS if condition != "no_decay"
        ),
        "P3_factor099_viable": viability["factor099"] and medians["factor099"] < medians["no_decay"],
        "P4_recency_viable": viability["recency"] and medians["recency"] < medians["factor099"],
        "P5_floor5_between": medians["floor5"] > medians["shipped"]
                             and medians["floor5"] < medians["recency"],
        "P6_floor2_control": all(
            abs(summaries["floor2"]["per_seed"][str(seed)] - shipped[str(seed)]) <= 2
            for seed in SEEDS
        ),
        "P7_perturbations_fire": all(
            cell["lifted_total"] > 0 for cell in cells
            if cell["condition"] in ("floor2", "floor5")
        ) and all(cell["exempted_total"] > 0 for cell in cells
                  if cell["condition"] == "recency"),
        "P8_ordering": (
            medians["no_decay"] >= medians["factor099"] > medians["recency"]
            > medians["floor5"] > medians["floor2"]
            and abs(medians["floor2"] - medians["shipped"]) <= 2
        ),
        "P9_stable_zero_later": all(
            sum(1 for seed in SEEDS
                if summaries[condition]["stable_zero"][str(seed)]
                > summaries["shipped"]["stable_zero"][str(seed)]) >= 2
            for condition in ("factor099", "no_decay")
        ),
    }
    label = decide(gates, live, viability, predictions)
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": __import__("organica").__version__,
        "question": "Q047",
        "protocol_digest": FROZEN_DIGEST,
        "preregistration": "docs/OPERATING-POINT-PREREGISTRATION.md",
        "world": "lattice_L1",
        "arm": "FULL",
        "seeds": list(SEEDS),
        "control_seed": CONTROL_SEED,
        "cycles": CYCLES,
        "conditions": list(CONDITIONS),
        "margin": MARGIN,
        "cells": cells,
        "summary": summaries,
        "viability": viability,
        "live": live,
        "label": label,
        "gates": gates,
        "predictions": predictions,
        "control": control,
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=1) + "\n", encoding="utf-8")
    return artifact


def render(artifact: dict) -> str:
    lines = [
        "# The decay operating point — result",
        "",
        "Generated from `docs/operating_point.json` by",
        "`python -m benchmarks.operating_point --render`. Do not edit by hand.",
        "",
        "Pre-registration: `docs/OPERATING-POINT-PREREGISTRATION.md`. Six conditions on the",
        "falsifier's `lattice_L1` world, reference arm FULL, seeds 20302401-20302403.",
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "| Condition | Death cycles | Median | Viable | Stable zero |",
        "| --- | --- | --- | --- | --- |",
    ]
    for condition in artifact["conditions"]:
        summary = artifact["summary"][condition]
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (condition, summary["death_cycles"], summary["median_death_cycle"],
               "yes" if artifact["viability"][condition] else "no",
               summary["stable_zero"])
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
        "The primary endpoint is theory death, with 301 meaning alive at cycle 300. A condition is",
        "viable when it gains at least %d cycles on at least 2 of 3 paired seeds." % artifact["margin"],
        "",
        "**`floor5` is an eligibility intervention, not a retention intervention.** It lifts every",
        "edge with count 1-4 to 5, so the `>= 5` admission gate stops filtering; admitted edges",
        "above 5 decay exactly as shipped. `floor2` lifts only count 1 to 2 and is the negative",
        "control, not a repair.",
        "",
        "**`no_decay` is an upper bound measured here for the first time on `lattice_L1`.** The",
        "degree-12 hub's no-decay survival is not evidence for this world.",
        "",
        "A viable arm is a persistence candidate, not an adoption recommendation. Adoption needs a",
        "capability study and an owner decision; this protocol scores no prediction, revision or",
        "adaptation task.",
        "",
        "The control (shipped FULL at seed %d) matched the committed falsifier theories: **%s**;"
        % (artifact["control_seed"], artifact["control"]["theory_match"]),
        "beliefs: **%s**." % artifact["control"]["belief_match"],
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
        print("%s: %s" % (artifact["label"], artifact["viability"]))
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
    from benchmarks.operating_point_prereg import validate
    registry = json.loads((ROOT / "docs" / "research_question_registry.json").read_text(encoding="utf-8"))
    problems = validate(text, registry, artifact,
                        seeds_used=harvest_seeds(ROOT / "docs") - set(SEEDS))
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    if artifact and artifact["label"] not in DOC.read_text(encoding="utf-8"):
        raise SystemExit("FAIL: the page does not name the label")
    print("operating point: protocol frozen, %s"
          % ("executed" if artifact else "no execution recorded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
