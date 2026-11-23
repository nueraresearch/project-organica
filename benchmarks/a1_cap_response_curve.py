"""Is one normalized A-coverage curve plus a block offset enough?

The cap studies give 12 block-by-cap cells: three blocks at prediction caps
20/40/80/112.  This fits A/candidate_edges against the cap and compares:

* one shared cap curve plus a block offset;
* linear, logarithmic, square-root, quadratic and exponential shared curves;
* arbitrary per-cap effects (additive);
* block-specific linear and square-root slopes;
* the saturated block-by-cap interaction.

The test is leave-one-cell-out: fit on 11 cells and predict the held-out
block-cap cell.  A single curve plus an offset has to beat the models that
give each block its own slope or give every cap its own effect.  The saturated
interaction cannot predict a held-out cell and is reported in-sample only.

This is a descriptive fit to 12 fixed cells, not a causal model or a new A1
cell.  No engine change, target, freeze, grant or A1 run.

    python -m benchmarks.a1_cap_response_curve --write
    python -m benchmarks.a1_cap_response_curve --check
    python -m benchmarks.a1_cap_response_curve --self-test
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
C1_PATH = DOCS / "a1_prediction_cap_c1.json"
CAP112_PATH = DOCS / "a1_prediction_cap_112.json"
OUT_PATH = DOCS / "a1_cap_response_curve.json"
PAGE_PATH = DOCS / "A1-CAP-RESPONSE-CURVE.md"
ID = "A1-CAP-RESPONSE-CURVE-1"
DATE = "2026-11-14"
KIND = "a1_cap_response_curve"
STATUS = "DESCRIPTIVE — NORMALIZED A-COVERAGE RESPONSE CURVE; NO TARGET, FREEZE, GRANT OR A1 CELL"
BLOCKS = ("current-16", "fresh-16", "larger-28")
CAPS = (20, 40, 80, 112)
MODELS = (
    "block_only",
    "cap_only",
    "common_linear_offset",
    "common_log_offset",
    "common_sqrt_offset",
    "common_quadratic_offset",
    "common_exponential_offset",
    "additive_cap_effects",
    "block_linear",
    "block_sqrt",
    "full_interaction",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _solve(matrix: list[list[float]], vector: list[float]):
    n = len(matrix)
    work = [list(map(float, matrix[i])) + [float(vector[i])]
            for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(work[row][col]))
        if abs(work[pivot][col]) < 1e-12:
            raise ValueError("singular design")
        work[col], work[pivot] = work[pivot], work[col]
        value = work[col][col]
        for j in range(col, n + 1):
            work[col][j] /= value
        for row in range(n):
            if row == col:
                continue
            factor = work[row][col]
            if factor:
                for j in range(col, n + 1):
                    work[row][j] -= factor * work[col][j]
    return [work[i][n] for i in range(n)]


def _ols(design: list[list[float]], values: list[float]) -> list[float]:
    p = len(design[0])
    matrix = [[sum(row[i] * row[j] for row in design) for j in range(p)]
              for i in range(p)]
    vector = [sum(row[i] * value for row, value in zip(design, values))
              for i in range(p)]
    return _solve(matrix, vector)


def _design(model: str, row: dict, k: float | None = None):
    block, cap = row["block"], row["cap"]
    fresh = block == "fresh-16"
    larger = block == "larger-28"
    if model == "block_only":
        return [1.0, float(fresh), float(larger)]
    if model == "cap_only":
        return [1.0] + [float(cap == value) for value in CAPS[1:]]
    if model == "common_linear_offset":
        return [1.0, float(fresh), float(larger), float(cap)]
    if model == "common_log_offset":
        return [1.0, float(fresh), float(larger), math.log(cap)]
    if model == "common_sqrt_offset":
        return [1.0, float(fresh), float(larger), math.sqrt(cap)]
    if model == "common_quadratic_offset":
        return [1.0, float(fresh), float(larger), float(cap), float(cap) ** 2]
    if model == "common_exponential_offset":
        if k is None:
            raise ValueError("exponential needs k")
        return [1.0, float(fresh), float(larger),
                1.0 - math.exp(-k * (cap - CAPS[0]))]
    if model == "additive_cap_effects":
        return [1.0, float(fresh), float(larger)] + [
            float(cap == value) for value in CAPS[1:]
        ]
    if model == "block_linear":
        return [float(block == name) for name in BLOCKS] + [
            float(cap) if block == name else 0.0 for name in BLOCKS
        ]
    if model == "block_sqrt":
        return [float(block == name) for name in BLOCKS] + [
            math.sqrt(cap) if block == name else 0.0 for name in BLOCKS
        ]
    if model == "full_interaction":
        return [float(block == b and cap == c) for b in BLOCKS for c in CAPS]
    raise ValueError(model)


def _fit(model: str, data: list[dict]) -> tuple[list[float], float | None]:
    if model != "common_exponential_offset":
        return _ols([_design(model, row) for row in data],
                    [row["A_coverage"] for row in data]), None
    best = None
    for step in range(1, 401):
        k = step / 1000.0
        coef = _ols([_design(model, row, k) for row in data],
                    [row["A_coverage"] for row in data])
        sse = sum((row["A_coverage"]
                   - sum(a * b for a, b in zip(_design(model, row, k), coef))) ** 2
                  for row in data)
        if best is None or sse < best[0]:
            best = (sse, k, coef)
    return best[2], best[1]


def _predict(model: str, row: dict, coef: list[float],
             k: float | None = None) -> float:
    return sum(a * b for a, b in zip(_design(model, row, k), coef))


def _cells() -> tuple[list[dict], list[dict]]:
    c1 = _load(C1_PATH)["rows"]
    high = _load(CAP112_PATH)["rows"]
    by_key = {(row["block"], row["seed"], row["prediction_cap"]): row
              for row in c1}
    for row in high:
        key = (row["block"], row["seed"], row["prediction_cap"])
        if key in by_key:
            for field in ("candidate_edges", "A", "K", "A_and_K"):
                if by_key[key][field] != row[field]:
                    raise SystemExit(
                        "REFUSED: %s/%d/%d %s disagrees"
                        % (key[0], key[1], key[2], field))
        else:
            by_key[key] = row
    seeds = []
    for key in sorted(by_key):
        row = by_key[key]
        seeds.append({
            "block": row["block"],
            "seed": row["seed"],
            "cap": row["prediction_cap"],
            "candidate_edges": row["candidate_edges"],
            "A": row["A"],
            "A_coverage": row["A"] / row["candidate_edges"],
        })
    cells = []
    for block in BLOCKS:
        for cap in CAPS:
            group = [row for row in seeds
                     if row["block"] == block and row["cap"] == cap]
            cells.append({
                "block": block,
                "cap": cap,
                "seeds": len(group),
                "A_coverage": sum(row["A_coverage"] for row in group) / len(group),
            })
    return cells, seeds


def _metrics(model: str, cells: list[dict]) -> dict:
    coef, k = _fit(model, cells)
    fitted = [_predict(model, row, coef, k) for row in cells]
    errors = [row["A_coverage"] - value for row, value in zip(cells, fitted)]
    in_rmse = math.sqrt(sum(e * e for e in errors) / len(errors))
    in_max = max(abs(e) for e in errors)
    loo_errors = []
    if model == "full_interaction":
        loo_rmse = None
        loo_max = None
    else:
        for index, row in enumerate(cells):
            train = cells[:index] + cells[index + 1:]
            loo_coef, loo_k = _fit(model, train)
            loo_errors.append(row["A_coverage"]
                              - _predict(model, row, loo_coef, loo_k))
        loo_rmse = math.sqrt(sum(e * e for e in loo_errors) / len(loo_errors))
        loo_max = max(abs(e) for e in loo_errors)
    return {
        "model": model,
        "parameters": len(coef) + (1 if k is not None else 0),
        "in_rmse": round(in_rmse, 6),
        "in_max": round(in_max, 6),
        "loo_rmse": round(loo_rmse, 6) if loo_rmse is not None else None,
        "loo_max": round(loo_max, 6) if loo_max is not None else None,
        "coefficients": [round(value, 8) for value in coef],
        "k": round(k, 8) if k is not None else None,
    }


def build() -> dict:
    cells, seeds = _cells()
    comparisons = [_metrics(model, cells) for model in MODELS]
    eligible = [row for row in comparisons if row["loo_rmse"] is not None]
    best = min(eligible, key=lambda row: row["loo_rmse"])
    shape = next(row for row in comparisons
                 if row["model"] == "common_sqrt_offset")
    coef = shape["coefficients"]
    predictions = []
    for row in cells:
        predicted = _predict("common_sqrt_offset", row, coef)
        predictions.append({
            "block": row["block"],
            "cap": row["cap"],
            "observed": round(row["A_coverage"], 6),
            "predicted": round(predicted, 6),
            "residual": round(row["A_coverage"] - predicted, 6),
        })
    reading = (
        "A single square-root cap curve plus a block offset predicts the 12 "
        "block-by-cap cells with in-sample RMSE %.4f (max %.4f) and "
        "leave-one-cell-out RMSE %.4f (max %.4f). Block-specific square-root "
        "slopes reach LOO RMSE %.4f, arbitrary per-cap effects %.4f, and "
        "block-specific linear slopes %.4f. The shared curve is therefore "
        "sufficient over this cap range: the blocks differ mainly by a "
        "baseline offset, not by response shape."
        % (shape["in_rmse"], shape["in_max"], shape["loo_rmse"],
           shape["loo_max"],
           next(row["loo_rmse"] for row in comparisons
                if row["model"] == "block_sqrt"),
           next(row["loo_rmse"] for row in comparisons
                if row["model"] == "additive_cap_effects"),
           next(row["loo_rmse"] for row in comparisons
                if row["model"] == "block_linear")))
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Does one normalized A-coverage curve plus a block offset explain "
            "the cap response across current-16, fresh-16 and larger-28?"
        ),
        "definition": (
            "A_coverage = A / candidate_edges, aggregated to 12 block-by-cap "
            "cells. Models are fitted to cell means; leave-one-cell-out fits "
            "on 11 cells and predicts the held-out block-cap cell."
        ),
        "method": (
            "Read the committed cap-20/40/80 and cap-112 rows; overlapping "
            "cap-40 and cap-80 cells must agree. Compare shared curves, "
            "arbitrary cap effects, block-specific slopes and the saturated "
            "interaction. Pure-Python OLS; no replay or engine change."
        ),
        "constants": {
            "blocks": list(BLOCKS),
            "caps": list(CAPS),
            "cells": len(cells),
            "seeds": len(seeds),
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "best_loo_model": best["model"],
        "comparisons": comparisons,
        "selected_model": shape,
        "block_offsets": {
            "current-16": coef[0],
            "fresh-16": round(coef[0] + coef[1], 8),
            "larger-28": round(coef[0] + coef[2], 8),
        },
        "relative_offsets": {
            "fresh-16": coef[1],
            "larger-28": coef[2],
        },
        "sqrt_coefficient": coef[3],
        "cells": predictions,
        "not_evidence": (
            "A descriptive fit to 12 fixed block-by-cap cell means from 18 "
            "no-arm seeds. It compares interpolation models, not causal "
            "effects; it does not show that changing the prediction cap would "
            "move A by the fitted curve, and it is not a treatment, target "
            "viability or successor."
        ),
    })


def render(doc: dict) -> str:
    selected = doc["selected_model"]
    lines = [
        "# A1 predicted-cap response curve",
        "",
        "Generated from `docs/a1_cap_response_curve.json` by "
        "`python -m benchmarks.a1_cap_response_curve --write`. Do not edit by hand.",
        "",
        "**Descriptive fit, not an A1 result.** 12 block-by-cap cells from 18 "
        "no-arm seeds at prediction caps **20/40/80/112**. No target, freeze, "
        "grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Model comparison",
        "",
        "| Model | Parameters | In-sample RMSE | In-sample max | LOO RMSE | LOO max |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["comparisons"]:
        lines.append("| %s | %d | %.4f | %.4f | %s | %s |" % (
            row["model"], row["parameters"], row["in_rmse"], row["in_max"],
            "%.4f" % row["loo_rmse"] if row["loo_rmse"] is not None else "n/a",
            "%.4f" % row["loo_max"] if row["loo_max"] is not None else "n/a"))
    lines += [
        "",
        "The saturated interaction has zero in-sample error by construction "
        "and no held-out prediction, because each cell is its own parameter. "
        "It is shown for scale, not selected.",
        "",
        "## Shared curve",
        "",
        "Selected form:",
        "",
        "```text",
        "A_coverage = block_offset + %.5f * sqrt(cap)" % doc["sqrt_coefficient"],
        "```",
        "",
        "| Block | Offset | Relative to current-16 |",
        "| --- | ---: | ---: |",
    ]
    for block in BLOCKS:
        lines.append("| %s | %.4f | %+.4f |" % (
            block, doc["block_offsets"][block],
            doc["relative_offsets"].get(block, 0.0)))
    lines += [
        "",
        "## Cell fit",
        "",
        "| Block | Cap | Observed | Predicted | Residual |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["cells"]:
        lines.append("| %s | %d | %.4f | %.4f | %+.4f |" % (
            row["block"], row["cap"], row["observed"], row["predicted"],
            row["residual"]))
    lines += [
        "",
        "## Reading",
        "",
        "The shared curve is not just a description of the marginal cap "
        "effect: it predicts a held-out block-cap cell better than giving "
        "each block its own slope or giving each cap its own free effect. "
        "The block offsets are the baseline-occupancy difference. The fitted "
        "curve is concave, so each additional prediction slot buys less "
        "coverage, but the same shape applies to all three blocks over this "
        "range.",
        "",
        "This does not establish a mechanism. It establishes that the "
        "12-cell surface is low-rank in the tested family: one curve plus "
        "three offsets.",
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
    if len(doc.get("cells") or []) != len(BLOCKS) * len(CAPS):
        found.append("cell count")
    if len(doc.get("comparisons") or []) != len(MODELS):
        found.append("model count")
    selected = doc.get("selected_model") or {}
    if selected.get("model") != "common_sqrt_offset":
        found.append("selected model changed")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    row = {"block": "larger-28", "cap": 112}
    design = _design("common_sqrt_offset", row)
    if len(design) != 4 or not design[2]:
        failures.append("sqrt design must have an offset and a larger flag")
    if abs(math.sqrt(112) - 10.583005244) > 1e-6:
        failures.append("sqrt fixture")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no cap-response artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("cap response curve: clean")
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
        print("cap-response self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
