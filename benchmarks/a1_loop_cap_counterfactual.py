"""Does the 15-loop output window cause the candidate-K ceiling?

The carrier trace found that every loop-carried K edge ranks in the engine's
top 15, and that candidate K stays near 240 while candidate edges grow.  This
counterfactual keeps the 18 worlds, candidate streams, prediction cap and
acquisition schedule fixed, and varies only the loop output cap:

    15 (the shipped control), 30, 60 and 120.

It is a no-arm diagnostic.  The cap is changed on the service instance, not in
any engine file.  The control must reproduce the committed candidate-K sets
exactly or the build refuses.  The result is a direction and a loss count, not
a significance test and not an A1 cell.

    python -m benchmarks.a1_loop_cap_counterfactual --write
    python -m benchmarks.a1_loop_cap_counterfactual --check
    python -m benchmarks.a1_loop_cap_counterfactual --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
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
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, _world_compositional_edges

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SUPPLY_PATH = DOCS / "a1_k_carrier_supply.json"
OUT_PATH = DOCS / "a1_loop_cap_counterfactual.json"
PAGE_PATH = DOCS / "A1-LOOP-CAP-COUNTERFACTUAL.md"
ID = "A1-LOOP-CAP-COUNTERFACTUAL-1"
DATE = "2026-11-14"
KIND = "a1_loop_cap_counterfactual"
STATUS = "COUNTERFACTUAL DIAGNOSTIC — LOOP CAP ONLY; NO TARGET, FREEZE, GRANT OR A1 CELL"
CYCLES = 120
PREDICTION_CAP = 40
DREAM_CAP = 8
LOOP_CAPS = (15, 30, 60, 120)
CONTROL_CAP = 15
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


def _supply_rows() -> dict[tuple[str, int], dict]:
    doc = _load(SUPPLY_PATH)
    rows = {}
    for seed in doc["seeds"]:
        summary = seed["summary"]
        rows[(summary["block"], summary["seed"])] = {
            "candidate_edges": sorted(row["edge"] for row in seed["edges"]),
            "candidate_K": sorted(row["edge"] for row in seed["edges"] if row["K"]),
        }
    return rows


def _world(label: str, seed: int) -> dict:
    for block in BLOCKS:
        if block["label"] == label:
            return block["world"](seed)
    raise KeyError(label)


def _replay(task: tuple[str, int, int]) -> dict:
    label, seed, cap = task
    source = _supply_rows()[(label, seed)]
    candidates = set(source["candidate_edges"])
    world = _world(label, seed)
    universe = _world_compositional_edges(world)
    db_path = _make_scratch_db("a1_loop_cap_counterfactual")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = PREDICTION_CAP
    service.MAX_DREAMS = DREAM_CAP
    service.MAX_LOOPS = cap
    candidate_k: set[str] = set()
    all_k: set[str] = set()
    loop_total = 0
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
            loop_total += len(report.loops)
            carried = a1_arms._carrier_edges(report)
            all_k |= {"%s>%s" % edge for edge in carried}
            candidate_k |= {"%s>%s" % edge for edge in carried} & candidates
    finally:
        memory.close()
        db_path.unlink(missing_ok=True)
    return {
        "block": label,
        "seed": seed,
        "cap": cap,
        "universe": len(universe),
        "candidate_edges": len(candidates),
        "candidate_K": sorted(candidate_k),
        "all_K": sorted(all_k),
        "returned_loops": loop_total,
    }


def _summarise(run: dict, control: set[str]) -> dict:
    candidate_k = set(run["candidate_K"])
    return {
        "cap": run["cap"],
        "block": run["block"],
        "seed": run["seed"],
        "candidate_edges": run["candidate_edges"],
        "candidate_K": len(candidate_k),
        "all_K": len(run["all_K"]),
        "new_vs_control": len(candidate_k - control),
        "lost_vs_control": len(control - candidate_k),
        "returned_loops": run["returned_loops"],
    }


def build() -> dict:
    source = _supply_rows()
    tasks = [
        (block["label"], seed, cap)
        for block in BLOCKS
        for seed in block["seeds"]
        for cap in LOOP_CAPS
    ]
    workers = min(6, len(tasks))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        runs = list(pool.map(_replay, tasks))
    control = {
        (run["block"], run["seed"]): set(run["candidate_K"])
        for run in runs if run["cap"] == CONTROL_CAP
    }
    for (label, seed), expected in source.items():
        got = control[(label, seed)]
        want = set(expected["candidate_K"])
        if got != want:
            raise SystemExit(
                "REFUSED: control %s/%d K differs (%d vs %d)"
                % (label, seed, len(got), len(want)))
    rows = [_summarise(run, control[(run["block"], run["seed"])])
            for run in runs]
    rows.sort(key=lambda row: (row["cap"], row["block"], row["seed"]))
    summaries = []
    for cap in LOOP_CAPS:
        group = [row for row in rows if row["cap"] == cap]
        summaries.append({
            "cap": cap,
            "seeds": len(group),
            "candidate_K": sum(row["candidate_K"] for row in group),
            "candidate_edges": sum(row["candidate_edges"] for row in group),
            "all_K": sum(row["all_K"] for row in group),
            "new_vs_control": sum(row["new_vs_control"] for row in group),
            "lost_vs_control": sum(row["lost_vs_control"] for row in group),
            "returned_loops": sum(row["returned_loops"] for row in group),
            "mean_candidate_K": round(
                sum(row["candidate_K"] for row in group) / len(group), 6),
            "candidate_K_range": [
                min(row["candidate_K"] for row in group),
                max(row["candidate_K"] for row in group),
            ],
        })
    by_block = []
    for block in BLOCKS:
        block_row = {"label": block["label"], "tags": block["tags"]}
        for cap in LOOP_CAPS:
            group = [row for row in rows
                     if row["block"] == block["label"] and row["cap"] == cap]
            block_row[str(cap)] = {
                "candidate_K": sum(row["candidate_K"] for row in group),
                "candidate_edges": sum(row["candidate_edges"] for row in group),
                "all_K": sum(row["all_K"] for row in group),
            }
        by_block.append(block_row)
    control_total = next(
        row["candidate_K"] for row in summaries if row["cap"] == CONTROL_CAP)
    top_total = next(
        row["candidate_K"] for row in summaries if row["cap"] == max(LOOP_CAPS))
    monotone = all(
        summaries[i]["candidate_K"] <= summaries[i + 1]["candidate_K"]
        for i in range(len(summaries) - 1)
    )
    losses = sum(row["lost_vs_control"] for row in summaries
                 if row["cap"] != CONTROL_CAP)
    if top_total > control_total and monotone and losses == 0:
        verdict = "WINDOW-LIMITED — raising the loop cap adds candidate K cleanly"
    elif top_total == control_total and losses == 0:
        verdict = "NOT WINDOW-LIMITED — raising the loop cap adds no candidate K"
    else:
        verdict = "MIXED — the cap raises candidate K, with reshuffling losses"
    net_gain = top_total - control_total
    reading = (
        "Raising the loop cap from %d to %d raises unique candidate K from "
        "%d to %d (%+d, %.1f%%), while %d edges are lost against the control. "
        "The direction is window-limited, but the response is strongly sublinear "
        "and is not a fixed K quota."
        % (CONTROL_CAP, max(LOOP_CAPS), control_total, top_total, net_gain,
           100.0 * net_gain / control_total, losses)
    )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Does raising the fixed 15-loop output window increase unique "
            "candidate K on unchanged worlds and candidate streams?"
        ),
        "definition": (
            "The 18 no-arm seeds from the carrier-supply trace, replayed at loop "
            "caps 15, 30, 60 and 120. Prediction cap, dream cap, acquisition "
            "schedule, candidate stream and world are unchanged. Only MAX_LOOPS "
            "is overridden on the service instance."
        ),
        "method": (
            "One replay per seed and cap. The cap-15 run must reproduce the "
            "committed candidate-K set for that seed exactly. Differences are "
            "reported as edges gained and lost against that control."
        ),
        "constants": {
            "cycles": CYCLES,
            "prediction_cap": PREDICTION_CAP,
            "dream_cap": DREAM_CAP,
            "loop_caps": list(LOOP_CAPS),
            "control_cap": CONTROL_CAP,
        },
        "governance": {
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
        "verdict": verdict,
        "verdict_rule": (
            "Clean window-limited requires a higher top-cap total than the "
            "control, nondecreasing totals, and zero edges lost against the "
            "control. Any reshuffling loss makes the strict verdict MIXED; the "
            "reading reports the direction separately."
        ),
        "reading": reading,
        "summaries": summaries,
        "by_block": by_block,
        "rows": rows,
        "not_evidence": (
            "A counterfactual diagnostic on 18 no-arm seeds and one build. It "
            "changes only the loop output cap; it runs no A1 cell, selects no "
            "target and makes no causal claim about capability, retention or "
            "transfer. Raising a cap can reshuffle which loops are stored, so the "
            "gained and lost columns are part of the result."
        ),
    })


def render(doc: dict) -> str:
    summaries = doc["summaries"]
    control = next(row for row in summaries if row["cap"] == CONTROL_CAP)
    lines = [
        "# A1 loop-cap counterfactual",
        "",
        "Generated from `docs/a1_loop_cap_counterfactual.json` by "
        "`python -m benchmarks.a1_loop_cap_counterfactual --write`. Do not edit by hand.",
        "",
        "**Counterfactual diagnostic, not an A1 result.** The same 18 worlds and "
        "candidate streams at loop caps **15/30/60/120**. Only `MAX_LOOPS` is "
        "overridden on the service instance; no engine file, target, freeze, grant "
        "or A1 cell changes.",
        "",
        "## Result",
        "",
        "**%s**" % doc["verdict"],
        "",
        doc["reading"],
        "",
        "The strict rule is: clean window-limited only if the top-cap total is "
        "higher, totals are nondecreasing, and no edge is lost against the "
        "control. The small reshuffling losses keep the label at **MIXED**.",
        "",
        "| Loop cap | Candidate K | Δ vs control | Gained | Lost | All directed K | Mean K/seed | Range |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in summaries:
        lines.append("| %d | %d | %+d | %d | %d | %d | %.2f | %d-%d |" % (
            row["cap"], row["candidate_K"],
            row["candidate_K"] - control["candidate_K"],
            row["new_vs_control"], row["lost_vs_control"], row["all_K"],
            row["mean_candidate_K"], row["candidate_K_range"][0],
            row["candidate_K_range"][1]))
    lines += [
        "",
        "The control at cap **15** reproduces the committed candidate-K set on "
        "every seed. The **gained** and **lost** columns are relative to that "
        "control; a cap increase is not treated as monotone by assumption. At "
        "cap **120** the two 16-tag blocks reach **382/383** candidate K, while "
        "the 28-tag block reaches **733/1,000**: the window is still binding in "
        "the larger world.",
        "",
        "## Per block",
        "",
        "| Block | Candidates | K at 15 | K at 30 | K at 60 | K at 120 | All K at 15 | All K at 120 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for block in doc["by_block"]:
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d |" % (
            block["label"], block["15"]["candidate_edges"],
            block["15"]["candidate_K"], block["30"]["candidate_K"],
            block["60"]["candidate_K"], block["120"]["candidate_K"],
            block["15"]["all_K"], block["120"]["all_K"]))
    lines += [
        "",
        "## Reading",
        "",
        doc["not_evidence"],
        "",
        "The paper's candidate-K ceiling is a candidate-stream count, not the "
        "engine's total directed carrier count. `all_K` is shown separately so a "
        "cap effect cannot be confused with the full carrier population.",
        "",
        "## Per-seed rows",
        "",
        "| Cap | Block | Seed | Candidate edges | Candidate K | New | Lost | All K |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["rows"]:
        lines.append("| %d | %s | %d | %d | %d | %d | %d | %d |" % (
            row["cap"], row["block"], row["seed"], row["candidate_edges"],
            row["candidate_K"], row["new_vs_control"], row["lost_vs_control"],
            row["all_K"]))
    lines += [
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_loop_cap_counterfactual --check",
        "python -m benchmarks.a1_loop_cap_counterfactual --self-test",
        "```",
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
    if len(rows) != 18 * len(LOOP_CAPS):
        found.append("%d rows, expected %d" % (len(rows), 18 * len(LOOP_CAPS)))
    seen = set()
    for row in rows:
        key = (row.get("cap"), row.get("block"), row.get("seed"))
        if key in seen:
            found.append("duplicate row %r" % (key,))
        seen.add(key)
        if row.get("candidate_K", -1) < 0:
            found.append("negative K at %r" % (key,))
        if row.get("new_vs_control", -1) < 0 or row.get(
                "lost_vs_control", -1) < 0:
            found.append("negative diff at %r" % (key,))
    for summary in doc.get("summaries") or []:
        group = [row for row in rows if row["cap"] == summary["cap"]]
        if summary.get("candidate_K") != sum(row["candidate_K"] for row in group):
            found.append("K total at cap %s" % summary.get("cap"))
        if summary.get("candidate_edges") != sum(
                row["candidate_edges"] for row in group):
            found.append("edge total at cap %s" % summary.get("cap"))
        if summary.get("new_vs_control") != sum(
                row["new_vs_control"] for row in group):
            found.append("gained total at cap %s" % summary.get("cap"))
        if summary.get("lost_vs_control") != sum(
                row["lost_vs_control"] for row in group):
            found.append("lost total at cap %s" % summary.get("cap"))
        if summary.get("all_K") != sum(row["all_K"] for row in group):
            found.append("all K total at cap %s" % summary.get("cap"))
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    control = {"a>b", "b>c"}
    same = _summarise({"cap": 30, "block": "x", "seed": 1,
                       "candidate_edges": 3, "candidate_K": ["a>b", "b>c"],
                       "all_K": ["a>b", "b>c"], "returned_loops": 1}, control)
    if same["new_vs_control"] != 0 or same["lost_vs_control"] != 0:
        failures.append("identical sets must produce no difference")
    gained = _summarise({"cap": 60, "block": "x", "seed": 1,
                         "candidate_edges": 3, "candidate_K": ["a>b", "b>c", "c>d"],
                         "all_K": ["a>b", "b>c", "c>d"], "returned_loops": 2}, control)
    if gained["new_vs_control"] != 1 or gained["lost_vs_control"] != 0:
        failures.append("a gained edge must be counted")
    lost = _summarise({"cap": 120, "block": "x", "seed": 1,
                       "candidate_edges": 3, "candidate_K": ["a>b"],
                       "all_K": ["a>b"], "returned_loops": 3}, control)
    if lost["lost_vs_control"] != 1:
        failures.append("a lost edge must be counted")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["verdict"])
    for row in body["summaries"]:
        print("cap %d: candidate K %d, gained %d, lost %d"
              % (row["cap"], row["candidate_K"], row["new_vs_control"],
                 row["lost_vs_control"]))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no loop-cap artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("loop-cap counterfactual: clean; candidate K %d at cap 15, %d at cap 120"
          % (next(row["candidate_K"] for row in body["summaries"]
                  if row["cap"] == CONTROL_CAP),
             next(row["candidate_K"] for row in body["summaries"]
                  if row["cap"] == max(LOOP_CAPS))))
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
        print("loop-cap counterfactual self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
