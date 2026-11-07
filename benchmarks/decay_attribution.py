"""Attribute the degree-12 collapse: which mechanism removes the stable edges, and when.

The theory-budget ceiling ends at zero coverage at every budget tested, so the next
question is not how much the engine can cover but what removes what it has. This
harness re-runs the ceiling's own world and setting with a per-cycle ledger and one
causal control: the same build with the temporal graph's per-cycle decay disabled. If
that decay is the killer, the control keeps its edges; if it is not, both arms fall
together and the loss is attributed elsewhere.

The protocol is docs/DECAY-ATTRIBUTION-PREREGISTRATION.md, written before the run; its
SHA-256 is recorded in the artifact so a later edit cannot pass as the committed one.
The engine is unchanged: the control is an in-process ablation of one class constant.

    ./.venv/bin/python -m benchmarks.decay_attribution --measure
    ./.venv/bin/python -m benchmarks.decay_attribution --reuse
    ./.venv/bin/python -m benchmarks.decay_attribution --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from datetime import date
from pathlib import Path

from benchmarks.decay_confirmation import (
    Counted,
    _feed,
    harvest_seeds,
    temp_db,
    world_edges,
)
from benchmarks.decay_fix_confirm import lattice_world
from organica.memory import MemoryService

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "decay_attribution" / "parts"
ARTIFACT = ROOT / "docs" / "decay_attribution.json"
DOC = ROOT / "docs" / "DECAY-ATTRIBUTION.md"
PREREG = ROOT / "docs" / "DECAY-ATTRIBUTION-PREREGISTRATION.md"

DEGREE = 12
CYCLES = 300
SEED_BASE = 20300601
SEED_COUNT = 3
ARMS = ("engine", "no_temporal_decay")
#: A control that ends this many cycles later than the engine did not collapse with it.
DELAY_MARGIN = 10
#: The ceiling artifact's own peak, re-checked here so the run is the one being explained.
CEILING_PEAK = 35
CEILING_COVERAGE = 0.5833


def protocol_digest() -> str | None:
    """SHA-256 of the committed protocol (sections 1-7), not of the outcome section.

    Section 8 is the post-run record and is written after the measurement; hashing it
    would make writing the result look like editing the protocol.
    """
    if not PREREG.exists():
        return None
    text = PREREG.read_text(encoding="utf-8")
    cut = text.find("\n## 8.")
    return hashlib.sha256((text[:cut] if cut >= 0 else text).encode("utf-8")).hexdigest()


class LedgerMemory(MemoryService):
    """Memory that records the decay call the engine makes, so it can be audited."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decay_calls: list[dict] = []

    def decay_temporal_edges(self, factor: float = 0.95, min_count: int = 1) -> int:
        rows = super().decay_temporal_edges(factor=factor, min_count=min_count)
        self.decay_calls.append({"factor": float(factor), "rows": int(rows)})
        return rows


class Ledger(Counted):
    """The shipped build plus the per-cycle quantities the attribution reads."""

    def __init__(self, memory, decay_factor: float):
        self.TEMPORAL_DECAY_FACTOR = float(decay_factor)
        super().__init__(memory)
        self.emitted: dict[tuple[str, str], float] = {}
        self.selection = (0, 0, 0)

    def begin_cycle(self) -> None:
        self.emitted = {}
        self.selection = (0, 0, 0)

    def _build_predictions(self, *args, **kwargs):
        out = super()._build_predictions(*args, **kwargs)
        for cand in out:
            key = (cand.source, cand.target)
            self.emitted[key] = max(self.emitted.get(key, 0.0), float(cand.strength))
        return out

    def _natural_selection(self, *args, **kwargs):
        out = super()._natural_selection(*args, **kwargs)
        self.selection = tuple(int(x) for x in out)
        return out


def attribution_seeds() -> list[int]:
    """The pre-registered block, verified free except for this harness's own record."""
    seeds = list(range(SEED_BASE, SEED_BASE + SEED_COUNT))
    if ARTIFACT.exists():
        try:
            recorded = json.loads(ARTIFACT.read_text(encoding="utf-8")).get("seeds") or []
        except (ValueError, OSError):
            recorded = []
        if recorded == seeds:
            return seeds
    overlap = sorted(set(seeds) & harvest_seeds(ROOT / "docs"))
    if overlap:
        raise SystemExit("the attribution block overlaps seeds already used under docs/: %s" % overlap)
    return seeds


def stored(service) -> dict[tuple[str, str], float]:
    """The stored prediction candidates, at their strongest live copy, with strengths."""
    service._prior_cache = None
    edges: dict[tuple[str, str], float] = {}
    for cand in service._load_prior_candidates():
        if cand.get("type") != "prediction_candidate":
            continue
        src, tgt = cand.get("source"), cand.get("target")
        if not src or not tgt:
            continue
        strength = float(cand.get("confidence") or cand.get("strength") or 0.0)
        edges[(src, tgt)] = max(edges.get((src, tgt), 0.0), strength)
    service._prior_cache = None
    return edges


def _graph(memory) -> tuple[dict[tuple[str, str], int], dict[str, int]]:
    temporal = {(src, tgt): int(count) for src, tgt, count in memory.temporal_edges(min_count=1)}
    freqs = dict(memory.tag_frequencies())
    return temporal, freqs


def _reason(
    edge: tuple[str, str],
    prior_strength: float,
    emitted: dict[tuple[str, str], float],
    threshold: float,
    death_threshold: float,
) -> str:
    """Why the engine no longer stores this edge as stable.

    Uses the engine's own three quantities: whether the edge was re-emitted, the
    strength it was stored with, and the candidate decay factor that applies when it
    was not. A stable edge that was re-emitted above the threshold and still vanished
    is not a mechanism; it is a ledger that disagrees with the engine.
    """
    if edge in emitted:
        return "below_threshold" if emitted[edge] < threshold else "unexplained"
    decayed = prior_strength * 0.8
    if decayed < death_threshold:
        return "pruned"
    if decayed < threshold:
        return "decayed"
    return "unexplained"


def cell(arm: str, seed: int, cycles: int = CYCLES) -> dict:
    events = lattice_world(DEGREE)
    world = world_edges(events)
    factor = 0.95 if arm == "engine" else 1.0
    db = temp_db("attrib_%s_%s.db" % (arm, seed))
    db.unlink(missing_ok=True)
    memory = LedgerMemory(db_path=str(db))
    service = Ledger(memory, factor)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    for text in events[:12]:
        memory.store(text, event_type="event", source="seed:bootstrap")

    series: list[dict] = []
    history: list[dict] = []
    previous: dict[tuple[str, str], float] = {}
    try:
        for cycle in range(cycles):
            _feed(memory, events, cycle)
            service.begin_cycle()
            memory.decay_calls = []
            service.run_sleep_cycle()
            now = stored(service)
            stable = {edge: value for edge, value in now.items()
                      if value >= service.STABLE_THRESHOLD}
            hits = [edge for edge in stable if edge in world]
            temporal, freqs = _graph(memory)
            counts = list(temporal.values())
            ratios = sorted(
                temporal.get(edge, 0) / max(freqs.get(edge[0], 1), 1) for edge in stable
            )
            deaths: dict[str, int] = {}
            edge_reasons: dict[tuple[str, str], str] = {}
            # The decay decision made during *this* cycle reads this cycle's predictions,
            # so the reason must be judged against `service.emitted`, never the previous
            # cycle's set: a re-emitted edge would otherwise be called absent and the
            # ledger would disagree with the engine on a death it actually explained.
            for edge, prior_strength in previous.items():
                if edge in stable:
                    continue
                reason = _reason(edge, prior_strength, service.emitted,
                                 service.STABLE_THRESHOLD, service.DEATH_THRESHOLD)
                deaths[reason] = deaths.get(reason, 0) + 1
                edge_reasons[edge] = reason
            strengthened, decayed, pruned = service.selection
            call = memory.decay_calls[-1] if memory.decay_calls else {"factor": None, "rows": 0}
            series.append({
                "cycle": cycle + 1,
                "stable": len(stable),
                "hits": len(hits),
                "coverage": round(len(hits) / len(world), 4) if world else None,
                "precision": round(len(hits) / len(stable), 4) if stable else None,
                "theories": int(getattr(service, "theories", 0)),
                "beliefs": int(getattr(service, "beliefs", 0)),
                "strengthened": strengthened,
                "decayed": decayed,
                "pruned": pruned,
                "emitted": len(service.emitted),
                "temporal_sum": sum(counts),
                "temporal_ge_min": sum(1 for c in counts if c >= service.PREDICTION_MIN_COUNT),
                "temporal_max": max(counts) if counts else 0,
                "hub_frequency": int(freqs.get("alpha", 0)),
                "median_ratio": round(statistics.median(ratios), 4) if ratios else None,
                "deaths": sum(deaths.values()),
                "by_reason": deaths,
                "decay_factor": call.get("factor"),
                "decay_rows": call.get("rows"),
            })
            history.append({"cycle": cycle + 1, "stable": set(stable),
                            "reasons": edge_reasons})
            previous = stable
    finally:
        memory.close()
        db.unlink(missing_ok=True)

    peak = max((len(row["stable"]) for row in history), default=0)
    peak_index = next((i for i, row in enumerate(history)
                       if len(row["stable"]) == peak), None)
    peak_edges = history[peak_index]["stable"] if peak_index is not None else set()
    peak_deaths: dict[str, int] = {}
    peak_death_cycles: list[int] = []
    for edge in sorted(peak_edges):
        for row in history[(peak_index or 0) + 1:]:
            if edge not in row["stable"]:
                reason = row["reasons"].get(edge, "unexplained")
                peak_deaths[reason] = peak_deaths.get(reason, 0) + 1
                peak_death_cycles.append(row["cycle"])
                break
    final_stable = history[-1]["stable"] if history else set()

    return {
        "arm": arm,
        "seed": seed,
        "degree": DEGREE,
        "cycles": cycles,
        "world_edges": len(world),
        "decay_factor_set": factor,
        "series": series,
        # The specific edges the peak was made of, followed to their own deaths -- not
        # every stable->unstable transition, which also counts churn that returns.
        "peak_edges": len(peak_edges),
        "peak_edge_deaths": peak_deaths,
        "peak_edge_death_cycles": sorted(peak_death_cycles),
        "peak_edges_alive_final": len(peak_edges & final_stable),
        "cycles_stable_exceeds_emitted": sum(
            1 for row in series if row["stable"] > row["emitted"]
        ),
    }


def _path(arm: str, seed: int) -> Path:
    return PARTS / ("cell_%s_s%d.json" % (arm, seed))


def run(seeds: list[int]) -> int:
    PARTS.mkdir(parents=True, exist_ok=True)
    for arm in ARMS:
        for seed in seeds:
            path = _path(arm, seed)
            if path.exists():
                print("cached", path.name)
                continue
            row = cell(arm, seed)
            path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            peak = max((s["stable"] for s in row["series"]), default=0)
            final = row["series"][-1]["stable"] if row["series"] else None
            print("%-17s s%d  peak=%2d final=%2d" % (arm, seed, peak, final), flush=True)
    return 0


def load_parts() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(PARTS.glob("cell_*.json"))]


def summarise(part: dict) -> dict:
    """Per-cell quantities, derived from the series and nothing else."""
    series = part["series"]
    if not series:
        return {"arm": part["arm"], "seed": part["seed"], "peak": 0, "measurable": False}
    peak = max(row["stable"] for row in series)
    peak_indices = [i for i, row in enumerate(series) if row["stable"] == peak]
    peak_index = peak_indices[0]
    peak_cycle = series[peak_index]["cycle"]
    peak_coverage = max((row["coverage"] for row in series if row["coverage"] is not None),
                        default=None)
    first_fall = next(
        (row["cycle"] for row in series[peak_index + 1:] if row["stable"] < peak), None
    )
    zero = next((row["cycle"] for i, row in enumerate(series)
                 if i > peak_index and row["stable"] == 0), None)
    # The terminal zero: the cycle after the last one with a live theory, and only if
    # the layer ends empty. The first zero is cycle 1 on every cell, so it cannot be the
    # comparison the ordering claim is judged on (rule 25: a gate that cannot fire is
    # decoration).
    last_theory = max((row["cycle"] for row in series if row["theories"] > 0), default=None)
    theory_zero = (
        last_theory + 1 if last_theory is not None and series[-1]["theories"] == 0 else None
    )
    half = next(
        (row["cycle"] for i, row in enumerate(series)
         if i > peak_index and peak and row["stable"] <= peak / 2.0), None
    )
    by_reason: dict[str, int] = {}
    for row in series:
        for reason, count in row.get("by_reason", {}).items():
            by_reason[reason] = by_reason.get(reason, 0) + int(count)
    at_peak = series[peak_index]
    ratio_at_peak = at_peak.get("median_ratio")
    death_ratios = [
        row.get("median_ratio") for row in series
        if row["cycle"] > peak_cycle and row.get("median_ratio") is not None
    ]
    increases = sum(
        1 for a, b in zip(series[peak_index:-1], series[peak_index + 1:])
        if b["stable"] > a["stable"]
    )
    return {
        "arm": part["arm"],
        "seed": part["seed"],
        "measurable": True,
        "peak": peak,
        "peak_cycle": peak_cycle,
        "peak_coverage": peak_coverage,
        "first_fall": first_fall,
        "zero_cycle": zero,
        "theory_zero_cycle": theory_zero,
        "half_life_cycles": (half - peak_cycle) if half is not None else None,
        "final_stable": series[-1]["stable"],
        "final_coverage": series[-1]["coverage"],
        "death_counts": by_reason,
        "deaths_total": sum(by_reason.values()),
        "increases_after_peak": increases,
        "median_ratio_at_peak": ratio_at_peak,
        "median_ratio_after_peak": round(statistics.median(death_ratios), 4) if death_ratios else None,
        "hub_frequency_at_peak": at_peak.get("hub_frequency"),
        "hub_frequency_final": series[-1].get("hub_frequency"),
        "temporal_sum_at_peak": at_peak.get("temporal_sum"),
        "temporal_sum_final": series[-1].get("temporal_sum"),
        "decay_factors": sorted({row.get("decay_factor") for row in series}),
        "peak_edges": part.get("peak_edges"),
        "peak_edge_deaths": part.get("peak_edge_deaths") or {},
        "peak_edge_death_cycles": part.get("peak_edge_death_cycles") or [],
        "peak_edges_alive_final": part.get("peak_edges_alive_final"),
        "cycles_stable_exceeds_emitted": part.get("cycles_stable_exceeds_emitted"),
    }


def _median(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def _range(values):
    values = [v for v in values if v is not None]
    return [min(values), max(values)] if values else None


def analyse(parts: list[dict]) -> dict:
    cells = [summarise(part) for part in parts]
    cells = [c for c in cells if c.get("measurable")]
    by_arm: dict[str, list[dict]] = {}
    for c in cells:
        by_arm.setdefault(c["arm"], []).append(c)

    failures: list[str] = []
    controls: dict[str, dict] = {}

    engine = by_arm.get("engine", [])
    control = by_arm.get("no_temporal_decay", [])
    if len(engine) < SEED_COUNT:
        failures.append("engine arm has %d of %d cells" % (len(engine), SEED_COUNT))
    if len(control) < SEED_COUNT:
        failures.append("control arm has %d of %d cells" % (len(control), SEED_COUNT))

    for group in ("engine", "no_temporal_decay"):
        for c in by_arm.get(group, []):
            if c["death_counts"].get("unexplained"):
                failures.append(
                    "%s seed %d has %d unexplained deaths: the ledger does not reproduce "
                    "the engine's own decision" % (group, c["seed"],
                                                   c["death_counts"]["unexplained"])
                )
            if c["decay_factors"] and c["decay_factors"] != ([0.95] if group == "engine" else [1.0]):
                failures.append(
                    "%s seed %d recorded decay factors %s, not the arm's own"
                    % (group, c["seed"], c["decay_factors"])
                )

    engine_peak_ok = bool(engine) and all(c["peak"] == CEILING_PEAK for c in engine)
    engine_coverage_ok = bool(engine) and all(
        c["peak_coverage"] is not None and abs(c["peak_coverage"] - CEILING_COVERAGE) < 5e-4
        for c in engine
    )
    controls["ceiling_reproduced"] = {
        "ok": engine_peak_ok and engine_coverage_ok,
        "peaks": [c["peak"] for c in engine],
        "peak_coverages": [c["peak_coverage"] for c in engine],
        "required": "peak stable %d and peak coverage %s in every engine cell"
                    % (CEILING_PEAK, CEILING_COVERAGE),
    }
    perturbation = bool(engine) and all(c["decay_factors"] == [0.95] for c in engine) \
        and bool(control) and all(c["decay_factors"] == [1.0] for c in control) \
        and all(c["temporal_sum_final"] != c["temporal_sum_at_peak"] for c in engine)
    controls["decay_perturbation_applied"] = {
        "ok": perturbation,
        "engine_factors": sorted({f for c in engine for f in c["decay_factors"]}),
        "control_factors": sorted({f for c in control for f in c["decay_factors"]}),
        "required": "engine calls decay with 0.95, control with 1.0, and the engine's graph "
                    "sum moves across the run",
    }

    engine_collapses = bool(engine) and all(c["final_stable"] == 0 for c in engine)
    control_collapses = bool(control) and all(c["final_stable"] == 0 for c in control)
    first_falls_engine = [c["first_fall"] for c in engine if c["first_fall"] is not None]
    first_falls_control = [c["first_fall"] for c in control if c["first_fall"] is not None]
    control_survives = [c for c in control if c["final_stable"] >= 1]
    delay = (
        _median([c["first_fall"] for c in control]) - _median([c["first_fall"] for c in engine])
        if first_falls_engine and first_falls_control else None
    )

    if not engine_collapses and engine:
        verdict = "NO_COLLAPSE"
    elif not engine_peak_ok or not engine_coverage_ok:
        verdict = "CEILING_NOT_REPRODUCED"
    elif control_survives and not control_collapses:
        verdict = "TEMPORAL_EDGE_DECAY"
    elif control_collapses and delay is not None and delay >= DELAY_MARGIN:
        verdict = "TEMPORAL_EDGE_DECAY_PARTIAL"
    elif control_collapses:
        verdict = "NOT_TEMPORAL_DECAY"
    else:
        verdict = "TEMPORAL_EDGE_DECAY_PARTIAL"

    total_deaths = sum(c["deaths_total"] for c in engine)
    shares = {}
    for c in engine:
        for reason, count in c["death_counts"].items():
            shares[reason] = shares.get(reason, 0) + count
    shares = {reason: (round(count / total_deaths, 4) if total_deaths else None)
              for reason, count in sorted(shares.items())}

    # The peak's own edges, followed to their deaths. This is the quantity the question
    # asks about; the churn count above also includes edges that die and return.
    peak_deaths: dict[str, int] = {}
    for c in engine:
        for reason, count in (c.get("peak_edge_deaths") or {}).items():
            peak_deaths[reason] = peak_deaths.get(reason, 0) + int(count)
    peak_total = sum(peak_deaths.values())
    peak_shares = {reason: (round(count / peak_total, 4) if peak_total else None)
                   for reason, count in sorted(peak_deaths.items())}

    predictions = {
        "P1_peak_is_35_at_0.5833": {
            "held": engine_peak_ok and engine_coverage_ok,
            "observed": [[c["peak"], c["peak_coverage"]] for c in engine],
        },
        "P2_final_is_zero": {
            "held": bool(engine) and all(c["final_stable"] == 0 for c in engine),
            "observed": [c["final_stable"] for c in engine],
        },
        "P3_edges_fall_after_theories_die": {
            "held": bool(engine) and all(
                c["theory_zero_cycle"] is not None and c["first_fall"] is not None
                and c["first_fall"] >= c["theory_zero_cycle"] for c in engine
            ),
            "observed": [[c["theory_zero_cycle"], c["first_fall"]] for c in engine],
            "note": "paired as (cycle after the last live theory, first cycle the edges "
                    "fall); the first zero is cycle 1 and is not the comparison",
        },
        "P4_control_survives_minus_ten_cycles": {
            "held": len(control_survives) >= 2 and all(
                c["first_fall"] is None or c["first_fall"] >= (c_engine or 0) + DELAY_MARGIN
                for c in control_survives
                for c_engine in [_median([e["first_fall"] for e in engine
                                          if e["first_fall"] is not None])]
            ),
            "observed": {
                "control_final": [c["final_stable"] for c in control],
                "delay_median_cycles": delay,
            },
        },
        "P5_strength_rule_outweighs_pruning": {
            "held": bool(total_deaths) and shares.get("below_threshold", 0) >= 0.5,
            "observed": shares,
        },
    }

    findings = []
    for group, label in (("engine", "engine"), ("no_temporal_decay", "no temporal decay")):
        rows = by_arm.get(group, [])
        if not rows:
            continue
        findings.append(
            "%s: peak %s at cycle %s, first fall %s, half-life %s cycles, zero at %s, "
            "final %s, deaths %s"
            % (
                label,
                _median([c["peak"] for c in rows]),
                _range([c["peak_cycle"] for c in rows]),
                _range([c["first_fall"] for c in rows]),
                _range([c["half_life_cycles"] for c in rows]),
                _range([c["zero_cycle"] for c in rows]),
                _range([c["final_stable"] for c in rows]),
                _range([c["deaths_total"] for c in rows]),
            )
        )

    if not controls["ceiling_reproduced"]["ok"]:
        failures.append("the engine's peak is not the ceiling's 35 at 0.5833")
    if not controls["decay_perturbation_applied"]["ok"]:
        failures.append("the decay perturbation was not applied as the arms declare")

    return {
        "date": date.today().isoformat(),
        "degree": DEGREE,
        "cycles": CYCLES,
        "seeds": sorted({p["seed"] for p in parts}),
        "cells": len(parts),
        "arms": list(ARMS),
        "delay_margin": DELAY_MARGIN,
        "preregistration": PREREG.relative_to(ROOT).as_posix(),
        "preregistration_sha256": protocol_digest(),
        "by_arm": {
            arm: {
                "cells": len(rows),
                "peak": _median([c["peak"] for c in rows]),
                "peak_range": _range([c["peak"] for c in rows]),
                "peak_cycle_range": _range([c["peak_cycle"] for c in rows]),
                "first_fall_range": _range([c["first_fall"] for c in rows]),
                "first_fall_by_seed": {str(c["seed"]): c["first_fall"] for c in rows},
                "half_life_range": _range([c["half_life_cycles"] for c in rows]),
                "zero_cycle_range": _range([c["zero_cycle"] for c in rows]),
                "final_stable_range": _range([c["final_stable"] for c in rows]),
                "final_coverage_range": _range([c["final_coverage"] for c in rows]),
                "increases_after_peak": [c["increases_after_peak"] for c in rows],
            }
            for arm, rows in sorted(by_arm.items())
        },
        "death_shares": shares,
        "deaths_total_engine": total_deaths,
        "ratio_at_peak": _range([c["median_ratio_at_peak"] for c in engine]),
        "ratio_after_peak": _range([c["median_ratio_after_peak"] for c in engine]),
        "hub_frequency_at_peak": _range([c["hub_frequency_at_peak"] for c in engine]),
        "hub_frequency_final": _range([c["hub_frequency_final"] for c in engine]),
        "temporal_sum_at_peak": _range([c["temporal_sum_at_peak"] for c in engine]),
        "temporal_sum_final": _range([c["temporal_sum_final"] for c in engine]),
        "theory_zero_range": _range([c["theory_zero_cycle"] for c in engine]),
        "peak_edge_death_shares": peak_shares,
        "peak_edge_deaths_total": peak_total,
        "peak_edge_last_death_range": _range([
            max(c["peak_edge_death_cycles"]) for c in engine if c["peak_edge_death_cycles"]
        ]),
        "peak_edges_alive_final_range": _range([
            c["peak_edges_alive_final"] for c in engine
            if c["peak_edges_alive_final"] is not None
        ]),
        "cycles_stable_exceeds_emitted_range": _range([
            c["cycles_stable_exceeds_emitted"] for c in engine
            if c["cycles_stable_exceeds_emitted"] is not None
        ]),
        "controls": controls,
        "predictions": predictions,
        "verdict": verdict,
        "findings": findings,
        "failures": failures,
    }


def _fmt(value) -> str:
    if value is None:
        return "not measurable"
    if isinstance(value, list):
        return "[%s, %s]" % (value[0], value[1])
    return str(value)


def render(record: dict) -> str:
    by = record["by_arm"]
    engine = by.get("engine", {})
    control = by.get("no_temporal_decay", {})
    shares = record["death_shares"]
    predictions = record["predictions"]
    lines = [
        "# What removes the degree-12 structure, and when",
        "",
        "**Generated from `docs/decay_attribution.json`. Do not edit this file.** Rebuild with",
        "`python -m benchmarks.decay_attribution --measure`; `--check` validates without writing.",
        "",
        "The protocol is `%s`, written before the run; the artifact records its SHA-256."
        % record["preregistration"],
        "",
        "## What was asked",
        "",
        "The budget ceiling ends at zero: peak coverage %s at every budget tested, final coverage"
        % _fmt(CEILING_COVERAGE),
        "0.00 at every budget tested. This run asks what removes the %d edges that reach the peak,"
        % CEILING_PEAK,
        "and at which cycle the removal starts.",
        "",
        "## What was run",
        "",
        "| Item | Value |",
        "| --- | --- |",
        "| World | `lattice_stream`, six triangles on hub `alpha`, degree %d |" % record["degree"],
        "| World edges | 60 |",
        "| Cycles | %d per cell |" % record["cycles"],
        "| Seeds | %s |" % ", ".join(str(s) for s in record["seeds"]),
        "| Cells | %d (%d arms x %d seeds) |"
        % (record["cells"], len(record["arms"]), len(record["seeds"])),
        "| Engine | pinned 0.13.0, unchanged |",
        "| Control | the same build with temporal edge decay disabled (factor 1.0) |",
        "",
        "## When the fall begins",
        "",
        "| Quantity | Engine | No temporal decay |",
        "| --- | --- | --- |",
        "| Peak stable edges | %s | %s |" % (_fmt(engine.get("peak")), _fmt(control.get("peak"))),
        "| Peak cycles | %s | %s |"
        % (_fmt(engine.get("peak_cycle_range")), _fmt(control.get("peak_cycle_range"))),
        "| First fall cycles | %s | %s |"
        % (_fmt(engine.get("first_fall_range")), _fmt(control.get("first_fall_range"))),
        "| Half-life from the peak (cycles) | %s | %s |"
        % (_fmt(engine.get("half_life_range")), _fmt(control.get("half_life_range"))),
        "| Cycle stable edges reach zero | %s | %s |"
        % (_fmt(engine.get("zero_cycle_range")), _fmt(control.get("zero_cycle_range"))),
        "| Final stable edges | %s | %s |"
        % (_fmt(engine.get("final_stable_range")), _fmt(control.get("final_stable_range"))),
        "| Final coverage | %s | %s |"
        % (_fmt(engine.get("final_coverage_range")), _fmt(control.get("final_coverage_range"))),
        "| Cycles that grew after the peak | %s | %s |"
        % (_fmt(engine.get("increases_after_peak")), _fmt(control.get("increases_after_peak"))),
        "",
        "The first fall is the first cycle after the peak whose stable-edge count is below the",
        "peak. The half-life is measured from the peak cycle and is reported as not measurable",
        "when the peak is zero or the series never reaches half of it.",
        "",
        "## What removed them",
        "",
        "| Death reason | Share of the engine's %d edge deaths |" % record["deaths_total_engine"],
        "| --- | --- |",
        "| `below_threshold` (re-emitted, strength under 0.30) | %s |"
        % _fmt(shares.get("below_threshold")),
        "| `decayed` (not re-emitted, x0.8 under 0.30) | %s |" % _fmt(shares.get("decayed")),
        "| `pruned` (not re-emitted, x0.8 under 0.15) | %s |" % _fmt(shares.get("pruned")),
        "| `unexplained` (the ledger disagrees with the engine) | %s |"
        % _fmt(shares.get("unexplained", 0.0)),
        "",
        "## The peak's own edges",
        "",
        "The count above includes churn: an edge can die and re-form. This table follows only the",
        "edges that made the peak, to their own first deaths.",
        "",
        "| Quantity | Engine |",
        "| --- | --- |",
        "| Peak edges followed | %s deaths across the seeds |" % record["peak_edge_deaths_total"],
        "| Alive at the final cycle | %s |" % _fmt(record["peak_edges_alive_final_range"]),
        "| Latest death among the peak edges (cycle) | %s |"
        % _fmt(record["peak_edge_last_death_range"]),
        "| Re-emitted, strength under 0.30 | %s |" % _fmt(record["peak_edge_death_shares"].get("below_threshold")),
        "| Not re-emitted, x0.8 under 0.30 | %s |" % _fmt(record["peak_edge_death_shares"].get("decayed")),
        "| Not re-emitted, x0.8 under 0.15 | %s |" % _fmt(record["peak_edge_death_shares"].get("pruned")),
        "| Cycles where more edges were stable than were re-emitted | %s |"
        % _fmt(record["cycles_stable_exceeds_emitted_range"]),
        "",
        "## The quantity that moves",
        "",
        "| Quantity | At the peak | After the peak | At the end |",
        "| --- | --- | --- | --- |",
        "| Median ratio (temporal count / source frequency), engine | %s | %s | not recorded |"
        % (_fmt(record["ratio_at_peak"]), _fmt(record["ratio_after_peak"])),
        "| Hub tag frequency, engine | %s | | %s |"
        % (_fmt(record["hub_frequency_at_peak"]), _fmt(record["hub_frequency_final"])),
        "| Temporal graph total, engine | %s | | %s |"
        % (_fmt(record["temporal_sum_at_peak"]), _fmt(record["temporal_sum_final"])),
        "",
        "## Predictions, scored",
        "",
        "| Prediction | Held | Observed |",
        "| --- | --- | --- |",
    ]
    for name, entry in predictions.items():
        observed = entry.get("observed")
        if isinstance(observed, dict):
            observed = "; ".join("%s=%s" % (k, _fmt(v)) for k, v in sorted(observed.items()))
        elif isinstance(observed, list):
            observed = _fmt(observed)
        else:
            observed = _fmt(observed)
        lines.append("| `%s` | %s | %s |" % (name, "yes" if entry["held"] else "**no**", observed))
    lines += [
        "",
        "## Verdict",
        "",
        "**%s.** %s" % (record["verdict"], CROWN[record["verdict"]]),
        "",
    ]
    if record["failures"]:
        lines += ["## Gate failures", ""]
        lines += ["- " + failure for failure in record["failures"]]
        lines.append("")
    lines += [
        "## What this establishes",
        "",
        "- **When the fall starts is measured, not inferred.** The first fall cycle is the engine's",
        "  own stable-edge series, not the first cycle in which coverage looks low.",
        "- **The removal has a named reason per death.** Every engine-arm death is attributed from",
        "  whether the edge was re-emitted and what the engine stored it as; an unattributable death",
        "  is reported as a defect and fails the run.",
        "- **The control either separates the arms or it does not.** The label is read from the",
        "  contrast, so a control that collapses with the engine falsifies the decay explanation.",
        "",
        "## What it does not establish",
        "",
        "- **One world, one degree, three seeds.** It attributes this collapse, not every collapse.",
        "- **Structural coverage only.** It counts world edges asserted, not prediction quality.",
        "- **Only the graph decay is ablated.** The candidate decay (x0.8) and the strength rule are",
        "  unchanged in both arms, so their share is read from the reasons rather than from a",
        "  second arm.",
        "",
    ]
    return "\n".join(lines)


CROWN = {
    "TEMPORAL_EDGE_DECAY": (
        "The control keeps its edges and the engine does not, so the graph's per-cycle decay is "
        "the removal mechanism. The next experiment belongs to the decay rule, not to the theory "
        "budget."
    ),
    "TEMPORAL_EDGE_DECAY_PARTIAL": (
        "The control also falls, but later than the engine did, so the graph decay contributes to "
        "the collapse without accounting for it. The residual loss is a second mechanism that must "
        "be named before anything is changed."
    ),
    "NOT_TEMPORAL_DECAY": (
        "Disabling the graph decay did not keep the edges, so the decay is not the killer. The "
        "strength rule or the frequency denominator is, and the next experiment moves there."
    ),
    "NO_COLLAPSE": (
        "The engine did not reach zero in this run, so the instrument cannot see the recorded "
        "death. Nothing is attributed, and the missing collapse is reported rather than scored."
    ),
    "CEILING_NOT_REPRODUCED": (
        "The engine's peak is not the ceiling's measured 35 at 0.5833, so this run is not the one "
        "being explained and no mechanism is read from it."
    ),
}


def problems(record: dict) -> list[str]:
    found: list[str] = []
    parts = load_parts()
    if len(parts) != len(ARMS) * SEED_COUNT:
        found.append("the record covers %d cells, not %d" % (len(parts), len(ARMS) * SEED_COUNT))
    fresh = analyse(parts)
    for key in ("verdict", "by_arm", "death_shares", "predictions", "controls"):
        if record.get(key) != fresh.get(key):
            found.append("the recorded %s does not match a fresh analysis of the parts" % key)
    if record.get("seeds") != sorted({p["seed"] for p in parts}):
        found.append("the recorded seeds do not match the parts")
    if not record.get("preregistration_sha256"):
        found.append("the artifact records no protocol hash")
    elif record["preregistration_sha256"] != protocol_digest():
        found.append("the pre-registration's protocol sections changed after the run")
    if record.get("failures"):
        found.append("the record carries failures: %s" % "; ".join(record["failures"]))
    if record.get("verdict") == "TEMPORAL_EDGE_DECAY":
        control_cells = [summarise(p) for p in parts if p["arm"] == "no_temporal_decay"]
        if any(c.get("measurable") and c["final_stable"] == 0 for c in control_cells):
            found.append("the verdict says the control survives but its final count is zero")
    if not DOC.exists():
        found.append("the result document does not exist")
    elif DOC.read_text(encoding="utf-8") != render(record):
        found.append("%s is stale; rebuild with python -m benchmarks.decay_attribution" % DOC.name)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measure", action="store_true", help="run any missing cells, then write")
    parser.add_argument("--reuse", action="store_true", help="summarise the existing cells")
    parser.add_argument("--check", action="store_true", help="validate without writing")
    args = parser.parse_args(argv)

    if args.check:
        found = problems(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("decay attribution: %s" % json.loads(ARTIFACT.read_text(encoding="utf-8"))["verdict"])
        return 0

    if args.measure or args.reuse:
        seeds = attribution_seeds()
        if args.measure:
            run(seeds)
        record = analyse(load_parts())
        ARTIFACT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        DOC.write_text(render(record), encoding="utf-8")
        for line in record["findings"]:
            print("finding:", line)
        for line in record["failures"]:
            print("FAIL:", line)
        print("verdict:", record["verdict"])
        return 0 if not record["failures"] else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
