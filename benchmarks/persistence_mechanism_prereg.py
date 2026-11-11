"""PERSISTENCE-MECHANISM-1: the mechanism follow-up T1b's decision names, frozen and unrun.

T1b returned ``PERSISTENCE CONTRIBUTES``: removing carried temporal counts removed served
world edges on every seed at cap 112. Its decision names the next question -- pursue the
persistence mechanism (decay, floor, denominator) -- and this block separates the two
mechanisms that can carry that contribution:

* the temporal decay factor: shipped 0.95 versus no decay 1.0; and
* the read/admission floor: shipped ``PREDICTION_MIN_COUNT = 5`` versus 1.

The design is a 2 x 2 factorial on the shipped arm, at cap 112, on six fresh seeds and 120
cycles. The denominator reading is fixed by G4, not re-opened: P is the denominator and a zero
``S_ever`` is a measured count. The block is a preregistration only. No runner exists, no grant
is recorded, and no cell may run.

    ./.venv/bin/python -m benchmarks.persistence_mechanism_prereg --freeze
    ./.venv/bin/python -m benchmarks.persistence_mechanism_prereg --check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks import presence_cap_experiment as cap

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "persistence_mechanism_prereg.json"
PAGE = ROOT / "docs" / "PERSISTENCE-MECHANISM-PREREGISTRATION.md"
RUN = ROOT / "docs" / "persistence_mechanism_run.json"
ARM = ROOT / "benchmarks" / "persistence_mechanism_arm.py"
T1B_RESULT = ROOT / "docs" / "T1B-PERSISTENCE-OFF-RESULT.md"

ID = "PERSISTENCE-MECHANISM-1"
STATUS = "FROZEN, NOT RUN"
FROZEN_ON = "2026-11-11"
SEEDS = [20612301, 20612302, 20612303, 20612304, 20612305, 20612306]
BOOTSTRAP = 20612307
CAP = 112
CYCLES = 120
T1B_DECISION = ("Pursue the persistence mechanism (decay, floor, denominator); the cap arm "
                "does not answer this question.")

ARMS = {
    "shipped": {
        "decay_factor": 0.95,
        "read_floor": 5,
        "description": "the shipped decay factor and the shipped read floor",
    },
    "no_decay": {
        "decay_factor": 1.0,
        "read_floor": 5,
        "description": "no temporal decay, shipped read floor",
    },
    "floor_one": {
        "decay_factor": 0.95,
        "read_floor": 1,
        "description": "shipped decay, read floor lowered to 1",
    },
    "no_decay_floor_one": {
        "decay_factor": 1.0,
        "read_floor": 1,
        "description": "no temporal decay and read floor lowered to 1",
    },
}

GATES = (
    "G1_build",
    "G2_world",
    "G3_treatments_live",
    "G4_denominator",
    "G5_seed_axis",
    "G6_determinism",
    "G7_cells",
)

VERDICTS = (
    "VOID",
    "BOTH MECHANISMS CARRY PERSISTENCE",
    "DECAY CARRIES PERSISTENCE",
    "READ FLOOR CARRIES PERSISTENCE",
    "NO MECHANISM DETECTED",
)


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def build() -> dict:
    return {
        "created": FROZEN_ON,
        "prereg": ID,
        "status": STATUS,
        "frozen_on": FROZEN_ON,
        "no_cells_run": True,
        "question": (
            "At cap 112, which persistence mechanism carries T1b's served-edge contribution: "
            "the temporal decay factor, the read/admission floor, or both?"
        ),
        "program": {
            "source": "T1B-PERSISTENCE-OFF",
            "decision_quote": T1B_DECISION,
            "relationship": (
                "T1b returned PERSISTENCE CONTRIBUTES: removing carried temporal counts removed "
                "served world edges on every seed at cap 112. Its decision says to pursue the "
                "persistence mechanism (decay, floor, denominator). This block follows that "
                "decision by separating decay from the read floor in one factorial. It does not "
                "re-read T1 or T1b, and it does not re-open T1b's corrected denominator reading."
            ),
        },
        "hypothesis": (
            "If carried counts reach the serving path through decay and the read floor, then "
            "removing decay and lowering the read floor should each increase served world edges "
            "at the same cap, world and seed; the floor effect is expected to be larger because "
            "T1b's zero cells are threshold-limited."
        ),
        "engine": {
            "version": "0.15.0",
            "edit": "none",
            "cap": CAP,
            "pin": "the 0.15.0 pin verified by benchmarks.landing_0_15_0 --check",
            "why_this_build": "0.15.0 is the shipped build and the build T1b ran at cap 112; the follow-up must hold it fixed.",
        },
        "design": {
            "arms": list(ARMS),
            "factors": {
                "decay_factor": {"shipped": 0.95, "no_decay": 1.0},
                "read_floor": {"shipped": 5, "one": 1},
            },
            "seeds": list(SEEDS),
            "bootstrap": BOOTSTRAP,
            "cap": CAP,
            "cycles": CYCLES,
            "cells": len(ARMS) * len(SEEDS),
            "cells_arithmetic": "4 arms x 6 seeds = 24 cells",
            "world": "the compositional world family of PHASE_ACQUISITION at cap 112 and 120 cycles",
            "pairing": "all four arms of a seed share the seed-determined world and stimulus; only the decay factor and read floor differ",
            "freshness": (
                "20612301-20612307 was scanned against every docs JSON at freeze and is unused; "
                "the seventh integer is the bootstrap seed and is not a world seed. The record and "
                "page are the only allow-listed new documents."
            ),
            "seed_axis": "six fresh seeds are a direction, not an effect size; no seed is dropped or added after the freeze",
        },
        "arms": ARMS,
        "mechanism": {
            "changes": (
                "An in-process SleepService/MemoryService subclass applies the arm's decay factor "
                "(shipped 0.95 -> no-decay 1.0) at the engine's temporal-decay call and sets the "
                "arm's PREDICTION_MIN_COUNT (shipped 5 -> floor 1). The engine files, pin and cap "
                "are unchanged."
            ),
            "shipped_reference": {"decay_factor": 0.95, "read_floor": 5},
            "treatments": {
                "no_decay": "decay factor 1.0; every temporal count is carried without decay",
                "floor_one": "PREDICTION_MIN_COUNT 5 -> 1; a count-1 transition is admissible",
                "no_decay_floor_one": "both changes in one arm; the interaction is reported",
            },
            "preserves": [
                "the shipped 0.15.0 build, its pin and cap 112",
                "the seed-determined world and stimulus",
                "the prediction budget and its 56-transition floor",
                "every other threshold, ranking key and memory table",
            ],
            "does_not": [
                "edit an engine file",
                "delete temporal rows",
                "change the cap or the denominator reading",
                "re-read T1 or T1b",
            ],
        },
        "endpoints": [
            {"stage": "P", "definition": "present world edges: the denominator of every share", "role": "denominator"},
            {"stage": "S_ever", "definition": "served world edges: the union of every served window intersect the world, counted once; zero is measured", "role": "primary"},
            {"stage": "A_W", "definition": "asserted world edges at the end of the run", "role": "secondary"},
            {"stage": "C", "definition": "constructed candidates: the pre-cap universe intersect the world", "role": "reported"},
        ],
        "effects": {
            "primary_endpoint": "S_ever",
            "definitions": {
                "decay_effect": "S_ever(no_decay, floor 5) - S_ever(shipped), paired by seed",
                "floor_effect": "S_ever(floor_one, decay 0.95) - S_ever(shipped), paired by seed",
                "interaction": "(S_ever(no_decay_floor_one) - S_ever(no_decay)) - (S_ever(floor_one) - S_ever(shipped)), paired by seed",
            },
            "bar": {
                "margin": 10,
                "positive_seeds": 5,
                "seeds": 6,
                "confidence": 95,
                "resamples": 10000,
                "rule": "an effect passes when its mean paired difference is at least 10 edges, at least 5 of 6 seeds are positive, and the paired 95% lower bound is above zero",
                "provenance": "the ten-edge margin and five-of-six rule are imported unchanged from T1b; T1b's observed differences do not set this block's bar",
            },
            "interaction_role": "reported, not required for a main-effect verdict; a non-zero interaction is not a third mechanism",
        },
        "gates": {
            "G1_build": "all 24 cells run the shipped 0.15.0 build at cap 112 with one sha256 and no engine edit; a mixed build or an edited engine is VOID",
            "G2_world": "each seed's world digest and present fingerprint are identical across all four arms and the six seeds are the frozen block; a differing world is VOID",
            "G3_treatments_live": "each arm records its designed decay factor and read floor (0.95/5, 1.0/5, 0.95/1, 1.0/1); an arm whose configured factor or floor is the control value is TREATMENT NOT LIVE, not a null",
            "G4_denominator": "P is non-zero in every cell; S_ever is a measured count, so a zero S_ever is read as zero served edges; a zero P is not measurable and VOIDS the block",
            "G5_seed_axis": "the six shipped cells hold at least three distinct (S_ever, A_W) pairs; one outcome repeated six times is not a seed axis",
            "G6_determinism": "a fresh-process rerun of seed 20612301 reproduces its four-arm stage rows exactly",
            "G7_cells": "exactly 24 cells, four arms x six seeds, with no extra seed, cap, cycle or arm",
        },
        "decision_table": [
            {
                "condition": "any gate fails",
                "verdict": "VOID",
                "reading": "the block is unrun or non-measurable and the failed gate names what did not happen",
                "decision": "record VOID; fix the harness and register a new block; read no mechanism",
            },
            {
                "condition": "gates pass; both the decay effect and the read-floor effect meet the bar",
                "verdict": "BOTH MECHANISMS CARRY PERSISTENCE",
                "reading": "removing decay and lowering the floor each add served world edges; the interaction is reported but is not required",
                "decision": "pursue both mechanisms jointly in a mechanism block; no adoption or capability claim follows",
            },
            {
                "condition": "gates pass; the decay effect meets the bar and the read-floor effect does not",
                "verdict": "DECAY CARRIES PERSISTENCE",
                "reading": "the decay factor is the live lever at cap 112; the floor does not move the endpoint on this block",
                "decision": "isolate decay levels next; do not treat the floor as the conversion lever",
            },
            {
                "condition": "gates pass; the read-floor effect meets the bar and the decay effect does not",
                "verdict": "READ FLOOR CARRIES PERSISTENCE",
                "reading": "the read/admission floor is the live lever at cap 112; decay does not move the endpoint on this block",
                "decision": "isolate floor values and precision next; do not treat decay as the conversion lever",
            },
            {
                "condition": "gates pass; neither effect meets the bar",
                "verdict": "NO MECHANISM DETECTED",
                "reading": "neither contrast locates the persistence contribution at this cap and world family",
                "decision": "make no mechanism claim; the next probe is the in-cycle construction or admission stage, or a larger fresh seed axis, not another re-read",
            },
        ],
        "prediction": {
            "statement": (
                "Both main effects on S_ever are positive, and the read-floor effect is larger "
                "than the decay effect; the interaction is not predicted to be necessary."
            ),
            "because": (
                "T1b's zero cells are threshold-limited: no world edge reaches 5 within-cycle "
                "observations after the reset, so lowering the read floor has a direct route to "
                "served edges. Decay is the other carried-count mechanism and should add a smaller "
                "positive effect at cap 112."
            ),
            "falsifier": (
                "Either effect at or below the bar, a negative paired mean, a failed treatment-live "
                "check, or any gate failure."
            ),
            "note": (
                "A pass is a mechanism-direction result, not an effect-size or capability result; "
                "a failure does not re-read T1b's PERSISTENCE CONTRIBUTES verdict."
            ),
        },
        "authorisation": {
            "required": True,
            "granted": False,
            "granted_on": None,
            "document": None,
            "quote": None,
            "note": "No dated grant exists. A grant naming the 24 cells, the rerun and the result artifact is required before an arm is built or a cell is opened. This preregistration authorises nothing to run.",
        },
        "runner": {
            "built": False,
            "planned_module": "benchmarks/persistence_mechanism_arm.py",
            "cells_run": 0,
            "why": "this record freezes the design, factors and gates only; no arm module exists and no cell has run",
        },
        "cost": {
            "cells": 24,
            "witness_cells": "one fresh-process determinism rerun of seed 20612301",
            "cycles": CYCLES,
            "wall_clock_estimate": "24 cells plus one four-arm rerun at 120 cycles each",
        },
        "stop_condition": (
            "No cell runs until a dated grant is recorded. After the grant, the block closes when "
            "the 24 cells and the rerun have produced their parts, G1-G7 have been scored once in "
            "the frozen order, and the verdict is recorded. Any gate failure is VOID; no cell is "
            "rerun to escape a gate and no gate is amended after a result."
        ),
        "not_evidence": (
            "A preregistration, not a result. No cell has run. It does not re-read T1 or T1b, does "
            "not re-open the denominator, and licenses no capability, retention or transfer claim. "
            "A mechanism direction is not an adoption recommendation."
        ),
        "amendments": [],
    }


def render(doc: dict) -> str:
    design = doc["design"]
    bar = doc["effects"]["bar"]
    lines = [
        "# PERSISTENCE-MECHANISM-1 — decay and the read floor at cap 112",
        "",
        "**Status.** %s. This page is rendered from `%s`; it is not edited by hand."
        % (doc["status"], RECORD.relative_to(ROOT)),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Preregistration | `%s` |" % doc["prereg"],
        "| Frozen on | %s |" % doc["frozen_on"],
        "| Engine | %s, cap %d, %s |" % (doc["engine"]["version"], doc["engine"]["cap"], doc["engine"]["edit"]),
        "| Cells planned | %d (%s) |" % (design["cells"], design["cells_arithmetic"]),
        "| Seeds | %s; bootstrap %d |" % (", ".join(str(seed) for seed in design["seeds"]), design["bootstrap"]),
        "| Cycles | %d |" % design["cycles"],
        "| Runner | not built |",
        "| Cells run | 0 |",
        "| Authorisation | not granted |",
        "",
        "## Why this block",
        "",
        "T1b's result decision says: **%s**" % doc["program"]["decision_quote"],
        "",
        doc["program"]["relationship"],
        "",
        "## The two mechanisms",
        "",
        "| Arm | Decay factor | Read floor | What changes |",
        "| --- | ---: | ---: | --- |",
    ]
    for name, arm in doc["arms"].items():
        lines.append("| `%s` | %s | %d | %s |"
                     % (name, arm["decay_factor"], arm["read_floor"], arm["description"]))
    lines += [
        "",
        "**Manipulation.** %s" % doc["mechanism"]["changes"],
        "",
        "## Endpoints",
        "",
        "| Stage | Definition | Role |",
        "| --- | --- | --- |",
    ]
    for row in doc["endpoints"]:
        lines.append("| %s | %s | %s |" % (row["stage"], row["definition"], row["role"]))
    lines += [
        "",
        "**Primary effects.** `decay_effect` = %s. `floor_effect` = %s. Interactive contrast: %s."
        % (doc["effects"]["definitions"]["decay_effect"],
           doc["effects"]["definitions"]["floor_effect"],
           doc["effects"]["definitions"]["interaction"]),
        "",
        "**Bar.** %s. Margin %d edges, %d of %d positive seeds, %d%% paired interval, %d resamples at seed %d."
        % (bar["rule"], bar["margin"], bar["positive_seeds"], bar["seeds"],
           bar["confidence"], bar["resamples"], design["bootstrap"]),
        "",
        "## Gates",
        "",
        "| Gate | Rule |",
        "| --- | --- |",
    ]
    for gate, rule in doc["gates"].items():
        lines.append("| `%s` | %s |" % (gate, rule))
    lines += [
        "",
        "## Decision table",
        "",
        "| Condition | Verdict | Reading | Decision |",
        "| --- | --- | --- | --- |",
    ]
    for row in doc["decision_table"]:
        lines.append("| %s | **%s** | %s | %s |"
                     % (row["condition"], row["verdict"], row["reading"], row["decision"]))
    lines += [
        "",
        "## Prediction, stated before any cell",
        "",
        "**Prediction.** %s" % doc["prediction"]["statement"],
        "",
        "**Because.** %s" % doc["prediction"]["because"],
        "",
        "**Falsifier.** %s" % doc["prediction"]["falsifier"],
        "",
        doc["prediction"]["note"],
        "",
        "## No cell has run",
        "",
        "**Authorisation.** %s" % doc["authorisation"]["note"],
        "",
        "**Cost.** %d cells plus %s, %d cycles each." % (
            doc["cost"]["cells"], doc["cost"]["witness_cells"], doc["cost"]["cycles"]),
        "",
        "**Stop condition.** %s" % doc["stop_condition"],
        "",
        "## What this record does not license",
        "",
        doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(doc: dict | None = None, page: str | None = None) -> list[str]:
    doc = record() if doc is None else doc
    page = PAGE.read_text(encoding="utf-8") if page is None else page
    found: list[str] = []
    if doc.get("prereg") != ID:
        found.append("the preregistration id is not %s" % ID)
    if doc.get("status") != STATUS:
        found.append("status is %r, not %r" % (doc.get("status"), STATUS))
    if doc.get("frozen_on") != FROZEN_ON:
        found.append("the record is not frozen on %s" % FROZEN_ON)
    if doc.get("no_cells_run") is not True:
        found.append("the record does not declare that no cell has run")
    if RUN.exists():
        found.append("%s exists for an unrun block" % RUN.relative_to(ROOT))
    if ARM.exists():
        found.append("%s exists although the record says the runner is not built" % ARM.relative_to(ROOT))

    design = doc.get("design") or {}
    seeds = list(design.get("seeds") or [])
    if seeds != SEEDS or design.get("bootstrap") != BOOTSTRAP:
        found.append("the seed block is not the frozen block")
    if design.get("cells") != 24 or design.get("cycles") != CYCLES or design.get("cap") != CAP:
        found.append("the cell, cycle or cap design is not 24/120/112")
    if design.get("cells_arithmetic") != "4 arms x 6 seeds = 24 cells":
        found.append("the cell arithmetic is not the frozen 4 x 6")
    freshness = (design.get("freshness") or "").lower()
    if "fresh" not in freshness and "unused" not in freshness:
        found.append("the fresh-seed declaration is missing")
    engine = doc.get("engine") or {}
    if (engine.get("version"), engine.get("cap"), engine.get("edit")) != ("0.15.0", CAP, "none"):
        found.append("the engine is not 0.15.0 at cap 112 with no edit")
    if set(design.get("arms") or []) != set(ARMS):
        found.append("the design arms are not the four factorial arms")
    collisions = cap.seed_collisions(seeds + [BOOTSTRAP], allow=(RECORD, PAGE))
    if collisions:
        found.append("the seed block is not fresh: %r" % (collisions,))

    arms = doc.get("arms") or {}
    if set(arms) != set(ARMS):
        found.append("the arm table does not hold the four factorial arms")
    for name, expected in ARMS.items():
        arm = arms.get(name) or {}
        if arm.get("decay_factor") != expected["decay_factor"]:
            found.append("%s has the wrong decay factor" % name)
        if arm.get("read_floor") != expected["read_floor"]:
            found.append("%s has the wrong read floor" % name)

    mechanism = doc.get("mechanism") or {}
    if "0.95" not in (mechanism.get("changes") or "") or "PREDICTION_MIN_COUNT" not in (mechanism.get("changes") or ""):
        found.append("the mechanism does not name the decay and read-floor changes")
    if "P is non-zero" not in (doc.get("gates") or {}).get("G4_denominator", ""):
        found.append("the denominator reading is not fixed")

    gates = doc.get("gates") or {}
    for gate in GATES:
        if gate not in gates:
            found.append("the gate %s is missing" % gate)
    if "0.95/5" not in (gates.get("G3_treatments_live") or ""):
        found.append("G3 does not name the shipped treatment values")
    if "zero S_ever" not in (gates.get("G4_denominator") or ""):
        found.append("G4 does not preserve the measured-zero reading")

    effects = doc.get("effects") or {}
    if effects.get("primary_endpoint") != "S_ever":
        found.append("the primary endpoint is not S_ever")
    for key in ("decay_effect", "floor_effect", "interaction"):
        if key not in (effects.get("definitions") or {}):
            found.append("the effect %s is not defined" % key)
    bar = effects.get("bar") or {}
    if (bar.get("margin"), bar.get("positive_seeds"), bar.get("seeds")) != (10, 5, 6):
        found.append("the effect bar is not the frozen 10/5-of-6 rule")
    if "at least 10" not in (bar.get("rule") or ""):
        found.append("the effect bar does not state the 10-edge margin")

    verdicts = {row.get("verdict") for row in doc.get("decision_table") or []}
    for verdict in VERDICTS:
        if verdict not in verdicts:
            found.append("the decision table has no %s row" % verdict)
    for row in doc.get("decision_table") or []:
        if not all(row.get(key) for key in ("condition", "verdict", "reading", "decision")):
            found.append("a decision row is incomplete")

    quote = (doc.get("program") or {}).get("decision_quote") or ""
    result_text = " ".join(T1B_RESULT.read_text(encoding="utf-8").split())
    if quote not in result_text:
        found.append("the T1b decision quote is not in the T1b result")
    if "T1" not in (doc.get("program") or {}).get("relationship", ""):
        found.append("the record does not carry the prior T1/T1b context")

    auth = doc.get("authorisation") or {}
    if auth.get("granted") is not False or auth.get("document") or auth.get("quote"):
        found.append("the record claims an authorisation it does not have")
    runner = doc.get("runner") or {}
    if runner.get("built") is not False or runner.get("cells_run") != 0:
        found.append("the record claims a built runner or a run cell")
    if runner.get("planned_module") != ARM.relative_to(ROOT).as_posix():
        found.append("the planned arm module is not %s" % ARM.relative_to(ROOT))
    if "no cell has run" not in (doc.get("not_evidence") or "").lower():
        found.append("the record does not say that no cell has run")
    if "capability" not in (doc.get("not_evidence") or "").lower():
        found.append("the record does not disclaim a capability claim")
    if page.strip() != render(doc).strip():
        found.append("the page does not match the record; run --freeze or --render")
    return found


def freeze() -> int:
    if RECORD.exists():
        print("REFUSED: %s already exists and is frozen" % RECORD.relative_to(ROOT))
        return 2
    doc = engine_stamp.stamp(build())
    RECORD.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(doc), encoding="utf-8")
    print("froze %s and %s" % (RECORD.relative_to(ROOT), PAGE.relative_to(ROOT)))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--render", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.freeze:
        return freeze()
    if args.render:
        PAGE.write_text(render(record()), encoding="utf-8")
        print("rendered %s" % PAGE.relative_to(ROOT))
        return 0
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    doc = record()
    print("persistence mechanism: %s, %d cells, %d seeds, runner not built, no grant"
          % (doc["status"], doc["design"]["cells"], len(doc["design"]["seeds"])))
    return 0
