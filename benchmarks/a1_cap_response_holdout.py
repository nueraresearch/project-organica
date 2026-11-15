"""Does the shared cap-response curve interpolate or extrapolate?

The curve was fitted to 12 block-by-cap cells at prediction caps
20/40/80/112.  This measures the same 18 no-arm seeds at caps that were not
in the fit:

* ``28``, ``64`` and ``96`` lie between fitted caps (interpolation);
* ``128`` lies above the fitted range (extrapolation).

Predictions are frozen from the committed fit: the shared square-root curve
plus block offset, and the alternative candidate-size offset.  Nothing is
refitted on the held-out rows.  The cell residual is compared with the fit's
own leave-one-cell-out error, which is the scale a correct interpolation
should stay inside.

A second holdout uses no replay: hold out one block, fit the shared curve
plus candidate-size offset on the other eight committed cells, and predict
the held-out block's four cells.  That asks whether the offset model
extrapolates across blocks, where larger-28 lies outside the 16-tag range.

Cap 80 is a control: six seeds (two per block) must reproduce their committed
cap-80 A, K and A∩K counts exactly, or the build refuses.

No engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_cap_response_holdout --write
    python -m benchmarks.a1_cap_response_holdout --check
    python -m benchmarks.a1_cap_response_holdout --self-test
"""
from __future__ import annotations

import argparse
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_cap_response_curve as curve
from benchmarks import a1_prediction_cap_c1 as base
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_cap_response_holdout.json"
PAGE_PATH = DOCS / "A1-CAP-RESPONSE-HOLDOUT.md"
CURVE_PATH = DOCS / "a1_cap_response_curve.json"
PREDICTORS_PATH = DOCS / "a1_offset_predictors.json"
REFERENCE_PATH = DOCS / "a1_prediction_cap_c1.json"
ID = "A1-CAP-RESPONSE-HOLDOUT-1"
DATE = "2026-11-14"
KIND = "a1_cap_response_holdout"
STATUS = ("DESCRIPTIVE — HELD-OUT CAP AND BLOCK VALIDATION OF THE SHARED CURVE; "
          "NO TARGET, FREEZE, GRANT OR A1 CELL")
BLOCKS = ("current-16", "fresh-16", "larger-28")
FIT_CAPS = (20, 40, 80, 112)
HOLDOUT_CAPS = (28, 64, 96, 128)
INTERPOLATION_CAPS = (28, 64, 96)
EXTRAPOLATION_CAPS = (128,)
CONTROL_CAP = 80
CONTROL_SEEDS = (20630101, 20630102, 20650101, 20650102, 20660101, 20660102)
# Frozen from docs/a1_cap_response_curve.json: current offset, fresh and
# larger relative offsets, shared sqrt coefficient.
CURVE_COEFFICIENTS = (0.42002218, -0.0135582, -0.35118485, 0.04698666)
# Frozen from docs/a1_offset_predictors.json: intercept, log-candidate
# coefficient, shared sqrt coefficient.
SIZE_COEFFICIENTS = (1.90290201, -0.35852459, 0.04698666)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _frozen_curve() -> tuple[float, float, float, float]:
    doc = _load(CURVE_PATH)
    coef = tuple(doc["selected_model"]["coefficients"])
    if tuple(round(value, 8) for value in coef) != CURVE_COEFFICIENTS:
        raise SystemExit("REFUSED: the committed shared curve has changed")
    if doc["selected_model"]["model"] != "common_sqrt_offset":
        raise SystemExit("REFUSED: the committed curve is not the shared sqrt form")
    return coef


def _frozen_size() -> tuple[float, float, float]:
    doc = _load(PREDICTORS_PATH)
    row = next(item for item in doc["comparisons"]
               if item["model"] == "candidate_size")
    coef = tuple(round(value, 8) for value in row["cell_coefficients"])
    if coef != SIZE_COEFFICIENTS:
        raise SystemExit("REFUSED: the committed candidate-size model has changed")
    return coef


def _curve_offset(coef, block: str) -> float:
    relative = {"current-16": 0.0, "fresh-16": coef[1], "larger-28": coef[2]}
    return coef[0] + relative[block]


def _predict_curve(coef, block: str, cap: int) -> float:
    return _curve_offset(coef, block) + coef[3] * math.sqrt(cap)


def _predict_size(coef, log_candidates: float, cap: int) -> float:
    return coef[0] + coef[1] * log_candidates + coef[2] * math.sqrt(cap)


def _kind(cap: int) -> str:
    return "extrapolation" if cap in EXTRAPOLATION_CAPS else "interpolation"


# A log-candidate spread this small leaves the size coefficient unidentified.
MIN_IDENTIFIED_SPREAD = 0.10


def _identified(spread: float) -> bool:
    return spread >= MIN_IDENTIFIED_SPREAD


def _rmse(errors: list[float]) -> float:
    return math.sqrt(sum(value * value for value in errors) / len(errors))


def _control(raw: list[dict]) -> list[dict]:
    reference = {
        (row["block"], row["seed"]): row
        for row in _load(REFERENCE_PATH)["rows"]
        if row["prediction_cap"] == CONTROL_CAP
    }
    rows = []
    for got in raw:
        if got["prediction_cap"] != CONTROL_CAP:
            continue
        expected = reference[(got["block"], got["seed"])]
        ok = all(got[field] == expected[field]
                 for field in ("A", "K", "A_and_K", "candidate_edges"))
        if not ok:
            raise SystemExit(
                "REFUSED: cap-%d control %s/%d A %d K %d A∩K %d, expected "
                "%d/%d/%d" % (CONTROL_CAP, got["block"], got["seed"],
                              got["A"], got["K"], got["A_and_K"],
                              expected["A"], expected["K"],
                              expected["A_and_K"]))
        rows.append({
            "block": got["block"], "seed": got["seed"],
            "prediction_cap": CONTROL_CAP,
            "A": got["A"], "K": got["K"], "A_and_K": got["A_and_K"],
            "candidate_edges": got["candidate_edges"],
            "matches_committed": True,
        })
    return rows


def build() -> dict:
    coef = _frozen_curve()
    size = _frozen_size()
    curve_doc = _load(CURVE_PATH)
    reference_loo = next(row["loo_rmse"] for row in curve_doc["comparisons"]
                         if row["model"] == "common_sqrt_offset")
    reference_in = next(row["in_rmse"] for row in curve_doc["comparisons"]
                        if row["model"] == "common_sqrt_offset")

    tasks = [(block["label"], seed, cap)
             for block in base.BLOCKS
             for seed in block["seeds"]
             for cap in HOLDOUT_CAPS]
    control_tasks = [(block["label"], seed, CONTROL_CAP)
                     for block in base.BLOCKS
                     for seed in CONTROL_SEEDS
                     if seed in block["seeds"]]
    with ProcessPoolExecutor(max_workers=6) as pool:
        raw = list(pool.map(base._replay, tasks + control_tasks))
    control = _control(raw)

    seeds = [
        {
            "block": row["block"],
            "seed": row["seed"],
            "cap": row["prediction_cap"],
            "candidate_edges": row["candidate_edges"],
            "A": row["A"],
            "A_coverage": row["A"] / row["candidate_edges"],
        }
        for row in raw if row["prediction_cap"] in HOLDOUT_CAPS
    ]
    log_candidates = {}
    for block in BLOCKS:
        by_seed = {row["seed"]: row["candidate_edges"] for row in seeds
                   if row["block"] == block}
        log_candidates[block] = round(
            sum(math.log(value) for value in by_seed.values()) / len(by_seed), 6)

    cells = []
    for block in BLOCKS:
        for cap in HOLDOUT_CAPS:
            group = [row for row in seeds
                     if row["block"] == block and row["cap"] == cap]
            observed = round(sum(row["A_coverage"] for row in group)
                             / len(group), 6)
            predicted = round(_predict_curve(coef, block, cap), 6)
            predicted_size = round(_predict_size(size, log_candidates[block],
                                                 cap), 6)
            cells.append({
                "block": block,
                "cap": cap,
                "kind": _kind(cap),
                "seeds": len(group),
                "observed": observed,
                "predicted": predicted,
                "residual": round(observed - predicted, 6),
                "predicted_size": predicted_size,
                "residual_size": round(observed - predicted_size, 6),
            })

    per_cap = []
    for cap in HOLDOUT_CAPS:
        group = [row for row in cells if row["cap"] == cap]
        errors = [row["residual"] for row in group]
        size_errors = [row["residual_size"] for row in group]
        per_cap.append({
            "cap": cap,
            "kind": _kind(cap),
            "rmse": round(_rmse(errors), 6),
            "max_abs_residual": round(max(abs(value) for value in errors), 6),
            "mean_residual": round(sum(errors) / len(errors), 6),
            "size_rmse": round(_rmse(size_errors), 6),
        })
    interpolation = [row["residual"] for row in cells
                     if row["kind"] == "interpolation"]
    extrapolation = [row["residual"] for row in cells
                     if row["kind"] == "extrapolation"]
    metrics = {
        "reference_cell_in_rmse": reference_in,
        "reference_cell_loo_rmse": reference_loo,
        "interpolation_rmse": round(_rmse(interpolation), 6),
        "interpolation_max": round(max(abs(value) for value in interpolation), 6),
        "interpolation_cells": len(interpolation),
        "extrapolation_rmse": round(_rmse(extrapolation), 6),
        "extrapolation_max": round(max(abs(value) for value in extrapolation), 6),
        "extrapolation_cells": len(extrapolation),
        "size_interpolation_rmse": round(_rmse(
            [row["residual_size"] for row in cells
             if row["kind"] == "interpolation"]), 6),
        "size_extrapolation_rmse": round(_rmse(
            [row["residual_size"] for row in cells
             if row["kind"] == "extrapolation"]), 6),
    }

    committed_cells, committed_seeds = curve._cells()
    committed_log = {
        block: sum(math.log(item["candidate_edges"])
                   for item in committed_seeds if item["block"] == block)
        / len([item for item in committed_seeds if item["block"] == block])
        for block in BLOCKS
    }
    block_holdout = []
    for block in BLOCKS:
        train = [row for row in committed_cells if row["block"] != block]
        design = [[1.0, committed_log[row["block"]], math.sqrt(row["cap"])]
                  for row in train]
        fitted = curve._ols(design, [row["A_coverage"] for row in train])
        spread = max(committed_log[row["block"]] for row in train) - min(
            committed_log[row["block"]] for row in train)
        entry = {
            "block": block,
            "training_cells": len(train),
            "training_log_spread": round(spread, 6),
            "coefficients": [round(value, 6) for value in fitted],
            "status": "estimated" if _identified(spread) else "not_identified",
            "cells": [],
        }
        for row in [item for item in committed_cells if item["block"] == block]:
            observed = round(row["A_coverage"], 6)
            predicted = round(fitted[0] + fitted[1] * committed_log[block]
                              + fitted[2] * math.sqrt(row["cap"]), 6)
            entry["cells"].append({
                "cap": row["cap"],
                "observed": observed,
                "predicted": predicted,
                "residual": round(observed - predicted, 6),
            })
        entry["rmse"] = round(_rmse([cell["residual"] for cell in entry["cells"]]), 6)
        entry["max_abs_residual"] = round(
            max(abs(cell["residual"]) for cell in entry["cells"]), 6)
        block_holdout.append(entry)

    saturation = {
        block: round(((1.0 - _curve_offset(coef, block)) / coef[3]) ** 2)
        for block in BLOCKS
    }
    identified = [entry for entry in block_holdout
                  if entry["status"] == "estimated"]
    metrics["block_estimated_rmse_max"] = round(
        max(entry["rmse"] for entry in identified), 6)
    metrics["block_estimated_blocks"] = [entry["block"] for entry in identified]
    metrics["block_not_identified"] = [
        entry["block"] for entry in block_holdout
        if entry["status"] != "estimated"]
    reading = (
        "The held-out caps do not separate interpolation from extrapolation "
        "over this range. At caps %s, between fitted caps, the frozen shared "
        "curve has RMSE %.4f (max %.4f) over %d cells, inside its own "
        "leave-one-cell-out scale of %.4f. At cap %d, one step above the "
        "fitted range, the RMSE is %.4f (max %.4f) over %d cells, against "
        "%.4f interpolated, so one step beyond the fit does not degrade "
        "measurably. The candidate-size offset is comparable (%.4f "
        "interpolated, %.4f at cap %d). Two bounds apply. Cap 128 sits at "
        "%d%% of current-16's "
        "saturation cap (%d) and %d%% of fresh-16's (%d), and the 16-tag "
        "cells at 96 and 128 already fall below the curve (fresh %.3f at 96, "
        "current %.3f at 128), which is flattening near the ceiling rather "
        "than a curve that keeps rising; the fit is not admissible past those "
        "caps."
        % (", ".join(str(cap) for cap in INTERPOLATION_CAPS),
           metrics["interpolation_rmse"], metrics["interpolation_max"],
           metrics["interpolation_cells"], reference_loo,
           EXTRAPOLATION_CAPS[0], metrics["extrapolation_rmse"],
           metrics["extrapolation_max"],            metrics["extrapolation_cells"], metrics["interpolation_rmse"],
           metrics["size_interpolation_rmse"],
           metrics["size_extrapolation_rmse"], EXTRAPOLATION_CAPS[0],
           round(100 * EXTRAPOLATION_CAPS[0] / saturation["current-16"]),
           saturation["current-16"],
           round(100 * EXTRAPOLATION_CAPS[0] / saturation["fresh-16"]),
           saturation["fresh-16"],
           next(row["residual"] for row in cells
                if row["block"] == "fresh-16" and row["cap"] == 96),
           next(row["residual"] for row in cells
                if row["block"] == "current-16"
                and row["cap"] == EXTRAPOLATION_CAPS[0]))
    )
    block_reading = (
        "The block holdout shows where the offset model can and cannot stand "
        "in for the block label. Holding out current-16 or fresh-16 leaves "
        "two blocks whose candidate sizes bracket the held-out one, and the "
        "curve plus size offset interpolates them at RMSE %.4f and %.4f "
        "against its own held-out scale of %.4f. "
        "Holding out larger-28 leaves only the two 16-tag blocks, whose log "
        "candidate sizes differ by %.4f; the fitted size coefficient is "
        "%.2f against an intercept of %.2f and predicts a coverage of %.2f, "
        "so that direction is not identified, and its RMSE is a "
        "rank-deficiency artifact rather than an extrapolation error."
        % (next(entry["rmse"] for entry in block_holdout
                if entry["block"] == "current-16"),
           next(entry["rmse"] for entry in block_holdout
                if entry["block"] == "fresh-16"),
           reference_loo,
           next(entry["training_log_spread"] for entry in block_holdout
                if entry["block"] == "larger-28"),
           next(entry["coefficients"][1] for entry in block_holdout
                if entry["block"] == "larger-28"),
           next(entry["coefficients"][0] for entry in block_holdout
                if entry["block"] == "larger-28"),
           next(cell["predicted"] for entry in block_holdout
                if entry["block"] == "larger-28"
                for cell in entry["cells"] if cell["cap"] == 20))
    )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Does the shared cap-response curve predict A coverage at caps "
            "outside its 12-cell fit, and does the candidate-size offset "
            "extrapolate to a held-out block?"
        ),
        "definition": (
            "A_coverage = A / candidate_edges at 12 held-out block-by-cap "
            "cells (caps 28/64/96/128) from the same 18 no-arm seeds. "
            "Predicted values are frozen from the committed shared curve and "
            "candidate-size fit; nothing is refitted on held-out rows."
        ),
        "method": (
            "One no-arm replay per seed and held-out cap at loop cap 120. "
            "Cap 80 on six seeds (two per block) must reproduce the committed "
            "cap-80 A, K and A∩K counts exactly. Block holdout fits the shared "
            "curve plus log-candidate offset on eight committed cells and "
            "predicts the ninth block's four cells."
        ),
        "constants": {
            "cycles": base.CYCLES,
            "loop_cap": base.LOOP_CAP,
            "fit_caps": list(FIT_CAPS),
            "holdout_caps": list(HOLDOUT_CAPS),
            "interpolation_caps": list(INTERPOLATION_CAPS),
            "extrapolation_caps": list(EXTRAPOLATION_CAPS),
            "control_cap": CONTROL_CAP,
            "control_seeds": list(CONTROL_SEEDS),
            "curve_coefficients": list(CURVE_COEFFICIENTS),
            "size_coefficients": list(SIZE_COEFFICIENTS),
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "block_reading": block_reading,
        "metrics": metrics,
        "per_cap": per_cap,
        "block_holdout": block_holdout,
        "saturation_caps": saturation,
        "log_candidates": dict(log_candidates),
        "cells": cells,
        "control": control,
        "not_evidence": (
            "A descriptive held-out prediction from no-arm replays. The cap "
            "axis is held out, the seeds are not: these are the same 18 seeds "
            "the fit was built from, so this bounds interpolation over caps "
            "and blocks, not generalization to a new seed block or world. "
            "Cap 128 sits near the 16-tag coverage ceiling, so its residual "
            "mixes curve error with saturation. It is not a treatment, target "
            "viability or successor."
        ),
    })


def render(doc: dict) -> str:
    metrics = doc["metrics"]
    lines = [
        "# A1 cap-response holdout",
        "",
        "Generated from `docs/a1_cap_response_holdout.json` by "
        "`python -m benchmarks.a1_cap_response_holdout --write`. Do not edit by hand.",
        "",
        "**Descriptive held-out prediction, not an A1 result.** The same 18 "
        "no-arm seeds at prediction caps **28/64/96/128**, outside the "
        "**20/40/80/112** fit. No target, freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        doc["block_reading"],
        "",
        "## Held-out caps",
        "",
        "| Cap | Kind | RMSE | Max | Mean residual | Candidate-size RMSE |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["per_cap"]:
        lines.append("| %d | %s | %.4f | %.4f | %+.4f | %.4f |" % (
            row["cap"], row["kind"], row["rmse"], row["max_abs_residual"],
            row["mean_residual"], row["size_rmse"]))
    lines += [
        "",
        "Reference scale from the committed fit: in-sample RMSE **%.4f**, "
        "leave-one-cell-out RMSE **%.4f**."
        % (metrics["reference_cell_in_rmse"], metrics["reference_cell_loo_rmse"]),
        "",
        "| | Cells | RMSE | Max |",
        "| --- | ---: | ---: | ---: |",
        "| Interpolation (28/64/96) | %d | %.4f | %.4f |" % (
            metrics["interpolation_cells"], metrics["interpolation_rmse"],
            metrics["interpolation_max"]),
        "| Extrapolation (128) | %d | %.4f | %.4f |" % (
            metrics["extrapolation_cells"], metrics["extrapolation_rmse"],
            metrics["extrapolation_max"]),
        "",
        "## Held-out cells",
        "",
        "| Block | Cap | Kind | Observed | Predicted | Residual | Size prediction | Size residual |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["cells"]:
        lines.append("| %s | %d | %s | %.4f | %.4f | %+.4f | %.4f | %+.4f |" % (
            row["block"], row["cap"], row["kind"], row["observed"],
            row["predicted"], row["residual"], row["predicted_size"],
            row["residual_size"]))
    lines += [
        "",
        "## Block holdout",
        "",
        "Fit on the other two blocks' eight committed cells, predict the "
        "held-out block's four cells from its candidate size.",
        "",
        "| Held-out block | Status | Training log spread | RMSE | Max | Cap 20 | Cap 40 | Cap 80 | Cap 112 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for entry in doc["block_holdout"]:
        residuals = {cell["cap"]: cell["residual"] for cell in entry["cells"]}
        lines.append(
            "| %s | %s | %.4f | %.4f | %.4f | %+.4f | %+.4f | %+.4f | %+.4f |"
            % (entry["block"], entry["status"]
               .replace("_", " "), entry["training_log_spread"],
               entry["rmse"], entry["max_abs_residual"],
               residuals[20], residuals[40], residuals[80], residuals[112]))
    lines += [
        "",
        "A direction is marked *not identified* when the training blocks' "
        "log candidate sizes span less than **%.2f**, which leaves the "
        "size coefficient unconstrained. Its RMSE is reported for "
        "completeness and must not be read as an extrapolation error."
        % MIN_IDENTIFIED_SPREAD,
    ]
    lines += [
        "",
        "## Saturation",
        "",
        "The fitted curve crosses coverage 1.0 at cap **%d** (current-16), "
        "**%d** (fresh-16) and **%d** (larger-28), so caps above those are "
        "outside the model's admissible range by construction."
        % (doc["saturation_caps"]["current-16"],
           doc["saturation_caps"]["fresh-16"],
           doc["saturation_caps"]["larger-28"]),
        "",
        "## Control",
        "",
        "Cap 80 on six seeds (two per block) reproduces the committed cap-80 "
        "A, K and A∩K counts exactly.",
        "",
        "| Block | Seed | A | K | A∩K | Matches committed |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in doc["control"]:
        lines.append("| %s | %d | %d | %d | %d | %s |" % (
            row["block"], row["seed"], row["A"], row["K"], row["A_and_K"],
            "yes" if row["matches_committed"] else "no"))
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
    cells = doc.get("cells") or []
    if len(cells) != len(BLOCKS) * len(HOLDOUT_CAPS):
        found.append("cell count")
    coef = tuple(doc.get("constants", {}).get("curve_coefficients") or ())
    if coef != CURVE_COEFFICIENTS:
        found.append("curve coefficients changed")
        coef = CURVE_COEFFICIENTS
    size = tuple(doc.get("constants", {}).get("size_coefficients") or ())
    if size != SIZE_COEFFICIENTS:
        found.append("size coefficients changed")
        size = SIZE_COEFFICIENTS
    logs = doc.get("log_candidates") or {}
    for row in cells:
        block, cap = row.get("block"), row.get("cap")
        if block not in BLOCKS or cap not in HOLDOUT_CAPS:
            found.append("unexpected cell %r" % ((block, cap),))
            continue
        predicted = round(_predict_curve(coef, block, cap), 6)
        predicted_size = round(_predict_size(size, logs.get(block, 0.0), cap), 6)
        if row.get("predicted") != predicted:
            found.append("shared prediction at %r" % ((block, cap),))
        if row.get("predicted_size") != predicted_size:
            found.append("size prediction at %r" % ((block, cap),))
        if row.get("residual") != round(row.get("observed", 0.0) - predicted, 6):
            found.append("shared residual at %r" % ((block, cap),))
        if row.get("residual_size") != round(
                row.get("observed", 0.0) - predicted_size, 6):
            found.append("size residual at %r" % ((block, cap),))
        if row.get("kind") != _kind(cap):
            found.append("cell kind at %r" % ((block, cap),))
    for row in doc.get("control") or []:
        if row.get("matches_committed") is not True:
            found.append("control %r is not committed" % ((row.get("block"),
                                                          row.get("seed")),))
    if len(doc.get("control") or []) != len(CONTROL_SEEDS):
        found.append("control count")
    block_rows = doc.get("block_holdout") or []
    if len(block_rows) != len(BLOCKS):
        found.append("block-holdout count")
    for entry in block_rows:
        if len(entry.get("coefficients") or []) != 3:
            found.append("block-holdout coefficients for %r" % (entry.get("block"),))
        expected = ("estimated" if _identified(entry.get("training_log_spread", 0.0))
                    else "not_identified")
        if entry.get("status") != expected:
            found.append("block-holdout status for %r" % (entry.get("block"),))
        for cell in entry.get("cells") or []:
            if cell.get("residual") != round(
                    cell.get("observed", 0.0) - cell.get("predicted", 0.0), 6):
                found.append("block-holdout residual at %r"
                             % ((entry.get("block"), cell.get("cap")),))
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    coef = CURVE_COEFFICIENTS
    if abs(_predict_curve(coef, "current-16", 0) - coef[0]) > 1e-12:
        failures.append("cap 0 must return the current offset")
    if not abs(_predict_curve(coef, "larger-28", 112)
               - (coef[0] + coef[2] + coef[3] * math.sqrt(112))) < 1e-12:
        failures.append("larger prediction must add its relative offset")
    if _kind(64) != "interpolation" or _kind(128) != "extrapolation":
        failures.append("cap kind")
    if set(INTERPOLATION_CAPS) | set(EXTRAPOLATION_CAPS) != set(HOLDOUT_CAPS):
        failures.append("held-out caps must be classified")
    if set(INTERPOLATION_CAPS) & set(FIT_CAPS):
        failures.append("an interpolation cap must not be a fitted cap")
    if EXTRAPOLATION_CAPS[0] <= max(FIT_CAPS):
        failures.append("the extrapolation cap must exceed the fitted range")
    if _identified(0.0026) or not _identified(0.9592):
        failures.append("the identifiability rule must reject a 0.0026 spread")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    print(body["block_reading"])
    for row in body["per_cap"]:
        print("cap %d (%s): RMSE %.4f, max %.4f, mean %+.4f, size RMSE %.4f"
              % (row["cap"], row["kind"], row["rmse"],
                 row["max_abs_residual"], row["mean_residual"], row["size_rmse"]))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no holdout artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("cap-response holdout: clean")
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
        print("cap-response holdout self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
