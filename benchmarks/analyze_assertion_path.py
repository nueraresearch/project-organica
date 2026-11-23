"""Summarise the admission trace, correct its field names, and record the resolution boundary."""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path
from benchmarks import engine_stamp

p = Path("docs/gate13_assertion_path.json")
art = json.loads(p.read_text())
cells = art["cells"]

for k, v in cells.items():
    v["admitted_then_absent"] = v.pop("never_asserted")
    v["in_asserted_not_admitted"] = v.pop("lost_edges")
    cov = set(v["covered_set"])
    win = set(v["first_hit"])
    v["covered_in_window"] = len(cov & win)
    v["covered_outside_window"] = len(cov - win)


def m(rows, key):
    return round(st.fmean(r[key] for r in rows), 2)


def by(group, arm):
    return [v for v in cells.values() if v["group"] == group and v["arm"] == arm]


summary = {}
for group in ("fail", "match"):
    summary[group] = {}
    for arm in ("C", "R"):
        rows = by(group, arm)
        summary[group][arm] = {
            "n": len(rows),
            "window_hits_total": round(st.fmean(sum(r["per_cycle_hits"]) for r in rows), 1),
            "window_edges_distinct": m(rows, "ever_world_edges"),
            "covered_in_window": round(st.fmean(r["covered_in_window"] for r in rows), 2),
            "covered_outside_window": round(st.fmean(r["covered_outside_window"] for r in rows), 2),
        }
        summary[group][arm]["covered"] = round(st.fmean(r["verified"]["covered"] for r in rows), 2)
        summary[group][arm]["asserted"] = round(st.fmean(r["verified"]["asserted"] for r in rows), 2)
        summary[group][arm]["covered_gt_window"] = sum(1 for r in rows
                                                       if r["verified"]["covered"] > r["ever_world_edges"])
allR = [v for v in cells.values() if v["arm"] == "R"]
allC = [v for v in cells.values() if v["arm"] == "C"]
summary["all"] = {
    "R": {"hits": round(st.fmean(sum(r["per_cycle_hits"]) for r in allR), 1),
          "distinct_min": min(r["ever_world_edges"] for r in allR),
          "distinct_max": max(r["ever_world_edges"] for r in allR),
          "covered": round(st.fmean(r["verified"]["covered"] for r in allR), 2),
          "outside": round(st.fmean(r["covered_outside_window"] for r in allR), 2),
          "covered_gt_window": sum(1 for r in allR if r["verified"]["covered"] > r["ever_world_edges"])},
    "C": {"hits": round(st.fmean(sum(r["per_cycle_hits"]) for r in allC), 1),
          "distinct_min": min(r["ever_world_edges"] for r in allC),
          "distinct_max": max(r["ever_world_edges"] for r in allC),
          "covered": round(st.fmean(r["verified"]["covered"] for r in allC), 2),
          "outside": round(st.fmean(r["covered_outside_window"] for r in allC), 2),
          "covered_gt_window": sum(1 for r in allC if r["verified"]["covered"] > r["ever_world_edges"])},
    "windows": (min(r["cycles_with_admissions"] for r in cells.values()),
                max(r["cycles_with_admissions"] for r in cells.values())),
    "window_size": sorted({r["window_size_median"] for r in cells.values()}),
}
art["summary"] = summary
art["resolution"] = (
    "The trace is at the prediction-window resolution: it sees the rows each sleep cycle admits to prediction. "
    "`structure_edges` aggregates all six structure types from the stored candidate snapshots, and the window touches "
    "only some of them, so a covered edge can exist without ever appearing in a window. Coverage is therefore not "
    "fully attributable from this trace, and no event-level claim about which admission produced a covered edge is made."
)
art["field_notes"] = {
    "never_asserted -> admitted_then_absent": "world edges that appeared in a window but are not in the final asserted set",
    "lost_edges -> in_asserted_not_admitted": "final covered edges that never appeared in any admission window",
    "covered_in_window": "covered edges that did appear in at least one window",
    "covered_outside_window": "covered edges that appeared in no window (other structure types)",
}
p.write_text(json.dumps(engine_stamp.stamp(art), indent=2) + "\n")
print(json.dumps(summary, indent=2))
