"""PRESENCE-BAND-2: the corrected band block, frozen and unrun.

BAND-1 named the 62 Q4 rank-21-40 transitions and ran them, but its B5 required the
cap-112 transition allocation to be **exactly 56**. The engine does not allocate a fixed
count: it guarantees ``MAX_PREDICTIONS // 2`` transitions and then backfills unused
cooccurrence slots with additional transitions (``organica/sleep_extraction.py``). The
observed 64-69 is therefore the floor plus backfill, and BAND-1's gate misread the rule.

BAND-1's first B5 also read served edges as character tuples, so the rank comparison
returned zero. This record fixes both defects before any cell: B5 is a floor condition
with a live rank comparison, and served edges are parsed strictly from ``source>target``.

This module freezes the design and the corrected gate. It builds no arm and runs no cell.
The record is ungranted; a dated grant must be recorded before an arm is built or a cell
is opened.

    ./.venv/bin/python -m benchmarks.presence_band_rank_2_prereg --freeze
    ./.venv/bin/python -m benchmarks.presence_band_rank_2_prereg --check
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "presence_band_rank_2_prereg.json"
PAGE = ROOT / "docs" / "PRESENCE-BAND-RANK-2-PREREGISTRATION.md"
RUN = ROOT / "docs" / "presence_band_rank_2_run.json"
ARM = ROOT / "benchmarks" / "presence_band_rank_2_arm.py"
BAND1 = ROOT / "docs" / "presence_band_rank_prereg.json"
Q4 = ROOT / "docs" / "presence_conversion_repair_run.json"
DECISION = ROOT / "docs" / "DECISION-ADMISSION-STEP.md"
SOURCE = ROOT / "organica" / "sleep_extraction.py"

ID = "PRESENCE-BAND-2"
BAND_TOTAL = 62
STATUS = "FROZEN, NOT RUN"
FROZEN_ON = "2026-11-11"


class RankReadingError(ValueError):
    """A served edge is not a single ``source>target`` pair."""


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def build() -> dict:
    base = json.loads(BAND1.read_text(encoding="utf-8"))
    band = copy.deepcopy(base["band"])
    band["identity_note"] = (
        "Copied by identity from BAND-1's frozen band block, which was derived from Q4's "
        "recorded per-cycle candidate ledger. BAND-2 reuses the same 62 edges because the "
        "band exists only in these six worlds; it does not re-derive a fresh band."
    )
    design = copy.deepcopy(base["design"])
    design.update({
        "reuse": (
            "Q4's six seeds are reused deliberately, not redrawn: the named edges exist only "
            "in Q4's worlds and BAND-2 is a confirmatory block on the same worlds. This is not "
            "a fresh-seed generalisation, and the record says so before any cell."
        ),
        "freshness": (
            "No new seed is drawn. The six worlds are Q4's, gated by the frozen world digest; "
            "a different world cannot pass as the same band."
        ),
    })
    gates = copy.deepcopy(base["gates"])
    gates["B5_cap_live"] = (
        "the 112 arm's transition count is **at least 56** — the engine guarantees "
        "`MAX_PREDICTIONS // 2 = 56` and backfills unused cooccurrence slots with further "
        "transitions, so **56 is a floor, not an exact count** — its served transition prefix "
        "extends past **block rank 40** on every seed, and no window exceeds **112** rows. The "
        "rank of a served edge is read by splitting `source>target` at **exactly one** `>` into "
        "**two non-empty** tags, then taking the **minimum** recorded rank for that exact edge; "
        "a served transition with **no recorded rank** fails the gate rather than contributing 0. "
        "A transition count below 56, a maximum served transition rank at or below 40, a window "
        "above 112, an unparseable served edge, or a served transition with no recorded rank is VOID."
    )
    return {
        "prereg": ID,
        "status": STATUS,
        "frozen_on": FROZEN_ON,
        "no_cells_run": True,
        "question": (
            "On the shipped 0.15.0 build, does BAND-2 read all 62 named Q4 rank-21-40 "
            "transitions as served at cap 112 and 0 at cap 40, per seed, with the corrected "
            "B5 floor condition and the fixed rank mapping, and with B1-B8 passing?"
        ),
        "program": {
            "draft": "docs/DECISION-ADMISSION-STEP.md",
            "question": "Q054",
            "relationship": (
                "BAND-1 was VOID on B5, not because the band failed but because B5 required an "
                "exact 56 transition rows and the rank reader returned character tuples. BAND-2 "
                "is a new block, not a re-score: it corrects both defects from the engine source, "
                "keeps the same 62 edges and the same Q4 worlds, and makes a pass a confirmation "
                "of same-world service rather than a fresh-seed generalisation. BAND-1 remains "
                "VOID and its cells are not re-read as this block's evidence."
            ),
        },
        "hypothesis": (
            "The 62 named edges are all served at 112 on every seed and none at 40; the 112 "
            "transition count is at least 56 with room for backfill, and the served transition "
            "prefix reaches a block rank above 40."
        ),
        "design": design,
        "band": band,
        "engine": copy.deepcopy(base["engine"]),
        "endpoints": copy.deepcopy(base["endpoints"]),
        "gates": gates,
        "b5_correction": {
            "previous_gate": (
                "BAND-1 required the 112 arm's transition allocation to be exactly 56 and its "
                "rank comparison to read a served edge. It was VOID on every seed: the allocation "
                "was 64-69 and the rank read was 0."
            ),
            "why_it_was_wrong": (
                "The transition allocation is a floor, not an exact count. "
                "`organica/sleep_extraction.py` sets `transition_budget = returned_budget // 2`, "
                "serves that many transitions, fills the remaining budget with cooccurrences, and "
                "then backfills any unused slots with further transitions (`more_trans`). At cap "
                "112 the floor is 56; 64-69 is 56 plus backfill, so the old exact-count condition "
                "could not pass on a correctly functioning engine."
            ),
            "source": "organica/sleep_extraction.py:511-525",
            "new_condition": (
                "transitions >= 56; max served transition rank > 40; every served edge parsed "
                "strictly; every served transition ranked; no window above 112."
            ),
            "does_not_change": (
                "BAND-1 remains VOID and is not re-scored. BAND-2 does not use BAND-1's cells as "
                "its own result; it repeats the same-world measurement under a corrected gate."
            ),
        },
        "rank_reading": {
            "previous_defect": (
                "BAND-1's first B5 built character tuples from the served strings, so the rank "
                "lookup found no served transition and reported 0."
            ),
            "rule": (
                "Each served edge is a string `source>target` in `windows_world`. Split at exactly "
                "one `>` and require two non-empty tags. The edge's rank is the minimum recorded "
                "rank for that exact tuple in the universe. A served transition with no recorded "
                "rank fails B5; it is never defaulted to 0. An unparseable served edge also fails."
            ),
            "helper": "benchmarks.presence_band_rank_2_prereg.rank_reading",
            "fixture": (
                "`amber>olive` maps to `('amber', 'olive')` and a recorded rank 41 must yield a "
                "maximum served transition rank of 41 with no missing rank; the pre-fix character "
                "tuple does not resolve and fails the fixture."
            ),
        },
        "acceptance": copy.deepcopy(base["acceptance"]),
        "prediction": {
            "statement": (
                "All 62 named edges are served at 112 on every seed and none at 40; the corrected "
                "B5 passes with a transition count of at least 56 and a maximum served transition "
                "rank above 40."
            ),
            "because": (
                "The 112 transition floor is 56 and the band occupies block ranks 21-40; the "
                "engine's backfill can only add transitions. BAND-1's ledger already recorded "
                "62/62 at 112, so this is a confirmatory prediction, not a discovery."
            ),
            "prior_observation": (
                "BAND-1's run recorded all 62 served at 112 and 0 at 40, but BAND-1 is VOID on "
                "B5. BAND-2 treats that only as the prior that motivates a corrected block; it is "
                "not BAND-2's result and is not counted as BAND-2 evidence."
            ),
            "falsifier": (
                "Any named edge served in 0 cap-112 cycles, any named edge served at cap 40, any "
                "transition count below 56, any maximum served transition rank at or below 40, any "
                "window above 112, any unparseable served edge, any served transition with no "
                "recorded rank, or any gate failure."
            ),
            "note": (
                "A pass is confirmation on the same worlds; it is not a fresh-seed replication and "
                "does not license a capability, retention or transfer claim."
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
                "condition": "B3 fails: a named edge is missing, not ranked 21-40, or served at cap 40",
                "verdict": "BAND NOT REPRODUCED",
                "reading": "the named edges are not the 21-40 band on the shipped build, so the band is build-dependent",
                "decision": "report the build dependence; the acceptance stays unadjudicated and the decision PENDING; do not substitute a fresh band",
            },
            {
                "condition": "gates pass; all 62 named edges served at 112 on every seed",
                "verdict": "BAND IN SERVICE",
                "reading": "the condition is met on the named edges with the corrected floor and a live rank comparison",
                "decision": "record the condition met; the allocation explanation is not refuted at this world family; BAND-1 remains VOID and is not re-scored; no capability claim",
            },
            {
                "condition": "gates pass; between 1 and 61 named edges served at 112",
                "verdict": "BAND PARTLY IN SERVICE",
                "reading": "the condition is not met; the unserved edges are the finding and are named in the ledger",
                "decision": "report the per-edge misses; the allocation explanation is refuted for them; the next step is the admission rule, not another level",
            },
            {
                "condition": "gates pass; none of the 62 named edges served at 112",
                "verdict": "BAND NOT IN SERVICE",
                "reading": "the condition is not met on any named edge",
                "decision": "record the refutation; the next step is the admission rule, not another level",
            },
        ],
        "authorisation": {
            "required": True,
            "granted": False,
            "granted_on": None,
            "document": None,
            "quote": None,
            "note": (
                "No dated grant exists. A grant naming the twelve cells, the determinism rerun and "
                "the result artifact must be recorded against this record before an arm is built "
                "or a cell is opened. This preregistration authorises nothing to run."
            ),
        },
        "runner": {
            "built": False,
            "planned_module": "benchmarks/presence_band_rank_2_arm.py",
            "cells_run": 0,
            "why": "this record freezes the design and corrected gates only; no arm module exists and no cell has run",
        },
        "cost": {
            "cells": 12,
            "witness_cells": "one fresh-process determinism rerun",
            "cycles": 120,
            "wall_clock_estimate": "twelve cells plus one rerun at 120 cycles each",
        },
        "stop_condition": (
            "No cell runs until a dated grant is recorded. After the grant, the block closes when "
            "the twelve cells and the rerun have produced their parts, B1-B8 have been scored once "
            "in the frozen order, and the verdict is recorded. Any gate failure is VOID; no cell is "
            "rerun to escape a gate and no gate is amended after a result."
        ),
        "not_evidence": (
            "A preregistration, not a result. No cell has run. BAND-1 remains VOID and its cells are "
            "not re-read; Q2's CAP LIMITING and Q4's CONVERSION STAGE MEASURED are not re-scored. "
            "This record licenses no capability, retention or transfer claim."
        ),
        "amendments": [],
    }


def render(doc: dict) -> str:
    design = doc["design"]
    engine = doc["engine"]
    b5 = doc["b5_correction"]
    lines = [
        "# PRESENCE-BAND-2 — corrected B5 and a live rank reading",
        "",
        "**Status.** %s. This page is rendered from `%s`; it is not edited by hand."
        % (doc["status"], RECORD.relative_to(ROOT)),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Preregistration | `%s` |" % doc["prereg"],
        "| Frozen on | %s |" % doc["frozen_on"],
        "| Engine | %s, cap %d, %s |" % (engine["version"], engine["cap"], engine["edit"]),
        "| Cells planned | %d (%s) |" % (design["cells"], design["cells_arithmetic"]),
        "| Seeds | %s |" % ", ".join(str(seed) for seed in design["seeds"]),
        "| Caps | %s |" % ", ".join(str(cap) for cap in design["caps"]),
        "| Cycles | %d |" % design["cycles"],
        "| Named band edges | %d |" % doc["band"]["total"],
        "| Runner | not built |",
        "| Cells run | 0 |",
        "| Authorisation | not granted |",
        "",
        "## Why a second block",
        "",
        doc["program"]["relationship"],
        "",
        "BAND-1's B5 required the cap-112 transition allocation to be exactly **56**. That was "
        "the wrong reading of the engine's allocation: 56 is a guaranteed floor, and unused "
        "cooccurrence slots are backfilled with further transitions. Its first rank comparison "
        "also read served edges as character tuples, so it resolved no rank. BAND-2 corrects "
        "both before any cell and keeps the 62 named edges and the same Q4 worlds.",
        "",
        "## The corrected B5",
        "",
        "**Previous condition.** %s" % b5["previous_gate"],
        "",
        "**Why it was wrong.** %s" % b5["why_it_was_wrong"],
        "",
        "**Source.** `%s`." % b5["source"],
        "",
        "**New condition.** %s" % b5["new_condition"],
        "",
        b5["does_not_change"],
        "",
        "## Fixed rank reading",
        "",
        "**Previous defect.** %s" % doc["rank_reading"]["previous_defect"],
        "",
        "**Rule.** %s" % doc["rank_reading"]["rule"],
        "",
        "**Fixture.** %s" % doc["rank_reading"]["fixture"],
        "",
        "## The 62 named edges",
        "",
        "These are Q4's never-served present transitions whose minimum block rank in the ceiling "
        "universe was 21–40. The identity block is copied from BAND-1's frozen band; BAND-2 does "
        "not re-derive a fresh band.",
        "",
        "| Seed | Edge | Q4 best rank |",
        "| ---: | --- | ---: |",
    ]
    for seed, row in doc["band"]["seeds"].items():
        for source, target, rank in row["edges"]:
            lines.append("| %s | `%s>%s` | %s |" % (seed, source, target, rank))
    lines += [
        "",
        "| Seed | World digest | Present | Named edges |",
        "| ---: | --- | ---: | ---: |",
    ]
    for seed, row in doc["band"]["seeds"].items():
        lines.append("| %s | `%s` | %d | %d |"
                     % (seed, row["world_digest"], row["present"], len(row["edges"])))
    lines += [
        "",
        "**Derivation.** %s" % doc["band"]["derivation"],
        "",
        "## Design",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Arms | cap 40 and cap 112 |",
        "| Variable | `SleepService.MAX_PREDICTIONS`, set per cell |",
        "| Observer | %s |" % design["observer"],
        "| World | %s |" % design["world"],
        "| Pairing | %s |" % design["pairing"],
        "| Reuse | %s |" % design["reuse"],
        "| Freshness | %s |" % design["freshness"],
        "| Cycles | %d |" % design["cycles"],
        "| Cells | %d |" % design["cells"],
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
        "## No cell has run",
        "",
        "**Authorisation.** %s" % doc["authorisation"]["note"],
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


def read_served_edge(item) -> tuple[str, str]:
    """Parse one served edge strictly; character tuples are the defect this rejects."""
    if not isinstance(item, str):
        raise RankReadingError("served edge is not a string: %r" % (item,))
    if item.count(">") != 1:
        raise RankReadingError("served edge is not a single source>target pair: %r" % (item,))
    source, target = item.split(">")
    if not source or not target:
        raise RankReadingError("served edge has an empty tag: %r" % (item,))
    return source, target


def served_edges(cell: dict) -> set[tuple[str, str]]:
    return {read_served_edge(item)
            for window in cell.get("windows_world") or [] for item in window}


def recorded_ranks(cell: dict) -> tuple[dict, dict]:
    ranks: dict[tuple[str, str], int] = {}
    relations: dict[tuple[str, str], str] = {}
    for cycle in cell.get("universe") or []:
        for row in cycle:
            edge = row["edge"]
            if isinstance(edge, str):
                edge = read_served_edge(edge)
            else:
                edge = tuple(edge)
            ranks[edge] = min(ranks.get(edge, 10 ** 9), int(row["rank"]))
            relations.setdefault(edge, row.get("relation"))
    return ranks, relations


def rank_reading(cell: dict) -> dict:
    """Read served edges and their ranks without ever defaulting a missing rank to 0."""
    served = served_edges(cell)
    ranks, relations = recorded_ranks(cell)
    transitions = {edge for edge in served if relations.get(edge) == "transition"}
    missing = sorted(edge for edge in served if edge not in ranks)
    max_rank = max((ranks[edge] for edge in transitions if edge in ranks), default=None)
    return {
        "served": len(served),
        "served_transitions": len(transitions),
        "max_served_transition_rank": max_rank,
        "missing_rank": ["%s>%s" % edge for edge in missing],
    }


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
    if len(seeds) != 6 or len(set(seeds)) != 6:
        found.append("the design does not hold six distinct seeds")
    if design.get("caps") != [40, 112] or design.get("shipped_cap") != 112:
        found.append("the caps are not 40 and 112 with 112 shipped")
    if design.get("cells") != len(seeds) * 2 or design.get("cycles") != 120:
        found.append("the cell or cycle count is not the frozen design")
    if "Q4" not in (design.get("reuse") or "") or "No new seed" not in (design.get("freshness") or ""):
        found.append("the Q4 reuse and the no-fresh-seed declaration are not stated")

    band = doc.get("band") or {}
    band_seeds = band.get("seeds") or {}
    if band.get("total") != BAND_TOTAL:
        found.append("the band total is not %d" % BAND_TOTAL)
    if set(band_seeds) != {str(seed) for seed in seeds}:
        found.append("the band's seeds are not the design's seeds")
    total = 0
    for seed, row in band_seeds.items():
        edges = row.get("edges") or []
        total += len(edges)
        if len({tuple(edge[:2]) for edge in edges}) != len(edges):
            found.append("seed %s names one edge twice" % seed)
        for edge in edges:
            if (not isinstance(edge, list) or len(edge) != 3
                    or not all(isinstance(part, str) and part for part in edge[:2])
                    or not 21 <= int(edge[2]) <= 40):
                found.append("seed %s has a malformed or out-of-band edge %r" % (seed, edge))
                break
    if total != BAND_TOTAL:
        found.append("the per-seed edges sum to %d, not %d" % (total, BAND_TOTAL))
    q4 = json.loads(Q4.read_text(encoding="utf-8")) if Q4.exists() else {}
    table = {str(row["seed"]): row for row in q4.get("stage_table", [])}
    for seed, row in band_seeds.items():
        if seed not in table:
            found.append("seed %s has no Q4 stage row" % seed)
        elif len(row.get("edges") or []) != table[seed].get("never_served_rank_half_to_cap"):
            found.append("seed %s's band is not Q4's 21-40 count" % seed)

    gates = doc.get("gates") or {}
    for gate in ("B1_build", "B2_world", "B3_band_identity", "B4_control_40",
                 "B5_cap_live", "B6_denominator", "B7_determinism", "B8_seed_axis"):
        if gate not in gates:
            found.append("the gate %s is missing" % gate)
    b5 = (gates.get("B5_cap_live") or "").lower()
    for needed in ("at least 56", "backfill", "floor", "exactly one", "two non-empty",
                   "minimum", "no recorded rank", "block rank 40", "112"):
        if needed not in b5:
            found.append("B5 does not carry %r" % needed)
    if "== 56" in b5 or "exactly 56" in b5:
        found.append("B5 still requires an exact 56-transition allocation")

    correction = doc.get("b5_correction") or {}
    source = correction.get("source") or ""
    if "sleep_extraction.py" not in source:
        found.append("B5's correction does not name the engine source")
    if SOURCE.exists():
        text = SOURCE.read_text(encoding="utf-8")
        if "transition_budget = returned_budget // 2" not in text:
            found.append("the engine source no longer guarantees the 56 floor")
        if "more_trans" not in text:
            found.append("the engine source no longer backfills with more transitions")
    else:
        found.append("the engine source is missing")

    rank = doc.get("rank_reading") or {}
    rule = (rank.get("rule") or "").lower()
    for needed in ("exactly one", "two non-empty", "minimum", "no recorded rank", "never defaulted"):
        if needed not in rule:
            found.append("the rank rule does not state %r" % needed)
    fixture = {
        "windows_world": [["amber>olive"]],
        "universe": [[{"edge": ["amber", "olive"], "rank": 41, "relation": "transition"}]],
    }
    reading = rank_reading(fixture)
    if reading["max_served_transition_rank"] != 41 or reading["missing_rank"]:
        found.append("the fixed rank reader does not resolve amber>olive at rank 41")
    try:
        read_served_edge("amberolive")
    except RankReadingError:
        pass
    else:
        found.append("the rank reader accepts an edge with no separator")

    auth = doc.get("authorisation") or {}
    if auth.get("granted") is not False:
        found.append("the record claims a grant")
    if auth.get("document") or auth.get("quote") or auth.get("granted_on"):
        found.append("an ungranted record carries grant fields")
    runner = doc.get("runner") or {}
    if runner.get("built") is not False or runner.get("cells_run") != 0:
        found.append("the record claims a built runner or a run cell")
    if runner.get("planned_module") != ARM.relative_to(ROOT).as_posix():
        found.append("the planned arm module is not %s" % ARM.relative_to(ROOT))

    acceptance = doc.get("acceptance") or {}
    quote = (acceptance.get("quote") or "").strip()
    decision_text = " ".join(DECISION.read_text(encoding="utf-8").split()) if DECISION.exists() else ""
    if not quote or quote not in decision_text:
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
        doc = record()
        PAGE.write_text(render(doc), encoding="utf-8")
        print("rendered %s" % PAGE.relative_to(ROOT))
        return 0
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    doc = record()
    print("presence band 2: %s, %d cells planned, %d named edges, runner not built, no grant"
          % (doc["status"], doc["design"]["cells"], doc["band"]["total"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
