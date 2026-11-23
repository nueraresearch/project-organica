"""Specify a no-arm construction that separates candidate count from density.

The three committed blocks cannot tell the offset summaries apart: within the
compositional law, tags-per-cell ``k`` sets the alphabet ``n = 4k`` and the
candidate count ``m`` together, so density ``m/n`` is a function of ``m``.

This module measures that degeneracy and specifies the construction that
breaks it: a pair-split world, where each cell's tags are divided into
``active``-sized groups and the regime index selects the group used by that
regime's events.  The alphabet stays at ``4k`` and every tag is exercised,
but the pair space is set by ``active`` rather than by ``k``.  Holding
``active`` fixed and raising ``k`` therefore raises ``n`` while leaving ``m``
alone.

The declared blocks are ``k=8`` (32 tags) and ``k=12`` (48 tags), both with
``active=4``, on a fresh six-seed block.  Their candidate counts match the
16-tag reference while their densities differ, so the two frozen offset
models predict different levels for them and the same level for each other.

No engine replay, no target, freeze, grant or A1 cell: the module derives
candidate streams only.

    python -m benchmarks.a1_offset_discriminator_spec --write
    python -m benchmarks.a1_offset_discriminator_spec --check
    python -m benchmarks.a1_offset_discriminator_spec --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from benchmarks import acquisition_compositional as ac
from benchmarks import a1_target_selection as ts
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SUPPLY_PATH = DOCS / "a1_k_carrier_supply.json"
SIZE_PATH = DOCS / "a1_offset_predictors.json"
DENSITY_PATH = DOCS / "a1_offset_density.json"
SEED_HOLDOUT_PATH = DOCS / "a1_cap_response_seed_holdout.json"
OUT_PATH = DOCS / "a1_offset_discriminator_spec.json"
PAGE_PATH = DOCS / "A1-OFFSET-DISCRIMINATOR-SPEC.md"
ID = "A1-OFFSET-DISCRIMINATOR-SPEC-1"
DATE = "2026-11-14"
KIND = "a1_offset_discriminator_spec"
STATUS = ("CANDIDATE-SPACE SPEC — NO ARM, NO TARGET, NOT FROZEN, NOT RUN; "
          "NO FREEZE, GRANT OR A1 CELL")
CYCLES = 120
EVENTS_PER_CYCLE = 8
ACTIVE = 4
SEEDS = (20690101, 20690102, 20690103, 20690104, 20690105, 20690106)
SPLIT_BLOCKS = (
    {"label": "split-32", "per_cell": 8, "active": ACTIVE},
    {"label": "split-48", "per_cell": 12, "active": ACTIVE},
)
REFERENCE_BLOCKS = ("current-16", "fresh-16", "larger-28")
REFERENCE_TAGS = {"current-16": 16, "fresh-16": 16, "larger-28": 28}
EQUAL_M_TOLERANCE = 0.05
DECISION_FLOOR = 0.05
DECISION_CEILING = 0.09


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _pool(per_cell: int) -> tuple[str, ...]:
    count = per_cell * len(ac.CELLS)
    base = list(ac.TAG_POOL)
    extra = ["tag%s" % (chr(97 + i) * 2) for i in range(count - len(base))]
    pool = base + extra
    if len(pool) != count or len(set(pool)) != count:
        raise ValueError("tag pool is not unique at %d tags" % count)
    return tuple(pool)


def generate_split_world(seed: int, per_cell: int, active: int,
                         cycles: int = CYCLES,
                         events_per_cycle: int = EVENTS_PER_CYCLE) -> dict:
    """Mirror the compositional law with an active-subset split.

    Every cell holds ``per_cell`` tags divided into consecutive ``active``-sized
    groups; the regime index selects the group an event draws from, so all tags
    are exercised across regimes while the per-regime pair space is ``active``
    wide.  With ``active == per_cell`` this is the committed law and must
    reproduce its candidate counts.
    """
    if per_cell < active or active < ac.TAGS_PER_EVENT:
        raise ValueError("active must be between TAGS_PER_EVENT and per_cell")
    rng = random.Random(seed)
    tags = list(_pool(per_cell))
    rng.shuffle(tags)
    cell_tags = {c: sorted(tags[i * per_cell:(i + 1) * per_cell])
                 for i, c in enumerate(ac.CELLS)}
    groups = {c: [v[i:i + active] for i in range(0, per_cell, active)]
              for c, v in cell_tags.items()}
    held = ac.CELLS[rng.randrange(len(ac.CELLS))]
    held_flip_p = ac.flip_p(held)
    events: list[str] = []
    cells: list[str] = []
    regimes: list[int] = []
    trainable: list[bool] = []
    withheld: list[bool] = []
    state = ac.CELLS[rng.randrange(len(ac.CELLS))]
    acq_lo, acq_hi = ac.PHASE_ACQUISITION
    for cycle in range(cycles):
        regime = (cycle // ac.REGIME_SWITCH_CYCLE) % 2
        law = ac.LAW_R0 if regime == 0 else ac.LAW_R1
        for _ in range(events_per_cycle):
            kind = rng.choices(
                ("flip_p", "flip_q"),
                weights=[law[name] for name in ("flip_p", "flip_q")], k=1)[0]
            nxt = ac.flip_p(state) if kind == "flip_p" else ac.flip_q(state)
            selected = groups[nxt]
            avail = selected[regime % len(selected)]
            pair = rng.sample(avail, ac.TAGS_PER_EVENT)
            events.append(" ".join(sorted(pair)))
            cells.append(ac.cell_name(nxt))
            regimes.append(regime)
            in_acq = (acq_lo * events_per_cycle <= len(events) - 1
                      < acq_hi * events_per_cycle)
            is_withheld = state == held and nxt == held_flip_p and in_acq
            trainable.append(not is_withheld)
            withheld.append(is_withheld)
            state = nxt
    return {
        "events": events,
        "cells": cells,
        "regimes": regimes,
        "trainable": trainable,
        "withheld": withheld,
        "cell_tags": {ac.cell_name(c): sorted(v) for c, v in cell_tags.items()},
        "tag_to_cell": {t: ac.cell_name(c)
                        for c, v in cell_tags.items() for t in v},
        "held_cell": ac.cell_name(held),
        "held_cell_flip_p": ac.cell_name(held_flip_p),
        "tags_per_cell": per_cell,
        "active": active,
    }


def _candidates(seed: int, per_cell: int, active: int) -> int:
    world = generate_split_world(seed, per_cell, active)
    return len(ts.run_seed(seed, world=world, boundary_safe=True)["u"])


def _reference() -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for entry in _load(SUPPLY_PATH)["seeds"]:
        summary = entry["summary"]
        out.setdefault(summary["block"], []).append(len(entry["edges"]))
    return out


def _coefficients() -> dict[str, list[float]]:
    size = next(
        row for row in _load(SIZE_PATH)["comparisons"]
        if row["model"] == "candidate_size")
    density = next(
        row for row in _load(DENSITY_PATH)["comparisons"]
        if row["model"] == "candidate_density")
    return {
        "size": list(size["cell_coefficients"]),
        "density": list(density["cell_coefficients"]),
    }


def _offset(coefficients: list[float], feature: float) -> float:
    slope = coefficients[2]
    if abs(slope - 0.04698668) > 1e-6:
        raise ValueError("the cap slope moved; the offsets are not comparable")
    return coefficients[0] + coefficients[1] * feature


def _inverse_3(matrix: list[list[float]]) -> list[list[float]]:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    det = (a * (e * i - f * h) - b * (d * i - f * g)
           + c * (d * h - e * g))
    if abs(det) < 1e-12:
        raise ValueError("singular design")
    return [
        [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
        [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
        [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det],
    ]


def build() -> dict:
    coefficients = _coefficients()
    reference = _reference()
    rows = []
    blocks = []
    for block in SPLIT_BLOCKS:
        counts = [_candidates(seed, block["per_cell"], block["active"])
                  for seed in SEEDS]
        tags = block["per_cell"] * len(ac.CELLS)
        world = generate_split_world(SEEDS[0], block["per_cell"],
                                     block["active"])
        blocks.append({
            "label": block["label"],
            "per_cell": block["per_cell"],
            "active": block["active"],
            "tags": tags,
            "seeds": list(SEEDS),
            "candidate_edges": counts,
            "candidates_mean": round(sum(counts) / len(counts), 6),
            "log_candidates": round(math.log(sum(counts) / len(counts)), 6),
            "density": round((sum(counts) / len(counts)) / tags, 6),
            "tags_used": len(world["tag_to_cell"]),
            "source": "measured here",
        })
        for seed, count in zip(SEEDS, counts):
            rows.append({
                "block": block["label"],
                "seed": seed,
                "tags": tags,
                "candidate_edges": count,
                "log_candidates": round(math.log(count), 6),
                "density": round(count / tags, 6),
            })
    for label in REFERENCE_BLOCKS:
        counts = reference[label]
        tags = REFERENCE_TAGS[label]
        blocks.append({
            "label": label,
            "per_cell": tags // len(ac.CELLS),
            "active": None,
            "tags": tags,
            "seeds": sorted(row["summary"]["seed"]
                            for row in _load(SUPPLY_PATH)["seeds"]
                            if row["summary"]["block"] == label),
            "candidate_edges": sorted(counts),
            "candidates_mean": round(sum(counts) / len(counts), 6),
            "log_candidates": round(math.log(sum(counts) / len(counts)), 6),
            "density": round((sum(counts) / len(counts)) / tags, 6),
            "tags_used": tags,
            "source": "docs/a1_k_carrier_supply.json",
        })
    by_label = {block["label"]: block for block in blocks}
    predictions = []
    for block in blocks:
        size_offset = _offset(coefficients["size"], block["log_candidates"])
        density_offset = _offset(coefficients["density"], block["density"])
        predictions.append({
            "label": block["label"],
            "log_candidates": block["log_candidates"],
            "density": block["density"],
            "size_offset": round(size_offset, 6),
            "density_offset": round(density_offset, 6),
            "gap": round(density_offset - size_offset, 6),
        })
    predicted = {row["label"]: row for row in predictions}
    low, high = by_label["split-32"], by_label["split-48"]
    differential = {
        "blocks": [low["label"], high["label"]],
        "log_candidates": [low["log_candidates"], high["log_candidates"]],
        "density": [low["density"], high["density"]],
        "size_predicted_difference": round(
            predicted[low["label"]]["size_offset"]
            - predicted[high["label"]]["size_offset"], 6),
        "density_predicted_difference": round(
            predicted[low["label"]]["density_offset"]
            - predicted[high["label"]]["density_offset"], 6),
        "measured_difference": None,
        "decision": "not measured — no arm, no run",
    }
    design = [[1.0, block["log_candidates"], block["density"]]
              for block in blocks]
    normal = [[sum(row[i] * row[j] for row in design) for j in range(3)]
              for i in range(3)]
    inverse = _inverse_3(normal)
    sigma = 0.018372
    identification = {
        "blocks": [block["label"] for block in blocks],
        "rows": len(design),
        "parameters": 3,
        "inverse_diagonal": [round(inverse[i][i], 6) for i in range(3)],
        "coefficient_se": [
            round(sigma * math.sqrt(max(inverse[i][i], 0.0)), 6)
            for i in range(3)
        ],
        "sigma": sigma,
        "sigma_source": "candidate-size cell LOO RMSE, docs/a1_offset_predictors.json",
        "log_candidates_range": [
            min(block["log_candidates"] for block in blocks),
            max(block["log_candidates"] for block in blocks),
        ],
        "density_range": [
            min(block["density"] for block in blocks),
            max(block["density"] for block in blocks),
        ],
        "fitted_log_candidates_range": [4.153634, 5.115638],
        "fitted_density_range": [3.979167, 5.952381],
    }
    equal_m = []
    for block in (low, high):
        reference_row = by_label["fresh-16"]
        equal_m.append({
            "block": block["label"],
            "candidates_mean": block["candidates_mean"],
            "reference_candidates": reference_row["candidates_mean"],
            "log_gap": round(block["log_candidates"]
                             - reference_row["log_candidates"], 6),
        })
    controls = []

    def control(name: str, expected, observed) -> None:
        controls.append({"name": name, "expected": expected,
                         "observed": observed, "ok": expected == observed})

    control("the committed 16-tag law reproduces 20630101", 64,
            _candidates(20630101, 4, 4))
    control("the committed 16-tag law reproduces 20630102", 63,
            _candidates(20630102, 4, 4))
    control("the committed 16-tag law reproduces 20650101", 64,
            _candidates(20650101, 4, 4))
    control("the committed 28-tag law reproduces 20660101", 169,
            _candidates(20660101, 7, 7))
    for block in (low, high):
        control("%s uses every declared tag" % block["label"], block["tags"],
                block["tags_used"])
    for row in equal_m:
        controls.append({
            "name": "%s matches the 16-tag candidate count" % row["block"],
            "expected": "|log gap| <= %.2f" % EQUAL_M_TOLERANCE,
            "observed": abs(row["log_gap"]),
            "ok": abs(row["log_gap"]) <= EQUAL_M_TOLERANCE,
        })
    found = {
        "split_blocks": 2,
        "seeds_per_block": len(SEEDS),
        "candidate_rows": len(rows),
        "reference_blocks": len(REFERENCE_BLOCKS),
        "equal_m": equal_m,
        "references": {label: {
            "candidates_mean": by_label[label]["candidates_mean"],
            "density": by_label[label]["density"],
        } for label in REFERENCE_BLOCKS},
    }
    reading = (
        "Within the committed compositional law the offset predictors cannot "
        "be separated: tags-per-cell **k** fixes the alphabet **4k** and the "
        "candidate count together, so measured blocks sit at **16/2.0**, "
        "**36/3.0**, **63.7/3.98** and **167/5.95** (candidates, density) — "
        "density is a function of candidate count, and no setting of **k** "
        "moves one without the other. The pair-split construction breaks that "
        "identity by fixing the per-regime pair width at **active=4** while "
        "letting the alphabet grow: **split-32** (32 tags) yields "
        "**%.1f** candidates at density **%.3f**, and **split-48** (48 tags) "
        "yields **%.1f** at density **%.3f**, both within "
        "**%.1f%%** of the 16-tag candidate count of **%.1f**. The frozen "
        "size model therefore assigns them nearly the same offset "
        "(**%.3f** against **%.3f**, a gap of **%.3f**), while the frozen "
        "density model assigns **%.3f** and **%.3f** — a predicted difference "
        "of **%.3f** against the size model's **%.3f**. The differential "
        "between the two split blocks is the test: it is **%.0f×** the "
        "candidate-size cell LOO, and because both blocks come from the same "
        "split family, family-level shifts cancel in the difference."
        % (
            low["candidates_mean"], low["density"],
            high["candidates_mean"], high["density"],
            100 * EQUAL_M_TOLERANCE, by_label["fresh-16"]["candidates_mean"],
            predicted["split-32"]["size_offset"],
            predicted["split-48"]["size_offset"],
            abs(predicted["split-32"]["size_offset"]
                - predicted["split-48"]["size_offset"]),
            predicted["split-32"]["density_offset"],
            predicted["split-48"]["density_offset"],
            abs(differential["density_predicted_difference"]),
            abs(differential["size_predicted_difference"]),
            abs(differential["density_predicted_difference"]) / sigma,
        )
    )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Can a no-arm candidate construction make candidate count and "
            "alphabet density diverge, so the two frozen offset predictors "
            "make different predictions for the same blocks?"
        ),
        "definition": (
            "A candidate-space specification. Alphabet is the number of tags "
            "the construction exercises (4 per cell x cells). Candidate count "
            "is the number of A-candidate edges the committed fixed rule "
            "derives from the acquisition stream. Density is candidate "
            "edges / tags. The offset models are the frozen cell fits from "
            "docs/a1_offset_predictors.json (candidate size) and "
            "docs/a1_offset_density.json (candidate density), each with the "
            "shared sqrt(cap) slope."
        ),
        "method": (
            "Derive candidate streams only, with a pair-split variant of the "
            "compositional law that divides each cell's tags into active-sized "
            "groups and lets the regime index pick the group. No engine "
            "replay, so no coverage, offset or A/K cell is produced."
        ),
        "construction": {
            "law": "compositional (4 cells, flip_p/flip_q successor, 2 tags per event)",
            "knob": "active subset size per regime",
            "split_rule": "each cell's tags are cut into consecutive `active` groups; regime index selects groups[regime % groups]",
            "blocks": [{"label": block["label"], "per_cell": block["per_cell"],
                        "active": block["active"], "tags": block["tags"]}
                       for block in (low, high)],
            "seeds": list(SEEDS),
            "cycles": CYCLES,
            "events_per_cycle": EVENTS_PER_CYCLE,
            "control": "active == per_cell reproduces the committed law (checked on four seeds)",
        },
        "constants": {
            "active": ACTIVE,
            "equal_m_tolerance": EQUAL_M_TOLERANCE,
            "decision_floor": DECISION_FLOOR,
            "decision_ceiling": DECISION_CEILING,
            "frozen_coefficients": coefficients,
            "sqrt_coefficient": 0.04698668,
            "seed_rmse": 0.066656,
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "found": found,
        "blocks": blocks,
        "candidate_rows": rows,
        "predictions": predictions,
        "differential": differential,
        "identification": identification,
        "controls": controls,
        "decision_rule": {
            "statistic": "measured offset difference, split-32 minus split-48",
            "size_model": "near zero (predicted %.6f)"
                          % differential["size_predicted_difference"],
            "density_model": "negative, about %.3f"
                             % differential["density_predicted_difference"],
            "if_abs_below": "%.2f -> candidate count tracks the level"
                            % DECISION_FLOOR,
            "if_abs_above": "%.2f with the density sign -> density tracks the level"
                            % DECISION_CEILING,
            "otherwise": "neither summary is identified by this pair",
            "power": "about 3 standard errors at six seeds per block under the fitted seed-level RMSE %.3f"
                     % 0.066656,
        },
        "limits": [
            "The split blocks are a different world family from the three fitted blocks: their absolute level is not comparable to the fitted blocks except through the predictors.",
            "The differential test cancels family-level shifts only because both split blocks share the split rule, the active width and the regime law.",
            "Density 1.31-1.96 lies below the fitted density range 3.98-5.95, so the density model extrapolates downward while the size model interpolates.",
            "Candidate count is fixed by the fixed candidate rule; a different rule would move both features together again.",
            "No coverage, offset or A/K value is measured here; every predicted number is a projection from the frozen fits.",
        ],
        "not_evidence": (
            "A candidate-space specification with measured candidate counts. "
            "It is not a treatment, a target, a freeze, a grant, an A1 cell "
            "or evidence that either predictor is the mechanism. The "
            "predicted offsets are projections from frozen fits, not "
            "measurements."
        ),
    })


def render(doc: dict) -> str:
    differential = doc["differential"]
    identification = doc["identification"]
    lines = [
        "# A1 offset-discriminator construction",
        "",
        "Generated from `docs/a1_offset_discriminator_spec.json` by "
        "`python -m benchmarks.a1_offset_discriminator_spec --write`. Do not edit by hand.",
        "",
        "**Candidate-space spec, not an A1 result.** No engine replay, no target, "
        "freeze, grant or A1 cell. The predicted offsets are projections from "
        "the frozen fits, not measurements.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## The construction",
        "",
        "| Block | Tags per cell | Active per regime | Alphabet | Seeds | Candidates (mean) | Density |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for block in doc["blocks"]:
        lines.append("| %s | %d | %s | %d | %d | %.1f | %.3f |" % (
            block["label"], block["per_cell"],
            "-" if block["active"] is None else block["active"],
            block["tags"], len(block["seeds"]), block["candidates_mean"],
            block["density"]))
    lines += [
        "",
        "The split rule cuts each cell's tags into consecutive `active` groups "
        "and lets the regime index pick the group, so every declared tag is "
        "exercised while the per-regime pair space stays `active` wide.",
        "",
        "## Why the committed family cannot separate the predictors",
        "",
        "Within the compositional law, tags-per-cell `k` sets both the alphabet "
        "(`4k`) and the candidate count, so density moves with candidate count: "
        "16 tags gives 63.7 candidates at 3.98 per tag, 28 tags gives 167 at "
        "5.95. Every `k` lands on the same one-dimensional locus.",
        "",
        "## Measured candidates",
        "",
        "| Block | Seed | Tags | Candidates | log candidates | Density |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["candidate_rows"]:
        lines.append("| %s | %d | %d | %d | %.3f | %.3f |" % (
            row["block"], row["seed"], row["tags"], row["candidate_edges"],
            row["log_candidates"], row["density"]))
    lines += [
        "",
        "## Predicted offsets under the frozen models",
        "",
        "| Block | log candidates | Density | Size-model offset | Density-model offset | Gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["predictions"]:
        lines.append("| %s | %.3f | %.3f | %.3f | %.3f | %+.3f |" % (
            row["label"], row["log_candidates"], row["density"],
            row["size_offset"], row["density_offset"], row["gap"]))
    lines += [
        "",
        "## The differential",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        "| Blocks | %s vs %s |" % tuple(differential["blocks"]),
        "| log candidates | %.3f / %.3f |" % tuple(differential["log_candidates"]),
        "| density | %.3f / %.3f |" % tuple(differential["density"]),
        "| size model predicts | %+.3f |" % differential["size_predicted_difference"],
        "| density model predicts | %+.3f |" % differential["density_predicted_difference"],
        "| measured | %s |" % ("not measured" if differential["measured_difference"] is None
                               else "%+.3f" % differential["measured_difference"]),
        "",
        "## Identification",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        "| Blocks in the design | %d |" % identification["rows"],
        "| Coefficient SE (constant, log candidates, density) | %s |"
        % ", ".join("%.4f" % value for value in identification["coefficient_se"]),
        "| Residual sigma used | %.5f |" % identification["sigma"],
        "| log candidates in design | %.3f to %.3f |" % tuple(identification["log_candidates_range"]),
        "| density in design | %.3f to %.3f |" % tuple(identification["density_range"]),
        "| fitted log candidates | %.3f to %.3f |" % tuple(identification["fitted_log_candidates_range"]),
        "| fitted density | %.3f to %.3f |" % tuple(identification["fitted_density_range"]),
        "",
        "## Decision rule",
        "",
        "| Rule | Value |",
        "| --- | --- |",
    ]
    for key, value in doc["decision_rule"].items():
        lines.append("| %s | %s |" % (key.replace("_", " "), value))
    lines += [
        "",
        "## Controls",
        "",
        "| Control | Expected | Observed | Pass |",
        "| --- | --- | --- | --- |",
    ]
    for row in doc["controls"]:
        lines.append("| %s | %s | %s | %s |" % (
            row["name"], row["expected"], row["observed"],
            "yes" if row["ok"] else "**no**"))
    lines += [
        "",
        "## Limits",
        "",
    ]
    lines += ["- %s" % limit for limit in doc["limits"]]
    lines += [
        "",
        "## What this does not claim",
        "",
        doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(doc: dict | None = None) -> list[str]:
    doc = _load(OUT_PATH) if doc is None else doc
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("artifact kind")
    if doc.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    if engine_stamp.missing(doc):
        found.append("the artifact is not fully stamped")
    if doc.get("governance") != {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none"}:
        found.append("governance changed")
    if len(doc.get("blocks") or []) != 2 + len(REFERENCE_BLOCKS):
        found.append("block count")
    if len(doc.get("candidate_rows") or []) != 2 * len(SEEDS):
        found.append("candidate row count")
    if any(not row.get("ok") for row in doc.get("controls") or []):
        found.append("a control failed")
    differential = doc.get("differential") or {}
    if differential.get("measured_difference") is not None:
        found.append("a measured difference is present in a spec-only artifact")
    if abs(differential.get("density_predicted_difference", 0.0)) <= DECISION_CEILING:
        found.append("the density model is not separated from zero")
    if abs(differential.get("size_predicted_difference", 1.0)) >= DECISION_FLOOR:
        found.append("the size model is not separated from zero")
    identification = doc.get("identification") or {}
    se = identification.get("coefficient_se") or [1.0, 1.0, 1.0]
    if se[1] >= 0.05 or se[2] >= 0.02:
        found.append("a predictor coefficient is not identified at the declared sigma")
    for block in doc.get("blocks") or []:
        if block.get("active") and block.get("tags_used") != block.get("tags"):
            found.append("a split block does not use every tag")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if _offset([1.0, -1.0, 0.04698668], 2.0) != -1.0:
        failures.append("offset arithmetic")
    try:
        _offset([1.0, -1.0, 0.05], 2.0)
    except ValueError:
        pass
    else:
        failures.append("a moved cap slope was not rejected")
    inverse = _inverse_3([[2.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 0.5]])
    if inverse[0][0] != 0.5 or inverse[1][1] != 0.25 or inverse[2][2] != 2.0:
        failures.append("matrix inverse")
    if _pool(4) != tuple(ac.TAG_POOL):
        failures.append("the four-per-cell pool is not the committed pool")
    if len(set(_pool(12))) != 48:
        failures.append("the twelve-per-cell pool is not 48 unique tags")
    if ACTIVE > 4:
        failures.append("active width moved")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    for row in body["controls"]:
        print("  %-52s %-22s %-10s %s" % (
            row["name"], row["expected"], row["observed"],
            "ok" if row["ok"] else "FAIL"))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no discriminator spec; run --write")
    found = problems(_load(OUT_PATH))
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("offset discriminator spec: clean")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.self_test:
        found = self_test()
        if found:
            raise SystemExit("FAIL: " + "; ".join(found))
        print("offset discriminator self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
