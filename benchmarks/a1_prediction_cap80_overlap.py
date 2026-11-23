"""Why do two larger-28 seeds fail joint C1 at prediction cap 80?

At loop cap 120 / prediction cap 80, all six larger-28 seeds clear the
marginal C1 ceiling, but only four clear the joint A∩K ceiling.  The two joint
failures are 20660102 (A 75, K 124, A∩K 56) and 20660103 (A 83, K 105,
A∩K 51).

This replay records every candidate edge's A and K membership and decomposes
the overlap into:

* A∩K — the joint C1 count;
* A\\K — predicted edges the loop/dream window did not carry;
* K\\A — carried edges the prediction window did not serve.

It then asks whether K coverage explains the two joint failures.  A seed can
fail jointly only through A\\K when A already clears 60; a seed with A<60
fails for an A reason.  The cap-80 A, K and A∩K counts must reproduce the
committed prediction-cap artifact exactly, or the build refuses.

No engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_prediction_cap80_overlap --write
    python -m benchmarks.a1_prediction_cap80_overlap --check
    python -m benchmarks.a1_prediction_cap80_overlap --self-test
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_prediction_cap112_decompose as decomp
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CAP_PATH = DOCS / "a1_prediction_cap_c1.json"
OUT_PATH = DOCS / "a1_prediction_cap80_overlap.json"
PAGE_PATH = DOCS / "A1-PREDICTION-CAP80-OVERLAP.md"
ID = "A1-PREDICTION-CAP80-OVERLAP-1"
DATE = "2026-11-14"
KIND = "a1_prediction_cap80_overlap"
STATUS = "DESCRIPTIVE — CAP-80 LARGER-28 OVERLAP DECOMPOSITION; NO TARGET, FREEZE, GRANT OR A1 CELL"
BLOCK = "larger-28"
SEEDS = (20660101, 20660102, 20660103, 20660104, 20660105, 20660106)
CAP = 80
C1_FLOOR = 60
SUPPORT_BINS = ("0", "1", "2-3", "4-7", "8-15", "16+")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _control() -> dict[tuple[str, int], dict]:
    return {
        (row["block"], row["seed"]): row
        for row in _load(CAP_PATH)["rows"]
        if row["prediction_cap"] == CAP and row["block"] == BLOCK
    }


def _edge(row: dict) -> dict:
    return {
        "edge": row["edge"],
        "support": row["support"],
        "support_bin": row["support_bin"],
        "A_rank": row["A_rank"],
    }


def _counts(rows: list[dict], field: str, labels: tuple[str, ...]) -> list[dict]:
    total = Counter(row[field] for row in rows)
    return [{"label": label, "edges": total.get(label, 0)} for label in labels]


def _seed_row(run: dict) -> dict:
    rows = run["rows"]
    a_rows = [row for row in rows if row["A"]]
    k_rows = [row for row in rows if row["K"]]
    a_edges = {row["edge"] for row in a_rows}
    k_edges = {row["edge"] for row in k_rows}
    a_only = a_edges - k_edges
    k_only = k_edges - a_edges
    joint = len(a_edges & k_edges)
    a = len(a_edges)
    k = len(k_edges)
    by_edge = {row["edge"]: row for row in rows}
    a_only_rows = [_edge(by_edge[edge]) for edge in sorted(a_only)]
    k_only_rows = [_edge(by_edge[edge]) for edge in sorted(k_only)]
    marginal_pass = a >= C1_FLOOR
    joint_pass = joint >= C1_FLOOR
    gap = C1_FLOOR - joint
    return {
        "block": BLOCK,
        "seed": run["seed"],
        "candidate_edges": len(rows),
        "A": a,
        "K": k,
        "A_and_K": joint,
        "A_only": len(a_only),
        "K_only": len(k_only),
        "K_coverage_of_A": round(joint / a, 6) if a else 0.0,
        "C1_marginal": a,
        "C1_joint": joint,
        "gap_to_60_marginal": C1_FLOOR - a,
        "gap_to_60_joint": gap,
        "C1_marginal_pass": marginal_pass,
        "C1_joint_pass": joint_pass,
        "A_needed_without_K": max(0, C1_FLOOR - a),
        "min_K_repair": max(0, gap),
        "K_volume_sufficient": k >= C1_FLOOR,
        "full_K_coverage_joint": a,
        "A_only_by_support": _counts(a_only_rows, "support_bin", SUPPORT_BINS),
        "K_only_by_support": _counts(k_only_rows, "support_bin", SUPPORT_BINS),
        "A_only_edges": a_only_rows,
        "K_only_edges": k_only_rows,
    }


def build() -> dict:
    tasks = [(BLOCK, seed, CAP) for seed in SEEDS]
    with ProcessPoolExecutor(max_workers=min(6, len(tasks))) as pool:
        raw = list(pool.map(decomp._replay, tasks))
    control = _control()
    for run in raw:
        expected = control[(BLOCK, run["seed"])]
        for field in ("A", "K", "A_and_K"):
            got = len({row["edge"] for row in run["rows"]
                       if row["A" if field != "K" else "K"]})
            if field == "A_and_K":
                got = len({row["edge"] for row in run["rows"] if row["A"]}
                          & {row["edge"] for row in run["rows"] if row["K"]})
            if got != expected[field]:
                raise SystemExit(
                    "REFUSED: control %s/%d %s %d, expected %d"
                    % (BLOCK, run["seed"], field, got, expected[field]))
    seed_rows = [_seed_row(run) for run in sorted(raw, key=lambda row: row["seed"])]
    failures = [row for row in seed_rows if not row["C1_joint_pass"]]
    passes = [row for row in seed_rows if row["C1_joint_pass"]]
    a_only_total = sum(row["A_only"] for row in seed_rows)
    k_only_total = sum(row["K_only"] for row in seed_rows)
    summary = {
        "seeds": len(seed_rows),
        "A_total": sum(row["A"] for row in seed_rows),
        "K_total": sum(row["K"] for row in seed_rows),
        "A_and_K_total": sum(row["A_and_K"] for row in seed_rows),
        "A_only_total": a_only_total,
        "K_only_total": k_only_total,
        "C1_marginal_pass": sum(row["C1_marginal_pass"] for row in seed_rows),
        "C1_joint_pass": len(passes),
        "joint_failures": [row["seed"] for row in failures],
        "joint_failure_A": [row["A"] for row in failures],
        "joint_failure_A_and_K": [row["A_and_K"] for row in failures],
        "joint_failure_A_only": [row["A_only"] for row in failures],
        "joint_failure_K_only": [row["K_only"] for row in failures],
        "joint_failure_min_K_repair": [row["min_K_repair"] for row in failures],
        "joint_failure_K_coverage": [row["K_coverage_of_A"] for row in failures],
        "pass_min_K_coverage": min(row["K_coverage_of_A"] for row in passes),
        "all_A_marginal": all(row["C1_marginal_pass"] for row in seed_rows),
        "all_joint_failures_A_marginal": all(
            row["C1_marginal_pass"] for row in failures),
        "A_only_by_support": _counts(
            [edge for row in seed_rows for edge in row["A_only_edges"]],
            "support_bin", SUPPORT_BINS),
        "K_only_by_support": _counts(
            [edge for row in seed_rows for edge in row["K_only_edges"]],
            "support_bin", SUPPORT_BINS),
    }
    if summary["all_joint_failures_A_marginal"] and failures:
        reading = (
            "All six larger-28 seeds clear A marginally (A %d-%d), so the two "
            "joint failures are not A shortages.  At cap 80, K covers %d/%d "
            "and %d/%d of the A edges on seeds %d and %d, leaving %d and %d "
            "A edges uncarried; only %d and %d of those need to be covered to "
            "reach 60.  K volume is not scarce (K %d and %d against A %d and "
            "%d), so the failure is selective K coverage: the joint ceiling "
            "loses %d and %d rows to A\\K."
            % (min(row["A"] for row in seed_rows),
               max(row["A"] for row in seed_rows),
               failures[0]["A_and_K"], failures[0]["A"],
               failures[1]["A_and_K"], failures[1]["A"],
               failures[0]["seed"], failures[1]["seed"],
               failures[0]["A_only"], failures[1]["A_only"],
               failures[0]["min_K_repair"], failures[1]["min_K_repair"],
               failures[0]["K"], failures[1]["K"],
               failures[0]["A"], failures[1]["A"],
               failures[0]["A_only"], failures[1]["A_only"]))
    elif failures:
        reading = (
            "%d larger-28 seeds fail joint C1 at cap 80; not all of them clear "
            "A marginally, so K coverage is not the sole explanation."
            % len(failures))
    else:
        reading = (
            "All larger-28 seeds clear joint C1 at cap 80; the overlap "
            "decomposition is descriptive only.")
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "At loop cap 120 / prediction cap 80, does K coverage explain the "
            "two larger-28 joint C1 failures?"
        ),
        "definition": (
            "Per-seed A, K, A∩K, A\\K and K\\A on the six larger-28 candidate "
            "streams at prediction cap 80, with C1 floor 60.  A\\K is the "
            "predicted-not-carried overlap loss; K\\A is the carried-not-"
            "predicted pool."
        ),
        "method": (
            "One no-arm replay per seed at cap 80.  A, K and A∩K must "
            "reproduce the committed prediction-cap rows exactly.  Every "
            "candidate edge's A and K membership is recorded so the overlap "
            "is decomposed by seed, family and support."
        ),
        "constants": {
            "block": BLOCK,
            "seeds": list(SEEDS),
            "prediction_cap": CAP,
            "loop_cap": decomp.LOOP_CAP,
            "c1_floor": C1_FLOOR,
        },
        "governance": {
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "summary": summary,
        "seed_rows": seed_rows,
        "not_evidence": (
            "A descriptive overlap decomposition on six no-arm larger-28 "
            "seeds at one cap pair.  It measures A\\K and K\\A availability; "
            "it is not a treatment, a K-repair result, target viability or a "
            "successor.  Full K coverage is a counterfactual, not an engine "
            "change."
        ),
    })


def render(doc: dict) -> str:
    s = doc["summary"]
    lines = [
        "# A1 larger-28 overlap at prediction cap 80",
        "",
        "Generated from `docs/a1_prediction_cap80_overlap.json` by "
        "`python -m benchmarks.a1_prediction_cap80_overlap --write`. Do not edit by hand.",
        "",
        "**Availability-only overlap decomposition, not an A1 result.** Six "
        "larger-28 seeds at loop cap **120** / prediction cap **80**. No "
        "target, freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "| Seeds | A | K | A∩K | A\\K | K\\A | Marginal pass | Joint pass |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        "| %d | %d | %d | %d | %d | %d | %d/6 | %d/6 |"
        % (s["seeds"], s["A_total"], s["K_total"], s["A_and_K_total"],
           s["A_only_total"], s["K_only_total"], s["C1_marginal_pass"],
           s["C1_joint_pass"]),
        "",
        "The joint count is `A∩K = A - |A\\K| = K - |K\\A|`. The two joint "
        "failures are **%s**, with A\\K **%s** and minimum K repair **%s**."
        % (", ".join(str(seed) for seed in s["joint_failures"]),
           ", ".join(str(value) for value in s["joint_failure_A_only"]),
           ", ".join(str(value) for value in s["joint_failure_min_K_repair"])),
        "",
        "## Per seed",
        "",
        "| Seed | A | K | A∩K | A\\K | K\\A | K coverage of A | Gap to 60 (joint) | Marginal | Joint |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in doc["seed_rows"]:
        lines.append(
            "| %d | %d | %d | %d | %d | %d | %.1f%% | %d | %s | %s |"
            % (row["seed"], row["A"], row["K"], row["A_and_K"],
               row["A_only"], row["K_only"], 100.0 * row["K_coverage_of_A"],
               row["gap_to_60_joint"],
               "yes" if row["C1_marginal_pass"] else "no",
               "yes" if row["C1_joint_pass"] else "no"))
    lines += [
        "",
        "## Failure test",
        "",
        "Both joint failures clear A marginally, so their deficit is entirely "
        "the overlap loss:",
        "",
        "| Seed | A | A∩K | A\\K | Need to reach 60 | K | K\\A | K coverage |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["seed_rows"]:
        if row["C1_joint_pass"]:
            continue
        lines.append(
            "| %d | %d | %d | %d | %d | %d | %d | %.1f%% |"
            % (row["seed"], row["A"], row["A_and_K"], row["A_only"],
               row["min_K_repair"], row["K"], row["K_only"],
               100.0 * row["K_coverage_of_A"]))
    lines += [
        "",
        "Both seeds have A≥60 and K≥60. K nevertheless misses %s A edges; "
        "recovering only %s of those would lift each joint ceiling to 60. "
        "The failures also have the two lowest K-coverage rates, while the "
        "four passing seeds have coverage at least %.1f%%."
        % (", ".join(str(value) for value in s["joint_failure_A_only"]),
           ", ".join(str(value) for value in s["joint_failure_min_K_repair"]),
           100.0 * s["pass_min_K_coverage"]),
        "",
        "K volume is therefore not the constraint: the failing seeds have "
        "K **%s** against A **%s**. The constraint is which A edges K covers."
        % (", ".join(str(value) for value in
                     [row["K"] for row in doc["seed_rows"]
                      if not row["C1_joint_pass"]]),
           ", ".join(str(value) for value in s["joint_failure_A"])),
        "",
        "## A\\K exact edges on the two failures",
        "",
        "| Seed | Edge | Support | A rank |",
        "| ---: | --- | ---: | ---: |",
    ]
    for row in doc["seed_rows"]:
        if row["C1_joint_pass"]:
            continue
        for edge in row["A_only_edges"]:
            lines.append("| %d | %s | %d | %s |" % (
                row["seed"], edge["edge"], edge["support"],
                edge["A_rank"] if edge["A_rank"] is not None else "-"))
    lines += [
        "",
        "## A\\K by support",
        "",
        "| Support | A\\K |",
        "| --- | ---: |",
    ]
    for row in s["A_only_by_support"]:
        lines.append("| %s | %d |" % (row["label"], row["edges"]))
    lines += [
        "",
        "## K\\A by support",
        "",
        "| Support | K\\A |",
        "| --- | ---: |",
    ]
    for row in s["K_only_by_support"]:
        lines.append("| %s | %d |" % (row["label"], row["edges"]))
    lines += [
        "",
        "## Reading",
        "",
        "Four seeds pass jointly because K covers enough of A, not because "
        "their A or K totals are larger. The two failures are not K-volume "
        "failures: both carry more K than A. They are selective-coverage "
        "failures, and full K coverage of A would make both pass because "
        "A alone is already 75 and 83.",
        "",
        "The K\\A pool is the alternative repair side: those edges are "
        "already carried, so serving them into A would also raise A∩K. This "
        "decomposition does not choose between repairing K coverage and "
        "serving the K\\A pool.",
        "",
        "## What this does not claim",
        "",
        doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def _row(a: int, k: int, both: int) -> dict:
    gap = C1_FLOOR - both
    return {
        "A": a, "K": k, "A_and_K": both, "A_only": a - both,
        "K_only": k - both, "C1_marginal": a, "C1_joint": both,
        "C1_marginal_pass": a >= C1_FLOOR,
        "C1_joint_pass": both >= C1_FLOOR,
        "gap_to_60_joint": gap, "min_K_repair": max(0, gap),
        "full_K_coverage_joint": a,
        "K_coverage_of_A": both / a if a else 0.0,
    }


def problems(doc: dict | None = None) -> list[str]:
    doc = _load(OUT_PATH) if doc is None else doc
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("artifact kind")
    if doc.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    if engine_stamp.missing(doc):
        found.append("the artifact is not fully stamped")
    if doc.get("governance") != {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none"}:
        found.append("governance changed")
    rows = doc.get("seed_rows") or []
    if len(rows) != len(SEEDS):
        found.append("%d seed rows, expected %d" % (len(rows), len(SEEDS)))
    for row in rows:
        if row.get("A_and_K") != row.get("A", 0) - row.get("A_only", -1):
            found.append("joint vs A\\K at seed %s" % row.get("seed"))
        if row.get("A_and_K") != row.get("K", 0) - row.get("K_only", -1):
            found.append("joint vs K\\A at seed %s" % row.get("seed"))
        if row.get("A_only") != len(row.get("A_only_edges") or []):
            found.append("A\\K edge list at seed %s" % row.get("seed"))
        if row.get("K_only") != len(row.get("K_only_edges") or []):
            found.append("K\\A edge list at seed %s" % row.get("seed"))
        if row.get("gap_to_60_joint") != C1_FLOOR - row.get("A_and_K", -1):
            found.append("joint gap at seed %s" % row.get("seed"))
        if row.get("C1_joint_pass") != (row.get("A_and_K", 0) >= C1_FLOOR):
            found.append("joint pass at seed %s" % row.get("seed"))
    if sum(row.get("A_only", 0) for row in rows) != (
            doc.get("summary") or {}).get("A_only_total"):
        found.append("A\\K total")
    if sum(row.get("K_only", 0) for row in rows) != (
            doc.get("summary") or {}).get("K_only_total"):
        found.append("K\\A total")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    row = _row(75, 124, 56)
    if row["C1_joint_pass"] or row["A_only"] != 19:
        failures.append("seed 20660102 must fail jointly with A\\K 19")
    if row["min_K_repair"] != 4:
        failures.append("seed 20660102 must need a 4-row K repair")
    row = _row(83, 105, 51)
    if row["C1_joint_pass"] or row["A_only"] != 32:
        failures.append("seed 20660103 must fail jointly with A\\K 32")
    if row["min_K_repair"] != 9:
        failures.append("seed 20660103 must need a 9-row K repair")
    row = _row(91, 121, 72)
    if not row["C1_joint_pass"] or row["A_only"] != 19:
        failures.append("a 72-row joint ceiling must pass with A\\K 19")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    for seed, a_only, repair in zip(
            body["summary"]["joint_failures"],
            body["summary"]["joint_failure_A_only"],
            body["summary"]["joint_failure_min_K_repair"]):
        print("joint failure %d: A\\K %d, min K repair %d"
              % (seed, a_only, repair))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no cap-80 overlap artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("cap-80 overlap: clean")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.self_test:
        found = self_test()
        if found:
            raise SystemExit("FAIL: " + "; ".join(found))
        print("cap-80 overlap self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
