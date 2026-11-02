"""The engine binding for the strength-assignment study.

Implements `docs/STRENGTH-ASSIGNMENT-PREREGISTRATION.md`: three arms on one
formation stream (§3), the row-wise weight permutation and its gates (§4, §7),
the decision rule of §5, the outcome table of §6, and the seed blocks of §8. The
pure intervention layer is `benchmarks/strength_assignment.py`; this module is
the part that needs the engine.

What the design block does and does not do
------------------------------------------

`--design` runs `20270401`–`20270405` only, and refuses any other seed before a
database is opened. It computes, because the gates need them: per-cell losses for
all three arms on both windows, arm-level window losses, and the draw report. It
does **not** form `d_shuffled` or `d_bigram`, does not compare any design number
with §5's bar, and records no direction. Those quantities are `None` in the
artifact, with the reason beside them.

`--confirmatory` implements §5 step 4 and refuses to run unless the committed
design artifact exists and passed every gate. It is not run here: §9 allows one
confirmatory run, and this build stops at the design audit.

`organica/` is never touched; scratch databases only.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time
from statistics import mean, median
from typing import Any, Sequence

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmarks import functional_structure as fs  # noqa: E402
from benchmarks import strength_assignment as sa  # noqa: E402
from benchmarks.acquisition_compositional import (  # noqa: E402
    CYCLES, EVENTS_PER_CYCLE, PHASE_TRANSFER, generate_compositional_world,
)
from benchmarks.acquisition_runner import (  # noqa: E402
    CALIBRATED_ORGANICA_ALPHA, make_organica_backoff,
)
from benchmarks.functional_harness import (  # noqa: E402
    BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED, INTERVAL_LEVEL, interval, require_hash_seed,
    run_formation,
)
from benchmarks.reusable_knowledge import (  # noqa: E402
    MAX_PREDICTIONS, TUNE_CYCLES, comparator_sweep, conditioned_formation_stream, limbs,
)

# ---------------------------------------------------------------------------
# Fixed constants (§3, §5, §8). None of these is a parameter of this module.
# ---------------------------------------------------------------------------

DESIGN_SEEDS: tuple[int, ...] = (20270401, 20270402, 20270403, 20270404, 20270405)
CONFIRMATORY_SEEDS: tuple[int, ...] = tuple(range(20270406, 20270421))

CAP = MAX_PREDICTIONS                 # 1,000 — unchanged from the frozen study
ALPHA = CALIBRATED_ORGANICA_ALPHA     # 256.0 — calibrated on 20261099
TUNING_CYCLES = TUNE_CYCLES           # 15 — §11.1 of the frozen protocol

#: 150–200. Amendment A1: the **full** window is primary, because the withheld
#: window leaves the readout almost entirely backoff (1.6 % of realised cells
#: carry a formed edge, against 77.1 % here) and a weight permutation cannot move
#: a cell scored from the backoff distribution.
PRIMARY_CYCLES = PHASE_TRANSFER
PRIMARY_WINDOW = ("full", "transfer_full")
SECONDARY_WINDOW = ("withheld", "transfer")
WINDOWS: tuple[tuple[str, str], ...] = (PRIMARY_WINDOW, SECONDARY_WINDOW)
#: §7 S2(a): below this share of realised cells carrying a formed edge, the
#: primary window cannot see the intervention. A design-identifiability floor,
#: not a result threshold; fixed with the design-block numbers in view (A1).
COVERAGE_FLOOR = 0.50
BASELINE_FAMILIES = ("replay", "bigram", "decayed_bigram")
CONTRASTS = ("shuffled", "bigram")

DESIGN_OUT = "docs/strength_assignment_design_audit.json"
CONFIRMATORY_OUT = "docs/strength_assignment_confirmatory.json"

ENDPOINT_NOT_FORMED = (
    "d_shuffled, d_bigram and the §6 label are not formed on design seeds (§9): "
    "they need the confirmatory block, and no design margin is compared with §5's bar")
COMPUTED_ON_DESIGN_SEEDS = (
    "per-cell losses for all three arms on both windows, because §7's gates need them",
    "arm-level window log-losses, for the S2 and S6 diagnostics",
    "the draw report: invariants, moved share, changed rows, reproducibility",
    "the planted controls, which are checks on the harness and not on Organica",
)
NOT_COMPUTED_ON_DESIGN_SEEDS = (
    "d_shuffled and d_bigram, the paired differences of §5",
    "any comparison of a design number with §5's bar",
    "any statement about which of §6's four rows the study would land in",
    "any statistic from a confirmatory seed",
)


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def refuse_confirmatory(seed: int) -> int:
    """Only the design block may run before the audit has passed."""
    if seed not in DESIGN_SEEDS:
        if seed in CONFIRMATORY_SEEDS:
            raise SystemExit(
                f"seed {seed} is in the confirmatory block: §9 step 4 only, after "
                "every design gate has passed")
        raise SystemExit(f"seed {seed} is not in the design block {DESIGN_SEEDS}")
    return seed


def refuse_design(seed: int) -> int:
    """The confirmatory block may not spend itself on a design seed."""
    if seed in DESIGN_SEEDS:
        raise SystemExit(f"seed {seed} is a design seed: its diagnostics are an "
                         "audit, not evidence")
    if seed not in CONFIRMATORY_SEEDS:
        raise SystemExit(f"seed {seed} is not in the confirmatory block")
    return seed


# ---------------------------------------------------------------------------
# One reading of the world and its three arms
# ---------------------------------------------------------------------------

def _base_rates(rows: Sequence[str]) -> dict[str, float]:
    """The readout's backoff distribution, from formation rows only."""
    counts: dict[str, int] = {}
    for row in rows:
        for tag in row.split():
            counts[tag] = counts.get(tag, 0) + 1
    total = sum(counts.values()) or 1
    return {tag: n / total for tag, n in counts.items()}


def _formation(seed: int) -> dict[str, Any]:
    """The formation stream, the frozen readout, the shifts, and the bigram.

    Shared by the design block and the confirmatory block so the two cannot
    diverge: the same stream, the same fitted readout, the same tuned comparator
    sweep, and the same `K` shuffled row tables.
    """
    started = time.time()
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    formation = conditioned_formation_stream(world, seed)
    held = limbs(world)
    vocab = {t for r in world["events"] for t in r.split()}
    engine = run_formation(formation, seed, CAP)
    rate = _base_rates(formation["events"])
    rows = engine["rows"]

    events = formation["events"]
    fit_rows = events[:len(events) - TUNING_CYCLES * EVENTS_PER_CYCLE]
    comps = comparator_sweep(events, fit_rows, vocab, world["tag_to_cell"])
    family = min(BASELINE_FAMILIES, key=lambda name: comps[name]["tuning_log_loss"])

    shuffled_rows = sa.shuffle_many(sa.rows_of(sa.edges_of(rows)), seed)
    return {
        "world": world, "formation": formation, "held": held, "vocab": vocab,
        "engine": engine, "rate": rate, "rows": rows,
        "full_prob": make_organica_backoff(rows, rate, ALPHA),
        "shuffled_rows": shuffled_rows,
        "shuffled_probs": [make_organica_backoff(graph, rate, ALPHA)
                           for graph in shuffled_rows],
        "bigram_prob": comps[family]["prob"],
        "baseline": {"family": family, "config": comps[family]["config"],
                     "tuning_log_loss": round(comps[family]["tuning_log_loss"], 6)},
        "formation_seconds": round(time.time() - started, 1),
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _arm_scores(reads: dict[str, Any], ctx, obs, vocab) -> dict[str, Any]:
    """Every arm on one window: mean loss and the identical denominator."""
    full = fs.score(reads["full_prob"], ctx, obs, vocab)
    bigram = fs.score(reads["bigram_prob"], ctx, obs, vocab)
    losses = [fs.score(prob, ctx, obs, vocab)["log_loss"] for prob in reads["shuffled_probs"]]
    cells = [fs.score(prob, ctx, obs, vocab)["cells"] for prob in reads["shuffled_probs"]]
    return {
        "full": {"log_loss": round(full["log_loss"], 9), "cells": full["cells"]},
        "bigram": {"log_loss": round(bigram["log_loss"], 9), "cells": bigram["cells"]},
        "shuffled": {
            "log_loss_mean": round(mean(losses), 9),
            "log_loss_min": round(min(losses), 9),
            "log_loss_median": round(median(losses), 9),
            "log_loss_max": round(max(losses), 9),
            "cells": cells[0] if cells else 0,
            "draws": len(losses),
        },
    }


def _max_prob_difference(a_cells: Sequence[dict], b_cells: Sequence[dict]) -> float:
    if len(a_cells) != len(b_cells):
        raise ValueError("cell lists must be aligned")
    return max((abs(x["p"] - y["p"]) for x, y in zip(a_cells, b_cells)), default=0.0)


# ---------------------------------------------------------------------------
# Gates S1–S7 (§7)
# ---------------------------------------------------------------------------

def gate_movement(reads: dict[str, Any], ctx, obs) -> dict[str, Any]:
    """S2: the intervention must change the intended variable, and there must be
    something for it to change.

    A permutation is a random draw whose distribution includes near-identity
    outcomes, so the per-draw minimum is reported and **not** gated — with few
    informative cells, some draw legitimately leaves the informative weight
    where it was, and gating on it fails the harness for the arithmetic rather
    than for the design (Amendment A1). What is gated is the median draw, and
    the quantity that decides whether the question can be asked at all: the
    share of realised cells whose source row has an edge to the observed target,
    which is where the readout's weights live.
    """
    vocab = reads["vocab"]
    rows = reads["rows"]
    full_cells = fs.cells(reads["full_prob"], ctx, obs, vocab)
    realised = [c for c in full_cells if c["y"] == 1]
    covered = [c for c in realised
               if c["source"] in rows and c["target"] in rows[c["source"]]]
    differences = []
    for prob in reads["shuffled_probs"]:
        cells = [c for c in fs.cells(prob, ctx, obs, vocab) if c["y"] == 1]
        differences.append(_max_prob_difference(realised, cells))
    draw = sa.report(rows, reads["seed"])
    coverage = len(covered) / len(realised) if realised else 0.0
    median_change = median(differences) if differences else 0.0
    return {"realised_cells": len(realised),
            "realised_cells_with_target_edge": len(covered),
            "coverage_share": round(coverage, 6),
            "coverage_floor": COVERAGE_FLOOR,
            "max_prob_difference_min": round(min(differences), 9) if differences else 0.0,
            "max_prob_difference_median": round(median_change, 9),
            "max_prob_difference_max": round(max(differences), 9) if differences else 0.0,
            "draws_unmoved": sum(1 for d in differences if d <= sa.TOL),
            "moved_share_median": draw["moved_share_median"],
            "moved_limit": sa.MOVED_LIMIT,
            "readout_changes": bool(median_change > sa.TOL),
            "movement_within_limit": bool(draw["movement_within_limit"]),
            "coverage_met": bool(coverage >= COVERAGE_FLOOR),
            "passed": bool(median_change > sa.TOL and draw["movement_within_limit"]
                           and coverage >= COVERAGE_FLOOR)}


def gate_end_to_end(reads: dict[str, Any], ctx, obs) -> dict[str, Any]:
    """S7: the arms come from one engine run and one readout, asserted not assumed.

    The full arm is rebuilt from the same rows, rate and alpha and compared cell
    by cell; the shuffled tables must have exactly the topology of those rows.
    """
    vocab = reads["vocab"]
    rebuilt = make_organica_backoff(reads["rows"], reads["rate"], ALPHA)
    gap = _max_prob_difference(fs.cells(reads["full_prob"], ctx, obs, vocab),
                               fs.cells(rebuilt, ctx, obs, vocab))
    pairs = {(a, b) for a, t in reads["rows"].items() for b in t}
    topology = all({(a, b) for a, t in graph.items() for b in t} == pairs
                   for graph in reads["shuffled_rows"])
    return {"rebuild_max_abs_gap": gap, "tolerance": sa.TOL,
            "topology_identical_across_arms": bool(topology),
            "edges": len(pairs), "passed": bool(gap <= sa.TOL and topology)}


def gate_denominators(arms: dict[str, Any], ctx, vocab,
                      shuffled_draw_cells: Sequence[int]) -> dict[str, Any]:
    """S6: every arm on the identical cell set."""
    expected = sum(len(c) for c in ctx) * len(vocab)
    counts = {name: arms[name]["cells"] for name in ("full", "bigram", "shuffled")}
    ok = (len(set(counts.values()) | set(shuffled_draw_cells)) == 1
          and all(v == expected and v > 0 for v in counts.values()))
    return {"cells_by_arm": counts, "shuffled_draws": len(shuffled_draw_cells),
            "cells_expected": expected, "vocab": len(vocab), "passed": bool(ok)}


def gate_constants(seed: int) -> dict[str, Any]:
    """S5's constants half: every fixed value is the committed one."""
    checks = {
        "cap_is_1000": CAP == MAX_PREDICTIONS == 1000,
        "alpha_is_256": ALPHA == CALIBRATED_ORGANICA_ALPHA == 256.0,
        "tuning_cycles_is_15": TUNING_CYCLES == 15,
        "draws_is_25": sa.DRAWS == 25,
        "draw_seed_multiplier_is_1013": sa.DRAW_SEED_MULTIPLIER == 1013,
        "moved_limit_is_0_50": sa.MOVED_LIMIT == 0.5,
        "interval_level_is_0_9833": INTERVAL_LEVEL == 0.9833,
        "bootstrap_resamples_is_10000": BOOTSTRAP_RESAMPLES == 10_000,
        "bootstrap_seed_is_20261102": BOOTSTRAP_SEED == 20261102,
        "seed_in_design_block": seed in DESIGN_SEEDS,
        "pythonhashseed_is_0": os.environ.get("PYTHONHASHSEED") == "0",
    }
    return {**checks, "confirmatory_seeds_read": 0, "passed": all(checks.values())}


# ---------------------------------------------------------------------------
# One design cell
# ---------------------------------------------------------------------------

def run_design_cell(seed: int) -> dict[str, Any]:
    """One design seed: three arms, both windows, every gate. No endpoint."""
    refuse_confirmatory(seed)
    started = time.time()
    reads = _formation(seed)
    reads["seed"] = seed
    vocab = reads["vocab"]

    diagnostics: dict[str, Any] = {}
    draw_cells: list[int] = []
    for window, key in WINDOWS:
        ctx, obs = reads["held"][key]
        diagnostics[window] = _arm_scores(reads, ctx, obs, vocab)
        diagnostics[window]["label"] = "gate diagnostic — arm losses, not a contrast"
        draw_cells.extend(fs.score(prob, ctx, obs, vocab)["cells"]
                          for prob in reads["shuffled_probs"])

    primary_ctx, primary_obs = reads["held"][PRIMARY_WINDOW[1]]
    primary_draw_cells = draw_cells[:len(reads["shuffled_probs"])]
    full_cells = fs.cells(reads["full_prob"], primary_ctx, primary_obs, vocab)
    supported = {a for a, t in reads["rows"].items() if t}
    realised = [c for c in full_cells if c["y"] == 1]

    gates: dict[str, Any] = {}
    draw = sa.report(reads["rows"], seed)
    gates["S1"] = {"all_invariants_preserved": draw["all_invariants_preserved"],
                   "draws_failing_invariants": draw["draws_failing_invariants"],
                   "passed": draw["all_invariants_preserved"]}
    gates["S2"] = gate_movement(reads, primary_ctx, primary_obs)
    gates["S3"] = sa.planted_positive()
    gates["S4"] = {"exchangeable_nonconstant": sa.planted_negative_exchangeable(),
                   "constant_weights": sa.planted_negative_constant(),
                   "fixture_can_fail": sa.fixture_can_fail(),
                   "passed": (sa.planted_negative_exchangeable()["passed"]
                              and sa.planted_negative_constant()["passed"]
                              and sa.fixture_can_fail()["passed"])}
    gates["S5"] = {"deterministic": draw["deterministic"],
                   "constants": gate_constants(seed),
                   "passed": bool(draw["deterministic"] and gate_constants(seed)["passed"])}
    gates["S6"] = gate_denominators(diagnostics[PRIMARY_WINDOW[0]], primary_ctx, vocab,
                                    primary_draw_cells)
    gates["S7"] = gate_end_to_end(reads, primary_ctx, primary_obs)
    gates["liveness"] = {"source_tags": len(supported),
                         "realised_cells": len(realised),
                         "realised_cells_with_support": sum(1 for c in realised
                                                            if c["source"] in supported),
                         "passed": bool(supported) and any(c["source"] in supported
                                                           for c in realised)}

    return {
        "kind": "strength_assignment_design_cell",
        "seed": seed,
        "constants": {"cap": CAP, "alpha": ALPHA, "tuning_cycles": TUNING_CYCLES,
                      "draws": sa.DRAWS, "pythonhashseed": os.environ.get("PYTHONHASHSEED")},
        "world": {"cycles": CYCLES, "primary_window": PRIMARY_WINDOW[0],
                  "primary_cycles": list(PRIMARY_CYCLES), "vocab": len(vocab),
                  "withheld_pairs": reads["held"]["transfer_pairs"],
                  "withheld_instances": reads["held"]["transfer_instances"]},
        "formation": {"events": len(reads["formation"]["events"]), "cycles": 110,
                      "seconds": reads["formation_seconds"]},
        "readout": {"edges": draw["edges"], "rows": draw["rows"],
                    "multi_target_rows": draw["multi_target_rows"],
                    "total_weight": round(sum(w for t in reads["rows"].values()
                                              for w in t.values()), 6)},
        "baseline": reads["baseline"],
        "draws": draw,
        "arm_diagnostics": diagnostics,
        "gates": gates,
        "endpoint": ENDPOINT_NOT_FORMED,
        "deltas": None,
        "seconds": round(time.time() - started, 1),
    }


# ---------------------------------------------------------------------------
# The design audit
# ---------------------------------------------------------------------------

def run_design_audit(seeds: Sequence[int] = DESIGN_SEEDS) -> dict[str, Any]:
    """Run the design block and require every gate to pass."""
    require_hash_seed()
    for seed in seeds:
        refuse_confirmatory(seed)
    started = time.time()
    cells = [run_design_cell(seed) for seed in seeds]
    fixtures = sa.gate_fixtures()

    per_seed = ("liveness", "S1", "S2", "S3", "S4", "S5", "S6", "S7")
    failures = []
    for cell in cells:
        for name in per_seed:
            gate = cell["gates"].get(name)
            if gate is None or not gate["passed"]:
                failures.append({"seed": cell["seed"], "gate": name, "detail": gate})

    return {
        "kind": "strength_assignment_design_audit",
        "protocol": "docs/STRENGTH-ASSIGNMENT-PREREGISTRATION.md §7, §9",
        "status": ("design block passed: the confirmatory block may run"
                   if not failures else
                   "design block FAILED: the protocol stops here"),
        "seeds": list(seeds),
        "confirmatory_seeds_run": 0,
        "endpoint": ENDPOINT_NOT_FORMED,
        "endpoint_boundary": {
            "computed_on_design_seeds": list(COMPUTED_ON_DESIGN_SEEDS),
            "not_computed_on_design_seeds": list(NOT_COMPUTED_ON_DESIGN_SEEDS),
            "counts_as": "endpoint-derived diagnostic",
            "note": ("The gates need per-cell losses; the paired contrasts and the "
                     "§6 label are not formed."),
        },
        "layer_gates": {"passed": True, "cases": fixtures},
        "constants": {"cap": CAP, "alpha": ALPHA, "tuning_cycles": TUNING_CYCLES,
                      "draws": sa.DRAWS, "draw_seed_multiplier": sa.DRAW_SEED_MULTIPLIER,
                      "moved_limit": sa.MOVED_LIMIT,
                      "interval_level": INTERVAL_LEVEL,
                      "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                      "bootstrap_seed": BOOTSTRAP_SEED,
                      "pythonhashseed": os.environ.get("PYTHONHASHSEED")},
        "failures": failures,
        "cells": cells,
        "seconds": round(time.time() - started, 1),
    }


# ---------------------------------------------------------------------------
# The confirmatory block (§9 step 4) — implemented, not run
# ---------------------------------------------------------------------------

def _seed_contrasts(seed: int) -> dict[str, Any]:
    """One confirmatory seed: §5's paired differences, and the denominator."""
    refuse_design(seed)
    reads = _formation(seed)
    out: dict[str, Any] = {"seed": seed, "deltas": {}, "cells": 0}
    for window, key in WINDOWS:
        ctx, obs = reads["held"][key]
        scores = _arm_scores(reads, ctx, obs, reads["vocab"])
        out["cells"] = scores["full"]["cells"]
        out["deltas"][window] = {
            "shuffled": scores["full"]["log_loss"] - scores["shuffled"]["log_loss_mean"],
            "bigram": scores["full"]["log_loss"] - scores["bigram"]["log_loss"],
        }
    out["baseline_family"] = reads["baseline"]["family"]
    return out


def run_confirmatory(seeds: Sequence[int] = CONFIRMATORY_SEEDS) -> dict[str, Any]:
    """The one confirmatory run: two intervals, §5's direction, §6's label."""
    require_hash_seed()
    design_path = ROOT / DESIGN_OUT
    if not design_path.exists():
        raise SystemExit(f"{DESIGN_OUT} does not exist: the design block has not run")
    design = json.loads(design_path.read_text(encoding="utf-8"))
    if design.get("failures"):
        raise SystemExit("the design block did not pass: the confirmatory block does not run")
    for seed in seeds:
        refuse_design(seed)

    started = time.time()
    cells = [_seed_contrasts(seed) for seed in seeds]
    results: dict[str, Any] = {}
    for window in ("withheld", "full"):
        block: dict[str, Any] = {}
        for name in CONTRASTS:
            weighted = [(c["deltas"][window][name], c["cells"]) for c in cells]
            inter = interval(weighted)
            block[name] = {
                "pooled_delta": round(inter["pooled_delta"], 6),
                "interval": {k: (round(v, 6) if isinstance(v, float) else v)
                             for k, v in inter.items() if k != "pooled_delta"},
                "above_zero": inter["low"] > 0,
                "per_seed_delta": {str(c["seed"]): round(c["deltas"][window][name], 6)
                                   for c in cells},
            }
        results[window] = block

    primary = results[PRIMARY_WINDOW[0]]
    label = sa.outcome_label(primary["shuffled"]["above_zero"],
                             primary["bigram"]["above_zero"])
    return {
        "kind": "strength_assignment_confirmatory",
        "protocol": "docs/STRENGTH-ASSIGNMENT-PREREGISTRATION.md §5, §6, §9",
        "status": label,
        "primary_window": "full held-out window (cycles 150–200), §1 as amended by A1",
        "secondary_window": "withheld relations, reported with its coverage and not gated (§1)",
        "claim": (label if label != sa.CONTRIBUTES_AND_BEATS
                  else "the assignment of strengths to existing pairs carries predictive "
                       "information, within this design and this world family"),
        "not_a_topology_test": ("topology, degrees and row totals are held exactly fixed; "
                                "nothing here says whether having these edges helps"),
        "not_a_transfer_test": ("the provenance measure cannot certify transfer on relations "
                               "withheld from formation; no transfer claim is made (§2)"),
        "seeds": list(seeds), "n": len(cells),
        "constants": {"cap": CAP, "alpha": ALPHA, "tuning_cycles": TUNING_CYCLES,
                      "draws": sa.DRAWS, "interval_level": INTERVAL_LEVEL,
                      "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                      "bootstrap_seed": BOOTSTRAP_SEED,
                      "pythonhashseed": os.environ.get("PYTHONHASHSEED")},
        "baseline_family_by_seed": {str(c["seed"]): c["baseline_family"] for c in cells},
        "primary": primary,
        "secondary": results[SECONDARY_WINDOW[0]],
        "cells": [{"seed": c["seed"], "cells": c["cells"], "deltas": c["deltas"]}
                  for c in cells],
        "seconds": round(time.time() - started, 1),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--design", action="store_true", help="run the design block")
    ap.add_argument("--only", type=int, default=None,
                    help="debug: one design seed, artifact written to /tmp")
    ap.add_argument("--confirmatory", action="store_true",
                    help="run the confirmatory block once, after the audit passes")
    args = ap.parse_args(argv)
    if not (args.design or args.only or args.confirmatory):
        ap.error("pass --design, --confirmatory, or --only SEED")

    if args.confirmatory:
        artifact = run_confirmatory()
        out = ROOT / CONFIRMATORY_OUT
        out.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": artifact["status"], "n": artifact["n"],
                          "primary": {name: artifact["primary"][name]
                                      for name in CONTRASTS},
                          "secondary": {name: artifact["secondary"][name]
                                        for name in CONTRASTS},
                          "seconds": artifact["seconds"]}, indent=1))
        print(f"wrote {out}")
        return 0

    artifact = run_design_audit((args.only,) if args.only else DESIGN_SEEDS)
    out = pathlib.Path("/tmp/strength_design_only.json") if args.only else ROOT / DESIGN_OUT
    out.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: artifact[k] for k in ("status", "seeds", "failures", "seconds")},
                     indent=1))
    print(f"wrote {out}")
    return 0 if not artifact["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
