"""The transition construct: what onset, slope and area can measure in this record.

The owner's decision makes a transition summary the primary candidate predictor,
with the settled state retained as a separate, unresolved construct. This module
does the audit that decision requires, and it is deliberately blind to behaviour:
no behavioural endpoint is read here, so no summary can be chosen because it
happens to relate to one. The only quantities computed are the measurement
properties of the three candidate summaries --

  * whether each is defined for every record or censored;
  * how much it varies *within* a generating configuration;
  * how much its ranking survives the run ending early;
  * how much the three overlap with each other.

It also implements the three settling criteria the owner separated, because the
project had been using one statistic for all three:

  (a) entry into a one-pair band around the run's own final value;
  (b) remaining inside that band for a stated number of cycles;
  (c) no meaningful remaining trend over a stated span.

(a) and (b) are retrospective (they use the final value, which is an artefact of
where the run stopped); (c) is the only one that speaks to whether the trajectory
would keep moving, and even it is bounded by the run.

    ./.venv/bin/python -m benchmarks.di_transition_construct
"""

from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "phase_l_results.json"
OUT = ROOT / "docs" / "di_transition_construct.json"

ARRIVAL = 150            # cycles before the late group exists at all
SUSTAINED = 10           # consecutive non-zero readings that count as onset
SUSTAINED_SWEEP = (5, 10, 20)  # the sustention rule is a declared constant: sweep it
MIN_DEFINED_SHARE = 0.9  # Stage B criterion 1: onset defined in >= 90% of a config
MIN_SD_CYCLES = 3.0      # Stage B criterion 2: within-configuration SD floor
MIN_SUPPORT = 30         # cycles needed before a slope is fitted
BAND_PAIRS = 1           # the one-pair tolerance band
PERSIST = (30, 50, 100)  # band durations reported
TREND_SPAN = 100         # cycles over which "remaining trend" is measured
TRUNCATE_AT = 450        # a shorter run, to test rank stability of each measure

# The behavioural clock. The predictor is available at the confirmation cycle, so the
# earliest legal behavioural cycle is the one after it: a margin of one cycle, not a
# taste parameter. The follow-up is the protocol's own 50 + 50, fixed here so that every
# world receives the same amount of behavioural opportunity after emergence.
POST_CONFIRMATION_MARGIN = 1
LEARN_CYCLES = 50
TEST_CYCLES = 50
FOLLOW_UP_CYCLES = LEARN_CYCLES + TEST_CYCLES


def _pvar(values: list[float]) -> float:
    return statistics.pvariance(values) if len(values) > 1 else 0.0


def _pstd(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def _rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _spearman(x: list, y: list) -> float | None:
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3:
        return None
    xs = _rank([p[0] for p in pairs])
    ys = _rank([p[1] for p in pairs])
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
    return num / den if den else None


def _ols_slope(values: list[float], start: int, end: int) -> float:
    k = end - start
    mx = (start + end - 1) / 2.0
    my = sum(values[start:end]) / k
    num = sum((x - mx) * (values[x] - my) for x in range(start, end))
    den = sum((x - mx) ** 2 for x in range(start, end))
    return num / den if den else 0.0


def _positive(v) -> bool:
    """A reading qualifies only if it is present and non-zero.

    A missing reading is not a non-zero reading: it breaks the run. This is the
    convention the artifact reports under ``conventions``, implemented here so
    that the stated rule and the executed rule are the same rule.
    """
    return v is not None and v > 0


def _onset(t: list, sustained: int = SUSTAINED) -> int | None:
    n = len(t)
    return next((k for k in range(n - sustained)
                 if all(_positive(t[k + m]) for m in range(sustained))), None)


def _onset_detail(t: list) -> dict:
    """The onset convention applied to one trajectory: anchor, confirmation, censoring.

    The event is the **first cycle of the qualifying run**, not the first non-zero
    reading, and it is confirmed only once the tenth consecutive reading has been
    recorded. A run interrupted before it qualifies does not count and does not
    move the anchor -- the search resumes at the cycle after the zero -- so an
    isolated blip can never be back-dated into an onset.
    """
    n = len(t)
    first_nonzero = next((k for k in range(n) if _positive(t[k])), None)
    anchor = _onset(t)
    interrupted = 0
    if first_nonzero is not None:
        limit = anchor if anchor is not None else n
        k = first_nonzero
        while k < limit:
            j = k
            while j < limit and _positive(t[j]):
                j += 1
            if j - k < SUSTAINED:
                interrupted += 1
            k = j + 1
    trailing = 0
    k = n - 1
    while k >= 0 and _positive(t[k]):
        trailing += 1
        k -= 1
    if anchor is not None:
        reason = None
    elif first_nonzero is None:
        reason = "no_nonzero_reading"
    elif trailing:
        reason = "end_of_record"
    else:
        reason = "interrupted"
    return {
        "anchor": anchor,
        "confirmation_cycle": None if anchor is None else anchor + SUSTAINED - 1,
        "first_nonzero_cycle": first_nonzero,
        "interrupted_attempts": interrupted,
        "trailing_nonzero": trailing,
        "censored_because": reason,
        "missing_readings": sum(1 for v in t if v is None),
    }


def _slope(t: list[float], denom: int) -> float | None:
    """Pairs per 100 cycles over the run's own support, or None if it never onsets."""
    onset = _onset(t)
    if onset is None or len(t) - onset < MIN_SUPPORT:
        return None
    return _ols_slope(t, onset, len(t)) * denom * 100


def _exposure(t: list[float], end: int, denom: int) -> float:
    """Mean DI over [arrival, end], in pairs: the accumulated stock, standardised."""
    return sum(t[ARRIVAL:end]) / (end - ARRIVAL) * denom


def _measures(t: list[float], denom: int, end: int | None = None) -> dict:
    pair = 1 / denom
    end = len(t) if end is None else end
    series = t[:end]
    onset = _onset(series)
    slope = None
    if onset is not None and len(series) - onset >= MIN_SUPPORT:
        slope = _ols_slope(series, onset, len(series)) * denom * 100
    return {
        "onset": onset,
        "slope_pairs_per_100_cycles": slope,
        "exposure_pairs": _exposure(series, end, denom),
        "area_pair_cycles": sum(series[ARRIVAL:end]) * denom,
        "settled_reading_pairs": series[-1] * denom,
    }


def _agg(values: list, round_to: int = 6) -> dict:
    vals = [v for v in values if v is not None]
    if not vals:
        return {"n": 0, "median": None, "min": None, "max": None, "sd": None,
                "distinct": 0}
    return {
        "n": len(vals),
        "median": round(statistics.median(vals), round_to),
        "min": round(min(vals), round_to),
        "max": round(max(vals), round_to),
        "sd": round(_pstd(vals), round_to),
        "distinct": len({round(v, 9) for v in vals}),
    }


def _onset_distribution(values: list, tol: float = MIN_SD_CYCLES) -> dict:
    """SD *and* the distribution behind it, so a few unusual worlds cannot hide a clump."""
    vals = sorted(v for v in values if v is not None)
    if len(vals) < 2:
        return {"n": len(vals), "median": None, "sd": None, "min": None, "max": None,
                "p25": None, "p75": None, "iqr": None, "distinct": len(set(vals)),
                "share_within_sd_threshold_of_median": None}
    q = statistics.quantiles(vals, n=4, method="inclusive")
    med = statistics.median(vals)
    return {
        "n": len(vals),
        "median": round(med, 6),
        "sd": round(_pstd(vals), 6),
        "min": min(vals),
        "max": max(vals),
        "p25": round(q[0], 6),
        "p75": round(q[2], 6),
        "iqr": round(q[2] - q[0], 6),
        "distinct": len(set(vals)),
        "share_within_sd_threshold_of_median": round(
            sum(1 for v in vals if abs(v - med) <= tol) / len(vals), 6),
    }


def build() -> dict:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    recs = payload["records"]
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    denom = sorted({r["results"]["organica"]["late_available"] for r in recs})[0]
    pair = 1 / denom

    rows = []
    trajs: list[list] = []
    for r in recs:
        t = r["results"]["secondary"]["di_trajectory"]
        trajs.append(t)
        full = _measures(t, denom)
        short = _measures(t, denom, end=TRUNCATE_AT)
        onset = full["onset"]
        entry = 0
        if onset is not None:
            idx = [k for k in range(len(t)) if abs(t[k] - t[-1]) >= pair - 1e-12]
            entry = 1 + max(idx) if idx else 0
        rows.append({
            "config": r["label"],
            "moves_at_all": any(v > 0 for v in t),
            "full": full,
            "at_450": short,
            "band_entry_cycle": entry,
            "band_persistence_cycles": len(t) - entry if onset is not None else None,
            "remaining_trend_pairs_last_100": (
                (t[-1] - t[-1 - TREND_SPAN]) * denom if onset is not None else None),
            "onset_detail": _onset_detail(t),
        })

    movers = [x for x in rows if x["full"]["onset"] is not None]
    configs = sorted({x["config"] for x in rows})

    # ---- per-configuration measurement properties -------------------------
    per_config: dict[str, dict] = {}
    for lab in configs:
        rs = [x for x in rows if x["config"] == lab]
        per_config[lab] = {
            "records": len(rs),
            "onset_cycles": _agg([x["full"]["onset"] for x in rs]),
            "slope_pairs_per_100_cycles": _agg(
                [x["full"]["slope_pairs_per_100_cycles"] for x in rs]),
            "exposure_pairs": _agg([x["full"]["exposure_pairs"] for x in rs]),
            "area_pair_cycles": _agg([x["full"]["area_pair_cycles"] for x in rs]),
            "censored_onset": sum(1 for x in rs if x["full"]["onset"] is None),
        }

    # ---- the onset convention, applied ------------------------------------
    details = [x["onset_detail"] for x in rows]
    onset_distribution = {lab: _onset_distribution(
        [x["full"]["onset"] for x in rows if x["config"] == lab]) for lab in configs}

    conventions = {
        "sustained_cycles": SUSTAINED,
        "anchor": "first cycle of the qualifying run, never the first non-zero reading",
        "confirmation": "the anchor is confirmed only once the %dth consecutive "
                        "reading has been recorded" % SUSTAINED,
        "available_from": "the confirmation cycle (anchor + %d) onward; the "
                          "predictor does not exist before then" % (SUSTAINED - 1),
        "assigned_retrospectively": True,
        "interruption_before_confirmation": "a run shorter than %d ended by a zero "
                                            "does not qualify, does not move the "
                                            "anchor, and the search resumes at the "
                                            "cycle after the zero" % SUSTAINED,
        "interruption_after_confirmation": "does not move a confirmed onset; the "
                                           "event is the first sustained emergence",
        "missing_reading": "counts as not qualifying, so it breaks the run; a "
                           "missing reading is never read as non-zero",
        "end_boundary": "a run still non-zero where the record ends, with fewer "
                        "than %d readings since its last zero, is censored -- "
                        "never an onset at the boundary" % SUSTAINED,
    }
    convention_counts = {
        "records": len(rows),
        "trajectory_lengths": sorted({len(t) for t in trajs}),
        "records_with_missing_readings": sum(1 for d in details if d["missing_readings"]),
        "records_with_no_nonzero_reading": sum(
            1 for d in details if d["first_nonzero_cycle"] is None),
        "records_where_anchor_is_first_nonzero": sum(
            1 for d in details if d["anchor"] is not None
            and d["anchor"] == d["first_nonzero_cycle"]),
        "records_where_anchor_follows_first_nonzero": sum(
            1 for d in details if d["anchor"] is not None
            and d["first_nonzero_cycle"] is not None
            and d["first_nonzero_cycle"] < d["anchor"]),
        "max_anchor_lag_cycles": max(
            (d["anchor"] - d["first_nonzero_cycle"] for d in details
             if d["anchor"] is not None and d["first_nonzero_cycle"] is not None),
            default=None),
        "interrupted_attempts_total": sum(d["interrupted_attempts"] for d in details),
        "records_with_an_interrupted_attempt": sum(
            1 for d in details if d["interrupted_attempts"]),
        "censored_end_of_record": sum(
            1 for d in details if d["censored_because"] == "end_of_record"),
        "censored_interrupted": sum(
            1 for d in details if d["censored_because"] == "interrupted"),
        "censored_no_nonzero_reading": sum(
            1 for d in details if d["censored_because"] == "no_nonzero_reading"),
        "latest_confirmation_cycle": max(
            (d["confirmation_cycle"] for d in details
             if d["confirmation_cycle"] is not None), default=None),
    }

    # ---- the sustention rule is a constant, so sweep it -------------------
    base_onsets = [_onset(t) for t in trajs]
    sustention: dict[str, dict] = {}
    for k in SUSTAINED_SWEEP:
        got = [_onset(t, k) for t in trajs]
        vals = [v for v in got if v is not None]
        diffs = [g - b for g, b in zip(got, base_onsets)
                 if g is not None and b is not None]
        sustention[str(k)] = {
            "defined": len(vals),
            "median": round(statistics.median(vals), 6) if vals else None,
            "sd": round(_pstd(vals), 6) if vals else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "median_shift_cycles_vs_10": (round(statistics.median(diffs), 6)
                                         if diffs else None),
            "max_abs_shift_cycles_vs_10": max((abs(d) for d in diffs), default=None),
            "records_whose_onset_moves": sum(1 for d in diffs if d != 0),
        }

    # ---- the sweep at the level of the predictor, not of the median -------
    # A sweep that leaves the median in place has said nothing about whether an
    # individual world keeps its rank, so the ordering is measured too: Spearman
    # across the records defined under both rules, the pairwise inversions among
    # them, the records whose eligibility appears or disappears, and whether the
    # two measurement criteria reach a different verdict under a different rule.
    threshold_ranks: dict[str, dict] = {}
    for lab in configs:
        idx = [i for i, x in enumerate(rows) if x["config"] == lab]
        per_k = {k: [_onset(trajs[i], k) for i in idx] for k in SUSTAINED_SWEEP}
        comparisons: dict[str, dict] = {}
        for a, b in ((5, 10), (10, 20), (5, 20)):
            va, vb = per_k[a], per_k[b]
            both = [(x, y) for x, y in zip(va, vb)
                    if x is not None and y is not None]
            inv = 0
            for i in range(len(both)):
                for j in range(i + 1, len(both)):
                    if (both[i][0] - both[j][0]) * (both[i][1] - both[j][1]) < 0:
                        inv += 1
            comparable = len(both) * (len(both) - 1) // 2
            ra = _rank([x for x, _ in both])
            rb = _rank([y for _, y in both])
            comparisons["%d_vs_%d" % (a, b)] = {
                "spearman": _spearman(va, vb),
                "records_defined_under_both": len(both),
                "records_defined_under_the_shorter_rule_only": sum(
                    1 for x, y in zip(va, vb) if x is not None and y is None),
                "records_defined_under_the_longer_rule_only": sum(
                    1 for x, y in zip(va, vb) if x is None and y is not None),
                "records_whose_eligibility_changes": sum(
                    1 for x, y in zip(va, vb) if (x is None) != (y is None)),
                "comparable_pairs": comparable,
                "pairwise_rank_inversions": inv,
                "inversion_share_of_comparable_pairs": (
                    round(inv / comparable, 6) if comparable else None),
                "max_rank_shift": (round(max(abs(x - y) for x, y in zip(ra, rb)), 6)
                                   if ra else None),
            }
        conclusions: dict[str, dict] = {}
        for k in SUSTAINED_SWEEP:
            vals = [v for v in per_k[k] if v is not None]
            share = len(vals) / len(idx) if idx else 0.0
            dist = _onset_distribution(vals)
            conclusions[str(k)] = {
                "defined_share": round(share, 6),
                "defined_share_pass": share >= MIN_DEFINED_SHARE,
                "median": dist["median"],
                "sd_cycles": dist["sd"],
                "sd_pass": (dist["sd"] or 0.0) >= MIN_SD_CYCLES,
            }
            conclusions[str(k)]["pass"] = bool(
                conclusions[str(k)]["defined_share_pass"]
                and conclusions[str(k)]["sd_pass"])
        threshold_ranks[lab] = {
            "records": len(idx),
            "comparisons": comparisons,
            "criteria_under_each_rule": conclusions,
            "conclusions_change": len({c["pass"] for c in conclusions.values()}) > 1,
        }

    threshold_sensitivity = {
        "rules_swept": list(SUSTAINED_SWEEP),
        "declared_rule": SUSTAINED,
        "per_config": threshold_ranks,
        "records_whose_eligibility_changes_by_rule": {
            "%d_vs_%d" % (a, b): sum(
                1 for t in trajs
                if (_onset(t, a) is None) != (_onset(t, b) is None))
            for a, b in ((5, 10), (10, 20), (5, 20))},
        "configurations_whose_conclusions_change": sorted(
            lab for lab, r in threshold_ranks.items() if r["conclusions_change"]),
        "note": "This does not reopen the ten-cycle decision. It measures whether the "
                "ordering of individual worlds, and the eligibility of individual "
                "runs, survive a different sustention rule; the rule stays frozen for "
                "Stage B either way.",
    }

    # ---- the behavioural clock -------------------------------------------
    # The predictor is available at the confirmation cycle, so the behavioural limb
    # opens the cycle after it, runs a fixed number of cycles, and never overlaps the
    # onset window. Absolute cycles differ across worlds; post-confirmation elapsed
    # time does not, and both are reported for every behavioural observation.
    clock: dict[str, dict] = {}
    for lab in configs:
        rs = [x for x in rows if x["config"] == lab]
        confs = sorted(x["onset_detail"]["confirmation_cycle"] for x in rs
                       if x["onset_detail"]["confirmation_cycle"] is not None)
        if not confs:
            continue
        starts = [c + POST_CONFIRMATION_MARGIN for c in confs]
        # The last behavioural cycle is an *index*; a run holds indices 0..L-1, so the
        # length needed is one larger than the last index. Keeping the two apart is the
        # whole point of this block.
        last = max(starts) + FOLLOW_UP_CYCLES - 1
        clock[lab] = {
            "runs_with_a_clock": len(confs),
            "confirmation_cycle_min": min(confs),
            "confirmation_cycle_median": statistics.median(confs),
            "confirmation_cycle_max": max(confs),
            "first_behavioural_cycle_min": min(starts),
            "first_behavioural_cycle_median": statistics.median(starts),
            "first_behavioural_cycle_max": max(starts),
            "last_behavioural_cycle_index_max": last,
            "run_length_needed_cycles": last + 1,
            "runs_that_fit_a_600_cycle_run": sum(
                1 for s in starts if s + FOLLOW_UP_CYCLES - 1 <= 599),
        }
    all_confs = [x["onset_detail"]["confirmation_cycle"] for x in rows
                 if x["onset_detail"]["confirmation_cycle"] is not None]
    all_starts = [c + POST_CONFIRMATION_MARGIN for c in all_confs]

    # The arithmetic that was previously only implied: the span is inclusive, the length
    # is the last index plus one, and the horizon is NOT the duration.
    assert ((POST_CONFIRMATION_MARGIN + FOLLOW_UP_CYCLES - 1)
            - POST_CONFIRMATION_MARGIN + 1) == FOLLOW_UP_CYCLES
    assert FOLLOW_UP_CYCLES + POST_CONFIRMATION_MARGIN != FOLLOW_UP_CYCLES
    behavioural_clock = {
        "post_confirmation_margin_cycles": POST_CONFIRMATION_MARGIN,
        "learn_cycles": LEARN_CYCLES,
        "test_cycles": TEST_CYCLES,
        "follow_up_cycles": FOLLOW_UP_CYCLES,
        "first_behavioural_cycle": "confirmation_cycle + %d" % POST_CONFIRMATION_MARGIN,
        "last_behavioural_cycle": "confirmation_cycle + %d"
                                  % (POST_CONFIRMATION_MARGIN + FOLLOW_UP_CYCLES - 1),
        "follow_up_length_is_identical_in_every_world": True,
        "first_behavioural_cycle_differs_by_world": True,
        "estimand": "behaviour over a fixed window after structural emergence: the "
                    "amount of behavioural opportunity is equalised, the developmental "
                    "age at which it opens is a property of the world and is reported "
                    "rather than equalised",
        "cycle_indexing": "counter values are zero-based indices into the stored "
                          "trajectory: a run of 600 readings holds indices 0-599, so the "
                          "confirmation index 598 quoted in section 3.1 is the 599th "
                          "reading. Every offset added to an index is an index too.",
        "behavioural_cycle_count": FOLLOW_UP_CYCLES,
        "inclusive_span_cycles": (POST_CONFIRMATION_MARGIN + FOLLOW_UP_CYCLES - 1)
                                 - POST_CONFIRMATION_MARGIN + 1,
        "last_behavioural_cycle_index_offset": (POST_CONFIRMATION_MARGIN
                                                + FOLLOW_UP_CYCLES - 1),
        "run_length_offset_from_confirmation_index": (POST_CONFIRMATION_MARGIN
                                                     + FOLLOW_UP_CYCLES),
        "run_length_is_one_more_than_the_last_index": (
            "the follow-up is %d behavioural cycles, from index c+%d through c+%d "
            "inclusive. The run must contain index c+%d, and a run of length L holds "
            "indices 0..L-1, so its length is c+%d. The two numbers are the same span "
            "counted from zero and from one, not a disagreement about duration"
            % (FOLLOW_UP_CYCLES, POST_CONFIRMATION_MARGIN,
               POST_CONFIRMATION_MARGIN + FOLLOW_UP_CYCLES - 1,
               POST_CONFIRMATION_MARGIN + FOLLOW_UP_CYCLES - 1,
               POST_CONFIRMATION_MARGIN + FOLLOW_UP_CYCLES)),
        "runs_with_a_clock": len(all_starts),
        "absolute_start_min": min(all_starts) if all_starts else None,
        "absolute_start_max": max(all_starts) if all_starts else None,
        "absolute_start_span_cycles": (max(all_starts) - min(all_starts))
                                      if all_starts else None,
        "last_behavioural_index_max": (max(all_starts) + FOLLOW_UP_CYCLES - 1)
                                      if all_starts else None,
        "run_length_needed_cycles": (max(all_starts) + FOLLOW_UP_CYCLES)
                                    if all_starts else None,
        "runs_that_fit_a_600_cycle_run": sum(
            1 for s in all_starts if s + FOLLOW_UP_CYCLES - 1 <= 599),
        "behavioural_cycles_at_or_before_confirmation": sum(
            1 for s, c in zip(all_starts, all_confs) if s <= c),
        "onset_window_ends": "the confirmation cycle -- the last reading the onset rule "
                             "itself reads",
        "exposure_interval_must_end_before_first_behavioural_cycle": True,
        "reporting_required_per_observation": ["absolute cycle",
                                                "cycles since confirmation"],
        "per_config": clock,
    }

    # ---- eligibility is a measurement fact; scope is the claim -----------
    eligibility: dict[str, dict] = {}
    for lab in configs:
        rs = [x for x in rows if x["config"] == lab]
        defined = per_config[lab]["onset_cycles"]["n"]
        share = defined / len(rs)
        ok = share >= MIN_DEFINED_SHARE
        eligibility[lab] = {
            "records": len(rs),
            "runs_that_ever_move": sum(1 for x in rs if x["moves_at_all"]),
            "runs_with_sustained_onset": defined,
            "defined_share": round(share, 6),
            "class": ("configurations with sustained structural emergence" if ok
                      else "configurations without sustained structural emergence"),
            "eligible": ok,
            "excluded_from_construct": not ok,
            "reason_if_excluded": None if ok else (
                "no run sustains %d consecutive non-zero readings: the manipulated "
                "quantity produces no sustained DI in this world (AGENTS 13a), which "
                "is a property of the world, not a null about the organism" % SUSTAINED),
        }

    accounting = {
        "records_total": sum(e["records"] for e in eligibility.values()),
        "records_in_eligible_configurations": sum(
            e["records"] for e in eligibility.values() if e["eligible"]),
        "records_in_ineligible_configurations": sum(
            e["records"] for e in eligibility.values() if not e["eligible"]),
        "records_dropped": 0,
        "records_with_onset": sum(e["runs_with_sustained_onset"]
                                  for e in eligibility.values()),
        "note": "Every stored record is counted; none is dropped. The 1:x "
                "configurations stay in the accounting and are excluded from the "
                "construct's claim, not from the study.",
    }

    # ---- Stage B's two measurement criteria, evaluated per configuration --
    stage_b_criteria: dict[str, dict] = {}
    for lab in configs:
        if not eligibility[lab]["eligible"]:
            continue
        dist = onset_distribution[lab]
        stage_b_criteria[lab] = {
            "defined_share": eligibility[lab]["defined_share"],
            "defined_share_threshold": MIN_DEFINED_SHARE,
            "defined_share_pass": eligibility[lab]["defined_share"] >= MIN_DEFINED_SHARE,
            "sd_cycles": dist["sd"],
            "sd_threshold_cycles": MIN_SD_CYCLES,
            "sd_pass": (dist["sd"] or 0.0) >= MIN_SD_CYCLES,
            "iqr_cycles": dist["iqr"],
            "range_cycles": [dist["min"], dist["max"]],
        }
        stage_b_criteria[lab]["pass"] = bool(
            stage_b_criteria[lab]["defined_share_pass"]
            and stage_b_criteria[lab]["sd_pass"])
    criteria_block = {
        "evaluated_per_configuration": True,
        "min_defined_share": MIN_DEFINED_SHARE,
        "min_sd_cycles": MIN_SD_CYCLES,
        "per_config": stage_b_criteria,
        "all_pass": bool(stage_b_criteria)
        and all(c["pass"] for c in stage_b_criteria.values()),
    }

    # ---- within- vs between-configuration variance, per measure -----------
    def _share(key: str) -> float:
        vals = [x["full"][key] for x in rows if x["full"][key] is not None]
        groups = [[x["full"][key] for x in rows
                   if x["config"] == lab and x["full"][key] is not None]
                  for lab in configs]
        groups = [g for g in groups if g]
        between = _pvar(vals)
        within = statistics.mean(_pvar(g) for g in groups) if groups else 0.0
        return round(within / between, 6) if between else 0.0

    variance_share = {
        "onset": _share("onset"),
        "slope_pairs_per_100_cycles": _share("slope_pairs_per_100_cycles"),
        "exposure_pairs": _share("exposure_pairs"),
        "settled_reading_pairs": _share("settled_reading_pairs"),
    }

    # ---- overlap among the three candidates ------------------------------
    overlap = {
        "onset_vs_exposure_pairs_movers": _spearman(
            [x["full"]["onset"] for x in movers],
            [x["full"]["exposure_pairs"] for x in movers]),
        "onset_vs_slope_movers": _spearman(
            [x["full"]["onset"] for x in movers],
            [x["full"]["slope_pairs_per_100_cycles"] for x in movers]),
        "slope_vs_exposure_movers": _spearman(
            [x["full"]["slope_pairs_per_100_cycles"] for x in movers],
            [x["full"]["exposure_pairs"] for x in movers]),
    }

    # ---- sensitivity to the run ending early ------------------------------
    truncation = {
        "onset_defined_at_450": sum(1 for x in rows if x["at_450"]["onset"] is not None),
        "onset_defined_full": sum(1 for x in rows if x["full"]["onset"] is not None),
        "slope_defined_at_450": sum(
            1 for x in rows if x["at_450"]["slope_pairs_per_100_cycles"] is not None),
        "exposure_rank_stability_450": _spearman(
            [x["full"]["exposure_pairs"] for x in rows],
            [x["at_450"]["exposure_pairs"] for x in rows]),
        "slope_rank_stability_450": _spearman(
            [x["full"]["slope_pairs_per_100_cycles"] for x in rows],
            [x["at_450"]["slope_pairs_per_100_cycles"] for x in rows]),
        "onset_rank_stability_450": _spearman(
            [x["full"]["onset"] for x in rows],
            [x["at_450"]["onset"] for x in rows]),
    }

    # ---- the three settling criteria, separated ---------------------------
    def _count(pred) -> int:
        return sum(1 for x in movers if pred(x))

    settling = {
        "population": len(movers),
        "entry_band_pairs": BAND_PAIRS,
        "entry_median_cycle": statistics.median([x["band_entry_cycle"] for x in movers]),
        "entry_max_cycle": max(x["band_entry_cycle"] for x in movers),
        "persistence_median_cycles": statistics.median(
            [x["band_persistence_cycles"] for x in movers]),
        "persistence_at_least": {
            str(k): _count(lambda x, k=k: x["band_persistence_cycles"] >= k)
            for k in PERSIST},
        "remaining_trend_pairs_last_100": {
            "median": round(statistics.median(
                [x["remaining_trend_pairs_last_100"] for x in movers]), 6),
            "min": round(min(x["remaining_trend_pairs_last_100"] for x in movers), 6),
            "max": round(max(x["remaining_trend_pairs_last_100"] for x in movers), 6),
            "zero_trend": _count(
                lambda x: abs(x["remaining_trend_pairs_last_100"]) < pair / 2),
            "at_least_one_pair": _count(
                lambda x: abs(x["remaining_trend_pairs_last_100"]) >= pair - 1e-12),
            "at_least_two_pairs": _count(
                lambda x: abs(x["remaining_trend_pairs_last_100"]) >= 2 * pair - 1e-12),
        },
        "satisfy_persistence_50_and_zero_trend": _count(
            lambda x: x["band_persistence_cycles"] >= 50
            and abs(x["remaining_trend_pairs_last_100"]) < pair / 2),
    }

    # ---- what each candidate would need to be usable ----------------------
    candidates = {
        "onset": {
            "defined_for_every_record": truncation["onset_defined_full"] == len(rows),
            "censored_records": len(rows) - truncation["onset_defined_full"],
            "unit": "cycles",
            "within_config_sd_native": per_config["6:1"]["onset_cycles"]["sd"],
            "rank_stability_under_truncation": truncation["onset_rank_stability_450"],
        },
        "slope": {
            "defined_for_every_record": truncation["slope_defined_at_450"] == len(rows),
            "censored_records": len(rows) - truncation["slope_defined_at_450"],
            "unit": "pairs per 100 cycles",
            "within_config_sd_native": per_config["6:1"]["slope_pairs_per_100_cycles"]["sd"],
            "rank_stability_under_truncation": truncation["slope_rank_stability_450"],
        },
        "exposure": {
            "defined_for_every_record": True,
            "censored_records": 0,
            "unit": "pairs",
            "within_config_sd_native": per_config["6:1"]["exposure_pairs"]["sd"],
            "rank_stability_under_truncation": truncation["exposure_rank_stability_450"],
        },
    }

    return {
        "what_this_is": "Audit of the transition construct: measurement properties "
                        "of onset, slope and accumulated exposure over the 240 stored "
                        "Phase L records. No behavioural endpoint is read; no engine, "
                        "no seed, no coefficient, no confirmatory run.",
        "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": digest,
                   "records": len(recs)},
        "units": {"late_pairs_per_record": denom, "one_pair": pair,
                  "arrival_cycle": ARRIVAL, "sustained_cycles": SUSTAINED,
                  "min_support_cycles": MIN_SUPPORT, "truncate_at": TRUNCATE_AT},
        "definitions": {
            "onset": "first cycle from which %d consecutive readings are non-zero"
                     % SUSTAINED,
            "slope": "least-squares slope in pairs per 100 cycles, fitted over "
                     "[onset, end), undefined without an onset",
            "exposure": "mean DI over [%d, end) expressed in pairs -- the "
                        "accumulated stock, standardised by the interval length"
                        % ARRIVAL,
            "band_entry": "cycle from which the run never again differs from its "
                          "own final value by a whole pair (retrospective: uses "
                          "the final value, which is where the run stopped)",
            "band_persistence": "cycles from band_entry to the end of the run",
            "remaining_trend": "value at the last cycle minus the value %d cycles "
                               "earlier, in pairs" % TREND_SPAN,
        },
        "per_config": per_config,
        "variance_share_within_config": variance_share,
        "overlap": overlap,
        "truncation": truncation,
        "settling_criteria": settling,
        "onset_conventions": conventions,
        "onset_convention_counts": convention_counts,
        "onset_distribution": onset_distribution,
        "sustention_sensitivity": sustention,
        "threshold_rank_sensitivity": threshold_sensitivity,
        "eligibility": eligibility,
        "accounting": accounting,
        "stage_b_measurement_criteria": criteria_block,
        "behavioural_clock": behavioural_clock,
        "candidates": candidates,
        "no_behaviour_read": "No correlation between any summary and Phase L's "
                             "behavioural endpoint was computed, by design: the "
                             "construct must be chosen on measurement grounds "
                             "before any outcome is examined.",
        "exploratory": True,
    }


def main() -> dict:
    result = build()
    OUT.write_text(json.dumps(engine_stamp.stamp(result), indent=2) + "\n", encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
    print("\nper configuration (native units)")
    for lab, row in result["per_config"].items():
        print("  %-4s onset %-28s exposure %-28s censored %2d"
              % (lab,
                 "%s +/- %s" % (row["onset_cycles"]["median"], row["onset_cycles"]["sd"]),
                 "%s +/- %s" % (row["exposure_pairs"]["median"],
                                row["exposure_pairs"]["sd"]),
                 row["censored_onset"]))
    print("\nwithin-config share of variance:",
          result["variance_share_within_config"])
    print("overlap:", {k: (round(v, 3) if v is not None else None)
                       for k, v in result["overlap"].items()})
    print("truncation:", {k: (round(v, 3) if isinstance(v, float) else v)
                          for k, v in result["truncation"].items()})
    print("settling:", json.dumps(result["settling_criteria"], indent=2))
    print("\nonset conventions:", json.dumps(result["onset_convention_counts"], indent=2))
    print("\nsustention:", json.dumps(result["sustention_sensitivity"], indent=2))
    print("\nthreshold rank sensitivity:",
          json.dumps(result["threshold_rank_sensitivity"], indent=2))
    print("\nbehavioural clock:", json.dumps(result["behavioural_clock"], indent=2))
    print("\nonset distribution:", json.dumps(result["onset_distribution"], indent=2))
    print("\neligibility:", json.dumps(result["eligibility"], indent=2))
    print("\naccounting:", json.dumps(result["accounting"], indent=2))
    print("\nstage B measurement criteria:",
          json.dumps(result["stage_b_measurement_criteria"], indent=2))
    for name, c in result["candidates"].items():
        print("  %-8s defined-for-all=%-5s censored=%-3d within-SD=%s stability=%s"
              % (name, c["defined_for_every_record"], c["censored_records"],
                 c["within_config_sd_native"],
                 None if c["rank_stability_under_truncation"] is None
                 else round(c["rank_stability_under_truncation"], 3)))
    return result


if __name__ == "__main__":
    main()
