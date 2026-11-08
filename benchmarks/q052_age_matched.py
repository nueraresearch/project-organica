"""Q052 addendum A2a: does the burst cohort-mass gap survive a death-age match?

Amendment A2 classified `burst_L1` as `DIFFERENT_SUPPORT_COLLAPSE` on cohort mass, and recorded
one confound against it: the burst cells die at cycles 131-134 and the lattice control at 300, so
a lower one-step mass retention might belong to *where the death lands* rather than to a
different mechanism. This addendum measures the two comparisons that can separate them, on the
known world, before any of it is read:

1. **Live transitions at the burst ages.** The lattice control at 0.9924 is alive at 131 and 134,
   so its (130 -> 131) and (133 -> 134) transitions carry no death. They measure what one live
   cycle does to the cohort's mass at those ages, which is what an age effect would have to move.
2. **A lattice death at the burst ages.** If some lattice decay factor dies within the match
   tolerance of 131-134, its death transition is the family-matched, age-matched comparator: the
   same world, the same death mechanism, a different age.

**Reading rule, fixed before the cells were read.** Tolerance 10 cycles; band 0.10 of mass ratio.

* `AGE_MATCH_UNAVAILABLE` -- no lattice death falls within 10 cycles of a burst death. The death
  comparison is not constructible with the factors run, and only the live comparison is reported.
* `AGE_EXPLAINS_THE_GAP` -- a matched lattice death's cohort ratio is within 0.10 of the burst
  ratio it is matched to. The gap is consistent with death age, and A2's label stands as a
  measurement while its *reason* is withdrawn.
* `AGE_DOES_NOT_EXPLAIN_THE_GAP` -- a matched lattice death's ratio differs by more than 0.10.
  Death age alone does not produce the burst ratio; the difference is family-specific.

This module reuses the instrument (`competition_census.run_cell`) and the amended arithmetic
(`q052_amendment_a2.cohort_census`). It writes its own parts, artifact and page; the A1 and A2
records are untouched.

    ./.venv/bin/python -m benchmarks.q052_age_matched --measure --factor 0.9924 --capture 131 134
    ./.venv/bin/python -m benchmarks.q052_age_matched --measure --factor 0.95
    ./.venv/bin/python -m benchmarks.q052_age_matched --measure --factor 0.97
    ./.venv/bin/python -m benchmarks.q052_age_matched --finish
    ./.venv/bin/python -m benchmarks.q052_age_matched --render
    ./.venv/bin/python -m benchmarks.q052_age_matched --check
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import organica
from benchmarks import competition_census as cc
from benchmarks import engine_stamp
from benchmarks import q052_amendment_a2 as a2

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "q052_census_age" / "parts"
ARTIFACT = ROOT / "docs" / "q052_age_matched.json"
DOC = ROOT / "docs" / "Q052-AGE-MATCHED.md"
DESIGN = ROOT / "docs" / "Q052-FRAMING-DESIGN.md"

CONTROL = cc.CONTROL
LIVE_CYCLES = (131, 134)
#: 0.95, 0.97, 0.98, 0.985 and 0.99 were added to *find* a lattice death near the burst ages.
#: The tolerance and the band were fixed before any cell ran and were not changed; adding cells
#: to search for a matching death is measurement, not a criterion change, and it is disclosed in
#: the artifact.
LATTICE_FACTORS = (0.9924, 0.95, 0.97, 0.98, 0.985, 0.99)
MATCH_TOLERANCE = 10
MATCH_BAND = 0.10
BURST_DEATHS = ((20303001, 134), (20303002, 131), (20303003, 131))

READING_RULE = (
    "Tolerance %d cycles; band %.2f of cohort mass ratio. AGE_MATCH_UNAVAILABLE when no lattice "
    "death falls within the tolerance of a burst death; AGE_EXPLAINS_THE_GAP when a matched "
    "lattice death's ratio is within the band; AGE_DOES_NOT_EXPLAIN_THE_GAP when it is not."
    % (MATCH_TOLERANCE, MATCH_BAND))


def part_path(family: str, factor: float, seed: int) -> Path:
    return PARTS / ("%s_%s_%d.json" % (family, factor, seed))


def measure(factor: float, seed: int = CONTROL["seed"],
            capture: tuple[int, ...] = ()) -> int:
    path = part_path(CONTROL["family"], factor, seed)
    if path.exists():
        print("cached", path.name, flush=True)
        return 0
    part = cc.run_cell(CONTROL["family"], factor, seed,
                       cc.events_for(CONTROL["family"], seed), capture=capture)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(engine_stamp.stamp(part), indent=1) + "\n", encoding="utf-8")
    steps = cc.transitions(part)
    print("lattice %s seed %d live %d/%d, transitions %s, captured %s"
          % (factor, seed, part["facts"]["live_cycles"], cc.CYCLES,
             ["%s@%d" % (step["kind"], step["cycle"]) for step in steps],
             part["captured_cycles"]), flush=True)
    return 0


def load_part(factor: float, seed: int = CONTROL["seed"]) -> dict:
    path = part_path(CONTROL["family"], factor, seed)
    if not path.exists():
        raise SystemExit("missing part %s" % path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def _window(part: dict) -> dict[int, dict]:
    return {int(cycle): row for cycle, row in part["window"].items()}


def live_cells(part: dict) -> list[dict]:
    window = _window(part)
    cells = []
    for cycle in LIVE_CYCLES:
        if cycle - 1 not in window or cycle not in window:
            continue
        census = a2.cohort_census(window[cycle - 1], window[cycle])
        cells.append({"cycle": cycle, "theories_at_before": census["theories_at_last_live"],
                      "theories_at_cycle": census["theories_at_death"],
                      **{k: census[k] for k in ("cohort_size", "cohort_survived",
                                                "edge_mass_at_last_live", "edge_mass_at_death",
                                                "mass_ratio")}})
    return cells


def death_cells(part: dict) -> list[dict]:
    window = _window(part)
    cells = []
    for step in cc.transitions(part):
        if step["kind"] != "LIVE_TO_DEAD":
            continue
        cycle = step["cycle"]
        census = a2.cohort_census(window[cycle - 1], window[cycle])
        cells.append({"death_cycle": cycle, "factor": part["factor"],
                      **{k: census[k] for k in ("cohort_size", "cohort_survived",
                                                "edge_mass_at_last_live", "edge_mass_at_death",
                                                "mass_ratio")}})
    return cells


def burst_cells() -> list[dict]:
    cells = []
    for seed, death in BURST_DEATHS:
        part = a2.load_part(a2.PROBED["family"], seed)
        found = [cell for cell in a2.cells_for(part) if cell["death_cycle"] == death]
        if not found:
            raise SystemExit("burst part %d has no death at cycle %d" % (seed, death))
        cell = found[0]
        cells.append({"seed": seed, "death_cycle": death,
                      "cohort_size": cell["cohort_size"],
                      "cohort_survived": cell["cohort_survived"],
                      "edge_mass_at_last_live": cell["edge_mass_at_last_live"],
                      "edge_mass_at_death": cell["edge_mass_at_death"],
                      "mass_ratio": cell["mass_ratio"]})
    return cells


def reading(burst_ratio: float, matched: dict | None) -> tuple[str, float | None]:
    if matched is None or matched.get("mass_ratio") is None:
        return "AGE_MATCH_UNAVAILABLE", None
    difference = round(matched["mass_ratio"] - burst_ratio, 6)
    if abs(difference) <= MATCH_BAND:
        return "AGE_EXPLAINS_THE_GAP", difference
    return "AGE_DOES_NOT_EXPLAIN_THE_GAP", difference


def bracket(deaths: list[dict], cycle: int) -> dict | None:
    """Interpolate the lattice death ratio at `cycle` from the deaths either side of it."""
    below = sorted((d for d in deaths if d["death_cycle"] <= cycle),
                   key=lambda d: d["death_cycle"])
    above = sorted((d for d in deaths if d["death_cycle"] >= cycle),
                   key=lambda d: d["death_cycle"])
    if not below or not above:
        return None
    low, high = below[-1], above[0]
    if low["mass_ratio"] is None or high["mass_ratio"] is None:
        return None
    span = high["death_cycle"] - low["death_cycle"]
    if span == 0:
        estimate = low["mass_ratio"]
    else:
        weight = (cycle - low["death_cycle"]) / span
        estimate = low["mass_ratio"] + weight * (high["mass_ratio"] - low["mass_ratio"])
    return {"estimate": round(estimate, 6), "below": low["death_cycle"],
            "above": high["death_cycle"]}


def finish() -> dict:
    lattice = {}
    for factor in LATTICE_FACTORS:
        if part_path(CONTROL["family"], factor, CONTROL["seed"]).exists():
            lattice[str(factor)] = load_part(factor)
    if not lattice:
        raise SystemExit("no lattice part has been measured")
    live = live_cells(lattice[str(CONTROL["factor"])])
    deaths = []
    for factor, part in lattice.items():
        deaths.extend(death_cells(part))
    burst = burst_cells()

    matches = []
    for cell in burst:
        nearest = min(deaths, key=lambda d: abs(d["death_cycle"] - cell["death_cycle"]),
                      default=None)
        distance = None if nearest is None else abs(nearest["death_cycle"] - cell["death_cycle"])
        matched = nearest if distance is not None and distance <= MATCH_TOLERANCE else None
        label, difference = reading(cell["mass_ratio"], matched)
        matches.append({"burst_seed": cell["seed"], "burst_death": cell["death_cycle"],
                        "burst_ratio": cell["mass_ratio"],
                        "nearest_lattice_death": None if nearest is None else nearest["death_cycle"],
                        "nearest_lattice_factor": None if nearest is None else nearest["factor"],
                        "nearest_lattice_ratio": None if nearest is None else nearest["mass_ratio"],
                        "distance": distance,
                        "lattice_ratio": None if matched is None else matched["mass_ratio"],
                        "difference": difference, "label": label})
    trend = sorted(({"death_cycle": d["death_cycle"], "factor": d["factor"],
                     "mass_ratio": d["mass_ratio"]} for d in deaths),
                   key=lambda d: d["death_cycle"])
    measured = [d["mass_ratio"] for d in trend if d["mass_ratio"] is not None]
    spread = round(max(measured) - min(measured), 6) if measured else None
    bracketed = []
    for cell in burst:
        estimate = bracket(deaths, cell["death_cycle"])
        if estimate is None:
            bracketed.append({"burst_seed": cell["seed"], "burst_death": cell["death_cycle"],
                              "estimate": None, "difference": None, "beyond_band": None})
            continue
        difference = round(cell["mass_ratio"] - estimate["estimate"], 6)
        bracketed.append({"burst_seed": cell["seed"], "burst_death": cell["death_cycle"],
                          "estimate": estimate["estimate"], "below": estimate["below"],
                          "above": estimate["above"], "difference": difference,
                          "beyond_band": abs(difference) > MATCH_BAND})
    labels = {match["label"] for match in matches}
    label = ("AGE_MATCH_UNAVAILABLE" if "AGE_MATCH_UNAVAILABLE" in labels
             else "AGE_DOES_NOT_EXPLAIN_THE_GAP" if "AGE_DOES_NOT_EXPLAIN_THE_GAP" in labels
             else "AGE_EXPLAINS_THE_GAP")
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": organica.__version__,
        "question": ("does the burst cohort-mass gap survive a lattice death at the same age?"),
        "amendment": "A2a",
        "amends": ["docs/q052_competition_census.json",
                   "docs/q052_competition_census_a2.json"],
        "design": DESIGN.relative_to(ROOT).as_posix(),
        "reading_rule": READING_RULE,
        "tolerance": MATCH_TOLERANCE,
        "band": MATCH_BAND,
        "factors_run": sorted(float(factor) for factor in lattice),
        "factor_addition": (
            "The first three factors (0.9924, 0.95, 0.97) put the lattice deaths at 300, 39 and 69, "
            "so no death fell inside the tolerance of 131-134. Three more factors were run to "
            "search for a death near those ages. The tolerance of %d cycles and the band of %.2f "
            "were fixed before any cell and were not changed." % (MATCH_TOLERANCE, MATCH_BAND)),
        "live_cycles": list(LIVE_CYCLES),
        "lattice_live": live,
        "lattice_deaths": deaths,
        "burst": burst,
        "matches": matches,
        "age_trend": trend,
        "age_spread": spread,
        "age_flat": spread is not None and spread <= MATCH_BAND,
        "bracketed": bracketed,
        "bracketed_note": (
            "Recorded after the exact match was found unavailable. It interpolates the lattice "
            "death ratio at the burst death age from the deaths either side, uses the same band "
            "of %.2f, and changes no label." % MATCH_BAND),
        "label": label,
        "scope": ("One world family, one instrument, four cells. The live comparison is not a "
                  "death: it shows what a live cycle does to the cohort at those ages, while the "
                  "death comparison needs a lattice factor that dies there."),
        "no_new_engine": True,
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
            return ["the age-matched artifact does not exist"]
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if artifact.get("amendment") != "A2a":
        found.append("the artifact does not record addendum A2a")
    if artifact.get("reading_rule") != READING_RULE:
        found.append("the artifact does not carry the pre-committed reading rule")
    if artifact.get("tolerance") != MATCH_TOLERANCE or artifact.get("band") != MATCH_BAND:
        found.append("the artifact's tolerance or band is not the committed one")
    if len(artifact.get("lattice_live", [])) != len(LIVE_CYCLES):
        found.append("a requested live cycle was not captured")
    for cell in artifact.get("lattice_live", []):
        if cell["theories_at_before"] == 0:
            found.append("live cycle %s was not live" % cell["cycle"])
    for cell in artifact.get("burst", []):
        if cell["mass_ratio"] is None:
            found.append("a burst cell has no mass ratio")
    trend = artifact.get("age_trend", [])
    if [cell["death_cycle"] for cell in trend] != sorted(cell["death_cycle"] for cell in trend):
        found.append("the age trend is not ordered")
    if trend:
        measured = [cell["mass_ratio"] for cell in trend if cell["mass_ratio"] is not None]
        if artifact.get("age_spread") != round(max(measured) - min(measured), 6):
            found.append("the recorded age spread is not the one the trend gives")
    if len(artifact.get("bracketed", [])) != len(artifact.get("burst", [])):
        found.append("a burst cell has no bracketed estimate")
    implied = ("AGE_MATCH_UNAVAILABLE"
               if any(m["label"] == "AGE_MATCH_UNAVAILABLE" for m in artifact.get("matches", []))
               else "AGE_DOES_NOT_EXPLAIN_THE_GAP"
               if any(m["label"] == "AGE_DOES_NOT_EXPLAIN_THE_GAP"
                      for m in artifact.get("matches", []))
               else "AGE_EXPLAINS_THE_GAP")
    if artifact.get("label") != implied:
        found.append("the label is not the one its matches imply")
    return found


def render(artifact: dict) -> str:
    lines = [
        "# Q052 addendum A2a: the same mass, at the same age",
        "",
        "Generated from `docs/q052_age_matched.json` by "
        "`python -m benchmarks.q052_age_matched --render`. Do not edit by hand.",
        "",
        "A2 classified `burst_L1` as `DIFFERENT_SUPPORT_COLLAPSE` and recorded one confound: the "
        "burst cells die at 131-134 and the control at 300, so the mass gap might belong to the "
        "death's age. This page measures the two comparisons that can separate them.",
        "",
        "**Reading rule, fixed before the cells were read.** %s" % artifact["reading_rule"],
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "## What a live cycle does at those ages",
        "",
        "The lattice control is alive at cycles %s, so these transitions carry no death. They "
        "measure how much cohort mass one live cycle costs at those ages, which is what an age "
        "effect would have to move." % ", ".join(str(c) for c in artifact["live_cycles"]),
        "",
        "| Cycle | Theories before -> at | Cohort | Survived | Mass before -> after | Ratio |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["lattice_live"]:
        lines.append("| %s | %s -> %s | %s | %s | %s -> %s | %s |" % (
            cell["cycle"], cell["theories_at_before"], cell["theories_at_cycle"],
            cell["cohort_size"], cell["cohort_survived"], cell["edge_mass_at_last_live"],
            cell["edge_mass_at_death"], cell["mass_ratio"]))
    lines += [
        "",
        "## The burst deaths under test",
        "",
        "| Seed | Death | Cohort | Survived | Mass before -> after | Ratio |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["burst"]:
        lines.append("| %s | %s | %s | %s | %s -> %s | %s |" % (
            cell["seed"], cell["death_cycle"], cell["cohort_size"], cell["cohort_survived"],
            cell["edge_mass_at_last_live"], cell["edge_mass_at_death"], cell["mass_ratio"]))
    lines += [
        "",
        "## The lattice deaths, and the age match",
        "",
        "| Factor | Death | Cohort | Survived | Mass before -> after | Ratio |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["lattice_deaths"]:
        lines.append("| %s | %s | %s | %s | %s -> %s | %s |" % (
            cell["factor"], cell["death_cycle"], cell["cohort_size"], cell["cohort_survived"],
            cell["edge_mass_at_last_live"], cell["edge_mass_at_death"], cell["mass_ratio"]))
    lines += [
        "",
        "| Burst seed | Burst death | Burst ratio | Nearest lattice death | Distance | Nearest "
        "ratio | Matched ratio | Difference | Label |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for match in artifact["matches"]:
        lines.append("| %s | %s | %s | %s (%s) | %s | %s | %s | %s | %s |" % (
            match["burst_seed"], match["burst_death"], match["burst_ratio"],
            match["nearest_lattice_death"], match["nearest_lattice_factor"],
            match["distance"], match["nearest_lattice_ratio"], match["lattice_ratio"],
            match["difference"], match["label"]))
    lines += [
        "",
        "## Does the ratio depend on the age of the death?",
        "",
        "| Death cycle | Factor | Cohort mass ratio |",
        "| --- | --- | --- |",
    ]
    for cell in artifact["age_trend"]:
        lines.append("| %s | %s | %s |" % (cell["death_cycle"], cell["factor"],
                                           cell["mass_ratio"]))
    lines += [
        "",
        "Spread across the lattice deaths: **%s**, so the age trend is %s against the band of "
        "%s." % (artifact["age_spread"],
                 "flat" if artifact["age_flat"] else "not flat", artifact["band"]),
        "",
        artifact["bracketed_note"],
        "",
        "| Burst seed | Burst death | Burst ratio | Bracketed lattice ratio | Difference | "
        "Beyond the band |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["bracketed"]:
        lines.append("| %s | %s | %s | %s (from %s and %s) | %s | %s |" % (
            cell["burst_seed"], cell["burst_death"],
            next(b["mass_ratio"] for b in artifact["burst"] if b["seed"] == cell["burst_seed"]),
            cell["estimate"], cell["below"], cell["above"], cell["difference"],
            cell["beyond_band"]))
    lines += [
        "",
        "## What this decides, and what it cannot",
        "",
        artifact["scope"],
        "",
        "A lattice death inside the tolerance is a family-matched, age-matched comparator; its "
        "absence means the death comparison is not constructible with the factors run, and the "
        "live comparison is the weaker statement that the measure itself does not drift with age.",
        "",
        "Factors run: %s." % ", ".join(str(f) for f in artifact["factors_run"]),
        "",
        artifact["factor_addition"],
        "",
        "This addendum changes no label. A2's `DIFFERENT_SUPPORT_COLLAPSE` stands as the "
        "classification the amended conditions imply; this record only decides whether the "
        "recorded *confound* explains the gap it was charged with.",
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
    parser.add_argument("--factor", type=float)
    parser.add_argument("--seed", type=int, default=CONTROL["seed"])
    parser.add_argument("--capture", type=int, nargs="*", default=())
    args = parser.parse_args(argv)
    if args.measure:
        if args.factor is None:
            raise SystemExit("--measure needs --factor")
        if args.factor not in LATTICE_FACTORS:
            raise SystemExit("factor %r is not one of %r" % (args.factor, LATTICE_FACTORS))
        return measure(args.factor, args.seed, tuple(args.capture))
    if args.finish:
        artifact = finish()
        print(artifact["label"])
        for match in artifact["matches"]:
            print("burst %s@%s ratio %s vs lattice %s@%s ratio %s -> %s"
                  % (match["burst_seed"], match["burst_death"], match["burst_ratio"],
                     match["nearest_lattice_factor"], match["nearest_lattice_death"],
                     match["lattice_ratio"], match["label"]))
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
    print("age-matched addendum: %s"
          % json.loads(ARTIFACT.read_text(encoding="utf-8"))["label"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
