"""The frozen Q053 mechanism preregistration: one mechanism, one block, one reading.

The record is data (`docs/q053_mechanism_prereg.json`) rendered to
`docs/Q053-MECHANISM-PREREGISTRATION.md`. The scorer in this module is the only analysis path:
it takes the run artifact, applies the gates, then the criteria in their frozen order, and returns
one of the decision table's labels. Nothing here runs a cell, and nothing here changes the engine.

    ./.venv/bin/python -m benchmarks.q053_mechanism_prereg --check
    ./.venv/bin/python -m benchmarks.q053_mechanism_prereg --render
    ./.venv/bin/python -m benchmarks.q053_mechanism_prereg --analyze docs/q053_mechanism_run.json
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs" / "q053_mechanism_prereg.json"
DOC = ROOT / "docs" / "Q053-MECHANISM-PREREGISTRATION.md"

VERDICTS = (
    "VOID",
    "MECHANISM DID NOT OPERATE",
    "COMPETITION PRESERVED WITH CAPABILITY GAIN",
    "COMPETITION PRESERVED, NO CAPABILITY GAIN",
    "GAIN AT AN EARLY COST",
    "UNDERPOWERED",
)


def prereg() -> dict:
    return json.loads(PREREG.read_text(encoding="utf-8"))


def _median(values: list[float]) -> float:
    return statistics.median(values)


def _interval(gaps: list[float], reps: int, rng_seed: int, level: float) -> tuple[float, float]:
    rng = random.Random(rng_seed)
    medians = []
    for _ in range(reps):
        sample = [gaps[rng.randrange(len(gaps))] for _ in gaps]
        medians.append(statistics.median(sample))
    medians.sort()
    low = medians[max(0, int((1.0 - level) / 2.0 * reps) - 1)]
    high = medians[min(reps - 1, int((1.0 + level) / 2.0 * reps) - 1)]
    return round(low, 6), round(high, 6)


def validate(body: dict | None = None) -> list[str]:
    found: list[str] = []
    body = body or prereg()
    if body.get("prereg") != "Q053-MECHANISM-1":
        found.append("the record is not Q053-MECHANISM-1")
    if body.get("status") != "FROZEN, NOT RUN":
        found.append("the record is not frozen and unrun")
    if body.get("no_cells_run") is not True or body.get("design", {}).get("no_cells_run") is not True:
        found.append("the record does not state that no cell has run")
    mechanism = body.get("mechanism", {})
    if mechanism.get("implemented") is not False:
        found.append("the mechanism must not be implemented by this record")
    if not mechanism.get("changes") or not mechanism.get("prediction"):
        found.append("the mechanism has no statement of what it changes or why")
    design = body.get("design", {})
    seeds = design.get("seeds", [])
    if len(seeds) != len(set(seeds)):
        found.append("the seed block repeats a seed")
    if design.get("bootstrap") in seeds:
        found.append("the bootstrap seed is also a world seed")
    window_floor = design.get("window_floor")
    if seeds and window_floor and min(seeds) < window_floor:
        found.append("the seed block is not the declared fresh window")
    if design.get("cells") != len(seeds) * len(design.get("arms", [])):
        found.append("the cell count is not arms times seeds")
    if body.get("scope", {}).get("family") != "lattice_L1":
        found.append("the record is not lattice_L1-scoped")
    if "DIFFERENT_SUPPORT_COLLAPSE" not in body.get("scope", {}).get("burst_excluded", ""):
        found.append("the burst exclusion does not name the classification that forces it")
    for arm, expected in body.get("arms", {}).items():
        if expected.get("decay") != 0.95 or expected.get("death_threshold") != 0.15:
            found.append("arm %s does not hold decay 0.95 and threshold 0.15" % arm)
    criteria = body.get("criteria", {})
    for name in ("M1_mechanism", "C1_capability", "C2_early_cost"):
        block = criteria.get(name, {})
        if not block.get("bar_provenance"):
            found.append("%s has no provenance for its bar" % name)
        if block.get("bar") is None:
            found.append("%s has no bar" % name)
    if not body.get("gates", {}).get("G1_liveness"):
        found.append("the record has no liveness gate")
    if not body.get("gates", {}).get("void_rule"):
        found.append("the record has no void rule")
    verdicts = {row.get("verdict") for row in body.get("decision_table", [])}
    for label in VERDICTS:
        if label not in verdicts:
            found.append("the decision table cannot reach %r" % label)
    if not body.get("stop_condition"):
        found.append("the record has no stop condition")
    return found


def render(body: dict) -> str:
    design = body["design"]
    mechanism = body["mechanism"]
    criteria = body["criteria"]
    arms = body["arms"]
    lines = [
        "# Q053 mechanism preregistration: one floor, one block, one reading",
        "",
        "Generated from `docs/q053_mechanism_prereg.json` by "
        "`python -m benchmarks.q053_mechanism_prereg --render`. Do not edit by hand.",
        "",
        "**Status: %s.** No cell has run. The mechanism is specified and **not implemented**; "
        "implementing it is an owner decision and is not authorised by this record."
        % body["status"],
        "",
        "## The question",
        "",
        body["question"],
        "",
        "Scope: **%s**, stimulus `%s`, through the online next-cycle recall@5 instrument at "
        "`k = %d`. %s" % (body["scope"]["family"], body["scope"]["stimulus"], design["k"],
                          body["scope"]["burst_excluded"]),
        "",
        "## The mechanism",
        "",
        "**%s** (`%s`)." % (mechanism["name"], mechanism["arm_class"]),
        "",
        mechanism["changes"],
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| competition floor | %s |" % mechanism["parameter"]["competition_floor"],
        "| order | %s |" % mechanism["parameter"]["order"],
        "| scope | %s |" % mechanism["parameter"]["scope"],
        "",
        "**Why it should work.** %s" % mechanism["prediction"],
        "",
        "**Risk, stated before the run.** %s" % mechanism["risk"],
        "",
        "**Edge case.** %s" % mechanism["off_by_one"],
        "",
        "It preserves: %s. It does not: %s."
        % ("; ".join(mechanism["preserves"]), "; ".join(mechanism["does_not"])),
        "",
        "## The two arms",
        "",
        "| Arm | Service | Decay | Death threshold | Rule |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name in design["arms"]:
        arm = arms[name]
        lines.append("| %s | `%s` | %s | %s | %s |" % (
            name, arm["service"], arm["decay"], arm["death_threshold"], arm["rule"]))
    lines += [
        "",
        "The decay factor is held at 0.95 in **both** arms: the treatment may not buy its effect "
        "with persistence, and the run artifact is refused if either arm records a different "
        "value.",
        "",
        "## The block",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| world seeds | %s |" % ", ".join(str(s) for s in design["seeds"]),
        "| bootstrap seed | %s |" % design["bootstrap"],
        "| cells | %s (%s) |" % (design["cells"], design["cells_arithmetic"]),
        "| cycles per cell | %s |" % design["cycles"],
        "| early window | %s-%s |" % tuple(design["early"]),
        "| late window | %s-%s |" % tuple(design["late"]),
        "| pairing | %s |" % design["pairing"],
        "",
        "Freshness: %s." % design["freshness"],
        "",
        "## Criteria, in the order they are read",
        "",
        "| Criterion | Quantity | Rule | Bar | Provenance |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name in criteria["order"]:
        block = criteria[name]
        lines.append("| %s | %s | %s | %s | %s |" % (
            name, block["quantity"], block["rule"], block["bar"], block["bar_provenance"]))
    lines += [
        "",
        "A failed `M1_mechanism` leaves the capability endpoint **unread**: an unrun experiment, "
        "not a null. `C1_capability` additionally requires an interval lower bound above zero and "
        "%s of %s positive seeds; an interval wider than %s is reported as underpowered."
        % (criteria["C1_capability"]["sign_test"]["required"],
           criteria["C1_capability"]["sign_test"]["of"], criteria["underpowered_width"]),
        "",
        "## Gates, which void the block before any criterion is read",
        "",
        "| Gate | Requirement |",
        "| --- | --- |",
    ]
    for name, rule in body["gates"].items():
        if name == "void_rule":
            continue
        lines.append("| %s | %s |" % (name, rule))
    lines += [
        "",
        "Void rule: %s." % body["gates"]["void_rule"],
        "",
        "## The decision table",
        "",
        "| Condition | Verdict | Reading |",
        "| --- | --- | --- |",
    ]
    for row in body["decision_table"]:
        lines.append("| %s | %s | %s |" % (row["condition"], row["verdict"], row["reading"]))
    lines += [
        "",
        "## Adoption",
        "",
        body["adoption"]["rule"],
        "",
        "Not authorised by this block: %s." % "; ".join(body["adoption"]["not_authorised"]),
        "",
        "## Stop condition",
        "",
        body["stop_condition"],
        "",
        "Cost: %s cells at %s cycles each. %s"
        % (body["cost"]["cells"], body["cost"]["cycles_per_cell"], body["cost"]["note"]),
        "",
        "## What this does not claim",
        "",
        "Nothing here shows that competition preservation improves capability, that the floor can "
        "be implemented as described, or that a result would generalise beyond this world family. "
        "The mechanism has not been built, no cell has run, and the engine is unchanged.",
        "",
    ]
    return "\n".join(lines)


def verdict(body: dict, run: dict) -> tuple[str, dict]:
    """The only analysis path: gates, then the criteria in their frozen order."""
    design = body["design"]
    criteria = body["criteria"]
    seeds = list(design["seeds"])
    arms = list(design["arms"])

    cells = {(cell.get("seed"), cell.get("arm")): cell for cell in run.get("cells", [])}
    if set(cells) != {(seed, arm) for seed in seeds for arm in arms}:
        return "VOID", {"gate": "G5_seed_block"}

    for arm in arms:
        recorded = run.get("arms", {}).get(arm, {})
        expected = body["arms"][arm]
        if (recorded.get("decay") != expected["decay"]
                or recorded.get("death_threshold") != expected["death_threshold"]):
            return "VOID", {"gate": "G4_persistence_confound", "arm": arm}

    if run.get("arms", {}).get("control", {}).get("fingerprint") != run.get("engine", {}).get("fingerprint"):
        return "VOID", {"gate": "G2_noop_control"}

    if run.get("control_rerun_fingerprint") != run.get("arms", {}).get("control", {}).get("fingerprint"):
        return "VOID", {"gate": "G3_determinism"}

    for seed in seeds:
        if cells[(seed, "control")].get("late_theory_zero_share", 0.0) < 0.9:
            return "VOID", {"gate": "G1_liveness", "seed": seed}

    for seed in seeds:
        for arm in arms:
            cell = cells[(seed, arm)]
            if not cell.get("predictions_early") or not cell.get("predictions_late"):
                return "VOID", {"gate": "G6_denominator", "seed": seed, "arm": arm}

    m1_gaps = [cells[(s, "treatment")]["late_competition_share"]
               - cells[(s, "control")]["late_competition_share"] for s in seeds]
    m1_median = round(_median(m1_gaps), 6)
    details = {"m1_median_gap": m1_median, "m1_bar": criteria["M1_mechanism"]["bar"],
               "seeds": len(seeds)}
    if m1_median < criteria["M1_mechanism"]["bar"]:
        return "MECHANISM DID NOT OPERATE", details

    capability_gaps = [cells[(s, "treatment")]["late_recall"] - cells[(s, "control")]["late_recall"]
                       for s in seeds]
    early_gaps = [cells[(s, "treatment")]["early_recall"] - cells[(s, "control")]["early_recall"]
                  for s in seeds]
    capability = criteria["C1_capability"]
    low, high = _interval(capability_gaps, capability["bootstrap_reps"], design["bootstrap"],
                          capability["interval"])
    median_gap = round(_median(capability_gaps), 6)
    positive = sum(1 for gap in capability_gaps if gap > 0)
    details.update({"capability_median_gap": median_gap, "capability_bar": capability["bar"],
                    "interval": [low, high], "width": round(high - low, 6),
                    "positive_seeds": positive,
                    "early_median_gap": round(_median(early_gaps), 6)})

    passed = (median_gap >= capability["bar"] and low > 0
              and positive >= capability["sign_test"]["required"])
    if passed:
        if details["early_median_gap"] >= criteria["C2_early_cost"]["bar"]:
            return "COMPETITION PRESERVED WITH CAPABILITY GAIN", details
        return "GAIN AT AN EARLY COST", details
    if details["width"] > criteria["underpowered_width"]:
        return "UNDERPOWERED", details
    return "COMPETITION PRESERVED, NO CAPABILITY GAIN", details


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--render", action="store_true")
    group.add_argument("--analyze")
    args = parser.parse_args(argv)
    body = prereg()
    if args.analyze:
        run = json.loads(Path(args.analyze).read_text(encoding="utf-8"))
        if run.get("prereg") != body["prereg"]:
            raise SystemExit("the run artifact is not for %s" % body["prereg"])
        label, details = verdict(body, run)
        print(json.dumps({"verdict": label, "details": details}, indent=1))
        return 0
    problems = validate(body)
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    page = render(body)
    if args.render:
        DOC.write_text(page, encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0
    if not DOC.exists():
        raise SystemExit("FAIL: %s does not exist" % DOC.name)
    if DOC.read_text(encoding="utf-8") != page:
        raise SystemExit("FAIL: the page is stale; rerun with --render")
    print("prereg %s: frozen, %d cells, no cell run" % (body["prereg"], body["design"]["cells"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
