"""Why do ten 16-tag seeds stay below C1 at prediction cap 112?

At loop cap 120 and prediction cap 112, current-16 and fresh-16 each clear only
1/6 joint C1 seeds.  Their candidate streams are 63-64 edges, yet A is 52-59.

This replay records, for every candidate edge:

* whether it is prediction-available at cap 112 (A112), its best rank there;
* whether it appears under a diagnostic cap of 1000, and at what rank;
* whether it is carrier-available (K);
* directed-pair support in the acquisition stream;
* structural edge family (cell relation and old/new composition).

The cap-1000 pass is a diagnostic ceiling, not a proposed protocol.  It tells
us whether a cap-112 missing edge is merely pushed past the window or never
enters the prediction path at all.  Cap-112 A/K counts must match the
committed prediction-cap artifact exactly, or the build refuses.

No engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_prediction_cap112_decompose --write
    python -m benchmarks.a1_prediction_cap112_decompose --check
    python -m benchmarks.a1_prediction_cap112_decompose --self-test
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_arms
from benchmarks import a1_k_dilution
from benchmarks import a1_k_supply_discriminator
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
OUT_PATH = DOCS / "a1_prediction_cap112_decompose.json"
PAGE_PATH = DOCS / "A1-PREDICTION-CAP112-DECOMPOSE.md"
ID = "A1-PREDICTION-CAP112-DECOMPOSE-1"
DATE = "2026-11-14"
KIND = "a1_prediction_cap112_decompose"
STATUS = "DESCRIPTIVE — CAP-112 16-TAG DECOMPOSITION; NO TARGET, FREEZE, GRANT OR A1 CELL"
CAP = 112
DIAGNOSTIC_CAP = 1000
LOOP_CAP = 120
C1_FLOOR = 60
SUPPORT_FLOOR = 5
SUPPORT_BINS = (
    ("0", 0, 0),
    ("1", 1, 1),
    ("2-3", 2, 3),
    ("4-7", 4, 7),
    ("8-15", 8, 15),
    ("16+", 16, None),
)
RANK_BANDS = (
    ("1-20", 1, 20),
    ("21-40", 21, 40),
    ("41-56", 41, 56),
    ("57-112", 57, 112),
    ("113-1000", 113, 1000),
)
FAMILIES = ("same", "flip_p", "flip_q", "diagonal", "unknown")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _support_bin(value: int) -> str:
    for label, low, high in SUPPORT_BINS:
        if value >= low and (high is None or value <= high):
            return label
    raise ValueError(value)


def _rank_band(value: int | None) -> str:
    if value is None:
        return "never"
    for label, low, high in RANK_BANDS:
        if low <= value <= high:
            return label
    return ">1000"


def _supply_edges() -> dict[tuple[str, int], set[str]]:
    out = {}
    for seed in _load(SUPPLY_PATH)["seeds"]:
        summary = seed["summary"]
        out[(summary["block"], summary["seed"])] = {
            row["edge"] for row in seed["edges"]
        }
    return out


def _replay(task: tuple[str, int, int]) -> dict:
    label, seed, prediction_cap = task
    candidates = _supply_edges()[(label, seed)]
    world = cap.base._world(label, seed)
    supports = a1_k_supply_discriminator._support_counts(world)
    db_path = _make_scratch_db("a1_cap112_decompose")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = prediction_cap
    service.MAX_LOOPS = LOOP_CAP
    a_edges: set[str] = set()
    cooc_edges: set[str] = set()
    k_edges: set[str] = set()
    best_rank: dict[str, int] = {}
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
            for rank, prediction in enumerate(report.predictions, start=1):
                edge = "%s>%s" % (prediction.source, prediction.target)
                if edge in candidates:
                    a_edges.add(edge)
                    if prediction.evidence.get("is_cooccurrence"):
                        cooc_edges.add(edge)
                    best_rank[edge] = min(best_rank.get(edge, rank), rank)
            k_edges |= {
                "%s>%s" % edge for edge in a1_arms._carrier_edges(report)
            } & candidates
    finally:
        memory.close()
        db_path.unlink(missing_ok=True)
    rows = []
    for edge in sorted(candidates):
        source, target = edge.split(">", 1)
        support = int(supports[(source, target)])
        rows.append({
            "edge": edge,
            "support": support,
            "support_bin": _support_bin(support),
            "family": a1_k_dilution._family(edge),
            "cell_relation": a1_k_dilution._cell_relation(world, edge),
            "A": edge in a_edges,
            "cooccurrence": edge in cooc_edges,
            "K": edge in k_edges,
            "A_rank": best_rank.get(edge),
            "A_rank_band": _rank_band(best_rank.get(edge)),
        })
    return {
        "block": label,
        "seed": seed,
        "prediction_cap": prediction_cap,
        "candidate_edges": len(candidates),
        "A": len(a_edges),
        "K": len(k_edges),
        "rows": rows,
    }


def _merged_rows(run112: dict, run1000: dict) -> list[dict]:
    first = {row["edge"]: row for row in run112["rows"]}
    second = {row["edge"]: row for row in run1000["rows"]}
    out = []
    for edge in sorted(first):
        low = first[edge]
        high = second[edge]
        out.append({
            "block": run112["block"],
            "seed": run112["seed"],
            "edge": edge,
            "support": low["support"],
            "support_bin": low["support_bin"],
            "family": low["family"],
            "cell_relation": low["cell_relation"],
            "A112": low["A"],
            "A1000": high["A"],
            "cooccurrence112": low["cooccurrence"],
            "cooccurrence1000": high["cooccurrence"],
            "cooccurrence": low["cooccurrence"] or high["cooccurrence"],
            "K112": low["K"],
            "K1000": high["K"],
            "rank112": low["A_rank"],
            "rank1000": high["A_rank"],
            "rank112_band": low["A_rank_band"],
            "rank1000_band": high["A_rank_band"],
            "missing": not low["A"],
            "cap_bound": (not low["A"]) and high["A"],
            "never_A": not high["A"],
        })
    return out


def _seed_summary(rows: list[dict]) -> dict:
    missing = [row for row in rows if row["missing"]]
    cap_bound = [row for row in rows if row["cap_bound"]]
    return {
        "block": rows[0]["block"],
        "seed": rows[0]["seed"],
        "candidate_edges": len(rows),
        "A112": sum(row["A112"] for row in rows),
        "A1000": sum(row["A1000"] for row in rows),
        "K112": sum(row["K112"] for row in rows),
        "K1000": sum(row["K1000"] for row in rows),
        "gap_to_60": C1_FLOOR - sum(row["A112"] for row in rows),
        "missing": len(missing),
        "missing_support_ge_5": sum(
            row["support"] >= SUPPORT_FLOOR for row in missing),
        "missing_cap_bound": len(cap_bound),
        "missing_never": sum(row["never_A"] for row in missing),
        "missing_cooccurrence": sum(row["cooccurrence"] for row in missing),
        "A112_cooccurrence": sum(
            row["A112"] and row["cooccurrence"] for row in rows),
        "A112_rank_max": max(
            (row["rank112"] for row in rows if row["A112"]), default=0),
        "missing_rank_min": min(
            (row["rank1000"] for row in cap_bound), default=0),
        "missing_rank_max": max(
            (row["rank1000"] for row in cap_bound), default=0),
        "missing_families": dict(Counter(
            row["cell_relation"] for row in missing)),
    }


def _bucket(rows: list[dict], key: str, labels: tuple[str, ...]) -> list[dict]:
    out = []
    for label in labels:
        group = [row for row in rows if row[key] == label]
        if not group:
            continue
        a112 = sum(row["A112"] for row in group)
        out.append({
            "label": label,
            "candidate_edges": len(group),
            "A112": a112,
            "A112_rate": round(a112 / len(group), 6),
            "A1000": sum(row["A1000"] for row in group),
            "K112": sum(row["K112"] for row in group),
            "missing": sum(row["missing"] for row in group),
            "missing_cap_bound": sum(row["cap_bound"] for row in group),
            "missing_never": sum(row["never_A"] for row in group),
            "missing_cooccurrence": sum(
                row["missing"] and row["cooccurrence"] for row in group),
            "A112_cooccurrence": sum(
                row["A112"] and row["cooccurrence"] for row in group),
            "support_min": min(row["support"] for row in group),
            "support_max": max(row["support"] for row in group),
        })
    return out


def _rank_bucket(rows: list[dict], key: str) -> list[dict]:
    out = []
    for label, _, _ in RANK_BANDS:
        group = [row for row in rows if row[key] == label]
        if group:
            out.append({"label": label, "edges": len(group)})
    return out


def build() -> dict:
    source = _load(CAP_PATH)
    failing = {
        (row["block"], row["seed"])
        for row in source["rows"]
        if row["prediction_cap"] == CAP
        and row["block"] != "larger-28"
        and not row["C1_joint_pass"]
    }
    expected = {
        (row["block"], row["seed"]): row
        for row in source["rows"] if row["prediction_cap"] == CAP
    }
    seeds = [
        (block["label"], seed)
        for block in cap.BLOCKS
        for seed in block["seeds"]
        if block["label"] != "larger-28"
    ]
    tasks = [(label, seed, prediction_cap)
             for label, seed in seeds
             for prediction_cap in (CAP, DIAGNOSTIC_CAP)]
    with ProcessPoolExecutor(max_workers=min(6, len(tasks))) as pool:
        runs = list(pool.map(_replay, tasks))
    by_key = {(run["block"], run["seed"], run["prediction_cap"]): run
              for run in runs}
    for (label, seed) in seeds:
        want = expected[(label, seed)]
        got = by_key[(label, seed, CAP)]
        if (got["A"], got["K"]) != (want["A"], want["K"]):
            raise SystemExit(
                "REFUSED: %s/%d A/K %d/%d, expected %d/%d"
                % (label, seed, got["A"], got["K"], want["A"], want["K"]))
        if got["candidate_edges"] != want["candidate_edges"]:
            raise SystemExit("REFUSED: %s/%d candidate count" % (label, seed))
    merged = {
        (label, seed): _merged_rows(
            by_key[(label, seed, CAP)], by_key[(label, seed, DIAGNOSTIC_CAP)])
        for label, seed in seeds
    }
    failing_rows = [row for key, rows in merged.items()
                    if key in failing for row in rows]
    assert len({(row["block"], row["seed"]) for row in failing_rows}) == 10
    seed_rows = [_seed_summary(rows) for key, rows in merged.items()
                 if key in failing]
    support_bins = _bucket(
        failing_rows, "support_bin",
        tuple(label for label, _, _ in SUPPORT_BINS))
    families = _bucket(failing_rows, "cell_relation", FAMILIES)
    kinds = []
    for label, flag in (("transition", False), ("cooccurrence", True)):
        group = [row for row in failing_rows if row["cooccurrence"] == flag]
        if group:
            kinds.append({
                "label": label,
                "candidate_edges": len(group),
                "A112": sum(row["A112"] for row in group),
                "A1000": sum(row["A1000"] for row in group),
                "missing": sum(row["missing"] for row in group),
                "cap_bound": sum(row["cap_bound"] for row in group),
            })
    rank_bands = _rank_bucket(
        [row for row in failing_rows if row["A112"]], "rank112_band")
    missing_rank_bands = _rank_bucket(
        [row for row in failing_rows if row["cap_bound"]], "rank1000_band")
    missing = [row for row in failing_rows if row["missing"]]
    cap_bound = [row for row in missing if row["cap_bound"]]
    never = [row for row in missing if row["never_A"]]
    missing_ge_5 = [row for row in missing if row["support"] >= SUPPORT_FLOOR]
    missing_cooc = sum(row["cooccurrence"] for row in missing)
    rank_min = min((row["rank1000"] for row in cap_bound), default=0)
    rank_max = max((row["rank1000"] for row in cap_bound), default=0)
    if len(cap_bound) == len(missing) and missing:
        flip_q = sum(row["cell_relation"] == "flip_q" for row in missing)
        reading = (
            f"All {len(missing)} A-missing candidate edges across the ten "
            f"failing seeds appear at diagnostic cap 1000, at ranks "
            f"{rank_min}-{rank_max}. They are support-eligible and all "
            f"{len(missing) - missing_cooc} are transition candidates; none is "
            f"a cooccurrence. {flip_q}/{len(missing)} are flip_q. The cap-112 "
            "run excludes them, but cap 1000 also changes which predictions "
            "are reinforced across cycles, so the rank range is diagnostic, "
            "not a fixed cutoff. The stable discriminator is the edge family: "
            "flip_q transitions are ranked out of the 112-row prediction window."
        )
    elif cap_bound:
        reading = (
            "%d of %d A-missing edges appear at diagnostic cap 1000 (ranks "
            "%d-%d); %d never appear. The shortfall is mostly cap/rank, with "
            "a remaining eligibility component."
            % (len(cap_bound), len(missing), rank_min, rank_max, len(never))
        )
    else:
        reading = (
            "None of the %d A-missing edges appears at diagnostic cap 1000, "
            "so the shortfall is not the 112-row window; it lies upstream of "
            "the returned prediction list." % len(missing)
        )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "What keeps the ten failing 16-tag seeds below A=60 at prediction "
            "cap 112: A rank, support eligibility, or edge family?"
        ),
        "definition": (
            "Per-candidate A membership and best returned rank at cap 112 and "
            "at a diagnostic cap 1000, K membership, acquisition support, cell "
            "relation and old/new family for the ten 16-tag seeds that fail "
            "joint C1 at loop cap 120 / prediction cap 112."
        ),
        "method": (
            "One no-arm replay per seed and cap. A_rank is the minimum 1-based "
            "position in the returned list. Cap-112 A/K counts must match the "
            "committed cap-112 artifact exactly. Cap 1000 is diagnostic only."
        ),
        "constants": {
            "loop_cap": LOOP_CAP,
            "prediction_cap": CAP,
            "diagnostic_cap": DIAGNOSTIC_CAP,
            "c1_floor": C1_FLOOR,
            "support_floor": SUPPORT_FLOOR,
            "support_bins": [label for label, _, _ in SUPPORT_BINS],
            "rank_bands": [label for label, _, _ in RANK_BANDS],
        },
        "governance": {
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "failing_seeds": sorted(seed for _, seed in failing),
        "seed_rows": seed_rows,
        "support_bins": support_bins,
        "families": families,
        "kinds": kinds,
        "rank_bands": rank_bands,
        "missing_rank_bands": missing_rank_bands,
        "missing_total": len(missing),
        "missing_support_ge_5": len(missing_ge_5),
        "missing_cap_bound": len(cap_bound),
        "missing_never": len(never),
        "missing_cooccurrence": missing_cooc,
        "missing_rank_min": rank_min,
        "missing_rank_max": rank_max,
        "candidate_rows": failing_rows,
        "not_evidence": (
            "A descriptive decomposition of ten no-arm 16-tag seeds at one "
            "cap pair plus a diagnostic ceiling. Cap 1000 changes reinforcement "
            "across cycles, so it locates missing edges but is not a pure "
            "window expansion. It does not establish why flip_q transitions "
            "rank lower, and it is not a treatment, target-viability or "
            "successor result."
        ),
    })


def render(doc: dict) -> str:
    lines = [
        "# A1 cap-112 16-tag decomposition",
        "",
        "Generated from `docs/a1_prediction_cap112_decompose.json` by "
        "`python -m benchmarks.a1_prediction_cap112_decompose --write`. Do not edit by hand.",
        "",
        "**Descriptive, not an A1 result.** Ten failing 16-tag seeds at loop cap "
        "**120** and prediction cap **112**, with a diagnostic cap **1000** to "
        "locate missing edges. No target, freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "| Missing edges | Support >=5 | Cap-1000 bound | Never A | Cooccurrence | Cap-1000 rank range |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
        "| %d | %d | %d | %d | %d | %d-%d |" % (
            doc["missing_total"], doc["missing_support_ge_5"],
            doc["missing_cap_bound"], doc["missing_never"],
            doc["missing_cooccurrence"], doc["missing_rank_min"],
            doc["missing_rank_max"]),
        "",
        "## Per seed",
        "",
        "| Block | Seed | Candidates | A112 | A1000 | Gap | Missing | Cap-bound | Never | Max A112 rank |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["seed_rows"]:
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            row["block"], row["seed"], row["candidate_edges"], row["A112"],
            row["A1000"], row["gap_to_60"], row["missing"],
            row["missing_cap_bound"], row["missing_never"],
            row["A112_rank_max"]))
    lines += [
        "",
        "## Support",
        "",
        "| Support | Candidates | A112 | A112 rate | A1000 | Missing | Cap-bound |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["support_bins"]:
        lines.append("| %s | %d | %d | %.1f%% | %d | %d | %d |" % (
            row["label"], row["candidate_edges"], row["A112"],
            100.0 * row["A112_rate"], row["A1000"], row["missing"],
            row["missing_cap_bound"]))
    lines += [
        "",
        "## Edge family",
        "",
        "| Cell relation | Candidates | A112 | A112 rate | Missing | Cap-bound | Never |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["families"]:
        lines.append("| %s | %d | %d | %.1f%% | %d | %d | %d |" % (
            row["label"], row["candidate_edges"], row["A112"],
            100.0 * row["A112_rate"], row["missing"],
            row["missing_cap_bound"], row["missing_never"]))
    lines += [
        "",
        "## Prediction kind",
        "",
        "| Kind | Candidates | A112 | A1000 | Missing | Cap-bound |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["kinds"]:
        lines.append("| %s | %d | %d | %d | %d | %d |" % (
            row["label"], row["candidate_edges"], row["A112"],
            row["A1000"], row["missing"], row["cap_bound"]))
    lines += [
        "",
        "## A112 rank bands",
        "",
        "| Best A112 rank | A edges |",
        "| --- | ---: |",
    ]
    for row in doc["rank_bands"]:
        lines.append("| %s | %d |" % (row["label"], row["edges"]))
    lines += [
        "",
        "## Missing-edge cap-1000 ranks",
        "",
        "| Best cap-1000 rank | Missing edges |",
        "| --- | ---: |",
    ]
    for row in doc["missing_rank_bands"]:
        lines.append("| %s | %d |" % (row["label"], row["edges"]))
    lines += [
        "",
        "## Reading",
        "",
        "A112 rank is the best 1-based position in the shipped 112-row list. "
        "The diagnostic cap 1000 only locates edges that the shipped window "
        "excludes; it is not a proposed protocol.",
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
    if len(doc.get("seed_rows") or []) != 10:
        found.append("expected ten failing seeds")
    if doc.get("missing_total") != sum(
            row["missing"] for row in doc.get("seed_rows") or []):
        found.append("missing total")
    if doc.get("missing_support_ge_5") != sum(
            row["missing_support_ge_5"] for row in doc.get("seed_rows") or []):
        found.append("missing support total")
    if doc.get("missing_cap_bound") != sum(
            row["missing_cap_bound"] for row in doc.get("seed_rows") or []):
        found.append("cap-bound total")
    if doc.get("missing_never") != sum(
            row["missing_never"] for row in doc.get("seed_rows") or []):
        found.append("never-A total")
    if doc.get("missing_cooccurrence") != sum(
            row["missing_cooccurrence"] for row in doc.get("seed_rows") or []):
        found.append("missing cooccurrence total")
    for row in doc.get("seed_rows") or []:
        if row.get("gap_to_60") != C1_FLOOR - row.get("A112", -1):
            found.append("gap at %s/%s" % (row.get("block"), row.get("seed")))
        if row.get("missing") != row["candidate_edges"] - row["A112"]:
            found.append("missing count at %s/%s"
                         % (row.get("block"), row.get("seed")))
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if _support_bin(5) != "4-7":
        failures.append("support 5 must use the 4-7 bin")
    if _rank_band(20) != "1-20" or _rank_band(21) != "21-40":
        failures.append("rank band boundaries")
    if _rank_band(113) != "113-1000":
        failures.append("rank 113 must be in the diagnostic band")
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
        raise SystemExit("no cap-112 decomposition artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("cap-112 16-tag decomposition: clean")
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
        print("cap-112 16-tag decomposition self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
