"""Measure 0.9924 and 0.9925 on the same seed block, so the edge is paired.

Q050 left the threshold between 0.9924 (dead on seeds 20302701-20302703) and 0.9925
(Q048 survivor on a different block, 20302501-20302503). This module reruns only
0.9925 on the threshold block and reuses the three committed 0.9924 cells, so the
factor is the only thing that differs between the two sides of the edge.

    ./.venv/bin/python -m benchmarks.decay_paired_bracket --measure
    ./.venv/bin/python -m benchmarks.decay_paired_bracket --finish
    ./.venv/bin/python -m benchmarks.decay_paired_bracket --render
    ./.venv/bin/python -m benchmarks.decay_paired_bracket --check
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from benchmarks.decay_sweep import run_cell
from benchmarks.reference_death_ledger import CYCLES, cell_facts, stimulus

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "decay_threshold" / "parts"
ARTIFACT = ROOT / "docs" / "decay_paired_bracket.json"
DOC = ROOT / "docs" / "DECAY-PAIRED-BRACKET.md"
PREREG = ROOT / "docs" / "DECAY-THRESHOLD-PREREGISTRATION.md"
WORLD = "lattice_L1"
ARM = "FULL"
LOWER = 0.9924
UPPER = 0.9925
SEEDS = (20302701, 20302702, 20302703)
ALIVE = CYCLES + 1
BUCKETS = ("PAIRED_BRACKET_CONFIRMED", "PAIRED_BRACKET_NOT_CONFIRMED", "VOID")
#: The committed 0.9924 cells: the Q050 screen cell and the two section-13 edge cells.
LOWER_PARTS = {
    20302701: "screen_0.9924_20302701.json",
    20302702: "edge_0.9924_20302702.json",
    20302703: "edge_0.9924_20302703.json",
}
CELL_KEYS = ("factor", "seed", "death_cycle", "stable_zero", "decay_calls_count",
             "decay_factors", "decay_rows_min", "cycles", "theory_cycles",
             "last_nonzero_cycle")


def upper_part(seed: int) -> Path:
    return PARTS / ("paired_0.9925_%d.json" % seed)


def lower_part(seed: int) -> Path:
    return PARTS / LOWER_PARTS[seed]


def _load(path: Path, factor: float, seed: int) -> dict:
    if not path.exists():
        raise SystemExit("missing part %s" % path.name)
    part = json.loads(path.read_text(encoding="utf-8"))
    if part.get("factor") != factor or part.get("seed") != seed:
        raise SystemExit("part %s does not hold %s on seed %d" % (path.name, factor, seed))
    if len(part.get("ledger") or []) != CYCLES:
        raise SystemExit("part %s is short: %d cycles" % (path.name, len(part.get("ledger") or [])))
    return part


def measure(seeds=SEEDS) -> int:
    events = stimulus()
    for seed in seeds:
        path = upper_part(seed)
        if path.exists():
            _load(path, UPPER, seed)
            print("cached", path.name, flush=True)
            continue
        rows, extra = run_cell(UPPER, seed, events)
        facts = {key: value for key, value in extra.items()
                 if key not in ("stable_series", "decay_calls")}
        facts.update(cell_facts(rows))
        part = {"factor": UPPER, "seed": seed, "facts": facts,
                "ledger": rows, "stable_series": extra["stable_series"]}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(part, indent=1) + "\n", encoding="utf-8")
        print("paired 0.9925 %d death=%s stable_zero=%s live=%s"
              % (seed, facts["death_cycle"], facts["stable_zero"], facts["decay_factors"]),
              flush=True)
    return 0


def cells_from_parts() -> list[dict]:
    cells = []
    for factor, paths in ((LOWER, {seed: lower_part(seed) for seed in SEEDS}),
                          (UPPER, {seed: upper_part(seed) for seed in SEEDS})):
        for seed in SEEDS:
            part = _load(paths[seed], factor, seed)
            cell = {"seed": seed, "factor": factor, **part["facts"]}
            cell["seed"] = seed
            cell["factor"] = factor
            cell["part"] = paths[seed].relative_to(ROOT).as_posix()
            cells.append(cell)
    return cells


def gates_for(cells: list[dict]) -> dict:
    upper = [cell for cell in cells if cell["factor"] == UPPER]
    seeds = {factor: {cell["seed"] for cell in cells if cell["factor"] == factor}
             for factor in (LOWER, UPPER)}
    return {
        "G1_factor_live": bool(upper) and all(
            cell["decay_calls_count"] == CYCLES
            and cell["decay_factors"] == [UPPER]
            and cell["decay_rows_min"] > 0
            for cell in upper
        ),
        "G2_denominators": bool(cells) and all(
            cell["cycles"] == CYCLES and cell["theory_cycles"] > 0 for cell in cells
        ),
        "G3_cells_complete": len(cells) == 2 * len(SEEDS),
        "G4_seed_pairing": seeds[LOWER] == seeds[UPPER] == set(SEEDS),
        "G5_artifact_matches_parts": True,
    }


def label_for(cells: list[dict], gates: dict | None = None) -> str:
    if gates is None:
        gates = gates_for(cells)
    if not all(gates.values()):
        return "VOID"
    lower = [cell for cell in cells if cell["factor"] == LOWER]
    upper = [cell for cell in cells if cell["factor"] == UPPER]
    if lower and upper and all(cell["death_cycle"] < ALIVE for cell in lower) \
            and all(cell["death_cycle"] == ALIVE for cell in upper):
        return "PAIRED_BRACKET_CONFIRMED"
    return "PAIRED_BRACKET_NOT_CONFIRMED"


def predictions_for(cells: list[dict]) -> dict:
    lower = [cell for cell in cells if cell["factor"] == LOWER]
    upper = [cell for cell in cells if cell["factor"] == UPPER]
    return {
        "P1_lower_dead_all": bool(lower) and all(cell["death_cycle"] < ALIVE for cell in lower),
        "P2_upper_alive_all": bool(upper) and all(cell["death_cycle"] == ALIVE for cell in upper),
    }


def finish() -> dict:
    cells = cells_from_parts()
    gates = gates_for(cells)
    label = label_for(cells, gates)
    pairs = []
    for seed in SEEDS:
        lower = next(cell for cell in cells if cell["factor"] == LOWER and cell["seed"] == seed)
        upper = next(cell for cell in cells if cell["factor"] == UPPER and cell["seed"] == seed)
        pairs.append({
            "seed": seed,
            "lower_death": lower["death_cycle"],
            "upper_death": upper["death_cycle"],
            "lower_dead": lower["death_cycle"] < ALIVE,
            "upper_alive": upper["death_cycle"] == ALIVE,
        })
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": __import__("organica").__version__,
        "question": "Q050 paired edge check",
        "preregistration": PREREG.relative_to(ROOT).as_posix(),
        "protocol_section": "14",
        "world": WORLD,
        "arm": ARM,
        "factors": [LOWER, UPPER],
        "seeds": list(SEEDS),
        "cycles": CYCLES,
        "cells": cells,
        "pairs": pairs,
        "gates": gates,
        "predictions": predictions_for(cells),
        "label": label,
    }
    if artifact["predictions"]["P1_lower_dead_all"] and artifact["predictions"]["P2_upper_alive_all"]:
        artifact["prediction_paired_bracket"] = True
    else:
        artifact["prediction_paired_bracket"] = False
    problems = validate(artifact, cells)
    if problems:
        raise SystemExit("refusing to write: " + "; ".join(problems))
    ARTIFACT.write_text(json.dumps(artifact, indent=1) + "\n", encoding="utf-8")
    return artifact


def validate(artifact: dict, cells: list[dict] | None = None) -> list[str]:
    found: list[str] = []
    if cells is None:
        try:
            cells = cells_from_parts()
        except SystemExit as error:
            return [str(error)]
    gates = artifact.get("gates") or {}
    expected_gates = gates_for(cells)
    if gates != expected_gates:
        found.append("the artifact's gates do not match the committed parts")
    if artifact.get("gates", {}).get("G5_artifact_matches_parts"):
        def rows(source):
            return sorted(({key: cell.get(key) for key in CELL_KEYS} for cell in source),
                          key=lambda row: (row["seed"], row["factor"]))
        if rows(artifact.get("cells") or []) != rows(cells):
            found.append("the artifact's per-cell facts do not equal the parts")
    if artifact.get("label") not in BUCKETS:
        found.append("label %r is not one of the frozen buckets" % artifact.get("label"))
    if artifact.get("label") != label_for(cells, expected_gates):
        found.append("the artifact's label is not the one its cells imply")
    if artifact.get("predictions") != predictions_for(cells):
        found.append("the artifact's predictions do not match the committed parts")
    if artifact.get("seeds") != list(SEEDS):
        found.append("the artifact's seeds are not the pre-registered block")
    if artifact.get("factors") != [LOWER, UPPER]:
        found.append("the artifact's factors are not the paired edge")
    if artifact.get("cycles") != CYCLES:
        found.append("the artifact's cycle count is not %d" % CYCLES)
    return found


def render(artifact: dict) -> str:
    lines = [
        "# The paired 0.9924/0.9925 edge check — result",
        "",
        "Generated from `docs/decay_paired_bracket.json` by "
        "`python -m benchmarks.decay_paired_bracket --render`. Do not edit by hand.",
        "",
        "Protocol: `docs/DECAY-THRESHOLD-PREREGISTRATION.md` section 14. Both factors are "
        "measured on the same three seeds, world, arm and runner; the 0.9924 cells are the "
        "committed Q050 screen and section-13 edge cells.",
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "| Seed | 0.9924 death | 0.9925 death | Paired |",
        "| --- | --- | --- | --- |",
    ]
    for pair in artifact["pairs"]:
        lines.append("| %s | %s | %s | %s |"
                     % (pair["seed"], pair["lower_death"], pair["upper_death"],
                        "lower dead, upper alive" if pair["lower_dead"] and pair["upper_alive"]
                        else "not the predicted bracket"))
    lines += [
        "",
        "**Prediction (all three 0.9924 dead, all three 0.9925 alive):** %s."
        % ("held" if artifact["prediction_paired_bracket"] else "failed"),
        "",
        "## Gates",
        "",
        "| Gate | Result |",
        "| --- | --- |",
    ]
    for name, ok in artifact["gates"].items():
        lines.append("| %s | %s |" % (name, "pass" if ok else "FAIL"))
    lines += [
        "",
        "## Scope",
        "",
        "This is a paired robustness check requested after Q050, not a new threshold. It fixes "
        "the seed block, so the only difference between the two sides of the edge is the decay "
        "factor. The resolution remains 0.0001; survival is theory-layer presence, not theory "
        "identity; and no adaptation or capability task is scored. Q050 keeps its "
        "`NO_INTERIOR_SURVIVOR` label, and 0.9925 remains the first tested survivor.",
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
    parser.add_argument("--seed", type=int, action="append", default=None,
                        help="run one seed of the block (default: all three)")
    args = parser.parse_args(argv)
    if args.measure:
        seeds = tuple(args.seed or SEEDS)
        unknown = sorted(set(seeds) - set(SEEDS))
        if unknown:
            raise SystemExit("seed %r is not in the pre-registered block" % unknown)
        return measure(seeds)
    if args.finish:
        artifact = finish()
        print("%s: %s" % (artifact["label"],
                          ", ".join("%d: %s/%s" % (pair["seed"], pair["lower_death"],
                                                   pair["upper_death"])
                                    for pair in artifact["pairs"])))
        return 0
    if args.render:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        page = render(artifact)
        if "{" in page or "}" in page:
            raise SystemExit("the page contains a brace; refusing to write it")
        DOC.write_text(page, encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0

    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    problems = validate(artifact)
    text = PREREG.read_text(encoding="utf-8")
    if "## 14. Paired same-block check" not in text:
        problems.append("the protocol has no section 14")
    if "PAIRED_BRACKET_CONFIRMED" not in text:
        problems.append("the protocol does not name the paired-bracket label")
    if artifact["label"] not in DOC.read_text(encoding="utf-8"):
        problems.append("the page does not name the artifact's label")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("paired bracket: %s" % artifact["label"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
