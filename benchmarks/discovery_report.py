"""
The discovery report: what the organism actually found, and when.

M5 is "development velocity", defined as `new items per 100 cycles`. The
campaign exposed a problem with that name. Over 300 cycles the FULL arm
recorded 74 new items; over 3,000 cycles it also recorded 74. The rate fell
from 24.667 to 2.467 because the **numerator stopped growing** while the
denominator grew tenfold. The rate had been dividing a finite inventory by
the run length, and calling that a "velocity" invited reading it as a rate
of ongoing development.

So this report does two things the metric cannot:

1. **Breaks the inventory down by category** -- how many distinct beliefs,
   questions, theories, dreams, investigations and experiments were ever
   discovered, per colony.
2. **Plots the cumulative discovery curve** -- the running total of distinct
   items against the cycle. A curve that rises steeply and then flattens is
   a repertoire being exhausted. A curve that keeps rising is development.

The stimulus matters for reading the curve, and the report states it: the
`lattice_L1` world contains **9 distinct events** and the organism's
experience **repeats every 9 cycles**. A repertoire cannot grow in a world
that does not change. So the flat tail is a fact about this world as much as
a fact about the organism, and the report says so rather than letting the
curve be read as an architectural ceiling.

Usage:
    python benchmarks/discovery_report.py
Writes docs/discovery.json and docs/figure_discovery.svg
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.figure_campaign import (  # noqa: E402
    COLORS, Svg, axes, panel, series_points)

CATEGORIES = ["beliefs", "questions", "theories", "dreams", "investigations",
              "experiments"]
M5_CATEGORIES = ["beliefs", "questions", "dreams", "experiments"]


def stimulus_facts() -> dict:
    """Measure the stimulus rather than asserting anything about it."""
    from organica.branch_streams import (
        NEUTRAL_HUB, NEUTRAL_PETALS, lattice_designs, lattice_stream)
    from organica.streams import EVENTS_PER_CYCLE

    lattice = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
    events = lattice_stream(lattice["L1_hub1_t3_disjoint"]["triangles"])
    consumed = []
    for i in range(400):
        start = (i * EVENTS_PER_CYCLE) % len(events)
        consumed.append(tuple(events[start:start + EVENTS_PER_CYCLE]))
    period = None
    for p in range(1, 200):
        if all(consumed[i] == consumed[i + p]
               for i in range(len(consumed) - p)):
            period = p
            break
    return {
        "stream_length": len(events),
        "distinct_event_strings": len(set(events)),
        "distinct_words": len({w for e in events for w in e.split()}),
        "events_per_cycle": EVENTS_PER_CYCLE,
        "experience_period_cycles": period,
        "triangles": lattice["L1_hub1_t3_disjoint"]["triangles"],
        "note": ("The organism's experience repeats every N cycles. A "
                 "repertoire cannot grow in a world that does not change, so "
                 "the flat tail of the discovery curve is a fact about this "
                 "stimulus as much as about the organism."),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default=str(REPO / "docs" / "force_matrix.json"))
    ap.add_argument("--out", default=str(REPO / "docs" / "discovery.json"))
    ap.add_argument("--figure",
                    default=str(REPO / "docs" / "figure_discovery.svg"))
    args = ap.parse_args()

    path = Path(args.matrix)
    if not path.exists():
        print("campaign artifact not present:", path)
        sys.exit(1)
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = {r["colony"]: r for r in doc["rows"]}
    cycles = doc.get("cycles") or 0

    print("=" * 92)
    print(f"DISCOVERY REPORT -- {cycles} cycles/colony, "
          f"stimulus {doc.get('stimulus')}")
    print("=" * 92)

    # ---- 1. the inventory, broken down ------------------------------------
    print()
    print("1. THE INVENTORY -- distinct items ever discovered, by category")
    print("-" * 92)
    header = f"{'colony':<20}" + "".join(f"{c[:11]:>12}" for c in CATEGORIES)
    print(header)
    print(f"{'':<20}" + "".join(f"{'M5 total':>12}" for _ in range(1)))
    inventory = {}
    for name, r in rows.items():
        m5 = r["metrics"]["M5_development_velocity"]
        per_cat = m5.get("inventory_per_category", {})
        inventory[name] = {
            "per_category": per_cat,
            "m5_total": m5.get("inventory_total"),
            "distinct_beliefs_ever": m5.get("distinct_beliefs_ever"),
            "rate_per_100_cycles": m5.get("new_per_100_cycles"),
            "last_100_new_total": m5.get("last_100_new_total"),
        }
        print(f"{name:<20}" + "".join(f"{per_cat.get(c, 0):>12}"
                                      for c in CATEGORIES))
    print(f"{'  (M5 counts only beliefs + questions + dreams + experiments)':<20}")
    print()
    print(f"{'colony':<20}{'M5 total':>12}{'rate/100cyc':>14}"
          f"{'new in last 100':>19}")
    for name, r in rows.items():
        inv = inventory[name]
        print(f"{name:<20}{inv['m5_total']:>12}"
              f"{inv['rate_per_100_cycles']:>14}{inv['last_100_new_total']:>19}")

    # ---- 2. the discovery curve -------------------------------------------
    print()
    print("2. THE DISCOVERY CURVE -- cumulative distinct items vs cycle")
    print("-" * 92)
    curve_stats = {}
    for name, r in rows.items():
        disc = r.get("series", {}).get("discovery", {})
        cum = disc.get("m5_cycle_cumulative_total") or []
        if not cum:
            continue
        total = cum[-1]
        # the cycle at which 95% of the inventory was already discovered
        reached = next((i for i, v in enumerate(cum) if v >= 0.95 * total), None)
        curve_stats[name] = {
            "cumulative": cum,
            "total": total,
            "cycle_95pct_reached": reached,
            "cycle_99pct_reached": next(
                (i for i, v in enumerate(cum) if v >= 0.99 * total), None),
            "per_category_cumulative": disc.get("cumulative", {}),
        }
        print(f"  {name:<20} total={total:<6} "
              f"95% discovered by cycle {reached}   "
              f"99% by cycle {curve_stats[name]['cycle_99pct_reached']}")

    # ---- 3. the stimulus --------------------------------------------------
    stim = stimulus_facts()
    print()
    print("3. THE STIMULUS -- what the organism could possibly find")
    print("-" * 92)
    for k, v in stim.items():
        if k == "note":
            continue
        print(f"  {k:<28} {v}")
    print()
    print("  " + stim["note"])

    Path(args.out).write_text(json.dumps({
        "matrix_artifact": args.matrix,
        "cycles": cycles,
        "stimulus": doc.get("stimulus"),
        "inventory": inventory,
        "discovery_curves": curve_stats,
        "stimulus_facts": stim,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")

    _figure(rows, curve_stats, cycles, Path(args.figure))


def _figure(rows, curve_stats, cycles, out: Path) -> None:
    svg = Svg(1240, 900)
    svg.text(30, 34, "Organica — the discovery curve", size=19, weight="bold")
    svg.text(30, 55,
             "cumulative distinct items discovered against cycle — a curve that "
             "flattens is a repertoire being exhausted, not development slowing",
             size=12, fill="#555")
    svg.text(30, 72,
             f"{cycles} cycles per colony · lattice_L1: 9 distinct events, "
             f"experience repeats every 9 cycles · PYTHONHASHSEED pinned to 0",
             size=11, fill="#777")

    # ---- A: cumulative discovery, every colony ---------------------------
    px, py, pw, ph = panel(svg, 30, 92, 580, 360,
                           "A · Cumulative items discovered")
    ymax = max((c["total"] for c in curve_stats.values()), default=1)
    axes(svg, px, py, pw, ph, 0, ymax, cycles, "distinct items", "cycle")
    for name, c in curve_stats.items():
        svg.polyline(series_points(c["cumulative"], px, py, pw, ph, 0, ymax,
                                   cycles),
                     COLORS.get(name, "#333"), width=1.8)
    for i, name in enumerate(curve_stats):
        lx = px + 14 + (i % 3) * 150
        ly = py + 10 + (i // 3) * 18
        svg.rect(lx, ly, 18, 4, COLORS.get(name, "#333"))
        svg.text(lx + 24, ly + 6, name, size=10,
                 fill=COLORS.get(name, "#333"), weight="bold")

    # ---- B: the shape of the first 120 cycles ---------------------------
    px, py, pw, ph = panel(svg, 630, 92, 580, 360,
                           "B · The first 120 cycles, close up")
    win = min(120, cycles)
    ymax = max((c["total"] for c in curve_stats.values()), default=1)
    axes(svg, px, py, pw, ph, 0, ymax, win, "distinct items", "cycle")
    for name, c in curve_stats.items():
        svg.polyline(series_points(c["cumulative"][:win], px, py, pw, ph,
                                   0, ymax, win),
                     COLORS.get(name, "#333"), width=1.8)

    # ---- C: per-cycle new items for FULL -------------------------------
    px, py, pw, ph = panel(svg, 30, 468, 580, 380,
                           "C · New items per cycle (reference arm)")
    disc = rows.get("FULL", {}).get("series", {}).get("discovery", {})
    new_per_cycle = disc.get("m5_cycle_new_total") or []
    if new_per_cycle:
        ymax = max(new_per_cycle)
        axes(svg, px, py, pw, ph, 0, ymax, cycles, "new items", "cycle")
        svg.polyline(series_points(new_per_cycle, px, py, pw, ph, 0, ymax,
                                   cycles),
                     COLORS["FULL"], width=1.4)
        svg.text(px + 10, py + 20,
                 f"peak {ymax} new items in one cycle; "
                 f"{disc.get('m5_cycle_cumulative_total', [0])[-1]} distinct "
                 f"items in total",
                 size=10, fill="#444")

    # ---- D: the inventory, per colony, per category ---------------------
    px, py, pw, ph = panel(svg, 630, 468, 580, 380,
                           "D · What was discovered, by category")
    cats = ["beliefs", "questions", "theories", "dreams", "investigations",
            "experiments"]
    names = list(rows)
    totals = [sum(rows[n]["metrics"]["M5_development_velocity"]
                  .get("inventory_per_category", {}).get(c, 0)
                  for c in cats) for n in names]
    ymax = max(totals) if totals else 1
    axes(svg, px, py, pw, ph, 0, ymax, len(names), "items discovered", "colony")
    bar_w = pw / max(1, len(names)) * 0.6
    for i, n in enumerate(names):
        x = px + pw * (i + 0.2) / max(1, len(names))
        per_cat = rows[n]["metrics"]["M5_development_velocity"].get(
            "inventory_per_category", {})
        bottom = 0
        palette = ["#1f4e79", "#c0504d", "#7f7f7f", "#e8a33d", "#4f9d69",
                   "#8064a2"]
        for j, c in enumerate(cats):
            v = per_cat.get(c, 0)
            if not v:
                continue
            h = v / (ymax or 1) * ph
            svg.rect(x, py + ph - bottom - h, bar_w, h, palette[j % len(palette)])
            bottom += h
        svg.text(x + bar_w / 2, py + ph + 16, n[:12], size=9, fill="#555",
                 anchor="middle")
    for j, c in enumerate(cats):
        lx = px + 10 + (j % 3) * 175
        ly = py + 12 + (j // 3) * 18
        svg.rect(lx, ly, 14, 4, ["#1f4e79", "#c0504d", "#7f7f7f", "#e8a33d",
                                 "#4f9d69", "#8064a2"][j])
        svg.text(lx + 20, ly + 6, c, size=10, fill="#444")

    svg.text(30, 872,
             "Theories and investigations are derived from beliefs and "
             "experiments, so the stack double-counts them; the M5 total "
             "counts only beliefs, questions, dreams and experiments.",
             size=10, fill="#777")
    svg.save(out)


if __name__ == "__main__":
    main()
