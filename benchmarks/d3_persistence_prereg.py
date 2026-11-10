"""The frozen D3 persistence preregistration: one repair, two stages, one reading.

The record is data (`docs/d3_persistence_prereg.json`) rendered to
`docs/D3-PERSISTENCE-PREREGISTRATION.md`. The scorer in this module is the only analysis path:
it takes a run artifact, applies the gates, then the criteria in their frozen order, and returns
one of the decision table's labels. Nothing here runs a cell, and nothing here changes the engine.

    ./.venv/bin/python -m benchmarks.d3_persistence_prereg --check
    ./.venv/bin/python -m benchmarks.d3_persistence_prereg --render
    ./.venv/bin/python -m benchmarks.d3_persistence_prereg --analyze docs/d3_persistence_run.json
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs" / "d3_persistence_prereg.json"
DOC = ROOT / "docs" / "D3-PERSISTENCE-PREREGISTRATION.md"

VERDICTS = (
    "VOID",
    "WITNESS BROKEN",
    "NO REPAIR",
    "PERSISTENCE REPAIRED WITH EARLY COST",
    "PERSISTENCE REPAIRED",
)

STAGES = ("witness", "preflight")
ARMS = ("control", "treatment")


def prereg() -> dict:
    return json.loads(PREREG.read_text(encoding="utf-8"))


def _median(values: list[float]) -> float:
    return statistics.median(values)


def validate(body: dict | None = None) -> list[str]:
    found: list[str] = []
    body = body or prereg()
    if body.get("prereg") != "D3-PERSISTENCE-1":
        found.append("the record is not D3-PERSISTENCE-1")
    if body.get("status") != "FROZEN, NOT RUN":
        found.append("the record is not frozen and unrun")
    if body.get("no_cells_run") is not True or body.get("design", {}).get("no_cells_run") is not True:
        found.append("the record does not state that no cell has run")
    mechanism = body.get("mechanism", {})
    if mechanism.get("implemented") is not False:
        found.append("the mechanism must not be implemented by this record")
    if not mechanism.get("changes") or not mechanism.get("prediction"):
        found.append("the mechanism has no statement of what it changes or why")
    predicts = body.get("predicts", {})
    if not predicts.get("success") or not predicts.get("failure"):
        found.append("the record has no success and failure predictions")
    if not body.get("adoption", {}).get("withdrawal"):
        found.append("the record has no withdrawal rule")
    design = body.get("design", {})
    seeds = design.get("seeds", [])
    if len(seeds) != 6:
        found.append("the seed block is not six seeds")
    if len(seeds) != len(set(seeds)):
        found.append("the seed block repeats a seed")
    if design.get("bootstrap") in seeds:
        found.append("the bootstrap seed is also a world seed")
    window_floor = design.get("window_floor")
    if seeds and window_floor and min(seeds) < window_floor:
        found.append("the seed block is not the declared fresh window")
    if design.get("cells") != len(seeds) * len(design.get("arms", [])) * 2:
        found.append("the cell count is not two stages times arms times seeds")
    stages = design.get("stages", {})
    if stages.get("witness", {}).get("design") != "L3_hub1_t3_mixed":
        found.append("the witness stage is not the adopted L3 witness")
    if stages.get("witness", {}).get("cycles") != 40:
        found.append("the witness stage is not 40 cycles")
    if stages.get("preflight", {}).get("design") != "L1_hub1_t3_disjoint":
        found.append("the preflight stage is not the campaign stimulus")
    if stages.get("preflight", {}).get("horizon") != 3000:
        found.append("the preflight horizon is not the campaign horizon")
    for arm, expected in body.get("arms", {}).items():
        if expected.get("decay") != 0.95 or expected.get("death_threshold") != 0.15:
            found.append("arm %s does not hold decay 0.95 and threshold 0.15" % arm)
    if body.get("arms", {}).get("treatment", {}).get("frequency_decay") != 0.95:
        found.append("the treatment does not match the 0.95 denominator decay")
    if body.get("arms", {}).get("control", {}).get("frequency_decay") != "none":
        found.append("the control is not free of the denominator decay")
    criteria = body.get("criteria", {})
    for name in ("W1_witness", "P1_persistence", "C1_early_cost"):
        block = criteria.get(name, {})
        if block.get("bar") is None:
            found.append("%s has no bar" % name)
        if not block.get("bar_provenance"):
            found.append("%s has no provenance for its bar" % name)
    gates = body.get("gates", {})
    for name in ("G1_baseline_death", "G2_manipulation_live", "G3_noop_control",
                 "G4_determinism", "G5_seed_block", "G6_denominator",
                 "G7_negative_controls", "void_rule"):
        if not gates.get(name):
            found.append("the record has no %s" % name)
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
    stages = design["stages"]
    lines = [
        "# D3 persistence preregistration: matched source-frequency decay",
        "",
        "Generated from `docs/d3_persistence_prereg.json` by "
        "`python -m benchmarks.d3_persistence_prereg --render`. Do not edit by hand.",
        "",
        "**Status: %s.** No cell has run. The repair is available only as the in-process "
        "`MatchedFrequencySleepService`; it is **not promoted into the engine**, and "
        "promotion is an owner decision." % body["status"],
        "",
        "D3 in `docs/DECISION-G1-WITNESS.md` is **PENDING** and requires its own preregistration. "
        "This is that record. It does not change an engine file and does not authorise a run.",
        "",
        "## The question",
        "",
        body["question"],
        "",
        "Scope: **%s**. Witness `%s`; campaign stimulus `%s`. %s"
        % (body["scope"]["family"], body["scope"]["witness_design"],
           body["scope"]["campaign_design"], body["scope"]["burst_excluded"]),
        "",
        "Pre-flight hook: `%s`." % body["scope"]["preflight_hook"],
        "",
        "## Why this repair, and not a slower decay",
        "",
        "Q046 already moved the temporal decay factor from 0.95 to 0.99 and delayed the death "
        "from cycle 39 to cycle 228 on all six arms. It did not reach the campaign horizon. The "
        "measured cause is not only the numerator: the source frequency that divides it grows "
        "without decay, so an edge renewed every cycle is still diluted by its own history. This "
        "record changes the denominator's horizon, not the decay constant.",
        "",
        "## The mechanism",
        "",
        "**%s** (`%s`)." % (mechanism["name"], mechanism["arm_class"]),
        "",
        mechanism["changes"],
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| frequency decay | %s |" % mechanism["parameter"]["frequency_decay"],
        "| order | %s |" % mechanism["parameter"]["order"],
        "| scope | %s |" % mechanism["parameter"]["scope"],
        "",
        "**Why it should work.** %s" % mechanism["prediction"],
        "",
        "**Risk, stated before the run.** %s" % mechanism["risk"],
        "",
        "**What success would look like.** %s" % body["predicts"]["success"],
        "",
        "**What failure would look like.** %s" % body["predicts"]["failure"],
        "",
        "**Edge case.** %s" % mechanism["off_by_one"],
        "",
        "It preserves: %s. It does not: %s."
        % ("; ".join(mechanism["preserves"]), "; ".join(mechanism["does_not"])),
        "",
        "## The two arms",
        "",
        "| Arm | Service | Decay | Death threshold | Frequency decay | Rule |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name in ARMS:
        arm = arms[name]
        lines.append("| %s | `%s` | %s | %s | %s | %s |" % (
            name, arm["service"], arm["decay"], arm["death_threshold"],
            arm["frequency_decay"], arm["rule"]))
    lines += [
        "",
        "The temporal decay factor is held at 0.95 in **both** arms. The treatment may not buy its "
        "effect by slowing the graph's decay: the run artifact is refused if either arm records a "
        "different value, or if the treatment records a denominator decay other than 0.95.",
        "",
        "## The block",
        "",
        "| Stage | Design | Cycles | What it reads |",
        "| --- | --- | --- | --- |",
        "| witness | `%s` | %s | %s |" % (stages["witness"]["design"], stages["witness"]["cycles"],
                                          stages["witness"]["reads"]),
        "| preflight | `%s` | %s | %s |" % (stages["preflight"]["design"],
                                            stages["preflight"]["horizon"],
                                            stages["preflight"]["reads"]),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| world seeds | %s |" % ", ".join(str(s) for s in design["seeds"]),
        "| bootstrap seed | %s |" % design["bootstrap"],
        "| cells | %s (%s) |" % (design["cells"], design["cells_arithmetic"]),
        "| early window | %s-%s |" % tuple(design["early"]),
        "| k | %s |" % design["k"],
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
        "The criteria are judged whole. A failed W1 leaves P1 and C1 unread: a repair that breaks "
        "the witness cannot be adopted for the campaign even if it keeps L1 alive.",
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
        "**Withdrawal.** %s" % body["adoption"]["withdrawal"],
        "",
        "Not authorised by this block: %s." % "; ".join(body["adoption"]["not_authorised"]),
        "",
        "## Stop condition",
        "",
        body["stop_condition"],
        "",
        "Cost: %s cells. %s." % (body["cost"]["cells"], body["cost"]["cycles"]),
        "",
        "## What this does not claim",
        "",
        "Nothing here shows that matched denominator decay restores persistence, that it can be "
        "implemented as described, or that a result would generalise beyond these two designs. "
        "The repair has not been built, no cell has run, and the engine is unchanged.",
        "",
    ]
    return "\n".join(lines)


def verdict(body: dict, run: dict) -> tuple[str, dict]:
    """The only analysis path: gates, then the criteria in their frozen order."""
    design = body["design"]
    criteria = body["criteria"]
    seeds = list(design["seeds"])

    cells = {(cell.get("stage"), cell.get("seed"), cell.get("arm")): cell
             for cell in run.get("cells", [])}
    expected = {(stage, seed, arm) for stage in STAGES for seed in seeds for arm in ARMS}
    if set(cells) != expected:
        return "VOID", {"gate": "G5_seed_block"}

    for arm in ARMS:
        recorded = run.get("arms", {}).get(arm, {})
        wanted = body["arms"][arm]
        if (recorded.get("decay") != wanted["decay"]
                or recorded.get("death_threshold") != wanted["death_threshold"]
                or recorded.get("frequency_decay") != wanted["frequency_decay"]):
            return "VOID", {"gate": "G2_manipulation_live", "arm": arm}

    if run.get("arms", {}).get("control", {}).get("fingerprint") != run.get("engine", {}).get("fingerprint"):
        return "VOID", {"gate": "G3_noop_control"}

    if run.get("control_rerun_fingerprint") != run.get("arms", {}).get("control", {}).get("fingerprint"):
        return "VOID", {"gate": "G4_determinism"}

    for key, cell in cells.items():
        if not cell.get("predictions_early"):
            return "VOID", {"gate": "G6_denominator", "cell": list(key)}

    controls = run.get("witness_negative_controls", {})
    if (controls.get("NO_DREAMS", {}).get("dreams_max") != 0
            or controls.get("NO_QUESTIONS", {}).get("questions_max") != 0):
        return "VOID", {"gate": "G7_negative_controls"}

    for seed in seeds:
        first_zero = cells[("preflight", seed, "control")].get("first_zero_cycle")
        if first_zero is None or not (1 <= first_zero <= 60):
            return "VOID", {"gate": "G1_baseline_death", "seed": seed}

    witness_ok = 0
    for seed in seeds:
        treatment = cells[("witness", seed, "treatment")]
        if (treatment.get("theory_cycles", 0) >= 39
                and treatment.get("peak", 0) >= 6):
            witness_ok += 1
    if witness_ok < 5:
        return "WITNESS BROKEN", {"witness_seeds": witness_ok, "seeds": len(seeds)}

    alive = 0
    for seed in seeds:
        treatment = cells[("preflight", seed, "treatment")]
        counts = treatment.get("theory_counts") or []
        if (treatment.get("first_zero_cycle") is None
                and len(counts) >= 100
                and min(counts[-100:]) > 0):
            alive += 1
    details = {"alive_seeds": alive, "seeds": len(seeds)}
    if alive < 5:
        return "NO REPAIR", details

    gaps = [cells[("preflight", seed, "treatment")]["recall_early"]
            - cells[("preflight", seed, "control")]["recall_early"] for seed in seeds]
    early_gap = round(_median(gaps), 6)
    details.update({"early_median_gap": early_gap,
                    "early_bar": criteria["C1_early_cost"]["bar"]})
    if early_gap < criteria["C1_early_cost"]["bar"]:
        return "PERSISTENCE REPAIRED WITH EARLY COST", details
    return "PERSISTENCE REPAIRED", details


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
