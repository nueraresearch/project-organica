"""The decay-attribution replication: 12 fresh seeds, 2 arms, the frozen protocol's gates.

Pre-registered in ``docs/DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md`` (sections 1-9 pinned by
SHA-256, section 11 pinned separately). The runner executes that protocol; it does not choose its
own targets. Everything the decision table reads is computed here from the ledger and recorded in
``docs/decay_attribution_study.json``:

- the six replication targets P1-P6 and the six gates G1-G6;
- P7 (``decayed`` share) and P8 (empty core) from the section 11 amendment;
- the four decision-table labels and the three secondary characterizations.

Operational detail worth naming: P8 says "no edge stays stable continuously from the peak cycle to
the first cycle with zero stable edges". At the first zero cycle the stable set is empty by
definition, so the literal reading cannot fire. The runner reads it as *stable through the last
non-empty cycle before the collapse* -- the last cycle in which a core could still exist -- and says
so here rather than in the outcome.

Run::

    python -m benchmarks.decay_attribution_study --run
    python -m benchmarks.decay_attribution_study --render
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from benchmarks.decay_attribution import CYCLES, DEGREE, cell as attribution_cell
from benchmarks.decay_attribution_study_prereg import (
    AMENDMENT_DIGEST,
    ARMS,
    ARTIFACT,
    BUCKETS,
    DOC as PREREG,
    FROZEN_DIGEST,
    SEEDS,
    amendment_digest,
    protocol_digest,
)
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGE = DOCS / "DECAY-ATTRIBUTION-STUDY.md"
PARTS = DOCS / "decay_attribution_study" / "parts"

QUESTIONS = ("Q029", "Q030", "Q031", "Q032", "Q036")
SECONDARY = ("Q033", "Q034", "Q035", "Q037")
SHIFT_BAND = (0.25, 0.40)
HALF_LIFE_BAND = (40, 90)


def cell(arm: str, seed: int) -> dict:
    """One cell: the first harness's ledger plus the per-cycle stable sets P8 needs."""
    history: list[set] = []
    row = attribution_cell(arm, seed, CYCLES, stable_history=history)
    series = row["series"]
    peak = max((r["stable"] for r in series), default=0)
    peak_index = next((i for i, r in enumerate(series) if r["stable"] == peak), None)
    peak_row = series[peak_index] if peak_index is not None else None

    first_zero_index = next((i for i, r in enumerate(series) if r["stable"] == 0), None)
    last_nonempty = (first_zero_index - 1) if first_zero_index is not None else len(series) - 1
    peak_set = history[peak_index] if peak_index is not None else set()
    core_edges: list[tuple[str, str]] = []
    if peak_index is not None and 0 <= peak_index <= last_nonempty:
        core_edges = sorted(
            edge for edge in peak_set
            if all(edge in history[i] for i in range(peak_index, last_nonempty + 1))
        )
    alive_at_last = (
        sorted(edge for edge in peak_set if edge in history[last_nonempty])
        if 0 <= last_nonempty < len(history) else []
    )

    first_fall = None
    if peak_index is not None:
        first_fall = next(
            (series[i]["cycle"] for i in range(peak_index + 1, len(series))
             if series[i]["stable"] < peak),
            None,
        )
    last_theory = max((r["cycle"] for r in series if r["theories"] > 0), default=None)

    half_life = None
    if peak_index is not None and peak > 0:
        target = peak / 2
        found = next((i for i in range(peak_index + 1, len(series))
                      if series[i]["stable"] <= target), None)
        if found is not None:
            half_life = series[found]["cycle"] - series[peak_index]["cycle"]

    reasons: Counter = Counter()
    for r in series:
        for name, count in (r.get("by_reason") or {}).items():
            reasons[name] += int(count)
    deaths = sum(reasons.values())

    def share(name: str):
        return round(reasons[name] / deaths, 4) if deaths else None

    return {
        "arm": arm,
        "seed": seed,
        "cycles": CYCLES,
        "degree": DEGREE,
        "world_edges": row["world_edges"],
        "peak": peak,
        "peak_cycle": series[peak_index]["cycle"] if peak_index is not None else None,
        "peak_hits": peak_row["hits"] if peak_row else None,
        "peak_coverage": peak_row["coverage"] if peak_row else None,
        "final": series[-1]["stable"] if series else None,
        "first_fall_cycle": first_fall,
        "last_theory_cycle": last_theory,
        "first_zero_cycle": series[first_zero_index]["cycle"] if first_zero_index is not None else None,
        "half_life_cycles": half_life,
        "deaths": deaths,
        "by_reason": dict(reasons),
        "below_threshold_share": share("below_threshold"),
        "decayed_share": share("decayed"),
        "pruned_share": share("pruned"),
        "unexplained_share": share("unexplained"),
        "peak_edges": len(peak_set),
        "peak_edges_alive_at_last_nonempty": len(alive_at_last),
        "core_edges": len(core_edges),
        "core_survives": bool(core_edges),
        "decay_factor_seen": sorted({r["decay_factor"] for r in series}, key=str),
        "decay_rows_min": min((r["decay_rows"] or 0) for r in series) if series else 0,
        "series": series,
    }


def gates_for(engine: list[dict], control: list[dict]) -> dict[str, bool]:
    """G1-G6, each read from the recorded cells and each able to fail."""
    return {
        "G1_perturbation_happened": (
            all(set(r["decay_factor_seen"]) == {0.95} and r["decay_rows_min"] > 0 for r in engine)
            and all(set(r["decay_factor_seen"]) == {1.0} for r in control)
        ),
        "G2_ceiling_reproduced": all(
            r["peak"] == 35 and r["peak_coverage"] == 0.5833 for r in engine
        ),
        "G3_collapse_visible": sum(1 for r in engine if r["first_zero_cycle"] is not None) >= 11,
        "G4_contrast_exists": sum(
            1 for r in control
            if r["first_zero_cycle"] is None and (r["final"] or 0) >= 1
        ) >= 11,
        "G5_attribution_complete": all(r["by_reason"].get("unexplained", 0) == 0 for r in engine),
        "G6_denominator_exists": all(r["deaths"] > 0 for r in engine if r["peak"] > 0),
    }


def predictions_for(engine: list[dict], control: list[dict]) -> dict[str, bool]:
    """P1-P8. A band that cannot be computed (no deaths, no half-life) fails rather than passes."""
    def in_band(value, band):
        return value is not None and band[0] <= value <= band[1]

    return {
        "P1_ceiling": all(r["peak"] == 35 and r["peak_coverage"] == 0.5833 for r in engine),
        "P2_final_zero": all(r["final"] == 0 for r in engine),
        "P3_fall_before_theory_death": sum(
            1 for r in engine
            if r["first_fall_cycle"] is not None and r["last_theory_cycle"] is not None
            and r["first_fall_cycle"] <= r["last_theory_cycle"]
        ) >= 11,
        "P4_control_survives": sum(
            1 for r in control
            if r["first_zero_cycle"] is None and (r["final"] or 0) >= 1
        ) >= 11,
        "P5_below_threshold_band": all(
            in_band(r["below_threshold_share"], SHIFT_BAND) for r in engine
        ),
        "P6_half_life_band": all(in_band(r["half_life_cycles"], HALF_LIFE_BAND) for r in engine),
        "P7_decayed_majority": all((r["decayed_share"] or 0) >= 0.50 for r in engine),
        "P8_empty_core": all(not r["core_survives"] for r in engine),
    }


def decide(engine: list[dict], control: list[dict]) -> dict:
    """The frozen decision table, with a void before every scientific bucket."""
    gates = gates_for(engine, control)
    preds = predictions_for(engine, control)
    instrument_ok = all(gates[name] for name in (
        "G1_perturbation_happened", "G2_ceiling_reproduced",
        "G5_attribution_complete", "G6_denominator_exists",
    ))
    p1_fail = sum(1 for r in engine if not (r["peak"] == 35 and r["peak_coverage"] == 0.5833))
    p2_fail = sum(1 for r in engine if r["final"] != 0)
    table_gap = None

    if not instrument_ok:
        label = "VOID_INSTRUMENT"
    elif (not gates["G3_collapse_visible"] or not gates["G4_contrast_exists"]
          or p1_fail >= 2 or p2_fail >= 2):
        label = "NOT_REPLICATED"
    elif (all(preds[name] for name in ("P1_ceiling", "P2_final_zero",
                                       "P5_below_threshold_band", "P6_half_life_band"))
          and preds["P3_fall_before_theory_death"] and preds["P4_control_survives"]):
        label = "REPLICATED"
    elif (p1_fail == 0 and p2_fail == 0 and gates["G4_contrast_exists"]):
        label = "REPLICATED_WITH_SHIFT"
        if preds["P5_below_threshold_band"] and preds["P6_half_life_band"]:
            table_gap = (
                "P5 and P6 held; the criterion that failed is outside the WITH_SHIFT condition, "
                "which names only P5 and P6"
            )
    else:
        label = "NOT_REPLICATED"
        if p1_fail < 2 and p2_fail < 2:
            table_gap = (
                "P1 and P2 did not hold in enough seeds for WITH_SHIFT, but the NOT_REPLICATED "
                "condition (two or more failures) was not met either"
            )
    return {"label": label, "gates": gates, "predictions": preds, "table_gap": table_gap}


def secondary_for(engine: list[dict]) -> dict:
    """The three section 11 characterizations, each with its own pre-committed decision."""
    zeros = [r["first_zero_cycle"] for r in engine if r["first_zero_cycle"] is not None]
    zero_range = (max(zeros) - min(zeros)) if zeros else None
    survivors = [r["seed"] for r in engine if r["core_survives"]]
    if len(survivors) >= 2:
        core = "CORE_SURVIVES"
    elif survivors:
        core = None
    else:
        core = "FULL_COLLAPSE"
    schedule = None
    if zero_range is not None:
        schedule = "COLLAPSE_SCHEDULED" if zero_range <= 2 else "COLLAPSE_SEEDED"
    threshold_seeds = sum(1 for r in engine if (r["below_threshold_share"] or 0) >= 0.50)
    if all((r["decayed_share"] or 0) >= 0.50 for r in engine):
        mechanism = "DECAY_DOMINANT"
    elif threshold_seeds > len(engine) / 2:
        mechanism = "THRESHOLD_DOMINANT"
    else:
        mechanism = None
    return {
        "core": core,
        "core_survives_seeds": survivors,
        "collapse": schedule,
        "first_zero_range": zero_range,
        "mechanism": mechanism,
        "threshold_seeds": threshold_seeds,
        "decayed_seeds": sum(1 for r in engine if (r["decayed_share"] or 0) >= 0.50),
    }


def _path(arm: str, seed: int) -> Path:
    return PARTS / ("cell_%s_s%d.json" % (arm, seed))


def run(seeds=SEEDS, arms=ARMS) -> int:
    from benchmarks.decay_confirmation import harvest_seeds

    overlap = sorted(set(seeds) & (harvest_seeds(DOCS) - set(SEEDS)))
    if overlap:
        raise SystemExit("seed block overlaps an existing record under docs/: %s" % overlap)
    PARTS.mkdir(parents=True, exist_ok=True)
    for arm in arms:
        for seed in seeds:
            path = _path(arm, seed)
            if path.exists():
                print("cached", path.name, flush=True)
                continue
            row = cell(arm, seed)
            path.write_text(json.dumps(engine_stamp.stamp(row), indent=1) + "\n", encoding="utf-8")
            print(
                "%-17s s%d peak=%2d final=%2d zero=%s half=%s below=%s decayed=%s core=%d"
                % (arm, seed, row["peak"], row["final"], row["first_zero_cycle"],
                   row["half_life_cycles"], row["below_threshold_share"],
                   row["decayed_share"], row["core_edges"]),
                flush=True,
            )
    return 0


def load_cells(seeds=SEEDS, arms=ARMS) -> list[dict]:
    rows = []
    for arm in arms:
        for seed in seeds:
            path = _path(arm, seed)
            if not path.exists():
                raise SystemExit("missing cell %s; run the study first" % path.name)
            rows.append(json.loads(path.read_text(encoding="utf-8")))
    return rows


def build(cells: list[dict]) -> dict:
    engine = [r for r in cells if r["arm"] == "engine"]
    control = [r for r in cells if r["arm"] == "no_temporal_decay"]
    decision = decide(engine, control)
    text = PREREG.read_text(encoding="utf-8")
    return {
        "kind": "decay_attribution_study",
        "protocol": "docs/DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md",
        "protocol_digest": protocol_digest(text),
        "amendment_digest": amendment_digest(text),
        "date": "2026-11-07",
        "questions": list(QUESTIONS),
        "secondary_questions": list(SECONDARY),
        "seeds": list(SEEDS),
        "arms": list(ARMS),
        "cycles": CYCLES,
        "degree": DEGREE,
        "label": decision["label"],
        "table_gap": decision["table_gap"],
        "gates": decision["gates"],
        "predictions": decision["predictions"],
        "secondary": secondary_for(engine),
        "cells": [{k: v for k, v in r.items() if k != "series"} for r in cells],
        "series": {"%s/s%d" % (r["arm"], r["seed"]): r["series"] for r in cells},
        "no_engine_change": True,
    }


def render(artifact: dict) -> str:
    lines = [
        "# The decay-attribution replication — result",
        "",
        "Generated from `docs/decay_attribution_study.json` by",
        "`python -m benchmarks.decay_attribution_study --render`. Do not edit by hand.",
        "",
        "Pre-registration: `docs/DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md`, sections 1-9 pinned at",
        "`%s`. Engine 0.13.0, unchanged." % artifact["protocol_digest"],
        "",
        "## Label",
        "",
        "**%s**" % artifact["label"],
        "",
    ]
    if artifact["table_gap"]:
        lines += [
            "**Decision-table gap recorded:** %s." % artifact["table_gap"],
            "",
        ]
    lines += [
        "## Gates",
        "",
        "| Gate | Result |",
        "| --- | --- |",
    ]
    for name, ok in artifact["gates"].items():
        lines.append("| %s | %s |" % (name, "pass" if ok else "FAIL"))
    lines += [
        "",
        "## Replication targets",
        "",
        "| Prediction | Result |",
        "| --- | --- |",
    ]
    for name, ok in artifact["predictions"].items():
        lines.append("| %s | %s |" % (name, "held" if ok else "failed"))
    lines += [
        "",
        "## Secondary characterizations",
        "",
        "| Question | Label |",
        "| --- | --- |",
        "| Q033 stable core | %s |" % artifact["secondary"]["core"],
        "| Q034 collapse timing | %s |" % artifact["secondary"]["collapse"],
        "| Q037 dominant mechanism | %s |" % artifact["secondary"]["mechanism"],
        "",
        "First-zero range across the 12 engine seeds: %s cycles."
        % artifact["secondary"]["first_zero_range"],
        "",
        "## Per seed, engine arm",
        "",
        "| Seed | Peak | Final | First zero | Half-life | Below-threshold share | Decayed share | Core edges |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact["cells"]:
        if row["arm"] != "engine":
            continue
        lines.append(
            "| %d | %d | %s | %s | %s | %s | %s | %d |"
            % (row["seed"], row["peak"], row["final"], row["first_zero_cycle"],
               row["half_life_cycles"], row["below_threshold_share"],
               row["decayed_share"], row["core_edges"])
        )
    lines += [
        "",
        "## Per seed, control arm",
        "",
        "| Seed | Peak | Final | First zero | Below-threshold share | Decayed share |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact["cells"]:
        if row["arm"] == "engine":
            continue
        lines.append(
            "| %d | %d | %s | %s | %s | %s |"
            % (row["seed"], row["peak"], row["final"], row["first_zero_cycle"],
               row["below_threshold_share"], row["decayed_share"])
        )
    lines += [
        "",
        "## What this establishes",
        "",
        "Whether the first study's values survive twelve seeds the first study never touched, and",
        "the label the frozen table assigns to that answer. It does not test new worlds, degrees or",
        "stimuli, and it contains no repair arm.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--arm", choices=ARMS)
    args = parser.parse_args(argv)
    arms = (args.arm,) if args.arm else ARMS
    if args.run:
        return run(SEEDS, arms)
    if args.render:
        artifact = build(load_cells())
        ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        PAGE.write_text(render(artifact), encoding="utf-8")
        print("label:", artifact["label"])
        print("gates:", artifact["gates"])
        print("predictions:", artifact["predictions"])
        return 0
    if args.check:
        if not ARTIFACT.exists() or not PAGE.exists():
            print("FAIL: the artifact or page is missing")
            return 1
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        text = PREREG.read_text(encoding="utf-8")
        problems = []
        if artifact.get("protocol_digest") != FROZEN_DIGEST:
            problems.append("artifact digest is not the frozen one")
        if artifact.get("label") not in BUCKETS:
            problems.append("label is not one of the frozen buckets")
        if protocol_digest(text) != artifact.get("protocol_digest"):
            problems.append("the protocol text moved after the artifact was written")
        if amendment_digest(text) != AMENDMENT_DIGEST:
            problems.append("the amendment text moved")
        if PAGE.read_text(encoding="utf-8") != render(artifact):
            problems.append("the page is stale")
        for problem in problems:
            print("FAIL:", problem)
        return 1 if problems else 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
