"""Is the target-entropy term what pushes flip_q edges past cap 112?

The engine orders transition candidates by schema prior, target entropy
ascending, transition probability descending, temporal count descending, then
source and target.  At loop cap 120 / prediction cap 112 the twelve 16-tag
seeds leave 73 transitions unserved, 65 of them `flip_q`.

This replay records, for every candidate transition and at every cycle, the
engine rank and the entropy / probability / count the engine used, plus two
counterfactual ranks of the same full list:

* count only (temporal count descending, then source/target),
* probability only (transition probability descending, then source/target).

Target entropy is computed per source, so within a source every outgoing edge
shares it.  The join therefore compares served against unserved edges, families
against each other, and edges that share a source, where the entropy term
cannot discriminate by construction.

The counterfactual orderings re-rank frozen candidate lists; they are not runs,
because serving a different set would change later reinforcement.  Every seed's
A, K and A∩K must reproduce the committed cap-112 artifact, and the engine order
must reproduce that seed's served transition set, or the build refuses.

No engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_cap112_ordering_term --write
    python -m benchmarks.a1_cap112_ordering_term --check
    python -m benchmarks.a1_cap112_ordering_term --self-test
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_arms
from benchmarks import a1_k_dilution
from benchmarks import a1_prediction_cap_112 as cap
from benchmarks import engine_stamp
from benchmarks.acquisition_harness import (
    PHASE_ACQUISITION,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CAP_PATH = DOCS / "a1_prediction_cap_112.json"
SUPPLY_PATH = DOCS / "a1_k_carrier_supply.json"
OUT_PATH = DOCS / "a1_cap112_ordering_term.json"
PAGE_PATH = DOCS / "A1-CAP112-ORDERING-TERM.md"
ID = "A1-CAP112-ORDERING-TERM-1"
DATE = "2026-11-14"
KIND = "a1_cap112_ordering_term"
STATUS = ("DESCRIPTIVE — CAP-112 ORDERING TERM ATTRIBUTION; NO TARGET, FREEZE, "
          "GRANT OR A1 CELL")
CAP = 112
LOOP_CAP = 120
BLOCKS = ("current-16", "fresh-16")
ORDERS = ("engine", "count_only", "probability_only")
FAMILIES = ("same", "flip_p", "flip_q", "diagonal")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _supply() -> dict[tuple[str, int], set[str]]:
    out = {}
    for seed in _load(SUPPLY_PATH)["seeds"]:
        summary = seed["summary"]
        out[(summary["block"], summary["seed"])] = {
            row["edge"] for row in seed["edges"]
        }
    return out


class _OrderService(a1_arms.A1ArmSleepService):
    """Record the engine's transition order and two counterfactual orders."""

    def __init__(self, memory, targets: set[str]):
        super().__init__(memory)
        self.targets = targets
        self.snapshots: list[dict] = []
        self.within = {
            "source_cycles": 0,
            "entropy_identical": 0,
            "flip_p_higher_probability": 0,
            "flip_p_ranks_first": 0,
        }

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        budget = self.MAX_PREDICTIONS
        self.MAX_PREDICTIONS = 100_000
        try:
            full = super()._build_predictions(temporal, freqs, prior_schemas)
        finally:
            self.MAX_PREDICTIONS = budget
        transitions = [row for row in full
                       if not row.evidence.get("is_cooccurrence")]
        cooccurrences = [row for row in full
                         if row.evidence.get("is_cooccurrence")]
        base = budget // 2
        cooc_limit = min(len(cooccurrences), budget - base)
        limit = base + max(0, budget - base - cooc_limit)
        all_rows = []
        for rank, row in enumerate(transitions, start=1):
            all_rows.append({
                "edge": "%s>%s" % (row.source, row.target),
                "engine_rank": rank,
                "entropy": float(row.evidence.get("target_entropy", 0.0)),
                "probability": float(row.evidence.get("transition_prob", 0.0)),
                "count": int(row.evidence.get("temporal_count", 0)),
            })
        rows = []
        if all_rows:
            count_rank = {
                row["edge"]: rank for rank, row in enumerate(
                    sorted(all_rows, key=lambda r: (-r["count"], r["edge"])),
                    start=1)
            }
            probability_rank = {
                row["edge"]: rank for rank, row in enumerate(
                    sorted(all_rows,
                           key=lambda r: (-r["probability"], r["edge"])),
                    start=1)
            }
            for row in all_rows:
                if row["edge"] not in self.targets:
                    continue
                rows.append({
                    **row,
                    "family": _family(self._world, row["edge"]),
                    "count_only": count_rank[row["edge"]],
                    "probability_only": probability_rank[row["edge"]],
                })
        if rows:
            self.snapshots.append({"limit": limit, "rows": rows})
            by_source: dict[str, list[dict]] = defaultdict(list)
            for row in rows:
                by_source[row["edge"].split(">")[0]].append(row)
            for edges in by_source.values():
                families = {row["family"] for row in edges}
                if "flip_p" not in families or "flip_q" not in families:
                    continue
                p = [row for row in edges if row["family"] == "flip_p"]
                q = [row for row in edges if row["family"] == "flip_q"]
                self.within["source_cycles"] += 1
                if all(abs(row["entropy"] - other["entropy"]) < 1e-9
                       for row in p for other in q):
                    self.within["entropy_identical"] += 1
                if min(row["probability"] for row in p) > max(
                        row["probability"] for row in q):
                    self.within["flip_p_higher_probability"] += 1
                if max(row["engine_rank"] for row in p) < min(
                        row["engine_rank"] for row in q):
                    self.within["flip_p_ranks_first"] += 1
        return super()._build_predictions(temporal, freqs, prior_schemas)


def _family(world: dict, edge: str) -> str:
    return a1_k_dilution._cell_relation(world, edge)


def _replay(task: tuple[str, int]) -> dict:
    label, seed = task
    candidates = _supply()[(label, seed)]
    world = cap.base._world(label, seed)
    expected = next(
        row for row in _load(CAP_PATH)["rows"]
        if row["prediction_cap"] == CAP
        and row["block"] == label and row["seed"] == seed
    )
    db_path = _make_scratch_db("a1_cap112_ordering")
    memory = _CountingMemoryService(str(db_path))
    service = _OrderService(memory, candidates)
    service._world = world
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
            "REFUSED: %s/%d A/K/A∩K %d/%d/%d, expected %d/%d/%d"
            % (label, seed, len(a_edges), len(k_edges), len(a_edges & k_edges),
               expected["A"], expected["K"], expected["A_and_K"]))
    model_served = set()
    for snapshot in service.snapshots:
        for row in snapshot["rows"]:
            if row["engine_rank"] <= snapshot["limit"]:
                model_served.add(row["edge"])
    if model_served != a_edges & candidates:
        raise SystemExit(
            "REFUSED: %s/%d the engine-order model serves %d edges, A serves %d"
            % (label, seed, len(model_served), len(a_edges & candidates)))
    rows = []
    for edge in sorted(candidates):
        best = {order: None for order in ORDERS}
        inside = {order: False for order in ORDERS}
        evidence = {}
        for snapshot in service.snapshots:
            for row in snapshot["rows"]:
                if row["edge"] != edge:
                    continue
                if not evidence or row["engine_rank"] < evidence["engine_rank"]:
                    evidence = row
                for order in ORDERS:
                    key = "engine_rank" if order == "engine" else order
                    value = row.get(key)
                    if value is None:
                        continue
                    best[order] = (value if best[order] is None
                                   else min(best[order], value))
                    if value <= snapshot["limit"]:
                        inside[order] = True
        if not evidence:
            continue
        rows.append({
            "block": label,
            "seed": seed,
            "edge": edge,
            "family": _family(world, edge),
            "served": edge in a_edges,
            "entropy": round(evidence["entropy"], 6),
            "probability": round(evidence["probability"], 6),
            "count": evidence["count"],
            "best_rank": best,
            "inside": inside,
        })
    return {"block": label, "seed": seed, "rows": rows,
            "candidates": len(candidates), "A": len(a_edges),
            "within": service.within}


def _mean(rows: list[dict], key: str) -> float | None:
    values = [row[key] for row in rows if row.get(key) is not None]
    return round(statistics.mean(values), 6) if values else None


def build() -> dict:
    tasks = [(block, seed) for block in BLOCKS
             for seed in next(item["seeds"] for item in cap.BLOCKS
                              if item["label"] == block)]
    with ProcessPoolExecutor(max_workers=min(6, len(tasks))) as pool:
        runs = list(pool.map(_replay, tasks))
    rows = [row for run in runs for row in run["rows"]]
    served = [row for row in rows if row["served"]]
    unserved = [row for row in rows if not row["served"]]
    recovered = {order: sum(row["inside"][order] for row in unserved)
                 for order in ORDERS}
    per_family = []
    for family in FAMILIES:
        group = [row for row in rows if row["family"] == family]
        if not group:
            continue
        missing = [row for row in group if not row["served"]]
        per_family.append({
            "family": family,
            "candidates": len(group),
            "served": len(group) - len(missing),
            "unserved": len(missing),
            "serve_rate": round((len(group) - len(missing)) / len(group), 6),
            "mean_entropy": _mean(group, "entropy"),
            "mean_probability": _mean(group, "probability"),
            "mean_count": _mean(group, "count"),
            "unserved_mean_entropy": _mean(missing, "entropy"),
            "unserved_mean_probability": _mean(missing, "probability"),
        })
    within = {key: sum(run["within"][key] for run in runs)
              for key in runs[0]["within"]}
    per_seed = [{
        "block": run["block"],
        "seed": run["seed"],
        "candidates": run["candidates"],
        "A": run["A"],
        "served_ranked": sum(row["served"] for row in run["rows"]),
        "unserved": sum(not row["served"] for row in run["rows"]),
        "recovered": {order: sum(row["inside"][order] for row in run["rows"]
                                 if not row["served"]) for order in ORDERS},
    } for run in sorted(runs, key=lambda run: (run["block"], run["seed"]))]
    found = {
        "seeds": len(runs),
        "candidates": len(rows),
        "served": len(served),
        "unserved": len(unserved),
        "families": dict(Counter(row["family"] for row in rows)),
        "unserved_families": dict(Counter(row["family"] for row in unserved)),
        "recovered": recovered,
        "served_mean_entropy": _mean(served, "entropy"),
        "unserved_mean_entropy": _mean(unserved, "entropy"),
        "served_mean_probability": _mean(served, "probability"),
        "unserved_mean_probability": _mean(unserved, "probability"),
        "served_mean_count": _mean(served, "count"),
        "unserved_mean_count": _mean(unserved, "count"),
        "within_source": within,
    }
    reading = (
        "The target-entropy term gates these edges, but it cannot be what "
        "selects `flip_q` over `flip_p`: the engine computes **one** entropy "
        "over each source's outgoing distribution, so every edge out of a "
        "source shares it. What tracks exclusion is entropy's **level**: "
        "served candidates average **%(se).3f** and unserved ones "
        "**%(ue).3f**, on the same 0-4 bit scale, so the window is filled by "
        "low-entropy sources and emptied of high-entropy ones regardless of "
        "family. Within a source the decision falls to the terms after "
        "entropy: of **%(ns)d** source-cycles that carry both a `flip_p` and "
        "a `flip_q` candidate, **%(ie)d** have identical entropy (as the "
        "construction requires), **%(ph)d** give the `flip_p` edge the higher "
        "probability (**%(pp).4f** against **%(pq).4f** on average) and "
        "**%(fr)d** rank the `flip_p` edge first. The family split in the "
        "unserved set follows from that: `flip_q` candidates average "
        "**%(qpro).4f** transition probability and **%(qcount).1f** count "
        "against **%(ppro).4f** and **%(pcount).1f** for `flip_p`, and "
        "`flip_q` serves at **%(qrate).3f** against **%(prate).3f**. Removing "
        "entropy from the key does not recover the window — re-ranking by "
        "probability alone rescues **%(rp)d** of **%(nu)d** and by count alone "
        "**%(rc)d** — because the excluded edges are also low on both of those "
        "terms. The ordering that pushes them out is therefore "
        "entropy-`then`-probability-`then`-count acting on a low-count, "
        "high-entropy tail, not an entropy penalty aimed at `flip_q`."
        % {
            "se": found["served_mean_entropy"],
            "ue": found["unserved_mean_entropy"],
            "ns": within["source_cycles"], "ie": within["entropy_identical"],
            "ph": within["flip_p_higher_probability"],
            "fr": within["flip_p_ranks_first"],
            "pp": next(row["mean_probability"] for row in per_family
                       if row["family"] == "flip_p"),
            "pq": next(row["mean_probability"] for row in per_family
                       if row["family"] == "flip_q"),
            "qpro": next(row["mean_probability"] for row in per_family
                         if row["family"] == "flip_q"),
            "ppro": next(row["mean_probability"] for row in per_family
                         if row["family"] == "flip_p"),
            "qcount": next(row["mean_count"] for row in per_family
                           if row["family"] == "flip_q"),
            "pcount": next(row["mean_count"] for row in per_family
                           if row["family"] == "flip_p"),
            "qrate": next(row["serve_rate"] for row in per_family
                          if row["family"] == "flip_q"),
            "prate": next(row["serve_rate"] for row in per_family
                          if row["family"] == "flip_p"),
            "rp": recovered["probability_only"], "rc": recovered["count_only"],
            "nu": found["unserved"],
        }
    )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Is the target-entropy term in the engine's transition ordering "
            "what pushes flip_q edges past the cap-112 window?"
        ),
        "definition": (
            "Every candidate transition in the twelve 16-tag seeds at loop cap "
            "120 / prediction cap 112, with its engine rank, the entropy, "
            "probability and count the engine used, two counterfactual ranks, "
            "and whether A serves it."
        ),
        "method": (
            "One no-arm replay per seed through a recording service that "
            "re-enumerates the full transition list each cycle and restores the "
            "real cap for selection. The transition-slot limit comes from the "
            "service's own budget arithmetic. A, K and A∩K must reproduce the "
            "committed cap-112 artifact and the engine order must reproduce the "
            "served transition set exactly, or the build refuses."
        ),
        "constants": {
            "prediction_cap": CAP,
            "loop_cap": LOOP_CAP,
            "orders": list(ORDERS),
            "seeds": len(tasks),
            "transition_base_slots": CAP // 2,
            "entropy_scale": "bits over each source's outgoing distribution",
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "found": found,
        "per_family": per_family,
        "per_seed": per_seed,
        "rows": rows,
        "limits": [
            "The counterfactual orderings re-rank frozen candidate lists; they are not runs, because serving a different set would change later reinforcement.",
            "Entropy is per source, so no within-source comparison can test it as a family discriminator; the test is between sources.",
            "Served versus unserved entropy is a comparison of the sets the window did and did not reach, not an intervention on the key.",
            "One cap pair and one world family: this attributes the cap-112 exclusion, not a general property of the ordering.",
        ],
        "not_evidence": (
            "A descriptive attribution of the cap-112 window on twelve no-arm "
            "16-tag seeds. It does not show that a different ordering would "
            "serve these edges in a real run, and it is not a treatment, "
            "target, freeze, grant or A1 cell."
        ),
    })


def render(doc: dict) -> str:
    found = doc["found"]
    lines = [
        "# A1 cap-112 ordering term",
        "",
        "Generated from `docs/a1_cap112_ordering_term.json` by "
        "`python -m benchmarks.a1_cap112_ordering_term --write`. Do not edit by hand.",
        "",
        "**Descriptive attribution, not an A1 result.** Counterfactual orderings "
        "re-rank a frozen stream; they are not runs.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Served against unserved",
        "",
        "| Set | Candidates | Mean entropy | Mean probability | Mean count |",
        "| --- | ---: | ---: | ---: | ---: |",
        "| served | %d | %.3f | %.4f | %.1f |" % (
            found["served"], found["served_mean_entropy"],
            found["served_mean_probability"], found["served_mean_count"]),
        "| unserved | %d | %.3f | %.4f | %.1f |" % (
            found["unserved"], found["unserved_mean_entropy"],
            found["unserved_mean_probability"], found["unserved_mean_count"]),
        "",
        "## Recovered by ordering",
        "",
        "| Ordering | Unserved edges inside the transition window |",
        "| --- | ---: |",
        "| engine (observed) | %d |" % found["recovered"]["engine"],
        "| probability only | %d |" % found["recovered"]["probability_only"],
        "| count only | %d |" % found["recovered"]["count_only"],
        "",
        "## By family",
        "",
        "| Family | Candidates | Served | Serve rate | Mean entropy | Mean probability | Mean count |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["per_family"]:
        lines.append("| %s | %d | %d | %.3f | %.3f | %.4f | %.1f |" % (
            row["family"], row["candidates"], row["served"], row["serve_rate"],
            row["mean_entropy"], row["mean_probability"], row["mean_count"]))
    within = found["within_source"]
    lines += [
        "",
        "## Within a source",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        "| Source-cycles carrying both families | %d |" % within["source_cycles"],
        "| Of those, identical entropy | %d |" % within["entropy_identical"],
        "| Of those, flip_p has the higher probability | %d |"
        % within["flip_p_higher_probability"],
        "| Of those, flip_p ranks first | %d |" % within["flip_p_ranks_first"],
        "",
        "## Per seed",
        "",
        "| Block | Seed | Candidates | A | Unserved | Probability | Count |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["per_seed"]:
        lines.append("| %s | %d | %d | %d | %d | %d | %d |" % (
            row["block"], row["seed"], row["candidates"], row["A"],
            row["unserved"], row["recovered"]["probability_only"],
            row["recovered"]["count_only"]))
    lines += [
        "",
        "## Limits",
        "",
    ]
    lines += ["- %s" % limit for limit in doc["limits"]]
    lines += [
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
    unserved = [row for row in doc.get("rows") or [] if not row["served"]]
    if len(unserved) != doc["found"]["unserved"]:
        found.append("unserved total")
    if doc["found"]["recovered"]["engine"] != 0:
        found.append("the engine order serves an unserved edge")
    if doc["found"]["unserved_mean_entropy"] <= doc["found"]["served_mean_entropy"]:
        found.append("unserved entropy is not above served entropy")
    if doc["found"]["within_source"]["entropy_identical"] != \
            doc["found"]["within_source"]["source_cycles"]:
        found.append("a shared source does not share its entropy")
    for row in unserved:
        if row["inside"]["engine"]:
            found.append("an unserved edge is inside the engine window")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if CAP // 2 != 56 or LOOP_CAP != 120:
        failures.append("cap constants moved")
    if set(ORDERS) != {"engine", "count_only", "probability_only"}:
        failures.append("order vocabulary")
    rows = [{"count": 3, "probability": 0.5}, {"count": 5, "probability": 0.2}]
    if sorted(rows, key=lambda r: (-r["count"],))[0]["count"] != 5:
        failures.append("count ordering")
    if sorted(rows, key=lambda r: (-r["probability"],))[0]["probability"] != 0.5:
        failures.append("probability ordering")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    print("recovered:", body["found"]["recovered"])
    print("within:", body["found"]["within_source"])
    for row in body["per_family"]:
        print(" ", row)
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no ordering-term artifact; run --write")
    found = problems(_load(OUT_PATH))
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("cap-112 ordering term: clean")
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
        print("ordering self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
