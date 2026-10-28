"""Proof-of-firing for the acquisition endpoint's instrument requirements.

Revision 3 §9 of `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` requires the
endpoint to be shown to work BEFORE any cell runs, and requires that every
check has a **proof of firing**: a variant in which the check fails.

A check that cannot fail is decoration.  These tests are the guard.

Two worlds are covered:

* the **transition** world (`benchmarks/acquisition_world.py`) — a
  CALIBRATION / CONTROL task.  It tests ordinary transition learning and
  law-change adaptation.  It is NOT evidence of abstraction beyond counts,
  because its law is first-order Markov and a bigram table is its natural
  learner.
* the **compositional** world (`benchmarks/acquisition_compositional.py`) —
  the PRIMARY task.  It withholds a COMBINATION of familiar elements, so
  the gap between the Bayes ceiling and the strongest count-based baseline
  is created by generalisation rather than by estimation error.

They are deliberately cheap: they use the world generators and the scoring
code, not the engine.  The engine-level check lives in
`tests/test_audit_trace_probe.py`'s pattern and is not duplicated here.
"""
from __future__ import annotations

import math
import sys
import unittest
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.acquisition_baselines import (  # noqa: E402
    fit_base_rate, fit_bigram, fit_cell_counter, score, select_best,
)
from benchmarks.acquisition_compositional import (  # noqa: E402
    PHASE_ACQUISITION as COMP_ACQ,
    PHASE_TRANSFER as COMP_TRANSFER,
    generate_compositional_world, make_broken_rule, make_ceiling,
    make_rule_holder, make_swapped_law,
)
from benchmarks.acquisition_world import (  # noqa: E402
    GROUPS, NOISE_TAGS, PHASE_ACQUISITION, PHASE_RETENTION, PHASE_REVISION,
    generate_rule_world, group_of, next_event_distribution,
)

EPS = 1e-12
EPC = 8
GATE = 0.05


# ---------------------------------------------------------------------------
# The transition world — calibration / control
# ---------------------------------------------------------------------------

class TransitionWorldTests(unittest.TestCase):
    """Every test here must FAIL when the thing it guards is broken."""

    @classmethod
    def setUpClass(cls):
        cls.w = generate_rule_world(seed=20261100, events_per_cycle=EPC)
        cls.events = cls.w["events"]

        def idx(phase):
            lo, hi = phase
            return list(range(lo * EPC, hi * EPC))

        cls.acq = idx(PHASE_ACQUISITION)
        cls.ret = idx(PHASE_RETENTION)
        cls.rev = idx(PHASE_REVISION)
        cls.tune = list(range((PHASE_ACQUISITION[1] - 20) * EPC,
                              PHASE_ACQUISITION[1] * EPC))
        cls.vocab = {t for e in (cls.events[i] for i in cls.acq) for t in e.split()}

        def win(ii):
            ctx = [sorted(cls.events[ii[k]].split()) for k in range(len(ii) - 1)]
            obs = [sorted(cls.events[ii[k + 1]].split()) for k in range(len(ii) - 1)]
            return ctx, obs

        cls.ret_ctx, cls.ret_obs = win(cls.ret)
        cls.rev_ctx, cls.rev_obs = win(cls.rev)
        cls.tune_ctx, cls.tune_obs = win(cls.tune)
        cls.d0 = next_event_distribution(0)
        cls.d1 = next_event_distribution(1)
        cls.acq_rows = [cls.events[i] for i in cls.acq]

    # ---- helpers ---------------------------------------------------------
    def _ceiling(self, regime):
        d = self.d0 if regime == 0 else self.d1
        return lambda u, v: d.get(group_of([u]), {}).get(v, 0.0)

    def _base_rate(self):
        cnt = defaultdict(int)
        for i in self.acq:
            for t in self.events[i].split():
                cnt[t] += 1
        tot = sum(cnt.values())
        base = {t: n / tot for t, n in cnt.items()}
        return lambda u, v: base.get(v, 0.0)

    def _trivial(self, u, v):
        return 0.0

    def _strongest_baseline(self):
        """The best of the strong simple baselines, each swept on the tuning
        split.  This is the comparator I2 must be measured against."""
        tag_to_group = {}
        for g, members in GROUPS.items():
            for t in members:
                tag_to_group[t] = g
        cands = {"base_rate": fit_base_rate(self.acq_rows, self.vocab)}
        _, _, p_big = select_best("bigram", self.acq_rows, self.vocab, {},
                                  self.tune_ctx, self.tune_obs)
        cands["bigram"] = p_big
        _, _, p_cell = select_best("cell", self.acq_rows, self.vocab,
                                   tag_to_group, self.tune_ctx, self.tune_obs)
        cands["cell_counter"] = p_cell
        return {k: score(v, self.ret_ctx, self.ret_obs, self.vocab)["log_loss"]
                for k, v in cands.items()}

    # ---- I1: non-degenerate ---------------------------------------------
    def test_I1_ceiling_beats_trivial(self):
        """The endpoint must distinguish a model that knows the law from one
        that knows nothing.  PROOF OF FIRING: the trivial model is scored and
        the gap is asserted to be large; a degenerate endpoint scores them
        equally and this test fails."""
        c = score(self._ceiling(0), self.ret_ctx, self.ret_obs, self.vocab)
        t = score(self._trivial, self.ret_ctx, self.ret_obs, self.vocab)
        self.assertLess(c["log_loss"], t["log_loss"],
                        "ceiling must beat trivial")
        self.assertGreater(t["log_loss"] - c["log_loss"], 0.5,
                           "the gap must be large, not marginal")

    def test_I1_monotone_in_structure(self):
        """More structure must not hurt.  PROOF OF FIRING: the three models
        are ordered, and the ordering is asserted."""
        c = score(self._ceiling(0), self.ret_ctx, self.ret_obs, self.vocab)
        b = score(self._base_rate(), self.ret_ctx, self.ret_obs, self.vocab)
        t = score(self._trivial, self.ret_ctx, self.ret_obs, self.vocab)
        self.assertGreater(t["log_loss"], b["log_loss"],
                           "base rate must beat trivial")
        self.assertGreater(b["log_loss"], c["log_loss"],
                           "the law must beat the base rate")

    # ---- I2: the world's classification ---------------------------------
    def test_I2_transition_world_is_classified_calibration(self):
        """The transition world's headroom over the STRONGEST simple
        baseline must be measured, and it must be BELOW the gate.

        PROOF OF FIRING: the gap is recomputed against the strongest
        baseline (a cell-level counter), not the base rate.  If a future
        change made the world discriminative, this test fails and the
        world's role must be re-examined.  The test that it must NOT be
        measured against the base rate is the one that catches the old
        defect, so both numbers are asserted here.
        """
        c = score(self._ceiling(0), self.ret_ctx, self.ret_obs, self.vocab)
        b = score(self._base_rate(), self.ret_ctx, self.ret_obs, self.vocab)
        strong = self._strongest_baseline()
        best = min(strong.values())
        gap_over_base = b["log_loss"] - c["log_loss"]
        gap_over_strong = best - c["log_loss"]
        # the OLD bar (base rate only) is comfortably satisfied ...
        self.assertGreater(gap_over_base, GATE)
        # ... but the CORRECT bar is not, which is why the world is
        # calibration-only.  If this ever becomes true, the world changed.
        self.assertLess(gap_over_strong, GATE,
                        "the transition world became discriminative — its role "
                        "in the protocol must be re-examined")

    def test_I2_base_rate_alone_would_pass_and_is_not_the_right_bar(self):
        """The defect this correction fixes, made explicit and guarded.

        PROOF OF FIRING: the base-rate gap exceeds the gate while the
        strongest-baseline gap does not.  If someone reverts the check to
        the base rate, this test still passes but the classification test
        above fails.  This test documents WHY the two differ.
        """
        c = score(self._ceiling(0), self.ret_ctx, self.ret_obs, self.vocab)
        b = score(self._base_rate(), self.ret_ctx, self.ret_obs, self.vocab)
        strong = self._strongest_baseline()
        gap_over_base = b["log_loss"] - c["log_loss"]
        gap_over_strong = min(strong.values()) - c["log_loss"]
        self.assertGreater(gap_over_base, gap_over_strong,
                           "the strong baseline must be at least as good as "
                           "the base rate")

    # ---- I4: the metric and readout are pinned together ------------------
    def test_I4_hard_readout_loses_to_base_rate(self):
        """A hard 0/1 readout must NOT be usable as the primary metric.
        PROOF OF FIRING: the world's exact edge set read as 0/1 is scored and
        must be worse than the base rate; if a future change made the hard
        read competitive, this test fails and the pairing is re-examined."""
        ceil = self._ceiling(0)
        base = self._base_rate()

        def hard(u, v):
            return 1.0 if ceil(u, v) > base(u, v) else 0.0

        h = score(hard, self.ret_ctx, self.ret_obs, self.vocab)
        b = score(base, self.ret_ctx, self.ret_obs, self.vocab)
        self.assertGreater(h["log_loss"], b["log_loss"],
                           "a hard 0/1 readout must lose to the base rate "
                           "under log-loss, or the metric is not pinned")

    # ---- R3: the limbs separate ------------------------------------------
    def test_R3_retention_and_transfer_differ(self):
        """Retention and transfer must be different numbers.  PROOF OF FIRING:
        the two windows are scored under their own laws and the difference is
        asserted non-zero; a single-window design scores them identically and
        fails."""
        c_ret = score(self._ceiling(0), self.ret_ctx, self.ret_obs, self.vocab)
        c_rev = score(self._ceiling(1), self.rev_ctx, self.rev_obs, self.vocab)
        self.assertNotAlmostEqual(c_ret["log_loss"], c_rev["log_loss"],
                                  places=6,
                                  msg="the two limbs must be different numbers")

    def test_R3_windows_are_under_different_laws(self):
        """The retention window must be under the old law and the revision
        window under the new one.  PROOF OF FIRING: the regimes are read off
        the generator's own hidden labels and asserted disjoint; a boundary
        error that put both windows under one law fails this."""
        regimes = self.w["hidden_regimes"]
        ret_r = {regimes[i] for i in self.ret}
        rev_r = {regimes[i] for i in self.rev}
        self.assertEqual(ret_r, {0}, "the retention window must be regime 0 only")
        self.assertEqual(rev_r, {1}, "the revision window must be regime 1 only")

    # ---- the world itself -------------------------------------------------
    def test_world_next_event_is_law_governed(self):
        """Consecutive events are coupled.  PROOF OF FIRING: P(next group =
        same group) is measured and asserted well above the independent-draw
        rate; a world that drew causes independently would score at chance
        and fail."""
        groups = self.w["hidden_groups"]
        regimes = self.w["hidden_regimes"]
        same = tot = 0
        for a, b, r in zip(groups[:-1], groups[1:], regimes[:-1]):
            if r == 0:
                tot += 1
                same += int(a == b)
        self.assertGreater(same / tot, 0.5,
                           "consecutive events must be coupled within a regime")

    def test_world_law_changes_at_the_switch(self):
        """The revision limb needs a law that changed.  PROOF OF FIRING: the
        two regime chains are compared and asserted different; if they were
        identical there would be nothing to revise."""
        self.assertNotEqual(self.d0, self.d1,
                            "the law must differ between regimes")

    def test_closed_form_matches_the_generator(self):
        """The ceiling must be the generator's true conditional.  PROOF OF
        FIRING: the closed form is compared with the empirical frequency in
        every well-populated cell; a formula that drifts from the generator
        fails here.  The tolerance is set for the sample sizes involved."""
        groups = self.w["hidden_groups"]
        events = self.events
        emp = defaultdict(lambda: [0, 0])
        for k in range(len(self.ret) - 1):
            g = groups[self.ret[k]]
            nxt = set(events[self.ret[k + 1]].split())
            for t in self.vocab:
                emp[(g, t)][1] += 1
                if t in nxt:
                    emp[(g, t)][0] += 1
        worst = 0.0
        for (g, t), (h, n) in emp.items():
            if n < 30:
                continue
            e = h / n
            c = self.d0.get(g, {}).get(t, 0.0)
            worst = max(worst, abs(e - c))
        self.assertLess(worst, 0.15,
                        "the closed-form conditional must track the generator")

    def test_vocabulary_is_fixed_by_the_acquisition_phase(self):
        """The vocabulary is fixed before the follow-up, and the probe's
        vocabulary must match.  PROOF OF FIRING: a follow-up-only tag would
        change the vocabulary and fail this."""
        self.assertEqual(len(self.vocab), 16)
        for t in self.vocab:
            self.assertIn(t, {x for f in GROUPS.values() for x in f}
                          | set(NOISE_TAGS))


# ---------------------------------------------------------------------------
# The compositional world — the PRIMARY task
# ---------------------------------------------------------------------------

class CompositionalWorldTests(unittest.TestCase):
    """The primary task.  Every test must FAIL when the thing it guards is
    broken."""

    @classmethod
    def setUpClass(cls):
        cls.w = generate_compositional_world(seed=20261200)
        cls.events = cls.w["events"]

        def idx(phase):
            lo, hi = phase
            return list(range(lo * EPC, hi * EPC))

        cls.acq = idx(COMP_ACQ)
        cls.test = idx(COMP_TRANSFER)
        cls.tune = list(range((COMP_ACQ[1] - 20) * EPC, COMP_ACQ[1] * EPC))
        cls.train_rows = [cls.events[i] for i in cls.acq if cls.w["trainable"][i]]
        cls.vocab = {t for e in cls.train_rows for t in e.split()}

        def win(ii):
            ctx = [sorted(cls.events[ii[k]].split()) for k in range(len(ii) - 1)]
            obs = [sorted(cls.events[ii[k + 1]].split()) for k in range(len(ii) - 1)]
            return ctx, obs

        cls.test_ctx, cls.test_obs = win(cls.test)
        cls.tune_ctx, cls.tune_obs = win(cls.tune)
        # staticmethod: these are plain functions, and a function stored as
        # a class attribute would bind `self` when accessed via the instance.
        cls.ceil = staticmethod(make_ceiling(cls.w, 0))

    # ---- G1: the gap over the strongest baseline -------------------------
    def test_G1_ceiling_beats_strongest_simple_baseline(self):
        """The PRIMARY task's headroom must clear the gate against the
        STRONGEST simple baseline, not the base rate.

        PROOF OF FIRING: the baselines are swept over a declared grid and
        selected on the tuning split, then the gap is asserted above the
        gate.  If the withheld combination stopped creating a gap — e.g.
        the split became empty — this test fails.
        """
        c = score(self.ceil, self.test_ctx, self.test_obs, self.vocab)
        baselines = {"base_rate": fit_base_rate(self.train_rows, self.vocab)}
        _, _, p_big = select_best("bigram", self.train_rows, self.vocab, {},
                                  self.tune_ctx, self.tune_obs)
        baselines["bigram"] = p_big
        _, _, p_cell = select_best("cell", self.train_rows, self.vocab,
                                   self.w["tag_to_cell"],
                                   self.tune_ctx, self.tune_obs)
        baselines["cell_counter"] = p_cell
        best = min(score(v, self.test_ctx, self.test_obs, self.vocab)["log_loss"]
                    for v in baselines.values())
        gap = best - c["log_loss"]
        self.assertGreater(gap, GATE,
                           f"the compositional task must clear the gate "
                           f"against the strongest baseline (gap {gap:.4f})")

    # ---- G2: the positive control -----------------------------------------
    def test_G2_positive_control_reaches_the_ceiling(self):
        """A learner that HOLDS the generating rule must reach the ceiling.
        PROOF OF FIRING: it is scored and compared with the closed form; if
        the rule holder and the closed form ever disagree, the closed form
        is wrong and this fails."""
        pos = make_rule_holder(self.w, 0)
        c = score(self.ceil, self.test_ctx, self.test_obs, self.vocab)
        p = score(pos, self.test_ctx, self.test_obs, self.vocab)
        self.assertAlmostEqual(c["log_loss"], p["log_loss"], places=6,
                                msg="the rule holder must reach the ceiling")

    # ---- G3: the broken-rule control -------------------------------------
    def test_G3_broken_rule_control_is_worse(self):
        """A learner with the WRONG law must be clearly worse.
        PROOF OF FIRING: it is scored and asserted to be worse than the
        ceiling by more than the gate; if the endpoint could not tell a
        wrong law from the right one, it would not be measuring the law."""
        broken = make_broken_rule(self.w, 0)
        c = score(self.ceil, self.test_ctx, self.test_obs, self.vocab)
        b = score(broken, self.test_ctx, self.test_obs, self.vocab)
        self.assertGreater(b["log_loss"] - c["log_loss"], GATE,
                           "the broken-rule control must be clearly worse")

    def test_G3_swapped_law_is_only_weakly_resolved(self):
        """The endpoint resolves the law's STRUCTURE sharply and its exact
        WEIGHTS weakly.  This is a resolution fact, recorded so no result
        over-claims.  PROOF OF FIRING: the swapped-law control is scored and
        asserted to be only slightly worse — if a future change made the
        endpoint resolve weights sharply, this test fails and the
        sensitivity note must be rewritten."""
        swapped = make_swapped_law(self.w, 0)
        c = score(self.ceil, self.test_ctx, self.test_obs, self.vocab)
        s = score(swapped, self.test_ctx, self.test_obs, self.vocab)
        excess = s["log_loss"] - c["log_loss"]
        self.assertGreater(excess, 0.0,
                           "a wrong law must still be worse than the right one")
        self.assertLess(excess, GATE,
                        "the endpoint is expected to resolve weights only "
                        "weakly; if this changed, the note is stale")

    # ---- G4: the withheld combination ------------------------------------
    def test_G4_withheld_combination_is_absent_from_training(self):
        """The withheld combination must genuinely not be in the training
        stream.  PROOF OF FIRING: the generator's own flags are checked
        against the training mask, and the retained consecutive pairs are
        re-derived from the events; a leak fails this."""
        held_tags = set(self.w["held_cell_tags"])
        flip_p_tags = set(self.w["cell_tags"][self.w["held_cell_flip_p"]])
        flagged = [i for i in self.acq if self.w["withheld"][i]]
        self.assertGreater(len(flagged), 0,
                           "the split must not be empty")
        for i in flagged:
            self.assertFalse(self.w["trainable"][i],
                             "a withheld event must be excluded from training")
        retained = [i for i in self.acq if self.w["trainable"][i]]
        for a, b in zip(retained, retained[1:]):
            if b != a + 1:
                continue
            self.assertFalse(
                (set(self.events[a].split()) & held_tags)
                and (set(self.events[b].split()) & flip_p_tags),
                "the held->flip-P transition leaked into the training stream")

    def test_G4_held_cell_still_appears_in_training(self):
        """The world must not be rigged: the held cell's tags are still
        present in the training stream, so the learner can still see them
        and learn which cell they belong to.  PROOF OF FIRING: the count is
        asserted to be non-zero; an empty count means the whole cell was
        removed, which would be a different and much easier task."""
        held_tags = set(self.w["held_cell_tags"])
        n = sum(1 for i in self.acq
                if self.w["trainable"][i]
                and set(self.events[i].split()) & held_tags)
        self.assertGreater(n, 0,
                           "the held cell must still be observed in training")

    # ---- G7: the withheld combination is what creates the gap -------------
    def test_G7_withheld_combination_drives_the_gap(self):
        """The gap must come from the withheld combination, not from generic
        estimation error.

        PROOF OF FIRING: the test split is split by whether the context is
        in the held cell, and the gap on the held cell is asserted to be
        much larger than the gap elsewhere.  If the gap were uniform, the
        benchmark would be measuring estimation rather than generalisation,
        and this fails.
        """
        held_tags = set(self.w["held_cell_tags"])
        h_ctx, h_obs, o_ctx, o_obs = [], [], [], []
        for ctx, obs in zip(self.test_ctx, self.test_obs):
            if set(ctx) & held_tags:
                h_ctx.append(ctx)
                h_obs.append(obs)
            else:
                o_ctx.append(ctx)
                o_obs.append(obs)
        self.assertTrue(h_ctx and o_ctx,
                        "both held and other contexts must be present")
        _, _, p_big = select_best("bigram", self.train_rows, self.vocab, {},
                                  self.tune_ctx, self.tune_obs)
        _, _, p_cell = select_best("cell", self.train_rows, self.vocab,
                                   self.w["tag_to_cell"],
                                   self.tune_ctx, self.tune_obs)
        base = fit_base_rate(self.train_rows, self.vocab)

        def best_gap(ctx, obs):
            c = score(self.ceil, ctx, obs, self.vocab)["log_loss"]
            b = min(score(m, ctx, obs, self.vocab)["log_loss"]
                    for m in (base, p_big, p_cell))
            return b - c

        gap_held = best_gap(h_ctx, h_obs)
        gap_other = best_gap(o_ctx, o_obs)
        self.assertGreater(gap_held, GATE,
                           "the held cell's gap must clear the gate")
        self.assertGreater(gap_held, 2 * gap_other,
                           "the held cell's gap must dominate the gap "
                           "elsewhere, or the benchmark is measuring "
                           "estimation rather than generalisation")

    # ---- the world itself -------------------------------------------------
    def test_G6_held_cell_varies_across_worlds(self):
        """The tag-to-cell mapping is randomised per world, so no fixed tag
        association can solve it.  PROOF OF FIRING: several worlds are
        generated and their held cells are asserted to differ."""
        held = {generate_compositional_world(seed=20261200 + k)["held_cell"]
                for k in range(8)}
        self.assertGreater(len(held), 1,
                           "the held cell must vary across worlds")

    def test_compositional_world_is_law_governed(self):
        """The successor cell must follow the law, not chance.  PROOF OF
        FIRING: the empirical distribution of successor cells is compared
        with the law's; a world that picked successors uniformly would fail.
        """
        cells = self.w["cells"]
        coord = {c: (int(c[1]), int(c[3])) for c in self.w["cell_tags"]}
        flip_p = 0
        flip_q = 0
        other = 0
        for a, b in zip(cells[:-1], cells[1:]):
            pa, qa = coord[a]
            pb, qb = coord[b]
            if pa != pb and qa == qb:
                flip_p += 1
            elif pa == pb and qa != qb:
                flip_q += 1
            else:
                other += 1
        self.assertEqual(other, 0,
                         "the successor must always differ in exactly one factor")
        self.assertGreater(flip_p, 0)
        self.assertGreater(flip_q, 0)


if __name__ == "__main__":
    unittest.main()
