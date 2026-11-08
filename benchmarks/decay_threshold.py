"""Measure the decay threshold inside Q048's 0.99-0.9925 gap.

The screen runs all 24 four-decimal candidates on one seed; the boundary and its immediate
neighbours are then confirmed on three seeds. The engine is unchanged: each cell is Q048's
in-process forced-factor memory over the same `lattice_L1` world.

    ./.venv/bin/python -m benchmarks.decay_threshold --measure --screen --max-cells 8
    ./.venv/bin/python -m benchmarks.decay_threshold --measure --confirm
    ./.venv/bin/python -m benchmarks.decay_threshold --finish
    ./.venv/bin/python -m benchmarks.decay_threshold --render
    ./.venv/bin/python -m benchmarks.decay_threshold --check
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from benchmarks.decay_confirmation import harvest_seeds
from benchmarks.decay_sweep import run_cell
from benchmarks.decay_threshold_prereg import (
    ARTIFACT,
    CANDIDATES,
    FROZEN_DIGEST,
    SCREEN_SEED,
    SEEDS,
    protocol_digest,
)
from benchmarks.decay_threshold_prereg import DOC as PREREG
from benchmarks.reference_death_ledger import CYCLES, cell_facts, stimulus

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "decay_threshold" / "parts"
DOC = ROOT / "docs" / "DECAY-THRESHOLD.md"
ALIVE = CYCLES + 1


def seeds_are_fresh() -> bool:
    if ARTIFACT.exists():
        try:
            recorded = json.loads(ARTIFACT.read_text(encoding="utf-8")).get("seeds") or []
        except (OSError, ValueError):
            recorded = []
        if tuple(recorded) == SEEDS:
            return True
    return not (set(SEEDS) & harvest_seeds(ROOT / "docs"))


def part_path(prefix: str, factor: float, seed: int) -> Path:
    return PARTS / ("%s_%s_%d.json" % (prefix, str(factor), seed))


def _check_frozen() -> str:
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to run")
    if "executions: 0" not in text:
        raise SystemExit("the protocol already records an execution; refusing to run again")
    if not seeds_are_fresh():
        raise SystemExit("the pre-registered seed block is already used under docs/")
    return text


def _run(prefix: str, factor: float, seed: int, events: list[str]) -> dict:
    path = part_path(prefix, factor, seed)
    if path.exists():
        part = json.loads(path.read_text(encoding="utf-8"))
        if len(part.get("ledger") or []) == CYCLES:
            print("cached", path.name, flush=True)
            return part
    rows, extra = run_cell(factor, seed, events)
    facts = {key: value for key, value in extra.items()
             if key not in ("stable_series", "decay_calls")}
    facts.update(cell_facts(rows))
    part = {"factor": float(factor), "seed": seed, "facts": facts,
            "ledger": rows, "stable_series": extra["stable_series"]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(part, indent=1) + "\n", encoding="utf-8")
    print("%s %s %d death=%s stable_zero=%s live=%s"
          % (prefix, factor, seed, facts["death_cycle"], facts["stable_zero"],
             facts["decay_factors"]), flush=True)
    return part


def measure_screen(max_cells: int | None = None) -> int:
    _check_frozen()
    events = stimulus()
    ran = 0
    for factor in CANDIDATES:
        path = part_path("screen", factor, SCREEN_SEED)
        if path.exists():
            part = json.loads(path.read_text(encoding="utf-8"))
            if len(part.get("ledger") or []) == CYCLES:
                continue
        if max_cells is not None and ran >= max_cells:
            break
        _run("screen", factor, SCREEN_SEED, events)
        ran += 1
    remaining = [factor for factor in CANDIDATES
                 if not (part_path("screen", factor, SCREEN_SEED).exists()
                         and len(json.loads(part_path("screen", factor, SCREEN_SEED)
                                            .read_text(encoding="utf-8")).get("ledger") or [])
                         == CYCLES)]
    print("screen ran %d; %d remaining" % (ran, len(remaining)), flush=True)
    return 0


def screen_cells() -> list[dict]:
    cells = []
    for factor in CANDIDATES:
        path = part_path("screen", factor, SCREEN_SEED)
        if not path.exists():
            raise SystemExit("missing screen part %s" % path.name)
        part = json.loads(path.read_text(encoding="utf-8"))
        if part.get("factor") != factor or part.get("seed") != SCREEN_SEED:
            raise SystemExit("screen part %s does not hold its cell" % path.name)
        if len(part.get("ledger") or []) != CYCLES:
            raise SystemExit("screen part %s is short" % path.name)
        cells.append({"factor": factor, "seed": SCREEN_SEED, **part["facts"]})
    return cells


def confirmation_factors() -> list[float]:
    alive = [cell["factor"] for cell in screen_cells() if cell["death_cycle"] == ALIVE]
    if not alive:
        return []
    boundary = min(alive)
    lower = round(max(0.99, boundary - 0.0001), 4)
    upper = round(min(0.9925, boundary + 0.0001), 4)
    return sorted({lower, boundary, upper})


def measure_confirm(max_cells: int | None = None) -> int:
    _check_frozen()
    events = stimulus()
    factors = confirmation_factors()
    if not factors:
        print("no interior survivor; no confirmation needed", flush=True)
        return 0
    print("confirming %s on %s" % (factors, SEEDS), flush=True)
    ran = 0
    for factor in factors:
        for seed in SEEDS:
            path = part_path("confirm", factor, seed)
            if path.exists():
                part = json.loads(path.read_text(encoding="utf-8"))
                if len(part.get("ledger") or []) == CYCLES:
                    continue
            if max_cells is not None and ran >= max_cells:
                print("confirm ran %d; stopping at the batch limit" % ran, flush=True)
                return 0
            _run("confirm", factor, seed, events)
            ran += 1
    print("confirm ran %d" % ran, flush=True)
    return 0


def confirm_cells(factors: list[float]) -> list[dict]:
    cells = []
    for factor in factors:
        for seed in SEEDS:
            path = part_path("confirm", factor, seed)
            if not path.exists():
                raise SystemExit("missing confirmation part %s" % path.name)
            part = json.loads(path.read_text(encoding="utf-8"))
            if part.get("factor") != factor or part.get("seed") != seed:
                raise SystemExit("confirmation part %s does not hold its cell" % path.name)
            if len(part.get("ledger") or []) != CYCLES:
                raise SystemExit("confirmation part %s is short" % path.name)
            cells.append({"factor": factor, "seed": seed, **part["facts"]})
    return cells


def _screen_label(cells: list[dict]) -> tuple[str, list[float], float | None]:
    deaths = [cell["death_cycle"] for cell in cells]
    alive = [cell["factor"] for cell in cells if cell["death_cycle"] == ALIVE]
    if len(cells) != len(CANDIDATES):
        return "VOID_INSTRUMENT", alive, None
    if any(death < deaths[index] for index, death in enumerate(deaths[1:])):
        return "NON_MONOTONE", alive, None
    if not alive:
        return "NO_INTERIOR_SURVIVOR", alive, None
    if len(alive) == len(CANDIDATES):
        return "BELOW_SCREEN", alive, None
    return "THRESHOLD_FOUND", alive, min(alive)


def finish() -> dict:
    _check_frozen()
    screen = screen_cells()
    label, alive, boundary = _screen_label(screen)
    factors = [] if boundary is None else sorted({
        round(max(0.99, boundary - 0.0001), 4),
        boundary,
        round(min(0.9925, boundary + 0.0001), 4),
    })
    confirm = confirm_cells(factors) if factors else []

    gates = {
        "G1_screen_factor_live": all(
            cell["decay_calls_count"] == CYCLES
            and cell["decay_factors"] == [cell["factor"]]
            and cell["decay_rows_min"] > 0
            for cell in screen
        ),
        "G2_confirmation_factor_live": all(
            cell["decay_calls_count"] == CYCLES
            and cell["decay_factors"] == [cell["factor"]]
            and cell["decay_rows_min"] > 0
            for cell in confirm
        ),
        "G3_denominators": all(
            cell["cycles"] == CYCLES and cell["theory_cycles"] > 0
            for cell in screen + confirm
        ),
        "G4_seeds_fresh": seeds_are_fresh(),
        "G5_screen_complete": len(screen) == len(CANDIDATES),
        "G6_confirmation_complete": (
            label != "THRESHOLD_FOUND" or len(confirm) == len(factors) * len(SEEDS)
        ),
    }

    if boundary is not None and factors:
        at = {cell["factor"]: cell for cell in confirm}
        lower, upper = factors[0], factors[-1]
        confirmed = (
            all(at[boundary]["seed"] == seed for seed in SEEDS)
            and all(cell["death_cycle"] == ALIVE for cell in confirm if cell["factor"] == boundary)
            and all(cell["death_cycle"] < ALIVE for cell in confirm if cell["factor"] == lower)
            and all(cell["death_cycle"] == ALIVE for cell in confirm if cell["factor"] == upper)
            and len(confirm) == len(factors) * len(SEEDS)
        )
    else:
        confirmed = False

    predictions = {
        "P1_screen_monotone": label != "NON_MONOTONE",
        "P2_interior_survivor": bool(alive),
        "P3_below_09925": bool(alive) and min(alive) < 0.9925,
        "P4_boundary_alive_3": boundary is not None and all(
            cell["death_cycle"] == ALIVE for cell in confirm if cell["factor"] == boundary
        ),
        "P5_lower_dead_3": boundary is not None and factors and all(
            cell["death_cycle"] < ALIVE for cell in confirm if cell["factor"] == factors[0]
        ),
        "P6_upper_alive_3": boundary is not None and factors and all(
            cell["death_cycle"] == ALIVE for cell in confirm if cell["factor"] == factors[-1]
        ),
    }

    if not all(gates.values()):
        label = "VOID_INSTRUMENT"
    elif label == "THRESHOLD_FOUND" and not confirmed:
        label = "CONFIRMATION_FAILED"

    smallest = boundary if label == "THRESHOLD_FOUND" else (
        0.9901 if label == "BELOW_SCREEN" else None
    )
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": __import__("organica").__version__,
        "question": "Q050",
        "protocol_digest": FROZEN_DIGEST,
        "preregistration": "docs/DECAY-THRESHOLD-PREREGISTRATION.md",
        "world": "lattice_L1",
        "arm": "FULL",
        "seeds": list(SEEDS),
        "screen_seed": SCREEN_SEED,
        "cycles": CYCLES,
        "candidates": list(CANDIDATES),
        "screen_cells": len(screen),
        "screen": screen,
        "confirm_factors": factors,
        "confirm_cells": len(confirm),
        "confirm": confirm,
        "screen_boundary": boundary,
        "smallest_survivor": smallest,
        "confirmed_boundary": boundary if label == "THRESHOLD_FOUND" else None,
        "gates": gates,
        "predictions": predictions,
        "label": label,
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=1) + "\n", encoding="utf-8")
    return artifact


def render(artifact: dict) -> str:
    lines = [
        "# The decay threshold inside 0.99–0.9925 — result",
        "",
        "Generated from `docs/decay_threshold.json` by "
        "`python -m benchmarks.decay_threshold --render`. Do not edit by hand.",
        "",
        "Pre-registration: `docs/DECAY-THRESHOLD-PREREGISTRATION.md`. Twenty-four "
        "four-decimal candidates, screen seed 20302701, confirmation seeds "
        "20302701–20302703.",
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "| Factor | Screen death | Alive at 300 |",
        "| --- | --- | --- |",
    ]
    for cell in artifact["screen"]:
        lines.append("| %s | %s | %s |"
                     % (cell["factor"], cell["death_cycle"],
                        "yes" if cell["death_cycle"] == artifact["cycles"] + 1 else "no"))
    lines += [
        "",
        "**Smallest confirmed survivor:** %s."
        % ("none" if artifact["smallest_survivor"] is None
           else artifact["smallest_survivor"]),
        "",
        "**Screen boundary:** %s."
        % ("none" if artifact["screen_boundary"] is None else artifact["screen_boundary"]),
        "",
        "## Confirmation",
        "",
    ]
    if artifact["confirm"]:
        lines += ["| Factor | Seed | Death |", "| --- | --- | --- |"]
        for cell in artifact["confirm"]:
            lines.append("| %s | %s | %s |"
                         % (cell["factor"], cell["seed"], cell["death_cycle"]))
    else:
        lines.append("No boundary was confirmed; see the label.")
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
        "This is a 0.0001-resolution screen plus a three-seed confirmation at the boundary and its",
        "two immediate neighbours. The screen is one seed per candidate; only the confirmed",
        "boundary is a claim. Survival is theory-layer presence, not theory identity, and no",
        "adaptation or capability task is scored here.",
        "",
        "The endpoints 0.99 and 0.9925 are Q048 results on a different seed block; this page",
        "does not re-measure them.",
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
    parser.add_argument("--screen", action="store_true")
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--max-cells", type=int, default=None)
    args = parser.parse_args(argv)
    if args.measure:
        if not (args.screen or args.confirm):
            raise SystemExit("--measure needs --screen or --confirm")
        if args.screen:
            return measure_screen(args.max_cells)
        return measure_confirm(args.max_cells)
    if args.finish:
        artifact = finish()
        print("%s: survivor=%s boundary=%s"
              % (artifact["label"], artifact["smallest_survivor"],
                 artifact["confirmed_boundary"]))
        return 0
    if args.render:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        page = render(artifact)
        if "{" in page or "}" in page:
            raise SystemExit("the page contains a brace; refusing to write it")
        DOC.write_text(page, encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0

    from benchmarks.decay_threshold_prereg import validate
    text = PREREG.read_text(encoding="utf-8")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else None
    registry = json.loads((ROOT / "docs" / "research_question_registry.json")
                          .read_text(encoding="utf-8"))
    problems = validate(text, registry, artifact,
                        seeds_used=harvest_seeds(ROOT / "docs") - set(SEEDS))
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    if artifact and artifact["label"] not in DOC.read_text(encoding="utf-8"):
        raise SystemExit("FAIL: the page does not name the label")
    print("decay threshold: protocol frozen, %s"
          % ("executed" if artifact else "no execution recorded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
