"""PRESENCE-BAND-3: fresh worlds, the fixed rank-21-40 band, and a B5 that can fail.

BAND-1 named 62 Q4 edges and returned VOID on a defective B5. BAND-2 fixed B5 and
the rank reader, but deliberately reused Q4's six worlds, so it could only confirm
same-world service. This block is the fresh-world repair: six unused seeds, the same
two caps, the strict ``source>target`` parser, and a B5 that remains a live cap test
rather than a restatement of the band.

The band is not copied or named before the run. For each fresh world it is every
present transition whose minimum block rank in the cap-112 ceiling universe is 21-40.
The block records the band and the per-edge service at both caps. No arm exists and no
cell has run; the dated grant is recorded before the arm is built.

    ./.venv/bin/python -m benchmarks.presence_band_rank_3_prereg --freeze
    ./.venv/bin/python -m benchmarks.presence_band_rank_3_prereg --check
    ./.venv/bin/python -m benchmarks.presence_band_rank_3_prereg --render
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.presence_band_rank_2_prereg import (
    RankReadingError,
    rank_reading,
    read_served_edge,
    recorded_ranks,
)

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "presence_band_rank_3_prereg.json"
PAGE = ROOT / "docs" / "PRESENCE-BAND-RANK-3-PREREGISTRATION.md"
RUN = ROOT / "docs" / "presence_band_rank_3_run.json"
ARM = ROOT / "benchmarks" / "presence_band_rank_3_arm.py"
AUTH = ROOT / "docs" / "AUTHORISATION-PRESENCE-BAND-3.md"
DECISION = ROOT / "docs" / "DECISION-ADMISSION-STEP.md"
SOURCE = ROOT / "organica" / "sleep_extraction.py"

ID = "PRESENCE-BAND-3"
STATUS = "FROZEN, NOT RUN"
FROZEN_ON = "2026-11-11"
SEEDS = (20612401, 20612402, 20612403, 20612404, 20612405, 20612406)
CAPS = (40, 112)
B5_FLOOR = 56
BAND_LOW = 21
BAND_HIGH = 40
GRANT_QUOTE = (
    "Preregister a repaired band block with fresh seeds and the fixed harness, "
    "with B5 still able to fail, and record its grant before running."
)


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def _served(cell: dict) -> set[tuple[str, str]]:
    return {read_served_edge(item)
            for window in cell.get("windows_world") or [] for item in window}


def band_edges(cell: dict) -> dict[tuple[str, str], int]:
    """The rank-21-40 present transitions, independent of whether they served."""
    if int(cell.get("cap") or 0) != 112:
        raise ValueError("the band is defined from the cap-112 ceiling cell")
    present = {tuple(edge) for edge in cell.get("present_edges") or []}
    ranks, relations = recorded_ranks(cell)
    return {
        edge: rank for edge, rank in ranks.items()
        if edge in present
        and relations.get(edge) == "transition"
        and BAND_LOW <= rank <= BAND_HIGH
    }


def b5_cap_live(cell: dict) -> dict:
    """B5 as a live cap test; a short cap, rank ceiling or broken parse fails it."""
    reasons: list[str] = []
    transitions = max(
        (int(row.get("transitions") or 0) for row in cell.get("allocation") or []),
        default=0,
    )
    max_rows = max((len(window) for window in cell.get("windows") or []), default=0)
    if transitions < B5_FLOOR:
        reasons.append(
            "the 112 transition count is %d, below the floor of %d" % (transitions, B5_FLOOR)
        )
    if max_rows > 112:
        reasons.append("a window holds %d rows, above 112" % max_rows)
    try:
        reading = rank_reading(cell)
    except (RankReadingError, ValueError) as exc:
        reasons.append("the served edges are not parseable: %s" % exc)
        reading = {"max_served_transition_rank": None, "missing_rank": []}
    max_rank = reading.get("max_served_transition_rank")
    if max_rank is None or max_rank <= BAND_HIGH:
        reasons.append(
            "the maximum served transition rank is %r, not above %d" % (max_rank, BAND_HIGH)
        )
    if reading.get("missing_rank"):
        reasons.append(
            "served transitions have no recorded rank: %s"
            % ", ".join(reading["missing_rank"])
        )
    return {
        "passed": not reasons,
        "transitions": transitions,
        "max_served_transition_rank": max_rank,
        "max_rows": max_rows,
        "missing_rank": reading.get("missing_rank") or [],
        "reasons": reasons,
    }


def _fixture(**overrides) -> dict:
    cell = {
        "cap": 112,
        "allocation": [{"transitions": 56}],
        "windows": [[("amber", "olive")]],
        "windows_world": [["amber>olive"]],
        "present_edges": [["amber", "olive"]],
        "universe": [[{"edge": ["amber", "olive"], "rank": 56, "relation": "transition"}]],
    }
    cell.update(overrides)
    return cell


def build() -> dict:
    return {
        "prereg": ID,
        "status": STATUS,
        "frozen_on": FROZEN_ON,
        "no_cells_run": True,
        "question": (
            "On the shipped 0.15.0 build, with six fresh worlds, does raising the "
            "Layer-1 cap from 40 to 112 put every measured rank-21-40 present "
            "transition into service, with B1-B8 passing and B5 still able to fail?"
        ),
        "program": {
            "draft": "docs/DECISION-ADMISSION-STEP.md",
            "question": "Q054",
            "relationship": (
                "BAND-1 named Q4's 62 rank-21-40 edges and was VOID on B5. BAND-2 fixed "
                "B5 and the rank reader but reused Q4's worlds, so it could not test a "
                "fresh-world band. BAND-3 keeps the fixed parser and the corrected floor, "
                "re-derives the band in six unused worlds, and leaves the cap-live gate "
                "able to fail. BAND-1 remains VOID and BAND-2 remains unrun and is not "
                "re-read as this block's evidence."
            ),
        },
        "hypothesis": (
            "In each fresh world, every present transition at rank 21-40 is served at "
            "cap 112 and none of them is served at cap 40; the 112 arm has at least 56 "
            "transitions and a maximum served transition rank above 40."
        ),
        "design": {
            "arms": ["cap 40", "cap 112"],
            "caps": list(CAPS),
            "shipped_cap": 112,
            "seeds": list(SEEDS),
            "cycles": 120,
            "cells": 12,
            "cells_arithmetic": "2 caps x 6 seeds = 12 cells",
            "variable": "SleepService.MAX_PREDICTIONS, set per cell",
            "observer": (
                "the repaired observer of PRESENCE-CONVERSION-2, returning the engine's "
                "own served list and recording the pre-cap universe with a second call"
            ),
            "world": (
                "the compositional world family of PHASE_ACQUISITION at 120 cycles on "
                "six fresh seeds; no Q4 world is reused"
            ),
            "pairing": (
                "each seed contributes one world and one stimulus to both caps; only the "
                "cap changes, and each band edge is paired across the two cells"
            ),
            "freshness": (
                "All six seeds are fresh and unused at freeze time: seed_collisions over "
                "every docs JSON returns no hit. The record and page are the only allowed "
                "artifacts that name them."
            ),
            "reuse": (
                "No Q4 seed, no named Q4 band and no BAND-1 or BAND-2 cell is reused. "
                "This is a fresh-world generalisation of the rank rule, not a replication "
                "of the 62 named edges."
            ),
        },
        "band": {
            "definition": (
                "For each seed, the band is every present transition whose minimum "
                "block rank in the cap-112 ceiling universe is 21-40. The band is "
                "measured from the 112 arm; it is not fixed to 62 edges and it is not "
                "filtered by cap-40 service."
            ),
            "derivation": (
                "Read the cap-112 cell's present_edges and universe; keep each edge "
                "whose relation is transition and whose minimum recorded rank is "
                "21-40. A missing rank is a failure, not a zero."
            ),
            "size": "measured per seed; no fixed total",
            "zero_band": (
                "A seed with zero rank-21-40 present transitions is a zero denominator: "
                "B6 fails and the block is VOID, never split as 0 served."
            ),
            "service_separation": (
                "Band membership is independent of cap-40 service and is not filtered by "
                "cap-40 service. B4 measures whether the 40 arm served a band edge; it is "
                "not removed from the band to make B4 pass."
            ),
        },
        "engine": {
            "version": "0.15.0",
            "cap": 112,
            "edit": "none",
            "treatment": "only SleepService.MAX_PREDICTIONS is set per cell",
        },
        "endpoints": [
            {"stage": "W", "definition": "world edges generated for the seed", "role": "denominator"},
            {"stage": "P", "definition": "world edges present in the temporal graph", "role": "band universe"},
            {"stage": "band", "definition": "present transitions at minimum block rank 21-40 in the 112 ceiling", "role": "measured treatment group"},
            {"stage": "S40", "definition": "band edges served in at least one cap-40 cycle", "role": "pre-treatment control"},
            {"stage": "S112", "definition": "band edges served in at least one cap-112 cycle", "role": "primary endpoint"},
            {"stage": "A112", "definition": "band edges asserted at the end of the cap-112 run", "role": "secondary, reported not adjudicated"},
            {"stage": "ledger", "definition": "per edge: rank at each cap, cycles served, first served cycle, asserted, relation", "role": "per-edge record"},
        ],
        "gates": {
            "B1_build": (
                "all twelve cells run the shipped 0.15.0 build at the named cap, with "
                "one sha256 across the run and only MAX_PREDICTIONS overridden; a mixed "
                "or edited build is VOID"
            ),
            "B2_world_fresh": (
                "each seed's world digest and present fingerprint are identical at 40 "
                "and 112, and every seed is absent from every prior docs artifact; a "
                "different world or a reused seed is VOID"
            ),
            "B3_band_identity": (
                "at cap 112 every band edge is a present transition whose minimum "
                "recorded rank is 21-40 and whose rank is present; each seed's band is "
                "non-empty; a missing edge, duplicate, missing rank or out-of-band rank "
                "fails B3. The band is read before cap-40 service is considered."
            ),
            "B4_control_40": (
                "the 40 arm serves exactly 20 transitions and 0 band edges on every "
                "seed; a band edge served at 40, or a transition count other than 20, "
                "fails B4"
            ),
            "B5_cap_live": (
                "the 112 arm has at least 56 transitions, a maximum served transition "
                "rank above block rank 40, no window above 112 rows, every served edge "
                "parsed as exactly one source>target, and every served transition "
                "ranked. A fixture with 20 transitions, or with 56 transitions but a "
                "maximum served rank of 40, must fail B5; B5 is not conditional on band "
                "service. A short count, a rank ceiling at or below 40, an overfull "
                "window, an unparseable edge or an unranked served transition is VOID."
            ),
            "B6_denominator": (
                "each seed's band is non-empty and every band edge reaches the ledger; "
                "a zero band or a zero P is not measurable and is VOID, never 0.0"
            ),
            "B7_determinism": (
                "a fresh-process rerun of seed 20612401 at 112 reproduces its per-edge "
                "ledger exactly"
            ),
            "B8_seed_axis": (
                "the six 112 ledgers hold at least three distinct served-band edge sets; "
                "a repeated set is one world, not six. Distinct served counts are not "
                "required because fresh band sizes may differ."
            ),
        },
        "b5_fixture": {
            "pass": "56 transitions, maximum served transition rank 56",
            "fail_transition_count": "20 transitions",
            "fail_max_rank": "56 transitions with maximum served transition rank 40",
            "fail_rank_read": "a served transition with no recorded rank, or an unparseable edge",
            "rule": "the same b5_cap_live helper is used by the arm and by the check; the fixture must show both pass and fail",
        },
        "acceptance": {
            "quote": (
                "The 21–40 transitions must be served at 112 and the block's own gates "
                "must pass, per seed, with the seed axis live."
            ),
            "source": "docs/DECISION-ADMISSION-STEP.md",
            "owner": (
                "The condition is the decision's, unchanged; this block adjudicates "
                "whether it holds and does not decide what follows."
            ),
        },
        "prediction": {
            "statement": (
                "Every measured band edge is served at 112 on every seed and none at "
                "40; B5 passes with at least 56 transitions and a maximum served "
                "transition rank above 40."
            ),
            "because": (
                "The 112 floor is 56 and the band is ranks 21-40 by construction. "
                "BAND-1 observed 62/62 served at 112 on its Q4 worlds; this is a "
                "fresh-world generalisation, not a discovery."
            ),
            "prior_observation": (
                "BAND-1's band was served 62/62 at 112 and 0/62 at 40, but BAND-1 is "
                "VOID on its B5. BAND-2 corrected B5 but reused the same worlds and is "
                "unrun. Neither is BAND-3's evidence."
            ),
            "falsifier": (
                "Any band edge unserved at 112, any band edge served at 40, any B5 "
                "failure, an empty band, a rank mismatch, an unparseable edge, or a "
                "missing rank."
            ),
            "note": (
                "A pass is fresh-world service for one world family and build; it is "
                "not a capability, retention or transfer claim."
            ),
        },
        "decision_table": [
            {
                "condition": "any gate other than B3 fails",
                "verdict": "VOID",
                "reading": "the block is unrun or non-reproducible and the failed gate names what did not happen",
                "decision": "record VOID; fix the failed gate and register a new block; read no acceptance",
            },
            {
                "condition": "B3 fails: a band edge is missing, duplicate, unranked, or not ranked 21-40",
                "verdict": "BAND NOT REPRODUCED",
                "reading": "the rank-21-40 band is not reproduced on the fresh build, so the band is build-dependent",
                "decision": "report the build dependence; the acceptance stays unadjudicated; do not substitute a fresh band",
            },
            {
                "condition": "gates pass; every measured band edge served at 112 on every seed",
                "verdict": "BAND IN SERVICE",
                "reading": "the condition is met on every measured fresh-world band edge",
                "decision": "record the condition met; the allocation explanation is not refuted at this world family; the owner decides any engine or promotion step; no capability claim",
            },
            {
                "condition": "gates pass; between 1 and all-but-one measured band edges served at 112",
                "verdict": "BAND PARTLY IN SERVICE",
                "reading": "the condition is not met; the unserved edges are the finding and are named in the ledger",
                "decision": "report the per-edge misses; the allocation explanation is refuted for them; the next step is the admission rule, not another level",
            },
            {
                "condition": "gates pass; none of the measured band edges served at 112",
                "verdict": "BAND NOT IN SERVICE",
                "reading": "the condition is not met on any measured band edge",
                "decision": "record the refutation; the next step is the admission rule, not another level",
            },
        ],
        "authorisation": {
            "required": True,
            "granted": True,
            "granted_on": FROZEN_ON,
            "document": "docs/AUTHORISATION-PRESENCE-BAND-3.md",
            "quote": GRANT_QUOTE,
            "note": (
                "Granted 2026-11-11 against this record before any cell. The twelve "
                "design cells, the determinism rerun and the result artifact/page are "
                "authorised. The arm is not built and no cell has run; building the arm "
                "does not open a cell without a passing preflight."
            ),
        },
        "runner": {
            "built": False,
            "planned_module": "benchmarks/presence_band_rank_3_arm.py",
            "cells_run": 0,
            "why": "the record and grant precede the arm; no arm module exists and no cell has run",
        },
        "cost": {
            "cells": 12,
            "witness_cells": "one fresh-process determinism rerun",
            "cycles": 120,
            "wall_clock_estimate": "twelve cells plus one rerun at 120 cycles each",
        },
        "stop_condition": (
            "No cell runs until the arm exists and its preflight passes. After that, "
            "the block closes when the twelve cells and rerun have produced their "
            "parts, B1-B8 have been scored once in the frozen order, and the verdict is "
            "recorded. A gate failure is VOID; no cell is rerun to escape a gate and no "
            "gate is amended after a result."
        ),
        "not_evidence": (
            "A preregistration and a grant, not a result. No cell has run. BAND-1 stays "
            "VOID and BAND-2 stays unrun; neither is re-read. This record licenses no "
            "capability, retention or transfer claim."
        ),
        "amendments": [
            {
                "date": FROZEN_ON,
                "kind": "grant-recorded",
                "note": (
                    "The grant was recorded before an arm was built or a cell opened; "
                    "at this date the record is FROZEN, NOT RUN with cells_run = 0."
                ),
            }
        ],
    }


def render(doc: dict) -> str:
    design = doc["design"]
    lines = [
        "# PRESENCE-BAND-3 — fresh worlds, the fixed band, and a B5 that can fail",
        "",
        "**Status.** %s. This page is rendered from `%s`; it is not edited by hand."
        % (doc["status"], RECORD.relative_to(ROOT).as_posix()),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Preregistration | `%s` |" % doc["prereg"],
        "| Frozen on | %s |" % doc["frozen_on"],
        "| Engine | %s, cap %d, %s |" % (doc["engine"]["version"], doc["engine"]["cap"], doc["engine"]["edit"]),
        "| Question | %s |" % doc["question"],
        "| Cells planned | %d (%s) |" % (design["cells"], design["cells_arithmetic"]),
        "| Seeds | %s |" % ", ".join(str(seed) for seed in design["seeds"]),
        "| Caps | %s |" % ", ".join(str(cap) for cap in design["caps"]),
        "| Cycles | %d |" % design["cycles"],
        "| Band | %s |" % doc["band"]["size"],
        "| Runner | not built |",
        "| Cells run | 0 |",
        "| Authorisation | granted |",
        "",
        "## Why a third block",
        "",
        doc["program"]["relationship"],
        "",
        "## The band is measured, not named before the run",
        "",
        doc["band"]["definition"],
        "",
        "**Derivation.** %s" % doc["band"]["derivation"],
        "",
        "**Zero band.** %s" % doc["band"]["zero_band"],
        "",
        "**Service separation.** %s" % doc["band"]["service_separation"],
        "",
        "## Design",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Arms | cap 40 and cap 112 |",
        "| Variable | `%s` |" % design["variable"],
        "| Observer | %s |" % design["observer"],
        "| World | %s |" % design["world"],
        "| Pairing | %s |" % design["pairing"],
        "| Freshness | %s |" % design["freshness"],
        "| Reuse | %s |" % design["reuse"],
        "| Cycles | %d |" % design["cycles"],
        "| Cells | %d |" % design["cells"],
        "",
        "## Endpoints",
        "",
        "| Stage | Definition | Role |",
        "| --- | --- | --- |",
    ]
    for row in doc["endpoints"]:
        lines.append("| %s | %s | %s |" % (row["stage"], row["definition"], row["role"]))
    lines += ["", "## Gates", "", "| Gate | Rule |", "| --- | --- |"]
    for gate, rule in doc["gates"].items():
        lines.append("| `%s` | %s |" % (gate, rule))
    fixture = doc["b5_fixture"]
    lines += [
        "",
        "## Fixed harness and a B5 that can fail",
        "",
        "The strict `source>target` parser and the minimum-rank lookup are imported from "
        "`benchmarks.presence_band_rank_2_prereg`. B5 is scored by `b5_cap_live`, the "
        "same helper the future arm must use.",
        "",
        "| Fixture | Expected |",
        "| --- | --- |",
        "| %s | PASS |" % fixture["pass"],
        "| %s | FAIL |" % fixture["fail_transition_count"],
        "| %s | FAIL |" % fixture["fail_max_rank"],
        "| %s | FAIL |" % fixture["fail_rank_read"],
        "",
        fixture["rule"],
        "",
        "## Acceptance condition",
        "",
        "> %s" % doc["acceptance"]["quote"],
        "",
        "Source: `%s`. %s" % (doc["acceptance"]["source"], doc["acceptance"]["owner"]),
        "",
        "## Prediction, stated before any cell",
        "",
        "**Prediction.** %s" % doc["prediction"]["statement"],
        "",
        "**Because.** %s" % doc["prediction"]["because"],
        "",
        "**Prior observation.** %s" % doc["prediction"]["prior_observation"],
        "",
        "**Falsifier.** %s" % doc["prediction"]["falsifier"],
        "",
        doc["prediction"]["note"],
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
        "## Grant and stop",
        "",
        "**Authorisation.** %s" % doc["authorisation"]["note"],
        "",
        "**Grant document.** `%s`" % doc["authorisation"]["document"],
        "",
        "> %s" % doc["authorisation"]["quote"],
        "",
        "**Cost.** %d cells (%s) x %d cycles." % (
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
        found.append("%s exists for an unrun block" % RUN.relative_to(ROOT).as_posix())
    if ARM.exists():
        found.append("%s exists although the record says the arm is not built" % ARM.relative_to(ROOT).as_posix())

    design = doc.get("design") or {}
    seeds = list(design.get("seeds") or [])
    if len(seeds) != 6 or len(set(seeds)) != 6:
        found.append("the design does not hold six distinct seeds")
    if design.get("caps") != list(CAPS) or design.get("shipped_cap") != 112:
        found.append("the caps are not 40 and 112 with 112 shipped")
    if design.get("cells") != len(seeds) * 2 or design.get("cycles") != 120:
        found.append("the cell or cycle count is not the frozen design")
    if "fresh" not in (design.get("freshness") or "").lower():
        found.append("the design does not declare fresh seeds")
    if "No Q4" not in (design.get("reuse") or ""):
        found.append("the design does not refuse Q4 reuse")
    try:
        from benchmarks.presence_cap_experiment import seed_collisions
        collisions = seed_collisions(seeds, allow=(RECORD, PAGE, AUTH))
        if collisions:
            found.append("seeds collide with existing artifacts: %r" % collisions)
    except Exception as exc:  # pragma: no cover
        found.append("the freshness scan could not run: %s" % exc)

    band = doc.get("band") or {}
    definition = (band.get("definition") or "").lower()
    for needed in ("present transition", "rank", "21-40", "measured"):
        if needed not in definition:
            found.append("the band definition does not carry %r" % needed)
    if "zero denominator" not in (band.get("zero_band") or "").lower():
        found.append("the band does not make an empty band a zero denominator")
    if "not filtered" not in (band.get("service_separation") or "").lower():
        found.append("the band does not separate membership from cap-40 service")

    gates = doc.get("gates") or {}
    for gate in ("B1_build", "B2_world_fresh", "B3_band_identity", "B4_control_40",
                 "B5_cap_live", "B6_denominator", "B7_determinism", "B8_seed_axis"):
        if gate not in gates:
            found.append("the gate %s is missing" % gate)
    b5 = (gates.get("B5_cap_live") or "").lower()
    for needed in ("at least 56", "above block rank 40", "not conditional", "20 transitions", "rank of 40"):
        if needed not in b5:
            found.append("B5 does not carry %r" % needed)
    if "exactly 56" in b5:
        found.append("B5 still requires an exact 56-transition allocation")
    if "no window above 112" not in b5:
        found.append("B5 does not bound the served window")

    good = b5_cap_live(_fixture())
    if not good["passed"]:
        found.append("B5 does not pass the 56-transition fixture: %s" % good["reasons"])
    bad = {
        "short": b5_cap_live(_fixture(allocation=[{"transitions": 20}])),
        "ceiling": b5_cap_live(_fixture(universe=[[{"edge": ["amber", "olive"], "rank": 40, "relation": "transition"}]])),
        "unranked": b5_cap_live(_fixture(windows_world=[["birch>cedar"]])),
        "malformed": b5_cap_live(_fixture(windows_world=[["amber>olive>bad"]])),
    }
    for name, result in bad.items():
        if result["passed"]:
            found.append("B5 passes the %s failure fixture" % name)

    auth = doc.get("authorisation") or {}
    if auth.get("granted") is not True:
        found.append("the record claims no authorisation")
    for field in ("granted_on", "document", "quote"):
        if not auth.get(field):
            found.append("the grant lacks `authorisation.%s`" % field)
    granted = ROOT / (auth.get("document") or "docs/NO-SUCH-GRANT.md")
    if not granted.exists():
        found.append("the authorisation document does not exist")
    else:
        text = granted.read_text(encoding="utf-8")
        if auth.get("quote") not in text:
            found.append("the quoted grant does not appear in its document")
        if auth.get("granted_on") not in text:
            found.append("the grant date does not appear in its document")
    runner = doc.get("runner") or {}
    if runner.get("built") is not False or runner.get("cells_run") != 0:
        found.append("the record claims a built arm or a run cell")
    if runner.get("planned_module") != ARM.relative_to(ROOT).as_posix():
        found.append("the planned arm module is not %s" % ARM.relative_to(ROOT).as_posix())

    acceptance = doc.get("acceptance") or {}
    quote = " ".join((acceptance.get("quote") or "").split())
    decision = " ".join(DECISION.read_text(encoding="utf-8").split()) if DECISION.exists() else ""
    if not quote or quote not in decision:
        found.append("the acceptance quote is not the admission decision's sentence")

    table = doc.get("decision_table") or []
    verdicts = {row.get("verdict") for row in table}
    for verdict in ("VOID", "BAND NOT REPRODUCED", "BAND IN SERVICE",
                    "BAND PARTLY IN SERVICE", "BAND NOT IN SERVICE"):
        if verdict not in verdicts:
            found.append("the decision table has no %s row" % verdict)
    directions = [row.get("decision") for row in table
                  if row.get("verdict") in ("BAND IN SERVICE", "BAND PARTLY IN SERVICE",
                                            "BAND NOT IN SERVICE")]
    if len(set(directions)) != len(directions):
        found.append("two service directions share one decision")
    if "no capability" not in (doc.get("not_evidence") or "").lower():
        found.append("the record does not disclaim a capability claim")
    if page.strip() != render(doc).strip():
        found.append("the page does not match the record; run --render")
    return found


def freeze() -> int:
    if RECORD.exists():
        print("REFUSED: %s already exists and is frozen" % RECORD.relative_to(ROOT).as_posix())
        return 2
    doc = engine_stamp.stamp(build())
    RECORD.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(doc), encoding="utf-8")
    print("froze %s and %s" % (RECORD.relative_to(ROOT).as_posix(), PAGE.relative_to(ROOT).as_posix()))
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
        doc = record()
        PAGE.write_text(render(doc), encoding="utf-8")
        print("rendered %s" % PAGE.relative_to(ROOT).as_posix())
        return 0
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    doc = record()
    print("presence band 3: %s, %d cells, fresh seeds, B5 fail-closed, grant recorded, no arm, no cell"
          % (doc["status"], doc["design"]["cells"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
