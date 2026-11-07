"""Re-run Q028's pair resolver across a declared seed block and report whether the split is stable.

The published calibration cell (seed 20261101) resolved **8 of 14** transfers to the schema's
role pair and left **6** as ``unresolved_pair_not_in_roles`` (polarity-only priming). That is one
draw. This module re-runs the same instrument, unchanged, on six fresh seeds plus the calibration
seed as a reproduction control, and reports the per-seed split rather than a single number.

**The rule, fixed before the run.** ``label_for`` compares each cell against the calibration cell's
published split, not against a threshold computed here:

- ``CONTROL_FAILED`` — seed 20261101 does not reproduce 14 transfers / 8 resolved / 6 polarity-only,
  so the instrument is not the one that produced the published number and nothing else is read;
- ``INCOMPLETE_DENOMINATOR`` — a fresh cell recorded no transfer event; its share is ``null`` and
  *not measurable*, never 0 (AGENTS rule 13b);
- ``STABLE_SPLIT`` — every fresh cell has 14 transfers, 8 resolved and 6 polarity-only;
- ``DENOMINATOR_STABLE`` — every fresh cell has 14 transfers, but the resolved or polarity-only
  count moves;
- ``VARIABLE_DENOMINATOR`` — the transfer count itself moves.

No verdict about Q028, no transfer claim, and no engine change.

Run::

    python -m benchmarks.pair_resolver_stability --run
    python -m benchmarks.pair_resolver_stability --check
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks.transfer_provenance import PAIR_STATUSES, measure, self_test

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARTIFACT = DOCS / "pair_resolver_stability.json"
PAGE = DOCS / "PAIR-RESOLVER-STABILITY.md"

CONTROL_SEED = 20261101
FRESH_SEEDS = tuple(range(20301801, 20301807))
SEEDS = (CONTROL_SEED,) + FRESH_SEEDS

PHASE_A_CYCLES = 40
PHASE_B_CYCLES = 40
CYCLES = PHASE_A_CYCLES + PHASE_B_CYCLES

# The published calibration cell, restated from docs/transfer_provenance.json.
PUBLISHED = {"denominator": 14, "resolved": 8, "polarity_only": 6}

BUCKETS = (
    "CONTROL_FAILED",
    "INCOMPLETE_DENOMINATOR",
    "STABLE_SPLIT",
    "DENOMINATOR_STABLE",
    "VARIABLE_DENOMINATOR",
)


def label_for(control: dict | None, fresh: list[dict]) -> str:
    """The pre-declared stability rule. The control is judged before the fresh cells."""
    if control is None:
        return "CONTROL_FAILED"
    for name, expected in PUBLISHED.items():
        if control.get(name) != expected:
            return "CONTROL_FAILED"
    if not fresh:
        return "INCOMPLETE_DENOMINATOR"
    if any(cell["denominator"] == 0 for cell in fresh):
        return "INCOMPLETE_DENOMINATOR"
    if all(
        cell["denominator"] == PUBLISHED["denominator"]
        and cell["resolved"] == PUBLISHED["resolved"]
        and cell["polarity_only"] == PUBLISHED["polarity_only"]
        for cell in fresh
    ):
        return "STABLE_SPLIT"
    if all(cell["denominator"] == PUBLISHED["denominator"] for cell in fresh):
        return "DENOMINATOR_STABLE"
    return "VARIABLE_DENOMINATOR"


def cell(seed: int) -> dict:
    measured = measure(seed, CYCLES, PHASE_A_CYCLES, PHASE_B_CYCLES)
    pair = measured["pair_measurement"]
    single = measured["measurement"]
    return {
        "seed": seed,
        "control": seed == CONTROL_SEED,
        "cycles": CYCLES,
        "denominator": pair["denominator"],
        "resolved": pair["resolved"],
        "share": pair["share"],
        "measurable": pair["measurable"],
        "not_measurable_reason": pair["not_measurable_reason"],
        "polarity_only": pair["statuses"].get("unresolved_pair_not_in_roles", 0),
        "statuses": pair["statuses"],
        "single_role_resolved": single["resolved"],
        "schemas_recorded": measured["pair_schemas_recorded"],
        "role_rows_recorded": measured["pair_roles_recorded"],
        "roles_recorded": measured["roles_recorded"],
        "priors_shared_with_a": measured["priors_shared_with_a"],
    }


def run(seeds=SEEDS) -> int:
    controls = self_test()
    if not controls["all_passed"]:
        raise SystemExit("the instrument's controls must pass before it measures")
    cells = []
    for seed in seeds:
        row = cell(seed)
        cells.append(row)
        print(
            "s%d  transfers=%2d resolved=%2d polarity=%2d single_role=%2d share=%s"
            % (seed, row["denominator"], row["resolved"], row["polarity_only"],
               row["single_role_resolved"],
               "not measurable" if row["share"] is None else "%.4f" % row["share"]),
            flush=True,
        )
    control = next((row for row in cells if row["control"]), None)
    fresh = [row for row in cells if not row["control"]]
    artifact = {
        "kind": "pair_resolver_stability",
        "instrument": "benchmarks/transfer_provenance.py",
        "question": "Q028",
        "date": "2026-11-07",
        "published": PUBLISHED,
        "control_seed": CONTROL_SEED,
        "fresh_seeds": list(FRESH_SEEDS),
        "seeds": list(SEEDS),
        "cycles": CYCLES,
        "phase_a_cycles": PHASE_A_CYCLES,
        "phase_b_cycles": PHASE_B_CYCLES,
        "label": label_for(control, fresh),
        "cells": cells,
        "controls_passed": controls["all_passed"],
        "no_verdict": True,
        "no_threshold": True,
        "scope": ("same instrument, same two contexts, same 40+40 cycles; stability of the "
                  "split across seeds, not a property of other worlds or cycle counts"),
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(artifact), encoding="utf-8")
    print("label:", artifact["label"])
    return 0


def render(artifact: dict) -> str:
    label = artifact["label"]
    lines = [
        "# Pair resolver stability (Q028)",
        "",
        "**Generated from [`docs/pair_resolver_stability.json`](pair_resolver_stability.json); do not",
        "edit by hand.** Rebuild with `python -m benchmarks.pair_resolver_stability --run`, and",
        "check the page with `--check`.",
        "",
        "## What was re-run",
        "",
        "The pair resolver in `benchmarks/transfer_provenance.py`, unchanged, on the calibration",
        "seed and on six fresh seeds. Each cell runs both contexts for %d + %d cycles and traces"
        % (artifact["phase_a_cycles"], artifact["phase_b_cycles"]),
        "every schema-primed prediction in context B. The published calibration cell is restated",
        "here, not re-derived: %d transfers, %d resolved to the schema's role pair, %d"
        % (artifact["published"]["denominator"], artifact["published"]["resolved"],
           artifact["published"]["polarity_only"]),
        "`unresolved_pair_not_in_roles`.",
        "",
        "**Label: `%s`**" % label,
        "",
        "| seed | role | transfers | resolved to pair | share | polarity-only | single-role resolved |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact["cells"]:
        share = "not measurable" if row["share"] is None else "%.4f" % row["share"]
        lines.append(
            "| %d | %s | %d | %d | %s | %d | %d |"
            % (row["seed"], "control" if row["control"] else "fresh", row["denominator"],
               row["resolved"], share, row["polarity_only"], row["single_role_resolved"])
        )
    lines += [
        "",
        "## What the label means",
        "",
    ]
    meaning = {
        "CONTROL_FAILED": (
            "The calibration seed did not reproduce the published split, so the instrument is not "
            "the one that produced it. Nothing is read as evidence about stability."
        ),
        "INCOMPLETE_DENOMINATOR": (
            "At least one fresh cell recorded no transfer event. That cell's share is not "
            "measurable and is reported as `null`, never as 0."
        ),
        "STABLE_SPLIT": (
            "Every fresh cell reproduced 14 transfers, 8 resolved and 6 polarity-only. Within this "
            "instrument and world family the split did not move across the six seeds."
        ),
        "DENOMINATOR_STABLE": (
            "Every fresh cell recorded the same 14 transfers, but the resolved or polarity-only "
            "count moved. The denominator is stable and the split is not."
        ),
        "VARIABLE_DENOMINATOR": (
            "The number of transfer events itself moved across seeds, so the split is a property "
            "of the draw as well as of the resolver."
        ),
    }
    lines.append(meaning[label])
    lines += [
        "",
        "## Controls and scope",
        "",
        "- The instrument's own control set runs before any cell; it passed: %s."
        % ("yes" if artifact["controls_passed"] else "no"),
        "- The calibration seed is a reproduction control, and it is judged before the fresh cells.",
        "- Every cell records the single-role reading as well, so the pair resolver's difference "
        "from the predicate it replaced stays visible.",
        "- This is not Q028's answer and not a transfer claim. It tests whether one calibration "
        "split is stable across seeds in the same world family, at the same cycle counts.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.run:
        return run()
    if args.check:
        if not ARTIFACT.exists() or not PAGE.exists():
            print("FAIL: the artifact or page is missing")
            return 1
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        if artifact["label"] not in BUCKETS:
            print("FAIL: label %r is not one of the declared buckets" % artifact["label"])
            return 1
        if PAGE.read_text(encoding="utf-8") != render(artifact):
            print("FAIL: %s is stale; rebuild with --run" % PAGE.name)
            return 1
        print("pair resolver stability: %s, page current" % artifact["label"])
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
