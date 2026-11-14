"""A1 design viability: C1 ceiling and conditional C2/C8 target competence.

This is a read-only report over committed no-arm artifacts.  It does not run a
cell, freeze a target, issue a grant, change a threshold or score a treatment
effect.

It records two different kinds of result:

* **C1 ceiling (proof for the current stream).**  C1's denominator is the set of
  paired-control available rows in the whole stream.  Target selection only
  partitions those rows; it cannot add available rows.  The largest denominator
  any selection can produce is therefore ``min(A_available, K_available)`` for
  the stream.  The candidate stream's maximum is below 60 on every seed, so the
  current C1 design is not reachable by target selection.
* **C2/C8 target competence (conditional).**  If C2 requires baseline A and K,
  the current N4 and N20 target blocks cannot supply a clean C8 block: N4 has at
  most 3 clean rows per seed for a 4-row block, and N20 has at most 12 for a
  20-row block.  C2 is a treatment gate, so a no-arm baseline cannot prove that
  a missing baseline path remains missing under treatment.  The report records
  this as a conditional target-selection incompatibility, not as a proof that
  C2 or C8 must fail.

    python -m benchmarks.a1_design_viability --write
    python -m benchmarks.a1_design_viability --check
    python -m benchmarks.a1_design_viability --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BASELINE_PATH = DOCS / "a1_baseline_availability.json"
TARGET_VIABILITY_PATH = DOCS / "a1_target_viability.json"
TARGET_SELECTION_PATH = DOCS / "a1_target_selection.json"
OUT_PATH = DOCS / "a1_design_viability.json"
PAGE_PATH = DOCS / "A1-DESIGN-VIABILITY.md"
ID = "A1-DESIGN-VIABILITY-1"
DATE = "2026-11-14"
KIND = "a1_design_viability"
SEEDS = (20630101, 20630102, 20630103, 20630104, 20630105, 20630106)
C1_FLOOR = 60
C8_ROWS = {"N4": 4, "N20": 20}
STREAMS = ("candidate_stream", "cell_stream")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _ceiling_row(seed: int, source: dict) -> dict:
    a = int(source["A_available"])
    k = int(source["K_available"])
    maximum = min(a, k)
    return {
        "seed": seed,
        "rows": int(source["candidate_rows"]),
        "A_available": a,
        "K_available": k,
        "max_attainable": maximum,
        "floor": C1_FLOOR,
        "shortfall": max(0, C1_FLOOR - maximum),
        "surplus": max(0, maximum - C1_FLOOR),
        "reaches_floor": maximum >= C1_FLOOR,
    }


def _stream(per_seed: list[dict]) -> dict:
    maxima = [row["max_attainable"] for row in per_seed]
    return {
        "per_seed": per_seed,
        "min_attainable": min(maxima),
        "max_attainable": max(maxima),
        "seeds_reaching_floor": sum(1 for row in per_seed if row["reaches_floor"]),
        "seeds_below_floor": sum(1 for row in per_seed if not row["reaches_floor"]),
    }


def _reverse(edge: str) -> str:
    left, right = edge.split(">", 1)
    return "%s>%s" % (right, left)


def _composition_row(seed: int, candidate: set[str], cell_edges: set[str],
                     cell_row: dict, candidate_row: dict) -> dict:
    reverse = {_reverse(edge) for edge in candidate}
    in_candidate = cell_edges & candidate
    in_reverse = cell_edges & reverse
    extra = cell_edges - candidate - reverse
    unique = {frozenset(edge.split(">", 1)) for edge in cell_edges}
    return {
        "seed": seed,
        "candidate_edges": len(candidate),
        "reverse_orientations": len(in_reverse),
        "extra_orientations": len(extra),
        "cell_rows": len(cell_edges),
        "unique_undirected": len(unique),
        "all_candidate_edges_present": candidate <= cell_edges,
        "candidate_max_c1": candidate_row["max_attainable"],
        "cell_max_c1": cell_row["max_attainable"],
        "inflation": cell_row["max_attainable"] - candidate_row["max_attainable"],
    }


def _composition(per_seed: list[dict]) -> dict:
    return {
        "per_seed": per_seed,
        "candidate_rows": sum(row["candidate_edges"] for row in per_seed),
        "reverse_orientations": sum(row["reverse_orientations"] for row in per_seed),
        "extra_orientations": sum(row["extra_orientations"] for row in per_seed),
        "cell_rows": sum(row["cell_rows"] for row in per_seed),
        "unique_undirected": sum(row["unique_undirected"] for row in per_seed),
        "all_candidate_edges_present": all(
            row["all_candidate_edges_present"] for row in per_seed),
        "unique_c1_min": min(row["candidate_max_c1"] for row in per_seed),
        "unique_c1_max": max(row["candidate_max_c1"] for row in per_seed),
        "conclusion": (
            "The 112-row cell stream is the candidate stream plus reverse "
            "orientations, not a wider independent universe. The four-seed "
            "apparent C1 pass is reverse-orientation duplication; on unique "
            "undirected edges the ceiling is still the candidate 31-44, below "
            "the 60-row floor on every seed."
        ),
    }


def _pool_row(seed: int, candidate: set[str], rows: dict[str, dict]) -> dict:
    a = sum(1 for edge in candidate if rows[edge]["A"])
    k = sum(1 for edge in candidate if rows[edge]["K"])
    both = sum(1 for edge in candidate if rows[edge]["A"] and rows[edge]["K"])
    required = C8_ROWS["N20"]
    return {
        "seed": seed,
        "candidate_edges": len(candidate),
        "A_available": a,
        "K_available": k,
        "A_and_K_available": both,
        "c8_rows_required": required,
        "pool_sufficient": both >= required,
    }


def _target_pool(per_seed: list[dict]) -> dict:
    return {
        "per_seed": per_seed,
        "c8_rows_required": C8_ROWS["N20"],
        "min_A_and_K_available": min(row["A_and_K_available"] for row in per_seed),
        "max_A_and_K_available": max(row["A_and_K_available"] for row in per_seed),
        "seeds_sufficient": sum(1 for row in per_seed if row["pool_sufficient"]),
        "conclusion": (
            "The candidate pool contains 23-36 A&K-available edges per seed, "
            "enough to construct a 20-row competent block on all six seeds. "
            "The current N20 selection has only 5-12 clean rows, so the current "
            "C2/C8 problem is a selection problem, not a supply problem. C1 is "
            "still not repaired: its full-stream K availability is 31-44."
        ),
    }


def _competence_row(seed: int, source: dict, key: str) -> dict:
    clean = int(source["fully_c2_viable"])
    required = C8_ROWS[key]
    return {
        "seed": seed,
        "fully_c2_viable": clean,
        "c8_rows_required": required,
        "shortfall": required - clean,
        "clean_c8_block_possible": clean >= required,
    }


def _competence_design(key: str, per_seed: list[dict]) -> dict:
    clean = [row["fully_c2_viable"] for row in per_seed]
    required = C8_ROWS[key]
    return {
        "c8_rows_required": required,
        "per_seed": per_seed,
        "max_clean_rows": max(clean),
        "total_clean_rows": sum(clean),
        "seeds_clean_block_possible": sum(
            1 for row in per_seed if row["clean_c8_block_possible"]),
        "seeds_needing_more_clean_rows": sum(
            1 for row in per_seed if not row["clean_c8_block_possible"]),
    }


def build() -> dict:
    baseline = _load(BASELINE_PATH)
    viability = _load(TARGET_VIABILITY_PATH)
    target = _load(TARGET_SELECTION_PATH)
    by_seed = {int(row["seed"]): row for row in baseline.get("per_seed") or []}
    target_by_seed = {int(seed): row for seed, row in (target.get("per_seed") or {}).items()}
    if set(by_seed) != set(SEEDS) or set(target_by_seed) != set(SEEDS):
        raise ValueError("source artifacts are not on the registered six seeds")

    candidate_sets = {seed: set(target_by_seed[seed]["u"]) for seed in SEEDS}
    candidate = _stream([
        _ceiling_row(seed, by_seed[seed]["protocol"]) for seed in SEEDS
    ])
    cell = _stream([
        _ceiling_row(seed, by_seed[seed]) for seed in SEEDS
    ])
    composition_rows = []
    pool_rows = []
    for index, seed in enumerate(SEEDS):
        cell_edges = {row["edge"] for row in by_seed[seed]["rows"]}
        composition_rows.append(_composition_row(
            seed, candidate_sets[seed], cell_edges,
            cell["per_seed"][index], candidate["per_seed"][index],
        ))
        pool_rows.append(_pool_row(
            seed, candidate_sets[seed],
            {row["edge"]: row for row in by_seed[seed]["rows"]},
        ))
    composition = _composition(composition_rows)
    target_pool = _target_pool(pool_rows)
    if not composition["all_candidate_edges_present"]:
        raise ValueError("the cell stream drops a candidate edge")
    designs = viability.get("designs") or {}
    if set(designs) != set(C8_ROWS):
        raise ValueError("target-viability report does not contain N4 and N20")
    competence = {}
    for key in ("N4", "N20"):
        rows = {int(row["seed"]): row for row in designs[key].get("per_seed") or []}
        if set(rows) != set(SEEDS):
            raise ValueError("%s seed block is not the registered six seeds" % key)
        competence[key] = _competence_design(key, [
            _competence_row(seed, rows[seed], key) for seed in SEEDS
        ])

    c1_ok = candidate["seeds_reaching_floor"] == 6
    cell_ok = cell["seeds_reaching_floor"] == 6
    clean_ok = all(
        competence[key]["seeds_clean_block_possible"] == 6 for key in C8_ROWS
    )
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": (
            "FLAGGED — C1 CEILING BELOW FLOOR; C2/C8 TARGET COMPETENCE CONDITIONAL"
            if not c1_ok and not clean_ok
            else "CHECK — DESIGN VIABILITY DIFFERS FROM THE RECORDED EXPECTATION"
        ),
        "source_artifacts": {
            "baseline_availability": BASELINE_PATH.relative_to(ROOT).as_posix(),
            "target_viability": TARGET_VIABILITY_PATH.relative_to(ROOT).as_posix(),
            "target_selection": TARGET_SELECTION_PATH.relative_to(ROOT).as_posix(),
        },
        "c1_ceiling": {
            "floor": C1_FLOOR,
            "proof": (
                "C1's denominator is the count of paired-control available rows "
                "across every target and non-target row in the stream. Target "
                "selection only partitions those rows; it cannot add available "
                "rows. The largest denominator any target selection can produce "
                "is therefore min(A_available, K_available) for the stream."
            ),
            "candidate_stream": {
                **candidate,
                "edge_count": [row["rows"] for row in candidate["per_seed"]],
                "conclusion": (
                    "Every seed's maximum is below the 60-row floor. The current "
                    "candidate stream is not C1-capable, even if every candidate "
                    "is selected and every available row is retained. This is a "
                    "branch-closing result for target selection on this stream."
                ),
            },
            "cell_stream": {
                **cell,
                "edge_count": [row["rows"] for row in cell["per_seed"]],
                "conclusion": (
                    "The 112-row cell stream reaches 60 on four seeds, but that "
                    "is reverse-orientation duplication rather than a wider "
                    "independent universe. On unique undirected edges the C1 "
                    "ceiling remains 31-44, below 60 on every seed. Switching to "
                    "it also changes the C4 stream to 108/92 directed rows, or "
                    "59-60/43-44 unique non-target rows."
                ),
            },
            "stream_composition": composition,
            "conclusion": (
                "The current registered design is not C1-capable under either "
                "reported stream. Target selection cannot repair the candidate "
                "stream; a new universe, a different seed block with better "
                "baseline availability, or a changed C1 estimator is required."
            ),
            "what_it_does_not_mean": (
                "This does not establish that A1 is impossible in principle. A "
                "different universe, seed block or C1 estimator could satisfy "
                "the floor. It establishes that the current stream and floor "
                "cannot be reconciled by selecting a different target block."
            ),
        },
        "c2_c8_competence": {
            "status": "CONDITIONAL — NOT A PROOF OF C2 OR C8 FAILURE",
            "assumption": (
                "This section treats baseline A and K availability as a "
                "precondition for a clean C2 row and a clean C8 double block. "
                "Under that target-competence reading, a row lacking baseline A "
                "or K cannot support all of C2's cells and cannot test a genuine "
                "A-K- double block."
            ),
            "induction_caveat": (
                "C2 is a treatment gate, not a no-arm gate. The no-arm baseline "
                "cannot prove that a missing baseline path remains missing under "
                "A- or K+ treatment. If the unblocked arm can induce the absent "
                "path, exact C2 remains unmeasured. The counts are a conditional "
                "target-selection incompatibility, not a proof that C2 or C8 "
                "must fail."
            ),
            "relationship": (
                "A1-TARGET-VIABILITY-1 reports carrier-missing exposure under "
                "the same baseline A/K reading. This report makes that reading "
                "explicit and does not treat it as proof of treatment failure."
            ),
            "designs": competence,
            "target_pool": target_pool,
            "conclusion": (
                "Under the stated competence reading, N4 has at most 3 clean "
                "rows per seed for a 4-row block and N20 has at most 12 for a "
                "20-row block. Neither current target set supplies a clean C8 "
                "block. The candidate pool has 23-36 A&K-available edges, so a "
                "20-row competent block is constructible by a new selection "
                "rule; the current N20 selection, not the supply, is the "
                "C2/C8 problem. C1 remains unresolved. Exact C2/C8 adjudication "
                "still requires cells or a pre-registered competence filter; "
                "the current data do not prove treatment failure."
            ),
        },
        "disposition": (
            "Do not freeze or run the current A1 design on these records. C1 is "
            "not target-selectable, and target competence requires an owner "
            "rule. A1 must be redesigned with a C1-capable universe or seed "
            "block and a pre-registered competence rule, or parked. No cell, "
            "target freeze, grant or threshold change is authorised."
        ),
        "not_evidence": (
            "A read-only design-viability report over committed no-arm "
            "artifacts. It runs no A1 cell, freezes no target, changes no "
            "threshold and measures no treatment effect. The C2/C8 section is "
            "conditional on baseline target competence, not a C2 or C8 verdict."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("report kind")
    if doc.get("id") != ID:
        found.append("report id")
    if not str(doc.get("status") or "").startswith("FLAGGED — C1 CEILING"):
        found.append("report status")
    c1 = doc.get("c1_ceiling") or {}
    if c1.get("floor") != C1_FLOOR:
        found.append("C1 floor changed")
    for key in STREAMS:
        stream = c1.get(key) or {}
        rows = stream.get("per_seed") or []
        if [row.get("seed") for row in rows] != list(SEEDS):
            found.append("%s seed block changed" % key)
            continue
        for row in rows:
            expected = min(row.get("A_available", -1), row.get("K_available", -1))
            if row.get("max_attainable") != expected:
                found.append("%s seed %s ceiling is not min(A,K)"
                             % (key, row.get("seed")))
            if row.get("shortfall") != max(0, C1_FLOOR - expected):
                found.append("%s seed %s shortfall is inconsistent"
                             % (key, row.get("seed")))
            if row.get("surplus") != max(0, expected - C1_FLOOR):
                found.append("%s seed %s surplus is inconsistent"
                             % (key, row.get("seed")))
            if row.get("reaches_floor") != (expected >= C1_FLOOR):
                found.append("%s seed %s floor flag is inconsistent"
                             % (key, row.get("seed")))
        maxima = [row.get("max_attainable") for row in rows]
        if stream.get("min_attainable") != min(maxima):
            found.append("%s minimum ceiling is inconsistent" % key)
        if stream.get("max_attainable") != max(maxima):
            found.append("%s maximum ceiling is inconsistent" % key)
        if stream.get("seeds_reaching_floor") != sum(
                1 for row in rows if row.get("reaches_floor")):
            found.append("%s floor count is inconsistent" % key)
    composition = c1.get("stream_composition") or {}
    composition_rows = composition.get("per_seed") or []
    if [row.get("seed") for row in composition_rows] != list(SEEDS):
        found.append("stream-composition seed block changed")
    else:
        for row in composition_rows:
            parts = (row.get("candidate_edges", 0)
                     + row.get("reverse_orientations", 0)
                     + row.get("extra_orientations", 0))
            if row.get("cell_rows") != parts:
                found.append("seed %s stream composition is inconsistent"
                             % row.get("seed"))
            if not row.get("all_candidate_edges_present"):
                found.append("seed %s drops a candidate edge" % row.get("seed"))
            if row.get("unique_undirected", 0) < row.get("candidate_edges", 0):
                found.append("seed %s unique count is below candidates"
                             % row.get("seed"))
            if row.get("inflation") != (
                    row.get("cell_max_c1", 0) - row.get("candidate_max_c1", 0)):
                found.append("seed %s C1 inflation is inconsistent"
                             % row.get("seed"))
        for total_key, row_key in (
                ("candidate_rows", "candidate_edges"),
                ("reverse_orientations", "reverse_orientations"),
                ("extra_orientations", "extra_orientations"),
                ("cell_rows", "cell_rows"),
                ("unique_undirected", "unique_undirected")):
            if composition.get(total_key) != sum(
                    row.get(row_key, 0) for row in composition_rows):
                found.append("stream-composition total %s is inconsistent" % total_key)
    competence = doc.get("c2_c8_competence") or {}
    if not str(competence.get("status") or "").startswith("CONDITIONAL"):
        found.append("C2/C8 status is not conditional")
    designs = competence.get("designs") or {}
    if set(designs) != set(C8_ROWS):
        found.append("C2/C8 design block is not N4/N20")
        return found
    for key, required in C8_ROWS.items():
        block = designs[key]
        rows = block.get("per_seed") or []
        if [row.get("seed") for row in rows] != list(SEEDS):
            found.append("%s C2/C8 seed block changed" % key)
            continue
        for row in rows:
            if row.get("c8_rows_required") != required:
                found.append("%s seed %s C8 row requirement changed"
                             % (key, row.get("seed")))
            if row.get("shortfall") != required - row.get("fully_c2_viable", 0):
                found.append("%s seed %s competence shortfall is inconsistent"
                             % (key, row.get("seed")))
            if row.get("clean_c8_block_possible") != (
                    row.get("fully_c2_viable", 0) >= required):
                found.append("%s seed %s competence flag is inconsistent"
                             % (key, row.get("seed")))
        if block.get("max_clean_rows") != max(
                row.get("fully_c2_viable", 0) for row in rows):
            found.append("%s maximum clean rows is inconsistent" % key)
        if block.get("total_clean_rows") != sum(
                row.get("fully_c2_viable", 0) for row in rows):
            found.append("%s total clean rows is inconsistent" % key)
        if block.get("seeds_clean_block_possible") != sum(
                1 for row in rows if row.get("clean_c8_block_possible")):
            found.append("%s clean-block seed count is inconsistent" % key)
    pool = competence.get("target_pool") or {}
    pool_rows = pool.get("per_seed") or []
    if [row.get("seed") for row in pool_rows] != list(SEEDS):
        found.append("competent-pool seed block changed")
    else:
        required = C8_ROWS["N20"]
        for row in pool_rows:
            if row.get("c8_rows_required") != required:
                found.append("seed %s pool C8 requirement changed" % row.get("seed"))
            if row.get("pool_sufficient") != (
                    row.get("A_and_K_available", 0) >= required):
                found.append("seed %s pool sufficiency is inconsistent"
                             % row.get("seed"))
        if pool.get("min_A_and_K_available") != min(
                row.get("A_and_K_available", 0) for row in pool_rows):
            found.append("pool minimum is inconsistent")
        if pool.get("max_A_and_K_available") != max(
                row.get("A_and_K_available", 0) for row in pool_rows):
            found.append("pool maximum is inconsistent")
        if pool.get("seeds_sufficient") != sum(
                1 for row in pool_rows if row.get("pool_sufficient")):
            found.append("pool sufficient-seed count is inconsistent")
    return found


def self_test() -> list[str]:
    found: list[str] = []
    row = _ceiling_row(1, {"candidate_rows": 64, "A_available": 44, "K_available": 44})
    if row["max_attainable"] != 44 or row["shortfall"] != 16 or row["reaches_floor"]:
        found.append("ceiling fixture is wrong")
    row = _ceiling_row(1, {"candidate_rows": 64, "A_available": 60, "K_available": 61})
    if row["max_attainable"] != 60 or row["shortfall"] != 0 or not row["reaches_floor"]:
        found.append("reaching ceiling fixture is wrong")
    row = _competence_row(1, {"fully_c2_viable": 10}, "N20")
    if row["shortfall"] != 10 or row["clean_c8_block_possible"]:
        found.append("competence fixture is wrong")
    row = _competence_row(1, {"fully_c2_viable": 20}, "N20")
    if row["shortfall"] != 0 or not row["clean_c8_block_possible"]:
        found.append("clean competence fixture is wrong")
    row = _composition_row(
        1, {"a>b"}, {"a>b", "b>a"},
        {"max_attainable": 2}, {"max_attainable": 1})
    if row["reverse_orientations"] != 1 or row["cell_rows"] != 2:
        found.append("stream-composition fixture is wrong")
    if row["unique_undirected"] != 1 or row["inflation"] != 1:
        found.append("stream-dedupe fixture is wrong")
    row = _pool_row(1, {"a>b"}, {"a>b": {"A": True, "K": True}})
    if row["A_and_K_available"] != 1 or row["pool_sufficient"]:
        found.append("competent-pool fixture is wrong")
    return found


def _c1_table(doc: dict, key: str) -> list[str]:
    stream = doc["c1_ceiling"][key]
    lines = [
        "| Seed | Stream rows | Baseline A | Baseline K | Max attainable C1 | Floor | Shortfall | Reaches floor? |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in stream["per_seed"]:
        lines.append(
            "| `%d` | %d | %d | %d | %d | %d | %d | %s |" % (
                row["seed"], row["rows"], row["A_available"],
                row["K_available"], row["max_attainable"], row["floor"],
                row["shortfall"], "YES" if row["reaches_floor"] else "NO",
            )
        )
    lines += [
        "",
        "**Seeds reaching the floor:** **%d/6**; maximum attainable **%d**, minimum **%d**." % (
            stream["seeds_reaching_floor"], stream["max_attainable"],
            stream["min_attainable"],
        ),
    ]
    return lines


def _composition_table(doc: dict) -> list[str]:
    comp = doc["c1_ceiling"]["stream_composition"]
    lines = [
        "| Seed | Candidate edges | Reverse orientations | Extra orientations | Cell rows | Unique undirected | Cell C1 max | Candidate C1 max | Inflation |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in comp["per_seed"]:
        lines.append(
            "| `%d` | %d | %d | %d | %d | %d | %d | %d | %d |" % (
                row["seed"], row["candidate_edges"], row["reverse_orientations"],
                row["extra_orientations"], row["cell_rows"],
                row["unique_undirected"], row["cell_max_c1"],
                row["candidate_max_c1"], row["inflation"],
            )
        )
    lines += [
        "",
        "**Totals:** %d candidate rows, %d reverse orientations, %d extra "
        "orientations, %d cell rows, %d unique undirected edges. The unique-edge "
        "C1 ceiling is **%d-%d**, still below 60." % (
            comp["candidate_rows"], comp["reverse_orientations"],
            comp["extra_orientations"], comp["cell_rows"],
            comp["unique_undirected"], comp["unique_c1_min"],
            comp["unique_c1_max"],
        ),
    ]
    return lines


def _pool_table(doc: dict) -> list[str]:
    pool = doc["c2_c8_competence"]["target_pool"]
    lines = [
        "| Seed | Candidate edges | A available | K available | A&K available | C8 rows needed | Pool sufficient? |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in pool["per_seed"]:
        lines.append(
            "| `%d` | %d | %d | %d | %d | %d | %s |" % (
                row["seed"], row["candidate_edges"], row["A_available"],
                row["K_available"], row["A_and_K_available"],
                row["c8_rows_required"],
                "YES" if row["pool_sufficient"] else "NO",
            )
        )
    return lines


def _competence_table(doc: dict) -> list[str]:
    lines = [
        "| Seed | N4 fully C2-viable | N4 needs | N4 clean? | N20 fully C2-viable | N20 needs | N20 clean? |",
        "| ---: | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    n4 = {row["seed"]: row for row in doc["c2_c8_competence"]["designs"]["N4"]["per_seed"]}
    for row in doc["c2_c8_competence"]["designs"]["N20"]["per_seed"]:
        four = n4[row["seed"]]
        lines.append(
            "| `%d` | %d | %d | %s | %d | %d | %s |" % (
                row["seed"], four["fully_c2_viable"], four["c8_rows_required"],
                "YES" if four["clean_c8_block_possible"] else "NO",
                row["fully_c2_viable"], row["c8_rows_required"],
                "YES" if row["clean_c8_block_possible"] else "NO",
            )
        )
    return lines


def render(doc: dict) -> str:
    c1 = doc["c1_ceiling"]
    comp = doc["c2_c8_competence"]
    n4 = comp["designs"]["N4"]
    n20 = comp["designs"]["N20"]
    lines = [
        "# A1 design viability — C1 ceiling and conditional C2/C8 target competence",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** It is a read-only report over committed no-arm artifacts; no cell was run, no target was frozen, no grant was issued and no threshold was changed.",
        "",
        "## C1 ceiling — proof for the current stream",
        "",
        c1["proof"],
        "",
        "### Candidate-protocol stream",
        "",
    ]
    lines += _c1_table(doc, "candidate_stream")
    lines += [
        "",
        c1["candidate_stream"]["conclusion"],
        "",
        "### Current cell stream",
        "",
    ]
    lines += _c1_table(doc, "cell_stream")
    lines += [
        "",
        c1["cell_stream"]["conclusion"],
        "",
        "### Cell-stream composition and dedupe",
        "",
    ]
    lines += _composition_table(doc)
    lines += [
        "",
        c1["stream_composition"]["conclusion"],
        "",
        "### What the ceiling means",
        "",
        c1["conclusion"],
        "",
        c1["what_it_does_not_mean"],
        "",
        "## C2/C8 target competence — conditional",
        "",
        "**Status:** `%s`" % comp["status"],
        "",
        comp["assumption"],
        "",
        comp["induction_caveat"],
        "",
        comp["relationship"],
        "",
        "| Design | Target rows | Fully C2-viable | C8 rows required | Max clean rows per seed | Seeds with a clean block |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, block in (("N4", n4), ("N20", n20)):
        lines.append(
            "| **%s** | %d | %d | %d | %d | **%d/6** |" % (
                key, 24 if key == "N4" else 120, block["total_clean_rows"],
                block["c8_rows_required"], block["max_clean_rows"],
                block["seeds_clean_block_possible"],
            )
        )
    lines += ["", "### Per-seed competence", ""]
    lines += _competence_table(doc)
    lines += [
        "",
        "### Competent target pool",
        "",
    ]
    lines += _pool_table(doc)
    lines += [
        "",
        comp["target_pool"]["conclusion"],
        "",
        comp["conclusion"],
        "",
        "## Disposition",
        "",
        doc["disposition"],
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_design_viability --check",
        "python -m benchmarks.a1_design_viability --self-test",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def write() -> int:
    doc = build()
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = _load(OUT_PATH)
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    designs = doc["c2_c8_competence"]["designs"]
    pool = doc["c2_c8_competence"]["target_pool"]
    print(
        "A1 design viability: clean; candidate C1 ceilings %d-%d < %d; "
        "C2/C8 max clean rows N4 %d/4, N20 %d/20; competent pool %d-%d"
        % (doc["c1_ceiling"]["candidate_stream"]["min_attainable"],
           doc["c1_ceiling"]["candidate_stream"]["max_attainable"],
           C1_FLOOR, designs["N4"]["max_clean_rows"],
           designs["N20"]["max_clean_rows"],
           pool["min_A_and_K_available"], pool["max_A_and_K_available"])
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        found = self_test()
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("A1 design viability: self-test clean")
        return 0
    if args.write:
        return write()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
