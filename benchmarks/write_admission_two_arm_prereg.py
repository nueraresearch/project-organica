"""Render the two-arm registration document from its artifact."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "admission_two_arm_prereg.json"
OUT = ROOT / "docs" / "ADMISSION-TWO-ARM-PREREGISTRATION.md"
RESULT = ROOT / "docs" / "admission_two_arm_result.json"


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


def render_result(body: dict, result: dict) -> str:
    """§9 is post-freeze: every number is read from the result artifact."""
    a, g = result["criteria"]["adoption"], result["criteria"]["guard"]
    level = int(round(body["criteria"]["interval"] * 100))
    rows = "\n".join("| %s | %+.6f | %+.6f |" % (seed, v["coverage_gain"],
                                                  v["precision_difference"])
                     for seed, v in sorted(result["criteria"]["per_seed"].items()))
    failed = sorted(k for k, v in result["gates"].items()
                    if isinstance(v, dict) and v.get("passed") is False)
    return """## 9. Result (post-freeze)

**%(verdict)s.** %(reading)s

- **Cells:** %(cells)d, all gates %(gates)s.
- **Coverage gain, adopted minus reference:** mean %(mean)+.6f, %(level)d%% interval
  [%(lo)+.6f, %(hi)+.6f], width %(width).6f, bar %(bar).2f, %(positive)d of %(of)d seeds positive.
- **Precision guard:** mean %(gmean)+.6f against %(gbar)+.2f — %(guard_state)s.

| Seed | Coverage gain (adopted − reference) | Precision difference |
| --- | --- | --- |
%(rows)s

Every figure above is the paired difference between the two arms, and the arm order is fixed:
positive means the adopted arm covered more. Cells are in
`docs/admission_two_arm_run.json`; the decision is in `docs/admission_two_arm_result.json`.
The registration itself is unchanged: §1–§7 are exactly as committed before the run.
""" % {
        "verdict": result["decision"]["verdict"],
        "reading": result["decision"]["reading"][:1].upper()
                   + result["decision"]["reading"][1:],
        "cells": result["cells"],
        "gates": "passed" if result["gates"]["all_passed"] else "failed: " + ", ".join(failed),
        "mean": a["mean_paired_gain"], "level": level,
        "lo": a["interval"][0], "hi": a["interval"][1], "width": a["interval_width"],
        "bar": a["bar"], "positive": a["seeds_positive"], "of": body["criteria"]["sign_test"]["of"],
        "gmean": g["mean_paired_precision_difference"], "gbar": g["bar"],
        "guard_state": "passed" if g["passed"] else "failed", "rows": rows,
    }


def render_withdrawal(body: dict) -> str:
    """§10 is post-freeze: the withdrawal is recorded beside the result, never over it."""
    w = body["withdrawn"]
    removed = "\n".join("- `%s`" % path for path in w["removed"])
    return """## 10. Withdrawal (post-freeze)

**%(decision)s on %(date)s.** The adoption this block was registered to test was removed the day
the result was read: %(reference)s.

**Removed from the package:**

%(removed)s

**Why the code and not only the record.** A rule its own measurement closed is not a policy an
engine version should carry, and a non-default arm that no document may present as a gain is a
liability that still has to be maintained. Deleting it is the version of this negative result the
code agrees with. §9 and the decision table above are unchanged: the result, the bar and the guard
keep their numbers, and the confirmatory block's verdict keeps its own instrument.

**Reproducibility.** The adopted arm was last present at commit **%(commit)s**. Checking that
commit out reproduces this block end to end; `benchmarks/run_admission_two_arm.py` resolves its
arms lazily and stops with that commit's name rather than raising an `ImportError`.

**Not a wider finding.** %(note)s.
""" % {"decision": w["decision"], "date": w["date"], "reference": w["reference"],
       "removed": removed, "commit": w["reproducible_from"],
       "note": w["note"][:1].upper() + w["note"][1:]}


def main() -> int:
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    text = render(body)
    assert "{" not in text.replace("{%", ""), "a placeholder survived the render"
    if body.get("run") and RESULT.exists():
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        banner = ("**This block has run: the frozen analysis path returned %s.** §9 records the "
                  "result%s, and §1–§7 are preserved exactly as committed before the run."
                  % (result["decision"]["verdict"],
                     " and §10 the withdrawal" if body.get("withdrawn") else ""))
        head, rest = text.split("\n\n", 1)
        text = head + "\n\n" + banner + "\n\n" + rest + "\n" + render_result(body, result)
        if body.get("withdrawn"):
            text += "\n" + render_withdrawal(body)
    assert "{" not in text.replace("{%", ""), "a placeholder survived the render"
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), "lines:", len(text.splitlines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
