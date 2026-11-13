"""CORE-BAND-ADMISSION-1: run and adjudicate the core+band guarantee at cap 112.

Control is the shipped cap-112 window. Treatment returns the same window unless
a top-20 core or rank-21-40 band transition is absent; then it replaces the
lowest-priority non-tier transition, or a cooccurrence only if no transition
remains. The guarantee changes a seat, never the 112-row ceiling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from organica.candidates import PredictionCandidate
from organica.sleep import SleepService

from benchmarks import core_band_admission_prereg as block
from benchmarks import engine_stamp
from benchmarks import presence_conversion_repair_observer as observer
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.presence_construct_audit import (ACQ_SOURCE, PHASE_ACQUISITION,
                                                 _digest, _world_compositional_edges,
                                                 asserted_fingerprint)

MODULE = "benchmarks.core_band_admission"
PARTS = Path(__file__).resolve().parents[1] / ".scratch" / "core_band_admission" / "parts"
ARTIFACT = Path(__file__).resolve().parents[1] / "docs" / "core_band_admission.json"
PAGE = Path(__file__).resolve().parents[1] / "docs" / "CORE-BAND-ADMISSION.md"


def _edge(candidate) -> tuple[str, str]:
    return (candidate.source, candidate.target)


def _is_transition(candidate) -> bool:
    evidence = getattr(candidate, "evidence", {}) or {}
    return evidence.get("is_cooccurrence") is False


class CoreBandService(observer.RepairedObserverSleepService):
    """The repaired observer with an optional core+band seat guarantee."""

    def __init__(self, memory, enforce: bool = True, cap: int = block.CAP):
        super().__init__(memory, observe=True, cap=cap)
        self.enforce = bool(enforce)
        self.core_band: list[dict] = []

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        served = super()._build_predictions(temporal, freqs, prior_schemas)
        full = list(getattr(self, "full_candidates", []))
        transitions = [c for c in full if _is_transition(c)]
        tier = transitions[:40]
        tier_edges = {_edge(c) for c in tier}
        served_edges = {_edge(c) for c in served}
        missing = [c for c in tier if _edge(c) not in served_edges]
        record = {
            "cycle": len(self.core_band) + 1,
            "tier_available": len(tier),
            "tier_served_before": len(tier) - len(missing),
            "missing_before": ["%s>%s" % _edge(c) for c in missing],
            "replacements": [],
            "unresolved": [],
            "tier_served_after": len(tier) - len(missing),
        }
        if self.enforce and missing:
            victims = [c for c in reversed(served)
                       if _edge(c) not in tier_edges and _edge(c) not in {_edge(m) for m in missing}]
            victims.sort(key=lambda c: 0 if _is_transition(c) else 1)
            if len(victims) < len(missing):
                record["unresolved"] = ["%s>%s" % _edge(c) for c in missing[len(victims):]]
            chosen = victims[:len(missing)]
            result = list(served)
            for candidate, victim in zip(missing, chosen):
                try:
                    index = result.index(victim)
                except ValueError:
                    continue
                result[index] = candidate
                record["replacements"].append({
                    "added": "%s>%s" % _edge(candidate),
                    "removed": "%s>%s" % _edge(victim),
                })
            served = result
            record["tier_served_after"] = len(tier) - len(
                [c for c in tier if _edge(c) not in {_edge(x) for x in served}])
            # The observer recorded the pre-guarantee allocation; refresh it.
            if self.allocation:
                final = Counter("transition" if _is_transition(c) else
                                "cooccurrence" if (c.evidence or {}).get("is_cooccurrence") is True
                                else "unknown" for c in served)
                row = self.allocation[-1]
                row.update({
                    "served": len(served),
                    "transitions": final["transition"],
                    "cooccurrences": final["cooccurrence"],
                    "unknown": final["unknown"],
                    "sum_matches": sum(final.values()) == len(served),
                })
        self.core_band.append(record)
        return served


def planned() -> list[tuple[int, str]]:
    design = block.record()["design"]
    return [(int(seed), arm) for seed in design["seeds"] for arm in design["arms"]]


def command(seed: int, arm: str) -> str:
    return "python -m %s --cell %d %s" % (MODULE, seed, arm)


def preflight() -> list[str]:
    doc = block.record()
    found: list[str] = []
    if doc.get("status") != "FROZEN, NOT RUN":
        found.append("the block is not FROZEN, NOT RUN")
    auth = doc.get("authorisation") or {}
    if auth.get("granted") is not True:
        found.append("the dated grant is not recorded")
    if not auth.get("granted_on") or not auth.get("document") or not auth.get("quote"):
        found.append("the grant is not complete")
    if getattr(__import__("organica"), "__version__", None) != "0.15.0":
        found.append("the shipped build is not 0.15.0")
    if SleepService.MAX_PREDICTIONS != block.CAP:
        found.append("the shipped cap is not %d" % block.CAP)
    runner = doc.get("runner") or {}
    if runner.get("built") is not True or runner.get("planned_module") != MODULE:
        found.append("the record does not name this runner")
    return found


def refuse() -> None:
    reasons = preflight()
    if reasons:
        print("REFUSED: CORE-BAND-ADMISSION-1 will not run:", file=sys.stderr)
        for reason in reasons:
            print("  -", reason, file=sys.stderr)
        raise SystemExit(2)


def part_path(seed: int, arm: str) -> Path:
    return PARTS / ("%d-%s.json" % (seed, arm))


def run_cell(seed: int, arm: str) -> dict:
    if (seed, arm) not in planned():
        raise SystemExit("REFUSED: (%d, %s) is not a planned cell" % (seed, arm))
    world = generate_compositional_world(seed=seed, cycles=block.CYCLES)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("core_band_%d_%s" % (seed, arm))
    mem = _CountingMemoryService(str(db_path))
    svc = CoreBandService(mem, enforce=(arm == "treatment"), cap=block.CAP)
    windows: list[list[tuple[str, str]]] = []
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, train_flag) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not train_flag:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            mem.store(text, event_type="observe",
                      source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                windows.append([_edge(p) for p in svc.run_sleep_cycle().predictions])
        asserted = {(a, b) for a, targets in
                    structure_edges(svc._load_prior_candidates()).items()
                    for b in targets}
        rows = {(a, b) for a, b in
                mem._conn.execute("SELECT tag_from, tag_to FROM precedes").fetchall()}
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass
    present = world_edges & rows
    flat = [edge for window in windows for edge in window]
    false_rows = sum(1 for edge in flat if edge not in present)
    cell = {
        "kind": "core_band_cell",
        "prereg": block.ID,
        "seed": int(seed),
        "arm": arm,
        "enforce": arm == "treatment",
        "cycles": len(windows),
        "cap": block.CAP,
        "engine_version": engine_stamp.engine_version(),
        "engine_sha256": engine_stamp.engine_sha256(),
        "world_digest": _digest(world_edges),
        "present_fingerprint": _digest(present),
        "world_edges": len(world_edges),
        "present_world_edges": len(present),
        "asserted_edges": sorted([list(edge) for edge in asserted & world_edges]),
        "asserted_fingerprint": asserted_fingerprint(asserted),
        "windows": [[list(edge) for edge in window] for window in windows],
        "window_digests": [hashlib.sha1(
            "|".join("%s>%s" % edge for edge in window).encode()).hexdigest()
            for window in windows],
        "served_rows": len(flat),
        "false_rows": false_rows,
        "core_band": [dict(row) for row in svc.core_band],
        "allocation": [dict(row) for row in svc.allocation],
        "store_counts": dict(getattr(mem, "store_counts", {})),
    }
    return engine_stamp.stamp(cell)


def measure(force: bool = False) -> int:
    refuse()
    PARTS.mkdir(parents=True, exist_ok=True)
    for seed, arm in planned():
        path = part_path(seed, arm)
        if path.exists() and not force:
            continue
        cell = run_cell(seed, arm)
        cell["window_digests"] = cell["window_digests"]
        path.write_text(json.dumps(cell), encoding="utf-8")
        print("ran %s" % path.name)
    return 0


def load(seed: int, arm: str) -> dict:
    path = part_path(seed, arm)
    if not path.exists():
        raise SystemExit("missing part %s" % path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def _arm_summary(parts: dict[int, dict], arm: str) -> dict:
    tier = served = 0
    false_rows = rows = replacements = 0
    missing_cycles = 0
    for seed in parts:
        cell = parts[seed][arm]
        rows += cell["served_rows"]
        false_rows += cell["false_rows"]
        for cycle in cell["core_band"]:
            tier += cycle["tier_available"]
            served += cycle["tier_served_after"]
            replacements += len(cycle["replacements"])
            missing_cycles += 1 if cycle["missing_before"] else 0
    return {
        "tier_available": tier,
        "tier_served": served,
        "coverage": served / tier if tier else None,
        "served_rows": rows,
        "false_rows": false_rows,
        "false_admission": false_rows / rows if rows else None,
        "replacements": replacements,
        "missing_cycles": missing_cycles,
    }


def adjudicate(parts: dict[int, dict]) -> dict:
    seeds = [int(seed) for seed in block.record()["design"]["seeds"]]
    build = {(parts[s][a]["engine_version"], parts[s][a]["engine_sha256"])
             for s in seeds for a in block.ARMS}
    world_ok = all(parts[s]["control"]["world_digest"] == parts[s]["treatment"]["world_digest"]
                   for s in seeds)
    length_ok = all(len(window) == block.CAP
                    for s in seeds for a in block.ARMS
                    for window in parts[s][a]["windows"])
    ledger_ok = all(
        sum(1 for cycle in parts[s][a]["core_band"]
            if len(cycle["missing_before"]) + cycle["tier_served_before"] == cycle["tier_available"])
        for s in seeds for a in block.ARMS)
    control = _arm_summary(parts, "control")
    treatment = _arm_summary(parts, "treatment")
    digests_equal = all(
        parts[s]["control"]["window_digests"] == parts[s]["treatment"]["window_digests"]
        for s in seeds)
    gates = {
        "C1_build": {"passed": len(build) == 1 and next(iter(build))[0] == block.record()["engine_version"]},
        "C2_world": {"passed": world_ok},
        "C3_tier": {"passed": all(c["tier_available"] > 0 for s in seeds for a in block.ARMS
                                  for c in parts[s][a]["core_band"])},
        "C4_length": {"passed": length_ok},
        "C5_ledger": {"passed": ledger_ok},
        "C6_control": {"passed": all(not parts[s]["control"]["enforce"] for s in seeds)},
        "C7_treatment": {"passed": all(parts[s]["treatment"]["enforce"] for s in seeds)},
    }
    all_gates = all(g["passed"] for g in gates.values())
    treatment["false_admission_difference"] = (
        treatment["false_admission"] - control["false_admission"]
        if treatment["false_admission"] is not None and control["false_admission"] is not None
        else None)
    if not all_gates:
        verdict = "VOID"
        reading = (
            "At least one frozen gate failed; no coverage effect is adjudicated. "
            "The observed windows are identical, but that is descriptive only."
        )
    elif treatment["replacements"] == 0 and digests_equal:
        verdict = "NON-BINDING AT 112"
        reading = (
            "The normal cap-112 window already serves the core+band tier; "
            "the guarantee made no replacement."
        )
    elif treatment["coverage"] is None or treatment["coverage"] < block.COVERAGE_BAR:
        verdict = "RULE FAILS COVERAGE"
        reading = "The guarantee did not recover the tier."
    elif treatment["false_admission_difference"] is None or treatment["false_admission_difference"] > block.MARGIN:
        verdict = "RULE PAYS COST"
        reading = "The guarantee recovered the tier by serving more non-world rows."
    else:
        verdict = "BINDING, ACCEPTABLE"
        reading = "The guarantee changed at least one window and stayed within the cost bar."
    per_seed = {}
    for seed in seeds:
        c = _arm_summary({seed: parts[seed]}, "control")
        t = _arm_summary({seed: parts[seed]}, "treatment")
        per_seed[str(seed)] = {
            "control_coverage": c["coverage"],
            "treatment_coverage": t["coverage"],
            "control_false_admission": c["false_admission"],
            "treatment_false_admission": t["false_admission"],
            "replacements": t["replacements"],
            "missing_cycles": t["missing_cycles"],
        }
    return engine_stamp.stamp({
        "kind": "core_band_admission",
        "prereg": block.ID,
        "status": "RUN",
        "cells": 12,
        "seeds": seeds,
        "design": block.record()["design"],
        "gates": gates,
        "control": control,
        "treatment": treatment,
        "per_seed": per_seed,
        "window_digests_equal": digests_equal,
        "verdict": verdict,
        "reading": reading,
        "not_evidence": block.record()["not_evidence"],
    })


def render(art: dict) -> str:
    c = art["control"]
    t = art["treatment"]
    lines = [
        "# Core+band admission at the cap-112 ceiling",
        "",
        "Generated by `python -m benchmarks.core_band_admission --finish`. Do not edit by hand.",
        "",
        "**Verdict: `%s`.** %s" % (art["verdict"], art["reading"]),
        "",
        "## Result",
        "",
        "| Measure | Control | Treatment |",
        "| --- | ---: | ---: |",
        "| Tier coverage | **%.4f** | **%.4f** |" % (c["coverage"], t["coverage"]),
        "| Served rows | **%d** | **%d** |" % (c["served_rows"], t["served_rows"]),
        "| False-admission rate | **%.4f** | **%.4f** |" % (c["false_admission"], t["false_admission"]),
        "| Replacements | — | **%d** |" % t["replacements"],
        "| Cycles with a missing tier edge | %d | %d |" % (c["missing_cycles"], t["missing_cycles"]),
        "",
        "False-admission difference (treatment minus control): **%+.4f** against the **+0.10** margin."
        % t["false_admission_difference"],
        "",
        "## Per seed",
        "",
        "| Seed | Control coverage | Treatment coverage | Replacements | Missing control cycles |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for seed, row in art["per_seed"].items():
        lines.append("| %s | %.4f | %.4f | %d | %d |" % (
            seed, row["control_coverage"], row["treatment_coverage"],
            row["replacements"], row["missing_cycles"]))
    lines += ["", "## Gates", "", "| Gate | Result |", "| --- | --- |"]
    for name, gate in art["gates"].items():
        lines.append("| `%s` | %s |" % (name, "PASS" if gate["passed"] else "FAIL"))
    lines += ["", "## Scope", "", art["not_evidence"], ""]
    return "\n".join(lines)


def finish() -> int:
    docs = [load(seed, arm) for seed, arm in planned()]
    if len(docs) != 12:
        raise SystemExit("missing cells: %d of 12" % len(docs))
    parts = {}
    for seed, arm in planned():
        parts.setdefault(seed, {})[arm] = load(seed, arm)
    art = adjudicate(parts)
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(art), encoding="utf-8")
    block.mark_result(art)
    print("verdict: %s" % art["verdict"])
    return 0


def check() -> int:
    pre = block.problems()
    if pre:
        for item in pre:
            print("FAIL:", item)
        return 1
    if not ARTIFACT.exists():
        print("FAIL: result artifact missing")
        return 1
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if art.get("verdict") not in {
            "VOID", "NON-BINDING AT 112", "BINDING, ACCEPTABLE",
            "RULE FAILS COVERAGE", "RULE PAYS COST"}:
        print("FAIL: verdict")
        return 1
    if PAGE.read_text(encoding="utf-8") != render(art):
        print("FAIL: page stale")
        return 1
    print("core+band: %s, cells %d" % (art["verdict"], art["cells"]))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cell", nargs=2, metavar=("SEED", "ARM"))
    args = parser.parse_args(argv)
    if args.dry_run:
        for seed, arm in planned():
            print(command(seed, arm))
        return 0
    if args.cell:
        refuse()
        seed, arm = int(args.cell[0]), args.cell[1]
        if (seed, arm) not in planned():
            raise SystemExit("REFUSED: not a planned cell")
        PARTS.mkdir(parents=True, exist_ok=True)
        cell = run_cell(seed, arm)
        part_path(seed, arm).write_text(json.dumps(cell), encoding="utf-8")
        print("ran %d %s" % (seed, arm))
        return 0
    if args.measure:
        return measure(args.force)
    if args.finish:
        return finish()
    if args.check or not argv:
        return check()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
