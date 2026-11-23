"""CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1.

A frozen follow-up to ``CONFIRMATORY-RETENTION-INCREMENTAL-1``.  The fixed
cycle-60 landmark left 103 eligible edges and no asserted events, because every
late assertion formed after cycle 60.  This block replaces the calendar
landmark with a per-edge, formation-anchored window:

    window     = the first 20 cycles from the edge's first loop
    landmark   = formation + 19
    population = never-served loop-forming edges with formation <= 90 and no
                 assertion at or before the landmark
    outcome    = asserted by cycle 120

Every eligible edge has a full 20-cycle predictor window.  Edges that form after
cycle 60 are admitted, and a separate gate requires the late cohort to contain
enough edges and events for the claim to include them.

This is a design record.  It spends no seed and has no grant; its runner is
built behind the grant check.

    python -m benchmarks.retention_formation_anchored_prereg --freeze
    python -m benchmarks.retention_formation_anchored_prereg --check
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

ID = "CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1"
MODULE = "benchmarks.retention_formation_anchored_prereg"
RUNNER = "benchmarks.retention_formation_anchored"
FROZEN_ON = "2026-11-12"
SEEDS = list(range(20619101, 20619113))
CYCLES = 120
CAP = 40
WINDOW = 20
LATE_AFTER = 60
MAX_FORMATION = 90
MIN_EDGES = 60
MIN_EVENTS = 20
MIN_LATE_EDGES = 10
MIN_LATE_EVENTS = 3

MODEL_NOTE = (
    "`formation` and `followup` are exact affine transforms: "
    "`followup = (101 - formation) / 120`.  The fitted model uses `followup` "
    "as the single horizon control; `formation_cycle` is descriptive and has "
    "no separate coefficient.  This amendment was recorded before any grant "
    "or seed replay."
)

PREREG = ROOT / "docs" / "retention_formation_anchored_prereg.json"
PAGE = ROOT / "docs" / "RETENTION-FORMATION-ANCHORED-PREREGISTRATION.md"
RESULT = ROOT / "docs" / "retention_formation_anchored.json"
PRIOR = ROOT / "docs" / "retention_incremental.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def record() -> dict:
    return _load(PREREG)


def build_prereg() -> dict:
    return {
        "prereg": ID,
        "kind": "retention_formation_anchored_prereg",
        "status": "FROZEN, NOT RUN",
        "frozen_on": FROZEN_ON,
        "question": (
            "Among never-served loop-forming world edges that formed by cycle 90 "
            "and were not asserted during their first 20 loop cycles, does early "
            "retention measured over that full 20-cycle window predict assertion "
            "by cycle 120, including for edges that formed after cycle 60?"
        ),
        "reference": {
            "source": "docs/retention_incremental.json",
            "status": "VOID, not evidence",
            "prior_population": {
                "never_served": 399,
                "loop_forming": 181,
                "eligible": 103,
                "asserted_events": 0,
                "late_assertions": 16,
                "late_assertions_with_formation_le_60": 0,
            },
            "why_this_block": (
                "The prior fixed cycle-60 landmark left no eligible asserted "
                "events.  This block keeps a full 20-cycle predictor window but "
                "anchors it at each edge's formation, so late-forming loop edges "
                "can enter the population.  No seed, part or row from the prior "
                "block is reused; its result is cited only as the reason for the "
                "new population."
            ),
        },
        "design": {
            "seeds": SEEDS,
            "cells": len(SEEDS),
            "cycles": CYCLES,
            "cap": CAP,
            "window_cycles": WINDOW,
            "late_formation_after": LATE_AFTER,
            "max_formation_cycle": MAX_FORMATION,
            "world": (
                "generate_compositional_world(seed=, cycles=120) with the "
                "PHASE_ACQUISITION schedule and one replay per seed"
            ),
            "population": (
                "never-served world edges with ever_loop=true, "
                "formation_cycle <= 90, and no assertion at or before "
                "formation_cycle + 19"
            ),
            "excluded": (
                "never-served edges that never loop; edges that form after cycle "
                "90; edges asserted during their first 20 loop cycles"
            ),
            "window": (
                "the 20 cycles formation_cycle through formation_cycle + 19, "
                "inclusive; the landmark is formation_cycle + 19"
            ),
            "outcome": (
                "asserted in the final structure at cycle 120, with at least one "
                "outcome cycle after the landmark"
            ),
            "outcome_horizon": (
                "formation_cycle + 20 through 120; this varies by formation, so "
                "followup_cycles/120 is a control and no edge has fewer than 10 "
                "outcome cycles"
            ),
            "freshness": (
                "New seed block 20619101-20619112.  The collision scan over docs "
                "JSON is empty at freeze time; the prior block's seeds and rows "
                "are excluded."
            ),
            "primary_predictors": {
                "early_retention": (
                    "distinct loop cycles in the 20-cycle window divided by 20; "
                    "range [0, 1], with a full window for every eligible edge"
                ),
                "rank20": (
                    "minimum 1-based position in the repaired observer's full "
                    "pre-cap universe over the 20-cycle window"
                ),
                "count20": "direct temporal transition count at the landmark",
                "strength20": (
                    "maximum loop_candidate strength over reported loops in the "
                    "20-cycle window"
                ),
                "formation_descriptive": (
                    "first loop cycle divided by 120; reported but not a fitted "
                    "predictor"
                ),
                "followup": (
                    "number of cycles from formation + 20 through 120, divided "
                    "by 120; the single fitted horizon control"
                ),
            },
            "late_cohort": (
                "eligible edges with formation_cycle > 60.  The model reports a "
                "separate late-cohort estimate, but the verdict is the frozen "
                "all-cohort primary plus the late-representation gate."
            ),
            "reverse_time": {
                "late_retention": (
                    "distinct loop cycles from formation + 20 through 120, "
                    "divided by the available outcome cycles"
                ),
                "assertion_cycle": (
                    "first cycle the edge appears in structure_edges after the "
                    "landmark; required for every asserted edge and must be "
                    "greater than formation_cycle + 19"
                ),
                "purpose": (
                    "If post-landmark retention carries the same association as "
                    "the first-20-cycle predictor, the result is concurrent or "
                    "reverse-time, not evidence that early retention precedes "
                    "assertion."
                ),
            },
        },
        "model": {
            "family": "binary logistic regression",
            "primary_formula": (
                "logit P(asserted by 120) = b0 + b_rank*z(log2(rank20)) "
                "+ b_count*z(count20) + b_strength*z(strength20) "
                "+ b_followup*z(followup) "
                "+ b_early*z(early_retention) + seed fixed effects"
            ),
            "reverse_formula": (
                "same controls, with late_retention replacing early_retention"
            ),
            "identification": MODEL_NOTE,
            "estimator": "Firth penalized likelihood",
            "standardization": "complete-case mean and population SD",
            "seed": "twelve-level fixed effect, first seed as reference",
            "selection": "none",
        },
        "inference": {
            "primary": (
                "Firth Wald 95% interval for the early-retention odds ratio per "
                "1 SD on the full eligible population.  This is the single "
                "primary criterion."
            ),
            "late_cohort": (
                "The same model is reported for eligible edges with formation > "
                "60.  It is descriptive and does not replace the all-cohort "
                "primary or the late-representation gate."
            ),
            "secondary": (
                "Rank, count, strength and follow-up are reported with "
                "intervals; formation is descriptive, and late retention is the "
                "reverse-time diagnostic."
            ),
            "alpha": 0.05,
            "multiplicity": (
                "one primary coefficient; the late-cohort and reverse-time "
                "models are diagnostics, not additional primary tests"
            ),
            "no_causal_claim": (
                "Observational formation-anchored model.  A null post-landmark "
                "result narrows reverse timing; it does not identify a mechanism."
            ),
        },
        "criteria": [
            {"id": "P1", "name": "early-retention direction",
             "test": "all-cohort early-retention OR > 1"},
            {"id": "P2", "name": "early-retention interval",
             "test": "all-cohort early-retention 95% CI lower bound > 1"},
            {"id": "P3", "name": "gates",
             "test": "all confirmatory gates pass, including late representation"},
            {"id": "R1", "name": "reverse-time diagnostic",
             "test": "late-retention OR <= 1 or its 95% CI includes 1"},
        ],
        "verdicts": {
            "CONFIRMED": "P1-P3 pass and R1 passes.",
            "CONFIRMED, TEMPORALLY AMBIGUOUS": (
                "P1-P3 pass but late retention also has an OR > 1 with a lower "
                "95% bound > 1; no temporal-direction claim."
            ),
            "DIRECTIONAL ONLY": "P1 and P3 pass, but the early interval includes 1.",
            "NOT CONFIRMED": "The early-retention OR is at or below 1.",
            "VOID": "A gate fails; no coefficient is read.",
        },
        "gates": {
            "M1_population": (
                "at least 60 eligible edges and 20 asserted events; one row per "
                "seed-edge"
            ),
            "M2_window_complete": (
                "every eligible row formed by 90, has no assertion at or before "
                "its landmark, and has finite early_retention in a full 20-cycle "
                "window"
            ),
            "M3_rank_coverage": "at least 95% of eligible edges have a finite rank20",
            "M4_seed_levels": "all twelve seeds contribute rows",
            "M5_convergence": (
                "both the primary and reverse Firth fits converge with finite "
                "coefficients"
            ),
            "M6_complete": (
                "every fitted row has finite count20, strength20 and followup"
            ),
            "M7_reverse_onset": (
                "every asserted eligible row has a finite assertion_cycle after "
                "its landmark; every non-asserted eligible row has no assertion_cycle"
            ),
            "M8_no_collision": "the seed block is collision-free at freeze and check",
            "M9_late_representation": (
                "at least 10 eligible edges and 3 asserted events have "
                "formation_cycle > 60; otherwise the late-forming claim is VOID"
            ),
        },
        "amendments": [{
            "date": "2026-11-12",
            "kind": "model-identification",
            "before_grant": True,
            "change": (
                "Removed `formation` from the fitted predictors and kept "
                "`followup` as the single horizon control."
            ),
            "reason": MODEL_NOTE,
        }],
        "sample_size": {
            "planned_seeds": len(SEEDS),
            "minimum_edges": MIN_EDGES,
            "minimum_events": MIN_EVENTS,
            "minimum_late_edges": MIN_LATE_EDGES,
            "minimum_late_events": MIN_LATE_EVENTS,
            "power_calculation": (
                "none.  Twelve fresh seeds test whether the formation-anchored "
                "population has both enough events and enough late-cohort "
                "representation; the block does not reuse the prior point estimate."
            ),
        },
        "authorisation": {
            "required": True,
            "granted": False,
            "document": None,
            "note": (
                "No grant is recorded.  This module freezes the design only; it "
                "must not run a cell."
            ),
        },
        "runner": {
            "built": True,
            "planned_module": RUNNER,
            "cells_run": 0,
            "measure_command": (
                "python -m benchmarks.retention_formation_anchored --measure"
            ),
            "write_command": (
                "python -m benchmarks.retention_formation_anchored --finish"
            ),
            "note": (
                "The runner is built behind the grant check.  No cell has run "
                "and no result exists."
            ),
        },
        "result": RESULT.relative_to(ROOT).as_posix(),
        "not_evidence": (
            "A preregistration, not a result.  It spends no seed and makes no "
            "capability, causal, retention or general engine claim.  The prior "
            "block's VOID is not evidence for this design; the 20-cycle window "
            "and the cycle-90 formation ceiling are design choices, and a "
            "different window or ceiling is a different block."
        ),
    }


def _validate(body: dict) -> list[str]:
    found: list[str] = []
    if body.get("prereg") != ID:
        found.append("prereg id")
    if body.get("status") not in (
            "FROZEN, NOT RUN", "GRANTED, NOT RUN", "FROZEN, RUN"):
        found.append("status")
    design = body.get("design") or {}
    if design.get("seeds") != SEEDS:
        found.append("seed block")
    if design.get("cycles") != CYCLES or design.get("cap") != CAP:
        found.append("cycles or cap")
    if design.get("window_cycles") != WINDOW:
        found.append("window")
    if design.get("max_formation_cycle") != MAX_FORMATION:
        found.append("formation ceiling")
    if design.get("late_formation_after") != LATE_AFTER:
        found.append("late cutoff")
    if [row.get("id") for row in body.get("criteria") or []] != [
            "P1", "P2", "P3", "R1"]:
        found.append("criteria")
    if set(body.get("verdicts") or {}) != {
            "CONFIRMED", "CONFIRMED, TEMPORALLY AMBIGUOUS", "DIRECTIONAL ONLY",
            "NOT CONFIRMED", "VOID"}:
        found.append("verdict vocabulary")
    model = body.get("model") or {}
    if model.get("identification") != MODEL_NOTE:
        found.append("model identification")
    if "b_formation" in str(model.get("primary_formula", "")):
        found.append("formation is still a fitted predictor")
    amendments = body.get("amendments") or []
    if not amendments or amendments[0].get("before_grant") is not True:
        found.append("model amendment")
    auth = body.get("authorisation") or {}
    if auth.get("granted") not in (False, True):
        found.append("grant flag")
    if auth.get("granted") is True:
        if not auth.get("granted_on") or not auth.get("document") or not auth.get("quote"):
            found.append("grant is incomplete")
    runner = body.get("runner") or {}
    if runner.get("built") is not True or runner.get("planned_module") != RUNNER:
        found.append("runner state")
    expected_cells = len(SEEDS) if body.get("status") == "FROZEN, RUN" else 0
    if runner.get("cells_run") != expected_cells:
        found.append("cells run")
    if body.get("status") == "FROZEN, RUN" and auth.get("granted") is not True:
        found.append("run without grant")
    if body.get("result") != RESULT.relative_to(ROOT).as_posix():
        found.append("result path")
    if engine_stamp.missing(body):
        found.append("stamp: %r" % (engine_stamp.missing(body),))
    return found


def render(body: dict) -> str:
    d = body["design"]
    ref = body["reference"]
    lines = [
        "# Retention formation-anchored — preregistration",
        "",
        "Generated from `%s` by "
        "`python -m benchmarks.retention_formation_anchored_prereg --freeze`. "
        "Do not edit by hand." % PREREG.relative_to(ROOT).as_posix(),
        "",
        "**Status: `%s`.** This is the frozen preregistration." % body["status"],
        "",
        "## Question",
        "",
        body["question"],
        "",
        "## Why this block exists",
        "",
        "`CONFIRMATORY-RETENTION-INCREMENTAL-1` fixed a calendar landmark at "
        "cycle 60.  It found **%d** eligible edges and **%d** asserted events: "
        "all **%d** late assertions in its never-served set formed after cycle "
        "60.  That block is **`VOID`** and is not reused here." % (
            ref["prior_population"]["eligible"],
            ref["prior_population"]["asserted_events"],
            ref["prior_population"]["late_assertions"]),
        "",
        ref["why_this_block"],
        "",
        "## Design",
        "",
        "- Seeds: **%s** (twelve fresh seeds)." % ", ".join(
            str(seed) for seed in d["seeds"]),
        "- **%d** cycles, cap **%d**, PHASE_ACQUISITION, one replay per seed."
        % (d["cycles"], d["cap"]),
        "- **Formation-anchored window:** **%d** cycles, from formation through "
        "formation + %d." % (d["window_cycles"], d["window_cycles"] - 1),
        "- Population: %s." % d["population"],
        "- Excluded: %s." % d["excluded"],
        "- Outcome: %s." % d["outcome"],
        "- Horizon control: `followup`; `formation` is descriptive.",
        "",
        "The window is the point of the design.  Every eligible edge has the "
        "same **20-cycle** predictor window measured from its own formation, so "
        "an edge that forms at cycle 61 or 90 is not excluded for being late.  "
        "The outcome horizon varies with formation; `followup/120` is a control, "
        "and the cycle-90 ceiling leaves at least 10 outcome cycles.",
        "",
        "## Primary model",
        "",
        "```text",
        body["model"]["primary_formula"],
        "```",
        "",
        "Early retention is the distinct loop cycles in the first 20 cycles "
        "divided by 20.  It is bounded to [0, 1].  Rank, count and strength are "
        "measured in the same window.  Follow-up is the single fitted horizon "
        "control; formation is descriptive.  The estimator is Firth penalized "
        "likelihood with twelve seed fixed effects.",
        "",
        "**Model identification.** %s" % body["model"]["identification"],
        "",
        "## Late cohort",
        "",
        "Edges with `formation_cycle > 60` are the late cohort.  The same model "
        "is reported for that cohort descriptively.  Gate **M9** requires at "
        "least **%d** eligible late edges and **%d** asserted late events; if it "
        "fails, the block is `VOID` and no late-forming claim is read." % (
            d["late_cohort"] if isinstance(d["late_cohort"], int) else MIN_LATE_EDGES,
            MIN_LATE_EVENTS),
        "",
        "## Reverse-time control",
        "",
        "The reverse model replaces early retention with **late retention**, "
        "measured from `formation + 20` through cycle 120 and divided by the "
        "available outcome cycles.  The first assertion cycle must be after the "
        "landmark.  A positive late-retention result labels the block "
        "`CONFIRMED, TEMPORALLY AMBIGUOUS`; it does not rescue the primary.",
        "",
        "## Criteria and verdicts",
        "",
        "| Criterion | Test |",
        "| --- | --- |",
    ]
    for row in body["criteria"]:
        lines.append("| `%s` %s | %s |" % (row["id"], row["name"], row["test"]))
    lines += [
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
        "- Minimum asserted events: **%d**." % body["sample_size"]["minimum_events"],
        "- Minimum late-cohort edges: **%d**." % body["sample_size"]["minimum_late_edges"],
        "- Minimum late-cohort events: **%d**." % body["sample_size"]["minimum_late_events"],
        "- Power calculation: %s" % body["sample_size"]["power_calculation"],
        "",
    ]
    if body.get("amendments"):
        lines += ["## Amendments", "",
                  "| Date | Kind | Change |", "| --- | --- | --- |"]
        for row in body["amendments"]:
            lines.append("| %s | `%s` | %s |" % (
                row["date"], row["kind"], row["change"]))
        lines += [""]
    lines += [
        "## Authorisation",
        "",
    ]
    auth = body.get("authorisation") or {}
    if auth.get("granted"):
        lines += [
            "Granted on **%s** in `%s`." % (
                auth.get("granted_on"), auth.get("document")),
        ]
        if auth.get("quote"):
            lines += ["", "Run authorisation:", "", "> %s" % auth["quote"]]
        lines += [
            "The runner is built behind the grant check.",
        ]
        if body.get("status") == "FROZEN, RUN":
            lines += ["The twelve cells have run; the result is `%s`."
                      % body.get("result")]
        else:
            lines += ["No cell has run."]
    else:
        lines += [
            "No grant is recorded.  The block is `FROZEN, NOT RUN`; the runner "
            "is built behind the grant check but no cell has run.  It must not "
            "be cited as evidence until it has a dated grant, a run artifact and "
            "a verdict from its own gates.",
        ]
    lines += [
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
    print("froze %s" % PREREG.relative_to(ROOT).as_posix())
    return 0


def problems(body: dict | None = None) -> list[str]:
    body = _load(PREREG) if body is None else body
    found = _validate(body)
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(body):
        found.append("page stale")
    from benchmarks.presence_cap_experiment import seed_collisions
    if seed_collisions(SEEDS, allow=(PREREG, RESULT)):
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
    print("retention formation-anchored: %s, seeds %d, cells %d"
          % (ID, len(SEEDS), len(SEEDS)))
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
