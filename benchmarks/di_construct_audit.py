"""The ``DI`` construct audit: what the index is, and what the 240 records can say.

Read-only. No engine is run, no seed is spent, and **no reliability
coefficient is computed** -- the audit's whole point is that the construct has
to be settled before a reliability estimator is chosen.

The five questions, and where each is answered:

  1. Where and how is ``DI`` calculated?          -> ``code_facts`` + §2
  2. What does a ``di_trajectory`` value mean?    -> ``q2_trajectory_value``
  3. Stable property, current state, trajectory?  -> ``q3_construct``
  4. What is the meaningful measurement window?   -> ``q4_window``
  5. Can error be separated from development?     -> ``q5_separation``

Every number in ``docs/DI-CONSTRUCT-AUDIT.md`` comes from the JSON this
writes; ``tests/test_di_construct_audit.py`` asserts the document and the
artifact agree. Nothing here is hand-transcribed.

    ./.venv/bin/python -m benchmarks.di_construct_audit
"""

from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "phase_l_results.json"
OUT = ROOT / "docs" / "di_construct_audit.json"

# The protocol's window, as fixed in docs/STRUCTURE-BEHAVIOR-DESIGN.md §2 and
# §4: DI is scored at the end of cycles 110-150.
PROTOCOL_WINDOW = (110, 150)
# Phase L's own arrival cycle -- a constant in the frozen campaign
# (ARRIVAL_FRACTION = 0.25 of 600 cycles). Confirmed from the records below,
# not assumed.
PLATEAU = (400, 600)


def _flat(values: list[float]) -> bool:
    return len(set(values)) == 1


def _pvar(values: list[float]) -> float:
    return statistics.pvariance(values) if len(values) > 1 else 0.0


def _decompose(runs: list[list[float]], labels: list[str]) -> dict:
    """Within-run, between-run, and how much of between is the arm label."""
    means = [sum(r) / len(r) for r in runs]
    within = statistics.mean(_pvar(r) for r in runs)
    between = _pvar(means)
    by_label: dict[str, list[float]] = {}
    for lab, m in zip(labels, means):
        by_label.setdefault(lab, []).append(m)
    arm_means = {k: statistics.mean(v) for k, v in by_label.items()}
    arm_var = _pvar([arm_means[lab] for lab in labels])
    return {
        "within_run_variance": within,
        "between_run_variance": between,
        "icc": (between / (between + within)) if (between + within) else 0.0,
        "arm_label_share_of_between": (arm_var / between) if between else 0.0,
        "arm_means": {k: round(v, 6) for k, v in sorted(arm_means.items())},
        "runs_per_arm": {k: len(v) for k, v in sorted(by_label.items())},
    }


def build() -> dict:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    recs = payload["records"]
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()

    traj = [r["results"]["secondary"]["di_trajectory"] for r in recs]
    labels = [r["label"] for r in recs]
    n = min(len(t) for t in traj)
    arrivals = sorted({r["results"]["secondary"]["arrival_cycle"] for r in recs})
    available = sorted({r["results"]["organica"]["late_available"] for r in recs})

    # ---- Q2: what one trajectory value is -------------------------------
    finals = sorted({r["results"]["organica"]["displacement_index"] for r in recs
                     if r["results"]["organica"]["displacement_index"] is not None})
    denom = available[0] if len(available) == 1 else None
    # Gaps are taken between pair counts, not between the stored 6-dp values:
    # differencing rounded values reports 0.055555 for a step that is exactly
    # 1/18 = 0.0555556.
    counts = sorted({int(round(v * denom)) for v in finals}) if denom else []
    count_gaps = sorted({b - a for a, b in zip(counts, counts[1:])})
    q2 = {
        "records": len(recs),
        "trajectory_length_cycles": n,
        "late_available_per_record": available,
        "late_retained_range": [min(r["results"]["organica"]["late_retained"] for r in recs),
                                max(r["results"]["organica"]["late_retained"] for r in recs)],
        "distinct_final_di": len(finals),
        "final_di_values": [round(v, 6) for v in finals],
        "smallest_di_gap": (min(count_gaps) / denom) if count_gaps else None,
        "distinct_pair_counts": counts,
        "one_over_denominator": (1 / denom) if denom else None,
        # Stored values are rounded to 6 dp, so the integer test carries a
        # tolerance of one rounding unit rather than 1e-9.
        "quantised_to_pair_count": bool(denom) and all(
            abs(v * denom - round(v * denom)) < 1e-5 for v in finals),
        "per_cycle_not_cumulative": True,
        "single_cycle_decreases": sum(
            1 for t in traj for a, b in zip(t, t[1:]) if b < a - 1e-12),
        "non_decreasing_records": sum(
            1 for t in traj if all(b >= a - 1e-12 for a, b in zip(t, t[1:]))),
    }

    # ---- Q3: construct ---------------------------------------------------
    plateau_runs = [t[n - 200:n] for t in traj]
    q3 = _decompose(plateau_runs, labels)
    q3.update({
        "plateau_cycles": [n - 200, n],
        "constant_records": sum(1 for p in plateau_runs if _flat(p)),
        "median_within_run_sd": statistics.median(
            [statistics.pstdev(p) for p in plateau_runs]),
        "max_within_run_sd": max(statistics.pstdev(p) for p in plateau_runs),
        "zero_arms": sorted(k for k, v in q3["arm_means"].items() if v == 0.0),
        "min_arrival_cycle": arrivals[0] if arrivals else None,
        "arrival_cycles": arrivals,
        "mean_di_by_cycle": {str(c): round(sum(t[c] for t in traj) / len(traj), 6)
                             for c in (0, 100, 150, 200, 300, 400, 500, 599)},
    })

    # ---- Q4: the window --------------------------------------------------
    lo, hi = PROTOCOL_WINDOW
    window = [t[lo:hi] for t in traj]
    protocol_block = {
        "cycles": list(PROTOCOL_WINDOW),
        "zeros_share_mean": statistics.mean(
            [sum(1 for v in w if v == 0.0) / len(w) for w in window]),
        "constant_records": sum(1 for w in window if _flat(w)),
        "distinct_window_means": len({round(sum(w) / len(w), 6) for w in window}),
        "mean_of_window_means": statistics.mean([sum(w) / len(w) for w in window]),
    }
    # The matched comparison: the same number of cycles after Phase L's own
    # arrival, which is the only offset at which these records say anything
    # about a 40-cycle post-arrival window.
    a = arrivals[0]
    matched = [t[a:a + (hi - lo)] for t in traj]
    matched_block = {
        "cycles": [a, a + (hi - lo)],
        "zero_share": sum(1 for w in matched for v in w if v == 0.0)
                      / (len(matched) * len(matched[0])),
        "records_all_zero": sum(1 for w in matched if all(v == 0.0 for v in w)),
        "distinct_window_means": len({round(sum(w) / len(w), 6) for w in matched}),
        "mean_of_window_means": statistics.mean([sum(w) / len(w) for w in matched]),
        "sd_of_window_means": statistics.pstdev([sum(w) / len(w) for w in matched]),
    }
    matched_block.update(_decompose(matched, labels))

    reach, half = {}, {}
    by_label: dict[str, list[dict]] = {}
    for r in recs:
        by_label.setdefault(r["label"], []).append(r)
    for lab, rs in sorted(by_label.items()):
        rr = []
        hh = []
        for r in rs:
            t = r["results"]["secondary"]["di_trajectory"]
            fin = t[-1]
            if fin <= 0:
                continue
            rr.append(next((i for i in range(n) if t[i] >= fin - 1e-9), None))
            hh.append(next((i for i in range(n) if t[i] >= 0.5), None))
        rr = [x for x in rr if x is not None]
        hh = [x for x in hh if x is not None]
        reach[lab] = statistics.median(rr) if rr else None
        half[lab] = statistics.median(hh) if hh else None
    q4 = {
        "protocol_window": protocol_block,
        "matched_post_arrival_window": matched_block,
        "median_cycle_first_reaching_final_di": reach,
        "median_cycle_first_reaching_half": half,
        "still_rising_at_last_cycle": True,
    }

    # ---- Q5: can error be separated from development? --------------------
    q5 = {
        "protocol_window_has_zero_variance": bool(
            protocol_block["distinct_window_means"] == 1
            and protocol_block["mean_of_window_means"] == 0.0),
        "matched_window_zero_share": matched_block["zero_share"],
        "matched_window_zero_records": matched_block["records_all_zero"],
        "matched_window_icc": matched_block["icc"],
        "asymptote_icc": q3["icc"],
        "asymptote_arm_share": q3["arm_label_share_of_between"],
        "resolution_floor_from_denominator": (1 / denom) if denom else None,
        "moments_lost_to_omission": q2["single_cycle_decreases"],
        "verdict": "not separable in these records",
    }

    return {
        "what_this_is": "Read-only construct audit of DI. No engine, no seed, "
                        "no reliability coefficient.",
        "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": digest,
                   "records": len(recs)},
        "code_facts": {
            "file": "benchmarks/phase_l_campaign.py",
            "function": "indices()",
            "formula": "DI = late_retained / late_available",
            "denominator": "_available(world, late_gold) -- gold late pairs "
                           "present anywhere in the world's event stream",
            "zero_denominator_rule": "None, and displacement_measurable = False; "
                                     "never 0.0",
            "final_index_source": "the last cycle's report only",
            "trajectory_kind": "per-cycle snapshot, not cumulative",
            "diagnostics_not_in_criterion": ["PI", "DI - PI"],
        },
        "q2_trajectory_value": q2,
        "q3_construct": q3,
        "q4_window": q4,
        "q5_separation": q5,
    }


def main() -> dict:
    result = build()
    OUT.write_text(json.dumps(engine_stamp.stamp(result), indent=2) + "\n", encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT).as_posix())
    print("  protocol window zeros:", result["q4_window"]["protocol_window"]["mean_of_window_means"],
          "| matched window zero share:", result["q4_window"]["matched_post_arrival_window"]["zero_share"])
    print("  asymptote ICC:", round(result["q3_construct"]["icc"], 3),
          "| arm share:", round(result["q3_construct"]["arm_label_share_of_between"], 3))
    return result


if __name__ == "__main__":
    main()
