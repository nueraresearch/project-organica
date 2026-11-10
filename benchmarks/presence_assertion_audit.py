"""Same-build construct audit: presence versus assertion at the 40-slot cap.

This is a measurement-only audit. It runs the existing Gate-13 instrument on the
shipped engine and records two quantities from the same acquisition runs:

* presence: world edges in raw temporal memory, before the prediction cap;
* assertion: world edges in the final asserted structure, with the engine's
  Layer-1 prediction budget at ``MAX_PREDICTIONS = 40``.

The final asserted structure aggregates all six structure types, so its total
size is not bounded by 40. The cap is the Layer-1 admission budget; the audit
records that distinction instead of treating "asserted" as "at most 40 rows".

No engine file is edited and no live database is touched.

    ./.venv/bin/python -m benchmarks.presence_assertion_audit --run
    ./.venv/bin/python -m benchmarks.presence_assertion_audit --check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                      # noqa: E402
from benchmarks.acquisition_harness import gate_acquisition_sufficiency, SHORT_CYCLES  # noqa: E402
from organica.sleep import SleepService                                  # noqa: E402

SEEDS = (20261100, 20261101, 20261102, 20261103, 20261104, 20261105)
CAP = 40
CYCLES = SHORT_CYCLES
ARTIFACT = ROOT / "docs" / "presence_assertion_audit_0.14.0.json"
PAGE = ROOT / "docs" / "PRESENCE-ASSERTION-AUDIT-0.14.0.md"
PRIOR = ROOT / "docs" / "temporal_presence_0.13.0.json"
KIND = "presence_assertion_construct_audit"


def _range(values: list[float]) -> list[float]:
    return [round(min(values), 6), round(max(values), 6)]


def _verdict(rows: list[dict]) -> str:
    if any(row["present_world_edges"] != row["world_edges"] for row in rows):
        return "PRESENCE NOT FULL"
    if all(row["asserted_world_edges"] < row["present_world_edges"] for row in rows):
        return "PRESENCE NOT ASSERTION"
    return "PRESENCE AND ASSERTION COINCIDE"


def _summarize(rows: list[dict]) -> dict:
    world_edges = {row["world_edges"] for row in rows}
    presence = [row["presence_rate"] for row in rows]
    assertion = [row["assertion_rate"] for row in rows]
    conversions = [row["conversion"] for row in rows if row["conversion"] is not None]
    gaps = [row["present_not_asserted"] for row in rows]
    asserted_sizes = [row["final_asserted_edges"] for row in rows]
    return {
        "seeds": len(rows),
        "world_edges": sorted(world_edges),
        "presence_rate_range": _range(presence),
        "assertion_rate_range": _range(assertion),
        "conversion_range": _range(conversions),
        "present_not_asserted_range": [min(gaps), max(gaps)],
        "final_asserted_edges_range": [min(asserted_sizes), max(asserted_sizes)],
        "all_presence_full": all(rate == 1.0 for rate in presence),
        "all_assertion_below_presence": all(
            row["asserted_world_edges"] < row["present_world_edges"] for row in rows),
        "layer1_cap": CAP,
    }


def build() -> dict:
    if SleepService.MAX_PREDICTIONS != CAP:
        raise SystemExit(
            "the shipped Layer-1 cap is %d, not the audited %d"
            % (SleepService.MAX_PREDICTIONS, CAP))
    rows = []
    for seed in SEEDS:
        result = gate_acquisition_sufficiency(seed=seed, cycles=CYCLES)
        present = result["covered_temporal_edges"]
        asserted = result["covered_asserted_edges"]
        rows.append({
            "seed": seed,
            "world_edges": result["world_edges"],
            "present_world_edges": present,
            "presence_rate": result["raw_temporal_coverage"],
            "asserted_world_edges": asserted,
            "assertion_rate": result["asserted_coverage"],
            "conversion": round(asserted / present, 6) if present else None,
            "present_not_asserted": present - asserted,
            "final_asserted_edges": result["asserted_edges"],
            "asserted_fingerprint": result["asserted_fingerprint"],
        })

    prior = None
    if PRIOR.exists():
        old = json.loads(PRIOR.read_text(encoding="utf-8"))
        prior = {
            "artifact": "docs/temporal_presence_0.13.0.json",
            "build": old.get("engine_version"),
            "presence_range": (old.get("summary") or {}).get("temporal_presence_min"),
            "assertion_range": (old.get("summary") or {}).get("asserted_coverage_range"),
            "note": ("descriptive prior only; the same-build audit does not re-score "
                     "or pool the 0.13.0 rows"),
        }

    body = {
        "kind": KIND,
        "date": "2026-11-10",
        "what": "same-build construct audit of raw temporal presence versus final asserted coverage",
        "question": ("On one build, with the shipped 40-slot Layer-1 prediction cap, "
                     "how many of the world's edges are present in raw temporal memory, "
                     "and how many survive into the final asserted structure?"),
        "method": (
            "gate_acquisition_sufficiency on the Gate-13 compositional world, six "
            "historical seeds, cycles=%d (warmup + acquisition), max_predictions=None "
            "so SleepService.MAX_PREDICTIONS=40 is used unchanged. Presence is measured "
            "from database temporal edges before the cap; assertion is measured from the "
            "final structure after the acquisition loop." % CYCLES
        ),
        "cap_scope": (
            "The 40-slot cap is the Layer-1 prediction admission budget. presence is "
            "measured before that budget is applied. The final asserted structure "
            "aggregates all six structure types, so final_asserted_edges is not capped "
            "at 40 and must not be read as the number of prediction slots."
        ),
        "same_build": {
            "version": engine_stamp.engine_version(),
            "sha256": engine_stamp.engine_sha256(),
            "layer1_cap": CAP,
            "cap_source": "organica.sleep.SleepService.MAX_PREDICTIONS",
        },
        "rows": rows,
        "summary": _summarize(rows),
        "prior_reference": prior,
        "verdict": _verdict(rows),
        "reading": (
            "The two quantities answer different questions. Presence is availability in "
            "the temporal substrate; assertion is survival in the final structure. A "
            "presence rate near 1.0 with a lower assertion rate is a construct separation, "
            "not by itself a defect or a causal claim about selection."
        ),
        "not_evidence": (
            "This audit does not identify which stage loses a present edge, does not "
            "manipulate the cap, and does not authorize an engine change. It is a "
            "same-build construct check, not a mechanism experiment."
        ),
    }
    return engine_stamp.stamp(body)


def render_page(art: dict) -> str:
    summary = art["summary"]
    lines = [
        "# Presence vs assertion at the 40-slot cap — same-build audit",
        "",
        "Generated from `docs/presence_assertion_audit_0.14.0.json` by "
        "`python -m benchmarks.presence_assertion_audit --run`. Do not edit by hand.",
        "",
        "**Build:** `%s`, `%s`; Layer-1 cap **%d**."
        % (art["same_build"]["version"], art["same_build"]["sha256"][:16],
           art["same_build"]["layer1_cap"]),
        "",
        "**Verdict: `%s`.**" % art["verdict"],
        "",
        "## What was measured",
        "",
        art["question"],
        "",
        art["method"],
        "",
        "**Cap scope.** %s" % art["cap_scope"],
        "",
        "## Per-seed audit",
        "",
        "| Seed | World edges | Present | Presence rate | Asserted world edges | Assertion rate | Conversion | Present, not asserted | Final asserted structures |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in art["rows"]:
        lines.append(
            "| %d | %d | %d | %.4f | %d | %.4f | %.4f | %d | %d |"
            % (row["seed"], row["world_edges"], row["present_world_edges"],
               row["presence_rate"], row["asserted_world_edges"],
               row["assertion_rate"], row["conversion"], row["present_not_asserted"],
               row["final_asserted_edges"]))
    lines += [
        "",
        "## Summary",
        "",
        "| Quantity | Result |",
        "| --- | --- |",
        "| Seeds | %d |" % summary["seeds"],
        "| World edges | %s |" % ", ".join(str(x) for x in summary["world_edges"]),
        "| Presence rate | %.4f–%.4f |" % tuple(summary["presence_rate_range"]),
        "| Assertion rate | %.4f–%.4f |" % tuple(summary["assertion_rate_range"]),
        "| Presence → assertion conversion | %.4f–%.4f |" % tuple(summary["conversion_range"]),
        "| Present but not asserted | %d–%d edges |" % tuple(summary["present_not_asserted_range"]),
        "| Final asserted structures (all types) | %d–%d |"
        % tuple(summary["final_asserted_edges_range"]),
        "",
        "## Reading",
        "",
        art["reading"],
        "",
        "## What this does not establish",
        "",
        art["not_evidence"],
        "",
    ]
    if art.get("prior_reference"):
        prior = art["prior_reference"]
        lines += [
            "## Prior reference (not pooled)",
            "",
            "`%s`, build `%s`: presence %s, asserted coverage %s. %s"
            % (prior["artifact"], prior["build"], prior["presence_range"],
               prior["assertion_range"], prior["note"]),
            "",
        ]
    lines += [
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.presence_assertion_audit --run",
        "python -m benchmarks.presence_assertion_audit --check",
        "```",
        "",
    ]
    return "\n".join(lines)


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no audit artifact; run --run")
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    problems = []
    if art.get("kind") != KIND:
        problems.append("artifact kind")
    if SleepService.MAX_PREDICTIONS != CAP:
        problems.append("shipped cap is not %d" % CAP)
    if art.get("same_build", {}).get("sha256") != engine_stamp.engine_sha256():
        problems.append("artifact build does not match the shipped engine")
    if engine_stamp.missing(art):
        problems.append("artifact is not fully stamped: %r" % engine_stamp.missing(art))
    rows = art.get("rows") or []
    if len(rows) != len(SEEDS) or {row.get("seed") for row in rows} != set(SEEDS):
        problems.append("artifact does not contain the frozen six-seed block")
    for row in rows:
        world = row.get("world_edges", 0)
        present = row.get("present_world_edges", 0)
        asserted = row.get("asserted_world_edges", 0)
        if world != 112:
            problems.append("seed %s has the wrong world-edge denominator" % row.get("seed"))
        if not 0 <= present <= world or not 0 <= asserted <= present:
            problems.append("seed %s has an impossible presence/assertion count" % row.get("seed"))
            continue
        if row.get("presence_rate") != round(present / world, 6):
            problems.append("seed %s presence rate is not derived" % row.get("seed"))
        if row.get("assertion_rate") != round(asserted / world, 6):
            problems.append("seed %s assertion rate is not derived" % row.get("seed"))
        if present and row.get("conversion") != round(asserted / present, 6):
            problems.append("seed %s conversion is not derived" % row.get("seed"))
        if row.get("present_not_asserted") != present - asserted:
            problems.append("seed %s gap is not derived" % row.get("seed"))
        if row.get("final_asserted_edges", 0) < asserted:
            problems.append("seed %s final structure is smaller than its world-edge assertion"
                            % row.get("seed"))
    if art.get("summary") != _summarize(rows):
        problems.append("summary is not derived from the rows")
    if art.get("verdict") != _verdict(rows):
        problems.append("verdict is not derived from the rows")
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render_page(art):
        problems.append("audit page is stale")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("presence/assertion audit %s: %s"
          % (art["same_build"]["version"], art["verdict"]))
    return 0


def run() -> int:
    art = build()
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render_page(art), encoding="utf-8")
    print("wrote %s and %s" % (ARTIFACT.relative_to(ROOT), PAGE.relative_to(ROOT)))
    print(json.dumps(art["summary"], indent=1))
    print("verdict:", art["verdict"])
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", action="store_true", help="run the six-seed audit and write the artifact")
    group.add_argument("--check", action="store_true", help="verify the artifact and page")
    args = parser.parse_args(argv)
    return run() if args.run else check()


if __name__ == "__main__":
    raise SystemExit(main())
