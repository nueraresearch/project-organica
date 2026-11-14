"""Which selection rule creates the cap-80 larger-28 overlap loss?

The overlap decomposition shows 104 A\\K edges and 338 K\\A edges across the
six larger-28 seeds.  This trace attributes each edge to the engine gate that
kept it out of the other set:

K side (A\\K)
  * no 2-/3-cycle ever reached LOOP_MIN_STRENGTH;
  * the edge's best loop rank was above the MAX_LOOPS=120 cut;
  * a selected loop or dream carried it (which would contradict A\\K).

A side (K\\A)
  * directed-pair support stayed below PREDICTION_MIN_COUNT=5;
  * the edge was a transition ranked below the cap-80 half-budget;
  * the edge was a cooccurrence ranked below its quota;
  * the edge was inside the returned window (which would contradict K\\A).

The trace wraps the prediction builder and loop builder to record the full
candidate order before the engine's caps are applied.  It does not change the
engine or the selected A/K sets; cap-80 A, K and A∩K must reproduce the
committed overlap artifact exactly, or the build refuses.

    python -m benchmarks.a1_prediction_cap80_selection --write
    python -m benchmarks.a1_prediction_cap80_selection --check
    python -m benchmarks.a1_prediction_cap80_selection --self-test
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_arms
from benchmarks import a1_k_carrier_supply
from benchmarks import a1_k_supply_discriminator
from benchmarks import a1_prediction_cap112_decompose as decomp
from benchmarks import engine_stamp
from benchmarks.acquisition_harness import (
    PHASE_ACQUISITION,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OVERLAP_PATH = DOCS / "a1_prediction_cap80_overlap.json"
OUT_PATH = DOCS / "a1_prediction_cap80_selection.json"
PAGE_PATH = DOCS / "A1-PREDICTION-CAP80-SELECTION.md"
ID = "A1-PREDICTION-CAP80-SELECTION-1"
DATE = "2026-11-14"
KIND = "a1_prediction_cap80_selection"
STATUS = "DESCRIPTIVE — CAP-80 LARGER-28 SELECTION-RULE TRACE; NO TARGET, FREEZE, GRANT OR A1 CELL"
BLOCK = "larger-28"
SEEDS = (20660101, 20660102, 20660103, 20660104, 20660105, 20660106)
CAP = 80
LOOP_CAP = 120
C1_FLOOR = 60
SUPPORT_FLOOR = 5
LOOP_LIMIT = LOOP_CAP
K_REASONS = (
    "no_2_or_3_cycle",
    "loop_rank_above_loop_cap",
    "carried_by_selected_loop",
    "carried_by_dream",
    "unclassified",
)
A_REASONS = (
    "support_below_prediction_floor",
    "transition_rank_below_half_budget",
    "cooccurrence_rank_below_quota",
    "no_prediction_candidate",
    "inside_returned_window",
    "unclassified",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _counts(rows: list[dict], key: str, labels: tuple[str, ...]) -> list[dict]:
    counts = Counter(row[key] for row in rows)
    return [{"label": label, "edges": counts.get(label, 0)} for label in labels]


class _TraceService(a1_arms.A1ArmSleepService):
    """Record candidate order and loop order without changing the result."""

    def __init__(self, memory):
        super().__init__(memory)
        self.best_transition_rank: dict[str, int] = {}
        self.best_cooccurrence_rank: dict[str, int] = {}
        self.transition_in_budget: set[str] = set()
        self.cooccurrence_in_budget: set[str] = set()
        self.ever_candidate: set[str] = set()
        self.best_loop_rank: dict[str, int] = {}
        self.ever_possible_loop: set[str] = set()
        self.ever_selected_loop: set[str] = set()
        self.ever_dream: set[str] = set()

    def _build_loops(self, temporal):
        selected = super()._build_loops(temporal)
        possible = a1_k_carrier_supply.possible_loops(temporal)
        for loop in possible:
            path = loop["path"]
            rank = loop["rank"]
            for edge in a1_k_carrier_supply._loop_edges(path):
                key = "%s>%s" % edge
                self.ever_possible_loop.add(key)
                self.best_loop_rank[key] = min(
                    self.best_loop_rank.get(key, rank), rank)
        for loop in selected:
            for edge in a1_k_carrier_supply._loop_edges(loop.path):
                self.ever_selected_loop.add("%s>%s" % edge)
        return selected

    def _generate_categorized_dreams(self, *args, **kwargs):
        dreams = super()._generate_categorized_dreams(*args, **kwargs)
        for dream in dreams:
            path = list(dream.path_or_context or [])
            for left, right in zip(path, path[1:]):
                self.ever_dream.add("%s>%s" % (left, right))
        return dreams

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        old_cap = self.MAX_PREDICTIONS
        self.MAX_PREDICTIONS = 100_000
        try:
            full = super()._build_predictions(temporal, freqs, prior_schemas)
        finally:
            self.MAX_PREDICTIONS = old_cap
        transitions = [row for row in full
                       if not row.evidence.get("is_cooccurrence")]
        cooccurrences = [row for row in full
                         if row.evidence.get("is_cooccurrence")]
        budget = old_cap
        base = budget // 2
        cooc_limit = min(len(cooccurrences), budget - base)
        transition_limit = base + max(0, budget - base - cooc_limit)
        for rank, row in enumerate(transitions, start=1):
            key = "%s>%s" % (row.source, row.target)
            self.ever_candidate.add(key)
            self.best_transition_rank[key] = min(
                self.best_transition_rank.get(key, rank), rank)
            if rank <= transition_limit:
                self.transition_in_budget.add(key)
        for rank, row in enumerate(cooccurrences, start=1):
            key = "%s>%s" % (row.source, row.target)
            self.ever_candidate.add(key)
            self.best_cooccurrence_rank[key] = min(
                self.best_cooccurrence_rank.get(key, rank), rank)
            if rank <= cooc_limit:
                self.cooccurrence_in_budget.add(key)
        return super()._build_predictions(temporal, freqs, prior_schemas)


def _candidate_edges(seed: int) -> set[str]:
    for block in _load(decomp.SUPPLY_PATH)["seeds"]:
        summary = block["summary"]
        if summary["block"] == BLOCK and summary["seed"] == seed:
            return {row["edge"] for row in block["edges"]}
    raise KeyError((BLOCK, seed))


def _replay(seed: int) -> dict:
    candidates = _candidate_edges(seed)
    world = decomp.cap.base._world(BLOCK, seed)
    supports = a1_k_supply_discriminator._support_counts(world)
    expected = {
        row["seed"]: row for row in _load(OVERLAP_PATH)["seed_rows"]
    }[seed]
    db_path = _make_scratch_db("a1_cap80_selection")
    memory = _CountingMemoryService(str(db_path))
    service = _TraceService(memory)
    service.MAX_PREDICTIONS = CAP
    service.MAX_LOOPS = LOOP_CAP
    a_edges: set[str] = set()
    k_edges: set[str] = set()
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo = acq_lo * EVENTS_PER_CYCLE
    event_hi = acq_hi * EVENTS_PER_CYCLE
    try:
        for index, (text, trainable) in enumerate(
                zip(world["events"], world["trainable"])):
            if event_lo <= index < event_hi and not trainable:
                continue
            if index % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = index // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=a1_arms.ACQ_SOURCE
                         if event_lo <= index < event_hi else "env")
            if (index + 1) % EVENTS_PER_CYCLE != 0:
                continue
            report = service.run_sleep_cycle()
            a_edges |= {
                "%s>%s" % (prediction.source, prediction.target)
                for prediction in report.predictions
            } & candidates
            k_edges |= {
                "%s>%s" % edge for edge in a1_arms._carrier_edges(report)
            } & candidates
    finally:
        memory.close()
        db_path.unlink(missing_ok=True)
    if (len(a_edges), len(k_edges), len(a_edges & k_edges)) != (
            expected["A"], expected["K"], expected["A_and_K"]):
        raise SystemExit(
            "REFUSED: seed %d A/K/A∩K %d/%d/%d, expected %d/%d/%d"
            % (seed, len(a_edges), len(k_edges), len(a_edges & k_edges),
               expected["A"], expected["K"], expected["A_and_K"]))
    rows = []
    for edge in sorted(candidates):
        source, target = edge.split(">", 1)
        support = int(supports[(source, target)])
        if edge in a_edges - k_edges:
            if edge in service.ever_dream:
                reason = "carried_by_dream"
            elif edge not in service.ever_possible_loop:
                reason = "no_2_or_3_cycle"
            elif service.best_loop_rank.get(edge, LOOP_LIMIT + 1) > LOOP_LIMIT:
                reason = "loop_rank_above_loop_cap"
            elif edge in service.ever_selected_loop:
                reason = "carried_by_selected_loop"
            else:
                reason = "unclassified"
            side = "A\\K"
        elif edge in k_edges - a_edges:
            if support < SUPPORT_FLOOR:
                reason = "support_below_prediction_floor"
            elif edge in service.transition_in_budget or (
                    edge in service.cooccurrence_in_budget):
                reason = "inside_returned_window"
            elif edge in service.best_transition_rank:
                reason = "transition_rank_below_half_budget"
            elif edge in service.best_cooccurrence_rank:
                reason = "cooccurrence_rank_below_quota"
            elif edge not in service.ever_candidate:
                reason = "no_prediction_candidate"
            else:
                reason = "unclassified"
            side = "K\\A"
        else:
            continue
        rows.append({
            "seed": seed,
            "edge": edge,
            "side": side,
            "reason": reason,
            "support": support,
            "A_rank": None,
            "best_loop_rank": service.best_loop_rank.get(edge),
            "best_transition_rank": service.best_transition_rank.get(edge),
            "best_cooccurrence_rank": service.best_cooccurrence_rank.get(edge),
        })
    return {
        "seed": seed,
        "A": len(a_edges),
        "K": len(k_edges),
        "A_and_K": len(a_edges & k_edges),
        "A_only": len(a_edges - k_edges),
        "K_only": len(k_edges - a_edges),
        "rows": rows,
        "carrier_dreams": len(service.ever_dream),
    }


def build() -> dict:
    with ProcessPoolExecutor(max_workers=min(6, len(SEEDS))) as pool:
        runs = list(pool.map(_replay, SEEDS))
    rows = [row for run in runs for row in run["rows"]]
    k_rows = [row for row in rows if row["side"] == "A\\K"]
    a_rows = [row for row in rows if row["side"] == "K\\A"]
    seed_rows = [{key: value for key, value in run.items() if key != "rows"}
                 for run in sorted(runs, key=lambda run: run["seed"])]
    summary = {
        "seeds": len(runs),
        "A_total": sum(run["A"] for run in runs),
        "K_total": sum(run["K"] for run in runs),
        "A_and_K_total": sum(run["A_and_K"] for run in runs),
        "A_only_total": len(k_rows),
        "K_only_total": len(a_rows),
        "K_reasons": _counts(k_rows, "reason", K_REASONS),
        "A_reasons": _counts(a_rows, "reason", A_REASONS),
        "K_reason_by_seed": [
            {"seed": run["seed"], "A_only": run["A_only"],
             **{row["label"]: row["edges"] for row in _counts(
                 [r for r in run["rows"] if r["side"] == "A\\K"],
                 "reason", K_REASONS)}}
            for run in sorted(runs, key=lambda run: run["seed"])
        ],
        "A_reason_by_seed": [
            {"seed": run["seed"], "K_only": run["K_only"],
             **{row["label"]: row["edges"] for row in _counts(
                 [r for r in run["rows"] if r["side"] == "K\\A"],
                 "reason", A_REASONS)}}
            for run in sorted(runs, key=lambda run: run["seed"])
        ],
    }
    top_k = max(k_rows, key=lambda row: sum(
        1 for other in k_rows if other["reason"] == row["reason"]),
        default={"reason": "none"})
    top_a = max(a_rows, key=lambda row: sum(
        1 for other in a_rows if other["reason"] == row["reason"]),
        default={"reason": "none"})
    k_count = sum(1 for row in k_rows if row["reason"] == top_k["reason"])
    a_count = sum(1 for row in a_rows if row["reason"] == top_a["reason"])
    reading = (
        "The %d A\\K edges are dominated by `%s` (%d/%d); the %d K\\A edges "
        "are dominated by `%s` (%d/%d). The overlap loss is therefore a "
        "K-side loop-rank effect plus an A-side budget/rank effect, with the "
        "support floor a minority component."
        % (len(k_rows), top_k["reason"], k_count, len(k_rows),
           len(a_rows), top_a["reason"], a_count, len(a_rows)))
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Which K-selection and A-selection rules produce the cap-80 "
            "larger-28 A\\K and K\\A edge sets?"
        ),
        "definition": (
            "For each larger-28 candidate edge at prediction cap 80, record "
            "whether it is A-only or K-only and the engine gate that kept it "
            "out of the other set. K reasons cover the 2/3-cycle strength "
            "floor and the MAX_LOOPS=15 rank cut; A reasons cover the "
            "PREDICTION_MIN_COUNT=5 floor, the half-budget transition quota "
            "and the cooccurrence quota."
        ),
        "method": (
            "One no-arm replay per seed. A behavior-neutral wrapper records "
            "the full prediction order and the full loop order before the "
            "engine applies its caps; the returned A/K sets still come from "
            "the unmodified service. Cap-80 A, K and A∩K must reproduce the "
            "committed overlap artifact exactly."
        ),
        "constants": {
            "block": BLOCK,
            "seeds": list(SEEDS),
            "prediction_cap": CAP,
            "loop_cap": LOOP_CAP,
            "loop_limit": LOOP_LIMIT,
            "support_floor": SUPPORT_FLOOR,
            "c1_floor": C1_FLOOR,
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "summary": summary,
        "seed_rows": seed_rows,
        "rows": rows,
        "not_evidence": (
            "A descriptive rule trace on six no-arm larger-28 seeds at one "
            "cap pair. It attributes excluded edges to the engine gate they "
            "hit; it does not establish that changing that gate would repair "
            "the overlap, and it is not a treatment, target viability or a "
            "successor."
        ),
    })


def render(doc: dict) -> str:
    s = doc["summary"]
    lines = [
        "# A1 larger-28 overlap: selection-rule trace at cap 80",
        "",
        "Generated from `docs/a1_prediction_cap80_selection.json` by "
        "`python -m benchmarks.a1_prediction_cap80_selection --write`. Do not edit by hand.",
        "",
        "**Availability-only rule trace, not an A1 result.** Six larger-28 "
        "seeds at loop cap **120** / prediction cap **80**. No target, freeze, "
        "grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "| Seeds | A | K | A∩K | A\\K | K\\A |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        "| %d | %d | %d | %d | %d | %d |"
        % (s["seeds"], s["A_total"], s["K_total"], s["A_and_K_total"],
           s["A_only_total"], s["K_only_total"]),
        "",
        "## K-side reasons for A\\K",
        "",
        "| Gate | Edges |",
        "| --- | ---: |",
    ]
    for row in s["K_reasons"]:
        lines.append("| %s | %d |" % (row["label"], row["edges"]))
    lines += [
        "",
        "## A-side reasons for K\\A",
        "",
        "| Gate | Edges |",
        "| --- | ---: |",
    ]
    for row in s["A_reasons"]:
        lines.append("| %s | %d |" % (row["label"], row["edges"]))
    lines += [
        "",
        "## Per seed",
        "",
        "| Seed | A | K | A∩K | A\\K | K\\A |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["seed_rows"]:
        lines.append("| %d | %d | %d | %d | %d | %d |" % (
            row["seed"], row["A"], row["K"], row["A_and_K"],
            row["A_only"], row["K_only"]))
    lines += [
        "",
        "## K-side by seed",
        "",
        "| Seed | A\\K | No cycle | Rank >120 | Other |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in s["K_reason_by_seed"]:
        lines.append("| %d | %d | %d | %d | %d |" % (
            row["seed"], row["A_only"], row["no_2_or_3_cycle"],
            row["loop_rank_above_loop_cap"],
            row["carried_by_selected_loop"] + row["carried_by_dream"]
            + row["unclassified"]))
    lines += [
        "",
        "## A-side by seed",
        "",
        "| Seed | K\\A | Support<5 | Transition quota | Cooccurrence quota | Other |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in s["A_reason_by_seed"]:
        lines.append("| %d | %d | %d | %d | %d | %d |" % (
            row["seed"], row["K_only"],
            row["support_below_prediction_floor"],
            row["transition_rank_below_half_budget"],
            row["cooccurrence_rank_below_quota"],
            row["no_prediction_candidate"] + row["inside_returned_window"]
            + row["unclassified"]))
    lines += [
        "",
        "## Exact A\\K edges",
        "",
        "| Seed | Edge | Support | Best loop rank |",
        "| ---: | --- | ---: | ---: |",
    ]
    for row in doc["rows"]:
        if row["side"] != "A\\K":
            continue
        lines.append("| %d | %s | %d | %s |" % (
            row["seed"], row["edge"], row["support"],
            row["best_loop_rank"] if row["best_loop_rank"] is not None else "-"))
    lines += [
        "",
        "## Reading",
        "",
        "The K-side loss is not a prediction-ranking loss: the A\\K edges are "
        "already served by A, often at rank 1. They are absent from K because "
        "their best loop rank is above the 120-loop cut, not because they lack "
        "a 2-/3-cycle. The A-side loss is the mirror: K\\A "
        "edges are carried, but they either fall below the prediction support "
        "floor, sit below the cap-80 half-budget transition quota, or sit "
        "below the cooccurrence quota.",
        "",
        "## What this does not claim",
        "",
        doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def _row(side: str, support: int, reason: str) -> dict:
    return {"side": side, "support": support, "reason": reason}


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
    if len(rows) != 104 + 338:
        found.append("%d rule rows, expected 442" % len(rows))
    summary = doc.get("summary") or {}
    for side, key in (("A\\K", "K_reasons"), ("K\\A", "A_reasons")):
        total = sum(row.get("edges", 0) for row in summary.get(key) or [])
        if total != sum(1 for row in rows if row.get("side") == side):
            found.append("%s reason total" % side)
    if sum(run.get("A_only", 0) for run in doc.get("seed_rows") or []) != (
            summary.get("A_only_total")):
        found.append("A-only seed total")
    if sum(run.get("K_only", 0) for run in doc.get("seed_rows") or []) != (
            summary.get("K_only_total")):
        found.append("K-only seed total")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if _row("A\\K", 5, "loop_rank_above_loop_cap")["side"] != "A\\K":
        failures.append("A-only must keep its side")
    if _row("K\\A", 4, "support_below_prediction_floor")["support"] >= SUPPORT_FLOOR:
        failures.append("support floor fixture must be below 5")
    if len(K_REASONS) != len(set(K_REASONS)):
        failures.append("K reasons must be unique")
    if len(A_REASONS) != len(set(A_REASONS)):
        failures.append("A reasons must be unique")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no cap-80 selection trace; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("cap-80 selection trace: clean")
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
        print("cap-80 selection self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
