"""Render the confirmatory admission pre-registration from its artifact.

    ./.venv/bin/python -m benchmarks.write_ranking_admission_prereg
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "ranking_admission_prereg.json"
OUT = ROOT / "docs" / "RANKING-ADMISSION-PREREGISTRATION.md"


def render(body: dict) -> str:
    design, seeds, crit = body["design"], body["seeds"], body["criteria"]
    low, high = seeds["block"]
    densities = ", ".join("%.1f" % d for d in design["densities"])
    caps = " and ".join(str(c) for c in design["caps"])
    edges = ", ".join(str(n) for n in design["world_edges_at_each_density"])
    table = "\n".join("| %s | **%s** | %s |" % (r["condition"], r["verdict"], r["reading"])
                      for r in body["decision_table"])
    gates = "\n".join("* **%s** — %s" % (k, v) for k, v in body["gates"]["rules"].items())
    text = """# The admission change, pre-registered with fresh seeds (2026-11-07)

**Status: FROZEN, NOT RUN (ready; no judged cell).** No cell, no judged world and no judged
engine cycle exist for this block. The criteria, the bar, the guard, the seeds and the
decision table below are committed before the run and may not be changed afterwards; a
defect found later is disclosed as an amendment, and the pre-registered reading stands
unless the amendment says plainly that it withdraws it.

This block confirms one thing: whether the admission change specified in
`docs/RANKING-ADMISSION-DESIGN.md` reproduces the coverage gain the completed ordering run
measured, on seeds that block did not use. The numbers are in
`docs/ranking_admission_prereg.json`, and this document is rendered from that artifact.

## 1. Question

Does **%(arms_control)s** beat **%(arms_diversity)s** in world-edge coverage at the sparsest
density, on fresh seeds, without losing coverage where the world is dense?

## 2. Design

- **Arms:** control is %(arms_control_rule)s; treatment is %(arms_diversity_rule)s.
- **Caps:** %(caps)s.
- **World family:** %(family)s, so |P_world| = 240 directed non-self pairs.
- **Densities:** %(densities)s, i.e. %(edges)s true edges.
- **Eligibility:** %(eligibility)s.
- **Exposure:** %(exposure)s.
- **Horizon:** %(horizon)s.
- **Cells:** %(cells)d — %(arithmetic)s.

## 3. Seeds

Block **%(low)d–%(high)d**, bootstrap **%(bootstrap)d**. %(freshness)s

%(consumed)s

## 4. The bar, and where it comes from

**Adoption bar %(bar).2f.** %(bar_provenance)s

**Guard bar %(guard).2f.** %(guard_provenance)s

The adoption criterion is a conjunction, judged whole: the mean gain at the sparsest
density at cap %(primary_cap)d must clear the bar, its %(level)d%% interval's lower bound must
clear zero, and at least %(required)d of %(of)d seeds must move the same way. Any one of the
three failing means the gain does not reproduce.

## 5. Decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
%(table)s

A gate failure is **VOID**, reported as the gate and never as a verdict. The dense-end guard
is not a second criterion: it can only prevent adoption, and a failure routes the result to
a priced trade rather than to a negated adoption.

## 6. Gates

%(gates)s

**Void rule.** %(void)s

## 7. Analysis path

%(command)s

The analysis path is `%(analysis)s`, frozen with this registration. It reads only the cells
the runner writes, imports nothing from the engine, and refuses a cell set that is not the
pre-registered grid. Its input is `%(input)s`.

## 8. Allocation

%(alloc_seeds)d world seeds, %(alloc_bootstrap)d bootstrap seed, %(alloc_cells)d cells,
%(alloc_thresholds)d thresholds and %(alloc_bars)d bars. %(alloc_note)s

No cell may run before this file is committed.
""" % {
        "arms_control": body["arms"]["control"]["name"],
        "arms_diversity": body["arms"]["diversity"]["name"],
        "arms_control_rule": body["arms"]["control"]["rule"],
        "arms_diversity_rule": body["arms"]["diversity"]["rule"],
        "caps": caps, "family": design["world_family"], "densities": densities,
        "edges": edges, "eligibility": design["eligibility"],
        "exposure": design["exposure"], "horizon": design["horizon"],
        "cells": design["cells"], "arithmetic": design["cells_arithmetic"],
        "low": low, "high": high, "bootstrap": seeds["bootstrap"],
        "freshness": seeds["freshness"], "consumed": seeds["consumed"],
        "bar": crit["adoption_bar"], "bar_provenance": crit["adoption_bar_provenance"],
        "guard": crit["guard_bar"], "guard_provenance": crit["guard_bar_provenance"],
        "primary_cap": int(design["caps"][0]), "level": int(round(crit["interval"] * 100)),
        "required": crit["sign_test"]["required"], "of": crit["sign_test"]["of"],
        "table": table, "gates": gates, "void": body["gates"]["void_rule"],
        "command": body["analysis"]["command"], "analysis": body["analysis"]["path"],
        "input": body["analysis"]["input"],
        "alloc_seeds": body["allocation"]["seeds"],
        "alloc_bootstrap": body["allocation"]["bootstrap_seeds"],
        "alloc_cells": body["allocation"]["cells"],
        "alloc_thresholds": body["allocation"]["thresholds"],
        "alloc_bars": body["allocation"]["bars"],
        "alloc_note": body["allocation"]["note"],
    }
    return text


def main() -> int:
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    text = render(body)
    assert "{" not in text.replace("{%", ""), "a placeholder survived the render"
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), "lines:", len(text.splitlines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
