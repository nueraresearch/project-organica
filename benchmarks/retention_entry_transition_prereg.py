"""CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1: the frozen preregistration.

This block replaces the formation-anchored block's post-landmark appearance with
a distinct structure-entry transition:

    f            = first loop cycle
    early        = f .. f+19
    proximal     = f+20 .. f+39
    structure-free through f+39
    outcome      = first two-cycle structure entry at t >= f+40

Both predictor windows end before the outcome window.  The primary model tests
early retention conditional on proximal retention, rank, count, strength and
follow-up horizon.  The proximal window is a pre-outcome control, not a
reverse-time variable.

This module freezes the design only.  It has no grant, no runner, no cell and
no result.

    python -m benchmarks.retention_entry_transition_prereg --freeze
    python -m benchmarks.retention_entry_transition_prereg --check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp  # noqa: E402

ID = "CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1"
MODULE = "benchmarks.retention_entry_transition_prereg"
RUNNER = "benchmarks.retention_entry_transition"
FROZEN_ON = "2026-11-13"
SEEDS = list(range(20620101, 20620125))
CYCLES = 120
CAP = 40
WINDOW = 20
MAX_FORMATION = 60
STRUCTURE_FREE_THROUGH = 39
OUTCOME_START = 40
ENTRY_RUN = 2
MIN_EDGES = 60
MIN_EVENTS = 20

PREREG = ROOT / "docs" / "retention_entry_transition_prereg.json"
PAGE = ROOT / "docs" / "RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md"
RESULT = ROOT / "docs" / "retention_entry_transition.json"
DESIGN = ROOT / "docs" / "RETENTION-ENTRY-TRANSITION-DESIGN.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def record() -> dict:
    return _load(PREREG)


def build_prereg() -> dict:
    return {
        "prereg": ID,
        "kind": "retention_entry_transition_prereg",
        "status": "FROZEN, NOT RUN",
        "frozen_on": FROZEN_ON,
        "design_document": DESIGN.relative_to(ROOT).as_posix(),
        "question": (
            "Among never-served world edges that first loop by cycle 60 and "
            "remain absent from the readout structure through cycle f + 39, "
            "does loop retention in the first 20 cycles predict a sustained "
            "first structure entry in cycles f + 40 through 120, after "
            "controlling for retention in the adjacent 20-cycle window and for "
            "early rank, count, strength and follow-up horizon?"
        ),
        "reference": {
            "source": "docs/retention_formation_anchored.json",
            "status": "CONFIRMED, TEMPORALLY AMBIGUOUS; not a temporal-order result",
            "prior_population": {
                "never_served": 434,
                "loop_forming": 180,
                "eligible": 172,
                "asserted_events": 70,
                "late_edges": 36,
                "late_events": 18,
            },
            "why_this_block": (
                "The prior block's assertion_cycle was the first structure "
                "appearance after the landmark. That admits a re-entry by an "
                "edge already present before the landmark and labels it a new "
                "assertion. The reverse model also used a post-landmark rate "
                "whose denominator was the follow-up control. This block "
                "requires a structure-free interval through f + 39, makes the "
                "event a two-cycle entry at f + 40 or later, and measures both "
                "early and proximal retention before the outcome window. No "
                "seed, row or part from the prior block is reused."
            ),
        },
        "design": {
            "seeds": SEEDS,
            "cells": len(SEEDS),
            "cycles": CYCLES,
            "cap": CAP,
            "early_window_cycles": WINDOW,
            "proximal_window_cycles": WINDOW,
            "max_formation_cycle": MAX_FORMATION,
            "structure_free_through_offset": STRUCTURE_FREE_THROUGH,
            "outcome_start_offset": OUTCOME_START,
            "entry_run_cycles": ENTRY_RUN,
            "world": (
                "generate_compositional_world(seed=, cycles=120) with the "
                "PHASE_ACQUISITION schedule and one replay per seed"
            ),
            "population": (
                "never-served world edges with ever_loop=true, "
                "formation_cycle <= 60, no structure appearance at any cycle "
                "<= formation_cycle + 39, and full early and proximal windows"
            ),
            "excluded": (
                "never-served edges that never loop; edges forming after cycle "
                "60; edges with any structure appearance through f + 39; edges "
                "served at least once; edges with incomplete predictor windows"
            ),
            "windows": {
                "early": "formation_cycle through formation_cycle + 19",
                "proximal": "formation_cycle + 20 through formation_cycle + 39",
                "outcome": "formation_cycle + 40 through 120",
            },
            "structure_free_interval": (
                "no structure appearance at any cycle from formation_cycle "
                "through formation_cycle + 39, inclusive"
            ),
            "outcome": (
                "sustained first structure entry: the first cycle t >= "
                "formation_cycle + 40 with appearances at both t and t + 1; "
                "entry_cycle = t. Final presence at cycle 120 is descriptive "
                "only."
            ),
            "outcome_horizon": (
                "formation_cycle + 40 through 120; f <= 60 leaves at least 21 "
                "outcome cycles; followup_cycles/120 is the single horizon "
                "control"
            ),
            "freshness": (
                "New seed block 20620101-20620124. The collision scan over "
                "docs JSON is empty at freeze time. No prior block's seed, row "
                "or part is reused."
            ),
            "primary_predictors": {
                "early_retention": (
                    "distinct loop cycles in formation_cycle..formation_cycle+19 "
                    "divided by 20"
                ),
                "proximal_retention": (
                    "distinct loop cycles in formation_cycle+20..formation_cycle+39 "
                    "divided by 20"
                ),
                "rank20": (
                    "minimum 1-based position in the repaired observer's full "
                    "pre-cap universe over formation_cycle..formation_cycle+19"
                ),
                "count20": "direct temporal transition count at formation_cycle + 19",
                "strength20": (
                    "maximum loop_candidate strength over reported loops in "
                    "formation_cycle..formation_cycle+19"
                ),
                "followup": (
                    "outcome cycles from formation_cycle + 40 through 120, "
                    "divided by 120; the single fitted horizon control"
                ),
            },
            "sensitivity_predictors": {
                "rank40": "minimum rank over formation_cycle+20..formation_cycle+39",
                "count40": "direct temporal transition count at formation_cycle + 39",
                "strength40": (
                    "maximum loop_candidate strength over "
                    "formation_cycle+20..formation_cycle+39"
                ),
                "final_assertion": (
                    "presence in the structure at cycle 120; descriptive "
                    "secondary outcome, never the primary event"
                ),
            },
            "late_cohort": None,
            "late_cohort_note": (
                "No late-formation subgroup. Edges with formation_cycle > 60 "
                "are outside this block's scope because the structure-free "
                "interval would leave too few outcome cycles."
            ),
        },
        "model": {
            "family": "binary logistic regression",
            "primary_formula": (
                "logit P(sustained entry) = b0 + b_early*z(early_retention) "
                "+ b_proximal*z(proximal_retention) "
                "+ b_rank*z(log2(rank20)) + b_count*z(count20) "
                "+ b_strength*z(strength20) + b_followup*z(followup) "
                "+ seed fixed effects"
            ),
            "estimator": "Firth penalized likelihood",
            "standardization": "complete-case mean and population SD",
            "seed": "twenty-four-level fixed effect, first seed as reference",
            "selection": "none",
            "primary_coefficient": "b_early",
            "proximal_role": (
                "pre-outcome control. It is measured in f+20..f+39, before the "
                "outcome window begins at f+40; it is not a reverse-time "
                "variable and is not defined after the event."
            ),
            "sensitivity_models": [
                "base model without proximal_retention",
                "full model adding rank40, count40 and strength40",
                "final-presence model with final_assertion as outcome",
            ],
            "sensitivity_status": (
                "reported but not used for the verdict; they cannot rescue a "
                "failed primary criterion"
            ),
        },
        "inference": {
            "primary": (
                "Firth Wald 95% interval for the early-retention odds ratio per "
                "1 SD in the joint model. This is the single primary criterion."
            ),
            "proximal": (
                "The proximal-retention coefficient is reported as the "
                "separation control. It determines whether the early window is "
                "distinguishable from the adjacent pre-outcome window."
            ),
            "alpha": 0.05,
            "multiplicity": (
                "one primary coefficient; the base, full and final-presence "
                "models are sensitivity diagnostics, not additional tests"
            ),
            "no_causal_claim": (
                "Observational entry-transition model. A positive early "
                "coefficient narrows the timing question; it does not identify "
                "a mechanism or a causal effect."
            ),
        },
        "criteria": [
            {"id": "P1", "name": "early-retention direction",
             "test": "joint-model early-retention OR > 1"},
            {"id": "P2", "name": "early-retention interval",
             "test": "joint-model early-retention 95% CI lower bound > 1"},
            {"id": "P3", "name": "gates",
             "test": "all gates D1-D10 pass"},
            {"id": "P4", "name": "proximal separation",
             "test": "proximal-retention OR <= 1 or its 95% CI includes 1"},
        ],
        "verdicts": {
            "CONFIRMED": (
                "P1-P4 pass: early retention adds a positive association with "
                "the later entry transition beyond proximal retention and the "
                "controls."
            ),
            "CONFIRMED, PROXIMALLY AMBIGUOUS": (
                "P1-P3 pass but P4 fails: both windows carry positive "
                "associations; the block does not identify the early window as "
                "the relevant one."
            ),
            "DIRECTIONAL ONLY": (
                "P1 and P3 pass but P2 fails: the point estimate is positive, "
                "the interval is not."
            ),
            "NOT CONFIRMED": "P1 fails.",
            "VOID": "A gate fails; no coefficient is read.",
        },
        "gates": {
            "D1_population": (
                "at least 60 eligible edges and 20 sustained entries; one row "
                "per seed-edge"
            ),
            "D2_structure_free": (
                "every eligible edge has no structure appearance at any cycle "
                "<= f + 39, has finite early and proximal retention in full "
                "20-cycle windows, and has f <= 60"
            ),
            "D3_rank_coverage": (
                "at least 95% of eligible edges have a finite rank20"
            ),
            "D4_seed_levels": "all 24 planned seeds contribute eligible rows",
            "D5_convergence": (
                "the primary joint fit and the base fit converge with finite "
                "coefficients"
            ),
            "D6_complete": (
                "every fitted row has finite count20, strength20 and followup"
            ),
            "D7_entry_validity": (
                "every entry has a finite entry_cycle > f + 39 with appearances "
                "at entry_cycle and entry_cycle + 1; every non-entry has "
                "entry_cycle = None; no edge has a structure appearance before "
                "f + 40"
            ),
            "D8_no_collision": (
                "the seed block is collision-free at freeze and check"
            ),
            "D9_separation": (
                "abs(Pearson r(early_retention, proximal_retention)) <= 0.80; "
                "otherwise the two windows are not separable and the block is "
                "VOID"
            ),
            "D10_exposure": (
                "every eligible edge has at least 20 cycles in f + 40..120; "
                "f <= 60 already implies at least 21"
            ),
        },
        "sample_size": {
            "planned_seeds": len(SEEDS),
            "minimum_edges": MIN_EDGES,
            "minimum_events": MIN_EVENTS,
            "power_calculation": (
                "none. The structure-free 40-cycle requirement may leave too "
                "few entries; D1 is the only feasibility check and is applied "
                "once. The thresholds are not lowered after the count is seen."
            ),
        },
        "amendments": [],
        "authorisation": {
            "required": True,
            "granted": False,
            "document": None,
            "quote": None,
            "note": (
                "No grant is recorded. This module freezes the design only; it "
                "must not run a cell."
            ),
        },
        "runner": {
            "built": True,
            "planned_module": RUNNER,
            "cells_run": 0,
            "measure_command": (
                "python -m benchmarks.retention_entry_transition --measure"
            ),
            "write_command": (
                "python -m benchmarks.retention_entry_transition --finish"
            ),
            "note": (
                "Runner built behind the grant check. --dry-run prints the 24 "
                "commands without a database; --cell, --measure and --finish "
                "refuse until a complete dated grant is recorded. No grant, "
                "cell or result exists."
            ),
        },
        "result": RESULT.relative_to(ROOT).as_posix(),
        "not_evidence": (
            "A preregistration, not a result. It spends no seed and makes no "
            "capability, causal, retention or general engine claim. The prior "
            "block's ambiguous result is not evidence for this design; the "
            "structure-free interval, the two-cycle entry and the 24-seed block "
            "are design choices, and a different interval or entry rule is a "
            "different block."
        ),
    }


def _validate(body: dict) -> list[str]:
    found: list[str] = []
    if body.get("prereg") != ID:
        found.append("prereg id")
    if body.get("status") not in ("FROZEN, NOT RUN", "FROZEN, RUN"):
        found.append("status")
    if body.get("frozen_on") != FROZEN_ON:
        found.append("frozen date")
    design = body.get("design") or {}
    if design.get("seeds") != SEEDS:
        found.append("seed block")
    if design.get("cells") != len(SEEDS):
        found.append("cells")
    if design.get("cycles") != CYCLES or design.get("cap") != CAP:
        found.append("cycles or cap")
    if design.get("early_window_cycles") != WINDOW:
        found.append("early window")
    if design.get("proximal_window_cycles") != WINDOW:
        found.append("proximal window")
    if design.get("max_formation_cycle") != MAX_FORMATION:
        found.append("formation ceiling")
    if design.get("structure_free_through_offset") != STRUCTURE_FREE_THROUGH:
        found.append("structure-free interval")
    if design.get("outcome_start_offset") != OUTCOME_START:
        found.append("outcome start")
    if design.get("entry_run_cycles") != ENTRY_RUN:
        found.append("entry run")
    if design.get("late_cohort") is not None:
        found.append("late cohort")
    if [row.get("id") for row in body.get("criteria") or []] != [
            "P1", "P2", "P3", "P4"]:
        found.append("criteria")
    if set(body.get("verdicts") or {}) != {
            "CONFIRMED", "CONFIRMED, PROXIMALLY AMBIGUOUS",
            "DIRECTIONAL ONLY", "NOT CONFIRMED", "VOID"}:
        found.append("verdict vocabulary")
    if set(body.get("gates") or {}) != {
            "D1_population", "D2_structure_free", "D3_rank_coverage",
            "D4_seed_levels", "D5_convergence", "D6_complete",
            "D7_entry_validity", "D8_no_collision", "D9_separation",
            "D10_exposure"}:
        found.append("gates")
    model = body.get("model") or {}
    formula = str(model.get("primary_formula", ""))
    if "b_early" not in formula or "b_proximal" not in formula:
        found.append("primary formula")
    if "b_formation" in formula:
        found.append("formation is a fitted predictor")
    auth = body.get("authorisation") or {}
    if auth.get("granted") is not False:
        found.append("grant")
    runner = body.get("runner") or {}
    if runner.get("built") is not True:
        found.append("runner state")
    if runner.get("planned_module") != RUNNER:
        found.append("runner module")
    expected_cells = len(SEEDS) if body.get("status") == "FROZEN, RUN" else 0
    if runner.get("cells_run") != expected_cells:
        found.append("cells run")
    if body.get("result") != RESULT.relative_to(ROOT).as_posix():
        found.append("result path")
    if engine_stamp.missing(body):
        found.append("stamp: %r" % (engine_stamp.missing(body),))
    return found


def render(body: dict) -> str:
    d = body["design"]
    lines = [
        "# Retention entry-transition — preregistration",
        "",
        "Generated from `%s` by "
        "`python -m benchmarks.retention_entry_transition_prereg --freeze`. "
        "Do not edit by hand." % PREREG.relative_to(ROOT),
        "",
        "**Status: `%s`.** The design was frozen before any cell. The runner "
        "is built behind the grant check; there is no grant, part or result."
        % body["status"],
        "",
        "## Question",
        "",
        body["question"],
        "",
        "## Why this block exists",
        "",
        "`CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` returned "
        "**`CONFIRMED, TEMPORALLY AMBIGUOUS`**: early-retention OR **2.09** "
        "(1.36–3.23), reverse post-landmark OR **32.83** (8.66–124.44). The "
        "reverse audit found the late OR stable to the follow-up control but "
        "concentrated at the boundaries: **11/11** edges at late retention "
        "**1.0** were asserted, **58/100** in between, against **1/55** at "
        "**0.0**. That block still "
        "defined assertion as a first post-landmark appearance, which can be a "
        "re-entry by an edge already present before the landmark.",
        "",
        body["reference"]["why_this_block"],
        "",
        "## Timeline",
        "",
        "```text",
        "f .............. f+19 | f+20 ........ f+39 | f+40 ................ 120",
        "     early retention      proximal retention     first sustained entry",
        "     <----------- structure-free through f+39 ----------->",
        "```",
        "",
        "## Design",
        "",
        "- Seeds: **%s** (24 fresh seeds)." % ", ".join(
            str(seed) for seed in d["seeds"]),
        "- **%d** cycles, cap **%d**, PHASE_ACQUISITION, one replay per seed."
        % (d["cycles"], d["cap"]),
        "- Formation ceiling: **f <= %d**." % d["max_formation_cycle"],
        "- Structure-free interval: **no structure appearance through f + %d**."
        % d["structure_free_through_offset"],
        "- Outcome window: **f + %d through 120**." % d["outcome_start_offset"],
        "- Population: %s." % d["population"],
        "- Excluded: %s." % d["excluded"],
        "- Outcome: %s." % d["outcome"],
        "- Horizon control: `followup`; `f` is descriptive.",
        "",
        "The event is not final presence. It is the first **two-cycle** "
        "structure entry at or after `f + 40`, so a one-cycle flicker does not "
        "count and a later exit does not erase the entry. Final presence at "
        "cycle 120 is reported separately.",
        "",
        "## Primary model",
        "",
        "```text",
        body["model"]["primary_formula"],
        "```",
        "",
        "The primary coefficient is `b_early`. `proximal_retention` is a "
        "pre-outcome control measured in `f+20..f+39`; it is not a "
        "reverse-time variable. The estimator is Firth penalized likelihood "
        "with 24 seed fixed effects.",
        "",
        "The base model without proximal retention, the full model adding "
        "`rank40`, `count40` and `strength40`, and the final-presence model are "
        "sensitivity diagnostics. They are reported but do not decide the "
        "verdict.",
        "",
        "## Criteria",
        "",
        "| ID | Criterion |",
        "| --- | --- |",
    ]
    for row in body["criteria"]:
        lines.append("| `%s` %s | %s |" % (row["id"], row["name"], row["test"]))
    lines += [
        "",
        "## Verdicts",
        "",
        "| Verdict | Reading |",
        "| --- | --- |",
    ]
    for name, text in body["verdicts"].items():
        lines.append("| `%s` | %s |" % (name, text))
    lines += [
        "",
        "## Gates",
        "",
        "| Gate | Requirement |",
        "| --- | --- |",
    ]
    for name, text in body["gates"].items():
        lines.append("| `%s` | %s |" % (name, text))
    lines += [
        "",
        "## Sample size",
        "",
        "- Planned seeds: **%d**." % body["sample_size"]["planned_seeds"],
        "- Minimum eligible edges: **%d**." % body["sample_size"]["minimum_edges"],
        "- Minimum sustained entries: **%d**." % body["sample_size"]["minimum_events"],
        "- Power calculation: %s" % body["sample_size"]["power_calculation"],
        "",
        "`D1_population` is a feasibility gate, not a target. If the strict "
        "structure-free interval leaves fewer than 60 eligible edges or 20 "
        "sustained entries, the block is `VOID`; no threshold is lowered after "
        "the count is seen.",
        "",
        "## Authorisation",
        "",
        "No grant is recorded. The block is `FROZEN, NOT RUN`; the runner is "
        "built behind the grant check, but no part, result, gate or verdict "
        "exists. It must not be cited as evidence until it has a dated grant, a "
        "run artifact and a verdict from its own gates.",
        "",
        "## What this does not establish",
        "",
        body["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def freeze() -> int:
    if PREREG.exists():
        print("REFUSED: prereg exists")
        return 2
    from benchmarks.presence_cap_experiment import seed_collisions
    if seed_collisions(SEEDS, allow=()):
        print("REFUSED: seed collision")
        return 2
    body = engine_stamp.stamp(build_prereg())
    PREREG.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    print("froze %s" % PREREG.relative_to(ROOT))
    return 0


def problems(body: dict | None = None) -> list[str]:
    body = _load(PREREG) if body is None else body
    found = _validate(body)
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(body):
        found.append("page stale")
    from benchmarks.presence_cap_experiment import seed_collisions
    if seed_collisions(SEEDS, allow=(PREREG,)):
        found.append("seed collision")
    if RESULT.exists() and body.get("status") != "FROZEN, RUN":
        found.append("result exists before run")
    return found


def check() -> int:
    if not PREREG.exists():
        raise SystemExit("no prereg; run --freeze")
    found = problems()
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("retention entry-transition: %s, seeds %d, cells 0, no grant"
          % (ID, len(SEEDS)))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return freeze() if args.freeze else check()


if __name__ == "__main__":
    raise SystemExit(main())
