"""Does the prediction cap move A once the loop window is no longer binding?

The cap-120 C1 replay removed K as the marginal blocker: A bound C1 on
18/18 seeds and the joint A∩K ceiling never reached 60.  This diagnostic holds
the loop cap at 120 and varies only the prediction cap:

    20, 40 (the cap-120 control), 80.

It records A, K, A∩K and min(A,K) together on the same 18 candidate streams.
The cap-40 rows must reproduce the committed cap-120 C1 artifact exactly, or
the build refuses.  Cap 80 is a diagnostic condition, not a proposed protocol.

No engine file changes; the caps are overridden on the service instance.  No
target, freeze, grant or A1 cell.

    python -m benchmarks.a1_prediction_cap_c1 --write
    python -m benchmarks.a1_prediction_cap_c1 --check
    python -m benchmarks.a1_prediction_cap_c1 --self-test
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

from benchmarks import a1_arms
from benchmarks import a1_larger_universe
from benchmarks import engine_stamp
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import (
    PHASE_ACQUISITION,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SUPPLY_PATH = DOCS / "a1_k_carrier_supply.json"
C1_PATH = DOCS / "a1_c1_cap120.json"
OUT_PATH = DOCS / "a1_prediction_cap_c1.json"
PAGE_PATH = DOCS / "A1-PREDICTION-CAP-C1.md"
ID = "A1-PREDICTION-CAP-C1-1"
DATE = "2026-11-14"
KIND = "a1_prediction_cap_c1"
STATUS = "COUNTERFACTUAL PREDICTION-CAP DIAGNOSTIC — AVAILABILITY ONLY; NO TARGET, FREEZE, GRANT OR A1 CELL"
CYCLES = 120
LOOP_CAP = 120
PREDICTION_CAPS = (20, 40, 80)
CONTROL_CAP = 40
C1_FLOOR = 60
BLOCKS = (
    {
        "label": "current-16",
        "tags": 16,
        "seeds": (20630101, 20630102, 20630103, 20630104, 20630105, 20630106),
        "world": lambda seed: generate_compositional_world(seed=seed, cycles=CYCLES),
    },
    {
        "label": "fresh-16",
        "tags": 16,
        "seeds": (20650101, 20650102, 20650103, 20650104, 20650105, 20650106),
        "world": lambda seed: generate_compositional_world(seed=seed, cycles=CYCLES),
    },
    {
        "label": "larger-28",
        "tags": 28,
        "seeds": (20660101, 20660102, 20660103, 20660104, 20660105, 20660106),
        "world": a1_larger_universe.generate_world,
    },
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _sources() -> tuple[dict, dict]:
    supply = _load(SUPPLY_PATH)
    candidates = {}
    for seed in supply["seeds"]:
        summary = seed["summary"]
        candidates[(summary["block"], summary["seed"])] = {
            row["edge"] for row in seed["edges"]
        }
    control = {}
    for row in _load(C1_PATH)["rows"]:
        if row["cap"] == LOOP_CAP:
            control[(row["block"], row["seed"])] = {
                "A": row["A"], "K": row["K"], "A_and_K": row["A_and_K"],
            }
    return candidates, control


def _world(label: str, seed: int) -> dict:
    for block in BLOCKS:
        if block["label"] == label:
            return block["world"](seed)
    raise KeyError(label)


def _replay(task: tuple[str, int, int]) -> dict:
    label, seed, cap = task
    candidates, _ = _sources()
    candidate_edges = candidates[(label, seed)]
    world = _world(label, seed)
    db_path = _make_scratch_db("a1_prediction_cap_c1")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = cap
    service.MAX_LOOPS = LOOP_CAP
    a_edges: set[str] = set()
    k_edges: set[str] = set()
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo = acq_lo * EVENTS_PER_CYCLE
    event_hi = acq_hi * EVENTS_PER_CYCLE
    try:
        for index, (text, trainable) in enumerate(
                zip(world["events"], world["trainable"])):
            in_acq = event_lo <= index < event_hi
            if in_acq and not trainable:
                continue
            if index % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = index // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=a1_arms.ACQ_SOURCE if in_acq else "env")
            if (index + 1) % EVENTS_PER_CYCLE != 0:
                continue
            report = service.run_sleep_cycle()
            predictions = {
                "%s>%s" % (prediction.source, prediction.target)
                for prediction in report.predictions
            }
            carried = {"%s>%s" % edge for edge in a1_arms._carrier_edges(report)}
            a_edges |= predictions & candidate_edges
            k_edges |= carried & candidate_edges
    finally:
        memory.close()
        db_path.unlink(missing_ok=True)
    both = a_edges & k_edges
    ceiling = min(len(a_edges), len(k_edges))
    if len(a_edges) < len(k_edges):
        binding = "A"
    elif len(k_edges) < len(a_edges):
        binding = "K"
    else:
        binding = "both"
    return {
        "block": label,
        "seed": seed,
        "prediction_cap": cap,
        "candidate_edges": len(candidate_edges),
        "A": len(a_edges),
        "K": len(k_edges),
        "A_and_K": len(both),
        "C1_marginal": ceiling,
        "C1_joint": len(both),
        "gap_to_60_marginal": C1_FLOOR - ceiling,
        "gap_to_60_joint": C1_FLOOR - len(both),
        "C1_marginal_pass": ceiling >= C1_FLOOR,
        "C1_joint_pass": len(both) >= C1_FLOOR,
        "binding": binding,
        "A_edges": sorted(a_edges),
        "K_edges": sorted(k_edges),
    }


def build() -> dict:
    candidates, control = _sources()
    tasks = [
        (block["label"], seed, cap)
        for block in BLOCKS
        for seed in block["seeds"]
        for cap in PREDICTION_CAPS
    ]
    with ProcessPoolExecutor(max_workers=min(6, len(tasks))) as pool:
        raw = list(pool.map(_replay, tasks))
    by_key = {(row["block"], row["seed"], row["prediction_cap"]): row
              for row in raw}
    for (label, seed), expected in control.items():
        got = by_key[(label, seed, CONTROL_CAP)]
        for field in ("A", "K", "A_and_K"):
            if got[field] != expected[field]:
                raise SystemExit(
                    "REFUSED: control %s/%d %s %d, expected %d"
                    % (label, seed, field, got[field], expected[field]))
    rows = []
    for row in sorted(raw, key=lambda item: (
            item["prediction_cap"], item["block"], item["seed"])):
        rows.append({key: value for key, value in row.items()
                     if key not in ("A_edges", "K_edges")})
    summaries = []
    for cap in PREDICTION_CAPS:
        group = [row for row in rows if row["prediction_cap"] == cap]
        summaries.append({
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
            "C1_marginal_range": [
                min(row["C1_marginal"] for row in group),
                max(row["C1_marginal"] for row in group),
            ],
            "C1_joint_range": [
                min(row["C1_joint"] for row in group),
                max(row["C1_joint"] for row in group),
            ],
            "binding_A": sum(row["binding"] == "A" for row in group),
            "binding_K": sum(row["binding"] == "K" for row in group),
            "binding_both": sum(row["binding"] == "both" for row in group),
        })
    by_block = []
    for block in BLOCKS:
        entry = {"label": block["label"], "tags": block["tags"]}
        for cap in PREDICTION_CAPS:
            group = [row for row in rows
                     if row["block"] == block["label"]
                     and row["prediction_cap"] == cap]
            entry[str(cap)] = {
                "candidate_edges": sum(row["candidate_edges"] for row in group),
                "A": sum(row["A"] for row in group),
                "K": sum(row["K"] for row in group),
                "A_and_K": sum(row["A_and_K"] for row in group),
                "C1_marginal_total": sum(row["C1_marginal"] for row in group),
                "C1_joint_total": sum(row["C1_joint"] for row in group),
                "C1_marginal_pass": sum(row["C1_marginal_pass"] for row in group),
                "C1_joint_pass": sum(row["C1_joint_pass"] for row in group),
                "C1_joint_range": [
                    min(row["C1_joint"] for row in group),
                    max(row["C1_joint"] for row in group),
                ],
            }
        by_block.append(entry)
    control_row = next(row for row in summaries
                       if row["prediction_cap"] == CONTROL_CAP)
    high = next(row for row in summaries
                if row["prediction_cap"] == max(PREDICTION_CAPS))
    a_lift = high["A_total"] - control_row["A_total"]
    joint_lift = high["C1_joint_total"] - control_row["C1_joint_total"]
    if a_lift > 0 and high["C1_joint_pass"] > control_row["C1_joint_pass"]:
        reading = (
            "A responds to the prediction cap while K stays flat, and the "
            "joint C1 ceiling rises with it; %d/18 seeds reach 60 jointly at "
            "cap %d."
            % (high["C1_joint_pass"], max(PREDICTION_CAPS))
        )
    elif a_lift > 0:
        reading = (
            "A responds to the prediction cap, but the joint A∩K ceiling does "
            "not clear 60: %d/18 seeds pass jointly at cap %d. The prediction "
            "path is movable; the overlap is the remaining constraint."
            % (high["C1_joint_pass"], max(PREDICTION_CAPS))
        )
    elif high["A_total"] == control_row["A_total"]:
        reading = (
            "A does not respond to the prediction cap at loop cap 120: A is "
            "flat at %d from cap %d to cap %d, and the joint ceiling stays "
            "below 60."
            % (high["A_total"], CONTROL_CAP, max(PREDICTION_CAPS))
        )
    else:
        reading = (
            "A moves non-monotonically with the prediction cap and the joint "
            "ceiling remains below 60; the cap is not a clean lever."
        )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "At loop cap 120, does raising the prediction cap move A and make "
            "the joint A∩K C1 ceiling reach 60?"
        ),
        "definition": (
            "A, K, A∩K and min(A,K) on the same 18 candidate streams at "
            "prediction caps 20/40/80, with the loop cap fixed at 120 and the "
            "C1 floor at 60."
        ),
        "method": (
            "One no-arm replay per seed and prediction cap. The cap-40 rows "
            "must reproduce the committed cap-120 C1 artifact's A, K and A∩K "
            "counts per seed; only MAX_PREDICTIONS is overridden."
        ),
        "constants": {
            "cycles": CYCLES,
            "loop_cap": LOOP_CAP,
            "prediction_caps": list(PREDICTION_CAPS),
            "control_cap": CONTROL_CAP,
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
            "An availability-only counterfactual on 18 no-arm seeds. It varies "
            "the prediction cap on the service instance and measures the C1 "
            "ceiling; it is not a treatment effect, target viability or a "
            "successor. Cap 80 is a diagnostic condition, not a proposed "
            "protocol."
        ),
    })


def render(doc: dict) -> str:
    summaries = {row["prediction_cap"]: row for row in doc["summaries"]}
    control = summaries[CONTROL_CAP]
    lines = [
        "# A1 C1 ceiling under the prediction cap",
        "",
        "Generated from `docs/a1_prediction_cap_c1.json` by "
        "`python -m benchmarks.a1_prediction_cap_c1 --write`. Do not edit by hand.",
        "",
        "**Availability-only counterfactual, not an A1 result.** Same 18 "
        "candidate streams at loop cap **120**, prediction caps **20/40/80**. "
        "No target, freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "| Prediction cap | A | K | A∩K | Σ min(A,K) | C1 pass (marginal) | C1 pass (joint) | Binding A/K/tie |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for cap in PREDICTION_CAPS:
        row = summaries[cap]
        lines.append("| %d | %d | %d | %d | %d | %d/18 | %d/18 | %d/%d/%d |" % (
            cap, row["A_total"], row["K_total"], row["A_and_K_total"],
            row["C1_marginal_total"], row["C1_marginal_pass"],
            row["C1_joint_pass"], row["binding_A"], row["binding_K"],
            row["binding_both"]))
    lines += [
        "",
        "The cap-40 control reproduces the committed cap-120 C1 rows exactly "
        "for A, K and A∩K. The marginal ceiling is `min(A,K)`; the joint "
        "ceiling is `A∩K`, which is the stricter targetable count.",
        "",
        "## Per block",
        "",
        "| Block | Candidates | A at 20 | A at 40 | A at 80 | K at 80 | A∩K at 80 | Joint pass at 80 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for block in doc["by_block"]:
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d/6 |" % (
            block["label"], block["20"]["candidate_edges"],
            block["20"]["A"], block["40"]["A"], block["80"]["A"],
            block["80"]["K"], block["80"]["A_and_K"],
            block["80"]["C1_joint_pass"]))
    lines += [
        "",
        "## Per-seed rows at cap 80",
        "",
        "| Block | Seed | Candidates | A | K | A∩K | min(A,K) | Gap to 60 (joint) | Binding | Marginal pass | Joint pass |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in doc["rows"]:
        if row["prediction_cap"] != max(PREDICTION_CAPS):
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
        "This moves only the prediction window at a fixed 120-loop cap. A "
        "response identifies the prediction path as a lever; it does not show "
        "that C1 is reachable, because the joint A∩K ceiling is reported "
        "beside the marginal `min(A,K)` ceiling.",
        "",
        "## What this does not claim",
        "",
        doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def _row(a: int, k: int, both: int, cap: int = 80) -> dict:
    marginal = min(a, k)
    return {
        "block": "x", "seed": 1, "prediction_cap": cap,
        "candidate_edges": 10, "A": a, "K": k, "A_and_K": both,
        "C1_marginal": marginal, "C1_joint": both,
        "gap_to_60_marginal": 60 - marginal, "gap_to_60_joint": 60 - both,
        "C1_marginal_pass": marginal >= 60, "C1_joint_pass": both >= 60,
        "binding": "A" if a < k else "K" if k < a else "both",
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
    rows = doc.get("rows") or []
    if len(rows) != 18 * len(PREDICTION_CAPS):
        found.append("%d rows, expected %d"
                     % (len(rows), 18 * len(PREDICTION_CAPS)))
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
                found.append("%s at cap %s" % (field, summary.get("prediction_cap")))
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
    a = _row(80, 100, 70)
    if a["C1_marginal"] != 80 or a["C1_joint"] != 70:
        failures.append("marginal and joint ceilings must stay distinct")
    if not a["C1_marginal_pass"] or not a["C1_joint_pass"]:
        failures.append("70 and 80 must both pass 60")
    b = _row(67, 138, 58)
    if not b["C1_marginal_pass"] or b["C1_joint_pass"]:
        failures.append("67 must pass marginally while a 58-row overlap fails")
    c = _row(59, 111, 46)
    if c["binding"] != "A":
        failures.append("A must bind when A<K")
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
        raise SystemExit("no prediction-cap C1 artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("prediction-cap C1: clean")
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
        print("prediction-cap C1 self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
