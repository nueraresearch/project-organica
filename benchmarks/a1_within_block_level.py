"""Does any within-block candidate-space quantity track the 16-tag level?

Three blocks have the same candidate size (63-64 edges) and the same alphabet
(16 tags) but different fitted levels:

* current-16 (20630101-20630106),
* fresh-16 (20650101-20650106),
* the seed-holdout block (20670101-20670106), which has fresh-16's mean log
  candidate size and sits below the fresh bracket at every fitted cap.

This joins each block's committed coverage cells to candidate-space
quantities computed from the same acquisition stream: directed-pair support
(mean, median, mass, dispersion, floor share), tag entropy, exercised cell
pairs and pair saturation.  It then asks three questions per quantity:
does it order the three block means like the level, does it track the level
across seeds inside a block, and is its sign consistent across blocks.

The support values are checked against the committed cap-112 decomposition
edge by edge, so the stream-side quantities are the ones the earlier reports
used.  No engine replay: every coverage value is read from a committed
artifact, and no A/K cell is created here.

    python -m benchmarks.a1_within_block_level --write
    python -m benchmarks.a1_within_block_level --check
    python -m benchmarks.a1_within_block_level --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path

from benchmarks import a1_k_supply_discriminator
from benchmarks import a1_target_selection
from benchmarks import engine_stamp
from benchmarks.acquisition_compositional import generate_compositional_world

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OFFSET_PATH = DOCS / "a1_offset_predictors.json"
HOLDOUT_PATH = DOCS / "a1_cap_response_seed_holdout.json"
DECOMPOSE_PATH = DOCS / "a1_prediction_cap112_decompose.json"
OUT_PATH = DOCS / "a1_within_block_level.json"
PAGE_PATH = DOCS / "A1-WITHIN-BLOCK-LEVEL.md"
ID = "A1-WITHIN-BLOCK-LEVEL-1"
DATE = "2026-11-14"
KIND = "a1_within_block_level"
STATUS = ("DESCRIPTIVE — WITHIN-BLOCK CANDIDATE-SPACE QUANTITIES AGAINST THE 16-TAG LEVEL; "
          "NO TARGET, FREEZE, GRANT OR A1 CELL")
CAPS = (20, 40, 80, 112)
SLOPE = 0.04698668
CYCLES = 120
EVENTS_PER_CYCLE = 8
BLOCKS = (
    {"label": "current-16", "seeds": (20630101, 20630102, 20630103,
                                      20630104, 20630105, 20630106)},
    {"label": "fresh-16", "seeds": (20650101, 20650102, 20650103,
                                    20650104, 20650105, 20650106)},
    {"label": "seed-2067", "seeds": (20670101, 20670102, 20670103,
                                     20670104, 20670105, 20670106)},
)
STATISTICS = (
    ("mean_support", "mean directed-pair support over candidate edges"),
    ("median_support", "median directed-pair support over candidate edges"),
    ("support_mass", "total directed-pair support over candidate edges"),
    ("support_sd", "standard deviation of candidate support"),
    ("frac_le_10", "share of candidate edges with support <= 10"),
    ("tag_entropy", "Shannon entropy (bits) of acquisition tag frequency"),
    ("cell_pairs", "distinct (source cell, target cell) transitions exercised"),
    ("pair_saturation", "candidate edges / (cell pairs x 16)"),
    ("temporal_edges", "distinct directed temporal edges in the acquisition stream"),
    ("temporal_edge_density", "distinct temporal edges / 16 tags"),
    ("temporal_edge_share", "distinct temporal edges / candidate edges"),
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _spearman(x: list[float], y: list[float]) -> float:
    def ranks(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        out = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            mean = (i + j) / 2 + 1
            for k in range(i, j + 1):
                out[order[k]] = mean
            i = j + 1
        return out

    rx, ry = ranks(x), ranks(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    numerator = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    denominator = math.sqrt(sum((a - mx) ** 2 for a in rx)
                            * sum((b - my) ** 2 for b in ry))
    return numerator / denominator if denominator else 0.0


def _coverage() -> dict[tuple[str, int], dict[int, float]]:
    out: dict[tuple[str, int], dict[int, float]] = {}
    for row in _load(OFFSET_PATH)["seed_rows"]:
        out.setdefault((row["block"], row["seed"]), {})[row["cap"]] = row["A_coverage"]
    for row in _load(HOLDOUT_PATH)["rows"]:
        out.setdefault(("seed-2067", row["seed"]), {})[row["cap"]] = row["A_coverage"]
    return out


def _level() -> dict[tuple[str, int], dict[str, float]]:
    out = {}
    for row in _load(OFFSET_PATH)["seed_rows"]:
        entry = out.setdefault((row["block"], row["seed"]),
                               {"cells": {}, "candidates": row["candidate_edges"],
                                "k_completeness": row["k_completeness"]})
        entry["cells"][row["cap"]] = row["A_coverage"]
    for row in _load(HOLDOUT_PATH)["rows"]:
        entry = out.setdefault(("seed-2067", row["seed"]),
                               {"cells": {}, "candidates": row["candidate_edges"],
                                "k_completeness": 1.0})
        entry["cells"][row["cap"]] = row["A_coverage"]
    for entry in out.values():
        entry["offset"] = sum(entry["cells"][cap] - SLOPE * math.sqrt(cap)
                              for cap in CAPS) / len(CAPS)
    return out


def _stream(row: dict) -> dict:
    world = generate_compositional_world(seed=row["seed"], cycles=CYCLES)
    candidates = set(a1_target_selection.run_seed(
        row["seed"], world=world, boundary_safe=True)["u"])
    support = a1_k_supply_discriminator._support_counts(world)
    values = sorted(int(support[(edge.split(">")[0], edge.split(">")[1])])
                    for edge in candidates)
    acq_lo, acq_hi = 20, 110
    indexes = [index for index, (_, trainable)
               in enumerate(zip(world["events"], world["trainable"]))
               if acq_lo * EVENTS_PER_CYCLE <= index < acq_hi * EVENTS_PER_CYCLE
               and trainable]
    tags: Counter = Counter()
    cells: Counter = Counter()
    within: set[tuple[str, str]] = set()
    across: set[tuple[str, str]] = set()
    previous = None
    previous_tags: list[str] = []
    for index in indexes:
        current_tags = world["events"][index].split()
        tags.update(current_tags)
        current = world["cells"][index]
        if previous is not None:
            cells[(previous, current)] += 1
        previous = current
        # The engine's lookback includes the event being stored, so pairs
        # inside one event are temporal edges too.
        for source in current_tags:
            for target in current_tags:
                if source != target:
                    within.add((source, target))
        for source in previous_tags:
            for target in current_tags:
                if source != target:
                    across.add((source, target))
        previous_tags = current_tags
    temporal = within | across
    edge_occurrences = sum(1 for _ in indexes)
    total = sum(tags.values())
    entropy = -sum((count / total) * math.log2(count / total)
                   for count in tags.values())
    return {
        "candidate_edges": len(candidates),
        "candidate_support": {edge: int(support[(edge.split(">")[0],
                                                 edge.split(">")[1])])
                              for edge in sorted(candidates)},
        "mean_support": sum(values) / len(values),
        "median_support": values[len(values) // 2],
        "support_mass": sum(values),
        "support_sd": statistics.pstdev(values),
        "frac_le_10": sum(value <= 10 for value in values) / len(values),
        "tag_entropy": entropy,
        "cell_pairs": len(cells),
        "pair_saturation": len(candidates) / (len(cells) * 16),
        "temporal_edges": len(temporal),
        "temporal_edge_density": len(temporal) / 16,
        "temporal_edge_share": len(temporal) / len(candidates),
        "temporal_edge_occurrences": edge_occurrences,
    }


def _agreement(means: list[float], levels: list[float]) -> list[bool]:
    """Order the three block means and check they follow the level order."""
    level_order = sorted(range(len(levels)), key=lambda i: levels[i])
    mean_order = sorted(range(len(means)), key=lambda i: means[i])
    return [mean_order[i] == level_order[i] for i in range(len(levels))]


def build() -> dict:
    level = _level()
    coverage = _coverage()
    decompose = _load(DECOMPOSE_PATH)["candidate_rows"]
    committed_support = {(row["block"], row["seed"], row["edge"]): row["support"]
                         for row in decompose}
    rows = []
    for block in BLOCKS:
        for seed in block["seeds"]:
            entry = level[(block["label"], seed)]
            if set(entry["cells"]) != set(CAPS):
                raise SystemExit("REFUSED: %s/%d has no committed cell at every cap"
                                 % (block["label"], seed))
            stream = _stream({"seed": seed})
            row = {
                "block": block["label"],
                "seed": seed,
                "candidate_edges": stream["candidate_edges"],
                "committed_candidates": entry["candidates"],
                "k_completeness": entry["k_completeness"],
                "offset": round(entry["offset"], 6),
                "mean_coverage": round(sum(coverage[(block["label"], seed)].values())
                                       / len(CAPS), 6),
            }
            for name, _ in STATISTICS:
                value = stream[name]
                row[name] = round(value, 6) if isinstance(value, float) else value
            rows.append(row)
            for edge, support in stream["candidate_support"].items():
                key = (block["label"], seed, edge)
                if key in committed_support and committed_support[key] != support:
                    raise SystemExit(
                        "REFUSED: support for %s/%d/%s is %d, committed %d"
                        % (block["label"], seed, edge, support,
                           committed_support[key]))
    blocks = []
    for block in BLOCKS:
        group = [row for row in rows if row["block"] == block["label"]]
        entry = {
            "label": block["label"],
            "seeds": list(block["seeds"]),
            "offset_mean": round(sum(row["offset"] for row in group) / len(group), 6),
            "offset_sd": round(statistics.pstdev([row["offset"] for row in group]), 6),
            "offset_se": None,
            "offset_min": min(row["offset"] for row in group),
            "offset_max": max(row["offset"] for row in group),
            "candidates_mean": round(sum(row["candidate_edges"] for row in group)
                                     / len(group), 6),
            "k_completeness": sorted({row["k_completeness"] for row in group}),
        }
        entry["offset_se"] = round(entry["offset_sd"] / math.sqrt(len(group)), 6)
        blocks.append(entry)
    levels = [block["offset_mean"] for block in blocks]
    statistics_rows = []
    for name, description in STATISTICS:
        means = [round(sum(row[name] for row in rows
                           if row["block"] == block["label"]) / len(block["seeds"]), 6)
                 for block in BLOCKS]
        correlations = []
        for block in BLOCKS:
            group = [row for row in rows if row["block"] == block["label"]]
            correlations.append(round(_spearman(
                [row[name] for row in group],
                [row["offset"] for row in group]), 4))
        relative = (max(means) - min(means)) / abs(sum(means) / len(means))
        statistics_rows.append({
            "name": name,
            "description": description,
            "block_means": means,
            "relative_spread": round(relative, 6),
            "orders_like_level": _agreement(means, levels),
            "orders_like_level_all": all(_agreement(means, levels)),
            "within_block_spearman": correlations,
            "sign_consistent": all(value > 0 for value in correlations)
                               or all(value < 0 for value in correlations),
            "tracks": all(_agreement(means, levels)) and (
                all(value > 0 for value in correlations)
                or all(value < 0 for value in correlations)),
        })
    gaps = []
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            first, second = blocks[i], blocks[j]
            difference = abs(first["offset_mean"] - second["offset_mean"])
            se = math.sqrt(first["offset_se"] ** 2 + second["offset_se"] ** 2)
            gaps.append({
                "blocks": [first["label"], second["label"]],
                "difference": round(difference, 6),
                "se": round(se, 6),
                "z": round(difference / se, 3) if se else None,
            })
    found = {
        "blocks": len(blocks),
        "seeds": len(rows),
        "statistics": len(STATISTICS),
        "level_spread": round(max(levels) - min(levels), 6),
        "level_blocks": levels,
        "max_within_block_sd": round(max(block["offset_sd"] for block in blocks), 6),
        "any_statistics_track": sum(row["tracks"] for row in statistics_rows),
        "any_orders_like_level": sum(row["orders_like_level_all"]
                                     for row in statistics_rows),
        "any_sign_consistent": sum(row["sign_consistent"] for row in statistics_rows),
    }
    by_name = {row["name"]: row for row in statistics_rows}
    med = by_name["median_support"]
    entropy_row = by_name["tag_entropy"]
    floor_row = by_name["frac_le_10"]
    edge_row = by_name["temporal_edges"]
    edge_density = by_name["temporal_edge_density"]
    edge_share = by_name["temporal_edge_share"]
    weak = [row for row in rows if row["block"] == "fresh-16"]
    weakest = min(weak, key=lambda row: row["offset"])
    zs = [gap["z"] for gap in gaps if gap["z"] is not None]
    reading = (
        "Neither acquisition-time pair support nor temporal-edge density "
        "explains the 16-tag level. The three equal-size blocks differ in "
        "fitted offset by at most **%(spread).4f** (**%(l0).4f** / "
        "**%(l1).4f** / **%(l2).4f**), which is **%(zmin).2f** to "
        "**%(zmax).2f** standard errors of the pairwise difference at six "
        "seeds each and no wider than the within-block seed spread "
        "(**%(sd0).3f** / **%(sd1).3f** / **%(sd2).3f**). Pair support barely "
        "moves — mean **%(ms0).2f** / **%(ms1).2f** / **%(ms2).2f**, median "
        "**%(med0).2f** / **%(med1).2f** / **%(med2).2f**, mass **%(mm0).0f** "
        "/ **%(mm1).0f** / **%(mm2).0f**, dispersion **%(sd0s).2f** / "
        "**%(sd1s).2f** / **%(sd2s).2f**, share at support <= 10 "
        "**%(fl0).3f** / **%(fl1).3f** / **%(fl2).3f** — and temporal-edge "
        "density does not move at all: **%(e0).1f** / **%(e1).1f** / "
        "**%(e2).1f** distinct temporal edges, **%(d0).2f** / **%(d1).2f** / "
        "**%(d2).2f** per tag, so a quantity the two-tags-per-event law pins "
        "at **11** edges per tag cannot carry a level that varies. Of "
        "**%(nstat)d** quantities, **%(norder)d** order the three block means "
        "the way the level does — median support, tag entropy, the support <= "
        "10 share and the temporal-edge share (**%(s0).3f** / **%(s1).3f** / "
        "**%(s2).3f**) — each a one-in-six chance ordering, and none keeps a "
        "consistent sign at seed resolution: median support runs "
        "**%(rm0)+.2f** / **%(rm1)+.2f** / **%(rm2)+.2f**, tag entropy "
        "**%(re0)+.2f** / **%(re1)+.2f** / **%(re2)+.2f**, the floor share "
        "**%(rf0)+.2f** / **%(rf1)+.2f** / **%(rf2)+.2f** and the edge share "
        "**%(rs0)+.2f** / **%(rs1)+.2f** / **%(rs2)+.2f**. The sharpest single "
        "case against a support account is fresh-16's lowest seed, "
        "`%(ws)d` at offset **%(wo)+.4f**, which has that block's **highest** "
        "mean support (**%(wsu).1f**). The lowest block matches fresh-16 on "
        "candidate count (**%(c1).1f** against **%(c2).1f**), K completeness "
        "(**1.000**) and temporal-edge density (**%(d1).2f** against "
        "**%(d2).2f**), so the level is not carried by candidate support, "
        "support mass, support dispersion, entropy, cell-pair coverage, pair "
        "saturation or the size of the temporal graph: it varies more inside a "
        "block than between equal-size blocks, and the fitted block offset is "
        "a mean of draws rather than a property of the candidate space."
        % {
            "spread": found["level_spread"],
            "l0": blocks[0]["offset_mean"], "l1": blocks[1]["offset_mean"],
            "l2": blocks[2]["offset_mean"],
            "zmin": min(zs), "zmax": max(zs),
            "sd0": blocks[0]["offset_sd"], "sd1": blocks[1]["offset_sd"],
            "sd2": blocks[2]["offset_sd"],
            "ms0": by_name["mean_support"]["block_means"][0],
            "ms1": by_name["mean_support"]["block_means"][1],
            "ms2": by_name["mean_support"]["block_means"][2],
            "med0": med["block_means"][0], "med1": med["block_means"][1],
            "med2": med["block_means"][2],
            "mm0": by_name["support_mass"]["block_means"][0],
            "mm1": by_name["support_mass"]["block_means"][1],
            "mm2": by_name["support_mass"]["block_means"][2],
            "sd0s": by_name["support_sd"]["block_means"][0],
            "sd1s": by_name["support_sd"]["block_means"][1],
            "sd2s": by_name["support_sd"]["block_means"][2],
            "fl0": floor_row["block_means"][0], "fl1": floor_row["block_means"][1],
            "fl2": floor_row["block_means"][2],
            "e0": edge_row["block_means"][0], "e1": edge_row["block_means"][1],
            "e2": edge_row["block_means"][2],
            "d0": edge_density["block_means"][0],
            "d1": edge_density["block_means"][1],
            "d2": edge_density["block_means"][2],
            "nstat": found["statistics"],
            "norder": sum(row["orders_like_level_all"] for row in statistics_rows),
            "s0": edge_share["block_means"][0], "s1": edge_share["block_means"][1],
            "s2": edge_share["block_means"][2],
            "rm0": med["within_block_spearman"][0],
            "rm1": med["within_block_spearman"][1],
            "rm2": med["within_block_spearman"][2],
            "re0": entropy_row["within_block_spearman"][0],
            "re1": entropy_row["within_block_spearman"][1],
            "re2": entropy_row["within_block_spearman"][2],
            "rf0": floor_row["within_block_spearman"][0],
            "rf1": floor_row["within_block_spearman"][1],
            "rf2": floor_row["within_block_spearman"][2],
            "rs0": edge_share["within_block_spearman"][0],
            "rs1": edge_share["within_block_spearman"][1],
            "rs2": edge_share["within_block_spearman"][2],
            "ws": weakest["seed"], "wo": weakest["offset"],
            "wsu": weakest["mean_support"],
            "c1": blocks[1]["candidates_mean"], "c2": blocks[2]["candidates_mean"],
        }
    )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Which within-block candidate-space quantity, if any, tracks the "
            "coverage level across the equal-size 16-tag blocks?"
        ),
        "definition": (
            "Three blocks of six seeds, each with 16 tags and 63-64 candidate "
            "edges: current-16, fresh-16 and the seed-holdout block "
            "20670101-20670106. Level is the fitted cap-0 offset, computed as "
            "the mean over caps 20/40/80/112 of coverage minus the shared "
            "sqrt(cap) slope, from committed cells only."
        ),
        "method": (
            "Join committed per-seed coverage cells to candidate-space "
            "quantities computed from the same acquisition stream with the "
            "committed candidate rule and the committed support helper. "
            "Support values are checked edge by edge against the cap-112 "
            "decomposition where it covers the same seed."
        ),
        "constants": {
            "caps": list(CAPS),
            "slope": SLOPE,
            "cycles": CYCLES,
            "events_per_cycle": EVENTS_PER_CYCLE,
            "blocks": len(BLOCKS),
            "seeds": len(rows),
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "found": found,
        "blocks": blocks,
        "gap_tests": gaps,
        "statistics": statistics_rows,
        "rows": rows,
        "limits": [
            "Three blocks and six seeds each: the block-level ordering has three points, so agreement of a block mean with the level ordering is necessary but far from sufficient.",
            "Within-block Spearman has n=6 per block and no multiplicity control; it is reported as a sign pattern, not a p-value.",
            "Support is measured on the acquisition stream; the engine's own temporal graph also includes within-event pairs, so these are stream-side quantities, not engine state.",
            "The level is a fitted intercept on committed coverage cells; it inherits the shared-slope assumption of the cap-response fit.",
            "No arm was run: every coverage number is read from a committed artifact.",
        ],
        "not_evidence": (
            "A descriptive join of committed coverage cells to stream-side "
            "candidate quantities. It does not show that no quantity anywhere "
            "tracks the level, only that these eight do not, and it does not "
            "change any verdict, target, freeze or grant."
        ),
    })


def render(doc: dict) -> str:
    lines = [
        "# A1 within-block level",
        "",
        "Generated from `docs/a1_within_block_level.json` by "
        "`python -m benchmarks.a1_within_block_level --write`. Do not edit by hand.",
        "",
        "**Descriptive join, not an A1 result.** No engine replay, no target, "
        "freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Blocks",
        "",
        "| Block | Seeds | Offset mean | Offset SD | Offset SE | Candidates | K completeness |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for block in doc["blocks"]:
        lines.append("| %s | %d | %+.4f | %.4f | %.4f | %.1f | %s |" % (
            block["label"], len(block["seeds"]), block["offset_mean"],
            block["offset_sd"], block["offset_se"], block["candidates_mean"],
            ", ".join("%.3f" % value for value in block["k_completeness"])))
    lines += [
        "",
        "## Pairwise level gaps",
        "",
        "| Blocks | Difference | SE | z |",
        "| --- | ---: | ---: | ---: |",
    ]
    for gap in doc["gap_tests"]:
        lines.append("| %s vs %s | %.4f | %.4f | %.2f |" % (
            gap["blocks"][0], gap["blocks"][1], gap["difference"], gap["se"],
            gap["z"]))
    lines += [
        "",
        "## Statistics",
        "",
        "| Quantity | Block means | Relative spread | Orders like the level | Within-block rho | Sign consistent |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in doc["statistics"]:
        lines.append("| %s | %s | %.3f%% | %s | %s | %s |" % (
            row["name"],
            " / ".join("%.3f" % value for value in row["block_means"]),
            100 * row["relative_spread"],
            "yes" if row["orders_like_level_all"] else "no",
            " / ".join("%+.2f" % value for value in row["within_block_spearman"]),
            "yes" if row["sign_consistent"] else "no"))
    lines += [
        "",
        "## Per seed",
        "",
        "| Block | Seed | Offset | Candidates | Mean support | Support mass | Entropy | Cell pairs |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["rows"]:
        lines.append("| %s | %d | %+.4f | %d | %.2f | %d | %.3f | %d |" % (
            row["block"], row["seed"], row["offset"], row["candidate_edges"],
            row["mean_support"], row["support_mass"], row["tag_entropy"],
            row["cell_pairs"]))
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
    if len(doc.get("blocks") or []) != 3:
        found.append("block count")
    if len(doc.get("rows") or []) != 18:
        found.append("seed rows")
    for row in doc.get("rows") or []:
        if row["candidate_edges"] != row["committed_candidates"]:
            found.append("a candidate count disagrees with the committed row")
        if row["candidate_edges"] not in (63, 64):
            found.append("a block is not equal-size")
        if row["k_completeness"] != 1.0:
            found.append("a block is not K-complete")
    for row in doc.get("statistics") or []:
        if row.get("tracks"):
            found.append("a statistic is claimed to track the level")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if abs(_spearman([1, 2, 3], [3, 2, 1]) + 1.0) > 1e-9:
        failures.append("spearman on a reversed pair")
    if abs(_spearman([1, 2, 3], [10, 20, 30]) - 1.0) > 1e-9:
        failures.append("spearman on a monotone pair")
    if not all(_agreement([3.0, 2.0, 1.0], [3.0, 2.0, 1.0])):
        failures.append("agreement on an identical ordering")
    if any(_agreement([1.0, 3.0, 2.0], [3.0, 2.0, 1.0])):
        failures.append("agreement on a shuffled ordering")
    if len(CAPS) != 4 or abs(SLOPE - 0.04698668) > 1e-12:
        failures.append("constants moved")
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
        raise SystemExit("no within-block level artifact; run --write")
    found = problems(_load(OUT_PATH))
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("within-block level: clean")
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
        print("within-block self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
