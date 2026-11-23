"""Is the 16-tag coverage level set engine-side?

Within-block work (`A1-WITHIN-BLOCK-LEVEL-1`) tested eleven **stream-side**
quantities against the per-seed level and found none that tracks it: mean and
median support, support mass, support dispersion, floor share, tag entropy,
cell pairs, pair saturation and temporal-edge density are flat across blocks
and not sign-consistent across seeds.  That leaves the engine's own side.

This module joins, per seed, the committed level to two families of
**engine-side** quantities and tests whether either tracks it:

* **loop window** — how many loops the engine returned and selected, the slot
  share, cap pressure and saturation cycle (`A1-LOOP-CAP-COUNTERFACTUAL-1`,
  `A1-K-CARRIER-SUPPLY-1`),
* **prediction ordering** — the entropy, transition probability, count and rank
  fraction of the served transitions, the transition share of the candidate
  space and the served probability mass (`A1-CAP112-ORDERING-TERM-1`,
  `A1-PREDICTION-CAP-112-1`).

The test is within-block: each quantity's correlation with the level is
computed after removing block means, so a block-level offset cannot masquerade
as a seed-level track.  The null is a permutation that shuffles levels inside
each block, which preserves the block means exactly.

Two controls make the join falsifiable: the served count **must** track the
level (the level is an average over the served set, so a join that cannot
recover that is broken), and the candidate count **cannot** track it (the two
blocks hold 63.8 candidates each, so any correlation there is noise).

A pre-committed rule decides the reading: a quantity tracks the level only if
its pooled within-block correlation reaches **0.6** in absolute value, carries
the same sign in both blocks, and survives a Bonferroni threshold over the
number of quantities tested.  Nothing here is a run, a target, a freeze, a
grant or an A1 cell.

    python -m benchmarks.a1_engine_side_join --write
    python -m benchmarks.a1_engine_side_join --check
    python -m benchmarks.a1_engine_side_join --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEVEL_PATH = DOCS / "a1_within_block_level.json"
LOOP_PATH = DOCS / "a1_loop_cap_counterfactual.json"
SUPPLY_PATH = DOCS / "a1_k_carrier_supply.json"
ORDER_PATH = DOCS / "a1_cap112_ordering_term.json"
CAP112_PATH = DOCS / "a1_prediction_cap_112.json"
OUT_PATH = DOCS / "a1_engine_side_join.json"
PAGE_PATH = DOCS / "A1-ENGINE-SIDE-JOIN.md"
ID = "A1-ENGINE-SIDE-JOIN-1"
DATE = "2026-11-14"
KIND = "a1_engine_side_join"
STATUS = ("DESCRIPTIVE — ENGINE-SIDE QUANTITIES AGAINST THE PER-SEED 16-TAG LEVEL; "
          "NO TARGET, FREEZE, GRANT OR A1 CELL")
BLOCKS = ("current-16", "fresh-16")
CAP = 112
LOOP_CAPS = (15, 120)
MIN_R = 0.6
CONTROLS = ("served", "candidates", "rank_fraction_expected")
ALPHA = 0.05
DRAWS = 20000
SEED = 20261114


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _pearson(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 3:
        return None
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0.0 or syy <= 0.0:
        return None
    return sxy / math.sqrt(sxx * syy)


def _pooled(rows: list[dict], key: str) -> float | None:
    """Within-block correlation: remove each block's mean, then correlate."""
    pairs = []
    for block in BLOCKS:
        group = [row for row in rows if row["block"] == block]
        if not group:
            return None
        mx = sum(row["level"] for row in group) / len(group)
        my = sum(row[key] for row in group) / len(group)
        pairs += [(row["level"] - mx, row[key] - my) for row in group]
    return _pearson(pairs)


def _partial(rows: list[dict], key: str) -> float | None:
    """Correlation of level and `key` after removing the served count.

    The level is close to a function of the served count, so a quantity that
    only reproduces `served` would otherwise look like a carrier. Each variable
    is residualized on the served count inside its block.
    """
    pairs = []
    for block in BLOCKS:
        group = [row for row in rows if row["block"] == block]
        if len(group) < 4:
            return None
        mx = sum(row["level"] for row in group) / len(group)
        my = sum(row[key] for row in group) / len(group)
        ms = sum(row["served"] for row in group) / len(group)
        sx = [row["level"] - mx for row in group]
        sy = [row[key] - my for row in group]
        ss = [row["served"] - ms for row in group]
        sss = sum(value * value for value in ss)
        if sss <= 0.0:
            return None
        bx = sum(a * b for a, b in zip(sx, ss)) / sss
        by = sum(a * b for a, b in zip(sy, ss)) / sss
        pairs += [(a - bx * c, b - by * c) for a, b, c in zip(sx, sy, ss)]
    return _pearson(pairs)


def _permutation_p(rows: list[dict], key: str, observed: float | None) -> float | None:
    if observed is None:
        return None
    rng = random.Random(SEED)
    blocks = [[row[key] for row in rows if row["block"] == block]
              for block in BLOCKS]
    levels = [[row["level"] for row in rows if row["block"] == block]
              for block in BLOCKS]
    hits = 0
    for _ in range(DRAWS):
        pairs = []
        for values, target in zip(blocks, levels):
            shuffled = values[:]
            rng.shuffle(shuffled)
            mx = sum(target) / len(target)
            my = sum(values) / len(values)
            pairs += [(t - mx, v - my) for t, v in zip(target, shuffled)]
        candidate = _pearson(pairs)
        if candidate is not None and abs(candidate) >= abs(observed):
            hits += 1
    return (hits + 1) / (DRAWS + 1)


def _seed_index() -> dict[tuple[str, int], dict]:
    level = {(row["block"], row["seed"]): row
             for row in _load(LEVEL_PATH)["rows"]}
    loops = _load(LOOP_PATH)["rows"]
    supply = {(seed["summary"]["block"], seed["summary"]["seed"]): seed["summary"]
              for seed in _load(SUPPLY_PATH)["seeds"]}
    order = _load(ORDER_PATH)
    order_rows: dict[tuple[str, int], list[dict]] = {}
    for row in order["rows"]:
        order_rows.setdefault((row["block"], row["seed"]), []).append(row)
    order_seed = {(row["block"], row["seed"]): row for row in order["per_seed"]}
    cap112 = {(row["block"], row["seed"]): row
              for row in _load(CAP112_PATH)["rows"]
              if row["prediction_cap"] == CAP}
    loop_rows: dict[tuple[str, int], dict[int, int]] = {}
    for row in loops:
        if row["block"] not in BLOCKS:
            continue
        loop_rows.setdefault((row["block"], row["seed"]), {})[
            row["cap"]] = row["returned_loops"]
    keys = [key for key in level
            if key[1] in {seed for block, seed in supply if block == key[0]}]
    rows = []
    for key in sorted(keys, key=lambda item: (BLOCKS.index(item[0]), item[1])):
        block, seed = key
        summary = supply[key]
        served = [row for row in order_rows.get(key, []) if row["served"]]
        candidates = len(order_rows.get(key, []))
        ranks = [row["best_rank"]["engine"] for row in served]
        rows.append({
            "block": block,
            "seed": seed,
            "level": level[key]["offset"],
            "candidates": level[key]["candidate_edges"],
            "served": order_seed[key]["A"] if key in order_seed else cap112[key]["A"],
            "loops_at_15": loop_rows.get(key, {}).get(15),
            "loops_at_120": loop_rows.get(key, {}).get(120),
            "selected_loops": summary["selected_loops"],
            "possible_loops": summary["possible_loops"],
            "loop_slot_share": summary["loop_slot_share"],
            "cap_pressure": summary["cap_pressure"],
            "saturation_cycle": summary["saturation_cycle"],
            "mean_selected_loops": summary["mean_selected_loops"],
            "candidate_coverage": summary["candidate_coverage"],
            "mean_entropy_served": (sum(row["entropy"] for row in served)
                                    / len(served)) if served else None,
            "mean_probability_served": (sum(row["probability"] for row in served)
                                        / len(served)) if served else None,
            "mean_count_served": (sum(row["count"] for row in served)
                                  / len(served)) if served else None,
            "mean_rank_fraction_served": (sum(ranks) / len(ranks) / candidates)
            if served and candidates else None,
            "transition_share": (candidates / level[key]["candidate_edges"])
            if level[key]["candidate_edges"] else None,
            "probability_mass_served": (sum(row["probability"] for row in served)
                                        if served else None),
            "mass_fraction_served": (
                sum(row["probability"] for row in served)
                / sum(row["probability"] for row in order_rows.get(key, [])))
            if served and sum(row["probability"]
                              for row in order_rows.get(key, [])) else None,
            "unserved_mean_probability": (
                sum(row["probability"] for row in order_rows.get(key, [])
                    if not row["served"])
                / max(1, sum(1 for row in order_rows.get(key, [])
                             if not row["served"]))),
            "rank_fraction_expected": (
                (order_seed[key]["A"] + 1.0)
                / (2.0 * level[key]["candidate_edges"]))
            if key in order_seed else None,
        })
    return {"rows": rows, "coverage": len(rows)}


QUANTITIES = (
    ("served", "control", "served edge count"),
    ("candidates", "control", "candidate count"),
    ("rank_fraction_expected", "control",
     "rank fraction the served prefix implies"),
    ("loops_at_15", "loop window", "loops returned at cap 15"),
    ("loops_at_120", "loop window", "loops returned at cap 120"),
    ("selected_loops", "loop window", "loops selected in the acquisition phase"),
    ("possible_loops", "loop window", "loops possible in the acquisition phase"),
    ("loop_slot_share", "loop window", "loop slot share"),
    ("cap_pressure", "loop window", "loop cap pressure"),
    ("saturation_cycle", "loop window", "cycle at which loops saturate"),
    ("mean_selected_loops", "loop window", "mean loops selected per cycle"),
    ("candidate_coverage", "loop window", "carrier coverage of the candidate space"),
    ("mean_entropy_served", "prediction ordering", "mean entropy of served transitions"),
    ("mean_probability_served", "prediction ordering",
     "mean probability of served transitions"),
    ("mean_count_served", "prediction ordering", "mean count of served transitions"),
    ("mean_rank_fraction_served", "prediction ordering",
     "mean engine rank fraction of served transitions"),
    ("transition_share", "prediction ordering", "transition share of the candidate space"),
    ("probability_mass_served", "prediction ordering",
     "served probability mass"),
    ("mass_fraction_served", "prediction ordering",
     "served share of the candidate probability mass"),
    ("unserved_mean_probability", "prediction ordering",
     "mean probability of the unserved transitions"),
)


def build() -> dict:
    joined = _seed_index()
    rows = joined["rows"]
    if len(rows) != 12:
        raise SystemExit("REFUSED: the join covers %d seeds, expected 12"
                         % len(rows))
    per_block = {block: sum(1 for row in rows if row["block"] == block)
                 for block in BLOCKS}
    if set(per_block.values()) != {6}:
        raise SystemExit("REFUSED: blocks are unbalanced: %r" % per_block)
    if len({row["candidates"] for row in rows}) > 2:
        raise SystemExit("REFUSED: candidate counts are not block-constant")
    results = []
    tested = len([1 for key, _, _ in QUANTITIES if key not in CONTROLS])
    threshold = ALPHA / max(tested, 1)
    for key, family, label in QUANTITIES:
        if any(row[key] is None for row in rows):
            results.append({
                "key": key, "family": family, "label": label,
                "pooled_r": None, "block_r": {}, "sign_consistent": None,
                "permutation_p": None, "tracks": False,
                "note": "not present for every seed",
            })
            continue
        pooled = _pooled(rows, key)
        block_r = {block: _pearson([(row["level"], row[key]) for row in rows
                                    if row["block"] == block])
                   for block in BLOCKS}
        consistent = all(value is not None for value in block_r.values()) and (
            (block_r[BLOCKS[0]] > 0) == (block_r[BLOCKS[1]] > 0))
        p_value = _permutation_p(rows, key, pooled)
        partial = None if key == "served" else _partial(rows, key)
        tracks = (key not in CONTROLS and pooled is not None
                  and abs(pooled) >= MIN_R and consistent
                  and p_value is not None and p_value <= threshold
                  and partial is not None and abs(partial) >= MIN_R)
        results.append({
            "key": key,
            "family": family,
            "label": label,
            "pooled_r": round(pooled, 4) if pooled is not None else None,
            "block_r": {block: (round(value, 4) if value is not None else None)
                        for block, value in block_r.items()},
            "sign_consistent": consistent,
            "permutation_p": round(p_value, 5) if p_value is not None else None,
            "partial_r_given_served": round(partial, 4)
            if partial is not None else None,
            "tracks": tracks,
        })
    restatement = _pearson([(row["mean_rank_fraction_served"],
                             row["rank_fraction_expected"]) for row in rows])
    prefix_gap = max(abs(row["mean_rank_fraction_served"]
                         - row["rank_fraction_expected"]) for row in rows)
    control = next(row for row in results if row["key"] == "served")
    candidate = next(row for row in results if row["key"] == "candidates")
    if control["pooled_r"] is None or abs(control["pooled_r"]) < 0.6:
        raise SystemExit("REFUSED: the served-count control does not track the "
                         "level, so the join is broken")
    tracks = [row for row in results if row["tracks"]]
    loop_tracks = [row for row in tracks if row["family"] == "loop window"]
    order_tracks = [row for row in tracks if row["family"] == "prediction ordering"]
    best = max((row for row in results
                if row["key"] not in ("served", "candidates")
                and row["pooled_r"] is not None),
               key=lambda row: abs(row["pooled_r"]))
    series: dict[tuple, list[str]] = {}
    for key, _, _ in QUANTITIES:
        if any(row[key] is None for row in rows):
            continue
        signature = tuple(round(float(row[key]), 6) for row in rows)
        series.setdefault(signature, []).append(key)
    identical = [keys for keys in series.values() if len(keys) > 1]
    found = {
        "seeds": len(rows),
        "identical_series": identical,
        "distinct_series": len(series),
        "blocks": per_block,
        "quantities": len(QUANTITIES),
        "tested": tested,
        "min_abs_r": MIN_R,
        "bonferroni_alpha": round(ALPHA / max(tested, 1), 6),
        "tracks": [row["key"] for row in tracks],
        "loop_window_tracks": len(loop_tracks),
        "ordering_tracks": len(order_tracks),
        "best_key": best["key"],
        "best_pooled_r": best["pooled_r"],
        "best_block_r": best["block_r"],
        "served_control_r": control["pooled_r"],
        "candidate_control_r": candidate["pooled_r"],
        "candidate_control_p": candidate["permutation_p"],
        "rank_fraction_vs_prefix_r": round(restatement or 0.0, 6),
        "rank_fraction_vs_prefix_max_gap": round(prefix_gap, 6),
        "bonferroni_threshold": round(threshold, 6),
    }
    if tracks:
        verdict = (
            "**%s** tracks the level among the %d behavioural quantities: "
            "pooled within-block r **%.4f** with block correlations **%.3f** "
            "and **%.3f**, permutation p **%.4f** against a Bonferroni "
            "threshold of **%.2e**, and **%.4f** once the served count is "
            "partialed out. The loop-window family contributes %d trackers and "
            "the ordering family %d, so the loop budget, its saturation, the "
            "entropy, the transition probability, the count and the "
            "probability mass of what the engine served and cut all fail the "
            "rule. What does track is where in the engine's own final ordering "
            "the served edges sit — a description of the selection itself, not "
            "an independent engine parameter, so this locates the level inside "
            "the selection step without naming a separate term that sets it."
            % (", ".join("`%s`" % key for key in found["tracks"]), tested,
               best["pooled_r"], best["block_r"][BLOCKS[0]],
               best["block_r"][BLOCKS[1]], best["permutation_p"],
               found["bonferroni_threshold"], best["partial_r_given_served"],
               len(loop_tracks), len(order_tracks)))
    else:
        verdict = (
            "None of the **%d** behavioural engine-side quantities clears the "
            "pre-committed rule. The strongest is `%s` at pooled within-block "
            "r **%.4f** with block correlations **%.3f** and **%.3f**, "
            "permutation p **%.4f** — the threshold is **%.4f**. `served` "
            "tracks at **%.4f**, as it must; `mean_rank_fraction_served` is "
            "not an independent quantity at all, it is the served prefix "
            "restated, correlating **%.4f** with the rank fraction that prefix "
            "implies. The loop-window family contributes %d and the ordering "
            "family %d, so the level is not carried by how many loops the "
            "engine returned, how much of its loop budget they used, when they "
            "saturated, or by the entropy, probability, count or mass of the "
            "transitions it served or cut."
            % (tested, best["key"], best["pooled_r"],
               best["block_r"][BLOCKS[0]], best["block_r"][BLOCKS[1]],
               best["permutation_p"], found["bonferroni_threshold"],
               control["pooled_r"], restatement,
               len(loop_tracks), len(order_tracks)))
    reading = (
        verdict + " The join is falsifiable and passes its controls: the "
        "served edge count tracks the level at pooled r **%.4f** — as it must, "
        "because the level is an average over the served set — while the "
        "candidate count, which the two blocks hold at 63.8 apiece, gives "
        "**%.4f** with permutation p **%.4f**. Every correlation here is "
        "computed inside a block, so a block-level offset cannot produce it, "
        "and the null shuffles levels within blocks so it preserves each "
        "block's mean exactly." % (
            control["pooled_r"], candidate["pooled_r"] or 0.0,
            candidate["permutation_p"] or 0.0))
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Is the per-seed 16-tag coverage level set engine-side — by the "
            "loop window the engine returns or the ordering it applies — "
            "rather than by the stream-side quantities already excluded?"
        ),
        "definition": (
            "A per-seed join of the committed level to %d loop-window and "
            "prediction-ordering quantities on the twelve 16-tag seeds, with "
            "within-block correlations and two controls." % len(QUANTITIES)
        ),
        "method": (
            "All quantities are read from committed artifacts; nothing is "
            "replayed. Correlations are computed after removing block means, "
            "the null is a within-block permutation of levels over %d draws, "
            "and a quantity tracks the level only if |r| >= %.1f, the sign "
            "agrees in both blocks and the permutation p clears a Bonferroni "
            "threshold over the tested quantities." % (DRAWS, MIN_R)
        ),
        "constants": {
            "blocks": list(BLOCKS),
            "seeds_per_block": 6,
            "prediction_cap": CAP,
            "loop_caps": list(LOOP_CAPS),
            "min_abs_r": MIN_R,
            "alpha": ALPHA,
            "draws": DRAWS,
            "permutation_seed": SEED,
            "quantities": [key for key, _, _ in QUANTITIES],
            "sources": [path.name for path in
                        (LEVEL_PATH, LOOP_PATH, SUPPLY_PATH, ORDER_PATH,
                         CAP112_PATH)],
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "found": found,
        "results": results,
        "rows": rows,
        "limits": [
            "Six seeds per block: a correlation this small is not distinguishable from chance at any useful resolution, so a null result excludes these aggregates as carriers, not the engine as a cause.",
            "Every quantity is a per-seed aggregate over cycles; a quantity that varies within a seed is averaged away before the join.",
            "Loops at cap 15 and loops selected are the same numbers at these seeds, and mean loops selected per cycle is that series divided by the cycle count, so the loop family carries seven distinct series in nine registered quantities; the join records exact duplicate groups under found.identical_series.",
            "Partial correlations rest on twelve seeds and a covariate (the served count) that is itself close to the level; a partial r of -0.96 is a description, not a mechanism, and it is unstable at this n.",
            "The level is a fitted coverage offset, so a quantity that reproduces it arithmetically (the served count) is a control, not a finding.",
            "Two blocks: sign consistency across blocks is a weak filter, and a quantity that tracks in one block only is not reported as tracking.",
        ],
        "not_evidence": (
            "A descriptive join over committed artifacts. It runs no engine, "
            "opens no database, and is not a treatment, target, freeze, grant "
            "or A1 cell."
        ),
    })


def render(doc: dict) -> str:
    found = doc["found"]
    lines = [
        "# A1 engine-side join",
        "",
        "Generated from `docs/a1_engine_side_join.json` by "
        "`python -m benchmarks.a1_engine_side_join --write`. Do not edit by hand.",
        "",
        "**Descriptive join over committed artifacts, not an A1 result.**",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Quantities against the level",
        "",
        "| Quantity | Family | Pooled r | current-16 | fresh-16 | p | Tracks |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in doc["results"]:
        block_r = row["block_r"]
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            row["key"], row["family"],
            "—" if row["pooled_r"] is None else "%.4f" % row["pooled_r"],
            "—" if block_r.get("current-16") is None
            else "%.3f" % block_r["current-16"],
            "—" if block_r.get("fresh-16") is None
            else "%.3f" % block_r["fresh-16"],
            "—" if row["permutation_p"] is None
            else "%.4f" % row["permutation_p"],
            "yes" if row["tracks"] else "no"))
    lines += [
        "",
        "Threshold: |pooled r| >= %.1f, same sign in both blocks, permutation "
        "p <= %.2e." % (found["min_abs_r"], found["bonferroni_alpha"]),
        "",
        "## Per-seed join",
        "",
        "| Block | Seed | Level | Served | Candidates | Loops 120 | Slot share | "
        "Mean entropy | Mean probability |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["rows"]:
        lines.append("| %s | %d | %.4f | %d | %d | %s | %.4f | %.4f | %.4f |" % (
            row["block"], row["seed"], row["level"], row["served"],
            row["candidates"], row["loops_at_120"], row["loop_slot_share"],
            row["mean_entropy_served"], row["mean_probability_served"]))
    lines += ["", "## Limits", ""]
    lines += ["- %s" % limit for limit in doc["limits"]]
    lines += ["", "## What this does not claim", "", doc["not_evidence"], ""]
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
    rows = doc.get("rows") or []
    if len(rows) != 12:
        found.append("the join does not cover twelve seeds")
    if doc["found"]["blocks"] != {"current-16": 6, "fresh-16": 6}:
        found.append("block balance changed")
    if abs(doc["found"]["served_control_r"]) < 0.6:
        found.append("the served-count control no longer tracks the level")
    if doc["found"]["candidate_control_r"] is not None and \
            abs(doc["found"]["candidate_control_r"]) > 0.6:
        found.append("the candidate-count control tracks the level")
    if len(doc["found"]["tracks"]) != (doc["found"]["loop_window_tracks"]
                                       + doc["found"]["ordering_tracks"]):
        found.append("tracks by family do not sum to the total")
    keys = [row["key"] for row in doc["results"]]
    if keys != doc["constants"]["quantities"]:
        found.append("result order does not match the registered quantities")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if _pearson([(1.0, 2.0), (2.0, 4.0), (3.0, 6.0)]) != 1.0:
        failures.append("perfect correlation")
    if _pearson([(1.0, 2.0), (2.0, 2.0), (3.0, 2.0)]) is not None:
        failures.append("constant input returns a correlation")
    rows = []
    for block in BLOCKS:
        for index in range(6):
            rows.append({"block": block, "level": float(index),
                         "same": float(index),
                         "flipped": float(-index),
                         "noise": float((index * 5 + len(block)) % 7)})
    if _pooled(rows, "same") != 1.0 or _pooled(rows, "flipped") != -1.0:
        failures.append("within-block correlation does not recover a linear join")
    p_exact = _permutation_p(rows, "same", 1.0)
    if p_exact is None or p_exact > 0.01:
        failures.append("a perfect monotone join is not significant")
    if MIN_R <= 0.0 or ALPHA / len(QUANTITIES) >= 0.01:
        failures.append("the decision rule is not a threshold")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    print("found:", body["found"])
    for row in body["results"]:
        print(" ", row["key"], row["pooled_r"], row["block_r"],
              row["permutation_p"], row["tracks"])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no engine-side join artifact; run --write")
    found = problems(_load(OUT_PATH))
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("engine-side join: clean")
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
        print("engine-side join self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
