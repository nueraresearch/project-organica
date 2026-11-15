"""Does candidate-space density predict the block offset, alone or with size?

The shared cap-response curve needs one offset per block.  An earlier
comparison found that ``log(candidate_edges)`` replaces those offsets with one
continuous term, and that K completeness does not add seed-level signal.  This
adds a third candidate: **candidate-space density**, the mean candidate edges
per tag in the block's alphabet.

Three blocks cannot separate monotone block summaries, so the test is run at
the cell and seed level as before, and the block-level collinearity between
density and candidate size is reported explicitly rather than hidden.  Models
compared, on 12 block-by-cap cells and 72 seed rows:

* free block offset;
* candidate size, ``log(candidate_edges)``;
* candidate density, ``candidate_edges / tags``;
* K completeness, ``K / candidate_edges``;
* size + density, size + K completeness, density + K completeness.

No engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_offset_density --write
    python -m benchmarks.a1_offset_density --check
    python -m benchmarks.a1_offset_density --self-test
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from benchmarks import a1_cap_response_curve as curve
from benchmarks import a1_offset_predictors as op
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_offset_density.json"
PAGE_PATH = DOCS / "A1-OFFSET-DENSITY.md"
ID = "A1-OFFSET-DENSITY-1"
DATE = "2026-11-14"
KIND = "a1_offset_density"
STATUS = ("DESCRIPTIVE — CANDIDATE-SPACE DENSITY AS A BLOCK-OFFSET PREDICTOR; "
          "NO TARGET, FREEZE, GRANT OR A1 CELL")
BLOCKS = ("current-16", "fresh-16", "larger-28")
CAPS = (20, 40, 80, 112)
TAGS = {"current-16": 16, "fresh-16": 16, "larger-28": 28}
MODELS = (
    "free_block_offset",
    "candidate_size",
    "candidate_density",
    "k_completeness",
    "size_plus_density",
    "size_plus_k",
    "density_plus_k",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _design(model: str, row: dict) -> list[float]:
    block, cap = row["block"], row["cap"]
    fresh = block == "fresh-16"
    larger = block == "larger-28"
    if model == "free_block_offset":
        return [1.0, float(fresh), float(larger), math.sqrt(cap)]
    if model == "candidate_size":
        return [1.0, row["log_candidates"], math.sqrt(cap)]
    if model == "candidate_density":
        return [1.0, row["density"], math.sqrt(cap)]
    if model == "k_completeness":
        return [1.0, row["k_completeness"], math.sqrt(cap)]
    if model == "size_plus_density":
        return [1.0, row["log_candidates"], row["density"], math.sqrt(cap)]
    if model == "size_plus_k":
        return [1.0, row["log_candidates"], row["k_completeness"],
                math.sqrt(cap)]
    if model == "density_plus_k":
        return [1.0, row["density"], row["k_completeness"], math.sqrt(cap)]
    raise ValueError(model)


def _fit(model: str, data: list[dict]) -> list[float]:
    return curve._ols([_design(model, row) for row in data],
                      [row["A_coverage"] for row in data])


def _predict(model: str, row: dict, coef: list[float]) -> float:
    return sum(a * b for a, b in zip(_design(model, row), coef))


def _metrics(model: str, cells: list[dict], seeds: list[dict]) -> dict:
    cell_coef = _fit(model, cells)
    cell_fit = [_predict(model, row, cell_coef) for row in cells]
    cell_errors = [row["A_coverage"] - value
                   for row, value in zip(cells, cell_fit)]
    cell_loo = []
    for index, row in enumerate(cells):
        train = cells[:index] + cells[index + 1:]
        cell_loo.append(row["A_coverage"]
                        - _predict(model, row, _fit(model, train)))
    seed_loo = []
    for index, row in enumerate(seeds):
        train = seeds[:index] + seeds[index + 1:]
        seed_loo.append(row["A_coverage"]
                        - _predict(model, row, _fit(model, train)))
    seed_coef = _fit(model, seeds)
    seed_fit = [_predict(model, row, seed_coef) for row in seeds]
    seed_errors = [row["A_coverage"] - value
                   for row, value in zip(seeds, seed_fit)]
    return {
        "model": model,
        "parameters": len(cell_coef),
        "cell_in_rmse": round(math.sqrt(sum(e * e for e in cell_errors)
                                        / len(cell_errors)), 6),
        "cell_loo_rmse": round(math.sqrt(sum(e * e for e in cell_loo)
                                         / len(cell_loo)), 6),
        "cell_loo_max": round(max(abs(e) for e in cell_loo), 6),
        "seed_in_rmse": round(math.sqrt(sum(e * e for e in seed_errors)
                                        / len(seed_errors)), 6),
        "seed_loo_rmse": round(math.sqrt(sum(e * e for e in seed_loo)
                                         / len(seed_loo)), 6),
        "seed_loo_max": round(max(abs(e) for e in seed_loo), 6),
        "cell_coefficients": [round(value, 8) for value in cell_coef],
        "seed_coefficients": [round(value, 8) for value in seed_coef],
    }


def _corr(left: list[float], right: list[float]) -> float:
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean)
                    for a, b in zip(left, right))
    denominator = math.sqrt(sum((a - left_mean) ** 2 for a in left)
                            * sum((b - right_mean) ** 2 for b in right))
    return numerator / denominator if denominator else 0.0


def build() -> dict:
    source = op.build()
    seed_rows = []
    for row in source["seed_rows"]:
        tags = TAGS[row["block"]]
        seed_rows.append({
            "block": row["block"],
            "seed": row["seed"],
            "cap": row["cap"],
            "candidate_edges": row["candidate_edges"],
            "log_candidates": row["log_candidates"],
            "density": round(row["candidate_edges"] / tags, 6),
            "k_completeness": row["k_completeness"],
            "A_coverage": row["A_coverage"],
        })
    cells = []
    for block in BLOCKS:
        for cap in CAPS:
            group = [row for row in seed_rows
                     if row["block"] == block and row["cap"] == cap]
            cells.append({
                "block": block,
                "cap": cap,
                "log_candidates": round(sum(row["log_candidates"]
                                            for row in group) / len(group), 6),
                "density": round(sum(row["density"] for row in group)
                                 / len(group), 6),
                "k_completeness": round(sum(row["k_completeness"]
                                            for row in group) / len(group), 6),
                "A_coverage": round(sum(row["A_coverage"] for row in group)
                                    / len(group), 6),
            })
    comparisons = [_metrics(model, cells, seed_rows) for model in MODELS]
    by_model = {row["model"]: row for row in comparisons}
    larger = [row for row in seed_rows if row["block"] == "larger-28"]
    correlations = {
        "A_vs_log_candidates_larger": round(_corr(
            [row["A_coverage"] for row in larger],
            [row["log_candidates"] for row in larger]), 6),
        "A_vs_density_larger": round(_corr(
            [row["A_coverage"] for row in larger],
            [row["density"] for row in larger]), 6),
        "A_vs_k_completeness_larger": round(_corr(
            [row["A_coverage"] for row in larger],
            [row["k_completeness"] for row in larger]), 6),
        "density_vs_log_candidates_larger": round(_corr(
            [row["density"] for row in larger],
            [row["log_candidates"] for row in larger]), 6),
        "density_vs_k_completeness_larger": round(_corr(
            [row["density"] for row in larger],
            [row["k_completeness"] for row in larger]), 6),
    }
    block_pairs = [{
        "block": block,
        "log_candidates": next(row["log_candidates"] for row in cells
                               if row["block"] == block
                               and row["cap"] == CAPS[0]),
        "density": next(row["density"] for row in cells
                        if row["block"] == block and row["cap"] == CAPS[0]),
    } for block in BLOCKS]
    size = by_model["candidate_size"]
    density = by_model["candidate_density"]
    kc = by_model["k_completeness"]
    both = by_model["size_plus_density"]
    reading = (
        "Density predicts the offset about as well as candidate size at cell "
        "level and slightly worse across seeds; with 12 cells and 72 rows "
        "none of the three continuous summaries separates from the others, "
        "and only K completeness is clearly worse. Candidate density reaches "
        "cell LOO %.4f and seed LOO %.4f, against %.4f and %.4f for candidate "
        "size, %.4f and %.4f for the free block offset, and %.4f and %.4f "
        "for K completeness. The cell-level edge over size (%.4f) and the "
        "seed-level gap (%.4f) are both small against the fits' own error. "
        "Adding density to size does not help: cell LOO moves from %.4f to "
        "%.4f and seed LOO from %.4f to %.4f, with coefficients %s, because "
        "density is candidate count divided by a block constant. Across the "
        "three blocks the pairs run %s, so every monotone block summary "
        "separates the 16-tag blocks from larger-28 equally well. Within "
        "larger-28, A coverage correlates %.3f with density, %.3f with log "
        "candidate size and %.3f with K completeness, while density and size "
        "correlate %.3f. Density is an equally admissible label, not a "
        "better one: the data cannot choose between counting candidates and "
        "measuring how full the alphabet is, and that choice needs a design "
        "that varies one while holding the other."
        % (density["cell_loo_rmse"], density["seed_loo_rmse"],
           size["cell_loo_rmse"], size["seed_loo_rmse"],
           by_model["free_block_offset"]["cell_loo_rmse"],
           by_model["free_block_offset"]["seed_loo_rmse"],
           kc["cell_loo_rmse"], kc["seed_loo_rmse"],
           size["cell_loo_rmse"] - density["cell_loo_rmse"],
           density["seed_loo_rmse"] - size["seed_loo_rmse"],
           size["cell_loo_rmse"], both["cell_loo_rmse"],
           size["seed_loo_rmse"], both["seed_loo_rmse"],
           str(both["cell_coefficients"]),
           "; ".join("%s (%.4f, %.4f)" % (row["block"],
                                          row["log_candidates"],
                                          row["density"])
                     for row in block_pairs),
           correlations["A_vs_density_larger"],
           correlations["A_vs_log_candidates_larger"],
           correlations["A_vs_k_completeness_larger"],
           correlations["density_vs_log_candidates_larger"]))
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Is the block offset predicted by candidate-space size, "
            "candidate-space density or K completeness, rather than a free "
            "block label?"
        ),
        "definition": (
            "A_coverage = A / candidate_edges on 12 block-by-cap cells and 72 "
            "seed rows. Density = candidate_edges / tags in the block's "
            "alphabet (16 for both 16-tag blocks, 28 for larger-28). Models "
            "are compared by cell and seed leave-one-out error."
        ),
        "method": (
            "Reuse the committed 12-cell and 72-row data. With three blocks a "
            "block-level regression is saturated, so density is tested at "
            "cell and seed level and its block-level collinearity with "
            "candidate size is reported directly."
        ),
        "constants": {
            "blocks": list(BLOCKS),
            "caps": list(CAPS),
            "tags": dict(TAGS),
            "cells": len(cells),
            "seed_rows": len(seed_rows),
            "density": "candidate_edges / tags",
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "comparisons": comparisons,
        "correlations": correlations,
        "block_pairs": block_pairs,
        "cells": cells,
        "seed_rows": seed_rows,
        "not_evidence": (
            "A descriptive predictor comparison on 12 fixed block-by-cap "
            "cells and 72 seed rows from no-arm runs. Density and size are "
            "not intervened, are collinear across three blocks, and cannot be "
            "separated by this design; the artifact does not show that "
            "changing either would move the offset, and it is not a "
            "treatment, target viability or successor."
        ),
    })


def render(doc: dict) -> str:
    lines = [
        "# A1 block-offset density predictors",
        "",
        "Generated from `docs/a1_offset_density.json` by "
        "`python -m benchmarks.a1_offset_density --write`. Do not edit by hand.",
        "",
        "**Descriptive predictor comparison, not an A1 result.** 12 "
        "block-by-cap cells and 72 seed rows at caps **20/40/80/112**. No "
        "target, freeze, grant or A1 cell.",
        "",
        "Density is **candidate edges per tag**: 64/16 = **4.00** for both "
        "16-tag blocks and 167/28 ≈ **5.96** for larger-28.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Model comparison",
        "",
        "| Model | Parameters | Cell LOO RMSE | Cell LOO max | Seed LOO RMSE | Seed LOO max |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["comparisons"]:
        lines.append("| %s | %d | %.4f | %.4f | %.4f | %.4f |" % (
            row["model"], row["parameters"], row["cell_loo_rmse"],
            row["cell_loo_max"], row["seed_loo_rmse"], row["seed_loo_max"]))
    lines += [
        "",
        "## Block-level collinearity",
        "",
        "| Block | Mean log candidates | Mean density (edges per tag) |",
        "| --- | ---: | ---: |",
    ]
    for row in doc["block_pairs"]:
        lines.append("| %s | %.4f | %.4f |" % (
            row["block"], row["log_candidates"], row["density"]))
    lines += [
        "",
        "All three blocks are ordered the same way by either quantity, so "
        "three points cannot distinguish them.",
        "",
        "## Within larger-28",
        "",
        "| Relation | Correlation |",
        "| --- | ---: |",
        "| A coverage vs density | %.3f |" % doc["correlations"]["A_vs_density_larger"],
        "| A coverage vs log candidates | %.3f |" % doc["correlations"]["A_vs_log_candidates_larger"],
        "| A coverage vs K completeness | %.3f |" % doc["correlations"]["A_vs_k_completeness_larger"],
        "| Density vs log candidates | %.3f |" % doc["correlations"]["density_vs_log_candidates_larger"],
        "| Density vs K completeness | %.3f |" % doc["correlations"]["density_vs_k_completeness_larger"],
        "",
        "## Reading",
        "",
        "Density is a legitimate replacement for the block label and ties "
        "with candidate size; the choice between them is not identifiable "
        "here, and neither carries seed-level signal inside larger-28. K "
        "completeness remains the only one of the three that fails the "
        "seed-level comparison.",
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
    if len(doc.get("comparisons") or []) != len(MODELS):
        found.append("model count")
    if len(doc.get("cells") or []) != 12:
        found.append("cell count")
    if len(doc.get("seed_rows") or []) != 72:
        found.append("seed count")
    for row in doc.get("seed_rows") or []:
        if row.get("density") != round(row.get("candidate_edges", 0)
                                        / TAGS.get(row.get("block"), 0), 6):
            found.append("seed density at %r"
                         % ((row.get("block"), row.get("seed")),))
        if row.get("block") not in TAGS:
            found.append("seed block at %r" % ((row.get("seed"),),))
    for row in doc.get("cells") or []:
        if row.get("block") not in TAGS:
            found.append("cell block at %r" % ((row.get("block"),),))
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    row = {"block": "larger-28", "cap": 112, "log_candidates": 5.1,
           "density": 5.96, "k_completeness": 0.73}
    if len(_design("candidate_density", row)) != 3:
        failures.append("density design")
    if len(_design("size_plus_density", row)) != 4:
        failures.append("size-plus-density design")
    if _design("candidate_size", row)[1] != row["log_candidates"]:
        failures.append("size design must use log candidates")
    current = {"block": "current-16", "cap": 20, "log_candidates": 4.15,
               "density": 4.0, "k_completeness": 1.0}
    a = _design("candidate_size", row)
    b = _design("candidate_size", current)
    if a[1] == b[1]:
        failures.append("the two blocks must differ in candidate size")
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
        raise SystemExit("no density-predictor artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("density predictors: clean")
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
        print("density-predictor self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
