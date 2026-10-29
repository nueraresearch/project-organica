"""The compositional task's discriminativeness gate.

What this script must establish, BEFORE any cell of the acquisition
experiment is run:

  G1  the ceiling beats the STRONGEST simple baseline by a margin whose
      LOWER UNCERTAINTY BOUND clears 0.05 nats across independent worlds;
  G2  the positive control — a learner holding the generating rule —
      reaches the ceiling;
  G3  the broken-rule control is clearly worse than the ceiling;
  G4  the withheld combination is genuinely withheld: no baseline has
      support for it in the training stream;
  G5  the ceiling and the baselines are monotone in the amount of
      structure they hold;
  G6  the held-out combination is not solvable by tag identity, because
      the tag-to-cell mapping is randomised per world;
  G7  THE WITHHELD COMBINATION IS WHAT CREATES THE GAP.  The gap on the
      held cell's own contexts must be far larger than the gap on the
      other cells' contexts.  Without this, the benchmark would be
      measuring estimation error rather than generalisation, and G1 would
      be passing for the wrong reason.

G1 is the gate that the previous probe got wrong: it compared the ceiling
against a BASE RATE, so it could pass while a bigram table was within
0.0275 nats of the ceiling.

Read-only.  No engine run.  Standard library only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.acquisition_baselines import (  # noqa: E402
    bootstrap_lower_bound, fit_base_rate, score, select_best,
)
from benchmarks.acquisition_compositional import (  # noqa: E402
    PHASE_ACQUISITION, PHASE_REVISION_LEARN, PHASE_REVISION_TEST,
    PHASE_RETENTION, PHASE_TRANSFER, generate_compositional_world,
    make_broken_rule, make_ceiling, make_rule_holder, make_swapped_law,
)

EPC = 8
GATE = 0.05
N_WORLDS = 30
SEED0 = 20261200


def ll(prob, ctx, obs, vocab):
    """The float log-loss, for the places where only the loss is used."""
    return score(prob, ctx, obs, vocab)["log_loss"]


def idx(phase):
    lo, hi = phase
    return list(range(lo * EPC, hi * EPC))


def win(events, ii):
    return ([sorted(events[ii[k]].split()) for k in range(len(ii) - 1)],
            [sorted(events[ii[k + 1]].split()) for k in range(len(ii) - 1)])


def main() -> int:
    print("=" * 78)
    print("COMPOSITIONAL TASK — DISCRIMINATIVENESS GATE")
    print("=" * 78)
    print(f"  worlds: {N_WORLDS}   gate: lower bound of the gap > {GATE} nats")
    print()

    rows = []
    g1_worlds = 0
    for k in range(N_WORLDS):
        seed = SEED0 + k
        w = generate_compositional_world(seed=seed)
        events = w["events"]
        trainable = w["trainable"]

        acq = idx(PHASE_ACQUISITION)
        # the TUNING SPLIT: the tail of the acquisition phase, still training
        tune = acq[-20 * EPC:]
        # the PRIMARY TEST SPLIT: the withheld combination, same law, frozen
        # state -- the transfer window, scored on the held cell's contexts
        transfer = idx(PHASE_TRANSFER)

        # the training stream: acquisition events, minus the withheld ones
        train_rows = [events[i] for i in acq if trainable[i]]
        vocab = {t for e in train_rows for t in e.split()}

        tune_ctx, tune_obs = win(events, tune)
        test_ctx, test_obs = win(events, transfer)

        # --- references -------------------------------------------------
        ceil = make_ceiling(w, 0)
        pos = make_rule_holder(w, 0)
        broken = make_broken_rule(w, 0)
        swapped = make_swapped_law(w, 0)

        r_ceil = ll(ceil, test_ctx, test_obs, vocab)
        r_pos = ll(pos, test_ctx, test_obs, vocab)
        r_broken = ll(broken, test_ctx, test_obs, vocab)
        r_swapped = ll(swapped, test_ctx, test_obs, vocab)

        # --- baselines, selected on the TUNING SPLIT --------------------
        b_base = fit_base_rate(train_rows, vocab)
        r_base = ll(b_base, test_ctx, test_obs, vocab)

        b_bigram, cfg_bigram, p_bigram = select_best(
            "bigram", train_rows, vocab, w["tag_to_cell"],
            tune_ctx, tune_obs)
        r_bigram = ll(p_bigram, test_ctx, test_obs, vocab)

        b_cell, cfg_cell, p_cell = select_best(
            "cell", train_rows, vocab, w["tag_to_cell"],
            tune_ctx, tune_obs)
        r_cell = ll(p_cell, test_ctx, test_obs, vocab)

        best_simple = min(r_base, r_bigram, r_cell)
        best_name = min(
            (("base_rate", r_base), ("bigram", r_bigram), ("cell_counter", r_cell)),
            key=lambda t: t[1])[0]
        gap = best_simple - r_ceil

        # ---- G7: is the WITHHELD COMBINATION what creates the gap? -------
        # Score the test split twice: once on the contexts whose cell is
        # the HELD cell, and once on the contexts whose cell is not.  If the
        # benchmark is measuring generalisation, the held cell's gap must be
        # far larger than the rest.  If they are similar, the gap is generic
        # estimation error and the benchmark is measuring the wrong thing.
        held_cells = set(w["held_cell_tags"])
        held_ctx, held_obs = [], []
        other_ctx, other_obs = [], []
        for ctx, obs in zip(test_ctx, test_obs):
            if set(ctx) & held_cells:
                held_ctx.append(ctx)
                held_obs.append(obs)
            else:
                other_ctx.append(ctx)
                other_obs.append(obs)
        if held_ctx and other_ctx:
            h_ceil = ll(ceil, held_ctx, held_obs, vocab)
            h_best = min(ll(b_base, held_ctx, held_obs, vocab),
                         ll(p_bigram, held_ctx, held_obs, vocab),
                         ll(p_cell, held_ctx, held_obs, vocab))
            o_ceil = ll(ceil, other_ctx, other_obs, vocab)
            o_best = min(ll(b_base, other_ctx, other_obs, vocab),
                         ll(p_bigram, other_ctx, other_obs, vocab),
                         ll(p_cell, other_ctx, other_obs, vocab))
            gap_held = h_best - h_ceil
            gap_other = o_best - o_ceil
        else:
            gap_held = gap_other = float("nan")

        # G4: is the withheld combination genuinely unsupported?
        held = w["held_cell"]
        held_tags = set(w["held_cell_tags"])
        # did the training stream contain the held cell as a context at all?
        held_contexts = sum(1 for i in acq
                             if trainable[i]
                             and set(events[i].split()) & held_tags)
        # The withheld transition is: the held cell as the CONTEXT of an
        # event whose SUCCESSOR is the held cell's flip-P neighbour.  In
        # the generator that is the event flagged `withheld`, so the check
        # is: no event flagged withheld may be in the training stream, and
        # no retained acquisition event may sit between a held-cell context
        # and its flip-P successor.
        flagged = [i for i in acq if w["withheld"][i]]
        flagged_in_training = [i for i in flagged if trainable[i]]
        # and, independently: is a held->flip_p transition still observable
        # in the retained stream?  count consecutive retained pairs.
        retained = [i for i in acq if trainable[i]]
        retained_set = set(retained)
        flip_p_tags = set(w["cell_tags"][w["held_cell_flip_p"]])
        still_present = 0
        for a, b in zip(retained, retained[1:]):
            if b != a + 1:
                continue          # not consecutive in the raw stream
            if (set(events[a].split()) & held_tags
                    and set(events[b].split()) & flip_p_tags):
                still_present += 1

        rows.append({
            "seed": seed,
            "held_cell": held,
            "ceiling": r_ceil,
            "positive_control": r_pos,
            "broken_control": r_broken,
            "swapped_law_control": r_swapped,
            "base_rate": r_base,
            "bigram": r_bigram,
            "bigram_cfg": cfg_bigram,
            "cell_counter": r_cell,
            "cell_cfg": cfg_cell,
            "best_simple": best_simple,
            "best_simple_name": best_name,
            "gap": round(gap, 6),
            "held_context_events_in_training": held_contexts,
            "withheld_transitions_still_in_training": still_present,
            "withheld_events_flagged": len(flagged),
            "withheld_flagged_but_in_training": len(flagged_in_training),
            "gap_on_held_cell": round(gap_held, 6),
            "gap_on_other_cells": round(gap_other, 6),
        })

        if k < 3 or k == N_WORLDS - 1:
            print(f"  world {k:>2} (seed {seed}) held={held}")
            print(f"    ceiling {r_ceil:>8.4f}   positive {r_pos:>8.4f}   "
                  f"broken {r_broken:>8.4f}")
            print(f"    base {r_base:>8.4f}   bigram {r_bigram:>8.4f}   "
                  f"cell {r_cell:>8.4f}   -> best simple: {best_name} "
                  f"{best_simple:.4f}")
            print(f"    GAP {gap:+.4f} nats")
            print(f"    held-cell context events in training: {held_contexts}; "
                  f"withheld transitions still present: {still_present}")
            print()

    # ---- G1 ------------------------------------------------------------
    gaps = [r["gap"] for r in rows]
    mean, lo, hi = bootstrap_lower_bound(gaps)
    g1 = lo > GATE
    print("=" * 78)
    print("G1  CEILING vs THE STRONGEST SIMPLE BASELINE")
    print("=" * 78)
    print(f"  mean gap      {mean:+.4f} nats")
    print(f"  99% interval  [{lo:+.4f}, {hi:+.4f}]")
    print(f"  lower bound must clear {GATE} nats: "
          f"{'PASS' if g1 else 'FAIL'}")
    best_counts: dict[str, int] = {}
    for r in rows:
        best_counts[r["best_simple_name"]] = best_counts.get(
            r["best_simple_name"], 0) + 1
    print(f"  the best simple baseline was: {best_counts}")

    # ---- G2, G3 --------------------------------------------------------
    g2 = max(abs(r["ceiling"] - r["positive_control"]) for r in rows) < 1e-6
    g3 = min(r["broken_control"] - r["ceiling"] for r in rows)
    g3_ok = g3 > GATE
    # the near-miss control is a SENSITIVITY measurement, not a gate
    sw = [r["swapped_law_control"] - r["ceiling"] for r in rows]
    sw_mean, sw_lo, sw_hi = bootstrap_lower_bound(sw)
    print()
    print("=" * 78)
    print("G2 / G3  THE CONTROLS")
    print("=" * 78)
    print(f"  G2  positive control reaches the ceiling: "
          f"{'PASS' if g2 else 'FAIL'}")
    print(f"  G3  broken-rule control (latched onto one transition type) is "
          f"worse than the ceiling by at least {g3:+.4f} nats: "
          f"{'PASS' if g3_ok else 'FAIL'}")
    print()
    print("  SENSITIVITY (reported, not gated): a control with the right")
    print("  structure but the two transition weights swapped is only")
    print(f"  {sw_mean:+.4f} nats worse [{sw_lo:+.4f}, {sw_hi:+.4f}].")
    print("  So the endpoint resolves the LAW'S STRUCTURE sharply and its")
    print("  exact WEIGHTS only weakly.  That is a resolution fact about")
    print("  the endpoint, and it bounds what a result can claim.")

    # ---- G4 ------------------------------------------------------------
    g4 = all(r["withheld_transitions_still_in_training"] == 0 for r in rows)
    g4b = all(r["held_context_events_in_training"] > 0 for r in rows)
    g4c = all(r["withheld_flagged_but_in_training"] == 0 for r in rows)
    g4d = all(r["withheld_events_flagged"] > 0 for r in rows)
    print()
    print("=" * 78)
    print("G4  THE WITHHELD COMBINATION IS GENUINELY WITHHELD")
    print("=" * 78)
    print(f"  no withheld transition appears in the training stream: "
          f"{'PASS' if g4 else 'FAIL'}")
    print(f"  every event the generator flagged as withheld is excluded from "
          f"the training stream: {'PASS' if g4c else 'FAIL'}")
    print(f"  every world actually withheld something (the split is not "
          f"empty): {'PASS' if g4d else 'FAIL'}")
    print(f"  the held cell still appears as a context in training (so the "
          f"world is not rigged): {'PASS' if g4b else 'FAIL'}")

    # ---- G5 ------------------------------------------------------------
    g5 = True
    for r in rows:
        if not (r["ceiling"] < r["cell_counter"] and r["cell_counter"] < r["base_rate"]):
            g5 = False
            break
    print()
    print("=" * 78)
    print("G5  MONOTONE IN STRUCTURE")
    print("=" * 78)
    print(f"  ceiling < cell counter < base rate, in every world: "
          f"{'PASS' if g5 else 'FAIL'}")

    # ---- G6 ------------------------------------------------------------
    held_cells = {r["held_cell"] for r in rows}
    g6 = len(held_cells) >= 3
    print()
    print("=" * 78)
    print("G6  THE HELD CELL VARIES ACROSS WORLDS")
    print("=" * 78)
    print(f"  distinct held cells across {N_WORLDS} worlds: {len(held_cells)} "
          f"{sorted(held_cells)}")
    print(f"  -> {'PASS' if g6 else 'FAIL'} (the tag-to-cell mapping is "
          f"randomised per world)")

    # ---- G7: the withheld combination is what creates the gap ------------
    gh = [r["gap_on_held_cell"] for r in rows if r["gap_on_held_cell"] == r["gap_on_held_cell"]]
    go = [r["gap_on_other_cells"] for r in rows if r["gap_on_other_cells"] == r["gap_on_other_cells"]]
    mh, loh, hih = bootstrap_lower_bound(gh)
    mo, loo, hio = bootstrap_lower_bound(go)
    g7 = loh > max(loo, 0.0) and loh > 0.05
    print()
    print("=" * 78)
    print("G7  THE WITHHELD COMBINATION IS WHAT CREATES THE GAP")
    print("=" * 78)
    print(f"  gap on the HELD cell's contexts    {mh:+.4f} "
          f"[{loh:+.4f}, {hih:+.4f}]")
    print(f"  gap on the OTHER cells' contexts   {mo:+.4f} "
          f"[{loo:+.4f}, {hio:+.4f}]")
    print(f"  the held cell's lower bound must exceed both the other cells' "
          f"lower bound and 0.05: {'PASS' if g7 else 'FAIL'}")
    print("  (without this, G1 could be passing because of generic")
    print("   estimation error rather than because of generalisation)")

    checks = {"G1_gap_lower_bound_clears_gate": bool(g1),
              "G2_positive_control_reaches_ceiling": bool(g2),
              "G3_broken_control_is_worse": bool(g3_ok),
              "G4_withheld_combination_absent_from_training": bool(g4),
              "G4b_held_cell_still_observed": bool(g4b),
              "G4c_flagged_events_all_excluded": bool(g4c),
              "G4d_split_is_not_empty": bool(g4d),
              "G5_monotone_in_structure": bool(g5),
              "G6_held_cell_varies_across_worlds": bool(g6),
              "G7_withheld_combination_drives_the_gap": bool(g7)}

    out = {"n_worlds": N_WORLDS, "gate_nats": GATE,
           "mean_gap": mean, "gap_lower_99": lo, "gap_upper_99": hi,
           "gap_on_held_cell": {"mean": mh, "lower_99": loh, "upper_99": hih},
           "gap_on_other_cells": {"mean": mo, "lower_99": loo, "upper_99": hio},
           "best_simple_counts": best_counts,
           "broken_control_min_excess": round(g3, 6),
           "swapped_law_sensitivity": {"mean": sw_mean, "lower_99": sw_lo,
                                       "upper_99": sw_hi},
           "checks": checks, "per_world": rows}
    dest = REPO / "docs" / "acquisition_compositional_gate.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\n  wrote {dest.relative_to(REPO)}")
    allok = all(checks.values())
    print(f"  ALL CHECKS: {'PASS' if allok else 'FAIL — the study does not run'}")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
