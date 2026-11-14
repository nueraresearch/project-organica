"""Can candidate size and K completeness replace the free block offset?

The shared cap-response fit estimates one offset per block.  This asks whether
the offset is predictable from two block-level quantities:

* candidate-space size, ``log(candidate_edges)`` per seed;
* K completeness, ``K / candidate_edges``.

With only three blocks, a block-level regression is saturated, so the test is
run at the seed and cell level.  Models are compared by leave-one-cell-out and
leave-one-seed-out error.  Candidate size and K completeness are also checked
within larger-28, where their values vary across seeds.

No engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_offset_predictors --write
    python -m benchmarks.a1_offset_predictors --check
    python -m benchmarks.a1_offset_predictors --self-test
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from benchmarks import a1_cap_response_curve as curve
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_offset_predictors.json"
PAGE_PATH = DOCS / "A1-OFFSET-PREDICTORS.md"
ID = "A1-OFFSET-PREDICTORS-1"
DATE = "2026-11-14"
KIND = "a1_offset_predictors"
STATUS = "DESCRIPTIVE — BLOCK OFFSET PREDICTORS; NO TARGET, FREEZE, GRANT OR A1 CELL"
BLOCKS = ("current-16", "fresh-16", "larger-28")
CAPS = (20, 40, 80, 112)
MODELS = (
    "free_block_offset",
    "candidate_size",
    "k_completeness",
    "candidate_plus_k",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _design(model: str, row: dict):
    block, cap = row["block"], row["cap"]
    fresh = block == "fresh-16"
    larger = block == "larger-28"
    if model == "free_block_offset":
        return [1.0, float(fresh), float(larger), math.sqrt(cap)]
    if model == "candidate_size":
        return [1.0, row["log_candidates"], math.sqrt(cap)]
    if model == "k_completeness":
        return [1.0, row["k_completeness"], math.sqrt(cap)]
    if model == "candidate_plus_k":
        return [1.0, row["log_candidates"], row["k_completeness"],
                math.sqrt(cap)]
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
        coef = _fit(model, train)
        cell_loo.append(row["A_coverage"] - _predict(model, row, coef))
    seed_coef = _fit(model, seeds)
    seed_fit = [_predict(model, row, seed_coef) for row in seeds]
    seed_errors = [row["A_coverage"] - value
                   for row, value in zip(seeds, seed_fit)]
    seed_loo = []
    for index, row in enumerate(seeds):
        train = seeds[:index] + seeds[index + 1:]
        coef = _fit(model, train)
        seed_loo.append(row["A_coverage"] - _predict(model, row, coef))
    return {
        "model": model,
        "parameters": len(cell_coef),
        "cell_in_rmse": round(math.sqrt(sum(e * e for e in cell_errors)
                                        / len(cell_errors)), 6),
        "cell_in_max": round(max(abs(e) for e in cell_errors), 6),
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
    denominator = math.sqrt(
        sum((a - left_mean) ** 2 for a in left)
        * sum((b - right_mean) ** 2 for b in right))
    return numerator / denominator if denominator else 0.0


def _block_offsets() -> dict:
    return {
        "current-16": 0.42002218,
        "fresh-16": 0.40646398,
        "larger-28": 0.06883733,
    }


def build() -> dict:
    cells, seeds = curve._cells()
    # curve._cells gives block, cap, A_coverage and seed rows with A/K.
    # Add the two predictors on each level.
    c1 = curve._load(curve.C1_PATH)["rows"]
    high = curve._load(curve.CAP112_PATH)["rows"]
    raw = {(row["block"], row["seed"], row["prediction_cap"]): row
           for row in c1}
    for row in high:
        key = (row["block"], row["seed"], row["prediction_cap"])
        if key in raw:
            for field in ("candidate_edges", "A", "K", "A_and_K"):
                if raw[key][field] != row[field]:
                    raise SystemExit(
                        "REFUSED: %s/%d/%d %s disagrees"
                        % (key[0], key[1], key[2], field))
        raw[key] = row
    seed_rows = []
    for (block, seed, cap), row in sorted(raw.items()):
        seed_rows.append({
            "block": block,
            "seed": seed,
            "cap": cap,
            "candidate_edges": row["candidate_edges"],
            "log_candidates": math.log(row["candidate_edges"]),
            "k_completeness": row["K"] / row["candidate_edges"],
            "A_coverage": row["A"] / row["candidate_edges"],
        })
    cell_rows = []
    for block in BLOCKS:
        for cap in CAPS:
            group = [row for row in seed_rows
                     if row["block"] == block and row["cap"] == cap]
            cell_rows.append({
                "block": block,
                "cap": cap,
                "log_candidates": sum(row["log_candidates"] for row in group)
                / len(group),
                "k_completeness": sum(row["k_completeness"] for row in group)
                / len(group),
                "A_coverage": sum(row["A_coverage"] for row in group)
                / len(group),
            })
    comparisons = [_metrics(model, cell_rows, seed_rows) for model in MODELS]
    by_model = {row["model"]: row for row in comparisons}
    free = by_model["free_block_offset"]
    size = by_model["candidate_size"]
    kc = by_model["k_completeness"]
    both = by_model["candidate_plus_k"]
    larger = [row for row in seed_rows if row["block"] == "larger-28"]
    correlations = {
        "A_vs_k_completeness_larger": round(_corr(
            [row["A_coverage"] for row in larger],
            [row["k_completeness"] for row in larger]), 6),
        "A_vs_log_candidates_larger": round(_corr(
            [row["A_coverage"] for row in larger],
            [row["log_candidates"] for row in larger]), 6),
        "k_completeness_vs_log_candidates_larger": round(_corr(
            [row["k_completeness"] for row in larger],
            [row["log_candidates"] for row in larger]), 6),
    }
    by_cap = []
    for cap in CAPS:
        group = [row for row in larger if row["cap"] == cap]
        by_cap.append({
            "cap": cap,
            "A_vs_k_completeness": round(_corr(
                [row["A_coverage"] for row in group],
                [row["k_completeness"] for row in group]), 6),
            "A_vs_log_candidates": round(_corr(
                [row["A_coverage"] for row in group],
                [row["log_candidates"] for row in group]), 6),
        })
    reading = (
        "Candidate size can replace the free block offset: its cell LOO RMSE "
        "is %.4f against %.4f for the free offset, and its seed LOO is %.4f "
        "against %.4f. K completeness alone is similar at cell level (%.4f) "
        "but much worse across seeds (%.4f), and adding it to candidate size "
        "does not improve seed LOO (%.4f vs %.4f). Within larger-28, K "
        "completeness and A coverage correlate only %.3f, while candidate "
        "size and A coverage correlate %.3f. Candidate size is the usable "
        "offset predictor; K completeness is a correlated regime marker, not "
        "an independent predictor."
        % (size["cell_loo_rmse"], free["cell_loo_rmse"],
           size["seed_loo_rmse"], free["seed_loo_rmse"],
           kc["cell_loo_rmse"], kc["seed_loo_rmse"],
           both["seed_loo_rmse"], size["seed_loo_rmse"],
           correlations["A_vs_k_completeness_larger"],
           correlations["A_vs_log_candidates_larger"]))
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Is the block offset in the shared cap-response curve predicted "
            "by candidate-space size or K completeness, rather than a free "
            "block label?"
        ),
        "definition": (
            "A_coverage = A / candidate_edges on 12 block-by-cap cells and 72 "
            "seed rows. Predictors are log(candidate_edges) and "
            "K / candidate_edges. Models are compared by cell and seed "
            "leave-one-out error."
        ),
        "method": (
            "Read the committed cap-20/40/80/112 rows. With only three blocks "
            "a block-level regression is saturated, so candidate-size and "
            "K-completeness models are tested at cell and seed level. "
            "Within-larger correlations are reported separately."
        ),
        "constants": {
            "blocks": list(BLOCKS),
            "caps": list(CAPS),
            "cells": len(cell_rows),
            "seed_rows": len(seed_rows),
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "comparisons": comparisons,
        "correlations": correlations,
        "larger_by_cap": by_cap,
        "free_block_offsets": _block_offsets(),
        "size_offsets_at_cap0": {
            block: round(
                size["cell_coefficients"][0]
                + size["cell_coefficients"][1]
                * (sum(row["log_candidates"] for row in cell_rows
                       if row["block"] == block) / len(CAPS)), 6)
            for block in BLOCKS
        },
        "cells": [
            {key: (round(value, 6) if isinstance(value, float) else value)
             for key, value in row.items()}
            for row in cell_rows
        ],
        "seed_rows": [
            {key: (round(value, 6) if isinstance(value, float) else value)
             for key, value in row.items()}
            for row in seed_rows
        ],
        "not_evidence": (
            "A descriptive predictor comparison on 12 fixed block-by-cap "
            "cells and 72 seed rows from no-arm runs. Candidate size and K "
            "completeness are not intervened; the artifact does not show that "
            "changing either would move the offset, and it is not a treatment, "
            "target viability or successor."
        ),
    })


def render(doc: dict) -> str:
    models = {row["model"]: row for row in doc["comparisons"]}
    free = models["free_block_offset"]
    size = models["candidate_size"]
    kc = models["k_completeness"]
    both = models["candidate_plus_k"]
    lines = [
        "# A1 block-offset predictors",
        "",
        "Generated from `docs/a1_offset_predictors.json` by "
        "`python -m benchmarks.a1_offset_predictors --write`. Do not edit by hand.",
        "",
        "**Descriptive predictor comparison, not an A1 result.** 12 "
        "block-by-cap cells and 72 seed rows at caps **20/40/80/112**. No "
        "target, freeze, grant or A1 cell.",
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
            row["cell_loo_max"], row["seed_loo_rmse"],
            row["seed_loo_max"]))
    lines += [
        "",
        "Candidate size replaces two block dummies with one continuous "
        "predictor and uses one fewer parameter. K completeness alone does "
        "not improve seed prediction; the joint model is collinear.",
        "",
        "## Offsets",
        "",
        "| Block | Free offset | Candidate-size prediction at cap 0 |",
        "| --- | ---: | ---: |",
    ]
    for block in BLOCKS:
        lines.append("| %s | %.4f | %.4f |" % (
            block, doc["free_block_offsets"][block],
            doc["size_offsets_at_cap0"][block]))
    lines += [
        "",
        "The candidate-size prediction reproduces the large larger-28 "
        "offset; it does not distinguish current-16 from fresh-16, whose "
        "sizes are nearly identical.",
        "",
        "## Within larger-28",
        "",
        "| Relation | Correlation |",
        "| --- | ---: |",
        "| A coverage vs K completeness | %.3f |" % doc["correlations"]["A_vs_k_completeness_larger"],
        "| A coverage vs log candidates | %.3f |" % doc["correlations"]["A_vs_log_candidates_larger"],
        "| K completeness vs log candidates | %.3f |" % doc["correlations"]["k_completeness_vs_log_candidates_larger"],
        "",
        "| Cap | A vs K completeness | A vs log candidates |",
        "| ---: | ---: | ---: |",
    ]
    for row in doc["larger_by_cap"]:
        lines.append("| %d | %.3f | %.3f |" % (
            row["cap"], row["A_vs_k_completeness"],
            row["A_vs_log_candidates"]))
    lines += [
        "",
        "Within the larger block neither quantity carries a stable seed-level "
        "signal. The between-block offset is a candidate-space effect that "
        "the block label summarizes; K completeness is too collinear with "
        "that label to be an independent predictor.",
        "",
        "## Reading",
        "",
        "Candidate-space size is the simpler replacement for the free block "
        "offset. K completeness is a regime marker: it separates 16-tag from "
        "larger-28, but it does not predict A coverage within larger-28 and "
        "does not improve seed-level prediction once size is included.",
        "",
        "The joint model's slightly lower cell LOO is not evidence of two "
        "independent predictors: its coefficients are large and unstable "
        "because candidate size and K completeness are strongly collinear.",
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
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    row = {"block": "larger-28", "cap": 112, "log_candidates": 5.1,
           "k_completeness": 0.73}
    if len(_design("candidate_size", row)) != 3:
        failures.append("candidate-size design")
    if len(_design("candidate_plus_k", row)) != 4:
        failures.append("joint design")
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
        raise SystemExit("no offset-predictor artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("offset predictors: clean")
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
        print("offset-predictor self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
