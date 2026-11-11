"""PRESENCE-BAND-4: a confirmatory allocation block with an independent failure.

BAND-1's exact-56 B5 was a gate defect: at cap 112 the engine guarantees
``MAX_PREDICTIONS // 2 = 56`` transitions, fills the remaining budget with
cooccurrences, and backfills unused cooccurrence slots with further transitions.
The six seeds it ran served 64-69 transitions, which is 56 plus backfill, not a
second allocation rule. BAND-2 and BAND-3 replaced the exact point with a floor.

That repair is still not a confirmatory gate. A floor-only check accepts a short
window of 56 transitions and no cooccurrences, so it can pass without showing the
allocation law that produced 64-69. This block is the confirmation: on fresh
worlds it requires the full 112-row allocation identity ``transitions +
cooccurrences = 112`` with ``transitions >= 56`` and ``cooccurrences <= 56``, and
it separately requires the measured rank-21-40 band to be served at 112 and not
at 40. The two criteria can fail independently: a perfect band result cannot
rescue a failed allocation law, and a perfect allocation cannot rescue a failed
band.

No cell is run by this module. It freezes the record and page only; no grant, arm,
runner or result exists.

    ./.venv/bin/python -m benchmarks.presence_band_rank_4_prereg --freeze
    ./.venv/bin/python -m benchmarks.presence_band_rank_4_prereg --check
    ./.venv/bin/python -m benchmarks.presence_band_rank_4_prereg --render
"""
from __future__ import annotations

import argparse
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
RECORD = ROOT / "docs" / "presence_band_rank_4_prereg.json"
PAGE = ROOT / "docs" / "PRESENCE-BAND-RANK-4-PREREGISTRATION.md"
RUN = ROOT / "docs" / "presence_band_rank_4_run.json"
ARM = ROOT / "benchmarks" / "presence_band_rank_4_arm.py"
DECISION = ROOT / "docs" / "DECISION-ADMISSION-STEP.md"
SOURCE = ROOT / "organica" / "sleep_extraction.py"

ID = "PRESENCE-BAND-4"
STATUS = "FROZEN, NOT RUN"
FROZEN_ON = "2026-11-11"
SEEDS = (20612501, 20612502, 20612503, 20612504, 20612505, 20612506)
CAPS = (40, 112)
B5_FLOOR = 56
B5_WINDOW = 112
B5_COOC_MAX = 56
BAND_LOW = 21
BAND_HIGH = 40


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def band_edges(cell: dict) -> dict[tuple[str, str], int]:
    """The rank-21-40 present transitions, measured from the 112 ceiling."""
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


def allocation_law(cell: dict, *, cap: int, floor: int, cooc_max: int) -> dict:
    """Check the engine's full-window floor-plus-backfill allocation.

    A short window is not treated as a full allocation. A cell must contain at
    least one full ``cap``-row window; every full window must satisfy
    ``transitions + cooccurrences = cap``, ``transitions >= floor`` and
    ``cooccurrences <= cooc_max``. Every allocation row must sum to its own
    window. The rank reading is included so a rank ceiling at or below 40 cannot
    pass merely because the counts look right.
    """
    reasons: list[str] = []
    rows = cell.get("allocation") or []
    windows = cell.get("windows") or []
    if not rows:
        reasons.append("no allocation rows")
    if len(rows) != len(windows):
        reasons.append(
            "the cell has %d allocation rows and %d windows" % (len(rows), len(windows))
        )
    full = 0
    transition_counts: list[int] = []
    cooccurrence_counts: list[int] = []
    for index, (row, window) in enumerate(zip(rows, windows), start=1):
        transitions = row.get("transitions")
        cooccurrences = row.get("cooccurrences")
        if transitions is None or cooccurrences is None:
            reasons.append("cycle %d does not record both allocation counts" % index)
            continue
        transitions = int(transitions)
        cooccurrences = int(cooccurrences)
        transition_counts.append(transitions)
        cooccurrence_counts.append(cooccurrences)
        served = len(window)
        if transitions < 0 or cooccurrences < 0:
            reasons.append("cycle %d has a negative allocation" % index)
        if transitions + cooccurrences != served:
            reasons.append(
                "cycle %d: %d transitions + %d cooccurrences != %d served"
                % (index, transitions, cooccurrences, served)
            )
        if cooccurrences > cooc_max:
            reasons.append(
                "cycle %d: %d cooccurrences exceeds the %d-slot ceiling"
                % (index, cooccurrences, cooc_max)
            )
        if served == cap:
            full += 1
            if transitions < floor:
                reasons.append(
                    "cycle %d: the full window has %d transitions, below the floor of %d"
                    % (index, transitions, floor)
                )
            if transitions + cooccurrences != cap:
                reasons.append(
                    "cycle %d: the full window does not sum to %d" % (index, cap)
                )
            if transitions != cap - cooccurrences:
                reasons.append(
                    "cycle %d: the full window leaves an unfilled backfill slot" % index
                )
        elif served > cap:
            reasons.append("cycle %d: window holds %d rows, above %d" % (index, served, cap))
    if full == 0:
        reasons.append("no window reaches the full %d-row budget" % cap)
    if not transition_counts or max(transition_counts) < floor:
        reasons.append(
            "the maximum transition count is %s, below the floor of %d"
            % (max(transition_counts) if transition_counts else "absent", floor)
        )
    try:
        reading = rank_reading(cell)
    except (RankReadingError, ValueError) as exc:
        reasons.append("the served edges are not parseable: %s" % exc)
        reading = {"max_served_transition_rank": None, "missing_rank": []}
    max_rank = reading.get("max_served_transition_rank")
    if max_rank is None or max_rank <= BAND_HIGH:
        reasons.append(
            "the maximum served transition rank is %r, not above %d"
            % (max_rank, BAND_HIGH)
        )
    if reading.get("missing_rank"):
        reasons.append(
            "served transitions have no recorded rank: %s"
            % ", ".join(reading["missing_rank"])
        )
    return {
        "passed": not reasons,
        "cap": cap,
        "floor": floor,
        "cooccurrence_ceiling": cooc_max,
        "full_windows": full,
        "max_transitions": max(transition_counts) if transition_counts else None,
        "max_cooccurrences": max(cooccurrence_counts) if cooccurrence_counts else None,
        "max_served_transition_rank": max_rank,
        "missing_rank": reading.get("missing_rank") or [],
        "reasons": reasons,
    }


def _fixture(
    *,
    transitions: int = 64,
    cooccurrences: int = 48,
    window: int = 112,
    max_rank: int = 64,
    parse: str = "amber>olive",
    recorded: bool = True,
) -> dict:
    """A minimal cell for the allocation fixtures (not a band result)."""
    served = [parse] * window
    universe = [[{"edge": ["amber", "olive"], "rank": max_rank, "relation": "transition"}]]
    if not recorded:
        universe = []
    return {
        "cap": 112,
        "allocation": [{"transitions": transitions, "cooccurrences": cooccurrences}],
        "windows": [served],
        "windows_world": [served],
        "present_edges": [["amber", "olive"]],
        "universe": universe,
    }


def b5_fixture_results() -> dict[str, dict]:
    return {
        "pass_64_plus_48": allocation_law(
            _fixture(), cap=112, floor=B5_FLOOR, cooc_max=B5_COOC_MAX
        ),
        "pass_56_plus_56": allocation_law(
            _fixture(transitions=56, cooccurrences=56),
            cap=112,
            floor=B5_FLOOR,
            cooc_max=B5_COOC_MAX,
        ),
        "fail_56_only": allocation_law(
            _fixture(transitions=56, cooccurrences=0, window=56),
            cap=112,
            floor=B5_FLOOR,
            cooc_max=B5_COOC_MAX,
        ),
        "fail_short_20": allocation_law(
            _fixture(transitions=20, cooccurrences=20, window=40),
            cap=112,
            floor=B5_FLOOR,
            cooc_max=B5_COOC_MAX,
        ),
        "fail_sum": allocation_law(
            _fixture(transitions=64, cooccurrences=40),
            cap=112,
            floor=B5_FLOOR,
            cooc_max=B5_COOC_MAX,
        ),
        "fail_cooccurrence_ceiling": allocation_law(
            _fixture(transitions=64, cooccurrences=60, window=124),
            cap=112,
            floor=B5_FLOOR,
            cooc_max=B5_COOC_MAX,
        ),
        "fail_rank_ceiling": allocation_law(
            _fixture(max_rank=40), cap=112, floor=B5_FLOOR, cooc_max=B5_COOC_MAX
        ),
        "fail_unranked": allocation_law(
            _fixture(recorded=False), cap=112, floor=B5_FLOOR, cooc_max=B5_COOC_MAX
        ),
        "fail_malformed": allocation_law(
            _fixture(parse="amber>olive>extra"),
            cap=112,
            floor=B5_FLOOR,
            cooc_max=B5_COOC_MAX,
        ),
    }


def build() -> dict:
    return {
        "prereg": ID,
        "status": STATUS,
        "frozen_on": FROZEN_ON,
        "no_cells_run": True,
        "question": (
            "On the shipped 0.15.0 build, with six fresh worlds, does the cap-112 "
            "allocation satisfy the full-window floor-plus-backfill identity and does "
            "the measured rank-21-40 band enter service, with the allocation law and "
            "band service able to fail independently?"
        ),
        "program": {
            "draft": "docs/DECISION-ADMISSION-STEP.md",
            "question": "Q054",
            "relationship": (
                "BAND-1 froze an exact-56 allocation, observed 64-69, and was VOID on "
                "that gate. BAND-2 and BAND-3 corrected the point to a floor. BAND-4 is "
                "the confirmatory allocation block: it does not repeat the point, does "
                "not use 64-69 as a cutoff, and does not re-read BAND-1, BAND-2 or "
                "BAND-3. BAND-1 stays VOID; BAND-2 and BAND-3 stay unrun."
            ),
        },
        "reconciliation": {
            "frozen_point": (
                "BAND-1's B5 required exactly 56 transitions at cap 112."
            ),
            "engine_law": (
                "`organica/sleep_extraction.py` sets `transition_budget = "
                "returned_budget // 2` (56 at 112), seats up to 56 cooccurrences in "
                "the remainder, then backfills unused cooccurrence slots with further "
                "transitions (`more_trans`). A full window therefore has "
                "`transitions + cooccurrences = 112` with `transitions >= 56` and "
                "`cooccurrences <= 56`."
            ),
            "observed_64_69": (
                "The six BAND-1 cells served 64-69 transitions, so their full-window "
                "cooccurrence counts were 48-43. That is the floor plus backfill; it "
                "is not a new allocation rule and it is not an acceptance threshold."
            ),
            "why_not_exact_56": (
                "A correct engine can serve more than 56 transitions whenever fewer "
                "than 56 cooccurrence candidates fill the remainder. Requiring exactly "
                "56 rejects a healthy backfill."
            ),
            "why_not_floor_only": (
                "A floor-only gate accepts 56 transitions with no cooccurrences in a "
                "56-row window. That is not the full allocation law and would pass "
                "without showing the backfill that produced 64-69. BAND-4 therefore "
                "requires a full 112-row window and the sum identity."
            ),
            "not_fitted": (
                "The law and its fixtures are written from `sleep_extraction.py` "
                "before any BAND-4 cell. The observed 64-69 is a consistency check, "
                "not a calibrated range, and no threshold is set to 64 or 69."
            ),
        },
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
                "own served list and recording the pre-cap universe and allocation"
            ),
            "world": (
                "the compositional world family of PHASE_ACQUISITION at 120 cycles on "
                "six fresh seeds; no Q4, BAND-1, BAND-2 or BAND-3 world is reused"
            ),
            "pairing": (
                "each seed contributes one world and one stimulus to both caps; only the "
                "cap changes, and each band edge is paired across the two cells"
            ),
            "freshness": (
                "All six seeds are fresh at freeze time: seed_collisions over every "
                "docs JSON returns no hit. The record and page are the only allowed "
                "artifacts that name them."
            ),
            "reuse": (
                "No prior block's cells, named band or result is reused. The 64-69 "
                "observation is cited only as the prior that motivates the allocation "
                "law; it is not BAND-4 evidence."
            ),
        },
        "band": {
            "definition": (
                "For each seed, the band is every present transition whose minimum "
                "block rank in the cap-112 ceiling universe is 21-40. It is measured "
                "from the 112 arm and is not filtered by cap-40 service."
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
                "it. B4 measures whether the 40 arm served a band edge."
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
            {"stage": "S112", "definition": "band edges served in at least one cap-112 cycle", "role": "band endpoint"},
            {"stage": "A112", "definition": "band edges asserted at the end of the cap-112 run", "role": "secondary, reported not adjudicated"},
            {"stage": "alloc", "definition": "per cycle transitions and cooccurrences in the 112 window", "role": "allocation endpoint"},
            {"stage": "ledger", "definition": "per edge: rank, cycles served at each cap, asserted, relation", "role": "per-edge record"},
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
                "at cap 40 no band edge is served on any seed, and the 40-row allocator "
                "satisfies the same sum identity with its 20-transition floor; a band "
                "edge served at 40, an incomplete full window, or a 40-row allocation "
                "that does not sum fails B4"
            ),
            "B5_allocation_law": (
                "at cap 112 every cell has at least one full 112-row window; every full "
                "window satisfies transitions >= 56, cooccurrences <= 56 and "
                "transitions + cooccurrences = 112, and every allocation row sums to its "
                "own served window. The maximum served transition rank is above block "
                "rank 40, every served edge parses as exactly one source>target, and "
                "every served transition is ranked. A 56-transition, 56-row window; a "
                "64-transition, 104-row sum; a cooccurrence count above 56; a rank "
                "ceiling at 40; an unparseable edge; or an unranked served transition "
                "fails B5. B5 is not conditional on band service."
            ),
            "B6_denominator": (
                "each seed's band is non-empty and every band edge reaches the ledger; "
                "a zero band or a zero P is not measurable and is VOID, never 0.0"
            ),
            "B7_determinism": (
                "a fresh-process rerun of seed 20612501 at 112 reproduces its per-edge "
                "ledger and allocation exactly"
            ),
            "B8_seed_axis": (
                "the six 112 ledgers hold at least three distinct served-band edge sets; "
                "a repeated set is one world, not six"
            ),
        },
        "b5_fixture": {
            "pass_64_plus_48": "64 transitions + 48 cooccurrences in a 112-row window, maximum rank 64",
            "pass_56_plus_56": "56 transitions + 56 cooccurrences in a 112-row window, maximum rank 56",
            "fail_56_only": "56 transitions + 0 cooccurrences in a 56-row window",
            "fail_short_20": "20 transitions + 20 cooccurrences in a 40-row window",
            "fail_sum": "64 transitions + 40 cooccurrences in a 112-row window",
            "fail_cooccurrence_ceiling": "64 transitions + 60 cooccurrences in a 124-row window",
            "fail_rank_ceiling": "a full window whose maximum served transition rank is 40",
            "fail_unranked": "a served transition with no recorded rank",
            "fail_malformed": "an edge with more than one source>target separator",
            "rule": (
                "the same allocation_law helper is used by the record check and the "
                "future arm; the pass fixtures cover both the observed backfill shape "
                "and the exact floor, and every failure fixture must fail"
            ),
        },
        "acceptance": {
            "kind": "co-primary, independently falsifiable",
            "criterion_a": (
                "B5 passes: the cap-112 allocation law holds on every full window and "
                "the rank ceiling is live."
            ),
            "criterion_b": (
                "B3, B4 and B6 pass: every measured rank-21-40 band edge is served at "
                "112, none is served at 40, and the seed axis is live."
            ),
            "confirmed": "CONFIRMED only when both criterion A and criterion B pass.",
            "independent_failure": (
                "The criteria fail independently: a block with perfect band service but "
                "a failed B5 is ALLOCATION LAW NOT CONFIRMED. A block with a perfect "
                "allocation but any unserved band edge is BAND NOT CONFIRMED. Neither "
                "result can be averaged into or rescued by the other."
            ),
            "not_fitted": (
                "The 64-69 observation is not used as a threshold. The allocation "
                "identity is fixed from the engine source, and the band criterion is "
                "the same rank rule fixed before the cells."
            ),
            "source": "organica/sleep_extraction.py and docs/DECISION-ADMISSION-STEP.md",
        },
        "decision_table": [
            {
                "condition": "B1, B2, B3 identity, B6, B7 or B8 fails",
                "verdict": "VOID",
                "reading": "the block is unrun or non-reproducible and the failed gate names what did not happen",
                "decision": "record VOID; fix the failed gate and register a new block; read no acceptance",
            },
            {
                "condition": "allocation law fails, band service passes",
                "verdict": "ALLOCATION LAW NOT CONFIRMED",
                "reading": "the band can be served while the full-window floor-plus-backfill identity is false",
                "decision": "report the allocation failure; do not call the band a confirmation; fix the allocation rule before another band block",
            },
            {
                "condition": "allocation law passes, any band edge is unserved at 112 or served at 40",
                "verdict": "BAND NOT CONFIRMED",
                "reading": "the allocation is correct but the measured rank-21-40 band does not enter service as claimed",
                "decision": "report the per-edge misses; the next step is the admission rule, not another cap level",
            },
            {
                "condition": "allocation law and band service both pass on every seed",
                "verdict": "CONFIRMED",
                "reading": "the floor-plus-backfill law and fresh-world rank-21-40 service both hold",
                "decision": "record the confirmation; the owner decides any engine or promotion step; no capability claim",
            },
        ],
        "authorisation": {
            "required": True,
            "granted": False,
            "granted_on": None,
            "document": None,
            "quote": None,
            "note": (
                "No dated grant exists. A grant naming the twelve cells, the determinism "
                "rerun and the result artifact must be recorded against this record "
                "before an arm is built or a cell is opened. This record authorises "
                "nothing to run."
            ),
        },
        "runner": {
            "built": False,
            "planned_module": "benchmarks/presence_band_rank_4_arm.py",
            "cells_run": 0,
            "why": "the record and page precede any grant, arm or cell",
        },
        "cost": {
            "cells": 12,
            "witness_cells": "one fresh-process determinism rerun",
            "cycles": 120,
            "wall_clock_estimate": "twelve cells plus one rerun at 120 cycles each",
        },
        "stop_condition": (
            "No cell runs until a dated grant is recorded and the arm's preflight "
            "passes. After that, the block closes when the twelve cells and rerun have "
            "produced their parts, B1-B8 have been scored once in the frozen order, and "
            "the verdict is recorded. Any gate failure is VOID; no cell is rerun to "
            "escape a gate and no gate is amended after a result."
        ),
        "not_evidence": (
            "A preregistration and page, not a result. No grant, arm, runner or cell "
            "exists. BAND-1 stays VOID; BAND-2 and BAND-3 stay unrun and are not "
            "re-read. This record licenses no capability, retention or transfer claim."
        ),
        "amendments": [
            {
                "date": FROZEN_ON,
                "kind": "frozen",
                "note": (
                    "The confirmatory allocation block and its independent criteria "
                    "were frozen before any grant, arm or cell."
                ),
            },
            {
                "date": FROZEN_ON,
                "kind": "wording-correction",
                "note": (
                    "Before any grant, arm or cell, the acceptance text was corrected "
                    "to say explicitly that the two criteria fail independently. No "
                    "criterion, seed, gate or threshold changed."
                ),
            },
        ],
    }


def render(doc: dict) -> str:
    design = doc["design"]
    rec = doc["reconciliation"]
    lines = [
        "# PRESENCE-BAND-4 — confirmatory allocation block",
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
        "| Seeds | %s |" % ", ".join(str(seed) for seed in design["seeds"]),
        "| Caps | %s |" % ", ".join(str(cap) for cap in design["caps"]),
        "| Cycles | %d |" % design["cycles"],
        "| Band | %s |" % doc["band"]["size"],
        "| Runner | not built |",
        "| Cells run | 0 |",
        "| Authorisation | not granted |",
        "",
        "## The reconciliation",
        "",
        "**Frozen point.** %s" % rec["frozen_point"],
        "",
        "**Engine law.** %s" % rec["engine_law"],
        "",
        "**Observed 64-69.** %s" % rec["observed_64_69"],
        "",
        "**Why not exact 56.** %s" % rec["why_not_exact_56"],
        "",
        "**Why not a floor alone.** %s" % rec["why_not_floor_only"],
        "",
        "**Not fitted to the observation.** %s" % rec["not_fitted"],
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
        "## Band",
        "",
        "**Definition.** %s" % doc["band"]["definition"],
        "",
        "**Derivation.** %s" % doc["band"]["derivation"],
        "",
        "**Zero band.** %s" % doc["band"]["zero_band"],
        "",
        "**Service separation.** %s" % doc["band"]["service_separation"],
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
    lines += [
        "",
        "## B5 fixtures",
        "",
        "| Fixture | Expected |",
        "| --- | --- |",
        "| %s | PASS |" % doc["b5_fixture"]["pass_64_plus_48"],
        "| %s | PASS |" % doc["b5_fixture"]["pass_56_plus_56"],
        "| %s | FAIL |" % doc["b5_fixture"]["fail_56_only"],
        "| %s | FAIL |" % doc["b5_fixture"]["fail_short_20"],
        "| %s | FAIL |" % doc["b5_fixture"]["fail_sum"],
        "| %s | FAIL |" % doc["b5_fixture"]["fail_cooccurrence_ceiling"],
        "| %s | FAIL |" % doc["b5_fixture"]["fail_rank_ceiling"],
        "| %s | FAIL |" % doc["b5_fixture"]["fail_unranked"],
        "| %s | FAIL |" % doc["b5_fixture"]["fail_malformed"],
        "",
        doc["b5_fixture"]["rule"],
        "",
        "## Acceptance can fail independently",
        "",
        "**Criterion A — allocation.** %s" % doc["acceptance"]["criterion_a"],
        "",
        "**Criterion B — band.** %s" % doc["acceptance"]["criterion_b"],
        "",
        "**Confirmed.** %s" % doc["acceptance"]["confirmed"],
        "",
        "**Independent failure.** %s" % doc["acceptance"]["independent_failure"],
        "",
        "**Not fitted.** %s" % doc["acceptance"]["not_fitted"],
        "",
        "Source: `%s`." % doc["acceptance"]["source"],
        "",
        "## Decision table",
        "",
        "| Condition | Verdict | Reading | Decision |",
        "| --- | --- | --- | --- |",
    ]
    for row in doc["decision_table"]:
        lines.append(
            "| %s | **%s** | %s | %s |"
            % (row["condition"], row["verdict"], row["reading"], row["decision"])
        )
    lines += [
        "",
        "## Grant and stop",
        "",
        "**Authorisation.** %s" % doc["authorisation"]["note"],
        "",
        "**Cost.** %d cells (%s) x %d cycles."
        % (doc["cost"]["cells"], doc["cost"]["witness_cells"], doc["cost"]["cycles"]),
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
        found.append("%s exists although the record says the arm is not built" % ARM.relative_to(ROOT))

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
    if "No prior block" not in (design.get("reuse") or ""):
        found.append("the design does not refuse prior-block reuse")
    try:
        from benchmarks.presence_cap_experiment import seed_collisions
        collisions = seed_collisions(seeds, allow=(RECORD, PAGE))
        if collisions:
            found.append("seeds collide with existing artifacts: %r" % collisions)
    except Exception as exc:  # pragma: no cover
        found.append("the freshness scan could not run: %s" % exc)

    rec = doc.get("reconciliation") or {}
    for needed in ("floor", "backfill", "64-69", "not an acceptance threshold", "full 112-row"):
        if needed not in (rec.get("observed_64_69") or "") and needed not in (rec.get("engine_law") or "") and needed not in (rec.get("why_not_floor_only") or ""):
            found.append("the reconciliation does not carry %r" % needed)
    if "not an exact 56" not in (rec.get("frozen_point") or "").lower() and "exactly 56" not in (rec.get("frozen_point") or "").lower():
        found.append("the reconciliation does not name the exact-56 defect")

    gates = doc.get("gates") or {}
    for gate in ("B1_build", "B2_world_fresh", "B3_band_identity", "B4_control_40",
                 "B5_allocation_law", "B6_denominator", "B7_determinism", "B8_seed_axis"):
        if gate not in gates:
            found.append("the gate %s is missing" % gate)
    b5 = (gates.get("B5_allocation_law") or "").lower()
    for needed in ("112-row", "transitions >= 56", "cooccurrences <= 56", "transitions + cooccurrences = 112", "not conditional"):
        if needed not in b5:
            found.append("B5 does not carry %r" % needed)
    if "exactly 56" in b5:
        found.append("B5 still requires an exact 56-transition allocation")

    fixtures = b5_fixture_results()
    for name in ("pass_64_plus_48", "pass_56_plus_56"):
        if fixtures[name]["passed"] is not True:
            found.append("B5 does not pass %s: %s" % (name, fixtures[name]["reasons"]))
    for name in ("fail_56_only", "fail_short_20", "fail_sum", "fail_cooccurrence_ceiling",
                 "fail_rank_ceiling", "fail_unranked", "fail_malformed"):
        if fixtures[name]["passed"] is not False:
            found.append("B5 passes the %s failure fixture" % name)

    acceptance = doc.get("acceptance") or {}
    if "co-primary" not in (acceptance.get("kind") or ""):
        found.append("acceptance is not co-primary")
    if "independently" not in (acceptance.get("independent_failure") or "").lower():
        found.append("acceptance does not state an independent failure")
    if "not used as a threshold" not in (acceptance.get("not_fitted") or ""):
        found.append("acceptance does not refuse the 64-69 threshold")

    auth = doc.get("authorisation") or {}
    if auth.get("granted") is not False:
        found.append("an unrun confirmatory block claims a grant")
    runner = doc.get("runner") or {}
    if runner.get("built") is not False or runner.get("cells_run") != 0:
        found.append("the record claims a built arm or a run cell")
    if runner.get("planned_module") != ARM.relative_to(ROOT).as_posix():
        found.append("the planned arm module is not %s" % ARM.relative_to(ROOT))

    table = doc.get("decision_table") or []
    verdicts = {row.get("verdict") for row in table}
    for verdict in ("VOID", "ALLOCATION LAW NOT CONFIRMED", "BAND NOT CONFIRMED", "CONFIRMED"):
        if verdict not in verdicts:
            found.append("the decision table has no %s row" % verdict)
    if page.strip() != render(doc).strip():
        found.append("the page does not match the record; run --render")
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
    print(
        "presence band 4: %s, %d cells, fresh seeds, allocation law + band co-primary, no grant, no arm, no cell"
        % (doc["status"], doc["design"]["cells"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
