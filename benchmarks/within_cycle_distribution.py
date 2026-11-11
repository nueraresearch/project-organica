"""What the 1-4 within-cycle world-edge counts are a distribution of.

The ceiling diagnostic records each world edge's maximum count inside a
persistence-off reset group. It says the maxima are 1-4 on the five zero cells,
but not how the individual counts are distributed or why they sit there. This
ledger measures the underlying population:

* every world edge observed in every processed reset group;
* the count histogram over edge-group observations;
* the same histogram split by group length (the nominal 8-event cycle versus
  groups made longer when a withheld block-end event suppresses the reset);
* the exact lag-1/lag-2 decomposition of each count;
* the same-group count, which excludes the engine's lookback into the last two
  events of the previous reset group, alongside the engine count;
* the per-group maximum and its top edge; and
* a synthetic repeated-pair control that can produce a count above 4.

It reads the committed zero-cell artifact and deterministic worlds. It runs no
engine cell, consumes no fresh seed, changes no floor and is marked
``not_a_result``.

    ./.venv/bin/python -m benchmarks.within_cycle_distribution --write
    ./.venv/bin/python -m benchmarks.within_cycle_distribution --check
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                      # noqa: E402
from benchmarks import persistence_zero_diagnostic as zero               # noqa: E402
from benchmarks.ceiling_diagnostic import (                             # noqa: E402
    CONTROL_SEEDS,
    ZERO_SEEDS,
    _stored_cycles,
)
from benchmarks.acquisition_compositional import generate_compositional_world  # noqa: E402
from benchmarks.acquisition_harness import _world_compositional_edges    # noqa: E402
from organica.memory import _extract_tags                                # noqa: E402

ARTIFACT = ROOT / "docs" / "within_cycle_distribution.json"
PAGE = ROOT / "docs" / "WITHIN-CYCLE-DISTRIBUTION.md"
KIND = "within_cycle_distribution"
WINDOW = 3
NOMINAL_EVENTS = 8


def _tag_cycles(cycles: list[list[str]]) -> list[list[list[str]]]:
    return [[_extract_tags(text) for text in cycle] for cycle in cycles]


def _group_rows(cycles: list[list[list[str]]],
                world_edges: set[tuple[str, str]]) -> list[dict]:
    """Count each edge in each group with and without cross-group lookback."""
    events: list[list[str]] = []
    group_ids: list[int] = []
    for group, tags in enumerate(cycles):
        for event in tags:
            events.append(event)
            group_ids.append(group)
    engine = [Counter() for _ in cycles]
    strict = [Counter() for _ in cycles]
    engine_lags = [Counter() for _ in cycles]
    strict_lags = [Counter() for _ in cycles]
    edge_lags = [defaultdict(Counter) for _ in cycles]
    cross_group = 0
    for j, new_tags in enumerate(events):
        group = group_ids[j]
        for k in range(max(0, j - WINDOW + 1), j + 1):
            lag = j - k
            for source in events[k]:
                for target in new_tags:
                    if source == target or (source, target) not in world_edges:
                        continue
                    edge = (source, target)
                    engine[group][edge] += 1
                    engine_lags[group][lag] += 1
                    edge_lags[group][edge][lag] += 1
                    if group_ids[k] == group:
                        strict[group][edge] += 1
                        strict_lags[group][lag] += 1
                    else:
                        cross_group += 1
    rows = []
    for index, tags in enumerate(cycles):
        occurrences = Counter(tag for event in tags for tag in event)
        top_edge, top_count = sorted(
            engine[index].items(), key=lambda item: (-item[1], item[0])
        )[0] if engine[index] else (None, 0)
        top = None
        if top_edge is not None:
            top = {
                "edge": "%s>%s" % top_edge,
                "source_occurrences": occurrences[top_edge[0]],
                "target_occurrences": occurrences[top_edge[1]],
                "lag0": edge_lags[index][top_edge][0],
                "lag1": edge_lags[index][top_edge][1],
                "lag2": edge_lags[index][top_edge][2],
            }
        engine_obs = sum(engine[index].values())
        strict_obs = sum(strict[index].values())
        rows.append({
            "group": index + 1,
            "events": len(tags),
            "distinct_world_edges": len(engine[index]),
            "edge_observations": engine_obs,
            "strict_edge_observations": strict_obs,
            "cross_group_observations": engine_obs - strict_obs,
            "max_count": max(engine[index].values(), default=0),
            "strict_max_count": max(strict[index].values(), default=0),
            "top_edge": top,
            "count_histogram": dict(sorted(Counter(engine[index].values()).items())),
            "strict_count_histogram": dict(sorted(Counter(strict[index].values()).items())),
            "lag0": engine_lags[index][0],
            "lag1": engine_lags[index][1],
            "lag2": engine_lags[index][2],
            "strict_lag0": strict_lags[index][0],
            "strict_lag1": strict_lags[index][1],
            "strict_lag2": strict_lags[index][2],
            "repeated_tags": sum(1 for value in occurrences.values() if value > 1),
            "max_tag_occurrences": max(occurrences.values(), default=0),
        })
    return rows, cross_group


def _pool(cells: list[dict]) -> dict:
    def aggregate(rows: list[dict], strict: bool = False) -> dict:
        histogram = Counter()
        maxima = Counter()
        lengths = Counter()
        lag0 = lag1 = lag2 = observations = groups = 0
        for row in rows:
            groups += 1
            lengths[row["events"]] += 1
            if strict:
                maxima[row["strict_max_count"]] += 1
                observations += row["strict_edge_observations"]
                lag0 += row["strict_lag0"]
                lag1 += row["strict_lag1"]
                lag2 += row["strict_lag2"]
                histogram.update(row["strict_count_histogram"])
            else:
                maxima[row["max_count"]] += 1
                observations += row["edge_observations"]
                lag0 += row["lag0"]
                lag1 += row["lag1"]
                lag2 += row["lag2"]
                histogram.update(row["count_histogram"])
        return {
            "groups": groups,
            "length_histogram": {str(key): value for key, value in sorted(lengths.items())},
            "edge_count_histogram": {str(key): value for key, value in sorted(histogram.items())},
            "max_count_histogram": {str(key): value for key, value in sorted(maxima.items())},
            "edge_observations": observations,
            "lag0": lag0,
            "lag1": lag1,
            "lag2": lag2,
        }

    def role_rows(role: str, short: bool | None = None) -> list[dict]:
        rows = [group for cell in cells if cell["role"] == role
                for group in cell["groups"]]
        if short is True:
            rows = [group for group in rows if group["events"] <= NOMINAL_EVENTS]
        elif short is False:
            rows = [group for group in rows if group["events"] > NOMINAL_EVENTS]
        return rows

    def block(rows: list[dict]) -> dict:
        result = aggregate(rows)
        result["strict"] = aggregate(rows, strict=True)
        result["cross_group_observations"] = sum(
            row["cross_group_observations"] for row in rows
        )
        result["count_ge5"] = sum(
            count for value, count in result["edge_count_histogram"].items()
            if int(value) >= 5
        )
        result["strict_count_ge5"] = sum(
            count for value, count in result["strict"]["edge_count_histogram"].items()
            if int(value) >= 5
        )
        return result

    zero_rows = role_rows("zero")
    control_rows = role_rows("control")
    zero = block(zero_rows)
    control = block(control_rows)
    for item in (zero, control):
        item["short"] = aggregate(
            [row for row in (zero_rows if item is zero else control_rows)
             if row["events"] <= NOMINAL_EVENTS]
        )
        item["short"]["strict"] = aggregate(
            [row for row in (zero_rows if item is zero else control_rows)
             if row["events"] <= NOMINAL_EVENTS], strict=True
        )
        item["long"] = aggregate(
            [row for row in (zero_rows if item is zero else control_rows)
             if row["events"] > NOMINAL_EVENTS]
        )
        item["long"]["strict"] = aggregate(
            [row for row in (zero_rows if item is zero else control_rows)
             if row["events"] > NOMINAL_EVENTS], strict=True
        )
        item["count_ge5_in_short"] = sum(
            count for value, count in item["short"]["edge_count_histogram"].items()
            if int(value) >= 5
        )
        item["strict_count_ge5_in_short"] = sum(
            count for value, count in item["short"]["strict"]["edge_count_histogram"].items()
            if int(value) >= 5
        )
    return {
        "zero": zero,
        "control": control,
        "zero_long_groups": zero["long"]["groups"],
        "control_long_groups": control["long"]["groups"],
        "short_engine_max": max(
            [int(value) for item in (zero["short"], control["short"])
             for value in item["max_count_histogram"]] or [0]
        ),
        "short_strict_max": max(
            [int(value) for item in (zero["short"], control["short"])
             for value in item["strict"]["max_count_histogram"]] or [0]
        ),
        "long_engine_max": max(
            [int(value) for item in (zero["long"], control["long"])
             for value in item["max_count_histogram"]] or [0]
        ),
        "long_strict_max": max(
            [int(value) for item in (zero["long"], control["long"])
             for value in item["strict"]["max_count_histogram"]] or [0]
        ),
    }


def analyse_cell(block: str, seed: int, role: str, source_row: dict) -> dict:
    world = generate_compositional_world(seed=seed, cycles=120)
    world_edges = _world_compositional_edges(world)
    groups, cross_group = _group_rows(_tag_cycles(_stored_cycles(world)), world_edges)
    maximum = max((group["max_count"] for group in groups), default=0)
    if maximum != source_row["max_world_count"]:
        raise SystemExit(
            "REFUSED: %s/%d replay max %d, stored max %d"
            % (block, seed, maximum, source_row["max_world_count"])
        )
    return {
        "block": block,
        "seed": seed,
        "role": role,
        "observed_s_ever": source_row["observed_s_ever"],
        "source_max_world_count": source_row["max_world_count"],
        "groups": groups,
        "group_count": len(groups),
        "length_histogram": dict(sorted(Counter(g["events"] for g in groups).items())),
        "max_count": maximum,
        "strict_max_count": max((g["strict_max_count"] for g in groups), default=0),
        "edge_observations": sum(g["edge_observations"] for g in groups),
        "strict_edge_observations": sum(g["strict_edge_observations"] for g in groups),
        "cross_group_observations": cross_group,
        "high_groups": [g for g in groups if g["max_count"] >= 5],
    }


def _positive_control() -> dict:
    tags = [["amber", "birch"] for _ in range(8)]
    rows, _cross = _group_rows([tags], {("amber", "birch")})
    row = rows[0]
    return {
        "name": "repeated_pair_control",
        "events": len(tags),
        "max_count": row["max_count"],
        "lag0": row["lag0"],
        "lag1": row["lag1"],
        "lag2": row["lag2"],
        "passes": row["max_count"] > 4,
    }


def summarise(cells: list[dict]) -> dict:
    pooled = _pool(cells)
    zero = pooled["zero"]
    control = pooled["control"]
    total_zero_edges = sum(zero["edge_count_histogram"].values())
    total_control_edges = sum(control["edge_count_histogram"].values())
    return {
        "cells": len(cells),
        "zero_cells": sum(1 for cell in cells if cell["role"] == "zero"),
        "control_cells": sum(1 for cell in cells if cell["role"] == "control"),
        "zero": zero,
        "control": control,
        "zero_long_groups": pooled["zero_long_groups"],
        "control_long_groups": pooled["control_long_groups"],
        "short_engine_max": pooled["short_engine_max"],
        "short_strict_max": pooled["short_strict_max"],
        "long_engine_max": pooled["long_engine_max"],
        "long_strict_max": pooled["long_strict_max"],
        "zero_edge_rows": total_zero_edges,
        "control_edge_rows": total_control_edges,
        "zero_count1_share": (
            zero["edge_count_histogram"].get("1", 0) / total_zero_edges
            if total_zero_edges else None
        ),
        "control_count1_share": (
            control["edge_count_histogram"].get("1", 0) / total_control_edges
            if total_control_edges else None
        ),
        "zero_lag0_share": zero["lag0"] / zero["edge_observations"],
        "zero_lag1_share": zero["lag1"] / zero["edge_observations"],
        "control_lag1_share": control["lag1"] / control["edge_observations"],
        "zero_cross_share": (
            zero["cross_group_observations"] / zero["edge_observations"]
        ),
        "control_cross_share": (
            control["cross_group_observations"] / control["edge_observations"]
        ),
        "zero_count_ge5": zero["count_ge5"],
        "control_count_ge5": control["count_ge5"],
        "zero_count_ge5_in_short": zero["count_ge5_in_short"],
        "control_count_ge5_in_short": control["count_ge5_in_short"],
        "zero_strict_count_ge5": zero["strict_count_ge5"],
        "control_strict_count_ge5": control["strict_count_ge5"],
        "zero_strict_count_ge5_in_short": zero["strict_count_ge5_in_short"],
        "control_strict_count_ge5_in_short": control["strict_count_ge5_in_short"],
    }


def build() -> dict:
    source = zero.load(zero.ARTIFACT)
    rows = {(row["block"], row["seed"]): row for row in source["rows"]
            if row["arm"] == "persistence_off"}
    cells = []
    for block, seed in ZERO_SEEDS:
        cells.append(analyse_cell(block, seed, "zero", rows[(block, seed)]))
    for block, seed in CONTROL_SEEDS:
        cells.append(analyse_cell(block, seed, "control", rows[(block, seed)]))
    summary = summarise(cells)
    zero_total = sum(summary["zero"]["edge_count_histogram"].values())
    zhist = summary["zero"]["edge_count_histogram"]
    summary["findings"] = [
        "The five zero cells have no reset group longer than 8 events; across %d groups "
        "their engine counts are 1-4 and never 5." % summary["zero"]["groups"],
        "Count 1 is the count in %.4f of zero-cell edge-cycle rows; count 2 in %.4f, "
        "count 3 in %.4f, count 4 in %.4f."
        % (summary["zero_count1_share"], zhist.get("2", 0) / zero_total,
           zhist.get("3", 0) / zero_total, zhist.get("4", 0) / zero_total),
        "Every count is an in-window source-target event pair: lag 0 supplies %.4f of "
        "zero-cell observations, lag 1 supplies %.4f and lag 2 supplies %.4f. Cross-group "
        "lookback supplies %.4f of them but never lifts a zero group above 4."
        % (summary["zero_lag0_share"], summary["zero_lag1_share"],
           1 - summary["zero_lag0_share"] - summary["zero_lag1_share"],
           summary["zero_cross_share"]),
        "Groups of at most 8 events have a maximum of 4 in both roles, even with cross-group "
        "lookback; the controls' 5-6 counts occur only in the %d groups longer than 8, created "
        "when a withheld block-end event suppresses the reset." % summary["control_long_groups"],
        "Count 1 is the common case because each event contributes only two tags and most "
        "source-target pairs are seen once inside the three-event lookback; higher counts "
        "require the same two tags to recur in nearby events.",
    ]
    return engine_stamp.stamp({
        "kind": KIND,
        "not_a_result": True,
        "question": (
            "What is the distribution of within-cycle world-edge observation counts, and "
            "why does it concentrate at 1-4 rather than at the floor?"
        ),
        "definition": (
            "A world edge's engine count in one processed reset group is the number of ordered "
            "source-then-target tag pairs within the engine's three-event lookback, restricted "
            "to edges in the world's training-edge set. The counts reset at the group boundary, "
            "but the event history does not: a current group can pair with the last two events "
            "of the previous group. The strict count uses only events in the same group. A "
            "withheld block-end event can make a group longer than the nominal eight events."
        ),
        "method": {
            "source": "docs/persistence_zero_served_diagnostic.json",
            "cells": "the five zero-S_ever persistence-off cells and all seven non-zero off cells",
            "seeds": [seed for _block, seed in ZERO_SEEDS + CONTROL_SEEDS],
            "cycles": "processed reset groups from the committed world; 120 nominal cycles",
            "window": WINDOW,
            "window_definition": "current event plus the two preceding events",
            "count_unit": "one ordered source-target tag pair in the lookback; not a distinct-edge count",
            "primary_count": "engine count with persistent event history and counts reset per group",
            "secondary_count": "strict count using only events in the same reset group",
            "group_split": "nominal-or-shorter (<=8 events) versus merged (>8 events)",
            "engine_edits": "none; replay-only",
            "positive_control": (
                "eight events alternating the same two tags; the repeated-pair control must "
                "produce a count above 4"
            ),
        },
        "cells": cells,
        "summary": summary,
        "controls": [_positive_control()],
        "not_evidence": (
            "A descriptive distribution on six committed seeds, one world family and one "
            "persistence-off replay. It does not test a floor, change a floor, run a cell or "
            "claim that the 1-4 concentration is a general property of the engine. The split "
            "between short and merged groups is a record-arithmetic distinction, not a treatment, "
            "and the cross-group lookback is part of the committed replay rather than an added "
            "mechanism."
        ),
    })


def _max_hist(histogram: dict) -> int:
    return max((int(key) for key in histogram), default=0)


def render(art: dict) -> str:
    s = art["summary"]
    lines = [
        "# Within-cycle world-edge count distribution",
        "",
        "Generated from `docs/within_cycle_distribution.json` by "
        "`python -m benchmarks.within_cycle_distribution --write`. Do not edit by hand.",
        "",
        "**Not a result artifact.** It measures the population behind the 1-4 maxima. It "
        "runs no engine cell, consumes no fresh seed and changes no floor.",
        "",
        "## What is counted",
        "",
        art["definition"],
        "",
        "The unit is an **edge-cycle observation**: one world edge in one processed reset "
        "group. An edge can contribute several observations in the same group; those are "
        "the counts in the histogram. This is not the number of distinct world edges in a "
        "cycle. The engine count is the primary measure; the strict same-group count is "
        "reported to show what the previous group's tail contributes.",
        "",
        "## Per cell",
        "",
        "| Block | Seed | Role | S_ever | Groups | Group lengths | Engine max | Same-group max | Engine observations | Cross-group observations | Count 1 row share | Lag-1 pair share |",
        "| --- | ---: | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cell in art["cells"]:
        hist = cell["length_histogram"]
        total = cell["edge_observations"]
        rows = sum(value for group in cell["groups"]
                   for value in group["count_histogram"].values())
        count1 = sum(g["count_histogram"].get("1", g["count_histogram"].get(1, 0))
                     for g in cell["groups"])
        lag1 = sum(g["lag1"] for g in cell["groups"])
        lines.append("| %s | %d | %s | %d | %d | %s | %d | %d | %d | %d | %.4f | %.4f |" % (
            cell["block"], cell["seed"], cell["role"], cell["observed_s_ever"],
            cell["group_count"], ", ".join("%d:%d" % (int(key), value)
                                               for key, value in hist.items()),
            cell["max_count"], cell["strict_max_count"], total,
            cell["cross_group_observations"], count1 / rows if rows else 0.0,
            lag1 / total if total else 0.0))
    lines += [
        "",
        "## The count histogram",
        "",
        "| Count | Zero-cell engine observations | Zero-cell same-group observations | Control engine observations | Control same-group observations |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    keys = sorted({int(k) for block in (s["zero"], s["control"])
                   for k in block["edge_count_histogram"]})
    for key in keys:
        lines.append("| %d | %d | %d | %d | %d |" % (
            key, s["zero"]["edge_count_histogram"].get(str(key), 0),
            s["zero"]["strict"]["edge_count_histogram"].get(str(key), 0),
            s["control"]["edge_count_histogram"].get(str(key), 0),
            s["control"]["strict"]["edge_count_histogram"].get(str(key), 0)))
    lines += [
        "",
        "## Short versus merged groups",
        "",
        "| Pool | Group length | Groups | Engine max | Same-group max | Engine count 5+ observations | Same-group count 5+ observations |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, block in (("zero", s["zero"]), ("control", s["control"])):
        for part, label in (("short", "<=8"), ("long", ">8")):
            item = block[part]
            lines.append("| %s | %s | %d | %d | %d | %d | %d |" % (
                name, label, item["groups"], _max_hist(item["max_count_histogram"]),
                _max_hist(item["strict"]["max_count_histogram"]),
                sum(count for value, count in item["edge_count_histogram"].items()
                    if int(value) >= 5),
                sum(count for value, count in item["strict"]["edge_count_histogram"].items()
                    if int(value) >= 5)))
    lines += [
        "",
        "## Why the mass is at 1-4",
        "",
    ]
    for item in s["findings"]:
        lines.append("- " + item)
    lines += [
        "",
        "## Positive control",
        "",
        "| Control | Events | Max count | Lag 0 | Lag 1 | Lag 2 | Passes >4 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for control in art["controls"]:
        lines.append("| %s | %d | %d | %d | %d | %d | %s |" % (
            control["name"], control["events"], control["max_count"],
            control["lag0"], control["lag1"], control["lag2"],
            "yes" if control["passes"] else "no"))
    lines += [
        "",
        "The control repeats one pair in every event, so the same edge has more than four "
        "in-window opportunities. It proves the 1-4 observation is not a hard-coded detector "
        "limit; the zero cells simply never contain that much repetition inside a short group.",
        "",
        "## What this does not claim",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = json.loads(ARTIFACT.read_text(encoding="utf-8")) if art is None else art
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("kind")
    if art.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    missing = engine_stamp.missing(art)
    if missing:
        found.append("the artifact is not fully stamped: %r" % (missing,))
    cells = art.get("cells") or []
    zero_cells = [cell for cell in cells if cell.get("role") == "zero"]
    controls = [cell for cell in cells if cell.get("role") == "control"]
    if len(zero_cells) != 5 or len(controls) != 7:
        found.append("expected five zero cells and seven controls")
    for cell in cells:
        groups = cell.get("groups") or []
        if len(groups) != cell.get("group_count"):
            found.append("%s/%s group count" % (cell.get("block"), cell.get("seed")))
        if cell.get("max_count") != cell.get("source_max_world_count"):
            found.append("%s/%s replay max" % (cell.get("block"), cell.get("seed")))
        if cell.get("strict_max_count", 0) > cell.get("max_count", 0):
            found.append("%s/%s strict max exceeds engine max" % (
                cell.get("block"), cell.get("seed")))
        if any(group.get("events", 0) < 1 for group in groups):
            found.append("%s/%s empty group" % (cell.get("block"), cell.get("seed")))
        for group in groups:
            if sum(int(value) * count for value, count in group.get(
                    "count_histogram", {}).items()) != group.get("edge_observations"):
                found.append("%s/%s group %s histogram sum" % (
                    cell.get("block"), cell.get("seed"), group.get("group")))
            if sum(int(value) * count for value, count in group.get(
                    "strict_count_histogram", {}).items()) != group.get(
                    "strict_edge_observations"):
                found.append("%s/%s group %s strict histogram sum" % (
                    cell.get("block"), cell.get("seed"), group.get("group")))
            if group.get("edge_observations") != group.get("strict_edge_observations", 0) + group.get(
                    "cross_group_observations", 0):
                found.append("%s/%s group %s cross count" % (
                    cell.get("block"), cell.get("seed"), group.get("group")))
            if group.get("edge_observations") != group.get("lag0", 0) + group.get(
                    "lag1", 0) + group.get("lag2", 0):
                found.append("%s/%s group %s lag sum" % (
                    cell.get("block"), cell.get("seed"), group.get("group")))
            if group.get("strict_edge_observations") != group.get("strict_lag0", 0) + group.get(
                    "strict_lag1", 0) + group.get("strict_lag2", 0):
                found.append("%s/%s group %s strict lag sum" % (
                    cell.get("block"), cell.get("seed"), group.get("group")))
            if group.get("max_count") != _max_hist(group.get("count_histogram", {})):
                found.append("%s/%s group %s max" % (
                    cell.get("block"), cell.get("seed"), group.get("group")))
            if group.get("strict_max_count") != _max_hist(
                    group.get("strict_count_histogram", {})):
                found.append("%s/%s group %s strict max" % (
                    cell.get("block"), cell.get("seed"), group.get("group")))
            if group.get("max_count") >= 5 and group.get("events") <= NOMINAL_EVENTS:
                found.append("%s/%s: count 5+ in a short group" % (
                    cell.get("block"), cell.get("seed")))
            if group.get("strict_max_count") >= 5 and group.get("events") <= NOMINAL_EVENTS:
                found.append("%s/%s: strict count 5+ in a short group" % (
                    cell.get("block"), cell.get("seed")))
        if cell.get("role") == "zero" and any(g.get("events", 0) > NOMINAL_EVENTS
                                              for g in groups):
            found.append("%s/%s: zero cell has a merged group" % (
                cell.get("block"), cell.get("seed")))
    if any(cell.get("max_count", 0) > 4 for cell in zero_cells):
        found.append("a zero cell reaches 5")
    if not any(cell.get("high_groups") for cell in controls):
        found.append("no control has a count-5+ group")
    expected = summarise(cells)
    actual = {key: value for key, value in (art.get("summary") or {}).items()
              if key != "findings"}
    if actual != expected:
        found.append("the summary does not match the cells")
    if not any(control.get("passes") for control in art.get("controls") or []):
        found.append("the positive control did not exceed 4")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("the page is stale")
    return found


def write() -> int:
    body = build()
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    print("within-cycle distribution: %s" % json.dumps({
        "zero_groups": body["summary"]["zero"]["groups"],
        "zero_max": body["summary"]["zero"]["max_count_histogram"],
        "control_long_groups": body["summary"]["control_long_groups"],
        "short_engine_max": body["summary"]["short_engine_max"],
    }))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no distribution artifact; run --write")
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("within-cycle distribution: %s" % json.dumps({
        "zero_groups": art["summary"]["zero"]["groups"],
        "zero_max": art["summary"]["zero"]["max_count_histogram"],
        "control_long_groups": art["summary"]["control_long_groups"],
        "short_engine_max": art["summary"]["short_engine_max"],
    }))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
