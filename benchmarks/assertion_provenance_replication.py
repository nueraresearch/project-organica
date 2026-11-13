"""Fresh-seed replication of the reverse-orientation provenance split.

The original ledger classifies 26 asserted-but-never-served Q4 edges as 18 identity
mismatches and 8 alternate loop/dream paths. That is one block. This module asks whether the
same classifier, applied to six fresh worlds, reproduces the split.

The design is frozen in ``docs/assertion_provenance_replication_prereg.json`` before the
run. Each seed is replayed for 120 cycles at cap 40 with the same acquisition schedule. The
population is every asserted world edge with zero direct served windows. A single replay
supplies both the service count and the recorded count, so the recording-gap category is
structurally zero and is not being tested; the endpoint is the identity-versus-alternate
split.

The pre-specified verdict is:

* ``REPLICATED`` when identity mismatches are the majority, both classes are present, and
  the fresh 95% Wilson interval contains the original 18/26 share;
* ``DIRECTIONAL ONLY`` when the direction is right but that interval excludes 18/26;
* ``NOT REPLICATED`` when the majority or both-class condition fails;
* ``VOID`` when the block has no never-served asserted edge or the seeds are not fresh.

    ./.venv/bin/python -m benchmarks.assertion_provenance_replication --write
    ./.venv/bin/python -m benchmarks.assertion_provenance_replication --check
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import assertion_provenance as provenance                 # noqa: E402
from benchmarks import engine_stamp                                      # noqa: E402
from benchmarks.acquisition_compositional import generate_compositional_world  # noqa: E402
from benchmarks.acquisition_harness import (                              # noqa: E402
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges  # noqa: E402
from benchmarks.presence_construct_audit import (                         # noqa: E402
    ACQ_SOURCE,
    PHASE_ACQUISITION,
    _world_compositional_edges,
)
from organica.sleep import SleepService                                   # noqa: E402

PREREG = ROOT / "docs" / "assertion_provenance_replication_prereg.json"
ARTIFACT = ROOT / "docs" / "assertion_provenance_replication.json"
PAGE = ROOT / "docs" / "ASSERTION-PROVENANCE-REPLICATION.md"
KIND = "assertion_provenance_replication"
PREREG_ID = "ASSERTION-PROVENANCE-REPLICATION-1"
SEEDS = [20613101, 20613102, 20613103, 20613104, 20613105, 20613106]
CYCLES = 120
CAP = 40
ORIGINAL_IDENTITY = 18
ORIGINAL_ALTERNATE = 8
ORIGINAL_EDGES = 26
ORIGINAL_SHARE = ORIGINAL_IDENTITY / ORIGINAL_EDGES
Z_95 = 1.959963984540054
VERDICTS = ("REPLICATED", "DIRECTIONAL ONLY", "NOT REPLICATED", "VOID")
COLLISION_ALLOW = (
    PREREG,
    ARTIFACT,
    ROOT / "docs" / "research_question_registry.json",
    ROOT / "docs" / "never_served_assertion_model_replication.json",
    ROOT / "docs" / "never_served_assertion_model_replication_prereg.json",
    ROOT / "docs" / "source_diversified_top20.json",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denominator = 1.0 + Z_95 * Z_95 / n
    centre = (p + Z_95 * Z_95 / (2.0 * n)) / denominator
    margin = (Z_95 * math.sqrt(p * (1.0 - p) / n
                               + Z_95 * Z_95 / (4.0 * n * n)) / denominator)
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def _criteria(identity: int, alternate: int) -> dict:
    n = identity + alternate
    low, high = _wilson(identity, n)
    return {
        "R1_direction": identity > alternate,
        "R2_original_share_in_interval": bool(n and low <= ORIGINAL_SHARE <= high),
        "R3_both_classes_present": identity > 0 and alternate > 0,
        "wilson_95": [round(low, 6), round(high, 6)],
        "n": n,
        "identity_share": round(identity / n, 6) if n else None,
    }


def _verdict(identity: int, alternate: int, criteria: dict) -> str:
    if identity + alternate == 0:
        return "VOID"
    if not criteria["R1_direction"] or not criteria["R3_both_classes_present"]:
        return "NOT REPLICATED"
    if criteria["R2_original_share_in_interval"]:
        return "REPLICATED"
    return "DIRECTIONAL ONLY"


def _validate_prereg(body: dict) -> list[str]:
    found: list[str] = []
    if body.get("prereg") != PREREG_ID:
        found.append("prereg id")
    if body.get("status") not in ("FROZEN, NOT RUN", "FROZEN, RUN"):
        found.append("prereg status")
    design = body.get("design") or {}
    if design.get("seeds") != SEEDS:
        found.append("seed block")
    if design.get("cells") != len(SEEDS):
        found.append("cell count")
    if design.get("cycles") != CYCLES or design.get("cap") != CAP:
        found.append("cycles or cap")
    reference = body.get("reference") or {}
    if (reference.get("identity_mismatch"), reference.get("alternate_assertion_path"),
            reference.get("edges")) != (ORIGINAL_IDENTITY, ORIGINAL_ALTERNATE,
                                        ORIGINAL_EDGES):
        found.append("reference split")
    if [row.get("id") for row in body.get("criteria") or []] != ["R1", "R2", "R3"]:
        found.append("criteria")
    if set(body.get("verdicts") or {}) != set(VERDICTS):
        found.append("verdict vocabulary")
    if body.get("result") != ARTIFACT.relative_to(ROOT).as_posix():
        found.append("result path")
    return found


def _run_seed(seed: int) -> dict:
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("assertion_provenance_replication")
    memory = _CountingMemoryService(str(db_path))
    service = SleepService(memory)
    service.MAX_PREDICTIONS = CAP
    windows: list[list[tuple[str, str]]] = []
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                windows.append([(p.source, p.target) for p in
                                service.run_sleep_cycle().predictions])
        candidates = service._load_prior_candidates()
        asserted = {(a, b) for a, targets in structure_edges(candidates).items()
                    for b in targets}
    finally:
        memory.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    asserted_world = asserted & world_edges
    served = Counter(edge for window in windows for edge in window
                     if edge in world_edges)
    contributed = provenance.contributions(candidates)
    rows = []
    for edge in sorted(asserted_world):
        direct = served.get(edge, 0)
        if direct:
            continue
        reverse = (edge[1], edge[0])
        reverse_count = served.get(reverse, 0)
        sources = {name: weight for name, weight in
                   sorted(contributed.get(edge, {}).items())}
        if not sources:
            raise SystemExit("REFUSED: seed %d asserted edge %s has no readout source"
                             % (seed, "%s>%s" % edge))
        category = provenance.classify(direct, direct, reverse_count, sources)
        if category == "recording_gap":
            raise SystemExit("REFUSED: one replay cannot create a recording gap")
        rows.append({
            "seed": seed,
            "edge": "%s>%s" % edge,
            "direct_served_windows": direct,
            "reverse_served_windows": reverse_count,
            "assertion_sources": sources,
            "category": category,
        })
    return {
        "seed": seed,
        "asserted_world_edges": len(asserted_world),
        "served_world_edges": len(served),
        "never_served_asserted": len(rows),
        "categories": dict(Counter(row["category"] for row in rows)),
        "rows": rows,
    }


def build() -> dict:
    prereg = _load(PREREG)
    problems = _validate_prereg(prereg)
    from benchmarks.presence_cap_experiment import seed_collisions
    collisions = seed_collisions(SEEDS, allow=COLLISION_ALLOW)
    if collisions:
        problems.append("seed collision: %r" % (collisions,))
    if problems:
        raise SystemExit("REFUSED: " + "; ".join(problems))

    traces = [_run_seed(seed) for seed in SEEDS]
    rows = [row for trace in traces for row in trace["rows"]]
    counts = Counter(row["category"] for row in rows)
    identity = counts.get("identity_mismatch", 0)
    alternate = counts.get("alternate_assertion_path", 0)
    residual = counts.get("assertion_without_service", 0)
    criteria = _criteria(identity, alternate)
    verdict = _verdict(identity, alternate, criteria)
    summary = {
        "asserted_world_edges": sum(trace["asserted_world_edges"] for trace in traces),
        "served_world_edges": sum(trace["served_world_edges"] for trace in traces),
        "never_served_asserted": len(rows),
        "identity_mismatch": identity,
        "alternate_assertion_path": alternate,
        "assertion_without_service": residual,
        "recording_gap": counts.get("recording_gap", 0),
        "identity_share": criteria["identity_share"],
        "wilson_95": criteria["wilson_95"],
        "original_identity": ORIGINAL_IDENTITY,
        "original_alternate": ORIGINAL_ALTERNATE,
        "original_edges": ORIGINAL_EDGES,
        "original_share": round(ORIGINAL_SHARE, 6),
        "criteria": criteria,
        "verdict": verdict,
    }
    return engine_stamp.stamp({
        "kind": KIND,
        "status": "RUN",
        "prereg": PREREG.relative_to(ROOT).as_posix(),
        "question": prereg["question"],
        "scope": (
            "Six fresh seeds, one compositional world family, 120 cycles, cap 40 and one "
            "replay per seed. This block tests whether the reverse-orientation provenance "
            "split replicates; it does not test recording fidelity (one replay makes the "
            "recording-gap category structurally zero) or whether service would change A_W."
        ),
        "design": prereg["design"],
        "reference": prereg["reference"],
        "endpoint": prereg["endpoint"],
        "criteria": prereg["criteria"],
        "seeds": traces,
        "rows": rows,
        "summary": summary,
        "not_evidence": prereg["not_evidence"],
    })


def render(art: dict) -> str:
    summary = art["summary"]
    lines = [
        "# Fresh-seed replication of the reverse-orientation provenance split",
        "",
        "Generated from `docs/assertion_provenance_replication.json` by "
        "`python -m benchmarks.assertion_provenance_replication --write`. Do not edit by hand.",
        "",
        "**Verdict: `%s`.** The design was frozen in "
        "`docs/assertion_provenance_replication_prereg.json` before the run." % summary["verdict"],
        "",
        "## Design",
        "",
        "- Seeds: **%s** (six fresh seeds; collision scan empty)."
        % ", ".join(str(seed) for seed in art["design"]["seeds"]),
        "- **%d** cycles, cap **%d**, PHASE_ACQUISITION schedule, no engine edit."
        % (art["design"]["cycles"], art["design"]["cap"]),
        "- Population: every asserted world edge with zero direct served windows.",
        "- One replay per seed. Direct service and recorded service are the same record, so "
        "the recording-gap category is structurally zero and is not tested here.",
        "",
        "## Result",
        "",
        "| Quantity | Original Q4 | Fresh block |",
        "| --- | ---: | ---: |",
        "| Never-served asserted edges | %d | %d |"
        % (summary["original_edges"], summary["never_served_asserted"]),
        "| Identity mismatch | %d | %d |"
        % (summary["original_identity"], summary["identity_mismatch"]),
        "| Alternate assertion path | %d | %d |"
        % (summary["original_alternate"], summary["alternate_assertion_path"]),
        "| Identity share | %.3f | %s |"
        % (summary["original_share"],
           "not measurable" if summary["identity_share"] is None
           else "%.3f" % summary["identity_share"]),
        "| 95%% Wilson interval | not recorded | %s |"
        % ("not measurable" if summary["identity_share"] is None
           else "[%.3f, %.3f]" % tuple(summary["wilson_95"])),
        "",
        "| Criterion | Passes |",
        "| --- | --- |",
        "| R1 identity > alternate | %s |"
        % ("yes" if summary["criteria"]["R1_direction"] else "no"),
        "| R2 original 18/26 inside fresh interval | %s |"
        % ("yes" if summary["criteria"]["R2_original_share_in_interval"] else "no"),
        "| R3 both classes present | %s |"
        % ("yes" if summary["criteria"]["R3_both_classes_present"] else "no"),
        "",
        "`assertion_without_service` residuals: **%d**. `recording_gap` rows: **%d** "
        "(structural for this one-replay design)." % (
            summary["assertion_without_service"], summary["recording_gap"]),
        "",
        "## Per seed",
        "",
        "| Seed | Asserted world edges | Served world edges | Never served | Identity | Alternate | Residual |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for trace in art["seeds"]:
        cats = trace["categories"]
        lines.append("| %d | %d | %d | %d | %d | %d | %d |" % (
            trace["seed"], trace["asserted_world_edges"], trace["served_world_edges"],
            trace["never_served_asserted"], cats.get("identity_mismatch", 0),
            cats.get("alternate_assertion_path", 0),
            cats.get("assertion_without_service", 0)))
    lines += [
        "",
        "## Every never-served edge",
        "",
        "| Seed | Edge | Direct served | Reverse served | Category | Sources |",
        "| ---: | --- | ---: | ---: | --- | --- |",
    ]
    for row in art["rows"]:
        lines.append("| %d | `%s` | %d | %d | %s | %s |" % (
            row["seed"], row["edge"], row["direct_served_windows"],
            row["reverse_served_windows"], row["category"].replace("_", " "),
            ", ".join("%s=%g" % item for item in row["assertion_sources"].items())))
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "This is a fresh-block test of whether the **orientation split** repeats. It does "
        "not test recording fidelity, because one replay cannot distinguish a direct service "
        "record from a replay; it also does not test whether serving the direct edges would "
        "change `A_W`, and it is not a capability or engine-effect claim.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("artifact kind")
    if art.get("status") != "RUN":
        found.append("artifact status")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    prereg = _load(PREREG)
    found.extend(_validate_prereg(prereg))
    if art.get("prereg") != PREREG.relative_to(ROOT).as_posix():
        found.append("prereg path")
    if art.get("design", {}).get("seeds") != SEEDS:
        found.append("artifact seed block")
    rows = art.get("rows") or []
    if any(row.get("direct_served_windows") != 0 for row in rows):
        found.append("a row is not never-served")
    if any(row.get("category") == "recording_gap" for row in rows):
        found.append("one replay produced a recording gap")
    summary = art.get("summary") or {}
    counts = Counter(row.get("category") for row in rows)
    identity = counts.get("identity_mismatch", 0)
    alternate = counts.get("alternate_assertion_path", 0)
    if summary.get("never_served_asserted") != len(rows):
        found.append("summary row count")
    if summary.get("identity_mismatch") != identity:
        found.append("summary identity count")
    if summary.get("alternate_assertion_path") != alternate:
        found.append("summary alternate count")
    if summary.get("assertion_without_service") != counts.get(
            "assertion_without_service", 0):
        found.append("summary residual count")
    criteria = _criteria(identity, alternate)
    if summary.get("criteria") != criteria:
        found.append("summary criteria")
    if summary.get("verdict") != _verdict(identity, alternate, criteria):
        found.append("summary verdict")
    if any(trace.get("never_served_asserted") != len(trace.get("rows") or [])
           for trace in art.get("seeds") or []):
        found.append("seed row count")
    from benchmarks.presence_cap_experiment import seed_collisions
    if seed_collisions(SEEDS, allow=COLLISION_ALLOW):
        found.append("seed collision")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    return found


def write() -> int:
    body = build()
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    print("assertion provenance replication: %s %s" % (
        body["summary"]["verdict"], json.dumps({
            "identity": body["summary"]["identity_mismatch"],
            "alternate": body["summary"]["alternate_assertion_path"],
            "total": body["summary"]["never_served_asserted"],
            "wilson_95": body["summary"]["wilson_95"],
        })))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no replication artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("assertion provenance replication: %s %s" % (
        art["summary"]["verdict"], json.dumps({
            "identity": art["summary"]["identity_mismatch"],
            "alternate": art["summary"]["alternate_assertion_path"],
            "total": art["summary"]["never_served_asserted"],
        })))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
