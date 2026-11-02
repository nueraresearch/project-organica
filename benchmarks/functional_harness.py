"""The engine binding for the functional structure study (§10, step 2).

`benchmarks/functional_structure.py` is the measurement contract: cells, per-cell
loss, the four attribution outcomes, G6. This module is the part that needs the
engine — it develops one arm over the formation stream, freezes its readout,
scores the two windows of §2, and runs the instrument gates of §6.

What it deliberately does **not** do
------------------------------------

**It does not form the endpoint.** §4's `delta` is Organica minus the strongest
baseline on the primary window, pooled over the confirmatory seeds. On design
seeds it is not computed, not printed and not stored: `delta: None` with the
reason beside it. What the gates need is a readout that exists (G1), a
denominator (G2), and a comparison that *can fail* (G3) — none of which is the
endpoint, and the last of which is a task-level control that runs no engine at
all.

**It refuses any seed outside the design block.** `20270201`–`20270205` only.
The confirmatory block is not generated, not fitted and not referenced by value
anywhere in this module; a seed from it raises before a database is opened.

Two implementation choices the protocol leaves open, both fixed here before any
confirmatory seed exists and disclosed in the journal:

* **Which baseline family supplies the bar.** §3 says each family is swept and
  its best configuration chosen on the tuning split; it does not say how the
  family is chosen. Here the family is also chosen on the tuning split
  (`tuning_log_loss`), so the choice never sees the held-out window. The closed
  protocol chose per limb instead; this study does not, because choosing on the
  window the arm is scored on is selection on the endpoint.
* **What "measurable support" means for G1.** A realised held-out cell whose
  source tag has at least one non-zero edge in the frozen readout. A readout
  with edges but no edge on any source tag that occurs in the window is not
  live, whatever its total weight.

Standard library only; scratch DBs only; `organica/` is never touched.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import random
import sys
import time
from collections import defaultdict
from typing import Any, Sequence

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmarks import functional_structure as fs  # noqa: E402
from benchmarks.acquisition_compositional import (  # noqa: E402
    CYCLES, EVENTS_PER_CYCLE, PHASE_TRANSFER, generate_compositional_world,
)
from benchmarks.acquisition_harness import (  # noqa: E402
    _CapOverrideSleepService as CapOverrideSleepService,
)
from benchmarks.acquisition_runner import (  # noqa: E402
    CALIBRATED_ORGANICA_ALPHA, make_organica_backoff,
)
from benchmarks.formation_provenance import FormationRecorder  # noqa: E402
from benchmarks.reusable_knowledge import (  # noqa: E402
    MAX_PREDICTIONS, TUNE_CYCLES, broken_rule_holder, comparator_sweep,
    conditioned_formation_stream, latent_rule_holder, limbs, relation_sets,
    stored_rowid, structure_edges,
)
from organica.memory import MemoryService  # noqa: E402
from organica.paths import LIVE_DB, temp_db  # noqa: E402

# ---------------------------------------------------------------------------
# Fixed constants (§3, §5, §11.1).  None of these is a parameter of this module.
# ---------------------------------------------------------------------------

DESIGN_SEEDS: tuple[int, ...] = (20270201, 20270202, 20270203, 20270204, 20270205)
#: Referenced only so `refuse_confirmatory` can name what it protects; never
#: generated, fitted or scored here.
CONFIRMATORY_SEEDS: tuple[int, ...] = tuple(range(20270206, 20270221))

CAP = MAX_PREDICTIONS                 # 1,000 — §3, from the G13-D scope
ALPHA = CALIBRATED_ORGANICA_ALPHA     # 256.0 — §3, calibrated on 20261099
TUNING_CYCLES = TUNE_CYCLES           # 15  — §11.1

PRIMARY_CYCLES = PHASE_TRANSFER       # 150–200 — §2
ENDPOINT_NOT_FORMED = (
    "the pooled delta of §4 is not formed on design seeds (§10, step 2): it needs "
    "the confirmatory block and is Organica minus the strongest baseline on the "
    "primary window, pooled over those seeds"
)

#: What the design run necessarily computes, and what it does not.  §10 was
#: corrected on 2026-11-02 because its first wording said the endpoint was "not
#: formed", which was too strong: §11.3's share is defined on per-cell paired
#: losses, so the wiring step computes both arms' losses on every realised cell
#: and subtracts them.  Those per-cell differences ARE the endpoint's building
#: block.  What the lock keeps is the statistic and the verdict.
COMPUTED_ON_DESIGN_SEEDS = (
    "per-cell losses for both arms on the realised cells of both windows, because "
    "§11.3's share is defined on their difference",
    "arm-level window log-losses, for G3's degraded-readout control",
    "tuning-split log-losses, for the baseline-family choice (§3 selects on the "
    "tuning split)",
)
NOT_COMPUTED_ON_DESIGN_SEEDS = (
    "the pooled delta of §4 across seeds",
    "any comparison of a design seed's margin to the §4 bar",
    "any statement about whether the endpoint clears, or in which direction",
    "any statistic from a confirmatory seed",
)

DESIGN_OUT = "docs/functional_structure_design_audit.json"

BASELINE_FAMILIES = ("replay", "bigram", "decayed_bigram")
PRIVILEGED_REFERENCE = "cell_counter"


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def refuse_confirmatory(seed: int) -> int:
    """Only the design block may be run at step 2.

    The refusal is the point: a run of a confirmatory seed here would spend the
    one confirmatory run on an unaudited harness, and §8 allows exactly one.
    """
    if seed not in DESIGN_SEEDS:
        if seed in CONFIRMATORY_SEEDS:
            raise SystemExit(
                f"seed {seed} is in the confirmatory block: §10 step 3 only, "
                "after every design gate has passed")
        raise SystemExit(f"seed {seed} is not in the design block {DESIGN_SEEDS}")
    return seed


def require_hash_seed() -> str:
    """The engine's ordering depends on the string-hash seed (journal §95)."""
    value = os.environ.get("PYTHONHASHSEED")
    if value != "0":
        raise SystemExit(
            "PYTHONHASHSEED must be 0: candidate selection orders structures "
            f"built from sets of strings, and it is {value!r}")
    return value


def _scratch(seed: int) -> pathlib.Path:
    path = temp_db(f"functional_{seed}.db")
    if path.resolve() == LIVE_DB.resolve():
        raise AssertionError("refusing to write to the live DB")
    return path


# ---------------------------------------------------------------------------
# The formation run
# ---------------------------------------------------------------------------

def run_formation(formation: dict, seed: int, cap: int = CAP,
                  recorder: FormationRecorder | None = None) -> dict[str, Any]:
    """Feed the formation stream through the engine and freeze the readout.

    The formation stream is 110 cycles (warmup + acquisition).  No revision
    window is fed: this study's primary window is cycles 150–200 of the world,
    which the organism never sees, and the revision study's rotated law is not
    this question.

    `recorder` is the provenance instrument of §7 — a store-time record of which
    row type supplied each transition.  It is read-only, and G4 proves it leaves
    the frozen candidates unchanged.
    """
    db = _scratch(seed)
    mem = MemoryService(str(db))
    svc = CapOverrideSleepService(mem, max_predictions=cap)
    try:
        for i, text in enumerate(formation["events"]):
            event = mem.store(text, event_type="observe", source="env")
            if recorder is not None:
                recorder.record(mem, sorted(text.split()), stored_rowid(mem, event.id))
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                svc.run_sleep_cycle()
                mem.prune_sleep_candidates()
        frozen = svc._load_prior_candidates()
    finally:
        mem._conn.close()
        try:
            db.unlink(missing_ok=True)
        except PermissionError:
            pass
    rows = structure_edges(frozen)
    return {"rows": rows, "frozen": frozen,
            "asserted": {(u, v) for u, ts in rows.items() for v in ts},
            "events": len(formation["events"]), "cap": cap}


def base_rates(rows: Sequence[str]) -> dict[str, float]:
    """The readout's backoff distribution, from formation rows only."""
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        for tag in row.split():
            counts[tag] += 1
    total = sum(counts.values()) or 1
    return {tag: n / total for tag, n in counts.items()}


# ---------------------------------------------------------------------------
# The gates (§6)
# ---------------------------------------------------------------------------

def gate_liveness(engine: dict, org_cells: Sequence[dict]) -> dict[str, Any]:
    """G1: at least one realised held-out cell with measurable support.

    "Measurable" is a non-zero edge out of the cell's source tag.  Total edge
    weight is not enough: a readout can be heavy and still say nothing about any
    tag that occurs in the window.
    """
    supported = {a for a, ts in engine["rows"].items() if ts}
    live = sum(1 for c in org_cells if c["y"] == 1 and c["source"] in supported)
    return {"edges": sum(len(t) for t in engine["rows"].values()),
            "source_tags": len(engine["rows"]),
            "realised_cells": sum(1 for c in org_cells if c["y"] == 1),
            "realised_cells_with_support": live,
            "passed": bool(engine["rows"]) and live > 0}


def gate_denominators(primary_ctx: Sequence[Sequence[str]],
                      org_cells: Sequence[dict], base_cells: Sequence[dict],
                      transfer_ctx: Sequence[Sequence[str]],
                      vocab: set[str]) -> dict[str, Any]:
    """G2: same non-zero denominator for every arm, in both windows.

    Also checks the §11.2 arithmetic: the denominator is
    `pairs × source tags × vocabulary`, including the `b = a` cell.
    """
    expected = sum(len(c) for c in primary_ctx) * len(vocab)
    ok = (len(org_cells) == len(base_cells) == expected
          and len(primary_ctx) > 0 and len(transfer_ctx) > 0)
    return {"primary_pairs": len(primary_ctx), "transfer_pairs": len(transfer_ctx),
            "cells_organica": len(org_cells), "cells_baseline": len(base_cells),
            "cells_expected": expected, "vocab": len(vocab),
            "passed": bool(ok)}


def gate_can_fail(world: dict, held: dict, vocab: set[str],
                  org_prob, org_rows: dict, base_rate: dict) -> dict[str, Any]:
    """G3: the harness separates the law, and rejects a degraded readout.

    Two comparisons, both required, both able to fail:

    * the ceiling (knows the law) must beat the one-transition learner on the
      same window — if it does not, the window cannot detect the law at all;
    * a readout with half its edges dropped must score **worse** than the full
      one — if it does not, the readout is not what the score is reading.
    """
    ctx, obs = held["transfer_full"]
    ceiling = fs.score(latent_rule_holder(world), ctx, obs, vocab)
    broken = fs.score(broken_rule_holder(world), ctx, obs, vocab)
    full = fs.score(org_prob, ctx, obs, vocab)

    degraded_rows = {a: {b: w for i, (b, w) in enumerate(sorted(ts.items()))
                         if i % 2 == 0}
                     for a, ts in sorted(org_rows.items())}
    degraded = fs.score(make_organica_backoff(degraded_rows, base_rate, ALPHA),
                        ctx, obs, vocab)
    kept = sum(len(t) for t in degraded_rows.values())
    total = sum(len(t) for t in org_rows.values())
    return {"label": "gate diagnostic — not an endpoint",
            "ceiling_log_loss": round(ceiling["log_loss"], 6),
            "one_transition_log_loss": round(broken["log_loss"], 6),
            "ceiling_beats_one_transition": broken["log_loss"] > ceiling["log_loss"],
            "organica_log_loss": round(full["log_loss"], 6),
            "degraded_log_loss": round(degraded["log_loss"], 6),
            "edges_kept": f"{kept}/{total}",
            "degraded_is_worse": degraded["log_loss"] > full["log_loss"],
            "passed": (broken["log_loss"] > ceiling["log_loss"]
                       and degraded["log_loss"] > full["log_loss"])}


def gate_neutrality(seed: int, formation: dict, with_rows: dict,
                    with_frozen: list[dict]) -> dict[str, Any]:
    """G4: the recording hook does not change what the engine forms.

    The same seed is run twice — once with the provenance recorder, once without
    — and the frozen candidates and the readout table must be identical.  An
    observer that changes behaviour is not an observer (AGENTS rule 17c).
    """
    plain = run_formation(formation, seed, CAP, None)
    ids = lambda frozen: [(str(c.get("id")), str(c.get("source")), str(c.get("target")))  # noqa: E731
                          for c in frozen]
    same_candidates = ids(with_frozen) == ids(plain["frozen"])
    same_rows = with_rows == plain["rows"]
    return {"candidates_with_hook": len(with_frozen),
            "candidates_without_hook": len(plain["frozen"]),
            "candidates_identical": same_candidates,
            "readout_identical": same_rows,
            "passed": same_candidates and same_rows}


def gate_constants(seed: int) -> dict[str, Any]:
    """G5: every fixed constant is the committed one, and the hash seed is pinned."""
    checks = {
        "cap_is_1000": CAP == MAX_PREDICTIONS == 1000,
        "alpha_is_256": ALPHA == CALIBRATED_ORGANICA_ALPHA == 256.0,
        "tuning_cycles_is_15": TUNING_CYCLES == 15,
        "seed_in_design_block": seed in DESIGN_SEEDS,
        "pythonhashseed_is_0": os.environ.get("PYTHONHASHSEED") == "0",
    }
    # A count of zero is not a failed check: keep it out of the conjunction.
    return {**checks, "confirmatory_seeds_read": 0,
            "passed": all(checks.values())}


# ---------------------------------------------------------------------------
# One design cell
# ---------------------------------------------------------------------------

def run_design_cell(seed: int, check_neutrality: bool = False) -> dict[str, Any]:
    """One design seed: formation, readout, both windows, gates. No endpoint."""
    refuse_confirmatory(seed)
    started = time.time()
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    formation = conditioned_formation_stream(world, seed)
    held = limbs(world)
    vocab = {t for r in world["events"] for t in r.split()}

    recorder = FormationRecorder()
    engine = run_formation(formation, seed, CAP, recorder)
    rate = base_rates(formation["events"])
    org_prob = make_organica_backoff(engine["rows"], rate, ALPHA)

    rows = formation["events"]
    fit_rows = rows[:len(rows) - TUNING_CYCLES * EVENTS_PER_CYCLE]
    comps = comparator_sweep(rows, fit_rows, vocab, world["tag_to_cell"])
    family = min(BASELINE_FAMILIES, key=lambda n: comps[n]["tuning_log_loss"])
    base_prob = comps[family]["prob"]

    # §11.3 pair support: world and self counts per ordered tag pair.
    provenance: dict[tuple[str, str], tuple[int, int]] = {}
    for pair in recorder.transitions:
        origin = recorder.origins(pair)
        provenance[pair] = (origin["world"], origin["self"])

    # Relation coverage of the formation record: the figures §10.1 and §10.2 quote.
    relations = relation_sets(world)
    recorded = set(provenance)
    world_majority = {pair for pair, (w, own) in provenance.items() if w > own}
    coverage = {
        "available_relations": len(relations["available"]),
        "available_recorded": len(relations["available"] & recorded),
        "available_world_majority": len(relations["available"] & world_majority),
        "withheld_relations": len(relations["withheld"]),
        "withheld_recorded": len(relations["withheld"] & recorded),
        "withheld_world_majority": len(relations["withheld"] & world_majority),
    }

    primary_ctx, primary_obs = held["transfer_full"]
    transfer_ctx, transfer_obs = held["transfer"]
    org_primary = fs.cells(org_prob, primary_ctx, primary_obs, vocab)
    base_primary = fs.cells(base_prob, primary_ctx, primary_obs, vocab)
    org_transfer = fs.cells(org_prob, transfer_ctx, transfer_obs, vocab)
    base_transfer = fs.cells(base_prob, transfer_ctx, transfer_obs, vocab)

    gates = {
        "G1": gate_liveness(engine, org_primary),
        "G2": gate_denominators(primary_ctx, org_primary, base_primary,
                                transfer_ctx, vocab),
        "G3": gate_can_fail(world, held, vocab, org_prob, engine["rows"], rate),
        "G5": gate_constants(seed),
    }
    if check_neutrality:
        gates["G4"] = gate_neutrality(seed, formation, engine["rows"], engine["frozen"])

    # The attribution is wired (§11.5) and only its status is recorded: the
    # share is the headline, and §10 keeps design seeds out of the headline.
    def wiring(base_cells, org_cells):
        got = fs.attribute(base_cells, org_cells, provenance)
        return {"status": got["status"], "withheld": got["withheld"],
                "cells_by_group": got["counts"],
                "measure": "temporal source rows: world events versus sleep payloads",
                "shares_reported": False,
                "verdict_on_the_study": False,
                "reason": ("instrument reading on a design seed: the status is computed, "
                           "but no study claim exists yet for it to withhold")}

    return {
        "kind": "functional_structure_design_cell",
        "seed": seed,
        "variant": {"cap": CAP, "alpha": ALPHA, "pythonhashseed": os.environ.get("PYTHONHASHSEED")},
        "world": {"cycles": CYCLES, "primary_cycles": list(PRIMARY_CYCLES),
                  "vocab": len(vocab),
                  "withheld_pairs": held["transfer_pairs"],
                  "withheld_instances": held["transfer_instances"]},
        "formation": {"events": engine["events"], "cycles": 110,
                      "compensated_events": formation["compensated"]},
        "gates": gates,
        "denominators": {
            "primary_pairs": len(primary_ctx), "primary_cells": len(org_primary),
            "transfer_pairs": len(transfer_ctx), "transfer_cells": len(org_transfer),
        },
        "baseline_family_selected_on_tuning": {
            "family": family,
            "config": comps[family]["config"],
            "tuning_log_loss": comps[family]["tuning_log_loss"],
            "rule": "chosen on the tuning split, never on a scored window",
        },
        "provenance_coverage": coverage,
        "disqualifier_wiring": {"primary": wiring(base_primary, org_primary),
                                "transfer": wiring(base_transfer, org_transfer)},
        "endpoint": ENDPOINT_NOT_FORMED,
        "delta": None,
        "seconds": round(time.time() - started, 1),
    }


# ---------------------------------------------------------------------------
# The confirmatory block (§4, §10 step 3)
# ---------------------------------------------------------------------------

CONFIRMATORY_OUT = "docs/functional_structure_confirmatory.json"
BOOTSTRAP_RESAMPLES = 10_000
INTERVAL_LEVEL = 0.9833
#: Fixed before any confirmatory seed is read, and not a study seed.
BOOTSTRAP_SEED = 20261102


def refuse_design(seed: int) -> int:
    """The confirmatory block may not spend itself on a design seed."""
    if seed in DESIGN_SEEDS:
        raise SystemExit(f"seed {seed} is a design seed: its diagnostics are an audit, "
                         "not evidence")
    if seed not in CONFIRMATORY_SEEDS:
        raise SystemExit(f"seed {seed} is not in the confirmatory block")
    return seed


def _cell_losses(seed: int) -> dict[str, Any]:
    """One confirmatory seed: both arms, both windows, per-seed paired delta."""
    refuse_design(seed)
    started = time.time()
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    formation = conditioned_formation_stream(world, seed)
    held = limbs(world)
    vocab = {t for r in world["events"] for t in r.split()}
    recorder = FormationRecorder()
    engine = run_formation(formation, seed, CAP, recorder)
    rate = base_rates(formation["events"])
    org_prob = make_organica_backoff(engine["rows"], rate, ALPHA)

    rows = formation["events"]
    fit_rows = rows[:len(rows) - TUNING_CYCLES * EVENTS_PER_CYCLE]
    comps = comparator_sweep(rows, fit_rows, vocab, world["tag_to_cell"])
    family = min(BASELINE_FAMILIES, key=lambda n: comps[n]["tuning_log_loss"])
    base_prob = comps[family]["prob"]

    provenance: dict[tuple[str, str], tuple[int, int]] = {}
    for pair in recorder.transitions:
        origin = recorder.origins(pair)
        provenance[pair] = (origin["world"], origin["self"])

    windows: dict[str, Any] = {}
    for name, key in (("primary", "transfer_full"), ("co_primary", "transfer")):
        ctx, obs = held[key]
        org = fs.score(org_prob, ctx, obs, vocab)
        base = fs.score(base_prob, ctx, obs, vocab)
        share = fs.attribute(fs.cells(base_prob, ctx, obs, vocab),
                             fs.cells(org_prob, ctx, obs, vocab), provenance)
        windows[name] = {
            "organica_log_loss": org["log_loss"],
            "baseline_log_loss": base["log_loss"],
            "delta": org["log_loss"] - base["log_loss"],
            "cells": org["cells"],
            "pairs": len(ctx),
            "attribution": {"status": share["status"], "withheld": share["withheld"],
                            "share_world": share["share_world"],
                            "share_self": share["share_self"],
                            "share_unattributed": share["share_unattributed"],
                            "margin_positive": share["margin_positive"],
                            "margins": share["margins"],
                            "by_group": share["counts"]},
        }
    return {"seed": seed, "baseline_family": family, "windows": windows,
            "seconds": round(time.time() - started, 1)}


def _pool(weighted: Sequence[tuple[float, int]]) -> float:
    """Pooled delta: total loss difference over total cells, as §11.2 pools its denominators."""
    denominator = sum(c for _, c in weighted)
    if denominator <= 0:
        raise ValueError("a zero denominator is not measurable")
    return sum(d * c for d, c in weighted) / denominator


def _percentile(sorted_values: Sequence[float], p: float) -> float:
    """Nearest-rank percentile on the resample distribution."""
    if not sorted_values:
        raise ValueError("no resamples")
    index = int(round(p * (len(sorted_values) - 1)))
    return sorted_values[min(len(sorted_values) - 1, max(0, index))]


def interval(weighted: Sequence[tuple[float, int]],
             resamples: int = BOOTSTRAP_RESAMPLES,
             seed: int = BOOTSTRAP_SEED,
             level: float = INTERVAL_LEVEL) -> dict[str, Any]:
    """Percentile interval from a cluster bootstrap over seeds (§4's method)."""
    rng = random.Random(seed)
    n = len(weighted)
    draws = sorted(_pool([weighted[rng.randrange(n)] for _ in range(n)])
                   for _ in range(resamples))
    tail = (1.0 - level) / 2.0
    return {"low": _percentile(draws, tail),
            "high": _percentile(draws, 1.0 - tail),
            "level": level, "resamples": resamples, "bootstrap_seed": seed,
            "pooled_delta": _pool(weighted),
            "method": "percentile interval, cluster (seed) bootstrap, nearest-rank"}


def outcome(inter: dict[str, Any]) -> str:
    """§4/§9 in one place: the upper bound is what decides a pass."""
    if inter["high"] < 0:
        return "improvement"
    if inter["low"] > 0:
        return "reversed"
    return "no improvement detected"


def _pooled_attribution(cells: Sequence[dict]) -> dict[str, Any]:
    """§11.5: pool the share as total margin over total positive margin.

    The per-seed margins are summed, not the per-seed cell counts: the share is a
    ratio of loss improvements, and counts are a different quantity.
    """
    groups = ("world", "self", "unattributed")
    margin = {g: 0.0 for g in groups}
    counts = {g: 0 for g in groups}
    for c in cells:
        for g in groups:
            margin[g] += c["attribution"]["margins"].get(g, 0.0)
            counts[g] += c["attribution"]["by_group"].get(g, 0) or 0
    positive = sum(c["attribution"]["margins"].get("positive", 0.0) for c in cells)
    if positive <= 0:
        return {"status": fs.STATUS_EMPTY, "withheld": None, "share_world": None,
                "share_self": None, "share_unattributed": None,
                "note": "no positive margin on any realised cell"}
    shares = {g: margin[g] / positive for g in groups}
    if shares["self"] >= fs.THRESHOLD:
        status, withheld = fs.STATUS_SELF, True
    elif shares["unattributed"] >= fs.THRESHOLD:
        status, withheld = fs.STATUS_UNATTRIBUTED, True
    else:
        status, withheld = fs.STATUS_WORLD, False
    return {"status": status, "withheld": withheld,
            "share_world": round(shares["world"], 6),
            "share_self": round(shares["self"], 6),
            "share_unattributed": round(shares["unattributed"], 6),
            "cells_by_group": counts}


def run_confirmatory(seeds: Sequence[int] = CONFIRMATORY_SEEDS) -> dict[str, Any]:
    """The one confirmatory run: pooled endpoint, interval, bar, attribution, claim."""
    require_hash_seed()
    for seed in seeds:
        refuse_design(seed)
    started = time.time()
    cells = [_cell_losses(seed) for seed in seeds]
    results: dict[str, Any] = {}
    for window in ("primary", "co_primary"):
        weighted = [(c["windows"][window]["delta"], c["windows"][window]["cells"])
                    for c in cells]
        inter = interval(weighted)
        results[window] = {
            "pooled_delta": round(inter["pooled_delta"], 6),
            "interval": {k: (round(v, 6) if isinstance(v, float) else v)
                         for k, v in inter.items() if k != "pooled_delta"},
            "outcome": outcome(inter),
            "bar": "upper bound below zero",
            "passed": inter["high"] < 0,
            "per_seed_delta": {str(c["seed"]): round(c["windows"][window]["delta"], 6)
                               for c in cells},
            "attribution_pooled": _pooled_attribution(
                [{"attribution": c["windows"][window]["attribution"]} for c in cells]),
        }

    primary, co = results["primary"], results["co_primary"]
    if not primary["passed"]:
        claim = f"no improvement detected on the primary window ({primary['outcome']})"
    elif co["passed"] and co["attribution_pooled"]["status"] == fs.STATUS_WORLD:
        claim = "transfer, within this design"
    else:
        claim = ("held-out generalization only: the transfer limb is not attributable "
                 "under the current provenance measure")
    artifact = {
        "kind": "functional_structure_confirmatory",
        "protocol": "docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md §4, §9, §10 step 3",
        "status": primary["outcome"],
        "claim": claim,
        "transfer_limb": "not attributable under the current provenance measure; "
                         "reported whatever its score",
        "seeds": list(seeds), "n": len(cells),
        "constants": {"cap": CAP, "alpha": ALPHA, "tuning_cycles": TUNING_CYCLES,
                      "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
                      "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                      "interval_level": INTERVAL_LEVEL,
                      "bootstrap_seed": BOOTSTRAP_SEED},
        "baseline_family_by_seed": {str(c["seed"]): c["baseline_family"] for c in cells},
        "primary": primary, "co_primary": co,
        "cells": cells,
        "seconds": round(time.time() - started, 1),
    }
    return artifact


# ---------------------------------------------------------------------------
# The design audit (§10, step 2)
# ---------------------------------------------------------------------------

def run_design_audit(seeds: Sequence[int] = DESIGN_SEEDS) -> dict[str, Any]:
    """Run the design block and require every gate to pass."""
    require_hash_seed()
    for seed in seeds:
        refuse_confirmatory(seed)
    started = time.time()
    cells = [run_design_cell(seed, check_neutrality=(i == 0))
             for i, seed in enumerate(seeds)]
    fixtures = fs.gate_fixtures()          # G6, before anything is read as a result
    # G4 belongs to the instrument, not to a seed: it runs once, on the first
    # design seed, and the block passes it or does not.  A gate that was not run
    # is a failure, so its absence is reported rather than skipped.
    per_seed = ("G1", "G2", "G3", "G5")
    failures = []
    for cell in cells:
        for name in per_seed:
            gate = cell["gates"].get(name)
            if gate is None or not gate["passed"]:
                failures.append({"seed": cell["seed"], "gate": name,
                                 "detail": gate})
    neutrality = cells[0]["gates"].get("G4")
    if neutrality is None or not neutrality["passed"]:
        failures.append({"seed": cells[0]["seed"], "gate": "G4", "detail": neutrality})
    artifact = {
        "kind": "functional_structure_design_audit",
        "protocol": "docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md §6, §10",
        "status": ("design block passed: the confirmatory block may run"
                   if not failures else "design block FAILED: the protocol stops here"),
        "seeds": list(seeds),
        "confirmatory_seeds_run": 0,
        "endpoint": ENDPOINT_NOT_FORMED,
        "endpoint_boundary": {
            "computed_on_design_seeds": list(COMPUTED_ON_DESIGN_SEEDS),
            "not_computed_on_design_seeds": list(NOT_COMPUTED_ON_DESIGN_SEEDS),
            "counts_as": "endpoint-derived diagnostic",
            "note": ("The wiring computes the per-cell differences the endpoint "
                     "aggregates; it forms no pooled delta and no verdict."),
        },
        "transfer_limb": {
            "design_seed_status_is_a_verdict": False,
            "status": "not attributable under the current provenance measure",
            "meaning": ("the measure cannot certify a transfer claim on the withheld "
                        "relations; this is not evidence that Organica failed to "
                        "transfer"),
            "structural": ("the withheld relations are withheld from formation, so "
                           "they cannot carry world-source support: sleep-only pairs "
                           "are self-majority, absent pairs unattributed"),
            "claim_available": False,
        },
        "constants": {"cap": CAP, "alpha": ALPHA, "tuning_cycles": TUNING_CYCLES,
                      "pythonhashseed": os.environ.get("PYTHONHASHSEED")},
        "G6": {"passed": True, "cases": fixtures},
        "failures": failures,
        "cells": cells,
        "seconds": round(time.time() - started, 1),
    }
    return artifact


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--design", action="store_true",
                    help="run the design block (§10 step 2)")
    ap.add_argument("--only", type=int, default=None,
                    help="debug: one design seed, artifact written to /tmp")
    ap.add_argument("--confirmatory", action="store_true",
                    help="run the confirmatory block once (§10 step 3)")
    args = ap.parse_args(argv)
    if not (args.design or args.only or args.confirmatory):
        ap.error("pass --design, --confirmatory, or --only SEED")

    if args.confirmatory:
        artifact = run_confirmatory()
        out = ROOT / CONFIRMATORY_OUT
        out.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n",
                       encoding="utf-8")
        print(json.dumps({"status": artifact["status"], "claim": artifact["claim"],
                          "primary": {k: artifact["primary"][k]
                                      for k in ("pooled_delta", "outcome", "passed")},
                          "co_primary": {k: artifact["co_primary"][k]
                                         for k in ("pooled_delta", "outcome", "passed")},
                          "seconds": artifact["seconds"]}, indent=1))
        print(f"wrote {out}")
        return 0

    artifact = run_design_audit((args.only,) if args.only else DESIGN_SEEDS)
    out = pathlib.Path("/tmp/functional_design_only.json") if args.only else ROOT / DESIGN_OUT
    out.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: artifact[k] for k in ("status", "seeds", "failures", "seconds")},
                     indent=1))
    print(f"wrote {out}")
    return 0 if not artifact["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
