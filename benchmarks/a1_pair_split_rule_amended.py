"""Amend the pair-split decision rule to the bands its own budget can pay for.

`A1-OFFSET-DISCRIMINATOR-SPEC-1` commits a rule on the split-32 minus split-48
offset difference: **size** if |d| <= 0.05, **density** if d <= -0.09, nothing
in between, with six seeds per block in the construction block and the note
"about 3 standard errors at six seeds per block".  `A1-SPLIT-POWER-1` then
priced that rule honestly: at a 5%/5% error guarantee with 80% power it needs
**nine** seeds per block, and at six seeds the density branch reaches only
**0.767** power.  `A1-BAND-FRONTIER-1` showed why and where the slack is: the
density ceiling is over-conservative while the size floor is already near its
bound, and **0.05/0.07** holds both error rates at 5% with both branches at 80%
at six seeds.

This artifact writes the **amended rule** — not an edit to the committed spec,
which stays exactly as it was — and records what it supersedes and why:

* the committed rule is restated verbatim with its measured cost,
* the amended bands are **0.05 / 0.07**, keeping the committed six seeds per
  block (**20690101-20690106**) and the committed construction,
* every number in the amendment carries the artifact and field it came from,
* the amendment is admissible only under the stated error budget, and the
  budget is stated.

No arm is run: this is a rule on paper, priced from committed artifacts.

    python -m benchmarks.a1_pair_split_rule_amended --write
    python -m benchmarks.a1_pair_split_rule_amended --check
    python -m benchmarks.a1_pair_split_rule_amended --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.a1_band_frontier import outcomes

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SPEC_PATH = DOCS / "a1_offset_discriminator_spec.json"
FRONTIER_PATH = DOCS / "a1_band_frontier.json"
POWER_PATH = DOCS / "a1_split_power.json"
OUT_PATH = DOCS / "a1_pair_split_rule_amended.json"
PAGE_PATH = DOCS / "A1-PAIR-SPLIT-RULE-AMENDED.md"
ID = "A1-PAIR-SPLIT-RULE-AMENDED-1"
DATE = "2026-11-14"
KIND = "a1_pair_split_rule_amended"
STATUS = ("AMENDED DESIGN RULE — PAIR-SPLIT DIFFERENTIAL WITH REPAIRED BANDS; "
          "NO ARM, NO RUN, NO TARGET, NO GRANT")
OLD_FLOOR = 0.05
OLD_CEILING = 0.09
NEW_FLOOR = 0.05
NEW_CEILING = 0.07
SEEDS_PER_BLOCK = 6
BUDGET = 0.05
POWER = 0.80
SIGMA = 0.066656


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _row(n: int, floor: float, ceiling: float) -> dict:
    return outcomes(n, floor, ceiling)


def build() -> dict:
    spec = _load(SPEC_PATH)
    frontier = _load(FRONTIER_PATH)
    power = _load(POWER_PATH)
    if spec["constants"]["decision_floor"] != OLD_FLOOR or \
            spec["constants"]["decision_ceiling"] != OLD_CEILING:
        raise SystemExit("REFUSED: the committed rule moved")
    gap = round(spec["predictions"][1]["density_offset"]
                - spec["predictions"][0]["density_offset"], 6)
    if abs(gap - 0.11638) > 1e-4:
        raise SystemExit("REFUSED: the differential moved")
    if frontier["found"]["cheapest_ceiling"] != NEW_CEILING:
        raise SystemExit("REFUSED: the frontier no longer recommends 0.07")
    cheapest = next(row for row in frontier["rows"]
                    if (row["floor"], row["ceiling"])
                    == (NEW_FLOOR, NEW_CEILING))
    committed = next(row for row in frontier["rows"]
                     if (row["floor"], row["ceiling"])
                     == (OLD_FLOOR, OLD_CEILING))
    amended = _row(SEEDS_PER_BLOCK, NEW_FLOOR, NEW_CEILING)
    old = _row(SEEDS_PER_BLOCK, OLD_FLOOR, OLD_CEILING)
    admissible = (amended["density_if_size"] <= BUDGET
                  and amended["size_if_density"] <= BUDGET
                  and amended["size_if_size"] >= POWER
                  and amended["density_if_density"] >= POWER)
    if not admissible:
        raise SystemExit("REFUSED: the amended bands do not meet their own "
                         "budget at the committed seed count")
    seeds = spec["construction"]["seeds"]
    if len(seeds) != SEEDS_PER_BLOCK:
        raise SystemExit("REFUSED: the construction block holds %d seeds, not %d"
                         % (len(seeds), SEEDS_PER_BLOCK))
    rule = {
        "statistic": "measured offset(split-32) minus offset(split-48)",
        "floor": NEW_FLOOR,
        "ceiling": NEW_CEILING,
        "size_if": "|d| <= %.2f" % NEW_FLOOR,
        "density_if": "d <= -%.2f" % NEW_CEILING,
        "undecided_if": "-%.2f < d < -%.2f, or d > %.2f"
        % (NEW_CEILING, NEW_FLOOR, NEW_FLOOR),
        "size_prediction": 0.0,
        "density_prediction": -gap,
        "seeds_per_block": SEEDS_PER_BLOCK,
        "seeds": seeds,
        "blocks": ["split-32", "split-48"],
        "error_budget": BUDGET,
        "power_target": POWER,
    }
    found = {
        "gap": gap,
        "old_rule": {"floor": OLD_FLOOR, "ceiling": OLD_CEILING,
                     "seeds_per_block": committed["seeds"]["0.05"],
                     "power_density_at_six": old["density_if_density"],
                     "power_size_at_six": old["size_if_size"],
                     "false_density_at_six": old["density_if_size"],
                     "false_size_at_six": old["size_if_density"]},
        "new_rule": {"floor": NEW_FLOOR, "ceiling": NEW_CEILING,
                     "seeds_per_block": cheapest["seeds"]["0.05"]},
        "seeds_saved_per_block": (committed["seeds"]["0.05"]
                                  - cheapest["seeds"]["0.05"]),
        "amended_at_six": amended,
        "admissible_at_six": admissible,
        "sigma": SIGMA,
        "sigma_source": power["found"]["primary_sigma_source"],
        "supersedes": [
            {"id": spec["id"], "field": "decision_rule.if_abs_above",
             "committed": spec["decision_rule"]["if_abs_above"],
             "amended": "0.07 with the density sign"},
            {"id": power["id"], "field": "found.seeds_both_at_primary",
             "committed": power["found"]["seeds_both_at_primary"],
             "amended": cheapest["seeds"]["0.05"]},
        ],
        "unchanged": {
            "construction": spec["construction"]["law"],
            "split_blocks": [block["label"] for block in spec["construction"]["blocks"]],
            "seeds": seeds,
            "equal_m_check": spec["constants"]["equal_m_tolerance"],
            "floor": NEW_FLOOR,
        },
    }
    reading = (
        "The amended rule keeps the committed construction, the committed six "
        "seeds per block and the committed **0.05** floor, and moves **one** "
        "number: the density ceiling falls from **0.09** to **0.07**. What it "
        "supersedes is the previous rule's cost, not its intent. `%s` needed "
        "**%d** seeds per block at a 5%%/5%% guarantee and reached only "
        "**%.3f** density-branch power at six; at the repaired ceiling the same "
        "six seeds hold the false-density rate at **%.4f** and the false-size "
        "rate at **%.4f**, with **%.3f** power on the size branch and **%.3f** "
        "on the density branch — admissible at the stated budget, so the seeds "
        "the construction already lists are enough and no new seed is bought. "
        "The amended rule is therefore: **size** if |d| ≤ **0.05**, **density** "
        "if d ≤ **−0.07**, undecided between them, on the split-32 minus "
        "split-48 difference with predictions **0.000** and **−0.116**. The "
        "ceiling cannot fall further at this budget: **0.0633** is the "
        "admissible edge at six seeds, and below it the rule starts calling "
        "density on seeds where the size summary is true. The ceiling touches only "
        "the density branch's two outcomes: the size branch's false rate is "
        "**%.4f** under either band, which is why the floor, not the ceiling, "
        "binds the size account. The amendment costs "
        "nothing to adopt — it removes the need for the three extra seeds the "
        "committed bands implied — and it is written as a separate artifact so "
        "the committed spec remains readable as the rule that was signed."
        % (spec["id"], committed["seeds"]["0.05"],
           old["density_if_density"], amended["density_if_size"],
           amended["size_if_density"], amended["size_if_size"],
           amended["density_if_density"], amended["size_if_density"])
    )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "What decision rule should the pair-split discriminator use, given "
            "that its committed bands cost nine seeds per block and its "
            "construction lists six?"
        ),
        "definition": (
            "The amended pair-split rule: statistic, bands, predictions, seed "
            "budget, error rates and power at the committed seed count, with "
            "each superseded number named against the artifact that carried it."
        ),
        "method": (
            "Read the committed rule and construction, the frontier's "
            "recommended bands and the split-power budget; recompute the four "
            "branch probabilities at six seeds with the same exact two-sample t "
            "used by both power artifacts; refuse to write unless the amended "
            "bands meet their own budget."
        ),
        "rule": rule,
        "provenance": [
            {"value": "floor 0.05", "artifact": "a1_offset_discriminator_spec.json",
             "field": "constants.decision_floor"},
            {"value": "ceiling 0.09 (superseded)",
             "artifact": "a1_offset_discriminator_spec.json",
             "field": "constants.decision_ceiling"},
            {"value": "ceiling 0.07 (amended)",
             "artifact": "a1_band_frontier.json",
             "field": "found.cheapest_ceiling"},
            {"value": "six seeds per block",
             "artifact": "a1_offset_discriminator_spec.json",
             "field": "construction.seeds"},
            {"value": "admissible ceiling edge 0.0633",
             "artifact": "a1_band_frontier.json",
             "field": "found.bounds[0].ceiling_min"},
            {"value": "per-seed SD 0.066656", "artifact": "a1_split_power.json",
             "field": "found.primary_sigma"},
        ],
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "found": found,
        "limits": [
            "The amendment changes a rule on paper only; no split block has been run, so the error rates it guarantees are the design's, not a measurement.",
            "The seeds the construction lists are reused, but they have never been spent on a split block; the budget statement says the block is sufficient, not that it has been executed.",
            "The per-seed SD is borrowed from 16-tag blocks; at a larger SD the admissible ceiling rises and the rule would need re-pricing before use.",
            "The committed spec is left unedited on purpose: a reader must be able to see the rule that was signed beside the rule that replaces it.",
        ],
        "not_evidence": (
            "An amended design rule priced from committed artifacts. It runs no "
            "arm, measures no split block, and is not a treatment, target, "
            "freeze, grant or A1 cell."
        ),
    })


def render(doc: dict) -> str:
    rule = doc["rule"]
    found = doc["found"]
    amended = found["amended_at_six"]
    lines = [
        "# A1 pair-split rule, amended",
        "",
        "Generated from `docs/a1_pair_split_rule_amended.json` by "
        "`python -m benchmarks.a1_pair_split_rule_amended --write`. "
        "Do not edit by hand.",
        "",
        "**Amended design rule, not a result. No split block has been run.**",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## The rule",
        "",
        "| Element | Value |",
        "| --- | --- |",
        "| Statistic | %s |" % rule["statistic"],
        "| Size if | `%s` |" % rule["size_if"],
        "| Density if | `%s` |" % rule["density_if"],
        "| Undecided if | `%s` |" % rule["undecided_if"],
        "| Predictions | size %.3f, density %.5f |" % (
            rule["size_prediction"], rule["density_prediction"]),
        "| Seeds per block | %d (%s) |" % (
            rule["seeds_per_block"],
            ", ".join(str(seed) for seed in rule["seeds"])),
        "| Error budget | %.2f per wrong branch |" % rule["error_budget"],
        "| Power target | %.2f per correct branch |" % rule["power_target"],
        "",
        "## What changed and what it costs",
        "",
        "| Quantity | Committed | Amended |",
        "| --- | ---: | ---: |",
        "| Density ceiling | %.2f | %.2f |" % (
            found["old_rule"]["ceiling"], found["new_rule"]["ceiling"]),
        "| Seeds per block at 5%% | %d | %d |" % (
            found["old_rule"]["seeds_per_block"],
            found["new_rule"]["seeds_per_block"]),
        "| Seeds saved per block | — | %d |" % found["seeds_saved_per_block"],
        "",
        "## At the committed six seeds per block",
        "",
        "| Quantity | Committed bands | Amended bands |",
        "| --- | ---: | ---: |",
        "| Size branch power | %.4f | %.4f |" % (
            found["old_rule"]["power_size_at_six"], amended["size_if_size"]),
        "| Density branch power | %.4f | %.4f |" % (
            found["old_rule"]["power_density_at_six"],
            amended["density_if_density"]),
        "| Declares density when size is true | %.4f | %.4f |" % (
            found["old_rule"]["false_density_at_six"], amended["density_if_size"]),
        "| Declares size when density is true | %.4f | %.4f |" % (
            found["old_rule"]["false_size_at_six"], amended["size_if_density"]),
        "",
        "## Superseded numbers",
        "",
        "| Artifact | Field | Committed | Amended |",
        "| --- | --- | --- | --- |",
    ]
    for row in found["supersedes"]:
        lines.append("| %s | %s | %s | %s |" % (
            row["id"], row["field"], row["committed"], row["amended"]))
    lines += [
        "",
        "## Provenance",
        "",
        "| Value | Artifact | Field |",
        "| --- | --- | --- |",
    ]
    for row in doc["provenance"]:
        lines.append("| %s | `%s` | `%s` |" % (
            row["value"], row["artifact"], row["field"]))
    lines += ["", "## Limits", ""]
    lines += ["- %s" % limit for limit in doc["limits"]]
    lines += ["", "## What this does not claim", "", doc["not_evidence"], ""]
    return "\n".join(lines)


def problems(doc: dict | None = None) -> list[str]:
    doc = _load(OUT_PATH) if doc is None else doc
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("artifact kind")
    if doc.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    if engine_stamp.missing(doc):
        found.append("the artifact is not fully stamped")
    if doc.get("governance") != {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none"}:
        found.append("governance changed")
    rule = doc.get("rule") or {}
    if rule.get("floor") != NEW_FLOOR or rule.get("ceiling") != NEW_CEILING:
        found.append("the amended bands are not 0.05/0.07")
    if rule.get("seeds_per_block") != SEEDS_PER_BLOCK:
        found.append("the amended seed budget changed")
    if len(rule.get("seeds") or []) != SEEDS_PER_BLOCK:
        found.append("the amended rule does not list six seeds")
    amended = doc["found"]["amended_at_six"]
    if amended["density_if_size"] > BUDGET or amended["size_if_density"] > BUDGET:
        found.append("the amended bands exceed their error budget")
    if amended["size_if_size"] < POWER or amended["density_if_density"] < POWER:
        found.append("the amended bands miss the power target")
    if amended["density_if_density"] <= doc["found"]["old_rule"][
            "power_density_at_six"]:
        found.append("the amended ceiling does not beat the committed power")
    if doc["found"]["seeds_saved_per_block"] != (
            doc["found"]["old_rule"]["seeds_per_block"]
            - doc["found"]["new_rule"]["seeds_per_block"]):
        found.append("the reported saving does not match the two budgets")
    if not doc.get("provenance"):
        found.append("no provenance")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    old = _row(SEEDS_PER_BLOCK, OLD_FLOOR, OLD_CEILING)
    new = _row(SEEDS_PER_BLOCK, NEW_FLOOR, NEW_CEILING)
    if new["density_if_density"] <= old["density_if_density"]:
        failures.append("the lower ceiling does not raise density-branch power")
    if new["size_if_size"] != old["size_if_size"]:
        failures.append("moving the ceiling changed the size branch")
    if new["density_if_size"] <= old["density_if_size"]:
        failures.append("the lower ceiling does not raise the false-density rate")
    if not (new["density_if_size"] <= BUDGET and new["size_if_density"] <= BUDGET):
        failures.append("the amended bands are not admissible at six seeds")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    print("found:", json.dumps(body["found"], indent=1)[:1600])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no amended-rule artifact; run --write")
    found = problems(_load(OUT_PATH))
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("pair-split amended rule: clean")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.self_test:
        found = self_test()
        if found:
            raise SystemExit("FAIL: " + "; ".join(found))
        print("pair-split amended rule: self-test clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
