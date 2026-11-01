"""The reusable-knowledge harness (§10 of the preregistration).

Question (Revision 2): is structure Organica formed during exposure **usable** on
held-out events — specifically, on the cell transitions that were withheld from
*every* formation exposure?

This module is the harness, not a result.  It builds the five items §10 enumerates:

1. **The conditioned sampler.**  Two declared directed cell transitions are
   withheld from warmup *and* acquisition alike, by conditioned sampling: when
   the world would take a withheld transition the *other* transition from the
   same context is taken instead, weighted by the law.  No event is skipped and
   no adjacency is manufactured, which is why the existing `trainable` mask in
   `acquisition_compositional.py` — which generates the event, advances the
   hidden state and only skips the *storage* — is **not** reused (§3.1, §15.4).
2. **The Gate F audit**, over the 96 relations available during formation
   (128 tag-pair relations − 32 withheld), with its precision companion (§14).
3. **The held-out limbs**: retention (the whole window) and transfer (only the
   withheld relations), on the real, unconditioned continuation of the world.
4. **The latent-rule holder** as the ceiling, closed form (§14).
5. **The comparator sweep**: replay, bigram and decayed bigram as the primary
   same-experience set, each swept over its declared grid and selected on a
   tuning split; the cell-level counter as a **privileged reference**, reported
   separately because it is granted the latent state.  The oracle-admitted arm
   is **deferred** and is not implemented here (§15.3).

Rules this module obeys
-----------------------

* `organica/` is never edited.  The variant is a subclass that changes only the
  Layer-1 truncation, imported from `acquisition_harness` so the instrument has
  one implementation rather than two (AGENTS rule 25).
* Every gate here **can fail**, and `harness_audit` demonstrates that it does.
* The confirmatory seeds are refused unless a committed calibration artifact
  says all five calibration seeds passed (§15.2).
* Standard library only.  Scratch DBs only.

No cell has run when this module is imported; `main` is the only entry point
that runs one.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import sys
from collections import defaultdict
from typing import Any, Callable

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmarks.acquisition_compositional import (  # noqa: E402
    CELLS, CYCLES, EVENTS_PER_CYCLE, LAW_R0, PHASE_ACQUISITION,
    PHASE_RETENTION, PHASE_TRANSFER, PHASE_WARMUP, TAGS_PER_CELL,
    cell_name, flip_p, flip_q, generate_compositional_world, score,
)
from benchmarks.acquisition_baselines import (  # noqa: E402
    BIGRAM_GRID, CELL_GRID, fit_bigram, fit_cell_counter,
)
from benchmarks.acquisition_runner import (  # noqa: E402
    fit_replay_learner, make_organica_backoff, structure_edges,
)
from benchmarks.acquisition_harness import (  # noqa: E402
    _CapOverrideSleepService as CapOverrideSleepService,
)
from organica.memory import MemoryService  # noqa: E402
from organica.paths import LIVE_DB, temp_db  # noqa: E402

# ---------------------------------------------------------------------------
# The variant and the gates (§15)
# ---------------------------------------------------------------------------

#: The variant of §15: a capacity change and nothing else.
VARIANT_NAME = "V1.1-cap(1000)"
MAX_PREDICTIONS = 1_000

#: The withheld transitions, fixed by the feasibility enumeration of 28 subsets
#: under criteria written before it ran (journal §91–§92).  Two of the eight
#: directed cell transitions, 25 %.
WITHHELD: tuple[tuple[tuple[int, int], str], ...] = (
    ((0, 0), "flip_p"),
    ((0, 1), "flip_q"),
)

#: Gate F (§14): asserted relations in the AVAILABLE set over 96, threshold 0.95.
GATE_F_THRESHOLD = 0.95
GATE_F_DENOMINATOR = 96

#: The calibrated readout smoothing (§14's readout form is unchanged).
ALPHA = 256.0

#: Seeds.  Calibration/design only; the confirmatory set is refused below.
CALIBRATION_SEEDS: tuple[int, ...] = (20261201, 20261202, 20261203, 20261204, 20261205)
CONFIRMATORY_SEEDS: tuple[int, ...] = tuple(range(20261207, 20261227))
BURNED_SEEDS: tuple[int, ...] = (20261206,)

#: The tuning split for the comparator sweep: the last `TUNE_CYCLES` of
#: formation, excluded from the configs' fitting rows so selection is not made
#: on the data the arm is fitted to.
TUNE_CYCLES = 15

CALIBRATION_OUT = "docs/reusable_knowledge_calibration.json"

#: The attribution share (§17): the share of the readout's edge weight carried
#: by the structure type this study is about.  A margin whose evidence sits
#: mostly in other structure types is not attributable to the learned transition
#: rule, whatever its size.  The minimum is the formation-utilization campaign's
#: A7 operating point, adopted **before** any confirmatory seed and not chosen
#: from these numbers.
ATTRIBUTION_MINIMUM = 0.50
LAYER1_TYPE = "prediction_candidate"

KINDS = ("flip_p", "flip_q")


# ---------------------------------------------------------------------------
# 1. The conditioned sampler
# ---------------------------------------------------------------------------

def _succ(cell: tuple[int, int], kind: str) -> tuple[int, int]:
    return flip_p(cell) if kind == "flip_p" else flip_q(cell)


def formation_cycles() -> int:
    """Warmup + acquisition — one formation exposure, as the runner feeds it."""
    return PHASE_ACQUISITION[1]


def conditioned_formation_stream(world: dict, seed: int,
                                 withheld=WITHHELD) -> dict[str, Any]:
    """Generate the formation stream with the declared transitions withheld.

    The events are *generated* under the condition, not filtered afterwards:
    when the law would take a withheld transition from the current cell, the
    permitted transition from that same cell is taken instead, weighted by
    `LAW_R0`.  So every stored event is a genuine successor of the one before
    it, the hidden state never jumps, and nothing is skipped.

    The tag mapping is the real world's, so the organism's vocabulary and the
    scored windows are the same world.
    """
    blocked = set(withheld)
    cell_tags = {_coord(name): tags
                 for name, tags in world["cell_tags"].items()}
    rng = random.Random(seed * 31 + 7)
    state = CELLS[0]
    events: list[str] = []
    cells: list[tuple[int, int]] = []
    observed: dict[str, int] = defaultdict(int)
    compensated = 0
    for _ in range(formation_cycles() * EVENTS_PER_CYCLE):
        options = [(state, k) for k in KINDS]
        kind = rng.choices([k for _, k in options],
                           weights=[LAW_R0[k] for _, k in options], k=1)[0]
        if (state, kind) in blocked:
            compensated += 1
            here = [k for k in KINDS if (state, k) not in blocked]
            if not here:                      # a context with no permitted exit
                raise AssertionError(f"cell {state} has no permitted transition")
            kind = rng.choices(here, weights=[LAW_R0[k] for k in here], k=1)[0]
        nxt = _succ(state, kind)
        observed[f"{state}|{kind}"] += 1
        events.append(" ".join(sorted(rng.sample(cell_tags[nxt], 2))))
        cells.append(nxt)
        state = nxt
    return {
        "events": events,
        "cells": [cell_name(c) for c in cells],
        "raw_cells": cells,
        "observed": dict(observed),
        "compensated": compensated,
        "withheld": [[list(c), k] for c, k in withheld],
    }


# ---------------------------------------------------------------------------
# 2. Relations and Gate F
# ---------------------------------------------------------------------------

def _coord(cname: str) -> tuple[int, int]:
    return (int(cname[1]), int(cname[3]))


def relation_sets(world: dict, withheld=WITHHELD) -> dict[str, set[tuple[str, str]]]:
    """The tag-pair relations, split by what formation exposure could support.

    `available` is Gate F's denominator (96): the relations implied by the six
    permitted transitions.  `withheld` is what the transfer limb scores (32).
    """
    blocked = set(withheld)
    tag_of = world["cell_tags"]
    permitted_transitions = [(c, k) for c in CELLS for k in KINDS
                             if (c, k) not in blocked]
    withheld_transitions = list(withheld)
    available: set[tuple[str, str]] = set()
    withheld_relations: set[tuple[str, str]] = set()
    for transitions, into in ((permitted_transitions, available),
                              (withheld_transitions, withheld_relations)):
        for c, k in transitions:
            nxt = cell_name(_succ(c, k))
            for u in tag_of[cell_name(c)]:
                for v in tag_of[nxt]:
                    into.add((u, v))
    return {
        "available": available,
        "withheld": withheld_relations,
        "all": available | withheld_relations,
        "permitted_transitions": permitted_transitions,
        "withheld_transitions": withheld_transitions,
    }


def gate_f(asserted: set[tuple[str, str]], relations: dict,
           threshold: float = GATE_F_THRESHOLD) -> dict[str, Any]:
    """Gate F: asserted relations in the AVAILABLE set over 96.

    Reported with its precision companion, because coverage alone can be bought
    by asserting everything: precision is `covered / |asserted|`.  A readout
    that asserts the whole 128-relation support and nothing else would score
    coverage 1.0 and precision 0.75, which is why the withheld relations are
    **not** in the denominator (§14).
    """
    available = relations["available"]
    covered = asserted & available
    denom = len(available)
    coverage = len(covered) / denom if denom else 0.0
    precision = len(covered) / len(asserted) if asserted else None
    in_world = len(asserted & relations["all"])
    return {
        "coverage": round(coverage, 6),
        "covered": len(covered),
        "denominator": denom,
        "threshold": threshold,
        "passed": coverage >= threshold,
        "asserted_total": len(asserted),
        "precision": None if precision is None else round(precision, 6),
        "asserted_in_available": len(covered),
        "asserted_outside_world": len(asserted) - in_world,
    }


# ---------------------------------------------------------------------------
# 3. The held-out limbs
# ---------------------------------------------------------------------------

def _pairs(events: list[str], lo: int, hi: int,
           epc: int = EVENTS_PER_CYCLE) -> tuple[list[list[str]], list[list[str]]]:
    idx = list(range(lo * epc, hi * epc))
    ctx = [sorted(events[i].split()) for i in idx[:-1]]
    obs = [sorted(events[i].split()) for i in idx[1:]]
    return ctx, obs


def limbs(world: dict, withheld=WITHHELD) -> dict[str, Any]:
    """Retention (all pairs) and transfer (only the withheld relations).

    The transfer limb is the point of the study: a pair is scored there only if
    its cell transition was withheld from every formation exposure, so a count
    of that transition has no support and a learner holding the law does.
    """
    blocked = set(withheld)
    events = world["events"]
    ret_ctx, ret_obs = _pairs(events, *PHASE_RETENTION)
    tr_ctx, tr_obs = _pairs(events, *PHASE_TRANSFER)
    names = [_coord(c) for c in world["cells"]]
    lo, hi = PHASE_TRANSFER[0] * EVENTS_PER_CYCLE, PHASE_TRANSFER[1] * EVENTS_PER_CYCLE
    keep_ctx, keep_obs, kinds = [], [], defaultdict(int)
    for i in range(lo, hi - 1):
        src, dst = names[i], names[i + 1]
        kind = ("flip_p" if dst == flip_p(src)
                else "flip_q" if dst == flip_q(src) else None)
        if kind is None or (src, kind) not in blocked:
            continue
        keep_ctx.append(sorted(events[i].split()))
        keep_obs.append(sorted(events[i + 1].split()))
        kinds[kind] += 1
    return {
        "retention": (ret_ctx, ret_obs),
        "transfer": (keep_ctx, keep_obs),
        "transfer_full": (tr_ctx, tr_obs),
        "transfer_instances": dict(kinds),
        "transfer_pairs": len(keep_ctx),
    }


# ---------------------------------------------------------------------------
# 4. The ceiling
# ---------------------------------------------------------------------------

def latent_rule_holder(world: dict, regime: int = 0) -> Callable[[str, str], float]:
    """The ceiling of §14, closed form: P(tag | context cell) = 0.5 x LAW[kind].

    Given the law and the grid, with no learning and no engine.  A learner that
    knows only one transition type does not hold the rule, so this is the full
    mixture and nothing weaker.
    """
    law = LAW_R0 if regime == 0 else {"flip_p": LAW_R0["flip_q"],
                                      "flip_q": LAW_R0["flip_p"]}
    cond = {c: {k: law[k] * (2 / TAGS_PER_CELL) for k in KINDS} for c in CELLS}
    tag_to_cell = {t: _coord(c) for t, c in world["tag_to_cell"].items()}

    def prob(u: str, v: str) -> float:
        src, dst = tag_to_cell.get(u), tag_to_cell.get(v)
        if src is None or dst is None or src == dst:
            return 0.0
        kind = "flip_p" if dst[0] != src[0] else "flip_q"
        return cond[src][kind]
    return prob


def broken_rule_holder(world: dict) -> Callable[[str, str], float]:
    """The control the endpoint must reject: right grid, one transition type.

    This is the mistake the withheld cell invites — its flip-P transitions are
    exactly what formation never showed — so a harness whose transfer limb
    cannot separate this from the ceiling is not measuring the law.
    """
    tag_to_cell = {t: _coord(c) for t, c in world["tag_to_cell"].items()}

    def prob(u: str, v: str) -> float:
        src, dst = tag_to_cell.get(u), tag_to_cell.get(v)
        if src is None or dst is None or src == dst:
            return 0.0
        return 0.99 * (2 / TAGS_PER_CELL) if dst[0] != src[0] else 0.01 * (2 / TAGS_PER_CELL)
    return prob


# ---------------------------------------------------------------------------
# 5. The comparators, swept on a tuning split
# ---------------------------------------------------------------------------

def _tuning_pairs(rows: list[str]) -> tuple[list[list[str]], list[list[str]]]:
    tune = rows[-TUNE_CYCLES * EVENTS_PER_CYCLE:]
    ctx = [sorted(tune[i].split()) for i in range(len(tune) - 1)]
    obs = [sorted(tune[i + 1].split()) for i in range(len(tune) - 1)]
    return ctx, obs


def comparator_sweep(rows: list[str], fit_rows: list[str], vocab: set[str],
                     tag_to_cell: dict[str, str]) -> dict[str, Any]:
    """Every comparator swept over its declared grid; its BEST config is used.

    Selection is made on the tuning split, which is excluded from `fit_rows`;
    the winning configuration is then refit on all formation rows for scoring.
    A baseline is never handicapped (AGENTS rule 11).
    """
    tune_ctx, tune_obs = _tuning_pairs(rows)

    def best_of(kind: str) -> dict[str, Any]:
        grid = BIGRAM_GRID if kind == "bigram" else CELL_GRID
        best = None
        for alpha, half_life, window in grid:
            if kind == "bigram":
                p = fit_bigram(fit_rows, vocab, alpha, half_life, window)
            elif kind == "decayed_bigram":
                if half_life is None:
                    continue                     # a decayed table needs a half-life
                p = fit_bigram(fit_rows, vocab, alpha, half_life, window)
            else:
                p = fit_cell_counter(fit_rows, vocab, tag_to_cell, alpha,
                                     half_life, window)
            if not tune_ctx:
                best = best or (0.0, (alpha, half_life, window), p)
                continue
            s = score(p, tune_ctx, tune_obs, vocab)["log_loss"]
            if best is None or s < best[0]:
                best = (s, (alpha, half_life, window), p)
        tune_score, cfg, _ = best
        if kind == "bigram":
            fitted = fit_bigram(rows, vocab, *cfg)
        elif kind == "decayed_bigram":
            fitted = fit_bigram(rows, vocab, *cfg)
        else:
            fitted = fit_cell_counter(rows, vocab, tag_to_cell, *cfg)
        return {"config": {"alpha": cfg[0], "half_life": cfg[1], "window": cfg[2]},
                "tuning_log_loss": round(tune_score, 6), "prob": fitted}

    best_replay = None
    from benchmarks.acquisition_runner import REPLAY_GRID  # noqa: PLC0415
    for window, half_life, alpha in REPLAY_GRID:
        p = fit_replay_learner(fit_rows, vocab, window, half_life, alpha)
        if not tune_ctx:
            best_replay = best_replay or (0.0, (window, half_life, alpha))
            continue
        s = score(p, tune_ctx, tune_obs, vocab)["log_loss"]
        if best_replay is None or s < best_replay[0]:
            best_replay = (s, (window, half_life, alpha))
    r_window, r_hl, r_alpha = best_replay[1]
    replay_prob = fit_replay_learner(rows, vocab, r_window, r_hl, r_alpha)

    return {
        "replay": {"config": {"window": r_window, "half_life": r_hl, "alpha": r_alpha},
                   "tuning_log_loss": round(best_replay[0], 6), "prob": replay_prob},
        "bigram": best_of("bigram"),
        "decayed_bigram": best_of("decayed_bigram"),
        "cell_counter": best_of("cell_counter"),
    }


# ---------------------------------------------------------------------------
# 6. One cell
# ---------------------------------------------------------------------------

def _scratch(seed: int) -> pathlib.Path:
    path = temp_db(f"rk_{seed}.db")
    if path.resolve() == LIVE_DB.resolve():
        raise AssertionError("refusing to write to the live DB")
    return path


def hash_seed() -> str | None:
    """The interpreter's string-hash seed, which the engine's ordering depends on.

    Candidate selection orders structures built from sets of strings, so two runs
    of the same seed can disagree unless the hash seed is fixed: calibration seed
    20261204 scored 0.60055 in one run and 0.6025 in another before this was
    pinned (journal §95).  The calibration that authorises the campaign therefore
    requires it.
    """
    import os
    return os.environ.get("PYTHONHASHSEED")


def variant_label(cap: int = MAX_PREDICTIONS) -> str:
    """The label is derived from the capacity, so a cap cannot borrow the name.

    §15.1 fixes the variant at 1,000 and says a different capacity is a
    different variant.  A diagnostic run at another cap therefore carries its
    own label; it must never be written up as `V1.1-cap(1000)`.
    """
    return VARIANT_NAME if cap == MAX_PREDICTIONS else f"V1.1-cap({cap})"


def _edge_weight(rows: dict[str, dict[str, float]]) -> float:
    return float(sum(w for targets in rows.values() for w in targets.values()))


def attribution_share(engine: dict) -> dict[str, Any]:
    """Share of the readout's edge weight carried by Layer-1 predictions.

    The readout sums evidence over every structure type, so a transfer margin
    can in principle be carried by concepts, loops, phrases or hypotheses
    rather than by the learned transition structure.  This measures where the
    evidence is (§17).

    A readout with no edge weight has **no** share: it is reported as not
    measurable (`None`) and fails the gate — never as `0.0` (AGENTS rule 13).
    The `without_layer1_share` companion is the counterfactual in which the
    readout holds no Layer-1 evidence at all: it must fall below the minimum, or
    the gate is not wired to Layer-1 and is decoration (AGENTS rule 25).
    """
    per_type = {t: _edge_weight(rows)
                for t, rows in (engine.get("type_rows") or {}).items()}
    total = sum(per_type.values())
    layer1 = per_type.get(LAYER1_TYPE, 0.0)
    other = total - layer1
    share = (layer1 / total) if total > 0 else None
    without = 0.0 if other > 0 else None
    return {
        "layer1_type": LAYER1_TYPE,
        "share": None if share is None else round(share, 6),
        "per_type_weight": {t: round(w, 6) for t, w in sorted(per_type.items())},
        "total_weight": round(total, 6),
        "minimum": ATTRIBUTION_MINIMUM,
        "without_layer1_share": without,
        "passed": share is not None and share >= ATTRIBUTION_MINIMUM,
        "reason": ("the structure type the study is about must carry the majority "
                   "of the readout's edge weight"),
    }


def run_engine(formation: dict, seed: int, cap: int = MAX_PREDICTIONS) -> dict[str, Any]:
    """Formation exposure on the conditioned stream, then the frozen readout.

    The variant differs from V1 in the Layer-1 truncation only.  `organica/` is
    untouched; the subclass is `acquisition_harness.CapOverrideSleepService`,
    the same instrument the paired capacity diagnostic used.
    """
    db = _scratch(seed)
    mem = MemoryService(str(db))
    svc = CapOverrideSleepService(mem, max_predictions=cap)
    epc = EVENTS_PER_CYCLE
    try:
        for i, text in enumerate(formation["events"]):
            mem.store(text, event_type="observe", source="env")
            if (i + 1) % epc == 0:
                svc.run_sleep_cycle()
                mem.prune_sleep_candidates()
        frozen = svc._load_prior_candidates()
        rows = structure_edges(frozen)
        asserted = {(u, v) for u, targets in rows.items() for v in targets}
        temporal = {(u, v) for u, v, _n in mem.temporal_edges(min_count=1)}
        by_type: dict[str, list[dict]] = defaultdict(list)
        for c in frozen:
            by_type[c.get("type", "")].append(c)
        type_rows = {t: structure_edges(cs) for t, cs in by_type.items()}
    finally:
        mem._conn.close()
        try:
            db.unlink(missing_ok=True)
        except PermissionError:
            pass
    return {"asserted_rows": rows, "asserted": asserted, "temporal": temporal,
            "type_rows": type_rows, "cap": cap,
            "formation_events": len(formation["events"])}


def run_cell(seed: int, cap: int = MAX_PREDICTIONS,
             withheld=WITHHELD) -> dict[str, Any]:
    """One seed: conditioned formation, Gate F, and every arm on both limbs."""
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    formation = conditioned_formation_stream(world, seed, withheld)
    relations = relation_sets(world, withheld)
    held = limbs(world, withheld)

    rows = formation["events"]
    split = len(rows) - TUNE_CYCLES * EVENTS_PER_CYCLE
    fit_rows = rows[:split]
    vocab = {t for r in rows for t in r.split()}

    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        for t in r.split():
            counts[t] += 1
    total = sum(counts.values()) or 1
    base_rate = {t: n / total for t, n in counts.items()}

    engine = run_engine(formation, seed, cap)
    gate = gate_f(engine["asserted"], relations)

    arms: dict[str, Any] = {}
    organica_prob = make_organica_backoff(engine["asserted_rows"], base_rate, ALPHA)
    arms["organica"] = {"prob": organica_prob, "privileged": False,
                        "config": {"alpha": ALPHA, "cap": cap}}
    comps = comparator_sweep(rows, fit_rows, vocab, world["tag_to_cell"])
    for name in ("replay", "bigram", "decayed_bigram", "cell_counter"):
        arms[name] = {"prob": comps[name]["prob"],
                      "privileged": name == "cell_counter",
                      "config": comps[name]["config"],
                      "tuning_log_loss": comps[name]["tuning_log_loss"]}
    arms["ceiling"] = {"prob": latent_rule_holder(world), "privileged": False,
                       "config": {"holder": "full latent rule"}}

    scores: dict[str, dict] = {}
    for name, arm in arms.items():
        scores[name] = {
            limb: score(arm["prob"], ctx, obs, vocab)["log_loss"]
            for limb, (ctx, obs) in (("retention", held["retention"]),
                                     ("transfer", held["transfer"]))
        }
    # The comparison the protocol asks for: the best NON-privileged comparator.
    primary = ["replay", "bigram", "decayed_bigram"]
    best_primary = min(primary, key=lambda n: scores[n]["transfer"])

    return {
        "kind": "reusable_knowledge_cell",
        "variant": variant_label(cap),
        "cap": cap,
        "cap_is_canonical": cap == MAX_PREDICTIONS,
        "pythonhashseed": hash_seed(),
        "seed": seed,
        "gate_f": gate,
        "attribution": attribution_share(engine),
        "formation": {
            "events": len(rows),
            "cycles": formation_cycles(),
            "withheld": formation["withheld"],
            "compensated_events": formation["compensated"],
            "transitions_observed": formation["observed"],
        },
        "relations": {
            "available": len(relations["available"]),
            "withheld": len(relations["withheld"]),
            "total": len(relations["all"]),
        },
        "held_out": {
            "retention_pairs": len(held["retention"][0]),
            "transfer_pairs": held["transfer_pairs"],
            "transfer_instances": held["transfer_instances"],
        },
        "engine": {"cap": engine["cap"], "asserted_pairs": len(engine["asserted"]),
                   "temporal_pairs": len(engine["temporal"])},
        "scores": {name: {limb: round(v, 6) for limb, v in s.items()}
                   for name, s in scores.items()},
        "privileged_reference": "cell_counter",
        "best_primary_comparator": best_primary,
        "organica_minus_best_primary": round(
            scores[best_primary]["transfer"] - scores["organica"]["transfer"], 6),
        "organica_minus_ceiling": round(
            scores["ceiling"]["transfer"] - scores["organica"]["transfer"], 6),
        "calibration_passed": bool(gate["passed"]),
    }


# ---------------------------------------------------------------------------
# 7. The audit — the harness must be able to fail
# ---------------------------------------------------------------------------

def harness_audit(cell: dict, world: dict, withheld=WITHHELD) -> dict[str, Any]:
    """Four checks that each CAN fail, run on an already-computed cell.

    E1  the endpoint separates the law from a one-transition learner
    E2  Gate F fires on a degraded readout (coverage, not a rubber stamp)
    E3  the conditioning actually removed the withheld transitions
    E4  every limb has a denominator to be scored against
    E5  the attribution share is measured, and its gate can fire
    """
    held = limbs(world, withheld)
    vocab = {t for r in world["events"] for t in r.split()}
    tr_ctx, tr_obs = held["transfer"]
    ceil = score(latent_rule_holder(world), tr_ctx, tr_obs, vocab)["log_loss"]
    broken = score(broken_rule_holder(world), tr_ctx, tr_obs, vocab)["log_loss"]
    e1 = broken > ceil

    available = relation_sets(world, withheld)["available"]
    keep = len(available) - int(0.10 * len(available))
    degraded = set(sorted(available)[:keep])          # drop ~10 % of coverage
    degraded_gate = gate_f(degraded, relation_sets(world, withheld))
    e2 = (not degraded_gate["passed"]) and cell["gate_f"]["threshold"] == GATE_F_THRESHOLD

    blocked = {f"{c}|{k}" for c, k in withheld}
    observed = cell["formation"]["transitions_observed"]
    e3 = all(observed.get(key, 0) == 0 for key in blocked) and \
        cell["formation"]["compensated_events"] > 0

    e4 = (cell["held_out"]["retention_pairs"] > 0
          and cell["held_out"]["transfer_pairs"] > 0)

    att = cell.get("attribution") or {}
    e5 = (bool(att.get("passed"))
          and att.get("without_layer1_share") is not None
          and att["without_layer1_share"] < att.get("minimum", ATTRIBUTION_MINIMUM))

    checks = {
        "E1_endpoint_separates_the_law": {
            "passed": e1, "ceiling_transfer": round(ceil, 6),
            "broken_rule_transfer": round(broken, 6),
            "reason": "a one-transition learner must score worse than the ceiling"},
        "E2_gate_f_can_fire": {
            "passed": e2, "degraded_coverage": degraded_gate["coverage"],
            "degraded_passed": degraded_gate["passed"],
            "reason": "dropping ~10 % of the available relations must fail Gate F"},
        "E3_conditioning_removed_the_withheld": {
            "passed": e3, "compensated_events": cell["formation"]["compensated_events"],
            "reason": "no withheld transition may appear in any formation exposure"},
        "E4_limbs_have_denominators": {
            "passed": e4, "retention_pairs": cell["held_out"]["retention_pairs"],
            "transfer_pairs": cell["held_out"]["transfer_pairs"],
            "reason": "a limb with no pairs is not measurable, not zero"},
        "E5_attribution_share_can_fire": {
            "passed": e5, "share": att.get("share"),
            "without_layer1_share": att.get("without_layer1_share"),
            "minimum": att.get("minimum", ATTRIBUTION_MINIMUM),
            "reason": ("a readout with no Layer-1 evidence must fall below the "
                       "minimum, or the gate is decoration")},
    }
    return {"all_passed": all(c["passed"] for c in checks.values()),
            "checks": checks}


# ---------------------------------------------------------------------------
# 8. Calibration, and the confirmatory guard
# ---------------------------------------------------------------------------

def _load_calibration() -> dict | None:
    path = ROOT / CALIBRATION_OUT
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def confirmatory_allowed() -> tuple[bool, str]:
    """Confirmatory seeds are refused unless the CANONICAL calibration passed.

    The guard checks the artifact's **capacity, variant and seed set**, not only
    its pass flag.  A calibration run at another cap carries another label
    (§15.1), and authorising the confirmatory set from it would attribute those
    cells to a variant that was never calibrated — the same class of defect as
    two gates sharing one name (AGENTS rule 25).
    """
    cal = _load_calibration()
    if cal is None:
        return False, f"no calibration artifact at {CALIBRATION_OUT}"
    if cal.get("cap") != MAX_PREDICTIONS:
        return False, (f"calibration artifact is at cap {cal.get('cap')}, not "
                       f"{MAX_PREDICTIONS}: a different capacity is a different variant")
    if cal.get("variant") != VARIANT_NAME:
        return False, (f"calibration artifact is labelled {cal.get('variant')!r}, not "
                       f"{VARIANT_NAME!r}")
    if list(cal.get("seeds") or []) != list(CALIBRATION_SEEDS):
        return False, "the artifact's seed set is not the five calibration seeds"
    if not cal.get("all_seeds_passed"):
        failed = [c["seed"] for c in cal.get("cells", []) if not c["calibration_passed"]]
        return False, f"calibration did not pass on seeds {failed}"
    if not cal.get("audit_all_passed"):
        return False, "the harness audit did not pass on every calibration seed"
    if not (cal.get("attribution") or {}).get("all_seeds_passed"):
        return False, ("the attribution share did not reach its minimum on every "
                       "calibration seed")
    return True, "calibration passed on all five seeds, at the canonical cap and label"


def run_calibration(cap: int = MAX_PREDICTIONS) -> dict[str, Any]:
    """The gate of §15.2: V1.1-cap(1000) alone, all five seeds must pass.

    A different capacity is a different variant (§15.1), so it may not run the
    calibration that authorises the confirmatory set.  The artifact records the
    cap, the label derived from it, and whether it authorises anything.
    """
    if cap != MAX_PREDICTIONS:
        raise ValueError(
            f"calibration runs at MAX_PREDICTIONS={MAX_PREDICTIONS} only; cap {cap} "
            f"is a different variant and needs its own amendment (§15.1)")
    if hash_seed() is None:
        raise ValueError(
            "set PYTHONHASHSEED to a fixed value before calibrating: the engine's "
            "candidate ordering is hash-sensitive, and two identical runs were "
            "observed to disagree (journal §95)")
    cells = []
    for seed in CALIBRATION_SEEDS:
        world = generate_compositional_world(seed=seed, cycles=CYCLES)
        cell = run_cell(seed, cap)
        cell["audit"] = harness_audit(cell, world)
        cells.append(cell)
    passed = [c["seed"] for c in cells if c["calibration_passed"]]
    attribution_passed = [c["seed"] for c in cells if c["attribution"]["passed"]]
    art = {
        "kind": "reusable_knowledge_calibration",
        "variant": variant_label(cap),
        "cap": cap,
        "canonical_cap": cap == MAX_PREDICTIONS,
        "pythonhashseed": hash_seed(),
        "attribution": {
            "rule": "every calibration seed must reach the minimum share",
            "layer1_type": LAYER1_TYPE,
            "minimum": ATTRIBUTION_MINIMUM,
            "seeds_passing": attribution_passed,
            "all_seeds_passed": len(attribution_passed) == len(CALIBRATION_SEEDS),
            "scope": "V1.1-cap(1000) only",
        },
        "gate": {
            "denominator": GATE_F_DENOMINATOR,
            "threshold": GATE_F_THRESHOLD,
            "rule": "all five calibration seeds must pass",
            "scope": "V1.1-cap(1000) only",
        },
        "seeds": list(CALIBRATION_SEEDS),
        "burned": list(BURNED_SEEDS),
        "cells": cells,
        "seeds_passed": passed,
        "all_seeds_passed": len(passed) == len(CALIBRATION_SEEDS),
        "audit_all_passed": all(c["audit"]["all_passed"] for c in cells),
        "confirmatory_seeds_touched": False,
        "authorises_confirmatory": (
            cap == MAX_PREDICTIONS
            and len(passed) == len(CALIBRATION_SEEDS)
            and len(attribution_passed) == len(CALIBRATION_SEEDS)
            and all(c["audit"]["all_passed"] for c in cells)),
        "note": (
            "Calibration is a go/no-go at n = 5 (section 15.2). A failure here "
            "is reported as formation not achieved at the calibration operating "
            "point and stops the study before any confirmatory seed."),
    }
    (ROOT / CALIBRATION_OUT).write_text(
        json.dumps(art, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return art


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Reusable-knowledge harness (§10).")
    ap.add_argument("--calibration", action="store_true",
                    help="run the five calibration seeds (the Gate F go/no-go)")
    ap.add_argument("--seed", type=int, default=None,
                    help="run one seed (must not be a confirmatory seed)")
    ap.add_argument("--cap", type=int, default=MAX_PREDICTIONS)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.calibration and args.cap != MAX_PREDICTIONS:
        print(f"refusing to calibrate at cap {args.cap}: calibration runs at "
              f"MAX_PREDICTIONS={MAX_PREDICTIONS} only, cap {args.cap} is a different "
              f"variant (§15.1), and the label {variant_label(args.cap)!r} authorises "
              f"nothing.", file=sys.stderr)
        return 4

    if args.calibration and hash_seed() is None:
        print("refusing to calibrate with PYTHONHASHSEED unset: the engine's candidate "
              "ordering is hash-sensitive, so the gate would not be reproducible "
              "(journal §95). Re-run as `PYTHONHASHSEED=0 python -m "
              "benchmarks.reusable_knowledge --calibration`.", file=sys.stderr)
        return 5

    if args.calibration:
        art = run_calibration(args.cap)
        print(json.dumps({k: art[k] for k in
                          ("seeds_passed", "all_seeds_passed",
                           "audit_all_passed", "confirmatory_seeds_touched")},
                         indent=1))
        for c in art["cells"]:
            print(f"  seed {c['seed']}  Gate F {c['gate_f']['coverage']:.4f} "
                  f"({'PASS' if c['gate_f']['passed'] else 'FAIL'})  "
                  f"transfer: organica {c['scores']['organica']['transfer']:.4f} "
                  f"vs {c['best_primary_comparator']} "
                  f"{c['scores'][c['best_primary_comparator']]['transfer']:.4f}  "
                  f"ceiling {c['scores']['ceiling']['transfer']:.4f}")
        return 0 if art["all_seeds_passed"] else 2

    seed = args.seed if args.seed is not None else CALIBRATION_SEEDS[0]
    if seed in CONFIRMATORY_SEEDS or seed in BURNED_SEEDS:
        ok, why = confirmatory_allowed()
        if not ok:
            print(f"refusing seed {seed}: {why}", file=sys.stderr)
            return 3
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    cell = run_cell(seed, args.cap)
    cell["audit"] = harness_audit(cell, world)
    if args.json:
        print(json.dumps(cell, indent=1, sort_keys=True))
    else:
        print(f"{variant_label(args.cap)} seed {seed}")
        print(f"  Gate F {cell['gate_f']['coverage']:.4f} "
              f"({cell['gate_f']['covered']}/{cell['gate_f']['denominator']}) "
              f"{'PASS' if cell['gate_f']['passed'] else 'FAIL'}"
              f"  precision {cell['gate_f']['precision']}")
        print(f"  held-out transfer pairs: {cell['held_out']['transfer_pairs']}")
        for name, s in sorted(cell["scores"].items()):
            print(f"  {name:<14} retention {s['retention']:.6f}  "
                  f"transfer {s['transfer']:.6f}")
        print(f"  audit: {'PASS' if cell['audit']['all_passed'] else 'FAIL'}")
    return 0 if cell["audit"]["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
