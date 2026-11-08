"""Run the decay-factor sweep on the cycle-39 world.

Pre-registered in ``docs/DECAY-SWEEP-PREREGISTRATION.md``. The engine is unchanged: each
factor is an in-process memory subclass that forces one decay factor, and the death ledger's
own observer records the theory layer. The page plots theory death and stable-edge zero
against the factor; the smallest factor alive at cycle 300 is reported as the survivor.

    ./.venv/bin/python -m benchmarks.decay_sweep --measure --factor 0.985
    ./.venv/bin/python -m benchmarks.decay_sweep --finish
    ./.venv/bin/python -m benchmarks.decay_sweep --render
    ./.venv/bin/python -m benchmarks.decay_sweep --check
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import date
from pathlib import Path

from benchmarks.decay_confirmation import harvest_seeds
from benchmarks.decay_sweep_prereg import (
    ARTIFACT,
    CONTROL_SEED,
    FACTORS,
    FROZEN_DIGEST,
    SEEDS,
    protocol_digest,
)
from benchmarks.decay_sweep_prereg import DOC as PREREG
from benchmarks.operating_point import stable_count, zero_cycle
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
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "decay_sweep" / "parts"
DOC = ROOT / "docs" / "DECAY-SWEEP.md"
STEP_CYCLES = 50
ANCHOR = 228


class SweepMemory(MemoryService):
    """Force one temporal-decay factor and record every applied perturbation."""

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
        self.calls.append({
            "factor": self.factor,
            "rows": int(rows),
            "mass_before": int(before),
            "mass_after": int(after),
        })
        return rows


def run_cell(factor: float, seed: int, events: list[str]) -> tuple[list[dict], dict]:
    """One factor on one seed, with the ledger's bootstrap and feed."""
    db = temp_db("decay_sweep_%s_%s.db" % (str(factor).replace(".", "p"), seed))
    db.unlink(missing_ok=True)
    memory = SweepMemory(db_path=str(db), factor=factor)
    service = ledger_class("FULL")(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    service.ledger_reset()
    stable: list[int] = []
    try:
        for text in events:
            memory.store(text, event_type="event", source="seed:bootstrap")
        for cycle in range(CYCLES):
            start = (cycle * EVENTS_PER_CYCLE) % len(events)
            for text in events[start:start + EVENTS_PER_CYCLE]:
                memory.store(text, event_type="event", source="cycle:%d" % cycle)
            service.run_sleep_cycle()
            stable.append(stable_count(service))
        rows = list(service.ledger_rows)
        facts = cell_facts(rows)
        calls = list(memory.calls)
        extra = {
            "factor": float(factor),
            "stable_series": stable,
            "stable_peak": max(stable) if stable else 0,
            "stable_final": stable[-1] if stable else 0,
            "stable_zero": zero_cycle(stable),
            "decay_calls": calls,
            "decay_calls_count": len(calls),
            "decay_factors": sorted({call["factor"] for call in calls}),
            "decay_rows_min": min((call["rows"] for call in calls), default=0),
            "mass_unchanged": all(call["mass_before"] == call["mass_after"] for call in calls),
        }
        facts.update({key: value for key, value in extra.items()
                      if key not in ("stable_series", "decay_calls")})
        return rows, extra
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def part_path(factor: float, seed: int) -> Path:
    return PARTS / ("%s_%d.json" % (str(factor), seed))


def seeds_are_fresh() -> bool:
    if ARTIFACT.exists():
        try:
            recorded = json.loads(ARTIFACT.read_text(encoding="utf-8")).get("seeds") or []
        except (OSError, ValueError):
            recorded = []
        if tuple(recorded) == SEEDS:
            return True
    return not (set(SEEDS) & harvest_seeds(ROOT / "docs"))


def measure(factor: float) -> int:
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to run")
    if "executions: 0" not in text:
        raise SystemExit("the protocol already records an execution; refusing to run again")
    if not seeds_are_fresh():
        raise SystemExit("the pre-registered seed block is already used under docs/")
    if factor not in FACTORS:
        raise SystemExit("factor must be one of %r" % (FACTORS,))

    events = stimulus()
    PARTS.mkdir(parents=True, exist_ok=True)
    for seed in SEEDS:
        path = part_path(factor, seed)
        if path.exists():
            part = json.loads(path.read_text(encoding="utf-8"))
            if len(part.get("ledger") or []) == CYCLES:
                print("cached", path.name, flush=True)
                continue
        rows, extra = run_cell(factor, seed, events)
        facts = {key: value for key, value in extra.items()
                 if key not in ("stable_series", "decay_calls")}
        facts.update(cell_facts(rows))
        part = {
            "factor": float(factor),
            "seed": seed,
            "facts": facts,
            "ledger": rows,
            "stable_series": extra["stable_series"],
        }
        path.write_text(json.dumps(engine_stamp.stamp(part), indent=1) + "\n", encoding="utf-8")
        print("%s %d death=%s stable_zero=%s live=%s"
              % (factor, seed, facts["death_cycle"], facts["stable_zero"],
                 facts["decay_factors"]), flush=True)
    return 0


def load_parts() -> list[dict]:
    cells: list[dict] = []
    for factor in FACTORS:
        for seed in SEEDS:
            path = part_path(factor, seed)
            if not path.exists():
                raise SystemExit("missing part %s; run the factor first" % path.name)
            part = json.loads(path.read_text(encoding="utf-8"))
            if part.get("factor") != factor or part.get("seed") != seed:
                raise SystemExit("part %s does not hold the cell it is named for" % path.name)
            if len(part.get("ledger") or []) != CYCLES:
                raise SystemExit("part %s is short" % path.name)
            cells.append({"factor": factor, "seed": seed, **part["facts"]})
    return cells


def summary(cells: list[dict], factor: float) -> dict:
    rows = [cell for cell in cells if cell["factor"] == factor]
    deaths = {cell["seed"]: cell["death_cycle"] for cell in rows}
    stable_zero = {cell["seed"]: cell["stable_zero"] for cell in rows}
    return {
        "cells": len(rows),
        "death_cycles": [deaths[seed] for seed in SEEDS],
        "median_death_cycle": statistics.median(deaths.values()),
        "per_seed": {str(seed): deaths[seed] for seed in SEEDS},
        "alive_at_end": sum(1 for cell in rows if cell["death_cycle"] == CYCLES + 1),
        "stable_zero_cycles": [stable_zero[seed] for seed in SEEDS],
        "stable_peak": max(cell["stable_peak"] for cell in rows),
        "stable_final": max(cell["stable_final"] for cell in rows),
        "theory_cycles": sum(cell["theory_cycles"] for cell in rows),
        "peak_theories": max(cell["theories_total"] for cell in rows),
        "decay_calls_count": min(cell["decay_calls_count"] for cell in rows),
        "decay_factors": sorted({item for cell in rows for item in cell["decay_factors"]}),
        "mass_unchanged": all(cell["mass_unchanged"] for cell in rows),
    }


def decide(gates: dict[str, bool], summaries: dict[float, dict],
           medians: list[float]) -> str:
    if not (gates["G1_neutral_observer"] and gates["G3_factor_live"]
            and gates["G4_denominators"] and gates["G5_seed_independence"]):
        return "VOID_INSTRUMENT"
    if not gates["G2_anchor_228"]:
        return "ANCHOR_NOT_REPRODUCED"
    diffs = [medians[index + 1] - medians[index] for index in range(len(medians) - 1)]
    if any(diff < 0 for diff in diffs):
        return "NON_MONOTONE"
    if len(set(medians)) <= 1:
        return "NO_EFFECT_IN_RANGE"
    if not any(factor < 1.0 and summaries[factor]["alive_at_end"] == len(SEEDS)
               for factor in FACTORS):
        return "ONLY_1_0_SURVIVES"
    if max(diffs) >= STEP_CYCLES:
        return "STEP"
    return "SMOOTH"


def finish() -> dict:
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to finish")
    if "executions: 0" not in text:
        raise SystemExit("the protocol already records an execution")
    if not seeds_are_fresh():
        raise SystemExit("the pre-registered seed block is already used under docs/")

    cells = load_parts()
    control = control_facts(run_cell(0.95, CONTROL_SEED, stimulus())[0])
    summaries = {factor: summary(cells, factor) for factor in FACTORS}
    medians = [summaries[factor]["median_death_cycle"] for factor in FACTORS]
    diffs = [medians[index + 1] - medians[index] for index in range(len(medians) - 1)]

    gates = {
        "G1_neutral_observer": bool(control["theory_match"] and control["belief_match"]),
        "G2_anchor_228": all(cell["death_cycle"] == ANCHOR
                             for cell in cells if cell["factor"] == 0.99),
        "G3_factor_live": all(
            cell["decay_calls_count"] == CYCLES
            and cell["decay_factors"] == [cell["factor"]]
            and (cell["mass_unchanged"] if cell["factor"] == 1.0
                 else cell["decay_rows_min"] > 0)
            for cell in cells
        ),
        "G4_denominators": all(cell["cycles"] == CYCLES and cell["theory_cycles"] > 0
                               for cell in cells),
        "G5_seed_independence": seeds_are_fresh(),
    }
    predictions = {
        "P1_anchor_228": gates["G2_anchor_228"],
        "P2_monotone_death": all(diff >= 0 for diff in diffs),
        "P3_0985_before_099": medians[0] < medians[1],
        "P4_no_decay_survives": all(
            cell["death_cycle"] == CYCLES + 1 for cell in cells if cell["factor"] == 1.0
        ),
        "P5_step_at_least_50": max(diffs) >= STEP_CYCLES,
        "P6_stable_zero_monotone": all(
            summaries[FACTORS[index]]["stable_zero_cycles"][0]
            <= summaries[FACTORS[index + 1]]["stable_zero_cycles"][0]
            for index in range(len(FACTORS) - 1)
        ),
        "P7_interior_survivor": any(
            factor < 1.0 and summaries[factor]["alive_at_end"] == len(SEEDS)
            for factor in FACTORS
        ),
    }
    survivors = [factor for factor in FACTORS
                 if summaries[factor]["alive_at_end"] == len(SEEDS)]
    step_index = max(range(len(diffs)), key=lambda index: diffs[index]) if diffs else None
    largest_step = {
        "cycles": max(diffs) if diffs else 0,
        "from": FACTORS[step_index] if step_index is not None else None,
        "to": FACTORS[step_index + 1] if step_index is not None else None,
    }
    label = decide(gates, summaries, medians)
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": __import__("organica").__version__,
        "question": "Q048",
        "protocol_digest": FROZEN_DIGEST,
        "preregistration": "docs/DECAY-SWEEP-PREREGISTRATION.md",
        "world": "lattice_L1",
        "arm": "FULL",
        "seeds": list(SEEDS),
        "control_seed": CONTROL_SEED,
        "cycles": CYCLES,
        "factors": list(FACTORS),
        "step_threshold": STEP_CYCLES,
        "anchor_death": ANCHOR,
        "cells": cells,
        "summary": {str(factor): summaries[factor] for factor in FACTORS},
        "gates": gates,
        "predictions": predictions,
        "label": label,
        "smallest_survivor": min(survivors) if survivors else None,
        "survivors": survivors,
        "largest_step": largest_step,
        "control": control,
    }
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1) + "\n", encoding="utf-8")
    return artifact


def _svg(artifact: dict) -> str:
    factors = artifact["factors"]
    width, height = 760, 380
    left, top, plot_w, plot_h = 70, 40, 650, 270
    n = len(factors)

    def x(index: int) -> float:
        return left + index * plot_w / (n - 1)

    def y(value: float) -> float:
        return top + (301 - min(value, 301)) * plot_h / 301

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" role="img" '
        'aria-label="Theory death and stable-edge zero against decay factor">'
        % (width, height, width, height),
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="%d" y="20" font-family="sans-serif" font-size="15" fill="#111">'
        'Theory death and stable-edge zero vs decay factor (lattice_L1)</text>' % (left - 10),
    ]
    for tick in range(0, 301, 50):
        yy = y(tick)
        out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#e5e7eb" '
                   'stroke-width="1"/>' % (left, yy, left + plot_w, yy))
        out.append('<text x="%d" y="%.1f" text-anchor="end" font-family="sans-serif" '
                   'font-size="11" fill="#667085">%d</text>' % (left - 8, yy + 4, tick))
    out.append('<text x="18" y="%d" transform="rotate(-90 18 %d)" '
               'font-family="sans-serif" font-size="12" fill="#344054">survival / zero cycle</text>'
               % (top + plot_h // 2, top + plot_h // 2))
    for index, factor in enumerate(factors):
        out.append('<text x="%.1f" y="%d" text-anchor="middle" '
                   'font-family="sans-serif" font-size="11" fill="#344054">%s</text>'
                   % (x(index), top + plot_h + 20, str(factor)))
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#667085" stroke-width="1"/>'
               % (left, top, left, top + plot_h))
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#667085" stroke-width="1"/>'
               % (left, top + plot_h, left + plot_w, top + plot_h))
    out.append('<text x="%d" y="%d" text-anchor="middle" font-family="sans-serif" '
               'font-size="12" fill="#344054">temporal decay factor</text>'
               % (left + plot_w // 2, height - 12))

    deaths = [artifact["summary"][str(factor)]["median_death_cycle"] for factor in factors]
    zeros = [artifact["summary"][str(factor)]["stable_zero_cycles"][0] for factor in factors]
    for series, colour, dash, label in (
        (deaths, "#1d4ed8", "", "theory death (301 = alive)"),
        (zeros, "#c2410c", ' stroke-dasharray="6 4"', "stable-edge zero"),
    ):
        points = " ".join("%.1f,%.1f" % (x(index), y(value))
                          for index, value in enumerate(series))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"%s/>'
                   % (points, colour, dash))
        for index, value in enumerate(series):
            out.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="%s"/>'
                       % (x(index), y(value), colour))
        out.append('<text x="%d" y="%d" font-family="sans-serif" font-size="11" '
                   'fill="%s">%s</text>' % (left + 12, top + 16 + (0 if colour == "#1d4ed8" else 18),
                                            colour, label))
    alive = [factor for factor in factors
             if artifact["summary"][str(factor)]["alive_at_end"] == len(artifact["seeds"])]
    out.append('<text x="%d" y="%d" text-anchor="end" font-family="sans-serif" '
               'font-size="11" fill="#667085">301 = alive at cycle %d</text>'
               % (left + plot_w, top - 4, artifact["cycles"]))
    out.append("</svg>")
    return "\n".join(out)


def render(artifact: dict) -> str:
    lines = [
        "# The decay factor sweep — result",
        "",
        "Generated from `docs/decay_sweep.json` by `python -m benchmarks.decay_sweep --render`.",
        "Do not edit by hand.",
        "",
        "Pre-registration: `docs/DECAY-SWEEP-PREREGISTRATION.md`. Seven factors on the",
        "falsifier's `lattice_L1` world, reference arm FULL, seeds 20302501-20302503.",
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "| Factor | Death cycles | Median | Alive at 300 | Stable zero | Peak stable | Final stable |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for factor in artifact["factors"]:
        summary = artifact["summary"][str(factor)]
        lines.append(
            "| %s | %s | %s | %d/3 | %s | %d | %d |"
            % (factor, summary["death_cycles"], summary["median_death_cycle"],
               summary["alive_at_end"], summary["stable_zero_cycles"],
               summary["stable_peak"], summary["stable_final"])
        )
    survivor = artifact["smallest_survivor"]
    lines += [
        "",
        "**Smallest factor alive at cycle 300:** %s."
        % ("none below 1.0" if survivor is None else str(survivor)),
        "",
        "**Largest adjacent step:** %s cycles, from %s to %s."
        % (artifact["largest_step"]["cycles"], artifact["largest_step"]["from"],
           artifact["largest_step"]["to"]),
        "",
        "## Survival versus decay",
        "",
        _svg(artifact),
        "",
        "The blue series is the median theory death cycle, with 301 at the top meaning the theory",
        "layer was still live at cycle 300. The orange series is the first stable-edge zero, also",
        "capped at 301. Both are read from the artifact; the plot is generated, not transcribed.",
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
        "A step means the operating point is a threshold on this range; a smooth curve means a",
        "gradient exists; only 1.0 surviving means the interior of this range is empty. In every",
        "case, 1.0 is the ceiling control, not an adoption recommendation.",
        "",
        "**`no_decay` survival is not adaptation.** This world is static and the protocol scores",
        "no held-out prediction, revision or adaptation task. The 42 and 30 figures from the",
        "degree-12 hub are not used here; Q047's `lattice_L1` `no_decay` stable peak is 21, and",
        "this sweep's stable peak is reported above.",
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
    parser.add_argument("--factor", type=float, choices=FACTORS)
    args = parser.parse_args(argv)
    if args.measure:
        if args.factor is None:
            raise SystemExit("--measure needs --factor")
        return measure(args.factor)
    if args.finish:
        artifact = finish()
        print("%s: survivor=%s step=%s"
              % (artifact["label"], artifact["smallest_survivor"],
                 artifact["largest_step"]))
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
    from benchmarks.decay_sweep_prereg import validate
    registry = json.loads((ROOT / "docs" / "research_question_registry.json").read_text(encoding="utf-8"))
    problems = validate(text, registry, artifact,
                        seeds_used=harvest_seeds(ROOT / "docs") - set(SEEDS))
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    if artifact and artifact["label"] not in DOC.read_text(encoding="utf-8"):
        raise SystemExit("FAIL: the page does not name the label")
    print("decay sweep: protocol frozen, %s"
          % ("executed" if artifact else "no execution recorded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
