"""Render A2's registration document from its artifact.

Every figure is substituted from `docs/density_interaction_a2_prereg.json` or, once the
block has run, from `docs/density_interaction_a2_result.json`. No number is typed here, and
the render asserts that no placeholder survives. A1's renderer is left untouched: its
document is frozen with its held artifact.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "density_interaction_a2_prereg.json"
OUT = ROOT / "docs" / "DENSITY-INTERACTION-A2-PREREGISTRATION.md"
RESULT = ROOT / "docs" / "density_interaction_a2_result.json"


def _audit_rows(block: dict) -> str:
    lines = ["| rho_world | control, cap 20 | treated, cap 20 | Delta, cap 20 "
             "| intra-cell share |", "|---|---|---|---|---|"]
    for row in block["rows"]:
        lines.append("| %.1f | %.4f | %.4f | %+.4f | %.4f |"
                     % (row["rho_world"], row["control_cap_20"],
                        row["treated_cap_20"], row["delta_cap_20"],
                        row["intra_cell_share"]))
    return "\n".join(lines)


def _pilot_rows(pilot: dict) -> str:
    lines = ["| scheme | sparse mean | dense mean | interaction mean | per seed |",
             "|---|---|---|---|---|"]
    for name in ("primary", "sensitivity"):
        row = pilot[name]
        lines.append("| %s | %.3f (sd %.3f) | %.3f (sd %.3f) | %+.4f (sd %.3f) | %s |"
                     % (name, row["sparse_delta_mean"], row["sparse_delta_sd"],
                        row["dense_delta_mean"], row["dense_delta_sd"],
                        row["interaction_mean"], row["interaction_sd"],
                        ", ".join("%+.2f" % v for v in row["interaction_per_seed"])))
    return "\n".join(lines)


def render(body: dict) -> str:
    d, s, c, pilot = body["design"], body["seeds"], body["criteria"], body["pilot"]
    low, high = s["block"]
    table = "\n".join("| %s | **%s** | %s | %s |"
                      % (row["condition"], row["verdict"], row["reading"],
                         row["decision"])
                      for row in body["decision_table"])
    gates = "\n".join("* **%s** — %s" % (key, value)
                      for key, value in body["gates"]["rules"].items())
    audit = body["leverage_audit"]
    return """# The density interaction, block A2: the registered block (2026-11-07)

**Status: %(status)s**

**Every figure this block produces carries its arm, its scheme and its cap.** The arms are
`%(control)s` (%(control_rule)s) and `%(treated)s` (%(treated_rule)s); the schemes are
`%(primary)s` exposure and `%(sensitivity)s` exposure. A number quoted from this block
without its arm, its cap and its scheme is not a number from this block.

A2 replaces A1 (%(held_id)s), which a pre-run review placed on hold as %(held_verdict)s
(`%(held_review)s`). A1 is retained, frozen and unrun; its failure was that the dense end
of its ladder was saturated by arithmetic, not that its question was wrong.

## 1. Question and endpoint

%(question)s

The endpoint is **precision at a fixed cap**: the share of the budget spent on the world's
edges. %(cap_note)s

This is a selection measurement, not a behavioural one: it says nothing about prediction,
revision or retention.

## 2. Design

**The world.** %(world)s

**Densities.** %(densities)s — %(edges)s world edges at 16 tags.

**Exposure.** %(exposure)s

**The grid.** %(cells)d judged cells and %(sensitivity_cells)d exposure-check cells over
seeds **%(low)d–%(high)d**, bootstrap **%(bootstrap)d**. %(arith)s

Freshness: %(freshness)s

## 3. The criterion, the bar and the gates

**The estimand.** %(estimand)s

**The bar is %(bar).2f.** %(bar_provenance)s

**C1 is the judged criterion.** %(c1)s

**The interaction is not a criterion.** %(c2)s

**Judged whole.** %(judged_whole)s

**The exposure check.** %(exposure_rule)s

%(gates)s

**Void rule.** %(void)s

## 4. Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
%(table)s

## 5. What is reported

Delta(rho) per seed, per scheme and per cap, with its paired interval; both arms'
precision and coverage at every density; the pool's intra-cell share and `rho_rank` at every
cell; and the recovery curve at the caps %(recovery_caps)s as a characterization, never as a
criterion and never as the rank of the first edge. The interaction is reported with its
interval and its per-seed values, and the decision table places it, but it is not scored.

## 6. The pilot: calibration on unregistered seeds

The bar and the seed count rest on a pilot that this block does not judge.
%(pilot_why)s

%(pilot_rows)s

%(pinned)s

%(power)s

The designed pools, which are the world's own construction with no engine, show the shape
the registration assumes: the intra-cell share falls (%(share_falls)s), the control's own
precision rises (%(control_rises)s) — the design record's mechanical prediction — and the
treatment's advantage rises with density (%(delta_rises)s) on the **designed** pools:

%(audit_rows)s

Those are properties of the world, not of the engine, and they are not scored. They
establish only that the registered direction is representable by this instrument.

## 7. Analysis and runner

`%(command)s`

The analysis path is `%(path)s`, frozen with this registration. It reads only the cells the
runner writes, validates the grid, and imports nothing from the engine. The runner is
`%(runner)s`; it can be sliced (`--scheme`, `--seeds`) and appended (`--append`), and it
refuses to overwrite a cell inside one block. A1's registration is held, and the runner
refuses it by name.

## 8. Allocation

%(seeds)d world seeds, %(bootstrap_seeds)d bootstrap seed, %(judged)d judged cells,
%(sensitivity_cells_alloc)d exposure-check cells, %(recovery)d recovery caps,
%(thresholds)d thresholds, %(bars)d bars. %(note)s

No arm may run before this file is committed.
""" % {
        "status": body["status"],
        "control": body["arms"]["control"]["name"],
        "control_rule": body["arms"]["control"]["rule"],
        "treated": body["arms"]["intra_cell_excluded"]["name"],
        "treated_rule": body["arms"]["intra_cell_excluded"]["rule"],
        "primary": "fixed-total", "sensitivity": "fixed-per-edge",
        "held_id": body["held_predecessor"]["prereg"],
        "held_verdict": body["held_predecessor"]["verdict"],
        "held_review": body["held_predecessor"]["review"],
        "question": body["question"],
        "cap_note": d["cap_note"],
        "world": d["world"],
        "densities": ", ".join("%.1f" % rho for rho in d["densities"]),
        "edges": ", ".join(str(row["world_edges"]) for row in audit["rows"]),
        "exposure": d["exposure"],
        "cells": d["cells"],
        "sensitivity_cells": d["sensitivity_cells"],
        "low": low, "high": high, "bootstrap": s["bootstrap"],
        "arith": d["cells_arithmetic"],
        "freshness": s["freshness"],
        "estimand": c["estimand"],
        "bar": float(c["sparse_bar"]),
        "bar_provenance": c["bar_provenance"],
        "c1": c["C1"], "c2": c["C2"],
        "judged_whole": c["judged_whole"],
        "exposure_rule": c["exposure_rule"],
        "gates": gates, "void": body["gates"]["void_rule"],
        "table": table,
        "recovery_caps": ", ".join(str(cap) for cap in d["recovery_caps"]),
        "pilot_why": pilot["why"],
        "pilot_rows": _pilot_rows(pilot),
        "pinned": pilot["dense_end_is_pinned"],
        "power": pilot["power"],
        "share_falls": "yes" if audit["share_falls"] else "no",
        "control_rises": "yes" if audit["control_rises"] else "no",
        "delta_rises": "yes" if audit["delta_rises"] else "no",
        "audit_rows": _audit_rows(audit),
        "command": body["analysis"]["command"],
        "path": body["analysis"]["path"],
        "runner": body["analysis"]["runner"],
        "seeds": body["allocation"]["seeds"],
        "bootstrap_seeds": body["allocation"]["bootstrap_seeds"],
        "judged": body["allocation"]["judged_cells"],
        "sensitivity_cells_alloc": body["allocation"]["sensitivity_cells"],
        "recovery": body["allocation"]["recovery_caps"],
        "thresholds": body["allocation"]["thresholds"],
        "bars": body["allocation"]["bars"],
        "note": body["allocation"]["note"],
    }


def render_result(result: dict) -> str:
    """Section 9 is post-freeze: every number is read from the result artifact."""
    crit, gates = result["criteria"], result["gates"]
    c1, slope = crit["C1_sparse_level"], crit["descriptive_interaction"]
    failed = sorted(key for key, value in gates.items()
                    if isinstance(value, dict) and value.get("passed") is False)
    rows = "\n".join(
        "| %s | %+.6f | %+.6f | %+.6f |"
        % (rho, row["primary"]["delta_precision_mean"],
           row["sensitivity"]["delta_precision_mean"],
           row["primary"]["delta_precision_mean"]
           - row["sensitivity"]["delta_precision_mean"])
        for rho, row in crit["profile"].items())
    return """
## 9. Result (post-freeze)

**%(verdict)s.** %(reading)s

- **Cells:** %(cells)d; gates %(gates)s.
- **C1, the sparse-end level:** mean %(mean)+.6f, 95 percent interval
  [%(lo)+.6f, %(hi)+.6f], width %(width).6f, bar %(bar).2f, %(pos)d of %(of)d seeds
  positive — %(state)s.
- **The interaction (descriptive, not judged):** mean %(imean)+.6f, interval
  [%(ilo)+.6f, %(ihi)+.6f].
- **Exposure check:** sensitivity-scheme sparse mean %(exp)+.6f, %(exppos)d of %(expof)d
  seeds positive — %(expstate)s.

| rho_world | Delta precision, primary | Delta precision, sensitivity | primary − sensitivity |
| --- | --- | --- | --- |
%(rows)s

Sections 1–8 are exactly as committed before the run. Cells are in
`docs/density_interaction_a2_run.json`; the verdict is the frozen scorer's output in
`docs/density_interaction_a2_result.json`.
""" % {
        "verdict": result["decision"]["verdict"],
        "reading": result["decision"]["reading"],
        "cells": result["cells"],
        "gates": "all passed" if gates["all_passed"] else "failed: " + ", ".join(failed),
        "mean": c1["mean"], "lo": c1["interval"][0], "hi": c1["interval"][1],
        "width": c1["interval_width"], "bar": c1["bar"],
        "pos": c1["seeds_positive"], "of": c1["of"],
        "state": "passed" if c1["passed"] else "failed",
        "imean": slope["mean"], "ilo": slope["interval"][0], "ihi": slope["interval"][1],
        "exp": crit["exposure"]["sensitivity_sparse_mean"],
        "exppos": crit["exposure"]["seeds_positive"],
        "expof": crit["exposure"]["of"],
        "expstate": "holds" if crit["exposure"]["holds"] else "does not hold",
        "rows": rows,
    }


def render_document(body: dict, result: dict | None = None) -> str:
    """Sections 1-8 from the artifact, then the banner and section 9 from the result."""
    text = render(body)
    if result is not None:
        banner = ("**This block has run: the frozen analysis path returned %s.** Section 9 "
                  "records the result, and sections 1–8 are preserved exactly as committed "
                  "before the run." % result["decision"]["verdict"])
        head, rest = text.split("\n\n", 1)
        text = head + "\n\n" + banner + "\n\n" + rest + "\n" + render_result(result)
    return text


def main() -> int:
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    result = (json.loads(RESULT.read_text(encoding="utf-8"))
              if body.get("run") and RESULT.exists() else None)
    text = render_document(body, result)
    assert "{" not in text.replace("{%", ""), "a placeholder survived the render"
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), "lines:", len(text.splitlines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
