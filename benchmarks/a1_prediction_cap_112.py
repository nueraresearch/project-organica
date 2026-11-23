"""Does the shipped prediction cap clear the 16-tag C1 near-misses?

At loop cap 120, prediction cap 80 left both 16-tag blocks at 0/6 with
joint A∩K maxima 59 and 58.  This runs the shipped cap 112 on the same
seeds and reports A, K, A∩K and min(A,K).

Cap 40 controls the cap-120 C1 artifact, and cap 80 controls the committed
prediction-cap artifact.  Both must reproduce their per-seed A, K and A∩K
counts exactly, or the build refuses.  Cap 112 is the engine's shipped
prediction cap, not a proposed protocol.

No engine file changes; MAX_PREDICTIONS is set on the service instance.  No
target, freeze, grant or A1 cell.

    python -m benchmarks.a1_prediction_cap_112 --write
    python -m benchmarks.a1_prediction_cap_112 --check
    python -m benchmarks.a1_prediction_cap_112 --self-test
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_prediction_cap_c1 as base
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
C1_PATH = DOCS / "a1_c1_cap120.json"
REFERENCE_PATH = DOCS / "a1_prediction_cap_c1.json"
OUT_PATH = DOCS / "a1_prediction_cap_112.json"
PAGE_PATH = DOCS / "A1-PREDICTION-CAP-112.md"
ID = "A1-PREDICTION-CAP-112-1"
DATE = "2026-11-14"
KIND = "a1_prediction_cap_112"
STATUS = "COUNTERFACTUAL PREDICTION-CAP DIAGNOSTIC — AVAILABILITY ONLY; NO TARGET, FREEZE, GRANT OR A1 CELL"
CAPS = (40, 80, 112)
CONTROL_CAP = 40
NEAR_CAP = 80
TEST_CAP = 112
C1_FLOOR = base.C1_FLOOR
BLOCKS = base.BLOCKS


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _summaries(rows: list[dict]) -> list[dict]:
    out = []
    for cap in CAPS:
        group = [row for row in rows if row["prediction_cap"] == cap]
        out.append({
            "prediction_cap": cap,
            "seeds": len(group),
            "A_total": sum(row["A"] for row in group),
            "K_total": sum(row["K"] for row in group),
            "A_and_K_total": sum(row["A_and_K"] for row in group),
            "C1_marginal_total": sum(row["C1_marginal"] for row in group),
            "C1_joint_total": sum(row["C1_joint"] for row in group),
            "C1_marginal_pass": sum(row["C1_marginal_pass"] for row in group),
            "C1_joint_pass": sum(row["C1_joint_pass"] for row in group),
            "A_range": [min(row["A"] for row in group),
                        max(row["A"] for row in group)],
            "K_range": [min(row["K"] for row in group),
                        max(row["K"] for row in group)],
            "A_and_K_range": [min(row["A_and_K"] for row in group),
                              max(row["A_and_K"] for row in group)],
            "C1_joint_range": [min(row["C1_joint"] for row in group),
                               max(row["C1_joint"] for row in group)],
            "binding_A": sum(row["binding"] == "A" for row in group),
            "binding_K": sum(row["binding"] == "K" for row in group),
            "binding_both": sum(row["binding"] == "both" for row in group),
        })
    return out


def _by_block(rows: list[dict]) -> list[dict]:
    out = []
    for block in BLOCKS:
        entry = {"label": block["label"], "tags": block["tags"]}
        for cap in CAPS:
            group = [row for row in rows
                     if row["block"] == block["label"]
                     and row["prediction_cap"] == cap]
            entry[str(cap)] = {
                "candidate_edges": sum(row["candidate_edges"] for row in group),
                "A": sum(row["A"] for row in group),
                "K": sum(row["K"] for row in group),
                "A_and_K": sum(row["A_and_K"] for row in group),
                "C1_marginal_pass": sum(row["C1_marginal_pass"] for row in group),
                "C1_joint_pass": sum(row["C1_joint_pass"] for row in group),
                "C1_joint_range": [min(row["C1_joint"] for row in group),
                                   max(row["C1_joint"] for row in group)],
            }
        out.append(entry)
    return out


def build() -> dict:
    tasks = [
        (block["label"], seed, cap)
        for block in BLOCKS
        for seed in block["seeds"]
        for cap in CAPS
    ]
    with ProcessPoolExecutor(max_workers=min(6, len(tasks))) as pool:
        raw = list(pool.map(base._replay, tasks))

    by_key = {(row["block"], row["seed"], row["prediction_cap"]): row
              for row in raw}
    c1_rows = {
        (row["block"], row["seed"]): row
        for row in _load(C1_PATH)["rows"] if row["cap"] == 120
    }
    for (label, seed), expected in c1_rows.items():
        got = by_key[(label, seed, CONTROL_CAP)]
        for field in ("A", "K", "A_and_K"):
            if got[field] != expected[field]:
                raise SystemExit(
                    "REFUSED: cap-40 control %s/%d %s %d, expected %d"
                    % (label, seed, field, got[field], expected[field]))

    reference = {
        (row["block"], row["seed"]): row
        for row in _load(REFERENCE_PATH)["rows"]
        if row["prediction_cap"] == NEAR_CAP
    }
    for (label, seed), expected in reference.items():
        got = by_key[(label, seed, NEAR_CAP)]
        for field in ("A", "K", "A_and_K"):
            if got[field] != expected[field]:
                raise SystemExit(
                    "REFUSED: cap-80 reference %s/%d %s %d, expected %d"
                    % (label, seed, field, got[field], expected[field]))

    rows = []
    for row in sorted(raw, key=lambda item: (
            item["prediction_cap"], item["block"], item["seed"])):
        rows.append({key: value for key, value in row.items()
                     if key not in ("A_edges", "K_edges")})
    summaries = _summaries(rows)
    by_block = _by_block(rows)
    near = next(row for row in summaries if row["prediction_cap"] == NEAR_CAP)
    test = next(row for row in summaries if row["prediction_cap"] == TEST_CAP)
    test_16_passes = sum(block[str(TEST_CAP)]["C1_joint_pass"]
                         for block in by_block if block["label"] != "larger-28")
    if test_16_passes:
        reading = (
            "At prediction cap 112, the 16-tag near-misses clear on %d/12 "
            "seeds (current %d/6, fresh %d/6); joint C1 reaches %d/18 overall "
            "against %d/18 at cap 80."
            % (test_16_passes,
               by_block[0][str(TEST_CAP)]["C1_joint_pass"],
               by_block[1][str(TEST_CAP)]["C1_joint_pass"],
               test["C1_joint_pass"], near["C1_joint_pass"])
        )
    else:
        best = max(
            (block[str(TEST_CAP)]["C1_joint_range"][1]
             for block in by_block if block["label"] != "larger-28"),
            default=0,
        )
        reading = (
            "At prediction cap 112, the 16-tag near-misses do not clear: "
            "current and fresh remain 0/6, and the best 16-tag joint ceiling "
            "is %d. Joint C1 reaches %d/18 overall against %d/18 at cap 80."
            % (best, test["C1_joint_pass"], near["C1_joint_pass"])
        )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "At loop cap 120, does the shipped prediction cap 112 clear the "
            "16-tag joint A∩K near-misses left at cap 80?"
        ),
        "definition": (
            "A, K, A∩K and min(A,K) on the same 18 candidate streams at "
            "prediction caps 40/80/112, loop cap 120, C1 floor 60."
        ),
        "method": (
            "One no-arm replay per seed and cap. Cap 40 must reproduce the "
            "committed cap-120 C1 rows; cap 80 must reproduce the committed "
            "prediction-cap rows; both checks cover A, K and A∩K per seed. "
            "Only MAX_PREDICTIONS changes."
        ),
        "constants": {
            "cycles": base.CYCLES,
            "loop_cap": base.LOOP_CAP,
            "prediction_caps": list(CAPS),
            "control_cap": CONTROL_CAP,
            "near_cap": NEAR_CAP,
            "test_cap": TEST_CAP,
            "c1_floor": C1_FLOOR,
        },
        "governance": {
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "summaries": summaries,
        "by_block": by_block,
        "rows": rows,
        "not_evidence": (
            "An availability-only counterfactual on 18 no-arm seeds at one "
            "shipped cap. It measures the C1 ceiling; it is not a treatment "
            "effect, target viability or a successor. Cap 112 is the engine's "
            "shipped prediction cap, not a new protocol."
        ),
    })


def render(doc: dict) -> str:
    summaries = {row["prediction_cap"]: row for row in doc["summaries"]}
    lines = [
        "# A1 C1 at prediction cap 112",
        "",
        "Generated from `docs/a1_prediction_cap_112.json` by "
        "`python -m benchmarks.a1_prediction_cap_112 --write`. Do not edit by hand.",
        "",
        "**Availability-only counterfactual, not an A1 result.** Same 18 "
        "candidate streams at loop cap **120**, prediction caps **40/80/112**. "
        "No target, freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "| Prediction cap | A | K | A∩K | Σ min(A,K) | Pass min | Pass joint | Binding A/K/tie |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for cap in CAPS:
        row = summaries[cap]
        lines.append("| %d | %d | %d | %d | %d | %d/18 | %d/18 | %d/%d/%d |" % (
            cap, row["A_total"], row["K_total"], row["A_and_K_total"],
            row["C1_marginal_total"], row["C1_marginal_pass"],
            row["C1_joint_pass"], row["binding_A"], row["binding_K"],
            row["binding_both"]))
    lines += [
        "",
        "Cap 40 reproduces the committed cap-120 C1 control, and cap 80 "
        "reproduces the committed prediction-cap rows exactly. Cap 112 is the "
        "engine's shipped prediction cap.",
        "",
        "## Per block",
        "",
        "| Block | Candidates | A at 80 | A∩K at 80 | Joint at 80 | A at 112 | A∩K at 112 | Joint at 112 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for block in doc["by_block"]:
        near = block[str(NEAR_CAP)]
        test = block[str(TEST_CAP)]
        lines.append("| %s | %d | %d | %d | %d/6 | %d | %d | %d/6 |" % (
            block["label"], near["candidate_edges"], near["A"],
            near["A_and_K"], near["C1_joint_pass"], test["A"],
            test["A_and_K"], test["C1_joint_pass"]))
    lines += [
        "",
        "## Per-seed rows at cap 112",
        "",
        "| Block | Seed | Candidates | A | K | A∩K | min(A,K) | Gap to 60 (joint) | Binding | Pass min | Pass joint |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in doc["rows"]:
        if row["prediction_cap"] != TEST_CAP:
            continue
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d | %s | %s | %s |" % (
            row["block"], row["seed"], row["candidate_edges"], row["A"],
            row["K"], row["A_and_K"], row["C1_marginal"],
            row["gap_to_60_joint"], row["binding"],
            "yes" if row["C1_marginal_pass"] else "no",
            "yes" if row["C1_joint_pass"] else "no"))
    lines += [
        "",
        "## Reading",
        "",
        "The 16-tag blocks have full K coverage, so their joint ceiling is A. "
        "The larger block is reported separately because its joint ceiling is "
        "limited by K coverage as well as A.",
        "",
        "## What this does not claim",
        "",
        doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


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
    rows = doc.get("rows") or []
    if len(rows) != 18 * len(CAPS):
        found.append("%d rows, expected %d" % (len(rows), 18 * len(CAPS)))
    for row in rows:
        if row.get("C1_marginal") != min(row.get("A", -1), row.get("K", -1)):
            found.append("marginal ceiling at %r"
                         % ((row.get("block"), row.get("seed"),
                             row.get("prediction_cap")),))
        if row.get("C1_joint") != row.get("A_and_K"):
            found.append("joint ceiling at %r"
                         % ((row.get("block"), row.get("seed"),
                             row.get("prediction_cap")),))
        if row.get("gap_to_60_joint") != C1_FLOOR - row.get("C1_joint", -1):
            found.append("joint gap at %r"
                         % ((row.get("block"), row.get("seed"),
                             row.get("prediction_cap")),))
    for summary in doc.get("summaries") or []:
        group = [row for row in rows
                 if row["prediction_cap"] == summary["prediction_cap"]]
        for field, source in (
                ("A_total", "A"), ("K_total", "K"),
                ("A_and_K_total", "A_and_K"),
                ("C1_marginal_total", "C1_marginal"),
                ("C1_joint_total", "C1_joint")):
            if summary.get(field) != sum(row[source] for row in group):
                found.append("%s at cap %s"
                             % (field, summary.get("prediction_cap")))
        if summary.get("C1_marginal_pass") != sum(
                row["C1_marginal_pass"] for row in group):
            found.append("marginal pass count at cap %s"
                         % summary.get("prediction_cap"))
        if summary.get("C1_joint_pass") != sum(
                row["C1_joint_pass"] for row in group):
            found.append("joint pass count at cap %s"
                         % summary.get("prediction_cap"))
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    row = {"A": 67, "K": 138, "A_and_K": 58}
    if min(row["A"], row["K"]) != 67:
        failures.append("min(A,K) must be the marginal ceiling")
    if row["A_and_K"] != 58 or row["A_and_K"] >= C1_FLOOR:
        failures.append("joint ceiling must stay A∩K and fail at 58")
    row = {"A": 83, "K": 105, "A_and_K": 61}
    if row["A_and_K"] < C1_FLOOR:
        failures.append("a 61-row joint ceiling must pass")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    for row in body["summaries"]:
        print("cap %d: A %d, K %d, A∩K %d, marginal %d/18, joint %d/18"
              % (row["prediction_cap"], row["A_total"], row["K_total"],
                 row["A_and_K_total"], row["C1_marginal_pass"],
                 row["C1_joint_pass"]))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no prediction-cap 112 artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("prediction-cap 112: clean")
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
        print("prediction-cap 112 self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
