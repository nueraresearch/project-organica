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

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "phase_l_results.json"
OUT = ROOT / "docs" / "di_transition_construct.json"

ARRIVAL = 150            # cycles before the late group exists at all
SUSTAINED = 10           # consecutive non-zero readings that count as onset
MIN_SUPPORT = 30         # cycles needed before a slope is fitted
BAND_PAIRS = 1           # the one-pair tolerance band
PERSIST = (30, 50, 100)  # band durations reported
TREND_SPAN = 100         # cycles over which "remaining trend" is measured
TRUNCATE_AT = 450        # a shorter run, to test rank stability of each measure


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


def _onset(t: list[float]) -> int | None:
    n = len(t)
    return next((k for k in range(n - SUSTAINED)
                 if all(t[k + m] > 0 for m in range(SUSTAINED))), None)


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


def build() -> dict:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    recs = payload["records"]
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    denom = sorted({r["results"]["organica"]["late_available"] for r in recs})[0]
    pair = 1 / denom

    rows = []
    for r in recs:
        t = r["results"]["secondary"]["di_trajectory"]
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
        "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": digest,
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
        "candidates": candidates,
        "no_behaviour_read": "No correlation between any summary and Phase L's "
                             "behavioural endpoint was computed, by design: the "
                             "construct must be chosen on measurement grounds "
                             "before any outcome is examined.",
        "exploratory": True,
    }


def main() -> dict:
    result = build()
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
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
    for name, c in result["candidates"].items():
        print("  %-8s defined-for-all=%-5s censored=%-3d within-SD=%s stability=%s"
              % (name, c["defined_for_every_record"], c["censored_records"],
                 c["within_config_sd_native"],
                 None if c["rank_stability_under_truncation"] is None
                 else round(c["rank_stability_under_truncation"], 3)))
    return result


if __name__ == "__main__":
    main()
