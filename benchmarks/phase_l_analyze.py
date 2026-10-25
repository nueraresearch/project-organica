"""Phase L analysis: read the campaign results and produce the report.

This is the analysis that produced the reported Phase L numbers, and it
lives in the repository (not in scratch) so every reported figure is
reproducible from committed code.

It implements the preregistered analysis:
  - per-arm DI / PI / DS curves and the revision-latency report
  - the four success criteria for the primary axis V1
  - the Revision Threshold and its paired bootstrap interval
  - robustness: 8 alternative bootstrap seeds + leave-one-seed-out
  - the adjacent-difference diagnostic (Amendment 3): the paired difference
    between each adjacent pair of sweep points, with a 99% paired interval
  - the pre-committed terminal outcome (H2-L / H2-L' / H2-L3 / H3-L)

Usage:
    python benchmarks/phase_l_analyze.py [--results docs/phase_l_results.json]

The bootstrap here pairs by SEED, not by position in the records list. The
records arrive in completion order, and completion order differs from label
to label, so pairing by position pairs unrelated seeds across labels.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import benchmarks.phase_l_campaign as P


def quantile(values, q):
    ordered = sorted(values)
    if not ordered:
        return None
    pos = (len(ordered) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return ordered[lo] if lo == hi else ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def curve_for(records, arm):
    by_label = {}
    for r in records:
        if r["arm"] == arm:
            by_label.setdefault(r["label"], []).append(r)
    order = [lbl for lbl in P._label_order(arm) if lbl in by_label]
    out = []
    for lbl in order:
        rows = by_label[lbl]
        dis = [r["results"]["organica"]["displacement_index"] for r in rows
               if r["results"]["organica"]["displacement_index"] is not None]
        pre = [r["results"]["organica"]["preservation_index"] for r in rows
               if r["results"]["organica"]["preservation_index"] is not None]
        dsc = [r["results"]["organica"].get("displacement_score") for r in rows
               if r["results"]["organica"].get("displacement_score") is not None]
        lat = [r["results"]["secondary"]["revision_latency_cycles"] for r in rows
               if r["results"].get("secondary", {}).get("revision_latency_cycles") is not None]
        out.append({
            "label": lbl,
            "n_seeds": len(rows),
            "n_measurable": min(len(dis), len(pre)),
            "di": statistics.mean(dis) if dis else None,
            "pi": statistics.mean(pre) if pre else None,
            "ds": statistics.mean(dsc) if dsc else None,
            "di_sd": statistics.stdev(dis) if len(dis) > 1 else 0.0,
            "pi_sd": statistics.stdev(pre) if len(pre) > 1 else 0.0,
            "latency_mean": statistics.mean(lat) if lat else None,
            "latency_median": statistics.median(lat) if lat else None,
            "latency_reached": sum(
                1 for r in rows
                if r["results"].get("secondary", {}).get("revision_latency_reached")),
            "di_values": dis,
            "pi_values": pre,
        })
    return out


def crossing_index(di, pi):
    for i in range(1, len(di)):
        if di[i - 1] <= pi[i - 1] and di[i] > pi[i]:
            return i
    return None


def rt_bootstrap(records, arm, crossing, bootstrap_seed=9000,
                 replicates=P.BOOTSTRAP_REPLICATES):
    """Resample seeds PAIRED across labels and record where the crossing
    lands in each resample. Returns (interval, n_with_crossing).

    The pairing is by SEED. Each label contributes {seed: value}, the seeds
    common to every label are drawn with replacement, and every label is
    evaluated on that same drawn set of seeds.
    """
    if crossing is None:
        return None, 0
    by_label = {}
    for r in records:
        if r["arm"] == arm:
            by_label.setdefault(r["label"], []).append(r)
    labels = [lbl for lbl in P._label_order(arm) if by_label.get(lbl)]
    di_maps = {lbl: P._seed_metric_map(by_label[lbl], "displacement_index")
               for lbl in labels}
    pi_maps = {lbl: P._seed_metric_map(by_label[lbl], "preservation_index")
               for lbl in labels}
    common = P._common_seeds([di_maps[l] for l in labels]
                              + [pi_maps[l] for l in labels])
    n_seeds = len(common)
    if n_seeds < 2:
        return None, 0
    crossings = []
    for b in range(replicates):
        rng = random.Random(bootstrap_seed + b)
        picks = [common[rng.randrange(n_seeds)] for _ in range(n_seeds)]
        d_s = [statistics.mean(di_maps[lbl][s] for s in picks) for lbl in labels]
        p_s = [statistics.mean(pi_maps[lbl][s] for s in picks) for lbl in labels]
        c = crossing_index(d_s, p_s)
        if c is not None:
            crossings.append(c)
    if not crossings:
        return None, 0
    return ([quantile(crossings, P.DECISION_LOWER_Q),
             quantile(crossings, P.DECISION_UPPER_Q)], len(crossings))


def adjacent_difference(records, arm, from_label, to_label, metric):
    """The paired difference (to - from) over the seeds present in both."""
    def pick(lbl):
        rows = [r for r in records if r["arm"] == arm and r["label"] == lbl]
        return P._seed_metric_map(rows, metric)
    a_map, b_map = pick(from_label), pick(to_label)
    shared = sorted(set(a_map) & set(b_map))
    if len(shared) < 2:
        return None
    diffs = [b_map[s] - a_map[s] for s in shared]
    rng = random.Random(31_000)
    means = sorted(statistics.mean(diffs[rng.randrange(len(diffs))]
                                   for _ in range(len(diffs)))
                   for _ in range(P.BOOTSTRAP_REPLICATES))
    return {
        "from": from_label, "to": to_label,
        "n_paired_seeds": len(shared),
        "mean_difference": round(statistics.mean(diffs), 6),
        "interval": [round(quantile(means, P.DECISION_LOWER_Q), 6),
                     round(quantile(means, P.DECISION_UPPER_Q), 6)],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="docs/phase_l_results.json")
    args = ap.parse_args()

    path = REPO / args.results
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data["records"]
    protocol = data.get("protocol", {})

    print("=" * 78)
    print("PHASE L -- ANALYSIS")
    print("=" * 78)
    print(f"  results file : {args.results}")
    print(f"  cells        : {len(records)}")
    print(f"  complete     : {protocol.get('complete')}")
    print(f"  hash seed    : {protocol.get('python_hash_seed')} "
          f"(pinned ok: {protocol.get('python_hash_seed_pinned_ok')})")
    print(f"  decision int.: {protocol.get('decision_interval_level')} "
          f"(alpha {protocol.get('decision_alpha')})")
    print(f"  wall clock   : {protocol.get('wall_clock_seconds')}s")

    for key in ("control", "ceiling_check", "degeneracy_audit", "v4_pressure_audit"):
        a = data.get(key)
        if isinstance(a, dict):
            print(f"  audit {key:20s}: {'PASS' if a.get('passed') else 'FAIL'}")

    arms = sorted({r["arm"] for r in records})
    print()
    for arm in arms:
        curve = curve_for(records, arm)
        di = [c["di"] for c in curve]
        pi = [c["pi"] for c in curve]
        print("-" * 78)
        print(f"ARM {arm}   (n={curve[0]['n_seeds']} seeds/point)" if curve else f"ARM {arm}")
        print(f"  {'label':>8}  {'DI':>7} {'(sd)':>6}  {'PI':>7} {'(sd)':>6}  "
              f"{'DS':>7}  {'latency':>8}")
        for c in curve:
            lat = (f"{c['latency_mean']:.0f}"
                   if c["latency_mean"] is not None else "-")
            reach = f"{c['latency_reached']}/{c['n_seeds']}"
            print(f"  {c['label']:>8}  {c['di']:7.3f} {c['di_sd']:6.3f}  "
                  f"{c['pi']:7.3f} {c['pi_sd']:6.3f}  {c['ds']:+7.3f}  "
                  f"{lat:>8} ({reach})")

        mono_di = all(a <= b + 1e-9 for a, b in zip(di, di[1:]))
        mono_pi = all(a >= b - 1e-9 for a, b in zip(pi, pi[1:]))
        rng_ = (max(di) - min(di)) if di else 0.0
        cross = crossing_index(di, pi)
        print(f"  monotone DI up: {mono_di}   monotone PI down: {mono_pi}   "
              f"DI range: {rng_:.3f}")
        if cross is not None:
            print(f"  crossing at {curve[cross]['label']} "
                  f"(index {cross} of {len(curve)-1} interior positions)")
        else:
            print("  no crossing")

        if arm == "V1" and cross is not None:
            interval, n_with = rt_bootstrap(records, arm, cross)
            print(f"  RT bootstrap interval (sweep positions): {interval}  "
                  f"[{n_with}/{P.BOOTSTRAP_REPLICATES} replicates found a crossing]")
            print(f"  decision interval: {P.DECISION_LOWER_Q:.5f} .. "
                  f"{P.DECISION_UPPER_Q:.5f}")

            # Robustness: 8 alternative bootstrap seeds.
            verdicts = []
            for s in range(1, 9):
                iv, _ = rt_bootstrap(records, arm, cross,
                                     bootstrap_seed=9000 + s * 1000, replicates=2000)
                if iv is None:
                    verdicts.append("NO_INTERVAL")
                else:
                    verdicts.append("INTERIOR" if (iv[0] > 0 and iv[1] < len(curve) - 1)
                                    else "INCLUDES_ENDPOINT")
            print(f"  robustness (8 bootstrap seeds): {sorted(set(verdicts))}")

            # Robustness: leave one seed out (drops by SEED, so this one was
            # already seed-correct).
            seeds = sorted({r["seed"] for r in records if r["arm"] == arm})
            loo = []
            for drop in seeds:
                sub = [r for r in records if not (r["arm"] == arm and r["seed"] == drop)]
                c2 = curve_for(sub, arm)
                d2 = [x["di"] for x in c2]
                p2 = [x["pi"] for x in c2]
                cr2 = crossing_index(d2, p2)
                if cr2 is None:
                    loo.append("NO_CROSSING")
                elif 0 < cr2 < len(c2) - 1:
                    loo.append(curve[cr2]["label"])
                else:
                    loo.append("ENDPOINT")
            print(f"  leave-one-seed-out crossings: {loo}")

        # The adjacent-difference diagnostic (Amendment 3).
        print("  adjacent differences (paired by seed; DIAGNOSTIC, not a criterion):")
        for i in range(len(curve) - 1):
            a_lbl, b_lbl = curve[i]["label"], curve[i + 1]["label"]
            dd = adjacent_difference(records, arm, a_lbl, b_lbl, "displacement_index")
            dp = adjacent_difference(records, arm, a_lbl, b_lbl, "preservation_index")
            def fmt(d):
                if d is None:
                    return "n/a"
                return f"{d['mean_difference']:+.3f} [{d['interval'][0]:+.3f}, {d['interval'][1]:+.3f}]"
            print(f"    {a_lbl:>4} -> {b_lbl:<4}  dDI {fmt(dd):>26}   dPI {fmt(dp):>26}")

    print()
    print("=" * 78)
    print("VERDICT (primary axis V1, by the four pre-committed criteria)")
    print("=" * 78)
    curve = curve_for(records, "V1")
    di = [c["di"] for c in curve]
    pi = [c["pi"] for c in curve]
    c1 = all(a <= b + 1e-9 for a, b in zip(di, di[1:]))
    c2 = all(a >= b - 1e-9 for a, b in zip(pi, pi[1:]))
    c3 = (max(di) - min(di)) >= 0.25
    cross = crossing_index(di, pi)
    interior = cross is not None and 0 < cross < len(curve) - 1
    interval, n_with = (rt_bootstrap(records, "V1", cross)
                        if cross is not None else (None, 0))
    c4 = interval is not None and interval[0] > 0 and interval[1] < len(curve) - 1
    print(f"  1. DI monotone increasing        : {c1}")
    print(f"  2. PI monotone decreasing        : {c2}")
    print(f"  3. DI range >= 0.25              : {c3} (range {max(di)-min(di):.3f})")
    print(f"     crossing interior to the sweep: {interior}"
          + (f" at {curve[cross]['label']}" if cross is not None else ""))
    print(f"  4. RT interval excludes endpoints : {c4} (interval {interval})")
    if all([c1, c2, c3, interior, c4]):
        print("  => H2-L  a boundary exists")
    elif cross is None:
        print("  => H2-L' no boundary (the system sits at a pole)")
    else:
        print("  => H3-L inconclusive (raise n; conclude nothing)")
    print()
    print("  NO OUTCOME HERE AUTHORISES A V2.")


if __name__ == "__main__":
    main()
