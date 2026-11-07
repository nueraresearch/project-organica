"""Render the density interaction's registration document from its artifact.

Every figure in the document is substituted from `docs/density_interaction_prereg.json`
or, once the block has run, from `docs/density_interaction_result.json`. No number is
typed here, and the render asserts that no placeholder survives.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "density_interaction_prereg.json"
OUT = ROOT / "docs" / "DENSITY-INTERACTION-PREREGISTRATION.md"
RESULT = ROOT / "docs" / "density_interaction_result.json"


def _audit_rows(block: dict) -> str:
    lines = ["| rho_world | control, cap 20 | treated, cap 20 | Delta, cap 20 "
             "| intra-cell share |", "|---|---|---|---|---|"]
    for row in block["rows"]:
        lines.append("| %.1f | %.4f | %.4f | %+.4f | %.4f |"
                     % (row["rho_world"], row["control_cap_20"],
                        row["treated_cap_20"], row["delta_cap_20"],
                        row["intra_cell_share"]))
    return "\n".join(lines)


def render(body: dict) -> str:
    d, s, c = body["design"], body["seeds"], body["criteria"]
    low, high = s["block"]
    table = "\n".join("| %s | **%s** | %s | %s |"
                      % (r["condition"], r["verdict"], r["reading"], r["decision"])
                      for r in body["decision_table"])
    gates = "\n".join("* **%s** — %s" % (k, v) for k, v in body["gates"]["rules"].items())
    audit = body["leverage_audit"]
    return """# The density interaction: the registered block (2026-11-07)

**Status: %(status)s**

**Every figure this block produces carries its arm and its scheme.** The arms are
`%(control)s` (%(control_rule)s) and `%(treated)s` (%(treated_rule)s); the schemes are
`%(primary)s` exposure and `%(sensitivity)s` exposure. A number quoted from this block
without its arm, its cap and its scheme is not a number from this block.

## 1. Question and endpoint

%(question)s

The endpoint is **precision at a fixed cap**: the share of the budget spent on the world's
edges. It is not coverage. Coverage divides by |W|, which grows from %(low_edges)d to
%(high_edges)d across this ladder, so a coverage difference is forced by arithmetic and
declines whether or not the treatment does anything — the defect that withdrew the
ordering block's second criterion. Precision's denominator is the arm's own selection, so
its shape across the ladder is a fact about the ranking.

This is a selection measurement, not a behavioural one: it says nothing about prediction,
revision or retention.

## 2. Design

**The world.** %(world)s

**Densities.** %(densities)s, i.e. %(edges)s world edges at 16 tags. The top of the
ladder is the whole cross-cell universe, which is why it stops at 0.8: a higher density is
not a denser version of this world but a different vocabulary.

**Exposure.** %(exposure)s

**The grid.** %(cells)d cells over seeds **%(low)d–%(high)d**, bootstrap **%(bootstrap)d**
— %(arith)s. Freshness: %(freshness)s

## 3. The bars, the criteria and the gates

**Interaction bar %(ibar).2f; level bar %(lbar).2f.** %(bar_provenance)s

**The criterion is the interaction, judged whole.** %(c1)s. %(c2)s. The conjunction is
the criterion: the number of criteria satisfied is not a score, and a failed half is not
re-read afterwards.

**The exposure check.** %(exposure_rule)s

%(gates)s

**Void rule.** %(void)s

## 4. Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
%(table)s

## 5. What is reported

Delta(rho) per seed, per scheme and per cap, with its paired interval; the precision and
coverage of both arms at every density; the pool's intra-cell share and `rho_rank` at every
cell; and the recovery curve at the caps %(recovery_caps)s as a characterization, never as
a criterion and never as the rank of the first edge.

## 6. Pre-run amendment A1 — the registered direction was corrected before any cell

**%(amendment_id)s, dated %(amendment_date)s, before the first judged cell.** %(amendment_why)s

The evidence is the design's own world, measured with no engine: the arms on the
**designed** pools, over the registered seed block. At the primary cap:

%(audit_rows)s

Across the ladder the intra-cell share falls (%(share_falls)s), the control's own
precision rises (%(control_rises)s) — which is the design record's mechanical prediction —
and the treatment's advantage rises with density (%(delta_rises)s). The mechanism is
stated in the registration: **the benefit of freeing budget is bounded by how many world
rows exist to fill it**, and that count grows with density, so a sparse world has too few
world edges for the freed budget to spend on.

These are properties of the world, not of the engine, and they are not scored. What they
establish is that the corrected direction is **representable** by this instrument — which
the original prediction was not, because on this world it is the opposite of what the
construction produces. The design record's original prediction is retained in its section
5 and marked superseded in its section 10. %(amendment_changes)s

## 7. Analysis and runner

`%(command)s`

The analysis path is `%(path)s`, frozen with this registration. It reads only the cells
the runner writes, validates the grid, and imports nothing from the engine. The runner is
`%(runner)s`; it can be sliced (`--scheme`, `--seeds`) and appended (`--append`), and it
refuses to overwrite a cell inside one block.

## 8. Allocation

%(seeds)d world seeds, %(bootstrap_seeds)d bootstrap seed, %(judged)d judged cells,
%(sensitivity_cells)d exposure-check cells, %(recovery)d recovery caps, %(thresholds)d
thresholds, %(bars)d bars. %(note)s

No arm may run before this file is committed.
""" % {
        "status": body["status"],
        "control": body["arms"]["control"]["name"],
        "control_rule": body["arms"]["control"]["rule"],
        "treated": body["arms"]["intra_cell_excluded"]["name"],
        "treated_rule": body["arms"]["intra_cell_excluded"]["rule"],
        "primary": "fixed-total", "sensitivity": "fixed-per-edge",
        "question": body["question"],
        "low_edges": audit["rows"][0]["world_edges"],
        "high_edges": audit["rows"][-1]["world_edges"],
        "world": d["world"],
        "densities": ", ".join("%.1f" % rho for rho in d["densities"]),
        "edges": ", ".join(str(row["world_edges"]) for row in audit["rows"]),
        "exposure": d["exposure"],
        "cells": d["cells"],
        "low": low, "high": high, "bootstrap": s["bootstrap"],
        "freshness": s["freshness"], "arith": d["cells_arithmetic"],
        "ibar": c["interaction_bar"], "lbar": c["level_bar"],
        "bar_provenance": c["bar_provenance"],
        "c1": c["C1"], "c2": c["C2"],
        "exposure_rule": c["exposure_rule"],
        "gates": gates, "void": body["gates"]["void_rule"],
        "table": table,
        "recovery_caps": ", ".join(str(cap) for cap in d["recovery_caps"]),
        "amendment_id": body["amendment"]["id"],
        "amendment_date": body["amendment"]["date"],
        "amendment_why": body["amendment"]["why"],
        "audit_rows": _audit_rows(audit),
        "share_falls": "yes" if audit["share_falls"] else "no",
        "control_rises": "yes" if audit["control_rises"] else "no",
        "delta_rises": "yes" if audit["delta_rises"] else "no",
        "amendment_changes": body["amendment"]["what_changes"],
        "command": body["analysis"]["command"],
        "path": body["analysis"]["path"], "runner": body["analysis"]["runner"],
        "seeds": body["allocation"]["seeds"],
        "bootstrap_seeds": body["allocation"]["bootstrap_seeds"],
        "judged": body["allocation"]["judged_cells"],
        "sensitivity_cells": body["allocation"]["sensitivity_cells"],
        "recovery": body["allocation"]["recovery_caps"],
        "thresholds": body["allocation"]["thresholds"],
        "bars": body["allocation"]["bars"],
        "note": body["allocation"]["note"],
    }


def render_result(body: dict, result: dict) -> str:
    """§9 is post-freeze: every number is read from the result artifact."""
    crit, gates = result["criteria"], result["gates"]
    c1, c2 = crit["C1_interaction"], crit["C2_level_at_dense"]
    failed = sorted(k for k, v in gates.items()
                    if isinstance(v, dict) and v.get("passed") is False)
    rows = "\n".join("| %s | %s | %+.6f |"
                     % (rho, " / ".join("%+.6f" % row[scheme]["delta_precision_mean"]
                                        for scheme in ("primary", "sensitivity")),
                        row["primary"]["delta_precision_mean"] - row["sensitivity"]
                        ["delta_precision_mean"])
                     for rho, row in crit["profile"].items())
    return """## 9. Result (post-freeze)

**%(verdict)s.** %(reading)s

- **Cells:** %(cells)d, gates %(gates)s.
- **C1, interaction:** mean %(c1mean)+.6f, %(level)d%% interval [%(c1lo)+.6f, %(c1hi)+.6f],
  width %(c1width).6f, bar %(c1bar).2f — %(c1state)s.
- **C2, level at the dense end:** mean %(c2mean)+.6f, interval [%(c2lo)+.6f, %(c2hi)+.6f],
  bar %(c2bar).2f, %(c2pos)d of %(c2of)d seeds positive — %(c2state)s.
- **Exposure check:** sensitivity-scheme interaction %(exp)+.6f — %(expstate)s.

| rho_world | Delta precision, primary / sensitivity (cap 20) | primary − sensitivity |
| --- | --- | --- |
%(rows)s

The registration's sections 1–8 are exactly as committed before the run. Cells are in
`docs/density_interaction_run.json`; the verdict is the frozen scorer's output in
`docs/density_interaction_result.json`.
""" % {
        "verdict": result["decision"]["verdict"],
        "reading": result["decision"]["reading"],
        "cells": result["cells"],
        "gates": "all passed" if gates["all_passed"] else "failed: " + ", ".join(failed),
        "c1mean": c1["mean"], "level": 95, "c1lo": c1["interval"][0],
        "c1hi": c1["interval"][1], "c1width": c1["interval_width"],
        "c1bar": c1["bar"], "c1state": "passed" if c1["passed"] else "failed",
        "c2mean": c2["mean"], "c2lo": c2["interval"][0], "c2hi": c2["interval"][1],
        "c2bar": c2["bar"], "c2pos": c2["seeds_positive"], "c2of": c2["of"],
        "c2state": "passed" if c2["passed"] else "failed",
        "exp": crit["exposure"]["sensitivity_interaction_mean"],
        "expstate": ("agrees in sign" if crit["exposure"]["agrees_in_sign"]
                     else "does not agree in sign"),
        "rows": rows,
    }


def main() -> int:
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    text = render(body)
    assert "{" not in text.replace("{%", ""), "a placeholder survived the render"
    if body.get("run") and RESULT.exists():
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        banner = ("**This block has run: the frozen analysis path returned %s.** Section 9 "
                  "records the result, and sections 1–8 are preserved exactly as committed "
                  "before the run." % result["decision"]["verdict"])
        head, rest = text.split("\n\n", 1)
        text = head + "\n\n" + banner + "\n\n" + rest + "\n" + render_result(body, result)
    assert "{" not in text.replace("{%", ""), "a placeholder survived the render"
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), "lines:", len(text.splitlines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
