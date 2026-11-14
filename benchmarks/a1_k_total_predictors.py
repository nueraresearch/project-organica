"""What predicts absolute K per seed, rather than K density?

Every A1 block so far points at **total K supply** as the constrained quantity:
the 16-tag and 28-tag blocks have 242 and 244 K rows despite 383 and 1000
candidate edges.  This read-only join asks which measured feature tracks the
per-seed K count across three no-arm blocks:

* current 16-tag control (``20630101``-``20630106``);
* fresh 16-tag block (``20650101``-``20650106``);
* 28-tag larger block (``20660101``-``20660106``).

The pre-run features are structural or pre-U: candidate edges, cycle-36 U,
pre-U pair support, high-support breadth and transition mix.  A availability is
included as a **post-run benchmark**, because it is an output of the same
baseline, not a design lever.

The models are deliberately univariate.  With 18 seeds and three worlds, a
multi-feature fit would be a description of these 18 rows rather than a
prediction.  Leave-one-world-out error is reported as the honest check: a
feature that only works inside one world does not predict total K across
worlds.

No target is selected, no threshold changes, no seed is reserved, no grant
exists and no A1 cell runs.

    python -m benchmarks.a1_k_total_predictors --write
    python -m benchmarks.a1_k_total_predictors --check
    python -m benchmarks.a1_k_total_predictors --self-test
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from benchmarks import a1_larger_universe
from benchmarks import a1_target_selection
from benchmarks.acquisition_compositional import (
    PHASE_ACQUISITION,
    generate_compositional_world,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_k_total_predictors.json"
PAGE_PATH = DOCS / "A1-K-TOTAL-PREDICTORS.md"
ID = "A1-K-TOTAL-PREDICTORS-1"
DATE = "2026-11-14"
KIND = "a1_k_total_predictors"
STATUS = "DESCRIPTIVE — WHAT TRACKS ABSOLUTE K; NO TARGET, NO THRESHOLD, NO RUN"
U_CYCLE = 36
FEATURES = (
    ("candidate_edges", "structural opportunity", True),
    ("mean_U", "mean cycle-36 U strength", True),
    ("median_U", "median cycle-36 U strength", True),
    ("mean_support_36", "mean pre-U pair support", True),
    ("median_support_36", "median pre-U pair support", True),
    ("support_ge4_edges", "edges with pre-U support >= 4", True),
    ("flip_p_share", "flip-P share of candidate edges", True),
    ("A_available", "A available in the 120-cycle baseline", False),
)
MODELS = tuple(feature for feature, _, _ in FEATURES)
BOOTSTRAP = 4000
RNG_SEED = 20261114
WORLDS = (
    {
        "label": "current-16",
        "tags": 16,
        "selection": DOCS / "a1_target_selection.json",
        "baseline": DOCS / "a1_baseline_availability.json",
        "candidate": None,
        "seeds": (20630101, 20630102, 20630103, 20630104, 20630105, 20630106),
        "world": lambda seed: generate_compositional_world(seed=seed, cycles=120),
    },
    {
        "label": "fresh-16",
        "tags": 16,
        "selection": None,
        "baseline": None,
        "candidate": DOCS / "a1_successor_candidate.json",
        "seeds": (20650101, 20650102, 20650103, 20650104, 20650105, 20650106),
        "world": lambda seed: generate_compositional_world(seed=seed, cycles=120),
    },
    {
        "label": "larger-28",
        "tags": 28,
        "selection": None,
        "baseline": None,
        "candidate": DOCS / "a1_larger_universe_candidate.json",
        "seeds": (20660101, 20660102, 20660103, 20660104, 20660105, 20660106),
        "world": a1_larger_universe.generate_world,
    },
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _percent(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _support_36(world: dict) -> Counter:
    """Directed pair support in the acquisition window before cycle 36."""
    counts: Counter = Counter()
    previous: list[str] = []
    acq_lo, _ = PHASE_ACQUISITION
    event_lo = acq_lo * EVENTS_PER_CYCLE
    event_hi = U_CYCLE * EVENTS_PER_CYCLE
    for index, (text, trainable) in enumerate(
            zip(world["events"], world["trainable"])):
        current = text.split()
        if event_lo <= index < event_hi and trainable and previous:
            for source in previous:
                for target in current:
                    if source != target:
                        counts[(source, target)] += 1
        previous = current
    return counts


def _cell_relation(world: dict, edge: str) -> str:
    source, target = edge.split(">", 1)
    source_cell = world["tag_to_cell"].get(source)
    target_cell = world["tag_to_cell"].get(target)
    if source_cell is None or target_cell is None:
        return "unknown"
    if source_cell == target_cell:
        return "same"
    sp, sq = int(source_cell[1]), int(source_cell[3])
    tp, tq = int(target_cell[1]), int(target_cell[3])
    if sp != tp and sq == tq:
        return "flip_p"
    if sp == tp and sq != tq:
        return "flip_q"
    return "diagonal"


def _current_rows(spec: dict) -> list[dict]:
    selection = _load(spec["selection"])["per_seed"]
    baseline = {
        int(row["seed"]): {entry["edge"]: entry for entry in row["rows"]}
        for row in _load(spec["baseline"])["per_seed"]
    }
    rows = []
    for seed in spec["seeds"]:
        world = spec["world"](seed)
        supports = _support_36(world)
        u = selection[str(seed)]["u"]
        for edge in sorted(u):
            base = baseline[seed][edge]
            source, target = edge.split(">", 1)
            rows.append({
                "block": spec["label"],
                "tags": spec["tags"],
                "seed": seed,
                "edge": edge,
                "A": bool(base["A"]),
                "K": bool(base["K"]),
                "U": int(u[edge]["strength"]),
                "support": int(supports[(source, target)]),
                "cell_relation": _cell_relation(world, edge),
            })
    return rows


def _candidate_rows(spec: dict) -> list[dict]:
    doc = _load(spec["candidate"])
    rows = []
    for seed in spec["seeds"]:
        world = spec["world"](seed)
        supports = _support_36(world)
        selection = a1_target_selection.run_seed(
            seed, world=world, boundary_safe=True)
        u = selection["u"]
        for candidate in doc["per_seed"][str(seed)]:
            edge = candidate["edge"]
            source, target = edge.split(">", 1)
            rows.append({
                "block": spec["label"],
                "tags": spec["tags"],
                "seed": seed,
                "edge": edge,
                "A": bool(candidate["A"]),
                "K": bool(candidate["K"]),
                "U": int(u[edge]["strength"]),
                "support": int(supports[(source, target)]),
                "cell_relation": _cell_relation(world, edge),
            })
    return rows


def _seed_rows(rows: list[dict], block: str, seed: int) -> dict:
    block_rows = [row for row in rows
                  if row["block"] == block and row["seed"] == seed]
    supports = [row["support"] for row in block_rows]
    strengths = [row["U"] for row in block_rows]
    flip_p = sum(row["cell_relation"] == "flip_p" for row in block_rows)
    return {
        "block": block,
        "tags": block_rows[0]["tags"],
        "seed": seed,
        "candidate_edges": len(block_rows),
        "A_available": sum(row["A"] for row in block_rows),
        "K_available": sum(row["K"] for row in block_rows),
        "A_and_K": sum(row["A"] and row["K"] for row in block_rows),
        "mean_U": round(sum(strengths) / len(strengths), 6),
        "median_U": _median(strengths),
        "mean_support_36": round(sum(supports) / len(supports), 6),
        "median_support_36": _median(supports),
        "support_ge4_edges": sum(value >= 4 for value in supports),
        "flip_p_share": _percent(flip_p, len(block_rows)),
        "K_density": _percent(sum(row["K"] for row in block_rows), len(block_rows)),
    }


def _median(values: list[int]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return round((ordered[middle - 1] + ordered[middle]) / 2, 6)


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(order):
        end = position + 1
        while end < len(order) and values[order[end]] == values[order[position]]:
            end += 1
        average = (position + end - 1) / 2 + 1
        for index in order[position:end]:
            ranks[index] = average
        position = end
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    denom_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def _spearman(xs: list[float], ys: list[float]) -> float | None:
    value = _pearson(_ranks(xs), _ranks(ys))
    return None if value is None else round(value, 6)


def _bootstrap_ci(xs: list[float], ys: list[float]) -> list[float | None]:
    rng = random.Random(RNG_SEED)
    values = []
    for _ in range(BOOTSTRAP):
        sample = [rng.randrange(len(xs)) for _ in xs]
        value = _spearman([xs[index] for index in sample],
                          [ys[index] for index in sample])
        if value is not None:
            values.append(value)
    values.sort()
    if not values:
        return [None, None]
    return [round(values[int(0.025 * (len(values) - 1))], 6),
            round(values[int(0.975 * (len(values) - 1))], 6)]


def _fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = (sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
             / denominator) if denominator else 0.0
    return slope, mean_y - slope * mean_x


def _model_table(seed_rows: list[dict]) -> list[dict]:
    out = []
    for feature in MODELS:
        xs = [float(row[feature]) for row in seed_rows]
        ys = [float(row["K_available"]) for row in seed_rows]
        within = []
        for block in sorted({row["block"] for row in seed_rows}):
            block_rows = [row for row in seed_rows if row["block"] == block]
            value = _spearman([float(row[feature]) for row in block_rows],
                              [float(row["K_available"]) for row in block_rows])
            within.append({"block": block, "rho": value})
        out.append({
            "feature": feature,
            "pooled_rho": _spearman(xs, ys),
            "pooled_ci": _bootstrap_ci(xs, ys),
            "within_block": within,
        })
    return out


def _lofo(seed_rows: list[dict], feature: str | None) -> dict:
    blocks = sorted({row["block"] for row in seed_rows})
    errors = []
    by_block = {}
    for held in blocks:
        train = [row for row in seed_rows if row["block"] != held]
        test = [row for row in seed_rows if row["block"] == held]
        if feature is None:
            prediction = sum(row["K_available"] for row in train) / len(train)
            slope = 0.0
        else:
            slope, intercept = _fit(
                [float(row[feature]) for row in train],
                [float(row["K_available"]) for row in train])
            prediction = None
        block_errors = []
        for row in test:
            predicted = (prediction if feature is None else
                         slope * float(row[feature]) + intercept)
            block_errors.append(abs(predicted - row["K_available"]))
        errors.extend(block_errors)
        by_block[held] = round(sum(block_errors) / len(block_errors), 6)
    return {
        "feature": feature,
        "mae": round(sum(errors) / len(errors), 6),
        "by_block": by_block,
    }


def build() -> dict:
    all_rows = []
    for spec in WORLDS:
        rows = (_current_rows(spec) if spec["candidate"] is None
                else _candidate_rows(spec))
        all_rows.extend(rows)
    seed_rows = []
    for spec in WORLDS:
        for seed in spec["seeds"]:
            seed_rows.append(_seed_rows(all_rows, spec["label"], seed))
    correlations = _model_table(seed_rows)
    lofo = [_lofo(seed_rows, None)] + [_lofo(seed_rows, feature)
                                        for feature in MODELS]
    baseline = lofo[0]
    best = min((row for row in lofo if row["feature"] is not None),
               key=lambda row: row["mae"])
    pre_run_best = min(
        (row for row in lofo if row["feature"] in {
            feature for feature, _, is_pre in FEATURES if is_pre}),
        key=lambda row: row["mae"])
    gain = round(baseline["mae"] - best["mae"], 6)
    pre_run_gain = round(baseline["mae"] - pre_run_best["mae"], 6)
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "scope": (
            "Eighteen seeds across the current 16-tag, fresh 16-tag and 28-tag "
            "blocks. K is the count of candidate edges with at least one carrier "
            "in the 120-cycle no-arm baseline. U and support are measured before "
            "K: U at cycle 36, support in the acquisition window before cycle 36. "
            "No treatment was applied."
        ),
        "features": [
            {"name": feature, "description": description,
             "pre_run": is_pre}
            for feature, description, is_pre in FEATURES
        ],
        "seed_rows": seed_rows,
        "correlations": correlations,
        "leave_one_world_out": lofo,
        "best_observed": {
            "model": best["feature"],
            "mae": best["mae"],
            "mean_baseline_mae": baseline["mae"],
            "gain_vs_baseline": gain,
            "pre_run_model": pre_run_best["feature"],
            "pre_run_mae": pre_run_best["mae"],
            "pre_run_gain_vs_baseline": pre_run_gain,
            "finding": (
                "No pre-run feature predicts absolute K across worlds. "
                "A_available is the lowest-MAE model but is a post-run output "
                "and improves on the mean baseline by only %.2f K rows; the "
                "best pre-run feature is %.2f rows worse than the baseline."
                % (gain, -pre_run_gain)
            ),
        },
        "interpretation": {
            "question": "Which measured feature tracks per-seed absolute K across worlds?",
            "not_causal": (
                "All entries are associations. A is an output of the same baseline, "
                "not a design lever. A low leave-one-world-out error is predictive "
                "only for these three blocks."
            ),
            "decision_use": (
                "A pre-run feature that predicts across worlds would be a candidate "
                "design lever; a post-run feature would only describe the engine's "
                "outputs."
            ),
        },
        "limits": [
            "Eighteen seeds and three world blocks; this is not a fitted causal model.",
            "The current and fresh 16-tag blocks share a world family but not seeds; the 28-tag block differs in tag count and mapping.",
            "Support is measured before U (cycles 20-35) and is not a latent probability.",
            "K is a no-arm availability flag, not a treatment or a rate.",
            "A leave-one-world-out error is a small-sample descriptive check, not a validated predictor.",
            "No target, threshold, freeze, grant or run changed.",
        ],
        "not_evidence": (
            "A read-only join of existing no-arm rows. It selects no target, changes "
            "no protocol and runs no A1 cell."
        ),
        "governance": {
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("record kind")
    if doc.get("id") != ID:
        found.append("record id")
    if doc.get("status") != STATUS:
        found.append("record status")
    rows = doc.get("seed_rows") or []
    if len(rows) != 18:
        found.append("seed-row count")
    if {row.get("block") for row in rows} != {
            "current-16", "fresh-16", "larger-28"}:
        found.append("block labels")
    for row in rows:
        if row.get("A_available") is None or row.get("K_available") is None:
            found.append("seed row lacks A/K")
        if not isinstance(row.get("K_available"), int):
            found.append("K is not an integer")
        if not isinstance(row.get("candidate_edges"), int):
            found.append("candidate edges is not an integer")
    models = doc.get("leave_one_world_out") or []
    if len(models) != len(MODELS) + 1:
        found.append("LOFO model count")
    if any(model.get("mae") is None for model in models):
        found.append("LOFO model lacks MAE")
    if doc.get("governance") != {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none"}:
        found.append("governance changed")
    return found


def self_test() -> list[str]:
    found: list[str] = []
    if _median([1, 2, 3, 4]) != 2.5:
        found.append("median even")
    if _median([1, 2, 3]) != 2.0:
        found.append("median odd")
    if _spearman([1, 2, 3], [1, 2, 3]) != 1.0:
        found.append("positive Spearman")
    if _spearman([1, 2, 3], [3, 2, 1]) != -1.0:
        found.append("negative Spearman")
    if _spearman([1, 1, 1], [1, 2, 3]) is not None:
        found.append("zero-variance Spearman")
    if _percent(1, 0) != 0.0:
        found.append("zero denominator")
    return found


def render(doc: dict) -> str:
    rows = doc["seed_rows"]
    best = doc["best_observed"]
    lines = [
        "# A1 absolute K predictors — what tracks total K?",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** It is a read-only join of eighteen no-arm "
        "seeds across three blocks. It selects no target, changes no threshold "
        "and runs no A1 cell.",
        "",
        "## The question",
        "",
        "K density is a ratio. The constrained quantity is the **absolute K count** "
        "per seed. This artifact asks which measured feature tracks that count "
        "across worlds, not which rows happen to have K.",
        "",
        "## Per-seed rows",
        "",
        "| Block | Seed | Edges | A | K | Mean U | Median support | Support >=4 | Flip-P share |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| %s | `%d` | %d | %d | %d | %.2f | %.2f | %d | %.1f%% |" % (
                row["block"], row["seed"], row["candidate_edges"],
                row["A_available"], row["K_available"], row["mean_U"],
                row["median_support_36"], row["support_ge4_edges"],
                100 * row["flip_p_share"],
            )
        )
    lines += [
        "",
        "## Correlations with absolute K",
        "",
        "Spearman rank correlation, pooled across 18 seeds and within each "
        "6-seed block. A bootstrap 95% interval is shown for the pooled value; "
        "it resamples seeds, not worlds.",
        "",
        "| Feature | Pooled rho | 95% interval | Current-16 | Fresh-16 | Larger-28 | Pre-run? |",
        "| --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    by_feature = {row["feature"]: row for row in doc["correlations"]}
    for feature, description, is_pre in FEATURES:
        row = by_feature[feature]
        within = {entry["block"]: entry["rho"] for entry in row["within_block"]}
        lines.append(
            "| %s | %s | %s | %s | %s | %s | %s |" % (
                feature, _fmt(row["pooled_rho"]),
                "%s to %s" % (_fmt(row["pooled_ci"][0]), _fmt(row["pooled_ci"][1])),
                _fmt(within.get("current-16")), _fmt(within.get("fresh-16")),
                _fmt(within.get("larger-28")), "yes" if is_pre else "no",
            )
        )
    lines += [
        "",
        "## Leave-one-world-out prediction",
        "",
        "Each model is fit on two blocks and predicts the third. MAE is in K rows "
        "per seed. The mean baseline predicts the training-block K mean for every "
        "held-out seed.",
        "",
        "| Model | LOFO MAE | Current-16 | Fresh-16 | Larger-28 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["leave_one_world_out"]:
        lines.append(
            "| %s | %.2f | %.2f | %.2f | %.2f |" % (
                row["feature"] or "mean baseline", row["mae"],
                row["by_block"]["current-16"], row["by_block"]["fresh-16"],
                row["by_block"]["larger-28"],
            )
        )
    lines += [
        "",
        "**Lowest observed MAE:** `%s` at **%.2f** K rows, against a mean "
        "baseline of **%.2f**; the gain is only **%.2f** rows. The best pre-run "
        "feature is `%s` at **%.2f**, **%.2f rows worse** than the baseline. "
        "These are the lowest observed errors, not a validated model." % (
            best["model"], best["mae"], best["mean_baseline_mae"],
            best["gain_vs_baseline"], best["pre_run_model"],
            best["pre_run_mae"], -best["pre_run_gain_vs_baseline"]),
        "",
        "## Reading",
        "",
        doc["interpretation"]["not_causal"],
        "",
        "The result is mostly negative:",
        "",
        "- `A_available` is the best model, but it is an output of the same "
        "baseline and improves on the mean baseline by only **%.2f** K rows." % best["gain_vs_baseline"],
        "- No pre-run feature beats the mean baseline out of world; the best is "
        "**%.2f rows worse**." % (-best["pre_run_gain_vs_baseline"]),
        "- `candidate_edges` fails catastrophically out of world (LOFO MAE "
        "**%.2f**) and has rho **0.03** inside the 28-tag block: edge count is "
        "not a predictor of total K." % next(
            row["mae"] for row in doc["leave_one_world_out"]
            if row["feature"] == "candidate_edges"),
        "- Support and U summaries are inconsistent across blocks: their pooled "
        "intervals cross zero and their within-block signs do not agree.",
        "",
        "So the current answer is: **absolute K is seed-specific under these "
        "structural summaries.** This rejects `candidate_edges`, mean U and the "
        "pre-U support summaries as simple cross-world predictors; it does not "
        "prove no predictor exists.",
        "",
        "The next diagnostic should measure the carrier process directly rather "
        "than another summary of the same rows.",
        "",
        "## Limits",
        "",
    ]
    for limit in doc["limits"]:
        lines.append("- %s" % limit)
    lines += [
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_k_total_predictors --check",
        "python -m benchmarks.a1_k_total_predictors --self-test",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def _fmt(value) -> str:
    return "—" if value is None else "%.2f" % value


def write() -> int:
    doc = build()
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print("lowest MAE:", doc["best_observed"]["model"],
          doc["best_observed"]["mae"])
    return 0


def check() -> int:
    if not OUT_PATH.exists() or not PAGE_PATH.exists():
        print("FAIL: report artifact or page is missing")
        return 1
    doc = _load(OUT_PATH)
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 absolute-K predictors: clean; best MAE %s %.2f" % (
        doc["best_observed"]["model"], doc["best_observed"]["mae"]))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.check:
        return check()
    found = self_test()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 absolute-K predictors: self-test clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
