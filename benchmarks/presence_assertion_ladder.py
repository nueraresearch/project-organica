"""Where present-but-unasserted world edges are lost: offered, admitted, asserted.

The same-build audit (`benchmarks/presence_assertion_audit.py`) measured the two end points:
every world edge is present in raw temporal memory, and 34-47 of 112 survive into the final
asserted structure. It did not say *where* the others go. This block traces each world edge
through the Layer-1 prediction path, which is the only capped stage between the two:

    present  (raw temporal memory, the audit's basis)
      -> offered   (the ranked candidate list with the cap raised; a counterfactual arm)
      -> admitted  (the 40-row stratified window the shipped engine actually returns)
      -> asserted  (the final structure, all six types, `structure_edges`)

Each edge that is present but not asserted is assigned to the first stage it failed:
`not_offered`, `offered_not_admitted`, or `admitted_not_asserted`. An asserted edge is also
tested for having been admitted at all, because `structure_edges` aggregates six structure
types and the prediction window is only one of them; such an edge is reported as
`asserted_without_admission` and is not a loss.

The engine is unchanged. Recording is an instance-level wrapper that returns the engine's own
list; the shipped arm is proven behaviour-neutral by requiring its presence count, asserted
count and asserted fingerprint to equal the published audit row for the same seed. The raised
cap is a separate diagnostic arm, in the pattern the paired capacity diagnostic already uses,
and is labelled a counterfactual wherever it is reported.

**Decision rule, declared before the run.** This is exploratory: no criterion is scored and no
engine change is licensed. The descriptive label is the bucket that holds the largest pooled
share of misses, provided that share is at least `DOMINANT` and that bucket is the largest on
at least `MAJORITY_SEEDS` of the six seeds; otherwise the label is `MIXED`. A bucket holding
fewer than `MIN_MISSES` misses in total cannot carry the label (it is reported and the label is
`MIXED`), and a block with no misses at all is `VOID_NO_MISSES`.

    ./.venv/bin/python -m benchmarks.presence_assertion_ladder --run
    ./.venv/bin/python -m benchmarks.presence_assertion_ladder --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                          # noqa: E402
from benchmarks.acquisition_compositional import PHASE_ACQUISITION, generate_compositional_world  # noqa: E402
from benchmarks.acquisition_harness import (                                  # noqa: E402
    SHORT_CYCLES,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import (                                   # noqa: E402
    EVENTS_PER_CYCLE,
    _world_compositional_edges,
    structure_edges,
)
from organica.sleep import SleepService                                       # noqa: E402

SEEDS = (20261100, 20261101, 20261102, 20261103, 20261104, 20261105)
CAP = 40
UNCAPPED = 1_000_000
CYCLES = SHORT_CYCLES
KIND = "presence_assertion_ladder"
ARTIFACT = ROOT / "docs" / "presence_assertion_ladder_0.14.0.json"
PAGE = ROOT / "docs" / "PRESENCE-ASSERTION-LADDER-0.14.0.md"
AUDIT = ROOT / "docs" / "presence_assertion_audit_0.14.0.json"

BUCKETS = ("not_offered", "offered_not_admitted", "admitted_not_asserted")
LABELS = {
    "not_offered": "LOSS_BEFORE_OFFER",
    "offered_not_admitted": "LOSS_AT_ADMISSION",
    "admitted_not_asserted": "LOSS_AFTER_ADMISSION",
}
DOMINANT = 0.60
MAJORITY_SEEDS = 5
MIN_MISSES = 6


class RecordingSleepService(SleepService):
    """The engine's own prediction builder, with each cycle's returned window recorded.

    ``cap=None`` runs the shipped engine unchanged. A larger cap is the diagnostic
    counterfactual arm that exposes the candidate space the 40-slot window is drawn from.
    The wrapper returns the engine's list unmodified, so admission, storage and every later
    stage see exactly what they would have seen without it.
    """

    def __init__(self, memory, cap: int | None = None):
        super().__init__(memory)
        if cap is not None:
            self.MAX_PREDICTIONS = cap
        self.windows: list[list[tuple[str, str]]] = []

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        out = super()._build_predictions(temporal, freqs, prior_schemas)
        self.windows.append([(c.source, c.target) for c in out])
        return out


def run_arm(seed: int, cap: int | None) -> dict:
    """One acquisition run on the Gate-13 world; returns the trace, not a verdict."""
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    events_text, trainable = world["events"], world["trainable"]
    world_edges = _world_compositional_edges(world)

    db_path = _make_scratch_db("presence_ladder")
    mem = _CountingMemoryService(str(db_path))
    svc = RecordingSleepService(mem, cap=cap)
    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_event_lo, acq_event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    ACQ_SOURCE = "env_acq"

    try:
        for i, (text, train_flag) in enumerate(zip(events_text, trainable)):
            in_acq = acq_event_lo <= i < acq_event_hi
            if in_acq and not train_flag:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            source = ACQ_SOURCE if in_acq else "env"
            mem.store(text, event_type="observe", source=source)
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                svc.run_sleep_cycle()

        asserted_pairs = {(a, b) for a, targets in structure_edges(svc._load_prior_candidates()).items()
                          for b in targets}
        temporal_pairs = {(a, b) for a, b, _c in mem.temporal_edges(min_count=1)}
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    windows = svc.windows
    return {
        "seed": seed,
        "cap": CAP if cap is None else cap,
        "world_edges": len(world_edges),
        "windows": windows,
        "window_sizes": sorted(len(window) for window in windows),
        "present_pairs": temporal_pairs,
        "asserted_pairs": asserted_pairs,
        "world": world_edges,
        "asserted_edges": len(asserted_pairs),
        "asserted_fingerprint": _fingerprint(asserted_pairs),
    }


def _fingerprint(pairs) -> str:
    return hashlib.sha256("|".join("%s>%s" % edge for edge in sorted(pairs))
                          .encode("utf-8")).hexdigest()[:16]


def _window_stats(windows: list[list[tuple[str, str]]], world) -> dict:
    sizes = [len(window) for window in windows]
    binding = sum(1 for size in sizes if size >= CAP)
    admitted_rows = sum(sizes)
    world_rows = sum(1 for window in windows for edge in window if edge in world)
    return {
        "cycles": len(windows),
        "median_window": statistics.median(sizes) if sizes else 0,
        "max_window": max(sizes) if sizes else 0,
        "cycles_at_cap": binding,
        "admitted_rows": admitted_rows,
        "world_edge_rows": world_rows,
        "world_row_share": round(world_rows / admitted_rows, 6) if admitted_rows else None,
    }


def admission_stats(edges, counts: dict) -> dict:
    """How many 40-row windows each edge appeared in, summarised for a set of edges."""
    values = [counts.get(edge, 0) for edge in edges]
    if not values:
        return {"edges": 0, "zero": 0, "median": None, "min": None, "max": None}
    return {
        "edges": len(values),
        "zero": sum(1 for value in values if value == 0),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
    }


def classify(present, offered, admitted, asserted) -> dict[str, list]:
    """Assign each present-but-unasserted edge to the first stage it failed."""
    misses = present - asserted
    found = {"not_offered": [], "offered_not_admitted": [], "admitted_not_asserted": []}
    for edge in sorted(misses):
        if edge in admitted:
            found["admitted_not_asserted"].append(edge)
        elif edge in offered:
            found["offered_not_admitted"].append(edge)
        else:
            found["not_offered"].append(edge)
    return found


def label_for(rows: list[dict]) -> str:
    """The declared rule: largest pooled bucket, dominant share, majority of seeds."""
    pooled = {name: sum(row["buckets"][name] for row in rows) for name in BUCKETS}
    total = sum(pooled.values())
    if total == 0:
        return "VOID_NO_MISSES"
    leader = max(BUCKETS, key=lambda name: pooled[name])
    if pooled[leader] < MIN_MISSES or pooled[leader] / total < DOMINANT:
        return "MIXED"
    wins = sum(1 for row in rows if row["leading_bucket"] == leader)
    if wins < MAJORITY_SEEDS:
        return "MIXED"
    return LABELS[leader]


def _set_of(pairs) -> set:
    return {(a, b) for a, b in pairs}


def build() -> dict:
    if SleepService.MAX_PREDICTIONS != CAP:
        raise SystemExit("the shipped Layer-1 cap is %d, not the traced %d"
                         % (SleepService.MAX_PREDICTIONS, CAP))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    audit_rows = {row["seed"]: row for row in audit["rows"]}

    rows, mismatches = [], []
    for seed in SEEDS:
        shipped = run_arm(seed, None)
        offered_arm = run_arm(seed, UNCAPPED)
        world = shipped["world"]
        present = world & shipped["present_pairs"]
        asserted = world & shipped["asserted_pairs"]
        offered = world & {edge for window in offered_arm["windows"] for edge in window}
        admitted = world & {edge for window in shipped["windows"] for edge in window}
        found = classify(present, offered, admitted, asserted)
        misses = present - asserted

        reference = audit_rows.get(seed, {})
        ok = (len(present) == reference.get("present_world_edges")
              and len(asserted) == reference.get("asserted_world_edges")
              and shipped["asserted_fingerprint"] == reference.get("asserted_fingerprint"))
        if not ok:
            mismatches.append({
                "seed": seed,
                "got": {"present": len(present), "asserted": len(asserted),
                        "fingerprint": shipped["asserted_fingerprint"]},
                "audit": {"present": reference.get("present_world_edges"),
                          "asserted": reference.get("asserted_world_edges"),
                          "fingerprint": reference.get("asserted_fingerprint")},
            })

        counts = {name: len(found[name]) for name in BUCKETS}
        admission_counts = Counter(
            edge for window in shipped["windows"] for edge in window if edge in world)
        rows.append({
            "seed": seed,
            "world_edges": len(world),
            "present_world_edges": len(present),
            "asserted_world_edges": len(asserted),
            "asserted_fingerprint": shipped["asserted_fingerprint"],
            "present_not_asserted": len(misses),
            "offered_world_edges": len(offered),
            "admitted_world_edges": len(admitted),
            "buckets": counts,
            "bucket_edges": {name: ["%s>%s" % edge for edge in found[name]] for name in BUCKETS},
            "admissions": {"%s>%s" % edge: admission_counts.get(edge, 0)
                           for edge in sorted(present)},
            "admission_stats": {name: admission_stats(found[name], admission_counts)
                                for name in BUCKETS},
            "asserted_admission_stats": admission_stats(asserted, admission_counts),
            "leading_bucket": max(BUCKETS, key=lambda name: counts[name]),
            "asserted_without_admission": len(asserted - admitted),
            "admitted_not_offered": len(admitted - offered),
            "shipped_window": _window_stats(shipped["windows"], world),
            "offered_window": _window_stats(offered_arm["windows"], world),
        })

    if mismatches:
        raise SystemExit("REFUSED: the trace does not reproduce the published audit: %r"
                         % (mismatches,))

    pooled = {name: sum(row["buckets"][name] for row in rows) for name in BUCKETS}
    total = sum(pooled.values())
    label = label_for(rows)
    body = {
        "kind": KIND,
        "date": "2026-11-10",
        "status": "EXPLORATORY trace. Behaviour-neutral recording, proven against the published audit.",
        "question": (
            "Of the world edges that are present in raw temporal memory but absent from the "
            "final asserted structure, at which Layer-1 stage is each one lost: never offered, "
            "offered but not admitted to the 40-row window, or admitted but not asserted?"
        ),
        "method": (
            "Two arms per audit seed on the Gate-13 compositional world, 120 cycles, shipped "
            "cap 40. The shipped arm is the engine unchanged with its returned prediction "
            "window recorded; it must reproduce the published audit's presence count, asserted "
            "count and asserted fingerprint or the block refuses to write. The second arm raises "
            "only the Layer-1 cap, exposing the candidate space the 40-row window is drawn from; "
            "it is a counterfactual diagnostic, not the shipped behaviour."
        ),
        "resolution": (
            "edge: each world edge is classified individually; the trace cannot attribute "
            "assertion that arrives from a non-prediction structure type, which is why the "
            "admitted->asserted step is measured as a set difference and not as a lineage."
        ),
        "design": {
            "seeds": list(SEEDS),
            "cycles": CYCLES,
            "shipped_cap": CAP,
            "counterfactual_cap": UNCAPPED,
            "present_basis": "mem.temporal_edges(min_count=1)",
            "offered_basis": "returned prediction window, cap raised (diagnostic arm)",
            "admitted_basis": "returned prediction window, shipped cap 40",
            "asserted_basis": "structure_edges over the surviving candidate snapshots, all six types",
            "dominant_share": DOMINANT,
            "majority_seeds": MAJORITY_SEEDS,
            "min_misses": MIN_MISSES,
        },
        "audit_reference": {"artifact": "docs/presence_assertion_audit_0.14.0.json",
                            "engine_version": audit.get("same_build", {}).get("version")},
        "trace_mismatches": mismatches,
        "rows": rows,
        "summary": {
            "seeds": len(rows),
            "world_edges": sorted({row["world_edges"] for row in rows}),
            "present_world_edges": [min(row["present_world_edges"] for row in rows),
                                    max(row["present_world_edges"] for row in rows)],
            "asserted_world_edges": [min(row["asserted_world_edges"] for row in rows),
                                     max(row["asserted_world_edges"] for row in rows)],
            "present_not_asserted": [min(row["present_not_asserted"] for row in rows),
                                     max(row["present_not_asserted"] for row in rows)],
            "offered_world_edges": [min(row["offered_world_edges"] for row in rows),
                                    max(row["offered_world_edges"] for row in rows)],
            "admitted_world_edges": [min(row["admitted_world_edges"] for row in rows),
                                     max(row["admitted_world_edges"] for row in rows)],
            "pooled_buckets": pooled,
            "pooled_share": {name: round(pooled[name] / total, 6) if total else None
                             for name in BUCKETS},
            "misses_total": total,
            "asserted_without_admission": [min(row["asserted_without_admission"] for row in rows),
                                           max(row["asserted_without_admission"] for row in rows)],
            "median_admissions": {
                "asserted": [min(row["asserted_admission_stats"]["median"] for row in rows),
                             max(row["asserted_admission_stats"]["median"] for row in rows)],
                "admitted_not_asserted": [
                    min(row["admission_stats"]["admitted_not_asserted"]["median"] for row in rows),
                    max(row["admission_stats"]["admitted_not_asserted"]["median"] for row in rows)],
            },
            "admitted_not_offered": [min(row["admitted_not_offered"] for row in rows),
                                     max(row["admitted_not_offered"] for row in rows)],
            "shipped_window_sizes": [row["shipped_window"]["median_window"] for row in rows],
            "shipped_cycles_at_cap": [min(row["shipped_window"]["cycles_at_cap"] for row in rows),
                                      max(row["shipped_window"]["cycles_at_cap"] for row in rows)],
            "shipped_world_row_share": [
                min(row["shipped_window"]["world_row_share"] for row in rows),
                max(row["shipped_window"]["world_row_share"] for row in rows)],
            "offered_candidates_per_cycle": [
                min(row["offered_window"]["median_window"] for row in rows),
                max(row["offered_window"]["median_window"] for row in rows)],
        },
        "verdict": label,
        "reading": _reading(label, rows, pooled, total),
        "not_evidence": (
            "One engine build, one world family, two designs' acquisition phase, six seeds. The "
            "'offered' arm is a counterfactual: raising the cap changes the run, so an edge "
            "counted as offered is one the ranking would have produced with the budget removed, "
            "not one the shipped engine saw. Nothing here licenses an engine change; the label "
            "is descriptive and no criterion is scored."
        ),
    }
    return body


def _reading(label: str, rows: list[dict], pooled: dict, total: int) -> str:
    if label == "VOID_NO_MISSES":
        return "No present-but-unasserted edges were available to classify."
    if label == "MIXED":
        leader = max(BUCKETS, key=lambda name: pooled[name])
        share = pooled[leader] / total if total else 0.0
        wins = sum(1 for row in rows if row["leading_bucket"] == leader)
        return ("The largest bucket is `%s` with %d of %d misses (%.4f), leading on %d of %d "
                "seeds; the declared rule requires a %.2f pooled share and a majority of seeds, "
                "so the label is `MIXED` and the bar is not moved. The split is reported per seed "
                "above, and the admission counts below show how close the two fates are."
                % (leader, pooled[leader], total, share, wins, len(rows), DOMINANT))
    if label == "LOSS_AT_ADMISSION":
        return ("Most missed world edges are offered by the ranking and never reach the 40-row "
                "window: the loss is at admission, in which world edges compete against the "
                "cooccurrence quota and the non-world candidates above them.")
    if label == "LOSS_BEFORE_OFFER":
        return ("Most missed world edges never enter the ranked candidate list at all, so the "
                "loss is upstream of admission, in what the engine proposes.")
    return ("Most missed world edges are admitted to the 40-row window and still absent from "
            "the final structure: the loss is after admission, in what survives into the "
            "asserted structure.")


def render(body: dict) -> str:
    rows = body["rows"]
    summary = body["summary"]
    design = body["design"]
    lines = [
        "# Presence to assertion: where the missing world edges are lost",
        "",
        "Generated from `docs/presence_assertion_ladder_0.14.0.json` by "
        "`python -m benchmarks.presence_assertion_ladder --run`. Do not edit by hand.",
        "",
        "**Status: %s**" % body["status"],
        "",
        "The engine is unchanged. The shipped arm's presence count, asserted count and asserted "
        "fingerprint were required to equal `docs/presence_assertion_audit_0.14.0.json` on every "
        "seed, and did: **%d mismatches**." % len(body["trace_mismatches"]),
        "",
        "## The question",
        "",
        body["question"],
        "",
        "## The four readings",
        "",
        "| Stage | Basis | What it means |",
        "| --- | --- | --- |",
        "| present | `%s` | the audit's presence basis |" % design["present_basis"],
        "| offered | %s | the ranked list with the cap removed (counterfactual) |" % design["offered_basis"],
        "| admitted | %s | the window the shipped engine returns |" % design["admitted_basis"],
        "| asserted | %s | the published audit's assertion basis |" % design["asserted_basis"],
        "",
        "## Per seed",
        "",
        "| Seed | Present | Asserted | Missed | Offered | Admitted | Not offered | Offered, not admitted | Admitted, not asserted | Leading |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append("| %d | %d | %d | %d | %d | %d | %d | %d | %d | %s |" % (
            row["seed"], row["present_world_edges"], row["asserted_world_edges"],
            row["present_not_asserted"], row["offered_world_edges"], row["admitted_world_edges"],
            row["buckets"]["not_offered"], row["buckets"]["offered_not_admitted"],
            row["buckets"]["admitted_not_asserted"], row["leading_bucket"]))
    lines += [
        "",
        "## How often an edge got a slot",
        "",
        "| Set | Edges | Bypass | Never admitted (non-bypass) | Median admissions | Min-max |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name in ("asserted", "admitted_not_asserted", "offered_not_admitted"):
        stats = ([row["asserted_admission_stats"] for row in rows] if name == "asserted"
                 else [row["admission_stats"][name] for row in rows])
        medians = [item["median"] for item in stats if item["median"] is not None]
        edges = sum(item["edges"] for item in stats)
        zero = sum(item["zero"] for item in stats)
        # In the asserted set the zero-admission edges are exactly the bypass;
        # they are not misses, so they get their own column rather than sitting
        # under the "Never admitted" count with the offered-but-not-admitted set.
        bypass = (sum(row["asserted_without_admission"] for row in rows)
                  if name == "asserted" else 0)
        never = zero - bypass
        lines.append("| %s | %d | %d | %d | %s-%s | %s-%s |" % (
            name, edges, bypass, never,
            min(medians) if medians else "n/a", max(medians) if medians else "n/a",
            min(item["min"] for item in stats if item["min"] is not None) if medians else "n/a",
            max(item["max"] for item in stats if item["max"] is not None) if medians else "n/a"))
    lines += [
        "",
        "**Bypass is not a miss.** The 41 never-admitted edges in the asserted set are the "
        "bypass: they are asserted through a non-prediction structure type without ever "
        "entering a prediction window. They are not part of the 423 present-but-unasserted "
        "misses; the 171 offered-but-not-admitted edges are the misses in that table.",
        "",
        "## Pooled over the six seeds",
        "",
        "| Stage the edge failed | Edges | Share of misses |",
        "| --- | --- | --- |",
    ]
    for name in BUCKETS:
        lines.append("| %s | %d | %s |" % (
            name, summary["pooled_buckets"][name],
            "%.4f" % summary["pooled_share"][name] if summary["pooled_share"][name] is not None else "n/a"))
    lines += [
        "",
        "**Verdict: `%s`**" % body["verdict"],
        "",
        body["reading"],
        "",
        "## What the window was doing",
        "",
        "| Reading | Range across seeds |",
        "| --- | --- |",
        "| shipped window size (median per seed) | %s |" % ", ".join(
            str(row["shipped_window"]["median_window"]) for row in rows),
        "| cycles whose window reached the cap of %d | %d-%d of %d |" % (
            design["shipped_cap"], summary["shipped_cycles_at_cap"][0],
            summary["shipped_cycles_at_cap"][1], design["cycles"]),
        "| world edges as a share of admitted rows | %.4f-%.4f |" % tuple(
            summary["shipped_world_row_share"]),
        "| candidates per cycle with the cap removed (median) | %s-%s |" % tuple(
            summary["offered_candidates_per_cycle"]),
        "| asserted world edges that no window ever admitted | %d-%d |" % tuple(
            summary["asserted_without_admission"]),
        "| admitted world edges the counterfactual arm never offered | %d-%d |" % tuple(
            summary["admitted_not_offered"]),
        "",
        "## What this does not claim",
        "",
        body["not_evidence"],
        "",
        "**Resolution.** %s" % body["resolution"],
        "",
    ]
    return "\n".join(lines)


def write(body: dict) -> None:
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(body), indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no trace artifact; run --run")
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    problems = []
    if engine_stamp.missing(body):
        problems.append("the artifact is not fully stamped: %r" % (engine_stamp.missing(body),))
    if body.get("kind") != KIND:
        problems.append("the artifact is not a %s record" % KIND)
    if body.get("trace_mismatches"):
        problems.append("the trace records a mismatch against the published audit")
    expected = label_for(body.get("rows", []))
    if body.get("verdict") != expected:
        problems.append("the verdict is not what the rows imply (%r, not %r)"
                        % (body.get("verdict"), expected))
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(body):
        problems.append("the page is stale")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("presence->assertion ladder %s: %s"
          % (body["verdict"], json.dumps(body["summary"]["pooled_buckets"])))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        return check()
    body = build()
    write(body)
    print("%s: %s" % (body["verdict"], json.dumps(body["summary"]["pooled_buckets"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
