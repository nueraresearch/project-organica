"""Does the shared cap-response curve hold on a seed block it never saw?

The earlier holdout held out caps.  This holds out the seeds: a new 16-tag
block, ``20670101-20670106``, is measured at the four fitted caps
20/40/80/112, and the frozen fits predict it without refitting.

Only one of the two fitted models can make that prediction.  The shared curve
carries a free offset per known block, so it has nothing to say about a block
it has never seen.  The candidate-size offset — the model that replaced those
offsets — can: its offset is a function of the block's own mean
``log(candidate_edges)``.  Both fitted 16-tag offsets are also applied as a
bracket, so the new block can be read against the two blocks the fit does
know.

The candidate stream is **not** selected for this holdout.  It is derived by
the committed fixed rule in ``a1_target_selection.run_seed`` — one
deterministic orientation per unordered pair present in the first 36
acquisition cycles, ``boundary_safe=True`` — which is the same rule that
produced the fresh-16 stream.  No target is selected, no K or A screening is
applied, and nothing is chosen on an outcome.

The seeds must be fresh: the build refuses if any of them appears in a
committed docs artifact other than this one.

Cap 80 on two committed seeds must reproduce their committed A, K and A∩K
counts, or the build refuses.

No engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_cap_response_seed_holdout --write
    python -m benchmarks.a1_cap_response_seed_holdout --check
    python -m benchmarks.a1_cap_response_seed_holdout --self-test
"""
from __future__ import annotations

import argparse
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_arms
from benchmarks import a1_cap_response_curve as curve
from benchmarks import a1_prediction_cap_c1 as base
from benchmarks import a1_target_selection
from benchmarks import engine_stamp
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import (
    PHASE_ACQUISITION,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_cap_response_seed_holdout.json"
PAGE_PATH = DOCS / "A1-CAP-RESPONSE-SEED-HOLDOUT.md"
CURVE_PATH = DOCS / "a1_cap_response_curve.json"
PREDICTORS_PATH = DOCS / "a1_offset_predictors.json"
REFERENCE_PATH = DOCS / "a1_prediction_cap_c1.json"
ID = "A1-CAP-RESPONSE-SEED-HOLDOUT-1"
DATE = "2026-11-14"
KIND = "a1_cap_response_seed_holdout"
STATUS = ("DESCRIPTIVE — UNSEEN-SEED-BLOCK VALIDATION OF THE SHARED CURVE; "
          "NO TARGET, FREEZE, GRANT OR A1 CELL")
BLOCK = "unseen-16"
SEEDS = (20670101, 20670102, 20670103, 20670104, 20670105, 20670106)
CAPS = (20, 40, 80, 112)
CONTROL_CAP = 80
CONTROL_SEEDS = (20630101, 20650101)
# Frozen from docs/a1_offset_predictors.json: intercept, log-candidate
# coefficient, shared sqrt coefficient.
SIZE_COEFFICIENTS = (1.90290201, -0.35852459, 0.04698666)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _frozen() -> tuple[tuple, dict, dict]:
    predictors = _load(PREDICTORS_PATH)
    row = next(item for item in predictors["comparisons"]
               if item["model"] == "candidate_size")
    size = tuple(round(value, 8) for value in row["cell_coefficients"])
    if size != SIZE_COEFFICIENTS:
        raise SystemExit("REFUSED: the committed candidate-size model has changed")
    curve_doc = _load(CURVE_PATH)
    if curve_doc["selected_model"]["model"] != "common_sqrt_offset":
        raise SystemExit("REFUSED: the committed curve is not the shared sqrt form")
    def loo(design, rows):
        errors = []
        for index, item in enumerate(rows):
            train = rows[:index] + rows[index + 1:]
            coef = curve._ols([design(train_row) for train_row in train],
                              [train_row["A_coverage"] for train_row in train])
            errors.append(item["A_coverage"] - sum(
                left * right for left, right in zip(design(item), coef)))
        return round(_rmse(errors), 6)

    sixteen_cells = [item for item in predictors["cells"]
                     if item["block"] != "larger-28"]
    sixteen_rows = [item for item in predictors["seed_rows"]
                    if item["block"] != "larger-28"]
    references = {
        "size_cell_loo": row["cell_loo_rmse"],
        "size_seed_loo": row["seed_loo_rmse"],
        "shared_cell_loo": next(
            item["loo_rmse"] for item in curve_doc["comparisons"]
            if item["model"] == "common_sqrt_offset"),
        "shared_cell_loo_16tag": loo(
            lambda item: [1.0, float(item["block"] == "fresh-16"),
                          math.sqrt(item["cap"])], sixteen_cells),
        "size_seed_loo_16tag": loo(
            lambda item: [1.0, item["log_candidates"],
                          math.sqrt(item["cap"])], sixteen_rows),
        "sqrt_coefficient": curve_doc["sqrt_coefficient"],
    }
    return size, dict(curve_doc["block_offsets"]), references


def _predict_size(coef, log_candidates: float, cap: int) -> float:
    return coef[0] + coef[1] * log_candidates + coef[2] * math.sqrt(cap)


def _predict_offset(offset: float, sqrt_coefficient: float, cap: int) -> float:
    return offset + sqrt_coefficient * math.sqrt(cap)


def _rmse(errors: list[float]) -> float:
    return math.sqrt(sum(value * value for value in errors) / len(errors))


def _replay_one(seed: int, cap: int, candidates: set[str], world: dict) -> dict:
    """One no-arm replay against a given candidate stream."""
    db_path = _make_scratch_db("a1_cap_response_seed_holdout")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = cap
    service.MAX_LOOPS = base.LOOP_CAP
    a_edges: set[str] = set()
    k_edges: set[str] = set()
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo = acq_lo * EVENTS_PER_CYCLE
    event_hi = acq_hi * EVENTS_PER_CYCLE
    try:
        for index, (text, trainable) in enumerate(
                zip(world["events"], world["trainable"])):
            in_acq = event_lo <= index < event_hi
            if in_acq and not trainable:
                continue
            if index % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = index // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=a1_arms.ACQ_SOURCE if in_acq else "env")
            if (index + 1) % EVENTS_PER_CYCLE != 0:
                continue
            report = service.run_sleep_cycle()
            predictions = {
                "%s>%s" % (prediction.source, prediction.target)
                for prediction in report.predictions
            }
            carried = {"%s>%s" % edge
                       for edge in a1_arms._carrier_edges(report)}
            a_edges |= predictions & candidates
            k_edges |= carried & candidates
    finally:
        memory.close()
        db_path.unlink(missing_ok=True)
    return {
        "block": BLOCK,
        "seed": seed,
        "prediction_cap": cap,
        "candidate_edges": len(candidates),
        "A": len(a_edges),
        "K": len(k_edges),
        "A_and_K": len(a_edges & k_edges),
    }


def _replay_seed(seed: int) -> list[dict]:
    """Derive the seed's candidate stream once, then replay all four caps."""
    selection = a1_target_selection.run_seed(seed, boundary_safe=True)
    candidates = set(selection["u"])
    world = generate_compositional_world(seed=seed, cycles=base.CYCLES)
    return [_replay_one(seed, cap, candidates, world) for cap in CAPS]


def build() -> dict:
    size, offsets, references = _frozen()
    from benchmarks.presence_cap_experiment import seed_collisions
    collisions = seed_collisions(list(SEEDS), allow=(OUT_PATH,))
    if collisions:
        raise SystemExit("REFUSED: the seed block is not fresh: %r" % collisions)

    control_tasks = [(block["label"], seed, CONTROL_CAP)
                     for block in base.BLOCKS
                     for seed in CONTROL_SEEDS if seed in block["seeds"]]
    with ProcessPoolExecutor(max_workers=6) as pool:
        batches = list(pool.map(_replay_seed, list(SEEDS)))
    with ProcessPoolExecutor(max_workers=2) as pool:
        control_raw = list(pool.map(base._replay, control_tasks))

    reference = {
        (row["block"], row["seed"]): row
        for row in _load(REFERENCE_PATH)["rows"]
        if row["prediction_cap"] == CONTROL_CAP
    }
    control = []
    for row in control_raw:
        expected = reference[(row["block"], row["seed"])]
        if any(row[field] != expected[field]
               for field in ("A", "K", "A_and_K", "candidate_edges")):
            raise SystemExit(
                "REFUSED: cap-%d control %s/%d A %d K %d A∩K %d, expected "
                "%d/%d/%d" % (CONTROL_CAP, row["block"], row["seed"], row["A"],
                              row["K"], row["A_and_K"], expected["A"],
                              expected["K"], expected["A_and_K"]))
        control.append({
            "block": row["block"], "seed": row["seed"],
            "prediction_cap": CONTROL_CAP,
            "A": row["A"], "K": row["K"], "A_and_K": row["A_and_K"],
            "matches_committed": True,
        })

    raw = [row for batch in batches for row in batch]
    rows = [{
        "seed": row["seed"],
        "cap": row["prediction_cap"],
        "candidate_edges": row["candidate_edges"],
        "A": row["A"],
        "K": row["K"],
        "A_and_K": row["A_and_K"],
        "A_coverage": round(row["A"] / row["candidate_edges"], 6),
    } for row in raw]
    rows.sort(key=lambda item: (item["cap"], item["seed"]))
    log_candidates = round(
        sum(math.log(value) for value in
            {row["seed"]: row["candidate_edges"] for row in rows}.values())
        / len(SEEDS), 6)
    size_offset = round(size[0] + size[1] * log_candidates, 6)

    cells = []
    for cap in CAPS:
        group = [row for row in rows if row["cap"] == cap]
        observed = round(sum(row["A_coverage"] for row in group) / len(group), 6)
        predicted_size = round(_predict_size(size, log_candidates, cap), 6)
        current = round(_predict_offset(offsets["current-16"],
                                        references["sqrt_coefficient"], cap), 6)
        fresh = round(_predict_offset(offsets["fresh-16"],
                                      references["sqrt_coefficient"], cap), 6)
        cells.append({
            "cap": cap,
            "seeds": len(group),
            "observed": observed,
            "predicted_size": predicted_size,
            "residual_size": round(observed - predicted_size, 6),
            "predicted_current": current,
            "residual_current": round(observed - current, 6),
            "predicted_fresh": fresh,
            "residual_fresh": round(observed - fresh, 6),
        })

    per_seed = []
    for seed in SEEDS:
        group = [row for row in rows if row["seed"] == seed]
        errors = [row["A_coverage"]
                  - _predict_size(size, math.log(row["candidate_edges"]),
                                  row["cap"]) for row in group]
        per_seed.append({
            "seed": seed,
            "candidate_edges": group[0]["candidate_edges"],
            "mean_coverage": round(sum(row["A_coverage"] for row in group)
                                   / len(group), 6),
            "rmse_size": round(_rmse(errors), 6),
            "max_abs_size": round(max(abs(value) for value in errors), 6),
        })

    seed_errors = [row["A_coverage"]
                   - _predict_size(size, math.log(row["candidate_edges"]), row["cap"])
                   for row in rows]
    cell_errors = [row["residual_size"] for row in cells]
    metrics = {
        "cell_rmse_size": round(_rmse(cell_errors), 6),
        "cell_max_size": round(max(abs(value) for value in cell_errors), 6),
        "seed_rmse_size": round(_rmse(seed_errors), 6),
        "seed_max_size": round(max(abs(value) for value in seed_errors), 6),
        "cell_mean_residual": round(sum(cell_errors) / len(cell_errors), 6),
        "cell_rmse_current": round(_rmse([row["residual_current"]
                                          for row in cells]), 6),
        "cell_rmse_fresh": round(_rmse([row["residual_fresh"]
                                        for row in cells]), 6),
        "reference_size_cell_loo": references["size_cell_loo"],
        "reference_size_seed_loo": references["size_seed_loo"],
        "reference_shared_cell_loo": references["shared_cell_loo"],
        "reference_shared_cell_loo_16tag": references["shared_cell_loo_16tag"],
        "reference_size_seed_loo_16tag": references["size_seed_loo_16tag"],
        "log_candidates": log_candidates,
        "size_offset": size_offset,
        "fresh16_log_candidates": round(next(
            item["log_candidates"] for item in _load(PREDICTORS_PATH)["cells"]
            if item["block"] == "fresh-16" and item["cap"] == CAPS[0]), 6),
        "fresh_bracket_residual_min": round(min(
            row["residual_fresh"] for row in cells), 6),
        "fresh_bracket_residual_max": round(max(
            row["residual_fresh"] for row in cells), 6),
    }
    metrics["same_size_as_fresh16"] = (
        metrics["log_candidates"] == metrics["fresh16_log_candidates"])
    fitted_16tag = [
        {"cap": row["cap"], "block": row["block"], "observed": row["observed"]}
        for row in _load(CURVE_PATH)["cells"]
        if row["block"] in ("current-16", "fresh-16")
    ]
    brackets = 0
    for cell in cells:
        bounds = [row["observed"] for row in fitted_16tag
                  if row["cap"] == cell["cap"]]
        if min(bounds) <= cell["observed"] <= max(bounds):
            brackets += 1
    within = (metrics["cell_rmse_size"]
              <= metrics["reference_shared_cell_loo_16tag"])
    reading = (
        "On the unseen block the offset model misses the block's level. The "
        "frozen candidate-size offset predicts the four fitted caps with RMSE "
        "%.4f (max %.4f) and mean residual %+.4f, against a 16-tag "
        "leave-one-cell-out error of %.4f for the curve with free block "
        "offsets and %.4f for the size model itself. The 24 seed-by-cap "
        "values give RMSE %.4f (max %.4f), inside the 16-tag seed LOO of "
        "%.4f, so the per-seed scatter is no worse than at fitting time while "
        "the level is. The block sits below both fitted 16-tag blocks at all "
        "four caps — coverage %s at caps %s against "
        "0.6362/0.7356/0.8299/0.9032 for current-16 — although its candidate "
        "space is the same size (%d edges per seed). Its mean log candidate "
        "size, %.6f, is identical to fresh-16's, so the size model gives it "
        "fresh-16's offset (%.4f) and cannot tell the two blocks apart, yet "
        "the block still sits %.4f to %.4f below the fresh-16 bracket at "
        "every cap. Applying a known 16-tag "
        "offset instead is no better in kind: cell RMSE %.4f (current-16) and "
        "%.4f (fresh-16), both outside the fitted 16-tag LOO. Candidate size "
        "therefore replaces the block label inside the fitted blocks, but it "
        "does not predict a new block's offset; the cell error is %s the "
        "fitted 16-tag scale."
        % (metrics["cell_rmse_size"], metrics["cell_max_size"],
           metrics["cell_mean_residual"],
           metrics["reference_shared_cell_loo_16tag"],
           metrics["reference_size_cell_loo"],
           metrics["seed_rmse_size"], metrics["seed_max_size"],
           metrics["reference_size_seed_loo_16tag"],
           "/".join("%.4f" % row["observed"] for row in cells),
           "/".join(str(row["cap"]) for row in cells),
           min(row["candidate_edges"] for row in rows),
           metrics["log_candidates"], metrics["size_offset"],
           abs(metrics["fresh_bracket_residual_max"]),
           abs(metrics["fresh_bracket_residual_min"]),
           metrics["cell_rmse_current"], metrics["cell_rmse_fresh"],
           "inside" if within else "outside")
    )

    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Does the candidate-size offset that replaced the free block "
            "label predict A coverage on a 16-tag seed block the fit never "
            "saw?"
        ),
        "definition": (
            "A_coverage = A / candidate_edges on a fresh 16-tag block "
            "(20670101-20670106) at the fitted caps 20/40/80/112. Predicted "
            "values are frozen from the committed candidate-size model; "
            "nothing is refitted on the new block."
        ),
        "method": (
            "The candidate stream is derived by a1_target_selection.run_seed "
            "with boundary_safe=True — the committed fixed rule, no K or A "
            "screening — then replayed no-arm at loop cap 120. The block must "
            "appear in no committed docs artifact other than this one, and "
            "cap 80 on two committed seeds must reproduce their counts."
        ),
        "constants": {
            "cycles": base.CYCLES,
            "loop_cap": base.LOOP_CAP,
            "block": BLOCK,
            "seeds": list(SEEDS),
            "caps": list(CAPS),
            "control_cap": CONTROL_CAP,
            "control_seeds": list(CONTROL_SEEDS),
            "size_coefficients": list(SIZE_COEFFICIENTS),
            "sqrt_coefficient": references["sqrt_coefficient"],
            "block_offsets": dict(offsets),
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "metrics": metrics,
        "cells": cells,
        "per_seed": per_seed,
        "rows": rows,
        "control": control,
        "fitted_16tag_cells": fitted_16tag,
        "not_evidence": (
            "A descriptive held-out prediction from no-arm replays. The seed "
            "block is new, the caps are the fitted ones, and the model is "
            "frozen; this bounds seed-axis transfer of the offset model over "
            "one 16-tag block, not a population of blocks. The candidate "
            "stream comes from a fixed rule, not from target selection, so "
            "these are not A1 protocol cells. It is not a treatment, target "
            "viability or successor."
        ),
    })


def render(doc: dict) -> str:
    metrics = doc["metrics"]
    lines = [
        "# A1 cap-response seed holdout",
        "",
        "Generated from `docs/a1_cap_response_seed_holdout.json` by "
        "`python -m benchmarks.a1_cap_response_seed_holdout --write`. Do not edit by hand.",
        "",
        "**Descriptive held-out prediction, not an A1 result.** A fresh 16-tag "
        "block, **20670101–20670106**, at the fitted caps **20/40/80/112**. "
        "Candidate stream from the committed fixed rule, not target "
        "selection. No target, freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Cells",
        "",
        "| Cap | Observed | Size prediction | Residual | Current-16 bracket | Residual | Fresh-16 bracket | Residual |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["cells"]:
        lines.append("| %d | %.4f | %.4f | %+.4f | %.4f | %+.4f | %.4f | %+.4f |" % (
            row["cap"], row["observed"], row["predicted_size"],
            row["residual_size"], row["predicted_current"],
            row["residual_current"], row["predicted_fresh"],
            row["residual_fresh"]))
    lines += [
        "",
        "Reference scales. All 12 cells: shared curve LOO **%.4f**, "
        "candidate-size model **%.4f** (cell) and **%.4f** (seed). 16-tag "
        "cells and rows only: shared curve **%.4f** (cell) and candidate-size "
        "model **%.4f** (seed)."
        % (metrics["reference_shared_cell_loo"],
           metrics["reference_size_cell_loo"],
           metrics["reference_size_seed_loo"],
           metrics["reference_shared_cell_loo_16tag"],
           metrics["reference_size_seed_loo_16tag"]),
        "",
        "## Per seed",
        "",
        "| Seed | Candidates | Mean coverage | RMSE vs size prediction | Max |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["per_seed"]:
        lines.append("| %d | %d | %.4f | %.4f | %.4f |" % (
            row["seed"], row["candidate_edges"], row["mean_coverage"],
            row["rmse_size"], row["max_abs_size"]))
    lines += [
        "",
        "## Fitted 16-tag blocks",
        "",
        "| Cap | Current-16 | Fresh-16 | Unseen-16 |",
        "| ---: | ---: | ---: | ---: |",
    ]
    by_cap = {}
    for row in doc["fitted_16tag_cells"]:
        by_cap.setdefault(row["cap"], {})[row["block"]] = row["observed"]
    for row in doc["cells"]:
        lines.append("| %d | %.4f | %.4f | %.4f |" % (
            row["cap"], by_cap[row["cap"]]["current-16"],
            by_cap[row["cap"]]["fresh-16"], row["observed"]))
    lines += [
        "",
        "## Control",
        "",
        "Cap 80 on two committed seeds reproduces their committed A, K and "
        "A∩K counts.",
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
    if len(doc.get("cells") or []) != len(CAPS):
        found.append("cell count")
    if len(doc.get("rows") or []) != len(SEEDS) * len(CAPS):
        found.append("row count")
    if len(doc.get("per_seed") or []) != len(SEEDS):
        found.append("per-seed count")
    constants = doc.get("constants") or {}
    size = tuple(constants.get("size_coefficients") or ())
    if size != SIZE_COEFFICIENTS:
        found.append("size coefficients changed")
        size = SIZE_COEFFICIENTS
    log_candidates = (doc.get("metrics") or {}).get("log_candidates", 0.0)
    for row in doc.get("rows") or []:
        if row.get("A_coverage") != round(row.get("A", 0)
                                          / row.get("candidate_edges", 1), 6):
            found.append("seed coverage at %r"
                         % ((row.get("seed"), row.get("cap")),))
        if row.get("block") is not None:
            found.append("row carries a block label")
    for row in doc.get("cells") or []:
        predicted = round(_predict_size(size, log_candidates, row.get("cap", 0)), 6)
        if row.get("predicted_size") != predicted:
            found.append("cell prediction at %r" % ((row.get("cap"),),))
        if row.get("residual_size") != round(
                row.get("observed", 0.0) - predicted, 6):
            found.append("cell residual at %r" % ((row.get("cap"),),))
    for row in doc.get("control") or []:
        if row.get("matches_committed") is not True:
            found.append("control %r is not committed" % ((row.get("seed"),),))
    if len(doc.get("control") or []) != len(CONTROL_SEEDS):
        found.append("control count")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    coef = SIZE_COEFFICIENTS
    if abs(_predict_size(coef, 4.15, 0) - (coef[0] + coef[1] * 4.15)) > 1e-12:
        failures.append("size prediction at cap 0")
    if _predict_offset(0.42, 0.047, 100) <= 0.42:
        failures.append("offset prediction must rise with the cap")
    if min(SEEDS) < 20670101:
        failures.append("the seed block must be the declared fresh block")
    if CAPS != (20, 40, 80, 112):
        failures.append("the holdout caps must be the fitted caps")
    if len(set(SEEDS)) != len(SEEDS):
        failures.append("the seed block has duplicates")
    if set(SEEDS) & set(CONTROL_SEEDS):
        failures.append("the control seeds must be outside the holdout block")
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
        raise SystemExit("no seed-holdout artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("cap-response seed holdout: clean")
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
        print("seed-holdout self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
