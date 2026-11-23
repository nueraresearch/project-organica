"""Q052 amendment A2: a mass definition that the death cannot move, and a calibrated floor.

The first Q052 run returned `VOID` on its own control (`docs/q052_competition_census.json`):
the lattice control reproduced the committed census exactly, but its `mass_ratio` was 0.578
against the design's required 0.90. The cause is the definition. Edge mass summed *every*
retained hypothesis at each cycle, so the hypotheses pruned at death -- most plausibly the
competing ones -- sat inside the drop. A floor on that quantity tests the premise with a
measure the premise predicts will fall.

A2 changes two things and nothing else:

* **the mass** is the support mass of the pairs retained at the **last live cycle**, tracked
  through death. A cohort member that is gone at the death cycle counts as zero; a hypothesis
  that was never in the cohort is not counted at all. Pruning something outside the cohort
  therefore cannot move the ratio, which is the property the first definition lacked.
* **the floor** is calibrated on committed lattice data that this run does not judge
  (`docs/decay_competition/parts/0.9924_<seed>.json`, seeds 20302701-20302703) and fixed
  before the judged block runs.

The labels, their conditions and their precedence are unchanged, and the probed block is
fresh: seeds 20303001-20303003, disjoint from the threshold block, the twelve-seed replication,
the burst calibration and the A1 block. The lattice control keeps seed 20302701 because its
job is to reproduce the committed census, which is a specific trajectory.

This module is an amendment layer, not a second instrument: it calls
`competition_census.run_cell`, which holds the observer and the capture, and reimplements only
the census arithmetic. The A1 artifact and its `--check` are untouched.

    ./.venv/bin/python -m benchmarks.q052_amendment_a2 --calibrate
    ./.venv/bin/python -m benchmarks.q052_amendment_a2 --measure --seed 20303001
    ./.venv/bin/python -m benchmarks.q052_amendment_a2 --measure --family lattice_L1 --seed 20302701
    ./.venv/bin/python -m benchmarks.q052_amendment_a2 --finish
    ./.venv/bin/python -m benchmarks.q052_amendment_a2 --render
    ./.venv/bin/python -m benchmarks.q052_amendment_a2 --check
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

import organica
from benchmarks import competition_census as cc
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "q052_census_a2" / "parts"
ARTIFACT = ROOT / "docs" / "q052_competition_census_a2.json"
DOC = ROOT / "docs" / "Q052-COMPETITION-CENSUS-A2.md"
DESIGN = ROOT / "docs" / "Q052-FRAMING-DESIGN.md"

#: Calibration data: the committed lattice probe, which this run does not judge.
#: 20302701 is deliberately excluded -- it is the control's seed, and rule 19 forbids
#: computing a threshold from the cell it judges. The remaining cells are the same family and
#: factor as the control, which is the known-answer world the amendment asked for; the
#: consequence is stated in the artifact: this floor is a within-family consistency bound, not
#: an independent ceiling.
CALIBRATION_PARTS = ROOT / "docs" / "decay_competition" / "parts"
CALIBRATION_SEEDS = (20302702, 20302703)
CALIBRATION_MARGIN = 0.05

#: Fixed before the judged block ran from `--calibrate`, and derived again here from the committed
#: calibration data so `validate` recomputes it instead of trusting a typed number. The value is
#: the lowest cohort ratio in the calibration set minus the margin.
FLOOR = None

SEEDS = (20303001, 20303002, 20303003)
MASS_DEFINITION = ("support mass of the pairs retained at the last live cycle, tracked through "
                   "death; a cohort member that is gone counts as zero and a hypothesis outside "
                   "the cohort is never counted")
CONTROL = cc.CONTROL
PROBED = cc.PROBED
BUCKETS = cc.BUCKETS


def _rows(row: dict) -> list[dict]:
    return row["retained_hypotheses"]


def cohort_census(before: dict, at: dict) -> dict:
    """The amended census: the cohort's own mass, plus the pair and competition counts."""
    cohort = {(h["subject"], h["expectation"]): int(h["support_count"])
              for h in _rows(before)}
    after = {(h["subject"], h["expectation"]): int(h["support_count"])
             for h in _rows(at)}
    mass_before = sum(cohort.values())
    mass_after = sum(after.get(key, 0) for key in cohort)
    pairs = Counter(h["subject"] for h in _rows(at))
    competing = Counter(h["subject"] for h in _rows(at)
                        if h["expectation"] != "high_structural_significance")
    top = (max(before["theories"], key=lambda t: t["support_count"])
           if before["theories"] else None)
    return {
        "theories_at_last_live": len(before["theories"]),
        "theories_at_death": len(at["theories"]),
        "top_theory": None if top is None else {
            "subject": top["subject"],
            "support_count": top["support_count"],
            "competing": [{"expectation": h["expectation"],
                           "support_count": h["support_count"]}
                          for h in top["hypotheses"]],
        },
        "cohort_size": len(cohort),
        "cohort_survived": sum(1 for key in cohort if key in after),
        "edge_mass_at_last_live": mass_before,
        "edge_mass_at_death": mass_after,
        "mass_ratio": None if not mass_before else round(mass_after / mass_before, 6),
        "subjects_with_pairs_at_death": {s: c for s, c in pairs.items() if c >= 2},
        "subjects_with_competing_at_death": {s: c for s, c in competing.items() if c >= 2},
        "subjects_with_competing_at_last_live": {
            s: c for s, c in Counter(
                h["subject"] for h in _rows(before)
                if h["expectation"] != "high_structural_significance").items() if c >= 2},
        "retained_at_death": _rows(at),
    }


def cells_for(part: dict) -> list[dict]:
    """One dying cell per live-to-dead transition in the capture."""
    window = {int(cycle): row for cycle, row in part["window"].items()}
    cells = []
    for cycle in sorted(window):
        previous = cycle - 1
        if previous not in window:
            continue
        if not window[previous]["theories"] or window[cycle]["theories"]:
            continue
        cells.append({"seed": part["seed"], "family": part["family"],
                      "factor": part["factor"],
                      "last_live_cycle": previous, "death_cycle": cycle,
                      **cohort_census(window[previous], window[cycle])})
    return cells


def control_check(part: dict) -> dict:
    window = {int(cycle): row for cycle, row in part["window"].items()}
    last_live = max(c for c, row in window.items() if row["theories"])
    death = last_live + 1
    census = cohort_census(window[last_live], window[death])
    top = census["top_theory"] or {}
    supports = [item["support_count"] for item in top.get("competing", [])]
    reproduced = (last_live == CONTROL["last_live_cycle"]
                  and death == CONTROL["death_cycle"]
                  and top.get("subject") == CONTROL["subject"]
                  and top.get("support_count") == CONTROL["support_count"]
                  and supports == CONTROL["supports"])
    return {**census, "reproduced": reproduced,
            "mass_floor_met": census["mass_ratio"] is not None
            and FLOOR is not None and census["mass_ratio"] >= FLOOR}


def calibration() -> dict:
    """Cohort ratios on committed lattice cells that this run does not judge."""
    ratios = {}
    for seed in CALIBRATION_SEEDS:
        path = CALIBRATION_PARTS / ("0.9924_%d.json" % seed)
        part = json.loads(path.read_text(encoding="utf-8"))
        window = {int(cycle): row for cycle, row in part["window"].items()}
        last_live = max(c for c, row in window.items() if row["theories"])
        ratios[str(seed)] = cohort_census(window[last_live],
                                          window[last_live + 1])["mass_ratio"]
    known = [value for value in ratios.values() if value is not None]
    floor = round(min(known) - CALIBRATION_MARGIN, 4) if known else None
    return {"source": CALIBRATION_PARTS.relative_to(ROOT).as_posix(),
            "seeds": list(CALIBRATION_SEEDS), "ratios": ratios,
            "margin": CALIBRATION_MARGIN, "floor": floor}


FLOOR = calibration()["floor"]


def classify(cells: list[dict], control: dict, probed_transitions: dict) -> tuple[str, dict]:
    floor = FLOOR if FLOOR is not None else 0.0
    fired = {
        "control_reproduced": bool(control["reproduced"]),
        "control_mass_floor": bool(control["mass_floor_met"]),
        "dying_cells": len(cells),
        "intermittent": any(count >= 2 for count in probed_transitions.values()),
        "support_collapse": any(
            cell["mass_ratio"] is not None and cell["mass_ratio"] < floor
            for cell in cells),
        "competition_present": any(cell["subjects_with_competing_at_death"] for cell in cells),
        "same": bool(cells) and all(
            not cell["subjects_with_competing_at_death"]
            and len(cell["subjects_with_pairs_at_death"]) >= 2
            and any(count >= 2 for count in cell["subjects_with_competing_at_last_live"].values())
            and cell["mass_ratio"] is not None and cell["mass_ratio"] >= floor
            for cell in cells),
    }
    if not control["reproduced"] or not control["mass_floor_met"] or len(cells) < 2:
        return "VOID", fired
    if fired["intermittent"]:
        return "DIFFERENT_INTERMITTENT", fired
    if fired["support_collapse"]:
        return "DIFFERENT_SUPPORT_COLLAPSE", fired
    if fired["competition_present"]:
        return "DIFFERENT_COMPETITION_PRESENT", fired
    if fired["same"]:
        return "SAME_COMPETITION_LOSS", fired
    return "VOID", fired


def part_path(family: str, seed: int) -> Path:
    return PARTS / ("%s_%d.json" % (family, seed))


def measure(seeds, family: str = PROBED["family"]) -> int:
    factor = CONTROL["factor"] if family == CONTROL["family"] else PROBED["factor"]
    for seed in seeds:
        path = part_path(family, seed)
        if path.exists():
            print("cached", path.name, flush=True)
            continue
        part = cc.run_cell(family, factor, seed, cc.events_for(family, seed))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(engine_stamp.stamp(part), indent=1) + "\n",
                        encoding="utf-8")
        print("%s %s seed %d live %d/%d cycles, transitions %s"
              % (family, factor, seed, part["facts"]["live_cycles"], cc.CYCLES,
                 ["%s@%d" % (step["kind"], step["cycle"])
                  for step in cc.transitions(part)]), flush=True)
    return 0


def load_part(family: str, seed: int) -> dict:
    path = part_path(family, seed)
    if not path.exists():
        raise SystemExit("missing part %s" % path.name)
    part = json.loads(path.read_text(encoding="utf-8"))
    if part["family"] != family or part["seed"] != seed:
        raise SystemExit("part %s does not hold %s on seed %d" % (path.name, family, seed))
    return part


def finish() -> dict:
    control = control_check(load_part(CONTROL["family"], CONTROL["seed"]))
    cells: list[dict] = []
    per_seed: dict[str, list] = {}
    transitions: dict[str, int] = {}
    for seed in SEEDS:
        part = load_part(PROBED["family"], seed)
        steps = cc.transitions(part)
        per_seed[str(seed)] = steps
        transitions[str(seed)] = sum(1 for step in steps if step["kind"] == "LIVE_TO_DEAD")
        cells.extend(cells_for(part))
    label, fired = classify(cells, control, transitions)
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": organica.__version__,
        "question": "Q052 framing -- is burst_L1's late collapse competition loss?",
        "amendment": "A2",
        "amends": "docs/q052_competition_census.json",
        "design": DESIGN.relative_to(ROOT).as_posix(),
        "mass_definition": MASS_DEFINITION,
        "floor": FLOOR,
        "calibration": calibration(),
        "calibration_note": ("Calibrated on committed lattice cells at the control's own factor "
                             "and family, excluding the control's seed. The floor is therefore "
                             "a within-family consistency bound -- the minimum mass ratio the "
                             "known-answer world is observed to give -- and not an independent "
                             "ceiling. The collapse test is a single boundary at that floor: A1's "
                             "extra 0.05 margin is removed, because a line 0.05 below the floor "
                             "would sit below the known world's own ratio."),
        "cycles": cc.CYCLES,
        "window": [1, cc.CYCLES],
        "arm": cc.ARM,
        "control": {**{k: CONTROL[k] for k in CONTROL}, **control},
        "probed": {"family": PROBED["family"], "factor": PROBED["factor"],
                   "seeds": list(SEEDS), "live_to_dead_transitions": transitions},
        "cells": cells,
        "transitions": per_seed,
        "fired": fired,
        "label": label,
        "scope": ("One family, one factor, three fresh seeds. The classification decides Q053's "
                  "scope; it is not a capability result and scores no prediction task."),
    }
    problems = validate(artifact)
    if problems:
        raise SystemExit("refusing to write: " + "; ".join(problems))
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1) + "\n",
                        encoding="utf-8")
    return artifact


def validate(artifact: dict | None = None) -> list[str]:
    found: list[str] = []
    if artifact is None:
        if not ARTIFACT.exists():
            return ["the amendment artifact does not exist"]
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if artifact.get("amendment") != "A2":
        found.append("the artifact does not record amendment A2")
    if artifact.get("mass_definition") != MASS_DEFINITION:
        found.append("the artifact does not carry the amended mass definition")
    if FLOOR is None or artifact.get("floor") != FLOOR:
        found.append("the artifact's floor is not the calibrated one")
    if artifact.get("calibration", {}).get("floor") != artifact.get("floor"):
        found.append("the recorded calibration does not yield the recorded floor")
    if artifact.get("label") not in BUCKETS:
        found.append("label %r is not one of the frozen buckets" % artifact.get("label"))
    if artifact.get("probed", {}).get("seeds") != list(SEEDS):
        found.append("the seeds are not the fresh A2 block")
    if artifact.get("probed", {}).get("factor") != PROBED["factor"]:
        found.append("the probed factor is not the one chosen before the run")
    for cell in artifact.get("cells", []):
        for field in ("cohort_size", "cohort_survived", "edge_mass_at_last_live",
                      "edge_mass_at_death", "mass_ratio", "subjects_with_pairs_at_death",
                      "subjects_with_competing_at_death"):
            if field not in cell:
                found.append("cell %s/%s is missing %s"
                             % (cell.get("family"), cell.get("seed"), field))
    implied, _ = classify(artifact.get("cells", []), artifact.get("control", {}),
                          artifact.get("probed", {}).get("live_to_dead_transitions", {}))
    if artifact.get("label") != implied:
        found.append("the label is not the one its cells and control imply")
    return found


def render(artifact: dict) -> str:
    control = artifact["control"]
    calibration = artifact["calibration"]
    lines = [
        "# Q052 census, amendment A2: a mass the death cannot move",
        "",
        "Generated from `docs/q052_competition_census_a2.json` by "
        "`python -m benchmarks.q052_amendment_a2 --render`. Do not edit by hand.",
        "",
        "The first run is `docs/q052_competition_census.json` and stands as it was recorded: "
        "`VOID`, because its control's mass ratio was below its floor. This page is the amended "
        "run, on a fresh probed block.",
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "## The two changes",
        "",
        "| Field | A1 | A2 |",
        "| --- | --- | --- |",
        "| mass | every retained hypothesis, each cycle | the pairs retained at the last live "
        "cycle, tracked to death |",
        "| floor | 0.90, fixed in the design | %s, calibrated below |" % artifact["floor"],
        "| probed seeds | 20302901-20302903 | %s |"
        % ", ".join(str(s) for s in artifact["probed"]["seeds"]),
        "",
        "## The calibration (committed data, not judged by this run)",
        "",
        "Source: `%s`, seeds %s." % (calibration["source"],
                                     ", ".join(str(s) for s in calibration["seeds"])),
        "",
        "| Seed | Cohort mass at last live | At death | Ratio |",
        "| --- | --- | --- | --- |",
    ]
    for seed, ratio in calibration["ratios"].items():
        lines.append("| %s | | | %s |" % (seed, ratio))
    lines += [
        "",
        "Floor = lowest calibration ratio minus the margin %s = **%s**."
        % (calibration["margin"], calibration["floor"]),
        "",
        "## The control, under the amended mass",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| reproduced the committed census | %s |" % control["reproduced"],
        "| cohort size at last live | %s |" % control["cohort_size"],
        "| of which survived to death | %s |" % control["cohort_survived"],
        "| mass at last live | %s |" % control["edge_mass_at_last_live"],
        "| mass at death | %s |" % control["edge_mass_at_death"],
        "| ratio | %s |" % control["mass_ratio"],
        "| floor met | %s |" % control["mass_floor_met"],
        "",
        "## The probed arm",
        "",
        "`%s` at `%s`, seeds %s. Live-to-dead transitions: %s."
        % (artifact["probed"]["family"], artifact["probed"]["factor"],
           ", ".join(str(s) for s in artifact["probed"]["seeds"]),
           ", ".join("%s: %s" % (seed, count)
                     for seed, count in artifact["probed"]["live_to_dead_transitions"].items())),
        "",
        "| Seed | Last live | Death | Top subject | Support | Cohort | Survived | Pairs at death "
        "| Competing at death | Mass ratio |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["cells"]:
        top = cell["top_theory"] or {}
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            cell["seed"], cell["last_live_cycle"], cell["death_cycle"],
            top.get("subject"), top.get("support_count"), cell["cohort_size"],
            cell["cohort_survived"], len(cell["subjects_with_pairs_at_death"]),
            len(cell["subjects_with_competing_at_death"]), cell["mass_ratio"]))
    lines += [
        "",
        "## Which conditions fired",
        "",
        "| Condition | Fired |",
        "| --- | --- |",
    ]
    for name, value in artifact["fired"].items():
        lines.append("| %s | %s |" % (name, value))
    lines += [
        "",
        "## Scope",
        "",
        artifact["scope"],
        "The supports are temporal transition counts, not observations, and survival is "
        "theory-layer presence, not theory identity. A label here decides which families Q053 "
        "may test; it says nothing about capability.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    global FLOOR
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--calibrate", action="store_true")
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--render", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--family", choices=(CONTROL["family"], PROBED["family"]))
    parser.add_argument("--seed", type=int, action="append", default=None)
    args = parser.parse_args(argv)
    calibration_record = calibration()
    if FLOOR is None:
        FLOOR = calibration_record["floor"]
    if args.calibrate:
        print(json.dumps(calibration_record, indent=1))
        return 0
    if args.measure:
        family = args.family or PROBED["family"]
        allowed = [CONTROL["seed"]] if family == CONTROL["family"] else list(SEEDS)
        seeds = tuple(args.seed or allowed)
        unknown = sorted(set(seeds) - set(allowed))
        if unknown:
            raise SystemExit("seed %r is not in the A2 block" % unknown)
        return measure(seeds, family)
    if args.finish:
        artifact = finish()
        print("%s: %s" % (artifact["label"],
                          ", ".join("%s %d dying cell(s)" % (s, n)
                                    for s, n in
                                    artifact["probed"]["live_to_dead_transitions"].items())))
        return 0
    if args.render:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        page = render(artifact)
        if "{" in page or "}" in page:
            raise SystemExit("the page contains a brace; refusing to write it")
        DOC.write_text(page, encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0
    problems = validate()
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("amendment A2 census: %s"
          % json.loads(ARTIFACT.read_text(encoding="utf-8"))["label"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
