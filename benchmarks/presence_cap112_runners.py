"""The cap-112 runners for the comparator, Q1 and Q2 -- built, gated, and runnable on 0.15.0.

`DECISION-CAP-LEVEL` chose option C (raise `SleepService.MAX_PREDICTIONS` to 112), the three
cap-112 records were granted on 2026-11-11, and the level landed the same day. Each record said
the runners were a separate step, because every installed harness declared cap 40. This module
is that step:

- **comparator** -- `PRESENCE-COMPARATOR-112`, six audit seeds, presence versus assertion as sets;
- **Q1** -- `PRESENCE-CONSTRUCT-1-112`, the same six seeds with gates C1-C9, C9 anchored to the
  comparator-112 row rather than the cap-40 audit row;
- **Q2** -- `PRESENCE-CAP-1-112`, a fresh block at levels 40 / 80 / 112 / uncapped, 24 cells and a
  witness at 112.

`preflight()` names every unmet prerequisite, and `--measure` raises `REFUSED` before a database
is opened. The runner refuses when the shipped cap is not 112, when the installed version is not
0.15.0, when the pin does not name that version, or when the block canaries were not re-recorded
on the installed bytes -- the four conditions the records' `engine.requires` states. On the
landed build the preflight is empty and the runners are runnable; no cell has run, and starting
one is a campaign run that nothing here does implicitly.

What can be checked without running a cell is the wiring: the gates, the verdict rules and their
controls run on hand-built rows, so a verdict that cannot be reached is a defect now rather than
a surprise after a campaign starts.

    ./.venv/bin/python -m benchmarks.presence_cap112_runners --check
    ./.venv/bin/python -m benchmarks.presence_cap112_runners --self-test
    ./.venv/bin/python -m benchmarks.presence_cap112_runners --dry-run
    ./.venv/bin/python -m benchmarks.presence_cap112_runners --measure --block comparator
    ./.venv/bin/python -m benchmarks.presence_cap112_runners --finish --block comparator
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from organica.sleep import SleepService

from benchmarks import engine_stamp
from benchmarks import presence_assertion_audit as comparator
from benchmarks import presence_cap_experiment as capexp
from benchmarks import presence_construct_audit as construct
from benchmarks.acquisition_compositional import generate_compositional_world

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PARTS = ROOT / ".scratch" / "presence_cap112" / "parts"
CAP = 112
TARGET_VERSION = "0.15.0"
RECORDS = {
    "comparator": "presence_comparator_112_prereg.json",
    "Q1": "presence_construct_1_112_prereg.json",
    "Q2": "presence_cap_1_112_prereg.json",
}
ARTIFACTS = {
    "comparator": DOCS / "presence_comparator_112_run.json",
    "Q1": DOCS / "presence_construct_1_112_run.json",
    "Q2": DOCS / "presence_cap_1_112_run.json",
}
PAGES = {
    "comparator": DOCS / "PRESENCE-COMPARATOR-112-RESULT.md",
    "Q1": DOCS / "PRESENCE-CONSTRUCT-1-112-RESULT.md",
    "Q2": DOCS / "PRESENCE-CAP-1-112-RESULT.md",
}
COMPARATOR_VERDICTS = ("PRESENCE NOT FULL", "PRESENCE NOT ASSERTION",
                       "PRESENCE AND ASSERTION COINCIDE")
Q1_VERDICTS = ("CONSTRUCT VALID", "OBJECT MISMATCH", "NOT MEASURABLE", "VOID")
Q1_GATE_VERDICT = {"C1_build": "VOID", "C2_world": "VOID", "C3_presence": "VOID",
                   "C4_denominator": "NOT MEASURABLE", "C5_object": "OBJECT MISMATCH",
                   "C6_witnesses": "VOID", "C7_seed_axis": "VOID", "C8_determinism": "VOID",
                   "C9_comparator_row": "VOID"}
Q1_VERDICT_ORDER = ("C1_build", "C2_world", "C3_presence", "C4_denominator", "C5_object",
                    "C6_witnesses", "C7_seed_axis", "C8_determinism", "C9_comparator_row")
Q2_VERDICTS = ("VOID", "CAP NOT BINDING", "ADMISSION-ONLY BOTTLENECK", "CAP LIMITING",
               "CAP LIMITING BELOW BAR", "CAP NOT LIMITING", "MIXED")
WITNESS_FIELDS = ("world_edges", "present_world_edges", "asserted_world_edges",
                  "asserted_fingerprint")


def record(block: str) -> dict:
    return json.loads((DOCS / RECORDS[block]).read_text(encoding="utf-8"))


def preflight() -> list[str]:
    """The four conditions the records' `engine.requires` names, checked in that order."""
    problems: list[str] = []
    shipped = int(SleepService.MAX_PREDICTIONS)
    if shipped != CAP:
        problems.append("the shipped Layer-1 cap is %d, not %d" % (shipped, CAP))
    version = engine_stamp.engine_version()
    if version != TARGET_VERSION:
        problems.append("the installed version is %s, not %s" % (version, TARGET_VERSION))
    pin = json.loads((DOCS / "engine_pin.json").read_text(encoding="utf-8"))
    if str(pin.get("version")) != TARGET_VERSION:
        problems.append("the engine pin names %s, not %s" % (pin.get("version"), TARGET_VERSION))
    canary = json.loads((DOCS / "block_canaries.json").read_text(encoding="utf-8"))
    if canary.get("engine_sha256") != engine_stamp.engine_sha256():
        problems.append("the block canaries were not re-recorded on the installed bytes")
    return problems


def refusal_message(problems: list[str]) -> str:
    """The refusal a cell would get, so the gate can be proved on an injected condition."""
    return "REFUSED: the cap-112 runners do not run on this build: %s" % "; ".join(problems)


def refuse() -> None:
    problems = preflight()
    if problems:
        raise SystemExit(refusal_message(problems))


def _world(seed: int, cycles: int) -> set[tuple[str, str]]:
    return construct._world_compositional_edges(
        generate_compositional_world(seed=seed, cycles=cycles))


def _comparator_row(cell: dict) -> dict:
    present, asserted = cell["present_world_edges"], cell["asserted_world_edges"]
    world = cell["world_edges"]
    return {
        "seed": cell["seed"], "world_edges": world, "world_digest": cell["world_digest"],
        "present_world_edges": present, "presence_rate": round(present / world, 6),
        "asserted_world_edges": asserted, "assertion_rate": round(asserted / world, 6),
        "conversion": round(asserted / present, 6) if present else None,
        "present_not_asserted": present - asserted,
        "present_fingerprint": cell["present_fingerprint"],
        "asserted_world_fingerprint": cell["asserted_world_fingerprint"],
        "asserted_fingerprint": cell["asserted_fingerprint"],
        "cap": cell.get("cap"), "engine_version": cell.get("engine_version"),
        "engine_sha256": cell.get("engine_sha256"), "engine_commit": cell.get("engine_commit"),
        "asserted_world_edges_list": ["%s>%s" % (edge["source"], edge["target"])
                                      for edge in cell["edges"] if edge["asserted"]],
    }


def comparator_failures(rows: list[dict], control: dict | None = None) -> dict:
    found: dict = {}
    if any(row["cap"] != CAP for row in rows) or len(
            {(row["engine_version"], row["engine_sha256"]) for row in rows}) != 1:
        found["A1_build"] = {"caps": sorted({row["cap"] for row in rows})}
    bad = [row["seed"] for row in rows
           if row["world_edges"] != 112
           or construct._digest(_world(row["seed"], 120)) != row["world_digest"]]
    if bad:
        found["A2_world"] = {"seeds": bad}
    empty = [row["seed"] for row in rows
             if not row["world_edges"] or not row["present_world_edges"]
             or not row["asserted_world_edges"]]
    if empty:
        found["A3_denominator"] = {"seeds": empty}
    not_a_set = [row["seed"] for row in rows
                 if len(row.get("asserted_world_edges_list") or []) != row["asserted_world_edges"]]
    if not_a_set:
        found["A4_object"] = {"seeds": not_a_set}
    if len({(row["present_fingerprint"], row["asserted_fingerprint"]) for row in rows}) < 2:
        found["A5_seed_axis"] = {"distinct": 1}
    if control is not None and any(control.get(field) != rows[0].get(field)
                                   for field in WITNESS_FIELDS):
        found["A6_control"] = {"differs": [field for field in WITNESS_FIELDS
                                          if control.get(field) != rows[0].get(field)]}
    return found


def comparator_verdict(rows: list[dict], control: dict | None = None) -> tuple[str, dict]:
    failures = comparator_failures(rows, control)
    for gate in ("A1_build", "A2_world", "A3_denominator", "A4_object", "A5_seed_axis",
                 "A6_control"):
        if gate in failures:
            return "VOID", {"gate": gate, **failures[gate]}
    return comparator._verdict(rows), {"seeds": len(rows)}


def _present(cell: dict) -> set[tuple[str, str]]:
    return {(edge["source"], edge["target"]) for edge in cell["edges"] if edge["present"]}


def _asserted(cell: dict) -> set[tuple[str, str]]:
    return {(edge["source"], edge["target"]) for edge in cell["edges"] if edge["asserted"]}


def construct_failures(rows: list[dict], control: dict | None,
                       comparator_rows: dict[int, dict]) -> dict:
    found: dict = {}
    bad = [cell["seed"] for cell in rows
           if cell.get("cap") != CAP or len({(c.get("engine_version"), c.get("engine_sha256"))
                                             for c in rows}) != 1]
    if bad:
        found["C1_build"] = {"seeds": bad}
    wrong = [cell["seed"] for cell in rows
             if cell["world_edges"] != 112
             or construct._digest(_world(cell["seed"], cell["cycles"])) != cell["world_digest"]]
    if wrong:
        found["C2_world"] = {"seeds": wrong}
    bad = [cell["seed"] for cell in rows
           if construct._digest(_present(cell)) != cell["present_fingerprint"]]
    if bad:
        found["C3_presence"] = {"seeds": bad}
    empty = [cell["seed"] for cell in rows
             if not cell["world_edges"] or not cell["present_world_edges"]
             or not cell["s_ever_world_edges"]]
    if empty:
        found["C4_denominator"] = {"seeds": empty}
    for cell in rows:
        absent = sorted(_asserted(cell) - _present(cell))
        if absent or not cell.get("a_w_subset_of_p"):
            found["C5_object"] = {"seed": cell["seed"],
                                  "edges": ["%s>%s" % edge for edge in absent[:5]]}
            break
    bad = [cell["seed"] for cell in rows
           if not _asserted(cell) or not (_present(cell) - _asserted(cell))]
    if bad:
        found["C6_witnesses"] = {"seeds": bad}
    if len({cell["pse_fingerprint"] for cell in rows}) < 2:
        found["C7_seed_axis"] = {"distinct": 1}
    if control is not None and any(control.get(field) != rows[0].get(field)
                                   for field in ("pse_fingerprint", "windows_world")):
        found["C8_determinism"] = {"differs": [field for field in ("pse_fingerprint", "windows_world")
                                              if control.get(field) != rows[0].get(field)]}
    for cell in rows:
        reference = comparator_rows.get(cell["seed"])
        if reference is None:
            found["C9_comparator_row"] = {"seed": cell["seed"], "reason": "no comparator row"}
            break
        differs = [field for field in WITNESS_FIELDS
                   if reference.get(field) != cell.get(field)]
        if differs:
            found["C9_comparator_row"] = {"seed": cell["seed"], "differs": differs}
            break
    return found


def construct_verdict(rows: list[dict], control: dict | None,
                      comparator_rows: dict[int, dict]) -> tuple[str, dict]:
    failures = construct_failures(rows, control, comparator_rows)
    for gate in Q1_VERDICT_ORDER:
        if gate in failures:
            return Q1_GATE_VERDICT[gate], {"gate": gate, **failures[gate]}
    return "CONSTRUCT VALID", {"seeds": len(rows)}


def q2_failures(design: dict, cells: list[dict], witness: dict | None,
                comparator_rows: dict[int, dict]) -> dict:
    found: dict = {}
    seeds, levels = list(design["seeds"]), list(design["levels"])
    index = {(cell["seed"], cell["cap"]): cell for cell in cells}
    if set(index) != {(seed, level) for seed in seeds for level in levels}:
        return {"K1_build": {"reason": "the cell set is not levels x seeds"}}
    if len({(cell["engine_sha256"], cell["engine_version"]) for cell in cells}) != 1 \
            or any(cell["cap_effective"] != cell["cap"] for cell in cells):
        found["K1_build"] = {"reason": "mixed build or cap not effective"}
    for seed in seeds:
        if len({index[(seed, level)]["world_digest"] for level in levels}) != 1:
            found["K2_same_world"] = {"seed": seed}
            break
        if len({index[(seed, level)]["present_fingerprint"] for level in levels}) != 1:
            found["K3_presence_invariant"] = {"seed": seed}
            break
    live, changed = 0, 0
    for seed in seeds:
        forty = index[(seed, 40)]
        if forty["max_window"] > 40:
            found["K4_cap_live"] = {"seed": seed, "max_window": forty["max_window"]}
            return found
        if forty["max_window"] == 40:
            live += 1
        if any(index[(seed, level)]["s_ever_fingerprint"] != forty["s_ever_fingerprint"]
               for level in levels if level > 40):
            changed += 1
    if live < 5 or changed < 1:
        found["K4_cap_live"] = {"full_windows": live, "s_ever_changed": changed}
    if capexp.treatment_overrides() != ["__init__"]:
        found["K5_cap_only"] = {"overrides": capexp.treatment_overrides()}
    if witness is None:
        found["K5_cap_only"] = {"reason": "no witness cell"}
    else:
        reference = comparator_rows.get(design["witness_cell"]["seed"])
        if reference is None:
            found["K5_cap_only"] = {"reason": "no comparator-112 row for the witness seed"}
        else:
            differs = [field for field in WITNESS_FIELDS
                       if reference.get(field) != witness.get(field)]
            if differs:
                found["K5_cap_only"] = {"reason": "the witness does not reproduce the comparator row",
                                        "differs": differs}
    if any(not (cell["world_edges"] and cell["present_world_edges"]
                and cell["s_ever_world_edges"]) for cell in cells):
        found["K6_denominator"] = {"reason": "an empty denominator"}
    return found


def q2_verdict(design: dict, cells: list[dict], witness: dict | None,
               comparator_rows: dict[int, dict], bar: int) -> tuple[str, dict]:
    failures = q2_failures(design, cells, witness, comparator_rows)
    for gate in ("K1_build", "K2_same_world", "K3_presence_invariant", "K4_cap_live",
                 "K5_cap_only", "K6_denominator"):
        if gate in failures:
            label = "CAP NOT BINDING" if gate == "K4_cap_live" else "VOID"
            return label, {"gate": gate, **failures[gate]}
    index = {(cell["seed"], cell["cap"]): cell for cell in cells}
    seeds, levels = list(design["seeds"]), list(design["levels"])

    def asserted(seed: int, level: int) -> int:
        return index[(seed, level)]["asserted_world_edges"]

    def ever(seed: int, level: int) -> int:
        return index[(seed, level)]["s_ever_world_edges"]

    steps = {seed: [asserted(seed, 80) - asserted(seed, 40),
                    asserted(seed, 112) - asserted(seed, 80),
                    asserted(seed, capexp.UNCAPPED) - asserted(seed, 112)] for seed in seeds}
    up = [seed for seed in seeds if capexp._same_direction(steps[seed])
          and any(step > 0 for step in steps[seed]) and steps[seed][0] >= 0]
    flat = [seed for seed in seeds if asserted(seed, 112) <= asserted(seed, 40)
            and asserted(seed, capexp.UNCAPPED) <= asserted(seed, 40)]
    reach = [seed for seed in seeds if ever(seed, 112) != ever(seed, 40)
             or ever(seed, capexp.UNCAPPED) != ever(seed, 40)]
    gains = [asserted(seed, 112) - asserted(seed, 40) for seed in seeds]
    mean_gain = round(statistics.mean(gains), 6)
    spread = statistics.stdev(gains) if len(gains) > 1 else 0.0
    lower = round(mean_gain - capexp.T_LOWER_95_DF5 * spread / math.sqrt(len(gains)), 6)
    details = {"gains_112": gains, "mean_gain": mean_gain, "lower_bound": lower, "bar": bar,
               "positive_seeds": sum(1 for gain in gains if gain > 0),
               "scaling_seeds": len(up), "flat_seeds": len(flat),
               "reach_changed_seeds": len(reach)}
    if len(flat) >= 5 and len(reach) >= 5:
        return "ADMISSION-ONLY BOTTLENECK", details
    if len(flat) >= 5:
        return "CAP NOT LIMITING", details
    if len(up) >= 5:
        if mean_gain >= bar and lower > 0 and details["positive_seeds"] >= 5:
            return "CAP LIMITING", details
        return "CAP LIMITING BELOW BAR", details
    return "MIXED", details


def part_path(block: str, seed: int, cap: int | None = None, suffix: str = "") -> Path:
    name = "%s-%d" % (block, seed) if cap is None else "%s-%d-%d" % (block, seed, cap)
    return PARTS / (name + suffix + ".json")


def run_one(block: str, seed: int, cap: int | None = None, cycles: int | None = None) -> dict:
    """One cell. The caller has already passed `refuse()`."""
    if block == "Q2":
        return capexp.run_cell(seed, int(cap), cycles or capexp.SHORT_CYCLES)
    cell = construct.run_cell(seed, cycles)
    if block == "comparator":
        row = _comparator_row(cell)
        row["kind"] = "presence_comparator_112_cell"
        return engine_stamp.stamp(row)
    cell["kind"] = "presence_construct_1_112_cell"
    return cell


def measure(block: str) -> int:
    refuse()
    PARTS.mkdir(parents=True, exist_ok=True)
    design = record(block)["design"]
    if block == "Q2":
        for seed in design["seeds"]:
            for cap in design["levels"]:
                path = part_path(block, seed, cap)
                if path.exists():
                    print("cached %s" % path.name, flush=True)
                    continue
                path.write_text(json.dumps(run_one(block, seed, cap), indent=1), encoding="utf-8")
        witness = design["witness_cell"]
        path = part_path(block, witness["seed"], witness["cap"], "-witness")
        if not path.exists():
            path.write_text(json.dumps(run_one(block, witness["seed"], witness["cap"]),
                                       indent=1), encoding="utf-8")
        return 0
    for seed in design["seeds"]:
        path = part_path(block, seed)
        if not path.exists():
            path.write_text(json.dumps(run_one(block, seed), indent=1), encoding="utf-8")
    control_seed = design.get("control_cell", {}).get("seed", design["seeds"][0])
    control = part_path(block, control_seed, suffix="-control")
    if not control.exists():
        control.write_text(json.dumps(run_one(block, control_seed), indent=1), encoding="utf-8")
    return 0


def _load(block: str, seed: int, cap: int | None = None, suffix: str = "") -> dict:
    path = part_path(block, seed, cap, suffix)
    if not path.exists():
        raise SystemExit("missing part %s; run --measure" % path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def comparator_rows() -> dict[int, dict]:
    """The finished comparator-112 rows, or the parts when the artifact is absent."""
    if ARTIFACTS["comparator"].exists():
        art = json.loads(ARTIFACTS["comparator"].read_text(encoding="utf-8"))
        return {row["seed"]: row for row in art.get("rows") or []}
    design = record("comparator")["design"]
    if all(part_path("comparator", seed).exists() for seed in design["seeds"]):
        return {seed: json.loads(part_path("comparator", seed).read_text(encoding="utf-8"))
                for seed in design["seeds"]}
    raise SystemExit("REFUSED: the comparator-112 rows do not exist yet; run and finish the "
                     "comparator before this block")


def finish(block: str) -> int:
    design = record(block)["design"]
    if block == "comparator":
        rows = [_load(block, seed) for seed in design["seeds"]]
        control = _load(block, design["seeds"][0], suffix="-control") \
            if part_path(block, design["seeds"][0], suffix="-control").exists() else None
        label, details = comparator_verdict(rows, control)
        art = {"kind": "presence_comparator_112_run", "prereg": "PRESENCE-COMPARATOR-112",
               "cap": CAP, "rows": rows, "verdict": label, "details": details,
               "checks": {gate: gate not in comparator_failures(rows, control)
                          for gate in ("A1_build", "A2_world", "A3_denominator", "A4_object",
                                       "A5_seed_axis", "A6_control")},
               "not_evidence": record(block)["not_evidence"]}
        page = _render_comparator(art)
    elif block == "Q1":
        rows = [_load(block, seed) for seed in design["seeds"]]
        control = _load(block, design["control_cell"]["seed"], suffix="-control")
        reference = comparator_rows()
        label, details = construct_verdict(rows, control, reference)
        art = {"kind": "presence_construct_1_112_run", "prereg": "PRESENCE-CONSTRUCT-1-112",
               "cap": CAP, "rows": rows, "control": control, "verdict": label,
               "details": details,
               "checks": {gate: gate not in construct_failures(rows, control, reference)
                          for gate in Q1_VERDICT_ORDER},
               "not_evidence": record(block)["not_evidence"]}
        page = _render_construct(art)
    else:
        cells = [_load(block, seed, cap) for seed in design["seeds"] for cap in design["levels"]]
        witness = _load(block, design["witness_cell"]["seed"], design["witness_cell"]["cap"],
                        "-witness")
        reference = comparator_rows()
        bar = int(json.loads((DOCS / "presence_cap_prereg.json").read_text(encoding="utf-8"))
                  ["bar"]["value"])
        label, details = q2_verdict(design, cells, witness, reference, bar)
        index = {(cell["seed"], cell["cap"]): cell for cell in cells}
        band = {
            "question": "do the 21-40 transitions enter service at 112?",
            "answer": "not identifiable from this block",
            "why": ("the 62 rank-21-40 edges are a Q4 artifact on Q4's six audit seeds; "
                    "Q2's fresh seeds have different worlds, and its cells record counts, "
                    "not per-edge ceiling ranks. The block shows more world edges entering "
                    "service, not that those named edges do."),
            "rows": [{"seed": seed,
                      "admitted_40": index[(seed, 40)]["admitted_world_edges"],
                      "admitted_112": index[(seed, 112)]["admitted_world_edges"],
                      "s_ever_40": index[(seed, 40)]["s_ever_world_edges"],
                      "s_ever_112": index[(seed, 112)]["s_ever_world_edges"],
                      "asserted_40": index[(seed, 40)]["asserted_world_edges"],
                      "asserted_112": index[(seed, 112)]["asserted_world_edges"]}
                     for seed in sorted({cell["seed"] for cell in cells})],
            "acceptance_adjudicated": False,
        }
        art = {"kind": "presence_cap_1_112_run", "prereg": "PRESENCE-CAP-1-112",
               "cap": CAP, "cells": cells, "witness": witness, "bar": bar,
               "band": band,
               "verdict": label, "details": details,
               "checks": {gate: gate not in q2_failures(design, cells, witness, reference)
                          for gate in ("K1_build", "K2_same_world", "K3_presence_invariant",
                                       "K4_cap_live", "K5_cap_only", "K6_denominator")},
               "not_evidence": record(block)["not_evidence"]}
        page = _render_q2(art)
    art = engine_stamp.stamp(art)
    ARTIFACTS[block].write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGES[block].write_text(page, encoding="utf-8")
    print("%s: %s" % (block, art["verdict"]))
    return 0


def _gate_table(art: dict) -> list[str]:
    lines = ["| Gate | Result |", "| --- | --- |"]
    for gate, passed in art["checks"].items():
        lines.append("| `%s` | %s |" % (gate, "PASS" if passed else "FAIL"))
    return lines


def _render_comparator(art: dict) -> str:
    lines = ["# PRESENCE-COMPARATOR-112 -- result", "",
             "**Verdict: `%s`** at the shipped cap **%d**." % (art["verdict"], art["cap"]), "",
             "| Seed | W | P | A_W | Conversion | Asserted fingerprint |",
             "| ---: | ---: | ---: | ---: | ---: | --- |"]
    for row in art["rows"]:
        lines.append("| %d | %d | %d | %d | %s | `%s` |" % (
            row["seed"], row["world_edges"], row["present_world_edges"],
            row["asserted_world_edges"], row["conversion"], row["asserted_fingerprint"]))
    return "\n".join(lines + ["", "## Gates", ""] + _gate_table(art) + [
        "", art["not_evidence"], ""])


def _render_construct(art: dict) -> str:
    lines = ["# PRESENCE-CONSTRUCT-1-112 -- result", "",
             "**Verdict: `%s`** at the shipped cap **%d**." % (art["verdict"], art["cap"]), "",
             "| Seed | W | P | S_ever | A_W | A_W subset of P |",
             "| ---: | ---: | ---: | ---: | ---: | --- |"]
    for row in art["rows"]:
        lines.append("| %d | %d | %d | %d | %d | %s |" % (
            row["seed"], row["world_edges"], row["present_world_edges"],
            row["s_ever_world_edges"], row["asserted_world_edges"], row["a_w_subset_of_p"]))
    return "\n".join(lines + ["", "## Gates", ""] + _gate_table(art) + [
        "", art["not_evidence"], ""])


def _render_q2(art: dict) -> str:
    lines = ["# PRESENCE-CAP-1-112 -- result", "",
             "**Verdict: `%s`** with **%d** shipped." % (art["verdict"], art["cap"]), "",
             "| Seed | A_W at 40 | A_W at 80 | A_W at 112 | A_W uncapped | Gain 40->112 |",
             "| ---: | ---: | ---: | ---: | ---: | ---: |"]
    index = {(cell["seed"], cell["cap"]): cell for cell in art["cells"]}
    for seed in sorted({cell["seed"] for cell in art["cells"]}):
        lines.append("| %d | %s |" % (seed, " | ".join(str(
            index[(seed, cap)]["asserted_world_edges"])
            for cap in (40, 80, 112, capexp.UNCAPPED)) + " | %d |" % (
                index[(seed, 112)]["asserted_world_edges"]
                - index[(seed, 40)]["asserted_world_edges"])))
    band = art["band"]
    lines += ["", "## The 21-40 band", "",
              "**Not identifiable from this block.** %s" % band["why"], "",
              "| Seed | Admitted 40 | Admitted 112 | S_ever 40 | S_ever 112 | A_W 40 | A_W 112 |",
              "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in band["rows"]:
        lines.append("| %d | %d | %d | %d | %d | %d | %d |" % (
            row["seed"], row["admitted_40"], row["admitted_112"],
            row["s_ever_40"], row["s_ever_112"], row["asserted_40"],
            row["asserted_112"]))
    lines += ["", "The block measures more world edges entering service, but not the "
              "named Q4 edges. The decision's acceptance condition therefore remains "
              "**unadjudicated**, and the decision stays **PENDING**."]
    return "\n".join(lines + ["", "## Gates", ""] + _gate_table(art) + [
        "", "Bar: **%d** asserted world edges." % art["bar"], "", art["not_evidence"], ""])


def _synthetic_comparator_rows() -> list[dict]:
    rows = []
    for index, seed in enumerate(record("comparator")["design"]["seeds"]):
        rows.append({"seed": seed, "world_edges": 112, "world_digest": construct._digest(
            _world(seed, 120)), "present_world_edges": 112 - index,
                     "presence_rate": round((112 - index) / 112, 6),
                     "asserted_world_edges": 60 - index,
                     "assertion_rate": round((60 - index) / 112, 6),
                     "conversion": round((60 - index) / (112 - index), 6),
                     "present_not_asserted": 52, "present_fingerprint": "p%d" % index,
                     "asserted_fingerprint": "a%d" % index, "cap": CAP,
                     "engine_version": TARGET_VERSION, "engine_sha256": "s",
                     "asserted_world_edges_list": ["x>y"] * (60 - index)})
    return rows


def self_test() -> list[str]:
    """The controls the records promise: a verdict that cannot be reached is a defect now."""
    found: list[str] = []
    rows = _synthetic_comparator_rows()
    labels = {comparator._verdict(rows)}
    quiet = [dict(row, present_world_edges=row["world_edges"],
                  presence_rate=1.0) for row in rows]
    labels |= {comparator._verdict(quiet)}
    coincide = [dict(row, present_world_edges=row["world_edges"],
                     asserted_world_edges=row["world_edges"]) for row in rows]
    labels |= {comparator._verdict(coincide)}
    if labels != set(COMPARATOR_VERDICTS):
        found.append("the comparator verdict rule cannot reach %s"
                     % sorted(set(COMPARATOR_VERDICTS) - labels))
    if "A1_build" not in comparator_failures([dict(rows[0], cap=40)]):
        found.append("a cap-40 comparator row is not rejected")
    if "A3_denominator" not in comparator_failures([dict(rows[0], present_world_edges=0)]):
        found.append("a zero denominator is not rejected")

    cell = {"seed": 20261100, "cap": CAP, "cycles": 120, "world_edges": 112,
            "world_digest": construct._digest(_world(20261100, 120)),
            "present_world_edges": 112, "present_fingerprint": "",
            "s_ever_world_edges": 90, "asserted_world_edges": 50,
            "asserted_fingerprint": "af", "pse_fingerprint": "pf", "windows_world": [[], []],
            "a_w_subset_of_p": True,
            "edges": [{"source": "a", "target": "b", "present": True, "asserted": True},
                      {"source": "a", "target": "c", "present": True, "asserted": False}]}
    cell["present_fingerprint"] = construct._digest(_present(cell))
    second = dict(cell, seed=20261101, present_fingerprint="", pse_fingerprint="pf2",
                  asserted_fingerprint="af2",
                  world_digest=construct._digest(_world(20261101, 120)),
                  edges=[{"source": "a", "target": "b", "present": True, "asserted": True},
                         {"source": "a", "target": "d", "present": True, "asserted": False}])
    second["present_fingerprint"] = construct._digest(_present(second))
    reference = {20261100: {"world_edges": 112, "present_world_edges": 112,
                            "asserted_world_edges": 50, "asserted_fingerprint": "af"},
                 20261101: {"world_edges": 112, "present_world_edges": 112,
                            "asserted_world_edges": 50, "asserted_fingerprint": "af2"}}
    control = dict(cell)
    if construct_verdict([cell, second], control, reference)[0] != "CONSTRUCT VALID":
        found.append("a valid synthetic Q1 cell is not CONSTRUCT VALID")
    broken = dict(cell, edges=cell["edges"] + [{"source": "z", "target": "z",
                                               "present": False, "asserted": True}],
                  a_w_subset_of_p=False)
    if construct_verdict([broken, second], control, reference)[0] != "OBJECT MISMATCH":
        found.append("Q1 does not reject an asserted edge that is not present")

    design = record("Q2")["design"]
    cells = []
    for index, seed in enumerate(design["seeds"]):
        for cap in design["levels"]:
            asserted = {40: 40, 80: 48, 112: 56, capexp.UNCAPPED: 60}[cap]
            cells.append({"seed": seed, "cap": cap, "cap_effective": cap,
                          "engine_version": TARGET_VERSION, "engine_sha256": "s",
                          "world_edges": 112, "world_digest": "w%d" % index,
                          "present_world_edges": 112, "present_fingerprint": "p%d" % index,
                          "s_ever_world_edges": 60 if cap > 40 else 45,
                          "s_ever_fingerprint": "e%d-%d" % (index, 1 if cap > 40 else 0),
                          "asserted_world_edges": asserted, "asserted_fingerprint": "a",
                          "max_window": 40 if cap == 40 else min(cap, 112)})
    witness = {"world_edges": 112, "present_world_edges": 112, "asserted_world_edges": 56,
               "asserted_fingerprint": "a"}
    ref = {design["witness_cell"]["seed"]: dict(witness)}
    if q2_verdict(design, cells, witness, ref, 10)[0] != "CAP LIMITING":
        found.append("Q2 cannot reach CAP LIMITING on a compliant synthetic block")
    over = [dict(cell) for cell in cells]
    for cell in over:
        if cell["cap"] == 40:
            cell["max_window"] = 41
    if q2_verdict(design, over, witness, ref, 10)[0] != "CAP NOT BINDING":
        found.append("Q2 does not reject a 40 arm that returns 41 rows")
    return found


def check() -> int:
    found: list[str] = []
    for block in RECORDS:
        body = record(block)
        if body.get("cap") != CAP:
            found.append("%s: the record is not at cap 112" % block)
        runner = body.get("runner") or {}
        if runner.get("status") != "built":
            found.append("%s: the record does not disclose a built runner" % block)
        if not (ROOT / (runner.get("module") or "")).exists():
            found.append("%s: the runner module named by the record does not exist" % block)
        if not body.get("amendments"):
            found.append("%s: the runner build is not disclosed as an amendment" % block)
    found.extend(self_test())
    problems = preflight()
    # The level has landed, so the preflight is satisfied here. The gate is proved on an injected
    # condition rather than by the build: the same builder `refuse` uses must name it.
    proof = refusal_message(problems or ["a synthetic unmet condition"])
    if not proof.startswith("REFUSED: ") or "cap-112 runners" not in proof:
        found.append("the refusal path does not name the condition it enforces")
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    print("cap-112 runners: 3 blocks built, %d prereg condition(s) unmet, refusal proved"
          % len(problems))
    return 0


def dry_run(block: str | None = None) -> int:
    """Print every planned cell and its part path; open no database and write nothing.

    The plan is derived from the frozen designs, not from a run: a cell that is already cached
    is marked, so a resumed measure can be read before it spends anything. The preflight is
    reported, not enforced -- a dry run is exactly how a blocked build is inspected.
    """
    blocks = [block] if block else sorted(RECORDS)
    unmet = preflight()
    print("preflight: %s" % ("; ".join(unmet) if unmet else "satisfied"))
    print("mode: dry run -- no cell opened, no database touched, nothing written")
    total = 0
    for name in blocks:
        body = record(name)
        design = body["design"]
        print("%s: %s (%s)" % (name, body["prereg"], RECORDS[name]))
        if name == "Q2":
            for seed in design["seeds"]:
                for cap in design["levels"]:
                    path = part_path(name, seed, cap)
                    print("  cell seed=%d cap=%d part=%s%s" % (
                        seed, cap, path.relative_to(ROOT),
                        " (cached)" if path.exists() else ""))
                    total += 1
            witness = design["witness_cell"]
            path = part_path(name, witness["seed"], witness["cap"], "-witness")
            print("  witness seed=%d cap=%d part=%s%s" % (
                witness["seed"], witness["cap"], path.relative_to(ROOT),
                " (cached)" if path.exists() else ""))
            total += 1
        else:
            for seed in design["seeds"]:
                path = part_path(name, seed)
                print("  cell seed=%d part=%s%s" % (
                    seed, path.relative_to(ROOT), " (cached)" if path.exists() else ""))
                total += 1
            control = design.get("control_cell", {}).get("seed", design["seeds"][0])
            path = part_path(name, control, suffix="-control")
            print("  control seed=%d part=%s%s" % (
                control, path.relative_to(ROOT), " (cached)" if path.exists() else ""))
            total += 1
    print("planned cells: %d" % total)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="print every planned cell and part path; open no database")
    parser.add_argument("--measure", action="store_true")
    parser.add_argument("--finish", action="store_true")
    parser.add_argument("--block", choices=sorted(RECORDS))
    parser.add_argument("--cell", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--cap", type=int)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.dry_run:
        return dry_run(args.block)
    if args.cell:
        refuse()
        if args.block is None or args.seed is None:
            raise SystemExit("--cell needs --block and --seed")
        cell = run_one(args.block, args.seed, args.cap)
        target = args.out or part_path(args.block, args.seed, args.cap if args.block == "Q2" else None)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(cell, indent=1), encoding="utf-8")
        return 0
    if args.self_test:
        found = self_test()
        for problem in found:
            print("FAIL:", problem)
        if not found:
            print("controls: every declared verdict reachable, every rejection fires")
        return 1 if found else 0
    if args.measure or args.finish:
        if args.block is None:
            raise SystemExit("--measure and --finish need --block")
        return measure(args.block) if args.measure else finish(args.block)
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
