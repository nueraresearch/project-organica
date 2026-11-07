"""Render the two-arm registration document from its artifact."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "admission_two_arm_prereg.json"
OUT = ROOT / "docs" / "ADMISSION-TWO-ARM-PREREGISTRATION.md"


def render(body: dict) -> str:
    d, s, c = body["design"], body["seeds"], body["criteria"]
    low, high = s["block"]
    table = "\n".join("| %s | **%s** | %s |" % (r["condition"], r["verdict"], r["reading"])
                      for r in body["decision_table"])
    gates = "\n".join("* **%s** — %s" % (k, v) for k, v in body["gates"]["rules"].items())
    return """# The adopted admission rule against the reference engine (2026-11-07)

**Status: FROZEN, NOT RUN (ready; no cell).** No arm has run on this registration. The bar, the
guard, the seeds, the endpoint and the decision table were committed before the first cell.

**Every figure this block produces carries its arm.** The arms are `%(ref)s` (%(ref_rule)s) and
`%(adp)s` (%(adp_rule)s). A number quoted from this block without its arm is not a number from
this block.

## 1. Question and endpoint

%(question)s

The endpoint is `%(endpoint)s`. It is coverage, not behaviour: it counts which world edges the
arm's asserted structure contains, and says nothing about prediction, revision or retention.

## 2. Design

%(cycles)d cycles of the Gate 13 compositional world, identical for both arms of a seed; the only
difference is the service class. %(cells)d cells — %(arith)s. Seeds **%(low)d–%(high)d**,
bootstrap **%(bootstrap)d**: %(freshness)s

## 3. The bar and the guard

**Gain bar %(bar).2f.** %(bar_provenance)s

**Precision guard %(guard).2f.** %(guard_provenance)s

The gain is a conjunction judged whole: the mean paired coverage difference at or above the bar,
its %(level)d%% interval's lower bound above zero, and at least %(required)d of %(of)d seeds with
a positive difference. The guard can only prevent a gain being claimed.

## 4. Decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
%(table)s

## 5. Gates

%(gates)s

**Void rule.** %(void)s

## 6. Analysis

`%(command)s`

The analysis path is `%(path)s`, frozen with this registration. It reads only the cells the
runner writes, validates the grid, and imports nothing from the engine. The runner is `%(runner)s`.

## 7. Allocation

%(seeds)d world seeds, %(bootstrap_seeds)d bootstrap seed, %(cells)d cells, %(thresholds)d
thresholds, %(bars)d bars. %(note)s

No arm may run before this file is committed.
""" % {
        "ref": body["arms"]["reference"]["service"],
        "ref_rule": body["arms"]["reference"]["rule"],
        "adp": body["arms"]["adopted"]["service"],
        "adp_rule": body["arms"]["adopted"]["rule"],
        "question": body["question"], "endpoint": d["endpoint"], "cycles": d["cycles"],
        "cells": d["cells"], "arith": d["cells_arithmetic"],
        "low": low, "high": high, "bootstrap": s["bootstrap"], "freshness": s["freshness"],
        "bar": c["bar"], "bar_provenance": c["bar_provenance"],
        "guard": c["guard_bar"], "guard_provenance": c["guard_provenance"],
        "level": int(round(c["interval"] * 100)),
        "required": c["sign_test"]["required"], "of": c["sign_test"]["of"],
        "table": table, "gates": gates, "void": body["gates"]["void_rule"],
        "command": body["analysis"]["command"], "path": body["analysis"]["path"],
        "runner": body["analysis"]["runner"],
        "seeds": body["allocation"]["seeds"],
        "bootstrap_seeds": body["allocation"]["bootstrap_seeds"],
        "thresholds": body["allocation"]["thresholds"],
        "bars": body["allocation"]["bars"], "note": body["allocation"]["note"],
    }


def main() -> int:
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    text = render(body)
    assert "{" not in text.replace("{%", ""), "a placeholder survived the render"
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), "lines:", len(text.splitlines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
