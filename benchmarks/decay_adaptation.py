"""Run the decay-adaptation pilot on the Phase J gradual-shift families.

Pre-registered in ``docs/DECAY-ADAPTATION-PREREGISTRATION.md``. The engine is unchanged: each arm
is an in-process memory subclass that forces one decay factor. The endpoint is the mean next-event
NLL over cycles 60-79 on the shifted world, computed from the organism's own predictions before
each cycle is stored, exactly as Phase J computes it.

    ./.venv/bin/python -m benchmarks.decay_adaptation --measure --arm shipped
    ./.venv/bin/python -m benchmarks.decay_adaptation --finish
    ./.venv/bin/python -m benchmarks.decay_adaptation --render
    ./.venv/bin/python -m benchmarks.decay_adaptation --check
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from datetime import date
from pathlib import Path

from benchmarks.decay_adaptation_prereg import (
    ARMS,
    ARTIFACT,
    CYCLES,
    FAMILIES,
    FROZEN_DIGEST,
    SEEDS,
    protocol_digest,
)
from benchmarks.decay_adaptation_prereg import DOC as PREREG
from benchmarks.decay_confirmation import harvest_seeds
from benchmarks.post_shift_adaptation import (
    FINAL_START,
    _cycle_loss,
    _organica_distributions,
    generate_world,
)
from organica.memory import MemoryService
from organica.paths import temp_db
from organica.sleep import SleepService
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "decay_adaptation" / "parts"
DOC = ROOT / "docs" / "DECAY-ADAPTATION.md"

FACTORS = {
    "shipped": 0.95,
    "factor099": 0.99,
    "factor09925": 0.9925,
    "no_decay": 1.0,
}
MARGIN = 0.05
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20261023


class AdaptMemory(MemoryService):
    """Force one decay factor and record every applied perturbation."""

    def __init__(self, *args, factor: float, **kwargs):
        self.factor = float(factor)
        self.calls: list[dict] = []
        super().__init__(*args, **kwargs)

    def decay_temporal_edges(self, factor: float = 0.95, min_count: int = 1) -> int:
        counts = {(src, tgt): int(count)
                  for src, tgt, count in self.temporal_edges(min_count=1)}
        before = sum(counts.values())
        rows = super().decay_temporal_edges(factor=self.factor, min_count=1)
        after = self._conn.execute(
            "SELECT COALESCE(SUM(count), 0) FROM precedes"
        ).fetchone()[0]
        self.calls.append({"factor": self.factor, "rows": int(rows),
                           "mass_before": int(before), "mass_after": int(after)})
        return rows


def run_cell(arm: str, family: str, seed: int) -> dict:
    world = generate_world(family, seed, shifted=True)
    db = temp_db("decay_adapt_%s_%s_%s.db" % (arm, family, seed))
    db.unlink(missing_ok=True)
    memory = AdaptMemory(db_path=str(db), factor=FACTORS[arm])
    service = SleepService(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    losses: list[float] = []
    report = None
    previous = None
    try:
        for cycle, trials in enumerate(world["cycles"]):
            events = [tag for pair in trials for tag in pair]
            distributions = _organica_distributions(report, world["tags"])
            losses.append(float(_cycle_loss(events, previous, distributions, world["tags"])))
            for event in events:
                memory.store(event, event_type="event", source="adapt:%d" % cycle)
            report = service.run_sleep_cycle()
            previous = events[-1]
        calls = list(memory.calls)
        facts = {
            "arm": arm,
            "family": family,
            "seed": seed,
            "factor": FACTORS[arm],
            "final_nll": statistics.mean(losses[FINAL_START:CYCLES]),
            "decay_calls_count": len(calls),
            "decay_factors": sorted({call["factor"] for call in calls}),
            "decay_rows_min": min((call["rows"] for call in calls), default=0),
            "mass_unchanged": all(call["mass_before"] == call["mass_after"] for call in calls),
            "mass_declined": any(call["mass_after"] < call["mass_before"] for call in calls),
            "losses": losses,
        }
        return facts
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def part_path(arm: str, family: str, seed: int) -> Path:
    return PARTS / ("%s_%s_%d.json" % (arm, family, seed))


def seeds_are_fresh() -> bool:
    if ARTIFACT.exists():
        try:
            recorded = json.loads(ARTIFACT.read_text(encoding="utf-8")).get("seeds") or []
        except (OSError, ValueError):
            recorded = []
        if tuple(recorded) == SEEDS:
            return True
    return not (set(SEEDS) & harvest_seeds(ROOT / "docs"))


def measure(arm: str) -> int:
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to run")
    if "executions: 0" not in text:
        raise SystemExit("the protocol already records an execution; refusing to run again")
    if not seeds_are_fresh():
        raise SystemExit("the pre-registered seed block is already used under docs/")
    if arm not in ARMS:
        raise SystemExit("arm must be one of %r" % (ARMS,))

    PARTS.mkdir(parents=True, exist_ok=True)
    for family in FAMILIES:
        for seed in SEEDS:
            path = part_path(arm, family, seed)
            if path.exists():
                part = json.loads(path.read_text(encoding="utf-8"))
                if len(part.get("losses") or []) == CYCLES:
                    print("cached", path.name, flush=True)
                    continue
            facts = run_cell(arm, family, seed)
            path.write_text(json.dumps(engine_stamp.stamp(facts), indent=1) + "\n", encoding="utf-8")
            print("%s %s %d final=%.5f mass=%s"
                  % (arm, family, seed, facts["final_nll"], facts["decay_factors"]),
                  flush=True)
    return 0


def load_parts() -> list[dict]:
    cells: list[dict] = []
    for arm in ARMS:
        for family in FAMILIES:
            for seed in SEEDS:
                path = part_path(arm, family, seed)
                if not path.exists():
                    raise SystemExit("missing part %s; run the arm first" % path.name)
                part = json.loads(path.read_text(encoding="utf-8"))
                if part.get("arm") != arm or part.get("family") != family or part.get("seed") != seed:
                    raise SystemExit("part %s does not hold the cell it is named for" % path.name)
                if len(part.get("losses") or []) != CYCLES:
                    raise SystemExit("part %s is short" % path.name)
                cells.append(part)
    return cells


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _bootstrap_interval(values: list[float]) -> list[float]:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(values)
    means = sorted(_mean([values[rng.randrange(n)] for _ in range(n)])
                   for _ in range(BOOTSTRAP_REPLICATES))

    def quantile(q: float) -> float:
        position = (len(means) - 1) * q
        lo, hi = math.floor(position), math.ceil(position)
        if lo == hi:
            return means[lo]
        return means[lo] + (means[hi] - means[lo]) * (position - lo)

    return [round(quantile(0.0125), 6), round(quantile(0.9875), 6)]


def summarize(cells: list[dict]) -> dict:
    by_key = {(cell["arm"], cell["family"], cell["seed"]): cell for cell in cells}
    summary: dict[str, dict] = {}
    for arm in ARMS:
        pooled: list[float] = []
        families: dict[str, dict] = {}
        for family in FAMILIES:
            deltas, finals = [], []
            for seed in SEEDS:
                cell = by_key[(arm, family, seed)]
                shipped = by_key[("shipped", family, seed)]
                finals.append(cell["final_nll"])
                deltas.append(cell["final_nll"] - shipped["final_nll"])
            pooled.extend(deltas)
            families[family] = {
                "cells": len(deltas),
                "final_nll_mean": round(_mean(finals), 6),
                "delta_mean": round(_mean(deltas), 6),
                "delta_ci": _bootstrap_interval(deltas),
            }
        summary[arm] = {
            "families": families,
            "pooled": {
                "cells": len(pooled),
                "delta_mean": round(_mean(pooled), 6),
                "delta_ci": _bootstrap_interval(pooled),
            },
        }
    return summary


def _cost(item: dict) -> bool:
    return item["delta_mean"] >= MARGIN and item["delta_ci"][0] > 0


def _better(item: dict) -> bool:
    return item["delta_mean"] <= -MARGIN and item["delta_ci"][1] < 0


def finish() -> dict:
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to finish")
    if "executions: 0" not in text:
        raise SystemExit("the protocol already records an execution")
    if not seeds_are_fresh():
        raise SystemExit("the pre-registered seed block is already used under docs/")

    cells = load_parts()
    summary = summarize(cells)
    pooled = {arm: summary[arm]["pooled"] for arm in ARMS}
    cost = {arm: _cost(pooled[arm]) for arm in ARMS if arm != "shipped"}
    better = {arm: _better(pooled[arm]) for arm in ARMS if arm != "shipped"}

    gates = {
        "G1_factor_live": all(
            cell["decay_calls_count"] == CYCLES
            and cell["decay_factors"] == [FACTORS[cell["arm"]]]
            and (cell["mass_unchanged"] if cell["arm"] == "no_decay"
                 else cell["decay_rows_min"] > 0)
            for cell in cells
        ),
        "G2_denominators": all(
            len(cell["losses"]) == CYCLES
            and all(math.isfinite(value) for value in cell["losses"])
            for cell in cells
        ),
        "G3_seed_independence": seeds_are_fresh(),
        "G4_complete_design": len(cells) == len(ARMS) * len(FAMILIES) * len(SEEDS),
        "G5_perturbation_changes_mass": all(
            cell["mass_declined"] for cell in cells if cell["arm"] == "shipped"
        ) and all(
            cell["mass_unchanged"] for cell in cells if cell["arm"] == "no_decay"
        ),
    }
    predictions = {
        "P1_no_decay_mass_unchanged": all(
            cell["mass_unchanged"] for cell in cells if cell["arm"] == "no_decay"
        ),
        "P2_shipped_mass_declines": all(
            cell["mass_declined"] for cell in cells if cell["arm"] == "shipped"
        ),
        "P3_no_decay_mapping_cost": summary["no_decay"]["families"]["mapping_mix"]["delta_mean"] > 0,
        "P4_operating_no_worse_than_ceiling": (
            pooled["factor09925"]["delta_mean"] <= pooled["no_decay"]["delta_mean"]
        ),
        "P5_cost_detected": cost["factor09925"] or cost["no_decay"],
        "P6_anchor_not_better": pooled["factor099"]["delta_mean"] > -MARGIN,
    }
    if not all(gates.values()):
        label = "VOID_INSTRUMENT"
    elif cost["factor09925"] and cost["no_decay"]:
        label = "BOTH_COST"
    elif cost["no_decay"]:
        label = "NO_DECAY_ONLY_COST"
    elif cost["factor09925"]:
        label = "OPERATING_ONLY_COST"
    elif better["factor09925"] or better["no_decay"]:
        label = "ARM_BETTER"
    else:
        label = "NO_COST_DETECTED"

    artifact = {
        "date": date.today().isoformat(),
        "engine_version": __import__("organica").__version__,
        "question": "Q049",
        "protocol_digest": FROZEN_DIGEST,
        "preregistration": "docs/DECAY-ADAPTATION-PREREGISTRATION.md",
        "seeds": list(SEEDS),
        "arms": list(ARMS),
        "families": list(FAMILIES),
        "cycles": CYCLES,
        "final_window": [FINAL_START, CYCLES - 1],
        "margin": MARGIN,
        "bootstrap": {"replicates": BOOTSTRAP_REPLICATES, "seed": BOOTSTRAP_SEED,
                      "interval": "97.5% paired percentile"},
        "cells": cells,
        "summary": summary,
        "pooled": pooled,
        "cost": cost,
        "better": better,
        "gates": gates,
        "predictions": predictions,
        "label": label,
    }
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1) + "\n", encoding="utf-8")
    return artifact


def render(artifact: dict) -> str:
    lines = [
        "# Does persistence cost adaptation? — result",
        "",
        "Generated from `docs/decay_adaptation.json` by",
        "`python -m benchmarks.decay_adaptation --render`. Do not edit by hand.",
        "",
        "Pre-registration: `docs/DECAY-ADAPTATION-PREREGISTRATION.md`. Four decay arms on the",
        "two Phase J gradual-shift families, 5 seeds, 80 cycles; endpoint is final NLL over",
        "cycles 60-79 on the shifted world.",
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "| Arm | Family | Final NLL | Delta vs shipped | 97.5% CI | Cells |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for arm in artifact["arms"]:
        for family in artifact["families"]:
            row = artifact["summary"][arm]["families"][family]
            lines.append("| %s | %s | %.6f | %+.6f | %s | %d |"
                         % (arm, family, row["final_nll_mean"], row["delta_mean"],
                            row["delta_ci"], row["cells"]))
        row = artifact["summary"][arm]["pooled"]
        lines.append("| **%s** | **pooled** |  | **%+.6f** | **%s** | **%d** |"
                     % (arm, row["delta_mean"], row["delta_ci"], row["cells"]))
    lines += [
        "",
        "A positive delta means the arm has higher post-shift loss than shipped, so it adapted",
        "worse. Cost is a pooled mean of at least %.2f nats per event with the interval's lower"
        % artifact["margin"],
        "bound above zero; better is the reverse. The 0.99 arm is descriptive only.",
        "",
        "## Gates",
        "",
        "| Gate | Result |",
        "| --- | --- |",
    ]
    for name, ok in artifact["gates"].items():
        lines.append("| %s | %s |" % (name, "pass" if ok else "FAIL"))
    lines += ["", "## Predictions", "", "| Prediction | Result |", "| --- | --- |"]
    for name, ok in artifact["predictions"].items():
        lines.append("| %s | %s |" % (name, "held" if ok else "failed"))
    lines += [
        "",
        "## Reading",
        "",
        "This is a five-seed pilot on two synthetic gradual-shift families. It is not a Phase J",
        "verdict, and it does not generalize to other generators or natural environments. The",
        "endpoint is online next-event NLL; it does not show that the organism learned the right",
        "structure. No capability, held-out prediction, revision or transfer task is scored.",
        "",
        "Survival at 1.0 is a persistence result. A no-cost adaptation result here would not make",
        "1.0 or 0.9925 an adoption recommendation, and a cost result prices a trade rather than",
        "closing the persistence question.",
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
    parser.add_argument("--arm", choices=ARMS)
    args = parser.parse_args(argv)
    if args.measure:
        if not args.arm:
            raise SystemExit("--measure needs --arm")
        return measure(args.arm)
    if args.finish:
        artifact = finish()
        print("%s: %s" % (artifact["label"], artifact["pooled"]))
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
    from benchmarks.decay_adaptation_prereg import validate
    registry = json.loads((ROOT / "docs" / "research_question_registry.json").read_text(encoding="utf-8"))
    problems = validate(text, registry, artifact,
                        seeds_used=harvest_seeds(ROOT / "docs") - set(SEEDS))
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    if artifact and artifact["label"] not in DOC.read_text(encoding="utf-8"):
        raise SystemExit("FAIL: the page does not name the label")
    print("decay adaptation: protocol frozen, %s"
          % ("executed" if artifact else "no execution recorded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
