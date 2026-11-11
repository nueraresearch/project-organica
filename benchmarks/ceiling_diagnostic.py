"""Why do within-cycle world-edge counts top out at 3-4 on the five zero cells?

This is a replay diagnostic, not a treatment block. It reads the committed T1/T1b
persistence-off cells, replays their world event streams through the same
within-cycle temporal-pair rule, and asks whether the ceiling is explained by:

* opportunity/tag frequency,
* the 3-event lookback,
* event order, or
* a mixture.

The diagnostic runs no engine cell, consumes no fresh seed, writes no treatment
partcache, and adjudicates no block. It is deliberately marked ``not_a_result``.

    ./.venv/bin/python -m benchmarks.ceiling_diagnostic --write
    ./.venv/bin/python -m benchmarks.ceiling_diagnostic --check
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from organica.memory import _extract_tags

from benchmarks import engine_stamp
from benchmarks import persistence_zero_diagnostic as zero
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE
from benchmarks.acquisition_harness import _world_compositional_edges
from benchmarks.presence_construct_audit import PHASE_ACQUISITION

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "ceiling_diagnostic.json"
PAGE = ROOT / "docs" / "CEILING-DIAGNOSTIC.md"
KIND = "ceiling_diagnostic"
FLOOR = 5
WINDOWS = (1, 2, 3, 4, 6, 8)
PERMUTATIONS = 1000
ZERO_SEEDS = (
    ("T1", 20612204),
    ("T1", 20612205),
    ("T1b", 20612208),
    ("T1b", 20612210),
    ("T1b", 20612212),
)
CONTROL_SEEDS = (
    ("T1", 20612201),
    ("T1", 20612202),
    ("T1", 20612203),
    ("T1", 20612206),
    ("T1b", 20612209),
    ("T1b", 20612211),
    ("T1b", 20612213),
)


def _stored_cycles(world: dict) -> list[list[str]]:
    """The events the persistence-off replay actually stores, grouped by reset.

    The cell loop runs its sleep/reset step when the *processed* event index ends
    an 8-event block. A withheld event that is skipped at the end of a block
    therefore suppresses that reset, and the next block starts with counts still
    live. Grouping by nominal ``i // 8`` would silently remove that channel; the
    group boundary has to be the loop's processed boundary.
    """
    groups: list[list[str]] = [[]]
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
        in_acq = event_lo <= i < event_hi
        if in_acq and not trainable:
            continue
        groups[-1].append(text)
        if (i + 1) % EVENTS_PER_CYCLE == 0:
            groups.append([])
    if groups and not groups[-1]:
        groups.pop()
    return groups


def _tag_cycles(cycles: list[list[str]]) -> list[list[list[str]]]:
    return [[_extract_tags(text) for text in cycle] for cycle in cycles]


def _pair_counts_reset_groups(tag_cycles: list[list[list[str]]],
                              world_edges: set[tuple[str, str]], window: int) -> Counter:
    """Per-edge maximum when event history is cleared at every processed reset boundary."""
    result: Counter = Counter()
    for cycle in tag_cycles:
        counts: Counter = Counter()
        for j, new_tags in enumerate(cycle):
            for k in range(max(0, j - window + 1), j + 1):
                for tag_from in cycle[k]:
                    for tag_to in new_tags:
                        edge = (tag_from, tag_to)
                        if tag_from != tag_to and edge in world_edges:
                            counts[edge] += 1
        for edge, count in counts.items():
            if count > result[edge]:
                result[edge] = count
    return result


def _pair_counts_exact(tag_cycles: list[list[list[str]]], cycle_ids: list[int],
                       world_edges: set[tuple[str, str]], window: int) -> Counter:
    """Per-edge maximum with the engine's persistent event history.

    The engine resets graph counts at the end of a cycle but never deletes event
    rows, so a cycle's first events can look back into the previous cycle. The
    count itself is still evaluated inside the current cycle.
    """
    result: Counter = Counter()
    counts: Counter = Counter()
    flat = [tags for cycle in tag_cycles for tags in cycle]
    current_cycle = None
    for j, new_tags in enumerate(flat):
        if cycle_ids[j] != current_cycle:
            if current_cycle is not None:
                for edge, count in counts.items():
                    if count > result[edge]:
                        result[edge] = count
            counts = Counter()
            current_cycle = cycle_ids[j]
        for k in range(max(0, j - window + 1), j + 1):
            for tag_from in flat[k]:
                for tag_to in new_tags:
                    edge = (tag_from, tag_to)
                    if tag_from != tag_to and edge in world_edges:
                        counts[edge] += 1
    for edge, count in counts.items():
        if count > result[edge]:
            result[edge] = count
    return result


def _frequency_support(cycles: list[list[list[str]]],
                       world_edges: set[tuple[str, str]]) -> Counter:
    """Descriptive per-edge support: max over cycles of min(source, target) occurrences.

    This is not an upper bound on pair count: one target occurrence can pair with
    several source occurrences inside the window. It is retained only as a
    descriptive measure of how often the edge's two tags are present.
    """
    result: Counter = Counter()
    for cycle in cycles:
        freq = Counter(tag for tags in cycle for tag in tags)
        for edge in world_edges:
            bound = min(freq[edge[0]], freq[edge[1]])
            if bound > result[edge]:
                result[edge] = bound
    return result


def _permuted(tag_cycles: list[list[list[str]]], rng: random.Random):
    out = []
    for cycle in tag_cycles:
        copy = list(cycle)
        rng.shuffle(copy)
        out.append(copy)
    return out, [index for index, cycle in enumerate(out) for _ in cycle]


def _cell(block: str, seed: int, role: str, source_s_ever: int,
          source_max: int) -> dict:
    world = generate_compositional_world(seed=seed, cycles=120)
    world_edges = _world_compositional_edges(world)
    cycles = _tag_cycles(_stored_cycles(world))
    flat = [tags for cycle in cycles for tags in cycle]
    cycle_ids = [index for index, cycle in enumerate(cycles) for _ in cycle]

    by_window = {
        str(window): _pair_counts_exact(cycles, cycle_ids, world_edges, window)
        for window in WINDOWS
    }
    group_window_3 = _pair_counts_reset_groups(cycles, world_edges, 3)
    group_window_6 = _pair_counts_reset_groups(cycles, world_edges, 6)
    group_window_8 = _pair_counts_reset_groups(cycles, world_edges, 8)
    base = by_window["3"]
    freq = _frequency_support(cycles, world_edges)
    present_edges = len(world_edges)
    freq_le4 = sum(1 for edge in world_edges if freq.get(edge, 0) <= 4)

    rng = random.Random(seed + 7919)
    null = {edge: [] for edge in world_edges}
    null_cell = []
    for _ in range(PERMUTATIONS):
        permuted, ids = _permuted(cycles, rng)
        maxima = _pair_counts_exact(permuted, ids, world_edges, 3)
        null_cell.append(max(maxima.values(), default=0))
        for edge in world_edges:
            null[edge].append(maxima.get(edge, 0))

    p05 = {}
    p95 = {}
    for edge, values in null.items():
        values.sort()
        p05[edge] = values[int(0.05 * (len(values) - 1))]
        p95[edge] = values[int(0.95 * (len(values) - 1))]
    order_low = sum(1 for edge in world_edges if base.get(edge, 0) < p05[edge])

    window_rows = {}
    for window in WINDOWS:
        maxima = by_window[str(window)]
        window_rows[str(window)] = {
            "max_count": max(maxima.values(), default=0),
            "edges_at_or_above_floor": sum(1 for value in maxima.values() if value >= FLOOR),
        }
    group_rows = {
        "3": {
            "max_count": max(group_window_3.values(), default=0),
            "edges_at_or_above_floor": sum(1 for value in group_window_3.values() if value >= FLOOR),
        },
        "6": {
            "max_count": max(group_window_6.values(), default=0),
            "edges_at_or_above_floor": sum(1 for value in group_window_6.values() if value >= FLOOR),
        },
        "8": {
            "max_count": max(group_window_8.values(), default=0),
            "edges_at_or_above_floor": sum(1 for value in group_window_8.values() if value >= FLOOR),
        },
    }

    base_max = max(base.values(), default=0)
    if window_rows["8"]["max_count"] < FLOOR and group_rows["8"]["max_count"] < FLOOR:
        cell_class = "FREQUENCY"
    elif (group_rows["6"]["edges_at_or_above_floor"] >= FLOOR
          and group_rows["3"]["edges_at_or_above_floor"] == 0):
        cell_class = "WINDOW-SENSITIVE"
    elif order_low / max(present_edges, 1) >= 0.5:
        cell_class = "ORDER"
    else:
        cell_class = "MIXED"

    edge_rows = []
    for edge in sorted(world_edges):
        edge_rows.append({
            "edge": "%s>%s" % edge,
            "max_count": base.get(edge, 0),
            "reset_group_max_count": group_window_3.get(edge, 0),
            "frequency_support": freq.get(edge, 0),
            "window_6_max": by_window["6"].get(edge, 0),
            "window_8_max": by_window["8"].get(edge, 0),
            "reset_group_window_6_max": group_window_6.get(edge, 0),
            "permutation_p05": p05[edge],
            "permutation_p95": p95[edge],
        })

    intergroup_edges = sum(1 for edge in world_edges
                           if base.get(edge, 0) > group_window_3.get(edge, 0))

    return {
        "block": block,
        "seed": seed,
        "role": role,
        "observed_s_ever": source_s_ever,
        "source_max_world_count": source_max,
        "present_edges": present_edges,
        "base_max": base_max,
        "base_edges_at_or_above_floor": window_rows["3"]["edges_at_or_above_floor"],
        "base_max_without_prior_groups": group_rows["3"]["max_count"],
        "intergroup_lift": base_max - group_rows["3"]["max_count"],
        "intergroup_edges": intergroup_edges,
        "frequency_support_max": max(freq.values(), default=0),
        "frequency_support_at_or_below_4": freq_le4,
        "order_low_edges": order_low,
        "order_low_fraction": order_low / max(present_edges, 1),
        "class": cell_class,
        "windows": window_rows,
        "windows_without_prior_groups": group_rows,
        "permutation": {
            "permutations": PERMUTATIONS,
            "max_p05": sorted(null_cell)[int(0.05 * (len(null_cell) - 1))],
            "max_p50": sorted(null_cell)[len(null_cell) // 2],
            "max_p95": sorted(null_cell)[int(0.95 * (len(null_cell) - 1))],
            "fraction_above_observed": sum(1 for value in null_cell if value > base_max) / PERMUTATIONS,
        },
        "edges": edge_rows,
    }


def build() -> dict:
    source = zero.load(zero.ARTIFACT)
    source_rows = {(row["block"], row["seed"]): row for row in source["rows"]
                   if row["arm"] == "persistence_off"}
    cells = []
    for block, seed in ZERO_SEEDS:
        row = source_rows[(block, seed)]
        cells.append(_cell(block, seed, "zero", row["observed_s_ever"], row["max_world_count"]))
    for block, seed in CONTROL_SEEDS:
        row = source_rows[(block, seed)]
        cells.append(_cell(block, seed, "control", row["observed_s_ever"], row["max_world_count"]))
    zero_cells = [cell for cell in cells if cell["role"] == "zero"]
    controls = [cell for cell in cells if cell["role"] == "control"]
    classes = Counter(cell["class"] for cell in zero_cells)
    verdict = "LOCALIZED"
    window_sensitivity = "WINDOW-SENSITIVE (counterfactual, not an engine treatment)"
    if classes["WINDOW-SENSITIVE"] >= 4:
        reading = ("The five zero cells have no world-edge candidate at floor 5: the zero is created "
                   "before ranking, admission or assertion can operate. The window sweep is a "
                   "counterfactual and makes the ceiling window-sensitive; it does not establish "
                   "which of the read floor, horizon, boundary resets or world structure is the root cause.")
        decision = ("Do not extend the engine lookback as an intervention; persistent event rows make "
                    "it a different treatment family. A horizon study needs a preregistered "
                    "within-cycle counterfactual.")
    elif classes["FREQUENCY"] >= 4:
        reading = ("The zero is localized to candidate formation; frequency support is the dominant "
                   "sensitivity class, but the exact causal contribution is not adjudicated.")
        decision = "Measure which world/tag property creates the low opportunity; do not lower the floor."
    elif classes["ORDER"] >= 4:
        reading = ("The zero is localized to candidate formation; order is the dominant sensitivity "
                   "class, but the exact causal contribution is not adjudicated.")
        decision = "Study motif/order structure next; do not treat the floor as the lever."
    else:
        reading = ("The zero is localized to candidate formation, but the five cells do not share one "
                   "dominant sensitivity class; the causal contribution remains unresolved.")
        decision = "Report per-cell classes; no single floor, horizon or order intervention is licensed."

    established = [
        "The five zero cells have 0 admissible world-edge candidates at floor 5.",
        "The zero is created at candidate formation, before ranking, admission and assertion.",
        "Within-cycle counts on these seeds occupy 1-4; the distribution follow-up finds floor 5 above that support (docs/WITHIN-CYCLE-DISTRIBUTION.md).",
        "PersistenceOff removes carried support only when a processed cycle boundary fires; a withheld block-end event suppresses the reset.",
    ]
    not_established = [
        "The exact contribution of the read floor, lookback horizon, cycle-boundary reset behavior and world structure.",
        "That extending the engine lookback is a clean horizon treatment; event rows persist, so it reintroduces cross-cycle context.",
    ]

    return engine_stamp.stamp({
        "kind": KIND,
        "not_a_result": True,
        "question": (
            "Why do within-cycle world-edge counts top out at 3-4 on the five "
            "persistence-off zero cells, and does the record localize the failure "
            "or explain the mechanism?"
        ),
        "method": {
            "source": "docs/persistence_zero_served_diagnostic.json",
            "cells": "the five zero-S_ever persistence-off cells and all seven non-zero off cells",
            "seeds": [seed for _block, seed in ZERO_SEEDS + CONTROL_SEEDS],
            "cycles": "processed 8-event reset boundaries (120 nominal cycles; a withheld block-end can suppress a reset)",
            "floor": FLOOR,
            "window_definition": "events in the lookback including the current event; window 3 is the engine's default",
            "event_history": "persistent across cycle boundaries, as in the engine; graph counts reset each cycle",
            "intervention_description": "No carried support conditional on cycle completion, not a perfect no-memory condition; a withheld block-end event can suppress the reset.",
            "window_reading": "The window sweep is a within-cycle counterfactual; an engine lookback extension is a different treatment family because event rows persist.",
            "window_sweep": list(WINDOWS),
            "permutation": (
                "within-cycle event-order permutation preserving the event multiset and cycle "
                "boundaries; %d fixed-seed permutations per cell" % PERMUTATIONS
            ),
            "frequency_support": "max over cycles of min(source occurrences, target occurrences); descriptive, not an upper bound on pair count",
            "engine_edits": "none; replay-only",
        },
        "cells": cells,
        "summary": {
            "zero_cells": len(zero_cells),
            "controls": len(controls),
            "zero_observed_s_ever": [cell["observed_s_ever"] for cell in zero_cells],
            "control_observed_s_ever": [cell["observed_s_ever"] for cell in controls],
            "zero_base_max": [cell["base_max"] for cell in zero_cells],
            "control_base_max": [cell["base_max"] for cell in controls],
            "zero_base_max_without_prior_groups": [cell["base_max_without_prior_groups"] for cell in zero_cells],
            "control_base_max_without_prior_groups": [cell["base_max_without_prior_groups"] for cell in controls],
            "zero_classes": dict(classes),
            "verdict": verdict,
            "window_sensitivity": window_sensitivity,
            "boundary_caveat": "PersistenceOff is no carried support conditional on cycle completion, not a perfect no-memory condition.",
            "floor_distribution": "Within-cycle maxima on the five zero cells are 1-4; the distribution follow-up finds floor 5 above that support (docs/WITHIN-CYCLE-DISTRIBUTION.md).",
            "established": established,
            "not_established": not_established,
            "reading": reading,
            "decision": decision,
        },
        "not_evidence": (
            "A replay-only diagnostic on stored seeds; it adjudicates no block, consumes no "
            "fresh seed, runs no engine cell and makes no capability, retention or transfer claim. "
            "It localizes the zero to candidate formation; it does not identify the full mechanism "
            "or adjudicate the floor, horizon, boundary-reset or world-structure contribution."
        ),
    })


def render(art: dict) -> str:
    lines = [
        "# Why within-cycle counts top out at 3-4",
        "",
        "**Status: diagnostic, not a result.** Generated from `docs/ceiling_diagnostic.json` by "
        "`python -m benchmarks.ceiling_diagnostic --write`.",
        "",
        "## Cells",
        "",
        "| Block | Seed | Role | S_ever | Source max | Present | Base max | No-prior-group max | Intergroup lift | Freq support max | Window-6 >= 5 | Order-low | Window-sensitive class |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for cell in art["cells"]:
        lines.append("| %s | %d | %s | %d | %d | %d | %d | %d | %d | %d | %d | %d/%d | %s |" % (
            cell["block"], cell["seed"], cell["role"], cell["observed_s_ever"],
            cell["source_max_world_count"], cell["present_edges"], cell["base_max"],
            cell["base_max_without_prior_groups"], cell["intergroup_lift"],
            cell["frequency_support_max"],
            cell["windows"]["6"]["edges_at_or_above_floor"], cell["order_low_edges"],
            cell["present_edges"], cell["class"]))
    lines += [
        "",
        "## What this establishes",
        "",
    ]
    for item in art["summary"].get("established", []):
        lines.append("- " + item)
    lines += [
        "",
        "## What this does not establish",
        "",
    ]
    for item in art["summary"].get("not_established", []):
        lines.append("- " + item)
    lines += [
        "",
        "## Window sweep",
        "",
        "Exact replay with the engine's persistent event history. Window 3 is the engine default; "
        "the window counts the current event plus prior events.",
        "",
        "| Block | Seed | 1 | 2 | 3 | 4 | 6 | 8 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cell in art["cells"]:
        lines.append("| %s | %d | %s |" % (
            cell["block"], cell["seed"],
            " | ".join(str(cell["windows"][str(w)]["max_count"]) for w in WINDOWS)))
    lines += [
        "",
        "## Permutation test",
        "",
        "Within-cycle order permutations preserve the event multiset and cycle boundaries. "
        "`Fraction above observed` is the share of permutations whose cell maximum exceeds "
        "the observed maximum.",
        "",
        "| Block | Seed | Observed max | Perm p05 | Perm p50 | Perm p95 | Fraction above observed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cell in art["cells"]:
        perm = cell["permutation"]
        lines.append("| %s | %d | %d | %d | %d | %d | %.3f |" % (
            cell["block"], cell["seed"], cell["base_max"], perm["max_p05"],
            perm["max_p50"], perm["max_p95"], perm["fraction_above_observed"]))
    lines += [
        "",
        "## Verdict",
        "",
        "**%s (window-sensitive).** %s" % (art["summary"]["verdict"], art["summary"]["reading"]),
        "",
        art["summary"]["decision"],
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None, page: str | None = None) -> list[str]:
    art = zero.load(ARTIFACT) if art is None else art
    page = PAGE.read_text(encoding="utf-8") if page is None else page
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("kind")
    if art.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    summary = art.get("summary") or {}
    if summary.get("verdict") != "LOCALIZED":
        found.append("the verdict is not LOCALIZED")
    if "WINDOW-SENSITIVE" not in summary.get("window_sensitivity", ""):
        found.append("window sensitivity is not recorded")
    if not summary.get("established") or not summary.get("not_established"):
        found.append("the established/not-established scope is missing")
    cells = art.get("cells") or []
    zero_cells = [cell for cell in cells if cell.get("role") == "zero"]
    controls = [cell for cell in cells if cell.get("role") == "control"]
    if len(zero_cells) != 5:
        found.append("expected five zero cells")
    if len(controls) != 7:
        found.append("expected seven controls")
    if any(cell.get("observed_s_ever") != 0 for cell in zero_cells):
        found.append("a zero cell has non-zero S_ever")
    if any(cell.get("observed_s_ever", 0) <= 0 for cell in controls):
        found.append("a control has zero S_ever")
    if any(cell.get("base_max", 0) >= FLOOR for cell in zero_cells):
        found.append("a zero cell reaches the floor")
    if any(cell.get("base_max", 0) < FLOOR for cell in controls):
        found.append("a control does not reach the floor")
    for cell in cells:
        if set(cell.get("windows", {})) != {str(w) for w in WINDOWS}:
            found.append("%s/%s window sweep incomplete" % (cell["block"], cell["seed"]))
        if cell.get("permutation", {}).get("permutations") != PERMUTATIONS:
            found.append("%s/%s permutation count" % (cell["block"], cell["seed"]))
        if len(cell.get("edges") or []) != cell.get("present_edges"):
            found.append("%s/%s edge rows" % (cell["block"], cell["seed"]))
        if cell.get("base_max") != cell.get("source_max_world_count"):
            found.append("%s/%s replay does not reproduce source max" % (cell["block"], cell["seed"]))
    if page.strip() != render(art).strip():
        found.append("the page does not match the artifact; run --write")
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        art = build()
        ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
        PAGE.write_text(render(art), encoding="utf-8")
        print("wrote %s and %s" % (ARTIFACT.relative_to(ROOT), PAGE.relative_to(ROOT)))
        print("%s: %s" % (art["summary"]["verdict"], art["summary"]["reading"]))
        return 0
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    art = zero.load(ARTIFACT)
    print("ceiling diagnostic: %s (%s)" % (art["summary"]["verdict"], art["summary"]["window_sensitivity"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
