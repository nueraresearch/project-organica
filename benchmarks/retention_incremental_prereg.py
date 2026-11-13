"""CONFIRMATORY-RETENTION-INCREMENTAL-1.

A frozen preregistration for a fresh-seed test of pre-assertion retention.

The post-hoc persistence extension found that loop retention survived rank,
count, strength and first-formation timing on the same twelve seeds that
produced the confirmatory loop-only model.  That result is observational and
the retention window runs to cycle 120, so it cannot separate retention before
assertion from retention after assertion.

This block fixes a cycle-60 landmark before the run:

    population = never-served loop-forming world edges with formation <= 60
                 and not asserted by cycle 60
    outcome    = asserted in the final structure at cycle 120
    primary    = early retention, loop cycles from formation through cycle 60
                 divided by the available cycles in that window

Rank, direct count and strength are also measured through cycle 60.  A separate
late-retention model uses only cycles 61-120 as the reverse-time diagnostic.  If
late retention predicts as strongly as early retention, the block is labelled
temporally ambiguous rather than read as evidence that retention precedes
assertion.

No seed is spent by this module.  It freezes the record and renders the page.

    python -m benchmarks.retention_incremental_prereg --freeze
    python -m benchmarks.retention_incremental_prereg --check
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

ID = "CONFIRMATORY-RETENTION-INCREMENTAL-1"
MODULE = "benchmarks.retention_incremental"
FROZEN_ON = "2026-11-12"
SEEDS = list(range(20618101, 20618113))
CYCLES = 120
CAP = 40
LANDMARK = 60
MIN_EDGES = 60
MIN_EVENTS = 20

PREREG = ROOT / "docs" / "retention_incremental_prereg.json"
PAGE = ROOT / "docs" / "RETENTION-INCREMENTAL-PREREGISTRATION.md"
RESULT = ROOT / "docs" / "retention_incremental.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def record() -> dict:
    return _load(PREREG)


def build_prereg() -> dict:
    return {
        "prereg": ID,
        "kind": "retention_incremental_prereg",
        "status": "FROZEN, NOT RUN",
        "frozen_on": FROZEN_ON,
        "question": (
            "Among never-served loop-forming world edges that formed by cycle 60 "
            "and were not yet asserted at cycle 60, does retention measured only "
            "through cycle 60 predict final assertion at cycle 120 beyond rank, "
            "count, strength and formation timing?"
        ),
        "reference": {
            "source": "docs/loop_persistence_assertion_model.json",
            "status": "POST-HOC, not confirmatory",
            "n": 177,
            "events": 77,
            "retention_or": 8.022351705444482,
            "retention_ci95": [2.5719, 25.019],
            "controlled_retention_or": 14.683359489693045,
            "controlled_retention_ci95": [3.677, 58.643],
            "controlled_formation_or": 6.252,
            "controlled_count_or": 0.714,
            "note": (
                "The post-hoc model used the full 120-cycle retention window. "
                "This block tests a stricter landmark predictor, not a direct "
                "replication of that coefficient."
            ),
        },
        "design": {
            "seeds": SEEDS,
            "cells": len(SEEDS),
            "cycles": CYCLES,
            "cap": CAP,
            "landmark_cycle": LANDMARK,
            "world": (
                "generate_compositional_world(seed=, cycles=120) with the "
                "PHASE_ACQUISITION schedule and one replay per seed"
            ),
            "population": (
                "world edges with zero direct served windows, ever_loop=true, "
                "formation_cycle <= 60, and no assertion at or before cycle 60"
            ),
            "excluded": (
                "edges never served but not loop-forming; edges whose first loop "
                "forms after cycle 60; edges asserted at or before cycle 60"
            ),
            "outcome": "asserted in the final structure at cycle 120",
            "freshness": (
                "The collision scan over docs JSON is empty at freeze time. No "
                "seed in this block has been replayed before the freeze."
            ),
            "primary_predictors": {
                "early_retention": (
                    "loop cycles with cycle <= 60, from formation through 60, "
                    "divided by (61 - formation_cycle); range [0, 1]"
                ),
                "rank60": (
                    "minimum 1-based position in the repaired observer's full "
                    "pre-cap universe over cycles 1-60"
                ),
                "count60": "direct temporal transition count at cycle 60",
                "strength60": (
                    "maximum loop_candidate strength over reported loops ending "
                    "at or before cycle 60"
                ),
                "formation": "first loop cycle divided by 120",
            },
            "reverse_time": {
                "late_retention": (
                    "loop cycles with 61 <= cycle <= 120, divided by 60"
                ),
                "late_strength": (
                    "maximum loop_candidate strength over reported loops ending "
                    "after cycle 60"
                ),
                "assertion_cycle": (
                    "first cycle the edge appears in structure_edges on the "
                    "observer's current candidate set; required for every asserted "
                    "edge and must be greater than 60"
                ),
                "purpose": (
                    "If late retention carries the same association as early "
                    "retention, the result is concurrent or reverse-time, not "
                    "evidence that retention precedes assertion."
                ),
            },
        },
        "model": {
            "family": "binary logistic regression",
            "primary_formula": (
                "logit P(asserted at 120) = b0 + b_rank*z(log2(rank60)) "
                "+ b_count*z(count60) + b_formation*z(formation) "
                "+ b_strength*z(strength60) + b_early*z(early_retention) "
                "+ seed fixed effects"
            ),
            "reverse_formula": (
                "same controls, with late_retention replacing early_retention"
            ),
            "estimator": "Firth penalized likelihood",
            "standardization": "complete-case mean and population SD",
            "seed": "twelve-level fixed effect, first seed as reference",
            "interactions": "none",
            "selection": "none",
        },
        "inference": {
            "primary": (
                "Firth Wald 95% interval for the early-retention odds ratio per "
                "1 SD. This is the single primary criterion."
            ),
            "secondary": (
                "Rank, count, formation and strength are reported with intervals; "
                "late retention is the reverse-time diagnostic and does not "
                "rescue a failed primary criterion."
            ),
            "alpha": 0.05,
            "multiplicity": (
                "one primary coefficient; the reverse-time model is a diagnostic, "
                "not a second primary test"
            ),
            "no_causal_claim": (
                "Observational landmark model. A negative late-retention result "
                "narrows reverse timing; it does not identify a mechanism."
            ),
        },
        "criteria": [
            {"id": "P1", "name": "early-retention direction",
             "test": "early-retention OR > 1"},
            {"id": "P2", "name": "early-retention interval",
             "test": "early-retention 95% CI lower bound > 1"},
            {"id": "P3", "name": "gates", "test": "all confirmatory gates pass"},
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
                "at least %d eligible loop-forming never-served edges and %d "
                "asserted events; one row per seed-edge" % (MIN_EDGES, MIN_EVENTS)
            ),
            "M2_landmark_complete": (
                "every eligible row has formation_cycle <= 60, is not asserted "
                "at or before 60, and has finite early_retention"
            ),
            "M3_rank_coverage": "at least 95% of eligible edges have a finite rank60",
            "M4_seed_levels": "all twelve seeds contribute rows",
            "M5_convergence": (
                "both the primary and reverse Firth fits converge with finite "
                "coefficients"
            ),
            "M6_complete": "every fitted row has finite count60 and strength60",
            "M7_reverse_onset": (
                "every asserted row has a finite assertion_cycle > 60; every "
                "non-asserted row has no assertion_cycle"
            ),
            "M8_no_collision": "the seed block is collision-free at freeze and check",
        },
        "sample_size": {
            "planned_seeds": len(SEEDS),
            "minimum_edges": MIN_EDGES,
            "minimum_events": MIN_EVENTS,
            "power_calculation": (
                "none. Twelve fresh seeds are used to test a narrower landmark "
                "claim, not to power the post-hoc point estimate."
            ),
        },
        "authorisation": {
            "required": True,
            "granted": False,
            "document": None,
            "note": (
                "No grant is recorded. This module registers the design only; it "
                "must not run a cell."
            ),
        },
        "runner": {
            "built": True,
            "planned_module": MODULE,
            "cells_run": 0,
            "measure_command": (
                "python -m benchmarks.retention_incremental --measure"
            ),
            "write_command": (
                "python -m benchmarks.retention_incremental --finish"
            ),
        },
        "result": RESULT.relative_to(ROOT).as_posix(),
        "not_evidence": (
            "A preregistration, not a result. It spends no seed and makes no "
            "capability, causal, retention or general engine claim. The landmark "
            "is one choice of cutoff; a different cutoff is a different design."
        ),
    }


def _validate(body: dict) -> list[str]:
    found: list[str] = []
    if body.get("prereg") != ID:
        found.append("prereg id")
    if body.get("status") not in ("FROZEN, NOT RUN", "GRANTED, NOT RUN", "FROZEN, RUN"):
        found.append("status")
    design = body.get("design") or {}
    if design.get("seeds") != SEEDS:
        found.append("seed block")
    if design.get("cycles") != CYCLES or design.get("cap") != CAP:
        found.append("cycles or cap")
    if design.get("landmark_cycle") != LANDMARK:
        found.append("landmark")
    if [row.get("id") for row in body.get("criteria") or []] != [
            "P1", "P2", "P3", "R1"]:
        found.append("criteria")
    if set(body.get("verdicts") or {}) != {
            "CONFIRMED", "CONFIRMED, TEMPORALLY AMBIGUOUS", "DIRECTIONAL ONLY",
            "NOT CONFIRMED", "VOID"}:
        found.append("verdict vocabulary")
    auth = body.get("authorisation") or {}
    if auth.get("granted") not in (False, True):
        found.append("grant flag")
    if auth.get("granted") is True:
        if not auth.get("granted_on") or not auth.get("document") or not auth.get("quote"):
            found.append("grant is incomplete")
    runner = body.get("runner") or {}
    if runner.get("built") is not True or runner.get("planned_module") != MODULE:
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
        "# Retention incremental — preregistration",
        "",
        "Generated from `%s` by "
        "`python -m benchmarks.retention_incremental_prereg --freeze`. "
        "Do not edit by hand." % PREREG.relative_to(ROOT).as_posix(),
        "",
        "**Status: `%s`.** This is the frozen preregistration." % body["status"],
    ]
    auth = body.get("authorisation") or {}
    if auth.get("granted"):
        lines += ["", "The owner's grant is recorded in `%s`, dated %s." % (
            auth.get("document"), auth.get("granted_on"))]
        if body.get("status") == "FROZEN, RUN":
            lines += ["The twelve cells have run; the result is `%s`."
                      % body.get("result")]
        else:
            lines += ["No cell has run."]
    else:
        lines += ["", "No grant is recorded. The design must not be cited as "
                  "evidence until it has a dated grant, a run artifact and a "
                  "verdict from its own gates."]
    lines += [
        "",
        "## Question",
        "",
        body["question"],
        "",
        "## Design",
        "",
        "- Seeds: **%s** (twelve fresh seeds)." % ", ".join(
            str(seed) for seed in d["seeds"]),
        "- **%d** cycles, cap **%d**, PHASE_ACQUISITION, one replay per seed."
        % (d["cycles"], d["cap"]),
        "- **Landmark:** cycle **%d**." % d["landmark_cycle"],
        "- Population: %s." % d["population"],
        "- Excluded: %s." % d["excluded"],
        "- Outcome: %s." % d["outcome"],
        "",
        "The landmark is the point of the design. All primary predictors are "
        "measured through cycle 60; the outcome is read at cycle 120. Edges that "
        "were already asserted at the landmark are excluded, so the primary "
        "comparison is prospective rather than a full-run association.",
        "",
        "## Primary model",
        "",
        "```text",
        body["model"]["primary_formula"],
        "```",
        "",
        "Early retention is loop cycles from formation through cycle 60 divided "
        "by the available cycles in that window. It is bounded to [0, 1]. Rank, "
        "count, strength and formation are also landmark-capped. The estimator "
        "is Firth penalized likelihood with twelve seed fixed effects.",
        "",
        "## Reverse-time control",
        "",
        "The reverse model replaces early retention with **late retention**, the "
        "loop cycles in cycles 61-120 divided by 60. The first assertion cycle is "
        "recorded for every asserted edge and must be greater than 60.",
        "",
        "The diagnostic is deliberately asymmetric: a positive early-retention "
        "result with a null late-retention result narrows reverse timing; a "
        "positive late-retention result means the association may be concurrent "
        "or post-assertion. It does not rescue a failed primary criterion.",
        "",
        "## Reference, not replication",
        "",
        "| Quantity | Post-hoc full-run model | This landmark block |",
        "| --- | ---: | ---: |",
        "| Loop-forming edges | **%d** | see result artifact |" % ref["n"],
        "| Asserted events | **%d** | see result artifact |" % ref["events"],
        "| Retention OR | **%.2f** | see result artifact |" % ref["retention_or"],
        "| Controlled retention OR | **%.2f** | see result artifact |"
        % ref["controlled_retention_or"],
        "",
        "The post-hoc result is `%s`. This block tests a stricter landmark "
        "predictor, so its coefficient is not expected to equal the full-run "
        "coefficient." % ref["status"],
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
        "- Power calculation: %s" % body["sample_size"]["power_calculation"],
        "",
        "## Authorisation",
        "",
    ]
    if body["authorisation"].get("granted"):
        lines += [
            "Granted on **%s** in `%s`." % (
                body["authorisation"].get("granted_on"),
                body["authorisation"].get("document")),
            "The twelve cells have run; the result is `%s`." % body["result"],
        ]
    else:
        lines += [
            "No grant is recorded. The block is `FROZEN, NOT RUN`; the runner is "
            "built behind the grant check and no cell has run. The design must not "
            "be cited as evidence until it has a dated grant, a run artifact and a "
            "verdict from its own gates.",
        ]
    lines += [
        "",
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
    print("retention incremental prereg: %s, seeds %d, cells %d"
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
