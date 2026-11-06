"""Stage A of the DI measurement-window design: what the 240 records support.

Exploratory by construction. The records are the ones that revealed the
protocol's window to be temporally misplaced, so anything selected here is
selected on data that has already been used for a decision, and must be
validated out of sample (Stage B) before it is trusted.

Computes, per configuration:

  * when ``DI`` first becomes non-zero, and when that becomes sustained;
  * whether a configuration ever expresses ``DI`` at all;
  * when the run settles (last cycle differing from its own final value by a
    whole pair), so a window can be placed after it;
  * the within-configuration predictor variance a window would actually offer
    -- the quantity a within-configuration correlation depends on, and the one
    that the ICC of 0.890 does not describe;
  * the resolution available in pairs at each candidate window.

No engine, no seed, no reliability coefficient.

    ./.venv/bin/python -m benchmarks.di_window_design
"""

from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "phase_l_results.json"
OUT = ROOT / "docs" / "di_window_design.json"

WINDOW = 40                      # the protocol's window length, cycles
CANDIDATE_ENDS = (190, 250, 300, 350, 400, 450, 500, 550, 600)
SUSTAINED = 10                   # cycles a non-zero reading must persist
LEARNING_CYCLES = 50             # protocol: revision learning 200-250
TEST_CYCLES = 50                 # protocol: revision test 250-300


def _pvar(values: list[float]) -> float:
    return statistics.pvariance(values) if len(values) > 1 else 0.0


def _pstd(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def build() -> dict:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    recs = payload["records"]
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()

    traj = [r["results"]["secondary"]["di_trajectory"] for r in recs]
    labels = [r["label"] for r in recs]
    n = min(len(t) for t in traj)
    denom = sorted({r["results"]["organica"]["late_available"] for r in recs})[0]
    pair = 1 / denom
    by_label: dict[str, list[list[float]]] = {}
    for lab, t in zip(labels, traj):
        by_label.setdefault(lab, []).append(t)

    # ---- emergence -------------------------------------------------------
    emergence: dict[str, dict] = {}
    for lab, runs in sorted(by_label.items()):
        first, sustained, ever = [], [], 0
        for t in runs:
            i = next((k for k, v in enumerate(t) if v > 0), None)
            if i is not None:
                ever += 1
                first.append(i)
                j = next((k for k in range(i, n - SUSTAINED)
                          if all(t[k + m] > 0 for m in range(SUSTAINED))), None)
                if j is not None:
                    sustained.append(j)
        emergence[lab] = {
            "runs": len(runs),
            "runs_ever_nonzero": ever,
            "identically_zero": ever == 0,
            "median_first_nonzero": statistics.median(first) if first else None,
            "min_first_nonzero": min(first) if first else None,
            "max_first_nonzero": max(first) if first else None,
            "median_sustained_nonzero": statistics.median(sustained) if sustained else None,
            "runs_never_sustained": len(runs) - len(sustained),
        }

    # ---- settling, among runs that ever move -----------------------------
    # A run that never leaves zero has no transition to settle; including it
    # would report a settle cycle of 0 and drag the median to a meaningless
    # value. Those runs are counted separately and excluded here.
    settling: dict[str, dict] = {}
    settle_movers: list[float] = []
    identically_zero = 0
    for lab, runs in sorted(by_label.items()):
        last = []
        for t in runs:
            if not any(v > 0 for v in t):
                identically_zero += 1
                continue
            final = t[-1]
            idx = [k for k in range(n) if abs(t[k] - final) >= pair - 1e-12]
            last.append(0 if not idx else max(idx) + 1)
        settle_movers.extend(last)
        settling[lab] = {
            "runs_that_ever_move": len(last),
            "median_settle_cycle": statistics.median(last) if last else None,
            "max_settle_cycle": max(last) if last else None,
            "runs_moving_in_last_50_cycles": sum(1 for c in last if c > n - 50),
        }
    settle_median = statistics.median(settle_movers) if settle_movers else 0.0
    settle_max = max(settle_movers) if settle_movers else 0.0

    # ---- candidate windows ----------------------------------------------
    candidates = []
    for end in CANDIDATE_ENDS:
        start = end - WINDOW
        means = {lab: [sum(t[start:end]) / WINDOW for t in runs]
                 for lab, runs in by_label.items()}
        arm_sd = {lab: _pstd(v) for lab, v in means.items()}
        arm_var_mean = statistics.mean(_pvar(v) for v in means.values())
        between = _pvar([m for v in means.values() for m in v])
        distinct = {lab: len({round(m / pair) for m in v}) for lab, v in means.items()}
        candidates.append({
            "cycles": [start, end],
            "within_config_sd_pairs_median": statistics.median(arm_sd.values()) * denom,
            "within_config_sd_pairs_max": max(arm_sd.values()) * denom,
            "within_config_share_of_variance": (arm_var_mean / between) if between else 0.0,
            "arms_with_single_value": sorted(lab for lab, k in distinct.items() if k == 1),
            "median_distinct_pair_counts": statistics.median(distinct.values()),
            "records_constant_over_window": sum(
                1 for lab, runs in by_label.items()
                for t in runs if len(set(t[start:end])) == 1),
        })

    # ---- resolution available in the settled window ----------------------
    settled = []
    for lab, runs in sorted(by_label.items()):
        vals = [sum(t[n - 50:n]) / 50 for t in runs]
        settled.append({
            "config": lab,
            "mean_di": statistics.mean(vals),
            "sd_pairs": _pstd(vals) * denom,
            "distinct_pair_counts": len({round(v / pair) for v in vals}),
            "min_pairs": min(round(v / pair) for v in vals),
            "max_pairs": max(round(v / pair) for v in vals),
        })

    # ---- the schedule consequence ---------------------------------------
    schedule = {
        "window_length": WINDOW,
        "median_settle_cycle_moving_runs": settle_median,
        "max_settle_cycle_moving_runs": settle_max,
        "runs_identically_zero": identically_zero,
        "run_length_needed_for_settled_measurement_then_learning_then_test":
            settle_median + LEARNING_CYCLES + TEST_CYCLES,
        "protocol_run_length": 150,
        "protocol_window": [110, 150],
        "protocol_measurement_ends_at_cycle": 150,
        "learning_cycles": LEARNING_CYCLES,
        "test_cycles": TEST_CYCLES,
    }

    return {
        "what_this_is": "Stage A of the DI measurement-window design: exploratory "
                        "diagnostics from the 240 stored Phase L records. No engine, "
                        "no seed, no reliability coefficient.",
        "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": digest,
                   "records": len(recs)},
        "units": {"late_pairs_per_record": denom, "one_pair": pair,
                  "window_length": WINDOW},
        "emergence": emergence,
        "settling": settling,
        "candidate_windows": candidates,
        "settled_window_550_600": settled,
        "schedule": schedule,
        "exploratory": True,
        "selection_risk": "These records already drove the decision that the "
                          "protocol's window is misplaced; a window chosen here "
                          "is chosen on them and needs Stage B validation.",
    }


def main() -> dict:
    result = build()
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
    for lab, e in result["emergence"].items():
        print("  %-4s ever %2d/%2d  zero_only=%-5s  first %s  sustained %s"
              % (lab, e["runs_ever_nonzero"], e["runs"], e["identically_zero"],
                 e["median_first_nonzero"], e["median_sustained_nonzero"]))
    print("settle (moving runs only): median %s  max %s  | identically-zero runs %s"
          % (result["schedule"]["median_settle_cycle_moving_runs"],
             result["schedule"]["max_settle_cycle_moving_runs"],
             result["schedule"]["runs_identically_zero"]))
    for c in result["candidate_windows"]:
        print("  %s  within-SD %.2f pairs (max %.2f)  within-share %.4f  single-valued arms %d"
              % (c["cycles"], c["within_config_sd_pairs_median"],
                 c["within_config_sd_pairs_max"], c["within_config_share_of_variance"],
                 len(c["arms_with_single_value"])))
    return result


if __name__ == "__main__":
    main()
