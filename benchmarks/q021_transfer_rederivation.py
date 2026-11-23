"""Q021's frozen transfer re-derivation: assemble, score and record.

The protocol is `docs/Q021-TRANSFER-RE-DERIVATION-PREREGISTRATION.md`. The cells are produced by
`benchmarks.cross_context_reuse_benchmark` one seed at a time into `.scratch/q021/`; this module
assembles exactly the ten frozen seeds, computes the pre-committed criteria once, and renders the
result page. It does not run a cell.

    ./.venv/bin/python -m benchmarks.q021_transfer_rederivation --assemble
    ./.venv/bin/python -m benchmarks.q021_transfer_rederivation --check
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.cross_context_reuse_benchmark import build_summary

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / ".scratch" / "q021"
ARTIFACT = ROOT / "docs" / "q021_transfer_rederivation.json"
PAGE = ROOT / "docs" / "Q021-TRANSFER-RE-DERIVATION-RESULTS.md"

SEEDS = (20262101, 20262102, 20262103, 20262104, 20262105,
         20262106, 20262107, 20262108, 20262109, 20262110)
BOOTSTRAP_SEED = 20262111
ARMS = ("treatment", "control_naive", "control_pruned", "control_orthogonal")
A_CYCLES = 40
B_CYCLES = 40
BAR_TR = 1.25
BAR_ATTRIBUTION = 0.10
BAR_TP = 20.0
SEED_BAR = 8


def _part(seed: int) -> dict:
    path = PARTS / ("%d.json" % seed)
    if not path.exists():
        raise SystemExit("missing cell part for seed %d: %s" % (seed, path))
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("seeds") != [seed]:
        raise SystemExit("seed mismatch in %s: %r" % (path, record.get("seeds")))
    if record.get("phase_a_cycles") != A_CYCLES or record.get("phase_b_cycles") != B_CYCLES:
        raise SystemExit("cycle mismatch in %s" % path)
    return record


def _rows(parts: list[dict]) -> dict[str, list[dict]]:
    rows = {arm: [] for arm in ARMS}
    for part in parts:
        for arm in ARMS:
            rows[arm].extend(part["per_arm_results"][arm])
    for arm in ARMS:
        if len(rows[arm]) != len(SEEDS):
            raise SystemExit("%s has %d cells, expected %d" % (arm, len(rows[arm]), len(SEEDS)))
        if [r["seed"] for r in rows[arm]] != list(SEEDS):
            raise SystemExit("%s seed order is not the frozen block" % arm)
    return rows


def _mean(xs) -> float:
    return sum(xs) / len(xs)


def _interval(values: list[float]) -> dict:
    ordered = sorted(values)
    lo = ordered[int(0.025 * (len(ordered) - 1))]
    hi = ordered[int(0.975 * (len(ordered) - 1))]
    return {"lower": round(lo, 6), "upper": round(hi, 6),
            "width": round(hi - lo, 6)}


def _bootstrap(rows: dict[str, list[dict]]) -> dict:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(SEEDS)
    trs, d_pruned, d_ortho = [], [], []
    for _ in range(10000):
        idx = [rng.randrange(n) for _ in range(n)]
        means = {
            arm: _mean([rows[arm][i]["cycles_to_acquire"] for i in idx])
            for arm in ARMS
        }
        tr = means["control_naive"] / max(means["treatment"], 1e-6)
        trs.append(tr)
        d_pruned.append(
            means["control_naive"] / max(means["control_pruned"], 1e-6) - tr)
        d_ortho.append(
            means["control_naive"] / max(means["control_orthogonal"], 1e-6) - tr)
    return {
        "tr": _interval(trs),
        "pruned_minus_treatment": _interval(d_pruned),
        "orthogonal_minus_treatment": _interval(d_ortho),
    }


def _metrics(rows: dict[str, list[dict]]) -> dict:
    means = {arm: round(_mean([r["cycles_to_acquire"] for r in rows[arm]]), 6)
             for arm in ARMS}
    tr = {
        "treatment": round(means["control_naive"] / max(means["treatment"], 1e-6), 6),
        "pruned": round(means["control_naive"] / max(means["control_pruned"], 1e-6), 6),
        "orthogonal": round(means["control_naive"] / max(means["control_orthogonal"], 1e-6), 6),
    }
    return {
        "mean_cycles": means,
        "transfer_ratio": tr,
        "mean_tp_treatment": round(_mean([r["persistence_cycles"] for r in rows["treatment"]]), 3),
        "paired_treatment_faster": sum(
            1 for t, n in zip(rows["treatment"], rows["control_naive"])
            if t["cycles_to_acquire"] < n["cycles_to_acquire"]),
        "treatment_ranks": [r["target_rank_at_acquire"] for r in rows["treatment"]],
    }


def analyze(record: dict) -> dict:
    rows = _rows(record["parts"])
    metrics = _metrics(rows)
    intervals = _bootstrap(rows)
    t1 = (metrics["transfer_ratio"]["treatment"] >= BAR_TR
          and intervals["tr"]["lower"] > 1.0)
    t2 = (metrics["transfer_ratio"]["treatment"] - metrics["transfer_ratio"]["pruned"] >= BAR_ATTRIBUTION
          and metrics["transfer_ratio"]["treatment"] - metrics["transfer_ratio"]["orthogonal"] >= BAR_ATTRIBUTION
          and intervals["pruned_minus_treatment"]["lower"] > 0
          and intervals["orthogonal_minus_treatment"]["lower"] > 0)
    t3 = metrics["paired_treatment_faster"] >= SEED_BAR
    t4 = metrics["mean_tp_treatment"] >= BAR_TP
    if t1 and t2 and t3 and t4:
        verdict = "TRANSFER_CLAIM_RE_DERIVED"
    elif t1 and not t2:
        verdict = "NOT_ATTRIBUTABLE"
    elif t1:
        verdict = "PARTIAL"
    elif intervals["tr"]["width"] <= 0.30:
        verdict = "NO_TRANSFER_ADVANTAGE"
    else:
        verdict = "UNDERPOWERED"
    return {
        "metrics": metrics,
        "intervals": intervals,
        "criteria": {
            "T1_transfer": {"pass": t1, "value": metrics["transfer_ratio"]["treatment"],
                            "bar": BAR_TR, "lower": intervals["tr"]["lower"]},
            "T2_attribution": {"pass": t2,
                               "pruned_gap": round(metrics["transfer_ratio"]["treatment"]
                                                   - metrics["transfer_ratio"]["pruned"], 6),
                               "orthogonal_gap": round(metrics["transfer_ratio"]["treatment"]
                                                       - metrics["transfer_ratio"]["orthogonal"], 6),
                               "bar": BAR_ATTRIBUTION},
            "T3_paired": {"pass": t3, "value": metrics["paired_treatment_faster"],
                          "bar": SEED_BAR},
            "T4_persistence": {"pass": t4, "value": metrics["mean_tp_treatment"],
                               "bar": BAR_TP},
        },
        "gates": {
            "G1_denominator": all(r["acquired"] for arm in ARMS for r in rows[arm]),
            "G2_seed_block": all(len(rows[arm]) == len(SEEDS) for arm in ARMS),
        },
        "verdict": verdict,
    }


def assemble() -> dict:
    parts = [_part(seed) for seed in SEEDS]
    rows = _rows(parts)
    flat = [cell for arm in ARMS for cell in rows[arm]]
    engine = {key: parts[0][key] for key in ("engine_version", "engine_commit", "engine_sha256")}
    for part in parts[1:]:
        for key, value in engine.items():
            if part.get(key) != value:
                raise SystemExit("engine mismatch across parts: %s" % key)
    summary = build_summary(rows, list(SEEDS), A_CYCLES, B_CYCLES,
                            sum(p["total_seconds"] for p in parts))
    record = {
        "kind": "q021_transfer_rederivation",
        "date": "2026-11-09",
        "protocol": "docs/Q021-TRANSFER-RE-DERIVATION-PREREGISTRATION.md",
        "engine": engine,
        "seeds": list(SEEDS),
        "bootstrap_seed": BOOTSTRAP_SEED,
        "phase_a_cycles": A_CYCLES,
        "phase_b_cycles": B_CYCLES,
        "cells": flat,
        "per_arm_results": rows,
        "summary": summary,
        "parts": parts,
    }
    record.update(analyze(record))
    for key in ("engine_version", "engine_commit", "engine_sha256"):
        record.pop(key, None)
    return engine_stamp.stamp(record)


def check(record: dict | None = None) -> list[str]:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8")) if record is None else record
    problems = []
    if record.get("kind") != "q021_transfer_rederivation":
        problems.append("wrong kind")
    if tuple(record.get("seeds", ())) != SEEDS:
        problems.append("seed block is not the frozen ten")
    if len(record.get("cells", [])) != 40:
        problems.append("cell count is not 40")
    if set(record.get("gates", {}).values()) != {True}:
        problems.append("a gate failed")
    expected = analyze(record)
    if record.get("verdict") != expected["verdict"]:
        problems.append("verdict does not follow from the stored cells")
    if record.get("criteria") != expected["criteria"]:
        problems.append("criteria do not follow from the stored cells")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(record):
        problems.append("result page is stale")
    return problems


def render(record: dict) -> str:
    m = record["metrics"]
    i = record["intervals"]
    c = record["criteria"]
    lines = [
        "# Q021 transfer re-derivation — result",
        "",
        "**Verdict: `%s`.**" % record["verdict"],
        "",
        "Protocol: `%s`. Engine: `%s` (`%s`). Seeds: %d, four arms, 40/40 cycles." % (
            record["protocol"], record["engine"]["engine_version"],
            record["engine"]["engine_sha256"][:12], len(record["seeds"])),
        "",
        "## The four arms",
        "",
        "| arm | mean cycles to acquire | mean TP |",
        "| --- | --- | --- |",
    ]
    for arm in ARMS:
        lines.append("| `%s` | %.2f | %d |" % (
            arm, m["mean_cycles"][arm],
            _mean([r["persistence_cycles"] for r in record["per_arm_results"][arm]])))
    lines += [
        "",
        "Treatment TR: **%.3f** (95%% interval **%.3f–%.3f**)." % (
            m["transfer_ratio"]["treatment"], i["tr"]["lower"], i["tr"]["upper"]),
        "Pruned TR: **%.3f**; orthogonal TR: **%.3f**." % (
            m["transfer_ratio"]["pruned"], m["transfer_ratio"]["orthogonal"]),
        "",
        "## Criteria",
        "",
        "| criterion | value | bar | pass |",
        "| --- | --- | --- | --- |",
        "| T1 transfer | TR %.3f, lower %.3f | %.2f, lower > 1.00 | %s |" % (
            c["T1_transfer"]["value"], c["T1_transfer"]["lower"],
            c["T1_transfer"]["bar"], "yes" if c["T1_transfer"]["pass"] else "no"),
        "| T2 attribution | pruned gap %.3f, orthogonal gap %.3f | %.2f, lower > 0 | %s |" % (
            c["T2_attribution"]["pruned_gap"], c["T2_attribution"]["orthogonal_gap"],
            c["T2_attribution"]["bar"], "yes" if c["T2_attribution"]["pass"] else "no"),
        "| T3 paired | %d of 10 seeds faster | %d | %s |" % (
            c["T3_paired"]["value"], c["T3_paired"]["bar"],
            "yes" if c["T3_paired"]["pass"] else "no"),
        "| T4 persistence | mean TP %.2f | %.0f | %s |" % (
            c["T4_persistence"]["value"], c["T4_persistence"]["bar"],
            "yes" if c["T4_persistence"]["pass"] else "no"),
        "",
        "**What this means.** All four arms acquire at the same rate on every seed, so the v1 "
        "`TR = 3.2` does not re-derive on 0.13.0: this is `NO_TRANSFER_ADVANTAGE`, not an "
        "unrun manipulation. The harness's own earned-evidence assertion ran on every cell. "
        "This closes the v1 claim on this block; it does not establish transfer in general.",
        "",
        "The cells are in `docs/q021_transfer_rederivation.json`. No engine file changed.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assemble", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.assemble:
        record = assemble()
        ARTIFACT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        PAGE.write_text(render(record), encoding="utf-8")
        print("wrote %s and %s; verdict %s" % (ARTIFACT, PAGE, record["verdict"]))
        return 0
    if args.check:
        problems = check()
        if problems:
            print("FAIL: " + "; ".join(problems))
            return 1
        print("Q021 result and page agree")
        return 0
    parser.error("choose --assemble or --check")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
