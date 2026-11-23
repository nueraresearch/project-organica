"""G9 stage-ledger validator: six classes, six invariants, synthetic fixtures.

The ledger is edge-level. Every row names one directed world edge and the first
cycle at which each stage was observed. Missing stages are null, never zero.
The class is derived from admitted/served/asserted presence; carrier timing is
recorded but does not change the class.

This module validates a ledger. It does not create a real ledger, run an engine,
assign a seed or authorise a G9 design.

    python -m benchmarks.g9_stage_ledger --write
    python -m benchmarks.g9_stage_ledger --check
    python -m benchmarks.g9_stage_ledger --self-test
    python -m benchmarks.g9_stage_ledger --check-ledger my_ledger.json
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FIXTURE_PATH = DOCS / "g9_stage_ledger_fixtures.json"
PAGE_PATH = DOCS / "G9-STAGE-LEDGER-VALIDATOR.md"

DATE = "2026-11-14"
CYCLES = 10
UNIVERSE = ("a>b", "b>c", "c>d", "d>e", "e>f", "f>g")
SEEDS = (1,)
STAGES = ("formed", "admitted", "served", "asserted", "carrier")
CLASSES = ("A", "B", "C", "D", "E", "F")
CLASS_READING = {
    "A": "admitted, served, asserted",
    "B": "admitted, never served, asserted",
    "C": "not admitted, not served, asserted",
    "D": "formed only",
    "E": "admitted but latent",
    "F": "served but not asserted",
}


def _row(edge: str, admitted: int | None, served: int | None,
         asserted: int | None, carrier: int | None, klass: str) -> dict:
    formed = 1
    values = {
        "formed": formed,
        "admitted": admitted,
        "served": served,
        "asserted": asserted,
        "carrier": carrier,
    }
    return {
        "seed": SEEDS[0],
        "edge": edge,
        "formed_cycle": formed,
        "admitted_cycle": admitted,
        "served_cycle": served,
        "asserted_cycle": asserted,
        "carrier_cycle": carrier,
        "class": klass,
        "sources": {stage: "observed" for stage, value in values.items()
                    if value is not None},
    }


def fixture_ledger() -> dict:
    """One valid ledger with exactly one row in each of the six classes."""
    rows = [
        _row("a>b", 2, 3, 4, 2, "A"),
        _row("b>c", 2, None, 4, None, "B"),
        _row("c>d", None, None, 4, 2, "C"),
        _row("d>e", None, None, None, None, "D"),
        _row("e>f", 2, None, None, 2, "E"),
        _row("f>g", 2, 3, None, 3, "F"),
    ]
    return {
        "kind": "g9_stage_ledger",
        "fixture": True,
        "date": DATE,
        "cycles": CYCLES,
        "universe": list(UNIVERSE),
        "seeds": list(SEEDS),
        "rows": rows,
        "expected_class_counts": {klass: 1 for klass in CLASSES},
        "not_evidence": (
            "Synthetic fixtures for validator self-testing. No engine, seed, cell "
            "or real stage ledger is used, and this is not a G9 result."
        ),
    }


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def classify(row: dict) -> str | None:
    """Derive the six-class label, or None when the stage combination is invalid."""
    if row.get("formed_cycle") is None:
        return None
    admitted = row.get("admitted_cycle") is not None
    served = row.get("served_cycle") is not None
    asserted = row.get("asserted_cycle") is not None
    if served and not admitted:
        return None
    if admitted and served and asserted:
        return "A"
    if admitted and not served and asserted:
        return "B"
    if not admitted and not served and asserted:
        return "C"
    if not admitted and not served and not asserted:
        return "D"
    if admitted and not served and not asserted:
        return "E"
    if admitted and served and not asserted:
        return "F"
    return None


def _cycle_problem(name: str, value: object, cycles: int) -> str | None:
    if value is None:
        return None
    if not _is_int(value):
        return "%s is not an integer: %r" % (name, value)
    if not 1 <= int(value) <= cycles:
        return "%s is outside 1..%d: %r" % (name, cycles, value)
    return None


def validate_ledger(doc: dict) -> list[str]:
    """Every invariant, including coverage of the fixed universe per seed."""
    problems: list[str] = []
    if not isinstance(doc, dict):
        return ["the ledger is not an object"]
    if doc.get("kind") != "g9_stage_ledger":
        problems.append("ledger kind is not g9_stage_ledger")
    cycles = doc.get("cycles")
    if not _is_int(cycles) or int(cycles) < 1:
        problems.append("cycles is not a positive integer")
        cycles = 0
    else:
        cycles = int(cycles)
    universe = doc.get("universe")
    if not isinstance(universe, list) or not universe:
        problems.append("universe is not a non-empty list")
        universe = []
    if any(not isinstance(edge, str) or not edge for edge in universe):
        problems.append("universe contains a non-string or empty edge")
    if len(set(universe)) != len(universe):
        problems.append("universe contains duplicate edges")
    universe_set = set(universe)
    seeds = doc.get("seeds")
    if not isinstance(seeds, list) or not seeds:
        problems.append("seeds is not a non-empty list")
        seeds = []
    if any(not _is_int(seed) for seed in seeds):
        problems.append("seeds contains a non-integer")
    if len(set(seeds)) != len(seeds):
        problems.append("seeds contains duplicates")
    seed_set = set(seeds)
    rows = doc.get("rows")
    if not isinstance(rows, list) or not rows:
        return problems + ["rows is not a non-empty list"]

    seen: set[tuple[int, str]] = set()
    per_seed: dict[int, set[str]] = {seed: set() for seed in seeds if _is_int(seed)}
    for index, row in enumerate(rows):
        where = "row %d" % index
        if not isinstance(row, dict):
            problems.append("%s is not an object" % where)
            continue
        seed = row.get("seed")
        edge = row.get("edge")
        if not _is_int(seed):
            problems.append("%s seed is not an integer" % where)
        elif seed not in seed_set:
            problems.append("%s seed %r is not in seeds" % (where, seed))
        if not isinstance(edge, str) or not edge:
            problems.append("%s edge is not a non-empty string" % where)
        elif edge not in universe_set:
            problems.append("%s edge %r is not in the fixed universe" % (where, edge))
        if _is_int(seed) and isinstance(edge, str) and edge:
            key = (int(seed), edge)
            if key in seen:
                problems.append("duplicate row for (%d, %s)" % key)
            seen.add(key)
            per_seed.setdefault(int(seed), set()).add(edge)

        for stage in STAGES:
            field = "%s_cycle" % stage
            problem = _cycle_problem("%s %s" % (where, field), row.get(field), cycles)
            if problem:
                problems.append(problem)
        formed = row.get("formed_cycle")
        if formed is None:
            problems.append("%s formed_cycle is missing" % where)
        admitted = row.get("admitted_cycle")
        served = row.get("served_cycle")
        asserted = row.get("asserted_cycle")
        if served is not None and admitted is None:
            problems.append("%s served_cycle without admitted_cycle" % where)
        if _is_int(served) and _is_int(admitted) and int(served) < int(admitted):
            problems.append("%s served_cycle < admitted_cycle" % where)
        if _is_int(asserted) and _is_int(formed) and int(asserted) < int(formed):
            problems.append("%s asserted_cycle < formed_cycle" % where)

        sources = row.get("sources")
        if not isinstance(sources, dict):
            problems.append("%s sources is not an object" % where)
            sources = {}
        for stage in STAGES:
            present = row.get("%s_cycle" % stage) is not None
            source = sources.get(stage)
            if present and source != "observed":
                problems.append("%s %s_cycle is present but not observed" % (where, stage))
            if not present and source is not None:
                problems.append("%s %s_cycle is null but has a source" % (where, stage))

        computed = classify(row)
        declared = row.get("class")
        if computed is None:
            problems.append("%s has no valid class" % where)
        elif declared != computed:
            problems.append("%s declares class %r but is %s" % (where, declared, computed))
        if declared is not None and declared not in CLASSES:
            problems.append("%s declares unknown class %r" % (where, declared))

    for seed in seeds:
        if not _is_int(seed):
            continue
        missing = universe_set - per_seed.get(int(seed), set())
        extra = per_seed.get(int(seed), set()) - universe_set
        if missing:
            problems.append("seed %d is missing edges: %s"
                            % (int(seed), ", ".join(sorted(missing))))
        if extra:
            problems.append("seed %d has edges outside the universe: %s"
                            % (int(seed), ", ".join(sorted(extra))))
    return problems


def summarize(doc: dict) -> dict:
    """Class counts overall and per seed. Call only after validation."""
    counts = {klass: 0 for klass in CLASSES}
    per_seed: dict[str, dict[str, int]] = {str(seed): {klass: 0 for klass in CLASSES}
                                           for seed in doc["seeds"]}
    for row in doc["rows"]:
        klass = classify(row)
        if klass is None:
            continue
        counts[klass] += 1
        per_seed[str(row["seed"])][klass] += 1
    return {"rows": len(doc["rows"]), "classes": counts, "per_seed": per_seed}


def render(doc: dict) -> str:
    counts = summarize(doc)
    lines = [
        "# G9 stage-ledger validator",
        "",
        "**Date:** %s  " % doc["date"],
        "**Status:** `CONTRACT BUILT — SYNTHETIC FIXTURES ONLY; NO REAL LEDGER, NO SEED, NO G9 DESIGN`",
        "",
        "This page documents the validator and its six-row synthetic fixture. It is not a stage map",
        "and not evidence for activation, self-modeling, transfer or external advantage.",
        "",
        "## Ledger schema",
        "",
        "| Field | Meaning |",
        "| --- | --- |",
        "| `seed` | Fixed seed |",
        "| `edge` | Directed world edge |",
        "| `formed_cycle` | First cycle a candidate structure exists |",
        "| `admitted_cycle` | First cycle the edge is eligible for service, before the cap |",
        "| `served_cycle` | First cycle the edge enters a served window |",
        "| `asserted_cycle` | First cycle the edge appears in the final structure |",
        "| `carrier_cycle` | First cycle a carrier exists; does not change the class |",
        "| `class` | One of A-F, computed from admitted/served/asserted presence |",
        "| `sources` | Per-stage provenance; every present stage must be `observed` |",
        "",
        "A missing stage is `null`, never `0`. A missing cycle is not measurable at that stage,",
        "not an early transition. The validator does not infer a missing stage from a later stock.",
        "",
        "## Invariants",
        "",
        "1. `(seed, edge)` is unique; every edge in the fixed universe has one row for every seed.",
        "2. Every present cycle is an integer in `1..cycles`; missing is `null`; zero is invalid.",
        "3. `formed_cycle` is present for every row.",
        "4. `served_cycle` implies `admitted_cycle`; a served edge cannot be unadmitted.",
        "5. `served_cycle >= admitted_cycle` and `asserted_cycle >= formed_cycle`; carrier timing is free.",
        "6. Every present stage has source `observed`; an absent stage has no source. A final assertion",
        "   cannot fill in a missing service cycle.",
        "",
        "The declared `class` must equal the class derived from stage presence. The validator never",
        "trusts a class label on its own.",
        "",
        "## Six classes",
        "",
        "| Class | Admitted | Served | Asserted | Reading | Fixture edge |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in doc["rows"]:
        lines.append("| **%s** | %s | %s | %s | %s | `%s` |" % (
            row["class"],
            "yes" if row["admitted_cycle"] is not None else "no",
            "yes" if row["served_cycle"] is not None else "no",
            "yes" if row["asserted_cycle"] is not None else "no",
            CLASS_READING[row["class"]], row["edge"]))
    lines += [
        "",
        "## Synthetic fixture",
        "",
        "The committed fixture has one row in every class on one seed and the fixed universe:",
        "",
        "| Class | Count |",
        "| --- | ---: |",
    ]
    for klass in CLASSES:
        lines.append("| **%s** | %d |" % (klass, counts["classes"][klass]))
    lines += [
        "",
        "The fixture is `docs/g9_stage_ledger_fixtures.json`. It validates only as a fixture; it is",
        "not a measured ledger and spends no seed.",
        "",
        "## Commands",
        "",
        "```bash",
        "python -m benchmarks.g9_stage_ledger --write",
        "python -m benchmarks.g9_stage_ledger --check",
        "python -m benchmarks.g9_stage_ledger --self-test",
        "python -m benchmarks.g9_stage_ledger --check-ledger my_ledger.json",
        "```",
        "",
        "## CI",
        "",
        "CI runs `--check` and `--self-test` next to the A1 readiness step. `--check` validates",
        "the committed fixture, page freshness and six-class coverage; `--self-test` independently",
        "exercises every class and every invariant.",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def _expect(doc: dict, needle: str) -> bool:
    return any(needle in problem for problem in validate_ledger(doc))


def self_test() -> list[str]:
    found: list[str] = []
    base = fixture_ledger()
    problems = validate_ledger(base)
    if problems:
        found.append("fixture is invalid: %s" % "; ".join(problems))
    for row in base["rows"]:
        if classify(row) != row["class"]:
            found.append("fixture row %s does not classify as %s"
                         % (row["edge"], row["class"]))
    summary = summarize(base)
    if summary["classes"] != {klass: 1 for klass in CLASSES}:
        found.append("fixture does not contain all six classes once")
    if summary["rows"] != 6:
        found.append("fixture does not have six rows")

    duplicate = copy.deepcopy(base)
    duplicate["rows"].append(copy.deepcopy(duplicate["rows"][0]))
    if not _expect(duplicate, "duplicate row"):
        found.append("a duplicate (seed, edge) is accepted")

    missing = copy.deepcopy(base)
    missing["rows"] = [row for row in missing["rows"] if row["edge"] != "d>e"]
    if not _expect(missing, "missing edges"):
        found.append("an incomplete universe is accepted")

    extra = copy.deepcopy(base)
    extra_row = copy.deepcopy(extra["rows"][0])
    extra_row["edge"] = "z>z"
    extra["rows"].append(extra_row)
    if not _expect(extra, "outside the universe"):
        found.append("an edge outside the fixed universe is accepted")

    no_formed = copy.deepcopy(base)
    no_formed["rows"][0]["formed_cycle"] = None
    if not _expect(no_formed, "formed_cycle is missing"):
        found.append("a missing formed_cycle is accepted")

    zero = copy.deepcopy(base)
    zero["rows"][0]["served_cycle"] = 0
    if not _expect(zero, "outside 1..%d" % CYCLES):
        found.append("a zero cycle is accepted as an early transition")

    not_integer = copy.deepcopy(base)
    not_integer["rows"][0]["served_cycle"] = "3"
    if not _expect(not_integer, "not an integer"):
        found.append("a non-integer cycle is accepted")

    no_admission = copy.deepcopy(base)
    no_admission["rows"][5]["admitted_cycle"] = None
    if not _expect(no_admission, "served_cycle without admitted_cycle"):
        found.append("a served edge without admission is accepted")

    wrong_order = copy.deepcopy(base)
    wrong_order["rows"][0]["admitted_cycle"] = 5
    wrong_order["rows"][0]["served_cycle"] = 3
    wrong_order["rows"][0]["sources"]["admitted"] = "observed"
    wrong_order["rows"][0]["sources"]["served"] = "observed"
    if not _expect(wrong_order, "served_cycle < admitted_cycle"):
        found.append("service before admission is accepted")

    bad_assertion = copy.deepcopy(base)
    bad_assertion["rows"][0]["formed_cycle"] = 5
    bad_assertion["rows"][0]["asserted_cycle"] = 4
    if not _expect(bad_assertion, "asserted_cycle < formed_cycle"):
        found.append("assertion before formation is accepted")

    wrong_source = copy.deepcopy(base)
    wrong_source["rows"][0]["sources"]["served"] = "asserted"
    if not _expect(wrong_source, "served_cycle is present but not observed"):
        found.append("a stage filled from another stage is accepted")

    missing_source = copy.deepcopy(base)
    missing_source["rows"][0]["sources"].pop("served")
    if not _expect(missing_source, "served_cycle is present but not observed"):
        found.append("a present stage with no source is accepted")

    absent_source = copy.deepcopy(base)
    absent_source["rows"][3]["sources"]["served"] = "asserted"
    if not _expect(absent_source, "served_cycle is null but has a source"):
        found.append("an absent stage with a source is accepted")

    wrong_class = copy.deepcopy(base)
    wrong_class["rows"][0]["class"] = "B"
    if not _expect(wrong_class, "declares class 'B' but is A"):
        found.append("a mislabelled class is accepted")
    return found


def check() -> int:
    if not FIXTURE_PATH.exists():
        print("FAIL: fixture is missing: %s" % FIXTURE_PATH)
        return 1
    if not PAGE_PATH.exists():
        print("FAIL: validator page is missing: %s" % PAGE_PATH)
        return 1
    doc = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if doc != fixture_ledger():
        print("FAIL: %s is stale" % FIXTURE_PATH)
        return 1
    problems = validate_ledger(doc)
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        return 1
    summary = summarize(doc)
    if summary["classes"] != {klass: 1 for klass in CLASSES}:
        print("FAIL: fixture does not cover all six classes once")
        return 1
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        print("FAIL: %s is stale" % PAGE_PATH)
        return 1
    found = self_test()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("G9 stage-ledger validator: fixture clean; six classes, six invariants")
    return 0


def check_ledger(path: Path) -> int:
    if not path.exists():
        print("FAIL: ledger is missing: %s" % path)
        return 1
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print("FAIL: ledger is not valid JSON: %s" % exc)
        return 1
    problems = validate_ledger(doc)
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        return 1
    result = summarize(doc)
    print("G9 stage-ledger: clean; %d rows; classes %s"
          % (result["rows"], result["classes"]))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--check-ledger", metavar="PATH", type=Path)
    args = parser.parse_args(argv)
    if args.write:
        doc = fixture_ledger()
        FIXTURE_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        PAGE_PATH.write_text(render(doc), encoding="utf-8")
        print("wrote %s and %s" % (FIXTURE_PATH, PAGE_PATH))
        return 0
    if args.check_ledger is not None:
        return check_ledger(args.check_ledger)
    if args.self_test:
        found = self_test()
        for problem in found:
            print("FAIL:", problem)
        if not found:
            print("G9 stage-ledger: every class and every invariant is exercised")
        return 1 if found else 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
