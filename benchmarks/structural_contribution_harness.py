"""The engine binding for the structural-contribution study.

Implements `docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md`: four arms on one
formation stream (§3), the rewiring rule and its gates (§4, §8 S3b/S4/S6), the
three paired contrasts and their bar (§5), the outcome table (§6), and the seed
blocks of §7. The pure rewiring layer is `benchmarks/structural_contribution.py`;
this module is the part that needs the engine.

What the design block does and does not do
------------------------------------------

`--design` runs `20270301`–`20270305` only, and refuses any other seed before a
database is opened. It computes, because the gates need them: per-cell losses for
all four arms on both windows, arm-level window losses, and the rewiring report.
It does **not** form the pooled `d_removed`, `d_rewired` or `d_bigram` of §5, does
not compare any design number with §5's bar, and records no direction. Those
quantities are `None` in the artifact, with the reason beside them.

`--confirmatory` implements §9 step 3 and refuses to run unless the committed
design artifact exists and passed every gate. It was not run in the build that
produced this file: §9 spends the block once, and the build stops at the design
audit.

`organica/` is never touched; scratch databases only.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import random
import sys
import time
from statistics import mean, median
from typing import Any, Sequence

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmarks import functional_structure as fs  # noqa: E402
from benchmarks import structural_contribution as sc  # noqa: E402
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
# Fixed constants (§3, §5, §7).  None of these is a parameter of this module.
# ---------------------------------------------------------------------------

DESIGN_SEEDS: tuple[int, ...] = (20270301, 20270302, 20270303, 20270304, 20270305)
#: Referenced only so a guard can name what it protects; never generated here
#: until `--confirmatory` is asked for after the design block has passed.
CONFIRMATORY_SEEDS: tuple[int, ...] = tuple(range(20270306, 20270321))

CAP = MAX_PREDICTIONS                 # 1,000 — §3, unchanged from the frozen study
ALPHA = CALIBRATED_ORGANICA_ALPHA     # 256.0 — §3, calibrated on 20261099
TUNING_CYCLES = TUNE_CYCLES           # 15 — §11.1 of the frozen protocol

PRIMARY_CYCLES = PHASE_TRANSFER       # 150–200 — §1's withheld-relation window
#: §1: the withheld window is primary; the full window is a secondary diagnostic
#: and gates nothing.
WINDOWS: tuple[tuple[str, str], ...] = (("withheld", "transfer"),
                                         ("full", "transfer_full"))
BASELINE_FAMILIES = ("replay", "bigram", "decayed_bigram")
CONTRASTS = ("removed", "rewired", "bigram")

DESIGN_OUT = "docs/structural_contribution_design_audit.json"
CONFIRMATORY_OUT = "docs/structural_contribution_confirmatory.json"

ENDPOINT_NOT_FORMED = (
    "the pooled d_removed, d_rewired and d_bigram of §5 are not formed on design "
    "seeds (§9 step 2): they need the confirmatory block, and no design margin is "
    "compared with §5's bar"
)
COMPUTED_ON_DESIGN_SEEDS = (
    "per-cell losses for all four arms on both windows, because §8's gates need them",
    "arm-level window log-losses, for the S1–S3 diagnostics",
    "the rewiring report: invariants, unchanged share, draw reproducibility",
    "the S3c oracle plant, which is a check on the harness and not on Organica",
)
NOT_COMPUTED_ON_DESIGN_SEEDS = (
    "the pooled contrasts d_removed, d_rewired, d_bigram across seeds",
    "any comparison of a design number with §5's bar",
    "any statement about which of §6's five rows the study would land in",
    "any statistic from a confirmatory seed",
)


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def refuse_confirmatory(seed: int) -> int:
    """Only the design block may be run at §9 step 2."""
    if seed not in DESIGN_SEEDS:
        if seed in CONFIRMATORY_SEEDS:
            raise SystemExit(
                f"seed {seed} is in the confirmatory block: §9 step 3 only, after "
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


def _formation(seed: int) -> dict[str, Any]:
    """One reading of the world and its four arms' probabilities.

    Shared by the design block and the confirmatory block so the two cannot
    diverge: the same formation stream, the same fitted readout, the same tuned
    comparator sweep, and the same `K` rewired graphs.
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

    probs = {
        "full": make_organica_backoff(rows, rate, ALPHA),
        "removed": make_organica_backoff({}, rate, ALPHA),
        "bigram": comps[family]["prob"],
    }
    rewired_rows = sc.rewire_many(sc.rows_of(sc.edges_of(rows)), seed)
    rewired_probs = [make_organica_backoff(graph, rate, ALPHA) for graph in rewired_rows]
    return {
        "world": world, "formation": formation, "held": held, "vocab": vocab,
        "engine": engine, "rate": rate, "rows": rows, "probs": probs,
        "rewired_probs": rewired_probs,
        "baseline": {"family": family, "config": comps[family]["config"],
                     "tuning_log_loss": round(comps[family]["tuning_log_loss"], 6)},
        "formation_seconds": round(time.time() - started, 1),
    }


def _base_rates(rows: Sequence[str]) -> dict[str, float]:
    """The readout's backoff distribution, from formation rows only."""
    counts: dict[str, int] = {}
    for row in rows:
        for tag in row.split():
            counts[tag] = counts.get(tag, 0) + 1
    total = sum(counts.values()) or 1
    return {tag: n / total for tag, n in counts.items()}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _arm_scores(reads: dict[str, Any], ctx, obs, vocab) -> dict[str, Any]:
    """Every arm on one window: mean loss, denominator, and the rewired spread."""
    out: dict[str, Any] = {}
    for name in ("full", "removed", "bigram"):
        got = fs.score(reads["probs"][name], ctx, obs, vocab)
        out[name] = {"log_loss": round(got["log_loss"], 9), "cells": got["cells"]}
    losses = [fs.score(prob, ctx, obs, vocab)["log_loss"]
              for prob in reads["rewired_probs"]]
    out["rewired"] = {
        "log_loss_mean": round(mean(losses), 9),
        "log_loss_min": round(min(losses), 9),
        "log_loss_median": round(median(losses), 9),
        "log_loss_max": round(max(losses), 9),
        "cells": full_cells(reads, ctx, obs, vocab),
        "draws": len(losses),
    }
    return out


def full_cells(reads: dict[str, Any], ctx, obs, vocab) -> int:
    """The denominator, taken once and required to agree across arms (gate S2)."""
    return fs.score(reads["probs"]["full"], ctx, obs, vocab)["cells"]


def _max_prob_difference(a_cells: Sequence[dict], b_cells: Sequence[dict]) -> float:
    if len(a_cells) != len(b_cells):
        raise ValueError("cell lists must be aligned")
    return max((abs(x["p"] - y["p"]) for x, y in zip(a_cells, b_cells)), default=0.0)


# ---------------------------------------------------------------------------
# Gates S1–S6 (§8)
# ---------------------------------------------------------------------------

def gate_liveness(reads: dict[str, Any], full_cells: Sequence[dict]) -> dict[str, Any]:
    """S1: the readout is live, and it says something about the scored tags."""
    rows = reads["rows"]
    supported = {a for a, targets in rows.items() if targets}
    realised = [c for c in full_cells if c["y"] == 1]
    live = sum(1 for c in realised if c["source"] in supported)
    return {"edges": sum(len(t) for t in rows.values()),
            "source_tags": len(supported),
            "realised_cells": len(realised),
            "realised_cells_with_support": live,
            "passed": bool(supported) and live > 0}


def gate_denominators(arms: dict[str, Any], ctx, vocab,
                      rewired_draw_cells: Sequence[int]) -> dict[str, Any]:
    """S2: the identical denominator for all four arms."""
    # The frozen protocol's own arithmetic: cells = summed context tags x vocab.
    expected = sum(len(c) for c in ctx) * len(vocab)
    counts = {name: arms[name]["cells"] for name in ("full", "removed", "bigram")}
    counts["rewired"] = arms["rewired"]["cells"]
    ok = (len(set(counts.values()) | set(rewired_draw_cells)) == 1
          and all(value == expected and value > 0 for value in counts.values())
          and all(value == expected for value in rewired_draw_cells))
    return {"cells_by_arm": counts, "rewired_draws": len(rewired_draw_cells),
            "cells_expected": expected, "vocab": len(vocab), "passed": bool(ok)}


def gate_controls(reads: dict[str, Any], ctx, obs) -> dict[str, Any]:
    """S3a and S3b: the two ablations must be ablations, and must differ."""
    rate = reads["rate"]
    removed_cells = fs.cells(reads["probs"]["removed"], ctx, obs, reads["vocab"])
    base_gap = max((abs(c["p"] - rate.get(c["target"], 0.0)) for c in removed_cells),
                   default=0.0)
    full_cells = fs.cells(reads["probs"]["full"], ctx, obs, reads["vocab"])
    differences = [_max_prob_difference(
        [c for c in full_cells if c["y"] == 1],
        [c for c in fs.cells(prob, ctx, obs, reads["vocab"]) if c["y"] == 1])
        for prob in reads["rewired_probs"]]
    report = sc.rewiring_report(reads["rows"], reads["seed"])
    s3a = base_gap <= sc.TOL
    s3b = (report["unchanged_within_limit"] and min(differences) > sc.TOL)
    return {"S3a_removed_equals_base_rate": {"max_abs_gap": base_gap,
                                             "tolerance": sc.TOL, "passed": s3a},
            "S3b_rewiring_changes_cells": {
                "unchanged_share_max": report["unchanged_share_max"],
                "unchanged_limit": sc.UNCHANGED_LIMIT,
                "min_realised_cell_difference": round(min(differences), 9),
                "passed": s3b},
            "passed": bool(s3a and s3b)}


def gate_plant(reads: dict[str, Any], ctx, obs) -> dict[str, Any]:
    """S3c: an oracle readout built from the scored window separates the arms.

    The plant knows the window, so it must win: if the full arm does not beat both
    ablations here, the harness cannot detect a contribution that is present, and
    the study stops. This is a check on the harness, not a claim about Organica,
    and it is labelled as one wherever it is printed.
    """
    oracle: dict[str, dict[str, float]] = {}
    for c, o in zip(ctx, obs):
        truth = set(o)
        for a in c:
            for b in truth:
                if b == a:
                    continue
                oracle.setdefault(a, {})
                oracle[a][b] = oracle[a].get(b, 0.0) + 1.0
    rate = reads["rate"]
    vocab = reads["vocab"]
    full = fs.score(make_organica_backoff(oracle, rate, ALPHA), ctx, obs, vocab)
    removed = fs.score(make_organica_backoff({}, rate, ALPHA), ctx, obs, vocab)
    graphs = sc.rewire_many(oracle, reads["seed"])
    rewired = [fs.score(make_organica_backoff(g, rate, ALPHA), ctx, obs, vocab)["log_loss"]
               for g in graphs]
    rewired_mean = mean(rewired)
    passed = (full["log_loss"] < removed["log_loss"]
              and full["log_loss"] < rewired_mean)
    return {"label": "gate diagnostic — oracle plant, not a result about Organica",
            "oracle_full_log_loss": round(full["log_loss"], 9),
            "edge_removed_log_loss": round(removed["log_loss"], 9),
            "rewired_log_loss_mean": round(rewired_mean, 9),
            "full_beats_removed": full["log_loss"] < removed["log_loss"],
            "full_beats_rewired": full["log_loss"] < rewired_mean,
            "passed": bool(passed)}


def gate_constants(seed: int) -> dict[str, Any]:
    """S5: every fixed constant is the committed one."""
    checks = {
        "cap_is_1000": CAP == MAX_PREDICTIONS == 1000,
        "alpha_is_256": ALPHA == CALIBRATED_ORGANICA_ALPHA == 256.0,
        "tuning_cycles_is_15": TUNING_CYCLES == 15,
        "draws_is_25": sc.DRAWS == 25,
        "attempts_per_edge_is_10": sc.ATTEMPTS_PER_EDGE == 10,
        "draw_seed_multiplier_is_1009": sc.DRAW_SEED_MULTIPLIER == 1009,
        "unchanged_limit_is_0_20": sc.UNCHANGED_LIMIT == 0.20,
        "bootstrap_resamples_is_10000": BOOTSTRAP_RESAMPLES == 10_000,
        "interval_level_is_0_9833": INTERVAL_LEVEL == 0.9833,
        "bootstrap_seed_is_20261102": BOOTSTRAP_SEED == 20261102,
        "seed_in_design_block": seed in DESIGN_SEEDS,
        "pythonhashseed_is_0": os.environ.get("PYTHONHASHSEED") == "0",
    }
    return {**checks, "confirmatory_seeds_read": 0, "passed": all(checks.values())}


# ---------------------------------------------------------------------------
# One design cell
# ---------------------------------------------------------------------------

def run_design_cell(seed: int) -> dict[str, Any]:
    """One design seed: four arms, both windows, gates S1–S6. No endpoint."""
    refuse_confirmatory(seed)
    started = time.time()
    reads = _formation(seed)
    reads["seed"] = seed
    vocab = reads["vocab"]

    diagnostics: dict[str, Any] = {}
    gates: dict[str, Any] = {}
    draw_cells: list[int] = []
    for window, key in WINDOWS:
        ctx, obs = reads["held"][key]
        diagnostics[window] = _arm_scores(reads, ctx, obs, vocab)
        diagnostics[window]["label"] = "gate diagnostic — arm losses, not a contrast"
        draw_cells.extend(fs.score(prob, ctx, obs, vocab)["cells"]
                          for prob in reads["rewired_probs"])

    primary_ctx, primary_obs = reads["held"]["transfer"]
    primary_draw_cells = draw_cells[:len(reads["rewired_probs"])]
    full_primary = fs.cells(reads["probs"]["full"], primary_ctx, primary_obs, vocab)

    gates["S1"] = gate_liveness(reads, full_primary)
    gates["S2"] = gate_denominators(diagnostics["withheld"], primary_ctx, vocab,
                                    primary_draw_cells)
    gates["S3"] = gate_controls(reads, primary_ctx, primary_obs)
    gates["S3c"] = gate_plant(reads, primary_ctx, primary_obs)
    report = sc.rewiring_report(reads["rows"], seed)
    gates["S4"] = {"all_invariants_preserved": report["all_invariants_preserved"],
                   "draws_failing_invariants": report["draws_failing_invariants"],
                   "unchanged_share_median": report["unchanged_share_median"],
                   "passed": report["all_invariants_preserved"]}
    gates["S5"] = gate_constants(seed)
    gates["S6"] = {"deterministic": report["deterministic"],
                   "passed": report["deterministic"]}

    return {
        "kind": "structural_contribution_design_cell",
        "seed": seed,
        "constants": {"cap": CAP, "alpha": ALPHA, "tuning_cycles": TUNING_CYCLES,
                      "draws": sc.DRAWS, "pythonhashseed": os.environ.get("PYTHONHASHSEED")},
        "world": {"cycles": CYCLES, "primary_cycles": list(PRIMARY_CYCLES),
                  "vocab": len(vocab),
                  "withheld_pairs": reads["held"]["transfer_pairs"],
                  "withheld_instances": reads["held"]["transfer_instances"]},
        "formation": {"events": len(reads["formation"]["events"]), "cycles": 110,
                      "compensated_events": reads["formation"]["compensated"],
                      "seconds": reads["formation_seconds"]},
        "readout": {"edges": report["edges"],
                    "source_tags": len([a for a, t in reads["rows"].items() if t]),
                    "distinct_targets": len({b for t in reads["rows"].values()
                                             for b in t}),
                    "possible_pairs_over_vocab": (len([a for a, t in reads["rows"].items() if t])
                                                  * len(vocab)),
                    "total_weight": round(sum(w for t in reads["rows"].values()
                                              for w in t.values()), 6)},
        "baseline": reads["baseline"],
        "rewiring": report,
        "arm_diagnostics": diagnostics,
        "gates": gates,
        "endpoint": ENDPOINT_NOT_FORMED,
        "deltas": None,
        "seconds": round(time.time() - started, 1),
    }


# ---------------------------------------------------------------------------
# The design audit (§9 step 2)
# ---------------------------------------------------------------------------

def run_design_audit(seeds: Sequence[int] = DESIGN_SEEDS) -> dict[str, Any]:
    """Run the design block and require every gate to pass."""
    require_hash_seed()
    for seed in seeds:
        refuse_confirmatory(seed)
    started = time.time()
    cells = [run_design_cell(seed) for seed in seeds]
    # The layer's own gates, before anything is read as a diagnostic.
    fixtures = sc.gate_fixtures()

    per_seed = ("S1", "S2", "S3", "S3c", "S4", "S5", "S6")
    failures = []
    for cell in cells:
        for name in per_seed:
            gate = cell["gates"].get(name)
            if gate is None or not gate["passed"]:
                failures.append({"seed": cell["seed"], "gate": name, "detail": gate})

    artifact = {
        "kind": "structural_contribution_design_audit",
        "protocol": "docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md §8, §9",
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
            "note": ("The gates need per-cell losses; the pooled contrasts and the "
                     "outcome label are not formed."),
        },
        "layer_gates": {"passed": True, "cases": fixtures},
        "constants": {"cap": CAP, "alpha": ALPHA, "tuning_cycles": TUNING_CYCLES,
                      "draws": sc.DRAWS, "attempts_per_edge": sc.ATTEMPTS_PER_EDGE,
                      "unchanged_limit": sc.UNCHANGED_LIMIT,
                      "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                      "interval_level": INTERVAL_LEVEL,
                      "bootstrap_seed": BOOTSTRAP_SEED,
                      "pythonhashseed": os.environ.get("PYTHONHASHSEED")},
        "failures": failures,
        "cells": cells,
        "seconds": round(time.time() - started, 1),
    }
    return artifact


# ---------------------------------------------------------------------------
# The confirmatory block (§9 step 3) — implemented, not run
# ---------------------------------------------------------------------------

def _seed_contrasts(seed: int) -> dict[str, Any]:
    """One confirmatory seed: the three paired differences of §5, and the cells."""
    refuse_design(seed)
    reads = _formation(seed)
    reads["seed"] = seed
    diffs: dict[str, float] = {}
    cells = 0
    for window, key in WINDOWS:
        ctx, obs = reads["held"][key]
        scores = _arm_scores(reads, ctx, obs, reads["vocab"])
        cells = scores["full"]["cells"]
        diffs[window] = {
            "removed": scores["full"]["log_loss"] - scores["removed"]["log_loss"],
            "rewired": scores["full"]["log_loss"] - scores["rewired"]["log_loss_mean"],
            "bigram": scores["full"]["log_loss"] - scores["bigram"]["log_loss"],
        }
    return {"seed": seed, "cells": cells, "deltas": diffs,
            "baseline_family": reads["baseline"]["family"]}


def run_confirmatory(seeds: Sequence[int] = CONFIRMATORY_SEEDS) -> dict[str, Any]:
    """The one confirmatory run: three intervals, the bar, and the §6 row."""
    require_hash_seed()
    design_path = ROOT / DESIGN_OUT
    if not design_path.exists():
        raise SystemExit(f"{DESIGN_OUT} does not exist: the design block (§9 step 2) "
                         "has not been run")
    design = json.loads(design_path.read_text(encoding="utf-8"))
    if design.get("failures"):
        raise SystemExit("the design block did not pass: §9 step 3 does not run")
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
                "below_zero": inter["high"] < 0,
                "per_seed_delta": {str(c["seed"]): round(c["deltas"][window][name], 6)
                                   for c in cells},
            }
        results[window] = block

    primary = results["withheld"]
    label = sc.outcome_label(primary["removed"]["below_zero"],
                             primary["rewired"]["below_zero"],
                             primary["bigram"]["below_zero"])
    artifact = {
        "kind": "structural_contribution_confirmatory",
        "protocol": "docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md §5, §6, §9 step 3",
        "status": label,
        "primary_window": "withheld relations (cycles 150–200), §1",
        "secondary_window": "full window, reported and not gated (§1)",
        "claim": ("the content of the formed structure contributes to the withheld-relation "
                  "score, within this design"
                  if label == sc.SUPPORTED else label),
        "not_a_transfer_test": ("the provenance measure cannot certify transfer on "
                                "relations withheld from formation; no transfer claim "
                                "is made in either direction (§2)"),
        "seeds": list(seeds), "n": len(cells),
        "constants": {"cap": CAP, "alpha": ALPHA, "tuning_cycles": TUNING_CYCLES,
                      "draws": sc.DRAWS, "attempts_per_edge": sc.ATTEMPTS_PER_EDGE,
                      "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                      "interval_level": INTERVAL_LEVEL,
                      "bootstrap_seed": BOOTSTRAP_SEED,
                      "pythonhashseed": os.environ.get("PYTHONHASHSEED")},
        "baseline_family_by_seed": {str(c["seed"]): c["baseline_family"] for c in cells},
        "withheld": primary,
        "full": results["full"],
        "cells": [{"seed": c["seed"], "cells": c["cells"],
                   "deltas": c["deltas"]} for c in cells],
        "seconds": round(time.time() - started, 1),
    }
    return artifact


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--design", action="store_true",
                    help="run the design block (§9 step 2)")
    ap.add_argument("--only", type=int, default=None,
                    help="debug: one design seed, artifact written to /tmp")
    ap.add_argument("--confirmatory", action="store_true",
                    help="run the confirmatory block once (§9 step 3)")
    args = ap.parse_args(argv)
    if not (args.design or args.only or args.confirmatory):
        ap.error("pass --design, --confirmatory, or --only SEED")

    if args.confirmatory:
        artifact = run_confirmatory()
        out = ROOT / CONFIRMATORY_OUT
        out.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n",
                       encoding="utf-8")
        print(json.dumps({"status": artifact["status"], "n": artifact["n"],
                          "withheld": {name: {"pooled_delta": artifact["withheld"][name]["pooled_delta"],
                                              "interval": artifact["withheld"][name]["interval"],
                                              "below_zero": artifact["withheld"][name]["below_zero"]}
                                       for name in CONTRASTS},
                          "seconds": artifact["seconds"]}, indent=1))
        print(f"wrote {out}")
        return 0

    artifact = run_design_audit((args.only,) if args.only else DESIGN_SEEDS)
    out = pathlib.Path("/tmp/structural_design_only.json") if args.only else ROOT / DESIGN_OUT
    out.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: artifact[k] for k in ("status", "seeds", "failures", "seconds")},
                     indent=1))
    print(f"wrote {out}")
    return 0 if not artifact["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
